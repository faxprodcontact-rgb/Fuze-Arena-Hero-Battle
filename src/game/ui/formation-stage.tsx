// Le plateau du choix de la section (style moderne, 26/11/2026) : un terrain d'entraînement dessiné pour la formation
// (ce n'est plus le décor du combat). Vu d'un peu au-dessus : au fond un ciel teinté par l'élément du clan ennemi, une
// crête lointaine où se dressent des châteaux (petits, voilés par la distance, toits et fanions de la couleur de
// l'élément), des collines, une haie ronde ; devant, une grande dalle de pierre lavande, plate, d'un bord à l'autre, calme
// sous les cinq postes. Une seule lumière, en haut à droite.
// La formation est posée dessus en dalles lisses : deux postes à l'arrière, le chef au centre, deux à l'avant, et trois
// chevrons du côté des ennemis. Chaque poste a sa dalle (`Plate`) : une tuile de verre clair aux coins arrondis (jamais un
// rond au sol), cerclée de la couleur de l'élément du héros, d'or pour le chef ; vide, elle appelle un héros.
import { Component } from 'preact';
import type { Element } from '../../core/types';
import type { Slot } from '../../core/battle/types';
import { clanElement, type Clan } from '../look';
import { Glow, Mat, Motes, Soft, VGrad, Vol, cloud, f, hills, mix, peaks, rr } from './backdrop-kit';
import './sections/backdrops.css';
import { retintSvg } from './theme';

export const STAGE_W = 420, STAGE_H = 360;
/** Le point où chaque héros pose les pieds (le centre de sa dalle). */
export const STAGE_POS: Record<Slot, [number, number]> = { 3: [100, 180], 4: [100, 292], 2: [210, 236], 0: [320, 180], 1: [320, 292] };

/** Les teintes du terrain selon l'élément du clan ennemi : ciel (haut, horizon), couleur des toits et des fanions. */
const TINT: Record<Element, { sky: [string, string]; accent: string; flag: string }> = {
  fire: { sky: ['#5b3db4', '#ffb08a'], accent: '#ff6b5e', flag: '#ffc22e' },
  water: { sky: ['#3466d8', '#a6dcff'], accent: '#2f8cff', flag: '#5ce1ff' },
  wind: { sky: ['#3a7fd8', '#bff2dc'], accent: '#3fcf8e', flag: '#fff6cf' },
  earth: { sky: ['#6b4fc4', '#ffd59a'], accent: '#ffae1f', flag: '#ff6b5e' },
};
/** Le fond de la dalle et la haie. */
const BACK = 122;

function Ground({ clan }: { clan: Clan }) {
  const el = clanElement(clan);
  const t = TINT[el];
  const p = `fs-${el}`;
  const W = STAGE_W, H = STAGE_H;
  return (
    <svg class="field-ground" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid slice">
      <defs>
        <Soft p={p} />
        <VGrad id={`${p}-sky`} y1={0} y2={BACK} stops={[[0, t.sky[0]], [1, t.sky[1]]]} />
        <VGrad id={`${p}-mat`} y1={BACK} y2={H} stops={[[0, '#a59bf0'], [0.35, '#8a7fe2'], [1, '#6a5ec8']]} />
        <linearGradient id={`${p}-sheen`} x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a1257" stop-opacity="0.12" /><stop offset="0.6" stop-color="#fff6cf" stop-opacity="0" /><stop offset="1" stop-color="#fff6cf" stop-opacity="0.2" /></linearGradient>
        <Glow id={`${p}-sun`} c="#fff3c7" a={0.85} />
        <Mat id={`${p}-hill`} c="#8f8de6" k={0.5} />
        <Mat id={`${p}-hedge`} c="#46b87e" />
        <Mat id={`${p}-ridge`} c={mix('#9a95ea', t.sky[1], 0.45)} k={0.4} />
        <VGrad id={`${p}-mist`} y1={BACK - 40} y2={BACK - 4} stops={[[0, t.sky[1], 0], [1, t.sky[1], 0.55]]} />
        <Mat id={`${p}-rim`} c="#c9c0fa" k={0.5} />
      </defs>
      {/* le ciel, sa lumière en haut à droite, un nuage */}
      <rect width={W} height={BACK + 4} fill={`url(#${p}-sky)`} />
      <circle class="bk-breathe" cx="392" cy="10" r="90" fill={`url(#${p}-sun)`} />
      <g class="bk-cloud" opacity="0.9"><Vol p={p} d={cloud(104, 40, 52, 6)} fill="#ffffff" line={0} depth={4} shade={0.15} rim={0} /></g>

      {/* au loin : une crête voilée, une brume à son pied */}
      <Vol p={p} d={peaks([[34, 24, 62], [214, 20, 86], [398, 26, 66]], BACK - 4, BACK + 4)} fill={`url(#${p}-ridge)`} line={0} depth={3} shade={0.12} rim={0.3} />
      <rect y={BACK - 40} width={W} height="40" fill={`url(#${p}-mist)`} />
      <Vol p={p} d={hills(13, BACK - 4, 12, 110, BACK + 4)} fill={`url(#${p}-hill)`} line={1.2} inkA={0.35} depth={5} shade={0.2} rim={0.35} />

      {/* la haie ronde, au fond de la dalle */}
      <Vol p={p} d={hills(41, BACK + 2, 12, 34, BACK + 12)} fill={`url(#${p}-hedge)`} line={1.3} inkA={0.5} depth={4} />

      {/* la dalle : plate, d'un bord à l'autre ; un liseré clair la cerne à peine ; la lumière vient de la droite */}
      <rect y={BACK + 6} width={W} height={H - BACK - 6} fill={`url(#${p}-mat)`} />
      <rect y={BACK + 6} width={W} height={H - BACK - 6} fill={`url(#${p}-sheen)`} />
      <rect y={BACK + 4} width={W} height="8" fill="#2a1257" opacity="0.3" filter={`url(#${p}-soft)`} />
      <Vol p={p} d={`${rr(14, BACK + 18, W - 28, H, 22)} ${rr(22, BACK + 25, W - 44, H, 16)}`} ring fill={`url(#${p}-rim)`} line={0} depth={2} shade={0.25} rim={0.5} />
      <Motes seed={3} n={7} x0={20} x1={400} y0={60} y1={BACK + 60} color="#fffbe6" />
    </svg>
  );
}

/** Dessiné une fois par clan : l'application se redessine chaque seconde, le terrain n'a pas à suivre. */
class Frozen extends Component<{ clan: Clan }> {
  shouldComponentUpdate(next: { clan: Clan }) { return next.clan !== this.props.clan; }
  // l'essai « pierre » (?theme=pierre) : la dalle lavande devient basalte (le ciel garde la couleur de l'élément)
  componentDidMount() { retintSvg(this.base as SVGElement, 'all'); }
  componentDidUpdate() { retintSvg(this.base as SVGElement, 'all'); }
  render({ clan }: { clan: Clan }) { return <Ground clan={clan} />; }
}

/** Le terrain de la formation et les chevrons vers les ennemis. */
export function FormationStage({ clan }: { clan: Clan }) {
  return (
    <div class="field-bg field-fresh" aria-hidden="true">
      <Frozen clan={clan} />
      <svg class="field-arrows" viewBox={`0 0 ${STAGE_W} ${STAGE_H}`} preserveAspectRatio="xMidYMid slice">
        {[0, 1, 2].map((i) => (
          <path class="fd-chevron" style={{ animationDelay: `${i * 0.25}s` }} d={`M${368 + i * 11} 224 L${378 + i * 11} 236 L${368 + i * 11} 248`}
            fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
        ))}
      </svg>
    </div>
  );
}

/** La dalle d'un poste : une tuile de verre aux coins arrondis, vue en perspective, posée au sol. */
export function Plate({ leader, empty, color }: { leader: boolean; empty: boolean; color?: string }) {
  const ring = empty ? (leader ? '#ffd65c' : '#ffffff') : leader ? '#ffc22e' : (color ?? '#c8c2ec');
  return (
    <svg class="field-plate" viewBox="0 0 120 52" aria-hidden="true">
      {/* l'ombre douce, l'épaisseur, le dessus */}
      <rect x="6" y="16" width="108" height="34" rx="15" fill="#0a0620" opacity="0.4" />
      <rect x="8" y="14" width="104" height="32" rx="14" fill={leader ? '#b06a00' : '#2e2470'} opacity={empty ? 0.55 : 0.9} />
      <rect x="8" y="9" width="104" height="32" rx="14" fill={empty ? '#ffffff' : leader ? '#fff1c7' : '#f4f2fc'} opacity={empty ? 0.18 : 0.92} />
      {!empty && <rect x="8" y="9" width="104" height="32" rx="14" fill={ring} opacity="0.22" />}
      <rect x="9.5" y="10.5" width="101" height="29" rx="12.5" fill="none" stroke={ring} stroke-width="3"
        stroke-dasharray={empty ? '7 6' : undefined} opacity={empty ? 0.9 : 1} />
      {empty && <path class="fd-plus" d="M60 17 V33 M52 25 H68" stroke={ring} stroke-width="3.600" stroke-linecap="round" />}
    </svg>
  );
}
