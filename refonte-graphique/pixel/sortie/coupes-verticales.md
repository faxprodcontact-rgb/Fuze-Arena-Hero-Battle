# Coupes verticales (export jeu)

<!-- liste automatique (controle_coupes.py) : ne pas écrire sous cette ligne -->

## Liste automatique

Rangées tranchées : au moins 8 rangées de suite où deux morceaux d'une même image (personnage / sur la cible / projectile) se touchent bord à bord sur la même colonne, hors contour sombre. Au corps à corps, le jeu recolle les morceaux au moment du coup (listés à part).

### Sur les planches exportées (public/art/hd + hd-meta.ts)

Tirs, sorts, jets :

| personnage | animation | genre | image | morceau | rangées |
|---|---|---|---|---|---|
| aldric | speciale | tir | 6 | projectile | 10 |
| meduse | attaque | tir | 3 | projectile | 8 |
| orin | speciale | tir | 8 | projectile | 8 |
| tessa | attaque | tir | 2 | projectile | 13 |

Corps à corps (recollé au coup) :

- aucun

### En refaisant la découpe des build.py (--calcul)

Tirs, sorts, jets :

| personnage | animation | genre | image | morceau | rangées |
|---|---|---|---|---|---|
| aldric | speciale | tir | 6 | depuis=162 | 10 |
| gorille-guerrier | speciale | rayon | 10 | depuis=166 | 12 |
| gorille-guerrier | speciale | rayon | 11 | depuis=166 | 16 |
| meduse | attaque | tir | 3 | depuis=130 | 8 |
| moine-tengu | speciale | rayon | 7 | depuis=163 | 12 |
| orin | speciale | tir | 8 | depuis=196 | 8 |
| salamandre | speciale | rayon | 4 | depuis=150 | 11 |
| salamandre | speciale | rayon | 5 | depuis=150 | 10 |
| salamandre | speciale | rayon | 6 | depuis=150 | 11 |
| salamandre | speciale | rayon | 7 | depuis=150 | 8 |
| tessa | attaque | tir | 2 | depuis=127 | 13 |

Corps à corps (recollé au coup) :

| personnage | animation | genre | image | morceau | rangées |
|---|---|---|---|---|---|
| garvin | attaque | melee | 5 | coupe=206 | 13 |

