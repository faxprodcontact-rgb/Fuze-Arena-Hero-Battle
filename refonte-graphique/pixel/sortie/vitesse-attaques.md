# Vitesse des attaques de base (personnages HD)

Mesuré par `npx tsx refonte-graphique/pixel/hd/anim/vitesse-attaques.ts` sur les vraies règles du jeu (`src/game/hd-tempo.ts`), à la vitesse ×1, sans la petite pause commune de 0,26 s entre deux coups. « Coup » = le moment où le chiffre s'affiche ; « fin » = quand le combat peut passer au coup suivant (course, vol et retour compris).

Cases : un personnage du premier rang qui frappe l'ennemi du premier rang (x 245 → 475) ; « du fond » : dernier rang contre dernier rang (x 82 → 638). Grand boss : depuis le milieu (x 548).

Tempo commun (`EVEN`) : coup vers 0,44 s, fin vers 0,98 s ; aucune image sous 45 ms ; une attaque rapide est allongée au plus de ×1.25 ; vol d'un projectile entre 0,12 et 0,38 s. Les spéciales ne changent pas.

## Résumé

| | coup | fin |
|---|---|---|
| avant (premier rang) | 0,29 à 1,14 s (moyenne 0,55) | 0,82 à 2,12 s (moyenne 1,29) |
| après (premier rang) | 0,36 à 0,56 s (moyenne 0,44) | 0,76 à 0,98 s (moyenne 0,98) |
| avant (du fond) | 0,31 à 1,19 s (moyenne 0,70) | 0,93 à 2,20 s (moyenne 1,49) |
| après (du fond) | 0,42 à 0,74 s (moyenne 0,50) | 0,96 à 1,28 s (moyenne 0,99) |

## Chaque personnage (secondes)

| personnage | id | sorte | attaque | avant : coup / fin | après : coup / fin | du fond, après | spéciale (images) |
|---|---|---|---|---|---|---|---|
| garvin | `knights-8` | héros | corps à corps | 0,77 / **2,12** | 0,44 / **0,98** | 0,44 / 0,98 | 2,30 |
| auriel | `angels-10` | héros | corps à corps | 0,58 / **1,71** | 0,44 / **0,98** | 0,44 / 0,98 | 2,58 |
| cyclope | `myths-3` | héros | corps à corps | 0,67 / **1,54** | 0,44 / **0,98** | 0,49 / 0,98 | 1,90 |
| zaroth | `demons-8` | héros | tir | 0,84 / **1,50** | 0,50 / **0,98** | 0,74 / 1,09 | 2,16 |
| ilian | `angels-2` | héros | corps à corps | 0,40 / **1,44** | 0,44 / **0,98** | 0,44 / 0,98 | 1,91 |
| kael | `assassins-2` | héros | corps à corps | 0,48 / **1,44** | 0,44 / **0,98** | 0,44 / 0,98 | 2,05 |
| lenore | `knights-9` | héros | corps à corps | 0,43 / **1,39** | 0,44 / **0,98** | 0,44 / 0,98 | 2,02 |
| velith | `demons-9` | héros | corps à corps | 0,47 / **1,38** | 0,44 / **0,98** | 0,44 / 0,98 | 2,56 |
| mira | `mages-2` | héros | corps à corps | 0,48 / **1,37** | 0,44 / **0,98** | 0,44 / 0,98 | 2,26 |
| berold | `knights-1` | héros | corps à corps | 0,42 / **1,37** | 0,44 / **0,98** | 0,44 / 0,98 | 2,00 |
| arcan | `mages-7` | héros | tir | 0,74 / **1,37** | 0,45 / **0,98** | 0,69 / 1,02 | 2,18 |
| orin | `mages-3` | héros | tir | 0,79 / **1,36** | 0,49 / **0,98** | 0,61 / 0,98 | 1,98 |
| nerith | `demons-12` | héros | tir | 0,60 / **1,34** | 0,44 / **0,98** | 0,63 / 1,01 | 1,85 |
| rook | `assassins-5` | héros | tir | 0,71 / **1,31** | 0,44 / **0,98** | 0,63 / 0,98 | 2,02 |
| solenn | `angels-7` | héros | corps à corps | 0,50 / **1,31** | 0,44 / **0,98** | 0,44 / 0,98 | 1,92 |
| arachne | `myths-10` | héros | corps à corps | 0,41 / **1,29** | 0,44 / **0,98** | 0,44 / 0,98 | 1,75 |
| sable | `assassins-3` | héros | tir | 0,44 / **1,28** | 0,44 / **0,98** | 0,52 / 1,28 | 1,55 |
| corvin | `assassins-7` | héros | corps à corps | 0,34 / **1,28** | 0,42 / **0,98** | 0,42 / 0,98 | 2,01 |
| celia | `angels-1` | héros | tir | 0,49 / **1,26** | 0,44 / **0,98** | 0,45 / 0,98 | 2,02 |
| barzul | `demons-3` | héros | tir | 0,61 / **1,24** | 0,44 / **0,98** | 0,47 / 0,98 | 1,92 |
| aldric | `knights-3` | héros | tir | 0,46 / **1,24** | 0,44 / **0,98** | 0,52 / 0,99 | 1,69 |
| eldra | `mages-8` | héros | corps à corps | 0,35 / **1,23** | 0,44 / **0,98** | 0,44 / 0,98 | 1,51 |
| minotaure | `myths-6` | héros | tir | 0,60 / **1,22** | 0,44 / **0,98** | 0,58 / 0,98 | 2,08 |
| isis | `myths-9` | héros | tir | 0,48 / **1,21** | 0,44 / **0,98** | 0,44 / 0,98 | 1,75 |
| gabryel | `angels-11` | héros | tir | 0,70 / **1,18** | 0,44 / **0,98** | 0,67 / 0,98 | 1,93 |
| zephyre | `assassins-11` | héros | tir | 0,47 / **1,16** | 0,44 / **0,98** | 0,56 / 1,25 | 1,55 |
| elyon | `angels-6` | héros | tir | 0,46 / **1,15** | 0,44 / **0,98** | 0,45 / 0,98 | 1,72 |
| anubis | `myths-7` | héros | tir | 0,63 / **1,14** | 0,44 / **0,98** | 0,60 / 0,98 | 2,10 |
| tessa | `mages-4` | héros | tir | 0,48 / **1,12** | 0,44 / **0,98** | 0,44 / 0,98 | 1,91 |
| lilou | `demons-4` | héros | corps à corps | 0,54 / **1,11** | 0,44 / **0,98** | 0,44 / 0,98 | 1,94 |
| ysolde | `knights-7` | héros | tir | 0,53 / **1,11** | 0,44 / **0,98** | 0,57 / 0,98 | 1,72 |
| tybalt | `knights-5` | héros | corps à corps | 0,40 / **1,10** | 0,44 / **0,98** | 0,44 / 0,98 | 1,68 |
| kesha | `demons-5` | héros | corps à corps | 0,42 / **1,09** | 0,44 / **0,98** | 0,44 / 0,98 | 1,87 |
| myrr | `mages-11` | héros | tir | 0,53 / **1,06** | 0,44 / **0,98** | 0,57 / 0,98 | 2,13 |
| jinn | `assassins-9` | héros | tir | 0,46 / **1,01** | 0,44 / **0,98** | 0,53 / 0,98 | 1,61 |
| meduse | `myths-4` | héros | tir | 0,55 / **0,97** | 0,44 / **0,91** | 0,57 / 0,98 | 1,92 |
| golem-lave | `mon-kael-costaud` | monstre | corps à corps | 0,80 / **1,92** | 0,44 / **0,98** | 0,44 / 0,98 | 2,30 |
| araignee-cuirassee | `mon-arachne-costaud` | monstre | corps à corps | 0,66 / **1,87** | 0,44 / **0,98** | 0,44 / 0,98 | 2,05 |
| oni-brute | `mon-lenore-costaud` | monstre | corps à corps | 0,53 / **1,75** | 0,44 / **0,98** | 0,44 / 0,98 | 2,13 |
| moine-tengu | `mon-orin-costaud` | monstre | sort | 1,14 / **1,73** | 0,56 / **0,98** | 0,56 / 0,98 | 2,11 |
| gorille-guerrier | `mon-eldra-costaud` | monstre | corps à corps | 0,66 / **1,64** | 0,44 / **0,98** | 0,47 / 0,98 | 2,10 |
| naga-bouclier | `mon-meduse-costaud` | monstre | corps à corps | 0,52 / **1,43** | 0,44 / **0,98** | 0,44 / 0,98 | 2,25 |
| meduse-eclair | `mon-kesha-sorts` | monstre | tir | 0,64 / **1,41** | 0,44 / **0,98** | 0,60 / 0,99 | 2,21 |
| canonnier | `mon-barzul-costaud` | monstre | tir | 0,69 / **1,41** | 0,44 / **0,98** | 0,64 / 0,98 | 2,07 |
| crabe-geant | `mon-kesha-costaud` | monstre | corps à corps | 0,58 / **1,36** | 0,44 / **0,98** | 0,44 / 0,98 | 2,08 |
| tengu-eventail | `mon-orin-sorts` | monstre | tir | 0,73 / **1,34** | 0,44 / **0,98** | 0,64 / 0,98 | 2,07 |
| tireur-pirate | `mon-barzul-tireur` | monstre | tir | 0,59 / **1,24** | 0,44 / **0,98** | 0,48 / 0,98 | 2,04 |
| araignee-tisseuse | `mon-arachne-tisseuse` | monstre | tir | 0,60 / **1,20** | 0,44 / **0,98** | 0,61 / 0,98 | 1,78 |
| araignee-bondissante | `mon-arachne-rapide` | monstre | corps à corps | 0,43 / **1,11** | 0,44 / **0,98** | 0,44 / 1,01 | 1,60 |
| singe-chaman | `mon-eldra-sorts` | monstre | tir | 0,64 / **1,10** | 0,44 / **0,96** | 0,63 / 0,98 | 1,96 |
| lutin-magma | `mon-kael-rapide` | monstre | corps à corps | 0,45 / **1,09** | 0,44 / **0,98** | 0,44 / 1,02 | 1,75 |
| pretresse-serpent | `mon-meduse-sorts` | monstre | tir | 0,56 / **1,05** | 0,44 / **0,98** | 0,57 / 0,98 | 1,65 |
| salamandre | `mon-kael-tireur` | monstre | tir | 0,71 / **1,03** | 0,44 / **0,76** | 0,64 / 0,96 | 1,96 |
| sorcier-oni | `mon-lenore-sorts` | monstre | tir | 0,50 / **1,03** | 0,44 / **0,98** | 0,56 / 0,98 | 1,94 |
| matelot | `mon-barzul-rapide` | monstre | corps à corps | 0,40 / **1,00** | 0,44 / **0,98** | 0,44 / 0,98 | 1,60 |
| singe-voleur | `mon-eldra-rapide` | monstre | corps à corps | 0,42 / **1,00** | 0,44 / **0,98** | 0,44 / 0,98 | 1,53 |
| corbeau-tengu | `mon-orin-rapide` | monstre | corps à corps | 0,34 / **0,96** | 0,43 / **0,98** | 0,44 / 0,98 | 1,71 |
| serpent-guerrier | `mon-meduse-rapide` | monstre | corps à corps | 0,35 / **0,91** | 0,44 / **0,98** | 0,44 / 0,98 | 1,79 |
| diablotin | `mon-lenore-rapide` | monstre | corps à corps | 0,29 / **0,85** | 0,36 / **0,98** | 0,44 / 0,99 | 1,61 |
| homme-poisson | `mon-kesha-rapide` | monstre | corps à corps | 0,33 / **0,82** | 0,41 / **0,98** | 0,44 / 0,98 | 1,57 |
| titan | `boss-terre` | grand boss | sort | 0,83 / **1,70** | 0,44 / **0,98** | 0,44 / 0,98 | 2,57 |
| leviathan | `boss-eau` | grand boss | sort | 0,69 / **1,47** | 0,44 / **0,98** | 0,44 / 0,98 | 1,95 |
| oiseau-tempete | `boss-vent` | grand boss | tir | 0,59 / **1,39** | 0,44 / **0,98** | 0,44 / 0,98 | 2,12 |
| dragon | `boss-feu` | grand boss | sort | 0,61 / **1,35** | 0,44 / **0,98** | 0,44 / 0,98 | 2,33 |
