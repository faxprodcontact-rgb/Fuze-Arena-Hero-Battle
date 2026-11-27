# Le matelot (mon-barzul-rapide, eau, monstre « rapide » du clan de Barzul, le capitaine pirate) redessiné en
# VECTORIEL lisse, dans le style moderne de l'interface (même outil, même trait, même échelle que Kael et que son
# équipage déjà redessiné, Barzul et Jessa : ../../heros/atelier.py, ../../heros/jessa/jessa.py).
#
#   python3 refonte-graphique/ui-moderne/monstres/matelot/matelot.py   # → matelot.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/matelot.txt) : le jeune mousse de l'équipage,
# maigre, sec et vif, tout en jambes. Trois quarts vers la droite, posture d'escrimeur qui bondit : grande fente, la
# jambe lointaine fléchie en avant (genou au-dessus du pied), la jambe proche tendue loin en arrière, pieds nus à plat.
# Bras lointain en avant, coude plié vers le bas, le poing serre le sabre d'abordage « en garde » (la lame prolonge
# l'avant-bras et monte vers l'ennemi) ; bras proche le long du corps, le poing serre un petit couteau tenu à l'envers
# (lame en bas, vers l'arrière).
# Tête : visage maigre et jeune (joues creuses, menton pointu sur la médiane), yeux rusés plissés vert d'eau sous une
# paupière sombre, sourcils froncés en V, nez fin, sourire en coin qui montre les dents du haut avec UNE dent en moins ;
# oreille soudée au crâne avec son anneau d'or ; bandana rouge noué derrière la tête (nœud, deux pans), mèches noires
# en bataille qui en dépassent (nuque, tempe).
# Tenue : chemise lavande ouverte en V sur une poitrine maigre, manches arrachées en lambeaux ; gilet court bleu marine
# sans manches à deux boutons d'or ; ceinture de cuir à boucle d'or, chiffon rouge noué sur la hanche lointaine (deux
# pans) ; pantalon court noir bleuté effiloché sous les genoux, accroc au genou proche ; jambes et pieds nus.
# Armes : sabre d'abordage (lame courbe d'acier qui s'élargit vers la pointe, coquille et branche de garde d'or,
# poignée de cuir) ; petit couteau (lame courte, manche de bois).
# Coordonnées = pixels du dessin pixel art (sol y = 116, pieds en (64, 116)), pour se poser au même endroit dans le jeu.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Mat, sm, limb, ribbon, sides, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp, resample  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (rot, add, sub, lerp, norm, ang_of, ik, arm_shape, crpath, taper, curve_band, under,  # noqa: E402
                    FigN, inset, poly, from_poly, fused, cut, unit)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-barzul-rapide'

# ---------- matières (celles de l'équipage de Barzul : mêmes bleus, mêmes ors, même rouge) ----------
VEST = Mat('#94bcff', '#4f80dc', '#2f4eaa', '#1e2a78', '#11174a', glint='#e8f4ff')       # gilet bleu marine
GOLD = Mat('#fff6c0', '#ffd04a', '#e8a032', '#a65a24', '#5c2418', glint='#fffbe8')
HAIR = Mat('#9cb4f4', '#5a6aa8', '#363a64', '#211f3e', '#120f26', glint='#d8e4ff')     # noir aux reflets bleutés
SKIN = Mat('#ffd2a0', '#efa46c', '#cf7e50', '#9e5242', '#5e2834')                        # peau hâlée
RED = Mat('#ffa488', '#f2664e', '#c8323c', '#861a3a', '#4c0c28')
LEATHER = Mat('#eaa870', '#c27c46', '#8e4c2c', '#5c2a26', '#341620')
SHIRT = Mat('#ffffff', '#f4f2ff', '#d6d6f0', '#a6a6d4', '#6c6aa2')                       # chemise lavande
STEEL = Mat('#f4f8ff', '#cad6ec', '#8e9cbe', '#565f84', '#2e3454', glint='#ffffff')
WOOD = Mat('#e6a468', '#b8763e', '#8a4e2c', '#5a2c26', '#341620')
PANTS = Mat('#7a7aae', '#4a4c7e', '#303056', '#1e1c3a', '#120f24')
TEETH = Mat('#ffffff', '#fbf6ee', '#e8e0d8', '#b0a6b6', '#6e6478')
LIPS = ('#6e2232', '#a8484a', '#d06a5e')
IRIS = ('#a8f4d4', '#3aa884', '#1a5a56')
EYE_INK = '#1c0c1c'

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol: 64 116)
FRAME = (34, 26, 96, 94)       # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
H0 = (73.0, 62.6)  # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)
PELVIS = (70.5, 88.0)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 ; crouch : il plie les genoux (le bassin descend) ; lean : le haut du corps penche depuis
#   les hanches (+ = en avant) ; head / tilt : la tête ; pl : les pans (bandana, chiffon) se balancent ;
#   blink : œil fermé ; sq : il plisse les yeux ; grin : le sourire en coin s'élargit ;
#   tx / lift : tout le corps avance / décolle (il fond sur l'ennemi) ; fn / ff : les pieds (proche / lointain) se
#   replient sous lui en l'air (décalage) ; fist : le poing au sabre (décalage) ; sa : l'angle de la lame (−50° au
#   repos, 0 = à plat vers la droite) ; na : le bras au couteau se balance (degrés).
SA0 = -50.0
F0 = (97.0, 68.4)          # le milieu du poing au sabre (au repos)
S0 = (58.0, 68.6)          # l'épaule proche
SF0 = (81.2, 67.6)         # l'épaule lointaine
LU, LF = 9.6, 9.4          # bras proche : bras, avant-bras
LUF, LFF = 10.0, 9.8       # bras lointain
W0 = (52.2, 85.6)          # le poignet proche (au repos)
HN0, HF0 = (64.2, 89.6), (76.6, 89.6)   # les hanches (proche, lointaine)
AN0, AF0 = (48.6, 110.6), (86.4, 110.6)  # les chevilles (proche, lointaine)
LTN, LSN = 14.2, 12.8      # jambe proche : cuisse, tibia
LTF, LSF = 13.4, 11.4      # jambe lointaine

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, pl=0.0, blink=0.0, sq=0.0, grin=0.0,
            tx=0.0, lift=0.0, fn=(0.0, 0.0), ff=(0.0, 0.0), fist=(0.0, 0.0), sa=SA0, na=0.0)


def saber_frame(F, a):
    """Le repère du sabre : (u le long de la lame vers la pointe, v vers le tranchant, en bas à droite) → dessin."""
    r = math.radians(a)
    d = (math.cos(r), math.sin(r))
    n = (-d[1], d[0])
    return lambda u, v: (F[0] + d[0] * u + n[0] * v, F[1] + d[1] * u + n[1] * v)


def _dir(M, v):
    a, b, c, d = M[:4]
    x, y = a * v[0] + c * v[1], b * v[0] + d * v[1]
    L = math.hypot(x, y) or 1
    return (x / L, y / L)


def swell(n, w, w0=0.1):
    """Les largeurs d'un trait effilé aux deux bouts (n+1 points, w au milieu)."""
    return [max(w0, w * math.sin(math.pi * i / n) ** 0.7) for i in range(n + 1)]


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigN(*frame, ow=ow)
    br = P['breath']
    ROOTM = mT(P['tx'], -P['lift'])
    U = mchain(ROOTM, mT(0, P['crouch']), mR(P['lean'], *PELVIS))           # le haut du corps (depuis le bassin)
    UC = mchain(U, mT(0, -0.45 * br))                                       # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 70, 86))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 72.5, 63.0), mS(1.1, 1.1, *H0))

    # ---- derrière tout : les pans du bandana, les cheveux de la nuque ----
    tails = bandana_tails(fig, P)
    fig.pose(tails, HEAD)
    hb = hair_back(fig, P)
    fig.pose(hb, HEAD)

    # ---- le bras lointain (derrière le buste ; le poing et le sabre viendront tout devant) ----
    SF = mapp(UC, SF0)
    Fs = mapp(ROOTM, add(F0, P['fist']))
    GM = mchain(mT(Fs[0] - F0[0], Fs[1] - F0[1]), mR(P['sa'] - SA0, *F0))  # la pose du sabre et de son poing
    WF = mapp(GM, saber_frame(F0, SA0)(-5.6, 1.5))                          # le poignet, au talon de la main
    EF = ik(SF, WF, LUF, LFF, 1)
    arm(fig, 'f', SF, EF, WF)

    # ---- les jambes (la lointaine, fléchie en avant, puis la proche, tendue en arrière) ----
    HN, HF = mapp(U, HN0), mapp(U, HF0)
    AN = add(mapp(ROOTM, AN0), P['fn'])
    AF = add(mapp(ROOTM, AF0), P['ff'])
    KF = ik(HF, AF, LTF, LSF, -1)
    KN = ik(HN, AN, LTN, LSN, -1)
    legs = []
    legs += leg(fig, 'f', HF, KF, AF, P, far=True)
    legs += leg(fig, 'n', HN, KN, AN, P, far=False)
    seat(fig, P, U, HN, HF)
    legs.append('seat')

    # ---- le bras proche (sur le côté, devant la jambe) ----
    S = mapp(UC, S0)
    W = add(S, rot(sub(W0, S0), P['na']))
    E = ik(S, W, LU, LF, -1)
    arm(fig, 'n', S, E, W)

    # ---- le buste : chemise (et ses moignons de manches en lambeaux), gilet, ceinture, chiffon rouge ----
    shirt(fig, P, S, E, SF, EF)
    fig.pose(['shirt'], TOR)
    vest(fig, P)
    fig.pose(['vestN', 'vestF'], TOR)
    belt_n = belt(fig, P)
    fig.pose(belt_n, U)
    rag_n = rag(fig, P)
    fig.pose(rag_n[:-1], mchain(U, mR(-2.6 * P['pl'], 80.6, 85.6)))
    fig.pose(rag_n[-1:], U)

    # ---- la main au couteau ----
    knife_fist(fig, P, E, W)

    # ---- le cou, la tête, le bandana ----
    neck(fig, P)
    fig.pose(['neck'], UC)
    hn = head(fig, P)
    fig.pose(hn, HEAD)
    bn = bandana(fig, P)
    fig.pose(bn, HEAD)

    # ---- le sabre et le poing lointain, tout devant ----
    sab = saber(fig, P)
    fig.pose(sab, GM)

    L = saber_frame(Fs, P['sa'])
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, GM=GM, L=L, tip=L(36.0, -1.4), guard=L(4.2, 0.0), fist=Fs,
                   head=mapp(HEAD, (72, 46)), mouth=mapp(HEAD, (74.4, 58.0)), chest=mapp(TOR, (70, 74)),
                   knife=mapp(ROOTM, (0, 0)), feet=(mapp(ROOTM, AN0), mapp(ROOTM, AF0)), AN=AN, AF=AF)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def xf_pt(o, a, p):
    r = rot(p, a)
    return (o[0] + r[0], o[1] + r[1])


# ---------------------------------------------------------------- les bras nus (maigres, d'un seul tenant)
def arm(fig, pre, S, E, W):
    near = pre == 'n'
    ws = (5.0, 4.3, 3.7) if near else (4.7, 4.1, 3.5)
    sh = arm_shape(S, E, W, ws)
    det = [(ribbon([lerp(S, E, 0.2), lerp(S, E, 0.8), lerp(E, W, 0.25), lerp(E, W, 0.8)], [0.2, 0.9, 0.7, 0.2]).move(1.0, -0.4), SKIN.light, 0.5),
           (ribbon([lerp(S, E, 0.3), E, lerp(E, W, 0.4)], [0.2, 1.0, 0.2]).move(-1.3, 0.5), SKIN.shadow, 0.35),
           # le creux du coude (une ombre douce du côté où il plie), un petit méplat clair sur l'avant-bras
           (ellipse(*lerp(E, W, 0.12), 0.9, 0.45, ang_of(sub(W, E))), SKIN.shadow, 0.3)]
    fig.part(pre + 'arm', sh, SKIN, grad=(S[0] + 4, S[1] - 2, W[0] - 3, W[1] + 2, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.9 if near else 0, details=det)


# ---------------------------------------------------------------- les jambes : pantalon effiloché, tibias et pieds nus
def hem_cut(shape, P0, d):
    """La forme coupée par la droite qui passe par P0, perpendiculaire à d (on garde le côté opposé à d)."""
    from shapely.geometry import Polygon
    n = (-d[1], d[0])
    A = add(P0, n, 40)
    B = add(P0, n, -40)
    half = Polygon([A, B, add(B, d, -60), add(A, d, -60)])
    g = _pp(shape).intersection(half)
    from outils import _shape
    return _shape(g)


def _pp(shape):
    from outils import _poly
    return _poly(shape)


def foot_shape(A, far, P):
    """Un pied nu posé à plat (le talon derrière la cheville, les orteils vers l'ennemi) ; d'un seul tenant avec la
    cheville. A = la cheville."""
    x, y = A
    g = GRD - P['lift'] if False else None  # (le pied suit la cheville : il se pose quand la cheville y est)
    s = 0.94 if far else 1.0
    pts = [(x - 2.0 * s, y - 2.2), (x + 1.8 * s, y - 2.0), (x + 3.6 * s, y + 1.4), (x + 6.6 * s, y + 2.8), (x + 9.0 * s, y + 3.6),
           (x + 10.2 * s, y + 4.6), (x + 10.0 * s, y + 5.5), (x + 3.0 * s, y + 5.6), (x - 3.0 * s, y + 5.6), (x - 4.4 * s, y + 4.6),
           (x - 4.2 * s, y + 2.4), (x - 3.0 * s, y + 0.4)]
    return sm(pts, sharp=(6, 8), t=0.92)


def leg(fig, pre, H, K, A, P, far):
    names = []
    dT = norm(sub(K, H))
    dS = norm(sub(A, K))
    # le tibia et le pied : une seule forme (de dans le pantalon jusqu'aux orteils)
    top = add(K, dT, -2.6)
    shin = limb([top, K, lerp(K, A, 0.5), A], [4.6, 4.4, 3.9, 3.4] if not far else [4.3, 4.1, 3.7, 3.2])
    foot = foot_shape(A, far, P)
    sh = fused([shin, foot], smooth=0.5)
    x, y = A
    s = 0.94 if far else 1.0
    det = [(ribbon([lerp(K, A, 0.1), lerp(K, A, 0.55), add(A, dS, -1.0)], [0.2, 0.8, 0.2]).move(1.0, -0.2), SKIN.light, 0.5),
           (ribbon([lerp(K, A, 0.1), lerp(K, A, 0.6), A], [0.2, 0.9, 0.2]).move(-1.2, 0.3), SKIN.shadow, 0.35),
           # le dessus du pied éclairé, la cheville (une bosse douce), la séparation du gros orteil (un seul trait court)
           (ellipse(x + 4.8 * s, y + 2.4, 2.6 * s, 0.8, 22), SKIN.hi, 0.35),
           (ellipse(x + 0.6 * s, y + 0.4, 0.9, 0.7), SKIN.shadow, 0.35),
           (ribbon([(x + 7.4 * s, y + 4.0), (x + 8.0 * s, y + 4.8), (x + 8.2 * s, y + 5.4)], [0.1, 0.35, 0.1]), SKIN.deep, 0.5),
           # la plante : un liseré sombre au ras du sol
           (sm([(x - 6, y + 4.9), (x + 12, y + 4.9), (x + 12, y + 7), (x - 6, y + 7)]), SKIN.deep, 0.45)]
    fig.part(pre + 'shin', sh, SKIN, grad=(x + 8, K[1], x - 4, y + 5, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.8, cast_on=['fshin', 'fpants'], details=det)
    names.append(pre + 'shin')
    # le pantalon : de la hanche jusque sous le genou, le bas effiloché (quelques lambeaux de tailles différentes)
    hem = add(K, dS, 2.3 if not far else 2.0)
    tube = arm_shape(add(H, dT, -3.0), K, add(hem, dS, 3.0), (8.6, 6.9, 6.4) if not far else (8.2, 6.6, 6.1))
    tube = hem_cut(tube, hem, dS)
    nS = (-dS[1], dS[0])
    rags = []
    for off, ln, w in ((-2.2, 1.5, 1.9), (-0.2, 2.6, 2.1), (2.0, 1.2, 1.7)):
        b = add(add(hem, nS, off), dS, -0.6)
        rags.append(taper([b, add(add(b, dS, ln * 0.6), nS, 0.15 * ln), add(add(b, dS, ln), nS, 0.3 * ln)], w, 0.25, tip='round'))
    tube = fused([tube] + rags, smooth=0.3)
    pdet = [(ribbon([lerp(H, K, 0.15), lerp(H, K, 0.6), K], [0.2, 1.2, 0.3]).move(1.4, -0.6), PANTS.light, 0.5),
            (ribbon([lerp(H, K, 0.3), K, hem], [0.2, 1.2, 0.2]).move(-1.6, 0.5), PANTS.deep, 0.35),
            # le pli du genou (une ombre douce en travers, côté où il plie)
            (ribbon([add(K, nS, -2.6), add(add(K, dT, -0.8), nS, 0.0), add(K, nS, 2.6)], [0.1, 0.6, 0.1]), PANTS.shadow, 0.55),
            # l'ourlet effiloché : le dessous des lambeaux plus sombre
            (ribbon([add(hem, nS, -3.4), add(add(hem, dS, 0.8), nS, 0), add(hem, nS, 3.4)], [0.2, 1.0, 0.2]), PANTS.shadow, 0.5)]
    if not far:
        # l'accroc au genou proche : la peau du genou dans une petite déchirure aux bords effilochés
        c = add(add(K, dT, -0.4), nS, -0.6)
        tear = sm([add(c, rot(dT, 0), 1.5), add(c, nS, 1.1), add(c, rot(dT, 180), 1.4), add(c, nS, -1.0)], t=0.95)
        pdet += [(tear.scale(1.25, 1.25, *c), PANTS.deep, 0.8), (tear, ('lin', c[0] + 1, c[1] - 1, c[0] - 1, c[1] + 1, [(0, SKIN.light), (1, SKIN.shadow)]), 1),
                 (ribbon([add(c, rot(dT, 180), 1.4), add(c, nS, -0.9), add(c, rot(dT, 0), 1.5)], [0.1, 0.35, 0.1]), PANTS.light, 0.5)]
    fig.part(pre + 'pants', tube, PANTS, grad=(H[0] + 6, H[1], K[0] - 4, hem[1] + 2, [(0, PANTS.light), (0.5, PANTS.base), (1, PANTS.shadow)]),
             cel=1.0, rim=0.5, cast=1.0, cast_on=[pre + 'shin', 'fshin', 'fpants'], details=pdet)
    names.append(pre + 'pants')
    return names


def seat(fig, P, U, HN, HF):
    """Le haut du pantalon : du dessous de la ceinture à l'entrejambe (il réunit les deux cuisses)."""
    pts = [mapp(U, p) for p in [(59.6, 83.6), (70.5, 84.2), (81.4, 83.6), (82.2, 87.4)]]
    pts += [add(HF, (3.6, 1.6)), add(HF, (1.4, 5.2)), mapp(U, (71.0, 94.2)), add(HN, (-2.0, 5.0)), add(HN, (-4.6, 1.0)), mapp(U, (59.2, 86.8))]
    sh = sm(pts, t=0.9)
    det = [(ribbon([mapp(U, (68.6, 86.0)), mapp(U, (70.2, 89.6)), mapp(U, (71.0, 93.4))], [0.1, 0.7, 0.1]), PANTS.deep, 0.45),
           (ribbon([mapp(U, (76.0, 86.0)), mapp(U, (79.6, 87.6)), mapp(U, (81.4, 86.4))], [0.2, 1.0, 0.2]), PANTS.light, 0.4)]
    fig.part('seat', sh, PANTS, grad=(82, 84, 60, 94, [(0, PANTS.light), (0.5, PANTS.base), (1, PANTS.shadow)]), cel=1.0, rim=0.5,
             cast=0.9, cast_on=['fpants', 'npants'], details=det)


# ---------------------------------------------------------------- la chemise lavande et ses manches arrachées
def stub(S, E, far):
    """Le moignon de manche autour de la racine du bras, son bas en lambeaux de tailles différentes."""
    d = norm(sub(E, S))
    n = (-d[1], d[0])
    L = 4.4 if not far else 4.0
    w = 6.8 if not far else 6.2
    base = add(S, d, -2.5)
    end = add(S, d, L)
    tube = limb([base, lerp(base, end, 0.5), end], [w, w, w * 0.98])
    tube = hem_cut(tube, end, d)
    tatters = []
    for off, ln, ww in ((-2.3, 2.4, 2.0), (-0.2, 1.3, 2.2), (1.9, 2.0, 1.8)):
        b = add(add(end, n, off * (w / 6.8)), d, -0.6)
        tatters.append(taper([b, add(b, d, ln * 0.6), add(add(b, d, ln), n, -0.25 * ln)], ww, 0.2, tip='round'))
    return fused([tube] + tatters, smooth=0.3), end, d, n


def shirt(fig, P, S, E, SF, EF):
    body = sm([(67.0, 63.4), (72.0, 64.4), (77.2, 63.2), (81.0, 64.0), (84.0, 65.6), (84.6, 68.8), (83.2, 72.6), (81.8, 77.0),
               (81.4, 81.6), (81.8, 86.0), (70.5, 86.8), (59.6, 86.2), (59.6, 81.2), (59.0, 76.2), (57.8, 72.2), (56.0, 69.2),
               (57.4, 65.8), (62.0, 64.0)], t=0.9)
    # les moignons de manche (calculés dans le repère du buste : la pose du buste les reposera)
    import atelier
    inv = lambda p: p  # le buste est posé ensuite par TOR (même repère que UC au souffle près)
    sn, en, dn, nn = stub(S, E, False)
    sf, ef, df, nf = stub(SF, EF, True)
    sh = fused([body, sn, sf], smooth=0.6)
    det = [
        # l'ombre du côté proche (la chemise tourne), la lumière sur l'épaule lointaine
        (sm([(54, 64), (61.5, 64), (62.4, 72), (62.6, 87), (54, 87)]), SHIRT.shadow, 0.35),
        (ribbon([(77.4, 64.0), (81.4, 64.8), (83.6, 66.8)], [0.2, 0.9, 0.2]), SHIRT.hi, 0.8),
        # la peau de la poitrine maigre dans l'ouverture en V (le col ouvert, ses deux revers)
        (sm([(67.4, 63.6), (72.2, 64.6), (76.6, 63.4), (74.4, 67.6), (71.4, 71.6), (69.6, 67.8)], sharp=(4,), t=0.85),
         ('lin', 76, 63, 68, 70, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), 1),
        (ribbon([(70.8, 66.4), (71.2, 68.6), (71.4, 70.6)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.45),
        (sm([(67.0, 63.4), (72.0, 64.4), (77.0, 63.2), (77.0, 64.6), (72.0, 66.0), (67.2, 64.8)]), SKIN.deep, 0.35),
        (ribbon([(67.6, 63.8), (69.8, 67.8), (71.4, 71.8)], [0.4, 0.9, 0.2]), SHIRT.shadow, 0.6),
        (ribbon([(76.4, 63.6), (74.2, 67.6), (71.6, 71.8)], [0.4, 0.8, 0.2]), SHIRT.hi, 0.8),
        # l'accroc de la chemise (bas, côté lointain) : la peau dans une petite déchirure
        (sm([(73.2, 79.2), (74.4, 78.4), (74.9, 79.6), (74.0, 81.0), (73.0, 80.6)], t=0.95), SHIRT.deep, 0.6),
        (sm([(73.4, 79.4), (74.3, 78.8), (74.6, 79.7), (73.9, 80.6), (73.2, 80.4)], t=0.95), SKIN.base, 1),
        # le pli de la chemise rentrée sous la ceinture
        (ribbon([(62.4, 83.4), (66.0, 84.4), (70.0, 84.6)], [0.1, 0.6, 0.1]), SHIRT.shadow, 0.5)]
    # les lambeaux : leur dessous dans l'ombre, la racine du bras dans l'ombre de la manche
    for end, d, n in ((en, dn, nn), (ef, df, nf)):
        det += [(ribbon([add(end, n, -3.4), add(add(end, d, 1.0), n, 0), add(end, n, 3.4)], [0.2, 1.3, 0.2]), SHIRT.shadow, 0.55),
                (ribbon([add(add(end, d, -3.2), n, -2.6), add(add(end, d, -2.0), n, 0.4), add(add(end, d, -0.8), n, 2.8)], [0.1, 0.5, 0.1]), SHIRT.shadow, 0.35)]
    fig.part('shirt', sh, SHIRT, grad=(84, 64, 58, 84, [(0, SHIRT.hi), (0.45, SHIRT.base), (1, SHIRT.shadow)]), cel=1.0, rim=0.6, cast=1.0,
             cast_on=['narm', 'farm', 'seat', 'npants', 'fpants'], details=det)


# ---------------------------------------------------------------- le gilet court bleu marine (deux pans, deux boutons d'or)
def vest(fig, P):
    near = sm([(62.0, 64.2), (66.0, 63.6), (68.6, 66.6), (68.8, 71.6), (68.4, 76.6), (68.0, 80.8), (63.6, 81.4), (59.4, 80.8),
               (59.0, 76.6), (58.2, 72.4), (57.0, 69.6), (59.6, 69.2), (61.2, 67.6)], sharp=(6, 7), t=0.88)
    det = [(sm([(54, 64), (61, 64), (62.4, 82), (54, 82)]), VEST.shadow, 0.45),
           (ribbon([(66.4, 64.6), (67.6, 70.0), (67.4, 76.0), (67.0, 80.0)], [0.2, 0.8, 0.8, 0.2]), VEST.light, 0.55),
           (ribbon([(62.8, 66.0), (63.6, 72.0), (63.0, 79.0)], [0.1, 0.6, 0.1]), VEST.shadow, 0.4),
           # le bord de devant, un peu plus clair (l'épaisseur du drap)
           (ribbon([(66.4, 63.8), (68.9, 67.0), (69.0, 74.0), (68.5, 80.8)], [0.4, 0.6, 0.6, 0.4]), VEST.hi, 0.45)]
    for by in (71.0, 76.6):
        bx = 67.0 + (by - 71) * -0.04
        det += [(ellipse(bx, by, 0.95, 0.9), GOLD.shadow, 1), (ellipse(bx + 0.05, by - 0.1, 0.7, 0.66), GOLD.light, 1),
                (ellipse(bx + 0.25, by - 0.35, 0.25, 0.22), GOLD.glint, 0.9)]
    fig.part('vestN', near, VEST, grad=(68, 64, 58, 80, [(0, VEST.light), (0.5, VEST.base), (1, VEST.shadow)]), cel=1.0, rim=0.5,
             cast=1.0, cast_on=['shirt'], details=det)
    far = sm([(76.6, 63.4), (80.0, 64.2), (82.4, 66.0), (84.6, 68.2), (83.6, 72.0), (82.2, 76.6), (81.8, 80.4), (77.4, 81.0),
              (73.6, 80.6), (73.6, 76.0), (73.8, 71.4), (74.6, 67.4)], sharp=(6, 7, 8), t=0.88)
    det = [(ribbon([(78.8, 65.0), (82.2, 67.6), (82.6, 72.0), (81.6, 77.6)], [0.2, 1.2, 1.2, 0.2]), VEST.light, 0.6),
           (ribbon([(80.0, 65.4), (82.4, 67.8), (82.6, 70.6)], [0.1, 0.5, 0.1]), VEST.hi, 0.6),
           (ribbon([(75.2, 68.0), (74.6, 74.0), (74.6, 80.0)], [0.2, 0.8, 0.2]), VEST.shadow, 0.5)]
    fig.part('vestF', far, VEST, grad=(84, 64, 74, 80, [(0, VEST.light), (0.5, VEST.base), (1, VEST.shadow)]), cel=0.9, rim=0.55,
             cast=1.0, cast_on=['shirt'], details=det)


# ---------------------------------------------------------------- la ceinture de cuir et sa boucle d'or
BELT_I = [(58.6, 82.0), (64.0, 82.9), (70.5, 83.2), (77.0, 82.8), (82.4, 81.8)]
BELT_O = [(58.8, 85.4), (64.0, 86.2), (70.5, 86.5), (77.0, 86.1), (82.6, 85.2)]


def belt(fig, P):
    sh = curve_band(BELT_I, BELT_O, 0, 1)
    sh = from_poly(poly(sh))
    from shapely.geometry import Polygon
    g = Polygon(poly(sh, 8)).buffer(0).intersection(Polygon([(59.0, 78), (82.2, 78), (82.4, 90), (59.0, 90)]))
    from outils import _shape
    sh = _shape(g.buffer(0.4, join_style=1).buffer(-0.4, join_style=1))
    det = [(curve_band(BELT_I, BELT_O, 0, 0.28), LEATHER.light, 0.7),
           (curve_band(BELT_I, BELT_O, 0.75, 1), LEATHER.shadow, 0.7),
           (sm([(55, 80), (63, 80), (63, 88), (55, 88)]), LEATHER.shadow, 0.4)]
    bx, by = 70.6, 84.8
    det += [(rpoly([(bx - 2.0, by - 2.1), (bx + 2.0, by - 2.2), (bx + 2.0, by + 2.0), (bx - 2.0, by + 2.1)], 0.7), GOLD.shadow, 1),
            (rpoly([(bx - 1.7, by - 1.85), (bx + 1.8, by - 1.95), (bx + 1.8, by + 1.7), (bx - 1.7, by + 1.8)], 0.6), GOLD.base, 1),
            (rpoly([(bx - 0.75, by - 0.85), (bx + 0.85, by - 0.9), (bx + 0.85, by + 0.75), (bx - 0.75, by + 0.8)], 0.3), LEATHER.deep, 1),
            (ribbon([(bx - 1.2, by - 1.5), (bx + 1.4, by - 1.6)], [0.25, 0.25]), GOLD.hi, 0.9),
            (ribbon([(bx + 1.45, by - 1.4), (bx + 1.45, by + 1.3)], [0.25, 0.2]), GOLD.light, 0.9),
            (ribbon([(bx - 0.2, by - 0.1), (bx + 2.6, by - 0.2)], [0.35, 0.35]), GOLD.light, 1)]
    fig.part('belt', sh, LEATHER, grad=(82, 82, 59, 86, [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]), cel=0.6,
             rim=0.45, cast=0.9, cast_on=['shirt', 'vestN', 'vestF', 'seat', 'fpants', 'npants'], details=det)
    return ['belt']


# ---------------------------------------------------------------- le chiffon rouge noué sur la hanche lointaine
def rag(fig, P):
    names = []
    tB = sm([(80.4, 85.4), (83.0, 85.6), (83.8, 89.6), (83.6, 93.8), (82.6, 95.0), (82.0, 93.6), (81.0, 94.4), (80.6, 90.0)],
            sharp=(4, 5, 6), t=0.9)
    fig.part('ragB', tB, RED, grad=(84, 86, 80, 95, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.5, cast=0.9,
             cast_on=['seat', 'fpants'], details=[(ribbon([(82.0, 86.6), (82.4, 90.4), (82.2, 93.6)], [0.2, 0.6, 0.2]), RED.shadow, 0.55)])
    tA = sm([(77.8, 85.6), (80.6, 85.8), (81.2, 90.4), (80.8, 95.8), (79.8, 97.0), (79.0, 95.6), (77.8, 96.6), (77.4, 90.6)],
            sharp=(4, 5, 6), t=0.9)
    fig.part('ragA', tA, RED, grad=(81, 86, 77, 97, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.5, cast=1.0,
             cast_on=['seat', 'fpants', 'npants', 'ragB'],
             details=[(ribbon([(79.4, 86.8), (79.8, 91.0), (79.4, 95.4)], [0.2, 0.7, 0.2]), RED.shadow, 0.5),
                      (ribbon([(80.4, 87.0), (80.6, 91.0)], [0.2, 0.4]), RED.hi, 0.6)])
    knot = sm([(77.4, 83.0), (80.4, 82.0), (83.2, 82.8), (84.0, 85.2), (82.8, 87.6), (79.8, 88.2), (77.4, 87.2), (76.8, 85.0)], t=0.9)
    fig.part('ragK', knot, RED, grad=(84, 82, 77, 88, [(0, RED.hi), (0.35, RED.light), (0.7, RED.base), (1, RED.shadow)]),
             cel=0.7, rim=0.55, cast=1.0, cast_on=['belt', 'ragA', 'ragB', 'seat', 'shirt', 'vestF', 'fpants'],
             details=[(ribbon([(78.0, 84.0), (80.2, 85.0), (82.6, 84.0)], [0.2, 0.6, 0.2]), RED.shadow, 0.55),
                      (ribbon([(78.2, 86.6), (80.2, 86.0), (82.6, 86.6)], [0.2, 0.5, 0.2]), RED.shadow, 0.45)])
    names += ['ragB', 'ragA', 'ragK']
    return names


# ---------------------------------------------------------------- la main au couteau (dos de la main, prise à l'envers)
def knife_fist(fig, P, E, W):
    """Le poing proche, vu de dos (jointures vers l'ennemi) : le manche de bois le traverse de l'avant-haut (pommeau,
    sous le pouce) à l'arrière-bas (la lame sort sous l'auriculaire, vers l'arrière et le bas)."""
    a = norm(sub(W, E))                                     # l'axe de l'avant-bras (vers la main)
    b = (a[1], -a[0])                                       # vers l'avant (l'ennemi) quand le bras pend
    if b[0] < 0:
        b = (-b[0], -b[1])
    H = lambda x, y: (W[0] + a[0] * x + b[0] * y, W[1] + a[1] * x + b[1] * y)   # x : vers les doigts, y : vers l'avant
    # la lame : du bas-arrière du poing, vers le bas et l'arrière
    kd = norm(add(rot(a, 38), (0, 0)))
    kd = norm((a[0] * math.cos(math.radians(40)) - a[1] * math.sin(math.radians(40)) * 0 - b[0] * 0.75,
               a[1] * 0.77 - b[1] * 0.75))
    base = H(3.4, -1.2)
    tip = add(base, kd, 8.6)
    kn = (-kd[1], kd[0])
    blade = sm([add(base, kn, -0.95), add(lerp(base, tip, 0.55), kn, -1.05), tip, add(lerp(base, tip, 0.7), kn, 0.95),
                add(base, kn, 0.85)], sharp=(2,), t=0.85)
    fig.part('kblade', blade, STEEL, grad=(*add(base, kn, -1), *add(tip, kn, 1), [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
             cel=0.35, rim=0.35, cast=0.6, cast_on=['npants', 'nshin'],
             details=[(ribbon([lerp(base, tip, 0.1), lerp(base, tip, 0.85)], [0.45, 0.15]).move(0.3, -0.3), STEEL.hi, 0.8)])
    # le pommeau de bois qui dépasse au-dessus du poing, côté pouce (cerclé d'une bague d'or)
    pc = H(1.2, 2.6)
    pom = ellipse(*pc, 1.25, 1.05, ang_of(a))
    fig.part('kpom', pom, WOOD, cel=0.4, rim=0.4, cast=0.5, details=[(ellipse(pc[0] + 0.3, pc[1] - 0.35, 0.45, 0.3), WOOD.hi, 0.6)])
    # le poing : dos de la main, jointures en avant, doigts repliés dessous
    body = sm([H(-0.6, -2.2), H(1.6, -2.6), H(4.2, -2.4), H(5.6, -1.2), H(5.8, 0.6), H(5.0, 2.2), H(3.0, 2.8), H(0.8, 2.6), H(-0.6, 1.8)], t=0.92)
    det = [(sm([H(0.2, -1.6), H(2.8, -2.0), H(3.6, -0.6), H(2.4, 1.2), H(0.4, 1.0)]), SKIN.hi, 0.22),
           # la rangée des jointures (le long de l'avant), le pli des doigts repliés
           (ellipse(*H(4.4, 1.6), 0.6, 0.5), SKIN.hi, 0.45), (ellipse(*H(4.9, 0.2), 0.6, 0.5), SKIN.hi, 0.4),
           (ellipse(*H(5.0, -1.2), 0.55, 0.45), SKIN.hi, 0.35),
           (ribbon([H(3.6, 2.2), H(4.6, 0.4), H(4.6, -1.6)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.5),
           (ribbon([H(5.4, 0.9), H(5.9, 0.95)], [0.25, 0.1]), SKIN.deep, 0.4),
           (ribbon([H(5.3, -0.6), H(5.8, -0.55)], [0.25, 0.1]), SKIN.deep, 0.4)]
    fig.part('nfist', body, SKIN, grad=(*H(0, 3), *H(5, -3), [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.7, rim=0.45, cast=0.8, cast_on=['kblade', 'kpom', 'npants', 'nshin', 'narm', 'seat'], details=det)
    # le pouce, replié sur le pommeau
    t0 = H(0.6, 1.8)
    th = limb([t0, H(1.0, 2.8), H(2.0, 3.0)], [2.0, 1.9, 1.6])
    fig.part('nthumb', th, SKIN, cel=0.4, rim=0.35, cast=0.5, cast_on=['nfist', 'kpom'],
             details=[(ellipse(*H(1.6, 3.0), 0.5, 0.3), SKIN.hi, 0.45)])


# ---------------------------------------------------------------- le cou
def neck(fig, P):
    sh = sm([(68.8, 57.6), (75.6, 58.4), (76.2, 62.4), (76.6, 65.4), (72.2, 66.4), (68.4, 65.6), (68.6, 61.6)], t=0.9)
    fig.part('neck', sh, SKIN, grad=(76, 58, 68, 64, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.8, rim=0.4, cast=0.8,
             cast_on=['shirt', 'vestN', 'vestF'],
             details=[(sm([(67, 57), (77, 58), (77, 61.6), (72, 62.4), (67, 61.0)]), SKIN.deep, 0.4),
                      (ribbon([(73.6, 62.4), (74.2, 64.0), (74.0, 65.6)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.4)])


# ---------------------------------------------------------------- la tête (avant l'agrandissement ×1,1)
# La boîte de la face (ovale sans cheveux ni oreille ni bandana) : les traits sont placés par ../../heros/visage.py
# (placer : œil proche, œil du fond, nez sur la médiane entre les yeux, bouche centrée sous le nez, menton sur la
# médiane, oreille). MESURES = les places réelles du dessin, contrôlées par verifier().
BOITE = (61.0, 40.0, 82.0, 62.5)
MESURES = {'oeil_proche': (70.3, 51.3, 4.2), 'oeil_fond': (78.6, 51.3, 3.5), 'nez': (74.7, 54.8), 'bouche': (74.4, 58.0, 4.5)}
FACE_PTS = [(62.6, 41.4), (71.8, 39.8), (80.4, 41.0), (82.0, 44.4), (82.4, 48.4), (82.0, 52.4), (80.8, 55.8), (78.8, 59.0),
            (76.2, 61.6), (73.6, 62.6), (71.0, 62.0), (67.6, 60.0), (64.4, 56.8), (62.2, 53.0), (61.2, 48.4), (61.4, 44.2)]
EAR_PTS = [(63.4, 49.6), (61.4, 48.8), (59.8, 49.4), (59.2, 51.4), (59.6, 54.0), (60.8, 56.2), (62.4, 57.0), (64.0, 56.4)]


def head(fig, P):
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    blink = P['blink'] > 0.5
    sq = P['sq']
    gr = P['grin']
    # la face et l'oreille : UNE forme (l'oreille soudée au crâne, la racine fondue dans la joue)
    face = fused([sm(FACE_PTS, t=0.92), sm(EAR_PTS, t=0.95)], smooth=0.7)
    fd = []
    # les plans : la tempe et la joue proches dans une ombre douce, la joue creusée sous la pommette, la tempe lointaine
    fd += [(sm([(61.0, 42.0), (64.6, 44.6), (65.6, 49.0), (67.0, 53.0), (69.6, 56.6), (72.6, 59.6), (74.6, 62.4), (70.0, 62.6),
                (66.0, 60.0), (62.4, 55.6), (60.6, 49.0)]), ('lin', 61, 50, 69, 48, [(0, SKIN.shadow, 0.55), (1, SKIN.shadow, 0)]), 1),
           (sm([(77.6, 41.0), (81.6, 41.4), (82.4, 44.6), (82.0, 46.6), (79.8, 45.4), (77.8, 43.4)]), SKIN.hi, 0.35),
           # la pommette (un méplat éclairé sous l'œil), le creux de la joue dessous (garçon maigre)
           (ellipse(70.6, 54.0, 2.4, 0.7, -8), SKIN.light, 0.4),
           (ribbon(crpath([(65.4, 54.8), (67.6, 57.0), (70.4, 58.6)], 8), swell(8, 1.2)), SKIN.shadow, 0.35),
           (ribbon(crpath([(80.6, 54.6), (79.8, 56.8), (78.4, 58.6)], 8), swell(8, 0.6)), SKIN.shadow, 0.25),
           # le menton pointu (une lumière douce), l'ombre sous la mâchoire
           (ellipse(74.4, 61.0, 1.2, 0.5), SKIN.light, 0.3),
           (sm([(69.4, 60.8), (73.6, 62.0), (78.8, 58.8), (79.4, 60.0), (75.4, 63.2), (70.4, 62.8)]),
            ('lin', 0, 60, 0, 63, [(0, SKIN.shadow, 0), (1, SKIN.shadow, 0.6)]), 1)]
    # l'ombre du bandana sur le front
    fd += [(sm([(60, 44.6), (84, 43.4), (84, 47.2), (75, 48.0), (66, 47.8), (60, 48.6)]), SKIN.deep, 0.3)]
    # l'oreille : sa conque dans l'ombre, l'ourlet éclairé, la racine fondue dans la joue (aucun trait)
    fd += [(sm([(62.6, 50.4), (61.2, 50.2), (60.6, 51.8), (61.0, 54.0), (62.0, 55.2), (62.8, 53.6), (62.2, 52.0)], t=0.9), SKIN.shadow, 0.7),
           (ribbon(crpath([(61.0, 49.4), (59.9, 51.0), (60.2, 53.8), (61.4, 55.8)], 10), swell(10, 0.5)), SKIN.hi, 0.5),
           (ellipse(63.6, 52.8, 1.0, 2.4), ('rad', 63.6, 52.8, 1.4, 2.6, [(0, SKIN.shadow, 0.35), (1, SKIN.shadow, 0)]), 1)]
    # les sourcils noirs, épais, froncés en V (ils descendent vers le nez)
    by = 0.4 * sq
    fd += [(sm([(67.2, 48.6), (68.8, 47.6), (70.8, 47.6), (72.4, 48.6 + by * 0.6), (73.2, 49.6 + by), (71.8, 49.4 + by), (70.4, 48.8),
                (68.6, 48.8)], sharp=(0, 4), t=0.85), HAIR.shadow, 1),
           (sm([(76.4, 49.6 + by), (77.0, 48.6 + by * 0.6), (78.4, 47.8), (80.2, 47.7), (81.0, 48.4), (79.8, 48.7), (78.4, 48.9),
                (77.2, 49.6 + by * 0.5)], sharp=(0, 4), t=0.85), HAIR.shadow, 1)]
    # les deux yeux : même forme (en miroir), même ligne, même regard vers la droite ; l'œil du fond un peu plus étroit
    for (ex, ey, ew), near in ((MESURES['oeil_proche'], True), (MESURES['oeil_fond'], False)):
        s = 1 if near else -1                       # le coin extérieur : à gauche (proche), à droite (fond)
        hw = ew / 2
        o_ = (ex - s * hw, ey + 0.05)              # coin extérieur
        i_ = (ex + s * hw, ey + 0.25)              # coin intérieur (vers le nez)
        top = 0.95 - 0.3 * sq
        al = [o_, (ex - s * hw * 0.4, ey - top), (ex + s * hw * 0.35, ey - top * 0.95), i_, (ex + s * hw * 0.3, ey + 0.8 - 0.15 * sq),
              (ex - s * hw * 0.4, ey + 0.75 - 0.15 * sq)]
        if not near:
            al = [al[3], al[2], al[1], al[0], al[5], al[4]]
        eye = sm(al, sharp=(0, 3), t=0.9)
        ix, iy, ir = ex + 0.55 * (hw / 2.1), ey - 0.05, 0.98 * (1 if near else 0.92)
        if blink:
            fd += [(eye.scale(1.08, 1.4, ex, ey), SKIN.base, 1),
                   (ribbon([o_, (ex, ey + 0.55), i_], [0.2, 0.55, 0.2]), EYE_INK, 0.95)]
            continue
        fd += [(eye.scale(1.1, 1.35, ex, ey), SKIN.shadow, 0.4), (eye, '#f4ece8', 1)]
        cid = fig.uid('eye')
        pup = ellipse(ix + 0.08, iy + 0.02, ir * 0.46, ir * 0.52)
        fd += [('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><path d="%s" fill="FILL"/>'
                '<path d="%s" fill="#0e0c1c"/></g>' % (cid, eye.d(), cid, ellipse(ix, iy, ir, ir * 1.05).d(), pup.d()),
                ('rad', ix + 0.25, iy + 0.45, ir * 1.25, ir * 1.25, [(0, IRIS[0]), (0.5, IRIS[1]), (1, IRIS[2])]), 1)]
        # l'ombre de la paupière sur le haut du blanc, les reflets
        fd += [(sm([al[0], al[1], al[2], al[3], lerp(al[2], (ix, iy), 0.4), lerp(al[1], (ix, iy), 0.4)], t=0.8), SKIN.deep, 0.35),
               (ellipse(ix + ir * 0.42, iy - ir * 0.36, ir * 0.3, ir * 0.26), '#ffffff', 1),
               (ellipse(ix - ir * 0.42, iy + ir * 0.42, ir * 0.13, ir * 0.11), '#ffffff', 0.6)]
        # la paupière haute, sombre et lourde (regard plissé, rusé) ; le trait du bas, fin
        lid = sm([(o_[0] - s * 0.5, o_[1] - 0.25), (ex - s * hw * 0.4, ey - top - 0.45), (ex + s * hw * 0.35, ey - top * 0.95 - 0.4),
                  (i_[0] + s * 0.2, i_[1] - 0.1), (ex + s * hw * 0.35, ey - top * 0.95 + 0.1), (ex - s * hw * 0.4, ey - top + 0.12)],
                 sharp=(0, 3), t=0.85)
        fd += [(lid, EYE_INK, 1),
               (ribbon([o_, (ex - s * hw * 0.4, ey + 0.72), (ex + s * hw * 0.3, ey + 0.78), i_], [0.1, 0.22, 0.18, 0.06]), EYE_INK, 0.45)]
    # le pli au-dessus de la paupière, la petite poche plissée sous l'œil proche (il sourit des yeux)
    fd += [(ribbon([(68.6, 49.6 + 0.2 * sq), (70.4, 49.2 + 0.25 * sq), (72.2, 49.8)], [0.1, 0.36, 0.1]), SKIN.shadow, 0.5),
           (ribbon([(68.8, 52.6), (70.4, 53.0), (72.0, 52.7)], [0.1, 0.3, 0.1]), SKIN.shadow, 0.35 + 0.2 * gr)]
    # le nez fin (sur la médiane, entre les yeux) : l'ombre côté proche, l'ombre douce dessous
    fd += [(sm([(74.0, 51.6), (74.4, 53.0), (74.4, 54.6), (73.8, 55.0), (73.4, 54.2), (73.6, 52.6)]),
            ('lin', 73.2, 53, 75, 53, [(0, SKIN.shadow, 0.45), (1, SKIN.shadow, 0)]), 1),
           (ellipse(75.0, 55.6, 1.3, 0.35, 2), SKIN.shadow, 0.4)]
    # la bouche : le sourire en coin (le coin du fond relevé), entrouverte sur les dents du haut ; une dent en moins
    # (le trou dans la rangée). Elle est centrée sous le nez, pas plus large que l'écart des yeux.
    mx, my, mw = MESURES['bouche']
    xl, xr = mx - mw / 2, mx + mw / 2
    lift = 0.7 + 0.35 * gr
    mo = sm([(xl, my + 0.25), (mx - 0.6, my - 0.35), (mx + 0.9, my - 0.55 - 0.2 * lift), (xr, my - lift), (mx + 1.0, my + 0.45 + 0.15 * gr),
             (mx - 0.7, my + 0.55)], sharp=(0, 3), t=0.85)
    cid = fig.uid('mouth')
    teeth = sm([(xl - 0.2, my - 1.2), (xr + 0.3, my - 2.2), (xr + 0.3, my + 0.05 - 0.4 * lift), (mx + 0.6, my + 0.15), (xl - 0.2, my + 0.35)],
               sharp=(0, 1, 2, 4), t=0.5)
    gap = rpoly([(mx + 0.45, my - 1.6), (mx + 1.2, my - 1.7), (mx + 1.2, my + 0.6), (mx + 0.45, my + 0.6)], 0.2)
    fd += [(mo.scale(1.12, 1.6, mx, my), SKIN.shadow, 0.35),
           (mo, LIPS[0], 1),
           ('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><path d="%s" fill="FILL"/>'
            '<path d="%s" fill="%s"/><path d="%s" fill="%s" opacity="0.5"/></g>' % (
                cid, mo.d(), cid, teeth.d(), gap.d(), '#3a0e1c', ribbon([(xl, my + 0.1), (mx, my - 0.05), (xr, my - lift + 0.2)], [0.1, 0.3, 0.1]).d(), TEETH.shadow),
            ('lin', 0, my - 1, 0, my + 0.4, [(0, TEETH.hi), (1, TEETH.base)]), 1),
           # la lèvre du haut (un trait sombre qui suit le sourire), la lèvre du bas (un méplat clair), la fossette du coin
           (ribbon([(xl - 0.15, my + 0.2), (mx - 0.6, my - 0.38), (mx + 0.9, my - 0.6 - 0.2 * lift), (xr + 0.15, my - lift - 0.05)],
                   [0.1, 0.28, 0.28, 0.12]), LIPS[0], 1),
           (ellipse(mx + 0.2, my + 1.25, 1.1, 0.3, -6), LIPS[2], 0.45),
           (ribbon([(xr + 0.2, my - lift - 0.6), (xr + 0.6, my - lift), (xr + 0.45, my - lift + 0.6)], [0.1, 0.26, 0.1]), SKIN.shadow, 0.5),
           (ribbon([(xl - 0.4, my - 0.2), (xl - 0.6, my + 0.3), (xl - 0.4, my + 0.7)], [0.1, 0.2, 0.1]), SKIN.shadow, 0.3)]
    part('face', face, SKIN, grad=(83, 41, 62, 58, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]), cel=0.8, rim=0.5, cast=1.0,
         cast_on=['hairB'], details=fd)
    # ---- le nez, fin, sur la médiane (sans contour : il est dans le visage) ; son petit bout arrondi ----
    nose = sm([(74.5, 51.4), (75.2, 51.8), (75.6, 53.4), (76.0, 54.5), (75.7, 55.1), (74.9, 55.3), (74.1, 55.0), (74.0, 54.2),
               (74.4, 52.8)], t=0.9)
    part('nose', nose, SKIN, grad=(76, 51.4, 74, 55.3, [(0, SKIN.light), (0.6, SKIN.base), (1, SKIN.base)]), cel=0, rim=0, cast=0,
         outline=False,
         details=[(ribbon([(74.9, 51.9), (75.4, 53.2), (75.6, 54.2)], [0.1, 0.28, 0.12]), SKIN.hi, 0.7),
                  (ellipse(75.4, 54.4, 0.34, 0.26), '#ffffff', 0.4),
                  (ellipse(74.5, 54.85, 0.38, 0.2, 15), SKIN.deep, 0.75)])
    # ---- la mèche de la tempe (elle sort de sous le bandana, devant l'oreille) ----
    lock = fused([taper(crpath([(63.0, 45.4), (63.6, 47.6), (63.2, 50.2)], 8), 2.6, 0.3, tip='sharp'),
                  taper(crpath([(64.8, 45.6), (65.6, 47.2), (66.0, 48.4)], 8), 1.8, 0.2, tip='sharp')], smooth=0.3)
    part('hairT', lock, HAIR, grad=(66, 45, 62, 50, [(0, HAIR.light), (1, HAIR.shadow)]), cel=0.4, rim=0.3, cast=0.6, cast_on=['face'],
         details=[(ribbon([(63.6, 45.8), (63.9, 47.6)], [0.3, 0.1]), HAIR.hi, 0.5)])
    # ---- l'anneau d'or au lobe (un fil courbe qui part du lobe et y revient : l'ouverture cachée dans le lobe) ----
    ring = limb([(61.4 + 1.05 * math.cos(math.radians(a_)), 57.6 + 1.25 * math.sin(math.radians(a_))) for a_ in range(-60, 261, 20)],
                [0.5] * 17)
    part('earring', ring, GOLD, cel=0.3, rim=0.35, cast=0.5, cast_on=['face', 'hairB', 'neck', 'shirt'],
         details=[(ellipse(62.2, 57.0, 0.28, 0.2, -30), GOLD.glint, 0.95)])
    return names


# ---------------------------------------------------------------- les cheveux de la nuque (sous le bandana)
def hair_back(fig, P):
    """Les mèches noires en bataille qui dépassent du bandana derrière l'oreille : UNE masse sous le bord du bandana,
    quelques mèches arrondies et lourdes de tailles différentes (jamais un éventail de pointes égales)."""
    core = sm([(58.6, 44.0), (64.0, 44.6), (64.6, 50.0), (64.4, 56.6), (62.6, 59.6), (60.0, 58.6), (58.6, 55.0), (58.0, 49.0)], t=0.9)
    locks = [taper(crpath([(59.6, 47.0), (57.4, 49.0), (56.0, 50.8)], 8), 3.2, 0.5, tip='round'),
             taper(crpath([(59.4, 51.4), (57.6, 53.6), (57.0, 55.8)], 8), 3.0, 0.6, tip='round'),
             taper(crpath([(60.6, 55.4), (59.6, 58.2), (60.2, 60.4)], 8), 2.6, 0.5, tip='round'),
             taper(crpath([(62.6, 57.4), (63.0, 59.6), (64.4, 61.0)], 8), 2.0, 0.4, tip='round')]
    sh = fused([core] + locks, smooth=0.4)
    det = [(ribbon(crpath([(60.2, 46.4), (58.6, 48.6), (57.4, 50.2)], 10), swell(10, 0.7)), HAIR.light, 0.6),
           (ribbon(crpath([(60.0, 51.2), (58.6, 53.4), (58.0, 55.0)], 10), swell(10, 0.6)), HAIR.light, 0.5),
           (ribbon(crpath([(61.4, 47.0), (61.6, 52.0), (61.4, 56.0)], 10), swell(10, 0.9)), HAIR.deep, 0.4)]
    fig.part('hairB', sh, HAIR, grad=(64, 44, 56, 60, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]), cel=0.9, rim=0.5,
             cast=0, details=det)
    return ['hairB']


# ---------------------------------------------------------------- le bandana rouge (calotte, nœud, deux pans)
# Le bord du bas : un morceau d'ellipse en perspective autour de la tête (au-dessus des sourcils), une seule courbe
# lisse qui file derrière la tête jusqu'au nœud.
def band_edge(n=14):
    cx, cy, R, r = 71.6, 45.4, 11.4, 1.1
    out = []
    for i in range(n + 1):
        ph = math.radians(-96 + 190 * i / n)
        out.append((cx + R * math.sin(ph), cy + r * math.cos(ph - math.radians(18)) + (0.9 * (1 - (i / 3)) if i < 3 else 0)))
    return out


def bandana_tails(fig, P):
    """Les deux pans du nœud, qui pendent derrière la nuque (ils se balancent avec `pl`)."""
    pl = P['pl']
    a = taper(crpath([(57.6, 46.6), (55.2, 50.6 + 0.3 * pl), (52.8 - 0.8 * pl, 55.0), (50.4 - 1.6 * pl, 58.6)], 14), 3.4, 2.2, tip='round', wmid=3.6)
    b = taper(crpath([(58.6, 47.4), (57.6, 51.6), (56.0 - 0.6 * pl, 56.4), (54.8 - 1.2 * pl, 60.6)], 14), 3.0, 1.8, tip='round', wmid=3.2)
    fig.part('tailA', a, RED, grad=(58, 46, 50, 59, [(0, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.4, cast=0,
             details=[(ribbon(crpath([(57.0, 48.0), (54.6, 52.2), (52.0, 56.6)], 10), swell(10, 0.6)), RED.deep, 0.4),
                      (ribbon(crpath([(56.4, 47.8), (54.0, 51.6)], 6), swell(6, 0.5)).move(0.6, -0.4), RED.light, 0.5)])
    fig.part('tailB', b, RED, grad=(59, 47, 54, 61, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.7, rim=0.45, cast=0.8,
             cast_on=['tailA'],
             details=[(ribbon(crpath([(58.0, 49.0), (57.0, 53.4), (55.6, 58.0)], 10), swell(10, 0.5)), RED.shadow, 0.5)])
    return ['tailA', 'tailB']


def bandana(fig, P):
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    edge = band_edge()
    dome = [(84.4, 44.0), (84.0, 40.2), (81.8, 36.4), (77.6, 33.6), (72.0, 32.6), (66.2, 33.4), (61.6, 35.8), (58.8, 39.4), (57.8, 43.0)]
    pts = edge[::-1][:-1] + [(59.0, 46.6)] + dome[::-1][:0] + dome[::-1][::-1][::-1][::-1]
    # (le bord du bas, de la droite vers l'arrière de la tête, puis la calotte de l'arrière vers l'avant)
    pts = edge[::-1] + [(59.4, 46.8), (58.0, 44.6)] + dome[::-1][1:][::-1][::-1]
    pts = list(edge[::-1]) + [(59.4, 46.8)] + list(reversed(dome))[0:0] + [(57.8, 43.0), (58.8, 39.4), (61.6, 35.8), (66.2, 33.4),
                                                                          (72.0, 32.6), (77.6, 33.6), (81.8, 36.4), (84.0, 40.2), (84.4, 44.0)]
    cap = sm(pts, sharp=(0, len(edge) - 1), t=0.9)
    # le bord du bas : une bande d'épaisseur égale (l'ourlet du foulard), une seule courbe
    ein = [(x, y - 1.3) for x, y in edge]
    det = [(curve_band(ein, edge, 0, 1), RED.shadow, 0.55),
           (curve_band(ein, edge, 0, 0.35), RED.light, 0.4),
           # deux plis doux tirés vers le nœud (tailles différentes), la lumière en haut à droite
           (ribbon(crpath([(79.0, 42.4), (72.0, 41.0), (65.0, 41.6), (60.0, 43.8)], 14), swell(14, 1.0)), RED.shadow, 0.45),
           (ribbon(crpath([(74.0, 36.4), (67.6, 37.4), (61.6, 40.6)], 12), swell(12, 0.8)), RED.shadow, 0.4),
           (ribbon(crpath([(70.0, 34.6), (76.6, 35.0), (81.4, 38.0), (83.2, 41.6)], 14), swell(14, 1.6)), RED.light, 0.55),
           (ribbon(crpath([(74.0, 34.2), (78.6, 35.4), (81.6, 38.2)], 12), swell(12, 0.6)), RED.hi, 0.55),
           (sm([(56, 34), (64, 34), (63, 47), (56, 47)]), ('lin', 58, 0, 65, 0, [(0, RED.shadow, 0.6), (1, RED.shadow, 0)]), 1)]
    part('cap', cap, RED, grad=(83, 34, 60, 46, [(0, RED.light), (0.45, RED.base), (1, RED.shadow)]), cel=1.0, rim=0.6, cast=1.0,
         cast_on=['face', 'hairB', 'hairT', 'nose'], details=det)
    # le nœud derrière la tête : deux lobes serrés, posé sur le bord de la calotte
    knot = fused([ellipse(58.6, 45.0, 2.6, 2.0, -30), ellipse(57.2, 46.8, 1.9, 1.6, 20)], smooth=0.4)
    part('knot', knot, RED, grad=(61, 43, 55, 48, [(0, RED.light), (0.5, RED.base), (1, RED.shadow)]), cel=0.6, rim=0.45, cast=0.9,
         cast_on=['cap', 'tailA', 'tailB', 'hairB'],
         details=[(ribbon([(57.0, 44.2), (58.2, 45.6), (59.8, 46.2)], [0.1, 0.5, 0.1]), RED.shadow, 0.6),
                  (ellipse(59.4, 44.2, 0.8, 0.5, -30), RED.hi, 0.5)])
    return names


# ---------------------------------------------------------------- le sabre d'abordage et le poing qui le serre
def saber(fig, P):
    """Dessiné au repos (poing en F0, lame à SA0), puis posé par GM. Le poing est vu côté paume : les doigts repliés
    autour de la poignée, le pouce couché dessus vers la coquille ; la branche de garde passe derrière le poing."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)
    L = saber_frame(F0, SA0)
    # la branche de garde (derrière le poing) : de la coquille au pommeau, en arc du côté des jointures
    bow = limb([L(4.0, 2.6), L(3.0, 4.0), L(0.0, 4.6), L(-3.0, 4.0), L(-4.6, 2.0), L(-5.0, 0.6)], [0.95, 1.05, 1.1, 1.05, 1.0, 0.95])
    part('bow', bow, GOLD, cel=0.4, rim=0.4, cast=0.5, details=[(ribbon([L(3.0, 3.6), L(0.0, 4.1), L(-3.0, 3.6)], [0.1, 0.35, 0.1]), GOLD.hi, 0.7)])
    # la lame courbe : le dos (v < 0) et le tranchant (v > 0) ; elle s'élargit vers la pointe, qui remonte vers le dos
    n = 20
    back, edge_ = [], []
    for i in range(n + 1):
        t = i / n
        u = 4.2 + 30.0 * t
        bend = -2.6 * t * t                                         # la courbe : la lame se cambre vers le dos
        w = 1.9 + 1.6 * t ** 1.3
        back.append(L(u, bend - 0.9))
        edge_.append(L(u, bend - 0.9 + w))
    tip = L(36.0, -2.6 - 1.2)
    blade = sm([L(3.6, -1.0)] + back[1:] + [tip] + edge_[::-1][:-1] + [L(3.6, 1.2)], sharp=(n + 1,), t=0.85)
    # le tranchant affûté (une bande claire le long du bord bas), la gouttière le long du dos, les reflets
    fil = sm(edge_ + [tip] + [lerp(a, b, 0.62) for a, b in zip(back, edge_)][::-1], t=0.85)
    det = [(fil, STEEL.light, 0.6),
           (ribbon([lerp(back[i], edge_[i], 0.25) for i in (2, 8, 14, 18)], [0.1, 0.3, 0.3, 0.1]), STEEL.shadow, 0.7),
           (ribbon([lerp(back[i], edge_[i], 0.8) for i in (3, 9, 15, 19)], [0.1, 0.35, 0.3, 0.1]), STEEL.hi, 0.9),
           (ellipse(*lerp(back[16], edge_[16], 0.6), 1.4, 0.35, SA0 - 8), '#ffffff', 0.8)]
    part('blade', blade, STEEL, grad=(*L(20, -2), *L(14, 4), [(0, STEEL.light), (0.5, STEEL.base), (1, STEEL.shadow)]),
         cel=0.5, rim=0.45, cast=0.6, details=det)
    # le bout de la poignée de cuir et le pommeau d'or (sous le talon de la main)
    grip = limb([L(-2.0, 0.2), L(-4.4, 0.4)], [2.0, 1.9])
    part('grip', grip, LEATHER, cel=0.4, rim=0.3, cast=0.4,
         details=[(ribbon([L(-2.6, -0.6), L(-3.0, 0.9)], [0.25, 0.25]), LEATHER.deep, 0.6)])
    pom = ellipse(*L(-5.0, 0.5), 1.25, 1.1, SA0)
    part('pommel', pom, GOLD, cel=0.4, rim=0.4, cast=0.5, details=[(ellipse(*L(-4.8, 0.1), 0.45, 0.32), GOLD.glint, 0.8)])
    # le poing : vu côté paume, les quatre doigts repliés autour de la poignée (trois plis courts, pas de rayons)
    body = sm([L(-3.2, -2.5), L(0.0, -2.8), L(2.8, -2.5), L(3.6, -0.6), L(3.4, 1.6), L(2.4, 3.0), L(0.0, 3.3), L(-2.4, 3.1),
               L(-3.6, 2.0), L(-3.8, -0.6)], t=0.92)
    det = [(sm([L(-2.2, -2.0), L(1.8, -2.2), L(2.4, -0.6), L(-1.8, -0.2)]), SKIN.hi, 0.2),
           # les doigts repliés (vus de face) : trois plis courts entre eux, les bouts arrondis du côté du pouce
           (ribbon([L(1.6, 0.4), L(1.7, 1.8), L(1.4, 3.0)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.55),
           (ribbon([L(-0.3, 0.6), L(-0.2, 2.0), L(-0.4, 3.1)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.55),
           (ribbon([L(-2.1, 0.6), L(-2.1, 1.9), L(-2.3, 2.9)], [0.1, 0.35, 0.1]), SKIN.shadow, 0.5),
           (ribbon([L(-3.2, 0.2), L(0.0, 0.0), L(3.0, 0.2)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.35),
           (ellipse(*L(2.4, 1.5), 0.55, 0.45), SKIN.hi, 0.35), (ellipse(*L(0.6, 1.7), 0.55, 0.45), SKIN.hi, 0.3),
           (ellipse(*L(-1.2, 1.7), 0.5, 0.42), SKIN.hi, 0.3)]
    part('ffist', body, SKIN, grad=(*L(3, -3), *L(-3, 3), [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]), cel=0.7,
         rim=0.45, cast=0.8, cast_on=['bow', 'grip', 'pommel', 'farm'], details=det)
    # le pouce, couché le long de la poignée, le bout contre la coquille
    th = limb([L(-1.8, -1.6), L(0.6, -2.0), L(2.6, -1.4)], [2.3, 2.0, 1.7])
    part('fthumb', th, SKIN, cel=0.45, rim=0.35, cast=0.55, cast_on=['ffist'],
         details=[(ellipse(*L(2.0, -1.8), 0.7, 0.3, SA0), SKIN.hi, 0.5)])
    # la coquille d'or (une coupe vue de côté, entre le poing et la lame)
    shell = sm([L(3.4, -3.0), L(4.6, -2.6), L(5.0, 0.2), L(4.6, 3.6), L(3.6, 4.2), L(3.0, 3.4), L(3.6, 0.2), L(3.0, -2.2)], t=0.9)
    part('shell', shell, GOLD, grad=(*L(5, -3), *L(3, 4), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.5, rim=0.45,
         cast=0.6, cast_on=['ffist', 'fthumb', 'blade', 'bow'],
         details=[(ribbon([L(4.5, -2.0), L(4.8, 0.6), L(4.4, 3.2)], [0.1, 0.4, 0.1]), GOLD.hi, 0.8),
                  (ellipse(*L(4.4, -1.4), 0.4, 0.3), GOLD.glint, 0.9)])
    return names


def main():
    """matelot.svg (grand) et matelot-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-barzul-rapide.webp (512 px de haut) et mon-barzul-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('matelot', 0.95, 512, ID_JEU), ('matelot-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
