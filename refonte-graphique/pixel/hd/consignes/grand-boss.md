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
`hd.py` travaille sur une case de 128 × 120 (sol en 64, 116) pour les héros et monstres. **Pour un grand boss (fait le
25/11 par le pilote, avec le dragon de feu)** : le fichier déclare sa case, sur une ligne avant `palette:` :

    cadre: 256 240          ← largeur hauteur ; le point « sol » tombe en (128, 236) (milieu, 4 px au-dessus du bas)
    sol: 128 236            ← les grilles font 256 × 240 : coordonnées de la grille = coordonnées de la case
    tete: x0 y0 x1 y1       ← la boîte du crâne et des mâchoires (sans les cornes)

(`cadre: 256 240 x y` place le sol ailleurs si besoin.) Sans `cadre:`, rien ne change : les 60 héros et monstres donnent
exactement les mêmes images qu'avant (vérifié au md5 : les 8 images et le `controle` des 60, les sorties `voir` de 4
héros et 4 monstres). Avec `cadre:`, `voir`, `zone`, `pose`, `planche` marchent pareil ; `controle` vérifie les bords de
la grande case et les mesures du boss (hauteur du SOMMET au sol 170 à 215 px, largeur ≥ 150, tête ≥ 30 × 30) au lieu
de celles des héros. Les « pixels isolés » se comptent sur ~32 000 pixels : au-delà de 40, les regarder (éclats voulus
sur l'obsidienne, l'oeil, les crocs) mais ce n'est pas une faute. Pour un script d'animation : `hd.case(h)` donne
(largeur, hauteur, (x, y) du sol).

L'image d'échelle demandée : `python3 hd.py echelle boss/<nom>.txt <clan du fond> <héros> <monstre>`
(ex. `python3 hd.py echelle boss/dragon.txt kael kael monstres/golem-lave`) → `pixel/sortie/boss-<nom>-echelle.png` :
le boss seul au milieu du côté ennemi (rang du milieu, retourné comme dans le jeu), un héros et un monstre du côté des
héros, sur `public/art/px/fonds/<clan>.webp`, 1 pixel du dessin = 1 pixel du fond, agrandi × 2.

Méthode qui a marché pour le dragon (≈ 32 000 pixels : trop pour tout taper) : un petit script dans le brouillon pose
les masses (ellipses, polygones, tubes), les éclaire (lumière en haut à droite, 3 à 7 tons par matière), pose les
plaques (Voronoï à bords ondulés, fentes seulement dans la lumière), les plis, les veines ; puis la tête (la zone forte)
est construite en PLANS à plat (dessus du museau éclairé, côté, lèvre, gueule, orbite) et ses détails posés au pixel
(oeil, crocs triangulaires, narine, larme, goutte) ; les pieds sont faits doigt par doigt avec des griffes recourbées
qui touchent le sol ; les doigts des ailes sont tracés rangée par rangée (une ligne nette, pas un tube) ; enfin un
nettoyage des orphelins et un fil de lumière sur les bords haut et droit. Relire à chaque étape avec des zooms
(`zone`, recadrages × 6) et l'image d'échelle, pas seulement `-net.png`.

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
