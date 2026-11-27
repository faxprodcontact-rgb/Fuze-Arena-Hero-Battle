# L'oni brute (monstre du clan de Lenore, feu, « costaud » ; dessin du jeu « mon-lenore-costaud ») redessiné en
# VECTORIEL lisse, dans le style moderne de l'interface (refonte des monstres, demande du propriétaire du 27/11/2026),
# sur le modèle des héros validés : Lenore (../../heros/lenore : l'oni rouge, son chef de clan, même kanabō, même
# pagne, même corde), Taurok (../../heros/taurok : la brute, le raccord épaule / buste d'Aurelle) et Oboro (l'oni sorcier).
#
#   python3 refonte-graphique/ui-moderne/monstres/oni-brute/oni-brute.py   # → oni-brute.svg + images 512 et 160 px
#
# Même monstre que le pixel art (refonte-graphique/pixel/hd/monstres/oni-brute.txt) : un grand oni BLEU NUIT, massif et
# lent, trois quarts vers la droite, pieds nus à plat. Énorme ventre rond qui déborde sur la corde (nombril, vieille
# balafre claire), pectoraux lourds posés dessus, bosse des trapèzes ; bras énormes (gros deltoïde, avant-bras épais),
# petites jambes courtes et solides, grands pieds nus aux orteils séparés et aux ongles d'ivoire. Tête basse, avancée
# entre les épaules : mâchoire énorme, deux grandes cornes d'ivoire (la proche plus grosse), sourcils rouges
# broussailleux froncés en V, petits yeux jaunes enfoncés, gros nez large, gueule ouverte en rictus (gorge rouge
# sombre, dents, deux crocs du haut), deux grosses défenses d'ivoire qui montent de la mâchoire du bas, oreille pointue
# à l'anneau d'or. Crinière rouge en grosses mèches en flammes balayées vers l'arrière, une crête entre les cornes.
# Le poing proche serre le manche du kanabō, tenu debout tout près du corps (fer à huit pans, clous en pointe de
# diamant en rangées décalées, collier d'or, manche de fer, bague et pommeau) ; le bras lointain pend derrière le flanc,
# poing serré. Bracelets d'or aux deux poignets, pagne en peau de tigre (en taches, pas de rayures) en touffes
# pointues, grosse corde torsadée nouée côté lointain (deux bouts qui pendent).
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; les membres sont d'un seul
# tenant (épaule → coude → poignet, hanche → genou → cheville → pied) ; la racine du bras proche se fond dans le deltoïde
# du buste (méthode d'Aurelle / Taurok : outils.FigureM) ; le visage est construit avec visage.py.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp, resample  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (rot, add, lerp, hexmix, body_limb, round_limb, ik, Seg, inv, FigureM, poly_of, shape_of,  # noqa: E402
                    crpath, taper, fused, cast_off, sm_under, matmix, shape_g)
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'mon-lenore-costaud'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières claires, ombres violettes) ----------
SKIN = Mat('#a9d2ee', '#5e82c8', '#3c529c', '#272f6c', '#171744')         # la peau bleu nuit (lumières vers le turquoise)
MANE = Mat('#ffa45a', '#e4502e', '#ac2c30', '#741a34', '#460f2c')         # la crinière rouge (le rouge du chef)
IVORY = Mat('#fffcee', '#f6ead0', '#e2cfac', '#a88c7e', '#5e4248')
GOLD = Mat('#fff4b4', '#f8c640', '#d8961e', '#8e5216', '#5a2c0e', glint='#ffffff')
IRON = Mat('#e4ebfa', '#98a2c0', '#666e90', '#3c4260', '#23233a', glint='#ffffff')
TIGER = Mat('#ffd885', '#f4a83c', '#d88026', '#9a4a18', '#5a2a12')
ROPE = Mat('#fff2c0', '#ecd08c', '#bc904c', '#70482a', '#42281a')
SPOT = '#2c1418'
GORGE = '#3e0a1c'
GUMS = '#86203a'
LIDC = '#120c30'
EYE_Y, EYE_K, PUPIL = '#ffe24c', '#c8801a', '#1a0810'
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
SKIN_HOT = Mat('#ffe4b0', '#9a8cd8', '#5e4ca8', '#3a2c74', '#22184a')      # la peau éclairée par le feu (rare)
IRON_HOT = Mat('#fff6c8', '#ffb43a', '#f2701a', '#b8301a', '#6a1410', glint='#fffbe4')

GRD = 116.0        # le sol (le point « sol » du pixel art)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-1.0, 0.0, 122.0, 119.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 (le buste monte, le ventre se gonfle) ; crouch : il se tasse (genoux, pieds au sol) ; lean :
#   il se penche en avant (+) ; head : décalage de la tête ; tilt : la tête tourne ; jaw : la gueule s'ouvre (0..3) ;
#   ph : phase des mèches ; ml : retard des mèches ; pg : le pagne se balance ; blink : yeux fermés ;
#   G : le point du manche serré au milieu du poing proche ; ang : la direction poing → tête de fer ; bend : sens du
#   coude ; wr : le poignet dans le repère de la massue ; length : la massue raccourcie (vue en raccourci, en plein élan) ;
#   nsh : l'épaule proche déplacée ; rn / rf : épaules soulevées ; far / far_rot : le bras lointain ;
#   eyes : les yeux deviennent blancs de feu (0..1) ; hot : le fer chauffe (0..2).
G0 = (18.6, 89.0)                    # le poing proche sur le manche (pixel art : x = 19 − 0,1 × (90 − y))
ANG0 = -95.7                         # la massue debout, la tête en haut, un peu penchée vers l'arrière
WR0 = (7.6, 4.7)                     # le poignet proche, dans le repère de la massue (le long, en travers)
S_N = (37.0, 49.6)                   # l'épaule proche (articulation)
S_F = (101.6, 58.4)                  # l'épaule lointaine
L1, L2 = 19.4, 16.8                  # bras, avant-bras proches (jusqu'au poignet)
R_N, R_F = 11.6, 7.4                 # le rayon de la racine du bras (proche, lointain) : celui des dômes du buste
HIP = (68.0, 92.0)                   # le pivot du buste
NECK = (88.0, 60.0)                  # le pivot (et le centre d'agrandissement) de la tête
HINGE = (73.6, 49.0)                 # la charnière de la mâchoire

# Le visage (règle commune ../../heros/visage.py) : la boîte de la face (sans cornes, crinière ni oreille), dans le
# repère de la tête AVANT son agrandissement ×1,1. L'oni brute a le front bas et une mâchoire énorme : la ligne des
# yeux est haute (0,37), la gueule basse ; ses petits yeux enfoncés sont étroits (0,16). placer() donne la place des
# deux yeux (l'œil du fond un peu plus étroit), du nez (sur la médiane, ENTRE les yeux) et de la bouche (sous le nez).
FACE_BOX = (69.0, 29.0, 104.0, 61.0)
V = placer(FACE_BOX, l_oeil=0.16, y_oeil=0.37, y_nez=0.55, y_bouche=0.73)
NOSE = V['nez']
EYE_N, EYE_F = V['oeil_proche'], V['oeil_fond']
MOUTH_L, MOUTH_R = (83.4, 50.6), (99.8, 50.2)     # les coins de la gueule (centrée sous le nez)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, jaw=0.0, ph=0.0, ml=0.0, pg=0.0, blink=0.0,
            G=G0, ang=ANG0, bend=-1.0, wr=WR0, length=1.0, nsh=(0.0, 0.0), rn=0.0, rf=0.0, far=(0.0, 0.0),
            far_rot=0.0, eyes=0.0, hot=0.0, lift=0.0, shift=0.0)


def mesures():
    """Les positions RÉELLES des traits (pour visage.verifier), repère de la tête avant l'agrandissement ×1,1 : les
    yeux et le nez sont construits aux places de placer() ; la bouche = le milieu de la gueule (entre ses deux coins)."""
    return {'oeil_proche': EYE_N, 'oeil_fond': EYE_F, 'nez': NOSE,
            'bouche': ((MOUTH_L[0] + MOUTH_R[0]) / 2, 52.0, MOUTH_R[0] - MOUTH_L[0])}


def shoulders(torso0, Sn, Sf):
    """(Repris de Taurok) Le buste avec ses deux deltoïdes : un dôme du rayon de la racine du bras autour de chaque
    articulation d'épaule (repère du buste), raccordé au trapèze par une fermeture LOCALE (le creux entre le dôme et le
    trapèze est comblé, le reste du buste ne bouge pas)."""
    from shapely.geometry import Point, box
    g = poly_of(torso0)
    for S, r, rb in ((Sn, R_N, 12.0), (Sf, R_F, 6.0)):
        u = g.union(Point(S).buffer(r, 64))
        closed = u.buffer(rb, 64, join_style=1).buffer(-rb, 64, join_style=1)
        g = u.union(closed.intersection(box(S[0] - r - 10.0, S[1] - r - 12.0, S[0] + r + 10.0, S[1] + 2.0)))
    g = g.buffer(2.0, 64, join_style=1).buffer(-2.0, 64, join_style=1)      # l'aisselle : un creux arrondi
    return shape_of(g, step=0.6)


def shoulder_mask(U, S, seg, r, zone, side=1):
    """(Repris de Taurok) Le masque en dégradé de la racine du bras (outils.FigureM) : opaque à l'articulation S,
    transparent à une racine de bras de là, dans la direction du buste (qui tourne avec le bras)."""
    d = rot(seg.u, -130.0 * side)
    return (*mapp(U, (S[0] - 2.0 * d[0], S[1] - 2.0 * d[1])), *mapp(U, (S[0] + (r + 1.0) * d[0], S[1] + (r + 1.0) * d[1])), zone)


def blob(c, r, seed, k=5, flat=0.8, ang=0.0):
    """Une tache irrégulière (peau de tigre) : k bosses de rayons inégaux, couchée (flat) et tournée (ang)."""
    pts = []
    for i in range(k):
        a = 2 * math.pi * i / k + 0.6 * math.sin(seed * 3.1 + i)
        rr = r * (0.75 + 0.35 * (0.5 + 0.5 * math.sin(seed * 7.7 + i * 2.3)))
        p = (rr * math.cos(a), rr * math.sin(a) * flat)
        p = rot(p, ang)
        pts.append((c[0] + p[0], c[1] + p[1]))
    return sm(pts, t=1.0)


def cuff(c, a, L, W, bow=0.9):
    """Un bracelet d'or autour d'un avant-bras (c = son milieu, a = la direction de l'avant-bras, L = sa largeur le long
    du bras, W = sa longueur en travers) : ses deux bords sont des arcs (il fait le tour du bras, vu en perspective)."""
    h, w = L / 2, W / 2
    pts = [(-h - bow * 0.2, -w), (-h + bow * 0.5, -w * 0.5), (-h + bow, 0.0), (-h + bow * 0.5, w * 0.5), (-h - bow * 0.2, w),
           (h + bow * 0.2, w), (h + bow, w * 0.5), (h + bow * 1.2, 0.0), (h + bow, -w * 0.5), (h + bow * 0.2, -w)]
    return xf(sm(pts, sharp=(0, 4, 5, 9), t=0.7), c[0], c[1], a)


def cuff_det(c, a, L, W, bow=0.9):
    """Les reflets du bracelet : le bourrelet du haut éclairé, l'ombre du bas, un éclat."""
    h, w = L / 2, W / 2
    X = lambda sh: xf(sh, c[0], c[1], a)
    return [(X(ribbon([(-h + bow * 0.3 + 0.7, -w * 0.82), (-h + bow + 0.7, 0.0), (-h + bow * 0.3 + 0.7, w * 0.82)], [0.1, 0.9, 0.1])), GOLD.hi, 0.85),
            (X(ribbon([(h + bow * 0.3 - 0.5, -w * 0.8), (h + bow * 1.1 - 0.5, 0.0), (h + bow * 0.3 - 0.5, w * 0.8)], [0.1, 0.8, 0.1])), GOLD.shadow, 0.6),
            (X(ellipse(-h + bow + 1.1, -w * 0.35, 0.7, 0.45)), GOLD.glint, 0.9)]


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigureM(*frame, ow=ow)
    hot = P['hot']
    skin = SKIN
    iron = matmix(IRON, IRON_HOT, 0.5 * hot)

    # ---- le squelette : une matrice par groupe de morceaux ----
    ROOTM = mT(P['shift'], -P['lift'])
    dyb = P['crouch'] * 0.85
    PEL = mchain(ROOTM, mT(0, dyb))
    U = mchain(PEL, mT(P['lean'] * 0.35, 0), mR(P['lean'] * 1.1, *HIP))       # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.7 * br))                                           # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.012 * br, 70, 96))                # le ventre se gonfle
    HEAD = mchain(UC, mT(P['head'][0], P['head'][1] - 0.3 * br), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    FARM = mchain(UC, mT(P['far'][0], P['far'][1] - 0.8 * P['rf']), mR(P['far_rot'], *S_F))
    CLO = mchain(PEL, mskx(-0.05 * P['pg'], 88))

    # ======================================================================== la crinière : les mèches du dos
    # Elles naissent de la nuque et tombent sur la bosse du dos, DERRIÈRE le buste et l'épaule (avis du propriétaire
    # pour Lenore : « la mèche de la nuque passe derrière l'épaule ») ; on ne voit que leur haut, au-dessus des trapèzes.
    ph, ml = P['ph'], P['ml']
    BACK = [
        ('mb2', (70.0, 48.0), (64.0, 48.4), (57.0, 50.4), (49.0, 55.0), 10.0),
        ('mb1', (69.0, 40.0), (60.0, 37.6), (50.0, 39.4), (40.6, 46.4), 14.0),
    ]
    MG = ('lin', 92.0, 14.0, 44.0, 56.0, [(0, MANE.light), (0.3, MANE.base), (0.75, MANE.shadow), (1, MANE.deep)])
    for i, (name, p0, p1, p2, p3, w0) in enumerate(BACK):
        w = ph - 0.9 * i
        p2 = (p2[0] + 0.5 * math.sin(2 * w + 1.0), p2[1] + 0.5 * math.sin(w) + 0.5 * ml)
        p3 = (p3[0] + 0.9 * math.sin(w + 0.8) - 0.3 * ml, p3[1] + 0.8 * math.cos(w) + 1.2 * ml)
        sh = lock(p0, p1, p2, p3, w0, n=12, bulge=0.3)
        x0_, y0_, x1_, y1_ = sh.bbox()
        fig.part(name, sh, MANE, grad=MG[1:], cel=0, rim=0.75, cast=1.2, cast_on=['mb2'],
                 details=[(sm_under(sh), ('lin', 0, y0_, 0, y1_, [(0, MANE.shadow), (1, MANE.deep)]), 0.85),
                          (lock(lerp(p0, p1, 0.3), lerp(p1, p2, 0.3), lerp(p2, p3, 0.2), lerp(p2, p3, 0.7), w0 * 0.2, n=8, bulge=0.1)
                           .move(0.3 + 0.03 * w0, -0.12 * w0), MANE.light, 0.5)])

    # ======================================================================== le bras lointain (gauche), derrière le flanc
    FE, FW = (106.0, 72.6), (106.4, 82.6)
    farm = body_limb([S_F, FE, FW], [(0, 7.6, 7.6), (0.25, 7.4, 7.4), (0.5, 6.2, 6.4), (0.66, 6.6, 6.8), (1, 5.6, 5.6)], n=22)
    s1, s2 = Seg(S_F, FE), Seg(FE, FW)
    fa1 = math.degrees(math.atan2(s1.u[1], s1.u[0]))
    fig.part('farm', farm, skin, cel=1.8, rim=0.7, cast=0,
             details=[(ribbon([s1.at(0.2, 4.6), s1.at(0.55, 5.4), s1.at(0.9, 4.4)], [0.1, 2.0, 0.1]), skin.light, 0.45),
                      (ribbon([s1.at(0.1, -2.0), s1.at(0.4, 0.8), s1.at(0.5, 4.6)], [0.1, 0.9, 0.1]), skin.shadow, 0.5),
                      (ribbon([s2.at(0.0, 4.2), s2.at(0.4, 5.0), s2.at(0.8, 4.2)], [0.1, 1.6, 0.1]), skin.light, 0.4)])
    ffist = sm([(100.4, 84.0), (105.4, 83.0), (110.6, 83.6), (113.0, 86.6), (113.2, 90.6), (111.6, 94.0), (106.6, 95.2),
                (102.2, 94.4), (100.0, 90.6)])
    fd = [(sm([(105.8, 83.6), (110.4, 84.0), (112.4, 87.0), (112.2, 91.0), (110.6, 93.6), (108.8, 89.4), (107.6, 86.0)]), skin.light, 0.5)]
    for yy in (87.0, 89.9, 92.6):
        fd.append((ribbon([(108.0, yy - 0.1), (110.6, yy + 0.2), (113.0, yy - 0.2)], [0.1, 0.6, 0.1]), skin.deep, 0.5))
    for yy in (85.6, 88.5, 91.3):
        fd.append((ellipse(111.0, yy, 1.0, 0.6, -10), skin.hi, 0.45))
    fig.part('ffist', ffist, skin, cel=1.4, rim=0.6, cast=0.9, cast_on=['farm'], details=fd)
    fbc = s2.at(0.82)
    fa2 = math.degrees(math.atan2(s2.u[1], s2.u[0]))
    fig.part('fbrac', cuff(fbc, fa2, 3.6, 14.0), GOLD, cel=0.8, rim=0.6, cast=0.8, cast_on=['farm', 'ffist'],
             details=cuff_det(fbc, fa2, 3.6, 14.0))

    # ======================================================================== les jambes : hanche → genou → cheville → pied,
    # d'un seul tenant (aucune couture au genou ni à la cheville) ; les grands pieds nus restent à plat au sol
    # Le grand pied nu d'oni (talon à gauche, orteils vers l'ennemi) : une plante large et plate, trois gros orteils
    # séparés à l'avant (le gros orteil devant, le plus grand), un ongle d'ivoire au bout de chacun. Le pied et la jambe
    # sont fondus en UNE forme (un creux arrondi au cou-de-pied) : aucune couture à la cheville.
    FOOT = [(33.0, 116.4), (32.4, 113.4), (33.6, 110.2), (37.0, 108.2), (44.0, 107.2), (49.0, 108.0), (52.0, 110.6),
            (55.0, 113.0), (58.0, 114.6), (61.0, 115.4), (62.0, 116.0), (61.4, 116.4)]
    TOES = [((60.4, 113.4), 3.0), ((56.0, 111.9), 2.7), ((52.0, 111.0), 2.3)]       # du gros orteil (devant) au petit

    def leg(name, Hr, A, L1_, L2_, bend, keys, dx, k, cast_on):
        H = mapp(PEL, Hr)
        A = mapp(ROOTM, A)
        Q = lambda p: mapp(ROOTM, (33.4 + (p[0] - 33.4) * k + dx, GRD + 0.4 + (p[1] - GRD - 0.4) * k))
        sc = min(1.0, math.dist(H, A) * 1.06 / (L1_ + L2_))
        K, A2 = ik(H, A, L1_ * sc, L2_ * sc, bend)
        limb_ = body_limb([H, K, A2], keys, n=22)
        from shapely.geometry import Point
        from shapely.ops import unary_union
        fg = poly_of(sm([Q(p) for p in FOOT], sharp=(0, 11), t=0.8), 8)
        g = unary_union([poly_of(limb_, 8), fg])
        g = g.buffer(1.4 * k, 64, join_style=1).buffer(-1.4 * k, 64, join_style=1)
        # les orteils séparés : posés APRÈS l'arrondi du cou-de-pied, pour garder les creux entre eux
        g = unary_union([g] + [Point(Q(c_)).buffer(r_ * k, 40) for c_, r_ in TOES])
        g = g.buffer(0.3 * k, 32, join_style=1).buffer(-0.3 * k, 32, join_style=1)
        sh = shape_of(g, step=0.4, t=0.9)
        th, sn = Seg(H, K), Seg(K, A2)
        sa = math.degrees(math.atan2(sn.u[1], sn.u[0]))
        det = [(ribbon([sn.at(0.0, 4.4), sn.at(0.5, 5.4), sn.at(1.0, 4.6)], [0.1, 1.6, 0.1]), skin.light, 0.5),
               (ellipse(*sn.at(0.1, 4.2), 1.0, 1.8, sa - 90), skin.hi, 0.3),
               (ribbon([th.at(0.8, -6.0), sn.at(0.3, -6.4), sn.at(0.9, -6.4)], [0.1, 1.0, 0.1]), skin.deep, 0.35)]
        # le dessus du pied éclairé, la plante dans l'ombre
        det += [(ribbon([Q((40.0, 108.6)), Q((50.0, 108.8)), Q((56.0, 110.8))], [0.1, 1.0 * k, 0.1]), skin.light, 0.5),
                (ribbon([Q((34.0, 115.2)), Q((46.0, 115.8)), Q((60.0, 115.6))], [0.1, 1.1 * k, 0.1]), skin.deep, 0.45)]
        # les orteils : le dessus éclairé de chacun, le pli entre deux, l'ongle d'ivoire au bout (une griffe courte)
        nails = []
        for j, (c_, r_) in enumerate(TOES):
            cx_, cy_ = Q(c_)
            rk = r_ * k
            det += [(ellipse(cx_ - 0.2 * rk, cy_ - 0.45 * rk, 0.55 * rk, 0.3 * rk, -20), skin.hi, 0.45)]
            nails.append((sm([(cx_ + 0.2 * rk, cy_ - 0.92 * rk), (cx_ + 0.9 * rk, cy_ - 0.78 * rk), (cx_ + 1.42 * rk, cy_ - 0.02 * rk),
                              (cx_ + 1.0 * rk, cy_ + 0.28 * rk), (cx_ + 0.4 * rk, cy_ - 0.28 * rk)], sharp=(2,), t=0.8),
                          (cx_ + 0.75 * rk, cy_ - 0.62 * rk), rk, j))
        for (c1, r1), (c2, r2) in zip(TOES, TOES[1:]):
            m_ = lerp(Q(c1), Q(c2), 0.5)
            det.append((ribbon([(m_[0] + 0.2 * k, m_[1] - 1.4 * k), (m_[0] - 0.1 * k, m_[1] + 0.2 * k), (m_[0] - 0.6 * k, m_[1] + 1.8 * k)],
                               [0.1, 0.55 * k, 0.1]), skin.deep, 0.6))
        fig.part(name, sh, skin, cel=1.9, rim=0.65, cast=1.0, cast_on=cast_on, details=det)
        for nl, hc, rk, j in nails[::-1]:
            fig.part('%sn%d' % (name, j), nl, IVORY, cel=0.35, rim=0.35, cast=0.45, cast_on=[name],
                     details=[(ellipse(hc[0], hc[1], 0.3 * rk, 0.17 * rk, -25), IVORY.hi, 0.95)])
        return K, A2

    # les deux genoux plient vers l'avant (vers l'ennemi, à droite) : bend = -1 ; jambes courtes et très épaisses
    leg('fleg', (89.0, 91.0), (91.4, 106.8), 9.0, 7.6, -1,
        [(0, 8.4, 8.6), (0.5, 7.8, 7.8), (0.7, 7.6, 7.4), (1, 7.2, 7.0)], 46.4, 0.8, None)
    leg('nleg', (49.0, 90.0), (45.2, 106.6), 9.6, 8.0, -1,
        [(0, 9.4, 10.0), (0.5, 9.2, 9.4), (0.7, 9.0, 8.8), (1, 8.6, 8.4)], 0.0, 1.0, ['fleg', 'flegn0', 'flegn1', 'flegn2'])

    # ======================================================================== le pagne en peau de tigre (en taches)
    # le bas en touffes pointues : longueurs et écarts inégaux (jamais une frise régulière)
    hem = [(99.0, 99.6, 1), (97.2, 96.0, 0), (95.6, 98.2, 1), (93.2, 95.6, 0), (90.6, 101.8, 1), (87.4, 97.2, 0),
           (85.6, 99.4, 1), (83.4, 96.8, 0), (80.6, 105.0, 1), (77.0, 98.4, 0), (75.0, 103.0, 1), (72.6, 98.0, 0),
           (69.2, 106.6, 1), (65.4, 98.6, 0), (63.6, 103.2, 1), (61.0, 97.8, 0), (57.6, 102.6, 1), (54.0, 97.2, 0),
           (51.8, 99.0, 1), (49.0, 96.0, 0), (45.4, 99.6, 1), (42.0, 95.0, 0), (39.6, 96.6, 1), (37.4, 93.6, 0)]
    cpts = [(35.4, 86.8), (48.0, 88.0), (62.0, 89.4), (76.0, 89.6), (90.0, 88.4), (100.8, 86.4), (101.8, 90.4), (101.2, 95.4)] + \
           [(x, y) for x, y, _ in hem] + [(35.4, 91.4), (34.6, 89.0)]
    cloth = sm(cpts, sharp=tuple(8 + i for i, h_ in enumerate(hem) if h_[2]), t=0.8)
    cd = []
    # les taches : des taches rondes irrégulières, de tailles et d'écarts inégaux (jamais des rayures)
    SPOTS = [((40.0, 90.8), 1.3), ((45.6, 93.4), 1.0), ((51.0, 91.6), 1.5), ((56.4, 95.2), 1.1), ((61.8, 92.8), 1.4),
             ((66.0, 98.6), 1.2), ((70.4, 94.2), 1.6), ((75.4, 100.0), 1.0), ((79.6, 94.6), 1.3), ((84.6, 98.2), 1.1),
             ((88.2, 93.0), 1.5), ((93.0, 97.0), 1.0), ((97.6, 92.0), 1.2), ((57.6, 99.6), 0.8), ((81.8, 101.0), 0.8)]
    for i, (c_, r_) in enumerate(SPOTS):
        cd.append((blob(c_, r_, i + 1, k=5, flat=0.75, ang=-8 + 5 * math.sin(i)), SPOT, 0.85))
        if r_ > 1.2:
            cd.append((blob((c_[0] + 1.9 * r_, c_[1] + 0.5), r_ * 0.45, i + 20, k=4, flat=0.8), SPOT, 0.8))
    # les plis doux du cuir (le creux, l'arête claire à côté) et la lumière sur le haut
    cd += [(ribbon([(54.0, 89.4), (54.6, 94.0), (54.4, 99.0)], [0.1, 1.2, 0.1]), TIGER.shadow, 0.55),
           (ribbon([(55.4, 89.6), (56.0, 94.0), (56.0, 98.0)], [0.1, 0.8, 0.1]), TIGER.hi, 0.45),
           (ribbon([(73.4, 90.0), (73.8, 95.0), (73.6, 100.6)], [0.1, 1.3, 0.1]), TIGER.shadow, 0.5),
           (ribbon([(74.8, 90.2), (75.2, 95.0), (75.0, 99.0)], [0.1, 0.9, 0.1]), TIGER.hi, 0.45),
           (ribbon([(88.6, 89.2), (89.0, 94.0), (88.6, 99.0)], [0.1, 1.1, 0.1]), TIGER.light, 0.5),
           (ribbon([(38.4, 88.6), (60.0, 90.6), (98.0, 88.2)], [0.1, 1.4, 0.1]), TIGER.deep, 0.35)]
    fig.part('cloth', cloth, TIGER, grad=(100, 86, 40, 102, [(0, TIGER.light), (0.5, TIGER.base), (1, TIGER.shadow)]),
             cel=1.4, rim=0.7, cast=1.2, details=cd)
    # la grosse corde torsadée : elle fait le tour des hanches sous le ventre (le ventre la cache au milieu)
    rope_c = [(32.0, 88.0), (42.0, 88.4), (55.0, 89.6), (70.0, 90.0), (85.0, 89.2), (97.0, 87.2)]
    # elle passe derrière les hanches à gauche : coupée par le bord du pagne (elle tourne autour du corps)
    rope = shape_of(poly_of(limb(rope_c, [3.2, 3.2], n=18), 8).intersection(poly_of(cloth, 8).buffer(0.3)), step=0.4, t=0.85)
    rd = []
    rr_ = resample(rope_c, 30)
    for i in range(1, 30):
        c_ = rr_[i]
        rd.append((ellipse(c_[0] + 0.2, c_[1] - 0.3, 0.95, 0.42, -55), ROPE.hi, 0.55))
        rd.append((ellipse(c_[0] - 0.55, c_[1] + 0.6, 0.7, 0.3, -55), ROPE.shadow, 0.5))
    fig.part('rope', rope, ROPE, cel=0.9, rim=0.5, cast=1.0, details=rd)

    # ======================================================================== le buste (avec la bosse des trapèzes)
    torso0 = sm([(46.0, 42.2), (54.0, 39.0), (62.6, 39.4), (70.6, 43.4), (78.0, 48.4), (86.0, 51.4), (94.0, 52.4),
                 (99.0, 54.0), (101.4, 58.0), (101.6, 64.0), (100.4, 71.0), (99.6, 78.0), (98.2, 84.6), (95.0, 90.6),
                 (88.6, 94.6), (77.0, 96.6), (64.0, 96.4), (53.0, 93.8), (45.0, 89.0), (40.8, 81.6), (39.6, 72.0),
                 (40.6, 63.0), (39.8, 55.0), (41.4, 46.6)])
    Sn_t = mapp(inv(TOR), mapp(UC, (S_N[0] + P['nsh'][0], S_N[1] + P['nsh'][1] - 0.8 * P['rn'])))
    Sf_t = mapp(inv(TOR), mapp(FARM, S_F))
    torso = shoulders(torso0, Sn_t, Sf_t)
    from shapely.geometry import Point
    tgp = poly_of(torso)
    zones = [(shape_of(tgp.intersection(Point(Sn_t).buffer(R_N + 2.0, 64)), step=0.5), TOR)]
    det = [(torso, ('lin', 40, 70, 62, 66, [(0, skin.deep, 0.5), (1, skin.deep, 0)]), 1)]
    # la bosse des trapèzes, éclairée en haut (la crinière tombe derrière)
    det += [(sm([(48.0, 42.6), (55.0, 40.0), (63.0, 40.6), (70.0, 44.6), (64.0, 46.0), (56.0, 45.0), (50.0, 45.4)]), skin.light, 0.45),
            (ribbon([(50.0, 41.8), (57.0, 40.0), (64.0, 41.0), (70.0, 44.0)], [0.1, 0.9, 0.8, 0.1]), skin.hi, 0.35)]
    # les pectoraux lourds posés sur le ventre : la plaque éclairée, le pli sombre dessous (le proche plus large)
    det += [(sm([(50.0, 55.4), (58.0, 53.0), (68.0, 53.6), (75.0, 56.6), (74.6, 61.8), (66.0, 64.4), (56.0, 63.4), (50.4, 60.0)]), skin.light, 0.42),
            (sm([(78.6, 56.6), (86.0, 55.4), (95.0, 56.4), (101.0, 59.4), (100.4, 64.4), (92.0, 66.4), (83.0, 65.4), (78.4, 61.6)]), skin.hi, 0.36),
            (ribbon([(48.6, 61.4), (56.0, 64.6), (66.0, 65.6), (73.4, 63.8), (77.0, 61.0)], [0.1, 1.6, 1.8, 1.3, 0.1]), skin.deep, 0.75),
            (ribbon([(78.4, 62.4), (84.0, 66.6), (93.0, 67.6), (101.4, 64.6)], [0.1, 1.5, 1.6, 0.1]), skin.deep, 0.7),
            (ribbon([(76.6, 55.4), (77.0, 59.0), (76.6, 62.0)], [0.1, 1.2, 0.2]), skin.shadow, 0.6)]
    # l'énorme ventre rond : son dôme éclairé (en haut à droite), la masse dans l'ombre en bas à gauche, le nombril,
    # la vieille balafre claire
    det += [(ellipse(84.0, 74.0, 13.0, 9.4, -18), ('rad', 88.0, 70.0, 16.0, 16.0, [(0, skin.hi, 0.55), (0.5, skin.light, 0.35), (1, skin.light, 0)]), 1),
            (sm([(42.0, 80.0), (48.0, 88.0), (58.0, 93.0), (72.0, 95.6), (86.0, 94.0), (96.4, 89.6), (92.0, 92.6), (80.0, 96.4),
                 (64.0, 96.6), (50.0, 93.0), (43.0, 87.0)]), skin.deep, 0.5),
            (ribbon([(43.6, 68.0), (42.8, 76.0), (45.0, 84.0), (50.0, 89.6)], [0.1, 1.6, 1.6, 0.1]), skin.shadow, 0.45),
            (sm([(78.8, 79.6), (80.4, 78.8), (81.6, 79.8), (80.6, 81.6), (79.0, 81.0)]), skin.deep, 0.85),
            (ribbon([(78.6, 79.4), (80.2, 78.6), (81.8, 79.4)], [0.1, 0.5, 0.1]), skin.shadow, 0.7),
            (ribbon([(80.0, 82.2), (81.2, 82.0)], [0.4, 0.1]), skin.hi, 0.6),
            (ribbon([(58.4, 70.4), (62.4, 73.6), (66.0, 77.4), (68.6, 81.4)], [0.2, 1.3, 1.1, 0.2]), '#8db0de', 0.85),
            (ribbon([(58.8, 70.8), (62.6, 74.0), (66.2, 77.8)], [0.1, 0.45, 0.1]), skin.shadow, 0.6)]
    # l'ombre de la tête sous le menton, le flanc lointain
    det += [(sm([(74.0, 50.0), (82.0, 53.0), (92.0, 54.6), (100.0, 56.4), (96.0, 59.6), (86.0, 59.0), (78.0, 56.4)]), skin.deep, 0.4),
            (ribbon([(101.6, 66.0), (100.6, 74.0), (99.4, 82.0)], [0.1, 1.2, 0.1]), skin.shadow, 0.5)]
    tor_part = fig.part('torso', torso, skin, cel=2.2, rim=0.75, cast=1.3, details=det, occl=(skin.deep, 0.22, 3.6))

    # le noeud de la corde côté lointain, et ses deux bouts effilochés qui pendent (devant le pagne)
    end1 = sm([(93.0, 89.0), (94.8, 89.4), (94.4, 93.6), (94.0, 97.0), (94.6, 99.4), (93.4, 98.4), (92.6, 99.8), (92.6, 96.4), (92.6, 92.6)],
              sharp=(4, 5, 6))
    end2 = sm([(97.0, 89.0), (98.8, 89.2), (99.2, 92.6), (99.8, 95.6), (99.6, 97.8), (98.6, 96.8), (97.8, 97.8), (97.8, 95.0), (97.2, 92.0)],
              sharp=(4, 5, 6))
    for nm, e_, xs in (('end1', end1, 93.8), ('end2', end2, 98.2)):
        fig.part(nm, e_, ROPE, cel=0.7, rim=0.45, cast=0.9, cast_on=['cloth', 'end1'],
                 details=[(ribbon([(xs, 90.4), (xs, 94.0)], [0.7, 0.1]), ROPE.hi, 0.6),
                          (ellipse(xs - 0.1, 92.2, 0.9, 0.4, -50), ROPE.shadow, 0.5)])
    knot = sm([(93.0, 86.6), (94.6, 84.8), (96.6, 84.6), (97.8, 85.6), (99.4, 85.4), (100.2, 87.4), (99.2, 89.6),
               (96.8, 90.2), (94.2, 89.8)])
    fig.part('knot', knot, ROPE, cel=0.9, rim=0.6, cast=1.0, cast_on=['cloth', 'end1', 'end2', 'torso', 'rope'],
             details=[(ribbon([(95.8, 84.9), (96.4, 87.6), (97.4, 90.0)], [0.1, 0.9, 0.1]), ROPE.shadow, 0.75),
                      (ellipse(94.8, 86.6, 1.0, 0.7, -30), ROPE.hi, 0.85), (ellipse(98.8, 86.8, 0.9, 0.6, -30), ROPE.hi, 0.8)])

    # ======================================================================== le kanabō (repère : G, u vers la tête de fer)
    G, ang = P['G'], P['ang']
    lk = P['length']

    def C(sh):
        return xf(sh, G[0], G[1], ang, lk, 1)

    def Cp(s, t=0.0):
        return C(Shape([((s, t), [])])).subs[0][0]
    u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    nv = (-u[1], u[0])
    lit_plus = (nv[0] * 0.6 - nv[1] * 0.8) > 0          # le pan « +t » regarde-t-il la lumière ?
    sgn = 1 if lit_plus else -1
    HW0, HW1, SA, SB = 7.0, 8.4, 33.6, 79.6
    head_c = C(sm([(SA, -HW0), (SB - 1.0, -HW1), (SB, -HW1 + 1.4), (SB, HW1 - 1.4), (SB - 1.0, HW1), (SA, HW0)],
                  sharp=(0, 1, 2, 3, 4, 5), t=0.5))
    # les quatre pans visibles du fer à huit pans : le pan éclairé, deux pans du milieu, le pan dans l'ombre ; un fil
    # de lumière sur l'arête du pan éclairé
    def band_(a, b):
        return C(sm([(SA, a * HW0), (SB, a * HW1), (SB, b * HW1), (SA, b * HW0)], sharp=(0, 1, 2, 3), t=0.3))
    hd_ = [(band_(0.5 * sgn, 1.0 * sgn), iron.light, 0.85),
           (band_(0.0, 0.5 * sgn), iron.base, 0.35),
           (band_(-0.5 * sgn, -1.0 * sgn), iron.deep, 0.55),
           (C(ribbon([(SA + 1, 0.5 * HW0 * sgn), ((SA + SB) / 2, 0.5 * (HW0 + HW1) / 2 * sgn), (SB - 0.8, 0.5 * HW1 * sgn)], [0.1, 0.7, 0.1])), iron.hi, 0.85),
           (C(ribbon([(SA + 1, -0.5 * HW0 * sgn), ((SA + SB) / 2, -0.5 * (HW0 + HW1) / 2 * sgn), (SB - 0.8, -0.5 * HW1 * sgn)], [0.1, 0.5, 0.1])), iron.deep, 0.5),
           # le dessus plat (un peu plus clair : il regarde vers le haut)
           (C(sm([(SB - 1.6, -HW1 + 0.4), (SB, -HW1 + 1.4), (SB, HW1 - 1.4), (SB - 1.6, HW1 - 0.4)], sharp=(0, 1, 2, 3), t=0.3)), iron.light, 0.5)]
    if hot > 0:
        a_, b_ = Cp(SA), Cp(SB)
        hd_.append((head_c, ('lin', a_[0], a_[1], b_[0], b_[1], [(0, LAVA[4], 0.3 * hot), (1, LAVA[2], 0.5 * hot)]), 1))
    fig.part('chead', head_c, iron, cel=1.2, rim=0.8, cast=0, details=hd_)
    # les clous en pointe de diamant : rangées décalées ; ceux du bord dépassent de la silhouette
    STUDS = []
    for j in range(8):
        s_ = SA + 4.4 + j * 5.6
        STUDS.append((s_, (-1.0, -0.5, 0.0, 0.5, 1.0) if j % 2 == 0 else (-0.75, -0.25, 0.25, 0.75)))
    k_ = 0
    for s_, ts in STUDS:
        hw = HW0 + (HW1 - HW0) * (s_ - SA) / (SB - SA)
        for tt in ts:
            t_ = tt * hw * (0.97 if abs(tt) == 1 else 1)
            r = 1.35 if abs(tt) == 1 else 1.1
            st = C(sm([(s_ - r, t_), (s_, t_ - r), (s_ + r, t_), (s_, t_ + r)], t=0.6))
            cx_, cy_ = Cp(s_, t_)
            lit_ = (tt * sgn) > 0.2
            fig.part('stud%d' % k_, st, iron, cel=0.4, rim=0.35, cast=0.55, cast_on=['chead'],
                     details=[(ellipse(cx_ + 0.3, cy_ - 0.35, 0.45, 0.34), iron.glint, 0.9 if lit_ else 0.6)])
            k_ += 1
    # le collier d'or évasé, le manche de fer, la bague d'or et le pommeau rond
    collar = C(sm([(29.0, -2.6), (33.2, -HW0 - 0.8), (34.2, -HW0 - 0.4), (34.2, HW0 + 0.4), (33.2, HW0 + 0.8), (29.0, 2.6)], sharp=(0, 5), t=0.7))
    fig.part('collar', collar, GOLD, cel=0.8, rim=0.6, cast=0.9, cast_on=['chead'],
             details=[(C(ribbon([(29.8, 1.8 * sgn), (32.2, 4.6 * sgn), (33.6, 6.4 * sgn)], [0.1, 0.8, 0.1])), GOLD.hi, 0.9),
                      (C(ribbon([(33.4, -HW0 * 0.9), (33.6, 0.0), (33.4, HW0 * 0.9)], [0.1, 0.6, 0.1])), GOLD.shadow, 0.5)])
    handle = C(sm([(-11.6, -2.0), (29.4, -2.0), (29.4, 2.0), (-11.6, 2.0)], sharp=(0, 1, 2, 3), t=0.3))
    fig.part('handle', handle, iron, cel=0.6, rim=0.45, cast=0,
             details=[(C(ribbon([(-10.6, 0.9 * sgn), (10, 1.0 * sgn), (28.6, 0.9 * sgn)], [0.1, 0.6, 0.1])), iron.hi, 0.75)])
    ring_ = C(rpoly([(-12.6, -2.6), (-10.2, -2.6), (-10.2, 2.6), (-12.6, 2.6)], 0.6))
    fig.part('cring', ring_, GOLD, cel=0.45, rim=0.4, cast=0.6, details=[(C(ribbon([(-12.0, 1.8 * sgn), (-11.0, 1.9 * sgn)], [0.4, 0.4])), GOLD.hi, 0.9)])
    pom = C(sm([(-12.4, -2.2), (-13.6, -2.6), (-15.6, -2.2), (-16.4, 0.0), (-15.6, 2.2), (-13.6, 2.6), (-12.4, 2.2)]))
    pc = Cp(-14.4)
    fig.part('pommel', pom, iron, cel=0.6, rim=0.5, cast=0.6, details=[(ellipse(pc[0] + 0.6, pc[1] - 0.6, 0.7, 0.5), iron.glint, 0.9)])

    # ======================================================================== le bras proche (droit) : épaule énorme →
    # coude → poignet d'un seul tenant ; le coude placé par le squelette (le poignet suit le poing, qui tient la massue)
    Sn = mapp(UC, (S_N[0] + P['nsh'][0], S_N[1] + P['nsh'][1] - 0.8 * P['rn']))
    Snu = mapp(inv(U), Sn)
    wr = P['wr']
    W = (G[0] + u[0] * wr[0] + nv[0] * wr[1], G[1] + u[1] * wr[0] + nv[1] * wr[1])
    E, W2 = ik(Snu, W, L1, L2, P['bend'])
    arm = round_limb([Snu, E, W2], [(0, R_N, R_N + 0.2), (0.16, 10.8, 11.0), (0.4, 8.8, 9.0), (0.53, 7.8, 7.8),
                                    (0.64, 8.4, 8.6), (0.8, 7.6, 7.6), (1, 6.4, 6.4)], n=34)
    a1, a2 = Seg(Snu, E), Seg(E, W2)
    aa1 = math.degrees(math.atan2(a1.u[1], a1.u[0]))
    aa2 = math.degrees(math.atan2(a2.u[1], a2.u[0]))
    fig.masks['narm'] = shoulder_mask(U, Snu, a1, R_N, zones[0])
    ad = [
        # le deltoïde énorme éclairé (le haut de l'épaule), sa limite douce sur le bras
        (ribbon([a1(-9.6, 4.6), a1(-11.4, -1.6), a1(-9.0, -7.6), a1(-2.4, -10.8)], [0.2, 3.6, 3.2, 0.3]), skin.light, 0.55),
        (ribbon([a1(-10.2, 5.4), a1(-11.4, 1.0), a1(-10.0, -4.4)], [0.1, 1.5, 0.1]), skin.hi, 0.45),
        (ribbon([a1.at(0.2, -9.0), a1.at(0.4, -2.4), a1.at(0.34, 7.8)], [0.1, 1.1, 0.1]), skin.shadow, 0.45),
        # le biceps devant (éclairé), le triceps dans l'ombre
        (ellipse(*a1.at(0.62, 3.6), 3.4, 7.2, aa1 - 90), skin.light, 0.16),
        (ribbon([a1.at(0.5, 7.0), a1.at(0.68, 7.8), a1.at(0.88, 6.8)], [0.1, 1.0, 0.1]), skin.hi, 0.3),
        # l'avant-bras épais : le gros muscle près du coude éclairé, la ligne du cubitus dans l'ombre
        (ribbon([a2.at(0.05, 4.4), a2.at(0.35, 5.6), a2.at(0.75, 4.6)], [0.1, 2.2, 0.1]), skin.light, 0.4),
        (ribbon([a2.at(0.15, -5.0), a2.at(0.55, -5.6), a2.at(0.9, -4.4)], [0.1, 1.0, 0.1]), skin.deep, 0.35),
    ]
    fig.part('narm', arm, skin, cel=2.0, rim=0.75, cast=1.4,
             cast_on=['torso', 'cloth', 'rope', 'nleg', 'chead', 'collar', 'handle', 'cring', 'pommel'] + ['stud%d' % i for i in range(k_)],
             details=ad)
    # le bracelet d'or au poignet, en travers de l'avant-bras (il cache le raccord du poing)
    bw = add(W2, a2.u, -3.2)
    fig.part('nbrac', cuff(bw, aa2, 3.4, 14.6), GOLD, cel=0.7, rim=0.6, cast=0.9, details=cuff_det(bw, aa2, 3.4, 14.6))

    # ======================================================================== la tête
    ja = P['jaw'] * 2.8

    def J(p, w=1.0):
        """Un point de la mâchoire du bas, qui tourne autour de la charnière quand la gueule s'ouvre."""
        if not ja:
            return p
        r = rot((p[0] - HINGE[0], p[1] - HINGE[1]), ja * w)
        return (HINGE[0] + r[0], HINGE[1] + r[1])

    head0 = sm([(70.6, 34.6), (73.6, 30.4), (79.0, 27.6), (86.0, 26.6), (93.0, 27.0), (98.8, 29.2), (102.4, 32.6),
                (104.0, 36.6), (103.4, 40.4), (103.8, 44.6), (104.2, 48.8), J((103.8, 53.0)), J((102.0, 57.0)),
                J((98.2, 60.2)), J((92.4, 61.8)), J((84.4, 61.2)), J((77.6, 58.6), 0.6), (72.8, 54.6), (69.8, 49.2),
                (68.8, 43.0), (69.2, 38.0)])
    # l'oreille pointue (couchée vers l'arrière) SORT du crâne : une seule forme avec la tête, sa racine s'évase dans le
    # crâne par deux creux arrondis (comme l'oreille de Taurok) ; son creux et son ombre sont peints dans la tête
    from shapely.geometry import box as _box
    ear = sm([(71.0, 37.6), (68.4, 36.8), (64.6, 34.2), (60.4, 30.6), (61.6, 35.4), (63.6, 40.6), (66.0, 45.0),
              (68.6, 47.6), (71.2, 47.0)], sharp=(3,))
    g_u = poly_of(head0).union(poly_of(ear))
    g_c = g_u.buffer(1.8, 64, join_style=1).buffer(-1.8, 64, join_style=1)
    head = shape_of(g_u.union(g_c.intersection(_box(64.0, 33.0, 72.0, 50.0))), step=0.45)
    ear_poly = poly_of(ear)
    hd = []
    # les plans : le côté (vers l'oreille) dans l'ombre, le front et le plan de face éclairés
    hd += [(sm([(69.4, 37.0), (73.4, 37.6), (76.4, 42.0), (77.6, 48.0), (78.6, 54.4), J((80.0, 60.4)), J((77.6, 58.6), 0.6),
                (72.8, 54.6), (69.8, 49.2)]), skin.shadow, 0.5),
           (sm([(84.0, 27.6), (93.0, 27.6), (99.0, 30.0), (101.0, 33.4), (94.0, 33.6), (86.0, 32.6)]), skin.hi, 0.35),
           (sm([(98.6, 41.6), (103.8, 41.0), (104.4, 45.6), (104.6, 48.6), (100.6, 48.0), (99.0, 45.0)]), skin.light, 0.55)]
    # l'oreille : le creux (pavillon) qui s'enfonce vers la racine, le bord haut éclairé, l'ombre douce sous elle
    hd += [(sm([(69.8, 39.4), (66.6, 37.4), (62.8, 33.6), (63.8, 37.6), (65.6, 41.6), (67.8, 44.6), (69.8, 45.0)], sharp=(2,)),
            ('lin', 70, 40, 63, 36, [(0, skin.shadow), (0.5, skin.deep), (1, '#4a2a6a')]), 0.7),
           (ribbon([(61.0, 31.4), (64.6, 34.0), (68.4, 36.4)], [0.1, 0.7, 0.1]), skin.light, 0.65),
           (ribbon([(66.4, 46.0), (69.6, 47.8), (72.6, 48.4)], [0.1, 0.8, 0.1]), skin.deep, 0.35)]
    # le gros nez large de l'oni, SUR la médiane entre les deux yeux (sa base en NOSE) : l'arête qui descend d'entre les
    # sourcils, le gros bout rond éclairé, les deux ailes larges, les narines (la proche plus grande), l'ombre dessous
    nx, ny = NOSE
    hd += [(sm([(nx - 0.4, ny - 6.6), (nx - 1.8, ny - 3.8), (nx - 3.2, ny - 1.0), (nx - 1.2, ny - 0.6), (nx + 0.4, ny - 3.4)]), skin.shadow, 0.45),
           (ribbon([(nx - 3.6, ny + 1.6), (nx + 0.8, ny + 2.4), (nx + 4.8, ny + 1.6)], [0.1, 1.0, 0.1]), skin.deep, 0.55),
           (ellipse(nx - 2.5, ny + 0.2, 1.9, 1.6, 0), skin.base, 0.95),
           (ellipse(nx + 3.4, ny + 0.1, 1.5, 1.4, 0), skin.base, 0.9),
           (ribbon([(nx - 3.8, ny - 0.8), (nx - 4.2, ny + 0.6), (nx - 3.0, ny + 1.6)], [0.1, 0.7, 0.1]), skin.deep, 0.6),
           (ribbon([(nx + 4.6, ny - 0.7), (nx + 4.9, ny + 0.5), (nx + 4.2, ny + 1.3)], [0.1, 0.5, 0.1]), skin.deep, 0.5),
           (ellipse(nx + 0.6, ny - 0.8, 3.8, 2.9, 0), skin.shadow, 0.55),
           (ellipse(nx + 0.9, ny - 1.3, 3.4, 2.6, 0), skin.light, 0.95),
           (ellipse(nx + 1.9, ny - 2.2, 1.4, 0.85, 18), skin.hi, 0.95),
           (ellipse(nx - 1.2, ny + 1.0, 1.1, 0.55, 12), LIDC, 0.9),
           (ellipse(nx + 2.8, ny + 1.0, 0.8, 0.45, -12), LIDC, 0.85)]
    # les orbites creusées sous l'arcade (les petits yeux enfoncés)
    hd += [(ellipse(EYE_N[0] - 0.2, EYE_N[1] + 0.2, EYE_N[2] * 0.78, 2.6, -4), skin.deep, 0.6),
           (ellipse(EYE_F[0] + 0.1, EYE_F[1] + 0.2, EYE_F[2] * 0.8, 2.4, 4), skin.deep, 0.55)]

    # les petits yeux jaunes : même ligne, même dessin (coin extérieur haut, coin intérieur bas : le regard furieux),
    # le lointain un peu plus étroit (largeurs de placer())
    def eye_shape(E, outer_left):
        ex, ey, ew = E
        pts = [(-0.5, -1.0), (0.0, -1.0), (0.5, 0.1), (0.3, 1.0), (-0.17, 1.05), (-0.42, 0.3)]
        if not outer_left:
            pts = [(-u_, v_) for u_, v_ in pts]
        return sm([(ex + u_ * ew, ey + v_) for u_, v_ in pts], sharp=(0, 2))
    eyeN = eye_shape(EYE_N, True)
    eyeF = eye_shape(EYE_F, False)
    eh = P['eyes']
    if eh > 0.05 and P['blink'] <= 0.5:
        for (cx, cy), rr in ((EYE_N[:2], 4.6), (EYE_F[:2], 3.8)):
            hd.append((ellipse(cx, cy, rr, rr * 0.7), ('rad', cx, cy, rr, rr * 0.7, [(0, LAVA[1], 0.8 * eh), (1, LAVA[3], 0)]), 1))
    for e, (cx, cy), pr in ((eyeN, EYE_N[:2], 1.0), (eyeF, EYE_F[:2], EYE_F[2] / EYE_N[2])):
        if P['blink'] > 0.5:
            hd += [(e.scale(1.12, 1.3, cx, cy), skin.deep, 0.75), (e, skin.shadow, 1),
                   (ribbon([(cx - 2.8 * pr, cy - 0.1), (cx, cy + 0.6), (cx + 2.6 * pr, cy + 0.1)], [0.1, 0.6, 0.1]), LIDC, 0.9)]
        else:
            yc = ('rad', cx + 0.4, cy - 0.3, 3.2, 1.9, [(0, '#fffbe4'), (0.4, '#fff2a0'), (1, LAVA[1])]) if eh > 0.5 else \
                 ('rad', cx + 0.4, cy - 0.3, 3.2, 1.9, [(0, '#fff6a8'), (0.5, EYE_Y), (1, '#f2b830')])
            hd += [(e.scale(1.16, 1.42, cx - 0.1, cy), LIDC, 0.92), (e, yc, 1),
                   (ribbon([(cx - 2.6 * pr, cy + 0.8), (cx, cy + 1.1), (cx + 2.4 * pr, cy + 0.8)], [0.1, 0.45, 0.1]), EYE_K, 0.7)]
            if eh <= 0.5:
                hd += [(ellipse(cx + 1.0 * pr, cy + 0.05, 0.6 * pr, 0.82), PUPIL, 1),
                       (ellipse(cx + 1.25 * pr, cy - 0.35, 0.26 * pr, 0.24), '#ffffff', 1)]
    # l'arête du nez, claire, qui descend d'entre les yeux
    hd += [(ribbon([(nx - 0.3, ny - 7.4), (nx + 0.1, ny - 5.4), (nx + 0.8, ny - 3.4)], [0.4, 1.3, 0.3]), skin.light, 1),
           (ribbon([(nx, ny - 7.0), (nx + 0.3, ny - 5.4), (nx + 0.9, ny - 3.8)], [0.1, 0.55, 0.1]), skin.hi, 0.6)]
    # les plis de colère au front, entre les sourcils (sur la médiane)
    mx = V['mediane']
    hd += [(ribbon([(mx(33.0) - 0.6, 33.0), (mx(35.0) - 0.2, 35.0), (mx(37.0) + 0.2, 37.0)], [0.1, 0.9, 0.1]), skin.deep, 0.6),
           (ribbon([(mx(31.0) - 6.0, 31.6), (mx(31.0), 30.8), (mx(31.0) + 6.0, 31.4)], [0.1, 0.8, 0.1]), skin.shadow, 0.5),
           (ribbon([(mx(30.2) - 5.6, 30.8), (mx(30.2), 30.0), (mx(30.2) + 5.6, 30.6)], [0.1, 0.5, 0.1]), skin.hi, 0.45)]
    # la pommette sous l'œil proche ; les plis du rictus qui descendent des ailes du nez aux coins de la gueule
    hd += [(ribbon([(78.6, 44.0), (83.0, 43.8), (87.4, 44.6)], [0.1, 1.2, 0.1]), skin.light, 0.6),
           (ribbon([(nx - 4.2, ny - 0.2), (nx - 5.6, ny + 1.4), (nx - 7.2, ny + 2.8), (MOUTH_L[0] - 0.6, MOUTH_L[1] + 0.6)], [0.1, 1.0, 0.9, 0.1]), skin.deep, 0.55),
           (ribbon([(nx + 5.0, ny - 0.2), (nx + 6.4, ny + 1.6), (MOUTH_R[0] + 0.4, MOUTH_R[1] + 0.2)], [0.1, 0.7, 0.1]), skin.deep, 0.45)]
    # la gueule ouverte en rictus : la gorge rouge sombre, les gencives, les dents du haut et deux crocs, les dents du bas
    up_edge = [MOUTH_L, (86.4, 49.6), (91.6, 49.3), (96.6, 49.4), MOUTH_R]
    lo_edge = [J((99.6, 51.4)), J((96.6, 53.6)), J((91.6, 54.4)), J((86.4, 53.9)), J((83.6, 52.0))]
    mouth = sm(up_edge + lo_edge, sharp=(0, 4), t=0.8)
    mc = lerp(up_edge[2], lo_edge[2], 0.5)
    hd += [(mouth.scale(1.04, 1.14, mc[0], mc[1]), LIDC, 0.95),
           (mouth, ('rad', mc[0] + 1, mc[1] + 0.8, 8.4, 3.6, [(0, '#7a1a30'), (0.6, GORGE), (1, '#24061a')]), 1)]
    tongue_ = sm([J((86.4, 53.6)), J((90.4, 52.2)), J((95.4, 52.4)), J((97.0, 53.2)), J((91.4, 54.2))])
    hd += [(tongue_, '#a02a40', 0.75)]
    hd += [(ribbon([(84.6, 50.2), (89.0, 49.7), (94.6, 49.7), (98.8, 50.2)], [0.4, 1.6, 1.6, 0.4]), IVORY.base, 1),
           (ribbon([(85.0, 50.0), (89.0, 49.55), (94.6, 49.55), (98.4, 49.9)], [0.2, 0.6, 0.6, 0.2]), IVORY.hi, 0.9)]
    for xg in (88.4, 91.2, 94.0, 96.4):
        hd.append((ribbon([(xg, 49.6), (xg - 0.1, 50.8)], [0.35, 0.1]), IVORY.shadow, 0.65))
    # les deux crocs du haut (le proche plus gros)
    hd += [(sm([(86.0, 50.0), (88.6, 49.8), (87.4, 53.2)], sharp=(0, 1, 2), t=0.7), IVORY.base, 1),
           (sm([(87.4, 50.0), (88.6, 49.8), (87.4, 53.0)], sharp=(0, 1, 2), t=0.7), IVORY.hi, 0.8),
           (sm([(95.4, 49.9), (97.4, 50.0), (96.2, 52.6)], sharp=(0, 1, 2), t=0.7), IVORY.base, 1),
           (sm([(96.4, 49.9), (97.4, 50.0), (96.2, 52.4)], sharp=(0, 1, 2), t=0.7), IVORY.hi, 0.7)]
    lt = [J(p) for p in [(87.4, 53.4), (91.6, 54.0), (96.4, 53.4)]]
    hd += [(ribbon(lt, [0.3, 1.3, 0.3]), IVORY.shadow, 1)]
    # les lèvres : la lèvre du haut sombre au-dessus des dents, la lèvre du bas éclairée, l'énorme menton éclairé
    hd += [(ribbon([MOUTH_L, (86.4, 48.6), (91.6, 48.3), (96.6, 48.4), (MOUTH_R[0] + 0.2, MOUTH_R[1] - 0.6)], [0.1, 0.9, 1.0, 0.8, 0.1]), skin.deep, 0.6),
           (ribbon([J((84.4, 55.2)), J((91.6, 56.0)), J((99.0, 54.6))], [0.1, 1.1, 0.1]), skin.light, 0.65),
           (sm([J((88.0, 57.0)), J((98.6, 56.2)), J((101.8, 55.8)), J((100.6, 58.6)), J((93.0, 60.0)), J((88.4, 59.0))]), skin.hi, 0.35),
           (ribbon([J((76.4, 57.6)), J((84.0, 60.4)), J((94.0, 61.0))], [0.1, 0.9, 0.1]), skin.deep, 0.45)]
    # les défenses sortent de la gueule : leur racine est plantée dans la gencive, au coin de la lèvre du bas
    hd += [(ellipse(*J((85.4, 53.4)), 2.4, 1.2, -8), LIDC, 0.75),
           (ellipse(*J((85.4, 53.2)), 2.0, 0.9, -8), GUMS, 1),
           (ellipse(*J((98.0, 52.6)), 1.7, 0.9, -12), LIDC, 0.7),
           (ellipse(*J((98.0, 52.5)), 1.35, 0.7, -12), GUMS, 1)]
    # l'ombre douce que l'oreille pose sur la joue
    hd += [(sm([(70.8, 46.6), (73.4, 47.4), (75.0, 50.0), (72.6, 50.4), (70.4, 48.6)]), skin.deep, 0.3)]
    fig.part('head', head, skin, grad=(104, 30, 70, 58, [(0, skin.light), (0.5, skin.base), (1, skin.shadow)]),
             cel=1.4, rim=0.65, cast=1.5, details=hd,
             cast_on=[q.name for q in fig.parts if q.name not in ('mb1', 'mb2', 'torso')])
    # l'ombre portée de la tête sur le buste est peinte DANS le buste (même décalages que l'outil)
    to_tor = inv(TOR)
    for (dx_, dy_), op_ in (((-1.5 * 0.55, 1.5 * 1.25), 0.2), ((-1.5 * 0.3, 1.5 * 0.6), 0.28)):
        sh_ = head.map(lambda q: mapp(to_tor, add(mapp(HEAD, q), (dx_, dy_))))
        tor_part.details.append((sh_, '#2a0f55', op_))
    # les deux grosses défenses d'ivoire qui montent de la mâchoire du bas (la proche plus grosse), devant la lèvre
    tN = sm([J(p) for p in [(83.8, 53.6), (84.0, 50.6), (84.6, 47.6), (86.0, 44.6), (86.8, 47.6), (87.0, 50.8), (87.0, 53.5), (85.4, 54.2)]], sharp=(3,))
    fig.part('tuskN', tN, IVORY, cel=0.7, rim=0.55, cast=0.8, cast_on=['head'],
             details=[(ribbon([J(p) for p in [(86.2, 53.0), (86.2, 49.6), (86.2, 46.6)]], [0.7, 0.5, 0.1]), IVORY.hi, 0.9),
                      (ribbon([J(p) for p in [(84.4, 53.4), (84.6, 51.0)]], [0.6, 0.1]), IVORY.shadow, 0.6)])
    tF = sm([J(p) for p in [(97.0, 53.0), (97.0, 50.6), (97.6, 48.0), (98.8, 45.6), (99.6, 48.2), (99.6, 50.8), (99.4, 52.9), (98.2, 53.4)]], sharp=(3,))
    fig.part('tuskF', tF, IVORY, cel=0.6, rim=0.5, cast=0.7, cast_on=['head'],
             details=[(ribbon([J(p) for p in [(99.0, 52.6), (99.0, 49.6), (98.9, 46.6)]], [0.6, 0.45, 0.1]), IVORY.hi, 0.85)])

    # ---- les sourcils rouges broussailleux froncés en V (le bout intérieur plus bas, vers le nez) : deux grosses touffes
    # arrondies, de la crinière, le dessus éclairé ----
    browN = sm([(74.4, 38.8), (75.2, 36.4), (77.6, 35.2), (80.4, 35.0), (83.4, 35.6), (86.6, 37.0), (89.4, 38.8),
                (90.2, 40.6), (87.6, 40.0), (84.0, 39.0), (80.0, 38.6), (76.6, 39.6)], sharp=(0, 7))
    browF = sm([(93.2, 40.6), (93.6, 38.8), (96.0, 37.2), (99.0, 35.8), (101.8, 35.0), (104.0, 35.0), (105.2, 36.2),
                (104.2, 37.8), (101.6, 38.4), (98.4, 39.2), (95.6, 40.4)], sharp=(0, 5))
    for nm, sh, gx in (('browN', browN, 82.0), ('browF', browF, 99.0)):
        fig.part(nm, sh, MANE, grad=(gx + 4, 34.8, gx - 3, 40.4, [(0, MANE.light), (0.5, MANE.base), (1, MANE.shadow)]),
                 cel=0.8, rim=0.55, cast=0.9, cast_on=['head'],
                 details=[(ribbon([(gx - 5.5, 37.4), (gx, 35.9), (gx + 5.0, 36.6)] if nm == 'browN' else
                                  [(gx - 4.0, 38.4), (gx, 36.6), (gx + 4.6, 35.6)], [0.1, 0.7, 0.1]), MANE.hi, 0.7),
                          (ribbon([(gx - 4.0, 39.0), (gx, 38.6), (gx + 4.0, 39.4)] if nm == 'browN' else
                                  [(gx - 4.0, 39.8), (gx, 38.8), (gx + 3.6, 37.8)], [0.1, 0.6, 0.1]), MANE.deep, 0.5)])

    # ======================================================================== la crinière qui naît du crâne
    # UNE masse fondue, peinte devant la tête : la calotte (racine derrière les cornes, puis derrière l'oreille jusqu'à
    # la nuque) et les mèches hautes qui en partent, en flammes balayées vers l'arrière, et la crête entre les cornes.
    # Les couleurs des mèches n'apparaissent qu'après leur racine (fondu) : aucune ligne entre le crâne et la crinière.
    # L'oreille passe devant (elle est découpée dans la masse).
    LOCKS = [
        ('mc', (90.2, 29.4), (91.0, 24.0), (89.0, 18.6), (85.6, 14.0), 7.6),     # la crête entre les cornes
        ('m1', (83.6, 25.8), (78.0, 19.4), (70.4, 17.0), (62.8, 19.0), 9.4),
        ('m2', (78.0, 27.8), (70.0, 23.4), (61.4, 23.6), (53.8, 28.4), 11.0),
        ('m3', (72.6, 32.6), (64.4, 30.4), (56.0, 32.6), (47.0, 38.6), 11.6),
        ('m4', (69.4, 40.0), (63.0, 40.4), (57.4, 44.0), (51.6, 49.4), 8.2),
    ]
    strands = []
    for i, (name, p0, p1, p2, p3, w0) in enumerate(LOCKS):
        k = 0.5 + 0.12 * i
        w = ph - 0.8 * i
        p2 = (p2[0] + 0.4 * k * math.sin(2 * w + 1.0), p2[1] + 0.6 * k * math.sin(w) + 0.4 * ml)
        p3 = (p3[0] + 0.8 * k * math.sin(w + 0.8) - 0.3 * ml, p3[1] + 0.9 * k * math.cos(w) + 1.0 * ml)
        sh = lock(p0, p1, p2, p3, w0, n=12, bulge=0.3)
        strands.append((name, sh, p0, p1, p2, p3, w0))
    # la racine sur le front : une ligne douce, quelques petites pointes arrondies, une pointe sur la médiane
    scalp = sm([(99.6, 29.8), (98.0, 29.0), (96.6, 30.4), (94.8, 29.4), (93.2, 30.6), (91.8, 31.6), (90.6, 30.0),
                (88.6, 30.6), (86.6, 29.8), (84.6, 31.0), (81.8, 31.0), (78.8, 31.8), (76.0, 33.0), (73.6, 35.4), (72.0, 37.6), (71.4, 41.0), (71.6, 45.4),
                (72.2, 48.8), (68.8, 50.4), (64.6, 47.4), (60.6, 41.0), (60.0, 33.8), (63.4, 27.6), (69.6, 23.4),
                (78.0, 21.6), (88.0, 21.8), (95.0, 24.0), (99.0, 26.4)], sharp=(2, 5, 7), t=0.85)
    mass0 = fused([scalp] + [q[1] for q in strands])
    mass = shape_g(poly_of(mass0, 8).difference(ear_poly.buffer(0.15)))
    hair = [(mass, ('rad', 92.0, 18.0, 36.0, 36.0, [(0, '#ff7a44'), (0.3, MANE.base), (0.72, MANE.shadow), (1, MANE.deep)]), 1),
            # le volume du crâne chevelu : la bosse éclairée en haut à droite, l'ombre douce vers la nuque
            (sm([(74.0, 24.6), (82.0, 22.6), (90.0, 22.8), (95.0, 25.0), (90.0, 25.6), (82.0, 25.4), (76.0, 26.8)]), MANE.light, 0.4),
            (sm([(61.0, 36.0), (63.6, 38.0), (65.6, 44.0), (68.6, 49.4), (64.6, 47.4), (60.8, 41.0)]), MANE.deep, 0.45)]
    head_poly = poly_of(head0, 8).buffer(0.25)
    for name, sh, p0, p1, p2, p3, w0 in strands:
        L_ = math.dist(p0, p3)
        start, fdd = min(0.3, 1.5 / L_), min(0.5, 6.0 / L_)

        def faded(stops, kk=1.0, fd=fdd, start=start):
            def col_at(o):
                for (o1, c1), (o2, c2) in zip(stops, stops[1:]):
                    if o1 <= o <= o2:
                        return hexmix(c1, c2, (o - o1) / ((o2 - o1) or 1))
                return stops[-1][1] if o > stops[-1][0] else stops[0][1]
            out = [(0, col_at(0), 0.0)]
            for j in range(7):
                o = start + (fd - start) * j / 6
                u_ = j / 6
                out.append((round(o, 4), col_at(o), round(kk * u_ * u_ * (3 - 2 * u_), 3)))
            return out + [(o, c_, kk) for o, c_ in stops if o > fd]
        ax = (p0[0], p0[1], p3[0], p3[1])
        for (dx, dy), op in (((-0.66, 1.5), 0.2), ((-0.36, 0.72), 0.28)):
            sh_ = cast_off(sh, dx, dy, head_poly.buffer(1.8))
            if sh_:
                hair.append((sh_, ('lin',) + ax + (faded([(0, '#2a0f55'), (1, '#2a0f55')], op / 0.28),), 0.28))
        hair.append((sm_under(sh), ('lin',) + ax + (faded([(0, MANE.shadow), (1, MANE.deep)]),), 0.85))
        hair.append((lock(lerp(p0, p1, 0.3), lerp(p1, p2, 0.3), lerp(p2, p3, 0.2), lerp(p2, p3, 0.75), w0 * 0.22, n=8, bulge=0.1)
                     .move(0.3 + 0.03 * w0, -0.12 * w0), ('lin',) + ax + (faded([(0, MANE.light), (1, MANE.light)], 0.6),), 1))
    # l'oreille passe devant : son ombre douce sur la crinière
    e_sh = cast_off(ear, -0.9, 1.4)
    if e_sh:
        hair.append((e_sh, '#2a0f55', 0.3))
    # le liseré de lumière : seulement sur le bord extérieur de la crinière (jamais sur la racine, sur la peau)
    from shapely import affinity
    mp = poly_of(mass, 8)
    rim_ = shape_g(mp.difference(affinity.translate(mp, -0.6, 0.8)).difference(head_poly).difference(ear_poly.buffer(1.6)), min_area=0.02)
    if rim_:
        hair.append((rim_, MANE.hi, 0.8))
    fig.part('mane', mass, MANE, cel=0, rim=0, cast=0, details=hair)
    ring = ellipse(68.0, 49.6, 1.7, 1.95).hole(ellipse(68.1, 49.7, 0.85, 1.05))
    fig.part('ering', ring, GOLD, cel=0.4, rim=0.4, cast=0.5, cast_on=['head', 'mane'],
             details=[(ellipse(69.0, 48.6, 0.5, 0.35, -30), GOLD.glint, 0.9)])

    # ---- les cornes d'ivoire : la proche plus grosse ; leur base s'enfonce dans la peau devant la racine de la
    # crinière. La corne du fond est la MÊME corne (même forme, en miroir par rapport à la médiane du crâne), un peu
    # plus courte (×0,9) : on voit bien les deux ----
    HORN_N = [(81.0, 31.4), (80.2, 27.0), (78.6, 21.6), (76.6, 16.4), (74.4, 11.0)]
    HB_F = (96.2, 31.6)

    def far(pts):
        b0 = HORN_N[0]
        return [(HB_F[0] - (x - b0[0]) * 0.9, HB_F[1] + (y - b0[1]) * 0.9) for x, y in pts]
    hornF = taper(crpath(far(HORN_N), 30), 6.4, 0.3, tip='sharp', wmid=4.6)
    fig.part('hornF', hornF, IVORY, grad=(101, 18, 93, 28, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=0.9, rim=0.7, cast=1.0, cast_on=['head', 'mane'],
             details=[(ribbon(far([(81.8, 29.4), (81.4, 25.0), (79.6, 19.4), (76.8, 13.6)]), [0.2, 1.0, 0.7, 0.1]), IVORY.deep, 0.35),
                      (ribbon(far([(79.4, 29.0), (78.6, 24.4), (77.0, 19.0), (75.4, 14.4)]), [0.2, 0.9, 0.6, 0.1]), IVORY.hi, 0.75),
                      (sm(far([(77.4, 29.2), (84.4, 29.0), (84.6, 31.8), (81.0, 32.8), (77.4, 32.0)])), IVORY.deep, 0.3)])
    hornN = taper(crpath(HORN_N, 30), 7.2, 0.3, tip='sharp', wmid=5.2)
    fig.part('hornN', hornN, IVORY, grad=(83, 18, 74, 28, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=1.0, rim=0.8, cast=1.2, cast_on=['head', 'mane', 'hornF'],
             details=[(ribbon([(82.2, 29.0), (81.6, 24.6), (79.8, 19.0), (77.2, 13.4)], [0.2, 1.1, 0.8, 0.1]), IVORY.hi, 0.8),
                      (sm([(77.2, 29.2), (84.8, 29.0), (85.0, 31.8), (81.0, 33.0), (77.2, 32.0)]), IVORY.deep, 0.35)])

    # ======================================================================== le poing proche, serré sur le manche :
    # le dos de la main du côté du poignet, quatre gros doigts en rouleaux qui passent DEVANT le manche (un pli d'ombre
    # entre deux, l'auriculaire plus petit), le pouce replié par-dessus l'index (du côté de la tête de massue)
    # Repère du poing : s le long du manche (vers la tête de fer), t en travers (vers le poignet). Quatre doigts en
    # rouleaux empilés le long du manche (l'index en haut, l'auriculaire en bas, plus petit) passent DEVANT le manche,
    # leur bout replié du côté opposé au poignet ; le dos de la main (côté poignet) est éclairé ; le pouce part du dos
    # de la main et se replie par-dessus l'index.
    # le poing se retourne (en miroir le long du manche) quand le poignet passe de l'autre côté du manche : le dos de
    # la main reste toujours du côté du poignet, les doigts de l'autre
    fl_ = 1.12 if P['wr'][1] >= 0 else -1.12

    def F(sh):
        return xf(sh, G[0], G[1], ang, 1.12, fl_)

    def Fp(s_, t_):
        return F(Shape([((s_, t_), [])])).subs[0][0]
    fist = F(sm([(7.0, -4.6), (7.8, -0.6), (7.4, 3.6), (6.0, 7.0), (2.4, 8.4), (-2.6, 8.2), (-6.2, 6.4), (-7.6, 2.4),
                 (-7.4, -2.6), (-6.0, -6.0), (-3.0, -7.4), (1.0, -7.6), (4.6, -7.2), (6.4, -6.2)]))
    fdet = [(F(sm([(6.8, 3.0), (7.2, 0.0), (6.0, 7.0), (2.4, 8.4), (-2.6, 8.2), (-6.0, 6.4), (-5.0, 3.6), (0.0, 2.8), (4.0, 2.8)])),
             skin.light, 0.45),
            (F(ribbon([(5.6, 6.6), (1.0, 7.6), (-4.0, 7.2)], [0.1, 0.9, 0.1])), skin.hi, 0.5)]
    ROLLS = [(3.7, 7.2, -7.0, 2.8), (0.25, 3.7, -7.4, 2.6), (-3.2, 0.25, -7.2, 2.4), (-6.6, -3.2, -6.2, 2.0)]
    for i_, (s0, s1, t0, t1) in enumerate(ROLLS):
        rl = F(rpoly([(s1 - 0.2, t0 + 0.6), (s1 - 0.2, t1), (s0 + 0.2, t1), (s0 + 0.2, t0 + 0.6)], [1.4, 1.0, 1.0, 1.4]))
        fdet += [(rl, ('lin', *Fp(s1, 0), *Fp(s0, 0), [(0, skin.light), (0.55, skin.base), (1, skin.shadow)]), 1),
                 (F(ribbon([(s1 - 0.6, t0 + 1.4), (s1 - 0.75, (t0 + t1) / 2), (s1 - 0.6, t1 - 0.6)], [0.1, 0.7, 0.1])), skin.hi, 0.55),
                 (F(ellipse(s0 + (s1 - s0) * 0.55, t1 - 0.4, (s1 - s0) * 0.34, 0.9)), skin.hi, 0.45)]
        if i_ < 3:
            fdet.append((F(ribbon([(s0, t0 + 0.6), (s0 - 0.05, (t0 + t1) / 2), (s0, t1 + 0.4)], [0.1, 0.7, 0.1])), skin.deep, 0.75))
    fdet += [(F(ribbon([(7.0, -6.6), (-1.0, -7.6), (-6.4, -6.0)], [0.1, 0.9, 0.1])), skin.deep, 0.4)]
    fig.part('fist', fist, skin, cel=1.3, rim=0.7, cast=1.2,
             cast_on=['handle', 'cring', 'pommel', 'collar', 'chead', 'narm', 'nbrac', 'cloth', 'nleg', 'torso', 'rope'], details=fdet)
    thumb = F(limb([(3.6, 6.0), (6.6, 3.4), (7.8, -0.4), (7.4, -3.4)], [3.8, 3.4, 3.0, 2.6]))
    fig.part('thumb', thumb, skin, cel=0.8, rim=0.6, cast=0.9, cast_on=['fist', 'handle', 'collar'],
             details=[(F(ribbon([(5.4, 5.0), (7.4, 1.8), (8.0, -1.6)], [0.1, 0.9, 0.1])), skin.hi, 0.55),
                      (F(ellipse(7.5, -2.6, 0.9, 1.1)), skin.light, 0.6)])

    # ---- chaque groupe de morceaux prend sa pose ----
    heads = ['head', 'tuskN', 'tuskF', 'browN', 'browF', 'mane', 'ering', 'hornN', 'hornF', 'mb1', 'mb2']
    fig.pose(heads, HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['farm', 'ffist', 'fbrac'], FARM)
    fig.pose(['cloth', 'end1', 'end2'], CLO)
    fig.pose(['rope', 'knot'], PEL)
    club = ['chead', 'collar', 'handle', 'cring', 'pommel'] + ['stud%d' % i for i in range(k_)]
    fig.pose(club + ['narm', 'nbrac', 'fist', 'thumb'], U)
    # l'ordre de dessin : la tête (et sa crinière) passe devant le bras proche quand il se lève ; le poing toujours devant
    order = [p.name for p in fig.parts]
    byname = {p.name: p for p in fig.parts}
    hg = ['head', 'tuskN', 'tuskF', 'browN', 'browF', 'mane', 'ering', 'hornF', 'hornN']
    rest = [n for n in order if n not in hg + ['fist', 'thumb']]
    fig.parts = [byname[n] for n in rest + hg + ['fist', 'thumb']]
    fig.ctx = dict(U=U, G=mapp(U, G), ang=ang + P['lean'] * 1.1, P=P, S=mapp(U, Snu),
                   tip=mapp(U, (G[0] + u[0] * SB * lk, G[1] + u[1] * SB * lk)),
                   club_pt=lambda s: mapp(U, (G[0] + u[0] * s * lk, G[1] + u[1] * s * lk)),
                   chest=mapp(TOR, (72, 66)), head=mapp(HEAD, (88, 42)), mouth=mapp(HEAD, (91.6, 51.8)),
                   nostril=mapp(HEAD, (NOSE[0] + 3.0, NOSE[1] + 1.0)), eyes=(mapp(HEAD, EYE_N[:2]), mapp(HEAD, EYE_F[:2])),
                   HEAD=HEAD, ROOT=ROOTM)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """oni-brute.svg (grand) et oni-brute-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-lenore-costaud.webp (512 px de haut) et mon-lenore-costaud-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('oni-brute', 0.95, 512, ID_JEU), ('oni-brute-petit', 1.35, 160, ID_JEU + '-160')):
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
    main()
