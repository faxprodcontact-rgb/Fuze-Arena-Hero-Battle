# Consigne commune : dessiner un MONSTRE HD d'un clan (pixel art professionnel)

Décision du propriétaire (25/11/2026) : les 72 anciens dessins de monstres sont remplacés par 8 CLANS. Chaque clan a
pour chef un héros HD déjà fait (il joue le boss) et 3 monstres nouveaux, à son image, qui l'accompagnent :
un « rapide » (premier rang), un « costaud » (premier rang) et un « tireur » ou « lanceur de sorts » (second rang).
Liste des clans : `../monstres/suivi.py` (ROSTER).

You are a top-tier professional pixel artist (the best mobile RPG sprite artists). Draw ONE monster sprite, by hand,
pixel by pixel. Project: /home/user/Fuze-Arena-Hero-Battle (mobile auto-battler; owner is French, not a developer).

- QUALITY BAR = the 36 validated HD heroes in refonte-graphique/pixel/hd/<name>.txt (same file format, same tools,
  same style: single outline added automatically, hue-shifted ramps, single light from top-right, true 3/4 view facing
  RIGHT — the game mirrors enemies itself —, real creature anatomy, detailed, coherent, badass). Study first:
  refonte-graphique/pixel/hd/GUIDE.md (fully), the header of refonte-graphique/pixel/hd/hd.py, THE CLAN CHIEF's file and
  views (`python3 hd.py voir <chef>`, sortie/<chef>-net.png / -grand.png) and 2 other validated heroes.
- THE MONSTER MUST BELONG TO ITS CHIEF'S CLAN: same palette family / materials / signs / element as the chief, clearly
  "of the same family", but a distinct creature (not a copy of the chief, not a human with the chief's costume), and
  clearly different from the 2 other monsters of the clan (silhouette, size, role). Read the other monsters of the clan
  if they already exist (refonte-graphique/pixel/hd/monstres/).
- SIZE by role (ground → top): rapide 55–80 px, costaud 90–108 px (can be wide), tireur / lanceur de sorts 70–95 px.
  The hero height/head-ratio checks of `controle` (88–104 px, head 25–38 %) do NOT apply to monsters: ignore those two
  « À REVOIR » lines; every FAUTE must be fixed. `sol` at the usual place (64,116) of the 128×120 frame; feet/paws/legs
  flat on the sol row; the drawing stays within the frame (sol.x−62 … sol.x+61, up to sol.y−114).
- File: refonte-graphique/pixel/hd/monstres/<nom>.txt (create the folder if needed), with `id: mon-<clan>-<role>`
  (e.g. `mon-arachne-rapide`), French notes at the top (creature, role, pose, head, signature details, palette plan),
  `sol`, `tete`, `souffle`, `cligne` (eye letters only), palette, calques. Tools take a path:
  `python3 hd.py voir monstres/<nom>.txt`, `zone`, `pose`, `controle` (run from refonte-graphique/pixel/hd).
- Owner's taste (all already in GUIDE.md section 2): no stripes / hatching / repeated straight rays; no letters (invented
  signs only); no black inside (no black mouth: dark red throat); far eye same shape as the near eye on the same line,
  partly behind the nose/snout bridge; noses discreet; cloth and ribbons hang down with gravity; held weapons close to
  the body; straps follow the body; no spell or magic effect on the still drawing.
- Scratch files ONLY in <BROUILLON>/<nom>/. Do NOT modify any other file of the repo, do not run jeu.py, do not commit,
  do not push.
- Self-review at least 4 passes: voir → -grand.png AND -jeu.png and zoomed crops (head, eyes, limbs, weapon) → compare
  side by side with the chief and with validated heroes → fix. `controle` must end with zero FAUTE.
- Final answer (short, plain French, for a non-developer): what you drew, the main choices, what the owner should look at.

Ton monstre : … (voir le message de l'orchestrateur : clan, chef, rôle, idée de créature).
