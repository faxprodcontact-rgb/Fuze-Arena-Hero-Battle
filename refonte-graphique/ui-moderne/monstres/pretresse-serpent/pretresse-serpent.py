# La prêtresse serpent (mon-meduse-sorts : clan de Méduse, terre, lanceuse de sorts, second rang ; elle pétrifie)
# redessinée en VECTORIEL lisse, dans le style moderne de l'interface (même outil, même trait, même échelle que les
# héros : ../../heros/atelier.py, ../../heros/kael/kael.py ; même clan qu'Ophira et Sarvik : mêmes écailles émeraude,
# même ventre jaune, même or, même violet, même peau de jade).
#
#   python3 refonte-graphique/ui-moderne/monstres/pretresse-serpent/pretresse-serpent.py
#   → pretresse-serpent.svg + public/art/vecto/mon-meduse-sorts.webp (512 px de haut) et mon-meduse-sorts-160.webp
#
# Même créature que le pixel art (refonte-graphique/pixel/hd/monstres/pretresse-serpent.txt) : une prêtresse naga
# mince et inquiétante, droite et immobile comme une statue. Buste très fin (épaules étroites, taille de guêpe) dans une
# longue robe violette fendue devant (on y voit les plaques jaunes du ventre du serpent), ceinture d'or à émeraude,
# ourlet d'or, un signe inventé brodé d'or sur le pan proche (un oeil de serpent et une goutte). Le corps de serpent sort
# sous la robe, tourne au sol devant elle et file vers la gauche, la pointe de la queue relevée en petit crochet. Grandes
# manches de prêtresse qui pendent sous les avant-bras (ourlet d'or) ; large collier d'or à perles d'émeraude (il fait
# le tour du cou). Visage long et étroit de jade, joues creuses, menton pointu, yeux verts luisants à pupille fendue
# sous des paupières lourdes, sourire mince et cruel aux lèvres sombres, la pointe d'un croc. Voile violet bordé d'or
# posé sur la tête (il encadre le visage et tombe dans le dos), diadème d'or à émeraude ; trois petits serpents sortent
# de la coiffe. Main lointaine serrée sur le sceptre tenu droit (doigts devant la tige, pouce par-dessus) ; main proche
# avancée devant la robe, longs doigts griffus recourbés vers le bas. Sceptre : tige de bronze, tête de serpent d'or de
# profil (gueule ouverte, croc, oeil d'émeraude), grosse pierre verte sertie sur sa tête, bague d'or, pointe en bas.
# Coordonnées = pixels de l'image du jeu (128 × 120, le point « pieds » en (64, 116), le sol y = 116), pour se poser au
# même endroit que le pixel art. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HERE)
sys.path.insert(0, HEROS)
from atelier import Figure, Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, sides, bez, resample  # noqa: E402,F401
from outils import (bent, crpath, taper, union, poly_of, shape_of, smooth_path, tube_poly, normals, band_poly,  # noqa: E402,F401
                    shape_poly, fuse, geom_shapes)
from visage import placer, verifier  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID = 'mon-meduse-sorts'

# ---------- matières (celles d'Ophira et de Sarvik, le même clan ; à elle : le voile plus sombre, la pierre verte) ----------
SKIN = Mat('#d8f4c8', '#8ccfa2', '#4ea28a', '#2b6e72', '#1a3c5a')            # peau de jade
SCALE = Mat('#d8f070', '#7cc63e', '#2e8c34', '#1a5c36', '#103636')           # écailles émeraude
SCALEB = Mat('#b8e05c', '#62ac3a', '#257830', '#164e34', '#0e3032')          # écailles des serpents du fond
BELLY = Mat('#fff8cc', '#f6da74', '#dcaa44', '#9c662e', '#5a3036')           # ventre jaune
GOLD = Mat('#fffbe0', '#fcd050', '#d89030', '#8e4822', '#46202a')            # or
PURPLE = Mat('#e2b8ff', '#b07ee0', '#7c44b0', '#4c2878', '#261642')          # robe
LILAC = Mat('#f0dcff', '#c8a0ec', '#9868cc', '#5e3a92', '#301c50')           # grandes manches (un violet plus clair)
VEIL = Mat('#d4b0f8', '#9a6ad4', '#6a3ea6', '#442472', '#24143e')            # voile (un violet plus profond)
EMER = Mat('#eaffd8', '#78e890', '#22a862', '#0e6450', '#08343a')            # émeraudes
STONE = Mat('#f0fff0', '#9cffb4', '#2fd070', '#138a4a', '#0a3a22')           # la pierre du sceptre
BRONZE = Mat('#fff6d8', '#e8b066', '#b8743c', '#6e3828', '#2e1a26')          # tige du sceptre
IVORY = Mat('#ffffff', '#f6f2e0', '#e2dcc4', '#a8a090', '#6a6070')           # griffes et croc
LIPS = ('#3c0c24', '#6e2040', '#9c4060')                                    # lèvres sombres
THROAT = '#4a0c26'
TONGUE = ('#ff9a9a', '#e0384a', '#9a1a34')
EYE = ('#fbffe0', '#d8ff7a', '#8cf03c', '#2f9a3a', '#0c2a18')                # coeur, clair, lueur, bord, pupille
LASH = '#0e2230'
VEN = ['#f6ffc8', '#b8ff58', '#6cd23c', '#2a9a4a', '#0e5a3e']                # venin (le vert du regard)

GRD = 116          # le sol
FEET = (64, 116)   # le point « pieds » du pixel art
FRAME = (8.0, 14.0, 90.0, 104.0)

# ---------- le visage (méthode commune, ../../heros/visage.py) ----------
# La boîte de la face (ovale du visage sans le voile, repère de la tête AVANT son ×1,1) : visage long et étroit.
FACE_BOX = (58.6, 34.6, 71.6, 53.0)
FACE_TOUR = 18
FACE_V = placer(FACE_BOX, tour=FACE_TOUR, l_oeil=0.24)
NECK_P = (66.0, 52.0)      # la tête tourne autour de ce point (haut du cou)
HK = 1.1                   # la tête un peu plus grande que le pixel art (comme les héros)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Pixels du dessin, degrés (y vers le bas).
#   breath : souffle 0..1 ; lean : le buste se porte vers l'ennemi (+) (la robe se cisaille, le bas ne bouge pas) ;
#   wave : le corps de serpent caché sous la robe la bombe (+ vers la droite) ; rise : elle se dresse (la robe
#   s'allonge vers le haut) ; hook : le crochet de la queue se relève (+) ; hump : (0..1, hauteur) une petite bosse qui
#   court sur le corps posé au sol ; head / tilt : la tête ; blink : paupières ; flare : les yeux s'allument (0..1) ;
#   sn : décalage de la tête de chaque petit serpent ; tg : leur langue (0 rentrée .. 2 longue) ; gape : leur gueule ;
#   arm : le poing lointain (et le sceptre) se déplace ; stilt : le sceptre s'incline (degrés, + vers l'ennemi) ;
#   gem : la pierre brûle (0..1) ; nhand : la main proche se déplace ; curl : ses doigts se replient (+) ou
#   s'ouvrent (−) ; smile : le sourire s'étire.
REST = dict(breath=0.0, lean=0.0, wave=0.0, rise=0.0, hook=0.0, hump=(0.0, 0.0), head=(0.0, 0.0), tilt=0.0,
            blink=0.0, flare=0.0, sn=None, tg={'SA': 1.0, 'SB': 0.7, 'SC': 0.0}, gape=None, arm=(0.0, 0.0), stilt=0.0, gem=0.0,
            nhand=(0.0, 0.0), curl=0.0, smile=0.0)

HEM_Y = 102.0              # l'ourlet (la robe ne bouge pas sous cette ligne)
SHO_Y = 58.0               # la ligne des épaules
SN0, EN0, WN0 = (57.2, 58.6), (54.0, 67.2), (60.8, 72.6)      # bras proche : épaule, coude, poignet
SF0, EF0, WF0 = (71.6, 58.6), (74.4, 67.0), (79.4, 61.4)      # bras lointain
FIST0 = (82.6, 59.6)                                           # le poing lointain (sur la tige)
STAFF_X = 82.9


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def norm(v):
    L = math.hypot(*v) or 1
    return (v[0] / L, v[1] / L)


def ik(S, W, L1, L2, bend):
    """Le coude (épaule S, poignet W, longueurs L1, L2), plié d'un côté (bend = ±1)."""
    d = math.dist(S, W)
    k = max(1.0, d / (L1 + L2 - 0.6))
    L1, L2 = L1 * k, L2 * k
    dd = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, d))
    alpha = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    th = math.atan2(W[1] - S[1], W[0] - S[0]) + bend * alpha
    return (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))


def bend_of(S, E, W):
    """Le côté du pli qui redonne le coude de repos."""
    a = ik(S, W, math.dist(S, E), math.dist(E, W), 1)
    b = ik(S, W, math.dist(S, E), math.dist(E, W), -1)
    return 1 if math.dist(a, E) < math.dist(b, E) else -1


BEND_N = bend_of(SN0, EN0, WN0)
BEND_F = bend_of(SF0, EF0, WF0)
LN = (math.dist(SN0, EN0), math.dist(EN0, WN0))
LF = (math.dist(SF0, EF0), math.dist(EF0, WF0))


def curve_pts(pts, n):
    """n+1 points réguliers sur la courbe souple qui passe par pts."""
    sh = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        seg = bez(p1, c1, c2, p2, 16)
        sh += seg if not sh else seg[1:]
    return resample(sh, n)


def curve_band(I, O, t0, t1):
    """La bande entre deux courbes (I : bord du haut, O : bord du bas, même nombre de points), de t0 à t1 en travers ;
    prolongée aux deux bouts (la découpe du morceau la ramène au bord : elle va d'un bord à l'autre)."""
    A = [lerp(a, b, t0) for a, b in zip(I, O)]
    B = [lerp(a, b, t1) for a, b in zip(I, O)]

    def ext(P):
        a, b = P[0], P[1]
        y, z = P[-1], P[-2]
        return [add(a, (a[0] - b[0], a[1] - b[1]), 3)] + P + [add(y, (y[0] - z[0], y[1] - z[1]), 3)]
    A, B = ext(A), ext(B)
    pts = A + B[::-1]
    return sm(pts, sharp=(0, len(A) - 1, len(A), len(pts) - 1), t=0.8)


def offset_line(pts, d):
    """La ligne décalée de d (à gauche du sens de marche, à l'écran : (dy, −dx) normalisé × −d)."""
    out = []
    n = len(pts)
    for i, p in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        u = norm((b[0] - a[0], b[1] - a[1]))
        out.append((p[0] - u[1] * d, p[1] + u[0] * d))
    return out


# ======================================================================== la robe (rest), et sa déformation
def warp_fn(P):
    """La déformation de la robe (et de ce qu'elle porte) : rien sous l'ourlet ; au-dessus, le buste se porte de côté
    (lean), le ventre caché bombe la robe (wave), elle se dresse (rise), le souffle soulève le haut."""
    lean, wave, rise, br = P['lean'], P['wave'], P['rise'], P['breath']

    def W(p):
        x, y = p
        t = (HEM_Y - y) / (HEM_Y - SHO_Y)
        t = max(0.0, min(1.2, t))
        tc = min(1.0, t)
        dx = lean * t ** 1.3 + wave * math.sin(math.pi * tc) * 0.9
        up = max(0.0, min(1.0, (t - 0.55) / 0.45))
        up = up * up * (3 - 2 * up)
        dy = -rise * t - 0.6 * br * up
        return (x + dx, y + dy)
    return W


def robe_shapes():
    """La robe d'une seule forme (buste + jupe), et les lignes utiles (au repos)."""
    robe = sm([(56.4, 57.0), (64.8, 56.2), (73.8, 57.0), (72.6, 61.0), (70.9, 64.6), (70.2, 67.8), (71.0, 72.0),
               (73.4, 81.0), (76.4, 90.6), (79.4, 99.4), (79.8, 101.2), (75.0, 102.4), (68.0, 103.0), (60.0, 102.9),
               (52.0, 102.3), (46.6, 101.4), (44.4, 100.4), (44.6, 96.0), (46.0, 88.0), (48.6, 80.6), (52.6, 73.4),
               (57.4, 68.6), (59.0, 65.4), (58.2, 61.4)], sharp=(9, 10, 16, 17), t=0.9)
    return robe


HEM_L = [(44.4, 100.4), (46.6, 101.4), (52.0, 102.3), (60.0, 102.9), (68.0, 103.0), (75.0, 102.4), (79.8, 101.2)]
SLIT_L = [(65.4, 69.4), (65.0, 78.0), (64.2, 90.0), (63.2, 103.2)]
SLIT_R = [(66.6, 69.4), (67.8, 78.0), (69.6, 90.0), (72.0, 103.0)]
BELT_T = [(56.0, 66.6), (60.0, 67.2), (66.0, 67.6), (71.0, 67.0), (74.0, 66.4)]
BELT_B = [(56.0, 69.2), (60.0, 69.9), (66.0, 70.3), (71.0, 69.7), (74.0, 69.0)]


def robe_part(fig, P, W):
    robe = robe_shapes().map(W)
    det = []
    # le côté proche (gauche) dans l'ombre douce, le pan lointain éclairé (lumière en haut à droite)
    det += [(sm([W(p) for p in [(44.0, 101.6), (45.6, 90.0), (48.6, 80.6), (53.0, 72.8), (57.4, 68.8), (60.6, 70.2),
                                (55.6, 78.0), (52.4, 88.0), (51.2, 102.6)]]), PURPLE.shadow, 0.5),
            (sm([W(p) for p in [(71.4, 72.6), (73.2, 80.4), (76.0, 90.0), (78.6, 98.6), (76.6, 99.0), (73.6, 90.0),
                                (71.0, 80.6), (69.8, 73.4)]]), PURPLE.light, 0.45)]
    # deux plis doux qui tombent de la ceinture (jamais des rayures)
    det += [(ribbon([W(p) for p in [(59.0, 71.0), (56.6, 84.0), (55.4, 102.6)]], [0.2, 1.3, 0.5]), PURPLE.shadow, 0.55),
            (ribbon([W(p) for p in [(60.0, 71.6), (58.0, 84.6), (57.0, 102.6)]], [0.1, 0.55, 0.2]), PURPLE.light, 0.4),
            (ribbon([W(p) for p in [(70.6, 72.4), (72.0, 86.0), (74.4, 102.0)]], [0.1, 0.8, 0.3]), PURPLE.shadow, 0.35)]
    # la fente devant : le ventre du serpent en plaques jaunes, bordée d'or des deux côtés
    SL = [W(p) for p in SLIT_L]
    SR = [W(p) for p in SLIT_R]
    slit = sm(SL + [W((67.6, 104.6))] + SR[::-1], sharp=(0, len(SL) - 1, len(SL) + 1, len(SL) * 2), t=0.8)
    det += [(slit, ('lin', SR[0][0] + 2, SR[0][1], SL[-1][0] - 2, SL[-1][1], [(0, BELLY.light), (0.5, BELLY.base), (1, BELLY.shadow)]), 1)]
    for k, y in enumerate((75.0, 80.2, 85.6, 91.2, 97.0)):
        a, b = lerp(SL[0], SL[-1], (y - 69.4) / 33.8), lerp(SR[0], SR[-1], (y - 69.4) / 33.8)
        m = lerp(a, b, 0.5)
        m = (m[0], m[1] + 0.7 + 0.12 * k)
        det += [(ribbon([add(a, (-1, 0)), m, add(b, (1, 0))], [0.2, 0.75, 0.2]), BELLY.shadow, 0.8),
                (ribbon([add(a, (-1, 0.8)), (m[0], m[1] + 0.8), add(b, (1, 0.8))], [0.1, 0.5, 0.1]), BELLY.hi, 0.6)]
    det += [(ribbon(curve_pts(SL, 12), [0.4] + [1.25] * 11 + [1.1]), GOLD.base, 1),
            (ribbon(curve_pts([add(p, (0.25, 0)) for p in SL], 12), [0.1] + [0.45] * 11 + [0.3]), GOLD.hi, 0.85),
            (ribbon(curve_pts(SR, 12), [0.4] + [1.25] * 11 + [1.1]), GOLD.base, 1),
            (ribbon(curve_pts([add(p, (0.3, -0.1)) for p in SR], 12), [0.1] + [0.45] * 11 + [0.3]), GOLD.light, 0.9)]
    # l'ourlet d'or (il suit le bas de la robe, d'un bord à l'autre)
    HL = curve_pts([W(p) for p in HEM_L], 24)
    HU = [add(p, (0, -2.2)) for p in HL]
    det += [(curve_band(HU, HL, 0.0, 1.6), GOLD.base, 1), (curve_band(HU, HL, 0.0, 0.28), GOLD.light, 0.95),
            (curve_band(HU, HL, 0.72, 1.6), GOLD.shadow, 0.8)]
    # la ceinture d'or (une courbe en perspective qui fait le tour de la taille)
    BT = curve_pts([W(p) for p in BELT_T], 20)
    BB = curve_pts([W(p) for p in BELT_B], 20)
    det += [(curve_band(BT, BB, 0.0, 1.0), ('lin', 74, 66, 58, 70, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
            (curve_band(BT, BB, 0.0, 0.25), GOLD.hi, 0.75), (curve_band(BT, BB, 0.78, 1.0), GOLD.shadow, 0.85)]
    # le signe brodé d'or sur le pan proche : un oeil de serpent (amande, pupille fendue) et une goutte dessous
    cx, cy = W((53.4, 87.0))
    almond = sm([(cx - 2.4, cy), (cx - 0.8, cy - 1.25), (cx + 0.9, cy - 1.2), (cx + 2.4, cy), (cx + 0.9, cy + 1.2),
                 (cx - 0.8, cy + 1.25)], sharp=(0, 3), t=0.9)
    inner = sm([(cx - 1.6, cy), (cx - 0.6, cy - 0.62), (cx + 0.7, cy - 0.6), (cx + 1.6, cy), (cx + 0.7, cy + 0.6),
                (cx - 0.6, cy + 0.62)], sharp=(0, 3), t=0.9)
    ring_ = almond.hole(inner)
    ring_.evenodd = True
    slitp = sm([(cx + 0.05, cy - 0.85), (cx + 0.38, cy), (cx + 0.05, cy + 0.85), (cx - 0.28, cy)], sharp=(0, 2), t=0.9)
    dropc = (cx - 0.3, cy + 4.2)
    dr = sm([(dropc[0], dropc[1] - 2.0), (dropc[0] + 0.95, dropc[1] - 0.1), (dropc[0] + 0.7, dropc[1] + 0.8),
             (dropc[0], dropc[1] + 1.1), (dropc[0] - 0.7, dropc[1] + 0.8), (dropc[0] - 0.95, dropc[1] - 0.1)], sharp=(0,), t=0.9)
    det += [(ring_, GOLD.light, 0.95), (slitp, GOLD.base, 1), (dr, GOLD.base, 0.95),
            (ellipse(dropc[0] + 0.3, dropc[1] - 0.1, 0.25, 0.35), GOLD.hi, 0.8)]
    fig.part('robe', robe, PURPLE, grad=(80, 58, 46, 102, [(0, PURPLE.light), (0.45, PURPLE.base), (1, PURPLE.shadow)]),
             cel=1.5, rim=0.7, cast=1.2, details=det, occl=(PURPLE.deep, 0.18, 3.0))
    # la boucle de la ceinture : une émeraude ovale sertie d'or, sur la médiane
    bc = W((66.2, 69.0))
    fig.part('buckle', ellipse(bc[0], bc[1], 2.0, 1.75), GOLD, cel=0.5, rim=0.4, cast=0.7, cast_on=['robe'],
             details=[(ellipse(bc[0] + 0.05, bc[1] + 0.05, 1.3, 1.1), EMER.shadow, 1),
                      (ellipse(bc[0] + 0.15, bc[1] - 0.1, 1.0, 0.85), ('lin', bc[0] + 1, bc[1] - 1, bc[0] - 1, bc[1] + 1, [(0, EMER.light), (1, EMER.base)]), 1),
                      (ellipse(bc[0] + 0.45, bc[1] - 0.4, 0.32, 0.25), EMER.hi, 0.95)])
    return SL, SR


# ======================================================================== le corps de serpent (au sol)
# Points clés (x, y, largeur) de la ligne du milieu : il descend sous la robe, sort à droite devant elle, tourne au sol
# et file vers la gauche, posé à plat ; la pointe se relève en petit crochet.
BODY0 = [(62.0, 92.0, 15.0), (67.0, 100.5, 14.0), (69.6, 106.4, 12.6), (66.0, 110.2, 11.6), (57.0, 110.6, 11.4),
         (46.0, 110.7, 11.0), (35.0, 110.6, 10.2), (26.6, 110.2, 9.2)]
HOOK0 = [(20.6, 108.6, 7.6), (17.0, 105.0, 5.6), (17.2, 101.4, 3.8), (19.8, 99.4, 1.4)]
HOOK_BASE = (22.0, 109.0)


def body_keys(P):
    keys = []
    hp, ha = P['hump']
    n = len(BODY0) - 1
    for i, (x, y, w) in enumerate(BODY0):
        u = i / n
        dx = 0.0
        if i <= 2:
            dx = P['wave'] * 0.5 * (1 - i / 2)
        bump = ha * math.exp(-((u - hp) / 0.2) ** 2) if i >= 3 else 0.0
        keys.append((x + dx, y - bump, w - 0.4 * bump))
    for i, (x, y, w) in enumerate(HOOK0):
        u = (i + 1) / len(HOOK0)
        r = rot((x - HOOK_BASE[0], y - HOOK_BASE[1]), P['hook'] * 9 * u)
        keys.append((HOOK_BASE[0] + r[0], HOOK_BASE[1] + r[1], w))
    return keys


def scale_crescents(c, ws, i0, i1, every=6.0, side=1):
    """Les écailles (comme Ophira et Sarvik) : de petites écailles en arc, en quinconce sur le dos, peu nombreuses et
    douces (jamais des rayures) : un arc sombre et, juste devant, son bord éclairé."""
    out = []
    nb = normals(c)
    row = 0
    i = i0
    while i < i1:
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        tx, ty = -ny, nx
        for f_ in ((0.5, 0.05) if row % 2 == 0 else (0.25, -0.2)):
            off = -side * f_ * w / 2
            q = (p[0] + nx * off, p[1] + ny * off)
            r = max(0.55, w * 0.075)
            ang = math.degrees(math.atan2(ty, tx))
            arc = xf(ribbon([(-r * 0.2, -r * 1.2), (r * 0.55, 0), (-r * 0.2, r * 1.2)], [0.05, r * 0.5, 0.05]), q[0], q[1], ang)
            lip = xf(ribbon([(-r * 0.75, -r * 1.0), (-r * 0.05, 0), (-r * 0.75, r * 1.0)], [0.05, r * 0.32, 0.05]), q[0], q[1], ang)
            out.append((arc, lip))
        row += 1
        i += max(2, int(every * (0.55 + 0.45 * w / 13) / 0.7))
    return out


def body_part(fig, P):
    keys = body_keys(P)
    c, ws = smooth_path(keys, step=0.7)
    poly = tube_poly(c, ws).buffer(2.2, join_style=1).buffer(-2.2, join_style=1)     # creux arrondis (aucune encoche)
    shape = shape_poly(poly, step=1.0)
    nb = normals(c)
    n = len(c)
    det = []
    # le volume : le dos rond éclairé (une bande claire décalée vers la lumière)
    L = (0.6, -0.8)
    lit_c, lit_w = [], []
    for i in range(n):
        nx, ny = nb[i]
        d = nx * L[0] + ny * L[1]
        off = (0.15 + 0.3 * d) * ws[i] / 2
        lit_c.append((c[i][0] + nx * off, c[i][1] + ny * off))
        lit_w.append(ws[i] * 0.22)
    lit = tube_poly(lit_c[8:-14], lit_w[8:-14]).intersection(poly)
    det.append((shape_poly(lit.buffer(0.7).intersection(poly), step=1.2), SCALE.light, 0.28))
    det.append((shape_poly(lit, step=1.2), SCALE.light, 0.45))
    # le ventre : une bande de plaques jaunes du côté extérieur du virage (dessous, au sol ; dehors, au crochet)
    side = 1
    i0 = 6
    i1 = n - 2
    A, B = [], []
    for i in range(i0, i1 + 1):
        u = min(1.0, (i - i0) / 10.0)
        u = u * u * (3 - 2 * u)
        f0, f1 = 1.2, 1.2 - (1.2 - 0.38) * u
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        A.append((p[0] + side * nx * w / 2 * f0, p[1] + side * ny * w / 2 * f0))
        B.append((p[0] + side * nx * w / 2 * f1, p[1] + side * ny * w / 2 * f1))
    from shapely.geometry import Polygon
    bpoly = Polygon(A + B[::-1]).buffer(0).intersection(poly)
    belly = shape_poly(bpoly, step=0.8)
    det.append((belly, ('lin', 70, 104, 24, 116, [(0, BELLY.light), (0.5, BELLY.base), (1, BELLY.shadow)]), 1))
    # les plaques : de petits traits doux en travers de la bande
    for i in range(i0 + 8, i1 - 3, 6):
        p, w, (nx, ny) = c[i], ws[i], nb[i]
        a = (p[0] + side * nx * w / 2 * 1.25, p[1] + side * ny * w / 2 * 1.25)
        b = (p[0] + side * nx * w / 2 * 0.3, p[1] + side * ny * w / 2 * 0.3)
        det.append((ribbon([a, lerp(a, b, 0.5), b], [0.1, 0.4, 0.1]), BELLY.shadow, 0.45))
    # la limite ventre / écailles : un liseré sombre doux
    det.append((ribbon(B[2:], [0.1] + [0.5] * (len(B) - 4) + [0.1]), SCALE.shadow, 0.5))
    for arc, lip in scale_crescents(c, ws, 12, n - 10, side=side):
        det.append((arc, SCALE.shadow, 0.32))
        det.append((lip, SCALE.light, 0.25))
    fig.part('body', shape, SCALE, grad=(74, 96, 20, 118, [(0, SCALE.light), (0.45, SCALE.base), (1, SCALE.shadow)]),
             cel=1.5, rim=0.7, cast=0, details=det, occl=(SCALE.deep, 0.2, 2.6))
    return c, ws


# ======================================================================== les manches
def sleeve_geom(S, E, W, hang, cuff=(3.0, 3.4)):
    """Une grande manche de prêtresse d'UNE seule forme : le bras (épaule → coude → poignet) dans un tissu qui s'élargit
    jusqu'au poignet, et la poche de tissu qui PEND sous l'avant-bras (toujours vers le bas : la pesanteur) jusqu'au
    bas de l'ouverture. Rend (forme, haut et bas de l'ouverture, sens de l'avant-bras, point bas de la poche)."""
    u = norm((W[0] - E[0], W[1] - E[1]))
    n_up = (-u[1], u[0]) if -u[1] * 0 + u[0] * 1 < 0 else (u[1], -u[0])
    if n_up[1] > 0:
        n_up = (-n_up[0], -n_up[1])
    nd = (-n_up[0], -n_up[1])
    v = norm((E[0] - S[0], E[1] - S[1]))
    pa, pb = (-v[1], v[0]), (v[1], -v[0])
    inner = pa if pa[0] * u[0] + pa[1] * u[1] > 0 else pb
    outer = (-inner[0], -inner[1])
    ic = norm((inner[0] + n_up[0], inner[1] + n_up[1]))
    # quand l'avant-bras se dresse, la poche pend sous le coude (et moins bas) : le tissu tombe toujours
    hz = min(1.0, abs(u[0]) / 0.62) ** 1.5
    T = add(add(W, n_up, cuff[0]), u, 0.6)
    B = add(add(add(W, nd, cuff[1] * (0.7 + 0.3 * hz)), u, -0.3), (0, 2.6 * hz))
    L = add(lerp(E, W, 0.4 * hz), (-0.6 * hz, 2.5 + (hang - 2.5) * hz))
    oE = add(add(E, outer, 2.5), (0, 1.8))
    mid = lerp(T, B, 0.5)
    pts = [add(S, (0, -2.6)), add(S, inner, 2.7), add(E, ic, 2.7), T, add(mid, u, 1.5), B,
           add(lerp(B, L, 0.45), (0.4, 1.4 * hz)), add(L, (1.3, -0.1)), add(L, (0.0, 0.5)), add(L, (-1.3, -0.5)),
           add(lerp(L, oE, 0.5), (-0.9 * hz, 0.2)), oE,
           add(lerp(S, E, 0.55), outer, 2.9), add(S, outer, 2.7)]
    shape = sm(pts, sharp=(3, 5), t=0.9)
    return shape, (T, B), u, L, hz


def sleeve_part(fig, name, S, E, W, hang, cuff=(3.0, 3.4), cast_on=None):
    shape, (T, B), u, Lw, hz = sleeve_geom(S, E, W, hang, cuff)
    det = []
    # l'ouverture vue de trois quarts : l'intérieur sombre (entre la lèvre de devant, sur le bord, et celle du fond),
    # l'ourlet d'or sur les deux lèvres (il fait le tour de l'ouverture)
    mid = lerp(T, B, 0.5)
    front = curve_pts([T, add(mid, u, 1.5), B], 14)
    backl = curve_pts([T, add(mid, u, -0.9), B], 14)
    det += [(sm(front + backl[::-1][1:-1], sharp=(0, len(front) - 1), t=0.9), LILAC.deep, 0.95),
            (ribbon(backl, [0.1] + [0.75] * 13 + [0.1]), GOLD.shadow, 0.9),
            (ribbon(offset_line(front, 0.0), [0.6] + [2.0] * 13 + [0.6]), GOLD.base, 1),
            (ribbon(offset_line(front, 0.0)[1:8], [0.1, 0.7, 0.8, 0.8, 0.7, 0.5, 0.1]), GOLD.light, 0.9)]
    # le pli doux de la poche (le tissu tombe en un creux), le haut du bras éclairé
    det += [(ribbon([lerp(E, Lw, 0.2), lerp(E, Lw, 0.65), add(lerp(Lw, B, 0.35), (0, -1.0))], [0.2, 1.1, 0.2]), LILAC.shadow, 0.55 * hz),
            (ribbon([lerp(S, E, 0.15), lerp(S, E, 0.6), lerp(E, T, 0.55)], [0.1, 0.9, 0.1]).move(0.9, -0.7), LILAC.hi, 0.3)]
    fig.part(name, shape, LILAC, cel=1.3, rim=0.6, cast=1.1, details=det, cast_on=cast_on)
    return T, B


# ======================================================================== le sceptre (au repos : vertical, poing en FIST0)
def staff_parts(fig, P, M, glow):
    """Tige de bronze, bague d'or, tête de serpent d'or de profil (gueule ouverte, croc, oeil d'émeraude), grosse pierre
    verte sertie sur sa tête, pointe d'or en bas. M : la pose du sceptre (matrice)."""
    x = STAFF_X
    names = []
    shaft = sm([(x - 0.95, 34.0), (x + 0.95, 34.0), (x + 0.9, 89.0), (x - 0.9, 89.0)], sharp=(0, 1, 2, 3), t=0.3)
    det = [(ribbon([(x + 0.35, 36.0), (x + 0.4, 60.0), (x + 0.35, 88.0)], [0.1, 0.5, 0.1]), BRONZE.hi, 0.8)]
    for y in (47.0, 75.0):
        det += [(sm([(x - 2, y - 0.8), (x + 2, y - 0.8), (x + 2, y + 0.8), (x - 2, y + 0.8)], sharp=(0, 1, 2, 3), t=0.2), GOLD.base, 1),
                (sm([(x - 2, y - 0.8), (x + 2, y - 0.8), (x + 2, y - 0.25), (x - 2, y - 0.25)], sharp=(0, 1, 2, 3), t=0.2), GOLD.light, 1)]
    fig.part('shaft', shaft, BRONZE, grad=(x + 1, 40, x - 1, 40, [(0, BRONZE.light), (0.5, BRONZE.base), (1, BRONZE.shadow)]),
             cel=0.5, rim=0.35, cast=0.8, details=det)
    names.append('shaft')
    tip = sm([(x - 1.25, 88.4), (x + 1.25, 88.4), (x + 0.9, 90.6), (x, 94.4), (x - 0.9, 90.6)], sharp=(0, 1, 3), t=0.7)
    fig.part('spike', tip, GOLD, cel=0.5, rim=0.4, cast=0.5,
             details=[(ribbon([(x + 0.3, 88.8), (x + 0.35, 91.0), (x + 0.05, 93.6)], [0.1, 0.4, 0.05]), GOLD.hi, 0.85)])
    names.append('spike')
    # la tête de serpent d'or, de profil vers l'ennemi : le cou monte de la bague en se cambrant, le crâne long et
    # plat, le museau arrondi, la gueule ouverte (mâchoire du bas un peu tombée), un croc qui part de la mâchoire du haut
    head = sm([(x - 2.0, 37.0), (x - 2.2, 33.0), (x - 2.0, 29.6), (x - 0.8, 27.4), (x + 1.6, 26.6), (x + 4.6, 26.9),
               (x + 6.8, 27.7), (x + 7.9, 28.7), (x + 7.8, 29.5), (x + 6.6, 29.9), (x + 1.2, 30.4),
               (x + 6.4, 31.3), (x + 6.8, 31.9), (x + 5.8, 32.5), (x + 2.6, 32.9), (x + 1.4, 34.2), (x + 1.6, 37.0)],
              sharp=(10,), t=0.85)
    hd = []
    mouth = sm([(x + 1.2, 30.4), (x + 6.6, 29.9), (x + 7.6, 29.7), (x + 7.0, 30.8), (x + 6.4, 31.3)], sharp=(0, 4), t=0.8)
    hd += [(mouth, THROAT, 1),
           (sm([(x + 2.6, 30.5), (x + 6.6, 30.3), (x + 6.2, 30.95), (x + 3.0, 30.8)], t=0.9), '#8e2a44', 0.75),
           # le croc d'ivoire : il part de la mâchoire du haut, dans la gueule
           (sm([(x + 5.3, 30.02), (x + 6.1, 29.95), (x + 5.55, 31.15)], sharp=(0, 1, 2), t=0.5), IVORY.light, 1),
           # le dessus du crâne éclairé ; l'arcade au-dessus de l'oeil d'émeraude (vers l'avant de la tête) ; la narine
           (ribbon([(x - 0.6, 28.0), (x + 2.0, 27.2), (x + 5.2, 27.4), (x + 7.2, 28.3)], [0.1, 0.6, 0.5, 0.1]), GOLD.hi, 0.75),
           (ribbon([(x + 2.6, 27.9), (x + 4.0, 27.45), (x + 5.4, 27.8)], [0.1, 0.45, 0.1]), GOLD.shadow, 0.85),
           (ellipse(x + 4.0, 28.65, 0.85, 0.72), EMER.shadow, 1), (ellipse(x + 4.12, 28.55, 0.62, 0.52), EMER.light, 1),
           (ellipse(x + 4.3, 28.35, 0.2, 0.16), '#ffffff', 0.95),
           (ellipse(x + 7.1, 28.35, 0.28, 0.16, 20), GOLD.deep, 0.8),
           # la mâchoire du bas, plus sombre ; le cou : un reflet doux le long de la gorge
           (sm([(x + 1.4, 31.2), (x + 6.4, 31.5), (x + 6.6, 32.0), (x + 5.0, 32.6), (x + 2.4, 32.9)], t=0.9), GOLD.shadow, 0.45),
           (ribbon([(x + 0.8, 33.6), (x + 1.0, 35.2), (x + 0.9, 36.8)], [0.1, 0.6, 0.2]), GOLD.light, 0.7),
           (ribbon([(x - 1.6, 31.0), (x - 1.8, 34.0), (x - 1.4, 36.6)], [0.1, 0.6, 0.2]), GOLD.shadow, 0.5)]
    fig.part('shead', head, GOLD, grad=(x + 6, 26, x - 3, 36, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.7, rim=0.5, cast=0.9, details=hd, cast_on=['shaft'])
    names.append('shead')
    # la bague d'or sous la tête
    ring_ = sm([(x - 2.4, 35.6), (x + 2.4, 35.6), (x + 2.6, 37.8), (x + 1.6, 38.4), (x - 1.6, 38.4), (x - 2.6, 37.8)], sharp=(0, 1), t=0.7)
    fig.part('sring', ring_, GOLD, cel=0.5, rim=0.4, cast=0.7, cast_on=['shaft', 'shead'],
             details=[(ribbon([(x - 2.0, 36.4), (x, 36.6), (x + 2.2, 36.4)], [0.1, 0.45, 0.1]), GOLD.hi, 0.85),
                      (ellipse(x + 0.2, 37.1, 0.75, 0.6), EMER.base, 1), (ellipse(x + 0.4, 36.9, 0.25, 0.2), EMER.hi, 0.9)])
    names.append('sring')
    # la pierre verte sertie sur la tête : un gros cabochon, ses griffes d'or
    gx, gy, gr = x + 1.6, 23.4, 3.1
    g = glow
    gem = ellipse(gx, gy, gr, gr * 1.02)
    gd = [(ellipse(gx - 0.5, gy + 0.6, gr * 0.85, gr * 0.85), STONE.shadow, 0.6),
          (ellipse(gx + 0.5, gy - 0.4, gr * 0.62, gr * 0.6), ('rad', gx + 0.6, gy - 0.6, gr * 0.7, gr * 0.7, [(0, STONE.hi), (0.5, STONE.light), (1, STONE.light, 0)]), 0.9),
          (sm([(gx + 0.4, gy - 2.6), (gx + 2.2, gy - 1.4), (gx + 1.4, gy - 0.9)], t=0.9), '#ffffff', 0.8),
          (ellipse(gx - 1.6, gy + 1.7, 0.6, 0.4, -30), STONE.light, 0.55)]
    if g > 0:
        gd.append((gem, ('rad', gx, gy, gr, gr, [(0, '#ffffff', 0.9 * g), (0.5, STONE.light, 0.7 * g), (1, STONE.base, 0.2 * g)]), 1))
    fig.part('gem', gem, STONE, grad=(gx + gr, gy - gr, gx - gr, gy + gr, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]),
             cel=0.9, rim=0.55, cast=0.8, details=gd, cast_on=['shead'])
    names.append('gem')
    # la sertissure : une coupe d'or basse posée sur le crâne, deux petites griffes qui tiennent la pierre
    setting = union(sm([(gx - 3.0, gy + 2.0), (gx - 1.2, gy + 2.9), (gx + 1.2, gy + 2.9), (gx + 3.0, gy + 2.0),
                        (gx + 2.4, gy + 3.7), (gx, gy + 4.1), (gx - 2.4, gy + 3.7)], sharp=(0, 3), t=0.9),
                    limb([(gx - 2.6, gy + 2.6), (gx - 3.15, gy + 1.0)], [0.9, 0.55]),
                    limb([(gx + 2.6, gy + 2.6), (gx + 3.15, gy + 1.0)], [0.9, 0.55]), step=0.25, smooth=0.3)
    fig.part('setting', setting, GOLD, cel=0.4, rim=0.35, cast=0.6, cast_on=['gem', 'shead'],
             details=[(ribbon([(gx - 2.0, gy + 3.1), (gx, gy + 3.6), (gx + 2.2, gy + 3.0)], [0.1, 0.4, 0.1]), GOLD.hi, 0.8)])
    names.append('setting')
    fig.pose(names, M)
    return names, mapp(M, (gx, gy))


def fist_part(fig, F, ang):
    """Le poing lointain serré sur la tige : le dos des doigts devant la tige, le pouce par-dessus (repère du poing
    tourné de `ang` avec le sceptre)."""
    def T(p):
        r = rot(p, ang)
        return (F[0] + r[0], F[1] + r[1])
    body = sm([T(p) for p in [(-3.0, -2.6), (0.6, -3.4), (2.8, -2.4), (3.0, 1.0), (2.2, 3.4), (-0.6, 3.8), (-2.8, 2.6),
                              (-4.2, 1.2), (-4.6, -1.0)]], t=0.95)
    det = [(ellipse(*T((1.4, -1.2)), 1.2, 2.0, ang - 8), SKIN.hi, 0.3)]
    for y0, y1 in ((-1.9, -0.3), (-0.3, 1.3), (1.3, 2.9)):
        det += [(ribbon([T((-2.4, y1)), T((-0.2, y1 + 0.2)), T((2.2, y1 - 0.1))], [0.1, 0.45, 0.1]), SKIN.shadow, 0.6),
                (ellipse(*T((0.2, (y0 + y1) / 2 - 0.2)), 1.3, 0.42, ang), SKIN.hi, 0.3)]
    # les petites griffes d'ivoire au bout des doigts repliés (contre la tige, à gauche)
    for y in (-1.2, 0.4, 2.0):
        det += [(sm([T((-2.0, y - 0.35)), T((-1.2, y - 0.1)), T((-2.1, y + 0.45))], sharp=(1,), t=0.7), IVORY.base, 0.9)]
    fig.part('fist', body, SKIN, grad=(F[0] + 3, F[1] - 3, F[0] - 3, F[1] + 4, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.8, cast_on=['shaft', 'fsleeve'], details=det)
    thumb = limb([T((2.4, -1.8)), T((0.4, -3.0)), T((-1.8, -2.8))], [1.9, 1.7, 1.4])
    fig.part('fthumb', thumb, SKIN, cel=0.4, rim=0.4, cast=0.6, cast_on=['fist', 'shaft'])
    return ['fist', 'fthumb']


# ======================================================================== la main proche, en griffe vers le bas
HANDN = dict(
    W0=WN0,
    palm=[(59.4, 72.6), (61.6, 71.0), (64.2, 71.6), (65.8, 73.8), (65.6, 76.6), (63.6, 77.8), (61.0, 77.4), (59.4, 75.4)],
    fingers=[([(60.4, 76.4), (59.8, 79.6), (60.6, 82.0)], 1.75, -1),
             ([(62.0, 77.2), (62.0, 80.8), (63.0, 83.2)], 1.85, -1),
             ([(63.8, 77.2), (64.6, 80.4), (65.8, 82.4)], 1.75, -1),
             ([(65.2, 76.0), (66.6, 78.6), (67.8, 80.2)], 1.55, -1)],
    thumb=([(65.0, 73.4), (67.2, 74.2), (68.4, 76.2)], 1.8, -1),
)


def hand_geom(Wr, rotd, curl, spec, k=0.86):
    """La géométrie d'une main en griffe (comme Ophira) : paume + doigts + pouce d'UNE seule forme, et les griffes."""
    W0h = spec['W0']

    def T(p):
        r = rot(((p[0] - W0h[0]) * k, (p[1] - W0h[1]) * k), rotd)
        return (Wr[0] + r[0], Wr[1] + r[1])
    palm = sm([T(p) for p in spec['palm']], t=0.9)
    digits, claws, creases = [], [], []
    for pts, w, hook in spec['fingers'] + [spec['thumb']]:
        a, b, c = pts
        d = (c[0] - b[0], c[1] - b[1])
        dc = rot(d, hook * (16 + 30 * curl))
        c2 = (b[0] + dc[0], b[1] + dc[1])
        ap, bp, cp = T(a), T(b), T(c2)
        w = w * k
        digits.append(limb([ap, lerp(ap, bp, 0.5), bp, lerp(bp, cp, 0.5), cp], [w, w * 0.95, w * 0.88, w * 0.8, w * 0.72]))
        u = (cp[0] - bp[0], cp[1] - bp[1])
        L = math.hypot(*u) or 1
        u = (u[0] / L, u[1] / L)
        n = (-u[1] * hook, u[0] * hook)
        base = (cp[0] - u[0] * 0.5, cp[1] - u[1] * 0.5)
        tip = (cp[0] + u[0] * 1.7 + n[0] * 0.8, cp[1] + u[1] * 1.7 + n[1] * 0.8)
        ww = w * 0.36
        claws.append(sm([(base[0] - n[0] * ww - u[0] * 0.2, base[1] - n[1] * ww - u[1] * 0.2),
                         (cp[0] + u[0] * 1.1 - n[0] * 0.2, cp[1] + u[1] * 1.1 - n[1] * 0.2), tip,
                         (cp[0] + u[0] * 0.7 + n[0] * ww, cp[1] + u[1] * 0.7 + n[1] * ww),
                         (base[0] + n[0] * ww, base[1] + n[1] * ww)], sharp=(2,), t=0.85))
        creases.append((ap, bp, cp, w))
    shape = union(palm, *digits, step=0.3, smooth=0.3)
    return shape, claws, creases, T


def hand_part(fig, Wr, rotd, curl):
    shape, claws, creases, T = hand_geom(Wr, rotd, curl, HANDN)
    det = []
    for a, b, c, w in creases:
        det.append((ribbon([lerp(a, b, 0.15), b, lerp(b, c, 0.6)], [0.1, 0.42, 0.1]).move(-w * 0.4, w * 0.15), SKIN.shadow, 0.5))
        det.append((ellipse(b[0] + 0.3, b[1] - 0.2, w * 0.24, w * 0.16), SKIN.hi, 0.3))
    det.append((ellipse(*T((63.4, 73.6)), 1.8, 1.2, rotd + 20), SKIN.hi, 0.3))
    fig.part('nhand', shape, SKIN, grad=(Wr[0] + 6, Wr[1] - 2, Wr[0] - 2, Wr[1] + 10, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.9, rim=0.5, cast=1.0, details=det, cast_on=['robe', 'buckle', 'nsleeve'])
    names = ['nhand']
    for i, cl in enumerate(claws):
        fig.part('nclaw%d' % i, cl, IVORY, cel=0.3, rim=0.3, cast=0.35)
        names.append('nclaw%d' % i)
    return names


# ======================================================================== les petits serpents de la coiffe
# Trois seulement (Méduse en a six). Ils sortent de la coiffe, de derrière le dôme du voile (leurs racines sont
# cachées dessous) : celui de gauche part vers l'arrière, celui du milieu se dresse, celui de droite file vers l'ennemi.
# Repère de la tête (avant son ×1,1). Par serpent : la ligne, le sens de la tête (+1 droite, −1 gauche), l'angle de la
# tête au repos, la taille.
SNAKES = {
    'SA': ([(60.0, 33.6), (57.6, 31.4), (55.4, 30.0), (53.2, 29.6)], -1, 192, 0.56),
    'SB': ([(64.6, 32.4), (63.8, 29.8), (64.0, 27.6), (64.8, 26.2)], 1, -50, 0.58),
    'SC': ([(69.4, 33.4), (70.6, 31.8), (71.6, 31.0), (72.4, 30.8)], 1, -14, 0.54),
}


def snake_head_shapes(gape, k):
    """La tête d'un petit serpent dans son repère (cou à l'origine, museau vers +x, dessus vers −y) (celle d'Ophira)."""
    g = gape

    def lo(p):
        r = rot((p[0] - 3.2, p[1] - 0.6), 14 * g)
        return (r[0] + 3.2, r[1] + 0.6)
    K = lambda pts: [(x * k, y * k) for x, y in pts]  # noqa: E731
    sil = sm(K([(-2.6, -1.4), (0.2, -2.4), (2.6, -3.1), (5.6, -3.3), (8.6, -2.6), (10.9, -1.1), (10.7, -0.2), (8.8, 0.25),
                lo((8.2, 1.0)), lo((9.8, 2.2)), lo((9.2, 3.1)), lo((5.8, 3.3)), lo((2.4, 2.9)), (0.0, 2.3), (-2.6, 1.4)]),
             sharp=(5, 8, 9), t=0.85)
    mouth = sm(K([(3.4, 0.6), (8.8, 0.25), lo((8.2, 1.0)), lo((5.2, 1.4))]), sharp=(1, 2), t=0.8)
    jaw = sm(K([lo((3.0, 1.2)), lo((8.4, 1.5)), lo((9.8, 2.2)), lo((9.2, 3.1)), lo((5.8, 3.3)), lo((2.4, 2.9)), (0.0, 2.3), (-2.0, 1.4)]),
             sharp=(2,), t=0.85)
    top = sm(K([(-0.6, -1.9), (1.4, -2.5), (5.6, -3.0), (8.6, -2.3), (10.2, -1.2), (7.4, -1.6), (4.0, -1.5)]), t=0.85)
    return sil, mouth, jaw, top


def snake_parts(fig, P):
    sn = P['sn'] or {}
    tg = P['tg'] or {}
    gp = P['gape'] or {}
    names = []
    for k_, (pts, face, a0, size) in SNAKES.items():
        dx, dy = sn.get(k_, (0.0, 0.0))
        n = len(pts) - 1
        moved = [(p[0] + dx * (i / n) ** 1.3, p[1] + dy * (i / n) ** 1.3) for i, p in enumerate(pts)]
        line = crpath(moved, n=16)
        ws = [2.5 - 0.6 * (i / 16) for i in range(17)]
        mat = SCALEB if k_ == 'SA' else SCALE
        body = limb(line, ws)
        ta = math.degrees(math.atan2(line[-1][1] - line[-4][1], line[-1][0] - line[-4][0]))
        da = ((a0 - ta + 180) % 360) - 180
        ang = ta + da * 0.75 + dy * 3 * face
        u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        nk = line[-1]
        hx, hy = nk[0] - u[0] * 1.2, nk[1] - u[1] * 1.2

        def H(sh, a=ang, hx=hx, hy=hy, face=face):
            if face > 0:
                return xf(sh, hx, hy, a)
            return xf(sh, hx, hy, a - 180, -1, 1)
        g = gp.get(k_, 0.5)
        K = size
        sil, mouth, jaw, top = snake_head_shapes(g, K)
        xs = [p[0] for p in line]
        ys = [p[1] for p in line]
        gx1, gy1, gx2, gy2 = max(xs) + 4, min(ys) - 4, min(xs) - 2, max(ys) + 3
        bel = band_poly(line, ws, 1.15, 0.42, 0, len(line) - 1, side=-face).intersection(poly_of(body))
        det = [(shape_poly(bel), ('lin', gx1, gy1, gx2, gy2, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1)]
        det += [(H(top), mat.light, 0.7),
                (H(jaw), ('lin', hx, hy - 1, hx, hy + 3, [(0, GOLD.light), (1, GOLD.shadow)]), 1),
                (H(mouth), THROAT, 1)]
        ex_, ey_ = 5.3 * K, -1.45 * K
        det += [(H(ellipse(ex_ - 0.1, ey_ - 0.05, 1.3 * K, 1.1 * K)), mat.deep, 0.85),
                (H(ellipse(ex_, ey_, 1.05 * K, 0.9 * K)), GOLD.light, 1),
                (H(sm([(ex_ + 0.05, ey_ - 0.8 * K), (ex_ + 0.3, ey_), (ex_ + 0.05, ey_ + 0.8 * K), (ex_ - 0.2, ey_)], sharp=(0, 2), t=0.9)), '#1a0c18', 1),
                (H(ellipse(ex_ + 0.45, ey_ - 0.3, 0.24, 0.18)), '#ffffff', 0.95),
                (H(ribbon([(3.7 * K, -2.45 * K), (5.2 * K, -2.75 * K), (6.7 * K, -2.35 * K)], [0.1, 0.45, 0.1])), mat.deep, 0.7)]
        fig.part(k_ + 'b', union(body, H(sil), step=0.3, smooth=0.4), mat,
                 grad=(gx1, gy1, gx2, gy2, [(0, mat.light), (0.55, mat.base), (1, mat.shadow)]),
                 cel=0.8, rim=0.45, cast=0.7, details=det)
        names.append(k_ + 'b')
        t_ = tg.get(k_, 1.0)
        if t_ > 0.05:
            Lg = 0.8 + 1.8 * t_
            base = (8.4 * K, 0.9 * K)
            tip = (base[0] + Lg, base[1] + 0.2 * t_)
            fork = 0.7 + 0.2 * t_
            tsh = union(limb([base, lerp(base, tip, 0.5), tip], [0.62, 0.55, 0.42]),
                        limb([tip, (tip[0] + fork, tip[1] - 0.55)], [0.42, 0.2]),
                        limb([tip, (tip[0] + fork, tip[1] + 0.62)], [0.42, 0.2]), step=0.2)
            fig.part(k_ + 't', H(tsh), Mat(TONGUE[0], TONGUE[0], TONGUE[1], TONGUE[2], TONGUE[2]), cel=0.2, rim=0.15, cast=0.3)
            names.append(k_ + 't')
    return names


# ======================================================================== la tête
# l'oeil en unités de l'oeil (x : sa largeur, du coin intérieur +0,5 vers la tempe −0,5 ; y : la largeur de l'oeil
# proche) : une amande étirée vers la tempe, le haut coupé par la paupière lourde (le regard mi-clos, menaçant)
EYE_SHAPE = [(0.5, 0.02), (0.3, -0.14), (0.0, -0.2), (-0.32, -0.17), (-0.56, -0.06), (-0.3, 0.14), (0.05, 0.17), (0.32, 0.12)]
EYE_LID = [(0.56, 0.02), (0.3, -0.18), (0.0, -0.25), (-0.34, -0.22), (-0.66, -0.1), (-0.34, -0.15), (0.0, -0.15), (0.3, -0.1)]
EYE_LIDTOP = [(0.5, -0.12), (0.2, -0.38), (-0.2, -0.42), (-0.55, -0.26), (-0.2, -0.27), (0.2, -0.24)]
EYE_BROW = [(0.62, -0.42), (0.2, -0.56), (-0.3, -0.66), (-0.74, -0.6), (-0.3, -0.58), (0.2, -0.47)]
EYE_LOW = [(0.38, 0.13), (0.0, 0.21), (-0.36, 0.17)]
EYE_SHUT = [(0.54, 0.0), (0.2, 0.09), (-0.2, 0.1), (-0.6, -0.02)]


def eye_pt(cx, cy, w, side, u, v, W0):
    if side > 0 and u < -0.5:
        u = -0.5 + (u + 0.5) * 0.5
    return (cx - side * u * w if side > 0 else cx + u * w, cy + v * W0)


def head_parts(fig, P):
    """Le visage long et étroit, le voile (avec le diadème), les petits serpents ; rend les noms (posés avec la tête)."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    (exn, eyn, ewn), (exf, eyf, ewf) = FACE_V['oeil_proche'], FACE_V['oeil_fond']
    nx, ny = FACE_V['nez']
    mx, my, mw = FACE_V['bouche']
    cx_, cy_ = FACE_V['menton']
    W0 = ewn

    # ---- les petits serpents (derrière le voile : leurs racines sont cachées sous le dôme) ----
    names += snake_parts(fig, P)

    # ---- le visage ----
    face = sm([(60.2, 36.0), (62.6, 34.6), (65.1, 34.3), (67.6, 34.6), (70.0, 36.0), (71.3, 39.2), (71.7, 42.8),
               (71.3, 46.0), (70.2, 48.6), (68.8, 50.9), (67.4, 52.5), (cx_, 53.25), (65.3, 52.7), (63.6, 51.4),
               (61.6, 49.4), (59.8, 46.6), (58.9, 43.2), (58.7, 39.6)], sharp=(11,), t=0.9)
    fd = []
    # la joue proche et la mâchoire dans l'ombre douce ; le creux sous la pommette (joues creuses) ; le front et la
    # joue lointaine éclairés
    fd += [(sm([(59.4, 44.0), (60.6, 47.6), (62.8, 50.4), (65.6, 52.8), (63.6, 51.4), (61.6, 49.4), (59.8, 46.6), (58.9, 43.2)]), SKIN.shadow, 0.55),
           (sm([(60.0, 46.2), (61.8, 46.0), (63.6, 47.2), (64.4, 49.0), (63.2, 49.6), (61.6, 48.8)], t=0.95), SKIN.shadow, 0.45),
           (sm([(69.2, 46.2), (70.6, 45.6), (70.8, 47.6), (69.8, 49.4)], t=0.95), SKIN.shadow, 0.3),
           (ellipse(exn + 0.2, eyn + 2.0, 1.5, 0.55, -8), SKIN.hi, 0.16),
           (sm([(66.0, 36.2), (70.2, 36.6), (71.2, 39.4), (69.4, 38.8), (66.4, 37.8)]), SKIN.hi, 0.3),
           (sm([(70.6, 41.0), (71.6, 43.0), (71.2, 46.0), (70.6, 44.0)]), SKIN.hi, 0.25)]
    # l'ombre sous le menton
    fd += [(sm([(64.4, 51.6), (cx_, 52.4), (68.2, 51.2), (67.4, 52.5), (cx_, 53.25), (65.3, 52.7)]), SKIN.shadow, 0.45)]
    # les deux yeux : LE MÊME oeil en miroir (coin intérieur vers le nez), celui du fond un peu plus étroit
    fl = P['flare']
    bl = P['blink']
    for (ex, ey, ew), side in (((exn, eyn, ewn), -1), ((exf, eyf, ewf), 1)):
        E = lambda u, v, ex=ex, ey=ey, ew=ew, side=side: eye_pt(ex, ey, ew, side, u, v, W0)  # noqa: E731
        brow = sm([E(*q) for q in EYE_BROW], sharp=(0, 3), t=0.85)
        fd += [(brow, SKIN.deep, 0.95)]
        lidtop = sm([E(*q) for q in EYE_LIDTOP], t=0.9)
        fd += [(lidtop, SKIN.shadow, 0.5)]
        if bl < 0.5:
            eye = sm([E(*q) for q in EYE_SHAPE], sharp=(0, 4), t=0.9)
            c = E(0.05, 0.0)
            fd += [(eye, ('rad', c[0], c[1] + 0.2, ew * 0.62, ew * 0.62, [(0, EYE[0]), (0.35, EYE[1]), (0.75, EYE[2]), (1, EYE[3])]), 1)]
            # la pupille fendue (le regard va vers l'ennemi : un peu vers le coin intérieur pour l'oeil proche)
            pc = E(-0.02 if side < 0 else 0.08, 0.01)
            ph = 0.17 * W0
            fd += [(sm([(pc[0], pc[1] - ph * 1.6), (pc[0] + 0.24, pc[1]), (pc[0], pc[1] + ph * 1.2), (pc[0] - 0.24, pc[1])],
                       sharp=(0, 2), t=0.9), EYE[4], 1)]
            hl = E(-0.18 if side < 0 else 0.22, -0.06)
            fd += [(ellipse(hl[0], hl[1], 0.28, 0.22), '#ffffff', 0.9)]
            # la paupière lourde : elle coupe le haut de l'oeil ; le trait des cils, étiré vers la tempe
            lid = sm([E(*q) for q in EYE_LID], sharp=(0, 4), t=0.9)
            fd += [(lid, ('lin', ex, ey - W0 * 0.3, ex, ey - W0 * 0.1, [(0, SKIN.shadow), (1, SKIN.deep)]), 1),
                   (ribbon([E(0.52, 0.0), E(0.25, -0.16), E(-0.1, -0.17), E(-0.45, -0.1), E(-0.72, -0.04)], [0.1, 0.32, 0.4, 0.34, 0.06]), LASH, 1),
                   (ribbon([E(*q) for q in EYE_LOW], [0.08, 0.2, 0.06]), SKIN.deep, 0.75)]
            if fl > 0:
                ring_ = sm([E(*q) for q in [(0.62, 0.02), (0.3, -0.26), (-0.3, -0.26), (-0.72, -0.06), (-0.3, 0.26), (0.3, 0.24)]], t=0.9)
                fd.insert(0, (ring_, EYE[2], 0.45 * fl))
                fd += [(eye, EYE[0], 0.35 * fl)]
        else:
            fd += [(sm([E(*q) for q in EYE_LID[:5]] + [E(-0.3, 0.06), E(0.05, 0.1), E(0.32, 0.06)], sharp=(0, 4), t=0.9), SKIN.shadow, 0.7),
                   (ribbon([E(*q) for q in EYE_SHUT], [0.1, 0.36, 0.34, 0.06]), LASH, 1)]
    # le nez : fin et un peu long, SUR la médiane, entre les deux yeux ; l'arête éclairée, le flanc proche dans
    # l'ombre, le bout arrondi, deux petites narines
    fd += [(sm([(nx - 0.4, ny - 4.0), (nx - 0.15, ny - 1.6), (nx - 0.35, ny - 0.2), (nx - 1.3, ny + 0.2), (nx - 1.1, ny - 1.8)]), SKIN.shadow, 0.4),
           (ribbon([(nx + 0.05, ny - 4.2), (nx + 0.3, ny - 2.0), (nx + 0.5, ny - 0.7)], [0.1, 0.26, 0.16]), SKIN.hi, 0.5),
           (sm([(nx - 1.4, ny + 0.1), (nx - 0.5, ny + 0.75), (nx + 0.9, ny + 0.7), (nx + 1.3, ny + 0.15), (nx + 0.6, ny + 0.35), (nx - 0.5, ny + 0.35)]), SKIN.shadow, 0.55),
           (ellipse(nx + 0.4, ny - 0.35, 0.4, 0.28, -10), SKIN.hi, 0.6),
           (ellipse(nx - 0.65, ny + 0.2, 0.36, 0.2, 12), SKIN.deep, 0.75),
           (ellipse(nx + 0.85, ny + 0.15, 0.26, 0.16, -12), SKIN.deep, 0.65)]
    # la bouche FERMÉE, centrée sous le nez : un sourire mince et cruel (le coin lointain relevé), lèvres sombres ;
    # la pointe d'un croc part de la lèvre du haut (dans la bouche), côté proche
    s_ = 0.6 + P['smile']
    L, R = mx - 0.53 * mw, mx + 0.47 * mw
    fd += [(sm([(L, my - 0.05 - 0.2 * s_), (mx - 0.9, my - 0.35), (mx, my - 0.45), (mx + 0.8, my - 0.45), (R, my - 0.35 - 0.5 * s_),
                (mx + 0.8, my + 0.25), (mx, my + 0.55), (mx - 0.9, my + 0.4)], sharp=(0, 4), t=0.85), LIPS[1], 1),
           (ribbon([(L - 0.1, my - 0.1 - 0.2 * s_), (mx - 0.9, my + 0.05), (mx, my + 0.05), (mx + 0.8, my - 0.08), (R + 0.2, my - 0.45 - 0.55 * s_)],
                   [0.1, 0.34, 0.36, 0.3, 0.08]), LIPS[0], 1),
           (ellipse(mx + 0.1, my + 0.4, 0.6, 0.15, -6), LIPS[2], 0.7),
           (sm([(mx - 0.95, my + 0.0), (mx - 0.35, my + 0.0), (mx - 0.62, my + 1.05)], sharp=(0, 1, 2), t=0.5), IVORY.light, 1),
           (ribbon([(R - 0.1, my - 0.5 - 0.5 * s_), (R + 0.5, my - 0.95 - 0.55 * s_)], [0.25, 0.05]), SKIN.deep, 0.45),
           (ribbon([(mx - 0.9, my + 1.5), (mx, my + 1.7), (mx + 0.8, my + 1.5)], [0.1, 0.3, 0.1]), SKIN.shadow, 0.3)]
    fig.face = dict(oeil_proche=(exn, eyn, ewn), oeil_fond=(exf, eyf, ewf), nez=(nx, ny), bouche=(mx, my, R - L))
    part('face', face, SKIN, grad=(72, 36, 60, 50, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.0, rim=0.5, cast=1.0, details=fd)

    # ---- le voile posé sur la tête : UNE forme qui couvre le crâne et encadre le visage des deux côtés (côté proche
    # plus large : trois quarts), bordé d'or ; il tombe sur l'épaule proche et derrière le cou ----
    inner = [(70.8, 53.4), (71.5, 47.6), (71.8, 42.0), (71.1, 37.8),
             (68.6, 36.6), (65.6, 36.4), (62.4, 36.8), (59.8, 38.2),
             (59.0, 41.6), (59.1, 46.0), (60.4, 49.8), (62.4, 53.0), (62.9, 56.6)]
    outer = [(56.0, 57.4), (53.4, 51.0), (52.6, 44.0), (53.6, 37.4), (56.6, 32.2), (61.0, 29.2), (66.0, 28.4),
             (70.6, 29.4), (74.0, 32.4), (75.6, 37.2), (75.8, 43.0), (75.2, 49.6), (74.2, 55.6)]
    hood = sm(outer + inner, sharp=(0, len(outer) - 1, len(outer), len(outer) + len(inner) - 1), t=0.9)
    vd = []
    # le volume du tissu : le dôme éclairé, le côté proche dans l'ombre, un pli qui tombe vers l'épaule
    vd += [(ribbon([(56.0, 36.0), (59.6, 31.6), (65.0, 29.8), (70.2, 30.8), (73.6, 34.0)], [0.2, 1.4, 1.8, 1.5, 0.2]), VEIL.light, 0.55),
           (ribbon([(61.6, 31.0), (66.0, 30.2), (69.6, 31.0)], [0.1, 0.5, 0.1]), VEIL.hi, 0.5),
           (ribbon([(56.8, 38.0), (55.8, 46.0), (56.4, 55.0)], [0.2, 1.6, 0.5]), VEIL.shadow, 0.55),
           (ribbon([(73.6, 38.0), (74.0, 46.0), (73.4, 54.0)], [0.2, 1.0, 0.3]), VEIL.light, 0.4)]
    # l'ourlet d'or qui borde l'ouverture du visage (d'un bout à l'autre)
    IN = curve_pts(inner, 40)
    vd += [(ribbon(offset_line(IN, 0.65), [0.3] + [1.15] * 39 + [0.3]), GOLD.base, 1),
           (ribbon(offset_line(IN, 0.85), [0.1] + [0.4] * 39 + [0.1]), GOLD.light, 0.9)]
    # le diadème d'or : une bande qui fait le tour de la tête sur le voile, posée au bord du front
    DT = curve_pts([(51.0, 37.0), (55.0, 35.0), (60.0, 34.2), (66.0, 34.0), (71.0, 34.6), (75.0, 36.0), (77.6, 38.0)], 30)
    DB = curve_pts([(51.6, 39.6), (55.6, 37.6), (60.2, 36.8), (66.0, 36.6), (71.0, 37.0), (75.0, 38.4), (77.4, 40.4)], 30)
    vd += [(curve_band(DT, DB, 0.0, 1.0), ('lin', 74, 34, 56, 40, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), 1),
           (curve_band(DT, DB, 0.0, 0.3), GOLD.hi, 0.7), (curve_band(DT, DB, 0.75, 1.0), GOLD.shadow, 0.8)]
    part('hood', hood, VEIL, grad=(76, 30, 54, 54, [(0, VEIL.light), (0.45, VEIL.base), (1, VEIL.shadow)]),
         cel=1.2, rim=0.6, cast=1.1, details=vd, cast_on=['face'] + [n for n in names if n.startswith('S')])
    # l'émeraude du diadème, sur la médiane du front (une goutte sertie d'or)
    gx = FACE_V['mediane'](36.0)
    em = sm([(gx, 34.6), (gx + 1.35, 35.9), (gx + 0.9, 37.8), (gx, 38.6), (gx - 0.9, 37.8), (gx - 1.35, 35.9)], sharp=(0, 3), t=0.9)
    part('demer', em, GOLD, cel=0.4, rim=0.3, cast=0.6, cast_on=['face', 'hood'],
         details=[(sm([(gx, 35.3), (gx + 0.85, 36.1), (gx + 0.55, 37.4), (gx, 37.9), (gx - 0.55, 37.4), (gx - 0.85, 36.1)], t=0.9), EMER.base, 1),
                  (sm([(gx + 0.1, 35.6), (gx + 0.6, 36.2), (gx + 0.2, 36.6)], t=0.9), EMER.hi, 0.9)])
    return names


def veil_back_part(fig):
    """La traîne du voile, dans le dos (derrière tout le corps), bordée d'or ; repère du haut du corps."""
    vb = sm([(62.0, 34.0), (56.0, 36.4), (53.4, 42.0), (51.6, 50.0), (49.0, 58.6), (46.6, 67.0), (45.2, 75.0),
             (45.6, 81.6), (48.0, 84.6), (51.6, 83.6), (55.6, 78.0), (60.0, 66.0), (64.0, 54.0), (66.0, 42.0)], t=0.9)
    BL = curve_pts([(45.0, 76.0), (45.6, 81.6), (48.0, 84.6), (51.6, 83.6), (55.8, 78.0)], 16)
    BU = [add(p, (0.4, -1.8)) for p in BL]
    det = [(curve_band(BU, BL, 0.0, 1.5), GOLD.base, 1), (curve_band(BU, BL, 0.0, 0.3), GOLD.light, 0.9),
           (ribbon([(50.4, 56.0), (48.2, 66.0), (47.4, 76.0)], [0.2, 1.4, 0.4]), VEIL.shadow, 0.5)]
    fig.part('veilback', vb, VEIL, grad=(60, 40, 44, 84, [(0, VEIL.base), (0.5, VEIL.shadow), (1, VEIL.deep)]),
             cel=1.2, rim=0.4, cast=0, details=det)
    return ['veilback']


# ======================================================================== le collier
CI = [(56.6, 56.0), (60.0, 57.4), (65.6, 58.1), (70.6, 57.4), (74.2, 55.8)]
CO = [(55.8, 57.6), (57.6, 60.6), (61.4, 62.6), (66.0, 63.2), (70.6, 62.2), (73.8, 60.0), (75.0, 57.4)]


def collar_back_part(fig):
    """L'arrière du large collier (il passe derrière le cou : le collier fait le tour)."""
    back = sm([(56.6, 56.4), (58.6, 54.4), (62.6, 53.2), (66.4, 52.9), (70.4, 53.4), (73.8, 55.0), (74.6, 56.6),
               (70.6, 55.6), (66.4, 55.2), (62.4, 55.4), (58.6, 56.4)], sharp=(0, 6), t=0.9)
    fig.part('collarback', back, GOLD, grad=(74, 53, 58, 57, [(0, GOLD.base), (1, GOLD.shadow)]), cel=0.5, rim=0.3, cast=0.6,
             details=[(ribbon([(59.0, 54.8), (66.4, 53.6), (73.0, 55.2)], [0.1, 0.4, 0.1]), GOLD.light, 0.6)])
    return ['collarback']


def collar_front_part(fig):
    """La bande de devant du large collier d'or à perles d'émeraude (posée sur les épaules, sur le bas du voile)."""
    I = curve_pts(CI, 30)
    O = curve_pts(CO[1:-1], 30)
    front = sm(curve_pts(CI, 30)[::3] + [CO[-1]] + curve_pts(CO[1:-1], 30)[::-3] + [CO[0]], t=0.9)
    cd = []
    cd += [(curve_band(I, O, -0.3, 0.16), GOLD.light, 0.9)]
    cd += [(curve_band(I, O, 0.3, 0.72), GOLD.shadow, 0.55)]
    for k in range(2, 30, 3):
        c = lerp(I[k], O[k], 0.5)
        r = 0.95 if 6 <= k <= 24 else 0.75
        cd += [(ellipse(c[0] - 0.1, c[1] + 0.15, r * 1.05, r * 0.95), GOLD.deep, 0.6),
               (ellipse(c[0], c[1], r, r * 0.92), ('lin', c[0] + r, c[1] - r, c[0] - r, c[1] + r, [(0, EMER.light), (0.6, EMER.base), (1, EMER.shadow)]), 1),
               (ellipse(c[0] + 0.3 * r, c[1] - 0.3 * r, 0.3 * r, 0.25 * r), EMER.hi, 0.9)]
    cd += [(curve_band(I, O, 0.8, 1.3), GOLD.shadow, 0.85)]
    fig.part('collar', front, GOLD, grad=(75, 55, 57, 62, [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.9, rim=0.55, cast=1.2, details=cd, occl=(GOLD.deep, 0.15, 2.0))
    return ['collar']


# ======================================================================== le dessin
def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    W = warp_fn(P)
    o = W((65.0, SHO_Y))
    UB = mT(o[0] - 65.0, o[1] - SHO_Y)                       # le haut du corps (épaules, cou, collier, voile)
    hx, hy = P['head']
    HEAD = mchain(UB, mT(hx, hy), mR(P['tilt'], *NECK_P), mS(HK, HK, 66.0, 53.0))
    for f_ in (fx or []):
        if hasattr(f_, 'back'):
            f_.back(fig, P)

    # ---- la traîne du voile (dans le dos) ----
    vb = veil_back_part(fig)
    fig.pose(vb, mchain(UB, mT(hx * 0.5, hy * 0.5)))

    # ---- le corps de serpent au sol ----
    body_part(fig, P)

    # ---- le bras lointain : la manche, le sceptre, le poing ----
    SF = mapp(UB, SF0)
    ax, ay = P['arm']
    F = (FIST0[0] + (o[0] - 65.0) + ax, FIST0[1] + (o[1] - SHO_Y) + ay)
    th = P['stilt']
    WF = add(F, rot((WF0[0] - FIST0[0], WF0[1] - FIST0[1]), th * 0.4))
    EF = ik(SF, WF, LF[0], LF[1], BEND_F)
    sleeve_part(fig, 'fsleeve', SF, EF, WF, 8.0, (2.8, 3.2), cast_on=['veilback', 'body'])
    SM = mchain(mT(F[0] - FIST0[0], F[1] - FIST0[1]), mR(th, FIST0[0], FIST0[1]))
    snames, gem_c = staff_parts(fig, P, SM, P['gem'])

    # ---- la robe ----
    robe_part(fig, P, W)

    # ---- le bras proche : la manche, la main en griffe ----
    SN = mapp(UB, SN0)
    nhx, nhy = P['nhand']
    WN = (WN0[0] + (o[0] - 65.0) * 0.8 + nhx, WN0[1] + (o[1] - SHO_Y) * 0.6 + nhy)
    EN = ik(SN, WN, LN[0], LN[1], BEND_N)
    sleeve_part(fig, 'nsleeve', SN, EN, WN, 11.0, (3.6, 4.0), cast_on=['robe', 'veilback', 'buckle', 'body'])
    fa = math.degrees(math.atan2(WN[1] - EN[1], WN[0] - EN[0]))
    fa0 = math.degrees(math.atan2(WN0[1] - EN0[1], WN0[0] - EN0[0]))
    hand_part(fig, WN, fa - fa0, P['curl'])

    # ---- le collier (arrière), le cou ----
    cb = collar_back_part(fig)
    neck = sm([(63.0, 47.0), (68.8, 47.0), (69.0, 52.4), (69.8, 56.6), (62.4, 56.8), (63.2, 52.2)], t=0.9)
    fig.part('neck', neck, SKIN, grad=(70, 48, 62, 56, [(0, SKIN.base), (1, SKIN.shadow)]), cel=1.0, rim=0.4, cast=0.8,
             details=[(sm([(63.0, 50.4), (66.4, 53.0), (69.2, 51.2), (69.2, 53.4), (66.4, 55.0), (63.0, 53.0)]), SKIN.shadow, 0.5),
                      (ribbon([(67.6, 53.2), (68.4, 55.4)], [0.5, 0.1]), SKIN.hi, 0.3)])

    # ---- la tête ----
    hn = head_parts(fig, P)
    # le collier de devant (posé sur les épaules, il passe sur le bas du voile)
    cf = collar_front_part(fig)

    # ---- le poing lointain sur la tige ----
    fn = fist_part(fig, F, th)

    fig.pose(cb + cf + ['neck'], UB)
    fig.pose(hn, HEAD)
    fig.ctx = dict(P=P, UB=UB, HEAD=HEAD, gem=gem_c, fist=F, SM=SM, th=th, W=W,
                   eyes=[mapp(HEAD, FACE_V['oeil_proche'][:2]), mapp(HEAD, FACE_V['oeil_fond'][:2])],
                   hand=WN, head=mapp(HEAD, (65.0, 42.0)))
    for f_ in (fx or []):
        if hasattr(f_, 'front'):
            f_.front(fig, P)
        elif callable(f_):
            f_(fig, fig.ctx)
    return fig


def face_check():
    """Le contrôle du visage (visage.py) sur les positions RÉELLES du dessin (repère de la tête avant ×1,1)."""
    fig = build()
    return verifier(fig.face, FACE_BOX)


def main():
    """pretresse-serpent.svg (grand) et -petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mon-meduse-sorts.webp (512 px de haut) et mon-meduse-sorts-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('pretresse-serpent', 0.95, 512, ID), ('pretresse-serpent-petit', 1.35, 160, ID + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    print('contrôle du visage :', face_check() or 'aucun défaut')
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
