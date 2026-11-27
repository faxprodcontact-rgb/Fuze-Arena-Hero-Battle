// Petites pièces communes au calendrier de connexion et à la boutique (vague 3, 26/11) : le héros en pied posé sur
// ses pieds, et des étincelles qui scintillent (ou jaillissent au moment de prendre). Le style : sections/boutique.css.
import { FigImage, figMeta } from './hero-fig';

/**
 * Un héros en pied (son dessin, qui respire), les pieds posés à l'endroit (--x, --y) que la règle CSS lui donne :
 * u = taille d'un pixel du dessin en pixels d'écran.
 */
export function BqFigure({ id, u, class: cls = '' }: { id: string; u: number; class?: string }) {
  const m = figMeta(id);
  if (!m) return null;
  return (
    <span class={`bq-fig ${cls}`} aria-hidden="true" style={{ '--w': m.w, '--h': m.h, '--fx': m.fx, '--fy': m.fy, '--u': `${u}px` } as never}>
      <FigImage id={id} />
    </span>
  );
}

// Places des étincelles (en % de la boîte) : semées à la main, jamais en rayons réguliers.
const SPOTS: [number, number, number, number][] = [
  [78, 14, 1, 0], [16, 30, 0.7, 0.9], [86, 62, 0.8, 1.7], [30, 8, 0.6, 2.3], [8, 70, 0.9, 0.5], [60, 4, 0.55, 1.2],
  [94, 36, 0.65, 2.8], [44, 86, 0.6, 1.4],
];
// Pour le jaillissement : direction (x, y en px) de chaque étincelle, de longueurs toutes différentes.
const JETS: [number, number][] = [[46, -52], [-38, -40], [58, 6], [-54, 14], [18, -70], [-14, 44], [34, 40], [-62, -18]];

export function Sparkles({ n, burst }: { n: number; burst?: boolean }) {
  return (
    <span class={`bq-sparks${burst ? ' bq-jet' : ''}`} aria-hidden="true">
      {SPOTS.slice(0, n).map(([x, y, k, d], i) => (
        <i style={burst
          ? { '--dx': `${JETS[i]![0]}px`, '--dy': `${JETS[i]![1]}px`, '--k': k + 0.3, animationDelay: `${i * 0.025}s` } as never
          : { left: `${x}%`, top: `${y}%`, '--k': k, animationDelay: `-${d}s` } as never} />
      ))}
    </span>
  );
}
