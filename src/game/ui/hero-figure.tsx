// Un héros en pied (le dessin entier, pas la vignette), posé dans une boîte 200 × 240 : ses pieds sont toujours au même
// endroit (53 % de la largeur, 95 % de la hauteur), quelle que soit la taille du dessin (arme levée, ailes, queue…),
// et tous les héros y ont la même stature (`norm`, mesurée par refonte-graphique/art-jeu.py).
// Sert à l'estrade de l'onglet Héros, au choix de la section et à la page d'un héros.
import { ART_META } from '../art-meta';
import { PIXEL } from '../pixel-meta';
import { artUrl, heroImage, isPixel, pixelUrl } from '../art';

// Pixel art : un pixel mesure `scale` unités au combat ; une unité du combat vaut 1 / 0,56 unité de la boîte (UNIT_PX).
const BOX_PER_UNIT = 1 / 0.56;

export function HeroFigure({ defId, class: cls = '' }: { defId: string; class?: string }) {
  if (isPixel(defId)) {
    // la planche animée (8 images) dans une fenêtre d'une case, pieds au même point que les autres héros
    const scale = PIXEL.chars[defId as keyof typeof PIXEL.chars][3];
    const u = scale * BOX_PER_UNIT; // un pixel du dessin, en unités de la boîte (200 × 240)
    const left = 53 - ((PIXEL.fx * u) / 200) * 100, top = 95 - ((PIXEL.fy * u) / 240) * 100;
    // chacun respire à son rythme : un décalage tiré de son nom
    let h = 0;
    for (const ch of defId) h = (h * 31 + ch.charCodeAt(0)) % 997;
    return (
      <span class={`hfig hfig-px ${cls}`}>
        <span class="px-win" style={{ left: `${left.toFixed(2)}%`, top: `${top.toFixed(2)}%`, width: `${(((PIXEL.cw * u) / 200) * 100).toFixed(2)}%`, aspectRatio: `${PIXEL.cw} / ${PIXEL.ch}` }}>
          <img src={pixelUrl(defId)} alt="" draggable={false} style={{ animationDelay: `-${((h % 8) * 0.14).toFixed(2)}s` }} />
        </span>
      </span>
    );
  }
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
