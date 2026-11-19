// Un donjon : une échelle de niveaux. On combat le niveau suivant (obligatoire pour avancer),
// ou on « balaie » le dernier niveau gagné (récompense tout de suite, sans combat). 3 essais par jour.
import { DUNGEON_ATTEMPTS_PER_DAY, DUNGEON_LEVELS, type DungeonKind } from '../../../core/data/modes';
import { fmt, t } from '../../i18n';
import { dungeonAttemptsLeft, dungeonPlan, dungeonPower, dungeonRewardPreview, sweepDungeon } from '../../state/actions';
import { teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, Icon, Page } from '../kit';
import { open, prepare } from '../nav';
import { DUNGEON_ICON } from './adventure';

function Reward({ kind, level }: { kind: DungeonKind; level: number }) {
  const r = dungeonRewardPreview(kind, level);
  return (
    <span class="row gap-s center-y">
      {r.gold !== undefined && <Cur k="gold" n={r.gold} />}
      {r.essence !== undefined && <Cur k="essence" n={r.essence} />}
      {r.items !== undefined && <span class="cur"><Icon name="weapon" size={18} /> ×{r.items}</span>}
    </span>
  );
}

export function DungeonPage({ kind }: { kind: DungeonKind }) {
  const s = useGame();
  const done = s.dungeons[kind];
  const next = done + 1;
  const left = dungeonAttemptsLeft(s, kind);
  const mine = teamPower(s);
  // Du haut vers le bas : les niveaux à venir (fermés), le prochain (à combattre), le dernier gagné (à balayer), les anciens.
  const rows = [next + 2, next + 1, next, done, done - 1].filter((l) => l >= 1 && l <= DUNGEON_LEVELS);

  return (
    <Page title={t(`dungeon.${kind}`)}>
      <div class={`dungeon-head dungeon-${kind}`}>
        <Icon name={DUNGEON_ICON[kind]} size={40} />
        <span class={`dungeon-tries big${left ? '' : ' none'}`}>{t('dungeon.tries')} {left} / {DUNGEON_ATTEMPTS_PER_DAY}</span>
      </div>
      <div class="dungeon-ladder">
        {rows.map((level) => {
          const state = level > next ? 'locked' : level === next ? 'next' : level === done ? 'last' : 'old';
          const need = dungeonPower(level);
          return (
            <div class={`dungeon-step ${state}`}>
              <div class="grow">
                <strong>{state === 'locked' && '🔒 '}{t('dungeon.level', { n: level })}</strong>
                <div class="row gap-s center-y">
                  <span class={`power-chip ${mine >= need ? 'ok' : 'low'}`}><Icon name="power" size={14} />{fmt(need)}</span>
                  <Reward kind={kind} level={level} />
                </div>
              </div>
              {state === 'next' && (
                <Btn kind="red" small disabled={!left} onClick={() => { const p = dungeonPlan(kind); if (p) prepare(p); }}>{t('fight')}</Btn>
              )}
              {state === 'last' && (
                <Btn kind="gold" small disabled={!left} onClick={() => {
                  const gain = sweepDungeon(kind);
                  if (gain) open({ type: 'gain', title: `${t(`dungeon.${kind}`)} · ${t('dungeon.level', { n: level })}`, gain });
                }}>» {t('dungeon.sweep')}</Btn>
              )}
            </div>
          );
        })}
      </div>
    </Page>
  );
}
