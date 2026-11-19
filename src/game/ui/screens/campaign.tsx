// Campagne : le prochain combat, la progression du chapitre et le butin hors ligne.
import { stagePower } from '../../../core/data/campaign';
import { CAMPAIGN_STAGES, OFFLINE_CAP_HOURS, STAGES_PER_CHAPTER } from '../../../core/data/economy';
import { campaignWaves, chapterElement, chapterOf, isBossStage, stageInChapter } from '../../../core/stages';
import { ELEMENT_COLOR, heroImage, monsterImage } from '../../art';
import { fmt, t } from '../../i18n';
import { adsLeft, campaignBattle, collectIdle, fastLoot, fastLootCost, watchAd } from '../../state/actions';
import { idlePreview, teamHeroes, teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Bar, Btn, Cur, Icon } from '../kit';
import { open, startBattle } from '../nav';

export function CampaignScreen() {
  const s = useGame();
  const next = Math.min(s.campaign.cleared + 1, CAMPAIGN_STAGES);
  const done = s.campaign.cleared >= CAMPAIGN_STAGES;
  const chapter = chapterOf(next);
  const pos = stageInChapter(next);
  const need = stagePower(next);
  const mine = teamPower(s);
  const firstWave = campaignWaves(next)[0] ?? [];
  const loot = idlePreview(s);
  const fastCost = fastLootCost(s);

  const showGain = (gain: ReturnType<typeof collectIdle> | null, title: string) => {
    if (gain) open({ type: 'gain', title, gain });
  };

  return (
    <div class="screen campaign">
      <section class="card chapter" style={{ '--el': ELEMENT_COLOR[chapterElement(chapter)] } as never}>
        <div class="chapter-head">
          <h1>{t('chapter')} {chapter}</h1>
          <span class="stage-tag">{chapter}-{pos}{isBossStage(next) ? ` · ${t('camp.boss')}` : ''}</span>
        </div>
        <Bar value={pos - 1} max={STAGES_PER_CHAPTER} color="var(--gold)" label={`${pos - 1} / ${STAGES_PER_CHAPTER}`} />

        <div class="versus">
          <div class="versus-side">
            {teamHeroes(s).map(({ hero }) => <img key={hero.uid} src={heroImage(hero.defId)} alt="" />)}
          </div>
          <span class="vs">VS</span>
          <div class="versus-side foes">
            {firstWave.map((u) => <img key={u.id} src={monsterImage(u.defId, u.element)} alt="" class={u.boss ? 'boss' : ''} />)}
          </div>
        </div>

        <div class={`power-line ${mine >= need ? 'ok' : 'low'}`}>
          <Icon name="power" size={20} />
          <strong>{fmt(mine)}</strong>
          <span class="muted">/ {fmt(need)}</span>
        </div>

        {done ? (
          <p class="center gold-text">{t('camp.done')}</p>
        ) : (
          <Btn kind="green" wide class={`btn-fight${s.campaign.cleared === 0 ? ' point' : ''}`} onClick={() => startBattle(campaignBattle())}>
            {t('fight')} · {chapter}-{pos}
          </Btn>
        )}
      </section>

      <section class="card loot">
        <div class="loot-head">
          <div class={`chest${loot.full ? ' chest-full' : ''}`} />
          <div class="loot-info">
            <h2>{t('camp.loot')}</h2>
            <Bar value={loot.hours} max={OFFLINE_CAP_HOURS} color="#4fd1ff" label={`${loot.hours.toFixed(1)} h / ${OFFLINE_CAP_HOURS} h`} />
            <div class="row gap wrap">
              <Cur k="gold" n={loot.gold} />
              <Cur k="essence" n={loot.essence} />
              {loot.items > 0 && <span class="cur">⚔ ×{loot.items}</span>}
            </div>
            <span class="muted small">
              <Cur k="gold" n={loot.perHour} /> {t('camp.perHour')}
            </span>
          </div>
        </div>
        <Btn kind="gold" wide dot={loot.hours >= 2} onClick={() => showGain(collectIdle(), t('camp.loot'))}>{t('collect')}</Btn>
        <div class="row gap">
          <Btn
            kind="purple"
            small
            wide
            disabled={fastCost === null || s.wallet.gems < (fastCost ?? 0)}
            dot={fastCost === 0}
            onClick={() => showGain(fastLoot(), t('camp.fast'))}
          >
            {t('camp.fast')} {fastCost === 0 ? `· ${t('free')}` : fastCost !== null ? <Cur k="gems" n={fastCost} /> : ''}
          </Btn>
          <Btn
            kind="ghost"
            small
            disabled={adsLeft(s) <= 0}
            onClick={() => {
              const reward = () => showGain(watchAd('idle'), t('camp.adBoost'));
              if (s.shop.noAds) reward();
              else open({ type: 'ad', onDone: reward });
            }}
          >
            <Icon name="ad" size={18} /> {t('camp.adBoost')}
          </Btn>
        </div>
      </section>
    </div>
  );
}
