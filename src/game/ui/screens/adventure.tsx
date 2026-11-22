// Aventure : les modes du quotidien (tour, missions, donjons, boss du jour, arène, défense).
import { sceneBg, sceneVar, useTerrainImage } from '../terrain-image';
import { useEffect, useState } from 'preact/hooks';
import { stagePower } from '../../../core/data/campaign';
import {
  ARENA_FREE_TICKETS, ARENA_LEAGUES, ARENA_SHOP, DAILY_BOSS_ATTEMPTS, DAILY_BOSS_TIERS,
  DUNGEON_ATTEMPTS_PER_DAY, TOWER_STAGE_PER_FLOOR, UNLOCKS, type DungeonKind,
} from '../../../core/data/modes';
import { ITEM_COLORS, heroImage, monsterImage } from '../../art';
import { fmt, t } from '../../i18n';
import {
  arenaPlan, buyExchange, claimMission, dailyBossId, dailyBossPlan, dungeonAttemptsLeft, markSeen, missionEnd,
  missionTemplate, opponentPower, refreshOpponents, towerPlan,
} from '../../state/actions';
import { isUnlocked, teamPower } from '../../state/selectors';
import { now, useGame } from '../../state/store';
import { ADVENTURE_ORDER, dots, isNew } from '../dots';
import { TeamStrip } from './heroes';
import { TileScene } from '../tile-scene';
import { ModeIcon } from '../mode-icons';
import { TitleBanner } from '../title-banner';
import { Art, Bar, Btn, Cur, Icon, Locked, duration } from '../kit';
import { open, openSub, prepare, toast, type Sub } from '../nav';

export function AdventureScreen({ sub }: { sub: Sub }) {
  const s = useGame();
  if (sub) {
    return (
      <div class="screen">
        <button class="back" onClick={() => openSub(null)}>‹ {t('back')}</button>
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
    <div class="screen adventure">
      <div class="adv-banner"><h1 class="sr-only">{t('nav.adventure')}</h1><TitleBanner title={t('nav.adventure')}><Icon name="adventure" size={27} /></TitleBanner></div>
      <div class="tiles">
        {ADVENTURE_ORDER.map((f) => {
          const unlocked = isUnlocked(s, f);
          return (
            <button
              class={`tile tile-${f}${unlocked ? '' : ' tile-locked'}`}
              onClick={() => {
                if (!unlocked) return toast(t('locked', { n: UNLOCKS[f] }));
                markSeen(f);
                openSub(f);
              }}
            >
              <TileScene kind={f} />
              <ModeIcon kind={f} />
              <span class="tile-name">
                {t(`adv.${f}`)}
                {/* l'information de la tuile est accrochée au bandeau du nom : elle ne recouvre jamais le picto */}
                {!unlocked && <Locked stage={UNLOCKS[f]} />}
                {unlocked && isNew(s, f) && <span class="tile-new">{t('new')}</span>}
              </span>
              {unlocked && !isNew(s, f) && dots[f](s) && <span class="dot" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/** Le Colisée (il remplace le Siège) : deux équipes de 3, un duel à la fois. Les règles restent à construire. */
function Colisee() {
  const s = useGame();
  const mine = s.formation.slice(0, 3).map(([uid]) => s.heroes.find((h) => h.uid === uid)).filter(Boolean);
  return (
    <section class="card center">
      <h1>{t('adv.defense')}</h1>
      <div class="boss-scene colisee-scene" style={sceneBg(useTerrainImage('arena'))}><ModeIcon kind="defense" size={132} class="colisee-art" /></div>
      <div class="colisee-duel">
        <div class="team-faces">{mine.map((h) => <span class="team-face"><img src={heroImage(h!.defId)} alt="" /></span>)}</div>
        <span class="vs">VS</span>
        <div class="team-faces">{[0, 1, 2].map(() => <span class="team-face unknown">?</span>)}</div>
      </div>
      <Btn kind="gold" wide disabled>{t('soon')}</Btn>
    </section>
  );
}

function PowerLine({ need }: { need: number }) {
  const s = useGame();
  const mine = teamPower(s);
  return (
    <div class={`power-line ${mine >= need ? 'ok' : 'low'}`}>
      <Icon name="power" size={20} /> <strong>{fmt(mine)}</strong> <span class="muted">/ {fmt(need)}</span>
    </div>
  );
}

function Tower() {
  const s = useGame();
  const floor = s.tower.floor + 1;
  return (
    <section class="card center">
      <h1>{t('adv.tower')}</h1>
      <div class="tower-art" style={sceneBg(useTerrainImage('tower'))}>
        {[2, 1, 0].map((k) => <div class={`tower-floor${k === 0 ? ' current' : ''}`}>{t('tower.floor', { n: floor + k })}</div>)}
        {s.tower.floor > 0 && <div class="tower-floor done">{t('tower.floor', { n: s.tower.floor })}</div>}
      </div>
      <div class="row gap center">
        <Cur k="essence" n={40 * floor} />
        {floor % 5 === 0 && <Cur k="scrolls" n={1} />}
        {floor % 10 === 0 && <Cur k="gems" n={100} />}
      </div>
      <PowerLine need={stagePower(floor * TOWER_STAGE_PER_FLOOR)} />
      <Btn kind="green" wide onClick={() => prepare(towerPlan())}>{t('tower.challenge')}</Btn>
    </section>
  );
}

function Missions() {
  const s = useGame();
  const [, tick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => tick((x) => x + 1), 1000);
    return () => clearInterval(id);
  }, []);
  return (
    <section class="list">
      <h1>{t('adv.missions')}</h1>
      {s.daily.missions.filter((m) => !m.claimed).map((m) => {
        const tpl = missionTemplate(m);
        const end = missionEnd(m);
        const ready = !!m.startedAt && now() >= end;
        return (
          <div class="card mission">
            <Icon name={`mission-${tpl.id}`} size={52} />
            <div class="grow">
              <strong>{t(`mission.${tpl.id}`)}</strong>
              <div class="muted small"><Icon name="clock" size={14} /> {tpl.hours} h · {t('mission.need', { n: tpl.heroes, s: tpl.minStars })}</div>
              <div class="row gap-s">
                {tpl.reward.amount ? <Cur k={tpl.reward.kind} n={tpl.reward.amount} /> : <span class="cur"><Icon name={tpl.reward.kind} size={18} /> {tpl.reward.hours} h</span>}
              </div>
              {m.startedAt && !ready && <Bar value={now() - m.startedAt} max={end - m.startedAt} color="#4fd1ff" label={duration(end - now())} />}
              {m.startedAt && (
                <div class="mini-team">{m.heroUids.map((u) => {
                  const h = s.heroes.find((x) => x.uid === u);
                  return h ? <img src={heroImage(h.defId)} alt="" /> : null;
                })}</div>
              )}
            </div>
            {!m.startedAt && <Btn kind="blue" small onClick={() => open({ type: 'mission', id: m.id })}>{t('send')}</Btn>}
            {ready && <Btn kind="gold" small dot onClick={() => {
              const gain = claimMission(m.id);
              if (gain) open({ type: 'gain', title: t(`mission.${tpl.id}`), gain });
            }}>{t('claim')}</Btn>}
          </div>
        );
      })}
    </section>
  );
}

const DUNGEON_KINDS: DungeonKind[] = ['gold', 'essence', 'gear'];
export const DUNGEON_ICON: Record<DungeonKind, string> = { gold: 'gold', essence: 'essence', gear: 'weapon' };

function Dungeons() {
  const s = useGame();
  const imgs = { gold: useTerrainImage('mine'), essence: useTerrainImage('spring'), gear: useTerrainImage('armory') };
  return (
    <section class="list">
      <h1>{t('adv.dungeons')}</h1>
      {DUNGEON_KINDS.map((k) => {
        const left = dungeonAttemptsLeft(s, k);
        return (
          <button class={`card dungeon dungeon-${k}`} style={sceneVar(imgs[k])} onClick={() => open({ type: 'dungeon', kind: k })}>
            <span class="dungeon-icon"><Icon name={DUNGEON_ICON[k]} size={34} /></span>
            <span class="grow">
              <strong>{t(`dungeon.${k}`)}</strong>
              <span class="muted small">{t('dungeon.level', { n: s.dungeons[k] })}</span>
            </span>
            <span class={`dungeon-tries${left ? '' : ' none'}`}>{left} / {DUNGEON_ATTEMPTS_PER_DAY}</span>
            {left > 0 && <span class="dot" />}
          </button>
        );
      })}
    </section>
  );
}

function DailyBoss() {
  const s = useGame();
  const boss = dailyBossId();
  const left = DAILY_BOSS_ATTEMPTS - s.daily.bossAttempts;
  const total = dailyBossPlan().waves[0]!.reduce((a, u) => a + u.maxHp, 0);
  const best = Math.min(1, s.daily.bossBest / total);
  return (
    <section class="card center">
      <h1>{t('adv.dailyBoss')} · {t(`monster.${boss}`)}</h1>
      <div class="boss-scene" style={sceneBg(useTerrainImage('lair'))}><img class="boss-img" src={monsterImage(boss, 'fire')} alt="" /></div>
      {/* Les récompenses sont des paliers sur la barre des dégâts : on voit d'un coup d'œil où on en est. */}
      <div class="boss-track">
        {DAILY_BOSS_TIERS.map((tier) => (
          <span class={`boss-mark${best >= tier.share ? ' on' : ''}`} style={{ left: `${tier.share * 100}%` }}>
            <Icon name="gems" size={16} />
            <small>{tier.gems}</small>
          </span>
        ))}
        <div class="boss-bar"><span style={{ width: `${best * 100}%` }} /></div>
      </div>
      <p class="muted small">{t('boss.best')} <b>{fmt(s.daily.bossBest)}</b></p>
      <Btn kind="red" wide disabled={left <= 0} onClick={() => prepare(dailyBossPlan())}>{t('boss.attack')} · {left} / {DAILY_BOSS_ATTEMPTS}</Btn>
    </section>
  );
}

function leagueOf(points: number): string {
  return [...ARENA_LEAGUES].reverse().find((l) => points >= l.from)!.id;
}

function Arena() {
  const s = useGame();
  const [tab, setTab] = useState<'fight' | 'shop'>('fight');
  const left = ARENA_FREE_TICKETS - s.daily.arenaFights;
  return (
    <section class="list">
      <div class="card arena-head">
        <h1>{t('adv.arena')}</h1>
        <div class="row between">
          <span class={`league league-${leagueOf(s.arena.points)}`}><Icon name={`league-${leagueOf(s.arena.points)}`} size={34} />{t(`league.${leagueOf(s.arena.points)}`)}</span>
          <span><b>{s.arena.points}</b> {t('arena.points')}</span>
          <Cur k="arenaTokens" n={s.wallet.arenaTokens} />
        </div>
        <div class="row gap">
          <Btn kind={tab === 'fight' ? 'blue' : 'ghost'} small wide onClick={() => setTab('fight')}>{t('adv.arena')}</Btn>
          <Btn kind={tab === 'shop' ? 'blue' : 'ghost'} small wide onClick={() => setTab('shop')}>{t('arena.shop')}</Btn>
        </div>
      </div>
      {tab === 'fight' ? (
        <>
          <TeamStrip />
          <div class="row between"><span class="muted">{t('arena.tickets', { n: left, m: ARENA_FREE_TICKETS })}</span>
            <Btn kind="ghost" small onClick={refreshOpponents}>{t('arena.refresh')}</Btn></div>
          {s.arena.opponents.map((o) => (
            <div class="card opponent">
              <div class="grow">
                <strong>{o.name}</strong> <span class="muted small">{o.points} pts</span>
                <div class="mini-team">{o.team.map((m) => <img src={heroImage(m.defId)} alt="" />)}</div>
              </div>
              <div class="col-end">
                <span class={`power-chip ${teamPower(s) >= opponentPower(o) ? 'ok' : 'low'}`}><Icon name="power" size={16} />{fmt(opponentPower(o))}</span>
                <Btn kind="red" small disabled={left <= 0} onClick={() => prepare(arenaPlan(o.id))}>{t('fight')}</Btn>
              </div>
            </div>
          ))}
        </>
      ) : (
        <div class="shop-grid">
          {ARENA_SHOP.map((x) => (
            <ShopTile cost={<Cur k="arenaTokens" n={x.cost} />} reward={x.reward} disabled={s.wallet.arenaTokens < x.cost}
              onBuy={() => {
                const gain = buyExchange('arena', x.id);
                if (gain) open({ type: 'gain', title: t('arena.shop'), gain });
              }} />
          ))}
        </div>
      )}
    </section>
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

