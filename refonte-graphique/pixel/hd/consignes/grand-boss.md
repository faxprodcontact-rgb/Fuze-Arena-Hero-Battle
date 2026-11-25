# Consigne commune : dessiner un GRAND BOSS HD (« big boss »)

Demande du propriétaire (25/11/2026) : « quelques boss en beaucoup plus gros, des big boss », comme proposé quand on a
décidé les clans : **4 grands boss, un par élément**, beaucoup plus grands que les héros, très spectaculaires, sans
héros derrière (ce ne sont pas des chefs de clan). Ils serviront aux combats de boss (boss du jour, boss de guilde) et
aux fins de région.

| élément | boss (idée, à rendre original) |
|---|---|
| feu | un dragon de lave et d'obsidienne, ailes repliées, gueule rougeoyante |
| eau | un léviathan / kraken des abysses qui sort de l'eau, tentacules |
| terre | un titan de pierre ancien couvert de mousse et de cristaux |
| vent | un oiseau-tempête géant (plumes, nuages, éclairs en courbes) |

## Qualité et règles
- Même qualité, même style, même finesse de pixel que les 36 héros et 24 monstres HD : lire
  `refonte-graphique/pixel/hd/GUIDE.md` en entier, l'en-tête de `hd.py`, et étudier 2 héros + 2 monstres validés
  (`python3 hd.py voir <nom>`, `sortie/<nom>-net.png`, `-grand.png`, `-jeu.png`).
- Même pixel que les autres (pas de dessin agrandi) : c'est la TAILLE qui change. Environ **2 fois la hauteur d'un
  héros** (≈ 180–210 px du sol au sommet) et large ; il occupe tout le côté ennemi (5 places) à lui seul. Vue de 3/4
  tournée vers la DROITE (le jeu retourne les ennemis), une seule lumière en haut à droite, contour unique ajouté par
  l'outil, rampes de couleurs décalées en teinte, pas de noir à l'intérieur (gorge rouge sombre), pas de rayures ni de
  rayons répétés, signes inventés et jamais de lettres, ce qui pend tombe avec la gravité, posé au sol (le léviathan
  sort d'une flaque/d'un trou d'eau posé au sol), aucun effet de sort sur le dessin fixe.
- Il doit se lire comme un **boss** au premier coup d'œil : silhouette forte et reconnaissable en petit, détails riches
  en grand, une « zone forte » (la tête) bien lisible.

## Outils
`hd.py` travaille aujourd'hui sur une case de 128 × 120 (sol en 64, 116). Le pilote ajoute, SANS rien changer pour les
60 personnages existants (vérifier : mêmes images `voir` / `jeu` qu'avant pour au moins 4 héros et 4 monstres, md5),
la possibilité d'une case plus grande déclarée dans le fichier (par exemple une ligne `cadre: 256 240` et le `sol`
correspondant), et les contrôles adaptés (taille, bords). Les contrôles propres aux héros (hauteur 88–104, part de la
tête) ne s'appliquent pas aux boss.

## Fichiers
- `refonte-graphique/pixel/hd/boss/<nom>.txt` (`id: boss-<element>`), notes en français en tête (créature, pose,
  tête, détails signature, palette), `sol`, `tete`, `souffle`, `cligne`, palette, calques.
- Brouillons uniquement dans `<BROUILLON>/boss-<nom>/`. Ne rien modifier d'autre (sauf `hd.py` pour le pilote, avec la
  vérification ci-dessus). Pas de commit.
- Au moins 4 relectures (grand, taille du jeu, zooms tête / pattes / ailes, comparaison avec les héros à côté).
  `controle` doit finir sans FAUTE. Montrer aussi le boss **à la taille du jeu à côté d'un héros et d'un monstre**,
  sur un fond de combat (`public/art/px/fonds/<clan>.webp`) pour juger l'échelle : `pixel/sortie/boss-<nom>-echelle.png`.
- Réponse finale courte, en français simple pour le propriétaire (ce qui est dessiné, les choix, ce qu'il doit
  regarder), puis une partie technique.
