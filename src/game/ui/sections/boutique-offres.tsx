// La vitrine de la boutique (vague 3, 26/11 : « que ça donne envie d'acheter ») : l'offre du moment en grand (héros
// Légendaire en pied posé à côté du cadeau), les autres offres en cases, les gemmes en piles de plus en plus grosses.
// Mêmes offres, mêmes prix, même achat simulé qu'avant (le serveur jugera plus tard). Style : sections/boutique.css.
// Le passe (PassTab) : la voie gratuite à gauche, la voie premium (pierre d'améthyste cerclée d'or) à droite, les paliers
// enfilés sur une piste d'or qui se remplit jusqu'au niveau du joueur ; gros paliers tous les 5, grand final au 30.
import { useEffect, useRef, useState } from 'preact/hooks';
import { HEROES } from '../../../core/data/heroes';
import {
  GEMS_PER_SUMMON, MONTHLY_CARD, OFFERS, PASS_LEVELS, PASS_POINTS_PER_LEVEL, RED_SCROLLS, type Offer, type Reward,
} from '../../../core/data/modes';
import { fmt, t } from '../../i18n';
import { buyRedScroll, claimPass, passLevel, redScrollsBought } from '../../state/actions';
import { open } from '../nav';
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

/** Le héros qui pose dans la vitrine : un Légendaire dessiné. */
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

/** Ce que donne la voie premium, en grand sur la carte à prendre (les quatre plus belles monnaies). */
const PASS_SHOW = (['gems', 'scrolls', 'crystals', 'dust'] as const).filter((k) => PASS_TOTAL[k]);

/** Le passe premium à prendre, en tête de l'onglet du passe (même achat) : tout ce qu'il donne, et ce qu'il vaut. */
export function PassBuy({ onBuy }: { onBuy: () => void }) {
  const o = OFFERS.find((x) => x.kind === 'pass');
  if (!o) return null;
  const x = valueX(o);
  return (
    <div class="bq-passbuy">
      <i class="bq-pb-light" />
      <span class="bq-stage"><i class="lg-glow" /><Art name="offer-pass" class="bq-art" /><Sparkles n={4} /></span>
      <span class="bq-pb-name"><strong>{t('offer.pass')}</strong>{x > 0 && <span class="bq-x">{t('bq.value', { n: x })}</span>}</span>
      <Price o={o} soldOut={false} size="m" onBuy={onBuy} />
      <span class="bq-pb-total">
        {PASS_SHOW.map((k) => <span class="bq-chip"><Icon name={k} size={24} /><b>{fmt(PASS_TOTAL[k] ?? 0)}</b></span>)}
      </span>
    </div>
  );
}

// ---------- Le passe ----------

/** L'ordre des gains, du plus précieux au plus commun : le premier est montré en grand. */
const RANK = ['scrolls', 'crystals', 'gems', 'dust', 'basicScrolls', 'essence', 'gold'];
const gains = (r: Reward) => (Object.entries(r) as [string, number][]).sort((a, b) => RANK.indexOf(a[0]) - RANK.indexOf(b[0]));

/** Les gains d'un palier : le principal en grand (picto et chiffre), les autres en petites pilules à côté. */
function Loot({ reward, list }: { reward: Reward; list?: boolean }) {
  const all = gains(reward);
  if (list) return <span class="ps-all">{all.map(([k, v]) => <span class="ps-mini"><Icon name={k} size={24} /><b>{fmt(v)}</b></span>)}</span>;
  const [[k, v] = ['gold', 0], ...more] = all;
  return (
    <span class="ps-loot">
      <span class="ps-main"><Icon name={k} size={34} /><b>{fmt(v)}</b></span>
      {more.length > 0 && <span class="ps-more">{more.map(([mk, mv]) => <span class="ps-mini"><Icon name={mk} size={16} /><b>{fmt(mv)}</b></span>)}</span>}
    </span>
  );
}

type CellState = 'done' | 'ready' | 'wait' | 'locked';

/** Une case de palier : à prendre (elle luit), prise (cochée), pas encore, ou fermée (premium pas pris : un cadenas). */
function PassCell({ reward, state, prem, burst, list, onClaim }: {
  reward: Reward; state: CellState; prem?: boolean; burst: boolean; list?: boolean; onClaim: () => void;
}) {
  return (
    <button class={`ps-cell ps-${state}${prem ? ' ps-prem' : ''}${burst ? ' ps-burst' : ''}`} aria-disabled={state !== 'ready'}
      onClick={() => state === 'ready' && onClaim()}>
      <Loot reward={reward} list={list} />
      {state === 'done' && <span class="ps-check"><Sign name="check" k={1.1} /></span>}
      {state === 'locked' && <span class="ps-lock"><Icon name="lock" size={18} /></span>}
      {burst && <><i class="lg-flash" /><Sparkles n={7} burst /></>}
    </button>
  );
}

/** L'onglet du passe : le niveau, la carte premium à prendre, puis les 30 paliers sur leur piste. */
export function PassTab({ onBuy }: { onBuy: () => void }) {
  const s = useGame();
  const level = passLevel(s);
  const prem = s.shop.passPremium;
  const pts = level >= PASS_LEVELS.length ? PASS_POINTS_PER_LEVEL : s.pass.points % PASS_POINTS_PER_LEVEL;
  const [burst, setBurst] = useState('');
  const list = useRef<HTMLDivElement>(null);
  const state = (i: number, p: boolean): CellState =>
    (p ? s.pass.claimedPremium : s.pass.claimedFree).includes(i) ? 'done' : p && !prem ? 'locked' : i < level ? 'ready' : 'wait';
  const claim = (i: number, p: boolean) => {
    if (!claimPass(i, p)) return;
    setBurst(`${i}${p ? 'p' : 'f'}`);
    setTimeout(() => setBurst(''), 800);
  };
  const last = PASS_LEVELS.length - 1;
  // à l'ouverture, la piste se place sur le premier palier à prendre (sinon sur le niveau du joueur)
  const firstReady = PASS_LEVELS.findIndex((_, i) => state(i, false) === 'ready' || state(i, true) === 'ready');
  const go = Math.min(last, firstReady >= 0 ? firstReady : level);
  useEffect(() => {
    const el = list.current;
    const row = el?.querySelector<HTMLElement>('.ps-go');
    if (el && row) el.scrollTop = Math.max(0, row.offsetTop - 6);
  }, []);
  const cell = (i: number, p: boolean, lst?: boolean) => (
    <PassCell reward={p ? PASS_LEVELS[i]!.premium : PASS_LEVELS[i]!.free} state={state(i, p)} prem={p} list={lst}
      burst={burst === `${i}${p ? 'p' : 'f'}`} onClaim={() => claim(i, p)} />
  );
  return (
    <div class={`ps${prem ? ' ps-has' : ''}`}>
      <div class="ps-head">
        <span class="ps-badge"><b>{level}</b></span>
        <span class="ps-prog">
          <span class="ps-prog-top"><strong>{t('pass.level', { n: level })}</strong><small>{t('pass.points', { n: pts, m: PASS_POINTS_PER_LEVEL })}</small></span>
          <span class="ps-bar"><i style={{ width: `${(pts / PASS_POINTS_PER_LEVEL) * 100}%` }} /></span>
        </span>
      </div>
      {!prem && <PassBuy onBuy={onBuy} />}
      <div class="ps-cols"><span>{t('pass.free')}</span><span /><span class="ps-cols-prem"><Icon name="crown" size={20} />{t('pass.premium')}</span></div>
      <div class="ps-list" ref={list}>
        {PASS_LEVELS.slice(0, last).map((_, i) => (
          <div class={`ps-row${(i + 1) % 5 === 0 ? ' ps-big' : ''}${i < level ? ' ps-on' : ''}${i === level ? ' ps-now' : ''}${i === go ? ' ps-go' : ''}`}
            style={{ '--fill': `${i < level ? 100 : i === level ? (pts / PASS_POINTS_PER_LEVEL) * 50 : 0}%` } as never}>
            {cell(i, false)}
            <span class="ps-node"><b>{i + 1}</b></span>
            {i === level && <i class="ps-here" />}
            {cell(i, true)}
          </div>
        ))}
        <div class={`ps-final${last < level ? ' ps-on' : ''}${last === go ? ' ps-go' : ''}`}>
          <span class="ps-final-top"><span class="ps-node"><b>{last + 1}</b></span></span>
          <div class="ps-final-row">
            {cell(last, false, true)}
            <span class="ps-final-show">
              <i class="lg-glow" /><Art name="chestReady" class="ps-final-art" /><i class="ps-final-plinth" /><Sparkles n={6} />
              <span class="ps-final-tag">{t('ps.final')}</span>
            </span>
            {cell(last, true, true)}
          </div>
        </div>
      </div>
    </div>
  );
}

/** Le parchemin rouge (portail spécial) contre des gemmes, quelques-uns par semaine (onglet Échanges). */
export function RedScrollOffer() {
  const s = useGame();
  const left = RED_SCROLLS.gemsPerWeek - redScrollsBought(s);
  const poor = s.wallet.gems < RED_SCROLLS.gems;
  return (
    <div class={`bq-card bq-red${left <= 0 ? ' bq-out' : ''}`}>
      <span class="bq-stage"><i class="lg-glow" /><Art name="redScrolls" class="bq-art" />{left > 0 && <Sparkles n={3} />}</span>
      <span class="bq-red-text">
        <strong>{t('cur.redScrolls')}</strong>
        <span class="bq-red-left"><b>{Math.max(0, left)}</b>/{RED_SCROLLS.gemsPerWeek}</span>
      </span>
      <button class={`bq-price bq-red-price ${btClass('or', 'm')}`} disabled={left <= 0 || poor}
        onClick={() => { const gain = buyRedScroll(); if (gain) open({ type: 'gain', title: t('cur.redScrolls'), gain }); }}>
        {left <= 0 ? <Sign name="check" k={1.6} /> : <><Icon name="gems" size={22} />{fmt(RED_SCROLLS.gems)}</>}
      </button>
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
