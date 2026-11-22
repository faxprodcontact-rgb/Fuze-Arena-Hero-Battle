# Personnages vectoriels — guide de travail (à lire en premier)

But : redessiner par le code, un par un, les 144 personnages du jeu (dessins Hailuo de `public/art/p/`) dans le style
de Ruka la sirène (`demons-7.cjs`), puis les animer (repos + attaque). Le propriétaire vérifie lui-même chaque
personnage sur la page d'exemple ; on ne lance **ni dessinateurs en parallèle ni relecteur** (trop cher en crédits).
Pas encore branché dans le jeu : la page d'exemple sert de vitrine.

## Méthode économe (une conversation = un ou deux personnages)

1. Choisir le **suivant de la file** (plus bas). Regarder l'original une fois en petit :
   `refonte-graphique/vecto/originaux/<id>.jpg` (le cadre w × h du dessin = la taille de cette image).
2. Gros plans quadrillés **seulement** des zones difficiles (visage, mains, objet) :
   `python3 refonte-graphique/vecto/outils/zoom.py <id> x0 y0 x1 y1 4 /tmp/z.png`.
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
| Ruban, voile, tentacule | `abysses-3.cjs` → `strip`, `veil` |
| Écailles | `demons-7.cjs` → `scales` |
| Plumes et ailes | `assassins-5.cjs` → `feather`, `quill`, `plume` (réutilisées par `<use>`, fichier léger) ; `glaces-4.cjs` → `feather`, `row`, `ruff` |
| Ailes translucides | `assassins-12.cjs` → morceaux `wingU`, `wingD` |
| Flammes, lueur intérieure | `bayou-4.cjs` → `tongue`, `band`, `face` ; flamme tenue : `knights-11.cjs` (morceau `flame`) |
| Roche, lave, fissures | `knights-8.cjs` → `stone`, `crack`, `fissure`, `glowSteps` |
| Métal à rivets, dents, étincelle | `parade-1.cjs` → `stud`, `tooth`, `sparkBody` |
| Coquille en spirale, cristaux | `cuirasses-4.cjs` → `spiral`, `moss` |
| Pattes et serres | `glaces-4.cjs` → `footD`, `nail` ; `assassins-5.cjs` → `toe`, `talon` |
| Jupe de feuilles, notes de musique | `assassins-12.cjs` → `leafGeo`, `skirtBody`, `noteFx` |
| Paille, touffes en mèches courbes | `epouvantails-2.cjs` → `strandAt`, `tuft`, `strawBody` (mèches larges, pas de brins fins : sinon stries) |
| Yeux qui luisent dans un trou, bouche en dents de scie | `epouvantails-2.cjs` → `eye`, `brow`, `MOUTH` (lueur dedans : `g-mglow`) |
| Tout le corps qui bascule pendant l'attaque | `epouvantails-2.cjs` → `LEAN`, `key`, `atkKeys` (autour du pied, ajouté au repos) |

## Faits (12)

Ruka `demons-7` (modèle) · héros : Garvin `knights-8`, Ozias `mages-10`, Valdis `knights-11`, Saïko `assassins-12`,
Rook `assassins-5` · monstres : pétard `parade-1`, méduse `abysses-3`, feu follet `bayou-4`, chouette `glaces-4`,
escargot de cristal `cuirasses-4`, épouvantail `epouvantails-2`.

## File d'attente (prendre le premier non fait)

Ordre : d'abord les monstres que le joueur rencontre en premier (région 1 de la campagne : familles `parade`,
`epouvantails`, `bayou`, `ronciers`), en intercalant un héros Légendaire (l'invocation les montre en grand).

1. `ronciers-1` (renard de feuilles) 2. héros `myths-12` Zeus
3. `bayou-1` 4. `parade-2` 5. héros `angels-4` Séraphin 6. `epouvantails-1` 7. `ronciers-2`
8. héros `mages-9` Nimue 9. `bayou-6` 10. `parade-3` 11. héros `assassins-2` Kael
Ensuite : le reste des familles de la région 1, puis `fauves` et `ruche` (région 2), `voliere` et `cuirasses`
(régions 3-4)… et un Légendaire tous les deux monstres (liste : `npx tsx` sur `HEROES` de
`src/core/data/heroes.ts`, rareté `legendary`), puis les Épiques.

Quand la page dépassera ~60 personnages (limite de 16 Mo d'une page claude.ai), la couper en deux pages.
