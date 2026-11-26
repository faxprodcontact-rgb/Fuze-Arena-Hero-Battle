// Le Colisée (26/11/2026) : PvP en duels, équipes de 3, classement de la semaine par ligue.
// La page (onglet Aventure, tuile « Colisée ») : la ligue et la place, trois onglets (classement du groupe avec les zones de
// montée et de descente, récompenses par place, boutique des insignes), puis en bas l'équipe (ordre de passage), les
// combats du jour et « Combattre ». Les fenêtres (adversaire, combat, résultat, fin de semaine, équipe) sont posées au-dessus
// de toute l'application (portail dans `.app`), au milieu de l'écran. Mise en page : sections/colisee.css (classes « col- »).
import '../sections/colisee.css';
import { createPortal } from 'preact/compat';
import { useEffect, useRef, useState } from 'preact/hooks';
import type { ComponentChildren } from 'preact';
import { rankZone, rankReward } from '../../../core/coliseum';
import { COLISEUM, COLISEUM_LEAGUES, COLISEUM_RANK_REWARDS, COLISEUM_SHOP } from '../../../core/data/coliseum';
import { heroDef } from '../../../core/data/heroes';
import { heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { runColiseumFight } from '../../scenes';
import {
  buyColiseumFight, buyExchange, claimColiseumWeek, coliseumExtraCost, coliseumFightsLeft, coliseumSetup, coliseumStandings,
  coliseumTeam, coliseumTeamPower, coliseumWeekEnd, findColiseumFoe, finishColiseum, setColiseumTeam,
  type ColiseumFightResult,
} from '../../state/actions';
import { heroPower, sortedHeroes } from '../../state/selectors';
import { now, useGame } from '../../state/store';
import type { ColiseumFoe } from '../../state/types';
import { Halo } from '../anim';
import { btClass } from '../buttons';
import { Art, Btn, Cur, HeroCard, Icon, Modal, Stars } from '../kit';
import { open, openSub, toast } from '../nav';
import { Tries } from './adventure';
import { ModeShop } from '../sections/boutiques-modes';

/** Le picto de chaque ligue (Champion : le blason à la couronne). */
export const LEAGUE_ICON = (l: number) => (COLISEUM_LEAGUES[l] === 'champion' ? 'emblem-0' : `league-${COLISEUM_LEAGUES[l]}`);
const leagueName = (l: number) => t(`league.${COLISEUM_LEAGUES[l]}`);

/** Les fenêtres du Colisée : au-dessus de toute l'application (comme les autres fenêtres du jeu). */
function Over({ children }: { children: ComponentChildren }) {
  const host = typeof document !== 'undefined' ? document.querySelector('.app') : null;
  return host ? createPortal(<>{children}</>, host) : <>{children}</>;
}

/** Temps jusqu'à la fin de la semaine : « 3 j 4 h », ou heures et minutes le dernier jour. */
function weekLeft(ms: number): string {
  const h = Math.max(0, Math.floor(ms / 3.6e6));
  if (h >= 24) return t('col.days', { d: Math.floor(h / 24), h: h % 24 });
  const m = Math.max(0, Math.floor((ms % 3.6e6) / 6e4));
  return `${h} h ${String(m).padStart(2, '0')}`;
}

/** Une place de la récompense (« 1 », « 4–10 »). */
const range = (r: { from: number; to: number }) => (r.from === r.to ? `${r.from}` : `${r.from}–${r.to}`);

type Tab = 'ranking' | 'rewards' | 'shop';
type Step = { kind: 'foe'; foe: ColiseumFoe } | { kind: 'fight'; foe: ColiseumFoe } | { kind: 'result'; res: ColiseumFightResult } | { kind: 'team' } | null;

export function Coliseum() {
  const s = useGame();
  const c = s.coliseum;
  const [tab, setTab] = useState<Tab>('ranking');
  const [step, setStep] = useState<Step>(null);
  if (!c) return null;
  const table = coliseumStandings(s);
  const me = table.find((r) => r.idx === -1)!;
  const left = coliseumFightsLeft(s);
  const extra = coliseumExtraCost(s);

  const fight = () => {
    if (left <= 0) {
      if (extra === null) return;
      if (s.wallet.gems < extra) return toast(t('col.gems'));
      if (!buyColiseumFight()) return;
    }
    const foe = findColiseumFoe();
    if (foe) setStep({ kind: 'foe', foe });
  };

  return (
    <>
      <header class="av-head">
        <button class="av-back bt-rond bt-galet" aria-label={t('back')} onClick={() => openSub(null)} />
        <h1>{t('adv.defense')}</h1>
        <div class="av-head-side"><Cur k="badge" n={s.wallet.badge} /></div>
      </header>
      <section class="col-page">
        <div class={`col-league league-${COLISEUM_LEAGUES[c.league]}`}>
          <Icon name={LEAGUE_ICON(c.league)} size={56} />
          <div class="col-league-main">
            <strong>{leagueName(c.league)}</strong>
            <span class="col-league-sub"><b>{t('col.rank', { n: me.rank })}</b> · {fmt(c.points)} {t('col.pts')}</span>
          </div>
          <span class="col-ends"><Icon name="clock" size={16} />{weekLeft(coliseumWeekEnd() - now())}</span>
        </div>
        <div class="av-seg col-tabs bt-rail" role="tablist">
          {(['ranking', 'rewards', 'shop'] as Tab[]).map((x) => (
            <button class={tab === x ? `on ${btClass('basalte', 's')}` : ''} onClick={() => setTab(x)}>
              <Icon name={x === 'ranking' ? 'ranking' : x === 'rewards' ? 'chestClosed' : 'shop'} size={20} />{t(`col.${x}`)}
            </button>
          ))}
        </div>
        <div class="col-body" key={tab}>
          {tab === 'ranking' && <Ranking league={c.league} />}
          {tab === 'rewards' && <Rewards league={c.league} rank={me.rank} />}
          {tab === 'shop' && <Shop />}
        </div>
        <div class="col-foot">
          <button class="col-team" onClick={() => setStep({ kind: 'team' })} aria-label={t('col.team')}>
            {coliseumTeam(s).map((h, i) => (
              <span class="col-team-face"><img src={heroImage(h.defId)} alt="" /><i>{i + 1}</i></span>
            ))}
            <span class="col-team-pow"><Icon name="power" size={14} />{fmt(coliseumTeamPower(s))}</span>
          </button>
          <div class="col-go">
            <Tries left={left} max={COLISEUM.freeFights + c.bought} />
            {left > 0 || extra === null ? (
              <Btn kind="green" wide disabled={left <= 0} onClick={fight}>{t('col.fight')}</Btn>
            ) : (
              <Btn kind="gold" wide onClick={fight}><span class="col-more">{t('col.more')}<Cur k="gems" n={extra} /></span></Btn>
            )}
          </div>
        </div>
      </section>
      {c.pending && <WeekResult />}
      {step?.kind === 'team' && <TeamPicker onDone={() => setStep(null)} />}
      {step?.kind === 'foe' && <Versus foe={step.foe} onGo={() => setStep({ kind: 'fight', foe: step.foe })} onClose={() => setStep(null)} />}
      {step?.kind === 'fight' && (
        <Fight foe={step.foe} onDone={() => {
          const res = finishColiseum();
          setStep(res ? { kind: 'result', res } : null);
        }} />
      )}
      {step?.kind === 'result' && <Result res={step.res} onClose={() => setStep(null)} />}
    </>
  );
}

/** Le classement du groupe : les 3 premiers (montée) en vert, les 3 derniers (descente) en corail, le joueur en or. */
function Ranking({ league }: { league: number }) {
  const s = useGame();
  const table = coliseumStandings(s);
  const list = useRef<HTMLOListElement>(null);
  // le joueur au milieu de la liste à l'ouverture
  useEffect(() => {
    const el = list.current?.querySelector<HTMLElement>('.me');
    const box = list.current?.parentElement;
    if (!el || !box) return;
    const at = el.getBoundingClientRect().top - box.getBoundingClientRect().top;
    box.scrollTop += at - box.clientHeight / 2 + el.clientHeight / 2;
  }, []);
  return (
    <ol class="col-rows" ref={list}>
      {table.map((r) => {
        const zone = rankZone(league, r.rank);
        return (
          <li class={`col-row${zone ? ` zone-${zone}` : ''}${r.idx === -1 ? ' me' : ''}`}>
            <span class="col-rank">{r.rank}</span>
            <span class="col-name">{r.idx === -1 ? s.name || t('col.me') : r.name}</span>
            {zone && <i class={`col-arrow ${zone}`} aria-label={t(zone === 'up' ? 'col.up' : 'col.down')} />}
            <span class="col-pts">{fmt(r.points)}</span>
          </li>
        );
      })}
    </ol>
  );
}

/** Les récompenses de la semaine selon la place (dans la ligue du joueur), et le chemin des ligues. */
function Rewards({ league, rank }: { league: number; rank: number }) {
  return (
    <div class="col-rewards">
      <div class="col-ladder">
        {COLISEUM_LEAGUES.map((_, l) => (
          <span class={`col-step${l === league ? ' on' : ''}${l < league ? ' done' : ''}`}><Icon name={LEAGUE_ICON(l)} size={l === league ? 40 : 30} /></span>
        ))}
      </div>
      <ol class="col-rows">
        {COLISEUM_RANK_REWARDS.map((tier) => {
          const r = rankReward(league, tier.from);
          const zone = rankZone(league, tier.from);
          return (
            <li class={`col-row col-tier${zone ? ` zone-${zone}` : ''}${rank >= tier.from && rank <= tier.to ? ' me' : ''}`}>
              <span class={`col-place p${tier.from <= 3 ? tier.from : 0}`}>{range(tier)}</span>
              {zone && <i class={`col-arrow ${zone}`} />}
              <span class="col-gifts"><Cur k="gems" n={r.gems} /><Cur k="badge" n={r.badge} /></span>
            </li>
          );
        })}
        <li class="col-row col-tier zone-down">
          <span class="col-place">{range({ from: COLISEUM.groupSize - COLISEUM.relegate + 1, to: COLISEUM.groupSize })}</span>
          <i class="col-arrow down" />
          <span class="col-gifts"><Icon name={LEAGUE_ICON(Math.max(0, league - 1))} size={26} /></span>
        </li>
      </ol>
    </div>
  );
}

function Shop() {
  const s = useGame();
  const l = s.coliseum?.league ?? 0;
  return <ModeShop kind="coliseum" items={COLISEUM_SHOP} league={COLISEUM_LEAGUES[l] === 'champion' ? undefined : COLISEUM_LEAGUES[l]} />;
}

/** Une équipe en 3 visages (ordre de passage). */
function Faces({ ids, foe }: { ids: string[]; foe?: boolean }) {
  return (
    <div class={`col-faces${foe ? ' foe' : ''}`}>
      {ids.map((id, i) => <span class="col-vface"><img src={heroImage(id)} alt={heroDef(id).name} /><i>{i + 1}</i></span>)}
    </div>
  );
}

/** L'adversaire tiré : les deux équipes face à face, puis « Combattre ». */
function Versus({ foe, onGo, onClose }: { foe: ColiseumFoe; onGo: () => void; onClose: () => void }) {
  const s = useGame();
  const mine = coliseumTeam(s);
  const foePow = foe.team.reduce((a, m) => a + heroPower(s, { uid: -1, defId: m.defId, stars: m.stars, level: m.level }), 0);
  return (
    <Over>
      <Modal center title={t('adv.defense')} onClose={onClose}>
        <div class="col-vs">
          <div class="col-side">
            <strong>{s.name || t('col.me')}</strong>
            <Faces ids={mine.map((h) => h.defId)} />
            <span class="av-power"><Icon name="power" size={16} /><b>{fmt(coliseumTeamPower(s))}</b></span>
          </div>
          <span class="col-vs-mark">VS</span>
          <div class="col-side">
            <strong>{foe.name}</strong>
            <Faces ids={foe.team.map((m) => m.defId)} foe />
            <span class="av-power"><Icon name="power" size={16} /><b>{fmt(foePow)}</b></span>
            <small>{fmt(foe.points)} {t('col.pts')}</small>
          </div>
        </div>
        <Btn kind="green" wide class="btn-fight" onClick={onGo}>{t('col.fight')}</Btn>
      </Modal>
    </Over>
  );
}

/** Le combat (scène Phaser plein écran). */
function Fight({ foe, onDone }: { foe: ColiseumFoe; onDone: () => void }) {
  const s = useGame();
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const setup = coliseumSetup();
    if (!host.current || !setup) return onDone();
    return runColiseumFight(host.current, { setup, names: { me: s.name || t('col.me'), foe: foe.name }, done: () => onDone() });
  }, []);
  return <Over><div class="battle"><div class="battle-host" ref={host} /></div></Over>;
}

/** Le résultat d'un combat : victoire ou défaite, les points gagnés ou perdus, la nouvelle place. */
function Result({ res, onClose }: { res: ColiseumFightResult; onClose: () => void }) {
  const up = res.rankAfter < res.rankBefore;
  return (
    <Over>
      <Modal center title={t('adv.defense')} onClose={onClose}>
        <div class="result-stage">{res.win && <Halo size={164} />}<Art class={`result-art ${res.win ? 'win' : 'lose'}`} name={res.win ? 'trophy' : 'defeat'} /></div>
        <div class={`result-title ${res.win ? 'win' : 'lose'}`}>{res.win ? t('col.win') : t('col.loss')}</div>
        <div class="col-delta">
          <span class={`col-pts-delta ${res.delta >= 0 ? 'col-up' : 'col-dn'}`}>{res.delta >= 0 ? '+' : '−'}{Math.abs(res.delta)} {t('col.pts')}</span>
          <span class="col-rank-move">
            <b>{res.rankBefore}</b><i class={`col-arrow ${up ? 'up' : res.rankAfter > res.rankBefore ? 'down' : 'same'}`} /><b>{res.rankAfter}</b>
          </span>
        </div>
        <div class="gain">{Object.entries(res.gain.currencies).map(([k, v]) => <Cur k={k} n={v ?? 0} big />)}</div>
        <Btn kind="green" wide onClick={onClose}>{t('ok')}</Btn>
      </Modal>
    </Over>
  );
}

/** Fin de la semaine : la place, la ligue qui monte (fête) ou descend, et la récompense à prendre. */
function WeekResult() {
  const s = useGame();
  const p = s.coliseum!.pending!;
  const move = p.next > p.league ? 'up' : p.next < p.league ? 'down' : 'stay';
  const claim = () => {
    const gain = claimColiseumWeek();
    if (gain) open({ type: 'gain', title: t('adv.defense'), gain });
  };
  return (
    <Over>
      <Modal center title={t('col.week')} onClose={claim}>
        <div class={`col-week ${move}`}>
          <div class="col-week-leagues">
            {move !== 'stay' && <Icon name={LEAGUE_ICON(p.league)} size={54} />}
            {move !== 'stay' && <i class={`col-arrow big ${move}`} />}
            <span class="col-week-new">{move === 'up' && <Halo size={150} />}<Icon name={LEAGUE_ICON(p.next)} size={96} /></span>
          </div>
          <strong class="col-week-title">{move === 'up' ? t('col.promoted') : move === 'down' ? t('col.relegated') : t('col.stay')}</strong>
          <span class="col-week-league">{leagueName(p.next)}</span>
          <span class="col-week-rank">{t('col.rank', { n: p.rank })}</span>
        </div>
        <div class="gain"><Cur k="gems" n={p.gems} big /><Cur k="badge" n={p.badge} big /></div>
        <Btn kind="gold" wide onClick={claim}>{t('claim')}</Btn>
      </Modal>
    </Over>
  );
}

/** Choisir les 3 héros et leur ordre de passage : toucher un héros l'ajoute à la première place libre, le retoucher l'enlève. */
function TeamPicker({ onDone }: { onDone: () => void }) {
  const s = useGame();
  const [team, setTeam] = useState<number[]>(() => coliseumTeam(s).map((h) => h.uid));
  const want = Math.min(COLISEUM.team, s.heroes.length);
  const toggle = (uid: number) => setTeam(team.includes(uid) ? team.filter((u) => u !== uid) : team.length < want ? [...team, uid] : [...team.slice(0, want - 1), uid]);
  const save = () => {
    if (team.length === want && setColiseumTeam(team)) onDone();
  };
  const power = team.reduce((a, u) => {
    const h = s.heroes.find((x) => x.uid === u);
    return a + (h ? heroPower(s, h) : 0);
  }, 0);
  return (
    <Over>
      <Modal center title={t('col.order')} onClose={onDone}>
        <div class="col-pickwrap">
        <div class="col-pick">
          {Array.from({ length: COLISEUM.team }, (_, i) => {
            const h = s.heroes.find((x) => x.uid === team[i]);
            return (
              <button class={`col-slot${h ? '' : ' empty'}`} onClick={() => h && toggle(h.uid)}>
                <i class="col-slot-n">{i + 1}</i>
                {h ? <><img src={heroImage(h.defId)} alt="" /><Stars stars={h.stars} /></> : <Icon name="unknownHero" size={40} />}
              </button>
            );
          })}
        </div>
        <span class="av-power col-pick-pow"><Icon name="power" size={18} /><b>{fmt(power)}</b></span>
        <div class="roster col-roster">
          {sortedHeroes(s).map((h) => {
            const at = team.indexOf(h.uid);
            return (
              <div class="hcard-wrap">
                <HeroCard hero={h} small power={heroPower(s, h)} selected={at >= 0} badge={at >= 0 ? String(at + 1) : undefined} onClick={() => toggle(h.uid)} />
              </div>
            );
          })}
        </div>
        <Btn kind="green" wide disabled={team.length !== want} onClick={save}>{t('ok')}</Btn>
        </div>
      </Modal>
    </Over>
  );
}
