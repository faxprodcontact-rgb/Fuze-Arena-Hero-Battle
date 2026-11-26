# Rook (assassins-5, feu, soigneuse) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (même
# méthode et même qualité que Kael : ../kael/kael.py, outil commun ../atelier.py ; outils en plus : outils.py).
#
#   python3 refonte-graphique/ui-moderne/heros/rook/rook.py          # → rook.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/rook.txt) : la harpie-phénix, reine des flammes, fière.
# Ses bras sont deux GRANDES AILES levées en V : le bras (épaule, coude, poignet, main) fait le bord d'attaque doré ;
# dessous, une rangée de petites couvertures d'or, une rangée de grandes couvertures orangées, puis les rémiges (rouges
# à la base, orange au milieu, pointe jaune qui se relève comme une flamme) et un rang intercalé plus sombre derrière.
# L'aile proche (à gauche) est grande, l'aile lointaine (derrière le corps) plus sombre. Bracelet d'or au rubis à la
# naissance de l'aile proche. Buste fin, plastron de plumes blanches aux ombres lilas, torque d'or et pendentif de
# rubis, ceinture d'or au médaillon, jupe de deux rangs de plumes, plumes de flanc cramoisies sous l'aile, pattes
# d'oiseau écailleuses aux serres sombres, longue queue de plumes qui touche le sol. Visage de femme fin, trois quarts
# vers la droite : sourcils fins arqués, grands yeux d'ambre au trait étiré vers la tempe, nez fin, lèvres pleines à
# peine entrouvertes ; chevelure de plumes rouges couchée vers l'arrière (pointes relevées comme des flammes), une
# plume le long de la joue, diadème d'or à fleuron et rubis.
# Coordonnées = pixels du dessin pixel art (y = 116 est le sol), pour se poser au même endroit dans le jeu.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; aucune jointure visible (outils.fuse).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import crpath, fuse, plume, under, lerp, rot, rotp, along, inter  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#fff0dc', '#ffd4b2', '#f4ac8a', '#cc7470', '#84405a')
GOLD = Mat('#fff7c4', '#ffd862', '#e29a28', '#9c4e1a', '#4c1a1e', glint='#fffbe6')
GOLDF = Mat('#ffe39a', '#e8aa3a', '#b86c22', '#7a3a1c', '#40141e')            # l'or de l'aile lointaine (ombre)
WHITE = Mat('#ffffff', '#fffaf2', '#f2e0e2', '#c6a2c2', '#8a5a88')
LEG = Mat('#ffe490', '#ffae3e', '#ea6420', '#ac3028', '#5e1430')
TALON = Mat('#dcd0f0', '#a090b8', '#5c4874', '#3a2a4e', '#22142c', glint='#f4f0ff')
RUBY = Mat('#ffd4cc', '#ff5c5c', '#d2203c', '#8c0c30', '#4a0620')
FEA = Mat('#ffd886', '#ffb83e', '#f05c1e', '#b8262e', '#6a1236')                # plumes de feu (pour les bandes)
CRIM = Mat('#ff9a6a', '#e04a30', '#a81e36', '#6c1238', '#3a0c2a')
FINK = '#330a1a'                                                                # le contour des plumes (comme Kael)
LASH = '#3a0e24'

# les dégradés des plumes, de la racine à la pointe
G_REM = [(0, '#8e1a36'), (0.32, '#d43a26'), (0.64, '#ff8a24'), (0.86, '#ffc03c'), (1, '#ffe486')]
G_REMF = [(0, '#5a1032'), (0.32, '#9e242e'), (0.64, '#dc5a22'), (0.86, '#f8952c'), (1, '#ffc052')]
G_BACK = [(0, '#5e1034'), (0.4, '#8e1c34'), (0.75, '#c8382a'), (1, '#f07a2a')]
G_BACKF = [(0, '#3e0c2c'), (0.4, '#661430'), (0.75, '#9a2a2c'), (1, '#cc5a28')]
G_COV = [(0, '#d2402a'), (0.5, '#ff8e2a'), (0.85, '#ffc240'), (1, '#ffd868')]
G_COVF = [(0, '#9a2a2c'), (0.5, '#e06624'), (0.85, '#f8a032'), (1, '#ffc050')]
G_LES = [(0, '#f4982c'), (0.55, '#ffcc48'), (1, '#fff09e')]
G_LESF = [(0, '#c86a26'), (0.55, '#eea83a'), (1, '#ffd680')]
G_CRIM = [(0, '#5a1034'), (0.45, '#9a1c36'), (0.85, '#d23c2c'), (1, '#f06a2a')]
G_SKB = [(0, '#6a1236'), (0.5, '#a01c30'), (0.85, '#d2341e'), (1, '#ef6a20')]   # jupe, rang du fond
G_SKF = [(0, '#b8262e'), (0.45, '#e2481e'), (0.8, '#ff9a26'), (1, '#ffd460')]   # jupe, rang de devant
G_TAIL = [(0, '#8a1a36'), (0.35, '#cc3424'), (0.7, '#ff8424'), (0.9, '#ffbc3c'), (1, '#ffe07e')]
G_TAILB = [(0, '#4e0e2e'), (0.4, '#86183a'), (0.75, '#c03228'), (1, '#ec7628')]
G_HAIR = [(0, '#a01c30'), (0.35, '#e0401e'), (0.68, '#ff8a24'), (0.88, '#ffbe3c'), (1, '#ffe07c')]
G_HAIRB = [(0, '#6a1236'), (0.45, '#a82030'), (0.8, '#e2522a'), (1, '#ff9a34')]

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol : 64 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin : les pieds (64, 116) y tombent en (69, 124)
FRAME = (-5, -8, 136, 126)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin et degrés (y vers le bas).
#   breath : souffle 0..1 ; crouch : elle se tasse sur ses pattes ; lean : elle se penche en avant (+) ; lift : elle
#   s'élève (pixels) ; head / tilt : la tête ; ph : phase des plumes (elles ondulent sans arrêt comme des flammes) ;
#   amp : amplitude de cette ondulation ; wn / wf : les ailes proche / lointaine tournent autour de l'épaule (degrés,
#   > 0 : elles s'abaissent) ; fold : le poignet se replie (+) ou s'ouvre (−) ; drag : les plumes traînent (vitesse du
#   battement : + quand les ailes descendent) ; q : la queue se balance ; sk : la jupe se balance ; blink : yeux
#   fermés ; fire : elle s'embrase d'or (0..3) ; legs_up : les pattes pendent (en vol).
REST = dict(breath=0.0, crouch=0.0, lean=0.0, lift=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, amp=1.0, wn=0.0, wf=0.0,
            fold=0.0, foldF=0.0, drag=0.0, q=0.0, sk=0.0, blink=0.0, fire=0.0, legs_up=0.0)

# ---- les ailes : os (épaule, coude, poignet, main, bout) et plumes, au repos ----
NEAR_BONES = [(56.5, 52.5), (46.5, 46.0), (36.0, 27.5), (27.0, 13.5), (15.0, 4.5)]
FAR_BONES = [(87.0, 53.0), (92.0, 44.0), (100.5, 26.5), (108.0, 16.5), (117.0, 9.5)]
# les pointes des rémiges, du corps vers le bout de l'aile (pixel art)
NEAR_TIPS = [(50.5, 80.0), (43.5, 81.0), (36.5, 79.5), (30.0, 76.5), (24.5, 72.0), (20.0, 66.5), (16.5, 60.0),
             (13.0, 53.5), (10.0, 47.0), (7.6, 40.5), (6.2, 34.0), (5.2, 27.5), (4.4, 21.0), (4.6, 14.5), (6.6, 8.6)]
FAR_TIPS = [(88.5, 78.5), (93.0, 80.5), (98.5, 80.0), (104.0, 77.0), (108.5, 72.5), (112.0, 67.0), (115.0, 61.0),
            (116.5, 55.0), (118.4, 48.0), (119.6, 41.0), (121.0, 33.5), (122.6, 26.0), (123.4, 19.0), (123.2, 12.6)]


def bone_pose(bones, S, r0, r1, r2):
    """Les os posés : tout tourne de r0 autour de l'épaule S, l'avant-bras de r1 en plus autour du coude, la main de
    r2 en plus autour du poignet. Rend les points posés et l'angle total de chaque tronçon."""
    b = [(p[0] - bones[0][0] + S[0], p[1] - bones[0][1] + S[1]) for p in bones]
    b = [rotp(p, r0, S) for p in b]
    E = b[1]
    b = b[:2] + [rotp(p, r1, E) for p in b[2:]]
    W = b[2]
    b = b[:3] + [rotp(p, r2, W) for p in b[3:]]
    return b


def seg_u(bones):
    """Les paramètres (0..1, longueur) du coude, du poignet, de la main le long des os au repos."""
    L = [0.0]
    for i in range(1, len(bones)):
        L.append(L[-1] + math.dist(bones[i - 1], bones[i]))
    return [x / L[-1] for x in L]


def rot_at(u, us, r0, r1, r2):
    """La rotation (degrés) d'une plume attachée au paramètre u : celle de son tronçon, fondue près des jointures."""
    def ramp(x, a, w=0.05):
        return max(0.0, min(1.0, (x - a + w) / (2 * w)))
    return r0 + r1 * ramp(u, us[1]) + r2 * ramp(u, us[2])


def wing(fig, side, P, S):
    """Une aile entière (side = 'n' proche, 'f' lointaine), son épaule posée en S. Rend les noms des morceaux."""
    near = side == 'n'
    bones0 = NEAR_BONES if near else FAR_BONES
    tips0 = NEAR_TIPS if near else FAR_TIPS
    sg = 1 if near else -1               # la rotation qui ABAISSE l'aile : −wn pour la proche (sens inverse des
    w_ = P['wn'] if near else P['wf']    # aiguilles), +wf pour la lointaine... les deux : r0 = −sg·w
    r0 = -w_ * sg + P['lean'] * 1.1
    fold = P['fold'] if near else P['foldF']
    r1 = fold * 0.5 * sg
    r2 = fold * sg
    bones = bone_pose(bones0, S, r0, r1, r2)
    us = seg_u(bones0)
    path0 = crpath(bones0, 40)
    path = crpath(bones, 40)
    ph, amp, drag = P['ph'], P['amp'], P['drag']
    names = []
    G1, GB, GC, GL = (G_REM, G_BACK, G_COV, G_LES) if near else (G_REMF, G_BACKF, G_COVF, G_LESF)
    gold = GOLD if near else GOLDF
    pre = 'w' + side

    def place(u, tip, off=2.0, k=0):
        """Une plume attachée au paramètre u, dont la pointe au repos est `tip` : sa racine et sa direction posées."""
        b0, _ = along(path0, u)
        d0 = math.degrees(math.atan2(tip[1] - b0[1], tip[0] - b0[0]))
        L = math.dist(b0, tip)
        r = rot_at(u, us, r0, r1, r2)
        b1, _ = along(path, u)
        # les plumes près du corps pendent : elles suivent moins la rotation de l'épaule (l'aile s'ouvre en éventail)
        kk = 0.42 + 0.58 * max(0.0, min(1.0, (u - 0.15) / 0.42))
        ang = d0 + r0 * kk + (r - r0)
        root = (b1[0] + off * math.cos(math.radians(ang)), b1[1] + off * math.sin(math.radians(ang)))
        # l'ondulation de flamme : une vague qui court vers le bout de l'aile
        wave = amp * 2.2 * math.sin(ph - 0.55 * k)
        return root, ang + wave * sg, L - off, wave

    n = len(tips0)
    ur = [0.17 + (0.965 - 0.17) * i / (n - 1) for i in range(n)]
    # -- le rang intercalé (derrière) : une seule forme sombre, entre les rémiges --
    backs = []
    for i in range(n - 1):
        u = (ur[i] + ur[i + 1]) / 2
        tip = lerp(tips0[i], tips0[i + 1], 0.5)
        b0, _ = along(path0, u)
        tip = lerp(b0, tip, 0.93)
        root, ang, L, wv = place(u, tip, 2.0, i + 0.5)
        backs.append(plume(root, ang, L, 6.4, curl=sg * (16 + 6 * wv + 14 * drag)))
    nm = pre + 'back'
    b0, b1 = backs[0].bbox()[:2], backs[-1].bbox()[2:]
    fig.part(nm, fuse(backs, close=0.3, step=0.6, t=0.7), CRIM,
             grad=(bones[0][0], bones[0][1], tips_center(tips0, bones0, bones)[0], tips_center(tips0, bones0, bones)[1], GB),
             cel=0, rim=0.5, cast=0, ink=FINK)
    names.append(nm)
    # -- les rémiges : du corps vers le bout (chacune pose son ombre sur la suivante, plus bas) --
    for i in range(n):
        u = ur[i]
        root, ang, L, wv = place(u, tips0[i], 2.0, i)
        wdt = (7.0 if i < n - 4 else 6.2) * (1 if near else 0.92)
        curl = sg * (14 + 5 * wv + 16 * drag + (6 if i % 3 == 1 else 0))
        sh = plume(root, ang, L, wdt, curl=curl)
        tip = sh_tip(root, ang, L, curl)
        nm = '%sr%d' % (pre, i)
        fig.part(nm, sh, FEA, grad=(root[0], root[1], tip[0], tip[1], G1), cel=0, rim=0.45, cast=1.1, ink=FINK,
                 cast_on=[x for x in names],
                 details=[(under(sh, 0.6 * sg, -2.2), ('lin', root[0], root[1], tip[0], tip[1],
                                                      [(0, '#5a0e2e', 0.5), (0.6, '#a8202c', 0.45), (1, '#e0501e', 0.3)]), 1)])
        names.append(nm)
    # -- les grandes couvertures orangées (écailles), sur les racines des rémiges --
    nc = 10
    for i in range(nc):
        u = 0.15 + (0.9 - 0.15) * i / (nc - 1)
        j = min(n - 1, int(round((u - ur[0]) / (ur[-1] - ur[0]) * (n - 1))))
        b0, _ = along(path0, u)
        full = math.dist(b0, tips0[j])
        tip = lerp(b0, tips0[j], (0.42 if i < 6 else 0.5) * (1 if near else 0.95))
        root, ang, L, wv = place(u, tip, 0.8, i * 1.4)
        wdt = 7.4 - 2.4 * i / (nc - 1)
        sh = plume(root, ang, L, wdt, curl=sg * (10 + 10 * drag), kind='cover')
        tp = sh_tip(root, ang, L, sg * 10)
        nm = '%sc%d' % (pre, i)
        fig.part(nm, sh, FEA, grad=(root[0], root[1], tp[0], tp[1], GC), cel=0, rim=0.45, cast=1.0, ink=FINK,
                 cast_on=[x for x in names],
                 details=[(under(sh, 0.5 * sg, -1.8), ('lin', root[0], root[1], tp[0], tp[1],
                                                      [(0, '#8a1a30', 0.45), (1, '#d2401e', 0.3)]), 1)])
        names.append(nm)
    # -- les petites couvertures d'or, le long du bord d'attaque --
    nl = 10
    for i in range(nl):
        u = 0.15 + (0.93 - 0.15) * i / (nl - 1)
        j = min(n - 1, int(round((u - ur[0]) / (ur[-1] - ur[0]) * (n - 1))))
        b0, _ = along(path0, u)
        L0 = 7.2 - 2.6 * i / (nl - 1)
        tip = lerp(b0, tips0[j], L0 / math.dist(b0, tips0[j]))
        root, ang, L, wv = place(u, tip, 1.0, i * 1.2)
        wdt = 4.8 - 2.0 * i / (nl - 1)
        sh = plume(root, ang, L + 0.6, wdt, curl=sg * 8, kind='cover')
        tp = sh_tip(root, ang, L, sg * 8)
        nm = '%sl%d' % (pre, i)
        fig.part(nm, sh, GOLD, grad=(root[0], root[1], tp[0], tp[1], GL), cel=0, rim=0.5, cast=0.9, ink=FINK,
                 cast_on=[x for x in names],
                 details=[(under(sh, 0.4 * sg, -1.5), ('lin', root[0], root[1], tp[0], tp[1],
                                                      [(0, '#b0581c', 0.45), (1, '#e0901e', 0.3)]), 1)])
        names.append(nm)
    # -- le bord d'attaque doré (le bras, de l'épaule au bout de la main), d'un seul tenant --
    c = crpath([lerp(bones[0], bones[1], 0.55)] + bones[1:], 30)
    ws = [5.0 - 3.5 * (i / 30) ** 1.1 for i in range(31)]
    band = limb(c, ws)
    nm = pre + 'edge'
    det = [(ribbon([(p[0] + 0.5 * sg - 0.2, p[1] - 0.9) for p in c[2:28:3]], [0.1] + [0.9] * 7 + [0.1]), gold.hi, 0.75)]
    fig.part(nm, band, gold, grad=(c[0][0] + 6 * sg, c[0][1] - 18, c[-1][0], c[-1][1] + 10,
                                   [(0, gold.light), (0.5, gold.base), (1, gold.light)]),
             cel=1.0, rim=0.6, cast=1.1, ink=FINK, details=det, cast_on=[x for x in names])
    names.append(nm)
    if not near:
        for p in fig.parts:
            if p.name in names:
                p.details.append((p.shape, '#2a0828', 0.16))
    return names, bones, path


def tips_center(tips0, bones0, bones):
    return bones[-1]


def sh_tip(root, ang, L, curl, n=14):
    x, y = root
    for i in range(1, n + 1):
        t = (i - 0.5) / n
        a = math.radians(ang + curl * t * t)
        x += L / n * math.cos(a)
        y += L / n * math.sin(a)
    return (x, y)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']

    # ---- le squelette : une matrice par groupe de morceaux ----
    LIFT = mT(0, -P['lift'])
    dyb = P['crouch'] * 0.85
    BODY = mchain(LIFT, mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 1.1, 71, 80))   # le haut du corps (depuis la taille)
    UC = mchain(BODY, mT(0, -0.55 * br))                                            # ce qui monte avec la poitrine
    TOR = mchain(BODY, mS(1, 1 + 0.014 * br, 71, 72))                               # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], 76, 46), mS(1.16, 1.16, 77, 47.5))  # tête un peu plus grande
    SKT = mchain(BODY, mskx(-0.05 * P['sk'], 73))

    # ---- l'aile lointaine (derrière tout) ----
    SF = mapp(UC, FAR_BONES[0])
    far_names, far_bones, _ = wing(fig, 'f', P, SF)

    # ---- la queue : longues plumes en éventail vers la gauche, la plus basse touche le sol ----
    tail_names = tail(fig, P, BODY)

    # ---- les pattes (elles restent au sol) : tarse écailleux et doigts d'un seul tenant, serres sombres ----
    leg_names = legs(fig, P, BODY, LIFT)

    # ---- les mèches de plumes de l'arrière de la tête et de la nuque (derrière le buste) ----
    hair_back = hair_locks(fig, P)

    # ---- la jupe : deux rangs de plumes qui naissent de la ceinture ----
    skirt_names = skirt(fig, P)

    # ---- le buste (cou, épaules, poitrine), d'un seul tenant avec le départ de l'aile proche ----
    SN = mapp(UC, NEAR_BONES[0])
    near_r0 = P['wn'] * -1 + P['lean'] * 1.1
    nb = bone_pose(NEAR_BONES, SN, near_r0, P['fold'] * 0.5, P['fold'])
    stub_end = lerp(nb[0], nb[1], 0.62)
    torso0 = [(71.6, 41.5), (71.0, 47.0), (66.4, 49.6), (61.2, 50.8), (57.6, 52.0), (56.6, 55.2), (58.4, 58.0),
              (60.6, 62.4), (62.8, 67.4), (63.6, 71.0), (63.8, 74.0), (78.8, 74.0), (78.6, 70.6), (80.0, 66.2),
              (82.2, 61.0), (84.4, 57.4), (87.4, 55.4), (88.0, 52.6), (85.6, 50.8), (81.4, 48.8), (79.6, 46.0),
              (79.6, 41.5)]
    torso = sm([mapp(TOR, p) for p in torso0], t=0.95)
    stub = limb([lerp(nb[0], nb[1], -0.05), lerp(nb[0], nb[1], 0.3), stub_end], [7.0, 6.4, 5.8])
    torso_f = fuse([torso, stub], close=0.9, step=0.7, t=0.9)
    T_ = lambda p: mapp(TOR, p)
    tdet = [(sm([T_((71.4, 46.0)), T_((74.0, 47.2)), T_((76.6, 48.6)), T_((74.2, 49.8)), T_((71.2, 48.6))]), SKIN.shadow, 0.35),
            (ribbon([T_((64.8, 52.4)), T_((68.6, 53.2)), T_((72.6, 52.8))], [0.1, 0.8, 0.1]), SKIN.shadow, 0.45),   # clavicule
            (ribbon([T_((78.6, 52.6)), T_((81.6, 53.0)), T_((84.4, 52.2))], [0.1, 0.6, 0.1]), SKIN.shadow, 0.35),
            (ellipse(*T_((81.8, 54.2)), 2.6, 1.1, -10), SKIN.hi, 0.55),
            (ellipse(*T_((62.4, 53.0)), 2.2, 1.0, -20), SKIN.hi, 0.35)]
    fig.part('torso', torso_f, SKIN, grad=(86, 46, 58, 70, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.1, rim=0.5, cast=1.0, details=tdet)

    # ---- les plumes de flanc, sous l'aile proche (une touffe cramoisie, en retrait), pointes vers la hanche ;
    # derrière le plastron ----
    ph, amp = P['ph'], P['amp']
    sw = 0.5 * amp * math.sin(ph - 1.6)
    fl0 = [(53.0, 53.6), (57.2, 53.4), (60.6, 56.4), (62.4, 61.4), (63.6, 66.4), (64.0, 70.6), (62.6, 75.6 + sw),
           (60.8, 72.6), (58.6, 77.0 + sw), (56.8, 72.8), (54.2, 76.2 + sw), (53.4, 70.0), (52.6, 61.4)]
    flk = sm([T_(p) for p in fl0], sharp=(6, 7, 8, 9, 10), t=0.9)
    fdet = [(ribbon([T_((56.2, 56.4)), T_((57.6, 64.0)), T_((60.6, 72.4))], [0.1, 0.9, 0.1]), '#5a0e2e', 0.45),
            (ribbon([T_((58.8, 57.0)), T_((60.6, 63.6)), T_((62.4, 70.6))], [0.1, 0.7, 0.1]), '#ff9a3a', 0.35),
            (ribbon([T_((54.4, 60.0)), T_((55.0, 67.0)), T_((56.8, 72.4))], [0.1, 0.8, 0.1]), '#5a0e2e', 0.4)]
    fig.part('flank', flk, CRIM, grad=(60, 54, 56, 77, [(0, '#7a1636'), (0.5, '#b8282e'), (1, '#e85a28')]),
             cel=1.0, rim=0.3, cast=1.0, ink=FINK, details=fdet)

    # ---- le plastron de plumes blanches (bustier) ----
    pl0 = [(58.8, 58.4), (61.6, 56.6), (65.2, 56.4), (68.4, 57.8), (70.8, 60.4), (73.4, 57.6), (76.8, 56.0),
           (80.4, 56.2), (83.6, 57.8), (82.0, 62.0), (80.0, 66.6), (78.9, 71.4), (63.6, 71.6), (62.6, 66.8), (60.6, 62.4)]
    plast = sm([T_(p) for p in pl0], sharp=(4,), t=0.9)
    pdet = []
    # les écailles de plumes : deux rangs de bords arrondis (ombre lilas sous chaque bord), irréguliers
    for row, (y0, xs) in enumerate(((62.2, [(61.4, 65.2), (64.8, 68.6), (72.8, 76.6), (76.2, 79.8)]),
                                    (66.4, [(62.8, 66.6), (66.4, 70.4), (70.2, 74.0), (73.8, 77.8)]))):
        for a, b in xs:
            m = (a + b) / 2
            yy = y0 + 0.2 * math.sin(a * 1.7)
            arc = [(a, yy - 0.3), (a + 0.25 * (b - a), yy + 0.6), (m, yy + 0.9), (b - 0.25 * (b - a), yy + 0.6), (b, yy - 0.3)]
            pdet.append((ribbon([T_(p) for p in arc], [0.1, 0.6, 0.8, 0.6, 0.1]), WHITE.shadow, 0.4))
            pdet.append((ribbon([T_((p[0], p[1] - 0.8)) for p in arc[1:4]], [0.1, 0.5, 0.1]), WHITE.hi, 0.7))
    pdet += [(sm([T_((62.4, 66.0)), T_((70.6, 67.6)), T_((79.6, 66.0)), T_((78.9, 71.6)), T_((63.6, 71.8))]), WHITE.shadow, 0.35),
             (ribbon([T_((70.8, 60.6)), T_((70.9, 63.6)), T_((70.6, 66.0))], [0.1, 0.7, 0.1]), WHITE.shadow, 0.5),
             (ellipse(*T_((77.6, 59.0)), 2.6, 1.0, -12), WHITE.hi, 0.9),
             (ellipse(*T_((65.8, 59.4)), 2.0, 0.9, -12), WHITE.hi, 0.6)]
    fig.part('plast', plast, WHITE, grad=(82, 56, 62, 72, [(0, WHITE.light), (0.55, WHITE.base), (1, '#dcc4d4')]),
             cel=1.0, rim=0.5, cast=1.0, cast_on=['torso'], details=pdet)

    # ---- le torque d'or (fait le tour du cou) et son pendentif de rubis ----
    tq0 = [(70.8, 47.2), (73.2, 48.6), (76.2, 49.2), (79.8, 47.8), (80.2, 49.6), (76.4, 51.2), (73.0, 50.8), (70.4, 49.2)]
    fig.part('torque', sm([T_(p) for p in tq0], t=0.9), GOLD, cel=0.6, rim=0.5, cast=0.8, cast_on=['torso'],
             details=[(ribbon([T_((71.6, 48.0)), T_((75.6, 49.4)), T_((79.4, 48.4))], [0.1, 0.5, 0.1]), GOLD.hi, 0.85)])
    pend = sm([T_((75.2, 50.8)), T_((76.8, 51.6)), T_((76.6, 53.6)), T_((75.6, 55.0)), T_((74.6, 53.4)), T_((74.4, 51.6))], sharp=(3,), t=0.9)
    fig.part('pend', pend, RUBY, cel=0.5, rim=0.4, cast=0.7, cast_on=['torso', 'plast'],
             details=[(ellipse(*T_((76.0, 52.2)), 0.5, 0.65), '#ffe2d8', 0.9)])

    # ---- la ceinture d'or et son médaillon au rubis ----
    bl0 = [(63.0, 70.4), (67.0, 71.0), (71.0, 71.2), (75.0, 70.8), (79.0, 70.2), (79.2, 73.4), (75.0, 74.2), (71.0, 74.4),
           (67.0, 74.2), (63.2, 73.6)]
    fig.part('belt', sm([T_(p) for p in bl0], t=0.9), GOLD, cel=0.8, rim=0.5, cast=1.0,
             details=[(ribbon([T_((63.6, 71.0)), T_((71.0, 71.8)), T_((78.6, 70.8))], [0.1, 0.5, 0.1]), GOLD.hi, 0.85),
                      (ribbon([T_((63.6, 73.2)), T_((71.0, 73.9)), T_((78.6, 73.0))], [0.1, 0.5, 0.1]), GOLD.shadow, 0.6)])
    mc = T_((71.6, 72.6))
    fig.part('medal', ellipse(mc[0], mc[1], 2.5, 2.4), GOLD, cel=0.6, rim=0.5, cast=0.8,
             details=[(ellipse(mc[0] - 0.05, mc[1] + 0.05, 1.35, 1.35), RUBY.deep, 1),
                      (ellipse(mc[0], mc[1], 1.1, 1.1), ('rad', mc[0] + 0.3, mc[1] - 0.3, 1.2, 1.2, [(0, RUBY.light), (0.6, RUBY.base), (1, RUBY.shadow)]), 1),
                      (ellipse(mc[0] + 0.35, mc[1] - 0.35, 0.35, 0.3), '#ffe8e0', 0.95)])

    # ---- l'aile proche ----
    near_names, near_bones, near_path = wing(fig, 'n', P, SN)
    # le bracelet d'or au rubis, à la naissance de l'aile (il fait le tour du bras : peint sur toute sa largeur)
    a, b = lerp(nb[0], nb[1], 0.5), lerp(nb[0], nb[1], 0.72)
    d = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    Lb = math.dist(a, b)
    from atelier import xf
    brac = xf(rpoly([(0, -3.3), (Lb, -3.1), (Lb, 3.1), (0, 3.3)], 1.0), a[0], a[1], d)
    mid = lerp(a, b, 0.5)
    nrm = rot((0, -1), d)
    gem = (mid[0] + nrm[0] * 0.2 * 0, mid[1])
    fig.part('brac', brac, GOLD, cel=0.7, rim=0.5, cast=1.0,
             details=[(xf(ribbon([(0.4, -2.6), (Lb * 0.5, -2.9), (Lb - 0.4, -2.6)], [0.1, 0.5, 0.1]), a[0], a[1], d), GOLD.hi, 0.7),
                      (ellipse(gem[0], gem[1], 1.25, 1.25), RUBY.deep, 1),
                      (ellipse(gem[0], gem[1], 0.95, 0.95), ('rad', gem[0] + 0.3, gem[1] - 0.3, 1.0, 1.0, [(0, RUBY.light), (0.6, RUBY.base), (1, RUBY.shadow)]), 1),
                      (ellipse(gem[0] + 0.3, gem[1] - 0.3, 0.3, 0.25), '#ffe8e0', 0.95)])

    # ---- la tête ----
    head_names = head(fig, P)

    # ---- elle s'embrase d'un feu doré bienfaisant (attaque spéciale) : toutes ses plumes montent vers l'or ----
    if P['fire'] > 0:
        for p in fig.parts:
            x0, y0, x1, y1 = p.shape.bbox()
            p.details.append((p.shape, ('lin', x1, y0, x0, y1, [(0, '#fff6c0'), (0.5, '#ffd858'), (1, '#ffa830')]),
                              min(0.55, 0.16 * P['fire'])))
            p.rim = max(p.rim, 0.35 + 0.2 * P['fire'])

    # ---- chaque groupe prend sa pose ----
    fig.pose(head_names + hair_back, HEAD)
    fig.pose(skirt_names, SKT)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(P=P, BODY=BODY, UC=UC, HEAD=HEAD, head=mapp(HEAD, (78, 34)), chest=T_((71, 64)), waist=T_((71, 72)),
                   tipN=near_bones[-1], tipF=far_bones[-1], wristN=near_bones[2], wristF=far_bones[2],
                   SN=SN, SF=SF, near_bones=near_bones, far_bones=far_bones, feet=mapp(LIFT, FEET),
                   parts=[p.name for p in fig.parts])
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def tail(fig, P, BODY):
    """La queue : longues plumes larges en éventail vers la gauche (courbes en S, pointes relevées), sous la jupe et
    derrière les pattes ; la plus basse repose au sol. Du fond vers le devant, de la plus basse à la plus haute."""
    names = []
    q = P['q']
    ph, amp = P['ph'], P['amp']
    T = [
        # (nom, p0, p1, p2, p3, largeur, posée au sol)
        ('tb0', (59.0, 84.6), (49.0, 93.0), (36.0, 104.0), (22.6, 110.8), 8.6, False),
        ('tb1', (59.0, 83.4), (47.6, 88.4), (32.4, 95.0), (17.4, 99.0), 8.6, False),
        ('tb2', (59.4, 82.2), (48.0, 84.6), (34.0, 88.6), (21.0, 91.8), 8.0, False),
        ('tf0', (59.6, 85.4), (50.0, 95.0), (38.4, 108.0), (26.6, 116.2), 10.0, True),
        ('tf1', (59.2, 84.4), (48.0, 91.4), (33.6, 101.0), (19.8, 105.2), 10.4, False),
        ('tf2', (59.2, 83.2), (47.4, 87.4), (32.4, 93.6), (18.6, 97.0), 10.0, False),
        ('tf3', (59.6, 82.0), (49.0, 82.6), (37.0, 85.4), (25.6, 88.0), 8.6, False),
    ]
    out = []
    for i, (nm, p0, p1, p2, p3, w, ground) in enumerate(T):
        R0 = mapp(BODY, p0)
        dx, dy = R0[0] - p0[0], R0[1] - p0[1]
        k = i % 4
        wv = amp * math.sin(ph - 0.7 * k - 0.4)
        if ground:
            # elle repose au sol : la pointe reste posée, le milieu se soulève à peine
            q1, q2, q3 = (p1[0] + dx, p1[1] + dy), (p2[0] + 0.4 * dx, p2[1] + 0.4 * dy - 0.3 * abs(q)), p3
        else:
            sw = 1.6 * q + 1.2 * wv
            q1 = rotp((p1[0] + dx, p1[1] + dy), sw * 0.5, R0)
            q2 = rotp((p2[0] + dx, p2[1] + dy), sw, R0)
            q3 = rotp((p3[0] + dx, p3[1] + dy), sw * 1.3, R0)
            q3 = (q3[0] + 0.6 * wv, q3[1] - 0.8 * wv)
        sh = lock(R0, q1, q2, q3, w, bulge=0.22)
        back = nm.startswith('tb')
        G = G_TAILB if back else G_TAIL
        fig.part(nm, sh, CRIM if back else FEA, grad=(R0[0], R0[1], q3[0], q3[1], G), cel=0, rim=0.45, cast=1.2, ink=FINK,
                 cast_on=list(names),
                 details=[(under(sh, 0.8, -2.8), ('lin', R0[0], R0[1], q3[0], q3[1], [(0, '#4a0c2a', 0.5), (0.6, '#a01e2c', 0.45), (1, '#d8481e', 0.3)]), 1)])
        names.append(nm)
        out.append(nm)
    return out


def bird_leg(top, ankle, toes, w0=5.2, w1=4.0):
    """Une patte d'oiseau d'une seule forme : le tarse (du haut caché sous la jupe à la cheville) et les doigts posés
    au sol, réunis sans couture. toes : [(points du doigt, largeurs)]."""
    tars = limb([top, lerp(top, ankle, 0.5), ankle], [w0, (w0 + w1) / 2, w1])
    shapes = [tars] + [limb(pts, ws) for pts, ws in toes]
    shapes.append(ellipse(ankle[0], ankle[1] + 1.4, 3.0, 2.2))
    return fuse(shapes, close=0.9, step=0.6, t=0.85)


def legs(fig, P, BODY, LIFT):
    names = []
    up = P['legs_up']
    for side in ('f', 'n'):
        if side == 'f':
            top = mapp(BODY, (80.2, 84.0))
            ank0 = (80.6, 110.2)
            toes0 = [([(80.6, 111.0), (86.0, 112.4), (91.0, 113.4), (94.6, 114.4)], [3.6, 3.3, 2.9, 2.5]),
                     ([(80.0, 111.6), (83.6, 113.8), (88.0, 115.0)], [3.4, 3.1, 2.7]),
                     ([(79.6, 111.4), (76.6, 113.6), (74.4, 114.6)], [3.2, 2.8, 2.4])]
            claws0 = [((94.6, 114.4), 1, 1.0), ((88.0, 115.0), 1, 0.9), ((74.4, 114.6), -1, 0.85)]
            mat_dark = 0.1
        else:
            top = mapp(BODY, (56.6, 85.0))
            ank0 = (55.8, 110.8)
            toes0 = [([(56.2, 111.6), (60.4, 113.0), (64.6, 114.4)], [3.8, 3.4, 2.8]),
                     ([(55.6, 112.2), (58.0, 114.4), (60.6, 115.2)], [3.4, 3.1, 2.7]),
                     ([(55.2, 111.8), (50.6, 113.4), (46.6, 114.6)], [3.4, 3.0, 2.5])]
            claws0 = [((64.6, 114.4), 1, 1.0), ((60.6, 115.2), 1, 0.85), ((46.6, 114.6), -1, 0.95)]
        # en vol (lift) les pattes pendent : les doigts se replient un peu vers le bas
        F = lambda p: mapp(LIFT, p)
        ank = F(ank0)
        toes = []
        claws = []
        for (pts, ws), (cp, dr, cs) in zip(toes0, claws0):
            q = [F(p) for p in pts]
            if up:
                q = [rotp(p, 28 * up * (1 if p[0] > ank0[0] else -1), ank) for p in q]
            toes.append((q, ws))
            cq = F(cp)
            if up:
                cq = rotp(cq, 28 * up * (1 if cp[0] > ank0[0] else -1), ank)
            claws.append((cq, dr, cs, q[-2]))
        leg = bird_leg(top, ank, toes)
        nm = 'leg' + side
        # les grandes plaques du tarse (écailles) : arcs clairs, de moins en moins visibles vers le bas
        det = []
        for k in range(4):
            t = 0.25 + 0.18 * k
            c = lerp(top, ank, t)
            det.append((ribbon([(c[0] - 2.0, c[1] - 0.3), (c[0] + 0.2, c[1] + 0.6), (c[0] + 2.2, c[1] - 0.2)], [0.1, 0.6, 0.1]), LEG.shadow, 0.5))
            det.append((ribbon([(c[0] - 1.6, c[1] - 1.0), (c[0] + 0.2, c[1] - 0.2), (c[0] + 1.8, c[1] - 0.9)], [0.1, 0.45, 0.1]), LEG.hi, 0.55))
        det.append((ribbon([(ank[0] + 1.2, ank[1] - 18), (ank[0] + 1.6, ank[1] - 8), (ank[0] + 1.2, ank[1])], [0.1, 0.9, 0.1]), LEG.hi, 0.6))
        if side == 'f':
            det.append((leg, '#4a1030', 0.22))
        fig.part(nm, leg, LEG, grad=(ank[0] + 4, top[1], ank[0] - 4, ank[1] + 4, [(0, LEG.light), (0.5, LEG.base), (1, LEG.shadow)]),
                 cel=1.0, rim=0.6, cast=1.0, details=det)
        names.append(nm)
        # la cuisse emplumée (la « culotte » de plumes) : du bord de la jupe jusqu'au haut du tarse, pointes en bas
        cx = 56.4 if side == 'n' else 80.4
        th0 = [(cx - 4.2, 83.4), (cx + 4.0, 83.4), (cx + 3.8, 89.0), (cx + 3.0, 95.0), (cx + 1.6, 92.4), (cx + 0.2, 97.2),
               (cx - 1.2, 92.6), (cx - 2.8, 95.6), (cx - 3.6, 90.0)]
        sway = 0.4 * P['amp'] * math.sin(P['ph'] - (2.0 if side == 'n' else 2.6))
        th0 = [(x + (sway if y > 91 else 0), y) for x, y in th0]
        thigh = sm([mapp(BODY, p) for p in th0], sharp=(3, 4, 5, 6, 7), t=0.9)
        G = G_SKF if side == 'n' else G_SKB
        tt = mapp(BODY, (cx, 83.4))
        fig.part('thigh' + side, thigh, FEA, grad=(tt[0] + 3, tt[1], tt[0] - 2, tt[1] + 14, G), cel=0.9, rim=0.4, cast=1.0,
                 ink=FINK, cast_on=[nm],
                 details=[(ribbon([mapp(BODY, (cx - 1.4, 85.0)), mapp(BODY, (cx - 0.8, 89.6)), mapp(BODY, (cx - 1.2, 93.0))], [0.1, 0.7, 0.1]), '#6a1236', 0.45),
                          (ribbon([mapp(BODY, (cx + 1.8, 85.0)), mapp(BODY, (cx + 2.0, 89.6)), mapp(BODY, (cx + 1.6, 92.4))], [0.1, 0.6, 0.1]), '#ffd060', 0.4)])
        names.append('thigh' + side)
        # les serres : crochets sombres au bout des doigts
        for i, (cp, dr, cs, prev) in enumerate(claws):
            a = math.atan2(cp[1] - prev[1], cp[0] - prev[0])
            ux, uy = math.cos(a), math.sin(a)
            nx, ny = -uy, ux
            s = 1.55 * cs
            base1 = (cp[0] - nx * s * 0.9 - ux * 0.6, cp[1] - ny * s * 0.9 - uy * 0.6)
            base2 = (cp[0] + nx * s * 0.9 - ux * 0.6, cp[1] + ny * s * 0.9 - uy * 0.6)
            tipc = (cp[0] + ux * s * 2.2, cp[1] + uy * s * 2.2 + 1.1 * s)
            tipc = (tipc[0], min(tipc[1], GRD + 0.4 - P['lift']) if not up else tipc[1])
            hook = (cp[0] + ux * s * 1.6, cp[1] + uy * s * 1.6 - 0.6 * s)
            sh = sm([base1, hook, tipc, (cp[0] + ux * s * 0.8, cp[1] + uy * s * 0.8 + 0.6 * s), base2], sharp=(2,), t=0.8)
            nm = 'claw%s%d' % (side, i)
            fig.part(nm, sh, TALON, cel=0.5, rim=0.4, cast=0.6,
                     details=[(ellipse(hook[0], hook[1] + 0.3, 0.6, 0.3, math.degrees(a)), TALON.glint, 0.8)])
            names.append(nm)
    return names


def skirt(fig, P):
    """La jupe de plumes : elle naît de la ceinture, centrée sous la taille, et s'évase doucement."""
    names = []
    ph, amp = P['ph'], P['amp']
    # rang du fond (cramoisi) puis rang de devant (rouge aux pointes jaunes) : (racine, pointe, largeur)
    back = [((64.6, 74.0), (55.6, 87.6), 7.0), ((79.0, 73.8), (86.6, 86.6), 6.8), ((68.0, 74.6), (62.0, 89.0), 7.4),
            ((75.6, 74.6), (80.6, 89.4), 7.4)]
    front = [((65.2, 74.4), (59.0, 86.0), 7.2), ((78.4, 74.2), (83.4, 85.4), 6.8), ((68.6, 74.8), (65.6, 89.4), 7.4),
             ((75.2, 74.8), (77.6, 89.8), 7.2), ((71.8, 75.0), (71.6, 90.6), 7.6)]
    for rank, lst, G, mat in (('sbk', back, G_SKB, CRIM), ('sfr', front, G_SKF, FEA)):
        for i, (r_, t_, w) in enumerate(lst):
            d0 = math.degrees(math.atan2(t_[1] - r_[1], t_[0] - r_[0]))
            L = math.dist(r_, t_)
            sw = amp * 1.8 * math.sin(ph - 0.8 * i - (1.2 if rank == 'sfr' else 0.6))
            ang = d0 + sw
            curl = 10 if t_[0] < 71 else -10
            sh = plume(r_, ang, L, w, curl=curl)
            tp = sh_tip(r_, ang, L, curl)
            nm = '%s%d' % (rank, i)
            fig.part(nm, sh, mat, grad=(r_[0], r_[1], tp[0], tp[1], G), cel=0, rim=0.45, cast=1.0, ink=FINK,
                     details=[(under(sh, 0.6, -2.2), ('lin', r_[0], r_[1], tp[0], tp[1], [(0, '#3a0c2a', 0.5), (0.6, '#8a1a30', 0.4), (1, '#c8381e', 0.3)]), 1)])
            names.append(nm)
    return names


def hair_locks(fig, P):
    """Les longues mèches de plumes de l'arrière de la tête, couchées vers l'arrière (une courbe en S, la pointe qui
    se relève comme une flamme ; longueurs et écarts inégaux, jamais des rayons), et les plumes de la nuque, derrière
    le buste : de la plus basse à la plus haute (chacune pose son ombre sur celle du dessous)."""
    names = []
    ph, amp = P['ph'], P['amp']
    LOCKS = [
        # (nom, p0 racine, p1, p2, p3 pointe, largeur)
        ('hn1', (69.6, 45.0), (68.6, 49.4), (66.6, 52.4), (63.4, 54.4), 5.6),
        ('hn0', (66.4, 44.0), (64.4, 48.6), (61.4, 51.6), (57.2, 52.0), 6.6),
        ('h6', (63.4, 42.6), (58.4, 46.4), (52.6, 47.6), (48.4, 43.6), 7.4),
        ('h5', (61.6, 37.4), (55.2, 39.8), (49.6, 39.6), (45.8, 34.0), 8.2),
        ('h4', (61.2, 31.4), (54.2, 32.4), (48.4, 31.2), (44.6, 24.6), 8.8),
        ('h3', (62.2, 25.4), (55.4, 25.2), (49.8, 23.0), (47.0, 15.2), 9.0),
        ('h2', (65.0, 20.4), (59.6, 18.8), (54.4, 15.6), (52.4, 7.4), 8.6),
        ('h1', (69.4, 17.0), (65.4, 12.4), (60.4, 9.6), (58.4, 1.6), 7.8),
    ]
    for i, (nm, p0, p1, p2, p3, w) in enumerate(LOCKS):
        k = 0.55 + 0.1 * i
        wv = math.sin(ph - 0.8 * i)
        p2 = (p2[0] + 0.5 * k * math.sin(2 * ph + 1.0 - 0.8 * i), p2[1] + 0.8 * k * wv)
        p3 = (p3[0] + 1.0 * k * math.sin(ph + 0.8 - 0.8 * i), p3[1] + 1.1 * k * math.cos(ph - 0.8 * i))
        p2 = lerp(lerp(p0, p2, 1.0), p2, amp) if amp != 1 else p2
        sh = lock(p0, p1, p2, p3, w, bulge=0.3)
        G = G_HAIRB if nm.startswith('hn') else G_HAIR
        fig.part(nm, sh, FEA, grad=(p0[0], p0[1], p3[0], p3[1], G), cel=0, rim=0.5, cast=1.2, ink=FINK,
                 cast_on=list(names),
                 details=[(under(sh, 0.8, -2.6), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, '#5a0e2e', 0.5), (0.5, '#b0242c', 0.45), (1, '#e0501e', 0.35)]), 1)])
        names.append(nm)
    return names


def head(fig, P):
    """Le visage fin de femme, la calotte de plumes, le diadème ; rend la liste des morceaux (posés avec la tête)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- le visage ----
    face = sm([(67.4, 31.0), (68.8, 26.4), (72.6, 23.6), (78.4, 23.0), (82.0, 24.8), (83.6, 28.2), (83.5, 31.2),
               (83.9, 33.6), (85.2, 36.0), (85.8, 37.3), (85.0, 38.3), (84.0, 38.8), (84.1, 39.6), (84.4, 40.5),
               (83.8, 41.3), (84.0, 42.4), (83.5, 43.9), (82.7, 45.4), (81.4, 46.6), (79.2, 47.1), (76.6, 46.1),
               (73.4, 43.8), (70.6, 40.8), (68.4, 36.8)], sharp=(9,), t=0.95)
    fd = []
    # les plans du visage : la joue proche et la tempe dans une ombre douce, le plan de face éclairé
    fd += [(sm([(68.6, 31.4), (70.8, 36.2), (73.2, 40.4), (76.6, 44.2), (79.4, 46.8), (76.6, 46.1), (73.4, 43.8), (70.6, 40.8), (68.4, 36.8)]), SKIN.shadow, 0.5),
           (sm([(78.6, 24.2), (82.0, 25.2), (83.4, 28.6), (83.2, 32.2), (81.0, 30.4), (79.0, 27.4)]), SKIN.hi, 0.5),
           (ellipse(82.4, 39.6, 1.5, 1.1), SKIN.hi, 0.3),
           (ellipse(74.0, 39.0, 2.6, 1.4, 12), '#f08c94', 0.26),          # la pommette proche (un peu de rose)
           (ellipse(82.6, 38.4, 1.1, 0.9), '#f08c94', 0.26)]
    # l'ombre sous le menton et la mâchoire
    fd += [(sm([(77.4, 45.4), (80.6, 46.0), (82.7, 45.0), (81.4, 46.6), (79.2, 47.1), (76.6, 46.1)]), SKIN.shadow, 0.5)]
    blink = P['blink'] > 0.5
    # les sourcils fins, arqués, qui descendent vers le nez (fière, décidée)
    fd += [(sm([(69.0, 31.6), (70.4, 30.4), (72.6, 29.8), (74.6, 30.6), (75.6, 31.6), (74.4, 31.2), (72.6, 30.6), (70.6, 31.0), (69.3, 32.0)],
               sharp=(0, 4), t=0.8), LASH, 1),
           (sm([(78.2, 31.8), (79.4, 30.8), (81.2, 30.2), (82.8, 30.4), (82.9, 30.9), (81.2, 30.8), (79.6, 31.3), (78.4, 32.2)],
               sharp=(0, 4), t=0.8), LASH, 0.95)]
    # les yeux en amande : (amande, trait des cils étiré vers la tempe, centre de l'iris, rayon)
    eyes = (
        (sm([(69.6, 33.9), (71.2, 32.6), (73.6, 32.5), (75.6, 34.1), (73.8, 35.6), (71.2, 35.4)], sharp=(0, 3), t=0.9),
         sm([(75.9, 34.1), (74.4, 32.4), (71.6, 31.9), (69.4, 32.6), (68.0, 32.5), (68.9, 33.4), (69.8, 34.2), (71.6, 33.1), (74.0, 33.0)],
            sharp=(0, 4), t=0.85),
         (73.0, 34.1), 1.5),
        (sm([(79.3, 34.3), (80.3, 32.9), (81.9, 32.6), (83.0, 33.4), (82.1, 34.6), (80.3, 34.9)], sharp=(0, 3), t=0.9),
         sm([(79.0, 34.0), (80.2, 32.3), (82.0, 31.9), (83.1, 32.8), (83.6, 32.3), (83.4, 33.4), (82.9, 33.9), (81.8, 33.0), (80.3, 33.2)],
            sharp=(0, 4), t=0.85),
         (81.3, 33.8), 1.1),
    )
    for almond, liner, (ix, iy), ir in eyes:
        if blink:
            fd += [(almond.scale(1.04, 1.1, ix, iy), SKIN.base, 1),
                   (ribbon([(almond_pt(almond, 0)[0], almond_pt(almond, 0)[1] + 0.3), (ix, iy + 1.1), (almond_pt(almond, 3)[0], almond_pt(almond, 3)[1] + 0.3)],
                           [0.2, 0.8, 0.2]), LASH, 0.95)]
        else:
            fd += [(almond.scale(1.06, 1.18, ix, iy + 0.2), SKIN.shadow, 0.55), (almond, '#fdf3ea', 1)]
            iris = inter(ellipse(ix, iy, ir * (1 if ir > 1.3 else 0.85), ir * 1.05), almond)
            if iris:
                fd += [(iris, ('rad', ix + 0.2, iy + 0.5, ir * 1.15, ir * 1.15, [(0, '#ffd47a'), (0.45, '#ffaa36'), (0.8, '#d8640e'), (1, '#8a2e0c')]), 1)]
            pup = inter(ellipse(ix + 0.05, iy - 0.05, ir * (0.42 if ir > 1.3 else 0.36), ir * 0.55), almond)
            if pup:
                fd += [(pup, '#2a0812', 1)]
            fd += [(sm([almond_pt(almond, 0), almond_pt(almond, 1), almond_pt(almond, 2), almond_pt(almond, 3),
                        lerp(almond_pt(almond, 2), (ix, iy), 0.4), lerp(almond_pt(almond, 1), (ix, iy), 0.45)], t=0.8), SKIN.shadow, 0.32),
                   (ellipse(ix + ir * 0.38, iy - ir * 0.3, ir * 0.3, ir * 0.25), '#ffffff', 1),
                   (ellipse(ix - ir * 0.35, iy + ir * 0.45, ir * 0.16, ir * 0.13), '#fff4d8', 0.8)]
            # la ligne des cils du bas, fine, au coin extérieur
            o, b1 = almond_pt(almond, 0), almond_pt(almond, 5)
            fd += [(ribbon([o, lerp(o, b1, 0.55), b1], [0.1, 0.35, 0.05]), LASH, 0.6)]
        fd += [(liner, LASH, 1)]
    # le nez fin : l'arête claire en diagonale, de l'entre-deux-yeux au bout qui dépasse à peine (elle cache le coin
    # intérieur de l'œil lointain), le flanc dans l'ombre douce dessous, une narine
    fd += [(sm([(78.4, 34.6), (81.4, 36.4), (83.6, 37.6), (84.2, 38.6), (82.2, 39.1), (80.2, 37.9)]), SKIN.shadow, 0.32),
           (ribbon([(79.6, 35.0), (82.0, 35.9), (83.8, 36.4), (85.2, 37.0)], [0.1, 0.4, 0.5, 0.3]), SKIN.hi, 0.85),
           (ribbon([(77.9, 32.4), (78.6, 33.4), (79.0, 34.2)], [0.1, 0.35, 0.1]), SKIN.hi, 0.5),
           (ellipse(85.0, 37.1, 0.6, 0.42, 20), '#fff8f0', 0.85),
           (ellipse(83.4, 38.4, 0.65, 0.32, 15), SKIN.deep, 0.8),
           (ribbon([(81.8, 39.2), (83.6, 39.3), (85.0, 38.7)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.5)]
    # les lèvres pleines, à peine entrouvertes, le coin relevé : l'intérieur rouge sombre (jamais noir)
    fd += [(sm([(79.4, 41.0), (81.0, 40.3), (82.3, 40.5), (83.0, 40.2), (84.1, 40.6), (83.9, 41.3), (81.6, 41.3), (79.9, 41.4)], sharp=(0, 5), t=0.85), '#b02c48', 1),
           (sm([(79.9, 41.35), (81.6, 41.25), (83.9, 41.25), (83.5, 41.9), (81.4, 42.0)], sharp=(0, 2), t=0.85), '#5c1024', 1),
           (sm([(80.4, 41.9), (82.0, 42.0), (83.5, 41.85), (83.5, 42.6), (82.3, 43.3), (80.9, 42.9)], t=0.9), '#cc3848', 1),
           (ellipse(82.4, 42.5, 0.75, 0.3, -6), '#f07476', 0.9),
           (ribbon([(81.2, 40.5), (82.3, 40.6), (83.0, 40.35)], [0.1, 0.3, 0.1]), '#e0606a', 0.7),
           (ribbon([(79.0, 40.6), (79.6, 41.2)], [0.1, 0.3]), SKIN.deep, 0.55)]
    # le menton éclairé
    fd += [(ellipse(82.0, 44.9, 1.1, 0.7, -20), SKIN.hi, 0.4)]
    part('face', face, SKIN, grad=(84, 26, 68, 46, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.0, rim=0.5, cast=1.0, details=fd)

    # ---- la calotte de plumes (sur le crâne) : la naissance des plumes arrondie sous le diadème, tempe dégagée ;
    # l'arrière se termine en pointes de plumes couchées (pas un bord de casque) ----
    ph, amp = P['ph'], P['amp']
    cap = sm([(82.8, 25.6), (80.2, 24.4), (75.6, 24.4), (71.8, 25.4), (69.4, 27.8), (68.2, 31.0), (67.6, 35.0),
              (66.8, 39.4), (65.4, 43.4), (61.6, 44.6), (63.4, 41.4), (59.4, 40.2), (62.0, 36.6), (58.2, 34.2),
              (61.4, 30.2), (58.6, 26.4), (62.6, 23.4), (61.4, 19.2), (66.2, 17.6), (67.4, 14.2), (73.6, 13.6),
              (79.8, 14.8), (84.4, 17.8), (86.2, 21.4), (85.2, 24.6)], sharp=(9, 11, 13, 15, 17, 19), t=0.95)
    cdet = [(cap, ('rad', 81, 17, 26, 26, [(0, '#ffb848'), (0.35, '#f47024'), (0.72, '#d03a24'), (1, '#9a1e32')]), 1)]
    # des plumes couchées vers l'arrière, dessinées dans la calotte (arcs doux, inégaux)
    for (a0, a1, a2), w_, col, op in ((((84.6, 20.4), (77.0, 16.8), (68.0, 18.6)), 1.6, '#ffd060', 0.7),
                                      (((82.0, 23.8), (74.4, 20.8), (65.0, 24.6)), 1.3, '#ffae40', 0.55),
                                      (((76.6, 25.8), (69.2, 26.4), (62.6, 32.0)), 1.2, '#9a1e32', 0.45),
                                      (((69.6, 31.2), (65.6, 34.6), (62.4, 40.0)), 1.1, '#8e1c32', 0.45)):
        cdet.append((ribbon([a0, a1, a2], [0.15, w_, 0.15]), col, op))
    part('cap', cap, FEA, cel=0.9, rim=0.6, cast=1.1, cast_on=['face'] + [n for n in fig_names(fig) if n.startswith('h')],
         ink=FINK, details=cdet)

    # ---- la grande plume du dessus du front : elle monte un peu en avant puis se couche vers l'arrière en suivant
    # le crâne, comme le reste de la chevelure, la pointe relevée ----
    w1 = math.sin(ph + 0.4)
    p0, p1, p2, p3 = (80.2, 23.4), (85.6, 18.8), (80.0, 13.4 + 0.4 * w1), (69.6 - 0.6 * amp * w1, 10.2 + 0.8 * amp * w1)
    sh = lock(p0, p1, p2, p3, 7.4, bulge=0.28)
    part('fore', sh, FEA, grad=(p0[0], p0[1], p3[0], p3[1], [(0, '#ffd070'), (0.3, '#ffa232'), (0.7, '#ee6222'), (1, '#c02c22')]),
         cel=0, rim=0.6, cast=1.1, ink=FINK,
         details=[(under(sh, 0.8, -2.6), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, '#e0601e', 0.6), (1, '#8e1c32', 0.6)]), 1)])

    # ---- le diadème d'or (fait le tour du front d'un bord à l'autre), fleuron et rubis ----
    dia = sm([(69.0, 26.6), (72.6, 24.8), (77.4, 24.2), (81.0, 24.5), (83.6, 25.3), (83.5, 26.9), (81.0, 26.2),
              (77.4, 25.9), (73.0, 26.5), (69.6, 28.4)], sharp=(0, 4, 5, 9), t=0.9)
    part('diadem', dia, GOLD, cel=0.5, rim=0.45, cast=0.9, cast_on=['face', 'cap'],
         details=[(ribbon([(70.0, 26.4), (74.0, 24.9), (78.0, 24.6), (83.0, 25.4)], [0.1, 0.45, 0.45, 0.1]), GOLD.hi, 0.9)])
    fl = sm([(76.2, 25.0), (76.0, 23.0), (77.6, 20.4), (79.2, 23.0), (79.0, 25.0)], sharp=(0, 2, 4), t=0.9)
    part('fleur', fl, GOLD, cel=0.5, rim=0.4, cast=0.8,
         details=[(ellipse(77.6, 23.3, 1.0, 1.05), RUBY.deep, 1),
                  (ellipse(77.6, 23.3, 0.78, 0.82), ('rad', 77.9, 23.0, 0.9, 0.9, [(0, RUBY.light), (0.6, RUBY.base), (1, RUBY.shadow)]), 1),
                  (ellipse(77.9, 23.0, 0.25, 0.22), '#ffeee8', 0.95)])

    # ---- la petite plume de la tempe (sa pointe orangée vient sur la pommette) ----
    a = 80 + amp * 2 * math.sin(ph + 0.4)
    sh = plume((68.2, 29.6), a, 9.6, 3.4, curl=-24)
    tp = sh_tip((68.2, 29.6), a, 9.6, -24)
    part('temple', sh, FEA, grad=(68.2, 29.6, tp[0], tp[1], [(0, '#c42c26'), (0.55, '#f26422'), (1, '#ffb23a')]), cel=0, rim=0.4,
         cast=0.9, ink=FINK, details=[(under(sh, 0.5, -1.4), '#5a0e2e', 0.35)])
    # ---- la longue plume qui suit la joue jusque sous la mâchoire (pointe jaune) ----
    a = 98 + amp * 2 * math.sin(ph - 0.4)
    sh = plume((67.8, 30.4), a, 18.8, 4.0, curl=-64)
    tp = sh_tip((67.8, 30.4), a, 18.8, -64)
    part('cheek', sh, FEA, grad=(67.8, 30.4, tp[0], tp[1], [(0, '#b42a2c'), (0.4, '#e8501e'), (0.75, '#ff9a2a'), (1, '#ffdc68')]),
         cel=0, rim=0.45, cast=1.1, ink=FINK, details=[(under(sh, 0.7, -1.8), ('lin', 67.6, 29.4, tp[0], tp[1], [(0, '#4a0c2a', 0.5), (1, '#c8381e', 0.3)]), 1)])
    return names


def fig_names(fig):
    return [p.name for p in fig.parts]


def almond_pt(sh, i):
    """Le i-ème point de passage d'une forme (sm)."""
    s, segs = sh.subs[0]
    return s if i == 0 else segs[i - 1][2]


def main():
    """rook.svg (grand) et rook-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/assassins-5.webp (512 px de haut) et assassins-5-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('rook', 0.95, 512, 'assassins-5'), ('rook-petit', 1.35, 160, 'assassins-5-160')):
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
