// Un héros en pied (pas seulement son visage), posé dans une boîte 200 × 240 : ses pieds sont toujours au même endroit
// (53 % de la largeur, 95 % de la hauteur) et tous ont la même échelle qu'au combat (un grand reste plus grand).
// Il respire : sa bande d'images (art/hd/pied/<id>.webp, refonte-graphique/pixel/hd/anim/vignettes.py) défile par le CSS.
// Sert à l'estrade de l'onglet Héros, au choix de la section et à la page d'un héros.
import { figureUrl, heroImage } from '../art';
import { HD_FIG } from '../hd-figures';
import { heroArt } from '../look';
import { vectoFig } from '../vecto';

/** Un pixel du dessin, en unités de la boîte (200 × 240) : un héros de 115 pixels mesure 200 unités. */
const BOX_PER_PX = 1.75;

/** Les mesures de la bande d'un personnage HD (voir hd-figures.ts). */
function fig(id: string): [number, number, number, number, number, number] | undefined {
  return (HD_FIG.chars as Record<string, readonly number[] | undefined>)[id] as [number, number, number, number, number, number] | undefined;
}

/** La bande qui défile (steps CSS) : chacun respire à son rythme, un décalage tiré de son nom. */
function Strip({ id, n, ms }: { id: string; n: number; ms: number }) {
  let hash = 0;
  for (const ch of id) hash = (hash * 31 + ch.charCodeAt(0)) % 997;
  return (
    <img src={figureUrl(id)} alt="" draggable={false} style={{
      width: `${n * 100}%`, animation: `px-idle ${((n * ms) / 1000).toFixed(2)}s steps(${n}) infinite`, animationDelay: `-${(((hash % n) * ms) / 1000).toFixed(2)}s`,
    }} />
  );
}

/** N'importe quel personnage HD (monstre, boss) qui respire, à la largeur de son cadre (regard tourné par le CSS). */
export function Figure({ id, class: cls = '' }: { id: string; class?: string }) {
  const m = fig(id);
  if (!m) return <img class={cls} src={heroImage(id)} alt="" />;
  const [w, h, , , n, ms] = m;
  return <span class={`px-fit ${cls}`} style={{ aspectRatio: `${w} / ${h}` }}><Strip id={id} n={n} ms={ms} /></span>;
}

/** `vecto` : toujours le dessin vectoriel quand il existe (tirage des invocations), même sans `?vecto=1`. */
export function HeroFigure({ defId, class: cls = '', vecto = false }: { defId: string; class?: string; vecto?: boolean }) {
  const art = heroArt(defId);
  const v = vectoFig(art, vecto);
  if (v) {
    // essai ?vecto=1 : le dessin vectoriel lisse, même échelle et mêmes pieds que le pixel art (il respire par le CSS)
    const left = 53 - ((v.fx * BOX_PER_PX) / 200) * 100, top = 95 - ((v.fy * BOX_PER_PX) / 240) * 100;
    return (
      <span class={`hfig hfig-vec ${cls}`}>
        <span class="px-win vec-win" style={{ left: `${left.toFixed(2)}%`, top: `${top.toFixed(2)}%`, width: `${(((v.w * BOX_PER_PX) / 200) * 100).toFixed(2)}%`, aspectRatio: `${v.w} / ${v.h}` }}>
          <img src={v.big} alt="" draggable={false} />
        </span>
      </span>
    );
  }
  const m = fig(art);
  if (!m) return <span class={`hfig ${cls}`}><img class="hfig-flat" src={heroImage(defId)} alt="" /></span>;
  const [w, h, fx, fy, n, ms] = m;
  const left = 53 - ((fx * BOX_PER_PX) / 200) * 100, top = 95 - ((fy * BOX_PER_PX) / 240) * 100;
  return (
    <span class={`hfig hfig-px ${cls}`}>
      <span class="px-win" style={{ left: `${left.toFixed(2)}%`, top: `${top.toFixed(2)}%`, width: `${(((w * BOX_PER_PX) / 200) * 100).toFixed(2)}%`, aspectRatio: `${w} / ${h}` }}>
        <Strip id={art} n={n} ms={ms} />
      </span>
    </span>
  );
}
