// Le plateau du choix de la section (style moderne, 26/11/2026) : le vrai décor du combat à venir (celui du clan des
// ennemis, en pixel art, comme au combat), vu de près, son sol bord à bord ; la formation posée dessus en dalles lisses :
// deux postes à l'arrière, le chef au centre, deux à l'avant, et trois chevrons du côté des ennemis.
// Chaque poste a sa dalle (`Plate`) : une tuile de verre clair aux coins arrondis (jamais un rond au sol), cerclée de la
// couleur de l'élément du héros, d'or pour le chef ; vide, elle appelle un héros (pointillés et « + »).
import type { Slot } from '../../core/battle/types';
import type { Clan } from '../look';
import { sceneBg } from './fond-image';

export const STAGE_W = 420, STAGE_H = 360;
/** Le point où chaque héros pose les pieds (le centre de sa dalle). */
export const STAGE_POS: Record<Slot, [number, number]> = { 3: [100, 180], 4: [100, 292], 2: [210, 236], 0: [320, 180], 1: [320, 292] };

/** Le décor du combat (image du clan, calée en bas : on voit son sol) et les chevrons vers les ennemis. */
export function FormationStage({ clan }: { clan: Clan }) {
  return (
    <div class="field-bg field-scene" style={sceneBg(clan)} aria-hidden="true">
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
