# Rook (assassins-5, feu, soigneuse) en VECTORIEL lisse, style moderne de l'interface (même méthode et même qualité
# que Kael : ../kael/kael.py, outil commun ../atelier.py ; outils en plus : outils.py ; visage : ../visage.py).
#
#   python3 refonte-graphique/ui-moderne/heros/rook/rook.py          # → rook.svg + images 512 et 160 px de haut
#
# REFONTE du 26/11/2026 (avis du propriétaire : « enlever le côté humain, faire un phénix, tête d'aigle, corps d'aigle,
# plus rien d'humain ; attention aux connexions entre les angles, à la cohérence du visage ») : Rook est un PHÉNIX
# debout, posé au sol sur ses serres, tourné de 3/4 vers la droite, les deux grandes ailes de feu levées en V (même
# pose et mêmes ailes que le pixel art refonte-graphique/pixel/hd/rook.txt).
# - Tête d'aigle de profil (un seul œil, placé par visage.placer(boite, tour=75)) : bec crochu doré, arcade sombre
#   qui abaisse le regard (fier), œil d'ambre, trait de flamme jaune sous l'œil, crête de grandes plumes de feu
#   couchées vers l'arrière, diadème d'or au rubis à la base de la crête ;
# - le cou est fait des plumes de la nuque (camail) qui descendent sur le dos et des plumes de la gorge qui tombent
#   sur le jabot : la tête se pose sur le corps SANS couture (plumes par-dessus plumes) ;
# - corps d'aigle en forme d'œuf, d'un seul tenant avec la naissance de l'aile proche (outils.fuse) ; jabot et
#   poitrine de plumes d'or en écailles ; torque d'or au rubis à la base du cou ; frange de plumes du ventre sur
#   les « culottes » de plumes des cuisses ; pattes écailleuses aux serres sombres ; longue queue de flammes.
# Coordonnées = pixels du dessin pixel art (y = 116 est le sol), pour se poser au même endroit dans le jeu.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; aucune jointure visible.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from outils import crpath, fuse, plume, under, lerp, rot, rotp, along, inter  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402,F401


ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
GOLD = Mat('#fff7c4', '#ffd862', '#e29a28', '#9c4e1a', '#4c1a1e', glint='#fffbe6')
GOLDF = Mat('#ffe39a', '#e8aa3a', '#b86c22', '#7a3a1c', '#40141e')            # l'or de l'aile lointaine (ombre)
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

STUB, CAP = True, True
GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art (sol : 64 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin : les pieds (64, 116) y tombent en (64, 124)
FRAME = (0, -8, 138, 126)

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
FAR_TIPS0 = [(88.5, 78.5), (93.0, 80.5), (98.5, 80.0), (104.0, 77.0), (108.5, 72.5), (112.0, 67.0), (115.0, 61.0),
            (116.5, 55.0), (118.4, 48.0), (119.6, 41.0), (121.0, 33.5), (122.6, 26.0), (123.4, 19.0), (123.2, 12.6)]
FAR_BONES0 = FAR_BONES
# le phénix : l'aile lointaine un peu plus ouverte vers la droite (14° autour de l'épaule, +2 px) pour que le bec
# crochu se détache sur le fond et non sur le bord doré de l'aile
FAR_BONES = [(p[0] + 2.0, p[1]) for p in (rotp(q, 14, FAR_BONES0[0]) for q in FAR_BONES0)]
FAR_TIPS = [(p[0] + 2.0, p[1]) for p in (rotp(q, 14, FAR_BONES0[0]) for q in FAR_TIPS0)]


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
        wdt = 7.4 - 2.4 * i / (nc - 1)
        root, ang, L, wv = place(u, tip, 0.48 * wdt, i * 1.4)
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
        wdt = 4.8 - 2.2 * i / (nl - 1)
        root, ang, L, wv = place(u, tip, 0.5 + 0.5 * wdt, i * 1.2)
        sh = plume(root, ang, L + 0.6, wdt, curl=sg * 8, kind='cover')
        tp = sh_tip(root, ang, L, sg * 8)
        nm = '%sl%d' % (pre, i)
        fig.part(nm, sh, GOLD, grad=(root[0], root[1], tp[0], tp[1], GL), cel=0, rim=0.5, cast=0.9, ink=FINK,
                 cast_on=[x for x in names],
                 details=[(under(sh, 0.4 * sg, -1.5), ('lin', root[0], root[1], tp[0], tp[1],
                                                      [(0, '#b0581c', 0.45), (1, '#e0901e', 0.3)]), 1)])
        names.append(nm)
    # -- le bord d'attaque doré (le bras, de l'épaule au bout de la main), d'un seul tenant --
    c = crpath(([lerp(bones[0], bones[1], 0.25)] if near else [lerp(bones[0], bones[1], -0.1)]) + bones[1:], 30)
    # l'aile proche : le bord doré NAÎT de l'épaule (il s'élargit depuis un point sur la naissance de l'aile, aucun
    # bout rond posé sur le corps)
    ws = [(5.0 - 3.5 * (i / 30) ** 1.1) * (min(1.0, 0.12 + 0.88 * (i / 7) ** 0.8) if near else 1.0) for i in range(31)]
    band = limb(c, ws)
    nm = pre + 'edge'
    det = [(ribbon([(p[0] + 0.5 * sg - 0.2, p[1] - 0.9) for p in c[2:28:3]], [0.1] + [0.9] * 7 + [0.1]), gold.hi, 0.75)]
    # l'aile lointaine : son bord doré s'assombrit vers l'épaule (en retrait derrière la tête et le bec)
    gstops = [(0, gold.light), (0.5, gold.base), (1, gold.light)] if near else [(0, '#e8aa3a'), (0.45, '#b86c22'), (1, '#6a2a1c')]
    fig.part(nm, band, gold, grad=(c[0][0] + 6 * sg, c[0][1] - 18, c[-1][0], c[-1][1] + 10, gstops) if near else
             (c[-1][0], c[-1][1], c[0][0], c[0][1], gstops),
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


# ---------- la tête d'aigle (repère du dessin, AVANT l'agrandissement ×1,1 autour du cou) ----------
HK = 1.1                                  # la tête un peu plus grande (comme Kael)
NECK = (77.0, 47.0)                       # le point du cou autour duquel la tête s'agrandit, tourne et penche
# Avis du 26/11 (tour 2) : la tête se voit PRESQUE DE FACE, comme l'autre chevalier aigle (Tessa) : deux yeux sur la
# même ligne, le bec part du MILIEU, entre les deux yeux (racine = la cire, sur la médiane), et descend en crochet.
FACE_BOX = (66.5, 20.0, 88.5, 43.5)       # l'ovale de la tête (sans la crête ni le bec)
FACE_V = placer(FACE_BOX, l_oeil=0.24)    # 3/4 léger commun à tous les héros (visage.py)
EYE = FACE_V['oeil_proche']               # (x, y, largeur) l'œil proche (à gauche de l'image)
EYE_F = FACE_V['oeil_fond']               # l'œil du fond, un peu plus étroit, même ligne
NOSE = FACE_V['nez']                      # la médiane du bec (racine entre les yeux)
NX, EYY = NOSE[0], EYE[1]
# les positions RÉELLES des traits dans le dessin (contrôlées par visage.verifier dans main()) : les narines dans la
# cire, la ligne de fermeture du bec (bec fermé)
fig_face = {'oeil_proche': EYE, 'oeil_fond': EYE_F, 'nez': (NX, EYY + 2.3), 'bouche': (80.2, 40.6, 6.0)}

BREAST = Mat('#fff6c8', '#ffd866', '#f6a634', '#cc6428', '#86283a', glint='#fffbe6')   # le jabot d'or
BODYM = Mat('#ffb45a', '#f0702a', '#c8342a', '#8a1a34', '#4e0e2e')                     # le dos, les flancs
HEADM = Mat('#ffd27a', '#ff9a34', '#e85a22', '#a8242e', '#5e1030')                     # les plumes de la tête
BEAK = Mat('#fffbe2', '#ffe47a', '#f4b83a', '#c47426', '#6a2e1a', glint='#ffffff')      # le bec doré
IRIS = ['#fff4b0', '#ffc83a', '#f08a1a', '#a8401a']


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']

    # ---- le squelette : une matrice par groupe de morceaux ----
    LIFT = mT(0, -P['lift'])
    dyb = P['crouch'] * 0.85
    BODY = mchain(LIFT, mT(P['lean'] * 0.35, dyb), mR(P['lean'] * 1.1, 71, 80))   # le corps (depuis le bassin)
    UC = mchain(BODY, mT(0, -0.55 * br))                                            # ce qui monte avec la poitrine
    TOR = mchain(BODY, mS(1 + 0.008 * br, 1 + 0.014 * br, 72, 80))                  # le jabot se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], NECK[0], NECK[1] - 2), mS(HK, HK, *NECK))
    T_ = lambda p: mapp(TOR, p)

    # ---- l'aile lointaine (derrière tout) ----
    SF = mapp(UC, FAR_BONES[0])
    far_names, far_bones, _ = wing(fig, 'f', P, SF)

    # ---- la queue : longues plumes en éventail vers la gauche, la plus basse touche le sol ----
    tail(fig, P, BODY)

    # ---- les pattes (elles restent au sol) : culottes de plumes, tarse écailleux, doigts, serres sombres ----
    legs(fig, P, BODY, LIFT)

    # ---- le corps d'aigle (un œuf penché), d'un seul tenant avec la naissance de l'aile proche ----
    SN = mapp(UC, NEAR_BONES[0])
    near_r0 = P['wn'] * -1 + P['lean'] * 1.1
    nb = bone_pose(NEAR_BONES, SN, near_r0, P['fold'] * 0.5, P['fold'])
    # le bas du corps finit en pointes de plumes qui tombent sur les culottes des cuisses (plumes sur plumes)
    body0 = [(65.4, 43.4), (70.6, 41.0), (77.0, 40.4), (82.2, 41.8), (85.8, 45.6), (88.4, 51.4), (89.4, 58.4),
             (88.8, 65.6), (86.8, 72.0), (84.2, 77.0), (84.6, 81.4), (81.4, 79.6), (79.6, 84.6), (76.6, 81.8),
             (73.0, 86.4), (70.0, 82.4), (66.4, 85.8), (64.0, 81.0), (60.6, 83.6), (59.4, 79.0), (56.4, 81.0),
             (55.0, 73.6), (55.0, 66.6), (55.0, 59.2), (56.0, 53.8), (59.0, 48.6), (62.2, 45.2)]
    # (avis du 26/11, tour 2 : la liaison corps ↔ cuisse proche) le flanc gauche descend droit jusqu'à la cuisse : le
    # bord de la culotte de plumes continue le contour du corps (plus d'encoche), la frange du ventre tombe dessus
    body = sm([T_(p) for p in body0], sharp=(10, 12, 14, 16, 18, 20), t=0.95)
    # la naissance de l'aile proche (avis du 26/11, tour 2 : « les liaisons ») : une aisselle souple, large contre le
    # corps et qui s'affine jusqu'au coude, sous le bord doré de l'aile ; le contour du corps monte sans marche jusqu'à
    # l'aile (plus de moignon rond)
    S0, E0 = nb[0], nb[1]
    ax, ay = E0[0] - S0[0], E0[1] - S0[1]
    al = math.hypot(ax, ay)
    nrm = (-ay / al, ax / al)                                  # vers le haut de l'aile (côté du bord doré)

    def off(t, d):
        q = lerp(S0, E0, t)
        return (q[0] + nrm[0] * d, q[1] + nrm[1] * d)
    stub = sm([T_((62.0, 44.6)), off(0.1, 2.6), off(0.45, 2.2), off(0.88, 1.6), off(1.0, 0.0), off(0.9, -2.4),
               off(0.55, -3.6), off(0.2, -5.0), T_((55.6, 61.0)), T_((57.0, 52.0))], sharp=(4,), t=0.95)
    body_f = fuse([body] + ([stub] if STUB else []), close=1.2, step=0.7, t=0.9)
    bdet = []
    # des plumes de dos et de flanc (arcs doux) dans la partie rouge, à gauche du jabot
    for (a0, a1, a2), w_, col, op in ((((59.2, 58.0), (61.6, 62.6), (61.4, 67.8)), 1.0, '#5e1030', 0.4),
                                      (((58.4, 67.6), (61.0, 72.0), (62.8, 76.4)), 1.0, '#5e1030', 0.4),
                                      (((62.6, 52.6), (65.2, 56.4), (65.6, 61.0)), 0.9, '#ff9a46', 0.35),
                                      (((62.4, 66.0), (64.6, 70.6), (66.4, 74.6)), 0.8, '#ff9a46', 0.3)):
        bdet.append((ribbon([T_(a0), T_(a1), T_(a2)], [0.1, w_, 0.1]), col, op))
    # le jabot et la poitrine d'or : peints DANS le corps (un dégradé qui se fond dans le rouge du dos, aucune
    # couture, pas un « plastron » posé dessus) ; des plumes en écailles, nettes sur le jabot, de plus en plus
    # douces vers le ventre
    bdet.append((body_f, ('rad', *T_((82.6, 57.0)), 15.5, 26.0, [(0, '#ffe68a', 1), (0.42, '#ffc248', 1), (0.7, '#f89234', 0.85),
                                                             (0.88, '#ee6a2c', 0.45), (1, '#e2502a', 0)]), 1))
    ROWS = ((51.2, [(73.0, 77.0), (76.8, 80.8), (80.6, 84.6)], 0.42),
            (56.2, [(71.4, 75.6), (75.4, 79.6), (79.4, 83.6), (83.4, 87.2)], 0.36),
            (61.8, [(70.4, 74.8), (74.6, 79.0), (78.8, 83.2), (83.0, 87.0)], 0.28),
            (67.8, [(72.0, 76.6), (76.4, 81.0), (80.8, 85.0)], 0.2))
    for row, (y0, xs, op) in enumerate(ROWS):
        for a, b in xs:
            m = (a + b) / 2
            yy = y0 + 0.35 * math.sin(a * 1.3 + row)
            dep = 1.5 + 0.2 * row
            # le bord arrondi d'une plume : un croissant d'ombre sous le bord, un liseré clair juste au-dessus
            cres = sm([T_((a, yy)), T_((a + 0.3 * (b - a), yy + 0.75 * dep)), T_((m, yy + dep)), T_((b - 0.3 * (b - a), yy + 0.75 * dep)),
                       T_((b, yy)), T_((m, yy + 0.45 * dep))], sharp=(0, 4), t=0.9)
            bdet.append((cres, '#d0642a', op))
            bdet.append((ribbon([T_((a + 0.6, yy - 0.2)), T_((m, yy + 0.35 * dep)), T_((b - 0.6, yy - 0.2))], [0.1, 0.45, 0.1]), '#fff2b0', op * 1.5))
    bdet.append((ellipse(*T_((85.0, 51.6)), 2.6, 1.2, -55), '#fff8d8', 0.6))
    fig.part('body', body_f, BODYM, grad=(86, 44, 58, 80, [(0, '#ff9a3a'), (0.4, '#e2502a'), (1, '#9a1e34')]),
             cel=1.2, rim=0.5, cast=1.0, ink=FINK, details=bdet)

    # ---- le petit plastron d'or (avis du 26/11, tour 2 : « une petite armure sur le torse ») : une pièce d'armure
    # ajustée, posée sur les plumes de la poitrine, accrochée sous le torque ; elle épouse le jabot (3/4 : la moitié
    # du fond plus étroite, l'arête un peu à droite du milieu), les plumes d'or du ventre sortent de dessous ----
    plate0 = [(67.4, 51.0), (72.4, 53.4), (78.2, 54.2), (83.6, 52.8), (87.6, 50.4), (88.4, 54.8), (87.8, 60.0),
              (86.0, 64.6), (82.8, 68.6), (78.8, 71.6), (74.8, 68.8), (71.2, 64.6), (68.6, 59.4), (67.4, 54.8)]
    plate = sm([T_(p) for p in plate0], sharp=(0, 4, 9), t=0.95)
    pdet = [
        # la moitié proche dans la demi-teinte (la lumière vient d'en haut à droite), l'arête plus vive
        (sm([T_(p) for p in ((67.4, 51.0), (72.4, 53.4), (78.2, 54.2), (78.9, 60.6), (78.8, 71.6), (74.8, 68.8), (71.2, 64.6),
                              (68.6, 59.4), (67.4, 54.8))], sharp=(0, 2, 4), t=0.95), ('lin', *T_((79, 56)), *T_((68, 66)),
                                                                                    [(0, '#e8962a', 0.2), (1, '#9c4e1a', 0.7)]), 1),
        (ribbon([T_((78.4, 54.6)), T_((79.0, 60.8)), T_((78.9, 66.6)), T_((78.8, 70.8))], [0.2, 0.7, 0.6, 0.1]), GOLD.hi, 0.9),
        # le bord relevé (un liseré plus sombre, parallèle au bord) et le reflet sur la moitié claire
        (ribbon([T_((69.2, 56.0)), T_((70.6, 61.6)), T_((73.6, 66.2)), T_((78.8, 70.0)), T_((83.0, 66.6)), T_((86.0, 61.4)), T_((86.8, 55.6))],
                [0.1, 0.5, 0.55, 0.55, 0.55, 0.5, 0.1]), '#9c4e1a', 0.55),
        (ribbon([T_((84.6, 54.2)), T_((85.4, 58.6)), T_((84.0, 63.0))], [0.1, 0.8, 0.1]), '#fffbe6', 0.8),
        # au milieu, un signe en relief : une flamme d'or (signe inventé)
        (sm([T_(p) for p in ((80.0, 57.4), (81.6, 60.0), (81.8, 62.8), (80.4, 65.0), (78.6, 65.4), (77.4, 63.4), (78.0, 60.8),
                              (79.0, 61.8))], sharp=(0, 7), t=0.9), '#a8561c', 0.55),
        (sm([T_(p) for p in ((80.2, 58.0), (81.4, 60.2), (81.4, 62.6), (80.2, 64.4), (79.0, 64.6), (78.2, 63.2), (78.6, 61.4),
                              (79.4, 62.2))], sharp=(0, 7), t=0.9), ('lin', *T_((81.4, 58.4)), *T_((78.4, 64.6)),
                                                                     [(0, '#fff6c8'), (0.5, '#ffd862'), (1, '#e29a28')]), 1),
    ]
    fig.part('plate', plate, GOLD, grad=(*T_((88, 51)), *T_((68, 70)), [(0, '#fff3b8'), (0.3, '#ffd862'), (0.7, '#eea434'), (1, '#b8621e')]),
             cel=0.7, rim=0.55, cast=1.2, ink=FINK, cast_on=['body'], details=pdet)

    # ---- le torque d'or (il fait le tour de la base du cou : l'arrière passe sous le camail) et son rubis ----
    tq0 = [(64.8, 46.4), (69.4, 49.4), (74.6, 51.2), (80.0, 50.8), (84.6, 48.6), (87.0, 47.6), (87.6, 49.6),
           (85.0, 51.0), (80.2, 53.0), (74.4, 53.4), (69.0, 51.6), (64.6, 48.6)]
    fig.part('torque', sm([T_(p) for p in tq0], sharp=(5, 6), t=0.9), GOLD, cel=0.6, rim=0.5, cast=0.8,
             cast_on=['body', 'plate'],
             details=[(ribbon([T_((66.0, 47.6)), T_((74.6, 51.8)), T_((84.8, 49.2))], [0.1, 0.55, 0.1]), GOLD.hi, 0.85)])
    pend = sm([T_((76.2, 52.4)), T_((78.2, 53.2)), T_((78.0, 55.6)), T_((76.9, 57.4)), T_((75.8, 55.6)), T_((75.6, 53.4))], sharp=(3,), t=0.9)
    fig.part('pend', pend, RUBY, cel=0.5, rim=0.4, cast=0.7, cast_on=['body', 'plate'],
             details=[(ellipse(*T_((77.3, 54.0)), 0.55, 0.7), '#ffe2d8', 0.9)])

    # ---- le camail : les plumes de la nuque descendent sur le dos (posées avec la tête) ----
    hack = hackles(fig, P)

    # ---- l'aile proche ----
    near_names, near_bones, near_path = wing(fig, 'n', P, SN)

    # ---- l'épaule (avis du 26/11, tour 2 : la liaison aile ↔ corps) : un paquet de plumes scapulaires, de la couleur
    # du dos, posé par-dessus la naissance de l'aile proche ; ses pointes tombent sur le flanc, le bord doré de l'aile
    # sort de dessous. Plus de moignon rond entre le corps et l'aile. ----
    if CAP:
        shoulder(fig, P, nb)

    # ---- la tête ----
    head_names = head(fig, P)

    # ---- il s'embrase d'un feu doré bienfaisant (attaque spéciale) : toutes ses plumes montent vers l'or ----
    if P['fire'] > 0:
        for p in fig.parts:
            x0, y0, x1, y1 = p.shape.bbox()
            pale = p.mat is BEAK
            p.details.append((p.shape, ('lin', x1, y0, x0, y1, [(0, '#fff6c0'), (0.5, '#ffd858'), (1, '#ffa830')]),
                              min(0.14 if pale else 0.3, (0.05 if pale else 0.1) * P['fire'])))
            p.rim = max(p.rim, 0.35 + 0.12 * P['fire'])

    # ---- chaque groupe prend sa pose ----
    fig.pose(head_names + hack, HEAD)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(P=P, BODY=BODY, UC=UC, HEAD=HEAD, head=mapp(HEAD, (78, 34)), chest=T_((76, 62)), waist=T_((71, 78)),
                   beak=mapp(HEAD, (83.1, 45.6)),
                   tipN=near_bones[-1], tipF=far_bones[-1], wristN=near_bones[2], wristF=far_bones[2],
                   SN=SN, SF=SF, near_bones=near_bones, far_bones=far_bones, feet=mapp(LIFT, FEET),
                   parts=[p.name for p in fig.parts])
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def shoulder(fig, P, nb):
    """Les plumes de l'épaule proche (scapulaires) : trois plumes larges et courtes qui partent de l'épaule et du haut du
    bras de l'aile, couchées vers le bas sur le flanc, réunies en une seule forme (une seule ombre portée)."""
    S, E = nb[0], nb[1]
    a_arm = math.degrees(math.atan2(E[1] - S[1], E[0] - S[0]))      # la direction du bras (vers le coude)
    r0 = a_arm - math.degrees(math.atan2(NEAR_BONES[1][1] - NEAR_BONES[0][1], NEAR_BONES[1][0] - NEAR_BONES[0][0]))
    ph, amp = P['ph'], P['amp']
    SC = [(0.62, 96.0, 9.6, 6.4), (0.34, 84.0, 11.4, 7.0), (0.04, 72.0, 10.0, 6.6), (-0.22, 62.0, 7.0, 5.6)]
    shapes, dets = [], []
    for i, (t, ang, L, w) in enumerate(SC):
        root = lerp(S, E, t)
        a = ang + 0.45 * r0 + 1.5 * amp * math.sin(ph - 0.6 * i - 1.2)
        sh = plume(root, a, L, w, curl=-10, kind='cover')
        shapes.append(sh)
        tip = sh_tip(root, a, L, -10)
        dets.append((root, tip, sh))
    cap = fuse(shapes + [ellipse(*lerp(S, E, 0.25), 4.6, 3.6, a_arm)], close=0.8, step=0.6, t=0.9)
    det = []
    # la séparation des plumes : la face du dessous de chacune (sauf la dernière, devant)
    for root, tip, sh in dets[:-1]:
        det.append((under(sh, -0.6, -1.8), ('lin', root[0], root[1], tip[0], tip[1], [(0, '#6a1236', 0.0), (0.5, '#8a1a34', 0.5), (1, '#5e1030', 0.55)]), 1))
    root, tip, _ = dets[1]
    fig.part('scap', cap, BODYM, grad=(S[0] + 3, S[1] - 6, tip[0] - 3, tip[1] + 2, [(0, '#ff9a3a'), (0.45, '#e2502a'), (1, '#a8243a')]),
             cel=1.0, rim=0.5, cast=1.1, ink=FINK, details=det)
    return ['scap']


def hackles(fig, P):
    """Le camail : de longues plumes de flamme partent de l'arrière du crâne et descendent sur le dos (courbes en S,
    pointes relevées ; longueurs et écarts inégaux). Du bas vers le haut : la plus haute recouvre celle du dessous."""
    names = []
    ph, amp = P['ph'], P['amp']
    LOCKS = [
        # (nom, p0 racine, p1, p2, p3 pointe, largeur) — repère de la tête (avant l'agrandissement)
        ('k3', (71.4, 43.0), (70.0, 46.4), (68.4, 49.4), (65.6, 51.8), 6.0),
        ('k2', (69.4, 40.0), (67.0, 44.0), (64.4, 47.0), (60.6, 49.2), 7.0),
        ('k1', (68.4, 35.6), (65.0, 39.6), (61.8, 42.4), (57.2, 43.4), 7.6),
        ('k0', (68.6, 30.6), (64.6, 33.8), (60.6, 35.6), (56.4, 34.8), 7.4),
    ]
    for i, (nm, p0, p1, p2, p3, w) in enumerate(LOCKS):
        k = 0.5 + 0.1 * i
        wv = math.sin(ph - 0.8 * i - 0.5)
        p2 = (p2[0] + 0.4 * k * amp * math.sin(2 * ph + 1.0 - 0.8 * i), p2[1] + 0.5 * k * amp * wv)
        p3 = (p3[0] + 0.8 * k * amp * math.sin(ph + 0.8 - 0.8 * i), p3[1] + 0.8 * k * amp * math.cos(ph - 0.8 * i))
        sh = lock(p0, p1, p2, p3, w, bulge=0.3)
        fig.part(nm, sh, FEA, grad=(p0[0], p0[1], p3[0], p3[1], G_HAIR), cel=0, rim=0.5, cast=1.1, ink=FINK,
                 details=[(under(sh, 0.8, -2.6), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, '#5a0e2e', 0.5), (0.5, '#b0242c', 0.45), (1, '#e0501e', 0.35)]), 1)])
        names.append(nm)
    return names


def head(fig, P):
    """La tête d'aigle presque de face (comme Tessa) : crête, crâne (gorge et nuque en pointes de plumes), deux yeux
    sous leurs arcades, bec crochu qui part du milieu, entre les yeux, diadème qui fait le tour du crâne.
    Rend la liste des morceaux (posés avec la tête)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    ph, amp = P['ph'], P['amp']
    # ---- la crête (derrière le crâne) : grandes plumes de feu couchées vers l'arrière, pointes relevées ----
    CREST = [
        ('cr0', (70.4, 27.6), (64.6, 26.4), (59.4, 25.6), (54.0, 21.4), 7.0),
        ('cr1', (71.8, 24.0), (66.0, 19.8), (61.0, 17.4), (56.4, 11.2), 7.8),
        ('cr2', (74.8, 21.8), (70.8, 15.0), (66.6, 10.8), (64.4, 3.4), 7.8),
    ]
    for i, (nm, p0, p1, p2, p3, w) in enumerate(CREST):
        wv = math.sin(ph - 0.7 * i)
        p2 = (p2[0] + 0.5 * amp * math.sin(2 * ph + 1.0 - 0.8 * i), p2[1] + 0.6 * amp * wv)
        p3 = (p3[0] + 1.0 * amp * math.sin(ph + 0.8 - 0.8 * i), p3[1] + 0.9 * amp * math.cos(ph - 0.8 * i))
        sh = lock(p0, p1, p2, p3, w, bulge=0.3)
        part(nm, sh, FEA, grad=(p0[0], p0[1], p3[0], p3[1], G_HAIR), cel=0, rim=0.5, cast=1.2, ink=FINK,
             cast_on=[n for n in names],
             details=[(under(sh, 0.8, -2.6), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, '#5a0e2e', 0.5), (0.5, '#b0242c', 0.45), (1, '#e0501e', 0.35)]), 1)])

    # ---- le crâne, presque de face : rond, la joue proche (à gauche) plus large, le côté du fond plus plat ; la gorge
    # finit en pointes de plumes posées sur le torque, et l'arrière de la tête aussi : de petites pointes de plumes
    # couchées sur le camail (plumes sur plumes, aucune ligne nette entre la tête et le cou) ----
    skull = sm([(67.2, 26.6), (70.4, 22.4), (75.2, 19.8), (80.8, 19.4), (85.4, 21.2), (88.2, 24.8), (89.2, 29.4),
                (89.0, 33.8), (87.8, 37.6), (86.0, 40.8), (84.4, 43.6), (84.6, 47.0), (82.2, 45.4), (80.6, 48.8),
                (78.6, 46.2), (76.6, 49.8), (74.6, 46.6), (72.2, 49.2), (70.6, 45.8), (68.0, 47.4), (67.4, 43.8),
                (64.8, 43.4), (66.0, 40.2), (64.2, 38.4), (65.8, 35.6), (65.0, 32.6), (66.2, 30.0)],
               sharp=(11, 13, 15, 17, 19, 21, 23, 25), t=0.95)
    exn, eyy, ewn = EYE
    exf, _, ewf = EYE_F
    nx = NX
    sd = []
    # l'arrière de la tête (vers la nuque) dans l'ombre, en plans de plumes (bord en petites pointes, pas une courbe)
    sd.append((sm([(66.4, 28.6), (69.6, 27.8), (70.4, 31.6), (69.0, 33.0), (70.6, 36.0), (69.2, 37.4), (71.0, 40.8),
                   (70.0, 44.6), (67.6, 46.4), (64.6, 43.2), (64.4, 36.0)], sharp=(2, 3, 4, 5, 6)), HEADM.shadow, 0.4))
    # le disque d'or du visage autour des deux yeux (l'or du phénix : les yeux se détachent, lisibles même tout petits)
    sd.append((sm([(71.2, 30.4), (74.4, 27.4), (79.0, 27.8), (81.0, 29.4), (83.2, 27.6), (87.4, 27.8), (89.0, 31.0),
                   (88.6, 35.6), (86.8, 39.4), (83.6, 41.0), (80.4, 39.4), (76.8, 40.6), (73.0, 39.2), (71.0, 35.4)]),
               ('rad', 81.6, 32.4, 10.6, 9.2, [(0, '#ffe68a', 1), (0.45, '#ffcc54', 0.95), (0.75, '#ffa63a', 0.5), (1, '#ff8a2a', 0)]), 1))
    # le trait de flamme jaune sous l'œil proche, qui file vers la nuque (le « masque » du phénix)
    sd.append((lock((exn + 0.6, eyy + 3.4), (exn - 2.6, eyy + 4.2), (exn - 6.0, eyy + 3.4), (exn - 9.0, eyy + 0.6), 2.4, bulge=0.2),
               ('lin', exn + 1, eyy + 3.4, exn - 9, eyy + 0.6, [(0, '#fff6c0'), (0.5, '#ffe070'), (1, '#ffb040', 0.7)]), 1))
    # des plumes couchées dans le crâne (arcs doux, inégaux) : le front lumineux en haut à droite, la joue proche
    for (a0, a1, a2), w_, col, op in ((((86.0, 23.2), (80.6, 21.4), (74.0, 23.0)), 1.2, '#ffd870', 0.6),
                                      (((72.6, 41.6), (70.4, 42.8), (68.6, 45.0)), 0.9, '#9a1e32', 0.25)):
        sd.append((ribbon([a0, a1, a2], [0.15, w_, 0.15]), col, op))
    # ---- les deux yeux, placés par visage.py (même ligne, même dessin ; l'œil du fond un peu plus étroit) : cerne
    # sombre, iris d'ambre, pupille vers la cible (à droite), reflet en haut à droite ; une arcade de plumes au-dessus
    # de chaque œil, un peu plus basse côté bec (regard fier, pas méchant), qui coupe le haut de l'iris ----
    # formes données pour l'œil proche (+x = côté bec) ; l'œil du fond les reprend en miroir, plus étroites
    BROW = [(-3.9, -2.3), (-1.2, -4.3), (2.2, -4.0), (4.0, -2.2), (3.6, -0.9), (1.2, -1.6), (-1.4, -2.1), (-3.4, -1.7)]
    BROW_HI = [(-3.6, -2.8), (-1.1, -4.3), (2.2, -4.0), (2.0, -3.5), (-1.0, -3.7)]
    for cx, w_, side in ((exn, ewn, 1), (exf, ewf, -1)):
        k = w_ / ewn
        rx, ry = w_ / 2, 2.45

        def loc(pts, cx=cx, k=k, side=side):
            return [(cx + side * x * k, eyy + y) for (x, y) in pts]
        if P['blink'] < 0.5:
            sd.append((ellipse(cx, eyy, rx + 0.5, ry + 0.45), '#2a0a1e', 1))
            sd.append((ellipse(cx, eyy, rx, ry - 0.05), ('rad', cx + 0.5 * k, eyy - 0.7, rx + 0.4, ry + 0.4,
                                                          [(0, IRIS[0]), (0.35, IRIS[1]), (0.8, IRIS[2]), (1, IRIS[3])]), 1))
            pc = (cx + 0.55 * k, eyy + 0.15)          # les deux pupilles regardent du même côté (vers la cible)
            sd.append((ellipse(pc[0], pc[1], 1.12 * k ** 0.5, 1.25), '#1a0612', 1))
            sd.append((ellipse(pc[0] + 0.55 * k, pc[1] - 0.8, 0.48 * k ** 0.5, 0.44), '#ffffff', 0.95))
            sd.append((ellipse(cx - 0.8 * k, eyy + 1.1, 0.3 * k, 0.24), '#fff4c0', 0.7))
        else:
            # paupière fermée : un trait sombre courbe sur la plume
            sd.append((ellipse(cx, eyy, rx + 0.4, ry + 0.3), '#ffc650', 1))
            sd.append((ribbon([(cx - rx, eyy + 0.2), (cx, eyy + 1.0), (cx + rx, eyy + 0.2)], [0.2, 0.8, 0.2]), '#2a0a1e', 1))
        brow = sm(loc(BROW), sharp=(0, 3), t=0.9)
        # l'ombre de l'arcade tombe sur le haut de l'œil
        sd.append((brow.move(-0.2, 0.6), '#3a0a22', 0.5))
        sd.append((brow, ('lin', cx + 2 * side, eyy - 4.0, cx - 2 * side, eyy - 1.2, [(0, '#ffa63a'), (0.6, '#f07028'), (1, '#c83a26')]), 1))
        sd.append((sm(loc(BROW_HI), sharp=(0, 2)), '#ffd27a', 0.85))
    part('skull', skull, HEADM, grad=(87, 20, 67, 46, [(0, '#ffb444'), (0.35, '#ff8a2c'), (0.7, '#e2502a'), (1, '#b02a2e')]),
         cel=1.0, rim=0.6, cast=1.1, ink=FINK, details=sd)

    # ---- la plume de devant de la crête (par-dessus le crâne), qui monte du milieu du front puis se couche en arrière
    w1 = math.sin(ph + 0.4)
    p0, p1, p2, p3 = (81.0, 22.6), (85.4, 17.6), (80.4, 12.4 + 0.4 * w1), (70.6 - 0.6 * amp * w1, 9.4 + 0.8 * amp * w1)
    sh = lock(p0, p1, p2, p3, 7.0, bulge=0.28)
    part('crf', sh, FEA, grad=(p0[0], p0[1], p3[0], p3[1], [(0, '#ffd070'), (0.3, '#ffa232'), (0.7, '#ee6222'), (1, '#c02c22')]),
         cel=0, rim=0.6, cast=1.1, ink=FINK,
         details=[(under(sh, 0.8, -2.6), ('lin', p0[0], p0[1], p3[0], p3[1], [(0, '#e0601e', 0.6), (1, '#8e1c32', 0.6)]), 1)])

    # ---- le diadème d'or : un bandeau qui fait le tour du crâne (il part du bord de la nuque et va jusqu'au bord du
    # fond, plus haut au milieu du front), fleuron et rubis sur la médiane ----
    dia = sm([(66.6, 28.4), (69.8, 24.8), (74.6, 22.0), (80.4, 21.0), (85.6, 22.2), (88.3, 25.0), (88.9, 27.4),
              (85.6, 24.6), (80.4, 23.4), (74.8, 24.4), (70.6, 27.0), (66.4, 30.8)], sharp=(0, 5, 6, 11), t=0.9)
    part('diadem', dia, GOLD, cel=0.5, rim=0.45, cast=0.9, cast_on=['skull', 'crf'] + [n for n in names if n.startswith('cr')],
         details=[(ribbon([(67.6, 28.2), (70.4, 25.4), (74.8, 22.8), (80.4, 21.8), (85.6, 22.9), (88.0, 25.2)], [0.1, 0.4, 0.45, 0.45, 0.45, 0.1]), GOLD.hi, 0.9)])
    fl = sm([(78.6, 22.6), (78.8, 20.0), (80.4, 17.2), (82.0, 20.0), (82.2, 22.6)], sharp=(0, 2, 4), t=0.9)
    part('fleur', fl, GOLD, cel=0.5, rim=0.4, cast=0.8,
         details=[(ellipse(80.4, 20.7, 1.05, 1.1), RUBY.deep, 1),
                  (ellipse(80.4, 20.7, 0.8, 0.85), ('rad', 80.7, 20.4, 0.9, 0.9, [(0, RUBY.light), (0.6, RUBY.base), (1, RUBY.shadow)]), 1),
                  (ellipse(80.7, 20.4, 0.26, 0.23), '#ffeee8', 0.95)])

    # ---- le bec crochu doré, vu presque de face : sa racine (la cire claire) ENTRE les deux yeux, sur la médiane ; il
    # s'élargit sous les yeux (commissures sous chaque œil) et se referme en crochet sous la médiane, un peu vers la
    # droite (il regarde à droite). Bec fermé : la mandibule ne dépasse qu'à peine sous le bord, côté proche. ----
    mand = sm([(76.2, 37.7), (78.2, 39.5), (80.3, 41.2), (82.4, 43.1), (82.4, 44.3), (80.1, 43.3), (78.0, 41.7), (76.4, 39.9), (75.6, 38.6)])
    part('beakL', mand, BEAK, grad=(83, 44, 76, 39, [(0, BEAK.base), (0.6, BEAK.shadow), (1, BEAK.deep)]), cel=0.6, rim=0.3, cast=0.9,
         ink=FINK, details=[(ribbon([(77.0, 39.2), (79.4, 41.2), (82.0, 43.6)], [0.1, 0.45, 0.1]), BEAK.light, 0.4)])
    up = sm([(nx - 1.5, eyy - 0.5), (nx, eyy - 1.1), (nx + 1.5, eyy - 0.5), (nx + 2.2, eyy + 2.2), (85.4, 35.1), (86.1, 36.9),
             (86.0, 39.2), (85.4, 41.5), (84.5, 43.6), (83.1, 45.6), (82.7, 44.1), (81.9, 42.5), (80.1, 40.5), (78.0, 38.9),
             (76.4, 37.6), (76.8, 35.9), (78.2, 34.5), (nx - 2.0, eyy + 1.6)], sharp=(9, 14))
    udet = [
        # le côté proche du bec dans la demi-teinte (la lumière vient d'en haut à droite)
        (sm([(76.4, 37.6), (76.8, 35.9), (78.2, 34.9), (80.0, 35.9), (81.6, 38.3), (82.9, 41.8), (83.1, 45.6), (82.7, 44.1),
             (81.9, 42.5), (80.1, 40.5), (78.0, 38.9)], sharp=(0, 6)), BEAK.shadow, 0.5),
        # la cire, plus claire, à la racine (entre les yeux), et les deux narines (celle du fond plus petite)
        (sm([(nx - 1.5, eyy - 0.5), (nx, eyy - 1.1), (nx + 1.5, eyy - 0.5), (nx + 2.1, eyy + 1.8), (nx + 1.4, eyy + 3.0), (nx, eyy + 3.4),
             (nx - 1.5, eyy + 3.0), (nx - 2.0, eyy + 1.6)]), BEAK.hi, 0.75),
        (ribbon([(nx - 1.9, eyy + 2.5), (nx - 1.2, eyy + 2.1), (nx - 0.5, eyy + 2.2)], [0.45, 0.65, 0.2]), '#8a4a1e', 0.9),
        (ribbon([(nx + 0.6, eyy + 2.2), (nx + 1.1, eyy + 2.0), (nx + 1.6, eyy + 2.3)], [0.2, 0.45, 0.3]), '#8a4a1e', 0.75),
        # l'arête éclairée, un peu à droite de la médiane, jusqu'au crochet
        (ribbon([(nx + 0.4, eyy + 3.0), (nx + 1.5, eyy + 5.6), (nx + 2.4, eyy + 8.8), (nx + 2.8, eyy + 11.2), (83.6, 44.8)],
                [0.1, 0.65, 0.75, 0.45, 0.1]), '#fffbe0', 0.8),
        # la ligne de fermeture du bec (bouche fermée) et l'ombre du côté du fond
        (ribbon([(76.4, 37.6), (78.0, 39.0), (80.1, 40.6), (82.0, 42.6), (82.7, 44.1)], [0.35, 0.6, 0.6, 0.4, 0.1]), BEAK.deep, 0.7),
        (ribbon([(86.0, 36.8), (85.7, 39.6), (84.6, 42.6)], [0.1, 0.5, 0.1]), BEAK.shadow, 0.45),
    ]
    part('beakU', up, BEAK, grad=(86, 33, 77, 43, [(0, BEAK.light), (0.5, BEAK.base), (1, '#e09a32')]),
         cel=0.7, rim=0.6, cast=1.2, ink=FINK, details=udet)
    return names


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
            lf = P['lift']
            q1, q2, q3 = (p1[0] + dx, p1[1] + dy), (p2[0] + 0.4 * dx, p2[1] + 0.4 * dy - 0.3 * abs(q) - 0.6 * lf), (p3[0], p3[1] - lf)
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
    """Les pattes d'aigle : la « culotte » de plumes (grosse cuisse emplumée qui sort de sous le ventre et finit en
    pointes de flamme), le tarse écailleux et les doigts d'un seul tenant, les serres sombres. Les pattes restent
    posées au sol (seul le corps se tasse) ; en vol (legs_up), les doigts se replient."""
    names = []
    up = P['legs_up']
    for side in ('f', 'n'):
        if side == 'f':
            dx = -1.0
            top0, ank0 = (80.2, 90.0), (80.6, 110.2)
            toes0 = [([(80.6, 111.0), (86.0, 112.4), (91.0, 113.4), (94.6, 114.4)], [4.0, 3.6, 3.1, 2.6]),
                     ([(80.0, 111.6), (83.6, 113.8), (88.0, 115.0)], [3.8, 3.3, 2.8]),
                     ([(79.6, 111.4), (76.6, 113.6), (74.4, 114.6)], [3.6, 3.0, 2.5])]
            claws0 = [((94.6, 114.4), 1, 1.0), ((88.0, 115.0), 1, 0.9), ((74.4, 114.6), -1, 0.85)]
        else:
            dx = 3.0
            top0, ank0 = (56.6, 90.0), (55.8, 110.8)
            toes0 = [([(56.2, 111.6), (60.4, 113.0), (64.6, 114.4)], [4.2, 3.6, 2.9]),
                     ([(55.6, 112.2), (58.0, 114.4), (60.6, 115.2)], [3.8, 3.3, 2.8]),
                     ([(55.2, 111.8), (50.6, 113.4), (46.6, 114.6)], [3.8, 3.2, 2.6])]
            claws0 = [((64.6, 114.4), 1, 1.0), ((60.6, 115.2), 1, 0.85), ((46.6, 114.6), -1, 0.95)]
        sh_ = lambda p: (p[0] + dx, p[1])
        F = lambda p: mapp(LIFT, sh_(p))
        top = mapp(BODY, sh_(top0))
        ank = F(ank0)
        toes, claws = [], []
        for (pts, ws), (cp, dr, cs) in zip(toes0, claws0):
            q = [F(p) for p in pts]
            if up:
                q = [rotp(p, 28 * up * (1 if p[0] > ank[0] else -1), ank) for p in q]
            toes.append((q, ws))
            cq = F(cp)
            if up:
                cq = rotp(cq, 28 * up * (1 if cq[0] > ank[0] else -1), ank)
            claws.append((cq, dr, cs, q[-2]))
        leg = bird_leg(top, ank, toes, w0=6.0, w1=4.6)
        nm = 'leg' + side
        # les grandes plaques du tarse (écailles) : arcs doux, de moins en moins visibles vers le bas
        det = []
        for k in range(3):
            t = 0.42 + 0.17 * k
            c = lerp(top, ank, t)
            det.append((ribbon([(c[0] - 2.2, c[1] - 0.3), (c[0] + 0.2, c[1] + 0.6), (c[0] + 2.4, c[1] - 0.2)], [0.1, 0.6, 0.1]), LEG.shadow, 0.45))
            det.append((ribbon([(c[0] - 1.8, c[1] - 1.0), (c[0] + 0.2, c[1] - 0.2), (c[0] + 2.0, c[1] - 0.9)], [0.1, 0.45, 0.1]), LEG.hi, 0.5))
        det.append((ribbon([(ank[0] + 1.4, ank[1] - 14), (ank[0] + 1.8, ank[1] - 7), (ank[0] + 1.4, ank[1])], [0.1, 0.9, 0.1]), LEG.hi, 0.6))
        if side == 'f':
            det.append((leg, '#4a1030', 0.22))
        fig.part(nm, leg, LEG, grad=(ank[0] + 4, top[1], ank[0] - 4, ank[1] + 4, [(0, LEG.light), (0.5, LEG.base), (1, LEG.shadow)]),
                 cel=1.0, rim=0.6, cast=1.0, details=det)
        names.append(nm)
        # la culotte de plumes : elle sort de sous le ventre, s'arrondit, et finit en trois pointes de flamme
        cx = (56.4 if side == 'n' else 80.4) + dx
        sway = 0.5 * P['amp'] * math.sin(P['ph'] - (2.0 if side == 'n' else 2.6)) - 0.04 * P['sk'] * 10
        th0 = [(cx - 3.4, 73.0), (cx + 4.6, 76.0), (cx + 6.4, 82.0), (cx + 6.2, 88.0), (cx + 4.8, 94.4), (cx + 3.0, 99.2),
               (cx + 1.4, 96.0), (cx - 0.2, 100.6), (cx - 1.8, 96.2), (cx - 3.6, 98.8), (cx - 4.8, 93.2), (cx - 6.2, 86.6),
               (cx - 6.0, 80.6)]
        th0 = [(x + (sway * (y - 90) / 10 if y > 90 else 0), y) for x, y in th0]
        thigh = sm([mapp(BODY, p) for p in th0], sharp=(5, 6, 7, 8, 9), t=0.95)
        G = [(0, '#a8242e'), (0.3, '#d23e28'), (0.7, '#f87a28'), (1, '#ffc040')] if side == 'n' else G_SKB
        tt = mapp(BODY, (cx, 78.0))
        # des plumes couchées (arcs en chevron, pointes vers le bas) : la cuisse est un paquet de plumes, pas un tissu
        tdet = []
        for (a0, a1, a2), col, op in ((((cx - 5.0, 82.4), (cx - 1.6, 86.6), (cx + 3.0, 84.0)), '#6a1236', 0.35),
                                      (((cx - 4.6, 88.6), (cx - 0.8, 92.4), (cx + 3.8, 89.6)), '#6a1236', 0.3),
                                      (((cx - 3.8, 81.2), (cx - 1.2, 84.6), (cx + 2.6, 82.6)), '#ffd060', 0.35)):
            tdet.append((ribbon([mapp(BODY, a0), mapp(BODY, a1), mapp(BODY, a2)], [0.1, 0.8, 0.1]), col, op))
        if side == 'f':
            tdet.append((thigh, '#2a0828', 0.18))
        fig.part('thigh' + side, thigh, FEA, grad=(tt[0] + 4, tt[1], tt[0] - 3, tt[1] + 22, G), cel=1.0, rim=0.5, cast=1.0,
                 ink=FINK, cast_on=[nm], details=tdet)
        names.append('thigh' + side)
        # les serres : crochets sombres au bout des doigts
        for i, (cp, dr, cs, prev) in enumerate(claws):
            a = math.atan2(cp[1] - prev[1], cp[0] - prev[0])
            ux, uy = math.cos(a), math.sin(a)
            nx, ny = -uy, ux
            s = 1.6 * cs
            base1 = (cp[0] - nx * s * 0.9 - ux * 0.6, cp[1] - ny * s * 0.9 - uy * 0.6)
            base2 = (cp[0] + nx * s * 0.9 - ux * 0.6, cp[1] + ny * s * 0.9 - uy * 0.6)
            tipc = (cp[0] + ux * s * 2.2, cp[1] + uy * s * 2.2 + 1.1 * s)
            tipc = (tipc[0], min(tipc[1], GRD + 0.4 - P['lift']) if not up else tipc[1])
            hook = (cp[0] + ux * s * 1.6, cp[1] + uy * s * 1.6 - 0.6 * s)
            sh = sm([base1, hook, tipc, (cp[0] + ux * s * 0.8, cp[1] + uy * s * 0.8 + 0.6 * s), base2], sharp=(2,), t=0.8)
            nm2 = 'claw%s%d' % (side, i)
            fig.part(nm2, sh, TALON, cel=0.5, rim=0.4, cast=0.6,
                     details=[(ellipse(hook[0], hook[1] + 0.3, 0.6, 0.3, math.degrees(a)), TALON.glint, 0.8)])
            names.append(nm2)
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
    print('visage (visage.verifier) : défauts =', verifier(fig_face, FACE_BOX) or 'aucun')
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
