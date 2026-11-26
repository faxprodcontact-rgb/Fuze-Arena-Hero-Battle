# Corvin (assassins-7, vent, protecteur, commun) redessiné en VECTORIEL lisse, dans le style moderne de l'interface
# (même outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/corvin/corvin.py      # → corvin.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/corvin.txt) : un jeune elfe des bois élancé, gardien de
# la forêt. Trois quarts vers la droite, garde de protecteur, pieds à plat. Capuche verte bordée d'un galon d'or (fermoir
# d'or sous le menton), la grande oreille pointue qui sort de la capuche vers l'arrière ; pèlerine verte à bord en dents
# de feuille soulignées d'or ; longue cape vert sombre qui traîne derrière ; tunique verte au bas découpé en dents bordées
# d'or, ceinture de cuir à boucle ronde d'or, baudrier en une seule diagonale (de l'épaule proche à la boucle) ; braies
# brun-violet, hautes bottes de cuir à revers, sangle de cheville à boucle d'or. Bras gauche (lointain) caché derrière le
# grand bouclier en amande laqué vert d'eau (bord de bois, quatre rivets d'or, grande feuille d'or au centre), tenu serré
# devant lui ; bras droit (proche) le long de la hanche, brassard de cuir bordé d'or, poing fermé sur la dague dont la
# lame courte pointe vers l'avant et le haut, devant le ventre, et passe devant le bord du bouclier.
# Visage jeune et anguleux, construit avec ../visage.py (yeux verts en amande, sourcils froncés en V, nez droit SUR la
# médiane entre les yeux, bouche serrée, menton pointu) ; frange brune en trois mèches balayées vers la droite, une patte
# le long de la joue proche.
# Coordonnées = pixels du dessin pixel art (sol y = 116, pieds en (64, 116)), pour se poser au même endroit dans le jeu.
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Mat, sm, sides, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (rot, add, sub, lerp, norm, ang_of, ik, arm_shape, crpath, taper, under, FigN, rim_band,  # noqa: E402
                    inset, unit)
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'assassins-7'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières jaune-vert chaud, ombres bleu nuit / violettes) ----------
GREEN = Mat('#d2f28a', '#72c95a', '#37944c', '#1f6048', '#123a3e', glint='#f0ffc8')       # capuche, pèlerine, tunique
CAPE = Mat('#7cc27a', '#3a8a5a', '#246448', '#16423e', '#0c2632')                        # la cape, plus sombre
LAQ = Mat('#d6fcd2', '#4cc88c', '#1a9068', '#0f5a56', '#0a3040', glint='#f4fff0')         # laque du bouclier (vert d'eau)
LEATHER = Mat('#f2bc78', '#c47e42', '#8e4e2c', '#5a2a22', '#321420')                      # cuir et bois
HAIR = Mat('#f0b874', '#bc7a40', '#86482a', '#55281f', '#2e1420')                         # cheveux bruns
GOLD = Mat('#fff6c0', '#ffd04a', '#e2a030', '#a65a1e', '#5c2416', glint='#fffbe8')
STEEL = Mat('#ffffff', '#dfe8f6', '#a2b0cc', '#5e6890', '#2c3050', glint='#ffffff')
PANTS = Mat('#b8957a', '#8e6c5a', '#6a4a48', '#48303e', '#2a1c2e')                        # braies brun-violet
SKIN = Mat('#ffe6c4', '#fbc592', '#e49c6e', '#b4644f', '#723442')
IRIS = ('#c4f8c8', '#46d07e', '#1a7a50')
EYE_INK = '#24101c'
LIP = '#8a3a40'

GRD = 116          # le sol (plante des pieds)
FEET = (64, 116)   # le point « pieds » du pixel art (sol: 64 116)
FRAME = (23.5, 11.8, 82, 106.5)      # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
H0 = (70.0, 53.0)  # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 ; crouch : il se ramasse (0..3) ; lean : le haut du corps penche depuis les hanches (+ = vers
#   l'avant) ; head / tilt : la tête ; ear : l'oreille se dresse (+) ou se couche (−) ; fr : la frange se balance ;
#   cape : la cape se balance ; blink : yeux fermés ;
#   sh : le bouclier se déplace (dans le repère du buste) ; srot : il tourne (degrés) ; glow : la feuille d'or s'illumine
#   (0..3) ;
#   g : le poing proche (dans le repère du buste) ; da : l'angle de la dague (−23° au repos : la lame vers l'avant et le
#   haut) ; wa : d'où vient le poignet (angle dans le repère de la dague : −99° = par au-dessus, au repos) ;
#   stretch : la lame s'étire par la vitesse ; red : la lueur rouge de la provocation sur lui (0..1).
S0 = (45.6, 58.6)          # l'épaule proche (sous la pèlerine)
SF0 = (75.0, 58.0)         # l'épaule lointaine (derrière le bouclier)
G0 = (49.6, 84.0)          # le poing proche (le milieu de la prise)
DA0 = -23.0                # l'angle de la dague au repos
WA0 = -99.0                # le poignet, vu de la dague
HAND_D = 5.4               # du poignet au milieu du poing
LU, LF = 11.4, 11.0        # bras, avant-bras
SC0 = (85.0, 79.0)         # le centre du bouclier
SA0 = 9.0                  # l'inclinaison du bouclier (la pointe vers l'arrière)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ear=0.0, fr=0.0, cape=0.0, blink=0.0,
            sh=(0.0, 0.0), srot=0.0, glow=0.0, g=G0, da=DA0, wa=WA0, stretch=0.0, red=0.0, bend=1.0)

# la boîte de la face (ovale du visage, SANS les cheveux ni l'oreille, avant l'agrandissement ×1,1) : ../visage.py
FACEBOX = (60.0, 28.0, 82.4, 52.2)
VZ = placer(FACEBOX, l_oeil=0.23)


def swell(n, w, w0=0.1):
    """Les largeurs d'un trait effilé aux deux bouts (n+1 points, w au milieu)."""
    return [max(w0, w * math.sin(math.pi * i / n) ** 0.7) for i in range(n + 1)]


def teeth(p0, p1, n, depth, sag=0.0):
    """Un bord découpé en dents de feuille, de p0 à p1 (de gauche à droite) : chaque dent a des flancs bombés et une
    pointe vers le bas. Rend les points (vallée, flanc, pointe, flanc…, vallée) et les indices des coins vifs."""
    pts, sharp = [], []
    for i in range(n):
        a = lerp(p0, p1, i / n)
        b = lerp(p0, p1, (i + 1) / n)
        m = lerp(a, b, 0.5)
        k = 4 * (i + 0.5) / n * (1 - (i + 0.5) / n)
        tip = (m[0] + 0.5, m[1] + depth + sag * k)
        if i == 0:
            sharp.append(len(pts))
            pts.append(add(a, (0, sag * 4 * (i / n) * (1 - i / n))))
        pts.append((lerp(a, tip, 0.5)[0] - 0.35, lerp(a, tip, 0.5)[1] + 0.25))
        sharp.append(len(pts))
        pts.append(tip)
        pts.append((lerp(tip, b, 0.5)[0] + 0.2, lerp(tip, b, 0.5)[1] + 0.35))
        sharp.append(len(pts))
        pts.append(add(b, (0, sag * 4 * ((i + 1) / n) * (1 - (i + 1) / n))))
    return pts, sharp


def below(pts, dy, far=12.0):
    """Tout ce qui est sous une ligne brisée décalée de dy vers le haut (le galon d'un bord découpé, peint DANS la
    forme : la découpe le ramène au bord)."""
    line = [(x, y - dy) for x, y in pts]
    x0, x1 = line[0][0] - 4, line[-1][0] + 4
    ring_ = [(x0, line[0][1])] + line + [(x1, line[-1][1]), (x1, line[-1][1] + far), (x0, line[0][1] + far)]
    return sm(ring_, sharp=tuple(range(len(ring_))), t=0.3)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigN(*frame, ow=ow)
    br = P['breath']
    ln = P['lean']
    dyc = P['crouch'] * 0.9
    U = mchain(mT(0.5 * ln, dyc), mR(0.9 * ln, 62, 92))                    # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.55 * br))                                       # ce qui monte avec le souffle
    TOR = mchain(U, mS(1 + 0.006 * br, 1 + 0.014 * br, 62, 76))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], H0[0], H0[1] - 4), mS(1.1, 1.1, *H0))
    LEG = mchain(mskx(-0.5 * ln / 26, GRD), mS(1, 1 - dyc / 26, 0, GRD))
    CAP = mchain(mT(0.3 * ln, dyc * 0.6), mskx(-0.05 * P['cape'] - 0.012 * ln, 56))
    SHM = mchain(UC, mT(*P['sh']), mR(P['srot'], *SC0))
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, SHM=SHM)

    cape(fig, P, CAP)
    far_arm(fig, P, UC, SHM)
    legs(fig, P, LEG)
    tunic(fig, P, TOR, U)
    pelerine(fig, P, UC, main=True)
    head(fig, P, HEAD, UC)
    shield(fig, P, SHM)
    near_arm(fig, P, UC)
    pelerine(fig, P, UC, main=False)
    dagger_and_fist(fig, P, UC)

    fig.ctx.update(head=mapp(HEAD, (71, 36)), chest=mapp(TOR, (60, 70)), hood_top=mapp(HEAD, (64, 17.5)),
                   leaf=mapp(SHM, (83.6, 75.5)), feet=FEET)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def _names(fig, start):
    return [p.name for p in fig.parts[start:]]


# ---------------------------------------------------------------- la cape (derrière tout)
def cape(fig, P, CAP):
    n0 = len(fig.parts)
    sh = sm([(46.0, 53.0), (41.0, 57.6), (36.4, 66.0), (32.6, 76.0), (29.6, 86.0), (27.4, 96.0), (25.6, 106.2),
             (30.6, 107.4), (36.0, 107.0), (41.0, 108.2), (47.0, 108.6), (56.0, 109.0), (66.0, 109.0), (73.0, 106.0),
             (75.0, 94.0), (74.6, 76.0), (73.0, 60.0), (66.0, 53.0), (56.0, 51.6)], sharp=(6,), t=0.9)
    det = [
        # les plis : peu, larges, inégaux (jamais des rayures)
        (ribbon(crpath([(40.0, 62.0), (35.6, 76.0), (32.0, 90.0), (30.4, 104.0)], 16), swell(16, 2.6)), CAPE.shadow, 0.8),
        (ribbon(crpath([(42.4, 66.0), (39.4, 80.0), (37.4, 92.0), (36.6, 104.6)], 16), swell(16, 1.6)), CAPE.light, 0.55),
        (ribbon(crpath([(31.6, 92.0), (29.6, 100.0), (28.6, 105.6)], 10), swell(10, 1.0)), CAPE.light, 0.4),
        (ribbon(crpath([(44.0, 74.0), (42.6, 90.0), (42.4, 104.0)], 12), swell(12, 1.8)), CAPE.shadow, 0.55),
        # entre les jambes et sous le bouclier : le dos de la cape, dans l'ombre
        (sm([(52.0, 86.0), (74.0, 86.0), (74.0, 110.0), (52.0, 110.0)]),
         ('lin', 0, 86, 0, 109, [(0, CAPE.deep, 0.9), (1, CAPE.deep, 0.55)]), 1),
        # l'ourlet, un peu plus clair dessus
        (ribbon([(25.8, 105.4), (31.0, 106.4), (36.0, 106.1), (41.0, 107.3), (46.6, 107.7)], [0.2, 0.6, 0.6, 0.6, 0.2]), CAPE.light, 0.4),
    ]
    fig.part('cape', sh, CAPE, grad=(70, 56, 30, 104, [(0, CAPE.light), (0.4, CAPE.base), (1, CAPE.shadow)]),
             cel=1.6, rim=0.7, cast=0, details=det)
    fig.pose(_names(fig, n0), CAP)


# ---------------------------------------------------------------- le bras lointain (derrière le bouclier)
def far_arm(fig, P, UC, SHM):
    S = mapp(UC, SF0)
    W = mapp(SHM, (79.4, 76.0))                     # la main sur la poignée, derrière le bouclier
    E = ik(S, W, 10.8, 10.6, 1)
    arm = arm_shape(S, E, W, (7.0, 6.2, 5.6))
    fig.part('farm', arm, GREEN, grad=(S[0] + 5, S[1], W[0] - 4, W[1], [(0, GREEN.base), (1, GREEN.shadow)]),
             cel=1.0, rim=0.4, cast=0, details=[(ribbon([S, E, W], [0.2, 1.4, 0.2]).move(1.4, -0.4), GREEN.light, 0.35)])


# ---------------------------------------------------------------- les jambes : braies et bottes à revers
def legs(fig, P, LEG):
    n0 = len(fig.parts)
    for nm, hip, knee, ank, heel, toe, far in (('f', (70.4, 86.0), (71.2, 95.6), (72.6, 105.6), 67.4, 86.6, True),
                                              ('n', (57.4, 86.0), (56.2, 95.6), (55.8, 105.6), 49.8, 66.8, False)):
        # la braie bouffante : de la hanche au revers de la botte
        w0, w1 = 10.4, 9.0
        pant = sm([(hip[0] - w0 / 2, hip[1] - 2), (hip[0] + w0 / 2, hip[1] - 2), (knee[0] + w1 / 2 + 0.6, knee[1]),
                   (ank[0] + 4.6, 101.0), (ank[0] - 4.8, 101.0), (knee[0] - w1 / 2 - 0.4, knee[1])], t=0.9)
        pdet = [(ellipse(knee[0] + 1.6, knee[1] - 1.4, 2.6, 4.2, -8), PANTS.light, 0.45),
                (ellipse(knee[0] + 2.2, knee[1] - 2.2, 1.0, 2.0, -8), PANTS.hi, 0.3),
                (sm([(hip[0] - 6, 86), (hip[0] + 6, 86), (hip[0] + 6, 90.6), (hip[0] - 6, 89.4)]), ('lin', 0, 86, 0, 91, [(0, PANTS.deep, 0.7), (1, PANTS.deep, 0)]), 1)]
        fig.part(nm + 'pant', pant, PANTS, grad=(hip[0] + 6, 86, hip[0] - 6, 100, [(0, PANTS.light), (0.5, PANTS.base), (1, PANTS.shadow)]),
                 cel=1.0, rim=0.6, cast=0.6, details=pdet)
        # la botte : tige, pied (talon, bout arrondi vers l'avant), semelle épaisse
        x0, x1 = ank[0] - 4.6, ank[0] + 4.4
        # le cou-de-pied descend en une seule courbe de la tige au bout (jamais de creux), le talon dépasse à peine
        fl = toe - x1
        boot = sm([(x0, 100.6), (x1, 100.6), (x1 + 0.15, 105.6), (x1 + 0.3 * fl, 108.3), (x1 + 0.7 * fl, 110.0),
                   (toe - 0.3, 112.0), (toe, 114.4), (toe - 0.6, GRD), (heel + 0.6, GRD), (heel, 114.4),
                   (heel + 0.15, 111.6), (x0 - 0.35 * (x0 - heel), 108.6)],
                  sharp=(7, 8), t=0.9)
        bdet = [
            # la semelle épaisse
            (sm([(heel - 1, 114.2), (toe + 1, 114.2), (toe + 1, 117), (heel - 1, 117)]), LEATHER.deep, 1),
            (sm([(heel - 1, 114.2), (toe + 1, 114.2), (toe + 1, 114.75), (heel - 1, 114.75)]), LEATHER.shadow, 0.9),
            # le cou-de-pied éclairé, le bout du pied
            (ellipse(toe - 4.6, 110.8, 3.4, 1.1, 18), LEATHER.hi, 0.45),
            (ribbon(crpath([(x1 - 0.8, 101.6), (x1 - 0.6, 105.0), (x1 + 1.6, 108.0)], 8), swell(8, 0.9)), LEATHER.light, 0.7),
            # la sangle de cheville et sa boucle d'or
            (ribbon([(x0 - 0.6, 106.2), ank, (x1 + 1.4, 105.2)], [1.5, 1.6, 1.5]).move(0, 0.4), LEATHER.deep, 0.9),
            (ribbon([(x0 - 0.6, 105.8), ank, (x1 + 1.4, 104.8)], [0.4, 0.5, 0.4]).move(0, 0.4), LEATHER.light, 0.5),
            (rpoly([(ank[0] + 0.4, 104.8), (ank[0] + 2.6, 104.6), (ank[0] + 2.6, 106.8), (ank[0] + 0.4, 107.0)], 0.5), GOLD.shadow, 1),
            (rpoly([(ank[0] + 0.7, 105.1), (ank[0] + 2.3, 104.95), (ank[0] + 2.3, 106.0), (ank[0] + 0.7, 106.1)], 0.3), GOLD.light, 1),
        ]
        fig.part(nm + 'boot', boot, LEATHER, grad=(x1 + 3, 101, heel, 114, [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
                 cel=1.2, rim=0.6, cast=0.8, cast_on=[nm + 'pant', 'cape', 'fboot', 'fpant'], details=bdet)
        # le revers (le haut de la botte, retourné, plus clair) : il recouvre le bas de la braie
        cuff = sm([(x0 - 1.0, 97.6), (ank[0], 96.8), (x1 + 1.2, 97.4), (x1 + 1.0, 101.4), (ank[0], 101.8), (x0 - 0.8, 101.6)], t=0.85)
        fig.part(nm + 'cuff', cuff, LEATHER, grad=(x1 + 1, 97, x0, 102, [(0, LEATHER.hi), (0.5, LEATHER.light), (1, LEATHER.base)]),
                 cel=0.7, rim=0.5, cast=0.8, cast_on=[nm + 'pant', nm + 'boot', 'cape'],
                 details=[(ribbon([(x0 - 0.6, 98.4), (ank[0], 97.6), (x1 + 0.8, 98.2)], [0.2, 0.6, 0.2]), LEATHER.glint, 0.5)])
    fig.pose(_names(fig, n0), LEG)


# ---------------------------------------------------------------- la tunique, la ceinture, le baudrier
HEM = teeth((45.4, 87.0), (73.0, 87.4), 5, 2.4, sag=0.4)


def tunic(fig, P, TOR, U):
    n0 = len(fig.parts)
    hp, hs = HEM
    top = [(73.4, 80.0), (72.4, 74.0), (74.0, 66.0), (73.6, 58.0), (64.0, 55.4), (52.0, 56.0), (47.4, 62.0), (46.8, 70.0),
           (47.4, 76.0), (46.4, 82.0)]
    pts = list(hp) + top
    sh = sm(pts, sharp=tuple(hs) + (len(hp) - 1, len(pts) - 1), t=0.9)
    det = [
        # le galon d'or le long des dents
        (below(hp, 1.25), ('lin', 72, 84, 46, 90, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
        (below([(x, y - 1.25) for x, y in hp], 0.45, far=0.45), GOLD.hi, 0.6),
        # les plis de la jupe de la tunique, sous la ceinture
        (ribbon(crpath([(52.6, 77.0), (51.6, 82.0), (50.8, 87.0)], 8), swell(8, 1.4)), GREEN.shadow, 0.55),
        (ribbon(crpath([(59.6, 77.0), (60.0, 82.0), (60.6, 87.4)], 8), swell(8, 1.2)), GREEN.light, 0.45),
        # le buste : l'ombre sous la pèlerine, la lumière du flanc droit
        (sm([(44, 60), (76, 58), (76, 64.6), (60, 66.4), (44, 66.4)]), ('lin', 0, 60, 0, 67, [(0, GREEN.deep, 0.6), (1, GREEN.deep, 0)]), 1),
        (ribbon(crpath([(70.6, 64.0), (70.2, 69.0), (69.6, 72.0)], 8), swell(8, 1.4)), GREEN.light, 0.5),
    ]
    fig.part('tunic', sh, GREEN, grad=(74, 60, 48, 86, [(0, GREEN.light), (0.45, GREEN.base), (1, GREEN.shadow)]),
             cel=1.3, rim=0.6, cast=1.0, details=det)
    fig.pose(['tunic'], TOR)
    # la ceinture de cuir (elle fait le tour : peinte d'un bord à l'autre du buste, sa découpe la ramène au bord)
    belt = sm([(46.6, 72.4), (60.0, 72.0), (73.6, 71.6), (73.8, 75.6), (60.0, 76.0), (46.8, 76.4)], sharp=(0, 2, 3, 5), t=0.6)
    fig.part('belt', belt, LEATHER, grad=(70, 71.6, 50, 76.4, [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
             cel=0.6, rim=0.5, cast=0.9, cast_on=['tunic'],
             details=[(ribbon([(47.0, 72.9), (60.0, 72.5), (73.4, 72.1)], [0.3, 0.5, 0.3]), LEATHER.hi, 0.5)])
    # le baudrier : une seule diagonale, de l'épaule proche (sous la pèlerine) jusqu'à la boucle
    bald = limb([(52.6, 58.0), (58.4, 64.4), (63.6, 70.2), (65.4, 72.6)], [2.0, 2.0, 2.0, 1.9])
    fig.part('bald', bald, LEATHER, grad=(66, 58, 54, 72, [(0, LEATHER.light), (1, LEATHER.shadow)]), cel=0.5, rim=0.45, cast=0.8,
             cast_on=['tunic'], details=[(ribbon([(53.6, 58.0), (59.2, 64.2), (64.2, 70.0)], [0.2, 0.5, 0.2]), LEATHER.hi, 0.45)])
    # la boucle ronde d'or
    buck = ellipse(66.2, 74.0, 2.6, 2.5)
    fig.part('buckle', buck, GOLD, grad=(68.6, 71.6, 64, 76.4, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.6, rim=0.5, cast=0.8, cast_on=['belt', 'tunic', 'bald'],
             details=[(ellipse(66.2, 74.0, 1.25, 1.15), LEATHER.shadow, 1),
                      (ellipse(66.0, 74.2, 1.25, 1.15).hole(ellipse(66.25, 73.85, 1.15, 1.05)), LEATHER.deep, 0.6),
                      (ribbon([(65.6, 74.0), (66.4, 74.0), (68.4, 74.0)], [0.6, 0.6, 0.6]), GOLD.base, 1),
                      (ellipse(67.6, 72.6, 0.5, 0.36, -30), GOLD.glint, 0.95)])
    fig.pose(['belt', 'bald', 'buckle'], U)


# ---------------------------------------------------------------- la pèlerine (deux pans : le grand, et le pan de l'épaule
# proche, posé par-dessus le bras proche ; même tissu, sans contour entre eux : un pli)
PEL_HEM = teeth((37.0, 64.8), (79.0, 62.2), 7, 2.7, sag=0.5)


def pelerine(fig, P, UC, main=True):
    n0 = len(fig.parts)
    hp, hs = PEL_HEM
    grad = (78, 52, 40, 66, [(0, GREEN.light), (0.45, GREEN.base), (1, GREEN.shadow)])
    band = below(hp, 1.2)
    bdet = [(band, ('lin', 78, 60, 38, 66, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
            (below([(x, y - 1.2) for x, y in hp], 0.4, far=0.4), GOLD.hi, 0.55)]
    if main:
        top = [(80.2, 58.6), (78.4, 54.6), (74.0, 51.4), (66.0, 50.0), (56.0, 50.4), (48.6, 51.6), (43.8, 54.0), (40.0, 57.4),
               (37.8, 61.0)]
        pts = list(hp) + top
        sh = sm(pts, sharp=tuple(hs) + (len(hp) - 1, 0), t=0.9)
        det = [
            # le creux du cou (sous la capuche), le pli doux sur la poitrine, la lumière sur l'épaule lointaine
            (sm([(54, 50), (74, 50), (72, 55.6), (62, 57.4), (54, 55.4)]), ('lin', 0, 50, 0, 57.4, [(0, GREEN.deep, 0.7), (1, GREEN.deep, 0)]), 1),
            (ribbon(crpath([(60.0, 57.0), (59.4, 60.0), (58.8, 63.0)], 8), swell(8, 1.2)), GREEN.shadow, 0.45),
            (ribbon(crpath([(72.6, 54.6), (76.6, 57.0), (78.2, 60.4)], 8), swell(8, 1.4)), GREEN.hi, 0.6),
        ] + bdet
        fig.part('pel', sh, GREEN, grad=grad, cel=1.2, rim=0.7, cast=1.0, cast_on=['tunic', 'bald', 'farm', 'belt'], details=det)
    else:
        # le pan de l'épaule proche : du cou à ses deux premières dents ; son bord droit est un pli (ombre portée douce)
        k = 6                                   # la vallée après la 2e dent
        top = [(50.6, 61.0), (50.8, 57.0), (49.6, 53.4), (46.6, 52.6), (43.8, 54.0), (40.0, 57.4), (37.8, 61.0)]
        pts = list(hp[:k + 1]) + top
        sh = sm(pts, sharp=tuple(i for i in hs if i <= k) + (k,), t=0.9)
        det = [(ribbon(crpath([(46.0, 54.0), (42.4, 57.0), (40.0, 61.0)], 8), swell(8, 1.0)), GREEN.light, 0.55)] + bdet
        fig.part('flap', sh, GREEN, grad=grad, cel=1.2, rim=0.0, cast=1.1, cast_on=['narm', 'pel', 'tunic', 'bald', 'cape'], details=det)
    fig.pose(_names(fig, n0), UC)


# ---------------------------------------------------------------- la tête (avant l'agrandissement ×1,1)
FACE_PTS = [(60.6, 31.6), (62.6, 29.2), (67.0, 28.0), (73.0, 27.7), (78.6, 28.2), (81.6, 29.8), (82.5, 33.4), (82.6, 37.4),
            (82.2, 41.0), (81.2, 44.4), (79.6, 47.6), (77.5, 50.1), (75.5, 52.1), (73.4, 53.2), (71.3, 52.8), (68.6, 51.6),
            (65.6, 49.7), (62.9, 47.0), (61.0, 43.8), (60.2, 39.6), (60.1, 35.6)]
HOOD_PTS = [(47.8, 53.0), (46.4, 46.0), (46.0, 40.0), (46.8, 33.4), (49.0, 27.6), (52.4, 22.8), (57.0, 19.0), (63.4, 17.6),
            (69.8, 17.9), (75.8, 19.6), (80.4, 22.8), (83.6, 26.8), (85.0, 30.4), (84.6, 33.6), (82.6, 36.6), (80.4, 40.0),
            (79.2, 45.0), (77.2, 49.2), (74.8, 53.8), (68.0, 55.4), (58.0, 55.2), (51.0, 54.4)]
# l'oreille : sa racine (les deux derniers points et le premier) est sous la joue, sur le côté du crâne, à hauteur des
# yeux (place donnée par ../visage.py : V['oreille'] ≈ (60.6, 41.6)) ; le visage la recouvre, elle sort de derrière la joue
EAR_PTS = [(62.0, 36.6), (54.6, 34.6), (47.8, 31.8), (42.8, 29.8), (39.6, 28.8), (42.2, 31.4), (47.2, 35.2), (52.6, 39.0),
           (56.2, 42.0), (58.8, 43.9), (62.0, 44.0)]
FRINGE_PTS = [(61.2, 28.0), (70.0, 26.8), (82.8, 27.4), (83.4, 30.4), (82.8, 35.0), (80.0, 33.8), (78.0, 30.2), (77.2, 36.2),
              (74.0, 34.4), (72.0, 30.4), (70.8, 36.4), (67.6, 34.2), (66.2, 30.8), (65.2, 35.0), (63.8, 33.2), (63.6, 37.4),
              (63.2, 43.8), (61.4, 41.0), (60.4, 35.2), (60.0, 31.0)]
# le galon de l'ouverture épouse le contour du visage (il mord un peu sur la joue : aucun vide sombre entre les deux) ;
# il s'interrompt là où l'oreille traverse la capuche (une fente) : un morceau au-dessus, un morceau au-dessous
TRIM_C = [(81.8, 26.7), (76.0, 26.4), (68.0, 26.5), (61.8, 27.5), (60.0, 29.5), (59.55, 32.4), (59.5, 35.7)]
EAR_LOW = 44.0             # le bord bas de l'oreille, là où le galon du dessous passe sous elle
TRIMLOW_C = [(60.3, 43.3), (60.75, 45.0), (62.3, 47.5), (65.1, 50.1), (68.3, 52.0), (71.0, 53.3)]
TRIMFAR_C = [(81.8, 26.7), (83.6, 28.2), (84.3, 30.8), (84.0, 33.8), (82.6, 37.2), (80.6, 40.4)]


def head(fig, P, HEAD, UC):
    blink = P['blink'] > 0.5
    n0 = len(fig.parts)
    # ---- la capuche (le dos de la tête) : une pointe douce en haut, vers l'arrière ----
    hood = sm(HOOD_PTS, sharp=(6,), t=0.92)
    hdet = [
        # l'intérieur de la capuche (dans l'ombre) : il reste DANS le galon (sous le visage), il ne se voit que sous le menton
        (sm([(60.6, 27.6), (84.2, 27.0), (84.0, 33.0), (80.2, 40.0), (78.4, 46.0), (76.0, 53.0), (70.0, 54.6), (64.2, 51.0),
             (61.0, 45.4), (59.9, 40.0), (59.9, 32.0)]),
         ('lin', 80, 30, 62, 52, [(0, GREEN.shadow), (1, GREEN.deep)]), 1),
        # un grand pli doux de la pointe vers la nuque, la lumière sur le dessus (en haut à droite)
        (ribbon(crpath([(56.6, 20.4), (51.4, 28.0), (49.6, 38.0), (50.4, 48.0)], 16), swell(16, 2.0)), GREEN.shadow, 0.6),
        (ribbon(crpath([(59.6, 19.4), (68.0, 18.8), (76.4, 21.0), (81.6, 25.0)], 16), swell(16, 2.2)).move(0, 0.6), GREEN.hi, 0.75),
        (ribbon(crpath([(56.0, 23.0), (54.0, 30.0), (53.6, 37.0)], 10), swell(10, 1.2)), GREEN.light, 0.45),
        # sous l'oreille : l'ombre de l'oreille sur la capuche
        (ribbon(crpath([(57.6, 44.6), (53.6, 41.8), (49.0, 38.4)], 10), swell(10, 1.6)), GREEN.deep, 0.45),
    ]
    fig.part('hood', hood, GREEN, grad=(82, 20, 48, 50, [(0, GREEN.light), (0.45, GREEN.base), (1, GREEN.shadow)]),
             cel=1.4, rim=0.8, cast=1.2, cast_on=['pel', 'cape', 'tunic'], details=hdet)
    # ---- le galon d'or du côté lointain de l'ouverture (derrière la joue lointaine) ----
    tf = limb(TRIMFAR_C, [1.9, 1.9, 1.9, 1.8, 1.6, 1.2])
    fig.part('trimfar', tf, GOLD, grad=(85, 27, 80, 40, [(0, GOLD.light), (0.6, GOLD.base), (1, GOLD.shadow)]), cel=0.4, rim=0.4,
             cast=0.5, cast_on=['hood'], details=[(ribbon([(83.0, 27.6), (84.4, 30.0), (84.4, 33.0)], [0.1, 0.5, 0.1]), GOLD.hi, 0.6)])
    fig.pose(_names(fig, n0), HEAD)

    # ---- l'oreille d'elfe : elle sort de l'ouverture de la capuche et se couche vers l'arrière ----
    n1 = len(fig.parts)
    ear = sm(EAR_PTS, sharp=(4,), t=0.9)
    edet = [
        # le creux de l'oreille, qui s'ouvre vers la base ; le bord ourlé clair au-dessus
        (sm([(60.6, 38.8), (53.8, 36.6), (47.6, 33.6), (43.6, 31.0), (48.2, 34.8), (53.2, 38.6), (56.8, 41.6), (60.6, 42.2)], t=0.9),
         ('lin', 58, 38, 44, 32, [(0, SKIN.shadow), (1, SKIN.base)]), 0.9),
        (sm([(59.4, 39.6), (55.2, 38.4), (52.6, 37.8), (55.6, 40.4), (59.0, 41.9)], t=0.9), SKIN.deep, 0.45),
        (ribbon(crpath([(60.6, 37.0), (53.8, 35.0), (47.2, 32.2), (41.6, 29.6)], 14), swell(14, 0.9)), SKIN.hi, 0.75),
    ]
    fig.part('ear', ear, SKIN, grad=(58, 36, 42, 32, [(0, SKIN.light), (1, SKIN.base)]), cel=0.8, rim=0.4, cast=1.0,
             cast_on=['hood'], details=edet)
    ER = mchain(HEAD, mR(-5.0 * P['ear'], 60.4, 40.4))     # elle frémit autour de sa racine (sous la joue)
    fig.pose(_names(fig, n1), ER)

    # ---- le visage : les traits sont placés par ../visage.py (VZ) ----
    n2 = len(fig.parts)
    (exN, eyY, ewN), (exF, _, ewF) = VZ['oeil_proche'], VZ['oeil_fond']
    nx, ny = VZ['nez']
    mx, my, mw = VZ['bouche']
    face = sm(FACE_PTS, t=0.92)          # menton arrondi, joue proche bien ronde (jamais de losange)
    fd = []
    # les plans : la tempe et la joue proches (bien rondes) dans une ombre douce, la joue lointaine éclairée
    fd += [(sm([(59.6, 34.0), (63.2, 37.0), (64.6, 42.0), (66.4, 46.4), (69.6, 50.0), (73.4, 52.8), (68.0, 52.0), (63.0, 48.6),
                (60.2, 44.0)]), ('lin', 60, 44, 68, 42, [(0, SKIN.shadow, 0.65), (1, SKIN.shadow, 0)]), 1),
           (sm([(79.4, 33.0), (82.6, 33.4), (82.8, 38.6), (82.0, 43.4), (80.4, 43.0), (80.8, 38.6)]), SKIN.hi, 0.35),
           # la pommette haute éclairée
           (ellipse(66.6, 43.2, 2.1, 0.7, -12), SKIN.light, 0.35),
           (ellipse(66.6, 45.4, 2.0, 1.1, 10), '#ff8a76', 0.12),
           # le menton éclairé, l'ombre sous la lèvre
           (ellipse(73.9, 51.5, 1.0, 0.45), SKIN.hi, 0.35),
           (ellipse(mx + 0.1, my + 1.35, 1.0, 0.3), SKIN.shadow, 0.3)]
    # l'ombre de la frange sur le front
    fd += [(sm([(59, 29), (84, 28.4), (84, 31.6), (80.6, 35.4), (77.4, 36.4), (71.4, 36.8), (65.6, 35.8), (59, 35.6)]),
            ('lin', 0, 31, 0, 36.6, [(0, SKIN.shadow, 0.55), (1, SKIN.shadow, 0)]), 1)]
    # les orbites, à peine creusées sous les sourcils, une par œil, à la même hauteur
    for ex, ew in ((exN, ewN), (exF, ewF)):
        fd.append((ellipse(ex, eyY - 0.4, ew * 0.62, 1.9), SKIN.shadow, 0.35))
    # les yeux verts en amande (MÊME dessin, même ligne, même regard vers la droite ; l'œil du fond un peu plus étroit) :
    # coin extérieur un peu relevé, paupière sombre, reflet blanc
    def eye_pts(ex, ew, s):
        hw = ew / 2
        rel = [(-hw, -0.5), (-hw * 0.42, -1.55), (hw * 0.38, -1.5), (hw, 0.15), (hw * 0.4, 1.15), (-hw * 0.45, 1.0)]
        return [(ex + s * a, eyY + b) for a, b in rel]
    for ex, ew, s in ((exN, ewN, 1), (exF, ewF, -1)):
        al = eye_pts(ex, ew, s)
        eye = sm(al, sharp=(0, 3), t=0.9)
        k = ew / ewN
        ix, iy, ir = ex + 0.55 * k, eyY + 0.1, 1.28 * k ** 0.5
        if blink:
            fd += [(eye.scale(1.06, 1.2, ex, eyY), SKIN.base, 1),
                   (ribbon([al[0], lerp(al[5], al[0], 0.3), lerp(al[5], al[4], 0.5), al[3]], [0.1, 0.5, 0.6, 0.2]).move(0, 0.2), EYE_INK, 0.95)]
            continue
        fd += [(eye.scale(1.1, 1.3, ex, eyY), SKIN.shadow, 0.45), (eye, '#fbf3ee', 1)]
        cid = fig.uid('eye')
        pup = ellipse(ix + 0.08, iy, ir * 0.46, ir * 0.55)
        fd += [('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><path d="%s" fill="FILL"/>'
                '<path d="%s" fill="#0c1418"/><path d="%s" fill="%s" opacity="0.35"/></g>' % (
                    cid, eye.d(), cid, ellipse(ix, iy, ir, ir * 1.05).d(), pup.d(),
                    sm([(ex - 4, eyY - 3), (ex + 4, eyY - 3), (ex + 4, eyY - 0.6), (ex - 4, eyY - 0.9)]).d(), EYE_INK),
                ('rad', ix + 0.3, iy + 0.5, ir * 1.25, ir * 1.25, [(0, IRIS[0]), (0.5, IRIS[1]), (1, IRIS[2])]), 1)]
        fd += [(ellipse(ix + ir * 0.4, iy - ir * 0.36, ir * 0.3, ir * 0.26), '#ffffff', 1),
               (ellipse(ix - ir * 0.42, iy + ir * 0.44, ir * 0.13, ir * 0.11), '#ffffff', 0.6)]
        # la paupière sombre (trait épais) avec sa petite pointe au coin extérieur ; le trait du bas, fin
        hw = ew / 2
        liner = sm([(ex - s * (hw + 0.8), eyY - 1.0), (ex - s * hw, eyY - 0.55), (ex - s * hw * 0.42, eyY - 1.62),
                    (ex + s * hw * 0.38, eyY - 1.58), (ex + s * (hw + 0.1), eyY + 0.12),
                    (ex + s * hw * 0.36, eyY - 0.95), (ex - s * hw * 0.42, eyY - 0.98), (ex - s * hw * 0.9, eyY - 0.2)],
                   sharp=(0, 4), t=0.8)
        fd += [(liner, EYE_INK, 1),
               (ribbon([al[0], lerp(al[0], al[5], 0.5), al[5], lerp(al[5], al[4], 0.6)], [0.1, 0.22, 0.2, 0.06]), EYE_INK, 0.45)]
    # les sourcils bruns froncés en V (l'intérieur plus bas) : même dessin, celui du fond un peu plus court
    for ex, ew, s in ((exN, ewN, 1), (exF, ewF, -1)):
        k = ew / ewN
        rel = [(-3.0, -2.6), (-0.6, -3.7), (2.6, -2.7), (3.4, -1.9), (2.0, -2.0), (-0.4, -2.75), (-2.6, -2.0)]
        b = sm([(ex + s * a * k, eyY + c) for a, c in rel], sharp=(0, 3), t=0.85)
        x0_, y0_, x1_, y1_ = b.bbox()
        fd += [(b.move(-0.2, 0.45), SKIN.deep, 0.35),
               (b, ('lin', x1_, y0_, x0_, y1_, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]), 1)]
    # le nez, long et droit, SUR la médiane entre les deux yeux : l'arête claire, le flanc proche dans l'ombre,
    # un petit bout arrondi, une narine du côté proche
    rx_ = VZ['mediane'](eyY)
    fd += [(ribbon(crpath([(rx_ - 0.7, eyY + 0.2), (nx - 0.9, ny - 2.0), (nx - 1.2, ny - 0.6)], 8), swell(8, 1.1)), SKIN.shadow, 0.55),
           (ribbon(crpath([(rx_ + 0.2, eyY + 0.1), (nx + 0.35, ny - 2.0), (nx + 0.4, ny - 1.0)], 8), swell(8, 0.55)), SKIN.hi, 0.85),
           (ellipse(nx + 0.1, ny - 0.55, 1.1, 0.85), SKIN.light, 0.55),
           (ellipse(nx + 0.4, ny - 0.85, 0.42, 0.3, 20), '#fff4e0', 0.9),
           (ellipse(nx - 0.7, ny + 0.05, 0.62, 0.3, 10), SKIN.deep, 0.8),
           (ellipse(nx + 0.2, ny + 0.45, 1.3, 0.38), SKIN.shadow, 0.5)]
    # la bouche serrée (fermée), centrée sous le nez, les coins qui tombent un peu : résolu
    hm = mw * 0.44
    fd += [(ribbon([(mx - hm, my + 0.45), (mx - hm * 0.45, my + 0.02), (mx, my - 0.05), (mx + hm * 0.5, my + 0.05), (mx + hm, my + 0.4)],
                   [0.1, 0.42, 0.46, 0.4, 0.1]), LIP, 0.95),
           (ribbon([(mx - hm * 0.6, my + 0.75), (mx, my + 0.85), (mx + hm * 0.6, my + 0.75)], [0.1, 0.35, 0.1]), SKIN.light, 0.5)]
    fig.part('face', face, SKIN, grad=(83, 30, 61, 50, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]), cel=0.8, rim=0.55,
             cast=1.0, cast_on=['hood', 'trimfar', 'ear'], details=fd)
    fig.ctx_face = dict(oeil_proche=(exN, eyY, ewN), oeil_fond=(exF, eyY, ewF), nez=(nx, ny), bouche=(mx, my, 2 * hm))
    fig.pose(_names(fig, n2), HEAD)

    # ---- la frange brune, trois mèches balayées vers la droite, une patte le long de la joue proche ----
    n3 = len(fig.parts)
    fr = sm(FRINGE_PTS, sharp=(4, 6, 7, 9, 10, 12, 13, 16), t=0.9)
    frd = [
        # le dessous des mèches dans l'ombre (le long de leurs bords bas), les creux entre les mèches
        (under(fr, 0.5, -1.3), HAIR.shadow, 0.75),
        (ribbon(crpath([(78.0, 30.4), (76.6, 29.0), (74.8, 28.2)], 6), swell(6, 0.6)), HAIR.deep, 0.5),
        (ribbon(crpath([(72.0, 30.6), (70.4, 29.2), (68.6, 28.4)], 6), swell(6, 0.6)), HAIR.deep, 0.5),
        (ribbon(crpath([(66.2, 31.0), (64.6, 29.6), (62.8, 28.8)], 6), swell(6, 0.5)), HAIR.deep, 0.45),
        # le reflet : un court trait clair sur le haut de chaque mèche (jamais une rayure)
        (ribbon(crpath([(78.8, 28.6), (80.8, 30.0), (81.8, 32.0)], 6), swell(6, 0.6)), HAIR.hi, 0.7),
        (ribbon(crpath([(72.8, 28.6), (75.0, 30.2), (76.0, 32.4)], 6), swell(6, 0.65)), HAIR.hi, 0.7),
        (ribbon(crpath([(67.0, 28.8), (69.0, 30.4), (69.8, 32.6)], 6), swell(6, 0.6)), HAIR.hi, 0.6),
        (ribbon(crpath([(61.6, 33.0), (62.2, 37.0), (62.6, 41.4)], 8), swell(8, 0.7)), HAIR.light, 0.45),
    ]
    fig.part('fringe', fr, HAIR, grad=(82, 27, 60, 40, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]), cel=0.7, rim=0.35,
             cast=0.6, cast_on=['face'], details=frd)
    fig.pose(_names(fig, n3), mchain(HEAD, mR(1.6 * P['fr'], 64.0, 28.0)))

    # ---- le galon d'or de l'ouverture (dessus et côté proche, jusqu'au fermoir), le fermoir sous le menton ----
    n4 = len(fig.parts)
    trim = limb(TRIM_C, [1.9] * len(TRIM_C))
    fig.part('trim', trim, GOLD, grad=(80, 25, 60, 52, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.5, rim=0.45,
             cast=1.0, cast_on=['face', 'fringe', 'hood', 'ear'],
             details=[(ribbon(crpath([(81.6, 26.2), (72.0, 25.8), (63.0, 26.6), (59.6, 29.2)], 12), swell(12, 0.5)), GOLD.hi, 0.75)])
    # le morceau du dessous part de SOUS l'oreille (avis, tour 3) : son bout est coupé net le long du bord bas de
    # l'oreille (plus de bout arrondi posé sur elle), l'oreille y jette une ombre douce
    tl_l, tl_r = sides(TRIMLOW_C, [1.9] * len(TRIMLOW_C))
    d0 = norm(sub(TRIMLOW_C[1], TRIMLOW_C[0]))

    def to_ear(p):                                # le coin du bout, ramené sur le bord bas de l'oreille (y = EAR_LOW)
        return add(p, d0, (EAR_LOW - p[1]) / d0[1])
    tl_l[0], tl_r[0] = to_ear(tl_l[0]), to_ear(tl_r[0])
    end = add(TRIMLOW_C[-1], norm(sub(TRIMLOW_C[-1], TRIMLOW_C[-2])), 0.95)
    trimlow = sm(tl_l + [end] + tl_r[::-1], sharp=(0, 2 * len(tl_l)), t=0.6)
    fig.part('trimlow', trimlow, GOLD, grad=(80, 25, 60, 52, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.5,
             rim=0.45, cast=1.0, cast_on=['face', 'fringe', 'hood'],
             details=[(sm([add(tl_l[0], d0, -1), add(tl_r[0], d0, -1), add(tl_r[0], d0, 0.9), add(tl_l[0], d0, 0.9)], t=0.5),
                       GOLD.shadow, 0.55)])
    clasp = sm([(70.6, 51.8), (72.6, 53.0), (73.0, 54.8), (71.2, 56.4), (69.0, 56.0), (68.2, 54.2), (69.0, 52.6)], t=0.95)
    fig.part('clasp', clasp, GOLD, grad=(73, 52, 68, 56.4, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.6, rim=0.5,
             cast=0.9, cast_on=['face', 'hood', 'pel', 'trim', 'trimlow'],
             details=[(ellipse(70.7, 54.2, 1.0, 0.95), GOLD.shadow, 0.7), (ellipse(70.85, 54.0, 0.65, 0.6), GOLD.light, 1),
                      (ellipse(71.6, 53.0, 0.42, 0.3, -30), GOLD.glint, 0.95)])
    fig.pose(_names(fig, n4), HEAD)


# ---------------------------------------------------------------- le bouclier en amande
SH_PTS = [(0.0, -26.4), (8.6, -25.2), (14.0, -21.4), (16.2, -14.6), (16.2, -5.0), (14.6, 5.4), (10.6, 15.0), (5.4, 21.8),
          (0.0, 26.4), (-5.4, 21.8), (-10.6, 15.0), (-14.6, 5.4), (-16.2, -5.0), (-16.2, -14.6), (-14.0, -21.4), (-8.6, -25.2)]
LEAF_PTS = [(0.0, -15.4), (2.6, -12.4), (4.6, -7.6), (5.1, -3.4), (4.3, 1.2), (2.5, 5.0), (0.2, 7.6), (-2.2, 5.0), (-4.2, 1.0),
            (-5.0, -3.6), (-4.4, -8.0), (-2.4, -12.6)]


def shield(fig, P, SHM):
    n0 = len(fig.parts)
    a = math.radians(SA0)

    def L(u, v):
        return (SC0[0] + u * math.cos(a) - v * math.sin(a), SC0[1] + u * math.sin(a) + v * math.cos(a))

    def LS(pts, **k):
        return sm([L(*p) for p in pts], **k)
    body = LS(SH_PTS, sharp=(8,), t=0.92)
    laq = inset(body, 2.1)
    g = P['glow']
    sdet = [
        # le bord de bois (le flanc gauche, dans l'ombre, montre son épaisseur)
        (ribbon(crpath([L(-15.4, -18), L(-15.6, -4), L(-13.4, 8), L(-8.6, 17), L(-2.4, 24.4)], 18), swell(18, 1.4)), LEATHER.shadow, 0.8),
        (ribbon(crpath([L(4, -25.6), L(11.6, -23.2), L(15.6, -17), L(16.2, -8)], 14), swell(14, 0.8)), LEATHER.hi, 0.7),
        # la laque vert d'eau : sombre à gauche, claire en haut à droite
        (laq, ('lin', *L(12, -22), *L(-12, 18), [(0, LAQ.light), (0.45, LAQ.base), (1, LAQ.shadow)]), 1),
        # le grand éclat en haut à droite (une bande courbe), un petit reflet
        (taper(crpath([L(4.6, -21.6), L(10.4, -19.0), L(13.0, -13.4), L(13.4, -6.0)], 14), 1.6, 0.3, tip='sharp', wmid=2.2), LAQ.hi, 0.75),
        (ellipse(*L(12.2, 0.6), 0.7, 1.6, SA0), LAQ.hi, 0.6),
        # les quatre rivets d'or sur le bord
    ]
    for u, v in ((-11.8, -20.2), (11.8, -20.2), (-12.0, 9.6), (12.0, 9.6)):
        c = L(u, v)
        sdet += [(ellipse(c[0] - 0.2, c[1] + 0.3, 1.05, 1.05), GOLD.deep, 0.6),
                 (ellipse(c[0], c[1], 0.95, 0.95), ('lin', c[0] + 1, c[1] - 1, c[0] - 1, c[1] + 1, [(0, GOLD.light), (1, GOLD.shadow)]), 1),
                 (ellipse(c[0] + 0.3, c[1] - 0.35, 0.3, 0.25), GOLD.glint, 0.95)]
    fig.part('shield', body, LEATHER, grad=(*L(14, -24), *L(-14, 20), [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
             cel=1.2, rim=0.6, cast=1.6, cast_on=['tunic', 'pel', 'belt', 'buckle', 'bald', 'fpant', 'fcuff', 'fboot', 'cape', 'farm'],
             details=sdet)
    # la grande feuille d'or nervurée, au centre (en relief : elle pose une ombre douce sur la laque)
    lc = (-0.6, -3.4)
    leaf = LS([(lc[0] + u, lc[1] + v) for u, v in LEAF_PTS], sharp=(0, 6), t=0.9)
    hot = min(1.0, g / 3.0)
    ldet = [
        # la moitié gauche dans l'ombre, la nervure centrale, deux nervures de chaque côté (inégales)
        (LS([(lc[0] + u, lc[1] + v) for u, v in [(0.0, -15.4), (0.0, 7.6), (-2.2, 5.0), (-4.2, 1.0), (-5.0, -3.6), (-4.4, -8.0), (-2.4, -12.6)]],
            sharp=(0, 1), t=0.9), GOLD.shadow, 0.55 * (1 - hot)),
        (ribbon(crpath([L(lc[0], lc[1] - 13.6), L(lc[0] + 0.1, lc[1] - 3), L(lc[0] + 0.1, lc[1] + 7.4)], 12), swell(12, 0.7)), GOLD.deep, 0.55 * (1 - hot)),
        (ribbon(crpath([L(lc[0] + 0.1, lc[1] - 6.4), L(lc[0] + 2.0, lc[1] - 8.6), L(lc[0] + 3.2, lc[1] - 10.8)], 6), swell(6, 0.45)), GOLD.shadow, 0.6 * (1 - hot)),
        (ribbon(crpath([L(lc[0] + 0.1, lc[1] + 0.4), L(lc[0] + 2.4, lc[1] - 1.4), L(lc[0] + 3.8, lc[1] - 3.6)], 6), swell(6, 0.45)), GOLD.shadow, 0.6 * (1 - hot)),
        (ribbon(crpath([L(lc[0], lc[1] - 3.8), L(lc[0] - 2.0, lc[1] - 5.8), L(lc[0] - 3.4, lc[1] - 8.4)], 6), swell(6, 0.45)), GOLD.deep, 0.45 * (1 - hot)),
        (ribbon(crpath([L(lc[0], lc[1] + 3.6), L(lc[0] - 1.8, lc[1] + 2.0), L(lc[0] - 3.2, lc[1] - 0.2)], 6), swell(6, 0.45)), GOLD.deep, 0.45 * (1 - hot)),
        # l'éclat sur le bord droit
        (taper(crpath([L(lc[0] + 2.2, lc[1] - 12.0), L(lc[0] + 4.2, lc[1] - 7.0), L(lc[0] + 4.2, lc[1] - 2.0)], 8), 0.6, 0.2, tip='sharp', wmid=0.9), GOLD.glint, 0.85),
    ]
    if g > 0:
        # la feuille s'illumine : de l'or au blanc doré
        ldet += [(leaf, ('rad', *L(lc[0] + 0.6, lc[1] - 4), 9, 9, [(0, '#fffde8'), (0.5, '#fff0a0'), (1, GOLD.light)]), min(1.0, 0.35 * g))]
    fig.part('leaf', leaf, GOLD, grad=(*L(lc[0] + 5, lc[1] - 14), *L(lc[0] - 5, lc[1] + 7), [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.base)]),
             cel=0.5, rim=0.5, cast=0.9, cast_on=['shield'], details=ldet)
    stem = limb([L(lc[0] + 0.2, lc[1] + 7.0), L(lc[0] - 0.2, lc[1] + 9.0), L(lc[0] - 1.0, lc[1] + 10.4)], [1.0, 0.8, 0.6])
    fig.part('stem', stem, GOLD, cel=0.2, rim=0.3, cast=0.5, cast_on=['shield'])
    fig.pose(_names(fig, n0), SHM)
    fig.ctx['shield_L'] = L


# ---------------------------------------------------------------- le bras proche (manche verte, brassard de cuir bordé d'or)
def arm_pts(P, UC):
    """L'épaule, le coude, le poignet et le poing du bras proche ; l'angle de la dague (repère du dessin)."""
    rotU = math.degrees(math.atan2(UC[1], UC[0]))
    S = mapp(UC, S0)
    G = mapp(UC, P['g'])
    da = P['da'] + rotU
    W = add(G, unit(da + P['wa']), HAND_D)
    E = ik(S, W, LU, LF, P['bend'])
    return S, E, W, G, da


def near_arm(fig, P, UC):
    S, E, W, G, da = arm_pts(P, UC)
    arm = arm_shape(S, E, W, (7.2, 6.6, 6.0))
    fa = ang_of(sub(W, E))
    nrm = unit(fa + 90)

    def F(t, off):                                # un point de l'avant-bras : t le long (0 = coude), off en travers
        return add(lerp(E, W, t), nrm, off)

    def cut(t0, t1):                              # une bande en travers de l'avant-bras (peinte DANS le bras)
        return sm([F(t0, -6), F(t1, -6), F(t1, 6), F(t0, 6)], sharp=(0, 1, 2, 3), t=0.3)
    lit = 1 if nrm[0] + (-nrm[1]) > 0 else -1     # le côté de l'avant-bras tourné vers la lumière (haut-droite)
    det = [
        # la manche : la lumière sur l'épaule, le pli au coude
        (ribbon([lerp(S, E, 0.1), lerp(S, E, 0.7), E], [0.2, 1.4, 0.2]).move(1.2, -0.6), GREEN.light, 0.55),
        # le brassard de cuir (du haut de l'avant-bras au poignet), bordé d'or, sa sangle et sa boucle
        (cut(0.16, 1.2), ('lin', *F(0.5, 3 * lit), *F(0.6, -3 * lit), [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]), 1),
        (sm([F(0.2, 3.2 * lit), F(1.1, 3.2 * lit), F(1.1, 1.5 * lit), F(0.2, 1.6 * lit)], t=0.6), LEATHER.hi, 0.35),
        (cut(0.16, 0.27), ('lin', *F(0.2, 3 * lit), *F(0.2, -3 * lit), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
        (cut(0.92, 1.2), ('lin', *F(1.0, 3 * lit), *F(1.0, -3 * lit), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
        (cut(0.54, 0.64), LEATHER.deep, 0.75),
        (rpoly([F(0.52, 0.4 * lit), F(0.66, 0.4 * lit), F(0.66, 2.0 * lit), F(0.52, 2.0 * lit)], 0.35), GOLD.base, 1),
        (ellipse(*F(0.6, 1.5 * lit), 0.3, 0.25), GOLD.glint, 0.9),
    ]
    fig.part('narm', arm, GREEN, grad=(S[0] + 5, S[1] - 2, W[0] - 5, W[1] + 2, [(0, GREEN.light), (0.5, GREEN.base), (1, GREEN.shadow)]),
             cel=1.1, rim=0.6, cast=1.2, cast_on=['tunic', 'cape', 'pel', 'belt', 'bald', 'shield', 'leaf'], details=det)
    fig.ctx.update(S=S, E=E, W=W, G=G, da=da)


# ---------------------------------------------------------------- la dague et le poing qui la serre
def dagger_and_fist(fig, P, UC):
    S, E, W, G, da = fig.ctx['S'], fig.ctx['E'], fig.ctx['W'], fig.ctx['G'], fig.ctx['da']
    u = unit(da)
    v = unit(da + 90)
    st = P['stretch']

    def D(x, y):                                  # repère de la dague : x vers la pointe, y en travers
        return (G[0] + u[0] * x + v[0] * y, G[1] + u[1] * x + v[1] * y)

    def DS(pts, **k):
        return sm([D(*p) for p in pts], **k)
    lit = 1 if (v[0] - v[1]) > 0 else -1          # le côté en travers tourné vers la lumière
    L_ = 26.0 + st
    # le pommeau d'or, la fusée de cuir
    pom = DS([(-5.2, -1.4), (-3.6, -1.6), (-3.2, 0.0), (-3.6, 1.6), (-5.2, 1.4), (-6.2, 0.0)], sharp=(0, 4), t=0.9)
    fig.part('pommel', pom, GOLD, grad=(*D(-4, -2 * lit), *D(-5, 2 * lit), [(0, GOLD.light), (1, GOLD.shadow)]), cel=0.4, rim=0.4,
             cast=0.5, details=[(ellipse(*D(-4.6, -0.7 * lit), 0.4, 0.3), GOLD.glint, 0.9)])
    grip = DS([(-3.8, -1.0), (3.4, -1.0), (3.4, 1.0), (-3.8, 1.0)], sharp=(0, 1, 2, 3), t=0.4)
    fig.part('grip', grip, LEATHER, cel=0.3, rim=0.3, cast=0.4)
    # la lame courte, en feuille : l'arête au milieu, le côté clair vers la lumière
    blade = DS([(4.0, -1.35), (9.0, -1.55), (16.0, -1.3), (22.0, -0.8), (L_, 0.0), (22.0, 0.8), (16.0, 1.3), (9.0, 1.55), (4.0, 1.35)],
               sharp=(0, 4, 8), t=0.85)
    bdet = [(DS([(4.0, 0.0), (L_, 0.0), (22.0, 1.5 * -lit), (9.0, 1.9 * -lit), (4.0, 1.6 * -lit)], sharp=(0, 1), t=0.7), STEEL.shadow, 0.7),
            (ribbon([D(5.0, 0.15 * lit), D(14.0, 0.2 * lit), D(L_ - 2.0, 0.05 * lit)], [0.1, 0.45, 0.1]), STEEL.glint, 0.95),
            (ribbon([D(6.0, -0.95 * -lit), D(15.0, -1.05 * -lit), D(21.0, -0.7 * -lit)], [0.1, 0.3, 0.1]), STEEL.hi, 0.7)]
    fig.part('blade', blade, STEEL, grad=(*D(L_, -2 * lit), *D(4, 2 * lit), [(0, STEEL.hi), (0.5, STEEL.light), (1, STEEL.base)]),
             cel=0.0, rim=0.0, cast=0.7, cast_on=['shield', 'leaf', 'tunic', 'belt', 'bald', 'pel'], details=bdet)
    # la garde d'or (en travers)
    guard = DS([(3.0, -3.4), (4.6, -3.0), (4.8, 0.0), (4.6, 3.0), (3.0, 3.4), (2.8, 0.0)], sharp=(0, 4), t=0.85)
    fig.part('guard', guard, GOLD, grad=(*D(4.6, -3 * lit), *D(3, 3 * lit), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.4, rim=0.4, cast=0.7, cast_on=['blade', 'tunic', 'shield'],
             details=[(ribbon([D(4.2, -2.6 * lit), D(4.4, -0.4 * lit)], [0.4, 0.2]), GOLD.glint, 0.8)])
    # le poing, vu du DOS de la main (avis du propriétaire, tour 3) : le dos de la main côté poignet, la rangée des
    # jointures parallèle à la fusée, les quatre doigts repliés dessous (l'index contre la garde) ; le pouce passe de
    # l'autre côté de la fusée, caché derrière : on ne le voit jamais.
    wv = norm(sub(W, G))                          # vers le poignet
    wy = wv[0] * v[0] + wv[1] * v[1]
    sy = 1 if wy < 0 else -1                      # le dos de la main est du côté du poignet (en travers)
    KX = (2.7, 0.9, -0.9, -2.6)                   # le milieu de chaque doigt (de l'index à l'auriculaire)
    fist = DS([(-3.4, -3.0 * sy), (0.2, -3.4 * sy), (3.2, -3.0 * sy), (3.8, -0.8 * sy), (3.8, 1.2 * sy),
               (3.4, 2.9 * sy), (2.7, 3.35 * sy), (1.8, 3.0 * sy), (0.9, 3.4 * sy), (0.0, 3.05 * sy), (-0.9, 3.35 * sy),
               (-1.75, 2.95 * sy), (-2.6, 3.05 * sy), (-3.5, 2.4 * sy), (-4.0, 0.4 * sy)], t=0.9)
    # le dos de la main (plat, il prend la lumière), les jointures en relief, le pli où les doigts se replient
    fdt = [(DS([(-3.0, -2.7 * sy), (3.0, -2.8 * sy), (3.4, -0.9 * sy), (-3.4, -0.7 * sy)], t=0.9), SKIN.light, 0.35)]
    for kx in KX:
        fdt += [(ellipse(*D(kx + 0.15, -0.05 * sy), 0.8, 0.45), SKIN.light, 0.4)]
    fdt += [(ribbon([D(-3.5, 0.9 * sy), D(0.0, 1.05 * sy), D(3.5, 0.9 * sy)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.45)]
    # les doigts repliés, séparés par des plis doux, chacun arrondi à sa deuxième jointure
    for x_ in (1.8, 0.0, -1.75):
        fdt += [(ribbon([D(x_ + 0.05, 1.2 * sy), D(x_, 2.1 * sy), D(x_ - 0.05, 3.0 * sy)], [0.1, 0.3, 0.1]), SKIN.deep, 0.4)]
    for kx in KX[:3]:
        fdt += [(ellipse(*D(kx + 0.2, 2.3 * sy), 0.5, 0.35), SKIN.light, 0.3)]
    fig.part('fist', fist, SKIN, grad=(*D(3, -3 * lit), *D(-3, 3 * lit), [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.6, cast=1.0, cast_on=['grip', 'narm', 'tunic', 'cape', 'belt', 'shield', 'blade', 'guard', 'pommel'], details=fdt)
    fig.ctx.update(tip=D(L_, 0.0), u=u)


def main():
    """corvin.svg (grand) et corvin-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/assassins-7.webp (512 px de haut) et assassins-7-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('corvin', 0.95, 512, ID_JEU), ('corvin-petit', 1.35, 160, ID_JEU + '-160')):
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
