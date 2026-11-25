# Effets REÇUS par l'équipe (génériques) : soin, régénération, purification, résurrection, bouclier, défense,
# attaque, énergie, provocation, affaiblissement et ralentissement (ces deux derniers sur les ennemis).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/effets/build.py
#
# Décision du propriétaire (25/11/2026) : le lanceur joue sa propre spéciale ; ce que REÇOIT chaque allié est une petite
# animation commune, la même pour tous les héros, jouée par le jeu sur chaque case occupée au « moment de lancement »
# de la spéciale (noté en tête du build.py de chaque héros).
#
# CE QUE ÇA ÉCRIT (dossier sortie/ à côté de ce fichier) :
#   <effet>-<élément>-dos.png     les images de l'effet DERRIÈRE le héros, côte à côte (128 × 120 chacune)
#   <effet>-<élément>-devant.png  les images de l'effet DEVANT le héros (mêmes cases, même nombre)
#   <effet>-<élément>.json        durée de chaque image (ms), boucle ou non, et « eclat » : de combien le jeu éclaircit
#                                 (ou teinte) le dessin du héros lui-même à chaque image (couleur, pourcentage)
#   provocation-marque.png (+ .json) : la marque inventée (un œil en amande, la même que celle de Zaroth) qui bat
#                                 au-dessus de la tête ; cases de 32 × 24, le bas de la marque au milieu du bas de la case,
#                                 à poser juste au-dessus de la tête (le haut du dessin du héros), pas dans la case 128 × 120
#   effets.json                   la liste de tout (le jeu peut la lire) ; apercu/<effet>.gif : chaque effet animé sur
#                                 trois héros (mince, moyen, massif), ses quatre éléments côte à côte ; apercu/planche-<effet>.png :
#                                 toutes les images, ×3, numérotées ; et ../../../sortie/effets-equipe-planche.png
#                                 (tous les effets × éléments, au temps fort, sur les trois héros).
# Éléments : feu, vent, eau, terre (sauf provocation : rouge pour tous ; affaiblissement et ralentissement : une seule
# version, pour les ennemis ; nom de fichier sans élément).
#
# COMMENT LE JEU LES POSE : chaque image fait 128 × 120, comme une image de héros HD, et son point « pieds » est en
# (64, 116), comme le point « sol » des héros. On la pose donc exactement comme le héros de la case (même point, même
# échelle : 1 pixel = 1,22 au combat), le calque « dos » juste sous le héros, le calque « devant » juste au-dessus
# (même profondeur que la case). On ne la retourne PAS pour les ennemis (la lumière reste en haut à droite) : on la pose
# dans le conteneur de la case, pas dans celui du dessin retourné.
#
# Principe du dessin (comme les animations validées d'Eldra, Kael, Ilian, Isis…) : pas de dessin lissé ni agrandi ;
# chaque forme est peinte au pixel avec quelques tons de la palette de l'élément (du blanc au plus sombre), éclairée en
# haut à droite ; formes courbes (rubans, volutes, gouttes, bouffées), jamais de rayons droits répétés, jamais de
# quadrillage ni d'alvéoles, aucun noir, aucun contour noir (ce sont des lumières, pas des objets). Les lueurs sont des
# pixels translucides en quatre paliers d'opacité (comme la lueur rouge de Zaroth). L'effet doit aller sur les 36
# silhouettes : il entoure une « enveloppe » commune du corps (le tronc est toujours entre x = 54 et 76, y = 50 et 96 ;
# la tête entre y = 2 et 58) au lieu d'épouser un dessin précis.
import sys, os, math, json
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUTFX = os.path.join(HERE, 'sortie')
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
FOND = os.path.abspath(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule)

FW, FH = hd.FRAME_W, hd.FRAME_H          # 128 × 120
FX, GY = hd.FEET                          # (64, 116) : les pieds
CX = 65                                   # le milieu du tronc (les héros se tiennent un peu penchés vers l'ennemi)
CHEST = (65, 64)                          # la poitrine (toujours dans le tronc, pour les 36 héros)
LIGHT = np.array([0.6, -0.8])             # la lumière vient d'en haut à droite (x vers la droite, y vers le bas)

# ---------------------------------------------------------------- palettes (reprises des héros validés)
# Chaque élément : une rampe de six tons, du coeur blanc au bord le plus sombre.
RAMPS = {
    # feu : les flammes de Kael / Tybalt / Rook (coeur blanc, jaune pâle, or, orange, rouge orangé, rouge)
    'feu': [(255, 252, 236), (255, 238, 150), (255, 202, 70), (255, 146, 44), (234, 86, 40), (186, 40, 44)],
    # vent : Eldra / Myrr / Orin (blanc, blanc bleuté, cyan pâle, jade clair, jade, jade sombre)
    'vent': [(255, 255, 255), (226, 250, 255), (176, 236, 240), (120, 214, 190), (52, 176, 146), (26, 110, 104)],
    # eau : Ilian / Elyon / Zaroth (écume blanche, écume pâle, cyan, eau, eau ombre, eau profonde)
    'eau': [(255, 255, 255), (214, 246, 255), (138, 226, 248), (62, 176, 232), (34, 118, 206), (26, 70, 156)],
    # terre : Isis / Méduse / Anubis (éclair blanc, blanc doré, or de la terre, ambre, roche ombre, roche creux)
    'terre': [(255, 255, 240), (255, 246, 206), (255, 212, 92), (224, 150, 56), (142, 102, 74), (94, 64, 70)],
}
# l'aura d'attaque : toujours chaude (rouge-orangé / or), quel que soit l'élément ; le cramoisi du bout des langues
WARM = [(255, 252, 236), (255, 238, 150), (255, 202, 70), (255, 146, 44), (234, 86, 40), (186, 40, 44), (122, 24, 48)]
# la provocation : les rouges de Zaroth (coeur brûlant, rouge vif, rouge, rouge sombre, très sombre)
RED = [(255, 226, 200), (255, 96, 84), (222, 40, 64), (150, 20, 58), (92, 14, 52)]
# les taches sombres de la purification (violet-gris, jamais du noir), de la plus sombre à la plus pâle
SMUT = [(52, 36, 66), (78, 58, 92), (112, 92, 124), (156, 140, 166), (204, 194, 212)]
# l'affaiblissement : les violets de la fumée d'Anubis (lilas clair, violet, violet sombre, creux, plus sombre)
VIOLET = [(232, 206, 255), (176, 128, 224), (118, 70, 170), (70, 38, 104), (46, 24, 72)]
# le ralentissement : un bleu lourd et froid (bleu-gris pâle -> bleu nuit)
SLOWB = [(214, 228, 255), (150, 176, 232), (96, 122, 198), (60, 80, 152), (38, 48, 106), (26, 30, 72)]
# la teinte du héros à l'éclat (ce que le jeu mélange au dessin du héros) : le ton pâle de l'élément
ELEMS = ('feu', 'vent', 'eau', 'terre')
ELEM_EN = {'feu': 'fire', 'vent': 'wind', 'eau': 'water', 'terre': 'earth'}

# paliers d'opacité des lueurs (du plus pâle au plus fort)
GLOW_A = (46, 84, 128, 176)


# ---------------------------------------------------------------- un calque d'effet (RGBA), peint au pixel
class Layer:
    def __init__(self):
        self.rgb = np.zeros((FH, FW, 3), np.float32)
        self.a = np.zeros((FH, FW), np.float32)        # 0..1

    def put(self, x, y, c, a=255):
        """pose un pixel par-dessus ce qui est déjà là (a = opacité 0..255) ; rien sous la ligne du bas"""
        x, y = int(math.floor(x)), int(math.floor(y))
        if not (0 <= x < FW and 0 <= y < FH) or a <= 0:
            return
        al = a / 255.0
        A = self.a[y, x]
        ao = al + A * (1 - al)
        if ao <= 0:
            return
        self.rgb[y, x] = (np.array(c, np.float32) * al + self.rgb[y, x] * A * (1 - al)) / ao
        self.a[y, x] = ao

    def glow(self, F, tones, alphas=GLOW_A, fade=1.0):
        """une lueur douce : F (0..1, une valeur par pixel) coupée en quatre paliers ; tones = 4 couleurs du plus pâle
        palier (le bord) au plus fort (le coeur). fade (0..1) baisse toute l'opacité."""
        th = (0.12, 0.32, 0.56, 0.8)
        lvl = np.full(F.shape, -1)
        for i in range(4):
            lvl[F >= th[i]] = i                       # chaque pixel prend le plus haut palier atteint (marches nettes)
        for i in range(4):
            ys, xs = np.nonzero(lvl == i)
            if not len(ys):
                continue
            al = alphas[i] / 255.0 * fade
            c = np.array(tones[i], np.float32)
            A = self.a[ys, xs][:, None]
            ao = al + A * (1 - al)
            self.rgb[ys, xs] = (c * al + self.rgb[ys, xs] * A * (1 - al)) / np.maximum(ao, 1e-6)
            self.a[ys, xs] = ao[:, 0]
        return self

    def image(self):
        out = np.zeros((FH, FW, 4), np.uint8)
        out[:, :, :3] = np.clip(self.rgb + 0.5, 0, 255).astype(np.uint8)
        out[:, :, 3] = np.clip(self.a * 255 + 0.5, 0, 255).astype(np.uint8)
        out[out[:, :, 3] == 0] = 0
        return out


YY, XX = np.mgrid[0:FH, 0:FW].astype(np.float32) + 0.5


def disc_paint(layer, pts, tones, alpha=255, keep_best=True):
    """peint une suite de disques (x, y, largeur) : coeur clair au milieu, bord sombre (tones : coeur -> bord)"""
    best = {}
    for (px, py, wv) in pts:
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.2 else 0.8
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        a = alpha if not callable(alpha) else alpha(x, y)
        layer.put(x, y, tones[min(m - 1, int(k * m))], a)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def sprite(layer, rows, x, y, ramp, shift=0, alpha=255):
    """un petit dessin fait main : chiffres = tons de la rampe (0 = le plus clair), '.' = vide ; shift pâlit (-) ou
    fonce (+) tous les tons"""
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                k = max(0, min(len(ramp) - 1, int(ch) + shift))
                layer.put(x + i, y + j, ramp[k], alpha)


def smooth01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ell_field(cx, cy, rx, ry):
    """distance « elliptique » de chaque pixel au centre (1 = sur le bord)"""
    return np.sqrt(((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2)


def capsule(top, bot, hw_bot, hw_top, t, wob=1.0):
    """une lueur en forme de flamme douce : de bot (en bas, large hw_bot) à top (en haut, large hw_top, arrondi) ;
    les bords ondulent doucement (aucun trait droit) ; 1 au milieu, 0 au bord"""
    span = max(bot - top, 1.0)
    v = np.clip((YY - top) / span, 0, 1)                     # 0 en haut, 1 en bas
    hw = (hw_top + (hw_bot - hw_top) * v) * (1 + 0.08 * wob * np.sin(YY * 0.19 + t * 1.4))
    cap = min(hw_top * 0.9, span * 0.5)
    yc = top + cap                                           # le haut arrondi
    dy = np.where(YY < yc, (yc - YY) / max(cap, 1), 0)
    dyb = np.where(YY > bot - 6, (YY - (bot - 6)) / 6.0, 0)  # le bas, arrondi aussi quand il décolle
    d = np.sqrt((np.abs(XX - CX) / np.maximum(hw, 1)) ** 2 + dy ** 2 + dyb ** 2)
    return np.clip(1.0 - d, 0, 1) ** 0.55


# ---------------------------------------------------------------- les petites lumières de chaque élément
# Grains qui montent (soin, régénération, résurrection…) : chiffres = tons de la rampe (0 = blanc). Trois tailles.
MOTES = {
    'feu': [['1', '3'],                                    # braise
            ['.0', '12', '3.'],                            # braise qui file
            ['.01', '123', '34.']],                        # flammèche
    'vent': [['21'],                                       # brin
             ['.10', '23.'],                               # petite feuille
             ['..10', '.21.', '32..']],                    # plume
    'eau': [['1', '2'],                                    # goutte
            ['.0.', '112', '.3.'],                         # gouttelette
            ['.10.', '2..0', '3..1', '.32.']],             # bulle (vide au milieu)
    'terre': [['10', '32'],                                # grain d'or
              ['.10', '221', '32.'],                       # pétale
              ['..0.', '.121', '2232', '.33.']],           # grand pétale
}


def halo(layer, x, y, r, tones, k=1.0):
    """une petite lueur ronde et douce (sous un grain, pour qu'il se lise sur n'importe quel fond)"""
    x0, x1, y0, y1 = max(0, int(x - r - 1)), min(FW, int(x + r + 2)), max(0, int(y - r - 1)), min(FH, int(y + r + 2))
    if x0 >= x1 or y0 >= y1:
        return
    F = np.zeros((FH, FW), np.float32)
    F[y0:y1, x0:x1] = np.clip(1.0 - np.hypot(XX[y0:y1, x0:x1] - x, YY[y0:y1, x0:x1] - y) / r, 0, 1) * k
    layer.glow(F, tones, alphas=(40, 70, 100, 130))


def mote(layer, elem, x, y, size, shift=0, alpha=255, ramp=None, glow=True):
    rows = MOTES[elem][max(0, min(2, size))]
    R = ramp or RAMPS[elem]
    if glow:
        halo(layer, x, y, 3.0 + 1.2 * size, [R[3], R[2], R[2], R[1]], k=alpha / 255)
    sprite(layer, rows, int(round(x)) - len(rows[0]) // 2, int(round(y)) - len(rows) // 2, ramp or RAMPS[elem], shift, alpha)


# ---------------------------------------------------------------- formes communes
def ground_ring(back, front, rx, ry, w, tones, segs, cy=None, alpha=255, cx=None):
    """un anneau posé au sol, autour des pieds, en arcs séparés (jamais un cercle régulier) : la moitié de derrière
    (au-dessus de la ligne des pieds) dans le calque dos, celle de devant dans le calque devant ; plus épais devant.
    segs = [(angle de début, angle de fin)] en degrés (0 = à droite, 90 = devant)."""
    cx = CX if cx is None else cx
    cy = GY - 3 if cy is None else cy
    for (a0, a1) in segs:
        n = max(8, int(abs(a1 - a0) / 3))
        ptsb, ptsf = [], []
        for i in range(n + 1):
            s = i / n
            a = math.radians(a0 + (a1 - a0) * s)
            x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
            taper = math.sin(math.pi * s) ** 0.6
            ww = w * (0.55 + 0.45 * max(0.0, math.sin(a))) * taper + 0.3
            (ptsf if math.sin(a) > 0.05 else ptsb).append((x, y, ww))
        disc_paint(back, ptsb, tones, alpha)
        disc_paint(front, ptsf, tones, alpha)


def pool(back, front, rx, ry, tones, fade=1.0, cy=None, cx=None):
    """une flaque de lumière au sol (lueur aplatie) : ce qui est derrière les pieds dans le dos, le bord de devant devant"""
    cx = CX if cx is None else cx
    cy = GY - 2 if cy is None else cy
    F = np.clip(1.15 - ell_field(cx, cy, rx, ry), 0, 1)
    F = np.where(YY <= GY + 3, F, 0)
    Fb = np.where(YY < GY - 1, F, 0)
    Ff = np.where(YY >= GY - 1, F, 0) * 0.8
    back.glow(Fb, tones, fade=fade)
    front.glow(Ff, tones, fade=fade * 0.8)


def helix(back, front, y0, y1, R0, phase, turns, head, tail, w, tones, alpha=255, cx=None):
    """un ruban qui monte en spirale autour du corps : il passe derrière (dos) puis devant (devant). head : où en est la
    tête du ruban (0 = au sol, 1 = en haut) ; tail : sa longueur (même échelle)."""
    cx = CX if cx is None else cx
    s0 = max(0.0, head - tail)
    n = 70
    pb, pf = [], []
    for i in range(n + 1):
        s = s0 + (head - s0) * i / n
        if s < 0 or s > 1:
            continue
        th = phase + 2 * math.pi * turns * s
        R = R0 * (1 - 0.35 * s)
        x = cx + R * math.cos(th)
        y = y0 + (y1 - y0) * s + 4 * math.sin(th) * (1 - 0.5 * s)
        k = (s - s0) / max(head - s0, 1e-6)                        # 0 au bout de la queue, 1 à la tête
        ww = w * (k ** 0.8) * (1 - 0.6 * max(0.0, (s - 0.85) / 0.15)) + 0.2
        (pf if math.sin(th) > 0 else pb).append((x, y, ww))
    disc_paint(back, pb, tones, alpha)
    disc_paint(front, pf, tones, alpha)


def bloom(layer, c, r, tones, facing=60.0, alpha=255):
    """un petit éclat en nuage (un coeur et des pétales arrondis), sans aucun rayon"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-80, -20, 40, 100, 160, 220, 280):
        a = math.radians(facing + da)
        lobes.append((r * 0.9 * math.cos(a), -r * 0.9 * math.sin(a), r * (0.55 if abs(((da + 180) % 360) - 180) < 70 else 0.42)))
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                if math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy) <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    m = len(tones)
    for (x, y), D in best.items():
        layer.put(x, y, tones[min(m - 1, int(D * m))], alpha)


def body_glow(front, ramp, k, cy=60, rx=18, ry=28):
    """le corps s'éclaire : une lueur très douce posée devant la poitrine (le jeu éclaircit aussi le dessin lui-même,
    voir « eclat »)"""
    if k <= 0:
        return
    F = np.clip(1.05 - ell_field(CX, cy, rx, ry), 0, 1) * k
    front.glow(F, [ramp[2], ramp[1], ramp[1], ramp[0]], alphas=(12, 22, 34, 46))


def rising_motes(back, front, elem, t, n, seed, spawn=(0, 6), life=(5, 7), spread=(12, 34), speed=(6, 9),
                 y0=(98, 116), ramp=None, sizes=(0, 1, 2), fade_to=0):
    """des grains de lumière qui montent en se balançant ; un sur deux passe derrière le héros"""
    rng = np.random.RandomState(seed)
    for i in range(n):
        s = rng.uniform(*spawn)
        L = rng.uniform(*life)
        side = rng.choice([-1, 1])
        x0 = CX + side * rng.uniform(*spread)
        yb = rng.uniform(*y0)
        v = rng.uniform(*speed)
        ph = rng.uniform(0, 6.28)
        size = sizes[rng.randint(len(sizes))]
        back_side = (i % 3 == 0)
        age = t - s
        if age < 0 or age > L:
            continue
        u = age / L
        x = x0 + 3.0 * math.sin(ph + age * 1.1) - side * 4 * u          # ils se rapprochent un peu du corps
        y = yb - v * age
        if y < 2:
            continue
        sz = size if u < 0.6 else max(0, size - 1) if u < 0.85 else 0
        shift = -1 if u > 0.7 else 0
        al = 255 if u < 0.75 else 200
        mote(back if back_side else front, elem, x, y, sz, shift, al, ramp)


# ---------------------------------------------------------------- 1) SOIN
# Une lumière douce monte du sol autour du corps (une flaque, puis une colonne de lueur qui s'élève et s'en va par le
# haut), deux rubans de lumière montent en spirale autour de lui (derrière puis devant), des grains de l'élément
# (braises, plumes, gouttes, pétales d'or) montent en se balançant ; au temps fort (image 6) le corps s'éclaire.
SOIN_MS = [70, 70, 80, 80, 80, 90, 130, 110, 90, 80, 80, 90]


def fx_soin(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    N = len(SOIN_MS)
    # la flaque au sol : elle s'ouvre (0-3), reste, s'efface (8-11)
    grow = ease_out((t + 1) / 4)
    fade = 1.0 if t < 8 else max(0.0, 1 - (t - 7) / 4.5)
    pool(back, front, 12 + 22 * grow, 3 + 3.5 * grow, [R[3], R[2], R[1], R[0]], fade=fade)
    # la lueur qui monte : une flamme de lumière douce (plus étroite en haut, bords qui ondulent, haut arrondi) ;
    # son haut monte (1-6), puis le bas décolle et tout s'en va par le haut (7-11)
    if t >= 1:
        top = GY - (GY - 8) * ease_out(t / 6)
        bot = GY + 4 if t < 7 else GY + 4 - 17 * (t - 6)
        amp = 1.0 if t < 7 else max(0.0, 1 - (t - 6) / 5)
        F = capsule(top, bot, 33, 22, t) * amp
        back.glow(F, [R[2], R[2], R[1], R[0]], alphas=(70, 110, 150, 190))
        front.glow(F * 0.55, [R[2], R[1], R[1], R[0]], alphas=(14, 24, 34, 44))
    # deux rubans en spirale (tons clairs de l'élément)
    if 1 <= t <= 10:
        head = min(1.0, (t - 1) / 6.5)
        tail = 0.45 if t < 8 else 0.45 - 0.13 * (t - 7)
        if tail > 0.02:
            h2 = head if t < 8 else min(1.0, head)
            for ph in (0.4, 0.4 + math.pi):
                helix(back, front, GY - 4, 14, 30, ph, 1.15, h2 + (0.08 * (t - 7) if t >= 8 else 0), tail, 3.4,
                      [R[0], R[1], R[2]], alpha=255)
    # les grains qui montent
    rising_motes(back, front, elem, t, 22, 11, spawn=(0, 7), life=(4, 6), spread=(8, 34), speed=(7, 10),
                 sizes=(0, 1, 2, 2))
    # le corps s'éclaire au temps fort
    body_glow(front, R, {5: 0.4, 6: 0.7, 7: 0.4}.get(t, 0))
    if t in (6, 7):
        bloom(front, (CHEST[0] + 2, CHEST[1] - 4), 3.2 if t == 6 else 2.2, [R[0], R[1], R[2]], alpha=230)
    return back, front


SOIN_ECLAT = {4: 6, 5: 12, 6: 20, 7: 12, 8: 5}


# ---------------------------------------------------------------- 2) RÉGÉNÉRATION (soin dans la durée, en boucle)
# La version légère du soin : une petite flaque qui respire au sol et quelques grains qui montent sans fin.
# Boucle parfaite (10 images de 100 ms) : chaque grain revient à sa place à la fin du tour.
REGEN_MS = [100] * 10


def fx_regen(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    N = len(REGEN_MS)
    breath = 0.5 + 0.5 * math.cos(2 * math.pi * t / N)
    pool(back, front, 26 + 3 * breath, 5 + 0.8 * breath, [R[3], R[2], R[1], R[0]], fade=0.9 + 0.1 * breath)
    F = capsule(30, GY + 4, 26, 16, t) * (0.35 + 0.1 * breath)
    back.glow(F, [R[2], R[2], R[1], R[0]], alphas=(60, 90, 120, 150))
    # 6 grains, chacun avec sa phase : y va du sol au-dessus de la tête en un tour
    spots = [(-24, 0.0, 2, 1), (18, 0.17, 1, 0), (-10, 0.34, 2, 0), (27, 0.5, 2, 0), (-28, 0.67, 1, 0), (8, 0.84, 2, 1),
             (-17, 0.42, 1, 1), (22, 0.92, 1, 0)]
    for (dx, ph, size, back_side) in spots:
        u = (t / N + ph) % 1.0
        y = GY - 6 - 88 * u
        x = CX + dx + 2.5 * math.sin(2 * math.pi * (u * 1.5 + ph)) - dx * 0.25 * u
        sz = size if u < 0.65 else max(0, size - 1)
        al = 255 if 0.1 < u < 0.8 else 150
        if u > 0.93:
            continue
        mote(back if back_side else front, elem, x, y, sz, -1 if u > 0.7 else 0, al)
    # une petite volute claire qui monte d'un côté puis de l'autre (une seule à la fois, douce)
    u = (t / N) % 1.0
    for side, off in ((-1, 0.0), (1, 0.5)):
        uu = (u + off) % 1.0
        if uu < 0.6:
            yb = GY - 8 - 60 * uu
            pts = []
            for i in range(16):
                s = i / 15
                y = yb - 14 * s
                x = CX + side * (22 - 4 * s + 2.5 * math.sin(3 * s + uu * 6))
                pts.append((x, y, 2.6 * math.sin(math.pi * s) + 0.3))
            disc_paint(back if side < 0 else front, pts, [R[0], R[1], R[2]], alpha=int(150 * math.sin(math.pi * uu / 0.6)) + 90)
    return back, front


# ---------------------------------------------------------------- 3) PURIFICATION
# De petites taches sombres (violet-gris, jamais du noir) apparaissent sur le corps, s'en détachent et montent en
# petites volutes qui pâlissent et s'évaporent en un grain de lumière de l'élément ; le corps s'éclaire, propre.
PURIF_MS = [70, 80, 90, 80, 80, 80, 90, 120, 100, 90, 90]
# (x, y de départ sur le tronc, image de départ, sens de la volute, taille)
WISPS = [(60, 58, 0, -1, 1.0), (73, 72, 1, 1, 0.95), (58, 86, 1, -1, 0.9), (71, 94, 2, 1, 0.8), (67, 46, 2, 1, 0.85),
         (75, 56, 3, -1, 0.75)]


def smut_wisp(front, x, y, age, cw, size, R):
    """une tache qui se détache : 0 = posée sur le corps, puis elle monte en petite bouffée de fumée qui s'enroule,
    pâlit et s'évapore en un grain de lumière ; une lueur de l'élément l'entoure (on la voit sur un héros sombre)"""
    if age < 0:
        return
    if age < 1:
        F = np.clip(1.0 - np.hypot(XX - x, YY - y) / (7 * size), 0, 1) ** 0.7
        front.glow(F, [R[2], R[1], R[1], R[0]], alphas=(50, 84, 120, 150))
        for (dx, dy, r) in ((0, 0, 2.6 * size), (2.0, -1.4, 1.8 * size), (-1.8, 1.0, 1.6 * size)):
            disc_paint(front, [(x + dx, y + dy, 2 * r)], [SMUT[1], SMUT[0]], alpha=240)
        return
    a = age - 1                               # 0.. : elle monte
    if a > 5.2:
        return
    rise = 9.0 * a + 1.5 * a * a
    hx = x + cw * 4.0 * math.sin(a * 0.9)
    hy = y - rise
    if a < 4.0:
        sz = size * (1.0 - 0.13 * a)
        F = np.clip(1.0 - np.hypot(XX - hx, YY - hy) / (8 * sz), 0, 1) ** 0.7
        front.glow(F, [R[2], R[1], R[1], R[0]], alphas=(60, 100, 140, 170), fade=1 - a / 6)
        # couleur : sombre -> gris -> pâle ; la traînée s'enroule sous la bouffée
        k = min(3, int(a * 0.85))
        tones = [SMUT[min(4, k + 1)], SMUT[k]]
        al = int(245 - 30 * a)
        pts = []
        n = 20
        L = 7 + 3 * min(a, 2.0)
        for i in range(n + 1):
            s = i / n
            ang = math.radians(90 + cw * 300 * s)
            r = (L * 0.5) * (1 - 0.6 * s)
            px = hx + cw * (s * 4) + r * math.cos(ang) * 0.7
            py = hy + 1 + s * L * 0.9 + r * math.sin(ang) * 0.45
            pts.append((px, py, (2.4 * sz) * (1 - s) ** 0.8 + 0.5))
        disc_paint(front, pts, tones, alpha=al)
        for (dx, dy, r) in ((0, 0, 2.6 * sz), (1.8, -1.2, 1.7 * sz)):
            disc_paint(front, [(hx + dx, hy + dy, 2 * r)], tones, alpha=al)
    else:
        # elle s'évapore : un petit éclat de lumière de l'élément
        bloom(front, (hx, hy), 1.8 if a < 4.6 else 1.1, [R[0], R[1], R[2]], alpha=230)


def fx_purif(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    # une lueur légère de l'élément au début (le sort arrive)
    body_glow(front, R, {0: 0.35, 1: 0.2}.get(t, 0))
    for (x, y, s, cw, size) in WISPS:
        smut_wisp(front, x, y, t - s, cw, size, R)
    # propre : le corps s'éclaire, deux ou trois grains montent
    body_glow(front, R, {6: 0.5, 7: 0.85, 8: 0.45, 9: 0.2}.get(t, 0))
    rising_motes(back, front, elem, t, 6, 23, spawn=(5, 8), life=(3, 4), spread=(6, 26), speed=(7, 9), y0=(60, 100),
                 sizes=(0, 1))
    if t == 7:
        bloom(front, (CHEST[0] + 3, CHEST[1] - 6), 2.6, [R[0], R[1], R[2]], alpha=220)
    return back, front


PURIF_ECLAT = {6: 12, 7: 24, 8: 10}


# ---------------------------------------------------------------- 4) RÉSURRECTION
# Une grande colonne de lumière descend du ciel sur la case (un fil qui tombe, touche le sol, s'élargit), une onde de
# lumière s'ouvre au sol, des grains montent dans la colonne ; puis la colonne se resserre et remonte au ciel.
RESU_MS = [60, 60, 70, 90, 80, 80, 90, 100, 110, 90, 80, 80, 90, 110]


def column(back, front, R, top, bot, hw, wob, t, amp=1.0):
    """la colonne de lumière, des bords qui ondulent doucement (aucun trait droit), le haut qui s'efface"""
    if hw <= 0.3 or bot <= top:
        return
    edge = hw * (1 + 0.12 * np.sin(YY * 0.16 + t * 1.3) * wob)
    d = np.abs(XX - CX - 0.8 * np.sin(YY * 0.07 + t)) / np.maximum(edge, 0.5)
    v = np.where((YY >= top) & (YY <= bot), 1.0, 0.0)
    fadetop = np.clip(YY / 16.0, 0, 1)                   # le haut de la case : la colonne s'efface (vient du ciel)
    F = np.clip(1.0 - d, 0, 1) ** 0.7 * v * fadetop * amp
    halo = np.clip(1.0 - d / 2.1, 0, 1) ** 0.9 * v * fadetop * amp
    back.glow(halo, [R[2], R[1], R[1], R[0]], alphas=(70, 120, 170, 220))
    front.glow(F * 0.8, [R[1], R[1], R[0], R[0]], alphas=(24, 44, 66, 96))


def fx_resu(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    # 0-2 : le fil descend ; 3 : il touche le sol et s'élargit ; 4-8 : la colonne ; 9-13 : elle se resserre et remonte
    if t <= 2:
        bot = [44, 86, GY][t]
        column(back, front, R, 0, bot, 2.0 + t, 0.4, t)
        # la goutte de tête : un petit éclat au bout du fil
        bloom(front, (CX, bot - 2), 2.0 + 0.5 * t, [R[0], R[1], R[2]], alpha=240)
    elif t <= 8:
        hw = [12, 17, 19, 19, 18, 18][t - 3]
        column(back, front, R, 0, GY, hw, 1.0, t)
    else:
        k = t - 8                                         # 1..5
        hw = 18 - 3.2 * k
        bot = GY - 22 * (k - 1) if k > 1 else GY
        column(back, front, R, 0, bot, hw, 1.0, t, amp=1 - 0.12 * k)
    # au sol : la flaque, et une onde qui s'ouvre en arcs (3-8)
    if 2 <= t <= 11:
        f = 1.0 if t < 9 else 1 - (t - 8) / 4
        pool(back, front, 14 + 16 * ease_out((t - 1) / 4), 3 + 3 * ease_out((t - 1) / 4), [R[3], R[2], R[1], R[0]], fade=f)
    if 3 <= t <= 8:
        u = (t - 3) / 5
        rx, ry = 14 + 26 * ease_out(u), 3 + 4.5 * ease_out(u)
        w = 3.2 * (1 - u) + 0.8
        ground_ring(back, front, rx, ry, w, [R[0], R[1], R[2], R[3]],
                    [(-150, -40), (-20, 70), (100, 205)], alpha=int(255 - 120 * u))
    # les grains qui montent dans la colonne
    rising_motes(back, front, elem, t, 16, 31, spawn=(3, 10), life=(3, 5), spread=(2, 18), speed=(9, 13),
                 y0=(88, 116), sizes=(0, 1, 1))
    return back, front


RESU_ECLAT = {3: 10, 4: 18, 5: 22, 6: 18, 7: 12, 8: 7, 9: 3}


# ---------------------------------------------------------------- 5) BOUCLIER
# Une bulle translucide se dessine autour du héros : son bord lumineux monte des deux côtés depuis le sol et se referme
# en haut (petit éclat), l'intérieur à peine teinté ; un reflet court sur le bord en haut à droite (la lumière), puis
# la bulle se pose : le bord s'affine et pâlit. Aucun quadrillage, aucune alvéole.
BOUC_MS = [60, 60, 70, 80, 130, 90, 90, 90, 90, 90, 90, 100]
DOME = (CX, 70, 50, 62)               # la bulle : centre, demi-largeur, demi-hauteur (posée au sol, coupée par lui)
AG = math.degrees(math.asin((DOME[1] - (GY - 1)) / DOME[3]))     # l'angle où le bord touche le sol (à droite)
AGX = DOME[2] * math.cos(math.radians(AG))                          # demi-largeur de la bulle au sol


def dome_pt(ang):
    """un point du bord de la bulle ; ang en degrés : AG = au sol à droite, 90 = en haut, 180 - AG = au sol à gauche"""
    cx, cy, rx, ry = DOME
    a = math.radians(ang)
    return cx + rx * math.cos(a), cy - ry * math.sin(a)


def dome_rim(layer, a0, a1, w, tones, alpha=255, light=True):
    """un morceau du bord : plus épais et plus clair en haut à droite (là d'où vient la lumière)"""
    n = max(6, int(abs(a1 - a0) * 1.6))
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        x, y = dome_pt(a)
        k = max(0.0, math.cos(math.radians(a - 55))) if light else 0
        pts.append((x, y, w * (0.75 + 0.6 * k)))
    disc_paint(layer, pts, tones, alpha)


def dome_mask(shrink=0.0):
    cx, cy, rx, ry = DOME
    d = np.sqrt(((XX - cx) / (rx - shrink)) ** 2 + ((cy - YY) / (ry - shrink)) ** 2)
    return np.where(YY <= GY, d, 9)


def fx_bouclier(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    # le pied au sol (un anneau aplati, en arcs)
    if t <= 10:
        f = 1.0 if t < 8 else 1 - (t - 7) / 4
        ground_ring(back, front, AGX + 1, 5.5, 2.6 * f + 0.4, [R[1], R[2], R[3]], [(-178, -2), (2, 178)],
                    alpha=int(230 * f), cy=GY - 3)
    if t <= 3:
        # le bord monte des deux côtés (0 -> 90°) ; la pointe est blanche
        u = ease_out((t + 1) / 4)
        reach = AG + (88 - AG) * u
        dome_rim(front, AG, reach, 2.4, [R[0], R[1], R[2]], alpha=240)
        dome_rim(front, 180 - AG, 180 - reach, 2.4, [R[0], R[1], R[2]], alpha=240)
        for a in (reach, 180 - reach):
            x, y = dome_pt(a)
            bloom(front, (x, y), 1.8, [R[0], R[0], R[1]], alpha=255)
        if t == 3:
            inside = dome_mask() < 1
            back.glow(np.where(inside, 0.2, 0), [R[1]] * 4, alphas=(40, 40, 40, 40))
    else:
        k = t - 4                                          # 0.. : fermé
        settle = max(0.0, (t - 7) / 4)                    # 0 -> 1 : il se pose (s'affine, pâlit)
        inside = dome_mask() < 1
        tint_a = int(36 - 20 * settle) if t < 11 else 10
        back.glow(np.where(inside, 0.2, 0), [R[1]] * 4, alphas=(tint_a,) * 4)
        front.glow(np.where(inside, 0.2, 0), [R[1]] * 4, alphas=(max(6, int(14 - 8 * settle)),) * 4)
        # un voile plus clair contre le bord (l'épaisseur de la bulle), surtout en haut à droite
        dm = dome_mask()
        band = np.clip(1 - np.abs(dm - 0.93) / 0.07, 0, 1)
        side = np.clip(0.35 + 0.65 * ((XX - DOME[0]) / DOME[2] * 0.6 + (DOME[1] - YY) / DOME[3] * 0.8), 0, 1)
        front.glow(band * side * (1 - 0.6 * settle), [R[1], R[1], R[0], R[0]], alphas=(30, 50, 76, 100))
        w = 2.4 - 1.2 * settle
        al = int(245 - 110 * settle)
        dome_rim(front, AG, 180 - AG, w, [R[1], R[2], R[3]] if settle < 0.6 else [R[2], R[3]], alpha=al)
        if t == 4:
            # il se referme en haut : un éclat
            bloom(front, dome_pt(90), 3.4, [R[0], R[0], R[1], R[2]])
        if t == 5:
            bloom(front, dome_pt(90), 2.0, [R[0], R[1]], alpha=200)
        # le reflet : un croissant clair en haut à droite, qui glisse le long du bord (vers le bas à droite)
        if t <= 10:
            g = 30 + 52 * (1 - min(1.0, k / 6))          # angle du reflet : 82° -> 30°
            dome_rim(front, g - 10, g + 12, 2.0 - 0.8 * settle, [R[0], R[0], R[1]], alpha=255 - int(80 * settle))
            # un second reflet plus discret, à l'intérieur, parallèle au bord (pas un trait : un croissant effilé)
            pts = []
            for i in range(13):
                s = i / 12
                a = math.radians(48 + 34 * s)
                x = DOME[0] + (DOME[2] - 6) * math.cos(a)
                y = DOME[1] - (DOME[3] - 7) * math.sin(a)
                pts.append((x, y, 1.6 * math.sin(math.pi * s) + 0.2))
            disc_paint(front, pts, [R[0], R[1]], alpha=int(150 * (1 - settle)))
        # quelques étincelles qui brillent sur le bord (une par image, à des places différentes)
        for (tt, a) in ((5, 140), (6, 20), (7, 115), (8, 160), (9, 60)):
            if t == tt:
                x, y = dome_pt(a)
                front.put(x, y, R[0], 255)
                front.put(x + 1, y, R[1], 220)
                front.put(x, y - 1, R[1], 220)
    return back, front


BOUC_ECLAT = {4: 20, 5: 10}


# ---------------------------------------------------------------- 6) DÉFENSE EN HAUSSE
# Des plaques de lumière de l'élément (écailles d'or en fusion, plumes de jade, cristaux de glace, pierres d'or)
# arrivent de tout autour en arcs et se plaquent sur lui (une ceinture autour de la taille, deux aux épaules), avec
# un petit à-coup ; un éclat les parcourt, un petit anneau s'ouvre au sol ; puis elles pâlissent et s'éteignent en grains.
DEF_MS = [60, 60, 70, 70, 120, 80, 90, 90, 90, 80, 80, 90]
# (x, y de la place sur le corps, devant ?, angle d'arrivée en degrés, retard)
PLATES = [(65, 79, True, 270, 0.0), (50, 77, True, 210, 0.3), (80, 77, True, 330, 0.15),
          (42, 72, False, 160, 0.45), (88, 71, False, 20, 0.2),
          (54, 51, True, 130, 0.35), (77, 50, True, 50, 0.1)]
# les plaques : une forme par élément, peinte au pixel et éclairée en haut à droite (le bord vers la lumière plus clair,
# une arête claire, le bas plus sombre) ; environ 10 × 12 pixels, assez grandes pour se lire comme une armure.
#   feu : une écaille d'or en fusion (arrondie en haut, pointe en bas) ; vent : une plume-plaque penchée ;
#   eau : un cristal de glace (pointu en haut et en bas, deux faces) ; terre : une pierre d'or taillée, plus large.
def plate_shape(elem, u, v):
    """u, v : position dans la plaque (-1..1, v vers le bas) ; renvoie la « profondeur » (>0 dedans) et la normale"""
    if elem == 'feu':
        w = math.sqrt(max(0.0, 1 - ((v + 0.25) / 0.85) ** 2)) if v < 0.2 else (1 - v) / 0.8 * 0.95
        inside = w - abs(u)
    elif elem == 'vent':
        uu = u - 0.35 * v                                   # penchée
        w = 0.62 * max(0.0, math.sin(math.pi * min(2.0, max(0.0, v + 1)) / 2)) ** 0.8
        inside = w - abs(uu)
        u = uu / max(w, 0.1)
    elif elem == 'eau':
        w = 0.8 * max(0.0, 1 - abs(v)) ** 0.9
        inside = w - abs(u)
    else:
        inside = 1 - (abs(u) ** 2.4 + (abs(v + 0.05) / 0.85) ** 2.4)
    return inside, u


def plate(layer, elem, x, y, shift=0, alpha=255, flash=False, size=1.0):
    R = RAMPS[elem]
    hw, hh = 5.0 * size, 6.0 * size
    if elem == 'terre':
        hw, hh = 6.0 * size, 5.0 * size
    for j in range(int(-hh - 1), int(hh + 2)):
        for i in range(int(-hw - 1), int(hw + 2)):
            u, v = (i + 0.5) / hw, (j + 0.5) / hh
            inside, un = plate_shape(elem, u, v)
            if inside <= 0:
                continue
            edge = inside < 0.22
            if elem == 'eau':
                k = 1 if un > 0 else 3                     # deux faces : la droite au soleil, la gauche à l'ombre
                if v > 0.25:
                    k += 1
            else:
                lit = 0.6 * un - 0.8 * v                    # lumière en haut à droite
                k = 3 - int(round(1.6 * lit + 0.4))
                k = max(1, min(4, k))
            if edge:
                k = 1 if (un > 0 or v < -0.3) else min(5, k + 1)
            if flash:
                k = max(0, k - 2)
            k = max(0, min(5, k + shift))
            layer.put(x + i, y + j, R[k], alpha)


def fx_defense(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    for i, (px, py, fr, ang, delay) in enumerate(PLATES):
        # arrivée : 0 -> 1 entre l'image delay et 3.5 + delay (en arc : elles tournent un peu autour de lui)
        u = (t - delay) / 3.6
        if u < 0:
            continue
        lay = front if fr else back
        if u < 1:
            e = ease_out(u)
            a = math.radians(ang + 40 * (1 - e))
            dist = 46 * (1 - e)
            x = px + dist * math.cos(a)
            y = py - dist * math.sin(a) * 0.8
            # une petite traînée courbe derrière la plaque (tons clairs, effilée)
            pts = []
            for j in range(8):
                s = j / 7
                e2 = ease_out(max(0.0, u - 0.18 * s))
                a2 = math.radians(ang + 40 * (1 - e2))
                d2 = 46 * (1 - e2)
                pts.append((px + d2 * math.cos(a2), py - d2 * math.sin(a2) * 0.8, 2.4 * (1 - s) + 0.3))
            disc_paint(lay, pts, [R[1], R[2]], alpha=170)
            plate(lay, elem, x, y, alpha=235)
            continue
        # posée : à-coup (un pixel plus près, puis en place), éclat qui les parcourt, puis elles pâlissent
        age = t - delay - 3.6
        snap = 1 if age < 1 else 0
        x = px + (CX - px) * 0.06 * snap
        y = py
        flash = (int(age) == 0) or (t == 6 + (i % 3))
        if t <= 8:
            plate(lay, elem, x, y, alpha=245, flash=flash)
        elif t <= 10:
            plate(lay, elem, x, y - (t - 8), shift=-1, alpha=int(200 - 60 * (t - 9)))
        else:
            # il en reste des grains qui montent
            mote(lay, elem, x + 1, y - 5, 0, -1, 200)
    # un petit anneau au sol, ouvert au moment où elles se plaquent
    if 4 <= t <= 9:
        u = (t - 4) / 5
        ground_ring(back, front, 22 + 14 * ease_out(u), 4 + 2.5 * ease_out(u), 2.8 * (1 - u) + 0.6,
                    [R[1], R[2], R[3]], [(-160, -30), (-10, 80), (100, 190)], alpha=int(240 - 120 * u))
    body_glow(front, R, {4: 0.6, 5: 0.35}.get(t, 0))
    return back, front


DEF_ECLAT = {4: 26, 5: 14, 6: 6}


# ---------------------------------------------------------------- 7) ATTAQUE EN HAUSSE
# Une aura chaude monte autour de lui : des langues de flamme douces (or, orange, rouge) naissent au sol et le long de
# son corps, ondulent vers le haut, puis se détachent et s'envolent ; des braises de l'élément montent, un ruban de
# l'élément tourne autour de lui (sa couleur à lui : feu, vent, eau, terre). Au temps fort, il s'échauffe (rougeoie).
ATK_MS = [60, 70, 70, 80, 90, 120, 90, 80, 80, 80, 80, 90]
# les langues : (x au pied, y au pied, hauteur, largeur, penche, phase, devant ?)
TONGUES = [(33, 116, 34, 9.0, -6, 0.0, False), (98, 116, 30, 8.5, 6, 1.7, False),
           (39, 92, 26, 7.5, -7, 2.9, False), (93, 86, 30, 8.0, 6, 0.9, False),
           (46, 62, 22, 6.5, -6, 2.2, False), (88, 58, 24, 7.0, 5, 3.6, False),
           (50, 117, 13, 6.0, -3, 1.1, True), (82, 117, 11, 5.5, 3, 2.5, True)]


def flame(layer, x0, y0, h, w, lean, ph, tones, alpha=255, cut=0.0):
    """une langue de flamme (pointe en haut, ondulante) ; tones : du coeur (au pied, au milieu) au bout (rouge) ;
    cut (0..1) : le bas est déjà parti (la flamme se détache et monte)"""
    if h < 2:
        return
    n = int(h * 1.5) + 4
    best = {}
    for i in range(n + 1):
        v = i / n
        if v < cut:
            continue
        yc = y0 - h * v
        xc = x0 + lean * v * v + 2.6 * math.sin(ph + v * 4.6) * v ** 1.4       # le bout ondule et se recourbe
        vv = min(1.0, 0.08 + v * 0.92)
        hw = w * (4 * vv * (1 - vv)) ** 0.55 * (1 - v) ** 0.25                  # une goutte : ventre en bas, bout effilé
        if cut:
            hw *= min(1.0, (v - cut) / 0.15 + 0.2)
        for x in range(int(xc - hw - 1), int(xc + hw + 2)):
            dx = abs(x + 0.5 - xc)
            if dx <= hw:
                k = 0.55 * (dx / max(hw, 0.5)) + 0.6 * v
                key = (x, int(yc))
                if k < best.get(key, 9):
                    best[key] = k
    m = len(tones)
    for (x, y), k in best.items():
        layer.put(x, y, tones[min(m - 1, int(k * m * 0.9))], alpha)


def fx_attaque(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    # la lueur chaude qui monte (derrière) ; plus forte au temps fort
    amp = [0.25, 0.45, 0.65, 0.8, 0.95, 1.0, 0.9, 0.8, 0.65, 0.45, 0.3, 0.15][t]
    top = GY - 100 * ease_out((t + 1) / 5)
    F = np.clip(1.05 - ell_field(CX, (GY + top) / 2 + 6, 31, (GY - top) / 2 + 6), 0, 1) ** 0.8
    F = np.where(YY <= GY + 1, F, 0) * amp
    back.glow(F, [WARM[4], WARM[3], WARM[2], WARM[1]], alphas=(70, 110, 150, 190))
    # les langues de flamme
    for (x0, y0, h, w, lean, ph, fr) in TONGUES:
        lay = front if fr else back
        grow = ease_out((t + 1) / 4) if t < 4 else 1.0
        flick = 1 + 0.18 * math.sin(ph + t * 2.1)
        hh = h * grow * flick
        cut = 0.0
        yy = y0
        if t >= 8:
            cut = 0.25 * (t - 7)                         # elles se détachent par le bas et montent
            yy = y0 - 6 * (t - 7)
        tones = WARM if fr else WARM[1:]
        if cut < 0.95:
            flame(lay, x0, yy, hh, w * (0.8 if fr else 1), lean, ph + t * 1.3, tones, alpha=235 if fr else 255, cut=cut)
    # un ruban de l'élément qui tourne autour de lui en montant (sa couleur)
    if 2 <= t <= 10:
        head = min(1.0, (t - 2) / 5.5)
        tail = 0.4 if t < 8 else 0.4 - 0.12 * (t - 7)
        if tail > 0.02:
            helix(back, front, GY - 6, 12, 32, 1.2, 1.0, head + (0.1 * (t - 7) if t >= 8 else 0), tail, 2.4,
                  [R[0], R[2], R[3]], alpha=230)
    # les braises (ton de l'élément)
    rising_motes(back, front, elem, t, 14, 47, spawn=(1, 8), life=(3, 5), spread=(10, 30), speed=(8, 12),
                 y0=(70, 112), sizes=(0, 1))
    return back, front


ATK_ECLAT = {4: 12, 5: 22, 6: 12, 7: 5}
ATK_TEINTE = (255, 120, 60)


# ---------------------------------------------------------------- 8) ÉNERGIE
# Trois orbes lumineux arrivent d'en haut et du côté, chacun sur sa courbe, avec une petite traînée effilée, et entrent
# dans la poitrine l'un après l'autre (petit éclat à chaque fois) ; au troisième, un éclat plus grand, le corps s'éclaire.
ENER_MS = [70, 70, 70, 80, 80, 90, 120, 90, 90, 100]
# (départ, deux points de contrôle de la courbe, image de départ, image d'arrivée)
ORBS = [((10, 14), (14, 40), (40, 66), 0, 3.2), ((96, 2), (110, 26), (88, 46), 0.6, 4.2), ((126, 56), (112, 86), (86, 80), 1.4, 5.3)]


def orb(layer, c, r, R, alpha=255):
    cx, cy = c
    # le halo (translucide), puis le coeur blanc
    F = np.clip(1.0 - np.hypot(XX - cx, YY - cy) / (r * 2.2), 0, 1)
    layer.glow(F * 1.1, [R[3], R[2], R[1], R[1]], alphas=(50, 90, 140, 190))
    disc_paint(layer, [(cx, cy, 2 * r)], [R[0], R[0], R[1], R[2]], alpha)  # noqa
    layer.put(cx + r * 0.4, cy - r * 0.5, R[0], 255)


def fx_energie(elem, t):
    R = RAMPS[elem]
    back, front = Layer(), Layer()
    tgt = (CHEST[0], CHEST[1] - 2)
    arrived = 0
    for (p0, p1, p2, s, e) in ORBS:
        if t < s:
            continue
        u = (t - s) / (e - s)
        if u >= 1:
            arrived += 1
            age = t - e
            if age < 1.2:
                bloom(front, (tgt[0] + 1, tgt[1]), 3.0, [R[0], R[1], R[2]], alpha=240)
            continue
        e2 = u ** 1.4                                     # il accélère en arrivant
        path = bezier(p0, p1, p2, tgt, 60)
        i = int(e2 * 60)
        cx, cy = path[i]
        # la traînée : le bout de la courbe parcourue, effilé
        j0 = max(0, i - 22)
        pts = [(path[j][0], path[j][1], 3.6 * ((j - j0) / max(i - j0, 1)) ** 1.3 + 0.2) for j in range(j0, i + 1)]
        disc_paint(front, pts, [R[1], R[2], R[3]], alpha=200)
        orb(front, (cx, cy), 3.2 + 0.6 * (1 - u), R)
    # le dernier entré : grand éclat, le corps s'éclaire, quelques grains repartent
    if t == 6:
        bloom(front, (tgt[0] + 1, tgt[1] - 1), 5.0, [R[0], R[0], R[1], R[2]])
    if t == 7:
        bloom(front, (tgt[0] + 1, tgt[1] - 1), 3.2, [R[0], R[1], R[2]], alpha=210)
    body_glow(front, R, {6: 0.9, 7: 0.55, 8: 0.25}.get(t, 0), cy=60)
    if t >= 6:
        rng = np.random.RandomState(5)
        for k in range(6):
            a = rng.uniform(0, 6.28)
            d = 6 + 5 * (t - 6) + rng.uniform(0, 3)
            x, y = tgt[0] + d * math.cos(a), tgt[1] - d * math.sin(a) * 0.8 - 2 * (t - 6)
            if t < 9 or k % 2:
                front.put(x, y, R[0] if t < 8 else R[1], 230)
                if t < 8:
                    front.put(x + 1, y, R[2], 200)
    return back, front


ENER_ECLAT = {3: 8, 4: 9, 5: 10, 6: 22, 7: 12, 8: 4}


# ---------------------------------------------------------------- 9) PROVOCATION (sur le lanceur seulement, rouge)
# Une lueur rouge douce et translucide pulse autour de son corps (deux battements : elle gonfle puis pâlit), plus large
# vers le haut comme une chaleur, sans aucun trait ni anneau ; la marque inventée (l'œil en amande de Zaroth) bat
# au-dessus de sa tête (fichier à part, à poser au-dessus du haut du dessin).
PROV_MS = [70, 80, 110, 90, 80, 80, 80, 110, 90, 90, 90, 100]
# la marque : la même que celle de Zaroth (validée) ; lettres = tons de RED (M coeur … Q très sombre)
MARK = {
    0: ['.....NNNNNNM.....',
        '...NNNNOOONNMM...',
        '..OOPPOQQQOOONM..',
        '.OOPPPQNMMQOOONM.',
        'POPPPPQNMMQOOOONM',
        '.POPPPQNNNQOOONN.',
        '..PPPPPQQQPOOOO..',
        '...PPPPPPPOOOO...',
        '.....PPPPPOO.....'],
    1: ['.......NNNNNNM.......',
        '....NNNNNNNNNNNMM....',
        '...ONNOOOQQQOOONMM...',
        '..OOPPPPQQMQQOOOOMM..',
        '.OOPPPPQQNMMQQOOOONM.',
        'POPPPPPQNNMMMQOOOOONM',
        '.POPPPPQQNNNQQOOOONN.',
        '..PPPPPPQQNQQOOOOOO..',
        '...PPPPPPQQQPPPOOO...',
        '....PPPPPPPPOOOOO....',
        '.......PPPPPOO.......'],
    2: ['....NNNNM....',
        '..NNNOQONNM..',
        '.OOPPQMQOONM.',
        'PPPPQNMMQOOOM',
        '.POPPQNQOONN.',
        '..PPPPQPOOO..',
        '....PPPPO....'],
}
MARK_LETTERS = {'M': 0, 'N': 1, 'O': 2, 'P': 3, 'Q': 4}
# la marque à chaque image : (taille 0, 1, 2 ou None, montée en pixels)
PROV_MARK = [None, 2, 0, 1, 1, 0, 0, 1, 1, 0, 2, 2]
MARK_W, MARK_H = 32, 24
# la lueur à chaque image : (ampleur 0..1, gonflement en pixels)
PROV_GLOW = [(0.35, 0), (0.7, 1), (1.0, 3), (0.85, 4), (0.6, 3), (0.45, 2), (0.7, 2), (1.0, 4), (0.85, 5), (0.6, 5),
             (0.35, 6), (0.15, 6)]


def fx_provoc(t):
    back, front = Layer(), Layer()
    amp, grow = PROV_GLOW[t]
    # une chaleur : enveloppe du corps, plus large en haut, des bords qui ondulent comme une flamme lente
    top = 8 - grow
    cy = (GY + top) / 2
    ry = (GY - top) / 2 + 2
    wav = 1 + 0.07 * np.sin(YY * 0.21 + t * 0.9) + 0.05 * np.sin(XX * 0.17 - t * 1.4)
    rx = (27 + grow) * (1 + 0.18 * np.clip((cy - YY) / ry, 0, 1))
    d = np.sqrt(((XX - CX) / rx) ** 2 + ((YY - cy) / ry) ** 2) * wav
    F = np.clip(1.25 - d, 0, 1) / 0.45
    F = np.clip(F, 0, 1) ** 0.9 * amp
    F = np.where(YY <= GY + 1, F, 0)
    back.glow(F, [RED[3], RED[2], RED[1], RED[1]], alphas=(50, 86, 124, 164))
    # un reflet rouge très léger devant le corps aux battements
    if amp >= 0.85:
        body_glow(front, [RED[1], RED[1], RED[1], RED[2]], 0.6 if amp >= 1 else 0.35)
    # deux braises rouges qui montent à chaque battement
    for (s, x0) in ((2, 44), (3, 86), (7, 50), (8, 82)):
        age = t - s
        if 0 <= age < 4:
            back.put(x0 + math.sin(age) * 2, 70 - 9 * age, RED[1] if age < 2 else RED[2], 230)
            back.put(x0 + math.sin(age) * 2, 71 - 9 * age, RED[2], 200)
    return back, front


MARK_SIZE = {0: (8.5, 4.2), 1: (10.5, 5.2), 2: (6.5, 3.3)}     # demi-largeur, demi-hauteur de l'œil


def mark_frame(t):
    """la marque seule, dans une case de 32 × 24 (le bas de la marque au milieu du bas de la case) : un œil en amande
    rouge (deux arcs qui se rejoignent en pointe), une pupille RONDE sombre et un reflet en haut à droite ; signe
    inventé, aucune lettre, aucune croix"""
    img = np.zeros((MARK_H, MARK_W, 4), np.uint8)
    k = PROV_MARK[t]
    if k is None:
        return img
    w, h = MARK_SIZE[k]
    cx, cy = MARK_W / 2, MARK_H - h - 1.5 - {0: 1, 1: 0, 2: 2}[k]
    pr = h * 0.62                                           # rayon de la pupille
    for y in range(MARK_H):
        for x in range(MARK_W):
            u, v = (x + 0.5 - cx) / w, (y + 0.5 - cy)
            if abs(u) >= 1:
                continue
            lim = h * (1 - u * u) ** 0.85
            if abs(v) > lim:
                continue
            border = abs(v) > lim - 1.3
            dp = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if border:
                c = RED[1] if (v < 0 and u > -0.4) else RED[3] if v > 0 else RED[2]
            elif dp <= pr:
                c = RED[4] if dp > pr - 1.1 else RED[3]
            else:
                c = RED[2] if v > 0 else RED[1]
            img[y, x, :3] = c
            img[y, x, 3] = 255
    # le reflet de la pupille (un pixel, deux pour le grand œil), en haut à droite
    hx, hy = int(cx + pr * 0.35), int(cy - pr * 0.45)
    img[hy, hx, :3] = RED[0]
    img[hy, hx, 3] = 255
    if k == 1:
        img[hy, hx - 1, :3] = RED[0]
        img[hy, hx - 1, 3] = 255
    return img


PROV_ECLAT = {2: 16, 3: 10, 7: 18, 8: 10}
PROV_TEINTE = RED[1]


# ---------------------------------------------------------------- 10) AFFAIBLISSEMENT (défense en baisse, ennemis)
# Un voile violet sombre et translucide se forme au-dessus de la tête, descend sur le corps (bord du bas en festons qui
# ondulent, quelques gouttes qui tombent) et s'enfonce dans le sol en une flaque qui s'efface ; de petits éclats
# d'armure violets se détachent et tombent.
AFF_MS = [70, 80, 90, 90, 90, 90, 100, 100, 90, 90, 90, 100]
# (x, y de départ, image de départ)
SHARDS = [(56, 60, 4, ['.21', '232', '33.']), (76, 66, 5, ['12.', '233', '.3.']), (62, 78, 6, ['.1', '23', '3.']),
          (72, 50, 6, ['21', '32'])]


def veil(back, front, top, bot, alpha_b, alpha_f, t, tones):
    """le voile : une bande entre top et bot, aux bords arrondis (l'enveloppe du corps) et au bas en festons"""
    hw = 33
    fest = bot + 3.5 * np.sin((XX - CX) * 0.33 + t * 0.8) + 1.5 * np.sin((XX - CX) * 0.71 - t)
    side = np.clip(1 - (np.abs(XX - CX) / hw) ** 4, 0, 1)
    arch = top + 9 * (np.abs(XX - CX) / hw) ** 2 + 1.5 * np.sin((XX - CX) * 0.4 - t * 0.7)   # le haut en voûte qui ondule
    inside = (YY >= arch) & (YY <= fest) & (side > 0)
    depth = np.clip((YY - arch) / max(bot - top, 1), 0, 1)
    F = np.where(inside, (0.3 + 0.7 * depth) * side ** 0.5, 0)
    edge = np.where(inside & (YY >= fest - 2.5), 1.0, 0)
    F = np.maximum(F, edge)
    back.glow(F, [tones[3], tones[2], tones[2], tones[1]], alphas=tuple(int(a * alpha_b) for a in (80, 120, 160, 210)))
    front.glow(F, [tones[3], tones[2], tones[2], tones[1]], alphas=tuple(int(a * alpha_f) for a in (50, 76, 104, 150)))
    return fest


def fx_affaib(t):
    back, front = Layer(), Layer()
    T = VIOLET
    # 0-2 : il naît au-dessus de la tête ; 3-8 : il descend ; 9-11 : il s'enfonce dans le sol
    if t <= 2:
        top, bot = 2, 6 + 6 * t
        ab, af = 0.6 + 0.2 * t, 0.5 + 0.2 * t
    elif t <= 8:
        u = smooth01((t - 2) / 6)
        top = 2 + 70 * u
        bot = 18 + 96 * u
        ab, af = 1.0, 1.0
    else:
        k = t - 8
        top = 72 + 14 * k
        bot = GY - 1
        ab, af = 1 - 0.22 * k, 1 - 0.25 * k
    if top < bot - 1:
        fest = veil(back, front, top, bot, ab, af, t, T)
        # des gouttes qui tombent du bas du voile (3-8)
        if 3 <= t <= 9:
            for (gx, ph) in ((44, 0.0), (60, 0.5), (79, 0.25), (88, 0.75)):
                drop_y = bot + 5 + ((t * 0.5 + ph) % 1.0) * 10
                if drop_y < GY:
                    front.put(gx, drop_y, T[1], 230)
                    front.put(gx, drop_y + 1, T[2], 230)
                    front.put(gx, drop_y + 2, T[3], 200)
    # la flaque au sol (elle grandit quand le voile arrive, puis s'efface)
    if t >= 6:
        f = min(1.0, (t - 5) / 3) * (1.0 if t < 10 else 1 - (t - 9) / 3)
        pool(back, front, 30, 5.5, [T[3], T[3], T[2], T[2]], fade=f)
    # les éclats d'armure qui se détachent et tombent
    for (x, y, s, rows) in SHARDS:
        age = t - s
        if 0 <= age < 5:
            yy = y + 3 * age + 2.2 * age * age
            if yy < GY - 1:
                halo(front, x + age * (1 if x > CX else -1) + 1, yy + 1, 4, [T[2], T[1], T[1], T[0]], k=0.8)
                sprite(front, rows, int(x + age * (1 if x > CX else -1)), int(yy), [T[0], T[0], T[1], T[2]], shift=min(1, age // 2))
    return back, front


AFF_ECLAT = {5: 12, 6: 20, 7: 20, 8: 12}
AFF_TEINTE = VIOLET[3]


# ---------------------------------------------------------------- 11) RALENTISSEMENT (ennemis)
# Trois longs rubans bleus, lourds (comme une eau épaisse), tombent sur lui, s'enroulent autour du corps et des jambes
# (derrière puis devant) et l'alourdissent : ils glissent lentement vers le sol, s'y étalent en une flaque qui colle,
# quelques gouttes lourdes tombent. Plus lent que les autres effets (c'est un ralentissement).
SLOW_MS = [70, 80, 90, 100, 110, 110, 110, 110, 100, 100, 100, 110]


def fx_ralent(t):
    back, front = Layer(), Layer()
    T = SLOWB
    # le haut des rubans : ils tombent vite (0-2) puis glissent lentement (3-10)
    if t <= 2:
        y_hi, y_lo = 10 + 8 * t, 30 + 26 * t
    else:
        u = smooth01((t - 2) / 8)
        y_hi, y_lo = 26 + 52 * u, 84 + 30 * u
    fade = 1.0 if t < 10 else 1 - (t - 9) / 3
    if t <= 11:
        # deux coulées épaisses (une eau lourde) qui font chacune un demi-tour autour du corps, gonflées de gouttes
        for k, (ph, R0, w) in enumerate(((0.5, 30, 6.0), (3.6, 28, 5.0))):
            n = 50
            pb, pf = [], []
            for i in range(n + 1):
                s_ = i / n
                th = ph + 2 * math.pi * 0.62 * s_ + t * 0.12
                y = y_hi + (y_lo - y_hi) * s_ + 4 * math.sin(th)
                if y > GY - 1:
                    continue
                R = R0 * (0.8 + 0.2 * s_)
                x = CX + R * math.cos(th)
                # effilée en haut, lourde en bas, des renflements (gouttes qui pendent)
                ww = (w * (0.3 + 0.7 * s_ ** 0.6) * (1 + 0.28 * math.sin(s_ * 17 + k * 2)) + 0.5) * (0.6 + 0.4 * fade)
                (pf if math.sin(th) > 0 else pb).append((x, y, ww))
            al = int(235 * fade) if t >= 10 else 235
            disc_paint(back, pb, [T[0], T[1], T[2], T[3], T[4]], al)
            disc_paint(front, pf, [T[0], T[1], T[2], T[3], T[4]], al)
    # un voile bleu très léger sur le corps (le froid qui pèse)
    if 3 <= t <= 10:
        F = np.clip(1.0 - ell_field(CX, 80, 26, 38), 0, 1) * (0.7 if t < 9 else 0.4)
        front.glow(F, [T[2], T[2], T[3], T[3]], alphas=(18, 30, 42, 54))
    # la flaque qui colle au sol
    if t >= 4:
        f = min(1.0, (t - 3) / 3) * (1.0 if t < 10 else 1 - (t - 9) / 3)
        pool(back, front, 26 + 6 * min(1.0, (t - 4) / 4), 5.5, [T[3], T[3], T[2], T[2]], fade=f)
        if t <= 10:
            ground_ring(back, front, 30, 5.5, 2.0, [T[2], T[3], T[4]], [(-170, -100), (-60, 20), (40, 150)],
                        alpha=int(200 * f))
    # gouttes lourdes
    for (gx, s) in ((46, 4), (84, 5), (58, 7), (76, 8)):
        age = t - s
        if 0 <= age < 3:
            y = 92 + 7 * age
            if y < GY - 1:
                front.put(gx, y, T[1], 230)
                front.put(gx, y + 1, T[2], 230)
                front.put(gx, y + 2, T[3], 220)
    return back, front


SLOW_ECLAT = {4: 10, 5: 16, 6: 20, 7: 20, 8: 16, 9: 10}
SLOW_TEINTE = SLOWB[3]


# ---------------------------------------------------------------- le catalogue
# nom : (fonction, durées, éclat {image: %}, teinte de l'éclat (None = ton pâle de l'élément), boucle, par élément ?)
EFFECTS = {
    'soin': (fx_soin, SOIN_MS, SOIN_ECLAT, None, False, True),
    'regeneration': (fx_regen, REGEN_MS, {}, None, True, True),
    'purification': (fx_purif, PURIF_MS, PURIF_ECLAT, None, False, True),
    'resurrection': (fx_resu, RESU_MS, RESU_ECLAT, None, False, True),
    'bouclier': (fx_bouclier, BOUC_MS, BOUC_ECLAT, None, False, True),
    'defense': (fx_defense, DEF_MS, DEF_ECLAT, None, False, True),
    'attaque': (fx_attaque, ATK_MS, ATK_ECLAT, ATK_TEINTE, False, True),
    'energie': (fx_energie, ENER_MS, ENER_ECLAT, None, False, True),
    'provocation': (lambda e, t: fx_provoc(t), PROV_MS, PROV_ECLAT, PROV_TEINTE, False, False),
    'affaiblissement': (lambda e, t: fx_affaib(t), AFF_MS, AFF_ECLAT, AFF_TEINTE, False, False),
    'ralentissement': (lambda e, t: fx_ralent(t), SLOW_MS, SLOW_ECLAT, SLOW_TEINTE, False, False),
}
# sur qui : équipe (chaque case occupée), lanceur (lui seul), ennemis
TARGET = {'provocation': 'lanceur', 'affaiblissement': 'ennemis', 'ralentissement': 'ennemis'}


def variants():
    """(effet, élément ou None, clé du fichier)"""
    out = []
    for name, (_, _, _, _, _, per) in EFFECTS.items():
        for e in (ELEMS if per else (None,)):
            out.append((name, e, f'{name}-{e}' if e else name))
    return out


def render(name, elem):
    """toutes les images d'un effet : [(dos RGBA, devant RGBA)]"""
    fn, ms = EFFECTS[name][0], EFFECTS[name][1]
    out = []
    for t in range(len(ms)):
        b, f = fn(elem, t)
        out.append((b.image(), f.image()))
    return out


# ---------------------------------------------------------------- aperçus (un héros dans sa case, avec l'effet)
def hero_frames(name):
    return [np.array(im) for im in hd.frames(name)]


# l'éclat des effets ennemis ASSOMBRIT (mélange vers la couleur) au lieu d'éclairer (ajout)
ECLAT_MODE = {'affaiblissement': 'melange', 'ralentissement': 'melange'}


def flash_hero(img, pct, col, mode='ajout'):
    """ce que le jeu fait à l'éclat : on AJOUTE au dessin du héros (pas à son contour) pct % de la couleur (comme une
    lumière : le héros s'éclaire dans la teinte de l'effet, sans devenir gris)"""
    out = img.copy()
    if not pct:
        return out
    m = (out[:, :, 3] > 0) & ~np.all(out[:, :, :3] == hd.INK, axis=2)
    c = out[m, :3].astype(int)
    if mode == 'melange':
        out[m, :3] = (c + (np.array(col) - c) * pct // 100).astype(np.uint8)
    else:
        out[m, :3] = np.clip(c + np.array(col) * pct // 100, 0, 255).astype(np.uint8)
    return out


def over(dst, src):
    """src posée sur dst (RGBA, même taille)"""
    a = src[:, :, 3:4].astype(np.float32) / 255
    A = dst[:, :, 3:4].astype(np.float32) / 255
    ao = a + A * (1 - a)
    rgb = (src[:, :, :3] * a + dst[:, :, :3] * A * (1 - a)) / np.maximum(ao, 1e-6)
    out = np.concatenate([rgb, ao * 255], 2)
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def eclat_color(name, elem):
    col = EFFECTS[name][3]
    return tuple(col) if col else RAMPS[elem][1]


def cell(hero_img, back, front, name, elem, t, mark=None, head_top=None):
    """une case : dos, héros (éclairci à l'éclat), devant, et la marque de provocation au-dessus de la tête"""
    pct = EFFECTS[name][2].get(t, 0)
    img = over(back, flash_hero(hero_img, pct, eclat_color(name, elem), ECLAT_MODE.get(name, 'ajout')))
    img = over(img, front)
    if mark is not None and head_top is not None:
        big = np.zeros((FH + MARK_H, FW, 4), np.uint8)
        big[MARK_H:] = img
        mx = FX - MARK_W // 2 + 4
        my = MARK_H + head_top - 1 - MARK_H
        big[my:my + MARK_H, mx:mx + MARK_W] = over(big[my:my + MARK_H, mx:mx + MARK_W], mark)
        return big
    return img


def meadow(w, h, feet_y):
    """un morceau du fond de combat (prairie) : les pieds posés sur le chemin de terre"""
    try:
        fond = Image.open(FOND).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        fy = 374 - feet_y
        base = fond.crop((0, fy, w, fy + h))
        if base.width < w or fy < 0:
            raise ValueError
        return base
    except Exception:
        return Image.new('RGBA', (w, h), (120, 170, 110, 255))


SHEET_HEROES = ('aldric', 'kael', 'minotaure')       # mince, moyen, massif


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune, pas de tramage (comme les animations des héros)"""
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


def write_all():
    os.makedirs(OUTFX, exist_ok=True)
    os.makedirs(os.path.join(OUTFX, 'apercu'), exist_ok=True)
    heroes = {n: hero_frames(n) for n in SHEET_HEROES}
    head_top = {n: int(np.nonzero(heroes[n][0][:, :, 3].any(1))[0].min()) for n in SHEET_HEROES}
    marks = [mark_frame(t) for t in range(len(PROV_MS))]
    index = {'taille': [FW, FH], 'pieds': [FX, GY], 'echelle_jeu': 1.22, 'effets': {}}
    rendered = {}
    for (name, elem, key) in variants():
        frames = render(name, elem)
        rendered[key] = frames
        ms = EFFECTS[name][1]
        n = len(frames)
        for side, idx in (('dos', 0), ('devant', 1)):
            strip = np.zeros((FH, FW * n, 4), np.uint8)
            for i, fr in enumerate(frames):
                strip[:, i * FW:(i + 1) * FW] = fr[idx]
            Image.fromarray(strip, 'RGBA').save(os.path.join(OUTFX, f'{key}-{side}.png'))
        meta = {
            'effet': name, 'element': ELEM_EN.get(elem) if elem else None, 'cible': TARGET.get(name, 'equipe'),
            'images': n, 'taille': [FW, FH], 'pieds': [FX, GY], 'durees_ms': ms, 'total_ms': sum(ms),
            'boucle': EFFECTS[name][4],
            'dos': f'{key}-dos.png', 'devant': f'{key}-devant.png',
            # éclat : à l'image i, le jeu mélange le dessin du héros à cette couleur (pourcentage)
            'eclat': {'couleur': '#%02x%02x%02x' % eclat_color(name, elem or 'vent'),
                      'mode': ECLAT_MODE.get(name, 'ajout'),
                      'par_image': {str(k): v for k, v in EFFECTS[name][2].items()}},
        }
        if name == 'provocation':
            meta['marque'] = {'fichier': 'provocation-marque.png', 'taille': [MARK_W, MARK_H],
                              'pose': 'le milieu du bas de la case juste au-dessus du haut du dessin du héros',
                              'images': n}
        json.dump(meta, open(os.path.join(OUTFX, f'{key}.json'), 'w'), ensure_ascii=False, indent=1)
        index['effets'][key] = meta
    strip = np.zeros((MARK_H, MARK_W * len(marks), 4), np.uint8)
    for i, m in enumerate(marks):
        strip[:, i * MARK_W:(i + 1) * MARK_W] = m
    Image.fromarray(strip, 'RGBA').save(os.path.join(OUTFX, 'provocation-marque.png'))
    json.dump(index, open(os.path.join(OUTFX, 'effets.json'), 'w'), ensure_ascii=False, indent=1)

    # ---- aperçus animés : chaque effet, ses éléments côte à côte, sur les trois héros (×2, sur la prairie)
    for name in EFFECTS:
        keys = [k for (n, e, k) in variants() if n == name]
        elems = [e for (n, e, k) in variants() if n == name]
        ms = EFFECTS[name][1]
        n = len(ms)
        top_pad = MARK_H if name == 'provocation' else 0
        ch = FH + top_pad
        bg = meadow(FW, ch, GY + top_pad)
        ims = []
        for t in range(n):
            canvas = Image.new('RGBA', (FW * len(SHEET_HEROES) * len(keys) + 6 * (len(keys) - 1), ch), (250, 250, 252, 255))
            for j, (key, elem) in enumerate(zip(keys, elems)):
                b, f = rendered[key][t]
                for i, hn in enumerate(SHEET_HEROES):
                    hi = heroes[hn][t % 8]
                    c = cell(hi, b, f, name, elem or 'vent', t, marks[t] if name == 'provocation' else None, head_top[hn])
                    im = bg.copy()
                    if c.shape[0] != ch:
                        cc = np.zeros((ch, FW, 4), np.uint8)
                        cc[ch - c.shape[0]:] = c
                        c = cc
                    im.alpha_composite(Image.fromarray(c, 'RGBA'))
                    canvas.paste(im, (j * (FW * len(SHEET_HEROES) + 6) + i * FW, 0))
            ims.append(canvas.resize((canvas.width * 2, canvas.height * 2), Image.NEAREST))
        save_gif(os.path.join(OUTFX, 'apercu', f'{name}.gif'), ims, ms)
        # toutes les images, ×3, numérotées (un rang par élément, sur le héros moyen)
        k = 3
        hn = 'kael'
        Wt = 8 + n * (FW * k + 4)
        Ht = 8 + len(keys) * (ch * k + 22)
        sh = Image.new('RGB', (Wt, Ht), (250, 250, 252))
        d = ImageDraw.Draw(sh)
        for j, (key, elem) in enumerate(zip(keys, elems)):
            y = 8 + j * (ch * k + 22)
            d.text((8, y), f'{key} : {n} images, {sum(ms)} ms', fill=(30, 20, 36))
            for t in range(n):
                b, f = rendered[key][t]
                c = cell(heroes[hn][t % 8], b, f, name, elem or 'vent', t, marks[t] if name == 'provocation' else None, head_top[hn])
                if c.shape[0] != ch:
                    cc = np.zeros((ch, FW, 4), np.uint8)
                    cc[ch - c.shape[0]:] = c
                    c = cc
                im = bg.copy()
                im.alpha_composite(Image.fromarray(c, 'RGBA'))
                X = 8 + t * (FW * k + 4)
                sh.paste(im.resize((FW * k, ch * k), Image.NEAREST), (X, y + 14))
                d.text((X + 2, y + 14 + 2), f'{t} ({ms[t]} ms)', fill=(255, 255, 255))
        sh.save(os.path.join(OUTFX, 'apercu', f'planche-{name}.png'))

    # ---- la grande planche : chaque effet (un rang) × éléments (groupes), au temps fort, sur les trois héros
    k = 2
    peak = {'soin': 6, 'regeneration': 3, 'purification': 4, 'resurrection': 6, 'bouclier': 6, 'defense': 5,
            'attaque': 5, 'energie': 5, 'provocation': 7, 'affaiblissement': 6, 'ralentissement': 7}
    cw, chh = FW * k, (FH + MARK_H) * k
    gw = cw * 3 + 10
    Wt = 120 + 4 * gw
    Ht = 30 + len(EFFECTS) * (chh + 18)
    sheet = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    for j, e in enumerate(ELEMS):
        d.text((120 + j * gw + 4, 8), f'{e}  ({", ".join(SHEET_HEROES)})', fill=(30, 20, 36))
    bg = meadow(FW, FH + MARK_H, GY + MARK_H)
    for r, name in enumerate(EFFECTS):
        y = 30 + r * (chh + 18)
        t = peak[name]
        d.text((6, y + chh // 2 - 10), name, fill=(30, 20, 36))
        d.text((6, y + chh // 2 + 4), f'image {t}', fill=(110, 100, 120))
        for j, e in enumerate(ELEMS):
            per = EFFECTS[name][5]
            if not per and j > 0:
                continue
            key = f'{name}-{e}' if per else name
            b, f = rendered[key][t]
            for i, hn in enumerate(SHEET_HEROES):
                c = cell(heroes[hn][t % 8], b, f, name, e, t, marks[t] if name == 'provocation' else None, head_top[hn])
                cc = np.zeros((FH + MARK_H, FW, 4), np.uint8)
                cc[FH + MARK_H - c.shape[0]:] = c
                im = bg.copy()
                im.alpha_composite(Image.fromarray(cc, 'RGBA'))
                sheet.paste(im.resize((cw, chh), Image.NEAREST), (120 + j * gw + i * cw, y))
    sheet.save(os.path.join(OUT, 'effets-equipe-planche.png'))
    return rendered


if __name__ == '__main__':
    only = sys.argv[1:]
    if only:
        # aperçu rapide d'un seul effet (pour travailler) : python3 build.py soin
        keep = {k: v for k, v in EFFECTS.items() if k in only}
        EFFECTS.clear()
        EFFECTS.update(keep)
    r = write_all()
    for key, fr in r.items():
        print(f'{key} : {len(fr)} images')
    print('écrit dans', OUTFX, 'et', os.path.join(OUT, 'effets-equipe-planche.png'))
