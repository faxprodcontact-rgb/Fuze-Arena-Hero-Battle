# Audit des pictos (25/11/2026) — « vérifie dans le jeu si vraiment tous les pictos ont été réalisés »

## Comment on a cherché

- **Dans le code** : tous les dessins SVG, les symboles écrits (★ ✓ ✕ 🔒 👆 ⚄ ⧉ ▲ ∅ ✚ ✦ ‹ › »), les contenus des `::before` /
  `::after` du CSS, les pastilles dessinées en dégradés, les images peintes, les pictos de secours de `kit.tsx`, les
  pictos animés de `mode-icons.tsx` et `anim.tsx`, les signes écrits par Phaser au combat.
- **Dans le vrai jeu** : `outils/pictos-audit.cjs` ouvre **tous les écrans et toutes les fenêtres** (accueil et ses bords,
  réglages, quêtes, boutique ×3, classement, tchat, chances, fragments, confirmation, publicité, butin rapide, carte des
  régions, nom, fusion, forge, renaissance, mission, donjons, amis, connexion, courrier, objet, mentions légales, victoire,
  défaite, préparation, fiche d'un héros ×3, onglets Héros / Invoquer / Aventure / Guilde, les 6 modes, guilde rejointe,
  tirage, combat, tutoriel) en **390 × 844 avec encoche et 360 × 640**, et relève tout petit dessin qui n'est pas un picto
  pixel art de la planche. Captures avant | après : `../sortie/ui/audit-pictos/`.

Résultat : les **162 pictos de la planche** étaient bien tous refaits en pixel art. Mais **une trentaine de petits signes
et dessins n'étaient pas dans la planche** (écrits avec des caractères, dessinés en SVG ou en CSS) : ils sont maintenant
tous en pixel art.

## Ce qui restait, et ce qui est fait

| Ce qui restait (ancien style) | Où on le voyait | Fait |
|---|---|---|
| Étoiles des héros écrites `★★★★★` (jaunes et rouges) | partout : cases des héros, préparation, fiche, fusion, renaissance, tirage, chances | étoiles en pixels `--px-star` / `--px-star-red` (`Stars` de `kit.tsx`), contours qui se chevauchent, nettes (×2) |
| Coffres des quêtes en SVG peint (`Chest` de `anim.tsx`, 3 états) | Quêtes (barre d'activité) | pictos `chestClosed` / **`chestReady`** (nouveau : le couvercle se soulève, la lumière passe) / `chestOpen` ; le coffre prêt sautille. Le coffre de l'accueil prend aussi `chestReady` quand le butin est prêt |
| Halo de runes en SVG lisse (`Halo`) | victoire, fusion réussie, tirage rare, fiche d'un Légendaire | halo en pixel art dessiné par `haloStrip()` de `px.ts` (lueur en paliers, anneau, 8 signes inventés qui tournent, 4 étincelles qui clignent), 16 images jouées par `steps()`, à la couleur demandée |
| Sablier SVG (`Hourglass`) | plus utilisé (l'accueil a le picto `hourglass`) | supprimé |
| 6 pictos animés des modes en SVG (`mode-icons.tsx`) | plus affichés (remplacés par la planche) | fichier supprimé, l'Aventure appelle directement les pictos `tower`, `missions`… |
| 38 pictos de secours en SVG (`ICONS` de `kit.tsx`) | jamais (tous les noms sont dans la planche) | supprimés ; `Icon` ne montre plus que la planche |
| Attributs de la fiche (8 dessins SVG) | fiche d'un héros | pictos de la planche `hp`, `atk`, `def`, `speed`, `crit`, `critDmg`, `dodge`, `tenacity` |
| Renaissance (SVG) et « tous les éléments » (4 losanges SVG) | onglet Héros | picto `rebirth` ; **`allElements`** (nouveau : 4 perles feu / vent / eau / terre) |
| Chevrons ‹ › de la fiche, lecture ▶ / arrêt ■ de l'aperçu (SVG) | fiche d'un héros | signes en pixels `chev`, `play`, `stop` |
| ✓ / + du bouton « dans la section », ▲ « mieux », ★ du palier de talent | fiche, sac, objets | signes `check`, `op-plus`, `up`, `star` |
| Coche ✓ en pastille dégradée sur une case choisie | Héros, préparation, fusion, renaissance | `--px-check` (sans pastille) |
| ✕ sur un héros fatigué | préparation (tour, arène…) | `--px-cross` |
| ✓ sur un objet choisi (recyclage) | sac | `--px-check` sur le voile rouge |
| 🔒 et ✔ sur la carte des régions | carte des régions | picto `lock`, signe `check` |
| 🔒 devant un niveau de donjon fermé | donjons | picto `lock` |
| 👆 (émoji) du tutoriel et » (bouton rond dégradé) pour le passer | tutoriel | picto **`hand`** (nouveau : la main « curseur », index levé) qui tapote ; bouton carré en pixels `--px-next` |
| ⚄ (caractère) du nom au hasard, bouton dégradé | écran du nom | picto **`dice`** (nouveau) sur un bouton crème en pixels |
| ⧉ (caractère) « copier mon code » | amis | picto **`copy`** (nouveau) |
| ✕ retirer un ami, ✕ vider la sélection | amis, sac | signe `cross` |
| ✓ / ★ en pastille violette dégradée | fusion (héros prêt, 2 choisis) | signes `check`, `star` |
| ★ et ✓ (caractères) des récompenses de connexion | connexion | picto `star`, signe `check` |
| ∅ courrier vide, ✓ courrier pris | courrier | picto `mail` grisé, signe `check` |
| `+`, `=`, `→` écrits entre les cases | fusion, forge, renaissance | signes `op-plus`, `op-eq`, `op-arrow` |
| › des lignes de réglages et du bandeau « Section », ‹ du bouton Retour des modes | réglages, arène, Héros, modes | signes `chev-s`, `back-s` |
| ★ écrit dans « 2 héros ★3+ » et « Éveil ★10 » | missions, fiche | étoile dessinée (`starText`) |
| ? sur les adversaires inconnus | Colisée | picto **`unknownHero`** (nouveau : silhouette encapuchonnée, deux yeux qui luisent) |
| « ✓ » / « ★ » en petit message | après une forge, une renaissance, un nom, une étoile | le signe dessiné (`TOAST_SIGNS` de `app.tsx`) |
| `+` rond dégradé sur une place d'objet vide | fiche (objets) | `--px-plus` |
| pastilles rondes dégradées (courrier non lu, cadeau d'ami en attente) | courrier, amis | `--px-badge`, `--px-badge-gold` |
| Combat : « ✚ » écrit quand un héros se relève, « ✦ » qui tourne quand un coup étourdit | tous les combats (Phaser) | picto **`revive`** (nouveau : croix verte) ; picto `st-stun` qui saute |
| 162 anciens pictos peints (`refonte-graphique/pictos/*.webp`) gardés « au cas où » par `assemble.py` | plus dans le jeu | supprimés ; `assemble.py` ne prend plus que les pictos pixel art |

Nouveaux pictos de la planche (famille `pictos/signes.py`) : `chestReady`, `hand`, `dice`, `copy`, `allElements`, `revive`,
`unknownHero` (planche : `../sortie/ui/audit-pictos/pictos-nouveaux.png`). Nouveaux petits signes dessinés par le code
(`SIGNS` de `src/game/ui/px.ts`, composant `<Sign>` de `kit.tsx`, variables CSS `--px-<signe>`) : `star`, `star-red`,
`check`, `cross`, `up`, `chev`, `chev-s`, `back-s`, `play`, `stop`, `op-plus`, `op-eq`, `op-arrow` ; boutons `--px-next`,
pastille `--px-badge-gold`. La planche compte maintenant **169 pictos** (33 Ko, sans perte).

## Pas des pictos (laissés tels quels)

Du vrai texte, à garder en texte : `×10`, `×1` (quantités), `+10`, `%`, `1 / 2`, `·`, `→` à l'intérieur d'une phrase
(« ATQ +12 % → +15 % »), `×2` de la vitesse du combat, les émojis tapés par les joueurs dans le tchat. Le `★` de deux
phrases traduites (« 2 héros ★3+ », « Éveil ★10 ») reste dans le texte i18n mais s'affiche en étoile dessinée (`starText` de
`kit.tsx`). Les boutons croix / retour (`.x`) gardent leur caractère pour les
lecteurs d'écran, mais il est caché : on voit le dessin en pixels.

## Laissé pour la vague 2 (grands dessins, pas des pictos)

| Quoi | Fichier | Partie |
|---|---|---|
| Décors des onglets et des pages (salle des héros, invocation, aventure, guilde, pages) | `ui/backdrop*.tsx` | décors |
| Portail d'invocation, scène du tirage, éclat, décor du tirage | `ui/portal.tsx`, `portal.css`, `ui/summon-stage.tsx` | Invoquer |
| Dos des cartes du tirage, boule du tirage (`TeaseOrb`) | `ui/card-back.tsx`, `screens/summon.tsx` | Invoquer |
| Petits décors des tuiles de l'Aventure | `ui/tile-scene.tsx` | Aventure |
| Scène et socle de la fiche d'un héros | `ui/hero-scene.tsx` (`Pedestal`) | Héros |
| Plateau de la préparation (sol, dalles) | `ui/formation-stage.tsx` | préparation |
| Carte du monde (peinte) | `public/art/ui/map.jpg` (`screens/campaign.tsx`) ; sa chaîne `refonte-graphique/decoupe-pictos.py` + `hailuo-v1/` : **ne plus lancer `decoupe-pictos.py`** (elle remettrait les anciens pictos peints) ; à retirer avec la carte | partie 9 |
| Pastilles encore en dégradés lisses autour des pictos : filtres d'éléments (`.el-pick`), boutons de la fiche (`.hp-team`, `.hp-play`), visages ronds (`.team-face`), étiquette « Mythique », reflet qui tourne sur les médaillons de l'accueil (`.edge-icon::before`), carrés de couleur des chances | `style.css` | Héros / accueil |
| Anneau bleu du bouclier au combat (un cercle tracé par Phaser : un effet, pas un picto) | `fight-view.ts` | combat |

## Pour vérifier à nouveau

    npx vite --port 4392
    node refonte-graphique/pixel/ui/outils/pictos-audit.cjs <dossier> 4392 --shots
    # <dossier>/audit.txt : chaque trouvaille une fois, avec les écrans où elle apparaît
    python3 refonte-graphique/pixel/ui/outils/avant-apres.py <avant> <après> <sortie> fiche-390x844 …

Il ne doit plus rester dans `audit.txt` que les grands dessins de la vague 2 (lignes `svg` de 100 px et plus), du texte
normal et les images `data:` (les pièces dessinées par `px.ts`).
