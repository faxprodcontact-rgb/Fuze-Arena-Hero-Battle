// Préparation d'un combat : la section posée sur le sol du décor du combat à venir (formation-stage.tsx), les héros en
// bas (en entier, dans leurs cases), Combattre tout en bas.
// Toucher un héros en bas = l'ajouter ou le retirer. Toucher une place = la choisir (elle s'allume, une croix la vide) ;
// puis toucher un héros en bas = le poser là (il remplace celui qui y était), ou une autre place = les échanger.
import { useState } from 'preact/hooks';
import { LEADER_SLOT, type Slot } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { ELEMENT_COLOR } from '../../art';
import { FormationStage, Plate, STAGE_H, STAGE_POS, STAGE_W } from '../formation-stage';
import { battleLook, idleLook, type Clan } from '../../look';
import { HeroFigure } from '../hero-figure';
import { fmt, t } from '../../i18n';
import { autoFormation, placeInSlot, startBattleFromPlan, swapSlots, toggleInFormation, type BattlePlan } from '../../state/actions';
import { formationOf, heroByUid, heroPower, slotCount, sortedHeroes, teamPower, type TeamKind } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Btn, HeroCard, Icon, Sign, Stars } from '../kit';
import { close, startBattle, toast } from '../nav';
import { talentText } from './hero-detail';

export function Board({ tired, team = 'main', clan, picked, setPicked, ask }: {
  tired?: Set<number>; team?: TeamKind; clan?: Clan; picked: Slot | null; setPicked: (s: Slot | null) => void; ask?: boolean;
}) {
  const s = useGame();
  const formation = formationOf(s, team);
  const tap = (slot: Slot) => {
    if (picked === null) return setPicked(slot);
    if (picked !== slot) swapSlots(picked, slot, team);
    setPicked(null);
  };
  /** La croix d'une place choisie : retire son héros (il en reste toujours au moins un). */
  const out = (uid: number) => {
    if (toggleInFormation(uid, team) === 'last') toast(t('heroes.last'));
    setPicked(null);
  };
  const leaderUid = formation.find(([, sl]) => sl === LEADER_SLOT)?.[0];
  const leader = leaderUid !== undefined ? heroByUid(s, leaderUid) : undefined;
  const chief = leader ? heroDef(leader.defId).talent : undefined;
  return (
    <div class="board-wrap">
      <div class="field">
        <div class="field-art">
        <FormationStage clan={clan ?? idleLook(s.campaign.cleared + 1).fond} />
        {([3, 0, 2, 4, 1] as Slot[]).map((slot) => {
          const uid = formation.find(([, sl]) => sl === slot)?.[0];
          const hero = uid !== undefined ? heroByUid(s, uid) : undefined;
          const [x, y] = STAGE_POS[slot];
          return (
            <button
              class={`field-slot${picked === slot ? ' on' : ''}${ask && !hero ? ' ask' : ''}${ask && hero ? ' ask-full' : ''}${slot === LEADER_SLOT ? ' leader' : ''}${hero ? '' : ' empty'}${hero && tired?.has(hero.uid) ? ' tired' : ''}`}
              style={{ left: `${(x / STAGE_W) * 100}%`, top: `${(y / STAGE_H) * 100}%`, zIndex: y }}
              onClick={() => tap(slot)}
            >
              <Plate leader={slot === LEADER_SLOT} empty={!hero} color={hero ? ELEMENT_COLOR[heroDef(hero.defId).element] : undefined} />
              {slot === LEADER_SLOT && (!hero || chief) && <Art name="crown" size={22} class="crown" />}
              {hero && <span class="field-hero"><HeroFigure defId={hero.defId} /></span>}
              {hero && <Stars stars={hero.stars} />}
              {hero && picked === slot && (
                <span class="field-out" role="button" aria-label={t('heroes.inTeam')} onClick={(e) => { e.stopPropagation(); out(hero.uid); }}><Sign name="cross" /></span>
              )}
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
  const need = plan?.need;
  const [picked, setPicked] = useState<Slot | null>(null);
  const [ask, setAsk] = useState(false);
  const pick = (uid: number) => {
    // une place est choisie : le héros touché s'y pose (il remplace celui qui y était, ou change de place)
    if (picked !== null) {
      if (placeInSlot(uid, picked, team) === 'full') toast(t('heroes.full'));
      setPicked(null);
      return;
    }
    const r = toggleInFormation(uid, team);
    if (r === 'last') toast(t('heroes.last'));
    if (r === 'full') {
      // section pleine : les places s'allument pour montrer qu'on en choisit une à remplacer
      setAsk(true);
      setTimeout(() => setAsk(false), 1600);
      toast(t('heroes.pickSlot'));
    }
  };
  return (
    <div class={`prep prep-hall${plan ? ' prep-plan' : ''}`}>
      <div class="backdrop prep-bg" aria-hidden="true" />
      <header class="prep-head">
        <button class="x bt-rond bt-galet" aria-label={t('close')} onClick={close}>‹</button>
        <h2>{plan ? `${t(`mode.${plan.kind}`)} ${plan.kind === 'dailyBoss' || plan.kind === 'guildBoss' ? t(`monster.${plan.title}`) : plan.title}` : team === 'defense' ? t('war.defense') : t('heroes.formation')}</h2>
        <span class={`power-chip${need === undefined ? '' : mine >= need ? ' ok' : ' low'}`}>
          <Icon name="power" size={18} />{fmt(mine)}{need !== undefined && <small> / {fmt(need)}</small>}
        </span>
      </header>

      <Board tired={tired} team={team} picked={picked} setPicked={setPicked} ask={ask} clan={plan ? battleLook(plan.kind, plan.title, plan.dungeon).fond : undefined} />

      <div class="row between prep-bar">
        <strong>{t('heroes.team')} {formation.length} / {slotCount(s)}</strong>
        <Btn kind="ghost" small onClick={() => autoFormation([...tired], team)}>{t('heroes.autoTeam')}</Btn>
      </div>

      <div class="roster">
        {sortedHeroes(s).map((h) => (
          <HeroCard key={h.uid} hero={h} small power={heroPower(s, h)} selected={inTeam.has(h.uid)} dim={tired.has(h.uid)}
            onClick={() => {
              if (tired.has(h.uid) && !inTeam.has(h.uid)) return toast(t('war.tired'));
              pick(h.uid);
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
