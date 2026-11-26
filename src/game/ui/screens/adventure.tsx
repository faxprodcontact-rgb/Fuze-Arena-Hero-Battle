// Aventure : les modes du quotidien (tour, missions, donjons, boss du jour, arène, Colisée).
// Style moderne (26/11/2026), onglet refait le 27/11 : six tuiles qui prennent tout l'écran (un petit paysage du mode dessiné
// par le code, TileScene de backdrop-adventure.tsx, son picto posé sur le sol, son nom, UNE information utile), sur un fond
// épuré. Chaque mode : une tête, son décor, une seule action. Mise en page dans sections/aventure.css (classes « av- »).
import '../sections/aventure.css';
import { sceneVar } from '../fond-image';
import { useEffect, useState } from 'preact/hooks';
import type { ComponentChildren } from 'preact';
import { stagePower } from '../../../core/data/campaign';
import {
  ARENA_FREE_TICKETS, ARENA_LEAGUES, ARENA_SHOP, DAILY_BOSS_ATTEMPTS, DAILY_BOSS_TIERS,
  DUNGEON_ATTEMPTS_PER_DAY, TOWER_STAGE_PER_FLOOR, UNLOCKS, type DungeonKind,
} from '../../../core/data/modes';
import { ITEM_COLORS, heroImage } from '../../art';
import { DUNGEON_CLAN, battleLook, bossArt, bossClan } from '../../look';
import { Figure } from '../hero-figure';
import { fmt, t } from '../../i18n';
import {
  arenaPlan, claimMission, dailyBossId, dailyBossPlan, dungeonAttemptsLeft, markSeen, missionEnd,
  missionTemplate, opponentPower, refreshOpponents, towerPlan,
} from '../../state/actions';
import { isUnlocked, teamPower } from '../../state/selectors';
import { now, useGame } from '../../state/store';
import { ADVENTURE_ORDER, dots, isNew } from '../dots';
import { TeamStrip } from './heroes';
import { TileScene } from '../backdrop-adventure';
import { Art, Btn, Cur, Icon, Locked, duration, starText } from '../kit';
import { btClass } from '../buttons';
import { ModeShop } from '../sections/boutiques-modes';
import { open, openSub, prepare, toast, type Sub } from '../nav';

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
    case 'dailyBoss':
      return <span class="av-chip">{t(`monster.${dailyBossId()}`)} · {DAILY_BOSS_ATTEMPTS - s.daily.bossAttempts} / {DAILY_BOSS_ATTEMPTS}</span>;
    case 'arena': {
      const l = leagueOf(s.arena.points).id;
      return <span class={`av-chip league-${l}`}><Icon name={`league-${l}`} size={16} />{t(`league.${l}`)}</span>;
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
        {sub === 'dailyBoss' && <DailyBoss />}
        {sub === 'arena' && <Arena />}
        {sub === 'defense' && <Colisee />}
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
                <Art name={f} class="av-tile-art" />
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

/** Le Colisée (il remplace le Siège) : deux équipes de 3, un duel à la fois. Les règles restent à construire. */
function Colisee() {
  const s = useGame();
  const mine = s.formation.slice(0, 3).map(([uid]) => s.heroes.find((h) => h.uid === uid)).filter(Boolean);
  return (
    <>
      <SubHead title={t('adv.defense')} />
      <section class="av-panel av-colisee">
        <div class="av-scene av-grow" style={sceneVar('lenore')}>
          <Art name="defense" class="av-scene-art" />
        </div>
        <div class="av-duel">
          <div class="av-faces">{mine.map((h) => <span class="av-face"><img src={heroImage(h!.defId)} alt="" /></span>)}</div>
          <span class="av-vs">VS</span>
          <div class="av-faces">{[0, 1, 2].map(() => <span class="av-face unknown"><Icon name="unknownHero" size={34} /></span>)}</div>
        </div>
        <Btn kind="gold" wide disabled>{t('soon')}</Btn>
      </section>
    </>
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

function DailyBoss() {
  const s = useGame();
  const boss = dailyBossId();
  const left = DAILY_BOSS_ATTEMPTS - s.daily.bossAttempts;
  const total = dailyBossPlan().waves[0]!.reduce((a, u) => a + u.maxHp, 0);
  const best = Math.min(1, s.daily.bossBest / total);
  return (
    <>
      <SubHead title={t('adv.dailyBoss')}>
        <Tries left={left} max={DAILY_BOSS_ATTEMPTS} />
      </SubHead>
      <section class="av-panel av-boss">
        <div class="av-scene av-grow" style={sceneVar(bossClan(boss))}>
          <Figure id={bossArt(boss)} class="av-boss-img" />
          <span class="av-scene-name">{t(`monster.${boss}`)}</span>
        </div>
        {/* Les récompenses sont des paliers sur la barre des dégâts : on voit d'un coup d'œil où on en est. */}
        <div class="av-track">
          <div class="av-track-bar"><span style={{ width: `${best * 100}%` }} /></div>
          {DAILY_BOSS_TIERS.map((tier) => (
            <span class={`av-tier${best >= tier.share ? ' on' : ''}`} style={{ left: `${tier.share * 100}%` }}>
              <i />
              <Icon name="gems" size={18} />
              <small>{tier.gems}</small>
            </span>
          ))}
        </div>
        <div class="av-action">
          <span class="av-record"><Icon name="trophy" size={18} />{t('boss.best')} <b>{fmt(s.daily.bossBest)}</b></span>
          <Btn kind="green" wide disabled={left <= 0} onClick={() => prepare(dailyBossPlan())}>{t('boss.attack')}</Btn>
        </div>
      </section>
    </>
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

export function ShopTile(p: { cost: preact.ComponentChildren; reward: Record<string, number | undefined>; disabled?: boolean; onBuy: () => void; art?: string }) {
  return (
    <div class="card shop-tile">
      {p.art && <Art class="shop-art" name={p.art} />}
      <div class="shop-reward">
        {Object.entries(p.reward).map(([k, v]) =>
          k === 'item' ? <span class="item" style={{ '--rar': ITEM_COLORS[v ?? 0] } as never}><Icon name={`weapon-${v}`} size={38} /></span> : <Cur k={k} n={v ?? 0} big />,
        )}
      </div>
      <Btn kind="gold" small wide disabled={p.disabled} onClick={p.onBuy}>{p.cost}</Btn>
    </div>
  );
}
