# Aldric (knights-3, feu, rare, tireur) redessiné en VECTORIEL lisse, dans le style moderne de l'interface (refonte de
# tous les héros, décision du propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py).
#
#   python3 refonte-graphique/ui-moderne/heros/aldric/aldric.py      # → aldric.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/aldric.txt) : un jeune moine du feu, vif et sûr de lui.
# Trois quarts vers la droite, garde de combat moyenne : jambe lointaine en avant (genou fléchi), jambe proche en
# arrière, pieds nus à plat. Bras lointain tendu vers l'ennemi, le poing serré sur le bord d'un anneau de jet (chakram,
# vu de face, trois dents recourbées) ; bras proche ramené, le poing à la hanche qui tient le second anneau (vu de
# biais, il pend sous le poing). Torse nu sec en V, écharpe orange en diagonale (de l'épaule lointaine à la hanche
# proche), chapelet de perles de bois avec une perle rouge et un gland, bandes de toile aux avant-bras, ceinture de
# tissu rouge nouée devant (deux pans), pantalon orange bouffant serré aux chevilles par des liens rouges.
# Tête : crâne rasé (repousse mauve dans l'ombre, reflet en haut à droite), chignon noir lié de rouge, bandeau rouge
# noué derrière (deux pans qui volent), sourcils noirs droits froncés, yeux ambre plissés, nez droit, bouche serrée au
# coin qui remonte, grande oreille.
#
# Coordonnées = pixels du dessin pixel art (même toile : le point « sol » (64, 116) est le même), pour se poser au même
# endroit dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; les membres sont d'un seul
# tenant (épaule → coude → poignet, hanche → genou → cheville) ; ce qui entoure (bandeau, écharpe, bandes de toile,
# liens) est découpé DANS la forme qu'il entoure ; les bandes de toile couvrent le raccord poignet-poing.
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import (rot, add, lerp, matmix, body_limb, ik, Seg, inv, poly_of, geom_shape, fuse, clip,  # noqa: E402
                    ring_map, chakram_geom, stations, edges)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'knights-3'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffd2a0', '#f2a66c', '#d27a4e', '#a04a40', '#682a36')
SCALP = Mat('#f6cdb0', '#e0a488', '#b47c70', '#7e5266', '#4c3048')
HAIR = Mat('#a49cd0', '#6c6494', '#40365c', '#261c36', '#120c1e')
RED = Mat('#ff9a78', '#ee5a42', '#bc2a32', '#7c1630', '#3e0c20')
ORANGE = Mat('#ffcc66', '#f88c2c', '#d85a1e', '#9a3024', '#52162a')
BRONZE = Mat('#fff2b8', '#ecb24e', '#be7a30', '#7e4224', '#40201c', glint='#fffcec')
LINEN = Mat('#fffcf2', '#fff6e2', '#e2d6c0', '#aa9ab6', '#6c5c84')
WOOD = Mat('#eaa86a', '#c27a44', '#8c4a2a', '#5a2a22', '#2c1420')
EYE_W, IRIS, IRIS_D, PUPIL = '#f4ece6', '#f4a424', '#b86418', '#1c0c14'
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
BRONZE_HOT = Mat('#fffbe4', '#fff0a0', '#ffc24a', '#f07a22', '#b8401a', glint='#ffffff')

GRD = 116.0
FEET = (64.0, 116.0)
FRAME = (30.0, 9.0, 98.0, 110.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse (genoux, pieds au sol) ; lean : il se penche en avant (+) ;
#   head / tilt : la tête ; ph : la phase des pans (bandeau, ceinture) ; tail : les pans du bandeau se relèvent (+)
#   ou retombent (−) ; pg : les pans de la ceinture se balancent ; blink : yeux fermés ;
#   fw : le poignet lointain ; fbend : le coude lointain ; fsh : le bras lointain dans le plan de l'image (0 : en
#   raccourci, tendu vers l'ennemi ; 1 : en travers de la poitrine) ; ffront : le bras lointain passe devant le buste ;
#   frot : le poing lointain tourne ; ringF : l'anneau lointain est dans la main (0/1) ; rF_sy : il se couche à plat ;
#   rF_spin : il tourne dans son plan ; rF_rot : l'ovale penche ;
#   nw : le poignet proche ; nrot : le poing proche tourne ; ringN : l'anneau proche est dans la main ;
#   fa : la cheville lointaine (coup de pied) ; fext : la jambe lointaine se déplie (0 : raccourcie, 1 : de profil) ;
#   foot : l'angle du pied lointain (0 : à plat, −90 : la plante vers l'ennemi) ; hot : les anneaux chauffent (0..2) ;
#   gl / gn : le reflet qui court sur l'anneau lointain / proche (degrés, None : aucun).
FS0 = (84.6, 56.6)                       # l'épaule lointaine
FW0 = (97.6, 56.5)                       # le poignet lointain, au repos
NS0 = (49.8, 57.8)                       # l'épaule proche
NE0 = (41.0, 70.2)                       # le coude proche, au repos
NW0 = (47.6, 79.4)                       # le poignet proche, au repos
NL1, NL2 = math.dist(NS0, NE0), math.dist(NE0, NW0)
HIP = (66.0, 84.0)                       # le pivot du buste
NECK = (67.0, 49.0)                      # le pivot (et le centre d'agrandissement) de la tête
FHIP, NHIP = (72.6, 86.0), (60.6, 86.4)  # les hanches
FA0, NA0 = (82.6, 106.6), (49.6, 106.6)  # les chevilles (milieu du lien rouge)
RC_F = (112.2, 56.0)                     # le centre de l'anneau lointain, au repos
RC_N = (48.3, 94.4)                      # le centre de l'anneau proche, au repos
RR, Rr = 10.2, 5.9                       # rayons de l'anneau

_E, _W = ik(FS0, FW0, 8.4, 6.2, 1.0)
FA_REST = math.degrees(math.atan2(_W[1] - _E[1], _W[0] - _E[0]))

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, tail=0.0, pg=0.0, blink=0.0,
            fw=FW0, fbend=1.0, fsh=0.0, ffront=0.0, frot=0.0, ringF=1.0, rF_sy=1.0, rF_spin=0.0, rF_rot=0.0, rF_da=0.0,
            nw=NW0, nrot=0.0, ringN=1.0, fa=FA0, fext=0.0, foot=0.0, fkb=-1.0, hot=0.0, gl=None, gn=None,
            shift=0.0, lift=0.0)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    _LAST.clear()
    fig = Figure(*frame, ow=ow)
    hot = P['hot']
    bronze = matmix(BRONZE, BRONZE_HOT, 0.5 * hot)

    # ---- le squelette : une matrice par groupe de morceaux ----
    ROOTM = mT(P['shift'], -P['lift'])
    dyb = P['crouch'] * 0.85
    PEL = mchain(ROOTM, mT(0, dyb))
    U = mchain(PEL, mT(P['lean'] * 0.35, 0), mR(P['lean'] * 1.1, *HIP))
    br = P['breath']
    UC = mchain(U, mT(0, -0.6 * br))
    TOR = mchain(U, mS(1, 1 + 0.014 * br, 66, 80))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))

    # ======================================================================== les pans du bandeau (derrière tout)
    ph, tl = P['ph'], P['tail']
    tails = band_tails(ph, tl)
    for name, sh, det in tails:
        fig.part(name, sh, RED, cel=0.8, rim=0.6, cast=0.9, details=det)

    # ======================================================================== le bras lointain (tendu), derrière le buste
    # (devant le buste quand il le ramène en travers de la poitrine : ffront)
    far_parts = []

    def far_arm():
        k = P['fsh']
        L1, L2 = 8.4 + 4.2 * k, 6.2 + 6.6 * k
        S = FS0
        E, W = ik(S, P['fw'], L1, L2, 1)
        E2, W2 = ik(S, P['fw'], L1, L2, -1)
        if E2[1] > E[1]:                         # le coude lointain reste toujours en bas
            E, W = E2, W2
        arm = body_limb([S, E, W], [(0, 4.6, 4.4), (0.3, 4.2, 4.1), (0.55, 3.6, 3.5), (0.72, 3.5, 3.4), (1, 3.2, 3.1)],
                        n=20, soft=True)
        a1, a2 = Seg(S, E), Seg(E, W)
        ad = [(ellipse(*a1.at(0.55, 1.2), 2.2, 3.6, a1.deg - 90), SKIN.light, 0.4),
              (ellipse(*a2.at(0.3, 1.0), 1.6, 2.6, a2.deg - 90), SKIN.light, 0.35)]
        fig.part('farm', arm, SKIN, cel=1.5, rim=0.6, cast=1.3 if P['ffront'] > 0.5 else 0, details=ad)
        # le poing (dessiné au repos, posé par un mouvement rigide : il suit l'avant-bras)
        fa_ = a2.deg + P['frot']
        flip = math.cos(math.radians(fa_)) < 0
        M = fist_matrix(FW0, FA_REST, W, fa_, flip)
        fist, fdet, thumb = far_fist()
        # l'anneau, tenu par son bord (celui qui passe dans le poing)
        if P['ringF'] > 0.5:
            G = mapp(M, (104.2, 56.0))
            q = mapp(M, (105.2, 56.0))
            d = rot((q[0] - G[0], q[1] - G[1]), P['rF_da'])   # du poing vers le centre de l'anneau
            sy = P['rF_sy']
            Rm = (RR + Rr) / 2 * math.hypot(d[0], d[1] * sy)
            C = (G[0] + d[0] * Rm, G[1] + d[1] * Rm)
            chakram(fig, 'ringF', C, 1.0, sy, P['rF_rot'], P['rF_spin'], bronze, P['gl'], cast=0.9)
        fig.part('ffist', fist.map(lambda p: mapp(M, p)), SKIN, cel=1.2, rim=0.6, cast=0.9,
                 details=[(s.map(lambda p: mapp(M, p)), c, o) for s, c, o in fdet])
        fig.part('fthumb', thumb.map(lambda p: mapp(M, p)), SKIN, cel=0.7, rim=0.55, cast=0.7, cast_on=['ffist', 'ringF'])
        # la bande de toile, autour de l'avant-bras et de la base du poing (elle cache le raccord)
        bandage(fig, 'fband', a2, arm, fist.map(lambda p: mapp(M, p)), a2.L - 4.6, a2.L + 1.3, 3.3)
        return S, E, W

    # ======================================================================== les jambes
    def leg(name, Hr, A, L1_, L2_, bend, keys, foot_pts, foot_ang, cast_on):
        H = mapp(PEL, Hr)
        A = mapp(ROOTM, A)
        sc = min(1.0, math.dist(H, A) * 1.06 / (L1_ + L2_))
        K, A2 = ik(H, A, L1_ * sc, L2_ * sc, bend)
        A = A2
        # le pied nu (sous le lien) : dessiné à plat au repos autour de la cheville, tourné par foot_ang
        fo_shape, fo_det, A0 = foot_pts
        Mf = mchain(mT(A[0] - A0[0], A[1] - A0[1]), mR(foot_ang, *A0))
        fig.part(name + 'foot', fo_shape.map(lambda p: mapp(Mf, p)), SKIN, cel=1.2, rim=0.6, cast=0.6, cast_on=['fleg', 'ffoot'],
                 details=[(s.map(lambda p: mapp(Mf, p)), c, o) for s, c, o in fo_det])
        # le pantalon bouffant : hanche → genou → cheville, d'un seul tenant
        sn0 = Seg(K, A)
        Ap = sn0(sn0.L - 2.4)                    # le pantalon s'arrête au-dessus du lien
        pants = body_limb([H, K, Ap], keys, n=24)
        th, sn = Seg(H, K), Seg(K, Ap)
        sd = 1 if name == 'f' else -1
        det = []
        # les plis : deux plis courbes qui retombent vers le lien (le tissu bouffe), un pli au creux du genou
        det += [(ribbon([sn.at(0.30, -2.2), sn.at(0.58, -1.0), sn.at(0.86, 0.6)], [0.1, 1.1, 0.1]), ORANGE.shadow, 0.6),
                (ribbon([sn.at(0.42, 2.6), sn.at(0.70, 2.4), sn.at(0.94, 1.4)], [0.1, 0.9, 0.1]), ORANGE.shadow, 0.5),
                (ribbon([sn.at(0.18, 3.4), sn.at(0.48, 4.4), sn.at(0.80, 3.4)], [0.1, 1.2, 0.1]), ORANGE.hi, 0.55),
                (ribbon([th.at(0.25, 2.6), th.at(0.6, 3.4), th.at(0.95, 3.0)], [0.1, 1.3, 0.1]), ORANGE.hi, 0.5),
                (ribbon([th.at(0.5, -1.2), th.at(0.82, -2.6), sn.at(0.12, -3.6)], [0.1, 1.0, 0.1]), ORANGE.deep, 0.35)]
        fig.part(name + 'leg', pants, ORANGE, cel=1.6, rim=0.65, cast=1.0, cast_on=cast_on, details=det)
        # le lien rouge à la cheville, en travers du bas de la jambe (il serre le pantalon et cache le raccord du pied)
        tie_c = A
        tie = xf(rpoly([(-2.6, -3.5), (2.2, -3.3), (2.4, 3.3), (-2.6, 3.5)], 1.1), tie_c[0], tie_c[1], sn.deg)
        fig.part(name + 'tie', tie, RED, cel=0.8, rim=0.6, cast=0.8, cast_on=[name + 'foot'],
                 details=[(xf(ribbon([(-2.6, -3.0), (-0.6, 0.0), (1.2, 3.0)], [0.1, 0.8, 0.1]), tie_c[0], tie_c[1], sn.deg), RED.shadow, 0.6),
                          (xf(ribbon([(-1.0, -3.2), (0.6, -0.4), (1.6, 2.6)], [0.1, 0.5, 0.1]), tie_c[0], tie_c[1], sn.deg), RED.hi, 0.6)])
        return H, K, A

    # la jambe lointaine (en avant, genou fléchi), puis la jambe proche (en arrière, bien plantée)
    fe = P['fext']
    fleg = leg('f', FHIP, P['fa'], 12.8 + 8.4 * fe, 10.6 + 2.6 * fe, P['fkb'],
               [(0, 7.0, 7.0), (0.4, 6.4, 7.0), (0.56, 6.6, 7.6), (0.78, 6.0, 6.4), (0.92, 4.6, 4.8), (1, 3.9, 3.9)],
               foot_far(), P['foot'], None)
    nleg = leg('n', NHIP, NA0, 12.2, 10.4, -1,
               [(0, 7.0, 7.0), (0.42, 6.6, 6.6), (0.58, 7.0, 6.8), (0.78, 6.2, 6.0), (0.92, 4.6, 4.6), (1, 3.9, 3.9)],
               foot_near(), 0.0, None)

    if P['ffront'] <= 0.5:
        FAR = far_arm()

    # ======================================================================== le buste (avec le cou)
    torso = sm([(57.6, 44.0), (57.6, 48.6), (55.6, 51.4), (51.0, 53.2), (47.4, 56.0), (47.6, 61.0), (50.4, 65.2),
                (52.2, 70.0), (52.8, 75.0), (53.0, 80.6), (62.0, 82.6), (70.0, 82.8), (77.8, 81.2), (78.0, 75.6),
                (77.4, 71.0), (78.6, 66.0), (80.6, 61.8), (83.4, 59.0), (86.6, 56.2), (86.0, 53.4), (82.6, 51.8),
                (78.8, 50.8), (75.2, 49.0), (74.2, 44.8)])
    det = [(torso, ('lin', 54, 66, 66, 62, [(0, SKIN.deep, 0.4), (1, SKIN.deep, 0)]), 1)]
    # les pectoraux plats et nets (le proche plus large, trois quarts) : la plaque éclairée, l'ombre douce dessous
    det += [(sm([(53.6, 55.4), (60.6, 54.2), (66.4, 55.2), (66.8, 59.6), (64.4, 62.0), (58.6, 62.0), (54.6, 59.6)]), SKIN.light, 0.5),
            (sm([(54.0, 60.6), (58.8, 62.8), (64.6, 63.0), (67.0, 60.4), (67.2, 62.8), (64.6, 64.6), (58.6, 64.4), (53.6, 62.4)]), SKIN.shadow, 0.7),
            (sm([(68.4, 55.4), (73.6, 54.2), (78.6, 55.8), (78.4, 59.6), (74.6, 61.2), (69.0, 60.6)]), SKIN.hi, 0.4),
            (sm([(68.4, 60.6), (74.4, 61.8), (78.6, 59.8), (78.0, 62.0), (74.4, 63.6), (68.6, 62.8)]), SKIN.shadow, 0.6),
            (ribbon([(67.4, 55.0), (67.6, 59.0), (67.4, 63.4)], [0.1, 1.0, 0.2]), SKIN.shadow, 0.55)]
    # les abdominaux dessinés : la ligne du milieu (décalée vers la droite, trois quarts), trois paires de blocs qui
    # rétrécissent vers le bas ; des creux doux, le haut de chaque bloc éclairé — jamais des cases
    det += [(ribbon([(67.4, 63.6), (67.2, 68.8), (67.4, 73.6), (67.8, 77.4)], [0.2, 1.0, 0.9, 0.2]), SKIN.shadow, 0.7),
            (ribbon([(57.0, 67.2), (62.0, 67.8), (66.8, 67.4)], [0.1, 0.9, 0.3]), SKIN.shadow, 0.6),
            (ribbon([(57.8, 71.8), (62.4, 72.2), (66.8, 71.8)], [0.1, 0.8, 0.3]), SKIN.shadow, 0.55),
            (ribbon([(68.0, 67.4), (72.0, 67.6), (75.6, 66.8)], [0.3, 0.7, 0.1]), SKIN.shadow, 0.5),
            (ribbon([(68.0, 71.8), (71.6, 72.0), (75.0, 71.2)], [0.3, 0.6, 0.1]), SKIN.shadow, 0.45),
            (rpoly([(57.6, 64.2), (66.6, 63.9), (66.4, 66.6), (58.0, 66.6)], 1.3), SKIN.light, 0.22),
            (rpoly([(58.2, 68.6), (66.6, 68.4), (66.4, 71.0), (58.6, 71.0)], 1.2), SKIN.light, 0.18),
            (rpoly([(59.2, 73.0), (66.8, 72.8), (66.8, 75.6), (60.0, 75.4)], 1.2), SKIN.light, 0.15),
            (rpoly([(68.2, 64.2), (75.4, 63.8), (75.0, 66.4), (68.2, 66.6)], 1.2), SKIN.hi, 0.22),
            (rpoly([(68.2, 68.4), (74.8, 68.2), (74.4, 70.8), (68.2, 71.0)], 1.1), SKIN.hi, 0.18),
            (rpoly([(68.3, 72.8), (74.0, 72.6), (73.6, 75.2), (68.4, 75.4)], 1.1), SKIN.hi, 0.15)]
    # les flancs (taille fine) ; le muscle du cou (de l'oreille à la clavicule) ; les clavicules
    det += [(ribbon([(54.6, 64.6), (55.6, 70.0), (55.4, 76.0)], [0.1, 0.9, 0.1]), SKIN.shadow, 0.45),
            (ribbon([(76.2, 64.6), (75.6, 70.0), (75.6, 76.0)], [0.1, 0.8, 0.1]), SKIN.shadow, 0.5),
            (ribbon([(62.0, 46.0), (64.6, 50.0), (66.2, 53.6)], [0.1, 1.0, 0.1]), SKIN.shadow, 0.45),
            (ribbon([(56.0, 53.4), (61.0, 53.8), (65.4, 53.4)], [0.1, 0.7, 0.1]), SKIN.hi, 0.5),
            (ribbon([(69.6, 53.6), (73.4, 53.2), (77.4, 53.8)], [0.1, 0.6, 0.1]), SKIN.hi, 0.45)]
    fig.part('torso', torso, SKIN, cel=1.9, rim=0.7, cast=1.2, details=det, occl=(SKIN.deep, 0.2, 3.0))

    # ---- l'écharpe orange de moine : une seule diagonale, de l'épaule lointaine à la hanche proche (découpée dans le
    # buste : elle passe sur l'épaule et suit le torse) ----
    sc_c = [(78.6, 48.6), (73.0, 56.4), (65.6, 64.6), (58.6, 72.0), (53.4, 79.0)]
    scarf_band = ribbon_flat(sc_c, [11.0, 7.4, 6.8, 6.8, 7.2])
    scarf = clip(scarf_band, torso)
    if scarf is not None:
        fig.part('scarf', scarf, ORANGE, cel=1.0, rim=0.7, cast=1.0, cast_on=['torso'],
                 details=[(ribbon([(75.6, 52.0), (69.4, 60.4), (61.6, 68.8), (55.2, 76.6)], [0.1, 1.2, 1.2, 0.2]), ORANGE.shadow, 0.55),
                          (ribbon([(79.2, 51.8), (73.4, 59.6), (66.2, 67.4), (59.0, 75.6)], [0.1, 0.9, 0.9, 0.1]), ORANGE.hi, 0.6),
                          (ribbon([(72.6, 53.8), (67.6, 60.8)], [0.1, 0.6, 0.1]), ORANGE.light, 0.6)])

    # ---- le chapelet : petites perles de bois sombre, une perle rouge en bas, un gland ----
    beads = [(57.6, 53.2, 0.95), (58.0, 55.2, 0.95), (58.7, 57.1, 0.95), (59.7, 58.8, 0.95), (61.1, 60.1, 0.95),
             (62.8, 60.9, 0.95), (68.0, 60.7, 0.95), (69.6, 59.6, 0.95), (70.9, 58.0, 0.95), (71.9, 56.3, 0.95),
             (72.6, 54.5, 0.95), (73.0, 52.7, 0.9)]
    cord = [(57.4, 51.6)] + [(x, y) for x, y, _ in beads[:6]] + [(65.4, 61.4)] + [(x, y) for x, y, _ in beads[6:]] + [(73.2, 51.0)]
    fig.part('cord', ribbon(cord, [0.1] + [0.55] * (len(cord) - 2) + [0.1]), WOOD, cel=0, rim=0, cast=0.4, cast_on=['torso', 'scarf'], outline=False)
    for i, (x, y, r) in enumerate(beads):
        fig.part('bead%d' % i, ellipse(x, y, r * 1.05, r), WOOD, cel=0.4, rim=0.3, cast=0.5, cast_on=['torso', 'scarf'],
                 details=[(ellipse(x + 0.3 * r, y - 0.35 * r, 0.42 * r, 0.3 * r, -25), WOOD.hi, 0.9)])
    tassel = sm([(65.0, 62.4), (66.0, 62.4), (66.6, 64.6), (66.9, 66.6), (66.0, 66.2), (65.4, 66.9), (64.6, 66.3),
                 (64.0, 66.8), (64.3, 64.6)], sharp=(3, 4, 5, 6, 7))
    fig.part('tassel', tassel, RED, cel=0.5, rim=0.4, cast=0.6, cast_on=['torso'],
             details=[(ribbon([(65.6, 62.8), (65.8, 64.6), (66.0, 66.0)], [0.1, 0.5, 0.1]), RED.hi, 0.6)])
    fig.part('rbead', ellipse(65.4, 61.4, 1.45, 1.35), RED, cel=0.5, rim=0.4, cast=0.6, cast_on=['torso', 'tassel'],
             details=[(ellipse(65.9, 60.9, 0.55, 0.4, -25), RED.hi, 0.95)])

    # ======================================================================== la ceinture de tissu rouge, nouée devant
    belt = sm([(52.2, 76.6), (58.0, 76.0), (66.0, 76.6), (73.0, 76.4), (78.6, 75.4), (79.2, 78.8), (78.8, 82.6),
               (72.0, 83.4), (65.0, 83.6), (58.0, 83.0), (52.4, 82.4), (51.8, 79.4)])
    bd = [(ribbon([(53.0, 79.4), (58.0, 79.0), (63.4, 79.8), (67.0, 79.6)], [0.1, 1.1, 0.9, 0.1]), RED.shadow, 0.55),
          (ribbon([(53.4, 77.4), (59.0, 77.0), (65.0, 77.6)], [0.1, 0.7, 0.1]), RED.hi, 0.55),
          (ribbon([(73.2, 80.6), (76.0, 79.8), (78.6, 79.6)], [0.1, 0.8, 0.1]), RED.shadow, 0.5),
          (ribbon([(72.8, 77.4), (75.6, 76.8), (78.4, 76.4)], [0.1, 0.6, 0.1]), RED.hi, 0.55)]
    fig.part('belt', belt, RED, cel=1.0, rim=0.6, cast=1.0, details=bd)
    # les deux pans qui pendent sur la cuisse lointaine (ils se balancent : pg)
    pg = P['pg']
    for name, pts, w0, w1 in (('sash1', [(69.4, 81.0), (69.2, 85.0), (68.8, 89.0), (68.6, 92.6)], 3.0, 3.4),
                              ('sash2', [(72.6, 81.0), (73.2, 84.6), (73.8, 88.2), (74.4, 90.8)], 2.6, 3.0)):
        pts = [(x - 0.35 * pg * ((y - 81) / 10) ** 1.3 * (1 + 0.3 * math.sin(ph + y * 0.2)), y) for x, y in pts]
        sh = cut_strip(pts, w0, w1, slant=(1 if name == 'sash1' else -1))
        fig.part(name, sh, RED, cel=0.8, rim=0.55, cast=0.9,
                 details=[(ribbon([lerp(pts[0], pts[1], 0.5), pts[2], lerp(pts[2], pts[3], 0.8)], [0.1, 0.6, 0.1]), RED.shadow, 0.55)])
    knot = sm([(67.6, 77.0), (70.4, 75.8), (73.4, 76.4), (74.2, 78.8), (73.6, 81.4), (70.8, 82.4), (68.2, 81.6),
               (67.2, 79.4)])
    fig.part('knot', knot, RED, cel=0.8, rim=0.6, cast=1.0,
             details=[(ribbon([(69.0, 76.6), (70.4, 79.2), (70.6, 82.0)], [0.1, 0.9, 0.1]), RED.shadow, 0.6),
                      (ribbon([(71.0, 76.4), (72.8, 78.2), (73.2, 80.6)], [0.1, 0.7, 0.1]), RED.hi, 0.6),
                      (ribbon([(67.8, 79.0), (69.0, 80.6), (70.4, 81.6)], [0.1, 0.6, 0.1]), RED.deep, 0.35)])

    if P['ffront'] > 0.5:
        FAR = far_arm()

    # ======================================================================== le bras proche (ramené), poing à la hanche
    S = (NS0[0], NS0[1] - 0.6 * br)
    E, W = ik(S, P['nw'], NL1, NL2, 1)
    if E[0] > S[0] - 2:                      # le coude part toujours vers l'arrière (à gauche)
        E, W = ik(S, P['nw'], NL1, NL2, -1)
    a1, a2 = Seg(S, E), Seg(E, W)
    na = math.degrees(math.atan2(NW0[1] - NE0[1], NW0[0] - NE0[0]))
    M = fist_matrix(NW0, na, W, a2.deg + P['nrot'], False)
    fist, fdet, thumb = near_fist()
    fist_m = fist.map(lambda p: mapp(M, p))
    if P['ringN'] > 0.5:
        G = mapp(M, (48.4, 86.2))
        C = (G[0] + (RC_N[0] - 48.4), G[1] + (RC_N[1] - 86.2))
        chakram(fig, 'ringN', C, 0.6, 0.88, -6.0 + (a2.deg + P['nrot'] - na) * 0.6, 15.0, bronze, P['gn'], cast=0.9)
    arm = body_limb([S, E, W], [(0, 5.3, 5.3), (0.16, 5.0, 4.6), (0.3, 4.3, 4.4), (0.5, 3.7, 3.7), (0.6, 3.6, 3.6),
                                (0.7, 4.0, 3.8), (1, 3.3, 3.2)], n=28, soft=True)
    # l'épaule ronde (le deltoïde) fondue avec le bras : une seule forme, aucune couture
    delt = ellipse(S[0] - 0.4, S[1] - 0.2, 5.5, 5.1, a1.deg - 90)
    arm, _ = fuse([arm, delt], smooth=1.2)
    ad = [(ellipse(*a1.at(0.1, 1.2), 3.8, 4.4, a1.deg), SKIN.light, 0.45),
          (ribbon([a1.at(0.18, -4.4), a1.at(0.34, -1.0), a1.at(0.28, 3.6)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.4),
          (ellipse(*a1.at(0.62, 1.8), 2.0, 4.0, a1.deg - 90), SKIN.light, 0.35),
          (ribbon([a1.at(0.42, 3.6), a1.at(0.66, 3.8), a1.at(0.88, 3.2)], [0.1, 0.7, 0.1]), SKIN.hi, 0.35)]
    fig.part('narm', arm, SKIN, cel=1.7, rim=0.7, cast=1.2, details=ad,
             cast_on=['torso', 'scarf', 'belt', 'nleg', 'fleg', 'ringN', 'bead0', 'bead1', 'cord'])
    fig.part('nfist', fist_m, SKIN, cel=1.2, rim=0.6, cast=1.0, details=[(s.map(lambda p: mapp(M, p)), c, o) for s, c, o in fdet])
    fig.part('nthumb', thumb.map(lambda p: mapp(M, p)), SKIN, cel=0.7, rim=0.55, cast=0.7, cast_on=['nfist', 'ringN'])
    bandage(fig, 'nband', a2, arm, fist_m, a2.L - 5.6, a2.L + 1.4, 4.0)

    # ======================================================================== la tête
    head = sm([(51.6, 35.0), (51.9, 31.0), (53.4, 27.8), (56.2, 25.2), (60.0, 23.6), (64.8, 23.0), (69.8, 23.4),
               (74.4, 25.2), (77.8, 28.0), (79.8, 31.4), (80.8, 34.8), (81.0, 36.8), (80.7, 38.3), (82.6, 41.0),
               (82.4, 42.4), (81.4, 43.0), (81.1, 43.9), (81.2, 45.2), (80.6, 46.7), (79.9, 48.2), (78.4, 49.7),
               (75.8, 50.5), (72.0, 50.4), (67.6, 49.2), (62.0, 46.8), (58.0, 45.8), (54.4, 44.4), (52.4, 41.0)],
              sharp=(13,))
    hd = []
    # le crâne rasé : la repousse (mauve dans l'ombre, claire dans la lumière) au-dessus du bandeau et derrière
    # l'oreille ; un reflet brillant en haut à droite
    scalp_zone = sm([(50.0, 20.0), (84.0, 20.0), (84.0, 31.4), (60.0, 31.0), (59.4, 33.6), (58.6, 38.0), (58.4, 44.6),
                     (50.0, 46.0)], sharp=(0, 1, 2, 7))
    scalp = clip(scalp_zone, head)
    hd += [(scalp, ('lin', 76, 24, 54, 40, [(0, SCALP.hi), (0.3, SCALP.light), (0.7, SCALP.base), (1, SCALP.shadow)]), 1),
           (ellipse(70.6, 26.6, 3.4, 1.5, -18), SCALP.hi, 0.85),
           (ellipse(71.8, 26.0, 1.3, 0.6, -18), '#fff6ec', 0.9)]
    # le plan de côté (vers l'oreille) dans l'ombre, la joue proche à mi-ton, le plan de face éclairé
    hd += [(sm([(58.4, 34.4), (62.0, 34.8), (64.0, 38.0), (64.6, 42.4), (66.0, 47.6), (62.0, 46.8), (58.4, 45.6)]), SKIN.shadow, 0.28),
           (sm([(73.6, 34.4), (80.6, 34.6), (81.0, 39.0), (79.8, 43.6), (80.6, 47.0), (77.6, 49.6), (75.6, 46.0),
                (74.0, 41.0)]), SKIN.light, 0.45)]
    # la pommette haute éclairée, sous l'oeil proche
    hd += [(ellipse(71.8, 41.6, 2.9, 1.2, -8), SKIN.hi, 0.5),
           (ellipse(72.6, 41.3, 1.1, 0.5, -8), '#fff0d8', 0.5)]
    # l'ombre douce sous l'arcade (les orbites), le creux de la tempe
    hd += [(sm([(65.6, 37.0), (70.0, 36.6), (73.6, 37.4), (73.2, 39.6), (69.6, 40.6), (66.4, 39.8)]), SKIN.shadow, 0.35),
           (sm([(76.4, 37.2), (79.6, 36.8), (80.6, 38.4), (79.4, 40.0), (77.0, 39.8)]), SKIN.shadow, 0.3)]
    # le nez droit : le flanc dans l'ombre (côté joue proche), l'arête éclairée, le bout, la narine, l'ombre dessous
    hd += [(sm([(74.6, 37.6), (76.4, 37.6), (79.6, 41.0), (80.6, 42.8), (78.6, 43.0), (76.4, 41.6)]), SKIN.shadow, 0.55),
           (ribbon([(76.0, 36.8), (78.6, 38.6), (81.2, 40.6)], [0.2, 0.9, 0.6]), SKIN.hi, 0.75),
           (ellipse(81.6, 41.2, 0.9, 0.6, 30), '#fff0d8', 0.85),
           (sm([(78.6, 42.2), (80.0, 41.8), (80.8, 42.6), (79.8, 43.2)]), SKIN.deep, 0.8),
           (ribbon([(77.8, 43.4), (79.6, 43.7), (81.2, 43.4)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.6)]
    # les yeux ambre plissés (même ligne ; le lointain plus étroit, son coin intérieur caché par l'arête du nez) ;
    # le regard file vers l'ennemi (iris vers la droite)
    eyeN = sm([(67.0, 38.6), (68.8, 37.7), (71.0, 37.5), (73.2, 38.1), (74.0, 38.8), (71.8, 39.8), (69.2, 39.8)], sharp=(0, 4))
    eyeF = sm([(77.0, 38.6), (78.4, 37.8), (80.1, 37.6), (80.8, 38.2), (79.8, 39.5), (78.0, 39.5)], sharp=(0, 3))
    for e, (ix, iy, ir), (cx, cy) in ((eyeN, (71.7, 38.7, 1.32), (70.4, 38.7)), (eyeF, (79.5, 38.6, 1.05), (78.9, 38.6))):
        if P['blink'] > 0.5:
            hd += [(e.scale(1.08, 1.4, cx, cy), SKIN.shadow, 0.9), (e, SKIN.base, 1),
                   (ribbon([(e.bbox()[0], cy + 0.3), (cx, cy + 0.8), (e.bbox()[2], cy + 0.1)], [0.1, 0.55, 0.1]), '#3a1426', 0.95)]
        else:
            iris = ellipse(ix, iy, ir, ir * 1.02)
            hd += [(e.scale(1.1, 1.36, cx, cy - 0.15), '#3a1426', 0.95), (e, EYE_W, 1)]
            hd += [(clip(iris, e), ('rad', ix + 0.3, iy - 0.4, ir * 1.3, ir * 1.3, [(0, '#ffd870'), (0.55, IRIS), (1, IRIS_D)]), 1),
                   (clip(ellipse(ix + 0.25 * ir, iy, 0.46 * ir, 0.55 * ir), e), PUPIL, 1),
                   (clip(sm([(e.bbox()[0] - 1, 37.0), (e.bbox()[2] + 1, 37.0), (e.bbox()[2] + 1, 38.4), (cx, 38.6),
                             (e.bbox()[0] - 1, 38.9)]), e), '#5a2a30', 0.35),
                   (ellipse(ix + 0.5 * ir, iy - 0.45 * ir, 0.3 * ir, 0.26 * ir), '#ffffff', 1)]
    # les paupières du haut, lourdes (le regard plissé) : un trait sombre épais qui déborde au coin extérieur
    hd += [(ribbon([(66.6, 38.9), (68.6, 37.6), (71.2, 37.2), (73.4, 37.8), (74.2, 38.6)], [0.3, 0.9, 0.9, 0.7, 0.2]), '#2c1020', 0.95),
           (ribbon([(77.0, 38.5), (78.4, 37.6), (80.2, 37.4), (81.0, 38.0)], [0.2, 0.7, 0.7, 0.2]), '#2c1020', 0.95),
           (ribbon([(68.6, 40.1), (71.2, 40.2), (73.6, 39.4)], [0.1, 0.45, 0.1]), SKIN.deep, 0.45)]
    # les sourcils noirs droits et froncés (le bout intérieur plus bas), le dessus lavande
    browN = sm([(64.4, 35.9), (67.4, 34.8), (71.0, 34.9), (74.6, 36.2), (74.4, 37.6), (70.8, 36.8), (67.4, 36.8), (64.8, 37.1)], sharp=(0, 3))
    browF = sm([(76.4, 37.0), (78.2, 35.5), (80.6, 34.7), (81.3, 35.5), (80.4, 36.5), (78.2, 37.6)], sharp=(0, 3))
    hd += [(browN, ('lin', 70, 35, 70, 37.4, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.deep)]), 1),
           (browF, ('lin', 79, 35, 79, 37.4, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.deep)]), 1),
           (ribbon([(65.4, 35.6), (68.6, 35.2), (72.4, 35.7)], [0.1, 0.45, 0.1]), HAIR.hi, 0.6),
           (ribbon([(74.4, 36.4), (75.6, 35.6), (76.6, 35.2)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.5)]
    # la bouche serrée, le coin proche qui remonte (assurance) ; la lèvre du bas éclairée ; le menton ferme
    hd += [(ribbon([(75.2, 44.0), (76.4, 44.7), (78.4, 45.0), (80.8, 44.8)], [0.2, 0.75, 0.7, 0.3]), '#5a1e2c', 0.95),
           (ribbon([(74.6, 43.4), (75.2, 44.0), (75.6, 44.9)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.6),
           (ribbon([(76.8, 45.9), (78.6, 46.3), (80.4, 45.9)], [0.1, 0.8, 0.1]), SKIN.light, 0.75),
           (ribbon([(76.0, 47.2), (78.4, 47.4), (80.2, 46.9)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.45),
           (ellipse(78.4, 48.3, 1.5, 0.75, -10), SKIN.hi, 0.35)]
    # la mâchoire : son arête dans l'ombre douce, sous l'oreille
    hd += [(ribbon([(59.4, 44.6), (63.0, 46.4), (66.6, 47.8)], [0.1, 0.8, 0.1]), SKIN.deep, 0.22)]
    fig.part('head', head, SKIN, grad=(82, 30, 56, 48, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.65, cast=1.3, details=hd)
    # la grande oreille proche (bord net côté extérieur ; la racine se fond dans la peau)
    ear = sm([(57.4, 36.0), (55.6, 36.2), (54.2, 37.8), (54.0, 40.6), (54.8, 43.0), (56.4, 44.6), (58.0, 44.2),
              (58.6, 41.6), (58.8, 38.6)])
    fig.part('ear', ear, SKIN, cel=0.9, rim=0.55, cast=0.7, cast_on=['head'],
             details=[(sm([(57.2, 37.6), (56.0, 38.0), (55.6, 40.2), (56.2, 42.4), (57.4, 43.0), (57.6, 40.6)]), SKIN.shadow, 0.7),
                      (sm([(57.0, 39.6), (56.6, 40.6), (57.2, 41.8), (57.8, 41.0)]), SKIN.deep, 0.6),
                      (ribbon([(55.0, 38.0), (54.7, 40.4), (55.4, 42.8)], [0.1, 0.6, 0.1]), SKIN.light, 0.7)])
    # le bandeau rouge sur le front, peint DANS la tête (il en fait le tour), noué derrière
    band_zone = sm([(50.0, 29.6), (60.0, 29.8), (70.0, 30.4), (84.0, 31.6), (84.0, 35.4), (70.0, 34.4), (60.0, 33.8),
                    (50.0, 33.8)], sharp=(0, 3, 4, 7))
    band = clip(band_zone, head)
    fig.part('band', band, RED, cel=0.9, rim=0.7, cast=1.0, cast_on=['head', 'ear'],
             details=[(ribbon([(56.0, 30.8), (66.0, 31.2), (76.0, 31.9), (80.4, 32.4)], [0.1, 0.8, 0.7, 0.1]), RED.hi, 0.55),
                      (ribbon([(54.0, 33.0), (62.0, 33.2), (70.0, 33.6)], [0.1, 0.7, 0.1]), RED.shadow, 0.6)])
    bknot = sm([(53.4, 29.6), (51.4, 28.4), (49.2, 28.9), (48.4, 31.4), (49.0, 33.8), (51.0, 34.6), (53.2, 33.8)])
    fig.part('bknot', bknot, RED, cel=0.8, rim=0.55, cast=0.9,
             details=[(ribbon([(51.6, 29.0), (50.4, 31.4), (51.4, 34.2)], [0.1, 0.8, 0.1]), RED.shadow, 0.6),
                      (ellipse(50.4, 30.0, 0.8, 0.5, -30), RED.hi, 0.7)])
    # le chignon noir serré sur le haut du crâne, et son lien rouge
    bun = sm([(56.6, 22.0), (56.4, 18.8), (58.2, 16.4), (61.2, 15.6), (64.0, 16.8), (65.4, 19.4), (65.0, 22.2), (62.8, 23.8),
              (59.2, 23.8)])
    fig.part('bun', bun, HAIR, grad=(65, 16, 57, 23, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
             cel=0.9, rim=0.7, cast=1.0, cast_on=['head'],
             details=[(ribbon([(58.4, 17.6), (61.4, 16.6), (64.2, 18.2)], [0.1, 0.7, 0.1]), HAIR.hi, 0.6),
                      (ribbon([(58.0, 20.0), (60.6, 18.8), (63.8, 20.6), (64.4, 22.0)], [0.1, 0.6, 0.5, 0.1]), HAIR.light, 0.45),
                      (ribbon([(57.4, 21.6), (59.6, 22.6), (62.6, 22.8)], [0.1, 0.6, 0.1]), HAIR.deep, 0.5)])
    btie = rpoly([(58.4, 22.6), (63.6, 22.4), (63.8, 25.0), (58.6, 25.2)], 1.0)
    fig.part('btie', btie, RED, cel=0.5, rim=0.45, cast=0.7, cast_on=['head', 'bun'],
             details=[(ribbon([(59.0, 23.2), (61.2, 23.0), (63.2, 23.2)], [0.1, 0.5, 0.1]), RED.hi, 0.7)])

    # ---- chaque groupe de morceaux prend sa pose ----
    heads = ['head', 'ear', 'band', 'bknot', 'bun', 'btie'] + [n for n, _, _ in tails]
    fig.pose(heads, HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(['scarf', 'cord', 'tassel', 'rbead'] + ['bead%d' % i for i in range(len(beads))], UC)
    fig.pose(['farm', 'ffist', 'fthumb', 'ringF', 'fband'], UC)
    fig.pose(['belt', 'knot', 'sash1', 'sash2', 'narm', 'nfist', 'nthumb', 'ringN', 'nband'], U)
    fig.ctx = dict(U=U, UC=UC, P=P, HEAD=HEAD, ROOT=ROOTM, far_w=mapp(UC, FAR[2]), near_w=mapp(U, W),
                   chest=mapp(TOR, (66, 64)), head=mapp(HEAD, (72, 38)), far_s=mapp(UC, FS0),
                   ringF=_LAST.get('ringF'), ringN=_LAST.get('ringN'), fleg=fleg, nleg=nleg, bronze=bronze)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


_LAST = {}


# ---------- morceaux dessinés au repos (posés ensuite par un mouvement rigide) ----------

def fist_matrix(W0, a0, W, a, flip):
    """Le mouvement rigide d'un poing : dessiné au repos (poignet W0, avant-bras à l'angle a0), posé au poignet W
    à l'angle a ; flip : retourné (le pouce reste en haut quand l'avant-bras pointe vers la gauche)."""
    if flip:
        return mchain(mT(W[0], W[1]), mR(a - 180), mS(-1, 1), mR(-a0), mT(-W0[0], -W0[1]))
    return mchain(mT(W[0], W[1]), mR(a - a0), mT(-W0[0], -W0[1]))


def far_fist():
    """Le poing gauche tendu, serré sur le bord de l'anneau : le dos de la main vers nous, les quatre doigts empilés
    (un pli doux entre chacun), la rangée des jointures à droite, le pouce par-dessus."""
    fist = sm([(97.0, 53.2), (99.6, 50.6), (103.0, 50.0), (105.6, 51.0), (106.8, 53.4), (107.0, 57.0), (106.6, 60.0),
               (104.6, 61.8), (101.0, 62.0), (98.2, 60.6), (96.8, 57.4)])
    det = [(sm([(97.6, 53.4), (99.8, 51.2), (102.6, 50.8), (103.2, 54.0), (102.8, 58.4), (101.6, 61.4), (98.6, 60.4),
                (97.4, 57.2)]), SKIN.light, 0.35)]
    for y0, y1 in ((51.6, 54.4), (54.4, 57.0), (57.0, 59.4), (59.4, 61.6)):
        det += [(rpoly([(103.0, y0 + 0.15), (106.4, y0 + 0.3), (106.6, y1 - 0.2), (103.2, y1 - 0.1)], [0.5, 1.1, 1.1, 0.5]), SKIN.base, 0.55),
                (ellipse(105.2, (y0 + y1) / 2 - 0.3, 1.0, 0.55), SKIN.hi, 0.45),
                (ribbon([(103.4, y1), (105.0, y1 + 0.05), (106.6, y1 - 0.25)], [0.1, 0.5, 0.1]), SKIN.deep, 0.5)]
    det += [(ribbon([(102.8, 51.6), (103.4, 56.0), (102.8, 61.0)], [0.1, 0.8, 0.1]), SKIN.shadow, 0.5)]
    thumb = limb([(99.0, 52.6), (102.0, 51.4), (104.6, 52.4)], [3.0, 2.8, 2.4])
    return fist, det, thumb


def near_fist():
    """Le poing droit à la hanche, serré sur le haut de l'anneau qui pend : les quatre doigts côte à côte (des plis
    doux entre eux), la rangée des jointures en bas, le pouce devant."""
    fist = sm([(44.8, 80.4), (47.4, 78.6), (51.0, 78.8), (53.6, 80.6), (54.6, 83.4), (54.0, 86.4), (51.2, 87.6),
               (47.0, 87.6), (44.4, 86.0), (43.8, 83.0)])
    det = [(sm([(45.2, 80.6), (47.6, 79.2), (51.0, 79.4), (53.4, 81.0), (53.6, 83.0), (49.0, 83.2), (45.0, 82.8)]), SKIN.light, 0.35)]
    for x0, x1 in ((44.6, 47.0), (47.0, 49.4), (49.4, 51.8), (51.8, 54.0)):
        det += [(rpoly([(x0 + 0.2, 83.4), (x1 - 0.1, 83.4), (x1 - 0.2, 87.2), (x0 + 0.3, 87.0)], [0.5, 0.5, 1.1, 1.1]), SKIN.base, 0.5),
                (ellipse((x0 + x1) / 2 + 0.2, 84.6, 0.7, 0.5), SKIN.hi, 0.45),
                (ribbon([(x1, 83.6), (x1 - 0.05, 85.4), (x1 + 0.05, 87.0)], [0.1, 0.5, 0.1]), SKIN.deep, 0.5)]
    thumb = limb([(53.2, 81.2), (53.8, 83.6), (52.6, 85.4)], [2.9, 2.7, 2.3])
    return fist, det, thumb


def foot_near():
    """Le pied nu proche (talon à gauche, orteils vers l'ennemi) : sa forme, ses orteils, et la cheville."""
    A0 = NA0
    out = sm([(46.8, 107.0), (52.4, 107.0), (53.2, 109.6), (55.6, 111.2), (58.6, 112.2), (60.4, 113.4), (60.9, 115.0),
              (60.2, 116.4), (44.6, 116.4), (43.2, 115.4), (43.4, 113.0), (45.2, 110.4)], sharp=(7, 8))
    det = toes([(56.8, 111.6), (58.5, 112.3), (60.1, 113.4)], 116.2) + [
        (ribbon([(46.0, 110.6), (50.6, 111.2), (55.6, 112.2)], [0.1, 0.7, 0.1]), SKIN.hi, 0.4),
        (ellipse(46.6, 109.6, 1.0, 0.8), SKIN.light, 0.5),
        (ribbon([(44.0, 115.2), (52.0, 115.7), (60.0, 115.6)], [0.1, 0.9, 0.1]), SKIN.deep, 0.35)]
    return out, det, A0


def foot_far():
    """Le pied nu lointain, tourné vers l'ennemi (plus long : il pointe en avant)."""
    A0 = FA0
    out = sm([(79.6, 107.0), (85.4, 107.0), (86.4, 109.6), (89.4, 111.2), (92.8, 112.2), (94.8, 113.4), (95.6, 115.0),
              (94.8, 116.4), (77.6, 116.4), (76.6, 115.2), (77.0, 112.8), (78.4, 110.2)], sharp=(7, 8))
    det = toes([(90.8, 111.6), (92.8, 112.3), (94.7, 113.4)], 116.2) + [
        (ribbon([(79.2, 110.4), (84.6, 111.0), (90.0, 112.0)], [0.1, 0.8, 0.1]), SKIN.hi, 0.45),
        (ellipse(79.6, 109.4, 1.0, 0.8), SKIN.light, 0.5),
        (ribbon([(77.6, 115.2), (86.0, 115.7), (94.6, 115.6)], [0.1, 0.9, 0.1]), SKIN.deep, 0.35)]
    return out, det, A0


def toes(tips, sole):
    """Les orteils : des plis doux qui séparent trois orteils au bout du pied, leurs ongles clairs."""
    out = []
    for i, (x, y) in enumerate(tips):
        out += [(ribbon([(x - 0.9, y + 0.2), (x - 0.7, y + 1.6), (x - 0.9, sole - 1.6)], [0.1, 0.45, 0.1]), SKIN.deep, 0.5),
                (ellipse(x + 0.2, y + 0.9, 0.55, 0.38, 25), SKIN.hi, 0.75)]
    return out


def ribbon_flat(center, widths):
    """Un ruban à bouts carrés le long d'une ligne (l'écharpe, avant découpe)."""
    from atelier import sides
    left, right = sides(center, widths)
    pts = left + right[::-1]
    return sm(pts, sharp=(0, len(left) - 1, len(left), len(pts) - 1), t=0.8)


def cut_strip(pts, w0, w1, slant=1):
    """Un pan de tissu : il part du noeud (largeur w0), s'élargit un peu (w1) et finit en coupe biaise."""
    from atelier import resample, sides
    c = resample(pts, 10)
    ws = [w0 + (w1 - w0) * i / 10 for i in range(11)]
    left, right = sides(c, ws)
    if slant > 0:
        right[-1] = (right[-1][0], right[-1][1] - 1.4)
    else:
        left[-1] = (left[-1][0], left[-1][1] - 1.4)
    p = left + right[::-1]
    return sm(p, sharp=(len(left) - 1, len(left)), t=0.85)


def band_tails(ph, tl):
    """Les deux pans du bandeau qui volent derrière la tête : ils partent du noeud, ondulent (la vague court vers le
    bout) et se relèvent (tl > 0) ou retombent (tl < 0)."""
    out = []
    for i, (name, pts, w0, w1, sl) in enumerate((
            ('tailA', [(50.0, 30.2), (46.6, 29.0), (42.6, 28.4), (38.0, 27.8)], 2.8, 4.0, 1),
            ('tailB', [(49.6, 32.6), (46.4, 33.4), (42.8, 34.6), (39.2, 36.4)], 2.6, 3.4, -1))):
        q = []
        for k, (x, y) in enumerate(pts):
            t = k / (len(pts) - 1)
            wv = math.sin(ph * 1.3 - 1.6 * t - 0.9 * i)
            q.append((x + 0.3 * t * math.cos(ph - i), y + (0.9 * wv - 1.6 * tl * (1 if i == 0 else 0.8)) * t ** 1.2))
        sh = cut_strip(q, w0, w1, slant=sl)
        det = [(ribbon([q[0], lerp(q[1], q[2], 0.5), lerp(q[2], q[3], 0.8)], [0.1, 0.7, 0.1]), RED.shadow if i == 0 else RED.deep, 0.45),
               (ribbon([(q[0][0], q[0][1] - 0.8), (q[1][0], q[1][1] - 1.0), (q[2][0], q[2][1] - 1.2)], [0.1, 0.5, 0.1]), RED.hi, 0.5)]
        out.append((name, sh, det))
    return out


def bandage(fig, name, seg, arm, fist, a0, a1, half):
    """Les bandes de toile autour de l'avant-bras et de la base du poing (découpées dans le bras et le poing) : un pli
    en biais, la lumière en haut à droite. a0, a1 : où elles commencent et finissent, en pixels depuis le coude."""
    L = seg.L
    a0, a1 = a0 / L, a1 / L
    band = sm([seg(L * a0, -half - 2), seg(L * a1, -half - 2), seg(L * a1, half + 2), seg(L * a0, half + 2)],
              sharp=(0, 1, 2, 3), t=0.3)
    sh, _ = fuse([arm, fist], smooth=0.3)
    b = clip(band, sh)
    if b is None:
        return
    mid = seg(L * (a0 + a1) / 2, 0)
    det = [(ribbon([seg(L * (a0 + 0.12), -half), seg(L * (a0 + a1) / 2, 0), seg(L * (a1 - 0.25), half)], [0.1, 0.8, 0.1]), LINEN.shadow, 0.7),
           (ribbon([seg(L * (a0 + 0.22), -half), seg(L * ((a0 + a1) / 2 + 0.1), 0), seg(L * (a1 - 0.15), half)], [0.1, 0.5, 0.1]), LINEN.hi, 0.8),
           (ribbon([seg(L * (a0 + 0.02), -half), seg(L * (a0 + 0.04), 0), seg(L * (a0 + 0.02), half)], [0.1, 0.6, 0.1]), LINEN.deep, 0.35)]
    fig.part(name, b, LINEN, cel=0.9, rim=0.6, cast=0.8, details=det)


def chakram(fig, name, C, sx, sy, tilt_rot, spin, mat, glint=None, cast=0.9, cast_on=None, grip=None):
    """L'anneau de jet (chakram) : couronne de bronze au tranchant clair, bord intérieur sombre en haut et éclairé en
    bas (on voit son épaisseur), trois petites dents recourbées. C : le centre ; sx, sy : vu de biais ; glint : l'angle
    du reflet qui court sur le tranchant."""
    m = ring_map(C, sx, sy, tilt_rot, spin)
    g = chakram_geom(RR, Rr)
    import shapely
    gm = shapely.transform(g, lambda a: __import__('numpy').array([m(tuple(p)) for p in a]))
    sh = geom_shape(gm, sharp_deg=45, simplify=0.03)
    _LAST[name] = dict(C=C, sx=sx, sy=sy, rot=tilt_rot, spin=spin)
    ring_ = lambda R0, R1, a0=0, a1=360, n=48: _arc_ring(m, R0, R1, a0, a1, n)
    # le tranchant extérieur, clair (plus vif en haut à droite) ; le bord intérieur : sombre en haut, éclairé en bas
    x0, y0, x1, y1 = sh.bbox()
    det = [(ring_(RR - 1.5, RR + 0.2), ('lin', x1, y0, x0, y1, [(0, mat.hi), (0.5, mat.light), (1, mat.base)]), 1),
           (ring_(Rr, Rr + 1.5), ('lin', 0, y0, 0, y1, [(0, mat.deep), (0.45, mat.shadow), (0.7, mat.light), (1, mat.hi)]), 1),
           (ring_(Rr + 2.0, RR - 1.9, 200, 340, 24), mat.shadow, 0.35)]
    if glint is not None:
        det += [(ring_(RR - 1.4, RR + 0.2, glint - 16, glint + 16, 12), mat.glint, 0.9)]
    fig.part(name, sh, mat, cel=0.9, rim=0.6, cast=cast, cast_on=cast_on, details=det)


def _arc_ring(m, R0, R1, a0, a1, n):
    """Une couronne (ou un morceau de couronne) dans le plan de l'anneau, posée dans le dessin."""
    outer = [m((R1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), R1 * math.sin(math.radians(a0 + (a1 - a0) * i / n)))) for i in range(n + 1)]
    inner = [m((R0 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), R0 * math.sin(math.radians(a0 + (a1 - a0) * i / n)))) for i in range(n + 1)]
    if a1 - a0 >= 359:
        o = sm(outer[:-1], t=0.9)
        i_ = sm(inner[:-1], t=0.9)
        return Shape(o.subs + i_.rev().subs)
    return sm(outer + inner[::-1], sharp=(0, n, n + 1, 2 * n + 1), t=0.9)


def main():
    """aldric.svg (grand) et aldric-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/knights-3.webp (512 px de haut) et knights-3-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('aldric', 0.95, 512, ID_JEU), ('aldric-petit', 1.35, 160, ID_JEU + '-160')):
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
