// Accueil : la section se bat en continu (c'est elle qui remplit le butin).
// Sur les bords : quêtes, passe, offres, classement, tchat. En bas : coffre, Combattre, butin rapide.
import { loginCalendar, mailWaiting } from '../../state/actions';
import { useEffect, useRef } from 'preact/hooks';
import { stagePower } from '../../../core/data/campaign';
import { CAMPAIGN_STAGES, OFFLINE_CAP_HOURS, STAGES_PER_CHAPTER } from '../../../core/data/economy';
import { chapterElement, chapterOf, isBossStage, stageInChapter } from '../../../core/stages';
import { ELEMENT_COLOR } from '../../art';
import { runIdle } from '../../idle-scene';
import { regionChapters } from '../../look';
import { fmt, t } from '../../i18n';
import {
  adsLeft, campaignPlan, collectIdle, fastLoot, fastLootCost, idleSetup, watchAd,
} from '../../state/actions';
import { idlePreview, teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { dots } from '../dots';
import { Art, Btn, Cur, Icon, Modal, RedDot } from '../kit';
import { close, open, prepare } from '../nav';

function IdleStage({ running }: { running: boolean }) {
  const s = useGame();
  const host = useRef<HTMLDivElement>(null);
  // La scène redémarre quand la section ou le niveau changent.
  const key = `${s.campaign.cleared}|${s.formation.map(([u, sl]) => `${u}:${sl}`).join(',')}`;
  useEffect(() => {
    if (!running || !host.current) return;
    return runIdle(host.current, idleSetup);
  }, [running, key]);
  return <div class="idle-canvas" ref={host} />;
}

function EdgeButton({ icon, label, dot, onClick }: { icon: string; label: string; dot?: boolean; onClick: () => void }) {
  return (
    <button class="edge-btn" onClick={onClick}>
      <span class="edge-icon"><Icon name={icon} size={28} /></span>
      <span class="edge-label">{label}</span>
      {dot && <RedDot />}
    </button>
  );
}

export function CampaignScreen({ running }: { running: boolean }) {
  const s = useGame();
  const next = Math.min(s.campaign.cleared + 1, CAMPAIGN_STAGES);
  const done = s.campaign.cleared >= CAMPAIGN_STAGES;
  const chapter = chapterOf(next);
  const pos = stageInChapter(next);
  const need = stagePower(next);
  const mine = teamPower(s);
  const loot = idlePreview(s);
  const h = Math.floor(loot.hours);
  const m = Math.floor((loot.hours - h) * 60);

  return (
    <div class="home" style={{ '--el': ELEMENT_COLOR[chapterElement(chapter)] } as never}>
      <div class="stage">
        <IdleStage running={running} />
        <div class="stage-title">
          <button class="stage-chapter" onClick={() => open({ type: 'worldMap' })}><Icon name="campaign" size={20} /> {t('chapter')} {chapter}</button>
          <span class="stage-progress"><span style={{ width: `${((pos - 1) / STAGES_PER_CHAPTER) * 100}%` }} /></span>
        </div>
        <div class="edge edge-left">
          <EdgeButton icon="calendar" label={t('login.title')} dot={!loginCalendar(s).claimed} onClick={() => open({ type: 'login' })} />
          <EdgeButton icon="quests" label={t('side.quests')} dot={dots.quests(s)} onClick={() => open({ type: 'quests' })} />
          <EdgeButton icon="pass" label={t('side.pass')} dot={dots.pass(s)} onClick={() => open({ type: 'shop', tab: 'pass' })} />
          <EdgeButton icon="shop" label={t('shop.offers')} dot={!s.shop.bought.starter} onClick={() => open({ type: 'shop' })} />
        </div>
        <div class="edge edge-right">
          <EdgeButton icon="ranking" label={t('side.ranking')} onClick={() => open({ type: 'ranking' })} />
          <EdgeButton icon="chat" label={t('side.chat')} onClick={() => open({ type: 'chat' })} />
          <EdgeButton icon="mail" label={t('mail.title')} dot={mailWaiting(s) > 0} onClick={() => open({ type: 'mail' })} />
          <EdgeButton icon="friends" label={t('friends.title')} dot={s.friends.inbox.length > 0} onClick={() => open({ type: 'friends' })} />
        </div>
      </div>

      <div class="dock">
        <button class={`dock-chest${loot.hours >= 2 ? ' ready' : ''}${loot.full ? ' full' : ''}`}
          onClick={() => open({ type: 'gain', title: t('camp.loot'), gain: collectIdle() })}>
          <Art class="chest chest-art" name={loot.hours >= 2 ? 'chestOpen' : 'chestClosed'} />
          <span class="dock-time">{h} h {String(m).padStart(2, '0')}</span>
          <span class="dock-bar"><span style={{ width: `${(loot.hours / OFFLINE_CAP_HOURS) * 100}%` }} /></span>
          {loot.hours >= 2 && <RedDot />}
        </button>

        <button class={`dock-fight${s.campaign.cleared === 0 ? ' point' : ''}`} disabled={done} onClick={() => prepare(campaignPlan())}>
          <span class="dock-fight-label">{done ? t('camp.done') : t('fight')}</span>
          {!done && (
            <span class="dock-fight-stage">
              {chapter}-{pos}{isBossStage(next) ? ` · ${t('camp.boss')}` : ''}
            </span>
          )}
          {!done && (
            <span class={`dock-power ${mine >= need ? 'ok' : 'low'}`}>
              <Icon name="power" size={14} />{fmt(mine)} / {fmt(need)}
            </span>
          )}
        </button>

        <button class="dock-fast" onClick={() => open({ type: 'fastLoot' })}>
          <Art class="hourglass hourglass-art" name="hourglass" />
          <span class="dock-time">{t('camp.fast')}</span>
          {fastLootCost(s) === 0 && <RedDot />}
        </button>
      </div>
    </div>
  );
}

/** Butin rapide : 2 h de butin d'un coup (gratuit une fois par jour), ou +2 h avec une pub. */
export function FastLootModal() {
  const s = useGame();
  const cost = fastLootCost(s);
  const loot = idlePreview(s);
  const show = (gain: ReturnType<typeof fastLoot>, title: string) => {
    close();
    if (gain) open({ type: 'gain', title, gain });
  };
  return (
    <Modal title={t('camp.fast')}>
      <div class="row gap center-y">
        <Art class="hourglass hourglass-art big" name="hourglass" />
        <div class="grow">
          <strong>2 h</strong>
          <div class="row gap-s wrap">
            <Cur k="gold" n={loot.perHour * 2} />
            <Cur k="essence" n={loot.perHour} />
            <span class="cur"><Icon name="weapon" size={18} /> ×1</span>
          </div>
        </div>
      </div>
      <Btn kind="purple" wide disabled={cost === null || s.wallet.gems < (cost ?? 0)} onClick={() => show(fastLoot(), t('camp.fast'))}>
        {cost === 0 ? t('free') : cost === null ? '—' : <Cur k="gems" n={cost} />}
      </Btn>
      <Btn kind="ghost" wide disabled={adsLeft(s) <= 0} onClick={() => {
        const reward = () => show(watchAd('idle'), t('camp.adBoost'));
        if (s.shop.noAds) reward();
        else {
          close();
          open({ type: 'ad', onDone: reward });
        }
      }}>
        <Icon name="ad" size={20} /> {t('camp.adBoost')} · {t('left', { n: adsLeft(s) })}
      </Btn>
    </Modal>
  );
}

/** Place de chaque région sur la carte (public/art/ui/map.jpg), en fraction de l'image. */
const MAP_PINS: [number, number][] = [[0.12, 0.71], [0.375, 0.76], [0.62, 0.75], [0.86, 0.72], [0.86, 0.2], [0.62, 0.19], [0.375, 0.18], [0.135, 0.2]];

/** Carte des 8 régions de la campagne : celles finies, celle en cours (qui brille) et celles encore fermées. */
export function WorldMapModal() {
  const s = useGame();
  const cur = chapterOf(Math.min(s.campaign.cleared + 1, CAMPAIGN_STAGES));
  return (
    <Modal title={t('chapter')} wide>
      <div class="wmap" style={{ backgroundImage: 'url(art/ui/map.jpg)' }}>
        {regionChapters().map((r, i) => {
          const [x, y] = MAP_PINS[i]!;
          const state = cur > r.to ? 'done' : cur >= r.from ? 'here' : 'locked';
          return (
            <span class={`wmap-pin ${state}`} style={{ left: `${x * 100}%`, top: `${y * 100}%` }}>
              <span class="wmap-tag">{r.from === r.to ? r.from : `${r.from}-${r.to}`}</span>
            </span>
          );
        })}
      </div>
    </Modal>
  );
}
