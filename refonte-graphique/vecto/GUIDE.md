# Personnages vectoriels — guide de travail (à lire en premier)

But : redessiner par le code, un par un, les 144 personnages du jeu (dessins Hailuo de `public/art/p/`) dans le style
de Ruka la sirène (`demons-7.cjs`), puis les animer (repos + attaque). Le propriétaire vérifie lui-même chaque
personnage sur la page d'exemple ; on ne lance **ni dessinateurs en parallèle ni relecteur** (trop cher en crédits).
Pas encore branché dans le jeu : la page d'exemple sert de vitrine.

## Méthode économe (une conversation = un ou deux personnages)

1. Choisir le **suivant de la file** (plus bas). Regarder l'original une fois en petit :
   `refonte-graphique/vecto/originaux/<id>.jpg` (le cadre w × h du dessin = la taille de cette image).
2. **Décalquer, pas dessiner à l'œil** (demande du propriétaire : « à chaque fois fidèle », aussi précis que le deuxième
   renard). Il faut OpenCV (`pip install opencv-python-headless`).
   - **Silhouette exacte** : `python3 refonte-graphique/vecto/outils/silhouette.py <id> --apercu /tmp/s.png` écrit
     `silhouettes/<id>.json` (vérifier l'aperçu une fois : les trous entre les pattes doivent être gardés). Dans le fichier
     du personnage : `figure({ master: require('./silhouettes/<id>.json'), … })`. Chaque morceau est alors découpé dans
     la silhouette d'origine (contour et couleurs), dans son propre repère : il suffit de dessiner les morceaux un peu
     plus grands que l'original sur les bords, et le bord tombe pile. Un morceau `free: true` (lueur) n'est pas découpé.
   - **Pièces** : `python3 refonte-graphique/vecto/outils/zone.py <id> x,y [x,y…] --seuil 80 --boite x0,y0,x1,y1`
     donne les points de la zone entourée de trait noir qui contient le point (une plume, une fusée, un œil) ;
     `outils/contour.py` donne le bord extérieur d'une région.
   - **Formes communes** : `formes.cjs` (`sm`, `rib`, `glint`, `tooth`, `nest`, `rooted`) — ne plus les recopier.
   - **Région de la silhouette** : `python3 refonte-graphique/vecto/outils/decoupe.py <id> "x,y x,y …"` (la silhouette
     coupée par un polygone, pour un corps, une tête, un fond) ; `outils/encre.py` montre les traits noirs seuls.
   - **Décalquer le bord, ADAPTER l'intérieur** (refus du propriétaire, 23/11 : Ilian, Zeus, Eldra, Sable… « on dirait
     de la peinture », « trop recopié, pas adapté ») : la silhouette (master) et la place des pièces viennent de
     l'original, mais l'intérieur se **dessine** comme Rook (`assassins-5`) : chaque pièce (épaulière, poing, barbe,
     jupe, couronne) est une forme nette relevée à la main sur un gros plan quadrillé, peinte avec `cel()` (une ombre
     franche, un liseré clair), puis quelques détails dessinés (mèches en fuseaux, plis, muscles en creux doux).
     **Jamais** les taches d'ombre ni les reflets de l'original recopiés (`couleurs.py` ne sert plus qu'à relever des
     couleurs ou une grande zone simple, jamais à peindre). Les deux yeux d'un visage se bâtissent avec la même
     fonction (même forme, même trait de cils), le plus loin un peu plus petit. Modèle refait : `angels-2` (Ilian).
   - **Ce qui est difficile à découper** (ficelle, mousse, pattes qui se croisent, fond entre des fusées) : un morceau
     « fond » placé tout derrière, dont la forme est la silhouette coupée par une boîte (voir `parade-3`, `myths-10`,
     `angels-4` : `tailBase`, `legsBase`, `tentBase`), puis les morceaux dessinés par-dessus.
   - Le tracé intérieur (œil, bouche, dents, limites de couleur) se lit sur un gros plan quadrillé, zoom 5 :
     `python3 refonte-graphique/vecto/outils/zoom.py <id> x0 y0 x1 y1 5 /tmp/z.png` ; relever les vraies couleurs.
   - **Mesurer** : `node refonte-graphique/vecto/outils/ecart.cjs <id> /tmp/e.png` donne le recouvrement des silhouettes
     et une image (rouge = manque, bleu = dépasse). **Viser au moins 95 %** (une lueur transparente compte comme un
     manque : la regarder à l'œil). Puis comparer en « calque » le visage, les mains et l'objet tenu.
3. Écrire `refonte-graphique/vecto/<id>.cjs` en partant du fichier fait le plus proche (voir « Pièces à reprendre ») :
   copier sa structure, ses outils et ses dégradés, puis changer les formes. Ne pas tout réinventer.
4. Contrôle, dans cet ordre et sans multiplier les images :
   - `node refonte-graphique/vecto/outils/apercu.cjs <id> 3 x0 y0 x1 y1 /tmp/a.png calque` sur le visage, puis les mains ;
   - une fois, le personnage entier : `... apercu.cjs <id> 1 - - - - /tmp/a.png duo` ;
   - une planche d'animation : `node refonte-graphique/vecto/outils/anim.cjs <id> /tmp/anim.png` (zoom 0,5 par défaut).
   Passer la liste de contrôle (plus bas) en regardant ces images. Une seule passe de retouches, regroupées.
5. Ajouter le nom du monstre dans `MONSTER_NAMES` de `exemple.cjs` (les héros ont leur nom dans `heroes.ts`).
6. Page d'exemple : `node refonte-graphique/vecto/exemple.cjs /tmp/personnages.html --artifact`, puis la publier
   (outil Artifact) **sur la même adresse** : https://claude.ai/artifact/5qE3vDUzsMFMQVC4ywqLrK (passer `url`).
   La galerie montre tout seul tous les fichiers `<famille>-<n>.cjs` du dossier.
7. Enregistrer (commit + envoi). Donner le lien au propriétaire, en une phrase, et attendre son avis.

Coûts à éviter : grandes planches à chaque essai, images en grand de tout le personnage, relire de gros fichiers en
entier (lire seulement la partie utile : `grep -n` puis `sed -n`), agents en parallèle.

## Le fichier d'un personnage

`module.exports = { id, w, h, pad, foot: [x, y], svg: (anime = true) => figure({ w, h, pad, defs, style, parts, anime }) }`

- Coordonnées = pixels du dessin d'origine (le vectoriel se pose exactement dessus). `foot` = point au sol entre les
  pieds (sous un personnage qui vole : là où serait son ombre). `pad` = marge pour que l'animation ne soit pas coupée.
- `lib.cjs` : `figure()` dessine d'abord TOUTES les silhouettes en sombre et épais (**un seul contour** autour du
  personnage), puis les couleurs par-dessus. Un morceau = `{ id, d, body, cls?, shadow?, rim? }`, du fond vers le
  devant. Jamais de contour par morceau : une ombre douce (`shadow`) sépare deux morceaux, un filet (`rim`) seulement
  là où un morceau passe devant un autre de même matière. Pas de filtre SVG (trop lent animé).
- Lumière en haut à droite : reflets en haut/droite, ombres en bas/gauche, ombres portées décalées vers le bas-gauche.
- Animation (CSS dans `style`) : le **repos** tourne toujours, avec les propriétés `translate` / `rotate` / `scale`
  (pivots = vraies articulations, `transform-origin` en pixels du dessin), rythmes différents par morceau, `alternate`.
  L'**attaque** dure 0,75 s quand le `<svg>` racine reçoit la classe `atk` (`.atk .a-bras{animation:…}`), avec
  `transform` : élan (0–35 %), frappe (35–55 %), retour (55–100 %) qui retombe exactement sur la pose de repos.
  `assassins-5` montre comment l'attaque s'ajoute au repos sans à-coup (`animation-composition: replace, add`).

## Vocabulaire du propriétaire

- « Main droite », « œil gauche »… = **du personnage**, donc main droite = à GAUCHE de l'image quand on regarde.
- « Vers la droite » pour une rotation = dans le sens des aiguilles d'une montre.

## Liste de contrôle (en plus de `refonte-graphique/LISEZMOI.md`, section « Liste de contrôle de cohérence »)

Leçons de la première série (corrections demandées par le propriétaire ou le relecteur) :
- **Fidélité mesurée** : chaque personnage passe `outils/ecart.cjs` (≥ 95 %) avant d'être montré.
- **Fidèle ≠ recopié** : la fidélité porte sur la silhouette, les proportions et la place des pièces ; le rendu, lui,
  est toujours le style net du jeu. Une zone blanche ou une tache de l'original n'est pas à reprendre telle quelle.
- **Forme fidèle** : la tête et les pattes doivent avoir la forme de l'original (renard refusé une première fois :
  museau trop long, œil trop petit, mâchoire mal placée). Toujours comparer en « calque » sur la tête et les pattes.
- **Mains** : doigts courts et arrondis (jamais pointus, jamais des « orteils » en bosses), pouce bien distinct, la
  main **dans l'axe de l'avant-bras** (pas de poignet cassé à 90°), le poignet qui rentre dans la manche. Un objet
  tenu passe dans la main ; une flûte touche les lèvres.
- **Yeux** : les deux yeux du même dessin (l'œil du fond = celui du devant en miroir, ~0,8 fois plus étroit, iris de
  même taille). Personnage fier ou méchant : paupière du haut qui coupe l'iris, sourcils épais qui plongent vers le
  nez (sinon il a l'air content ou surpris).
- **Pas de traits parallèles** : ni stries dans les cheveux, les queues, les tentacules, les ailes, ni rangées de
  marques identiques ; préférer 1 ou 2 grands reflets en forme. Pas de rayons réguliers autour d'une étincelle.
- **Pas de trait noir à l'intérieur** (une rainure = un côté sombre + une arête claire).
- Ce qui fait le tour (ceinture, diadème, bandeau) va d'un bord à l'autre et suit la courbe du corps ou du crâne.
- Après tout déplacement d'un morceau, vérifier qu'aucun **trou sombre** n'apparaît entre deux morceaux.
- Une silhouette pleine et lisible à la taille du jeu (~70 px de haut) : dernière case de `anim.cjs`.

## Pièces à reprendre (où trouver ce qui est déjà réussi)

| Besoin | Fichier → fonctions |
|---|---|
| Courbe douce par des points | `knights-11.cjs` → `sm`, `taper` (aussi dans `bayou-4`, `glaces-4`, `assassins-12`) |
| Œil (iris, reflets, cils, clignement) | `demons-7.cjs` → `eye` ; regard dur : `mages-10.cjs` → `eye` (+ œil du fond en miroir) |
| Main ouverte, doigts repliés | `knights-11.cjs` → `fingerPts`, `crease`, morceaux `handR`, `fing1-4` |
| Poing, pivoter un morceau d'un bloc | `knights-11.cjs` → `handSil`, `HAND_ROT`, `handDefs` (poing `fistL`, `fk1-4`, `thumbL`) ; `assassins-12.cjs` → `fist` |
| Grandes mèches de cheveux | `demons-7.cjs` → `backLock`, morceaux `lockA-D` ; `mages-10.cjs` → `lock` |
| Diadème qui suit le crâne | `mages-10.cjs` → `bandPt`, `BAND` |
| Épée et traînée de lumière | `mages-10.cjs` → `bladeD`, `trailD`, `poseAt` |
| Ruban, voile, tentacule | `abysses-3.cjs` → `strip`, `veil` ; tentacules à ventouses : `angels-4.cjs` → `TENTS`, `tentBody` |
| Arme tenue à deux mains, qui pivote à l'épaule sans décoller le bras | `angels-4.cjs` → morceaux `staff`, `armL`, `handL` (pivot `staff` = l'épaule) |
| Écailles | `demons-7.cjs` → `scales` ; grosses écailles en rangées décalées : `parade-2.cjs` → `scales` |
| Plumes en faucille (queue de coq) | `epouvantails-1.cjs` → `quillPts`, `TAIL` (un dégradé par plume, de la racine à la pointe) |
| Plumes et ailes | `assassins-5.cjs` → `feather`, `quill`, `plume` (réutilisées par `<use>`, fichier léger) ; `glaces-4.cjs` → `feather`, `row`, `ruff` |
| Ailes translucides | `assassins-12.cjs` → morceaux `wingU`, `wingD` |
| Éclair tenu et sa lueur, couronne de laurier, regard en colère (paupière lourde) | `mages-9.cjs` → `boltBody`, `leafPt`, morceau `crown`, paupières dans `faceBody` |
| Flammes, lueur intérieure | `bayou-4.cjs` → `tongue`, `band`, `face` ; flamme tenue : `knights-11.cjs` (morceau `flame`) |
| Roche, lave, fissures | `knights-8.cjs` → `stone`, `crack`, `fissure`, `glowSteps` |
| Métal à rivets, dents, étincelle | `parade-1.cjs` → `stud`, `tooth`, `sparkBody` |
| Mousse, herbe, champignons | `ronciers-2.cjs` → morceaux `moss` (bord en brins), `capS`/`capB` |
| Gueule ouverte en coin vue de profil, crocs avec contour | `bayou-6.cjs` → `upAt`, `lowAt`, `toothD`, morceaux `teethT`, `teethB` |
| Fusée (tube, bagues dorées, pointe), queue enroulée | `parade-3.cjs` → `rocketGeo`, `rocketBody`, morceau `tail` (`rib` en spirale) |
| Grande épée sur un axe (lame, garde, poignée, pommeau), tranchants de feu | `assassins-2.cjs` → `SA`, `SB`, `sp`, `spa`, morceaux `blade`, `guard`, `grip` |
| Crinière de flammes (langues courbes, pas de rayons) | `assassins-2.cjs` → `TONGUES`, `fireBody` |
| Objet vivant qui flotte, lumière intérieure, glands | `parade-4.cjs` → `g-inner`, `faceBody`, `tasselBody`, groupe `a-root` |
| Nœuds de tissu, ficelle, pans de toile cousus | `epouvantails-3.cjs` → `bow`, `STR`, `kiteBody` |
| Pattes d'araignée (grosses pattes courbes à genou haut) | `myths-10.cjs` → `legPts`, `legD`, `legBody`, `FAR`, `NEAR` |
| Carapace à pics, pattes à griffes (le modèle de la méthode « décalque ») | `bayou-2.cjs` → `SHELL`, `LOWER`, `HEAD`, `spikeFace`, `claws` |
| Piquants en rangs (pointes relevées sur la silhouette), guirlande de feuilles, baies | `ronciers-3.cjs` → `TIPS`, `QUILLS`, `INNER`, `quillBody`, `ARC`, `LEAVES`, `BERRIES` |
| Objet rond vu de biais (bandes mesurées colonne par colonne, zigzag, clous), visage sur une face, bras qui sortent de dessous sans dépasser | `parade-5.cjs` → `DRUM`, `BAND_T`, `BAND_B`, `ZIG`, `stud`, `RING`, `SKIN`, `MASK`, `stick`, `ball`, bras coupés sous le bord du tambour (`ARM_L`, `ARM_R`) |
| Objet suspendu qui se balance (pivot au crochet), tubes d'argent qui oscillent chacun à son rythme, voile | `epouvantails-4.cjs` → `TUBES`, `tubeBody`, `PEND`, `SAIL`, `a-root` autour du crochet |
| Héros mixte : aplats automatiques pour la tête, mais le bas du corps redessiné pièce par pièce quand les aplats sont trop morcelés (cape, robe, tablier, collier, bras) ; disque derrière la tête (cercle ajusté) ; lames en feuilles | `assassins-3.cjs` → `lowerBody`, `CAPE`, `APRON`, `COLLAR`, `SUN`, `BLADES` |
| Ailes qui battent (quatre morceaux, pivot à la racine), yeux d'ailes en anneaux, duvet en touffes inégales (`fuzz`), antennes en plume prises dans la silhouette | `ronciers-4.cjs` → `UL`, `UR`, `LL`, `LR`, `spot`, `veins`, `fuzz`, `ANT` |
| Poisson : nageoires découpées dans la silhouette (chacune bat à son rythme), bandes par leur couleur, rayons doux, boule d'eau crachée à l'attaque | `bayou-3.cjs` → `TAIL`, `DORSAL`, `FINS`, `PECT`, `RAYS`, `rays`, `glow-atk` |
| (à refaire) Héros peint par matières lissées « par vote » (`couleurs.py --vote --noyau 9` : zones rondes, sans trou), peinture partagée une fois (`<use href="#p-mat"/>`), plumes et queue retirées du corps (sinon fantôme quand elles bougent), bâton mesuré | `mages-8.cjs` → `PAINT`, `BODY`, `PLUMES`, `STAFF`, `along`, `CHEST`, `SKIRT`, `eye` |
| Héros peint par matières (relevées), couronne par sa couleur, manche en deux tronçons | `angels-2.cjs` → `TONES`, `paint`, `PIECE`, `middle`, `CROWN` |
| Coquille en spirale, cristaux | `cuirasses-4.cjs` → `spiral`, `moss` |
| Pattes et serres | `glaces-4.cjs` → `footD`, `nail` ; `assassins-5.cjs` → `toe`, `talon` |
| Jupe de feuilles, notes de musique | `assassins-12.cjs` → `leafGeo`, `skirtBody`, `noteFx` |
| Paille, touffes en mèches courbes | `epouvantails-2.cjs` → `strandAt`, `tuft`, `strawBody` (mèches larges, pas de brins fins : sinon stries) |
| Yeux qui luisent dans un trou, bouche en dents de scie | `epouvantails-2.cjs` → `eye`, `brow`, `MOUTH` (lueur dedans : `g-mglow`) |
| Tout le corps qui bascule pendant l'attaque | `epouvantails-2.cjs` → `LEAN`, `key`, `atkKeys` (autour du pied, ajouté au repos) |
| Feuilles en tuiles, éventail de feuilles | `ronciers-1.cjs` → `leafPts`, `leafHalf`, `leaves` (manteau `MANTLE`, queue `TAIL`) |
| Animal de profil : gueule ouverte, crocs, langue, mâchoire qui claque | `ronciers-1.cjs` → `tooth`, morceaux `mouth` et `jaw` (dents du bas dans `a-teeth`), `nest`, groupe `a-root` pour le bond |
| Pattes de quadrupède, griffes | `ronciers-1.cjs` → `legBody` ; griffes en croc : `bayou-1.cjs` → `claw` |
| Crête, voile et nageoire à côtes en éventail | `bayou-1.cjs` → morceaux `crest`, `fin` |
| Couronne à pointes, barbe avec favoris, yeux à paupière lourde | `myths-12.cjs` → morceaux `crown`, `beard`, `stache`, `eye` |
| Hampe tenue (trident, lance), flamme bleue sans contour | `myths-12.cjs` → morceaux `trident`, `handL`, `flame` (`flameBody`) |
| Épaulière en écailles, bottes de fer | `myths-12.cjs` → morceaux `pauR`, `legL`, `legR` |

## Faits (35)

Ruka `demons-7` (modèle) · héros : Zeus `myths-12`, Séraphin `angels-4`, Nimue `mages-9` (le dessin montre un dieu de
l'orage doré), Kael `assassins-2`, Thor `myths-10` (le dessin montre une femme-araignée), Ilian `angels-2`, Eldra `mages-8`, Sable `assassins-3`, Garvin `knights-8`, Ozias `mages-10`, Valdis `knights-11`, Saïko `assassins-12`,
Rook `assassins-5` · monstres : pétard `parade-1`, lion de la parade `parade-2`, singe aux fusées `parade-3`, lanterne `parade-4`, méduse
`abysses-3`, dino-voile `bayou-1`, tortue hargneuse `bayou-2`, feu follet `bayou-4`, croco cuirassé `bayou-6`, chouette `glaces-4`, escargot de
cristal `cuirasses-4`, coq-girouette `epouvantails-1`, épouvantail `epouvantails-2`, cerf-volant `epouvantails-3`, renard de feuilles `ronciers-1`,
blaireau moussu `ronciers-2`, porc-épic des ronces `ronciers-3`, tambour grondeur `parade-5`, carillon `epouvantails-4`, poisson-archer `bayou-3`, phalène `ronciers-4`.

## File d'attente (prendre le premier non fait)

Ordre : d'abord les monstres que le joueur rencontre en premier (région 1 de la campagne : familles `parade`,
`epouvantails`, `bayou`, `ronciers`), en intercalant un héros Légendaire (l'invocation les montre en grand).

1. `parade-6` 2. `epouvantails-5` 3. héros `myths-8` Freyja 4. `bayou-5` 5. `ronciers-5` 6. héros `angels-3` Aube
7. `epouvantails-6` 8. `ronciers-6` 9. héros `mages-11` Myrr
Ensuite : `fauves` et `ruche` (région 2), `voliere` et `cuirasses` (régions 3-4)… et un Légendaire tous les deux
monstres. Légendaires restants : `assassins-4` Vesper, `assassins-6` Isha, `mages-12` Faust, `angels-5` Lumen,
`angels-6` Elyon, `myths-9` Isis, `myths-11` Atlas (liste complète : `npx tsx` sur `HEROES` de
`src/core/data/heroes.ts`, rareté `legendary`), puis les Épiques.

Quand la page dépassera ~60 personnages (limite de 16 Mo d'une page claude.ai), la couper en deux pages.
