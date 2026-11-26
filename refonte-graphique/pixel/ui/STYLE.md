# Le style de l'interface : « moderne » (choisi le 26/11/2026) — la référence pour toutes les sections

> « J'adore le mode moderne. On part là-dessus. » (le propriétaire, 26/11/2026)

Remplace le style « pixel » de la v0.58.0 (pièces dessinées en pixels par `px.ts`) et l'essai à deux habillages de la
v0.58.2 (`skin.css`, `?skin=`, supprimés). Les **personnages, monstres, boss et décors restent en pixel art HD** (validés) ;
les **pictos** (`icons.webp`) sont refaits à part, lisses et HD : on les pose tels quels (`Icon`, `Art` de `kit.tsx`).

## En une phrase

Un fond **raisin profond**, des **formes arrondies**, des **ombres douces**, des **dégradés légers**, des **couleurs à rôle**,
des **fenêtres claires** à bandeau de titre coloré et bouton fermer rond, des **monnaies en pilules**, de gros boutons
tactiles, de l'air, une hiérarchie claire. Joyeux, très lisible, actuel (jeux mobiles à succès de 2026).

## Où c'est fait

| Quoi | Où |
|---|---|
| Jetons (couleurs, arrondis, ombres, espaces, tailles de texte), pièces, composants communs, accueil, campagne | `src/game/ui/style.css` (sections 1 à 5) |
| Base de mise en page des autres sections + retouches de l'essai | `style.css` section 6 et fin du fichier (à reprendre dans `src/game/ui/sections/<section>.css`) |
| Composants Preact communs | `ui/kit.tsx` (`Btn`, `Modal`, `Page`, `Tabs`, `Bar`, `Cur`, `RedDot`, `Sign`, `Stars`, `HeroCard`, `CardFigure`, `ItemIcon`), `ui/chrome.tsx` (`BarArt`, `ChapterPlaque`, `LevelShield`, `Medallion`, `Chevron`), `ui/title-banner.tsx` (`TitleBanner`), `ui/anim.tsx` (`Halo`) |
| Boutons « Pierre de l'arène » (v0.60.0) | `src/game/ui/buttons.ts` (dessins SVG, `installButtons()` appelé par `main.tsx`), `style.css` section « Boutons » |
| Combat (Phaser) | `src/game/hud-art.tsx` (feuille du bas, tuiles des portraits, pilules de vie/énergie, galets et dalles rendus depuis `buttons.ts`), `battle-scene.ts`, `fight-view.ts` (barres au-dessus des têtes, chiffres) |
| Chargement | `index.html` (fait par `pixel/ui/chargement.py`) : jauge en pilule, `theme-color` raisin |
| Fonds des menus (26/11) | Illustrations vectorielles lisses dessinées par le code, même manière que les pictos (une lumière en haut à droite, un contour adouci, liseré clair, ombre intérieure douce) : atelier `ui/backdrop-kit.tsx` (`Vol`, `Mat`…), `backdrop.tsx` (pages) + `backdrop-heroes/-summon/-adventure/-guild.tsx`, terrain de la préparation `formation-stage.tsx` (teinté par l'élément du clan, plus le décor du combat) ; mouvements doux `sections/backdrops.css` (coupés si « moins de mouvements ») ; détails en haut et aux bords, calme sous le contenu, sol plat bord à bord. Contrôle : `pixel/ui/outils/fonds-captures.cjs` |

Ordre de chargement : `main.tsx` importe `style.css` **avant** l'application ; le CSS d'une section, importé par ses écrans,
passe donc après lui : à priorité égale, **la section gagne**. `<html data-skin="moderne">` reste posé (`skin.ts`).

## Les jetons (`:root`, en tête de `style.css`)

**Fond (raisin)** : `--c-bg-0` `#0c0822` … `--c-bg-4` `#3d2f8a` (barres, pages, combat). Verre sombre posé sur le jeu :
`--c-glass` (`#120b33b3`), `--c-glass-strong`, filet `--c-glass-line` ; voile clair sur le sombre : `--c-veil`, `--c-veil-2`.

**Surfaces claires** (fenêtres, cartes) : `--c-surface` blanc, `--c-surface-2` `#f4f2fc`, `--c-surface-3` `#e7e3f6` (creux,
pistes), filet `--c-line`. Texte : `--c-text` `#221c45`, `--c-muted`, `--c-title` ; sur le sombre : `--c-on-dark`,
`--c-on-dark-muted`.

**Couleurs à rôle** (chacune avec `-hi` = lumière, `-lo` = ombre / lèvre / couleur du texte posé dessus) :

| Rôle | Jeton | Sert à |
|---|---|---|
| Vert | `--c-action` | l'action principale : Combattre, OK, Prendre, interrupteur allumé, vie des héros |
| Azur | `--c-select` | ce qui est choisi : onglet ouvert, case choisie, action secondaire, focus |
| Or | `--c-reward` | récompenses, puissance, mis en avant, « Victoire » |
| Violet | `--c-gem` | gemmes, invocation, passe |
| Corail | `--c-danger` | fermer, danger, pastille rouge, « Défaite », vie des ennemis |
| Sarcelle | `--c-info` | neutre coloré |

Bandeau de titre : `--g-head` (dégradé violet → azur). Arrondis : `--r-xs` 8, `--r-s` 12, `--r-m` 16, `--r-l` 20, `--r-xl` 26,
`--r-pill`. Ombres : `--sh-1` (posé dans une fenêtre), `--sh-2` (carte), `--sh-3` (fenêtre), `--sh-float` (posé sur le jeu).
Espaces : `--sp-1` 4 … `--sp-5` 24. Texte : `--fs-xs` 11, `--fs-s` 13, `--fs-m` 15, `--fs-l` 18, `--fs-xl` 22, `--fs-xxl` 30.
Polices : `--font-title` (Lilita One : titres, boutons, chiffres ; une seule graisse, jamais « bold ») et `--font` (Fredoka).
Signes blancs des boutons ronds : `--ico-x`, `--ico-back`, `--ico-next`, `--ico-plus`, `--ico-down`.

Noms historiques gardés (tous les écrans s'en servent, ils suivent les jetons) : `--gold`, `--green`, `--blue`, `--red`,
`--purple` (+ `-hi`, `-dark`), `--text`, `--muted`, `--title`, `--panel`, `--inset`, `--navy-0…4` (= raisin),
`--gold-0…4`, `--cream-0…3`, et ceux de l'essai `--s-*` (`--s-gold`, `--s-bg-2`, `--s-head`…).

## Les pièces (`--pxf`, `--pr`, `--psh`)

Un élément « à pièce » a son fond sur son `::before` : `--pxf` = le fond (un dégradé), `--pr` = l'arrondi, `--psh` = l'ombre
La classe **`pxf`** donne ce mécanisme à un nouvel élément. Fonds prêts
(noms historiques `--px-…`, ce sont des dégradés) : `--px-panel`, `--px-frame`, `--px-inset`, `--px-groove(-s)`,
`--px-plaque-<navy|blue|purple|red|green|teal|gold>`,
`--px-chip`, `--px-badge(-gold)`, et les signes `--px-star`, `--px-check`, `--px-cross`, `--px-badge`… (SVG lisses de `signs-art.ts`, posés sur `<html>` par `installSigns()` de `px.ts` ; `<Sign>`).

## Les composants (classes à utiliser)

- **Boutons « Pierre de l'arène »** (choisis le 26/11, v0.60.0 ; maquettes : `refonte-graphique/ui-moderne/boutons/`) : une
  dalle taillée aux coins éclatés, comme le sol de l'arène. Dessins SVG faits par `ui/buttons.ts` ; `installButtons()` les pose
  dans `--bt-pierre-<teinte>-<taille>[-down]` et `--bt-pierre-rond-<teinte>[-down]` (+ `--bt-pierre-creux-rail`) et relie les
  classes aux dessins. Un bouton = `bt bt-<teinte> bt-<taille>` (`btClass(teinte, taille)`) : le dessin sur le `::before` en
  3 morceaux (bouts fixes, milieu étiré : toute largeur). Tailles : `s` 38, `m` 48, `l` 62, `xl` 72, `xxl` 84.
  Teintes : **basalte** = l'action principale (pierre sombre où brûle une lumière d'or, lettres qui luisent, deux fêlures à
  partir de `l`) ; **or** = récompense, achat ; **arcane** = invocation ; **feu** = danger, fermer ; **ardoise** = secondaire
  (pierre claire, lettres brunes) ; **galet** = neutre sombre (outils, pause, vitesse, retour) ; **eau / terre / vent / feu**
  = un élément (`ELEMENT_TONE`). Enfoncé (`:active`, `.is-down`) : la dalle descend de son épaisseur. Impossible
  (`:disabled`) : la pierre éteinte (`off`). Un prix dedans : `.cur` devient un creux taillé.
  `Btn` (kit.tsx) garde son API : `green` → basalte, `gold` → or, `purple` → arcane, `red` → feu, `blue` / `ghost` → ardoise ;
  `small` → s, normal → m, `btn-fight` → l (ou `size`) ; les classes `btn btn-<sorte>` restent (le tutoriel les vise).
  Rond : `bt-rond bt-<teinte>` (galet de 44 × 48, mis à l'échelle), son signe par `--sg` / `--sgs` (`.x` = feu + croix,
  retour = galet + chevron, `.plus` = vent, filtres d'élément allumés de leur couleur, AUTO allumé = basalte).
  Onglets : rail creusé (`.tabs`, `.bt-rail`) et onglet ouvert = petite dalle de basalte allumée (`Tabs`, `.av-seg`,
  `.g-tabs`, `.sum-kinds`, barre des onglets du bas). Combat : `hud-art.tsx` rend les mêmes SVG en textures Phaser
  (`hud-round-<galet|basalte|feu>`, `hud-btn-…`, avec `-down`).
- **Fenêtres** `Modal` → `.modal-back` (voile + flou) › `.modal` (corps lavande clair, coins 24, `--sh-3`) › `.modal-head`
  (bandeau `--g-head`, titre blanc) + `.x` (galet de feu, croix blanche) › `.modal-body`. Toujours au milieu de l'écran.
- **Pages** `Page` → `.page` › `.prep-head` (même bandeau, coins arrondis en bas, retour = galet sombre) › `.page-body`.
- **Cartes** `.card` (blanche, coins 20, `--sh-2`) ; une ligne posée dans une fenêtre : `.block`, `.quests li`,
  `.setting-row`… (blanche, coins 14, `--sh-1`). Liste groupée (réglages) : `.settings-group` (une seule carte, filets).
- **Onglets** `Tabs` → `.tabs` (rail de pierre creusé) › `.tab`, `.tab-on` (dalle de basalte allumée, `bt-s`).
- **Barre du haut** `.topbar` (bandeau raisin aux coins arrondis en bas, posé sur le jeu : `margin-bottom: -18px`) :
  `.avatar` (portrait en tuile arrondie cerclée d'un dégradé, `LevelShield` en pilule d'or), `.who`, `.wallet` › `.pill`
  (monnaie : pilule de verre sombre, picto qui déborde à gauche, `.plus` = petit galet allumé de vert).
- **Barre des onglets** `.tabbar` (coins arrondis en haut, `margin-top: -18px`) › `.tabbar-btn` ; ouvert : `.on` (dalle de
  basalte allumée derrière, picto agrandi). `BarArt` toujours **dernier enfant** de sa barre.
- **Pastilles** : `RedDot` → `.dot` (rond corail cerclé de blanc, 16 px, sautille) ; compteurs/pilules : `.cur-big`, `.chip`
  (`.chip.on` = azur), `.tag`, `.pts` (or).
- **Jauges** `Bar` → `.bar` (pilule creusée) › `.bar-fill` (pilule, lumière en haut) ; `.chapter-bar`, `.dock-bar`.
- **Interrupteur** `.switch` (pilule, rond blanc qui glisse ; `.on` = vert).
- **Bandeau de titre** `TitleBanner tone=…` → `.title-banner .tb-<teinte>` (pilule pleine de la teinte) ; `.plaque`.
- **Message court** `.toast` (pilule sombre au milieu). **Halo** `Halo` (lueur qui respire + étincelles qui tournent : `haloLayers` de `px.ts`).
- **Médaillon** `Medallion tone=…` → `.medal .medal-<teinte>` (tuile lisse en dégradé ; forme réglée par l'endroit).
- **Case d'un héros** `HeroCard` → `.hcard` : le héros **en entier** (`CardFigure`, bande `art/hd/pied/`), même échelle pour
  tous (la case = 128 pixels du dessin + marge : `--u: calc(84cqw / 128)`), pieds au milieu à `--feet` (80 %) de la
  hauteur ; liseré net de la couleur de la rareté (`--rar`), niveau en haut à gauche, élément en haut à droite, étoiles.
  Choisi : `.hcard-on` (anneau azur + coche). Pour changer la place des pieds dans une liste : `--feet` sur `.hcard`.
- **Case d'un objet** `ItemIcon` → `.item` (coins 14, liseré de la rareté).

## À faire / à ne pas faire

- Faire : des formes arrondies ; une ombre douce dessous ; une lumière douce en haut des boutons et plaques ; une couleur par
  rôle (tableau plus haut) ; des pilules pour les nombres ; de l'air ; des boutons d'au moins 44 px de haut.
- Faire : les textes posés sur une couleur ont une ombre franche de la couleur sombre du fond (`--o` + `var(--outline)` ou
  `var(--outline-s)`), pas de cerne tout autour.
- Ne pas faire : de bordure dorée, de cadre en pixels, de rivets, de rubans, de losanges, de reflet qui passe, de rayures ou
  de rayons répétés ; pas de `image-rendering: pixelated` sur une pièce d'interface (seulement sur les dessins en pixel art :
  personnages, décors, pictos) ; pas de nouvelle couleur hors des jetons ; pas de `url(art/…)` dans le CSS (passer par un
  `style` dans le TSX) ; jamais `display: none` sur un `TitleBanner`.
- Mise en page (rappels du propriétaire) : un titre, des icônes, des chiffres, aucune phrase évidente ; pas de défilement si
  possible (vérifier en 390 × 844 avec encoche **et** 360 × 640) ; fenêtres au milieu ; zone sûre (`env(safe-area-inset-…)`).
  Le propriétaire laisse libre de changer la disposition, la taille et la place des éléments pour plus de clarté.

## Vérifier

`npm run build`, `npx vite preview --port 4471`, puis
`node refonte-graphique/pixel/ui/outils/socle-captures.cjs <dossier> 4471 [écrans…]` ; boutons dans tout le jeu (héros,
fiche, invoquer, aventure, arène, guilde, combat, AUTO allumé, pause) : `outils/boutons-captures.cjs <dossier> 4471 [écrans…]` (accueil, bords, reglages, carte,
rapide, butin, connexion, quetes, passe, boutique, classement, tchat, courrier, amis, prep, combat, victoire, defaite) ;
avant | après : `pixel/ui/outils/avant-apres.py`. Captures du Socle : `refonte-graphique/pixel/sortie/ui/moderne/socle/` ; des boutons de pierre : `…/moderne/boutons-jeu/` (`apercu.png`).
