# Zéphyre (assassins-11, vent, commun, assassin) redessinée en VECTORIEL lisse, dans le style moderne de l'interface
# (refonte des héros du 26/11/2026, même méthode et même échelle que Kael : ../kael/).
#
#   python3 refonte-graphique/ui-moderne/heros/zephyre/zephyre.py   # → images du jeu 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/zephyre.txt) : une kunoichi fine et athlétique, ramassée
# comme un ressort, trois quarts vers la droite. Garde basse de ninja : les deux genoux pliés, la jambe proche en avant
# (cuisse presque à plat, genou vers l'ennemi), la jambe lointaine repliée derrière ; buste penché vers l'ennemi. Bras
# lointain levé, coude plié : le poing serre la branche basse du grand shuriken à quatre branches. Bras proche replié
# devant la poitrine, avant-bras en travers : le kunaï tenu à l'envers (doigts devant le manche, anneau du côté du
# poignet, lame vers l'ennemi). Tenue ajustée bleu nuit (jamais de noir pur), cagoule ronde et masque (on ne voit que la
# fente des yeux), bandeau turquoise noué derrière la tête (deux pans qui pendent), sangle de cuir en diagonale (boucle de
# laiton), poignée du sabre court tressée de turquoise derrière l'épaule (pommeau et garde de laiton), brassards et
# jambières d'acier, bandages turquoise aux poignets, sous les genoux et aux chevilles, plaque d'acier sur le dos de la
# main, ceinture turquoise nouée sur la hanche (deux pans), sacoche de cuir sur la cuisse, tabi et sandales de corde.
#
# Visage : construit avec ../visage.py (boîte FACEBOX) : deux yeux de femme en amande sur la même ligne (l'œil du fond un
# peu plus étroit, jamais coupé), iris turquoise, trait de cils relevé au coin extérieur, sourcils fins qui descendent
# vers le nez ; le cache-cou remonte sur le nez (un léger relief du tissu sur la médiane, entre les yeux), la bouche est
# sous le masque (un pli à peine marqué, à sa place).
# Articulations : chaque bras et chaque jambe est UNE seule forme (outils.bent : aucune couture au coude ni au genou ;
# la jambe et son pied sont fondus) ; brassards, bandages et jambières sont peints DANS le membre (ils en font le tour).
# Coordonnées = pixels du dessin pixel art (le point « sol » (64, 116) est le même ; les semelles posent en y = 117).
# Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mskx, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from outils import bent, crpath, fuse, taper, geom_shapes, rot, lerp, ang_of, ik, sign_for, wrap_band  # noqa: E402
from visage import placer  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ID_JEU = 'assassins-11'
TMP = os.environ.get('ZEPHYRE_TMP', os.path.join(tempfile.gettempdir(), 'zephyre-vecto'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières froides et claires, ombres violettes) ----------
CLOTH = Mat('#a9bcee', '#6478b2', '#3d4a84', '#272b58', '#181838')
TURQ = Mat('#d6fff2', '#5cdcc6', '#21a4a4', '#106478', '#0a3a54')
STEEL = Mat('#f8fafe', '#c4ccdc', '#808aa0', '#494d66', '#25243a', glint='#ffffff')
LEATHER = Mat('#e09c64', '#ae6c40', '#7e4632', '#4e2a2c', '#2c161e')
BRASS = Mat('#fff4b4', '#f6d67a', '#c88e2e', '#7a4818', '#4a2810', glint='#fffbe6')
SKIN = Mat('#fff0dc', '#ffd0a8', '#eba27e', '#b86658', '#74304a')
ROPE = Mat('#f2c88e', '#c68c54', '#96623a', '#5e3a30', '#3a2026')
IRIS = ('#7cf0dc', '#22acb4', '#0e5a76')                 # bas de l'iris (clair), milieu, haut (sombre)
EYE_INK = '#1a1026'                                      # cils
BROW = '#3a1e30'                                         # sourcils
WHITE = '#f6f0f2'
LIGHT = (0.6, -0.8)                                      # la lumière vient d'en haut à droite

GRD = 117.0                     # le sol (dessous des semelles)
FEET = (64.0, 116.0)            # le point « sol » du pixel art
FRAME = (27.0, 1.0, 88.0, 118.0)   # x0, y0, largeur, hauteur (pixels du dessin)

# ---------- le squelette ----------
HIP = (66.0, 86.0)              # le pivot du buste (elle se penche depuis les hanches)
NECK = (74.0, 56.0)             # le pivot de la tête (agrandie ×1,1 autour de ce point)
HSC = 1.1
FS, FE0, FW0 = (85.0, 60.5), (95.4, 58.8), (93.6, 36.6)      # bras lointain levé : épaule, coude, poignet
NS, NE0, NW0 = (57.2, 62.0), (53.2, 75.6), (66.4, 73.6)      # bras proche replié devant la poitrine
FH, FK0, FA0 = (59.5, 87.0), (48.0, 98.6), (47.6, 109.4)     # jambe lointaine (repliée derrière) : hanche, genou, cheville
NH, NK0, NA0 = (66.5, 87.5), (85.8, 91.6), (83.8, 109.6)     # jambe proche (en avant)
FL = (math.dist(FS, FE0), math.dist(FE0, FW0))
NL = (math.dist(NS, NE0), math.dist(NE0, NW0))
FLL = (math.dist(FH, FK0), math.dist(FK0, FA0))
NLL = (math.dist(NH, NK0), math.dist(NK0, NA0))
SG_FA, SG_NA = sign_for(FS, FE0, FW0), sign_for(NS, NE0, NW0)
SG_FL, SG_NL = sign_for(FH, FK0, FA0), sign_for(NH, NK0, NA0)
STAR_LOCAL = (19.9, 3.4)        # le centre du shuriken dans le repère du poing (le long de l'avant-bras, vers la droite)
STAR_R = 11.0

# la boîte de la face (ovale du visage sous la cagoule, sans le crâne) et la place des traits (../visage.py)
FACEBOX = (62.0, 29.5, 88.5, 56.0)
V = placer(FACEBOX, l_oeil=0.24)

REST = dict(breath=0.0, crouch=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, t=0.0, e=0.0, blink=0.0,
            fw=FW0, fbend=0.0, hand=0.0, star=1.0, spin=0.0, nw=(0.0, 0.0), shift=(0.0, 0.0), squint=0.0)
#   breath : souffle 0..1 ; crouch : elle se tasse sur les genoux (0..5) ; lean : elle se penche vers l'ennemi (+) ou
#   recule le buste (−) ; head / tilt : la tête (un seul bloc : tous les traits ensemble) ; t : les pans du bandeau se
#   balancent (−2..2) ; e : les pans de la ceinture ; blink : yeux fermés ; squint : elle plisse les yeux (vise) ;
#   fw : le poignet lointain (repère du buste) ; hand : 0 = poing fermé, 1 = main ouverte (après le lancer) ;
#   star : 1 = le shuriken est dans le poing ; spin : il tourne dans la main (degrés) ; nw : décalage du poing proche ;
#   shift : tout le personnage glisse (décalage).


def MP(M, pts):
    return [mapp(M, p) for p in pts]


def unit(deg):
    a = math.radians(deg)
    return (math.cos(a), math.sin(a))


def lit_normal(A, B):
    """La normale d'un segment tournée vers la lumière."""
    L = math.dist(A, B) or 1
    n = (-(B[1] - A[1]) / L, (B[0] - A[0]) / L)
    if n[0] * LIGHT[0] + n[1] * LIGHT[1] < 0:
        n = (-n[0], -n[1])
    return n


def across(A, B, t, half, mat, stops=None):
    """Un dégradé en travers d'un membre (clair du côté de la lumière) au point t de A→B."""
    n = lit_normal(A, B)
    c = lerp(A, B, t)
    st = stops or [(0, mat.light), (0.5, mat.base), (1, mat.shadow)]
    return ('lin', c[0] + n[0] * half, c[1] + n[1] * half, c[0] - n[0] * half, c[1] - n[1] * half, st)


def streak(A, B, t0, t1, off, w):
    """Un reflet long (le long d'un membre), décalé vers la lumière."""
    n = lit_normal(A, B)
    pts = [lerp(A, B, t0 + (t1 - t0) * k / 4) for k in range(5)]
    pts = [(p[0] + n[0] * off, p[1] + n[1] * off) for p in pts]
    return ribbon(pts, [0.05, w * 0.8, w, w * 0.8, 0.05])


def limb_bands(A, B, specs):
    """Brassards / bandages / jambières peints dans un membre : specs = [(t0, t1, matière, demi-largeur)]."""
    out = []
    for t0, t1, mat, half in specs:
        band = wrap_band(A, B, t0, t1, half + 2.5, bow=0.45)
        out.append((band, across(A, B, (t0 + t1) / 2, half, mat), 1))
        # le bord haut de la bande (vers l'épaule / le genou) pose une ombre douce sur le tissu juste dessous… non :
        # la bande est un peu en relief : une ombre fine sous son bord bas, un liseré clair sur son bord haut
        lo = wrap_band(A, B, t1, t1 + 0.06, half + 2.5, bow=0.45)
        out.append((lo, mat.deep if mat is not CLOTH else CLOTH.deep, 0.35))
        hi = wrap_band(A, B, t0, t0 + 0.035, half + 2.5, bow=0.45)
        out.append((hi, mat.hi, 0.45))
        if mat is STEEL:
            out.append((streak(A, B, t0 + 0.08, t1 - 0.08, half * 0.35, 0.9), STEEL.hi, 0.85))
            out.append((streak(A, B, t0 + 0.1, t1 - 0.12, -half * 0.55, 0.7), STEEL.deep, 0.35))
    return out


# ---------- le grand shuriken (quatre branches égales, deux pans par branche, moyeu percé) ----------

def star_shapes(C, ang, R=STAR_R, squash=1.0):
    """Le contour du shuriken et ses pans. ang = direction de la première branche (degrés). squash < 1 : vu de biais
    (il tourne sur lui-même en vol)."""
    rb = R * 0.31
    tips, inner = [], []
    for k in range(4):
        d = ang + 90 * k
        u = unit(d)
        tips.append((C[0] + u[0] * R, C[1] + u[1] * R * squash))
        v = unit(d + 45)
        inner.append((C[0] + v[0] * rb, C[1] + v[1] * rb * squash))
    pts = []
    for k in range(4):
        pts.append(tips[k])
        # le bord creux entre deux branches
        a, b, m = tips[k], tips[(k + 1) % 4], inner[k]
        pts.append(lerp(a, m, 0.72))
        pts.append(m)
        pts.append(lerp(b, m, 0.72))
    outline = sm(pts, sharp=tuple(range(0, 16, 4)), t=0.55)
    hole = ellipse(C[0], C[1], R * 0.1, R * 0.1 * squash)
    facets = []
    for k in range(4):
        tip = tips[k]
        for side, m in ((1, inner[k]), (-1, inner[k - 1])):
            mid = ((tip[0] + m[0]) / 2 - C[0], (tip[1] + m[1]) / 2 - C[1])
            L = math.hypot(*mid) or 1
            lit = (mid[0] * LIGHT[0] + mid[1] * LIGHT[1]) / L
            col = STEEL.light if lit > 0.35 else (STEEL.base if lit > -0.35 else STEEL.shadow)
            facets.append((sm([C, tip, lerp(tip, m, 0.72), m], sharp=(0, 1, 3), t=0.5), col, 1))
        facets.append((ribbon([lerp(C, tip, 0.18), lerp(C, tip, 0.6), lerp(C, tip, 0.97)], [0.1, 0.42, 0.05]), STEEL.glint, 0.9))
    return outline.hole(hole), facets, hole


def add_star(fig, name, C, ang, R=STAR_R, squash=1.0, cast=0.8):
    outline, facets, hole = star_shapes(C, ang, R, squash)
    hub = ellipse(C[0], C[1], R * 0.25, R * 0.25 * squash)
    det = facets + [(hub, ('rad', C[0] + R * 0.08, C[1] - R * 0.08, R * 0.3, R * 0.3,
                           [(0, STEEL.hi), (0.6, STEEL.light), (1, STEEL.base)]), 1),
                    (ellipse(C[0] - R * 0.03, C[1] + R * 0.04, R * 0.13, R * 0.13 * squash), STEEL.deep, 0.9)]
    return fig.part(name, outline, STEEL, cel=0.5, rim=0.35, cast=cast, details=det)


# ---------- le kunaï (anneau, manche, lame en feuille) ----------

def kunai_shapes(ring_c, tip):
    """Le kunaï le long de l'axe anneau → pointe : l'anneau, le manche, la lame en feuille (pan haut clair, pan bas
    sombre, arête claire)."""
    L = math.dist(ring_c, tip)
    a = ang_of(ring_c, tip)
    u = unit(a)
    nrm = (-u[1], u[0])                  # vers le bas de la lame (côté ombre)

    def P_(s, o):
        return (ring_c[0] + u[0] * s + nrm[0] * o, ring_c[1] + u[1] * s + nrm[1] * o)
    sb = L - 21.5                        # la base de la lame
    blade = sm([P_(sb - 0.4, -0.95), P_(sb + 5.5, -2.05), P_(sb + 13, -1.35), P_(L, 0), P_(sb + 13, 1.35), P_(sb + 5.5, 2.05),
                P_(sb - 0.4, 0.95)], sharp=(3,), t=0.85)
    handle = ribbon([P_(1.2, 0), P_(sb * 0.5, 0), P_(sb + 0.2, 0)], [1.5, 1.6, 1.6])
    ring_ = ellipse(*ring_c, 1.75, 1.75).hole(ellipse(*ring_c, 0.8, 0.8))
    up = sm([P_(sb + 0.3, -0.85), P_(sb + 5.5, -1.85), P_(sb + 13, -1.15), P_(L - 0.4, -0.02), P_(sb + 13, 0.05),
             P_(sb + 5.5, 0.05), P_(sb + 0.3, 0.05)], sharp=(3,), t=0.8)
    ridge = ribbon([P_(sb + 1.2, -0.2), P_(sb + 8, -0.25), P_(L - 1.2, -0.05)], [0.1, 0.45, 0.05])
    edge = ribbon([P_(sb + 4, -1.75), P_(sb + 10, -1.5), P_(L - 1.5, -0.25)], [0.05, 0.3, 0.05])
    return blade, handle, ring_, up, ridge, edge, u, nrm


# ---------- les mains ----------

def fist_local(open_=0.0):
    """Le poing (repère local : x le long de l'avant-bras depuis le poignet, y vers la droite de l'avant-bras).
    Renvoie (contour, détails) en coordonnées locales. Les doigts serrés devant (quatre bourrelets), le pouce par-dessus."""
    if open_ > 0.5:
        # la main ouverte, tranchant vers l'ennemi, doigts serrés (moufle), pouce relevé
        shape = sm([(-0.6, -2.9), (3.6, -3.4), (8.6, -3.0), (11.6, -2.0), (12.4, -0.6), (11.8, 0.9), (8.4, 1.8), (4.6, 2.4),
                    (4.0, 3.6), (2.6, 5.4), (1.0, 5.2), (0.6, 3.0), (-0.6, 2.6)], sharp=(10,), t=0.85)
        det = [(ribbon([(3.8, 0.9), (7.6, 0.5), (11.0, -0.4)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.55),
               (ribbon([(2.6, -1.6), (7.0, -2.2), (10.8, -1.6)], [0.1, 0.55, 0.1]), SKIN.hi, 0.5),
               (ribbon([(1.4, 2.6), (2.2, 3.8), (2.0, 4.8)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.5)]
        return shape, det
    shape = sm([(-0.6, -3.2), (2.6, -4.3), (6.8, -4.4), (9.3, -3.4), (10.2, -0.9), (10.0, 2.0), (8.8, 4.2), (5.4, 4.8),
                (1.8, 4.4), (-0.4, 3.2)], t=0.9)
    det = []
    # les doigts repliés (vus de face) : quatre bourrelets, le bout des doigts dans l'ombre côté paume (y < 0)
    for i in range(4):
        x0 = 1.0 + 2.25 * i
        det.append((ribbon([(x0 + 2.1, -3.6), (x0 + 2.15, -0.6), (x0 + 2.0, 2.6)], [0.05, 0.42, 0.05]), SKIN.shadow, 0.5 if i < 3 else 0))
        det.append((ellipse(x0 + 1.15, -2.9, 0.95, 0.75), SKIN.shadow, 0.35))
        det.append((ellipse(x0 + 1.3, 1.4, 0.75, 1.5), SKIN.hi, 0.28))
    # le pouce, par-dessus (au bout du poing)
    det += [(sm([(6.6, -3.6), (9.2, -3.0), (10.4, -0.6), (9.8, 1.6), (8.6, 1.2), (8.6, -1.2), (7.0, -2.4)], t=0.9), SKIN.light, 0.9),
            (ribbon([(6.8, -2.6), (8.4, -1.6), (9.0, 0.8)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.45)]
    return shape, det


# ---------- le dessin ----------

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    cr = P['crouch']
    sx, sy = P['shift']

    # ---- le squelette : une matrice par groupe de morceaux ----
    BASE = mT(sx, sy)
    PEL = mchain(BASE, mT(P['lean'] * 0.3, cr * 0.85))                     # le bassin descend quand elle se tasse
    U = mchain(PEL, mR(P['lean'] * 1.1, *HIP))                             # le haut du corps (depuis les hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                       # ce qui monte avec la poitrine
    TOR = mchain(U, mS(1 + 0.006 * br, 1 + 0.014 * br, 70, 82))            # le buste se gonfle
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], *NECK), mS(HSC, HSC, *NECK))
    TAILS = mchain(HEAD, mskx(-0.05 * P['t'], 34))                          # les pans du bandeau traînent
    BTAIL = mchain(U, mskx(-0.06 * P['e'], 83))                             # les pans de la ceinture

    # ======================================================================== les pans du bandeau (derrière tout)
    t_ = P['t']
    tail_long = crpath([(55.4, 34.2), (50.0, 36.6), (44.4, 40.2), (40.4, 45.6), (38.6, 51.6), (38.2, 57.6)], 22)
    tail_short = crpath([(55.8, 36.4), (54.2, 40.6), (53.2, 45.4), (52.8, 50.0)], 16)

    def pan(center, w0, w1, cut=0.9):
        # un ruban de largeur presque constante, bout coupé en biais
        sh = taper(center, w0, w1, tip='round', bulge=0.08)
        x0_, y0_, x1_, y1_ = sh.bbox()
        e = center[-1]
        cutter = sm([(e[0] - 6, e[1] - cut - 1.6), (e[0] + 6, e[1] + cut - 1.6), (e[0] + 6, e[1] + 9), (e[0] - 6, e[1] + 9)])
        from outils import P as PG_
        g = PG_(sh).difference(PG_(cutter))
        from outils import geom_shape
        return geom_shape(g, sharp_deg=40) or sh
    tl = pan(tail_long, 3.3, 2.8, 1.4)
    ts = pan(tail_short, 3.0, 2.7, -1.2)
    # la torsion du pan long : l'envers (plus sombre) montré après le tournant
    twist = sm([(41.2, 44.4), (43.6, 42.2), (41.6, 47.4), (39.6, 49.6)], t=0.8)
    fig.part('tailL', tl, TURQ, grad=(50, 34, 38, 58, [(0, TURQ.light), (0.45, TURQ.base), (1, TURQ.shadow)]), cel=0.8, rim=0.5,
             cast=0, details=[(twist, TURQ.shadow, 0.75), (ribbon([(50.6, 35.6), (45.6, 38.4), (42.2, 42.4)], [0.1, 0.5, 0.1]), TURQ.hi, 0.55)])
    fig.part('tailS', ts, TURQ, grad=(56, 36, 52, 50, [(0, TURQ.light), (0.5, TURQ.base), (1, TURQ.shadow)]), cel=0.7, rim=0.45,
             cast=0.7, cast_on=['tailL'])
    knot = sm([(55.0, 31.6), (57.8, 31.2), (59.6, 33.4), (59.2, 36.6), (57.0, 38.0), (54.8, 37.2), (54.0, 34.4)], t=0.95)
    fig.part('knot', knot, TURQ, cel=0.7, rim=0.5, cast=0.8, cast_on=['tailL', 'tailS'],
             details=[(ribbon([(55.6, 34.0), (57.0, 34.6), (58.4, 34.4)], [0.1, 0.45, 0.1]), TURQ.deep, 0.5)])

    # ======================================================================== la poignée du sabre (derrière l'épaule)
    pom, grd = (44.4, 50.0), (55.6, 57.0)
    ga = ang_of(pom, grd)
    grip = ribbon([lerp(pom, grd, 0.05), lerp(pom, grd, 0.5), lerp(pom, grd, 1.0)], [2.6, 2.9, 2.9])
    gdet = []
    for k in range(3):        # la tresse : trois losanges clairs (pas de rayures)
        c = lerp(pom, grd, 0.25 + 0.22 * k)
        gdet.append((xf(sm([(-0.9, 0), (0, -0.7), (0.9, 0), (0, 0.7)], sharp=(0, 1, 2, 3), t=0.6), c[0], c[1], ga), TURQ.light, 0.65))
    fig.part('grip', grip, TURQ, cel=0.6, rim=0.45, cast=0, details=gdet)
    fig.part('tsuba', ellipse(grd[0] - 0.4, grd[1] - 0.2, 1.0, 2.8, ga), BRASS, cel=0.4, rim=0.35, cast=0.5, cast_on=['grip'])
    fig.part('pommel', ellipse(pom[0], pom[1], 1.9, 1.7, ga), BRASS, cel=0.5, rim=0.4, cast=0.5, cast_on=['grip'],
             details=[(ellipse(pom[0] + 0.5, pom[1] - 0.5, 0.55, 0.4), BRASS.glint, 0.9)])
    sword_names = ['grip', 'tsuba', 'pommel']

    # ======================================================================== le bras lointain, levé (derrière le buste)
    S = mapp(UC, FS)
    W_ = mapp(UC, P['fw'])
    E, W = ik(S, W_, FL[0], FL[1], SG_FA)
    if P['fbend']:
        E = (E[0] + P['fbend'] * 0.0, E[1])
    farm = bent(S, E, W, 7.0, 6.4, 5.9, bulge=(0.05, 0.04))
    fdet = [(sm([S, E, W]).move(0, 0), CLOTH.base, 0)]
    fdet = limb_bands(E, W, [(0.16, 0.73, STEEL, 3.1), (0.74, 0.97, TURQ, 3.0)])
    fdet.append((ribbon([lerp(S, E, 0.3), lerp(S, E, 0.75), lerp(E, W, 0.08)], [0.1, 0.6, 0.1]), CLOTH.light, 0.35))
    fig.part('farm', farm, CLOTH, grad=(W[0] + 3, W[1], S[0] - 3, S[1] + 4, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.1, rim=0.55, cast=0, details=fdet)
    fa = ang_of(E, W)
    FIST = mchain(mT(*W), mR(fa))
    if P['star'] > 0.5 and P['hand'] < 0.5:
        C = mapp(FIST, STAR_LOCAL)
        a0 = ang_of(C, mapp(FIST, (8.0, 0.6))) + P['spin']
        add_star(fig, 'star', C, a0)
        star_c, star_a = C, a0
    else:
        star_c, star_a = mapp(FIST, STAR_LOCAL), fa + 180
    fsh, fdt = fist_local(P['hand'])
    fig.part('ffist', fsh.map(lambda p: mapp(FIST, p)), SKIN,
             grad=(*mapp(FIST, (8, 4)), *mapp(FIST, (1, -4)), [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
             cel=0.7, rim=0.5, cast=0.7, cast_on=['farm', 'star'],
             details=[(s.map(lambda p: mapp(FIST, p)), c, o) for s, c, o in fdt])
    far_names = ['farm', 'star', 'ffist']

    # ======================================================================== les jambes (la lointaine, repliée derrière)
    def leg(name, Hb, Kb, A, L, sg, ws, foot, toe_split, strap, sole, plate, front_cast):
        H = mapp(PEL, Hb)
        K, A2 = ik(H, A, L[0], L[1], sg, stretch=1.0)
        shape_leg = bent(H, K, A, *ws, bulge=(0.06, 0.08))
        sh, _ = fuse([shape_leg, foot], smooth=0.5)
        det = []
        # le pantalon ample : l'ombre sous la cuisse, le pli qui retombe derrière le genou
        det.append((ribbon([lerp(H, K, 0.25), lerp(H, K, 0.7), K], [0.1, 1.1, 0.2]), CLOTH.light, 0.25))
        det += limb_bands(K, A, [(0.1, 0.28, TURQ, ws[1] / 2), (0.82, 1.06, TURQ, ws[2] / 2)])
        # la jambière d'acier : sur le devant du tibia (côté ennemi), entre les deux bandages
        n = lit_normal(K, A)
        p0, p1 = lerp(K, A, 0.3), lerp(K, A, 0.8)
        half = ws[2] / 2 + 0.6
        u = ((A[0] - K[0]) / math.dist(K, A), (A[1] - K[1]) / math.dist(K, A))
        side = (abs(u[1]), -u[0] if u[1] > 0 else u[0])
        side = (1.0, 0.0) if True else side
        g_ = sm([(p0[0] - 0.8, p0[1] - 0.2), (p0[0] + half + 1.5, p0[1] - 0.4), (p1[0] + half + 1.5, p1[1] + 0.3),
                 (p1[0] - 0.4, p1[1] + 0.6), (lerp(p0, p1, 0.5)[0] - 1.2, lerp(p0, p1, 0.5)[1])], t=0.8)
        det += [(g_, ('lin', p0[0] + half, p0[1], p0[0] - 1, p0[1], [(0, STEEL.light), (0.6, STEEL.base), (1, STEEL.shadow)]), 1),
                (ribbon([(p0[0] + half * 0.55, p0[1] + 0.6), lerp((p0[0] + half * 0.55, p0[1]), (p1[0] + half * 0.55, p1[1]), 0.5),
                         (p1[0] + half * 0.55, p1[1] - 0.6)], [0.05, 0.7, 0.05]), STEEL.hi, 0.85),
                (ribbon([(p0[0] - 0.5, p0[1] + 0.4), (lerp(p0, p1, 0.5)[0] - 0.9, lerp(p0, p1, 0.5)[1]), (p1[0] - 0.2, p1[1] - 0.2)],
                        [0.05, 0.5, 0.05]), STEEL.deep, 0.45)]
        if plate:
            det += plate(K)
        # le tabi : l'orteil séparé, la lanière de la sandale en diagonale
        det += [(ribbon(toe_split, [0.05, 0.35, 0.05]), CLOTH.deep, 0.75),
                (ribbon(strap, [0.6, 0.7, 0.6]), ROPE.base, 1),
                (ribbon([(x + 0.1, y - 0.25) for x, y in strap], [0.05, 0.3, 0.05]), ROPE.hi, 0.6)]
        fig.part(name, sh, CLOTH, grad=(K[0] + 6, H[1] - 4, A[0] - 6, GRD, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
                 cel=1.2, rim=0.55, cast=front_cast, details=det, occl=(CLOTH.deep, 0.15, 2.4))
        fig.part(name + 'sole', sole, ROPE, cel=0.4, rim=0.35, cast=0.4, cast_on=[name],
                 details=[(ribbon([(sole.bbox()[0] + 1.2, GRD - 1.0), ((sole.bbox()[0] + sole.bbox()[2]) / 2, GRD - 1.1),
                                   (sole.bbox()[2] - 1.2, GRD - 1.0)], [0.05, 0.35, 0.05]), ROPE.shadow, 0.6)])
        return H, K, A

    ffoot = sm([(43.6, 108.0), (49.8, 107.6), (52.6, 110.2), (55.6, 111.8), (57.8, 113.6), (57.6, 115.7), (41.0, 115.7),
                (40.4, 113.0), (41.6, 110.2)], t=0.9)
    fsole = rpoly([(39.6, 115.0), (58.4, 115.0), (58.0, GRD), (39.8, GRD)], 0.8)
    fig_fk = leg('fleg', FH, FK0, FA0, FLL, SG_FL, (10.0, 8.0, 6.0), ffoot,
                 [(54.2, 112.2), (54.9, 113.8), (55.2, 115.2)], [(46.2, 111.2), (50.6, 112.6), (54.0, 113.0)], fsole, None, 0)

    # ======================================================================== les pans de la ceinture (sur la hanche)
    e_ = P['e']
    bt1 = crpath([(52.6, 84.0), (49.4, 88.0), (45.6, 92.6), (42.4, 97.0), (40.6, 100.4)], 18)
    bt2 = crpath([(53.4, 85.0), (51.4, 89.0), (49.0, 93.4), (47.4, 97.6)], 14)
    b1 = taper(bt1, 3.2, 2.8, tip='round', bulge=0.06)
    b2 = taper(bt2, 3.0, 2.7, tip='round', bulge=0.06)
    fig.part('btail1', b1, TURQ, grad=(53, 84, 41, 100, [(0, TURQ.light), (0.5, TURQ.base), (1, TURQ.shadow)]), cel=0.8, rim=0.5,
             cast=0.8, details=[(sm([(44.8, 93.2), (46.6, 91.6), (45.2, 95.6), (43.4, 97.2)], t=0.8), TURQ.shadow, 0.7)])
    fig.part('btail2', b2, TURQ, grad=(54, 85, 47, 98, [(0, TURQ.light), (0.5, TURQ.base), (1, TURQ.shadow)]), cel=0.7, rim=0.5,
             cast=0.9, cast_on=['btail1', 'fleg'])

    # ======================================================================== la jambe proche (en avant)
    nfoot = sm([(79.8, 107.8), (86.0, 107.6), (88.6, 110.0), (91.4, 111.6), (93.6, 113.4), (93.4, 115.7), (76.4, 115.7),
                (75.8, 113.0), (77.4, 110.0)], t=0.9)
    nsole = rpoly([(75.0, 115.0), (94.2, 115.0), (93.8, GRD), (75.2, GRD)], 0.8)

    def knee_plate(K):
        c = (K[0] + 1.4, K[1] - 0.6)
        return [(ellipse(c[0], c[1], 3.0, 3.5, -10), ('rad', c[0] + 1, c[1] - 1.2, 3.6, 3.6,
                                                     [(0, STEEL.hi), (0.45, STEEL.light), (1, STEEL.shadow)]), 1),
                (ribbon([(c[0] - 1.6, c[1] + 2.4), (c[0] - 0.2, c[1] + 3.2), (c[0] + 1.6, c[1] + 2.6)], [0.05, 0.4, 0.05]), STEEL.deep, 0.6)]
    nH, nK, nA = leg('nleg', NH, NK0, NA0, NLL, SG_NL, (10.6, 8.4, 6.2), nfoot,
                     [(90.2, 112.0), (90.9, 113.8), (91.2, 115.2)], [(82.2, 111.2), (86.6, 112.6), (90.0, 113.0)], nsole,
                     knee_plate, 1.0)

    # la sacoche de cuir sur la cuisse (pendue à la ceinture), sa boucle de laiton
    pouch = rpoly([(66.4, 88.6), (73.4, 88.2), (73.8, 96.2), (66.8, 96.6)], 1.6)
    flap = rpoly([(66.0, 88.4), (73.8, 88.0), (74.0, 92.0), (70.0, 93.0), (66.2, 92.2)], 1.2)
    fig.part('pouch', pouch, LEATHER, cel=0.8, rim=0.5, cast=1.0, cast_on=['nleg'],
             details=[(flap, ('lin', 74, 88, 66, 93, [(0, LEATHER.light), (0.6, LEATHER.base), (1, LEATHER.shadow)]), 1),
                      (ribbon([(66.4, 92.4), (70.0, 93.4), (73.8, 92.2)], [0.1, 0.5, 0.1]), LEATHER.deep, 0.55),
                      (ellipse(70.0, 92.2, 1.0, 0.9), BRASS.base, 1), (ellipse(70.3, 91.9, 0.4, 0.3), BRASS.glint, 1)])

    # ======================================================================== le buste (veste croisée, tunique à pans)
    torso = sm([(66.5, 55.0), (61.0, 56.4), (56.6, 58.4), (53.6, 61.8), (52.2, 67.0), (51.9, 73.0), (52.4, 79.0), (51.6, 84.0),
                (51.8, 88.6), (53.6, 91.0), (59.0, 91.4), (65.0, 90.8), (69.4, 89.6), (71.0, 91.2), (76.2, 90.8), (81.6, 89.8),
                (83.4, 86.6), (82.6, 82.0), (82.0, 78.6), (84.6, 72.4), (87.4, 66.0), (88.4, 60.8), (86.6, 57.4), (81.4, 55.4),
                (74.0, 54.6)], sharp=(9, 12, 15), t=0.92)
    td = []
    # les plans : le flanc proche dans l'ombre, la poitrine éclairée en haut à droite, l'ombre sous la poitrine
    td += [(sm([(76.0, 58.0), (84.8, 58.6), (86.6, 63.4), (84.0, 70.0), (79.6, 67.4), (76.6, 62.4)]), CLOTH.light, 0.35),
           (ribbon([(62, 76.2), (70, 77.6), (80.6, 76.6)], [0.2, 1.4, 0.2]), CLOTH.deep, 0.35)]
    # le col : la veste croisée (le pan lointain par-dessus), son liseré clair et l'ombre qu'il pose
    lap = [(79.4, 55.6), (76.6, 60.2), (72.6, 65.2), (68.0, 70.2), (63.4, 75.6)]
    td += [(ribbon([(x - 0.7, y + 1.0) for x, y in lap], [0.2, 1.3, 1.3, 1.1, 0.2]), CLOTH.deep, 0.5),
           (ribbon(lap, [0.1, 0.75, 0.75, 0.7, 0.1]), CLOTH.hi, 0.8),
           (sm([(70.4, 55.2), (79.6, 55.4), (75.8, 59.2), (72.4, 58.4)], t=0.8), CLOTH.deep, 0.75)]
    # la sangle de cuir du sabre : une diagonale de l'épaule proche à la hanche lointaine, boucle de laiton
    strap = [(55.2, 58.2), (61.0, 61.8), (67.6, 66.6), (74.4, 72.6), (82.6, 79.8)]
    td += [(ribbon([(x - 0.4, y + 0.7) for x, y in strap], [2.3] * 5), CLOTH.deep, 0.45),
           (ribbon(strap, [2.3] * 5), ('lin', 60, 58, 62, 64, [(0, LEATHER.light), (1, LEATHER.base)]), 1),
           (ribbon([(x + 0.25, y - 0.6) for x, y in strap], [0.05, 0.5, 0.5, 0.5, 0.05]), LEATHER.hi, 0.55)]
    bk = xf(rpoly([(-1.7, -1.9), (1.7, -1.9), (1.7, 1.9), (-1.7, 1.9)], 0.6), 60.4, 61.4, 33)
    bkh = xf(rpoly([(-0.7, -1.0), (0.7, -1.0), (0.7, 1.0), (-0.7, 1.0)], 0.3), 60.4, 61.4, 33)
    td += [(bk.move(-0.3, 0.5), LEATHER.deep, 0.5), (bk, ('lin', 62, 59.6, 58.8, 63.2, [(0, BRASS.hi), (0.5, BRASS.light), (1, BRASS.base)]), 1),
           (bkh, LEATHER.deep, 0.9)]
    # la ceinture turquoise (elle fait le tour : peinte dans le buste), sa boucle de laiton
    belt = sm([(49.0, 79.6), (60.0, 80.4), (70.0, 80.6), (84.0, 79.4), (84.0, 84.6), (70.0, 85.6), (60.0, 85.4), (49.0, 84.4)],
              sharp=(0, 3, 4, 7), t=0.8)
    td += [(belt.move(-0.4, 0.8), CLOTH.deep, 0.5),
           (belt, ('lin', 0, 79.6, 0, 85.6, [(0, TURQ.light), (0.45, TURQ.base), (1, TURQ.shadow)]), 1),
           (ribbon([(50, 80.4), (60, 81.1), (70, 81.3), (83.6, 80.2)], [0.1, 0.5, 0.5, 0.1]), TURQ.hi, 0.6)]
    bb = rpoly([(69.0, 80.0), (73.2, 79.9), (73.4, 85.2), (69.2, 85.4)], 0.7)
    td += [(bb.move(-0.35, 0.6), TURQ.deep, 0.55), (bb, ('lin', 73, 80, 69, 85, [(0, BRASS.hi), (0.5, BRASS.light), (1, BRASS.base)]), 1),
           (rpoly([(70.3, 81.4), (72.0, 81.3), (72.1, 83.8), (70.4, 83.9)], 0.4), TURQ.shadow, 1)]
    # la tunique sous la ceinture : la fente devant, un pli doux, l'ombre de la ceinture
    td += [(ribbon([(69.6, 85.8), (69.8, 87.8), (69.5, 89.6)], [0.2, 0.6, 0.1]), CLOTH.deep, 0.55),
           (ribbon([(57.6, 86.2), (58.6, 88.6), (59.0, 90.8)], [0.1, 0.5, 0.1]), CLOTH.shadow, 0.45),
           (ribbon([(73.0, 86.0), (77.4, 87.4), (80.8, 88.6)], [0.1, 0.5, 0.1]), CLOTH.light, 0.35)]
    fig.part('torso', torso, CLOTH, grad=(86, 56, 56, 88, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.4, rim=0.6, cast=1.2, details=td, occl=(CLOTH.deep, 0.18, 3.0))

    # le nœud de la ceinture, sur la hanche proche (compact)
    bknot = sm([(49.4, 80.4), (53.0, 79.8), (55.6, 81.6), (55.4, 85.0), (52.8, 86.6), (49.6, 85.8), (48.4, 83.0)], t=0.95)
    fig.part('bknot', bknot, TURQ, cel=0.7, rim=0.5, cast=0.9, cast_on=['torso', 'btail1', 'btail2', 'fleg'],
             details=[(ribbon([(50.0, 82.0), (52.0, 83.2), (54.6, 82.8)], [0.1, 0.5, 0.1]), TURQ.deep, 0.5),
                      (ellipse(53.2, 81.4, 1.0, 0.6, -10), TURQ.hi, 0.55)])

    # ======================================================================== le bras proche, replié devant la poitrine
    nx_, ny_ = P['nw']
    S2 = mapp(UC, NS)
    W2_ = mapp(UC, (NW0[0] + nx_, NW0[1] + ny_))
    E2, W2 = ik(S2, W2_, NL[0], NL[1], SG_NA)
    narm = bent(S2, E2, W2, 7.6, 6.6, 5.8, bulge=(0.06, 0.05))
    ndet = limb_bands(E2, W2, [(0.16, 0.68, STEEL, 2.9), (0.7, 0.98, TURQ, 2.8)])
    # le pli de la manche au creux du coude, le dessus de l'épaule éclairé
    ndet += [(ribbon([lerp(S2, E2, 0.62), lerp(S2, E2, 0.86), lerp(E2, W2, 0.1)], [0.1, 0.6, 0.1]), CLOTH.deep, 0.4),
             (ribbon([lerp(S2, E2, 0.05), lerp(S2, E2, 0.35), lerp(S2, E2, 0.6)], [0.1, 0.9, 0.1]).move(1.4, 0), CLOTH.light, 0.3)]
    fig.part('narm', narm, CLOTH, grad=(S2[0] + 4, S2[1] - 2, E2[0] - 3, E2[1] + 3, [(0, CLOTH.light), (0.55, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.1, rim=0.5, cast=1.2, cast_on=['torso', 'bknot', 'grip', 'tsuba'], details=ndet)

    # ---- le kunaï : l'anneau côté poignet, la lame vers l'ennemi ----
    NF = mchain(UC, mT(nx_, ny_))
    ring_c, tip = mapp(NF, (64.0, 68.6)), mapp(NF, (100.8, 74.4))
    blade, handle, ring_, up, ridge, edge, ku, kn = kunai_shapes(ring_c, tip)
    fig.part('khandle', handle, CLOTH, cel=0.3, rim=0.3, cast=0.4, cast_on=['narm', 'torso'],
             details=[(handle, ('lin', *ring_c, *lerp(ring_c, tip, 0.4), [(0, TURQ.base), (1, TURQ.shadow)]), 1)])
    fig.part('kring', ring_, STEEL, cel=0.35, rim=0.35, cast=0.6, cast_on=['narm', 'torso', 'khandle'],
             details=[(ellipse(ring_c[0] + 0.7, ring_c[1] - 0.8, 0.5, 0.35), STEEL.glint, 0.9)])
    fig.part('blade', blade, STEEL, grad=(tip[0], tip[1] - 2, ring_c[0] + 15, ring_c[1] + 3, [(0, STEEL.shadow), (1, STEEL.deep)]),
             cel=0.25, rim=0, cast=0.7,
             details=[(up, ('lin', tip[0], tip[1] - 2, ring_c[0] + 15, ring_c[1], [(0, STEEL.hi), (0.5, STEEL.light), (1, STEEL.base)]), 1),
                      (ridge, STEEL.glint, 0.95), (edge, '#ffffff', 0.7)])

    # ---- le poing proche (doigts devant le manche), la plaque d'acier sur le dos de la main ----
    nf = sm([(66.4, 69.8), (69.0, 67.6), (74.0, 67.2), (78.4, 68.2), (79.6, 70.8), (79.2, 74.0), (76.6, 75.8), (71.6, 76.0),
             (67.6, 75.4), (65.8, 73.0)], t=0.9)
    nfd = [(ellipse(72.6, 72.6, 6.0, 3.4), ('rad', 76, 70, 7.5, 7.5, [(0, SKIN.light, 0.0), (1, SKIN.shadow, 0.25)]), 1)]
    for i in range(4):            # quatre doigts repliés devant le manche (le bout des doigts en bas, dans l'ombre)
        x0 = 67.6 + 2.8 * i
        nfd.append((ellipse(x0 + 1.35, 73.9, 1.2, 0.8), SKIN.shadow, 0.45))
        nfd.append((ellipse(x0 + 1.6, 71.2, 0.75, 1.5), SKIN.hi, 0.35))
        if i:
            nfd.append((ribbon([(x0, 70.0), (x0 + 0.05, 72.6), (x0 - 0.1, 75.2)], [0.05, 0.42, 0.05]), SKIN.shadow, 0.5))
    plate = sm([(67.4, 69.4), (69.8, 67.0), (74.4, 66.6), (78.6, 67.6), (79.4, 69.4), (74.2, 69.0), (69.6, 69.6)], t=0.85)
    nfd += [(plate.move(-0.3, 0.6), SKIN.deep, 0.4),
            (plate, ('lin', 79, 66.6, 68, 69.8, [(0, STEEL.hi), (0.45, STEEL.light), (1, STEEL.shadow)]), 1)]
    fig.part('nfist', nf.map(lambda p: mapp(NF, p)), SKIN, grad=(*mapp(NF, (79, 67)), *mapp(NF, (66, 76)),
                                                                   [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.9, cast_on=['narm', 'torso', 'khandle', 'kring', 'blade'],
             details=[(s.map(lambda p: mapp(NF, p)) if hasattr(s, 'map') else s, c, o) for s, c, o in nfd])
    near_names = ['narm', 'khandle', 'kring', 'blade', 'nfist']

    # ======================================================================== la tête
    head_names, face = head(fig, P)

    # ---- chaque groupe de morceaux prend sa pose ----
    fig.pose(['tailL', 'tailS'], TAILS)
    fig.pose(['knot'] + head_names, HEAD)
    fig.pose(sword_names, UC)
    fig.pose(['torso', 'bknot'], TOR)
    fig.pose(['btail1', 'btail2'], BTAIL)
    fig.pose(['pouch'], PEL)
    # ce que les effets doivent savoir (repère du dessin)
    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, face=face, wrist=W, elbow=E, fa=fa, star=(star_c, star_a), FIST=FIST,
                   tip=tip, ring=ring_c, chest=mapp(UC, (70, 68)), head=mapp(HEAD, (74, 40)), feet=mapp(BASE, FEET),
                   hip=mapp(PEL, HIP))
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def head(fig, P):
    """La cagoule ronde, le bandeau, la fente des yeux (yeux placés par ../visage.py), le masque qui remonte sur le nez.
    Renvoie (noms des morceaux, mesures réelles des traits pour visage.verifier)."""
    (exN, eyY, ewN), (exF, _, ewF) = V['oeil_proche'], V['oeil_fond']
    nx, ny = V['nez']
    mx, my, mw = V['bouche']
    blink = P['blink'] > 0.5
    sq = P['squint']
    hood = sm([(65.0, 26.4), (72.0, 25.0), (79.6, 26.2), (84.8, 29.6), (87.6, 34.6), (88.6, 40.4), (88.2, 46.0), (86.4, 50.8),
               (82.8, 54.4), (77.8, 56.4), (72.0, 56.8), (66.4, 55.4), (61.6, 52.0), (58.6, 47.0), (57.4, 40.6), (58.4, 33.6),
               (61.0, 29.0)], t=0.95)
    hd = []
    # les plans de la cagoule : le crâne éclairé en haut à droite, la nuque et le côté proche dans l'ombre, le dessous
    # de la mâchoire (le masque) plus sombre
    hd += [(sm([(68.0, 26.8), (76.0, 25.6), (82.6, 27.8), (86.0, 31.6), (82.4, 31.0), (75.6, 29.0), (69.6, 28.8)], t=0.9), CLOTH.light, 0.5),
           (sm([(57.0, 38.0), (60.4, 37.4), (62.4, 44.6), (64.6, 50.6), (68.6, 55.6), (63.0, 54.8), (58.6, 48.6)], t=0.9), CLOTH.shadow, 0.55),
           (sm([(64.6, 52.2), (72.0, 54.0), (78.6, 53.4), (84.6, 50.6), (82.4, 54.6), (77.6, 57.2), (70.6, 57.4), (65.4, 55.6)], t=0.9), CLOTH.deep, 0.45)]
    # le bandeau turquoise : il suit la courbe du crâne, d'un bord à l'autre (peint dans la cagoule)
    band_top = [(56.0, 32.6), (62.0, 32.2), (70.0, 32.4), (78.0, 32.2), (84.0, 31.6), (90.0, 30.8)]
    band_bot = [(90.0, 36.8), (84.0, 37.3), (78.0, 37.6), (70.0, 37.7), (62.0, 37.4), (56.0, 37.6)]
    band = sm(band_top + band_bot, sharp=(0, 5, 6, 11), t=0.8)
    hd += [(band.move(-0.4, 0.9), CLOTH.deep, 0.55),
           (band, ('lin', 0, 31, 0, 37.8, [(0, TURQ.light), (0.5, TURQ.base), (1, TURQ.shadow)]), 1),
           (ribbon([(60, 32.9), (70, 33.0), (78, 32.8), (86.6, 32.0)], [0.1, 0.6, 0.6, 0.1]), TURQ.hi, 0.7),
           (sm([(56.0, 32.6), (61.6, 32.2), (63.0, 37.4), (56.0, 37.6)]), TURQ.deep, 0.35)]
    # la fente des yeux : la peau, sous le bandeau ; elle s'arrête avant le bord du visage (la cagoule fait le tour)
    slit = sm([(65.6, 39.6), (68.0, 38.4), (74.0, 38.2), (80.0, 38.3), (85.4, 38.4), (87.3, 39.8), (87.5, 42.6), (86.6, 45.4),
               (82.6, 46.2), (79.4, 45.4), (75.8, 46.3), (71.0, 46.4), (67.4, 45.6), (65.6, 43.4)], t=0.92)
    hd += [(slit.move(-0.3, 0.5), CLOTH.deep, 0.6),
           (slit, ('lin', 87, 38.4, 66, 46, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]), 1),
           # l'ombre du bord de la cagoule sur le haut de la fente, la tempe proche dans l'ombre
           (Shape(slit.subs + slit.move(0.0, 1.25).subs, evenodd=True), SKIN.shadow, 0.55),
           (sm([(65.0, 39.0), (67.8, 38.6), (68.6, 42.6), (67.6, 46.4), (65.0, 45.0)], t=0.9), SKIN.shadow, 0.45),
           (ellipse(83.6, 44.6, 2.0, 0.9), SKIN.light, 0.35)]
    # les sourcils fins, qui descendent vers le nez (regard décidé) ; même dessin, celui du fond plus court
    by = 0.35 * sq

    def brow(ex, ew, inner_right):
        s = 1 if inner_right else -1
        k = ew / ewN
        rel = [(-3.3, -2.9), (-1.0, -3.55), (1.6, -3.3), (3.4, -2.45 + by), (1.6, -2.75), (-1.0, -3.0)]
        return sm([(ex + s * a * k, eyY + b) for a, b in rel], sharp=(0, 3), t=0.85)
    hd += [(brow(exN, ewN, True), BROW, 1), (brow(exF, ewF, False), BROW, 1)]

    # les yeux en amande : même dessin, même ligne, même regard (vers l'ennemi) ; l'œil du fond un peu plus étroit
    def eye_pts(ex, ew, inner_right):
        s = 1 if inner_right else -1
        hw = ew / 2
        rel = [(-hw, -0.25), (-hw * 0.42, -1.5 + 0.35 * sq), (hw * 0.45, -1.4 + 0.4 * sq), (hw, 0.15), (hw * 0.38, 1.2 - 0.15 * sq),
               (-hw * 0.46, 1.05 - 0.1 * sq)]
        return [(ex + s * a, eyY + b) for a, b in rel]
    for ex, ew, inner_right in ((exN, ewN, True), (exF, ewF, False)):
        al = eye_pts(ex, ew, inner_right)
        s = 1 if inner_right else -1
        e = sm(al, sharp=(0, 3), t=0.9)
        outer = al[0]
        flick = (outer[0] - s * 1.1, outer[1] - 1.05)
        if blink:
            hd += [(ribbon([flick, lerp(al[0], al[5], 0.5), (ex, eyY + 0.95), lerp(al[3], al[4], 0.5), al[3]],
                           [0.1, 0.55, 0.6, 0.4, 0.15]), EYE_INK, 0.95),
                   (ribbon([lerp(al[0], al[1], 0.6), (ex, eyY - 0.6), lerp(al[2], al[3], 0.4)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.45)]
            continue
        ix, iy, ir = ex + 0.14 * ew + (0.1 if inner_right else 0.25), eyY + 0.05, 1.42 * (ew / ewN) ** 0.25
        cid = fig.uid('ey')
        x0_, y0_, x1_, y1_ = e.bbox()
        pup = ellipse(ix + 0.08, iy + 0.05, ir * 0.42, ir * 0.5)
        lid = sm([(x0_ - 1, y0_ - 1), (x1_ + 1, y0_ - 1), (x1_ + 1, y0_ + 0.9), (x0_ - 1, y0_ + 1.2)])
        hd += [(e.scale(1.1, 1.3, ex, eyY), SKIN.shadow, 0.4),
               (e, ('lin', 0, y0_, 0, y1_, [(0, '#c8bccc'), (0.45, WHITE), (1, '#ffffff')]), 1),
               ('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><path d="%s" fill="FILL"/>'
                '<path d="%s" fill="#120c1c"/><path d="%s" fill="#1a1440" opacity="0.35"/></g>' % (
                    cid, e.d(), cid, ellipse(ix, iy, ir, ir * 1.06).d(), pup.d(), lid.d()),
                ('lin', 0, iy - ir, 0, iy + ir, [(0, IRIS[2]), (0.5, IRIS[1]), (1, IRIS[0])]), 1),
               (ellipse(ix + ir * 0.38, iy - ir * 0.38, ir * 0.3, ir * 0.27), '#ffffff', 1),
               (ellipse(ix - ir * 0.4, iy + ir * 0.45, ir * 0.13, ir * 0.12), '#ffffff', 0.65)]
        # le trait de cils, épais, relevé au coin extérieur ; le trait du bas, fin
        top = [flick, lerp(al[0], al[1], 0.4), al[1], al[2], al[3]]
        hd += [(ribbon(top, [0.1, 0.75, 0.8, 0.6, 0.18]).move(0, -0.1), EYE_INK, 1),
               (ribbon([lerp(al[0], al[5], 0.4), al[5], al[4], lerp(al[4], al[3], 0.6)], [0.05, 0.22, 0.2, 0.05]), EYE_INK, 0.5)]
    # la racine du nez entre les yeux (une ombre douce où elle entre sous le masque, rien de dessiné en peau)
    rx_ = V['mediane'](eyY)
    hd += [(ribbon([(rx_ - 0.5, eyY - 0.6), (rx_ - 0.7, eyY + 1.2), (rx_ - 0.6, eyY + 2.8)], [0.1, 0.9, 0.5]), SKIN.shadow, 0.4),
           (ribbon([(rx_ + 0.4, eyY - 0.4), (rx_ + 0.5, eyY + 1.4), (rx_ + 0.5, eyY + 2.8)], [0.05, 0.45, 0.2]), SKIN.hi, 0.45)]
    # le masque (cache-cou) qui remonte sur le nez : son bord épais sur la fente, le léger relief du nez sur la médiane
    mask_edge = [(64.8, 45.2), (70.0, 46.6), (75.0, 46.6), (rx_ - 0.6, 45.9), (rx_ + 0.4, 45.5), (83.0, 46.4), (87.6, 45.4)]
    hd += [(ribbon([(x, y + 0.6) for x, y in mask_edge], [0.3, 1.2, 1.2, 1.2, 1.2, 1.2, 0.3]), CLOTH.deep, 0.35),
           (ribbon(mask_edge, [0.2, 0.7, 0.7, 0.7, 0.7, 0.6, 0.2]), CLOTH.light, 0.75),
           # le nez sous le tissu : l'arête éclairée (lumière en haut à droite), le flanc proche dans l'ombre, le bout
           (ribbon([(rx_ + 0.2, 46.4), (nx + 0.1, ny - 0.4), (nx + 0.2, ny + 0.6)], [0.1, 0.7, 0.3]), CLOTH.light, 0.45),
           (sm([(rx_ - 0.6, 46.4), (nx - 0.6, ny - 0.8), (nx - 0.2, ny + 1.0), (nx - 2.4, ny + 1.4), (nx - 2.6, ny)], t=0.9),
            CLOTH.shadow, 0.35),
           (ellipse(nx - 0.1, ny + 1.3, 1.8, 0.5), CLOTH.deep, 0.35),
           # la bouche, sous le masque : un pli à peine marqué, à sa place (centrée sous le nez)
           (ribbon([(mx - mw * 0.4, my + 0.1), (mx, my + 0.25), (mx + mw * 0.4, my)], [0.05, 0.35, 0.05]), CLOTH.deep, 0.35),
           # la joue proche, ronde, sous le tissu ; le menton sur la médiane
           (ellipse(70.0, 50.0, 3.6, 2.4), CLOTH.light, 0.13),
           (ellipse(V['menton'][0], V['menton'][1] - 1.6, 2.6, 0.8), CLOTH.light, 0.18)]
    fig.part('hood', hood, CLOTH, grad=(86, 27, 60, 54, [(0, CLOTH.light), (0.5, CLOTH.base), (1, CLOTH.shadow)]),
             cel=1.3, rim=0.6, cast=1.3, cast_on=['torso', 'farm', 'narm', 'grip', 'tsuba', 'pommel', 'knot', 'tailS', 'tailL'],
             details=hd)
    mesures = {'oeil_proche': (exN, eyY, ewN), 'oeil_fond': (exF, eyY, ewF), 'nez': (nx, ny), 'bouche': (mx, my, mw)}
    return ['hood'], mesures


def main():
    """Les images du jeu : public/art/vecto/assassins-11.webp (512 px de haut) et assassins-11-160.webp (160 px de haut)
    (contour plus épais pour les petites cases). Les dessins SVG intermédiaires vont dans un dossier temporaire."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for name, ow, h, out in (('zephyre', 0.95, 512, ID_JEU), ('zephyre-petit', 1.35, 160, ID_JEU + '-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(TMP, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(TMP, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =',
          [round(w), round(h), round(FEET[0] - x0), round(FEET[1] - y0)])


if __name__ == '__main__':
    main()
