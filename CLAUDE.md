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
- **Univers** : style manga inspiré de Black Clover, mais aucun nom, personnage, symbole ou histoire repris.
- **Langues** : français et anglais dès le départ ; aucun texte écrit en dur dans le code de l'interface.
- **Supabase** : ne rien lire ni modifier sans l'accord explicite du propriétaire, ne jamais lui demander de
  clé dans la conversation. Décidé : au début de l'étape 3, supprimer l'ancien projet Fuze Arena (après une
  sauvegarde) pour faire de la place ; garder le projet AVA.
- Code en anglais (noms de variables), commentaires et textes pour le propriétaire en français.
