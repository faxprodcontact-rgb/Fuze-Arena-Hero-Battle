# Tessa (mages-4, vent, épique, tireuse) redessinée en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte de tous les héros, 26/11/2026, sur le modèle de Kael validé : ../kael/kael.py, outil commun ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/tessa/tessa.py        # → tessa.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/tessa.txt) : la femme-aigle archère, fière, froide et
# précise. Vraie tête de pygargue (blanche, de 3/4 : deux yeux d'ambre sur la même ligne, arcades lourdes en « V » qui
# coupent le haut de l'iris ; le bec jaune citron crochu part du MILIEU du visage, entre les yeux — demande du
# propriétaire du 26/11 —, traits placés par ../visage.py : FACE_BOX, FACE_V) ; un VRAI COU de plumes (demande du propriétaire sur le pixel art) : les plumes blanches de la tête
# s'allongent en descendant, leurs pointes tournent au tiède et s'emboîtent dans un col de plumes brunes posé sur la
# cuirasse ; elles s'évasent sur les deux épaulières. Grandes ailes brunes levées et repliées en manteau (l'aile proche
# en éventail à gauche, l'aile lointaine plus sombre derrière la tête). Épaulières en dôme d'or bordées de plumes d'or,
# cuirasse d'or galbée (deux coques) sur un ventre de plumes brunes, ceinture de cuir à boucle d'or au jade, tablier de
# jade (pli, ourlet d'or, pendentif en losange), tassettes en grandes plumes d'or, culottes de plumes en deux étages,
# tarses jaunes écailleux et serres (trois doigts devant, un derrière, griffes d'ardoise). Tir à hauteur de poitrine :
# le bras lointain tient l'arc récurve de jade, la main proche a tiré la corde jusque devant le sternum.
# Coordonnées = pixels de la grille de tessa.txt (même échelle, mêmes pieds : y = 116 est le sol), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import INK, Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, resample, bez, mchain, mT, mR, mS, mapp  # noqa: E402
from outils import bent, taper, crpath, ik, under, plume, feston, lerp, add, unit, norm  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402,F401

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
ARM = Mat('#f6c890', '#c4884e', '#9a5e36', '#68382a', '#42202a')            # les bras : brun plus chaud que les ailes
WHITE = Mat('#ffffff', '#fbf9ff', '#e4e1f0', '#aaa5c8', '#6a6490')
WARM = Mat('#fff4ee', '#ece0de', '#d2bec0', '#a2868e', '#6e5468')          # pointes tièdes des plumes du cou
BROWN = Mat('#f0c07c', '#b97c44', '#8c5230', '#5e3226', '#3a1c22')
BROWNF = Mat('#c08a5a', '#7e4c30', '#5c3226', '#3e2020', '#28141c')        # l'aile lointaine, plus sombre
GOLD = Mat('#fff3b8', '#f6c24a', '#d48826', '#9c4e1a', '#5a2418')
BEAK = Mat('#fffbd2', '#ffe45a', '#f6c42e', '#dc8a2a', '#9c4c1c')          # bec, mains et serres : jaune citron
CLAW = Mat('#d2cee6', '#8e88a6', '#5e566e', '#3a3248', '#221a30')
JADE = Mat('#c2f6e0', '#5ccaab', '#2a8682', '#1a5260', '#102a3a')
BELT = Mat('#b88a64', '#7a5038', '#56362a', '#3a2222', '#24141a')           # cuir brun (ceinture, poignée)
LEATHER = Mat('#e09a70', '#a8523a', '#7a3428', '#4e1c22', '#300e18')         # cuir rouge sombre (brassards)
STEEL = Mat('#f6f8ff', '#cfd3e6', '#8e88a6', '#5c5674', '#34304a')
SHAFT = Mat('#fff0c4', '#ecc282', '#c8924e', '#8a5630', '#5a3020')
EYE = ('#ffe9a0', '#f5a623', '#a8501a', '#1a0c12')
STRING = '#fdf6e6'

GRD = 116.6        # le dessous des serres
FEET = (64, 116)   # le point « sol » du pixel art (l'image se pose par ce point)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-4, -4, 132, 123)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath 0..1 : le buste se soulève ; crouch : elle se tasse ; lean : penchée en avant (+) ; head : décalage de la
#   tête (elle bouge par à-coups, comme un oiseau) ; tilt : la tête tourne (− = vers le ciel) ; blink ; fix : regard
#   fixé (le reflet de l'œil s'éteint) ; ruff : les plumes du cou se hérissent (0..3) ; ph : phase des mouvements
#   secondaires ; wn / wf : les ailes (lift : le bout des plumes monte ; spread : elles se hérissent, en éventail) ;
#   hand : le poing proche (sur la corde) ; open : la main s'ouvre (0..1) ; arrow : la flèche encochée (1) ou partie
#   (0) ; free : la corde est libre (droite, elle vibre de `bulge`) ; relax : l'arc se détend (+) ou se bande (−) ;
#   bow_dx : l'arc saute en avant ; bow_tilt : il penche (degrés).
S_N = (47.6, 57.6)          # l'épaule proche
S_F = (80.5, 59.0)          # l'épaule lointaine
GRIP = (108.6, 68.6)        # le milieu de la poignée de l'arc (dans le poing lointain)
HAND0 = (57.2, 68.6)        # le poing proche, sur la corde (l'encoche de la flèche)
NECK = (68.0, 50.0)         # le pivot de la tête (agrandie ×1,1 autour de ce point)
# la face (sans la nuque) : visage.py y place les yeux, la racine du bec (le « nez ») et la fermeture du bec
FACE_BOX = (54.0, 18.0, 84.0, 45.0)
FACE_V = placer(FACE_BOX, l_oeil=0.24)
fig_face = {}
L1N, L2N = 17.6, 13.4       # bras, avant-bras (proche)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0, fix=0.0, ruff=0.0, ph=0.0,
            wn_lift=0.0, wn_spread=0.0, wf_lift=0.0, wf_spread=0.0, hand=HAND0, open=0.0, arrow=1.0, free=0.0,
            bulge=0.0, relax=0.0, bow_dx=0.0, bow_tilt=0.0, wave=0.0)


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def rot_about(p, c, deg):
    r = rot((p[0] - c[0], p[1] - c[1]), deg)
    return (c[0] + r[0], c[1] + r[1])


def g2(c1, c2):
    return [(0, c1), (1, c2)]


# ================================================================ les ailes d'aigle

def eagle_wing(fig, key, R, W, feathers, mat, P, lift, spread, ph, cov=1.0, edge=None):
    """Une aile d'aigle repliée en manteau : les rémiges (du bout de l'aile vers le corps ; chacune pose une ombre douce
    sur la précédente, aucune ligne), deux rangées de couvertures (des plumes plus courtes, plus claires, au bout
    arrondi, qui recouvrent les racines), puis le bord d'attaque (petites couvertures claires, sans trait).
    feathers = [(u, tip, w)] : la racine à u le long du bras W → R, le bout de la plume, sa largeur.
    lift (degrés) : toute l'aile tourne autour de la racine ; spread : les plumes s'écartent en éventail (hérissées).
    edge = [(point, profondeur)] : le bord d'attaque suit cette courbe lisse (au repos) au lieu du bras ; elle passe
    au-dehors de toutes les racines de plumes, pour un bord net d'un seul trait (aile lointaine, avis du 26/11 soir)."""
    names = []
    Wp = rot_about(W, R, lift)
    n = len(feathers)
    dirs_at = []
    for i, (u, tip, w) in enumerate(feathers):
        root = lerp(Wp, R, u)
        tip = rot_about(tip, R, lift)
        # l'éventail s'ouvre autour de la racine : les plumes du bout tournent plus ; elles ondulent un peu
        tip = rot_about(tip, root, spread * (1.0 - i / max(1, n - 1)) + 0.9 * math.sin(ph - 0.6 * i) * (0.6 + 0.4 * abs(spread) / 10))
        d = norm((tip[0] - root[0], tip[1] - root[1]))
        dirs_at.append((u, d))
        side = (-d[1], d[0])
        L = math.dist(root, tip)
        bend = 1.2 + 0.4 * math.sin(ph * 0.7 - 0.5 * i)
        p1 = add(add(root, d, L * 0.33), side, bend * 0.3)
        p2 = add(add(root, d, L * 0.7), side, bend)
        sh = plume(root, p1, p2, tip, w)
        nm = '%s_r%d' % (key, i)
        names.append(nm)
        fig.part(nm, sh, mat, grad=(root[0] + 3, root[1] - 3, tip[0], tip[1], [(0, mat.light), (0.5, mat.base), (1, mat.shadow)]),
                 cel=0.9, rim=0.4, cast=1.3)

    def dir_at(u):
        for j in range(len(dirs_at) - 1):
            u0, d0 = dirs_at[j]
            u1, d1 = dirs_at[j + 1]
            if u0 <= u <= u1:
                return norm(lerp(d0, d1, (u - u0) / ((u1 - u0) or 1)))
        return dirs_at[0][1] if u < dirs_at[0][0] else dirs_at[-1][1]
    # le bras de l'aile, un peu bombé vers la lumière (en haut à droite)
    dv = norm((Wp[0] - R[0], Wp[1] - R[1]))
    nv = (-dv[1], dv[0])
    if nv[0] < 0:
        nv = (-nv[0], -nv[1])
    arm = lambda t: add(lerp(R, Wp, t), nv, 2.2 * math.sin(math.pi * t))
    # les couvertures : deux rangées de plumes au bout arrondi (longueurs et écarts un peu inégaux), du bout vers le
    # corps ; les grandes couvrent les racines des rémiges, les moyennes le haut des grandes
    rows = ((key + '_g', 7, 0.04, 0.92, 15.0 * cov, 9.4 * cov, mat.base, (1.0, 0.9, 1.06, 0.95, 1.05, 0.9, 1.0), 4.4 * cov),
            (key + '_m', 8, 0.0, 0.95, 9.6 * cov, 7.4 * cov, mat.light, (0.95, 1.06, 0.9, 1.0, 1.08, 0.94, 1.0, 0.92), 1.6 * cov))
    for rk, cnt, ua, ub, Lc, wc, col, jit, off in rows:
        for j in range(cnt - 1, -1, -1):
            u = ua + (ub - ua) * j / (cnt - 1)
            d = dir_at(u)
            root = add(arm(1 - u), d, off)
            L = Lc * jit[j] * (0.7 + 0.3 * math.sin(math.pi * min(1, u * 1.2 + 0.15)))
            tip = add(root, d, L)
            side = (-d[1], d[0])
            sh = plume(root, add(root, d, L * 0.35), add(add(root, d, L * 0.72), side, 0.5), tip, wc * (0.8 + 0.2 * jit[j]), n=10, tip=0.6)
            nm = '%s%d' % (rk, j)
            names.append(nm)
            fig.part(nm, sh, mat, grad=(root[0] + 2, root[1] - 2, tip[0], tip[1], [(0, lite_(col)), (0.55, col), (1, mat.shadow)]),
                     cel=0.7, rim=0.4, cast=1.0)
    # le bord d'attaque : une bande de petites couvertures claires, large au poignet, fine à l'épaule ; le haut suit le
    # bras bombé, le bas fait de petits festons (aucun trait)
    if edge:
        # le bord net : la courbe donnée (tournée avec l'aile), les festons vers l'intérieur de l'aile
        line = crpath([rot_about(p, R, lift) for p, _ in edge], n=14)
        m = len(line) - 1
        ne = len(edge) - 1
        dk = []
        for k in range(m + 1):
            v = k / m * ne
            k0 = min(ne - 1, int(v))
            dk.append(edge[k0][1] + (edge[k0 + 1][1] - edge[k0][1]) * (v - k0))
        dirs = []
        for k in range(m + 1):
            a, b = line[max(0, k - 1)], line[min(m, k + 1)]
            t_ = norm((b[0] - a[0], b[1] - a[1]))
            dirs.append((-t_[1], t_[0]))   # la normale tournée vers la gauche (vers l'aile)
        deps = [d * cov for d in dk]
        lead = feston(line, dirs, deps, 6, (1.0, 0.9, 1.1, 0.95))
    else:
        line = [arm(t) for t in [k / 12 for k in range(13)]]
        dirs = [dir_at(1 - k / 12) for k in range(13)]
        deps = [(2.6 + 3.8 * math.sin(math.pi * min(1, 0.15 + 0.85 * k / 12))) * cov for k in range(13)]
        lead = feston(line, dirs, deps, 6, (1.0, 0.9, 1.1, 0.95))
    nm = key + '_lead'
    names.append(nm)
    fig.part(nm, lead, mat, grad=(Wp[0] + 3, Wp[1] - 2, R[0] - 4, R[1] + 4, [(0, mat.hi), (0.4, mat.light), (1, mat.base)]),
             cel=0.9, rim=0.7, cast=1.1)
    return names, Wp


def lite_(c):
    from lib import lite
    return lite(c, 0.18)


# les plumes de l'aile proche (au repos) : (racine le long du bras W → R, bout, largeur), du bout de l'aile vers le corps
R_N = (45.0, 53.0)          # l'attache de l'aile proche (derrière l'épaule)
W_N = (23.0, 9.0)           # le « poignet » de l'aile (en haut)
NEAR_FEATHERS = [
    (0.00, (5.4, 7.4), 9.6),
    (0.06, (1.6, 16.6), 10.6),
    (0.14, (0.6, 27.4), 11.4),
    (0.24, (2.4, 38.6), 12.0),
    (0.36, (6.4, 49.6), 12.4),
    (0.50, (11.8, 60.2), 12.4),
    (0.64, (18.8, 69.6), 12.0),
    (0.78, (26.4, 76.4), 11.0),
    (0.90, (33.6, 79.0), 9.6),
]
R_F = (63.0, 50.0)          # l'aile lointaine : derrière la tête, plus sombre
W_F = (49.0, 15.0)
FAR_FEATHERS = [
    (0.00, (40.6, 3.2), 8.2),
    (0.10, (34.6, 8.6), 9.0),
    (0.24, (30.8, 17.6), 9.6),
    (0.40, (30.4, 28.6), 9.8),
    (0.58, (33.0, 40.4), 9.6),
    (0.76, (38.0, 50.0), 9.0),
]
# le bord d'attaque de l'aile lointaine (avis du 26/11 soir : plus de marches ni de copeaux contre la tête) : une
# courbe lisse qui longe le bord de la première rémige, passe au-dehors des racines des couvertures et plonge
# franchement derrière le crâne ; (point, profondeur des festons)
FAR_EDGE = [((46.6, 7.8), 1.2), ((49.4, 11.4), 3.0), ((51.2, 15.6), 4.2), ((52.6, 20.4), 4.6), ((54.2, 25.6), 4.4),
            ((56.4, 32.0), 4.0), ((59.0, 39.0), 3.6), ((61.6, 46.0), 3.0)]


# ================================================================ le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    ph = P['ph']

    # ---- le squelette : une matrice par groupe de morceaux ----
    dyb = P['crouch'] * 0.85
    U = mchain(mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 0.8, 66, 88))          # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                            # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 66, 76))                              # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'] + 2.0, NECK[0], NECK[1] - 4), mS(1.1, 1.1, NECK[0], NECK[1]))
    LEG = mS(1, 1 - dyb / 34, 0, GRD)                                           # les jambes plient (pieds au sol)

    # ================================================================ les ailes (derrière tout)
    fw_names, _ = eagle_wing(fig, 'wf', R_F, W_F, FAR_FEATHERS, BROWNF, P, P['wf_lift'], P['wf_spread'], ph + 1.1, cov=0.8,
                              edge=FAR_EDGE)
    nw_names, _ = eagle_wing(fig, 'wn', R_N, W_N, NEAR_FEATHERS, BROWN, P, P['wn_lift'], P['wn_spread'], ph)

    # ================================================================ le bras lointain (vers l'arc), derrière le buste
    bx = P['bow_dx']
    grip = (GRIP[0] + bx, GRIP[1])
    Wf = (grip[0] - 5.6, grip[1] - 0.6)
    Ef = ik(S_F, Wf, 12.6, 11.4, -1)
    farm = bent(S_F, Ef, Wf, 8.6, 7.6, 6.6, bulge=(0.06, 0.08))
    fa = math.atan2(Wf[1] - Ef[1], Wf[0] - Ef[0])
    Lf = math.dist(Ef, Wf)
    F_ = lambda sh: xf(sh, Ef[0], Ef[1], math.degrees(fa))
    fbz = lambda u0, u1, h0, h1, r=0.6: F_(rpoly([(Lf * u0, -h0), (Lf * u1 + 2, -h1), (Lf * u1 + 2, h1), (Lf * u0, h0)], r))
    fig.part('farm', farm, ARM, cel=1.4, rim=0.6, cast=0,
             details=[(ribbon([lerp(S_F, Ef, 0.2), lerp(S_F, Ef, 0.6), lerp(Ef, Wf, 0.1)], [0.1, 0.9, 0.1]), ARM.light, 0.6),
                      (fbz(0.28, 1.0, 4.4, 3.8, 0.9), LEATHER.base, 1),
                      (F_(rpoly([(Lf * 0.28, -4.4), (Lf + 2, -3.8), (Lf + 2, -1.6), (Lf * 0.28, -1.8)], 0.4)), LEATHER.light, 0.95),
                      (fbz(0.26, 0.36, 4.7, 4.7, 0.4), GOLD.base, 1),
                      (F_(rpoly([(Lf * 0.26, -4.7), (Lf * 0.36 + 2, -4.7), (Lf * 0.36 + 2, -2.4), (Lf * 0.26, -2.4)], 0.3)), GOLD.light, 1),
                      (F_(ellipse(Lf * 0.68, -0.2, 0.95, 0.95)), GOLD.base, 1),
                      (F_(ellipse(Lf * 0.68 + 0.25, -0.5, 0.4, 0.4)), GOLD.hi, 1)])

    # ================================================================ les jambes : culottes de plumes, tarses, serres
    def leg(key, hip, knee, ankle, toes, back_toe, flip=1.0):
        """Une jambe d'aigle : le tarse jaune écailleux (d'un seul tenant avec le pied), trois doigts devant et un
        derrière, griffes d'ardoise posées au sol ; la culotte de plumes en deux étages, posée par-dessus."""
        tars = limb([knee, lerp(knee, ankle, 0.5), ankle], [5.2, 4.6, 4.8])
        scales = []
        for k in range(4):
            t = 0.2 + 0.2 * k
            c = lerp(knee, ankle, t)
            scales.append((ribbon([(c[0] - 1.8, c[1] - 0.2), (c[0] + 0.2, c[1] + 0.6), (c[0] + 2.0, c[1] - 0.1)], [0.1, 0.55, 0.1]), BEAK.shadow, 0.7))
        fig.part(key + '_tars', tars, BEAK, cel=1.1, rim=0.6, cast=0.8, details=scales)
        # le doigt arrière (hallux), sa griffe
        bt0, bt1 = back_toe
        fig.part(key + '_btoe', limb([ankle, lerp(ankle, bt0, 0.5), bt0], [4.0, 3.4, 3.0]), BEAK, cel=0.9, rim=0.5, cast=0.6)
        fig.part(key + '_bclaw', sm([(bt0[0] + 0.6, bt0[1] - 1.5), (bt1[0] - 0.2, bt0[1] - 0.6), (bt1[0], GRD), (bt0[0] - 0.4, bt0[1] + 1.4)], sharp=(2,)),
                 CLAW, cel=0.5, rim=0.4, cast=0.4)
        # les trois doigts devant (le plus lointain d'abord), aux phalanges renflées, griffes crochues au sol
        for j, (tip, w) in enumerate(toes):
            mid = lerp(ankle, tip, 0.55)
            mid = (mid[0], mid[1] - 1.0)
            sh = limb([(ankle[0] - 0.6, ankle[1] + 0.4), mid, tip], [4.4, 3.6, w])
            det = [(ribbon([lerp(ankle, tip, 0.3), lerp(ankle, tip, 0.34)], [0.4, 0.4]), BEAK.shadow, 0.0)]
            for t in (0.45, 0.72):
                c = lerp(ankle, tip, t)
                det.append((ribbon([(c[0] - 0.2, c[1] - 1.5), (c[0] + 0.3, c[1]), (c[0] - 0.1, c[1] + 1.4)], [0.1, 0.5, 0.1]), BEAK.shadow, 0.7))
            fig.part('%s_toe%d' % (key, j), sh, BEAK, cel=0.9, rim=0.55, cast=0.7, details=det)
            cl = sm([(tip[0] - 0.8, tip[1] - 1.5), (tip[0] + 1.4, tip[1] - 1.0), (tip[0] + 2.6, GRD - 0.2), (tip[0] + 2.4, GRD),
                     (tip[0] + 0.6, tip[1] + 1.0), (tip[0] - 0.6, tip[1] + 0.9)], sharp=(3,))
            fig.part('%s_claw%d' % (key, j), cl, CLAW, cel=0.5, rim=0.4, cast=0.4)
        # la culotte de plumes : l'étage du bas (longues plumes en pointe sur le genou), puis celui du haut
        hx_, hy_ = hip
        kx, ky = knee
        low = sm([(hx_ - 7.4, hy_ + 5), (hx_ + 6.6, hy_ + 4), (kx + 6.4, ky - 6), (kx + 5.6, ky - 1.6), (kx + 3.8, ky + 1.4),
                  (kx + 2.2, ky - 1.0), (kx + 0.2, ky + 3.0), (kx - 1.6, ky - 0.4), (kx - 3.8, ky + 1.8), (kx - 4.6, ky - 2.4),
                  (kx - 6.8, ky - 0.6), (kx - 7.0, ky - 6)], sharp=(4, 5, 6, 7, 8, 9, 10))
        fig.part(key + '_low', low, BROWN, cel=1.5, rim=0.6, cast=1.2,
                 details=[(ribbon([(kx - 2.0, ky - 9), (kx - 1.4, ky - 4), (kx - 1.6, ky + 0.6)], [0.1, 0.8, 0.1]), BROWN.shadow, 0.7),
                          (ribbon([(kx + 2.0, ky - 8), (kx + 2.4, ky - 4), (kx + 2.2, ky)], [0.1, 0.7, 0.1]), BROWN.light, 0.7)])
        mid_y = (hy_ + ky) / 2
        up = sm([(hx_ - 7.8, hy_ - 2), (hx_ + 7.0, hy_ - 2.4), (hx_ + 7.6, mid_y + 1), (hx_ + 5.4, mid_y + 4.2), (hx_ + 3.4, mid_y + 1.6),
                 (hx_ + 1.0, mid_y + 5.0), (hx_ - 1.4, mid_y + 2.0), (hx_ - 3.8, mid_y + 4.6), (hx_ - 5.8, mid_y + 1.2), (hx_ - 8.4, mid_y + 2.6)],
                sharp=(3, 4, 5, 6, 7, 8, 9))
        fig.part(key + '_up', up, BROWN, grad=(hx_ + 7, hy_ - 3, hx_ - 6, mid_y + 4, [(0, BROWN.light), (0.5, BROWN.base), (1, BROWN.shadow)]),
                 cel=1.3, rim=0.7, cast=1.3,
                 details=[(ribbon([(hx_ + 2.6, hy_ + 1), (hx_ + 3.6, mid_y - 2), (hx_ + 3.2, mid_y + 1.2)], [0.1, 0.8, 0.1]), BROWN.hi, 0.45)])
        return [key + s for s in ('_tars', '_btoe', '_bclaw', '_low', '_up')] + ['%s_toe%d' % (key, j) for j in range(3)] + ['%s_claw%d' % (key, j) for j in range(3)]

    lf = leg('lf', (81.6, 84.0), (83.6, 101.4), (84.0, 110.4),
             [((90.8, 113.4), 2.8), ((95.0, 114.2), 3.0), ((92.6, 115.2), 3.2)], ((78.4, 113.2), (76.2, 113.0)))
    ln = leg('ln', (50.6, 84.0), (49.4, 101.6), (50.6, 110.6),
             [((57.6, 113.4), 2.8), ((61.6, 114.2), 3.0), ((59.4, 115.2), 3.2)], ((45.0, 113.2), (42.8, 113.0)))

    # ================================================================ les tassettes : grandes plumes d'or à nervure
    def gold_feather(name, root, tip, w, cast=1.0):
        d = norm((tip[0] - root[0], tip[1] - root[1]))
        side = (-d[1], d[0])
        L = math.dist(root, tip)
        sh = plume(root, add(root, d, L * 0.33), add(add(root, d, L * 0.7), side, 0.6), tip, w, tip=0.35)
        fig.part(name, sh, GOLD, grad=(root[0] + 4, root[1], tip[0] - 2, tip[1], [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
                 cel=1.0, rim=0.6, cast=cast,
                 details=[(ribbon([lerp(root, tip, 0.08), lerp(root, tip, 0.5), lerp(root, tip, 0.9)], [0.2, 0.7, 0.1]), GOLD.shadow, 0.8),
                          (ribbon([add(lerp(root, tip, 0.1), side, -0.6), add(lerp(root, tip, 0.5), side, -0.6), add(lerp(root, tip, 0.85), side, -0.4)], [0.1, 0.5, 0.1]), GOLD.hi, 0.7)])
        return name
    tas = [gold_feather('tf1', (80.0, 77.0), (83.4, 90.6), 7.4), gold_feather('tf2', (76.6, 77.4), (77.8, 88.4), 6.6),
           gold_feather('tn1', (49.2, 76.8), (45.4, 93.4), 8.4), gold_feather('tn3', (56.8, 77.0), (56.2, 94.6), 8.0),
           gold_feather('tn2', (52.8, 77.0), (50.4, 95.6), 8.6)]

    # ================================================================ le buste : ventre de plumes brunes, cuirasse d'or
    torso = sm([(58.4, 50.4), (52.6, 53.0), (47.4, 58.6), (45.6, 65.6), (50.6, 71.6), (54.6, 77.6), (66.0, 79.0),
                (79.4, 77.6), (80.6, 71.0), (83.6, 64.6), (85.6, 58.6), (83.0, 53.4), (77.0, 50.4)])
    det = [(sm([(54.0, 69.0), (79.6, 69.2), (80.6, 72.4), (79.6, 77.8), (66, 79.2), (54.6, 77.8), (54.0, 73)]), BROWN.base, 1)]
    # les plumes du ventre (sous la cuirasse) : quelques pointes douces
    for (x, y, s) in ((57.6, 73.6, 1.0), (62.4, 74.4, 1.1), (67.6, 74.6, 1.1), (72.6, 74.2, 1.0), (77.2, 73.4, 0.9)):
        det.append((sm([(x - 2.4 * s, y - 2.6), (x + 2.4 * s, y - 2.6), (x + 0.2, y + 2.6 * s)], sharp=(2,)), BROWN.light, 0.55))
    # la cuirasse d'or galbée : deux coques éclairées en haut à droite (la lointaine plus étroite)
    cuir = sm([(52.0, 55.0), (58.6, 52.6), (76.6, 52.6), (84.6, 56.4), (83.4, 63.4), (80.6, 69.6), (67.6, 71.6),
               (54.6, 70.2), (51.2, 63.4)])
    det += [(cuir, ('lin', 82, 52, 56, 70, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1)]
    shellN = sm([(55.0, 57.6), (61.6, 55.4), (68.6, 56.6), (70.0, 62.6), (66.8, 68.0), (59.6, 68.6), (54.6, 64.6)])
    shellF = sm([(71.8, 56.4), (77.6, 55.2), (82.6, 57.6), (82.0, 63.4), (78.6, 67.6), (73.0, 67.4), (70.8, 62.4)])
    for sh_, cx, cy in ((shellN, 63.0, 59.0), (shellF, 78.4, 58.6)):
        det += [(sh_.move(-0.6, 1.0), GOLD.shadow, 0.9),
                (sh_, ('rad', cx + 2.6, cy - 1.4, 9.0, 8.0, [(0, GOLD.hi), (0.35, GOLD.light), (0.8, GOLD.base), (1, GOLD.shadow)]), 1)]
    det += [(ellipse(66.0, 58.8, 2.0, 0.9, -20), GOLD.hi, 0.9), (ellipse(80.6, 58.2, 1.3, 0.7, -20), GOLD.hi, 0.85),
            (ribbon([(70.4, 57.0), (70.8, 62.6), (69.6, 69.4)], [0.2, 1.0, 0.2]), GOLD.shadow, 0.7),
            (ribbon([(53.0, 70.0), (66.0, 71.8), (80.4, 69.6)], [0.2, 1.2, 0.2]), GOLD.deep, 0.55)]
    fig.part('torso', torso, BROWN, cel=1.6, rim=0.6, cast=1.2, details=det, occl=(BROWN.deep, 0.25, 3.0))

    # ---- la ceinture de cuir (plus basse devant), la boucle ronde d'or au jade ----
    belt = sm([(53.6, 72.4), (66.0, 74.4), (80.6, 72.0), (81.0, 76.4), (66.0, 78.6), (53.8, 76.8)])
    fig.part('belt', belt, BELT, cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([(54.6, 73.6), (66, 75.4), (80, 73.2)], [0.1, 0.4, 0.1]), BELT.hi, 0.5)])
    fig.part('buckle', ellipse(66.4, 76.2, 3.0, 2.9), GOLD, cel=0.8, rim=0.6, cast=0.9,
             details=[(ellipse(66.5, 76.2, 1.7, 1.6), JADE.shadow, 1), (ellipse(66.6, 76.0, 1.3, 1.2), ('rad', 67.1, 75.5, 1.5, 1.5, [(0, JADE.hi), (0.5, JADE.light), (1, JADE.base)]), 1),
                      (ellipse(67.0, 75.6, 0.4, 0.35), '#ffffff', 0.9)])

    # ---- le tablier de jade qui pend droit (un pli, ourlet d'or, pendentif en losange brodé) ----
    sway = 0.25 * math.sin(ph * 0.8 + 0.5) + P['wave'] * 0.6
    apron = sm([(60.4, 77.4), (72.2, 77.6), (72.4 + sway * 0.4, 86), (72.8 + sway, 96.6), (60.0 + sway, 96.8), (60.2 + sway * 0.4, 86)],
               sharp=(3, 4), t=0.6)
    hem = sm([(59.9 + sway, 94.6), (72.9 + sway, 94.4), (72.9 + sway, 97.0), (59.9 + sway, 97.2)], sharp=(0, 1, 2, 3), t=0.5)
    dia = sm([(66.4, 81.4), (68.4, 84.6), (66.4 + sway * 0.4, 88.2), (64.4, 84.6)], sharp=(0, 1, 2, 3), t=0.4)
    fig.part('apron', apron, JADE, grad=(72, 78, 61, 96, [(0, JADE.light), (0.5, JADE.base), (1, JADE.shadow)]), cel=1.2, rim=0.8, cast=1.0,
             details=[(ribbon([(63.0, 79.0), (62.8 + sway * 0.3, 87), (62.6 + sway * 0.8, 94.4)], [0.2, 1.4, 0.4]), JADE.shadow, 0.75),
                      (ribbon([(69.8, 79.0), (70.2 + sway * 0.3, 87), (70.4 + sway * 0.8, 94.4)], [0.2, 0.9, 0.3]), JADE.hi, 0.45),
                      (hem, GOLD.base, 1), (sm([(59.9 + sway, 94.6), (72.9 + sway, 94.4), (72.9 + sway, 95.4), (59.9 + sway, 95.6)], sharp=(0, 1, 2, 3), t=0.5), GOLD.light, 1),
                      (dia.scale(1.35, 1.25, 66.4, 84.8), GOLD.shadow, 1), (dia, GOLD.base, 1),
                      (sm([(66.4, 81.6), (68.1, 84.4), (66.4, 84.6)], sharp=(0, 1, 2), t=0.4), GOLD.hi, 0.9),
                      (ellipse(66.4, 84.7, 0.6, 0.6), JADE.hi, 1)])
    # les tassettes de la hanche lointaine passent sous le tablier, celles de la hanche proche par-dessus le ventre

    # ================================================================ l'épaulière lointaine (dôme d'or), devant le buste
    domeF = sm([(79.0, 54.8), (83.0, 51.0), (88.2, 51.4), (91.6, 55.2), (91.0, 60.0), (86.2, 61.6), (80.8, 60.6)])
    fig.part('domeF', domeF, GOLD, cel=1.1, rim=0.8, cast=1.1,
             details=[(sm([(83.0, 53.6), (86.8, 51.9), (90.4, 54.2), (87.2, 54.4)]), GOLD.hi, 0.7)])
    fr_names = []
    for i, (x, y, w, L) in enumerate(((81.6, 59.4, 3.0, 4.4), (84.4, 60.4, 3.4, 4.8), (87.4, 60.2, 3.2, 4.4), (90.0, 58.8, 2.8, 3.6))):
        nm = 'frF%d' % i
        fr_names.append(nm)
        sh = plume((x, y), (x + 0.1, y + L * 0.35), (x + 0.2, y + L * 0.7), (x + 0.4 + 0.2 * i, y + L), w, n=8, tip=0.45)
        fig.part(nm, sh, GOLD, grad=(x + 1, y, x - 1, y + L, g2(GOLD.light, GOLD.shadow)), cel=0.6, rim=0.4, cast=0.8)

    # ================================================================ le bras proche : bras et avant-bras d'une seule
    # forme (le coude en arrière, aucune couture), le brassard de cuir aux bagues d'or ; le poing sur la corde
    hand = P['hand']
    Sn = (S_N[0], S_N[1] - 0.6 * br)
    Wn = (hand[0] - 4.6, hand[1] + 0.6)
    En = ik(Sn, Wn, L1N, L2N, 1)
    narm = bent(Sn, En, Wn, 9.6, 8.0, 6.6, bulge=(0.08, 0.1))
    na = math.atan2(Wn[1] - En[1], Wn[0] - En[0])
    Ln = math.dist(En, Wn)
    N_ = lambda sh: xf(sh, En[0], En[1], math.degrees(na))
    sg = -1 if math.cos(na) > 0 else 1        # le dessus de l'avant-bras (vers la lumière)
    bz = lambda u0, u1, h0, h1, r=0.6: N_(rpoly([(Ln * u0, -h0), (Ln * u1 + 1.4, -h1), (Ln * u1 + 1.4, h1), (Ln * u0, h0)], r))
    bztop = lambda u0, u1, h0, h1, k0, k1: N_(rpoly([(Ln * u0, -h0 * -sg), (Ln * u1 + 1.4, -h1 * -sg), (Ln * u1 + 1.4, -k1 * -sg), (Ln * u0, -k0 * -sg)], 0.4))
    fig.part('narm', narm, ARM, cel=1.6, rim=0.8, cast=1.4, cast_on=['torso', 'belt', 'buckle', 'tn1', 'tn2', 'tn3'] + nw_names,
             details=[(ribbon([lerp(Sn, En, 0.2), lerp(Sn, En, 0.6), lerp(En, Wn, 0.05)], [0.1, 1.2, 0.1]), ARM.light, 0.6),
                      (bz(0.22, 1.0, 4.6, 4.0, 1.0), LEATHER.base, 1),
                      (bztop(0.22, 1.0, 4.6, 4.0, 1.6, 1.4), LEATHER.light, 0.95),
                      (N_(ribbon([(Ln * 0.3, 2.6 * sg), (Ln * 0.65, 2.9 * sg), (Ln * 0.98, 2.4 * sg)], [0.1, 0.8, 0.1])), LEATHER.shadow, 0.7),
                      (bz(0.2, 0.3, 4.9, 4.9, 0.4), GOLD.base, 1), (bztop(0.2, 0.3, 4.9, 4.9, 2.4, 2.4), GOLD.light, 1),
                      (bz(0.92, 1.0, 4.3, 4.3, 0.4), GOLD.base, 1), (bztop(0.92, 1.0, 4.3, 4.3, 2.0, 2.0), GOLD.light, 1),
                      (N_(ellipse(Ln * 0.62, 0.2 * sg, 1.1, 1.1)), GOLD.shadow, 1), (N_(ellipse(Ln * 0.62, 0.0, 0.85, 0.85)), GOLD.base, 1),
                      (N_(ellipse(Ln * 0.62 + 0.3, -0.3, 0.38, 0.38)), GOLD.hi, 1)])

    # ---- l'épaulière proche : grand dôme d'or bordé d'un rang de plumes d'or pendantes ----
    frN = []
    for i, (x, y, L, w) in enumerate(((41.0, 58.8, 4.8, 4.0), (44.6, 60.2, 5.4, 4.4), (48.4, 60.8, 5.2, 4.4), (52.2, 60.4, 4.6, 4.0), (55.4, 58.8, 3.8, 3.4))):
        nm = 'frN%d' % i
        frN.append(nm)
        a = 96 - 4 * (i - 2) + 2.0 * math.sin(ph - 0.7 * i) * P['ruff'] * 0.3
        tip = add((x, y), unit(a), L)
        sh = plume((x, y), add((x, y), unit(a), L * 0.33), add((x, y), unit(a - 4), L * 0.7), tip, w, n=8, tip=0.42)
        fig.part(nm, sh, GOLD, grad=(x + 2, y - 1, tip[0] - 1, tip[1], [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.7, rim=0.5, cast=0.9,
                 details=[(ribbon([(x, y + 0.6), lerp((x, y), tip, 0.5), lerp((x, y), tip, 0.85)], [0.2, 0.5, 0.1]), GOLD.shadow, 0.8)])
    domeN = sm([(38.6, 56.6), (41.6, 50.6), (47.6, 47.4), (54.6, 48.0), (58.6, 52.6), (58.4, 58.0), (53.6, 61.6), (45.6, 62.0), (40.0, 60.6)])
    fig.part('domeN', domeN, GOLD, cel=1.4, rim=0.9, cast=1.3,
             details=[(sm([(40.8, 55.4), (43.6, 51.0), (48.6, 48.6), (54.2, 49.2), (57.4, 52.6), (52.6, 51.6), (46.6, 52.4), (42.4, 56.2)]), GOLD.light, 0.85),
                      (ribbon([(43.4, 54.0), (47.6, 50.6), (54.0, 50.2)], [0.2, 1.1, 0.2]), GOLD.hi, 0.9),
                      (ribbon([(40.6, 58.6), (48.6, 60.4), (57.0, 57.6)], [0.2, 1.6, 0.2]), GOLD.deep, 0.35),
                      (ellipse(54.2, 51.6, 1.3, 0.7, -30), '#ffffff', 0.8)])

    # ================================================================ le cou : col brun, puis longues plumes blanches
    # Le col de plumes brunes (du corps) est posé sur la cuirasse ; il remonte entre les pointes blanches.
    collar = sm([(56.6, 47.0), (81.6, 47.0), (85.4, 52.6), (85.0, 58.4), (82.4, 59.2), (80.2, 62.2), (77.2, 60.6), (74.2, 64.0),
                 (70.8, 61.6), (67.4, 64.8), (64.0, 62.0), (60.6, 64.4), (57.6, 61.0), (54.2, 62.2), (52.4, 56.6), (53.2, 51.0)],
                sharp=(3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    fig.part('collar', collar, BROWN, grad=(84, 50, 56, 63, [(0, BROWN.light), (0.5, BROWN.base), (1, BROWN.shadow)]),
             cel=1.0, rim=0.6, cast=1.1, cast_on=['torso', 'domeF', 'domeN'] + fr_names + frN)
    # Les longues plumes blanches du cou : elles s'allongent en descendant, leurs pointes tournent au tiède
    # (mauve-taupe) ; longueurs et écarts inégaux ; elles frémissent (ruff) et s'évasent sur les deux épaulières.
    RUFF = [
        # (racine, bout, largeur, courbure) — d'abord la rangée du fond (pointes entre celles de devant), puis celle de
        # devant ; de la nuque (gauche, dans l'ombre) vers la gorge ; longueurs et écarts inégaux
        ((58.4, 46.0), (55.4, 59.6), 6.0, 0.8, 0),
        ((64.6, 47.4), (62.6, 61.6), 6.4, 0.5, 0),
        ((70.4, 47.4), (70.0, 60.8), 6.2, 0.2, 0),
        ((76.0, 46.4), (77.4, 59.0), 5.8, -0.2, 0),
        ((55.6, 44.6), (51.4, 57.2), 6.4, 1.0, 1),
        ((61.6, 46.6), (59.0, 60.4), 6.8, 0.7, 1),
        ((67.6, 47.6), (66.4, 62.0), 7.0, 0.4, 1),
        ((73.2, 47.0), (73.8, 60.2), 6.6, 0.0, 1),
        ((78.6, 45.2), (81.4, 56.8), 6.0, -0.4, 1),
        ((81.4, 43.6), (85.6, 52.8), 4.8, -0.6, 1),
    ]
    rn = []
    rf = P['ruff']
    for i, (r0, t0, w, cv, front) in enumerate(RUFF):
        d = norm((t0[0] - r0[0], t0[1] - r0[1]))
        side = (-d[1], d[0])
        L = math.dist(r0, t0) * (1 + 0.05 * rf)
        flick = 0.4 * math.sin(ph * 1.3 - 0.9 * i) + 0.5 * rf * math.sin(ph * 4 - 1.3 * i)
        tip = add(add(r0, d, L), side, flick + 0.4 * rf * (r0[0] - 68) / 8)
        sh = plume(r0, add(add(r0, d, L * 0.35), side, cv * 0.6), add(add(r0, d, L * 0.72), side, cv + 0.2 * flick), tip, w, tip=0.42)
        nm = 'ruff%d' % i
        rn.append(nm)
        light = r0[0] > 63
        c0 = WHITE.light if light else WHITE.base
        c1 = WHITE.base if light else '#d4d0e6'
        if not front:
            c0, c1 = c1, '#c8c3dc'
        fig.part(nm, sh, WHITE, grad=(r0[0] + 2, r0[1], tip[0], tip[1], [(0, c0), (0.45, c1), (0.72, WARM.light if light else WARM.base), (1, WARM.shadow if light else WARM.deep)]),
                 cel=0.7, rim=0.45 if light else 0.25, cast=0.8, cast_on=['collar', 'torso', 'domeF', 'domeN'] + fr_names + frN + rn[:-1])
    # ================================================================ la tête de pygargue (agrandie ×1,1 autour du cou)
    # crâne plat, front qui avance en arcade au-dessus de l'œil, petites plumes pointues sur la nuque ; le bas de la
    # tête finit en courtes pointes de plumes posées sur les longues plumes du cou (aucune coupure)
    head = sm([(53.8, 25.0), (58.0, 20.6), (64.0, 18.8), (71.0, 18.4), (77.0, 19.2), (81.2, 21.6), (83.4, 25.4), (84.2, 29.0),
               (84.0, 33.0), (82.8, 37.2), (81.0, 41.0), (79.2, 44.6), (76.8, 48.0), (73.8, 46.2), (70.2, 49.2), (66.8, 46.8),
               (63.0, 49.0), (59.8, 46.6), (56.2, 47.8), (53.6, 44.4), (52.2, 41.8), (50.2, 39.0),
               (51.8, 35.8), (50.8, 32.2), (52.6, 28.8)],
              sharp=(12, 13, 14, 15, 16, 17, 18, 21, 23))
    hd = []
    # le côté de la tête vers la nuque, dans l'ombre lilas (plans nets), la demi-teinte autour ; la gorge sous le bec
    # (le bord des plans n'est pas une courbe lisse : de petites pointes de plumes couchées vers la nuque)
    hd += [(sm([(52.6, 28.8), (56.4, 26.2), (57.4, 29.6), (59.6, 32.2), (57.8, 33.4), (59.0, 36.8), (61.0, 39.6), (58.8, 40.4),
                (60.0, 43.6), (61.4, 47.0), (58.6, 47.0), (55.6, 48.6), (53.4, 44.6), (52.2, 41.8), (50.2, 39.0), (51.8, 35.8), (50.8, 32.2)],
               sharp=(3, 4, 6, 7, 9, 10)), WHITE.shadow, 0.9),
           (sm([(56.6, 24.2), (60.6, 22.8), (60.8, 27.6), (62.2, 32.0), (60.8, 33.0), (62.0, 36.8), (64.4, 40.2), (62.6, 40.6), (64.0, 44.2),
                (65.6, 46.6), (62.4, 47.6), (60.0, 43.6), (58.6, 37.4), (58.4, 31.0)], sharp=(3, 4, 6, 7, 9, 10)), '#d4d0e6', 0.8),
           (sm([(69.4, 41.6), (78.4, 44.6), (79.0, 46.4), (76.8, 48.4), (73.0, 47.2), (69.0, 44.6)]), '#d4d0e6', 0.7)]
    # quelques petites plumes sur la joue (des festons doux, jamais de traits sombres)
    for (x, y, s) in ((60.4, 41.8, 1.0), (63.8, 43.8, 1.0), (67.0, 45.4, 0.8)):
        hd.append((ribbon([(x - 2.2 * s, y - 0.6), (x, y + 0.9), (x + 2.2 * s, y - 0.4)], [0.1, 0.55, 0.1]), WHITE.shadow, 0.45))
    # le front lumineux, en haut à droite
    hd += [(sm([(66.0, 20.0), (73.6, 19.6), (79.2, 21.8), (81.8, 24.8), (77.0, 23.8), (71.6, 22.2)]), '#ffffff', 0.7)]
    # ---- le visage, placé par visage.py (tête d'aigle de 3/4 : les deux yeux sur la même ligne, la racine du bec SUR
    # la médiane, au milieu de l'écart entre les yeux ; le bec descend de là, crochet vers l'avant). Les places viennent
    # de FACE_V, les formes restent celles du pygargue (arcade lourde, iris d'ambre coupé en haut : regard dur).
    (exn, eyy, ewn), (exf, _, ewf) = FACE_V['oeil_proche'], FACE_V['oeil_fond']
    fixk = P['fix']
    # les deux arcades, lourdes, plus basses du côté du bec (le « V » du regard dur) : l'ombre violette dessous coupe
    # le haut de l'iris, la crête claire au-dessus ; entre les deux, le blanc du front descend jusqu'à la racine du bec
    # (formes données pour l'œil proche, coin extérieur à gauche ; l'œil du fond les reprend en miroir, un peu plus étroites)
    BROW_SH = [(-4.5, -1.3), (-4.6, -2.1), (-1.0, -3.3), (4.5, -1.0), (3.9, 0.1), (2.4, -0.5), (-2.6, -1.6)]
    BROW_HI = [(-4.9, -2.3), (-1.2, -4.3), (4.8, -1.6), (4.5, -1.0), (-1.0, -3.3), (-4.6, -2.1)]
    EYE_SH = [(-3.6, 0.3), (-2.6, -1.5), (2.4, -0.4), (3.6, 0.6), (2.0, 1.8), (-1.6, 1.9)]
    eyes = []
    for cx, w_, side in ((exn, ewn, 1), (exf, ewf, -1)):
        k = w_ / ewn

        def loc(pts, cx=cx, k=k, side=side):
            return [(cx + side * x * k, eyy + y) for (x, y) in pts]
        hd += [(sm(loc(BROW_SH), sharp=(0, 3)), WHITE.deep, 0.62 + 0.1 * fixk),
               (sm(loc(BROW_HI), sharp=(0, 2)), '#ffffff', 1)]
        eyes.append((sm(loc(EYE_SH), sharp=(0, 3)), cx, w_, side, k))
    # les yeux : amande d'ambre au bord haut tendu et penché vers le bec, pupille noire qui touche la paupière et
    # regarde vers la cible (à droite), petit reflet ; l'œil du fond un peu plus étroit (même hauteur, même regard)
    for e, cx, w_, side, k in eyes:
        cy = eyy
        pr = 1.15
        pc = (cx + 0.75 * k, cy + 0.3)               # les deux pupilles regardent du même côté (vers la cible)
        hd += [(e.scale(1.1, 1.25, cx, cy + 0.2), WHITE.deep, 0.9)]
        if P['blink'] > 0.5:
            x0_, _, x1_, _ = e.bbox()
            hd += [(e, WHITE.base, 1), (ribbon([(x0_ + 0.4, cy + 0.6), (cx, cy + 1.2), (x1_ - 0.4, cy + 0.6)], [0.1, 0.6, 0.1]), WHITE.shadow, 0.9)]
        else:
            hd += [(e, ('rad', cx + 0.5, cy - 0.2, 0.5 * w_, 0.5 * w_, [(0, EYE[0]), (0.45, EYE[1]), (1, EYE[2])]), 1),
                   (ellipse(pc[0], pc[1], pr * k ** 0.4, pr * 1.05), EYE[3], 1),
                   # l'ombre de l'arcade sur le haut de l'iris
                   (sm([(cx + side * x * k, cy + y) for (x, y) in [(-3.4, 0.0), (-2.6, -1.5), (2.4, -0.4), (3.4, 0.4), (1.6, 0.4 + 0.3 * fixk), (-2.0, -0.2 + 0.3 * fixk)]]),
                    WHITE.deep, 0.4 + 0.15 * fixk)]
            if fixk < 0.5:
                hd += [(ellipse(pc[0] + 0.45 * pr, pc[1] - 0.1, pr * 0.32, pr * 0.28), '#ffffff', 1)]
    fig.part('head', head, WHITE, grad=(81, 19, 53, 46, [(0, '#ffffff'), (0.45, WHITE.light), (0.8, WHITE.base), (1, '#d4d0e6')]),
             cel=1.1, rim=0.6, cast=1.3, cast_on=['collar'] + rn + ['domeF', 'domeN'] + fr_names + frN, details=hd)
    # ---- le bec, vu de 3/4 : sa racine (la cire claire) entre les deux yeux, sur la médiane ; il s'élargit sous les
    # yeux, l'arête éclairée un peu à droite de la médiane, le crochet tombe devant la mandibule. Bouche fermée : la
    # mandibule dépasse à peine sous le bord du bec (côté proche), la commissure finit sous l'œil proche. ----
    nx, ny = FACE_V['nez']
    mand = sm([(67.4, 38.8), (70.0, 41.0), (72.8, 43.0), (75.6, 45.4), (75.6, 46.8), (72.6, 45.6), (69.8, 43.6), (67.6, 41.4), (66.6, 39.8)])
    fig.part('mand', mand, BEAK, grad=(76, 44, 67, 41, [(0, BEAK.base), (0.6, BEAK.shadow), (1, BEAK.deep)]), cel=0.6, rim=0.4, cast=0.9,
             details=[(ribbon([(68.4, 41.0), (71.4, 43.4), (74.6, 45.6)], [0.1, 0.5, 0.1]), BEAK.light, 0.4),
                      (ellipse(67.4, 39.7, 1.2, 0.95, 35), BEAK.light, 0.75)])
    # le bec : un écu qui part de la racine (entre les yeux), s'élargit jusqu'aux deux commissures (sous chaque œil) et
    # se referme sur le crochet ; l'arête un peu à droite de la médiane (il avance vers la droite), le côté droit dans
    # la lumière, le côté proche dans la demi-teinte
    beak = sm([(nx - 2.4, eyy - 0.6), (nx, eyy - 1.4), (nx + 2.4, eyy - 0.6), (nx + 3.4, eyy + 2.4), (79.6, 35.6), (80.6, 37.8),
               (80.4, 40.6), (79.6, 43.4), (78.4, 46.0), (76.6, 48.0), (76.0, 46.6), (75.0, 44.6), (72.6, 42.2), (69.8, 40.2),
               (67.6, 38.6), (68.2, 36.6), (70.0, 34.8), (nx - 2.8, eyy + 1.8)], sharp=(9, 13))
    bk = [(sm([(67.6, 38.6), (68.2, 36.6), (70.0, 35.4), (72.4, 36.6), (74.6, 39.4), (76.4, 43.4), (76.6, 48.0), (76.0, 46.6), (75.0, 44.6),
               (72.6, 42.2), (69.8, 40.2)], sharp=(0, 6)), BEAK.shadow, 0.5),
          # la cire, plus claire, à la racine (entre les yeux), et la narine du côté proche
          (sm([(nx - 2.4, eyy - 0.6), (nx, eyy - 1.4), (nx + 2.4, eyy - 0.6), (nx + 3.2, eyy + 2.0), (nx + 2.2, eyy + 3.2), (nx, eyy + 3.6),
               (nx - 2.2, eyy + 3.2), (nx - 2.8, eyy + 1.8)]), BEAK.hi, 0.75),
          (ribbon([(nx - 2.2, eyy + 2.4), (nx - 1.3, eyy + 2.0), (nx - 0.5, eyy + 2.1)], [0.5, 0.7, 0.2]), BEAK.deep, 0.9),
          # l'arête éclairée (la lumière vient d'en haut à droite), jusqu'au crochet
          (ribbon([(nx + 0.6, eyy + 3.0), (nx + 1.9, eyy + 6.0), (nx + 3.0, eyy + 10.0), (nx + 3.6, eyy + 12.8), (77.2, 46.8)],
                  [0.1, 0.7, 0.8, 0.5, 0.1]), '#fffbe0', 0.75),
          # la ligne de fermeture du bec (bouche fermée) et l'ombre sous le crochet
          (ribbon([(67.6, 38.6), (69.8, 40.3), (72.6, 42.3), (75.0, 44.7), (76.0, 46.6)], [0.4, 0.7, 0.7, 0.5, 0.1]), BEAK.deep, 0.7),
          (ribbon([(80.4, 38.4), (79.8, 41.6), (78.4, 45.0)], [0.1, 0.5, 0.1]), BEAK.shadow, 0.5)]
    fig.part('beak', beak, BEAK, grad=(80, 33, 70, 43, [(0, BEAK.light), (0.5, BEAK.base), (1, BEAK.shadow)]), cel=0.7, rim=0.6, cast=1.2,
             details=bk, cast_on=['head', 'mand'] + rn + ['collar'])
    # les positions réelles des traits (repère de la tête, avant l'agrandissement) : contrôlées par visage.verifier
    fig_face.update(oeil_proche=(exn, eyy, ewn), oeil_fond=(exf, eyy, ewf), nez=(nx, eyy + 2.0), bouche=(nx + 0.6, 42.4, 7.6))

    # ================================================================ l'arc récurve de jade (tenu par la main lointaine)
    rl = P['relax']
    bt = P['bow_tilt']
    G = grip

    def bow_pt(p):
        return rot_about((p[0] + bx, p[1]), G, bt)
    # la ligne de l'arc (le dos), du bout haut au bout bas : bras qui se bandent vers l'archère, pointes recourbées
    top_tip = bow_pt((104.6 + 1.0 * rl, 32.6 - 0.5 * rl))
    bot_tip = bow_pt((104.6 + 1.0 * rl, 104.6 + 0.5 * rl))
    spine = crpath([bow_pt((106.6 + 0.4 * rl, 31.0 - 0.5 * rl)), top_tip, bow_pt((107.4 + 0.6 * rl, 38.6)), bow_pt((110.4 + 0.2 * rl, 50.0)),
                    bow_pt((110.6, 61.0)), bow_pt((110.6, 76.2)), bow_pt((110.4 + 0.2 * rl, 87.2)), bow_pt((107.4 + 0.6 * rl, 98.6)),
                    bot_tip, bow_pt((106.6 + 0.4 * rl, 106.2 + 0.5 * rl))], n=60)
    ws = []
    for i in range(61):
        t = i / 60
        mid = 1 - abs(t - 0.5) * 2
        ws.append(1.5 + 2.2 * mid ** 0.8)
    bow = taper(spine, 1.5, 1.5, wmid=None)
    # largeur variable : refait à la main
    from atelier import sides as sides_
    L_, R_ = sides_(spine, ws)
    bow = sm(L_ + R_[::-1], t=0.9)
    fig.part('bow', bow, JADE, grad=(114, 40, 104, 70, [(0, JADE.hi), (0.35, JADE.light), (0.7, JADE.base), (1, JADE.shadow)]),
             cel=0.9, rim=0.6, cast=1.0,
             details=[(ribbon([spine[k_] for k_ in range(8, 53, 4)], [0.1] + [0.7] * 10 + [0.1]), JADE.hi, 0.55)])
    # les embouts d'or (les pointes) et les bagues d'or de part et d'autre de la poignée
    for nm, a, b in (('bt_top', 1, 7), ('bt_bot', 53, 59)):
        seg = spine[a - 1:b + 1]
        sh = limb(seg, [2.6] * len(seg))
        fig.part(nm, sh, GOLD, cel=0.5, rim=0.5, cast=0.6)
    for nm, i0 in (('bring_t', 22), ('bring_b', 37)):
        c = spine[i0]
        d = norm((spine[i0 + 1][0] - spine[i0 - 1][0], spine[i0 + 1][1] - spine[i0 - 1][1]))
        sh = limb([add(c, d, -0.8), add(c, d, 0.8)], [5.2, 5.2])
        fig.part(nm, sh, GOLD, cel=0.5, rim=0.5, cast=0.6)
    # la poignée de cuir
    c0, c1 = spine[24], spine[36]
    fig.part('bgrip', limb([c0, spine[30], c1], [4.6, 4.8, 4.6]), BELT, cel=0.6, rim=0.4, cast=0.6)

    # ---- le poing lointain, serré sur la poignée : doigts d'aigle (jointures vers nous), pouce par-dessus ----
    fx_, fy_ = G[0], G[1] + 2.8                # le poing est SOUS la flèche (elle repose sur l'index)
    fist = sm([(fx_ - 5.2, fy_ - 4.0), (fx_ - 1.0, fy_ - 4.8), (fx_ + 3.2, fy_ - 4.4), (fx_ + 4.4, fy_ - 1.2), (fx_ + 4.2, fy_ + 3.0),
               (fx_ + 1.6, fy_ + 5.2), (fx_ - 2.8, fy_ + 5.0), (fx_ - 5.6, fy_ + 1.6)])
    fig.part('ffist', fist, BEAK, cel=1.0, rim=0.6, cast=1.0,
             details=[(sm([(fx_ - 4.8, fy_ - 3.6), (fx_ - 1.0, fy_ - 4.4), (fx_ - 0.4, fy_ - 0.6), (fx_ - 4.4, fy_ + 0.4)]), BEAK.light, 0.5)])
    # les doigts repliés sur la poignée, jointures vers nous (quatre phalanges de tailles inégales), griffes rentrées
    for j, (y0, h, x1) in enumerate(((-4.4, 2.6, 4.2), (-1.9, 2.5, 4.6), (0.5, 2.4, 4.4), (2.8, 2.2, 3.6))):
        seg = rpoly([(fx_ - 1.0, fy_ + y0), (fx_ + x1, fy_ + y0 + 0.2), (fx_ + x1 + 0.4, fy_ + y0 + h), (fx_ - 1.0, fy_ + y0 + h)], [0.5, 1.1, 1.1, 0.5])
        fig.part('ff%d' % j, seg, BEAK, cel=0.55, rim=0.45, cast=0.55, cast_on=['ffist'] + ['ff%d' % k for k in range(j)],
                 details=[(ellipse(fx_ + x1 - 1.6, fy_ + y0 + 0.7, 1.3, 0.4), BEAK.hi, 0.55),
                          (sm([(fx_ + x1 - 0.6, fy_ + y0 + h - 0.9), (fx_ + x1 + 0.9, fy_ + y0 + h - 0.2), (fx_ + x1 - 0.4, fy_ + y0 + h + 0.4)], sharp=(1,)), CLAW.base, 0.9)])
    fig.part('fthumb', limb([(fx_ - 4.2, fy_ - 2.0), (fx_ - 1.6, fy_ - 3.4), (fx_ + 1.2, fy_ - 3.6)], [3.0, 2.8, 2.4]), BEAK, cel=0.6, rim=0.5, cast=0.7)

    # ================================================================ la corde (deux traits fins et clairs) et la flèche
    Hn = hand
    ta = (top_tip[0] - 0.2, top_tip[1] + 2.4)
    ba = (bot_tip[0] - 0.2, bot_tip[1] - 2.4)
    # l'encoche : dans le poing proche ; quand la corde est libre (free = 1), au milieu de la corde droite, qui vibre
    hold = (Hn[0] + 3.0, Hn[1] + 0.4)
    mid = lerp(ta, ba, (hold[1] - ta[1]) / ((ba[1] - ta[1]) or 1))
    mid = (mid[0] + P['bulge'], mid[1])
    nock = lerp(hold, mid, max(0.0, min(1.0, P['free'])))
    strings = [[ta, nock], [ba, nock]]
    for i, s in enumerate(strings):
        # un fil clair (pas de gros contour : une fine bordure sombre, comme le trait d'un pixel du pixel art)
        edge = ribbon(resample(s, 8), [0.5] + [1.25] * 7 + [0.5], sharp_ends=False)
        core = ribbon(resample(s, 8), [0.2] + [0.55] * 7 + [0.2], sharp_ends=False)
        fig.part('sedge%d' % i, edge, WHITE, grad=(ta[0], ta[1], nock[0], nock[1], [(0, INK, 0.75), (1, INK, 0.75)]), cel=0, rim=0, cast=0, outline=False)
        fig.part('string%d' % i, core, WHITE, grad=(ta[0], ta[1], nock[0], nock[1], g2('#ffffff', STRING)), cel=0, rim=0, cast=0.4, outline=False)
    if P['arrow'] > 0.5:
        a0 = nock
        L = 62.0
        tip = (a0[0] + L, a0[1])
        shaft = limb([(a0[0] + 1.0, a0[1]), (a0[0] + L * 0.5, a0[1]), (a0[0] + L - 4.0, a0[1])], [1.1, 1.1, 1.1])
        fig.part('shaft', shaft, SHAFT, grad=(a0[0], a0[1] - 1, a0[0], a0[1] + 1, [(0, SHAFT.light), (0.5, SHAFT.base), (1, SHAFT.shadow)]), cel=0, rim=0, cast=0.8)
        head_ = sm([(tip[0] - 5.4, a0[1] - 0.5), (tip[0] - 3.4, a0[1] - 2.2), (tip[0] + 0.4, a0[1]), (tip[0] - 3.4, a0[1] + 2.2), (tip[0] - 5.4, a0[1] + 0.5)],
                   sharp=(0, 2, 4), t=0.7)
        fig.part('ahead', head_, STEEL, grad=(tip[0], a0[1] - 2, tip[0] - 5, a0[1] + 2, [(0, STEEL.hi), (0.5, STEEL.light), (1, STEEL.shadow)]),
                 cel=0.4, rim=0.4, cast=0.5, details=[(ribbon([(tip[0] - 5, a0[1]), (tip[0] - 0.6, a0[1])], [0.4, 0.1]), STEEL.shadow, 0.7)])
        # l'empennage : une plume blanche au-dessus, une brune dessous (bord arrière en biais, pointe vers l'avant)
        x0f, yf = a0
        vane_b = sm([(x0f + 1.6, yf + 0.5), (x0f + 2.2, yf + 3.0), (x0f + 5.6, yf + 3.2), (x0f + 11.4, yf + 0.5)], sharp=(0, 1, 3), t=0.7)
        vane_t = sm([(x0f + 1.6, yf - 0.5), (x0f + 2.4, yf - 3.4), (x0f + 6.0, yf - 3.4), (x0f + 11.6, yf - 0.5)], sharp=(0, 1, 3), t=0.7)
        fig.part('vane_b', vane_b, BROWN, grad=(x0f + 10, yf, x0f + 2, yf + 3, g2(BROWN.light, BROWN.shadow)), cel=0.5, rim=0.4, cast=0.6)
        fig.part('vane_t', vane_t, WHITE, grad=(x0f + 10, yf - 3, x0f + 2, yf, g2('#ffffff', WHITE.base)), cel=0.5, rim=0.4, cast=0.6,
                 details=[(ribbon([(x0f + 3.0, yf - 2.2), (x0f + 6.4, yf - 1.8), (x0f + 9.6, yf - 0.9)], [0.1, 0.4, 0.1]), WHITE.shadow, 0.6)])

    # ================================================================ le poing proche, sur la corde (ou ouvert)
    hx, hy = Hn
    op = P['open']
    if op < 0.5:
        # le dos de la main (vers nous), les jointures vers l'avant ; trois doigts repliés sur la corde, griffes rentrées
        nf = sm([(hx - 5.0, hy - 2.8), (hx - 1.4, hy - 4.4), (hx + 2.0, hy - 4.0), (hx + 3.2, hy - 1.6), (hx + 2.6, hy + 3.0),
                 (hx - 1.0, hy + 4.4), (hx - 4.6, hy + 3.4), (hx - 5.8, hy + 0.4)])
        fig.part('nfist', nf, BEAK, cel=1.1, rim=0.6, cast=1.1,
                 details=[(sm([(hx - 4.6, hy - 2.4), (hx - 1.4, hy - 4.0), (hx + 1.8, hy - 3.6), (hx + 1.0, hy - 0.8), (hx - 3.2, hy - 0.4)]), BEAK.light, 0.65),
                          (ribbon([(hx - 3.6, hy + 1.2), (hx - 1.2, hy + 1.6), (hx + 1.4, hy + 1.0)], [0.1, 0.5, 0.1]), BEAK.shadow, 0.6)])
        for j, (y0, h) in enumerate(((-2.8, 2.6), (-0.4, 2.6), (2.0, 2.4))):
            seg = rpoly([(hx + 0.6, hy + y0), (hx + 4.2, hy + y0 + 0.2), (hx + 4.6, hy + y0 + h), (hx + 0.6, hy + y0 + h)], [0.5, 1.1, 1.1, 0.5])
            fig.part('nfing%d' % j, seg, BEAK, cel=0.6, rim=0.45, cast=0.6, cast_on=['nfist', 'nfing0', 'nfing1'],
                     details=[(ellipse(hx + 2.8, hy + y0 + 0.7, 1.2, 0.4), BEAK.hi, 0.6)])
        fig.part('nclaw', sm([(hx + 3.6, hy + 4.0), (hx + 4.8, hy + 4.2), (hx + 3.4, hy + 5.6)], sharp=(1, 2)), CLAW, cel=0.3, rim=0.3, cast=0.3)
        fig.part('nthumb', limb([(hx - 3.0, hy - 2.6), (hx + 0.2, hy - 3.8), (hx + 3.0, hy - 3.6)], [2.8, 2.6, 2.2]), BEAK, cel=0.6, rim=0.5, cast=0.7)
    else:
        # la main ouverte après le lâcher : les doigts d'aigle s'écartent vers l'arrière
        palm = sm([(hx - 4.4, hy - 2.6), (hx - 0.6, hy - 3.6), (hx + 1.6, hy - 1.4), (hx + 1.4, hy + 2.4), (hx - 1.6, hy + 3.6), (hx - 4.8, hy + 2.0)])
        fig.part('npalm', palm, BEAK, cel=0.9, rim=0.5, cast=1.0)
        # (les trois doigts détendus, presque parallèles, un peu écartés ; la corde vient de les quitter)
        for j, (a, L) in enumerate(((-24, 4.6), (-6, 5.2), (12, 4.6))):
            p0 = (hx + 0.4, hy - 1.8 + 1.9 * j)
            tip = add(p0, unit(a), L)
            fig.part('nfing%d' % j, limb([p0, lerp(p0, tip, 0.5), tip], [2.8, 2.5, 2.1]), BEAK, cel=0.6, rim=0.4, cast=0.7)
            fig.part('nclaw%d' % j, sm([add(tip, unit(a - 90), 0.9), add(tip, unit(a), 1.8), add(tip, unit(a + 90), 0.9)], sharp=(1,)), CLAW, cel=0.3, rim=0.3, cast=0.3)

    # ---- chaque groupe de morceaux prend sa pose ----
    names_head = ['head', 'beak', 'mand']
    fig.pose(names_head, HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['belt', 'buckle', 'apron', 'tf1', 'tf2', 'tn1', 'tn2', 'tn3', 'farm', 'narm'], U)
    fig.pose(['domeF', 'domeN', 'collar'] + fr_names + frN + rn + fw_names + nw_names, UC)
    fig.pose(lf + ln, LEG)
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, grip=G, nock=nock, top=top_tip, bot=bot_tip,
                   tip=(nock[0] + 62.0, nock[1]), eye=mapp(HEAD, FACE_V['oeil_proche'][:2]), beak=mapp(HEAD, (78.6, 42.0)), feet=FEET)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """tessa.svg (grand) et tessa-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mages-4.webp (512 px de haut) et mages-4-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('tessa', 0.95, 512, 'mages-4'), ('tessa-petit', 1.35, 160, 'mages-4-160')):
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
