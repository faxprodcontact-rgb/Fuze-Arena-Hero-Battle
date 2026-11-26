// La vitrine de la boutique (vague 3, 26/11 : « que ça donne envie d'acheter ») : l'offre du moment en grand (héros
// Légendaire en pied posé à côté du cadeau), les autres offres en cases, les gemmes en piles de plus en plus grosses.
// Mêmes offres, mêmes prix, même achat simulé qu'avant (le serveur jugera plus tard). Style : sections/boutique.css.
import { HEROES } from '../../../core/data/heroes';
import { GEMS_PER_SUMMON, MONTHLY_CARD, OFFERS, PASS_LEVELS, type Offer, type Reward } from '../../../core/data/modes';
import { fmt, t } from '../../i18n';
import { now, useGame } from '../../state/store';
import { Art, Icon, Sign } from '../kit';
import { btClass } from '../buttons';
import { BqFigure, Sparkles } from './boutique-kit';
import { figMeta } from './hero-fig';

const euros = (o: Offer) => parseFloat(o.price.replace(',', '.').replace(/[^\d.]/g, '')) || 1;

/** Tout ce que donne la voie premium du passe (ses 30 paliers). */
const PASS_TOTAL: Reward = PASS_LEVELS.reduce<Reward>((acc, lv) => {
  for (const [k, v] of Object.entries(lv.premium)) acc[k as keyof Reward] = (acc[k as keyof Reward] ?? 0) + (v ?? 0);
  return acc;
}, {});

/** Ce que vaut une offre en gemmes (parchemin = une invocation ; la carte compte ses 30 jours, le passe ses paliers). */
function worth(o: Offer): number {
  const r = o.kind === 'pass' ? PASS_TOTAL : o.reward;
  return (r.gems ?? 0) + (r.scrolls ?? 0) * GEMS_PER_SUMMON + (o.kind === 'card' ? MONTHLY_CARD.days * MONTHLY_CARD.gemsPerDay : 0);
}

/** Gemmes par euro du plus petit paquet : la base des « ×N » et des « +N % ». */
const BASE = (() => {
  const g = OFFERS.find((o) => o.kind === 'gems');
  return g ? worth(g) / euros(g) : 1;
})();

/** Le multiple de valeur d'une offre par rapport au petit paquet de gemmes (rien sous ×2). */
function valueX(o: Offer): number {
  const x = Math.round(worth(o) / euros(o) / BASE);
  return x >= 2 ? x : 0;
}

/** Le héros qui pose dans la vitrine : un Légendaire dessiné en HD. */
const SHOW_HERO = ['angels-2', ...HEROES.filter((h) => h.rarity === 'legendary').map((h) => h.id)].find((id) => figMeta(id));

function Price({ o, soldOut, size, onBuy }: { o: Offer; soldOut: boolean; size: 's' | 'm' | 'l'; onBuy: () => void }) {
  return (
    <button class={`bq-price ${btClass('or', size)}`} disabled={soldOut} onClick={() => !soldOut && onBuy()}>
      {soldOut ? <><Sign name="check" k={1.6} /> {t('offer.owned')}</> : o.price}
    </button>
  );
}

function Rewards({ o, big }: { o: Offer; big?: boolean }) {
  return (
    <span class={`bq-rw${big ? ' bq-rw-big' : ''}`}>
      {Object.entries(o.kind === 'pass' ? PASS_TOTAL : o.reward).map(([k, v]) => <span class="bq-chip"><Icon name={k} size={big ? 26 : 20} /><b>{fmt(v ?? 0)}</b></span>)}
    </span>
  );
}

/** Ce qui s'ajoute sous le nom d'une offre sans monnaie (carte, passe, sans pub). */
function Extra({ o }: { o: Offer }) {
  if (o.kind === 'card') return <span class="bq-rw"><span class="bq-chip"><Icon name="gems" size={20} /><b>{t('bq.perDay', { n: MONTHLY_CARD.gemsPerDay })}</b></span></span>;
  if (o.kind === 'noAds') return null;
  return <Rewards o={o} />;
}

export function OffersTab({ onBuy }: { onBuy: (id: string) => void }) {
  const s = useGame();
  const list = OFFERS.filter((o) => o.kind !== 'gems');
  const soldOut = (o: Offer) => o.limit > 0 && (s.shop.bought[o.id] ?? 0) >= o.limit;
  // L'offre du moment : la première offre unique encore à prendre (départ, puis croissance), sinon la première libre.
  const feat = list.find((o) => o.limit === 1 && (o.kind === 'starter' || o.kind === 'growth') && !soldOut(o)) ?? list.find((o) => !soldOut(o));
  const rest = list.filter((o) => o !== feat).sort((a, b) => Number(soldOut(a)) - Number(soldOut(b)));
  return (
    <div class="bq-offers">
      {feat && (
        <div class={`bq-feat bq-k-${feat.kind}`}>
          <i class="bq-feat-sky" />
          <i class="bq-floor" />
          {SHOW_HERO && <BqFigure id={SHOW_HERO} u={1.08} class="bq-feat-hero" />}
          <span class="bq-feat-gift"><i class="lg-glow" /><Art name={`offer-${feat.kind}`} /></span>
          <Sparkles n={5} />
          <div class="bq-feat-text">
            <span class="bq-tags">
              {valueX(feat) > 0 && <span class="bq-x">{t('bq.value', { n: valueX(feat) })}</span>}
              {feat.limit === 1 && <span class="bq-once"><Icon name="hourglass" size={18} />{t('bq.once')}</span>}
            </span>
            <strong>{t(`offer.${feat.id}`)}</strong>
            <Rewards o={feat} big />
            <Price o={feat} soldOut={false} size="l" onBuy={() => onBuy(feat.id)} />
          </div>
        </div>
      )}
      <div class="bq-grid">
        {rest.map((o) => {
          const out = soldOut(o);
          const x = valueX(o);
          const cardLeft = o.kind === 'card' ? Math.ceil((s.shop.cardUntil - now()) / 86_400_000) : 0;
          return (
            <div class={`bq-card bq-k-${o.kind}${out ? ' bq-out' : ''}`}>
              <span class="bq-stage"><i class="lg-glow" /><Art name={`offer-${o.kind}`} class="bq-art" /></span>
              {!out && x > 0 && <span class="bq-x bq-corner">{t('bq.value', { n: x })}</span>}
              {!out && !x && o.limit === 1 && <span class="bq-once bq-corner"><Icon name="hourglass" size={16} /></span>}
              {cardLeft > 0 && <span class="bq-once bq-time bq-corner-l"><Icon name="clock" size={16} />{t('bq.days', { n: cardLeft })}</span>}
              <strong>{t(`offer.${o.id}`)}</strong>
              {!out && <Extra o={o} />}
              <Price o={o} soldOut={out} size="s" onBuy={() => onBuy(o.id)} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

/** Le passe premium à prendre, en tête de l'onglet du passe (même achat). */
export function PassBuy({ onBuy }: { onBuy: () => void }) {
  const o = OFFERS.find((x) => x.kind === 'pass');
  if (!o) return null;
  return (
    <div class="bq-passbuy">
      <span class="bq-stage"><i class="lg-glow" /><Art name="offer-pass" class="bq-art" /></span>
      <strong>{t('offer.pass')}</strong>
      <Price o={o} soldOut={false} size="m" onBuy={onBuy} />
    </div>
  );
}

export function GemsTab({ onBuy }: { onBuy: (id: string) => void }) {
  const packs = OFFERS.filter((o) => o.kind === 'gems');
  const best = packs.reduce((a, b) => (worth(b) / euros(b) > worth(a) / euros(a) ? b : a), packs[0]!);
  return (
    <div class="bq-gems">
      {packs.map((o, i) => {
        const bonus = Math.round((worth(o) / euros(o) / BASE - 1) * 100);
        return (
          <div class={`bq-card bq-gem bq-tier-${i}${o === best ? ' bq-best' : ''}`}>
            {o === best && <span class="bq-crown"><Icon name="crown" size={20} />{t('bq.best')}</span>}
            <span class="bq-stage"><i class="lg-glow" /><Art name={`offer-${o.id}`} class="bq-art" />{i >= 2 && <Sparkles n={i + 1} />}</span>
            {bonus >= 5 && <span class="bq-x bq-corner">{t('bq.bonus', { n: bonus })}</span>}
            <span class="bq-amount"><Icon name="gems" size={26} /><b>{fmt(o.reward.gems ?? 0)}</b></span>
            <Price o={o} soldOut={false} size="m" onBuy={() => onBuy(o.id)} />
          </div>
        );
      })}
    </div>
  );
}
