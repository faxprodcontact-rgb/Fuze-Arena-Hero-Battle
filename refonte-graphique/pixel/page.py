# La page d'essai : le combat animé (fond + 5 héros + 5 monstres aux places du jeu), puis chaque personnage en grand.
# Écrit aussi les bandes d'animation dans sortie/ (8 images de 96 × 96 chacune) et le fond (240 × 388).
# python3 page.py sortie.html
import sys, os, io, base64, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'persos'))
from PIL import Image, ImageDraw
from pix import sheet, FRAME_W, FRAME_H, OX, OY
import fond
from scene import HEROES, MONSTERS, HERO_X, ENEMY_X, FEET

NAMES = {'kael': ('Kael', 'Héros · feu'), 'sable': ('Sable', 'Héroïne · soleil'), 'eldra': ('Eldra', 'Héroïne · bâton'),
         'rook': ('Rook', 'Héroïne · phénix'), 'ilian': ('Ilian', 'Héros · mers'),
         'renard': ('Renard de feuilles', 'Ronciers'), 'dino': ('Dino-voile', 'Bayou'), 'follet': ('Feu follet', 'Bayou'),
         'petard': ('Pétard', 'Parade'), 'chouette': ('Chouette des neiges', 'Glaces')}
OUT_DIR = os.path.join(HERE, 'sortie')


def b64(im):
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def main(out):
    os.makedirs(OUT_DIR, exist_ok=True)
    sheets = {}
    for pid, _ in HEROES + MONSTERS:
        sh = sheet(importlib.import_module(pid).draw)
        sh.save(os.path.join(OUT_DIR, f'{pid}.png'))
        sheets[pid] = b64(sh)
    bg = fond.draw().convert('RGBA')
    for pid, s in HEROES + MONSTERS:
        x = HERO_X[s] if (pid, s) in HEROES else ENEMY_X[s]
        shadow = Image.new('RGBA', (40, 8), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse((0, 0, 39, 7), fill=(20, 40, 16, 110))
        bg.alpha_composite(shadow, (x - 20, FEET[s] - 5))
    bg.save(os.path.join(OUT_DIR, 'fond-clairiere.png'))
    units = sorted([(FEET[s], HERO_X[s], pid, False) for pid, s in HEROES] + [(FEET[s], ENEMY_X[s], pid, True) for pid, s in MONSTERS])
    sprites = ''
    for k, (feet, x, pid, flip) in enumerate(units):
        fx = OX + 48 if not flip else FRAME_W - OX - 48
        left, top = (x - fx) / fond.W * 100, (feet - 94 - OY) / fond.H * 100
        sprites += (f'<div class="unit{" flip" if flip else ""}" style="left:{left:.3f}%;top:{top:.3f}%">'
                    f'<img src="{sheets[pid]}" alt="{NAMES[pid][0]}" style="animation-delay:-{(k * 0.37) % 1.12:.2f}s"></div>')

    def cards(group):
        return ''.join(f'<figure class="card"><div class="frame"><img src="{sheets[pid]}" alt="{NAMES[pid][0]}" '
                       f'style="animation-delay:-{(k * 0.29) % 1.12:.2f}s"></div><figcaption><b>{NAMES[pid][0]}</b><span>{NAMES[pid][1]}</span></figcaption></figure>'
                       for k, (pid, _) in enumerate(group))

    html = f'''<title>Essai pixel art</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lilita+One&family=Fredoka:wght@400;600&display=swap">
<style>
/* une seule ambiance, celle du jeu : émail bleu nuit cerclé d'or ; la scène au centre, les fiches en grille dessous */
:root {{
  --night: #0f1a33; --enamel: #17284a; --rim: #e8b54a; --rim-soft: #8a6a2a; --ink: #f3ecdc; --muted: #a9b4cc;
  --display: "Lilita One", "Trebuchet MS", system-ui, sans-serif; --text: "Fredoka", system-ui, sans-serif;
  color-scheme: dark;
}}
body {{ background: var(--night); color: var(--ink); font-family: var(--text); font-size: 16px; }}
.wrap {{ max-width: 1040px; margin: 0 auto; padding-block: 28px 48px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 36px; }}
h1, h2 {{ font-family: var(--display); font-weight: 400; letter-spacing: .02em; margin: 0; text-wrap: balance; }}
h1 {{ font-size: clamp(28px, 6vw, 44px); color: var(--rim); }}
h2 {{ font-size: 24px; }}
p {{ margin: 0; color: var(--muted); max-width: 65ch; line-height: 1.5; }}
header {{ display: grid; gap: 10px; }}
section {{ display: grid; gap: 16px; }}
.stage {{ position: relative; width: min(480px, 100%); aspect-ratio: 240 / 420; margin: 0 auto; border: 3px solid var(--rim);
  border-radius: 18px; overflow: hidden; box-shadow: 0 0 0 6px var(--enamel), 0 18px 40px rgba(0,0,0,.45);
  background: url({b64(bg)}) 0 0 / 100% 100%; image-rendering: pixelated; }}
.unit {{ position: absolute; width: {FRAME_W / 240 * 100:.3f}%; aspect-ratio: {FRAME_W} / {FRAME_H}; overflow: hidden; }}
.unit.flip {{ transform: scaleX(-1); }}
.unit img, .frame img {{ display: block; width: 800%; max-width: none; height: 100%; image-rendering: pixelated; animation: idle 1.12s steps(8) infinite; }}
@keyframes idle {{ to {{ transform: translateX(-100%); }} }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 14px; }}
.card {{ margin: 0; background: var(--enamel); border: 2px solid var(--rim-soft); border-radius: 14px; padding: 10px; display: grid; gap: 8px; }}
.frame {{ aspect-ratio: {FRAME_W} / {FRAME_H}; overflow: hidden; border-radius: 8px; background: linear-gradient(#2f6f9a, #173f6b); }}
figcaption {{ display: grid; gap: 2px; }}
figcaption b {{ font-family: var(--display); font-weight: 400; font-size: 19px; }}
figcaption span {{ color: var(--muted); font-size: 13px; letter-spacing: .04em; text-transform: uppercase; }}
@media (prefers-reduced-motion: reduce) {{ .unit img, .frame img {{ animation: none; }} }}
</style>
<div class="wrap">
  <header>
    <h1>Essai pixel art</h1>
    <p>Personnages de 96 × 96 pixels, fond de 240 × 388 pixels (trois fois plus petit que l’écran de combat du jeu, agrandi sans flou). Une palette commune, une seule lumière en haut à droite, le même contour et les mêmes yeux « tampons » pour tous. Chaque personnage respire et cligne des yeux.</p>
  </header>
  <section>
    <h2>Le combat</h2>
    <div class="stage">{sprites}</div>
  </section>
  <section>
    <h2>Les héros</h2>
    <div class="grid">{cards(HEROES)}</div>
  </section>
  <section>
    <h2>Les monstres</h2>
    <div class="grid">{cards(MONSTERS)}</div>
  </section>
</div>
'''
    open(out, 'w').write(html)
    print(out, len(html) // 1024, 'Ko')


if __name__ == '__main__':
    main(sys.argv[1])
