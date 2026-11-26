# Zaroth (demons-8, eau, épique, protecteur) redessiné en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte de tous les héros, 26/11/2026, sur le modèle de Kael validé : ../kael/kael.py, outil commun ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/zaroth/zaroth.py      # → zaroth.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/zaroth.txt) : le samouraï masqué, un mur d'armure rouge.
# Grosse tête casquée (bol laqué rouge, visière qui met les yeux dans l'ombre, grand croissant d'or sur une monture à
# gemme bleue, aileron retourné à blason de vague, protège-nuque en trois paliers), cache-cou de tissu rouge à liseré
# d'or qui couvre tout le bas du visage jusqu'au bord avant (avis du propriétaire : plus de nez), yeux ambre sous de gros
# sourcils blancs froncés ; deux grandes épaulières carrées à laçage bleu, cuirasse en tonneau (liserés d'or, blason de
# vague), jupe de plaques, hakama bleu nuit, jambières laquées, tabi et sandales de paille ; sabre tenu à deux mains
# devant le ventre, lame qui monte vers l'ennemi ; fourreau bleu nuit qui dépasse derrière la hanche.
# Garde de samouraï : jambe proche tendue en arrière, jambe lointaine en avant, genou fléchi, pieds à plat.
# Coordonnées = pixels de la grille de zaroth.txt (mêmes pieds, même échelle : y = 116 est le sol), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import bent, taper, crpath  # noqa: E402
from visage import placer  # noqa: E402
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'demons-8'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
LACQ = Mat('#ffb487', '#ff6644', '#dc3634', '#9a1b3c', '#520d34')       # laque rouge
GOLD = Mat('#fff1a6', '#f8cc50', '#d8922a', '#965220', '#5a2a18')
NAVY = Mat('#8ea4ea', '#4b61ac', '#2e3a78', '#1e2252', '#121334', glint='#cad8ff')
STEEL = Mat('#f6f9ff', '#d2deee', '#9ca8c6', '#5c6488', '#33385a')
BLADE = Mat('#ffffff', '#dfe8f4', '#a8b6d2', '#64709a', '#363c60')
SKIN = Mat('#ffd2a4', '#eea474', '#bf7052', '#7c3a3c', '#3e1828')
WHITE = Mat('#ffffff', '#f4f0fa', '#dcd6ea', '#a49cbc', '#5e5680')
STRAW = Mat('#f8e0a0', '#dab86c', '#aa7e44', '#6e4c2e', '#3e2618')
BRAID = Mat('#ffffff', '#efeaf6', '#d0c8e0', '#8e86aa', '#5a5476')
FANG = Mat('#fffaf0', '#f4ead6', '#dccdb8', '#a8907e', '#6b5040')
WATER = ['#ffffff', '#d8f2ff', '#9ed8f6', '#5cacea', '#2f74c4', '#1c4a92']
EYE = ('#fff3c4', '#ffb020', '#c0501a', '#1a0814')

# le visage (visage.py) : l'ovale de la face sous le casque (bord avant = le contour de la joue et du cache-cou)
FACE_BOX = (52.0, 26.0, 88.4, 54.6)
# gabarits des yeux (repère : milieu de l'œil ; largeur 7,2 pour l'œil proche ; le regard part vers la droite)
EYE_N = [(-3.6, 0.1), (-1.0, -1.2), (2.2, -1.1), (3.6, -0.1), (1.4, 1.2), (-1.8, 1.1)]
EYE_F = [(-3.6, 0.1), (-1.4, -1.0), (2.2, -1.3), (3.6, -0.6), (1.4, 0.7), (-1.9, 0.9)]

GRD = 116          # le sol (dessous des sandales)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin : les pieds (64, 116)
FRAME = (12, -6, 102, 125)
FEET = (64, 116)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath 0..1 (le buste se gonfle, épaules et tête montent) ; crouch (il se tasse dans la garde) ; lean (penché en
#   avant +) ; head / tilt : la tête ; blink ; O : le milieu de la garde du sabre ; ang : où pointe la lame ;
#   edge : le fil devant (+1) ou derrière (−1) ; bn / bf : le sens du pli des coudes ; shn / shf : les épaules glissent ;
#   lift : les épaulières se soulèvent (bras levés) ; sn / sf : retard des plaques des épaulières ; kz : la jupe de
#   plaques se balance ; stretch : la lame s'allonge par la vitesse ; sw_front : le sabre passe devant la tête.
O0 = (79.4, 73.8)                 # la garde, au repos
ANG0 = -54.1                      # la lame monte vers l'avant (vers l'ennemi)
S_N0 = (47.5, 63.5)               # l'épaule proche (sous l'épaulière)
S_F0 = (92.5, 64.0)               # l'épaule lointaine
L_N = (14.5, 14.2)                # bras, avant-bras (jusqu'au poignet)
L_F = (15.5, 14.6)
FIST_N = (-5.7, 0.0)              # centre des poings dans le repère du sabre (x le long de la lame, y vers le fil)
FIST_F = (-12.0, 0.9)
WRIST_N = (-5.4, -6.5)            # les poignets : la main proche par le dos du sabre, la main lointaine par le fil
WRIST_F = (-10.4, 7.6)
BLADE_L = 49.0
HEAD_C = (70.0, 54.0)             # le centre de l'agrandissement de la tête (le cou)
# les épaulières (avis du propriétaire, tour 2 : « Réduire la taille des épaulettes ») : plaques moins nombreuses, moins
# hautes et moins larges ; x gauche / droit de la plaque du haut, y du haut, hauteur d'une plaque, pas entre deux, nombre
NS_X, NS_Y, NS_H, NS_STEP, NS_N = (39.6, 54.4), 52.2, 5.4, 4.6, 4
FS_X, FS_Y, FS_H, FS_STEP, FS_N = (88.6, 97.4), 54.8, 5.4, 4.6, 3

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0, O=O0, ang=ANG0, edge=1,
            bn=0, bf=0, shn=(0.0, 0.0), shf=(0.0, 0.0), lift=0.0, sn=0.0, sf=0.0, kz=0.0, stretch=0.0,
            sw_front=False, tint=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def under(sh, dx=0.6, dy=-1.8):
    """La face du dessous d'une forme : la forme moins elle-même décalée vers le haut-droit (découpée dans la forme)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def ring_of(sh, k, cx, cy):
    """Un liseré : la forme moins elle-même rétrécie (pair-impair)."""
    return Shape(sh.subs + sh.scale(k, k, cx, cy).subs, evenodd=True)


def ik(S, W, L1, L2, bend):
    """Le coude (cinématique inverse) ; si le poing est trop loin, le bras se tend (le haut reste sous l'épaulière)."""
    d = math.dist(S, W)
    if d >= L1 + L2 - 0.05:
        k = L1 / (L1 + L2)
        return lerp(S, W, k)
    dd = max(abs(L1 - L2) + 0.01, d)
    al = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    base = math.atan2(W[1] - S[1], W[0] - S[0])
    cands = [(S[0] + L1 * math.cos(base + b * al), S[1] + L1 * math.sin(base + b * al)) for b in (1, -1)]
    if bend == 0:                     # le coude pend : on prend la solution la plus basse (la pesanteur)
        return max(cands, key=lambda e: e[1])
    return cands[0] if bend > 0 else cands[1]


def wave_sign(cx, cy, r, turn=1.0):
    """Le blason de vague (signe inventé) : une volute qui s'enroule, effilée, et la crête qui retombe."""
    pts = []
    for i in range(23):
        t = i / 22
        a = math.radians(200 + 400 * t * turn)
        rr = r * (1 - 0.78 * t)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pts = [(cx - r * 1.25, cy + r * 0.55)] + pts
    ws = [0.25 * r] + [r * (0.42 - 0.3 * i / 22) for i in range(23)]
    from atelier import sides
    left, right = sides(pts, ws)
    return sm(left + [pts[-1]] + right[::-1], t=0.8)


def lace(x, y, h=2.2, w=0.95):
    """Un cordon de laçage (bleu nuit, un point d'eau en haut) : petit bâtonnet arrondi, discret."""
    return [(rpoly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], w * 0.45), NAVY.shadow, 0.95),
            (ellipse(x + 0.08, y - h / 2 + 0.5, w * 0.3, 0.38), WATER[3], 0.9)]


def plate_parts(fig, name, rows, mat=LACQ, cords=(), gold_top=False, gold_bot=False, cast=0.9, tilt=0.0):
    """Une épaulière (ou un panneau) en plaques : de la plus basse à la plus haute (celle du dessus recouvre celle du
    dessous et y pose son ombre). rows : liste de (x gauche, y haut, x droit, y bas) ; cords : x des colonnes de laçage."""
    n = len(rows)
    for i in range(n - 1, -1, -1):
        xl, yt, xr, yb = rows[i]
        sag = 0.5
        sh = sm([(xl, yt + tilt), ((xl + xr) / 2, yt + 0.15), (xr, yt - tilt), (xr + 0.25, (yt + yb) / 2), (xr, yb - tilt + 0.2),
                 ((xl + xr) / 2, yb + sag), (xl, yb + tilt + 0.3), (xl - 0.25, (yt + yb) / 2)], sharp=(0, 2, 4, 6), t=0.7)
        det = [(sm([(xl, yt + tilt), (xr, yt - tilt), (xr, yt - tilt + 1.5), (xl, yt + tilt + 1.6)], sharp=(0, 1, 2, 3)), mat.light, 0.55)]
        for cx in cords:
            x = xl + (xr - xl) * cx
            det += lace(x, yb - 1.9, 2.6, 1.15)
        if gold_top and i == 0:
            det += [(sm([(xl - 1, yt + tilt - 1), (xr + 1, yt - tilt - 1), (xr + 1, yt - tilt + 1.25), (xl - 1, yt + tilt + 1.35)], sharp=(0, 1, 2, 3)), GOLD.base, 1),
                    (sm([(xl - 1, yt + tilt - 1), (xr + 1, yt - tilt - 1), (xr + 1, yt - tilt + 0.5), (xl - 1, yt + tilt + 0.6)], sharp=(0, 1, 2, 3)), GOLD.light, 1)]
        if gold_bot and i == n - 1:
            det += [(sm([(xl - 1, yb + tilt - 0.9), (xr + 1, yb - tilt - 0.9), (xr + 1, yb + 2), (xl - 1, yb + 2)], sharp=(0, 1, 2, 3)), GOLD.base, 1),
                    (sm([(xl - 1, yb + tilt - 0.9), (xr + 1, yb - tilt - 0.9), (xr + 1, yb - tilt - 0.3), (xl - 1, yb + tilt - 0.2)], sharp=(0, 1, 2, 3)), GOLD.light, 0.9)]
        fig.part('%s%d' % (name, i), sh, mat, cel=1.1, rim=0.6, cast=cast, details=det)
    return ['%s%d' % (name, i) for i in range(n)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 1.0, 66, 94))       # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.5 * br))                                          # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 70, 80))                            # la cuirasse se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 72, 54), mS(1.1, 1.1, *HEAD_C))   # tête un peu plus grande
    SN = mchain(UC, mT(P['shn'][0] * 0.5, -P['lift'] + P['sn']))              # épaulière proche
    SF = mchain(UC, mT(P['shf'][0] * 0.4, -P['lift'] * 0.7 + P['sf']))        # épaulière lointaine
    KZ = mchain(U, mskx(-0.05 * P['kz'], 76))                                 # la jupe de plaques se balance
    LEG = mS(1, 1 - dyb / 24, 0, GRD)                                         # les jambes plient (pieds au sol)

    # ---- le fourreau bleu nuit, qui dépasse derrière la hanche (derrière tout) ----
    saya = limb([(50.4, 88.0), (43.6, 90.6), (36.6, 92.9), (29.6, 95.1), (25.0, 96.4)], [4.8, 4.6, 4.4, 4.2, 4.1])
    fig.part('saya', saya, NAVY, cel=1.0, rim=0.6, cast=0,
             details=[(ribbon([(48, 87.6), (38, 90.9), (27, 94.4)], [0.2, 0.9, 0.2]), NAVY.hi, 0.6),
                      (sm([(34.6, 91.0), (36.6, 90.4), (38.4, 95.0), (36.4, 95.6)], sharp=(0, 1, 2, 3)), WATER[3], 1),
                      (sm([(35.6, 90.8), (36.6, 90.4), (37.4, 92.6), (36.4, 93.0)], sharp=(0, 1, 2, 3)), WATER[1], 0.9)])
    kojiri = sm([(26.6, 94.4), (25.6, 99.0), (21.4, 99.8), (18.6, 98.2), (18.8, 95.6), (22.0, 94.0)])
    fig.part('kojiri', kojiri, GOLD, cel=0.9, rim=0.6, cast=0.6,
             details=[(ellipse(22.6, 95.8, 1.6, 0.7, -15), GOLD.hi, 0.9)])

    # ---- la jambe lointaine (gauche), en avant, genou fléchi : sandale, tabi, jambière, hakama ----
    fig.part('fsole', rpoly([(74.4, 113.4), (94.6, 113.2), (95.0, 116.2), (74.2, 116.2)], [1.2, 1.6, 0.6, 0.6]), STRAW, cel=0.6, rim=0.5, cast=0,
             details=[(sm([(74, 115.2), (95.4, 115.2), (95.4, 116.4), (74, 116.4)]), STRAW.shadow, 1)])
    ffoot = sm([(78.0, 108.6), (85.6, 108.4), (89.8, 110.4), (93.6, 112.2), (94.0, 114.2), (76.0, 114.4), (75.4, 111.4)])
    fig.part('ffoot', ffoot, WHITE, cel=1.0, rim=0.6, cast=0.8,
             details=[(ribbon([(88.6, 110.6), (86.2, 113.0), (84.6, 114.4)], [0.2, 1.0, 0.6]), STRAW.base, 1),
                      (ribbon([(88.6, 110.6), (90.6, 112.6), (91.6, 114.3)], [0.2, 0.9, 0.5]), STRAW.base, 1),
                      (ellipse(88.6, 110.7, 0.9, 0.7), STRAW.light, 1)])
    fgreave = sm([(80.4, 102.4), (91.6, 102.2), (91.2, 107.0), (90.4, 111.0), (81.0, 111.2), (80.0, 107.0)], sharp=(0, 1))
    fig.part('fgreave', fgreave, LACQ, cel=1.2, rim=0.7, cast=0.9,
             details=[(sm([(80, 109.6), (91, 109.4), (91, 111.6), (80, 111.6)]), GOLD.base, 1),
                      (sm([(80, 109.6), (91, 109.4), (91, 110.2), (80, 110.4)]), GOLD.light, 1),
                      (ellipse(87.8, 106.0, 0.9, 0.9), GOLD.base, 1), (ellipse(88.0, 105.8, 0.4, 0.4), GOLD.hi, 1),
                      (ribbon([(89.6, 103.2), (89.4, 106), (88.8, 109)], [0.2, 1.0, 0.2]), LACQ.hi, 0.55)])
    fleg = bent((78.4, 89.6), (88.2, 98.4), (86.8, 103.4), 16.0, 13.8, 13.0, bulge=(0.06, 0.04))
    fig.part('fleg', fleg, NAVY, cel=1.5, rim=0.7, cast=1.0,
             details=[(ribbon([(78.4, 92), (84.6, 97.6), (83.6, 101.6), (82.8, 104.8)], [0.2, 1.0, 0.9, 0.2]), NAVY.shadow, 0.8),
                      (ribbon([(73.6, 94.4), (79.2, 100.0), (80.2, 104.6)], [0.2, 0.9, 0.2]), NAVY.deep, 0.5),
                      (ribbon([(84.4, 92.6), (89.2, 97.4), (89.8, 101.4), (89.6, 104.6)], [0.2, 0.8, 0.7, 0.2]), NAVY.light, 0.7)])

    # ---- la jambe proche (droite), tendue loin en arrière ----
    fig.part('nsole', rpoly([(29.2, 113.4), (48.2, 113.2), (48.6, 116.2), (29.0, 116.2)], [1.2, 1.6, 0.6, 0.6]), STRAW, cel=0.6, rim=0.5, cast=0,
             details=[(sm([(29, 115.2), (49, 115.2), (49, 116.4), (29, 116.4)]), STRAW.shadow, 1)])
    nfoot = sm([(33.0, 108.6), (40.2, 108.4), (43.8, 110.4), (47.4, 112.2), (47.8, 114.2), (30.8, 114.4), (30.2, 111.4)])
    fig.part('nfoot', nfoot, WHITE, cel=1.0, rim=0.6, cast=0.8,
             details=[(ribbon([(42.6, 110.6), (40.4, 113.0), (38.8, 114.4)], [0.2, 1.0, 0.6]), STRAW.base, 1),
                      (ribbon([(42.6, 110.6), (44.6, 112.6), (45.6, 114.3)], [0.2, 0.9, 0.5]), STRAW.base, 1),
                      (ellipse(42.6, 110.7, 0.9, 0.7), STRAW.light, 1)])
    ngreave = sm([(35.6, 102.4), (46.4, 102.2), (45.4, 107.0), (44.6, 111.0), (35.0, 111.2), (34.6, 107.0)], sharp=(0, 1))
    fig.part('ngreave', ngreave, LACQ, cel=1.2, rim=0.7, cast=0.9,
             details=[(sm([(34, 109.6), (46, 109.4), (46, 111.6), (34, 111.6)]), GOLD.base, 1),
                      (sm([(34, 109.6), (46, 109.4), (46, 110.2), (34, 110.4)]), GOLD.light, 1),
                      (ellipse(42.0, 106.0, 0.9, 0.9), GOLD.base, 1), (ellipse(42.2, 105.8, 0.4, 0.4), GOLD.hi, 1),
                      (ribbon([(44.2, 103.2), (43.8, 106), (43.2, 109)], [0.2, 1.0, 0.2]), LACQ.hi, 0.55)])
    nleg = limb([(52.6, 89.0), (48.8, 93.8), (45.2, 98.6), (41.8, 103.2)], [16.6, 15.6, 14.4, 13.4])
    fig.part('nleg', nleg, NAVY, cel=1.6, rim=0.7, cast=1.0, cast_on=['fleg', 'fgreave', 'ffoot'],
             details=[(ribbon([(50.4, 91.6), (45.6, 98.0), (41.6, 104.6)], [0.2, 1.1, 0.2]), NAVY.shadow, 0.8),
                      (ribbon([(55.6, 93.4), (51.0, 99.6), (47.2, 104.6)], [0.2, 0.9, 0.2]), NAVY.light, 0.65),
                      (ribbon([(45.8, 93.4), (40.8, 99.6), (37.2, 104.2)], [0.2, 0.8, 0.2]), NAVY.deep, 0.45)])

    # ---- la jupe de plaques (kusazuri) : trois rangées, la plus basse d'abord ; un laçage par panneau ----
    KZR = [((39.4, 74.6), (91.0, 75.6), 7.8), ((37.8, 80.8), (92.0, 81.6), 8.0), ((36.2, 87.0), (93.0, 87.6), 8.2)]
    for i in (2, 1, 0):
        (xl, yl), (xr, yr), h = KZR[i]
        mid = (64.0, max(yl, yr) + 2.0)
        sag = 1.5
        notch = []
        for xn in (55.0, 73.5):
            t = (xn - xl) / (xr - xl)
            yb = yl + h + (yr - yl) * t + sag * math.sin(math.pi * t)
            notch.append((xn, yb))
        pts = [(xl, yl), mid, (xr, yr), (xr + 0.8, yr + h * 0.55), (xr + 0.6, yr + h),
               (notch[1][0] + 1.2, notch[1][1] + 0.3), (notch[1][0], notch[1][1] - 0.9), (notch[1][0] - 1.2, notch[1][1] + 0.3),
               (notch[0][0] + 1.2, notch[0][1] + 0.4), (notch[0][0], notch[0][1] - 0.9), (notch[0][0] - 1.2, notch[0][1] + 0.4),
               (xl - 0.6, yl + h), (xl - 0.8, yl + h * 0.5)]
        sh = sm(pts, sharp=(0, 2, 4, 5, 6, 7, 8, 9, 10, 11), t=0.75)
        det = [(sm([(xl - 1, yl), mid, (xr + 1, yr), (xr + 1, yr + 1.6), (mid[0], mid[1] + 1.6), (xl - 1, yl + 1.6)], sharp=(0, 2, 3, 5)), LACQ.light, 0.5)]
        for xn, yb in notch:
            det += [(ribbon([(xn - 0.2, yb - h + 1.4), (xn, yb - h * 0.5), (xn, yb - 0.6)], [0.2, 0.9, 0.3]), LACQ.deep, 0.45),
                    (ribbon([(xn + 0.8, yb - h + 1.6), (xn + 0.8, yb - h * 0.5), (xn + 0.8, yb - 0.8)], [0.1, 0.5, 0.1]), LACQ.hi, 0.35)]
        for xc in (46.0, 64.4, 83.0):
            t = (xc - xl) / (xr - xl)
            yb = yl + h + (yr - yl) * t + sag * math.sin(math.pi * t)
            det += lace(xc, yb - 2.2, 2.6, 1.15)
        if i == 2:
            det += [(sm([(xl - 2, yl + h - 1.4), (64, yl + h + 0.4), (xr + 2, yr + h - 1.4), (xr + 2, yr + h + 3), (64, yl + h + 4), (xl - 2, yl + h + 3)]), GOLD.base, 1)]
        fig.part('kz%d' % i, sh, LACQ, cel=1.2, rim=0.6, cast=1.0, details=det)

    # ---- la cuirasse en tonneau (dō) : liseré d'or en haut, bande d'or, plaque basse, blason de vague ----
    do = sm([(54.0, 55.4), (63.0, 53.2), (72.0, 52.6), (82.0, 53.0), (89.4, 54.6), (92.0, 59.0), (92.6, 66.0), (91.4, 73.0),
             (89.6, 78.2), (72.0, 79.8), (56.0, 78.8), (53.4, 72.0), (53.0, 62.0)])
    det = [(do, ('lin', 54, 66, 72, 64, [(0, LACQ.deep, 0.5), (1, LACQ.deep, 0)]), 1),
           (sm([(52, 53.8), (63, 51.8), (72, 51.2), (82, 51.6), (93, 53.4), (93.6, 57.4), (82, 55.8), (72, 55.4), (63, 56.0), (52, 58.0)]), GOLD.base, 1),
           (sm([(52, 53.8), (63, 51.8), (72, 51.2), (82, 51.6), (93, 53.4), (93.6, 55.0), (82, 53.6), (72, 53.2), (63, 53.8), (52, 55.6)]), GOLD.light, 1),
           (sm([(52, 70.2), (72, 71.6), (93, 70.0), (93, 72.6), (72, 74.2), (52, 72.8)]), GOLD.base, 1),
           (sm([(52, 70.2), (72, 71.6), (93, 70.0), (93, 70.9), (72, 72.5), (52, 71.1)]), GOLD.light, 1),
           (sm([(52, 72.8), (72, 74.2), (93, 72.6), (93, 74.2), (72, 75.8), (52, 74.4)]), LACQ.deep, 0.45),
           (ellipse(84.6, 62.6, 2.3, 5.4, 8), LACQ.hi, 0.32), (ellipse(85.4, 59.6, 0.9, 1.6, 8), '#ffe4cc', 0.7),
           (ellipse(86.0, 76.2, 2.6, 1.0, -4), LACQ.hi, 0.3)]
    em = wave_sign(69.6, 63.2, 3.6)
    det += [(em.move(-0.35, 0.45), GOLD.shadow, 0.9), (em, ('lin', 66, 60, 72, 67, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.base)]), 1)]
    fig.part('do', do, LACQ, cel=2.0, rim=0.8, cast=1.2, details=det, occl=(LACQ.deep, 0.25, 3.2))

    # ---- le gorgerin sombre sous le menton ----
    gorget = sm([(59.6, 52.6), (66, 50.4), (76, 50.2), (84.4, 51.8), (85.4, 54.6), (78, 56.6), (68, 56.8), (60.4, 55.6)])
    fig.part('gorget', gorget, NAVY, cel=0.8, rim=0.5, cast=0.8)

    # ---- le sabre : où sont la garde, les poings, les poignets ----
    O = P['O']
    ang, sg = P['ang'], P['edge']
    st_ = 1 + 0.035 * P['stretch']

    def loc(p):                       # repère du sabre → dessin (avant le squelette du haut du corps)
        r_ = rot((p[0], p[1] * sg), ang)
        return (O[0] + r_[0], O[1] + r_[1])

    def xs(sh):
        return xf(sh, O[0], O[1], ang, 1, sg)

    def xb(sh):
        return xf(sh, O[0], O[1], ang, st_, sg)

    WN, WF = loc(WRIST_N), loc(WRIST_F)
    SNp = (S_N0[0] + P['shn'][0], S_N0[1] - 0.5 * br - P['lift'] + P['shn'][1])
    SFp = (S_F0[0] + P['shf'][0], S_F0[1] - 0.5 * br - P['lift'] * 0.7 + P['shf'][1])
    EN = ik(SNp, WN, L_N[0], L_N[1], P['bn'])
    EF = ik(SFp, WF, L_F[0], L_F[1], P['bf'])

    def arm(name, S, E, W, w0, w1, w2, cast_on):
        """Un bras d'un seul tenant (manche bleu nuit) : plaque de fer sur l'avant-bras, cubitière, poignet d'or."""
        sh = bent(S, E, W, w0, w1, w2, bulge=(0.04, 0.06))
        fa = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0]))
        Lf = math.dist(E, W)
        nx, ny = rot((0, 1), fa)
        sgn = -1 if (nx * 0.6 - ny * 0.8) > 0 else 1        # le côté de l'avant-bras tourné vers la lumière
        F = lambda s: xf(s, E[0], E[1], fa)
        d = [(F(rpoly([(Lf * 0.16, -3.0 * sgn), (Lf * 0.82, -2.6 * sgn), (Lf * 0.82, 0.6 * sgn), (Lf * 0.16, 0.9 * sgn)], 1.0)), STEEL.base, 1),
             (F(rpoly([(Lf * 0.18, -3.0 * sgn), (Lf * 0.8, -2.6 * sgn), (Lf * 0.8, -1.5 * sgn), (Lf * 0.18, -1.7 * sgn)], 0.6)), STEEL.light, 1),
             (F(ellipse(Lf * 0.5, -2.4 * sgn, 2.0, 0.35)), STEEL.hi, 0.9),
             (F(ribbon([(Lf * 0.2, 1.4 * sgn), (Lf * 0.5, 1.8 * sgn), (Lf * 0.8, 1.6 * sgn)], [0.2, 0.9, 0.2])), NAVY.deep, 0.6),
             (F(rpoly([(-2.6, -3.4), (2.2, -3.6), (3.0, 0), (2.2, 3.6), (-2.6, 3.4), (-3.4, 0)], 1.6)), STEEL.shadow, 1),
             (F(rpoly([(-2.2, -3.0), (1.8, -3.2), (2.4, -0.2), (0, -0.6), (-2.8, -0.4)], 1.2)), STEEL.light, 0.95),
             (F(ellipse(-0.2, -2.0, 1.0, 0.45)), STEEL.hi, 0.9),
             (F(rpoly([(Lf - 1.8, -4.4), (Lf + 1.0, -4.4), (Lf + 1.0, 4.4), (Lf - 1.8, 4.4)], 0.4)), GOLD.base, 1),
             (F(rpoly([(Lf - 1.8, -4.4), (Lf - 0.7, -4.4), (Lf - 0.7, 4.4), (Lf - 1.8, 4.4)], 0.3)), GOLD.light, 1)]
        fig.part(name, sh, NAVY, cel=1.3, rim=0.6, cast=1.0, cast_on=cast_on, details=d)

    # ---- le bras lointain : il sort de sous l'épaulière lointaine, l'avant-bras passe devant la cuirasse ----
    arm('farm', SFp, EF, WF, 9.0, 8.0, 6.6, ['do', 'kz0', 'kz1', 'kz2', 'fleg', 'gorget'])
    fs = plate_parts(fig, 'fs', [(FS_X[0] + 0.15 * i, FS_Y + FS_STEP * i, FS_X[1] + 0.3 * i, FS_Y + FS_H + FS_STEP * i) for i in range(FS_N)],
                     cords=(0.58,), gold_top=True, gold_bot=True, cast=0.8, tilt=0.3)

    def sword():
        blade = sm([(2.4, -1.55), (16, -1.85), (30, -2.45), (42, -3.25), (BLADE_L, -4.35), (46.4, -2.2), (42.6, -1.0),
                    (30, -0.15), (16, 0.35), (2.4, 0.55)], sharp=(0, 4, 9), t=0.6)
        edge = sm([(2.4, -0.15), (16, -0.3), (30, -0.8), (42.6, -1.5), (46.4, -2.6), (BLADE_L, -4.35), (46.2, -2.3), (42.6, -1.0),
                   (30, -0.15), (16, 0.35), (2.4, 0.55)], sharp=(0, 5, 10), t=0.6)
        back = sm([(2.4, -1.55), (16, -1.85), (30, -2.45), (42, -3.25), (BLADE_L, -4.35), (42, -2.8), (30, -2.05), (16, -1.45), (2.4, -1.15)],
                  sharp=(0, 4, 8), t=0.6)
        fig.part('blade', xb(blade), BLADE, cel=0, rim=0, cast=0,
                 details=[(xb(blade), ('lin', *loc((0, -1.8)), *loc((0, 0.6)), [(0, BLADE.base), (0.55, BLADE.light), (1, BLADE.hi)]), 1),
                          (xb(back), BLADE.shadow, 1),
                          (xb(edge), ('lin', *loc((0, -0.6)), *loc((0, 0.6)), [(0, BLADE.light), (1, '#ffffff')]), 1),
                          (xb(ribbon([(6, -0.9), (24, -1.25), (40, -2.0)], [0.1, 0.45, 0.1])), '#ffffff', 0.85)])
        fig.part('habaki', xs(rpoly([(0.6, -2.1), (3.4, -1.8), (3.4, 0.85), (0.6, 1.1)], 0.4)), GOLD, cel=0.4, rim=0.4, cast=0.5)
        fig.part('tsuba', xs(sm([(1.2, -4.6), (1.4, 0), (1.2, 4.4), (-0.8, 4.8), (-1.4, 0), (-0.8, -5.0)])), GOLD, cel=0.7, rim=0.6, cast=0.7,
                 details=[(xs(ellipse(0.2, -0.1, 0.5, 1.6)), GOLD.shadow, 0.9)])
        fig.part('tsuka', xs(rpoly([(-0.8, -1.75), (-17.2, -1.6), (-17.2, 1.6), (-0.8, 1.75)], 0.5)), BRAID, cel=0.5, rim=0.4, cast=0.5,
                 details=[(xs(sm([(u - 1.0, 0), (u, -1.5), (u + 1.0, 0), (u, 1.5)], sharp=(0, 1, 2, 3))), NAVY.base, 1)
                          for u in (-9.0, -15.4)] + [(xs(ellipse(-9.4, -0.8, 0.5, 0.3)), NAVY.light, 0.8)])
        fig.part('kashira', xs(sm([(-16.8, -2.0), (-19.0, -1.6), (-19.6, 0), (-19.0, 1.6), (-16.8, 2.0)], sharp=(0, 4))), GOLD, cel=0.5, rim=0.5, cast=0.6)
        # le poing lointain (main gauche), sous l'autre, arrivé par le côté du fil
        fist(name='ffist', c=FIST_F, side=-1)

    def fist(name, c, side):
        """Un poing serré sur la poignée : le dos de la main du côté du poignet, quatre doigts repliés en travers de la
        poignée (séparés par des plis doux), la rangée des jointures éclairée."""
        cx, cy = c
        s = side
        pts = [(cx + 2.9, -4.6 * s), (cx, -5.4 * s), (cx - 2.9, -4.8 * s), (cx - 3.3, -0.4 * s), (cx - 3.0, 3.4 * s),
               (cx, 3.9 * s), (cx + 2.9, 3.4 * s), (cx + 3.3, -0.4 * s)]
        pts = [(x, y + cy) for x, y in pts]
        L = xs
        d = [(L(sm([(cx + 2.9, cy - 4.6 * s), (cx, cy - 5.4 * s), (cx - 2.9, cy - 4.8 * s), (cx - 3.1, cy - 0.6 * s), (cx + 3.1, cy - 0.6 * s)])), SKIN.light, 0.5)]
        seg = [(cx + 2.9, cx + 1.45), (cx + 1.35, cx - 0.1), (cx - 0.2, cx - 1.7), (cx - 1.8, cx - 3.1)]
        for k, (u0, u1) in enumerate(seg):
            v1 = (3.6 - 0.3 * abs(k - 1.2)) * s
            fg = L(rpoly([(u0, cy - 0.4 * s), (u1, cy - 0.4 * s), (u1, cy + v1), (u0, cy + v1)], [0.5, 0.5, 0.75, 0.75]))
            a_, b_ = loc(((u0 + u1) / 2, cy - 0.4 * s)), loc(((u0 + u1) / 2, cy + v1))
            d += [(fg, ('lin', a_[0], a_[1], b_[0], b_[1], [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]), 1),
                  (L(ribbon([(u1 + 0.05, cy + 0.1 * s), (u1, cy + v1 * 0.55), (u1 + 0.1, cy + v1 - 0.3 * s)], [0.1, 0.5, 0.1])), SKIN.deep, 0.55)]
        d += [(L(ribbon([(cx + 2.6, cy - 0.5 * s), (cx, cy - 0.7 * s), (cx - 2.8, cy - 0.5 * s)], [0.1, 0.7, 0.1])), SKIN.hi, 0.45)]
        fig.part(name, L(sm(pts)), SKIN, cel=1.0, rim=0.6, cast=0.9, details=d)

    # ---- l'ordre : sabre et poing lointain, bras proche, épaulière proche, poing proche, puis la tête ----
    if not P['sw_front']:
        sword()
    arm('narm', SNp, EN, WN, 9.2, 8.0, 6.6, ['do', 'kz0', 'kz1', 'kz2', 'farm', 'gorget', 'tsuka', 'ffist', 'nleg', 'fleg'])
    ns = plate_parts(fig, 'ns', [(NS_X[0] - 0.45 * i, NS_Y + NS_STEP * i, NS_X[1] + 0.12 * i, NS_Y + NS_H + NS_STEP * i) for i in range(NS_N)],
                     cords=(0.27, 0.66), gold_top=True, gold_bot=True, cast=1.0, tilt=0.15)

    def near_fist():
        fist(name='nfist', c=FIST_N, side=1)
        thumb = xs(limb([(FIST_N[0] - 1.8, -3.6), (FIST_N[0] + 1.4, -2.6), (FIST_N[0] + 3.3, -1.2)], [2.4, 2.1, 1.8]))
        fig.part('nthumb', thumb, SKIN, cel=0.6, rim=0.5, cast=0.6, cast_on=['nfist', 'tsuka', 'tsuba'])
    if not P['sw_front']:
        near_fist()

    # ---- la tête (agrandie ×1,1) ----
    hd = head(fig, P)
    if P['sw_front']:
        sword()
        near_fist()

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(hd, HEAD)
    fig.pose(['do'], TOR)
    fig.pose(['gorget', 'saya', 'kojiri', 'blade', 'habaki', 'tsuba', 'tsuka', 'kashira', 'ffist', 'nfist', 'nthumb',
              'farm', 'narm'], U)
    fig.pose(['kz0', 'kz1', 'kz2'], KZ)
    fig.pose(ns, SN)
    fig.pose(fs, SF)
    fig.pose(['fleg', 'nleg'], LEG)
    # ce que les effets doivent savoir (repère du dessin)
    tip = mapp(U, loc((BLADE_L * st_, -4.35)))
    fig.ctx = dict(HEAD=HEAD, U=U, O=mapp(U, O), ang=ang + P['lean'] * 1.0, tip=tip, P=P, chest=mapp(TOR, (72, 66)),
                   head=mapp(HEAD, (74, 40)), crest=mapp(HEAD, (75, 2)), EN=mapp(U, EN), EF=mapp(U, EF),
                   WN=mapp(U, WN), WF=mapp(U, WF))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def head(fig, P):
    """La tête casquée : protège-nuque, visage dans l'ombre, bol laqué, aileron, visière, cache-cou, croissant."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- le protège-nuque (shikoro) : trois plaques en paliers, la plus basse (la plus large) d'abord ----
    SH = [((40.6, 37.0), (60.0, 36.4), 6.2), ((37.4, 42.0), (60.0, 41.6), 6.0), ((34.0, 46.8), (60.0, 46.4), 6.0)]
    for i in (2, 1, 0):
        (xl, yl), (xr, yr), h = SH[i]
        sh = sm([(xl + 1.2, yl), (xr, yr), (xr + 0.6, yr + h), ((xl + xr) / 2, yl + h + 0.8), (xl - 0.6, yl + h + 0.4), (xl, yl + h * 0.5)],
                sharp=(0, 1, 2, 4), t=0.7)
        det = [(sm([(xl, yl - 0.4), (xr, yr - 0.4), (xr, yr + 1.4), (xl, yl + 1.6)], sharp=(0, 1, 2, 3)), LACQ.light, 0.45),
               (sm([(xl - 1, yl + h - 1.0), ((xl + xr) / 2, yl + h - 0.2), (xr + 1, yr + h - 1.0), (xr + 1, yr + h + 1.5), (xl - 1, yl + h + 1.5)]), GOLD.base, 1),
               (sm([(xl - 1, yl + h - 1.0), ((xl + xr) / 2, yl + h - 0.2), (xr + 1, yr + h - 1.0), (xr + 1, yr + h - 0.3), (xl - 1, yl + h - 0.3)]), GOLD.light, 0.9)]
        for xc in ((0.18, 0.5) if i == 2 else (0.22, 0.56)):
            det += lace(xl + (xr - xl) * xc, yl + h - 2.6, 2.2, 1.05)
        part('shik%d' % i, sh, LACQ, grad=(xr, yl, xl, yl + h, [(0, LACQ.base), (0.6, LACQ.shadow), (1, LACQ.deep)]),
             cel=1.0, rim=0.5, cast=1.0, details=det)

    # ---- le visage, dans l'ombre de la visière : seuls les yeux ambre se voient, sous de gros sourcils froncés ----
    # Places et tailles des yeux : visage.py (boîte FACE_BOX : l'ovale de la face sous le casque et le cache-cou).
    V = placer(FACE_BOX)
    face = sm([(57.6, 33.6), (80, 33.0), (87.4, 35.0), (88.0, 40.0), (86.0, 46.0), (70, 47.0), (57.6, 46.0)])
    fd = [(face, ('lin', 72, 35, 72, 42.5, [(0, SKIN.deep), (0.45, SKIN.shadow), (1, SKIN.base)]), 1),
          (sm([(84.6, 38.8), (87.4, 38.6), (87.6, 42.0), (85.0, 42.4)]), SKIN.base, 0.9)]
    # positions RÉELLES des traits (pour verifier() de visage.py) ; nez et bouche sont cachés sous le cache-cou, à leur place
    fig.face = {'nez': V['nez'], 'bouche': V['bouche']}
    for key, (cx_, cy_, w_), tpl, irx in (('oeil_proche', V['oeil_proche'], EYE_N, 0.8), ('oeil_fond', V['oeil_fond'], EYE_F, 0.45)):
        k_ = w_ / 7.2
        e = sm([(cx_ + px * k_, cy_ + py) for px, py in tpl], sharp=(0, 3))
        bx = e.bbox()
        fig.face[key] = ((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2, bx[2] - bx[0])
        cx, cy, r = cx_ + irx * k_, cy_, 2.1 * min(1.0, k_ * 1.0) if tpl is EYE_N else 2.1 * k_ * 0.97
        if P['blink'] > 0.5:
            fd += [(e.scale(1.12, 1.4, cx - 0.6, cy), SKIN.deep, 0.95), (e.move(0, -0.3), SKIN.shadow, 1),
                   (ribbon([(cx - 3.4 * k_, cy + 0.6), (cx - 0.6 * k_, cy + 0.9), (cx + 2.2 * k_, cy + 0.4)], [0.1, 0.5, 0.1]), SKIN.deep, 1)]
        else:
            fd += [(e.scale(1.14, 1.42, cx - 0.4, cy), '#2a0c1c', 0.95), (e, EYE[0], 1),
                   (ellipse(cx, cy, r * 0.62, r * 0.62), ('rad', cx + 0.2, cy - 0.2, r * 0.7, r * 0.7, [(0, '#fff0a0'), (0.45, EYE[1]), (1, EYE[2])]), 1),
                   (ellipse(cx + 0.1, cy + 0.05, r * 0.26, r * 0.34), EYE[3], 1),
                   (ellipse(cx + 0.45, cy - 0.45, r * 0.16, r * 0.16), '#ffffff', 1),
                   (sm([(e.bbox()[0], cy - 1.2), (e.bbox()[2], cy - 1.4), (e.bbox()[2], cy - 0.4), (e.bbox()[0], cy - 0.3)]), '#2a0c1c', 0.35)]
    # sourcils blancs, gros et froncés (le bout intérieur descend vers la racine du nez, sur la médiane)
    browN = sm([(59.6, 37.0), (63.4, 36.0), (67.8, 36.6), (71.4, 38.0), (73.2, 39.8), (70.0, 39.2), (66.0, 38.4), (62.0, 38.6), (59.8, 38.8)],
               sharp=(4,), t=0.85)
    fb = lambda x: 77.6 + (x - 75.6) * 0.88    # sourcil du fond, posé au-dessus de l'œil du fond (visage.py)
    browF = sm([(fb(75.6), 39.8), (fb(77.4), 38.0), (fb(80.6), 36.6), (fb(84.4), 36.4), (fb(86.2), 37.2), (fb(84.4), 38.2), (fb(81.2), 38.4), (fb(78.0), 39.4)],
               sharp=(0,), t=0.85)
    for b in (browN, browF):
        fd += [(b.move(-0.3, 0.6), SKIN.deep, 0.7), (b, ('lin', 0, 36, 0, 39.5, [(0, WHITE.hi), (0.6, WHITE.base), (1, WHITE.shadow)]), 1)]
    part('face', face, SKIN, cel=0, rim=0, cast=0, details=fd)

    # ---- le bol du casque, laqué rouge, avec un grand reflet ----
    bowl = sm([(49.2, 37.0), (49.8, 30.0), (54.0, 24.4), (60.8, 21.0), (68.6, 20.0), (76.4, 21.4), (82.4, 25.0), (86.0, 29.8),
               (87.0, 34.0), (70, 34.6), (56, 35.6)], sharp=(8, 9, 10))
    part('bowl', bowl, LACQ, grad=(84, 21, 54, 34, [(0, LACQ.light), (0.45, LACQ.base), (1, LACQ.shadow)]), cel=1.6, rim=0.8, cast=1.0,
         details=[(ribbon([(58.4, 26.2), (63.6, 22.8), (70.6, 21.8), (77.4, 23.8)], [0.3, 2.0, 2.2, 0.3]), LACQ.hi, 0.55),
                  (ellipse(71.6, 22.6, 2.2, 0.8, -4), '#ffe6d0', 0.8),
                  (ribbon([(52.0, 33.0), (54.2, 27.8), (58.6, 24.0)], [0.2, 1.6, 0.2]), LACQ.deep, 0.45)])

    # ---- l'aileron retourné (fukigaeshi), liseré d'or, blason de vague ----
    fuki = sm([(44.0, 33.6), (51.0, 31.6), (58.8, 32.0), (59.6, 38.0), (58.6, 43.8), (51.0, 44.6), (44.6, 43.8), (42.6, 38.6)])
    em = wave_sign(51.6, 38.0, 3.0)
    part('fuki', fuki, LACQ, cel=1.2, rim=0.7, cast=1.1,
         details=[(ring_of(fuki, 0.84, 51.4, 38.0), GOLD.base, 1),
                  (sm([(44.4, 33.0), (52.8, 31.4), (58.8, 32.2), (59.2, 33.8), (52.8, 32.8), (44.8, 34.4)]), GOLD.light, 1),
                  (em.move(-0.3, 0.4), GOLD.shadow, 0.9), (em, ('lin', 49, 35, 54, 41, [(0, GOLD.hi), (0.5, GOLD.light), (1, GOLD.base)]), 1)])

    # ---- la visière qui avance (mabizashi) : dessus éclairé, liseré d'or dessous ----
    visor = sm([(56.6, 32.6), (66, 31.4), (78, 30.8), (86, 31.6), (90.6, 33.4), (89.6, 35.6), (80, 36.2), (68, 36.4), (57.2, 36.8)],
               sharp=(4,), t=0.8)
    part('visor', visor, LACQ, grad=(90, 31, 60, 36, [(0, LACQ.hi), (0.35, LACQ.light), (1, LACQ.base)]), cel=0.9, rim=0.7, cast=1.3,
         cast_on=['face', 'bowl', 'shik0', 'shik1', 'shik2'],
         details=[(sm([(56, 35.2), (68, 34.8), (80, 34.6), (90, 34.0), (90.4, 36.4), (80, 36.6), (68, 36.8), (56, 37.4)]), GOLD.base, 1),
                  (sm([(56, 35.2), (68, 34.8), (80, 34.6), (90, 34.0), (90.2, 34.8), (80, 35.4), (68, 35.6), (56, 36.0)]), GOLD.light, 1),
                  (ellipse(84.6, 32.2, 2.0, 0.55, -6), '#ffe6d0', 0.8)])

    # ---- le cache-cou de tissu rouge (avis du propriétaire, 26/11) : il monte jusque sous les yeux et couvre tout le bas
    # du visage jusqu'au bord avant (plus de nez, de gueule ni de moustache) ; liseré d'or en haut, il descend dans le col.
    mask = sm([(57.8, 41.6), (68, 41.2), (78, 41.0), (85.2, 41.2), (88.2, 42.0), (88.9, 45.2), (88.7, 49.2), (87.6, 52.8),
               (84.8, 55.4), (76, 56.4), (66, 55.8), (60, 53.2), (57.6, 47.6)])
    md = [(sm([(56, 40.6), (88, 40.4), (90, 42.8), (68, 42.4), (56, 43.0)]), GOLD.base, 1),
          (sm([(56, 40.6), (88, 40.4), (90, 41.7), (68, 41.4), (56, 41.9)]), GOLD.light, 1),
          # la lumière (en haut à droite) sur le devant arrondi du tissu
          (sm([(82.0, 43.4), (86.6, 43.2), (88.0, 46.4), (87.4, 50.6), (85.0, 53.0), (83.2, 49.0)]), LACQ.light, 0.5),
          # deux plis doux : le tissu qui épouse le menton puis rentre dans le col, et qui se tend vers la joue
          (ribbon([(67.0, 54.0), (72.6, 55.0), (78.6, 54.9), (83.0, 53.6)], [0.1, 0.55, 0.5, 0.1]), LACQ.deep, 0.4),
          (ribbon([(61.0, 44.6), (62.2, 47.8), (64.8, 50.4)], [0.1, 0.6, 0.1]), LACQ.deep, 0.35)]
    part('mask', mask, LACQ, grad=(88, 42, 60, 54, [(0, LACQ.light), (0.5, LACQ.base), (1, LACQ.shadow)]), cel=1.3, rim=0.7, cast=1.1,
         cast_on=['face', 'shik0', 'shik1', 'shik2'], details=md)

    # ---- le grand croissant d'or (corne proche plus grande), la monture à gemme bleue ----
    hN = taper(crpath([(71.6, 26.8), (66.4, 24.4), (61.4, 20.4), (58.4, 14.8), (57.0, 8.8), (56.8, 3.4)], 20), 3.6, 1.1, wmid=3.0)
    hF = taper(crpath([(79.4, 26.0), (83.6, 22.8), (87.6, 17.6), (90.2, 11.4), (91.2, 5.6)], 18), 3.2, 1.0, wmid=2.7)
    for name, h in (('hornF', hF), ('hornN', hN)):
        part(name, h, GOLD, grad=(92, 4, 60, 26, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.base)]), cel=0.9, rim=0.6, cast=1.0,
             details=[(under(h, 0.5, -1.2), GOLD.shadow, 0.55)])
    mount = sm([(69.4, 28.0), (71.2, 24.6), (75.2, 23.2), (79.4, 24.2), (81.6, 27.2), (80.0, 30.4), (75.4, 31.4), (70.8, 30.6)])
    part('mount', mount, GOLD, cel=1.0, rim=0.7, cast=1.1,
         details=[(ellipse(75.6, 27.4, 2.5, 2.7), GOLD.shadow, 1),
                  (ellipse(75.5, 27.3, 2.0, 2.2), ('rad', 76.2, 26.4, 2.6, 2.6, [(0, WATER[1]), (0.45, WATER[3]), (1, WATER[5])]), 1),
                  (ellipse(76.3, 26.4, 0.65, 0.5, -30), '#ffffff', 1)])
    return names


def main():
    """zaroth.svg (grand) et zaroth-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/demons-8.webp (512 px de haut) et demons-8-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('zaroth', 0.95, 512, ID_JEU), ('zaroth-petit', 1.35, 160, ID_JEU + '-160')):
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
