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
  **Colisée** (v0.61.0 : 3 héros, duels 1 contre 1 « le gagnant reste », ligues de 30, insignes ; `src/core/coliseum.ts`, clé `defense` gardée).
- Héros : **44 héros** (36 de `HERO_IDS` + 8 monstres de clan devenus héros, `CLAN_HEROES`, dessin par `heroArt()` de `look.ts`), tous dessinés et animés en pixel art HD (`HERO_IDS` de `src/core/data/heroes.ts` ; les 36 autres
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
  pixel) et leurs chaînes de fabrication sont supprimés (v0.56.0) ; pictos : `icons.webp`, en style moderne (v0.59.0)
  (`refonte-graphique/ui-moderne/pictos/fabrique.py` ; l'ancienne chaîne pixel `pixel/ui/pictos/assemble.py` demande `--pixel` ; petits signes (SVG lisses) et halo : `style.css`, `anim.css`).
- **Interface en nouvelle DA (pixel art HD), partie par partie** (demande du 25/11) : plan, inventaire et outils dans
  `refonte-graphique/pixel/ui/` (lire `PLAN.md`) ; partie 1 faite en v0.57.0 (chargement, logo, icône d'application).
  **Style « moderne » choisi le 26/11 : lire `refonte-graphique/pixel/ui/STYLE.md`** (jetons en tête de
  `src/game/ui/style.css` : fond raisin, couleurs à rôle, arrondis, ombres douces ; fenêtres claires à bandeau coloré ;
  plus de pièces en pixels ni de `?skin=`) ; tout le jeu est passé (v0.59.0), sections dans
  `src/game/ui/sections/<section>.css` ; **boutons « Pierre de l'arène »** (v0.60.0, `ui/buttons.ts`, classes `bt-<teinte>`) ; **habillage pierre grise et or** (v0.63.0 : `ui/theme.ts` + `theme-pierre.css` GÉNÉRÉ par `npx tsx refonte-graphique/ui-moderne/theme/pierre.ts` : le relancer après tout changement de couleur dans un CSS) ;
  fonds des menus dessinés par le code (`ui/backdrop-kit.tsx`, `backdrop-*.tsx`, préparation `formation-stage.tsx`). Personnages, monstres, décors restent en pixel art HD.
- Interface : polices **Lilita One** (titres, chiffres) et **Fredoka** (textes), `font-synthesis: none`, jamais
  `fontStyle: 'bold'` dans Phaser. Composants communs : `ui/kit.tsx` (`HeroCard` = le héros en entier, `CardFigure`),
  `ui/chrome.tsx` (`ChromeDefs` posé une fois, jamais caché ; `BarArt` toujours **dernier enfant** de sa barre).
  **Toutes les fenêtres s'ouvrent au milieu de l'écran.** Combat plein écran, interface qui flotte dessus (pause, pilules,
  AUTO/vitesse ronds, cartes des héros) : `hud-art.tsx` + `battle-scene.ts`. Tirage : `sections/summon-reveal.tsx` (le héros sort du portail, plus de cartes).
- **Connexion Google / Apple** (26/11) : étape « Bienvenue » avant le nom (`NameScreen`), ligne du compte dans les
  Réglages, invité par défaut (champ `auth` de la sauvegarde) ; tout passe par `src/game/auth.ts` (éteint tant que
  `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` manquent : fenêtre « Bientôt disponible »). Comptes à créer, branchement,
  invité → compte lié : **`docs/connexion-comptes.md`**.
- **Refonte des héros en vectoriel animé** (décidée le 26/11 après l'essai de Kael) : un héros = un dossier
  `refonte-graphique/ui-moderne/heros/<nom>/` (outil commun `atelier.py`, modèle `kael/`), sorties `pixel/sortie/ui/vecto/<nom>/`
  (`STATUT.txt`), images `public/art/vecto/<id>.webp`, table `VECTO` de `src/game/vecto.ts` (menus, `?vecto=1`).
  Page de suivi : `python3 refonte-graphique/ui-moderne/heros/suivi.py` → https://claude.ai/artifact/L59gwsBUz9SPcEG272Jh4c.
  **Visage : toujours construit avec `heros/visage.py`** (placer / verifier / guide_svg ; contrôle `visage.png`), le plus gros
  défaut relevé par le propriétaire (yeux, nez, bouche incohérents ; nez de profil sur un visage de 3/4).
  Avis du propriétaire (notes, cercles au doigt, OK / à reprendre) : `python3 refonte-graphique/ui-moderne/heros/avis.py`
  → https://claude.ai/artifact/D5UVkXKfKg8AmFzy5Ezart (republier avec root = dépôt et `avis/fichiers.json` ; ses notes se lisent
  avec ArtifactData, collection `avis`, un document par héros : text, status ok/redo, strokes en 0-1000).
  **3 nouveaux dragons** (27/11, même famille qu'Elvyn = eau) : Brasyr feu, Rocvar terre, Venthys vent (`heros/brasyr|rocvar|venthys/`,
  images `dragon-feu|terre|vent`), dessinés seulement : pas encore dans les données du jeu ni au combat (liste `NOUVEAUX` de `suivi.py`).
- Plus tard : profil du joueur, événements, sons et musique, Siège. Ensuite : serveur (Supabase) → habillage → social
  réel → argent réel → bêta → lancement.

### Leçons à garder (demandes du propriétaire)

- Plus aucune rayure ni hachure, ni rayons répétés ; signes inventés, jamais de lettres ; une seule lumière (en haut à
  droite) ; tout élément est posé au sol ; de l'air autour du sujet ; sous une grille de tuiles, un décor calme.
- Un seul contour par personnage ou objet dessiné, ombres douces entre les morceaux (jamais un contour par morceau).
- **iPhone (Safari) plante par manque de mémoire graphique** (26/11) : jamais de flou SVG (`feGaussianBlur`) sur une grande
  forme, jamais un morceau de grande planche affiché en l'agrandissant (une image par picto : `art/icons/<nom>.webp`),
  jamais de bande d'images animée par carte, un seul `Phaser.Game` à la fois. Outils utilisés pour le
  trouver (boîte noire `?diag=1`, `?leger=1`, test automatique `?bisect=1`) : retirés en v0.63.2, à retrouver dans
  l'historique git (`src/game/diag.ts`) si un plantage revient.
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
