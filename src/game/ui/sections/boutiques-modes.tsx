// Les boutiques d'échange de la guilde et de l'arène (vague 3, 26/11 : « plus spectaculaires »). Même famille que la
// boutique (boutique-offres.tsx : lueurs, étincelles, dalles d'or), chacune avec son caractère :
// - guilde = le trésor de la guilde : la bannière de la guilde derrière la pièce maîtresse, des coussins de velours sur
//   des étagères de pierre, l'or chaud ;
// - arène = la salle des trophées des champions : des socles de pierre cerclés de bronze, d'argent et d'or, la médaille de
//   la ligue du joueur sur le grand socle.
// Mêmes objets, mêmes prix, même achat (buyExchange) qu'avant. Style : sections/boutiques-modes.css.
// Variante `compact` (onglet « Échanges » de la boutique, où les deux boutiques sont l'une sous l'autre) : une seule
// vitrine par boutique, son enseigne et la bourse en haut, les objets debout côte à côte sur une étagère de pierre d'un
// bord à l'autre, le prix sur la face de l'étagère ; la plus chère au bout, sous la lumière.
import { useState } from 'preact/hooks';
import type { ShopItem } from '../../../core/data/modes';
import { ITEM_COLORS } from '../../art';
import { fmt, t } from '../../i18n';
import { buyExchange } from '../../state/actions';
import { useGame } from '../../state/store';
import { Art, Icon } from '../kit';
import { btClass } from '../buttons';
import { open } from '../nav';
import { Sparkles } from './boutique-kit';
import './boutique.css';
import './boutiques-modes.css';

type Kind = 'guild' | 'arena';
const CURRENCY: Record<Kind, 'guildCoins' | 'arenaTokens'> = { guild: 'guildCoins', arena: 'arenaTokens' };

/** Le contenu d'un objet : sa monnaie (ou son équipement) et sa quantité. */
function content(x: ShopItem): [string, number] {
  const [k, v] = Object.entries(x.reward)[0] ?? ['gold', 0];
  return [k, v ?? 0];
}
const artOf = (k: string, v: number) => (k === 'item' ? `weapon-${v}` : k === 'gold' ? 'goldPile' : k);

/** La quantité sous le picto : « ×20 », l'or tel quel (« 20 k »), la couleur d'un équipement. */
function Qty({ x }: { x: ShopItem }) {
  const [k, v] = content(x);
  if (k === 'item') return <span class="mx-qty mx-rar" style={{ '--rar': ITEM_COLORS[v] } as never}>{t(`item.${v}`)}</span>;
  return <span class="mx-qty">{k === 'gold' ? fmt(v) : `×${fmt(v)}`}</span>;
}

function Price({ kind, x, poor, size, onBuy }: { kind: Kind; x: ShopItem; poor: boolean; size: 's' | 'm'; onBuy: () => void }) {
  return (
    <button class={`mx-price ${btClass('or', size)}`} disabled={poor} onClick={onBuy}>
      <Icon name={CURRENCY[kind]} size={size === 'm' ? 24 : 20} /><span>{fmt(x.cost)}</span>
    </button>
  );
}

/** Le moment de l'achat : la case saute, un éclair, le picto s'envole, des étincelles jaillissent. */
function Burst({ art }: { art: string }) {
  return <><i class="lg-flash" /><Art name={art} class="lg-fly" /><Sparkles n={7} burst /></>;
}

export function ModeShop({ kind, items, league, crest, compact }: { kind: Kind; items: ShopItem[]; league?: string; crest?: string; compact?: boolean }) {
  const s = useGame();
  const cur = CURRENCY[kind];
  const have = s.wallet[cur];
  const [burst, setBurst] = useState('');
  // la pièce maîtresse : la plus chère ; les autres sur l'étagère, de la moins chère à la plus chère
  const feat = items.reduce((a, b) => (b.cost > a.cost ? b : a), items[0]!);
  const rest = items.filter((x) => x !== feat).sort((a, b) => a.cost - b.cost);
  const title = t(kind === 'guild' ? 'guild.shop' : 'arena.shop');
  const buy = (x: ShopItem) => {
    if (burst) return;
    const gain = buyExchange(kind, x.id);
    if (!gain) return;
    setBurst(x.id);
    setTimeout(() => { setBurst(''); open({ type: 'gain', title, gain }); }, 720);
  };
  if (compact) {
    const all = [...rest, feat];
    return (
      <div class={`mx mx-${kind} mx-compact${league ? ` mx-lg-${league}` : ''}`}>
        <span class="mx-bg">
          <i class="mx-light" />
          {kind === 'arena' && <i class="mx-beam" />}
          <i class="mx-shelf" />
        </span>
        <header class="mx-head">
          <span class="mx-sign">
            <Icon name={kind === 'arena' ? (league ? `league-${league}` : 'arena') : crest ?? 'guild'} size={30} />
            <strong>{t(kind === 'arena' ? 'adv.arena' : 'nav.guild')}</strong>
          </span>
          <span class="mx-purse"><Icon name={cur} size={30} /><b>{fmt(have)}</b></span>
        </header>
        <div class="mx-row">
          {all.map((x, i) => {
            const [k, v] = content(x);
            const poor = have < x.cost;
            const top = x === feat;
            return (
              <div class={`mx-card mx-tier-${i}${top ? ' mx-top' : ''}${poor ? ' mx-poor' : ''}${burst === x.id ? ' mx-burst' : ''}`}>
                <span class="mx-stage">
                  <i class="lg-glow" />
                  <Art name={artOf(k, v)} class="mx-art" />
                  <i class={kind === 'guild' ? 'mx-cushion' : 'mx-plinth'} />
                  {top && <Sparkles n={4} />}
                </span>
                {top && <span class="mx-tag"><Icon name="crown" size={16} />{t(`mx.best.${kind}`)}</span>}
                <Qty x={x} />
                <Price kind={kind} x={x} poor={poor} size="s" onBuy={() => buy(x)} />
                {burst === x.id && <Burst art={artOf(k, v)} />}
              </div>
            );
          })}
        </div>
      </div>
    );
  }
  const [fk, fv] = content(feat);
  const fArt = artOf(fk, fv);
  return (
    <div class={`mx mx-${kind}${league ? ` mx-lg-${league}` : ''}`}>
      <div class={`mx-feat${have < feat.cost ? ' mx-poor' : ''}${burst === feat.id ? ' mx-burst' : ''}`}>
        <span class="mx-bg">
          <i class="mx-light" />
          {kind === 'guild' ? <i class="mx-banner"><Icon name={crest ?? 'guild'} size={30} /></i> : <i class="mx-beam" />}
          <i class="mx-floor" />
        </span>
        <span class="mx-show">
          <i class="lg-glow" />
          <Art name={fArt} class="mx-art" />
          <i class={kind === 'guild' ? 'mx-cushion' : 'mx-plinth'} />
          <span class="mx-tag"><Icon name={kind === 'arena' && league ? `league-${league}` : 'crown'} size={20} />{t(`mx.best.${kind}`)}</span>
          <Sparkles n={5} />
        </span>
        <div class="mx-feat-text">
          <span class="mx-purse"><Icon name={cur} size={30} /><b>{fmt(have)}</b></span>
          <span class="mx-name"><strong>{fk === 'item' ? t('mx.gear') : t(`cur.${fk}`)}</strong><Qty x={feat} /></span>
          <Price kind={kind} x={feat} poor={have < feat.cost} size="m" onBuy={() => buy(feat)} />
        </div>
        {burst === feat.id && <Burst art={fArt} />}
      </div>
      <div class="mx-row">
        {rest.map((x, i) => {
          const [k, v] = content(x);
          const poor = have < x.cost;
          return (
            <div class={`mx-card mx-tier-${i}${poor ? ' mx-poor' : ''}${burst === x.id ? ' mx-burst' : ''}`}>
              <span class="mx-stage">
                <i class="lg-glow" />
                <Art name={artOf(k, v)} class="mx-art" />
                <i class={kind === 'guild' ? 'mx-cushion' : 'mx-plinth'} />
              </span>
              <Qty x={x} />
              <Price kind={kind} x={x} poor={poor} size="s" onBuy={() => buy(x)} />
              {burst === x.id && <Burst art={artOf(k, v)} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}
