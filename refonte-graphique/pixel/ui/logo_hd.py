#!/usr/bin/env python3
"""Le LOGO du jeu en HD (vectoriel, net à toutes les tailles) — demande du propriétaire du 25/11 : « le logo pas en pixel,
en HD, beau ». Même disposition que l'ancien logo peint : « FUZE / ARENA » en grosses lettres d'or, le ruban rouge
« HERO BATTLE » bordé d'or, deux épées croisées derrière (plus d'étoile : demande du propriétaire, 25/11).

Les lettres sont les vrais contours de la police des titres du jeu (Lilita One, lilita-one.woff2) convertis en tracés :
le logo ne dépend d'aucune police chargée. Or : dégradé métallique (haut clair, « ligne d'horizon » au milieu, bas orangé),
liseré clair sur les bords tournés vers la lumière (en haut à droite), bord plus sombre en bas à gauche, reflet doux,
tranche brun rouge en dessous, un seul contour sombre épais, ombre portée douce.

  python3 refonte-graphique/pixel/ui/logo_hd.py → public/art/ui/logo.svg (lu par ui-moderne/chargement/chargement.py, posé dans index.html)
Aperçu PNG haute définition : refonte-graphique/pixel/sortie/ui/logo-hd.png (fait par la capture Playwright).
"""
import os
import sys
import math
import re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uilib as U  # noqa: E402

VW, VH = 640, 500           # tout compris : pointes et pommeaux des épées, queues du ruban, contour épais, ombre
FONT = TTFont(U.POLICE)
GS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
HMTX = FONT['hmtx']


def mot(texte, taille, cx, base, espace=0.0, courbe=None):
    """Le tracé SVG d'un mot centré sur cx, ligne de base `base` ; taille = hauteur de l'em en unités du logo.
    courbe(x) = (décalage vertical, angle en degrés) pour suivre un ruban."""
    k = taille / 1000
    largeurs = [HMTX[CMAP[ord(c)]][0] * k for c in texte]
    total = sum(largeurs) + espace * (len(texte) - 1)
    x = cx - total / 2
    d = []
    for c, w in zip(texte, largeurs):
        g = CMAP[ord(c)]
        dy, ang = courbe(x + w / 2) if courbe else (0, 0)
        a = math.radians(ang)
        mx, my = x + w / 2, base + dy
        # x' = mx + cos·(gx−w/2) − sin·(−gy) … (la police a y vers le haut)
        ca, sa = math.cos(a), math.sin(a)
        t = (k * ca, k * sa, k * sa, -k * ca, mx - ca * w / 2, my - sa * w / 2)
        pen = SVGPathPen(GS)
        GS[g].draw(TransformPen(pen, t))
        d.append(re.sub(r'-?\d+\.\d+', lambda m: f'{float(m.group()):.1f}'.rstrip('0').rstrip('.'), pen.getCommands()))
        x += w + espace
    return ' '.join(d)


def epee(id_, sens):
    """Une des deux épées, refaites le 29/11 (« le bandeau et les 2 épées : refais-les correctement et mieux ») : elles se
    croisent par leurs poignées juste sous le ruban, au milieu (garde d'or courbée avec un rubis, poignée de cuir,
    pommeau d'or), et leurs lames s'ouvrent en V derrière le logo : les pointes d'acier ressortent en haut, de part et
    d'autre de « FUZE ». Un seul contour sombre ; la moitié de la lame tournée vers la lumière est claire ; une arête fine."""
    ang = 39 * sens                        # sens -1 : la lame part en haut à gauche ; +1 : en haut à droite
    gx, gy = 320 - 22 * sens, 392          # la garde, sous le ruban (les deux poignées se croisent en dessous)
    lame = 'M-17,-8 L17,-8 L15,-388 Q10,-420 0,-442 Q-10,-420 -15,-388 Z'
    clair = 'M0,-8 L17,-8 L15,-388 Q10,-420 0,-442 Z'
    arete = 'M-1.8,-16 L1.8,-16 L1.6,-408 L0,-424 L-1.6,-408 Z'
    garde = 'M-64,6 Q-40,-2 0,-2 Q40,-2 64,6 Q72,-6 68,-19 Q40,-11 0,-12 Q-40,-11 -68,-19 Q-72,-6 -64,6 Z'
    return f'''
  <g transform="translate({gx},{gy}) rotate({ang}) scale(1.08)">
    <path d="{lame}" fill="#7e89b8" stroke="#241434" stroke-width="8" stroke-linejoin="round"/>
    <path d="{clair}" fill="url(#lg-acier)"/>
    <path d="{arete}" fill="#f6f9ff" opacity=".85"/>
    <rect x="-11" y="4" width="22" height="58" rx="9" fill="url(#lg-cuir)" stroke="#241434" stroke-width="7"/>
    <rect x="1" y="10" width="4" height="46" rx="2" fill="#c8605a" opacity=".55"/>
    <path d="{garde}" fill="url(#lg-or-piece)" stroke="#241434" stroke-width="7" stroke-linejoin="round"/>
    <circle cx="0" cy="-5" r="10" fill="#d9303a" stroke="#5e1418" stroke-width="3.5"/>
    <circle cx="3" cy="-8.5" r="3.4" fill="#ffc8b8"/>
    <circle cx="0" cy="76" r="17" fill="url(#lg-or-piece)" stroke="#241434" stroke-width="7"/>
    <circle cx="0" cy="76" r="6.5" fill="#d9303a" stroke="#5e1418" stroke-width="2.5"/>
    <circle cx="4.5" cy="70" r="4.5" fill="#fff6c8"/>
  </g>'''


def ruban_y(x):
    """Le ruban est cintré : ses bouts remontent (sourire), et chaque lettre s'incline avec lui."""
    t = (x - 320) / 224
    return 24 * t * t, math.degrees(math.atan(2 * 24 * t / 224))


def svg():
    fuze = mot('FUZE', 178, 320, 160, espace=4)
    arena = mot('ARENA', 186, 320, 300, espace=2)
    hero = mot('HERO BATTLE', 54, 320, 371, espace=5, courbe=ruban_y)
    lettres = f'{fuze} {arena}'
    # le ruban (29/11, refait) : une bande cintrée de x 96 à 544, haute de 64, bordée de deux filets d'or ; à chaque bout
    # une queue plus sombre qui part derrière, fendue en V, et le pli (le plus sombre) qui relie la bande à la queue
    X0, X1, TOP, BOT = 96, 544, 316, 380

    def bord(y0, a=X0, b=X1, n=44):
        return [(a + (b - a) * i / n, y0 + ruban_y(a + (b - a) * i / n)[0]) for i in range(n + 1)]
    haut, bas = bord(TOP), bord(BOT)
    bande = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in haut) + ' L' + ' L'.join(
        f'{x:.1f},{y:.1f}' for x, y in reversed(bas)) + ' Z'
    ligne_h = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in bord(TOP + 7, X0 + 6, X1 - 6))
    ligne_b = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in bord(BOT - 7, X0 + 6, X1 - 6))
    reflet = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in bord(TOP + 12, X0 + 20, X1 - 20))
    yl, yr = ruban_y(X0)[0], ruban_y(X1)[0]
    queue_g = (f'M{X0 + 26},{TOP + 18 + yl:.0f} L{X0 - 62},{TOP + 26 + yl:.0f} L{X0 - 34},{TOP + 54 + yl:.0f} '
               f'L{X0 - 66},{BOT + 30 + yl:.0f} L{X0 + 26},{BOT + 24 + yl:.0f} Z')
    queue_d = (f'M{X1 - 26},{TOP + 18 + yr:.0f} L{X1 + 62},{TOP + 26 + yr:.0f} L{X1 + 34},{TOP + 54 + yr:.0f} '
               f'L{X1 + 66},{BOT + 30 + yr:.0f} L{X1 - 26},{BOT + 24 + yr:.0f} Z')
    pli_g = f'M{X0},{BOT + yl:.0f} L{X0 + 26},{BOT + 24 + yl:.0f} L{X0 + 26},{BOT + yl - 4:.0f} Z'
    pli_d = f'M{X1},{BOT + yr:.0f} L{X1 - 26},{BOT + 24 + yr:.0f} L{X1 - 26},{BOT + yr - 4:.0f} Z'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="4 0 {VW - 8} {VH}" role="img" aria-label="Fuze Arena – Hero Battle">
  <defs>
    <linearGradient id="lg-or" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="300">
      <stop offset="0" stop-color="#fffbe0"/><stop offset=".14" stop-color="#ffe886"/><stop offset=".3" stop-color="#ffc93a"/>
      <stop offset=".41" stop-color="#f39a1c"/><stop offset=".47" stop-color="#ffe27a"/><stop offset=".6" stop-color="#ffd24a"/>
      <stop offset=".72" stop-color="#ffb02c"/><stop offset=".88" stop-color="#ffd860"/><stop offset="1" stop-color="#e2801c"/>
    </linearGradient>
    <linearGradient id="lg-tranche" gradientUnits="userSpaceOnUse" x1="0" y1="60" x2="0" y2="320">
      <stop offset="0" stop-color="#9a3a1a"/><stop offset="1" stop-color="#5a1820"/>
    </linearGradient>
    <linearGradient id="lg-acier" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#aab6dc"/><stop offset=".45" stop-color="#eef3ff"/><stop offset=".55" stop-color="#c3cdea"/><stop offset="1" stop-color="#7d88b8"/>
    </linearGradient>
    <linearGradient id="lg-or-piece" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff0a0"/><stop offset=".45" stop-color="#ffc23a"/><stop offset="1" stop-color="#b8601a"/>
    </linearGradient>
    <linearGradient id="lg-cuir" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#5e1e2a"/><stop offset=".6" stop-color="#9a3a34"/><stop offset="1" stop-color="#6a2230"/>
    </linearGradient>
    <linearGradient id="lg-queue" gradientUnits="userSpaceOnUse" x1="0" y1="330" x2="0" y2="420">
      <stop offset="0" stop-color="#b8283a"/><stop offset="1" stop-color="#6e1222"/>
    </linearGradient>
    <linearGradient id="lg-rouge" gradientUnits="userSpaceOnUse" x1="0" y1="316" x2="0" y2="404">
      <stop offset="0" stop-color="#ff7a62"/><stop offset=".22" stop-color="#e4423e"/><stop offset=".7" stop-color="#b42632"/><stop offset="1" stop-color="#7e1426"/>
    </linearGradient>
    <linearGradient id="lg-reflet" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="170">
      <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <path id="lg-l" d="{lettres}"/>
    <clipPath id="lg-c0"><use href="#lg-l"/></clipPath>
    <clipPath id="lg-c1"><use href="#lg-l" transform="translate(-3,4)"/></clipPath>
    <clipPath id="lg-c2"><use href="#lg-l" transform="translate(3,-4)"/></clipPath>
  </defs>
  <g opacity=".2" transform="translate(-8,20)">
    <use href="#lg-l" fill="#0c0614" stroke="#0c0614" stroke-width="30" stroke-linejoin="round"/>
    <path d="{bande}" fill="#0c0614" stroke="#0c0614" stroke-width="18"/>
  </g>
  <g opacity=".28" transform="translate(-4,13)">
    <use href="#lg-l" fill="#0c0614" stroke="#0c0614" stroke-width="26" stroke-linejoin="round"/>
    <path d="{bande}" fill="#0c0614" stroke="#0c0614" stroke-width="12"/>
  </g>
  {epee('g', -1)}
  {epee('d', +1)}
  <use href="#lg-l" transform="translate(0,12)" fill="#2a1030" stroke="#2a1030" stroke-width="24" stroke-linejoin="round"/>
  <use href="#lg-l" fill="#2a1030" stroke="#2a1030" stroke-width="24" stroke-linejoin="round"/>
  <use href="#lg-l" transform="translate(0,11)" fill="url(#lg-tranche)"/>
  <use href="#lg-l" transform="translate(0,6)" fill="url(#lg-tranche)"/>
  <g clip-path="url(#lg-c0)">
    <rect width="{VW}" height="{VH}" fill="#fffbe6"/>
    <g clip-path="url(#lg-c1)">
      <rect width="{VW}" height="{VH}" fill="#c4581a"/>
      <use href="#lg-l" transform="translate(3,-4)" fill="url(#lg-or)"/>
    </g>
    <ellipse cx="350" cy="78" rx="250" ry="66" fill="url(#lg-reflet)" opacity=".7"/>
  </g>
  <path d="{queue_g}" fill="url(#lg-queue)" stroke="#2a1030" stroke-width="8" stroke-linejoin="round"/>
  <path d="{queue_d}" fill="url(#lg-queue)" stroke="#2a1030" stroke-width="8" stroke-linejoin="round"/>
  <path d="{pli_g}" fill="#4a0c1a" stroke="#2a1030" stroke-width="5" stroke-linejoin="round"/>
  <path d="{pli_d}" fill="#4a0c1a" stroke="#2a1030" stroke-width="5" stroke-linejoin="round"/>
  <path d="{bande}" fill="url(#lg-rouge)" stroke="#2a1030" stroke-width="8" stroke-linejoin="round"/>
  <path d="{reflet}" fill="none" stroke="#ff9a82" stroke-width="5" stroke-linecap="round" opacity=".45"/>
  <path d="{ligne_h}" fill="none" stroke="#ffd24a" stroke-width="4.5" stroke-linecap="round"/>
  <path d="{ligne_b}" fill="none" stroke="#c98a24" stroke-width="4.5" stroke-linecap="round"/>
  <path d="{hero}" fill="#2a1030" stroke="#2a1030" stroke-width="10" stroke-linejoin="round" transform="translate(0,3)"/>
  <path d="{hero}" fill="#fff3d6" stroke="#5e1418" stroke-width="5" stroke-linejoin="round" paint-order="stroke"/>
</svg>'''


if __name__ == '__main__':
    s = svg()
    p = os.path.join(U.PUBLIC, 'art', 'ui', 'logo.svg')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)
    print('public/art/ui/logo.svg', len(s), 'caractères')
