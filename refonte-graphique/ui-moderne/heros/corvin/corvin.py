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
from atelier import Mat, sm, limb, ribbon, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
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
FRAME = (21, 12, 85, 107)      # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
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
                                              ('n', (57.4, 86.0), (56.2, 95.6), (55.8, 105.6), 45.6, 64.2, False)):
        # la braie bouffante : de la hanche au revers de la botte
        w0, w1 = 10.4, 9.0
        pant = sm([(hip[0] - w0 / 2, hip[1] - 2), (hip[0] + w0 / 2, hip[1] - 2), (knee[0] + w1 / 2 + 0.6, knee[1]),
                   (ank[0] + 4.6, 101.0), (ank[0] - 4.8, 101.0), (knee[0] - w1 / 2 - 0.4, knee[1])], t=0.9)
        pdet = [(ribbon(crpath([(hip[0] + 1.6, 88.0), (knee[0] + 2.0, 94.0), (ank[0] + 2.2, 99.4)], 10), swell(10, 1.4)), PANTS.light, 0.6),
                (ribbon(crpath([(hip[0] - 2.4, 88.0), (knee[0] - 2.0, 95.0), (ank[0] - 2.6, 99.6)], 10), swell(10, 1.6)), PANTS.shadow, 0.6),
                (ellipse(knee[0] + 1.0, knee[1] - 0.6, 2.2, 1.2, -20), PANTS.hi, 0.25)]
        fig.part(nm + 'pant', pant, PANTS, grad=(hip[0] + 6, 86, hip[0] - 6, 100, [(0, PANTS.light), (0.5, PANTS.base), (1, PANTS.shadow)]),
                 cel=1.0, rim=0.6, cast=0.6, details=pdet)
        # la botte : tige, pied (talon, bout arrondi vers l'avant), semelle épaisse
        x0, x1 = ank[0] - 4.6, ank[0] + 4.4
        boot = sm([(x0, 100.6), (x1, 100.6), (x1 + 0.2, 106.0), (x1 + 2.4, 108.6), (toe - 3.0, 110.0), (toe - 0.4, 112.0),
                   (toe, 114.4), (toe - 0.6, GRD), (heel + 0.6, GRD), (heel, 114.0), (heel + 0.4, 110.6), (x0 - 0.2, 107.6)],
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
    bald = ribbon([(52.6, 58.0), (58.4, 64.4), (63.6, 70.2), (65.2, 72.4)], [2.0, 2.0, 2.0, 1.9], sharp_ends=False)
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
