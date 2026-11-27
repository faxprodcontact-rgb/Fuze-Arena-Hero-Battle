# Le Diablotin (monstre RAPIDE du clan de Lenore, feu ; dessin du jeu « mon-lenore-rapide ») redessiné en VECTORIEL
# lisse, dans le style moderne de l'interface (refonte des monstres du 27/11/2026, sur le modèle des héros validés :
# ../../heros/kael/kael.py, ../../heros/oboro/oboro.py pour le clan, ../../heros/gribou/gribou.py pour le squelette).
#
#   python3 refonte-graphique/ui-moderne/monstres/diablotin/diablotin.py   # → diablotin.svg + images 512 et 160 px
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/diablotin.txt) : un petit diablotin oni, espiègle
# et vicieux, trois quarts vers la droite, qui bondit sur la pointe des pieds (jambe proche en arrière qui pousse,
# jambe lointaine en avant, talons levés, genoux pliés vers l'avant). Grosse tête large en haut, menton pointu, une
# seule petite corne d'ivoire au milieu du front, houppe de crinière noir-bleuté en trois mèches rabattues vers
# l'arrière, deux grandes oreilles pointues soudées au crâne (la proche immense, anneau d'or au lobe ; la lointaine en
# pointe derrière le front), sourcils froncés en V, gros yeux jaunes tournés vers l'ennemi, petit nez discret, grand
# sourire en croissant plein de dents pointues (gueule de monstre voulue : les dents partent des gencives). Corps sec,
# ventre rond, petit croc d'ivoire en pendentif, pagne en peau de tigre (deux marques seulement) serré par une
# cordelette nouée côté lointain. Bras proche replié, coude bas, le poing (bracelet d'or) serre un petit kanabō de fer
# armé vers l'arrière ; bras lointain tendu vers l'ennemi, main ouverte en griffes d'ivoire. Anneau d'or à la cheville
# lointaine, griffes d'ivoire aux orteils, longue queue fine terminée en fer de pique.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au
# même endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; chaque membre est
# d'un seul tenant (pas de couture au coude ni au genou) et tourne autour des vraies jointures (ik) ; l'épaule proche
# se fond dans le buste (FigureM, méthode d'Aurelle) ; le visage est placé par ../../heros/visage.py.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.join(HERE, '..', '..', 'heros')
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Mat, sm, lock, limb, ribbon, ellipse, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import crpath, taper, ik, Seg, inv, round_limb, FigureM, poly_of, shape_of, rot, lerp  # noqa: E402
from visage import placer, verifier  # noqa: E402
from lib import Shape  # noqa: E402,F401
from shapely.geometry import Point, box  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-lenore-rapide'         # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffae66', '#f06c38', '#d4462a', '#962638', '#541430')          # rouge-orangé, plus chaud que Lenore
HOT = Mat('#fff0a0', '#ffb24a', '#f2701a', '#b8361e', '#6a1424')            # la peau qui rougeoie (spéciale)
HAIR = Mat('#9284c4', '#625684', '#3e3258', '#2a2040', '#1a1328')           # crinière noir-bleuté
IVORY = Mat('#fffcee', '#f6ead0', '#e2cfac', '#a88c7e', '#5e4248')
GOLD = Mat('#fff4b4', '#f8c640', '#d8961e', '#8e5216', '#5a2c0e', glint='#ffffff')
TIGER = Mat('#ffd885', '#f4a83c', '#d88026', '#9a4a18', '#5a2a12')
ROPE = Mat('#fff0bc', '#ecd08a', '#b48a48', '#6a4426', '#3e2616')
IRON = Mat('#d6dcee', '#9098b6', '#5e6486', '#383c5a', '#22223a', glint='#ffffff')
STRIPE = '#3a1a20'
EYE_Y, EYE_K, PUPIL = '#ffe04a', '#c8801a', '#1a0810'
EYEINK = '#2a0a1c'
GORGE, GUM, TONGUE = '#4c0e22', '#8a1c2c', '#c83c4c'
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']

GRD = 116.0        # le sol (le point « sol » du pixel art)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (28.0, 43.0, 78.0, 76.0)

# ---------- le squelette (pose de repos, pixels du dessin, y vers le bas) ----------
HIP = (69.0, 100.0)                       # le pivot du buste (il se penche depuis les hanches)
NECK = (74.0, 84.5)                       # le pivot (et le centre d'agrandissement ×1,1) de la tête
HIP_N, HIP_F = (62.6, 101.0), (77.2, 101.0)
ANK_N, ANK_F = (54.8, 111.4), (79.4, 110.4)
BALL_N, BALL_F = (57.8, 115.1), (82.6, 115.1)          # la plante du pied (sur la pointe : talon levé)
SH_N, SH_F = (62.4, 88.0), (84.6, 88.6)                # les épaules
G0 = (49.6, 84.6)                         # le milieu du poing proche (le manche de la massue le traverse)
ANG0 = 201.0                              # la massue : du poing vers sa tête (degrés, repère de l'écran, y vers le bas)
WR_F0 = (92.2, 88.6)                      # le poignet lointain (main ouverte)
TAIL_R = (59.0, 102.4)                    # la racine de la queue
L_TN, L_SN = 7.4, 7.0                     # cuisse et jambe (proche)
L_TF, L_SF = 5.4, 5.0
L_UN, L_FN = 13.0, 8.0                    # bras et avant-bras (proche)
L_UF, L_FF = 5.8, 5.2

# Une pose = ces réglages ; REST est la pose du dessin.
#   shift / lift : tout le diablotin se déplace (bonds) ; crouch : il se tasse (les pieds restent au sol, les genoux
#   plient) ; lean : il se penche (degrés, + vers l'ennemi, depuis les hanches) ; breath : souffle 0..1 ; head :
#   décalage de la tête ; tilt : la tête penche ; G : le poing proche (repère du buste) ; ang : la massue ;
#   fh : décalage de la main lointaine ; fa : la main lointaine tourne ; fN / fF : décalage des pieds (en l'air) ;
#   q : la queue se balance (+ : le bout monte) ; qc : elle se recourbe ; en / ef : les oreilles frémissent (degrés) ;
#   pg : le bas du pagne se balance ; blink : yeux fermés ; eyes : les yeux s'allument (0..1) ; heat : la peau
#   rougeoie (0..1) ; hot : le fer de la massue chauffe au rouge (0..1).
REST = dict(shift=0.0, lift=0.0, crouch=0.0, lean=0.0, breath=0.0, head=(0.0, 0.0), tilt=0.0, G=G0, ang=ANG0,
            fh=(0.0, 0.0), fa=0.0, fN=(0.0, 0.0), fF=(0.0, 0.0), q=0.0, qc=0.0, en=0.0, ef=0.0, pg=0.0, blink=0.0,
            eyes=0.0, heat=0.0, hot=0.0)

# ---------- le visage (../../heros/visage.py : la même sphère pour tous, 3/4 léger tourné vers la droite) ----------
FACE_BOX = (56.5, 57.5, 84.5, 84.5)       # l'ovale de la face (sans les oreilles, la corne ni la crinière)
FACE_V = placer(FACE_BOX, l_oeil=0.24)    # de gros yeux (comme le pixel art)
fig_face = {}


def MS(M, shape):
    return shape.map(lambda p: mapp(M, p))


def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def heated(m, k):
    """La matière de la peau qui rougeoie (k de 0 à 1)."""
    if k <= 0.001:
        return m
    return Mat(*(hexmix(a, b, k) for a, b in ((m.hi, HOT.hi), (m.light, HOT.light), (m.base, HOT.base),
                                               (m.shadow, HOT.shadow), (m.deep, HOT.deep))))


def iron_of(k):
    if k <= 0.001:
        return IRON
    H = Mat('#fff6c8', '#ffb04a', '#e0521e', '#8a2018', '#4a1020', glint='#ffffff')
    return Mat(*(hexmix(a, b, k) for a, b in ((IRON.hi, H.hi), (IRON.light, H.light), (IRON.base, H.base),
                                               (IRON.shadow, H.shadow), (IRON.deep, H.deep))), glint='#ffffff')


# ---------- morceaux dessinés dans un repère local ----------


def foot_shape(A, B, near=True):
    """Le pied d'oni sur la pointe : talon levé derrière la cheville A, cou-de-pied qui descend jusqu'à la plante B
    (au sol), orteils couchés vers l'avant. Une seule forme (la jambe la recouvre à la cheville)."""
    u = Seg(A, B)
    k = 1.0 if near else 0.92
    toe = (B[0] + 3.6 * k, B[1] + 0.6)
    # (Seg : b > 0 = du côté du cou-de-pied, en haut à droite ; b < 0 = le talon et la plante)
    pts = [u(-0.4, 1.45), u(-1.7, 0.4), u(-1.7, -1.0), u(0.2, -1.55), u(u.L * 0.55, -1.4), (B[0] - 0.2, B[1] + 0.85),
           (toe[0] - 0.9, toe[1] + 0.45), (toe[0] + 0.2, toe[1] - 0.2), (toe[0] - 0.5, toe[1] - 1.5),
           (B[0] + 0.6, B[1] - 1.7), u(u.L * 0.6, 1.5), u(u.L * 0.2, 1.5)]
    return sm(pts, sharp=(), t=0.9), toe


def band(c, ax, w, th=1.1, sag=0.35):
    """Un anneau (bracelet, anneau de cheville) vu de côté : une bande courbe qui traverse le membre d'un bord à
    l'autre en passant devant (un peu plus bas au milieu) ; ax = la direction du membre (degrés)."""
    a = math.radians(ax)
    v = (math.cos(a), math.sin(a))
    n = (-v[1], v[0])
    pts = [(c[0] + n[0] * w * t + v[0] * sag * (1 - t * t), c[1] + n[1] * w * t + v[1] * sag * (1 - t * t)) for t in (-1, -0.5, 0, 0.5, 1)]
    return ribbon(pts, [th * 0.8, th, th, th, th * 0.8], sharp_ends=False), pts


def claws_at(toe, ang=0.0, k=1.0, n=2):
    """Les griffes d'ivoire au bout des orteils : de petits crochets qui pointent vers l'avant."""
    out = []
    for j in range(n):
        x, y = toe[0] - 1.1 * j, toe[1] - 0.2 + 0.9 * j
        pts = [(x - 0.4, y - 1.0), (x + 1.2 * k, y - 0.6), (x + 2.0 * k, y + 0.5), (x + 0.6, y + 0.4)]
        out.append(sm([rot((p[0] - toe[0], p[1] - toe[1]), ang) for p in pts], sharp=(2,), t=0.7)
                   .move(toe[0], toe[1]))
    return out


def fist_shape(G, deg):
    """Le poing proche serré sur le manche (le manche le traverse dans l'axe de la massue) : un bloc arrondi, les
    doigts repliés vers nous. Repère : G le milieu du poing, la massue part vers `deg`."""
    loc = [(-2.6, -2.4), (-0.4, -2.9), (2.0, -2.6), (3.1, -1.0), (3.0, 1.4), (1.6, 2.9), (-0.8, 3.0), (-2.6, 2.0),
           (-3.1, 0.0)]
    return sm([(G[0] + p[0], G[1] + p[1]) for p in (rot(q, deg - 180.0) for q in loc)], t=0.95)


# ---------- le petit kanabō (repère : G le poing, u vers la tête de la massue, n en travers) ----------


def club(G, deg):
    a = math.radians(deg)
    u = (math.cos(a), math.sin(a))
    n = (-u[1], u[0])
    C = lambda s, t: (G[0] + u[0] * s + n[0] * t, G[1] + u[1] * s + n[1] * t)
    # le manche de fer (du bout caché dans le poing au collier d'or)
    handle = sm([C(-3.4, -0.9), C(5.0, -0.85), C(5.0, 0.85), C(-3.4, 0.9)], sharp=(0, 1, 2, 3), t=0.6)
    collar = sm([C(4.2, -1.3), C(5.6, -1.85), C(6.4, -1.95), C(6.4, 1.95), C(5.6, 1.85), C(4.2, 1.3)], sharp=(2, 3), t=0.7)
    # la tête de fer à pans qui s'élargit jusqu'au bout plat ; les clous du bord dépassent (des bosses du contour)
    top, bot = [], []
    for s in [6.2 + i * 0.5 for i in range(24)]:
        w = 2.4 + 0.9 * (s - 6.2) / 11.5
        top.append([s, -w])
        bot.append([s, w])
    for s0, side in ((8.6, -1), (11.6, 1), (14.4, -1), (9.8, 1), (13.0, -1), (16.0, 1)):
        for p in (top if side < 0 else bot):
            d = abs(p[0] - s0)
            if d < 0.75:
                p[1] += side * 0.9 * (1 - (d / 0.75) ** 2)
    head = sm([C(*p) for p in top] + [C(17.9, -3.3), C(18.2, 0.0), C(17.9, 3.3)] + [C(*p) for p in bot[::-1]], t=0.8)
    return C, u, n, handle, collar, head


# ======================================================================== le dessin


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    br = P['breath']
    S = heated(SKIN, 0.3 * P['heat'])           # la peau rougeoie sans perdre son rouge
    SF = Mat(*(hexmix(c, '#3a1030', 0.16) for c in (S.hi, S.light, S.base, S.shadow, S.deep)))   # côté du fond
    IR = iron_of(P['hot'])

    # ---- le squelette : une matrice par groupe de morceaux ----
    ROOTM = mT(P['shift'], -P['lift'])
    PEL = mchain(ROOTM, mT(0, P['crouch']))
    U = mchain(PEL, mT(P['lean'] * 0.2, 0), mR(P['lean'], *HIP))            # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.5 * br))                                         # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.01 * br, 1 + 0.025 * br, 72, 98))               # le ventre se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))   # tête un peu plus grande (×1,1)
    PAG = mchain(PEL, mskx(-0.06 * P['pg'], 96))

    # ---- les jambes : les hanches suivent le bassin, les pieds restent où on les pose ----
    def foot_t(A0, off):
        return (A0[0] + P['shift'] + off[0], A0[1] - P['lift'] + off[1])
    hipN, hipF = mapp(PEL, HIP_N), mapp(PEL, HIP_F)
    aN0, aF0 = foot_t(ANK_N, P['fN']), foot_t(ANK_F, P['fF'])
    kN, aN = ik(hipN, aN0, L_TN, L_SN, -1)
    kF, aF = ik(hipF, aF0, L_TF, L_SF, -1)
    # la plante : au sol quand le pied y est ; en l'air, le pied pend (pointe vers le bas)
    def ball(A0, A, B0):
        up = max(0.0, (A0[1] - P['lift']) - A[1]) + P['lift']
        d = (B0[0] - A0[0], B0[1] - A0[1])
        return (A[0] + d[0], A[1] + d[1]) if up < 0.5 else (A[0] + d[0] * 0.75 + 0.6, A[1] + d[1] * 1.12 + 0.4)
    bN, bF = ball(ANK_N, aN, BALL_N), ball(ANK_F, aF, BALL_F)

    # ================================================================ du fond vers le devant
    # ---- la longue queue fine et son fer de pique (une seule forme), derrière tout ----
    q, qc = P['q'], P['qc']
    tr = mapp(PEL, TAIL_R)
    tpts = [(59.0, 102.4), (54.6, 104.6), (48.6, 105.4), (43.0, 104.4), (39.0, 101.6), (36.6, 98.0), (35.6, 95.0)]
    tpts = [rot((p[0] - 59.0, p[1] - 102.4), -q * 9.0 * (i / 6) ** 1.3) for i, p in enumerate(tpts)]
    tpts = [(tr[0] + p[0], tr[1] + p[1]) for p in tpts]
    tpts = tpts[:4] + [(p[0] + qc * 1.2 * (i + 1), p[1] - qc * 0.8 * (i + 1)) for i, p in enumerate(tpts[4:])]
    tc = crpath(tpts, 40)
    tail = taper(tc, 2.6, 1.7, tip='round')
    tip = tc[-1]
    d = (tc[-1][0] - tc[-4][0], tc[-1][1] - tc[-4][1])
    ta = math.degrees(math.atan2(d[1], d[0]))
    # le fer de pique : une pointe en haut, deux barbes arrondies en bas (en forme de coeur pointu), le bout de la
    # queue entre dans son creux du bas
    sp = [(0.6, 0.0), (-0.6, -1.6), (-1.4, -3.4), (0.8, -3.3), (3.2, -2.5), (5.6, -1.2), (7.6, 0.0), (5.6, 1.2),
          (3.2, 2.5), (0.8, 3.3), (-1.4, 3.4), (-0.6, 1.6)]
    spade = sm([(tip[0] + p[0], tip[1] + p[1]) for p in (rot(v, ta) for v in sp)], sharp=(2, 6, 10), t=0.85)
    from shapely.geometry import box as _box  # noqa: F401
    g = poly_of(tail).union(poly_of(spade))
    g = g.union(g.buffer(0.9, 32, join_style=1).buffer(-0.9, 32, join_style=1))
    tailsh = shape_of(g, step=0.4, t=0.8)
    sc = (tip[0] + 4.0 * math.cos(math.radians(ta)), tip[1] + 4.0 * math.sin(math.radians(ta)))
    fig.part('tail', tailsh, S, grad=(tr[0] + 2, tr[1] - 8, sc[0] - 3, sc[1] + 6, [(0, S.light), (0.5, S.base), (1, S.shadow)]),
             cel=0.8, rim=0.5, cast=0.6,
             details=[(taper(crpath(tpts[1:6], 20), 0.5, 0.2, tip='sharp').move(0.3, -0.7), S.hi, 0.45),
                      (ribbon([(sc[0] - 2.6, sc[1] - 1.6), (sc[0] + 0.4, sc[1] - 2.4), (sc[0] + 3.0, sc[1] - 0.8)], [0.1, 0.7, 0.1]), S.hi, 0.6)])

    # ---- la jambe lointaine (en avant), son pied sur la pointe, l'anneau d'or à la cheville ----
    def leg(pre, hip, kn, an, b, M, near):
        """La jambe et son pied : UNE seule forme (cuisse, genou, jambe, cheville, pied), la cheville arrondie par un
        creux doux ; le genou plie vers l'avant."""
        w0, w1, w2 = (4.6, 3.1, 2.4) if near else (4.2, 2.9, 2.2)
        fsh, toe = foot_shape(an, b, near)
        lg = round_limb([hip, kn, an], [(0, w0 / 2, w0 / 2), (0.45, w1 / 2 * 1.08, w1 / 2 * 1.08), (0.6, w1 / 2, w1 / 2), (1, w2 / 2, w2 / 2)], n=22)
        gl = poly_of(lg).union(poly_of(fsh))
        gl = gl.union(gl.buffer(1.0, 32, join_style=1).buffer(-1.0, 32, join_style=1).intersection(Point(an).buffer(3.2, 32)))
        sh = shape_of(gl, step=0.35, t=0.85)
        t1, t2 = Seg(hip, kn), Seg(kn, an)
        det = [(ribbon([t1.at(0.25, 0.9), t1.at(0.75, 1.0), t2.at(0.3, 0.8), t2.at(0.8, 0.6)], [0.1, 0.6, 0.5, 0.1]), M.hi, 0.4),
               (ribbon([lerp(an, b, 0.35), lerp(an, b, 0.8), (b[0] + 2.2, b[1] - 1.1)], [0.1, 0.55, 0.1]), M.hi, 0.45),
               (ribbon([(b[0] - 1.0, b[1] + 0.7), (toe[0] - 0.6, toe[1] + 0.3)], [0.4, 0.2]), M.deep, 0.5),
               (ellipse(kn[0] + 0.4, kn[1] - 0.2, 1.1, 0.8), M.light, 0.3)]
        fig.part(pre + 'leg', sh, M, grad=(kn[0] + 3, hip[1], hip[0] - 3, b[1] + 1, [(0, M.light), (0.5, M.base), (1, M.shadow)]),
                 cel=0.8, rim=0.5, cast=0.8, details=det)
        for j, c in enumerate(claws_at(toe, 8.0, 1.0 if near else 0.9)):
            fig.part('%sclaw%d' % (pre, j), c, IVORY, cel=0.25, rim=0.3, cast=0.35, cast_on=[pre + 'leg'])
    leg('F', hipF, kF, aF, bF, SF, False)
    s2 = Seg(kF, aF)
    ank = s2.at(0.9)
    anklet, ap = band(ank, math.degrees(math.atan2(s2.u[1], s2.u[0])), 1.55, 1.45)
    fig.part('anklet', anklet, GOLD, cel=0.3, rim=0.4, cast=0.5, cast_on=['Fleg'],
             details=[(ribbon(ap[2:], [0.3, 0.4, 0.1]), GOLD.glint, 0.75)])
    # ---- la jambe proche (en arrière, elle pousse) ----
    leg('N', hipN, kN, aN, bN, S, True)

    # ---- le bras lointain, tendu vers l'ennemi : sa racine passe derrière le buste ; la main ouverte en griffes ----
    shF = mapp(UC, SH_F)
    wF0 = mapp(UC, (WR_F0[0] + P['fh'][0], WR_F0[1] + P['fh'][1]))
    eF, wF = ik(shF, wF0, L_UF, L_FF, +1)
    farm = round_limb([shF, eF, wF], [(0, 1.7, 1.7), (0.5, 1.45, 1.45), (0.6, 1.35, 1.35), (1, 1.15, 1.15)], n=18)
    fig.part('farm', farm, SF, grad=(wF[0], wF[1] - 3, shF[0], eF[1] + 2, [(0, SF.light), (0.5, SF.base), (1, SF.shadow)]),
             cel=0.6, rim=0.45, cast=0.6)
    # la main : la paume (un peu de face, tournée vers l'ennemi), trois doigts écartés et le pouce, griffes d'ivoire
    fa = P['fa'] + math.degrees(math.atan2(wF[1] - eF[1], wF[0] - eF[0])) * 0.3 - 8
    H_ = lambda x, y: (wF[0] + rot((x, y), fa)[0], wF[1] + rot((x, y), fa)[1])
    palm = sm([H_(-0.8, -1.4), H_(1.4, -2.0), H_(2.8, -1.6), H_(3.4, 0.2), H_(2.8, 1.8), H_(0.8, 2.0), H_(-0.9, 1.2)])
    fingers = [((2.6, -1.6), (4.2, -4.6), (4.6, -6.0), 1.15), ((3.2, -0.4), (5.6, -2.2), (6.6, -3.2), 1.2),
               ((3.2, 1.0), (5.8, 0.6), (7.0, 0.2), 1.1)]
    g = poly_of(palm)
    tips = []
    for a, b, c, w in fingers:
        fsh = limb(crpath([H_(*a), H_(*b), H_(*c)], 8), [w, w * 0.85], n=8)
        g = g.union(poly_of(fsh))
        tips.append((H_(*b), H_(*c)))
    thumb = limb(crpath([H_(0.2, -1.4), H_(0.6, -3.4), H_(1.4, -4.6)], 8), [1.2, 1.0], n=8)
    g = g.union(poly_of(thumb))
    tips.append((H_(0.6, -3.4), H_(1.4, -4.6)))
    g = g.union(g.buffer(0.45, 32, join_style=1).buffer(-0.45, 32, join_style=1))
    hand = shape_of(g, step=0.3, t=0.8)
    fig.part('fhand', hand, SF, grad=(wF[0] + 6, wF[1] - 5, wF[0] - 1, wF[1] + 2, [(0, SF.light), (0.5, SF.base), (1, SF.shadow)]),
             cel=0.5, rim=0.4, cast=0.5, cast_on=['farm'],
             details=[(ellipse(*H_(1.4, 0.0), 1.4, 1.1, fa), SF.shadow, 0.45)])
    for j, (b, c) in enumerate(tips):
        da = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]))
        cw = [rot(v, da) for v in ((-0.6, -0.55), (0.9, -0.5), (2.2, 0.2), (0.4, 0.6))]
        fig.part('fclaw%d' % j, sm([(c[0] + v[0], c[1] + v[1]) for v in cw], sharp=(2,), t=0.7), IVORY,
                 cel=0.2, rim=0.3, cast=0.3, cast_on=['fhand'])

    # ---- le buste : corps sec, épaules étroites, ventre rond (le dôme de l'épaule proche fait partie du buste) ----
    torso0 = sm([(69.0, 83.4), (65.6, 84.8), (62.8, 86.6), (61.2, 89.0), (60.8, 92.0), (61.0, 95.0), (61.2, 98.0),
                 (62.6, 100.6), (70.0, 101.4), (78.6, 100.8), (83.4, 98.8), (86.0, 95.8), (86.6, 92.6), (86.0, 89.6),
                 (84.8, 87.2), (82.8, 85.2), (79.6, 83.6), (75.0, 83.0)], t=0.95)
    Sn = mapp(inv(TOR), mapp(UC, SH_N))
    tg0 = poly_of(torso0)
    u_ = tg0.union(Point(Sn).buffer(2.2, 48))
    cl = u_.buffer(3.0, 48, join_style=1).buffer(-3.0, 48, join_style=1)
    from shapely.geometry import box
    tg = u_.union(cl.intersection(box(Sn[0] - 6, Sn[1] - 6, Sn[0] + 6, Sn[1] + 1.5)))
    torso = shape_of(tg, step=0.5, t=0.9)
    zoneN = shape_of(tg.intersection(Point(Sn).buffer(5.0, 48)), step=0.4)
    td = [(torso, ('lin', 60, 94, 70, 94, [(0, S.deep, 0.45), (1, S.deep, 0)]), 1)]
    # la poitrine sèche : deux petits pectoraux doux (le proche plus large), le creux du sternum
    td += [(sm([(63.0, 87.4), (68.4, 86.2), (73.0, 87.0), (72.6, 90.2), (67.6, 91.0), (63.4, 90.2)]), S.light, 0.35),
           (ribbon([(63.2, 90.6), (67.8, 91.6), (72.8, 90.6)], [0.1, 0.9, 0.1]), S.shadow, 0.6),
           (sm([(75.4, 86.6), (80.6, 85.8), (84.6, 87.4), (84.2, 90.2), (80.0, 90.8), (75.6, 90.0)]), S.hi, 0.3),
           (ribbon([(75.6, 90.4), (79.8, 91.2), (84.0, 90.4)], [0.1, 0.8, 0.1]), S.shadow, 0.55),
           (ribbon([(74.2, 85.0), (74.0, 88.0), (74.2, 90.6)], [0.1, 0.8, 0.1]), S.shadow, 0.45)]
    # le ventre rond : le gros du ventre éclairé à droite, l'ombre dessous, le nombril
    td += [(ellipse(77.4, 95.8, 7.6, 4.6, -8), ('rad', 80.0, 93.6, 7.0, 7.0, [(0, S.hi, 0.6), (0.6, S.light, 0.25), (1, S.light, 0)]), 1),
           (ribbon([(65.4, 98.2), (72.0, 100.2), (79.0, 99.8), (84.0, 97.2)], [0.1, 1.2, 1.1, 0.1]), S.shadow, 0.55),
           (ellipse(77.0, 96.2, 0.6, 0.45), S.deep, 0.6)]
    # le cou (court, sous le menton), le côté proche du buste dans l'ombre
    td += [(sm([(69.6, 83.2), (75.0, 82.8), (79.8, 83.6), (78.0, 86.2), (74.0, 86.8), (70.4, 86.0)]), S.shadow, 0.45),
           (sm([(60.8, 91.6), (62.8, 92.6), (63.4, 96.0), (62.8, 99.6), (61.2, 98.4), (61.0, 95.0)]), S.shadow, 0.4)]
    xa, ya, xb, yb = torso0.bbox()
    fig.part('torso', torso, S, grad=(xb, ya, xa + (xb - xa) * 0.25, yb, [(0, S.light), (0.5, S.base), (1, S.shadow)]),
             cel=1.1, rim=0.65, cast=0.9, details=td, occl=(S.deep, 0.2, 2.2))

    # ---- le pendentif : une cordelette autour du cou (un morceau d'ellipse en perspective), un petit croc d'ivoire ----
    # (ses deux bouts remontent derrière le menton : le collier passe derrière le cou)
    cord_pts = [(74.4 + 7.4 * math.cos(math.radians(a)), 82.4 + 5.8 * math.sin(math.radians(a)))
                for a in [178 - 176 * i / 24 for i in range(25)]][::-1]
    cordc = cord_pts
    pend = cordc[13]
    # coupée par le buste : ses deux bouts disparaissent derrière la base du cou
    cord = shape_of(poly_of(ribbon(cordc, [0.75] * len(cordc), sharp_ends=False)).intersection(poly_of(torso0)), step=0.3, t=0.7)
    fig.part('cord', cord, ROPE, cel=0.2, rim=0.25, cast=0.5, cast_on=['torso'], outline=False,
             details=[(ribbon([(x, y - 0.15) for x, y in cordc[3:-3]], [0.1] + [0.3] * (len(cordc) - 8) + [0.1]), ROPE.hi, 0.6)])
    pf = sm([(pend[0] - 0.9, pend[1] + 0.2), (pend[0] + 0.9, pend[1] + 0.2), (pend[0] + 0.7, pend[1] + 2.0),
             (pend[0] - 0.1, pend[1] + 4.2), (pend[0] - 0.6, pend[1] + 2.4)], sharp=(3,), t=0.8)
    fig.part('fang', pf, IVORY, cel=0.3, rim=0.35, cast=0.6, cast_on=['torso'],
             details=[(ribbon([(pend[0] + 0.3, pend[1] + 0.6), (pend[0] + 0.25, pend[1] + 2.2), (pend[0] - 0.05, pend[1] + 3.6)], [0.25, 0.25, 0.05]), IVORY.hi, 0.8)])
    fig.part('fknot', ellipse(pend[0], pend[1] + 0.1, 1.0, 0.75), ROPE, cel=0.2, rim=0.3, cast=0.4, cast_on=['fang', 'torso'])

    # ---- le pagne en peau de tigre (plus long devant, bas en touffes), la cordelette nouée côté lointain ----
    pag_pts = [(58.6, 96.0), (64.0, 97.6), (71.0, 98.4), (78.0, 97.8), (84.4, 96.4), (85.2, 99.6), (84.8, 103.0),
               (83.6, 106.4), (81.6, 104.4), (80.2, 107.4), (78.0, 104.8), (75.6, 106.2), (73.4, 104.0), (70.6, 105.2),
               (68.2, 103.2), (65.0, 104.2), (62.6, 102.4), (59.8, 103.4), (58.2, 100.6)]
    pag = sm(pag_pts, sharp=(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17), t=0.9)
    pd = [(taper(crpath([(66.8, 97.8), (66.2, 100.6), (66.6, 103.0)], 10), 1.5, 0.2, tip='sharp'), STRIPE, 0.88),
          (taper(crpath([(76.8, 98.0), (77.6, 100.8), (77.2, 104.0)], 10), 1.7, 0.2, tip='sharp'), STRIPE, 0.88),
          # les plis : le creux, l'arête claire à sa droite ; la lumière du côté lointain
          (ribbon([(71.6, 99.0), (71.4, 101.8), (71.8, 104.0)], [0.2, 1.0, 0.2]), TIGER.shadow, 0.5),
          (ribbon([(72.8, 99.0), (72.8, 101.6), (73.2, 103.4)], [0.1, 0.7, 0.1]), TIGER.light, 0.55),
          (ribbon([(80.2, 98.4), (81.6, 101.6), (82.2, 105.0)], [0.2, 1.2, 0.2]), TIGER.hi, 0.5),
          (sm([(58.6, 97.0), (61.4, 98.0), (61.8, 101.6), (59.8, 103.0), (58.4, 100.6)]), TIGER.deep, 0.35)]
    fig.part('pagne', pag, TIGER, grad=(84, 97, 60, 105, [(0, TIGER.light), (0.5, TIGER.base), (1, TIGER.shadow)]),
             cel=1.0, rim=0.6, cast=1.0, details=pd)
    # la cordelette de la ceinture : un morceau d'ellipse autour de la taille (une seule courbe lisse)
    belt_c = [(71.4 + 13.6 * math.cos(math.radians(a)), 95.4 + 2.5 * math.sin(math.radians(a))) for a in [176 - 172 * i / 30 for i in range(31)]][::-1]
    belt = ribbon(belt_c, [0.9] + [1.55] * 29 + [0.9], sharp_ends=False)
    fig.part('belt', belt, ROPE, cel=0.45, rim=0.4, cast=0.7, cast_on=['pagne', 'torso'],
             details=[(ribbon([(x, y - 0.4) for x, y in belt_c[2:-2]], [0.1] + [0.45] * 25 + [0.1]), ROPE.hi, 0.7)]
             + [(ellipse(x, y, 0.45, 0.75, -20), ROPE.shadow, 0.5) for x, y in belt_c[3:-2:4]])
    # le noeud côté lointain et ses deux bouts qui pendent
    kx, ky = 81.4, 97.4
    ends = [limb(crpath([(kx + 0.2, ky + 0.6), (kx - 0.4, ky + 2.6), (kx - 0.2, ky + 4.6)], 8), [1.0, 0.8], n=8),
            limb(crpath([(kx + 0.8, ky + 0.6), (kx + 1.6, ky + 2.4), (kx + 1.4, ky + 3.8)], 8), [0.95, 0.75], n=8)]
    for j, e in enumerate(ends):
        fig.part('bend%d' % j, e, ROPE, cel=0.25, rim=0.3, cast=0.5, cast_on=['pagne', 'belt'])
    fig.part('bknot', ellipse(kx + 0.4, ky + 0.1, 1.35, 1.05, -15), ROPE, cel=0.3, rim=0.35, cast=0.6, cast_on=['pagne', 'belt', 'bend0', 'bend1'])

    # ---- le bras proche (épaule, coude bas, avant-bras qui remonte), sa racine fondue dans le buste ----
    shN = mapp(UC, SH_N)
    Gw = mapp(UC, P['G'])
    deg = P['ang'] + P['lean']
    # le poignet : sous le poing, du côté du coude
    tow = (shN[0] - 4.0 - Gw[0], shN[1] + 7.0 - Gw[1])
    L_ = math.hypot(*tow) or 1
    wN0 = (Gw[0] + tow[0] / L_ * 3.4, Gw[1] + tow[1] / L_ * 3.4)
    Snu = mapp(inv(U), shN)
    eN, wN = ik(shN, wN0, L_UN, L_FN, -1)
    narm = round_limb([shN, eN, wN], [(0, 1.95, 1.95), (0.4, 1.55, 1.55), (0.6, 1.45, 1.45), (0.62, 1.4, 1.4), (1, 1.25, 1.25)], n=22)
    a1 = Seg(shN, eN)
    dmask = rot(a1.u, 130.0)
    fig.masks['narm'] = (shN[0] - 1.2 * dmask[0], shN[1] - 1.2 * dmask[1], shN[0] + 4.0 * dmask[0], shN[1] + 4.0 * dmask[1], (zoneN, TOR))
    fig.part('narm', narm, S, grad=(eN[0] + 4, shN[1] - 2, eN[0] - 3, eN[1] + 2, [(0, S.light), (0.5, S.base), (1, S.shadow)]),
             cel=0.8, rim=0.55, cast=0.8, cast_on=['torso', 'pagne', 'belt', 'tail'],
             details=[(ribbon([a1.at(0.15, -1.0), a1.at(0.6, -1.3), a1.at(0.95, -0.8)], [0.1, 0.6, 0.1]), S.hi, 0.45)])
    # le bracelet d'or au poignet
    s3 = Seg(eN, wN)
    bp = s3.at(0.82)
    brace, bpts = band(bp, math.degrees(math.atan2(s3.u[1], s3.u[0])), 1.45, 1.2)
    fig.part('brace', brace, GOLD, cel=0.3, rim=0.4, cast=0.5, cast_on=['narm', 'torso'],
             details=[(ribbon(bpts[2:], [0.3, 0.4, 0.1]), GOLD.glint, 0.75)])

    # ---- la tête (avec ses deux oreilles soudées), la crinière, la corne, l'anneau ----
    head_part(fig, P, S, HEAD)

    # ---- le petit kanabō dans le poing proche, puis le poing (par-dessus le manche) ----
    C, u, n, handle, collar, chead = club(Gw, deg)
    fig.part('handle', handle, IR, cel=0.3, rim=0.3, cast=0.5)
    # la tête : le pan éclairé (l'arête du dessus), le pan du dessous dans l'ombre, les clous en quinconce
    lit = (n[0] * 0.6 - n[1] * 0.8) < 0
    sg = -1 if lit else 1
    cd = [(sm([C(6.4, sg * 0.2), C(17.6, sg * 0.4), C(17.8, sg * 3.4), C(6.4, sg * 2.4)]), IR.light, 0.55),
          (sm([C(6.4, -sg * 0.6), C(17.6, -sg * 0.8), C(17.8, -sg * 3.4), C(6.4, -sg * 2.5)]), IR.shadow, 0.55),
          (ribbon([C(6.6, sg * 0.3), C(12.0, sg * 0.4), C(17.4, sg * 0.5)], [0.1, 0.5, 0.1]), IR.hi, 0.85)]
    for s0, t0 in ((8.6, -1.5), (11.6, 1.5), (14.4, -1.7), (9.8, 1.4), (13.0, -1.55), (16.0, 1.7), (10.6, -0.1), (15.2, 0.1)):
        c0 = C(s0, t0)
        cd += [(ellipse(c0[0] - 0.25, c0[1] + 0.3, 0.62, 0.62), IR.deep, 0.55),
               (ellipse(c0[0], c0[1], 0.55, 0.55), IR.light, 1),
               (ellipse(c0[0] + 0.18, c0[1] - 0.2, 0.22, 0.2), IR.glint, 0.9)]
    cd += [(sm([C(17.0, -3.2), C(18.1, -1.1), C(18.1, 1.1), C(17.0, 3.2)]), IR.deep, 0.45)]
    if P['hot'] > 0.05:
        cd += [(chead, ('rad', *C(14.0, 0), 9.0, 9.0, [(0, '#fff2b0', 0.7 * P['hot']), (0.5, '#ffb43a', 0.45 * P['hot']), (1, '#f2701a', 0)]), 1)]
    fig.part('chead', chead, IR, grad=(*C(12, -3), *C(10, 3), [(0, IR.light), (0.5, IR.base), (1, IR.shadow)]),
             cel=0.6, rim=0.5, cast=0.8, details=cd)
    fig.part('collar', collar, GOLD, grad=(*C(5, -2), *C(5, 2), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.35, rim=0.4, cast=0.6, cast_on=['handle', 'chead'],
             details=[(ribbon([C(4.6, sg * 1.2), C(5.6, sg * 1.6), C(6.2, sg * 1.7)], [0.1, 0.35, 0.1]), GOLD.glint, 0.8)])
    fist = fist_shape(Gw, deg)
    fdet = []
    for k in (-1.4, 0.0, 1.4):
        a0 = C(-1.0, k - 0.1)
        fdet.append((ellipse(*C(-0.2, k * 0.95), 0.9, 0.5, deg + 90), S.light, 0.45))
        fdet.append((ribbon([C(-2.4, k + 0.7), C(-0.6, k + 0.75), C(1.4, k + 0.6)], [0.05, 0.35, 0.05]), S.deep, 0.5))
    fig.part('fist', fist, S, grad=(Gw[0] + 3, Gw[1] - 3, Gw[0] - 3, Gw[1] + 3, [(0, S.light), (0.5, S.base), (1, S.shadow)]),
             cel=0.6, rim=0.5, cast=0.7, cast_on=['handle', 'chead', 'collar', 'narm', 'torso'], details=fdet)
    th = limb(crpath([C(-1.6, 2.6), C(0.8, 2.9), C(2.6, 1.8)], 8), [1.5, 1.2], n=8)
    fig.part('thumb', th, S, cel=0.35, rim=0.4, cast=0.5, cast_on=['fist', 'handle', 'collar'])

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['torso'], TOR)
    fig.pose(['cord', 'fang', 'fknot'], UC)
    fig.pose(['pagne', 'belt', 'bend0', 'bend1', 'bknot'], PAG)
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, club_tip=C(18.0, 0.0), club_mid=C(12.0, 0.0), fist=Gw, deg=deg,
                   eyes=(mapp(HEAD, FACE_V['oeil_proche'][:2]), mapp(HEAD, FACE_V['oeil_fond'][:2])),
                   head=mapp(HEAD, (72.0, 68.0)), feet=(bN, bF), hand=wF)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def head_part(fig, P, S, HEAD):
    """La tête : crâne large, menton pointu ; les deux oreilles soudées au crâne en une seule forme (creux arrondis à
    leur racine) ; visage construit sur la sphère commune (visage.py) ; crinière, corne, anneau d'or."""
    V = FACE_V
    med = V['mediane']
    (exn, eyy, ewn), (exf, _, ewf) = V['oeil_proche'], V['oeil_fond']
    nx, ny = V['nez']
    mx, my, mw = V['bouche']
    cx_, cy_ = V['menton']
    en, ef = P['en'], P['ef']

    head0 = sm([(cx_, cy_ + 0.2), (77.6, 83.0), (81.4, 80.2), (84.0, 76.6), (85.1, 72.6), (85.4, 68.6), (85.0, 64.6),
                (83.4, 61.0), (80.4, 58.4), (75.4, 56.6), (69.4, 56.4), (64.0, 57.6), (60.2, 60.4), (57.6, 64.2),
                (56.5, 68.6), (56.6, 73.2), (57.8, 77.2), (60.4, 80.6), (64.4, 83.0), (69.0, 84.3)], sharp=(0,), t=0.95)
    # l'oreille proche, immense, couchée vers l'arrière ; elle frémit autour de sa racine
    ER = (57.6, 70.4)
    ear = [(58.6, 64.6), (54.0, 61.8), (48.6, 58.6), (44.4, 56.4), (40.8, 54.8), (43.6, 58.6), (47.0, 63.0),
           (50.6, 67.8), (53.4, 72.0), (55.2, 75.6), (57.6, 77.6), (59.4, 75.0)]
    ear = [(ER[0] + rot((x - ER[0], y - ER[1]), en)[0], ER[1] + rot((x - ER[0], y - ER[1]), en)[1]) for x, y in ear]
    earN = sm(ear, sharp=(4,), t=0.9)
    # l'oreille lointaine, en pointe derrière le front
    FR = (85.0, 64.0)
    earf = [(83.4, 60.8), (86.2, 58.4), (88.8, 56.0), (91.2, 54.0), (90.2, 57.4), (88.6, 61.4), (86.6, 65.2), (85.2, 67.0)]
    earf = [(FR[0] + rot((x - FR[0], y - FR[1]), ef)[0], FR[1] + rot((x - FR[0], y - FR[1]), ef)[1]) for x, y in earf]
    earF = sm(earf, sharp=(3,), t=0.9)
    from shapely.geometry import box as _box
    gh = poly_of(head0)
    gu = gh.union(poly_of(earN)).union(poly_of(earF))
    gc = gu.buffer(2.2, 64, join_style=1).buffer(-2.2, 64, join_style=1)
    # le comblement arrondi seulement autour des racines (le reste du crâne ne bouge pas)
    g = gu.union(gc.intersection(_box(52.0, 60.0, 61.0, 80.0))).union(gc.intersection(_box(82.0, 54.0, 90.0, 70.0)))
    head = shape_of(g, step=0.45, t=0.9)

    hd = []
    # les plans : la calotte éclairée en haut à droite, le côté proche (vers l'oreille) dans l'ombre douce
    hd += [(sm([(66.0, 58.6), (72.0, 57.0), (78.6, 57.8), (83.0, 61.0), (84.6, 65.0), (80.4, 62.4), (74.6, 60.6), (68.4, 60.6)]), S.light, 0.6),
           (ribbon([(70.0, 57.6), (76.0, 57.4), (81.0, 59.4), (84.0, 62.8)], [0.1, 0.8, 0.7, 0.1]), S.hi, 0.6),
           (sm([(57.0, 66.0), (60.2, 64.6), (61.8, 69.0), (61.6, 74.4), (63.2, 79.0), (65.6, 82.6), (61.0, 80.4), (57.8, 76.4), (56.8, 71.0)]), S.shadow, 0.5),
           (sm([(81.2, 69.4), (84.6, 68.4), (85.0, 72.4), (83.6, 76.4), (81.6, 73.6)]), S.light, 0.45)]
    # l'oreille proche : le bord du haut éclairé, le creux sombre qui s'enfonce vers la racine, l'ombre douce du pli à
    # la racine (peinte dans la tête : aucune couture)
    R = lambda pts: [(ER[0] + rot((x - ER[0], y - ER[1]), en)[0], ER[1] + rot((x - ER[0], y - ER[1]), en)[1]) for x, y in pts]
    hd += [(sm(R([(57.0, 66.8), (53.0, 64.4), (48.4, 61.0), (44.0, 57.8), (46.8, 61.8), (50.2, 66.4), (53.2, 70.6),
                  (55.6, 73.8), (57.6, 73.0)]), sharp=(3,)), S.deep, 0.55),
           (sm(R([(56.8, 67.8), (53.4, 65.6), (49.0, 62.4), (46.6, 60.4), (49.4, 64.6), (52.6, 69.0), (55.4, 72.0)]), sharp=(3,)), '#3a0c26', 0.35),
           (ribbon(R([(41.6, 55.2), (46.0, 57.6), (51.4, 60.8), (56.0, 63.6)]), [0.1, 0.7, 0.6, 0.1]), S.hi, 0.65),
           (ribbon(R([(56.0, 75.8), (57.6, 72.0), (58.4, 67.0)]), [0.1, 1.2, 0.1]), S.shadow, 0.4)]
    # l'oreille lointaine : sa face éclairée (elle est du côté de la lumière), un mince creux
    RF = lambda pts: [(FR[0] + rot((x - FR[0], y - FR[1]), ef)[0], FR[1] + rot((x - FR[0], y - FR[1]), ef)[1]) for x, y in pts]
    hd += [(ribbon(RF([(85.2, 60.0), (88.4, 56.6), (91.6, 53.2)]), [0.1, 0.6, 0.1]), S.hi, 0.6),
           (ribbon(RF([(86.4, 63.6), (88.6, 59.6), (90.8, 55.6)]), [0.1, 0.8, 0.1]), S.shadow, 0.45)]

    # les arcades froncées (creux au-dessus des yeux, plus bas vers le nez : l'air vicieux)
    hd += [(ribbon([(exn - 3.8, 67.8), (exn - 0.8, 67.2), (exn + 2.6, 68.4), (exn + 4.0, 69.4)], [0.2, 1.2, 1.0, 0.2]), S.shadow, 0.4),
           (ribbon([(exf - 3.4, 69.4), (exf - 1.6, 68.2), (exf + 1.0, 67.4), (exf + 3.0, 67.6)], [0.2, 0.9, 0.9, 0.2]), S.shadow, 0.35),
           (ribbon([(med(64.0) - 1.0, 63.4), (med(66.0) - 0.4, 66.2), (med(68.0) - 0.2, 68.2)], [0.1, 0.6, 0.1]), S.shadow, 0.35)]
    # les gros yeux jaunes : même forme (amande), même ligne ; le lointain plus étroit ; la paupière du haut tombe
    # vers le nez (le regard méchant) ; petite pupille tournée vers l'ennemi
    eh = P['eyes']
    eyes_ = []
    for cx, w_, pr, inner in ((exn, ewn, 1.0, 1), (exf, ewf, 0.88, -1)):
        hw = w_ / 2
        hh = 2.0 * pr
        if P['blink'] > 0.5:
            hd += [(ribbon([(cx - hw, eyy - 0.1), (cx, eyy + 0.6 * pr), (cx + hw, eyy)], [0.1, 0.65, 0.1]), EYEINK, 0.95),
                   (ribbon([(cx - hw * 0.8, eyy - 0.9), (cx, eyy - 0.6), (cx + hw * 0.8, eyy - 0.8)], [0.1, 0.5, 0.1]), S.light, 0.4)]
            continue
        # le coin intérieur (côté nez) plus bas : la paupière du haut descend en biais
        ti = -0.8 * inner
        eye = sm([(cx - hw, eyy + 0.15 + ti * 0.1), (cx - hw * 0.45, eyy - hh * 0.95 + ti * 0.5), (cx + hw * 0.45, eyy - hh * 0.95 - ti * 0.5),
                  (cx + hw, eyy + 0.15 - ti * 0.1), (cx + hw * 0.4, eyy + hh * 0.85), (cx - hw * 0.4, eyy + hh * 0.85)], sharp=(0, 3))
        eyes_.append(eye)
        hd += [(eye.scale(1.16, 1.3, cx, eyy), EYEINK, 0.92), (eye, '#fff6d0', 1)]
        cid = fig.uid('ce')
        fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, eye.d()))
        stops = [(0, '#ffffff'), (0.35, '#fff6c0'), (0.8, '#ffd84a'), (1, '#ffa62a')] if eh > 0.5 else \
            [(0, '#fff6b0'), (0.45, EYE_Y), (0.85, '#f2b028'), (1, EYE_K)]
        hd += [('<path d="%s" fill="FILL" clip-path="url(#%s)"/>' % (eye.scale(1.0, 1.0, cx, eyy).d(), cid),
                ('rad', cx + 0.4, eyy - 0.5, hw * 1.3, hw * 1.3, stops), 1)]
        # l'ombre de la paupière du haut dans l'oeil
        hd += [('<path d="%s" fill="%s" opacity="0.5" clip-path="url(#%s)" fill-rule="evenodd"/>' % (eye.d() + eye.move(0.0, 0.5).d(), EYE_K, cid), '', 1)]
        pk = 0.7 if eh > 0.5 else 1.0
        px_ = cx + hw * 0.38
        hd += [('<path d="%s" fill="%s" clip-path="url(#%s)"/>' % (ellipse(px_, eyy + 0.1, 0.62 * pr * pk, 0.95 * pr * pk).d(), PUPIL, cid), '', 1),
               (ellipse(px_ + 0.35 * pr, eyy - 0.45 * pr, 0.3 * pr, 0.28 * pr), '#ffffff', 1),
               (ribbon([(cx - hw * 1.05, eyy + 0.2 + ti * 0.1), (cx - hw * 0.4, eyy - hh * 1.0 + ti * 0.55), (cx + hw * 0.45, eyy - hh * 1.0 - ti * 0.55),
                        (cx + hw * 1.05, eyy + 0.2 - ti * 0.1)], [0.1, 0.65, 0.65, 0.1]), EYEINK, 1)]
        if eh > 0.05:
            hd += [(ellipse(cx, eyy, hw * 1.7, hh * 1.5), ('rad', cx, eyy, hw * 1.7, hw * 1.7, [(0, LAVA[1], 0.55 * eh), (1, LAVA[3], 0)]), 1)]
    # les sourcils sombres froncés en V (le bout intérieur plus bas, vers le nez), de la couleur de la crinière
    browN = sm([(exn - 4.2, 66.0), (exn - 2.0, 65.6), (exn + 1.0, 66.4), (exn + 3.6, 67.6), (exn + 4.4, 68.9),
                (exn + 2.6, 69.2), (exn + 0.0, 68.0), (exn - 2.4, 67.0)], sharp=(0, 4), t=0.9)
    browF = sm([(exf - 3.7, 69.0), (exf - 3.0, 67.6), (exf - 0.8, 66.5), (exf + 1.6, 65.9), (exf + 3.4, 66.0),
                (exf + 1.8, 67.0), (exf - 0.6, 68.0), (exf - 2.2, 69.2)], sharp=(0, 4), t=0.9)
    hd += [(browN, ('lin', exn + 3, 65, exn - 3, 69, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]), 1),
           (browF, ('lin', exf + 3, 65, exf - 3, 69, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]), 1),
           (ribbon([(exn - 3.6, 66.0), (exn - 0.4, 66.1), (exn + 3.0, 67.6)], [0.1, 0.4, 0.1]), HAIR.hi, 0.7),
           (ribbon([(exf - 2.6, 67.8), (exf - 0.2, 66.7), (exf + 2.8, 66.1)], [0.1, 0.35, 0.1]), HAIR.hi, 0.7)]
    # les pommettes (sous les yeux), la joue proche qui se gonfle du sourire, le pli de la joue au coin de la bouche
    hd += [(ribbon([(exn - 3.0, eyy + 3.0), (exn, eyy + 3.6), (exn + 2.6, eyy + 3.2)], [0.1, 0.9, 0.1]), S.light, 0.55),
           (ribbon([(exf - 2.0, eyy + 3.2), (exf + 0.2, eyy + 3.6), (exf + 2.4, eyy + 3.0)], [0.1, 0.8, 0.1]), S.hi, 0.45),
           (ellipse(exn - 0.6, eyy + 4.6, 2.6, 1.4, -10), S.light, 0.3)]
    # le petit nez SUR la ligne médiane, entre les yeux : l'arête claire qui descend d'entre les sourcils, le bout
    # rond qui ne dépasse pas, deux narines
    nose = sm([(nx - 0.6, ny - 4.0), (nx + 0.6, ny - 4.0), (nx + 1.3, ny - 1.6), (nx + 2.0, ny - 0.4), (nx + 1.6, ny + 0.6),
               (nx, ny + 0.9), (nx - 1.6, ny + 0.6), (nx - 2.0, ny - 0.4), (nx - 1.3, ny - 1.6)])
    hd += [(nose.move(-0.6, 0.5), S.shadow, 0.5),
           (nose, ('lin', nx + 2, ny - 3, nx - 2, ny + 1, [(0, S.light), (0.5, S.base), (1, S.shadow)]), 1),
           (ribbon([(nx + 0.1, ny - 3.6), (nx + 0.5, ny - 2.0), (nx + 0.9, ny - 0.6)], [0.1, 0.5, 0.1]), S.hi, 0.75),
           (ellipse(nx + 0.9, ny - 0.4, 0.55, 0.35, -20), '#ffd6a8', 0.75),
           (ellipse(nx - 0.95, ny + 0.25, 0.48, 0.3, 15), '#3a0a1e', 0.85),
           (ellipse(nx + 1.0, ny + 0.25, 0.36, 0.26, -15), '#3a0a1e', 0.75)]
    # le grand sourire en croissant (gueule de monstre voulue) : centré sous le nez, les coins qui remontent dans les
    # joues ; la lèvre du haut, les gencives d'où PARTENT les dents pointues (deux crocs en haut, deux en bas), la gorge
    # rouge sombre (jamais noire), la langue
    hl, hr = 7.4, 5.8                                   # demi-largeurs : la moitié proche plus large (3/4)
    xl, xr = mx - hl, mx + hr
    top_ = [(xl, my - 1.9), (mx - hl * 0.55, my - 0.9), (mx, my - 0.7), (mx + hr * 0.55, my - 0.9), (xr, my - 1.9)]
    bot_ = [(xr, my - 1.9), (mx + hr * 0.6, my + 2.0), (mx, my + 3.0), (mx - hl * 0.6, my + 2.0), (xl, my - 1.9)]
    mouth = sm(top_ + bot_[1:-1], sharp=(0, 4), t=0.9)
    mcid = fig.uid('cm')
    fig.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (mcid, mouth.d()))
    inner = []
    # la gorge
    inner.append((mouth, ('rad', mx, my + 0.6, 6, 6, [(0, '#6a1426'), (1, GORGE)]), 1))
    # la langue (dans le bas, côté proche)
    inner.append((ellipse(mx - 1.2, my + 2.4, 3.6, 1.5, -4), TONGUE, 1))
    inner.append((ellipse(mx - 0.6, my + 1.8, 1.6, 0.5, -4), '#e86a74', 0.7))
    # les gencives du haut et les dents du haut (pointes vers le bas), qui suivent la lèvre
    gum_t = ribbon([(xl, my - 1.6), (mx - hl * 0.55, my - 0.6), (mx, my - 0.35), (mx + hr * 0.55, my - 0.6), (xr, my - 1.6)], [1.0, 1.3, 1.3, 1.3, 1.0], sharp_ends=False)
    inner.append((gum_t, GUM, 1))
    def tooth(x, y, w, h, down=True):
        s = 1 if down else -1
        return sm([(x - w / 2, y), (x + w / 2, y), (x + w * 0.12, y + s * h), (x - w * 0.05, y + s * h * 0.98)], sharp=(0, 1, 2, 3), t=0.7)
    def lip_y(x, top=True):
        pts = top_ if top else bot_[::-1]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if x1 <= x <= x2:
                return y1 + (y2 - y1) * (x - x1) / ((x2 - x1) or 1)
        return pts[-1][1]
    teeth = []
    # en haut : une rangée de petites dents régulières, deux crocs plus longs ; en bas : deux crocs près des coins et
    # deux petites dents au milieu (elles ne croisent jamais celles du haut)
    for x, h, w in ((mx - hl * 0.8, 1.0, 1.1), (mx - hl * 0.56, 2.2, 1.5), (mx - hl * 0.3, 1.15, 1.3), (mx - hl * 0.07, 1.2, 1.3),
                    (mx + hr * 0.18, 1.15, 1.25), (mx + hr * 0.45, 1.9, 1.35), (mx + hr * 0.72, 0.95, 1.05)):
        teeth.append(tooth(x, lip_y(x) + 0.3, w, h, True))
    gum_b = ribbon([(mx - hl * 0.78, my + 1.2), (mx - hl * 0.4, my + 2.4), (mx, my + 2.85), (mx + hr * 0.4, my + 2.4), (mx + hr * 0.78, my + 1.2)],
                   [0.6, 0.9, 0.9, 0.9, 0.6], sharp_ends=False)
    inner.append((gum_b, GUM, 0.9))
    for x, h, w in ((mx - hl * 0.66, 1.7, 1.3), (mx - hl * 0.2, 0.8, 1.1), (mx + hr * 0.2, 0.8, 1.05), (mx + hr * 0.62, 1.45, 1.15)):
        yb = lip_y(x, False) - 0.4
        teeth.append(tooth(x, yb, w, h, False))
    for t_ in teeth:
        inner.append((t_, '#f2e6cc', 1))
        inner.append((t_.move(0.25, -0.1), '#fffbee', 0.0))
    for sh, fl, op in inner:
        if isinstance(fl, tuple):
            hd.append(('<path d="%s" fill="FILL" clip-path="url(#%s)"%s/>' % (sh.d(), mcid, '' if op == 1 else ' opacity="%g"' % op), fl, 1))
        else:
            hd.append(('<path d="%s" fill="%s" clip-path="url(#%s)"%s/>' % (sh.d(), fl, mcid, '' if op == 1 else ' opacity="%g"' % op), '', 1))
    # les lèvres (fines, sombres) autour de l'ouverture ; le pli de la joue au coin de la bouche ; le menton éclairé
    hd += [(ribbon(top_, [0.25, 0.6, 0.5, 0.6, 0.25]), '#5a1228', 0.9),
           (ribbon(bot_, [0.25, 0.55, 0.7, 0.55, 0.25]), '#6a1a2c', 0.8),
           (ribbon([(xl - 0.4, my - 3.0), (xl - 1.0, my - 1.6), (xl - 0.6, my - 0.2)], [0.1, 0.55, 0.1]), S.shadow, 0.6),
           (ribbon([(xr + 0.3, my - 3.0), (xr + 0.8, my - 1.7), (xr + 0.5, my - 0.4)], [0.1, 0.45, 0.1]), S.shadow, 0.5),
           (ribbon([(mx - 3.6, my + 3.8), (mx, my + 4.4), (mx + 3.0, my + 3.8)], [0.1, 0.6, 0.1]), S.light, 0.45),
           (ellipse(cx_ + 0.4, cy_ - 1.2, 1.4, 0.7, -10), S.hi, 0.35)]
    # le pli d'ombre sous la crinière et autour de la corne (la peau rentre sous les mèches)
    hd += [(ribbon([(60.6, 61.6), (64.0, 59.8), (68.0, 59.6), (72.0, 59.8)], [0.1, 1.1, 1.0, 0.1]), S.shadow, 0.5),
           (ellipse(med(59.6) + 0.2, 60.0, 3.2, 1.0, -4), S.shadow, 0.5)]
    def box_(sh):
        x0_, y0_, x1_, y1_ = sh.bbox()
        return ((x0_ + x1_) / 2, (y0_ + y1_) / 2, x1_ - x0_)
    if eyes_:
        fig_face.update({'oeil_proche': box_(eyes_[0]), 'oeil_fond': box_(eyes_[1])})
    fig_face.update({'nez': (nx, ny), 'bouche': box_(mouth)})
    fig.part('head', head, S, grad=(86, 58, 58, 82, [(0, S.light), (0.5, S.base), (1, S.shadow)]),
             cel=1.1, rim=0.6, cast=1.0, details=hd, occl=(S.deep, 0.16, 2.0))

    # ---- l'anneau d'or au lobe de l'oreille proche ----
    lobe = R([(57.4, 77.6)])[0]
    ring = ellipse(lobe[0] - 0.4, lobe[1] + 1.4, 1.35, 1.55).hole(ellipse(lobe[0] - 0.35, lobe[1] + 1.5, 0.7, 0.85))
    fig.part('ering', ring, GOLD, cel=0.3, rim=0.35, cast=0.5, cast_on=['head'])

    # ---- la houppe de crinière noir-bleuté : une seule masse qui naît du crâne, trois mèches rabattues vers l'arrière
    # (tailles et courbes différentes, jamais un éventail régulier) ----
    hs = P.get('hs', 0.0)
    scalp = sm([(60.6, 62.0), (61.4, 59.6), (64.0, 57.4), (68.0, 56.0), (72.6, 55.6), (76.6, 56.4), (76.2, 58.2),
                (73.4, 59.2), (70.4, 59.0), (67.2, 59.6), (64.4, 60.0), (62.6, 61.2)], t=0.9)
    LOCKS = [((75.4, 57.2), (73.6, 53.4), (70.4, 50.6), (66.0, 48.6), 6.2),
             ((70.6, 57.4), (67.6, 54.0), (64.4, 52.4), (60.0, 51.8), 5.4),
             ((65.6, 58.6), (62.6, 56.6), (59.4, 56.0), (55.2, 56.8), 4.2)]
    locks = []
    for p0, p1, p2, p3, w in LOCKS:
        p3 = (p3[0] + hs * 0.6, p3[1] - hs * 0.3)
        locks.append(lock(p0, p1, p2, p3, w, n=10, bulge=0.3))
    gh2 = poly_of(scalp)
    for l_ in locks:
        gh2 = gh2.union(poly_of(l_))
    gh2 = gh2.union(gh2.buffer(0.8, 32, join_style=1).buffer(-0.8, 32, join_style=1))
    hair = shape_of(gh2, step=0.35, t=0.8)
    hdet = []
    for (p0, p1, p2, p3, w), l_ in zip(LOCKS, locks):
        hdet += [(l_.move(-0.4, 0.7), HAIR.deep, 0.35),
                 (l_, ('lin', p0[0], p0[1], p3[0], p3[1], [(0, HAIR.base, 0.0), (0.3, HAIR.base, 0.9), (1, HAIR.shadow, 1)]), 1),
                 (ribbon(crpath([lerp(p0, p1, 0.6), p1, p2, lerp(p2, p3, 0.6)], 10), [0.1, 0.8, 0.7, 0.1] if False else [0.1] + [0.75] * 9 + [0.1]), HAIR.light, 0.55)]
    hdet += [(ribbon([(66.0, 56.8), (70.0, 55.6), (74.6, 55.8)], [0.1, 0.6, 0.1]), HAIR.hi, 0.5)]
    fig.part('hair', hair, HAIR, grad=(76, 50, 58, 60, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
             cel=0.6, rim=0.6, cast=0.9, cast_on=['head'], details=hdet)

    # ---- la petite corne d'ivoire au milieu du front, couchée un peu en arrière (plantée sur la médiane) ----
    hb = (med(59.8), 59.8)
    hornc = crpath([hb, (hb[0] - 0.1, 56.0), (hb[0] - 0.7, 52.6), (hb[0] - 1.9, 49.2)], 24)
    horn = taper(hornc, 4.6, 0.3, tip='sharp', wmid=3.2)
    fig.part('horn', horn, IVORY, grad=(hb[0] + 2.4, 50, hb[0] - 2.4, 58, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=0.6, rim=0.6, cast=0.9, cast_on=['head', 'hair'],
             details=[(ribbon([(hb[0] + 1.0, 58.6), (hb[0] + 0.9, 55.6), (hb[0] + 0.2, 52.4), (hb[0] - 1.2, 50.0)], [0.2, 0.8, 0.6, 0.1]), IVORY.hi, 0.85),
                      (sm([(hb[0] - 2.4, 59.8), (hb[0] + 2.4, 59.8), (hb[0] + 2.0, 58.2), (hb[0] - 2.2, 58.4)]), IVORY.shadow, 0.55)])
    fig.pose(['head', 'ering', 'hair', 'horn'], HEAD)


def main():
    """diablotin.svg (grand) et diablotin-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-lenore-rapide.webp (512 px de haut) et mon-lenore-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('diablotin', 0.95, 512, ID_JEU), ('diablotin-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [round(w, 2), round(h, 2), round(FEET[0] - x0, 2), round(FEET[1] - y0, 2)])
    print('visage :', verifier(fig_face, FACE_BOX) or 'aucun défaut')


if __name__ == '__main__':
    main()
