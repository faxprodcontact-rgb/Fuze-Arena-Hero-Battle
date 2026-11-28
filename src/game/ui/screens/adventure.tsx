// Aventure : les modes du quotidien (tour, missions, donjons, Événement, arène, Colisée).
// Style moderne (26/11/2026), onglet refait le 27/11 : six tuiles qui prennent tout l'écran (un petit paysage du mode dessiné
// par le code, TileScene de backdrop-adventure.tsx, son picto posé sur le sol, son nom, UNE information utile), sur un fond
// épuré. Chaque mode : une tête, son décor, une seule action. Mise en page dans sections/aventure.css (classes « av- »).
import '../sections/aventure.css';
import { sceneVar } from '../fond-image';
import { useEffect, useState } from 'preact/hooks';
import type { ComponentChildren } from 'preact';
import { stagePower } from '../../../core/data/campaign';
import {
  ARENA_FREE_TICKETS, ARENA_LEAGUES, ARENA_SHOP,
  DUNGEON_ATTEMPTS_PER_DAY, TOWER_STAGE_PER_FLOOR, UNLOCKS, type DungeonKind,
} from '../../../core/data/modes';
import { heroImage } from '../../art';
import { DUNGEON_CLAN, battleLook } from '../../look';
import { Figure } from '../hero-figure';
import { fmt, t } from '../../i18n';
import {
  arenaPlan, claimMission, dungeonAttemptsLeft, eventAbandon, eventBattle, eventChooseBonus, eventOf, eventPlan, eventTriesLeft, markSeen, missionEnd,
  missionTemplate, opponentPower, refreshOpponents, towerPlan,
} from '../../state/actions';
import { isUnlocked, teamPower } from '../../state/selectors';
import { now, useGame } from '../../state/store';
import { ADVENTURE_ORDER, dots, isNew } from '../dots';
import { TeamStrip } from './heroes';
import { TileScene } from '../backdrop-adventure';
import { Coliseum, LEAGUE_ICON } from './coliseum';
import { COLISEUM_LEAGUES } from '../../../core/data/coliseum';
import { Art, Btn, Cur, Icon, Locked, duration, starText } from '../kit';
import { btClass } from '../buttons';
import { ModeShop } from '../sections/boutiques-modes';
import { open, openSub, prepare, startBattle, toast, type Sub } from '../nav';
import { EVENT_BONUS_VALUE, EVENT_LEVELS, EVENT_SCROLL_LEVELS, EVENT_TRIES_PER_DAY, eventStage, type EventBonus } from '../../../core/data/event';
import { FEATURED_BANNER } from '../../../core/data/summon';
import { heroByUid } from '../../state/selectors';

type Mode = (typeof ADVENTURE_ORDER)[number];

const leagueOf = (points: number) => [...ARENA_LEAGUES].reverse().find((l) => points >= l.from)!;
const DUNGEON_KINDS: DungeonKind[] = ['gold', 'essence', 'gear'];
/** Le grand picto de chaque donjon (la mine, la source, l'armurerie). */
export const DUNGEON_ART: Record<DungeonKind, string> = { gold: 'goldMine', essence: 'essenceSpring', gear: 'armory' };

/** L'information d'une tuile ouverte : une seule, la plus utile (un picto et un chiffre). */
function TileInfo({ f }: { f: Mode }) {
  const s = useGame();
  switch (f) {
    case 'tower':
      return <span class="av-chip"><Icon name="tower" size={16} />{t('tower.floor', { n: s.tower.floor + 1 })}</span>;
    case 'missions': {
      const live = s.daily.missions.filter((m) => !m.claimed && m.startedAt);
      if (live.some((m) => now() >= missionEnd(m))) return <span class="av-chip gold"><Icon name="chestReady" size={16} />{t('claim')}</span>;
      if (live.length) return <span class="av-chip"><Icon name="hourglass" size={16} />{duration(Math.min(...live.map(missionEnd)) - now())}</span>;
      return <span class="av-chip"><Icon name="missions" size={16} />{s.daily.missions.filter((m) => !m.claimed).length}</span>;
    }
    case 'dungeons': {
      const left = DUNGEON_KINDS.reduce((a, k) => a + dungeonAttemptsLeft(s, k), 0);
      return <span class={`av-chip${left ? '' : ' off'}`}>{t('dungeon.tries')} {left} / {DUNGEON_ATTEMPTS_PER_DAY * DUNGEON_KINDS.length}</span>;
    }
    case 'event': {
      const ev = eventOf(s);
      return ev.run
        ? <span class="av-chip gold">{t('event.level', { n: ev.run.level })} / {EVENT_LEVELS}</span>
        : <span class={`av-chip${eventTriesLeft(s) ? '' : ' off'}`}>{t('event.difficulty', { n: ev.difficulty })} · {eventTriesLeft(s)} / {EVENT_TRIES_PER_DAY}</span>;
    }
    case 'arena': {
      const l = leagueOf(s.arena.points).id;
      return <span class={`av-chip league-${l}`}><Icon name={`league-${l}`} size={16} />{t(`league.${l}`)}</span>;
    }
    case 'defense': {
      const l = s.coliseum?.league ?? 0;
      return <span class={`av-chip league-${COLISEUM_LEAGUES[l]}`}><Icon name={LEAGUE_ICON(l)} size={16} />{t(`league.${COLISEUM_LEAGUES[l]}`)}</span>;
    }
    default:
      return <span class="av-chip off">{t('soon')}</span>;
  }
}

export function AdventureScreen({ sub }: { sub: Sub }) {
  const s = useGame();
  if (sub) {
    return (
      <div class={`screen av-sub av-sub-${sub}`}>
        {sub === 'tower' && <Tower />}
        {sub === 'missions' && <Missions />}
        {sub === 'dungeons' && <Dungeons />}
        {sub === 'event' && <EventMode />}
        {sub === 'arena' && <Arena />}
        {sub === 'defense' && <Coliseum />}
      </div>
    );
  }
  return (
    <div class="screen adventure av-hub">
      {/* plus de titre ni de panorama (27/11) : les six tuiles prennent tout l'écran */}
      <h1 class="sr-only">{t('nav.adventure')}</h1>
      <div class="av-tiles">
        {ADVENTURE_ORDER.map((f) => {
          const unlocked = isUnlocked(s, f);
          const fresh = unlocked && isNew(s, f);
          return (
            <button
              class={`av-tile tile-${f}${unlocked ? '' : ' is-locked'}`}
              onClick={() => {
                if (!unlocked) return toast(t('locked', { n: UNLOCKS[f] }));
                markSeen(f);
                openSub(f);
              }}
            >
              {/* le petit paysage du mode, son picto posé sur le sol (jamais coupé : il tient dans la case) */}
              <span class="av-tile-scene">
                <TileScene mode={f} />
                <Art name={f === 'event' ? 'redScrolls' : f} class="av-tile-art" />
                {fresh && <span class="av-new">{t('new')}</span>}
                {!unlocked && <span class="av-lock"><Icon name="lock" size={30} /></span>}
              </span>
              <span class="av-tile-foot">
                <strong class="av-tile-name">{t(`adv.${f}`)}</strong>
                {unlocked ? <TileInfo f={f} /> : <Locked stage={UNLOCKS[f]} />}
              </span>
              {unlocked && !fresh && dots[f](s) && <span class="dot" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/** La tête d'un mode : retour rond, titre, et à droite l'information du mode (essais, monnaie…). */
function SubHead({ title, children }: { title: string; children?: ComponentChildren }) {
  return (
    <header class="av-head">
      <button class="av-back bt-rond bt-galet" aria-label={t('back')} onClick={() => openSub(null)} />
      <h1>{title}</h1>
      {children && <div class="av-head-side">{children}</div>}
    </header>
  );
}

/** La force de la section face à celle demandée (verte si elle suffit). */
function PowerVs({ need }: { need: number }) {
  const mine = teamPower(useGame());
  return (
    <span class={`av-power ${mine >= need ? 'ok' : 'low'}`}>
      <Icon name="power" size={18} /><b>{fmt(mine)}</b><small>/ {fmt(need)}</small>
    </span>
  );
}

/** La tour : le chemin des étages (les prochains au-dessus, celui à défier en grand, le dernier gagné dessous). */
function Tower() {
  const s = useGame();
  const floor = s.tower.floor + 1;
  const milestone = (n: number) => (n % 10 === 0 ? 'gems' : n % 5 === 0 ? 'scrolls' : null);
  return (
    <>
      <SubHead title={t('adv.tower')} />
      <section class="av-panel av-tower">
        <div class="av-scene av-grow av-floors" style={sceneVar(battleLook('tower', String(floor)).fond)}>
          {[3, 2, 1].map((k) => {
            const m = milestone(floor + k);
            return (
              <div class="av-floor up">
                <span>{t('tower.floor', { n: floor + k })}</span>
                {m && <Icon name={m} size={20} />}
              </div>
            );
          })}
          <div class="av-floor now">
            <Art name="tower" size={40} />
            <span>{t('tower.floor', { n: floor })}</span>
          </div>
          {s.tower.floor > 0 && <div class="av-floor done"><i class="av-check" /><span>{t('tower.floor', { n: s.tower.floor })}</span></div>}
        </div>
        <div class="av-rewards">
          <Cur k="essence" n={40 * floor} />
          {floor % 5 === 0 && <Cur k="scrolls" n={1} />}
          {floor % 10 === 0 && <Cur k="gems" n={100} />}
        </div>
        <div class="av-action">
          <PowerVs need={stagePower(floor * TOWER_STAGE_PER_FLOOR)} />
          <Btn kind="green" wide onClick={() => prepare(towerPlan())}>{t('tower.challenge')}</Btn>
        </div>
      </section>
    </>
  );
}

function Missions() {
  const s = useGame();
  const [, tick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => tick((x) => x + 1), 1000);
    return () => clearInterval(id);
  }, []);
  // les missions finies d'abord (à récupérer), puis celles en cours, puis celles à envoyer
  const rank = (m: (typeof s.daily.missions)[number]) => (!m.startedAt ? 2 : now() >= missionEnd(m) ? 0 : 1);
  const list = s.daily.missions.filter((m) => !m.claimed).sort((a, b) => rank(a) - rank(b));
  return (
    <>
      <SubHead title={t('adv.missions')} />
      <section class="av-list">
        {list.map((m) => {
          const tpl = missionTemplate(m);
          const end = missionEnd(m);
          const ready = !!m.startedAt && now() >= end;
          const running = !!m.startedAt && !ready;
          return (
            <div class={`av-row av-mission${ready ? ' ready' : running ? ' running' : ''}`}>
              <span class="av-row-icon"><Icon name={`mission-${tpl.id}`} size={44} /></span>
              <div class="av-row-main">
                <strong>{t(`mission.${tpl.id}`)}</strong>
                {running ? (
                  <div class="av-progress">
                    <span style={{ width: `${Math.min(100, ((now() - m.startedAt!) / (end - m.startedAt!)) * 100)}%` }} />
                    <b>{duration(end - now())}</b>
                  </div>
                ) : (
                  <div class="av-meta">
                    <span><Icon name="clock" size={14} />{tpl.hours} h</span>
                    <span>{starText(t('mission.need', { n: tpl.heroes, s: tpl.minStars }))}</span>
                  </div>
                )}
              </div>
              <div class="av-row-side">
                {tpl.reward.amount ? <Cur k={tpl.reward.kind} n={tpl.reward.amount} /> : <span class="cur"><Icon name={tpl.reward.kind} size={18} /> {tpl.reward.hours} h</span>}
                {!m.startedAt && <Btn kind="blue" small onClick={() => open({ type: 'mission', id: m.id })}>{t('send')}</Btn>}
                {running && (
                  <span class="av-faces small">{m.heroUids.map((u) => {
                    const h = s.heroes.find((x) => x.uid === u);
                    return h ? <span class="av-face"><img src={heroImage(h.defId)} alt="" /></span> : null;
                  })}</span>
                )}
                {ready && <Btn kind="gold" small onClick={() => {
                  const gain = claimMission(m.id);
                  if (gain) open({ type: 'gain', title: t(`mission.${tpl.id}`), gain });
                }}>{t('claim')}</Btn>}
              </div>
            </div>
          );
        })}
      </section>
    </>
  );
}

/** Les essais du jour en petites pastilles (pleines = restants). */
export function Tries({ left, max }: { left: number; max: number }) {
  return (
    <span class={`av-tries${left ? '' : ' none'}`}>
      {Array.from({ length: max }, (_, i) => <i class={i < left ? 'on' : ''} />)}
      <b>{left} / {max}</b>
    </span>
  );
}

function Dungeons() {
  const s = useGame();
  return (
    <>
      <SubHead title={t('adv.dungeons')} />
      <section class="av-list av-dungeons">
        {DUNGEON_KINDS.map((k) => {
          const left = dungeonAttemptsLeft(s, k);
          return (
            <button class={`av-dcard dungeon-${k}`} style={sceneVar(DUNGEON_CLAN[k])} onClick={() => open({ type: 'dungeon', kind: k })}>
              <Art name={DUNGEON_ART[k]} class="av-dcard-art" />
              <span class="av-dcard-text">
                <strong>{t(`dungeon.${k}`)}</strong>
                <span class="av-chip">{t('dungeon.level', { n: s.dungeons[k] })}</span>
              </span>
              <Tries left={left} max={DUNGEON_ATTEMPTS_PER_DAY} />
              {left > 0 && <span class="dot" />}
            </button>
          );
        })}
      </section>
    </>
  );
}

/** Le chemin des 20 niveaux : un serpentin qui monte (4 niveaux par rangée, le niveau 1 en bas à gauche), en unités
 * d'une boîte de 400 × 520. */
const PATH_W = 400, PATH_H = 520;
function nodePos(n: number): [number, number] {
  const r = Math.floor((n - 1) / 4), c = (n - 1) % 4;
  const col = r % 2 === 0 ? c : 3 - c;
  return [(col * PATH_W) / 3, PATH_H - (r * PATH_H) / 4];
}
/** Une courbe douce qui passe par tous les points (Catmull-Rom → Bézier). */
function smoothPath(pts: [number, number][]): string {
  if (pts.length < 2) return '';
  let d = `M${pts[0]![0]} ${pts[0]![1]}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] ?? pts[i]!, p1 = pts[i]!, p2 = pts[i + 1]!, p3 = pts[i + 2] ?? p2;
    const k = 0.22;
    d += ` C${(p1[0] + (p2[0] - p0[0]) * k).toFixed(1)} ${(p1[1] + (p2[1] - p0[1]) * k).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) * k).toFixed(1)} ${(p2[1] - (p3[1] - p1[1]) * k).toFixed(1)} ${p2[0]} ${p2[1]}`;
  }
  return d;
}
const BONUS_ICON: Record<EventBonus, string> = { heal: 'hp', atk: 'atk', def: 'def', revive: 'revive' };

/** Le mode Événement (27/11, à la place du boss du jour ; règles : core/data/event.ts). Un chemin de 20 niveaux sur le
 * décor d'un clan ; l'équipe inscrite et sa vie ; un choix de bonus tous les 2 niveaux ; on s'arrête entre deux combats. */
function EventMode() {
  const s = useGame();
  const ev = eventOf(s);
  const run = ev.run;
  const level = run?.level ?? 1;
  const left = eventTriesLeft(s);
  const all = Array.from({ length: EVENT_LEVELS }, (_, i) => nodePos(i + 1));
  const done = run ? all.slice(0, level) : [all[0]!];
  return (
    <>
      <SubHead title={t('adv.event')}>
        <Tries left={left} max={EVENT_TRIES_PER_DAY} />
      </SubHead>
      <section class="av-panel ev-panel">
        <div class="ev-head">
          <span class="ev-diff"><Icon name="redScrolls" size={20} />{t('event.difficulty', { n: ev.difficulty })}</span>
          <span class="ev-name">{t(`banner.${FEATURED_BANNER.id}`)}</span>
        </div>
        {/* le chemin, sur le décor du clan du niveau à jouer */}
        <div class="ev-map av-scene" style={sceneVar(battleLook('event', `${ev.difficulty}-${level}`).fond)}>
          <div class="ev-track">
          <svg class="ev-road" viewBox={`0 0 ${PATH_W} ${PATH_H}`} preserveAspectRatio="none" aria-hidden="true">
            <path d={smoothPath(all)} class="ev-road-edge" />
            <path d={smoothPath(all)} class="ev-road-in" />
            {run && level > 1 && <path d={smoothPath(done)} class="ev-road-done" />}
          </svg>
          {all.map(([x, y], i) => {
            const n = i + 1;
            const state = run && n < level ? 'done' : n === level ? 'now' : 'next';
            const boss = n % 5 === 0;
            return (
              <span class={`ev-node ${state}${boss ? ' boss' : ''}`} style={{ left: `${(x / PATH_W) * 100}%`, top: `${(y / PATH_H) * 100}%` }}>
                {boss ? <Icon name="dailyBoss" size={26} /> : <b>{n}</b>}
                {state === 'done' && <i class="ev-check" />}
                {EVENT_SCROLL_LEVELS.includes(n) && state !== 'done' && <span class="ev-prize"><Icon name="redScrolls" size={18} /></span>}
                {n % 2 === 0 && n < EVENT_LEVELS && state !== 'done' && <span class="ev-gift"><Icon name="gift" size={14} /></span>}
              </span>
            );
          })}
          </div>
        </div>
        {run ? <EventRunPanel /> : (
          <div class="av-action">
            <span class="av-power ev-need"><Icon name="power" size={18} /><small>{t('event.level', { n: 1 })}</small><b>{fmt(stagePower(eventStage(ev.difficulty, 1)))}</b></span>
            <Btn kind="green" wide disabled={left <= 0} onClick={() => prepare(eventPlan())}>{t('event.join')}</Btn>
          </div>
        )}
      </section>
      {run?.offer && <EventOffer offer={run.offer} />}
    </>
  );
}

/** La partie en cours : l'équipe (vie de chacun, morts éteints), les bonus gagnés, combattre ou abandonner. */
function EventRunPanel() {
  const s = useGame();
  const run = eventOf(s).run!;
  return (
    <div class="ev-run">
      <div class="ev-team">
        {run.team.map(([uid]) => {
          const h = heroByUid(s, uid);
          if (!h) return null;
          const hp = run.hp[uid] ?? 1;
          return (
            <span class={`ev-hero${hp > 0 ? '' : ' dead'}`}>
              <img src={heroImage(h.defId)} alt="" />
              <i class="ev-hp"><i style={{ width: `${Math.round(hp * 100)}%` }} /></i>
            </span>
          );
        })}
      </div>
      {(run.atk > 0 || run.def > 0) && (
        <div class="ev-buffs">
          {run.atk > 0 && <span class="ev-buff"><Icon name="atk" size={16} />+{Math.round(run.atk * 100)} %</span>}
          {run.def > 0 && <span class="ev-buff"><Icon name="def" size={16} />+{Math.round(run.def * 100)} %</span>}
        </div>
      )}
      <div class="row gap-s">
        <Btn tone="galet" small onClick={() => open({ type: 'confirm', text: t('event.quitAsk'), onYes: eventAbandon })}>{t('event.quit')}</Btn>
        <Btn kind="green" wide onClick={() => { const req = eventBattle(); if (req) startBattle(req); }}>
          {t('fight')} · {t('event.level', { n: run.level })}
        </Btn>
      </div>
    </div>
  );
}

/** Le choix d'un bonus (tous les 2 niveaux gagnés) : deux cartes, on en touche une. */
function EventOffer({ offer }: { offer: EventBonus[] }) {
  return (
    <div class="ev-offer-back">
      <div class="ev-offer">
        <h3>{t('event.pick')}</h3>
        <div class="ev-offer-cards">
          {offer.map((b) => (
            <button class={`ev-card ev-card-${b}`} onClick={() => eventChooseBonus(b)}>
              <Art name={BONUS_ICON[b]} class="ev-card-art" />
              <strong>{t(`event.bonus.${b}`)}</strong>
              <small>{t(`event.bonusText.${b}`, { p: Math.round(EVENT_BONUS_VALUE[b] * 100) })}</small>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function Arena() {
  const s = useGame();
  const [tab, setTab] = useState<'fight' | 'shop'>('fight');
  const left = ARENA_FREE_TICKETS - s.daily.arenaFights;
  const league = leagueOf(s.arena.points);
  const next = ARENA_LEAGUES[ARENA_LEAGUES.indexOf(league) + 1];
  const mine = teamPower(s);
  return (
    <>
      <SubHead title={t('adv.arena')}>
        <Cur k="arenaTokens" n={s.wallet.arenaTokens} />
      </SubHead>
      <section class="av-arena">
        <div class={`av-league league-${league.id}`}>
          <Icon name={`league-${league.id}`} size={58} />
          <div class="av-league-main">
            <div class="av-league-top"><strong>{t(`league.${league.id}`)}</strong><span><b>{fmt(s.arena.points)}</b> {t('arena.points')}</span></div>
            {next && (
              <div class="av-league-next">
                <div class="av-progress gold"><span style={{ width: `${Math.min(100, ((s.arena.points - league.from) / (next.from - league.from)) * 100)}%` }} /></div>
                <Icon name={`league-${next.id}`} size={24} />
              </div>
            )}
          </div>
        </div>
        <div class="av-seg bt-rail" role="tablist">
          <button class={tab === 'fight' ? `on ${btClass('basalte', 's')}` : ''} onClick={() => setTab('fight')}><Icon name="arena" size={20} />{t('adv.arena')}</button>
          <button class={tab === 'shop' ? `on ${btClass('basalte', 's')}` : ''} onClick={() => setTab('shop')}><Icon name="shop" size={20} />{t('arena.shop')}</button>
        </div>
        {tab === 'fight' ? (
          <>
            <TeamStrip />
            <div class="av-bar-row">
              <Tries left={left} max={ARENA_FREE_TICKETS} />
              <Btn kind="ghost" small onClick={refreshOpponents}>{t('arena.refresh')}</Btn>
            </div>
            {s.arena.opponents.map((o) => {
              const p = opponentPower(o);
              return (
                <div class="av-row av-opponent">
                  <div class="av-row-main">
                    <strong>{o.name} <small>{fmt(o.points)}</small></strong>
                    <span class="av-faces small">{o.team.map((m) => <span class="av-face"><img src={heroImage(m.defId)} alt="" /></span>)}</span>
                  </div>
                  <div class="av-row-side">
                    <span class={`av-power ${mine >= p ? 'ok' : 'low'}`}><Icon name="power" size={16} /><b>{fmt(p)}</b></span>
                    <Btn kind="green" small disabled={left <= 0} onClick={() => prepare(arenaPlan(o.id))}>{t('fight')}</Btn>
                  </div>
                </div>
              );
            })}
          </>
        ) : (
          <ModeShop kind="arena" items={ARENA_SHOP} league={league.id} />
        )}
      </section>
    </>
  );
}
