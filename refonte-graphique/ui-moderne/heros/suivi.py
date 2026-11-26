"""Page de suivi de la refonte des héros en vectoriel (pour le propriétaire, 26/11/2026).

python3 refonte-graphique/ui-moderne/heros/suivi.py
→ refonte-graphique/ui-moderne/heros/suivi/index.html + images (px/, vx/, gif/) à publier ensemble (Artifact).

État d'un héros :
- « fait » / « à revoir » : lu dans refonte-graphique/pixel/sortie/ui/vecto/<nom>/STATUT.txt (première ligne) ;
- « en cours » : son dossier refonte-graphique/ui-moderne/heros/<nom>/ existe mais pas encore de STATUT ;
- « à faire » : rien encore.
"""
import html
import json
import os
import re
import subprocess

from PIL import Image

RACINE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
HEROS = os.path.join(RACINE, 'refonte-graphique', 'ui-moderne', 'heros')
SORTIE_V = os.path.join(RACINE, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto')
PAGE = os.path.join(HEROS, 'suivi')

RARETE = {'legendary': 'Légendaire', 'epic': 'Épique', 'rare': 'Rare', 'common': 'Commun'}
ELEMENT = {'fire': 'feu', 'water': 'eau', 'earth': 'terre', 'wind': 'vent'}
ORDRE = ['legendary', 'epic', 'rare', 'common']


def slug(nom):
    t = nom.lower()
    for a, b in (('é', 'e'), ('è', 'e'), ('ê', 'e'), ('ë', 'e'), ('à', 'a'), ('ï', 'i'), ('ô', 'o')):
        t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def heros():
    out = subprocess.run(['npx', 'tsx', '-e', (
        "import { HEROES } from './src/core/data/heroes'; import { heroArt } from './src/game/look';"
        "console.log(JSON.stringify(HEROES.map(h => ({ id: h.id, name: h.name, r: h.rarity, el: h.element, art: heroArt(h.id) }))));")],
        cwd=RACINE, capture_output=True, text=True, check=True).stdout
    return json.loads(out.strip().splitlines()[-1])


def vignette(src, dst, h):
    im = Image.open(src).convert('RGBA')
    k = h / im.height
    im = im.resize((max(1, round(im.width * k)), h), Image.NEAREST if im.height < h else Image.LANCZOS)
    im.save(dst, quality=88, method=6)


def gif_petit(src, dst, w=420):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf',
                    f'fps=12,scale={w}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse',
                    dst], check=True)


def main():
    for d in ('px', 'vx', 'gif'):
        os.makedirs(os.path.join(PAGE, d), exist_ok=True)
    rows = []
    for h in sorted(heros(), key=lambda h: (ORDRE.index(h['r']), h['el'], h['name'])):
        s = slug(h['name'])
        statut, note = 'à faire', ''
        f = os.path.join(SORTIE_V, s, 'STATUT.txt')
        if os.path.exists(f):
            lignes = open(f, encoding='utf-8').read().strip().splitlines()
            statut = 'fait' if lignes and lignes[0].strip().lower().startswith('fait') else 'à revoir'
            note = ' '.join(l.strip() for l in lignes[1:])[:240] if statut == 'fait' else ' '.join(lignes)[:240]
        elif os.path.isdir(os.path.join(HEROS, s)):
            statut = 'en cours'
        vignette(os.path.join(RACINE, 'public', 'art', 'hd', 'pose', f"{h['art']}.webp"), os.path.join(PAGE, 'px', f"{h['id']}.webp"), 360)
        vx = os.path.join(RACINE, 'public', 'art', 'vecto', f"{h['art']}.webp")
        has_vx = statut in ('fait', 'à revoir') and os.path.exists(vx)
        if has_vx:
            vignette(vx, os.path.join(PAGE, 'vx', f"{h['id']}.webp"), 360)
        g = os.path.join(SORTIE_V, s, 'anim.gif')
        has_gif = has_vx and os.path.exists(g)
        dg = os.path.join(PAGE, 'gif', f"{h['id']}.gif")
        if has_gif and (not os.path.exists(dg) or os.path.getmtime(g) > os.path.getmtime(dg) or Image.open(dg).width < 420):
            gif_petit(g, os.path.join(PAGE, 'gif', f"{h['id']}.gif"))
        rows.append((h, statut, note, has_vx, has_gif))

    n = {k: sum(1 for r in rows if r[1] == k) for k in ('fait', 'à revoir', 'en cours', 'à faire')}
    cartes = []
    for h, statut, note, has_vx, has_gif in rows:
        cls = {'fait': 'ok', 'à revoir': 'redo', 'en cours': 'wip', 'à faire': 'todo'}[statut]
        vx_html = (f'<img src="gif/{h["id"]}.gif" alt="{html.escape(h["name"])} animé" loading="lazy">' if has_gif
                   else f'<img src="vx/{h["id"]}.webp" alt="{html.escape(h["name"])} vectoriel" loading="lazy">' if has_vx
                   else '<span class="vide">—</span>')
        cartes.append(f'''<article class="hero {cls} r-{h["r"]}">
  <header><h3>{html.escape(h["name"])}</h3><span class="pill">{statut}</span></header>
  <p class="meta">{RARETE[h["r"]]} · {ELEMENT[h["el"]]}</p>
  <div class="duo"><figure><img src="px/{h["id"]}.webp" alt="{html.escape(h["name"])} pixel art" loading="lazy"><figcaption>avant</figcaption></figure>
  <figure>{vx_html}<figcaption>après</figcaption></figure></div>
  {f'<p class="note">{html.escape(note)}</p>' if note else ''}
</article>''')
    page = f'''<title>Refonte des héros</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* une salle de pierre sombre et or, comme le jeu ; un seul thème, voulu */
:root {{ --bg: #15131b; --panel: #221f2b; --line: #3a3546; --text: #f1ece0; --muted: #aaa3b8; --gold: #e8b64c;
  --ok: #5fcf8a; --redo: #ff8a6a; --wip: #e8b64c; --todo: #6f6880;
  --display: "Lilita One", "Trebuchet MS", sans-serif; --body: "Fredoka", system-ui, sans-serif; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--text); font: 15px/1.45 var(--body); }}
main {{ max-width: 1180px; margin: 0 auto; padding-block: 24px 40px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
h1 {{ font: 400 clamp(28px, 6vw, 40px)/1.1 var(--display); color: var(--gold); margin: 0 0 6px; text-wrap: balance; }}
.sub {{ color: var(--muted); margin: 0 0 18px; max-width: 65ch; }}
.bar {{ display: flex; flex-wrap: wrap; gap: 8px 16px; margin: 0 0 22px; font-variant-numeric: tabular-nums; }}
.bar span {{ padding: 6px 12px; border-radius: 999px; background: var(--panel); border: 1px solid var(--line); }}
.bar b {{ font: 400 18px var(--display); margin-right: 6px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 420px), 1fr)); gap: 14px; }}
.hero {{ background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 12px; min-width: 0; }}
.hero header {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
.hero h3 {{ margin: 0; font: 400 24px var(--display); }}
.pill {{ font-size: 12px; padding: 3px 10px; border-radius: 999px; color: #111; text-transform: uppercase; letter-spacing: .04em; }}
.ok .pill {{ background: var(--ok); }} .redo .pill {{ background: var(--redo); }} .wip .pill {{ background: var(--wip); }} .todo .pill {{ background: var(--todo); color: var(--text); }}
.meta {{ margin: 2px 0 8px; color: var(--muted); font-size: 13px; }}
.duo {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
figure {{ margin: 0; background: #1a1822; border-radius: 10px; display: grid; place-items: center; min-height: 260px; padding: 8px; cursor: zoom-in; }}
figure img {{ max-height: 320px; width: auto; image-rendering: auto; }}
.duo {{ grid-template-columns: 1fr 1.4fr; }}
#zoom {{ border: 0; padding: 0; background: #0d0b12f2; max-width: 100vw; max-height: 100vh; width: 100vw; height: 100vh; }}
#zoom img {{ width: 100%; height: 100%; object-fit: contain; }}
#zoom::backdrop {{ background: #000c; }}
.duo figure:first-child img {{ image-rendering: pixelated; }}
figcaption {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }}
.vide {{ color: var(--todo); font: 400 28px var(--display); }}
.note {{ margin: 8px 0 0; font-size: 13px; color: var(--muted); }}
.r-legendary {{ border-color: #7a5d22; }}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500&family=Lilita+One&display=swap">
<main>
<h1>Refonte des héros</h1>
<p class="sub">Chaque héros redessiné dans le style de l’interface et animé. À gauche le pixel art d’avant, à droite le nouveau dessin (animé quand il est fini). Dis-moi lesquels reprendre.</p>
<div class="bar"><span><b>{n["fait"]}</b>faits</span><span><b>{n["à revoir"]}</b>à revoir</span><span><b>{n["en cours"]}</b>en cours</span><span><b>{n["à faire"]}</b>à faire</span><span><b>{len(rows)}</b>héros</span></div>
<section class="grid">
{chr(10).join(cartes)}
</section>
</main>
<dialog id="zoom"><img alt=""></dialog>
<script>
const z = document.getElementById('zoom');
document.addEventListener('click', (e) => {{
  const img = e.target.closest('figure') ? e.target.closest('figure').querySelector('img') : null;
  if (z.open) {{ z.close(); return; }}
  if (img) {{ z.querySelector('img').src = img.src; z.querySelector('img').style.imageRendering = img.closest('figure').parentElement.firstElementChild === img.closest('figure') ? 'pixelated' : 'auto'; z.showModal(); }}
}});
</script>
'''
    open(os.path.join(PAGE, 'index.html'), 'w', encoding='utf-8').write(page)
    print(f"suivi : {n} → {os.path.relpath(os.path.join(PAGE, 'index.html'), RACINE)}")


if __name__ == '__main__':
    main()
