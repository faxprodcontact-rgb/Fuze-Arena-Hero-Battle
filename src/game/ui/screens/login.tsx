// Calendrier de connexion : une case cochée par jour de connexion. Bienvenue (7 jours), puis 28 jours qui recommencent
// (montrés semaine par semaine). Refait le 26/11 (vague 3, « plus spectaculaire ») : gros pictos posés sur une lueur,
// la case du jour qui brille et respire, le 7e jour en vitrine (héros Légendaire en ombre dorée, ou pile de récompenses),
// et au moment de prendre : la récompense saute, s'envole, la coche tombe ; puis la fenêtre des gains (même action).
import { useEffect, useRef, useState } from 'preact/hooks';
import { HEROES } from '../../../core/data/heroes';
import type { LoginReward } from '../../../core/data/modes';
import { fmt, t } from '../../i18n';
import { claimLogin, loginCalendar, loginLegendChoices, loginNeedsChoice } from '../../state/actions';
import { now, useGame } from '../../state/store';
import { Art, Btn, HeroCard, Icon, Modal, Sign } from '../kit';
import { open, swap } from '../nav';
import { BqFigure, Sparkles } from '../sections/boutique-kit';
import { figMeta } from '../sections/hero-fig';
import '../sections/boutique.css';
import { resolveReward } from '../../state/selectors';
import { getState } from '../../state/store';

type DayState = 'done' | 'today' | 'next';

/** Le temps jusqu'à minuit (le jour suivant du calendrier), en « h:mm:ss ». */
function untilTomorrow(ms: number): string {
  const d = new Date(ms);
  const left = Math.max(0, new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1).getTime() - ms);
  const s = Math.floor(left / 1000);
  return `${Math.floor(s / 3600)}:${String(Math.floor(s / 60) % 60).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
}

/** Les monnaies d'une récompense (sans le héros Légendaire). */
function parts(r: LoginReward): [string, number][] {
  return Object.entries(resolveReward(getState(), r)).filter(([k, v]) => k !== 'legendary' && v) as [string, number][];
}

const WINGED = ['assassins-5', 'mages-11'];

/** Le héros Légendaire montré en ombre dorée : un que le joueur n'a pas encore, si possible. */
function mysteryHero(owned: Set<string>): string | undefined {
  // les silhouettes ailées d'abord (elles se lisent le mieux en ombre), puis les autres Légendaires
  const pool = HEROES.filter((h) => h.rarity === 'legendary' && figMeta(h.id))
    .sort((a, b) => Number(!WINGED.includes(a.id)) - Number(!WINGED.includes(b.id)));
  return (pool.find((h) => !owned.has(h.id)) ?? pool[0])?.id;
}

function DayTile({ n, r, state, burst }: { n: number; r: LoginReward; state: DayState; burst: boolean }) {
  const [[k, v] = ['gold', 0]] = parts(r);
  return (
    <div class={`lg-day lg-${state}${burst ? ' lg-burst' : ''}`}>
      <span class="lg-n">{n}</span>
      <span class="lg-stage">
        <i class="lg-glow" />
        <Art name={k} class="lg-art" />
        {state === 'today' && <Sparkles n={3} />}
      </span>
      <span class="lg-amt">{fmt(v)}</span>
      {state === 'done' && <span class="lg-check"><Sign name="check" k={2.2} /></span>}
      {burst && <><i class="lg-flash" /><Art name={k} class="lg-fly" /><Sparkles n={6} burst /></>}
    </div>
  );
}

function BigTile({ n, r, state, burst, hero }: { n: number; r: LoginReward; state: DayState; burst: boolean; hero?: string }) {
  const list = parts(r);
  const legend = !!r.legendary;
  return (
    <div class={`lg-day lg-big lg-${state}${burst ? ' lg-burst' : ''}`}>
      <span class="lg-n">{n}</span>
      <span class="lg-show">
        <i class="lg-glow" />
        {legend && hero ? <BqFigure id={hero} u={0.8} class="lg-mystery" />
          : list.map(([k], i) => <Art name={k} class={`lg-pile lg-pile-${i}`} />)}
        <Sparkles n={4} />
      </span>
      <span class="lg-prize">
        {legend ? (
          <>
            <span class="lg-rar">{t('rarity.legendary')}</span>
            <span class="lg-stars">{[0, 1, 2, 3, 4].map(() => <Sign name="star" k={2.6} />)}</span>
          </>
        ) : list.map(([k, v]) => <span class="lg-pill"><Icon name={k} size={30} /><b>{fmt(v)}</b></span>)}
      </span>
      {state === 'done' && <span class="lg-check"><Sign name="check" k={3} /></span>}
      {burst && <><i class="lg-flash" /><Sparkles n={8} burst /></>}
    </div>
  );
}

export function LoginModal() {
  const s = useGame();
  const cal = loginCalendar(s);
  const [burst, setBurst] = useState(-1);
  const [clock, setClock] = useState(now());
  const alive = useRef(true);
  useEffect(() => {
    const id = setInterval(() => setClock(now()), 1000);
    return () => { alive.current = false; clearInterval(id); };
  }, []);

  // Le mois se montre semaine par semaine (7 cases, la 7e en vitrine) ; la jauge du dessus suit tout le calendrier.
  const week = cal.kind === 'month' ? Math.floor(cal.index / 7) : 0;
  const first = week * 7;
  const days = cal.rewards.slice(first, first + 7);
  const doneCount = cal.index + (cal.claimed ? 1 : 0);
  const total = cal.rewards.length;
  const owned = new Set(s.heroes.map((h) => h.defId));
  const hero = mysteryHero(owned);
  const stateOf = (i: number): DayState => (i < cal.index || (i === cal.index && cal.claimed) ? 'done' : i === cal.index ? 'today' : 'next');

  const claim = () => {
    if (cal.claimed || burst >= 0) return;
    // le 7e jour de bienvenue : le joueur choisit son Légendaire (28/11)
    if (loginNeedsChoice()) { swap({ type: 'legendPick' }); return; }
    const index = cal.index;
    const gain = claimLogin();
    if (!gain) return;
    setBurst(index);
    const calm = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
    setTimeout(() => {
      const modal = { type: 'gain' as const, title: t(cal.kind === 'welcome' ? 'login.welcome' : 'login.title'), gain };
      if (alive.current) swap(modal); else open(modal);
    }, calm ? 0 : 1250);
  };

  return (
    <Modal title={t(cal.kind === 'welcome' ? 'login.welcome' : 'login.title')} wide center>
      <div class={`lg ${cal.kind}`}>
        <div class="lg-track">
          <span class="lg-count"><Icon name="calendar" size={26} /><b>{doneCount}</b><small>/ {total}</small></span>
          <span class="lg-bar">
            <i style={{ width: `${(doneCount / total) * 100}%` }} />
            {cal.kind === 'month' && [1, 2, 3, 4].map((w) => (
              <span class={`lg-node${doneCount >= w * 7 ? ' on' : ''}${w === week + 1 ? ' here' : ''}`} style={{ left: `${(w / 4) * 100}%` }}>
                <Art name={parts(cal.rewards[w * 7 - 1]!)[0]?.[0] ?? 'gift'} />
                {doneCount >= w * 7 && <Sign name="check" k={1.4} />}
              </span>
            ))}
          </span>
        </div>
        {cal.kind === 'month' && <div class="lg-week">{t('login.week', { n: week + 1 })}</div>}
        <div class="lg-grid">
          {days.slice(0, 6).map((r, j) => <DayTile n={first + j + 1} r={r} state={stateOf(first + j)} burst={burst === first + j} />)}
          {days[6] && <BigTile n={first + 7} r={days[6]} state={stateOf(first + 6)} burst={burst === first + 6} hero={hero} />}
        </div>
        {cal.claimed && burst < 0 ? (
          <Btn kind="gold" size="l" wide disabled class="lg-claim"><Icon name="clock" size={26} /> {untilTomorrow(clock)}</Btn>
        ) : (
          <Btn kind="gold" size="l" wide class="lg-claim" onClick={claim}><Icon name="gift" size={30} /> {t('claim')}</Btn>
        )}
      </div>
    </Modal>
  );
}

/** Le 7e jour de bienvenue : un Légendaire au choix (ceux qu'on n'a pas encore d'abord). */
export function LegendPickModal() {
  const s = useGame();
  const choices = loginLegendChoices(s);
  return (
    <Modal title={t('login.pick')} wide center>
      <div class="grid lg-pick">
        {choices.map((id) => (
          <HeroCard hero={{ uid: -1, defId: id, stars: 4, level: 1 }} onClick={() => {
            const gain = claimLogin(id);
            if (gain) swap({ type: 'gain', title: t('login.welcome'), gain });
          }} />
        ))}
      </div>
    </Modal>
  );
}
