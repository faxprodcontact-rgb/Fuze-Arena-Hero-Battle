# Recherche graphique (proposition du 19/11/2026, pas encore dans le jeu)

Personnages « chibi » de trois-quarts dessinés par le code, aux positions réelles du combat (5 contre 5 sur 3 rangées).

- `kit.cjs` : outils de peinture (contour, lumière, ombre, volume, contre-jour).
- `chibi.cjs` : le personnage paramétrable (coiffure, tenue, arme, pose, oreilles, visage…).
- `cast.cjs` : les 5 héros et les 5 ennemis de la planche.
- `scene.cjs` : la scène du jeu (720 × 980) avec le terrain en profondeur ; `sheet.cjs` : la planche des personnages.

Pour régénérer : `node scene.cjs` (écrit `scene.html`), puis une capture d'écran avec Playwright.
