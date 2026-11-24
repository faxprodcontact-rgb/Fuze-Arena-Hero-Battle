# Arachné (myths-10, terre, assassin) : animations — pose (respiration), attaque de base, attaque spéciale.
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/arachne/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-arachne-pose.gif, anim-arachne-attaque.gif,
# anim-arachne-speciale.gif, anim-arachne-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-arachne-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py decoupe   → sortie de contrôle : la découpe des morceaux en couleurs (dans le brouillon)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py, dont les outils sont recopiés ici) :
#   - le dessin validé (../../arachne.txt) n'est PAS modifié : on le découpe en morceaux. Calque « araignee » :
#     le corps (abdomen + céphalothorax) et les HUIT pattes, chacune à part (repérée par son squelette : hanche,
#     genou, pointe) ; calque « femme » : tête, bras proche + dague, bras lointain + dague, épaulière, buste ;
#   - une patte bouge en se pliant : chaque pixel de la patte suit le déplacement de ses articulations (hanche,
#     genou, pointe), au pixel près (on va chercher le pixel source : jamais de trou, jamais de lissage) ; la pointe
#     reste plantée au sol sauf quand la patte se lève ;
#   - les pattes qui se lèvent pour frapper sont REDESSINÉES (cuisse, genou pointu, jambe effilée, anneaux rouges,
#     épines), avec les tons de chitine du dessin et la lumière en haut à droite ;
#   - le bras proche qui frappe est REDESSINÉ (bras de peau, brassard de chitine) et la dague retracée à chaque angle
#     (lame courbe d'acier : dos sombre, fil clair, éclat ; garde d'or, poignée rouge) ; le poing est celui du dessin ;
#   - une araignée : mouvements nerveux et saccadés (images tenues, puis changement brusque), les pattes ne bougent
#     jamais toutes ensemble ;
#   - les effets (toile, pierre, cristaux, poussière) ont leur petite palette, sans contour noir, en formes courbes ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'arachne'
SRC = hd.load(os.path.join(HD, 'arachne.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)
BROUILLON = '/tmp/claude-0/-home-user-Fuze-Arena-Hero-Battle/4f44ed70-e2c6-5441-ade8-1b1349ae17e5/scratchpad/anim-arachne'

# ---------------------------------------------------------------- palette des effets (toile, pierre, cristaux, poussière)
# Lettres libres (le héros utilise 1-5, a-i, k-z sauf j et l, A-F, L, M).
FXPAL = {
    'G': (255, 252, 244),   # soie, éclat
    'H': (232, 226, 236),   # soie
    'I': (178, 168, 198),   # soie, ombre (lavande)
    'J': (120, 108, 150),   # soie, creux
    'K': (226, 202, 166),   # pierre, lumière (grès clair)
    'N': (172, 136, 106),   # pierre, ton de base (grès brun)
    'O': (122, 90, 78),     # pierre, ombre
    'P': (82, 56, 62),      # pierre, creux (brun violacé)
    'Q': (64, 38, 48),      # pierre, fond des fissures
    'R': (255, 214, 196),   # cristal, éclat
    'S': (255, 128, 104),   # cristal, lumière (grenat clair)
    'T': (206, 50, 66),     # cristal (grenat, comme les anneaux de ses pattes)
    'U': (124, 22, 52),     # cristal, ombre
    'V': (240, 226, 204),   # poussière, lumière
    'W': (206, 184, 156),   # poussière
    'X': (160, 136, 122),   # poussière, ombre
    'Y': (118, 98, 104),    # poussière, creux
    'j': (255, 246, 214),   # étincelle (blanc doré)
    'l': (255, 255, 255),   # blanc pur (éclair d'impact)
}
assert not set(FXPAL) & set(PAL), set(FXPAL) & set(PAL)
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du héros est posé en SOL ; l'ennemi est à droite (vers x = 215).
W, H = 268, 176
SOL = (84, 160)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
FOE = (214, GROUND)                                        # le pied de l'ennemi (toile)


def g2c(x, y):
    return x + OX, y + OY


def grid(rows):
    return np.array([list(r) for r in rows])


SPIDER = grid(SRC['calques'][0][2])
WOMAN = grid(SRC['calques'][1][2])
GH, GW = SPIDER.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


SKIN = set('12345')
CHIT = set('ABCDEF')
REDS = set('rstuv')

# ---------------------------------------------------------------- découpe de l'araignée : le corps et les 8 pattes
# Chaque patte : son squelette (points de la grille, de la hanche à la pointe), l'indice du GENOU dans cette liste,
# son épaisseur (rayon de capture autour du squelette), et 'devant' (True : elle passe devant le corps, elle garde
# les pixels qui recouvrent l'abdomen ; False : elle est derrière, le corps garde les pixels communs).
LEGS = {
    # côté gauche (arrière)
    'L1': dict(sk=[(35, 67), (25, 55), (22, 61), (17, 76), (12, 90), (9, 101), (6.5, 116)], knee=1,
               r=[3.6, 3.0, 3.0, 3.0, 3.0, 3.0], front=False),
    'L2': dict(sk=[(67, 100), (31, 81), (26, 88), (23, 92), (19.5, 97), (17.5, 100), (16, 116)], knee=1,
               r=[4.6, 3.4, 3.4, 3.4, 3.0, 2.6], front=True),
    'L3': dict(sk=[(45, 95), (42, 101), (40.5, 106), (39, 116)], knee=0, r=[3.2, 3.0, 2.4], front=False),
    'L4': dict(sk=[(57, 97), (56.5, 104), (55.5, 116)], knee=0, r=[2.4, 2.2], front=False),
    # côté droit (avant, vers l'ennemi)
    'R1': dict(sk=[(83, 88), (88, 80.5), (90.5, 86), (93, 97), (93.5, 101), (93, 116)], knee=1,
               r=[3.0, 3.2, 3.8, 3.0, 2.4], front=True),
    'R2': dict(sk=[(86, 80.5), (98.5, 70.5), (100, 74), (101.5, 82), (103, 92), (103.5, 100), (103, 116)], knee=1,
               r=[3.8, 3.4, 2.4, 2.4, 2.4, 2.2], front=False),
    'R3': dict(sk=[(91, 90), (102, 76.5), (104, 74.5), (106.5, 79), (111, 89), (114.5, 97), (116.5, 116)], knee=2,
               r=[4.4, 3.0, 3.2, 4.4, 4.6, 2.6], front=True),
    'R4': dict(sk=[(101, 75), (113.5, 67), (115, 73), (118, 85), (121, 93), (123.5, 116)], knee=1,
               r=[3.0, 2.8, 3.0, 3.0, 2.6], front=False),
}
# ordre de pose, du fond vers le devant
SPIDER_ORDER = ['L1', 'R4', 'R2', 'L3', 'L4', 'corps', 'L2', 'R3', 'R1']


def seg_dist(p, a, b):
    """distance du point p au segment ab, et le paramètre t (0..1) du point le plus proche"""
    a, b = np.array(a, float), np.array(b, float)
    v = b - a
    t = float(np.clip((p - a) @ v / max(v @ v, 1e-9), 0, 1))
    return float(np.linalg.norm(p - (a + t * v))), t


def sk_locate(sk, p):
    """(distance, abscisse) du point p au squelette : abscisse = indice du segment + t"""
    best = (1e9, 0.0)
    for i in range(len(sk) - 1):
        d, t = seg_dist(p, sk[i], sk[i + 1])
        if d < best[0]:
            best = (d, i + t)
    return best


def sk_radius(L, s):
    i = min(int(s), len(L['r']) - 1)
    return L['r'][i]


def body_mask():
    """l'abdomen (ellipse) et le céphalothorax : là où une patte « derrière » ne prend rien"""
    ab = ((XX + 0.5 - 43.5) / 23.5) ** 2 + ((YY + 0.5 - 80.0) / 18.0) ** 2 <= 1.0
    ce = (XX >= 60) & (XX <= 90) & (YY >= 83) & (YY <= 103)
    return ab | ce


BODYM = body_mask()
LABEL = np.full((GH, GW), '', dtype=object)
ABSC = np.zeros((GH, GW))            # abscisse le long du squelette de sa patte (pour le pliage)
filled = SPIDER != '.'
for y, x in zip(*np.nonzero(filled)):
    p = np.array([x + 0.5, y + 0.5])
    best, who = 1e9, 'corps'
    for name, L in LEGS.items():
        d, s = sk_locate(L['sk'], p)
        if d <= sk_radius(L, s) and d - sk_radius(L, s) < best and (L['front'] or not BODYM[y, x]):
            best, who = d - sk_radius(L, s), name
            ABSC[y, x] = s
    if who == 'corps' and not BODYM[y, x]:
        # pixel isolé hors du corps (une épine, un bord) : il va à la patte la plus proche
        for name, L in LEGS.items():
            d, s = sk_locate(L['sk'], p)
            if d - sk_radius(L, s) < best:
                best, who = d - sk_radius(L, s), name
                ABSC[y, x] = s
    LABEL[y, x] = who

PARTS = {}
for name in list(LEGS) + ['corps']:
    PARTS[name] = np.where(LABEL == name, SPIDER, '.')


def fill_under(part, holes, passes=4):
    """repeint les pixels du corps cachés sous une patte de devant (pour qu'aucun trou n'apparaisse quand la patte
    bouge) : chaque trou prend le ton le plus fréquent de ses voisins du corps, de proche en proche"""
    out = part.copy()
    todo = holes & (out == '.')
    for _ in range(passes):
        new = out.copy()
        for y, x in zip(*np.nonzero(todo)):
            nb = [out[y + dy, x + dx] for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1))
                  if 0 <= y + dy < GH and 0 <= x + dx < GW and out[y + dy, x + dx] != '.']
            if len(nb) >= 3:
                new[y, x] = max(set(nb), key=nb.count)
        todo &= new == '.'
        out = new
    return out


# sous les pattes de devant, le corps continue (repeint une fois pour toutes)
_under = np.zeros((GH, GW), bool)
for _n in ('L2', 'R1', 'R3'):
    _under |= (PARTS[_n] != '.') & BODYM
PARTS['corps'] = fill_under(PARTS['corps'], _under, passes=8)


def label_image(path, k=6):
    cols = {'corps': (120, 120, 120), 'L1': (230, 60, 60), 'L2': (60, 200, 60), 'L3': (60, 60, 230),
            'L4': (230, 200, 40), 'R1': (230, 60, 230), 'R2': (40, 200, 220), 'R3': (240, 140, 40),
            'R4': (140, 80, 220)}
    im = Image.new('RGB', (GW * k, GH * k), (250, 250, 250))
    d = ImageDraw.Draw(im)
    for y, x in zip(*np.nonzero(filled)):
        c = np.array(cols[LABEL[y, x]])
        base = np.array(PAL[SPIDER[y, x]])
        c = tuple(int(v) for v in (c * 0.6 + base * 0.4))
        d.rectangle([x * k, y * k, x * k + k - 1, y * k + k - 1], fill=c)
    for name, L in LEGS.items():
        pts = [(px * k, py * k) for px, py in L['sk']]
        d.line(pts, fill=(0, 0, 0), width=1)
    im.crop((0, 50 * k, GW * k, GH * k)).save(path)




# ---------------------------------------------------------------- découpe de la femme
_wf = WOMAN != '.'
WP = {}
_restw = WOMAN.copy()


def takew(mask):
    part = np.where(mask, _restw, '.')
    _restw[mask] = '.'
    return part


WP['tete'] = takew(_wf & (YY <= 46) & (XX >= 58))
WP['brasP'] = takew(_wf & ((XX <= 57) | ((XX <= 60) & (YY >= 54) & (YY <= 61) & isin(WOMAN, SKIN))))
WP['epaule'] = takew(_wf & (XX >= 58) & (XX <= 74) & (YY >= 44) & (YY <= 58) & isin(WOMAN, CHIT))
WP['brasL'] = takew(_wf & (XX >= 99) & (YY >= 52) & (YY <= 68))
WP['buste'] = _restw.copy()
BREATH_Y = SRC['souffle']                 # 66 : au-dessus, la femme monte d'un pixel quand elle inspire
BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty():
    return np.full((H, W), '.', dtype='<U1')


def blit(canvas, part, dx=0, dy=0, swap=None):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + int(dy) + OY, xs + int(dx) + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = part[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def stretch_cols(part, x_cut, n):
    """le morceau s'allonge vers la droite de n colonnes : tout ce qui est à droite de x_cut glisse de n pixels,
    la colonne x_cut est répétée dans l'écart (un bras qui se tend, sans trou)"""
    if n == 0:
        return part
    out = part.copy()
    if n < 0:                                   # il se replie : les colonnes x_cut..x_cut+|n| disparaissent
        out[:, x_cut:GW + n] = part[:, x_cut - n:]
        out[:, GW + n:] = '.'
        return out
    out[:, x_cut + n:] = part[:, x_cut:GW - n]
    for i in range(n):
        out[:, x_cut + i] = part[:, x_cut]
    return out


def swell(part, x_max, y_mid, x_mid, n=1):
    """l'abdomen palpite : la moitié haute (rangées < y_mid) monte de n pixels et la moitié gauche (colonnes < x_mid)
    recule de n pixels, la rangée / colonne du milieu est répétée — seulement pour les colonnes x <= x_max"""
    if n <= 0:
        return part
    zone = part.copy()
    zone[:, x_max + 1:] = '.'
    keep = part.copy()
    keep[:, :x_max + 1] = '.'
    z = zone.copy()
    z[:y_mid - n] = zone[n:y_mid]
    for i in range(n):
        z[y_mid - n + i] = zone[y_mid]
    z2 = z.copy()
    z2[:, :x_mid - n] = z[:, n:x_mid]
    for i in range(n):
        z2[:, x_mid - n + i] = z[:, x_mid]
    return np.where(z2 != '.', z2, keep)


# ---------------------------------------------------------------- une patte qui se plie (pixels du dessin)
def leg_disp(L, dH, dK, dT, mid=None):
    """déplacement (dx, dy) de chaque point du squelette : hanche dH, genou dK, pointe dT, interpolés le long de la
    patte ; mid (optionnel) = déplacement en plus au milieu de la jambe (entre genou et pointe)"""
    n = len(L['sk'])
    k = L['knee']
    out = []
    for i in range(n):
        if i <= k:
            t = i / k if k else 1.0
            d = np.array(dH, float) * (1 - t) + np.array(dK, float) * t
        else:
            t = (i - k) / (n - 1 - k)
            d = np.array(dK, float) * (1 - t) + np.array(dT, float) * t
            if mid is not None:
                d = d + np.array(mid, float) * math.sin(math.pi * t)
        out.append(d)
    return np.array(out)


def draw_leg_pixels(cv, name, disp, ox=0, oy=0):
    """pose la patte « name » du dessin, pliée : chaque pixel de la toile va chercher son pixel source (on recule du
    déplacement du point le plus proche du squelette déformé) ; jamais de trou, jamais de pixel inventé."""
    L = LEGS[name]
    part = PARTS[name]
    sk = np.array(L['sk'], float)
    dsk = sk + disp
    ys, xs = np.nonzero(part != '.')
    m = int(np.abs(disp).max()) + 3
    x0, x1 = xs.min() - m, xs.max() + m + 1
    y0, y1 = ys.min() - m, ys.max() + m + 1
    QY, QX = np.mgrid[y0:y1, x0:x1]
    qx, qy = QX.ravel() + 0.5, QY.ravel() + 0.5
    best = np.full(qx.shape, 1e9)
    sabs = np.zeros(qx.shape)
    for i in range(len(dsk) - 1):
        a, b = dsk[i], dsk[i + 1]
        v = b - a
        t = np.clip(((qx - a[0]) * v[0] + (qy - a[1]) * v[1]) / max(v @ v, 1e-9), 0, 1)
        d = np.hypot(qx - (a[0] + t * v[0]), qy - (a[1] + t * v[1]))
        upd = d < best
        best[upd] = d[upd]
        sabs[upd] = i + t[upd]
    idx = np.arange(len(dsk))
    ddx = np.interp(sabs, idx, disp[:, 0])
    ddy = np.interp(sabs, idx, disp[:, 1])
    sx = np.floor(qx - ddx).astype(int)
    sy = np.floor(qy - ddy).astype(int)
    ok = (sx >= 0) & (sx < GW) & (sy >= 0) & (sy < GH) & (best <= 7)
    sx, sy, qxi, qyi = sx[ok], sy[ok], QX.ravel()[ok], QY.ravel()[ok]
    vals = part[sy, sx]
    good = vals != '.'
    cx, cy = qxi[good] + OX + int(ox), qyi[good] + OY + int(oy)
    inb = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H) & (cy <= GROUND)
    cv[cy[inb], cx[inb]] = vals[good][inb]


# ---------------------------------------------------------------- une patte redessinée (quand elle se lève et frappe)
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)


def chit_tone(k, far=False):
    if far:
        return 'D' if k > 0.7 else 'C' if k > 0.2 else 'B' if k > -0.35 else 'A'
    return 'E' if k > 0.62 else 'D' if k > 0.2 else 'C' if k > -0.25 else 'B' if k > -0.65 else 'A'


def ring_tone(k):
    return 'v' if k > 0.7 else 'u' if k > 0.2 else 't' if k > -0.3 else 's' if k > -0.7 else 'r'


def capsule(cv, P0, P1, r0, r1, tone, t0=0.0, t1=1.0, keep=None):
    """un segment arrondi de P0 à P1 (toile), rayon r0 -> r1, modelé par la lumière : tone(k, t) donne la lettre"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L2 = max(v @ v, 1e-6)
    R = max(r0, r1) + 1
    x0, x1 = int(min(P0[0], P1[0]) - R), int(max(P0[0], P1[0]) + R + 1)
    y0, y1 = int(min(P0[1], P1[1]) - R), int(max(P0[1], P1[1]) + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            p = np.array([x + 0.5, y + 0.5])
            t = float(np.clip((p - P0) @ v / L2, 0, 1))
            if t < t0 - 1e-9 or t > t1 + 1e-9:
                continue
            c = P0 + t * v
            r = r0 + (r1 - r0) * t
            w = p - c
            d = math.hypot(*w)
            if d <= r and (keep is None or keep(x, y)):
                k = (w @ LN) / max(r, 1e-6)
                ch = tone(k, t)
                if ch:
                    cv[y, x] = ch


def draw_leg_new(cv, hip, knee, ankle, tip, far=False, rth=(2.5, 1.9), rsh=(1.8, 1.3, 0.5), spines=True):
    """une patte d'araignée redessinée (toile) : cuisse hanche -> genou (pointu), jambe genou -> cheville, puis
    l'effilé jusqu'à la pointe ; anneaux rouges au genou et à la cheville ; deux petites épines côté extérieur"""
    hip, knee, ankle, tip = (np.array(p, float) for p in (hip, knee, ankle, tip))
    ct = lambda k, t: chit_tone(k, far)
    capsule(cv, hip, knee, rth[0], rth[1], ct)
    capsule(cv, knee, ankle, rsh[0], rsh[1], ct)
    capsule(cv, ankle, tip, rsh[1], rsh[2], ct)
    # le genou pointu : une petite bosse claire au-dessus de l'articulation
    v1 = (knee - hip) / max(np.linalg.norm(knee - hip), 1e-6)
    v2 = (ankle - knee) / max(np.linalg.norm(ankle - knee), 1e-6)
    bis = v1 - v2
    bis = bis / max(np.linalg.norm(bis), 1e-6)
    capsule(cv, knee, knee + 1.6 * bis, 1.6, 0.9, lambda k, t: chit_tone(k + 0.25, far))
    # anneaux rouges (bandes en travers de la patte)
    for (a, b, c0, c1, r) in ((knee, ankle, 0.07, 0.15, rsh[0]), (ankle, tip, 0.0, 0.07, rsh[1])):
        capsule(cv, a, b, r, r, lambda k, t: ring_tone(k - (0.35 if far else 0)), t0=c0, t1=c1)
    if spines:
        n = np.array([v2[1], -v2[0]])
        if n @ LN < 0:
            n = -n
        for s in (0.35, 0.62):
            p = knee + s * (ankle - knee) + n * (rsh[0] + 0.4)
            for q in (p, p + n * 0.9 + v2 * 0.9):
                x, y = int(q[0]), int(q[1])
                if 0 <= x < W and 0 <= y < H:
                    cv[y, x] = 'B' if far else 'C'


def layered(cv, draw, rim):
    """dessine un morceau sur un calque à part, puis le pose sur la toile ; là où il passe devant ce qui est déjà
    peint, son bord prend un ton plus sombre de sa matière (une séparation douce, pas un trait noir)"""
    lay = empty()
    out = draw(lay)
    m = lay != '.'
    under = cv != '.'
    edge = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(m, dy, 0), dx, 1)
        edge |= m & ~nb & np.roll(np.roll(under, dy, 0), dx, 1)
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys, xs):
        lay[y, x] = rim(lay[y, x])
    cv[m] = lay[m]
    return out


def rim_chit(ch):
    return {'E': 'C', 'D': 'B', 'C': 'A', 'B': 'A', 'F': 'D', 'v': 't', 'u': 's', 't': 'r', 's': 'r'}.get(ch, ch)


def rim_skin(ch):
    return {'5': '3', '4': '2', '3': '2', '2': '1'}.get(ch, rim_chit(ch))


def rim_steel(ch):
    return {'q': 'o', 'p': 'n', 'o': 'n', 'n': 'm', 'i': 'h', 'h': 'g'}.get(ch, ch)


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((H, W, 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None):
    """le héros (avec son contour) entre les effets de fond et ceux de devant ; renvoie une image RGBA"""
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


class Ctx:
    """ce qu'une image a calculé (positions sur la toile) : utile aux effets"""
    pass


# ---------------------------------------------------------------- la femme (buste qui respire et se penche)
def woman_shift(s, b, lean):
    """décalage (dx, dy) de la rangée s du calque « femme » : au-dessus du souffle elle monte de b ; le haut du corps
    se penche de lean pixels (de la taille, rangée 84, jusqu'aux épaules, rangée 60)"""
    dy = -b if s < BREATH_Y else 0
    if s <= 60:
        dx = lean
    elif s >= 84:
        dx = 0
    else:
        dx = int(math.floor(lean * (84 - s) / 24 + 0.5)) if lean >= 0 else -int(math.floor(-lean * (84 - s) / 24 + 0.5))
    return dx, dy


def draw_woman_rows(cv, part, ox, oy, b, lean, swap=None):
    """pose un morceau de la femme rangée par rangée (le souffle double la rangée BREATH_Y - 1)"""
    for s in range(GH):
        row = part[s]
        xs = np.nonzero(row != '.')[0]
        if not len(xs):
            continue
        dx, dy = woman_shift(s, b, lean)
        reps = [dy]
        if b and s == BREATH_Y - 1:
            reps.append(0)                  # la rangée sous la poitrine est doublée : pas de trou
        for ddy in reps:
            cy = s + ddy + oy + OY
            if not 0 <= cy < H:
                continue
            cx = xs + dx + ox + OX
            ok = (cx >= 0) & (cx < W)
            vals = row[xs[ok]]
            if swap:
                vals = np.array([swap.get(v, v) for v in vals])
            cv[cy, cx[ok]] = vals


# ---------------------------------------------------------------- une image montée
LEG_ORDER_BACK = ['L1', 'R4', 'R2', 'L3', 'L4']     # derrière le corps
LEG_ORDER_FRONT = ['L2', 'R3', 'R1']                # devant le corps
ABD = dict(x_max=68, y_mid=79, x_mid=40)            # l'abdomen (pour la palpitation)


def rig_frame(f):
    """f : réglages de l'image. Renvoie (héros, effets derrière, effets devant, ctx)."""
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    sdx, sdy = f.get('sp', (0, 0))                  # le corps de l'araignée (abdomen + céphalothorax)
    kf = f.get('kf', 0.5)                           # part du mouvement du corps que suivent les genoux
    legs = f.get('legs', {})
    ctx.sp = (sdx, sdy)
    ctx.tips = {}

    def leg(name):
        spec = legs.get(name, {})
        if 'new' in spec:                           # patte redessinée : (hanche, genou, cheville, pointe), grille
            # la hanche et le genou suivent le corps, la cheville à moitié, la pointe est où on l'a mise
            follow = (1.0, 1.0, 0.5, 0.0)
            pts = [np.array(g2c(*p), float) + fo * np.array([sdx, sdy], float) for p, fo in zip(spec['new'], follow)]
            ctx.tips[name] = pts[3]
            far = name in ('L1', 'R4', 'R2', 'L3', 'L4')
            layered(cv, lambda lay: draw_leg_new(lay, *pts, far=far, spines=name in ('R3', 'R1', 'L2')), rim_chit)
            return
        dH = np.array([sdx, sdy], float)
        dK = dH * kf + np.array(spec.get('k', (0, 0)), float)
        dT = np.array(spec.get('t', (0, 0)), float)
        draw_leg_pixels(cv, name, leg_disp(LEGS[name], dH, dK, dT, spec.get('mid')))

    for name in LEG_ORDER_BACK:
        leg(name)
    corps = swell(PARTS['corps'], n=f.get('abd', 0), **ABD) if f.get('abd') else PARTS['corps']
    blit(cv, corps, sdx, sdy)
    for name in LEG_ORDER_FRONT:
        if not legs.get(name, {}).get('over'):
            leg(name)
    for fx in f.get('fx_mid', []):                  # effets entre l'araignée et la femme
        fx(cv, back, front, ctx)

    # la femme
    b, lean = f.get('b', 0), f.get('lean', 0)
    wx, wy = f.get('w', (0, 0))
    ox, oy = sdx + wx, sdy + wy
    swap = BLINK if f.get('blink') else None
    draw_woman_rows(cv, WP['buste'], ox, oy, b, lean)
    sdxL, sdyL = woman_shift(60, b, lean)
    arm_l = f.get('armL', (0, 0, 0))                # bras lointain : (glissé x, glissé y, colonnes d'allongement)
    blit(cv, stretch_cols(WP['brasL'], 99, arm_l[2]), ox + sdxL + arm_l[0], oy + sdyL + arm_l[1])
    ctx.tipL = np.array(g2c(125, 54), float) + (ox + sdxL + arm_l[0] + arm_l[2], oy + sdyL + arm_l[1])
    for name in LEG_ORDER_FRONT:                    # une patte avant levée passe devant le bras lointain
        if legs.get(name, {}).get('over'):
            leg(name)
    hdx, hdy = woman_shift(40, b, lean)
    head = f.get('head', (0, 0))
    blit(cv, WP['tete'], ox + hdx, oy + hdy, swap)
    if head != (0, 0):
        blit(cv, WP['tete'], ox + hdx + head[0], oy + hdy + head[1], swap)
    ctx.head = (ox + hdx + head[0], oy + hdy + head[1])
    sdxP, sdyP = woman_shift(56, b, lean)
    ctx.sh = np.array(g2c(*SH_NEAR), float) + (ox + sdxP, oy + sdyP)
    arm = f.get('armP', ('orig', 0, 0))
    if arm[0] == 'orig':
        if arm[1] or arm[2]:
            # bras levé / ramené : le bras du dessin glisse, le haut du bras est redessiné dessous (pas de trou)
            E = np.array(g2c(*ELBOW0), float) + (ox + sdxP + arm[1], oy + sdyP + arm[2])
            layered(cv, lambda lay: upper_arm(lay, ctx.sh, E), rim_skin)
        blit(cv, WP['brasP'], ox + sdxP + arm[1], oy + sdyP + arm[2])
        ctx.tipP = np.array(g2c(53, 20), float) + (ox + sdxP + arm[1], oy + sdyP + arm[2])
    else:
        draw_near_arm(cv, back, front, ctx, *arm[1:])
    blit(cv, WP['epaule'], ox + sdxP, oy + sdyP)
    for fx in f.get('fx_list', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- le bras proche, redessiné pour frapper
SH_NEAR = (60.5, 57.5)        # l'épaule proche (sous l'épaulière), grille
ELBOW0 = (49.0, 58.0)         # le coude du dessin
ARM = (12.0, 12.5)            # bras, avant-bras (du coude au poignet)


def skin_tone(k, t=0):
    return '5' if k > 0.72 else '4' if k > 0.18 else '3' if k > -0.3 else '2' if k > -0.72 else '1'


def upper_arm(cv, S, E):
    capsule(cv, S, E, 3.2, 2.9, skin_tone)


def ik(S, T, L1, L2, bend):
    S, T = np.array(S, float), np.array(T, float)
    v = T - S
    d = max(np.linalg.norm(v), 1e-6)
    u = v / d
    if d > L1 + L2:
        k = d / (L1 + L2)
        L1, L2 = L1 * k, L2 * k
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(L1 * L1 - a * a, 0))
    perp = np.array([-u[1], u[0]])
    return S + a * u + bend * hh * perp


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), -math.sin(a)])


def bracer_tone(k, t):
    """l'avant-bras pris dans le brassard de chitine, cerclé de rouge aux deux bouts (comme le dessin)"""
    if t < 0.12 or 0.86 < t < 0.97:
        return ring_tone(k)
    return chit_tone(k)


# Le poing qui tient la dague pointée en avant (dessiné à la main, d'après la main lointaine du dessin : dos de la
# main, doigts repliés en paliers, pouce dessus) ; 'o' = le point de prise (centre de la poignée) à placer.
FIST_FWD = [
    '..3445..',
    '.345554.',
    '23444553',
    '23434344',
    '12434343',
    '12323232',
    '.121212.',
]
FIST_GRIP = (7.5, 3.5)          # où passe l'axe de la dague (colonne, rangée) dans la grille du poing


def draw_dagger(cv, G, ang, length=15.0, smear=0):
    """la dague retracée : garde d'or en travers à G (toile), lame courbe vers 'ang' (degrés) ; dos sombre, fil
    clair côté lumière, éclat près de la pointe. smear > 0 : la lame s'allonge (vitesse)."""
    u = unit(ang)
    n = np.array([u[1], -u[0]])               # normale : le côté où la lame se bombe (vers le haut quand elle pointe à droite)
    if n @ LN < 0:
        n = -n
    L = length + smear
    best = {}
    for i in range(int(L * 3) + 1):
        t = i / (L * 3) * L
        s = t / L
        # lame courbe : le centre se décale vers n (dos bombé), largeur qui s'effile en pointe
        off = 1.2 * math.sin(math.pi * s * 0.9)
        half = 1.9 * (1 - s) ** 0.75 + 0.35
        c = np.array(G, float) + (t + 1.0) * u + off * n
        for y in range(int(c[1] - 3), int(c[1] + 4)):
            for x in range(int(c[0] - 3), int(c[0] + 4)):
                w = np.array([x + 0.5, y + 0.5]) - c
                along = w @ u
                if abs(along) > 0.6:
                    continue
                d = w @ n
                if abs(d) <= half:
                    kk = d / half
                    if (x, y) not in best or abs(along) < best[(x, y)][1]:
                        best[(x, y)] = (kk, abs(along), s)
    for (x, y), (kk, _, s) in best.items():
        ch = 'p' if kk > 0.45 else 'o' if kk > -0.1 else 'n' if kk > -0.6 else 'm'
        if 0.62 < s < 0.8 and kk > 0.2:
            ch = 'q'
        if 0 <= x < W and 0 <= y < H:
            cv[y, x] = ch
    # la garde d'or, en travers
    capsule(cv, np.array(G, float) - 2.6 * n, np.array(G, float) + 2.6 * n, 1.0, 1.0,
            lambda k, t: 'i' if k > 0.5 else 'h' if k > -0.3 else 'g')
    return np.array(G, float) + (L + 1.0) * u


def sprite_at(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                X, Y = int(x) + i, int(y) + j
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


def draw_near_arm(cv, back, front, ctx, wrist, ang=-8.0, bend=1, smear=0, fx=None):
    """bras proche redessiné : épaule -> coude -> poignet (grille, relatif au buste), poing en avant, dague vers ang"""
    o = ctx.sh - np.array(g2c(*SH_NEAR), float)
    Wr = np.array(g2c(*wrist), float) + o
    S = ctx.sh
    E = ik(S, Wr, ARM[0], ARM[1], bend)
    ctx.E, ctx.Wr = E, Wr
    layered(cv, lambda lay: capsule(lay, S, E, 3.2, 2.9, skin_tone), rim_skin)
    layered(cv, lambda lay: capsule(lay, E, Wr, 2.7, 2.4, bracer_tone), rim_chit)
    u = unit(ang)
    # le poing : posé au bout de l'avant-bras ; la garde de la dague juste devant les doigts
    fx0 = Wr + 1.5 * u - np.array([2.5, 3.5])
    G = fx0 + np.array(FIST_GRIP) + np.array([0.5, 0])
    if fx is not None:
        fx(cv, back, front, ctx, G, u)
    lay = empty()
    ctx.tipP = draw_dagger(lay, G, ang, smear=smear)
    sprite_at(lay, FIST_FWD, round(fx0[0]), round(fx0[1]))
    m = lay != '.'
    cv[m] = lay[m]
    ctx.G = G


# ---------------------------------------------------------------- les effets : formes courbes, sans contour
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def puff(cv, c, r, tones='VWX', hollow=0.0):
    """une bouffée de poussière, ronde, éclairée en haut à droite ; hollow > 0 : elle se défait (trou au milieu)"""
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                ch = tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))]
                put(cv, x, y, ch)


def cloud(cv, c, r, tones='VWXY', hollow=0.0, seed=0):
    """un nuage de poussière en chou-fleur : une grosse bouffée et des petites autour (pas une bille ronde).
    hollow (0..1) : le nuage se défait — les bouffées s'écartent, montent un peu, rapetissent et pâlissent."""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(4):
        a = math.radians(150 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.55, 0.8)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.7, r * rng.uniform(0.5, 0.7)))
    if hollow:
        out = []
        for (dx, dy, rr) in lobes[1:]:
            out.append((dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.45 * hollow)))
        out.append((0, -hollow * r * 0.4, r * (1 - 0.6 * hollow)))
        lobes = out
        tones = tones[:1] * 2 + tones[1:2] if hollow > 0.5 else tones
    for (dx, dy, rr) in lobes:
        puff(cv, (cx + dx, min(cy + dy, GROUND - rr * 0.6)), rr, tones)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones, keep=None):
    """peint un ruban le long de points, avec une épaisseur par point (coeur clair -> bord sombre)"""
    best = {}
    for (px, py), wv in zip(pts, widths):
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.2 else 0.85
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))], keep)


def thread(cv, pts, tones='HJ', start=0.0, end=1.0):
    """un fil de soie : un trait d'un pixel clair, doublé dessous d'un pixel d'ombre lavande (lisible sur tous les
    fonds) ; seulement la portion start..end de la courbe"""
    n = len(pts)
    seen = set()
    for i in range(int(start * (n - 1)), int(end * (n - 1)) + 1):
        x, y = int(math.floor(pts[i][0])), int(math.floor(pts[i][1]))
        if (x, y) in seen:
            continue
        seen.add((x, y))
        put(cv, x, y + 1, tones[1], keep='.' + tones[1])
    for (x, y) in seen:
        put(cv, x, y, tones[0])


def pop(cv, c, r, facing=0.0, tones='ljST'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for i, da in enumerate((-70, -25, 20, 65, 150, 210)):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                d = math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy)
                if d <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def arc_trail(cv, c, R, a_from, a_to, w, tones, inner=0.0):
    """traînée pleine en croissant (ce qui tourne autour de c) : de l'angle a_from (le bout de la traînée, fin) à
    a_to (là où est la lame, épais) ; bord extérieur sur le cercle R ; les tons suivent la courbe"""
    cx, cy = c
    m = len(tones)
    span = (a_to - a_from)
    for y in range(int(cy - R - 2), int(cy + R + 3)):
        for x in range(int(cx - R - 2), int(cx + R + 3)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > R + 0.5 or r < inner:
                continue
            ang = math.degrees(math.atan2(-dy, dx))
            s = ((ang - a_from) / span) if span else 0
            for k360 in (-360, 360):
                if not 0 <= s <= 1:
                    s2 = ((ang + k360 - a_from) / span)
                    if 0 <= s2 <= 1:
                        s = s2
            if not 0 <= s <= 1:
                continue
            ww = w * s ** 0.9 + 0.6
            if r < R - ww:
                continue
            k = min(1.0, max(0.0, (R - r) / max(ww, 1e-6)))
            i = int((0.6 * (1 - s) + 0.4 * k) * m)
            put(cv, x, y, tones[min(m - 1, i)])


def sprite(cv, rows, x, y, flipx=False):
    for j, r in enumerate(rows):
        if flipx:
            r = r[::-1]
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


# éclats de pierre (dessinés à la main) et cailloux
CHUNKS = [
    ['.KN', 'KNO', 'NOP'],
    ['KN.', 'NOO', '.OP'],
    ['.K', 'NO'],
    ['KNN.', 'NOOP', '.OP.'],
]
SHARDS = [
    ['.S', 'TU'],
    ['RS.', '.TU'],
    ['S', 'T', 'U'],
]


def chunk(cv, x, y, k=0, flip=False):
    sprite(cv, CHUNKS[k % len(CHUNKS)], int(x), int(y), flip)


def shard(cv, x, y, k=0, flip=False):
    sprite(cv, SHARDS[k % len(SHARDS)], int(x), int(y), flip)


# ---------------------------------------------------------------- 1) la pose (respiration)
# 10 images. La femme respire (le buste monte d'un pixel, la tête suit avec une image de retard) ; l'abdomen palpite
# en double battement (gonfle, retombe, regonfle) ; les huit pattes ne bougent jamais ensemble : un genou se crispe
# (monte d'un pixel, une image ou deux), la patte avant proche tapote le sol (pointe levée, reposée), le corps se tasse
# d'un pixel à l'expiration (les genoux remontent un peu par rapport au corps). Un clignement.
POSE = [
    dict(ms=150),
    dict(b=1, head=(0, 1), abd=1, legs={'L1': dict(k=(0, -1))}, ms=110),
    dict(b=1, legs={'L1': dict(k=(0, -1)), 'R4': dict(k=(0, -1))}, ms=120),
    dict(b=1, abd=1, legs={'R4': dict(k=(0, -1)), 'R3': dict(k=(0, -1), t=(1, -2))}, ms=80),
    dict(b=1, legs={'R3': dict(k=(1, -2), t=(2, -3))}, ms=70),
    dict(head=(0, -1), legs={'R2': dict(k=(-1, 0))}, ms=150),
    dict(sp=(0, 1), head=(0, -1), abd=1, legs={'R2': dict(k=(-1, 0)), 'L2': dict(k=(0, -1))}, ms=120),
    dict(sp=(0, 1), blink=1, legs={'L2': dict(k=(0, -1)), 'L4': dict(mid=(1, 0))}, ms=100),
    dict(sp=(0, 1), legs={'R1': dict(k=(1, -1))}, ms=130),
    dict(head=(0, 1), legs={'L3': dict(mid=(-1, 0))}, ms=120),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Piqûre »
# Coup d'assassin vicieux : elle se ramasse en arrière (corps reculé, dague levée plus haut, les deux pattes avant
# dressées, frémissantes), tenue nerveuse ; puis tout part d'un coup : le corps bondit en avant, la dague pique droit
# dans l'ennemi pendant que les deux pattes avant se plantent devant elle comme deux pieux (trois pointes qui
# convergent) ; impact tenu, éclat grenat ; retour saccadé, patte après patte.
def fx_thrust(level):
    """le souffle de l'estoc : un fuseau d'acier pâle le long de la lame lointaine, et un croissant d'air devant la
    pointe (formes courbes, effilées)"""
    def f(cv, back, front, ctx):
        tip = ctx.tipL
        u = np.array([0.94, -0.33])
        u = u / np.linalg.norm(u)
        nrm = np.array([u[1], -u[0]])
        if level >= 1:
            p0 = tip - 34 * u
            pts = bezier(p0, p0 + 12 * u + 2.5 * nrm, tip - 6 * u + 1.5 * nrm, tip + 6 * u, 40)
            wd = [5.0 * math.sin(math.pi * i / 40) ** 0.8 + 0.3 for i in range(41)]
            stroke(back, pts, wd, 'pon')
            pts = bezier(p0 + 6 * u - 4 * nrm, p0 + 16 * u - 6 * nrm, tip - 10 * u - 5 * nrm, tip - 2 * u - 3 * nrm, 30)
            stroke(back, pts, [2.2 * math.sin(math.pi * i / 30) + 0.2 for i in range(31)], 'on')
        if level >= 2:
            c = tip + 1 * u
            pts = [(c[0] + 7 * math.cos(math.radians(a)) * 0.7, c[1] - 7 * math.sin(math.radians(a))) for a in np.arange(-70, 71, 2)]
            stroke(front, pts, [2.4 * math.sin(math.pi * i / (len(pts) - 1)) + 0.4 for i in range(len(pts))], 'pon')
    return f


def fx_hit(level, legs_dust=True):
    def f(cv, back, front, ctx):
        tip = ctx.tipL + np.array([1, 0])
        if level == 0:
            pop(front, tip, 4.6, facing=10, tones='ljSTU')
            for (dx, dy, k) in ((8, -7, 0), (10, 3, 1), (5, 7, 2)):
                shard(front, tip[0] + dx, tip[1] + dy, k)
        elif level == 1:
            pop(front, tip + np.array([3, -1]), 3.2, facing=20, tones='STU')
            for (dx, dy, k) in ((13, -11, 0), (15, 5, 1), (8, 11, 2)):
                shard(front, tip[0] + dx, tip[1] + dy, k)
        else:
            pop(front, tip, 3.4, facing=0, tones='ljST')
            for (dx, dy, k) in ((7, -5, 1), (6, 5, 0)):
                shard(front, tip[0] + dx, tip[1] + dy, k)
        if legs_dust:
            for name in ('R3', 'R4'):                # la poussière sous les pointes plantées
                if name in ctx.tips:
                    t = ctx.tips[name]
                    if t[1] >= GROUND - 2:
                        cloud(back, (t[0] + 1, GROUND - 2), 3.4 if level == 0 else 2.6, 'VWXY',
                              hollow=0.0 if level == 0 else 0.5, seed=3 if name == 'R3' else 5)
    return f


R3_REST = [(90, 89), (104, 73.5), (114.5, 96.5), (116.5, 116)]
R4_REST = [(99, 77), (113.5, 66.5), (121, 93), (123.5, 116)]
R3_UP = [(90, 89), (106, 64), (118, 70), (122, 84)]
R4_UP = [(99, 77), (114, 56), (126, 60), (131, 72)]
R3_HIT = [(90, 89), (113, 69), (130, 91), (136, 116)]
R4_HIT = [(99, 77), (121, 63), (137, 85), (144, 115)]
ATTAQUE = [
    # 0 : tension (une patte avant se crispe)
    dict(legs={'R3': dict(k=(0, -1)), 'L1': dict(k=(0, -1))}, ms=90),
    # 1 : elle se ramasse en arrière : dague lointaine ramenée, dague proche levée, pattes avant dressées
    dict(sp=(-3, 1), lean=-2, head=(0, 1), abd=1, armP=('orig', -1, -2), armL=(-2, 1, -3),
         legs={'R3': dict(new=R3_UP), 'R4': dict(new=R4_UP), 'L1': dict(k=(-1, -1)), 'L2': dict(k=(0, -1))}, ms=170),
    # 2 : frémissement (tout tremble d'un pixel, l'abdomen se serre)
    dict(sp=(-3, 1), lean=-3, armP=('orig', -1, -3), armL=(-3, 1, -3),
         legs={'R3': dict(new=[(90, 89), (105, 63), (118, 68), (123, 82)]),
               'R4': dict(new=[(99, 77), (115, 55), (127, 59), (131, 71)]),
               'L1': dict(k=(-1, -1)), 'L2': dict(k=(0, -1))}, ms=100),
    # 3 : départ (image de vitesse) : tout le corps jaillit, la dague fend l'air, les pattes fusent
    dict(sp=(4, 0), lean=3, armP=('orig', 1, 0), armL=(2, -1, 7),
         legs={'R3': dict(new=[(90, 89), (112, 66), (128, 84), (134, 104)]),
               'R4': dict(new=[(99, 77), (120, 60), (134, 76), (141, 94)])}, fx_list=[fx_thrust(2)], ms=50),
    # 4 : impact (tenu) : dague plantée, pattes plantées devant
    dict(sp=(6, 1), lean=4, head=(1, 0), armP=('orig', 1, 1), armL=(3, 0, 5),
         legs={'R3': dict(new=R3_HIT), 'R4': dict(new=R4_HIT), 'L1': dict(k=(1, 0)), 'L2': dict(k=(1, 0))},
         fx_list=[fx_hit(0)], ms=170),
    # 5 : elle retire la dague d'un coup sec (l'éclat se défait)
    dict(sp=(4, 1), lean=2, head=(1, 0), armP=('orig', 0, 0), armL=(0, 0, 0),
         legs={'R3': dict(new=R3_HIT), 'R4': dict(new=R4_HIT)}, fx_list=[fx_hit(1)], ms=70),
    # 6 : et repique aussitôt (deuxième piqûre, plus courte)
    dict(sp=(6, 1), lean=4, head=(1, 1), armP=('orig', 1, 1), armL=(3, 1, 5),
         legs={'R3': dict(new=R3_HIT), 'R4': dict(new=R4_HIT)}, fx_list=[fx_thrust(1), fx_hit(2, False)], ms=120),
    # 7 : elle se replie (les pattes se relèvent)
    dict(sp=(1, 0), lean=1, armP=('orig', 0, 0), armL=(0, 0, 0),
         legs={'R3': dict(new=[(90, 89), (108, 67), (122, 82), (126, 98)]),
               'R4': dict(new=[(99, 77), (117, 61), (129, 77), (134, 93)])}, ms=100),
    # 8 : les pattes se reposent l'une après l'autre
    dict(sp=(0, 0),
         legs={'R3': dict(k=(0, -1), t=(1, -2)), 'R4': dict(new=[(99, 77), (114, 64), (122, 88), (124, 108)])}, ms=90),
    # 9 : en garde
    dict(legs={'R4': dict(k=(0, -1)), 'L2': dict(k=(0, -1))}, ms=130),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Nid de pierre »
# Elle se tasse (le corps s'enfonce entre les genoux, l'abdomen se gonfle), se cabre (pattes avant dressées) et
# lance de ses filières, à l'arrière de l'abdomen, deux longs fils de soie qui passent au-dessus d'elle en grandes
# courbes et vont s'enrouler autour de l'ennemi : un cocon. Elle tire sur les fils, puis plante ses deux pattes avant
# dans le sol : une fissure court jusqu'au cocon et QUATRE grandes pattes de pierre aux pointes de cristal grenat
# jaillissent de la terre autour de lui et se referment comme une araignée sur sa proie (arrêt sur image), puis
# s'effritent en éclats et en nuages de poussière. Elle se remet en garde, patte après patte.
FOE_G = (FOE[0] - OX, GROUND - OY)                  # le pied de l'ennemi, en coordonnées de la grille
COCOON = (FOE[0], GROUND - 19)                      # centre du cocon (toile)


def spinneret(ctx):
    """les filières : l'arrière de l'abdomen (toile)"""
    return np.array(g2c(20.5, 81), float) + np.array(ctx.sp, float)


def silk_paths(ctx, taut=0.0):
    """les deux fils : de grandes courbes au-dessus d'elle, des filières jusqu'au cocon. taut (0..1) : tendus"""
    p0 = spinneret(ctx)
    out = []
    for (c1, c2, end) in (((-30, -54), (104, -50), (-2, -16)), ((-18, -34), (128, -34), (3, -8))):
        p3 = np.array(COCOON, float) + end
        a1 = p0 + np.array(c1, float)
        a2 = np.array(g2c(*c2), float)
        # tendu : les points de contrôle se rapprochent de la droite qui va des filières au cocon
        l1, l2 = p0 + (p3 - p0) * 0.33, p0 + (p3 - p0) * 0.66 + np.array([0, -18])
        a1 = a1 * (1 - taut) + l1 * taut
        a2 = a2 * (1 - taut) + l2 * taut
        out.append(bezier(p0, a1, a2, p3, 900))
    return out


def fx_silk(progress, taut=0.0, cut=None):
    """les fils de soie : progress (0..1) = jusqu'où ils sont arrivés ; une petite boule de soie en tête.
    cut = (a, b) : les fils ont cassé, il n'en reste que les bouts 0..a et b..1 (qui se recourbent)"""
    def f(cv, back, front, ctx):
        for i, pts in enumerate(silk_paths(ctx, taut)):
            pr = min(1.0, progress * (1.0 if i == 0 else 1.15))
            if cut:
                thread(back, pts, 'HJ', 0.0, cut[0])
                thread(back, pts, 'HJ', cut[1], 1.0)
                continue
            thread(back, pts, 'HJ', 0.0, pr)
            if pr < 1.0:
                hx, hy = pts[int(pr * (len(pts) - 1))]
                puff(back, (hx, hy), 1.8, 'GHI')
    return f


def cocoon(cv, c, rx, ry, level=1.0, flash=False):
    """le cocon de soie : un ovale posé au sol, éclairé en haut à droite, avec trois fils qui l'entourent en biais
    (courbes, jamais parallèles) ; level (0..1) : il se forme (il monte du sol)"""
    cx, cy = c
    top = cy + ry - 2 * ry * level
    tones = 'lGG' if flash else 'GHIJ'
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0 and y + 0.5 >= top:
                w = np.array([dx, dy * 0.8])
                k = (w @ LN)
                i = 0 if k > 0.45 else 1 if k > -0.1 else 2 if k > -0.55 else 3
                put(cv, x, y, tones[min(i, len(tones) - 1)])
    if flash:
        return
    # trois fils enroulés en biais (des bouts d'ellipses inclinées), sur la face visible
    for (tilt, sc, a0, a1) in ((22, 0.55, -80, 95), (-14, 0.2, -95, 80), (8, -0.35, -70, 100)):
        pts = []
        for a in np.arange(a0, a1, 0.7):
            ex, ey = rx * 1.02 * math.cos(math.radians(a)), ry * 0.22 * math.sin(math.radians(a))
            t = math.radians(tilt)
            px, py = ex * math.cos(t) - ey * math.sin(t), ex * math.sin(t) + ey * math.cos(t)
            Y = cy + sc * ry + py
            X = cx + px
            if Y >= top and ((X - cx) / (rx - 0.8)) ** 2 + ((Y - cy) / (ry - 0.8)) ** 2 <= 1.0:
                pts.append((X, Y))
        if pts:
            thread(cv, pts, 'IJ')


def fx_wrap(level):
    """les fils qui s'enroulent autour de l'ennemi, puis le cocon"""
    def f(cv, back, front, ctx):
        cx, cy = COCOON
        if level < 1:
            for (rx, ry, tilt, a0, a1) in ((13, 6, 18, -40, 250), (11, 5, -16, 120, 400), (12, 5, 6, 200, 470)):
                pts = []
                for a in np.arange(a0, a1, 0.7):
                    ex, ey = rx * math.cos(math.radians(a)), ry * math.sin(math.radians(a))
                    t = math.radians(tilt)
                    pts.append((cx + ex * math.cos(t) - ey * math.sin(t), cy - 4 + (a - a0) / 40 + ex * math.sin(t) + ey * math.cos(t)))
                thread(front, pts, 'HJ')
            cocoon(front, (cx, cy + 4), 7, 13, level=0.5)
        else:
            cocoon(front, (cx, cy), 9, 18, level=1.0)
    return f


def crack(cv, x0, x1, seed=1):
    """une fissure qui court au sol (courbe, ses lèvres claires au-dessus) de x0 à x1 (toile)"""
    rng = np.random.RandomState(seed)
    y = GROUND
    x = x0
    pts = []
    while x <= x1:
        pts.append((x, y))
        x += 1
        if rng.rand() < 0.22:
            y = GROUND - 1 if y == GROUND else GROUND
    for (x, y) in pts:
        put(cv, x, y, 'Q')
        if y == GROUND - 1:
            put(cv, x, y + 1, 'P')
        put(cv, x, y - 1, 'O' if rng.rand() < 0.7 else 'N', keep='.')
    # deux petites branches recourbées
    for bx in (x0 + (x1 - x0) * 0.35, x0 + (x1 - x0) * 0.7):
        for i in range(4):
            put(cv, bx + i, GROUND - 1 - (i // 2), 'P', keep='.O')


def curve_limb(cv, P0, P1, bulge, r0, r1, tone, keep=None):
    """un segment de membre COURBE (arc de P0 à P1, bombé de 'bulge' pixels sur le côté), rayon r0 -> r1, modelé par
    la lumière ; tone(k, s) donne la lettre (k = orientation vers la lumière, s = 0..1 le long du segment)"""
    P0, P1 = np.array(P0, float), np.array(P1, float)
    v = P1 - P0
    L = max(np.linalg.norm(v), 1e-6)
    nrm = np.array([-v[1], v[0]]) / L
    C = (P0 + P1) / 2 + bulge * nrm * 2
    n = int(L * 3) + 2
    ts = np.linspace(0, 1, n)
    pts = ((1 - ts) ** 2)[:, None] * P0 + (2 * (1 - ts) * ts)[:, None] * C + (ts ** 2)[:, None] * P1
    rad = r0(ts) if callable(r0) else r0 + (r1 - r0) * ts
    R = float(rad.max()) + 1
    x0, x1 = int(pts[:, 0].min() - R), int(pts[:, 0].max() + R + 1)
    y0, y1 = int(pts[:, 1].min() - R), int(pts[:, 1].max() + R + 1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            d = np.hypot(pts[:, 0] - x - 0.5, pts[:, 1] - y - 0.5) - rad
            i = int(np.argmin(d))
            if d[i] <= 0 and (keep is None or keep(x, y)):
                w = np.array([x + 0.5, y + 0.5]) - pts[i]
                k = (w @ LN) / max(rad[i], 1e-6)
                ch = tone(k, ts[i])
                if ch:
                    cv[y, x] = ch


LIGHTER = {'K': 'l', 'N': 'K', 'O': 'N', 'P': 'O', 'R': 'l', 'S': 'R', 'T': 'S', 'U': 'T'}


def claw_leg(cv, base, knee, tip, w0=8.0, flash=False, cut=1.0, bulge=(2.0, 2.5), seed=0):
    """une grande patte de pierre sortie du sol, comme une patte d'araignée : cuisse épaisse et courbe qui monte en
    s'écartant, genou pointu cerclé de cristal, jambe en crochet qui redescend en pointe de cristal grenat sur la
    proie. cut (0..1) : brisée, il n'en reste que cette part (depuis le sol)"""
    base, knee, tip = (np.array(p, float) for p in (base, knee, tip))
    below = lambda x, y: y <= GROUND

    def stone(k, s, x=None, y=None):
        if s > cut:
            return None
        if s > 0.76:                                  # la griffe de cristal
            ch = 'R' if k > 0.62 else 'S' if k > 0.15 else 'T' if k > -0.45 else 'U'
        elif 0.47 < s < 0.53:                         # l'anneau de cristal au genou
            ch = 'S' if k > 0.35 else 'T' if k > -0.3 else 'U'
        else:
            ch = 'K' if k > 0.55 else 'N' if k > 0.0 else 'O' if k > -0.55 else 'P'
        return LIGHTER.get(ch, ch) if flash else ch
    sg = 1 if knee[0] < base[0] else -1               # de quel côté elle se bombe (vers l'extérieur)
    curve_limb(cv, base, knee, sg * bulge[0], w0 / 2, w0 / 2 * 0.6, lambda k, t: stone(k, 0.5 * t), keep=below)
    # la jambe : pierre qui s'affine, puis la griffe de cristal qui regonfle un peu avant la pointe
    def rad(t):
        r = w0 / 2 * 0.68
        return np.where(t < 0.44, r - (r - 1.9) * t / 0.44,
                        np.where(t < 0.56, 1.9 + 0.7 * (t - 0.44) / 0.12, 2.6 * (1 - (t - 0.56) / 0.44) ** 0.8 + 0.4))
    curve_limb(cv, knee, tip, sg * bulge[1], rad, None, lambda k, t: stone(k, 0.5 + 0.5 * t), keep=below)
    v1 = (knee - base) / np.linalg.norm(knee - base)
    v2 = (tip - knee) / np.linalg.norm(tip - knee)
    bis = (v1 - v2) / max(np.linalg.norm(v1 - v2), 1e-6)
    if cut >= 0.5:
        capsule(cv, knee, knee + 2.8 * bis, 2.0, 0.6, lambda k, t: stone(k + 0.25, 0.45), keep=below)


# les quatre pattes de pierre autour de l'ennemi : (base x, genou x, genou hauteur, pointe x, pointe hauteur,
# épaisseur, devant ?) — x par rapport à l'ennemi, hauteurs au-dessus du sol
CLAWS = [(-9, -31, 60, -4, 29, 9.0, False), (9, 30, 56, 4, 27, 9.0, False),
         (-5, -23, 47, -1, 19, 8.0, True), (6, 22, 50, 2, 21, 8.0, True)]


def fx_claws(progress, close=0.0, flash=False, crumble=0.0):
    def f(cv, back, front, ctx):
        for fr in (False, True):
            if fr and crumble < 0.3:
                cocoon(front, (COCOON[0], COCOON[1] + int(2 * close)), 9 - int(2 * close), 18 - int(3 * close),
                       flash=flash)
            for (bx, kx, kh, px, ph, w, front_) in CLAWS:
                if front_ != fr:
                    continue
                sink = (1 - progress) * kh
                base = (FOE[0] + bx, GROUND + 3)
                sg = -1 if kx < 0 else 1
                knee = (FOE[0] + kx - sg * 3 * close, GROUND - kh + sink + 2 * close)
                tip = (FOE[0] + px - sg * 3 * close, GROUND - ph + sink + 5 * close)
                claw_leg(front, base, knee, tip, w, flash=flash, cut=1.0 - crumble, seed=int(bx))
    return f


def fx_ground(level):
    """le sol se soulève sous l'ennemi (une bosse de terre fendue)"""
    def f(cv, back, front, ctx):
        cx = FOE[0]
        for (dx, r) in ((-6, 4.5), (5, 4.0), (0, 5.5)):
            for y in range(int(GROUND - r * level), GROUND + 1):
                for x in range(int(cx + dx - r - 1), int(cx + dx + r + 2)):
                    if ((x + 0.5 - cx - dx) / r) ** 2 + ((y + 0.5 - GROUND) / max(r * level, 0.5)) ** 2 <= 1:
                        k = ((x + 0.5 - cx - dx) * LN[0] + (y + 0.5 - GROUND) * LN[1]) / r
                        put(front, x, y, 'K' if k > 0.4 else 'N' if k > -0.2 else 'O')
        put(front, cx - 1, GROUND - int(5 * level), 'Q')
        put(front, cx, GROUND - int(5 * level) + 1, 'Q')
    return f


def fx_debris(t, seed=7, dust=0.0, hollow=0.0):
    """éclats de pierre et de cristal projetés (paraboles) + nuages de poussière au pied des pattes de pierre"""
    def f(cv, back, front, ctx):
        rng = np.random.RandomState(seed)
        cx = FOE[0]
        for i in range(9):
            vx = rng.uniform(-1.6, 1.6) * 14
            vy = rng.uniform(1.4, 2.3) * 18
            x = cx + rng.uniform(-14, 14) + vx * t
            y = GROUND - 10 - vy * t + 30 * t * t
            if y < GROUND - 1:
                if i % 3 == 0:
                    shard(front, x, y, i)
                else:
                    chunk(front, x, y, i, flip=vx < 0)
        if dust:
            for (dx, dy, r, sd) in ((-25, 0, 6.5, 1), (24, 1, 6.0, 2), (-14, -1, 5.0, 3), (15, -1, 4.5, 4)):
                cloud(front, (cx + dx * (1 + 0.35 * hollow), GROUND - 4 + dy * dust - 7 * hollow), r * dust, 'VWXY',
                      hollow=hollow, seed=sd)
    return f


def fx_slam_dust(level):
    def f(cv, back, front, ctx):
        for name in ('R3', 'R4'):
            if name in ctx.tips:
                t = ctx.tips[name]
                cloud(back, (t[0] + 1, GROUND - 2), (4.0 if level == 0 else 3.0), 'VWXY',
                      hollow=0.0 if level == 0 else 0.6, seed=11 if name == 'R3' else 13)
    return f


def fx_crack(frac):
    def f(cv, back, front, ctx):
        x0 = (ctx.tips.get('R3', np.array(g2c(132, 116)))[0]) + 3
        x1 = x0 + (FOE[0] - 6 - x0) * frac
        crack(front, int(x0), int(x1))
    return f


R3_HIGH = [(90, 89), (108, 56), (123, 54), (131, 64)]
R4_HIGH = [(99, 77), (117, 48), (131, 46), (139, 56)]
R3_SLAM = [(90, 89), (112, 70), (128, 94), (132, 116)]
R4_SLAM = [(99, 77), (120, 64), (136, 90), (141, 116)]
SPECIALE = [
    # 0 : tension
    dict(abd=1, legs={'L2': dict(k=(0, -1)), 'R1': dict(k=(0, -1))}, ms=100),
    # 1 : elle se tasse entre ses genoux, l'abdomen se gonfle
    dict(sp=(-2, 3), kf=0.15, lean=-2, head=(0, 1), abd=2, armP=('orig', 0, 1), armL=(-2, 1, -2),
         legs={'R3': dict(k=(0, -2)), 'L1': dict(k=(0, -1))}, ms=170),
    # 2 : elle se cabre, pattes avant dressées ; le premier fil sort des filières
    dict(sp=(-3, -4), kf=0.6, lean=-3, head=(0, -1), abd=1, armP=('orig', -1, -3), armL=(1, -3, 0),
         legs={'R3': dict(new=R3_HIGH), 'R4': dict(new=R4_HIGH), 'L1': dict(k=(0, -2)), 'L2': dict(k=(0, -1))},
         fx_list=[fx_silk(0.06)], ms=190),
    # 3 : les fils jaillissent au-dessus d'elle
    dict(sp=(-2, -3), kf=0.6, lean=-2, head=(0, -1), armP=('orig', -1, -3), armL=(1, -3, 0),
         legs={'R3': dict(new=R3_HIGH), 'R4': dict(new=R4_HIGH), 'L1': dict(k=(0, -2))},
         fx_list=[fx_silk(0.5)], ms=70),
    # 4 : ils arrivent sur l'ennemi et s'enroulent
    dict(sp=(-2, -3), kf=0.6, lean=-2, armP=('orig', -1, -3), armL=(1, -3, 0),
         legs={'R3': dict(new=R3_HIGH), 'R4': dict(new=R4_HIGH), 'L1': dict(k=(0, -2))},
         fx_list=[fx_silk(1.0), fx_wrap(0)], ms=80),
    # 5 : le cocon ; elle tire sur les fils (recul)
    dict(sp=(-4, -2), kf=0.6, lean=-4, head=(-1, 0), abd=1, armP=('orig', -2, -2), armL=(-1, -2, -2),
         legs={'R3': dict(new=[(90, 89), (107, 57), (122, 55), (130, 65)]), 'R4': dict(new=R4_HIGH),
               'L1': dict(k=(-1, -2)), 'L2': dict(k=(-1, -1))},
         fx_list=[fx_silk(1.0, taut=0.35), fx_wrap(1)], ms=120),
    # 6 : elle plante les deux pattes avant dans le sol ; les fils cassent
    dict(sp=(3, 2), lean=3, head=(1, 1), armP=('orig', 1, 1), armL=(2, 1, 2),
         legs={'R3': dict(new=R3_SLAM), 'R4': dict(new=R4_SLAM), 'L1': dict(k=(1, 0))},
         fx_list=[fx_silk(1.0, cut=(0.12, 0.9)), fx_wrap(1), fx_slam_dust(0), fx_crack(0.3)], ms=60),
    # 7 : la fissure court jusqu'au cocon, le sol se soulève
    dict(sp=(3, 2), lean=3, head=(1, 0), armP=('orig', 1, 1), armL=(2, 1, 2),
         legs={'R3': dict(new=R3_SLAM), 'R4': dict(new=R4_SLAM)},
         fx_list=[fx_wrap(1), fx_slam_dust(1), fx_crack(1.0), fx_ground(1.0)], ms=60),
    # 8 : LES PATTES DE PIERRE JAILLISSENT (arrêt sur image, éclair)
    dict(sp=(3, 2), lean=3, head=(1, 0), armP=('orig', 1, 1), armL=(2, 1, 2),
         legs={'R3': dict(new=R3_SLAM), 'R4': dict(new=R4_SLAM)},
         fx_list=[fx_crack(1.0), fx_claws(1.0, flash=True), fx_debris(0.12, dust=0.7)], ms=230),
    # 9 : elles se referment sur le cocon
    dict(sp=(3, 2), lean=3, head=(1, 0), armP=('orig', 1, 1), armL=(2, 1, 2),
         legs={'R3': dict(new=R3_SLAM), 'R4': dict(new=R4_SLAM)},
         fx_list=[fx_crack(1.0), fx_claws(1.0, close=1.0), fx_debris(0.3, dust=0.9)], ms=120),
    # 10 : elles se brisent
    dict(sp=(2, 1), lean=2, armP=('orig', 0, 0), armL=(1, 0, 1),
         legs={'R3': dict(new=R3_SLAM), 'R4': dict(new=R4_SLAM)},
         fx_list=[fx_crack(1.0), fx_claws(1.0, close=1.0, crumble=0.4), fx_debris(0.5, dust=1.1, hollow=0.2)], ms=100),
    # 11 : éboulis et poussière
    dict(sp=(1, 1), lean=1, armP=('orig', 0, 0),
         legs={'R3': dict(new=R3_SLAM), 'R4': dict(new=R4_SLAM)},
         fx_list=[fx_crack(1.0), fx_claws(1.0, crumble=0.8), fx_debris(0.75, dust=1.2, hollow=0.5)], ms=100),
    # 12 : la poussière se défait
    dict(sp=(1, 0), legs={'R3': dict(new=[(90, 89), (108, 67), (122, 82), (126, 98)]),
                          'R4': dict(new=[(99, 77), (117, 61), (129, 77), (134, 93)])},
         fx_list=[fx_debris(1.0, dust=1.1, hollow=0.85)], ms=110),
    # 13 : les pattes se reposent l'une après l'autre
    dict(legs={'R3': dict(k=(0, -1), t=(1, -2)), 'R4': dict(new=[(99, 77), (114, 64), (122, 88), (124, 108)])}, ms=100),
    # 14 : en garde, un dernier frisson
    dict(abd=1, legs={'R4': dict(k=(0, -1)), 'L1': dict(k=(0, -1))}, ms=140),
]


# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom de l'animation][numéro d'image] = [(x, y, 'TEXTE')] : TEXTE écrit sur la toile du héros à partir de
# (x, y) en coordonnées de la GRILLE du dessin ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX, y + OY
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images
def build_all(which=('pose', 'attaque', 'speciale')):
    anims = {}
    for name in which:
        specs = {'pose': POSE, 'attaque': globals().get('ATTAQUE', []), 'speciale': globals().get('SPECIALE', [])}[name]
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []))
            fr.append((compose(cv, back, front, flash=spec.get('flash')), spec['ms']))
        anims[name] = fr
    return anims


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin), min(H, ys.max() + 1 + margin))


GAME_BOX = (OX, OY, OX + hd.FRAME_W, OY + hd.FRAME_H)       # la case du jeu : 128 × 120, sol en (64, 116)


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune, pas de tramage (les pixels restent nets)"""
    rgb = [im.convert('RGB') for im in images]
    W0, H0 = rgb[0].size
    sheet = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet.paste(im, (0, i * H0))
    ncol = len(sheet.getcolors(maxcolors=1 << 20) or [])
    if ncol <= 256:
        pal = sheet.quantize(colors=min(256, ncol), method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    boxes = {'pose': GAME_BOX}
    both = anims['attaque'] + anims['speciale'] + anims['pose']
    bb = bbox(both, 6)
    boxes['attaque'] = boxes['speciale'] = bb
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    # la planche : chaque animation sur ses rangées, ×3, numérotées (numéro et durée au-dessus de chaque image)
    k = 3
    blocks = []
    for name, per in (('pose', 10), ('attaque', 5), ('speciale', 5)):
        box = GAME_BOX if name == 'pose' else bb
        cells = [on_bg(img).crop(box) for img, _ in anims[name]]
        blocks.append((name, per, cells, [ms for _, ms in anims[name]]))
    Wt = max(min(per, len(cells)) * (cells[0].width * k + 6) for _, per, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + per - 1) // per) * (cells[0].height * k + 22) for _, per, cells, _ in blocks)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (dague et pattes avant)',
              'speciale': 'ATTAQUE SPECIALE (toile et griffes de pierre)'}
    for name, per, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % per == 0:
                y += ch + 22
            X = 6 + (i % per) * (cw + 6)
            sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sheet.save(os.path.join(OUT, f'anim-{NAME}-planche.png'))
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat, ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        bw, bh = box[2] - box[0], box[3] - box[1]
        fy = 374 - (GROUND - box[1])                    # les pieds sur le chemin de terre
        base = fond.crop((0, fy, bw, fy + bh))
        if base.width < bw:
            raise ValueError
    except Exception:
        base = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


# ---------------------------------------------------------------- outils de contrôle (brouillon)
def dev_sheet(name, frames, k=3, per=10, box=None, path=None):
    box = box or bbox(frames, 3)
    cells = [on_bg(img).crop(box) for img, _ in frames]
    cw, ch = cells[0].width * k, cells[0].height * k
    rows = (len(cells) + per - 1) // per
    sheet = Image.new('RGB', (min(per, len(cells)) * (cw + 4) + 4, rows * (ch + 16) + 4), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cells):
        X, Y = 4 + (i % per) * (cw + 4), 4 + (i // per) * (ch + 16)
        sheet.paste(c.resize((cw, ch), Image.NEAREST), (X, Y + 12))
        d.text((X + 2, Y), f'{i} ({frames[i][1]})', fill=(30, 20, 36))
    sheet.save(path or os.path.join(BROUILLON, f'dev-{name}.png'))


if __name__ == '__main__':
    os.makedirs(BROUILLON, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'decoupe':
        label_image(os.path.join(BROUILLON, 'decoupe.png'))
    elif len(sys.argv) > 1 and sys.argv[1] == 'dev':
        which = sys.argv[2]
        a = build_all((which,))
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        per = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        box = None
        if len(sys.argv) > 8:
            x0, y0, x1, y1 = map(int, sys.argv[5:9])
            box = (x0 + OX, y0 + OY, x1 + OX, y1 + OY)
        dev_sheet(which, a[which], k, per, box)
    else:
        anims = build_all()
        write_outputs(anims)
        for n in ('pose', 'attaque', 'speciale'):
            print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
        print('écrit dans', OUT)
