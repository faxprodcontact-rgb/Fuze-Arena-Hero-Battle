"""Construction COMMUNE du visage des héros vectoriels (demande du propriétaire, 26/11/2026).

Le plus gros défaut relevé par le propriétaire : yeux, nez et bouche mal placés les uns par rapport aux autres
(nez dessiné de profil collé au bord de la joue alors que les yeux sont presque de face, œil du fond au mauvais
endroit, bouche décentrée). Ce module place les traits sur une SPHÈRE qui tourne : tout le visage tourne ensemble,
donc tout reste cohérent.

Usage dans le dessin d'un héros :

    from visage import placer, verifier, planche
    V = placer((x0, y0, x1, y1))      # boîte du visage (ovale de la face, SANS les cheveux ni les oreilles)
    V['oeil_proche']  -> (x, y, largeur)   # l'œil côté gauche de l'image (le plus large)
    V['oeil_fond']    -> (x, y, largeur)   # l'œil près du contour droit (plus étroit), JAMAIS coupé par le contour
    V['nez']          -> (x, y)            # racine/base du nez SUR la ligne médiane, entre les deux yeux
    V['bouche']       -> (x, y, largeur)   # centre de la bouche sur la ligne médiane, sous le nez
    V['mediane']      -> fonction y -> x   # la ligne médiane courbe du visage
    V['oreille']      -> (x, y)            # oreille proche (côté gauche), à hauteur des yeux

Le héros regarde vers la DROITE de l'image : on voit davantage sa joue gauche (côté gauche de l'image) ; l'œil
proche est à gauche et large, l'œil du fond est à droite, plus étroit ; la ligne médiane (nez, bouche, menton) est
décalée vers la droite. Le nez ne sort que très peu du contour (petit bout arrondi), il ne forme pas un profil.

Têtes d'animaux / museaux / becs / visages masqués vus de profil : `placer(..., tour=70)` ou plus → un seul œil
(oeil_fond vaut None) : c'est ce que veut le propriétaire (« enlever l'œil du fond »).

Contrôle (obligatoire avant de rendre un héros) :
    verifier(mesures, boite) -> liste de défauts (vide = bon), où mesures = les positions RÉELLES de ton dessin
    (centres des yeux et leurs largeurs, nez, bouche) ;
    planche(svg_tete, boite, sortie_png) -> image zoomée du visage avec la sphère, la médiane et la ligne des yeux.
"""
import math

# Réglages du style (chibi « interface », tête ×1,1 comme Kael)
TOUR = 18          # degrés : 3/4 léger, le visage se lit presque de face (comme les jeux de référence)
AZ_OEIL = 25       # écart angulaire des yeux par rapport à la médiane (sur la sphère)
Y_OEIL = 0.50      # ligne des yeux (fraction de la hauteur de la boîte du visage, depuis le haut)
Y_NEZ = 0.66       # base du nez
Y_BOUCHE = 0.80    # milieu de la bouche
L_OEIL = 0.20      # largeur d'un œil vu de face (fraction de la largeur du visage)
L_BOUCHE = 0.22    # largeur de la bouche vue de face


def placer(boite, tour=TOUR, az_oeil=AZ_OEIL, y_oeil=Y_OEIL, y_nez=Y_NEZ, y_bouche=Y_BOUCHE,
           l_oeil=L_OEIL, l_bouche=L_BOUCHE):
    x0, y0, x1, y1 = boite
    w, h = x1 - x0, y1 - y0
    cx, r = x0 + w / 2, w / 2
    b = math.radians(tour)

    def X(az_deg, y_frac=0.5):
        # la sphère se rétrécit vers le haut et le bas (ellipse) : rayon à cette hauteur
        k = math.sqrt(max(0.0, 1 - ((y_frac - 0.5) / 0.62) ** 2))
        return cx + r * k * math.sin(math.radians(az_deg) + b)

    def larg(az_deg, base):
        return base * w * max(0.0, math.cos(math.radians(az_deg) + b)) ** 0.6   # chibi : l'œil du fond reste lisible

    def mediane(y):
        return X(0, (y - y0) / h)

    ye = y0 + y_oeil * h
    proche = (X(-az_oeil, y_oeil), ye, larg(-az_oeil, l_oeil))
    if tour >= 60:
        # tête de profil (animal, bec, museau) : l'œil unique se voit de côté, PAS écrasé ; il garde une bonne
        # taille (lisible au téléphone : au moins 0,24 de la largeur de la tête) et reste au-dessus de la racine
        # du museau / du bec, jamais collé au bord avant de la tête.
        proche = (min(proche[0], x0 + 0.78 * w), ye, max(l_oeil, 0.24) * w)
    fond_az = az_oeil + tour
    fond = None if fond_az >= 80 else (X(az_oeil, y_oeil), ye, larg(az_oeil, l_oeil))
    return {
        'boite': boite, 'tour': tour,
        'oeil_proche': proche,
        'oeil_fond': fond,
        'nez': (X(0, y_nez), y0 + y_nez * h),
        'bouche': (X(0, y_bouche), y0 + y_bouche * h, larg(0, l_bouche)),
        'menton': (X(0, 0.98), y0 + 0.98 * h),
        'oreille': (X(-90, y_oeil + 0.06), ye + 0.06 * h),
        'mediane': mediane,
    }


def verifier(mesures, boite, tol=0.06):
    """mesures : {'oeil_proche': (x, y, w), 'oeil_fond': (x, y, w) ou None, 'nez': (x, y), 'bouche': (x, y, w)}.
    Renvoie la liste des défauts (en français). tol = tolérance en fraction de la largeur du visage."""
    x0, y0, x1, y1 = boite
    w = x1 - x0
    d = []
    p, f, n, b = mesures['oeil_proche'], mesures.get('oeil_fond'), mesures['nez'], mesures['bouche']
    if f:
        if abs(p[1] - f[1]) > tol * w:
            d.append(f"les deux yeux ne sont pas sur la même ligne (écart {abs(p[1]-f[1]):.1f})")
        if not (p[0] < n[0] < f[0]):
            d.append("le nez n'est pas ENTRE les deux yeux (il doit être entre l'œil proche et l'œil du fond)")
        if f[2] > p[2] * 1.02:
            d.append("l'œil du fond est plus large que l'œil proche (il doit être un peu plus étroit)")
        if f[2] < p[2] * 0.7:
            d.append("l'œil du fond est trop écrasé (moins de 70 % de l'œil proche) : tourner moins la tête")
        if f[0] + f[2] / 2 > x1 - 0.02 * w:
            d.append("l'œil du fond touche ou dépasse le contour du visage")
        mid = (p[0] + f[0]) / 2
        if abs(n[0] - mid) > 0.18 * w:
            d.append("le nez est trop loin du milieu des deux yeux")
    if abs(b[0] - n[0]) > tol * w:
        d.append("la bouche n'est pas centrée sous le nez")
    if n[0] > x1 + 0.04 * w:
        d.append("le nez sort trop du contour (nez de profil sur un visage de 3/4)")
    if not (p[1] < n[1] < b[1]):
        d.append("ordre vertical faux : il faut yeux, puis nez, puis bouche")
    return d


def guide_svg(boite, tour=TOUR, couleur='#00e0ff'):
    """Calque SVG (à poser par-dessus la tête) : contour de la sphère, médiane, ligne des yeux, places idéales."""
    V = placer(boite, tour)
    x0, y0, x1, y1 = boite
    w, h = x1 - x0, y1 - y0
    pts = ' '.join(f"{V['mediane'](y0 + h * t / 20):.2f},{y0 + h * t / 20:.2f}" for t in range(21))
    s = [f'<g fill="none" stroke="{couleur}" stroke-width="{w/120:.2f}" opacity=".9">',
         f'<ellipse cx="{x0+w/2:.2f}" cy="{y0+h/2:.2f}" rx="{w/2:.2f}" ry="{h/2:.2f}" stroke-dasharray="{w/40:.2f}"/>',
         f'<polyline points="{pts}"/>',
         f'<line x1="{x0:.2f}" y1="{V["oeil_proche"][1]:.2f}" x2="{x1:.2f}" y2="{V["oeil_proche"][1]:.2f}"/>']
    for k in ('oeil_proche', 'oeil_fond'):
        e = V[k]
        if e:
            s.append(f'<ellipse cx="{e[0]:.2f}" cy="{e[1]:.2f}" rx="{e[2]/2:.2f}" ry="{e[2]/3:.2f}"/>')
    n, b = V['nez'], V['bouche']
    s.append(f'<circle cx="{n[0]:.2f}" cy="{n[1]:.2f}" r="{w/40:.2f}"/>')
    s.append(f'<line x1="{b[0]-b[2]/2:.2f}" y1="{b[1]:.2f}" x2="{b[0]+b[2]/2:.2f}" y2="{b[1]:.2f}"/>')
    s.append('</g>')
    return '\n'.join(s)


if __name__ == '__main__':
    # démonstration : visage de 100 × 110
    V = placer((0, 0, 100, 110))
    for k, v in V.items():
        if k != 'mediane':
            print(k, v)
    m = {'oeil_proche': V['oeil_proche'], 'oeil_fond': V['oeil_fond'], 'nez': V['nez'], 'bouche': V['bouche']}
    print('défauts :', verifier(m, (0, 0, 100, 110)) or 'aucun')
