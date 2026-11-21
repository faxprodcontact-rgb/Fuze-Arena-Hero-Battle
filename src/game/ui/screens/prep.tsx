// Préparation d'un combat : les ennemis en haut, la section sur le plateau, les héros en bas.
// Toucher un héros = l'ajouter ou le retirer. Toucher deux postes = les échanger.
import { useState } from 'preact/hooks';
import { LEADER_SLOT, type Slot } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { heroImage, monsterImage } from '../../art';
import { battleLook } from '../../look';
import { GLYPHS } from '../backdrop-adventure';
import { fmt, t } from '../../i18n';
import { autoFormation, startBattleFromPlan, swapSlots, toggleInFormation, type BattlePlan } from '../../state/actions';
import { formationOf, heroByUid, heroPower, slotCount, sortedHeroes, teamPower, type TeamKind } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Btn, HeroCard, Icon, Stars } from '../kit';
import { close, startBattle, toast } from '../nav';
import { Backdrop } from '../backdrop';
import { talentText } from './hero-detail';

/**
 * Le plateau : l'estrade de la salle des héros, vue de près, avec une dalle par poste. La section garde la disposition du
 * combat (deux à l'arrière, le chef au centre, deux à l'avant, face aux ennemis qui seront à droite), centrée dans le cadre.
 */
const FIELD_W = 420;
const FIELD_H = 330;
/** Le point où chaque héros pose les pieds (le centre de sa dalle). */
const POS: Record<Slot, [number, number]> = { 3: [86, 138], 4: [86, 286], 2: [210, 212], 0: [334, 138], 1: [334, 286] };

/** Une flamme de brasero : trois langues emboîtées qui dansent. */
function Fire({ x, y }: { x: number; y: number }) {
  const drop = (k: number) => `M0 0 C${-9 * k} ${-3 * k} ${-8 * k} ${-14 * k} ${-2 * k} ${-25 * k} C0 ${-18 * k} ${7 * k} ${-16 * k} ${8 * k} ${-7 * k} C${8 * k} ${-2 * k} ${4 * k} 0 0 0 Z`;
  return (
    <g transform={`translate(${x} ${y})`}>
      <circle class="an-glow" cx="0" cy="-8" r="34" fill="url(#fd-fire)" />
      <path d="M-13 0 Q-13 12 0 12 Q13 12 13 0 Z" fill="#2f1b0c" /><path d="M-11 1 Q-11 10 0 10 Q11 10 11 1 Z" fill="url(#fd-bronze)" /><ellipse cx="0" cy="0" rx="13" ry="3" fill="#2f1b0c" /><ellipse cx="0" cy="0" rx="10.500" ry="2" fill="#ff8a2a" />
      <path class="ad-flame" d={drop(0.950)} fill="#ff6a1a" /><path class="ad-flame" style={{ animationDelay: '-0.2s', animationDuration: '0.42s' }} d={drop(0.660)} fill="#ffb02a" /><path class="ad-flame" style={{ animationDelay: '-0.35s', animationDuration: '0.36s' }} d={drop(0.380)} fill="#fff3b0" />
    </g>
  );
}

function FieldBackground() {
  const [a, b, c, d, e] = [POS[3], POS[4], POS[2], POS[0], POS[1]];
  // le tracé de la formation, serti dans la pierre : les deux postes arrière, le chef, les deux postes avant
  const lines = `M${a[0]} ${a[1]} L${c[0]} ${c[1]} L${d[0]} ${d[1]} M${b[0]} ${b[1]} L${c[0]} ${c[1]} L${e[0]} ${e[1]} M${a[0]} ${a[1]} L${b[0]} ${b[1]} M${d[0]} ${d[1]} L${e[0]} ${e[1]}`;
  return (
    <svg class="field-bg" viewBox={`0 0 ${FIELD_W} ${FIELD_H}`} preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs>
        <linearGradient id="fd-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a2254" /><stop offset="1" stop-color="#3d4c96" /></linearGradient>
        <linearGradient id="fd-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34407e" /><stop offset="1" stop-color="#141938" /></linearGradient>
        <radialGradient id="fd-top" cx="210" cy="190" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(210 190) scale(240 150) translate(-210 -190)"><stop offset="0" stop-color="#eef0ff" /><stop offset="0.55" stop-color="#b9c1ec" /><stop offset="1" stop-color="#7c86c4" /></radialGradient>
        <radialGradient id="fd-light" cx="210" cy="60" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(210 60) scale(250 170) translate(-210 -60)"><stop offset="0" stop-color="#ffe9a0" stop-opacity="0.6" /><stop offset="0.6" stop-color="#ffb86a" stop-opacity="0.12" /><stop offset="1" stop-color="#ffb86a" stop-opacity="0" /></radialGradient>
        <radialGradient id="fd-fire"><stop offset="0" stop-color="#ffb02a" stop-opacity="0.75" /><stop offset="0.5" stop-color="#ff7a1a" stop-opacity="0.22" /><stop offset="1" stop-color="#ff7a1a" stop-opacity="0" /></radialGradient>
        <linearGradient id="fd-bronze" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd98a" /><stop offset="0.45" stop-color="#c98a3a" /><stop offset="1" stop-color="#6b4016" /></linearGradient>
        <linearGradient id="fd-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.5" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
      </defs>
      {/* le pied du mur de la salle, la plinthe, le sol sombre autour de l'estrade */}
      <rect width={FIELD_W} height="40" fill="url(#fd-wall)" /><rect y="36" width={FIELD_W} height="4" fill="#56669e" /><rect y="36" width={FIELD_W} height="1.200" fill="#aab6e6" />
      <rect y="40" width={FIELD_W} height={FIELD_H - 40} fill="url(#fd-floor)" />
      {/* l'estrade : la marche du bas, le dessus de pierre claire, le filet d'or */}
      <ellipse cx="210" cy="200" rx="262" ry="160" fill="#5e6ab0" /><ellipse cx="210" cy="196" rx="262" ry="160" fill="#8d97d2" />
      <ellipse cx="210" cy="190" rx="242" ry="146" fill="#4a5494" /><ellipse cx="210" cy="186" rx="242" ry="146" fill="url(#fd-top)" />
      <ellipse cx="210" cy="186" rx="228" ry="135" fill="none" stroke="#c9952a" stroke-width="2.200" /><ellipse cx="210" cy="186" rx="223" ry="131" fill="none" stroke="#fff6dc" stroke-width="0.800" opacity="0.9" />
      <rect width={FIELD_W} height={FIELD_H} fill="url(#fd-light)" />
      {/* le tracé de la formation : une rainure sombre, un filet d'or dedans */}
      <path d={lines} fill="none" stroke="#6a74b8" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.7" />
      <path d={lines} fill="none" stroke="#d9a63e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      {/* vers l'avant : trois chevrons d'or s'allument l'un après l'autre, du côté des ennemis */}
      {[0, 1, 2].map((i) => (
        <g class="fd-chevron" style={{ animationDelay: `${i * 0.25}s` }}>
          <path d={`M${376 + i * 11} 197 L${387 + i * 11} 212 L${376 + i * 11} 227`} fill="none" stroke="#2f1b0c" stroke-width="6.500" stroke-linecap="round" stroke-linejoin="round" />
          <path d={`M${376 + i * 11} 197 L${387 + i * 11} 212 L${376 + i * 11} 227`} fill="none" stroke="url(#fd-gold)" stroke-width="3.400" stroke-linecap="round" stroke-linejoin="round" />
        </g>
      ))}
      {/* les braseros des coins */}
      <Fire x={22} y={30} /><Fire x={398} y={30} />
    </svg>
  );
}

/** La dalle d'un poste : un disque de pierre serti d'or. Celle du chef est plus riche (cercle de signes qui tourne) ; vide, elle appelle un héros. */
function Plate({ leader, empty }: { leader: boolean; empty: boolean }) {
  return (
    <svg class="field-plate" viewBox="0 0 120 52" aria-hidden="true">
      <ellipse cx="60" cy="31" rx="56" ry="19" fill="#0a0d24" opacity="0.45" />
      <path d="M8 24 V29 A52 17 0 0 0 112 29 V24 Z" fill={leader ? '#8a5a12' : '#3a4486'} />
      <ellipse cx="60" cy="24" rx="52" ry="17" fill={leader ? '#fff0c0' : '#d5daf8'} />
      <ellipse cx="60" cy="24" rx="52" ry="17" fill="none" stroke={leader ? '#b8720a' : '#5e6ab0'} stroke-width="1.600" />
      <ellipse cx="60" cy="24" rx="45" ry="13.500" fill="none" stroke={leader ? '#e0a020' : '#8d97d2'} stroke-width={leader ? 2.200 : 1.600} stroke-dasharray={empty ? '5 5' : undefined} />
      {leader && (
        <g transform="translate(60 24) scale(1 0.3)">
          <g class="fd-ring" fill="none" stroke="#d08a10">
            {Array.from({ length: 10 }, (_, i) => <path d={GLYPHS[i % GLYPHS.length]} stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round" transform={`rotate(${i * 36}) translate(0 -34) scale(1.700)`} />)}
          </g>
        </g>
      )}
      {empty && <path class="fd-plus" d="M60 16 V32 M46 24 H74" stroke={leader ? '#b8720a' : '#5e6ab0'} stroke-width="3.600" stroke-linecap="round" />}
    </svg>
  );
}

export function Board({ tired, team = 'main' }: { tired?: Set<number>; team?: TeamKind } = {}) {
  const s = useGame();
  const formation = formationOf(s, team);
  const [picked, setPicked] = useState<Slot | null>(null);
  const tap = (slot: Slot) => {
    if (picked === null) {
      if (formation.some(([, sl]) => sl === slot)) setPicked(slot);
      return;
    }
    if (picked !== slot) swapSlots(picked, slot, team);
    setPicked(null);
  };
  const leaderUid = formation.find(([, sl]) => sl === LEADER_SLOT)?.[0];
  const leader = leaderUid !== undefined ? heroByUid(s, leaderUid) : undefined;
  const chief = leader ? heroDef(leader.defId).talent : undefined;
  return (
    <div class="board-wrap">
      <div class="field">
        <FieldBackground />
        {([3, 0, 2, 4, 1] as Slot[]).map((slot) => {
          const uid = formation.find(([, sl]) => sl === slot)?.[0];
          const hero = uid !== undefined ? heroByUid(s, uid) : undefined;
          const [x, y] = POS[slot];
          return (
            <button
              class={`field-slot${picked === slot ? ' on' : ''}${slot === LEADER_SLOT ? ' leader' : ''}${hero ? '' : ' empty'}${hero && tired?.has(hero.uid) ? ' tired' : ''}`}
              style={{ left: `${(x / FIELD_W) * 100}%`, top: `${(y / FIELD_H) * 100}%`, zIndex: y }}
              onClick={() => tap(slot)}
            >
              <Plate leader={slot === LEADER_SLOT} empty={!hero} />
              {slot === LEADER_SLOT && (!hero || chief) && <Art name="crown" size={22} class="crown" />}
              {hero && <img src={heroImage(hero.defId)} alt="" />}
              {hero && <Stars stars={hero.stars} />}
            </button>
          );
        })}
      </div>
      {chief && <p class="leader-line"><Icon name="crown" size={18} /> {talentText(chief)}</p>}
    </div>
  );
}

export function Prep({ plan, team = 'main' }: { plan: BattlePlan | null; team?: TeamKind }) {
  const s = useGame();
  const formation = formationOf(s, team);
  const inTeam = new Set(formation.map(([u]) => u));
  const tired = new Set(plan?.exclude ?? []);
  // En guerre de guildes, les héros qui ont déjà attaqué aujourd'hui ne comptent pas.
  const mine = tired.size
    ? formation.filter(([u]) => !tired.has(u)).reduce((sum, [u]) => sum + heroPower(s, heroByUid(s, u)!), 0)
    : teamPower(s, team);
  const waves = plan?.waves ?? [];
  const look = plan ? battleLook(plan.kind, plan.title, plan.dungeon) : undefined;
  return (
    <div class="prep">
      <Backdrop kind="page" />
      <header class="prep-head">
        <button class="x" aria-label={t('close')} onClick={close}>‹</button>
        <h2>{plan ? `${t(`mode.${plan.kind}`)} ${plan.kind === 'dailyBoss' || plan.kind === 'guildBoss' ? t(`monster.${plan.title}`) : plan.title}` : team === 'defense' ? t('war.defense') : t('heroes.team')}</h2>
        <span class="power-chip"><Icon name="power" size={18} />{fmt(mine)}</span>
      </header>

      {plan && (
        <section class="prep-enemies">
          <div class="row between">
            <span class="muted small">{waves.length > 1 ? `${t('battle.wave')} ×${waves.length}` : ''}</span>
            {plan.need !== undefined && (
              <span class={`power-chip ${mine >= plan.need ? 'ok' : 'low'}`}><Icon name="power" size={16} />{fmt(plan.need)}</span>
            )}
          </div>
          <div class="enemy-row">
            {(waves[waves.length - 1] ?? []).map((u) => (
              <img class={u.boss ? 'boss' : ''} src={u.side === 'enemy' && u.defId.includes('-') ? heroImage(u.defId) : monsterImage(u.defId, u.element, look)} alt="" />
            ))}
          </div>
        </section>
      )}

      <Board tired={tired} team={team} />

      <div class="row between prep-bar">
        <strong>{t('heroes.team')} {formation.length} / {slotCount(s)}</strong>
        <Btn kind="ghost" small onClick={() => autoFormation([...tired], team)}>{t('heroes.autoTeam')}</Btn>
      </div>

      <div class="roster">
        {sortedHeroes(s).map((h) => (
          <HeroCard key={h.uid} hero={h} small power={heroPower(s, h)} selected={inTeam.has(h.uid)} dim={tired.has(h.uid)}
            onClick={() => {
              if (tired.has(h.uid) && !inTeam.has(h.uid)) return toast(t('war.tired'));
              const r = toggleInFormation(h.uid, team);
              if (r === 'full') toast(t('heroes.full'));
            }} />
        ))}
      </div>

      {plan && (
        <div class="prep-go">
          <Btn kind="green" wide class="btn-fight" onClick={() => {
            const req = startBattleFromPlan(plan);
            if (!req) return;
            close();
            startBattle(req);
          }}>{t('fight')}</Btn>
        </div>
      )}
    </div>
  );
}
