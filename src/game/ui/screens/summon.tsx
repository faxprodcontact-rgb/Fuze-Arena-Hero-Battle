// Invocations : normale (parchemins ou gemmes), simple (Communs et Rares), fragments, et révélation.
import { BASIC_SUMMON_RATES, LEGENDARY_PITY, SUMMON_RATES } from '../../../core/data/summon';
import { HEROES, heroDef } from '../../../core/data/heroes';
import { FRAGMENTS_PER_COPY } from '../../../core/data/stars';
import { RARITIES, type Hero } from '../../../core/types';
import { RARITY_COLOR, heroImage } from '../../art';
import { useState } from 'preact/hooks';
import { fmt, t } from '../../i18n';
import { SummonBackdrop } from '../backdrop-summon';
import { SummonStage } from '../summon-stage';
import { Medallion } from '../chrome';
import { TitleBanner } from '../title-banner';
import { adsLeft, claimFragments, newlyFound, summon, summonCost, watchAd } from '../../state/actions';
import { useGame } from '../../state/store';
import { Art, Bar, Btn, Cur, HeroCard, Icon, Modal, Stars } from '../kit';
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

/** La révélation : sur fond de nuit, les héros les plus rares d'abord ; chacun arrive de dos dans une lueur de la couleur de
 *  sa rareté, puis se retourne. Les meilleurs sont mis en valeur (halo, éclat) ; un héros seul est montré en grand. */
export function SummonResult({ heroes }: { heroes: Hero[] }) {
  const rank = (h: Hero) => RARITIES.indexOf(heroDef(h.defId).rarity);
  const sorted = [...heroes].sort((a, b) => rank(b) - rank(a));
  const top = RARITIES[rank(sorted[0]!)]!;
  const one = heroes.length === 1;
  return (
    <div class={`reveal-screen reveal-${top}${one ? ' reveal-one' : ' reveal-many'}`} style={{ '--best': RARITY_COLOR[top] } as never}>
      <div class="reveal-decor"><SummonBackdrop /></div>
      <div class="reveal-sky" />
      <h2 class="sr-only">{t('summon.normal')}</h2>
      <div class="reveal-stage">
        {one && (
          <>
            {/* l'éclat derrière le héros : une étoile à huit branches qui tourne, une onde, des étincelles projetées */}
            <svg class="reveal-burst" viewBox="-100 -100 200 200" aria-hidden="true">
              <defs><radialGradient id="rv-star"><stop offset="0" stop-color="#fff" stop-opacity="0.95" /><stop offset="0.4" stop-color="var(--best)" stop-opacity="0.7" /><stop offset="1" stop-color="var(--best)" stop-opacity="0" /></radialGradient></defs>
              <g class="rv-spin">{Array.from({ length: 8 }, (_, i) => <path transform={`rotate(${i * 45})`} d={i % 2 ? 'M-7 0 L0 -62 L7 0 Z' : 'M-10 0 L0 -96 L10 0 Z'} fill="url(#rv-star)" />)}</g>
              <circle class="rv-wave" r="40" fill="none" stroke="#fff" stroke-width="3" />
            </svg>
            {Array.from({ length: 12 }, (_, i) => <span class="rv-spark" style={{ '--a': `${i * 30 + 10}deg`, '--r': `${120 + (i % 3) * 30}px`, animationDelay: `${450 + (i % 4) * 60}ms` } as never} />)}
          </>
        )}
        <div class="reveal">
          {sorted.map((h, i) => {
            const d = heroDef(h.defId);
            const best = d.rarity === top && top !== 'common';
            return (
              <div class={`reveal-card r-${d.rarity}${best ? ' is-best' : ''}`} style={{ animationDelay: `${i * 90}ms`, '--rar': RARITY_COLOR[d.rarity], '--d': `${300 + i * 140}ms` } as never}>
                <span class="reveal-beam" />
                <div class="reveal-flip"><HeroCard hero={h} small={!one} /></div>
                <Art class="reveal-back" name="cardBack" />
                {newlyFound.has(h.uid) && <span class="new-tag new-ribbon">{t('new')} !</span>}
                <span class="reveal-name">{d.name}</span>
              </div>
            );
          })}
        </div>
      </div>
      <button class="sum-btn sum-btn-10 reveal-ok" onClick={close}><span class="sum-btn-n">{t('ok')}</span></button>
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
