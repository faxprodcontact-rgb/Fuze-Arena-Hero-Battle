# Le fond de combat du clan d'ELDRA (vent), la montagne des singes, redessiné en VECTORIEL lisse et animé (27/11/2026,
# demande du propriétaire : les 7 autres fonds sur le modèle du volcan de Kael, ui-moderne/fonds/kael/kael.py).
#
# Même univers que le fond pixel (refonte-graphique/pixel/fonds/eldra/build.py), recomposé pour le VRAI combat (le jeu
# agrandit le fond ×1,4 et coupe les côtés : on voit x = 84 → 506 ; les rangs du combat ont les pieds à 828 / 880 /
# 933 ; le haut des cartes est à 985). Le style est celui des héros et monstres vectoriels (ui-moderne/heros/atelier.py) :
# grandes formes simples, dégradés doux, une seule lumière en haut à droite (liseré clair en haut à droite, bande
# d'ombre en bas à gauche), un seul contour sombre seulement sur les plans proches, aucun flou SVG. Le fond reste MOINS
# contrasté et MOINS saturé que les personnages ; la profondeur vient de la brume (le lointain plus pâle et plus bleu).
#
# Ce qu'on voit, du fond vers le devant : le ciel du matin (bleu tendre en haut, lilas, rose puis pêche à l'horizon),
# le soleil doré en haut à droite, de gros nuages crème aux ombres lilas ; deux chaînes de monts ronds couverts de forêt
# dans la brume ; au milieu, la MONTAGNE DE LA CASCADE (pierre chaude, mousse, glycines, trois arbres sur le sommet) et
# la grande cascade qui tombe dans la rivière turquoise ; à gauche une falaise moussue qui porte un vieux PÊCHER en
# fleurs et une bannière rouge ; à droite une falaise qui porte un bosquet de BAMBOUS, la STATUE de pierre d'un singe
# assis (bandeau d'or, yeux de jade) et deux bannières ; la berge d'herbe fleurie ; l'arène : une terrasse de grandes
# dalles ocre, calme, d'un bord à l'autre ; son flanc moussu ; dessous, le ruisseau sombre ; deux pierres dans les coins.
# Ce qui bouge : la cascade, son écume et sa brume, la rivière, deux fils d'eau lointains, les bambous, les bannières,
# les pétales du pêcher et quelques feuilles que le vent emporte vers la droite.
# La touche vivante (comme les dragons de Kael) : trois grues qui traversent le ciel (une proche, une plus loin, un vol
# de trois tout au loin) et l'ombre d'un singe qui saute d'arbre en arbre sur le sommet de la montagne.
# Le signe du clan (inventé, comme le pixel) : l'anneau d'or des singes serti d'un jade en haut, qui enroule une volute
# de vent.
#
#   python3 refonte-graphique/ui-moderne/fonds/eldra/eldra.py --fixe     # brouillons (vue du combat) pour composer
#   python3 refonte-graphique/ui-moderne/fonds/eldra/eldra.py            # images du jeu + calques + test + contrôles
#   python3 refonte-graphique/ui-moderne/fonds/eldra/eldra.py --video    # en plus : anim.gif et anim.mp4
#
# Sorties : public/art/vecto/fonds/eldra.webp (fixe ×2), eldra-anim.webp (planche ×2), fond-eldra.json et meta.json (à
# côté de ce fichier ; meta.json est repris par ../assemble_ts.py dans src/game/fond-vecto.ts) ;
# pixel/sortie/ui/vecto/fond-eldra/ (fond.png, situation.png, comparaison.png, anim.gif, anim.mp4, STATUT.txt).
import hashlib
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'pictos'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from lib import Shape, ellipse, mix, rpoly, ring  # noqa: E402
from atelier import sm, ribbon, bez, resample, sides  # noqa: E402

CLAN = 'eldra'
BROUILLON = os.environ.get('BROUILLON', '/tmp/fonds-brouillon')
TMP = os.path.join(BROUILLON, 'vecto-fond-' + CLAN)
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'fond-' + CLAN)
JEU = os.path.join(ROOT, 'public', 'art', 'vecto', 'fonds')
RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu-lot.cjs')

# ------------------------------------------------------------------------------------------------ les mesures
W, H = 590, 1100
UP = 2                          # les images du jeu sont rendues ×2 (vectoriel : plus fin que le pixel)
HZ, P0, P1 = 789, 800, 1047      # P0 = 800 : en combat, le rang du fond a ses pieds à 828
RANGS = (860, 934, 1007)
PERIODE = 19200                 # toutes les boucles divisent cette période : l'aperçu boucle sans couture
UNIT = 720 / W
HERO_X_U = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}
ENEMY_X_U = {0: 475, 1: 475, 2: 557, 3: 638, 4: 638}
ROW_OF = {0: 0, 3: 0, 2: 1, 1: 2, 4: 2}

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
# Reprises d'Eldra et de ses singes vectoriels (laque rouge, or, jade, fourrure fauve, nuage crème aux ombres lilas)
# et du fond pixel (pierre chaude, mousse, fleurs de pêcher, eau turquoise), mais plus sourdes.
INK = '#1f1238'                 # le contour (le raisin de l'interface), seulement sur les plans proches
CIEL = [(0, '#4c76a8'), (0.30, '#6c92bc'), (0.52, '#93abc6'), (0.68, '#b7b6c8'), (0.82, '#d8c2c2'),
        (0.93, '#ecccb8'), (1, '#f4d6b6')]
NUAGE = dict(base='#eedfd8', light='#faf0e8', rim='#ffffff', sh='#c2aecb')
LOIN1 = dict(base='#a3adc3', light='#adb6ca', rim='#c4cad8', sh='#97a1b9')        # la chaîne la plus lointaine
LOIN2 = dict(base='#86a1ab', light='#92acb2', rim='#b0c6c6', sh='#7792a0')        # la forêt plus proche
MONT = dict(base='#a07f79', light='#b89584', rim='#d6b69c', sh='#7e6068')         # la montagne (un voile d'air)
FAL = dict(base='#8c6a62', light='#a6806e', rim='#cca688', sh='#634854')          # les falaises (plan moyen)
ROC = dict(base='#725558', light='#8e6c64', rim='#bc957e', sh='#4c3843')          # les pierres du premier plan
MOUSSE = dict(base='#68905a', light='#80a862', rim='#b0cc80', sh='#476e4c')
FEUIL = dict(base='#5a8a5c', light='#74a062', rim='#a6c87e', sh='#3e6a50')
ROSE = dict(base='#e6a2b6', light='#f4c0cc', rim='#ffe6ec', sh='#c27c98')
ECORCE = dict(base='#6e4640', light='#8a5a48', rim='#b07a5a', sh='#4a2e32')
BAMBOU = dict(base='#6a9c58', light='#86b462', rim='#bcdc8a', sh='#467852')
GLYCINE = dict(base='#ac8ac4', light='#c6a8d8', rim='#e8d4f2', sh='#7e60a0')
STATUE = dict(base='#8e8690', light='#a89ea0', rim='#d0c4b6', sh='#605868')
ROUGE = dict(base='#b02e34', light='#cc443a', rim='#ee7c5c', sh='#74182e')
OR = dict(base='#d8a03c', light='#f0c058', rim='#fff0b0', sh='#9a6224')
BOIS = dict(base='#5a3a36', light='#76503e', rim='#a8785a', sh='#3a2430')
JADE = '#3cb894'
SOL = dict(back='#8e7660', front='#9a8166')                                         # l'arène : valeur moyenne
EAU = dict(deep='#3f8698', mid='#5c9eac', light='#8cc2c4', pale='#bcdcd6', foam='#eefaf6')


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


def encre(shapes, iw=1.0):
    """Le contour unique d'un objet fait de plusieurs morceaux : on trace tous les morceaux en encre (trait compris),
    puis on peint les morceaux par-dessus (les traits intérieurs sont recouverts)."""
    return ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        D(s), INK, INK, fm(2 * iw)) for s in shapes)


def polyline_d(pts):
    return 'M' + ' L'.join('%s %s' % (fm(x), fm(y)) for x, y in pts)


def lobes_shape(x0, x1, yb, lobes, sag=3):
    """Un nuage : dessous presque plat, dessus en lobes ronds (lobes = [(cx, cy, r)] de droite à gauche)."""
    pts = [(x0, yb - 2), (x0 + (x1 - x0) * 0.3, yb + sag), (x0 + (x1 - x0) * 0.7, yb + sag * 0.6), (x1, yb - 2)]
    sharp = []
    for k, (cx, cy, r) in enumerate(lobes):
        if k > 0:
            sharp.append(len(pts))
        for a in (5, 50, 90, 130, 175):
            ra = math.radians(a)
            pts.append((cx + r * math.cos(ra), cy - r * math.sin(ra)))
    return sm(pts, sharp=tuple(sharp), t=0.9)


def interp(pts, x):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if xa <= x <= xb:
            return ya + (yb - ya) * (x - xa) / ((xb - xa) or 1)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]


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


def membre(pts, w0, w1, n=10):
    """Un membre arrondi (bras, jambe, queue, tige) le long d'une ligne douce, de la largeur w0 à w1."""
    c = resample(catmull(pts, 4), n)
    ws = [w0 + (w1 - w0) * i / n for i in range(n + 1)]
    return ribbon(c, ws, sharp_ends=False)


def feuille(x, y, ang, L, w):
    """Une feuille en lame (bambou, fougère) : attachée en (x, y), pointe dans la direction ang (degrés), longueur L."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def P(u, v):
        return (x + u * ca - v * sa, y + u * sa + v * ca)
    return sm([P(0, 0), P(L * 0.3, -w * 0.5), P(L * 0.7, -w * 0.32), P(L, 0), P(L * 0.66, w * 0.36),
               P(L * 0.28, w * 0.46)], sharp=(0, 3), t=0.8)


# ------------------------------------------------------------------------------------------------ les profils
# La falaise de gauche (le pêcher) et celle de droite (les bambous, la statue) sont plus basses que la montagne : on
# voit la forêt lointaine au-dessus d'elles ; leurs faces tournées vers l'arène tiennent dans ce que montre le combat.
FAL_G_HAUT = [(-14, 596), (20, 592), (52, 598), (84, 608), (112, 616), (140, 622), (164, 632), (182, 646)]
FAL_G_FACE = [(192, 670), (188, 700), (196, 736), (204, 772)]
FAL_D_FACE = [(400, 772), (406, 740), (400, 706), (408, 672), (416, 646)]
FAL_D_HAUT = [(428, 628), (452, 620), (480, 614), (510, 606), (540, 598), (572, 592), (604, 588)]


def sol_g(x):
    return interp(FAL_G_HAUT, x)


def sol_d(x):
    return interp(FAL_D_HAUT, x)


# ================================================================================================ LES ÉLÉMENTS
# Chaque élément : id, profondeur, genre ('fixe' : dans l'image fixe seulement ; 'boucle' ; 'morceau' = une boucle
# d'une image remise par-dessus ; 'defile' ; 'particules') et sa fonction de dessin.
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
SOLEIL = (452, 396)          # vu sur tous les téléphones, à droite des pilules du haut


@element('ciel', -29.9, 'fixe')
def ciel(doc):
    out = [path('M-20 -20H610V840H-20Z', doc.lin(0, 0, 0, 800, CIEL))]
    # la lueur chaude de l'horizon (le matin)
    out.append('<ellipse cx="330" cy="800" rx="420" ry="230" fill="%s"/>' % doc.rad(
        330, 800, 420, [(0, '#fbe4c4', 0.55), (0.5, '#f4d2bc', 0.22), (1, '#e8c8c0', 0)], ry=230))
    # le soleil doré en haut à droite (la seule lumière)
    sx, sy = SOLEIL
    out.append('<circle cx="%d" cy="%d" r="130" fill="%s"/>' % (sx, sy, doc.rad(
        sx, sy, 130, [(0, '#fff2d2', 0.50), (0.35, '#fbe2c0', 0.20), (1, '#e8d0c8', 0)])))
    out.append('<circle cx="%d" cy="%d" r="20" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 6, sy - 6, 26, [(0, '#fffcf0'), (0.65, '#fff0cc'), (1, '#f8d8a0')])))
    return ''.join(out)


@element('nuages', -29.5, 'fixe')
def nuages(doc):
    out = []
    # A : le grand banc en haut à gauche (le haut des téléphones longs)
    a = lobes_shape(-30, 300, 318, [(282, 306, 16), (246, 288, 28), (200, 270, 36), (148, 262, 40), (94, 254, 42),
                                    (42, 260, 38), (-4, 272, 34), (-30, 290, 26)], sag=6)
    out.append(vol(doc, a, NUAGE, r=2.2, c=4.5))
    a2 = lobes_shape(-30, 230, 214, [(214, 204, 14), (180, 192, 24), (136, 180, 28), (88, 176, 30), (40, 182, 28),
                                     (-6, 190, 26), (-30, 202, 18)], sag=4)
    out.append(vol(doc, a2, dict(NUAGE, base='#e2d6dc', light='#eee4e6', sh='#b6a6c6'), r=2, c=3.5))
    # B : en haut à droite
    b = lobes_shape(370, 620, 290, [(612, 278, 16), (578, 264, 24), (538, 256, 26), (494, 262, 22), (452, 270, 18),
                                    (404, 280, 14)], sag=3)
    out.append(vol(doc, b, NUAGE, r=2, c=3.5))
    # C : un petit banc qui voile le bas du soleil ; E : un petit à gauche, sous le banc A
    c = lobes_shape(466, 620, 424, [(610, 416, 11), (580, 406, 15), (544, 404, 14), (506, 410, 12), (478, 416, 8)],
                    sag=2)
    out.append(vol(doc, c, dict(NUAGE, base='#f2e2da', sh='#ccb6c8'), r=1.8, c=2.8))
    e = lobes_shape(96, 226, 372, [(216, 366, 9), (188, 356, 13), (150, 352, 15), (114, 358, 11)], sag=2)
    out.append(vol(doc, e, dict(NUAGE, base='#eadcdc', sh='#c2b0c8'), r=1.8, c=2.8))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
def crete(x0, x1, domes, bosses=0.0, graine=1, pas=7):
    """Le profil d'une chaîne de monts ronds : le plus haut des dômes (cx, sommet, demi-largeur) en chaque x, avec de
    petites bosses irrégulières d'arbres (bosses = leur hauteur)."""
    pts = []
    x = x0
    i = 0
    while x <= x1:
        y = min(top + 46 * ((x - cx) / hw) ** 2 for cx, top, hw in domes)
        if bosses:
            y -= bosses * abs(math.sin(x * 0.21 + graine) * 0.7 + math.sin(x * 0.083 + 2 * graine) * 0.5)
        pts.append((x, y))
        x += pas + 2 * math.sin(i * 1.7 + graine)
        i += 1
    return pts


@element('lointain', -28.5, 'fixe')
def lointain(doc):
    out = []
    r1 = crete(-20, 610, [(-10, 566, 90), (130, 552, 80), (262, 566, 86), (388, 548, 84), (520, 560, 90)], 2.2, 1)
    s1 = sm([(-20, 800)] + r1 + [(610, 800)], sharp=(0, len(r1) + 1), t=0.7)
    out.append(vol(doc, s1, LOIN1, grad=doc.lin(0, 548, 0, 680, [(0, LOIN1['light']), (1, LOIN1['sh'])]), r=1.2, c=0))
    r2 = crete(-20, 610, [(40, 606, 80), (170, 620, 70), (300, 612, 80), (440, 598, 86), (566, 614, 80)], 3.4, 4)
    s2 = sm([(-20, 800)] + r2 + [(610, 800)], sharp=(0, len(r2) + 1), t=0.7)
    out.append(vol(doc, s2, LOIN2, grad=doc.lin(0, 596, 0, 720, [(0, LOIN2['light']), (0.6, LOIN2['base']),
                                                                 (1, LOIN2['sh'])]), r=1.4, c=0))
    # quelques grands arbres ronds sur la forêt proche (des têtes plus sombres, côté ombre), dans la brume
    cl = doc.clip(s2.d())
    inner = []
    for x, y, r in ((22, 612, 13), (74, 618, 11), (392, 606, 12), (476, 604, 13), (528, 612, 11), (586, 618, 12)):
        t_ = sm([(x - r, y + r * 0.6), (x - r * 0.9, y - r * 0.2), (x - r * 0.3, y - r * 0.75), (x + r * 0.4, y - r * 0.7),
                 (x + r, y - r * 0.1), (x + r * 0.9, y + r * 0.6)], t=0.9)
        inner.append(path(t_, LOIN2['sh'], 0.45))
        inner.append(path(t_.move(1.2, -1.2), LOIN2['rim'], 0.25))
    out.append('<g clip-path="%s">%s</g>' % (cl, ''.join(inner)))
    return ''.join(out)


# deux fils d'eau tombent de la forêt lointaine, dans les trouées entre la montagne et les falaises
FILS = [(201, 624, 664, 2.2), (398, 610, 652, 2.6)]          # x, haut, bas, largeur


@element('fils-fixe', -28.4, 'fixe')
def fils_fixe(doc):
    out = []
    for x, y0, y1, w in FILS:
        out.append(path(rpoly([(x - w / 2, y0), (x + w / 2, y0), (x + w / 2 + 0.6, y1), (x - w / 2 - 0.6, y1)], 0.8),
                        doc.lin(0, y0, 0, y1, [(0, '#dcecee', 0.85), (0.8, '#cfe2e6', 0.6), (1, '#cfe2e6', 0)])))
    return ''.join(out)


def fil(k):
    x, y0, y1, w = FILS[k]

    def fn(doc, ph):
        out = []
        for s0 in (0.0, 0.5):
            u = (s0 + ph) % 1
            y = y0 + u * (y1 - y0)
            out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="7" fill="%s"/>' % (fm(x), fm(y), fm(w * 0.55), doc.rad(
                x, y, w * 0.55, [(0, '#ffffff', 0.85 * (1 - u)), (1, '#ffffff', 0)], ry=7)))
        return '<g clip-path="%s">%s</g>' % (doc.clip('M%s %sH%sV%sH%sZ' % (
            fm(x - w), y0, fm(x + w), y1, fm(x - w))), ''.join(out))
    return fn


element('fil1', -28.3, 'boucle', box=(FILS[0][0] - 3, FILS[0][1], 6, FILS[0][2] - FILS[0][1]), n=8, ms=200)(fil(0))
element('fil2', -28.3, 'boucle', box=(FILS[1][0] - 3, FILS[1][1], 6, FILS[1][2] - FILS[1][1]), n=8, ms=200)(fil(1))


@element('brume', -27, 'fixe')
def brume(doc):
    # la brume chaude du matin passe devant la forêt lointaine (pas devant la montagne ni les falaises)
    return path('M-10 600H600V800H-10Z', doc.lin(0, 600, 0, 790, [(0, '#f0d8c8', 0), (0.55, '#f0d4c4', 0.35),
                                                                  (1, '#f4dcc8', 0.7)]))


# ---------------------------------------------------------------------------------------------------- la montagne
MONTAGNE = [(190, 792), (198, 744), (208, 700), (206, 660), (214, 620), (218, 580), (226, 540), (230, 508),
            (240, 490), (256, 482), (274, 488), (284, 490), (310, 490), (318, 486), (336, 480), (352, 486),
            (362, 500), (366, 532), (374, 572), (380, 616), (390, 664), (388, 712), (398, 752), (406, 792)]
# La montagne est dessinée dans ses coordonnées d'origine puis étirée vers le haut (×1,08 depuis son pied, y = 792) :
# plus haute, comme dans le pixel, son sommet reste sous les pilules du haut.
MONT_K = 1.08


def MY(y):
    return 792 - (792 - y) * MONT_K


ARBRES = [(256, MY(485), 18, 'vert'), (298, MY(491), 20, 'rose'), (340, MY(483), 17, 'vert')]   # x, y du pied, rayon
CASC_X, CASC_Y0_BRUT, CASC_W = 297, 498, 28                                                 # la grande cascade
CASC_Y0 = round(MY(CASC_Y0_BRUT))


def montagne_forme():
    return sm(MONTAGNE, sharp=(0, len(MONTAGNE) - 1), t=0.8)


def buisson(doc, x, y, r, fleurs=True, m=MOUSSE, voile=0.0):
    """Un buisson rond posé sur une corniche (son pied en (x, y)), quelques grappes roses dessus."""
    s = sm([(x - r, y + 1), (x - r * 0.95, y - r * 0.45), (x - r * 0.45, y - r * 0.95), (x + r * 0.2, y - r * 1.05),
            (x + r * 0.8, y - r * 0.6), (x + r, y + 1)], sharp=(0, 5), t=0.9)
    mm = {k: mix(v, '#d8c6c8', voile) for k, v in m.items()}
    out = [vol(doc, s, mm, r=1.0, c=1.4)]
    if fleurs:
        for dx, dy, rr in ((-0.35, -0.55, 0.28), (0.3, -0.75, 0.24), (0.55, -0.25, 0.2)):
            f = ellipse(x + dx * r, y + dy * r, rr * r, rr * r * 0.8)
            out.append(vol(doc, f, {k: mix(v, '#d8c6c8', voile) for k, v in ROSE.items()}, r=0.5, c=0.6))
    return ''.join(out)


def glycine(doc, x, y, n=2, L=16, voile=0.0):
    """Des grappes de glycine qui pendent d'un rebord en (x, y) : une ou deux grandes grappes lilas (bord en petites
    bosses irrégulières, pointe en bas), une feuille au-dessus."""
    out = []
    mm = {k: mix(v, '#d8c6c8', voile) for k, v in GLYCINE.items()}
    for i in range(n):
        dx = (i - (n - 1) / 2) * 7.5
        ln = L * (1.0 if i % 2 == 0 else 0.72)
        w = 4.2 if i % 2 == 0 else 3.4
        g = []
        for j, t in enumerate((0.0, 0.22, 0.45, 0.68)):
            g.append((x + dx - w * (1 - t) ** 0.8 - 0.7 * (j % 2), y + 1 + t * ln))
        g.append((x + dx + 0.4, y + ln))
        for j, t in enumerate((0.68, 0.45, 0.22, 0.0)):
            g.append((x + dx + w * (1 - t) ** 0.8 + 0.7 * ((j + 1) % 2), y + 1 + t * ln))
        out.append(vol(doc, sm(g, sharp=(4,), t=0.9), mm, r=0.8, c=1.1))
    f = feuille(x - 2, y + 1, 170, 9, 3.6)
    out.append(vol(doc, f, {k: mix(v, '#d8c6c8', voile) for k, v in FEUIL.items()}, r=0.5, c=0.6))
    return ''.join(out)


@element('montagne', -24, 'fixe')
def montagne(doc):
    return '<g transform="translate(0 792) scale(1 %s) translate(0 -792)">%s</g>' % (fm(MONT_K), montagne_brut(doc))


def montagne_brut(doc):
    out = []
    s = montagne_forme()
    g = doc.lin(400, 520, 220, 700, [(0, MONT['light']), (0.5, MONT['base']), (1, MONT['sh'])])
    out.append(vol(doc, s, MONT, grad=g, r=2.0, c=3.4))
    inner = []
    # les grands pans de roche : des ombres douces côté gauche, un pan clair côté lumière (peu, irréguliers)
    inner.append(path(sm([(190, 580), (232, 530), (248, 580), (242, 650), (256, 720), (248, 792), (184, 792)], t=0.8),
                      MONT['sh'], 0.4))
    inner.append(path(sm([(332, 500), (360, 500), (370, 570), (380, 640), (386, 720), (364, 700), (352, 610),
                          (338, 550)], t=0.8), MONT['light'], 0.55))
    # le creux humide derrière la cascade (plus sombre, un peu bleuté)
    inner.append(path(sm([(CASC_X - 20, CASC_Y0_BRUT - 4), (CASC_X + 20, CASC_Y0_BRUT - 4), (CASC_X + 24, 600), (CASC_X + 26, 700),
                          (CASC_X + 30, 792), (CASC_X - 30, 792), (CASC_X - 26, 700), (CASC_X - 24, 600)], t=0.8),
                      '#6a5a6a', 0.45))
    # deux corniches (de grandes marches : un dessus clair, une ombre douce dessous)
    for pts in ([(208, 590), (236, 584), (264, 588)], [(332, 634), (358, 628), (386, 634)],
                [(212, 696), (240, 690), (266, 694)]):
        c = resample(catmull(pts), 16)
        n_ = len(c) - 1
        wl = [0.6 + 5 * math.sin(math.pi * i / n_) ** 0.8 for i in range(n_ + 1)]
        inner.append(path(ribbon([(x, y + 4) for x, y in c], wl), MONT['sh'], 0.5))
        inner.append(path(ribbon(c, [w * 0.4 for w in wl]), MONT['rim'], 0.5))
    # la brume du pied (la montagne se fond dans l'air du matin)
    inner.append(path('M150 640H450V800H150Z', doc.lin(0, 660, 0, 790, [(0, '#f0d8c8', 0), (1, '#f2dac8', 0.55)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    # la mousse du sommet (un chapeau vert aux bords festonnés)
    top = [(p[0], p[1]) for p in MONTAGNE[7:17]]
    cap = [(226, 540)] + [(x, y - 1.5) for x, y in top] + [(366, 532)]
    bas = [(362, 520), (352, 508), (340, 512), (326, 504), (312, 508), (284, 508), (270, 504), (256, 512),
           (244, 506), (236, 526)]
    out.append(vol(doc, sm(cap + bas, t=0.8), {k: mix(v, '#cfc0c4', 0.12) for k, v in MOUSSE.items()}, r=1.4, c=2.0))
    # des buissons et des glycines sur les corniches
    out.append(buisson(doc, 240, 583, 8, voile=0.15))
    out.append(buisson(doc, 360, 629, 7, fleurs=False, voile=0.18))
    out.append(glycine(doc, 222, 592, 2, 18, voile=0.12))
    out.append(glycine(doc, 372, 512, 2, 16, voile=0.12))
    return ''.join(out)


def arbre(doc, x, y, r, sorte, voile=0.1):
    """Un arbre rond posé sur le sommet : un tronc court, une couronne en lobes (verte, ou rose en fleurs)."""
    m = {k: mix(v, '#d6c8cc', voile) for k, v in (ROSE if sorte == 'rose' else FEUIL).items()}
    e = {k: mix(v, '#d6c8cc', voile) for k, v in ECORCE.items()}
    out = []
    tronc = sm([(x - 2.2, y + 1), (x - 1.6, y - r * 0.7), (x + 1.4, y - r * 0.7), (x + 2.2, y + 1)], sharp=(0, 3), t=0.8)
    out.append(vol(doc, tronc, e, r=0.6, c=0.8))
    cy = y - r * 0.95
    lob = [(x + r * 0.95, cy + r * 0.2, r * 0.42), (x + r * 0.55, cy - r * 0.45, r * 0.5), (x - r * 0.05, cy - r * 0.6,
           r * 0.52), (x - r * 0.62, cy - r * 0.32, r * 0.48), (x - r * 0.95, cy + r * 0.22, r * 0.4)]
    pts = [(x - r * 1.0, cy + r * 0.45), (x - r * 0.2, cy + r * 0.62), (x + r * 0.6, cy + r * 0.55),
           (x + r * 1.05, cy + r * 0.42)]
    sharp = []
    for k, (lx, ly, lr) in enumerate(lob):
        if k > 0:
            sharp.append(len(pts))
        for a in (10, 60, 110, 165):
            ra = math.radians(a)
            pts.append((lx + lr * math.cos(ra), ly - lr * math.sin(ra)))
    cour = sm(pts, sharp=tuple(sharp), t=0.85)
    out.append(vol(doc, cour, m, r=1.3, c=2.2))
    # un lobe d'ombre à gauche (le volume)
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(cour.d()), path(ellipse(x - r * 0.7, cy + r * 0.3, r * 0.6,
                                                                               r * 0.5), m['sh'], 0.35)))
    return ''.join(out)


@element('arbres', -23.9, 'fixe')
def arbres(doc):
    return ''.join(arbre(doc, x, y, r, s) for x, y, r, s in ARBRES)


# ---------------------------------------------------------------------------------------------------- la cascade
CASC = (CASC_X - CASC_W // 2, CASC_Y0, CASC_W, 760 - CASC_Y0)      # la boîte du défilé (x, y, w, h)
CASC_T = (CASC_W, 128)                                             # la tuile (elle coule de 80 px/s : 1,6 s par tour)


def cascade_tuile(doc):
    """La tuile de la cascade (28 × 128), qui se répète exactement en hauteur : l'eau claire, plus sombre à gauche
    (l'ombre), plus claire à droite (la lumière), des paquets d'écume allongés qui descendent."""
    tw, th = CASC_T
    out = [path('M0 0H%dV%dH0Z' % (tw, th), doc.lin(0, 0, tw, 0, [
        (0, EAU['deep']), (0.3, EAU['mid']), (0.7, EAU['light']), (1, EAU['pale'])]))]
    taches = [(0.30, 6, 3.0, 14, '#ffffff', 0.55), (0.62, 30, 2.6, 18, '#ffffff', 0.5), (0.18, 52, 2.2, 10, '#ffffff', 0.4),
              (0.78, 70, 2.8, 16, '#ffffff', 0.6), (0.45, 96, 3.2, 20, '#ffffff', 0.5), (0.85, 118, 2.0, 12, '#ffffff', 0.5),
              (0.12, 88, 2.0, 16, EAU['deep'], 0.4), (0.55, 64, 2.2, 12, EAU['deep'], 0.3),
              (0.38, 120, 1.8, 10, EAU['deep'], 0.3), (0.92, 40, 1.6, 14, '#ffffff', 0.45)]
    for u, y, rx, ry, col, op in taches:
        for dy in (-th, 0, th):
            out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(u * tw), fm(y + dy), fm(rx), fm(ry), doc.rad(u * tw, y + dy, rx, [(0, col, op), (0.6, col, op * 0.5),
                                                                                   (1, col, 0)], ry=ry)))
    # le bord gauche plus sombre, le bord droit éclairé (un fil)
    out.append(path('M0 0H2V%dH0Z' % th, EAU['deep'], 0.6))
    out.append(path('M%s 0H%dV%dH%sZ' % (fm(tw - 1.4), tw, th, fm(tw - 1.4)), '#f2fffa', 0.6))
    return out


element('cascade', -23, 'defile', box=CASC, tuile=CASC_T, vx=0.0, vy=80.0, tuile_dessin=cascade_tuile)


@element('cascade-haut', -22.9, 'morceau', box=(CASC_X - 24, CASC_Y0 - 10, 48, 22))
def cascade_haut(doc):
    """La lèvre d'où l'eau sort : deux pierres moussues de chaque côté, l'eau qui s'arrondit et blanchit."""
    x = CASC_X
    out = []
    lip = sm([(x - CASC_W / 2 - 1, CASC_Y0 + 5), (x - CASC_W / 2 + 2, CASC_Y0 - 3), (x, CASC_Y0 - 6),
              (x + CASC_W / 2 - 2, CASC_Y0 - 3), (x + CASC_W / 2 + 1, CASC_Y0 + 5), (x, CASC_Y0 + 8)], t=0.9)
    out.append(path(lip, doc.lin(x - 14, 0, x + 14, 0, [(0, EAU['light']), (0.6, EAU['pale']), (1, '#f4fffb')])))
    out.append('<ellipse cx="%s" cy="%s" rx="13" ry="4" fill="%s"/>' % (x, CASC_Y0 + 3, doc.rad(
        x, CASC_Y0 + 3, 13, [(0, '#ffffff', 0.8), (1, '#ffffff', 0)], ry=4)))
    for sg in (-1, 1):
        px = x + sg * (CASC_W / 2 + 4)
        p = sm([(px - 9, CASC_Y0 + 9), (px - 8, CASC_Y0 + 2), (px - 3, CASC_Y0 - 3), (px + 4, CASC_Y0 - 3.5),
                (px + 9, CASC_Y0 + 2), (px + 9, CASC_Y0 + 9)], sharp=(0, 5), t=0.85)
        out.append(vol(doc, p, {k: mix(v, '#cfc0c4', 0.12) for k, v in MOUSSE.items()}, r=1.0, c=1.4))
    return ''.join(out)


def ecume(doc, ph):
    """Le pied de la cascade : l'écume qui bouillonne sur la rivière (des lobes blancs qui gonflent et retombent)."""
    x, y = CASC_X, 758
    out = ['<ellipse cx="%s" cy="%s" rx="34" ry="9" fill="%s"/>' % (x, y, doc.rad(
        x, y, 34, [(0, '#ffffff', 0.55), (0.6, '#e8f8f4', 0.25), (1, '#e8f8f4', 0)], ry=9))]
    lobes = []
    for j, (dx, r0) in enumerate(((-16, 5.0), (-8, 6.5), (0, 7.5), (8, 6.4), (16, 5.0), (-24, 3.6), (24, 3.6))):
        b = 0.5 + 0.5 * math.sin(2 * math.pi * (ph * 2 + j * 0.37))
        lobes.append((x + dx, y - 1 - 1.6 * b, r0 * (0.85 + 0.25 * b)))
    pts = [(x - 30, y + 3), (x - 12, y + 5), (x + 12, y + 5), (x + 30, y + 3)]
    sharp = []
    for k, (lx, ly, lr) in enumerate(sorted(lobes, key=lambda l: -l[0])):
        if k > 0:
            sharp.append(len(pts))
        for a in (10, 60, 120, 170):
            ra = math.radians(a)
            pts.append((lx + lr * math.cos(ra), ly - lr * 0.8 * math.sin(ra)))
    s = sm(pts, sharp=tuple(sharp), t=0.85)
    out.append(vol(doc, s, dict(base='#e8f6f4', light='#ffffff', rim='#ffffff', sh='#a8d4d4'), r=0.8, c=1.6))
    return ''.join(out)


element('ecume', -17.9, 'boucle', box=(CASC_X - 36, 742, 72, 26), n=8, ms=150)(ecume)


def brume_image(doc, i, n):
    """Une bouffée de brume (une image de sa vie) : elle grossit et s'efface."""
    t = i / (n - 1)
    r = 5 + 9 * t
    op = min(1, 0.3 + 2 * t) if t < 0.4 else (1 - (t - 0.4) / 0.6) ** 1.2
    cx = cy = 15
    s = lobes_shape(cx - r * 1.2, cx + r * 1.2, cy + r * 0.5, [(cx + r * 0.6, cy - r * 0.05, r * 0.6),
                                                             (cx - 0.1 * r, cy - r * 0.3, r * 0.78),
                                                             (cx - r * 0.7, cy + r * 0.05, r * 0.52)], sag=r * 0.1)
    return '<g opacity="%g">%s</g>' % (op * 0.55, path(s, '#ffffff'))


element('brume-chute', -17.8, 'particules', taille=(30, 30), images=6, dessin=brume_image,
        zone=(CASC_X - 14, 748, CASC_X + 10, 754), nombre=5, vie=(2800, 3800), vx=(2, 6), vy=(-9, -5),
        ondule=(1.5, 2000))


# ---------------------------------------------------------------------------------------------------- les falaises
def falaise_g_forme():
    pts = [(-14, 790)] + FAL_G_HAUT + FAL_G_FACE + [(214, 790)]
    return sm(pts, sharp=(0, 1, len(pts) - 1), t=0.75)


def falaise_d_forme():
    pts = FAL_D_FACE + FAL_D_HAUT + [(604, 790), (392, 790)]
    return sm(pts, sharp=(len(pts) - 3, len(pts) - 2, len(pts) - 1, 0), t=0.75)


def chapeau(doc, haut, x0, x1, graine):
    """La mousse qui couvre le dessus d'une falaise : elle suit le bord et retombe en festons irréguliers."""
    top = [(x, interp(haut, x) - 1.5) for x in range(int(x0), int(x1) + 1, 8)]
    bas = []
    for i, (x, y) in enumerate(reversed(top)):
        bas.append((x, y + 9 + 7 * abs(math.sin(i * 1.3 + graine)) + 3 * math.sin(i * 0.7 + graine)))
    return sm(top + bas, sharp=(0, len(top) - 1, len(top)), t=0.8)


@element('falaises', -20, 'fixe')
def falaises(doc):
    out = []
    for forme, droite in ((falaise_g_forme(), False), (falaise_d_forme(), True)):
        xs = [p[0] for p in forme.pts()]
        x0, x1 = min(xs), max(xs)
        g = doc.lin(x1, 620, x0 + 20, 780, [(0, FAL['light']), (0.45, FAL['base']), (1, FAL['sh'])])
        out.append(vol(doc, forme, FAL, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0))
        inner = []
        if not droite:
            # la face de droite (tournée vers la lumière), un grand pan plus clair ; une ombre côté gauche
            inner.append(path(sm([(146, 630), (180, 646), (194, 680), (190, 720), (200, 750), (208, 790), (164, 790),
                                  (158, 730), (154, 680)], t=0.8), FAL['light'], 0.6))
            inner.append(path(sm([(-14, 640), (40, 660), (74, 730), (60, 790), (-14, 790)], t=0.8), FAL['sh'], 0.45))
            corn = [[(10, 664), (50, 658), (92, 664), (124, 672)]]
        else:
            inner.append(path(sm([(470, 630), (604, 600), (604, 740), (540, 750), (500, 690)], t=0.8), FAL['light'], 0.5))
            inner.append(path(sm([(394, 670), (432, 670), (442, 740), (432, 790), (394, 790)], t=0.8), FAL['sh'], 0.45))
            corn = [[(440, 700), (472, 692), (504, 698)], [(520, 650), (560, 642), (600, 646)]]
        for pts in corn:
            c = resample(catmull(pts), 16)
            n_ = len(c) - 1
            wl = [0.6 + 6.5 * math.sin(math.pi * i / n_) ** 0.8 for i in range(n_ + 1)]
            inner.append(path(ribbon([(x, y + 4) for x, y in c], wl), FAL['sh'], 0.5))
            inner.append(path(ribbon(c, [w * 0.4 for w in wl]), FAL['rim'], 0.45))
        # l'eau d'en bas éclaire à peine le pied (un reflet frais)
        inner.append(path('M-20 720H610V800H-20Z', doc.lin(0, 728, 0, 790, [(0, '#9ad0cc', 0), (1, '#9ad0cc', 0.22)])))
        out.append('<g clip-path="%s">%s</g>' % (doc.clip(forme.d()), ''.join(inner)))
        # la mousse du dessus
        if droite:
            out.append(vol(doc, chapeau(doc, FAL_D_HAUT, 420, 604, 2), MOUSSE, r=1.6, c=2.2, ink=INK, iw=0.8))
        else:
            out.append(vol(doc, chapeau(doc, FAL_G_HAUT, -14, 186, 5), MOUSSE, r=1.6, c=2.2, ink=INK, iw=0.8))
    # de longues mèches de mousse qui retombent du dessus, sur la face tournée vers l'arène
    for x, L, w in ((150, 30, 9), (176, 44, 8), (436, 40, 9), (462, 24, 8), (530, 30, 10)):
        y = (sol_g(x) if x < 300 else sol_d(x)) + 6
        m = sm([(x - w, y - 2), (x + w, y - 2), (x + w * 0.7, y + L * 0.45), (x + w * 0.2, y + L),
                (x - w * 0.35, y + L * 0.72), (x - w * 0.8, y + L * 0.35)], sharp=(0, 1, 3), t=0.85)
        out.append(vol(doc, m, MOUSSE, r=1.0, c=1.6))
    # buissons et glycines sur les faces
    out.append(buisson(doc, 474, 695, 7))
    out.append(glycine(doc, 180, 652, 2, 18))
    out.append(glycine(doc, 420, 640, 2, 17))
    return ''.join(out)


@element('buissons-rive', -18.5, 'fixe')
def buissons_rive(doc):
    """Une frange de buissons ronds au pied des falaises et de la montagne, de l'autre côté de la rivière (leur bas
    est caché par l'eau) : des tailles et des écarts différents, quelques fleurs."""
    out = []
    x, i = -12, 0
    while x < 604:
        r = 7 + 5 * abs(math.sin(i * 1.7)) + 2 * math.sin(i * 0.6)
        if not (CASC_X - 22 < x < CASC_X + 22):
            fl = (i % 3 == 1)
            out.append(buisson(doc, x, 753, r, fleurs=fl, m=MOUSSE if i % 2 else FEUIL,
                               voile=0.18 if 190 < x < 410 else 0.06))
        x += r * 1.5 + 4 * abs(math.sin(i * 2.3))
        i += 1
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le pêcher
PECHER = (122, sol_g(122))


@element('pecher', -19.8, 'fixe')
def pecher(doc):
    """Le vieux pêcher en fleurs posé sur la falaise de gauche : un tronc tordu, deux branches, une large couronne
    rose en grappes ; un seul contour pour tout l'arbre."""
    x, y = PECHER
    tronc = membre([(x - 2, y + 1), (x + 1, y - 14), (x - 3, y - 30), (x + 4, y - 46), (x + 10, y - 58)], 9, 4.5)
    br1 = membre([(x - 2, y - 30), (x - 16, y - 44), (x - 30, y - 56)], 4.5, 2.2, 8)
    br2 = membre([(x + 4, y - 46), (x + 22, y - 58), (x + 40, y - 64)], 4.0, 2.0, 8)
    racine = sm([(x - 12, y + 2), (x - 6, y - 4), (x + 6, y - 4), (x + 12, y + 2)], sharp=(0, 3), t=0.8)
    cx, cy = x + 6, y - 82
    grappes = [(cx - 40, cy + 18, 17), (cx - 24, cy - 2, 21), (cx, cy - 12, 24), (cx + 26, cy - 4, 21),
               (cx + 44, cy + 14, 16), (cx + 16, cy + 18, 18), (cx - 12, cy + 20, 17)]
    cour = None
    for gx, gy, gr in grappes:
        e = ellipse(gx, gy, gr, gr * 0.86)
        cour = e if cour is None else cour + e
    out = [encre([tronc, br1, br2, racine] + [ellipse(gx, gy, gr, gr * 0.86) for gx, gy, gr in grappes], 1.0)]
    for s in (racine, tronc, br1, br2):
        out.append(vol(doc, s, ECORCE, r=0.9, c=1.4))
    # la couronne : une forme, éclairée en haut à droite, des grappes d'ombre dessous et quelques grappes claires
    g = doc.lin(cx + 50, cy - 36, cx - 30, cy + 40, [(0, ROSE['light']), (0.5, ROSE['base']), (1, ROSE['sh'])])
    out.append(vol(doc, cour, ROSE, grad=g, r=1.8, c=3.0))
    inner = []
    for gx, gy, gr, col, op in ((cx - 30, cy + 26, 12, ROSE['sh'], 0.45), (cx + 2, cy + 28, 13, ROSE['sh'], 0.4),
                                (cx + 32, cy + 22, 10, ROSE['sh'], 0.35), (cx + 14, cy - 18, 10, ROSE['rim'], 0.4),
                                (cx - 18, cy - 10, 8, ROSE['rim'], 0.3), (cx + 36, cy - 2, 7, ROSE['rim'], 0.35)):
        inner.append(path(ellipse(gx, gy, gr, gr * 0.8), col, op))
    # les branches se voient un peu entre les grappes du bas
    inner.append(path(membre([(x + 10, y - 58), (x + 6, y - 74), (x - 6, y - 86)], 2.6, 1.2, 6), ECORCE['base'], 0.7))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(cour.d()), ''.join(inner)))
    return ''.join(out)


def petale_image(doc, i, n):
    """Un pétale qui tourne sur lui-même en volant."""
    a = 2 * math.pi * i / n
    sx = 0.35 + 0.65 * abs(math.cos(a))
    p = sm([(0, -2.6), (1.6, -0.6), (0.9, 2.2), (0, 2.8), (-0.9, 2.2), (-1.6, -0.6)], t=0.9)
    p = p.map(lambda q: (5 + q[0] * sx * math.cos(a * 0.5) - q[1] * math.sin(a * 0.5),
                         5 + q[0] * sx * math.sin(a * 0.5) + q[1] * math.cos(a * 0.5)))
    return path(p, mix(ROSE['light'], ROSE['base'], 0.5 + 0.5 * math.sin(a))) + path(p, ROSE['rim'], 0.35)


def feuille_image(doc, i, n):
    """Une petite feuille verte qui tourne en volant."""
    a = 2 * math.pi * i / n
    sx = 0.3 + 0.7 * abs(math.cos(a))
    f = feuille(0, 0, 0, 9, 3.6).map(lambda q: (q[0] - 4.5, q[1] * sx))
    f = f.map(lambda q: (6 + q[0] * math.cos(a * 0.5 + 0.4) - q[1] * math.sin(a * 0.5 + 0.4),
                         6 + q[0] * math.sin(a * 0.5 + 0.4) + q[1] * math.cos(a * 0.5 + 0.4)))
    return path(f, mix(BAMBOU['light'], BAMBOU['base'], 0.5 + 0.5 * math.sin(a)))


# les pétales partent de la couronne du pêcher et le vent les porte vers la droite (ils s'éteignent avant la berge)
element('petales', -14, 'particules', taille=(10, 10), images=8, ms=120, dessin=petale_image,
        zone=(96, 528, 176, 580), nombre=7, vie=(6000, 9000), vx=(14, 24), vy=(3, 8), ondule=(4, 2400))
# quelques feuilles arrivent de la gauche, haut dans le ciel, et traversent tout le décor
element('feuilles', -13.9, 'particules', taille=(12, 12), images=8, ms=140, dessin=feuille_image,
        zone=(-10, 470, -6, 560), nombre=2, vie=(16000, 19200), vx=(36, 44), vy=(-1, 3), ondule=(7, 3200))


# ---------------------------------------------------------------------------------------------------- les bambous
# (x du pied, hauteur, penche, épaisseur) ; le pied est posé sur le dessus de la falaise de droite. Le haut se
# balance (un calque), le bas reste dans l'image fixe : on coupe à BCUT, là où le balancement est encore nul.
TIGES = [(440, 196, -0.07, 4.2), (456, 236, 0.02, 4.8), (474, 186, -0.03, 4.0), (492, 230, -0.05, 5.0),
         (514, 208, 0.04, 4.4), (536, 220, -0.03, 4.8), (560, 196, 0.05, 4.2), (580, 214, -0.02, 4.6)]
TIGES_LOIN = [(448, 222, 0.05), (466, 204, -0.06), (484, 228, -0.03), (526, 214, 0.06), (570, 236, -0.04)]
BCUT = 500
BAMB_BOX = (424, 364, 166, BCUT - 364)
BALANCE = 2.4


def bambou_ligne(x, h, pen, ph, k):
    """La ligne d'une tige, du pied au sommet, déplacée par le vent (plus en haut qu'en bas, rien sous BCUT)."""
    y0 = sol_d(x) + 1
    pts = []
    for i in range(13):
        u = i / 12
        y = y0 - h * u
        dx = pen * h * u * u
        if y < BCUT:
            f = ((BCUT - y) / (BCUT - (y0 - h))) ** 2
            dx += f * BALANCE * (0.6 + 0.4 * math.sin(2 * math.pi * ph + k * 1.3)) + f * BALANCE * 0.5 * \
                math.sin(2 * math.pi * ph + k * 1.3)
        pts.append((x + dx, y))
    return pts


def bambous_dessin(doc, ph):
    out = []
    # les tiges du fond (dans l'ombre du bosquet, plus pâles et plus bleues)
    loin = dict(base='#7aa48a', light='#8eb494', rim='#b4d0a4', sh='#5e8a76')
    for k, (x, h, pen) in enumerate(TIGES_LOIN):
        c = bambou_ligne(x, h, pen, ph, k + 7)
        out.append(vol(doc, ribbon(resample(c, 14), [3.2] * 14 + [1.0], sharp_ends=False), loin, r=0.6, c=0.8))
        tx, ty = c[-1]
        for j, (ang, L) in enumerate(((-150, 18), (-110, 15), (-40, 17), (-70, 14), (160, 16), (20, 17))):
            out.append(path(feuille(tx, ty + 4, ang + 8 * math.sin(2 * math.pi * ph + j), L, 4.6), loin['base'], 0.9))
        for u, angs in ((0.55, (150, 30, -160)), (0.75, (-20, 160))):
            px, py = c[int(u * 12)]
            for j, ang in enumerate(angs):
                out.append(path(feuille(px, py, ang + 6 * math.sin(2 * math.pi * ph + j + k), 15, 4.2), loin['base'],
                                0.9))
    for k, (x, h, pen, ep) in enumerate(TIGES):
        c = bambou_ligne(x, h, pen, ph, k)
        cc = resample(c, 24)
        ws = [ep * (1 - 0.35 * i / 24) for i in range(25)]
        tige = ribbon(cc, ws, sharp_ends=False)
        out.append(vol(doc, tige, BAMBOU, r=0.9, c=1.2))
        # des nœuds peu marqués, à des hauteurs irrégulières
        inner = []
        for u in (0.18 + 0.03 * (k % 3), 0.41 + 0.04 * (k % 2), 0.63 + 0.02 * (k % 4), 0.84):
            px, py = cc[int(u * 24)]
            inner.append(path(ellipse(px, py, ep * 0.62, 0.9), BAMBOU['rim'], 0.55))
            inner.append(path(ellipse(px - 0.3, py + 1.4, ep * 0.6, 0.7), BAMBOU['sh'], 0.5))
        out.append('<g clip-path="%s">%s</g>' % (doc.clip(tige.d()), ''.join(inner)))
        # les feuilles : un bouquet au sommet et un à mi-hauteur
        for u, angs, L in ((1.0, (-140, -96, -58, -18, 34, 148), 22), (0.78, (-10, 40, 140, -170), 19),
                           (0.56, (44, 136, 0), 17), (0.36, (40, 144), 15)):
            px, py = cc[int(u * 24)]
            for j, a0 in enumerate(angs):
                ang = a0 + 10 * math.sin(k * 1.7 + j) + 6 * math.sin(2 * math.pi * ph + k + j * 0.5)
                f = feuille(px, py + 2, ang, L * (0.8 + 0.2 * math.sin(j + k)), 5.4)
                out.append(vol(doc, f, FEUIL, r=0.7, c=0.9))
    return ''.join(out)


@element('bambous-bas', -19.6, 'fixe')
def bambous_bas(doc):
    x, y, w, h = BAMB_BOX
    return '<g clip-path="%s">%s</g>' % (doc.clip('M380 %dH620V700H380Z' % BCUT), bambous_dessin(doc, 0))


def bambous(doc, ph):
    x, y, w, h = BAMB_BOX
    return '<g clip-path="%s">%s</g>' % (doc.clip('M%d %dH%dV%dH%dZ' % (x, y, x + w, BCUT, x)), bambous_dessin(doc, ph))


element('bambous', -19.5, 'boucle', box=BAMB_BOX, n=8, ms=400)(bambous)


# ---------------------------------------------------------------------------------------------------- le clan
def signe_pieces(cx, cy, k):
    """Le signe d'Eldra : l'anneau d'or des singes, serti d'un jade en haut, qui enroule une volute de vent ; aucune
    lettre (la volute s'ouvre vers la droite, la queue du vent sort de l'anneau)."""
    anneau = ring(cx, cy, 3.4 * k, 2.3 * k)
    spir = []
    for i in range(15):
        a = math.radians(200 - i * 26)
        r = (0.2 + 1.5 * i / 14) * k
        spir.append((cx + r * math.cos(a) * 1.05, cy - r * math.sin(a)))
    spir += [(cx + 2.8 * k, cy + 1.6 * k), (cx + 4.8 * k, cy + 2.8 * k)]
    volute = ribbon(resample(spir, 16), [0.3 * k + 0.5 * k * math.sin(math.pi * i / 16) for i in range(17)])
    jade = ellipse(cx, cy - 3.0 * k, 1.05 * k, 1.25 * k)
    return anneau, volute, jade


def signe(doc, cx, cy, k, col='#f0c058'):
    anneau, volute, jade = signe_pieces(cx, cy, k)
    return path(anneau, col, extra=EO) + path(volute, col) + path(jade, JADE) + path(
        ellipse(cx + 0.35 * k, cy - 3.35 * k, 0.4 * k, 0.4 * k), '#c8fff0', 0.8)


STATUE_P = (466, sol_d(466))


@element('statue', -19, 'fixe')
def statue(doc):
    """La statue de pierre d'un singe assis sur son socle (bandeau d'or, yeux de jade), tournée un peu vers l'arène."""
    x, y = STATUE_P
    y += 1
    K = 1.35

    def P(u, v):
        return (x + u * K, y + v * K)
    socle = rpoly([P(-12, 1), P(-11, -8), P(11, -8), P(12, 1)], 1.4)
    socle_haut = rpoly([P(-13, -7), P(-12, -10), P(12, -10), P(13, -7)], 1.2)
    corps = sm([P(-7.5, -10), P(-8.5, -18), P(-6, -26), P(0, -28.5), P(5.5, -26), P(8, -18), P(7.5, -10)],
               sharp=(0, 6), t=0.85)
    def E(u, v, rx, ry):
        return ellipse(*P(u, v), rx * K, ry * K)
    genou_g = E(-3.8, -12.5, 4.4, 2.8)
    genou_d = E(4.2, -12.5, 4.0, 2.7)
    tete = E(-0.8, -33.5, 5.6, 5.2)
    oreille_g = E(-6.4, -34, 2.0, 2.3)
    oreille_d = E(4.9, -34.2, 1.8, 2.1)
    bras_g = membre([P(-5.5, -24), P(-7.2, -18), P(-4, -14)], 2.8, 2.2, 6)
    bras_d = membre([P(5.2, -24), P(7, -18), P(3.8, -14)], 2.6, 2.1, 6)
    queue = membre([P(-6.5, -11), P(-11.5, -11), P(-14, -15), P(-13, -20), P(-10.2, -21.5), P(-9.6, -18.8)], 2.4, 1.2, 12)
    pieces = [socle, socle_haut, queue, corps, genou_g, genou_d, bras_g, bras_d, oreille_g, oreille_d, tete]
    out = [encre(pieces, 1.0)]
    out.append(vol(doc, socle, dict(STATUE, base='#7a7280', light='#948a92', sh='#544c5c'), r=1.0, c=1.6))
    out.append(vol(doc, socle_haut, STATUE, r=0.9, c=1.0))
    for s in (queue, corps, genou_g, genou_d, bras_g, bras_d, oreille_g, oreille_d, tete):
        out.append(vol(doc, s, STATUE, r=1.0, c=1.4))
    # le visage (un masque plus clair, en cœur), le museau, les yeux de jade, le bandeau d'or
    masque = sm([P(-4.6, -34.5), P(-2.6, -36.4), P(-0.9, -35.2), P(0.8, -36.4), P(2.8, -34.4), P(2.4, -30.6),
                 P(-0.9, -29.2), P(-4.2, -30.6)], t=0.9)
    out.append(path(masque, '#bcb2aa'))
    out.append(path(E(-0.9, -31, 2.6, 1.6), '#a89e98'))
    for ex in (-2.8, 1.0):
        out.append(path(E(ex, -33.6, 0.85, 0.75), JADE))
        out.append(path(E(ex + 0.25, -33.9, 0.3, 0.3), '#d8fff2'))
    bandeau = membre([P(-6.0, -37.4), P(-0.8, -38.8), P(4.6, -37.6)], 1.7, 1.5, 8)
    out.append(vol(doc, bandeau, OR, r=0.5, c=0.6))
    out.append(path(E(-0.8, -38.8, 0.9, 0.9), JADE))
    # le signe du clan gravé sur le socle, un peu de mousse sur le socle
    out.append(signe(doc, *P(0.5, -3.6), 0.9 * K, col='#d0a050'))
    out.append(vol(doc, sm([P(-12, -9.5), P(-8, -11), P(-3, -10), P(-5, -8.6), P(-11, -8.4)], t=0.9), MOUSSE,
                   r=0.5, c=0.5))
    return ''.join(out)


MATS = [(174, sol_g(174)), (432, sol_d(432)), (552, sol_d(552))]
MAT_H = 50


def mat(doc, x, y):
    out = [vol(doc, rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6),
               BOIS, r=0.7, c=0.8, ink=INK, iw=0.7)]
    out.append(vol(doc, rpoly([(x - 12, y - MAT_H + 2), (x + 12, y - MAT_H + 2), (x + 13, y - MAT_H + 5),
                               (x - 13, y - MAT_H + 5)], 1.2), ROUGE, r=0.7, c=0.8, ink=INK, iw=0.7))
    out.append('<circle cx="%s" cy="%s" r="2.6" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        fm(x), fm(y - MAT_H - 1), doc.rad(x + 1, y - MAT_H - 2, 3, [(0, '#fff0b0'), (1, '#d09a3a')]), INK))
    out.append(vol(doc, rpoly([(x - 6, y + 3), (x - 5, y - 2), (x + 5, y - 2.5), (x + 7, y + 3)], 1.2), ROC,
                   r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


def banniere(k):
    x, y = MATS[k]
    top = y - MAT_H + 5

    def fn(doc, ph):
        # la toile pend sous la traverse ; le vent vient de la gauche : elle part un peu vers la droite et ondule
        L, w_ = 32, 20
        a = 2 * math.pi * ph

        def P(u, v):          # u : -1..1 en travers, v : 0..1 en descendant
            sway = v ** 1.5 * (2.2 * math.sin(a + v * 2.2 + k) + 1.6)
            return (x + u * w_ / 2 * (1 - 0.08 * v) + sway, top + v * L + 0.8 * math.sin(a + u * 1.5 + k) * v)
        pts = [P(-1, 0), P(1, 0)]
        for v in (0.33, 0.66, 0.92):
            pts.append(P(1, v))
        pts += [P(1, 1.04), P(0, 0.86), P(-1, 1.04)]
        for v in (0.92, 0.66, 0.33):
            pts.append(P(-1, v))
        s = sm(pts, sharp=(0, 1, 5, 6, 7), t=0.6)
        out = [mat(doc, x, y), vol(doc, s, ROUGE, r=1.3, c=2.0, ink=INK, iw=0.9)]
        # un galon d'or en bas, le signe au milieu
        sx, sy = P(0, 0.42)
        out.append(signe(doc, sx, sy, 1.55))
        return ''.join(out)
    return fn


for _k in range(3):
    _x, _y = MATS[_k]
    element('banniere%d' % (_k + 1), -16, 'boucle', box=(_x - 16, _y - MAT_H - 5, 40, MAT_H + 10), n=12,
            ms=200)(banniere(_k))


# ---------------------------------------------------------------------------------------------------- la rivière
RIV = (0, 748, 590, 42)          # la boîte du défilé (x, y, w, h)
RIV_T = (192, 42)                # la tuile (elle coule de 20 px/s vers la droite : 9,6 s par tour)


def riviere_tuile(doc):
    """La tuile de la rivière turquoise (192 × 42), qui se répète exactement en x : plus pâle au loin (la brume),
    des reflets allongés, un peu d'écume et deux pétales qui flottent."""
    tw, th = RIV_T
    out = [path('M0 0H%dV%dH0Z' % (tw, th), doc.lin(0, 0, 0, th, [
        (0, '#b0d4d0'), (0.22, EAU['light']), (0.6, EAU['mid']), (1, EAU['deep'])]))]
    out.append(path('M0 0H%dV2.4H0Z' % tw, '#6e8c90', 0.35))        # l'ombre de la rive d'en face
    for x, y, w_, h_, col, op in ((30, 9, 26, 1.4, '#ffffff', 0.5), (118, 7, 34, 1.3, '#ffffff', 0.45),
                                  (72, 16, 40, 1.8, '#ffffff', 0.4), (160, 18, 28, 1.6, '#ffffff', 0.45),
                                  (20, 26, 44, 2.2, '#e8fbf6', 0.4), (110, 30, 50, 2.4, '#e8fbf6', 0.35),
                                  (176, 34, 30, 2.0, '#e8fbf6', 0.35), (60, 36, 26, 1.8, EAU['deep'], 0.35),
                                  (140, 24, 22, 1.6, EAU['deep'], 0.3)):
        for dx in (-tw, 0, tw):
            out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(x + dx), fm(y), fm(w_ / 2), fm(h_), doc.rad(x + dx, y, w_ / 2, [(0, col, op), (0.6, col, op * 0.5),
                                                                                   (1, col, 0)], ry=h_)))
    for x, y, a in ((52, 21, 20), (150, 31, -30)):
        for dx in (-tw, 0, tw):
            p = sm([(0, -2.2), (1.4, -0.4), (0.8, 1.9), (0, 2.4), (-0.8, 1.9), (-1.4, -0.4)], t=0.9)
            ra = math.radians(a)
            p = p.map(lambda q: (x + dx + q[0] * math.cos(ra) - q[1] * 0.6 * math.sin(ra),
                                 y + q[0] * math.sin(ra) * 0.6 + q[1] * 0.6 * math.cos(ra)))
            out.append(path(p, ROSE['light'], 0.9))
    return out


element('riviere', -18, 'defile', box=RIV, tuile=RIV_T, vx=20.0, vy=0.0, tuile_dessin=riviere_tuile)


@element('rives', -17.5, 'morceau', box=(0, 772, 590, P0 - 772))
def rives(doc):
    """La berge d'herbe fleurie entre la rivière et l'arène."""
    out = []
    pts = [(-10, P0 + 2), (-10, 784)]
    x, i = -10, 0
    while x < 600:
        x += 14 + 6 * math.sin(i * 1.9)
        pts.append((x, 781 - 2.2 * abs(math.sin(i * 1.3)) - 1.2 * math.sin(i * 0.7)))
        i += 1
    pts += [(600, 784), (600, P0 + 2)]
    s = sm(pts, sharp=(0, 1, len(pts) - 2, len(pts) - 1), t=0.7)
    out.append(vol(doc, s, MOUSSE, grad=doc.lin(0, 778, 0, P0, [(0, MOUSSE['light']), (0.5, MOUSSE['base']),
                                                               (1, MOUSSE['sh'])]), r=1.2, c=0))
    # le reflet de la berge dans l'eau (une ombre douce juste au-dessus)
    out.append(path('M-10 778H600V782H-10Z', doc.lin(0, 776, 0, 782, [(0, '#2e6a7a', 0), (1, '#2e6a7a', 0.25)])))
    # des touffes de fleurs, peu, à des places irrégulières
    for x, col in ((36, ROSE['light']), (150, '#fff4dc'), (248, ROSE['light']), (346, '#fff4dc'), (430, ROSE['light']),
                   (528, '#fff4dc'), (572, ROSE['light'])):
        yb = 790
        out.append(vol(doc, sm([(x - 5, yb), (x - 3, yb - 4), (x + 2, yb - 5), (x + 5, yb)], sharp=(0, 3), t=0.8),
                       MOUSSE, r=0.6, c=0.6))
        for dx, dy in ((-2, -5), (1.6, -6), (3.4, -3.6)):
            out.append(path(ellipse(x + dx, yb + dy, 1.4, 1.2), col))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0 - 1.5, P0 + 0.5), '#3e5a40', 0.5))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- l'arène
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
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, 0, 590, 0, [(0, '#3a2a2a', 0.06),
                                                                              (1, '#fff4dc', 0.05)])))
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
    out.append('<path d="%s" fill="none" stroke="#fff6e4" stroke-width="1.2" opacity="0.06" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#3a2826" stroke-width="1" opacity="0.11"/>' % jd)
    # quelques dalles un peu plus claires ou plus sombres (très peu)
    for (g0, i, col, op) in ((-220, 1, '#fff4e0', 0.035), (60, 3, '#3a2826', 0.04), (300, 2, '#fff4e0', 0.03),
                             (-90, 4, '#3a2826', 0.035), (180, 5, '#fff4e0', 0.03)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 140, ya), ya), (sol_x(g0 + 140, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le bord arrière : l'arête éclairée
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 1.6), '#c4ac94', 0.6))
    # le reflet frais de la rivière sur le fond du dallage (doux)
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 24), doc.lin(0, P0, 0, P0 + 24, [(0, '#9ad0cc', 0.08),
                                                                                       (1, '#9ad0cc', 0)])))
    # l'arête avant éclairée, puis le flanc moussu
    out.append(path('M-10 %dH600V%dH-10Z' % (P1, 1066), doc.lin(0, P1, 0, 1066, [
        (0, '#6a5450'), (0.6, '#5a4646'), (1, '#4a3a40')])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P1 - 1, P1 + 1.6), '#c8b098', 0.8))
    pts = [(-10, P1 + 1), (600, P1 + 1)]
    x, i = 600, 0
    while x > -10:
        x -= 18 + 8 * math.sin(i * 1.7)
        pts.append((x, P1 + 5 + 3.5 * abs(math.sin(i * 2.3)) + 1.5 * math.cos(i * 1.1)))
        i += 1
    pts.append((-10, P1 + 5))
    out.append(vol(doc, sm(pts, sharp=(0, 1), t=0.7), MOUSSE, r=0, c=1.4))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- sous l'arène
@element('dessous', -15.4, 'fixe')
def dessous(doc):
    """Sous le flanc de l'arène : en combat, c'est sous les cartes des héros (y > 985) ; donc simple et sombre, le
    ruisseau dans l'ombre (l'accueil, qui le montre, garde un bas calme)."""
    out = [path('M-10 1064H600V1104H-10Z', doc.lin(0, 1064, 0, 1100, [(0, '#2e5a64'), (0.35, '#244852'),
                                                                     (1, '#1c3440')]))]
    out.append(path('M-10 1064H600V1067H-10Z', '#122a34', 0.5))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- premier plan
@element('pierre-gauche', 1300, 'morceau', box=(0, 1026, 84, 74))
def pierre_g(doc):
    s = sm([(-12, 1104), (-12, 1048), (8, 1040), (30, 1042), (50, 1054), (66, 1072), (78, 1092), (80, 1104)],
           sharp=(0, 7), t=0.8)
    fougeres = [feuille(18, 1044, -110, 24, 7), feuille(26, 1044, -70, 22, 6.5), feuille(12, 1046, -150, 20, 6)]
    out = [encre(fougeres + [s], 1.1)]
    for f in fougeres:
        out.append(vol(doc, f, FEUIL, r=0.9, c=1.2))
    out.append(vol(doc, s, ROC, r=2.0, c=3.0))
    out.append(path(sm([(30, 1046), (50, 1056), (64, 1074), (52, 1082), (36, 1064)], t=0.9), ROC['light'], 0.5))
    out.append(vol(doc, sm([(-12, 1052), (8, 1042), (30, 1044), (44, 1050), (24, 1054), (4, 1056)], t=0.9), MOUSSE,
                   r=0.9, c=1.0))
    return ''.join(out)


@element('pierre-droite', 1300, 'morceau', box=(520, 1026, 70, 74))
def pierre_d(doc):
    s = sm([(524, 1104), (530, 1080), (544, 1060), (562, 1046), (584, 1040), (604, 1044), (604, 1104)],
           sharp=(0, 6), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(566, 1050), (590, 1044), (600, 1060), (584, 1068)], t=0.9), ROC['light'], 0.45))
    out.append(buisson(doc, 572, 1047, 8))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les grues
# La touche vivante du ciel (comme les dragons de Kael) : des grues qui passent lentement, dans la couleur de la brume
# du ciel en plus foncé ; plus loin = plus petit et plus pâle. Elles volent au-dessus des arbres du sommet et du
# pêcher, derrière les bambous (un calque plus proche), jamais sur l'arène. Chacune est une particule seule qui vit une
# période entière : elle naît hors de l'image et finit hors de l'image ; ses ailes battent lentement.
GRUES = [
    # id, y, échelle, x de départ, x d'arrivée, montée (px/s), couleur, opacité, profondeur, vol (1 ou 3 grues)
    ('grue1', 420, 0.62, -60, 650, -0.3, '#4e5274', 0.85, -23.8, 1),     # la plus proche, de gauche à droite
    ('grue2', 396, 0.38, 640, -50, 0.0, '#6a6e8e', 0.72, -23.79, 1),     # plus loin, de droite à gauche
    ('grues3', 368, 0.22, -50, 640, -0.2, '#7e809c', 0.62, -23.78, 3),   # tout au loin, un vol de trois
]
GRUE_N, GRUE_MS = 12, 100                        # un battement d'ailes = 1,2 s
GRUE_BOITE = (-40, -40, 80, 70)                  # la silhouette (repère local, tête à droite) : x, y, w, h


def grue(ph, col, col_loin):
    """Une grue en vol (repère local, tête à droite) : long cou tendu, pattes qui traînent, grandes ailes aux
    rémiges écartées. ph : le battement (0 = en haut, 0,5 = en bas)."""
    a = 2 * math.pi * ph
    f = 0.25 + 0.75 * math.cos(a)                   # 1 : ailes en haut, −0,5 : en bas
    b = -1.2 * math.sin(a)                         # le corps monte un peu quand les ailes descendent
    out = []

    def aile(near):
        k = 1.0 if near else 0.76
        S = (2, -1 + b) if near else (8, -2 + b)

        def P(dx, dy):
            return (S[0] + dx * k * (0.85 + 0.15 * abs(f)), S[1] + dy * f * k)
        bord = [(0, 0), (-3, -13), (-10, -24), (-15, -33)]                 # le bord d'attaque jusqu'au bout
        doigts = [(-19, -29), (-23, -27), (-21, -23), (-25, -19)]
        fuite = [(-21, -11), (-15, -4), (-8, 1)]
        pts = [P(x, y) for x, y in bord + doigts + fuite]
        return sm(pts, sharp=(3, 5, 7), t=0.8)
    out.append(path(aile(False), col_loin))
    corps = membre([(-22, 1 + b), (-12, 0 + b), (0, -1 + b), (7, -2 + b)], 4.6, 4.0, 10)
    cou = membre([(6, -2 + b), (13, -4 + b), (20, -6 + b)], 2.4, 1.6, 6)
    tete = ellipse(21.5, -6.4 + b, 2.4, 2.0)
    bec = sm([(22, -7.4 + b), (30, -6.0 + b), (22, -5.2 + b)], sharp=(0, 1, 2), t=0.5)
    queue = sm([(-20, -1 + b), (-28, 0 + b), (-21, 3.4 + b)], sharp=(1,), t=0.7)
    pattes = membre([(-20, 2 + b), (-30, 3 + b), (-38, 3.6 + b)], 1.4, 0.8, 6)
    for s in (pattes, queue, corps, cou, tete, bec):
        out.append(path(s, col))
    out.append(path(aile(True), col))
    return ''.join(out)


def grue_image(id_):
    _, y, k, x0, x1, vy, col, op, _, nb = next(g for g in GRUES if g[0] == id_)
    sg = 1 if x1 > x0 else -1
    bx, by, bw, bh = GRUE_BOITE
    vol_ = [(0, 0, 0.0)] if nb == 1 else [(0, 0, 0.0), (-46, 12, 0.33), (-40, -16, 0.62)]
    xs = [d[0] for d in vol_]
    ys = [d[1] for d in vol_]
    gw = bw + max(xs) - min(xs)
    gh = bh + max(ys) - min(ys)
    w, h = gw * k + 4, gh * k + 4

    def fn(doc, i, n):
        ph = i / n
        col_loin = mix(col, '#b4b8cc', 0.35)              # l'aile lointaine, plus dans la brume
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        out = ['<g transform="translate(%s %s) scale(%s %s)">' % (fm(w / 2), fm(h / 2), fm(k * sg), fm(k))]
        for dx, dy, dph in vol_:
            out.append('<g transform="translate(%s %s)">%s</g>' % (
                fm(dx - cx - (bx + bw / 2)), fm(dy - cy - (by + bh / 2)), grue((ph + dph) % 1, col, col_loin)))
        out.append('</g>')
        return '<g opacity="%g">%s</g>' % (op, ''.join(out))
    return fn, (round(w), round(h))


for _g in GRUES:
    _fn, _t = grue_image(_g[0])
    _vx = (_g[4] - _g[3]) * 1000 / PERIODE
    element(_g[0], _g[8], 'particules', taille=_t, images=GRUE_N, ms=GRUE_MS, dessin=_fn,
            zone=(_g[3], _g[1], _g[3], _g[1]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_g[5], _g[5]),
            ondule=(0, PERIODE))


# ---------------------------------------------------------------------------------------------------- le singe
# L'ombre d'un singe qui saute d'arbre en arbre sur le sommet de la montagne (une boucle de 9,6 s) : assis sur l'arbre
# de gauche, il saute sur l'arbre rose, puis sur celui de droite, se retourne et revient. Une silhouette de la couleur
# de la brume (comme les grues), un peu plus foncée : on la lit sur le ciel clair.
SINGE_N, SINGE_MS = 96, 100
SINGE_BOX = (230, 394, 136, 50)
SINGE_COL = '#4e4a68'


def singe_dessin(x, y, s, face, ang=0.0):
    """La silhouette du singe, ses pieds en (x, y) ; s : 0 accroupi (assis), 1 tendu (en plein saut), < 0 : ramassé
    (il prend son élan ou se reçoit) ; face : 1 regarde à droite, −1 à gauche ; ang : l'inclinaison (degrés).
    Un seul bloc : le tronc (un ovale), la tête qui le chevauche, des membres aux bouts ronds, la longue queue."""
    q = max(0.0, s)
    z = max(0.0, -s)
    K = 1.3

    def L(a, b):
        return (a[0] + (b[0] - a[0]) * q, (a[1] + (b[1] - a[1]) * q) * (1 - 0.16 * z))
    # repère local : pieds en (0, 0), tête à droite
    hanche = L((-0.6, -3.6), (-4, -6.2))
    poitrine = L((0.8, -8.6), (2.6, -8.2))
    tete = L((1.9, -12.2), (6.2, -9.8))
    coude = L((3.2, -6.4), (6.6, -11.2))
    main = L((3.4, -2.6), (10.4, -12.6))
    genou = L((3.4, -4.0), (-8.0, -5.6))
    pied = L((2.2, -0.4), (-11.6, -3.6))
    queue = [L((-2.6, -2.6), (-6.8, -6.6)), L((-6.4, -2.6), (-11.6, -8.6)), L((-9.0, -5.8), (-15.2, -10.6)),
             L((-8.8, -9.6), (-17.4, -14.0)), L((-6.6, -11.0), (-16.2, -16.8))]
    a = math.radians(ang)

    def T(p):
        px, py = p
        rx, ry = px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)
        return (x + rx * face * K, y + ry * K)

    def rond(p, r):
        return ellipse(*T(p), r * K, r * K)

    def trait(pts, w0, w1):
        out = [membre([T(p) for p in pts], w0 * K, w1 * K, 8)]
        return out + [rond(pts[0], w0 * 0.5), rond(pts[-1], w1 * 0.5)] + [rond(p, (w0 + w1) * 0.25) for p in pts[1:-1]]
    mx, my = (hanche[0] + poitrine[0]) / 2, (hanche[1] + poitrine[1]) / 2
    dl = math.hypot(poitrine[0] - hanche[0], poitrine[1] - hanche[1])
    rot = math.degrees(math.atan2(poitrine[1] - hanche[1], poitrine[0] - hanche[0]))
    cx, cy = T((mx, my))
    tronc = ellipse(cx, cy, (dl / 2 + 2.4) * K, 2.8 * K, rot=(rot + ang) * face if face > 0 else 180 - (rot + ang))
    parts = [tronc, rond(tete, 2.9), rond((tete[0] + 2.0, tete[1] + 0.8), 1.5), rond((tete[0] - 1.5, tete[1] - 1.6), 1.1)]
    parts += trait([poitrine, coude, main], 1.8, 1.3)
    parts += trait([hanche, genou, pied], 2.5, 1.5)
    parts += [membre([T(p) for p in [hanche] + queue], 1.5 * K, 0.6 * K, 12)]
    return ''.join(path(p, SINGE_COL) for p in parts)


# les trois arbres : là où le singe se pose (le haut de la couronne)
def cime(k):
    x, y, r, _ = ARBRES[k]
    return (x + r * 0.05, y - r * 0.95 - r * 0.6 * 0.98 - 0.6)


def singe_plan():
    """Les 96 images de la boucle : (x, y, s, face, angle)."""
    plan = []

    def assis(k, face, n):
        x, y = cime(k)
        plan.extend([(x, y, 0.0, face, 0.0)] * n)

    def saut(a, b, face):
        (xa, ya), (xb, yb) = cime(a), cime(b)
        plan.append((xa, ya, -1.0, face, 0.0))                       # l'élan
        for i in range(1, 7):
            u = i / 7
            x = xa + (xb - xa) * u
            y = ya + (yb - ya) * u - 15 * 4 * u * (1 - u)
            pente = (yb - ya) - 15 * 4 * (1 - 2 * u)
            plan.append((x, y, math.sin(math.pi * u) ** 0.6, face, math.degrees(math.atan2(pente, abs(xb - xa))) * 0.35))
        plan.append((xb, yb, -1.0, face, 0.0))                       # il se reçoit
    assis(0, 1, 14)
    saut(0, 1, 1)
    assis(1, 1, 14)
    saut(1, 2, 1)
    assis(2, 1, 8)
    assis(2, -1, 10)
    saut(2, 1, -1)
    assis(1, -1, 8)
    saut(1, 0, -1)
    assis(0, -1, SINGE_N - len(plan) - 0)
    assert len(plan) == SINGE_N, len(plan)
    return plan


_SINGE = singe_plan()


def singe(doc, ph):
    x, y, s, face, ang = _SINGE[int(round(ph * SINGE_N)) % SINGE_N]
    return '<g opacity="0.9">%s</g>' % singe_dessin(x, y, s, face, ang)


element('singe', -23.5, 'boucle', box=SINGE_BOX, n=SINGE_N, ms=SINGE_MS)(singe)


def devant(ids, box):
    """Un morceau du paysage remis devant les calques : ces éléments seuls (sans le ciel), coupés à la boîte."""
    def fn(doc):
        x, y, w, h = box
        body = ''.join(e['fn'](doc) for e in sorted(ELEMS, key=lambda e: e['prof']) if e['id'] in ids)
        return '<g clip-path="%s">%s</g>' % (doc.clip('M%s %sH%sV%sH%sZ' % (x, y, x + w, y + h, x)), body)
    return fn


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
        r = rng(CLAN + '-' + e['id'])
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


def phase(e, t):
    if e['genre'] == 'boucle':
        return (int(t // e['ms']) % e['n']) / e['n']
    return 0


def defile_dessin(doc, e, t):
    """Un défilé à l'instant t : la tuile répétée (chaque copie coupée à sa case, comme le jeu), décalée de vx, vy."""
    x, y, w, h = e['box']
    tw, th = e['tuile']
    offx = (t / 1000 * e['vx']) % tw
    offy = (t / 1000 * e['vy']) % th
    sid = doc.uid('t')
    doc.defs.append('<g id="%s"><g clip-path="%s">%s</g></g>' % (
        sid, doc.clip('M0 0H%dV%dH0Z' % (tw, th)), ''.join(e['tuile_dessin'](doc))))
    out = []
    for k in range(-1, w // tw + 2):
        for l in range(-1, h // th + 2):
            out.append('<use href="#%s" x="%s" y="%s"/>' % (sid, fm(x + k * tw + offx), fm(y + l * th + offy)))
    return '<g clip-path="%s">%s</g>' % (doc.clip('M%d %dH%dV%dH%dZ' % (x, y, x + w, y + h, x)), ''.join(out))


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
            body.append(defile_dessin(doc, e, t))
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
# Côté héros : Zéphyre (angels-2) au fond, Venthys (dragon-vent) au milieu, Eldra (mages-8) devant ; en face, les
# trois singes du clan d'Eldra (le voleur, le gorille, le vieux chaman), retournés vers la gauche.
PERSOS = [('angels-2', 'heros', 0), ('dragon-vent', 'heros', 2), ('mages-8', 'heros', 4),
          ('mon-eldra-rapide', 'ennemis', 0), ('mon-eldra-costaud', 'ennemis', 2), ('mon-eldra-sorts', 'ennemis', 4)]


def vecto_table():
    import re
    s = open(os.path.join(ROOT, 'src', 'game', 'vecto.ts')).read()
    out = {}
    for m in re.finditer(r"'([\w-]+)': \[([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\]", s):
        out[m.group(1)] = tuple(float(m.group(i)) for i in range(2, 6))
    return out


def poser(im, s, x0, y0, persos=PERSOS):
    """Pose les personnages vectoriels (public/art/vecto/<id>.webp) comme le combat : places de place_combat(),
    taille K_PERSO, l'ombre du jeu (ovale noir à 30 %). L'image `im` est le fond rendu à l'échelle s (pixels d'image
    par pixel du fond), son coin haut-gauche en (x0, y0) du fond."""
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
    """Rend les images de chaque calque (×UP), les range dans une planche et écrit la description JSON. Les images
    identiques (le singe assis, par exemple) ne sont rangées qu'une fois dans la planche."""
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
            svg = doc.svg(''.join(e['tuile_dessin'](doc)), (0, 0, tw, th))
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
        # les SVG identiques ne sont rendus qu'une fois
        uniq = {}
        for s_, p_, key in lst:
            uniq.setdefault(s_, p_)
        rendre([(s_, p_) for s_, p_ in uniq.items()], w_, h_)
        for s_, p_, key in lst:
            images[key] = Image.open(uniq[s_]).convert('RGBA')
    # les images identiques : une seule place dans la planche
    signature = {}
    alias = {}
    for k in sorted(images):
        im = images[k]
        h_ = hashlib.md5(im.tobytes() + bytes(str(im.size), 'ascii')).hexdigest()
        if h_ in signature:
            alias[k] = signature[h_]
        else:
            signature[h_] = k
    # la planche : des étagères, les plus hautes d'abord, 2048 px de large au plus. Chaque image est « étirée » de 2 px
    # tout autour (ses bords recopiés) : le jeu agrandit en lissant, et sans cela un liseré sombre apparaît au bord
    # des morceaux remis devant (vu dans le vrai combat).
    keys = sorted([k for k in images if k not in alias], key=lambda k: (-images[k].height, k))
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
    for k, v in alias.items():
        pos[k] = pos[v]
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
                     graine=CLAN + '-' + e['id'])
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
    Image.open(fixe).convert('RGB').save(os.path.join(JEU, CLAN + '.webp'), quality=95, method=6)
    # le fond entier pour le propriétaire (les grues en vol)
    rendre([(scene(T_VUE), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    assert max(planche.size) <= 2048, planche.size
    planche.save(os.path.join(JEU, CLAN + '-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': CLAN, 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/%s.webp' % CLAN, 'planche': 'art/vecto/fonds/%s-anim.webp' % CLAN,
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("%s-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'
                 % CLAN),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-%s.json' % CLAN), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print('  jeu : public/art/vecto/fonds/%s.webp %d Ko, %s-anim.webp %d Ko (%d × %d), %d calques' % (
        CLAN, os.path.getsize(os.path.join(JEU, CLAN + '.webp')) // 1024, CLAN,
        os.path.getsize(os.path.join(JEU, CLAN + '-anim.webp')) // 1024, planche.size[0], planche.size[1], len(meta)))
    return doc


def ecrire_ts(doc):
    """meta.json (les calques au format de FOND_META), puis ../assemble_ts.py écrit src/game/fond-vecto.ts avec tous
    les clans (lu par bg/fond-px.ts derrière ?vecto=1)."""
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
    dst = os.path.join(HERE, 'meta.json')
    json.dump(meta, open(dst + '.tmp', 'w'), separators=(',', ':'))
    os.replace(dst + '.tmp', dst)
    sys.path.insert(0, os.path.join(HERE, '..'))
    from assemble_ts import assemble
    print('  fond-vecto.ts :', ', '.join(assemble()))


def composer_jeu(doc, t):
    """Contrôle : l'image à l'instant t refaite comme le jeu la ferait (fixe + calques de la planche), à ×UP."""
    base = Image.open(os.path.join(JEU, CLAN + '.webp')).convert('RGBA')
    pl = Image.open(os.path.join(TMP, 'planche.png')).convert('RGBA')
    for c in sorted(doc['calques'], key=lambda c: c['prof']):
        if c['genre'] == 'boucle':
            i = 0 if c['ms'] == 0 else int(t // c['ms']) % len(c['cases'])
            sx, sy = c['cases'][i]
            base.alpha_composite(pl.crop((sx, sy, sx + c['w'] * UP, sy + c['h'] * UP)), (c['x'] * UP, c['y'] * UP))
        elif c['genre'] == 'defile':
            sx, sy, tw, th = c['case']
            tile = pl.crop((sx, sy, sx + tw, sy + th))
            offx = round((t / 1000 * c['vx']) % (tw / UP) * UP) if c['vx'] else 0
            offy = round((t / 1000 * c['vy']) % (th / UP) * UP) if c['vy'] else 0
            bw, bh = c['w'] * UP, c['h'] * UP
            big = Image.new('RGBA', (bw + 2 * tw, bh + 2 * th))
            for i in range(bw // tw + 3):
                for j in range(bh // th + 3):
                    big.alpha_composite(tile, (i * tw, j * th))
            base.alpha_composite(big.crop((tw - offx, th - offy, tw - offx + bw, th - offy + bh)),
                                 (c['x'] * UP, c['y'] * UP))
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


T_VUE = 6200            # l'instant montré dans les images fixes (les grues en vol, le singe en plein saut)


def main():
    args = sys.argv[1:]
    os.makedirs(TMP, exist_ok=True)
    if '--fixe' in args:
        # le brouillon : la vue du combat sur un téléphone 390 × 844 (avec les personnages) et sur un court
        t = float(args[args.index('--fixe') + 1]) if len(args) > args.index('--fixe') + 1 else T_VUE
        vue_combat(t, 780).convert('RGB').save(os.path.join(TMP, 'brouillon-390.png'))
        vue_combat(t, 720, phone=(360, 640, 0)).convert('RGB').save(os.path.join(TMP, 'brouillon-360.png'))
        p = os.path.join(TMP, 'brouillon-entier.png')
        rendre([(scene(t), p)], W, H)
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
    vue_combat(T_VUE, 780).convert('RGB').save(os.path.join(SORTIE, 'situation.png'))
    # la comparaison : ancien fond pixel | nouveau fond vectoriel, mêmes personnages, même cadrage
    pix = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', CLAN + '.webp')).convert('RGBA')
    a = vue_combat(0, 780, fond=pix)
    b = vue_combat(T_VUE, 780)
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
