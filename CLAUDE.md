# Fuze Arena – Hero Battle — notes pour Claude

Jeu mobile de héros automatique (style AFK Arena / Idle Heroes / Hero Wars), destiné à l'App Store puis
Google Play. Le propriétaire n'est pas développeur : lui répondre en français, simplement, sans jargon.

- Cahier de conception (la référence, document vivant, à lire avec les outils de documents Claude) :
  https://claude.ai/artifact/EBxryovSeVavxCCEd4koMv
- Résultats des simulations d'équilibrage : `docs/simulations.md`.

## Où en est le projet

- Étape 1 (conception) et étape 2 (prototype du combat) : faites.
- En cours : **interface** (le propriétaire veut qu'elle soit parfaite avant la suite), sur la version complète avec
  dessins provisoires, jouable hors ligne (sauvegarde sur le téléphone).
- Site de test (comme l'ancien Fuze) : https://faxprodcontact-rgb.github.io/Fuze-Arena-Hero-Battle/ — mis en ligne
  automatiquement à chaque envoi par `.github/workflows/site-test.yml` (branche `gh-pages`, à ne jamais modifier à la main).
  Copie aussi sur claude.ai : https://claude.ai/artifact/EigGhykFPgfeb7L1UoYfDX (outil Artifact : `dist/`, CSS dans la page).
  Les téléphones se mettent à jour tout seuls (`src/game/updater.ts` compare `version.json`, créé à chaque construction).
  La copie claude.ai ne se met pas à jour seule : la republier à chaque envoi.
- Disposition inspirée d'AFK Arena / Idle Heroes : accueil = combat permanent (`idle-scene.ts`) avec icônes sur les bords
  (quêtes, passe, offres, classement, tchat), coffre de butin / Combattre / butin rapide en bas ; avant chaque combat,
  écran de préparation (`screens/prep.tsx`) ; réglages par l'avatar.
- Outil de test à retirer avant la bêta : `TEST_OPEN_ALL_MODES` (`src/core/data/modes.ts`, tous les modes ouverts dès le
  début, demandé par le propriétaire pour les regarder), en plus des « Outils de test » des réglages.
- Décidé : plus de camps (factions) dans le jeu ; la fusion demande des héros du **même élément**. Le champ `faction`
  des héros provisoires ne sert plus qu'au dessin, il disparaîtra avec la création des vrais héros.
- Courrier de l'équipe : `src/core/data/mail.ts` (un `id` unique par message, jamais réutilisé). Tutoriel : `src/game/ui/tutorial.tsx`.
- Base des héros faite (19/11/2026, détaillée dans le cahier, section « Base des héros et des équipements ») : 72 gabarits
  rareté × élément × rôle × variante dans `src/core/data/heroes.ts` (6 rôles, 8 statistiques, 2 passifs à ★3/★5, éveil ★10,
  1 chef sur 3) ; bibliothèque d'effets et statuts dans `src/core/battle/types.ts` + `engine.ts` ; textes fabriqués par
  `src/game/describe.ts` ; équipements par emplacement + panoplies dans `src/core/data/items.ts`. Les noms et dessins
  sont provisoires : l'habillage (nom, histoire, dessin) viendra par-dessus chaque gabarit.
- En cours : **graphismes**. Recherche de style dans `refonte-graphique/` (pas encore dans le jeu) : personnages chibi
  de trois-quarts façon Idle Heroes, dessinés par le code. AVANT de montrer un personnage, passer la **liste de contrôle
  de cohérence** de `refonte-graphique/LISEZMOI.md` (cheveux d'un seul tenant, capuche fermée, ceintures d'un bord à
  l'autre, mains et objets, etc.) en le regardant en grand, et montrer la scène dans l'écran réel du jeu.
  Essai d'images par IA fait le 19/11/2026 (`refonte-graphique/essai-ia/`, 10 crédits gratuits Higgsfield, épuisés) :
  rendu peint plus beau mais des défauts de cohérence. **Décidé le 20/11/2026 : on continue avec le dessin par code**,
  en version épurée (v5 : `refonte-graphique/mini.cjs` + `cast5.cjs`) : personnages petits à l'écran, peu de formes,
  un ou deux éléments forts par personnage, regard dur. Ne jamais dépenser de crédits sans son accord.
  **20/11/2026 (soir)** : le propriétaire veut essayer de faire redessiner nos dessins par Hailuo (avec ses crédits, il
  lance lui-même). Planches 4K de 18 personnages sans texte : `node refonte-graphique/planche-ia.cjs heros|monstres
  fire|wind|water|earth sortie.png` ; prompts (moins de 1 500 caractères, en anglais) dans `refonte-graphique/PROMPTS-HAILUO.md`.
  La refonte par le code des familles de monstres est en pause (Glaces, Échiquier, Feu faits ; les autres à moitié).
  **Les 144 dessins Hailuo sont dans l'aperçu** (v0.20.0) : images rendues gardées dans `refonte-graphique/hailuo-v1/`,
  découpées par `python3 refonte-graphique/decoupe-hailuo.py` → `public/art/p/<id>.webp` + `public/apercu/hailuo.js` (taille et place
  calées sur la silhouette du dessin d'origine). Un seul morceau par personnage : l'aperçu anime le corps entier (respiration,
  élan, frappe, recul, chute) + effets ; bouton « Hailuo / Code » pour comparer. Étape suivante possible : animations
  d'attaque par la vidéo de Hailuo (à essayer sur 2-3 personnages avant de dépenser des crédits).
  **Branchés dans le vrai jeu depuis la v0.21.0** (combats, accueil, préparation, Siège, menus) : tout est dans `public/art/`
  (`p/` personnages entiers, `c/` vignettes carrées, `t/` 12 terrains, `fx/` 32 effets d'attaque sans fond noir), décrit par
  `src/game/art-meta.ts` (fabriqué par `python3 refonte-graphique/art-jeu.py`, après `decoupe-hailuo.py` / `decoupe-decors.py`).
  `src/game/look.ts` choisit le terrain et la famille de monstres selon le mode et le chapitre (8 régions de campagne,
  une famille par élément et par région ; tour, donjons, antre des boss, arène). Les règles ne changent pas : seuls les
  dessins des anciens monstres (gobelin, loup…) sont remplacés. Décidé (v0.22.0) : les images d'effets ne servent
  qu'aux compétences (attaques spéciales), chacune avec sa mini-chorégraphie (`skillFx` dans `fight-view.ts` : la lame balaie et
  percute, l'éclair tombe, les pics jaillissent, le météore s'écrase…) ; les attaques de base restent discrètes, dessinées
  par le code (`basicMelee`, `basicShot`). Au corps à corps, le héros fonce sur sa cible pendant sa compétence.
  Décidé (v0.23.0) : **chacun son tour** en combat (héros et ennemis) : `advance()` dans `fight-view.ts` joue les coups un
  par un et met les règles en pause pendant chaque coup (`TURN_MS` : attaque 430 ms, compétence 980 ms à ×1). Les règles et
  le résultat ne changent pas (le serveur peut toujours rejouer) ; les barres de vie suivent les coups montrés (`View.hp`).
  v0.24.0 (demande du propriétaire) : équipes plus espacées (`HERO_X`/`ENEMY_X`, repris par l'écran de préparation),
  respiration et léger balancement au repos (`syncUnits`) ; coups de base sobres mais percutants (élan, ruée, recul de la
  cible, étincelles, petite secousse) ; compétences spectaculaires : décor assombri (`dim`), lanceur qui se charge
  (`charge` : rayons, double lumineux, halo `preFX` coupé ensuite), bandeau de cinéma des héros (`cutIn`, pas sur
  l'accueil ni dans la fiche), puis impact (`punch` : éclair de couleur, secousse, zoom, distorsion). Relu par un agent.
  v0.25.0 : **les 144 personnages sont découpés en morceaux** (tête, bras armé + arme, bouclier, ailes, queue…) qui tournent
  autour de leurs articulations (repos, attaque, spéciale). Méthode et contrôle : `refonte-graphique/RIG-GUIDE.md` ; un
  fichier par personnage `refonte-graphique/rig/<id>.json` ; `python3 refonte-graphique/rig.py <id>` (ou `tout`) fabrique
  `public/art/r/<id>.webp` (corps rebouché + morceaux regroupés dans une seule image) et la planche de contrôle `rig-out/<id>.png` ; puis
  `art-jeu.py` (champ `rigs` de `art-meta.ts`). Dans le combat : `addView` / `animateParts` de `fight-view.ts`
  (`act` = attaque ou spéciale en cours).
  v0.26.0 (21/11/2026) : **tous les nouveaux dessins Hailuo branchés**. 36 monstres « animaux » + 6 retouches + Apsara refaits
  (`decoupe-hailuo.py --seulement=…`, la planche la plus récente gagne) et leurs découpes animées refaites ; fonds prairie,
  forêt, bayou refaits + 3 fonds de donjons (`mine`, `spring`, `armory`, dans `look.ts`) ; **162 pictos** dans une seule image `public/art/icons.webp` (un par un dans `refonte-graphique/pictos/`)
  (`decoupe-pictos.py` → `src/game/icons-meta.ts` ; `Icon` / `Art` de `kit.tsx` la découpent ; seuls les pictos de `HOLES` ont leurs trous de fond retirés, le blanc peint des dessins est gardé) : monnaies, menus,
  modes, équipements par rareté (`weapon-0..5`…), panoplies (`set-*`), effets en combat (`st-*`, au-dessus des barres de vie),
  ligues, boutique (`offer-*`), missions, autel et dos de carte (invocation), emblèmes de guilde, hibou du tutoriel,
  colisée ; `public/art/ui/` : logo, icône de l'application, écran de chargement (`index.html`), carte des régions
  (`WorldMapModal`, en touchant « Chapitre »). Combats : chaque terrain a son cercle tracé au sol (`OVALS` de
  `decoupe-decors.py`) et `drawArena` place l'équipe dedans ; le premier plan (`FRONT` → `art/t/<nom>-fg.webp`) passe
  devant les combattants (effacé pendant l'assombrissement des compétences).
  v0.27.0 (22/11/2026) : **refonte complète de l'interface**, demandée par le propriétaire (« couleurs claires, épurées
  mais soignées, à la hauteur des dessins »). Thème clair dans le trait des dessins : ciel doux, panneaux « papier crème »,
  gros contour à l'encre (`--ink`), reflet en haut et tranche sombre en bas sur les boutons, liserés dorés, texte blanc
  cerné d'encre sur les couleurs (`--stroke`). Tout est dans `src/game/ui/style.css` (variables en tête). Cases de héros :
  fond aux couleurs de l'élément (halo, rayons, sol), cadre de rareté, picto d'élément ; cases d'équipement colorées par
  rareté. **Portail d'invocation dessiné par le code et animé** (`ui/portal.tsx` + `portal.css` : socle de pierre, anneau
  d'or, runes qui s'allument, tourbillon à trois vitesses, étincelles), dans sa scène (`.summon-scene`). Combats : l'écran
  s'étire selon le téléphone (`H`..`H_MAX` dans `battle-scene.ts`), décor sur toute la hauteur, panneau des héros et
  boutons ancrés en bas (`hudY`), mêmes couleurs que les menus (`C` de `fight-view.ts`). Une scène peinte par mode (boss
  dans l'antre, tour, donjons). Étiquettes claires à bord coloré (plus de pastilles sombres), pictos à la place des
  caractères de texte, virgule décimale en français. Relu par un agent sur 50 captures, corrigé.
  **v0.28.0 (22/11/2026) : le thème clair est REFUSÉ par le propriétaire** (« trop clair, traits trop grossiers »). Interface
  refaite de zéro dans `style.css` : tons moyens tirés des décors, traits fins (1,5 px), double filet (bord sombre + filet doré),
  rivets aux coins, fond de l'application = un décor flouté et teinté (`public/art/ui/bg-<onglet>.jpg`, `.app-bg`), cases de
  héros et d'équipement = couleur unie de la rareté en dégradé. **Trois directions à l'essai** (`src/game/theme.ts`, attribut
  `data-theme` sur `<html>`, choix dans Réglages → Outils de test, ou `#theme=royal` dans l'adresse) : `bois` (bois et parchemin,
  par défaut), `royal` (bleu roi et or), `crepuscule` (prune et or). Le panneau des combats suit la direction (`applyTheme` dans
  `fight-view.ts`, variables `--hud-*`). Quand le propriétaire aura choisi : retirer les deux autres et le sélecteur.
  Captures des trois directions : `scratchpad/art5/themes.cjs`.
  **Réponse du propriétaire (22/11/2026) : aucune des trois, « trop simple, trop plat » → il veut des cadres PEINTS par Hailuo**
  (bois sculpté, parchemin, or). Planches et prompts 25 (cadres, barres, plaque, ruban) et 26 (boutons, cases de héros et
  d'équipement par rareté) : `node refonte-graphique/planches-ui.cjs cadres|boutons`, prompts à la fin de `PROMPTS-HAILUO.md`,
  emplacements des pièces dans `refonte-graphique/ui-pieces.json`. En attendant ses rendus, le jeu garde la direction `bois`.
  À faire à leur arrivée : les ranger dans `hailuo-v1/ui-cadres.jpg` et `ui-boutons.jpg`, les découper (fond blanc retiré),
  puis monter l'interface avec (`border-image` pour les cadres et boutons étirables, image entière pour les cases).
  **v0.29.0 (22/11/2026), demandes du propriétaire** : plus AUCUNE rayure (ni hachures sur les panneaux, ni rayons répétés) ;
  il **aime beaucoup le style du portail** (dessin par le code, animé) et veut d'autres éléments dans ce trait. Faits :
  `ui/anim.tsx` + `anim.css` (sablier dont le sable coule puis qui se retourne, coffre de butin fermé / entrouvert / plein,
  halo de runes derrière le trophée et le héros fusionné) ; `ui/backdrop.tsx` = **fonds dessinés par le code**, épurés mais
  décorés et vivants (un par onglet : salle des héros, nuit d'invocation, route de l'aventure, forteresse de la guilde, et
  un crépuscule pour les pages) : silhouettes, grand cercle de runes qui tourne lentement, poussières de lumière, bannières,
  fanions, nuages. Panneaux : coins ouvragés dorés (`--corner-*`), reflet en haut et ombre en bas (`--sheen`). Petits
  mouvements (fin de `style.css`) : pictos des modes qui flottent, onglet ouvert qui saute, reflet sur Combattre et sur les
  barres, éclat qui tourne sur les médaillons, fanion du chapitre, monnaies, reflet d'or sur les cases légendaires.
  **Le propriétaire valide cette direction (22/11/2026) et veut avancer « partie par partie »**. v0.30.0, **partie Aventure** :
  décor refait avec soin (`ui/backdrop-adventure.tsx` : soleil et cercle de runes, sommets enneigés, château sur son rocher,
  nuages, montgolfière, oiseaux, chemin qui serpente, sapins ; lumière venue de la droite), bandeau en haut de l'écran
  (`.adv-banner`, titre sur une `.plaque`) pour que le panorama se voie, tuiles au fond animé (`ui/tile-scene.tsx` : lueur,
  anneau gravé qui tourne, et un petit décor par mode). **La tuile Siège est remplacée par le Colisée** (picto `colisee`,
  clé interne toujours `defense`) : écran de présentation avec « Bientôt », **les règles du Colisée restent à construire** ;
  l'ancien mode Défense n'est plus accessible (son code est encore là). Prochaines parties à refaire de la même façon : Héros,
  Invocation, Guilde, Accueil.
  v0.31.0 : le propriétaire trouve l'Aventure « bien mieux » et demande des **dessins « 100 fois mieux, plus travaillés, plus
  professionnels »**. Décor entièrement redessiné (`backdrop-adventure.tsx`) : sommets à deux faces et arêtes brisées (`Peak`),
  nuages en volume (`Cloud`), château à tours rondes ombrées en cylindre (`Tower`), remparts, châtelet, cascade, moulin dont les
  ailes tournent, hameau, rivière et pont, sapins et arbres ronds éclairés à droite, campement et feu au premier plan.
  **Quatre calques** superposés (fond fixe, soleil et nuages qui bougent, château et campagne fixes, puis ce qui bouge devant) :
  garder cet ordre, sinon les nuages passent devant le château. Tuiles : une vraie petite scène par mode dans `tile-scene.tsx`
  (nuit et mer de nuages, route et fanion, grotte et cristaux, antre et lave, colonnes et bannières, arcades du Colisée).
  C'est le niveau de dessin attendu pour les prochaines parties (Héros, Invocation, Guilde, Accueil).
  Relu par un regard neuf puis corrigé (v0.31.1). Leçons à garder pour les prochains décors : **sous une grille de tuiles ou
  de cartes, le décor reste calme** (collines seules ; chemin, rivière et arbres coupés par les tuiles font du bruit) ; tout
  élément est posé (ombre courte à gauche, pied qui mord dans l'herbe) ; raccords par une lisière de forêt (`forest`), pas par
  des bandes de brume ; faces à l'ombre bleu-violet, faces éclairées tiédies ; signes inventés (`GLYPHS`), jamais de lettres ;
  l'anneau des tuiles passe derrière leur décor.
  v0.31.2 (retour du propriétaire, capture de son iPhone) : à l'arrivée sur l'onglet il fallait faire défiler, et le titre
  passait sur le château. Cause : le décor était calé sur toute l'application alors que la barre du haut est plus haute sur
  un iPhone à encoche. Désormais **le décor de l'Aventure vit dans la zone de contenu** (`.content-adv` + `.adv-scroll` dans
  `app.tsx`, dessin remonté de `TOP` dans `backdrop-adventure.tsx`), le bandeau a une hauteur liée à la largeur (44 %, comme
  le dessin) et **les six tuiles se partagent le reste de la hauteur : rien ne défile**. À vérifier pour chaque partie refaite :
  `scratchpad/art5/tailles.cjs` (cinq tailles de téléphone, encoche imitée) doit répondre « tient sans défiler ».
  v0.32.0 : **les six pictos des modes de l'Aventure sont dessinés par le code et animés** (`ui/mode-icons.tsx`, `ModeIcon`,
  demande du propriétaire : « même style graphique, du mieux possible ») : tour sur son rocher flottant et cristal, boussole
  dont l'aiguille cherche le nord, porte du donjon avec herse et torches, crâne cornu aux yeux en flammes, bouclier et épées
  qui se heurtent, Colisée à trois étages d'arcades. Un seul contour par objet (filtre `.mi-body` dans `anim.css`), dégradés
  communs dans `Defs`. Les pictos peints (Hailuo) de ces six modes ne servent plus dans les tuiles ; ils restent dans
  `icons.webp` pour le reste du jeu.
  v0.32.1, après relecture par un regard neuf et retours du propriétaire : **vrai contour d'épaisseur constante** par filtre de
  dilatation (`mi-out-c` bleu nuit pour les pictos froids, `mi-out-w` brun pour les chauds ; ne pas revenir aux ombres portées
  empilées, qui donnaient un contour décalé), grandes masses plutôt que petits traits répétés, Colisée en pierre ivoire sur son
  socle, yeux du crâne en brasiers (`EyeFire`). **Les étiquettes d'information des tuiles (« Nouveau », niveau requis) sont
  accrochées au bandeau du nom** (dans `.tile-name`), jamais posées sur le picto. La taille des pictos suit la hauteur des tuiles.
  v0.33.0 (retours du propriétaire sur le haut de l'Aventure) : **raccord panorama-prairie refait** (collines boisées au pied
  des montagnes, bois de feuillus au dessus éclairé `canopy`, prairie qui commence dans l'ombre des arbres puis s'éclaircit,
  touffes d'herbe `tufts`, sapins posés dans l'herbe : plus de bande sombre) ; **bandeau de titre dessiné** (`ui/title-banner.tsx`,
  `TitleBanner` : ruban cramoisi, plaque de bois dans un cadre d'or, fleuron, gemmes, lettres d'or, reflet qui passe), à
  réutiliser pour les titres des autres parties ; décor enrichi (tour de guet reliée au château par un pont de pierre, lierre,
  champs et meules au hameau, strates des sommets, nuages lointains, halo du soleil sur les montagnes).
  v0.34.0 : **partie Invocation refaite** (demande : « plus badass, comme la partie d'avant, donne tout »). Décor
  `ui/backdrop-summon.tsx` (sanctuaire la nuit : lune et cercle de signes, étoiles, aurore, étoile filante, pics noirs, îles
  flottantes à cristaux, pierres levées gravées, plateau fendu de lueurs), dans la zone de contenu comme l'Aventure. Scène du
  portail `ui/summon-stage.tsx` : cercle de signes couché au sol, estrade à trois marches, deux obélisques à cristal, arcs
  d'énergie, orbes en orbite, étincelles aspirées ; le portail a une couronne de pointes (`claws` de `Portal`). Écran sans
  défilement : bandeau (`TitleBanner`, ruban violet ou bleu), médaillons à gauche pour choisir le portail (avec le nombre de
  parchemins), « Chances » et « Fragments » à droite (fenêtre `fragments`), panneau du bas (jauge du Légendaire garanti, gros
  boutons ×1 et ×10, invocation gratuite). **Séquence d'invocation** (`casting`, 1 s : le portail enfle, onde au sol, éclair
  blanc) puis **révélation plein écran** (`SummonResult` : décor assombri, halo de runes, un faisceau par héros, cartes qui se
  retournent). Vérifier avec `scratchpad/art5/sum.cjs` et `tailles.cjs 3 s`.
  v0.34.1, après relecture par un regard neuf (leçons à garder) : **de l'air autour du sujet** (obélisques écartés du portail,
  îles et lune loin de l'axe, pas de lune derrière les médaillons) ; aurores qui sortent des deux bords (jamais de bord net) ;
  lumière au sol en flaque, pas en cône ; pas de fissures au sol (deux ellipses gravées suffisent) ; signes du portail inventés
  (`RUNES`, plus rien qui ressemble à une lettre) ; comètes à traîne en orbite plutôt que des billes ; pendant le lancement le
  panneau est assombri par un filtre (pas par transparence, sinon le décor passe au travers). Révélation : héros triés du plus
  rare au plus commun, les meilleurs cerclés de lumière, les communs assombris, **4 cartes par rangée** (grandes) pour ×10,
  une seule grande carte au cadre d'or avec étoile de lumière, onde et étincelles pour ×1, bouton OK en bas.
  v0.35.0 : **partie Héros refaite** (demande : « améliore 100 fois la page, et le fond derrière les héros, prends exemple sur
  les jeux connus »). Onglet : `ui/backdrop-heroes.tsx` = la salle des héros (verrière au ciel du soir, colonnes, bannières,
  braseros, estrade ronde `DAIS`) dans la zone de contenu ; la section se tient **en pied sur l'estrade** sur deux rangs
  (`Hall` et `SPOTS` de `screens/heroes.tsx`, `ui/hero-figure.tsx` : `HeroFigure` pose le dessin entier `art/p/` les pieds
  au point 53 % / 95 % de sa boîte), la toucher ouvre son réglage ; médaillons Fusion et Renaissance ; filtre par élément
  (`el-pick`) et tri ; seule la liste défile (`.hall-scroll`). **Cases de héros** (`HeroCard` de `kit.tsx`, partout dans le jeu) :
  mur sombre teinté de la rareté avec l'emblème de l'élément (`--crest`, classes `el-*`), lumière derrière le buste, sol
  éclairé (le héros y est posé : image ancrée par le bas), cadre de métal `.hcard-frame` (anneau en dégradé, il luit sur les
  Légendaires), niveau en haut à gauche, élément dans son œillet, « dans la section » = liseré d'or + écusson vert à gauche.
  **Page d'un héros** (`screens/hero-detail.tsx`, plein écran, plus une fenêtre) : décor animé par élément
  (`ui/hero-scene.tsx` : volcan, sanctuaire des cimes, grotte marine, canyon), héros sur son piédestal (`Pedestal`, teintes
  de l'élément, gemme de la rareté), aura selon la rareté, équipement de part et d'autre (le toucher ouvre l'onglet
  Équipement), flèches pour passer au héros suivant (`swap` de `nav.ts`), bouton « dans la section » en haut à droite, plaque
  étoiles + puissance, panneau sombre à trois onglets (attributs avec pictos `StatIcon`, compétence, équipement) ; un niveau
  gagné fait jaillir un éclair, des étincelles et le nouveau niveau. Vérifier avec `scratchpad/art5/her2.cjs` (et `her2.cjs se`),
  `her3.cjs` (sac, préparation, fusion), `tailles.cjs 2 h`. Leçons de la relecture : la rareté se lit dans le cadre et la lueur,
  pas dans un aplat saturé ; une place réservée par information sur une case ; panneau du bas sombre (le clair vole le regard
  au héros) ; volcan et soleil décentrés, jamais dans l'axe du héros ; un astre différent par décor ; ne jamais cacher un
  `TitleBanner` par `display: none` (ses dégradés ont les mêmes identifiants : les autres bandeaux se vident) ; la grille de
  l'application a `minmax(0, 1fr)` pour ne plus déborder à droite sur petit téléphone.
  v0.35.1 (retours du propriétaire, « c'est très bien ») : sur la page d'un héros, **le panneau du bas se déploie vers le haut**
  (glisser vers le haut ou toucher la poignée `.hp-grab` ; `.hp-panel.tall`, 76 % de l'écran, par-dessus la scène sans la
  déplacer ; glisser vers le bas le referme) ; **plateau de la section refait** (`Board` de `screens/prep.tsx`) : ce n'est plus
  le terrain du combat mais l'estrade de la salle des héros vue de près, faite pour les cinq postes (`POS` : deux à l'arrière,
  le chef au centre sur sa dalle d'or, deux à l'avant), une dalle par poste (`Plate`, « + » sur un poste vide), le tracé de
  la formation serti d'or, trois chevrons vers l'avant, deux braseros. Vérifier avec `scratchpad/art5/her4.cjs`.
  v0.35.2 (le propriétaire voulait le fond du choix de la section « plus travaillé, plus cohérent ») : tout l'écran est
  maintenant **dans la salle des héros** : `ui/formation-stage.tsx` (`FormationStage` : mur, verrière au ciel du soir, niches
  et bannières, colonnes, braseros, grande estrade à deux marches avec sa frise de signes gravés qui tourne, tracé de la
  formation ; `Plate` : dalle cerclée de la couleur de l'élément du héros, or pour le chef ; `STAGE_POS` = les cinq postes),
  plateau bord à bord sous le titre (plus de cadre), bas fondu dans le sol, fond de page bleu nuit uni (`.prep-bg`, à la place
  des montagnes). Avant un combat (`.prep-plan`) le plateau se resserre et se fond aussi sur les côtés (`.field-art` garde
  les proportions). Vérifier avec `scratchpad/art5/her5.cjs`.
  v0.35.3 (retour du propriétaire : selon l'endroit, un héros paraissait plus grand qu'un autre) : **tous les héros ont la même
  stature partout**. `art-jeu.py` mesure la stature de chaque héros (des pieds au sommet de la tête, sans l'arme, le bouclier,
  les ailes ni la queue, grâce aux découpes `rig-out/`) et écrit un 6e nombre `norm` dans `art-meta.ts` (0 pour les monstres,
  qui gardent leur échelle). `norm` sert aux combats (`addView` de `fight-view.ts`), aux héros en pied (`HeroFigure`) et aux
  vignettes `art/c/` des héros, refaites à stature égale (`python3 refonte-graphique/art-jeu.py --cartes=heros` ; ce qui dépasse
  du carré, pointe d'arme ou aile, est coupé). Le plateau de la section montre maintenant les héros en pied (`.field-hero`).
  Ne plus cadrer une vignette de héros sur toute sa silhouette : une longue lance le rapetisse. Essais de mesure gardés en
  tête : la boîte de la tête seule est trop bruitée (museaux, coiffes, chevelures).
  v0.35.4 (retour du propriétaire : « des zones blanches derrière les personnages, pas pro ») : **détourage refait**.
  `decoupe-hailuo.py` laissait du blanc dans les petites zones fermées (entre deux mèches, entre un bras et le corps, dans
  une boucle d'oreille) et un liseré clair le long du contour. Ajouts dans `cut()` : règle « 2 bis » (petites zones blanches
  retirées si elles sont cernées de trait noir sans couleur contre elles, ou près du bord et bien cernées, ou collées au
  fond ; le blanc peint est gardé : voisin d'une couleur vive, rond et plein comme un reflet d'œil, ombré) ; le liseré du
  bord est traité partout, comme du trait noir mêlé de blanc. Exceptions par personnage : `BLANC_PEINT` (motif blanc d'un
  bouclier, blanc d'un œil) en plus de `PLEIN`. Quatre planches à la fois (10 min au lieu de 35). **Ordre à suivre après
  tout nouveau détourage** : garder une copie de `public/art/p/` et de `public/apercu/hailuo.js`, lancer
  `decoupe-hailuo.py`, puis `python3 refonte-graphique/recadre.py <copie>` (remet chaque dessin dans son ancien cadre au
  pixel près, sinon les découpes animées se décalent), puis `rig.py tout` (14 min), puis `art-jeu.py --cartes`.
  Contrôle fait sur les 144 personnages, sur fond sombre, zone retirée par zone retirée. Les images sources sont des JPG :
  les PNG d'origine du propriétaire donneraient des bords encore plus nets, mais ne sont pas nécessaires.
  v0.36.0 (retours du propriétaire : « ça fait dessin posé, trop sec » puis « il reste des trous, vérifie chaque sprite un par un ») :
  **contrôle sprite par sprite et dessins adoucis.** (1) Revue des 144 sprites : chaque trou fermé (425) et chaque morceau
  « mangé par le bord » (234 poches) regardé à côté du dessin d'origine. Résultat dans `refonte-graphique/retouches-detourage.json`
  (lu par `decoupe-hailuo.py`, coordonnées en pixels de `public/art/p/<id>.webp`) : `garder` = blanc PEINT retiré à tort, à
  remettre (dents, griffes, défenses, reflets d'yeux, peintures de visage, cheveux blancs… ; un point = la zone vide qui le
  contient, trou fermé ou poche) ; `retirer` = miettes d'ombre à enlever. `SCELLER` (contour épaissi pendant le remplissage)
  pour la tour d'échecs et l'ange, dont un morceau entier partait. `cadres.json` (écrit par `recadre.py`) : décalage des 3
  dessins recadrés. (2) `refonte-graphique/adoucir.py` (`soften`, OpenCV : `pip install opencv-python-headless`) : trait
  noir affiné et teinté de la couleur qu'il cerne, hachures et petits détails fondus, noirs moins durs, léger voile de
  lumière, bord fondu sur un pixel. Appliqué par `decoupe-hailuo.py` à chaque dessin (`--brut` pour s'en passer). Ordre
  complet : copie de `public/art/p/` → `decoupe-hailuo.py` → `recadre.py <copie>` → `rig.py` (en quatre lots) → `art-jeu.py --cartes`.
  Si le propriétaire trouve l'adoucissement trop fort ou trop faible : paramètre `k` de `soften` (1 = réglage actuel).
  v0.36.1 (retour du propriétaire, capture du picto « Escorte » : « des fonds blancs un peu partout, même sur les pictos ») :
  **toutes les découpes reprises.** Pictos : les 162 revus un par un ; retouches dans `refonte-graphique/retouches-pictos.json`
  (lu par `decoupe-pictos.py`, positions en fraction de la case) : `points` (fond resté enfermé : sous le cheval du chariot,
  dans le panneau « sans pub », anse du sac, anses du vase, anneau de la boussole), `auto` (petits restes cernés de trait dans
  un rectangle : rayons de roue, entre les poutres), `effacer` (tache claire peinte par erreur), `halo` (lueur des
  équipements rares, des fragments et du sceptre : transparente selon sa blancheur, plus de liseré blanc). Le blanc PEINT
  des pictos (reflets des lames, gemmes, yeux du hibou, cadran) est gardé. Sprites : chaque zone blanche restée opaque (290)
  regardée à côté du dessin d'origine ; 58 zones de fond ajoutées à `retirer` dans `retouches-detourage.json` (entre un bras
  et la tête, sous une jupe, entre des pics, entre les cordes d'une lyre…). Logo, 32 effets et premiers plans des décors
  contrôlés : rien à corriger. Chaîne complète en une commande : voir l'ordre de la v0.36.0 (25 minutes).
  **v0.37.0 (22/11/2026), page d'un héros refaite** (le propriétaire : « les héros passent moins bien en gros », page « un peu
  plus comme avant ») : le héros se tient, à taille modeste, dans **sa case** (fenêtre sur le décor de son élément : `HeroScene`
  avec `crop` ; cadre de métal de la rareté `.hcard-frame`, niveau, élément, couronne du chef, étoiles ; flèches à cheval sur le
  cadre, ou geste sur la case) ; à côté : rareté et rôle, puissance, les quatre attributs principaux ; dessous, les quatre
  secondaires sur une rangée ; puis un panneau sombre qui défile : équipement (un emplacement ouvre sa fenêtre qui monte du bas,
  `.hp-sheet`), niveau, attaque spéciale (aperçu en boucle à la demande, bouton ▶), talents (★3, ★5), chef de section. Les
  passifs s'appellent « Talent » dans le jeu. Plus d'onglets ni de panneau déployable. Vérifier avec `scratchpad/art5/her7.cjs`
  (et `her7.cjs se`). Essai abandonné le même jour à la demande du propriétaire : Ruka redessinée entièrement par le code
  (`refonte-graphique/vecto/`) ; on garde les dessins Hailuo.
  **Chargement (v0.30.1, le propriétaire le trouvait « très long »)** : Phaser et les scènes de combat ne sont plus dans le code
  de départ, ils arrivent à la demande (`src/game/scenes.ts` : `runIdle`, `runBattle`… en `import()` ; toujours passer par ce
  fichier depuis les menus, jamais importer `fight-view` ou une `*-scene` directement) ; Phaser a son propre fichier
  (`manualChunks` dans `vite.config.ts`), gardé par les téléphones d'une mise à jour à l'autre ; les 32 images d'effets et la
  planche de pictos de Phaser se chargent en arrière-plan après l'affichage (`preload` de `fight-view.ts`) ; la planche de pictos
  est préchargée dans `index.html` et l'écran de chargement s'efface dès qu'elle est là (plus d'attente de tout le reste).
  Mesure : `scratchpad/art5/net2.cjs` (premier écran en 3,8 s au lieu de 9,7 s sur un réseau ralenti).
  La copie claude.ai a maintenant plusieurs fichiers de code dans `assets/` : les publier tous et retirer les anciens.
  Attention : dans le CSS, ne pas écrire `url(art/…)` (mal résolu une fois le jeu construit) : passer l'adresse par un
  `style` dans le TSX. Tour complet en captures : `scratchpad/art5/tour.cjs` (à refaire si besoin).
  Sources Hailuo des terrains et effets : `refonte-graphique/hailuo-v1/terrains-*.jpg`, `effets-*.jpg`.
  Aperçu animé sur le site de test : `public/apercu/` (page à part, bouton « Aperçu des animations » dans les Outils de
  test des réglages) : les personnages v5 animés morceau par morceau. Les images viennent de
  `node refonte-graphique/export5.cjs` (à relancer après tout changement de dessin). Pas encore branché dans le vrai combat.
  **Les 72 héros sont dessinés, version 6** (20/11/2026, noms provisoires, inspirés des mythologies du monde) : refaits
  un par un après la demande du propriétaire (« améliore x100 ») : carrures, jambes, visages et poses différents, aucun
  héros ne part d'un autre, museaux et becs d'une seule courbe. Liste dans `refonte-graphique/HEROS.md`, gabarit
  `fig6.cjs` + `face6.cjs` + `legs6.cjs` + `wear6.cjs` + `items6.cjs`, héros dans `h6-fire|wind|water|earth.cjs`,
  export `node refonte-graphique/export72.cjs` → `public/apercu/h/<identifiant du jeu>.png` + `heros.js` + `HEROS.md`.
  Galerie : `public/apercu/heros.html` ; la page d'animations tire des équipes au hasard parmi les 72.
  Certains héros (pas tous, et jamais d'étoile) ont un **petit élément entier qui brille** (flamme, perle, lanterne… :
  `shine` dans leur fiche) ; les Épiques et Légendaires ont une **aura** (violette / dorée). Visibles aussi dans les
  combats de l'aperçu.
  AVANT de montrer un héros nouveau ou modifié : le regarder en grand (`node zoom6.cjs "fire:4" sortie.html`) et passer
  le contrôle de `refonte-graphique/LISEZMOI.md` (rien ne traverse une barbe, un visage ou un museau ; rien de coupé
  ni de flottant ; arme dans le bon sens ; pas de doublon de silhouette, de pose ou d'arme), puis faire relire les
  planches par un regard neuf (agent de relecture) : il trouve ce qu'on ne voit plus.
  Héros et monstres ont **un seul contour par personnage** (ombres douces entre les morceaux, lumière d'ensemble) :
  ne jamais remettre un contour par morceau.
- **Monstres** (commencés le 20/11/2026) : 12 familles de 6 validées par le propriétaire (liste et règles dans
  `refonte-graphique/LISEZMOI.md`, section « Les monstres » ; pas de famille vue partout, plutôt de vraies créatures).
  Gabarit `refonte-graphique/mon6.cjs`, une famille par fichier `m-<famille>.cjs`, export `node refonte-graphique/exportM.cjs`
  → `public/apercu/m/` + `monstres.js` + `MONSTRES.md`. **Les 72 monstres sont dessinés** ; la page d'animations fait
  affronter les héros et une famille tirée au hasard. À vérifier sur CHAQUE monstre (demande du propriétaire) : gueule
  ouverte découpée dans la silhouette, membres attachés sous le corps, et **un seul contour par créature** (ombres
  douces aux jonctions, jamais un contour par morceau : pas d'effet « formes posées les unes sur les autres »).
  Pas encore branchés dans le vrai jeu.
- **Décidé le 21/11/2026 : le mode Défense (tower defense) est retiré**, remplacé par le **Colisée** : duel 1 contre 1 entre
  deux équipes de 3 héros qui entrent chacun leur tour ; il réutilise les fonds existants (picto à venir de Hailuo).
- Plus tard : profil du joueur, événements temporaires, sons et musique, ouverture du Siège.
- Ensuite : serveur (Supabase) → habillage manga → social réel → argent réel → bêta → lancement.

## Organisation du code

| Dossier | Rôle |
|---|---|
| `src/core/` | Règles du jeu, **sans aucun affichage** : le même code servira au téléphone, au serveur et aux simulations |
| `src/core/data/` | Tous les réglages (héros, monstres, étoiles, fusion, invocations, économie, campagne, modes, boutique). On équilibre ici, pas ailleurs |
| `src/core/battle/` | Moteur de combat déterministe (graine + choix du joueur = combat rejouable par le serveur) |
| `src/game/state/` | État du joueur et **toutes ses actions** (`actions.ts` = la seule porte d'entrée ; à brancher sur le serveur plus tard) |
| `src/game/ui/` | Menus (Preact) : `app.tsx` (coquille), `screens/*` (un fichier par écran), `kit.tsx`, `style.css` |
| `src/game/fight-view.ts` | Base commune des scènes de combat (personnages, coups, chiffres) |
| `src/game/battle-scene.ts` | Écran de combat (Phaser), utilisé par tous les modes |
| `src/game/idle-scene.ts` | Combat permanent de l'accueil (image du butin hors ligne) |
| `src/core/defense/engine.ts` + `src/game/defense-scene.ts` | Mode Défense (tower defense) : règles déterministes, puis l'affichage ; réglages dans `src/core/data/defense.ts` |
| `src/game/art.ts` | Dessins provisoires faits par le code (héros et monstres) |
| `src/game/i18n.ts` | Tous les textes, français et anglais |
| `simulations/` | Joueurs virtuels qui jouent des mois en accéléré pour vérifier le rythme |
| `tests/` | Tests automatiques des règles |
| `docs/` | Résultats des simulations |

Commandes : `npm run dev` (jeu en local), `npm run build` (construit `dist/`), `npm test` (tests),
`npm run verifier` (vérification du code), `npm run simuler` (rapport de progression),
`npm run simuler -- --calibrer` (recalcule la difficulté de la campagne, à recopier dans `src/core/data/campaign.ts`),
`npm run combat` (force des monstres à puissance égale), `npx tsx simulations/premiers-jours.ts` (première semaine du
vrai jeu jouée par un joueur automatique). Réglages → « Outils de test » dans le jeu : avancer le temps, ressources,
tout débloquer.

## Règles de travail

- **Pas de phrases évidentes dans le jeu.** Ne jamais écrire de texte qui explique ce que tout le monde devine
  (exemple interdit : « L'invocation sert à obtenir des héros plus forts » au-dessus du bouton d'invocation).
  Écrans dégagés : un titre, des icônes, des chiffres. Montrer par un geste plutôt que par un texte.
- **Le serveur est le juge** : invocations, achats, monnaies et récompenses sont décidés côté serveur.
  Le hasard passe par `src/core/rng.ts` (graine), pour que le serveur puisse rejouer et vérifier.
- **Équilibrage** : décision du propriétaire, **pas de simulation à chaque changement** pendant le travail sur
  l'interface et les fonctions. On met des valeurs raisonnables, et on fait **un grand réglage final avant la bêta**
  (`npm run simuler -- --calibrer`, `npm run combat`, `simulations/premiers-jours.ts`, puis `docs/simulations.md`).
  Ne lancer une simulation plus tôt que si le propriétaire le demande.
- **Univers** : Black Clover a seulement inspiré les TYPES de personnages (pas le style graphique, abandonné le 19/11/2026).
  Aucun nom, personnage, symbole ou histoire repris. Graphismes : faits par Claude, sans autre abonnement d’IA (choix du propriétaire).
- **Langues** : français et anglais dès le départ ; aucun texte écrit en dur dans le code de l'interface.
- **Supabase** : ne rien lire ni modifier sans l'accord explicite du propriétaire, ne jamais lui demander de
  clé dans la conversation. Décidé : au début de l'étape 3, supprimer l'ancien projet Fuze Arena (après une
  sauvegarde) pour faire de la place ; garder le projet AVA.
- Code en anglais (noms de variables), commentaires et textes pour le propriétaire en français.
