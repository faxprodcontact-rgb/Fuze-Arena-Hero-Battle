# Essai de style : pixel art (23/11/2026)

Demande du propriétaire : essayer un autre style que le dessin vectoriel, plus précis. Essai : 5 héros, 5 monstres,
1 fond, en pixel art. Personnages dessinés dans un repère de **96 × 96** (pieds vers y = 93), sur une toile de
**128 × 120** (marge `OX`, `OY` dans `pix.py`) : armes, ailes et flammes peuvent dépasser sans être coupées. Fond de
**240 × 420** aux mesures de l'écran de combat (÷ 3), son bas = le bas du terrain.

Depuis le 23/11/2026 (v0.43.0) : les héros sont **en position de combat** (fente, buste penché, arme pointée vers
l'ennemi, visages durs). À vérifier sur chaque personnage : rien ne touche le bord de la toile (contrôle dans le
journal, v0.43.0), aucun bras ne passe devant la barbe ou le visage, les cheveux visibles devant, la couronne ou le
bandeau posé sur la tête, des ailes en plumes (pas des rayons). `python3 jeu.py` met tout dans le jeu.

- `pix.py` : l'atelier. Une toile, des morceaux (formes + matière à 5 tons), ombrage automatique (lumière en haut à
  droite : bande d'ombre en bas à gauche, liseré clair en haut à droite, ou ombrage « boule »), un trait sombre quand un
  morceau passe devant un autre, un contour d'un pixel autour du personnage, des « tampons » en texte pour les yeux
  (le même pour les deux yeux d'un visage). `sheet()` fait la bande d'animation de repos (8 images : souffle + clignement).
- `persos/<nom>.py` : un fichier par personnage, une fonction `draw(c, t)`.
- Style retenu (v0.45.0) : **gros pixels encrés** — `c.part(..., 'ink')` met un trait noir autour de chaque morceau ;
  un héros encré a un `ORIGIN` (pieds en y = 71, milieu x = 40) et ~64 pixels de haut. Voir le journal, v0.45.0.
- `persos/tetes.py` : les têtes des héros dessinées pixel par pixel (plus précis que les formes) ; `c.sprite()` les pose.
  Chaque héros a une pose différente (voir le journal, v0.44.0).
- `fond.py` : le fond « prairie » du combat d'essai (arène de terre battue d'un bord à l'autre, jamais de rond au sol, tout est posé).
- `scene.py` : une scène de combat fixe ; `voir.py` : aperçu agrandi ; `page.py` : la page d'essai (combat animé + fiches).
- `sortie/` : les bandes d'animation et le fond, en PNG.

Aperçu : `python3 refonte-graphique/pixel/voir.py /tmp/a.png kael sable --x 3 --une`
Page : `python3 refonte-graphique/pixel/page.py /tmp/essai.html`
