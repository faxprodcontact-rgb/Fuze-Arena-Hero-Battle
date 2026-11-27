# Le fond de combat du clan d'ORIN (vent), le sommet sacré des tengu, redessiné en VECTORIEL lisse et animé (27/11/2026,
# demande du propriétaire : les 7 autres fonds après le test validé du volcan de Kael, même façon de faire :
# refonte-graphique/ui-moderne/fonds/kael/kael.py).
#
# Même univers que le fond pixel (refonte-graphique/pixel/fonds/orin/build.py) et mêmes mesures que Kael : une image
# de 590 × 1100 pixels du fond ; en combat le jeu l'agrandit ×1,4 et n'en montre que x = 84 → 506 ; la plateforme
# commence à P0 = 800 (pieds des rangs à 828 / 880 / 933), le haut des cartes des héros est à 985 (dessous : une bande
# sombre et simple). Style des héros vectoriels : grandes formes simples, dégradés doux, une seule lumière en haut à
# droite, un seul contour sombre seulement sur les plans proches, aucun flou SVG ; le lointain plus pâle dans la brume.
#
# Ce qu'on voit, du fond vers le devant : un ciel d'aube très haut au-dessus du monde (indigo → lavande → rose →
# pêche), le soleil levant pâle en haut à droite, des bancs de nuages aux bords dorés ; des pics lointains bleu lavande
# qui percent une immense MER DE NUAGES ; au milieu, un piton qui porte le TEMPLE DES TENGU (pagode à trois toits
# recourbés noir corbeau à reflets bleus, piliers vermillon, murs ivoire, flèche d'or ; deux lanternes rouges aux coins
# du grand toit) ; à gauche un piton avec un GRAND PIN TORDU couché par le vent et un pont de cordes vers le temple ; à
# droite un éperon : la pierre levée du clan (le signe rempli d'or, ceinte d'une corde rouge à glands) et deux
# bannières noir corbeau au signe d'or ; derrière la terrasse, une corniche moussue et deux lanternes de pierre ; la
# terrasse de grandes dalles de granit, d'un bord à l'autre, calme ; son mur ; deux rochers dans les coins du bas.
# Ce qui bouge : trois grands corbeaux lointains qui traversent le ciel (derrière le temple), des pétales emportés par
# le vent (de la gauche vers la droite), la mer de nuages qui dérive, des écharpes de brume au pied des pitons, le pin
# qui se balance, les lanternes du temple, les bannières, les glands de la corde et l'or du signe, les flammes des
# lanternes de pierre.
# Le signe du clan (inventé, comme le pixel) : une plume dressée dont la pointe s'enroule (le vent), et deux ailes
# ouvertes vers le bas de part et d'autre de sa tige.
#
#   python3 refonte-graphique/ui-moderne/fonds/orin/orin.py --fixe     # la vue du combat dans le brouillon (composer)
#   python3 refonte-graphique/ui-moderne/fonds/orin/orin.py            # images du jeu + calques + test + contrôles
#   python3 refonte-graphique/ui-moderne/fonds/orin/orin.py --video    # en plus : anim.gif et anim.mp4
#
# Sorties : public/art/vecto/fonds/orin.webp (fixe ×2), orin-anim.webp (planche ×2), fond-orin.json et meta.json (à
# côté de ce fichier) puis src/game/fond-vecto.ts par assemble_ts.py ; pixel/sortie/ui/vecto/fond-orin/ (fond.png,
# situation.png, comparaison.png, anim.gif, anim.mp4, STATUT.txt).
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

CLAN = 'orin'
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
VISIBLE = {'court': 377, 'moyen': 148, 'long': 50}
PERIODE = 19200                 # toutes les boucles divisent cette période : l'aperçu boucle sans couture
UNIT = 720 / W
HERO_X_U = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}
ENEMY_X_U = {0: 475, 1: 475, 2: 557, 3: 638, 4: 638}
ROW_OF = {0: 0, 3: 0, 2: 1, 1: 2, 4: 2}


def place(side, slot):
    xs = HERO_X_U if side == 'heros' else ENEMY_X_U
    return int(round(xs[slot] / UNIT)), RANGS[ROW_OF[slot]]


# Le VRAI combat (src/game/battle-scene.ts, fight-view.ts) : le décor y est agrandi ×1,4 (FOND_ZOOM), centré, son bas
# au bas de l'écran (au-dessus de la barre de geste) ; on n'en voit que x = 84 → 506.
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
# Reprises d'Orin et de ses monstres vectoriels (ailes noir corbeau à reflets bleus, veste ivoire, ceinture vermillon,
# or), et du ciel d'aube du pixel ; plus sourdes que les personnages.
INK = '#1f1a3a'                 # le contour, seulement sur les plans proches
CIEL = [(0, '#1c1c46'), (0.22, '#2a2a5e'), (0.42, '#453c78'), (0.6, '#6a548e'), (0.72, '#946a9a'),
        (0.84, '#bc889c'), (1, '#d8a49c')]
NUAGE = dict(base='#5e5288', light='#74649a', rim='#e6b892', sh='#463e70')         # bancs du ciel, bords dorés
NUAGE2 = dict(base='#4a4278', light='#5a4e88', rim='#c89a92', sh='#3a3466')        # les plus hauts (plus sombres)
LOIN1 = dict(base='#9a8eb6', light='#aa9cbe', rim='#d0b8c8', sh='#8a80aa')        # les pics les plus lointains
LOIN2 = dict(base='#7e74a2', light='#8e82ac', rim='#bca6c0', sh='#6c6494')
PITON = dict(base='#5c5672', light='#6e6884', rim='#a89cb8', sh='#433e5a')        # le piton du temple
FAL = dict(base='#4c4762', light='#5e5874', rim='#9a90ae', sh='#34304a')          # piton du pin, éperon (plan moyen)
ROC = dict(base='#403b54', light='#55506a', rim='#8e86a4', sh='#2b273c')          # les rochers du premier plan
MOUSSE = dict(base='#4f6658', light='#627a66', rim='#9ab48e', sh='#3b4e46')
PIN = dict(base='#30564c', light='#3e6a5a', rim='#80aa8e', sh='#203c38')
BOIS = dict(base='#5a424c', light='#72565c', rim='#a88a86', sh='#3c2c36')
TOIT = dict(base='#2c2e48', light='#3e4466', rim='#7e8cc0', sh='#1c1c30')           # tuiles noir corbeau
VERMILLON = dict(base='#b04238', light='#c65a48', rim='#ec9474', sh='#7c2a30')
IVOIRE = dict(base='#d2c6ba', light='#e2d6c8', rim='#fbf0e2', sh='#a49892')
OR = dict(base='#c8a052', light='#e0bc6a', rim='#fce0a0', sh='#8a6a3a')
CORBEAU = dict(base='#262840', light='#363c58', rim='#6c78a6', sh='#181a2a')        # les bannières
GRANIT = dict(base='#7a7488', light='#8e889a', rim='#bab2c4', sh='#5a546c')         # la pierre levée
SOL = dict(back='#69647a', front='#77717f')                                         # la terrasse : valeur moyenne
PETALE = dict(base='#f0c4cc', light='#fbe0e4', sh='#d89aaa')


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


def trait(pts, ws, n=16):
    """Un ruban effilé le long d'une ligne douce (branches, cordes, reliefs) ; ws : largeurs aux points donnés."""
    c = resample(catmull(pts), n)
    wl = []
    for i in range(n + 1):
        f = i / n * (len(ws) - 1)
        j = min(len(ws) - 2, int(f))
        wl.append(ws[j] + (ws[j + 1] - ws[j]) * (f - j))
    return ribbon(c, wl)


def tige(pts, ws, n=16):
    """Comme trait(), mais aux bouts carrés (un tronc, une corde tendue entre deux points)."""
    c = resample(catmull(pts), n)
    wl = []
    for i in range(n + 1):
        f = i / n * (len(ws) - 1)
        j = min(len(ws) - 2, int(f))
        wl.append(ws[j] + (ws[j + 1] - ws[j]) * (f - j))
    left, right = sides(c, wl)
    return sm(left + right[::-1], sharp=(0, len(left) - 1, len(left), 2 * len(left) - 1), t=0.8)


# ------------------------------------------------------------------------------------------------ les profils
# Le piton du pin (à gauche), le piton du temple (au milieu), l'éperon (à droite) : leurs pieds plongent dans la mer
# de nuages (vers y = 700), qui les cache.
PIN_HAUT = [(-14, 612), (20, 606), (60, 602), (96, 604), (128, 606), (160, 603), (180, 606)]
PIN_FACE = [(186, 628), (180, 664), (190, 704), (196, 760)]
TEMPLE_HAUT = [(238, 584), (270, 582), (300, 581), (334, 582), (364, 584)]
TEMPLE_G = [(232, 602), (236, 640), (224, 690), (218, 760)]
TEMPLE_D = [(372, 606), (368, 650), (380, 700), (386, 760)]
EPERON_FACE = [(412, 760), (404, 704), (410, 664), (400, 632), (408, 618)]
EPERON_HAUT = [(422, 613), (452, 615), (482, 612), (520, 616), (560, 612), (604, 616)]


def sol_g(x):
    return interp(PIN_HAUT, x)


def sol_d(x):
    return interp(EPERON_HAUT, x)


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
SOLEIL = (452, 392)          # vu sur tous les téléphones, à droite des pilules du haut


@element('ciel', -29.9, 'fixe')
def ciel(doc):
    out = [path('M-20 -20H610V800H-20Z', doc.lin(0, 0, 0, 790, CIEL))]
    # la lueur de l'aube sur l'horizon, plus forte à droite (côté soleil)
    out.append('<ellipse cx="380" cy="700" rx="380" ry="200" fill="%s"/>' % doc.rad(
        380, 700, 380, [(0, '#eeb898', 0.5), (0.5, '#d29c9a', 0.22), (1, '#b28298', 0)], ry=200))
    # le soleil levant pâle (la seule lumière)
    sx, sy = SOLEIL
    out.append('<circle cx="%d" cy="%d" r="130" fill="%s"/>' % (sx, sy, doc.rad(
        sx, sy, 130, [(0, '#ffe6c0', 0.34), (0.35, '#f0b8a0', 0.14), (1, '#b28298', 0)])))
    out.append('<circle cx="%d" cy="%d" r="22" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 6, sy - 6, 27, [(0, '#fffaf0'), (0.7, '#ffeccc'), (1, '#f6cfa8')])))
    return ''.join(out)


def lobes_dores(doc, x0, x1, yb, lobes, m, sag=4, r=2.4, c=3.6):
    """Un banc de nuages éclairé par l'aube : le bord doré en haut à droite."""
    return vol(doc, lobes_shape(x0, x1, yb, lobes, sag=sag), m, r=r, c=c, rim_op=0.85)


@element('nuages', -29.5, 'fixe')
def nuages(doc):
    out = []
    # A : le grand banc en haut à gauche (le haut des téléphones longs)
    out.append(lobes_dores(doc, -30, 250, 232, [(232, 222, 16), (196, 208, 26), (150, 196, 30), (100, 192, 32),
                                                (50, 196, 30), (4, 204, 28), (-30, 216, 20)], NUAGE2, sag=4))
    out.append(lobes_dores(doc, -30, 300, 326, [(282, 316, 16), (246, 300, 28), (200, 284, 36), (148, 276, 38),
                                                (94, 270, 40), (42, 274, 38), (-6, 286, 34), (-30, 302, 26)],
                           NUAGE, sag=6, r=2.8, c=4))
    # B : en haut à droite
    out.append(lobes_dores(doc, 380, 620, 292, [(612, 280, 16), (578, 268, 22), (540, 262, 22), (500, 266, 20),
                                                (460, 272, 18), (414, 280, 14)], NUAGE, sag=3))
    # C : un petit banc sous le soleil (il le voile à peine), E : un petit à gauche
    out.append(lobes_dores(doc, 470, 620, 428, [(608, 420, 11), (578, 412, 15), (542, 410, 14), (506, 416, 11),
                                                (482, 422, 7)], dict(NUAGE, base='#7a6696', light='#8a74a2'),
                           sag=2, r=2, c=2.6))
    out.append(lobes_dores(doc, 92, 214, 380, [(204, 374, 9), (176, 366, 13), (140, 364, 14), (106, 370, 11)],
                           dict(NUAGE, base='#6a5c90', light='#7a6a9c'), sag=2, r=2, c=2.6))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
def pics(doc, ridge, m, tips, lit=0.5):
    """Une chaîne de pics : la silhouette, puis une facette éclairée à droite de chaque sommet (la lumière vient
    d'en haut à droite) ; tips = les indices des sommets dans ridge."""
    s = sm(ridge, sharp=(0, 1, len(ridge) - 2, len(ridge) - 1) + tuple(tips), t=0.55)
    out = [vol(doc, s, m, r=1.4, c=0)]
    inner = []
    for i in tips:
        x, y = ridge[i]
        xb = ridge[i + 1][0]
        yb = ridge[i + 1][1]
        inner.append(path(sm([(x, y), (xb + (x - xb) * 0.05, yb), (x + (xb - x) * 0.35, 720)], sharp=(0, 1, 2), t=0.4),
                          m['light'], lit))
        inner.append(path(sm([(x, y), (x - (x - ridge[i - 1][0]) * 0.25, 720), (x - (x - ridge[i - 1][0]) * 0.75,
                                                                               ridge[i - 1][1] + 30)],
                             sharp=(0, 1, 2), t=0.4), m['sh'], 0.35))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


@element('lointain', -28.5, 'fixe')
def lointain(doc):
    out = []
    r1 = [(-20, 760), (-20, 640), (14, 596), (40, 572), (74, 604), (112, 632), (156, 612), (206, 566), (236, 544),
          (272, 586), (330, 612), (380, 576), (430, 556), (470, 540), (510, 566), (560, 598), (610, 584), (610, 760)]
    out.append(pics(doc, r1, LOIN1, (3, 8, 13), lit=0.55))
    r2 = [(-20, 760), (-20, 672), (36, 650), (86, 618), (128, 654), (176, 672), (222, 638), (262, 662), (330, 676),
          (392, 642), (440, 614), (488, 648), (540, 664), (610, 640), (610, 760)]
    out.append(pics(doc, r2, LOIN2, (3, 6, 10), lit=0.45))
    # la brume de l'aube monte sur le pied des pics (ils se perdent dans la mer de nuages)
    out.append(path('M-20 600H610V760H-20Z', doc.lin(0, 600, 0, 712, [(0, '#c89aa0', 0), (0.6, '#c49aa4', 0.4),
                                                                      (1, '#c2a0ac', 0.75)])))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le temple
TX = 300
PLINTHE = 576


def toit(cx, y_eave, y_top, half, top_half, lift):
    """Un toit de pagode : les bords se relèvent en pointe aux coins (lift), la pente se creuse vers le haut."""
    l, r = cx - half, cx + half
    pts = [(l, y_eave - lift), (l + half * 0.16, y_eave - lift * 0.55), (l + half * 0.48, y_eave - (y_eave - y_top) * 0.35),
           (cx - top_half - 2, y_top + 3), (cx - top_half, y_top), (cx + top_half, y_top), (cx + top_half + 2, y_top + 3),
           (r - half * 0.48, y_eave - (y_eave - y_top) * 0.35), (r - half * 0.16, y_eave - lift * 0.55),
           (r, y_eave - lift), (r - half * 0.1, y_eave - lift * 0.2), (r - half * 0.4, y_eave + 1), (cx, y_eave + 2),
           (l + half * 0.4, y_eave + 1), (l + half * 0.1, y_eave - lift * 0.2)]
    return sm(pts, sharp=(0, 4, 5, 9), t=0.75)


def mur(doc, x0, x1, y0, y1, piliers=(), porte=None, fenetres=()):
    """Un étage : le mur ivoire, ses piliers vermillon, sa porte et ses fenêtres sombres, l'ombre du toit en haut."""
    out = [vol(doc, rpoly([(x0, y1), (x0, y0), (x1, y0), (x1, y1)], 0.6), IVOIRE, r=1.0, c=1.6, ink=INK, iw=0.8)]
    for (a, b) in fenetres:
        out.append(path(rpoly([(a, y0 + (y1 - y0) * 0.38), (b, y0 + (y1 - y0) * 0.38), (b, y1 - (y1 - y0) * 0.22),
                               (a, y1 - (y1 - y0) * 0.22)], 0.8), '#3a3046'))
    if porte:
        a, b = porte
        out.append(path(rpoly([(a, y1), (a, y0 + (y1 - y0) * 0.3), (b, y0 + (y1 - y0) * 0.3), (b, y1)], 1.0), '#2c2438'))
        out.append(path(rpoly([(a + 1.5, y1), (a + 1.5, y0 + (y1 - y0) * 0.3 + 2), ((a + b) / 2 - 0.5, y0 + (y1 - y0) * 0.3 + 2),
                               ((a + b) / 2 - 0.5, y1)], 0.5), '#4a3a4c', 0.8))
    for x in piliers:
        out.append(vol(doc, rpoly([(x - 2.2, y1), (x - 2.2, y0), (x + 2.2, y0), (x + 2.2, y1)], 0.5), VERMILLON,
                       r=0.7, c=0.9, ink=INK, iw=0.6))
    # la poutre rouge sous le toit et l'ombre du toit sur le mur
    out.append(vol(doc, rpoly([(x0 - 3, y0 + 4), (x0 - 3, y0), (x1 + 3, y0), (x1 + 3, y0 + 4)], 0.6), VERMILLON,
                   r=0.6, c=0.8, ink=INK, iw=0.6))
    out.append(path('M%s %sH%sV%sH%sZ' % (fm(x0), fm(y0 + 4), fm(x1), fm(y0 + 9), fm(x0)),
                    doc.lin(0, y0 + 4, 0, y0 + 9, [(0, '#2a2236', 0.45), (1, '#2a2236', 0)])))
    return ''.join(out)


def temple_brut(doc):
    out = []
    # le socle de pierre et ses deux marches
    out.append(vol(doc, rpoly([(250, PLINTHE + 2), (252, PLINTHE - 8), (348, PLINTHE - 8), (350, PLINTHE + 2)], 1.2),
                   PITON, r=1.2, c=1.6, ink=INK, iw=0.8))
    out.append(vol(doc, rpoly([(288, PLINTHE - 7), (290, PLINTHE - 12), (310, PLINTHE - 12), (312, PLINTHE - 7)], 0.8),
                   PITON, r=0.8, c=1.0, ink=INK, iw=0.6))
    # le rez-de-chaussée, le grand toit (lanternes : calques)
    out.append(mur(doc, 262, 338, 536, PLINTHE - 12, piliers=(264, 283, 317, 336), porte=(292, 308),
                   fenetres=((270, 278), (322, 330))))
    out.append(vol(doc, toit(TX, 534, 506, 76, 22, 13), TOIT, r=1.8, c=2.6, ink=INK, iw=1.0))
    # le 2e étage et son toit
    out.append(mur(doc, 279, 321, 488, 507, piliers=(281, 319), fenetres=((288, 296), (304, 312))))
    out.append(vol(doc, toit(TX, 489, 465, 62, 16, 11), TOIT, r=1.6, c=2.4, ink=INK, iw=1.0))
    # le 3e étage et son toit
    out.append(mur(doc, 286, 314, 450, 466, piliers=(288, 312), fenetres=((296, 304),)))
    out.append(vol(doc, toit(TX, 451, 430, 48, 10, 9), TOIT, r=1.4, c=2.0, ink=INK, iw=0.9))
    # les arêtes d'or au bout des toits (une petite pointe dorée à chaque coin relevé)
    for y_e, half, lift in ((534, 76, 13), (489, 62, 11), (451, 48, 9)):
        for sg in (-1, 1):
            x, y = TX + sg * half, y_e - lift
            out.append('<circle cx="%s" cy="%s" r="1.6" fill="%s" stroke="%s" stroke-width="0.7"/>' % (
                fm(x - sg * 0.5), fm(y - 0.8), doc.rad(x + 0.5, y - 1.5, 2, [(0, OR['rim']), (1, OR['base'])]), INK))
    # la flèche d'or : un mât, trois renflements (pas d'anneaux répétés), le signe au sommet
    out.append(vol(doc, rpoly([(TX - 1.4, 432), (TX - 1.4, 404), (TX + 1.4, 404), (TX + 1.4, 432)], 0.6), OR,
                   r=0.6, c=0.8, ink=INK, iw=0.6))
    for y, rx, ry in ((428, 5.5, 2.8), (419, 4.2, 2.2), (411, 3.0, 1.8)):
        out.append(vol(doc, ellipse(TX, y, rx, ry), OR, r=0.7, c=0.9, ink=INK, iw=0.6))
    for s in signe_formes(TX, 400, 0.95):
        out.append(path(s, OR['light']))
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.6" stroke-linejoin="round"/>' % (s.d(), INK))
    return ''.join(out)


@element('piton-temple', -27.5, 'fixe')
def piton_temple(doc):
    pts = [(214, 760)] + TEMPLE_G[::-1] + TEMPLE_HAUT + TEMPLE_D + [(390, 760)]
    s = sm(pts, sharp=(0, len(pts) - 1), t=0.75)
    g = doc.lin(380, 590, 230, 720, [(0, PITON['light']), (0.5, PITON['base']), (1, PITON['sh'])])
    out = [vol(doc, s, PITON, grad=g, r=2.0, c=3.2)]
    inner = []
    # la face droite, tournée vers la lumière : un grand pan plus clair ; une fente côté ombre ; une corniche
    inner.append(path(sm([(326, 590), (372, 600), (370, 650), (384, 720), (338, 724), (334, 660)], t=0.8),
                      PITON['light'], 0.6))
    inner.append(path(ribbon(resample([(258, 598), (252, 640), (262, 680), (250, 730)], 12),
                             [0.4, 1.4, 2.2, 2.8, 3.0, 2.8, 2.6, 2.2, 2, 1.6, 1.2, 0.8, 0.3]), PITON['sh'], 0.7))
    c = resample(catmull([(286, 640), (318, 634), (352, 642)]), 16)
    wl = [0.6 + 6 * math.sin(math.pi * i / 16) ** 0.8 for i in range(17)]
    inner.append(path(ribbon([(x, y + 4) for x, y in c], wl), PITON['sh'], 0.5))
    inner.append(path(ribbon(c, [w * 0.4 for w in wl]), PITON['rim'], 0.4))
    # un liseré de mousse sur le bord du dessus
    inner.append(path(sm([(238, 586), (270, 583), (300, 582), (334, 583), (364, 586), (360, 592), (330, 589),
                          (300, 590), (270, 590), (242, 593)], t=0.8), MOUSSE['base'], 0.85))
    inner.append(path('M200 650H400V760H200Z', doc.lin(0, 660, 0, 720, [(0, '#c49aa4', 0), (1, '#c2a0ac', 0.45)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


@element('temple', -27, 'fixe')
def temple(doc):
    return temple_brut(doc)


# ---------------------------------------------------------------------------------------------------- le signe
def signe_formes(cx, cy, k):
    """Le signe d'Orin : une plume dressée dont la pointe s'enroule sur le côté (le vent), et deux ailes déployées à
    l'horizontale de part et d'autre de sa tige, leurs pennes tournées vers le bas ; aucune lettre. Des formes séparées
    (chacune remplie de la même couleur)."""
    def P(u, v):
        return (cx + u * k, cy + v * k)
    plume = sm([P(0, 8), P(-1.3, 4), P(-1.6, -0.5), P(-1.0, -4.6), P(0.2, -6.4), P(1.4, -4.6), P(1.6, -0.5),
                P(1.2, 4)], sharp=(0,), t=0.85)
    spirale = []
    for i in range(16):
        a = math.radians(170 - i * 26)
        rr = 3.0 - i * 0.13
        spirale.append(P(2.6 + rr * math.cos(a), -7.4 - rr * math.sin(a)))
    volute = ribbon(spirale, [0.3 + 0.75 * math.sin(math.pi * i / 15) for i in range(16)])
    ailes = []
    for sg in (-1, 1):
        ailes.append(sm([P(sg * 1.0, 0.4), P(sg * 4.0, -0.6), P(sg * 7.6, -1.4), P(sg * 7.0, 0.8), P(sg * 6.0, 2.6),
                         P(sg * 5.0, 1.6), P(sg * 4.0, 3.2), P(sg * 3.0, 2.0), P(sg * 1.6, 3.0)],
                        sharp=(2, 4, 6, 8), t=0.75))
    return [plume, volute] + ailes


# ---------------------------------------------------------------------------------------------------- le pin, le pont
@element('piton-pin', -20, 'fixe')
def piton_pin(doc):
    out = []
    pts = [(-14, 760)] + PIN_HAUT + PIN_FACE
    s = sm(pts, sharp=(0, 1, len(pts) - 1), t=0.75)
    g = doc.lin(190, 600, 20, 740, [(0, FAL['light']), (0.45, FAL['base']), (1, FAL['sh'])])
    out.append(vol(doc, s, FAL, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0))
    inner = []
    inner.append(path(sm([(140, 610), (182, 608), (186, 640), (182, 670), (194, 720), (150, 724), (146, 660)], t=0.8),
                      FAL['light'], 0.6))
    inner.append(path(ribbon(resample([(66, 626), (60, 664), (70, 700), (58, 740)], 12),
                             [0.4, 1.6, 2.4, 2.8, 3.0, 2.8, 2.6, 2.2, 2, 1.6, 1.2, 0.8, 0.3]), FAL['sh'], 0.75))
    c = resample(catmull([(10, 664), (50, 658), (96, 668), (130, 676)]), 16)
    wl = [0.6 + 6 * math.sin(math.pi * i / 16) ** 0.8 for i in range(17)]
    inner.append(path(ribbon([(x, y + 4) for x, y in c], wl), FAL['sh'], 0.5))
    inner.append(path(ribbon(c, [w * 0.4 for w in wl]), FAL['rim'], 0.4))
    # l'herbe et la mousse du dessus
    inner.append(path(sm([(-14, 614), (20, 607), (60, 603), (96, 605), (128, 607), (160, 604), (182, 607),
                          (176, 614), (140, 612), (100, 613), (60, 611), (20, 615), (-14, 620)], t=0.8),
                      MOUSSE['base'], 0.9))
    inner.append(path(sm([(60, 604), (96, 605), (128, 607), (150, 606), (130, 610), (96, 609)], t=0.8),
                      MOUSSE['light'], 0.8))
    inner.append(path('M-20 660H200V760H-20Z', doc.lin(0, 670, 0, 730, [(0, '#c49aa4', 0), (1, '#c2a0ac', 0.4)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


PONT_A, PONT_B = (176, 607), (244, 584)


@element('pont', -21, 'fixe')
def pont(doc):
    """Le pont de cordes, du piton du pin au piton du temple : un tablier plein (pas de planches une à une), deux
    mains courantes, un poteau à chaque bout planté dans la roche."""
    (ax, ay), (bx, by) = PONT_A, PONT_B
    deck = [(ax + (bx - ax) * u, ay + (by - ay) * u + 11 * math.sin(math.pi * u)) for u in [i / 16 for i in range(17)]]
    out = [path(tige(deck, [2.4, 2.4], n=16), BOIS['sh'])]
    out.append(path(tige([(x, y - 0.8) for x, y in deck], [1.0, 1.0], n=16), BOIS['light'], 0.8))
    rope = [(x, y - 9 + 3 * math.sin(math.pi * i / 16)) for i, (x, y) in enumerate(deck)]
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.9" stroke-linecap="round"/>' % (
        polyline_d(rope), BOIS['base']))
    for (x, y), h_ in (((ax + 1, ay + 1), 12), ((bx - 1, by + 1), 12)):
        out.append(vol(doc, rpoly([(x - 1.4, y + 2), (x - 1.4, y - h_), (x + 1.4, y - h_), (x + 1.4, y + 2)], 0.6),
                       BOIS, r=0.6, c=0.7, ink=INK, iw=0.6))
    return ''.join(out)


PIN_PADS = [
    # (x0, x1, y du bas, lobes [(cx, cy, r)] de droite à gauche), phase du balancement
    ((136, 192, 516, [(186, 512, 6), (172, 506, 9), (156, 503, 10), (142, 508, 7)]), 0.0),
    ((176, 214, 530, [(208, 527, 5), (198, 522, 8), (184, 521, 8)]), 0.7),
    ((184, 210, 546, [(205, 544, 4), (196, 540, 6), (188, 541, 5)]), 1.3),
    ((62, 104, 552, [(98, 549, 6), (86, 543, 8), (70, 545, 7)]), 2.1),
    ((106, 140, 534, [(134, 531, 5), (124, 526, 7), (112, 528, 6)]), 2.8),
]


def pin(doc, ph):
    """Le grand pin tordu, couché vers la droite par le vent : tronc et branches fixes, les coussins d'aiguilles se
    balancent un peu (plus en haut qu'en bas)."""
    a = 2 * math.pi * ph
    out = []
    branches = [
        ([(114, 608), (118, 590), (128, 572), (140, 554), (150, 538), (158, 522)], [8, 7, 6, 5, 4, 3]),
        ([(150, 538), (170, 530), (190, 528), (206, 534)], [3.4, 2.8, 2.2, 1.4]),
        ([(176, 530), (186, 538), (196, 544)], [1.8, 1.4, 1.0]),
        ([(132, 568), (114, 560), (96, 554), (80, 552)], [3.0, 2.4, 1.8, 1.2]),
        ([(142, 552), (128, 540), (120, 532)], [2.0, 1.6, 1.0]),
    ]
    for pts, ws in branches:
        out.append(vol(doc, tige(pts, ws), BOIS, r=0.8, c=1.0, ink=INK, iw=0.8))
    # les racines posées sur la roche
    out.append(vol(doc, sm([(104, 611), (110, 604), (118, 602), (126, 606), (132, 611)], sharp=(0, 4), t=0.8), BOIS,
                   r=0.6, c=0.8, ink=INK, iw=0.8))
    for (x0, x1, yb, lobes), p in PIN_PADS:
        dx = 1.6 * math.sin(a + p) * (1 + (560 - yb) / 60)
        dy = 0.5 * math.sin(a * 2 + p)
        lob = [(cx + dx, cy + dy, r) for cx, cy, r in lobes]
        s = lobes_shape(x0 + dx, x1 + dx, yb + dy, lob, sag=1.5)
        out.append(vol(doc, s, PIN, r=1.3, c=2.0, ink=INK, iw=0.9))
    return ''.join(out)


element('pin', -16, 'boucle', box=(52, 494, 170, 122), n=12, ms=200)(pin)


# ---------------------------------------------------------------------------------------------------- l'éperon
@element('eperon', -20, 'fixe')
def eperon(doc):
    pts = EPERON_FACE + EPERON_HAUT + [(604, 760)]
    s = sm(pts, sharp=(0, len(pts) - 2, len(pts) - 1), t=0.75)
    g = doc.lin(600, 610, 410, 740, [(0, FAL['light']), (0.45, FAL['base']), (1, FAL['sh'])])
    out = [vol(doc, s, FAL, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0)]
    inner = []
    inner.append(path(sm([(500, 620), (604, 620), (604, 700), (540, 712), (510, 670)], t=0.8), FAL['light'], 0.5))
    inner.append(path(ribbon(resample([(452, 632), (458, 676), (448, 716), (454, 750)], 12),
                             [0.4, 1.4, 2.2, 2.6, 2.8, 2.6, 2.4, 2.2, 2, 1.6, 1.2, 0.8, 0.3]), FAL['sh'], 0.75))
    inner.append(path(sm([(398, 626), (424, 650), (430, 720), (420, 770), (398, 770)], t=0.8), FAL['sh'], 0.45))
    c = resample(catmull([(470, 680), (514, 672), (560, 678), (604, 672)]), 16)
    wl = [0.6 + 6 * math.sin(math.pi * i / 16) ** 0.8 for i in range(17)]
    inner.append(path(ribbon([(x, y + 4) for x, y in c], wl), FAL['sh'], 0.5))
    inner.append(path(ribbon(c, [w * 0.4 for w in wl]), FAL['rim'], 0.4))
    inner.append(path(sm([(406, 620), (422, 614), (452, 616), (482, 613), (520, 617), (560, 613), (604, 617),
                          (604, 624), (560, 620), (520, 623), (482, 620), (452, 622), (420, 622)], t=0.8),
                      MOUSSE['base'], 0.9))
    inner.append(path('M380 660H610V770H380Z', doc.lin(0, 670, 0, 730, [(0, '#c49aa4', 0), (1, '#c2a0ac', 0.4)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


PIERRE = (458, sol_d(458))


def pierre(doc, ph):
    """La pierre levée du clan : le signe rempli d'or (son éclat respire), la corde rouge et ses deux glands qui
    bougent au vent."""
    x, y = PIERRE
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    s = sm([(x - 11, y + 2), (x - 12.5, y - 18), (x - 11, y - 38), (x - 5, y - 48), (x + 4, y - 46), (x + 10, y - 40),
            (x + 12.5, y - 20), (x + 11.5, y + 2)], sharp=(0, 3, 4, 7), t=0.7)
    out = [vol(doc, s, GRANIT, r=1.4, c=2.6, ink=INK, iw=1.0, rim_op=0.7)]
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), path(sm([(x + 2, y - 47), (x + 13, y - 38),
                                                                         (x + 13, y + 2), (x + 5, y + 2),
                                                                         (x + 6, y - 30)], t=0.8), GRANIT['light'], 0.5)))
    # le signe gravé : un creux sombre, puis l'or dedans
    for f in signe_formes(x, y - 26, 1.35):
        out.append(path(f.move(-0.6, 0.6), '#4e4860', 0.9))
        out.append(path(f, mix(OR['base'], OR['rim'], 0.25 + 0.55 * k)))
    out.append('<ellipse cx="%s" cy="%s" rx="10" ry="12" fill="%s"/>' % (x, y - 26, doc.rad(
        x, y - 26, 10, [(0, '#ffe8b0', 0.10 + 0.18 * k), (1, '#ffe0a0', 0)], ry=12)))
    # la corde rouge (un peu sous le milieu), son nœud, ses deux glands
    cy = y - 12
    corde = sm([(x - 12.5, cy - 1.5), (x, cy - 0.5), (x + 12.5, cy - 2.2), (x + 12.5, cy + 1.2), (x, cy + 2.8),
                (x - 12.5, cy + 1.8)], sharp=(0, 2, 3, 5), t=0.8)
    out.append(vol(doc, corde, VERMILLON, r=0.6, c=0.8, ink=INK, iw=0.7))
    a = 2 * math.pi * ph
    for k_, (bx, sw) in enumerate(((x - 4, 0.0), (x + 4, 1.1))):
        ang = 7 * math.sin(a + sw) + 5            # le vent vient de la gauche
        r_ = math.radians(ang)
        L = 9
        ex, ey = bx + L * math.sin(r_), cy + 2 + L * math.cos(r_)
        out.append('<path d="M%s %s L%s %s" stroke="%s" stroke-width="0.9" stroke-linecap="round"/>' % (
            fm(bx), fm(cy + 2), fm(ex), fm(ey), VERMILLON['sh']))
        g = sm([(ex - 1.8, ey - 0.6), (ex + 1.8, ey - 0.6), (ex + 2.2, ey + 4.4), (ex, ey + 5.4), (ex - 2.2, ey + 4.4)],
               sharp=(0, 1), t=0.8)
        out.append(vol(doc, g, VERMILLON, r=0.5, c=0.7, ink=INK, iw=0.6))
        out.append('<circle cx="%s" cy="%s" r="1.3" fill="%s" stroke="%s" stroke-width="0.5"/>' % (
            fm(ex), fm(ey - 0.6), OR['light'], INK))
    # le socle de cailloux (posée)
    out.append(vol(doc, rpoly([(x - 15, y + 4), (x - 14, y - 2), (x + 14, y - 3), (x + 16, y + 4)], 1.5), ROC,
                   r=0.9, c=1.2, ink=INK, iw=0.9))
    return ''.join(out)


element('pierre', -16.5, 'boucle', box=(PIERRE[0] - 18, PIERRE[1] - 52, 40, 60), n=12, ms=400)(pierre)

MATS = [(426, sol_d(426)), (494, sol_d(494))]
MAT_H = 52


def mat(doc, x, y):
    out = [vol(doc, rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6),
               BOIS, r=0.7, c=0.8, ink=INK, iw=0.7)]
    out.append(vol(doc, rpoly([(x - 13, y - MAT_H + 2), (x + 13, y - MAT_H + 2), (x + 13, y - MAT_H + 5),
                               (x - 13, y - MAT_H + 5)], 1.2), BOIS, r=0.7, c=0.8, ink=INK, iw=0.7))
    out.append('<circle cx="%s" cy="%s" r="2.6" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        x, y - MAT_H - 1, doc.rad(x + 1, y - MAT_H - 2, 3, [(0, OR['rim']), (1, OR['base'])]), INK))
    out.append(vol(doc, rpoly([(x - 6, y + 3), (x - 5, y - 2), (x + 5, y - 2.5), (x + 7, y + 3)], 1.2), ROC,
                   r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


def banniere(k):
    x, y = MATS[k]
    top = y - MAT_H + 5

    def fn(doc, ph):
        # la toile noir corbeau pend sous la traverse ; elle ondule, poussée vers la droite (le vent vient de la gauche)
        L, w_ = 34, 22
        a = 2 * math.pi * ph

        def P(u, v):          # u : -1..1 en travers, v : 0..1 en descendant
            sway = v ** 1.5 * (2.4 * math.sin(a + v * 2.2 + k * 1.7) + 1.4)
            return (x + u * w_ / 2 * (1 - 0.08 * v) + sway, top + v * L + 0.8 * math.sin(a + u * 1.5 + k) * v)
        pts = [P(-1, 0), P(1, 0)]
        for v in (0.33, 0.66, 0.92):
            pts.append(P(1, v))
        pts += [P(1, 1.04), P(0.5, 0.9), P(0, 1.08), P(-0.5, 0.9), P(-1, 1.04)]
        for v in (0.92, 0.66, 0.33):
            pts.append(P(-1, v))
        s = sm(pts, sharp=(0, 1, 5, 7, 9), t=0.6)
        out = [mat(doc, x, y), vol(doc, s, CORBEAU, r=1.3, c=2.0, ink=INK, iw=0.9)]
        sx, sy = P(0, 0.45)
        for f in signe_formes(sx, sy + 0.5, 1.1):
            out.append(path(f, OR['light']))
        return ''.join(out)
    return fn


for _k in range(2):
    _x, _y = MATS[_k]
    element('banniere%d' % (_k + 1), -16, 'boucle', box=(_x - 18, _y - MAT_H - 5, 42, MAT_H + 10), n=12,
            ms=200)(banniere(_k))


# ---------------------------------------------------------------------------------------------------- les lanternes du temple
LANTERNES = [(TX - 76 + 0.5, 534 - 13), (TX + 76 - 0.5, 534 - 13)]


def lanterne(k):
    x, y = LANTERNES[k]

    def fn(doc, ph):
        a = math.radians(5 * math.sin(2 * math.pi * ph + k * 1.3) + 3)     # poussée vers la droite par le vent
        L = 6

        def R(u, v):        # repère de la lanterne : u en travers, v vers le bas depuis le point d'attache
            return (x + u * math.cos(a) + v * math.sin(a), y + v * math.cos(a) - u * math.sin(a))
        out = ['<path d="M%s %s L%s %s" stroke="%s" stroke-width="0.8"/>' % (
            fm(x), fm(y), fm(R(0, L)[0]), fm(R(0, L)[1]), '#2a2236')]
        cx, cy = R(0, L + 6)
        out.append('<ellipse cx="%s" cy="%s" rx="9" ry="10" fill="%s"/>' % (fm(cx), fm(cy), doc.rad(
            cx, cy, 9, [(0, '#ffb070', 0.32), (1, '#ff8a50', 0)], ry=10)))
        body = sm([R(-3.6, L + 1.6), R(3.6, L + 1.6), R(4.6, L + 6), R(3.6, L + 10.4), R(-3.6, L + 10.4),
                   R(-4.6, L + 6)], t=0.9)
        out.append(vol(doc, body, dict(base='#d24a3a', light='#ee7a54', rim='#ffc09a', sh='#902c30'), r=0.8, c=1.0,
                       ink=INK, iw=0.6))
        for v in (L + 1.2, L + 10.8):
            out.append(vol(doc, rpoly([R(-2.2, v - 0.9), R(2.2, v - 0.9), R(2.2, v + 0.9), R(-2.2, v + 0.9)], 0.3),
                           OR, r=0.3, c=0.4, ink=INK, iw=0.4))
        return ''.join(out)
    return fn


for _k in range(2):
    _x, _y = LANTERNES[_k]
    element('lanterne%d' % (_k + 1), -26, 'boucle', box=(_x - 10, _y - 2, 20, 26), n=12, ms=200)(lanterne(_k))


# ---------------------------------------------------------------------------------------------------- la mer de nuages
MER = (0, 690, 590, 92)          # la boîte du défilé (x, y, w, h)
MER_T = (192, 92)                # la tuile


def profil_lobes(lobes, tw, x0, x1, base, off=0.0, n_par_tuile=240):
    """Le dessus d'un rang de nuages (bouffées réunies en une seule masse) : pour chaque x, le plus haut des demi-ovales
    (cx, cy, rx, ry), répétés tous les tw et décalés de off (la tuile se raccorde exactement)."""
    n = max(2, round((x1 - x0) / tw * n_par_tuile))
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = base
        for cx, cy, rx, ry in lobes:
            dx = (x - off - cx + tw / 2) % tw - tw / 2
            u = dx / rx
            if abs(u) < 1:
                y = min(y, cy - ry * math.sqrt(1 - u * u))
        pts.append((x, y))
    return pts


MER_RANGS = [
    # (bas du rang, lobes (cx, cy, rx, ry), teintes) : du lointain vers l'avant
    (30, [(6, 24, 20, 7), (34, 22, 16, 9), (62, 25, 22, 6), (96, 23, 18, 9), (124, 25, 16, 6), (150, 22, 20, 9),
          (178, 25, 16, 7)],
     dict(base='#b496b4', light='#c0a0b6', rim='#eac6b4', sh='#a28aac')),
    (52, [(14, 46, 26, 11), (52, 44, 22, 13), (92, 48, 24, 9), (128, 43, 26, 14), (168, 47, 24, 11)],
     dict(base='#a88eb0', light='#b498b4', rim='#e2bab0', sh='#9682a8')),
    (96, [(0, 74, 34, 15), (50, 70, 30, 17), (98, 75, 30, 12), (140, 70, 34, 17)],
     dict(base='#9c86aa', light='#a890b0', rim='#d8b2ac', sh='#8a78a2')),
]


def mer_dessin(doc, x0, x1, off=0.0):
    """La mer de nuages de x0 à x1 (repère de la tuile, haut = 0), décalée de off : trois rangs de bouffées larges
    et basses, réunies (une masse par rang, plus grosses vers l'avant), le dessus rosé par l'aube, peu de contraste."""
    tw, th = MER_T
    out = [path('M%s 16H%sV%dH%sZ' % (fm(x0), fm(x1), th, fm(x0)), doc.lin(0, 16, 0, th, [(0, '#a68cb0'),
                                                                                           (1, '#8a78a2')]))]
    for yb, lobes, m in MER_RANGS:
        top = profil_lobes(lobes, tw, x0, x1, yb, off)
        s = sm(top + [(x1, th + 4), (x0, th + 4)], t=0.0)
        g = doc.lin(0, min(y for _, y in top), 0, yb + 4, [(0, m['light']), (0.55, m['base']), (1, m['sh'])])
        out.append(vol(doc, s, m, grad=g, r=1.3, c=0, rim_op=0.7))
    return ''.join(out)


def mer_tuile(doc):
    """La tuile (192 × 92) : le dessin déborde de 8 de chaque côté, la boîte de la tuile le coupe."""
    return mer_dessin(doc, -8, MER_T[0] + 8)


def mer(doc, off):
    x, y, w, h = MER
    return '<g clip-path="%s"><g transform="translate(%s %s)">%s</g></g>' % (
        doc.clip('M%d %dH%dV%dH%dZ' % (x, y, x + w, y + h, x)), fm(x), fm(y), mer_dessin(doc, -10, w + 10, off))


element('mer', -18, 'defile', box=MER, tuile=MER_T, vx=10.0, vy=0.0, dessin=mer, tuile_dessin=mer_tuile)

BRUME = (0, 640, 590, 48)
BRUME_T = (192, 48)
ECHARPES = ((44, 26, 60, 11, 0.24), (146, 34, 46, 9, 0.18))


def brume_dessin(doc, k0, k1, off=0.0):
    """Des écharpes de brume claire, longues et douces (transparentes), une fois par tuile de k0 à k1."""
    tw, th = BRUME_T
    out = []
    for k in range(k0, k1 + 1):
        for x, y, rx, ry, op in ECHARPES:
            cx = x + k * tw + off
            out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(cx), fm(y), fm(rx), fm(ry), doc.rad(cx, y, rx, [(0, '#e6cad0', op), (0.6, '#dcc0cc', op * 0.6),
                                                                  (1, '#d4b8c8', 0)], ry=ry)))
    return ''.join(out)


def brume_tuile(doc):
    return brume_dessin(doc, -1, 1)


def brume(doc, off):
    x, y, w, h = BRUME
    return '<g clip-path="%s"><g transform="translate(%s %s)">%s</g></g>' % (
        doc.clip('M%d %dH%dV%dH%dZ' % (x, y, x + w, y + h, x)), fm(x), fm(y),
        brume_dessin(doc, -2, w // BRUME_T[0] + 2, off))


element('brume', -19, 'defile', box=BRUME, tuile=BRUME_T, vx=20.0, vy=0.0, dessin=brume, tuile_dessin=brume_tuile)


# ---------------------------------------------------------------------------------------------------- la corniche
TORO = [(92, 786), (500, 786)]


def toro(doc, x, y):
    """Une lanterne de pierre posée sur la corniche : socle, fût, la loge de la flamme (vide : la flamme est un calque),
    le chapeau recourbé, le bouton du haut."""
    out = []
    out.append(vol(doc, rpoly([(x - 7, y + 1), (x - 6, y - 3), (x + 6, y - 3), (x + 7, y + 1)], 1.0), GRANIT,
                   r=0.6, c=0.8, ink=INK, iw=0.7))
    out.append(vol(doc, rpoly([(x - 2.4, y - 2), (x - 2.4, y - 13), (x + 2.4, y - 13), (x + 2.4, y - 2)], 0.6), GRANIT,
                   r=0.6, c=0.8, ink=INK, iw=0.7))
    out.append(vol(doc, rpoly([(x - 6, y - 12), (x - 6, y - 14), (x + 6, y - 14), (x + 6, y - 12)], 0.6), GRANIT,
                   r=0.5, c=0.6, ink=INK, iw=0.6))
    out.append(vol(doc, rpoly([(x - 5, y - 14), (x - 5, y - 22), (x + 5, y - 22), (x + 5, y - 14)], 0.8), GRANIT,
                   r=0.6, c=0.8, ink=INK, iw=0.7))
    out.append(path(rpoly([(x - 2.6, y - 15), (x - 2.6, y - 21), (x + 2.6, y - 21), (x + 2.6, y - 15)], 0.6), '#3a2e3a'))
    out.append(vol(doc, toit(x, y - 22, y - 27, 9, 2.5, 2.4), GRANIT, r=0.6, c=0.8, ink=INK, iw=0.7))
    out.append(vol(doc, ellipse(x, y - 28.4, 1.6, 1.8), GRANIT, r=0.4, c=0.5, ink=INK, iw=0.5))
    return ''.join(out)


@element('rives', -17.5, 'morceau', box=(0, 754, 590, P0 - 754))
def rives(doc):
    """La corniche de roche moussue derrière la terrasse (elle cache le pied de la mer de nuages), et ses deux
    lanternes de pierre."""
    out = []
    pts = [(-10, P0 + 4), (-10, 780), (30, 777), (80, 780), (130, 776), (190, 779), (250, 775), (300, 778),
           (360, 775), (420, 779), (480, 776), (540, 780), (600, 777), (600, P0 + 4)]
    s = sm(pts, sharp=(0, 1, len(pts) - 2, len(pts) - 1), t=0.7)
    out.append(vol(doc, s, FAL, grad=doc.lin(0, 776, 0, P0, [(0, '#5e5872'), (0.5, '#4a455e'), (1, '#383450')]),
                   r=1.4, c=0))
    # des coussins de mousse posés sur le dessus (quelques-uns, de tailles différentes)
    for x0, x1, h_ in ((14, 70, 3.2), (150, 230, 3.6), (316, 352, 2.6), (420, 470, 3.0), (536, 600, 3.4)):
        yb = interp(pts[1:-1], (x0 + x1) / 2) + 2.5
        m = sm([(x0, yb), (x0 + (x1 - x0) * 0.2, yb - h_), (x0 + (x1 - x0) * 0.6, yb - h_ * 1.15), (x1, yb)],
               sharp=(0, 3), t=0.8)
        out.append(vol(doc, m, MOUSSE, r=0.9, c=0, rim_op=0.6))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0 - 2, P0), '#2a2638', 0.7))
    for x, y in TORO:
        out.append(toro(doc, x, y))
    return ''.join(out)


def flamme(k):
    x, y = TORO[k]

    def fn(doc, ph):
        a = 2 * math.pi * ph
        f = 0.5 + 0.5 * math.sin(a + k) * 0.6 + 0.2 * math.sin(3 * a + k * 2)
        out = ['<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            x, y - 18, fm(9 + 1.5 * f), fm(8 + 1.2 * f), doc.rad(x, y - 18, 10, [
                (0, '#ffc070', 0.3 + 0.12 * f), (1, '#ffa050', 0)], ry=9))]
        out.append(path(rpoly([(x - 2.6, y - 15), (x - 2.6, y - 21), (x + 2.6, y - 21), (x + 2.6, y - 15)], 0.6),
                        doc.rad(x, y - 16.5, 4, [(0, '#fff0c0'), (0.6, '#ffc070'), (1, '#c86a3a')])))
        fl = sm([(x - 1.2, y - 15.4), (x - 1.0 + 0.3 * f, y - 18), (x + 0.2 * f, y - 19.6 - 0.8 * f), (x + 1.2, y - 17.6),
                 (x + 1.2, y - 15.4)], sharp=(2,), t=0.8)
        out.append(path(fl, '#fffbe8', 0.9))
        return ''.join(out)
    return fn


for _k in range(2):
    _x, _y = TORO[_k]
    element('flamme%d' % (_k + 1), -17, 'boucle', box=(_x - 12, _y - 28, 24, 20), n=8, ms=300)(flamme(_k))


# ---------------------------------------------------------------------------------------------------- la terrasse
def sol_x(g, y):
    """Le dallage en perspective : la coordonnée au sol g → x à l'écran (les joints filent vers le centre)."""
    k = (y - 600) / (P1 - 600)
    return 295 + g * k


@element('terrasse', -15.5, 'fixe')
def terrasse(doc):
    out = []
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, P0, 0, P1, [(0, SOL['back']), (1, SOL['front'])])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, 0, 590, 0, [(0, '#1e1a30', 0.06),
                                                                              (1, '#fff4e8', 0.04)])))
    # les grandes dalles de granit : des joints à peine marqués, décalés d'un rang à l'autre
    rows = [P0, 826, 856, 892, 936, 986, P1]
    joints = []
    for i in range(len(rows) - 1):
        ya, yb = rows[i], rows[i + 1]
        if i > 0:
            joints.append('M-10 %s H600' % fm(ya))
        step = 170
        off = (i % 2) * step / 2 + (i * 41) % 46
        g = -900 + off
        while g < 900:
            xa, xb = sol_x(g, ya), sol_x(g, yb)
            if -10 < min(xa, xb) and max(xa, xb) < 600:
                joints.append('M%s %s L%s %s' % (fm(xa), fm(ya + 1), fm(xb), fm(yb - 1)))
            g += step + 22 * math.sin(i * 2.7 + g)
    jd = ' '.join(joints)
    out.append('<path d="%s" fill="none" stroke="#fff6ee" stroke-width="1.2" opacity="0.05" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#25203a" stroke-width="1" opacity="0.11"/>' % jd)
    # quelques dalles un peu plus claires ou plus sombres, usées (très peu)
    for (g0, i, col, op) in ((-240, 1, '#fff4ee', 0.035), (40, 3, '#25203a', 0.04), (280, 2, '#fff4ee', 0.03),
                             (-110, 4, '#25203a', 0.035), (160, 5, '#fff4ee', 0.03)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 160, ya), ya), (sol_x(g0 + 160, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le bord arrière éclairé, la lumière rosée de l'aube sur le fond du dallage
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 1.6), '#a49cb0', 0.7))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 26), doc.lin(0, P0, 0, P0 + 26, [(0, '#e0b0a8', 0.08),
                                                                                       (1, '#e0b0a8', 0)])))
    # l'arête avant éclairée, puis le mur de la terrasse
    out.append(path('M-10 %dH600V%dH-10Z' % (P1, 1066), doc.lin(0, P1, 0, 1066, [
        (0, '#4c4660'), (0.5, '#423d56'), (1, '#36324a')])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P1 - 1, P1 + 1.6), '#aaa2b4', 0.85))
    for g in range(-600, 700, 180):
        x = sol_x(g, P1)
        out.append(path(rpoly([(x - 0.6, P1 + 2), (x - 0.6, 1062), (x + 0.6, 1062), (x + 0.6, P1 + 2)], 0.3),
                        '#25203a', 0.3))
    return ''.join(out)


@element('dessous', -15.4, 'fixe')
def dessous(doc):
    """Sous le mur de la terrasse : en combat, c'est sous les cartes des héros (y > 985) ; donc simple et sombre, la
    mer de nuages dans l'ombre du sommet, sans détail (l'accueil, qui la montre, garde un bas calme)."""
    out = [path('M-10 1062H600V1104H-10Z', doc.lin(0, 1062, 0, 1100, [(0, '#3a3454'), (1, '#2a2642')]))]
    pts = [(-10, 1104), (-10, 1068)]
    x, i = -10, 0
    while x < 600:
        x += 30 + 10 * math.sin(i * 1.9)
        pts.append((x, 1068 - 3 - 2 * math.sin(i * 2.3)))
        i += 1
    pts.append((600, 1104))
    out.append(path(sm(pts, sharp=(0, 1, len(pts) - 1), t=0.7), doc.lin(0, 1062, 0, 1100, [(0, '#4a4466'),
                                                                                           (1, '#2e2a48')])))
    out.append(path('M-10 1060H600V1066H-10Z', '#1e1a30', 0.5))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- premier plan
@element('rocher-gauche', 1300, 'morceau', box=(0, 1016, 84, 84))
def rocher_g(doc):
    s = sm([(-12, 1104), (-12, 1046), (8, 1038), (30, 1040), (50, 1052), (66, 1070), (78, 1092), (80, 1104)],
           sharp=(0, 7), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(30, 1044), (50, 1054), (64, 1072), (52, 1080), (36, 1062)], t=0.9), ROC['light'], 0.55))
    # une touffe de pin posée sur le rocher
    out.append(vol(doc, tige([(26, 1041), (30, 1032), (38, 1026)], [2.0, 1.6, 1.0]), BOIS, r=0.5, c=0.6, ink=INK,
                   iw=0.7))
    out.append(vol(doc, lobes_shape(22, 52, 1028, [(48, 1026, 4), (40, 1022, 6), (30, 1023, 5)], sag=1), PIN,
                   r=1.0, c=1.4, ink=INK, iw=0.8))
    return ''.join(out)


@element('rocher-droite', 1300, 'morceau', box=(522, 1028, 68, 72))
def rocher_d(doc):
    s = sm([(524, 1104), (530, 1080), (544, 1058), (562, 1042), (584, 1036), (604, 1040), (604, 1104)],
           sharp=(0, 6), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(566, 1046), (590, 1040), (600, 1056), (584, 1064)], t=0.9), ROC['light'], 0.5))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les corbeaux
# La touche vivante (comme les dragons de Kael) : trois grands corbeaux lointains, dans la couleur de la brume du
# ciel en plus foncé ; plus loin = plus petit, plus clair, plus lent. Ils traversent le ciel derrière le temple (un
# « morceau » remet le temple devant eux), jamais sur la terrasse. Chacun est une particule seule qui vit une période
# entière : il naît caché (hors de l'image ou derrière le temple) et finit caché ; ses ailes battent (12 images).
CORBEAUX = [
    # id, y, échelle, x de départ, x d'arrivée, montée (px/s), couleur, opacité, profondeur
    ('corbeau1', 432, 0.72, -50, 640, -0.4, '#26244a', 0.88, -29.75),     # le plus proche : de bord à bord, avec le vent
    ('corbeau2', 522, 0.42, 300, 640, -1.0, '#3a3462', 0.72, -29.74),     # sort de derrière le temple, file à droite
    ('corbeau3', 468, 0.28, 640, 300, 0.0, '#4a4272', 0.6, -29.73),       # le plus loin : rentre derrière le temple
]
CORBEAU_N, CORBEAU_MS = 12, 160                     # un battement d'ailes = 1,92 s
CORBEAU_BOITE = (-46, -58, 84, 116)                 # la silhouette (repère local, tête à droite) : x, y, w, h


def aile_corbeau(ph, near=True):
    """Une aile de corbeau (repère local, tête à droite) : le bord d'attaque jusqu'au poignet, les grandes rémiges
    écartées en doigts au bout, le bord de fuite jusqu'au dos. ph : le battement (0 = en haut, 0,5 = en bas)."""
    a = 2 * math.pi * ph
    f = 0.15 + 0.85 * math.cos(a)                 # 1 : en haut, −0,7 : en bas
    sx = 0.85 + 0.15 * abs(f)
    S = (2, -2) if near else (6, -3)
    k = 1 if near else 0.86

    def P(dx, dy):
        return (S[0] + dx * sx * k, S[1] + dy * f * k)
    loc = [(0, 0), (-2, -16), (-6, -30),                                        # épaule → poignet
           (-9, -48), (-12, -43), (-15, -50), (-18, -44), (-22, -49), (-25, -42), (-29, -45), (-31, -37),   # rémiges
           (-30, -26), (-26, -14), (-19, -4), (-12, 0)]                         # bord de fuite → dos
    return [P(x, y) for x, y in loc]


def corbeau_corps(ph):
    """Le corps fuselé, la tête au gros bec, la queue en éventail (repère local), qui montent un peu au battement."""
    b = -1.0 * math.sin(2 * math.pi * ph)
    corps = sm([(-24, -1 + b), (-12, -5 + b), (2, -6 + b), (12, -5 + b), (18, -3 + b), (20, 1 + b), (12, 3 + b),
                (0, 4 + b), (-12, 3 + b), (-24, 2 + b)], sharp=(0, 9), t=0.85)
    tete = sm([(14, -5 + b), (20, -8 + b), (25, -6.5 + b), (34, -3.5 + b), (26, -1 + b), (21, 1 + b), (15, 1 + b)],
              sharp=(3,), t=0.85)
    queue = sm([(-22, -2 + b), (-36, -6 + b), (-40, -2 + b), (-41, 2 + b), (-37, 5 + b), (-22, 2 + b)],
               sharp=(1, 4), t=0.75)
    return [corps, tete, queue]


def corbeau_image(id_):
    _, y, k, x0, x1, vy, col, op, _ = next(d for d in CORBEAUX if d[0] == id_)
    sg = 1 if x1 > x0 else -1
    bx, by, bw, bh = CORBEAU_BOITE
    w, h = bw * k + 4, bh * k + 4

    def fn(doc, i, n):
        ph = i / n
        loin = mix(col, '#7a6a9c', 0.35)                   # l'aile lointaine, plus dans la brume
        ox = w / 2 - (bx + bw / 2) * k * sg
        oy = h / 2 - (by + bh / 2) * k
        out = ['<g transform="translate(%s %s) scale(%s %s)">' % (fm(ox), fm(oy), fm(k * sg), fm(k))]
        out.append(path(sm(aile_corbeau(ph, False), sharp=(0, 3, 5, 7, 9), t=0.6), loin, 0.9))
        out.extend(path(p_, col) for p_ in corbeau_corps(ph))
        out.append(path(sm(aile_corbeau(ph, True), sharp=(0, 3, 5, 7, 9), t=0.6), col))
        out.append('</g>')
        return '<g opacity="%g">%s</g>' % (op, ''.join(out))
    return fn, (round(w), round(h))


for _d in CORBEAUX:
    _fn, _t = corbeau_image(_d[0])
    _vx = (_d[4] - _d[3]) * 1000 / PERIODE
    element(_d[0], _d[8], 'particules', taille=_t, images=CORBEAU_N, ms=CORBEAU_MS, dessin=_fn,
            zone=(_d[3], _d[1], _d[3], _d[1]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_d[5], _d[5]),
            ondule=(0, PERIODE))


def devant(ids, box):
    """Un morceau du paysage remis devant les corbeaux : ces éléments seuls (sans le ciel), coupés à la boîte."""
    def fn(doc):
        x, y, w, h = box
        body = ''.join(e['fn'](doc) for e in sorted(ELEMS, key=lambda e: e['prof']) if e['id'] in ids)
        return '<g clip-path="%s">%s</g>' % (doc.clip('M%s %sH%sV%sH%sZ' % (x, y, x + w, y + h, x)), body)
    return fn


DEVANT_TEMPLE = (218, 392, 164, 176)       # le temple seul, jusqu'au haut du socle (le pont, dessous, reste intact)
element('devant-temple', -26.9, 'morceau', box=DEVANT_TEMPLE)(devant(('temple',), DEVANT_TEMPLE))


# ---------------------------------------------------------------------------------------------------- les pétales
PETALE_N = 16


def petale_image(doc, i, n):
    """Un pétale emporté par le vent (une image de sa vie) : il tourne sur lui-même, apparaît et s'efface."""
    t = i / (n - 1)
    op = min(1, t / 0.15, (1 - t) / 0.15)
    ang = i * 47
    flip = 0.45 + 0.55 * abs(math.cos(i * 0.9))
    s = sm([(-3.2, 0), (-1.2, -1.6), (1.8, -1.4), (3.2, -0.3), (2.0, 0.2), (3.0, 0.9), (1.4, 1.4), (-1.4, 1.3)],
           sharp=(0, 4), t=0.85)
    body = path(s, PETALE['base']) + path(sm([(-1.6, -0.6), (0.8, -1.1), (2.2, -0.4), (0.4, 0.1)], t=0.9),
                                          PETALE['light'], 0.8)
    return '<g opacity="%g" transform="translate(6 6) rotate(%d) scale(1 %s)">%s</g>' % (
        max(0, op) * 0.9, ang, fm(flip), body)


element('petales', -14, 'particules', taille=(12, 12), images=PETALE_N, dessin=petale_image, zone=(30, 470, 230, 650),
        nombre=6, vie=(7000, 9500), vx=(16, 26), vy=(-3, 4), ondule=(5, 2600))


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
# Côté héros : Eldra (mages-8, l'autre clan du vent) au fond, Venthys (dragon-vent) au milieu, Orin (mages-3) devant ;
# en face, les trois monstres du clan d'Orin (corbeau, tengu costaud, masque aux sorts), retournés vers la gauche.
PERSOS = [('mages-8', 'heros', 0), ('dragon-vent', 'heros', 2), ('mages-3', 'heros', 4),
          ('mon-orin-rapide', 'ennemis', 0), ('mon-orin-costaud', 'ennemis', 2), ('mon-orin-sorts', 'ennemis', 4)]


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
    # le fond entier pour le propriétaire (les dragons en vol)
    rendre([(scene(5200), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    planche.save(os.path.join(JEU, CLAN + '-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': CLAN, 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/%s.webp' % CLAN, 'planche': 'art/vecto/fonds/%s-anim.webp' % CLAN,
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("orin-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-%s.json' % CLAN), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print('  jeu : public/art/vecto/fonds/orin.webp %d Ko, orin-anim.webp %d Ko (%d × %d), %d calques' % (
        os.path.getsize(os.path.join(JEU, CLAN + '.webp')) // 1024,
        os.path.getsize(os.path.join(JEU, CLAN + '-anim.webp')) // 1024, planche.size[0], planche.size[1], len(meta)))
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
    # (le fond pixel est supprimé depuis la v0.65.0 : la comparaison ne se fait que s'il est encore là)
    pxf = os.path.join(ROOT, 'public', 'art', 'px', 'fonds', CLAN + '.webp')
    if os.path.exists(pxf):
        pix = Image.open(pxf).convert('RGBA')
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
