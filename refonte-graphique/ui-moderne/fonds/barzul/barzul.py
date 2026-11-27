# Le fond de combat du clan de BARZUL (eau), la crique des pirates, redessiné en VECTORIEL lisse et animé (27/11/2026,
# demande du propriétaire après le test validé du volcan de Kael : « les 7 autres fonds »). Même façon de faire et mêmes
# mesures que refonte-graphique/ui-moderne/fonds/kael/kael.py (le modèle) ; l'univers et la composition sont ceux du
# fond pixel (refonte-graphique/pixel/fonds/barzul/build.py), recadrés pour le vrai combat (le jeu agrandit le fond
# ×1,4 et n'en montre que x = 84 → 506 ; la plateforme commence à y = 800 ; sous y = 985, les cartes des héros).
#
# Ce qu'on voit, du fond vers le devant : le ciel de fin d'après-midi (bleu nuit du manteau de Barzul → lavande →
# pêche), le soleil doré en haut à droite (la seule lumière), des nuages ronds lavande bordés d'or ; la mer jusqu'à
# l'horizon (claire au loin, bleu-vert tout près), deux îles dans la brume ; à gauche le cap de grès doré coiffé
# d'herbe (deux palmiers, la bannière rouge du clan, un canon pointé vers le large), à son pied une grotte où brille le
# trésor et une petite plage (une chaloupe, un tonneau) ; à droite le NAVIRE de Barzul au mouillage (coque bleu nuit à
# préceintes d'or, sabords aux mantelets rouges, fenêtres et fanal de poupe, figure de proue d'or, trois mâts, voiles
# gonflées, le signe du clan sur la grand-voile, le pavillon rouge en haut) ; l'eau proche ; l'arène : le grand ponton
# de bois de la crique, d'un bord à l'autre, calme ; sa poutre de rive, l'eau sombre dessous ; deux pieux d'amarrage
# dans les coins du bas (un cordage à gauche, une mouette posée à droite).
# Ce qui bouge : la touche vivante du lointain (trois mouettes qui traversent le ciel à des distances différentes, et
# un voilier pirate lointain qui glisse sur l'horizon : il sort de derrière les voiles du navire et va se cacher
# derrière le cap), les reflets du soleil sur la mer, l'eau proche, le reflet de la coque, l'écume de la plage, le
# pavillon, la bannière, les palmes, l'éclat du trésor dans la grotte.
# Le signe du clan (inventé, comme le pixel) : « l'œil des mers », un œil en amande posé au-dessus de deux vagues.
#
#   BROUILLON=<dossier> python3 refonte-graphique/ui-moderne/fonds/barzul/barzul.py --fixe   # brouillon (composer)
#   python3 refonte-graphique/ui-moderne/fonds/barzul/barzul.py            # images du jeu + calques + test + contrôles
#   python3 refonte-graphique/ui-moderne/fonds/barzul/barzul.py --video    # en plus : anim.gif et anim.mp4
#
# Sorties : public/art/vecto/fonds/barzul.webp (fixe ×2), barzul-anim.webp (planche ×2), fond-barzul.json et meta.json
# (à côté de ce fichier ; meta.json est réuni avec les autres clans dans src/game/fond-vecto.ts par ../assemble_ts.py) ;
# pixel/sortie/ui/vecto/fond-barzul/ (fond.png, situation.png, comparaison.png, anim.gif, anim.mp4, STATUT.txt).

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
from atelier import sm, ribbon, bez, resample, sides, lock  # noqa: E402

BROUILLON = os.environ.get('BROUILLON', '/tmp/fonds-brouillon')
TMP = os.path.join(BROUILLON, 'vecto-fond-barzul')
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'fond-barzul')
JEU = os.path.join(ROOT, 'public', 'art', 'vecto', 'fonds')
RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu-lot.cjs')

# ------------------------------------------------------------------------------------------------ les mesures
W, H = 590, 1100
UP = 2                          # les images du jeu sont rendues ×2 (vectoriel : plus fin que le pixel)
HZ, P0, P1 = 652, 800, 1047      # HZ : l'horizon de la mer ; P0 = 800 : en combat, le rang du fond a ses pieds à 828
RANGS = (860, 934, 1007)
VISIBLE = {'court': 377, 'moyen': 148, 'long': 50}
PERIODE = 19200                 # toutes les boucles divisent cette période : l'aperçu boucle sans couture
                                # (19,2 s : les mouettes et le voilier lointain passent une fois par période)
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
# Reprises de Barzul et de son équipage vectoriels (manteau bleu roi, or, rouge de l'écharpe et des bandanas, cuir et
# bois bruns, toile écrue), mais plus sourdes et plus brumeuses que les personnages.
INK = '#1f1238'                 # le contour (le raisin de l'interface), seulement sur les plans proches
CIEL = [(0, '#151b3e'), (0.2, '#1c2754'), (0.4, '#2e3f72'), (0.56, '#4c5888'), (0.68, '#76769e'), (0.79, '#a68ca2'),
        (0.89, '#cfa49e'), (1, '#e9bd9c')]
NUAGE_HAUT = dict(base='#545a8a', light='#666a98', rim='#b8a0b4', sh='#43487a')     # les bancs hauts (ciel nuit)
NUAGE = dict(base='#86829f', light='#9a92ae', rim='#f2cca4', sh='#6c6c92')          # plus bas : lavande bordée d'or
NUAGE_BAS = dict(base='#b29aa8', light='#c4a8ae', rim='#f8dab0', sh='#9c8aa2')      # tout près de l'horizon
LOIN1 = dict(base='#a094b0', light='#ac9eb4', rim='#e6c4b0', sh='#9288aa')        # l'île la plus lointaine
LOIN2 = dict(base='#8c86a8', light='#9890ae', rim='#d8b8ae', sh='#7e7aa0')
MER = [(0, '#e2c8ae'), (0.06, '#bcbcb8'), (0.2, '#8eaab2'), (0.45, '#5e8ca4'), (0.75, '#3c6e92'), (1, '#2a5a84')]
GRES = dict(base='#a2735e', light='#c08c6c', rim='#e6be8c', sh='#7a5256')           # le grès doré du cap
HERBE = dict(base='#4e7a4a', light='#66904e', rim='#a8c272', sh='#37583e')
TRONC = dict(base='#7c5a46', light='#977052', rim='#c49a6c', sh='#57403c')
PALME = dict(base='#3f6c46', light='#58864c', rim='#9cba6a', sh='#2c4c3c')
SABLE = dict(base='#c8a684', light='#d8b890', rim='#f0d6aa', sh='#a68670')
BOIS = dict(base='#6c4632', light='#8a5c3c', rim='#c08a5a', sh='#4a3029')
COQUE = dict(base='#2c3e7c', light='#3c5494', rim='#7e9ccc', sh='#1e2a5c')           # le bleu du manteau du capitaine
OR = dict(base='#c4903c', light='#e2b45a', rim='#ffe2a0', sh='#8a5a2c')
ROUGE = dict(base='#a2343c', light='#bc4a42', rim='#e6785c', sh='#6c2032')
TOILE = dict(base='#d6c6ae', light='#e8dcc4', rim='#fff4de', sh='#a89a98')
FER = dict(base='#3e4562', light='#545e80', rim='#96a2c4', sh='#282d46')
SOL = dict(back='#72686a', front='#807268')                                         # le ponton : valeur moyenne
POTEAU = dict(base='#5e4a42', light='#76604e', rim='#a88a6c', sh='#40322e')          # pieux, poutres


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



def le_long(c, u):
    """Le point à la fraction u (0..1) d'une ligne échantillonnée régulièrement."""
    f = u * (len(c) - 1)
    k = min(len(c) - 2, int(f))
    t = f - k
    return (c[k][0] + (c[k + 1][0] - c[k][0]) * t, c[k][1] + (c[k + 1][1] - c[k][1]) * t)



def rond(cx, cy, r, stops, doc, ry=None):
    """Une tache douce (dégradé radial), jamais un rond au sol : lueurs, halos, reflets."""
    ry = r if ry is None else ry
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(cx), fm(cy), fm(r), fm(ry),
                                                                    doc.rad(cx, cy, r, stops, ry=ry))


def trait(pts, col, w, op=1.0):
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"%s/>' % (
        polyline_d(pts), col, fm(w), '' if op == 1 else ' opacity="%g"' % op)


def poutre(doc, a, b, w0, w1, m, ink=True, iw=0.7):
    """Un bois droit (mât, vergue, beaupré, pieu) de a à b, plus fin au bout b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    pts = [(a[0] + nx * w0 / 2, a[1] + ny * w0 / 2), (b[0] + nx * w1 / 2, b[1] + ny * w1 / 2),
           (b[0] - nx * w1 / 2, b[1] - ny * w1 / 2), (a[0] - nx * w0 / 2, a[1] - ny * w0 / 2)]
    return vol(doc, rpoly(pts, min(w0, w1) * 0.3), m, r=min(1.0, w1 * 0.3), c=min(1.2, w1 * 0.35),
               ink=INK if ink else None, iw=iw)


def signe_forme(cx, cy, k):
    """Le signe de Barzul, « l'œil des mers » : un œil en amande (paupières, iris) au-dessus de deux vagues qui
    s'enroulent. Aucune lettre. Une seule forme (règle pair-impair) : le blanc de l'œil est un creux."""
    def P(u, v):
        return (cx + u * k, cy + v * k)
    oeil = sm([P(-6.4, 0), P(-3.4, -2.9), P(0, -3.8), P(3.4, -2.9), P(6.4, 0), P(3.4, 2.9), P(0, 3.8), P(-3.4, 2.9)],
              sharp=(0, 4), t=0.9)
    creux = sm([P(-4.6, 0), P(-2.4, -2.0), P(0, -2.6), P(2.4, -2.0), P(4.6, 0), P(2.4, 2.0), P(0, 2.6), P(-2.4, 2.0)],
               sharp=(0, 4), t=0.9)
    s = oeil.hole(creux) + ellipse(cx + 0.3 * k, cy, 1.5 * k, 1.5 * k)
    for ox in (-3.3, 3.1):
        c = catmull([P(ox - 3.1, 7.4), P(ox - 1.4, 5.6), P(ox + 0.8, 5.2), P(ox + 2.2, 6.2), P(ox + 1.2, 7.4)], 4)
        n_ = len(c) - 1
        s = s + ribbon(c, [k * (0.25 + 1.0 * math.sin(math.pi * min(1, i / n_ * 1.15)) ** 0.7) for i in range(n_ + 1)])
    return s


def redessine(ids, box):
    """Un morceau du paysage remis par-dessus (ces éléments seuls, sans le ciel), coupé à la boîte : il cache ce qui
    passe derrière (le voilier lointain), ou il repasse devant ce qu'une boucle dessine (les reflets du soleil)."""
    def fn(doc):
        x, y, w, h = box
        body = ''.join(e['fn'](doc) for e in sorted(ELEMS, key=lambda e: e['prof']) if e['id'] in ids)
        return '<g clip-path="%s">%s</g>' % (doc.clip('M%s %sH%sV%sH%sZ' % (x, y, x + w, y + h, x)), body)
    return fn


# ---------------------------------------------------------------------------------------------------- le ciel
SOLEIL = (462, 398)          # vu sur tous les téléphones (le court montre le fond à partir de y = 351), à droite des pilules


@element('ciel', -29.9, 'fixe')
def ciel(doc):
    out = [path('M-20 -20H610V%dH-20Z' % (HZ + 6), doc.lin(0, 0, 0, HZ, CIEL))]
    # la lueur dorée de l'horizon, sous le soleil
    out.append(rond(430, HZ, 400, [(0, '#f6d2a2', 0.55), (0.45, '#e8b496', 0.2), (1, '#d0a098', 0)], doc, ry=170))
    # le soleil doré en haut à droite (la seule lumière), son halo
    sx, sy = SOLEIL
    out.append(rond(sx, sy, 130, [(0, '#ffe4ae', 0.36), (0.35, '#f2c09a', 0.15), (1, '#c8a0a8', 0)], doc))
    out.append('<circle cx="%d" cy="%d" r="22" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 6, sy - 6, 27, [(0, '#fff8e2'), (0.7, '#ffe6b0'), (1, '#f4c886')])))
    return ''.join(out)


@element('nuages', -29.5, 'fixe')
def nuages(doc):
    out = []
    # A : le grand banc en haut à gauche (le haut des téléphones longs : derrière la pause et la pilule)
    a2 = lobes_shape(-30, 260, 228, [(240, 218, 16), (204, 204, 26), (156, 192, 30), (104, 188, 32), (52, 192, 30),
                                     (4, 200, 28), (-30, 212, 20)], sag=4)
    out.append(vol(doc, a2, dict(NUAGE_HAUT, base='#484e80', light='#585c8c', sh='#3c4272'), r=2, c=3.5))
    a = lobes_shape(-30, 318, 318, [(296, 306, 16), (260, 290, 28), (214, 274, 36), (160, 264, 38), (104, 258, 40),
                                    (50, 262, 36), (2, 272, 34), (-30, 290, 26)], sag=6)
    out.append(vol(doc, a, NUAGE_HAUT, r=2.4, c=4))
    # B : en haut à droite
    b = lobes_shape(392, 620, 288, [(612, 276, 16), (578, 264, 22), (540, 258, 22), (500, 262, 20), (462, 268, 17),
                                    (420, 276, 13)], sag=3)
    out.append(vol(doc, b, NUAGE_HAUT, r=2.2, c=3))
    # C : un petit banc au-dessus du soleil, E : un petit à gauche, sous le banc A (lavande bordée d'or)
    c = lobes_shape(486, 620, 342, [(610, 334, 12), (580, 324, 16), (544, 322, 14), (512, 328, 11)], sag=2)
    out.append(vol(doc, c, NUAGE, r=1.8, c=2.6))
    e = lobes_shape(96, 226, 370, [(216, 364, 9), (188, 356, 13), (150, 352, 15), (114, 360, 11)], sag=2)
    out.append(vol(doc, e, NUAGE, r=1.8, c=2.6))
    # F : un long banc bas, posé sur l'horizon derrière les îles (la brume chaude du soir)
    f = lobes_shape(150, 620, 624, [(600, 612, 12), (560, 604, 16), (512, 606, 12), (470, 610, 10), (420, 608, 13),
                                    (370, 612, 9), (318, 610, 12), (262, 614, 9), (214, 612, 11), (170, 618, 7)], sag=1)
    out.append('<g opacity="0.7">%s</g>' % vol(doc, f, NUAGE_BAS, r=1.4, c=0))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
@element('iles', -29.2, 'fixe')
def iles(doc):
    out = []
    # la grande île lointaine à droite, derrière la poupe ; une petite, très loin, dans la trouée du milieu
    i1 = [(466, HZ + 2), (488, 638), (512, 624), (534, 612), (552, 606), (568, 610), (588, 620), (606, 634),
          (612, HZ + 2)]
    out.append(vol(doc, sm(i1, sharp=(0, len(i1) - 1), t=0.8), LOIN2, r=1.4, c=2))
    i2 = [(206, HZ + 2), (222, 645), (240, 638), (256, 634), (270, 637), (286, 645), (300, HZ + 2)]
    out.append(vol(doc, sm(i2, sharp=(0, len(i2) - 1), t=0.8), LOIN1, r=1.2, c=1.4))
    # la brume du pied des îles
    out.append(path('M-10 %dH600V%dH-10Z' % (HZ - 30, HZ + 2), doc.lin(0, HZ - 30, 0, HZ, [
        (0, '#e2c4ac', 0), (1, '#e6c8ae', 0.55)])))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- la mer
def mer_degrade(doc, dy=0):
    """Le dégradé de la mer (y du fond ; dy : décalage d'une tuile)."""
    return doc.lin(0, HZ - dy, 0, P0 - dy, MER)


@element('mer', -29.0, 'fixe')
def mer(doc):
    out = [path('M-10 %dH600V%dH-10Z' % (HZ, P0 + 4), mer_degrade(doc))]
    # la ligne claire de l'horizon, et la grande lueur du soleil sur l'eau (fixe)
    out.append(path('M-10 %dH600V%dH-10Z' % (HZ, HZ + 2.2), '#f6e2c6', 0.7))
    out.append(rond(SOLEIL[0], 690, 56, [(0, '#ffe4b0', 0.4), (0.5, '#f0c8a0', 0.14), (1, '#d8b0a0', 0)], doc, ry=48))
    # quelques rides calmes, éparses (plus longues tout près) : pas des rayures, des touches posées au hasard
    r = rng('barzul-rides')
    for k in range(30):
        u = r() ** 0.8
        y = HZ + 8 + u * (764 - HZ - 8)
        x = r(-10, 600)
        lw = 6 + 26 * u * r(0.6, 1.2)
        th = 0.7 + 1.6 * u
        c = [(x - lw / 2, y), (x, y - th * 0.15), (x + lw / 2, y)]
        col = mix('#f2e2cc', '#9cc0cc', min(1, u * 1.6))
        out.append(path(ribbon(resample(c, 6), [th * math.sin(math.pi * i / 6) ** 0.7 for i in range(7)]), col,
                        0.35 - 0.12 * u))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le navire
WL = 768                        # la ligne de flottaison du navire (l'eau proche commence à 770)
COQUE_PTS = [(286, 706), (298, 703), (336, 707), (340, 717), (422, 719), (426, 707), (462, 705), (466, 693),
             (498, 689), (506, 698), (504, 722), (497, 746), (486, WL + 6), (330, WL + 6), (306, 756), (292, 734)]
COQUE_SHARP = (0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13)
# les mâts : (x, pied, tête) ; les voiles établies : (mât, haut, bas, demi-largeur en haut, en bas) ;
# les vergues aux voiles serrées : (mât, y, demi-largeur)
MATS = [(340, 717, 520), (404, 719, 462), (462, 705, 556)]
VOILES = [(340, 606, 698, 34, 40), (340, 549, 598, 27, 31), (404, 594, 704, 43, 48), (404, 525, 586, 33, 38),
          (462, 586, 638, 23, 27)]
SERREES = [(340, 528, 20), (404, 488, 24), (462, 568, 18)]
BEAUPRE = ((298, 704), (244, 683))
NDX = -18                       # le navire est dessiné dans ses coordonnées d'origine puis décalé à gauche (toute la
                                # poupe et son fanal restent dans ce que montre le combat, x ≤ 506)
SABORDS = (352, 374, 396, 418, 440)


def preceinte(k):
    """Les deux préceintes d'or (lignes douces le long de la coque)."""
    if k == 0:
        return catmull([(286, 720), (330, 724), (400, 726), (460, 723), (506, 714)])
    return catmull([(292, 744), (334, 748), (400, 750), (460, 747), (500, 738)])


def voile_forme(mx, y0, y1, h0, h1):
    bel = (y1 - y0) * 0.06
    pts = [(mx - h0, y0), (mx + h0, y0), (mx + h0 + (h1 - h0) * 0.55 + 2, (y0 + y1) / 2), (mx + h1, y1 - bel),
           (mx + h1 * 0.4, y1 + bel * 0.4), (mx - h1 * 0.4, y1 + bel * 0.4), (mx - h1, y1 - bel),
           (mx - h0 - (h1 - h0) * 0.55 - 2, (y0 + y1) / 2)]
    return sm(pts, sharp=(0, 1, 3, 6), t=0.75)


def voile(doc, mx, y0, y1, h0, h1, signe=False):
    """Une voile établie, gonflée par le vent du large (la droite) : la toile éclairée à droite, son ventre dans
    l'ombre douce en bas à gauche, l'ombre de la vergue sous la vergue."""
    s = voile_forme(mx, y0, y1, h0, h1)
    g = doc.lin(mx + h1, y0, mx - h1, y1, [(0, TOILE['light']), (0.5, TOILE['base']), (1, TOILE['sh'])])
    out = [vol(doc, s, TOILE, grad=g, r=1.4, c=2.6, ink=INK, iw=0.7)]
    inner = [path('M%s %sH%sV%sH%sZ' % (fm(mx - h1 - 6), fm(y0), fm(mx + h1 + 6), fm(y0 + 5), fm(mx - h1 - 6)),
                  doc.lin(0, y0, 0, y0 + 5, [(0, TOILE['sh'], 0.7), (1, TOILE['sh'], 0)]))]
    inner.append(rond(mx - h1 * 0.45, y1 - (y1 - y0) * 0.22, h1 * 0.7, [(0, TOILE['sh'], 0.42), (1, TOILE['sh'], 0)],
                      doc, ry=(y1 - y0) * 0.36))
    inner.append(rond(mx + h1 * 0.35, y0 + (y1 - y0) * 0.42, h1 * 0.55, [(0, '#fff8e8', 0.35), (1, '#fff8e8', 0)],
                      doc, ry=(y1 - y0) * 0.3))
    if signe:
        inner.append(path(signe_forme(mx + 2, (y0 + y1) / 2 + 2, 2.7), ROUGE['base'], 0.85, extra=EO))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


def serree(doc, mx, y, hw):
    """Une vergue et sa voile serrée : un rouleau de toile bosselé sous le bois."""
    pts = [(mx - hw, y + 1)]
    n = int(hw / 4.5)
    for j in range(n + 1):
        x = mx - hw + 2 * hw * j / n
        pts.append((x, y + 4.2 + 0.9 * math.sin(j * 1.9)))
    pts.append((mx + hw, y + 1))
    roll = sm(pts, sharp=(0, len(pts) - 1), t=0.8)
    out = [vol(doc, roll, dict(TOILE, base='#c4b4a0', light='#d6c8b2'), r=0.8, c=1.4, ink=INK, iw=0.6)]
    out.append(poutre(doc, (mx - hw - 2, y), (mx + hw + 2, y), 2.4, 2.4, BOIS, iw=0.6))
    return ''.join(out)


def navire_formes():
    """La silhouette pleine du navire (coque, voiles, mâts, vergues, fanal), dans ses coordonnées d'origine : elle
    sert de masque aux reflets du soleil (on ne les voit que sur l'eau libre)."""
    out = [sm(COQUE_PTS, sharp=COQUE_SHARP, t=0.7).d()]
    out += [voile_forme(mx, y0, y1, h0, h1).d() for mx, y0, y1, h0, h1 in VOILES]
    for x, pied, tete in MATS:
        out.append('M%s %sH%sV%sH%sZ' % (fm(x - 3), tete, fm(x + 3), pied, fm(x - 3)))
    for mx, y, hw in SERREES:
        out.append('M%s %sH%sV%sH%sZ' % (fm(mx - hw - 3), y - 3, fm(mx + hw + 3), y + 8, fm(mx - hw - 3)))
    out.append('M494 664H507V692H494Z')
    return out


@element('navire', -22, 'fixe')
def navire(doc):
    return '<g transform="translate(%d 0)">%s</g>' % (NDX, navire_brut(doc))


def navire_brut(doc):
    out = []
    # le gréement (peu de cordages, tendus : pas une grille), derrière les voiles
    lignes = [[(340, 524), BEAUPRE[1]], [(404, 468), (340, 552)], [(462, 560), (404, 592)], [(404, 468), (500, 690)],
              [(462, 560), (504, 694)], [(340, 540), (326, 708)], [(340, 540), (356, 716)], [(404, 480), (388, 720)],
              [(404, 480), (422, 716)], [(462, 572), (452, 706)], [(462, 572), (476, 694)]]
    for p_ in lignes:            # opaques (le morceau remis devant le voilier les redessine à l'identique)
        out.append(trait(p_, '#56465e', 0.75))
    out.append(poutre(doc, BEAUPRE[0], BEAUPRE[1], 3.6, 2.0, BOIS, iw=0.7))
    for x, pied, tete in MATS:
        out.append(poutre(doc, (x, pied), (x, tete), 4.4, 2.6, BOIS, iw=0.7))
        out.append('<circle cx="%s" cy="%s" r="2" fill="%s" stroke="%s" stroke-width="0.8"/>' % (
            x, tete - 1, OR['light'], INK))
    for mx, y, hw in SERREES:
        out.append(serree(doc, mx, y, hw))
    for k, (mx, y0, y1, h0, h1) in enumerate(VOILES):
        out.append(voile(doc, mx, y0, y1, h0, h1, signe=(k == 2)))
        out.append(poutre(doc, (mx - h0 - 3, y0), (mx + h0 + 3, y0), 2.6, 2.6, BOIS, iw=0.6))
    # la coque
    s = sm(COQUE_PTS, sharp=COQUE_SHARP, t=0.7)
    g = doc.lin(505, 690, 300, 770, [(0, COQUE['light']), (0.5, COQUE['base']), (1, COQUE['sh'])])
    out.append(vol(doc, s, COQUE, grad=g, r=1.6, c=2.8, ink=INK, iw=1.0))
    cl = doc.clip(s.d())
    inner = []
    # les œuvres vives (bois sombre) sous la préceinte basse
    lo = preceinte(1)
    inner.append(path(polyline_d(lo) + 'L510 800L280 800Z', doc.lin(0, 744, 0, 772, [(0, '#4a3434'), (1, '#33262e')])))
    for k in (0, 1):
        c = preceinte(k)
        inner.append(path(ribbon(c, [3.2] * len(c), sharp_ends=False), OR['base']))
        inner.append(path(ribbon([(x, y - 0.9) for x, y in c], [1.0] * len(c), sharp_ends=False), OR['rim'], 0.7))
    # le liseré d'or du plat-bord (il suit les marches du gaillard et de la dunette)
    inner.append('<path d="%s" fill="%s" mask="%s"/>' % (s.d(), OR['base'], doc.minus(s.d(), 0, 2.6)))
    inner.append('<path d="%s" fill="%s" opacity="0.8" mask="%s"/>' % (s.d(), OR['rim'], doc.minus(s.d(), 0, 0.9)))
    # les sabords entre les préceintes : l'ouverture sombre, son cadre d'or, le mantelet rouge relevé
    for x in SABORDS:
        y = 731 + (x - 400) ** 2 * 0.00012
        inner.append(vol(doc, rpoly([(x - 3.6, y - 3.4), (x + 3.6, y - 3.4), (x + 3.6, y + 3.6), (x - 3.6, y + 3.6)],
                                    0.8), OR, r=0.5, c=0.6))
        inner.append(path(rpoly([(x - 2.4, y - 2.2), (x + 2.4, y - 2.2), (x + 2.4, y + 2.6), (x - 2.4, y + 2.6)], 0.5),
                          '#141026'))
        inner.append(vol(doc, rpoly([(x - 3.4, y - 4.2), (x + 3.4, y - 4.2), (x + 4.2, y - 8.4), (x - 2.6, y - 8.6)],
                                    0.6), ROUGE, r=0.5, c=0.6))
    # les fenêtres de la dunette (lumière chaude) et le fond de la proue dans l'ombre (elle tourne)
    for wx in (474, 488):
        inner.append(vol(doc, rpoly([(wx - 4.6, 700), (wx + 4.6, 700), (wx + 4.6, 711), (wx - 4.6, 711)], 1), OR,
                         r=0.5, c=0.6))
        inner.append(path(rpoly([(wx - 3.2, 701.6), (wx + 3.2, 701.6), (wx + 3.2, 709.6), (wx - 3.2, 709.6)], 0.8),
                          doc.lin(wx + 3, 702, wx - 3, 710, [(0, '#fff0b8'), (1, '#f0b05a')])))
    inner.append(rond(286, 740, 26, [(0, COQUE['sh'], 0.6), (1, COQUE['sh'], 0)], doc, ry=40))
    out.append('<g clip-path="%s">%s</g>' % (cl, ''.join(inner)))
    # la figure de proue : une volute d'or sous le beaupré
    c = catmull([(298, 712), (290, 714), (285, 720), (288, 726), (293, 725), (292, 721)], 4)
    out.append(vol(doc, ribbon(c, [2.6 - 1.8 * i / (len(c) - 1) for i in range(len(c))], sharp_ends=False), OR,
                   r=0.6, c=0.8, ink=INK, iw=0.6))
    # le câble de l'ancre qui plonge de l'écubier
    out.append(trait([(302, 728), (299, 748), (298, WL + 4)], '#3a2a2c', 1.4))
    out.append('<circle cx="302" cy="728" r="1.8" fill="%s" stroke="%s" stroke-width="0.6"/>' % (OR['base'], INK))
    # le grand fanal de poupe (cage d'or, verre chaud)
    out.append(poutre(doc, (500, 690), (500, 680), 1.6, 1.4, OR, iw=0.5))
    out.append(rond(500, 675, 10, [(0, '#ffd890', 0.45), (1, '#ffb860', 0)], doc))
    out.append(vol(doc, rpoly([(496.6, 672), (503.4, 672), (502.6, 680), (497.4, 680)], 1.2),
                   dict(base='#ffd27a', light='#fff0b8', rim='#fff8e0', sh='#d0903c'), r=0.6, c=0.8, ink=INK, iw=0.6))
    out.append(vol(doc, rpoly([(495.6, 670), (504.4, 670), (503, 667), (497, 667)], 0.8), OR, r=0.4, c=0.5,
                   ink=INK, iw=0.5))
    return ''.join(out)


def pavillon(doc, ph):
    """Le pavillon rouge au signe d'or tout en haut du grand mât : il flotte vers la gauche (le vent vient du large)."""
    x, top = 404 + NDX, MATS[1][2]
    a = 2 * math.pi * ph
    out = [poutre(doc, (x, top + 2), (x, top - 16), 2.0, 1.4, BOIS, iw=0.5)]
    out.append('<circle cx="%s" cy="%s" r="1.7" fill="%s" stroke="%s" stroke-width="0.6"/>' % (
        x, top - 17, OR['light'], INK))
    L, h_ = 25, 13
    y0 = top - 15

    def P(u, v):           # u : 0 (au mât) → 1 (au bout) ; v : 0 (en haut) → 1 (en bas)
        o = 2.0 * u * math.sin(a - u * 4.2) + 0.6 * u * math.sin(2 * a - u * 7)
        return (x - 1 - u * L, y0 + v * h_ + o + u * 1.5 + 0.5 * v * u * math.sin(a - u * 3))
    pts = [P(0, 0)] + [P(u, 0) for u in (0.33, 0.66)] + [P(1.02, 0), P(0.86, 0.5), P(1.02, 1)] + \
        [P(u, 1) for u in (0.66, 0.33)] + [P(0, 1)]
    s = sm(pts, sharp=(0, 3, 4, 5, 8), t=0.6)
    out.append(vol(doc, s, ROUGE, r=1.0, c=1.6, ink=INK, iw=0.7))
    sx, sy = P(0.42, 0.5)
    out.append(path(signe_forme(sx, sy - 1, 0.9), OR['light'], extra=EO))
    return ''.join(out)


element('pavillon', -16, 'boucle', box=(372 + NDX, 438, 38, 30), n=12, ms=200)(pavillon)


# ---------------------------------------------------------------------------------------------------- le cap
CAP_HAUT = [(-14, 566), (20, 560), (58, 556), (98, 558), (128, 562), (148, 568)]
CAP_FACE = [(164, 586), (172, 616), (176, 650), (174, 684), (184, 714), (198, 742), (212, 770)]


def cap_y(x):
    return interp(CAP_HAUT, x)


def cap_forme():
    pts = [(-14, 790)] + CAP_HAUT + CAP_FACE + [(214, 790)]
    return sm(pts, sharp=(0, 1, len(pts) - 1), t=0.75)


CORN_CAP = [[(84, 628), (116, 625), (148, 628), (170, 636)], [(26, 700), (66, 697), (106, 701), (138, 709)]]
TOUFFES = [(112, 625, 1.0), (134, 626, 0.7), (60, 697, 0.9)]
GROTTE = [(160, 768), (161, 750), (168, 738), (179, 734), (190, 740), (196, 754), (198, 768)]


@element('cap', -20, 'fixe')
def cap(doc):
    out = []
    forme = cap_forme()
    g = doc.lin(200, 560, 0, 760, [(0, GRES['light']), (0.45, GRES['base']), (1, GRES['sh'])])
    out.append(vol(doc, forme, GRES, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0))
    inner = []
    # la face de droite, tournée vers le soleil : un grand pan plus clair ; quelques grands blocs (pas des rayures)
    inner.append(path(sm([(130, 572), (156, 572), (170, 604), (174, 650), (172, 690), (186, 726), (204, 770),
                          (170, 770), (150, 700), (140, 630)], t=0.8), GRES['light'], 0.6))
    for pts, op in (([(20, 600), (70, 596), (92, 630), (60, 656), (14, 650)], 0.18),
                    ([(70, 676), (128, 668), (140, 712), (96, 730), (60, 716)], 0.16),
                    ([(-14, 700), (30, 692), (50, 740), (-14, 760)], 0.2)):
        inner.append(path(sm(pts, t=0.85), GRES['sh'], op))
    for pts, ws in (([(104, 590), (98, 626), (106, 660)], [0.3, 1.6, 2.2, 2.4, 2.0, 1.4, 0.3]),
                    ([(40, 660), (48, 700), (40, 740)], [0.3, 1.4, 2.0, 2.2, 1.8, 1.2, 0.3]),
                    ([(146, 612), (140, 646)], [0.3, 1.2, 1.6, 1.4, 1.0, 0.6, 0.2])):
        inner.append(path(ribbon(resample(pts, 6), ws), GRES['sh'], 0.65))
    # deux corniches : un dessus éclairé, une ombre douce dessous (de grandes marches, pas des rayures)
    for pts in CORN_CAP:
        c = resample(catmull(pts), 16)
        n_ = len(c) - 1
        wl = [0.6 + 5 * math.sin(math.pi * i / n_) ** 0.6 for i in range(n_ + 1)]
        inner.append(path(ribbon([(x, y + 3.4) for x, y in c], wl), GRES['sh'], 0.4))
        inner.append(path(ribbon(c, [w * 0.36 for w in wl]), GRES['rim'], 0.4))
    # la lumière du soir sur le haut du cap
    inner.append(path('M-20 556H220V620H-20Z', doc.lin(0, 560, 0, 620, [(0, '#f4c890', 0.18), (1, '#f4c890', 0)])))
    # la grotte : une bouche sombre au pied de la face ; dedans, le trésor de l'équipage qui luit (coffre, pièces)
    gr = sm(GROTTE, sharp=(0, len(GROTTE) - 1), t=0.8)
    inner.append(path(gr, doc.lin(0, 734, 0, 768, [(0, '#1c1424'), (1, '#2a1e28')])))
    gin = doc.clip(gr.d())
    tre = [rond(180, 768, 24, [(0, '#ffcc6a', 0.55), (0.5, '#e09a40', 0.2), (1, '#c07a30', 0)], doc, ry=16)]
    tre.append(vol(doc, sm([(170, 770), (174, 762), (182, 758), (190, 762), (194, 770)], sharp=(0, 4), t=0.8), OR,
                   r=0.8, c=1.0))
    tre.append(vol(doc, rpoly([(164, 770), (164, 759), (176, 759), (176, 770)], 1.2), BOIS, r=0.7, c=0.9))
    tre.append(vol(doc, rpoly([(163, 760), (165, 754), (175, 754), (177, 760)], 1.6), BOIS, r=0.7, c=0.9))
    tre.append(path(rpoly([(163.5, 759.2), (176.5, 759.2), (176.5, 760.8), (163.5, 760.8)], 0.3), OR['base']))
    tre.append(path(rpoly([(169, 761), (171, 761), (171, 764), (169, 764)], 0.3), OR['light']))
    inner.append('<g clip-path="%s">%s</g>' % (gin, ''.join(tre)))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(forme.d()), ''.join(inner)))
    # l'herbe qui coiffe le cap (un tapis bosselé, qui déborde un peu sur la face éclairée)
    hp = [(-14, 572), (-14, 562)]
    for x, dy in ((-2, -6), (16, -9), (34, -7), (52, -11), (72, -8), (92, -10), (112, -7), (130, -9), (146, -4),
                  (154, 2)):
        hp.append((x, cap_y(x) + dy))
    hp += [(160, 584), (154, 580), (146, 574), (120, 568), (80, 566), (40, 568), (0, 572)]
    out.append(vol(doc, sm(hp, sharp=(0, 1), t=0.8), HERBE, r=1.8, c=2.4, ink=INK, iw=0.9))
    # des touffes d'herbe posées sur les corniches
    for x, y, k in TOUFFES:
        out.append(vol(doc, sm([(x - 9 * k, y + 1), (x - 7 * k, y - 4 * k), (x - 2 * k, y - 6 * k), (x + 3 * k, y - 5 * k),
                                (x + 8 * k, y - 3 * k), (x + 10 * k, y + 1)], sharp=(0, 5), t=0.85), HERBE, r=1.0,
                       c=1.2, ink=INK, iw=0.8))
    out.append(canon(doc))
    return ''.join(out)


def canon(doc):
    """Un canon de la batterie des pirates, sur son affût, pointé vers le large (la droite)."""
    x, y = 116, cap_y(116) - 3
    out = [vol(doc, rpoly([(x - 13, y + 1), (x - 11, y - 8), (x + 7, y - 9), (x + 9, y + 1)], 1.4), BOIS, r=0.8,
               c=1.2, ink=INK, iw=0.8)]
    out.append(vol(doc, rpoly([(x - 14, y - 12), (x + 4, y - 17), (x + 24, y - 21.5), (x + 25, y - 17.5),
                               (x + 5, y - 9), (x - 12, y - 6)], 2.2), FER, r=1.0, c=1.6, ink=INK, iw=0.8))
    out.append(vol(doc, rpoly([(x + 22, y - 23), (x + 26.5, y - 24), (x + 28, y - 17), (x + 23.5, y - 16)], 1),
                   FER, r=0.6, c=0.8, ink=INK, iw=0.7))
    # la roue (de profil, posée au sol) et deux boulets
    out.append(vol(doc, ellipse(x - 4, y - 2, 4.6, 4.6), BOIS, r=0.7, c=1.0, ink=INK, iw=0.7))
    for bx in (x - 20, x - 14):
        out.append(vol(doc, ellipse(bx, y - 2.6, 2.8, 2.8), FER, r=0.6, c=0.8, ink=INK, iw=0.6))
    return ''.join(out)


def palmier_tronc(base, top, w0=7.0, w1=4.2):
    c = resample(bez(base, (base[0] + (top[0] - base[0]) * 0.1, base[1] - (base[1] - top[1]) * 0.45),
                     (top[0] - (top[0] - base[0]) * 0.25, top[1] + 12), top), 14)
    return ribbon(c, [w0 + (w1 - w0) * i / 14 for i in range(15)], sharp_ends=False), c


PALMIERS = [((74, 560), (112, 468), 1.0, 0), ((28, 558), (8, 488), 0.86, 1)]


@element('troncs', -19.5, 'fixe')
def troncs(doc):
    out = []
    for base, top, k, _ in PALMIERS:
        t, c = palmier_tronc(base, top, 7 * k, 4.2 * k)
        out.append(vol(doc, t, TRONC, r=1.2, c=2.0, ink=INK, iw=0.9))
        # quelques anneaux à peine marqués près du haut (pas une rayure : trois touches)
        for u in (0.62, 0.76, 0.88):
            x, y = le_long(c, u)
            out.append(path(ellipse(x + 0.6, y, 2.6 * k, 0.8), TRONC['sh'], 0.35))
    return ''.join(out)


def couronne(k_, ph):
    """La couronne d'un palmier : des palmes arquées (une feuille effilée, retombante), qui se balancent doucement."""
    base, top, k, i_ = PALMIERS[k_]
    a = 2 * math.pi * ph

    def fn(doc):
        out = []
        cx, cy = top
        palmes = [(-160, 30, 1.0), (-120, 36, 0.95), (-60, 34, 0.9), (-20, 40, 1.0), (20, 38, 0.95), (155, 28, 0.9),
                  (95, 30, 0.85), (-95, 26, 0.7)]
        for j, (ang, L, kk) in enumerate(palmes):
            sw = 3.0 * math.sin(a + j * 0.8 + k_) * (0.6 + 0.4 * kk)
            th = math.radians(ang + sw)
            L *= k * 1.15
            dx, dy = math.cos(th), math.sin(th)
            droop = 0.55 * L
            p0 = (cx, cy)
            p3 = (cx + dx * L, cy + dy * L * 0.55 + droop * 0.8)
            p1 = (cx + dx * L * 0.35, cy + dy * L * 0.35 - 7 * k)
            p2 = (cx + dx * L * 0.8, cy + dy * L * 0.5 - 2 * k)
            m = PALME if dy > -0.2 or dx > 0 else dict(PALME, base='#36603e', light='#4a7646')
            # la palme : étroite au pied, large au milieu, pointue au bout
            c = resample(bez(p0, p1, p2, p3, 30), 14)
            ws = [9.5 * k * kk * math.sin(math.pi * min(1, (i / 14) ** 0.75)) ** 0.9 for i in range(15)]
            out.append(vol(doc, ribbon(c, ws), m, r=1.0, c=1.4, ink=INK, iw=0.8))
        # les noix, au cœur de la couronne
        for dx, dy in ((-2.4, 3), (2.2, 3.4), (0, 5.4)):
            out.append(vol(doc, ellipse(cx + dx * k, cy + dy * k, 2.6 * k, 2.6 * k), TRONC, r=0.6, c=0.8, ink=INK,
                           iw=0.6))
        return ''.join(out)
    return fn


def couronne_boucle(k_):
    def fn(doc, ph):
        return couronne(k_, ph)(doc)
    return fn


element('palme1', -19, 'boucle', box=(54, 430, 116, 86), n=12, ms=200)(couronne_boucle(0))
element('palme2', -19, 'boucle', box=(0, 450, 58, 80), n=12, ms=200)(couronne_boucle(1))

MAT_CLAN = (150, cap_y(150) + 3)
MAT_H = 50


def banniere(doc, ph):
    """La bannière rouge du clan, au bord du cap : la toile pend sous la traverse et ondule (vent de la droite)."""
    x, y = MAT_CLAN
    top = y - MAT_H + 5
    bois = dict(base='#5a3c34', light='#7a5440', rim='#b08a68', sh='#3a2828')
    out = [vol(doc, rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6),
               bois, r=0.7, c=0.8, ink=INK, iw=0.7)]
    out.append(vol(doc, rpoly([(x - 12, y - MAT_H + 2), (x + 12, y - MAT_H + 2), (x + 12, y - MAT_H + 5),
                               (x - 12, y - MAT_H + 5)], 1.2), bois, r=0.7, c=0.8, ink=INK, iw=0.7))
    out.append('<circle cx="%s" cy="%s" r="2.4" fill="%s" stroke="%s" stroke-width="1.1"/>' % (
        x, y - MAT_H - 1, OR['light'], INK))
    L, w_ = 32, 20
    a = 2 * math.pi * ph

    def P(u, v):
        sway = v ** 1.5 * (2.2 * math.sin(a + v * 2.2) - 1.4)
        return (x + u * w_ / 2 * (1 - 0.08 * v) + sway, top + v * L + 0.8 * math.sin(a + u * 1.5) * v)
    pts = [P(-1, 0), P(1, 0)]
    for v in (0.33, 0.66, 0.92):
        pts.append(P(1, v))
    pts += [P(1, 1.04), P(0.5, 0.9), P(0, 1.08), P(-0.5, 0.9), P(-1, 1.04)]
    for v in (0.92, 0.66, 0.33):
        pts.append(P(-1, v))
    s = sm(pts, sharp=(0, 1, 5, 7, 9), t=0.6)
    out.append(vol(doc, s, ROUGE, r=1.3, c=2.0, ink=INK, iw=0.9))
    sx, sy = P(0, 0.42)
    out.append(path(signe_forme(sx, sy, 1.15), OR['light'], extra=EO))
    out.append(vol(doc, rpoly([(x - 6, y + 3), (x - 5, y - 2), (x + 5, y - 2.5), (x + 7, y + 3)], 1.2), GRES,
                   r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


element('banniere', -16, 'boucle', box=(MAT_CLAN[0] - 18, MAT_CLAN[1] - MAT_H - 5, 36, MAT_H + 10), n=12,
        ms=200)(banniere)


def tresor(doc, ph):
    """Une pièce du trésor qui brille de temps en temps au fond de la grotte (une lueur et une petite étincelle)."""
    k = max(0.0, math.sin(2 * math.pi * ph)) ** 2
    out = []
    if k > 0.01:
        out.append(rond(185, 763, 7, [(0, '#fff4c8', 0.7 * k), (1, '#ffd070', 0)], doc))
        s = 4.5 * k + 0.5
        out.append(path(sm([(185, 763 - s), (185.7, 762.3), (185 + s * 0.8, 763), (185.7, 763.7), (185, 763 + s * 0.8),
                            (184.3, 763.7), (185 - s * 0.7, 763), (184.3, 762.3)], sharp=(0, 2, 4, 6), t=0.5),
                        '#fff8dc', min(1, 1.4 * k)))
    return ''.join(out)


element('tresor', -19, 'boucle', box=(176, 754, 18, 18), n=12, ms=400)(tresor)


# ---------------------------------------------------------------------------------------------------- la plage
PLAGE = [(140, 790), (140, 768), (176, 766), (204, 760), (232, 758), (256, 761), (272, 768), (276, 790)]


@element('plage', -19.8, 'fixe')
def plage(doc):
    out = []
    s = sm(PLAGE, sharp=(0, len(PLAGE) - 1), t=0.8)
    out.append(vol(doc, s, SABLE, grad=doc.lin(260, 756, 160, 772, [(0, SABLE['light']), (1, SABLE['base'])]),
                   r=1.2, c=1.6))
    # le sable mouillé au bord de l'eau
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), path('M120 764H290V790H120Z', doc.lin(
        0, 764, 0, 772, [(0, SABLE['sh'], 0), (1, '#8a7a7a', 0.7)]))))
    # quelques rochers ronds au pied du cap, un tonneau, la chaloupe tirée au sec
    for x, y, w_, h_ in ((206, 760, 12, 6), (150, 768, 14, 7), (262, 765, 8, 4)):
        out.append(vol(doc, sm([(x - w_ / 2, y + 1), (x - w_ * 0.3, y - h_), (x + w_ * 0.2, y - h_ * 1.05),
                                (x + w_ / 2, y + 1)], sharp=(0, 3), t=0.8), GRES, r=0.9, c=1.2, ink=INK, iw=0.7))
    tx, ty = 188, 763
    out.append(vol(doc, sm([(tx - 5, ty + 1), (tx - 5.8, ty - 6), (tx - 4.6, ty - 12), (tx + 4.6, ty - 12),
                            (tx + 5.8, ty - 6), (tx + 5, ty + 1)], sharp=(0, 2, 3, 5), t=0.8), BOIS, r=0.9, c=1.2,
                   ink=INK, iw=0.8))
    for yy in (ty - 9.5, ty - 2.5):
        out.append(path(rpoly([(tx - 5.6, yy - 0.8), (tx + 5.6, yy - 0.8), (tx + 5.6, yy + 0.8), (tx - 5.6, yy + 0.8)],
                              0.3), FER['light'], 0.8))
    out.append(chaloupe(doc, 234, 764))
    return ''.join(out)


def chaloupe(doc, x, y):
    """La chaloupe tirée au sec, un peu penchée : coque de bois, liseré rouge, une rame posée dedans."""
    s = sm([(x - 16, y - 9), (x + 14, y - 10), (x + 19, y - 13), (x + 15, y - 3), (x + 8, y + 1), (x - 10, y + 1),
            (x - 16, y - 4)], sharp=(0, 1, 2), t=0.8)
    out = [vol(doc, s, BOIS, r=1.0, c=1.6, ink=INK, iw=0.8)]
    out.append(path(ribbon(catmull([(x - 15.6, y - 8.4), (x, y - 9.4), (x + 14, y - 9.6), (x + 18.4, y - 12.4)], 4),
                           [1.4] * 13, sharp_ends=False), ROUGE['base'], 0.9))
    out.append(trait([(x - 6, y - 14), (x + 8, y - 8)], '#9a7656', 1.4))
    return ''.join(out)


def ecume(doc, ph):
    """L'écume qui va et vient sur le sable : un liseré clair qui monte, s'étale et se retire (une fois par boucle)."""
    a = 2 * math.pi * ph
    d = 1.6 + 1.6 * math.sin(a)
    out = []
    pts = [(146, 772), (176, 770.5 - d * 0.5), (206, 768 - d * 0.7), (236, 767 - d), (260, 769 - d * 0.6),
           (278, 773)]
    c = catmull(pts, 5)
    n_ = len(c) - 1
    out.append(path(ribbon(c, [(1.2 + 1.4 * (0.5 + 0.5 * math.sin(a + 1.2))) * math.sin(math.pi * i / n_) ** 0.5
                               for i in range(n_ + 1)]), '#f4f2e8', 0.75))
    c2 = catmull([(x, y + 2.4 + 0.6 * math.cos(a)) for x, y in pts], 5)
    out.append(path(ribbon(c2, [0.9 * math.sin(math.pi * i / n_) ** 0.5 for i in range(n_ + 1)]), '#dff0ee', 0.5))
    return ''.join(out)


element('ecume', -17.4, 'boucle', box=(140, 760, 144, 18), n=12, ms=200)(ecume)


# ---------------------------------------------------------------------------------------------------- les reflets
REFLETS_BOX = (408, HZ + 2, 104, WL - HZ - 4)


def reflets(doc, ph):
    """Les reflets du soleil sur la mer : de petites touches dorées qui s'allument et s'éteignent sous le soleil
    (masqués par la silhouette du navire : on ne les voit que sur l'eau libre)."""
    r = rng('barzul-reflets')
    out = []
    for k in range(26):
        u = r() ** 0.9
        y = HZ + 6 + u * (WL - HZ - 14)
        x = SOLEIL[0] + r(-1, 1) * (8 + 34 * u)
        p0 = r()
        k_ = max(0.0, math.sin(2 * math.pi * (ph + p0))) ** 1.5
        if k_ < 0.02:
            continue
        lw = (3 + 9 * u) * (0.6 + 0.4 * k_)
        out.append(path(ribbon(resample([(x - lw / 2, y), (x + lw / 2, y)], 4),
                               [0, 0.9 * (1 + u), 1.2 * (1 + u), 0.9 * (1 + u), 0]), '#fff2cc', 0.85 * k_))
    i = doc.uid('m')
    doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d"><rect width="%d" '
                    'height="%d" fill="#fff"/><g transform="translate(%d 0)">%s</g></mask>' % (
                        i, W, H, W, H, NDX, ''.join('<path d="%s" fill="#000"/>' % d for d in navire_formes())))
    return '<g mask="url(#%s)">%s</g>' % (i, ''.join(out))


element('reflets', -21, 'boucle', box=REFLETS_BOX, n=8, ms=300)(reflets)


# ---------------------------------------------------------------------------------------------------- l'eau proche
EAU = (0, 770, 590, P0 - 770)      # la boîte du défilé (x, y, w, h)
EAU_T = (192, P0 - 770)            # la tuile


def eau_tuile(doc):
    """La tuile de l'eau proche (192 × 30), qui se répète exactement en x : le même dégradé que la mer, des rides
    douces (claires dessus, une ombre dessous), posées irrégulièrement."""
    tw, th = EAU_T
    out = [path('M0 0H%dV%dH0Z' % (tw, th), mer_degrade(doc, 770))]
    rides = [(18, 6, 26), (74, 4, 18), (130, 8, 30), (172, 3, 16), (44, 15, 34), (108, 18, 24), (160, 16, 28),
             (10, 25, 30), (70, 27, 38), (138, 26, 26)]
    for x, y, lw in rides:
        for dx in (-tw, 0, tw):
            c = resample([(x + dx - lw / 2, y), (x + dx, y - 1), (x + dx + lw / 2, y)], 6)
            th_ = 0.9 + y / th * 1.6
            out.append(path(ribbon([(px, py + th_ * 0.9) for px, py in c],
                                   [th_ * math.sin(math.pi * i / 6) ** 0.7 for i in range(7)]), '#1c3e66', 0.3))
            out.append(path(ribbon(c, [th_ * 0.8 * math.sin(math.pi * i / 6) ** 0.7 for i in range(7)]), '#9cc4d0',
                            0.4))
    return ''.join(out)


def eau(doc, off):
    x, y, w, h = EAU
    tw, th = EAU_T
    out = []
    for k in range(-1, w // tw + 2):
        out.append('<g transform="translate(%s %s)">%s</g>' % (fm(x + k * tw + off), fm(y), eau_tuile(doc)))
    return '<g clip-path="%s">%s</g>' % (doc.clip('M%d %dH%dV%dH%dZ' % (x, y, x + w, y + h, x)), ''.join(out))


element('eau', -18, 'defile', box=EAU, tuile=EAU_T, vx=10.0, vy=0.0, dessin=eau, tuile_dessin=eau_tuile)


def reflet_coque(doc, ph):
    """Le reflet de la coque dans l'eau proche : une tache bleu nuit qui ondule, le fil d'or des préceintes."""
    a = 2 * math.pi * ph
    out = []
    top = 770
    pts = [(296 + NDX, top)]
    for i in range(13):
        x = 300 + NDX + i * 16
        pts.append((x + 1.5 * math.sin(a + i * 1.3), top + 13 - 5 * abs(i - 6) / 6 + 2.4 * math.sin(a * 1 + i * 0.9)))
    pts.append((500 + NDX, top))
    out.append(path(sm(pts, sharp=(0, len(pts) - 1), t=0.7), doc.lin(0, top, 0, top + 16, [
        (0, '#1e2a58', 0.7), (1, '#1e2a58', 0.1)])))
    c = [(304 + NDX + i * 16, top + 6 + 1.2 * math.sin(a + i * 1.1)) for i in range(12)]
    out.append(path(ribbon(resample(catmull(c, 3), 24), [1.4 * abs(math.sin(i * 0.9 + a)) for i in range(25)]),
                    OR['base'], 0.45))
    return ''.join(out)


element('reflet-coque', -17.6, 'boucle', box=(288 + NDX, 770, 220, 22), n=8, ms=300)(reflet_coque)


# ---------------------------------------------------------------------------------------------------- l'arène
def sol_x(g, y):
    """Le ponton en perspective : la coordonnée au sol g → x à l'écran (les joints filent vers le centre)."""
    k = (y - 600) / (P1 - 600)
    return 295 + g * k


@element('arene', -15.5, 'fixe')
def arene(doc):
    out = []
    # le dessus : un rectangle d'un bord à l'autre, une seule valeur moyenne (planches grises usées par le sel) qui
    # s'éclaire à peine vers l'avant et vers la droite (la lumière)
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, P0, 0, P1, [(0, SOL['back']), (1, SOL['front'])])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, 0, 590, 0, [(0, '#1e2040', 0.06),
                                                                              (1, '#fff0d8', 0.04)])))
    # les planches : de grandes planches couchées, joints à peine marqués, bouts décalés d'une planche à l'autre
    rows = [P0, 822, 848, 878, 914, 958, 1004, P1]
    joints = []
    for i in range(len(rows) - 1):
        ya, yb = rows[i], rows[i + 1]
        if i > 0:
            joints.append('M-10 %s H600' % fm(ya))
        step = 210
        off = (i % 2) * step / 2 + (i * 53) % 60
        g = -900 + off
        while g < 900:
            xa, xb = sol_x(g, ya), sol_x(g, yb)
            if -10 < min(xa, xb) and max(xa, xb) < 600:
                joints.append('M%s %s L%s %s' % (fm(xa), fm(ya + 1), fm(xb), fm(yb - 1)))
            g += step + 24 * math.sin(i * 3.1 + g)
    jd = ' '.join(joints)
    out.append('<path d="%s" fill="none" stroke="#fff4e6" stroke-width="1.2" opacity="0.05" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#2a2030" stroke-width="1" opacity="0.11"/>' % jd)
    # quelques planches un peu plus claires (le sel) ou plus sombres (très peu)
    for (g0, i, col, op) in ((-230, 1, '#fff6ea', 0.04), (40, 3, '#2a2030', 0.04), (290, 2, '#fff6ea', 0.035),
                             (-110, 4, '#2a2030', 0.035), (170, 5, '#fff6ea', 0.035), (-300, 6, '#2a2030', 0.03)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 170, ya), ya), (sol_x(g0 + 170, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le bord arrière : l'arête éclairée, et l'ombre du ponton sur l'eau juste derrière
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 1.6), '#a89a92', 0.7))
    # l'avant : l'arête éclairée, puis la poutre de rive
    out.append(path('M-10 %dH600V%dH-10Z' % (P1, 1064), doc.lin(0, P1, 0, 1064, [
        (0, '#5c4a46'), (0.6, '#4e3e3e'), (1, '#3e3238')])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P1 - 1, P1 + 1.6), '#b0a094', 0.85))
    for g in range(-600, 700, 160):
        x = sol_x(g, P1)
        out.append(path(rpoly([(x - 0.6, P1 + 2), (x + 0.6, P1 + 2), (x + 0.6, 1061), (x - 0.6, 1061)], 0.3),
                        '#2a2030', 0.35))
    return ''.join(out)


@element('dessous', -15.4, 'fixe')
def dessous(doc):
    """Sous la poutre de rive : en combat, c'est sous les cartes des héros (y > 985) ; donc simple et sombre, l'eau
    profonde et les têtes des pieux qui portent le ponton, sans détail perdu (l'accueil, qui la montre, garde un bas
    calme)."""
    out = [path('M-10 1062H600V1104H-10Z', doc.lin(0, 1062, 0, 1100, [(0, '#1c3050'), (0.4, '#16263e'),
                                                                     (1, '#101a30')]))]
    out.append(path('M-10 1062H600V1066H-10Z', '#0c1426', 0.6))
    for x in (64, 226, 386, 540):
        out.append(vol(doc, rpoly([(x - 6, 1062), (x + 6, 1062), (x + 6, 1104), (x - 6, 1104)], 1.5), dict(
            base='#3a2e32', light='#4a3a3a', rim='#6e5a54', sh='#2a2028'), r=1.0, c=1.4))
    return ''.join(out)


POSE = P0 + 9                   # le pied de ce qui est posé au fond du ponton (devant son arête, derrière le rang du fond)


@element('bord', -15.3, 'morceau', box=(0, 760, 590, POSE - 760 + 4))
def bord(doc):
    """Le fond du ponton : son arête, et ce qu'on y a posé : tonneaux et caisses dans les coins (vus à l'accueil),
    une bitte d'amarrage et un cordage enroulé (en combat, derrière le rang du fond)."""
    out = [path('M-10 %dH600V%dH-10Z' % (P0 - 2.4, P0 + 0.2), '#3a3036', 0.9)]
    # les tonneaux du coin gauche
    for x, y, s_ in ((16, POSE, 1.0), (38, POSE, 0.9), (26, POSE - 17, 0.85)):
        out.append(tonneau(doc, x, y, s_))
    # les caisses du coin droit
    for x, y, w_, h_ in ((560, POSE, 26, 20), (582, POSE, 20, 16), (566, POSE - 20, 18, 15)):
        b = rpoly([(x - w_ / 2, y), (x - w_ / 2, y - h_), (x + w_ / 2, y - h_), (x + w_ / 2, y)], 1.4)
        out.append(vol(doc, b, BOIS, r=1.0, c=1.4, ink=INK, iw=0.8))
        out.append(path(ribbon(resample([(x - w_ / 2 + 2, y - 2), (x + w_ / 2 - 2, y - h_ + 2)], 4),
                               [0.3, 1.2, 1.4, 1.2, 0.3]), BOIS['sh'], 0.6))
    # une bitte d'amarrage et un cordage enroulé
    for x in (130, 462):
        y = POSE - 2
        out.append(vol(doc, rpoly([(x - 4.4, y), (x - 4.4, y - 13), (x + 4.4, y - 13), (x + 4.4, y)], 1.6),
                       POTEAU, r=0.8, c=1.2, ink=INK, iw=0.8))
        out.append(vol(doc, rpoly([(x - 5.6, y - 12), (x + 5.6, y - 12), (x + 5.6, y - 15), (x - 5.6, y - 15)],
                                  1.2), POTEAU, r=0.6, c=0.8, ink=INK, iw=0.7))
    out.append(rouleau(doc, 148, POSE - 2))
    return ''.join(out)


def tonneau(doc, x, y, k=1.0):
    s = sm([(x - 7 * k, y), (x - 8 * k, y - 8 * k), (x - 6.5 * k, y - 17 * k), (x + 6.5 * k, y - 17 * k),
            (x + 8 * k, y - 8 * k), (x + 7 * k, y)], sharp=(0, 2, 3, 5), t=0.8)
    out = [vol(doc, s, BOIS, r=1.0, c=1.4, ink=INK, iw=0.8)]
    for yy in (y - 13.5 * k, y - 3.5 * k):
        out.append(path(rpoly([(x - 7.6 * k, yy - 0.9), (x + 7.6 * k, yy - 0.9), (x + 7.6 * k, yy + 0.9),
                               (x - 7.6 * k, yy + 0.9)], 0.3), FER['light'], 0.7))
    return ''.join(out)


def rouleau(doc, x, y):
    """Un cordage enroulé posé à plat (une galette bombée, vue de côté : jamais un rond au sol)."""
    corde = dict(base='#a08458', light='#bc9e6c', rim='#dcc08a', sh='#765e40')
    out = [vol(doc, sm([(x - 11, y), (x - 10, y - 4), (x - 4, y - 6.4), (x + 4, y - 6.4), (x + 10, y - 4), (x + 11, y)],
                       sharp=(0, 5), t=0.8), corde, r=0.9, c=1.2, ink=INK, iw=0.8)]
    out.append(path(ribbon(catmull([(x - 8, y - 3.4), (x, y - 4.6), (x + 8, y - 3.4)], 4), [0.3] + [0.9] * 7 + [0.3]),
                    corde['sh'], 0.7))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- premier plan
@element('pieu-gauche', 1300, 'morceau', box=(0, 1004, 84, 96))
def pieu_g(doc):
    """Le gros pieu d'amarrage du coin gauche, un cordage enroulé autour."""
    s = rpoly([(14, 1104), (12, 1016), (48, 1012), (50, 1104)], 4)
    out = [vol(doc, s, POTEAU, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(vol(doc, sm([(12, 1016), (20, 1008), (40, 1006), (50, 1012), (40, 1018), (20, 1019)], t=0.9),
                   dict(POTEAU, base='#7a6250', light='#8e7458'), r=1.0, c=0.8, ink=INK, iw=0.9))
    corde = dict(base='#a08458', light='#bc9e6c', rim='#dcc08a', sh='#765e40')
    for k, y in enumerate((1040, 1050, 1060)):
        out.append(vol(doc, sm([(9, y + 2), (12, y - 4), (30, y - 6 + k), (52, y - 4), (54, y + 2), (30, y + 5)],
                               t=0.9), corde, r=0.8, c=1.0, ink=INK, iw=0.8))
    out.append(vol(doc, ribbon(catmull([(54, 1062), (64, 1074), (60, 1090), (70, 1104)], 4), [3.4] * 13,
                               sharp_ends=False), corde, r=0.7, c=0.9, ink=INK, iw=0.8))
    return ''.join(out)


@element('pieu-droit', 1300, 'morceau', box=(524, 990, 66, 110))
def pieu_d(doc):
    """Le pieu du coin droit, une mouette posée dessus."""
    s = rpoly([(546, 1104), (544, 1026), (580, 1022), (584, 1104)], 4)
    out = [vol(doc, s, POTEAU, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(vol(doc, sm([(544, 1026), (552, 1018), (572, 1016), (582, 1022), (572, 1028), (552, 1029)], t=0.9),
                   dict(POTEAU, base='#7a6250', light='#8e7458'), r=1.0, c=0.8, ink=INK, iw=0.9))
    out.append(mouette_posee(doc, 562, 1021))
    return ''.join(out)


def mouette_posee(doc, x, y):
    blanc = dict(base='#e6e4ea', light='#f6f4f4', rim='#ffffff', sh='#b8b6c8')
    gris = dict(base='#8e90a8', light='#a2a4b8', rim='#c8c8d8', sh='#6c6e88')
    out = [trait([(x - 2, y), (x - 2, y - 5)], '#e8a050', 1.2), trait([(x + 2, y), (x + 2, y - 5)], '#e8a050', 1.2)]
    out.append(vol(doc, sm([(x - 12, y - 10), (x - 6, y - 15), (x + 4, y - 16), (x + 8, y - 12), (x + 4, y - 5),
                            (x - 4, y - 5)], t=0.9), blanc, r=0.9, c=1.4, ink=INK, iw=0.8))
    out.append(vol(doc, sm([(x - 14, y - 10), (x - 6, y - 14), (x + 3, y - 13), (x, y - 9), (x - 8, y - 8)],
                           sharp=(0,), t=0.9), gris, r=0.7, c=1.0, ink=INK, iw=0.7))
    out.append(vol(doc, ellipse(x + 7, y - 19, 4.2, 3.8), blanc, r=0.8, c=1.0, ink=INK, iw=0.8))
    out.append(vol(doc, rpoly([(x + 10.5, y - 19.6), (x + 16, y - 18.6), (x + 10.5, y - 17.4)], 0.4),
                   dict(base='#e8a83a', light='#f6c860', rim='#ffe6a0', sh='#b87a2a'), r=0.3, c=0.4, ink=INK, iw=0.5))
    out.append('<circle cx="%s" cy="%s" r="0.9" fill="#1a1426"/>' % (fm(x + 8.4), fm(y - 19.8)))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- la touche vivante
# Demande du propriétaire : « une touche vivante dans le ciel ou au loin ». Ici, la crique vit : trois mouettes qui
# traversent le ciel (plus loin = plus petite, plus pâle, dans la brume) en battant des ailes puis en planant, et la
# silhouette d'un voilier pirate lointain qui glisse sur l'horizon. Chacune est une particule seule qui vit une
# période entière : elle naît cachée (hors de l'image, ou derrière les voiles du navire) et finit cachée (hors de
# l'image, ou derrière le cap) ; jamais devant les personnages ni sur le ponton.
MOUETTES = [
    # id, y, échelle, x de départ, x d'arrivée, montée (px/s), couleur, gris des ailes, opacité, profondeur
    ('mouette1', 424, 0.8, -36, 630, -0.5, '#eceaf2', '#7c7e9c', 0.92, -29.75),
    ('mouette2', 396, 0.56, 626, -30, 0.3, '#d8d4e6', '#8a8aa8', 0.8, -29.74),
    ('mouette3', 444, 0.4, -24, 620, -0.3, '#c8c2d8', '#9a96b4', 0.66, -29.73),
]
MOUETTE_N, MOUETTE_MS = 12, 160                   # 8 images de battement, 4 de vol plané : 1,92 s
MOUETTE_BOITE = (-30, -22, 52, 36)                # la silhouette (repère local, tête à droite) : x, y, w, h


def mouette_vol(ph_i, col, gris):
    """Une mouette en vol (repère local, tête à droite), vue de côté : corps fuselé, tête ronde, bec, deux ailes en
    « M » (le coude, la main au bout gris). ph_i : image 0..11 (0..7 un battement, 8..11 le vol plané)."""
    if ph_i < 8:
        f = math.cos(2 * math.pi * ph_i / 8)      # 1 : en haut, −1 : en bas
    else:
        f = 0.42 + 0.06 * math.sin(math.pi * (ph_i - 8) / 4)
    out = []

    def aile(dx, dy, k, c_main, c_bout):
        S = (dx + 0, dy - 1)
        E = (dx - 4, dy - 1 - 10 * f * k)                         # le coude
        T = (dx - 19 * k, dy - 1 - 15 * f * k + 4 * (1 - abs(f)) * k)  # le bout de l'aile
        pts = [(S[0] + 3, S[1]), (E[0] + 1.5, E[1] - 1.2), (T[0], T[1]), (E[0] - 3, E[1] + 2.4), (S[0] - 5, S[1] + 1)]
        w = sm(pts, sharp=(2,), t=0.8)
        tip = sm([(T[0], T[1]), (T[0] + 6 * k, T[1] + 1.4 + 2.4 * f * k), (T[0] + 4 * k, T[1] + 4.2 * f * k + 1.2)],
                 sharp=(0,), t=0.7)
        return [path(w, c_main), path(tip, c_bout, 0.9)]
    out += aile(2, -1, 0.82, mix(col, gris, 0.35), mix(gris, col, 0.2))        # l'aile lointaine
    body = sm([(-11, 0.6), (-4, -2.4), (5, -2.2), (9, -1.2), (10, 0.8), (4, 2.4), (-5, 2.2)], sharp=(0,), t=0.9)
    out.append(path(body, col))
    out.append(path(ellipse(9, -1.4, 2.6, 2.4), col))
    out.append(path(rpoly([(11, -1.8), (14.4, -0.9), (11, -0.4)], 0.3), '#e8a840'))
    out.append(path(sm([(-11, 0.6), (-15, -1.2), (-15.4, 1.8)], sharp=(0, 1, 2), t=0.7), gris, 0.8))
    out += aile(0, 0, 1.0, col, gris)                                          # l'aile proche
    return out


def mouette_image(id_):
    _, y, k, x0, x1, vy, col, gris, op, _ = next(d for d in MOUETTES if d[0] == id_)
    sg = 1 if x1 > x0 else -1
    bx, by, bw, bh = MOUETTE_BOITE
    w, h = bw * k + 4, bh * k + 4

    def fn(doc, i, n):
        ox = w / 2 - (bx + bw / 2) * k * sg
        oy = h / 2 - (by + bh / 2) * k
        body = ''.join(mouette_vol(i, col, gris))
        return '<g opacity="%g"><g transform="translate(%s %s) scale(%s %s)">%s</g></g>' % (
            op, fm(ox), fm(oy), fm(k * sg), fm(k), body)
    return fn, (round(w), round(h))


for _d in MOUETTES:
    _fn, _t = mouette_image(_d[0])
    _vx = (_d[4] - _d[3]) * 1000 / PERIODE
    element(_d[0], _d[9], 'particules', taille=_t, images=MOUETTE_N, ms=MOUETTE_MS, dessin=_fn,
            zone=(_d[3], _d[1], _d[3], _d[1]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_d[5], _d[5]),
            ondule=(0, PERIODE))

# le voilier lointain : il naît derrière la misaine du navire, glisse vers la gauche sur l'horizon et se cache
# derrière le cap ; posé sur l'eau (sa flottaison un peu sous l'horizon), dans la brume.
VOILIER = dict(x0=310, x1=146, y=HZ - 12, taille=(44, 38))


def voilier_image(doc, i, n):
    """La silhouette d'un navire pirate lointain (proue à gauche) : coque sombre, deux mâts, voiles pâles dans la
    brume, un petit pavillon ; il tangue à peine (4 images)."""
    w, h = VOILIER['taille']
    a = 2 * math.pi * i / n
    t = 1.2 * math.sin(a)
    hull = '#4c4e7a'
    sail = '#b4aec6'
    sail_sh = '#9894b4'
    out = ['<g transform="rotate(%s %s %s) translate(0 %s)">' % (fm(t), fm(w / 2), fm(h - 6), fm(0.4 * math.sin(a)))]
    out.append(trait([(14, h - 10), (14, 6)], hull, 1.1))
    out.append(trait([(28, h - 10), (28, 9)], hull, 1.1))
    out.append(trait([(14, 8), (3, h - 11)], hull, 0.6, 0.8))
    for mx, y0, y1, hw in ((14, 9, 20, 6), (14, 21, 29.5, 7), (28, 11, 21, 5.2), (28, 22, 29.5, 6.2)):
        s = sm([(mx - hw, y0), (mx + hw, y0), (mx + hw + 1.2, (y0 + y1) / 2), (mx + hw, y1), (mx - hw, y1),
                (mx - hw - 0.6, (y0 + y1) / 2)], sharp=(0, 1, 3, 4), t=0.8)
        out.append(path(s, doc.lin(mx + hw, y0, mx - hw, y1, [(0, sail), (1, sail_sh)])))
    out.append(path(sm([(4, h - 11), (11, h - 9.6), (36, h - 9.6), (40, h - 13), (39, h - 7), (34, h - 4.6),
                        (10, h - 4.6)], sharp=(0, 3), t=0.8), hull))
    out.append(path(rpoly([(14, 2.4), (19, 3.4), (14, 5.6)], 0.3), '#3a3458'))
    out.append('</g>')
    return '<g opacity="0.85">%s</g>' % ''.join(out)


_vxv = (VOILIER['x1'] - VOILIER['x0']) * 1000 / PERIODE
element('voilier', -28.95, 'particules', taille=VOILIER['taille'], images=4, ms=1200, dessin=voilier_image,
        zone=(VOILIER['x0'], VOILIER['y'], VOILIER['x0'], VOILIER['y']), nombre=1, vie=(PERIODE, PERIODE),
        vx=(_vxv, _vxv), vy=(0, 0), ondule=(0, PERIODE))

# les morceaux remis devant le voilier : les voiles basses du navire (où il naît) et son étai, et le cap (où il se
# cache)
element('devant-voiles', -28.9, 'morceau', box=(232, 598, 140, 68))(redessine(('navire',), (232, 598, 140, 68)))
element('devant-cap', -28.9, 'morceau', box=(110, 600, 76, 66))(redessine(('cap',), (110, 600, 76, 66)))


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
        r = rng('barzul-' + e['id'])
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
# Côté héros : Kesha (demons-5) au fond, Elvyn le dragon d'eau (angels-6) au milieu, Barzul (demons-3) devant ; en
# face, les trois monstres du clan de Barzul (matelot, canonnier, tireuse), retournés vers la gauche.
PERSOS = [('demons-5', 'heros', 0), ('angels-6', 'heros', 2), ('demons-3', 'heros', 4),
          ('mon-barzul-rapide', 'ennemis', 0), ('mon-barzul-costaud', 'ennemis', 2), ('mon-barzul-tireur', 'ennemis', 4)]


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
                     graine='barzul-' + e['id'])
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
    Image.open(fixe).convert('RGB').save(os.path.join(JEU, 'barzul.webp'), quality=95, method=6)
    # le fond entier pour le propriétaire (les dragons en vol)
    rendre([(scene(5200), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    planche.save(os.path.join(JEU, 'barzul-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': 'barzul', 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/barzul.webp', 'planche': 'art/vecto/fonds/barzul-anim.webp',
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("barzul-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-barzul.json'), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print('  jeu : public/art/vecto/fonds/barzul.webp %d Ko, barzul-anim.webp %d Ko (%d × %d), %d calques' % (
        os.path.getsize(os.path.join(JEU, 'barzul.webp')) // 1024,
        os.path.getsize(os.path.join(JEU, 'barzul-anim.webp')) // 1024, planche.size[0], planche.size[1], len(meta)))
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
    base = Image.open(os.path.join(JEU, 'barzul.webp')).convert('RGBA')
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
    pix = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'barzul.webp')).convert('RGBA')
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
    if '--reprise' not in sys.argv:        # --reprise : garde les images déjà rendues (après une coupure)
        for f in os.listdir(d):
            os.unlink(os.path.join(d, f))
    jobs = [(scene(i * 1000 / fps, (x0, top, VUE_X[1] - x0, H - top)), os.path.join(d, 'f%04d.png' % i))
            for i in range(n)]
    # par paquets, avec de nouveaux essais : sur une machine chargée, un long rendu d'un seul tenant peut casser
    reste = [j for j in jobs if not os.path.exists(j[1])]
    for k in range(0, len(reste), 48):
        for essai in range(3):
            try:
                rendre(reste[k:k + 48], 720, hh)
                break
            except subprocess.CalledProcessError:
                if essai == 2:
                    raise
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
