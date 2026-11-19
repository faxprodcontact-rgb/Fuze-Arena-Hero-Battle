// Aventure : les modes du quotidien (tour, missions, donjons, boss du jour, arène, défense).
import { useEffect, useState } from 'preact/hooks';
import { stagePower } from '../../../core/data/campaign';
import {
  ARENA_FREE_TICKETS, ARENA_LEAGUES, ARENA_SHOP, DAILY_BOSS_ATTEMPTS, DAILY_BOSS_TIERS, DUNGEON_BY_WEEKDAY,
  DUNGEON_ENTRIES_PER_DAY, DUNGEON_TIERS, TOWER_STAGE_PER_FLOOR, UNLOCKS, type DungeonKind,
} from '../../../core/data/modes';
import { heroImage, monsterImage } from '../../art';
import { fmt, t } from '../../i18n';
import {
  arenaBattle, buyExchange, claimMission, dailyBossBattle, dailyBossId, dungeonBattle, markSeen, missionEnd,
  missionTemplate, opponentPower, refreshOpponents, sendMission, towerBattle,
} from '../../state/actions';
import { isUnlocked, teamPower } from '../../state/selectors';
import { now, useGame } from '../../state/store';
import { ADVENTURE_ORDER, dots, isNew } from '../dots';
import { Bar, Btn, Cur, Icon, Locked, duration } from '../kit';
import { open, openSub, startBattle, toast, type Sub } from '../nav';

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
        {sub === 'defense' && <Defense />}
      </div>
    );
  }
  return (
    <div class="screen">
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
              <Icon name={f} size={44} />
              <span class="tile-name">{t(`adv.${f}`)}</span>
              {!unlocked && <Locked stage={UNLOCKS[f]} />}
              {unlocked && isNew(s, f) && <span class="tile-new">{t('new')}</span>}
              {unlocked && !isNew(s, f) && dots[f](s) && <span class="dot" />}
            </button>
          );
        })}
      </div>
    </div>
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
      <div class="tower-art">
        {[2, 1, 0].map((k) => <div class={`tower-floor${k === 0 ? ' current' : ''}`}>{t('tower.floor', { n: floor + k })}</div>)}
        {s.tower.floor > 0 && <div class="tower-floor done">{t('tower.floor', { n: s.tower.floor })}</div>}
      </div>
      <div class="row gap center">
        <Cur k="essence" n={40 * floor} />
        {floor % 5 === 0 && <Cur k="scrolls" n={1} />}
        {floor % 10 === 0 && <Cur k="gems" n={100} />}
      </div>
      <PowerLine need={stagePower(floor * TOWER_STAGE_PER_FLOOR)} />
      <Btn kind="green" wide onClick={() => startBattle(towerBattle())}>{t('tower.challenge')}</Btn>
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
            {!m.startedAt && <Btn kind="blue" small onClick={() => !sendMission(m.id) && toast(t('mission.missing'))}>{t('send')}</Btn>}
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

function Dungeons() {
  const s = useGame();
  const open_ = DUNGEON_BY_WEEKDAY[new Date(now()).getDay()] ?? [];
  const kinds: DungeonKind[] = ['gold', 'essence', 'gear'];
  const ref = stagePower(Math.max(1, s.campaign.cleared));
  return (
    <section class="list">
      <h1>{t('adv.dungeons')}</h1>
      {kinds.map((k) => {
        const isOpen = open_.includes(k);
        const used = s.daily.entries[k];
        return (
          <div class={`card dungeon dungeon-${k}${isOpen ? '' : ' closed'}`}>
            <div class="row between">
              <h2><Icon name={k === 'gear' ? 'arena' : k} size={24} /> {t(`dungeon.${k}`)}</h2>
              <span class="muted small">{isOpen ? t('dungeon.entries', { n: DUNGEON_ENTRIES_PER_DAY - used, m: DUNGEON_ENTRIES_PER_DAY }) : t('dungeon.closed')}</span>
            </div>
            {isOpen && (
              <div class="tiers">
                {DUNGEON_TIERS.map((f, tier) => (
                  <Btn kind={teamPower(s) >= ref * f ? 'green' : 'ghost'} small disabled={used >= DUNGEON_ENTRIES_PER_DAY}
                    onClick={() => startBattle(dungeonBattle(k, tier))}>
                    {t('dungeon.tier', { n: tier + 1 })} · {fmt(ref * f)}
                  </Btn>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}

function DailyBoss() {
  const s = useGame();
  const boss = dailyBossId();
  const left = DAILY_BOSS_ATTEMPTS - s.daily.bossAttempts;
  return (
    <section class="card center">
      <h1>{t('adv.dailyBoss')} · {t(`monster.${boss}`)}</h1>
      <img class="boss-img" src={monsterImage(boss, 'fire')} alt="" />
      <p>{t('boss.best')} : <b>{fmt(s.daily.bossBest)}</b></p>
      <div class="boss-tiers">{DAILY_BOSS_TIERS.map((tier) => <span><Cur k="gems" n={tier.gems} /><small>{Math.round(tier.share * 100)} %</small></span>)}</div>
      <p class="muted">{t('boss.attempts', { n: left, m: DAILY_BOSS_ATTEMPTS })}</p>
      <Btn kind="red" wide disabled={left <= 0} onClick={() => startBattle(dailyBossBattle())}>{t('boss.attack')}</Btn>
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
          <span class={`league league-${leagueOf(s.arena.points)}`}>{t(`league.${leagueOf(s.arena.points)}`)}</span>
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
          <div class="row between"><span class="muted">{t('arena.tickets', { n: left, m: ARENA_FREE_TICKETS })}</span>
            <Btn kind="ghost" small onClick={refreshOpponents}>{t('arena.refresh')}</Btn></div>
          {s.arena.opponents.map((o) => (
            <div class="card opponent">
              <div class="grow">
                <strong>{o.name}</strong> <span class="muted small">{o.points} pts</span>
                <div class="mini-team">{o.team.map((m) => <img src={heroImage(m.defId)} alt="" />)}</div>
              </div>
              <div class="col-end">
                <span class="power-chip"><Icon name="power" size={16} />{fmt(opponentPower(o))}</span>
                <Btn kind="red" small disabled={left <= 0} onClick={() => {
                  const req = arenaBattle(o.id);
                  if (req) startBattle(req);
                }}>{t('fight')}</Btn>
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

export function ShopTile(p: { cost: preact.ComponentChildren; reward: Record<string, number | undefined>; disabled?: boolean; onBuy: () => void }) {
  return (
    <div class="card shop-tile">
      <div class="shop-reward">
        {Object.entries(p.reward).map(([k, v]) =>
          k === 'item' ? <span class="cur">⚔ {t(`item.${v}`)}</span> : <Cur k={k} n={v ?? 0} big />,
        )}
      </div>
      <Btn kind="gold" small wide disabled={p.disabled} onClick={p.onBuy}>{p.cost}</Btn>
    </div>
  );
}

function Defense() {
  return (
    <section class="card center defense">
      <h1>{t('adv.defense')}</h1>
      <svg viewBox="0 0 300 200" class="defense-map" aria-hidden="true">
        <path d="M0 160 C 80 160, 80 40, 150 40 S 220 160, 300 120" stroke="#c08a4a" stroke-width="26" fill="none" stroke-linecap="round" />
        <circle cx="70" cy="80" r="16" fill="#4c8dff" />
        <circle cx="150" cy="100" r="16" fill="#3ccf7a" />
        <circle cx="230" cy="70" r="16" fill="#ffc94a" />
        <circle cx="280" cy="125" r="10" fill="#e5484d" />
      </svg>
      <p class="muted">{t('defense.text')}</p>
      <span class="tag">{t('soon')}</span>
    </section>
  );
}
