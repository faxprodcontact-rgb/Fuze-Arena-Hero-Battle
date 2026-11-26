# Taurok (myths-3, terre, rare, guerrier) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte
# de tous les héros, décision du propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py).
#
#   python3 refonte-graphique/ui-moderne/heros/taurok/taurok.py      # → taurok.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/cyclope.txt, ancien nom de fichier) : le minotaure brun,
# un colosse. Trois quarts vers la droite, grande fente, sabots à plat. Énorme bosse de trapèzes (plus de crinière :
# avis du propriétaire, tour 2), la tête posée au milieu entre les épaules, une épaulière d'acier rivetée sur chaque
# épaule ; deltoïdes énormes, torse en tonneau, bras épais, petites jambes
# solides poilues jusqu'aux sabots fendus (fanons). Il tient la grosse hache double à deux mains, basse, en travers du
# corps : main droite (proche) près du pommeau, main gauche (lointaine) près du fer ; les doigts passent devant le
# manche, le pouce par-dessus. Vraie tête de taureau : toupet bouclé, grosses cornes ivoire aux pointes sombres,
# oreilles couchées, arcades froncées en V, yeux rouges qui brûlent, large mufle nu aux grands naseaux et à l'anneau
# d'or, rictus, menton lourd, balafre sur la joue. Harnais de cuir croisé (anneau d'or), ceinture cloutée d'or à
# boucle rectangulaire, pagne rouge (deux plis, pan de devant déchiré), brassards d'or rivetés.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; les membres sont d'un seul
# tenant (épaule → coude → poignet, hanche → genou → cheville) : aucune jointure visible.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp, bez, resample  # noqa: E402
from lib import Shape  # noqa: E402
from outils import rot, add, lerp, hexmix, body_limb, round_limb, ik, Seg, inv, bent  # noqa: E402,F401
from visage import placer, verifier  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'myths-3'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
FUR = Mat('#f4b46c', '#cc7a40', '#9a5232', '#62303a', '#3a1a2e')
MANE = Mat('#d08a54', '#9a5434', '#6c3630', '#44202e', '#28121f')
MUZ = Mat('#fff4d6', '#f2cea0', '#cc9c78', '#906464', '#5a3848')
HORN = Mat('#fffcee', '#f2e6c8', '#dac8a6', '#a08a84', '#5e4a5c')
HORN_TIP = '#433652'
GOLD = Mat('#fff4b4', '#f8c640', '#d8961e', '#8e5216', '#5a2c0e', glint='#ffffff')
STEEL = Mat('#f4f8ff', '#b2c0da', '#7684a4', '#464f72', '#272c48', glint='#ffffff')
WOOD = Mat('#dc9a5c', '#aa6630', '#7a4426', '#4c2422', '#2e1418')
LEATHER = Mat('#b47e64', '#784a40', '#4f2c34', '#311a26', '#1e1018')
CLOTH = Mat('#ff9460', '#e8503c', '#b42e3c', '#761a36', '#46102a')
HOOF = Mat('#e4d6d8', '#a698ac', '#70627e', '#4a3e5c', '#2a2238')
EYE = ['#fff8c0', '#ffc848', '#ff6a22', '#d0241e', '#6a0a18']
LID = '#2a0b1c'
EARTH = ['#fff6ce', '#ffd45c', '#e09638', '#c8a070', '#8e664a', '#5e404a', '#3e2a36']   # la lueur et la roche de la terre

# ---------- le visage (méthode commune visage.py, avis du propriétaire du 26/11) ----------
# La face du taureau (sans cornes, oreille ni toupet) dans le repère de la tête : une sphère tournée de 18° vers la
# droite. Les yeux d'un taureau sont plus écartés que ceux d'un humain (az 35°) et plus hauts (ligne des yeux à 0,376) ;
# le « nez » de la méthode = la racine du chanfrein, sur la médiane entre les yeux, là où le mufle commence ; la bouche
# = le trait de la bouche sous le mufle. L'œil du fond est donc loin, près du contour droit, au-dessus du mufle.
FACE_BOX = (53.4, 15.0, 94.6, 53.8)
FACE = placer(FACE_BOX, tour=18, az_oeil=35, y_oeil=0.376, y_nez=0.47, y_bouche=0.87, l_oeil=0.205)
MOUTH = ((77.4, 51.2), (85.2, 48.4))   # le coin proche (tiré vers le bas) et le bout lointain du trait (caché ensuite par le mufle)


def mesures_visage():
    """Les positions RÉELLES du dessin (repère de la tête), pour verifier() de visage.py."""
    (nx, ny, nw), (fx_, fy_, fw) = FACE['oeil_proche'], FACE['oeil_fond']
    return {'oeil_proche': (nx, ny, nw), 'oeil_fond': (fx_, fy_, fw), 'nez': (FACE['nez'][0], FACE['nez'][1]),
            'bouche': ((MOUTH[0][0] + MOUTH[1][0]) / 2, (MOUTH[0][1] + MOUTH[1][1]) / 2, MOUTH[1][0] - MOUTH[0][0])}


GRD = 116.0        # le sol (le point « sol » du pixel art)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (1.0, -14.0, 130.0, 133.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse (les genoux plient, sabots au sol) ; lean : il se penche en avant (+) ;
#   head : décalage de la tête ; tilt : la tête tourne (+ = le mufle descend) ; ph : phase des mèches de la crinière ;
#   ml : retard des mèches ; pg : le pagne se balance ; blink : yeux fermés ; rn / rf : épaules soulevées ;
#   G : le point du manche serré au milieu du poing proche ; ang : la direction du manche (vers le fer) ; sf : où la
#   main lointaine tient le manche (distance depuis le poing proche) ; bn / bf : sens des coudes ; lift / shift : tout
#   le corps en l'air / avancé ; legl : le sabot avant (le lointain) levé (hauteur, recul) ; glow : les yeux et la
#   terre s'embrasent (0..2) ; hot : le fil de la hache brille (0..1).
G0 = (29.4, 91.4)                    # le poing proche sur le manche
ANG0 = -9.9                          # le manche monte un peu vers le fer (du pommeau (7, 95,5) au fer (107, 78))
SF0 = 57.0                           # la main lointaine, à 57 px du poing proche le long du manche
WRN = (1.2, -6.4)                    # le poignet proche, dans le repère du manche (le long, en travers)
WRF = (0.8, -5.6)                    # le poignet lointain
S_N = (25.6, 51.0)                   # l'épaule proche (articulation)
S_F = (92.0, 56.0)                   # l'épaule lointaine
LN1, LN2 = 29.4, 15.0                # bras proche : bras, avant-bras (jusqu'au poignet)
LF1, LF2 = 18.0, 12.6                # bras lointain
HIP = (64.0, 86.0)                   # le pivot du buste
NECK = (74.0, 50.0)                  # le pivot (et le centre d'agrandissement) de la tête
# la tête posée bien au milieu, entre les deux épaules (avis du propriétaire du 26/11, tour 2) : tout ce qui est
# dessiné dans le repère de la tête glisse de ce décalage (le visage garde ses propres mesures)
HEAD_AT = (-16.0, -8.0)
S_POM, S_END, S_HEAD = -22.6, 88.0, 79.0     # le pommeau, le bout du manche, l'axe du fer (le long du manche)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, ml=0.0, pg=0.0, blink=0.0,
            rn=0.0, rf=0.0, G=G0, ang=ANG0, sf=SF0, bn=1.0, bf=-1.0, lift=0.0, shift=0.0, legl=(0.0, 0.0),
            legn=(0.0, 0.0), glow=0.0, hot=0.0, length=1.0, fsh=(0.0, 0.0), nsh=(0.0, 0.0), farfront=0.0)


def sm_under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une mèche : la mèche moins elle-même décalée vers le haut (le haut reste éclairé)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def cuff(c, a, L, W):
    """Un brassard d'or autour d'un avant-bras : c = son milieu, a = la direction de l'avant-bras, L = sa longueur le
    long du bras, W = sa largeur en travers. Les bords sont un peu bombés (il entoure le bras)."""
    h, w = L / 2, W / 2
    pts = [(-h, -w), (-h * 0.2, -w - 0.5), (h * 0.6, -w - 0.3), (h, -w + 0.2), (h + 0.5, 0), (h, w - 0.2), (h * 0.6, w + 0.3),
           (-h * 0.2, w + 0.5), (-h, w), (-h - 0.5, 0)]
    return xf(sm(pts, sharp=(0, 3, 5, 8), t=0.7), c[0], c[1], a)


def cuff_det(c, a, L, W, nr):
    """Les reflets du brassard : les deux bourrelets (bords), une gorge sombre au milieu, des rivets."""
    h, w = L / 2, W / 2
    X = lambda sh: xf(sh, c[0], c[1], a)
    out = [(X(sm([(-h, -w), (-h + 1.6, -w), (-h + 1.6, w), (-h, w)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.light, 0.75),
           (X(sm([(h - 1.6, -w + 0.2), (h, -w + 0.2), (h, w - 0.2), (h - 1.6, w - 0.2)], sharp=(0, 1, 2, 3), t=0.3)), GOLD.light, 0.6),
           (X(ribbon([(-h + 1.8, 0.2 - w * 0.75), (0, -w * 0.82), (h - 1.8, 0.2 - w * 0.75)], [0.1, 0.9, 0.1])), GOLD.hi, 0.85),
           (X(ribbon([(-h + 1.6, w * 0.7), (0, w * 0.8), (h - 1.6, w * 0.7)], [0.1, 1.1, 0.1])), GOLD.shadow, 0.6)]
    for i in range(nr):
        v = (-w * 0.5) + (w * 1.0) * (i + 0.5) / nr
        out += [(X(ellipse(0, v, 0.75, 0.75)), GOLD.shadow, 0.8), (X(ellipse(0.25, v - 0.3, 0.42, 0.38)), GOLD.glint, 0.95)]
    return out



# ---------- les épaulières du minotaure (avis du propriétaire du 26/11, tour 3) ----------
# Pas la calotte ronde rivetée des chevaliers : deux grandes écailles de fer noirci martelé, en pointe vers le bas du
# bras, l'une sur l'autre (celle du dessous dépasse plus bas, vers l'extérieur), bordées de bronze, un clou d'or de
# chaque côté ; une petite pointe de fer plantée sur l'écaille du dessus (vers le haut et l'extérieur) ; une sangle de
# cuir autour du haut du bras qui la tient. Petites et ajustées au deltoïde. Elle est fixée à l'épaule : elle ne suit
# le bras qu'à moitié quand il se lève (l'angle du bras au repos + la moitié de l'écart) ; la sangle, elle, suit le bras.
NARM_REST, FARM_REST = 109.45, 71.71           # l'angle du haut du bras au repos (proche, lointain)
IRON = Mat('#dfe4f4', '#98a0c0', '#666c90', '#3e4264', '#24263e', glint='#ffffff')   # le fer noirci martelé
BRONZE = Mat('#ffe8b0', '#e0a85a', '#b07434', '#74401e', '#46220e', glint='#ffffff')


def pauldron(S, ang, k, o):
    """Les morceaux d'une épaulière : [(suffixe, forme, matière, détails)], du fond (l'écaille du dessous) au devant
    (la pointe de fer). S : l'articulation de l'épaule ; ang : la direction du haut du bras ; k : la taille (1 = épaule
    proche) ; o : le côté extérieur de l'épaule (−1 : vers la gauche de l'image, +1 : vers la droite).
    Repère : a le long du bras (− = vers le haut de l'épaule), c en travers (+ = vers l'extérieur)."""
    sg = Seg(S, (S[0] + math.cos(math.radians(ang)), S[1] + math.sin(math.radians(ang))))
    P_ = lambda a, c: sg(a * k, o * c * k)
    pts = lambda L: [P_(a, c) for a, c in L]

    def stud(a, c, r=0.8):
        p_ = P_(a, c)
        return [(ellipse(p_[0] - 0.15 * k, p_[1] + 0.2 * k, r * k, r * k), BRONZE.deep, 0.7),
                (ellipse(p_[0], p_[1], r * 0.8 * k, r * 0.8 * k), GOLD.base, 1),
                (ellipse(p_[0] + 0.25 * k, p_[1] - 0.3 * k, r * 0.36 * k, r * 0.3 * k), GOLD.glint, 0.95)]

    def scale_(a0, c0, W, Lg):
        """Une écaille en écusson : le haut arrondi, la pointe vers le bas du bras ; bordée de bronze en bas."""
        h, w = Lg / 2, W / 2
        prof = [(-1.0, 0.0), (-0.9, 0.42), (-0.62, 0.86), (-0.2, 1.0), (0.22, 0.86), (0.6, 0.5), (1.0, 0.0)]
        L = [(a0 + h * x, c0 + w * y) for x, y in prof] + [(a0 + h * x, c0 - w * y) for x, y in prof[1:-1][::-1]]
        sh = sm(pts(L), sharp=(6,), t=0.85)
        rim = [(-0.12, 0.93), (0.22, 0.8), (0.58, 0.46), (0.9, 0.0), (0.58, -0.46), (0.22, -0.8), (-0.12, -0.93)]
        R = [(a0 + h * x, c0 + w * y) for x, y in rim]
        det = [(ribbon(pts(R), [0.15 * k] + [1.15 * k] * 5 + [0.15 * k]), BRONZE.base, 1),
               (ribbon(pts([(a - 0.55, c) for a, c in R]), [0.1 * k] + [0.42 * k] * 5 + [0.1 * k]), BRONZE.hi, 0.85),
               # le martelage : deux creux doux et un reflet (lumière en haut à droite)
               (ellipse(*P_(a0 - h * 0.25, c0 - w * 0.25), w * 0.32 * k, h * 0.22 * k), IRON.shadow, 0.3),
               (ellipse(*P_(a0 + h * 0.15, c0 + w * 0.3), w * 0.26 * k, h * 0.18 * k), IRON.shadow, 0.25),
               (ribbon(pts([(a0 - h * 0.78, c0 - w * 0.2), (a0 - h * 0.62, c0 - w * 0.6), (a0 - h * 0.25, c0 - w * 0.82)]),
                       [0.1 * k, 0.9 * k, 0.1 * k]), IRON.hi, 0.7)]
        det += stud(a0 + h * 0.1, c0 + w * 0.66) + stud(a0 + h * 0.1, c0 - w * 0.66)
        return sh, det
    out = []
    # l'écaille du dessous : elle dépasse sous la première, plus bas sur le bras, vers l'extérieur
    sh, det = scale_(5.0, 2.6, 13.0, 13.6)
    out.append(('l', sh, IRON, det))
    # l'écaille du dessus : elle coiffe le haut du deltoïde
    sh, det = scale_(-3.6, 0.4, 18.4, 18.4)
    out.append(('c', sh, IRON, det))
    # la pointe de fer : un cône court planté sur l'écaille, vers le haut et l'extérieur
    base_ = (-8.6, 3.4)
    d_ = (-0.66, 0.75)
    nrm = (d_[1], -d_[0])
    L_, w_ = 6.0, 2.0
    tip = (base_[0] + d_[0] * L_, base_[1] + d_[1] * L_)
    q = lambda t, s_: (base_[0] + d_[0] * t + nrm[0] * s_, base_[1] + d_[1] * t + nrm[1] * s_)
    spike = sm(pts([q(0, w_), q(2.4, 1.2), tip, q(2.4, -1.2), q(0, -w_), q(-0.8, 0)]), sharp=(2,), t=0.8)
    sd = [(ellipse(*P_(*base_), 2.2 * k, 2.2 * k), BRONZE.base, 0.95),
          (ellipse(*P_(*base_), 1.3 * k, 1.3 * k), IRON.light, 0.9),
          (ribbon(pts([q(0.6, 0.9), q(2.6, 0.5), tip]), [0.2 * k, 0.55 * k, 0.05 * k]), IRON.glint, 0.75)]
    out.append(('s', spike, IRON, sd))
    return out


def arm_strap(sg_, a, hw, k):
    """La sangle de cuir autour du haut du bras (sg_ : le repère du bras, a : sa place le long du bras, hw : la
    demi-largeur du bras à cet endroit) : un peu bombée vers le bas (elle fait le tour), une petite boucle d'or."""
    sh = limb([sg_(a, -hw + 0.6), sg_(a + 1.1 * k, -hw * 0.4), sg_(a + 1.3 * k, 0.0), sg_(a + 1.1 * k, hw * 0.4), sg_(a, hw - 0.6)],
              [2.5 * k, 2.5 * k], n=18)
    det = [(ribbon([sg_(a - 0.7 * k, -hw * 0.8), sg_(a + 0.5 * k, 0.0), sg_(a - 0.7 * k, hw * 0.8)], [0.1, 0.5 * k, 0.1]), LEATHER.hi, 0.55)]
    bc = sg_(a + 1.25 * k, hw * 0.3)
    buckle = rpoly([(bc[0] - 1.5 * k, bc[1] - 1.6 * k), (bc[0] + 1.5 * k, bc[1] - 1.6 * k), (bc[0] + 1.5 * k, bc[1] + 1.6 * k),
                    (bc[0] - 1.5 * k, bc[1] + 1.6 * k)], 0.5 * k)
    bd = [(ellipse(bc[0] + 0.4 * k, bc[1] - 0.6 * k, 0.5 * k, 0.4 * k), GOLD.glint, 0.9),
          (rpoly([(bc[0] - 0.6 * k, bc[1] - 0.7 * k), (bc[0] + 0.6 * k, bc[1] - 0.7 * k), (bc[0] + 0.6 * k, bc[1] + 0.7 * k),
                  (bc[0] - 0.6 * k, bc[1] + 0.7 * k)], 0.2 * k), LEATHER.base, 1)]
    return sh, det, buckle, bd


def pgrad(sh, m=STEEL):
    """Le dégradé d'une pièce d'armure : clair en haut à droite, sombre en bas à gauche."""
    x0, y0, x1, y1 = sh.bbox()
    return (x1, y0, x0 + (x1 - x0) * 0.25, y1, [(0, m.hi), (0.3, m.light), (0.68, m.base), (1, m.shadow)])


def put_pauldron(fig, pre, S, ang, k, o, arm_seg, a_strap, hw, cast_on):
    """Pose la sangle (sur le bras) puis l'épaulière (sur l'épaule) : morceaux pre+'strap', pre+'buck', pre+'paull',
    pre+'paulc', pre+'pauls'."""
    sh, det, buckle, bd = arm_strap(arm_seg, a_strap, hw, k)
    fig.part(pre + 'strap', sh, LEATHER, cel=0.5, rim=0.4, cast=0.6, cast_on=[pre + 'arm', 'torso'], details=det)
    fig.part(pre + 'buck', buckle, GOLD, cel=0.3, rim=0.3, cast=0.4, cast_on=[pre + 'strap'], details=bd)
    for sfx, sh, m, det_ in pauldron(S, ang, k, o):
        fig.part(pre + 'paul' + sfx, sh, m, grad=pgrad(sh, m), cel=0.8 * k if sfx != 's' else 0.4, rim=0.5 if sfx != 's' else 0.35,
                 cast=(0.9 if sfx == 'c' else 0.6) * k, cast_on=cast_on + [pre + 'arm', pre + 'strap', pre + 'buck', pre + 'paull', pre + 'paulc'],
                 details=det_)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    glow = P['glow']

    # ---- le squelette : une matrice par groupe de morceaux ----
    ROOTM = mT(P['shift'], -P['lift'])
    dyb = P['crouch'] * 0.85
    PEL = mchain(ROOTM, mT(0, dyb))
    U = mchain(PEL, mT(P['lean'] * 0.35, 0), mR(P['lean'] * 1.1, *HIP))       # le haut du corps (depuis les hanches)
    br = P['breath']
    UC = mchain(U, mT(0, -0.6 * br))                                           # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 64, 84))
    HEAD = mchain(UC, mT(*HEAD_AT), mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    CLO = mchain(PEL, mskx(-0.05 * P['pg'], 82))

    # ======================================================================== la corne lointaine (derrière la tête)
    hornF = lock((82.6, 20.6), (88.4, 20.2), (93.2, 15.0), (95.2, 2.6), 5.8, n=14, bulge=0.06)
    fig.part('hornF', hornF, HORN, grad=(84, 20, 95.2, 2.6, [(0, HORN.base), (0.35, HORN.light), (0.62, '#c8b6a0'), (0.82, '#8a788a'), (1, HORN_TIP)]),
             cel=0.9, rim=0.7, cast=0,
             details=[(ribbon([(87.4, 18.4), (91.4, 15.2), (93.6, 9.6), (94.6, 4.6)], [0.2, 0.9, 0.6, 0.1]), HORN.hi, 0.8)])

    # ======================================================================== les jambes : hanche → genou → cheville,
    # d'un seul tenant (aucune couture au genou) ; les fanons poilus couvrent le haut des sabots fendus
    def leg(name, Hr, B, L1_, L2_, bend, keys, cast_on, lifted=(0.0, 0.0)):
        """Une jambe : la hanche Hr (repère du bassin), le dessous du sabot B (au sol) ; lifted = (hauteur, recul)."""
        H = mapp(PEL, Hr)
        B = mapp(ROOTM, B)
        hl, hb = lifted
        B = (B[0] - hb, B[1] - hl)
        A = (B[0] + 0.4, B[1] - 9.6)              # la cheville, cachée sous les fanons
        sc = min(1.0, math.dist(H, A) * 1.05 / (L1_ + L2_))
        K, A2 = ik(H, A, L1_ * sc, L2_ * sc, bend)
        if math.dist(A2, A) > 0.01:
            B = (B[0] + A2[0] - A[0], B[1] + A2[1] - A[1])
        sh = body_limb([H, K, A2], keys, n=22)
        th, sn = Seg(H, K), Seg(K, A2)
        sa = math.degrees(math.atan2(sn.u[1], sn.u[0]))
        det = [(ellipse(*sn.at(0.4, 3.6), 2.6, 4.6, sa - 90), FUR.light, 0.45),
               (ribbon([sn.at(0.1, -5.6), sn.at(0.5, -6.2), sn.at(0.95, -5.6)], [0.1, 1.3, 0.1]), FUR.deep, 0.35)]
        # quelques mèches de poil sur le tibia (courtes, inégales, pas une rangée)
        for (a, b, ln) in ((0.3, 1.2, 3.6), (0.55, -2.6, 3.0), (0.72, 4.0, 2.6)):
            p_ = sn.at(a, b)
            det.append((ribbon([p_, add(p_, sn.u, ln * 0.5), add(add(p_, sn.u, ln), sn.v, -0.6)], [0.1, 0.7, 0.1]), FUR.shadow, 0.5))
        fig.part(name, sh, FUR, cel=1.7, rim=0.6, cast=1.0, cast_on=cast_on, details=det)

        def Hp(pts):
            return [(B[0] + x, B[1] + y) for x, y in pts]
        # le sabot fendu : deux onglons côte à côte (le sillon entre eux), la sole sombre, un reflet de corne sur chacun
        hoof = sm(Hp([(-12.6, 0.4), (-12.8, -3.0), (-11.4, -5.8), (-7.6, -7.2), (-2.6, -7.0), (0.2, -6.2), (2.6, -7.2),
                      (7.4, -7.4), (11.0, -5.8), (12.8, -3.0), (12.8, 0.4)]), sharp=(0, 10), t=0.85)
        hd_ = [(sm(Hp([(-12.8, -1.4), (12.8, -1.4), (12.8, 0.6), (-12.8, 0.6)])), HOOF.deep, 0.9),
               (ribbon(Hp([(0.4, -6.4), (0.2, -3.4), (0.4, -0.8)]), [0.3, 1.2, 0.4]), HOOF.deep, 0.85),
               (ellipse(*Hp([(7.0, -5.4)])[0], 2.8, 1.0, -6), HOOF.hi, 0.75),
               (ellipse(*Hp([(-5.4, -5.0)])[0], 2.4, 0.8, -6), HOOF.light, 0.6)]
        fig.part(name + 'h', hoof, HOOF, cel=1.2, rim=0.7, cast=0.9, details=hd_)
        # les fanons : une touffe de poil autour de la cheville ; des pointes inégales tombent sur le sabot
        fet = sm(Hp([(-9.6, -13.6), (-4.0, -14.6), (3.6, -14.6), (9.4, -13.4), (10.6, -9.4), (9.6, -7.6), (7.8, -8.6),
                     (6.0, -6.2), (4.0, -8.2), (1.6, -5.8), (-0.6, -7.8), (-3.2, -5.8), (-5.0, -8.0), (-7.4, -6.2), (-8.6, -8.6),
                     (-10.6, -8.0)]), sharp=(5, 6, 7, 8, 9, 10, 11, 12, 13, 14), t=0.8)
        fig.part(name + 'f', fet, FUR, cel=1.1, rim=0.6, cast=1.0, cast_on=[name + 'h'],
                 details=[(ribbon(Hp([(2.0, -13.0), (5.2, -10.4), (6.8, -8.8)]), [0.1, 0.9, 0.1]), FUR.hi, 0.5),
                          (ribbon(Hp([(-3.4, -12.6), (-2.6, -9.6), (-1.6, -7.4)]), [0.1, 0.7, 0.1]), FUR.deep, 0.4),
                          (ribbon(Hp([(-8.0, -12.0), (-7.0, -9.8), (-6.4, -8.0)]), [0.1, 0.6, 0.1]), FUR.deep, 0.35)])
        return K, B

    KF, AF = leg('fleg', (88.6, 87.0), (89.8, 116.4), 11.0, 10.4, -1,
                 [(0, 9.2, 9.4), (0.5, 8.8, 8.8), (0.75, 8.2, 7.8), (1, 7.8, 7.6)], None, P['legl'])
    KN, AN = leg('nleg', (41.4, 87.0), (40.0, 116.4), 11.0, 10.4, -1,
                 [(0, 9.6, 9.8), (0.5, 9.2, 9.2), (0.75, 8.6, 8.2), (1, 8.2, 8.0)], ['fleg', 'flegh', 'flegf'], P['legn'])

    # ======================================================================== le buste (avec la bosse et le cou)
    torso = sm([(66.0, 30.4), (57.0, 32.4), (47.0, 32.4), (39.0, 35.6), (33.4, 42.4), (30.6, 51.0), (31.0, 60.0),
                (32.6, 68.0), (33.4, 75.0), (33.8, 81.8), (48.0, 83.6), (64.0, 84.4), (80.0, 83.4), (93.4, 82.0),
                (94.0, 76.4), (95.6, 70.6), (97.8, 64.6), (99.6, 58.8), (99.6, 53.6), (97.0, 50.2), (93.2, 48.4),
                (89.4, 46.2), (86.2, 42.6), (84.4, 37.4), (81.0, 32.0), (74.0, 29.6)])
    det = [(torso, ('lin', 34, 66, 56, 62, [(0, FUR.deep, 0.5), (1, FUR.deep, 0)]), 1)]
    # les pectoraux : la plaque éclairée, l'ombre dessous (le proche plus large, trois quarts)
    det += [(sm([(43.0, 51.6), (52.0, 49.8), (61.6, 51.4), (66.0, 54.6), (64.8, 59.4), (57.6, 62.0), (48.0, 60.8), (42.0, 56.4)]), FUR.light, 0.5),
            (sm([(41.6, 58.0), (48.0, 62.2), (57.6, 63.6), (65.4, 60.4), (66.2, 63.8), (58.0, 66.4), (47.4, 65.2), (40.8, 61.0)]), FUR.shadow, 0.8),
            (sm([(69.4, 54.4), (78.0, 53.2), (88.4, 53.6), (95.6, 55.8), (95.0, 61.0), (87.4, 63.4), (76.4, 63.0), (69.6, 59.4)]), FUR.hi, 0.42),
            (sm([(69.4, 61.0), (77.0, 64.6), (87.6, 65.0), (95.2, 62.0), (94.4, 65.6), (87.2, 67.6), (76.4, 67.0), (69.0, 64.4)]), FUR.shadow, 0.75),
            (ribbon([(67.2, 51.0), (67.8, 57.4), (67.4, 64.4)], [0.1, 1.3, 0.2]), FUR.shadow, 0.6)]
    # les abdominaux : des blocs doux qui rétrécissent vers le bas (la ligne du milieu décalée vers la droite)
    det += [(ribbon([(68.2, 66.0), (68.0, 71.6), (68.4, 77.0), (68.8, 80.0)], [0.2, 1.1, 1.0, 0.2]), FUR.shadow, 0.7),
            (ribbon([(55.6, 70.6), (61.4, 71.2), (67.4, 70.8)], [0.1, 1.0, 0.3]), FUR.shadow, 0.65),
            (ribbon([(57.0, 75.2), (62.2, 75.6), (67.4, 75.2)], [0.1, 0.9, 0.3]), FUR.shadow, 0.6),
            (ribbon([(69.2, 70.8), (75.6, 71.2), (82.4, 70.2)], [0.3, 0.9, 0.1]), FUR.shadow, 0.55),
            (ribbon([(69.2, 75.2), (75.0, 75.6), (80.6, 74.8)], [0.3, 0.8, 0.1]), FUR.shadow, 0.5),
            (rpoly([(56.6, 67.4), (67.2, 67.0), (67.0, 70.0), (57.0, 69.8)], 1.4), FUR.light, 0.22),
            (rpoly([(57.8, 72.0), (67.2, 71.8), (67.0, 74.4), (58.2, 74.4)], 1.3), FUR.light, 0.18),
            (rpoly([(69.4, 67.2), (82.0, 66.8), (81.6, 69.8), (69.4, 70.0)], 1.3), FUR.hi, 0.2),
            (rpoly([(69.4, 71.8), (80.6, 71.6), (80.2, 74.2), (69.4, 74.4)], 1.2), FUR.hi, 0.17)]
    # le dentelé (côté proche, dans l'ombre) ; le flanc lointain éclairé
    det += [(ribbon([(38.6, 63.0), (42.4, 64.4), (45.4, 63.6)], [0.1, 0.9, 0.1]), FUR.deep, 0.4),
            (ribbon([(39.0, 67.6), (42.8, 68.6), (45.6, 67.8)], [0.1, 0.8, 0.1]), FUR.deep, 0.35),
            (ribbon([(90.6, 68.0), (89.4, 74.0), (89.0, 80.0)], [0.1, 1.0, 0.1]), FUR.shadow, 0.5)]
    # le cou de taureau (avis du propriétaire du 26/11, tour 3 : la tête ne s'enfonce plus dans le torse) : une colonne
    # épaisse et courte sous la mâchoire, éclairée à droite, le muscle du cou côté lumière, le pli à sa base (le haut
    # du sternum et les clavicules), le creux du sternum au milieu
    det += [(sm([(48.0, 41.0), (64.0, 44.6), (78.0, 44.4), (85.6, 39.4), (88.8, 45.4), (84.6, 49.6), (74.0, 52.0), (62.0, 52.4),
                 (52.0, 49.6), (45.6, 45.4)]), FUR.light, 0.3),
            (ribbon([(86.2, 40.4), (84.6, 44.6), (80.6, 48.8), (76.4, 51.2)], [0.1, 1.5, 1.2, 0.1]), FUR.hi, 0.5),
            (ribbon([(45.0, 46.2), (53.0, 50.6), (62.0, 53.0), (72.0, 53.0), (82.0, 50.8), (90.2, 46.8)],
                    [0.1, 1.0, 1.4, 1.4, 1.0, 0.1]), FUR.shadow, 0.6),
            (ribbon([(66.4, 50.6), (67.0, 53.0), (67.4, 55.6)], [0.1, 1.0, 0.1]), FUR.shadow, 0.5)]
    # la bosse : la masse des trapèzes, éclairée en haut
    det += [(sm([(44.0, 34.4), (54.0, 34.0), (62.0, 38.6), (58.0, 42.0), (48.0, 40.6), (40.6, 40.4)]), FUR.light, 0.35)]
    fig.part('torso', torso, FUR, cel=2.0, rim=0.7, cast=1.2, details=det, occl=(FUR.deep, 0.22, 3.4))

    # ---- le harnais de cuir croisé, l'anneau d'or au croisement ----
    RING = (64.6, 62.0)
    for nm, pts in (('strapB', [(83.6, 46.6), (74.0, 54.2), RING, (54.4, 69.6), (44.6, 77.4)]),
                    ('strapA', [(36.4, 41.6), (50.6, 51.6), RING, (77.2, 70.4), (89.0, 78.6)])):
        sh = limb(pts, [3.1, 3.1], n=20)
        x0_, y0_, x1_, y1_ = sh.bbox()
        fig.part(nm, sh, LEATHER, cel=0.8, rim=0.6, cast=0.9, cast_on=['torso', 'strapB'],
                 details=[(ribbon([lerp(pts[0], pts[1], 0.2), pts[1], lerp(pts[1], pts[2], 0.8)], [0.1, 0.45, 0.1]), LEATHER.hi, 0.6),
                          (ribbon([lerp(pts[2], pts[3], 0.25), pts[3], lerp(pts[3], pts[4], 0.8)], [0.1, 0.45, 0.1]), LEATHER.hi, 0.5)])
    ring = ellipse(RING[0], RING[1], 2.9, 2.9).hole(ellipse(RING[0] + 0.1, RING[1] + 0.1, 1.35, 1.35))
    fig.part('ring', ring, GOLD, cel=0.6, rim=0.5, cast=0.8, cast_on=['torso', 'strapA', 'strapB'],
             details=[(ellipse(RING[0] + 1.3, RING[1] - 1.4, 0.7, 0.5, -30), GOLD.glint, 0.9)])

    # ======================================================================== le pagne rouge (deux plis, pan déchiré)
    cloth = sm([(34.6, 79.4), (50.0, 80.6), (64.0, 81.2), (80.0, 80.4), (93.4, 79.2), (93.8, 86.0), (92.4, 93.0),
                (90.6, 99.6), (88.4, 97.4), (86.2, 100.2), (83.6, 97.0), (81.2, 100.6), (78.4, 98.0), (76.4, 103.4),
                (73.8, 100.6), (71.2, 105.2), (68.6, 101.0), (66.2, 104.6), (63.6, 100.4), (61.0, 103.0), (58.8, 97.6),
                (57.0, 93.0), (53.6, 91.4), (50.4, 93.2), (47.4, 90.4), (44.4, 92.2), (41.4, 89.4), (38.4, 90.6),
                (36.2, 87.0), (35.0, 83.0)],
               sharp=tuple(range(7, 28)), t=0.8)
    cd = [(sm([(57.0, 83.0), (78.0, 82.6), (78.4, 98.0), (76.4, 103.4), (73.8, 100.6), (71.2, 105.2), (68.6, 101.0),
                (66.2, 104.6), (63.6, 100.4), (61.0, 103.0), (58.8, 97.6), (57.0, 93.0)], sharp=tuple(range(2, 12))),
           ('lin', 76, 83, 60, 102, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]), 0.55),
          # les deux plis : le creux sombre et l'arête claire à côté
          (ribbon([(57.2, 83.4), (57.6, 89.4), (58.4, 96.6)], [0.2, 1.8, 0.3]), CLOTH.deep, 0.7),
          (ribbon([(78.2, 83.0), (78.4, 90.0), (78.2, 97.6)], [0.2, 1.6, 0.3]), CLOTH.deep, 0.65),
          (ribbon([(59.4, 83.6), (60.2, 90.0), (61.4, 97.0)], [0.1, 1.0, 0.1]), CLOTH.hi, 0.55),
          (ribbon([(80.0, 83.0), (80.6, 89.0), (80.6, 95.4)], [0.1, 0.9, 0.1]), CLOTH.light, 0.6),
          (ribbon([(68.0, 84.6), (68.4, 92.0), (68.2, 99.6)], [0.1, 1.1, 0.1]), CLOTH.light, 0.45),
          (ribbon([(44.0, 82.6), (46.4, 86.0), (47.6, 89.6)], [0.1, 1.0, 0.1]), CLOTH.shadow, 0.5)]
    fig.part('cloth', cloth, CLOTH, cel=1.4, rim=0.7, cast=1.2, details=cd)

    # ======================================================================== la ceinture cloutée d'or, la boucle
    belt = sm([(32.8, 74.4), (48.0, 76.0), (62.0, 76.8), (78.0, 76.0), (94.8, 74.2), (95.2, 80.4), (78.0, 82.6),
               (62.0, 83.4), (48.0, 82.4), (32.6, 80.6)])
    bd = [(ribbon([(34.0, 75.4), (48.0, 77.0), (62.0, 77.8), (78.0, 77.0), (93.8, 75.2)], [0.1, 0.7, 0.8, 0.7, 0.1]), LEATHER.light, 0.7)]
    fig.part('belt', belt, LEATHER, cel=1.0, rim=0.5, cast=1.0, details=bd)
    for i, (x, y) in enumerate(((38.2, 78.2), (46.4, 79.0), (54.4, 79.6), (77.6, 79.4), (86.8, 78.4))):
        fig.part('stud%d' % i, ellipse(x, y, 1.15, 1.15), GOLD, cel=0.35, rim=0.3, cast=0.5, cast_on=['belt'],
                 details=[(ellipse(x + 0.35, y - 0.4, 0.45, 0.35), GOLD.glint, 0.9)])
    buckle = rpoly([(60.4, 72.4), (71.4, 72.0), (71.6, 81.2), (60.6, 81.6)], 1.4)
    hole = rpoly([(62.8, 74.6), (69.2, 74.4), (69.4, 79.0), (63.0, 79.2)], 0.7)
    fig.part('buckle', buckle, GOLD, cel=0.9, rim=0.7, cast=0.9,
             details=[(hole, LEATHER.base, 1), (sm([(62.8, 74.6), (69.2, 74.4), (69.3, 75.8), (62.9, 76.0)]), LEATHER.deep, 0.8),
                      (ribbon([(62.6, 76.8), (66.2, 76.8), (69.0, 76.6)], [0.4, 1.1, 0.4]), GOLD.base, 1),
                      (ribbon([(62.6, 76.4), (66.2, 76.4), (69.0, 76.2)], [0.1, 0.45, 0.1]), GOLD.hi, 0.9),
                      (ellipse(70.2, 73.2, 0.8, 0.5, -20), GOLD.glint, 0.9)])

    # ======================================================================== la hache (repère : G, u vers le fer)
    G, ang = P['G'], P['ang']
    lk = P['length']

    def A_(sh):
        return xf(sh, G[0], G[1], ang, lk, 1)

    def Ap(s, t=0.0):
        a = math.radians(ang)
        return (G[0] + s * lk * math.cos(a) - t * math.sin(a), G[1] + s * lk * math.sin(a) + t * math.cos(a))
    u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    nv = (-u[1], u[0])
    lit_up = (nv[0] * 0.6 - nv[1] * 0.8) < 0          # le côté « −t » regarde-t-il la lumière ?
    sg = -1 if lit_up else 1
    # ======================================================================== le bras lointain (gauche) : il tient le
    # manche près du fer ; épaule → coude → poignet d'un seul tenant, devant le flanc
    # (dessiné derrière la tête, ou devant elle quand il lève la hache : farfront)
    sf = P['sf']

    def draw_far():
        Sf = mapp(UC, (S_F[0] + P['fsh'][0], S_F[1] + P['fsh'][1] - 0.8 * P['rf']))
        Sfu = mapp(inv(U), Sf)
        sf = P['sf']
        Wf = Ap(sf + WRF[0], WRF[1])
        Ef, Wf2 = ik(Sfu, Wf, LF1, LF2, P['bf'])
        farm = round_limb([Sfu, Ef, Wf2], [(0, 7.6, 7.8), (0.25, 6.6, 6.8), (0.55, 5.0, 5.2), (0.66, 5.2, 5.2), (0.85, 4.6, 4.6),
                                           (1, 4.2, 4.2)], n=24)
        f1, f2 = Seg(Sfu, Ef), Seg(Ef, Wf2)
        fa1 = math.degrees(math.atan2(f1.u[1], f1.u[0]))
        fig.part('farm', farm, FUR, cel=1.6, rim=0.7, cast=1.2, cast_on=['torso', 'belt', 'cloth', 'strapA', 'strapB', 'stud3', 'stud4', 'buckle', 'haft', 'head'],
                 details=[(ribbon([f1(-5.6, 3.6), f1(-6.8, -1.0), f1(-4.4, -5.6)], [0.2, 2.2, 0.2]), FUR.light, 0.5),
                          (ellipse(*f1.at(0.65, 2.0), 2.0, 4.0, fa1 - 90), FUR.light, 0.22)])
        # l'épaulière de l'épaule lointaine (plus petite : elle est plus loin)
        put_pauldron(fig, 'f', Sfu, FARM_REST + 0.5 * (fa1 - FARM_REST), 0.74, 1, f1, 6.4, 6.6, ['torso', 'strapA', 'strapB'])
        fa2 = math.degrees(math.atan2(f2.u[1], f2.u[0]))
        bc = f2.at(0.42)
        fig.part('fbrac', cuff(bc, fa2, 7.0, 10.6), GOLD, cel=0.8, rim=0.6, cast=0.9, details=cuff_det(bc, fa2, 7.0, 10.6, 2))

    if P['farfront'] <= 0.5:
        draw_far()
    # ======================================================================== la tête de taureau
    # la corne proche : épaisse à la base, elle part vers l'arrière puis remonte ; la pointe sombre, un reflet
    hornN = lock((66.2, 22.4), (52.0, 25.2), (41.2, 22.6), (39.4, 3.4), 8.8, n=16, bulge=0.04)
    fig.part('hornN', hornN, HORN, grad=(64, 22, 39.4, 3.4, [(0, HORN.base), (0.3, HORN.light), (0.62, '#cdbca4'), (0.84, '#8a788a'), (1, HORN_TIP)]),
             cel=1.2, rim=0.8, cast=1.3, cast_on=['torso'],
             details=[(ribbon([(60.0, 19.6), (51.0, 19.8), (44.6, 17.4), (41.6, 11.6), (40.4, 5.6)], [0.2, 1.3, 1.0, 0.6, 0.1]), HORN.hi, 0.75),
                      (ribbon([(63.6, 24.4), (54.0, 25.0), (46.6, 23.4)], [0.2, 0.9, 0.1]), HORN.deep, 0.35)])
    head = sm([(57.6, 23.8), (62.6, 19.6), (68.0, 16.4), (75.0, 15.4), (82.0, 16.6), (87.6, 19.6), (91.2, 23.8),
               (92.8, 28.0), (95.8, 30.0), (98.6, 32.4), (100.0, 35.8), (100.1, 40.4), (98.9, 44.4), (96.2, 46.8),
               (92.8, 47.9), (91.4, 50.2), (87.2, 52.6), (80.0, 53.6), (72.0, 52.6), (65.0, 49.8), (59.4, 45.2),
               (55.6, 39.6), (54.2, 33.2), (55.2, 27.6)])
    hd = []
    # les plans : le côté (vers l'oreille) dans l'ombre, la joue proche à mi-ton, le front éclairé
    hd += [(sm([(54.2, 30.0), (60.0, 31.0), (64.0, 36.0), (66.4, 42.0), (70.0, 48.6), (72.0, 52.6), (65.0, 49.8),
                (59.4, 45.2), (55.6, 39.6)]), FUR.shadow, 0.55),
           (sm([(70.0, 17.0), (80.0, 16.4), (87.6, 19.8), (90.6, 24.0), (84.0, 25.0), (76.0, 26.6), (70.0, 24.0)]), FUR.hi, 0.35),
           (sm([(66.0, 33.6), (72.0, 32.0), (78.0, 34.0), (79.0, 40.0), (77.0, 46.0), (71.0, 46.4), (67.0, 41.0)]), FUR.light, 0.18)]
    # le mufle nu (le poil du visage descend sur ses côtés) : beige, éclairé en haut, plus sombre dessous
    muz = sm([(81.0, 31.6), (86.0, 31.0), (92.6, 31.8), (96.8, 32.4), (99.5, 34.4), (100.2, 37.6), (99.8, 42.0),
              (98.0, 45.4), (93.6, 47.4), (88.0, 47.8), (83.4, 46.6), (80.4, 43.4), (79.6, 38.0), (80.0, 34.0)])
    hd += [(muz, ('lin', 98, 30, 84, 47, [(0, MUZ.light), (0.5, MUZ.base), (1, MUZ.shadow)]), 1),
           (sm([(82.6, 32.0), (87.0, 31.4), (93.0, 32.2), (97.4, 32.9), (99.3, 34.8), (94.0, 34.2), (88.0, 33.9), (84.0, 34.2)]), MUZ.hi, 0.75),
           (sm([(80.4, 40.0), (84.0, 43.0), (90.0, 44.6), (96.0, 44.0), (99.4, 42.4), (98.0, 45.4), (93.6, 47.4), (88.0, 47.8),
                (83.4, 46.6), (80.4, 43.4)]), MUZ.shadow, 0.6)]
    # le poil des joues qui descend sur les côtés du mufle (des pointes inégales)
    hd += [(sm([(78.0, 29.0), (82.4, 30.2), (83.8, 32.8), (82.0, 35.0), (83.2, 38.6), (81.6, 41.4), (82.2, 44.6),
                (79.6, 46.0), (77.0, 38.0)], sharp=(2, 4, 6)), FUR.base, 1),
           (ribbon([(79.6, 31.0), (81.4, 33.4), (80.8, 36.6)], [0.1, 0.6, 0.1]), FUR.light, 0.55)]
    # les naseaux : deux grands creux (le proche plus grand), leur bord éclairé, l'aile au-dessus
    hd += [(sm([(84.4, 36.6), (86.6, 35.6), (89.2, 36.6), (89.4, 38.6), (87.0, 39.6), (84.8, 38.8)]), MUZ.shadow, 0.6),
           (sm([(92.4, 36.2), (94.4, 35.4), (96.8, 36.0), (97.0, 37.8), (94.8, 38.6), (92.8, 38.0)]), MUZ.shadow, 0.55),
           (sm([(85.2, 37.0), (87.0, 36.4), (88.8, 37.2), (88.6, 38.6), (86.8, 39.0), (85.4, 38.4)]), '#3a1626', 1),
           (sm([(93.0, 36.6), (94.6, 36.0), (96.2, 36.6), (96.2, 37.8), (94.6, 38.2), (93.2, 37.8)]), '#3a1626', 1),
           (ribbon([(84.6, 35.2), (87.2, 34.4), (89.8, 35.4)], [0.1, 0.6, 0.1]), MUZ.hi, 0.8),
           (ribbon([(92.6, 34.8), (94.8, 34.2), (97.2, 35.0)], [0.1, 0.5, 0.1]), MUZ.hi, 0.75),
           (ribbon([(90.4, 36.4), (90.8, 38.6), (90.6, 40.6)], [0.1, 0.6, 0.1]), MUZ.shadow, 0.5)]
    # la bouche fermée en rictus (le coin tiré vers le bas), la lèvre du bas, le menton lourd éclairé
    hd += [(ribbon([MOUTH[1], (82.6, 48.7), (79.4, 49.7), MOUTH[0]], [0.1, 0.9, 0.8, 0.1]), '#2a0d1c', 0.85),
           (ribbon([(79.0, 48.4), (77.8, 49.6), (77.2, 51.0)], [0.1, 0.5, 0.1]), '#2a0d1c', 0.5),
           (ribbon([(80.4, 49.0), (86.0, 50.0), (91.0, 49.6)], [0.1, 1.0, 0.1]), MUZ.base, 0.7),
           (sm([(82.0, 50.6), (88.0, 50.8), (90.8, 50.2), (89.6, 52.2), (84.0, 53.0), (80.4, 52.4)]), FUR.light, 0.45),
           (ribbon([(66.0, 49.6), (72.4, 51.8), (80.0, 52.8)], [0.1, 0.8, 0.1]), FUR.deep, 0.45)]
    # ---- les yeux, placés par visage.py (FACE) : même forme (en miroir), même ligne ; l'œil du fond plus étroit, loin
    # vers le contour droit, au-dessus du mufle. Chaque trait se dessine autour du centre de son œil (k = sa largeur).
    (enx, eny, enw), (efx, efy, efw) = FACE['oeil_proche'], FACE['oeil_fond']
    kn, kf = enw / 8.6, efw / 8.6

    def around(pts, cx, cy, k, mirror, ky=1.0):
        return [(cx + (-x if mirror else x) * k, cy + y * ky) for x, y in pts]
    EYE_PTS = [(-4.4, -0.9), (-1.4, -1.5), (2.0, -0.9), (4.2, 0.7), (1.2, 1.5), (-2.4, 0.9)]   # coin intérieur plus bas (colère)
    ORB_PTS = [(-6.2, -2.0), (0.8, -2.4), (6.4, 0.0), (5.4, 3.4), (-1.2, 3.8), (-5.6, 1.8)]
    BROW_PTS = [(-9.2, -3.0), (-4.6, -5.6), (1.4, -5.0), (6.6, -2.2), (8.8, 0.6), (5.8, 0.6), (1.2, -1.6), (-3.6, -2.0), (-7.8, -0.8)]
    EYES = ((enx, eny, kn, False, 1.0), (efx, efy, kf, True, 0.92))
    # les orbites creusées sous les arcades
    for cx, cy, k, mi, ky in EYES:
        hd.append((sm(around(ORB_PTS, cx, cy, k, mi, ky if not mi else 0.72)), FUR.deep, 0.55 if not mi else 0.5))
    # lueur des yeux sur le poil
    for cx, cy, k, mi, ky in EYES:
        hd.append((ellipse(cx, cy, 6.0 * k, 3.8 * ky), ('rad', cx, cy, 6.0 * k, 3.8 * ky, [(0, EYE[2], 0.55 + 0.15 * glow), (1, EYE[3], 0)]), 1))
    # les yeux rouges qui brûlent
    for cx, cy, k, mi, ky in EYES:
        e = sm(around(EYE_PTS, cx, cy, k, mi, ky), sharp=(0, 3))
        if P['blink'] > 0.5:
            hd += [(e.scale(1.12, 1.3, cx, cy), LID, 0.8), (e, FUR.shadow, 1),
                   (ribbon(around([(-4.0, 0.2), (0.0, 0.9), (3.6, 0.6)], cx, cy, k, mi, ky), [0.1, 0.7, 0.1]), LID, 0.9)]
        else:
            hd += [(e.scale(1.14, 1.4, cx - 0.1, cy), LID, 0.95),
                   (e, ('rad', cx + 0.5 * k, cy - 0.2, 4.2 * k, 2.4 * ky, [(0, EYE[0]), (0.3, EYE[1]), (0.7, EYE[2]), (1, EYE[3])]), 1),
                   (ellipse(cx + 1.1 * k, cy - 0.4 * ky, 0.75 * max(k, 0.8), 0.5 * ky), '#ffffff', 1)]
    # les arcades froncées en V (le bout intérieur plus bas, vers la médiane) : un bourrelet de poil sombre, le dessus
    # éclairé
    for cx, cy, k, mi, ky in EYES:
        br_ = sm(around(BROW_PTS, cx, cy, k, mi, ky), sharp=(0, 4))
        hd += [(br_, ('lin', cx, cy - 6, cx, cy, [(0, FUR.light), (0.45, FUR.base), (1, FUR.deep)]), 1),
               (ribbon(around([(-7.2, -4.0), (-3.2, -5.2), (1.8, -4.6), (6.2, -2.2)], cx, cy, k, mi, ky), [0.1, 0.7, 0.6, 0.1]), FUR.hi, 0.7)]
    # les plis de colère entre les arcades, sur la médiane du front
    mx = FACE['mediane']
    hd += [(ribbon([(mx(25.0) - 0.4, 25.0), (mx(27.2), 27.2), (mx(29.0) + 0.3, 29.0)], [0.1, 0.8, 0.1]), FUR.deep, 0.55),
           (ribbon([(mx(22.4) - 3.4, 22.6), (mx(22.0), 21.8), (mx(22.4) + 3.4, 22.4)], [0.1, 0.7, 0.1]), FUR.shadow, 0.45)]
    # la balafre sur la joue proche : une cicatrice claire, son creux
    hd += [(ribbon([(62.6, 34.4), (64.8, 37.6), (66.4, 41.2), (67.0, 43.6)], [0.2, 1.1, 1.0, 0.2]), '#d08a76', 0.95),
           (ribbon([(62.9, 35.0), (65.0, 38.0), (66.4, 41.4)], [0.1, 0.4, 0.1]), '#7a3a40', 0.7)]
    fig.part('head', head, FUR, grad=(98, 24, 60, 50, [(0, FUR.light), (0.5, FUR.base), (1, FUR.shadow)]),
             cel=1.3, rim=0.65, cast=1.4, details=hd)
    # l'anneau d'or du mufle, qui pend sous la cloison
    nring = ellipse(90.8, 43.4, 2.7, 3.0).hole(ellipse(90.8, 43.6, 1.5, 1.85))
    fig.part('nring', nring, GOLD, cel=0.5, rim=0.45, cast=0.6, cast_on=['head'],
             details=[(ellipse(92.6, 41.8, 0.6, 0.45, -40), GOLD.glint, 0.95)])
    # l'oreille couchée à l'horizontale (vers l'arrière), son creux rose
    ear = sm([(58.0, 29.6), (52.4, 29.0), (46.6, 29.6), (42.0, 31.8), (46.6, 33.8), (52.4, 35.2), (58.0, 35.8)], sharp=(3,))
    fig.part('ear', ear, FUR, cel=0.9, rim=0.5, cast=0.9, cast_on=['head'],
             details=[(sm([(56.8, 31.0), (51.6, 30.8), (47.0, 31.4), (44.6, 32.0), (47.6, 33.0), (52.4, 33.8), (56.6, 34.0)], sharp=(3,)),
                       ('lin', 56, 31, 46, 33, [(0, '#e09a88'), (1, '#a85e62')]), 0.95)])
    # le toupet bouclé du front, entre les cornes
    tuft = sm([(63.6, 22.0), (63.8, 19.6), (65.6, 17.2), (68.2, 17.0), (70.2, 14.8), (73.2, 14.0), (75.4, 15.8),
               (78.0, 15.4), (80.4, 17.2), (80.8, 20.2), (79.6, 22.2), (77.8, 22.8), (76.4, 22.0), (75.0, 23.4),
               (73.0, 23.2), (71.6, 22.2), (70.0, 23.4), (68.0, 23.2), (66.8, 22.2), (65.2, 22.8)])
    td = [(ribbon([(65.6, 21.2), (66.8, 19.0), (68.8, 19.2), (69.2, 21.0)], [0.1, 0.8, 0.8, 0.1]), FUR.deep, 0.45),
          (ribbon([(71.0, 19.0), (72.2, 16.6), (74.4, 16.8), (74.8, 18.8)], [0.1, 0.8, 0.8, 0.1]), FUR.deep, 0.4),
          (ribbon([(75.8, 21.0), (77.0, 18.6), (79.0, 18.8), (79.6, 20.6)], [0.1, 0.7, 0.7, 0.1]), FUR.deep, 0.4),
          (ribbon([(66.4, 18.2), (68.0, 17.4), (69.6, 18.4)], [0.1, 0.6, 0.1]), FUR.hi, 0.7),
          (ribbon([(71.6, 15.4), (73.4, 14.8), (74.8, 16.0)], [0.1, 0.6, 0.1]), FUR.hi, 0.75),
          (ribbon([(76.6, 16.8), (78.6, 16.4), (80.0, 17.6)], [0.1, 0.6, 0.1]), FUR.hi, 0.7)]
    fig.part('tuft', tuft, FUR, grad=(80, 13, 65, 23, [(0, FUR.hi), (0.45, FUR.light), (1, FUR.base)]),
             cel=0.6, rim=0.6, cast=0.35, cast_on=['head', 'hornN', 'hornF'], details=td)

    if P['farfront'] > 0.5:
        draw_far()
    # ---- le manche de bois, le pommeau d'or ----
    haft = A_(sm([(S_POM + 1.2, -1.45), (S_END, -1.45), (S_END, 1.45), (S_POM + 1.2, 1.45)], sharp=(0, 1, 2, 3), t=0.3))
    fig.part('haft', haft, WOOD, cel=0.6, rim=0.45, cast=0,
             details=[(A_(ribbon([(S_POM + 2, 0.6 * sg), (30, 0.7 * sg), (S_END - 1, 0.6 * sg)], [0.1, 0.55, 0.1])), WOOD.hi, 0.65),
                      (A_(ribbon([(-12, -0.4 * sg), (20, -0.2 * sg), (50, -0.4 * sg), (70, -0.3 * sg)], [0.1, 0.4, 0.4, 0.1])), WOOD.deep, 0.4)])
    pom = A_(sm([(S_POM - 2.2, 0), (S_POM - 1.6, -2.0), (S_POM, -2.7), (S_POM + 1.5, -2.2), (S_POM + 2.2, 0),
                 (S_POM + 1.5, 2.2), (S_POM, 2.7), (S_POM - 1.6, 2.0)]))
    pc = Ap(S_POM)
    fig.part('pommel', pom, GOLD, cel=0.6, rim=0.5, cast=0.6,
             details=[(ellipse(pc[0] + 0.6, pc[1] - 0.9, 0.8, 0.55, -20), GOLD.glint, 0.9)])
    fig.part('pring', A_(rpoly([(S_POM + 2.2, -2.0), (S_POM + 4.0, -2.0), (S_POM + 4.0, 2.0), (S_POM + 2.2, 2.0)], 0.5)), GOLD,
             cel=0.4, rim=0.4, cast=0.5)

    # ======================================================================== le fer de la hache : deux lames en
    # croissant (fil clair, biseau, joue sombre près du manche, un losange gravé), la douille d'or rivetée
    def blade(side):
        """Une lame (side = −1 : celle du haut, +1 : celle du bas), dans le repère du manche (s le long, t en travers)."""
        s0 = S_HEAD
        pts = [(s0 - 4.6, 2.6), (s0 - 6.6, 6.4), (s0 - 11.4, 11.6), (s0 - 16.2, 15.6), (s0 - 15.0, 18.8), (s0 - 9.6, 21.6),
               (s0 - 2.0, 22.8), (s0 + 5.6, 22.0), (s0 + 12.0, 19.6), (s0 + 15.6, 15.8), (s0 + 11.2, 12.0),
               (s0 + 6.8, 7.0), (s0 + 4.8, 2.6)]
        return [(s, t * side) for s, t in pts]

    def edge_band(side, a, b):
        """Le fil de la lame : la bande entre deux décalages a et b (0 = le bord) le long du croissant."""
        s0 = S_HEAD
        arc = [(s0 - 15.0, 18.8), (s0 - 9.6, 21.6), (s0 - 2.0, 22.8), (s0 + 5.6, 22.0), (s0 + 12.0, 19.6), (s0 + 15.6, 15.8)]
        outer = [(s, (t - a) * side) for s, t in arc]
        inner = [(s, (t - b) * side) for s, t in arc[::-1]]
        return sm(outer + inner, sharp=(0, len(arc) - 1, len(arc), 2 * len(arc) - 1), t=0.7)
    hot = P['hot']
    for nm, side in (('bladeU', -1), ('bladeD', 1)):
        sh = A_(sm(blade(side), sharp=(3, 4, 9, 10), t=0.8))
        s0 = S_HEAD
        lit = (side == -1) == lit_up                       # la lame tournée vers la lumière
        bd = [(A_(sm([(s0 - 6.0, 2.6 * side), (s0 - 8.6, 8.4 * side), (s0 + 7.6, 8.4 * side), (s0 + 6.0, 2.6 * side)])), STEEL.shadow, 0.7),
              (A_(edge_band(side, 0.0, 4.2)), STEEL.light, 0.95),
              (A_(edge_band(side, 0.0, 1.6)), STEEL.hi if not hot else '#fffbe4', 1)]
        # le losange gravé (signe inventé) : un creux sombre, son bord bas éclairé, un point clair au milieu
        lc = (s0 + 0.4, 12.4 * side)
        loz = A_(sm([(lc[0] - 2.8, lc[1]), (lc[0], lc[1] - 2.8), (lc[0] + 2.8, lc[1]), (lc[0], lc[1] + 2.8)], sharp=(0, 1, 2, 3), t=0.3))
        lozi = A_(sm([(lc[0] - 1.2, lc[1]), (lc[0], lc[1] - 1.2), (lc[0] + 1.2, lc[1]), (lc[0], lc[1] + 1.2)], sharp=(0, 1, 2, 3), t=0.3))
        bd += [(loz, STEEL.deep, 0.9), (lozi, STEEL.light, 1)]
        cpt = Ap(s0 + 8.0, 17.0 * side)
        bd += [(ellipse(cpt[0], cpt[1], 2.6, 0.8, ang - 20), STEEL.glint, 0.7 if lit else 0.45)]
        if hot > 0:
            p_a, p_b = Ap(s0, 0), Ap(s0, 23 * side)
            bd.append((sh, ('lin', p_a[0], p_a[1], p_b[0], p_b[1], [(0, EARTH[1], 0), (0.7, EARTH[1], 0.25 * hot), (1, EARTH[0], 0.8 * hot)]), 1))
        mat = STEEL
        fig.part(nm, sh, mat, grad=(*Ap(s0 + 14, 22 * side), *Ap(s0 - 10, 4 * side),
                                     [(0, STEEL.light if lit else STEEL.base), (0.6, STEEL.base), (1, STEEL.shadow)]),
                 cel=1.0, rim=0.8, cast=0.6, details=bd)
    sock = A_(rpoly([(S_HEAD - 8.4, -3.4), (S_HEAD + 8.6, -3.4), (S_HEAD + 8.6, 3.4), (S_HEAD - 8.4, 3.4)], 1.2))
    sd_ = [(A_(ribbon([(S_HEAD - 7.4, -2.2 * -sg), (S_HEAD, -2.4 * -sg), (S_HEAD + 7.6, -2.2 * -sg)], [0.1, 0.9, 0.1])), GOLD.hi, 0.85),
           (A_(rpoly([(S_HEAD - 8.4, -3.4), (S_HEAD - 6.6, -3.4), (S_HEAD - 6.6, 3.4), (S_HEAD - 8.4, 3.4)], 0.6)), GOLD.shadow, 0.6),
           (A_(rpoly([(S_HEAD + 6.8, -3.4), (S_HEAD + 8.6, -3.4), (S_HEAD + 8.6, 3.4), (S_HEAD + 6.8, 3.4)], 0.6)), GOLD.shadow, 0.5)]
    for rs in (S_HEAD - 4.0, S_HEAD + 4.2):
        rc = Ap(rs, 0.2)
        sd_ += [(ellipse(rc[0], rc[1], 0.85, 0.85), GOLD.shadow, 0.9), (ellipse(rc[0] + 0.25, rc[1] - 0.3, 0.45, 0.4), GOLD.glint, 1)]
    fig.part('socket', sock, GOLD, cel=0.8, rim=0.6, cast=0.9, details=sd_)

    # ======================================================================== les poings sur le manche : le dos de la
    # main en haut, quatre doigts repliés qui passent devant le manche, le pouce par-dessus
    def fist(name, s_c, cast_extra):
        def F(sh):
            return A_(sh.move(s_c, 0))
        out = F(sm([(-6.6, -3.2), (-5.4, -7.0), (-1.0, -8.0), (4.4, -7.2), (6.8, -4.0), (6.9, 1.6), (5.6, 5.4),
                    (0.4, 6.4), (-5.0, 5.8), (-7.0, 2.2)]))
        fd = [(F(sm([(-5.6, -3.6), (-4.6, -6.8), (-0.8, -7.6), (4.2, -6.8), (6.2, -4.0), (2.0, -2.6), (-3.0, -2.6)])), FUR.light, 0.4)]
        for u0, u1 in ((-6.2, -3.1), (-3.1, 0.0), (0.0, 3.1), (3.1, 6.3)):
            seg = F(rpoly([(u0 + 0.15, -1.6), (u1 - 0.15, -1.6), (u1 - 0.3, 5.4 - abs(u0 + u1) * 0.1), (u0 + 0.3, 5.4 - abs(u0 + u1) * 0.1)],
                          [0.7, 0.7, 1.5, 1.5]))
            fd += [(seg, FUR.base, 0.9),
                   (F(ellipse((u0 + u1) / 2 + 0.3, 0.4, abs(u1 - u0) * 0.34, 0.8)), FUR.light, 0.55),
                   (F(ribbon([(u1, -1.2), (u1 - 0.05, 1.8), (u1 + 0.1, 4.8)], [0.1, 0.55, 0.1])), FUR.deep, 0.6)]
        fd += [(F(ribbon([(-6.0, 4.6), (0.0, 5.4), (6.0, 4.4)], [0.1, 0.9, 0.1])), FUR.deep, 0.45)]
        fig.part(name, out, FUR, cel=1.2, rim=0.6, cast=1.0, cast_on=['haft', 'cloth', 'belt', 'pring', 'pommel'] + cast_extra, details=fd)
        th_ = F(limb([(-4.4, -4.6), (-0.6, -3.4), (3.6, -1.6)], [3.4, 3.2, 2.8]))
        fig.part(name + 't', th_, FUR, cel=0.8, rim=0.6, cast=0.8, cast_on=[name, 'haft'],
                 details=[(F(ellipse(3.8, -1.7, 0.9, 0.6, 20)), MUZ.base, 0.7)])

    # ======================================================================== le bras proche (droit) : épaule énorme →
    # coude → poignet d'un seul tenant ; le coude placé par le squelette (le poignet suit le poing)
    Sn = mapp(UC, (S_N[0] + P['nsh'][0], S_N[1] + P['nsh'][1] - 0.8 * P['rn']))
    Snu = mapp(inv(U), Sn)
    Wn = Ap(WRN[0], WRN[1])
    En, Wn2 = ik(Snu, Wn, LN1, LN2, P['bn'])
    arm = round_limb([Snu, En, Wn2], [(0, 11.4, 11.8), (0.18, 10.6, 10.8), (0.42, 8.2, 8.4), (0.63, 6.2, 6.4),
                                     (0.74, 6.4, 6.6), (0.88, 5.6, 5.8), (1, 5.0, 5.0)], n=32)
    a1, a2 = Seg(Snu, En), Seg(En, Wn2)
    aa1 = math.degrees(math.atan2(a1.u[1], a1.u[0]))
    aa2 = math.degrees(math.atan2(a2.u[1], a2.u[0]))
    ad = [
        # le deltoïde énorme éclairé (le haut de l'épaule), sa limite douce sur le bras
        (ribbon([a1(-9.0, 4.0), a1(-11.0, -2.0), a1(-8.6, -8.0), a1(-2.0, -10.6)], [0.2, 3.4, 3.0, 0.3]), FUR.light, 0.55),
        (ribbon([a1(-9.6, 5.0), a1(-11.0, 1.0), a1(-9.6, -4.4)], [0.1, 1.4, 0.1]), FUR.hi, 0.45),
        (ribbon([a1.at(0.18, -9.0), a1.at(0.36, -2.4), a1.at(0.3, 7.6)], [0.1, 1.0, 0.1]), FUR.shadow, 0.45),
        # le biceps devant (éclairé), le triceps dans l'ombre
        (ellipse(*a1.at(0.62, 3.6), 3.2, 6.4, aa1 - 90), FUR.light, 0.22),
        (ribbon([a1.at(0.48, 6.6), a1.at(0.66, 7.4), a1.at(0.84, 6.4)], [0.1, 0.9, 0.1]), FUR.hi, 0.3),
        # l'avant-bras poilu : le muscle près du coude éclairé, quelques mèches
        (ellipse(*a2.at(0.22, 2.4), 3.0, 4.2, aa2 - 90), FUR.light, 0.45),
    ]
    fig.part('narm', arm, FUR, cel=1.9, rim=0.7, cast=1.4,
             cast_on=['torso', 'cloth', 'belt', 'nleg', 'nlegf', 'strapA', 'strapB', 'haft', 'stud0', 'stud1'], details=ad)
    # l'épaulière de l'épaule proche (par-dessus le bras et le harnais ; la tête passe devant)
    put_pauldron(fig, 'n', Snu, NARM_REST + 0.5 * (aa1 - NARM_REST), 1.0, -1, a1, 10.6, 9.8, ['torso', 'strapA', 'strapB'])
    # le brassard d'or riveté sur l'avant-bras proche
    bc = a2.at(0.64)
    fig.part('nbrac', cuff(bc, aa2, 8.4, 13.4), GOLD, cel=0.9, rim=0.6, cast=1.0, details=cuff_det(bc, aa2, 8.4, 13.4, 3))
    fist('nfist', 0.0, ['narm', 'nbrac'])
    fist('ffist', sf, ['farm', 'fbrac', 'strapA'])

    # ---- chaque groupe de morceaux prend sa pose ----
    heads = ['hornF', 'hornN', 'head', 'nring', 'ear', 'tuft']
    fig.pose(heads, HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['strapA', 'strapB', 'ring'], UC)
    fig.pose(['cloth'], CLO)
    fig.pose(['belt', 'buckle'] + ['stud%d' % i for i in range(5)], PEL)
    axe = ['haft', 'pommel', 'pring', 'bladeU', 'bladeD', 'socket']
    pauls = [pre + nm for pre in 'nf' for nm in ('strap', 'buck', 'paull', 'paulc', 'pauls')]
    fig.pose(axe + ['narm', 'nbrac', 'nfist', 'nfistt', 'farm', 'fbrac', 'ffist', 'ffistt'] + pauls, U)
    # l'ordre de dessin (avis du propriétaire du 26/11, tour 3 : la tête passe DEVANT les deux épaulières) :
    #   … le bras lointain et son épaulière, le bras proche et son épaulière, la TÊTE, puis la hache, le brassard et
    #   les poings, toujours devant (le poignet proche est caché par le poing, là où le bras touche le manche).
    hg = ['hornN', 'head', 'nring', 'ear', 'tuft']
    near = ['narm'] + ['n' + nm for nm in ('strap', 'buck', 'paull', 'paulc', 'pauls')]
    byname = {p.name: p for p in fig.parts}
    rest = [p for p in fig.parts if p.name not in near + hg + ['nbrac']]
    at = [p.name for p in rest].index('haft')
    fig.parts = rest[:at] + [byname[n] for n in near + hg] + rest[at:at + 6] + [byname['nbrac']] + rest[at + 6:]
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(U=U, G=mapp(U, G), ang=ang + P['lean'] * 1.1, P=P,
                   head_pt=mapp(U, Ap(S_HEAD, 0)), edge_lo=mapp(U, Ap(S_HEAD, 22.8)), edge_up=mapp(U, Ap(S_HEAD, -22.8)),
                   chest=mapp(TOR, (64, 66)), head=mapp(HEAD, (75, 32)), muzzle=mapp(HEAD, (100, 40)),
                   nostrils=[mapp(HEAD, (87.0, 38.6)), mapp(HEAD, (94.8, 37.8))], horns=[mapp(HEAD, (39.4, 3.4)), mapp(HEAD, (95.2, 2.6))],
                   hooves=[AN, AF], HEAD=HEAD, ROOT=ROOTM)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """taurok.svg (grand) et taurok-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/myths-3.webp (512 px de haut) et myths-3-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('taurok', 0.95, 512, ID_JEU), ('taurok-petit', 1.35, 160, ID_JEU + '-160')):
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
