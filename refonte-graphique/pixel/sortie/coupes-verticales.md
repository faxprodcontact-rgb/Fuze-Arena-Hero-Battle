# Coupes verticales (export « jeu » des animations HD)

Bug vu par le propriétaire le 26/11/2026 (capture d'un vrai combat) : pendant la spéciale d'Ilian (vieux roi au trident),
un coin d'eau bleu claire coupé par un bord vertical bien droit restait devant le trident, et la vague qui s'écrase sur
la cible était coupée net à gauche. Avant/après dans le vrai jeu : `bug-ilian-avant-apres.png`.

**Cause.** L'export (`hd/anim/jeu_export.py`) découpe chaque image par colonnes : ce qui est à droite de `coupe` est posé
aux pieds de la vraie cible, ce qui est à droite de `depuis` vole. La vague d'Ilian traversait la colonne 190 : sa partie
gauche restait au roi, sa partie droite partait sur la cible. Plus la cible est loin, plus les deux morceaux s'écartent.

**Ce qui change dans l'export (pour tout le monde)**

- `calques=True` (clé de `JEU`, facultative) : le personnage n'est plus jamais coupé (arme comprise), les effets partent
  par morceaux entiers (pixels qui se touchent), et ce que le personnage cachait d'un effet qui part est complété.
- `rase=True` : chaque image du projectile est repérée par son bout et par le sol (sa base reste au sol quand l'image
  change ; avant, une vague de plusieurs images flottait).
- L'export écrit `ATTENTION … tranche un dessin sur N rangées` dès qu'une coupe traverse un dessin (≥ 8 rangées, hors
  contour sombre, hors corps à corps et jets) : le bug ne peut plus revenir sans prévenir.
- Contrôle : `python3 refonte-graphique/pixel/hd/anim/controle_coupes.py [--calcul]` → planches « comme au combat »
  dans `controle-speciales/` (cible proche en haut, cible au fond en bas, cadre rouge = suspect) et la liste ci-dessous.
- Jeu (`src/game/hd-fight.ts`) : au corps à corps contre une cible large (crabe, araignée, boss), ce qui est posé sur la
  1re cible est décalé de la même distance que le lanceur (avant : l'arme coupée ne se recollait pas). Un jet (`rayon`)
  s'étire jusqu'à ×6 (au lieu de ×3) : vers le rang du fond, il s'arrêtait en chemin depuis l'écart du 26/11.

**Corrections (seulement les `JEU` des build.py ; dessins et GIF inchangés)**

| personnage | animation | avant | correction |
|---|---|---|---|
| Ilian | spéciale | vague coupée à 190 : coin bleu devant le trident, vague tranchée sur la cible | la vague, une fois haute, court au ras du sol jusqu'à la vraie cible (`tir`, `rase`, images 4-5) et s'y écrase entière (`calques`) |
| oni-brute | spéciale | ligne de feu coupée à 257, flammes laissées au lanceur | la ligne de feu court au sol jusqu'à la cible (`tir`, `rase`), puis y flambe entière |
| canonnier | spéciale | gerbes de glace coupées à 213-218 | les gerbes courent au sol jusqu'à la cible (`tir`, `rase`), la fumée reste au canon |
| naga-bouclier | spéciale | ligne de pics coupée à 133 | la ligne entière sort de terre devant la cible (`calques`) |
| araignée cuirassée | spéciale | cristaux coupés à 153 | ligne de cristaux entière devant la cible (`calques`) |
| golem de lave | spéciale | jets de lave coupés à 259 | fissure et jets entiers devant la cible (`calques`) |
| Barzul | spéciale | traînée d'un boulet coupée à 180 | boulets entiers (`calques`, coupe 120) |
| dragon | spéciale | un météore coupé à 377 | météores entiers (`calques`, coupe 355) |
| Kael | spéciale | mur de flammes tranché à 153, traînée laissée au sol | le mur part entier avec sa traînée (`calques`, depuis 126) |
| Sable | spéciale ; attaque | crinière du lion de feu laissée au bâton ; traînée du lancer coupée | le lion part entier (`calques`) ; depuis 142 |
| crabe géant | spéciale | jet d'eau coupé à 200 | vague entière (`calques`, coupe 160) |
| sorcier-oni, Ysolde, Orin | spéciale | une boule de feu / des rubans / le souffle coupés au départ | morceaux entiers (`calques` ; Orin depuis 165) |
| Aldric | spéciale | traînée de la boule de feu coupée à 162 | depuis 142 (entre le pied et la boule) |
| Velith | spéciale | petit cristal du poing coupé en deux à 170 | colonne 176 (entre ce cristal et le premier pic) |
| Tessa | attaque | lueur de la corde coupée à 127 | depuis 130 |
| Méduse | attaque | griffe coupée dans la main à l'image 3 | elle vole dès l'image 4 |
| gorille guerrier | spéciale | onde de poussière en `rayon` : coupée à 166, étirée, elle s'arrêtait en chemin | elle court au ras du sol jusqu'à la cible (`tir`, `rase`, `calques`) |
| Tybalt | spéciale (jet) | flamme tranchée à 147 | coupée à 144, là où elle est la plus fine |
| Lenore, cyclope (spéciales sur le rang de devant) et 25 corps à corps | attaque / spéciale | l'arme et les effets coupés : recollés au coup sur la 1re cible, mais un bout d'arme ou d'explosion tranché sur la 2e cible, et décalé pendant la course | `calques` : l'arme reste toujours avec le personnage, les effets partent entiers |

Corps à corps passés en `calques` : arachne, araignée bondissante, araignée cuirassée, Auriel, Bérold, corbeau-tengu,
Corvin, crabe géant, cyclope, diablotin, Eldra, gorille guerrier, homme-poisson, Ilian, Kesha, Lenore, Lilou,
lutin de magma, matelot, Mira, naga-bouclier, oni-brute, serpent guerrier, singe voleur, Solenn, Tybalt, Velith.

**Laissés tels quels (voulus)**

- Les jets (`rayon` : moine-tengu, salamandre, Tybalt, Méduse, prêtresse serpent) sont coupés exprès à la bouche : le jeu étire le
  jet depuis ce point jusqu'à la cible.
- Garvin (attaque, image 5) : corps à corps recollé au coup ; pas touché, un autre agent le redessine.

<!-- liste automatique (controle_coupes.py) : ne pas écrire sous cette ligne -->

## Liste automatique

Rangées tranchées : au moins 8 rangées de suite où deux morceaux d'une même image (personnage / sur la cible / projectile) se touchent bord à bord sur la même colonne, hors contour sombre. Au corps à corps, le jeu recolle les morceaux au moment du coup (listés à part).

### Sur les planches exportées (public/art/hd + hd-meta.ts)

Tirs, sorts, jets :

- aucun

Corps à corps (recollé au coup) :

| personnage | animation | genre | image | morceau | rangées |
|---|---|---|---|---|---|
| garvin | attaque | melee | 5 | cible | 13 |

### En refaisant la découpe des build.py (--calcul)

Tirs, sorts, jets :

| personnage | animation | genre | image | morceau | rangées |
|---|---|---|---|---|---|
| moine-tengu | speciale | rayon | 7 | depuis=163 | 12 |
| salamandre | speciale | rayon | 4 | depuis=150 | 11 |
| salamandre | speciale | rayon | 5 | depuis=150 | 10 |
| salamandre | speciale | rayon | 6 | depuis=150 | 11 |
| salamandre | speciale | rayon | 7 | depuis=150 | 8 |

Corps à corps (recollé au coup) :

| personnage | animation | genre | image | morceau | rangées |
|---|---|---|---|---|---|
| garvin | attaque | melee | 5 | coupe=206 | 13 |

