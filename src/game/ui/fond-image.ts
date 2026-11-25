// L'image fixe d'un décor de combat (celui d'un clan, public/art/px/fonds/<clan>.webp) pour les cadres des menus :
// la tour, les donjons, les boss, le Colisée. En pixel art : le CSS l'agrandit sans flou (`image-rendering: pixelated`).
import type { Clan } from '../look';

const url = (clan: Clan) => `url(art/px/fonds/${clan}.webp)`;

/** Le style d'un cadre qui montre le décor en image de fond. */
export const sceneBg = (clan: Clan) => ({ backgroundImage: url(clan) });
/** La même image, passée par la variable `--scene` (cartes et en-tête des donjons). */
export const sceneVar = (clan: Clan) => ({ '--scene': url(clan) } as never);
