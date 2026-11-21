# Planches pour Hailuo

Fabriquées par `refonte-graphique/planche-ia.cjs` (`node planche-ia.cjs heros fire sortie.png`, ou `monstres`).
Images 4K (3840 × 2160, format 16:9), 18 personnages par planche, fond blanc, sans texte ni aura de rareté
(le jeu ajoute l'aura lui-même). Une planche = un prompt (même numéro). Chaque prompt fait moins de 1 500 caractères.

## Les images rendues par Hailuo

Gardées dans `refonte-graphique/hailuo-v1/` (8 planches + 2 de rattrapage, telles que Hailuo les rend : 3696 × 1584,
signature en bas à droite). Ce sont les sources des futurs dessins du jeu.

## Comment faire

1. Dans Hailuo, choisir la création d'image **à partir d'une image de référence**, et importer la planche.
2. Coller le prompt de la planche (il est en anglais : ces outils comprennent mieux l'anglais).
3. Format **16:9**, la meilleure qualité proposée.
4. Commencer par la planche 1 des héros. Si les 18 personnages sont bien gardés, dans le même ordre, faire les autres.
   Si l'IA en mélange ou en oublie, il faudra des planches de 9 (à demander à Claude).

L'ordre se lit de gauche à droite, rangée par rangée. Dans chaque prompt, les personnages sont décrits dans cet ordre.

## Héros 1 — Feu

Planche : `heros-1-feu.png`

```
Redraw this sheet as 2D mobile RPG character art. Keep EXACTLY the same 18 characters in the same 6x3 grid and order, none added or removed. Each keeps its species, head shape, outfit, colors, weapon in the same hand, pose and silhouette: full body, three-quarter view facing right. Upgrade: chibi proportions, fierce expressive faces, clean anatomy, fingers gripping items, rich materials (metal, cloth, fur, scales), painted cel shading, light from top right, rim light, one bold dark outline per character, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, extra limbs; nothing cropped, no weapon over a face, characters never touch.
Row 1: Greek hoplite, spear, round fire shield | bald bearded blacksmith, hammer on shoulder | fire-breather, bottle, flame in hand | Roman legionary, sword, black cracked shield | orange salamander-man, dagger | veiled priestess holding an oil lamp.
Row 2: Polynesian volcano priestess raising a flame | black magma golem, glowing cracks | red horned oni, spiked club | Chinese soldier, conical helmet, fire lance | white-haired fox girl, fox tail, blue flame | Aztec sun priest, feather crown, gold disc.
Row 3: genie, turban, smoke tail | fire giant, flaming hair, horns, huge glowing sword | lioness goddess, sun disc, golden arrows | black horned demon, bat wings, tail, two blades | phoenix girl, flame wings | sun goddess, radiant crown, gold mirror.
```

## Héros 2 — Vent

Planche : `heros-2-vent.png`

```
Redraw this sheet as 2D mobile RPG character art. Keep EXACTLY the same 18 characters in the same 6x3 grid and order, none added or removed. Each keeps its species, head shape, outfit, colors, weapon in the same hand, pose and silhouette: full body, three-quarter view facing right. Upgrade: chibi proportions, fierce expressive faces, clean anatomy, fingers gripping items, rich materials (metal, cloth, fur, scales), painted cel shading, light from top right, rim light, one bold dark outline per character, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, extra limbs; nothing cropped, no weapon over a face, characters never touch.
Row 1: mountain guard, teal hood, pickaxe, spiral shield | viking, axe, round shield, blond beard | steppe archer, fur hat, drawing a bow | griffin knight, great helm, lance, teal shield | ninja, mask, big shuriken on back, kunai | fairy, green bun, wings, playing a flute.
Row 2: young bard, lyre, toga, teal cape | valkyrie, winged helmet, spear, blue round shield | red long-nosed tengu, black wings, fan, blade | eagle-headed warrior, red wings, gold rings | weasel man, two sickles, red scarf | dancer, tiara, pink veils, lotus.
Row 3: green horned wind demon, wild black hair, wind bag | monkey king, long staff, red cape | bearded god, gold crown, toga, raised lightning bolt | dark queen, black hair, crow cloak, sword | angel, halo, six white wings | blue thunder god, ring of red drums, cloud.
```

## Héros 3 — Eau

Planche : `heros-3-eau.png`

```
Redraw this sheet as 2D mobile RPG character art. Keep EXACTLY the same 18 characters in the same 6x3 grid and order, none added or removed. Each keeps its species, head shape, outfit, colors, weapon in the same hand, pose and silhouette: full body, three-quarter view facing right. Upgrade: chibi proportions, fierce expressive faces, clean anatomy, fingers gripping items, rich materials (metal, cloth, fur, scales), painted cel shading, light from top right, rim light, one bold dark outline per character, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, extra limbs; nothing cropped, no weapon over a face, characters never touch.
Row 1: coral-crowned soldier, big seashell shield | fisherman, straw hat, harpoon | pirate, eyepatch, feathered hat, pistol, hook | green kappa, beak, turtle shell, water dish on head | shark-man, sawtooth club | water nymph, teal hair, pouring a jar.
Row 2: red-haired mermaid singing, music notes | crab samurai, red shell armor, mask, katana | frost giant, white beard, ice axe | Inuit hunter, fur parka, crossbow | pale drowned spirit, reed crown, claws | sea goddess, red robe, tasseled crown, lantern staff.
Row 3: snow woman, white kimono, blowing ice crystals | sea king, gold crown, white beard, trident | winter huntress, wolf-pelt hood, bow, skis | purple tentacled sea witch, hook | water mother, white turban, pearls, water orb | dragon king, antlers, whiskers, blue robe, pearl.
```

## Héros 4 — Terre

Planche : `heros-4-terre.png`

```
Redraw this sheet as 2D mobile RPG character art. Keep EXACTLY the same 18 characters in the same 6x3 grid and order, none added or removed. Each keeps its species, head shape, outfit, colors, weapon in the same hand, pose and silhouette: full body, three-quarter view facing right. Upgrade: chibi proportions, fierce expressive faces, clean anatomy, fingers gripping items, rich materials (metal, cloth, fur, scales), painted cel shading, light from top right, rim light, one bold dark outline per character, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, extra limbs; nothing cropped, no weapon over a face, characters never touch.
Row 1: red-bearded dwarf, spiked mace, shield | satyr, goat horns and legs | young slinger, sling raised | one-eyed cyclops lifting a boulder | hooded scorpion-man, scorpion tail and legs, spear | tree nymph, leafy green hair, bark dress.
Row 2: druid, green hood, white beard, leafy staff, gold sickle | terracotta general, topknot, scale armor, sword | minotaur, red eyes, nose ring, double axe | gorgon, snake hair, snake tail, green gaze | jackal-headed god, scales, curved sword | Egyptian goddess, throne crown, wing sleeves, ankh.
Row 3: voodoo baron, top hat, skull cane, bottle | hero in lion pelt, big club | stag-skull hunter, antlers, green cloak, bow | spider-woman, spider body, needles | earth mother, flowery green hair, earth orb | underworld king, spiked crown, bident, blue flame.
```

## Monstres 1 — Feu (Parade des pétards · Fauves de cendre · Idoles d’airain)

Planche : `monstres-1-feu.png`

```
Redraw this sheet as 2D mobile RPG monster art. Keep EXACTLY the same 18 creatures in the same 6x3 grid and order, none added or removed; each row is one monster family, the last two of each row are the bigger elite and boss. Each keeps its species, body shape, colors, pose and silhouette: full body, facing right. Upgrade: real creature anatomy, menacing faces, sharp eyes, open mouths with fangs, legs, wings and tails attached naturally under the body, rich textures, painted cel shading, light from top right, rim light, one bold dark outline per creature, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
Row 1, living fireworks parade: firecracker imp with lit fuse | paper lion dance costume | monkey carrying rockets | paper lantern with glowing face | giant drum with drumsticks and war mask | parade dragon on poles.
Row 2, ash beasts with ember cracks: spotted hyena | warthog | spitting cobra | vulture | black lioness | ember buffalo, huge horns.
Row 3, bronze idols with patina and rivets: temple lion-dog | bull with furnace door | archer statue | incense bearer | colossus | great idol, furnace belly, demon mask.
```

## Monstres 2 — Vent (Épouvantails · Ruche · Volière d’orage)

Planche : `monstres-2-vent.png`

```
Redraw this sheet as 2D mobile RPG monster art. Keep EXACTLY the same 18 creatures in the same 6x3 grid and order, none added or removed; each row is one monster family, the last two of each row are the bigger elite and boss. Each keeps its species, body shape, colors, pose and silhouette: full body, facing right. Upgrade: real creature anatomy, menacing faces, sharp eyes, open mouths with fangs, legs, wings and tails attached naturally under the body, rich textures, painted cel shading, light from top right, rim light, one bold dark outline per creature, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
Row 1, haunted farm things: weathervane rooster | scarecrow | kite with angry face | wind chime | straw reaper with scythe | windmill with one eye and fanged door.
Row 2, giant hive: worker bee | armored soldier bee | wax-spitting larva | nurse bee with honey cup | giant hornet | crowned queen bee with scepter.
Row 3, storm birds: diving falcon | marabou stork | crow with glowing stone | storm peacock fanning its tail | cassowary | thunderbird with lightning wings.
```

## Monstres 3 — Eau (Abysses · Horde des glaces · Bayou)

Planche : `monstres-3-eau.png`

```
Redraw this sheet as 2D mobile RPG monster art. Keep EXACTLY the same 18 creatures in the same 6x3 grid and order, none added or removed; each row is one monster family, the last two of each row are the bigger elite and boss. Each keeps its species, body shape, colors, pose and silhouette: full body, facing right. Upgrade: real creature anatomy, menacing faces, sharp eyes, open mouths with fangs, legs, wings and tails attached naturally under the body, rich textures, painted cel shading, light from top right, rim light, one bold dark outline per creature, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
Row 1, deep sea: hatchetfish | hermit crab in a diving helmet | jellyfish | anglerfish with glowing lure | long-legged spider crab | colossal squid.
Row 2, ice age: sabertooth tiger | woolly rhino | narwhal | snowy owl | cave bear | woolly mammoth.
Row 3, swamp: crested basilisk lizard | alligator snapping turtle | archerfish | ghostly will-o'-wisp | giant catfish with barbels | old crocodile.
```

## Monstres 4 — Terre (Échiquier · Cuirassés · Ronciers)

Planche : `monstres-4-terre.png`

```
Redraw this sheet as 2D mobile RPG monster art. Keep EXACTLY the same 18 creatures in the same 6x3 grid and order, none added or removed; each row is one monster family, the last two of each row are the bigger elite and boss. Each keeps its species, body shape, colors, pose and silhouette: full body, facing right. Upgrade: real creature anatomy, menacing faces, sharp eyes, open mouths with fangs, legs, wings and tails attached naturally under the body, rich textures, painted cel shading, light from top right, rim light, one bold dark outline per creature, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
Row 1, living ivory chess pieces on felt bases, red glowing cracks: knight horse head | rook with fists | pawn throwing a ball | bishop with halo | queen with lance | king with gold sword and crown.
Row 2, armored beasts: armadillo | rhinoceros beetle | pangolin | stone snail with crystals | triceratops | ankylosaurus with club tail.
Row 3, bramble forest: autumn-leaf fox | moss badger with mushrooms | thorn porcupine | bark moth with eye spots | twig mantis | bramble stag with leafy antlers.
```

## Monstres « animaux » à refaire (21/11/2026) : trop réalistes à côté des héros

Les 6 familles d'animaux (Bayou, Cuirassés, Fauves de cendre, Horde des glaces, Ronciers, Volière) sont sorties comme des
illustrations animalières réalistes (poils, écailles, couleurs ternes) ; les héros sont des chibis nets. Planches 16:9,
7 × 3, les 3 dernières cases vides : `node refonte-graphique/planche-ia.cjs liste "m:bayou:0,…,_,_,_" sortie.png 7 16:9`.
À rendre en **4K 16:9**. Si Hailuo accepte une 2e image : `reference-style-personnages.jpg` (6 héros + 6 monstres au bon
style). Après rendu : refaire leur découpe (`decoupe-hailuo.py`) ET leurs morceaux animés (`rig/<id>.json` à reprendre).

### Monstres animaux 1 — Bayou · Cuirassés · Fauves de cendre

Planche : `monstres-style-1.png`

```
Redraw image 1 as 2D mobile RPG monster art in the drawing style of image 2. Keep EXACTLY the same 18 creatures in the same 7x3 grid and order, none added or removed; the last three cells stay EMPTY white. Each keeps its species, body shape, colors, pose and silhouette: full body, facing right. Style: stylized cartoon game art, simple clean shapes, menacing cartoon faces, sharp eyes, open mouths with fangs, legs, wings and tails attached naturally under the body, one bold dark outline per creature, bright vibrant colors, cel shading, light from top right, glowing parts glow. Not realistic, no detailed textures. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
In order: basilisk lizard with orange crest | snapping turtle | archer fish | will-o'-wisp ghost flame | giant catfish | old crocodile | armadillo | rhinoceros beetle | pangolin | stone snail with green crystals | triceratops | ankylosaurus with tail club | spotted hyena | warthog | spitting cobra | vulture | black lioness with ember cracks | ember buffalo, huge horns.
```

### Monstres animaux 2 — Horde des glaces · Ronciers · Volière d'orage

Planche : `monstres-style-2.png`

```
Redraw image 1 as 2D mobile RPG monster art in the drawing style of image 2. Keep EXACTLY the same 18 creatures in the same 7x3 grid and order, none added or removed; the last three cells stay EMPTY white. Each keeps its species, body shape, colors, pose and silhouette: full body, facing right. Style: stylized cartoon game art, simple clean shapes, menacing cartoon faces, sharp eyes, open mouths with fangs, legs, wings and tails attached naturally under the body, one bold dark outline per creature, bright vibrant colors, cel shading, light from top right, glowing parts glow. Not realistic, no detailed textures. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
In order: sabertooth tiger | woolly rhinoceros | narwhal | snowy owl | cave bear | woolly mammoth with only two tusks | leaf fox | moss badger | thorn porcupine | bark moth | twig mantis | bramble stag | falcon | marabou stork | crow | storm peacock | cassowary | giant storm eagle with lightning wings.
```

## Rattrapage (après le premier passage)

Deux planches dans les mêmes conditions que les premières (4K 16:9, grille 6 × 3, mêmes tailles) : un essai au format
21:9, avec des personnages plus petits et mélangés, est ressorti presque identique aux dessins d'origine. Le bas à
droite est laissé vide pour la signature de Hailuo. Le prompt reprend mot pour mot celui qui a marché, avec en plus
une phrase qui demande de tout repeindre (« not the flat vector look of the sheet »).
On y a remis : les 2 personnages du bas à droite de chaque planche (cachés par la signature), et ceux ratés au
premier passage : chamane du volcan, apsara et Morrigane (un bras en trop), minotaure (deux têtes), mammouth
(défenses), buffle de braise (pattes en trop), les 6 abeilles de la Ruche (becs d'oiseau au lieu de mandibules) ;
en bonus Fūjin (sac à vent), Général d'argile (lance en trop) et Ifrit (une lame perdue).
Fabriquées par `node planche-ia.cjs liste "h:fire:6,…" sortie.png 6 16:9`.

### Rattrapage héros

Planche : `rattrapage-heros.png`

```
Redraw this sheet as 2D mobile RPG character art. Keep EXACTLY the same 15 characters in the same 6x3 grid and order, none added or removed; the last three cells stay EMPTY. Each keeps its species, head shape, outfit, colors, weapon in the same hand, pose and silhouette: full body, three-quarter view facing right. Each has exactly two arms and one head. Fully repaint each figure as detailed hand-painted cartoon art with crisp ink lines and textured shading, not the flat vector look of the sheet. Upgrade: chibi proportions, fierce expressive faces, clean anatomy, fingers gripping items, rich materials (metal, cloth, fur, scales), painted cel shading, light from top right, rim light, one bold dark outline per character, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, extra limbs; nothing cropped, no weapon over a face, characters never touch.
Row 1: volcano priestess raising a flame | phoenix girl, flame wings | sun goddess, gold mirror | angel, six wings, golden horn | blue thunder god, ring of drums | water mother, turban, water orb.
Row 2: dragon king, pearl | earth mother, earth orb | underworld king, bident | dancer raising a lotus | dark queen, sword, raised fist | minotaur, double axe.
Row 3: green wind demon, wind bag | terracotta general, sword | black winged demon, two blades.
```

### Rattrapage monstres

Planche : `rattrapage-monstres.png`

```
Redraw this sheet as 2D mobile RPG monster art. Keep EXACTLY the same 16 creatures in the same 6x3 grid and order, none added or removed; the last two cells stay EMPTY. Each keeps its species, body shape, colors, pose and silhouette: full body, facing right. Each has one head and the right number of legs; the six bees and hornets have insect mandibles, never bird beaks. Fully repaint each figure as detailed hand-painted cartoon art with crisp ink lines and textured shading, not the flat vector look of the sheet. Upgrade: real creature anatomy, menacing faces, sharp eyes, open mouths with fangs, legs, wings and tails attached naturally under the body, rich textures, painted cel shading, light from top right, rim light, one bold dark outline per creature, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
Row 1: bronze colossus | great bronze idol, furnace belly | cassowary | thunderbird, lightning wings | giant catfish | old crocodile.
Row 2: twig mantis | bramble stag | woolly mammoth with only two tusks | ember buffalo, four legs, huge horns | worker bee | armored soldier bee.
Row 3: wax-spitting larva | nurse bee, honey cup | giant hornet | crowned queen bee, scepter.
```

### Rattrapage Apsara (après le deuxième passage)

Planche : `rattrapage-apsara.png` : la même héroïne 3 fois (une seule génération, 3 essais : garder le meilleur).
Elle avait encore une main en trop (qui tenait son voile). Tous les autres personnages du rattrapage sont bons.

```
Redraw this sheet as 2D mobile RPG character art. The sheet shows the same dancer three times: draw three versions of her, one per figure, nothing else; the rest of the sheet stays EMPTY white. Each keeps its species, head shape, outfit, colors, weapon in the same hand, pose and silhouette: full body, three-quarter view facing right. She has exactly two arms and two hands: one arm raises a pink lotus, the other is bent with its hand at her chest; her pink veils hang behind her and no hand holds them. Fully repaint her as detailed hand-painted cartoon art with crisp ink lines and textured shading, not the flat vector look of the sheet. Upgrade: chibi proportions, fierce expressive faces, clean anatomy, fingers gripping items, rich materials (metal, cloth, fur, scales), painted cel shading, light from top right, rim light, one bold dark outline, vibrant colors, glowing parts glow. Pure white background, soft shadow under feet. No text, frames, scenery, extra limbs; nothing cropped, no weapon over a face, the three figures never touch.
The dancer: Thai-style celestial dancer, golden spired tiara, teal and gold outfit, bare feet, graceful dance pose.
```

## Effets d'attaque

Deux planches de 16 effets (6 × 3, les 2 dernières cases vides pour la signature), fond NOIR : dans le jeu, les effets
s'ajoutent à la lumière, le noir devient transparent tout seul (pas de découpage du fond). Croquis simples faits par
`node refonte-graphique/effets-ia.cjs 1|2 sortie.png` : Hailuo fait le rendu. Effets gardés pour une prochaine planche
si besoin : bulle de protection, tourbillon d'eau, malédiction, renforcement.

### Effets 1 — physique, feu, eau et glace

Planche : `effets-1.png`

```
Redraw this sheet as 2D mobile RPG attack VFX sprites. Keep EXACTLY the same 16 effects in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY black. Each effect keeps its shape, direction, size and colors. Upgrade: premium hand-painted cartoon VFX like top mobile RPGs, bright white-hot cores, saturated glowing edges, soft bloom, motion streaks, small energy particles and sparks, clean readable silhouettes. Pure flat BLACK background everywhere (the black is removed in game), no gradient, no vignette. No characters, no weapons, no text, no frames, no ground or scenery; nothing cropped, effects never touch.
Row 1, physical: white sword slash arc | golden X cross slash | three red claw slash marks | yellow hit impact star burst | ground shockwave ring with rocks and dust | light-blue piercing thrust streak with air rings.
Row 2, fire: fireball with ember trail | fiery explosion with smoke | flame pillar from the ground | orange fire slash arc | flaming meteor rock falling | ember spark burst.
Row 3, water and ice: water bolt with droplet trail | crashing water splash wave | ice spikes from the ground | frost snowflake burst.
```

### Effets 2 — vent, foudre, terre, nature, soin, lumière, ombre

Planche : `effets-2.png`

```
Redraw this sheet as 2D mobile RPG attack VFX sprites. Keep EXACTLY the same 16 effects in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY black. Each effect keeps its shape, direction, size and colors. Upgrade: premium hand-painted cartoon VFX like top mobile RPGs, bright white-hot cores, saturated glowing edges, soft bloom, motion streaks, small energy particles and sparks, clean readable silhouettes. Pure flat BLACK background everywhere (the black is removed in game), no gradient, no vignette. No characters, no weapons, no text, no frames, no ground or scenery; nothing cropped, effects never touch.
Row 1, wind and lightning: green wind tornado | three green wind blade crescents | yellow lightning bolt strike | blue electric energy orb with arcs | gust of wind with flying leaves | white sonic shockwave rings.
Row 2, earth and nature: brown rock spikes bursting from the ground | ground crack quake with flying rocks | green poison gas cloud with bubbles | thorny green vine whip | swirling leaf storm | falling boulder with dust.
Row 3, support and magic: green healing sparkles with plus signs | golden holy light beam from the sky | golden magic shield | purple dark void orb with tendrils.
```

## Terrains de combat

12 terrains en hauteur (comme l'écran de combat), 3 par planche au format que rend Hailuo (21:9, 3696 × 1584), bande
noire en bas pour la signature. Croquis faits par `node refonte-graphique/terrains-ia.cjs 1..4 sortie.png`. Disposition
commune : ciel et décor au loin en haut, horizon au milieu, sol plat dégagé en bas avec l'ovale de combat au centre.
La campagne (30 chapitres de 40 niveaux) change de terrain tous les 3-4 chapitres.

### Terrains 1 — Campagne 1 à 3 : prairie aux moulins (chapitres 1-4), forêt des ronces (5-8), marais du bayou (9-12)

Planche : `terrains-1.png`

```
Redraw this sheet as 3 separate vertical battle backgrounds for a 2D mobile RPG, side by side, same order, same layout, separated by thin black gaps; the black strip at the bottom stays EMPTY black. Fully repaint each one as rich hand-painted cartoon game art like premium mobile RPG battle scenes, not the flat vector look of the sketch: depth, atmospheric perspective, soft light, detailed textures, vibrant colors. Keep each scene's place, colors, mood and composition: sky and distant scenery in the top half, horizon near the middle, flat open ground in the bottom half with the oval battle area in the center left completely clear for the fighters; decor only on the left and right edges. Front view, from slightly above. No characters, creatures, people, text, UI, frames.
Left: sunny farmland meadow with a windmill, rolling green hills, wooden fence, dirt arena, flowers and haystacks.
Middle: deep bramble forest, giant tree trunks, thorny bramble arches, sun rays, mossy ground, red mushrooms, fireflies.
Right: misty swamp bayou, cypress trees with hanging moss, still water, wooden boardwalk platform, lily pads, lanterns.
```

### Terrains 1 bis — à refaire (21/11/2026) : prairie, forêt des ronces et bayou n'avaient pas le style du jeu

Le premier rendu (21:9) est sorti en peinture réaliste (bayou) et en paysage d'animé doux (prairie) : il jure avec les
héros. Planche 16:9 : `node refonte-graphique/terrains-ia.cjs 1 terrains-1-v2.png 16:9` (bayou plus lumineux, avec
l'ovale de combat). À rendre en **4K 16:9** comme les planches 2 à 4. Si Hailuo accepte une 2e image, joindre
`reference-style-terrains.jpg` (4 fonds au bon style + quelques héros, fabriquée à partir de `public/art/`).

```
Redraw image 1, in the drawing style of image 2, as 3 separate vertical battle backgrounds for a 2D mobile RPG, side by side, same order, same layout, separated by thin black gaps; the black strip at the bottom stays EMPTY black. Art style: stylized cartoon mobile-game background art like Hero Wars battle maps: clean bold shapes, crisp dark outlines around objects, bright saturated cheerful colors, simple cel shading with soft gradients, chunky simplified trees, rocks and props, clear silhouettes. NOT realistic, NOT photographic, NOT a soft anime painting, no fine texture noise, no murky colors, no fog over the ground. Keep each scene's composition: sky and distant scenery in the top half, horizon near the middle, flat open ground in the bottom half with a round battle circle in the center left completely clear for the fighters; decor only on the left and right edges. Front view, slightly from above. No characters, no creatures, no people, no text, no UI, no frames.
Left: sunny farmland meadow, cute windmill, green hills, wooden fence, dirt battle circle, flowers, haystacks.
Middle: bright enchanted forest, big stylized tree trunks, thorny bramble arches, sun rays, mossy grass circle, red mushrooms, fireflies.
Right: cheerful bayou in daylight, stylized cypress trees with hanging moss, turquoise water, round wooden boardwalk platform, lily pads, glowing lanterns.
```

### Terrains 2 — Campagne 4 à 6 : savane de cendres (13-16), toundra glacée (17-20), pics d'orage (21-24)

Planche : `terrains-2.png`

```
Redraw this sheet as 3 separate vertical battle backgrounds for a 2D mobile RPG, side by side, same order, same layout, separated by thin black gaps; the black strip at the bottom stays EMPTY black. Fully repaint each one as rich hand-painted cartoon game art like premium mobile RPG battle scenes, not the flat vector look of the sketch: depth, atmospheric perspective, soft light, detailed textures, vibrant colors. Keep each scene's place, colors, mood and composition: sky and distant scenery in the top half, horizon near the middle, flat open ground in the bottom half with the oval battle area in the center left completely clear for the fighters; decor only on the left and right edges. Front view, slightly from above. No characters, no creatures, no people, no text, no UI, no frames.
Left: ash savanna at dusk, erupting volcano far away, dark acacia trees, cracked dark ground with glowing lava cracks, embers.
Middle: frozen tundra, aurora in the sky, snowy mountains, snowy pine trees, icy ground, ice crystals.
Right: stormy mountain peaks, dark purple storm clouds, lightning, sharp rock spires, rope bridge, windswept stone plateau.
```

### Terrains 3 — Campagne 7-8 et Tour : désert du temple d'airain (25-27), grotte des abysses (28-30), sommet de la Tour des Épreuves

Planche : `terrains-3.png`

```
Redraw this sheet as 3 separate vertical battle backgrounds for a 2D mobile RPG, side by side, same order, same layout, separated by thin black gaps; the black strip at the bottom stays EMPTY black. Fully repaint each one as rich hand-painted cartoon game art like premium mobile RPG battle scenes, not the flat vector look of the sketch: depth, atmospheric perspective, soft light, detailed textures, vibrant colors. Keep each scene's place, colors, mood and composition: sky and distant scenery in the top half, horizon near the middle, flat open ground in the bottom half with the oval battle area in the center left completely clear for the fighters; decor only on the left and right edges. Front view, slightly from above. No characters, no creatures, no people, no text, no UI, no frames.
Left: golden desert at sunset, ancient bronze temple with columns, two giant bronze statues, sand dunes, sand arena with stone tiles.
Middle: deep underwater abyss cave, stalactites, light shafts from above, glowing jellyfish, sunken shipwreck, pink corals, glowing sea floor.
Right: top of a magic tower above the clouds, round stone platform with glowing blue runes, broken white pillars, floating rocks.
```

### Terrains 4 — Modes : donjons, arène, antre des boss (boss du jour et de guilde)

Planche : `terrains-4.png`

```
Redraw this sheet as 3 separate vertical battle backgrounds for a 2D mobile RPG, side by side, same order, same layout, separated by thin black gaps; the black strip at the bottom stays EMPTY black. Fully repaint each one as rich hand-painted cartoon game art like premium mobile RPG battle scenes, not the flat vector look of the sketch: depth, atmospheric perspective, soft light, detailed textures, vibrant colors. Keep each scene's place, colors, mood and composition: sky and distant scenery in the top half, horizon near the middle, flat open ground in the bottom half with the oval battle area in the center left completely clear for the fighters; decor only on the left and right edges. Front view, slightly from above. No characters, no creatures, no people, no text, no UI, no frames.
Left: underground dungeon cave, dark cave mouth, purple and blue crystals, piles of gold coins, wall torches, stone floor.
Middle: sunny gladiator arena, stone colosseum walls with red banners, sand floor, blue sky.
Right: boss lair, dark red volcanic hall, huge gate with chains, fire braziers, lava streams, stone floor with a glowing orange circle.
```

## Interface

6 planches de 16 éléments (6 × 3, les 2 dernières cases vides pour la signature), fond blanc, sans texte. Croquis faits par
`node refonte-graphique/ui-ia.cjs 1..6 sortie.png` : les pictos actuels du jeu (`kit.tsx`) et des croquis simples pour le
reste. Direction artistique (réponses du propriétaire, 19/11/2026) : monde lumineux et joyeux, fantasy médiévale, ados et
adultes, menus « moderne épuré » ; pictos dans le même rendu que les héros Hailuo (contour net, ombré peint).
21/11/2026 : style renforcé dans les 6 prompts (« Hero Wars / AFK Arena », pas réaliste). À rendre en 4K 16:9 ; si Hailuo
accepte une 2e image, joindre `reference-style-personnages.jpg`.

### Interface 1 — Monnaies et ressources

Planche : `interface-1.png`

```
Redraw image 1 as 2D mobile RPG game icons in the drawing style of image 2. Keep EXACTLY the same 16 icons in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY white. Each keeps its object, shape, main colors and orientation. Fully repaint each as cartoon game icons in the style of Hero Wars or AFK Arena, for a bright, joyful medieval-fantasy mobile RPG: chunky simple shapes readable at small size, crisp bold dark outline, cel shading with soft gradients, light from top right, glossy highlights, bright saturated colors, slight 3D volume. NOT realistic, no photo textures, no fine detail, not the flat vector look of the sketch. Centered, same size. Pure white background. No text, no letters, no numbers, no frames, no backdrop behind icons; nothing cropped, icons never touch.
Row 1, currencies: gold coin with an embossed crown | teal essence droplet | pink faceted gem | golden summoning scroll with purple wax seal | plain blue-grey basic scroll | purple magic crystal.
Row 2: golden hero soul shards | sparkling teal and purple dust (recycling) | red arena token with crossed swords | blue guild coin with a shield crest | yellow lightning bolt (power) | gift box with ribbon.
Row 3: green play-video button | round clock | padlock | gold star.
```

### Interface 2 — Menus

Planche : `interface-2.png`

```
Redraw image 1 as 2D mobile RPG game icons in the drawing style of image 2. Keep EXACTLY the same 16 icons in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY white. Each keeps its object, shape, main colors and orientation. Fully repaint each as cartoon game icons in the style of Hero Wars or AFK Arena, for a bright, joyful medieval-fantasy mobile RPG: chunky simple shapes readable at small size, crisp bold dark outline, cel shading with soft gradients, light from top right, glossy highlights, bright saturated colors, slight 3D volume. NOT realistic, no photo textures, no fine detail, not the flat vector look of the sketch. Centered, same size. Pure white background. No text, no letters, no numbers, no frames, no backdrop behind icons; nothing cropped, icons never touch.
Row 1, menus: red battle flag on a pole | knight shield | glowing star medallion (summon) | folded treasure map | guild banner with crest | calendar with a green check mark.
Row 2: envelope letter | quest scroll with check mark | shopping bag | purple pass ticket with a star | golden trophy cup | two friends silhouettes.
Row 3: blue chat speech bubble | settings gear | purple and gold orbs merging (fusion) | teal circular arrow around a soul (rebirth).
```

### Interface 3 — Modes et équipement

Planche : `interface-3.png`

```
Redraw image 1 as 2D mobile RPG game icons in the drawing style of image 2. Keep EXACTLY the same 16 icons in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY white. Each keeps its object, shape, main colors and orientation. Fully repaint each as cartoon game icons in the style of Hero Wars or AFK Arena, for a bright, joyful medieval-fantasy mobile RPG: chunky simple shapes readable at small size, crisp bold dark outline, cel shading with soft gradients, light from top right, glossy highlights, bright saturated colors, slight 3D volume. NOT realistic, no photo textures, no fine detail, not the flat vector look of the sketch. Centered, same size. Pure white background. No text, no letters, no numbers, no frames, no backdrop behind icons; nothing cropped, icons never touch.
Row 1, game modes: stone trial tower | compass | dungeon gate archway | horned skull (boss) | two crossed swords (arena) | wooden siege catapult.
Row 2: gold mine entrance with coins | magic spring of teal essence | anvil with a sword (armory) | sword | chest armor | knight helmet.
Row 3: leather boots | leather bag | forge hammer on an anvil | recycle arrows with sparkling dust.
```

### Interface 4 — Éléments, rôles et statistiques

Planche : `interface-4.png`

```
Redraw image 1 as 2D mobile RPG game icons in the drawing style of image 2. Keep EXACTLY the same 16 icons in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY white. Each keeps its object, shape, main colors and orientation. Fully repaint each as cartoon game icons in the style of Hero Wars or AFK Arena, for a bright, joyful medieval-fantasy mobile RPG: chunky simple shapes readable at small size, crisp bold dark outline, cel shading with soft gradients, light from top right, glossy highlights, bright saturated colors, slight 3D volume. NOT realistic, no photo textures, no fine detail, not the flat vector look of the sketch. Centered, same size. Pure white background. No text, no letters, no numbers, no frames, no backdrop behind icons; nothing cropped, icons never touch.
Row 1, elements and roles: fire flame | green wind swirl | blue water drop | brown earth rock peak with grass | blue protector shield with cross | warrior crossed swords.
Row 2: wooden bow with arrow | twin daggers | green healing cross | golden support figure with aura | red heart (health) | short sword (attack).
Row 3: steel shield (defense) | winged boot (speed) | red target (critical) | swift blue wind trails (dodge).
```

### Interface 5 — Accueil et récompenses (coffre, sablier…)

Planche : `interface-5.png`

```
Redraw image 1 as 2D mobile RPG game icons in the drawing style of image 2. Keep EXACTLY the same 16 icons in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY white. Each keeps its object, shape, main colors and orientation. Fully repaint each as cartoon game icons in the style of Hero Wars or AFK Arena, for a bright, joyful medieval-fantasy mobile RPG: chunky simple shapes readable at small size, crisp bold dark outline, cel shading with soft gradients, light from top right, glossy highlights, bright saturated colors, slight 3D volume. NOT realistic, no photo textures, no fine detail, not the flat vector look of the sketch. Centered, same size. Pure white background. No text, no letters, no numbers, no frames, no backdrop behind icons; nothing cropped, icons never touch.
Row 1, home and rewards: closed wooden treasure chest with gold trim | open chest full of gold coins and a gem | golden hourglass with flowing sand | small silver reward chest | purple summoning portal | golden crown with a ruby.
Row 2: golden victory trophy | broken sword (defeat) | empty grey star | pile of gold coins | pile of pink gems | orange star burst (critical damage).
Row 3: clenched fist (tenacity) | red notification badge with exclamation mark | green level-up arrow | round gold avatar frame with a small level badge.
```

### Interface 6 — Boutons, cadres et fenêtres

Planche : `interface-6.png`

```
Redraw image 1 as a 2D mobile RPG user interface kit in the drawing style of image 2. Keep EXACTLY the same 16 elements in the same 6x3 grid and order, one per cell, none added or removed; the last two cells stay EMPTY white. Each keeps its shape, proportions and main color. Style: modern and clean, not ornate, matching a bright joyful medieval-fantasy mobile RPG: glossy rounded shapes, soft bevel, subtle gold accents, cel shading with soft gradients, light from top right, crisp bold dark outline, like Hero Wars or AFK Arena menus. NOT realistic, no photo textures, no ornate detail. Every button, frame and panel keeps a large FLAT EMPTY center (text is added in game). Front view, no perspective. Pure white background. No text, no letters, no numbers, no icons inside buttons; nothing cropped, elements never touch.
Row 1: wide rounded buttons, green | red | blue | purple | gold | grey (disabled).
Row 2: round dark navy icon button with gold rim | round dark close button with white X | empty hero card frames: grey common | blue rare | purple epic | gold legendary with a small star.
Row 3: dark navy window panel with thin gold border and header strip | red ribbon title banner | dark resource capsule with a coin slot and green plus button | dark bottom tab bar with one highlighted tab.
```

## Retouches après le rendu du 21/11/2026

Rendus gardés dans `hailuo-v1/` : `terrains-1.jpg` (l'ancien : `terrains-1-v1.jpg`), `monstres-style-1.jpg`,
`monstres-style-2.jpg`, `interface-1..6.jpg`. Planches de retouche faites à partir de ces rendus (découpés tels quels) :
6 monstres à l'anatomie fausse et 8 pictos peu lisibles ou en double. À rendre en 4K 16:9, référence
`reference-style-personnages.jpg`.

### Retouche monstres — `retouche-monstres.png` (silure, pangolin, ankylosaure, lionne, mante, casoar)

```
Redraw image 1 as 2D mobile RPG monster art in the drawing style of image 2. Keep EXACTLY the same 6 creatures in the same 4x2 grid and order, none added or removed; the last two cells stay EMPTY white. Keep each one's colors, face, size and look, full body, facing right, and only fix its anatomy:
1. giant catfish: one long fish body lying low, its tail fin stays low and flat behind it, never raised like a neck; long whiskers.
2. pangolin: only ONE scaly tail, curled behind it; no second tail.
3. ankylosaurus: short thick tail held low behind it with a bony club at the tip, near the ground; no long raised tail.
4. black lioness: a slim big cat, cat head with small ears and a longer muzzle, long legs, long thin tail with an ember tip; NOT a bear.
5. twig mantis: a praying mantis with exactly four thin walking legs and two folded front claws, long thin body.
6. cassowary: a big flightless bird standing on its two legs only, no arms, no hands, tiny wings hidden in its black feathers.
Style: stylized cartoon game art, one bold dark outline per creature, bright vibrant colors, cel shading, light from top right. Not realistic. Pure white background, soft shadow under feet. No text, frames, scenery, people, extra limbs; nothing cropped, creatures never touch.
```

### Retouche interface — `retouche-interface.png` (fragments, bannière de guilde, amis, forge, recyclage, guerrier, soutien, barre d'onglets)

```
Redraw image 1 as 2D mobile RPG game icons in the drawing style of image 2. Keep EXACTLY 8 icons in the same 5x2 grid and order, one per cell, none added or removed; the last two cells stay EMPTY white. Keep their cartoon look (crisp bold dark outline, cel shading, glossy highlights, bright saturated colors, slight 3D volume) but change each one as described:
1. hero soul shards: three glowing golden crystal shards with a soft glow.
2. guild banner: blue hanging banner with gold trim and a golden lion head crest in the middle.
3. friends: two smiling cartoon adventurer faces side by side, one in a blue hood, one with brown hair.
4. forge: a big blacksmith hammer striking a glowing orange hot blade on an anvil, sparks.
5. recycle: two curved teal arrows chasing each other in a circle, sparkling dust in the middle.
6. warrior role: one big double-bladed battle axe, steel head, wooden handle.
7. support role: a golden magic staff topped with a glowing star, soft yellow aura.
8. tab bar: long dark navy horizontal bar with thin gold border, split into four equal empty tabs, the second tab raised and lit in gold.
Centered, same size. Pure white background. No text, no letters, no numbers, no frames; nothing cropped, icons never touch.
```

### Retouche Apsara — `retouche-apsara.png` (3 essais, garder le meilleur)

Tête trop petite, corps trop fin et dessin trop « aquarelle » à côté des autres héros. Planche faite à partir de son rendu
Hailuo, tête agrandie ×1,3 (le bras et le lotus gardés à leur place).

```
Redraw image 1 as 2D mobile RPG character art in the drawing style of image 2. The sheet shows the same dancer three times: draw three versions of her, one per figure, nothing else; the right part of the sheet stays EMPTY white. Keep her outfit, colors, golden spired tiara, pink lotus, pink veils and pose: full body, three-quarter view facing right. Give her the same head size, proportions and finish as the heroes of image 2: chibi proportions, simple clean shapes, one bold dark outline, bright vibrant colors, cel shading, light from top right. She has exactly two arms and two hands: one arm raises a pink lotus, the other is bent with its hand at her chest; her veils hang behind her and no hand holds them. Not realistic, no soft watercolor painting, no fine detail. Pure white background, soft shadow under feet. No text, frames, scenery, extra limbs; nothing cropped, the three figures never touch.
```
