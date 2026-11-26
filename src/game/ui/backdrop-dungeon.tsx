// L'image de l'onglet Boss de la guilde (demande du propriétaire, 26/11/2026 : « une belle image du type que le boss est ;
// comme ça change à chaque fois, ce sera un autre élément affiché ») : la porte du donjon de l'élément du boss du jour de
// la guilde, dessinée par le code dans le style moderne (backdrop-kit.tsx : volumes, un seul contour adouci, lumière en
// haut à droite, ombres douces). Une image par élément :
// - feu : la porte de basalte d'un donjon volcanique, pointes et fissures de lave, deux braseros, volcans, braises qui montent ;
// - eau : la porte d'un temple englouti (fronton), corail, algues qui ondulent, méduses, taches de lumière, bulles qui montent ;
// - terre : une porte taillée dans la falaise moussue d'une caverne de cristaux, rochers qui flottent, cristaux qui brillent ;
// - vent : la porte d'une forteresse du ciel sur une mer de nuages, ailes de plumes, île qui flotte, tourbillons, plumes.
// La porte est à droite (la carte du nom et du temps se pose en haut à gauche) ; le sol est une bande plate d'un bord à
// l'autre (jamais de rond au sol) ; la jauge de vie se pose en bas, sur un sol calme. Mouvements : sections/guilde.css
// (gd-*) et sections/backdrops.css (bk-*), coupés si le téléphone demande moins de mouvements.
import type { ComponentChildren, JSX } from 'preact';
import type { Element } from '../../core/types';
import { Flag, Glow, INK, Mat, Soft, VGrad, Vol, cloud, f, rng, rr, spark } from './backdrop-kit';

/**
 * Le cadre du dessin : la porte y tient toujours en entier (preserveAspectRatio « xMidYMax meet »), le sol en bas, calé à droite
 * (sur un téléphone plus petit, la place en trop passe à gauche, sous la carte du nom) ; autour, le dessin continue (de X0 à X1, depuis Y0) pour remplir une scène plus large ou plus haute que le cadre.
 */
const VX = 20, VY = 4, DW = 392, DH = 200;
/** Le sol, et le milieu de la porte (à droite : la carte du nom se pose en haut à gauche). */
const G = 166, GX = 258;
const X0 = -120, X1 = DW + 120, Y0 = -120;

/** Une arche (x = gauche, y = haut, w = largeur, jusqu'en y + h). */
const arch = (x: number, y: number, w: number, h: number) =>
  `M${f(x)} ${f(y + h)} V${f(y + w / 2)} A${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(x + w)} ${f(y + w / 2)} V${f(y + h)} Z`;

/** Une ligne de bosses rondes (collines, rochers, nuages) fermée en bas, de X0 à X1. */
function bumps(seed: number, base: number, amp: number, step: number, bottom: number) {
  const r = rng(seed);
  let d = `M${X0} ${bottom} L${X0} ${f(base)}`;
  for (let x = X0; x < X1; x += step) d += ` Q${f(x + step * 0.5)} ${f(base - amp * (0.5 + 0.5 * r()))} ${f(x + step)} ${f(base - amp * 0.2 * r())}`;
  return `${d} L${X1 + step} ${bottom} Z`;
}

/** Un cône aux flancs creusés (volcan, stalagmite, flèche) : base en y, demi-largeur w, sommet arrondi en apex. */
const cone = (x: number, y: number, w: number, apex: number, round = 6) =>
  `M${f(x - w)} ${f(y)} Q${f(x - w * 0.3)} ${f(y - (y - apex) * 0.55)} ${f(x - round)} ${f(apex)} Q${f(x)} ${f(apex - round * 0.4)} ${f(x + round)} ${f(apex)} Q${f(x + w * 0.3)} ${f(y - (y - apex) * 0.55)} ${f(x + w)} ${f(y)} Z`;

/** Une flamme (signe du feu, flamme des braseros) : pied en (x, y), hauteur h. */
const flame = (x: number, y: number, h: number) => {
  const w = h * 0.42;
  return `M${f(x)} ${f(y - h)} Q${f(x + w * 0.5)} ${f(y - h * 0.62)} ${f(x + w)} ${f(y - h * 0.32)} Q${f(x + w * 1.1)} ${f(y)} ${f(x)} ${f(y)} Q${f(x - w * 1.1)} ${f(y)} ${f(x - w)} ${f(y - h * 0.34)} Q${f(x - w * 0.7)} ${f(y - h * 0.55)} ${f(x - w * 0.3)} ${f(y - h * 0.5)} Q${f(x - w * 0.2)} ${f(y - h * 0.8)} ${f(x)} ${f(y - h)} Z`;
};
/** Une goutte (signe de l'eau) : pointe en haut, pied en (x, y). */
const drop = (x: number, y: number, h: number) => {
  const w = h * 0.36;
  return `M${f(x)} ${f(y - h)} Q${f(x + w * 0.4)} ${f(y - h * 0.62)} ${f(x + w)} ${f(y - w * 1.1)} A${f(w)} ${f(w)} 0 0 1 ${f(x - w)} ${f(y - w * 1.1)} Q${f(x - w * 0.4)} ${f(y - h * 0.62)} ${f(x)} ${f(y - h)} Z`;
};
/** Un cristal (prisme à pointe) : pied en (x, y), hauteur h, largeur w, penché de `lean`. */
const prism = (x: number, y: number, h: number, w: number, lean = 0) =>
  `M${f(x - w / 2)} ${f(y)} L${f(x - w / 2 + lean)} ${f(y - h + w * 0.55)} L${f(x + lean)} ${f(y - h)} L${f(x + w / 2 + lean)} ${f(y - h + w * 0.55)} L${f(x + w / 2)} ${f(y)} Z`;
/** Une plume (plumes qui volent) : centrée en (x, y), longueur l. */
const feather = (x: number, y: number, l: number) =>
  `M${f(x - l / 2)} ${f(y)} Q${f(x - l * 0.1)} ${f(y - l * 0.3)} ${f(x + l / 2)} ${f(y - l * 0.06)} Q${f(x)} ${f(y + l * 0.2)} ${f(x - l / 2)} ${f(y)} Z`;
/** Un tourbillon de vent : une courbe qui s'enroule au bout (trait, sans remplissage). */
const swirl = (x: number, y: number, w: number, k = 1) =>
  `M${f(x)} ${f(y)} C${f(x + w * 0.35)} ${f(y - 10 * k)} ${f(x + w * 0.65)} ${f(y + 8 * k)} ${f(x + w * 0.86)} ${f(y - 2 * k)} C${f(x + w * 1.02)} ${f(y - 9 * k)} ${f(x + w * 0.96)} ${f(y - 20 * k)} ${f(x + w * 0.85)} ${f(y - 17 * k)} C${f(x + w * 0.77)} ${f(y - 15 * k)} ${f(x + w * 0.79)} ${f(y - 8 * k)} ${f(x + w * 0.87)} ${f(y - 9 * k)}`;

/** La porte commune : deux piliers, l'arche percée, la clé de voûte et son signe, une marche. `stone`, `trim` : les matières. */
function Gate({ p, stone, trim, sign, children, over, back }: {
  p: string; stone: string; trim: string; sign: ComponentChildren;
  /** derrière l'arche (cornes, coquille, rochers…) */ back?: ComponentChildren;
  /** dessiné dans la pierre de l'arche (fissures, mousse…) */ children?: ComponentChildren;
  /** posé devant l'arche (corail, cristaux…) */ over?: ComponentChildren;
}) {
  const ox = GX - 60, top = 58, w = 120;
  const ix = GX - 32, itop = 86, iw = 64;
  return (
    <g>
      {/* la lumière qui sort de la porte, derrière elle */}
      <circle class="bk-breathe" cx={GX} cy={G - 34} r="92" fill={`url(#${p}-halo)`} />
      {back}
      {/* l'ouverture, puis l'arche percée et ses piliers */}
      <path d={arch(ix, itop, iw, G - itop)} fill={`url(#${p}-door)`} />
      <circle class="bk-glow" cx={GX} cy={G - 18} r="34" fill={`url(#${p}-core)`} />
      <Vol p={p} d={`${arch(ox, top, w, G - top)} ${arch(ix, itop, iw, G - itop + 2)}`} ring fill={`url(#${p}-${stone})`} depth={7} shade={0.38}>{children}</Vol>
      {/* le bord intérieur de l'arche, dans l'ombre (la porte est profonde) */}
      <path d={arch(ix, itop, iw, G - itop)} fill="none" stroke="#1a0b33" stroke-opacity="0.45" stroke-width="5" transform="translate(2 1)" />
      {[-1, 1].map((sx) => (
        <g>
          <Vol p={p} d={rr(GX + sx * 66 - 11, 84, 22, G - 84, 4)} fill={`url(#${p}-${stone})`} depth={5} shade={0.34} />
          <Vol p={p} d={rr(GX + sx * 66 - 15, 76, 30, 11, 4)} fill={`url(#${p}-${trim})`} line={1.3} depth={2} rim={0.6} />
          <Vol p={p} d={rr(GX + sx * 66 - 14, G - 10, 28, 10, 3)} fill={`url(#${p}-${trim})`} line={1.3} depth={2} />
        </g>
      ))}
      {/* la clé de voûte et le signe de l'élément */}
      <Vol p={p} d={`M${GX} ${top - 16} Q${GX + 3} ${top - 16} ${GX + 18} ${top + 2} Q${GX + 20} ${top + 5} ${GX + 18} ${top + 8} L${GX + 3} ${top + 24} Q${GX} ${top + 27} ${GX - 3} ${top + 24} L${GX - 18} ${top + 8} Q${GX - 20} ${top + 5} ${GX - 18} ${top + 2} Q${GX - 3} ${top - 16} ${GX} ${top - 16} Z`} fill={`url(#${p}-${trim})`} line={1.5} depth={4} rim={0.65} />
      {sign}
      {/* deux marches, plates, d'un pilier à l'autre */}
      <Vol p={p} d={rr(GX - 52, G - 6, 104, 8, 3)} fill={`url(#${p}-${trim})`} line={1.2} depth={2} shade={0.3} />
      {over}
    </g>
  );
}

/** Le sol : une bande plate d'un bord à l'autre, son liseré de lumière. */
function Ground({ p, extra }: { p: string; extra?: ComponentChildren }) {
  return (
    <g>
      <rect x={X0} y={G} width={X1 - X0} height={DH - G + 20} fill={`url(#${p}-ground)`} />
      <rect x={X0} y={G} width={X1 - X0} height="1.5" fill="#fff6cf" opacity="0.35" />
      {extra}
    </g>
  );
}

/** Des points qui montent (braises, bulles, poussières) : classe d'animation `cls`, dans une zone. */
function Rising({ seed, n, x0, x1, y0, y1, cls, children }: {
  seed: number; n: number; x0: number; x1: number; y0: number; y1: number; cls: string;
  children: (x: number, y: number, s: number, i: number) => ComponentChildren;
}) {
  const r = rng(seed);
  return (
    <g>
      {Array.from({ length: n }, (_, i) => {
        const x = x0 + r() * (x1 - x0), y = y0 + r() * (y1 - y0), s = 0.8 + r() * 1.4;
        return <g class={cls} style={{ animationDelay: `${f(-r() * 9)}s`, animationDuration: `${f(6 + r() * 5)}s` }}>{children(x, y, s, i)}</g>;
      })}
    </g>
  );
}

// ---------- Feu : la porte du donjon volcanique ----------
function Fire() {
  const P = 'gdf';
  const cracks = [
    `M${GX - 54} 122 Q${GX - 46} 112 ${GX - 48} 100 Q${GX - 44} 92 ${GX - 47} 82`,
    `M${GX + 46} 152 Q${GX + 52} 138 ${GX + 47} 126 Q${GX + 50} 116 ${GX + 55} 110`,
    `M${GX - 20} 70 Q${GX - 27} 76 ${GX - 37} 74`,
    `M${GX + 22} 66 Q${GX + 30} 72 ${GX + 38} 70 Q${GX + 42} 74 ${GX + 46} 82`,
  ];
  /** une pointe de basalte posée sur l'arche, à la pointe arrondie (dx = écart au milieu, h = hauteur) */
  const spike = (dx: number, h: number) => {
    const x = GX + dx, base = 60 + Math.abs(dx) * 0.5, lean = dx * 0.25;
    return `M${f(x - 9)} ${f(base + 8)} Q${f(x - 5 + lean * 0.5)} ${f(base - h * 0.5)} ${f(x + lean - 2)} ${f(base - h)} Q${f(x + lean)} ${f(base - h - 2)} ${f(x + lean + 2)} ${f(base - h)} Q${f(x + 5 + lean * 0.5)} ${f(base - h * 0.5)} ${f(x + 9)} ${f(base + 8)} Z`;
  };
  /** un rocher posé, à la base plate */
  const rock = (x: number, w: number, h: number) =>
    `M${f(x - w)} ${G + 1} Q${f(x - w)} ${f(G - h * 0.7)} ${f(x - w * 0.3)} ${f(G - h)} Q${f(x + w * 0.5)} ${f(G - h * 1.05)} ${f(x + w)} ${f(G - h * 0.2)} L${f(x + w)} ${G + 1} Z`;
  return (
    <>
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={VY - 20} y2={G} stops={[[0, '#1a0824'], [0.4, '#42123a'], [0.75, '#9a2c30'], [1, '#f07a34']]} />
        <VGrad id={`${P}-ground`} y1={G} y2={DH} stops={[[0, '#4a2632'], [0.35, '#2e1628'], [1, '#1a0c1e']]} />
        <Glow id={`${P}-halo`} c="#ff8a3a" a={0.75} />
        <Glow id={`${P}-core`} c="#fff0a0" a={0.9} />
        <Glow id={`${P}-crater`} c="#ffb04a" a={0.95} />
        <VGrad id={`${P}-door`} stops={[[0, '#5a1424'], [0.55, '#ff6a2a'], [1, '#ffe48a']]} />
        <Mat id={`${P}-basalt`} c="#5a4060" k={0.8} />
        <Mat id={`${P}-trim`} c="#7a5a72" k={0.8} />
        <Mat id={`${P}-far`} c="#56203e" k={0.5} />
        <Mat id={`${P}-far2`} c="#3e1834" k={0.5} />
        <Mat id={`${P}-cliff`} c="#341830" k={0.6} />
        <Mat id={`${P}-rock`} c="#4a3048" k={0.7} />
        <VGrad id={`${P}-flame`} stops={[[0, '#fff3b0'], [0.45, '#ffb43a'], [1, '#f0502a']]} />
        <VGrad id={`${P}-lava`} stops={[[0, '#ffe08a'], [0.5, '#ff8a2a'], [1, '#d8401e']]} />
        <VGrad id={`${P}-smoke`} stops={[[0, '#7a3a5a'], [1, '#3a1a3a']]} />
      </defs>
      <rect x={X0} y={Y0} width={X1 - X0} height={G - Y0 + 4} fill={`url(#${P}-sky)`} />
      {/* le grand volcan derrière la porte (en haut à droite, d'où vient la lumière) : son cratère embrasé, sa coulée */}
      <circle class="bk-breathe" cx="372" cy="34" r="74" fill={`url(#${P}-crater)`} />
      <g class="bk-cloud bk-slow" opacity="0.85"><Vol p={P} d={cloud(300, 26, 120, 6)} fill={`url(#${P}-smoke)`} line={0} depth={5} shade={0.2} rim={0.35} /></g>
      <Vol p={P} d={cone(372, G - 14, 120, 44, 18)} fill={`url(#${P}-far)`} line={1.2} inkA={0.4} depth={7} shade={0.25} rim={0.4}>
        <path class="gd-lava" d="M366 48 Q354 66 362 86 Q368 102 354 122" fill="none" stroke={`url(#${P}-lava)`} stroke-width="4" stroke-linecap="round" />
        <path class="gd-lava" d="M380 50 Q388 66 383 82" fill="none" stroke={`url(#${P}-lava)`} stroke-width="3" stroke-linecap="round" />
      </Vol>
      {/* un volcan plus loin, à gauche, et sa fumée */}
      <circle class="bk-breathe" cx="96" cy="86" r="34" fill={`url(#${P}-crater)`} opacity="0.7" />
      <Vol p={P} d={cone(96, G - 18, 80, 86, 12)} fill={`url(#${P}-far2)`} line={1.1} inkA={0.35} depth={6} shade={0.22} rim={0.3}>
        <path class="gd-lava" d="M92 88 Q84 108 94 124 Q100 136 90 150" fill="none" stroke={`url(#${P}-lava)`} stroke-width="3.4" stroke-linecap="round" />
      </Vol>
      <g class="bk-cloud" opacity="0.7"><Vol p={P} d={cloud(56, 74, 74, 4)} fill={`url(#${P}-smoke)`} line={0} depth={4} shade={0.2} rim={0.3} /></g>
      {/* les falaises proches */}
      <Vol p={P} d={bumps(11, G - 12, 24, 46, G + 2)} fill={`url(#${P}-cliff)`} line={1.2} inkA={0.45} depth={5} shade={0.25} rim={0.25} />
      <Gate p={P} stone="basalt" trim="trim"
        back={[[-46, 18], [46, 18], [-26, 30], [26, 30]].map(([dx, h]) => (
          <Vol p={P} d={spike(dx!, h!)} fill={`url(#${P}-basalt)`} line={1.4} depth={3} shade={0.34} rim={0.5}>
            <path d={spike(dx!, h!)} fill="none" stroke="#ff8a3a" stroke-width="3" opacity="0.5" transform="translate(-2 2)" />
          </Vol>
        ))}
        sign={<path class="gd-flicker" style={{ transformOrigin: `${GX}px 76px` }} d={flame(GX, 76, 22)} fill={`url(#${P}-flame)`} stroke={INK} stroke-opacity="0.55" stroke-width="1.2" />}>
        {cracks.map((d) => <path class="gd-lava" d={d} fill="none" stroke="#ff9a3a" stroke-width="2.4" stroke-linecap="round" />)}
      </Gate>
      {/* deux braseros posés au sol, leur flamme qui danse */}
      {[GX - 100, GX + 96].map((x, i) => (
        <g>
          <circle class="bk-glow" cx={x} cy={G - 36} r="26" fill={`url(#${P}-halo)`} />
          <g class="gd-flicker" style={{ transformOrigin: `${x}px ${G - 26}px`, animationDelay: `${-i * 0.7}s` }}>
            <path d={flame(x, G - 25, 24)} fill={`url(#${P}-flame)`} stroke={INK} stroke-opacity="0.4" stroke-width="1" />
          </g>
          <Vol p={P} d={`M${x - 13} ${G - 27} H${x + 13} Q${x + 12} ${G - 15} ${x + 4} ${G - 13} V${G - 4} H${x + 8} V${G} H${x - 8} V${G - 4} H${x - 4} V${G - 13} Q${x - 12} ${G - 15} ${x - 13} ${G - 27} Z`} fill={`url(#${P}-trim)`} line={1.3} depth={2} />
        </g>
      ))}
      <Vol p={P} d={rock(62, 22, 18)} fill={`url(#${P}-rock)`} line={1.3} depth={4} shade={0.3} rim={0.4} />
      <Vol p={P} d={rock(100, 12, 10)} fill={`url(#${P}-rock)`} line={1.2} depth={3} shade={0.3} rim={0.4} />
      <Ground p={P} extra={
        <>
          {/* un ruisseau de lave, plat, qui traverse le sol */}
          <path class="gd-shimmer" d={`M${X0} ${G + 10} Q60 ${G + 6} 120 ${G + 11} T${GX} ${G + 9} T${X1} ${G + 12} V${G + 17} Q300 ${G + 20} ${GX} ${G + 16} T120 ${G + 18} T${X0} ${G + 16} Z`} fill={`url(#${P}-lava)`} opacity="0.9" />
          <path d={`M${GX - 30} ${G} H${GX + 30} L${GX + 52} ${G + 10} H${GX - 52} Z`} fill="#ffb45a" opacity="0.28" />
        </>
      } />
      <Rising seed={31} n={18} x0={30} x1={400} y0={70} y1={G} cls="gd-ember">
        {(x, y, s) => <circle cx={f(x)} cy={f(y)} r={f(s)} fill={s > 1.6 ? '#ffe08a' : '#ff9a3a'} />}
      </Rising>
    </>
  );
}

// ---------- Eau : la porte du temple englouti ----------
function Water() {
  const P = 'gdw';
  const weed = (x: number, h: number, i: number) => (
    <g class="bk-sway" style={{ transformOrigin: `${x}px ${G}px`, animationDelay: `${-i * 1.3}s` }}>
      <path d={`M${x} ${G} C${x - 8} ${G - h * 0.3} ${x + 8} ${G - h * 0.6} ${x - 2} ${G - h} C${x + 6} ${G - h * 0.62} ${x - 3} ${G - h * 0.3} ${x + 5} ${G} Z`}
        fill={`url(#${P}-weed)`} stroke={INK} stroke-opacity="0.45" stroke-width="1.1" />
    </g>
  );
  const coral = (x: number, y: number, k: number) =>
    `M${f(x - 3 * k)} ${f(y)} Q${f(x - 4 * k)} ${f(y - 8 * k)} ${f(x - 10 * k)} ${f(y - 12 * k)} Q${f(x - 12 * k)} ${f(y - 16 * k)} ${f(x - 8 * k)} ${f(y - 16 * k)} Q${f(x - 4 * k)} ${f(y - 13 * k)} ${f(x - 1 * k)} ${f(y - 9 * k)} Q${f(x)} ${f(y - 18 * k)} ${f(x + 2 * k)} ${f(y - 21 * k)} Q${f(x + 6 * k)} ${f(y - 22 * k)} ${f(x + 5 * k)} ${f(y - 17 * k)} Q${f(x + 4 * k)} ${f(y - 11 * k)} ${f(x + 5 * k)} ${f(y - 8 * k)} Q${f(x + 9 * k)} ${f(y - 12 * k)} ${f(x + 11 * k)} ${f(y - 10 * k)} Q${f(x + 12 * k)} ${f(y - 6 * k)} ${f(x + 4 * k)} ${f(y - 3 * k)} L${f(x + 3 * k)} ${f(y)} Z`;
  /** le fronton du temple, posé sur les chapiteaux des piliers (derrière l'arche) */
  const pediment = `M${GX - 78} 84 L${GX - 7} 34 Q${GX} 29 ${GX + 7} 34 L${GX + 78} 84 Q${GX + 81} 89 ${GX + 74} 89 H${GX - 74} Q${GX - 81} 89 ${GX - 78} 84 Z`;
  const tympan = `M${GX - 56} 82 L${GX - 5} 46 Q${GX} 43 ${GX + 5} 46 L${GX + 56} 82 Z`;
  /** une méduse qui luit : sa cloche et ses filaments courbes */
  const jelly = (x: number, y: number, k: number, i: number) => (
    <g class={`bk-float${i ? ' bk-float-2' : ''}`}>
      <circle class="bk-glow" cx={x} cy={y} r={18 * k} fill={`url(#${P}-jglow)`} />
      <g fill="none" stroke="#ffc8f0" stroke-width={1.4 * k} stroke-linecap="round" opacity="0.85">
        {[-5, 0, 5].map((dx, j) => <path d={`M${f(x + dx * k)} ${f(y + 3 * k)} q${f(3 * k)} ${f(6 * k)} 0 ${f(10 * k)} t0 ${f((10 + j * 2) * k)}`} />)}
      </g>
      <Vol p={P} d={`M${f(x - 10 * k)} ${f(y + 4 * k)} Q${f(x - 11 * k)} ${f(y - 10 * k)} ${f(x)} ${f(y - 10 * k)} Q${f(x + 11 * k)} ${f(y - 10 * k)} ${f(x + 10 * k)} ${f(y + 4 * k)} Q${f(x + 5 * k)} ${f(y + 1 * k)} ${f(x)} ${f(y + 4 * k)} Q${f(x - 5 * k)} ${f(y + 1 * k)} ${f(x - 10 * k)} ${f(y + 4 * k)} Z`} fill={`url(#${P}-jelly)`} line={1.1} depth={2} shade={0.2} rim={0.7} />
    </g>
  );
  return (
    <>
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={VY - 20} y2={G} stops={[[0, '#2d6f86'], [0.4, '#1b4a6e'], [0.75, '#142f5c'], [1, '#101f48']]} />
        <VGrad id={`${P}-ground`} y1={G} y2={DH} stops={[[0, '#3a4a6a'], [0.35, '#24294e'], [1, '#141634']]} />
        <Glow id={`${P}-halo`} c="#4ee0d0" a={0.6} />
        <Glow id={`${P}-core`} c="#e4fff2" a={0.85} />
        <Glow id={`${P}-sun`} c="#c8fff0" a={0.55} />
        <Glow id={`${P}-jglow`} c="#ff9ae0" a={0.55} />
        <VGrad id={`${P}-door`} stops={[[0, '#0c2240'], [0.55, '#2bb0b8'], [1, '#c8fbe6']]} />
        <Mat id={`${P}-stone`} c="#8b9fb0" k={0.8} />
        <Mat id={`${P}-trim`} c="#c8b494" k={0.8} />
        <Mat id={`${P}-ruin`} c="#24456a" k={0.45} />
        <Mat id={`${P}-coral`} c="#ff7a7a" />
        <Mat id={`${P}-coral2`} c="#ffa24a" />
        <Mat id={`${P}-weed`} c="#3aa07a" k={0.7} />
        <Mat id={`${P}-fish`} c="#ffc24a" />
        <Mat id={`${P}-jelly`} c="#e48ae0" />
        <VGrad id={`${P}-sign`} stops={[[0, '#e8fff8'], [0.5, '#5ae0d8'], [1, '#2a8ab8']]} />
      </defs>
      <rect x={X0} y={Y0} width={X1 - X0} height={G - Y0 + 4} fill={`url(#${P}-sky)`} />
      {/* la lumière de la surface (en haut à droite) et ses reflets qui ondulent, en courbes */}
      <circle class="bk-breathe" cx="350" cy="10" r="130" fill={`url(#${P}-sun)`} />
      <g class="gd-caustic">
        {[[150, 26, 40, 9], [236, 14, 46, 10], [318, 40, 34, 8], [80, 44, 30, 7], [196, 52, 26, 6]].map(([x, y, rx, ry]) => (
          <ellipse cx={x} cy={y} rx={rx} ry={ry} fill={`url(#${P}-sun)`} opacity="0.7" />
        ))}
      </g>
      {/* les ruines englouties au loin : colonnes et arches dans le bleu profond */}
      <g opacity="0.85">
        {[[50, 96, 16], [92, 110, 14], [140, 120, 12], [362, 92, 16], [398, 104, 14]].map(([x, top, w]) => (
          <Vol p={P} d={rr(x! - w! / 2, top!, w!, G - top!, 3)} fill={`url(#${P}-ruin)`} line={1.1} inkA={0.35} depth={4} shade={0.2} rim={0.25} />
        ))}
        <Vol p={P} d={`M42 96 H100 V104 H42 Z`} fill={`url(#${P}-ruin)`} line={1.1} inkA={0.35} depth={3} shade={0.2} rim={0.25} />
      </g>
      <Vol p={P} d={bumps(5, G - 8, 18, 52, G + 2)} fill="#1c2f58" line={1.1} inkA={0.4} depth={4} shade={0.22} rim={0.2} />
      {/* deux poissons qui passent, deux méduses qui luisent */}
      <g class="gd-fish">
        <Vol p={P} d="M330 50 Q342 40 354 48 L362 42 L360 52 L362 60 L354 54 Q342 62 330 50 Z" fill={`url(#${P}-fish)`} line={1.1} depth={2} shade={0.25} rim={0.5} />
      </g>
      <g class="gd-fish gd-fish-2">
        <Vol p={P} d="M150 126 Q158 120 166 125 L171 121 L170 127 L171 133 L166 129 Q158 134 150 126 Z" fill={`url(#${P}-coral)`} line={1} depth={1.5} shade={0.25} rim={0.5} />
      </g>
      {jelly(176, 108, 1, 0)}
      {jelly(352, 92, 0.75, 1)}
      {[[60, 64, 0], [110, 50, 1], [134, 40, 2], [368, 58, 3], [392, 46, 4]].map(([x, h, i]) => weed(x!, h!, i!))}
      <Gate p={P} stone="stone" trim="trim"
        back={
          <>
            <Vol p={P} d={pediment} fill={`url(#${P}-trim)`} line={1.5} depth={5} shade={0.34} rim={0.6}>
              <path d={tympan} fill="#5a7890" opacity="0.45" />
            </Vol>
            <Vol p={P} d={coral(GX + 44, 62, 0.75)} fill={`url(#${P}-coral)`} line={1.1} depth={2} rim={0.5} />
          </>
        }
        sign={<g class="gd-bob"><path d={drop(GX, 78, 24)} fill={`url(#${P}-sign)`} stroke={INK} stroke-opacity="0.55" stroke-width="1.2" /><circle cx={GX + 3.5} cy="67" r="2.4" fill="#fff" opacity="0.9" /></g>}>
        {/* les traces de l'eau sur la pierre, en courbes douces */}
        <path d={`M${GX - 58} 112 Q${GX - 48} 108 ${GX - 40} 114 Q${GX - 34} 120 ${GX - 26} 116`} fill="none" stroke="#4a6a86" stroke-width="2" stroke-linecap="round" opacity="0.6" />
        <path d={`M${GX + 30} 104 Q${GX + 40} 98 ${GX + 48} 104 Q${GX + 54} 110 ${GX + 60} 106`} fill="none" stroke="#4a6a86" stroke-width="2" stroke-linecap="round" opacity="0.6" />
      </Gate>
      {/* le corail et les algues accrochés à la porte */}
      <Vol p={P} d={coral(GX - 72, G - 2, 1.5)} fill={`url(#${P}-coral)`} line={1.2} depth={2.5} rim={0.5} />
      <Vol p={P} d={coral(GX + 76, G - 2, 1.15)} fill={`url(#${P}-coral2)`} line={1.2} depth={2.5} rim={0.5} />
      {[[GX + 54, 34, 5], [GX - 88, 44, 6]].map(([x, h, i]) => weed(x!, h!, i!))}
      <Ground p={P} extra={
        <>
          <path d={`M${GX - 30} ${G} H${GX + 30} L${GX + 50} ${G + 10} H${GX - 50} Z`} fill="#8af0e0" opacity="0.22" />
          {[[70, 10], [140, 8], [360, 12]].map(([x, w]) => <Vol p={P} d={cloud(x! - w!, G + 7, w! * 2, x!)} fill="#3a4a72" line={1} inkA={0.4} depth={2} shade={0.25} rim={0.3} />)}
        </>
      } />
      <Rising seed={17} n={14} x0={30} x1={400} y0={70} y1={G} cls="gd-bubble">
        {(x, y, s) => (
          <g>
            <circle cx={f(x)} cy={f(y)} r={f(s * 2.2)} fill="#c8fff0" fill-opacity="0.12" stroke="#d8fff4" stroke-opacity="0.8" stroke-width="0.9" />
            <circle cx={f(x + s * 0.7)} cy={f(y - s * 0.7)} r={f(s * 0.55)} fill="#fff" opacity="0.85" />
          </g>
        )}
      </Rising>
    </>
  );
}

// ---------- Terre : la porte taillée dans la roche d'une caverne de cristaux ----------
function Earth() {
  const P = 'gde';
  const cluster = (x: number, k: number, mat: string, flip = 1, y = G) => (
    <g>
      <Vol p={P} d={prism(x - 9 * k * flip, y, 26 * k, 11 * k, -7 * k * flip)} fill={`url(#${P}-${mat})`} line={1.2} depth={2.5} rim={0.7} />
      <Vol p={P} d={prism(x + 8 * k * flip, y, 22 * k, 10 * k, 6 * k * flip)} fill={`url(#${P}-${mat})`} line={1.2} depth={2.5} rim={0.7} />
      <Vol p={P} d={prism(x, y, 40 * k, 14 * k, 1)} fill={`url(#${P}-${mat})`} line={1.3} depth={3} rim={0.75} />
    </g>
  );
  const rock = (x: number, y: number, w: number) =>
    `M${f(x - w)} ${f(y)} Q${f(x - w * 0.9)} ${f(y - w * 0.7)} ${f(x - w * 0.2)} ${f(y - w * 0.8)} Q${f(x + w * 0.8)} ${f(y - w * 0.9)} ${f(x + w)} ${f(y - w * 0.1)} Q${f(x + w * 0.5)} ${f(y + w * 0.9)} ${f(x)} ${f(y + w * 1.1)} Q${f(x - w * 0.6)} ${f(y + w * 0.7)} ${f(x - w)} ${f(y)} Z`;
  /** la falaise où la porte est taillée : de gros blocs ronds, du sol jusqu'au-dessus de l'arche */
  const cliff = `M${GX - 112} ${G} Q${GX - 118} 120 ${GX - 100} 96 Q${GX - 104} 64 ${GX - 76} 54 Q${GX - 70} 30 ${GX - 40} 32 Q${GX - 20} 14 ${GX + 6} 24 Q${GX + 34} 12 ${GX + 52} 32 Q${GX + 84} 34 ${GX + 88} 60 Q${GX + 112} 72 ${GX + 108} 100 Q${GX + 122} 124 ${GX + 114} ${G} Z`;
  return (
    <>
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={VY - 20} y2={G} stops={[[0, '#1a1028'], [0.5, '#2e1c38'], [0.85, '#4a2e3e'], [1, '#6a4436']]} />
        <VGrad id={`${P}-ground`} y1={G} y2={DH} stops={[[0, '#5a3a34'], [0.35, '#3a2430'], [1, '#1e1222']]} />
        <Glow id={`${P}-halo`} c="#7aff9a" a={0.5} />
        <Glow id={`${P}-core`} c="#f4ffc0" a={0.85} />
        <Glow id={`${P}-crys`} c="#5affb0" a={0.6} />
        <Glow id={`${P}-light`} c="#ffe2a0" a={0.5} />
        <VGrad id={`${P}-door`} stops={[[0, '#16241a'], [0.55, '#4ac06a'], [1, '#eaffb0']]} />
        <Mat id={`${P}-rock`} c="#a07a5c" k={0.8} />
        <Mat id={`${P}-cliff`} c="#6e4e48" k={0.7} />
        <Mat id={`${P}-trim`} c="#c49a6c" k={0.8} />
        <Mat id={`${P}-cave`} c="#3a2436" k={0.5} />
        <Mat id={`${P}-moss`} c="#6ab04a" k={0.8} />
        <Mat id={`${P}-emerald`} c="#3ad08a" />
        <Mat id={`${P}-amber`} c="#ffb43a" />
        <Mat id={`${P}-float`} c="#7a5a4a" k={0.8} />
      </defs>
      <rect x={X0} y={Y0} width={X1 - X0} height={G - Y0 + 4} fill={`url(#${P}-sky)`} />
      {/* une ouverture dans la voûte, en haut à droite : la lumière du jour qui tombe doucement */}
      <circle class="bk-breathe" cx="370" cy="20" r="110" fill={`url(#${P}-light)`} />
      {/* la voûte de la caverne : des stalactites arrondies qui pendent */}
      <Vol p={P} d={`M${X0} ${Y0} H${X1} V${VY - 4} ${[420, 380, 330, 290, 240, 196, 150, 108, 60, 20].map((x, i) => `Q${x + 14} ${VY + (i % 2 ? 30 : 12)} ${x} ${VY + (i % 2 ? 34 : 16)} Q${x - 10} ${VY + (i % 2 ? 14 : 4)} ${x - 22} ${VY - 2}`).join(' ')} L${X0} ${VY - 4} Z`} fill={`url(#${P}-cave)`} line={1.2} inkA={0.5} depth={5} shade={0.25} rim={0.3} />
      {/* des stalagmites au loin */}
      {[[54, 60, 20], [104, 44, 14], [144, 30, 10], [376, 52, 16], [410, 70, 22]].map(([x, h, w]) => (
        <Vol p={P} d={cone(x!, G - 6, w!, G - 6 - h!, 4)} fill={`url(#${P}-cave)`} line={1.1} inkA={0.4} depth={4} shade={0.22} rim={0.3} />
      ))}
      <Vol p={P} d={bumps(23, G - 8, 16, 40, G + 2)} fill="#3e2834" line={1.1} inkA={0.45} depth={4} shade={0.22} rim={0.25} />
      {/* des rochers qui flottent, des pointes de cristal sur eux */}
      <g class="bk-float">
        <Vol p={P} d={prism(160, 112, 18, 8, 2)} fill={`url(#${P}-emerald)`} line={1.1} depth={2} rim={0.7} />
        <Vol p={P} d={rock(160, 118, 15)} fill={`url(#${P}-float)`} line={1.3} depth={4} />
      </g>
      <g class="bk-float bk-float-2">
        <Vol p={P} d={prism(372, 62, 14, 7, -2)} fill={`url(#${P}-amber)`} line={1.1} depth={2} rim={0.7} />
        <Vol p={P} d={rock(372, 68, 12)} fill={`url(#${P}-float)`} line={1.2} depth={3} />
      </g>
      <g class="bk-float"><Vol p={P} d={rock(118, 136, 7)} fill={`url(#${P}-float)`} line={1.1} depth={2} /></g>
      <Gate p={P} stone="rock" trim="trim"
        back={
          <>
            <Vol p={P} d={cliff} fill={`url(#${P}-cliff)`} line={1.5} depth={8} shade={0.36} rim={0.45}>
              {/* la mousse sur le haut de la falaise */}
              <path d={`M${GX - 104} 70 Q${GX - 86} 44 ${GX - 56} 40 Q${GX - 30} 18 ${GX} 26 Q${GX + 36} 14 ${GX + 60} 38 Q${GX + 92} 42 ${GX + 104} 70 L${GX + 104} 60 Q${GX + 88} 54 ${GX + 76} 60 Q${GX + 60} 48 ${GX + 44} 52 Q${GX + 22} 34 ${GX} 42 Q${GX - 24} 34 ${GX - 42} 52 Q${GX - 62} 48 ${GX - 76} 62 Q${GX - 92} 58 ${GX - 104} 70 Z`} fill={`url(#${P}-moss)`} opacity="0.95" />
            </Vol>
            {cluster(GX - 70, 0.55, 'amber', 1, 36)}
            {cluster(GX + 66, 0.6, 'emerald', -1, 34)}
          </>
        }
        sign={<g class="gd-gem" style={{ transformOrigin: `${GX}px 66px` }}><Vol p={P} d={`M${GX} 52 L${GX + 10} 62 L${GX + 6} 76 H${GX - 6} L${GX - 10} 62 Z`} fill={`url(#${P}-emerald)`} line={1.2} depth={2} rim={0.8} /></g>}>
        {/* la mousse qui coule sur le haut de l'arche */}
        <path d={`M${GX - 66} 98 Q${GX - 58} 60 ${GX} 56 Q${GX + 58} 60 ${GX + 66} 98 L${GX + 66} 92 Q${GX + 58} 100 ${GX + 52} 92 Q${GX + 44} 84 ${GX + 38} 90 Q${GX + 30} 76 ${GX + 22} 80 Q${GX + 12} 70 ${GX} 76 Q${GX - 12} 70 ${GX - 22} 80 Q${GX - 32} 74 ${GX - 40} 88 Q${GX - 48} 82 ${GX - 54} 96 Q${GX - 60} 100 ${GX - 66} 98 Z`} fill={`url(#${P}-moss)`} />
      </Gate>
      {/* les cristaux de part et d'autre de la porte, leur lueur */}
      <circle class="bk-glow" cx={GX - 98} cy={G - 22} r="34" fill={`url(#${P}-crys)`} />
      <circle class="bk-glow bk-late" cx={GX + 98} cy={G - 18} r="28" fill={`url(#${P}-crys)`} />
      {cluster(GX - 96, 1.2, 'emerald')}
      {cluster(GX + 98, 0.95, 'amber', -1)}
      {cluster(70, 0.7, 'amber')}
      <Ground p={P} extra={
        <>
          <path d={`M${GX - 30} ${G} H${GX + 30} L${GX + 50} ${G + 10} H${GX - 50} Z`} fill="#c8ff9a" opacity="0.2" />
          {[[104, 9], [180, 7], [372, 10]].map(([x, w]) => <Vol p={P} d={cloud(x! - w!, G + 8, w! * 2, x! + 3)} fill="#6a4a3c" line={1} inkA={0.45} depth={2} shade={0.25} rim={0.35} />)}
        </>
      } />
      {/* des éclats de lumière sur les cristaux */}
      {[[GX - 92, G - 44], [GX + 102, G - 34], [GX + 66, 2], [74, G - 22]].map(([x, y], i) => (
        <path class="bk-twinkle" style={{ animationDelay: `${-i * 0.8}s`, transformOrigin: `${x}px ${y}px` }} d={spark(x!, y!, 5)} fill="#f4ffd8" />
      ))}
      <Rising seed={41} n={10} x0={40} x1={400} y0={70} y1={G} cls="bk-mote">
        {(x, y, s) => <circle cx={f(x)} cy={f(y)} r={f(s * 0.9)} fill="#d8ffb0" />}
      </Rising>
    </>
  );
}

// ---------- Vent : la porte de la forteresse du ciel ----------
function Wind() {
  const P = 'gdv';
  /** une aile de plumes rondes de part et d'autre de la clé de voûte (sx = -1 à gauche, 1 à droite) */
  const wing = (sx: number) => {
    const X = (d: number) => f(GX + sx * d);
    return `M${X(16)} 60 Q${X(32)} 42 ${X(64)} 34 Q${X(66)} 41 ${X(58)} 46 Q${X(63)} 51 ${X(52)} 55 Q${X(55)} 61 ${X(43)} 62 Q${X(44)} 68 ${X(32)} 67 Q${X(30)} 73 ${X(16)} 72 Z`;
  };
  /** une île qui flotte au loin, sa petite tour */
  const isle = (x: number, y: number, w: number) =>
    `M${f(x - w)} ${f(y)} Q${f(x - w * 0.6)} ${f(y - 4)} ${f(x)} ${f(y - 3)} Q${f(x + w * 0.6)} ${f(y - 4)} ${f(x + w)} ${f(y)} Q${f(x + w * 0.5)} ${f(y + w * 0.5)} ${f(x + w * 0.1)} ${f(y + w * 0.9)} Q${f(x - w * 0.4)} ${f(y + w * 0.5)} ${f(x - w)} ${f(y)} Z`;
  return (
    <>
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={VY - 20} y2={G} stops={[[0, '#3a2a8a'], [0.45, '#6e5ac8'], [0.78, '#c79ae0'], [1, '#ffdcc0']]} />
        <VGrad id={`${P}-ground`} y1={G} y2={DH} stops={[[0, '#f4ecff'], [0.3, '#cdbaf0'], [1, '#8a72c8']]} />
        <Glow id={`${P}-halo`} c="#b4ffe4" a={0.55} />
        <Glow id={`${P}-core`} c="#ffffff" a={0.85} />
        <Glow id={`${P}-sun`} c="#fff2c8" a={0.9} />
        <VGrad id={`${P}-door`} stops={[[0, '#3a2a7a'], [0.55, '#6ad8c0'], [1, '#f4fff0']]} />
        <Mat id={`${P}-marble`} c="#ece4f4" k={0.9} />
        <Mat id={`${P}-gold`} c="#ffc24a" />
        <Mat id={`${P}-spire`} c="#b4a4e0" k={0.6} />
        <Mat id={`${P}-roof`} c="#4fb8a0" />
        <Mat id={`${P}-wing`} c="#fff8ee" k={0.8} />
        <Mat id={`${P}-isle`} c="#9a7ac8" k={0.6} />
        <Mat id={`${P}-grass`} c="#6ad0a0" k={0.7} />
        <VGrad id={`${P}-cloud`} stops={[[0, '#ffffff'], [0.6, '#f0e4ff'], [1, '#c8b4ec']]} />
        <VGrad id={`${P}-far`} stops={[[0, '#e8d8ff'], [1, '#a890dc']]} />
      </defs>
      <rect x={X0} y={Y0} width={X1 - X0} height={G - Y0 + 4} fill={`url(#${P}-sky)`} />
      <circle class="bk-breathe" cx="370" cy="30" r="100" fill={`url(#${P}-sun)`} />
      <circle cx="370" cy="30" r="13" fill="#fffbe8" />
      {/* les nuages lointains qui glissent, une île qui flotte et sa tour */}
      <g class="bk-cloud" opacity="0.75"><Vol p={P} d={cloud(10, 100, 120, 3)} fill={`url(#${P}-far)`} line={0} depth={4} shade={0.18} rim={0.6} /></g>
      <g class="bk-cloud bk-slow" opacity="0.7"><Vol p={P} d={cloud(300, 74, 80, 8)} fill={`url(#${P}-far)`} line={0} depth={4} shade={0.18} rim={0.6} /></g>
      <g class="bk-float">
        <Vol p={P} d={rr(140, 106, 9, 16, 2)} fill={`url(#${P}-spire)`} line={1.1} depth={2} />
        <Vol p={P} d={cone(144.5, 107, 7, 96, 1.5)} fill={`url(#${P}-roof)`} line={1.1} depth={2} />
        <Vol p={P} d={isle(146, 124, 22)} fill={`url(#${P}-isle)`} line={1.2} depth={4}>
          <path d="M122 124 Q146 116 170 124 V128 H122 Z" fill={`url(#${P}-grass)`} />
        </Vol>
      </g>
      {/* deux flèches de la forteresse derrière la porte, leurs fanions */}
      {[[GX - 84, 66, 12], [GX + 88, 48, 13]].map(([x, top, w], i) => (
        <g>
          <Flag p={P} x={x!} y={top! - 26} h={16} color={i ? '#ffc24a' : '#4fb8a0'} w={16} />
          <Vol p={P} d={rr(x! - w! / 2, top!, w!, G - top!, 3)} fill={`url(#${P}-spire)`} depth={4} />
          <Vol p={P} d={cone(x!, top! + 2, w! * 0.85, top! - 26, 2)} fill={`url(#${P}-roof)`} line={1.3} depth={3} />
        </g>
      ))}
      <Gate p={P} stone="marble" trim="gold"
        sign={<g class="gd-spin" style={{ transformOrigin: `${GX}px 66px` }}>
          <path d={`M${GX - 9} 70 C${GX - 10} 58 ${GX + 6} 54 ${GX + 9} 63 C${GX + 11} 70 ${GX + 2} 74 ${GX - 1} 68 C${GX - 3} 64 ${GX + 2} 61 ${GX + 4} 64`} fill="none" stroke={INK} stroke-opacity="0.55" stroke-width="5" stroke-linecap="round" />
          <path d={`M${GX - 9} 70 C${GX - 10} 58 ${GX + 6} 54 ${GX + 9} 63 C${GX + 11} 70 ${GX + 2} 74 ${GX - 1} 68 C${GX - 3} 64 ${GX + 2} 61 ${GX + 4} 64`} fill="none" stroke="#4fd8b4" stroke-width="2.8" stroke-linecap="round" />
        </g>}
        back={
          // les ailes de plumes de part et d'autre de la clé de voûte, qui battent doucement
          [-1, 1].map((sx) => (
            <g class="gd-wing" style={{ transformOrigin: `${GX + sx * 16}px 66px`, '--s': sx } as never}>
              <Vol p={P} d={wing(sx)} fill={`url(#${P}-wing)`} line={1.4} depth={3} rim={0.6} />
            </g>
          ))
        }>
        {/* les filets d'or de l'arche */}
        <path d={`M${GX - 60} 116 Q${GX - 60} 60 ${GX} 60 Q${GX + 60} 60 ${GX + 60} 116`} fill="none" stroke="#ffc24a" stroke-width="2.2" opacity="0.8" />
      </Gate>
      {/* la mer de nuages : une bande plate dont le haut est fait de bosses */}
      <Ground p={P} extra={<path d={`M${GX - 30} ${G} H${GX + 30} L${GX + 50} ${G + 10} H${GX - 50} Z`} fill="#b4ffe4" opacity="0.3" />} />
      <g class="bk-cloud bk-slow"><Vol p={P} d={bumps(13, G + 4, 16, 36, G + 16)} fill={`url(#${P}-cloud)`} line={1.1} inkA={0.25} depth={4} shade={0.15} rim={0.7} /></g>
      {/* les tourbillons de vent, des traits qui passent */}
      <g fill="none" stroke="#ffffff" stroke-linecap="round" stroke-width="2.4">
        <path class="gd-wind" d={swirl(60, 140, 120)} opacity="0.75" />
        <path class="gd-wind gd-wind-2" d={swirl(300, 96, 96, -1)} opacity="0.6" />
        <path class="gd-wind gd-wind-3" d={swirl(150, 76, 90, -0.8)} opacity="0.55" />
      </g>
      {/* des plumes qui volent */}
      {[[110, 70, 14], [190, 140, 11], [340, 128, 12], [210, 40, 9]].map(([x, y, l], i) => (
        <g class="gd-feather" style={{ animationDelay: `${-i * 2.6}s` }}>
          <Vol p={P} d={feather(x!, y!, l!)} fill={`url(#${P}-wing)`} line={1} depth={1.5} shade={0.2} rim={0.5} />
        </g>
      ))}
    </>
  );
}

const SCENES: Record<Element, () => JSX.Element> = { fire: Fire, water: Water, earth: Earth, wind: Wind };

/** La porte du donjon d'un élément, qui remplit son cadre (le sol reste en bas). */
export function DungeonArt({ element, class: cls }: { element: Element; class?: string }) {
  const Scene = SCENES[element];
  return (
    <svg class={cls} viewBox={`${VX} ${VY} ${DW - VX} ${DH - VY}`} preserveAspectRatio="xMaxYMax meet" aria-hidden="true">
      <Scene />
    </svg>
  );
}
