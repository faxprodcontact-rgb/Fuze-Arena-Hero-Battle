# Héros HD — guide de dessin (à lire en entier avant de dessiner)

Décision du propriétaire (23/11/2026) : refaire les 72 héros **100 fois plus beaux et détaillés**, en vrai pixel art
professionnel, dessiné **pixel par pixel**. Ce guide remplace, pour les héros HD, l'ancien style « encré » de
`../GUIDE.md` (trait noir autour de chaque morceau, formes géométriques posées l'une sur l'autre : **refusé**).

Ce que le propriétaire reproche aux anciens héros, et qu'il ne faut plus jamais voir :
- tous ont le **même buste** → chaque héros a **sa propre forme de corps** ;
- les têtes ont **la même forme et le même visage** → chaque héros a **sa tête** : un requin a une vraie tête de requin,
  un dragon une vraie tête de dragon, un taureau une vraie tête de taureau ; deux humains n'ont jamais le même visage ;
- membres **grossiers et lourds**, mains **en ronds** → des membres dessinés (attaches fines, muscles, coudes, genoux,
  poignets) et de **vraies mains** (doigts, pouce, phalanges) ;
- **formes simples posées l'une sur l'autre** → un dessin d'un seul tenant, comme un graphiste le ferait ;
- pas assez de détails → coutures, sangles, boucles, rivets, plis, écailles, gravures… lisibles, pas du bruit ;
- pose de face ou de profil → **une vraie pose de trois quarts**, tournée vers la droite (l'ennemi) ;
- il veut des héros **cohérents, différents et badass**.

## 1. Le format (outil : `hd.py`)

Un héros = `hd/<nom>.txt` (le nom de l'atelier, ex. `kesha`). Voir l'en-tête de `hd.py` pour le format exact :
`id`, `sol`, `tete`, `souffle`, `cligne`, `palette:` (une lettre = une couleur `#rrggbb`), puis un ou plusieurs
`calque:` (grilles de lettres de même taille, du fond vers le devant ; `.` = vide). Coordonnées : x de gauche à droite,
y de haut en bas, (0, 0) = coin haut-gauche de la grille.

- **Taille** : du haut de la tête au sol ≈ **96 px** (88 à 104 ; un nain peut être plus petit, un géant plus grand).
- **La place autour** : le point `sol` est posé en (64, 116) d'une image de 128 × 120. Le dessin peut donc aller de
  `sol.x − 62` à `sol.x + 61` en largeur et jusqu'à `sol.y − 114` en hauteur (arme levée, cornes, ailes). Rien sous la
  ligne du sol. `controle` vérifie que rien n'est coupé.
- **Tête** : 25 à 38 % de la hauteur (≈ 26 à 34 px de haut). Grosses têtes lisibles, mais pas de bébé.
- **Le contour noir est ajouté tout seul** autour de la silhouette entière (1 px, en dehors du dessin). Ne pas le
  dessiner. **À l'intérieur, jamais de trait noir** : les séparations se font avec des teintes plus foncées de la
  matière (le dessous du bras = la peau dans l'ombre, pas un trait). Le presque-noir est réservé aux pupilles, à
  l'intérieur d'une bouche ouverte, aux creux très profonds.
- `souffle: y` : au repos, tout ce qui est au-dessus de la ligne y monte d'un pixel (la ligne y−1 est doublée). La
  placer vers le milieu du torse (sous les pectoraux, au-dessus de la ceinture). `calque: arme fixe` = un calque qui ne
  bouge pas (une arme plantée au sol).
- `cligne:` : les lettres des yeux deviennent celles d'une paupière (image 6 sur 8). Les yeux doivent avoir leurs
  propres lettres (pas la même lettre que d'autres choses du dessin).

Outils (depuis `refonte-graphique/pixel/hd/`) :
- `python3 hd.py voir <nom>` → `sortie/<nom>-grand.png` (×8, règle en coordonnées de la grille, sol en vert, boîte de
  la tête en rouge), `-net.png` (×6 sans règle), `-jeu.png` (à la taille du jeu, sur le fond de combat), `-anim.png`.
- `python3 hd.py zone <nom> x0 y0 x1 y1` → le morceau de grille avec ses coordonnées, pour retoucher précisément.
- `python3 hd.py pose <nom> x y TEXTE` → réécrit des pixels d'une ligne.
- `python3 hd.py controle <nom>` → les contrôles automatiques. Il faut **zéro FAUTE**.
- On a le droit d'écrire un petit script Python pour poser une première ébauche (masses, symétries, dégradés), mais le
  résultat final doit être **retouché pixel par pixel** : lignes propres, grappes de couleur nettes, détails à la main.

## 2. La direction artistique

- **Pas de sort sur l'illustration** (décision du propriétaire, 24/11/2026) : ni boule d'eau, ni rayon, ni vague lancée
  par la main. Les sorts seront des effets du combat. Le héros tient son arme ou ses objets ; une main libre reste le
  long du corps ou dans un geste naturel.
- **Le nez** (reproché sur trois héroïnes) : en trois quarts, l'arête du nez se lit en une ligne claire côté lumière et
  une ombre douce dessous, la narine en un ou deux pixels. **Le bout du nez ne dépasse PAS du contour du visage** (il
  affleure le profil, au plus) : le propriétaire trouve que nos nez « vont souvent un peu trop loin » (24/11, Mira).
  Exception : vrais museaux, becs et nez de créature (tengu…).
  **À l'intérieur du visage aussi, rester discret** : l'arête claire sur 2 ou 3 pixels et une petite ombre sous le bout,
  jamais une longue ligne d'ombre en diagonale qui traverse la joue (« on voit trop la démarcation », 24/11, Mira). Pas de tache, pas de pixels au hasard.
- **Les yeux** : l'œil du fond est caché en partie DERRIÈRE l'arête du nez (de trois quarts, le nez passe devant lui),
  même forme que l'œil proche, sur la même ligne.
- **Poings et bras** (retours du propriétaire) : poing fermé = le pouce replié SOUS les autres doigts (on ne le voit
  pas en travers) ; le coude à bonne distance de la main (un vrai avant-bras, sinon effet « poignet cassé ») ; un
  manche tenu ressort des deux côtés de la main, bien droit, dans l'axe de l'arme.
- **Pas de trou** : aucun vide de fond entre deux morceaux qui se touchent (épaule, aile et corps, bouclier fermé).
- **Le corps reste cohérent avec la pose** : une carapace, un abdomen, une queue suivent la rotation du corps de trois
  quarts et sont attachés au bon endroit (pas d'espace vide entre deux morceaux qui se tiennent).

- **Pixel art de jeu mobile haut de gamme**, gros pixels francs, couleurs saturées, très lisible à la taille du jeu.
- **Une seule lumière, en haut à droite.** Les formes sont éclairées en haut à droite, ombrées en bas à gauche.
- **Gammes de couleurs décalées en teinte** : les ombres tirent vers le violet / bleu froid, les lumières vers le jaune
  / chaud (jamais une gamme obtenue en ajoutant juste du noir ou du blanc). 3 à 5 tons par matière. ≤ 40 couleurs.
- **Volumes** : on modèle chaque forme selon la lumière (pas de « pillow shading » = une ombre tout autour du bord,
  claire au milieu). Ombres portées douces entre les morceaux (le bras porte une ombre sur le torse, le menton sur le
  cou, le chapeau sur le front).
- **Lignes propres** : courbes en paliers réguliers (1-1-2-2-3…, jamais 1-3-1-2), pas de « jaggies », pas de pixels
  orphelins (un pixel seul d'une couleur = un reflet voulu, sinon du bruit). Pas de **banding** (deux lignes de tons
  parallèles qui suivent exactement le même bord).
- **Matières** différentes et reconnaissables : métal (reflets durs, éclat blanc), cuir (mat, coutures), tissu (plis),
  peau (douce), écailles (motif régulier mais pas mécanique), fourrure (mèches en grappes), bois (veines), pierre.
- Leçons du propriétaire, toujours valables : **plus aucune rayure ni hachure, ni rayons répétés** ; des signes inventés,
  **jamais de lettres** ; tout est **posé au sol** ; de l'air autour du sujet ; rien devant le visage.

## 3. La pose de trois quarts (tournée vers la droite, vers l'ennemi)

- Le corps est tourné à environ 45° vers la droite : on voit la poitrine ET le côté droit du personnage. « Main
  droite », « œil gauche » = ceux **du personnage**. Le côté droit du personnage est le plus proche de nous (à gauche
  de l'image) ; son côté gauche est le plus loin (à droite de l'image), raccourci.
- **Épaules** : l'épaule proche est plus large et plus basse dans l'image, l'épaule lointaine plus étroite. Le milieu
  du torse (sternum, boutons, fermeture) est décalé vers la droite de l'image.
- **Tête** : le visage regarde vers la droite. L'œil lointain est plus petit et proche du bord du visage ; le nez (ou
  le museau) dépasse du contour à droite ; l'oreille visible est celle de gauche de l'image (côté proche) ; la mâchoire
  dessine un angle.
- **Bras** : le haut du bras proche passe **devant** le torse ; le bras lointain est **derrière** le torse (on n'en voit
  qu'une partie). Les coudes et poignets sont marqués, les avant-bras s'affinent vers le poignet.
- **Jambes** : posture de combat avec un appui (le poids sur une jambe, l'autre en avant ou en arrière). La plupart des
  héros ont un écart **modéré** ; quelques-uns seulement une fente large. Le pied proche est tourné vers la droite en
  trois quarts, le pied lointain en partie caché.
- **Premier et second plan** : le cou est court et en partie caché par la mâchoire ; un bouclier tenu par le bras
  lointain a son bord le plus loin qui passe derrière ; une cape passe derrière les jambes ; une arme tenue par la main
  proche passe devant le corps, jamais devant le visage.

## 4. Identité : chaque héros est unique

- **Corps** : choisir une morphologie qui raconte le personnage, différente de ses voisins : colosse (épaules énormes,
  bras épais, petites jambes solides), athlète, élancé, sec et nerveux, trapu (nain), massif et lourd, frêle et vieux,
  silhouette féminine fine ou puissante, corps animal (queue, pattes de bouc, tentacules…). La **silhouette seule**
  (en noir) doit permettre de le reconnaître.
- **Tête** : dessinée pour ce personnage. Les têtes animales suivent la vraie anatomie de l'animal, adaptée en héros :
  - requin : museau pointu qui avance, petits yeux noirs ronds placés sur le côté, fentes des branchies, gueule qui
    s'ouvre sous le museau avec des rangées de dents triangulaires, nageoire dorsale ; peau gris-bleu, ventre clair ;
  - dragon : long museau avec naseaux, arcade sourcilière marquée au-dessus d'un œil de reptile (pupille fendue),
    cornes ou bois, écailles (petites sur le museau, plus grandes sur le crâne), barbillons, crocs ;
  - taureau : large mufle carré avec deux grands naseaux, anneau, front bombé et poilu, cornes épaisses à la base qui
    s'affinent, oreilles à l'horizontale, cou énorme qui fait corps avec les épaules ;
  - humain : forme du visage, âge, nez, yeux, sourcils, bouche, cicatrices, coiffure et pilosité propres à chacun.
- **Expression badass** : regard dur, mâchoire serrée ou rictus, crocs, sourcils froncés, cicatrice… selon le caractère.
- **Accessoires** : l'arme et les objets du personnage sont dessinés avec soin (forme lisible de loin, détails de
  près) et tenus pour de vrai (les doigts se referment autour du manche, le pouce par-dessus).

## 5. Les mains, les pieds, les détails

- Une main mesure environ la longueur du visage (7 à 10 px). **Poing fermé** : 4 doigts repliés qui forment des
  phalanges, le pouce par-dessus, une ombre sous les doigts. **Main ouverte** : la paume, 4 doigts (ou 3 dans l'ombre)
  et le pouce écartés, les griffes si c'est une bête. **Main qui tient** : les doigts passent devant le manche, le
  manche ressort des deux côtés.
- Pieds : bottes, sandales, sabots, pattes griffues… avec semelle et épaisseur, posés à plat sur le sol.
- Détails : coutures, rivets, boucles, plis, sangles, motifs gravés, cicatrices, écailles, mèches. Ils doivent rester
  lisibles à la taille du jeu (regarder `-jeu.png`) : mieux vaut 5 beaux détails que 50 pixels de bruit.

## 6. Méthode (chaque héros)

1. Regarder l'ancienne image peinte du personnage (`public/art/p/<id>.webp`, l'idée d'origine) et la note en tête de
   l'ancien fichier `../persos/<nom>.py` (thème, arme, pose). Garder le thème, les couleurs principales et l'arme ;
   améliorer tout le reste.
2. Choisir : morphologie, pose de trois quarts, ce qui le rend unique et badass. Écrire ces choix en notes (`#`) en
   tête du fichier.
3. Ébaucher la silhouette (une ou deux couleurs), la regarder en petit (`-jeu.png`) : doit être lisible et différente.
4. Poser les grandes masses de couleur, puis la lumière et les ombres, puis les détails, puis le nettoyage des lignes.
5. **Se relire plusieurs fois** : `voir`, regarder `-grand.png` ET `-jeu.png`, corriger, recommencer. Vérifier la liste
   ci-dessous à chaque passage. `controle` : zéro FAUTE.

## 7. Liste de contrôle (avant de dire « fini »)

- [ ] Pose de trois quarts vers la droite, appui clair, posture de combat badass.
- [ ] Corps à lui (pas le buste standard), silhouette reconnaissable en noir.
- [ ] Tête propre au personnage (vraie tête d'animal si c'est une bête), expression forte, rien devant le visage.
- [ ] Mains avec doigts et pouce, qui tiennent vraiment ; pieds posés à plat sur le sol.
- [ ] Pas de trait noir à l'intérieur ; ombres colorées ; une lumière en haut à droite ; pas de pillow shading.
- [ ] Lignes propres, pas de pixels orphelins non voulus, pas de banding, pas de rayures ni de hachures.
- [ ] Premier / second plan cohérents (bras proche devant, bras lointain derrière, cou court, bouclier, cape).
- [ ] Détails nombreux mais lisibles à la taille du jeu.
- [ ] Respiration (souffle) et clignement qui marchent (`-anim.png`).
- [ ] `controle` sans FAUTE.
