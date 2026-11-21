// Le décor de l'onglet Aventure, version travaillée : la route qui part vers le château.
// En haut (au-dessus des tuiles), le panorama : soleil et son cercle de runes, deux chaînes de sommets à facettes coiffés
// de neige, le château sur son rocher (tours rondes, remparts, cascade), les nuages en volume, la montgolfière, le moulin
// et son hameau. En dessous, la campagne : collines, rivière et pont, chemin, bosquets, campement au premier plan.
// Une seule lumière, venue de la droite (le soleil) : chaque volume a sa face claire à droite et son ombre à gauche.
// Sous la grille des tuiles, la prairie reste calme (des collines seules) : un détail coupé par une tuile ferait du bruit.
// Quatre dessins superposés : le ciel ; le soleil et les nuages (ils bougent) ; les montagnes, le château et la campagne ;
// puis ce qui bouge devant (fanions, cascade, ailes du moulin, montgolfière, oiseaux, fumée).

const W = 390, H = 844;
/** Le château est dessiné puis réduit autour du milieu de son pied : ses fanions suivent le même réglage. */
const CASTLE = 'translate(110 186) scale(0.9) translate(-110 -186)';


function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}
const f = (n: number) => n.toFixed(1);

/** Une ligne de collines douces, fermée en bas. */
function hills(seed: number, base: number, amp: number, step: number): string {
  const r = rng(seed);
  let d = `M-10 ${H} L-10 ${base}`;
  for (let x = -10; x <= W + 10; x += step) d += ` Q${x + step * 0.5} ${f(base - amp * (0.4 + 0.6 * r()))} ${x + step} ${f(base - amp * 0.25 * r())}`;
  return `${d} L${W + 10} ${H} Z`;
}
/** La même ligne, sans la fermeture : pour le liseré clair sur la crête. */
function crest(seed: number, base: number, amp: number, step: number): string {
  const r = rng(seed);
  let d = `M-10 ${base}`;
  for (let x = -10; x <= W + 10; x += step) d += ` Q${x + step * 0.5} ${f(base - amp * (0.4 + 0.6 * r()))} ${x + step} ${f(base - amp * 0.25 * r())}`;
  return d;
}

/** Une lisière de forêt : des cimes de sapins de tailles variées, sur une ligne qui ondule. */
function forest(seed: number, base: number, hMin: number, hMax: number, wMin: number, wMax: number): string {
  const r = rng(seed);
  const at = (x: number) => base + Math.sin(x / 47 + seed) * 3.500;
  let x = -12, d = `M-12 ${base + 40} L-12 ${f(at(-12))}`;
  while (x < W + 12) {
    const w = wMin + r() * (wMax - wMin), h = hMin + r() * (hMax - hMin);
    d += ` L${f(x + w * 0.5)} ${f(at(x + w * 0.5) - h)} L${f(x + w)} ${f(at(x + w) - r() * 2)}`;
    x += w;
  }
  return `${d} L${W + 12} ${base + 40} Z`;
}

type Pt = [number, number];
/** Abscisse d'une ligne brisée à une hauteur donnée. */
function xAt(line: Pt[], y: number): number {
  for (let i = 1; i < line.length; i++) {
    const [x0, y0] = line[i - 1]!, [x1, y1] = line[i]!;
    if (y <= y1) return x0 + ((x1 - x0) * (y - y0)) / (y1 - y0 || 1);
  }
  return line[line.length - 1]![0];
}

/** Un sommet à deux faces (ombre à gauche, lumière à droite), séparées par une arête brisée, coiffé de neige. */
function Peak({ a, l, r, by, ridge, snow, shade, lit, snowShade = '#c9dcf2' }: { a: Pt; l: number; r: number; by: number; ridge: Pt[]; snow: number; shade: string; lit: string; snowShade?: string }) {
  const full: Pt[] = [a, ...ridge];
  const end = ridge[ridge.length - 1]!;
  const path = (pts: Pt[]) => pts.map((p, i) => `${i ? 'L' : 'M'}${f(p[0])} ${f(p[1])}`).join(' ');
  const sy = a[1] + snow;
  const xL = a[0] + ((l - a[0]) * snow) / (by - a[1]), xR = a[0] + ((r - a[0]) * snow) / (by - a[1]), xM = xAt(full, sy + 4);
  const above = full.filter((p) => p[1] < sy + 4);
  const dl = xM - xL, dr = xR - xM;
  return (
    <g>
      <path d={`${path([a, [l, by], end, ...[...ridge].reverse().slice(1)])} Z`} fill={shade} />
      <path d={`${path([a, ...ridge, [r, by]])} Z`} fill={lit} />
      <path d={`${path([a, [xL, sy], [xL + dl * 0.28, sy - 5], [xL + dl * 0.52, sy + 5], [xL + dl * 0.78, sy - 3], [xM, sy + 4], ...[...above].reverse().slice(0, -1)])} Z`} fill={snowShade} />
      <path d={`${path([...above, [xM, sy + 4], [xM + dr * 0.25, sy - 4], [xM + dr * 0.5, sy + 6], [xM + dr * 0.76, sy - 3], [xR, sy + 1]])} Z`} fill="#fff" />
    </g>
  );
}

/** Un sapin à quatre étages, face droite éclairée. */
function Pine({ x, y, s, dark = '#2a6a46', light = '#4c9a62' }: { x: number; y: number; s: number; dark?: string; light?: string }) {
  const tiers: [number, number, number][] = [[-58, 8, 14], [-49, 12, 17], [-38, 16, 19], [-25, 20, 22]];
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ellipse cx="-7" cy="2.500" rx="13" ry="3" fill="#123a2a" opacity="0.22" />
      <rect x="-2.6" y="-5" width="5.2" height="8" fill="#5e4026" />
      {tiers.map(([top, w, h]) => <path d={`M0 ${top} L${w} ${top + h} Q0 ${top + h + 4} ${-w} ${top + h} Z`} fill={dark} />)}
      {tiers.map(([top, w, h]) => <path d={`M0 ${top} L${w} ${top + h} Q${w * 0.5} ${top + h + 3} 1 ${top + h + 2} Z`} fill={light} />)}
    </g>
  );
}

/** Un arbre rond : tronc, feuillage en trois boules, reflets du côté du soleil. */
function Oak({ x, y, s, dark = '#2f7a4a', mid = '#46995c', light = '#74c07a' }: { x: number; y: number; s: number; dark?: string; mid?: string; light?: string }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ellipse cx="-8" cy="1.500" rx="15" ry="3.500" fill="#123a2a" opacity="0.22" />
      <path d="M-3 2 L-2 -14 L2 -14 L3 2 Z" fill="#5e4026" />
      <circle cx="-9" cy="-20" r="11" fill={dark} /><circle cx="9" cy="-19" r="12" fill={dark} /><circle cx="0" cy="-30" r="13" fill={dark} />
      <circle cx="-6" cy="-23" r="9" fill={mid} /><circle cx="9" cy="-22" r="10" fill={mid} /><circle cx="2" cy="-32" r="10.500" fill={mid} />
      <circle cx="12" cy="-25" r="6" fill={light} /><circle cx="5" cy="-35" r="6.500" fill={light} /><circle cx="-4" cy="-27" r="4" fill={light} opacity="0.8" />
    </g>
  );
}

/** Un nuage en volume : dessous plat et bleuté, bosses rondes, creux ombrés. `lobes` = [x, y du centre, rayon]. */
function Cloud({ x, y, s, lobes, w, opacity = 1 }: { x: number; y: number; s: number; lobes: [number, number, number][]; w: number; opacity?: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} opacity={opacity} fill="url(#ad-cloudg)">
      <rect x="0" y="-18" width={w} height="18" rx="9" />
      {lobes.map(([cx, cy, r]) => <circle cx={cx} cy={cy - 2} r={r} />)}
      {/* le haut des bosses accroche la lumière, du côté du soleil */}
      <g fill="#fff">{lobes.map(([cx, cy, r]) => <circle cx={cx + r * 0.14} cy={cy - 2 - r * 0.16} r={r * 0.78} />)}</g>
    </g>
  );
}
const CLOUD_A: [number, number, number][] = [[14, -14, 13], [34, -24, 19], [58, -18, 16], [76, -13, 11]];
const CLOUD_B: [number, number, number][] = [[12, -12, 11], [30, -20, 15], [50, -14, 12]];
const CLOUD_C: [number, number, number][] = [[16, -16, 15], [40, -28, 22], [68, -30, 20], [92, -20, 17], [112, -13, 11]];

/** Une tour ronde : fût ombré en cylindre, encorbellement, toit conique, fenêtres. */
function Tower({ x, w, top, base, roof, slits = 1, lit = false }: { x: number; w: number; top: number; base: number; roof: number; slits?: number; lit?: boolean }) {
  const cx = x + w / 2;
  return (
    <g>
      <rect x={x} y={top} width={w} height={base - top} fill="url(#ad-stone)" />
      {/* encorbellement et créneaux sous le toit */}
      <rect x={x - 1.6} y={top - 1} width={w + 3.2} height="5" rx="0.8" fill="url(#ad-stone)" />
      <rect x={x - 1.6} y={top + 3.2} width={w + 3.2} height="1.6" fill="#7d6d55" opacity="0.55" />
      <rect x={x} y={top + 4.8} width={w} height="3" fill="#000" opacity="0.1" />
      {/* toit */}
      <path d={`M${x - 3} ${top - 1} L${cx} ${top - roof} L${x + w + 3} ${top - 1} Q${cx} ${top + 2.5} ${x - 3} ${top - 1} Z`} fill="url(#ad-roof)" />
      <path d={`M${cx} ${top - roof} L${x + w + 3} ${top - 1} Q${cx + w * 0.3} ${top + 1} ${cx + 1} ${top + 1.4} Z`} fill="#fff" opacity="0.14" />
      <circle cx={cx} cy={top - roof} r="1.3" fill="#ffd45c" />
      {/* fenêtres */}
      {Array.from({ length: slits }, (_, i) => {
        const wy = top + 12 + i * 15;
        return lit && i === 0
          ? <path d={`M${cx - 1.8} ${wy + 6} V${wy + 1.6} Q${cx} ${wy - 1.4} ${cx + 1.8} ${wy + 1.6} V${wy + 6} Z`} fill="#ffd98a" stroke="#7d6d55" stroke-width="0.7" />
          : <path d={`M${cx - 1.2} ${wy + 5.500} V${wy + 1.2} Q${cx} ${wy - 0.8} ${cx + 1.2} ${wy + 1.2} V${wy + 5.500} Z`} fill="#4a3f36" />;
      })}
    </g>
  );
}

/** Des signes inventés pour le cercle du soleil (aucune lettre). */
const GLYPHS = ['M-3 3 L0 -3 L3 3', 'M0 -4 L3 0 L0 4 L-3 0 Z', 'M-3 2 Q0 -5 3 2', 'M-2 -4 V4 M2 -4 V4', 'M0 -4 L3.500 3 H-3.500 Z', 'M-3 0 h0.01 M0 0 h0.01 M3 0 h0.01', 'M-3 -2 Q0 2 3 -2 M-3 2 Q0 6 3 2', 'M-3 0 A3 3 0 1 0 3 0 A3 3 0 1 0 -3 0', 'M-3 3 L0 -3 L3 3', 'M0 -4 L3 0 L0 4 L-3 0 Z', 'M-3 2 Q0 -5 3 2', 'M-2 -4 V4 M2 -4 V4'];

/** Une corniche du rocher : dessus clair, dessous dans l'ombre. */
function Ledge({ x0, x1, y }: { x0: number; x1: number; y: number }) {
  const m = (x0 + x1) / 2;
  return (
    <g>
      <path d={`M${x0 + 3} ${y + 4} Q${m} ${y + 1.500} ${x1 - 2} ${y + 2.500} L${x1 - 6} ${y + 6.500} Q${m} ${y + 4.500} ${x0 + 8} ${y + 7.500} Z`} fill="#3f5288" opacity="0.8" />
      <path d={`M${x0} ${y + 1} Q${m} ${y - 4} ${x1} ${y - 1} L${x1 - 2} ${y + 3} Q${m} ${y + 1} ${x0 + 3} ${y + 4.500} Z`} fill="#a9bfe2" />
      <path d={`M${x0} ${y + 1} Q${m} ${y - 4} ${x1} ${y - 1}`} fill="none" stroke="#7fc27a" stroke-width="2.2" stroke-linecap="round" />
    </g>
  );
}

/** Une maison du hameau : mur à l'ombre à gauche, toit qui déborde, cheminée, porte. */
function House({ x, y, w, roof }: { x: number; y: number; w: number; roof: string }) {
  const h = w * 0.62;
  return (
    <g>
      <ellipse cx={x - 2} cy={y + 0.500} rx={w * 0.7} ry="1.8" fill="#123a2a" opacity="0.22" />
      <rect x={x + w * 0.62} y={y - h - w * 0.52} width="2" height="4.500" fill="#a99a80" />
      <rect x={x} y={y - h} width={w} height={h} fill="#f6efdc" /><rect x={x} y={y - h} width={w * 0.36} height={h} fill="#cdbfa3" />
      <path d={`M${x - 1.600} ${y - h + 0.600} L${x + w / 2} ${y - h - w * 0.5} L${x + w + 1.600} ${y - h + 0.600} Z`} fill={roof} />
      <path d={`M${x + w / 2} ${y - h - w * 0.5} L${x + w + 1.600} ${y - h + 0.600} H${x + w / 2 + 0.600} Z`} fill="#fff" opacity="0.2" />
      <rect x={x + w * 0.56} y={y - h * 0.62} width={w * 0.2} height={h * 0.62} fill="#5e4026" />
    </g>
  );
}

/** Le fond : le ciel, tout simplement. */
function Back() {
  return (
    <>
      <defs>
        <linearGradient id="ad-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c56b0" /><stop offset="0.13" stop-color="#3684d8" /><stop offset="0.25" stop-color="#8fcaf0" /><stop offset="0.32" stop-color="#d9f0fb" /><stop offset="1" stop-color="#d9f0fb" /></linearGradient>
      </defs>
      <rect width={W} height={H} fill="url(#ad-sky)" />
    </>
  );
}

/** Derrière les montagnes, en mouvement : le soleil, son cercle de signes, les nuages. */
function Mid() {
  const sun = { x: 318, y: 128 };
  return (
    <>
      <defs>
        <radialGradient id="ad-sun"><stop offset="0" stop-color="#fffef4" /><stop offset="0.5" stop-color="#fff7cf" /><stop offset="0.82" stop-color="#ffeeb0" /><stop offset="1" stop-color="#ffeeb0" stop-opacity="0" /></radialGradient>
        <radialGradient id="ad-bloom"><stop offset="0" stop-color="#fffdf0" stop-opacity="0.9" /><stop offset="0.3" stop-color="#ffffff" stop-opacity="0.42" /><stop offset="0.65" stop-color="#ffffff" stop-opacity="0.14" /><stop offset="1" stop-color="#ffffff" stop-opacity="0" /></radialGradient>
        <linearGradient id="ad-cloudg" x1="0" y1="-46" x2="0" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0.3" stop-color="#ffffff" /><stop offset="0.8" stop-color="#eaf3fb" /><stop offset="1" stop-color="#d3e4f4" /></linearGradient>
      </defs>
      <circle class="bd-sun" cx={sun.x} cy={sun.y} r="150" fill="url(#ad-bloom)" />
      <g class="bd-ring" style={{ transformOrigin: `${sun.x}px ${sun.y}px`, animationDuration: '90s' }} fill="none" stroke="#fff" opacity="0.7">
        <circle cx={sun.x} cy={sun.y} r="52" stroke-width="1.4" /><circle cx={sun.x} cy={sun.y} r="55.500" stroke-width="0.7" opacity="0.7" />
        <circle cx={sun.x} cy={sun.y} r="39" stroke-width="1" stroke-dasharray="1 7" stroke-linecap="round" />
        {GLYPHS.map((d, i) => {
          const a = (i / GLYPHS.length) * Math.PI * 2;
          return <path d={d} stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(sun.x + Math.cos(a) * 45.500)} ${f(sun.y + Math.sin(a) * 45.500)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(0.62)`} />;
        })}
        {[0, 1, 2, 3].map((i) => { const a = (i / 4) * Math.PI * 2 + Math.PI / 4, x = sun.x + Math.cos(a) * 52, y = sun.y + Math.sin(a) * 52; return <path d={`M${f(x)} ${f(y - 4)} L${f(x + 2)} ${f(y)} L${f(x)} ${f(y + 4)} L${f(x - 2)} ${f(y)} Z`} transform={`rotate(${(a * 180) / Math.PI + 90} ${f(x)} ${f(y)})`} fill="#fff" stroke="none" />; })}
      </g>
      <circle cx={sun.x} cy={sun.y} r="27" fill="url(#ad-sun)" />
      <g class="bd-cloud bd-slow"><Cloud x={-46} y={176} s={1.1} lobes={CLOUD_C} w={126} /></g>
      <g class="bd-cloud"><Cloud x={150} y={106} s={0.6} lobes={CLOUD_B} w={62} /></g>
    </>
  );
}

/** Sans mouvement : les montagnes, la forêt, le rocher et son château, le hameau, la prairie. */
function Front() {
  return (
    <>
      <defs>
        <linearGradient id="ad-mist" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="1" stop-color="#fff" stop-opacity="0.75" /></linearGradient>
        <linearGradient id="ad-stone" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9f93a0" /><stop offset="0.3" stop-color="#d6cab6" /><stop offset="0.72" stop-color="#fdf6e4" /><stop offset="1" stop-color="#ead9b8" /></linearGradient>
        <linearGradient id="ad-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6eeda" /><stop offset="1" stop-color="#d2c2a2" /></linearGradient>
        <linearGradient id="ad-roof" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a3040" /><stop offset="0.35" stop-color="#c9503f" /><stop offset="0.7" stop-color="#f08460" /><stop offset="1" stop-color="#c8543f" /></linearGradient>
        <linearGradient id="ad-rock" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5a6aa6" /><stop offset="0.55" stop-color="#7f97c6" /><stop offset="1" stop-color="#a9b9da" /></linearGradient>
        <linearGradient id="ad-fall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" /><stop offset="1" stop-color="#d6f0ff" /></linearGradient>
        <linearGradient id="ad-h1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b8e4a0" /><stop offset="1" stop-color="#84c888" /></linearGradient>
        <linearGradient id="ad-h2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#93d490" /><stop offset="0.45" stop-color="#68b878" /></linearGradient>
        <linearGradient id="ad-h3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#74c17e" /><stop offset="0.45" stop-color="#4fa268" /></linearGradient>
        <linearGradient id="ad-h4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#57a86c" /><stop offset="0.55" stop-color="#357c52" /></linearGradient>
        <linearGradient id="ad-river" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d6f1ff" /><stop offset="1" stop-color="#6fbcec" /></linearGradient>
      </defs>

      {/* la chaîne lointaine : pâle, d'une seule teinte, ses neiges à peine marquées */}
      <path d="M-10 290 L-10 226 L14 204 L30 216 L52 190 L74 214 L96 200 L126 232 L150 214 L176 236 L204 206 L226 226 L252 196 L282 228 L306 208 L330 230 L352 204 L378 224 L400 206 V290 Z" fill="#bcd3ee" />
      <path d="M52 190 L74 214 L62 222 L64 206 Z M252 196 L282 228 L264 230 L266 212 Z M352 204 L378 224 L362 230 L364 214 Z M204 206 L226 226 L212 232 Z M14 204 L30 216 L20 226 Z" fill="#eef4fc" />

      {/* les grands sommets : face de gauche bleu-violet, face de droite tiédie par le soleil */}
      <Peak a={[206, 124]} l={146} r={268} by={290} ridge={[[212, 146], [203, 168], [216, 196], [207, 226], [220, 290]]} snow={34} shade="#7c8fcc" lit="#d3ddf2" snowShade="#c6d4f0" />
      <Peak a={[286, 164]} l={236} r={336} by={290} ridge={[[291, 184], [283, 206], [294, 236], [288, 290]]} snow={22} shade="#8698d2" lit="#dbe3f4" snowShade="#c6d4f0" />
      <Peak a={[374, 150]} l={318} r={430} by={290} ridge={[[379, 172], [370, 196], [382, 228], [374, 290]]} snow={28} shade="#7c8fcc" lit="#d3ddf2" snowShade="#c6d4f0" />
      <Peak a={[20, 168]} l={-40} r={84} by={290} ridge={[[25, 190], [17, 214], [28, 244], [22, 290]]} snow={24} shade="#8698d2" lit="#dbe3f4" snowShade="#c6d4f0" />
      {/* les contreforts : plus proches, plus soutenus, sans transparence */}
      <path d="M150 290 L186 212 L210 250 L206 290 Z" fill="#6f84c2" /><path d="M186 212 L210 250 L206 290 H232 Z" fill="#b9c8e8" />
      <path d="M226 290 L252 228 L270 256 L266 290 Z" fill="#6f84c2" /><path d="M252 228 L270 256 L266 290 H288 Z" fill="#b9c8e8" />
      <path d="M322 290 L340 240 L354 262 L350 290 Z" fill="#6f84c2" /><path d="M340 240 L354 262 L350 290 H368 Z" fill="#b9c8e8" />
      {/* une brume légère, seulement au pied */}
      <rect y="232" width={W} height="52" fill="url(#ad-mist)" opacity="0.55" />
      {/* la forêt du fond : une lisière de cimes inégales */}
      <path d={forest(5, 272, 5, 13, 6, 12)} fill="#6aa7a6" />

      {/* le rocher du château */}
      <path d="M6 290 L20 242 L36 230 L44 208 L56 198 L58 185 L162 185 L164 198 L176 208 L186 232 L198 248 L212 290 Z" fill="url(#ad-rock)" />
      <path d="M58 185 L56 198 L44 208 L36 230 L20 242 L6 290 H64 L76 238 L86 206 Z" fill="#46549a" opacity="0.85" />
      <path d="M162 185 L164 198 L176 208 L186 232 L198 248 L212 290 H164 L152 240 L138 208 Z" fill="#c9d0e6" />
      <path d="M86 206 L98 236 L92 290 M138 208 L128 238 L138 290 M112 198 L116 244 L110 290" fill="none" stroke="#3d4c8a" stroke-width="1" opacity="0.45" />
      <path d="M162 185 L164 198 L176 208 L186 232 L198 248 L212 290" fill="none" stroke="#fff" stroke-width="1.2" opacity="0.6" />
      <Ledge x0={41} x1={64} y={207} /><Ledge x0={158} x1={180} y={207} /><Ledge x0={17} x1={42} y={241} /><Ledge x0={182} x1={203} y={248} />
      <Pine x={53} y={206} s={0.34} dark="#2f6d55" light="#4c9a6a" /><Pine x={169} y={206} s={0.3} dark="#2f6d55" light="#4c9a6a" /><Pine x={30} y={240} s={0.36} dark="#2f6d55" light="#4c9a6a" /><Pine x={192} y={247} s={0.32} dark="#2f6d55" light="#4c9a6a" />
      {/* le plateau : une vraie épaisseur d'herbe, et l'ombre du château dessus */}
      <path d="M54 186 Q110 178 166 186 L163 194 Q110 188 57 194 Z" fill="#4f9a58" />
      <path d="M54 186 Q110 178 166 186 L165 189 Q110 182 55 189 Z" fill="#9bd98a" />
      <ellipse cx="104" cy="186" rx="50" ry="3.500" fill="#1f4a34" opacity="0.3" />
      {/* la cascade : elle sort d'une arche sous le rempart, en rubans inégaux */}
      <path d="M73 201 Q80 191 87 201 V206 H73 Z" fill="#2c3a66" />
      <path d="M75 202 H85 L88 280 H72 Z" fill="url(#ad-fall)" /><path d="M86 208 h3 l2.500 70 h-4.500 Z" fill="#fff" opacity="0.7" /><path d="M71 214 h2.500 l-1.500 64 h-3 Z" fill="#fff" opacity="0.55" />

      {/* le château (réduit autour de son pied pour tenir sur le plateau) */}
      <g transform={CASTLE}>
        <Tower x={100} w={24} top={114} base={187} roof={34} slits={3} lit />
        <rect x="121" y="122" width="7" height="13" fill="url(#ad-stone)" /><path d="M119.500 122 L124.500 111 L129.500 122 Z" fill="url(#ad-roof)" /><path d="M121 135 L124.500 140 L128 135 Z" fill="#a99a80" />
        <Tower x={78} w={16} top={134} base={187} roof={25} slits={2} />
        <Tower x={130} w={15} top={142} base={187} roof={23} slits={2} lit />
        <path d="M70 187 V164 h4 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 h24 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 V187 Z" fill="url(#ad-wall)" />
        <path d="M70 187 V164 h4 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 h3 V187 Z" fill="#6f6890" opacity="0.32" />
        <path d="M70 166 H150" stroke="#8f8068" stroke-width="0.8" opacity="0.6" />
        <g fill="#4a3f36"><rect x="76" y="171" width="1.6" height="6" /><rect x="88" y="171" width="1.6" height="6" /><rect x="132" y="171" width="1.6" height="6" /><rect x="143" y="171" width="1.6" height="6" /></g>
        <g fill="none" stroke="#a99a80" stroke-width="0.6" opacity="0.7"><path d="M73 180 h5 M82 176 h4 M126 179 h5 M138 176 h4 M146 181 h3 M104 150 h4 M114 162 h4 M106 172 h3" /></g>
        <path d="M99 187 V158 h3.500 v-3.500 h3.500 v3.500 h4 v-3.500 h3.500 v3.500 h4 v-3.500 h3.500 v3.500 V187 Z" fill="url(#ad-stone)" />
        <path d="M105 187 V174 Q105 167 111 167 Q117 167 117 174 V187 Z" fill="#3a2f28" />
        <path d="M105 187 V174 Q105 167 111 167 Q117 167 117 174 V187" fill="none" stroke="#8f8068" stroke-width="1.2" />
        <path d="M108 170 V187 M111 168 V187 M114 170 V187 M105.500 175 H116.500 M105.500 180 H116.500" stroke="#7a6a58" stroke-width="0.6" />
        <Tower x={144} w={10} top={160} base={187} roof={15} slits={1} />
        <Tower x={66} w={10} top={160} base={187} roof={15} slits={1} />
        <path d="M100.500 160 h4 v9 l-2 -2 l-2 2 Z" fill="#d1493f" /><path d="M117.500 160 h4 v9 l-2 -2 l-2 2 Z" fill="#d1493f" />
        <path d="M100.500 160 h4 v1.500 h-4 Z M117.500 160 h4 v1.500 h-4 Z" fill="#ffd45c" />
        {/* le pied des murs, plus sombre, mord dans l'herbe */}
        <rect x="66" y="182" width="88" height="5" fill="#4a3f56" opacity="0.22" />
        <path d="M112 80 V66 M86 109 V99 M137.500 119 V110" stroke="#4a3f36" stroke-width="1.1" stroke-linecap="round" />
      </g>
      {/* des touffes d'herbe devant le pied des murs */}
      <g fill="#7fc87a">{[68, 79, 90, 104, 118, 129, 141, 151].map((x, i) => <path d={`M${x - 4} 188 Q${x - 2} ${182 - (i % 2)} ${x} 186 Q${x + 2} ${181 + (i % 2)} ${x + 4} 188 Z`} />)}</g>

      {/* la colline du moulin et son hameau */}
      <path d="M262 290 Q296 250 334 252 Q368 248 402 262 V290 Z" fill="#8fcf8c" />
      <path d="M262 290 Q296 250 334 252 Q368 248 402 262" fill="none" stroke="#d3f2bc" stroke-width="1.4" />
      <House x={294} y={267} w={10} roof="#c9503f" /><House x={308} y={270} w={8.500} roof="#4a76b8" /><House x={366} y={265} w={10} roof="#c9503f" /><House x={381} y={268} w={8} roof="#d99a3a" />
      <Oak x={323} y={268} s={0.3} /><Oak x={358} y={263} s={0.34} />
      <ellipse cx="338" cy="263" rx="12" ry="2.400" fill="#123a2a" opacity="0.24" />
      <path d="M335 263 L338 234 H350 L353 263 Z" fill="url(#ad-stone)" /><path d="M337 234 L344 224 L351 234 Z" fill="url(#ad-roof)" />
      <rect x="342.500" y="253" width="3.4" height="10" rx="1.6" fill="#4a3f36" /><rect x="343" y="241" width="2.4" height="3.600" fill="#4a3f36" />

      {/* la forêt proche : elle cache le pied du rocher, sauf là où tombe la cascade */}
      <path d={forest(11, 282, 6, 16, 7, 13)} fill="#4f9a7c" />
      <path d={forest(23, 288, 4, 12, 6, 11)} fill="#3f8a66" />
      {/* le bassin au pied de la cascade */}
      <ellipse cx="80" cy="282" rx="34" ry="8" fill="#3f7a5e" /><ellipse cx="80" cy="281" rx="31" ry="6.500" fill="url(#ad-river)" />
      <path d="M58 281 q8 -2 14 0 M92 284 q7 -1.500 12 0" fill="none" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity="0.8" />
      <path d="M48 284 l5 -5 l6 2 l2 4 Z M104 286 l4 -6 l6 1 l3 5 Z" fill="#8a94b8" /><path d="M53 279 l6 2 l2 4 h-4 Z M108 280 l6 1 l3 5 h-4 Z" fill="#c9d0e6" />

      {/* la prairie : des collines seules, calmes, sous la grille des tuiles */}
      <path d={hills(7, 300, 16, 130)} fill="url(#ad-h1)" />
      <path d={crest(7, 300, 16, 130)} fill="none" stroke="#e2f6cc" stroke-width="1.6" opacity="0.9" />
      <path d={hills(19, 400, 40, 160)} fill="url(#ad-h2)" />
      <path d={crest(19, 400, 40, 160)} fill="none" stroke="#c9eeb4" stroke-width="1.6" opacity="0.7" />
      <path d={hills(29, 540, 50, 180)} fill="url(#ad-h3)" />
      <path d={crest(29, 540, 50, 180)} fill="none" stroke="#a9e0a0" stroke-width="1.6" opacity="0.6" />
      <path d={hills(41, 700, 40, 200)} fill="url(#ad-h4)" />
      <path d={crest(41, 700, 40, 200)} fill="none" stroke="#8fd08f" stroke-width="1.6" opacity="0.55" />
      {/* tout en bas : des buissons à plusieurs bosses et des fleurs par petits groupes */}
      {[[20, 792, 1.2], [70, 800, 0.9], [330, 798, 1], [376, 790, 1.3], [200, 806, 1.1], [136, 808, 0.8], [268, 806, 0.85]].map(([x, y, k]) => (
        <g transform={`translate(${x} ${y}) scale(${k})`}>
          <path d="M-26 14 Q-30 -2 -16 -4 Q-14 -18 0 -14 Q10 -22 18 -10 Q32 -8 26 14 Z" fill="#256040" />
          <path d="M-12 14 Q-14 0 -4 -2 Q0 -12 10 -8 Q22 -8 24 4 Q28 10 22 14 Z" fill="#337a50" />
          <path d="M4 -6 Q12 -12 18 -5 Q12 -4 8 0 Z M-8 0 Q-2 -6 4 -1 Q-2 0 -5 4 Z" fill="#58a868" />
        </g>
      ))}
      {[[104, 792], [296, 794], [170, 800], [236, 802]].map(([x, y], i) => (
        <g>
          {[[0, 0, '#fff'], [7, 3, '#ffd45c'], [-6, 4, '#ff9fb5']].map(([dx, dy, c]) => <g><path d={`M${x! + (dx as number)} ${y! + (dy as number)} q${i % 2 ? 1 : -1} 4 0 8`} fill="none" stroke="#2f7448" stroke-width="1.1" /><circle cx={x! + (dx as number)} cy={y! + (dy as number)} r="2.400" fill={c as string} /><circle cx={x! + (dx as number)} cy={y! + (dy as number)} r="0.900" fill="#f0a020" /></g>)}
        </g>
      ))}
    </>
  );
}

/** Tout devant, en mouvement : nuages bas, fanions, cascade, ailes du moulin, fumée, montgolfière, oiseaux. */
function Top() {
  return (
    <>
      <defs>
        <radialGradient id="ad-foamg"><stop offset="0" stop-color="#fff" stop-opacity="0.95" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></radialGradient>
        <linearGradient id="ad-balloon" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a8322e" /><stop offset="0.45" stop-color="#e0564e" /><stop offset="0.8" stop-color="#f58a72" /><stop offset="1" stop-color="#d94f47" /></linearGradient>
      </defs>
      <g class="bd-cloud bd-slow"><Cloud x={226} y={226} s={0.5} lobes={CLOUD_A} w={90} opacity={0.96} /></g>

      {/* les fanions et les fenêtres allumées du château */}
      <g transform={CASTLE}>
        <path class="bd-flag" style={{ transformOrigin: '112px 70px' }} d="M112 66 q8 -1 15 3 q-7 4 -15 4.500 Z" fill="#e0564e" />
        <path class="bd-flag" style={{ transformOrigin: '86px 102px', animationDelay: '-0.6s' }} d="M86 99 q5 -0.500 10 2.500 q-5 3 -10 3.500 Z" fill="#ffd45c" />
        <path class="bd-flag" style={{ transformOrigin: '137.500px 113px', animationDelay: '-1.1s' }} d="M137.500 110 q5 -0.500 10 2.500 q-5 3 -10 3.500 Z" fill="#ffd45c" />
        <g fill="#fff3c4"><circle class="bd-star" cx="112" cy="129.500" r="1.5" /><circle class="bd-star" style={{ animationDelay: '-1.7s' }} cx="137.500" cy="157" r="1.3" /></g>
      </g>
      {/* la cascade : des filets d'eau inégaux qui filent, l'écume qui bouillonne dans le bassin */}
      <path class="ad-fall" d="M78 204 L77 278 M82.500 204 L84 278" fill="none" stroke="#bfe6fb" stroke-width="1.2" stroke-dasharray="11 5 4 9 16 6" stroke-linecap="round" opacity="0.9" />
      <ellipse class="ad-foam" cx="80" cy="279" rx="19" ry="7" fill="url(#ad-foamg)" />
      <g fill="#fff"><circle class="ad-foam" cx="73" cy="279" r="4" /><circle class="ad-foam" style={{ animationDelay: '-0.7s' }} cx="80" cy="281" r="5" /><circle class="ad-foam" style={{ animationDelay: '-1.3s' }} cx="88" cy="279" r="3.600" /></g>

      {/* la fumée d'une cheminée du hameau */}
      {[0, 1, 2].map((i) => <circle class="ad-smoke" style={{ animationDelay: `${-i * 1.5}s` }} cx="301" cy="254" r="1.700" fill="#fff" />)}
      {/* les ailes du moulin */}
      <g class="ad-sails" style={{ transformOrigin: '344px 234px' }}>
        {[0, 90, 180, 270].map((a) => (
          <g transform={`rotate(${a} 344 234)`}>
            <path d="M344 234 V214" stroke="#5e4026" stroke-width="1.2" stroke-linecap="round" />
            <path d="M345 231 H351 V215 H345 Z" fill="#f6efdc" stroke="#8f8068" stroke-width="0.6" /><path d="M345 226 H351 M345 220.500 H351 M348 231 V215" stroke="#8f8068" stroke-width="0.5" />
          </g>
        ))}
        <circle cx="344" cy="234" r="1.8" fill="#5e4026" />
      </g>

      {/* la montgolfière */}
      <g class="ad-balloon">
        <g transform="translate(232 112)">
          <path d="M-6 21 L-3.500 27 M6 21 L3.500 27 M0 22 V27" stroke="#5e4026" stroke-width="0.8" />
          <path d="M-4.500 27 H4.500 L3.600 33 H-3.600 Z" fill="#9a6a38" /><path d="M-4.500 27 H4.500 L4.200 29 H-4.200 Z" fill="#c99556" />
          <path d="M0 -20 C15 -20 20 -8 17.500 2 C15.500 10 8.500 16 6 21 H-6 C-8.500 16 -15.500 10 -17.500 2 C-20 -8 -15 -20 0 -20 Z" fill="url(#ad-balloon)" />
          <path d="M-17.300 3 Q0 9 17.300 3 Q16.500 6 15 8.500 Q0 14 -15 8.500 Q-16.500 6 -17.300 3 Z" fill="#ffd45c" />
          <path d="M0 -2 l3 4 l-3 4 l-3 -4 Z" fill="#fff6c4" opacity="0.9" />
          <path d="M6 -17 C12 -13 14.500 -6 13 1" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity="0.38" />
          <path d="M-6 21 H6 L5 23.500 H-5 Z" fill="#8f342f" />
        </g>
      </g>
      {/* un vol d'oiseaux, au loin */}
      <g class="bd-birds" fill="none" stroke="#2f4a6a" stroke-linecap="round">
        <path d="M150 150 q4 -4 6.500 0 q2.500 -4 6.500 0" stroke-width="1.1" /><path d="M166 160 q3 -3 5 0 q2 -3 5 0" stroke-width="0.9" /><path d="M138 162 q3 -3 5 0 q2 -3 5 0" stroke-width="0.9" />
        <path d="M156 170 q2.500 -2.500 4 0 q1.500 -2.500 4 0" stroke-width="0.8" /><path d="M176 148 q2.500 -2.500 4 0 q1.500 -2.500 4 0" stroke-width="0.8" />
      </g>
    </>
  );
}

export function AdventureBackdrop() {
  const box = { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'xMidYMin slice' };
  return (
    <>
      <svg {...box}><Back /></svg>
      <svg {...box}><Mid /></svg>
      <svg {...box}><Front /></svg>
      <svg {...box}><Top /></svg>
    </>
  );
}
