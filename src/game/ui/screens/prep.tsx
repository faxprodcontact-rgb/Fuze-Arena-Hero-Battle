// Préparation d'un combat : les ennemis en haut, la section sur le plateau, les héros en bas.
// Toucher un héros = l'ajouter ou le retirer. Toucher deux postes = les échanger.
import { useState } from 'preact/hooks';
import { LEADER_SLOT, type Slot } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { heroImage, monsterImage } from '../../art';
import { fmt, t } from '../../i18n';
import { autoFormation, startBattleFromPlan, swapSlots, toggleInFormation, type BattlePlan } from '../../state/actions';
import { heroByUid, heroPower, slotCount, sortedHeroes, teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, HeroCard, Icon, Stars } from '../kit';
import { close, startBattle, toast } from '../nav';
import { talentText } from './hero-detail';

/** Position des postes sur le plateau : l'avant est à droite, comme au combat. */
const BOARD: Record<Slot, [number, number]> = { 3: [0, 0], 4: [0, 1], 2: [1, 0.5], 0: [2, 0], 1: [2, 1] };

export function Board() {
  const s = useGame();
  const [picked, setPicked] = useState<Slot | null>(null);
  const tap = (slot: Slot) => {
    if (picked === null) {
      if (s.formation.some(([, sl]) => sl === slot)) setPicked(slot);
      return;
    }
    if (picked !== slot) swapSlots(picked, slot);
    setPicked(null);
  };
  const leaderUid = s.formation.find(([, sl]) => sl === LEADER_SLOT)?.[0];
  const leader = leaderUid !== undefined ? heroByUid(s, leaderUid) : undefined;
  return (
    <div class="board-wrap">
      <div class="board">
        {([0, 1, 2, 3, 4] as Slot[]).map((slot) => {
          const uid = s.formation.find(([, sl]) => sl === slot)?.[0];
          const hero = uid !== undefined ? heroByUid(s, uid) : undefined;
          const [col, row] = BOARD[slot];
          return (
            <button
              class={`board-slot${picked === slot ? ' on' : ''}${slot === LEADER_SLOT ? ' leader' : ''}`}
              style={{ left: `${6 + col * 30}%`, top: `${row * 50}%` }}
              onClick={() => tap(slot)}
            >
              {slot === LEADER_SLOT && <span class="crown">♛</span>}
              {hero && <img src={heroImage(hero.defId)} alt="" />}
              {hero && <Stars stars={hero.stars} />}
            </button>
          );
        })}
        <span class="board-arrow">›</span>
      </div>
      {leader && <p class="leader-line">♛ {talentText(heroDef(leader.defId).talent)}</p>}
    </div>
  );
}

export function Prep({ plan }: { plan: BattlePlan | null }) {
  const s = useGame();
  const inTeam = new Set(s.formation.map(([u]) => u));
  const mine = teamPower(s);
  const waves = plan?.waves ?? [];
  return (
    <div class="prep">
      <header class="prep-head">
        <button class="x" aria-label={t('close')} onClick={close}>‹</button>
        <h2>{plan ? `${t(`mode.${plan.kind}`)} ${plan.kind === 'dailyBoss' || plan.kind === 'guildBoss' ? t(`monster.${plan.title}`) : plan.title}` : t('heroes.team')}</h2>
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
              <img class={u.boss ? 'boss' : ''} src={u.side === 'enemy' && u.defId.includes('-') ? heroImage(u.defId) : monsterImage(u.defId, u.element)} alt="" />
            ))}
          </div>
        </section>
      )}

      <Board />

      <div class="row between prep-bar">
        <strong>{t('heroes.team')} {s.formation.length} / {slotCount(s)}</strong>
        <Btn kind="ghost" small onClick={autoFormation}>{t('heroes.autoTeam')}</Btn>
      </div>

      <div class="roster">
        {sortedHeroes(s).map((h) => (
          <HeroCard key={h.uid} hero={h} small power={heroPower(s, h)} selected={inTeam.has(h.uid)}
            onClick={() => {
              const r = toggleInFormation(h.uid);
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
