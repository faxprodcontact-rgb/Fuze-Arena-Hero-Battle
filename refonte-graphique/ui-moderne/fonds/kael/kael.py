# Le fond de combat du clan de KAEL (feu), le volcan, redessiné en VECTORIEL lisse et animé (test du 27/11/2026,
# demande du propriétaire : « On a fait les héros, les monstres, maintenant il faut adapter les fonds en style
# moderne : fais-moi un test graphique sur un fond déjà existant »).
#
# Même composition et mêmes mesures que le fond pixel (refonte-graphique/pixel/fonds/kael/build.py, LISEZMOI.md) :
# une image de 590 × 1100 pixels du fond, plateforme de P0 = 819 à P1 = 1047, rangs 860 / 934 / 1007 ; ce qui compte
# est entre y = 377 et 1100. Le style est celui des héros et monstres vectoriels (ui-moderne/heros/atelier.py) :
# grandes formes simples, dégradés doux, une seule lumière en haut à droite (liseré clair en haut à droite, bande
# d'ombre en bas à gauche), un seul contour sombre seulement sur les plans proches, aucun flou SVG. Le fond reste
# MOINS contrasté et MOINS saturé que les personnages ; la profondeur vient de la brume (le lointain plus clair et
# plus froid).
#
# Ce qu'on voit, du fond vers le devant : le ciel de cendre (violet nuit → rouge braise), le soleil pâle voilé en haut
# à droite, des bancs de fumée ; des crêtes lointaines dans la brume ; le volcan (face droite éclairée), son cratère
# qui rougeoie, ses coulées, son panache qui part vers la gauche ; à gauche une falaise d'où tombe une chute de lave,
# à droite un éperon (une chute sort d'une faille, la stèle d'obsidienne au signe du clan, deux bannières pourpres) ;
# la rivière de lave derrière l'arène ; l'arène : un dallage rectangulaire d'un bord à l'autre, calme ; son flanc,
# la lave qui coule dessous ; deux rochers dans les coins du bas.
# Ce qui bouge : la lueur du cratère, la fumée, les coulées, les deux chutes, la rivière, la lave du bas, les
# bannières, le signe de la stèle, les braises.
# Le signe du clan (inventé, comme le pixel) : une lame pointe en bas dans une flamme ouverte en croissant.
#
#   python3 refonte-graphique/ui-moderne/fonds/kael/kael.py --fixe     # l'image fixe dans le brouillon (pour composer)
#   python3 refonte-graphique/ui-moderne/fonds/kael/kael.py            # images du jeu + calques + test + contrôles
#   python3 refonte-graphique/ui-moderne/fonds/kael/kael.py --video    # en plus : anim.gif et anim.mp4 (≈ 2 min)
#
# Sorties : public/art/vecto/fonds/kael.webp (fixe ×2), kael-anim.webp (planche ×2), fond-kael.json (à côté de ce
# fichier : les calques, format proche de FOND_META) ; pixel/sortie/ui/vecto/fond-kael/ (fond.png, situation.png,
# comparaison.png, anim.gif, anim.mp4, STATUT.txt).
import base64
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'pictos'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from lib import Shape, blob, ellipse, mix, rpoly  # noqa: E402
from atelier import sm, ribbon, bez, resample, sides  # noqa: E402

BROUILLON = os.environ.get('BROUILLON', '/tmp/fonds-brouillon')
TMP = os.path.join(BROUILLON, 'vecto-fond-kael')
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'fond-kael')
JEU = os.path.join(ROOT, 'public', 'art', 'vecto', 'fonds')
RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu-lot.cjs')

# ------------------------------------------------------------------------------------------------ les mesures
W, H = 590, 1100
UP = 2                          # les images du jeu sont rendues ×2 (vectoriel : plus fin que le pixel)
HZ, P0, P1 = 789, 800, 1047      # P0 avancé (819 → 800) : en combat, le rang du fond a ses pieds à 828
RANGS = (860, 934, 1007)
VISIBLE = {'court': 377, 'moyen': 148, 'long': 50}
PERIODE = 19200                 # toutes les boucles divisent cette période : l'aperçu boucle sans couture
                                # (19,2 s : les dragons traversent le ciel lentement, une fois par période)
UNIT = 720 / W
HERO_X_U = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}
ENEMY_X_U = {0: 475, 1: 475, 2: 557, 3: 638, 4: 638}
ROW_OF = {0: 0, 3: 0, 2: 1, 1: 2, 4: 2}


def place(side, slot):
    xs = HERO_X_U if side == 'heros' else ENEMY_X_U
    return int(round(xs[slot] / UNIT)), RANGS[ROW_OF[slot]]


# Le VRAI combat (src/game/battle-scene.ts, fight-view.ts) : le décor y est agrandi ×1,4 (FOND_ZOOM), centré, son bas
# au bas de l'écran (au-dessus de la barre de geste) ; on n'en voit que x = 84 → 506. Les combattants : spreadX,
# ROW_DY (90 / 180 / 270) + FEET (47) sous le haut du sol (= bas de l'image − 430 × 1,4), dessinés à 1,22 × 0,95.
ZOOM = 1.4
UC = 720 / W * ZOOM                                   # unités de jeu par pixel du fond, en combat
OXC = (720 - W * UC) / 2                              # le bord gauche de l'image (unités, négatif : coupé)
VUE_X = (-OXC / UC, (720 - OXC) / UC)                 # 84,3 → 505,7 : ce qu'on voit en largeur
K_PERSO = 1.22 * 0.95 / UC                            # un pixel d'un personnage = 0,68 pixel du fond en combat
ROW_DY = {0: 90, 3: 90, 2: 180, 1: 270, 4: 270}
RANGS_COMBAT = tuple(1100 - (430 * ZOOM - d - 47) / UC for d in (90, 180, 270))     # 828 / 880 / 933
CARTES = 1100 - (14 + 182) / UC                       # 985 : le haut des cartes des héros (tout ce qui est dessous est caché)


def place_combat(side, slot):
    spread = lambda x: (720 - 288) / 2 + (x - 245) * 0.88
    x = spread(HERO_X_U[slot]) if side == 'heros' else 720 - spread(720 - ENEMY_X_U[slot])
    return (x - OXC) / UC, 1100 - (430 * ZOOM - ROW_DY[slot] - 47) / UC


def telephone(w, h, bas=0):
    """Un téléphone (w × h points, `bas` = la barre de geste) : (haut visible du fond, hauteur du jeu en unités)."""
    hu = max(1280, min(1640, round(720 * h / w)))
    return 1100 - (hu - bas * 720 / w) / UC, hu


# ------------------------------------------------------------------------------------------------ les couleurs
# Reprises de Kael et de ses monstres vectoriels (roche violet-brun, lave, pagne pourpre), mais plus sourdes.
INK = '#1f1238'                 # le contour (le raisin de l'interface), seulement sur les plans proches
CIEL = [(0, '#1b0d22'), (0.28, '#2c1230'), (0.52, '#481b35'), (0.70, '#6c2a3a'), (0.84, '#8a3c3e'), (1, '#9a4840')]
FUMEE = dict(base='#4a2335', light='#5c2c3d', rim='#7c4048', sh='#38192c')
LOIN1 = dict(base='#7a4659', light='#86505f', rim='#9a6068', sh='#6c3d54')        # crête la plus lointaine
LOIN2 = dict(base='#5e3046', light='#6a3a4c', rim='#86505a', sh='#4e2840')
VOLC = dict(base='#4f2a3c', light='#6c3a48', rim='#8a5056', sh='#3a1e30')
FAL = dict(base='#3c2a37', light='#4e3843', rim='#7a5c60', sh='#2a1d2b')         # les falaises (plan moyen)
ROC = dict(base='#352632', light='#4a3540', rim='#7a5e60', sh='#241a26')          # les rochers du premier plan
SOL = dict(back='#6c5c62', front='#7a6765')                                         # l'arène : valeur moyenne
LAVE = dict(hot='#ffdc9e', glow='#f8ac5c', mid='#e9803e', deep='#d0532e', dark='#8e2c2a',
            crust='#4a2129', crust_hi='#6e3433')
POURPRE = dict(base='#7a2848', light='#9a3a58', rim='#c0586a', sh='#521a36')
OBSI = dict(base='#2a1c36', light='#3c2c4c', rim='#7a6a96', sh='#1c1226')
CRIST = dict(base='#c4473a', light='#e8704a', rim='#ffb48a', sh='#7a2236')


def fm(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


# ------------------------------------------------------------------------------------------------ le document SVG
class Doc:
    """Un dessin SVG : collecte les dégradés, masques et symboles (defs) ; chaque fonction de dessin rend du texte."""

    def __init__(self):
        self.defs = []
        self.n = 0

    def uid(self, p):
        self.n += 1
        return '%s%d' % (p, self.n)

    @staticmethod
    def _stops(stops):
        return ''.join('<stop offset="%g" stop-color="%s"%s/>' % (
            s[0], s[1], (' stop-opacity="%g"' % s[2]) if len(s) > 2 else '') for s in stops)

    def lin(self, x1, y1, x2, y2, stops):
        i = self.uid('l')
        self.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s'
                         '</linearGradient>' % (i, fm(x1), fm(y1), fm(x2), fm(y2), self._stops(stops)))
        return 'url(#%s)' % i

    def rad(self, cx, cy, r, stops, ry=None):
        i = self.uid('r')
        tr = ''
        if ry is not None and ry != r:
            tr = ' gradientTransform="translate(%s %s) scale(1 %s) translate(%s %s)"' % (
                fm(cx), fm(cy), fm(ry / r), fm(-cx), fm(-cy))
        self.defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s"%s>%s'
                         '</radialGradient>' % (i, fm(cx), fm(cy), fm(r), tr, self._stops(stops)))
        return 'url(#%s)' % i

    def minus(self, d, dx, dy):
        """Un masque : la forme moins elle-même décalée de (dx, dy) (une bande le long d'un bord)."""
        i = self.uid('m')
        self.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-200" y="-200" width="1000" height="1500">'
                         '<path d="%s" fill="#fff"/><path d="%s" fill="#000" transform="translate(%s %s)"/></mask>'
                         % (i, d, d, fm(dx), fm(dy)))
        return 'url(#%s)' % i

    def clip(self, d, evenodd=False):
        i = self.uid('c')
        self.defs.append('<clipPath id="%s"><path d="%s"%s/></clipPath>' % (
            i, d, ' clip-rule="evenodd"' if evenodd else ''))
        return 'url(#%s)' % i

    def svg(self, body, box, size=None):
        x, y, w, h = box
        sz = ' width="%s" height="%s"' % (fm(size[0]), fm(size[1])) if size else ''
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s"%s><defs>%s</defs>%s</svg>'
                % (fm(x), fm(y), fm(w), fm(h), sz, ''.join(self.defs), body))


EO = ' fill-rule="evenodd"'


def D(s):
    return s if isinstance(s, str) else s.d()


def path(d, fill, op=1.0, extra=''):
    return '<path d="%s" fill="%s"%s%s/>' % (D(d), fill, '' if op == 1 else ' opacity="%g"' % op, extra)


def vol(doc, shape, m, grad=None, r=1.6, c=2.4, ink=None, iw=1.0, rim_op=0.9, sh_op=0.85):
    """Un volume dans le style des héros : dégradé (clair en haut à droite), bande d'ombre nette en bas à gauche,
    liseré de lumière en haut à droite ; `ink` : le contour (plans proches seulement)."""
    d = D(shape)
    xs = [p[0] for p in shape.pts()] if not isinstance(shape, str) else [0, W]
    ys = [p[1] for p in shape.pts()] if not isinstance(shape, str) else [0, H]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    out = []
    if ink:
        out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
            d, ink, ink, fm(2 * iw)))
    g = grad or doc.lin(x1, y0, x0 + (x1 - x0) * 0.25, y1, [(0, m['light']), (0.55, m['base']), (1, m['sh'])])
    out.append(path(d, g))
    if c:
        out.append('<path d="%s" fill="%s" opacity="%g" mask="%s"/>' % (d, m['sh'], sh_op, doc.minus(d, c * 0.8, -c)))
    if r:
        out.append('<path d="%s" fill="%s" opacity="%g" mask="%s"/>' % (d, m['rim'], rim_op, doc.minus(d, -r * 0.75, r)))
    return ''.join(out)


def polyline_d(pts):
    return 'M' + ' L'.join('%s %s' % (fm(x), fm(y)) for x, y in pts)


def length(pts):
    return sum(math.dist(pts[i - 1], pts[i]) for i in range(1, len(pts)))


def lobes_shape(x0, x1, yb, lobes, sag=3):
    """Un banc de fumée : dessous presque plat, dessus en lobes ronds (lobes = [(cx, cy, r)] de droite à gauche)."""
    pts = [(x0, yb - 2), (x0 + (x1 - x0) * 0.3, yb + sag), (x0 + (x1 - x0) * 0.7, yb + sag * 0.6), (x1, yb - 2)]
    sharp = []
    for k, (cx, cy, r) in enumerate(lobes):
        if k > 0:
            sharp.append(len(pts))
        for a in (5, 50, 90, 130, 175):
            ra = math.radians(a)
            pts.append((cx + r * math.cos(ra), cy - r * math.sin(ra)))
    return sm(pts, sharp=tuple(sharp), t=0.9)


# ------------------------------------------------------------------------------------------------ les profils
def interp(pts, x):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if xa <= x <= xb:
            return ya + (yb - ya) * (x - xa) / ((xb - xa) or 1)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]


# La falaise de gauche est plus basse que dans le pixel (les dragons passent au-dessus) ; l'éperon de droite est
# avancé de 18 pixels vers le milieu (le combat coupe les bords : on voit x = 84 → 506).
FAL_G_HAUT = [(-14, 536), (14, 530), (44, 526), (72, 530), (96, 538), (110, 544), (126, 545), (142, 540),
              (160, 538), (176, 546)]
FAL_G_FACE = [(184, 572), (182, 612), (190, 650), (186, 690), (196, 730), (214, 776)]
FAL_D_DX = -18
FAL_D_FACE = [(x + FAL_D_DX, y) for x, y in
              [(418, 776), (424, 730), (414, 690), (424, 648), (418, 604), (430, 570)]]
FAL_D_HAUT = [(x + FAL_D_DX, y) for x, y in
              [(442, 556), (468, 551), (494, 547), (520, 545), (548, 540), (576, 543), (604, 538)]] + [(604, 538)]


def sol_g(x):
    return interp(FAL_G_HAUT, x)


def sol_d(x):
    return interp(FAL_D_HAUT, x)


# ================================================================================================ LES ÉLÉMENTS
# Chaque élément : id, profondeur (plans du pixel : ciel −29, derrière −25, paysage −20, devant −15, premier 1300),
# genre ('fixe' : dans l'image fixe seulement ; 'boucle' ; 'morceau' = une boucle d'une image remise par-dessus ;
# 'defile' ; 'particules') et sa fonction de dessin.
ELEMS = []


def element(id, prof, genre, **kw):
    if 'box' in kw:
        kw['box'] = tuple(int(round(v)) for v in kw['box'])
    e = dict(id=id, prof=prof, genre=genre, fn=None, **kw)
    ELEMS.append(e)

    def deco(fn):
        e['fn'] = fn
        return fn
    return deco


# ---------------------------------------------------------------------------------------------------- le ciel
SOLEIL = (450, 388)          # vu sur tous les téléphones (le court montre le fond à partir de y = 351), à droite des pilules


@element('ciel', -29.9, 'fixe')
def ciel(doc):
    out = [path('M-20 -20H610V840H-20Z', doc.lin(0, 0, 0, 830, CIEL))]
    # la lueur rouge de l'horizon, derrière le volcan
    out.append('<ellipse cx="340" cy="740" rx="360" ry="190" fill="%s"/>' % doc.rad(
        340, 740, 360, [(0, '#b4553e', 0.45), (0.5, '#a04a3e', 0.2), (1, '#8a3c3e', 0)], ry=190))
    # le soleil pâle voilé de cendre, en haut à droite (la seule lumière)
    sx, sy = SOLEIL
    out.append('<circle cx="%d" cy="%d" r="120" fill="%s"/>' % (sx, sy, doc.rad(
        sx, sy, 120, [(0, '#f4c48c', 0.30), (0.35, '#d88a6a', 0.14), (1, '#a04a4e', 0)])))
    out.append('<circle cx="%d" cy="%d" r="21" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 6, sy - 6, 26, [(0, '#fff2d0'), (0.7, '#f8d8a4'), (1, '#e8b48a')])))
    return ''.join(out)


@element('nuages', -29.5, 'fixe')
def nuages(doc):
    out = []
    # A : le grand banc en haut à gauche, où le panache du volcan se perd (le haut des téléphones longs)
    a = lobes_shape(-30, 320, 330, [(292, 318, 18), (254, 300, 30), (206, 284, 38), (152, 274, 40), (96, 266, 44),
                                    (42, 270, 40), (-6, 282, 38), (-30, 300, 30)], sag=6)
    out.append(vol(doc, a, FUMEE, r=2.2, c=4))
    a2 = lobes_shape(-30, 250, 232, [(232, 222, 16), (196, 208, 26), (150, 196, 30), (100, 192, 32), (50, 196, 30),
                                     (4, 204, 28), (-30, 216, 20)], sag=4)
    out.append(vol(doc, a2, dict(FUMEE, base='#3f1d30', light='#4c2436', sh='#311629'), r=2, c=3.5))
    # B : en haut à droite
    b = lobes_shape(380, 620, 292, [(612, 280, 16), (578, 268, 22), (540, 262, 22), (500, 266, 20), (460, 272, 18),
                                    (414, 280, 14)], sag=3)
    out.append(vol(doc, b, FUMEE, r=2, c=3))
    # C : un petit banc au-dessus du soleil (il le voile un peu), E : un petit à gauche, sous le banc A
    c = lobes_shape(452, 620, 330, [(610, 322, 12), (578, 312, 16), (540, 310, 15), (500, 316, 13), (470, 322, 9)],
                    sag=2)
    out.append(vol(doc, c, dict(FUMEE, base='#55283a', light='#64303f'), r=1.8, c=2.6))
    e = lobes_shape(90, 214, 372, [(204, 366, 9), (176, 358, 13), (140, 356, 14), (106, 362, 11)], sag=2)
    out.append(vol(doc, e, dict(FUMEE, base='#55283a', light='#64303f'), r=1.8, c=2.6))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
@element('lointain', -28.5, 'fixe')
def lointain(doc):
    out = []
    r1 = [(-20, 800), (-20, 668), (20, 650), (60, 662), (110, 682), (150, 676), (190, 690), (240, 700), (300, 706),
          (400, 690), (430, 664), (470, 642), (510, 652), (550, 664), (610, 650), (610, 800)]
    out.append(vol(doc, sm(r1, sharp=(0, 1, len(r1) - 2, len(r1) - 1), t=0.7), LOIN1, r=1.4, c=0))
    # deux aiguilles de roche dans la brume, posées sur la crête
    for x, h_, w_ in ((232, 40, 9), (414, 32, 8)):
        y = 706 if x < 300 else 694
        s = sm([(x - w_, y + 6), (x - w_ * 0.5, y - h_ * 0.6), (x - 1, y - h_), (x + 2, y - h_ + 2),
                (x + w_ * 0.55, y - h_ * 0.5), (x + w_, y + 6)], sharp=(0, 5), t=0.8)
        out.append(vol(doc, s, LOIN2, r=1.2, c=1.6))
    r2 = [(-20, 800), (-20, 724), (40, 716), (110, 730), (180, 738), (260, 744), (330, 742), (420, 734),
          (480, 722), (540, 728), (610, 718), (610, 800)]
    out.append(vol(doc, sm(r2, sharp=(0, 1, len(r2) - 2, len(r2) - 1), t=0.7), LOIN2, r=1.4, c=0))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le volcan
VOLCAN = [(70, 792), (150, 738), (214, 668), (258, 600), (288, 532), (308, 478), (320, 450), (330, 441),
          (346, 445), (364, 441), (376, 440), (388, 452), (402, 490), (428, 552), (464, 618), (510, 684),
          (570, 742), (640, 792)]
COULEES = [
    # (points du centre, largeurs) : de la lèvre du cratère vers le bas, en lacets
    ([(328, 444), (323, 462), (316, 482), (312, 502), (305, 522), (302, 544), (296, 566)],
     [5.0, 6.2, 5.4, 6.0, 4.8, 4.0, 1.4]),
    ([(374, 444), (379, 464), (385, 486), (391, 510), (399, 534), (407, 558), (416, 582), (426, 606)],
     [5.4, 6.4, 5.6, 6.2, 5.6, 4.8, 3.8, 2.0]),
    ([(352, 446), (356, 460), (353, 474), (357, 490)], [3.8, 3.6, 3.0, 1.2]),
]


def catmull(pts, n=6):
    """Une ligne douce passant par les points (Catmull-Rom), n points par segment."""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def coulee_ligne(k, n=24):
    pts, ws = COULEES[k]
    c = resample(catmull(pts), n)
    wl = []
    for i in range(n + 1):
        f = i / n * (len(ws) - 1)
        j = min(len(ws) - 2, int(f))
        wl.append(ws[j] + (ws[j + 1] - ws[j]) * (f - j))
    return c, wl


# Le volcan (cône, panache, cratère, coulées) est dessiné dans ses coordonnées d'origine puis décalé : un peu à
# gauche et plus bas, pour qu'il soit au milieu de ce que montre le combat (x = 84 → 506) et sous les pilules du haut.
VDX, VDY = -24, 10


def vgroupe(body):
    return '<g transform="translate(%d %d)">%s</g>' % (VDX, VDY, body)


def vbox(x, y, w, h):
    return (x + VDX, y + VDY, w, h)


@element('volcan', -28, 'fixe')
def volcan(doc):
    return vgroupe(volcan_brut(doc))


def volcan_brut(doc):
    out = []
    s = sm(VOLCAN, sharp=(0, 6, 7, 9, 10, len(VOLCAN) - 1), t=0.8)
    g = doc.lin(470, 470, 250, 640, [(0, VOLC['light']), (0.5, VOLC['base']), (1, VOLC['sh'])])
    out.append(vol(doc, s, VOLC, grad=g, r=2.0, c=3.4))
    clip = doc.clip(s.d())
    inner = []
    # les grands pans du cône : des ravines douces côté ombre, des arêtes claires côté lumière (peu, irrégulières)
    for pts, w_, col, op in (
            ([(318, 470), (300, 520), (276, 590), (250, 650), (222, 702)], [3, 6, 9, 10, 8], VOLC['sh'], 0.55),
            ([(338, 462), (330, 520), (318, 590), (310, 660), (300, 740)], [2, 5, 8, 11, 12], VOLC['sh'], 0.35),
            ([(392, 470), (408, 520), (430, 580), (458, 640), (492, 700)], [2, 4, 6, 6, 4], VOLC['rim'], 0.28),
            ([(370, 470), (376, 540), (384, 610), (392, 680)], [1.5, 4, 6, 5], VOLC['light'], 0.45)):
        inner.append(path(ribbon(resample(pts, 12), [w_[min(len(w_) - 1, int(i * len(w_) / 13))] for i in range(13)]),
                          col, op))
    # la lueur du cratère sur le haut du cône (la lave chauffe la roche tout près)
    inner.append('<ellipse cx="350" cy="452" rx="70" ry="44" fill="%s"/>' % doc.rad(
        350, 452, 70, [(0, '#c4523a', 0.55), (0.6, '#8a3a3c', 0.18), (1, '#6c2a3a', 0)], ry=44))
    # le halo des coulées (fixe : la lave ne fait que couler, la lueur reste)
    for k in range(len(COULEES)):
        c, wl = coulee_ligne(k)
        inner.append(path(ribbon(c, [w * 3.0 for w in wl]), '#e0643a', 0.16))
    # la brume du pied (le cône se fond dans l'horizon)
    inner.append(path('M0 600H600V800H0Z', doc.lin(0, 620, 0, 790, [(0, '#8a3c3e', 0), (1, '#9a4a40', 0.7)])))
    out.append('<g clip-path="%s">%s</g>' % (clip, ''.join(inner)))
    return ''.join(out)


@element('panache', -29.6, 'fixe')
def panache(doc):
    return vgroupe(panache_brut(doc))


def panache_brut(doc):
    """Le grand panache fixe : il sort de derrière la lèvre du cratère, monte et part vers la gauche, jusqu'au banc
    de fumée (qui le recouvre). Une seule forme (des volutes réunies), éclairée en haut à droite."""
    c = resample(bez((352, 446), (350, 396), (306, 346), (196, 262)), 36)
    s = None
    for i, (x, y) in enumerate(c):
        u = i / 36
        r = 11 + 44 * u ** 1.15
        a = math.sin(i * 0.9)
        ox, oy = r * 0.16 * a, -r * 0.06 * math.cos(i * 1.3)
        e = ellipse(x + ox, y + oy, r, r * 0.92)
        s = e if s is None else s + e
    g = doc.lin(420, 330, 240, 380, [(0, '#5e2c3c'), (0.5, '#4c2435'), (1, '#3f1d30')])
    out = [vol(doc, s, FUMEE, grad=g, r=2.6, c=4.5)]
    out.append('<g clip-path="%s"><ellipse cx="352" cy="430" rx="46" ry="40" fill="%s"/></g>' % (
        doc.clip(s.d()), doc.rad(352, 430, 46, [(0, '#b04a3c', 0.75), (1, '#7a3040', 0)], ry=40)))
    return ''.join(out)


def cratere(doc, ph):
    return vgroupe(cratere_brut(doc, ph))


def cratere_brut(doc, ph):
    """La lèvre du cratère et sa lueur qui respire (doucement : une montée et une descente par boucle)."""
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    out = ['<ellipse cx="352" cy="438" rx="%s" ry="%s" fill="%s"/>' % (
        fm(38 + 6 * k), fm(20 + 3 * k), doc.rad(352, 438, 44, [(0, '#ff9a4a', 0.38 + 0.2 * k),
                                                                (0.55, '#e0643a', 0.16 + 0.08 * k),
                                                                (1, '#c04a3a', 0)], ry=24))]
    # on voit le sommet d'en dessous : pas l'intérieur du cratère, seulement la lave qui affleure à la lèvre
    lip = sm([(324, 444), (336, 439), (352, 438.5), (366, 437.5), (382, 441), (368, 442.6), (352, 443), (336, 444.2)],
             sharp=(0, 4), t=0.9)
    out.append(path(lip, doc.lin(326, 440, 380, 442, [(0, LAVE['deep']), (0.35, LAVE['mid']),
                                                       (0.7, mix(LAVE['glow'], LAVE['hot'], 0.4 * k)),
                                                       (1, LAVE['mid'])])))
    return ''.join(out)


element('cratere', -26, 'boucle', box=vbox(306, 412, 92, 54), n=8, ms=600)(cratere)


def fumee_image(doc, i, n):
    """Une bouffée de fumée (une image de sa vie) : elle grossit et s'efface."""
    t = i / (n - 1)
    r = 6 + 12 * t
    op = min(1, 0.4 + 2 * t) if t < 0.5 else (1 - (t - 0.5) / 0.5) ** 1.2 * 0.92 + 0.08
    cx = cy = 20
    s = lobes_shape(cx - r * 1.3, cx + r * 1.3, cy + r * 0.55, [(cx + r * 0.6, cy - r * 0.05, r * 0.62),
                                                              (cx - 0.1 * r, cy - r * 0.3, r * 0.8),
                                                              (cx - r * 0.75, cy + r * 0.05, r * 0.55)], sag=r * 0.12)
    m = dict(base=mix('#5c2b3b', '#4c2435', t), light=mix('#6e3444', '#5a2a3b', t), rim=mix('#8a4a52', '#74404a', t),
             sh='#3f1d30')
    return '<g opacity="%g">%s</g>' % (op * 0.8, vol(doc, s, m, r=0.8, c=0, rim_op=0.6))


element('fumee', -25, 'particules', taille=(40, 40), images=7, dessin=fumee_image, zone=(316, 436, 338, 446),
        nombre=7, vie=(4200, 5200), vx=(-11, -5), vy=(-15, -10), ondule=(2.5, 2400))


def coulee_masque():
    """Les coulées passent derrière l'éperon de droite : on les coupe là où il commence."""
    return 'M240 436H460V650H240Z' + sm([(424, 556), (412, 570), (400, 604), (406, 648), (402, 662), (462, 662),
                                         (462, 540)], sharp=(4, 5, 6), t=0.75).d()


def le_long(c, u):
    """Le point à la fraction u (0..1) d'une ligne échantillonnée régulièrement."""
    f = u * (len(c) - 1)
    k = min(len(c) - 2, int(f))
    t = f - k
    return (c[k][0] + (c[k + 1][0] - c[k][0]) * t, c[k][1] + (c[k + 1][1] - c[k][1]) * t)


def coulee(k):
    def fn(doc, ph):
        pts, ws = COULEES[k]
        c, wl = coulee_ligne(k)
        body = ribbon(c, wl)
        out = [path(body, doc.lin(c[0][0], c[0][1], c[-1][0], c[-1][1],
                                  [(0, LAVE['glow']), (0.45, LAVE['mid']), (1, LAVE['deep'])]))]
        # des taches plus chaudes qui glissent vers le bas (une longueur entière par boucle : sans couture)
        inner = []
        for j, (s0, rr) in enumerate(((0.0, 1.0), (0.37, 0.8), (0.61, 1.1), (0.83, 0.7))):
            u = (s0 + ph) % 1
            x, y = le_long(c, u)
            w = max(ws) * rr * (1.2 - 0.6 * u)
            inner.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(x), fm(y), fm(w * 0.9), fm(w * 1.8), doc.rad(x, y, w * 0.9, [
                    (0, LAVE['hot'], 0.75), (1, LAVE['glow'], 0)], ry=w * 1.8)))
        out.append('<g clip-path="%s">%s</g>' % (doc.clip(body.d()), ''.join(inner)))
        return '<g clip-path="%s">%s</g>' % (doc.clip(coulee_masque(), evenodd=True), vgroupe(''.join(out)))
    return fn


element('coulee-g', -24, 'boucle', box=vbox(286, 438, 50, 134), n=12, ms=200)(coulee(0))
element('coulee-d', -24, 'boucle', box=vbox(364, 438, 72, 180), n=12, ms=200)(coulee(1))
element('coulee-c', -24, 'boucle', box=vbox(345, 440, 18, 54), n=12, ms=200)(coulee(2))


@element('brume', -23, 'fixe')
def brume(doc):
    # la brume chaude de l'horizon passe devant le lointain et le pied du volcan (pas devant les falaises)
    return path('M-10 636H600V800H-10Z', doc.lin(0, 636, 0, 792, [(0, '#9a4a42', 0), (0.7, '#a2503f', 0.32),
                                                                  (1, '#a85440', 0.5)]))


# ---------------------------------------------------------------------------------------------------- les falaises
def falaise_g_forme():
    pts = [(-14, 790)] + FAL_G_HAUT + FAL_G_FACE + [(220, 790)]
    return sm(pts, sharp=(0, 1, len(pts) - 1), t=0.75)


def falaise_d_forme():
    pts = FAL_D_FACE + FAL_D_HAUT + [(604, 790)]
    return sm(pts, sharp=(len(pts) - 2, len(pts) - 1, 0), t=0.75)


def cristaux(doc, x, y, k=1.0, flip=False):
    """Une touffe de trois cristaux posée au sol en (x, y) (pied), lumière en haut à droite."""
    out = []
    sg = -1 if flip else 1
    for dx, h_, w_, ang in ((-5, 14, 4.2, -18), (3, 22, 5.2, 6), (9, 11, 3.6, 26)):
        a = math.radians(ang * sg)
        bx, by = x + dx * k * sg, y
        def P(u, v):
            return (bx + (u * math.cos(a) - v * math.sin(a)) * k, by + (u * math.sin(a) + v * math.cos(a)) * k)
        pts = [P(-w_, 2), P(-w_, -h_ * 0.62), P(0, -h_), P(w_, -h_ * 0.62), P(w_, 2)]
        s = rpoly(pts, 0.6)
        out.append(vol(doc, s, CRIST, r=1.1, c=1.6, ink=INK, iw=0.8))
        face = rpoly([P(0, -h_), P(w_, -h_ * 0.62), P(w_, 2), P(0, 2)], 0.4)
        out.append(path(face, CRIST['light'], 0.55))
    # un socle de cailloux (le pied est posé)
    out.append(vol(doc, sm([(x - 11 * k, y + 2), (x - 6 * k, y - 3 * k), (x + 6 * k, y - 3.5 * k), (x + 13 * k, y + 2)],
                           sharp=(0, 3), t=0.8), ROC, r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


CORN_G = [[(20, 640), (60, 634), (98, 642), (134, 652)], [(126, 712), (156, 706), (194, 716)]]
CORN_D = [[(486, 640), (530, 630), (576, 636), (606, 630)], [(422, 708), (452, 700), (478, 706)]]


@element('falaises', -20, 'fixe')
def falaises(doc):
    out = []
    for forme, droite in ((falaise_g_forme(), False), (falaise_d_forme(), True)):
        xs = [p[0] for p in forme.pts()]
        x0, x1 = min(xs), max(xs)
        g = doc.lin(x1, 500, x0 + 20, 780, [(0, FAL['light']), (0.45, FAL['base']), (1, FAL['sh'])])
        out.append(vol(doc, forme, FAL, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0))
        inner = []
        if not droite:
            # la face de droite (tournée vers la lumière), un grand pan plus clair ; une fente côté ombre
            inner.append(path(sm([(150, 560), (178, 548), (186, 580), (182, 620), (190, 660), (198, 720),
                                  (212, 780), (170, 780), (160, 690), (156, 630)], t=0.8), FAL['light'], 0.7))
            inner.append(path(ribbon(resample([(52, 572), (46, 620), (54, 670), (42, 730)], 12),
                                     [0.4, 1.6, 2.4, 2.8, 3.0, 2.8, 2.6, 2.2, 2, 1.6, 1.2, 0.8, 0.3]), FAL['sh'], 0.8))
            inner.append(path(sm([(-14, 600), (40, 640), (70, 720), (60, 790), (-14, 790)], t=0.8), FAL['sh'], 0.45))
        else:
            inner.append('<g transform="translate(%d 0)">' % FAL_D_DX)
            inner.append(path(sm([(500, 560), (640, 548), (640, 680), (560, 700), (520, 650)], t=0.8),
                              FAL['light'], 0.55))
            inner.append(path(ribbon(resample([(470, 580), (476, 640), (466, 700), (472, 760)], 12),
                                     [0.4, 1.4, 2.2, 2.6, 2.8, 2.6, 2.4, 2.2, 2, 1.6, 1.2, 0.8, 0.3]), FAL['sh'], 0.8))
            inner.append(path(sm([(416, 610), (446, 640), (452, 720), (440, 790), (416, 790)], t=0.8), FAL['sh'], 0.5))
            # la faille d'où sort la chute de droite : une bouche sombre, rougie dedans
            inner.append(path(sm([(426, 640), (434, 630), (446, 634), (450, 648), (440, 654), (428, 652)], t=0.9),
                              '#1c1222'))
            inner.append('<ellipse cx="439" cy="646" rx="9" ry="6" fill="%s"/>' % doc.rad(
                439, 646, 9, [(0, '#e06a3a', 0.9), (1, '#8a2c2a', 0)], ry=6))
        # deux corniches par falaise : un dessus éclairé, une ombre douce dessous (de grandes marches, pas des rayures)
        for pts in (CORN_D if droite else CORN_G):
            c = resample(catmull(pts), 16)
            n_ = len(c) - 1
            wl = [0.6 + 7 * math.sin(math.pi * i / n_) ** 0.8 for i in range(n_ + 1)]
            inner.append(path(ribbon([(x, y + 4) for x, y in c], wl), FAL['sh'], 0.55))
            inner.append(path(ribbon(c, [w * 0.4 for w in wl]), FAL['rim'], 0.45))
        if droite:
            inner.append('</g>')
        # la lave d'en bas chauffe le pied des falaises (lumière douce, tout près de la rivière)
        inner.append(path('M-20 700H610V800H-20Z', doc.lin(0, 712, 0, 790, [(0, '#c0523a', 0), (1, '#d0603e', 0.35)])))
        out.append('<g clip-path="%s">%s</g>' % (doc.clip(forme.d()), ''.join(inner)))
    # des cristaux de feu posés sur la falaise de gauche, et au pied de l'éperon
    out.append(cristaux(doc, 160, sol_g(160) + 1, 0.9))
    out.append(cristaux(doc, 154, 707, 0.75))
    out.append(cristaux(doc, 442, 702, 0.7, flip=True))
    # la stèle (avec son signe) et les bannières (avec leurs mâts) sont des calques : ils passent devant les dragons
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le clan
STELE = (461, sol_d(461))


def stele(doc):
    x, y = STELE
    s = sm([(x - 12, y + 2), (x - 12, y - 34), (x - 8, y - 44), (x, y - 49), (x + 8, y - 44), (x + 12, y - 34),
            (x + 12, y + 2)], sharp=(0, 6), t=0.8)
    out = [vol(doc, s, OBSI, r=1.6, c=2.4, ink=INK, iw=1.0)]
    # un reflet net vertical sur le bord droit (verre noir)
    out.append(path(ribbon(resample([(x + 7, y - 40), (x + 9, y - 26), (x + 9, y - 10)], 8),
                           [0.2, 0.9, 1.4, 1.6, 1.6, 1.4, 1.1, 0.7, 0.2]), '#9a8ab8', 0.6))
    out.append(vol(doc, rpoly([(x - 15, y + 4), (x - 14, y - 2), (x + 14, y - 3), (x + 16, y + 4)], 1.5), ROC,
                   r=0.9, c=1.2, ink=INK, iw=0.9))
    return ''.join(out)


def signe_forme(cx, cy, k):
    """Le signe de Kael : une flamme à trois langues traversée par une lame pointe en bas (la lame se lit en creux
    dans la flamme, puis pleine dessous) ; aucune lettre, ni anneau ni barre (rien qui rappelle une ancre)."""
    def P(u, v):
        return (cx + u * k, cy + v * k)
    flamme = sm([P(0, 2.4), P(-3.4, 1.2), P(-4.4, -1.6), P(-3.6, -4.4), P(-4.4, -6.8), P(-2.0, -4.8), P(-1.2, -5.8),
                 P(0.2, -9.0), P(1.4, -5.8), P(2.2, -4.8), P(4.6, -6.6), P(3.8, -4.4), P(4.6, -1.6), P(3.4, 1.2)],
                sharp=(4, 7, 10), t=0.85)
    lame = rpoly([P(-0.95, -3.4), P(0.95, -3.4), P(0.85, 4.6), P(0, 7.2), P(-0.85, 4.6)], 0.25)
    return flamme + lame


def signe(doc, ph):
    x, y = STELE
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    out = [stele(doc)]
    out.append('<ellipse cx="%s" cy="%s" rx="11" ry="13" fill="%s"/>' % (x, y - 24, doc.rad(
        x, y - 24, 11, [(0, '#ff8a3a', 0.25 + 0.25 * k), (1, '#ff6a2a', 0)], ry=13)))
    out.append(path(signe_forme(x, y - 22, 1.45), mix(LAVE['deep'], LAVE['glow'], 0.35 + 0.55 * k), extra=EO))
    return ''.join(out)


element('signe', -19, 'boucle', box=(STELE[0] - 18, STELE[1] - 53, 36, 60), n=12, ms=400)(signe)

MATS = [(100, sol_g(100)), (433, sol_d(433)), (492, sol_d(492))]
MAT_H = 52


def mat(doc, x, y):
    out = [vol(doc, rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6),
               dict(base='#4a3438', light='#6a4c4c', rim='#a08070', sh='#2e2028'), r=0.7, c=0.8, ink=INK, iw=0.7)]
    out.append(vol(doc, rpoly([(x - 13, y - MAT_H + 2), (x + 13, y - MAT_H + 2), (x + 13, y - MAT_H + 5),
                               (x - 13, y - MAT_H + 5)], 1.2),
                   dict(base='#4a3438', light='#6a4c4c', rim='#a08070', sh='#2e2028'), r=0.7, c=0.8, ink=INK, iw=0.7))
    out.append('<circle cx="%s" cy="%s" r="2.6" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        x, y - MAT_H - 1, doc.rad(x + 1, y - MAT_H - 2, 3, [(0, '#ffe3a0'), (1, '#d08a3a')]), INK))
    out.append(vol(doc, rpoly([(x - 6, y + 3), (x - 5, y - 2), (x + 5, y - 2.5), (x + 7, y + 3)], 1.2), ROC,
                   r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


def banniere(k):
    x, y = MATS[k]
    top = y - MAT_H + 5

    def fn(doc, ph):
        # la toile pend sous la traverse ; elle ondule doucement (plus en bas qu'en haut), le vent vient de la droite
        L, w_ = 34, 22
        a = 2 * math.pi * ph

        def P(u, v):          # u : -1..1 en travers, v : 0..1 en descendant
            sway = v ** 1.5 * (2.4 * math.sin(a + v * 2.2 + k) - 1.2)
            return (x + u * w_ / 2 * (1 - 0.08 * v) + sway, top + v * L + 0.8 * math.sin(a * 1 + u * 1.5 + k) * v)
        pts = [P(-1, 0), P(1, 0)]
        for v in (0.33, 0.66, 0.92):
            pts.append(P(1, v))
        pts += [P(1, 1.04), P(0.5, 0.9), P(0, 1.08), P(-0.5, 0.9), P(-1, 1.04)]
        for v in (0.92, 0.66, 0.33):
            pts.append(P(-1, v))
        s = sm(pts, sharp=(0, 1, 5, 7, 9), t=0.6)
        out = [mat(doc, x, y), vol(doc, s, POURPRE, r=1.3, c=2.0, ink=INK, iw=0.9)]
        sx, sy = P(0, 0.45)
        out.append(path(signe_forme(sx, sy + 1, 1.2), '#e8a45a', extra=EO))
        return ''.join(out)
    return fn


for _k in range(3):
    _x, _y = MATS[_k]
    element('banniere%d' % (_k + 1), -16, 'boucle', box=(_x - 20, _y - MAT_H - 5, 40, MAT_H + 10), n=12,
            ms=200)(banniere(_k))


# ---------------------------------------------------------------------------------------------------- les chutes
CHUTES = [
    # (haut, bas, largeur en haut, en bas)
    ((118, 547), (114, 764), 22, 30),
    ((421, 646), (419, 764), 13, 18),
]


def chute(k, n_):
    (xt, yt), (xb, yb), wt, wb = CHUTES[k]

    def fn(doc, ph):
        c = resample(bez((xt, yt), (xt + 3, yt + 10), (xb, yb - (yb - yt) * 0.6), (xb, yb)), 20)
        ws = [(wt + (wb - wt) * (i / 20) ** 0.7) * (1 + 0.07 * math.sin(i * 1.35 + k) + 0.05 * math.sin(i * 2.9))
              + 4 * max(0, 1 - i / 2.5) for i in range(21)]
        left, right = sides(c, ws)
        # la lèvre en haut, arrondie ; le pied s'évase dans la rivière
        body = sm(left + [(xb + wb * 0.62, yb + 2), (xb, yb + 4), (xb - wb * 0.62, yb + 2)] + right[::-1], t=0.8)
        out = [path(body, doc.lin(xt + wt / 2, yt, xt - wt / 2, yb,
                                  [(0, LAVE['glow']), (0.25, LAVE['mid']), (0.85, LAVE['mid']), (1, LAVE['deep'])]))]
        cl = doc.clip(body.d())
        inner = []
        # le bord gauche (côté ombre) un peu plus sombre, sans bande claire le long des bords
        inner.append('<path d="%s" fill="%s" opacity="0.6" mask="%s"/>' % (body.d(), LAVE['deep'],
                                                                             doc.minus(body.d(), wt * 0.22, 0)))
        # des paquets de lave qui descendent : taches allongées et douces, chaudes ou plus sombres (croûte), à des
        # places et des tailles différentes ; chacune fait un tour entier (ou deux) par boucle : sans couture
        span = yb - yt
        for j, (u, s0, tours, ln, col, op) in enumerate((
                (-0.22, 0.00, 1, 0.20, LAVE['hot'], 0.55), (0.18, 0.13, 1, 0.14, LAVE['hot'], 0.45),
                (0.02, 0.31, 1, 0.24, LAVE['glow'], 0.6), (-0.10, 0.52, 1, 0.16, LAVE['hot'], 0.5),
                (0.24, 0.66, 1, 0.20, LAVE['glow'], 0.55), (-0.26, 0.80, 1, 0.12, LAVE['glow'], 0.5),
                (0.10, 0.90, 1, 0.18, LAVE['hot'], 0.4),
                (0.12, 0.22, 1, 0.16, LAVE['dark'], 0.28), (-0.16, 0.70, 1, 0.14, LAVE['dark'], 0.24))):
            v = (s0 + ph * tours) % 1
            y = yt - span * ln * 0.5 + v * span * (1 + ln)
            f = min(1, max(0, (y - yt) / span))
            w = wt + (wb - wt) * f ** 0.7
            x = xt + (xb - xt) * f + u * w
            rx, ry = w * (0.16 + 0.05 * (j % 3)), span * ln * 0.5
            inner.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(x), fm(y), fm(rx), fm(ry), doc.rad(x, y, rx, [(0, col, op), (0.6, col, op * 0.5), (1, col, 0)],
                                                       ry=ry)))
        # le haut, là où la lave passe la lèvre : plus chaud
        inner.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(xt), fm(yt + 3), fm(wt * 0.6), fm(wt * 0.3), doc.rad(xt, yt + 3, wt * 0.6, [
                (0, LAVE['hot'], 0.9), (1, LAVE['glow'], 0)], ry=wt * 0.3)))
        out.append('<g clip-path="%s">%s</g>' % (cl, ''.join(inner)))
        # le pied qui bouillonne : un bourrelet clair qui gonfle et retombe
        b = 0.5 + 0.5 * math.sin(2 * math.pi * ph * n_)
        foot = sm([(xb - wb * 0.75, yb + 3), (xb - wb * 0.4, yb - 2 - b), (xb, yb - 3 - 1.4 * b), (xb + wb * 0.45, yb - 2),
                   (xb + wb * 0.8, yb + 3), (xb, yb + 5)], t=0.9)
        out.append(path(foot, LAVE['glow'], 0.9))
        return ''.join(out)
    return fn


element('chute1', -17, 'boucle', box=(95, 542, 46, 232), n=16, ms=150)(chute(0, 1))
element('chute2', -17, 'boucle', box=(405, 640, 28, 134), n=16, ms=150)(chute(1, 1))


@element('lueurs-chutes', -21, 'fixe')
def lueurs_chutes(doc):
    """La lueur des chutes sur la roche (fixe, sous les chutes)."""
    out = []
    for (xt, yt), (xb, yb), wt, wb in CHUTES:
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(xb), fm((yt + yb) / 2), fm(wb * 1.6), fm((yb - yt) / 2 + 10), doc.rad(
                xb, (yt + yb) / 2, wb * 1.6, [(0, '#e06a3a', 0.35), (0.6, '#c0503a', 0.12), (1, '#a0403a', 0)],
                ry=(yb - yt) / 2 + 10)))
    return ''.join(out)


def plaque(doc, cx, y, w_, h_, k=1.0, loin=0.0):
    """Une plaque de croûte qui flotte : un dessus de cendre éclairé (en haut à droite), son épaisseur sombre
    dessous, et la lave plus chaude tout autour de son bord."""
    s = sm([(cx - w_ / 2, y + h_ * 0.2), (cx - w_ * 0.3, y - h_ * 0.45), (cx + w_ * 0.1, y - h_ * 0.55),
            (cx + w_ * 0.45, y - h_ * 0.3), (cx + w_ / 2, y + h_ * 0.15), (cx + w_ * 0.2, y + h_ * 0.5),
            (cx - w_ * 0.25, y + h_ * 0.48)], t=0.9)
    out = ['<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(cx), fm(y + h_ * 0.2), fm(w_ * 0.62), fm(h_ * 0.95), doc.rad(cx, y + h_ * 0.2, w_ * 0.62, [
            (0, LAVE['hot'], 0.55 * k), (0.75, LAVE['glow'], 0.3 * k), (1, LAVE['glow'], 0)], ry=h_ * 0.95))]
    out.append(path(s.move(0, h_ * 0.35), mix('#3a1820', '#8a3a2c', loin)))
    top = dict(base=mix('#6a3a36', '#8a4a38', loin), light=mix('#86524a', '#a05a40', loin),
               rim=mix('#b88068', '#c88058', loin), sh=mix('#4e2a2e', '#7a3a30', loin))
    out.append(vol(doc, s, top, r=0.9, c=0, rim_op=0.8))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- la rivière
RIV = (0, 744, 590, 44)          # la boîte du défilé (x, y, w, h)
RIV_T = (192, 44)                # la tuile


def riviere_tuile(doc, ox=0):
    """La tuile de la rivière de lave (192 × 46), qui se répète exactement en x."""
    tw, th = RIV_T
    out = [path('M0 0H%dV%dH0Z' % (tw, th), doc.lin(0, 0, 0, th, [
        (0, '#c8583a'), (0.35, LAVE['mid']), (0.7, '#f39448'), (1, LAVE['mid'])]))]
    plaques = [(34, 11, 40, 3.6), (126, 9, 30, 3.0), (78, 26, 50, 5.0), (168, 28, 36, 4.4), (24, 38, 44, 5.0),
               (118, 39, 56, 5.4)]
    for x, y, w_, h_ in plaques:
        for dx in (-tw, 0, tw):
            out.append(plaque(doc, x + dx, y, w_, h_, k=0.8, loin=0.35 * (1 - y / th)))
    # le lointain de la rivière dans la brume
    out.append(path('M0 0H%dV14H0Z' % tw, doc.lin(0, 0, 0, 14, [(0, '#a8503e', 0.55), (1, '#a8503e', 0)])))
    return ''.join(out)


@element('rives', -17.5, 'morceau', box=(0, 740, 590, P0 - 740))
def rives(doc):
    """La rive d'en face (un fil sombre) et la rive proche, la corniche de basalte qui va jusqu'à l'arène."""
    out = []
    loin = sm([(-10, 740), (600, 740), (600, 745), (520, 746), (430, 744), (330, 746), (240, 745), (150, 747),
               (60, 745), (-10, 746)], sharp=(0, 1), t=0.7)
    out.append(path(loin, '#5a2a36', 0.85))
    pts = [(-10, P0 + 4), (-10, 783), (30, 780), (80, 784), (130, 780), (190, 783), (250, 779), (300, 782),
           (360, 778), (420, 782), (480, 779), (540, 783), (600, 780), (600, P0 + 4)]
    s = sm(pts, sharp=(0, 1, len(pts) - 2, len(pts) - 1), t=0.7)
    out.append(vol(doc, s, dict(base='#3a2730', light='#4a3238', rim='#8a5a4e', sh='#2c1e28'),
                   grad=doc.lin(0, 780, 0, P0, [(0, '#5a3634'), (0.45, '#3e2a32'), (1, '#2e2029')]), r=1.4, c=0))
    out.append(corniche(doc))
    return ''.join(out)


def riviere(doc, off):
    x, y, w, h = RIV
    tw, th = RIV_T
    out = []
    for k in range(-1, w // tw + 2):
        out.append('<g transform="translate(%s %s)">%s</g>' % (fm(x + k * tw + off), fm(y), riviere_tuile(doc)))
    return '<g clip-path="%s">%s</g>' % (doc.clip('M%d %dH%dV%dH%dZ' % (x, y, x + w, y + h, x)), ''.join(out))


element('riviere', -18, 'defile', box=RIV, tuile=RIV_T, vx=20.0, vy=0.0, dessin=riviere, tuile_dessin=riviere_tuile)


# ---------------------------------------------------------------------------------------------------- l'arène
def corniche(doc):
    """Entre la rive et l'arène : la corniche de basalte, calme, et quelques pierres posées."""
    out = [path('M-10 %dH600V%dH-10Z' % (P0 - 2, P0), '#241820', 0.8)]
    for x, w_, h_ in ((22, 26, 8), (246, 18, 6), (338, 22, 7), (548, 30, 9)):
        y = P0 - 1
        s = sm([(x - w_ / 2, y), (x - w_ * 0.3, y - h_), (x + w_ * 0.2, y - h_ * 1.05), (x + w_ / 2, y)],
               sharp=(0, 3), t=0.8)
        out.append(vol(doc, s, ROC, r=1.0, c=1.4))
    out.append(cristaux(doc, 296, P0 - 5, 0.65))
    return ''.join(out)


def sol_x(g, y):
    """Le dallage en perspective : la coordonnée au sol g → x à l'écran (les joints filent vers le centre)."""
    k = (y - 600) / (P1 - 600)
    return 295 + g * k


@element('arene', -15.5, 'fixe')
def arene(doc):
    out = []
    # le dessus : un rectangle d'un bord à l'autre, une seule valeur moyenne qui s'éclaire à peine vers l'avant et
    # vers la droite (la lumière)
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, P0, 0, P1, [(0, SOL['back']), (1, SOL['front'])])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, 0, 590, 0, [(0, '#2a1a2a', 0.06),
                                                                              (1, '#fff0d8', 0.04)])))
    # les dalles : des joints à peine marqués (rangs plus hauts devant), décalés d'un rang à l'autre
    rows = [P0, 824, 852, 886, 928, 980, P1]
    joints = []
    for i in range(len(rows) - 1):
        ya, yb = rows[i], rows[i + 1]
        if i > 0:
            joints.append('M-10 %s H600' % fm(ya))
        step = 150
        off = (i % 2) * step / 2 + (i * 37) % 40
        g = -900 + off
        while g < 900:
            xa, xb = sol_x(g, ya), sol_x(g, yb)
            if -10 < min(xa, xb) and max(xa, xb) < 600:
                joints.append('M%s %s L%s %s' % (fm(xa), fm(ya + 1), fm(xb), fm(yb - 1)))
            g += step + 20 * math.sin(i * 3.1 + g)
    jd = ' '.join(joints)
    out.append('<path d="%s" fill="none" stroke="#fff4e6" stroke-width="1.2" opacity="0.05" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#2a1826" stroke-width="1" opacity="0.11"/>' % jd)
    # quelques dalles un peu plus claires ou plus sombres (très peu)
    for (g0, i, col, op) in ((-220, 1, '#fff0e0', 0.035), (60, 3, '#2a1826', 0.04), (300, 2, '#fff0e0', 0.03),
                             (-90, 4, '#2a1826', 0.035), (180, 5, '#fff0e0', 0.03)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 140, ya), ya), (sol_x(g0 + 140, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le bord arrière : un fil d'ombre, puis l'arête éclairée
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 1.6), '#9a8682', 0.7))
    # la lueur de la rivière sur le fond du dallage (douce)
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 26), doc.lin(0, P0, 0, P0 + 26, [(0, '#d0603e', 0.10),
                                                                                       (1, '#d0603e', 0)])))
    # l'arête avant éclairée, puis le flanc (rougi par la lave d'en dessous)
    out.append(path('M-10 %dH600V%dH-10Z' % (P1, 1064), doc.lin(0, P1, 0, 1064, [
        (0, '#4a3438'), (0.5, '#4e3236'), (1, '#7a3a30')])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P1 - 1, P1 + 1.6), '#a89088', 0.85))
    for g in range(-600, 700, 160):
        x = sol_x(g, P1)
        out.append(path(rpoly([(x - 0.6, P1 + 2), (x + 0.6, P1 + 2), (x + 0.6, 1060), (x - 0.6, 1060)], 0.3),
                        '#2a1826', 0.35))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- sous l'arène
@element('dessous', -15.4, 'fixe')
def dessous(doc):
    """Sous le flanc de l'arène : en combat, c'est sous les cartes des héros (y > 985) ; donc simple et sombre, une
    croûte de lave refroidie à peine rougie, sans détail perdu (l'accueil, qui la montre, garde un bas calme)."""
    out = [path('M-10 1062H600V1104H-10Z', doc.lin(0, 1062, 0, 1100, [(0, '#5a2a28'), (0.3, '#3e1e26'),
                                                                     (1, '#2e1822')]))]
    pts = [(-10, 1058), (600, 1058), (600, 1064)]
    x, i = 600, 0
    while x > -10:
        x -= 22 + 9 * math.sin(i * 1.7)
        pts.append((x, 1064 + 3 * math.sin(i * 2.3) + 1.5 * math.cos(i * 1.1)))
        i += 1
    pts.append((-10, 1064))
    out.append(path(sm(pts, sharp=(0, 1), t=0.7), doc.lin(0, 1058, 0, 1068, [(0, '#6a3630'), (1, '#5a2c2a')])))
    return ''.join(out)


def braise_image(doc, i, n):
    t = i / (n - 1)
    r = 1.5 - 0.6 * t
    op = 1 - 0.75 * t
    return ('<circle cx="6" cy="6" r="5" fill="%s"/><circle cx="6" cy="6" r="%s" fill="%s"/>' % (
        doc.rad(6, 6, 5, [(0, '#ff9a40', 0.55 * op), (1, '#ff7a30', 0)]), fm(r),
        mix('#fff0b0', '#ffb060', t)) if op > 0 else '')


element('braises-fond', -14, 'particules', taille=(12, 12), images=4, dessin=braise_image, zone=(10, 748, 580, 776),
        nombre=6, vie=(2200, 3400), vx=(-3, 4), vy=(-14, -8), ondule=(2, 1800))



# ---------------------------------------------------------------------------------------------------- premier plan
@element('rocher-gauche', 1300, 'morceau', box=(0, 1030, 84, 70))
def rocher_g(doc):
    s = sm([(-12, 1104), (-12, 1046), (8, 1038), (30, 1040), (50, 1052), (66, 1070), (78, 1092), (80, 1104)],
           sharp=(0, 7), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(30, 1044), (50, 1054), (64, 1072), (52, 1080), (36, 1062)], t=0.9), ROC['light'], 0.55))
    return ''.join(out)


@element('rocher-droite', 1300, 'morceau', box=(522, 1028, 68, 72))
def rocher_d(doc):
    s = sm([(524, 1104), (530, 1080), (544, 1058), (562, 1042), (584, 1036), (604, 1040), (604, 1104)],
           sharp=(0, 6), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(566, 1046), (590, 1040), (600, 1056), (584, 1064)], t=0.9), ROC['light'], 0.5))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les dragons
# Demande du propriétaire (27/11) : « des ombres de dragons qui volent dans le fond ». Trois silhouettes lointaines,
# ailes déployées (bras, doigts en os, membrane), long cou, longue queue, dans la couleur de la brume du ciel en un
# peu plus foncé ; plus loin = plus petit, plus clair et plus lent. Ils traversent le ciel derrière le volcan et la
# fumée (deux « morceaux » remettent le panache et le haut du cône devant eux), jamais sur l'arène. Chacun est une
# particule seule qui vit une période entière : il naît caché (hors de l'image, ou derrière le cône ou le panache)
# et finit caché ; ses ailes battent lentement (12 images en boucle).
DRAGONS = [
    # id, y, échelle, x de départ, x d'arrivée, montée (px/s), couleur, opacité, profondeur
    ('dragon1', 418, 0.6, -46, 636, -0.6, '#280e24', 0.9, -29.75),       # le plus proche : de bord à bord
    ('dragon2', 490, 0.3, 330, -30, 0.0, '#3a1830', 0.7, -29.74),        # sort de derrière le cône, part à gauche
    ('dragon3', 352, 0.2, 262, 630, -0.4, '#321430', 0.62, -29.73),      # le plus loin : sort du panache
]
DRAGON_N, DRAGON_MS = 12, 160                     # un battement d'ailes = 1,92 s
DRAGON_BOITE = (-74, -64, 114, 104)                # la silhouette (repère local, tête à droite) : x, y, w, h


def aile(ph, near=True):
    """Une aile (repère local, tête à droite) : le bras (épaule, coude, poignet), trois doigts en os et la membrane
    festonnée tendue entre eux jusqu'à la hanche. ph : le battement (0 = en haut, 0,5 = en bas)."""
    a = 2 * math.pi * ph
    f = 0.2 + 0.8 * math.cos(a)                  # 1 : en haut, −0,6 : en bas
    sx = 0.8 + 0.2 * abs(f)
    S = (0, -3) if near else (4, -4)
    k = 1 if near else 0.84

    def P(dx, dy):
        return (S[0] + dx * sx * k, S[1] + dy * f * k)
    e, wr = (-8, -18), (4, -38)
    tips = [(-18, -56), (-40, -45), (-56, -25)]
    hip = (-26, 2)

    def creux(a, b, k_=0.26):
        """Deux points d'un feston entre deux pointes : la membrane se creuse vers le poignet."""
        out = []
        for t in (0.33, 0.67):
            m = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            out.append((m[0] + (wr[0] - m[0]) * k_ * (1 - abs(t - 0.5)), m[1] + (wr[1] - m[1]) * k_ * (1 - abs(t - 0.5))))
        return out
    loc = [(0, 0), e, wr, tips[0]] + creux(tips[0], tips[1]) + [tips[1]] + creux(tips[1], tips[2]) + [tips[2]] + \
        creux(tips[2], (hip[0], hip[1] - 2), 0.18) + [(hip[0] + 4, hip[1] - 3)]
    memb = [P(x, y) for x, y in loc]
    Wr, E = P(*wr), P(*e)
    F = [P(*t_) for t_ in tips]
    os_ = [([S, E, Wr], 2.0), ([Wr, F[0]], 1.3), ([Wr, F[1]], 1.2), ([Wr, F[2]], 1.1)]
    return memb, os_


def dragon_corps(ph):
    """Le cou, la tête, le corps, la queue et les pattes repliées (repère local), qui montent un peu au battement."""
    b = -1.2 * math.sin(2 * math.pi * ph)
    dos = [(-64, -6), (-54, 0), (-42, 3), (-28, 2), (-14, 0), (0, -1), (10, -4), (18, -9), (25, -13)]
    dos = [(x, y + b * (0.4 + 0.6 * min(1, max(0, (x + 20) / 40)))) for x, y in dos]
    c = resample(catmull(dos), 24)
    ws = []
    for i in range(25):
        u = i / 24
        ws.append(0.6 + 7.6 * math.sin(math.pi * min(1, max(0, (u - 0.12) / 0.74))) ** 1.8 if u < 0.85
                  else 2.4 - 3 * (u - 0.85))
    corps = ribbon(c, ws)
    hx, hy = c[-1]
    tete = sm([(hx - 4, hy - 2.2), (hx + 4, hy - 2.6), (hx + 10, hy + 0.4), (hx + 4, hy + 2.4), (hx - 3, hy + 2.6)],
              sharp=(2,), t=0.8)
    cornes = [ribbon([(hx - 1, hy - 1.6), (hx - 6, hy - 5), (hx - 10, hy - 6.4)], [1.4, 0.9, 0.2]),
              ribbon([(hx + 1, hy - 2), (hx - 3, hy - 6.6), (hx - 6, hy - 9)], [1.2, 0.8, 0.2])]
    tx, ty = c[0]
    pique = sm([(tx + 3, ty), (tx - 3, ty - 4), (tx - 8, ty + 0.5), (tx - 3, ty + 3)], sharp=(1, 2, 3), t=0.6)
    pattes = [ribbon([(-14, 2 + b * 0.5), (-19, 7), (-25, 8.5)], [2.4, 1.6, 0.4]),
              ribbon([(4, 0 + b), (3, 5), (-1, 6.5)], [1.8, 1.2, 0.3])]
    return [corps, tete, pique] + cornes + pattes


def dragon_image(id_):
    _, y, k, x0, x1, vy, col, op, _ = next(d for d in DRAGONS if d[0] == id_)
    sg = 1 if x1 > x0 else -1
    bx, by, bw, bh = DRAGON_BOITE
    w, h = bw * k + 4, bh * k + 4

    def fn(doc, i, n):
        ph = i / n
        ciel_ = mix(col, '#5a2338', 0.35)                   # l'aile lointaine, plus dans la brume
        ox = w / 2 - (bx + bw / 2) * k * sg
        oy = h / 2 - (by + bh / 2) * k
        out = ['<g transform="translate(%s %s) scale(%s %s)">' % (fm(ox), fm(oy), fm(k * sg), fm(k))]
        for near, c in ((False, ciel_), (True, col)):
            memb, os_ = aile(ph, near)
            if near:
                out.extend(path(p_, col) for p_ in dragon_corps(ph))
            out.append(path(sm(memb, sharp=(0, 2, 3, 6, 9, 12), t=0.7), c, 0.88))
            for b_, sw in os_:
                out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" '
                           'stroke-linejoin="round"/>' % (polyline_d(b_), mix(c, '#1a0818', 0.25), sw))
        out.append('</g>')
        return '<g opacity="%g">%s</g>' % (op, ''.join(out))
    return fn, (round(w), round(h))


for _d in DRAGONS:
    _fn, _t = dragon_image(_d[0])
    _vx = (_d[4] - _d[3]) * 1000 / PERIODE
    element(_d[0], _d[8], 'particules', taille=_t, images=DRAGON_N, ms=DRAGON_MS, dessin=_fn,
            zone=(_d[3], _d[1], _d[3], _d[1]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_d[5], _d[5]),
            ondule=(0, PERIODE))


def devant(ids, box):
    """Un morceau du paysage remis devant les dragons : ces éléments seuls (sans le ciel), coupés à la boîte."""
    def fn(doc):
        x, y, w, h = box
        body = ''.join(e['fn'](doc) for e in sorted(ELEMS, key=lambda e: e['prof']) if e['id'] in ids)
        return '<g clip-path="%s">%s</g>' % (doc.clip('M%s %sH%sV%sH%sZ' % (x, y, x + w, y + h, x)), body)
    return fn


element('devant-panache', -27.9, 'morceau', box=(226, 336, 150, 118))(devant(('panache', 'nuages', 'volcan'),
                                                                              (226, 336, 150, 118)))
element('devant-volcan', -27.9, 'morceau', box=(276, 474, 104, 32))(devant(('volcan',), (276, 474, 104, 32)))


# ================================================================================================ LE TEMPS
def rng(seed):
    """Le hasard à graine du jeu (src/game/bg/fond-px.ts), recopié à l'identique : mêmes particules qu'en combat."""
    M = 0xffffffff
    a = 991
    for ch in seed:
        a = ((a * 31) + ord(ch)) & M

    def imul(x, y):
        return ((x & M) * (y & M)) & M

    def r(lo=0.0, hi=1.0):
        nonlocal a
        a = (a + 0x6d2b79f5) & M
        t = a
        t = imul(t ^ (t >> 15), t | 1)
        t = (t ^ ((t + imul(t ^ (t >> 7), t | 61)) & M)) & M
        return lo + (((t ^ (t >> 14)) & M) / 4294967296) * (hi - lo)
    return r


_PART_CACHE = {}


def particules_a(e, t):
    """Où sont les particules à l'instant t (la règle du jeu : chaque place renaît au même endroit à chaque période ;
    images jouées sur la vie, ou en boucle toutes les `ms`)."""
    if e['id'] not in _PART_CACHE:
        r = rng('kael-' + e['id'])
        P = PERIODE
        life0 = (e['vie'][0] + e['vie'][1]) / 2
        slots = max(e['nombre'], math.ceil(e['nombre'] * P / life0))
        lst = []
        for s in range(slots):
            life = min(P, r(*e['vie']))
            born = (s + r()) * P / slots
            x0, y0 = r(e['zone'][0], e['zone'][2]), r(e['zone'][1], e['zone'][3])
            vx, vy = r(*e['vx']), r(*e['vy'])
            ph = r(0, 6.283)
            lst.append((life, born, x0, y0, vx, vy, ph))
        _PART_CACHE[e['id']] = lst
    out = []
    amp, per = e['ondule']
    ms = e.get('ms', 0)
    for life, born, x0, y0, vx, vy, ph in _PART_CACHE[e['id']]:
        age = ((t - born) % PERIODE + PERIODE) % PERIODE
        if age >= life:
            continue
        s = age / 1000
        x = x0 + vx * s + amp * math.sin(ph + 2 * math.pi * age / max(1, per))
        y = y0 + vy * s
        i = int((age + ph * 100) // ms) % e['images'] if ms else min(e['images'] - 1, int(age / life * e['images']))
        out.append((x, y, i))
    return out


def phase(e, t, override=None):
    if override and e['id'] in override:
        return override[e['id']]
    if e['genre'] == 'boucle':
        return (int(t // e['ms']) % e['n']) / e['n']
    return 0


def scene(t=0, box=(0, 0, W, H), particules=True, base=False):
    """Tout le fond à l'instant t, en SVG (sans les personnages). base : seulement l'image fixe du jeu (ce qui ne
    bouge pas : les boucles, défilés et particules sont des calques posés par-dessus)."""
    doc = Doc()
    body = []
    for e in sorted(ELEMS, key=lambda e: e['prof']):
        g = e['genre']
        if base and g not in ('fixe', 'morceau'):
            continue
        if g in ('fixe', 'morceau'):
            body.append(e['fn'](doc))
        elif g == 'boucle':
            body.append(e['fn'](doc, phase(e, t)))
        elif g == 'defile':
            tw = e['tuile'][0]
            off = (t / 1000 * e['vx']) % tw
            body.append(e['dessin'](doc, off))
        elif g == 'particules' and particules:
            ids = []
            for i in range(e['images']):
                sid = doc.uid('s')
                doc.defs.append('<g id="%s">%s</g>' % (sid, e['dessin'](doc, i, e['images'])))
                ids.append(sid)
            w_, h_ = e['taille']
            for x, y, i in particules_a(e, t):
                body.append('<use href="#%s" x="%s" y="%s"/>' % (ids[i], fm(x - w_ / 2), fm(y - h_ / 2)))
    return doc.svg(''.join(body), box)


# ================================================================================================ LE RENDU
def rendre(jobs, w, h):
    """jobs = [(svg, sortie.png)] tous rendus à w × h par le moteur des héros (Chromium, rendu-lot.cjs)."""
    os.makedirs(os.path.join(TMP, 'svg'), exist_ok=True)
    frames = []
    for k, (svg, out) in enumerate(jobs):
        p = os.path.join(TMP, 'svg', '%d-%d-%d.svg' % (w, h, k))
        open(p, 'w').write(svg)
        frames.append([p, out])
    jp = os.path.join(TMP, 'svg', 'job-%d-%d.json' % (w, h))
    json.dump({'w': w, 'h': h, 'frames': frames}, open(jp, 'w'))
    subprocess.run(['node', RENDU, jp], check=True)
    return [f[1] for f in frames]


# ------------------------------------------------------------------------------------------------ les personnages
# Côté héros : Aurelle (angels-10) au fond, Brasyr (dragon-feu) au milieu, Kael (assassins-2) devant ; en face, les
# trois monstres du clan de Kael (lutin de magma, golem, salamandre), retournés vers la gauche.
PERSOS = [('angels-10', 'heros', 0), ('dragon-feu', 'heros', 2), ('assassins-2', 'heros', 4),
          ('mon-kael-rapide', 'ennemis', 0), ('mon-kael-costaud', 'ennemis', 2), ('mon-kael-tireur', 'ennemis', 4)]


def vecto_table():
    import re
    s = open(os.path.join(ROOT, 'src', 'game', 'vecto.ts')).read()
    out = {}
    for m in re.finditer(r"'([\w-]+)': \[([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\]", s):
        out[m.group(1)] = tuple(float(m.group(i)) for i in range(2, 6))
    return out


def poser(im, s, x0, y0, persos=PERSOS):
    """Pose les personnages vectoriels (public/art/vecto/<id>.webp) comme le combat : places de place_combat(),
    taille K_PERSO (un pixel de mesure = 0,68 pixel du fond), l'ombre du jeu (ovale noir à 30 %). L'image `im` est le
    fond rendu à l'échelle s (pixels d'image par pixel du fond), son coin haut-gauche en (x0, y0) du fond."""
    tab = vecto_table()
    acts = sorted([(place_combat(side, slot)[1], cid, side, slot) for cid, side, slot in persos])
    ss = 4
    sh = Image.new('L', (im.width * ss, im.height * ss), 0)
    d = ImageDraw.Draw(sh)
    for fy, cid, side, slot in acts:
        fx, fy = place_combat(side, slot)
        w_ = min(160, tab[cid][0] * 0.6 * 1.22 * 0.95 * 1.1) / UC
        hh = 10 / UC
        d.ellipse(((fx - x0 - w_ / 2) * s * ss, (fy - y0 - hh) * s * ss, (fx - x0 + w_ / 2) * s * ss,
                   (fy - y0 + hh) * s * ss), fill=77)
    sh = sh.resize(im.size, Image.LANCZOS)
    black = Image.new('RGBA', im.size, (0, 0, 0, 255))
    black.putalpha(sh)
    im.alpha_composite(black)
    for fy, cid, side, slot in acts:
        fx, fy = place_combat(side, slot)
        w_, h_, ax, ay = tab[cid]
        k = K_PERSO * s
        sp = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', cid + '.webp')).convert('RGBA')
        sp = sp.resize((round(w_ * k), round(h_ * k)), Image.LANCZOS)
        if side == 'heros':
            x = (fx - x0) * s - ax * k
        else:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            x = (fx - x0) * s - (w_ - ax) * k
        y = (fy - y0) * s - ay * k
        im.paste(sp, (round(x), round(y)), sp) if x < 0 or y < 0 else im.alpha_composite(sp, (round(x), round(y)))
    return im


def vue_combat(t, largeur, phone=(390, 844, 34), fond=None):
    """Ce que montre le combat sur un téléphone (sans l'interface) : le fond (vectoriel à l'instant t, ou l'image
    `fond` donnée), les personnages, et sous le terrain la bande de la barre de geste (fond du jeu)."""
    top, hu = telephone(*phone)
    x0 = VUE_X[0]
    s = largeur / (VUE_X[1] - VUE_X[0])
    hh = round((H - top) * s)
    if fond is None:
        p = os.path.join(TMP, 'vue-%d.png' % largeur)
        rendre([(scene(t, (x0, top, VUE_X[1] - x0, H - top)), p)], largeur, hh)
        im = Image.open(p).convert('RGBA')
    else:
        im = fond.crop((round(x0 * fond.width / W), round(top * fond.height / H), round(VUE_X[1] * fond.width / W),
                        fond.height)).resize((largeur, hh), Image.NEAREST).convert('RGBA')
    im = poser(im, s, x0, top)
    return geste(im, s, phone)


def geste(im, s, phone):
    bas = round(phone[2] * 720 / phone[0] / UC * s)
    out = Image.new('RGBA', (im.width, im.height + bas), (21, 15, 54, 255))
    out.alpha_composite(im, (0, 0))
    return out


# ================================================================================================ LES EXPORTS
def calques():
    """Rend les images de chaque calque (×UP), les range dans une planche et écrit la description JSON."""
    os.makedirs(os.path.join(TMP, 'calques'), exist_ok=True)
    groupes = {}        # (w, h) → [(svg, png, (id, i))]
    for e in sorted(ELEMS, key=lambda e: e['prof']):
        g = e['genre']
        if g in ('boucle', 'morceau'):
            x, y, w_, h_ = e['box']
            n = e.get('n', 1)
            for i in range(n):
                doc = Doc()
                body = e['fn'](doc, i / n) if g == 'boucle' else e['fn'](doc)
                svg = doc.svg(body, (x, y, w_, h_))
                png = os.path.join(TMP, 'calques', '%s-%02d.png' % (e['id'], i))
                groupes.setdefault((w_ * UP, h_ * UP), []).append((svg, png, (e['id'], i)))
        elif g == 'defile':
            tw, th = e['tuile']
            doc = Doc()
            svg = doc.svg(e['tuile_dessin'](doc), (0, 0, tw, th))
            png = os.path.join(TMP, 'calques', '%s-tuile.png' % e['id'])
            groupes.setdefault((tw * UP, th * UP), []).append((svg, png, (e['id'], 0)))
        elif g == 'particules':
            w_, h_ = e['taille']
            for i in range(e['images']):
                doc = Doc()
                svg = doc.svg(e['dessin'](doc, i, e['images']), (0, 0, w_, h_))
                png = os.path.join(TMP, 'calques', '%s-%02d.png' % (e['id'], i))
                groupes.setdefault((w_ * UP, h_ * UP), []).append((svg, png, (e['id'], i)))
    images = {}
    for (w_, h_), lst in groupes.items():
        rendre([(s_, p_) for s_, p_, _ in lst], w_, h_)
        for _, p_, key in lst:
            images[key] = Image.open(p_).convert('RGBA')
    # la planche : des étagères, les plus hautes d'abord, 2048 px de large au plus. Chaque image est « étirée » de 2 px
    # tout autour (ses bords recopiés) : le jeu agrandit en lissant, et sans cela un liseré sombre apparaît au bord
    # des morceaux remis devant (vu dans le vrai combat).
    keys = sorted(images, key=lambda k: (-images[k].height, k))
    PW, EX = 2048, 2
    pos = {}
    x = y = EX
    rowh = 0
    for k in keys:
        im = images[k]
        if x + im.width + EX > PW:
            x, y, rowh = EX, y + rowh + 2 * EX + 1, 0
        pos[k] = (x, y)
        x += im.width + 2 * EX + 1
        rowh = max(rowh, im.height)
    ph = y + rowh + EX
    planche = Image.new('RGBA', (PW, ph), (0, 0, 0, 0))
    for k, (px_, py_) in pos.items():
        im = images[k]
        w_, h_ = im.size
        big = Image.new('RGBA', (w_ + 2 * EX, h_ + 2 * EX))
        big.paste(im.resize((w_ + 2 * EX, h_ + 2 * EX), Image.NEAREST), (0, 0))   # les bords, étirés
        big.paste(im, (EX, EX))
        for i in range(EX):
            big.paste(im.crop((0, 0, w_, 1)), (EX, i))
            big.paste(im.crop((0, h_ - 1, w_, h_)), (EX, h_ + EX + i))
            big.paste(im.crop((0, 0, 1, h_)), (i, EX))
            big.paste(im.crop((w_ - 1, 0, w_, h_)), (w_ + EX + i, EX))
        planche.paste(big, (px_ - EX, py_ - EX))
    used = max(px_ + images[k].width + EX for k, (px_, py_) in pos.items())
    planche = planche.crop((0, 0, used, ph))
    meta = []
    for e in sorted(ELEMS, key=lambda e: e['prof']):
        g = e['genre']
        c = dict(id=e['id'], prof=e['prof'])
        if g in ('boucle', 'morceau'):
            x_, y_, w_, h_ = e['box']
            n = e.get('n', 1)
            c.update(genre='boucle', x=x_, y=y_, w=w_, h=h_, ms=e.get('ms', 0) if n > 1 else 0,
                     cases=[list(pos[(e['id'], i)]) for i in range(n)])
        elif g == 'defile':
            x_, y_, w_, h_ = e['box']
            sx, sy = pos[(e['id'], 0)]
            c.update(genre='defile', x=x_, y=y_, w=w_, h=h_, case=[sx, sy, e['tuile'][0] * UP, e['tuile'][1] * UP],
                     vx=e['vx'], vy=e['vy'])
        elif g == 'particules':
            w_, h_ = e['taille']
            c.update(genre='particules', cases=[list(pos[(e['id'], i)]) + [w_ * UP, h_ * UP] for i in range(e['images'])],
                     zone=list(e['zone']), nombre=e['nombre'], vie=list(e['vie']), vx=list(e['vx']), vy=list(e['vy']),
                     ondule=list(e['ondule']), images='boucle' if e.get('ms') else 'vie', ms=e.get('ms', 0),
                     graine='kael-' + e['id'])
        else:
            continue
        meta.append(c)
    return planche, meta


def exporter():
    os.makedirs(JEU, exist_ok=True)
    os.makedirs(SORTIE, exist_ok=True)
    # l'image fixe du jeu ×UP : seulement ce qui ne bouge pas (les calques animés se posent dessus, entiers)
    fixe = os.path.join(TMP, 'fixe-x2.png')
    rendre([(scene(0, particules=False, base=True), fixe)], W * UP, H * UP)
    Image.open(fixe).convert('RGB').save(os.path.join(JEU, 'kael.webp'), quality=95, method=6)
    # le fond entier pour le propriétaire (les dragons en vol)
    rendre([(scene(5200), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    planche.save(os.path.join(JEU, 'kael-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': 'kael', 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/kael.webp', 'planche': 'art/vecto/fonds/kael-anim.webp',
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("kael-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-kael.json'), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print('  jeu : public/art/vecto/fonds/kael.webp %d Ko, kael-anim.webp %d Ko (%d × %d), %d calques' % (
        os.path.getsize(os.path.join(JEU, 'kael.webp')) // 1024,
        os.path.getsize(os.path.join(JEU, 'kael-anim.webp')) // 1024, planche.size[0], planche.size[1], len(meta)))
    return doc


def ecrire_ts(doc):
    """src/game/fond-vecto.ts : les calques au format de FOND_META (lu par bg/fond-px.ts derrière ?vecto=1)."""
    out = []
    for c in doc['calques']:
        z = c['prof']
        if c['genre'] == 'boucle':
            out.append(dict(id=c['id'], g='b', z=z, x=c['x'], y=c['y'], w=c['w'], h=c['h'], ms=c['ms'], f=c['cases']))
        elif c['genre'] == 'defile':
            out.append(dict(id=c['id'], g='d', z=z, x=c['x'], y=c['y'], w=c['w'], h=c['h'], f=c['case'], vx=c['vx'],
                            vy=c['vy']))
        else:
            out.append(dict(id=c['id'], g='p', z=z, f=c['cases'], zone=c['zone'], n=c['nombre'], vie=c['vie'],
                            vx=[round(v, 4) for v in c['vx']], vy=c['vy'], ondule=c['ondule'], ms=c['ms']))
    meta = {'w': W, 'h': H, 'up': UP, 'periode': PERIODE, 'calques': out}
    json.dump(meta, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meta.json'), 'w'), separators=(',', ':'))
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from assemble_ts import assemble
    assemble()


def composer_jeu(doc, t):
    """Contrôle : l'image à l'instant t refaite comme le jeu la ferait (fixe + calques de la planche), à ×UP."""
    base = Image.open(os.path.join(JEU, 'kael.webp')).convert('RGBA')
    pl = Image.open(os.path.join(TMP, 'planche.png')).convert('RGBA')
    for c in sorted(doc['calques'], key=lambda c: c['prof']):
        if c['genre'] == 'boucle':
            i = 0 if c['ms'] == 0 else int(t // c['ms']) % len(c['cases'])
            sx, sy = c['cases'][i]
            base.alpha_composite(pl.crop((sx, sy, sx + c['w'] * UP, sy + c['h'] * UP)), (c['x'] * UP, c['y'] * UP))
        elif c['genre'] == 'defile':
            sx, sy, tw, th = c['case']
            tile = pl.crop((sx, sy, sx + tw, sy + th))
            off = round((t / 1000 * c['vx']) % (tw / UP) * UP)
            strip = Image.new('RGBA', (c['w'] * UP + 2 * tw, th))
            for k in range(c['w'] * UP // tw + 3):
                strip.alpha_composite(tile, (k * tw, 0))
            base.alpha_composite(strip.crop((tw - off, 0, tw - off + c['w'] * UP, th)), (c['x'] * UP, c['y'] * UP))
    return base


def contrôles(img_x1):
    """Mesures du sol de combat (comme le contrôle du pixel) : là où sont les pieds en combat, au-dessus des cartes."""
    a = np.asarray(img_x1.convert('RGB'), float)
    zone = a[P0 + 6:int(CARTES), int(VUE_X[0]):int(VUE_X[1])]
    L = zone[..., 0] * 0.3 + zone[..., 1] * 0.59 + zone[..., 2] * 0.11
    edges = (np.abs(np.diff(L, axis=1)) > 28).mean()
    print('  sol de combat (y %d → %d, x %d → %d) : luminosité moyenne %.0f, écart %.1f, %.2f %% de bords durs' % (
        P0 + 6, CARTES, VUE_X[0], VUE_X[1], L.mean(), L.std(), edges * 100))
    return L.mean(), L.std(), edges


def main():
    args = sys.argv[1:]
    os.makedirs(TMP, exist_ok=True)
    if '--fixe' in args:
        # le brouillon : la vue du combat sur un téléphone 390 × 844 (avec les personnages) et sur un court
        vue_combat(5200, 780).convert('RGB').save(os.path.join(TMP, 'brouillon-390.png'))
        vue_combat(5200, 720, phone=(360, 640, 0)).convert('RGB').save(os.path.join(TMP, 'brouillon-360.png'))
        print('  ', TMP)
        return
    os.makedirs(SORTIE, exist_ok=True)
    doc = exporter()
    # contrôle : le jeu (fixe + calques) donne bien la même image que le dessin entier
    for t in (0, 1650, 5100):
        ref = os.path.join(TMP, 'ref-%d.png' % t)
        rendre([(scene(t, particules=False), ref)], W * UP, H * UP)
        a = np.asarray(Image.open(ref).convert('RGB'), float)
        b = np.asarray(composer_jeu(doc, t).convert('RGB'), float)
        diff = np.abs(a - b).max(2)
        print('  jeu = dessin à t = %d ms : écart moyen %.2f, %.2f %% des pixels à plus de 24' % (
            t, diff.mean(), (diff > 24).mean() * 100))
        if t == 1650:
            Image.fromarray(np.clip(diff * 4, 0, 255).astype(np.uint8)).save(os.path.join(TMP, 'diff-jeu.png'))
    contrôles(Image.open(os.path.join(TMP, 'ref-0.png')).resize((W, H), Image.LANCZOS))
    # la situation : un téléphone 390 × 844 (×2), cadré comme le vrai combat, sans l'interface
    vue_combat(5200, 780).convert('RGB').save(os.path.join(SORTIE, 'situation.png'))
    # la comparaison : ancien fond pixel | nouveau fond vectoriel, mêmes personnages, même cadrage
    pix = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'kael.webp')).convert('RGBA')
    a = vue_combat(0, 780, fond=pix)
    b = vue_combat(5200, 780)
    comp = Image.new('RGB', (780 * 2 + 12, a.height), (31, 18, 56))
    comp.paste(a.convert('RGB'), (0, 0))
    comp.paste(b.convert('RGB'), (792, 0))
    comp.save(os.path.join(SORTIE, 'comparaison.png'))
    print('  test : fond.png, situation.png, comparaison.png')
    if '--video' in args:
        video()


def video():
    """L'animation en situation, cadrée comme le combat d'un téléphone 390 × 844 : une période entière (19,2 s),
    25 images par seconde, sans couture. Le mp4 à 720 de large (= les unités du jeu), le gif à 400 (une image sur
    deux)."""
    fps = 25
    n = PERIODE * fps // 1000
    phone = (390, 844, 34)
    top, hu = telephone(*phone)
    x0 = VUE_X[0]
    s = 720 / (VUE_X[1] - x0)
    hh = round((H - top) * s)
    d = os.path.join(TMP, 'video')
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.unlink(os.path.join(d, f))
    jobs = [(scene(i * 1000 / fps, (x0, top, VUE_X[1] - x0, H - top)), os.path.join(d, 'f%04d.png' % i))
            for i in range(n)]
    rendre(jobs, 720, hh)
    gif = []
    for i in range(n):
        im = geste(poser(Image.open(jobs[i][1]).convert('RGBA'), s, x0, top), s, phone).convert('RGB')
        if im.height % 2:
            im = im.crop((0, 0, im.width, im.height - 1))
        im.save(os.path.join(d, 'v%04d.png' % i))
        if i % 2 == 0:
            gif.append(im.resize((400, round(im.height * 400 / 720)), Image.LANCZOS))
    mp4 = os.path.join(SORTIE, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(d, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-movflags',
                    '+faststart', mp4], check=True)
    sample = Image.new('RGB', (400, gif[0].height * 4))
    for k in range(4):
        sample.paste(gif[k * len(gif) // 4], (0, k * gif[0].height))
    pal = sample.quantize(255, method=Image.Quantize.MEDIANCUT)
    q = [g.quantize(palette=pal, dither=Image.Dither.NONE) for g in gif]          # sans tramage : ≤ 3 Mo
    gp = os.path.join(SORTIE, 'anim.gif')
    q[0].save(gp, save_all=True, append_images=q[1:], duration=2000 // fps, loop=0, optimize=True)
    print('  vidéo : anim.mp4 %d Ko, anim.gif %d Ko (%d images)' % (
        os.path.getsize(mp4) // 1024, os.path.getsize(gp) // 1024, len(q)))


if __name__ == '__main__':
    main()
