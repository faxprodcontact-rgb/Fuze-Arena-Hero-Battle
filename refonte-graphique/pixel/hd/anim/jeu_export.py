# Export « jeu » des animations HD : du build.py d'un personnage aux planches du combat (public/art/hd/) et à
# src/game/hd-meta.ts (généré, ne pas modifier à la main). Consigne pour les agents : ../consignes/export-jeu.md.
#
#   python3 refonte-graphique/pixel/hd/anim/jeu_export.py eldra jinn matelot …   → exporte ces personnages
#   python3 refonte-graphique/pixel/hd/anim/jeu_export.py --voir <dossier> eldra   → en plus, une planche de contrôle
#                                                                                 (calques séparés, image par image)
#   python3 refonte-graphique/pixel/hd/anim/jeu_export.py --effets                 → les effets reçus (../effets/sortie)
#
# Principe : le build.py n'est pas réécrit. On l'importe, on remplace un instant sa fonction compose(hero, fx_back,
# fx_front, …) par une version qui garde les calques à part, puis on appelle son build_all(). Pour chaque image on a
# donc : le personnage (avec son contour), les effets de derrière, ceux de devant. Le build.py ajoute seulement un
# dictionnaire JEU qui dit, pour chaque attaque, quel genre de coup c'est et où sont ses moments clés :
#
#   JEU = {
#       'attaque': dict(genre='melee', coup=3, cible=(ENEMY_X, GROUND - 40), coupe=ENEMY_X - 30,
#                       avance=[f.get('tx', 0) for f in ATTAQUE]),
#       'speciale': dict(genre='tir', tir=(4, 7), coup=7, cible=(ENEMY_X, HIT_Y), coupe=150, charge=(0, 3)),
#   }
#
#   genre   'melee' : le jeu l'amène devant sa cible, il frappe, il revient ;
#           'tir'   : il tire sur place, le projectile vole jusqu'à la vraie cible (images `tir`), puis l'impact ;
#           'sort'  : il lance sur place, l'effet apparaît directement sur chaque cible (éclair, pluie, colonne…) ;
#           'equipe': sort d'équipe (soin, bouclier…) : rien sur l'ennemi, le jeu pose les effets reçus sur les alliés.
#   coup    l'image où les dégâts tombent (pour 'tir' : la première image de l'impact, après le vol)
#   cible   (x, y) de la toile du build.py : le milieu de l'ennemi tel que l'animateur l'a imaginé (x = ses pieds,
#           y = la hauteur où le coup le touche). Les effets « sur la cible » se poseront aux pieds de la vraie cible.
#   coupe   colonne de la toile : les effets à droite de cette colonne sont « sur la cible » (ils restent avec
#           l'ennemi), ceux de gauche restent sur le personnage. Défaut : cible x − 36.
#   avance  (facultatif) le déplacement vers l'avant cuit dans chaque image (pixels) : retiré, c'est le jeu qui
#           déplace le personnage. Pour 'melee', le jeu le fait avancer au même rythme.
#   tir     (i0, i1) : images où le projectile vole (i0 = il part, i1 = première image après le vol = coup).
#           Les effets à droite de `depuis` (défaut : le bord avant du personnage au repos) forment le projectile.
#   charge  (i0, i1) : images de la charge (incluses) : le jeu y pose une petite lumière douce de l'élément.
#   arc     (facultatif, 'tir') : hauteur de la cloche du vol, en pixels (0 = tout droit).
#   retour  (facultatif, 'tir') (i0, i1) : images où l'arme lancée revient (boomerang) : ce qui est à droite de
#           `depuis` vole de la cible jusqu'à la main.
#   rase    (facultatif, 'tir') : le projectile court au ras du sol (vague, pics de glace) : il glisse à plat jusqu'aux
#           pieds de la cible, à la hauteur où il a quitté le personnage.
#   vitesse, pente (facultatifs, 'tir') : imposent la vitesse (pixels/s) et l'angle du dessin du projectile (sinon mesurés).
import sys, os, json, math, hashlib, importlib.util, inspect
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(HD, '..', '..', '..'))
OUT = os.path.join(ROOT, 'public', 'art', 'hd')
META = os.path.join(ROOT, 'src', 'game', 'hd-meta.ts')
sys.path.insert(0, HD)
import hd  # noqa: E402

UP = 2                     # les planches sont agrandies ×2 sans flou (le jeu les réduit : un pixel du dessin = 1,22)
SCALE = 1.22               # taille d'un pixel du dessin au combat (unités du jeu, écran de 720 de large), comme jeu.py
MAXW = 2048 // UP * UP     # largeur de la planche avant agrandissement : 4096 au plus une fois agrandie
ANIMS = ('pose', 'attaque', 'speciale')


# ---------------------------------------------------------------- 1) lire le build.py : les calques de chaque image
def load_build(name):
    path = os.path.join(HERE, name, 'build.py')
    spec = importlib.util.spec_from_file_location(f'build_{name.replace("-", "_")}', path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(path))
    spec.loader.exec_module(mod)
    sys.path.pop(0)
    return mod


def capture(mod):
    """appelle build_all() en gardant l'image rendue par chaque appel à compose() : {anim: [(image, ms)…]}.
    On garde l'image FINALE de compose (exactement celle du GIF), quels que soient ses arguments (positionnels ou
    nommés : obj, solid, ghosts, veil, shake, tint…) et sa façon de poser les calques translucides. La découpe qui suit
    (personnage / sur la cible / projectile) se fait par colonnes : elle n'a pas besoin des calques séparés."""
    orig = mod.compose
    calls, heroes = [], {}
    # `calques` (JEU) : on garde aussi l'image du personnage SEUL (compose sans ses effets fx_…), pour couper les
    # effets sans jamais couper le personnage (voir split)
    seul = any(d.get('calques') for d in getattr(mod, 'JEU', {}).values())
    sig = inspect.signature(orig) if seul else None

    def spy(*args, **kw):
        out = orig(*args, **kw)
        calls.append(out)
        if seul:
            b = sig.bind(*args, **kw)
            for k in list(b.arguments):
                if k.startswith('fx'):
                    b.arguments[k] = None
            heroes[id(out)] = orig(*b.args, **b.kwargs)
        return out

    mod.compose = spy
    try:
        anims = mod.build_all()
    finally:
        mod.compose = orig
    res, k = {}, 0
    for name in ANIMS:
        fr = []
        for img, ms in anims[name]:
            # chaque image rendue doit être celle d'un appel à compose (dans l'ordre)
            while k < len(calls) and calls[k] is not img:
                k += 1
            if k >= len(calls):
                raise SystemExit(f'{mod.__name__} : une image de « {name} » ne vient pas de compose() '
                                 '(voir consignes/export-jeu.md, cas particuliers)')
            hero = heroes.get(id(img))
            fr.append((img.copy(), int(ms), None if hero is None else hero.copy()))
            k += 1
        res[name] = fr
    return res


# ---------------------------------------------------------------- 2) séparer : personnage / projectile / sur la cible
def alpha(img):
    return img[:, :, 3] > 0


def shift(img, dx, dy=0):
    """décale une image d'un nombre entier de pixels (rien n'est lissé)"""
    out = np.zeros_like(img)
    H, W = img.shape[:2]
    xs0, xs1 = max(0, -dx), min(W, W - dx)
    ys0, ys1 = max(0, -dy), min(H, H - dy)
    if xs1 > xs0 and ys1 > ys0:
        out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = img[ys0:ys1, xs0:xs1]
    return out


def cols(img, x0=None, x1=None):
    out = np.zeros_like(img)
    a, b = (x0 or 0), (img.shape[1] if x1 is None else x1)
    out[:, max(0, a):max(0, b)] = img[:, max(0, a):max(0, b)]
    return out


def bbox(img):
    a = alpha(img)
    if not a.any():
        return None
    ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def head_point(img):
    """le bout avant d'un projectile (il vole vers la droite) : la colonne la plus à droite, sa hauteur moyenne"""
    a = alpha(img)
    xs = np.nonzero(a.any(0))[0]
    x1 = xs.max()
    band = a[:, max(0, x1 - 3):x1 + 1]
    ys = np.nonzero(band.any(1))[0]
    return float(x1 + 1), float(ys.mean() + 0.5)


def flight(heads, img0, ms):
    """(vitesse en pixels du dessin par seconde, pente en radians) du vol d'un projectile dans le GIF. heads = [(image,
    (x, y) du bout)…] pendant le vol. Le bout avance d'une image à l'autre : on prend du premier au dernier bout qui a
    vraiment avancé (un bout coincé au bord de la toile ou déjà sur la cible ne compte pas)."""
    start = lambda i: sum(ms[:i])
    moves = [(a, b) for a, b in zip(heads, heads[1:]) if b[1][0] - a[1][0] >= 8]
    if moves:
        (i0, h0), (i1, h1) = moves[0][0], moves[-1][1]
        dx, dy = h1[0] - h0[0], h1[1] - h0[1]
        return dx / max(1, start(i1) - start(i0)) * 1000, math.atan2(dy, dx)
    # une seule image de vol : le projectile a quitté l'arme (`depuis`) au début de cette image ; sa pente, de sa
    # queue (au bord `depuis`) à son bout
    i0, h0 = heads[0]
    a = alpha(img0)
    xs = np.nonzero(a.any(0))[0]
    tail = a[:, xs.min():xs.min() + 4]
    ty = float(np.nonzero(tail.any(1))[0].mean() + 0.5)
    run = max(8.0, h0[0] - xs.min())
    return run / max(1, ms[i0]) * 1000, math.atan2(h0[1] - ty, run)


def pieces(m):
    """numérote les morceaux d'un masque (pixels voisins, diagonales comprises) : 0 = vide"""
    H, W = m.shape
    lab = np.where(m, np.arange(1, H * W + 1).reshape(H, W), 0)
    big = H * W + 1
    while True:
        p = np.pad(np.where(m, lab, big), 1, constant_values=big)
        low = np.min([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)], axis=0)
        new = np.where(m, np.minimum(lab, low), 0)
        flat = new.ravel()
        new = np.where(m, flat[np.maximum(new, 1) - 1], 0)      # saut de pointeur : bien plus rapide
        if np.array_equal(new, lab):
            return lab
        lab = new


def take(L, hero, x0):
    """(ce qui part, ce qui reste) : sans `hero`, tout ce qui est à droite de la colonne x0 part. Avec `hero` (l'image
    du personnage seul, JEU `calques`) : seuls les EFFETS à droite de x0 partent, le personnage n'est jamais coupé
    (là où un effet le couvrait, on retrouve le personnage)."""
    if hero is None:
        return cols(L, x0, None), cols(L, None, x0)
    fx = alpha(L) & ~(alpha(hero) & np.all(L == hero, axis=2))
    # les effets partent par morceaux entiers (pixels qui se touchent) : un morceau part s'il commence à droite de
    # x0, sinon il reste en entier. Rien n'est jamais tranché en ligne droite.
    lab = pieces(fx)
    keep = np.unique(lab[:, :max(0, x0)])
    fx &= ~np.isin(lab, keep[keep > 0])
    gone = np.zeros_like(L)
    gone[fx] = L[fx]
    rest = L.copy()
    rest[fx] = hero[fx]
    return gone, rest


def seams(left, right, x, run=8):
    """la plus longue suite de rangées où une coupe à la colonne x tranche un morceau : `left` a un pixel en x − 1 ET
    `right` en x (le même dessin coupé net, en ligne droite). 0 si rien n'est tranché."""
    if x is None or x <= 0 or x >= left.shape[1]:
        return 0
    # deux dessins qui se touchent par leur contour (encre sombre) ne sont pas coupés : on ne compte pas ces rangées
    ink = lambda c: c[:, :3].max(1) < 64
    m = alpha(left)[:, x - 1] & alpha(right)[:, x] & ~ink(left[:, x - 1]) & ~ink(right[:, x])
    best = cur = 0
    for v in m:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def split(mod, layers, name):
    """renvoie {'perso': [img…], 'cible': [img|None…], 'proj': [img|None…], 'ms': […], réglages…} pour une animation.
    Tous les calques (personnage compris : une flèche plantée dans l'ennemi est souvent dessinée avec lui) sont coupés
    à la colonne `coupe` ; pendant le vol (`tir`) ou le jet (`rayon`), ce qui est à droite de `depuis` part avec le projectile."""
    sol = tuple(mod.SOL)
    jeu = dict(getattr(mod, 'JEU', {}).get(name, {}))
    genre = jeu.get('genre', 'pose' if name == 'pose' else 'sort')
    n = len(layers)
    avance = list(jeu.get('avance', [0] * n))
    assert len(avance) == n, f'{name} : avance a {len(avance)} valeurs pour {n} images'
    cible = jeu.get('cible')
    coupe = jeu.get('coupe', (cible[0] - 36) if cible else None)
    if genre in ('pose', 'equipe'):
        coupe = None
    coupes = list(coupe) if isinstance(coupe, (list, tuple)) else [coupe] * n
    assert len(coupes) == n, f'{name} : coupe a {len(coupes)} valeurs pour {n} images'
    vol = jeu.get('tir') or jeu.get('rayon')
    depuis = jeu.get('depuis', None)
    if vol and depuis is None:
        raise SystemExit(f'{mod.__name__} {name} : `depuis` manque (la colonne où le projectile quitte le personnage)')
    retour = jeu.get('retour')
    out = {'genre': genre, 'perso': [], 'cible': [], 'proj': [], 'retour': [], 'ms': [], 'jeu': jeu, 'sol': sol,
           'alertes': []}
    calques = bool(jeu.get('calques'))
    out['coupes'] = []
    for i, (L, ms, hero) in enumerate(layers):
        dx = -int(round(avance[i]))
        flying = bool(vol) and vol[0] <= i < vol[1]
        back = bool(retour) and retour[0] <= i < retour[1]
        c = coupes[i]
        proj = tgt = ret = np.zeros_like(L)
        hero = hero if calques else None
        cuts = []
        if flying:
            proj, L = take(L, hero, depuis)
            cuts.append(('proj', depuis))
        if back:
            # l'arme qui revient (boomerang) : le jeu la fait voler de la cible jusqu'à la main
            ret, L = take(L, hero, depuis)
        if c is not None:
            tgt, L = take(L, hero, c)
            cuts.append(('cible', c))
        out['coupes'].append(cuts)
        # contrôle : une coupe qui tranche un dessin en ligne droite se verra au combat (le morceau de gauche reste
        # près du lanceur, celui de droite part sur la cible ou vole). Au corps à corps, le jeu recolle les morceaux.
        if genre != 'melee':
            for kind, x in cuts:
                n_ = seams(L, proj if kind == 'proj' else tgt, x)
                if n_ >= 8:
                    out['alertes'].append(f'{name} {i} : coupe {"depuis" if kind == "proj" else "coupe"}={x} tranche '
                                          f'un dessin sur {n_} rangées (bord droit visible)')
        perso = shift(L, dx)
        out['perso'].append(perso)
        out['cible'].append(tgt if alpha(tgt).any() else None)
        out['proj'].append(proj if alpha(proj).any() else None)
        out['retour'].append(ret if alpha(ret).any() else None)
        out['ms'].append(ms)
    return out


# ---------------------------------------------------------------- 3) la planche du jeu (images rognées, rangées)
class Sheet:
    def __init__(self):
        self.imgs, self.rects, self.keys = [], [], {}

    def add(self, img, anchor):
        """ajoute une image rognée ; renvoie son numéro. anchor = le point (toile) qui sert de repère dans le jeu"""
        bb = bbox(img)
        if bb is None:
            return -1
        x0, y0, x1, y1 = bb
        crop = img[y0:y1, x0:x1]
        key = hashlib.md5(crop.tobytes() + bytes(str((x0 - anchor[0], y0 - anchor[1])), 'ascii')).hexdigest()
        if key in self.keys:
            return self.keys[key]
        self.imgs.append(crop)
        # [x, y, l, h, ax, ay] : place dans la planche (remplie à l'emballage), puis coin haut-gauche par rapport au repère
        self.rects.append([0, 0, x1 - x0, y1 - y0, int(x0 - round(anchor[0])), int(y0 - round(anchor[1]))])
        self.keys[key] = len(self.imgs) - 1
        return self.keys[key]

    def pack(self):
        """rangées (les plus hautes d'abord), 1 pixel d'air entre deux images"""
        order = sorted(range(len(self.imgs)), key=lambda i: -self.rects[i][3])
        x = y = rowh = 0
        for i in order:
            w, h = self.rects[i][2], self.rects[i][3]
            if x + w > MAXW:
                x, y, rowh = 0, y + rowh + 1, 0
            self.rects[i][0], self.rects[i][1] = x, y
            x += w + 1
            rowh = max(rowh, h)
        Wt, Ht = MAXW if y else x, y + rowh
        if Ht * UP > 4096:
            print(f'  ATTENTION : planche de {Wt * UP} × {Ht * UP} (plus de 4096 de haut)')
        im = np.zeros((Ht, Wt, 4), np.uint8)
        for img, (x, y, w, h, _, _) in zip(self.imgs, self.rects):
            im[y:y + h, x:x + w] = img
        # rognée à droite au plus juste
        used = max(r[0] + r[2] for r in self.rects)
        return Image.fromarray(im[:, :used], 'RGBA')


def export(name, voir=None):
    mod = load_build(name)
    src = mod.SRC
    cid = src['id']
    layers = capture(mod)
    sheet = Sheet()
    meta = {'name': name, 'anims': {}}
    parts = {}
    for an in ANIMS:
        p = split(mod, layers[an], an)
        parts[an] = p
        for msg in p['alertes']:
            print(f'  ATTENTION {name} {msg} : voir consignes/export-jeu.md (`coupe` par image, `calques`)')
        sol = p['sol']
        jeu = p['jeu']
        a = {'genre': p['genre'], 'ms': p['ms'], 'f': [sheet.add(img, sol) for img in p['perso']]}
        cible = jeu.get('cible')
        if cible:
            foot = (cible[0], sol[1])                         # les pieds de l'ennemi imaginé
            a['portee'] = int(round(cible[0] - sol[0]))       # pieds à pieds au moment du coup (le jeu s'en sert au corps à corps)
            a['haut'] = int(round(sol[1] - cible[1]))         # hauteur du coup au-dessus du sol
            if any(c is not None for c in p['cible']):
                a['cible'] = [sheet.add(img, foot) if img is not None else -1 for img in p['cible']]
        if p['genre'] != 'pose':
            a['coup'] = int(jeu.get('coup', 0))
        if jeu.get('charge'):
            a['charge'] = list(jeu['charge'])
        tir = jeu.get('tir')
        if tir:
            heads = [(i, head_point(img)) for i, img in enumerate(p['proj']) if img is not None]
            if not heads:
                raise SystemExit(f'{name} {an} : aucune image de projectile entre {tir[0]} et {tir[1]}')
            i0, h0 = heads[0]
            # au ras du sol (`rase`) : chaque image repérée par son bout ET le sol, pour que sa base reste au sol quand
            # l'image change (avant : par la hauteur de son bout, qui bouge d'une image à l'autre)
            reps = [(i, (hp[0], float(sol[1])) if jeu.get('rase') else hp) for i, hp in heads]
            a['proj'] = [sheet.add(p['proj'][i], hp) for i, hp in reps]
            a['projMs'] = [p['ms'][i] for i, _ in heads]
            a['depart'] = i0                                   # l'image où le projectile part
            a['bouche'] = [int(round(h0[0] - sol[0])), int(round(reps[0][1][1] - sol[1]))]   # d'où il part (par rapport aux pieds)
            # sa vitesse (pixels du dessin par seconde) et l'angle de son vol dans le GIF (le dessin du projectile est
            # penché ainsi : le jeu tourne de la différence) : mesurés sur le mouvement du bout du projectile d'une
            # image de vol à l'autre ; avec une seule image de vol, du bout du projectile à `cible`. JEU peut les imposer.
            vitesse, pente = flight(heads, p['proj'][heads[0][0]], p['ms'])
            a['vitesse'] = int(round(jeu.get('vitesse', vitesse)))
            a['pente'] = round(float(jeu.get('pente', pente)), 3)
            if jeu.get('arc'):
                a['arc'] = int(jeu['arc'])
            if jeu.get('retour'):
                # le retour : chaque image repérée par son milieu, que le jeu amène de la cible à la main
                r0, r1 = jeu['retour']
                mid = lambda img: ((bbox(img)[0] + bbox(img)[2]) / 2, (bbox(img)[1] + bbox(img)[3]) / 2)
                a['retour'] = [sheet.add(p['retour'][i], mid(p['retour'][i])) if p['retour'][i] is not None else -1
                               for i in range(r0, r1)]
                a['retourDe'] = int(r0)
            if jeu.get('rase'):
                a['rase'] = 1                                  # il court au ras du sol (vague, pics) : à plat, à sa hauteur
        ray = jeu.get('rayon')
        if ray:
            # un jet continu (souffle de feu, rayon) : chaque image part de la bouche ; le jeu l'étire jusqu'à la cible
            idx = [i for i, img in enumerate(p['proj']) if img is not None]
            first = p['proj'][idx[0]]
            band = alpha(first)[:, jeu['depuis']:jeu['depuis'] + 4]
            ys = np.nonzero(band.any(1))[0]
            mouth = (float(jeu['depuis']), float(ys.mean() + 0.5) if len(ys) else float(cible[1]))
            a['rayon'] = [sheet.add(p['proj'][i], mouth) if p['proj'][i] is not None else -1
                          for i in range(len(p['ms']))]
            a['bouche'] = [int(round(mouth[0] - sol[0])), int(round(mouth[1] - sol[1]))]
            a['longueur'] = int(round(cible[0] - mouth[0]))   # de la bouche à la cible, dans le GIF
        if jeu.get('elan'):
            a['elan'] = list(jeu['elan'])
        if p['genre'] == 'melee':
            av = list(jeu.get('avance', [0] * len(p['ms'])))
            if max(av) > 3:
                a['avance'] = [int(round(v)) for v in av]
        meta['anims'][an] = a
    img = sheet.pack()
    os.makedirs(OUT, exist_ok=True)
    big = img.resize((img.width * UP, img.height * UP), Image.NEAREST)
    big.save(os.path.join(OUT, f'{cid}.webp'), lossless=True, quality=100, method=6)
    # la silhouette au repos (première image de la pose) : le haut de la tête et la largeur au sol, pour la barre de vie et l'ombre
    pose0 = parts['pose']['perso'][0]
    sol = parts['pose']['sol']
    bb = bbox(pose0)
    a = alpha(pose0)
    low = a[max(0, sol[1] - 14):sol[1] + 1]
    xs = np.nonzero(low.any(0))[0]
    meta['top'] = int(sol[1] - bb[1])
    # l'avant du corps (vers l'ennemi) : 3 rangées sur 4 s'arrêtent avant cette colonne (par rapport aux pieds). Un
    # gros (crabe, araignée) est attaqué de plus loin au corps à corps (hd-fight.ts)
    rights = [np.nonzero(r)[0].max() + 1 for r in a if r.any()]
    meta['avant'] = int(np.percentile(rights, 75) - sol[0])
    meta['sol'] = [int(xs.min() - sol[0]), int(xs.max() + 1 - sol[0])]
    # le visage (portrait du choix des combattants) : un carré en haut de la silhouette au repos, centré sur la tête ;
    # [x, y, côté] dans la planche (pixels du dessin)
    side = int(min(56, max(28, round((sol[1] - bb[1]) * 0.45))))
    head = a[bb[1]:bb[1] + side]
    cx = float(np.nonzero(head)[1].mean())
    r0 = sheet.rects[meta['anims']['pose']['f'][0]]
    side = min(side, r0[2])                                  # dans l'image (rien des voisines de la planche)
    x = int(np.clip(round(r0[0] + cx - bb[0] - side / 2), r0[0], r0[0] + r0[2] - side))
    meta['visage'] = [x, int(r0[1]), side]
    if src.get('cadre') and src.get('tete'):
        # grand boss (case « cadre: », voir hd.case) : le haut de la silhouette est le bout des ailes, pas la tête ; le
        # carré du visage est pris sur la boîte « tete » du dessin (grille -> toile du build.py -> planche)
        tx0, ty0, tx1, ty1 = src['tete']
        ox, oy = sol[0] - src['sol'][0], sol[1] - src['sol'][1]
        side = int(min(r0[2], r0[3], max(tx1 - tx0, ty1 - ty0) + 1))
        hx, hy = (tx0 + tx1) / 2 + ox - bb[0], (ty0 + ty1) / 2 + oy - bb[1]
        x = int(np.clip(round(r0[0] + hx - side / 2), r0[0], r0[0] + r0[2] - side))
        y = int(np.clip(round(r0[1] + hy - side / 2), r0[1], r0[1] + r0[3] - side))
        meta['visage'] = [x, y, side]
    meta['frames'] = sheet.rects
    meta['size'] = [img.width * UP, img.height * UP]
    print(f'{name} ({cid}) : {len(sheet.rects)} images, planche {img.width * UP} × {img.height * UP}')
    if voir:
        controle(name, parts, voir)
    return cid, meta


# ---------------------------------------------------------------- planche de contrôle (pour l'animateur)
def controle(name, parts, folder):
    os.makedirs(folder, exist_ok=True)
    k = 2
    rows = []
    for an in ANIMS:
        p = parts[an]
        H, W = p['perso'][0].shape[:2]
        for i in range(len(p['ms'])):
            cell = Image.new('RGBA', (W, H), (236, 238, 244, 255))
            d = ImageDraw.Draw(cell)
            for x in range(0, W, 20):
                d.line([(x, 0), (x, H)], fill=(220, 222, 230, 255) if x % 100 else (190, 194, 210, 255))
            sol = p['sol']
            d.line([(0, sol[1]), (W, sol[1])], fill=(170, 200, 170, 255))
            jeu = p['jeu']
            if jeu.get('cible'):
                cx, cy = jeu['cible']
                d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], outline=(220, 40, 40, 255))
                c = jeu.get('coupe', cx - 36)
                c = c[i] if isinstance(c, (list, tuple)) else c
                if c is not None:
                    d.line([(c, 0), (c, H)], fill=(240, 150, 150, 255))
            cell.alpha_composite(Image.fromarray(p['perso'][i]))
            if p['cible'][i] is not None:
                t = p['cible'][i].copy()
                t[alpha(t), :3] = (t[alpha(t), :3] * 0.5 + np.array([255, 60, 60]) * 0.5).astype(np.uint8)
                cell.alpha_composite(Image.fromarray(t))
            for lay, col in (('proj', (40, 80, 255)), ('retour', (40, 200, 80))):
                if p[lay][i] is not None:
                    t = p[lay][i].copy()
                    t[alpha(t), :3] = (t[alpha(t), :3] * 0.5 + np.array(col) * 0.5).astype(np.uint8)
                    cell.alpha_composite(Image.fromarray(t))
            d = ImageDraw.Draw(cell)
            tag = f'{an} {i} {p["ms"][i]}ms'
            if jeu.get('coup') == i:
                tag += ' COUP'
            ch = jeu.get('charge')
            if ch and ch[0] <= i <= ch[1]:
                tag += ' charge'
            d.text((3, 2), tag, fill=(20, 20, 30, 255))
            rows.append((an, cell))
    W, H = rows[0][1].size
    per = 6
    lines = (len(rows) + per - 1) // per
    out = Image.new('RGBA', (per * W * k, lines * H * k), (255, 255, 255, 255))
    for j, (_, c) in enumerate(rows):
        out.paste(c.resize((W * k, H * k), Image.NEAREST), ((j % per) * W * k, (j // per) * H * k))
    path = os.path.join(folder, f'export-{name}.png')
    out.convert('RGB').save(path)
    print('  contrôle :', path)


# ---------------------------------------------------------------- les effets reçus par les alliés (../effets/sortie)
def export_effets():
    """chaque effet : une planche (images rognées du dos et de devant) ; repère = les pieds (64, 116)"""
    d = json.load(open(os.path.join(HERE, 'effets', 'sortie', 'effets.json')))
    res = {}
    os.makedirs(os.path.join(OUT, 'fx'), exist_ok=True)
    for key, e in d['effets'].items():
        fw, fh = e['taille']
        feet = e['pieds']
        sheet = Sheet()
        lay = {}
        for side in ('dos', 'devant'):
            strip = np.array(Image.open(os.path.join(HERE, 'effets', 'sortie', e[side])).convert('RGBA'))
            lay[side] = [sheet.add(strip[:, i * fw:(i + 1) * fw], feet) for i in range(e['images'])]
        img = sheet.pack()
        img.resize((img.width * UP, img.height * UP), Image.NEAREST).save(os.path.join(OUT, 'fx', f'{key}.webp'),
                                                                          lossless=True, quality=100, method=6)
        ec = e.get('eclat') or {}
        res[key] = {'ms': e['durees_ms'], 'dos': lay['dos'], 'devant': lay['devant'], 'frames': sheet.rects,
                    'size': [img.width * UP, img.height * UP], 'boucle': bool(e.get('boucle')),
                    'eclat': [ec.get('couleur', '#ffffff'), {int(k): v for k, v in ec.get('par_image', {}).items()}]}
    print(f'{len(res)} effets reçus')
    return res


# ---------------------------------------------------------------- 4) le fichier du jeu
def read_meta():
    if not os.path.exists(META):
        return {'chars': {}, 'fx': {}}
    txt = open(META).read()
    return json.loads(txt[txt.index('{'):txt.rindex('}') + 1])


def write_meta(m):
    with open(META, 'w') as fh:
        fh.write('// Généré par refonte-graphique/pixel/hd/anim/jeu_export.py : ne pas modifier à la main.\n')
        fh.write('// Animations HD du combat. Planche art/hd/<id>.webp (agrandie ×up) ; frames : [x, y, l, h, ax, ay] en pixels du\n')
        fh.write('// dessin, (ax, ay) = coin haut-gauche par rapport au repère (pieds du personnage, pieds de la cible, bout du\n')
        fh.write('// projectile). Une animation : f (images du personnage, en place), ms, genre, coup, cible (images posées aux\n')
        fh.write('// pieds de la cible, -1 = rien), proj/projMs/depart/bouche/vitesse (le projectile), charge [i0, i1], portee, haut.\n')
        body = json.dumps({'up': UP, 'scale': SCALE, 'chars': m['chars'], 'fx': m['fx']}, separators=(',', ':'), default=int)
        fh.write('export const HD_ANIM = ' + body + ' as const;\n')
    print(META)


def main(argv):
    voir = None
    if '--voir' in argv:
        i = argv.index('--voir')
        voir = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    fx = None
    if '--effets' in argv:
        argv = [a for a in argv if a != '--effets']
        fx = export_effets()
    done = [export(name, voir) for name in argv]
    # plusieurs agents peuvent exporter en même temps : on relit hd-meta.ts sous verrou juste avant de l'écrire
    import fcntl
    import tempfile
    with open(os.path.join(tempfile.gettempdir(), 'fuze-hd-meta.lock'), 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        m = read_meta()
        if fx is not None:
            m['fx'] = fx
        for cid, meta in done:
            m['chars'][cid] = meta
        write_meta(m)


if __name__ == '__main__':
    main(sys.argv[1:])
