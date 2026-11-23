# Essai de style : pixel art (23/11/2026)

Demande du propriétaire : essayer un autre style que le dessin vectoriel, plus précis. Essai : 5 héros, 5 monstres,
1 fond, en pixel art. Personnages de **96 × 96 pixels**, fond de **240 × 388** (l'écran de combat du jeu, 720 × 1163,
divisé par 3 : un pixel du fond = un pixel d'un personnage).

- `pix.py` : l'atelier. Une toile, des morceaux (formes + matière à 5 tons), ombrage automatique (lumière en haut à
  droite : bande d'ombre en bas à gauche, liseré clair en haut à droite, ou ombrage « boule »), un trait sombre quand un
  morceau passe devant un autre, un contour d'un pixel autour du personnage, des « tampons » en texte pour les yeux
  (le même pour les deux yeux d'un visage). `sheet()` fait la bande d'animation de repos (8 images : souffle + clignement).
- `persos/<nom>.py` : un fichier par personnage, une fonction `draw(c, t)`.
- `fond.py` : le fond « clairière » (sol plat d'un bord à l'autre, tout est posé).
- `scene.py` : une scène de combat fixe ; `voir.py` : aperçu agrandi ; `page.py` : la page d'essai (combat animé + fiches).
- `sortie/` : les bandes d'animation et le fond, en PNG.

Aperçu : `python3 refonte-graphique/pixel/voir.py /tmp/a.png kael sable --x 3 --une`
Page : `python3 refonte-graphique/pixel/page.py /tmp/essai.html`
