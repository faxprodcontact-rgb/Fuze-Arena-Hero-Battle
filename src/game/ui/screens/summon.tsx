// Invocations : normale (parchemins ou gemmes), simple (Communs et Rares), fragments. Le tirage lui-même (portail qui
// s'ouvre, héros qui sortent) est dans sections/summon-reveal.tsx ; le portail et son estrade dans sections/summon-gate.tsx.
import { BASIC_SUMMON_RATES, LEGENDARY_PITY, SUMMON_RATES } from '../../../core/data/summon';
import { HEROES, heroDef } from '../../../core/data/heroes';
import { FRAGMENTS_PER_COPY } from '../../../core/data/stars';
import { RARITIES, type Hero } from '../../../core/types';
import { RARITY_COLOR, heroImage } from '../../art';
import { useState } from 'preact/hooks';
import { fmt, t } from '../../i18n';
import { GateStage } from '../sections/summon-gate';
import { rememberCast } from '../sections/summon-reveal';
import { adsLeft, claimFragments, summon, summonCost, watchAd } from '../../state/actions';
import { useGame } from '../../state/store';
import { Bar, Btn, Cur, Icon, Modal, Stars } from '../kit';
import { close, open } from '../nav';
import '../sections/invoquer.css';

export { SummonResult } from '../sections/summon-reveal';

type Kind = 'normal' | 'basic';

/** Le choix du portail : deux onglets arrondis, chacun avec son parchemin et le nombre qu'il en reste. */
function KindTab({ kind, on, icon, n, onClick }: { kind: Kind; on: boolean; icon: string; n: number; onClick: () => void }) {
  return (
    <button class={`sum-kind sum-kind-tab-${kind}${on ? ' on' : ''}`} aria-pressed={on} onClick={onClick}>
      <Icon name={icon} size={30} />
      <span class="sum-kind-n">{fmt(n)}</span>
    </button>
  );
}

/** Un petit bouton rond posé sur la scène (chances, fragments). */
function RoundBtn({ icon, label, dot, onClick }: { icon: string; label: string; dot?: boolean; onClick: () => void }) {
  return (
    <button class="sum-round" onClick={onClick}>
      <span class="sum-round-icon"><Icon name={icon} size={28} /></span>
      <span class="sum-round-label">{label}</span>
      {dot && <span class="dot" />}
    </button>
  );
}

export function SummonScreen() {
  const s = useGame();
  const [kind, setKind] = useState<Kind>('normal');
  // L'invocation est décidée tout de suite (le coût est payé) ; le portail de l'onglet aspire un instant, puis le tirage
  // s'ouvre par-dessus (sections/summon-reveal.tsx).
  const [casting, setCasting] = useState(false);
  const cast = (heroes: Hero[] | null | undefined) => {
    if (!heroes) return;
    setCasting(true);
    setTimeout(() => { setCasting(false); open({ type: 'summon', heroes }); }, 420);
  };
  const button = (count: 1 | 10) => {
    const cost = summonCost(kind, count);
    return (
      <button
        class={`sum-btn sum-btn-${count}${kind === 'normal' && count === 10 ? ' tuto-summon10' : ''}`}
        disabled={s.wallet[cost.currency] < cost.amount}
        onClick={() => { rememberCast({ kind, count }); cast(summon(kind, count)); }}
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
      <div class="sum-head">
        <div class="sum-kinds" role="tablist">
          <KindTab kind="normal" on={kind === 'normal'} icon="scrolls" n={s.wallet.scrolls} onClick={() => setKind('normal')} />
          <KindTab kind="basic" on={kind === 'basic'} icon="basicScrolls" n={s.wallet.basicScrolls} onClick={() => setKind('basic')} />
        </div>
        <h1 class="sum-name">{t(`summon.${kind}`)}</h1>
      </div>

      <div class="sum-stage">
        <GateStage kind={kind} casting={casting} />
        <div class="sum-corner sum-corner-r">
          <RoundBtn icon="star" label={t('summon.odds')} onClick={() => open({ type: 'odds' })} />
        </div>
        {owned.length > 0 && (
          <div class="sum-corner sum-corner-l">
            <RoundBtn icon="fragments" label={t('summon.fragments')} dot={owned.some(([, n]) => n >= FRAGMENTS_PER_COPY)} onClick={() => open({ type: 'fragments' })} />
          </div>
        )}
      </div>

      <div class="sum-panel">
        {kind === 'normal' && (
          <div class="sum-pity">
            <span class="sum-pity-gem"><Icon name="star" size={22} /></span>
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
              const go = () => { rememberCast(null); cast(watchAd('summon')?.heroes); };
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
            if (h) { close(); rememberCast(null); open({ type: 'summon', heroes: [h] }); }
          }}>{t('summon.copy')}</Btn>
        </div>
      ))}
    </Modal>
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
