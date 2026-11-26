// Le héros en pied pour la page d'un héros (sa bande de respiration art/hd/pied/<id>.webp, hd-figures.ts).
// (Les cases des héros prennent CardFigure de kit.tsx, fait par le Socle.)
import { figureUrl } from '../../art';
import { HD_FIG } from '../../hd-figures';

/** [largeur, hauteur d'une image, x et y des pieds, nombre d'images, durée d'une image (ms), haut de la tête au-dessus des pieds]. */
type Fig = [number, number, number, number, number, number, number];

/** Les mesures en pied d'un personnage HD, ou rien s'il n'a pas de dessin en pied. */
export function figMeta(id: string): Fig | undefined {
  return (HD_FIG.chars as Record<string, readonly number[] | undefined>)[id] as Fig | undefined;
}

/** La bande d'images qui défile (respiration), décalée selon le nom pour que les héros ne respirent pas ensemble. */
export function FigStrip({ id, n, ms }: { id: string; n: number; ms: number }) {
  let hash = 0;
  for (const ch of id) hash = (hash * 31 + ch.charCodeAt(0)) % 997;
  return (
    <img src={figureUrl(id)} alt="" draggable={false} style={{
      width: `${n * 100}%`, animation: `px-idle ${((n * ms) / 1000).toFixed(2)}s steps(${n}) infinite`, animationDelay: `-${(((hash % n) * ms) / 1000).toFixed(2)}s`,
    }} />
  );
}
