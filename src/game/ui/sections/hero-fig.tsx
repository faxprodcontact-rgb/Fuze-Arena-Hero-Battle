// Le héros en pied pour la page d'un héros, la boutique et le calendrier : son dessin vectoriel (art/vecto/<id>.webp,
// vecto.ts), qui respire par le CSS (pieds fixes). (Les cases des héros prennent CardFigure de kit.tsx.)
import { heroArt } from '../../look';
import { vectoFig, type VectoFig } from '../../vecto';

/** Le dessin en pied d'un héros (mesures en pixels du dessin, à l'échelle du combat), ou rien s'il n'est pas dessiné. */
export function figMeta(id: string): VectoFig | undefined {
  // un monstre de clan devenu héros (Gribou…) a le dessin de son monstre : heroArt (bug du 26/11 : visage géant)
  return vectoFig(heroArt(id));
}

/** L'image en pied, qui respire (décalée selon le nom, pour que les héros ne respirent pas ensemble). */
export function FigImage({ id }: { id: string }) {
  const v = figMeta(id);
  if (!v) return null;
  let hash = 0;
  for (const ch of id) hash = (hash * 31 + ch.charCodeAt(0)) % 997;
  return (
    <img class="fig-breathe" src={v.big} alt="" draggable={false} style={{
      transformOrigin: `${((v.fx / v.w) * 100).toFixed(1)}% ${((v.fy / v.h) * 100).toFixed(1)}%`, animationDelay: `-${((hash % 34) / 10).toFixed(1)}s`,
    }} />
  );
}
