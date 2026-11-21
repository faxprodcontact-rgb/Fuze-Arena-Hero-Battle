// Un héros en pied (le dessin entier, pas la vignette), posé dans une boîte 200 × 240 : ses pieds sont toujours au même
// endroit (53 % de la largeur, 95 % de la hauteur), quelle que soit la taille du dessin (arme levée, ailes, queue…).
// Sert à l'estrade de l'onglet Héros et à la page d'un héros.
import { ART_META } from '../art-meta';
import { artUrl, heroImage } from '../art';

export function HeroFigure({ defId, class: cls = '' }: { defId: string; class?: string }) {
  const m = (ART_META.chars as unknown as Record<string, number[] | undefined>)[defId];
  if (!m) return <span class={`hfig ${cls}`}><img class="hfig-flat" src={heroImage(defId)} alt="" /></span>;
  const [ox, oy, w] = m as [number, number, number];
  return (
    <span class={`hfig ${cls}`}>
      <img src={artUrl(defId)} alt="" draggable={false} style={{ left: `${(ox / 2).toFixed(2)}%`, top: `${(oy / 2.4).toFixed(2)}%`, width: `${(w / 2).toFixed(2)}%` }} />
    </span>
  );
}
