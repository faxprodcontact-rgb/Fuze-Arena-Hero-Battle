// Héros : la section (5 postes) et toute la collection.
import { useState } from 'preact/hooks';
import { LEADER_SLOT, type Slot } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { FACTIONS, type Faction } from '../../../core/types';
import { FACTION_COLOR, heroImage } from '../../art';
import { t } from '../../i18n';
import { autoFormation, fuseAllSimple, swapSlots } from '../../state/actions';
import { heroByUid, heroPower, slotCount, sortedHeroes, teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, HeroCard, Icon, Stars } from '../kit';
import { open, toast } from '../nav';

/** Position des postes sur le plateau : l'avant est à droite, comme au combat. */
const BOARD: Record<Slot, [number, number]> = { 3: [0, 0], 4: [0, 1], 2: [1, 0.5], 0: [2, 0], 1: [2, 1] };

export function HeroesScreen() {
  const s = useGame();
  const [picked, setPicked] = useState<Slot | null>(null);
  const [faction, setFaction] = useState<Faction | 'all'>('all');
  const inTeam = new Set(s.formation.map(([u]) => u));
  const heroes = sortedHeroes(s).filter((h) => faction === 'all' || heroDef(h.defId).faction === faction);

  const tapSlot = (slot: Slot) => {
    if (picked === null) {
      if (s.formation.some(([, sl]) => sl === slot)) setPicked(slot);
      return;
    }
    if (picked !== slot) swapSlots(picked, slot);
    setPicked(null);
  };

  return (
    <div class="screen heroes">
      <section class="card">
        <div class="row between">
          <h2>{t('heroes.team')} {s.formation.length} / {slotCount(s)}</h2>
          <span class="power-chip"><Icon name="power" size={18} />{Math.round(teamPower(s)).toLocaleString('fr-FR')}</span>
        </div>
        <div class="board">
          {([0, 1, 2, 3, 4] as Slot[]).map((slot) => {
            const uid = s.formation.find(([, sl]) => sl === slot)?.[0];
            const hero = uid !== undefined ? heroByUid(s, uid) : undefined;
            const [col, row] = BOARD[slot];
            return (
              <button
                class={`board-slot${picked === slot ? ' on' : ''}${slot === LEADER_SLOT ? ' leader' : ''}`}
                style={{ left: `${8 + col * 31}%`, top: `${row * 50}%` }}
                onClick={() => tapSlot(slot)}
              >
                {slot === LEADER_SLOT && <span class="crown">♛</span>}
                {hero && <img src={heroImage(hero.defId)} alt="" />}
                {hero && <Stars stars={hero.stars} />}
              </button>
            );
          })}
          <span class="board-arrow">›</span>
        </div>
        <div class="row gap">
          <Btn kind="blue" small wide onClick={autoFormation}>{t('heroes.autoTeam')}</Btn>
          <Btn kind="gold" small wide onClick={() => toast(t('heroes.fused', { n: fuseAllSimple() }))}>{t('heroes.fuseAll')}</Btn>
        </div>
      </section>

      <div class="chips">
        <button class={`chip${faction === 'all' ? ' on' : ''}`} onClick={() => setFaction('all')}>{t('all')}</button>
        {FACTIONS.map((f) => (
          <button class={`chip${faction === f ? ' on' : ''}`} onClick={() => setFaction(f)}>
            <span class="chip-dot" style={{ background: FACTION_COLOR[f] }} />
            {t(`faction.${f}`)}
          </button>
        ))}
      </div>

      <div class="grid">
        {heroes.map((h) => (
          <HeroCard
            key={h.uid}
            hero={h}
            power={heroPower(s, h)}
            selected={inTeam.has(h.uid)}
            badge={s.formation.find(([u]) => u === h.uid)?.[1] === LEADER_SLOT ? '♛' : undefined}
            onClick={() => open({ type: 'hero', uid: h.uid })}
          />
        ))}
      </div>
    </div>
  );
}
