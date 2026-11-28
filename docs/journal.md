# Journal détaillé du projet (déplacé de CLAUDE.md le 22/11/2026)

Historique complet des décisions et de chaque version, gardé tel quel. CLAUDE.md n'en garde qu'un résumé ; lire ce
journal seulement quand on retouche une partie (chercher son nom ou son fichier avec `grep -n`).

## Où en était le projet (texte complet)

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
  **v0.38.0 (22/11/2026), décors de combat refaits par le code** (le propriétaire : les fonds peints « ne passent vraiment pas »,
  il aime le style de l'Aventure). Les 14 terrains (`look.ts`) sont dessinés par le code dans `src/game/bg/` : `kit.tsx` (sommets,
  nuages, collines `curve`/`bump`, forêts, arbres, rochers, ciel, `Platform`, `Flagstones`, `Overhang`, `FaceStones`), `props.tsx`
  (troncs, champignons, fougères, braseros, torches, bannières, emblèmes inventés, colonnes, cristaux, eau, parois `RockWall`,
  murs `Masonry`, flammes et lueurs animées), un fichier par décor (`meadow`, `forest` = bramble, `bayou`, `ash`, `tundra`,
  `storm`, `temple`, `abyss`, `tower`, `cave` = mine + spring, `halls` = armory + lair + arena), liste dans `scenes.ts`.
  `engine.ts` (avec Phaser) change chaque dessin en image au lancement du combat (`loadBackdrop` dans `preload`, `placeBackdrop`
  dans `drawArena` de `fight-view.ts`), pour la taille exacte de l'écran (le ciel s'allonge sur un grand téléphone), et anime
  les éléments d'après l'heure (dérive, balancement, rotation, flamme, lueur, courant, éclair) ; particules Phaser. Ordre
  des calques à respecter : ciel (−30) < ce qui est derrière le paysage (−29…−21 : nuages, aurore, mousse et lianes qui
  pendent DERRIÈRE le feuillage, fumée qui sort du cratère) < paysage et sol (−20) < ce qui bouge devant le paysage (−19…−11)
  < voile des compétences (5) < combattants < premier plan (1300, coupé au bas du terrain, il s'efface pendant les
  compétences). **Décidé par le propriétaire : plus jamais de rond au sol** ; chaque décor a une **plateforme rectangulaire
  d'un bord à l'autre** (`Platform`, repères `p0`/`p1` de `Ctx` : 50 px derrière les pieds du rang du fond, 48 px devant ceux du
  rang de devant), avec son chant devant et ce qui est dessous (herbe, eau, lave, vide…). Tout est posé : les maisons et
  arbres des collines sont placés sur la crête par la même fonction que la colline (`curve`), les objets du fond se tiennent
  juste derrière `p0`. Les menus (tour, donjons, boss du jour, Colisée) montrent la même scène en image fixe
  (`bg/compose.ts` + `ui/terrain-image.ts`, sans Phaser). Outil de test : `#fond=<terrain>` dans l'adresse impose un décor.
  Vérifier avec `scratchpad/art5/fonds.cjs <pro|se|grand> <terrains…>` (vrai combat + accueil), `zooms.py` (bande du paysage et
  bas en pleine résolution), `menus-fonds.cjs`, `modes.cjs` (vrai combat dans chaque mode). Les anciens fonds peints
  (`public/art/t/`) ne servent plus (sauf `dungeon`, terrain inutilisé).
  v0.38.1 : le combat (`.battle`, plan 48) passe au-dessus des pages (45) : un combat de donjon, lancé depuis la page du
  donjon restée ouverte, était caché derrière elle (bug signalé par le propriétaire) ; les fenêtres de résultat (50) restent dessus.
  **v0.38.2 (22/11/2026), les 14 décors revus un par un** (le propriétaire avait trouvé un arbre coupé sur une île de la Tour
  et veut tout regarder lui-même : planches « décor seul / en combat » envoyées, il dit ce qui ne va pas, on corrige). Outils :
  `scratchpad/bgcheck/` (`check.tsx` + `run.cjs` : signale tout élément animé dont le dessin sort de son image, il doit dire
  « rien ne déborde » ; `clean.tsx` + `clean.cjs` : une image propre de chaque décor dans `propres/` ; `planches.py` : les
  14 planches dans `.apercus/decors/`) ; dans le jeu, Réglages → Outils de test → « Décor des combats » impose un décor.
  Corrigé : îles de la Tour et éclair de l'orage (marges), ailes du moulin plus petites au sommet de la tour, troncs de la
  forêt qui montent sous la voûte (dégradé retourné `leafFlip` : la voûte est dessinée tête en bas), plus de taches claires
  sur les plateformes, lune de la toundra à droite sous une aurore en biais (`tilt`), étoiles nettes (`sparkle`), ciel de
  l'orage fondu dans le noir et poteaux du pont, voûte de roche d'où pendent les stalactites (`RockWall`), rails posés sur
  leurs traverses, hotte et conduit de la forge jusqu'à la poutre (plus de torche dans la cheminée), murs des salles qui
  montent et se perdent dans le noir (`Gloom`), bouches de pierre des chutes de lave, porte de l'arène à la place de l'arche
  du milieu, public aux arches, fanions de deux couleurs, lave qui luit dans tous les joints des dalles (`flagJoints`).
  Signes des frises : `RUNES` de `bg/kit.tsx` (aucun ne ressemble à une lettre ; les `GLYPHS` restent pour les menus).
  **v0.39.0 (22/11/2026), l'interface dans le trait des décors** (demande du propriétaire : barres, ronds, coffre, sablier,
  boutons, panneau des combats, police, encadrements, guilde, portail). Polices : **Lilita One** (titres, boutons, chiffres) et
  **Fredoka** (textes) ; Lilita n'a qu'une graisse : `font-synthesis: none` sur html, et jamais `fontStyle: 'bold'` dans
  Phaser (`FONT` de `fight-view.ts`) ; les scènes attendent la police (`fontReady` de `scenes.ts`, 1,5 s au plus).
  `ui/chrome.tsx` = les pièces dessinées : `ChromeDefs` (dégradés communs `cx-…`, posés une fois par l'application, jamais
  cachés), `Medallion`, `Chevron`, `Gem`, `BarArt` (barre du haut, des onglets, bas de l'accueil : bois et rail d'or, dessinés
  à la mesure exacte par `useSize`), `TabSocket` (socle de l'onglet ouvert), `ChapterPlaque`, `FightButtonArt`, `LevelShield`.
  **`BarArt` toujours en dernier enfant** de sa barre : le tutoriel vise les onglets par `nth-child`. Accueil : les boutons
  ronds sont des médaillons rangés dans deux colonnes **repliables** (`EdgeColumn`, repliées par défaut, choix gardé dans
  `fuze-edge-left/right`, point rouge sur la languette). Couronne du chef : sur le rebord avant gauche de sa dalle
  (`.field-slot .crown`), plus sur la tête du héros. Tous les boutons (`.btn`, `.sum-btn`, `.x`, `.tabs`, titres des
  fenêtres) : contour brun, cadre d'or, émail bombé, lettres cernées (`--bt`). Coffre et sablier redessinés (`anim.tsx` ;
  coffre grand ouvert = couvercle rabattu dessiné à part et trésor). Combats : `hud-art.tsx` (planche, plateau cerclé d'or,
  anneaux des portraits avec la rainure de l'énergie, disques par élément, rainure de vie, boutons), chargé dans `preload`
  de `battle-scene.ts` ; portraits en buste coupés en rond. Guilde : `ui/backdrop-guild.tsx` (forteresse au coucher du
  soleil, deux tours à bannières, rempart, braseros, un dragon qui passe), bandeau `TitleBanner` (ruban bleu) et plaque
  `.guild-info` ; `TitleBanner` ajuste la taille d'un titre long (jamais coupé). Invocation : **rien de ce qui est posé au
  sol n'est dans le fond** (pierres levées, îles proches, anneaux et cristaux retirés de `backdrop-summon.tsx` : ils se
  mêlaient à la scène) ; cristaux du premier plan dans `summon-stage.tsx` ; portail : couronne, ailes (plumes partant d'un
  même point : des ailes, pas des rayons), double anneau perlé, gemmes serties, tunnel aspiré, éclat du cœur. Captures :
  `scratchpad/art5/tour2.cjs <pro|se>` (24 écrans), `ui1.cjs`, `ui-guild.cjs`, `ui-summon.cjs`, `ui-crown.cjs`, `tailles.cjs`.
  **v0.40.0 (22/11/2026), le tirage des héros refait** (demande : « plus spectaculaire, des impacts de couleur selon la
  rareté pour teaser le personnage, dos de carte refait de zéro »). `SummonResult` (`screens/summon.tsx`) : une boule de
  magie (`TeaseOrb`) encaisse un impact par rareté gagnée, sa couleur monte (argent, bleu, violet, or : `TEASE`, variable CSS
  `--tc`) jusqu'à la meilleure rareté du tirage ; chaque impact secoue l'écran et fait enfler la boule ; éclairs dès l'Épique,
  colonne d'or pour le Légendaire. La boule tient la couleur atteinte (`HOLD_MS`), éclate, et les cartes en jaillissent (elles
  partent du centre : `--dx`/`--dy` mesurés). Cartes de dos qui luisent de la couleur de leur rareté, puis retournement en 3D
  de la moins rare à la plus rare ; la meilleure tremble, se fait attendre (`BEST_PAUSE`) et éclaire tout l'écran
  (`.rv-final`). Toucher l'écran passe tout ; OK n'arrive qu'à la fin. Le rythme : constantes `FIRST_MS`…`FLIP_MS`.
  **Dos de carte** : `ui/card-back.tsx` (`CardBack`, par le code : cadre d'or biseauté, clous sertis aux coins, étoiles et
  constellations, cercle de signes en filigrane, le portail en miniature avec ailes et flèche ; cœur, gemmes et lueur de la
  couleur de la rareté cachée). Le tutoriel attend OK à la fin du tirage (`.reveal-ok`, la main n'y va qu'une fois le bouton
  visible). Vérifier avec `scratchpad/art5/tirage.cjs <nom> <pro|se> <1|10> <pitié 0..39> [passer]` (filme le tirage ; 39 =
  Légendaire garanti), `tirage-planche.py`, `tirage-video.py` et `tuto-run.cjs` (tutoriel joué jusqu'à l'onglet Héros).
  **v0.41.0 (22/11/2026), retours du propriétaire sur son iPhone** : (1) **le bois de l'interface est remplacé par un émail
  bleu nuit cerclé d'or**, « plus actuel » (barres du haut et du bas, bas de l'accueil, titres des fenêtres et des pages,
  plaque du chapitre, `TitleBanner`, plaque « Victoire ! », étiquettes des médaillons, plaque de la guilde, panneau et bouton
  Quitter des combats) : variables de la direction `bois` (nom gardé, « Bleu nuit » dans les outils de test), `BAR_TONES` et
  `cx-navy` de `chrome.tsx`, `tb-navy` de `title-banner.tsx`, `Panel` et `HUD_BUTTONS.navy` de `hud-art.tsx`. Les panneaux
  restent en parchemin, leurs bords et textes passent au bleu nuit. (2) **Toutes les fenêtres s'ouvrent au milieu de l'écran**
  (plus rien ne monte du bas : `.modal`, la fenêtre d'un emplacement `.hp-sheet`, les petits messages `.toast`, les pages
  apparaissent sur place). (3) Plus de socle sous l'onglet ouvert de la barre du bas (le propriétaire n'aimait pas cette
  « zone ») : le picto se soulève, lumière douce sans bord. (4) Combattre de l'accueil plus petit, lettres dans le cadre,
  gemmes plus coupées (plus de `overflow: hidden` ni de second reflet). (5) Préparation : **plus d'aperçu des ennemis en
  haut** ; leur puissance est à côté de la nôtre dans le titre (« 145 / 50 », vert ou rouge) ; le plateau reprend la place.
  (6) Plus de couronne au-dessus du chef pendant le combat. (7) Page d'un héros : un emplacement vide reste vide (la
  silhouette grise passait pour un vrai objet et l'iPhone ne la dessinait qu'au rebond) ; plus de rebond nulle part
  (`overscroll-behavior: none`). Vérifier avec `scratchpad/art5/proprio.cjs <dossier>` (écrans touchés, à la taille de son
  téléphone, encoche imitée), `tour2.cjs <pro|se>`, `tuto-run.cjs`.
  **v0.42.0 (23/11/2026), essai du pixel art dans le vrai jeu** (demande : « de la même taille que dans le jeu, à chaque place
  où les anciens persos étaient ») : les 10 personnages de l'essai (Kael `assassins-2`, Sable `assassins-3`, Eldra `mages-8`,
  Rook `assassins-5`, Ilian `angels-2`, et les monstres `ronciers-1`, `bayou-1`, `bayou-4`, `parade-1`, `glaces-4`) remplacent
  les anciens dessins partout. `python3 refonte-graphique/pixel/jeu.py` écrit `public/art/px/<id>.webp` (planche de 8 images,
  cases de 100 × 100 avec 2 pixels d'air, agrandie ×4 sans flou), `public/art/px/c-<id>.webp` (vignette cadrée comme
  `art-jeu.py`, 512 de côté) et `src/game/pixel-meta.ts`. Taille : un pixel = 1,35 unité de combat pour les héros (≈ 124 de
  haut comme avant), 0,96 pour les monstres (≈ 86) : une seule taille de pixel par groupe. Code : `isPixel` / `pixelUrl` /
  `cardUrl` (`art.ts`), au combat une planche animée à la place du dessin découpé, sans écrasement ni balancement en plus
  (`View.px`), bandeau des compétences ; héros en pied (`hero-figure.tsx`, `.px-win`, `image-rendering: pixelated`). Les
  anciens dessins restent dans `art/p`, `art/c`, `art/r` : enlever un nom de `CHARS` dans `jeu.py` le remet comme avant.
  **v0.42.1** : le propriétaire ne les voyait pas (ses héros et ses monstres n'en font pas partie) → bouton « Combat pixel
  art » dans les Outils de test : `pixelDemoBattle()` (`actions.ts`, combat `demo` sans récompense, ~30 s gagné par les
  héros), décor prairie et familles des monstres redessinés (`look.ts`, cas `demo`).
  **v0.43.0 (23/11/2026)** : demande « héros plus poussés, position de combat, plus agressifs, corps et têtes plus
  badass ; rien de coupé ; fond de combat en pixel art ». Les 5 héros redessinés en garde (Ilian : barbe dégagée, aucun
  bras devant, mèches devant, couronne posée ; Kael en élan, épée traînée ; Sable lionne qui rugit ; Eldra bâton en lance ;
  Rook ailes de feu en plumes, pas en rayons). Toile 128 × 120 avec une marge autour du repère 96 × 96 (`pix.py` :
  `FRAME_W`, `OX`…), planches ×3 (3168 px de large, sous la limite de 4096 des téléphones), `pixel-meta.ts` : `cw`, `ch`.
  Contrôle « rien de coupé » : aucun pixel opaque sur le bord de la toile, sur les 8 images (petit script dans la
  conversation : `sheet()` puis bords de chaque case). Fond `fond.py` → `public/art/px/fond-prairie.webp` (240 × 420 ×3),
  posé par `drawArena` quand le décor a `pixel` (`Look.pixel`, cas `demo`), son bas sur le bas du terrain.
  **v0.44.0 (23/11/2026)** : demande « des poses différentes, pas toutes les mêmes ; les ailes du phénix d'avant ; les têtes
  brouillonnes, plus de précision ». Les **têtes sont dessinées pixel par pixel** (`refonte-graphique/pixel/persos/tetes.py` :
  une grille de lettres par tête, une légende de couleurs, les yeux fermés par `*_BLINK` ; `python3 persos/tetes.py x.png`
  les montre en grand), posées par `c.sprite()` (`pix.py`). Cinq poses : Kael en élan (épée traînée), Sable un genou à
  terre (lames tendues), Eldra sur une jambe (bâton au-dessus de la tête), Rook debout ailes ouvertes (ailes du premier
  essai : une langue de feu de la racine vers chaque pointe), Ilian bien campé (trident planté, boule d'eau). Leçon : une
  pose accroupie « en boule » ne se lit pas en pixel art ; garder des silhouettes simples et différentes.
  **v0.45.0 (23/11/2026), style « gros pixels encrés »** (référence du propriétaire : un chevalier en pixel art à gros
  traits) : héros d'environ 64 pixels de haut (au lieu de 90), grosse tête dessinée pixel par pixel, **un trait noir autour
  de chaque morceau** (style `'ink'` de `pix.part`), ombrage net. Corps faits par morceaux nets : cou et trapèzes sous la
  tête (la tête ne flotte pas), épaulières, bras / coude / avant-bras et brassard / poing, cuisses épaisses, genouillères,
  torse détaillé (pectoraux, abdominaux). Chaque héros encré donne son `ORIGIN` (repère : pieds en y = 71, milieu x = 40)
  et n'a pas de contour ajouté par `sheet()` ; au combat un pixel = 1,8 unité (`SCALE['ink']`). Mêmes poses qu'en v0.44.
  Ilian validé d'abord seul (essai), puis les quatre autres. Les monstres sont encore dans l'ancien style.
  **v0.46.0 (23/11/2026)** : retours. Ilian : bras plus gros et plus longs, poings et main plus grands, épaulières plus
  larges. Sable : chaque bras et chaque jambe **d'un seul morceau** (pas de trait noir aux articulations sur un corps de
  fourrure). Kael : la crinière est **une seule masse de flammes** (langues réunies, un seul trait noir autour, cœur orange
  puis jaune par érosion du masque, braises) au lieu de pics séparés. Eldra : bottes plus petites, la jambe levée dessinée
  **derrière la jupe et la ceinture** (elle en sort). Rook refaite de zéro (consigne : « harpie / phénix sur le thème du
  feu ») : ailes pleines à la place des bras (forme entière cerclée de noir, bord festonné, plumes de couverture dorées,
  bouts jaunes), crête de flammes, tête pixel par pixel (yeux d'ambre cerclés de noir), queue en éventail, serres.
  **v0.46.1** : les bras d'Ilian refaits plus simples (demande : « trop brouillon ») : **une seule forme cerclée de noir de
  l'épaule au poignet** (pas de coude ni d'avant-bras séparés), un brassard d'or en travers (`bracer()`), un poing dessiné
  pixel par pixel ; l'épaulière posée par-dessus le haut du bras. Sable : les jambes dessinées avant la jupe et le tablier
  (le bas des habits passe devant le haut des cuisses).
  **v0.47.0 (23/11/2026), les 12 chevaliers** (knights-1 à 12) en gros pixels encrés, d'après l'idée de leurs anciens
  dessins (`planche_faction.py` dans la conversation : les vignettes `art/c/` d'un groupe sur une planche). Nouveau :
  `persos/kit.py`, la **boîte de pièces communes** (bras, jambes, bottes, torse, jupe, ceinture, épaulières, cape, armes,
  boucliers, arc, flammes, poings ; squelettes de jambes `'large'`, `'moyen'`, `'droit'`, `'fente'`). Chaque héros garde
  sa tête dessinée pixel par pixel. Retour du propriétaire pendant le travail (pas tous les jambes écartées ; haut des
  bras devant le tee-shirt ; cou trop long ou devant ; coins de bouclier) → `arm()` avant le torse puis `arm_front()`
  après (la racine du bras reste sous le vêtement), `neck()` avant le torse, règles ajoutées au guide (§ 3, § 6, § 9) ;
  appliqué aussi à Eldra, Sable et Ilian. `controle.py` contrôle tous les héros de `jeu.CHARS`.
  **v0.48.0 : les 9 autres assassins** (Nyx le génie à la queue de fumée, Vesper le démon aux ailes de chauve-souris,
  Isha la déesse au soleil, Corvin l'elfe au bouclier, Lysa le guerrier du nord, Jinn l'archer, Morrow le chevalier en
  armure complète, Zéphyre la ninja, Saïko la fée). Ajout au kit : `FACE` (le visage commun, lignes 6 à 19) et
  `face_legend()`, pour les têtes qui ne changent que les cheveux ou la coiffe.
  **v0.49.0 : les 11 autres mages** (Pell le poète à la lyre, Mira la valkyrie, Orin le tengu, Tessa à tête d'aigle, Ilvar le
  chacal aux faucilles, Sélène la danseuse au lotus, Arcan l'ogre au sac à vent, Nimue le vieux dieu de l'orage, Ozias le
  vampire, Myrr l'ange à la trompette, Faust le dieu du tonnerre et ses tambours). Ajout au kit : `feather_wing()` (aile de
  plumes pleine, bord festonné, couvertures ; même méthode que la harpie). Contrôle utile : une tête de moins de 16 lignes
  n'est pas reconnue (tête trop petite, Tessa corrigée).
  **v0.50.0 : les 12 démons** (Grizz le roi des mers au bouclier de coquillage, Vrak le pêcheur au harpon, Barzul le pirate,
  Lilou la tortue boxeuse, Kesha l'homme-requin à la scie, Morgath la nymphe à la jarre, Ruka la sirène, Zaroth le samouraï
  masqué, Velith le yéti à la hache de glace, Skarn le chasseur à l'arbalète, Azgor le spectre des marais, Nerith
  l'impératrice à la lanterne). Têtes trop petites (ratio < 27 %) : agrandies en doublant une ou deux lignes du visage.
  **v0.51.0 : les 11 autres anges** (Célia la dame des neiges, Aube la chasseuse au loup blanc, Séraphin la sorcière
  pieuvre, Lumen la prêtresse à la boule d'eau, Elyon le dragon à la perle, Solenn le nain, Ariel le faune, Raphaëlle le
  frondeur, Auriel le cyclope au rocher, Gabryel l'homme-scorpion, Céleste la dryade). Une queue en anneaux = une seule
  forme avec des traits aux jointures (des boules séparées font un chapelet). `ONE_EYE = True` dans un fichier de
  personnage : `controle.py` ne compare pas les deux yeux (cyclope).
  **v0.52.0 : les 12 mythes, les 72 héros sont faits** (Faune le druide à la faucille, Satyre le guerrier au chignon,
  Cyclope le minotaure à la hache, Méduse la gorgone au rayon, Dryade le dieu chacal, Minotaure la reine ailée, Anubis le
  baron vaudou, Freyja le barbare à la massue, Isis le chasseur au crâne de cerf, Thor la femme-araignée, Atlas l'enfant
  de la forêt, Zeus le roi noir). Les noms de fichiers suivent les noms du jeu, pas ce que montre le dessin. Une couleur
  de clignement passe par une lettre de la légende (jamais une couleur directe dans `HEAD_BLINK`).
  **v0.57.4** : chargement : étoile du logo retirée, colisée entièrement retravaillé (pierre chaude, blocs, arcades en relief, gradins, sable, porte). Pictos armes / équipements / éléments / rôles / stats refaits (`pixel/ui/pictos/`).
  **v0.57.3** : chargement : plus de crête au premier plan, mer de nuages en 3 rangées, colisée refait sur son piton, logo au milieu, oiseaux au loin ; tests : `.claude/**` exclu (vite.config.ts).
  **v0.65.0** : **tout le jeu passe au vectoriel, le pixel art est supprimé** (demande du 27/11). Les 67 planches de combat réexportées avec l'outil final (`jeu_export_vecto.py`, toutes sous 4,2 Mo ; dragon de lave et léviathan allégés) ; plus de drapeau `?vecto` : menus, cartes, fiche, formation, invocation, accueil, tous les combats, fonds, effets reçus et têtes sont vectoriels ; dessin fixe provisoire des dragons retiré (`stillStrike`) ; décors des menus en image réduite (`fonds/<clan>-menu.webp`) ; supprimés : `public/art/hd/`, `public/art/px/`, `hd-meta.ts`, `hd-figures.ts`, `fond-meta.ts`, les chaînes pixel (`pixel/hd/`, `pixel/fonds/`, `pixel/persos/`, outils) et leurs sorties (`fondlib.py` gardé dans `pixel/ui/` pour l'écran de chargement). Test `tests/images.test.ts` (toutes les images existent). Détail : `refonte-graphique/ui-moderne/EXPORT-JEU.md`, sections 4 et 5 ; captures `refonte-graphique/pixel/sortie/ui/vecto/bascule/`.
  **v0.66.0** : **écran de chargement en style moderne** (demande du 27/11 : « refais en style moderne l'écran de chargement du début, le plus précis possible »). Même scène que le pixel (ciel du soir, soleil en haut à droite, nuages hauts aux bords dorés, oiseaux, montagnes pâles, colisée sur son piton qui sort d'une mer de nuages, logo au milieu, jauge en bas), redessinée en vectoriel lisse comme les fonds de combat par `refonte-graphique/ui-moderne/chargement/chargement.py` (scène 540 × 1170, rendue ×1,5) → `public/art/chargement/` (fond fixe + 4 bandes en tuiles : nuages hauts et 3 rangs de la mer de nuages ; 74 ko en tout) et le bloc « chargement » d'`index.html`. Tout bouge en CSS, sans script : bandes qui glissent à 4 vitesses, halo du soleil, 3 oiseaux, lucioles d'or, logo qui arrive, reflet sur la jauge (pilule de pierre cerclée d'or). L'image fixe `chargement.webp` sert de fond à l'écran « Bienvenue » / du nom. Supprimés : `pixel/ui/chargement.py`, `paysage.py`, `public/art/ui-px/chargement*.webp`.
  **v0.66.1** : **signe du repos, essai sur Kael** (demande du 27/11 : « une petite animation lente mais visible de ce qui est propre à chaque héros, partout, même quand on l'obtient »). Kael : la crinière ondule plus fort, la lame rougeoie lentement (boucle de 3 s). Au combat : la boucle du repos (12 images) ; dans les menus où le héros est en grand (fiche, tirage, estrade) : `heros/repos.py` ne garde que les zones qui bougent (bandes `art/vecto/repos/`, `vecto-repos.ts`, `ui/vecto-live.tsx`), pas dans les petites cases (mémoire iPhone). Consigne pour les autres : `refonte-graphique/ui-moderne/heros/REPOS.md`.
  **v0.67.0** : **signe du repos pour les 47 héros** (après l'essai de Kael validé : chaque héros a son élément qui bouge lentement, boucle de 3 s : armes qui rougeoient, capes, queues, crinières, lanternes, ailes…), fait par groupes de 8, un agent à la fois (consigne `heros/REPOS.md`) ; au combat 12 images de repos (Orin 8 et Velith 10 pour le budget de 4,2 Mo) ; dans les menus 1,2 à 6,8 Mo par héros (ailes trop grandes : seulement au combat, `signe_combat`). `repos.py` compare chaque image à la première (lueurs lentes). Aussi : **taille des héros en grand** cohérente (`hero-size.ts` : hauteur de corps mesurée × gabarit ; fiche, estrade, tirage, préparation) ; **fenêtre Équipement** refaite (pierre grise de la DA, boutons galet aux lettres blanches, fiche de l'objet touché avec sa panoplie et son bonus, `Modal class="modal-dark"`) ; recyclage sans compteur d'objets.
  **v0.68.0** (27/11) : **bugs visuels des personnages** : le signe du repos des menus est refait avec une marge autour du cadre (ce qui en sortait, comme une patte de Nyrra, est montré), des gouttières entre les images de la bande (plus de fil de l'image voisine), des noms de fichiers à empreinte (un jeu resté ouvert sur l'ancienne version montre l'image fixe au lieu de mélanger mesures et images : le cadre sombre autour de la tête de Nyrra) ; **combat** : `bords_combat` (script de contrôle) a trouvé 39 personnages dont des images touchaient le bord de leur vue (trident d'Ilian, spéciales d'Orin, de Célia, araignée cuirassée, titan, léviathan…) : `JEU['vue']` élargie dans leur `jeu.py` et planches refaites (dragon : 7 images de repos pour le budget). Aussi : **Fonderie** à la place du recyclage (picto `foundry`, « Fondre ») ; **gemme des Légendaires** qui dépasse du haut des cartes (`.hcard-clip`) ; **élément des cartes** dans une languette symétrique du niveau avec un signe épuré d'une couleur (`ElementSign`) ; **Fusion** et **Renaissance** sur un autel de pierre grise (`.fuse-altar`), liste de la fusion rangée par rareté et en fondu sous « Tout fusionner ».
  **v0.69.0** (27/11) : **plus aucun fond blanc** (demande : « tous les fonds blancs en fond comme les fusions ») : `src/game/ui/theme-sombre.css` (chargé après theme-pierre) redéfinit les surfaces claires (fenêtres, cartes, lignes, champs, jauges, pilules) en pierre de l'autel de la fusion, lettres claires, filet d'or ; les écrans aux cartes blanches écrites en dur (Aventure, Guilde, tchat, butin rapide, Colisée, fiche) y sont repris un par un ; boutons bleus et discrets en pierre `galet` (plus de beige). Les boutons Google et Apple restent blancs (leurs règles). Renaissance sur l'autel (`.fuse-altar`).
  **v0.70.0** (27/11) : **les deux barres toujours au premier plan** : les pages (fusion, renaissance, forge, formation, fiche, mission, donjon, amis, courrier) prennent la place du contenu entre la barre du haut et celle du bas (`.app > .page` en ligne 2 de la grille ; barres et contenu placés explicitement), changer d'onglet les referme (`go()` de nav.ts) ; petit téléphone : autel de la fusion plus compact, liste des héros avec au moins une rangée et demie. Listes sous une barre (fusion, renaissance, formation, mission) : fondu plus long sous la barre. Sablier de l'accueil centré et vivant (seul le sable coule), pictos d'élément épurés partout, puces de filtre grises, Fonderie sur une ligne.
  **v0.71.0** (28/11) : **mode Événement à la place du Boss du jour** (`src/core/data/event.ts`, section « Le mode Événement » d'`actions.ts`, `EventMode` d'`adventure.tsx`) : zones de 20 niveaux en chemin serpentant sur le décor d'un clan ; on inscrit l'équipe de la formation (un des 3 essais du jour), vie et morts gardées d'un niveau à l'autre (`UnitInit.hpFrac`, `BattleResult.heroHp`) ; tous les 2 niveaux, 2 bonus au hasard (soin 30 %, attaque +, défense +, retour d'un mort) jusqu'à la fin de la partie ; perdre ou abandonner finit la partie ; 20 niveaux → difficulté suivante, remise à 1 à chaque nouvel événement (`FEATURED_BANNER.id`). Gains : parchemins d'événement (niveaux 10 et 20) et XP des héros (`Hero.xp`, montée de niveau automatique). Quête du jour « Événement ». `dailyBossId` reste pour le boss de guilde.
  **v0.71.1** (28/11) : fiche du héros : les flèches (héros précédent / suivant) passent de part et d'autre du nom (dans la scène, depuis le recadrage, elles passaient sous les médaillons) ; liste des héros : les cartes passent sous les filtres dans un fondu. Toutes les pages recadrées revues (360×640 et 390×844).
  **v0.72.0** (28/11, nuit) : **grand réglage de tout le jeu** (demande du propriétaire ; réponses : joueur de référence 3 × 20 min par jour, tout le jeu en 5 à 7 mois, payeur ≈ 2 fois plus rapide, premier tirage vraiment au hasard, connexion 7 jours avec Légendaire au choix, simulations oui, agents non). Détail et chiffres : `docs/simulations.md`, partie « Grand réglage du 28/11 ».
  - Outils : `simulations/vrai-jeu.ts` joue le VRAI jeu (mêmes actions que les boutons, tous les modes) pendant des mois, profils `regulier` et `payeur` ; `simulations/calibrer-vrai.ts` règle `CAMPAIGN_ANCHORS` dessus (passes successives ; en fin de partie la courbe oscille d'une passe à l'autre : prendre la moyenne de deux passes encadrantes) ; `simulations/heros.ts` mesure la force de chaque héros (combats 5 contre 5 au hasard, à niveau et étoiles égaux). L'ancien modèle (`npm run simuler`) ne suit plus le vrai jeu.
  - Leçons : un joueur automatique doit jouer comme un vrai (garder les copies de Légendaires, acheter les fragments de son héros) sinon les étoiles rouges semblent impossibles ; les fins de région (grand boss seul) et les débuts de chapitre (une seule vague plus forte) faisaient des murs de plusieurs semaines : regarder la mesure « mur » de la calibration ; une boucle sans fin dans le joueur automatique se voit à une simulation qui ne finit plus.
  - Campagne : une région = un clan (monstres, décor, élément) du début à la fin, ordre vent, eau, terre, feu deux fois (`REGION_ELEMENTS`, `CLANS`) ; régions de 2, 3, 3, 4, 4, 5, 5, 4 chapitres ; le grand boss de fin de région est seul ; boss moins forts en attaque (`BALANCE` de core/stages.ts) ; déblocages 15 / 30 / 50 / 90 / 140 / 220 / 360.
  - Départ : plus de héros offert, un premier tirage au hasard (le parchemin du départ), tutoriel refait (`tutorial.tsx`), 10 invocations à la fin du tutoriel, 7e jour de connexion = Légendaire au choix.
  - Économie : récompenses d'or et d'essence en heures de butin (`goldH`, `essenceH`, `resolveReward`) ; tour et donjons moins généreux ; passe en saisons de 28 jours ; une invocation par pub et par jour ; coffres de quêtes réduits ; carte mensuelle 300 gemmes par jour ; passe premium plus riche ; fragments des boutiques sur le Légendaire visé (ou celui qui en a le plus) ; marches rouges allégées, Mythique à 400 cristaux.
  - Héros : profils de rôle, raretés, compétences retouchés (tireurs et soigneurs relevés, protecteurs baissés) ; moyenne de victoires : Légendaires 58 %, Épiques 52 %, Rares 47 %, Communs 43 %.
  **v0.73.0** (29/11) : **héros joker** (demande du propriétaire, pour les joueurs malchanceux) : un petit golem de cristal ★5 (dessin `refonte-graphique/ui-moderne/monstres/golem-joker/golem-joker.py`, images `art/vecto/joker-<élément>`), gagné au 20e niveau d'une zone d'Événement, la première fois de chaque événement (sa tête brille sur le chemin ; puis une carte « Héros joker » où l'on choisit l'élément, il sort du portail) ; il ne combat pas, ne va ni en section ni en mission, ne sert qu'aux fusions (`JOKERS`, `isJoker` de data/heroes.ts ; `claimJoker` d'actions.ts ; test `tests/joker.test.ts`). Avantage d'élément 30 % → 20 % (`ADVANTAGE_MULT`). Marches rouges remises aux valeurs d'origine (les jokers fournissent les ★5 à sacrifier), seconde moitié de la campagne plus dure. **Icône de l'appli** refaite en vectoriel : la tête d'Elvyn, le dragon d'eau (`ui-moderne/icone/icone.py`, aussi en 1024 px pour les boutiques). Logo du chargement : un essai « style moderne » (plaque de pierre, 4 cristaux d'élément) a été refusé par le propriétaire (« pas le concept du jeu, je préférais l'ancien ») : l'ancien logo est remis ; pas de pierres ni de cristaux partout. Puis, à sa demande, le ruban et les épées du logo refaits dans le même esprit (`pixel/ui/logo_hd.py`) : ruban plus grand et bien cintré, deux filets d'or, queues fendues en V avec leur pli ; deux vraies épées (garde d'or au rubis, poignée de cuir, pommeau) croisées par les poignées sous le ruban, lames en V dont les pointes ressortent en haut ; ombre sans flou (viewBox 640 × 500).
  **v0.64.0** : connexion Google / Apple préparée : étape « Bienvenue » au premier lancement (boutons officiels, « Jouer en invité »), ligne Compte dans les réglages (lier plus tard), `src/game/auth.ts` + `auth-supabase.ts` (éteints tant que `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` ne sont pas donnés), guide `docs/connexion-comptes.md`. Sablier de l'accueil à la hauteur du coffre, sans libellé.
  **v0.63.2** : le propriétaire confirme : plus de plantage sur iPhone. Outils de recherche (`diag.ts` : boîte noire, mode léger, test automatique) retirés.
  **v0.63.1** : LA cause du plantage iPhone (trouvée par le test automatique `?bisect=1` : « sans le fond : OK », « sans filtres : OK ») : les fonds des menus dessinés par le code avaient une ombre floue (`feGaussianBlur`) par volume, calculée sur un rectangle géant (`BIG` de `backdrop-kit.tsx`) ; Safari préparait une image énorme pour chacune. Plus aucun flou SVG dans les décors (`Soft` vide, ombres nettes). Leçon : **jamais de filtre SVG (flou) sur une grande forme**, ni dans les décors ni ailleurs.
  **v0.63.0** : la pierre grise et or devient l'habillage du jeu (choix du propriétaire) : `installTheme()` pose toujours `data-theme="pierre"` ; le bleu nuit n'est plus proposé. Les couleurs restent écrites en bleu dans les CSS d'origine et converties par `theme-pierre.css` (à régénérer par `npx tsx refonte-graphique/ui-moderne/theme/pierre.ts` après tout changement de couleur).
  **v0.62.0** : plantage iPhone en changeant d'onglet (trouvé avec la boîte noire `?diag=1` de `diag.ts` et le mode `?leger=1`) : Safari gardait une copie de la planche entière des pictos (2560 × 1760) par taille de picto affichée, et de la bande de 12 images par carte de héros ; désormais une petite image par picto (`public/art/icons/<nom>.webp`, `pictos/decoupe.py`, lancé par `fabrique.py`) et par carte (`public/art/hd/pose/<id>.webp`, `vignettes.py`). Leçon : dans les menus, ne jamais afficher un morceau d'une grande planche en l'agrandissant (background-size) ni une bande animée par carte. Dock de l'accueil à écarts égaux, coffre et sablier redessinés en pierre et or ; essai de thème « pierre grise et or » par `?theme=pierre` (`ui/theme.ts`, `theme-pierre.css` généré par `refonte-graphique/ui-moderne/theme/pierre.ts`).
  **v0.61.3** : mémoire des dessins divisée par 4 (iPhone qui plantait) : planches HD à ×1 au lieu de ×2 (`UP = 1` de `jeu_export.py`, `up: 1` de `hd-meta.ts` ; réduction exacte, chaque pixel était un bloc 2×2), respirations en pied ×1 et visages `FACE = 2` (`vignettes.py`) : 914 Mo → 229 Mo pour les 64 personnages. Le jeu les agrandit lui-même (WebGL / `image-rendering: pixelated`).
  **v0.61.2** : un seul jeu Phaser en mémoire à la fois : le combat de l'accueil est libéré dès qu'un autre combat démarre (`releaseIdle` de `game-kill.ts`) ; écran du nom refait sans image (carte bleu nuit cerclée d'or).
  **v0.61.1** : plantage sur iPhone en changeant d'écran : le combat permanent de l'accueil n'est plus recréé à chaque retour (un seul jeu Phaser, mis en sommeil hors de l'accueil : `runIdle` de `idle-scene.ts`) et les autres jeux rendent leur contexte WebGL à leur fin (`game-kill.ts`). Leçon : ne jamais recréer un `Phaser.Game` à chaque affichage d'un écran.
  **v0.61.0 (26/11)** : vague 3 de l'interface — accueil sans cadres, colonnes des bords en ruban avec flèche en bas, carte des chapitres dessinée (`ui/world-map.tsx`, `sections/carte.css`), plus de bleu clair (bleu nuit + pierre/or), calendrier et boutique « premium » (`sections/boutique-*.tsx`), boutiques guilde / arène / Colisée en vitrines (`sections/boutiques-modes.tsx` `ModeShop`), Échanges et Passe refaits, passe plus riche et carte mensuelle à 200 gemmes/jour, portail d'invocation en anneau de pierre et Chances par rareté (ombres pour les héros jamais obtenus), Aventure en 6 cartes plein écran, nouvelle Guilde et boss de guilde en image de donjon de son élément (`ui/backdrop-dungeon.tsx`, boss qui tourne chaque jour : `guildBossId`), bouton Formation + choix soi-même (`placeInSlot`), portrait du joueur au choix, raretés des héros spectaculaires (`sections/cartes-heros.css`) et nouvelles raretés des 44 héros (`RARITY` de `heroes.ts` : 8 L / 12 É / 13 R / 11 C), morts et altérations en combat (`fx-death.ts`, `fx-status.ts`), cartes du combat en pied, **mode Colisée** (`core/coliseum.ts`, `core/data/coliseum.ts`, `coliseum-scene.ts`, `screens/coliseum.tsx` : duels « le gagnant reste », ligues, insignes), contrôle complet (`refonte-graphique/pixel/sortie/controle-complet/RAPPORT.md`), portraits moins zoomés (`vignettes.py` MARGIN 1.85). Leçons : images avec empreinte `?h=` (`art-url.ts`, module `virtual:art-hash` de vite.config.ts) pour ne jamais mêler vieille image et nouvelles mesures ; le jeu ne se recharge plus en pleine partie (`updater.ts`) ; `?tout=1` ouvre tout (essai, à retirer avant la bêta).
  **v0.60.0** : boutons « Pierre de l'arène » dans tout le jeu (choix du propriétaire) : `src/game/ui/buttons.ts` (dalles et galets SVG, `installButtons()`), section « Boutons » de `style.css`, `Btn` (green → basalte, gold → or, purple → arcane, red → feu, blue/ghost → ardoise), Combattre, invocations, fiche du héros, onglets, fermer/retour, guilde, aventure ; au combat les mêmes dessins (`hud-art.tsx` : AUTO allumé = basalte) ; anciens `--px-btn-*` et `FightButtonArt` supprimés ; contrôle `refonte-graphique/pixel/ui/outils/boutons-captures.cjs`, images `pixel/sortie/ui/moderne/boutons-jeu/`. Fonds des menus refaits en style moderne (dessins SVG par le code, `ui/backdrop-kit.tsx`, `sections/backdrops.css`) : Héros, Invoquer, Aventure, Guilde, pages ; préparation sur un terrain d'entraînement dessiné exprès (`formation-stage.tsx`, teinté par l'élément ennemi) ; héros plus petit sur sa fiche (`StageFigure` ×0,74).
  **v0.59.1** : attaques spéciales jamais coupées (bug de la vague d'Ilian) : `calques=True` dans `JEU` (effets partis par morceaux entiers, personnage jamais coupé), `rase` pour les vagues au sol, avertissement `seams()` de `jeu_export.py` ; contrôle des 64 : `python3 refonte-graphique/pixel/hd/anim/controle_coupes.py` (`pixel/sortie/controle-speciales/`, `coupes-verticales.md`) ; `hd-fight.ts` : morceaux recollés contre une cible large, jets étirés jusqu'à ×6.
  **v0.59.0 : style « moderne » pour tout le jeu (26/11)** : Socle (jetons, composants, `skin.css` supprimé, `px.ts` réduit, `HeroCard` = héros en entier), Campagne, combat plein écran sans bandeau (`hud-art.tsx`, `battle-scene.ts` : cartes de héros, boutons ronds, pause), Héros (page « sanctuaire » `hero-detail.tsx` `hx-*`), Invoquer (portail SVG + particules, héros invoqué en pied, plus de cartes : `sections/summon-*.tsx`), Aventure, Guilde ; 169 pictos et signes en style moderne (`refonte-graphique/ui-moderne/pictos/fabrique.py`, `ICON_CELL` 160) ; écart au milieu entre les équipes « V1 » (`BATTLE_LAYOUT` de `fight-view.ts`) ; 8 monstres devenus héros (Nyrra, Sarvik, Jessa, Oboro, Sorai, Bao, Gribou, Karu : `CLAN_HEROES`, `heroArt()` de `look.ts`) ; Garvin redessiné en roche naturelle. Leçon : après tout export HD, vérifier que `size` de `hd-meta.ts` = taille du `.webp` (un export parallèle avait laissé une entrée périmée), puis `vignettes.py`. Propositions de boutons (4 matières) : `refonte-graphique/ui-moderne/boutons/`, en attente du choix.
  **v0.58.2** : essai de 2 habillages d'interface plus actuels (A « moderne », B « hybride ») à côté de l'actuel « pixel » : `src/game/ui/skin.ts` / `skin.css`, choix par `?skin=moderne|hybride|pixel` (gardé sur le téléphone, défaut pixel). Comparaisons : `pixel/sortie/ui/essai-style/`.
  **v0.58.1** : audit des pictos (`pixel/ui/AUDIT-PICTOS.md`) : plus aucun symbole écrit (★ ✓ ✕ 🔒…) ni petit dessin à l'ancienne ; 7 pictos de plus (169), signes en pixels (`px.ts SIGNS`, `Sign`), halo animé en pixels, anciens pictos peints et `mode-icons.tsx` supprimés.
  **v0.58.0 : nouvelle DA de l'interface, vague 1 (26/11)** : fondation du style (`pixel/ui/STYLE.md`) — pièces en
  pixel art dessinées par le code (`src/game/ui/px.ts` : palette `PAL`, `installPx()` pose les variables `--px-<pièce>`, fonds
  en 9 morceaux sur un `::before`, ×2 sans flou ; `pxBg()` pour une couleur quelconque ; `pxCanvas`/`radialCanvas` pour
  Phaser). Plus d'ornements (losanges, gemmes, clous, rubans, reflets). Boutons à lèvre (enfoncés : sans lèvre), fenêtres
  cadre d'or + bandeau bleu nuit, croix et retour dessinés, plaques de titre par teinte (`TitleBanner tone`), médaillons
  en pixels à la taille exacte, barres `BarArt` (fond CSS). Section Campagne : accueil (coffre et sablier = pictos
  `chestClosed`/`chestOpen`/`hourglass`), préparation, panneau des combats (`hud-art.tsx` en pixels), fenêtres. Le combat
  se dessine dans la zone sûre (`.battle-host` : il débordait de la hauteur de l'encoche). Captures : `pixel/sortie/ui/campagne/`.
  **v0.57.2** : chargement sans héros (décor animé seul, bannière qui claque sur la crête), logo plus petit et plus coupé (viewBox).
  **v0.57.1** : chargement refait à la demande du propriétaire : illustration construite exprès (`pixel/ui/paysage.py` : crête
  rocheuse, mer de nuages, arène au loin ; Elvyn, Sylvar, Kael en pose de combat) et logo VECTORIEL HD (`pixel/ui/logo_hd.py`
  → `public/art/ui/logo.svg`, recopié dans `index.html`), plus de logo en pixels.
  **v0.57.0 : interface en nouvelle DA, partie 1** : page de chargement en pixel art HD (volcan de Kael animé, Myrr, Bérold,
  Kael face au dragon, canvas léger sans Phaser écrit par `refonte-graphique/pixel/ui/chargement.py` dans `index.html`), logo
  et icône d'application refaits (`public/art/ui-px/`), écran du nom. Plan des 9 parties : `refonte-graphique/pixel/ui/PLAN.md`.
  Tessa retouchée (cou en plumes).
  **Nouveaux noms (v0.56.0, validés le 25/11)** : Néfira (ex-Minotaure), Taurok (ex-Astérion), Ophira (ex-Méduse), Soyane
  (ex-Arachné), Malgrave (ex-Anubis), Sylvar (ex-Isis), Dardane (ex-Gabryel), Elvyn (ex-Elyon), Aurelle (ex-Auriel), Jarek
  (ex-Jinn) ; identifiants et noms de fichiers inchangés. 4 grands boss animés (dragon, léviathan, titan, oiseau-tempête).
  **v0.56.0 : jeu propre, tout en HD** (demande du 25/11 : « supprimer les anciens
  fonds et personnages, tout brancher, retirer les boutons de test »). **36 héros** (`HERO_IDS`, les 36 dessinés en HD ;
  les 36 autres retirés : une vieille sauvegarde les échange contre parchemins selon rareté et étoiles, niveaux et
  emplacements rendus, objets au sac, courrier personnel `heros-retires-2611`, `state/migrate.ts`, test
  `heros-retires.test.ts`). **Monstres par clan** (`look.ts` refait : gobelin/loup = rapide, golem = costaud,
  archer/chaman/spectre = tireur ou sorts ; boss = général du clan agrandi, ou grand boss de l'élément pour le boss du
  jour, de guilde et la **fin de chaque région**, qui devient un boss seul : `REGION_CHAPTERS`, `soloBoss` de
  `core/stages.ts`) ; boss du jour : titan (terre), léviathan (eau), dragon (feu) (`BOSS_ELEMENT`). **Décors** : celui du
  clan des ennemis dans tous les modes ; menus : image fixe du décor (`ui/fond-image.ts` ; dans une variable CSS, adresse
  complète, sinon elle se lit depuis `assets/`). **Combats** : `fight-view.ts` réécrit, uniquement HD + `hd-fight.ts`
  (grand boss seul au milieu, `BIG_BOSS_X`) ; portraits du panneau = visages HD. **Menus** : visages et héros en pied
  qui respirent, faits par `refonte-graphique/pixel/hd/anim/vignettes.py` (`art/hd/v/`, `art/hd/pied/`, `hd-figures.ts`
  léger, sans charger `hd-meta.ts`) ; **à relancer après chaque export** (grands boss compris). **Supprimés** : outils de
  test des réglages, `TEST_OPEN_ALL_MODES`, combats d'essai pixel et HD (`hd-roster`, `hd-trial`, `hd-pick`), décor imposé
  (`#fond`), couleurs d'essai (thèmes royal / crépuscule), mode Défense, décors dessinés par le code (`src/game/bg/` sauf
  `fond-px.ts`), anciens dessins (`public/art/p`, `r`, `c`, `t`, `fx`, `px` sauf `fonds/`, `public/apercu`),
  `art-meta.ts`, `pixel-meta.ts`, dessins provisoires d'`art.ts`, et leurs chaînes (`art-jeu.py`, `decoupe-hailuo.py`,
  `decoupe-decors.py`, `rig*.py`, `rig/`, `rig-out/`, `recadre.py`, `adoucir.py`, `pixel/jeu.py`, `fond.py`, `page.py`).
  Vérifié dans le vrai jeu (Playwright, 390 × 844 et 360 × 640) : `refonte-graphique/pixel/sortie/jeu-propre/`.
  Les 4 grands boss (dragon, léviathan, titan, oiseau-tempête) sont branchés. Test `clans.test.ts` (chaque monstre des
  règles a son dessin HD dans tous les modes). Note : Chromium sans carte graphique tourne à ~9 images/s, les combats y
  paraissent lents (pas sur un téléphone).
  **v0.55.0 : 8 fonds de combat pixel art HD animés, un par clan** (Eldra, Arachné, Méduse, Kael, Orin, Barzul, Lenore,
  Kesha) : dessinés par `refonte-graphique/pixel/fonds/<clan>/build.py` (outillage `fondlib.py`, LISEZMOI.md), mis au jeu par
  `fonds/jeu.py` → `public/art/px/fonds/`, `src/game/fond-meta.ts`, `src/game/bg/fond-px.ts`. Un fond par région de la campagne
  (et l'accueil), combat HD d'essai = clan des ennemis, Outils de test → « Décor des combats ». Tour, donjons, boss, arène :
  anciens décors pour l'instant.
  **v0.54.0 : les 60 personnages HD dans le combat d'essai** : fenêtre de choix (5 héros, 5 monstres, « Au hasard »,
  « Les 60 à la suite » en 6 manches), `src/game/hd-roster.ts`, `ui/screens/hd-pick.tsx`. Export corrigé (`jeu_export.py` garde
  l'image rendue par compose ; vitesse/pente mesurées ; clés `retour`, `rase`, `avant`, `visage`). 8 fonds pixel HD animés
  en préparation (`refonte-graphique/pixel/fonds/`, pas encore branchés).
  **v0.53.0 : combat HD d'essai** (Réglages → Outils de test → « Combat HD (essai) ») : Eldra, Myrr, Jinn contre matelot,
  sorcier oni, salamandre, avec les animations HD. Corps à corps : le personnage va jusqu'à sa cible ; tirs : le projectile
  va jusqu'à la vraie case ; spéciales : halo de charge doux. Export des animations : `refonte-graphique/pixel/hd/anim/jeu_export.py`
  (dictionnaire `JEU` dans chaque build.py, consigne `hd/consignes/export-jeu.md`) → `public/art/hd/`, `src/game/hd-meta.ts` ;
  jeu : `src/game/hd-fight.ts`, `hd-trial.ts`. Les autres modes gardent les anciens dessins.
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


## Refonte en vectoriel animé (26-27/11/2026) : héros, dragons, monstres

- **Héros** : les 44 héros redessinés en vectoriel lisse et animés (repos, attaque, spéciale), modèle Kael
  (`refonte-graphique/ui-moderne/heros/<nom>/`, outil `atelier.py`, visage par `visage.py`). Visibles dans les menus avec
  `?vecto=1` (table `VECTO` de `src/game/vecto.ts`) ; le combat utilise encore le pixel art HD.
- **Avis du propriétaire** : 4 tours sur la page https://claude.ai/artifact/D5UVkXKfKg8AmFzy5Ezart (archives
  `heros/avis/historique-1..4/`). Leçons retenues (à appliquer à tout nouveau dessin) : visages cohérents (visage.py),
  un seul œil sur les têtes de profil, dents qui partent de la bouche, cheveux et crinières nés du crâne, épaules fondues
  dans le buste (méthode d'Aurelle, `FigureM`), oreilles/becs/museaux soudés au crâne, colliers et ceintures sur une
  seule courbe, objets tenus de façon crédible, rien de vide entre les jambes, aucun motif répété (rayures, rayons,
  grillage de plaques), deux cornes bien visibles.
- **Rook** : le phénix est remplacé par un chevalier (heaume, armure noir/gris, touches rouge sang, épée de feu, aura) ;
  même id `assassins-5`, nom provisoire. Ysolde porte un bandana.
- **3 nouveaux dragons** de la famille d'Elvyn (eau) : Brasyr feu, Rocvar terre, Venthys vent (images `dragon-*`).
  Dessinés seulement : pas encore dans les données du jeu ni au combat (à faire quand le propriétaire valide).
- **Monstres** : les 16 monstres de clan restants + 4 grands boss redessinés
  (`refonte-graphique/ui-moderne/monstres/<nom>/`), page d'avis à part https://claude.ai/artifact/JgkepjcHadyFrT3UUpMqD8
  (`avis.py --monstres`, archive `heros/avis-monstres/historique-1/`). Tour 1 de l'avis : 6 corrigés (canonnier, oni
  brute, léviathan, dragon redevenu élancé, diablotin, moine tengu).
- Questions encore ouvertes avec le propriétaire : nom du chevalier Rook ; noms des dragons ; trou d'eau ovale du
  léviathan (« jamais de rond au sol ») ; sourires ouverts de certains monstres ; épaulière ronde du gorille.
- Reste à faire : passer le combat aux dessins vectoriels ; mettre les 3 dragons dans le jeu (statistiques, compétences,
  textes FR/EN) ; nouveaux tours d'avis.
- **Fonds de combat** (27/11) : les 8 fonds de clan refaits en vectoriel animé (volcan de Kael en pilote, puis les 7 autres
  en même temps), recadrés pour le vrai écran de combat, chacun avec une touche vivante au loin (dragons, chauves-souris,
  serpents ailés, raies et serpent de mer, mouettes et voilier, corbeaux, grues et singe). Branchés derrière `?vecto=1`
  seulement ; sorties et vraies captures dans `refonte-graphique/pixel/sortie/ui/vecto/fond-<clan>/`.
- **Bascule (v0.65.0, 27/11)** : les 67 personnages (47 héros dont les 3 dragons et les 8 héros de clan, les monstres de
  clan, les 4 grands boss) réexportés pour le combat, effets reçus et fonds vectoriels branchés partout, sans drapeau ;
  le pixel art et ses chaînes sont supprimés (voir la ligne v0.65.0 plus haut et `EXPORT-JEU.md`). Les outils de
  comparaison pixel / vectoriel (`presentation.py`, `pixel_frames` de certains `anim.py`) n'ont plus d'objet et ne
  marchent plus. Mémoire graphique d'un combat complet : ~75 à 85 Mo de textures (le fond vectoriel ×2 du clan pèse
  23 à 26 Mo, la planche des pictos 18 Mo, 9 planches de personnages ~30 Mo).
