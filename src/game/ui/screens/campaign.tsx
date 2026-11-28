// Accueil : la section se bat en continu (c'est elle qui remplit le butin).
// Sur les bords : quêtes, passe, offres, classement, tchat. En bas : coffre, Combattre, butin rapide.
import { loginCalendar, mailWaiting } from '../../state/actions';
import type { ComponentChildren } from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';
import { stagePower } from '../../../core/data/campaign';
import { CAMPAIGN_STAGES, OFFLINE_CAP_HOURS, STAGES_PER_CHAPTER } from '../../../core/data/economy';
import { campaignElement, chapterOf, isBossStage, stageInChapter } from '../../../core/stages';
import { ELEMENT_COLOR } from '../../art';
import { runIdle } from '../../scenes';
import { fmt, t } from '../../i18n';
import {
  adsLeft, campaignPlan, collectIdle, fastLoot, fastLootCost, idleSetup, watchAd,
} from '../../state/actions';
import { idlePreview, teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { dots } from '../dots';
import { Art, Btn, Cur, Icon, Modal, RedDot } from '../kit';
import { ChapterMap } from '../world-map';
import { close, open, prepare } from '../nav';
import { BarArt, ChapterPlaque, Chevron, Medallion } from '../chrome';

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
      <Medallion size={50}><Icon name={icon} size={30} /></Medallion>
      <span class="edge-label">{label}</span>
      {dot && <RedDot />}
    </button>
  );
}

/**
 * Une colonne de boutons, repliable pour dégager le combat (demande du 26/11) : repliée (par défaut), il ne reste que sa
 * flèche, avec un point rouge si un des boutons en a un ; dépliée, les boutons descendent l'un sous l'autre sur un ruban
 * bleu foncé à demi transparent, reliés par un trait, et la flèche pour remonter passe en bas. Le choix est gardé sur le
 * téléphone.
 */
function EdgeColumn({ side, dot, children }: { side: 'left' | 'right'; dot: boolean; children: ComponentChildren }) {
  const key = `fuze-edge-${side}`;
  const [open, setOpen] = useState(() => { try { return localStorage.getItem(key) === '1'; } catch { return false; } });
  const toggle = () => {
    setOpen(!open);
    try { localStorage.setItem(key, open ? '0' : '1'); } catch { /* sans mémoire, la colonne se replie au prochain lancement */ }
  };
  return (
    <div class={`edge edge-${side}${open ? ' open' : ''}`}>
      <span class="edge-ribbon" aria-hidden="true"><span class="edge-line" /></span>
      <div class="edge-list" aria-hidden={!open} inert={!open}><div class="edge-list-in">{children}</div></div>
      <button class="edge-toggle" aria-expanded={open} aria-label={t(open ? 'edge.fold' : 'edge.unfold')} onClick={toggle}>
        <Medallion size={38}><Chevron up={open} /></Medallion>
        {!open && dot && <RedDot />}
      </button>
    </div>
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
  const leftDots = [!loginCalendar(s).claimed, dots.quests(s), dots.pass(s), !s.shop.bought.starter];
  const rightDots = [mailWaiting(s) > 0, s.friends.inbox.length > 0];

  return (
    <div class="home" style={{ '--el': ELEMENT_COLOR[campaignElement(chapter)] } as never}>
      <div class="stage">
        <IdleStage running={running} />
        <button class="stage-title" aria-label={`${t('chapter')} ${chapter}`} onClick={() => open({ type: 'worldMap' })}>
          <ChapterPlaque title={`${t('chapter')} ${chapter}`} progress={(pos - 1) / STAGES_PER_CHAPTER} icon={<Icon name="campaign" size={22} />} />
        </button>
        <EdgeColumn side="left" dot={leftDots.some(Boolean)}>
          <EdgeButton icon="calendar" label={t('login.title')} dot={leftDots[0]} onClick={() => open({ type: 'login' })} />
          <EdgeButton icon="quests" label={t('side.quests')} dot={leftDots[1]} onClick={() => open({ type: 'quests' })} />
          <EdgeButton icon="pass" label={t('side.pass')} dot={leftDots[2]} onClick={() => open({ type: 'shop', tab: 'pass' })} />
          <EdgeButton icon="shop" label={t('shop.offers')} dot={leftDots[3]} onClick={() => open({ type: 'shop' })} />
        </EdgeColumn>
        <EdgeColumn side="right" dot={rightDots.some(Boolean)}>
          <EdgeButton icon="ranking" label={t('side.ranking')} onClick={() => open({ type: 'ranking' })} />
          <EdgeButton icon="chat" label={t('side.chat')} onClick={() => open({ type: 'chat' })} />
          <EdgeButton icon="mail" label={t('mail.title')} dot={rightDots[0]} onClick={() => open({ type: 'mail' })} />
          <EdgeButton icon="friends" label={t('friends.title')} dot={rightDots[1]} onClick={() => open({ type: 'friends' })} />
        </EdgeColumn>
      </div>

      <div class="dock">
        <button class={`dock-chest${loot.hours >= 2 ? ' ready' : ''}${loot.full ? ' full' : ''}`}
          onClick={() => open({ type: 'gain', title: t('camp.loot'), gain: collectIdle() })}>
          <span class="dock-pic"><Icon name={loot.full ? 'chestOpen' : loot.hours >= 2 ? 'chestReady' : 'chestClosed'} size={62} /></span>
          <span class="dock-time">{h} h {String(m).padStart(2, '0')}</span>
          <span class="dock-bar"><span style={{ width: `${(loot.hours / OFFLINE_CAP_HOURS) * 100}%` }} /></span>
          {loot.hours >= 2 && <RedDot />}
        </button>

        <button class="dock-fight bt bt-basalte bt-xxl" disabled={done} onClick={() => prepare(campaignPlan())}>
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

        <button class="dock-fast" aria-label={t('camp.fast')} onClick={() => open({ type: 'fastLoot' })}>
          {/* même hauteur que le coffre (son dessin remplit toute sa case, celui du coffre les trois quarts) ; plus de libellé */}
          <span class="dock-pic"><HourglassLive /></span>
          {fastLootCost(s) === 0 && <RedDot />}
        </button>
        <BarArt kind="dock" />
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
      <div class="fast-hero">
        <Icon name="hourglass" size={64} />
        <div class="fast-gain grow">
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

/** La carte de la campagne : les 8 régions sur un chemin, celle en cours brille (dessin : ui/world-map.tsx). */
export function WorldMapModal() {
  const s = useGame();
  const cur = chapterOf(Math.min(s.campaign.cleared + 1, CAMPAIGN_STAGES));
  return (
    <Modal title={`${t('chapter')} ${cur}`} wide>
      <ChapterMap cur={cur} />
    </Modal>
  );
}

/**
 * Le sablier du butin rapide, vivant (27/11 : « son animation, c'est juste le sable qui coule ; il arrête de se
 * retourner ») : le même dessin que le picto `hourglass` (socle et chapeau de basalte cerclés d'or, montants d'or, verre
 * ambré) ; seul le sable bouge : le filet tombe grain à grain, le haut baisse, le tas du bas monte (style.css, .hg-*).
 */
function HourglassLive() {
  const glass = 'M31 19H69Q68 30 66 37Q60 45 54 50Q60 55 66 63Q68 70 69 81H31Q32 70 34 63Q40 55 46 50Q40 45 34 37Q32 30 31 19Z';
  return (
    <svg class="hg" viewBox="0 0 100 100" width="46" height="46" aria-hidden="true">
      <defs>
        <radialGradient id="hg-glow" cx="50" cy="70" r="34" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffc94d" stop-opacity="0.55" /><stop offset="1" stop-color="#ffc94d" stop-opacity="0" /></radialGradient>
        <linearGradient id="hg-glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff8e6" /><stop offset="0.55" stop-color="#e9dcc2" /><stop offset="1" stop-color="#b9a98c" /></linearGradient>
        <linearGradient id="hg-gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b8701a" /><stop offset="0.5" stop-color="#ffd86a" /><stop offset="1" stop-color="#e0961f" /></linearGradient>
        <linearGradient id="hg-stone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6a6788" /><stop offset="1" stop-color="#2e2c47" /></linearGradient>
        <clipPath id="hg-in"><path d={glass} /></clipPath>
        <clipPath id="hg-up"><rect x="0" y="0" width="100" height="49" /></clipPath>
      </defs>
      <ellipse cx="50" cy="70" rx="34" ry="28" fill="url(#hg-glow)" />
      <path d={glass} fill="url(#hg-glass)" stroke="#2a1f33" stroke-width="2.6" stroke-linejoin="round" />
      <g clip-path="url(#hg-in)">
        <g clip-path="url(#hg-up)"><g class="hg-top"><path d="M28 30H72V52H28Z" fill="#ffcf3a" /><path d="M28 30H72V32.5H28Z" fill="#fff0a8" opacity="0.8" /></g></g>
        <path class="hg-stream" d="M50 47V80" stroke="#ffcf3a" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="3 2.4" />
        <g class="hg-bottom"><path d="M28 82H72L66 71Q50 58 34 71Z" fill="#f6a417" /><path d="M40 81H61L58 73Q50 65 43 73Z" fill="#ffe58a" opacity="0.8" /></g>
      </g>
      <path d="M61 24Q63 30 61 35" stroke="#fff" stroke-width="2.2" stroke-linecap="round" fill="none" opacity="0.8" />
      {[23, 77].map((x) => <rect x={x - 3.5} y="15" width="7" height="70" rx="3.5" fill="url(#hg-gold)" stroke="#2a1f33" stroke-width="1.6" />)}
      {[[5, 17], [82, 78]].map(([y, rim]) => (
        <g><rect x="13" y={y} width="74" height="13" rx="6.5" fill="url(#hg-stone)" stroke="#2a1f33" stroke-width="2" />
          <rect x="18" y={rim} width="64" height="5.5" rx="2.7" fill="url(#hg-gold)" /></g>
      ))}
      {[11.5, 88.5].map((y) => <circle cx="50" cy={y} r="3.4" fill="#f29a12" stroke="#7a3d06" stroke-width="1" />)}
    </svg>
  );
}

