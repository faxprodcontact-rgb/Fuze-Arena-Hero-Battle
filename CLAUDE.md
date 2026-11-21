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
