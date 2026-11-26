// Invocations : normale (parchemins ou gemmes), simple (Communs et Rares), fragments. Le tirage lui-même (portail qui
// s'ouvre, héros qui sortent) est dans sections/summon-reveal.tsx ; le portail et son estrade dans sections/summon-gate.tsx.
import { BASIC_SUMMON_RATES, LEGENDARY_PITY, SUMMON_RATES } from '../../../core/data/summon';
import { HEROES, heroDef } from '../../../core/data/heroes';
import { FRAGMENTS_PER_COPY, RARITY_RULES } from '../../../core/data/stars';
import { RARITIES, type Hero, type Rarity } from '../../../core/types';
import { RARITY_COLOR, heroImage } from '../../art';
import { useState } from 'preact/hooks';
import { fmt, t } from '../../i18n';
import { GateStage } from '../sections/summon-gate';
import { rememberCast } from '../sections/summon-reveal';
import { adsLeft, claimFragments, summon, summonCost, watchAd } from '../../state/actions';
import { useGame } from '../../state/store';
import { Bar, Btn, Cur, HeroCard, Icon, Modal } from '../kit';
import { btClass } from '../buttons';
import { close, open } from '../nav';
import '../sections/invoquer.css';

export { SummonResult } from '../sections/summon-reveal';

type Kind = 'normal' | 'basic';

/** Le choix du portail : deux onglets arrondis, chacun avec son parchemin et le nombre qu'il en reste. */
function KindTab({ kind, on, icon, n, onClick }: { kind: Kind; on: boolean; icon: string; n: number; onClick: () => void }) {
  return (
    <button class={`sum-kind sum-kind-tab-${kind}${on ? ` on ${btClass('or', 's')}` : ''}`} aria-pressed={on} onClick={onClick}>
      <Icon name={icon} size={30} />
      <span class="sum-kind-n">{fmt(n)}</span>
    </button>
  );
}

/** Un petit bouton rond posé sur la scène (chances, fragments, invocation gratuite). */
function RoundBtn({ icon, label, dot, off, disabled, onClick }: { icon: string; label: string; dot?: boolean; off?: boolean; disabled?: boolean; onClick: () => void }) {
  return (
    <button class={`sum-round${off ? ' sum-off' : ''}`} disabled={disabled || off} tabIndex={off ? -1 : 0} aria-hidden={off} onClick={onClick}>
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
        class={`sum-btn sum-btn-${count} ${btClass(count === 10 ? 'basalte' : 'arcane', 'l')}${kind === 'normal' && count === 10 ? ' tuto-summon10' : ''}`}
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
        <div class="sum-kinds bt-rail" role="tablist">
          <KindTab kind="normal" on={kind === 'normal'} icon="scrolls" n={s.wallet.scrolls} onClick={() => setKind('normal')} />
          <KindTab kind="basic" on={kind === 'basic'} icon="basicScrolls" n={s.wallet.basicScrolls} onClick={() => setKind('basic')} />
        </div>
        <h1 class="sum-name">{t(`summon.${kind}`)}</h1>
      </div>

      <div class="sum-stage">
        <GateStage kind={kind} casting={casting} />
        <div class="sum-corner sum-corner-r">
          <RoundBtn icon="star" label={t('summon.odds')} onClick={() => { oddsKind = kind; open({ type: 'odds' }); }} />
        </div>
        <div class="sum-corner sum-corner-l">
          {owned.length > 0 && (
            <RoundBtn icon="fragments" label={t('summon.fragments')} dot={owned.some(([, n]) => n >= FRAGMENTS_PER_COPY)} onClick={() => open({ type: 'fragments' })} />
          )}
          {/* l'invocation gratuite (une publicité) : seulement pour le portail normal ; sa place est gardée pour l'autre */}
          <RoundBtn icon="ad" label={t('summon.freeShort')} off={kind !== 'normal'} disabled={adsLeft(s) <= 0} dot={kind === 'normal' && adsLeft(s) > 0}
            onClick={() => {
              const go = () => { rememberCast(null); cast(watchAd('summon')?.heroes); };
              if (s.shop.noAds) go();
              else open({ type: 'ad', onDone: go });
            }} />
        </div>
      </div>

      {/* le panneau : la même hauteur pour les deux portails ; en haut, la jauge du Légendaire garanti (portail normal) ou
          les deux raretés possibles et leur part (invocation simple), puis les deux gros boutons */}
      <div class="sum-panel">
        {kind === 'normal' ? (
          <div class="sum-pity">
            <span class="sum-pity-gem"><Icon name="star" size={22} /></span>
            <div class="sum-pity-bar"><span style={{ width: `${(s.summon.pity / LEGENDARY_PITY) * 100}%` }} /></div>
            <strong>{left}</strong>
          </div>
        ) : (
          <div class="sum-pity sum-rates">
            {RARITIES.filter((r) => (BASIC_SUMMON_RATES[r] ?? 0) > 0).map((r) => (
              <span class="sum-rate" style={{ '--rar': RARITY_COLOR[r] } as never}>
                <i />{t(`rarity.${r}`)}<strong>{Math.round((BASIC_SUMMON_RATES[r] ?? 0) * 100)} %</strong>
              </span>
            ))}
          </div>
        )}
        <div class="sum-buttons">{button(1)}{button(10)}</div>
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

/** Le portail dont on montre les chances (celui de l'onglet quand on touche « Chances »). */
let oddsKind: Kind = 'normal';

/**
 * Les chances d'un portail, calculées sur les vraies tables (core/data/summon.ts) et le vrai tirage (core/summon.ts : la
 * rareté d'abord, puis un héros de cette rareté, tous à parts égales) : pour chaque rareté, de la plus rare à la plus
 * commune, sa part, puis chaque héros avec sa propre chance, du plus probable au moins probable.
 */
function oddsOf(kind: Kind) {
  const rates: Partial<Record<Rarity, number>> = kind === 'basic' ? BASIC_SUMMON_RATES : SUMMON_RATES;
  return [...RARITIES].reverse().map((r) => {
    const total = rates[r] ?? 0;
    const defs = HEROES.filter((h) => h.rarity === r);
    const list = defs.map((def) => ({ def, p: defs.length ? total / defs.length : 0 }))
      .sort((a, b) => b.p - a.p || a.def.name.localeCompare(b.def.name));
    return { r, total, list };
  }).filter((g) => g.total > 0 && g.list.length > 0);
}

/** Un pourcentage lisible : 45 %, 16,5 %, 0,97 % (virgule en français). */
function pct(v: number, lang: string): string {
  const x = v * 100;
  const s = (x >= 10 ? x.toFixed(1) : x.toFixed(2)).replace(/\.?0+$/, '');
  return `${lang === 'en' ? s : s.replace('.', ',')} %`;
}

export function OddsModal() {
  const s = useGame();
  const [kind, setKind] = useState<Kind>(oddsKind);
  const pick = (k: Kind) => { oddsKind = k; setKind(k); };
  return (
    <Modal title={t('summon.odds')}>
      <div class={`odds2 odds2-${kind}`}>
        <div class="odds2-kinds bt-rail" role="tablist">
          {(['normal', 'basic'] as const).map((k) => (
            <button class={`odds2-kind${kind === k ? ` on ${btClass('or', 's')}` : ''}`} aria-pressed={kind === k} onClick={() => pick(k)}>
              <Icon name={k === 'basic' ? 'basicScrolls' : 'scrolls'} size={24} />
              <span>{t(`summon.${k}`)}</span>
            </button>
          ))}
        </div>
        <div class="odds2-list">
          {oddsOf(kind).map((g) => (
            <section class={`odds2-group odds2-${g.r}`} style={{ '--rar': RARITY_COLOR[g.r] } as never}>
              <header class="odds2-head">
                <span class="odds2-rar">{t(`rarity.${g.r}`)}</span>
                <strong class="odds2-total">{pct(g.total, s.lang)}</strong>
              </header>
              {g.r === 'legendary' && kind === 'normal' && <p class="odds2-pity">{t('summon.pity', { n: LEGENDARY_PITY })}</p>}
              <div class="odds2-grid">
                {g.list.map(({ def, p }) => (
                  <div class="odds2-cell">
                    <HeroCard hero={{ uid: 0, defId: def.id, stars: RARITY_RULES[def.rarity].bornStars, level: 1 }} small />
                    <span class="odds2-p">{pct(p, s.lang)}</span>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      </div>
    </Modal>
  );
}
