// Invocations : normale (parchemins ou gemmes), simple (Communs et Rares), fragments, et révélation.
import { BASIC_SUMMON_RATES, LEGENDARY_PITY, SUMMON_RATES } from '../../../core/data/summon';
import { HEROES, heroDef } from '../../../core/data/heroes';
import { FRAGMENTS_PER_COPY } from '../../../core/data/stars';
import { RARITIES, type Hero } from '../../../core/types';
import { RARITY_COLOR, heroImage } from '../../art';
import { t } from '../../i18n';
import { adsLeft, claimFragments, newlyFound, summon, summonCost, watchAd } from '../../state/actions';
import { useGame } from '../../state/store';
import { Art, Bar, Btn, Cur, HeroCard, Icon, Modal, Stars } from '../kit';
import { open } from '../nav';

function SummonButton({ kind, count }: { kind: 'normal' | 'basic'; count: 1 | 10 }) {
  const s = useGame();
  const cost = summonCost(kind, count);
  const ok = s.wallet[cost.currency] >= cost.amount;
  return (
    <Btn
      kind={kind === 'normal' ? 'purple' : 'blue'}
      class={kind === 'normal' && count === 10 ? 'tuto-summon10' : ''}
      wide
      disabled={!ok}
      onClick={() => {
        const heroes = summon(kind, count);
        if (heroes) open({ type: 'summon', heroes });
      }}
    >
      {t(`summon.x${count}`)} <Cur k={cost.currency} n={cost.amount} />
    </Btn>
  );
}

export function SummonScreen() {
  const s = useGame();
  // Seulement les héros dont on a des fragments : on ne dévoile jamais un héros pas encore rencontré.
  const owned = Object.entries(s.fragments).filter(([, n]) => n > 0);
  return (
    <div class="screen summon">
      <section class="card portal">
        <Art class="portal-altar" name="summonAltar" />
        <h1>{t('summon.normal')}</h1>
        <p class="muted">{t('summon.pity', { n: LEGENDARY_PITY - s.summon.pity })}</p>
        <div class="row gap">
          <SummonButton kind="normal" count={1} />
          <SummonButton kind="normal" count={10} />
        </div>
        <div class="row gap">
          <Btn kind="ghost" small onClick={() => open({ type: 'odds' })}>{t('summon.odds')}</Btn>
          <Btn
            kind="ghost"
            small
            disabled={adsLeft(s) <= 0}
            onClick={() => {
              const go = () => {
                const gain = watchAd('summon');
                if (gain) open({ type: 'summon', heroes: gain.heroes });
              };
              if (s.shop.noAds) go();
              else open({ type: 'ad', onDone: go });
            }}
          >
            <Icon name="ad" size={18} /> {t('summon.adFree')}
          </Btn>
        </div>
      </section>

      <section class="card portal basic">
        <h2>{t('summon.basic')}</h2>
        <div class="row gap">
          <SummonButton kind="basic" count={1} />
          <SummonButton kind="basic" count={10} />
        </div>
      </section>

      {owned.length > 0 && (
        <section class="card">
          <h2>{t('summon.fragments')}</h2>
          {owned.map(([defId, n]) => (
            <div class="row gap center-y frag-row">
              <img class="frag-img" src={heroImage(defId)} alt="" />
              <div class="grow">
                <strong>{heroDef(defId).name}</strong>
                <Bar value={n} max={FRAGMENTS_PER_COPY} color="var(--gold)" label={`${n} / ${FRAGMENTS_PER_COPY}`} />
              </div>
              <Btn kind="gold" small disabled={n < FRAGMENTS_PER_COPY} onClick={() => {
                const h = claimFragments(defId);
                if (h) open({ type: 'summon', heroes: [h] });
              }}>{t('summon.copy')}</Btn>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

export function SummonResult({ heroes }: { heroes: Hero[] }) {
  const best = heroes.reduce((a, h) => Math.max(a, RARITIES.indexOf(heroDef(h.defId).rarity)), 0);
  return (
    <Modal title={t('summon.normal')} wide>
      <div class={`reveal reveal-${RARITIES[best]}`}>
        {heroes.map((h, i) => {
          const d = heroDef(h.defId);
          return (
            <div class="reveal-card" style={{ animationDelay: `${i * 90}ms`, '--rar': RARITY_COLOR[d.rarity], '--d': `${300 + i * 140}ms` } as never}>
              <div class="reveal-flip"><HeroCard hero={h} small /></div>
              <Art class="reveal-back" name="cardBack" />
              {newlyFound.has(h.uid) && <span class="new-tag">{t('new')} !</span>}
              <span class="reveal-name">{d.name}</span>
            </div>
          );
        })}
      </div>
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
