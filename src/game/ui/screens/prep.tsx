// Préparation d'un combat : les ennemis en haut, la section sur le plateau, les héros en bas.
// Toucher un héros = l'ajouter ou le retirer. Toucher deux postes = les échanger.
import { useState } from 'preact/hooks';
import { HERO_X } from '../../fight-view';
import { LEADER_SLOT, type Slot } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { heroImage, monsterImage } from '../../art';
import { ART_META } from '../../art-meta';
import { battleLook, type Terrain } from '../../look';
import { fmt, t } from '../../i18n';
import { autoFormation, startBattleFromPlan, swapSlots, toggleInFormation, type BattlePlan } from '../../state/actions';
import { formationOf, heroByUid, heroPower, slotCount, sortedHeroes, teamPower, type TeamKind } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Btn, HeroCard, Icon, Stars } from '../kit';
import { close, startBattle, toast } from '../nav';
import { talentText } from './hero-detail';

/**
 * Le plateau est la moitié du terrain de combat côté héros, avec les mêmes positions qu'au combat
 * (voir HERO_X et ROW_DY dans fight-view.ts) : l'avant est à droite, face aux ennemis.
 */
const FIELD_W = 420;
const FIELD_H = 330;
const FIELD_GROUND = 50;
/** Les rangées sont un peu resserrées (×0,85) pour laisser de la place à la liste des héros. */
const POS: Record<Slot, [number, number]> = { 3: [HERO_X[3], 76], 4: [HERO_X[4], 230], 2: [HERO_X[2], 153], 0: [HERO_X[0], 76], 1: [HERO_X[1], 230] };

function FieldBackground({ terrain }: { terrain?: Terrain }) {
  // Le décor du combat à venir : la moitié gauche du terrain (côté héros), l'arène à hauteur des postes.
  terrain ??= 'meadow';
  if (terrain) {
    const m = ART_META.terrains[terrain];
    return <div class="field-bg" style={{ backgroundImage: `url(art/t/${terrain}.jpg)`, backgroundSize: '171% auto', backgroundPosition: `0% ${Math.round(m.cy * 100 - 4)}%` }} />;
  }
  return (
    <svg class="field-bg" viewBox={`0 0 ${FIELD_W} ${FIELD_H}`} preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id="field-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b3a78" /><stop offset="1" stop-color="#6b5ca8" /></linearGradient>
        <linearGradient id="field-ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3d6b4a" /><stop offset="1" stop-color="#274a34" /></linearGradient>
      </defs>
      <rect width={FIELD_W} height={FIELD_GROUND + 30} fill="url(#field-sky)" />
      {[0, 1, 2, 3].map((i) => (
        <polygon fill="#4a5a9a" opacity="0.6"
          points={`${i * 150 - 40},${FIELD_GROUND + 10} ${i * 150 + 60},${FIELD_GROUND - 40 - (i % 2) * 22} ${i * 150 + 160},${FIELD_GROUND + 10}`} />
      ))}
      <rect y={FIELD_GROUND} width={FIELD_W} height={FIELD_H - FIELD_GROUND} fill="url(#field-ground)" />
      <ellipse cx={FIELD_W} cy={FIELD_GROUND + 153} rx="380" ry="150" fill="#fff" opacity="0.06" />
    </svg>
  );
}

export function Board({ tired, team = 'main', terrain }: { tired?: Set<number>; team?: TeamKind; terrain?: Terrain } = {}) {
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
        <FieldBackground terrain={terrain} />
        {([3, 0, 2, 4, 1] as Slot[]).map((slot) => {
          const uid = formation.find(([, sl]) => sl === slot)?.[0];
          const hero = uid !== undefined ? heroByUid(s, uid) : undefined;
          const [x, dy] = POS[slot];
          return (
            <button
              class={`field-slot${picked === slot ? ' on' : ''}${slot === LEADER_SLOT ? ' leader' : ''}${hero ? '' : ' empty'}${hero && tired?.has(hero.uid) ? ' tired' : ''}`}
              style={{ left: `${(x / FIELD_W) * 100}%`, top: `${((FIELD_GROUND + dy) / FIELD_H) * 100}%`, zIndex: dy }}
              onClick={() => tap(slot)}
            >
              <span class="field-spot" />
              {slot === LEADER_SLOT && (!hero || chief) && <Art name="crown" size={22} class="crown" />}
              {hero && <img src={heroImage(hero.defId)} alt="" />}
              {hero && <Stars stars={hero.stars} />}
            </button>
          );
        })}
        <span class="board-arrow">›</span>
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

      <Board tired={tired} team={team} terrain={look?.terrain} />

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
