// Le décor de l'onglet Aventure, version travaillée : la route qui part vers le château.
// En haut (au-dessus des tuiles), le panorama : soleil et son cercle de runes, deux chaînes de sommets à facettes coiffés
// de neige, le château sur son rocher (tours rondes, remparts, cascade), les nuages en volume, la montgolfière, le moulin
// et son hameau. En dessous, la campagne : collines, rivière et pont, chemin, bosquets, campement au premier plan.
// Une seule lumière, venue de la droite (le soleil) : chaque volume a sa face claire à droite et son ombre à gauche.
// Deux dessins superposés : ce qui ne bouge pas (peint une fois) et ce qui bouge (nuages, fanions, ailes du moulin…).
import { RUNES } from './portal';

const W = 390, H = 844;


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
      <path d="M-3 2 L-2 -14 L2 -14 L3 2 Z" fill="#5e4026" />
      <circle cx="-9" cy="-20" r="11" fill={dark} /><circle cx="9" cy="-19" r="12" fill={dark} /><circle cx="0" cy="-30" r="13" fill={dark} />
      <circle cx="-6" cy="-23" r="9" fill={mid} /><circle cx="9" cy="-22" r="10" fill={mid} /><circle cx="2" cy="-32" r="10.500" fill={mid} />
      <circle cx="12" cy="-25" r="6" fill={light} /><circle cx="5" cy="-35" r="6.500" fill={light} /><circle cx="-4" cy="-27" r="4" fill={light} opacity="0.8" />
    </g>
  );
}

/** Un nuage en volume : dessous plat et bleuté, bosses rondes, creux ombrés. `lobes` = [x, y du centre, rayon]. */
function Cloud({ x, y, s, lobes, w, opacity = 1 }: { x: number; y: number; s: number; lobes: [number, number, number][]; w: number; opacity?: number }) {
  const shape = (dy: number, fill: string, grow = 0) => (
    <g fill={fill} transform={`translate(0 ${dy})`}>
      <rect x={-grow} y="-13" width={w + grow * 2} height="13" rx="6.500" />
      {lobes.map(([cx, cy, r]) => <circle cx={cx} cy={cy} r={r + grow} />)}
    </g>
  );
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} opacity={opacity}>
      {shape(0, '#a9c8e6')}
      {shape(-2.500, 'url(#ad-cloudg)')}
      {/* le haut des bosses accroche la lumière */}
      <g fill="#fff">{lobes.map(([cx, cy, r]) => <circle cx={cx + r * 0.12} cy={cy - 2.500 - r * 0.14} r={r * 0.8} />)}</g>
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

/** Le fond qui ne bouge pas : ciel et montagnes. */
function Back() {
  return (
    <>
      <defs>
        <linearGradient id="ad-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c56b0" /><stop offset="0.13" stop-color="#3684d8" /><stop offset="0.25" stop-color="#8fcaf0" /><stop offset="0.32" stop-color="#d9f0fb" /><stop offset="1" stop-color="#d9f0fb" /></linearGradient>
        <radialGradient id="ad-warm" cx="318" cy="128" r="170" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff6d6" stop-opacity="0.7" /><stop offset="0.4" stop-color="#ffefc0" stop-opacity="0.22" /><stop offset="1" stop-color="#ffefc0" stop-opacity="0" /></radialGradient>
        <linearGradient id="ad-mist" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="0.65" stop-color="#fff" stop-opacity="0.72" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></linearGradient>
        <linearGradient id="ad-stone" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a99a80" /><stop offset="0.3" stop-color="#d9cdb2" /><stop offset="0.72" stop-color="#fbf5e6" /><stop offset="1" stop-color="#e2d7bf" /></linearGradient>
        <linearGradient id="ad-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3ebd6" /><stop offset="1" stop-color="#cfc1a4" /></linearGradient>
        <linearGradient id="ad-roof" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8f342f" /><stop offset="0.35" stop-color="#c9503f" /><stop offset="0.7" stop-color="#ea7a5e" /><stop offset="1" stop-color="#c2503f" /></linearGradient>
        <linearGradient id="ad-rock" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5d7ea8" /><stop offset="1" stop-color="#86a6cd" /></linearGradient>
        <linearGradient id="ad-fall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" /><stop offset="0.8" stop-color="#dff3ff" /><stop offset="1" stop-color="#dff3ff" stop-opacity="0" /></linearGradient>
        <linearGradient id="ad-h1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b6e3a2" /><stop offset="1" stop-color="#86c98a" /></linearGradient>
        <linearGradient id="ad-h2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#93d490" /><stop offset="0.45" stop-color="#68b878" /></linearGradient>
        <linearGradient id="ad-h3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#74c17e" /><stop offset="0.45" stop-color="#4fa268" /></linearGradient>
        <linearGradient id="ad-h4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#57a86c" /><stop offset="0.55" stop-color="#357c52" /></linearGradient>
        <linearGradient id="ad-path" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d9bd80" /><stop offset="0.35" stop-color="#f1dfb0" /><stop offset="1" stop-color="#f9efcf" /></linearGradient>
        <linearGradient id="ad-river" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfe8fb" /><stop offset="1" stop-color="#5fb1e6" /></linearGradient>
        <radialGradient id="ad-shadow"><stop offset="0" stop-color="#1f5a3c" stop-opacity="0.32" /><stop offset="1" stop-color="#1f5a3c" stop-opacity="0" /></radialGradient>
      </defs>
      <rect width={W} height={H} fill="url(#ad-sky)" />
      <rect width={W} height="340" fill="url(#ad-warm)" />

      {/* la chaîne la plus lointaine : pâle, presque fondue dans le ciel */}
      <path d="M-10 272 L-10 226 L14 204 L30 216 L52 190 L74 214 L96 200 L126 232 L150 214 L176 236 L204 206 L226 226 L252 196 L282 228 L306 208 L330 230 L352 204 L378 224 L400 206 V272 Z" fill="#b4d0ee" />
      <path d="M52 190 L74 214 L60 226 L64 208 Z M252 196 L282 228 L262 232 L266 212 Z M352 204 L378 224 L360 232 L362 214 Z M204 206 L226 226 L212 236 Z M14 204 L30 216 L20 230 Z" fill="#fff" opacity="0.45" />
      <rect y="206" width={W} height="70" fill="url(#ad-mist)" opacity="0.75" />

      {/* les grands sommets */}
      <Peak a={[206, 124]} l={146} r={268} by={274} ridge={[[212, 146], [203, 168], [216, 196], [207, 226], [220, 274]]} snow={34} shade="#7c9fd0" lit="#c4d9f2" />
      <Peak a={[286, 164]} l={236} r={336} by={274} ridge={[[291, 184], [283, 206], [294, 236], [288, 274]]} snow={22} shade="#86a8d6" lit="#cbdef4" />
      <Peak a={[374, 150]} l={318} r={430} by={274} ridge={[[379, 172], [370, 196], [382, 228], [374, 274]]} snow={28} shade="#7c9fd0" lit="#c4d9f2" />
      <Peak a={[20, 168]} l={-40} r={84} by={274} ridge={[[25, 190], [17, 214], [28, 244], [22, 274]]} snow={24} shade="#86a8d6" lit="#cbdef4" />
      {/* contreforts : de petites arêtes à mi-pente */}
      <path d="M172 226 L186 204 L198 230 L190 274 H150 Z" fill="#7092c4" opacity="0.7" /><path d="M186 204 L198 230 L190 274 H206 L210 240 Z" fill="#a9c4e8" opacity="0.7" />
      <path d="M236 244 L250 220 L262 246 L258 274 H226 Z" fill="#7092c4" opacity="0.6" /><path d="M250 220 L262 246 L258 274 H276 L272 250 Z" fill="#b4cdec" opacity="0.7" />
      <rect y="222" width={W} height="62" fill="url(#ad-mist)" />
    </>
  );
}

/** Devant les nuages, sans mouvement : le rocher, le château, le moulin, la campagne. */
function Front() {
  return (
    <>
      {/* le rocher du château */}
      <path d="M14 276 L26 240 L42 228 L50 206 L66 198 L74 185 L144 185 L154 200 L166 208 L176 232 L190 248 L200 276 Z" fill="url(#ad-rock)" />
      <path d="M74 185 L66 198 L50 206 L42 228 L26 240 L14 276 H70 L80 236 L90 206 Z" fill="#48688f" opacity="0.75" />
      <path d="M144 185 L154 200 L166 208 L176 232 L190 248 L200 276 H154 L144 240 L130 208 Z" fill="#a9c3e2" opacity="0.8" />
      <path d="M90 206 L100 232 L94 276 M130 208 L124 236 L134 276 M110 196 L112 276" fill="none" stroke="#3f5d84" stroke-width="1" opacity="0.5" />
      <path d="M50 206 L66 198 L62 212 Z M154 200 L166 208 L156 216 Z M26 240 L42 228 L40 244 Z M176 232 L190 248 L176 250 Z" fill="#fff" opacity="0.2" />
      {/* l'herbe sur les replats */}
      <path d="M72 187 Q110 181 146 187 L143 191 Q110 187 75 191 Z" fill="#5fae62" />
      <path d="M72 187 Q110 181 146 187 L146 188.500 Q110 183 72 188.500 Z" fill="#9bd98a" />
      <Pine x={57} y={204} s={0.34} dark="#2f6d55" light="#4c9a6a" /><Pine x={160} y={207} s={0.3} dark="#2f6d55" light="#4c9a6a" /><Pine x={34} y={237} s={0.36} dark="#2f6d55" light="#4c9a6a" /><Pine x={182} y={246} s={0.32} dark="#2f6d55" light="#4c9a6a" />
      {/* la cascade sort d'une arche sous les remparts */}
      <path d="M106 199 Q111 192 116 199 V204 H106 Z" fill="#2f4668" />
      <path d="M107.500 200 H114.500 L117 268 H105 Z" fill="url(#ad-fall)" />

      {/* le château */}
      <g>
        {/* le donjon, au fond */}
        <Tower x={100} w={24} top={114} base={186} roof={34} slits={3} lit />
        {/* une échauguette accrochée à son angle */}
        <rect x="121" y="122" width="7" height="13" fill="url(#ad-stone)" /><path d="M119.500 122 L124.500 111 L129.500 122 Z" fill="url(#ad-roof)" /><path d="M121 135 L124.500 140 L128 135 Z" fill="#a99a80" />
        <Tower x={78} w={16} top={134} base={186} roof={25} slits={2} />
        <Tower x={130} w={15} top={142} base={186} roof={23} slits={2} lit />
        {/* le rempart et ses créneaux */}
        <path d="M70 186 V164 h4 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 h24 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 V186 Z" fill="url(#ad-wall)" />
        <path d="M70 186 V164 h4 v-4 h4 v4 h5 v-4 h4 v4 h5 v-4 h4 v4 h3 V186 Z" fill="#8f8068" opacity="0.38" />
        <path d="M70 166 H150" stroke="#8f8068" stroke-width="0.8" opacity="0.6" />
        <g fill="#4a3f36"><rect x="76" y="171" width="1.6" height="6" /><rect x="88" y="171" width="1.6" height="6" /><rect x="132" y="171" width="1.6" height="6" /><rect x="143" y="171" width="1.6" height="6" /></g>
        {/* quelques pierres, juste suggérées */}
        <g fill="none" stroke="#a99a80" stroke-width="0.6" opacity="0.7"><path d="M73 180 h5 M82 176 h4 M126 179 h5 M138 176 h4 M146 181 h3 M104 150 h4 M114 162 h4 M106 172 h3" /></g>
        {/* le châtelet et sa porte */}
        <path d="M99 186 V158 h3.500 v-3.500 h3.500 v3.500 h4 v-3.500 h3.500 v3.500 h4 v-3.500 h3.500 v3.500 V186 Z" fill="url(#ad-stone)" />
        <path d="M105 186 V174 Q105 167 111 167 Q117 167 117 174 V186 Z" fill="#3a2f28" />
        <path d="M105 186 V174 Q105 167 111 167 Q117 167 117 174 V186" fill="none" stroke="#8f8068" stroke-width="1.2" />
        <path d="M108 170 V186 M111 168 V186 M114 170 V186 M105.500 175 H116.500 M105.500 180 H116.500" stroke="#7a6a58" stroke-width="0.6" />
        {/* une petite tourelle à l'angle droit, en surplomb */}
        <Tower x={144} w={10} top={160} base={186} roof={15} slits={1} />
        <Tower x={66} w={10} top={160} base={186} roof={15} slits={1} />
        {/* les étendards du châtelet */}
        <path d="M100.500 160 h4 v9 l-2 -2 l-2 2 Z" fill="#d1493f" /><path d="M117.500 160 h4 v9 l-2 -2 l-2 2 Z" fill="#d1493f" />
        <path d="M100.500 160 h4 v1.500 h-4 Z M117.500 160 h4 v1.500 h-4 Z" fill="#ffd45c" />
        {/* les hampes des fanions */}
        <path d="M112 80 V66 M86 109 V99 M137.500 119 V110" stroke="#4a3f36" stroke-width="1.1" stroke-linecap="round" />
      </g>

      {/* la colline du moulin et son hameau */}
      <path d="M270 276 Q300 250 334 252 Q368 248 400 262 V276 Z" fill="#8fcf8c" />
      <path d="M270 276 Q300 250 334 252 Q368 248 400 262" fill="none" stroke="#c9eeb4" stroke-width="1.4" />
      <g>
        <path d="M296 266 h9 v-6 h-9 Z" fill="#f3ebd6" /><path d="M294.500 260 l6 -5 l6 5 Z" fill="#c9503f" /><rect x="299" y="262" width="2.4" height="4" fill="#4a3f36" />
        <path d="M309 268 h8 v-5 h-8 Z" fill="#e9dfc8" /><path d="M307.500 263 l5.500 -4.500 l5.500 4.500 Z" fill="#4a76b8" />
        <path d="M368 264 h9 v-6 h-9 Z" fill="#f3ebd6" /><path d="M366.500 258 l6 -5 l6 5 Z" fill="#c9503f" /><rect x="371" y="260" width="2.4" height="4" fill="#4a3f36" />
        <Oak x={322} y={266} s={0.3} /><Oak x={360} y={262} s={0.34} /><Oak x={384} y={266} s={0.3} />
        {/* le moulin (ses ailes tournent, dans le dessin animé) */}
        <path d="M335 262 L338 234 H350 L353 262 Z" fill="url(#ad-stone)" /><path d="M337 234 L344 224 L351 234 Z" fill="url(#ad-roof)" />
        <rect x="342.500" y="252" width="3.4" height="10" rx="1.6" fill="#4a3f36" /><rect x="343" y="241" width="2.4" height="3.600" fill="#4a3f36" />
      </g>

      {/* la brume du pied des montagnes, puis la forêt de l'horizon */}
      <rect y="236" width={W} height="52" fill="url(#ad-mist)" opacity="0.8" />
      <path d={hills(3, 274, 9, 26)} fill="#7fbf8f" opacity="0.9" />

      {/* la campagne : quatre plans de collines, de plus en plus proches */}
      <path d={hills(7, 286, 20, 120)} fill="url(#ad-h1)" />
      <path d={crest(7, 286, 20, 120)} fill="none" stroke="#dff5c8" stroke-width="1.6" opacity="0.9" />
      <Oak x={222} y={280} s={0.36} dark="#4f9a6a" mid="#68b47a" light="#93d28f" /><Oak x={238} y={283} s={0.3} dark="#4f9a6a" mid="#68b47a" light="#93d28f" /><Pine x={34} y={284} s={0.4} dark="#4f9a6a" light="#74bd84" /><Pine x={46} y={287} s={0.34} dark="#4f9a6a" light="#74bd84" />
      <ellipse cx="290" cy="330" rx="90" ry="20" fill="url(#ad-shadow)" /><ellipse cx="70" cy="350" rx="70" ry="16" fill="url(#ad-shadow)" />
      {/* la rivière : elle naît au pied de la cascade */}
      <path d="M103 276 C150 300 250 300 300 340 C350 380 396 392 402 396 L402 420 C380 412 330 404 288 366 C240 322 150 318 96 284 Z" fill="url(#ad-river)" />
      <path d="M130 292 C170 304 230 306 270 328 M300 356 C330 380 370 392 396 402" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="14 18" opacity="0.7" />
      <path d={hills(19, 384, 46, 150)} fill="url(#ad-h2)" />
      <path d={crest(19, 384, 46, 150)} fill="none" stroke="#c9eeb4" stroke-width="1.6" opacity="0.8" />
      <ellipse cx="120" cy="470" rx="100" ry="22" fill="url(#ad-shadow)" />
      <path d={hills(29, 528, 56, 170)} fill="url(#ad-h3)" />
      <path d={crest(29, 528, 56, 170)} fill="none" stroke="#a9e0a0" stroke-width="1.6" opacity="0.7" />
      {/* le chemin : du premier plan jusqu'au pied du rocher, plus clair du côté du soleil */}
      <path d="M146 844 C116 716 310 644 258 512 C222 418 150 380 186 286 L194 286 C166 378 250 414 292 512 C350 642 196 716 256 844 Z" fill="url(#ad-path)" />
      <path d="M146 844 C116 716 310 644 258 512 C222 418 150 380 186 286" fill="none" stroke="#b89858" stroke-width="1.4" opacity="0.6" />
      <g fill="#c9ac6c" opacity="0.7"><ellipse cx="236" cy="470" rx="5" ry="2" /><ellipse cx="270" cy="560" rx="6" ry="2.4" /><ellipse cx="240" cy="640" rx="7" ry="2.600" /><ellipse cx="204" cy="740" rx="8" ry="3" /><ellipse cx="200" cy="350" rx="3" ry="1.2" /></g>
      {/* le pont de pierre, là où le chemin passe la rivière */}
      <g transform="translate(196 318)">
        <path d="M-22 6 Q0 -12 22 6 L22 12 Q0 -4 -22 12 Z" fill="url(#ad-wall)" /><path d="M-22 6 Q0 -12 22 6" fill="none" stroke="#fbf5e6" stroke-width="1.6" /><path d="M-12 9 Q0 -1 12 9 L12 14 H-12 Z" fill="#3f7ab0" opacity="0.5" />
      </g>
      {/* bosquets */}
      <Oak x={52} y={410} s={0.8} /><Pine x={78} y={420} s={0.62} dark="#3a8656" light="#5cae70" /><Oak x={96} y={428} s={0.56} />
      <Oak x={344} y={458} s={0.9} /><Pine x={316} y={470} s={0.7} dark="#3a8656" light="#5cae70" /><Pine x={368} y={474} s={0.8} dark="#3a8656" light="#5cae70" />
      <Pine x={28} y={604} s={1.15} /><Oak x={62} y={630} s={1.05} /><Pine x={366} y={654} s={1.25} /><Oak x={332} y={676} s={1.1} /><Pine x={96} y={650} s={0.9} />
      <path d={hills(41, 744, 44, 190)} fill="url(#ad-h4)" />
      <path d={crest(41, 744, 44, 190)} fill="none" stroke="#8fd08f" stroke-width="1.6" opacity="0.6" />
      {/* premier plan : poteau indicateur, tente, buissons et fleurs */}
      <g transform="translate(332 770)">
        <rect x="-2.6" y="-48" width="5.2" height="50" rx="1" fill="#6b4a2a" /><rect x="0.6" y="-48" width="2" height="50" fill="#8a6238" />
        <path d="M-2 -46 H24 L31 -39.500 L24 -33 H-2 Z" fill="#d9a865" /><path d="M-2 -46 H24 L26 -44 H-2 Z" fill="#f0c98a" /><path d="M2 -29 H-22 L-29 -22.500 L-22 -16 H2 Z" fill="#b98545" /><path d="M2 -29 H-22 L-24 -27 H2 Z" fill="#d9a865" />
      </g>
      <g transform="translate(72 784)">
        <path d="M-32 0 L0 -42 L32 0 Z" fill="#d9ccae" /><path d="M0 -42 L32 0 H8 Z" fill="#f6efdc" /><path d="M-8 0 L0 -20 L8 0 Z" fill="#5e4026" /><path d="M0 -42 L-32 0 H-26 L0 -34 L26 0 H32 Z" fill="#b8433f" opacity="0.85" />
        <path d="M0 -42 v-14" stroke="#5e4026" stroke-width="1.6" />
      </g>
      <g>
        {[[12, 800, 22], [40, 812, 18], [372, 808, 24], [344, 818, 16], [200, 826, 20], [150, 820, 14], [262, 822, 16]].map(([x, y, r]) => (
          <g><circle cx={x} cy={y} r={r} fill="#235a3a" /><circle cx={x! + r! * 0.25} cy={y! - r! * 0.25} r={r! * 0.72} fill="#2f7448" /><circle cx={x! + r! * 0.45} cy={y! - r! * 0.5} r={r! * 0.36} fill="#4c9a5e" /></g>
        ))}
        {[[112, 792, '#fff'], [124, 800, '#ffd45c'], [288, 794, '#ff9fb5'], [300, 802, '#fff'], [176, 800, '#ffd45c'], [232, 804, '#ff9fb5']].map(([x, y, c]) => (
          <g><path d={`M${x} ${y} v7`} stroke="#2f7448" stroke-width="1.2" /><circle cx={x} cy={y} r="2.600" fill={c as string} /><circle cx={x} cy={y} r="1" fill="#f0a020" /></g>
        ))}
      </g>
    </>
  );
}

/** Entre les montagnes et le château, en mouvement : le soleil et les nuages. */
function Mid() {
  const sun = { x: 318, y: 128 };
  return (
    <>
      <defs>
        <radialGradient id="ad-sun"><stop offset="0" stop-color="#ffffff" /><stop offset="0.6" stop-color="#fffbe0" /><stop offset="1" stop-color="#ffe88f" /></radialGradient>
        <radialGradient id="ad-bloom"><stop offset="0" stop-color="#fff6cf" stop-opacity="0.9" /><stop offset="0.4" stop-color="#ffe9a0" stop-opacity="0.4" /><stop offset="1" stop-color="#ffe9a0" stop-opacity="0" /></radialGradient>
        <linearGradient id="ad-cloudg" x1="0" y1="-40" x2="0" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0.2" stop-color="#ffffff" /><stop offset="1" stop-color="#cfe3f5" /></linearGradient>
        <radialGradient id="ad-foamg"><stop offset="0" stop-color="#fff" stop-opacity="0.95" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></radialGradient>
        <linearGradient id="ad-balloon" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a8322e" /><stop offset="0.45" stop-color="#e0564e" /><stop offset="0.8" stop-color="#f58a72" /><stop offset="1" stop-color="#d94f47" /></linearGradient>
      </defs>
      {/* le soleil, son halo et son cercle de runes */}
      <circle class="bd-sun" cx={sun.x} cy={sun.y} r="82" fill="url(#ad-bloom)" />
      <g class="bd-ring" style={{ transformOrigin: `${sun.x}px ${sun.y}px`, animationDuration: '90s' }} fill="none" stroke="#fff" opacity="0.62">
        <circle cx={sun.x} cy={sun.y} r="52" stroke-width="1.4" /><circle cx={sun.x} cy={sun.y} r="55.500" stroke-width="0.7" opacity="0.7" />
        <circle cx={sun.x} cy={sun.y} r="39" stroke-width="1" stroke-dasharray="2 6" />
        {RUNES.map((d, i) => {
          const a = (i / RUNES.length) * Math.PI * 2;
          return <path d={d} stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(sun.x + Math.cos(a) * 45.500)} ${f(sun.y + Math.sin(a) * 45.500)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(0.4)`} />;
        })}
        {[0, 1, 2, 3].map((i) => { const a = (i / 4) * Math.PI * 2, x = sun.x + Math.cos(a) * 52, y = sun.y + Math.sin(a) * 52; return <path d={`M${f(x)} ${f(y - 3.2)} L${f(x + 3.2)} ${f(y)} L${f(x)} ${f(y + 3.2)} L${f(x - 3.2)} ${f(y)} Z`} fill="#fff" stroke="none" />; })}
      </g>
      <circle cx={sun.x} cy={sun.y} r="23" fill="url(#ad-sun)" />

      {/* les nuages : un grand banc derrière le château, d'autres qui passent */}
      <g class="bd-cloud bd-slow"><Cloud x={-46} y={170} s={1.1} lobes={CLOUD_C} w={126} /></g>
      <g class="bd-cloud"><Cloud x={150} y={104} s={0.6} lobes={CLOUD_B} w={62} opacity={0.96} /></g>
      <g class="bd-cloud"><Cloud x={268} y={198} s={0.5} lobes={CLOUD_B} w={62} opacity={0.9} /></g>
    </>
  );
}

/** Tout devant, en mouvement : nuages bas, fanions, cascade, ailes du moulin, montgolfière, oiseaux, feu de camp. */
function Top() {
  return (
    <>
      <g class="bd-cloud bd-slow"><Cloud x={226} y={236} s={0.62} lobes={CLOUD_A} w={90} opacity={0.96} /></g>

      {/* les fanions du château */}
      <path class="bd-flag" style={{ transformOrigin: '112px 70px' }} d="M112 66 q8 -1 15 3 q-7 4 -15 4.500 Z" fill="#e0564e" />
      <path class="bd-flag" style={{ transformOrigin: '86px 102px', animationDelay: '-0.6s' }} d="M86 99 q5 -0.500 10 2.500 q-5 3 -10 3.500 Z" fill="#ffd45c" />
      <path class="bd-flag" style={{ transformOrigin: '137.500px 113px', animationDelay: '-1.1s' }} d="M137.500 110 q5 -0.500 10 2.500 q-5 3 -10 3.500 Z" fill="#ffd45c" />
      {/* ses fenêtres allumées */}
      <g fill="#ffe9a8">
        <circle class="bd-star" cx="112" cy="129.500" r="1.5" /><circle class="bd-star" style={{ animationDelay: '-1.7s' }} cx="137.500" cy="157" r="1.3" />
      </g>
      {/* la cascade : l'eau file, l'écume bouillonne en bas */}
      <path class="ad-fall" d="M109.500 201 L108 266 M112.500 201 L114 266" fill="none" stroke="#fff" stroke-width="1.4" stroke-dasharray="5 7" stroke-linecap="round" opacity="0.9" />
      <ellipse class="ad-foam" cx="111" cy="270" rx="20" ry="9" fill="url(#ad-foamg)" />
      <g fill="#fff" opacity="0.9"><circle class="ad-foam" cx="105" cy="270" r="2.4" /><circle class="ad-foam" style={{ animationDelay: '-0.7s' }} cx="112" cy="272" r="3" /><circle class="ad-foam" style={{ animationDelay: '-1.3s' }} cx="118" cy="270" r="2.2" /></g>

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
        <g transform="translate(246 118)">
          <path d="M-6 21 L-3.500 27 M6 21 L3.500 27 M0 22 V27" stroke="#5e4026" stroke-width="0.8" />
          <path d="M-4.500 27 H4.500 L3.600 33 H-3.600 Z" fill="#9a6a38" /><path d="M-4.500 27 H4.500 L4.200 29 H-4.200 Z" fill="#c99556" />
          <path d="M0 -20 C15 -20 20 -8 17.500 2 C15.500 10 8.500 16 6 21 H-6 C-8.500 16 -15.500 10 -17.500 2 C-20 -8 -15 -20 0 -20 Z" fill="url(#ad-balloon)" />
          <path d="M-17.300 3 Q0 9 17.300 3 Q16.500 6 15 8.500 Q0 14 -15 8.500 Q-16.500 6 -17.300 3 Z" fill="#ffd45c" />
          <path d="M0 -2 l3 4 l-3 4 l-3 -4 Z" fill="#fff6c4" opacity="0.9" />
          <path d="M6 -17 C12 -13 14.500 -6 13 1" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity="0.38" />
          <path d="M-6 21 H6 L5 23.500 H-5 Z" fill="#8f342f" />
        </g>
      </g>
      {/* les oiseaux */}
      <g class="bd-birds" fill="none" stroke="#2f4a6a" stroke-width="1.5" stroke-linecap="round"><path d="M70 190 q5 -5 8 0 q3 -5 8 0" /><path d="M94 204 q4 -4 7 0 q3 -4 7 0" /><path d="M52 210 q3.500 -3.500 6 0 q2.500 -3.500 6 0" /></g>
      {/* le fanion et le feu du campement */}
      <path class="bd-flag" style={{ transformOrigin: '72px 730px' }} d="M72 728 q7 -1 13 3 q-6 4 -13 4.500 Z" fill="#ffd45c" />
      <g transform="translate(118 786)">
        <path d="M-9 2 L9 2 M-7 -1 L8 4 M7 -1 L-8 4" stroke="#5e4026" stroke-width="2.4" stroke-linecap="round" />
        <path class="ad-flame" d="M0 -18 C6 -10 8 -6 5 0 H-5 C-8 -6 -5 -10 0 -18 Z" fill="#ff9a3d" /><path class="ad-flame" style={{ animationDelay: '-0.3s' }} d="M0 -10 C3 -6 4 -3 2.500 0 H-2.500 C-4 -3 -2.500 -6 0 -10 Z" fill="#ffe27a" />
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

