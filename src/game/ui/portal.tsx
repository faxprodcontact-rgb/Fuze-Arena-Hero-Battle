// Petites formes communes des dessins faits par le code : l'étincelle à quatre branches et les signes inventés.
// (L'ancien portail d'invocation est remplacé par sections/summon-gate.tsx, 26/11/2026.)

/** Une étoile à quatre branches (étincelle). */
export function spark(x: number, y: number, r: number): string {
  const q = r * 0.28;
  return `M${x} ${y - r} L${x + q} ${y - q} L${x + r} ${y} L${x + q} ${y + q} L${x} ${y + r} L${x - q} ${y + q} L${x - r} ${y} L${x - q} ${y - q} Z`;
}

/** Les signes : inventés (chevrons, arcs, points, losanges), jamais une forme de lettre. */
export const RUNES = [
  'M-5 5 L0 -5 L5 5', 'M0 -6 L5 0 L0 6 L-5 0 Z', 'M-5 3 Q0 -8 5 3', 'M-3 -6 V6 M3 -6 V6',
  'M0 -6 L5.500 5 H-5.500 Z', 'M-4.500 0 h0.010 M0 0 h0.010 M4.500 0 h0.010', 'M-5 -3 Q0 3 5 -3 M-5 3 Q0 9 5 3', 'M-4.500 0 A4.500 4.500 0 1 0 4.500 0 A4.500 4.500 0 1 0 -4.500 0',
  'M-5 -4 Q0 -9 5 -4 M0 -2 V6', 'M-5 5 L0 0 L-5 -5 M1 5 L6 0 L1 -5', 'M0 -6 V6 M-5 0 h0.010 M5 0 h0.010', 'M-5 -2 L0 -6 L5 -2 M-5 4 L0 0 L5 4',
];
