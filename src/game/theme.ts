// Direction graphique de l'interface : trois essais au choix (réglages → outils de test), retenus sur le téléphone.
// Les couleurs elles-mêmes sont dans ui/style.css (attribut data-theme sur <html>).
export const THEMES = ['bois', 'royal', 'crepuscule'] as const;
export type Theme = (typeof THEMES)[number];
const KEY = 'fuze-theme';

export function getTheme(): Theme {
  let saved: string | null = null;
  try { saved = localStorage.getItem(KEY); } catch { /* stockage fermé : direction par défaut */ }
  // l'adresse peut imposer une direction (#theme=royal), pratique pour comparer
  const forced = /theme=(\w+)/.exec(location.hash)?.[1];
  const wanted = forced ?? saved;
  return (THEMES as readonly string[]).includes(wanted ?? '') ? (wanted as Theme) : 'bois';
}

export function setTheme(theme: Theme) {
  document.documentElement.dataset.theme = theme;
  try { localStorage.setItem(KEY, theme); } catch { /* tant pis : elle vaudra jusqu'à la fermeture */ }
}

/** Une couleur de la direction en cours (variable CSS `--nom`), en nombre pour Phaser. */
export function themeColor(name: string, fallback: number): number {
  const v = getComputedStyle(document.documentElement).getPropertyValue(`--${name}`).trim();
  return /^#[0-9a-f]{6}$/i.test(v) ? Number.parseInt(v.slice(1), 16) : fallback;
}
