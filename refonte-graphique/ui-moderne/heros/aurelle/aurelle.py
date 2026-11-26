# Aurelle (angels-10, terre, protecteur, commun) redessiné en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte de tous les héros, décision du propriétaire du 26/11/2026, sur le modèle validé de Kael : ../kael/kael.py ;
# même outil ../atelier.py, même trait, même échelle).
#
#   python3 refonte-graphique/ui-moderne/heros/aurelle/aurelle.py    # → aurelle.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/auriel.txt, ancien nom de fichier) : le cyclope, un
# géant brut qui lève sa massue pour écraser l'ennemi. Trois quarts vers la droite, grande fente, pieds nus à plat.
# Corps : trapèzes qui montent derrière la mâchoire, deltoïdes ronds, gros pectoraux lourds (pli d'ombre dessous,
# sillon du sternum décalé à droite), flanc proche dans l'ombre, gros ventre rond qui retombe sur la corde, hanches
# larges, cuisses lourdes, grands pieds nus à quatre orteils. Bras proche (droit) levé : le haut du bras à l'horizontale,
# l'avant-bras qui monte, le poing serré sur le manche de la massue tenue haut en arrière (rien devant le visage). Bras
# lointain (gauche) en garde : coude bas derrière le ventre, poing levé vers l'ennemi (phalanges, pouce en travers).
# Tête : crâne chauve et rond (reflet sur le dôme, cicatrice pâle), UN grand œil ambre au milieu du visage, un seul
# gros sourcil froncé en V, plis de colère, nez épaté qui dépasse à droite, grande bouche ouverte en grimace (dents de
# travers, gorge rouge sombre), défenses tordues qui montent de la mâchoire du bas, grande oreille décollée.
# Massue : un tronc noueux qui s'élargit en tête ronde, quatre pointes de fer, un nœud creux, mousse verte sur le dessus.
# Ceinture de corde tressée (nœud côté lointain, deux bouts, un petit crâne de bête), un os à la hanche proche, pagne de
# fourrure en grosses grappes (pan de devant plus long, pan de derrière dans l'ombre), brassards de cuir à plaques d'os.
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
from atelier import Figure, Mat, sm, lock, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import rot, add, lerp, body_limb, round_limb, ik, Seg, inv  # noqa: E402
from visage import placer, verifier, guide_svg  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'angels-10'

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#ffdc9c', '#eaa36a', '#c4784e', '#8a4446', '#55263a')
FUR = Mat('#e2b06c', '#a8723e', '#74462e', '#4a2a2c', '#2c1624')
ROPE = Mat('#fff0bc', '#e6cc8c', '#b49658', '#74583a', '#46322a')
LEATHER = Mat('#b07468', '#80504a', '#56323a', '#36202c', '#22121e')
BONE = Mat('#fffcee', '#f4e8cc', '#dccaa8', '#a8908a', '#64505e')
WOOD = Mat('#eec48a', '#bc8c56', '#875c38', '#55342e', '#33202a')
MOSS = Mat('#e4f49a', '#9cc450', '#5a8a3a', '#335434', '#1e3226')
IRON = Mat('#f6f8ff', '#c6cadc', '#8a8ea6', '#525672', '#2e2c42', glint='#ffffff')
SCAR = '#f4c4a4'
EYE_W = ('#fbf6ea', '#d8c8cc', '#a4909e')            # le blanc de l'œil : clair, ombre sous le sourcil, creux
IRIS = ('#fff2a8', '#ffc83e', '#e8861e', '#a8461a', '#5e1e12')
MOUTH = ('#3c0e1e', '#6e1a2c', '#b4404a', '#d8646a')  # gorge, bouche, langue, lumière de la langue
EARTH = ['#fff6ce', '#ffd45c', '#e09638', '#c8a070', '#8e664a', '#5e404a', '#3e2a36']   # la lueur et la roche de la terre

GRD = 116.0        # le sol (le point « sol » du pixel art)
FEET = (64.0, 116.0)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-2.5, -4.5, 130.0, 124.0)

# ---------- le squelette ----------
# Une pose = ces réglages ; REST est la pose du dessin (pixels du dessin, degrés, y vers le bas).
#   breath : souffle 0..1 ; crouch : il se tasse (les genoux plient, pieds au sol) ; lean : il se penche en avant (+) ;
#   head : décalage de la tête ; tilt : la tête tourne (+ = le menton descend) ; blink : l'œil se ferme (0..1) ;
#   eye : l'iris roule dans le blanc (dx, dy) ; glow : l'œil et la terre s'embrasent (0..2) ;
#   G : le milieu du poing proche sur le manche ; ang : la direction du manche vers la tête de la massue ;
#   bn : sens du coude proche ; nsh : l'épaule proche avance (dx, dy) ; rn / rf : épaules soulevées ;
#   FF : le poing lointain ; ffa : l'angle de l'avant-bras lointain (degrés) ; bf : sens du coude lointain ;
#   pg : le pagne se balance ; lift / shift : tout le corps en l'air / avancé ; front : le bras proche passe devant la
#   tête (bras levé) ; length : la massue s'allonge par la vitesse.
G0 = (23.4, 35.4)                    # le poing proche sur le manche
ANG0 = -110.0                        # le manche monte vers l'arrière (la tête de la massue en haut à gauche)
WRN = (-5.0, -4.6)                   # le poignet proche, dans le repère du manche (le long, en travers)
S_N = (43.6, 61.4)                   # l'épaule proche (articulation)
S_F = (96.6, 62.4)                   # l'épaule lointaine
LN1, LN2 = 28.4, 19.6                # bras proche : bras, avant-bras (jusqu'au poignet)
LF1, LF2 = 17.6, 17.0                # bras lointain
FF0 = (111.4, 60.6)                  # le poing lointain (son milieu)
FFA0 = -62.0                         # l'avant-bras lointain monte vers la droite
HIP = (68.0, 90.0)                   # le pivot du buste
NECK = (66.0, 54.0)                  # le pivot (et le centre d'agrandissement) de la tête
# Le visage est placé par l'outil commun ../visage.py (une sphère qui tourne de 18° : tout le visage tourne ensemble).
# Un cyclope : son œil unique est SUR la ligne médiane, à la hauteur des yeux ; le nez sous l'œil sur la médiane, la
# bouche centrée sous le nez (fermée au repos). Repère de la tête AVANT son agrandissement (×1,1 autour de NECK).
FACE_BOX = (47.0, 21.0, 86.0, 56.0)  # l'ovale de la face (crâne chauve compris, sans l'oreille)
FACE = placer(FACE_BOX)
EYE_C = (round(FACE['mediane'](37.0), 2), 37.0)     # le milieu de l'œil unique, sur la médiane
NOSE = FACE['nez']                                   # la base du nez, sur la médiane
MOUTH_C = (FACE['bouche'][0], FACE['bouche'][1] + 0.6)   # le milieu de la bouche, sur la médiane

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, blink=0.0, eye=(0.0, 0.0), glow=0.0,
            G=G0, ang=ANG0, bn=-1.0, nsh=(0.0, 0.0), rn=0.0, rf=0.0, FF=FF0, ffa=FFA0, bf=1.0, pg=0.0, lift=0.0,
            shift=0.0, front=0.0, length=1.0, mouth=0.0)


def sm_under(sh, dx=0.8, dy=-2.4):
    """La face du dessous d'une grappe : la forme moins elle-même décalée vers le haut (le haut reste éclairé)."""
    return Shape(sh.subs + sh.move(dx, dy).subs, evenodd=True)


def tuft(p0, p1, p2, p3, w0, n=14, k=2.2):
    """Une grappe de poils : large et ronde presque jusqu'au bout, puis vite pointue (pas un triangle), le long d'une
    courbe de Bézier ; la racine (p0) est un bord droit, caché sous la corde."""
    from atelier import bez, resample, sides
    c = resample(bez(p0, p1, p2, p3, 40), n)
    ws = [max(0.0, w0 * (1 - (i / n) ** k) ** 0.75 * (1 + 0.12 * math.sin(math.pi * i / n))) for i in range(n + 1)]
    left, right = sides(c, ws)
    pts = left[:-1] + [c[-1]] + right[:-1][::-1]
    return sm(pts, sharp=(len(left) - 1,), t=0.9)


def diag(mat, x0, y0, x1, y1):
    """Le dégradé « diagonal » d'une matière dans une boîte donnée (comme atelier, mais une boîte choisie : deux morceaux
    d'un même membre gardent ainsi exactement la même couleur à leur raccord)."""
    return (x1, y0, x0 + (x1 - x0) * 0.2, y1, [(0, mat.light), (0.55, mat.base), (1, mat.shadow)])


def bracer(c, a, L, W):
    """Un brassard de cuir autour d'un avant-bras : c = son milieu, a = la direction de l'avant-bras, L = sa longueur le
    long du bras, W = sa largeur en travers. Les bords sont un peu bombés (il entoure le bras)."""
    h, w = L / 2, W / 2
    pts = [(-h, -w), (-h * 0.2, -w - 0.45), (h * 0.6, -w - 0.3), (h, -w + 0.3), (h + 0.5, 0), (h, w - 0.3), (h * 0.6, w + 0.3),
           (-h * 0.2, w + 0.45), (-h, w), (-h - 0.5, 0)]
    return xf(sm(pts, sharp=(0, 3, 5, 8), t=0.7), c[0], c[1], a)


def bracer_det(c, a, L, W, up):
    """Le brassard : deux coutures douces aux bords, une plaque d'os bombée (ivoire, ombrée en bas), un lacet.
    up = le côté (±1, en travers) tourné vers la lumière."""
    h, w = L / 2, W / 2
    X = lambda sh: xf(sh, c[0], c[1], a)
    out = [(X(ribbon([(-h + 1.0, -w * 0.9), (-h + 1.2, 0), (-h + 1.0, w * 0.9)], [0.1, 0.7, 0.1])), LEATHER.deep, 0.55),
           (X(ribbon([(h - 1.0, -w * 0.9), (h - 1.2, 0), (h - 1.0, w * 0.9)], [0.1, 0.7, 0.1])), LEATHER.deep, 0.5),
           (X(ribbon([(-h + 1.6, up * w * 0.78), (0, up * w * 0.86), (h - 1.6, up * w * 0.78)], [0.1, 0.8, 0.1])), LEATHER.hi, 0.55)]
    # la plaque d'os : une écaille arrondie, un peu de travers, au milieu du brassard
    pl = X(sm([(-h * 0.55, -w * 0.42), (h * 0.1, -w * 0.62), (h * 0.62, -w * 0.3), (h * 0.58, w * 0.34), (-h * 0.05, w * 0.6),
               (-h * 0.6, w * 0.36)]))
    out += [(X(sm([(-h * 0.62, -w * 0.48), (h * 0.12, -w * 0.7), (h * 0.7, -w * 0.34), (h * 0.66, w * 0.42), (-h * 0.05, w * 0.7),
                   (-h * 0.68, w * 0.42)])), LEATHER.deep, 0.75),
            (pl, BONE.base, 1),
            (X(sm([(-h * 0.5, up * -w * 0.1), (h * 0.5, up * -w * 0.0), (h * 0.55, up * w * 0.32), (-h * 0.05, up * w * 0.58),
                   (-h * 0.58, up * w * 0.34)])), BONE.shadow, 0.55),
            (X(ellipse(h * 0.12, up * -w * 0.3, h * 0.32, w * 0.13)), BONE.hi, 0.95),
            (X(ribbon([(-h * 0.2, w * 0.02), (h * 0.05, -w * 0.04), (h * 0.3, w * 0.06)], [0.1, 0.4, 0.1])), BONE.deep, 0.45)]
    return out


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
    TOR = mchain(U, mS(1 + 0.008 * br, 1 + 0.014 * br, 70, 86))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(1.1, 1.1, *NECK))
    CLO = mchain(PEL, mskx(-0.05 * P['pg'], 88))
    SK = mchain(U)                                                             # la peau du buste (même dégradé partout)

    # ======================================================================== la massue (repère : G, u vers la tête)
    G, ang = P['G'], P['ang']
    lk = P['length']

    def C_(sh):
        return xf(sh, G[0], G[1], ang, lk, 1)

    def Cp(u, v=0.0):
        a = math.radians(ang)
        return (G[0] + u * lk * math.cos(a) - v * math.sin(a), G[1] + u * lk * math.sin(a) + v * math.cos(a))
    a_ = math.radians(ang)
    nv = (-math.sin(a_), math.cos(a_))                  # le côté « +v » du manche, dans le dessin
    up = 1 if (nv[0] * 0.6 - nv[1] * 0.8) > 0 else -1  # le côté tourné vers la lumière (haut-droit)

    def draw_club():
        # les quatre pointes de fer (leur base passe sous le bois) : des cônes, le dessus éclairé, la pointe claire
        for i, (u0, side, ln) in enumerate(((22.6, 1, 5.6), (22.8, -1, 5.4), (29.6, 1, 5.2), (29.8, -1, 5.0))):
            r0 = 7.2 if u0 < 25 else 7.9
            base = [(u0 - 1.9, side * (r0 - 1.2)), (u0 + 1.9, side * (r0 - 1.0))]
            tip = (u0 + 0.9, side * (r0 + ln))
            sp = C_(sm([base[0], (u0 - 1.6, side * (r0 + 0.6)), (tip[0] - 0.4, tip[1] - side * 0.6), tip,
                        (tip[0] + 0.5, tip[1] - side * 0.7), (u0 + 1.9, side * (r0 + 0.5)), base[1]], sharp=(3,), t=0.7))
            lit = side == up
            fig.part('spk%d' % i, sp, IRON, cel=0.6, rim=0.5, cast=0.4,
                     grad=(*Cp(u0 + 2, side * r0), *Cp(u0 - 2, side * (r0 + ln)),
                           [(0, IRON.light if lit else IRON.base), (0.6, IRON.base), (1, IRON.shadow)]),
                     details=[(C_(ribbon([(u0 + 0.6, side * (r0 + 0.2)), (u0 + 0.8, side * (r0 + ln * 0.55)), (tip[0], tip[1] - side * 0.4)],
                                         [0.2, 0.7, 0.1])), IRON.hi, 0.85 if lit else 0.5)])
        # le tronc noueux : le manche, un nœud, puis il s'élargit en tête ronde
        R = [(-11.6, 2.5), (-6.0, 2.3), (1.0, 2.35), (6.4, 2.7), (10.4, 3.3), (12.4, 4.3), (14.2, 3.8), (17.4, 4.6),
             (21.0, 5.9), (25.0, 6.7), (29.4, 7.0), (33.0, 6.5), (36.0, 4.8), (37.8, 2.2)]
        L = [(37.6, -2.6), (35.6, -5.4), (32.6, -6.9), (28.4, -7.1), (24.0, -6.6), (20.2, -5.5), (17.2, -4.2), (14.2, -3.5),
             (10.6, -3.1), (8.6, -3.7), (7.0, -3.0), (2.0, -2.35), (-6.0, -2.3), (-11.6, -2.5)]
        fat = lambda pts: [(u, v * (1 + 0.22 * min(1.0, max(0.0, (u - 10) / 12)))) for u, v in pts]
        R, L = fat(R), fat(L)
        body = C_(sm(R + [(38.8, -0.2)] + L + [(-12.8, 0.0)], t=0.85))
        cd = [
            # l'arête éclairée du côté de la lumière, l'ombre de l'autre côté (dans la forme)
            (C_(ribbon([(-10, 1.6 * up), (4, 1.7 * up), (12, 2.7 * up), (20, 4.4 * up), (28, 5.6 * up), (34, 4.6 * up)],
                       [0.1, 0.8, 0.9, 1.3, 1.5, 0.1])), WOOD.hi, 0.75),
            (C_(ribbon([(-9, -1.4 * up), (6, -1.6 * up), (16, -2.6 * up), (24, -4.4 * up), (31, -5.0 * up)],
                       [0.1, 0.9, 1.1, 1.4, 0.1])), WOOD.shadow, 0.7),
            # des veines courtes (le fil du bois), inégales
            (C_(ribbon([(15.6, 0.6), (19.6, 1.4), (23.0, 0.8)], [0.1, 0.55, 0.1])), WOOD.deep, 0.5),
            (C_(ribbon([(26.4, 2.6), (30.4, 3.4), (33.4, 2.4)], [0.1, 0.5, 0.1])), WOOD.deep, 0.45),
            (C_(ribbon([(8.0, -0.4), (11.6, 0.2)], [0.1, 0.4])), WOOD.deep, 0.4),
            # le bourrelet du nœud du manche
            (C_(ellipse(12.4, 2.6 * up, 1.4, 0.9)), WOOD.light, 0.8),
            # le nœud creux : un trou sombre, son bord éclairé du côté de la lumière
            (C_(ellipse(26.2, -2.2 * up, 2.2, 1.6)), WOOD.base, 1),
            (C_(ellipse(26.0, -2.0 * up, 1.6, 1.1)), WOOD.deep, 0.95),
            (C_(ribbon([(24.4, -0.9 * up), (26.2, -0.5 * up), (27.8, -1.0 * up)], [0.1, 0.5, 0.1])), WOOD.hi, 0.7),
        ]
        fig.part('club', body, WOOD, cel=1.1, rim=0.7, cast=0.9,
                 grad=(*Cp(36, 8 * up), *Cp(-10, -3 * up), [(0, WOOD.light), (0.5, WOOD.base), (1, WOOD.shadow)]),
                 details=cd)
        # la mousse sur le dessus : une calotte verte qui coule un peu sur les côtés (bord en lobes inégaux)
        moss = C_(sm([(32.4, -7.8), (35.4, -6.4), (37.8, -3.4), (39.2, 0.0), (38.0, 3.6), (35.4, 6.6), (32.2, 7.9),
                      (31.4, 5.6), (33.0, 3.6), (31.8, 1.4), (33.4, -0.8), (32.0, -3.2), (33.2, -5.2)], t=0.8))
        fig.part('moss', moss, MOSS, cel=0.6, rim=0.6, cast=0.7, cast_on=['club'],
                 grad=(*Cp(39, 3 * up), *Cp(32, -4 * up), [(0, MOSS.light), (0.55, MOSS.base), (1, MOSS.shadow)]),
                 details=[(C_(ellipse(37.0, 1.6 * up, 1.2, 0.8)), MOSS.hi, 0.8),
                          (C_(ellipse(35.2, -2.6 * up, 0.9, 0.6)), MOSS.hi, 0.5)])

    # ======================================================================== le bras lointain (gauche), en garde :
    # coude bas derrière le ventre, l'avant-bras revient devant le ventre, le poing levé vers l'ennemi
    FFp = P['FF']
    ffa = P['ffa']
    fa_ = math.radians(ffa)
    Wf_target = (FFp[0] - 5.4 * math.cos(fa_), FFp[1] - 5.4 * math.sin(fa_))   # le poignet, sous le poing
    Sf = mapp(UC, (S_F[0], S_F[1] - 0.8 * P['rf']))
    Sfu = mapp(inv(U), Sf)
    Wfu = mapp(inv(U), Wf_target)
    Ef, Wf = ik(Sfu, Wfu, LF1, LF2, P['bf'])
    FAR_GRAD = diag(SKIN, 92, 54, 114, 88)
    fkeys = [(0, 8.0, 8.0), (0.22, 7.4, 7.6), (0.48, 6.0, 6.2), (0.58, 6.0, 6.0), (0.74, 6.0, 6.2), (1, 5.0, 5.0)]
    far_arm = round_limb([Sfu, Ef, Wf], fkeys, n=26)
    f1, f2 = Seg(Sfu, Ef), Seg(Ef, Wf)
    fig.part('farm', far_arm, SKIN, grad=FAR_GRAD, cel=1.5, rim=0.6, cast=0.8,
             details=[(ellipse(*f1.at(0.2, -2.0), 4.6, 3.4, 0), SKIN.light, 0.35)])

    def draw_far_front():
        """L'avant-bras lointain repassé DEVANT le ventre (le même membre, même couleur : le coude est derrière le
        ventre), son brassard, puis le poing."""
        fa2 = math.degrees(math.atan2(f2.u[1], f2.u[0]))
        fore = body_limb([f2.at(-0.02), f2.at(0.5), Wf], [(0, 6.0, 6.2), (0.3, 6.0, 6.2), (1, 5.0, 5.0)], n=14)
        fig.part('ffore', fore, SKIN, grad=FAR_GRAD, cel=1.3, rim=0.6, cast=1.0, cast_on=['torso', 'farm'],
                 details=[(ellipse(*f2.at(0.25, 2.0), 3.0, 4.0, fa2 - 90), SKIN.light, 0.3)])
        bc = f2.at(0.6)
        upf = 1 if (-f2.v[0] * 0.6 + f2.v[1] * 0.8) < 0 else -1
        fig.part('fbrac', bracer(bc, fa2, 9.4, 11.4), LEATHER, cel=0.8, rim=0.5, cast=0.9,
                 details=bracer_det(bc, fa2, 9.4, 11.4, -upf))
        far_fist(Wf, fa2)

    def far_fist(W, a_deg):
        """Le poing lointain fermé, tourné vers l'ennemi (le poignet cassé) : quatre doigts repliés vus de côté, l'un
        au-dessus de l'autre (phalanges vers l'ennemi), le pouce en travers devant les doigts du bas, avec son ongle."""
        fa = a_deg + 44                  # le poing se tourne vers l'ennemi (le poignet plie)

        def F(sh):
            return xf(sh, W[0], W[1], fa)
        # repère : x vers les phalanges (vers l'ennemi), y en travers (+ = vers le bas)
        out = F(sm([(-1.6, -4.6), (1.4, -6.8), (6.4, -7.4), (10.8, -6.4), (12.8, -3.6), (13.2, 0.4), (12.6, 4.4),
                    (10.4, 6.8), (5.4, 7.4), (1.0, 6.4), (-1.4, 3.0)]))
        fd = [(F(sm([(-0.6, -4.4), (1.8, -6.2), (6.4, -6.8), (10.4, -5.8), (9.0, -4.4), (3.0, -3.6)])), SKIN.light, 0.5)]
        # quatre doigts repliés, de tailles inégales, séparés par des plis doux ; le bout de chacun éclairé
        for i, (y0_, y1_, x0_) in enumerate(((-6.4, -3.0, 4.6), (-3.0, 0.4, 4.0), (0.4, 3.6, 4.4), (3.6, 6.4, 5.4))):
            x1_ = 12.8 - 0.25 * abs(i - 1.2)
            seg = F(rpoly([(x0_, y0_ + 0.2), (x1_, y0_ + 0.3), (x1_, y1_ - 0.3), (x0_, y1_ - 0.2)], [1.2, 1.6, 1.6, 1.2]))
            fd += [(seg, SKIN.base, 0.4),
                   (F(ellipse(x1_ - 1.6, (y0_ + y1_) / 2 - 0.5, 1.4, (y1_ - y0_) * 0.26)), SKIN.hi, 0.55)]
            if i < 3:
                fd.append((F(ribbon([(x0_ + 0.6, y1_ + 0.05), ((x0_ + x1_) / 2, y1_ + 0.15), (x1_ - 0.3, y1_)], [0.1, 0.6, 0.3])), SKIN.deep, 0.5))
        fig.part('ffist', out, SKIN, cel=1.2, rim=0.6, cast=1.0, details=fd)
        # le pouce en travers, devant les doigts du bas, son ongle
        th = F(limb([(1.8, 5.8), (5.6, 4.6), (9.4, 2.6)], [3.6, 3.4, 3.0]))
        fig.part('fthumb', th, SKIN, cel=0.8, rim=0.5, cast=0.8, cast_on=['ffist'],
                 details=[(F(ellipse(9.2, 2.6, 1.05, 0.8, -25)), '#f4c8b0', 0.9),
                          (F(ellipse(9.4, 2.3, 0.45, 0.3, -25)), '#ffffff', 0.6)])

    # ======================================================================== le pan de derrière du pagne (dans
    # l'ombre, entre les jambes)
    back = sm([(58.0, 94.0), (80.0, 94.0), (82.4, 100.0), (80.6, 105.4), (79.0, 103.0), (77.4, 108.6), (75.6, 105.2),
               (73.2, 110.6), (71.0, 105.8), (68.4, 109.2), (66.6, 104.6), (64.2, 107.4), (62.6, 102.4), (60.2, 104.6),
               (58.6, 99.8)], sharp=tuple(range(3, 15)), t=0.85)
    fig.part('backfur', back, FUR, grad=(80, 94, 62, 110, [(0, FUR.base), (0.5, FUR.shadow), (1, FUR.deep)]),
             cel=0.8, rim=0.3, cast=0)

    # ======================================================================== les jambes : hanche → genou → cheville,
    # d'un seul tenant (aucune couture au genou) ; les grands pieds nus à quatre orteils
    def leg(name, Hr, B, L1_, L2_, bend, keys, toes_dir, cast_on):
        H = mapp(PEL, Hr)
        B = mapp(ROOTM, B)
        A = (B[0] - 1.6 * toes_dir, B[1] - 8.4)            # la cheville (le bout de la jambe se pose dans le pied)
        sc = min(1.0, math.dist(H, A) * 1.04 / (L1_ + L2_))
        K, A2 = ik(H, A, L1_ * sc, L2_ * sc, bend)
        th, sn = Seg(H, K), Seg(K, A2)
        sh = body_limb([H, K, A2], keys, n=22)
        ga = math.degrees(math.atan2(sn.u[1], sn.u[0]))
        det = [(ellipse(*th.at(0.45, 2.6 * toes_dir), 4.0, 5.6, math.degrees(math.atan2(th.u[1], th.u[0])) - 90), SKIN.light, 0.28),
               (ellipse(*sn.at(0.0, 0.8 * toes_dir), 3.0, 2.4, ga), SKIN.light, 0.35),             # la rotule
               (ribbon([sn.at(0.18, -1.4 * toes_dir), sn.at(0.28, 0.4 * toes_dir), sn.at(0.22, 2.4 * toes_dir)], [0.1, 0.6, 0.1]), SKIN.shadow, 0.45),
               (ellipse(*sn.at(0.55, -3.0 * toes_dir), 2.6, 3.4, ga - 90), SKIN.light, 0.22)]       # le mollet
        def Fp(pts):
            return [(B[0] + x * toes_dir, B[1] + y) for x, y in pts]
        # le pied : talon rond derrière, le cou-de-pied qui descend vers quatre gros orteils devant ; la plante au sol
        foot = sm(Fp([(-14.6, 0.0), (-15.4, -2.8), (-14.2, -5.6), (-9.8, -8.0), (-4.0, -8.6), (1.6, -7.6), (6.4, -6.0),
                      (10.6, -5.4), (13.6, -4.4), (15.6, -2.4), (15.8, 0.0)]), sharp=(0, 10), t=0.85)
        fd = [(sm(Fp([(-15.4, -1.2), (15.8, -1.2), (15.8, 0.4), (-15.4, 0.4)])), SKIN.deep, 0.55),
              (ellipse(*Fp([(-2.6, -6.6)])[0], 4.6, 1.3, -6 * toes_dir), SKIN.light, 0.55),
              (ellipse(*Fp([(-11.4, -4.6)])[0], 2.2, 1.4, 0), SKIN.light, 0.35)]
        # les orteils : quatre bosses inégales séparées par des plis doux, un ongle sur chacun
        for i, (x, w_, h_) in enumerate(((5.2, 2.7, 3.5), (8.6, 2.5, 3.2), (11.6, 2.3, 2.9), (14.2, 2.0, 2.5))):
            if i:
                fd.append((ribbon(Fp([(x - w_ * 0.62, -h_ - 0.6), (x - w_ * 0.68, -h_ * 0.5), (x - w_ * 0.6, -0.6)]), [0.1, 0.5, 0.2]), SKIN.deep, 0.42))
            fd += [(ellipse(*Fp([(x - 0.1, -h_ * 0.66)])[0], w_ * 0.36, h_ * 0.3), SKIN.light, 0.35),
                   (ellipse(*Fp([(x + w_ * 0.36, -h_ * 0.5)])[0], w_ * 0.2, h_ * 0.17, -20 * toes_dir), '#efc0a4', 0.55)]
        fig.part(name + 'p', foot, SKIN, grad=diag(SKIN, B[0] - 15, B[1] - 9, B[0] + 16, B[1]), cel=1.2, rim=0.7, cast=0.9,
                 cast_on=cast_on, details=fd)
        fig.part(name, sh, SKIN, grad=diag(SKIN, H[0] - 12, H[1] - 2, H[0] + 12, B[1]), cel=1.7, rim=0.6, cast=1.0,
                 cast_on=(cast_on + [name + 'p']) if cast_on else None, details=det)

        return K, B

    KF, BF = leg('fleg', (88.4, 89.0), (99.6, 116.0), 12.6, 9.4, -1,
                 [(0, 9.4, 9.6), (0.45, 8.2, 8.2), (0.58, 7.2, 7.0), (0.82, 6.4, 6.4), (1, 5.8, 5.8)], 1, None)
    KN, BN = leg('nleg', (49.6, 89.0), (35.6, 116.0), 12.6, 9.4, -1,
                 [(0, 9.8, 10.0), (0.45, 8.6, 8.6), (0.58, 7.6, 7.4), (0.82, 6.6, 6.6), (1, 6.0, 6.0)], 1, None)

    # ======================================================================== le pagne de fourrure : de grosses grappes
    # de poils aux pointes fendues ; le pan de devant plus long ; inégales (jamais une rangée régulière)
    # chaque grappe : une touffe large sous la corde, qui tombe en s'effilant (la pointe un peu tournée vers l'extérieur),
    # avec une petite pointe fendue à côté ; du fond vers le devant (hanche lointaine, hanche proche, puis le devant)
    TUFTS = [  # (racine x, racine y, pointe x, pointe y, largeur, sens de la fente)
        (99.4, 89.6, 101.2, 96.8, 7.6, 1), (93.0, 90.6, 94.6, 99.4, 8.6, 1),
        (40.4, 89.4, 38.8, 97.8, 8.6, -1), (48.0, 90.2, 47.4, 100.0, 8.8, 1),
        (86.2, 91.6, 87.6, 102.6, 8.8, 1), (56.4, 91.6, 55.8, 103.6, 8.8, -1), (79.0, 92.2, 80.4, 105.8, 9.0, 1),
        (64.0, 92.4, 64.0, 108.0, 9.4, -1), (71.8, 92.4, 72.8, 109.2, 9.4, 1)]
    tnames = []
    ph = P['pg']
    for i, (x0_, y0_, x3, y3, w0, sd_) in enumerate(TUFTS):
        sw = 0.5 * ph * (1 + 0.15 * (i % 3))                       # le balancement (les pointes traînent)
        p0 = (x0_, y0_ - 3.0)
        p3 = (x3 - sw, y3)
        p1 = (x0_ + 0.2 * (x3 - x0_), y0_ + (y3 - y0_) * 0.3)
        p2 = (x3 - 0.3 * (x3 - x0_) - 0.6 * sw, y3 - (y3 - y0_) * 0.32)
        sh = tuft(p0, p1, p2, p3, w0)
        # la petite pointe fendue, à côté de la grande (derrière elle)
        q0 = (x0_ + sd_ * w0 * 0.12, y0_ + (y3 - y0_) * 0.35)
        q3 = (x3 + sd_ * w0 * 0.3 - sw, y3 - 1.6 - 0.3 * (i % 2))
        sp = tuft(q0, (q0[0] + sd_ * 0.6, (q0[1] + q3[1]) / 2), (q3[0] - sd_ * 0.4, q3[1] - 2.0), q3, w0 * 0.46, n=10)
        x0b, y0b, x1b, y1b = sh.bbox()
        grd = (x1b + 2, y0b, x0b + (x1b - x0b) * 0.3, y1b, [(0, FUR.light), (0.5, FUR.base), (1, FUR.shadow)])
        below = ['nleg', 'fleg', 'backfur'] + tnames
        fig.part('tus%d' % i, sp, FUR, grad=grd, cel=0.5, rim=0.4, cast=0.6, cast_on=below)
        fig.part('tuf%d' % i, sh, FUR, grad=grd, cel=0, rim=0.45, cast=1.1, cast_on=below + ['tus%d' % i],
                 details=[(sm_under(sh, 0.9, -2.2), ('lin', 0, y0b, 0, y1b, [(0, FUR.base), (1, FUR.shadow)]), 0.75),
                          (tuft(lerp(p0, p1, 0.5), lerp(p1, p2, 0.3), lerp(p2, p3, 0.2), lerp(p2, p3, 0.7), w0 * 0.3, n=10)
                           .move(0.4 + 0.12 * w0, -0.05 * w0), FUR.hi, 0.4),
                          (ribbon([lerp(p0, p1, 0.9), lerp(p1, p2, 0.6), lerp(p2, p3, 0.6)], [0.1, 0.7, 0.1]), FUR.deep, 0.45)])
        tnames += ['tus%d' % i, 'tuf%d' % i]
    SKIRT = tnames

    # ======================================================================== la ceinture de corde tressée (elle suit
    # la taille en trois quarts : plus basse devant, elle remonte sur les hanches et passe derrière)
    RC = [(38.6, 88.4), (44.0, 89.2), (52.0, 90.4), (60.0, 91.4), (68.0, 92.0), (76.0, 91.8), (84.0, 91.0), (92.0, 89.8),
          (98.0, 88.8), (102.2, 88.0)]
    rope = limb(RC, [5.0] * len(RC))
    rd = [(rope, ROPE.shadow, 0.6)]
    # la torsade : des brins dodus en fuseau, penchés, qui se recouvrent ; chacun éclairé en haut à droite et ombré en
    # bas à gauche (des volumes, pas des rayures)
    from atelier import resample
    cpts = resample(RC, 21)
    for i in range(len(cpts) - 1):
        p, q = cpts[i], cpts[i + 1]
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        a = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
        L = math.dist(p, q)
        bead = xf(sm([(-L * 0.95, 0.0), (-L * 0.3, -1.55), (L * 0.5, -1.35), (L * 0.95, 0.0), (L * 0.3, 1.55), (-L * 0.5, 1.35)], t=0.9),
                  mx, my, a + 38)
        rd += [(bead, ('lin', mx + 1.2, my - 2.0, mx - 1.2, my + 2.0, [(0, ROPE.light), (0.55, ROPE.base), (1, ROPE.shadow)]), 1),
               (xf(ellipse(L * 0.1, -0.6, L * 0.42, 0.45), mx, my, a + 38), ROPE.hi, 0.7)]
    fig.part('rope', rope, ROPE, cel=0.9, rim=0.5, cast=1.0, cast_on=SKIRT + ['nleg', 'fleg'], details=rd)
    # l'os qui pend à la hanche proche, attaché à la corde
    fig.part('bonecord', limb([(45.2, 90.0), (45.0, 92.4)], [1.2, 1.0]), ROPE, cel=0.3, rim=0.2, cast=0.5)
    bone = sm([(43.2, 92.0), (44.6, 91.6), (45.8, 92.2), (46.0, 93.4), (45.4, 94.4), (45.6, 97.6), (46.6, 98.6), (46.2, 100.0),
               (44.8, 100.2), (44.0, 99.4), (42.8, 99.8), (42.0, 98.6), (43.0, 97.4), (43.6, 94.4), (42.6, 93.2)])
    fig.part('bone', bone, BONE, cel=0.6, rim=0.5, cast=0.8, cast_on=SKIRT + ['nleg'],
             details=[(ribbon([(45.0, 93.0), (44.8, 96.0), (45.2, 99.2)], [0.1, 0.6, 0.1]), BONE.hi, 0.8)])

    # ======================================================================== le buste (avec les trapèzes et le ventre)
    torso = sm([(54.0, 49.0), (47.4, 51.6), (41.6, 54.2), (38.0, 57.8), (36.6, 63.4), (37.2, 70.4), (37.0, 78.0),
                (36.6, 84.0), (37.8, 88.0), (44.0, 88.6), (52.0, 89.6), (60.0, 90.8), (68.0, 91.6), (76.0, 91.4),
                (84.0, 90.2), (92.0, 88.8), (97.6, 87.4), (100.8, 84.6), (102.8, 79.4), (103.4, 73.2), (102.8, 67.6),
                (101.4, 62.8), (99.4, 58.8), (95.2, 56.0), (89.8, 54.6), (84.8, 52.0), (80.0, 49.4)])
    det = [(torso, ('lin', 37, 70, 58, 66, [(0, SKIN.deep, 0.55), (1, SKIN.deep, 0)]), 1)]   # le flanc proche dans l'ombre
    # les trapèzes qui montent vers la mâchoire : la masse éclairée en haut
    det += [(sm([(44.0, 53.6), (50.0, 51.0), (55.6, 51.6), (54.0, 54.4), (48.0, 55.6), (42.6, 56.6)]), SKIN.light, 0.35),
            (sm([(80.6, 51.6), (86.0, 53.4), (92.0, 55.2), (97.0, 57.6), (92.0, 58.0), (85.6, 56.2), (80.6, 54.4)]), SKIN.hi, 0.35)]
    # les pectoraux lourds : la plaque éclairée, le pli d'ombre dessous (le proche plus large, trois quarts)
    det += [(sm([(46.0, 58.6), (55.0, 56.4), (65.0, 56.8), (73.0, 59.4), (74.6, 64.6), (71.6, 69.4), (62.0, 71.0),
                 (52.0, 70.0), (45.6, 66.0)]), SKIN.light, 0.42),
            (sm([(44.6, 67.0), (52.0, 71.2), (62.0, 72.6), (71.4, 70.8), (75.0, 66.6), (75.6, 70.8), (71.8, 74.0),
                 (62.0, 75.6), (51.2, 74.0), (44.0, 70.4)]), SKIN.shadow, 0.78),
            (sm([(77.4, 58.4), (85.0, 56.8), (93.2, 58.0), (99.4, 61.6), (99.0, 66.4), (94.4, 69.0), (85.6, 69.2),
                 (78.6, 66.4)]), SKIN.hi, 0.42),
            (sm([(77.6, 67.0), (85.6, 70.4), (94.6, 70.2), (99.6, 67.2), (99.0, 70.8), (94.6, 73.2), (85.4, 73.2),
                 (77.2, 70.4)]), SKIN.shadow, 0.7),
            # le sillon du sternum, décalé à droite (trois quarts)
            (ribbon([(75.6, 56.8), (76.2, 62.0), (76.0, 67.6), (75.4, 71.2)], [0.1, 1.2, 1.0, 0.1]), SKIN.shadow, 0.6),
            (ribbon([(76.8, 58.4), (77.4, 63.0), (77.2, 67.0)], [0.1, 0.6, 0.1]), SKIN.hi, 0.35)]
    # le gros ventre rond : sa lumière en haut à droite, son ombre en bas à gauche, le nombril
    det += [(ellipse(86.6, 79.4, 11.6, 7.6, -12), SKIN.light, 0.4),
            (ellipse(89.4, 77.2, 6.4, 3.6, -14), SKIN.hi, 0.35),
            (sm([(42.0, 80.6), (52.0, 84.6), (64.0, 87.4), (76.0, 88.6), (88.0, 87.6), (96.4, 85.2), (92.0, 89.0),
                 (84.0, 90.4), (68.0, 91.6), (52.0, 89.8), (40.0, 88.2)]), SKIN.shadow, 0.55),
            (ellipse(80.4, 84.6, 1.3, 0.85, -10), SKIN.deep, 0.85),
            (ribbon([(79.0, 85.6), (80.6, 86.1), (82.0, 85.5)], [0.1, 0.5, 0.1]), SKIN.hi, 0.6),
            # le flanc proche : un pli doux entre la poitrine et le ventre
            (ribbon([(39.0, 74.6), (43.0, 76.6), (47.4, 76.0)], [0.1, 0.9, 0.1]), SKIN.deep, 0.35)]
    # les cicatrices pâles : sur le pectoral proche (en biais), sur le ventre
    det += [(ribbon([(54.6, 60.4), (58.6, 63.6), (62.0, 67.4)], [0.2, 1.0, 0.2]), SCAR, 0.9),
            (ribbon([(54.9, 60.9), (58.8, 64.0), (61.8, 67.8)], [0.1, 0.35, 0.1]), SKIN.shadow, 0.6),
            (ribbon([(90.6, 81.2), (93.0, 79.6), (95.6, 79.4)], [0.2, 0.8, 0.2]), SCAR, 0.85)]
    fig.part('torso', torso, SKIN, grad=(100, 52, 44, 90, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=2.0, rim=0.7, cast=1.2, details=det, occl=(SKIN.deep, 0.22, 3.4))

    # le nœud de la corde, devant côté lointain : la boule, deux bouts qui pendent, le petit crâne de bête
    for nm, pts_, w_ in (('rend1', [(88.6, 92.6), (88.2, 96.6), (89.0, 100.4)], [1.8, 1.7, 1.4]),
                         ('rend2', [(90.2, 92.8), (91.6, 96.0), (91.8, 99.0)], [1.7, 1.6, 1.3])):
        sh = limb(pts_, w_)
        fig.part(nm, sh, ROPE, cel=0.5, rim=0.4, cast=0.8, cast_on=SKIRT + ['rope', 'fleg'],
                 details=[(ribbon([(pts_[0][0] + 0.4, pts_[0][1] + 1), (pts_[1][0] + 0.4, pts_[1][1]), (pts_[2][0] + 0.3, pts_[2][1] - 0.6)],
                                  [0.1, 0.5, 0.1]), ROPE.hi, 0.6)])
    fig.part('knot', ellipse(89.2, 91.4, 2.6, 2.2, -15), ROPE, cel=0.6, rim=0.5, cast=0.9,
             details=[(ellipse(89.8, 90.6, 1.2, 0.7, -25), ROPE.hi, 0.7),
                      (ribbon([(87.6, 91.0), (89.2, 92.2), (90.8, 91.6)], [0.1, 0.5, 0.1]), ROPE.shadow, 0.6)])
    fig.part('skcord', limb([(86.4, 92.4), (84.8, 95.2)], [1.0, 0.9]), ROPE, cel=0.3, rim=0.2, cast=0.5)
    skull = sm([(81.2, 96.4), (82.8, 95.0), (85.2, 94.8), (87.0, 96.0), (87.4, 98.0), (86.6, 99.4), (86.4, 101.4),
                (85.0, 102.0), (83.4, 101.8), (82.4, 100.8), (81.4, 99.4), (80.8, 97.8)])
    fig.part('skull', skull, BONE, cel=0.7, rim=0.5, cast=0.9, cast_on=SKIRT + ['rope', 'fleg'],
             details=[(ellipse(82.9, 97.9, 1.0, 1.15), BONE.deep, 0.9), (ellipse(85.6, 97.8, 0.9, 1.05), BONE.deep, 0.9),
                      (ellipse(84.4, 100.0, 0.45, 0.6), BONE.deep, 0.75),
                      (ribbon([(82.8, 101.4), (84.4, 101.7), (86.0, 101.2)], [0.1, 0.5, 0.1]), BONE.shadow, 0.8),
                      (ellipse(85.6, 95.8, 1.2, 0.5, -15), BONE.hi, 0.9)])
    # deux petites cornes du crâne
    fig.part('skhorn', sm([(86.2, 95.4), (88.0, 93.6), (89.4, 93.4), (88.4, 94.8), (87.2, 96.4)], sharp=(2,)), BONE,
             cel=0.3, rim=0.3, cast=0.4, cast_on=['skull', 'rope'])

    # ======================================================================== la tête du cyclope
    def draw_head():
        head = sm([(56.0, 22.8), (62.0, 21.2), (68.6, 21.0), (74.6, 21.9), (79.4, 24.0), (82.8, 27.2), (84.6, 31.2),
                   (85.4, 35.8), (85.9, 40.4), (85.9, 45.0), (85.4, 49.0),
                   (84.8, 52.2), (82.0, 54.6), (76.0, 55.8), (68.0, 56.2), (60.0, 55.6), (54.0, 53.8), (50.0, 50.8),
                   (48.0, 46.4), (47.0, 40.0), (47.0, 33.4), (48.6, 28.4), (51.8, 24.6)])
        hd = []
        # les plans : le côté (vers l'oreille) dans l'ombre, le dôme éclairé, la joue proche à mi-ton
        hd += [(sm([(47.0, 33.0), (52.0, 33.6), (56.0, 38.0), (57.4, 44.0), (56.4, 50.0), (58.4, 55.4), (54.0, 53.8),
                    (50.0, 50.8), (48.0, 46.4), (47.0, 40.0)]), SKIN.shadow, 0.5),
               (sm([(60.0, 22.4), (68.0, 21.6), (75.0, 22.6), (80.4, 25.6), (78.0, 26.6), (70.0, 25.0), (62.0, 24.6)]), SKIN.hi, 0.55),
               (ellipse(73.6, 23.4, 3.4, 1.0, 6), '#fff4d4', 0.7)]
        # la cicatrice pâle en biais sur le crâne
        hd += [(ribbon([(51.6, 25.6), (54.4, 28.4), (56.6, 31.8)], [0.2, 0.9, 0.2]), SCAR, 0.9),
               (ribbon([(51.9, 26.0), (54.6, 28.8), (56.6, 32.0)], [0.1, 0.3, 0.1]), SKIN.shadow, 0.6)]
        # les plis de colère sur le front (courts, inégaux)
        hd += [(ribbon([(60.4, 25.6), (64.6, 24.8), (68.6, 25.4)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.5),
               (ribbon([(70.4, 23.8), (73.6, 23.6), (76.0, 24.6)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.35),
               (ribbon([(71.4, 25.4), (71.8, 27.4)], [0.1, 0.7]), SKIN.deep, 0.4)]
        # l'orbite creusée sous le sourcil, la pommette éclairée, la poche sous l'œil
        e = P['eye']
        ex, ey = EYE_C
        hd += [(ellipse(ex - 0.6, ey + 0.4, 8.4, 6.2, -4), SKIN.shadow, 0.35),
               (ellipse(ex + 11.0, ey + 3.4, 2.8, 2.2, -20), SKIN.hi, 0.45),
               (ribbon([(ex - 6.2, ey + 5.0), (ex, ey + 6.4), (ex + 6.0, ey + 5.6)], [0.1, 0.9, 0.1]), SKIN.shadow, 0.6),
               (ribbon([(ex - 5.4, ey + 5.8), (ex, ey + 7.2), (ex + 5.6, ey + 6.4)], [0.1, 0.5, 0.1]), SKIN.light, 0.5),
               # les pattes d'oie de colère au coin extérieur de l'œil
               (ribbon([(ex - 8.4, ey - 0.6), (ex - 10.2, ey + 0.2)], [0.5, 0.1]), SKIN.deep, 0.5),
               (ribbon([(ex - 8.2, ey + 1.8), (ex - 10.0, ey + 3.2)], [0.5, 0.1]), SKIN.deep, 0.45)]
        # l'œil unique : le blanc (ombré sous le sourcil), l'iris ambre en anneau qui roule, la pupille, le reflet
        white = ellipse(ex, ey, 6.5, 4.5, -3)
        bl = P['blink']
        if bl < 0.95:
            hd += [(ellipse(ex - 0.1, ey + 0.1, 7.3, 5.3, -3), '#3a1424', 0.95),
                   (white, ('lin', ex, ey - 4.5, ex, ey + 4.5, [(0, EYE_W[2]), (0.3, EYE_W[1]), (0.55, EYE_W[0]), (1, EYE_W[0])]), 1)]
            ix, iy = ex + 0.7 + e[0], ey - 0.2 + e[1]
            g = glow
            irs = [(0, IRIS[0] if g < 1 else '#ffffff'), (0.35, IRIS[1] if g < 1.5 else IRIS[0]), (0.7, IRIS[2] if g < 1.5 else IRIS[1]),
                   (1, IRIS[3] if g < 1.5 else IRIS[2])]
            iris = ellipse(ix, iy, 3.7, 4.0)
            # l'iris est coupé par le blanc (paupières) : on le peint dans un chemin « blanc ∩ iris » via un masque simple :
            # on ne le laisse pas sortir du blanc en le rétrécissant près des bords
            hd += [(iris.scale(1.08, 1.08, ix, iy), IRIS[4], 1),
                   (iris, ('rad', ix + 0.8, iy - 1.0, 4.2, 4.2, irs), 1),
                   (ellipse(ix + 0.3, iy + 0.2, 1.05, 2.35), '#1e0c18', 1),
                   (ellipse(ix + 1.4, iy - 1.6, 0.95, 0.75, -20), '#ffffff', 0.95),
                   (ellipse(ix - 1.2, iy + 1.8, 0.4, 0.3), '#ffffff', 0.6)]
            # l'ombre du sourcil sur le haut de l'œil (par-dessus l'iris)
            cres = [(ex + 6.5 * math.cos(math.radians(t)), ey + 4.5 * math.sin(math.radians(t))) for t in range(180, 361, 15)]
            cres += [(ex + 6.5 * math.cos(math.radians(t)), ey + 4.5 * 0.3 * math.sin(math.radians(t)) - 0.6) for t in range(345, 179, -15)]
            hd += [(sm(cres, sharp=(0, 12)), EYE_W[2], 0.45)]
            if bl > 0.05:
                # la paupière qui descend (peau), la ligne des cils en bas
                k = bl
                lid = sm([(ex - 7.2, ey - 5.6), (ex + 7.0, ey - 5.6), (ex + 6.8, ey - 4.8 + 9.6 * k), (ex, ey - 4.4 + 10.6 * k),
                          (ex - 6.8, ey - 4.6 + 9.2 * k)])
                hd += [(lid, ('lin', ex, ey - 5, ex, ey + 5, [(0, SKIN.base), (1, SKIN.shadow)]), 1),
                       (ribbon([(ex - 6.8, ey - 4.6 + 9.2 * k), (ex, ey - 4.4 + 10.6 * k), (ex + 6.8, ey - 4.8 + 9.6 * k)], [0.2, 0.9, 0.2]), '#3a1424', 0.9)]
        else:
            # l'œil fermé : la paupière de peau, la ligne des cils en bas (un sourire de colère)
            hd += [(white, ('lin', ex, ey - 5, ex, ey + 5, [(0, SKIN.base), (1, SKIN.shadow)]), 1),
                   (ribbon([(ex - 6.4, ey + 1.0), (ex, ey + 2.6), (ex + 6.4, ey + 1.0)], [0.2, 1.0, 0.2]), '#3a1424', 0.9),
                   (ribbon([(ex - 4.0, ey - 1.6), (ex + 1.0, ey - 2.4), (ex + 5.0, ey - 1.4)], [0.1, 0.5, 0.1]), SKIN.light, 0.6)]
        if glow > 0:
            hd += [(ellipse(ex + 1.4, ey - 0.4, 9.0, 7.6), ('rad', ex + 1.4, ey - 0.4, 9.0, 9.0,
                                                           [(0, EARTH[1], 0.0), (0.45, EARTH[1], 0.32 * min(1, glow)), (1, EARTH[2], 0)]), 1)]
        # le sourcil unique, épais, froncé en V : un bourrelet de poil brun, le dessus éclairé, quelques poils
        brow = sm([(53.4, 27.4), (58.0, 25.6), (63.6, 24.8), (69.0, 26.0), (72.4, 28.0), (76.6, 25.8), (81.0, 25.0), (84.2, 26.2),
                   (84.4, 28.6), (80.6, 29.2), (76.6, 30.4), (73.0, 32.4), (69.4, 31.4), (64.0, 30.2), (58.6, 30.6), (54.6, 30.4)],
                  sharp=(0, 4, 8, 11))
        hd += [(brow.scale(1.05, 1.18, 69, 28.4), '#3a1424', 0.55),
               (brow, ('lin', 70, 24.8, 70, 32.4, [(0, FUR.light), (0.4, FUR.base), (1, FUR.deep)]), 1),
               (ribbon([(55.0, 27.2), (60.0, 25.8), (65.4, 25.6), (70.6, 27.6)], [0.1, 0.8, 0.7, 0.1]), FUR.hi, 0.55),
               (ribbon([(74.4, 27.4), (79.0, 25.8), (83.4, 26.4)], [0.1, 0.8, 0.1]), FUR.hi, 0.65),
               (ribbon([(60.6, 28.8), (63.0, 27.6), (65.4, 28.6)], [0.1, 0.5, 0.1]), FUR.deep, 0.5),
               (ribbon([(77.6, 28.4), (80.0, 27.4), (82.2, 28.2)], [0.1, 0.45, 0.1]), FUR.deep, 0.45)]
        # le nez épaté, court, sur la médiane sous l'œil (son bout dépasse à peine vers la droite) : l'arête éclairée, le
        # bout rond, les narines, l'ombre portée à gauche
        nx, ny = NOSE
        N = lambda pts: [(nx + x, ny + y) for x, y in pts]
        hd += [(sm(N([(-3.8, -0.8), (-0.4, -1.6), (3.2, -0.8), (4.6, 1.2), (3.4, 3.4), (0.0, 3.8), (-3.2, 3.2), (-4.4, 1.2)])), SKIN.deep, 0.32),
               (sm(N([(-2.6, -1.9), (0.6, -2.2), (3.6, -1.2), (4.6, 0.8), (3.4, 2.6), (0.2, 3.0), (-2.8, 2.4), (-3.8, 0.4)])),
                ('lin', nx + 4.6, ny - 2.6, nx - 3.8, ny + 3.0, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]), 1),
               (ellipse(nx + 1.8, ny - 1.0, 1.6, 0.8, 16), '#fff0cc', 0.6),
               (ellipse(nx + 1.4, ny + 1.8, 1.15, 0.55, 8), '#3a1424', 0.75),
               (ellipse(nx - 2.0, ny + 1.6, 0.8, 0.45, -8), '#3a1424', 0.5)]
        # la bouche : fermée au repos (une grimace, les coins tirés vers le bas, la mâchoire du bas qui avance) ; elle
        # s'ouvre en grand quand il frappe (mo) : la gorge rouge sombre, la langue, les dents de travers en haut
        mo = P['mouth']
        MX, MY = MOUTH_C
        if mo > 0.04:
            mouth = sm([(MX + -6.96, MY + 1.10), (MX + -4.44, MY + -0.10), (MX + 0.00, MY + -0.30), (MX + 4.44, MY + -0.10), (MX + 6.96, MY + 0.90), (MX + 5.77, MY + 1.70 + 2.6 * mo),
                        (MX + 2.22, MY + 2.30 + 4.2 * mo), (MX + -2.22, MY + 2.50 + 4.4 * mo), (MX + -5.62, MY + 1.90 + 2.8 * mo)], sharp=(0, 4))
            hd += [(mouth.scale(1.05, 1.18, MX, MY + 1.3 + 2 * mo), '#2a0c1c', 0.95),
                   (mouth, ('lin', MX, MY - 0.3, MX, MY + 2.7 + 4 * mo, [(0, MOUTH[0]), (0.6, MOUTH[1]), (1, MOUTH[1])]), 1),
                   (ellipse(MX + 0.00, MY + 2.10 + 3.6 * mo, 5.0, 0.8 + 0.9 * mo), MOUTH[2], 0.9)]
            for (dx, w_, h_) in ((-4.6, 1.9, 1.6), (-2.3, 2.1, 2.0), (0.0, 2.0, 1.7), (2.4, 2.1, 2.1), (4.6, 1.8, 1.5)):
                x, yt = MX + dx, MY - 0.2
                hd.append((sm([(x - w_ / 2, yt), (x + w_ / 2, yt + 0.1), (x + w_ * 0.3, yt + h_ * mo + 0.4), (x - w_ * 0.25, yt + h_ * mo + 0.2)]),
                           BONE.light, 1))
        # les lèvres serrées : la fente sombre (plus épaisse au milieu), la lèvre du haut éclairée, celle du bas qui avance
        lip = [(MX + -6.96, MY + 1.30 + 0.6 * mo), (MX + -4.14, MY + 0.30), (MX + 0.00, MY + 0.00), (MX + 4.14, MY + 0.20), (MX + 6.96, MY + 1.10 + 0.6 * mo)]
        if mo <= 0.04:
            hd += [(ribbon(lip, [0.2, 0.9, 1.1, 0.9, 0.2]), '#3a1424', 0.92),
                   (ribbon([(MX + -6.81, MY + 1.90), (MX + -6.22, MY + 3.10)], [0.5, 0.1]), '#3a1424', 0.5),
                   (ribbon([(MX + 6.81, MY + 1.70), (MX + 6.36, MY + 2.90)], [0.5, 0.1]), '#3a1424', 0.5),
                   (ribbon([(MX + -4.88, MY + -0.70), (MX + 0.00, MY + -1.10), (MX + 4.88, MY + -0.80)], [0.1, 0.7, 0.1]), SKIN.shadow, 0.5)]
        # la lèvre du bas, la grosse mâchoire qui avance, le menton éclairé
        dj = 4.0 * mo
        hd += [(ribbon([(MX + -5.92, MY + 2.10 + dj), (MX + 0.00, MY + 2.70 + dj), (MX + 5.92, MY + 2.10 + dj)], [0.1, 1.1, 0.1]), SKIN.light, 0.45),
               (ribbon([(MX + -6.36, MY + 3.30 + dj), (MX + 0.00, MY + 4.10 + dj), (MX + 6.36, MY + 3.30 + dj)], [0.1, 0.8, 0.1]), SKIN.shadow, 0.55),
               (sm([(MX + -1.48, MY + 4.50), (MX + 4.44, MY + 3.90), (MX + 8.44, MY + 2.30), (MX + 7.40, MY + 4.30), (MX + 2.96, MY + 5.50), (MX + -1.48, MY + 5.70)]), SKIN.hi, 0.4),
               (ribbon([(54.0, 49.4), (MX + -11.40, MY + 2.30), (MX + -7.40, MY + 4.90)], [0.1, 0.8, 0.1]), SKIN.deep, 0.4)]
        # les défenses tordues qui montent de la mâchoire du bas, aux deux coins de la bouche (la lointaine un peu
        # plus petite), devant la lèvre du haut
        for (pts_, w0) in (([(MX + -6.36, MY + 4.10), (MX + -6.96, MY + 1.50), (MX + -6.22, MY + -0.90), (MX + -6.81, MY + -3.50)], 2.5),
                           ([(MX + 6.22, MY + 3.70), (MX + 6.66, MY + 1.50), (MX + 6.22, MY + -0.50), (MX + 6.81, MY + -2.50)], 2.1)):
            pts_ = [(x, y + dj * (1 - i / 3)) for i, (x, y) in enumerate(pts_)]
            tk = lock(pts_[0], pts_[1], pts_[2], pts_[3], w0, n=10, bulge=0.05)
            hd += [(tk.scale(1.18, 1.06, pts_[0][0], (pts_[0][1] + pts_[3][1]) / 2), '#3a1424', 0.9),
                   (tk, ('lin', pts_[0][0] + 1.4, pts_[3][1], pts_[0][0] - 1.4, pts_[0][1], [(0, BONE.hi), (0.45, BONE.light), (1, BONE.shadow)]), 1),
                   (ribbon([(pts_[0][0] + 0.5, pts_[0][1] - 1.0), (pts_[1][0] + 0.6, pts_[1][1]), (pts_[2][0] + 0.4, pts_[2][1])], [0.1, 0.5, 0.1]), '#ffffff', 0.6)]
        fig.part('head', head, SKIN, grad=(84, 22, 52, 54, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
                 cel=1.3, rim=0.65, cast=1.4, details=hd)
        # la grande oreille décollée, côté proche : son creux dans l'ombre (la racine se fond dans la peau du crâne)
        ear = sm([(49.4, 32.2), (46.4, 29.6), (43.2, 28.8), (41.0, 30.8), (40.8, 35.0), (41.8, 39.8), (43.8, 43.6), (46.4, 45.4),
                  (49.6, 44.6)])
        fig.part('ear', ear, SKIN, grad=(84, 22, 52, 54, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
                 cel=0.9, rim=0.5, cast=0.9, cast_on=['head', 'torso'],
                 details=[(sm([(48.2, 33.4), (45.6, 31.4), (43.6, 31.2), (42.8, 34.4), (43.4, 38.6), (45.2, 42.0), (47.6, 42.8)]),
                           ('lin', 46, 31, 44, 42, [(0, SKIN.shadow), (1, SKIN.deep)]), 0.85),
                          (ribbon([(44.6, 33.0), (44.4, 36.6), (45.6, 40.0)], [0.1, 0.8, 0.1]), SKIN.base, 0.6),
                          (ribbon([(42.0, 31.6), (41.6, 35.6), (42.8, 40.4)], [0.1, 0.6, 0.1]), SKIN.light, 0.5),
                          (sm([(49.4, 32.2), (48.6, 38.0), (49.6, 44.6), (51.0, 38.0)]), SKIN.base, 0.5)])

    # ======================================================================== le bras proche (droit), levé : épaule →
    # coude → poignet d'un seul tenant ; le coude placé par le squelette (le poignet suit le poing)
    def draw_near():
        Sn = mapp(UC, (S_N[0] + P['nsh'][0], S_N[1] + P['nsh'][1] - 0.8 * P['rn']))
        Snu = mapp(inv(U), Sn)
        Wn = Cp(WRN[0], WRN[1])
        En, Wn2 = ik(Snu, Wn, LN1, LN2, P['bn'])
        keys = [(0, 9.0, 9.0), (0.16, 8.8, 8.6), (0.38, 8.0, 7.4), (0.56, 6.8, 6.6), (0.66, 7.2, 7.2), (0.82, 6.6, 6.6), (1, 6.0, 6.0)]
        arm = round_limb([Snu, En, Wn2], keys, n=34)
        a1, a2 = Seg(Snu, En), Seg(En, Wn2)
        aa1 = math.degrees(math.atan2(a1.u[1], a1.u[0]))
        aa2 = math.degrees(math.atan2(a2.u[1], a2.u[0]))
        # le côté du bras tourné vers la lumière (haut-droit), pour poser biceps et deltoïde
        s1 = 1 if (a1.v[0] * 0.6 - a1.v[1] * 0.8) > 0 else -1
        s2 = 1 if (a2.v[0] * 0.6 - a2.v[1] * 0.8) > 0 else -1
        ad = [
            # le deltoïde rond éclairé (le haut de l'épaule)
            (ellipse(*a1(1.6, 3.2 * s1), 7.0, 5.2, aa1), SKIN.light, 0.42),
            (ellipse(*a1(0.4, 5.4 * s1), 3.6, 1.6, aa1), SKIN.hi, 0.45),
            (ribbon([a1.at(0.24, 8.0 * s1), a1.at(0.32, 1.0 * s1), a1.at(0.28, -7.0 * s1)], [0.1, 1.0, 0.1]), SKIN.shadow, 0.4),
            # le biceps gonflé (au-dessus, éclairé), le triceps dans l'ombre (dessous)
            (ellipse(*a1.at(0.6, 3.4 * s1), 7.4, 3.6, aa1), SKIN.light, 0.36),
            (ellipse(*a1.at(0.62, 4.6 * s1), 3.6, 1.3, aa1), SKIN.hi, 0.4),
            (ribbon([a1.at(0.42, -5.4 * s1), a1.at(0.66, -6.0 * s1), a1.at(0.9, -4.8 * s1)], [0.1, 1.6, 0.1]), SKIN.deep, 0.32),
            # la pointe du coude, le muscle de l'avant-bras près du coude
            (ellipse(*a2.at(0.04, -1.0 * s2), 2.2, 1.6, aa2), SKIN.shadow, 0.35),
            (ellipse(*a2.at(0.24, 2.6 * s2), 2.4, 4.0, aa2 - 90), SKIN.light, 0.4),
        ]
        fig.part('narm', arm, SKIN, grad=diag(SKIN, min(Snu[0], En[0], Wn2[0]) - 8, min(Snu[1], En[1], Wn2[1]) - 8,
                                                 max(Snu[0], En[0], Wn2[0]) + 8, max(Snu[1], En[1], Wn2[1]) + 8),
                 cel=1.9, rim=0.7, cast=1.4, cast_on=['torso', 'club', 'moss', 'rope', 'nleg', 'head', 'ear'] + SKIRT + ['spk%d' % i for i in range(4)],
                 details=ad)
        bc = a2.at(0.6)
        fig.part('nbrac', bracer(bc, aa2, 10.4, 13.8), LEATHER, cel=0.9, rim=0.6, cast=1.0, details=bracer_det(bc, aa2, 10.4, 13.8, s2))
        # le poing serré sur le manche : le dos de la main du côté du poignet, quatre doigts repliés qui passent devant
        # le manche (phalanges vers l'ennemi), le pouce par-dessus
        out = C_(sm([(-6.4, -6.4), (-2.0, -7.4), (3.4, -7.0), (6.6, -4.6), (7.2, 0.4), (6.6, 5.6), (3.4, 7.0),
                     (-1.0, 7.2), (-5.4, 6.2), (-7.2, 2.2), (-7.4, -2.6)]))
        fd = [(C_(sm([(-6.2, -6.0), (-2.0, -7.0), (3.2, -6.6), (5.4, -4.4), (2.0, -2.6), (-4.0, -2.6)])), SKIN.light, 0.4)]
        for i, (u0, u1) in enumerate(((-6.6, -3.4), (-3.4, -0.1), (-0.1, 3.3), (3.3, 6.4))):
            ve = 6.6 - abs(u0 + u1) * 0.12
            seg = C_(rpoly([(u0 + 0.2, -1.6), (u1 - 0.2, -1.6), (u1 - 0.3, ve), (u0 + 0.3, ve)], [0.7, 0.7, 1.6, 1.6]))
            fd += [(seg, SKIN.base, 0.6),
                   (C_(ellipse((u0 + u1) / 2 + 0.3 * up, ve - 1.4, abs(u1 - u0) * 0.32, 0.9)), SKIN.hi, 0.5),
                   (C_(ribbon([(u1, -1.0), (u1 - 0.05, 2.4), (u1 + 0.1, ve - 0.4)], [0.1, 0.55, 0.1])), SKIN.deep, 0.55 if i < 3 else 0)]
        fd += [(C_(ribbon([(-6.0, -1.8), (0.0, -2.2), (6.0, -1.6)], [0.1, 0.8, 0.1])), SKIN.deep, 0.35)]
        fig.part('nfist', out, SKIN, cel=1.3, rim=0.7, cast=1.1,
                 cast_on=['club', 'narm', 'nbrac', 'torso', 'spk0', 'spk1', 'moss', 'head', 'ear', 'rope'] + SKIRT, details=fd)
        thumb = C_(limb([(3.2, -6.4), (5.6, -2.6), (5.0, 2.6)], [3.6, 3.4, 3.0]))
        fig.part('nthumb', thumb, SKIN, cel=0.8, rim=0.6, cast=0.8, cast_on=['nfist', 'club'],
                 details=[(C_(ellipse(5.4, 2.0, 0.9, 1.1)), '#f4c8b0', 0.9), (C_(ellipse(5.6, 1.8, 0.4, 0.45)), '#ffffff', 0.6)])
        return En

    # l'ordre : la massue (derrière le bras), l'avant-bras lointain devant le ventre, la tête, le bras proche (devant la
    # tête seulement quand il est levé au-dessus d'elle)
    draw_club()
    draw_far_front()
    if P['front'] <= 0.5:
        En = draw_near()
        draw_head()
    else:
        draw_head()
        En = draw_near()

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['head', 'ear'], HEAD)
    fig.pose(['torso'], TOR)
    fig.pose(SKIRT + ['backfur'], CLO)
    fig.pose(['rope', 'knot', 'rend1', 'rend2', 'skcord', 'skull', 'skhorn', 'bonecord', 'bone'], PEL)
    club = ['club', 'moss'] + ['spk%d' % i for i in range(4)]
    fig.pose(club + ['narm', 'nbrac', 'nfist', 'nthumb', 'farm', 'ffore', 'fbrac', 'ffist', 'fthumb'], U)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(U=U, G=mapp(U, G), ang=ang + P['lean'] * 1.1, P=P, club_head=mapp(U, Cp(29.0, 0)), club_top=mapp(U, Cp(38.6, 0)),
                   chest=mapp(TOR, (72, 70)), head=mapp(HEAD, (68, 36)), eye=mapp(HEAD, EYE_C), feet=[BN, BF], HEAD=HEAD, ROOT=ROOTM,
                   ffist=mapp(U, FFp))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def main():
    """aurelle.svg (grand) et aurelle-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/angels-10.webp (512 px de haut) et angels-10-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('aurelle', 0.95, 512, ID_JEU), ('aurelle-petit', 1.35, 160, ID_JEU + '-160')):
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
