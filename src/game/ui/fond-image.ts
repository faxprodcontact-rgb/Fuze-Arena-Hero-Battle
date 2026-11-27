// L'image fixe d'un décor de combat (celui d'un clan) pour les cadres des menus : la tour, les donjons, les boss, le
// Colisée. Une copie réduite du fond vectoriel (public/art/vecto/fonds/<clan>-menu.webp, 590 × 1100, faite par
// refonte-graphique/ui-moderne/fonds/assemble_ts.py) : le fond du combat (×2) prendrait 4 fois plus de mémoire.
import type { Clan } from '../look';
import { artUrl } from '../art-url';

// adresse complète : dans une variable CSS, une adresse relative se lirait depuis la feuille de style (assets/)
const url = (clan: Clan) => `url(${new URL(artUrl(`art/vecto/fonds/${clan}-menu.webp`), document.baseURI).href})`;

/** Le style d'un cadre qui montre le décor en image de fond. */
export const sceneBg = (clan: Clan) => ({ backgroundImage: url(clan) });
/** La même image, passée par la variable `--scene` (cartes et en-tête des donjons). */
export const sceneVar = (clan: Clan) => ({ '--scene': url(clan) } as never);
