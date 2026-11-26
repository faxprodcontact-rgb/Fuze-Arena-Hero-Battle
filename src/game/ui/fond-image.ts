// L'image fixe d'un décor de combat (celui d'un clan, public/art/px/fonds/<clan>.webp) pour les cadres des menus :
// la tour, les donjons, les boss, le Colisée. En pixel art : le CSS l'agrandit sans flou (`image-rendering: pixelated`).
import type { Clan } from '../look';
import { artUrl } from '../art-url';

// adresse complète : dans une variable CSS, une adresse relative se lirait depuis la feuille de style (assets/)
const url = (clan: Clan) => `url(${new URL(artUrl(`art/px/fonds/${clan}.webp`), document.baseURI).href})`;

/** Le style d'un cadre qui montre le décor en image de fond. */
export const sceneBg = (clan: Clan) => ({ backgroundImage: url(clan) });
/** La même image, passée par la variable `--scene` (cartes et en-tête des donjons). */
export const sceneVar = (clan: Clan) => ({ '--scene': url(clan) } as never);
