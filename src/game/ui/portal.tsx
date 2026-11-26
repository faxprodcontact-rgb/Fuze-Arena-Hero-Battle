// Petite forme commune des dessins faits par le code : l'étincelle à quatre branches (les fonds ont la leur, backdrop-kit.tsx).
// (L'ancien portail d'invocation est remplacé par sections/summon-gate.tsx, 26/11/2026.)

/** Une étoile à quatre branches (étincelle). */
export function spark(x: number, y: number, r: number): string {
  const q = r * 0.28;
  return `M${x} ${y - r} L${x + q} ${y - q} L${x + r} ${y} L${x + q} ${y + q} L${x} ${y + r} L${x - q} ${y + q} L${x - r} ${y} L${x - q} ${y - q} Z`;
}

