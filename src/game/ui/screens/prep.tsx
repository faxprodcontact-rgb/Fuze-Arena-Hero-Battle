// Préparation d'un combat : les ennemis en haut, la section sur l'estrade de la salle des héros (formation-stage.tsx),
// les héros en bas.
// Toucher un héros = l'ajouter ou le retirer. Toucher deux postes = les échanger.
import { useState } from 'preact/hooks';
import { LEADER_SLOT, type Slot } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { ELEMENT_COLOR, heroImage, monsterImage } from '../../art';
import { battleLook } from '../../look';
import { FormationStage, Plate, STAGE_H, STAGE_POS, STAGE_W } from '../formation-stage';
import { HeroFigure } from '../hero-figure';
import { fmt, t } from '../../i18n';
import { autoFormation, startBattleFromPlan, swapSlots, toggleInFormation, type BattlePlan } from '../../state/actions';
import { formationOf, heroByUid, heroPower, slotCount, sortedHeroes, teamPower, type TeamKind } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Btn, HeroCard, Icon, Stars } from '../kit';
import { close, startBattle, toast } from '../nav';
import { talentText } from './hero-detail';

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
        <div class="field-art">
        <FormationStage />
        {([3, 0, 2, 4, 1] as Slot[]).map((slot) => {
          const uid = formation.find(([, sl]) => sl === slot)?.[0];
          const hero = uid !== undefined ? heroByUid(s, uid) : undefined;
          const [x, y] = STAGE_POS[slot];
          return (
            <button
              class={`field-slot${picked === slot ? ' on' : ''}${slot === LEADER_SLOT ? ' leader' : ''}${hero ? '' : ' empty'}${hero && tired?.has(hero.uid) ? ' tired' : ''}`}
              style={{ left: `${(x / STAGE_W) * 100}%`, top: `${(y / STAGE_H) * 100}%`, zIndex: y }}
              onClick={() => tap(slot)}
            >
              <Plate leader={slot === LEADER_SLOT} empty={!hero} color={hero ? ELEMENT_COLOR[heroDef(hero.defId).element] : undefined} />
              {slot === LEADER_SLOT && (!hero || chief) && <Art name="crown" size={22} class="crown" />}
              {hero && <span class="field-hero"><HeroFigure defId={hero.defId} /></span>}
              {hero && <Stars stars={hero.stars} />}
            </button>
          );
        })}
        </div>
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
    <div class={`prep prep-hall${plan ? ' prep-plan' : ''}`}>
      <div class="backdrop prep-bg" aria-hidden="true" />
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
