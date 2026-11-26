# Ysolde (knights-7, feu, soutien, rare) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (même
# outil, même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/ysolde/ysolde.py     # → ysolde.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/ysolde.txt) : la danseuse du feu, joyeuse et féroce.
# Athlétique et vive : épaules rondes, taille fine, ventre nu, longues jambes musclées, pieds nus. Trois quarts vers la
# droite, en pleine danse, en équilibre sur la jambe droite (proche), le pied à plat ; le genou gauche (lointain) monté
# à hauteur de hanche, le tibia qui pend, le pied pointé. Bras gauche (lointain) levé en équerre : le haut du bras part
# derrière le buste, l'avant-bras monte droit, le poing (pouce par-dessus, doigts devant le manche, phalanges à
# droite) serre une torche au-dessus de la tête, jamais devant le visage ; le manche ressort dessous avec un embout
# d'or ; la flamme (une seule forme à trois langues, penchée vers l'arrière, cœur clair) dans une coupe d'or. Bras
# droit (proche) tendu vers l'arrière, gracieux : main ouverte, doigts en éventail, index relevé, pouce dessous.
# Visage de femme à la peau sombre : front dégagé, cheveux tirés en arrière, sourcils épais qui descendent vers le nez
# (regard féroce), grands yeux en amande à l'iris ambre, grand sourire aux dents visibles, lèvres baies ; oreille à
# l'anneau d'or. La grande crinière noir bleuté vole loin vers la gauche en cinq mèches ondulées (reflets lavande,
# trois bagues d'or), une longue mèche descend dans le dos ; deux plumes (rouge, orange) nouées d'une perle d'or
# derrière l'oreille. Collier de perles d'or à goutte de cornaline ; haut rouge en cœur ourlé d'or ; ceinture d'or
# basse à trois médaillons ; jupe rouge : pan avant tendu sur la cuisse levée, long pan arrière qui vole à gauche,
# ourlet d'or à gouttes ; deux bracelets d'or à chaque poignet, un anneau d'or à chaque cheville.
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (64, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Figure, Mat, sm, lock, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp, ID  # noqa: E402
from lib import Shape, ring  # noqa: E402
from outils import (rot, unit, add, sub, lerp, norm, ang_of, ik, crpath, taper, under, almond_pt, union,  # noqa: E402
                    limb_u, limb_geom, ell_geom, shape_of, shapes_of, several, inter, poly_of)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#f2b27a', '#c9814c', '#9a5434', '#6a2f36', '#3c1630', glint='#ffd8a8')
HAIR = Mat('#9a8cc4', '#5a4e7c', '#3b3256', '#282240', '#19142a', glint='#c8bce8')
RED = Mat('#ff9a5c', '#e8482e', '#b42430', '#761634', '#440c28')
GOLD = Mat('#fff6c0', '#ffd04a', '#e8a032', '#a65a24', '#5c2418', glint='#fffbe8')
WOOD = Mat('#c88a56', '#9a6038', '#6e3c24', '#4a2420', '#2e1418')
FLAME = Mat('#ffe9a0', '#ffc23a', '#ff8424', '#d8361a', '#8e1c12')
FEATR = Mat('#ff9a6a', '#ee5a3a', '#c42c2e', '#801a34', '#4a0e26')       # la plume rouge
FEATO = Mat('#ffd890', '#ffa63e', '#f07a26', '#b0461e', '#6a2416')       # la plume orange
CARN = Mat('#ffb08a', '#f0603a', '#c42a22', '#7e1420', '#46081c')        # la cornaline
LAVA = ['#fffbe4', '#ffe68a', '#ffb43a', '#f2701a', '#cc3a12', '#8a1a10']
LIPS = ('#4a0c1c', '#8e2a3a', '#b84a4c', '#e07a76')
BROW = '#211a34'
LASH = '#170e22'
FINK = '#3a0c18'                     # le contour des flammes (comme la crinière de Kael)

GRD = 116                            # le sol
FEET = (64, 116)                     # le point « pieds » du pixel art (sol: 64 116)
FRAME = (1, -1, 108, 120)            # la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
H0 = (77.0, 48.0)                    # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (buste et épaules montent, la tête suit) ; crouch : elle plie le genou d'appui (0..3) ;
#   hip : les hanches balancent (pixels, + vers la droite) ; lean : le buste se penche en avant (+) depuis la taille ;
#   head / tilt : la tête (décalage, rotation) ; ph : phase de la crinière (elle ondule sans arrêt) ; hw : amplitude
#   de la vague ; trail : la crinière file vers l'arrière (vitesse) ; lift : elle se soulève ; pan : le pan arrière de
#   la jupe se balance ; lk : la longue mèche du dos se balance ; foot : la cheville de la jambe levée (le genou suit) ;
#   arm : le poignet lointain (la torche suit, droite dans le poing) ; tang : l'angle de la torche (0 = droite) ;
#   near : le poignet proche ; fl : phase de la flamme ; flare : la flamme enfle ; blink : yeux fermés ;
#   spin : la pirouette (degrés : 0 = de face, 180 = de dos, vue retournée) ; smile : le sourire (0..1).
SF0 = (80.0, 52.6)                   # l'épaule lointaine (derrière le buste)
LUF, LFF = 16.2, 12.6                # bras lointain : bras, avant-bras (jusqu'au poignet)
WF0 = (95.6, 37.4)                   # le poignet lointain, sous le poing
SN0 = (58.2, 55.4)                   # l'épaule proche
LUN, LFN = 11.9, 9.6                 # bras proche
WN0 = (37.6, 59.8)                   # le poignet proche (tendu vers l'arrière)
HN0 = (60.6, 79.0)                   # la hanche proche
KN0 = (57.6, 93.4)                   # le genou proche
AN0 = (57.8, 105.8)                  # la cheville proche (le pied reste à plat au sol)
HF0 = (71.0, 79.0)                   # la hanche lointaine
LTF, LSF = 17.6, 12.4                # cuisse, jambe (lointaine)
AF0 = (90.2, 95.6)                   # la cheville lointaine (la jambe levée)
WAIST = (68.0, 72.0)                 # le pivot du buste

REST = dict(breath=0.0, crouch=0.0, hip=0.0, lean=0.0, head=(0.0, 0.0), tilt=0.0, ph=0.0, hw=1.0, trail=0.0, lift=0.0,
            pan=0.0, lk=0.0, foot=AF0, arm=WF0, bend=1.0, tang=0.0, near=WN0, nbend=-1.0, fl=0.0, flare=0.0,
            blink=0.0, spin=0.0, smile=1.0, glow=0.0, open=0.0)


def LT(m):
    """Une transformation → une fonction point → point."""
    return lambda p: mapp(m, p)


def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = Figure(*frame, ow=ow)
    br = P['breath']
    cr = P['crouch']
    # les hanches : elles descendent quand le genou d'appui plie, et balancent de côté
    HIP = mT(P['hip'] * 0.8, cr * 0.9)
    U = mchain(HIP, mR(P['lean'] * 1.2, *WAIST))                                   # le buste (depuis la taille)
    UC = mchain(U, mT(0, -0.55 * br))                                              # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 68, 66))
    HEADN = mchain(UC, mT(*P['head']), mR(P['tilt'], H0[0], H0[1] - 6))           # la tête (sans agrandissement)
    HEAD = mchain(HEADN, mS(1.1, 1.1, *H0))                                        # la tête, agrandie ×1,1
    fig.M = dict(U=U, UC=UC, TOR=TOR, HEAD=HEAD, HEADN=HEADN, HIP=HIP)

    # ---- lueur de la torche (derrière tout) ----
    SF = mapp(UC, SF0)
    WF = mapp(UC, P['arm'])
    torch = torch_frame(WF, P['tang'])
    fc = torch(0, -16.5)
    fig.glow(fc[0], fc[1], 15 + 4 * P['flare'], 15 + 4 * P['flare'], '#ff8a2a', 0.3 + 0.08 * P['flare'])

    # ---- la crinière : cinq mèches ondulées (de la plus basse à la plus haute), puis la longue mèche du dos ----
    hair_names = mane(fig, P, HEADN)

    # ---- le pan arrière de la jupe, qui vole à gauche (derrière les jambes) ----
    pan_names = back_panel(fig, P, HIP)

    # ---- le bras lointain (gauche), levé en équerre : derrière le buste ----
    EF = ik(SF, WF, LUF, LFF, P['bend'])
    farm = limb_u([SF, EF, WF], [3.6, 3.0, 2.45], bulges=[(*lerp(SF, EF, 0.42), 3.9, 3.2, ang_of(sub(EF, SF))),
                                                          (*lerp(EF, WF, 0.3), 3.25, 2.9, ang_of(sub(WF, EF)))])
    fa = ang_of(sub(WF, EF))
    fdet = [(ribbon([lerp(SF, EF, 0.2), lerp(SF, EF, 0.6), lerp(EF, WF, 0.05), lerp(EF, WF, 0.6)], [0.1, 1.4, 1.1, 0.1]).move(0.6, -1.4), SKIN.light, 0.55),
            (ellipse(*add(EF, (0.4, -0.6)), 1.4, 1.0, fa), SKIN.hi, 0.35)]
    fig.part('farm', farm, SKIN, grad=(EF[0] + 3, EF[1] - 8, SF[0] - 2, SF[1] + 5, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=1.1, rim=0.5, cast=0, details=fdet)
    # ---- la torche : le manche, la flamme, la coupe d'or ; puis le poing et les bracelets ----
    torch_names = torch_parts(fig, P, torch)
    fist_names = fist(fig, torch, WF, ['farm'] + torch_names)
    bracelets(fig, 'fbr', EF, WF, 2.7, ['farm'] + fist_names)

    # ---- la jambe lointaine (gauche), levée : la cuisse sous la jupe, le tibia qui pend, le pied pointé ----
    HF = mapp(HIP, HF0)
    AF = mapp(HIP, P['foot'])
    KF = ik(HF, AF, LTF, LSF, -1)
    far_leg(fig, HF, KF, AF)

    # ---- la jambe proche (droite), d'appui : le pied à plat au sol ----
    HN = mapp(HIP, HN0)
    KN = ik(HN, AN0, math.dist(HN0, KN0), math.dist(KN0, AN0), -1)
    near_leg(fig, HN, KN, AN0)

    # ---- le corps : buste, cou et bras proche d'une seule forme (aucune jointure à l'épaule) ----
    SN = mapp(UC, SN0)
    WN = mapp(UC, P['near'])
    EN = ik(SN, WN, LUN, LFN, P['nbend'])
    body(fig, P, U, UC, TOR, SN, EN, WN, hair_names + pan_names)
    hand_names = hand(fig, P, EN, WN, ['body'] + hair_names + pan_names)
    bracelets(fig, 'nbr', EN, WN, 2.5, ['body'] + hand_names + hair_names)

    # ---- le haut rouge en cœur, le collier, la jupe avant, la ceinture ----
    top(fig, TOR, UC)
    skirt(fig, P, HIP, U, mapp(HIP, HF0), KF)
    belt(fig, U)

    # ---- la tête ----
    head(fig, P, HEAD, HEADN)

    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, HIP=HIP, torch=torch, flame=torch(0, -16.0), tip=torch(-0.6, -27.5),
                   wrist=WF, elbow=EF, head=mapp(HEAD, (80, 36)), chest=mapp(TOR, (68, 60)), waist=mapp(U, (68, 70)),
                   knee=KF, ankle=AF, hand=WN)
    if P['spin']:
        spin_view(fig, P['spin'])
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def spin_view(fig, spin):
    """La pirouette : elle tourne autour de sa jambe d'appui. La figure se resserre (cos de l'angle) et, de dos, elle
    est vue retournée (comme le pixel art) ; la lumière reste en haut à droite (les ombres ne tournent pas)."""
    a = math.radians(spin)
    c = math.cos(a)
    k = math.copysign(max(0.42, abs(c)) ** 0.7, c)
    M = mS(k, 1, 58.0, GRD)
    for p in fig.parts:
        p.M = mchain(M, p.M)
    fig.spin_k = k


# ======================================================================== la crinière
LOCKS = [
    # nom, points de la ligne (racine → pointe, en pixels du dessin, tête non agrandie), largeur à la racine ; des
    # longueurs, des courbures et des pointes toutes différentes (jamais des rayons réguliers)
    ('h4', [(60.0, 36.0), (50.0, 39.6), (40.0, 45.6), (30.0, 47.6), (20.0, 49.0), (12.0, 52.0)], 14.0),
    ('h3b', [(58.0, 33.0), (47.0, 36.0), (37.0, 40.4), (28.0, 41.4), (20.0, 43.8)], 10.5),
    ('h3', [(60.0, 28.6), (49.0, 29.0), (38.0, 33.6), (27.0, 37.2), (17.0, 37.4), (7.0, 36.4)], 14.6),
    ('h2', [(62.0, 21.6), (51.0, 19.6), (40.0, 22.8), (29.0, 26.0), (17.0, 25.8), (5.5, 23.6)], 14.8),
    ('h1', [(68.0, 16.4), (58.0, 12.6), (47.0, 13.0), (37.0, 15.0), (27.0, 13.2), (17.0, 11.4)], 12.6),
]
LONG = ('h5', [(61.5, 42.0), (56.4, 49.6), (53.4, 57.6), (51.6, 64.6), (47.8, 71.6), (41.6, 79.6)], 12.0)
MASS = [(66.0, 14.0), (56.0, 10.8), (44.0, 11.4), (34.0, 13.6), (26.0, 18.6), (21.0, 25.6), (25.0, 31.4), (21.0, 37.4),
        (25.0, 43.6), (33.0, 49.6), (43.0, 54.0), (51.0, 58.0), (57.0, 53.0), (62.0, 44.0), (64.0, 30.0)]
RINGS = {'h2': 0.56, 'h3': 0.5, 'h4': 0.44}


def wave(pts, P, i, amp=1.0, down=False):
    """Une mèche qui vit : la vague court de la racine vers la pointe (phase ph), plus forte vers la pointe ;
    trail : la mèche file à l'horizontale (vitesse) ; lift : elle se soulève."""
    out = []
    n = len(pts) - 1
    ph = P['ph'] - i * 0.7
    A = P['hw'] * amp
    for k, p in enumerate(pts):
        t = k / n
        a, b = (pts[max(0, k - 1)], pts[min(n, k + 1)])
        d = norm(sub(b, a))
        nrm = (-d[1], d[0])
        off = A * 1.25 * t ** 1.3 * math.sin(ph - 2.2 * t)
        q = add(p, nrm, off)
        q = (q[0] - 2.2 * P['trail'] * t ** 1.5, q[1] - (1.6 * P['lift'] + 0.6 * P['trail']) * t ** 1.5 * (0.4 if down else 1))
        out.append(q)
    return out


def mane(fig, P, HEADN):
    """Les mèches de la crinière, chacune une forme effilée qui ondule ; reflets lavande qui suivent la mèche, face du
    dessous dans l'ombre ; une bague d'or sur trois d'entre elles. Posées avec la tête (non agrandie : la longueur
    reste celle du pixel art)."""
    names = []
    M = LT(HEADN)
    # la masse de la chevelure, derrière les mèches (pas de trou entre elles près de la tête)
    ph = P['ph']
    mass = sm([M((x - 0.6 * P['hw'] * math.sin(ph + 0.12 * y) * max(0, (60 - x) / 40) - 1.5 * P['trail'] * max(0, (60 - x) / 40),
                  y - P['lift'] * max(0, (60 - x) / 40))) for x, y in MASS], t=0.9)
    fig.part('hm', mass, HAIR, grad=(*M((62, 12)), *M((26, 50)), [(0, HAIR.base), (0.5, HAIR.shadow), (1, HAIR.deep)]),
             cel=0, rim=0.4, cast=0)
    names.append('hm')
    specs = [LONG] + LOCKS
    for i, (name, pts, w0) in enumerate(specs):
        down = name == 'h5'
        pts = wave(pts, P, i, 0.8 if down else 1.0, down)
        if down:
            sw = P['lk']
            pts = [(x + sw * 1.6 * (k / 4) ** 1.4, y) for k, (x, y) in enumerate(pts)]
        c = crpath([M(p) for p in pts], 40)
        sh = taper(c, w0, 0.25, tip='sharp', tipk=1.7)
        det = [(under(sh, 0.6, -2.4), HAIR.shadow, 0.85),
               (under(sh, 0.4, -1.1), HAIR.deep, 0.55)]
        # les reflets lavande : deux filets qui suivent la mèche, sur son dessus (vers la lumière)
        for off, t0, t1, wr, op in ((-0.26, 0.08, 0.62, 1.3, 0.75), (-0.05, 0.18, 0.82, 0.7, 0.6)):
            seg = c[int(t0 * 40):int(t1 * 40) + 1]
            ws = []
            line = []
            for k, p in enumerate(seg):
                t = (t0 + (t1 - t0) * k / max(1, len(seg) - 1))
                j = min(39, int(t * 40))
                d = norm(sub(c[j + 1], c[j]))
                nrm = (-d[1], d[0])
                if nrm[1] > 0:
                    nrm = (-nrm[0], -nrm[1])
                wl = w0 * (1 - t ** 1.7)
                line.append(add(p, nrm, wl * (0.5 + off) - 0.2))
                ws.append(wr * math.sin(math.pi * k / max(1, len(seg) - 1)) + 0.05)
            det.append((ribbon(line, ws), HAIR.light if op > 0.7 else HAIR.hi, op))
        if name in RINGS:
            t = RINGS[name]
            j = int(t * 40)
            p = c[j]
            d = norm(sub(c[j + 1], c[j - 1]))
            wl = w0 * (1 - t ** 1.7) * 0.6
            a = ang_of(d)
            band = xf(rpoly([(-1.05, -wl), (1.05, -wl), (1.05, wl), (-1.05, wl)], 0.5), p[0], p[1], a)
            det += [(xf(rpoly([(-1.35, -wl - 0.35), (1.35, -wl - 0.35), (1.35, wl + 0.35), (-1.35, wl + 0.35)], 0.6), p[0] - 0.3, p[1] + 0.5, a), HAIR.deep, 0.6),
                    (band, ('lin', p[0] + 1, p[1] - wl, p[0] - 1, p[1] + wl, [(0, GOLD.hi), (0.35, GOLD.light), (0.7, GOLD.base), (1, GOLD.shadow)]), 1),
                    (xf(rpoly([(-0.25, -wl), (0.25, -wl), (0.25, wl), (-0.25, wl)], 0.2), p[0], p[1], a).move(0.3, -0.2), GOLD.hi, 0.8)]
        fig.part(name, sh, HAIR, grad=(c[0][0] + 4, c[0][1] - 8, c[-1][0], c[-1][1] + 6, [(0, HAIR.light), (0.45, HAIR.base), (1, HAIR.shadow)]),
                 cel=0, rim=0.55, cast=1.0, details=det)
        names.append(name)
    return names


# ======================================================================== la jupe
def fringe(pts, n, size=1.0, k0=0.5):
    """Des gouttes d'or espacées le long d'un ourlet (pas de hachures) : chacune une petite larme qui pend."""
    out = []
    c = crpath(pts, 60)
    for i in range(n):
        t = (i + k0) / n
        p = c[int(t * 60)]
        out.append(drop(p[0], p[1] + 0.2, 0.85 * size, 2.3 * size))
    return out


def drop(x, y, r, h):
    """Une goutte d'or qui pend sous un point (x, y)."""
    return sm([(x - 0.35 * r, y), (x + 0.35 * r, y), (x + r, y + h - r), (x, y + h + 0.1), (x - r, y + h - r)], sharp=(0, 1), t=0.95)


def back_panel(fig, P, HIP):
    """Le long pan arrière de la jupe qui vole à gauche : il part sous la ceinture, côté proche, et s'effile en pointe
    vers l'arrière ; ourlet d'or et franges en gouttes d'or espacées. Plis qui partent de la taille."""
    s = P['pan']
    M = LT(HIP)
    sw = lambda p, k: (p[0] - 0.4 * s * k, p[1] - 1.5 * s * k)
    top_ = [(57.5, 71.5), (49.0, 76.0), (38.0, 82.4), (27.0, 88.0), (17.0, 92.6)]
    bot = [(16.4, 95.2), (26.0, 95.0), (37.0, 94.4), (47.0, 93.4), (55.0, 91.0), (58.6, 84.0)]
    T = [M(sw(p, (58 - p[0]) / 41)) for p in top_]
    B = [M(sw(p, (58 - p[0]) / 41)) for p in bot]
    sh = sm(T + B, sharp=(4, 5), t=0.9)
    hem_line = B[:5]
    det = []
    # deux plis larges et doux qui suivent le vent (pas de rayures)
    for line, w, col, op in (([(55.6, 77.0), (46.0, 84.0), (36.0, 90.0), (28.0, 93.0)], 2.4, RED.deep, 0.5),
                             ([(55.0, 74.0), (44.0, 79.6), (32.0, 86.6), (22.0, 91.6)], 1.4, RED.light, 0.4)):
        L_ = [M(sw(p, (58 - p[0]) / 41)) for p in line]
        cc = crpath(L_, 12)
        det.append((ribbon(cc, [0.1] + [w * math.sin(math.pi * i / 12) + 0.1 for i in range(1, 12)] + [0.1]), col, op))
    # l'ourlet d'or, le long du bas
    hem = crpath(hem_line, 40)
    det += [(taper(hem, 2.2, 2.2), GOLD.base, 1), (taper([(x + 0.1, y - 0.5) for x, y in hem], 0.8, 0.8), GOLD.light, 0.95)]
    fig.part('pan', sh, RED, grad=(B[-1][0], T[0][1], T[-1][0], B[0][1] + 2, [(0, RED.base), (0.5, RED.shadow), (1, RED.deep)]),
             cel=1.2, rim=0.6, cast=0, details=det)
    names = ['pan']
    fr = several(fringe(hem_line[::-1], 8, 0.85, 0.45))
    fig.part('panfr', fr, GOLD, grad=(T[0][0], 92, T[-1][0], 99, [(0, GOLD.light), (1, GOLD.shadow)]), cel=0.4, rim=0.3, cast=0.6,
             cast_on=['pan'])
    names.append('panfr')
    return names


def skirt(fig, P, HIP, U, HF, KF):
    """Le pan avant de la jupe, tendu sur la cuisse levée : il part de la ceinture et file jusqu'au genou ; plis qui
    suivent la cuisse ; ourlet d'or et franges en gouttes. Le genou tire l'ourlet (il suit la jambe)."""
    M = LT(HIP)
    # l'ourlet de droite suit le genou ; la gauche reste sur la jambe d'appui
    kx, ky = KF[0] - mapp(HIP, (88.2, 83.0))[0], KF[1] - mapp(HIP, (88.2, 83.0))[1]
    def K(p, w):
        q = M(p)
        return (q[0] + kx * w, q[1] + ky * w)
    pts = [K((55.4, 71.0), 0), K((67.0, 72.2), 0.05), K((79.6, 70.6), 0.2), K((88.0, 75.8), 0.7), K((97.6, 79.8), 1.0),
           K((99.4, 81.6), 1.0), K((92.8, 83.8), 1.0), K((82.0, 86.4), 0.6), K((70.0, 88.4), 0.25), K((60.0, 89.0), 0.05),
           K((53.2, 88.6), 0), K((53.8, 80.0), 0)]
    sh = sm(pts, sharp=(4, 5, 10), t=0.9)
    hem = [pts[10], pts[9], pts[8], pts[7], pts[6], pts[5]]
    det = []
    # l'ombre sous la ceinture, le flanc de la jambe d'appui dans l'ombre
    det += [(sm([K((53, 70), 0), K((80, 69), 0.2), K((80, 73.4), 0.2), K((67, 74.6), 0.05), K((53, 73.6), 0)]), RED.deep, 0.45),
            (sm([K((52.6, 72), 0), K((58.4, 73), 0), K((60.6, 80), 0.02), K((61.6, 89.4), 0.05), K((52.6, 89.4), 0)]), RED.shadow, 0.55)]
    # les plis qui suivent la cuisse (peu nombreux, larges et doux, jamais des rayures) : le grand creux entre les
    # deux jambes, le dessous de la cuisse levée ; une arête claire sur la cuisse
    for pts_, w, col, op in (([((63.0, 74.4), 0.02), ((63.6, 81.0), 0.05), ((64.6, 88.6), 0.1)], 2.6, RED.deep, 0.45),
                             ([((71.0, 75.0), 0.05), ((76.0, 81.6), 0.4), ((79.4, 86.6), 0.6)], 2.0, RED.shadow, 0.6),
                             ([((75.0, 74.0), 0.15), ((82.0, 78.0), 0.5), ((90.4, 82.4), 0.95)], 1.6, RED.light, 0.45)):
        line = [K(p_, k_) for p_, k_ in pts_]
        det.append((ribbon(crpath(line, 10), [0.1] + [w * math.sin(math.pi * i / 10) + 0.1 for i in range(1, 10)] + [0.1]), col, op))
    # le haut de la cuisse levée, éclairé
    det += [(sm([K((78, 74), 0.2), K((90, 77.4), 0.7), K((97, 80.4), 1.0), K((92, 80.2), 0.9), K((82, 77.6), 0.4)]), RED.hi, 0.3)]
    hc = crpath(hem, 50)
    det += [(taper(hc, 2.3, 2.3), GOLD.base, 1), (taper([(x + 0.15, y - 0.55) for x, y in hc], 0.85, 0.85), GOLD.light, 0.95),
            (taper([(x - 0.1, y + 0.6) for x, y in hc], 0.6, 0.6), GOLD.shadow, 0.7)]
    fig.part('skirt', sh, RED, grad=(pts[5][0], pts[2][1] - 2, pts[10][0], pts[10][1] + 2, [(0, RED.light), (0.45, RED.base), (1, RED.shadow)]),
             cel=1.1, rim=0.7, cast=1.2, cast_on=['nleg', 'fleg', 'pan', 'panfr', 'body'], details=det)
    fr = several(fringe(hem, 9, 0.85, 0.5))
    fig.part('skfr', fr, GOLD, grad=(60, 88, 70, 93, [(0, GOLD.light), (1, GOLD.shadow)]), cel=0.4, rim=0.3, cast=0.6,
             cast_on=['nleg', 'fleg', 'pan'])


def belt(fig, U):
    """La ceinture d'or basse, posée sur les hanches (plus basse devant), trois médaillons."""
    M = LT(U)
    I = [M(p) for p in [(54.6, 68.6), (61.0, 69.3), (68.0, 69.5), (74.6, 68.8), (80.4, 67.6)]]
    O = [M(p) for p in [(54.6, 72.2), (61.0, 73.0), (68.0, 73.2), (74.6, 72.4), (80.6, 71.2)]]
    sh = sm(I + O[::-1], sharp=(0, 4, 5, 9), t=0.9)
    det = [(sm(I + [lerp(a, b, 0.32) for a, b in zip(I, O)][::-1], sharp=(0, 4, 5, 9), t=0.9), GOLD.light, 0.9),
           (sm([lerp(a, b, 0.72) for a, b in zip(I, O)] + O[::-1], sharp=(0, 4, 5, 9), t=0.9), GOLD.shadow, 0.7)]
    fig.part('belt', sh, GOLD, cel=0.6, rim=0.5, cast=1.0, details=det)
    names = ['belt']
    for i, (x, y, r) in enumerate(((58.6, 71.6, 1.9), (67.6, 72.2, 2.3), (76.4, 71.2, 2.0))):
        c = M((x, y + 0.3))
        med = ellipse(c[0], c[1], r * 0.92, r)
        fig.part('med%d' % i, med, GOLD, grad=(c[0] + r, c[1] - r, c[0] - r, c[1] + r, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]),
                 cel=0.5, rim=0.4, cast=0.7, cast_on=['belt', 'skirt', 'body'],
                 details=[(ellipse(c[0] + 0.1, c[1] + 0.1, r * 0.5, r * 0.55), CARN.base, 1),
                          (ellipse(c[0] + 0.25, c[1] - 0.05, r * 0.36, r * 0.38), ('rad', c[0] + 0.4, c[1] - 0.3, r * 0.5, r * 0.5, [(0, CARN.hi), (1, CARN.base)]), 1),
                          (ellipse(c[0] + 0.35, c[1] - 0.3, r * 0.13, r * 0.13), '#ffffff', 0.9)])
        names.append('med%d' % i)
    return names


# ======================================================================== les jambes
def near_leg(fig, H, K, A):
    """La jambe d'appui, d'un seul tenant de la hanche au pied (cuisse, genou, mollet qui bombe derrière, cheville
    fine, pied nu à plat, orteils vers la droite), puis l'anneau d'or de la cheville."""
    th = ang_of(sub(K, H))
    sa = ang_of(sub(A, K))
    leg = limb_geom([H, K, A], [5.4, 3.5, 2.5],
                    bulges=[(*add(lerp(H, K, 0.4), (0.2, 0)), 5.6, 4.6, th),                       # la cuisse
                            (*add(lerp(K, A, 0.32), (-1.3, 0.0)), 3.9, 2.9, sa)], smooth=0.8)   # le mollet, derrière
    from shapely.geometry import Polygon
    x, y = A
    # le pied nu à plat : talon rond, plante posée, orteils arrondis vers la droite, cou-de-pied qui descend
    footp = Polygon([(x - 2.2, y - 0.4), (x - 2.5, y + 2.6), (x - 3.4, y + 4.6), (x - 4.6, GRD - 3.0), (x - 4.6, GRD - 1.4),
                     (x - 3.6, GRD), (x + 4.0, GRD), (x + 9.4, GRD), (x + 12.6, GRD - 0.3), (x + 13.2, GRD - 1.4),
                     (x + 12.4, GRD - 2.5), (x + 10.0, GRD - 3.0), (x + 7.4, GRD - 4.0), (x + 5.2, y + 5.0), (x + 3.4, y + 2.8),
                     (x + 2.4, y + 0.6), (x + 2.3, y - 0.8)]).buffer(0.8, join_style=1).buffer(-0.8, join_style=1)
    from shapely.ops import unary_union
    g = unary_union([leg, footp]).buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
    from shapely.geometry import box
    g = g.intersection(box(-50, -50, 200, GRD))
    sh = shape_of(g, step=0.5)
    det = []
    # le genou : la rotule éclairée, le creux dessous ; le dessus de la cuisse et le tibia éclairés (côté droit)
    det += [(ellipse(K[0] + 1.6, K[1] - 0.6, 1.6, 2.2, th - 90), SKIN.light, 0.55),
            (ellipse(K[0] + 2.0, K[1] - 1.2, 0.7, 1.0, th - 90), SKIN.hi, 0.5),
            (ribbon([add(K, (2.6, 2.0)), lerp(K, A, 0.5), add(A, (1.6, -1.6))], [0.2, 1.0, 0.2]), SKIN.light, 0.55),
            (ribbon([add(H, (3.4, 2)), lerp(H, K, 0.55), add(K, (2.8, -2.6))], [0.2, 1.6, 0.2]), SKIN.light, 0.45),
            # le mollet : son ombre ronde, derrière
            (ribbon([add(K, (-3.4, 1.6)), add(lerp(K, A, 0.35), (-4.4, 0)), add(A, (-2.4, -1.4))], [0.2, 1.4, 0.2]), SKIN.shadow, 0.6),
            # le pied : le cou-de-pied éclairé, les orteils, l'ombre de la plante
            (sm([(A[0] + 1.2, A[1] + 1.2), (A[0] + 4.6, A[1] + 3.6), (A[0] + 8.0, GRD - 4.6), (A[0] + 11.6, GRD - 3.2),
                 (A[0] + 8.6, GRD - 3.2), (A[0] + 4.0, A[1] + 4.6)]), SKIN.light, 0.55),
            (ellipse(A[0] + 7.4, A[1] + 4.6, 1.8, 0.6, 28), SKIN.hi, 0.45),
            (ellipse(A[0] + 1.2, A[1] + 1.2, 1.0, 0.8), SKIN.light, 0.5),                    # la malléole
            (ribbon([(A[0] - 4.8, GRD - 0.7), (A[0] + 4.0, GRD - 0.9), (A[0] + 12.6, GRD - 0.8)], [0.2, 0.8, 0.2]), SKIN.deep, 0.5)]
    for i, x_ in enumerate((9.9, 11.4)):
        det.append((ribbon([(A[0] + x_ - 0.3, GRD - 3.4 + 0.3 * i), (A[0] + x_ + 0.1, GRD - 2.0), (A[0] + x_ + 0.2, GRD - 0.7)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.6))
    fig.part('nleg', sh, SKIN, grad=(K[0] + 6, H[1], A[0] - 6, GRD, [(0, SKIN.light), (0.45, SKIN.base), (1, SKIN.shadow)]),
             cel=1.2, rim=0.5, cast=0, details=det)
    anklet(fig, 'nank', A, sa, 3.3, ['nleg'])


def far_leg(fig, H, K, A):
    """La jambe levée : la cuisse (sous la jupe), le genou, le tibia qui pend, le mollet derrière, le pied pointé vers
    le bas comme une danseuse ; l'anneau d'or de la cheville."""
    th = ang_of(sub(K, H))
    sa = ang_of(sub(A, K))
    u = unit(sa)
    v = (-u[1], u[0])            # la normale (côté gauche de la jambe quand elle descend : vers l'arrière)
    if v[0] > 0:
        v = (-v[0], -v[1])
    toe = add(add(A, u, 10.0), v, -1.6)
    heel = add(add(A, u, 1.6), v, 2.2)
    leg = limb_geom([H, K, A], [5.2, 3.3, 2.2],
                    bulges=[(*lerp(H, K, 0.45), 5.4, 4.6, th), (*add(lerp(K, A, 0.33), v, 1.2), 3.5, 2.6, sa)], smooth=0.8)
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    # le pied pointé : talon rond derrière, cou-de-pied bombé devant, orteils arrondis vers le bas
    L = lambda a_, b_: add(add(A, u, a_), v, b_)
    footp = Polygon([L(-0.6, 2.2), L(0.8, 2.8), L(2.8, 2.4), L(5.0, 1.0), L(7.6, 0.4), L(9.6, -0.1), L(10.7, -0.9),
                     L(10.4, -2.1), L(8.6, -2.6), L(6.0, -3.4), L(3.4, -3.7), L(0.8, -3.0), L(-0.6, -2.3)]).buffer(0.8, join_style=1).buffer(-0.8, join_style=1)
    g = unary_union([leg, footp]).buffer(0.8, join_style=1).buffer(-0.8, join_style=1)
    sh = shape_of(g, step=0.5)
    det = [(ellipse(*add(K, (1.6, 0.4)), 1.8, 2.6, sa), SKIN.light, 0.5),
           (ribbon([add(K, (2.2, 2.6)), add(lerp(K, A, 0.5), v, -1.6), add(A, v, -1.8)], [0.2, 0.9, 0.2]), SKIN.light, 0.55),
           (ribbon([add(K, v, 2.4), add(lerp(K, A, 0.4), v, 3.2), add(A, v, 1.8)], [0.2, 1.3, 0.2]), SKIN.shadow, 0.55),
           (ribbon([add(add(A, u, 2.4), v, -1.6), add(add(A, u, 6.0), v, -2.0), add(toe, v, -0.2)], [0.2, 0.9, 0.2]), SKIN.light, 0.6),
           (ellipse(*add(add(A, u, 7.2), v, 0.6), 1.4, 0.7, sa), SKIN.shadow, 0.45)]
    fig.part('fleg', sh, SKIN, grad=(K[0] + 6, K[1] - 2, A[0] - 4, toe[1], [(0, SKIN.base), (0.5, SKIN.shadow), (1, SKIN.deep)]),
             cel=1.0, rim=0.45, cast=0, details=det)
    anklet(fig, 'fank', A, sa, 3.1, ['fleg'])


def anklet(fig, name, A, ang, w, cast_on):
    """Un anneau d'or à la cheville : il fait le tour (le bord du bas suit la courbe de la jambe)."""
    sh = xf(rpoly([(-1.0, -w), (1.1, -w), (1.1, w), (-1.0, w)], 0.7), A[0], A[1], ang)
    sh = xf(sm([(-1.0, -w), (0.2, -w - 0.1), (1.2, -w), (1.4, 0), (1.2, w), (0.2, w + 0.1), (-1.0, w), (-0.8, 0)], t=0.9), A[0], A[1], ang)
    fig.part(name, sh, GOLD, grad=(A[0] + w, A[1] - 2, A[0] - w, A[1] + 2, [(0, GOLD.hi), (0.35, GOLD.light), (0.7, GOLD.base), (1, GOLD.shadow)]),
             cel=0.5, rim=0.4, cast=0.7, cast_on=cast_on,
             details=[(xf(ribbon([(0.1, -w * 0.8), (0.2, 0), (0.1, w * 0.8)], [0.1, 0.5, 0.1]), A[0], A[1], ang), GOLD.shadow, 0.6)])


# ======================================================================== le corps
def body(fig, P, U, UC, TOR, SN, EN, WN, bg):
    """Le buste (épaules rondes, taille fine, ventre nu), le cou et le bras proche : UNE seule forme de peau (pas de
    jointure visible à l'épaule ni au coude)."""
    T = LT(TOR)
    C = LT(UC)
    torso = sm([C((70.2, 44.0)), C((69.4, 49.0)), C((64.4, 51.0)), C((59.4, 52.2)), (SN[0] - 2.6, SN[1] - 0.6),
                T((55.6, 58.4)), T((56.6, 62.0)), T((58.6, 65.6)), T((58.4, 69.4)), T((56.8, 73.0)), T((56.6, 76.0)),
                T((67.0, 77.0)), T((79.0, 75.0)), T((79.2, 71.0)), T((78.0, 67.4)), T((78.4, 63.4)), T((80.0, 59.4)),
                C((81.6, 55.6)), C((81.6, 52.6)), C((79.6, 50.4)), C((80.0, 47.4)), C((79.6, 44.0))], t=0.9)
    ua = ang_of(sub(EN, SN))
    arm = limb_geom([add(SN, (1.4, 0.2)), SN, EN, WN], [4.6, 4.2, 2.85, 2.25],
                    bulges=[(*lerp(SN, EN, 0.3), 4.3, 3.6, ua),                               # le deltoïde, l'épaule ronde
                            (*lerp(EN, WN, 0.28), 3.0, 2.8, ang_of(sub(WN, EN)))], smooth=0.9)
    g = poly_of(torso).union(arm).buffer(0.9, join_style=1).buffer(-0.9, join_style=1)
    sh = shape_of(g, step=0.5)
    det = []
    # le buste : le flanc proche dans l'ombre, la clavicule, le sternum, le dessous des seins (portée par le haut)
    det += [(sm([T((55.0, 57.0)), T((60.0, 60.0)), T((61.4, 66.0)), T((60.4, 71.6)), T((58.6, 77.0)), T((54.6, 77.0)), T((55.0, 66.0))]), SKIN.shadow, 0.55),
            (ribbon([C((61.0, 52.6)), C((66.0, 53.0)), C((70.4, 53.2))], [0.2, 0.8, 0.2]), SKIN.shadow, 0.45),
            (ribbon([C((61.0, 51.8)), C((66.0, 52.1)), C((70.4, 52.3))], [0.1, 0.7, 0.1]), SKIN.light, 0.5),
            (ribbon([C((72.4, 52.8)), C((76.0, 52.6)), C((79.6, 51.6))], [0.2, 0.7, 0.2]), SKIN.hi, 0.5),
            (sm([C((74.6, 48.6)), C((79.6, 47.6)), C((80.6, 51.4)), C((76.6, 51.0))]), SKIN.light, 0.4),
            # le cou : l'ombre portée par la mâchoire, le muscle du cou
            (sm([C((69.6, 44.0)), C((79.8, 44.0)), C((79.4, 47.6)), C((74.6, 48.6)), C((70.4, 48.6))]), SKIN.deep, 0.55),
            (ribbon([C((72.0, 46.0)), C((74.4, 48.8)), C((77.6, 51.2))], [0.2, 0.8, 0.2]), SKIN.shadow, 0.4),
            # le ventre : la taille fine, la ligne du ventre, le nombril, les côtes sous le haut
            (ribbon([T((68.2, 63.4)), T((68.6, 66.0)), T((68.3, 68.4))], [0.2, 0.9, 0.2]), SKIN.shadow, 0.5),
            (ellipse(*T((68.6, 67.0)), 0.55, 0.8), SKIN.deep, 0.8),
            (ellipse(*T((68.9, 66.6)), 0.4, 0.3), SKIN.light, 0.6),
            (sm([T((71.0, 62.4)), T((77.6, 62.0)), T((77.4, 66.6)), T((73.4, 69.0)), T((70.6, 66.4))]), SKIN.light, 0.5),
            (sm([T((72.6, 62.6)), T((77.0, 62.6)), T((76.4, 65.0)), T((73.6, 65.6))]), SKIN.hi, 0.3),
            (ribbon([T((61.4, 63.2)), T((63.0, 66.0)), T((63.0, 69.6))], [0.2, 1.0, 0.2]), SKIN.shadow, 0.35),
            (sm([T((56.0, 74.0)), T((79.6, 71.4)), T((79.6, 76.0)), T((56.0, 77.0))]), SKIN.deep, 0.5)]
    # le bras proche : le dessus éclairé (épaule ronde, avant-bras), le creux du coude doux, le dessous dans l'ombre
    fa = ang_of(sub(WN, EN))
    det += [(ribbon([lerp(SN, EN, 0.0), lerp(SN, EN, 0.5), lerp(EN, WN, 0.1), lerp(EN, WN, 0.75)], [0.6, 1.5, 0.9, 0.2]).move(0.3, -1.6), SKIN.light, 0.55),
            (ellipse(*add(lerp(SN, EN, 0.25), (0.6, -1.8)), 2.2, 1.0, ua), SKIN.hi, 0.4),
            (ellipse(*add(EN, (0.2, 1.3)), 1.3, 0.55, fa), SKIN.shadow, 0.35)]
    fig.part('body', sh, SKIN, grad=(82, 46, 56, 76, [(0, SKIN.light), (0.4, SKIN.base), (1, SKIN.shadow)]),
             cel=1.4, rim=0.6, cast=1.2, cast_on=['farm', 'fleg', 'nleg'] + bg, details=det, occl=(SKIN.deep, 0.18, 3.0))


def top(fig, TOR, UC):
    """Le haut rouge en cœur (deux bonnets, le proche plus grand), liseré d'or en haut, bande d'or dessous ; le collier
    de perles d'or en arc, la goutte de cornaline."""
    T = LT(TOR)
    sh = sm([T((56.0, 57.6)), T((59.0, 55.2)), T((63.2, 54.6)), T((67.2, 56.4)), T((68.8, 57.8)), T((71.0, 56.0)),
             T((75.0, 55.0)), T((78.6, 56.0)), T((80.6, 58.4)), T((80.2, 62.4)), T((74.0, 63.0)), T((68.6, 62.8)),
             T((62.0, 63.2)), T((56.8, 62.6))], sharp=(4,), t=0.9)
    det = [  # les volumes : le bonnet proche dans une ombre douce, le lointain éclairé, le creux entre les deux
        (sm([T((56.0, 57.6)), T((59.0, 55.6)), T((61.4, 58.0)), T((61.0, 62.0)), T((56.8, 62.6))]), RED.shadow, 0.55),
        (sm([T((63.0, 55.8)), T((66.6, 57.0)), T((66.2, 59.4)), T((63.4, 58.8))]), RED.light, 0.6),
        (sm([T((73.4, 56.0)), T((77.8, 56.6)), T((79.0, 59.4)), T((75.4, 59.6))]), RED.light, 0.7),
        (ellipse(*T((76.6, 57.2)), 1.3, 0.6, -15), RED.hi, 0.6),
        (ellipse(*T((65.0, 56.6)), 1.1, 0.5, -10), RED.hi, 0.45),
        (ribbon([T((68.8, 57.8)), T((68.4, 59.8)), T((68.6, 61.8))], [0.3, 1.2, 0.2]), RED.deep, 0.6),
        # le liseré d'or du haut (il suit les deux bonnets)
        (taper(crpath([T((56.0, 57.6)), T((59.0, 55.2)), T((63.2, 54.6)), T((67.2, 56.4)), T((68.8, 57.8))], 20), 1.1, 1.1), GOLD.base, 1),
        (taper(crpath([T((68.8, 57.8)), T((71.0, 56.0)), T((75.0, 55.0)), T((78.6, 56.0)), T((80.6, 58.4))], 20), 1.1, 1.1), GOLD.base, 1),
        (taper(crpath([T((59.2, 55.0)), T((63.2, 54.4)), T((67.0, 56.0))], 12), 0.45, 0.45).move(0.1, -0.15), GOLD.hi, 0.9),
        (taper(crpath([T((71.2, 55.8)), T((75.0, 54.8)), T((78.4, 55.8))], 12), 0.45, 0.45).move(0.1, -0.15), GOLD.hi, 0.9),
        # la bande d'or dessous (elle fait le tour du buste : peinte d'un bord à l'autre)
        (sm([T((54.0, 60.4)), T((68.0, 60.8)), T((82.0, 59.6)), T((82.0, 64.0)), T((68.0, 64.4)), T((54.0, 64.0))]), GOLD.base, 1),
        (sm([T((54.0, 60.4)), T((68.0, 60.8)), T((82.0, 59.6)), T((82.0, 61.4)), T((68.0, 62.0)), T((54.0, 61.6))]), GOLD.light, 0.95),
        (sm([T((54.0, 62.6)), T((68.0, 63.0)), T((82.0, 62.2)), T((82.0, 64.0)), T((68.0, 64.4)), T((54.0, 64.0))]), GOLD.shadow, 0.6)]
    fig.part('top', sh, RED, grad=(80, 54, 58, 63, [(0, RED.light), (0.45, RED.base), (1, RED.shadow)]),
             cel=0.9, rim=0.6, cast=1.1, cast_on=['body'], details=det)
    # le collier : des perles d'or en arc (de plus en plus petites vers la nuque), une goutte de cornaline au milieu
    C = LT(UC)
    arc = crpath([(59.6, 51.6), (63.0, 53.6), (67.2, 54.8), (71.6, 54.6), (75.6, 53.4), (79.2, 51.4)], 60)
    beads = []
    n = 15
    for i in range(n):
        t = i / (n - 1)
        p = C(arc[int(t * 60)])
        r = 0.72 + 0.2 * math.sin(math.pi * t)
        beads.append((p, r))
    from shapely.geometry import Point
    from shapely.ops import unary_union
    gp = unary_union([Point(p).buffer(r, quad_segs=10) for p, r in beads])
    dc = C((70.0, 56.2))
    gp = gp.union(Point(dc).buffer(0.9, quad_segs=10)).union(poly_of(sm([(dc[0] - 1.2, dc[1] + 0.4), (dc[0] + 1.2, dc[1] + 0.4),
                                                                         (dc[0] + 1.4, dc[1] + 2.4), (dc[0], dc[1] + 4.0), (dc[0] - 1.4, dc[1] + 2.4)], sharp=(3,))))
    sh = shapes_of(gp, step=0.25, t=0.8)
    det = []
    for p, r in beads:
        det += [(ellipse(p[0] - 0.12, p[1] + 0.14, r * 0.9, r * 0.9), GOLD.shadow, 0.6),
                (ellipse(p[0] + 0.08, p[1] - 0.08, r * 0.72, r * 0.72), GOLD.base, 1),
                (ellipse(p[0] + 0.22, p[1] - 0.22, r * 0.3, r * 0.3), GOLD.hi, 1)]
    det += [(sm([(dc[0] - 0.9, dc[1] + 0.9), (dc[0] + 0.9, dc[1] + 0.9), (dc[0] + 1.0, dc[1] + 2.4), (dc[0], dc[1] + 3.5), (dc[0] - 1.0, dc[1] + 2.4)], sharp=(3,)),
             ('rad', dc[0] + 0.4, dc[1] + 1.6, 2.0, 2.0, [(0, CARN.hi), (0.45, CARN.light), (1, CARN.shadow)]), 1),
            (ellipse(dc[0] + 0.35, dc[1] + 1.5, 0.3, 0.45, -20), '#ffffff', 0.85)]
    fig.part('necklace', sh, GOLD, cel=0.3, rim=0.25, cast=0.7, cast_on=['body', 'top'], details=det)


# ======================================================================== les mains, les bracelets, la torche
def hand(fig, P, E, W, bg):
    """La main proche, ouverte, tendue vers l'arrière : la paume, les doigts en éventail (l'index relevé), le pouce
    dessous. Une seule forme (aucun cercle au poignet), les doigts séparés par des creux doux."""
    fa = ang_of(sub(W, E))
    u = unit(fa)                         # le long de l'avant-bras (vers la main)
    v = (-u[1], u[0])                    # en travers
    if v[1] > 0:
        v = (-v[0], -v[1])               # v vers le haut (côté de l'index)

    def L(x, y):
        return (W[0] + u[0] * x + v[0] * y, W[1] + u[1] * x + v[1] * y)
    palm = poly_of(sm([L(-0.6, 2.1), L(2.4, 2.8), L(5.0, 2.7), L(6.6, 1.0), L(6.6, -1.6), L(4.8, -2.9), L(1.6, -2.8), L(-0.6, -2.0)], t=0.9))
    from shapely.ops import unary_union
    from outils import cone
    fingers = [  # base, direction (degrés depuis u, + vers l'index), longueur, rayon
        ((5.6, 2.0), 52, 4.9, 1.0),      # l'index, relevé
        ((6.4, 0.7), 20, 5.2, 1.0),      # le majeur
        ((6.4, -0.6), -4, 4.6, 0.95),    # l'annulaire
        ((5.4, -1.9), -26, 3.6, 0.85),   # l'auriculaire
    ]
    gs = [palm]
    tips = []
    for (bx, by), a, ln, r in fingers:
        b = L(bx, by)
        d = rot(u, -a) if (v[0] * rot(u, 90)[0] + v[1] * rot(u, 90)[1]) < 0 else rot(u, a)
        mid = add(b, d, ln * 0.55)
        d2 = rot(d, -8 if a > 0 else 6)
        tip = add(mid, d2, ln * 0.45)
        gs.append(cone(b, r * 1.05, mid, r))
        gs.append(cone(mid, r, tip, r * 0.82))
        tips.append((b, mid, tip, r))
    th0, th1, th2 = L(1.6, -2.4), L(3.6, -4.0), L(6.0, -4.4)
    gs += [cone(th0, 1.2, th1, 0.95), cone(th1, 0.95, th2, 0.78)]
    g = unary_union(gs).buffer(0.25, join_style=1).buffer(-0.25, join_style=1)
    sh = shape_of(g, step=0.3, t=0.85)
    det = [(sm([L(0.6, 1.6), L(4.6, 2.0), L(5.6, 0.2), L(2.0, -0.4)]), SKIN.light, 0.45),
           (ribbon([L(2.0, -1.2), L(4.0, -1.6), L(5.6, -1.0)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.5)]
    for b, mid, tip, r in tips:
        det += [(ribbon([lerp(b, mid, 0.2), mid, lerp(mid, tip, 0.8)], [0.1, 0.45, 0.1]).move(0.25, -0.35), SKIN.light, 0.6),
                (ribbon([b, lerp(b, mid, 0.6)], [0.4, 0.1]).move(-0.2, 0.5), SKIN.shadow, 0.5)]
    det += [(ribbon([th0, th1, th2], [0.1, 0.5, 0.1]).move(0.2, -0.3), SKIN.light, 0.5)]
    fig.part('nhand', sh, SKIN, grad=(W[0] + 2, W[1] - 4, W[0] - 8, W[1] + 4, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.7, rim=0.45, cast=0.8, cast_on=bg, details=det)
    return ['nhand']


def bracelets(fig, name, E, W, w, cast_on):
    """Deux bracelets d'or au poignet (ils font le tour : le bord suit la courbe du bras), le second un peu plus haut."""
    fa = ang_of(sub(W, E))
    for i, x in enumerate((-0.9, -3.3)):
        c = add(W, unit(fa), x)
        ww = w + 0.15 * i
        sh = xf(sm([(-0.75, -ww), (0.25, -ww - 0.15), (0.85, -ww), (1.05, 0), (0.85, ww), (0.25, ww + 0.15), (-0.75, ww), (-0.55, 0)], t=0.9),
                c[0], c[1], fa)
        fig.part('%s%d' % (name, i), sh, GOLD, grad=(c[0] + ww, c[1] - ww, c[0] - ww, c[1] + ww, [(0, GOLD.hi), (0.35, GOLD.light), (0.75, GOLD.base), (1, GOLD.shadow)]),
                 cel=0.4, rim=0.35, cast=0.6, cast_on=cast_on,
                 details=[(xf(ribbon([(0.1, -ww * 0.85), (0.15, 0), (0.1, ww * 0.85)], [0.1, 0.35, 0.1]), c[0], c[1], fa), GOLD.shadow, 0.55)])


def torch_frame(WF, tang):
    """Le repère de la torche : l'origine au milieu du poing, y vers la flamme (la torche droite quand tang = 0)."""
    C = add(WF, (0.2, -6.8))
    a = math.radians(tang)
    ca, sa = math.cos(a), math.sin(a)

    def T(x, y):
        return (C[0] + x * ca - y * sa, C[1] + x * sa + y * ca)
    T.C, T.a = C, tang
    return T


def torch_parts(fig, P, T):
    """Le manche de bois (il ressort sous le poing avec un embout d'or), la flamme à trois langues penchées vers
    l'arrière (cœur clair), la coupe d'or."""
    names = []
    handle = sm([T(-1.1, -10.6), T(1.1, -10.6), T(1.0, 6.2), T(-1.0, 6.2)], sharp=(0, 1, 2, 3), t=0.5)
    fig.part('handle', handle, WOOD, grad=(*T(1, -8), *T(-1, 4), [(0, WOOD.light), (1, WOOD.shadow)]), cel=0.5, rim=0.4, cast=0.6,
             details=[(sm([T(0.25, -10.6), T(1.1, -10.6), T(1.0, 6.2), T(0.25, 6.2)], sharp=(0, 1, 2, 3), t=0.5), WOOD.light, 0.6)])
    names.append('handle')
    cap = sm([T(-1.4, 5.6), T(1.4, 5.6), T(1.6, 7.0), T(0.0, 8.0), T(-1.6, 7.0)], sharp=(0, 1), t=0.9)
    fig.part('hcap', cap, GOLD, grad=(*T(1.4, 5.6), *T(-1.4, 8), [(0, GOLD.light), (1, GOLD.shadow)]), cel=0.3, rim=0.3, cast=0.5,
             details=[(ellipse(*T(0.6, 6.4), 0.35, 0.3), GOLD.hi, 0.9)])
    names.append('hcap')
    # la flamme : trois langues (la plus haute au milieu), penchées vers l'arrière, d'UNE seule forme
    ph, fl = P['fl'], P['flare']
    lean = -4.0 - 2.0 * P['trail']
    k = 1 + 0.18 * fl
    tongues = [((-1.6, -12.6), (-4.4 + lean * 0.3, -15.6), (-5.6 + lean * 0.7 + 0.7 * math.sin(ph + 1.3), -19.6 * k), (-6.0 + lean + 0.9 * math.sin(ph + 2.1), -23.6 * k + 0.6 * math.cos(ph)), 4.2),
               ((0.4, -12.6), (0.2 + lean * 0.3, -17.0), (-1.4 + lean * 0.7 + 0.8 * math.sin(ph), -22.6 * k), (-1.6 + lean + 1.1 * math.sin(ph + 0.8), -28.6 * k + 0.8 * math.cos(ph + 0.5)), 5.6),
               ((2.2, -12.4), (3.6 + lean * 0.3, -15.4), (3.6 + lean * 0.6 + 0.6 * math.sin(ph + 2.6), -19.4 * k), (4.6 + lean * 0.8 + 0.8 * math.sin(ph + 3.0), -22.0 * k + 0.6 * math.cos(ph + 1.7)), 3.8)]
    shapes = [lock(T(*a), T(*b), T(*c), T(*d), w, n=12, bulge=0.45) for a, b, c, d, w in tongues]
    base = ellipse(*T(0.2, -13.2), 3.8 + 0.4 * fl, 2.8)
    flame = union(base, *shapes, step=0.35, smooth=0.6)
    cx, cy = T(0.0, -14.2)
    det = [(flame, ('rad', cx, cy + 1, 15 * k, 15 * k, [(0, '#fff8d0'), (0.2, '#ffe070'), (0.45, '#ffaa30'), (0.75, '#f86a1e'), (1, '#d8361a')]), 1)]
    core = [lock(T(-0.6, -12.6), T(-0.6 + lean * 0.2, -15.6), T(-1.0 + lean * 0.4 + 0.4 * math.sin(ph), -18.6 * k), T(-1.0 + lean * 0.5 + 0.6 * math.sin(ph + 0.8), -21.6 * k), 3.4, n=10, bulge=0.4),
            ellipse(*T(0.0, -13.6), 2.4, 1.8)]
    coresh = union(*core, step=0.3, smooth=0.4)
    det += [(under(flame, 0.6, -1.8), '#e8461c', 0.35), (coresh, ('rad', cx, cy - 1, 7 * k, 7 * k, [(0, '#ffffff'), (0.4, '#fff6c0'), (1, '#ffd23a')]), 0.95)]
    fig.part('flame', flame, FLAME, cel=0, rim=0.6, cast=0, ink=FINK, details=det)
    names.append('flame')
    # la coupe d'or (plus large en haut, son bord tourné vers nous : on voit l'ellipse du dessus)
    cup = sm([T(-4.4, -12.6), T(4.4, -12.6), T(3.4, -11.0), T(1.4, -9.0), T(1.2, -7.6), T(-1.2, -7.6), T(-1.4, -9.0), T(-3.4, -11.0)],
             sharp=(0, 1), t=0.9)
    det = [(ellipse(*T(0.0, -12.6), 4.4, 1.0, T.a), GOLD.shadow, 1), (ellipse(*T(0.0, -12.9), 3.6, 0.6, T.a), '#ffb43a', 0.9),
           (sm([T(1.0, -12.0), T(3.8, -12.0), T(2.8, -10.6), T(1.0, -9.2)]), GOLD.hi, 0.5),
           (ribbon([T(-4.2, -11.4), T(0, -11.0), T(4.2, -11.4)], [0.2, 0.5, 0.2]), GOLD.shadow, 0.55),
           (ellipse(*T(-0.1, -8.2), 1.4, 0.5, T.a), GOLD.base, 1), (ellipse(*T(0.3, -8.4), 0.6, 0.25, T.a), GOLD.hi, 0.9)]
    fig.part('cup', cup, GOLD, grad=(*T(4, -12), *T(-3, -8), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]), cel=0.6, rim=0.4,
             cast=0.7, cast_on=['handle', 'flame'], details=det)
    names.append('cup')
    return names


def fist(fig, T, W, bg):
    """Le poing lointain serré sur le manche : quatre doigts devant le manche (phalanges à droite), le pouce
    par-dessus. Repère de la torche (y vers la flamme)."""
    body_ = sm([T(-3.2, -3.6), T(-1.0, -4.6), T(2.6, -4.4), T(4.0, -2.4), T(4.2, 1.6), T(3.4, 3.8), T(0.6, 4.8),
                T(-2.6, 4.2), T(-3.8, 1.4)], t=0.95)
    det = [(sm([T(1.6, -4.0), T(3.8, -2.4), T(4.0, 2.4), T(2.6, 3.6), T(1.8, 0.0)]), SKIN.light, 0.5)]
    for y0, y1 in ((-3.4, -1.4), (-1.4, 0.6), (0.6, 2.5), (2.5, 4.2)):
        det += [(ribbon([T(3.6, y1), T(1.0, y1 + 0.1), T(-2.4, y1)], [0.1, 0.45, 0.1]), SKIN.shadow, 0.65),
                (ellipse(*T(3.2, (y0 + y1) / 2), 0.55, 0.7), SKIN.hi, 0.45)]
    fig.part('ffist', body_, SKIN, grad=(*T(4, -4), *T(-4, 4), [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.8, cast_on=bg, details=det)
    thumb = limb_u([T(-2.8, -3.6), T(-0.6, -5.4), T(1.8, -5.0)], [1.25, 1.05, 0.85], smooth=0.4, step=0.3)
    fig.part('fthumb', thumb, SKIN, cel=0.45, rim=0.4, cast=0.6, cast_on=['ffist', 'handle'] + bg,
             details=[(ribbon([T(-2.2, -4.2), T(-0.6, -5.8), T(1.4, -5.6)], [0.1, 0.45, 0.1]), SKIN.light, 0.6)])
    return ['ffist', 'fthumb']


# ======================================================================== la tête
def head(fig, P, HEAD, HEADN):
    """Le visage (agrandi ×1,1), les cheveux tirés en arrière (une seule forme sur le crâne), les deux plumes nouées
    d'une perle d'or, l'oreille et son anneau d'or."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    # ---- le visage ----
    face = sm([(69.5, 25.0), (75.0, 22.6), (81.0, 22.4), (85.0, 24.0), (86.8, 26.8), (87.2, 29.4), (86.6, 31.8),
               (86.9, 33.8), (87.9, 36.0), (88.9, 37.7), (88.7, 38.8), (87.3, 39.4), (87.4, 40.5), (87.6, 41.8),
               (87.1, 42.9), (87.3, 44.0), (86.5, 45.2), (86.1, 46.5), (85.0, 47.9), (82.6, 48.7), (79.2, 48.4),
               (75.6, 47.0), (71.8, 44.6), (68.6, 41.6), (66.8, 37.0), (66.8, 31.0)], sharp=(10,), t=0.9)
    fd = []
    blink = P['blink'] > 0.5
    sm_ = P['smile']
    # les plans : la joue proche et la tempe dans une ombre douce, le plan de face éclairé (front, nez, joue lointaine)
    fd += [(sm([(67.0, 31.0), (68.6, 36.0), (70.8, 41.0), (74.2, 44.6), (79.0, 47.4), (77.6, 48.6), (73.0, 46.6),
                (68.8, 42.6), (66.6, 37.0)]), SKIN.shadow, 0.55),
           (sm([(80.6, 23.2), (85.2, 24.4), (86.8, 28.0), (85.8, 30.0), (82.4, 28.2)]), SKIN.hi, 0.4),
           (sm([(84.4, 35.6), (86.8, 34.6), (88.2, 37.2), (87.0, 39.4), (85.0, 40.6)]), SKIN.light, 0.4),
           (ellipse(77.0, 39.0, 2.6, 1.5, -12), SKIN.light, 0.3),             # la pommette proche
           (ellipse(77.6, 38.6, 1.2, 0.55, -14), SKIN.hi, 0.25),
           (ellipse(76.0, 40.4, 2.4, 1.3, 0), '#e0604c', 0.1)]                # un peu de rouge aux joues
    # l'ombre sous le menton, la mâchoire nette sur le cou
    fd += [(sm([(74.6, 46.0), (79.6, 47.6), (84.6, 47.4), (83.0, 48.8), (78.6, 48.8), (74.0, 47.2)]), SKIN.shadow, 0.55)]
    # les orbites : un creux doux sous l'arcade
    fd += [(sm([(72.0, 32.4), (75.6, 31.6), (79.6, 32.6), (80.6, 34.6), (78.6, 36.8), (73.6, 36.8), (71.6, 35.0)]), SKIN.shadow, 0.35),
           (sm([(81.6, 33.0), (84.6, 32.2), (86.6, 33.0), (86.2, 35.4), (82.8, 36.4)]), SKIN.shadow, 0.3)]
    # les yeux : grands, en amande, iris ambre coupé par les paupières, pupille, éclat ; trait de cils épais en haut ;
    # l'œil lointain de même forme, sur la même ligne, plus étroit, son coin intérieur caché par l'arête du nez
    eyes = (
        (sm([(72.3, 34.9), (73.7, 33.2), (76.4, 32.6), (78.8, 34.4), (77.1, 36.4), (74.3, 36.4)], sharp=(0, 3), t=0.9),
         (76.1, 34.6), 1.55, 1.0, False),
        (sm([(81.6, 34.4), (82.8, 32.9), (84.7, 32.6), (86.2, 33.6), (85.2, 35.6), (82.8, 35.9)], sharp=(0, 3), t=0.9),
         (83.7, 34.3), 1.4, 0.78, True),
    )
    for almond, (ix, iy), ir, sx, far in eyes:
        p0, p1, p2, p3, p4, p5 = (almond_pt(almond, i) for i in range(6))
        if blink:
            fd += [(almond.scale(1.04, 1.1, ix, iy), SKIN.base, 1),
                   (ribbon([p0, lerp(p5, p4, 0.5), p3], [0.3, 0.8, 0.25]).move(0, -0.2), LASH, 0.95)]
            continue
        fd += [(almond.scale(1.08, 1.22, ix, iy + 0.1), SKIN.deep, 0.5), (almond, '#f4ebe4', 1)]
        iris = inter(ellipse(ix, iy, ir * sx, ir * 1.02), almond)
        pup = inter(ellipse(ix + 0.05, iy + 0.05, ir * 0.5 * sx, ir * 0.55), almond)
        if iris:
            fd += [(iris, ('rad', ix + 0.3, iy + 0.6, ir * 1.25, ir * 1.25, [(0, '#f2b450'), (0.45, '#c47420'), (1, '#6a3010')]), 1)]
        if pup:
            fd += [(pup, '#22080c', 1)]
        # l'ombre de la paupière du haut sur l'œil, les éclats
        fd += [(sm([p0, p1, p2, p3, lerp(p3, (ix, iy), 0.3), lerp(p2, (ix, iy + 0.7), 0.45), lerp(p1, (ix, iy + 0.7), 0.45)], t=0.8), SKIN.deep, 0.35),
               (ellipse(ix + ir * 0.38 * sx, iy - ir * 0.28, ir * 0.3 * sx, ir * 0.27), '#ffffff', 1),
               (ellipse(ix - ir * 0.35 * sx, iy + ir * 0.42, ir * 0.13 * sx, ir * 0.11), '#ffffff', 0.7)]
        # les cils : un trait épais sur le haut, qui déborde en pointe au coin extérieur (le regard de braise)
        if not far:
            fd += [(ribbon([add(p0, (-0.9, -0.45)), add(p0, (0.1, -0.05)), p1, p2, add(p3, (0.15, 0.1))], [0.1, 0.6, 0.85, 0.7, 0.2]), LASH, 0.95),
                   (ribbon([p0, p5, p4, p3], [0.1, 0.32, 0.28, 0.1]), '#4a1a2a', 0.65)]
        else:
            fd += [(ribbon([add(p0, (-0.1, 0.0)), p1, p2, p3, add(p3, (0.7, -0.4))], [0.2, 0.6, 0.75, 0.55, 0.1]), LASH, 0.95),
                   (ribbon([p0, p5, p4, p3], [0.1, 0.28, 0.25, 0.1]), '#4a1a2a', 0.6)]
    # les sourcils épais, qui descendent vers le nez (le regard féroce)
    fd += [(sm([(71.0, 31.8), (72.6, 30.2), (75.2, 29.4), (78.0, 30.2), (80.4, 32.0), (79.8, 32.9), (77.4, 31.6),
                (74.8, 31.0), (72.6, 31.4)], sharp=(0, 4), t=0.85), BROW, 0.97),
           (sm([(81.2, 32.6), (82.4, 30.8), (84.6, 29.9), (86.9, 29.9), (86.8, 30.8), (84.6, 31.0), (82.8, 32.0), (81.8, 33.2)],
               sharp=(0, 3), t=0.85), BROW, 0.97),
           (ribbon([(72.8, 30.2), (75.4, 29.6), (77.8, 30.4)], [0.1, 0.35, 0.1]), HAIR.light, 0.5)]
    # le nez : l'arête claire (une seule ligne douce), le flanc proche dans une ombre douce, l'aile, une narine, un éclat
    # (en trois quarts, l'arête descend d'entre les yeux le long du coin de l'œil lointain, puis le bout file vers la
    # droite et dépasse un peu du profil)
    fd += [(sm([(80.0, 34.4), (81.4, 36.6), (83.4, 38.6), (85.6, 39.6), (84.0, 40.2), (81.6, 39.4), (80.0, 37.4)]), SKIN.shadow, 0.42),
           (ribbon([(80.7, 33.2), (81.5, 35.4), (83.0, 37.0), (85.4, 37.6), (87.6, 37.7)], [0.1, 0.42, 0.5, 0.45, 0.2]), SKIN.light, 0.75),
           (ellipse(87.9, 37.6, 0.75, 0.48, 15), SKIN.glint, 0.85),
           (sm([(84.0, 38.4), (86.4, 38.6), (87.2, 39.5), (85.8, 40.0), (84.0, 39.6)]), SKIN.shadow, 0.6),
           (ellipse(86.2, 39.5, 0.55, 0.28, 15), SKIN.deep, 0.9)]
    # la bouche : grand sourire sûr d'elle, les dents du haut, la gorge rouge sombre (jamais de noir), lèvres baies
    if sm_ > 0.5:
        mouth = sm([(80.4, 41.5), (82.6, 41.5), (85.4, 41.2), (87.4, 41.4), (86.8, 42.8), (84.4, 43.9), (82.2, 43.4)], sharp=(0, 3), t=0.9)
        fd += [(mouth.scale(1.04, 1.25, 84, 42.4), LIPS[0], 0.9), (mouth, '#5a1222', 1)]
        teeth = inter(sm([(80.0, 41.0), (87.8, 40.8), (87.8, 42.5), (84.0, 42.6), (80.0, 42.1)]), mouth)
        if teeth:
            fd += [(teeth, ('lin', 87, 41, 81, 42.4, [(0, '#fffaf2'), (0.6, '#f2e6dc'), (1, '#c4aaa6')]), 1)]
        fd += [(ribbon([(83.4, 41.3), (83.5, 42.3)], [0.18, 0.1]), '#c4aaa6', 0.7),
               (ribbon([(85.6, 41.2), (85.7, 42.1)], [0.15, 0.1]), '#c4aaa6', 0.6),
               (ellipse(84.6, 43.3, 1.6, 0.5), '#8e2a3a', 0.6)]
        # la lèvre du haut (fine, l'arc de cupidon), la lèvre du bas (pleine, un éclat)
        fd += [(sm([(80.2, 41.5), (82.4, 40.8), (84.2, 40.7), (85.0, 40.4), (86.0, 40.6), (87.6, 41.3), (86.0, 41.3), (83.0, 41.5)], sharp=(0, 5), t=0.85), LIPS[1], 1),
               (ribbon([(82.6, 40.85), (84.0, 40.75), (85.6, 40.6)], [0.1, 0.3, 0.1]), LIPS[3], 0.5),
               (sm([(81.6, 43.3), (84.0, 44.0), (86.6, 43.1), (86.4, 44.2), (84.4, 45.0), (82.6, 44.6)], sharp=(0, 2), t=0.9), LIPS[1], 1),
               (ellipse(84.8, 44.2, 1.0, 0.32, -6), LIPS[3], 0.85),
               # les coins relevés, le pli du sourire sur la joue proche
               (ribbon([(79.4, 40.6), (80.2, 41.5), (80.6, 42.4)], [0.1, 0.4, 0.1]), SKIN.deep, 0.5),
               (ribbon([(79.0, 40.0), (79.5, 41.4), (80.2, 42.8)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.35),
               (ribbon([(82.0, 45.8), (84.0, 46.2), (86.0, 45.6)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.35),
               (ellipse(85.2, 46.4, 1.0, 0.5), SKIN.light, 0.4)]
    else:
        fd += [(sm([(80.6, 41.9), (83.0, 41.4), (85.6, 41.3), (87.4, 41.6), (85.6, 42.4), (83.0, 42.6)], sharp=(0, 3), t=0.85), LIPS[1], 1),
               (ribbon([(80.6, 42.0), (83.6, 42.0), (87.2, 41.7)], [0.1, 0.35, 0.1]), LIPS[0], 0.95),
               (sm([(81.8, 42.6), (84.4, 42.7), (86.6, 42.3), (86.0, 43.6), (83.8, 44.0)], t=0.9), LIPS[2], 1)]
    part('face', face, SKIN, grad=(88, 25, 67, 46, [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
         cel=1.0, rim=0.5, cast=1.0, cast_on=['body', 'top', 'necklace', 'h1', 'h2', 'h3', 'h3b', 'h4', 'h5', 'hm'], details=fd)

    # ---- les cheveux tirés en arrière : UNE seule forme sur le crâne (front dégagé, tempe, derrière l'oreille,
    # nuque) ; les mèches de la crinière en partent ----
    cap = sm([(86.6, 25.4), (84.4, 24.0), (80.4, 23.6), (76.4, 24.4), (72.8, 26.0), (70.6, 28.8), (69.6, 32.0),
              (68.4, 34.8), (66.4, 34.6), (64.6, 36.6), (64.2, 41.0), (65.2, 45.0), (62.0, 47.4), (58.4, 43.6),
              (56.6, 36.0), (57.0, 27.4), (60.4, 19.8), (66.0, 15.2), (73.6, 13.4), (80.2, 14.6), (84.8, 17.6), (87.0, 21.8)],
             sharp=(0, 8), t=0.9)
    hd = []
    # l'anneau de reflet sur le crâne (lavande), les mèches tirées vers l'arrière (creux doux), la nuque dans l'ombre
    hd += [(ribbon([(62.0, 23.0), (67.0, 17.8), (74.0, 16.0), (80.6, 17.2), (85.0, 20.4)], [0.2, 1.3, 1.6, 1.2, 0.2]), HAIR.light, 0.8),
           (ribbon([(64.0, 21.6), (69.0, 17.6), (75.0, 16.6)], [0.1, 0.6, 0.1]).move(0.4, -0.3), HAIR.hi, 0.6),
           (ribbon([(84.4, 23.8), (78.0, 22.4), (71.4, 22.6), (65.0, 25.4), (60.6, 29.4)], [0.1, 0.6, 0.7, 0.6, 0.1]), HAIR.shadow, 0.7),
           (ribbon([(70.6, 27.6), (66.0, 28.6), (61.4, 32.4)], [0.1, 0.5, 0.1]), HAIR.shadow, 0.6),
           (ribbon([(81.0, 20.6), (74.6, 19.8), (68.0, 21.0), (62.6, 24.6)], [0.1, 0.4, 0.4, 0.1]), HAIR.light, 0.45),
           (sm([(57.0, 36.0), (61.4, 37.4), (64.2, 41.0), (65.0, 45.4), (61.6, 47.4), (58.0, 43.0)]), HAIR.deep, 0.45)]
    part('cap', cap, HAIR, grad=(86, 14, 58, 44, [(0, HAIR.light), (0.4, HAIR.base), (1, HAIR.shadow)]),
         cel=0.9, rim=0.6, cast=1.0, cast_on=['face', 'h1', 'h2', 'h3', 'h3b', 'h4', 'h5', 'hm'], details=hd)

    # ---- les deux plumes, nouées d'une perle d'or derrière l'oreille, couchées le long de la crinière ----
    for name, mat, a, b, c, d, w in (('pl1', FEATR, (63.0, 30.4), (58.0, 27.6), (52.0, 24.6), (45.4, 22.0), 2.6),
                                      ('pl2', FEATO, (62.4, 32.6), (58.0, 31.4), (53.6, 30.6), (48.6, 30.2), 2.3)):
        cpts = crpath([a, b, c, d], 24)
        sh = taper(cpts, w * 0.55, 0.25, tip='sharp', wmid=w * 1.25)
        tipc = mat.hi
        det = [(sh, ('lin', a[0], a[1], d[0], d[1], [(0, mat.shadow), (0.35, mat.base), (0.75, mat.light), (1, tipc)]), 1),
               (under(sh, 0.3, -1.0), mat.deep, 0.45),
               (ribbon(cpts[1:-3], [0.1] + [0.3] * (len(cpts) - 6) + [0.1]), mat.hi, 0.7)]
        # deux petites encoches douces dans les barbes (pas de hachures)
        for t in (0.45, 0.7):
            p = cpts[int(t * 24)]
            det.append((ellipse(p[0], p[1] + 0.8, 0.6, 0.3, -20), mat.deep, 0.5))
        part(name, sh, mat, cel=0, rim=0.4, cast=0.8, cast_on=['cap', 'h1', 'h2', 'h3', 'h3b', 'h4', 'hm', 'pl1'], details=det)
    bead = ellipse(63.2, 31.6, 1.35, 1.4)
    part('bead', bead, GOLD, grad=(64.4, 30.2, 62, 33, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.4, rim=0.3, cast=0.6,
         cast_on=['cap', 'pl1', 'pl2'], details=[(ellipse(63.6, 31.1, 0.4, 0.35), '#ffffff', 0.9)])

    # ---- l'oreille (devant les cheveux de la nuque, sa racine fondue dans la peau), l'anneau d'or ----
    ear = sm([(68.6, 36.2), (66.8, 35.2), (65.1, 36.2), (64.7, 39.0), (65.4, 41.8), (66.8, 43.4), (68.4, 42.8)], t=0.95)
    part('ear', ear, SKIN, grad=(68.6, 36, 64.6, 43, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.6, rim=0.45, cast=0.7,
         cast_on=['cap'],
         details=[(sm([(67.6, 37.0), (66.2, 37.2), (65.9, 39.4), (66.6, 41.6), (67.4, 40.0)], t=0.9), SKIN.deep, 0.55),
                  (ribbon([(66.8, 35.8), (65.6, 37.2), (65.4, 40.0)], [0.1, 0.45, 0.1]), SKIN.light, 0.7)])
    hoop = ring(66.0, 45.5, 1.9, 1.15)
    part('hoop', hoop, GOLD, grad=(67.8, 43.8, 64.2, 47.2, [(0, GOLD.hi), (0.4, GOLD.light), (1, GOLD.shadow)]), cel=0.3, rim=0.3,
         cast=0.6, cast_on=['face', 'cap', 'ear', 'body', 'h5'],
         details=[(ellipse(67.2, 44.6, 0.35, 0.3), '#ffffff', 0.85)])

    fig.pose(names, HEAD)
    return names


def main():
    """ysolde.svg (grand) et ysolde-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/knights-7.webp (512 px de haut) et knights-7-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('ysolde', 0.95, 512, 'knights-7'), ('ysolde-petit', 1.35, 160, 'knights-7-160')):
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
