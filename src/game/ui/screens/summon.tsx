// Invocations : normale (parchemins ou gemmes), simple (Communs et Rares), fragments, et révélation.
import { BASIC_SUMMON_RATES, LEGENDARY_PITY, SUMMON_RATES } from '../../../core/data/summon';
import { HEROES, heroDef } from '../../../core/data/heroes';
import { FRAGMENTS_PER_COPY } from '../../../core/data/stars';
import { RARITIES, type Hero } from '../../../core/types';
import { RARITY_COLOR, heroImage } from '../../art';
import { useEffect, useLayoutEffect, useRef, useState } from 'preact/hooks';
import { fmt, t } from '../../i18n';
import { SummonBackdrop } from '../backdrop-summon';
import { SummonStage } from '../summon-stage';
import { Medallion } from '../chrome';
import { CardBack, RUNES } from '../card-back';
import { Halo } from '../anim';
import { spark } from '../portal';
import { TitleBanner } from '../title-banner';
import { adsLeft, claimFragments, newlyFound, summon, summonCost, watchAd } from '../../state/actions';
import { useGame } from '../../state/store';
import { Bar, Btn, Cur, HeroCard, Icon, Modal, Stars } from '../kit';
import { close, open } from '../nav';

type Kind = 'normal' | 'basic';

/** Un médaillon du bord de la scène : un picto cerclé d'or, un chiffre ou un mot dessous. */
function Medal({ icon, label, on, dot, onClick }: { icon: string; label: string; on?: boolean; dot?: boolean; onClick: () => void }) {
  return (
    <button class={`sum-med${on ? ' on' : ''}`} onClick={onClick}>
      <Medallion size={50} class="sum-med-icon"><Icon name={icon} size={30} /></Medallion>
      <span class="sum-med-label">{label}</span>
      {dot && <span class="dot" />}
    </button>
  );
}

export function SummonScreen() {
  const s = useGame();
  const [kind, setKind] = useState<Kind>('normal');
  // L'invocation est décidée tout de suite (le coût est payé), puis le portail s'emballe un instant avant la révélation.
  const [casting, setCasting] = useState(false);
  const cast = (heroes: Hero[] | null | undefined) => {
    if (!heroes) return;
    setCasting(true);
    setTimeout(() => { setCasting(false); open({ type: 'summon', heroes }); }, 1050);
  };
  const button = (count: 1 | 10) => {
    const cost = summonCost(kind, count);
    return (
      <button
        class={`sum-btn sum-btn-${count}${kind === 'normal' && count === 10 ? ' tuto-summon10' : ''}`}
        disabled={s.wallet[cost.currency] < cost.amount}
        onClick={() => cast(summon(kind, count))}
      >
        <span class="sum-btn-n">{t(`summon.x${count}`)}</span>
        <Cur k={cost.currency} n={cost.amount} />
      </button>
    );
  };
  // Seulement les héros dont on a des fragments : on ne dévoile jamais un héros pas encore rencontré.
  const owned = Object.entries(s.fragments).filter(([, n]) => n > 0);
  const left = LEGENDARY_PITY - s.summon.pity;
  return (
    <div class={`screen summon sum-kind-${kind}${casting ? ' sum-casting' : ''}`}>
      <div class="sum-title">
        <h1 class="sr-only">{t('summon.normal')}</h1>
        <TitleBanner title={t(`summon.${kind}`)} ribbon={kind === 'normal' ? ['#a565f0', '#5f2fb4', '#2f1466'] : ['#5aa8f0', '#2a5fb5', '#16356e']} />
      </div>

      <div class="sum-stage">
        <SummonStage kind={kind} casting={casting} />
        {/* à gauche : les deux portails (on voit combien de parchemins il reste pour chacun) */}
        <div class="sum-side sum-left">
          <Medal icon="scrolls" label={fmt(s.wallet.scrolls)} on={kind === 'normal'} onClick={() => setKind('normal')} />
          <Medal icon="basicScrolls" label={fmt(s.wallet.basicScrolls)} on={kind === 'basic'} onClick={() => setKind('basic')} />
        </div>
        {/* à droite : les chances, et les fragments quand on en a */}
        <div class="sum-side sum-right">
          <Medal icon="star" label={t('summon.odds')} onClick={() => open({ type: 'odds' })} />
          {owned.length > 0 && <Medal icon="fragments" label={t('summon.fragments')} dot={owned.some(([, n]) => n >= FRAGMENTS_PER_COPY)} onClick={() => open({ type: 'fragments' })} />}
        </div>
      </div>

      <div class="sum-panel">
        {kind === 'normal' && (
          <div class="sum-pity">
            <Icon name="star" size={22} />
            <div class="sum-pity-bar"><span style={{ width: `${(s.summon.pity / LEGENDARY_PITY) * 100}%` }} /></div>
            <strong>{left}</strong>
          </div>
        )}
        <div class="sum-buttons">{button(1)}{button(10)}</div>
        {kind === 'normal' && (
          <button
            class="sum-free"
            disabled={adsLeft(s) <= 0}
            onClick={() => {
              const go = () => cast(watchAd('summon')?.heroes);
              if (s.shop.noAds) go();
              else open({ type: 'ad', onDone: go });
            }}
          >
            <Icon name="ad" size={18} /> {t('summon.adFree')}
          </button>
        )}
      </div>
    </div>
  );
}

/** Les fragments : une copie du héros dès qu'on en a assez. */
export function FragmentsModal() {
  const s = useGame();
  const owned = Object.entries(s.fragments).filter(([, n]) => n > 0);
  return (
    <Modal title={t('summon.fragments')}>
      {owned.map(([defId, n]) => (
        <div class="row gap center-y frag-row">
          <img class="frag-img" src={heroImage(defId)} alt="" />
          <div class="grow">
            <strong>{heroDef(defId).name}</strong>
            <Bar value={n} max={FRAGMENTS_PER_COPY} color="var(--gold)" label={`${n} / ${FRAGMENTS_PER_COPY}`} />
          </div>
          <Btn kind="gold" small disabled={n < FRAGMENTS_PER_COPY} onClick={() => {
            const h = claimFragments(defId);
            if (h) { close(); open({ type: 'summon', heroes: [h] }); }
          }}>{t('summon.copy')}</Btn>
        </div>
      ))}
    </Modal>
  );
}

/** Les couleurs des impacts du tirage, de la plus commune à la plus rare (l'argent plus vif que le gris des cartes). */
const TEASE = ['#dfe6f5', '#4d9bff', '#b06bff', '#ffc94a'];
/**
 * Le rythme du tirage (ms) : la boule se charge, un impact par rareté gagnée, puis elle tient la couleur atteinte (plus
 * longtemps pour une belle rareté) et éclate ; les cartes en jaillissent, puis se retournent l'une après l'autre.
 */
const FIRST_MS = 420, STEP_MS = 700, HOLD_MS = [600, 750, 900, 1100], DEAL_MS = 700, FLIP_GAP = 130, BEST_PAUSE = 650, FLIP_MS = 640;

/** Un éclair qui crépite autour de la boule (à partir de l'Épique) : une ligne brisée de r0 à r1, dans la direction a. */
function bolt(a: number, r0: number, r1: number, seed: number): string {
  const pts: string[] = [];
  for (let k = 0; k <= 5; k++) {
    const r = r0 + ((r1 - r0) * k) / 5;
    const off = k === 0 || k === 5 ? 0 : (((seed * 7 + k * 13) % 9) - 4) * 0.055;
    pts.push(`${(100 + Math.cos(a + off) * r).toFixed(1)} ${(100 + Math.sin(a + off) * r).toFixed(1)}`);
  }
  return `M${pts.join(' L')}`;
}

/**
 * La boule de magie du tirage : un halo, de la lumière aspirée vers le centre, un anneau de signes et une couronne de perles
 * qui tournent en sens contraires, la sphère et ses bras, trois éclats en orbite ; des éclairs à partir de l'Épique.
 * Toutes ses couleurs suivent `--tc`, la couleur de la rareté atteinte (elle change à chaque impact).
 */
function TeaseOrb() {
  const arm = (k: number) => `M100 100 Q${100 + Math.cos(k) * 30} ${100 + Math.sin(k) * 30} ${100 + Math.cos(k + 1.4) * 34} ${100 + Math.sin(k + 1.4) * 34} Q${100 + Math.cos(k + 0.9) * 18} ${100 + Math.sin(k + 0.9) * 18} 100 100 Z`;
  const tc = { stopColor: 'var(--tc)' };
  return (
    <svg class="tease-orb" viewBox="0 0 200 200" aria-hidden="true">
      <defs>
        <radialGradient id="to-glow"><stop offset="0" style={tc} stop-opacity="0.95" /><stop offset="0.42" style={tc} stop-opacity="0.34" /><stop offset="1" style={tc} stop-opacity="0" /></radialGradient>
        <radialGradient id="to-ball" cx="0.42" cy="0.38" r="0.62"><stop offset="0" stop-color="#ffffff" /><stop offset="0.35" style={tc} /><stop offset="1" stop-color="#140c3a" /></radialGradient>
        <clipPath id="to-clip"><circle cx="100" cy="100" r="36" /></clipPath>
      </defs>
      <circle class="to-breathe" cx="100" cy="100" r="98" fill="url(#to-glow)" />
      {/* la lumière aspirée vers le centre */}
      <g class="to-suck">
        {Array.from({ length: 14 }, (_, i) => (
          <circle class="to-p" cx="100" cy="100" r={1.6 + (i % 3) * 0.7} fill="#fff"
            style={{ '--a': `${(i * 137.5) % 360}deg`, animationDelay: `${(-(i * 0.37) % 1.3).toFixed(2)}s` } as never} />
        ))}
      </g>
      {/* la couronne de perles, l'anneau de signes */}
      <g class="to-beads">{Array.from({ length: 28 }, (_, i) => {
        const a = (i / 28) * Math.PI * 2;
        return <circle cx={(100 + Math.cos(a) * 74).toFixed(1)} cy={(100 + Math.sin(a) * 74).toFixed(1)} r={i % 7 === 0 ? 2.6 : 1.3} fill="#fff" opacity={i % 7 === 0 ? 1 : 0.6} />;
      })}</g>
      <g class="to-ring">
        <circle cx="100" cy="100" r="64" fill="none" style={{ stroke: 'var(--tc)' }} stroke-width="2.2" opacity="0.9" />
        <circle cx="100" cy="100" r="52" fill="none" stroke="#fff" stroke-width="1" opacity="0.55" />
        {RUNES.map((d, i) => {
          const a = (i / RUNES.length) * Math.PI * 2;
          return <path d={d} transform={`translate(${(100 + Math.cos(a) * 58).toFixed(1)} ${(100 + Math.sin(a) * 58).toFixed(1)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(0.95)`} fill="none" style={{ stroke: 'var(--tc)' }} stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />;
        })}
      </g>
      {/* les éclairs (Épique et Légendaire) */}
      <g class="to-arcs">{[0.3, 1.9, 3.4, 4.9].map((a, i) => (
        <path class="to-arc" d={bolt(a, 40, 70, i + 1)} fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" style={{ animationDelay: `${i * 0.13}s` }} />
      ))}</g>
      <circle cx="100" cy="100" r="38.5" fill="#0c0824" />
      <circle cx="100" cy="100" r="36" fill="url(#to-ball)" />
      <g clip-path="url(#to-clip)"><g class="to-swirl">{[0, 2.1, 4.2].map((k) => <path d={arm(k)} fill="#fff" opacity="0.55" />)}</g></g>
      <ellipse cx="88" cy="84" rx="12" ry="7" fill="#fff" opacity="0.55" transform="rotate(-30 88 84)" />
      <g class="to-orbit">{[0, 120, 240].map((a) => <path transform={`rotate(${a} 100 100)`} d={spark(100, 22, 5)} fill="#fff" />)}</g>
    </svg>
  );
}

/** Secoue l'écran (plus fort pour une rareté plus haute). */
function shake(el: HTMLElement | null, level: number) {
  if (!el?.animate) return;
  const a = 3 + level * 3;
  el.animate([
    { transform: 'translate(0, 0)' }, { transform: `translate(${-a}px, ${a * 0.6}px)` }, { transform: `translate(${a}px, ${-a * 0.5}px)` },
    { transform: `translate(${-a * 0.4}px, ${a * 0.3}px)` }, { transform: 'translate(0, 0)' },
  ], { duration: 260 + level * 70, easing: 'ease-out' });
}

/**
 * Le tirage : d'abord la boule de magie encaisse des impacts dont la couleur monte d'un cran à chaque fois (argent, bleu,
 * violet, or) et s'arrête sur la meilleure rareté obtenue : on devine ce qui arrive avant de le voir. Elle éclate, les
 * cartes en jaillissent de dos, chacune luisant de la couleur de sa rareté, et se retournent de la moins rare à la plus
 * rare (la meilleure tremble, se fait attendre, et frappe plus fort). Toucher l'écran passe directement aux héros.
 */
export function SummonResult({ heroes }: { heroes: Hero[] }) {
  const rank = (h: Hero) => RARITIES.indexOf(heroDef(h.defId).rarity);
  const sorted = [...heroes].sort((a, b) => rank(b) - rank(a));
  const best = rank(sorted[0]!);
  const top = RARITIES[best]!;
  const one = heroes.length === 1;
  const [step, setStep] = useState(-1);
  const [phase, setPhase] = useState<'tease' | 'cards'>('tease');
  const [skip, setSkip] = useState(false);
  const stage = useRef<HTMLDivElement>(null);
  // la montée des couleurs : un impact par rareté, de l'argent jusqu'à la meilleure du tirage, puis les cartes
  useEffect(() => {
    if (phase !== 'tease') return;
    const id = setTimeout(() => {
      if (step < best) setStep(step + 1);
      else setPhase('cards');
    }, step === -1 ? FIRST_MS : step < best ? STEP_MS : HOLD_MS[best]);
    return () => clearTimeout(id);
  }, [step, phase]);
  // chaque impact secoue l'écran et fait enfler la boule, un peu plus fort à chaque rareté
  useEffect(() => {
    if (step < 0 || phase !== 'tease') return;
    shake(stage.current, step);
    const orb = stage.current?.querySelector<SVGElement>('.tease-orb');
    orb?.animate?.([{ scale: '1' }, { scale: `${1.16 + step * 0.05}` }, { scale: '1' }], { duration: 420, easing: 'cubic-bezier(.2,1.6,.4,1)' });
  }, [step]);
  // l'ordre des retournements : de la moins rare à la plus rare ; la meilleure carte se fait attendre
  const order = sorted.map((h, i) => ({ i, r: rank(h) })).sort((a, b) => a.r - b.r || b.i - a.i).map((x) => x.i);
  const flipAt = new Map<number, number>();
  order.forEach((idx, k) => flipAt.set(idx, DEAL_MS + k * FLIP_GAP + (k === order.length - 1 && best >= 2 ? BEST_PAUSE : 0)));
  const last = flipAt.get(0)!;
  const total = Math.max(...flipAt.values()) + FLIP_MS;
  // les cartes jaillissent de la boule : chacune part du centre de la scène vers sa place
  useLayoutEffect(() => {
    const st = stage.current;
    const grid = st?.querySelector<HTMLElement>('.reveal');
    if (phase !== 'cards' || !st || !grid) return;
    const cx = st.clientWidth / 2 - grid.offsetLeft, cy = st.clientHeight / 2 - grid.offsetTop;
    grid.querySelectorAll<HTMLElement>('.reveal-card').forEach((c) => {
      c.style.setProperty('--dx', `${Math.round(cx - (c.offsetLeft + c.offsetWidth / 2))}px`);
      c.style.setProperty('--dy', `${Math.round(cy - (c.offsetTop + c.offsetHeight / 2))}px`);
    });
  }, [phase]);
  // la meilleure carte (Épique, Légendaire) secoue l'écran en se retournant
  useEffect(() => {
    if (phase !== 'cards' || skip || best < 2) return;
    const id = setTimeout(() => shake(stage.current, best), last + 300);
    return () => clearTimeout(id);
  }, [phase, skip]);
  const tc = TEASE[phase === 'cards' ? best : Math.max(0, step)]!;
  const finish = () => { if (phase === 'tease') setPhase('cards'); setSkip(true); };
  return (
    <div class={`reveal-screen reveal-${top}${one ? ' reveal-one' : ' reveal-many'} rv-${phase}${skip ? ' rv-skip' : ''}`}
      style={{ '--best': RARITY_COLOR[top], '--tc': tc, '--total': `${skip ? 0 : total}ms`, '--last': `${last}ms` } as never} onClick={finish}>
      <div class="reveal-decor"><SummonBackdrop /></div>
      <div class="reveal-sky" />
      <h2 class="sr-only">{t('summon.normal')}</h2>
      <div class="reveal-stage" ref={stage}>
        {phase === 'tease' && (
          <div class={`tease s${Math.max(0, step)}`}>
            <TeaseOrb />
            {step >= 0 && (
              <div class={`tease-hit th-${step}`} key={step}>
                <span class="th-flash" /><span class="th-core" />
                <span class="th-ring" /><span class="th-ring th-ring-2" />
                {Array.from({ length: 10 + step * 4 }, (_, i) => <span class="th-spark" style={{ '--a': `${(i * 360) / (10 + step * 4) + step * 13}deg`, '--r': `${110 + (i % 3) * 34 + step * 22}px` } as never} />)}
                {step === 3 && <span class="th-pillar" />}
              </div>
            )}
          </div>
        )}
        {phase === 'cards' && (
          <>
            {!skip && (
              <span class="rv-burst">
                <span class="rb-flash" /><span class="rb-ring" />
                {Array.from({ length: 16 }, (_, i) => <span class="rb-spark" style={{ '--a': `${i * 22.5 + 7}deg`, '--r': `${150 + (i % 4) * 40}px` } as never} />)}
              </span>
            )}
            {one && best >= 2 && <span class="rv-halo-wrap"><Halo size={330} color={RARITY_COLOR[top]} /></span>}
            <div class="reveal">
              {sorted.map((h, i) => {
                const d = heroDef(h.defId);
                const r = rank(h);
                return (
                  <div class={`reveal-card r-${d.rarity}${r === best && best > 0 ? ' is-best' : ''}`}
                    style={{ '--rar': RARITY_COLOR[d.rarity], '--tint': TEASE[r], '--deal': `${skip ? 0 : 40 + i * 45}ms`, '--flip': `${skip ? 0 : flipAt.get(i)}ms` } as never}>
                    <span class="reveal-beam" />
                    <div class="rv-inner">
                      <div class="rv-face rv-back"><CardBack uid={i} color={TEASE[r]!} h={one ? 180 : 200} /></div>
                      <div class="rv-face rv-front"><HeroCard hero={h} small={!one} /></div>
                    </div>
                    <span class="rv-hit"><i /><i /></span>
                    {newlyFound.has(h.uid) && <span class="new-tag new-ribbon">{t('new')} !</span>}
                    <span class="reveal-name">{d.name}</span>
                  </div>
                );
              })}
            </div>
            {best >= 2 && !skip && <span class="rv-final" />}
          </>
        )}
      </div>
      {phase === 'cards' && <button class="sum-btn sum-btn-10 reveal-ok" onClick={(e) => { e.stopPropagation(); close(); }}><span class="sum-btn-n">{t('ok')}</span></button>}
    </div>
  );
}

export function OddsModal() {
  return (
    <Modal title={t('summon.odds')}>
      <h3>{t('summon.normal')}</h3>
      <table class="odds">
        {RARITIES.map((r) => (
          <tr>
            <td style={{ color: RARITY_COLOR[r] }}>{t(`rarity.${r}`)}</td>
            <td>{(SUMMON_RATES[r] * 100).toFixed(1)} %</td>
            <td class="muted">{HEROES.filter((h) => h.rarity === r).length}</td>
          </tr>
        ))}
      </table>
      <p class="muted small">{t('summon.pity', { n: LEGENDARY_PITY })}</p>
      <h3>{t('summon.basic')}</h3>
      <table class="odds">
        {Object.entries(BASIC_SUMMON_RATES).map(([r, v]) => (
          <tr>
            <td style={{ color: RARITY_COLOR[r as keyof typeof RARITY_COLOR] }}>{t(`rarity.${r}`)}</td>
            <td>{((v ?? 0) * 100).toFixed(0)} %</td>
            <td />
          </tr>
        ))}
      </table>
      <div class="center"><Stars stars={5} /></div>
    </Modal>
  );
}
