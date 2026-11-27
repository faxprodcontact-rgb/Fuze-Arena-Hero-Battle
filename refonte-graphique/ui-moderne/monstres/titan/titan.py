# Le TITAN DES RUINES (grand boss de terre, boss-terre) redessiné en VECTORIEL lisse, dans le style moderne de
# l'interface, comme les héros (modèle : heros/kael/, outils : heros/atelier.py, roche et mousse comme heros/garvin/).
#
#   python3 refonte-graphique/ui-moderne/monstres/titan/titan.py     # → titan.svg + art/vecto/boss-terre.webp (+ -160)
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/boss/titan.txt) : une montagne qui s'est levée. Corps de
# roche brute (gris olive, ombres violet nuit), posture de gorille : dos en bosse, appuyé sur ses deux poings ; la TÊTE
# est celle d'une statue de roi d'un temple oublié, en grès taillé plus clair (la zone forte), prise dans la roche ; un
# portique de pierres levées (deux montants, un linteau penché, moussu) sur le dos ; des cristaux de grenat poussent dans
# ses fêlures et ses articulations ; la mousse couvre tout ce qui regarde le ciel.
# Coordonnées = pixels du dessin pixel art (case de 256 × 240, sol en (128, 236)) : il se pose au même endroit.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; tourné vers la DROITE.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from atelier import Mat, sm, limb, ribbon, ellipse, rpoly, sides, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import fuse, P as PG, geom_shape, geom_shapes, crpath, taper, FigureM  # noqa: E402
from visage import placer as _placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'boss-terre'

# ---------- matières (tons du pixel art passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
ROCK = Mat('#d6cca2', '#a09878', '#716c66', '#4a4256', '#2b2338', glint='#f6eed2')
ROCKF = Mat('#a49c86', '#7a7270', '#56505e', '#3a3248', '#241c30')          # la roche du fond (bras et jambe lointains)
SAND = Mat('#fbefcc', '#e2cfa8', '#b9a387', '#856e74', '#503c4c', glint='#fffaea')   # grès taillé : la statue, le portique
MOSS = Mat('#dcea84', '#97bc46', '#5e9236', '#33623a', '#1a3a32')
GAR = Mat('#ffd6dc', '#ff7488', '#d6365a', '#8c1c4a', '#4e143a', glint='#ffffff')    # grenat
EYE = ('#fff0dc', '#ffb08a', '#ff5a3c', '#d82a2e', '#8c1626')
MOUTH = ('#7a2238', '#561630', '#3a0e26')                                     # l'intérieur de la gueule (rouge sombre)

GRD = 236.0                     # le sol (plante des pieds, bas des poings)
FEET = (128.0, 236.0)           # le point « sol » du pixel art
FRAME = (20.0, 14.0, 238.0, 224.0)   # x0, y0, largeur, hauteur de l'image (pixels du dessin)

# ---------- le squelette ----------
HIP = (150.0, 194.0)            # le haut du corps bascule autour des hanches (il se cabre)
NECK = (206.0, 150.0)           # la tête tourne autour de la nuque (sous la mâchoire)
NS, NE0, NW0 = (82.0, 104.0), (50.0, 146.0), (68.0, 194.0)        # bras proche : épaule, coude, poignet (repos)
FS, FE0, FW0 = (204.0, 148.0), (212.0, 170.0), (224.0, 198.0)     # bras lointain (l'épaule est cachée par la mâchoire)

# la face (ovale du visage, sans le crâne moussu ni l'oreille) et la place des traits : visage.py, commun à tous
FACE_BOX = (176.0, 78.0, 238.0, 150.0)
FACE_ARGS = dict(y_oeil=0.42, y_nez=0.6, y_bouche=0.78, l_oeil=0.19)
FACE_V = _placer(FACE_BOX, **FACE_ARGS)

REST = dict(breath=0.0, bx=0.0, by=0.0, pitch=0.0, head=(0.0, 0.0), tilt=0.0, gape=0.0, ff=(0.0, 0.0), fn=(0.0, 0.0),
            frot=0.0, nrot=0.0, glow=0.0, blink=0.0, sway=0.0)
_GL = [0.0]                     # l'embrasement en cours (cristaux, yeux, signes)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def MS(M, sh):
    return sh.map(lambda p: mapp(M, p))


def ang_of(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def ik(S, W, L1, L2, sign):
    """Le coude (ou le genou) : deux segments de longueurs L1, L2 de S à W ; sign choisit le côté du pli."""
    d = math.dist(S, W)
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    al = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + sign * al
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    if d > L1 + L2:
        W = (S[0] + (W[0] - S[0]) / d * (L1 + L2), S[1] + (W[1] - S[1]) / d * (L1 + L2))
    return E, W


def sign_for(S, E, W):
    c = (E[0] - S[0]) * (W[1] - S[1]) - (E[1] - S[1]) * (W[0] - S[0])
    return -1 if c > 0 else 1


NL = (math.dist(NS, NE0), math.dist(NE0, NW0))
FL = (math.dist(FS, FE0), math.dist(FE0, FW0))
NSG = -1 if ((NE0[0] - NS[0]) * (NW0[1] - NS[1]) - (NE0[1] - NS[1]) * (NW0[0] - NS[0])) > 0 else 1
FSG = -1 if ((FE0[0] - FS[0]) * (FW0[1] - FS[1]) - (FE0[1] - FS[1]) * (FW0[0] - FS[0])) > 0 else 1


# ---------- petits outils de dessin ----------

def rk(pts, r=2.6):
    """Un rocher : un polygone irrégulier aux coins arrondis (des faces planes, pas un coussin)."""
    return rpoly(pts, r)


def cribbon(pts, widths):
    left, right = sides(pts, widths)
    ring_ = [pts[0]] + left[1:-1] + [pts[-1]] + right[1:-1][::-1]
    return sm(ring_, sharp=tuple(range(len(ring_))), t=0.5)


def fissure(pts, w=0.8, mat=ROCK, k=1.0):
    """Une fêlure dans la pierre : un creux sombre et son arête éclairée au-dessus (aucun trait noir)."""
    n = len(pts)
    sh = cribbon(pts, [0.1] + [w] * (n - 2) + [0.1])
    hl = cribbon([(x + 0.4, y - 0.5) for x, y in pts], [0.05] + [w * 0.5] * (n - 2) + [0.05])
    return [(hl, mat.hi, 0.45 * k), (sh, mat.deep, 0.62 * k)]


def zig(a, b, n, amp, seed=0):
    L = math.dist(a, b) or 1
    nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    out = [a]
    for i in range(1, n):
        t = i / n
        s = (1 if (i + seed) % 2 else -1) * amp * (0.55 + 0.45 * ((i * 0.618 + seed * 0.37) % 1))
        out.append((a[0] + (b[0] - a[0]) * t + nx * s, a[1] + (b[1] - a[1]) * t + ny * s))
    out.append(b)
    return out


def face(pts, color, op, r=1.6):
    """Une face plane de rocher (bords arrondis), peinte dans le morceau."""
    return (rk(pts, r), color, op)


def grad_of(sh, stops):
    x0, y0, x1, y1 = sh.bbox()
    return (x1, y0, x0 + (x1 - x0) * 0.15, y1, stops)


ROCK_G = [(0, '#aaa182'), (0.45, '#77716a'), (1, '#463e52')]
ROCKF_G = [(0, '#7c7470'), (0.5, '#59525e'), (1, '#352d44')]
SAND_G = [(0, '#efe0bc'), (0.5, '#c4ae90'), (1, '#8a7478')]


def moss_cap(pts, k=1.0, drips=()):
    """Un coussin de mousse (bord bas en lobes) et ses mèches qui pendent (longueurs inégales, bouts arrondis)."""
    sh = sm(pts, t=0.85)
    x0, y0, x1, y1 = sh.bbox()
    out = [(sh.move(-0.5, 1.0), MOSS.deep, 0.5 * k),
           (sh, ('lin', x1, y0, x0, y1, [(0, MOSS.hi), (0.28, MOSS.light), (0.7, MOSS.base), (1, MOSS.shadow)]), k)]
    for (x, y, L, w) in drips:
        d = taper(crpath([(x, y - 1.0), (x - 0.3, y + L * 0.5), (x - 0.6, y + L)], 8), w, w * 0.55)
        out.append((d, MOSS.shadow, 0.95 * k))
        out.append((taper(crpath([(x + w * 0.12, y - 1.0), (x - 0.1, y + L * 0.45)], 5), w * 0.4, w * 0.2), MOSS.light, 0.6 * k))
    return out


# ---------- les cristaux de grenat ----------

def crystal(base, ang, L, w, tipk=0.3):
    """Un cristal de grenat : un prisme hexagonal pointu (vu de 3/4), planté par sa base ; ang = direction (degrés,
    0 = vers le haut, + = vers la droite). Renvoie la forme et ses faces (gauche sombre, droite claire, arête vive)."""
    a = math.radians(ang)
    u = (math.sin(a), -math.cos(a))           # le long du cristal
    v = (math.cos(a), math.sin(a))            # en travers (vers la droite du cristal)

    def P(s, t):
        return (base[0] + u[0] * s + v[0] * t, base[1] + u[1] * s + v[1] * t)
    h = w / 2
    sL = L * (1 - tipk)
    body = sm([P(-2, -h), P(sL, -h), P(L, -h * 0.12), P(L * 0.99, h * 0.05), P(sL * 0.97, h), P(-2, h)], sharp=(1, 2, 3, 4), t=0.4)
    ridge = 0.18 * h
    left = sm([P(-2, -h), P(sL, -h), P(L, -h * 0.12), P(sL * 1.0, -ridge * 0.6), P(-2, -ridge)], sharp=(0, 1, 2, 3, 4), t=0.3)
    right = sm([P(-2, ridge), P(sL * 0.98, ridge), P(L * 0.985, 0.0), P(sL * 0.97, h), P(-2, h)], sharp=(0, 1, 2, 3, 4), t=0.3)
    tipf = sm([P(sL, -h), P(L, -h * 0.12), P(L * 0.99, h * 0.05), P(sL * 0.97, h), P(sL * 0.98, ridge)], sharp=(0, 1, 2, 3, 4), t=0.3)
    glint = ribbon([P(sL * 0.15, ridge * 1.4), P(sL * 0.6, ridge * 1.6), P(sL * 0.95, ridge * 1.2)], [0.1, max(0.35, w * 0.08), 0.1])
    return body, left, right, tipf, glint


def crystal_part(fig, name, base, ang, L, w, cast=0.8, cast_on=None, dim=0.0):
    body, left, right, tipf, glint = crystal(base, ang, L, w)
    g = _GL[0]
    lit = GAR.light if g < 1.5 else GAR.hi
    det = [(left, GAR.shadow, 0.85 - 0.25 * dim), (right, lit, 0.75), (tipf, GAR.hi, 0.55 + 0.1 * g), (glint, GAR.glint, 0.7)]
    if dim:
        det.append((body, '#2a0f40', 0.35 * dim))
    x0, y0, x1, y1 = body.bbox()
    fig.part(name, body, GAR, grad=(x1, y0, x0, y1, [(0, lite_(GAR.light, 0.15 * g)), (0.5, GAR.base), (1, GAR.shadow)]),
             cel=0.6, rim=0.45, cast=cast, cast_on=cast_on, details=det)


def lite_(c, t):
    a = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (255 - x) * max(0, min(1, t))) for x in a)


def glyph(cx, cy, s, kind):
    """Un signe inventé (jamais une lettre) gravé et luisant : losange, chevrons, croc, œil."""
    if kind == 0:
        return [sm([(cx, cy - s), (cx + s * 0.7, cy), (cx, cy + s), (cx - s * 0.7, cy)], sharp=(0, 1, 2, 3), t=0.5)]
    if kind == 1:
        return [sm([(cx - s * 0.8, cy - s * 0.6), (cx, cy + s * 0.2), (cx + s * 0.8, cy - s * 0.6), (cx + s * 0.8, cy - s * 0.1),
                    (cx, cy + s * 0.75), (cx - s * 0.8, cy - s * 0.1)], sharp=(0, 1, 2, 3, 4, 5), t=0.5)]
    if kind == 2:
        return [sm([(cx - s * 0.5, cy - s), (cx + s * 0.55, cy - s * 0.2), (cx - s * 0.5, cy + s * 0.9), (cx - s * 0.1, cy - s * 0.1)],
                   sharp=(0, 1, 2, 3), t=0.5)]
    return [ellipse(cx, cy, s * 0.85, s * 0.5), ]


# ---------- les poings (posés sur les phalanges) ----------
# Un poing de gorille vu de 3/4 avant : une masse arrondie sous le poignet ; devant, les quatre doigts repliés, posés
# sur le sol l'un à côté de l'autre (de l'auriculaire, au fond à gauche, à l'index, devant à droite), séparés par des
# creux doux ; le pouce couché contre l'index. Repère local : origine au poignet, +y vers le sol.
FIST = [(-27.0, 10.0), (-19.0, 0.0), (-4.0, -4.0), (13.0, -2.0), (24.0, 7.0), (29.0, 22.0), (30.0, 34.0), (29.0, 42.0),
        (-30.0, 42.0), (-32.0, 30.0)]
FINGERS = [(-27.0, -15.5, 22.0), (-16.5, -3.0, 19.5), (-4.0, 9.5, 18.0), (8.5, 23.0, 17.0)]   # x0, x1, haut du doigt
THUMB = [(16.0, 12.0), (24.0, 8.0), (30.0, 12.0), (31.0, 20.0), (27.0, 26.0), (21.0, 25.0), (17.5, 19.0)]


def fist_parts(fig, name, W, ang, k, mat, grad, dark=0.0, front_cast=None):
    """Pose un poing au poignet W, tourné de `ang` degrés (0 = posé au sol), à l'échelle k."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def L(p):
        x, y = p[0] * k, p[1] * k
        return (W[0] + x * ca - y * sa, W[1] + x * sa + y * ca)

    def LR(pts, r):
        return rk([L(p) for p in pts], r * k)
    body = sm([L(p) for p in FIST], t=0.9)
    det = []
    # le dos de la main : un plan éclairé en haut à droite
    det.append((LR([(-14.0, 1.0), (4.0, -2.0), (16.0, 1.0), (24.0, 9.0), (12.0, 12.0), (-6.0, 11.0)], 3.0), mat.light, 0.55))
    det.append((LR([(-31.0, 18.0), (-25.0, 10.0), (-20.0, 19.0), (-24.0, 34.0), (-31.0, 34.0)], 2.0), mat.shadow, 0.45))
    # les doigts repliés : chacun un gros bout arrondi posé au sol, plus clair devant
    tones = [mat.shadow, mat.base, lite_(mat.base, 0.06), mat.light]
    for i, (x0, x1, top) in enumerate(FINGERS):
        fg = LR([(x0 + 0.4, top), (x1 - 0.4, top - 0.6), (x1 - 0.2, 41.6), (x0 + 0.2, 41.6)], [4.6, 4.6, 0.6, 0.6])
        det.append((LR([(x0 - 0.8, top + 1.2), (x0 + 1.6, top + 0.4), (x0 + 1.6, 41.8), (x0 - 0.8, 41.8)], 0.8), mat.deep, 0.55))
        det.append((fg, tones[i], 0.95))
        # la face éclairée de chaque doigt (haut-droit)
        det.append((LR([((x0 + x1) / 2 - 1.0, top + 1.4), (x1 - 1.6, top + 1.2), (x1 - 1.4, top + 9.0), ((x0 + x1) / 2 + 0.4, top + 8.0)], 1.6),
                    mat.hi, 0.35))
    # l'ombre au ras du sol
    det.append((LR([(-33.0, 38.6), (31.0, 38.6), (31.0, 42.4), (-33.0, 42.4)], 0.4), mat.deep, 0.45))
    if dark:
        det.append((body, '#2a0f40', 0.25 * dark))
    fig.part(name, body, mat, grad=grad_of(body, grad), cel=1.8, rim=0.8, cast=1.4, details=det, cast_on=front_cast)
    th = sm([L(p) for p in THUMB], t=0.9)
    fig.part(name + 't', th, mat, grad=grad_of(th, grad), cel=1.0, rim=0.6, cast=1.0, cast_on=[name],
             details=[(LR([(22.0, 9.6), (28.6, 12.6), (29.6, 18.0), (25.0, 15.0)], 1.4), mat.hi, 0.45)])
    return body


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    _GL[0] = P['glow']
    g = P['glow']
    br = P['breath']
    fig = FigureM(*frame, ow=ow)

    # ---- le squelette ----
    U = mchain(mT(P['bx'], P['by']), mR(P['pitch'], *HIP))                 # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -1.0 * br))                                         # ce qui monte avec le souffle
    BODY = mchain(U, mS(1, 1 + 0.008 * br, 150, 196))
    HEAD = mchain(UC, mT(P['head'][0], P['head'][1] - 0.4 * br), mR(P['tilt'], *NECK))
    lift = -P['by'] + P['pitch'] * 0.6
    LEGN = mchain(mS(1, 1 + lift / 50.0, 0, GRD), mT(0, 0))
    LEGF = mchain(mS(1, 1 + lift / 52.0, 0, GRD))

    if fx:
        for item in fx:
            if isinstance(item, tuple):
                fig.fx_back.append(item[0])
                fig.fx_front.append(item[1])

    # lueur douce des cristaux quand il se charge (dégradé, aucun flou)
    if g > 0.6:
        c = mapp(UC, (118, 60))
        fig.glow(c[0], c[1], 70, 46, '#ff4a6a', min(0.32, 0.07 * g))

    # ================================================================ derrière : cristaux du dos, bras et jambe lointains
    BACK_CR = [('cr1', (68.0, 64.0), -26, 34.0, 10.5), ('cr2', (60.0, 70.0), -44, 22.0, 8.0), ('cr3', (86.0, 58.0), -8, 24.0, 9.0),
               ('cr4', (151.0, 56.0), 18, 20.0, 8.5), ('cr5', (163.0, 62.0), 34, 12.0, 6.0)]
    for nm, b, a, L, w in BACK_CR:
        crystal_part(fig, nm, mapp(UC, b), a + P['pitch'], L, w, cast=0)

    # ---- le bras lointain (sort de derrière la mâchoire, plus sombre) ----
    S = mapp(UC, FS)
    Wt = (FW0[0] + P['ff'][0], FW0[1] + P['ff'][1])
    E, Wf = ik(S, Wt, FL[0] * 1.02, FL[1] * 1.02, FSG)
    farm = fuse([limb([S, lerp(S, E, 0.5), E], [30.0, 31.0, 30.0]), limb([E, lerp(E, Wf, 0.5), Wf], [30.0, 33.0, 30.0])], 1.5, 70)[0]
    fdet = [face([lerp(E, Wf, 0.1), (Wf[0] + 13, Wf[1] - 6), (Wf[0] + 8, Wf[1] - 2), (E[0] + 7, E[1] + 4)], ROCKF.light, 0.5)]
    fdet += fissure(zig((Wf[0] + 2, Wf[1] - 24), (Wf[0] - 4, Wf[1] - 8), 3, 1.2, 1), 0.7, ROCKF)
    fig.part('farm', farm, ROCKF, grad=grad_of(farm, ROCKF_G), cel=1.8, rim=0.7, cast=0, details=fdet)
    crystal_part(fig, 'crf', (Wf[0] + 12.0, Wf[1] - 34.0), 62, 15.0, 7.0, cast=0.6, cast_on=['farm'], dim=0.2)
    fa = (ang_of(E, Wf) - ang_of(FE0, FW0)) * 0.4 + P['frot']
    fist_parts(fig, 'ffist', Wf, fa, 0.72, ROCKF, ROCKF_G, dark=0.3)

    # ---- la jambe lointaine (à moitié cachée, plus sombre) ----
    fleg = limb([(178.0, 178.0), (177.0, 200.0), (178.0, 220.0)], [32.0, 30.0, 28.0])
    fig.part('fleg', fleg, ROCKF, grad=grad_of(fleg, ROCKF_G), cel=1.8, rim=0.6, cast=0,
             details=[face([(180.0, 196.0), (192.0, 194.0), (193.0, 208.0), (184.0, 209.0)], ROCKF.light, 0.45)])
    ffoot = rk([(158.0, 236.0), (158.5, 226.0), (163.0, 218.0), (176.0, 214.0), (190.0, 215.0), (198.0, 222.0), (200.0, 236.0)], [0.6, 4, 5, 5, 5, 4, 0.6])
    fig.part('ffoot', ffoot, ROCKF, grad=grad_of(ffoot, ROCKF_G), cel=1.6, rim=0.7, cast=1.0,
             details=toes([(183.0, 192.0), (191.0, 199.5)], 222.0, ROCKF) + [
                 face([(164.0, 220.0), (176.0, 216.0), (186.0, 217.0), (180.0, 222.0), (168.0, 223.0)], ROCKF.light, 0.45)])
    fig.pose(['fleg', 'ffoot'], LEGF)
    fig.pose(['fleg'], mchain(LEGF))

    # ---- la jambe proche : la cuisse sort de sous le ventre, genou de rocher, pied large aux trois orteils ----
    nleg = fuse([limb([(124.0, 176.0), (120.0, 198.0), (122.0, 220.0)], [44.0, 42.0, 38.0]),
                 rk([(104.0, 196.0), (114.0, 190.0), (130.0, 192.0), (134.0, 206.0), (124.0, 214.0), (108.0, 212.0)], 6.0)], 1.0, 70)[0]
    fig.part('nleg', nleg, ROCK, grad=grad_of(nleg, ROCK_G), cel=2.0, rim=0.7, cast=1.0, cast_on=['fleg', 'ffoot'],
             details=[face([(112.0, 193.0), (126.0, 191.0), (133.0, 199.0), (128.0, 206.0), (116.0, 204.0)], ROCK.light, 0.6),
                      face([(103.0, 204.0), (110.0, 200.0), (112.0, 214.0), (104.0, 216.0)], ROCK.shadow, 0.5)]
             + fissure(zig((130.0, 208.0), (136.0, 222.0), 3, 1.0, 2), 0.7))
    nfoot = rk([(100.0, 236.0), (100.0, 226.0), (105.0, 216.0), (118.0, 212.0), (134.0, 212.0), (146.0, 216.0), (153.0, 224.0), (155.0, 236.0)],
               [0.6, 4, 6, 6, 6, 5, 4, 0.6])
    fig.part('nfoot', nfoot, ROCK, grad=grad_of(nfoot, ROCK_G), cel=1.8, rim=0.8, cast=1.2,
             details=toes([(128.0, 138.0), (137.5, 146.5), (146.0, 155.0)], 222.0, ROCK) + [
                 face([(106.0, 218.0), (118.0, 213.5), (134.0, 213.5), (128.0, 219.0), (112.0, 221.0)], ROCK.light, 0.5),
                 (moss_cap([(103.0, 222.0), (106.0, 216.5), (113.0, 213.6), (118.0, 214.0), (113.0, 217.0), (107.0, 222.0)])[1][0], MOSS.base, 0.0)])
    fig.pose(['nleg', 'nfoot'], LEGN)

    # ================================================================ le corps : la montagne (bosse, poitrine, ventre)
    body = sm([(56.0, 128.0), (52.0, 104.0), (55.0, 84.0), (66.0, 70.0), (84.0, 60.0), (106.0, 54.0), (130.0, 51.0), (152.0, 53.0),
               (170.0, 59.0), (184.0, 66.0), (196.0, 74.0), (214.0, 96.0), (232.0, 132.0), (238.0, 158.0), (236.0, 180.0), (226.0, 192.0),
               (206.0, 197.0), (186.0, 198.0), (164.0, 196.0), (144.0, 192.0), (122.0, 188.0), (104.0, 182.0), (98.0, 168.0),
               (98.0, 150.0), (90.0, 138.0), (72.0, 134.0)], t=0.9)
    bdet = []
    # les grandes dalles de roche (lisibles dans la lumière, perdues dans l'ombre)
    bdet += [face([(98.0, 58.0), (128.0, 53.0), (150.0, 56.0), (146.0, 74.0), (120.0, 80.0), (100.0, 74.0)], ROCK.light, 0.55, 4.0),
             face([(152.0, 58.0), (170.0, 62.0), (186.0, 72.0), (178.0, 88.0), (160.0, 86.0), (150.0, 76.0)], ROCK.light, 0.5, 4.0),
             face([(122.0, 84.0), (148.0, 80.0), (162.0, 92.0), (154.0, 110.0), (130.0, 112.0), (120.0, 100.0)], ROCK.light, 0.28, 4.0),
             face([(66.0, 76.0), (90.0, 64.0), (98.0, 78.0), (90.0, 92.0), (70.0, 92.0)], ROCK.light, 0.32, 4.0)]
    bdet += fissure([(100.0, 74.0), (120.0, 80.0), (146.0, 74.0), (150.0, 56.0)], 0.9)
    bdet += fissure([(150.0, 76.0), (160.0, 86.0), (178.0, 88.0)], 0.9)
    bdet += fissure([(120.0, 80.0), (122.0, 96.0), (130.0, 112.0)], 0.8, k=0.8)
    bdet += fissure([(160.0, 86.0), (162.0, 94.0), (154.0, 110.0)], 0.8, k=0.8)
    bdet += fissure([(98.0, 78.0), (106.0, 92.0), (104.0, 108.0)], 0.7, k=0.6)
    # la poitrine dans l'ombre, sous la tête (l'avant du corps regarde le sol)
    bdet += [(sm([(96.0, 128.0), (124.0, 118.0), (160.0, 122.0), (186.0, 140.0), (200.0, 170.0), (196.0, 198.0), (100.0, 198.0), (94.0, 160.0)], t=0.9),
              ROCK.shadow, 0.55),
             (sm([(100.0, 150.0), (130.0, 140.0), (164.0, 146.0), (184.0, 164.0), (186.0, 198.0), (104.0, 196.0)], t=0.9), ROCK.deep, 0.3)]
    bdet += fissure([(128.0, 130.0), (134.0, 146.0), (130.0, 164.0), (136.0, 182.0)], 0.7, k=0.5)
    # le signe du clan sur le ventre : un losange de grenat entre deux crochets, gravé et luisant
    sg = (156.0, 174.0)
    hot = min(1.0, 0.45 + 0.18 * g)
    bdet += [(ellipse(sg[0], sg[1], 9.0 + g, 7.0 + g), ('rad', sg[0], sg[1], 9.0 + g, 7.0 + g, [(0, '#ff6a80', 0.5 * hot), (1, '#ff6a80', 0)]), 1)]
    for s in (-1, 1):
        hook = taper(crpath([(sg[0] + s * 4.5, sg[1] - 5.2), (sg[0] + s * 7.2, sg[1] - 1.0), (sg[0] + s * 6.6, sg[1] + 3.6), (sg[0] + s * 4.0, sg[1] + 5.4)], 10), 1.3, 0.6)
        bdet += [(hook.move(0.3, 0.4), ROCK.deep, 0.6), (hook, GAR.base, 0.9)]
    dia = glyph(sg[0], sg[1], 4.2, 0)[0]
    bdet += [(dia.move(0.3, 0.5), ROCK.deep, 0.6), (dia, ('lin', sg[0] + 3, sg[1] - 4, sg[0] - 3, sg[1] + 4, [(0, GAR.hi), (0.5, GAR.light), (1, GAR.base)]), 1)]
    fig.part('body', body, ROCK, grad=grad_of(body, ROCK_G), cel=2.6, rim=0.9, cast=1.6, cast_on=['nleg', 'fleg', 'farm', 'ffoot'],
             details=bdet, occl=(ROCK.deep, 0.25, 4.0))
    fig.pose(['body'], BODY)

    # ---- le portique de pierres levées : deux montants, un linteau penché, moussu ----
    pl = rk([(100.0, 60.0), (100.5, 36.0), (111.0, 35.0), (111.0, 60.0)], 1.6)
    pr = rk([(128.0, 58.0), (128.5, 38.0), (139.0, 37.5), (139.5, 58.0)], 1.6)
    lin_ = rk([(94.0, 34.0), (95.0, 26.0), (147.0, 28.5), (146.0, 36.5)], 1.8)
    for nm, sh in (('pill', pl), ('pilr', pr)):
        x0, y0, x1, y1 = sh.bbox()
        fig.part(nm, sh, SAND, grad=(x1, y0, x0, y1, [(0, SAND.light), (0.5, SAND.base), (1, SAND.shadow)]), cel=1.4, rim=0.7, cast=1.0,
                 cast_on=['body'], details=[face([(x1 - 4.0, y0 + 1.0), (x1 - 0.4, y0 + 1.0), (x1 - 0.4, y1 - 2.0), (x1 - 4.4, y1 - 2.0)], SAND.hi, 0.35, 0.8)]
                 + fissure([(x0 + 3.0, y0 + 8.0), (x0 + 5.0, y0 + 12.0), (x0 + 4.0, y0 + 16.0)], 0.6, SAND, 0.7))
    ldet = [face([(96.0, 27.0), (146.0, 29.5), (145.5, 31.5), (96.0, 29.2)], SAND.hi, 0.5, 0.6)]
    ldet += fissure([(120.0, 28.0), (121.5, 31.5), (120.0, 35.4)], 0.6, SAND, 0.8)
    ldet += [(g_, SAND.deep, 0.0) for g_ in []]
    fig.part('lintel', lin_, SAND, grad=(147.0, 26.0, 94.0, 37.0, [(0, SAND.light), (0.6, SAND.base), (1, SAND.shadow)]), cel=1.2, rim=0.7,
             cast=1.2, cast_on=['pill', 'pilr', 'body'], details=ldet)
    # la mousse du linteau (une seule nappe sur le dessus, deux mèches qui pendent)
    lm = sm([(94.0, 28.0), (96.0, 23.4), (104.0, 21.6), (114.0, 22.8), (124.0, 21.4), (136.0, 23.0), (146.0, 24.6), (148.6, 28.4),
             (144.0, 30.2), (136.0, 29.0), (126.0, 30.4), (114.0, 29.0), (104.0, 30.4), (97.0, 30.2)], t=0.85)
    fig.part('lmoss', lm, MOSS, grad=(148.0, 21.0, 96.0, 31.0, [(0, MOSS.hi), (0.3, MOSS.light), (0.75, MOSS.base), (1, MOSS.shadow)]),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['lintel'],
             details=drips_of([(103.0, 29.6, 5.0, 2.0), (131.0, 29.0, 3.2, 1.8)]))
    fig.pose(['pill', 'pilr', 'lintel', 'lmoss'], mchain(UC, mR(P['sway'] * 0.4, 120, 58)))

    # ---- la nappe de mousse du dos (une seule, de la bosse au crâne : elle couvre le pied des montants) ----
    bm = sm([(52.0, 96.0), (53.0, 82.0), (60.0, 71.0), (72.0, 63.0), (88.0, 56.0), (106.0, 51.6), (124.0, 49.2), (142.0, 49.6),
             (160.0, 54.0), (176.0, 61.0), (188.0, 68.0), (182.0, 72.0), (170.0, 67.0), (156.0, 62.4), (146.0, 61.2), (138.0, 63.0),
             (126.0, 60.6), (114.0, 62.6), (100.0, 63.4), (88.0, 66.6), (76.0, 72.6), (66.0, 80.0), (60.0, 90.0)], t=0.85)
    fig.part('bmoss', bm, MOSS, grad=(186.0, 48.0, 56.0, 96.0, [(0, MOSS.hi), (0.3, MOSS.light), (0.7, MOSS.base), (1, MOSS.shadow)]),
             cel=1.4, rim=0.7, cast=1.6, cast_on=['body', 'pill', 'pilr'],
             details=drips_of([(64.0, 84.0, 9.0, 2.6), (79.0, 70.0, 5.0, 2.2), (118.0, 61.6, 6.4, 2.4), (150.0, 61.6, 4.0, 2.0),
                               (172.0, 66.0, 7.4, 2.4)]))
    fig.pose(['bmoss'], UC)

    # ================================================================ le col de rocher sous la mâchoire
    col = sm([(170.0, 142.0), (190.0, 136.0), (222.0, 138.0), (242.0, 148.0), (246.0, 164.0), (242.0, 182.0), (228.0, 190.0),
              (204.0, 190.0), (184.0, 182.0), (172.0, 166.0)], t=0.9)
    cdet = [face([(214.0, 146.0), (240.0, 150.0), (244.0, 164.0), (236.0, 168.0), (222.0, 160.0)], ROCK.light, 0.55, 3.0),
            face([(176.0, 164.0), (192.0, 170.0), (210.0, 186.0), (188.0, 184.0), (176.0, 174.0)], ROCK.deep, 0.35, 3.0)]
    cdet += fissure([(222.0, 160.0), (218.0, 172.0), (224.0, 186.0)], 0.8)
    cdet += fissure([(196.0, 150.0), (200.0, 164.0), (196.0, 176.0)], 0.7, k=0.7)
    fig.part('col', col, ROCK, grad=grad_of(col, [(0, '#a8a084'), (0.5, '#6e6866'), (1, '#433b52')]), cel=2.0, rim=0.8, cast=1.6,
             cast_on=['body', 'farm'], details=cdet)
    fig.pose(['col'], UC)

    # ================================================================ la tête de statue (la zone forte)
    head_parts(fig, P, HEAD, UC)

    # ================================================================ le bras proche (devant le corps)
    near_arm(fig, P, UC)
    return fig


def toes(xs, top, mat):
    """Les orteils d'un pied posé à plat : des bouts arrondis posés au sol, séparés par des creux doux (devant)."""
    out = []
    for i, (x0, x1) in enumerate(xs):
        out.append((rk([(x0 - 0.6, top + 1.0), (x0 + 1.0, top + 0.6), (x0 + 1.0, 236.4), (x0 - 0.6, 236.4)], 0.6), mat.deep, 0.55))
        out.append((rk([(x0 + 0.5, top), (x1 - 0.5, top - 0.4), (x1, 236.0), (x0 + 0.2, 236.0)], [4.0, 4.0, 0.4, 0.4]),
                    mat.light if i == len(xs) - 1 else mat.base, 0.8))
        out.append((rk([((x0 + x1) / 2, top + 1.2), (x1 - 1.0, top + 1.0), (x1 - 0.8, top + 6.5), ((x0 + x1) / 2 + 0.8, top + 6.0)], 1.2), mat.hi, 0.3))
    out.append((rk([(xs[0][0] - 30, 233.0), (xs[-1][1] + 2, 233.0), (xs[-1][1] + 2, 236.6), (xs[0][0] - 30, 236.6)], 0.3), mat.deep, 0.4))
    return out


def drips_of(drips):
    out = []
    for (x, y, L, w) in drips:
        d = taper(crpath([(x, y - 2.0), (x - 0.2, y + L * 0.5), (x - 0.5, y + L)], 8), w, w * 0.62)
        out.append((d, MOSS.shadow, 0.95))
        out.append((taper(crpath([(x + w * 0.15, y - 1.5), (x, y + L * 0.5)], 5), w * 0.38, w * 0.2), MOSS.base, 0.8))
    return out


# ---------------------------------------------------------------- la tête

def head_parts(fig, P, HEAD, UC):
    V = FACE_V
    g = P['glow']
    gape = 1.0 + P['gape']
    names = []

    # ---- l'oreille sculptée et la tête (une seule forme : l'oreille est soudée au crâne) ----
    skull = sm([(172.0, 96.0), (176.0, 82.0), (186.0, 74.0), (202.0, 70.0), (220.0, 72.0), (232.0, 78.0), (238.0, 88.0),
                (239.0, 102.0), (238.0, 116.0), (237.5, 128.0), (236.0, 140.0), (230.0, 148.0), (220.0, 152.6), (206.0, 153.4),
                (192.0, 150.0), (182.0, 142.0), (175.0, 128.0), (171.5, 112.0)], t=0.9)
    ox, oy = V['oreille']
    ear = sm([(ox + 3.0, oy - 9.0), (ox - 3.0, oy - 10.0), (ox - 7.0, oy - 5.0), (ox - 7.6, oy + 3.0), (ox - 4.0, oy + 10.0), (ox + 2.0, oy + 11.0),
              (ox + 4.0, oy + 4.0)], t=0.9)
    head, _ = fuse([skull, ear], 1.6, 80)
    V_ = V
    hdet = []
    # les plans de la face : le front éclairé, la joue proche ronde (demi-teinte), le côté du fond plus clair
    hdet += [(sm([(190.0, 78.0), (214.0, 74.0), (232.0, 80.0), (237.0, 92.0), (226.0, 96.0), (204.0, 94.0), (188.0, 90.0)], t=0.9), SAND.light, 0.55)]
    hdet += [(sm([(222.0, 104.0), (236.0, 100.0), (238.0, 120.0), (236.0, 138.0), (228.0, 132.0), (224.0, 118.0)], t=0.9), SAND.hi, 0.28)]
    hdet += [(sm([(174.0, 100.0), (186.0, 104.0), (190.0, 122.0), (196.0, 140.0), (204.0, 150.0), (190.0, 150.0), (178.0, 138.0), (172.0, 116.0)], t=0.9),
              SAND.shadow, 0.5)]
    # le bandeau sculpté sur le front (un morceau d'ellipse autour de la tête), serti d'un grenat sur la médiane
    yb = 85.0
    band_top = [(173.0, yb - 1.0), (190.0, yb - 4.4), (V['mediane'](yb), yb - 5.6), (234.0, yb - 5.0), (240.0, yb - 3.6)]
    band_bot = [(240.0, yb + 3.0), (234.0, yb + 2.2), (V['mediane'](yb), yb + 2.6), (190.0, yb + 3.8), (173.0, yb + 6.8)]
    band = sm(crpath(band_top, 14) + crpath(band_bot, 14), sharp=(0, 14, 15, 29), t=0.8)
    hdet += [(band.move(-0.4, 1.0), SAND.deep, 0.45), (band, ('lin', 238.0, 78.0, 176.0, 92.0, [(0, SAND.hi), (0.5, SAND.light), (1, SAND.shadow)]), 1)]
    hdet += [(sm(crpath(band_top, 14) + crpath([(240.0, yb - 2.2), (234.0, yb - 3.4), (V['mediane'](yb), yb - 3.6), (190.0, yb - 2.6), (173.0, yb + 0.6)], 14),
                 sharp=(0, 14, 15, 29), t=0.8), SAND.hi, 0.6)]
    gx = V['mediane'](yb)
    hdet += [(ellipse(gx, yb - 1.4, 5.2 + 0.6 * g, 4.2 + 0.6 * g), ('rad', gx, yb - 1.4, 5.2 + 0.6 * g, 4.2 + 0.6 * g, [(0, '#ff7088', 0.5 + 0.1 * g), (1, '#ff7088', 0)]), 1)]
    gem = sm([(gx, yb - 5.0), (gx + 2.6, yb - 1.4), (gx, yb + 2.2), (gx - 2.4, yb - 1.4)], sharp=(0, 1, 2, 3), t=0.5)
    hdet += [(gem.move(-0.3, 0.6), SAND.deep, 0.6), (gem, ('lin', gx + 2, yb - 5, gx - 2, yb + 2, [(0, GAR.hi), (0.45, GAR.light), (1, GAR.shadow)]), 1),
             (ellipse(gx + 0.7, yb - 2.6, 0.8, 0.6), '#ffffff', 0.85)]
    # signes du bandeau (inventés) de part et d'autre du grenat
    for (x, k_) in ((198.0, 1), (230.0, 2)):
        y = yb - 0.6 + (0.0 if x > 210 else 0.2)
        for gl in glyph(x, y, 2.0, k_):
            hdet += [(gl, GAR.base, 0.55 + 0.1 * g)]

    # ---- les orbites (creux sous l'arcade froncée), les yeux de braise ----
    ep, ef = V['oeil_proche'], V['oeil_fond']
    for (ex, ey, ew), near in ((ep, True), (ef, False)):
        hw = ew / 2
        orb = sm([(ex - hw - 1.2, ey - 1.0), (ex - hw * 0.3, ey - 4.4), (ex + hw + 1.0, ey - 3.0), (ex + hw + 0.6, ey + 2.4),
                  (ex, ey + 4.0), (ex - hw - 0.6, ey + 2.6)], t=0.9)
        hdet += [(orb, SAND.deep, 0.85), (orb.move(0.8, 0.8), MOUTH[2], 0.35)]
    eyes = []
    for (ex, ey, ew), near in ((ep, True), (ef, False)):
        hw = ew / 2 * 0.78
        eh = 2.3 * (1 - P['blink'])
        if P['blink'] < 0.9:
            # l'œil : une braise en amande (coin intérieur plus bas, côté du nez), regard dur sous l'arcade
            if near:
                pts = [(ex - hw, ey - 0.2), (ex - hw * 0.2, ey - eh * 0.9), (ex + hw, ey - eh * 0.5), (ex + hw * 0.6, ey + eh * 0.55), (ex - hw * 0.4, ey + eh * 0.6)]
            else:
                pts = [(ex - hw, ey - eh * 0.5), (ex + hw * 0.2, ey - eh * 0.9), (ex + hw, ey - 0.2), (ex + hw * 0.4, ey + eh * 0.6), (ex - hw * 0.6, ey + eh * 0.55)]
            eye = sm(pts, sharp=(0, 2), t=0.8)
            r_ = 7.0 + 1.2 * g
            eyes += [(ellipse(ex, ey, r_, r_ * 0.75), ('rad', ex, ey, r_, r_ * 0.75, [(0, EYE[2], 0.55 + 0.1 * g), (1, EYE[3], 0)]), 1),
                     (eye, ('rad', ex + 0.6, ey - 0.4, hw * 1.1, hw * 1.1, [(0, EYE[0]), (0.35, EYE[1]), (0.75, EYE[2]), (1, EYE[3])]), 1),
                     (ellipse(ex + hw * 0.15, ey - 0.3, 0.9, 0.7), '#ffffff', 0.9)]
        else:
            eyes += [(ribbon([(ex - hw, ey), (ex, ey + 0.6), (ex + hw, ey)], [0.1, 0.8, 0.1]), SAND.deep, 0.8)]
    hdet += eyes
    # l'arcade lourde, froncée en V vers le nez (le sourcil de la statue) : un bourrelet de pierre au-dessus des yeux
    nx_, ny_ = V['nez']
    m_y = ep[1] - 4.6
    brow = sm([(ep[0] - ep[2] / 2 - 3.6, m_y - 3.2), (ep[0] - 1.0, m_y - 4.4), (V['mediane'](m_y) - 0.6, m_y + 1.6), (ef[0] + 1.0, m_y - 3.6),
               (ef[0] + ef[2] / 2 + 2.6, m_y - 3.0), (ef[0] + ef[2] / 2 + 2.2, m_y - 0.6), (ef[0] + 0.6, m_y - 0.6),
               (V['mediane'](m_y) - 0.4, m_y + 4.0), (ep[0] - 1.0, m_y - 0.8), (ep[0] - ep[2] / 2 - 3.6, m_y - 0.2)], sharp=(2, 7), t=0.8)
    hdet += [(brow.move(-0.4, 1.4), SAND.deep, 0.55), (brow, ('lin', ef[0] + 6, m_y - 4, ep[0] - 6, m_y + 2, [(0, SAND.hi), (0.5, SAND.light), (1, SAND.base)]), 1)]
    # le nez : large et plat, SUR la médiane entre les deux yeux (racine entre les arcades, base au-dessus de la bouche)
    mx = V['mediane']
    nose = sm([(mx(m_y + 3.0) - 1.6, m_y + 3.4), (mx(m_y + 3.0) + 1.8, m_y + 3.2), (nx_ + 3.6, ny_ - 3.0), (nx_ + 5.0, ny_ + 0.4),
               (nx_ + 2.6, ny_ + 2.0), (nx_, ny_ + 1.2), (nx_ - 2.8, ny_ + 2.0), (nx_ - 5.4, ny_ + 0.4), (nx_ - 4.0, ny_ - 3.0)], t=0.85)
    hdet += [(nose.move(-0.8, 1.2), SAND.shadow, 0.6),
             (nose, ('lin', nx_ + 5, m_y, nx_ - 5, ny_ + 2, [(0, SAND.hi), (0.45, SAND.light), (1, SAND.base)]), 1),
             (ellipse(nx_ - 2.6, ny_ + 0.6, 1.4, 0.75), SAND.deep, 0.75), (ellipse(nx_ + 2.5, ny_ + 0.6, 1.1, 0.65), SAND.deep, 0.6),
             (ribbon([(mx(m_y + 4) + 0.6, m_y + 5.0), (nx_ + 1.8, ny_ - 5.0), (nx_ + 3.0, ny_ - 1.6)], [0.1, 0.9, 0.1]), SAND.glint, 0.5)]
    # la gueule ouverte : lèvres de pierre, rangées de dents carrées, l'intérieur rouge sombre (jamais noir)
    bx_, by_, bw = V['bouche']
    mw = bw * 1.55
    top = by_ - 3.2 * gape
    bot = by_ + 4.6 * gape
    hdet += mouth(bx_, top, bot, mw, gape)
    # la fêlure du crâne à la mâchoire (côté proche, derrière l'œil), des cristaux poussent dedans à la tempe
    hdet += fissure([(188.0, 72.0), (186.0, 84.0), (182.0, 94.0), (184.0, 106.0), (180.0, 118.0), (182.0, 132.0), (188.0, 146.0)], 1.0, SAND)
    hdet += fissure([(222.0, 140.0), (226.0, 146.0), (224.0, 152.0)], 0.6, SAND, 0.7)
    fig.part('head', head, SAND, grad=grad_of(head, SAND_G), cel=2.2, rim=0.9, cast=1.8, cast_on=['col', 'body', 'farm'],
             details=hdet, occl=(SAND.deep, 0.2, 3.0))
    names.append('head')

    # ---- les défenses de grenat : elles montent de la mâchoire du bas, aux coins de la gueule (la lointaine plus sombre)
    t1 = (bx_ - mw / 2 + 1.6, bot - 0.6)
    t2 = (bx_ + mw / 2 - 1.2, bot - 0.6)
    crystal_part(fig, 'tusk2', t2, 6, 13.0 + 2 * P['gape'], 4.4, cast=0.6, cast_on=['head'], dim=0.35)
    crystal_part(fig, 'tusk1', t1, -6, 17.0 + 2 * P['gape'], 5.2, cast=0.8, cast_on=['head'])
    names += ['tusk1', 'tusk2']

    # ---- la bosse enveloppe la nuque : une coque de roche brute, le grès se fend contre elle ----
    nape = sm([(170.0, 128.0), (166.0, 104.0), (168.0, 86.0), (176.0, 72.0), (190.0, 66.0), (196.0, 70.0), (190.0, 78.0),
               (184.0, 86.0), (180.0, 100.0), (181.0, 112.0), (178.0, 122.0)], t=0.85)
    fig.part('nape', nape, ROCK, grad=grad_of(nape, ROCK_G), cel=1.6, rim=0.7, cast=1.4, cast_on=['head'],
             details=[face([(178.0, 72.0), (190.0, 67.0), (192.0, 72.0), (184.0, 80.0), (176.0, 82.0)], ROCK.light, 0.55, 2.0)]
             + fissure([(172.0, 96.0), (176.0, 106.0), (173.0, 116.0)], 0.7))
    names.append('nape')
    # ---- un seul coussin de mousse passe de la bosse au crâne ----
    hm = sm([(168.0, 80.0), (172.0, 70.0), (182.0, 64.6), (196.0, 63.6), (212.0, 65.0), (226.0, 68.6), (234.0, 74.0), (237.0, 80.0),
             (231.0, 80.6), (224.0, 77.0), (214.0, 76.4), (202.0, 76.0), (192.0, 78.0), (182.0, 82.0), (174.0, 88.0)], t=0.85)
    fig.part('hmoss', hm, MOSS, grad=(236.0, 62.0, 170.0, 88.0, [(0, MOSS.hi), (0.3, MOSS.light), (0.72, MOSS.base), (1, MOSS.shadow)]),
             cel=1.2, rim=0.7, cast=1.3, cast_on=['head', 'nape'],
             details=drips_of([(176.0, 84.0, 6.0, 2.2), (196.0, 76.4, 3.6, 1.8), (229.0, 78.4, 4.4, 1.8)]))
    names.append('hmoss')
    # ---- la barbe de mousse pend sous le menton (gravité), sur le col ----
    bd = sm([(196.0, 150.0), (206.0, 152.4), (220.0, 152.0), (231.0, 147.0), (234.0, 151.0), (230.0, 156.0), (226.0, 156.4),
             (222.0, 162.4), (218.0, 157.6), (212.0, 158.0), (207.0, 166.0), (203.0, 158.0), (198.0, 156.0)], t=0.85)
    fig.part('beard', bd, MOSS, grad=(234.0, 148.0, 198.0, 164.0, [(0, MOSS.light), (0.5, MOSS.base), (1, MOSS.shadow)]),
             cel=1.0, rim=0.6, cast=1.2, cast_on=['col'], details=[])
    names.append('beard')
    # ---- les cristaux de la tempe (dans la fêlure) et de la jointure sous l'oreille ----
    crystal_part(fig, 'ct1', (184.0, 94.0), -58, 11.0, 5.0, cast=0.7, cast_on=['head', 'nape'])
    crystal_part(fig, 'ct2', (185.5, 98.0), -82, 8.0, 4.0, cast=0.6, cast_on=['head', 'nape'])
    names += ['ct1', 'ct2']
    crystal_part(fig, 'cj1', (174.0, 132.0), -62, 16.0, 6.4, cast=0.8, cast_on=['head', 'col', 'body'])
    crystal_part(fig, 'cj2', (172.0, 138.0), -96, 12.0, 5.4, cast=0.7, cast_on=['head', 'col', 'body'])
    crystal_part(fig, 'cj3', (177.0, 141.0), -128, 8.0, 4.2, cast=0.6, cast_on=['col', 'body'])
    names += ['cj1', 'cj2', 'cj3']
    fig.pose(names, HEAD)
    fig.pose(['cj1', 'cj2', 'cj3'], UC)


def mouth(cx, top, bot, w, gape):
    """La gueule ouverte de la statue, centrée sous le nez : l'ouverture (rouge sombre), une rangée de dents carrées en
    haut (plantées dans la lèvre du haut) et en bas, la lèvre de pierre éclairée en dessous."""
    hw = w / 2
    out = []
    op = sm([(cx - hw, top + 1.4), (cx - hw * 0.4, top - 0.4), (cx + hw * 0.5, top - 0.2), (cx + hw, top + 1.6),
             (cx + hw * 0.92, bot - 0.6), (cx + hw * 0.3, bot + 0.6), (cx - hw * 0.4, bot + 0.6), (cx - hw * 0.95, bot - 0.8)], sharp=(0, 3), t=0.85)
    out += [(op.move(-0.4, 1.2), SAND.deep, 0.5),
            (op, ('lin', cx, top, cx, bot, [(0, MOUTH[2]), (0.55, MOUTH[1]), (1, MOUTH[0])]), 1)]
    # les dents du haut : carrées, plantées dans la lèvre ; plus étroites vers le fond (côté droit)
    n = 5
    xs = [cx - hw + 1.2 + i * (w - 2.0) / n for i in range(n + 1)]
    for i in range(n):
        a, b = xs[i] + 0.35, xs[i + 1] - 0.35
        hgt = 3.0 + 0.4 * (1 - abs(i - 2) / 2)
        out += [(rk([(a, top - 0.8), (b, top - 0.8), (b, top + hgt), (a, top + hgt)], [0.3, 0.3, 0.9, 0.9]), SAND.hi if i >= 2 else SAND.light, 1)]
    for i in range(1, n - 1):
        a, b = xs[i] + 0.4, xs[i + 1] - 0.4
        hgt = 2.4 + 0.3 * (i % 2)
        out += [(rk([(a, bot - hgt), (b, bot - hgt), (b, bot + 0.8), (a, bot + 0.8)], [0.9, 0.9, 0.3, 0.3]), SAND.light if i >= 2 else SAND.base, 1)]
    # la lèvre du bas (le menton de pierre) éclairée
    out += [(ribbon([(cx - hw * 0.8, bot + 1.8), (cx, bot + 2.6), (cx + hw * 0.9, bot + 1.6)], [0.2, 1.1, 0.2]), SAND.hi, 0.5)]
    return out


# ---------------------------------------------------------------- le bras proche

def near_arm(fig, P, UC):
    S = mapp(UC, NS)
    Wt = (NW0[0] + P['fn'][0], NW0[1] + P['fn'][1])
    E, W = ik(S, Wt, NL[0], NL[1], NSG)
    up = limb([S, lerp(S, E, 0.5), E], [46.0, 42.0, 34.0])
    fo = limb([E, lerp(E, W, 0.55), W], [34.0, 41.0, 36.0])
    arm, garm = fuse([up, fo], 2.0, 80)
    det = []
    # les faces de roche du bras : l'épaule-dôme éclairée, le dessus de l'avant-bras ; l'intérieur dans l'ombre
    d1 = ((E[0] - S[0]) / NL[0], (E[1] - S[1]) / NL[0])
    det.append(face([lerp(S, E, 0.05), (S[0] + 8, S[1] - 14), (S[0] + 18, S[1] - 4), lerp(lerp(S, E, 0.5), (E[0] + 16, E[1] - 2), 0.4),
                     lerp(S, E, 0.55)], ROCK.light, 0.0, 3.0))
    fdir = ((W[0] - E[0]) / NL[1], (W[1] - E[1]) / NL[1])
    nrm = (fdir[1], -fdir[0])            # vers la droite du membre (côté de la lumière)
    det.append(face([(E[0] + nrm[0] * 6, E[1] + nrm[1] * 6), (E[0] + nrm[0] * 16, E[1] + nrm[1] * 16 + 4),
                     (W[0] + nrm[0] * 17, W[1] + nrm[1] * 17 - 6), (W[0] + nrm[0] * 8, W[1] + nrm[1] * 8 - 8)], ROCK.light, 0.5, 3.0))
    det.append(face([(E[0] - nrm[0] * 6, E[1] - nrm[1] * 6 + 6), (E[0] - nrm[0] * 16, E[1] - nrm[1] * 16), (W[0] - nrm[0] * 18, W[1] - nrm[1] * 18 - 4),
                     (W[0] - nrm[0] * 8, W[1] - nrm[1] * 8)], ROCK.shadow, 0.45, 3.0))
    det += fissure(zig(lerp(S, E, 0.35), lerp(S, E, 0.8), 3, 1.6, 1), 0.8)
    # le brassard de grès gravé : une bande qui fait le tour de l'avant-bras (deux arcs d'ellipse parallèles)
    c0 = lerp(E, W, 0.6)
    c1 = lerp(E, W, 0.84)
    band = bracer(c0, c1, nrm, fdir, 23.0, P['glow'])
    det += band
    fig.part('narm', arm, ROCK, grad=grad_of(arm, [(0, '#a29a7c'), (0.5, '#736d68'), (1, '#463e52')]), cel=2.2, rim=0.9, cast=2.0,
             cast_on=['body', 'nleg', 'nfoot', 'col', 'farm', 'fleg'], details=det)
    # la racine du bras se fond dans la bosse (aucune couture à l'épaule)
    a0 = mapp(UC, (72.0, 112.0))
    a1 = mapp(UC, (104.0, 84.0))
    fig.masks['narm'] = (a0[0], a0[1], a1[0], a1[1], 'body')
    # les cristaux du coude (dans la jointure, côté du dos), de longueurs différentes
    ob = (-d1[0] * 0.5 - fdir[0] * 0.5, -d1[1] * 0.5 - fdir[1] * 0.5)
    L_ = math.hypot(*ob) or 1
    ob = (ob[0] / L_, ob[1] / L_)
    base = (E[0] + ob[0] * 12.0, E[1] + ob[1] * 12.0)
    a_ob = math.degrees(math.atan2(ob[0], -ob[1]))
    crystal_part(fig, 'ce1', (base[0] + 2.0, base[1] - 6.0), a_ob + 34, 20.0, 7.4, cast=1.0, cast_on=['narm'])
    crystal_part(fig, 'ce2', base, a_ob + 4, 14.0, 6.4, cast=0.9, cast_on=['narm', 'ce1'])
    crystal_part(fig, 'ce3', (base[0] + 1.0, base[1] + 6.0), a_ob - 30, 9.0, 5.0, cast=0.8, cast_on=['narm'])
    # le poing proche, posé sur les phalanges
    na = (ang_of(E, W) - ang_of(NE0, NW0)) * 0.4 + P['nrot']
    fist_parts(fig, 'nfist', W, na, 1.0, ROCK, [(0, '#aaa286'), (0.5, '#78726c'), (1, '#4a4256')])


def bracer(c0, c1, nrm, fdir, hw, glow):
    """Le brassard : une bande entre deux arcs (perspective : le bord proche plus bas au milieu), gravé de signes qui
    luisent ; peint DANS l'avant-bras (il en fait le tour d'un bord à l'autre)."""
    def arc(c, sag):
        pts = []
        for i in range(13):
            t = -1 + 2 * i / 12
            s = hw * 1.3 * t
            d = sag * (1 - t * t)
            pts.append((c[0] + nrm[0] * s + fdir[0] * d, c[1] + nrm[1] * s + fdir[1] * d))
        return pts
    a = arc(c0, 3.2)
    b = arc(c1, 3.2)
    sh = sm(a + b[::-1], sharp=(0, 12, 13, 25), t=0.8)
    lit = sm(a + arc(lerp(c0, c1, 0.28), 3.2)[::-1], sharp=(0, 12, 13, 25), t=0.8)
    out = [(sh.move(-0.6, 1.6), SAND.deep, 0.5),
           (sh, ('lin', c0[0] + nrm[0] * hw, c0[1] - 6, c0[0] - nrm[0] * hw, c1[1] + 4, [(0, SAND.light), (0.5, SAND.base), (1, SAND.shadow)]), 1),
           (lit, SAND.hi, 0.55)]
    # les signes gravés (inventés), qui luisent comme les cristaux
    cm = lerp(c0, c1, 0.56)
    for i, (t, k) in enumerate(((-0.62, 1), (-0.18, 0), (0.26, 2), (0.66, 1))):
        s = hw * 1.3 * t
        d = 3.2 * (1 - t * t)
        p = (cm[0] + nrm[0] * s + fdir[0] * d, cm[1] + nrm[1] * s + fdir[1] * d)
        op = 0.55 + 0.12 * glow if abs(t) < 0.9 else 0.3
        for gl in glyph(p[0], p[1], 2.3, k):
            out += [(gl.move(0.2, 0.5), SAND.deep, 0.5), (gl, GAR.light if glow > 1.5 else GAR.base, op)]
    return out


def main():
    """titan.svg (grand) et titan-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/boss-terre.webp (1000 px de haut : même finesse que les héros, il est deux fois plus grand) et
    boss-terre-160.webp (même densité que les petites images des héros)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', '..', 'heros', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    x0, y0, w, h = FRAME
    for name, ow, hh, out in (('titan', 0.95, 1000, ID_JEU), ('titan-petit', 1.35, 312, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(hh)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
