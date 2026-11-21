// Un héros en pied (le dessin entier, pas la vignette), posé dans une boîte 200 × 240 : ses pieds sont toujours au même
// endroit (53 % de la largeur, 95 % de la hauteur), quelle que soit la taille du dessin (arme levée, ailes, queue…),
// et tous les héros y ont la même stature (`norm`, mesurée par refonte-graphique/art-jeu.py).
// Sert à l'estrade de l'onglet Héros, au choix de la section et à la page d'un héros.
import { ART_META } from '../art-meta';
import { artUrl, heroImage } from '../art';

export function HeroFigure({ defId, class: cls = '' }: { defId: string; class?: string }) {
  const m = (ART_META.chars as unknown as Record<string, number[] | undefined>)[defId];
  if (!m) return <span class={`hfig ${cls}`}><img class="hfig-flat" src={heroImage(defId)} alt="" /></span>;
  const [ox, oy, w] = m as [number, number, number];
  const k = m[5] || 1;
  // le dessin est agrandi ou réduit autour du point des pieds (106, 228 dans son repère)
  const left = 53 + ((ox - 106) / 2) * k, top = 95 + ((oy - 228) / 2.4) * k;
  return (
    <span class={`hfig ${cls}`}>
      <img src={artUrl(defId)} alt="" draggable={false} style={{ left: `${left.toFixed(2)}%`, top: `${top.toFixed(2)}%`, width: `${((w / 2) * k).toFixed(2)}%` }} />
    </span>
  );
}
