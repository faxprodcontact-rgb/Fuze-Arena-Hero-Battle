// Invocations : normale (parchemins ou gemmes), simple (Communs et Rares), fragments, et révélation.
import { BASIC_SUMMON_RATES, LEGENDARY_PITY, SUMMON_RATES } from '../../../core/data/summon';
import { HEROES, heroDef } from '../../../core/data/heroes';
import { FRAGMENTS_PER_COPY } from '../../../core/data/stars';
import { RARITIES, type Hero } from '../../../core/types';
import { RARITY_COLOR, heroImage } from '../../art';
import { t } from '../../i18n';
import { adsLeft, claimFragments, setFragmentTarget, summon, summonCost, watchAd } from '../../state/actions';
import { useGame } from '../../state/store';
import { Btn, Cur, HeroCard, Icon, Modal, Stars } from '../kit';
import { open, toast } from '../nav';

function SummonButton({ kind, count }: { kind: 'normal' | 'basic'; count: 1 | 10 }) {
  const s = useGame();
  const cost = summonCost(kind, count);
  const ok = s.wallet[cost.currency] >= cost.amount;
  return (
    <Btn
      kind={kind === 'normal' ? 'purple' : 'blue'}
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
  const legendaries = HEROES.filter((h) => h.rarity === 'legendary');
  const target = s.fragmentTarget ?? legendaries[0]!.id;
  const have = s.fragments[target] ?? 0;
  return (
    <div class="screen summon">
      <section class="card portal">
        <div class="portal-ring" />
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

      <section class="card">
        <h2>{t('summon.fragments')}</h2>
        <div class="row gap center-y">
          <img class="frag-img" src={heroImage(target)} alt="" />
          <div class="grow">
            <strong>{heroDef(target).name}</strong>
            <div class="row gap-s center-y"><Cur k="fragments" n={have} /> <span class="muted">/ {FRAGMENTS_PER_COPY}</span></div>
          </div>
          <Btn kind="gold" small disabled={have < FRAGMENTS_PER_COPY} onClick={() => {
            const h = claimFragments(target);
            if (h) open({ type: 'summon', heroes: [h] });
          }}>{t('summon.copy')}</Btn>
        </div>
        <p class="muted small">{t('summon.target')}</p>
        <div class="frag-list">
          {legendaries.map((d) => (
            <button class={`frag-pick${d.id === target ? ' on' : ''}`} onClick={() => { setFragmentTarget(d.id); toast(d.name); }}>
              <img src={heroImage(d.id)} alt={d.name} />
            </button>
          ))}
        </div>
      </section>
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
            <div class="reveal-card" style={{ animationDelay: `${i * 90}ms`, '--rar': RARITY_COLOR[d.rarity] } as never}>
              <HeroCard hero={h} small />
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
