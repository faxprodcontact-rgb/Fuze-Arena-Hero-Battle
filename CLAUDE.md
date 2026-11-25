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
  avant chaque combat ; réglages par l'avatar (plus aucun outil de test dans le jeu depuis la v0.56.0 : les modes
  s'ouvrent avec la campagne, `UNLOCKS` de `src/core/data/modes.ts`).
- Décidé : plus de camps ; la fusion demande des héros du **même élément**. Le mode Défense est supprimé, remplacé par le
  **Colisée** (duel 1 contre 1, équipes de 3) dont **les règles restent à construire** (tuile « Bientôt », clé `defense`).
- Héros : **36 héros**, tous dessinés et animés en pixel art HD (`HERO_IDS` de `src/core/data/heroes.ts` ; les 36 autres
  gabarits sont retirés, une vieille sauvegarde reçoit un dédommagement par courrier : `src/game/state/migrate.ts`).
  Effets dans `src/core/battle/`, textes par `src/game/describe.ts`, équipements dans `src/core/data/items.ts`. Courrier :
  `src/core/data/mail.ts` (un `id` unique, jamais réutilisé ; `personal` = cadeau rangé dans la sauvegarde). Tutoriel :
  `src/game/ui/tutorial.tsx` (il vise les éléments par sélecteurs CSS).
- **Tout le jeu est en pixel art HD** (v0.56.0) : `refonte-graphique/pixel/hd/` (lire `hd/GUIDE.md` ; pour reprendre :
  `hd/consignes/REPRISE.md` ; suivi du propriétaire : https://claude.ai/artifact/SB9xsSLSYbExWSV89HQfaj, `hd/suivi.py`).
  Chaîne : dessin `.txt` → animation `hd/anim/<nom>/build.py` → `hd/anim/jeu_export.py`
  (`public/art/hd/<id>.webp`, `src/game/hd-meta.ts`, consigne `hd/consignes/export-jeu.md`) → **`python3
  refonte-graphique/pixel/hd/anim/vignettes.py`** (visages `art/hd/v/`, respiration en pied `art/hd/pied/`,
  `src/game/hd-figures.ts` pour les menus). Au combat : `src/game/hd-fight.ts` (corps à corps jusqu'à la cible,
  projectile jusqu'à la vraie case, lumière de charge, sorts d'équipe et effets reçus `art/hd/fx/`).
- **8 clans** (2 par élément : Arachné et Méduse = terre, Kesha et Barzul = eau, Lenore et Kael = feu, Orin et Eldra =
  vent) : un général (héros HD, joue les boss, dessiné plus grand), 3 monstres `mon-<clan>-<rôle>` et un décor animé
  (`refonte-graphique/pixel/fonds/`, `public/art/px/fonds/`, `src/game/fond-meta.ts`, `src/game/bg/fond-px.ts`).
  `src/game/look.ts` choisit le clan et son décor selon le mode (campagne : région + élément du chapitre ; tour ; donjons ;
  boss ; arène). **Grands boss** (un par élément, `hd/boss/`, ids `boss-feu`, `boss-eau`, `boss-terre`, `boss-vent`) :
  boss du jour, de guilde et fin de chaque région (seul, au milieu) dès qu'ils sont exportés, sinon le général du clan.
  Décors : une plateforme rectangulaire d'un bord à l'autre (**jamais de rond au sol**), tout est posé.
- Anciens essais graphiques (pas dans le jeu) : personnages redessinés par le code `refonte-graphique/vecto/` (page
  https://claude.ai/artifact/5qE3vDUzsMFMQVC4ywqLrK, lire
  `vecto/GUIDE.md`) ; pixel art « gros pixels encrés » `refonte-graphique/pixel/persos/` (lire `pixel/GUIDE.md`, contrôle
  `python3 refonte-graphique/pixel/controle.py <nom>`). Les anciens dessins (Hailuo, décors dessinés par le code, 72 héros
  pixel) et leurs chaînes de fabrication sont supprimés (v0.56.0) ; pictos : `icons.webp`, tous en pixel art
  (`refonte-graphique/pixel/ui/pictos/`, `assemble.py` ; petits signes et halo dessinés par `src/game/ui/px.ts`).
- **Interface en nouvelle DA (pixel art HD), partie par partie** (demande du 25/11) : plan, inventaire et outils dans
  `refonte-graphique/pixel/ui/` (lire `PLAN.md`) ; partie 1 faite en v0.57.0 (chargement, logo, icône d'application).
  **Style commun (26/11) : lire `refonte-graphique/pixel/ui/STYLE.md`** (pièces en pixels de `src/game/ui/px.ts`, variables
  `--px-…`, aucun ornement) ; section Campagne faite, vague 2 : Héros, Invoquer, Aventure, Guilde.
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
| `src/game/hd-fight.ts` + `hd-meta.ts` | Personnages HD au combat : leurs planches (générées par `jeu_export.py`) et leur mise en scène |
| `src/game/look.ts` | Clan des monstres, général, grand boss et décor animé de chaque combat (`bg/fond-px.ts`, `fond-meta.ts`) |
| `src/game/art.ts` + `hd-figures.ts` | Couleurs, visages et héros en pied des menus (générés par `vignettes.py`) |
| `src/game/i18n.ts` | Tous les textes, français et anglais |
| `simulations/` | Joueurs virtuels qui jouent des mois en accéléré pour vérifier le rythme |
| `tests/` | Tests automatiques des règles |
| `docs/` | Résultats des simulations |

Commandes : `npm run dev` (jeu en local), `npm run build` (construit `dist/`), `npm test` (tests),
`npm run verifier` (vérification du code), `npm run simuler` (rapport de progression),
`npm run simuler -- --calibrer` (recalcule la difficulté de la campagne, à recopier dans `src/core/data/campaign.ts`),
`npm run combat` (force des monstres à puissance égale), `npx tsx simulations/premiers-jours.ts` (première semaine du
vrai jeu jouée par un joueur automatique).

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
