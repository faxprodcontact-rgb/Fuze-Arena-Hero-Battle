// ESSAI du 26/11 (demande du propriétaire : « Dans toutes les interfaces tu as mis un bleu foncé. Tu peux essayer avec un
// mix de gris et jaune comme les boutons ? Fais un test et montre-moi. ») : un second habillage, « pierre », à côté du
// « nuit » (le bleu foncé raisin, qui reste celui par défaut).
// - `?theme=pierre` l'allume (gardé dans le téléphone, clé `fuze-theme`), `?theme=nuit` revient au bleu foncé.
// - Il pose <html data-theme="pierre"> : le CSS de l'essai (theme-pierre.css, fabriqué par
//   refonte-graphique/ui-moderne/theme/pierre.ts à partir de TOUS les fichiers CSS) repeint chaque bleu foncé de
//   l'interface en pierre de basalte (le gris des boutons), et ajoute quelques filets d'or (theme-pierre-or.css).
// - Les fonds des menus dessinés par le code (backdrop*.tsx) et les pièces SVG communes passent par `stone()` /
//   `retintSvg()` : même conversion, faite une seule fois au dessin.
// La conversion ne touche QUE les bleus-violets peu saturés (le raisin des barres, fenêtres, textes) : les couleurs
// vives (gemmes violettes, éléments, raretés, or, vert, corail) ne bougent pas.

export type Theme = 'nuit' | 'pierre';
const KEY = 'fuze-theme';
let theme: Theme = 'nuit';

/** Lit l'adresse (?theme=pierre / ?theme=nuit) et la mémoire, pose data-theme sur <html> (avant le premier dessin). */
export function installTheme(): Theme {
  let t: string | null = null;
  try {
    const q = new URLSearchParams(location.search).get('theme');
    if (q === 'pierre' || q === 'nuit') localStorage.setItem(KEY, q);
    t = localStorage.getItem(KEY);
  } catch { /* sans mémoire : l'habillage par défaut */ }
  theme = t === 'pierre' ? 'pierre' : 'nuit';
  if (theme === 'pierre') document.documentElement.dataset.theme = 'pierre';
  else delete document.documentElement.dataset.theme;
  return theme;
}

export const isStone = () => theme === 'pierre';

// ---------- La conversion raisin → pierre ----------

/** La teinte de la pierre (celle du basalte des boutons, buttons.ts) et sa saturation la plus forte. */
const STONE_HUE = 246, STONE_SAT = 0.12;
/** Les clairs (fenêtres, cartes) deviennent crème, comme la pierre claire « ardoise » des boutons. */
const CREAM_HUE = 40, CREAM_SAT = 0.4;

function hsl(r: number, g: number, b: number) {
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn;
  if (!d) return [0, 0, l] as const;
  const s = d / (1 - Math.abs(2 * l - 1));
  const h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return [(h * 60 + 360) % 360, s, l] as const;
}
function rgb(h: number, s: number, l: number) {
  const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = l - c / 2;
  const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return [r + m, g + m, b + m].map((v) => Math.round(Math.max(0, Math.min(1, v)) * 255));
}
const h2 = (v: number) => v.toString(16).padStart(2, '0');

/** Jusqu'où va la conversion : `ui` = seulement le raisin peu saturé (les violets vifs des gemmes restent) ; `all` (fonds
 *  dessinés, où le violet n'est que l'ambiance de la nuit) = tous les bleus-violets. */
export type Reach = 'ui' | 'all';

/** Une couleur (#rgb, #rrggbb, #rrggbbaa) en pierre si c'est un bleu-violet raisin ; sinon telle quelle. */
export function stoneHex(hex: string, reach: Reach = 'ui'): string {
  let c = hex.slice(1);
  if (c.length === 3 || c.length === 4) c = [...c].map((x) => x + x).join('');
  if (c.length !== 6 && c.length !== 8) return hex;
  const r = parseInt(c.slice(0, 2), 16), g = parseInt(c.slice(2, 4), 16), b = parseInt(c.slice(4, 6), 16);
  const chroma = Math.max(r, g, b) - Math.min(r, g, b);
  const [h, s, l] = hsl(r / 255, g / 255, b / 255);
  // le raisin : bleu-violet (teinte 225 à 290) et le bleu nuit (210 à 225, sombre)
  if (chroma < 6 || h < 210 || h > 290) return hex;
  if (h < 225) {
    // le bleu nuit (boutique) : seulement les tons sombres, pas trop vifs (le bleu de l'eau reste)
    if (l >= 0.42 || s >= 0.75) return hex;
  } else if (reach === 'ui') {
    // les violets vifs (gemmes, invocation : saturation forte) restent, sauf les très sombres ; tout passe dans les fonds dessinés
    const raisin = s <= 0.66 && chroma <= 140;
    const night = l < 0.25 && s <= 0.85;
    if (!raisin && !night) return hex;
  }
  const light = l > 0.84;
  const out = light ? rgb(CREAM_HUE, Math.min(s, CREAM_SAT), l) : rgb(STONE_HUE, Math.min(s, STONE_SAT), l);
  return `#${out.map(h2).join('')}${c.slice(6)}`;
}

/** Toutes les couleurs d'un texte (SVG, CSS) en pierre. */
export function stoneText(text: string, reach: Reach = 'ui'): string {
  return text.replace(/#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b/g, (c) => stoneHex(c, reach));
}

/** Une couleur pour le dessin en cours : en pierre si l'essai est allumé. */
export const stone = (c: string) => (theme === 'pierre' ? stoneHex(c) : c);

const ATTRS = ['fill', 'stroke', 'stop-color', 'flood-color', 'color'];
/** Repeint une fois un dessin SVG déjà posé (fonds des menus) : seulement si l'essai est allumé. */
export function retintSvg(root: Element | null | undefined, reach: Reach = 'ui') {
  if (theme !== 'pierre' || !root) return;
  const all = [root, ...root.querySelectorAll('*')];
  for (const e of all) {
    for (const a of ATTRS) {
      const v = e.getAttribute(a);
      if (v && v.includes('#')) e.setAttribute(a, stoneText(v, reach));
    }
    const st = e.getAttribute('style');
    if (st && st.includes('#')) e.setAttribute('style', stoneText(st, reach));
  }
}
