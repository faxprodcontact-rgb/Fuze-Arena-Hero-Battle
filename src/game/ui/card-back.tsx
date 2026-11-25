// Le dos des cartes du tirage, dessiné par le code (il remplace l'ancien picto peint) : une carte d'émail nuit dans un
// cadre d'or biseauté, un filet d'or intérieur aux coins cloutés, un ciel d'étoiles et de constellations, un grand cercle
// de signes en filigrane, et au centre le portail d'invocation en miniature (anneau d'or, ailes, flèche et gemmes, cœur
// tourbillonnant, étoile d'or). Le cœur du portail, ses gemmes et la lueur du centre ont la couleur de la rareté du héros
// caché dessous : c'est le dos qui « annonce » la carte avant qu'elle se retourne.
// Un reflet passe sur la carte, la lueur respire, le cœur tourne. `h` = 200 (carte 3 : 4) ou 180 (5 : 6, la grande carte seule).
import { spark } from './portal';

const INK = '#2f1b0c';

/**
 * Les signes des cercles en filigrane (dos des cartes, tirage) : inventés, et aucun ne ressemble à une lettre ou à un
 * chiffre (pas de « II », de « Λ » ni de « O », qu'on lirait en grand). Tracés au trait, bouts ronds ; un `h0.01` = un point.
 */
export const RUNES = [
  'M0 -4 L3 0 L0 4 L-3 0 Z M0 0 h0.01',
  'M0 -4 L3.5 3 H-3.5 Z M0 1 h0.01',
  'M-3 2 Q0 -5 3 2 M0 3.6 h0.01',
  'M-3 -2 Q0 2 3 -2 M-3 2 Q0 6 3 2',
  'M-4 0 Q0 -4 4 0 Q0 4 -4 0 Z M0 0 h0.01',
  'M0 -4 L2.5 -1.5 L0 1 L-2.5 -1.5 Z M0 1 V4',
  'M-3 -0.5 L0 -3.5 L3 -0.5 M-3 3 L0 0 L3 3',
  'M-3.5 1 Q0 -4 3.5 1 M-2 3.4 H2',
];

/** Quelques étoiles du ciel de la carte (x, y en fraction, rayon). */
const STARS: [number, number, number][] = [
  [0.22, 0.16, 1.2], [0.7, 0.13, 0.9], [0.83, 0.3, 1.1], [0.16, 0.38, 0.8], [0.3, 0.8, 1], [0.78, 0.74, 1.3], [0.62, 0.88, 0.8],
  [0.12, 0.62, 1], [0.88, 0.55, 0.8], [0.45, 0.1, 0.7], [0.55, 0.92, 1], [0.36, 0.27, 0.6], [0.66, 0.3, 0.6], [0.4, 0.71, 0.7],
];
/** Les constellations : des étoiles reliées (numéros dans STARS). */
const LINKS: [number, number][] = [[0, 11], [11, 9], [1, 12], [12, 2], [7, 3], [4, 13], [5, 6], [6, 10]];

export function CardBack({ color, uid, h = 200 }: { color: string; uid: string | number; h?: number }) {
  const w = 150, cx = w / 2, cy = h / 2, R = 26;
  const id = (k: string) => `cb${uid}-${k}`;
  const gold = `url(#${id('g')})`;
  /** Un clou d'or serti d'une gemme de la couleur de la rareté. */
  const stud = (x: number, y: number, r: number) => (
    <g>
      <circle cx={x} cy={y} r={r + 1.3} fill={INK} />
      <circle cx={x} cy={y} r={r} fill={gold} />
      <path d={`M${x} ${y - r * 0.62} L${x + r * 0.52} ${y} L${x} ${y + r * 0.62} L${x - r * 0.52} ${y} Z`} fill={color} stroke={INK} stroke-width="0.8" />
      <circle cx={x - r * 0.35} cy={y - r * 0.4} r={r * 0.22} fill="#fff" opacity="0.8" />
    </g>
  );
  /** Un coin du filet intérieur : l'équerre arrondie et sa volute. */
  const corner = (x: number, y: number, sx: number, sy: number) => (
    <g transform={`translate(${x} ${y}) scale(${sx} ${sy})`}>
      <path d="M0 18 V6 Q0 0 6 0 H18" fill="none" stroke={INK} stroke-width="4.2" stroke-linecap="round" />
      <path d="M0 18 V6 Q0 0 6 0 H18" fill="none" stroke={gold} stroke-width="2.2" stroke-linecap="round" />
      <path d="M6 15 Q6 6 15 6" fill="none" stroke="#ffe9a0" stroke-width="1.1" stroke-linecap="round" opacity="0.7" />
    </g>
  );
  /** Une aile du portail : trois plumes d'or qui partent d'un même point de l'anneau et montent en éventail. */
  const wing = (side: 1 | -1) => {
    const ra = (-20 * Math.PI) / 180, rx = cx + side * Math.cos(ra) * R, ry = cy + Math.sin(ra) * R;
    return (
      <g transform={`translate(${rx.toFixed(1)} ${ry.toFixed(1)}) scale(${side} 1)`}>
        {[[-62, 18, 5.2], [-16, 20, 5.6], [-38, 27, 7]].map(([deg, len, fw]) => (
          <g transform={`rotate(${deg})`}>
            <path d={`M0 ${-fw! / 2} Q${len! * 0.55} ${-fw! * 1.05} ${len!} ${-fw! * 0.12} Q${len! * 0.62} ${fw! * 0.55} 0 ${fw! / 2} Z`} fill={gold} stroke={INK} stroke-width="1.3" stroke-linejoin="round" />
            <path d={`M2 ${-fw! * 0.12} Q${len! * 0.55} ${-fw! * 0.5} ${len! * 0.88} ${-fw! * 0.14}`} fill="none" stroke="#fff" stroke-width="0.8" stroke-linecap="round" opacity="0.65" />
          </g>
        ))}
      </g>
    );
  };
  const top = cy - R;
  return (
    <svg class="card-back" viewBox={`0 0 ${w} ${h}`} aria-hidden="true">
      <defs>
        <linearGradient id={id('g')} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
        <linearGradient id={id('b')} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffeaa0" /><stop offset="0.4" stop-color="#f2b52e" /><stop offset="1" stop-color="#9c5a08" /></linearGradient>
        <radialGradient id={id('f')} cx="0.5" cy="0.45" r="0.72"><stop offset="0" stop-color="#4b37a8" /><stop offset="0.55" stop-color="#271a68" /><stop offset="1" stop-color="#110931" /></radialGradient>
        <radialGradient id={id('l')}><stop offset="0" stop-color={color} stop-opacity="0.85" /><stop offset="0.45" stop-color={color} stop-opacity="0.3" /><stop offset="1" stop-color={color} stop-opacity="0" /></radialGradient>
        <radialGradient id={id('e')} cx="0.45" cy="0.42" r="0.62"><stop offset="0" stop-color="#fff" /><stop offset="0.3" stop-color={color} /><stop offset="1" stop-color="#1a1052" /></radialGradient>
        <clipPath id={id('c')}><rect x="9.5" y="9.5" width={w - 19} height={h - 19} rx="7" /></clipPath>
        <clipPath id={id('d')}><circle cx={cx} cy={cy} r={R - 4.5} /></clipPath>
      </defs>
      {/* le cadre d'or biseauté (clair en haut à gauche, sombre en bas à droite), son filet sombre, l'émail de nuit */}
      <rect x="1" y="1" width={w - 2} height={h - 2} rx="13" fill={INK} />
      <rect x="3" y="3" width={w - 6} height={h - 6} rx="11.5" fill={`url(#${id('b')})`} />
      <path d={`M14 5.2 H${w - 14}`} stroke="#fffbe0" stroke-width="1.2" stroke-linecap="round" opacity="0.9" />
      <path d={`M5.2 16 V${h - 16}`} stroke="#fffbe0" stroke-width="1" stroke-linecap="round" opacity="0.55" />
      <path d={`M16 ${h - 5.2} H${w - 16}`} stroke="#6b3a05" stroke-width="1.2" stroke-linecap="round" opacity="0.7" />
      <rect x="8" y="8" width={w - 16} height={h - 16} rx="8" fill={INK} />
      <rect x="9.5" y="9.5" width={w - 19} height={h - 19} rx="7" fill={`url(#${id('f')})`} />
      <g clip-path={`url(#${id('c')})`}>
        {/* le ciel : constellations, étoiles, grand cercle de signes en filigrane */}
        {LINKS.map(([a, b]) => <path d={`M${STARS[a]![0] * w} ${STARS[a]![1] * h} L${STARS[b]![0] * w} ${STARS[b]![1] * h}`} stroke="#b9b0ff" stroke-width="0.6" opacity="0.35" />)}
        {STARS.map(([x, y, r], i) => <circle cx={x * w} cy={y * h} r={r} fill="#fff" opacity={0.45 + (i % 3) * 0.2} />)}
        <g opacity="0.3">
          <circle cx={cx} cy={cy} r="49" fill="none" stroke="#9d8fff" stroke-width="0.8" />
          <circle cx={cx} cy={cy} r="63" fill="none" stroke="#9d8fff" stroke-width="0.8" />
          {RUNES.concat(RUNES).map((d, i) => {
            const a = (i / 16) * Math.PI * 2 + 0.2;
            return <path d={d} transform={`translate(${(cx + Math.cos(a) * 56).toFixed(1)} ${(cy + Math.sin(a) * 56).toFixed(1)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(1.05)`} fill="none" stroke="#b3a8ff" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" />;
          })}
        </g>
        {/* la lueur du portail, de la couleur de la rareté */}
        <circle class="cb-glow" cx={cx} cy={cy} r="62" fill={`url(#${id('l')})`} />
        {/* le reflet qui passe */}
        <path class="cb-sheen" d={`M-40 0 H-10 L-60 ${h} H-90 Z`} fill="#fff" opacity="0.16" />
      </g>
      {/* le filet d'or intérieur, ses coins, un clou à chaque angle, un losange en haut et en bas */}
      <rect x="16" y="16" width={w - 32} height={h - 32} rx="5" fill="none" stroke={gold} stroke-width="1.2" opacity="0.75" />
      {corner(16, 16, 1, 1)}{corner(w - 16, 16, -1, 1)}{corner(16, h - 16, 1, -1)}{corner(w - 16, h - 16, -1, -1)}
      {stud(16, 16, 4.2)}{stud(w - 16, 16, 4.2)}{stud(16, h - 16, 4.2)}{stud(w - 16, h - 16, 4.2)}
      {[16, h - 16].map((y) => <path d={`M${cx} ${y - 4.5} L${cx + 4.5} ${y} L${cx} ${y + 4.5} L${cx - 4.5} ${y} Z`} fill={gold} stroke={INK} stroke-width="1.2" />)}
      {/* le portail en miniature : les ailes et la flèche derrière l'anneau */}
      {wing(1)}{wing(-1)}
      <path d={`M${cx - 8} ${top + 4} Q${cx - 7} ${top - 4} ${cx - 3.2} ${top - 8} L${cx} ${top - 23} L${cx + 3.2} ${top - 8} Q${cx + 7} ${top - 4} ${cx + 8} ${top + 4} Z`} fill={gold} stroke={INK} stroke-width="1.4" stroke-linejoin="round" />
      <path d={`M${cx} ${top - 23} L${cx + 3.2} ${top - 8} Q${cx + 7} ${top - 4} ${cx + 8} ${top + 4} H${cx + 2} Q${cx + 2} ${top - 6} ${cx} ${top - 23} Z`} fill="#fff" opacity="0.3" />
      <path d={`M${cx - 8} ${top - 1} Q${cx - 15} ${top - 2} ${cx - 16} ${top - 7} Q${cx - 12} ${top - 4} ${cx - 7} ${top - 5} Z M${cx + 8} ${top - 1} Q${cx + 15} ${top - 2} ${cx + 16} ${top - 7} Q${cx + 12} ${top - 4} ${cx + 7} ${top - 5} Z`} fill={gold} stroke={INK} stroke-width="1.1" stroke-linejoin="round" />
      {/* l'anneau d'or et son cœur de la couleur de la rareté, qui tourbillonne */}
      <circle cx={cx} cy={cy} r={R} fill="none" stroke={INK} stroke-width="8" />
      <circle cx={cx} cy={cy} r={R - 4} fill={`url(#${id('e')})`} />
      <g clip-path={`url(#${id('d')})`}>
        <g class="cb-spin" style={{ transformOrigin: `${cx}px ${cy}px` }}>
          {[0, 2.1, 4.2].map((k) => {
            const p = (a: number, r: number) => `${(cx + Math.cos(k + a) * r).toFixed(1)} ${(cy + Math.sin(k + a) * r).toFixed(1)}`;
            return <path d={`M${cx} ${cy} Q${p(0, 17)} ${p(1.4, 21)} Q${p(0.9, 11)} ${cx} ${cy} Z`} fill="#fff" opacity="0.45" />;
          })}
        </g>
      </g>
      <circle cx={cx} cy={cy} r={R} fill="none" stroke={gold} stroke-width="4.6" />
      <circle cx={cx} cy={cy} r={R - 2.6} fill="none" stroke="#7a4a08" stroke-width="0.8" opacity="0.8" />
      <path d={`M${cx - R * 0.72} ${cy - R * 0.72} A${R} ${R} 0 0 1 ${cx + R * 0.3} ${cy - R * 0.96}`} fill="none" stroke="#fffbe0" stroke-width="1.3" stroke-linecap="round" opacity="0.85" />
      {/* quatre gemmes serties sur l'anneau (en diagonale : la flèche est en haut, les ailes sur les côtés) */}
      {[45, 135, 225, 315].map((deg) => stud(cx + Math.cos((deg * Math.PI) / 180) * R, cy + Math.sin((deg * Math.PI) / 180) * R, 3.4))}
      {/* l'étoile d'or : quatre grandes branches, quatre petites, la gemme au cœur ; la gemme de la flèche */}
      <path d={spark(cx, cy, 9.5)} transform={`rotate(45 ${cx} ${cy})`} fill={gold} stroke={INK} stroke-width="1.1" stroke-linejoin="round" />
      <path d={spark(cx, cy, 14.5)} fill={gold} stroke={INK} stroke-width="1.2" stroke-linejoin="round" />
      <path d={`M${cx} ${cy - 5} L${cx + 4} ${cy} L${cx} ${cy + 5} L${cx - 4} ${cy} Z`} fill={color} stroke={INK} stroke-width="1.1" />
      <path d={`M${cx} ${cy - 5} L${cx + 4} ${cy} H${cx} Z`} fill="#fff" opacity="0.6" />
      <path d={`M${cx} ${top - 7} L${cx + 3} ${top - 2.5} L${cx} ${top + 2} L${cx - 3} ${top - 2.5} Z`} fill={color} stroke={INK} stroke-width="1" />
      {/* la goutte d'or sous l'anneau */}
      <path d={`M${cx - 5} ${cy + R + 2} Q${cx} ${cy + R + 6} ${cx} ${cy + R + 13} Q${cx} ${cy + R + 6} ${cx + 5} ${cy + R + 2} Z`} fill={gold} stroke={INK} stroke-width="1.1" stroke-linejoin="round" />
      {/* deux fleurons d'or, en haut et en bas */}
      {[[30, 1], [h - 30, -1]].map(([y, k]) => (
        <g transform={`translate(${cx} ${y}) scale(1 ${k})`}>
          <path d="M0 -8 L3.6 -1.8 L10 -3.6 L5.4 2.7 H-5.4 L-10 -3.6 L-3.6 -1.8 Z" fill={gold} stroke={INK} stroke-width="1.2" stroke-linejoin="round" />
          <circle cx="0" cy="-1.2" r="1.8" fill={color} stroke={INK} stroke-width="0.7" />
        </g>
      ))}
    </svg>
  );
}
