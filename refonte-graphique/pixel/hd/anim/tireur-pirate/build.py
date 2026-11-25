# Tireuse pirate (mon-barzul-tireur, clan de Barzul, eau, tireur) : animations — pose (la tireuse calme et son ara),
# attaque de base « Coup de hanche » (elle abaisse le long mousquet à l'horizontale contre la hanche, le chien s'abat,
# le coup part : éclair, balle, fumée blanche ; le recul relève le canon jusqu'à la garde ; l'ara sursaute et crie),
# attaque spéciale « Lame de fond » (elle épaule et vise longuement, la joue contre la crosse ; l'eau de mer
# s'enroule autour de la bouche du canon et s'y engouffre, l'ara déploie ses ailes et crie ; le coup part : une
# grosse balle d'eau enroulée d'écume file à l'horizontale et éclate sur l'ennemi en une gerbe d'eau qui retombe en
# pluie ; le recul la repousse, le canon se cabre, puis elle redescend l'arme en garde).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/tireur-pirate/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-tireur-pirate-pose.gif, anim-tireur-pirate-attaque.gif,
# anim-tireur-pirate-speciale.gif, anim-tireur-pirate-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-tireur-pirate-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py zone x0 y0 x1 y1 [morceau]  → affiche un morceau de la découpe (pour les retouches)
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que le chef du clan, Barzul (../barzul/build.py),
# dont viennent la charpente (corps qui plie par rangées, rendu, fichiers), la fumée de poudre, l'éclair du coup, la
# balle, et les outils d'eau (gouttes, écume, nappes modelées par la lumière, volutes) avec leur palette de sept bleus :
#   - le dessin validé (../../monstres/tireur-pirate.txt) n'est PAS modifié : on le découpe en morceaux (tête et
#     chapeau avec les cheveux, l'ara en trois morceaux — tête, corps, queue —, les pans de l'écharpe, le bras
#     lointain, le reste du corps) et chaque image pose ces morceaux ;
#   - ce qui se déplace sans tourner est décalé au pixel près, ou plié par rangées / colonnes (jamais d'image lissée) ;
#   - le mousquet, qui tourne dans les attaques, est REDESSINÉ à chaque angle (canon d'acier, fût et crosse de bois,
#     bagues et plaque de couche en laiton, platine, chien et pontet) avec les tons du dessin ; les angles choisis sont
#     des pentes « propres » en pixel art (à plat, 1 pour 8, 1 pour 4) ; en garde, c'est le mousquet du dessin ;
#   - les bras qui bougent sont redessinés (manche bleue modelée par la lumière, revers d'or, jabot, mains dessinées à
#     la main plus bas) ; ce que le bras proche cachait (le flanc de la veste, l'écharpe, la basque) est repeint à la
#     main (RACCORD) ;
#   - l'ara : sa tête hoche (comme un vrai ara), sa queue se balance avec retard ; ses ailes ouvertes et son bec ouvert
#     sont dessinés à la main (grilles plus bas) ;
#   - les effets (fumée, feu de la poudre, balle, eau, écume, gouttes) ont leur petite palette, sans contour noir, en
#     formes rondes et courbes (jamais de rayons droits répétés) ;
#   - à la fin, chaque image peut recevoir des retouches pixel par pixel (RETOUCHES, plus bas).
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des dessins HD)

NAME = 'tireur-pirate'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = dict(SRC['palette'])
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (celle de Barzul, le chef)
# Les effets sont peints sur leurs propres toiles (derrière / devant) et rendus avec CETTE palette seule.
FXPAL = {
    # l'eau : les sept bleus communs aux héros d'eau (Kesha, Zaroth, Ilian, Barzul)
    'W': (255, 255, 255),   # écume blanche, coeur de la gerbe
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'B': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
    # la fumée de poudre : blanche, ombrée de gris lavande (jamais de noir)
    's': (250, 248, 244),   # fumée, lumière
    't': (226, 226, 234),   # fumée
    'u': (190, 192, 210),   # fumée, ombre
    'v': (148, 150, 176),   # fumée, creux
    # le feu de la poudre (étincelle, éclair du coup)
    'e': (255, 252, 228),   # coeur blanc
    'f': (255, 224, 110),   # jaune
    'g': (255, 158, 60),    # orange
    'h': (220, 88, 50),     # rouge orangé
    # la balle de plomb
    'i': (206, 212, 232),   # reflet
    'j': (112, 116, 150),   # plomb, lumière
    'k': (62, 58, 88),      # plomb
    'l': (36, 30, 54),      # plomb, ombre
    # la poussière soulevée au sol par le recul
    'm': (238, 226, 200),   # poussière, lumière
    'n': (206, 186, 150),   # poussière
    'o': (160, 136, 112),   # poussière, ombre
}
LIGHT = np.array([0.6, -0.8])
LN = LIGHT / np.linalg.norm(LIGHT)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du dessin est posé en SOL. De la place à droite : la balle file hors du
# cadre, la balle d'eau de la spéciale éclate sur l'ennemi. La pose seule se recadre en 128 × 120 (le format du jeu,
# sol en (64, 116)).
W, H = 344, 200
SOL = (96, 190)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = 262                                              # où se tient l'ennemi (toile)


def grid(rows):
    return np.array([list(r) for r in rows])


ORIG = grid(SRC['calques'][0][2])
MUSK = grid(SRC['calques'][1][2])                          # le mousquet du dessin et les deux mains (calque fixe)
GH, GW = ORIG.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


SKIN, HAIR, GOLD, COAT, SHIRT, RED, LEATHER = '123456', 'ABCD', 'ghijk', 'mnopq', 'stuw', 'EFGH', 'LMNOP'
PBLUE = 'abcd'                                             # les bleus vifs de l'ara

# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = ORIG.copy()
filled = rest != '.'


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


P = {}
# l'ara : la queue qui pend derrière le bras, le corps (aile repliée, pattes), la tête (et le bec clair, posé devant
# les cheveux)
P['ara_queue'] = take(filled & (XX <= 43) & (YY >= 57) & (YY <= 73) & ~((XX == 43) & (YY <= 59)))
P['ara_corps'] = take(filled & (XX >= 43) & (XX <= 51) & (YY >= 51) & (YY <= 60))
P['ara_tete'] = take(filled & (((XX >= 44) & (XX <= 51) & (YY >= 41) & (YY <= 50)) |
                               ((XX >= 52) & (XX <= 56) & (YY >= 42) & (YY <= 49) & isin(ORIG, 'tuw'))))
# les pans de l'écharpe rouge (noués sur la hanche lointaine, ils pendent)
P['echarpe'] = take(filled & isin(ORIG, RED) & (XX >= 76) & (YY >= 78) & (YY <= 87))
# le bras lointain (manche, revers d'or) : il est redessiné dans les attaques
P['brasL'] = take(filled & isin(ORIG, COAT + GOLD) & (((XX >= 81) & (YY >= 62) & (YY <= 69)) |
                                                    ((XX >= 80) & (YY >= 70) & (YY <= 77))))
# la tête : chapeau, visage, cheveux (les deux mèches qui tombent aux épaules), oreille et anneau
P['tete'] = take(filled & ((YY <= 57) & (XX >= 52) | ((YY <= 60) & (XX >= 52) & (XX <= 62) & isin(ORIG, HAIR))))
P['corps'] = rest.copy()
# sous le bec de l'ara (quand sa tête bouge) : les cheveux continuent
for (_x, _y) in zip(*np.nonzero((P['ara_tete'] != '.') & (XX >= 52))[::-1]):
    P['tete'][_y, _x] = 'B'
