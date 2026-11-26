# Karu (le corbeau-tengu du clan d'Orin, vent, rare, monstre de clan devenu héros ; dessin du jeu « mon-orin-rapide »)
# redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte de tous les héros, décision du
# propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py ; même famille qu'Orin : ../orin/orin.py).
#
#   python3 refonte-graphique/ui-moderne/heros/karu/karu.py      # → karu.svg + images 512 et 160 px de haut
#   python3 refonte-graphique/ui-moderne/heros/karu/karu.py --apercu <sortie.png> [hauteur]   # un aperçu (brouillon)
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/monstres/corbeau-tengu.txt) : un karasu-tengu, le petit
# tengu corbeau qui sert Orin. Une VRAIE tête de corbeau : gros bec gris-noir épais, un peu crochu, entrouvert (gorge
# rouge sombre), plumes noires bleutées et luisantes, yeux d'ambre ronds sous des sourcils de plumes froncés, plumes de
# nuque hérissées vers l'arrière, petit tokin noir laqué sur le front. Petit et sec, accroupi très bas, prêt à bondir,
# trois quarts vers la droite : jambe lointaine pliée devant (genou en avant), jambe proche repliée derrière, geta à
# plat ; ailes à demi ouvertes et levées vers l'arrière (la proche en éventail à gauche, la lointaine dépasse
# au-dessus) ; petite queue de corbeau sous la veste. Veste de yamabushi ivoire à grande manche, pompons rouges du
# yuigesa sur la poitrine, ceinture de soie rouge à pans, hakama prune bouffant, jambières et tabi ivoire, hanao
# rouge, geta à une dent. La serre proche (doigts écailleux, griffes claires) tient un kodachi à la hanche, lame
# pointée vers l'avant et le haut, contre le corps.
#
# Coordonnées = pixels du dessin pixel art (même toile, le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; le bras est d'un seul
# tenant dans sa manche (outils.bent : pas de couture au coude).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import crpath, bent, taper, ik, wing, unit, add, lerp, norm, sub_  # noqa: E402
from lib import Shape  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-orin-rapide'          # l'id du DESSIN dans le jeu (heroArt) : celui des images et de src/game/vecto.ts

# ---------- matières (celles d'Orin, son chef de clan : mêmes tons ; le bec et les serres d'un gris-noir plus chaud) ----------
RAVEN = Mat('#b6c0ea', '#6c72a8', '#48446e', '#2f2a4c', '#1a1530', glint='#e0e6ff')
RAVENF = Mat('#98a0cc', '#5a5c8c', '#3c3658', '#28223e', '#161124', glint='#c4ccf2')
BEAK = Mat('#e2d8e6', '#9a8ca0', '#6a5c72', '#43384c', '#261d30', glint='#ffffff')
CLAW = Mat('#ffffff', '#ece6f0', '#cfc6d8', '#958aa6', '#5e5272')
CLOTH = Mat('#fffaf0', '#f6ead6', '#e0cebe', '#a88ea2', '#6a5070')
HAKAMA = Mat('#a48aac', '#7e6486', '#5e4466', '#402c4a', '#28182e')
GOLD = Mat('#fff1a6', '#f8cc50', '#d8922a', '#965220', '#5a2a18')
STEEL = Mat('#f6f9ff', '#d2deee', '#9ca8c6', '#5c6488', '#33385a')
WOOD = Mat('#e2ac72', '#c89058', '#9c6436', '#6a3a24', '#3a1e1a')
SILK = Mat('#ffa088', '#ef5848', '#cc3036', '#8e1c34', '#581028')
LACQ = Mat('#9aa2d6', '#4c4c74', '#2c2842', '#1c1628', '#0e0a16', glint='#e8ecff')
EYE = ('#fff3c8', '#f2a826', '#b8620e', '#200c14')
GORGE = ('#3a0a1c', '#6c1426', '#a62028')

GRD = 116.0        # le sol (dessous des geta)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (1.0, 26.0, 114.0, 92.0)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   X : il bondit vers l'ennemi ; lift : il décolle ; breath : souffle 0..1 ; crouch : il se tasse (négatif : il
#   s'étire) ; lean : il se penche en avant (+) depuis les hanches ; head / tilt : la tête (l'oiseau qui pique) ;
#   blink : yeux fermés ; wn / wf : les ailes proche / lointaine (W, T, a_in, a_out, l_in, l_out, comme Orin) ;
#   ws : les plumes ondulent ; ph : phase des ondulations ; tail : la queue frétille (degrés) ; pg : les pans de la
#   ceinture ; sw : la manche se balance ; fh : le centre de la serre (repère du buste) ; sang : l'angle de la lame
#   (degrés, y vers le bas : −26,6 = vers l'avant et le haut).
HIP = (68.0, 92.0)                  # le pivot du buste
NECK = (77.0, 64.0)                 # le pivot (et le centre d'agrandissement) de la tête
HEAD_OFF = (1.2, 2.4)               # la tête agrandie, reposée plus bas et plus en avant
S_N = (60.4, 66.4)                  # l'épaule proche (dans la manche)
R_N = (60.0, 55.0)                  # l'attache de l'aile proche (derrière l'épaule)
R_F = (68.0, 52.0)                  # l'attache de l'aile lointaine
L1, L2 = 10.6, 9.6                  # bras, avant-bras (jusqu'au poignet)
SANG0 = -26.6                       # la lame monte de deux pixels par rangée (comme le dessin)
FH0 = (66.4, 83.0)                  # le centre de la serre, au repos
GRIP_S = -4.6                       # le centre de la serre sur la poignée (repère du sabre : x le long de la lame)
BLADE_L = 30.5

WINGS_N = dict(
    demi=((-20, -13), (-18, 2), 104, 176, 37, 21),
    haut=((-15, -21), (-14, -9), 138, 205, 34, 20),
    bas=((-22, -1), (-15, 9), 96, 148, 33, 19),
    grande=((-19, -24), (-19, -11), 128, 214, 37, 22),
    serre=((-16, -6), (-12, 6), 100, 140, 32, 16),
)
WINGS_F = dict(
    demi=((-11, -14), (-13, -3), 150, 194, 22, 16),
    haut=((-6, -19), (-10, -10), 170, 228, 22, 17),
    bas=((-15, -6), (-12, 3), 128, 170, 21, 15),
    grande=((-6, -22), (-12, -12), 166, 236, 24, 19),
    serre=((-10, -9), (-10, 0), 140, 175, 20, 14),
)


def wing_vals(d, state):
    (wx, wy), (tx, ty), ai, ao, li, lo = d[state]
    return [wx, wy, tx, ty, ai, ao, li, lo]


REST = dict(X=0.0, lift=0.0, breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0,
            wn=wing_vals(WINGS_N, 'demi'), wf=wing_vals(WINGS_F, 'demi'), ws=0.0, ph=0.0, tail=0.0, pg=0.0, sw=0.0,
            fh=FH0, sang=SANG0, open=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une plume : la forme moins elle-même décalée vers le haut-droit."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def fluff(cx, cy, r, n=9, k=0.93, a0=0.3):
    """Un pompon : une boule aux bords doucement bosselés (des lobes arrondis, jamais des rayons)."""
    pts = []
    for i in range(n * 2):
        a = a0 + math.pi * i / n
        rr = r if i % 2 == 0 else r * k
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return sm(pts, t=1.0)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    ph = P['ph']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.9
    ROOTM = mT(P['X'], -P['lift'])
    U = mchain(ROOTM, mT(P['lean'] * 0.3, dyb), mR(P['lean'] * 1.1, *HIP))       # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                           # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.018 * br, 74, 86))                             # le buste se gonfle
    # tête un peu plus grande (×1,1), posée un peu plus bas et plus en avant (elle pique vers l'ennemi, comme le dessin)
    HEAD = mchain(UC, mT(*P['head']), mT(*HEAD_OFF), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    CLO = mchain(U, mskx(-0.08 * P['pg'], 82))
    TAIL = mchain(U, mR(P['tail'], 57.0, 88.0))
    LEG = mchain(ROOTM, mS(1, 1 - dyb / 32, 0, GRD))                            # les jambes plient (pieds au sol)

    # ================================================================ les ailes (derrière tout)
    fw_names, fW, fT = wing(fig, 'wf', R_F, P['wf'], RAVENF, ph + 1.3, P['ws'], scale=0.78,
                            widths=[13.0, 13.0, 12.0, 11.4, 10.6, 9.6, 8.4, 7.2], cov=(0.85, 0.9))
    nw_names, nW, nT = wing(fig, 'wn', R_N, P['wn'], RAVEN, ph, P['ws'], scale=1.0,
                            widths=[14.0, 14.0, 13.0, 12.0, 9.0, 7.8, 7.0, 6.2])

    # ================================================================ la petite queue de corbeau (sous la veste)
    tail_names = []
    for k, (a, L, w) in enumerate(((158, 15.0, 6.4), (138, 17.0, 7.0), (147, 18.6, 7.4))):
        a = a + 2.5 * math.sin(ph * 1.3 + k)
        p0 = (58.0 + 1.2 * k, 86.0 + 0.6 * k)
        d = unit(a)
        sd = (-d[1], d[0])
        p3 = add(p0, d, L)
        sh = taper(crpath([p0, add(add(p0, d, L * 0.5), sd, 0.8), p3], 14), w, 1.2, tip='round', wmid=w * 0.95)
        nm = 'tail%d' % k
        tail_names.append(nm)
        fig.part(nm, sh, RAVEN, grad=(p0[0] + 3, p0[1] - 3, p3[0], p3[1], [(0, RAVEN.light), (0.45, RAVEN.base), (1, RAVEN.shadow)]),
                 cel=0.9, rim=0.5, cast=1.2,
                 details=[(ribbon([lerp(p0, p3, 0.15), lerp(p0, p3, 0.55), lerp(p0, p3, 0.92)], [0.1, 0.7, 0.1]), RAVEN.glint, 0.35)])

    # ================================================================ les jambes : geta, tabi et jambières
    def geta(key, x0, L=18.6):
        tooth = rpoly([(x0 + 5.0, 110.8), (x0 + 11.0, 110.8), (x0 + 10.8, GRD), (x0 + 5.2, GRD)], [0.4, 0.4, 0.8, 0.8])
        fig.part(key + 'tooth', tooth, WOOD, cel=1.0, rim=0.6, cast=0,
                 details=[(rpoly([(x0 + 5.0, 110.8), (x0 + 11.0, 110.8), (x0 + 11.0, 112.2), (x0 + 5.0, 112.2)], 0), WOOD.deep, 0.6)])
        board = rpoly([(x0, 108.2), (x0 + L, 108.2), (x0 + L, 111.8), (x0, 111.8)], [1.0, 1.4, 1.0, 1.0])
        fig.part(key + 'board', board, WOOD, cel=1.0, rim=0.7, cast=0.8,
                 details=[(rpoly([(x0 + 0.4, 108.2), (x0 + L - 0.4, 108.2), (x0 + L - 0.6, 109.4), (x0 + 0.6, 109.4)], 0.6), WOOD.hi, 0.7)])

    def hanao(bx, by, s=1.0):
        """La lanière rouge : un V renversé, du nœud entre les orteils vers les deux bords du pied."""
        return [(ribbon([(bx - 5.2 * s, by + 5.0), (bx - 2.4 * s, by + 1.4), (bx, by)], [0.9, 1.1, 0.8]), SILK.shadow, 1),
                (ribbon([(bx, by), (bx + 1.8 * s, by + 1.6), (bx + 3.6 * s, by + 4.0)], [0.8, 1.0, 0.8]), SILK.base, 1),
                (ellipse(bx + 0.1, by + 0.2, 1.1, 0.9), SILK.light, 1),
                (ellipse(bx + 0.4, by - 0.1, 0.45, 0.35), SILK.hi, 0.9)]

    geta('f', 80.0)
    geta('n', 33.2)
    # la jambe lointaine : genou en avant, la jambière tombe droite, le tabi pointe vers l'ennemi
    fshin = sm([(84.8, 95.6), (91.8, 95.6), (92.0, 101.4), (93.6, 104.0), (96.8, 105.8), (98.2, 107.6), (97.8, 108.6),
                (81.6, 108.6), (81.2, 106.6), (83.0, 104.0), (84.4, 100.6)], sharp=(6, 7))
    fig.part('fshin', fshin, CLOTH, cel=1.2, rim=0.7, cast=0.9,
             details=[(ribbon([(84.6, 101.2), (88.0, 101.9), (91.8, 101.2)], [0.1, 0.8, 0.1]), CLOTH.shadow, 0.5),
                      (ribbon([(85.2, 97.6), (88.4, 98.2), (91.4, 97.6)], [0.1, 0.6, 0.1]), CLOTH.shadow, 0.35),
                      (sm([(90.6, 103.6), (93.0, 103.6), (95.6, 105.2), (97.4, 107.0), (95.4, 107.6), (91.8, 106.4)]), CLOTH.light, 0.6)]
             + hanao(91.0, 103.6))
    # la jambe proche, repliée derrière : la jambière descend en biais du genou (sous le hakama) à la cheville
    nshin = sm([(52.4, 93.6), (59.8, 95.4), (58.4, 99.4), (52.6, 102.6), (49.4, 104.0), (50.8, 105.6), (51.4, 107.6),
                (51.0, 108.6), (34.8, 108.6), (34.4, 106.6), (36.4, 104.6), (40.0, 103.4), (44.0, 101.0), (48.2, 97.0)],
               sharp=(7, 8))
    fig.part('nshin', nshin, CLOTH, cel=1.3, rim=0.7, cast=0.9,
             details=[(ribbon([(41.6, 103.6), (44.4, 104.6), (47.6, 103.8)], [0.1, 0.8, 0.1]), CLOTH.shadow, 0.5),
                      (ribbon([(47.0, 98.6), (51.0, 99.6), (55.0, 98.6)], [0.1, 0.7, 0.1]), CLOTH.shadow, 0.4),
                      (sm([(48.0, 103.0), (49.6, 104.2), (50.8, 106.4), (50.2, 107.6), (47.6, 106.0)]), CLOTH.light, 0.55)]
             + hanao(45.2, 103.8, 0.9))

    # ================================================================ le hakama prune, bouffant
    fhaka = sm([(60.0, 83.4), (80.0, 83.0), (91.4, 84.0), (97.8, 86.6), (100.6, 90.6), (100.0, 95.0), (96.6, 97.8),
                (90.6, 98.6), (84.4, 98.0), (76.0, 97.6), (67.0, 96.6), (61.4, 92.6)])
    fig.part('fhaka', fhaka, HAKAMA, grad=(98, 84, 66, 98, [(0, HAKAMA.light), (0.5, HAKAMA.base), (1, HAKAMA.shadow)]),
             cel=1.8, rim=0.8, cast=1.0,
             details=[(ribbon([(70.0, 86.6), (80.0, 89.6), (90.0, 91.2), (97.0, 92.0)], [0.2, 1.4, 1.2, 0.2]), HAKAMA.hi, 0.35),
                      (ribbon([(68.0, 90.8), (78.0, 93.6), (88.0, 95.2), (94.0, 95.6)], [0.2, 1.6, 1.4, 0.2]), HAKAMA.shadow, 0.7),
                      (ribbon([(84.6, 95.2), (88.2, 97.6), (92.6, 97.4)], [0.1, 1.0, 0.1]), HAKAMA.deep, 0.5)],
             occl=(HAKAMA.deep, 0.3, 3.0))
    nhaka = sm([(50.6, 84.4), (63.6, 84.4), (66.0, 89.4), (64.8, 95.0), (61.0, 98.6), (54.4, 99.4), (49.4, 97.4),
                (47.8, 92.4), (48.6, 87.4)])
    fig.part('nhaka', nhaka, HAKAMA, grad=(64, 85, 48, 99, [(0, HAKAMA.light), (0.5, HAKAMA.base), (1, HAKAMA.shadow)]),
             cel=1.8, rim=0.8, cast=1.2, cast_on=['fhaka', 'fshin', 'nshin'] + tail_names,
             details=[(ribbon([(56.0, 87.0), (55.0, 92.0), (52.4, 97.4)], [0.2, 1.5, 0.2]), HAKAMA.shadow, 0.7),
                      (ribbon([(57.2, 87.2), (56.4, 92.0), (54.0, 97.0)], [0.1, 0.7, 0.1]), HAKAMA.hi, 0.35),
                      (ribbon([(61.6, 88.0), (62.4, 92.4), (60.6, 96.6)], [0.1, 0.9, 0.1]), HAKAMA.light, 0.5)],
             occl=(HAKAMA.deep, 0.3, 3.0))

    # ================================================================ le buste : veste ivoire, col croisé, pompons, ceinture
    torso = sm([(57.6, 63.2), (65.0, 60.8), (76.0, 60.2), (86.0, 61.0), (91.6, 63.6), (93.4, 69.0), (92.8, 76.0),
                (91.0, 82.0), (89.6, 87.0), (76.0, 87.6), (62.0, 87.2), (56.6, 81.0), (55.8, 71.0)])
    det = []
    # les plumes noires de la poitrine dans l'ouverture du col (un V), le revers lointain croisé par-dessus
    vee = sm([(70.0, 61.0), (87.0, 61.4), (84.6, 65.6), (81.4, 70.0), (79.0, 73.4), (76.2, 68.0), (72.6, 63.6)], sharp=(0, 1, 4))
    det += [(vee, ('lin', 86, 61, 72, 70, [(0, RAVEN.light), (0.5, RAVEN.base), (1, RAVEN.shadow)]), 1),
            (sm([(70.0, 61.0), (74.4, 61.2), (76.4, 65.0), (78.6, 70.0), (79.0, 73.4), (76.2, 68.0), (72.6, 63.6)], sharp=(0, 4)), RAVEN.deep, 0.5)]
    det += [(ribbon([(87.4, 61.6), (83.6, 67.4), (78.0, 74.6), (70.0, 82.0), (64.0, 87.0)], [0.3, 2.2, 2.2, 1.8, 0.4]), CLOTH.shadow, 0.55),
            (ribbon([(88.6, 61.8), (84.8, 67.6), (79.4, 74.6), (71.6, 82.0)], [0.2, 1.0, 0.9, 0.2]), CLOTH.hi, 0.85)]
    # le côté de la veste dans une ombre douce, quelques plis
    det += [(ribbon([(60.0, 66.0), (59.0, 73.0), (60.6, 80.0)], [0.2, 1.4, 0.2]), CLOTH.shadow, 0.45),
            (ribbon([(89.0, 66.0), (90.6, 72.0), (89.6, 78.0)], [0.2, 1.2, 0.2]), CLOTH.light, 0.6)]
    # la ceinture de soie rouge : elle fait le tour (peinte dans le buste, d'un bord à l'autre)
    sash = sm([(50.0, 80.2), (70.0, 80.6), (96.0, 79.6), (96.0, 88.0), (70.0, 88.6), (50.0, 88.2)])
    det += [(sash, ('lin', 0, 80.2, 0, 88.0, [(0, SILK.light), (0.4, SILK.base), (1, SILK.shadow)]), 1),
            (ribbon([(58.0, 81.4), (72.0, 81.8), (90.0, 81.0)], [0.2, 0.9, 0.2]), SILK.hi, 0.55),
            (ribbon([(58.0, 86.4), (72.0, 86.8), (90.0, 86.2)], [0.2, 1.2, 0.2]), SILK.deep, 0.5),
            (ribbon([(54.0, 80.4), (72.0, 80.8), (94.0, 79.8)], [0.2, 0.9, 0.2]), CLOTH.deep, 0.35)]
    fig.part('torso', torso, CLOTH, grad=(92, 62, 60, 86, [(0, CLOTH.light), (0.55, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.8, rim=0.8, cast=1.3, details=det, occl=(CLOTH.shadow, 0.3, 3.2))
    # les pompons rouges du yuigesa (deux colonnes sur la poitrine)
    pom_names = []
    for k, (x, y, r) in enumerate(((74.2, 68.4, 2.1), (87.4, 67.4, 1.9), (73.2, 75.0, 2.2), (88.4, 74.0, 2.0))):
        sh = fluff(x, y, r, a0=0.3 + k)
        nm = 'pom%d' % k
        pom_names.append(nm)
        fig.part(nm, sh, SILK, grad=None, cel=0, rim=0, cast=0.7, cast_on=['torso'],
                 details=[(sh, ('rad', x + 0.6 * r, y - 0.6 * r, r * 1.9, r * 1.9, [(0, SILK.hi), (0.35, SILK.light), (0.7, SILK.base), (1, SILK.shadow)]), 1),
                          (ellipse(x - 0.3 * r, y + 0.4 * r, 0.55 * r, 0.3 * r, -30), SILK.deep, 0.35),
                          (ellipse(x + 0.42 * r, y - 0.45 * r, 0.32 * r, 0.24 * r, -35), '#ffe6dc', 0.9)])

    # ---- le nœud de la ceinture et ses deux pans (ils se balancent) ----
    tail1 = sm([(83.0, 85.6), (85.6, 85.4), (86.0, 89.6), (85.6, 93.2), (84.4, 94.8), (83.4, 93.0), (82.8, 89.4)], sharp=(4,))
    tail2 = sm([(86.6, 85.4), (89.0, 85.2), (89.8, 88.4), (90.4, 91.6), (89.4, 93.0), (88.2, 91.6), (87.2, 88.8)], sharp=(4,))
    fig.part('pan2', tail2, SILK, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(88.4, 86.8), (89.0, 89.6), (89.6, 92.6)], [0.2, 0.7, 0.1]), SILK.shadow, 0.6)])
    fig.part('pan1', tail1, SILK, cel=1.0, rim=0.6, cast=1.0,
             details=[(ribbon([(83.6, 86.8), (84.0, 90.4), (84.2, 94.0)], [0.2, 0.8, 0.1]), SILK.shadow, 0.6)])
    knot = sm([(82.4, 81.2), (85.8, 82.4), (89.2, 80.8), (90.2, 84.2), (89.0, 87.4), (85.8, 85.8), (82.4, 87.2), (81.4, 84.2)],
              sharp=(1, 5))
    fig.part('knot', knot, SILK, cel=0.9, rim=0.7, cast=1.1,
             details=[(ellipse(85.8, 84.1, 1.6, 1.9), SILK.light, 0.9),
                      (ellipse(86.2, 83.6, 0.7, 0.7), SILK.hi, 0.6),
                      (ribbon([(82.6, 85.6), (84.0, 85.2), (84.6, 84.4)], [0.1, 0.6, 0.1]), SILK.deep, 0.5),
                      (ribbon([(87.4, 85.0), (88.4, 85.6), (89.2, 86.4)], [0.1, 0.5, 0.1]), SILK.deep, 0.45)])

    # ================================================================ la tête de corbeau (agrandie ×1,1 autour du cou)
    # les plumes de nuque hérissées vers l'arrière (derrière la tête) : une seule forme à quelques pointes inégales
    ruff = sm([(70.0, 41.0), (64.6, 40.2), (58.0, 38.6), (61.8, 42.6), (55.0, 44.2), (60.6, 46.6), (54.4, 50.6),
               (60.2, 52.0), (55.8, 56.6), (61.8, 57.4), (60.0, 62.0), (66.0, 61.0), (68.0, 52.0)],
              sharp=(2, 4, 6, 8, 10))
    fig.part('ruff', ruff, RAVEN, grad=(70, 40, 56, 58, [(0, RAVEN.light), (0.5, RAVEN.base), (1, RAVEN.shadow)]),
             cel=1.0, rim=0.6, cast=1.3,
             details=[(ribbon([(66.0, 42.0), (61.0, 41.4), (59.0, 40.0)], [0.2, 0.7, 0.1]), RAVEN.hi, 0.6),
                      (ribbon([(64.6, 46.0), (60.0, 45.6), (57.0, 45.0)], [0.2, 0.6, 0.1]), RAVEN.light, 0.5),
                      (ribbon([(64.2, 51.0), (59.0, 51.0), (56.8, 51.0)], [0.2, 0.6, 0.1]), RAVEN.light, 0.4)])
    # la tête : crâne rond, front qui avance au-dessus du bec, gorge en petites pointes de plumes sur le col
    head = sm([(62.6, 48.4), (64.6, 42.6), (69.4, 38.4), (76.0, 36.2), (82.6, 35.8), (88.0, 37.6), (91.2, 41.0),
               (92.6, 44.6), (92.2, 49.0), (90.4, 53.4), (88.4, 58.4), (87.4, 62.6), (85.6, 65.4), (82.6, 64.4),
               (80.8, 67.4), (78.0, 65.6), (75.6, 68.0), (73.4, 65.4), (70.4, 66.6), (68.8, 63.8), (65.6, 62.6),
               (63.6, 58.4), (62.4, 53.4)], sharp=(12, 13, 14, 15, 16, 17, 18, 19))
    hd = []
    # les plans : le côté vers la nuque dans l'ombre, le front éclairé en haut à droite ; petites plumes couchées
    hd += [(sm([(62.6, 48.4), (64.6, 42.6), (68.6, 39.0), (68.0, 44.6), (69.6, 50.0), (68.4, 55.0), (70.4, 60.4),
                (68.8, 63.8), (65.6, 62.6), (63.6, 58.4), (62.4, 53.4)], sharp=(3, 5, 7)), RAVEN.shadow, 0.75),
           (sm([(76.0, 37.4), (82.6, 36.8), (88.2, 38.4), (91.4, 41.4), (92.4, 44.6), (88.0, 42.2), (82.0, 40.0)]), RAVEN.light, 0.8),
           (sm([(80.0, 37.6), (85.0, 37.2), (89.0, 38.8), (86.0, 39.6)]), RAVEN.hi, 0.55)]
    # trois plumes de la joue (des festons doux, inégaux ; jamais une rangée régulière)
    for (x, y, s) in ((72.0, 56.4, 1.2), (79.4, 59.4, 1.0), (74.2, 62.0, 0.9)):
        hd += [(ribbon([(x - 2.8 * s, y - 1.0), (x - 0.4, y + 0.8), (x + 2.6 * s, y - 0.4)], [0.1, 0.9, 0.1]), RAVEN.shadow, 0.45),
               (ribbon([(x - 2.0 * s, y - 1.6), (x, y - 0.4), (x + 2.2 * s, y - 1.1)], [0.1, 0.55, 0.1]), RAVEN.light, 0.35)]
    # la joue sous l'œil, un peu plus claire (le volume du crâne), et le coin charnu du bec
    hd += [(sm([(74.0, 50.8), (80.6, 50.6), (84.0, 53.0), (82.6, 56.4), (77.0, 56.4), (73.4, 54.0)]), RAVEN.light, 0.28),
           (ellipse(84.0, 57.4, 1.6, 1.0, 20), BEAK.shadow, 0.8)]
    # l'arête du front entre les yeux (claire), qui descend vers le bec et cache le bord de l'œil lointain
    hd += [(sm([(82.4, 41.6), (85.0, 41.0), (86.0, 44.6), (85.4, 49.0), (84.2, 51.0), (83.0, 47.6)]), RAVEN.light, 0.7)]
    # les orbites (creux sombres autour des yeux)
    hd += [(ellipse(77.8, 47.2, 3.4, 3.2), RAVEN.deep, 0.65),
           (ellipse(88.4, 45.6, 2.3, 2.8, 8), RAVEN.deep, 0.6)]
    # les yeux d'ambre ronds, petite pupille vers l'ennemi, un éclat ; le lointain plus étroit, sur la même ligne
    for (cx, cy), (rx, ry), pr, (px, py) in (((77.8, 47.2), (2.45, 2.35), 0.92, (78.6, 47.1)),
                                             ((88.5, 45.6), (1.5, 2.0), 0.7, (89.0, 45.6))):
        if P['blink'] > 0.5:
            hd += [(ellipse(cx, cy, rx, ry), RAVEN.base, 1),
                   (ribbon([(cx - rx, cy + 0.2), (cx, cy + 0.9), (cx + rx, cy + 0.1)], [0.1, 0.6, 0.1]), RAVEN.deep, 0.9),
                   (ribbon([(cx - rx * 0.8, cy - 0.6), (cx, cy - 0.2), (cx + rx * 0.8, cy - 0.7)], [0.1, 0.45, 0.1]), RAVEN.light, 0.6)]
        else:
            hd += [(ellipse(cx, cy, rx, ry), ('rad', cx + 0.6 * rx, cy - 0.6 * ry, rx * 2.0, rx * 2.0, [(0, EYE[0]), (0.35, '#ffd25a'), (0.7, EYE[1]), (1, EYE[2])]), 1),
                   (ellipse(px, py, pr, pr * 1.05), EYE[3], 1),
                   (ellipse(px + 0.45 * pr, py - 0.5 * pr, 0.42 * pr, 0.38 * pr), '#ffffff', 1),
                   (ribbon([(cx - rx * 0.9, cy + ry * 0.55), (cx, cy + ry * 0.95), (cx + rx * 0.9, cy + ry * 0.5)], [0.1, 0.45, 0.1]), EYE[2], 0.5)]
    fig.part('head', head, RAVEN, grad=(90, 38, 64, 62, [(0, RAVEN.light), (0.35, RAVEN.base), (1, RAVEN.shadow)]),
             cel=1.3, rim=0.7, cast=1.3, cast_on=['ruff', 'torso'] + pom_names + nw_names + fw_names, details=hd)
    # les sourcils de plumes froncés (en V : le bout vers le bec plus bas, il écrase le coin de l'œil)
    browN = sm([(72.4, 43.4), (73.6, 41.4), (75.6, 42.4), (77.4, 41.0), (79.0, 42.6), (81.2, 43.4), (83.2, 45.6),
                (82.6, 46.8), (80.4, 45.8), (77.6, 45.2), (74.6, 45.2)], sharp=(1, 3, 6))
    browF = sm([(85.2, 44.8), (86.4, 43.0), (88.8, 42.0), (91.0, 40.8), (92.4, 41.4), (93.4, 41.0), (92.6, 42.8),
                (90.6, 43.8), (88.0, 44.6), (86.2, 45.6)], sharp=(0, 3, 5))
    for nm, sh, gx in (('browN', browN, 78), ('browF', browF, 89)):
        fig.part(nm, sh, RAVEN, grad=(gx + 4, 41, gx - 4, 46, [(0, RAVEN.hi), (0.5, RAVEN.light), (1, RAVEN.base)]),
                 cel=0.6, rim=0.5, cast=1.0, cast_on=['head'],
                 details=[(ribbon([(gx - 4, 43.8), (gx, 43.6), (gx + 4, 44.8)], [0.1, 0.5, 0.1]), RAVEN.glint, 0.5)])
    # le tokin : petit bonnet noir laqué à facettes, posé sur le front
    tokin = sm([(79.6, 37.6), (80.2, 35.0), (81.8, 32.8), (83.6, 31.6), (85.4, 33.0), (86.6, 35.4), (86.8, 37.8), (83.2, 38.6)],
               sharp=(0, 3, 6))
    fig.part('tokin', tokin, LACQ, grad=(87, 30, 78, 38, [(0, LACQ.light), (0.5, LACQ.base), (1, LACQ.shadow)]),
             cel=0.8, rim=0.7, cast=1.2, cast_on=['head'],
             details=[(sm([(83.6, 31.9), (85.4, 33.2), (86.6, 35.6), (86.6, 37.4), (84.8, 37.8), (84.4, 34.6)], sharp=(0, 4)), LACQ.light, 0.7),
                      (ribbon([(84.2, 32.6), (85.4, 35.0), (85.8, 37.2)], [0.1, 0.6, 0.2]), LACQ.glint, 0.75),
                      (sm([(79.6, 36.6), (83.2, 37.4), (86.8, 36.8), (86.8, 37.8), (83.2, 38.6), (79.6, 37.6)]), LACQ.deep, 0.8),
                      (ellipse(85.0, 33.8, 0.5, 0.3, -55), '#ffffff', 0.8)])
    # ---- le bec entrouvert : la gorge rouge sombre au fond, la mandibule, puis le bec crochu par-dessus ----
    op = P['open']
    gorge = sm([(85.0, 56.6), (92.0, 57.2), (99.0, 57.8), (103.4, 59.2), (99.6, 59.8 + 0.8 * op), (92.0, 59.8 + 1.2 * op),
                (86.0, 59.4 + 0.8 * op)], sharp=(3,))
    fig.part('gorge', gorge, Mat(GORGE[2], GORGE[2], GORGE[1], GORGE[0], GORGE[0]), grad=None, cel=0, rim=0, cast=0,
             details=[(gorge, ('lin', 92, 57, 92, 61, [(0, GORGE[0]), (0.5, GORGE[1]), (1, GORGE[2])]), 1),
                      (ribbon([(88.0, 59.6 + 0.6 * op), (95.0, 60.0 + 0.9 * op), (101.0, 60.0 + 0.6 * op)], [0.1, 0.6, 0.1]), '#c84038', 0.6)])
    MAND = mR(4.0 * op, 86.0, 59.0)
    mand = sm([(84.6, 58.8), (90.0, 59.4), (96.0, 59.8), (101.0, 60.0), (104.4, 60.4), (101.2, 61.8), (96.0, 62.6),
               (90.4, 62.8), (86.4, 62.0), (84.4, 60.6)], sharp=(4,))
    fig.part('mand', mand, BEAK, grad=(102, 60, 86, 64, [(0, BEAK.light), (0.5, BEAK.base), (1, BEAK.shadow)]),
             cel=0.7, rim=0.45, cast=0.9, cast_on=['head', 'gorge', 'torso'] + pom_names,
             details=[(ribbon([(87.0, 60.6), (94.0, 61.0), (101.6, 60.8)], [0.1, 0.6, 0.1]), BEAK.light, 0.5)])
    beak = sm([(83.4, 50.4), (87.0, 48.4), (91.6, 47.0), (97.2, 48.4), (102.2, 51.6), (106.0, 55.4), (108.2, 59.4),
               (108.0, 62.6), (106.4, 61.2), (103.6, 59.2), (98.6, 58.0), (92.6, 57.6), (87.2, 57.8), (84.0, 56.6),
               (83.0, 53.4)], sharp=(7,))
    bk = [(sm([(85.0, 54.2), (92.0, 54.6), (98.4, 55.6), (104.0, 57.6), (107.2, 60.4), (108.0, 62.8), (106.4, 61.4),
               (103.6, 59.4), (98.6, 58.2), (92.6, 57.6), (87.2, 57.8), (84.0, 56.6)]), BEAK.shadow, 0.6),
          # l'arête éclairée (le dessus du bec), le reflet ; la narine sous les plumes de la base
          (ribbon([(87.0, 49.0), (92.0, 48.2), (97.6, 49.6), (103.0, 53.0), (106.8, 57.8)], [0.2, 1.3, 1.2, 0.9, 0.2]), BEAK.light, 0.9),
          (ribbon([(90.0, 48.4), (95.0, 49.0), (100.6, 51.6)], [0.1, 0.6, 0.1]), BEAK.glint, 0.75),
          (ellipse(91.2, 51.6, 1.1, 0.5, 6), BEAK.deep, 0.7),
          # les petites plumes de la base qui couvrent le haut du bec (comme les vibrisses du corbeau)
          (sm([(83.4, 50.4), (86.4, 48.8), (89.4, 48.6), (92.2, 50.0), (88.8, 51.2), (85.6, 52.6), (83.2, 52.8)], sharp=(3,)), RAVEN.base, 1),
          (ribbon([(84.2, 50.0), (87.0, 49.4), (90.0, 49.4)], [0.1, 0.5, 0.1]), RAVEN.light, 0.7)]
    fig.part('beak', beak, BEAK, grad=(104, 50, 86, 58, [(0, BEAK.light), (0.45, BEAK.base), (1, BEAK.shadow)]),
             cel=0.8, rim=0.6, cast=1.2, cast_on=['head', 'mand', 'gorge', 'torso'] + pom_names, details=bk)

    # ================================================================ le bras proche : la grande manche, la serre, le kodachi
    sang = P['sang']
    FH = P['fh']
    u_s = unit(sang)
    G = add(FH, u_s, -GRIP_S)                          # la garde
    Wr = add(FH, rot((-4.2, -1.6), sang))               # le poignet (derrière la serre, côté du coude)
    S = S_N
    E = ik(S, Wr, L1, L2, 1)                            # le coude plie vers l'arrière
    # la toile qui pend sous le bras (gravité), jusqu'à l'ourlet : derrière le bras
    sway = P['sw']
    low = max(E[1], Wr[1])
    hem_y = low + 12.0
    xl = min(E[0], S[0]) - 4.6
    xr = Wr[0] + 1.0
    drape = sm([(S[0] - 3.8, S[1] - 1.6), (xl + 0.6, (S[1] + E[1]) / 2), (xl - 0.2 + sway * 0.4, E[1] + 4.0),
                (xl + 1.6 + sway * 0.8, hem_y - 1.6), (xl + (xr - xl) * 0.45 + sway, hem_y + 0.6),
                (xr - 0.6 + sway * 0.6, hem_y - 1.8), (xr + 0.6, Wr[1] + 2.6), (Wr[0] - 1.0, Wr[1] - 1.0)])
    dd = [(ribbon([(xl + 3.0, E[1] + 1.0), (xl + 3.4 + sway * 0.5, (E[1] + hem_y) / 2), (xl + 4.6 + sway * 0.8, hem_y - 0.4)],
                  [0.2, 1.8, 0.3]), CLOTH.shadow, 0.6),
          (ribbon([(xr - 3.0, Wr[1] + 3.0), (xr - 3.2 + sway * 0.6, (Wr[1] + hem_y) / 2 + 1), (xr - 2.6 + sway * 0.7, hem_y - 1.2)],
                  [0.2, 1.4, 0.3]), CLOTH.shadow, 0.45),
          (ribbon([(xl + 5.4, E[1] + 2.0), (xl + 6.0 + sway * 0.5, (E[1] + hem_y) / 2), (xl + 7.0 + sway * 0.8, hem_y)],
                  [0.1, 1.0, 0.1]), CLOTH.hi, 0.6)]
    fig.part('drape', drape, CLOTH, grad=(xr, S[1], xl, hem_y, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.4, rim=0.7, cast=1.2, cast_on=['torso', 'nhaka', 'fhaka', 'knot', 'pan1', 'pan2'] + tail_names + pom_names,
             details=dd, occl=(CLOTH.shadow, 0.25, 2.6))
    # le bras dans sa manche : épaule, coude et avant-bras d'une seule forme ; l'ouverture de la manche au poignet
    arm = bent(S, E, Wr, 9.2, 8.6, 8.0, bulge=(0.06, 0.04))
    uf = norm(sub_(Wr, E))
    adet = [(ellipse(*add(Wr, uf, -0.4), 1.6, 3.4, math.degrees(math.atan2(uf[1], uf[0]))), CLOTH.deep, 0.9),
            (ribbon([lerp(S, E, 0.2), lerp(S, E, 0.85), lerp(E, Wr, 0.5)], [0.1, 1.1, 0.1]), CLOTH.shadow, 0.35)]
    fig.part('arm', arm, CLOTH, grad=(S[0] + 6, S[1] - 2, E[0] - 4, E[1] + 4, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.2, rim=0.7, cast=1.0, cast_on=['torso', 'drape', 'knot', 'pan1', 'pan2', 'nhaka'] + pom_names, details=adet)
    # le poignet écailleux qui sort de la manche (la serre est au bout)
    wrist = limb([add(Wr, uf, -1.4), lerp(Wr, FH, 0.6)], [4.6, 4.2])
    fig.part('wrist', wrist, BEAK, cel=0.6, rim=0.4, cast=0.6, cast_on=['arm'])

    # ---- le kodachi : lame d'acier (dos clair en haut, fil plus sombre), habaki et tsuba d'or vus de biais,
    # poignée noire tressée, pommeau d'or ----
    def S_(sh):
        return xf(sh, G[0], G[1], sang)
    blade = S_(sm([(0.6, -1.3), (20.0, -1.35), (27.0, -1.0), (BLADE_L + 0.4, 0.3), (27.8, 1.3), (12.0, 1.4), (0.6, 1.3)],
                  sharp=(0, 3, 6), t=0.5))
    fig.part('blade', blade, STEEL, grad=None, cel=0.4, rim=0.3, cast=0.9,
             details=[(blade, ('lin', *add(G, rot((0, 1.4), sang)), *add(G, rot((0, -1.4), sang)), [(0, STEEL.shadow), (0.45, STEEL.base), (0.55, STEEL.light), (1, STEEL.hi)]), 1),
                      (S_(ribbon([(2.0, -0.6), (14.0, -0.75), (26.0, -0.5)], [0.1, 0.5, 0.1])), '#ffffff', 0.95),
                      (S_(ribbon([(2.0, 0.9), (15.0, 1.0), (26.6, 0.8)], [0.1, 0.6, 0.1])), STEEL.deep, 0.5)])
    hab = S_(rpoly([(-0.4, -1.8), (2.2, -1.8), (2.2, 1.8), (-0.4, 1.8)], 0.5))
    fig.part('habaki', hab, GOLD, cel=0.4, rim=0.4, cast=0.5)
    grip = S_(rpoly([(-1.0, -1.45), (-9.6, -1.3), (-9.6, 1.3), (-1.0, 1.45)], 0.5))
    gdet = []
    for k in range(4):
        s0 = -2.0 - k * 2.0
        gdet.append((S_(sm([(s0, -1.4), (s0 - 1.1, 0.0), (s0, 1.4), (s0 - 0.6, 0.0)], sharp=(0, 2), t=0.6)), LACQ.light, 0.75))
    fig.part('grip', grip, LACQ, cel=0.5, rim=0.4, cast=0.6, details=gdet)
    pom = S_(rpoly([(-9.2, -1.8), (-11.6, -1.6), (-11.6, 1.6), (-9.2, 1.8)], 0.9))
    fig.part('pommel', pom, GOLD, cel=0.5, rim=0.4, cast=0.5,
             details=[(S_(ellipse(-10.2, -0.8, 0.8, 0.4)), GOLD.hi, 0.7)])
    tsuba = S_(ellipse(0.0, -0.4, 1.0, 3.0))
    fig.part('tsuba', tsuba, GOLD, cel=0.5, rim=0.5, cast=0.7,
             details=[(S_(ellipse(0.2, -1.0, 0.42, 1.6)), GOLD.hi, 0.7)])

    # ---- la serre, serrée sur la poignée : le dos de la main (écailles), trois doigts repliés, les griffes claires ----
    def F_(sh):
        return xf(sh, FH[0], FH[1], sang)
    fist = F_(sm([(3.6, -2.8), (1.0, -4.0), (-2.6, -4.0), (-4.6, -2.0), (-4.6, 1.6), (-3.2, 3.6), (0.4, 4.0), (3.6, 3.2),
                  (4.6, 0.4)]))
    fdet = [(F_(sm([(3.4, -2.6), (1.0, -3.6), (-2.4, -3.6), (-4.0, -1.8), (-1.0, -0.8), (2.6, -0.6)])), BEAK.light, 0.55)]
    # les doigts (trois phalanges repliées en travers de la poignée) : un creux entre deux, une écaille éclairée
    for s0, s1 in ((3.8, 1.4), (1.4, -1.0), (-1.0, -3.4)):
        fdet += [(F_(ribbon([(s1, 0.2), (s1 - 0.05, 1.9), (s1 + 0.15, 3.6)], [0.1, 0.55, 0.1])), BEAK.deep, 0.7),
                 (F_(ellipse((s0 + s1) / 2, 1.2, abs(s1 - s0) * 0.3, 0.45)), BEAK.hi, 0.5),
                 (F_(ellipse((s0 + s1) / 2 + 0.2, 2.6, abs(s1 - s0) * 0.26, 0.35)), BEAK.light, 0.35)]
    fig.part('fist', fist, BEAK, grad=None, cel=1.0, rim=0.6, cast=1.0, details=fdet,
             cast_on=['grip', 'tsuba', 'habaki', 'blade', 'torso', 'drape', 'arm', 'knot', 'pan1', 'pan2', 'fhaka', 'nhaka'])
    claw_names = []
    for k, s in enumerate((2.6, 0.2, -2.2)):
        cw = F_(sm([(s + 0.9, 3.2), (s - 0.9, 3.4), (s - 1.6, 4.8), (s - 1.0, 6.0), (s - 0.6, 4.8)], sharp=(3,), t=0.7))
        nm = 'claw%d' % k
        claw_names.append(nm)
        fig.part(nm, cw, CLAW, cel=0.35, rim=0.3, cast=0.5, cast_on=['fist', 'grip', 'blade', 'torso', 'drape', 'fhaka', 'knot'])
    # le pouce (le doigt de derrière de l'oiseau) par-dessus la poignée, sa griffe
    thumb = F_(limb([(-3.2, -3.0), (-0.4, -3.8), (2.4, -3.2)], [2.8, 2.6, 2.2]))
    fig.part('thumb', thumb, BEAK, cel=0.6, rim=0.5, cast=0.7, cast_on=['fist', 'grip', 'tsuba', 'habaki'])
    tcl = F_(sm([(2.0, -4.2), (3.8, -3.6), (5.0, -2.4), (3.4, -2.4), (2.2, -2.6)], sharp=(2,), t=0.7))
    fig.part('tclaw', tcl, CLAW, cel=0.3, rim=0.3, cast=0.4, cast_on=['thumb', 'grip', 'tsuba', 'blade'])

    # ---- chaque groupe de morceaux prend sa pose ----
    head_names = ['ruff', 'head', 'browN', 'browF', 'tokin', 'gorge', 'mand', 'beak']
    arm_names = ['drape', 'arm', 'wrist', 'blade', 'habaki', 'grip', 'pommel', 'tsuba', 'fist', 'thumb', 'tclaw'] + claw_names
    fig.pose(fw_names + nw_names, UC)
    fig.pose(tail_names, TAIL)
    fig.pose(['fshin', 'nshin', 'fboard', 'nboard', 'ftooth', 'ntooth', 'fhaka', 'nhaka'], LEG)
    fig.pose(['torso'] + pom_names, TOR)
    fig.pose(['knot'], U)
    fig.pose(['pan1', 'pan2'], CLO)
    fig.pose(arm_names, U)
    fig.pose(head_names, HEAD)
    fig.pose(['mand'], mchain(HEAD, MAND))
    # ce que les effets doivent savoir (repère du dessin)
    tipb = mapp(U, add(G, u_s, BLADE_L))
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, ROOT=ROOTM, G=mapp(U, G), fist=mapp(U, FH), tip=tipb,
                   ang=sang + P['lean'] * 1.1, head=mapp(HEAD, (80, 48)), beak=mapp(HEAD, (106, 60)),
                   eye=mapp(HEAD, (77.8, 47.2)), chest=mapp(TOR, (78, 72)), feet=(mapp(ROOTM, FEET)),
                   wn=(mapp(UC, nW), mapp(UC, nT)), wf=(mapp(UC, fW), mapp(UC, fT)), feet_y=GRD - P['lift'])
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def bounds(fig):
    """La boîte de tout le dessin (pixels du dessin), contour compris."""
    xs, ys = [], []
    for p in fig.parts:
        for q in p.shape.pts():
            x, y = mapp(p.M, q)
            xs.append(x)
            ys.append(y)
    o = fig.ow
    return min(xs) - o, min(ys) - o, max(xs) + o, max(ys) + o


def main():
    """karu.svg (grand) et karu-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-orin-rapide.webp (512 px de haut) et mon-orin-rapide-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('karu', 0.95, 512, ID_JEU), ('karu-petit', 1.35, 160, ID_JEU + '-160')):
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


if __name__ == '__main__':
    if '--apercu' in sys.argv:
        out = sys.argv[sys.argv.index('--apercu') + 1]
        h = sys.argv[sys.argv.index('--apercu') + 2] if len(sys.argv) > sys.argv.index('--apercu') + 2 else '900'
        p = out.replace('.png', '.svg')
        fg = build()
        print('boîte du dessin :', [round(v, 1) for v in bounds(fg)])
        open(p, 'w').write(fg.svg())
        subprocess.run(['node', os.path.join(HERE, '..', 'rendu.cjs'), p, out, h, '#e9e6f2'], check=True)
    else:
        main()
