# Le fond de combat du clan de KESHA (eau), le récif des abysses, redessiné en VECTORIEL lisse et animé (27/11/2026,
# demande du propriétaire après le test du volcan de Kael : « les 7 autres fonds »). Même façon de faire que
# ../kael/kael.py (le modèle) : dessin SVG → rendu par heros/rendu-lot.cjs, image fixe + calques animés d'une planche.
#
# Même composition que le fond pixel (refonte-graphique/pixel/fonds/kesha/build.py), recadrée pour le vrai combat
# (le jeu agrandit le fond ×1,4 et n'en montre que x = 84 → 506) : une image de 590 × 1100 pixels du fond, plateforme
# de P0 = 800 à P1 = 1047 ; rangs du combat 828 / 880 / 933, rangs de l'accueil 860 / 934 / 1007 ; sous y = 985 (le
# haut des cartes des héros) une bande sombre et simple. Style des héros et monstres vectoriels : grandes formes
# simples, dégradés doux, une seule lumière en haut à droite (la surface, très loin), un seul contour sombre seulement
# sur les plans proches, aucun flou SVG, aucun rayon de lumière. Le lointain se fond dans l'eau bleue (la brume).
#
# Ce qu'on voit, du fond vers le devant : l'eau profonde (plus claire et plus verte vers le haut), la grande lueur de
# la surface en haut à droite, des voiles d'eau claire ; en haut à gauche le dessous d'un surplomb de récif ; au loin,
# des tours de récif en champignon et des ombres de varech ; au milieu LA MÂCHOIRE de requin géante, à demi enfouie,
# ses dents tournées vers l'intérieur ; à gauche le massif de récif (son chapeau porte un jardin de coraux, la
# bannière et LA DENT fossile au signe du clan ; une grotte où luisent de petites bêtes) ; à droite l'ÉPAVE (château
# de poupe et sa fenêtre qui luit, trou dans la coque, mât brisé et pavillon, anémone sur la proue) ; deux grands
# varechs ; la rive de sable (rochers, étoile de mer, coquillages, deux évents) ; l'arène : un dallage englouti, à
# demi couvert de sable clair, d'un bord à l'autre, calme ; son flanc, la fosse sombre ; deux coraux dans les coins.
# Ce qui bouge : les varechs, l'anémone, la bannière et le pavillon, le signe de la dent, la grotte, la fenêtre, les
# bulles des évents, la neige des abysses ; et la touche vivante : deux raies manta et un serpent de mer, des ombres
# lointaines qui passent lentement dans l'eau (le serpent passe derrière la grande tour).
# Le signe du clan (inventé, comme le pixel) : un aileron de requin (l'encoche d'une vieille morsure) qui sort d'un
# croissant de vague.
#
#   BROUILLON=<dossier> python3 refonte-graphique/ui-moderne/fonds/kesha/kesha.py --fixe   # brouillon (composer)
#   BROUILLON=<dossier> python3 refonte-graphique/ui-moderne/fonds/kesha/kesha.py          # jeu + calques + contrôles
#   BROUILLON=<dossier> python3 refonte-graphique/ui-moderne/fonds/kesha/kesha.py --video  # en plus : anim.gif, anim.mp4
#
# Sorties : public/art/vecto/fonds/kesha.webp (fixe ×2), kesha-anim.webp (planche ×2), fond-kesha.json et meta.json
# (à côté de ce fichier ; meta.json est réuni aux autres clans par ../assemble_ts.py dans src/game/fond-vecto.ts) ;
# pixel/sortie/ui/vecto/fond-kesha/ (fond.png, situation.png, comparaison.png, anim.gif, anim.mp4, STATUT.txt).
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

CLAN = 'kesha'
BROUILLON = os.environ.get('BROUILLON', '/tmp/fonds-brouillon')
TMP = os.path.join(BROUILLON, 'vecto-fond-' + CLAN)
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'fond-' + CLAN)
JEU = os.path.join(ROOT, 'public', 'art', 'vecto', 'fonds')
RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu-lot.cjs')

# ------------------------------------------------------------------------------------------------ les mesures
W, H = 590, 1100
UP = 2                          # les images du jeu sont rendues ×2 (vectoriel : plus fin que le pixel)
HZ, P0, P1 = 776, 800, 1047      # HZ : le haut de la rive de sable ; P0 : le bord arrière de l'arène
RANGS = (860, 934, 1007)
VISIBLE = {'court': 377, 'moyen': 148, 'long': 50}
PERIODE = 19200                 # toutes les boucles divisent cette période : l'aperçu boucle sans couture
T_VUE = 15400                   # l'instant montré dans fond.png et situation.png (les trois ombres sont dans l'eau)
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
# Reprises de Kesha et de ses monstres vectoriels (peau gris-bleu, pagne bleu nuit, ivoire des dents, laiton ; crabe
# rouille et cuivre ; méduse bleue aux bras violets, cœur cyan), mais plus sourdes : le fond reste sous les personnages.
INK = '#141638'                 # le contour (bleu nuit), seulement sur les plans proches
EAU = [(0, '#2f6488'), (0.22, '#28557e'), (0.45, '#214572'), (0.64, '#1c3964'), (0.8, '#1b345e'), (1, '#203d67')]
VOILE = dict(base='#2d5c84', light='#36668c', rim='#4a7c9c', sh='#28527a')        # les voiles d'eau claire
LOIN1 = dict(base='#2a5079', light='#30577f', rim='#3f6889', sh='#264a73')        # les tours les plus lointaines
LOIN2 = dict(base='#264670', light='#2d4f78', rim='#3e6286', sh='#213f68')
SURPL = dict(base='#22406a', light='#2a4a74', rim='#3c5f86', sh='#1c3760')        # le surplomb d'en haut à gauche
ROCHE = dict(base='#38476a', light='#465a7e', rim='#7088a8', sh='#283454')         # le massif de récif (plan moyen)
ROC = dict(base='#323d5e', light='#425074', rim='#6c7e9e', sh='#232c48')            # les rochers proches
OS_ = dict(base='#9a9898', light='#b0aca4', rim='#cec8b8', sh='#6a6e82')            # l'ivoire de la mâchoire
DENT = dict(base='#c2bcae', light='#d6d0c0', rim='#eee8d8', sh='#8e8c8e')           # ses dents
FOSS = dict(base='#4a5272', light='#5e6888', rim='#a2aecc', sh='#343a58')           # la dent fossile (grise)
BOIS = dict(base='#463f4e', light='#574d5c', rim='#887a80', sh='#2e2a3c')           # le bois noyé de l'épave
CUIVRE = dict(base='#a85a40', light='#c07448', rim='#e0a070', sh='#743c40')         # corail branchu (le crabe)
ROSE = dict(base='#a05a80', light='#b8708e', rim='#dc9cae', sh='#6c3c66')           # corail cerveau
VIOL = dict(base='#5c4696', light='#7258ae', rim='#a08ad0', sh='#3e2e72')           # l'éventail, les éponges
JAUNE = dict(base='#b08a3c', light='#c8a24c', rim='#ecd088', sh='#7a5a2c')          # éponges en tubes (le laiton)
ALGUE = dict(base='#3e6a56', light='#4e7c60', rim='#80aa7c', sh='#2a4a44')          # herbes de mer
KELP = dict(base='#5a6a3c', light='#6e7e44', rim='#a2a862', sh='#3c4a32')           # varech brun olive
MARINE = dict(base='#283478', light='#34449a', rim='#5a6cc4', sh='#1a2152')         # le pagne de Kesha (bannières)
LAITON = '#d6b25a'
LUEUR = dict(c0='#e8fff8', c1='#9ef0e6', c2='#4ec4c8', c3='#2e7a96')               # le cœur de la méduse (lueurs)
SABLE = dict(back='#5c6178', front='#686a7e')                                       # l'arène : valeur moyenne
SABLE_R = dict(base='#3a4262', light='#475072', rim='#6a7494', sh='#2c3350')        # le sable de la rive


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


def objet(doc, parts, ink=INK, iw=1.0, volumes=True):
    """Un objet de plusieurs morceaux : UN seul contour autour de l'ensemble (tous les traits d'abord, puis les
    volumes par-dessus : entre les morceaux, pas de trait, seulement leurs ombres douces)."""
    out = []
    if ink:
        for p in parts:
            out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
                D(p[0]), ink, ink, fm(2 * iw)))
    for p in parts if volumes else ():
        kw = p[2] if len(p) > 2 else {}
        out.append(vol(doc, p[0], p[1], **kw))
    return ''.join(out)


def bosse(x, y, w_, h_, k=0.8):
    """Une forme posée au sol en (x, y) : dessous plat, dessus arrondi (rocher, éponge, corail cerveau)."""
    return sm([(x - w_ / 2, y + 1), (x - w_ * 0.42, y - h_ * 0.55), (x - w_ * 0.12, y - h_), (x + w_ * 0.22, y - h_ * 0.92),
               (x + w_ * 0.46, y - h_ * 0.45), (x + w_ / 2, y + 1)], sharp=(0, 5), t=k)


# ================================================================================================ LES ÉLÉMENTS
# Chaque élément : id, profondeur, genre ('fixe' : dans l'image fixe seulement ; 'boucle' ; 'morceau' = une boucle
# d'une image remise par-dessus ; 'particules') et sa fonction de dessin.
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


# ---------------------------------------------------------------------------------------------------- l'eau
LUMI = (452, 300)            # la lueur de la surface, très loin là-haut (la seule lumière)


@element('eau', -29.9, 'fixe')
def eau(doc):
    out = [path('M-20 -20H610V840H-20Z', doc.lin(0, 0, 0, 800, EAU))]
    lx, ly = LUMI
    out.append('<ellipse cx="%d" cy="%d" rx="340" ry="300" fill="%s"/>' % (lx, ly, doc.rad(
        lx, ly, 340, [(0, '#8ed0cc', 0.34), (0.35, '#5c9cb2', 0.16), (1, '#3a6e98', 0)], ry=300)))
    out.append('<ellipse cx="%d" cy="%d" rx="92" ry="80" fill="%s"/>' % (lx + 6, ly - 8, doc.rad(
        lx + 6, ly - 8, 92, [(0, '#e4fff6', 0.42), (0.45, '#aee6dc', 0.17), (1, '#8ccacc', 0)], ry=80)))
    # l'eau un peu plus claire près du sable lointain : le lointain s'y fond
    out.append(path('M-20 560H610V820H-20Z', doc.lin(0, 560, 0, 790, [(0, '#2a5078', 0), (1, '#33618a', 0.55)])))
    return ''.join(out)


@element('voiles', -29.5, 'fixe')
def voiles(doc):
    """Des voiles d'eau plus claire (comme des nuages sous la mer), grands et doux."""
    out = []
    a = lobes_shape(-30, 270, 214, [(256, 208, 9), (214, 198, 16), (160, 192, 20), (100, 190, 21), (40, 194, 19),
                                    (-12, 202, 14), (-30, 208, 9)], sag=3)
    out.append('<g opacity="0.55">%s</g>' % vol(doc, a, dict(VOILE, base='#2b5880', light='#31608a'), r=1.6, c=2.6))
    b = lobes_shape(330, 620, 268, [(612, 260, 10), (576, 254, 14), (534, 250, 15), (490, 252, 14), (446, 256, 12),
                                    (402, 260, 9), (360, 264, 6)], sag=2)
    out.append('<g opacity="0.6">%s</g>' % vol(doc, b, dict(VOILE, base='#3a6c90', light='#447896', rim='#62909e'),
                                                r=1.6, c=2.4))
    return ''.join(out)


@element('surplomb', -29.3, 'fixe')
def surplomb(doc):
    """En haut à gauche, le dessous d'un grand surplomb de récif (vu d'en dessous, dans l'eau), quelques algues qui
    pendent ; il reste au-dessus de y = 250 (les ombres des raies passent dessous)."""
    pts = [(-20, -20), (250, -20), (244, 14), (226, 48), (214, 92), (190, 130), (170, 166), (138, 196), (104, 214),
           (70, 226), (36, 240), (0, 246), (-20, 248)]
    s = sm(pts, sharp=(0, 1, len(pts) - 1), t=0.8)
    out = [vol(doc, s, SURPL, grad=doc.lin(240, 0, 40, 240, [(0, SURPL['light']), (0.6, SURPL['base']),
                                                              (1, SURPL['sh'])]), r=1.8, c=3.2, ink=INK, iw=0.8)]
    inner = [path(sm([(-20, 170), (60, 200), (120, 190), (176, 150), (214, 96), (240, 40), (240, 260), (-20, 260)],
                     t=0.8), SURPL['sh'], 0.55),
             path(sm([(150, -20), (240, -20), (232, 30), (214, 80), (190, 70), (176, 30)], t=0.8), SURPL['light'], 0.5)]
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    # trois algues qui pendent (des longueurs différentes)
    for x0, y0, L, sw in ((52, 236, 22, 1.0), (98, 214, 32, -1.0), (150, 184, 18, 1.0)):
        c = resample(bez((x0, y0 - 2), (x0 + 3 * sw, y0 + L * 0.4), (x0 - 4 * sw, y0 + L * 0.7), (x0 + 2 * sw, y0 + L)), 10)
        out.append(objet(doc, [(ribbon(c, [3.4, 3.2, 3, 2.8, 2.6, 2.4, 2.2, 2, 1.6, 1.2, 0.4]),
                                dict(ALGUE, base='#2e5a52', light='#386658', sh='#22463e'), dict(r=0.6, c=0.8))],
                         iw=0.6))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
def tour(doc, x, yb, ytop, cw, ch, sw, m, r=1.2, c=1.8):
    """Une tour de récif en champignon : un pied qui s'évase en bas, un chapeau aplati qui déborde."""
    h_ = yb - ytop
    s2 = sw / 2
    stem = sm([(x - s2 * 1.9, yb + 4), (x - s2 * 1.1, yb - h_ * 0.3), (x - s2 * 0.85, ytop + ch * 0.6),
               (x + s2 * 0.85, ytop + ch * 0.6), (x + s2 * 1.05, yb - h_ * 0.35), (x + s2 * 2.0, yb + 4)],
              sharp=(0, 5), t=0.8)
    cap = sm([(x - cw / 2, ytop + ch * 0.74), (x - cw * 0.44, ytop + ch * 0.28), (x - cw * 0.22, ytop + ch * 0.04),
              (x + cw * 0.08, ytop), (x + cw * 0.36, ytop + ch * 0.16), (x + cw / 2, ytop + ch * 0.62),
              (x + cw * 0.32, ytop + ch * 0.96), (x, ytop + ch), (x - cw * 0.32, ytop + ch * 0.95)], t=0.85)
    out = [vol(doc, stem, m, r=r, c=c)]
    # l'ombre du chapeau sur le haut du pied
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(stem.d()), path(
        'M%s %sH%sV%sH%sZ' % (fm(x - sw * 2), fm(ytop), fm(x + sw * 2), fm(ytop + ch + h_ * 0.12), fm(x - sw * 2)),
        doc.lin(0, ytop + ch * 0.8, 0, ytop + ch + h_ * 0.12, [(0, m['sh'], 0.8), (1, m['sh'], 0)]))))
    out.append(vol(doc, cap, m, r=r * 1.2, c=c * 1.3))
    return ''.join(out)


def kelp_loin(doc, x, yb, h_, sw, col, op):
    c = resample(catmull([(x, yb), (x + 3 * sw, yb - h_ * 0.3), (x - 3 * sw, yb - h_ * 0.65), (x + 2 * sw, yb - h_)]), 16)
    ws = [3.6 - 2.6 * (i / 16) ** 1.4 for i in range(17)]
    out = [path(ribbon(c, ws), col, op)]
    for i in range(3, 15, 3):
        px, py = c[i]
        sgn = 1 if i % 2 else -1
        leaf = sm([(px, py), (px + sgn * 5, py - 7), (px + sgn * 9, py - 13), (px + sgn * 4, py - 9)], sharp=(0, 2), t=0.7)
        out.append(path(leaf, col, op))
    return ''.join(out)


T1 = (452, 772, 318, 118, 36, 34)          # la grande tour (x, pied, haut, largeur et hauteur du chapeau, pied)


@element('lointain', -28.5, 'fixe')
def lointain(doc):
    out = []
    r1 = [(-20, 800), (-20, 712), (40, 700), (100, 712), (170, 724), (250, 718), (330, 726), (400, 712), (470, 704),
          (540, 714), (610, 706), (610, 800)]
    out.append(vol(doc, sm(r1, sharp=(0, 1, len(r1) - 2, len(r1) - 1), t=0.7), LOIN1, r=1.2, c=0))
    # les tours en champignon, de la plus lointaine à la plus proche
    out.append(tour(doc, 40, 760, 468, 84, 26, 24, LOIN1))
    out.append(tour(doc, 548, 762, 546, 70, 22, 20, LOIN1))
    out.append(tour(doc, *T1, LOIN1, r=1.6, c=2.4))
    # des ombres de varech au loin, en touffes
    for x, h_, sw in ((262, 170, 1), (276, 132, -1), (356, 150, -1), (370, 196, 1), (510, 160, 1), (524, 118, -1)):
        out.append(kelp_loin(doc, x, 760, h_, sw, '#2a4c74', 0.9))
    out.append(tour(doc, 322, 768, 530, 62, 22, 20, LOIN2))
    out.append(tour(doc, 238, 770, 584, 48, 18, 15, LOIN2))
    r2 = [(-20, 800), (-20, 744), (60, 738), (140, 748), (220, 752), (300, 748), (380, 754), (460, 746), (530, 750),
          (610, 742), (610, 800)]
    out.append(vol(doc, sm(r2, sharp=(0, 1, len(r2) - 2, len(r2) - 1), t=0.7), LOIN2, r=1.2, c=0))
    return ''.join(out)


@element('brume', -23, 'fixe')
def brume(doc):
    # l'eau bleue passe devant le lointain (pas devant le massif, la mâchoire ni l'épave)
    return path('M-10 640H600V800H-10Z', doc.lin(0, 640, 0, 790, [(0, '#2e5880', 0), (0.7, '#30598a', 0.3),
                                                                  (1, '#34618c', 0.5)]))


# ---------------------------------------------------------------------------------------------------- la mâchoire
MCX, MBASE = 290, 792


def arche(a, b, p=2.6, n=44):
    """Une arche (superellipse un peu carrée) : de son pied gauche, par le haut, à son pied droit."""
    pts = []
    for i in range(n + 1):
        th = math.pi * (1 - i / n)
        c, s = math.cos(th), math.sin(th)
        pts.append((MCX + a * math.copysign(abs(c) ** (2 / p), c), MBASE - b * abs(s) ** (2 / p)))
    return pts


def normale_dedans(pts, i):
    a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    return (dx / L, dy / L), (-dy / L, dx / L)          # la tangente, et la normale vers l'intérieur de l'arche


@element('machoire', -21.5, 'fixe')
def machoire(doc):
    """La mâchoire de requin géante, debout, à demi enfouie : un os ivoire en arche, ses dents tournées vers
    l'intérieur (deux rangs), ses deux articulations ; le sable la recouvre en bas (la rive)."""
    ext = arche(84, 160)
    inn = arche(58, 130)
    os_ = sm(ext + inn[::-1], sharp=(0, len(ext) - 1, len(ext), len(ext) * 2 - 1), t=0.9)
    parts = []
    dents = []
    for rang, (n_, L0, L1, w_, m, off) in enumerate(((10, 9, 14, 9, dict(DENT, base='#a29e98', light='#b2ada4'), 0.5),
                                                     (11, 12, 22, 11.5, DENT, 0.0))):
        for j in range(n_):
            u = (j + 0.5 + off * 0.5) / (n_ + off * 0.5)
            i = int(round(4 + u * (len(inn) - 9)))
            px, py = inn[i]
            (tx, ty), (nx, ny) = normale_dedans(inn, i)
            haut = math.sin(math.pi * i / (len(inn) - 1))           # les dents du haut sont les plus grandes
            L = L0 + (L1 - L0) * haut ** 2
            if rang == 0:
                L *= 0.85
            bx, by = px - nx * 3, py - ny * 3
            tip = (px + nx * L + tx * L * 0.12, py + ny * L + ty * L * 0.12)
            t_ = rpoly([(bx - tx * w_ / 2, by - ty * w_ / 2), (bx + tx * w_ / 2, by + ty * w_ / 2), tip], [1.5, 1.5, 0.8])
            dents.append((t_, m, dict(r=0.7, c=1.0)))
    parts = [(os_, OS_, dict(r=2.0, c=3.0))] + dents
    out = [objet(doc, parts, iw=1.0, volumes=False), vol(doc, os_, OS_, r=2.0, c=3.0)]
    # le creux de l'os (une gouttière plus sombre le long du bord intérieur) et un éclat plus clair en haut à droite
    inner = [path(ribbon(resample(arche(64, 136)[6:-6], 30), [1.2] + [3.4] * 29 + [1.2]), OS_['sh'], 0.35),
             path(ribbon(resample(arche(76, 152)[24:38], 12), [0.6, 2.4, 3.6, 4, 4, 3.6, 3.4, 3, 2.6, 2, 1.4, 0.8, 0.3]),
                  OS_['rim'], 0.5)]
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(os_.d()), ''.join(inner)))
    out.extend(vol(doc, d_[0], d_[1], **d_[2]) for d_ in dents)
    # un corail cuivre accroché à l'épaule droite, une algue sur la gauche (la mâchoire est là depuis longtemps)
    out.append(corail_branchu(doc, 344, 668, 0.7, ang=36))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les coraux
def corail_branchu(doc, x, y, k=1.0, ang=0, m=CUIVRE, iw=0.8):
    """Un corail branchu posé en (x, y) : un tronc court, des branches qui se divisent, bouts arrondis."""
    a0 = math.radians(ang)

    def R(u, v):
        return (x + (u * math.cos(a0) - v * math.sin(a0)) * k, y + (u * math.sin(a0) + v * math.cos(a0)) * k)
    branches = [
        ([(0, 2), (0, -6), (-3, -12), (-8, -17), (-10, -23)], [4.4, 4, 3.4, 3, 2.6]),
        ([(0, -6), (3, -12), (5, -19), (4, -26)], [3.6, 3.2, 2.8, 2.6]),
        ([(3, -12), (9, -16), (12, -21)], [3, 2.6, 2.4]),
        ([(-3, -12), (-2, -19), (-4, -25)], [2.8, 2.6, 2.4]),
    ]
    parts = []
    for pts, ws in branches:
        c = [R(u, v) for u, v in pts]
        ws_ = [w * k for w in ws]
        left, right = sides(c, ws_)
        tip = c[-1]
        dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
        L = math.hypot(dx, dy) or 1
        cap = (tip[0] + dx / L * ws_[-1] * 0.55, tip[1] + dy / L * ws_[-1] * 0.55)
        parts.append((sm(left + [cap] + right[::-1], sharp=(0, len(left) * 2), t=0.7), m, dict(r=0.8, c=1.0)))
    return objet(doc, parts, iw=iw)


def corail_cerveau(doc, x, y, w_, h_, m=ROSE):
    s = bosse(x, y, w_, h_, 0.9)
    out = [objet(doc, [(s, m, dict(r=1.0, c=1.4))], iw=0.8)]
    inner = []
    for dy_, dx_ in ((0.62, -0.1), (0.36, 0.08)):
        c = resample(catmull([(x - w_ * 0.36, y - h_ * dy_ + 2), (x - w_ * 0.1, y - h_ * (dy_ + 0.12)),
                              (x + w_ * (0.14 + dx_), y - h_ * (dy_ - 0.06)), (x + w_ * 0.36, y - h_ * dy_ - 1)]), 10)
        inner.append(path(ribbon(c, [0.3, 1.2, 1.6, 1.8, 1.8, 1.8, 1.6, 1.4, 1.2, 0.8, 0.2]), m['sh'], 0.5))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


def eponges(doc, x, y, k=1.0, m=JAUNE):
    """Des éponges en tubes (trois tubes de hauteurs différentes, une bouche sombre en haut)."""
    parts, bouches = [], []
    for dx, h_, w_ in ((-5, 13, 5.4), (1.5, 19, 6.2), (7.5, 10, 4.8)):
        cx = x + dx * k
        top = y - h_ * k
        parts.append((rpoly([(cx - w_ / 2 * k, y + 1), (cx - w_ / 2 * k * 1.08, top), (cx + w_ / 2 * k * 1.08, top),
                             (cx + w_ / 2 * k, y + 1)], [0.5, 1.8 * k, 1.8 * k, 0.5]), m, dict(r=0.8, c=1.0)))
        bouches.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(cx), fm(top + 1.3 * k), fm(w_ * 0.34 * k), fm(0.9 * k), mix(m['sh'], INK, 0.4)))
    return objet(doc, parts, iw=0.8) + ''.join(bouches)


def eventail(doc, x, y, k=1.0, m=VIOL):
    """Un corail éventail : une feuille plate et ondulée sur un pied court, deux trous (pas de nervures)."""
    s = sm([(x - 1.5 * k, y + 1), (x - 2 * k, y - 6 * k), (x - 11 * k, y - 12 * k), (x - 13 * k, y - 22 * k),
            (x - 6 * k, y - 29 * k), (x + 3 * k, y - 27 * k), (x + 11 * k, y - 24 * k), (x + 13 * k, y - 15 * k),
            (x + 6 * k, y - 8 * k), (x + 1.5 * k, y - 5 * k), (x + 1.5 * k, y + 1)], sharp=(0, 10), t=0.85)
    s = s.hole(ellipse(x - 4 * k, y - 19 * k, 2.2 * k, 1.6 * k)).hole(ellipse(x + 5 * k, y - 17 * k, 1.8 * k, 1.4 * k))
    return objet(doc, [(s, m, dict(r=0.9, c=1.2))], iw=0.8)


def herbe(doc, x, y, k=1.0, m=ALGUE):
    parts = []
    for dx, h_, b_ in ((-3, 9, -3), (0, 13, 1), (3, 8, 3)):
        c = resample(bez((x + dx * k, y + 1), (x + dx * k, y - h_ * k * 0.4), (x + (dx + b_) * k, y - h_ * k * 0.7),
                         (x + (dx + b_ * 1.6) * k, y - h_ * k)), 6)
        parts.append((ribbon(c, [2.6 * k, 2.4 * k, 2 * k, 1.6 * k, 1.2 * k, 0.8 * k, 0.2]), m, dict(r=0.5, c=0.6)))
    return objet(doc, parts, iw=0.6)


# ---------------------------------------------------------------------------------------------------- le massif
MASSIF_HAUT = [(-14, 530), (16, 522), (50, 517), (84, 519), (112, 516), (140, 514), (168, 518), (192, 526)]
MASSIF_RESTE = [(206, 540), (210, 558), (204, 574), (190, 584), (172, 590), (158, 596), (150, 612), (154, 650),
                (148, 690), (152, 732), (162, 770), (170, 792), (-14, 792)]


def sol_m(x):
    return interp(MASSIF_HAUT, x)


def massif_forme():
    pts = MASSIF_HAUT + MASSIF_RESTE
    return sm(pts, sharp=(0, len(pts) - 2, len(pts) - 1), t=0.75)


GROTTE = (114, 690)


@element('massif', -20, 'fixe')
def massif(doc):
    s = massif_forme()
    g = doc.lin(210, 520, 20, 760, [(0, ROCHE['light']), (0.45, ROCHE['base']), (1, ROCHE['sh'])])
    out = [vol(doc, s, ROCHE, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0)]
    inner = []
    # le chapeau : un grand pan éclairé (en haut à droite), son rebord ; le pied sous le chapeau, plus sombre
    inner.append(path(sm([(110, 522), (190, 528), (208, 552), (196, 578), (150, 586), (120, 560)], t=0.85),
                      ROCHE['light'], 0.55))
    inner.append(path(sm([(-20, 590), (60, 582), (130, 592), (160, 600), (172, 590), (200, 582), (200, 640),
                          (140, 650), (40, 640), (-20, 646)], t=0.8), ROCHE['sh'], 0.6))
    inner.append(path(sm([(-20, 650), (30, 680), (54, 760), (40, 800), (-20, 800)], t=0.8), ROCHE['sh'], 0.45))
    # un grand pan clair sur le pied, côté lumière
    inner.append(path(sm([(128, 640), (150, 630), (148, 690), (154, 740), (164, 790), (138, 790), (134, 720)],
                         t=0.85), ROCHE['light'], 0.4))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    # le jardin de coraux sur le chapeau (de gauche à droite ; la bannière et la dent sont des calques)
    out.append(eventail(doc, 30, sol_m(30) + 1, 1.0))
    out.append(corail_cerveau(doc, 58, sol_m(58) + 1, 26, 14))
    out.append(herbe(doc, 76, sol_m(76) + 1, 1.0))
    out.append(corail_cerveau(doc, 128, sol_m(128) + 1, 20, 12))
    out.append(herbe(doc, 140, sol_m(140) + 1, 0.8))
    out.append(eponges(doc, 180, sol_m(180) + 1.5, 1.0))
    out.append(corail_branchu(doc, 196, 529, 0.8, ang=14))
    # sur la paroi : un petit corail rose, des herbes au pied
    out.append(corail_cerveau(doc, 158, 646, 14, 8, dict(ROSE, base='#8e5276', light='#a4648a')))
    out.append(herbe(doc, 162, 790, 1.1))
    return ''.join(out)


def grotte(doc, ph):
    """La grotte du massif : une bouche sombre où luisent de petites bêtes (leur lueur respire, chacune à son tour)."""
    x, y = GROTTE
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    bouche = sm([(x - 22, y + 10), (x - 20, y - 2), (x - 10, y - 11), (x + 4, y - 13), (x + 16, y - 8), (x + 22, y + 2),
                 (x + 20, y + 11), (x, y + 13)], t=0.9)
    out = [path(bouche, INK)]
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(bouche.d()), ''.join([
        path(bouche.move(3, 4), '#0e1430'),
        '<ellipse cx="%d" cy="%d" rx="22" ry="12" fill="%s"/>' % (x + 2, y + 6, doc.rad(
            x + 2, y + 6, 22, [(0, LUEUR['c2'], 0.28 + 0.18 * k), (1, LUEUR['c3'], 0)], ry=12))])))
    for j, (dx, dy, r_) in enumerate(((-12, 6, 1.6), (-3, 8, 1.3), (7, 4, 1.8), (14, 7, 1.2))):
        kk = 0.5 - 0.5 * math.cos(2 * math.pi * (ph + j * 0.27))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x + dx), fm(y + dy), fm(r_ * 3), doc.rad(
            x + dx, y + dy, r_ * 3, [(0, LUEUR['c1'], 0.5 * kk), (1, LUEUR['c2'], 0)])))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x + dx), fm(y + dy), fm(r_),
                                                                     mix(LUEUR['c2'], LUEUR['c0'], kk)))
    return ''.join(out)


element('grotte', -19.8, 'boucle', box=(GROTTE[0] - 26, GROTTE[1] - 17, 52, 34), n=12, ms=400)(grotte)


# ---------------------------------------------------------------------------------------------------- le clan
DENT_FOSS = (157, sol_m(157))


def dent_fossile(doc):
    """La dent de requin fossile géante, plantée debout (pointe en haut, un peu penchée), sur un socle de pierres."""
    x, y = DENT_FOSS
    s = sm([(x - 13, y + 2), (x - 12, y - 10), (x - 8, y - 28), (x - 1, y - 46), (x + 3, y - 50), (x + 5, y - 44),
            (x + 9, y - 26), (x + 13, y - 8), (x + 13, y + 2)], sharp=(0, 4, 8), t=0.8)
    out = [vol(doc, s, FOSS, r=1.6, c=2.4, ink=INK, iw=1.0)]
    # la racine plus sombre en bas, un reflet sur le bord droit
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), path('M%d %dH%dV%dH%dZ' % (x - 16, y - 8, x + 16, y + 4,
                                                                                         x - 16), FOSS['sh'], 0.7)))
    out.append(path(ribbon(resample([(x + 5, y - 40), (x + 9, y - 26), (x + 11, y - 12)], 8),
                           [0.2, 0.8, 1.2, 1.4, 1.4, 1.2, 1, 0.6, 0.2]), FOSS['rim'], 0.6))
    out.append(vol(doc, rpoly([(x - 17, y + 4), (x - 15, y - 2), (x + 15, y - 3), (x + 17, y + 4)], 1.5), ROC,
                   r=0.9, c=1.2, ink=INK, iw=0.9))
    return ''.join(out)


def signe_forme(cx, cy, k):
    """Le signe de Kesha : un aileron de requin (l'encoche d'une vieille morsure sur son bord arrière) qui sort d'un
    croissant de vague ; aucune lettre."""
    def P(u, v):
        return (cx + u * k, cy + v * k)
    aileron = sm([P(-3.4, 1.4), P(-2.8, -1.6), P(-1.4, -4.4), P(0.6, -6.6), P(2.4, -7.6), P(1.6, -5.2), P(1.3, -3.0),
                  P(2.1, -2.3), P(1.3, -1.4), P(1.6, 0.2), P(2.4, 1.4)], sharp=(0, 4, 6, 7, 8, 10), t=0.85)
    vague = sm([P(-5.6, 0.6), P(-3.2, 2.6), P(0, 3.4), P(3.4, 2.4), P(5.4, 0.2), P(6.2, -1.6), P(5.0, -1.2),
                P(4.4, -0.2), P(3.0, 1.2), P(0, 1.9), P(-3.0, 1.5)], sharp=(0, 5), t=0.85)
    return aileron + vague


def signe(doc, ph):
    x, y = DENT_FOSS
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    out = [dent_fossile(doc)]
    out.append('<ellipse cx="%s" cy="%s" rx="12" ry="13" fill="%s"/>' % (x + 1, y - 20, doc.rad(
        x + 1, y - 20, 12, [(0, LUEUR['c1'], 0.18 + 0.22 * k), (1, LUEUR['c2'], 0)], ry=13)))
    out.append(path(signe_forme(x + 1, y - 17, 1.45), mix(LUEUR['c3'], LUEUR['c1'], 0.35 + 0.6 * k)))
    return ''.join(out)


element('signe', -19, 'boucle', box=(DENT_FOSS[0] - 20, DENT_FOSS[1] - 55, 40, 62), n=12, ms=400)(signe)

MAT_H = 50
BOIS_MAT = dict(base='#4a4048', light='#62545a', rim='#988070', sh='#2e2834')


def mat(doc, x, y):
    out = [vol(doc, rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6),
               BOIS_MAT, r=0.7, c=0.8, ink=INK, iw=0.7)]
    out.append(vol(doc, rpoly([(x - 13, y - MAT_H + 2), (x + 13, y - MAT_H + 2), (x + 13, y - MAT_H + 5),
                               (x - 13, y - MAT_H + 5)], 1.2), BOIS_MAT, r=0.7, c=0.8, ink=INK, iw=0.7))
    out.append('<circle cx="%s" cy="%s" r="2.6" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        x, y - MAT_H - 1, doc.rad(x + 1, y - MAT_H - 2, 3, [(0, '#fff0b8'), (1, '#b88a3a')]), INK))
    out.append(vol(doc, rpoly([(x - 6, y + 3), (x - 5, y - 2), (x + 5, y - 2.5), (x + 7, y + 3)], 1.2), ROC,
                   r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


def toile(doc, x, top, ph, k, L=32, w_=21, avec_mat=None):
    """Une bannière bleu nuit qui flotte dans le courant (elle ondule plus en bas qu'en haut), le signe en laiton."""
    a = 2 * math.pi * ph

    def P(u, v):          # u : -1..1 en travers, v : 0..1 en descendant
        sway = v ** 1.4 * (2.6 * math.sin(a + v * 2.4 + k) - 1.4)
        return (x + u * w_ / 2 * (1 - 0.06 * v) + sway, top + v * L + 0.9 * math.sin(a + u * 1.5 + k) * v)
    pts = [P(-1, 0), P(1, 0)]
    for v in (0.33, 0.66, 0.92):
        pts.append(P(1, v))
    pts += [P(1, 1.04), P(0, 0.86), P(-1, 1.04)]
    for v in (0.92, 0.66, 0.33):
        pts.append(P(-1, v))
    s = sm(pts, sharp=(0, 1, 5, 6, 7), t=0.6)
    out = [avec_mat or '', vol(doc, s, MARINE, r=1.3, c=2.0, ink=INK, iw=0.9)]
    sx, sy = P(0, 0.42)
    out.append(path(signe_forme(sx - 0.4, sy + 1.5, 1.15), LAITON))
    return ''.join(out)


BANNIERE = (106, sol_m(106))


def banniere(doc, ph):
    x, y = BANNIERE
    return toile(doc, x, y - MAT_H + 5, ph, 0, avec_mat=mat(doc, x, y))


element('banniere', -16, 'boucle', box=(BANNIERE[0] - 20, BANNIERE[1] - MAT_H - 5, 40, MAT_H + 10), n=12,
        ms=200)(banniere)


# ---------------------------------------------------------------------------------------------------- l'épave
MAT_E = [(436, 730), (433, 660), (430, 596)]        # le mât brisé (pied sur le pont, haut cassé)
VERGUE = (431, 612)                                  # la vergue brisée où pend le pavillon
FENETRE = (492, 676)


@element('epave', -20, 'fixe')
def epave(doc):
    """L'épave enfoncée dans le sable, la poupe plus haute (le château et sa fenêtre), un trou dans la coque, le mât
    brisé ; mangée par les coraux et les bernacles."""
    out = []
    # le mât (derrière la coque) et sa vergue brisée
    c = resample(MAT_E, 12)
    mat_ = ribbon(c, [5.2, 5, 4.8, 4.6, 4.5, 4.4, 4.3, 4.2, 4.1, 4.0, 3.9, 3.8, 3.6], sharp_ends=False)
    cass = sm([(427.8, 598), (429, 590), (431, 594), (432.4, 588), (433.4, 600)], sharp=(0, 1, 2, 3, 4), t=0.4)
    vx, vy = VERGUE
    vergue = rpoly([(vx - 17, vy - 1), (vx + 12, vy - 3), (vx + 12, vy + 1), (vx - 17, vy + 2.4)], 1.2)
    out.append(objet(doc, [(mat_, BOIS_MAT, dict(r=0.9, c=1.2)), (cass, BOIS_MAT, dict(r=0.5, c=0.6)),
                           (vergue, BOIS_MAT, dict(r=0.7, c=0.9))], iw=0.9))
    # la coque : la proue à gauche (plus basse, enfoncée), le pont qui monte vers la poupe
    coque = sm([(398, 794), (392, 770), (388, 748), (384, 734), (392, 736), (420, 732), (452, 726), (474, 720),
                (520, 716), (600, 710), (600, 794)], sharp=(0, 3, 4, 9, 10), t=0.8)
    chateau = sm([(468, 724), (470, 662), (474, 654), (540, 646), (600, 642), (600, 718)], sharp=(0, 1, 3, 4, 5), t=0.6)
    rambarde = rpoly([(468, 657), (600, 641), (600, 646), (470, 662)], 1.5)
    g = doc.lin(600, 650, 400, 780, [(0, BOIS['light']), (0.5, BOIS['base']), (1, BOIS['sh'])])
    out.append(objet(doc, [(chateau, BOIS, dict(r=1.8, c=2.6)), (rambarde, dict(BOIS, base='#524858'), dict(r=1, c=1)),
                           (coque, BOIS, dict(grad=g, r=2.0, c=3.2))], iw=1.0))
    inner = []
    # une préceinte (un renfort clair le long de la coque) et l'ombre sous le plat-bord
    c = resample(catmull([(390, 746), (430, 742), (480, 736), (540, 731), (600, 727)]), 20)
    inner.append(path(ribbon(c, [1.6] + [3.4] * 19 + [1.6]), BOIS['sh'], 0.55))
    c2 = resample(catmull([(396, 768), (440, 764), (500, 758), (600, 752)]), 20)
    inner.append(path(ribbon(c2, [1] + [2.6] * 19 + [1]), BOIS['rim'], 0.28))
    # le trou dans la coque, deux bouts de bordages cassés
    trou = sm([(416, 766), (420, 757), (428, 752), (436, 752), (444, 748), (452, 754), (456, 763), (450, 770),
               (440, 771), (430, 774), (421, 772)], sharp=(2, 4, 7, 9), t=0.8)
    inner.append(path(trou, '#1e1e34'))
    inner.append('<g clip-path="%s">%s</g>' % (doc.clip(trou.d()), path(trou.move(4, 4), '#141428')))
    # deux bouts de bordages cassés qui pointent dans le trou (le bois clair de la cassure)
    for pts, ws in (([(424, 752), (428, 759), (430, 765)], [3.2, 2.6, 2, 1.4, 1, 0.6, 0.2]),
                    ([(448, 750), (446, 757), (447, 763)], [3, 2.4, 1.8, 1.2, 0.8, 0.5, 0.2])):
        inner.append(path(ribbon(resample(pts, 6), ws), BOIS['base']))
        inner.append(path(ribbon(resample(pts, 6), [w * 0.45 for w in ws]), BOIS['rim'], 0.6))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(coque.d()), ''.join(inner)))
    # le château : un pan éclairé, le cadre de la fenêtre (la vitre qui luit est un calque)
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(chateau.d()), path(
        sm([(520, 648), (600, 640), (600, 716), (540, 712)], t=0.8), BOIS['light'], 0.35)))
    fx, fy = FENETRE
    out.append(objet(doc, [(rpoly([(fx - 9, fy + 10), (fx - 9, fy - 6), (fx, fy - 12), (fx + 9, fy - 6),
                                   (fx + 9, fy + 10)], 2.5), dict(BOIS, base='#3a3442'), dict(r=0.8, c=1))], iw=0.8))
    # des bernacles (de petites bosses ivoire, en grappes) et des coraux
    for gx, gy, n_ in ((404, 776, 4), (462, 742, 3), (512, 734, 4), (486, 700, 3)):
        for j in range(n_):
            bx = gx + j * 4.2 - n_ * 2 + (j % 2) * 1.2
            by = gy - (j % 2) * 3.2
            out.append(objet(doc, [(bosse(bx, by, 4.4, 3.4), dict(DENT, base='#8e8a88', light='#a29c96', rim='#c4bcb0'),
                                    dict(r=0.5, c=0.6))], iw=0.5))
    out.append(corail_branchu(doc, 516, 650, 0.85, ang=-6))
    out.append(corail_cerveau(doc, 482, 658, 16, 9))
    out.append(eponges(doc, 560, 645, 0.9, VIOL))
    return ''.join(out)


def fenetre(doc, ph):
    """La fenêtre du château qui luit (une lueur qui respire lentement)."""
    fx, fy = FENETRE
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    vitre = rpoly([(fx - 6, fy + 7.5), (fx - 6, fy - 4.5), (fx, fy - 9), (fx + 6, fy - 4.5), (fx + 6, fy + 7.5)], 2)
    out = [path(vitre, doc.lin(fx + 4, fy - 8, fx - 4, fy + 8, [(0, mix(LUEUR['c1'], LUEUR['c0'], k * 0.5)),
                                                                 (1, LUEUR['c2'])]))]
    out.append('<ellipse cx="%s" cy="%s" rx="14" ry="15" fill="%s"/>' % (fx, fy, doc.rad(
        fx, fy, 14, [(0, LUEUR['c1'], 0.2 + 0.2 * k), (1, LUEUR['c2'], 0)], ry=15)))
    out.append(path(rpoly([(fx - 0.7, fy - 8), (fx + 0.7, fy - 8), (fx + 0.7, fy + 7.5), (fx - 0.7, fy + 7.5)], 0.2),
                    '#3a3442', 0.9))
    return ''.join(out)


element('fenetre', -19.6, 'boucle', box=(FENETRE[0] - 15, FENETRE[1] - 16, 30, 32), n=8, ms=600)(fenetre)


def pavillon(doc, ph):
    vx, vy = VERGUE
    return toile(doc, vx - 9, vy + 1, ph, 1.7, L=30, w_=18)


element('pavillon', -16, 'boucle', box=(VERGUE[0] - 30, VERGUE[1] - 2, 42, 40), n=12, ms=200)(pavillon)


def anemone(doc, ph):
    """L'anémone posée sur la proue : un pied rose violet, des tentacules épais qui ondulent dans le courant."""
    x, y = 399, 733
    a = 2 * math.pi * ph
    parts = []
    for j, ang in enumerate((-150, -125, -100, -80, -58, -34)):
        r0 = math.radians(ang)
        L = 10 + 2 * (j % 2)
        pts = []
        for v in range(5):
            u = v / 4
            sway = 2.4 * u * math.sin(a + j * 0.9 + u * 2)
            pts.append((x + math.cos(r0) * (5 + L * u) + sway, y - 6 + math.sin(r0) * (3 + L * u)))
        parts.append((ribbon(pts, [3.2, 3, 2.6, 2.2, 1.6], sharp_ends=False), dict(VIOL, base='#9a5aa0', light='#b072b2',
                                                                                    rim='#d8a2d0', sh='#6a3a7a'),
                      dict(r=0.6, c=0.7)))
    pied = sm([(x - 6, y + 2), (x - 6, y - 4), (x - 3, y - 7), (x + 3, y - 7), (x + 6, y - 4), (x + 6, y + 2)],
              sharp=(0, 5), t=0.8)
    parts.append((pied, ROSE, dict(r=0.8, c=1.0)))
    return objet(doc, parts, iw=0.7)


element('anemone', -15.8, 'boucle', box=(378, 710, 42, 30), n=8, ms=300)(anemone)


# ---------------------------------------------------------------------------------------------------- les varechs
VARECHS = [
    # (pied x, pied y, hauteur, côté où penchent les feuilles d'abord, phase)
    (198, 788, 300, 1, 0.0),
    (384, 788, 268, -1, 0.4),
    (70, 790, 196, 1, 0.7),
]
VARECH_N, VARECH_MS = 8, 300


def varech(k):
    bx, by, h_, sg, ph0 = VARECHS[k]

    def fn(doc, ph):
        a = 2 * math.pi * (ph + ph0)
        n = 18
        c = []
        for i in range(n + 1):
            v = i / n
            sway = 9 * v ** 1.6 * math.sin(a - v * 2.2) + 3 * v * math.sin(2 * a - v * 3 + 1)
            c.append((bx + sway + 2 * math.sin(v * 5 + k), by - h_ * v))
        ws = [3.4 - 1.6 * (i / n) for i in range(n + 1)]
        parts = [(ribbon(c, ws), KELP, dict(r=0.6, c=0.8))]
        # des frondes le long de la tige, alternées, qui suivent le courant
        for j, i in enumerate(range(3, n + 1, 2)):
            px, py = c[i]
            s_ = sg * (1 if j % 2 == 0 else -1)
            v = i / n
            L = 15 + 7 * math.sin(math.pi * v) - (4 if i == n else 0)
            lean = 0.55 + 0.25 * math.sin(a - v * 2.2 + 1.2)
            tip = (px + s_ * L * 0.6 + 3 * math.sin(a - v * 2), py - L * lean - 4)
            mid = ((px + tip[0]) / 2 + s_ * 2.4, (py + tip[1]) / 2 + 1.5)
            leaf = sm([(px, py + 1), (mid[0] + s_ * 2.6, mid[1] + 2.2), tip, (mid[0] - s_ * 2.2, mid[1] - 2.6)],
                      sharp=(0, 2), t=0.8)
            parts.append((leaf, KELP, dict(r=0.6, c=0.8)))
            if j % 2 == 0:
                parts.append((ellipse(px + s_ * 1.6, py - 0.5, 2.2, 2.0), dict(KELP, base='#7a8a48', light='#8e9a52'),
                               dict(r=0.4, c=0.4)))
        return objet(doc, parts, iw=0.7)
    return fn


for _k, (_bx, _by, _h, _sg, _ph) in enumerate(VARECHS):
    element('varech%d' % (_k + 1), -18.5 if _k < 2 else -15.9, 'boucle', box=(_bx - 32, _by - _h - 14, 64, _h + 18),
            n=VARECH_N, ms=VARECH_MS)(varech(_k))


# ---------------------------------------------------------------------------------------------------- la rive
EVENTS = [(150, 783), (466, 785)]


def etoile_mer(doc, x, y, k=1.0, ang=12):
    pts = []
    for i in range(10):
        r_ = (7 if i % 2 == 0 else 2.8) * k
        a = math.radians(ang + i * 36)
        pts.append((x + r_ * math.cos(a), y + r_ * math.sin(a) * 0.45))
    return objet(doc, [(rpoly(pts, [1.6 * k if i % 2 == 0 else 0.8 * k for i in range(10)]),
                        dict(base='#b0684c', light='#c4805a', rim='#e0a884', sh='#7a4040'), dict(r=0.5, c=0.7))], iw=0.6)


def coquillage(doc, x, y, k=1.0):
    s = sm([(x - 4 * k, y + 1), (x - 3.4 * k, y - 2.6 * k), (x, y - 4 * k), (x + 3.4 * k, y - 2.6 * k), (x + 4 * k, y + 1)],
           sharp=(0, 4), t=0.9)
    return objet(doc, [(s, dict(base='#c4a8a0', light='#d8c0b4', rim='#f0e0d4', sh='#8a7480'), dict(r=0.5, c=0.6))],
                 iw=0.5)


def evente(doc, x, y):
    """Un évent : une petite cheminée de roche d'où montent les bulles."""
    s = sm([(x - 10, y + 2), (x - 7, y - 5), (x - 4, y - 10), (x + 4, y - 10), (x + 7, y - 4), (x + 11, y + 2)],
           sharp=(0, 5), t=0.85)
    out = [objet(doc, [(s, ROC, dict(r=0.9, c=1.2))], iw=0.8)]
    out.append('<ellipse cx="%s" cy="%s" rx="3.4" ry="1.3" fill="%s"/>' % (x, y - 9.6, '#12162e'))
    return ''.join(out)


@element('rive', -17.5, 'fixe')
def rive(doc):
    """La rive de sable : devant le massif, la mâchoire (qu'elle enterre) et l'épave, jusqu'au bord de l'arène."""
    out = []
    pts = [(-10, P0 + 2), (-10, 788), (40, 784), (100, 786), (160, 781), (200, 776), (240, 770), (292, 767),
           (340, 770), (380, 776), (400, 778), (430, 783), (480, 780), (540, 784), (600, 781), (600, P0 + 2)]
    s = sm(pts, sharp=(0, 1, len(pts) - 2, len(pts) - 1), t=0.7)
    out.append(vol(doc, s, SABLE_R, grad=doc.lin(0, 768, 0, P0, [(0, SABLE_R['light']), (0.5, SABLE_R['base']),
                                                                  (1, SABLE_R['sh'])]), r=1.4, c=0))
    # rochers, herbes, coquillages, étoile de mer, évents (peu de choses, et pas devant le milieu du combat)
    for x, w_, h_ in ((26, 26, 9), (198, 16, 6), (342, 18, 6), (556, 28, 9)):
        out.append(objet(doc, [(bosse(x, 793, w_, h_), ROC, dict(r=1.0, c=1.4))], iw=0.8))
    for x, y in EVENTS:
        out.append(evente(doc, x, y))
    out.append(herbe(doc, 112, 789, 1.0))
    out.append(herbe(doc, 262, 784, 0.8, dict(ALGUE, base='#46705a')))
    out.append(herbe(doc, 412, 789, 0.9))
    out.append(etoile_mer(doc, 320, 788, 0.9))
    out.append(coquillage(doc, 242, 790, 0.9))
    out.append(coquillage(doc, 498, 792, 0.8))
    # le bord de l'arène : un fil sombre (la corniche)
    out.append(path('M-10 %dH600V%dH-10Z' % (P0 - 2, P0), '#1c2242', 0.75))
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
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, P0, 0, P1, [(0, SABLE['back']), (1, SABLE['front'])])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, 0, 590, 0, [(0, '#141a38', 0.06),
                                                                              (1, '#e8fff8', 0.04)])))
    # les grandes dalles d'un temple englouti : des joints à peine marqués, décalés d'un rang à l'autre
    rows = [P0, 826, 856, 892, 936, 988, P1]
    joints = []
    for i in range(len(rows) - 1):
        ya, yb = rows[i], rows[i + 1]
        if i > 0:
            joints.append('M-10 %s H600' % fm(ya))
        step = 170
        off = (i % 2) * step / 2 + (i * 41) % 50
        g = -900 + off
        while g < 900:
            xa, xb = sol_x(g, ya), sol_x(g, yb)
            if -10 < min(xa, xb) and max(xa, xb) < 600:
                joints.append('M%s %s L%s %s' % (fm(xa), fm(ya + 1), fm(xb), fm(yb - 1)))
            g += step + 24 * math.sin(i * 2.7 + g)
    jd = ' '.join(joints)
    out.append('<path d="%s" fill="none" stroke="#eef6ff" stroke-width="1.2" opacity="0.05" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#161a36" stroke-width="1" opacity="0.11"/>' % jd)
    # le sable clair qui recouvre à demi le dallage : de grandes nappes très douces, allongées (jamais rondes)
    for pts, op in (([(-10, 801), (70, 801), (150, 802), (214, 804), (178, 811), (120, 816), (60, 822), (-10, 819)],
                     0.06),
                    ([(310, 801), (420, 801), (530, 801), (600, 801), (600, 818), (548, 822), (470, 815), (380, 810)],
                     0.05)):
        out.append(path(sm(pts, sharp=(0, 3) if pts[0][0] < 0 else (0, 3), t=0.9), '#e8e2d8', op))
    # quelques dalles un peu plus sombres (très peu)
    for (g0, i, col, op) in ((60, 3, '#161a36', 0.04), (-90, 4, '#161a36', 0.035), (240, 1, '#161a36', 0.03)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 150, ya), ya), (sol_x(g0 + 150, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le bord arrière : l'arête éclairée ; une ombre douce juste devant la rive
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 1.6), '#8e94a8', 0.7))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0 + 1.6, P0 + 14), doc.lin(0, P0, 0, P0 + 14, [(0, '#1a2040', 0.12),
                                                                                             (1, '#1a2040', 0)])))
    # l'arête avant éclairée, puis le flanc de blocs (sous les cartes en combat : simple)
    out.append(path('M-10 %dH600V%dH-10Z' % (P1, 1064), doc.lin(0, P1, 0, 1064, [
        (0, '#3e4462'), (0.5, '#363c58'), (1, '#262c48')])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P1 - 1, P1 + 1.6), '#9aa0b4', 0.85))
    for g in range(-600, 700, 170):
        x = sol_x(g, P1)
        out.append(path(rpoly([(x - 0.6, P1 + 2), (x + 0.6, P1 + 2), (x + 0.6, 1060), (x - 0.6, 1060)], 0.3),
                        '#161a36', 0.35))
    return ''.join(out)


@element('dessous', -15.4, 'fixe')
def dessous(doc):
    """Sous le flanc de l'arène, la fosse : en combat, c'est sous les cartes des héros (y > 985) ; donc simple et
    sombre, sans détail ni animation."""
    out = [path('M-10 1062H600V1104H-10Z', doc.lin(0, 1062, 0, 1100, [(0, '#1e2648'), (0.35, '#161c3a'),
                                                                     (1, '#10142c')]))]
    pts = [(-10, 1058), (600, 1058), (600, 1064)]
    x, i = 600, 0
    while x > -10:
        x -= 22 + 9 * math.sin(i * 1.7)
        pts.append((x, 1064 + 3 * math.sin(i * 2.3) + 1.5 * math.cos(i * 1.1)))
        i += 1
    pts.append((-10, 1064))
    out.append(path(sm(pts, sharp=(0, 1), t=0.7), doc.lin(0, 1058, 0, 1068, [(0, '#2c3456'), (1, '#222a4a')])))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- premier plan
@element('corail-gauche', 1300, 'morceau', box=(0, 1026, 84, 74))
def corail_g(doc):
    s = sm([(-12, 1104), (-12, 1052), (10, 1044), (34, 1048), (54, 1060), (68, 1078), (78, 1104)], sharp=(0, 6), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(30, 1050), (50, 1062), (62, 1078), (48, 1084), (34, 1066)], t=0.9), ROC['light'], 0.5))
    out.append(corail_branchu(doc, 22, 1048, 1.0, ang=-8))
    return ''.join(out)


@element('corail-droite', 1300, 'morceau', box=(520, 1026, 70, 74))
def corail_d(doc):
    s = sm([(522, 1104), (530, 1080), (546, 1060), (566, 1048), (590, 1044), (604, 1048), (604, 1104)], sharp=(0, 6),
           t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(568, 1052), (592, 1048), (600, 1064), (584, 1070)], t=0.9), ROC['light'], 0.5))
    out.append(eponges(doc, 574, 1050, 1.0, VIOL))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- bulles et neige
def bulle_image(doc, i, n):
    t = i / (n - 1)
    r = 1.6 + 1.6 * t
    op = 0.85 if t < 0.8 else 0.85 * (1 - (t - 0.8) / 0.2) + 0.1
    return ('<circle cx="6" cy="6" r="%s" fill="%s" opacity="%g"/>' % (fm(r), doc.rad(
        6 + r * 0.3, 6 - r * 0.3, r * 1.2, [(0, '#e8fff8', 0.55), (0.6, '#9edce0', 0.25), (1, '#7ac0d0', 0.45)]), op)
        + '<circle cx="%s" cy="%s" r="%s" fill="#f4fffc" opacity="%g"/>' % (
            fm(6 + r * 0.4), fm(6 - r * 0.4), fm(r * 0.3), op))


for _k, (_x, _y) in enumerate(EVENTS):
    element('bulles%d' % (_k + 1), -14, 'particules', taille=(12, 12), images=5, dessin=bulle_image,
            zone=(_x - 2, _y - 12, _x + 2, _y - 10), nombre=4, vie=(4200, 5800), vx=(-1.5, 1.5), vy=(-22, -15),
            ondule=(2.2, 1600))


def neige_image(doc, i, n):
    op = (0.25, 0.6, 0.7, 0.6, 0.25)[i]
    return '<circle cx="3" cy="3" r="1.1" fill="#d4ecf2" opacity="%g"/>' % op


element('neige', -14, 'particules', taille=(6, 6), images=5, dessin=neige_image, zone=(96, 250, 500, 620), nombre=16,
        vie=(7000, 10000), vx=(-2, 2), vy=(3, 6), ondule=(3, 5200))


# ---------------------------------------------------------------------------------------------------- les ombres
# La touche vivante (comme les dragons de Kael) : deux raies manta et un serpent de mer, des ombres lointaines dans
# l'eau, de la couleur de l'eau en plus sombre ; plus loin = plus petit, plus pâle et plus lent. Elles passent au-dessus
# du massif, de la mâchoire, des varechs et de l'épave (jamais devant eux ni sur l'arène) ; le serpent, le plus loin,
# passe derrière la grande tour (un morceau la remet devant lui). Chacune est une particule seule qui vit une période
# entière : elle naît hors de l'image et finit hors de l'image ; ses ailes (ou son corps) ondulent en boucle.
OMBRES = [
    # id, genre, y, échelle, x de départ, x d'arrivée, montée (px/s), couleur, opacité, profondeur
    ('manta1', 'manta', 412, 0.6, -70, 660, -0.3, '#152a4e', 0.78, -28.4),     # la plus proche, sous les autres
    ('manta-loin', 'manta', 288, 0.36, 640, -50, 0.2, '#1d3a62', 0.6, -29.45),      # loin, en haut, vers la gauche
    ('serpent1', 'serpent', 344, 0.5, 680, -110, -0.2, '#1e3c64', 0.58, -29.44),  # le plus loin, derrière la tour
]
OMBRE_N, OMBRE_MS = 12, 200                     # un battement = 2,4 s
BOITES = {'manta': (-64, -48, 100, 96), 'serpent': (-130, -30, 196, 60)}       # repère local (tête à droite)


def manta_formes(ph):
    """Une raie manta vue d'en dessous, de trois quarts (tête à droite, elle file vers la droite) : le losange des
    ailes, les deux cornes de la tête, la queue fine. Au battement, l'envergure se raccourcit (les ailes montent ou
    descendent, vues de face) et les pointes vont en avant puis en arrière. Renvoie (aile du haut, le reste)."""
    a = 2 * math.pi * ph
    s_ = 0.8 + 0.2 * math.cos(a)
    b = math.sin(a)

    def aile(sg):
        tip = (-13 - 7 * b, sg * 44 * s_)
        return sm([(16, sg * 3), (13, sg * (13 * s_ + 3)), (3, sg * 30 * s_), tip, (-13 - 3 * b, sg * 25 * s_),
                   (-16, sg * 13 * s_), (-20, sg * 3)], sharp=(3,), t=0.85)
    corps = sm([(-23, -4), (-4, -8), (12, -9), (18, -7), (19, 0), (18, 7), (12, 9), (-4, 8), (-23, 4)],
               sharp=(3, 5), t=0.8)
    cornes = [sm([(16, sg * 6), (25, sg * 10.5), (28, sg * 9), (24, sg * 6.5), (18, sg * 3)], sharp=(2,), t=0.8)
              for sg in (-1, 1)]
    queue = ribbon([(-21, 0), (-36, 0.8), (-50, 2), (-62, 3.4)], [3.4, 2, 1.1, 0.3])
    return aile(-1), [corps, aile(1), queue] + cornes


def serpent_corps(ph):
    """Le serpent de mer vu de côté (tête à droite) : un long corps qui ondule (l'onde file de la tête vers la queue),
    une tête allongée, une crête de trois nageoires, deux petites nageoires sous le cou."""
    n = 40
    c = []
    for i in range(n + 1):
        u = i / n                                   # 0 : la queue, 1 : la tête
        x = -126 + 168 * u
        A = 9 * (1 - 0.75 * u ** 2)
        c.append((x, A * math.sin(2 * math.pi * (u * 1.6 + ph))))
    ws = [0.8 + 13.2 * math.sin(math.pi * min(1, u / 0.9)) ** 0.7 if u < 0.9 else 10 for u in (i / n for i in range(n + 1))]
    corps = ribbon(c, ws, sharp_ends=False)
    hx, hy = c[-1]
    tete = sm([(hx - 6, hy - 6.4), (hx + 6, hy - 7), (hx + 19, hy - 2.4), (hx + 24, hy + 1.6), (hx + 12, hy + 5.6),
               (hx - 4, hy + 6.4)], sharp=(3,), t=0.85)
    out = [corps, tete]
    for u0, h_ in ((0.42, 7), (0.6, 9), (0.78, 7)):
        i = int(u0 * n)
        (x0, y0), (x1, y1) = c[i - 2], c[i + 2]
        out.append(sm([(x0, y0 - ws[i] * 0.4), ((x0 + x1) / 2 - 2, (y0 + y1) / 2 - ws[i] * 0.5 - h_), (x1, y1 - ws[i] * 0.4)],
                      sharp=(0, 1, 2), t=0.7))
    out.append(sm([(hx - 14, hy + 3), (hx - 20, hy + 11), (hx - 9, hy + 5)], sharp=(0, 1, 2), t=0.7))
    out.append(ribbon([(hx + 2, hy - 4), (hx - 6, hy - 10), (hx - 13, hy - 12)], [2, 1.2, 0.3]))
    return out


def ombre_image(id_):
    _, genre, y, k, x0, x1, vy, col, op, _ = next(d for d in OMBRES if d[0] == id_)
    sg = 1 if x1 > x0 else -1
    bx, by, bw, bh = BOITES[genre]
    w, h = bw * k + 4, bh * k + 4

    def fn(doc, i, n):
        ph = i / n
        loin = mix(col, '#2c5a84', 0.3)                     # l'aile lointaine, plus dans l'eau
        ox = w / 2 - (bx + bw / 2) * k * sg
        oy = h / 2 - (by + bh / 2) * k
        out = ['<g transform="translate(%s %s) scale(%s %s)">' % (fm(ox), fm(oy), fm(k * sg), fm(k))]
        if genre == 'manta':
            haut, reste = manta_formes(ph)
            out.append(path(haut, loin))
            out.extend(path(p_, col) for p_ in reste)
        else:
            out.extend(path(p_, col) for p_ in serpent_corps(ph))
        out.append('</g>')
        return '<g opacity="%g">%s</g>' % (op, ''.join(out))
    return fn, (round(w), round(h))


for _d in OMBRES:
    _fn, _t = ombre_image(_d[0])
    _vx = (_d[5] - _d[4]) * 1000 / PERIODE
    element(_d[0], _d[9], 'particules', taille=_t, images=OMBRE_N, ms=OMBRE_MS, dessin=_fn,
            zone=(_d[4], _d[2], _d[4], _d[2]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_d[6], _d[6]),
            ondule=(0, PERIODE))


def devant(ids, box):
    """Un morceau du paysage remis devant les ombres : ces éléments seuls (sans l'eau), coupés à la boîte."""
    def fn(doc):
        x, y, w, h = box
        body = ''.join(e['fn'](doc) for e in sorted(ELEMS, key=lambda e: e['prof']) if e['id'] in ids)
        return '<g clip-path="%s">%s</g>' % (doc.clip('M%s %sH%sV%sH%sZ' % (x, y, x + w, y + h, x)), body)
    return fn


DEVANT_TOUR = (386, 306, 132, 70)
element('devant-tour', -28.45, 'morceau', box=DEVANT_TOUR)(devant(('lointain',), DEVANT_TOUR))


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
# Côté héros : trois héros vectoriels ; en face, les trois monstres du clan de Kesha (homme-poisson, crabe géant,
# méduse éclair), retournés vers la gauche.
PERSOS = [('knights-1', 'heros', 0), ('dragon-vent', 'heros', 2), ('mages-3', 'heros', 4),
          ('mon-kesha-rapide', 'ennemis', 0), ('mon-kesha-costaud', 'ennemis', 2), ('mon-kesha-sorts', 'ennemis', 4)]


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
    rendre([(scene(T_VUE), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    planche.save(os.path.join(JEU, CLAN + '-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': CLAN, 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/' + CLAN + '.webp', 'planche': 'art/vecto/fonds/' + CLAN + '-anim.webp',
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("kesha-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-' + CLAN + '.json'), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print('  jeu : public/art/vecto/fonds/%s.webp %d Ko, %s-anim.webp %d Ko (%d × %d), %d calques' % (CLAN,
        os.path.getsize(os.path.join(JEU, CLAN + '.webp')) // 1024, CLAN,
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
        vue_combat(T_VUE, 780).convert('RGB').save(os.path.join(TMP, 'brouillon-390.png'))
        vue_combat(T_VUE, 720, phone=(360, 640, 0)).convert('RGB').save(os.path.join(TMP, 'brouillon-360.png'))
        rendre([(scene(T_VUE), os.path.join(TMP, 'brouillon-fond.png'))], W, H)
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
