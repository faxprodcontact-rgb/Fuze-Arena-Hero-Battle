# Consigne commune : animer un héros HD (respiration, attaque, attaque spéciale)

You are a top-tier professional pixel-art ANIMATOR (mobile RPG quality, like the best idle/auto-battler games). The project owner (French, not a developer) tested character animation on ONE hero, Eldra, and LOVED it ("Super, j'aime bien"). Now do the same, at the same quality and in the same system, for ONE other hero (named at the end). Other animators work at the same time on other heroes.

Project root: /home/user/Fuze-Arena-Hero-Battle. Read first:
- THE VALIDATED REFERENCE: refonte-graphique/pixel/hd/anim/eldra/build.py (method, file layout, French comments, outputs) and its outputs refonte-graphique/pixel/sortie/anim-eldra-*.gif and anim-eldra-planche.png. Reuse its approach and as much of its code as makes sense (copy what you need into your own folder; do NOT modify the eldra folder or its outputs).
- refonte-graphique/pixel/hd/GUIDE.md, the header of refonte-graphique/pixel/hd/hd.py (file format, `frame()`), and your hero's file refonte-graphique/pixel/hd/<name>.txt (notes + layers; this still drawing is VALIDATED by the owner: keep its exact look, palette, proportions, outline and quality in every frame). Look at `python3 refonte-graphique/pixel/hd/hd.py voir <name>` outputs.

WHAT TO MAKE (same 3 animations as Eldra, facing right, feet on the same ground line, enemy to the right):
1. **Pose / respiration (idle)**, seamless loop ~8–12 frames: breathing, slight weight shift, head micro-motion with a little delay, secondary motion on hair/cloth/tail/cape etc. (cloth hangs down with gravity, it only sways), one blink.
2. **Attaque basique avec l'arme**, ~8–10 frames: clear punchy attack suited to THIS hero's weapon and role (melee strike, or for an archer a real shot: draw, release, arrow flying off to the right, recoil): anticipation hold, fast action (smear frames allowed), impact/release held a bit, recovery to guard.
3. **Attaque forte (attaque spéciale)**, ~14–20 frames, MORE SPECTACULAR, with effects of the hero's ELEMENT (given below), with a brief hit-stop on the big moment, then recovery. Effects ARE allowed here. Owner's taste: NO repeated straight rays/hatching/stripes (organic curved shapes, puffs, volutes, chunks), single light from top-right, grounded, air around the subject, one outline per object, no black inside. Make the special clearly DIFFERENT from Eldra's (not another leap + ground slam unless it really is this hero's thing) and true to this hero's identity, weapon and element.

Craft: keyframes then in-betweens, arcs, sparing squash & stretch, overlap/follow-through; face, hands and weapon stay on-model in every frame; hands hold the weapon coherently; per-frame durations with longer holds on anticipation and impact. Reuse validated parts by moving them pixel-exact; REDRAW by hand what rotates/deforms (never smooth/rotate/resample the sprite; nearest-neighbour only, fix jaggies by hand). Hero palette + a small effect palette (list it).

FILES (do NOT modify any existing file — not <name>.txt, hd.py, jeu.py, the eldra folder, game code; do not commit/push):
- Sources in a new folder refonte-graphique/pixel/hd/anim/<name>/ with a re-runnable `build.py` (French comments).
- Outputs in refonte-graphique/pixel/sortie/: `anim-<name>-pose.gif`, `anim-<name>-attaque.gif`, `anim-<name>-speciale.gif` (×4, nearest, background #e8ecf2, real per-frame durations, looping), `anim-<name>-planche.png` (all frames, ×3, numbered with durations), and `anim-<name>-jeu.gif` (pose ×2 → attaque → pose → spéciale → pose, on the meadow background like Eldra's, ×2).
- Scratch only in <BROUILLON>/anim-<name>/.

SELF-REVIEW at least 4 passes (contact sheet zoomed, single frames ×8 crops, silhouette, arcs, timing, on-model face/hands/weapon, no stray pixels, no flicker, idle loop seam). Compare side by side with Eldra's animations for quality and fix.

FINAL ANSWER (short, plain French, for a non-developer): what each animation does (frames, duration), main choices, and what the owner should look at.
