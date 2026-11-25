# L'interface en pixel art HD — inventaire et plan (demande du propriétaire, 25/11/2026)

« Refais la page de chargement du jeu avec les nouveaux designs, et passe tous les pictos etc. à la nouvelle DA. J'aimerais
tout repasser à la nouvelle DA, fait par partie, et connecte au jeu. »

La nouvelle DA = celle des 36 héros, des monstres, des 4 grands boss et des 8 fonds animés (`../hd/GUIDE.md`,
`../fonds/LISEZMOI.md`) : pixel art HD, **un pixel du dessin = un pixel d'un héros HD**, gammes décalées en teinte (ombres
vers le violet / bleu, lumières vers le jaune), une seule lumière en haut à droite, **un seul contour** sombre autour de
chaque objet, pas de rayures ni de hachures, des signes inventés (jamais de lettres, sauf le nom du jeu dans le logo).
Le jeu agrandit toujours sans flou (`image-rendering: pixelated`, plus proche voisin).

Ce qui ne change pas : les **textes** restent en Lilita One / Fredoka (lisibles, traduits) ; les couleurs de l'interface
(émail bleu nuit cerclé d'or, parchemin) ; la disposition des écrans.

## Les outils (dossier `refonte-graphique/pixel/ui/`)

| Fichier | Rôle |
|---|---|
| `uilib.py` | l'atelier commun : toile numpy, masques, contour unique, texte Lilita sans lissage, lecture des `*-meta.ts` |
| `logo.py` | le logo → `public/art/ui-px/logo.webp` |
| `chargement.py` | l'écran de chargement → `public/art/ui-px/chargement*.webp` + le bloc « chargement » d'`index.html` |
| `icone.py` | l'icône de l'application → `public/art/ui-px/icone-180/192/512.png` |
| `lilita-one.woff2` | la police des titres (licence OFL), pour le logo seulement |

Aperçus pour le propriétaire : `refonte-graphique/pixel/sortie/ui/`. Images du jeu : `public/art/ui-px/`.

## Inventaire : tout ce qui n'est pas encore dans la nouvelle DA

| Quoi | Où c'est fait | Où on le voit |
|---|---|---|
| ~~Écran de chargement~~ `public/art/ui/loading.jpg` (peint) | `index.html`, `main.tsx` | au lancement ; aussi l'écran du nom (`screens/meta.tsx`) — **fait (partie 1)** |
| ~~Logo~~ `public/art/ui/logo.webp` (peint) | `index.html` | écran de chargement — **fait (partie 1)** |
| ~~Icône de l'application~~ `public/art/ui/icon-180/192/512.png` | `index.html` | écran d'accueil du téléphone, onglet du navigateur — **fait (partie 1)** |
| **Planche des pictos** `public/art/icons.webp` (162 pictos peints par Hailuo, 128 px, `src/game/icons-meta.ts`, chaîne `refonte-graphique/decoupe-pictos.py`) | `Art` / `Icon` de `ui/kit.tsx` ; statuts dans `fight-view.ts` (Phaser) | partout (voir le détail par partie) |
| Pictos de secours en SVG (`ICONS` de `ui/kit.tsx`, ~38) | `Icon` quand la planche n'a pas le picto | quelques puces, boutons |
| Barres, médaillons, plaques, bouton Combattre, bouclier de niveau, gemmes, chevrons, scintillements | `ui/chrome.tsx` (SVG) | barre du haut, barre des onglets, bas de l'accueil, chapitre |
| Bandeau de titre (ruban) | `ui/title-banner.tsx` (SVG) | Héros, Invocation, Aventure, Guilde, fiche héros |
| Sablier, coffre, halo | `ui/anim.tsx` (SVG animé) | accueil (butin), résultats, fusion, invocation |
| Pictos animés des modes (tour, missions, donjons, boss du jour, arène, Colisée) | `ui/mode-icons.tsx` (SVG animé) | tuiles de l'Aventure, Colisée |
| Décors des tuiles de modes (tour, missions, donjons, boss, arène) | `ui/tile-scene.tsx` (SVG) | tuiles de l'Aventure |
| Décors des onglets (Héros, Invocation, Aventure, Guilde, pages) | `ui/backdrop*.tsx` (SVG animé) | derrière chaque onglet |
| Scène de la fiche d'un héros (par élément) + socle | `ui/hero-scene.tsx` (SVG) | fiche héros |
| Plateau de préparation (dalles, couronne) | `ui/formation-stage.tsx` (SVG) + picto `crown` | préparation avant chaque combat |
| Portail d'invocation, cristaux | `ui/portal.tsx`, `portal.css`, `ui/summon-stage.tsx` (SVG) | onglet Invocation |
| Dos de carte, boule de tirage | `ui/card-back.tsx`, `TeaseOrb` de `screens/summon.tsx` | tirage des héros |
| Panneau des combats (planche, anneaux des portraits, boutons) | `hud-art.tsx` (SVG → texture Phaser) | tous les combats |
| Carte du monde `public/art/ui/map.jpg` (peinte) | `screens/campaign.tsx` | carte des régions de la campagne |
| Boutons, panneaux parchemin, cadres des fenêtres | `ui/style.css` (dégradés CSS) | partout |

Déjà dans la nouvelle DA : héros, monstres, grands boss (`art/hd/`), visages et héros en pied des menus (`art/hd/v/`,
`art/hd/pied/`), effets de combat (`art/hd/fx/`), les 8 fonds (`art/px/fonds/`, aussi derrière l'accueil et des menus).

### Détail de la planche des pictos (162) et où ils servent

- **Monnaies et ressources** : `gold`, `gems`, `crystals`, `essence`, `scrolls`, `basicScrolls`, `fragments`, `dust`,
  `arenaTokens`, `guildCoins`, `goldPile`, `gemPile`, `power`, `star`, `starEmpty`, `levelUp`, `lock`, `clock`, `ad`
  (barre du haut `WalletPill`, `Cur` partout, récompenses, boutique, puissance).
- **Onglets et médaillons** : `campaign`, `heroes`, `summon`, `adventure`, `guild` (barre du bas) ; `mail`, `quests`,
  `missions`, `shop`, `pass`, `calendar`, `friends`, `ranking`, `settings`, `chat`, `gift`, `bag`, `forge`, `fusion`,
  `chestClosed`, `chestOpen`, `questChest`, `hourglass`, `avatarFrame`, `badge` (colonnes repliables de l'accueil,
  barre du haut, réglages) ; la chouette du tutoriel `owl-explain`, `owl-happy`, `owl-point`, `owl-surprised`.
- **Modes** : `tower`, `dungeons`, `dailyBoss`, `arena`, `colisee`, `defense`, `mission-escort/hunt/patrol/relic/ruins/siege`,
  `league-bronze/silver/gold/platinum/diamond`, `trophy`, `goldMine`, `essenceSpring`, `summonAltar`, `summonPortal`.
- **Héros** : éléments `fire`, `water`, `earth`, `wind` ; rôles `warrior`, `protector`, `assassin`, `marksman`,
  `healer`, `support` ; `crown`, `rebirth`, `recycle`, `cardBack`.
- **Équipement et stats** : `weapon`, `armor`, `helmet`, `boots` et leurs 6 raretés (`weapon-0` … `-5`), ensembles
  `set-fury/guard/rampart/storm/vampire`, stats `atk`, `def`, `hp`, `speed`, `crit`, `critDmg`, `dodge`, `tenacity`.
- **Combat** : 14 statuts `st-*` (Phaser, au-dessus des barres de vie et en chiffres volants), `defeat`.
- **Guilde et boutique** : 12 blasons `emblem-0` … `-11`, 9 offres `offer-*`.

## La méthode commune (à partir de la partie 2)

1. **Pictos** : un picto = une grille de lettres + palette (comme les héros HD), dessiné **pixel par pixel**
   (`ui/pictos/<nom>.txt`), taille de base **32 × 32** (24 × 24 pour les statuts de combat, 48 × 48 pour la chouette
   et les gros objets), contour sombre ajouté tout seul, contrôles automatiques (pixels orphelins, contour, couleurs).
   Un outil `pictos.py` (`voir`, `controle`, `export`) fabrique **une planche** `public/art/ui-px/pictos.webp` et
   `src/game/ui/pictos-meta.ts` (nom → case, nombre d'images, durée).
2. **Branchement progressif** : `Art` / `Icon` de `ui/kit.tsx` prennent le picto dans la nouvelle planche s'il y est,
   sinon dans l'ancienne : chaque partie se voit dans le jeu dès qu'elle est finie, sans attendre les autres. Agrandis
   sans flou. Les statuts de combat suivent (`fight-view.ts`).
3. **Animés quand ça a du sens** (coffre qui s'ouvre, sablier qui coule, portail, chouette qui cligne, flamme d'un
   mode) : bande d'images dans la planche, animée par le CSS (`steps()`), comme les héros en pied des menus.
4. **Scènes** (décors d'onglets, tuiles, fiche héros) : faites avec l'atelier des fonds (`../fonds/fondlib.py`) et
   jouées dans un `<canvas>` par le petit moteur de la partie 1 (le script de l'écran de chargement, à sortir dans
   `src/game/ui/px-scene.ts` : calques en boucle, défilés, particules, à sa vraie taille puis agrandi sans flou).
5. Chaque partie : aperçus dans `sortie/ui/`, vérification dans le vrai jeu (Playwright, 390 × 844 avec encoche et
   360 × 640), anciennes images et anciens dessins SVG retirés quand plus rien ne s'en sert.

## Les parties, dans l'ordre

1. **Chargement, logo, icône de l'application — FAIT** (détails plus bas).
2. **Monnaies et ressources** (~19 pictos de la liste « Monnaies et ressources ») : ce qu'on voit le plus (barre du haut,
   récompenses, boutique). Crée `pictos.py`, la planche, et le branchement progressif de `kit.tsx`.
3. **Barre du bas, barre du haut, médaillons de l'accueil** (~30 pictos + la chouette du tutoriel en 4 poses) ; le
   **coffre** et le **sablier** du bas de l'accueil (`anim.tsx`) redessinés en pixel art animé.
4. **Tuiles des modes (Aventure)** : les 6 pictos animés de `mode-icons.tsx` en bandes d'images, les 5 décors de
   `tile-scene.tsx` (des morceaux de fonds pixel art), missions (6), ligues (5), Colisée, boss du jour, donjons.
5. **Décors des onglets et des pages** (`backdrop*.tsx`, `hero-scene.tsx` + socle, `formation-stage.tsx`) : des scènes
   pixel art animées (canvas), une par onglet et une par élément pour la fiche héros ; dalles et couronne de la préparation.
6. **Invocation** : portail animé (`portal.tsx`, `summon-stage.tsx`), dos de carte (`card-back.tsx`, couleur de la
   rareté par changement de palette), boule du tirage, pictos `summonAltar` / `summonPortal` / `cardBack`.
7. **Héros, équipement, stats, combat** : éléments, rôles, 4 pièces × 6 raretés, 5 ensembles, 8 stats, 14 statuts de
   combat (aussi dans Phaser), blasons de guilde (12), offres de la boutique (9), victoire / défaite, couronne, etc.
   Ensuite l'ancienne planche `icons.webp`, `icons-meta.ts`, `decoupe-pictos.py`, `refonte-graphique/pictos/` et les
   pictos SVG de secours de `kit.tsx` sont supprimés (et le préchargement d'`index.html` / l'attente de `main.tsx`
   passent à la nouvelle planche).
8. **Cadres, boutons, bandeaux** (`chrome.tsx`, `title-banner.tsx`, `hud-art.tsx`, boutons et panneaux de `style.css`) :
   à décider avec le propriétaire sur un essai de deux pièces (barre du haut + bouton Combattre) : cadres en pixel art
   étirés sans flou (`border-image`), les textes restant en Lilita / Fredoka.
9. **Carte du monde de la campagne** (`map.jpg` → une carte pixel art des 8 régions, une par clan, avec l'eau qui
   bouge), branchée dans `screens/campaign.tsx` (les places des régions sont des fractions de l'image).

## Partie 1 — faite (25/11/2026)

- **Écran de chargement** (`chargement.py`) : le volcan de Kael (fond HD du clan du feu, recadré 340 × 737 = la forme
  d'un grand téléphone), Myrr l'ange, Bérold le spartiate et Kael face au grand dragon de feu (retourné vers eux) ; ombres au
  sol ; tout ce qui bouge dans le fond bouge (cratère, coulées, rivière et bassin de lave, chute, fumée, braises) et les
  quatre personnages respirent. Peint à sa vraie taille dans un `<canvas>` par un script de ~2 Ko posé dans `index.html`
  (pas de Phaser, il s'affiche avant le code du jeu), agrandi sans flou pour couvrir l'écran : `--px` = la taille d'un
  pixel du dessin ; les petits téléphones coupent surtout du ciel (`ANCRE`). Logo en haut (sous l'encoche), barre en
  bas (au-dessus de la barre de geste) : cadre d'or et émail bleu nuit en pixel art, jauge d'or qui avance pixel par
  pixel. Poids : fond 15 Ko + planche 45 Ko + logo 3 Ko (l'ancien : 200 + 96 Ko). `main.tsx` le retire comme avant ; le
  script s'arrête quand l'écran est retiré. Pas de phrase d'astuce (pas de texte évident ; et l'écran s'affiche avant
  les traductions).
- **Écran du nom** (premier lancement) : l'image fixe complète `chargement.webp` en fond.
- **Logo** (`logo.py`) : refait en pixel art (même disposition que l'ancien : « FUZE / ARENA » en or épais, ruban rouge
  « HERO BATTLE », deux épées croisées), plus net et lisible à petite taille que l'ancien logo peint.
- **Icône de l'application** (`icone.py`) : Bérold le spartiate en buste sur l'émail bleu nuit avec un halo clair ; 64 × 64
  agrandi ×8 (512), ×3 (192), 180 = 192 sans 6 pixels de bord.
- Retirés : `public/art/ui/loading.jpg`, `logo.webp`, `icon-180/192/512.png` (et leur fabrication dans
  `decoupe-pictos.py`). `map.jpg` reste (partie 9).
- À relancer si le fond de Kael, un des personnages ou le logo changent : `logo.py`, puis `chargement.py --gif`.
