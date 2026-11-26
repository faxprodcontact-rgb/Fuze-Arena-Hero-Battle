// Un donjon : une échelle de niveaux. On combat le niveau suivant (obligatoire pour avancer),
// ou on « balaie » le dernier niveau gagné (récompense tout de suite, sans combat). 3 essais par jour.
// Style moderne : le décor du donjon en tête (grand picto, essais du jour), puis un chemin de niveaux (pastille numérotée
// reliée aux autres, carte claire, une seule action sur la carte qui en a une).
import '../sections/aventure.css';
import { sceneVar } from '../fond-image';
import { DUNGEON_CLAN } from '../../look';
import { DUNGEON_ATTEMPTS_PER_DAY, DUNGEON_LEVELS, type DungeonKind } from '../../../core/data/modes';
import { fmt, t } from '../../i18n';
import { dungeonAttemptsLeft, dungeonPlan, dungeonPower, dungeonRewardPreview, sweepDungeon } from '../../state/actions';
import { teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Btn, Cur, Icon, Page } from '../kit';
import { open, prepare } from '../nav';
import { DUNGEON_ART, Tries } from './adventure';

function Reward({ kind, level }: { kind: DungeonKind; level: number }) {
  const r = dungeonRewardPreview(kind, level);
  return (
    <span class="av-reward">
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
      <div class={`av-scene av-dhead dungeon-${kind}`} style={sceneVar(DUNGEON_CLAN[kind])}>
        <Art name={DUNGEON_ART[kind]} class="av-dhead-art" />
        <span class="av-dhead-side">
          <span class="av-chip">{t('dungeon.tries')}</span>
          <Tries left={left} max={DUNGEON_ATTEMPTS_PER_DAY} />
        </span>
      </div>
      <div class="av-ladder">
        {rows.map((level) => {
          const state = level > next ? 'locked' : level === next ? 'next' : level === done ? 'last' : 'old';
          const need = dungeonPower(level);
          return (
            <div class={`av-step ${state}`}>
              <span class="av-step-node">{state === 'locked' ? <Icon name="lock" size={18} /> : level}</span>
              <div class="av-step-card">
                <div class="av-step-main">
                  <strong>{t('dungeon.level', { n: level })}</strong>
                  <span class="av-step-info">
                    <span class={`av-power ${mine >= need ? 'ok' : 'low'}`}><Icon name="power" size={15} /><b>{fmt(need)}</b></span>
                    <Reward kind={kind} level={level} />
                  </span>
                </div>
                {state === 'next' && (
                  <Btn kind="green" small disabled={!left} onClick={() => { const p = dungeonPlan(kind); if (p) prepare(p); }}>{t('fight')}</Btn>
                )}
                {state === 'last' && (
                  <Btn kind="gold" small disabled={!left} onClick={() => {
                    const gain = sweepDungeon(kind);
                    if (gain) open({ type: 'gain', title: `${t(`dungeon.${kind}`)} · ${t('dungeon.level', { n: level })}`, gain });
                  }}>{t('dungeon.sweep')}</Btn>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Page>
  );
}
