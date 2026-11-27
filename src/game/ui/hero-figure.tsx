// Un héros en pied (pas seulement son visage), posé dans une boîte 200 × 240 : ses pieds sont toujours au même endroit
// (53 % de la largeur, 95 % de la hauteur) et tous ont la même échelle qu'au combat (un grand reste plus grand).
// Son dessin vectoriel (art/vecto/<id>.webp, vecto.ts), lisse ; il respire par le CSS (pieds fixes).
// Sert à l'estrade de l'onglet Héros, au choix de la section, à la préparation et au tirage des invocations.
import { heroImage } from '../art';
import { heroArt } from '../look';
import { vectoFig } from '../vecto';
import { VectoImage } from './vecto-live';

/** Un pixel du dessin, en unités de la boîte (200 × 240) : un héros de 115 pixels mesure 200 unités. */
const BOX_PER_PX = 1.75;

/** N'importe quel personnage dessiné (monstre, boss), à la largeur de son cadre (regard tourné par le CSS). */
export function Figure({ id, class: cls = '' }: { id: string; class?: string }) {
  const v = vectoFig(id);
  if (!v) return null;
  return <img class={cls} src={v.big} alt="" draggable={false} style={{ aspectRatio: `${v.w} / ${v.h}` }} />;
}

/** `live` : le héros joue son signe du repos (vecto-live.tsx) : là où il est en grand et peu nombreux. */
export function HeroFigure({ defId, class: cls = '', live = false }: { defId: string; class?: string; live?: boolean }) {
  const art = heroArt(defId);
  const v = vectoFig(art);
  if (!v) return <span class={`hfig ${cls}`}><img class="hfig-flat" src={heroImage(defId)} alt="" /></span>;
  const left = 53 - ((v.fx * BOX_PER_PX) / 200) * 100, top = 95 - ((v.fy * BOX_PER_PX) / 240) * 100;
  return (
    <span class={`hfig hfig-vec ${cls}`}>
      <span class="px-win vec-win" style={{ left: `${left.toFixed(2)}%`, top: `${top.toFixed(2)}%`, width: `${(((v.w * BOX_PER_PX) / 200) * 100).toFixed(2)}%`, aspectRatio: `${v.w} / ${v.h}` }}>
        <VectoImage id={art} src={v.big} live={live} />
      </span>
    </span>
  );
}
