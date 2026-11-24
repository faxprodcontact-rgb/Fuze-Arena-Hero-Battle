# Fuze Arena – Hero Battle — notes pour Claude

Jeu mobile de héros automatique (style AFK Arena / Idle Heroes / Hero Wars), destiné à l'App Store puis
Google Play. Le propriétaire n'est pas développeur : lui répondre en français, simplement, sans jargon.

- Cahier de conception (la référence, document vivant, à lire avec les outils de documents Claude) :
  https://claude.ai/artifact/EBxryovSeVavxCCEd4koMv
- Résultats des simulations d'équilibrage : `docs/simulations.md`.

## Où en est le projet

Le journal détaillé de chaque version (décisions, leçons, outils de contrôle) est dans `docs/journal.md` : y chercher
une partie (`grep -n`) avant de la retoucher, plutôt que de tout relire.

- Étapes 1 (conception) et 2 (prototype du combat) faites. En cours : **interface et graphismes** (le propriétaire
  veut l'interface parfaite avant la suite), sur la version complète jouable hors ligne (sauvegarde sur le téléphone).
- Site de test : https://faxprodcontact-rgb.github.io/Fuze-Arena-Hero-Battle/ — mis en ligne à chaque envoi par
  `.github/workflows/site-test.yml` (branche `gh-pages`, jamais à la main). Les téléphones se mettent à jour seuls
  (`src/game/updater.ts`, `version.json`). Copie claude.ai : https://claude.ai/artifact/EigGhykFPgfeb7L1UoYfDX (`dist/`,
  CSS dans la page, plusieurs fichiers `assets/` : publier les nouveaux, retirer les anciens), à republier à chaque envoi.
- Publier : changer `src/game/version.ts`, `npx tsc --noEmit`, `npm test`, `npm run build`, une note courte dans
  `docs/journal.md`, commit, envoi, copie claude.ai.
- Disposition (inspirée d'AFK Arena / Idle Heroes) : accueil = combat permanent (`idle-scene.ts`) avec médaillons sur
  les bords (colonnes repliables), coffre / Combattre / butin rapide en bas ; écran de préparation (`screens/prep.tsx`)
  avant chaque combat ; réglages par l'avatar. Outils de test à retirer avant la bêta : `TEST_OPEN_ALL_MODES`
  (`src/core/data/modes.ts`) et les « Outils de test » des réglages.
- Décidé : plus de camps ; la fusion demande des héros du **même élément**. Le mode Défense est retiré, remplacé par le
  **Colisée** (duel 1 contre 1, équipes de 3) dont **les règles restent à construire** (tuile « Bientôt », clé `defense`).
- Héros : 72 gabarits dans `src/core/data/heroes.ts` (noms provisoires), effets dans `src/core/battle/`, textes par
  `src/game/describe.ts`, équipements dans `src/core/data/items.ts`. Courrier : `src/core/data/mail.ts` (un `id` unique,
  jamais réutilisé). Tutoriel : `src/game/ui/tutorial.tsx` (il vise les éléments par sélecteurs CSS).
- Dessins du jeu : 144 personnages peints par Hailuo, découpés et animés morceau par morceau (`public/art/p/`, `r/`,
  `c/`, `art-meta.ts` ; chaîne de découpe et contrôles : voir le journal, v0.35.4 à v0.36.1). Pictos : `icons.webp`.
  `src/game/look.ts` choisit décor et famille de monstres selon le mode et le chapitre.
- **Personnages redessinés par le code** (en cours, un par un) : `refonte-graphique/vecto/` — **lire
  `refonte-graphique/vecto/GUIDE.md` avant d'y toucher** (méthode économe, outils, file d'attente). Page d'exemple :
  https://claude.ai/artifact/5qE3vDUzsMFMQVC4ywqLrK . Pas encore branchés dans le jeu.
- **Pixel art « gros pixels encrés »** (style retenu pour les héros) : `refonte-graphique/pixel/` — **lire
  `refonte-graphique/pixel/GUIDE.md` avant de dessiner** (DA, proportions, tête pixel par pixel, pas de trait aux
  articulations, ordre premier/second plan, refus passés). Mannequin à recopier : `persos/_gabarit.py` ; contrôle
  obligatoire avant de montrer : `python3 refonte-graphique/pixel/controle.py <nom>`. **Les 72 héros** (v0.52.0) et 5 monstres
  (ancien style) sont dans le jeu à la place des anciens : `python3 refonte-graphique/pixel/jeu.py` (`public/art/px/`,
  `pixel-meta.ts`), combat d'essai dans les Outils de test. **Refonte HD en cours** (36 héros choisis, ~96 px, dessinés pixel par pixel par des agents) : `refonte-graphique/pixel/hd/` (lire `hd/GUIDE.md`), page de suivi pour le propriétaire https://claude.ai/artifact/SB9xsSLSYbExWSV89HQfaj (`python3 refonte-graphique/pixel/hd/suivi.py` puis republier `hd/sortie/suivi.html` à chaque changement ; états dans `VALIDES`, `RETOUCHES`, `FAITES`). **Pour reprendre : lire `refonte-graphique/pixel/hd/consignes/REPRISE.md`** (consignes des agents, méthode, où on en est).
- Décors de combat dessinés par le code : `src/game/bg/` (un fichier par décor, `scenes.ts`). Règles : une plateforme
  rectangulaire d'un bord à l'autre (**jamais de rond au sol**), tout est posé, ordre des calques fixé (voir journal
  v0.38.0). Outil de test : `#fond=<terrain>`.
- Interface (v0.39 à v0.41) : polices **Lilita One** (titres, chiffres) et **Fredoka** (textes), `font-synthesis: none`,
  jamais `fontStyle: 'bold'` dans Phaser. Couleurs : **émail bleu nuit cerclé d'or** (le bois brun est refusé),
  panneaux parchemin ; variables en tête de `src/game/ui/style.css`. Pièces dessinées : `ui/chrome.tsx` (`ChromeDefs`
  posé une fois, jamais caché ; `BarArt` toujours **dernier enfant** de sa barre). **Toutes les fenêtres s'ouvrent au
  milieu de l'écran.** Décors des onglets et pictos animés dessinés par le code (`ui/backdrop-*.tsx`, `mode-icons.tsx`,
  `portal.tsx`, `anim.tsx`). Combats : panneau `hud-art.tsx`. Tirage des héros : `SummonResult` + `ui/card-back.tsx`.
- Plus tard : profil du joueur, événements, sons et musique, Siège. Ensuite : serveur (Supabase) → habillage → social
  réel → argent réel → bêta → lancement.

### Leçons à garder (demandes du propriétaire)

- Plus aucune rayure ni hachure, ni rayons répétés ; signes inventés, jamais de lettres ; une seule lumière (en haut à
  droite) ; tout élément est posé au sol ; de l'air autour du sujet ; sous une grille de tuiles, un décor calme.
- Un seul contour par personnage ou objet dessiné, ombres douces entre les morceaux (jamais un contour par morceau).
- Écrans sans défilement quand c'est possible (vérifier sur plusieurs tailles de téléphone, encoche comprise).
- Ne jamais cacher un `TitleBanner` par `display: none` (dégradés partagés) ; dans le CSS, jamais `url(art/…)` (passer
  l'adresse par un `style` dans le TSX) ; depuis les menus, passer par `src/game/scenes.ts` pour lancer un combat.
- « Main droite », « œil gauche » = ceux **du personnage** (à gauche de l'image pour sa droite).
- Avant de montrer un dessin : le regarder en grand, vérifier la liste de contrôle de `refonte-graphique/LISEZMOI.md`,
  et le montrer dans l'écran réel du jeu.

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
- **Économie de crédits** (demande du propriétaire) : pas d'agents en parallèle ni de relecteur sans son accord ; peu
  d'images, petites, sur la zone utile ; lire les fichiers par morceaux (`grep -n`, `sed -n`) ; une conversation par
  petite tâche (le propriétaire vérifie lui-même et dit ce qu'il faut reprendre).
