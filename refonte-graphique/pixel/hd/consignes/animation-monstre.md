# Consigne commune : animer un MONSTRE HD (respiration, attaque, attaque spéciale)

Demande du propriétaire (25/11/2026) : animer les 24 monstres des 8 clans comme les 36 héros.

FOLLOW EXACTLY refonte-graphique/pixel/hd/consignes/animation.md (the hero animation brief: same 3 animations, same
method, same quality, same file layout and outputs, same self-review, same owner's taste), with these differences:

- Your subject is a MONSTER: its file is refonte-graphique/pixel/hd/monstres/<nom>.txt (`python3 hd.py voir
  monstres/<nom>.txt` from refonte-graphique/pixel/hd). Keep its exact look in every frame. Do NOT modify it.
- References: besides Eldra (anim/eldra/build.py), look at the animation of THE CLAN CHIEF
  (anim/<chef>/build.py and pixel/sortie/anim-<chef>-*.gif): the monster must feel of the same family in motion,
  but its moves follow ITS OWN body (spider legs, snake tail, tentacles, wings, four legs, floating jellyfish...):
  real creature motion, not a human animation pasted on a creature.
- Sources in refonte-graphique/pixel/hd/anim/<nom>/build.py ; outputs in refonte-graphique/pixel/sortie/:
  anim-<nom>-pose.gif, anim-<nom>-attaque.gif, anim-<nom>-speciale.gif, anim-<nom>-planche.png, anim-<nom>-jeu.gif
  (same formats as the heroes). Scratch only in <BROUILLON>/anim-<nom>/.
- Facing RIGHT like the heroes (the game mirrors enemies itself); enemy on the right.
- By ROLE:
  - rapide : quick, nervous, light idle; the basic attack is a fast leap / dash / flurry that comes back to its place;
    special = a fast combo or a bounding strike, with the element's effects.
  - costaud : heavy, slow idle (big breathing); the basic attack is a heavy blow with a long anticipation and a strong
    impact (ground shake allowed: small dust puffs, NOT straight rays); special = a crushing blow hitting the whole
    front row (effect spreading along the ground to the right).
  - tireur : the basic attack is a real shot (projectile flying off to the right, recoil); special = a stronger shot
    or a volley, with the element's effects.
  - sorts : the basic attack is a small spell thrown to the right; special = a big spell of the element (curved shapes,
    puffs, volutes, chunks; never repeated straight rays, never letters).
- Element effects (palette of the clan chief's special when possible): terre = stone chunks, dust, venom green for the
  serpent/spider clans; eau = water drops, foam, bubbles, splashes; feu = flames, embers, lava; vent = swirls of
  air, leaves, feathers, clouds.
- Final answer: short, plain French (owner is not a developer): what each animation does, main choices, what to check.

Ton monstre : … (voir le message de l'orchestrateur).
