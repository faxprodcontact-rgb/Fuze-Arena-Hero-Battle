# Le style de l'interface (nouvelle DA, 26/11/2026) — la référence pour toutes les sections

Demande du propriétaire : « épuré mais actuel, pixel art poussé au maximum, coloré, joyeux, très compréhensible ; plus
d'éléments too much (losanges sur les traits, etc.) ». Planche de toutes les pièces : `../sortie/ui/style-kit.png`
(refaite par `bash refonte-graphique/pixel/ui/outils/kit.sh`). Exemple fini : la section Campagne
(`../sortie/ui/campagne/` : avant | après, et `accueil.gif`).

## En une phrase

Des **pièces en pixel art** (un pixel du dessin = **2 px CSS**, agrandi sans flou), **un seul contour** violet très sombre
(`#221022`, celui des héros HD), **une seule lumière en haut à droite** (arête claire en haut et à droite, ombre en bas et à
gauche), des **aplats** de couleurs vives tirés d'une seule palette, des **coins arrondis en escalier**, et **rien d'autre** :
ni losange, ni gemme, ni clou, ni ruban, ni fleuron, ni double cadre, ni reflet qui passe, ni dégradé lisse. Les textes
restent du vrai texte (i18n) en Lilita One (titres, boutons, chiffres) et Fredoka (phrases), cernés net.

Identité gardée : **émail bleu nuit cerclé d'or** pour tout ce qui encadre (barres, titres, plaques) et **parchemin clair**
pour ce qu'on lit (panneaux, fenêtres) ; les couleurs vives (vert, bleu, or, rouge, violet) pour ce qu'on touche.

## Où c'est fait

| Fichier | Rôle |
|---|---|
| `src/game/ui/px.ts` | **toutes les pièces**, dessinées pixel par pixel par le code à partir de la palette `PAL` ; `installPx()` (appelé par `main.tsx` avant le premier dessin) les pose dans le CSS sous forme de variables `--px-<pièce>` (fond en 9 morceaux : coins fixes, bords et milieu étirés, ×2, net) |
| `src/game/ui/style.css` | les couleurs (variables en tête : gammes `--navy-0…4`, `--gold-0…4`, `--cream-0…3`, couleurs franches), la règle commune des pièces (« Les pièces dessinées »), boutons, fenêtres, barres |
| `src/game/ui/chrome.tsx` | composants : `BarArt` (fond d'une barre, **toujours dernier enfant**), `Medallion` (médaillon rond en pixels, à la taille exacte), `ChapterPlaque`, `FightButtonArt`, `LevelShield`, `Chevron` |
| `src/game/ui/title-banner.tsx` | `TitleBanner` : une plaque de la teinte voulue (`tone`), picto à gauche, titre jamais coupé |
| `src/game/hud-art.tsx` | les mêmes pièces pour Phaser (panneau des combats) : `pxCanvas`, `radialCanvas`, agrandies ×4 unités de combat |

## La palette (`PAL` de px.ts = variables CSS)

Chaque gamme a 5 tons, du plus sombre au plus clair ; les ombres glissent vers le violet, les lumières vers le jaune.

| Gamme | Sert à | Tons |
|---|---|---|
| `navy` | barres, bandeaux de titre, plaques, médaillons, fond des pages | `#121636 #1c2457 #273479 #34489c #5a76d0` (`--navy-0…4`) |
| `gold` | filets, anneaux, chiffres importants, l'onglet choisi | `#8a3f16 #c76a1a #f0a830 #ffd650 #fff4b0` (`--gold-0…4`) |
| `cream` | panneaux, fenêtres, creux, bouton neutre | `#a8805e #dcc093 #f3e3c0 #fff3da #ffffff` (`--cream-0…3`) |
| `green` | **l'action principale** (Combattre, OK, Prendre), interrupteur allumé | `#145040 #1f8a4a #3dbb4c #7fe05c #d0ff94` |
| `blue` | action secondaire, retour | `#1c2f7a #2456b8 #2f8be8 #64c6ff #c2f2ff` |
| `gold` (bouton) | choix mis en avant, onglet choisi | (gamme `gold`) |
| `red` | danger, fermer, défaite, pastille | `#5c1438 #ad2846 #e5434d #ff7f6a #ffd2b4` |
| `purple` | gemmes, invocation, achat | `#3a1c78 #6636bd #9459e8 #c58fff #f2d0ff` |
| `teal` | réserve (eau, guilde…) | `#0f4450 #16807e #22b6a4 #5fe6c0 #c8fff0` |
| `grey` | impossible (bouton désactivé) | `#4b4c62 #77788f #a2a3b6 #c9cad6 #ececf2` |
| `well` | creux sombres (monnaies, jauges vides) | `#07081a #0d1030 #161b45 #222a62 #3a4690` |

Textes : bleu nuit `--text #23244a` sur le clair, crème `#fff3da` sur le sombre, or `--gold-3` pour un titre sur bleu nuit.
Une couleur qui n'est pas dans la palette (rareté, élément) : `rampFrom(couleur)` en fait une gamme du même genre.

## Les pièces (variables `--px-…`)

| Variable | Dessin | Pour |
|---|---|---|
| `--px-panel` | parchemin clair, contour, arête claire | `.card`, `.team-strip`, `.name-card`… (panneau posé sur un décor) |
| `--px-frame` | contour, filet d'or, parchemin | `.modal` (la fenêtre ; son titre `.modal-head` est un bandeau bleu nuit à filet d'or) |
| `--px-inset` | creux clair sans contour (ombre en haut, lumière en bas) | une ligne dans un panneau : `.setting-row`, `.block`, `.quests li`, `.cur-big`… |
| `--px-groove`, `--px-groove-s` | creux sombre à contour (rayon 3 ou 2) | monnaie (`.pill`), onglets (`.tabs`), jauges (`.bar`, `.dock-bar`, `.chapter-bar`) |
| `--px-btn-<teinte>` / `-down` | bouton : contour, arête claire, émail, **lèvre sombre de 2 pixels** ; enfoncé = sans lèvre, plus bas | teintes `green blue gold red purple teal grey cream navy` |
| `--px-plaque-<teinte>` | contour, filet d'or, émail | titres (`TitleBanner`, `.plaque`, « Victoire ! », plaque du chapitre, niveau, petits messages) ; teintes `navy blue purple red green teal gold` |
| `--px-chip` | petite plaque bleu nuit sans filet d'or | étiquettes discrètes (noms sous les médaillons, numéros de la carte) |
| `--px-well-green` | creux vert | interrupteur allumé |
| `--px-bar-top`, `--px-bar-bottom` | émail bleu nuit, filet d'or + contour du côté du jeu | barre du haut, barre des onglets, bas de l'accueil (`BarArt`) |
| `--px-close`, `--px-back`, `--px-plus` | boutons carrés avec leur signe (croix, chevron, plus) | `.x` (le signe est dans le dessin : le texte du bouton est caché), `.prep-head .x`, `.plus` |
| `--px-badge` | pastille rouge 7 × 7 | `.dot` / `<RedDot />` |

Images entières (pas de 9 morceaux) : `medalUrl(taille, teinte)` (médaillon rond, à la taille exacte), `chevronUrl(haut)`,
`glyph(lignes, gamme)` (un petit signe dessiné en « X » : contour et lumière ajoutés tout seuls).

## Comment s'en servir

1. **Poser une pièce sur un élément** : la pièce se pose sur son `::before` (derrière les enfants, qui restent nets).
   - élément commun déjà prévu (liste dans `style.css`, « Les pièces dessinées ») : rien à faire ;
   - nouvel élément : ajouter la classe `pxf` et choisir la pièce : `--pxf: var(--px-panel)` (dans le CSS ou le `style`).
   - n'importe quelle couleur (rareté, élément) : `style={{ '--pxf': pxBg('rim' | 'plaque' | 'btn' | 'panel', couleur) }}`
     (`rim` = un cadre seul au milieu vide, pour les cases des héros et des objets).
   - **jamais** `image-rendering: pixelated` sur un parent qui contient des pictos peints ou des portraits (la propriété
     s'hérite : les pictos agrandis deviendraient crénelés). D'où le `::before`.
   - pas de `border`, `border-radius`, `box-shadow` floue ni dégradé sur une pièce dessinée : tout est dans le dessin.
     Une ombre portée, oui, mais **nette** : `filter: drop-shadow(0 4px 0 #00000047)`.
   - les marges intérieures tiennent compte du bord du dessin : panneau et plaque 8 px, fenêtre 6 px, bouton `0 18px 6px`
     (la lèvre fait 4 px en bas ; enfoncé, le contenu descend de 4 px : déjà réglé pour `.btn`).
2. **Boutons** : `<Btn kind="green|blue|gold|red|purple|ghost">` (`ghost` = crème, neutre) ; désactivé = gris tout seul.
   Une seule action verte par écran (la principale). Les lettres : blanches, cernées net de la couleur sombre du bouton
   (`--o` + `text-shadow: var(--outline-s)` ou `var(--outline)` pour les gros titres).
3. **Titres de partie** : `<TitleBanner title=… tone="blue">{picto}</TitleBanner>` ; `ribbon` (ancien) est encore compris
   (la teinte la plus proche est prise), à remplacer par `tone`.
4. **Médaillons** : `<Medallion size={50} tone="navy">` — une taille **paire** (2 px = 1 pixel du dessin).
5. **Fenêtres** : `<Modal>` (au milieu de l'écran, cadre d'or, bandeau bleu nuit, croix rouge) ; pages plein écran :
   `<Page>` / `.prep-head` (bandeau bleu nuit, bouton retour bleu).
6. **Chiffres et monnaies** : `<Cur>` dans un creux (`.cur-big`) ; compteur de la barre du haut : `.pill` (creux sombre, picto
   qui déborde à gauche).
7. **Pictos** : toujours `<Icon name=…>` / `<Art>` (la planche `icons.webp`, toute en pixel art : `pictos/`). Taille
   ronde : 22, 28, 32, 58… **Petits signes** (étoile des héros, coche, croix, flèche « mieux », chevrons, lecture, plus / égal /
   flèche) : `<Sign name=… k={2}>` (dessinés par `SIGNS` de `px.ts`, variables `--px-<signe>`, aussi utilisables dans un
   `::before`) ; jamais un caractère (★ ✓ ✕ 🔒…) ni un SVG. Étoiles d'un héros : `<Stars>` ; « ★ » dans un texte traduit :
   `starText(t(…))`. Halo derrière un trophée ou un héros : `<Halo size color>` (pixel art animé, `haloStrip` de `px.ts`).
8. **Phaser** (combats) : `pxCanvas('btn-green', largeur, hauteur, 4)`, `radialCanvas(...)`, `medalCanvas` → `textures.addCanvas`
   puis filtre au plus proche (voir `hud-art.tsx`).
9. **Mouvement** : peu, et en pixels : un picto qui saute (`translate` de quelques px), un coffre qui sautille, un sablier qui
   se retourne, une fenêtre qui apparaît (`steps()`). Pas de reflet qui passe, pas de lueur qui pulse partout.

## Mise en page (rappels du propriétaire)

Écran dégagé : un titre, des icônes, des chiffres ; aucune phrase évidente. Pas de défilement si possible (vérifier en
390 × 844 avec encoche **et** 360 × 640). Fenêtres au milieu de l'écran. Le combat et les menus restent dans la zone sûre
(encoche en haut, barre de geste en bas : `env(safe-area-inset-…)`).

## Pour les autres sections (vague 2)

Chaque section part de ce qui existe (les pièces communes ont déjà changé partout : boutons, fenêtres, onglets, creux,
plaques, bandeaux de titre) et refait **ses propres dessins** dans ce style :
- **Héros** : la case d'un héros (`.hcard` : cadre `pxBg('rim', couleur de rareté)` au lieu du métal dégradé, niveau dans une
  `--px-chip`, étoiles), la case d'un objet (`.item`), la fiche du héros (`hero-detail.tsx`, `hero-scene.tsx` : fond sobre,
  niveau bien visible, attributs en pictos dans des creux), la salle (`backdrop-heroes.tsx`).
- **Invoquer** : `portal.tsx`, `summon-stage.tsx`, `card-back.tsx`, les gros boutons `.sum-btn` (→ `--px-btn-purple` / `-gold`),
  le tirage (`SummonResult`).
- **Aventure** : tuiles `.tile` (une plaque de la couleur du mode, son petit décor), `.plaque`, `tile-scene.tsx`,
  `mode-icons.tsx`, `.dungeon-head`, `backdrop-adventure.tsx`.
- **Guilde** : `backdrop-guild.tsx`, `.guild-info`, guerre, tchat.
- Restent en ancien style (SVG lisse), à refaire par la section qui s'en sert : `formation-stage.tsx` (dalles de la
  préparation), la carte du monde (`map.jpg`, partie 9 du plan). Le coffre, le sablier et le halo de `anim.tsx` sont faits
  (audit du 25/11 : `AUDIT-PICTOS.md`).

Vérifier dans le vrai jeu : `refonte-graphique/pixel/ui/outils/campagne-captures.cjs` (captures des écrans, 390 × 844 avec
encoche imitée et 360 × 640 ; à adapter aux écrans de la section), `campagne-gif.cjs` (petit film).
