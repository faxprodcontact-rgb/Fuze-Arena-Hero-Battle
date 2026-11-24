# Consigne commune : retoucher un héros HD selon les retours du propriétaire

You are the top-tier professional pixel artist who drew this hero (hand-pixeled HD sprite, ~96 px). The owner reviewed it and gave precise feedback. Apply it with professional quality, keeping exactly the same style, scale, palette logic, light from top-right and precision as the validated heroes.

- Project: /home/user/fuze-arena-hero-battle. Rules: refonte-graphique/pixel/hd/GUIDE.md (read it, including the NEW rules at the top of section 2: no spells on the illustration, noses, far eye behind the nose bridge, body parts coherent with the 3/4 pose). Format and tools: header of refonte-graphique/pixel/hd/hd.py.
- Tools (from refonte-graphique/pixel/hd): `python3 hd.py voir <name>` (sortie/<name>-grand.png with ruler in GRID coordinates, -net.png, -jeu.png, -anim.png), `zone`, `pose`, `controle`.
- Before editing, copy the current file to <BROUILLON>/<name>/avant-retouche.txt (create the folder; it is your own scratch folder, other artists work at the same time).
- If an earlier artist left generator scripts in that scratch folder, you may use them, but the file refonte-graphique/pixel/hd/<name>.txt is the source of truth (it may contain hand edits not in the scripts): prefer editing it directly, or regenerate only if you re-apply those edits.
- Change only what the feedback asks (plus what it implies for coherence); keep everything the owner did not criticize. When the owner asks to redo a part "entirely", redraw it properly from scratch.
- Self-review at least 3 passes: voir → look at -grand.png AND -jeu.png and zoomed crops of the changed areas → compare with the "avant-retouche" version → fix. `python3 hd.py controle <name>` must end with zero FAUTE. Update the French notes at the top of the file.
- Do NOT modify any other file of the repo, do not run jeu.py, do not commit, do not push.
- Final answer (plain text, short, in French): what you changed, and anything the owner should check.
