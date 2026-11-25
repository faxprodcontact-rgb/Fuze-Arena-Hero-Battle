// Les couleurs de l'interface sont dans ui/style.css (variables en tête du fichier) ; Phaser les relit ici.

/** Une couleur de l'interface (variable CSS `--nom`), en nombre pour Phaser. */
export function themeColor(name: string, fallback: number): number {
  const v = getComputedStyle(document.documentElement).getPropertyValue(`--${name}`).trim();
  return /^#[0-9a-f]{6}$/i.test(v) ? Number.parseInt(v.slice(1), 16) : fallback;
}
