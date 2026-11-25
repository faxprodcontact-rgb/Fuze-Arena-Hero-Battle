// Social : guilde (boss commun, membres, tchat, boutique), tchat général, classements.
// Dans le prototype, les autres joueurs sont des joueurs fictifs : le vrai social arrivera avec le serveur.
import { sceneBg } from '../fond-image';
import { bossArt, bossClan } from '../../look';
import { Figure } from '../hero-figure';
import { useEffect, useRef, useState } from 'preact/hooks';
import { GUILD_BOSS_ATTEMPTS, GUILD_SHOP, GUILD_WAR, UNLOCKS } from '../../../core/data/modes';
import { createRng } from '../../../core/rng';
import { heroImage } from '../../art';
import { CHAT_LINES, fmt, t } from '../../i18n';
import {
  BOT_GUILDS, botChatter, buyExchange, claimWar, ensureWar, guildBossPlan, joinGuild, leaveGuild, markSeen, sendChat,
  warAttacksLeft, warDefenses, warPhase, warPlan, warScores,
} from '../../state/actions';
import { isUnlocked, teamPower } from '../../state/selectors';
import { getState, now, useGame } from '../../state/store';
import type { ChatMessage } from '../../state/types';
import { Bar, Btn, Cur, Icon, Locked, Modal, Tabs } from '../kit';
import { open, prepare } from '../nav';
import { ShopTile } from './adventure';
import { TitleBanner } from '../title-banner';
import { TeamStrip } from './heroes';

const MEMBER_NAMES = ['Kaïro', 'Lunaria', 'Vaelis', 'Tormund', 'Ishara', 'Mikaze', 'Orsolya', 'Bastien', 'Yuna', 'Ragnis', 'Selka', 'Noctis'];
const GUILD_BOSS_HP = 50_000_000;

/** Membres fictifs de la guilde : leur force suit celle du joueur, leurs dégâts montent avec le temps. */
/** Emblème d'une guilde (12 dessins) : choisi d'après son nom, toujours le même pour une guilde. */
function emblem(guild: string): string {
  let h = 0;
  for (const c of guild) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return `emblem-${h % 12}`;
}

function members(guild: string) {
  const rng = createRng(guild.length * 977);
  const mine = Math.max(1000, teamPower(getState()));
  return MEMBER_NAMES.slice(0, 9).map((name, i) => ({
    name,
    power: Math.round(mine * (0.6 + rng() * 0.9)),
    role: i === 0 ? 'crown' : i < 3 ? 'star' : '',
    defId: ['knights-9', 'mages-11', 'angels-6', 'demons-9', 'myths-10', 'assassins-11', 'knights-7', 'mages-7', 'angels-10'][i]!,
  }));
}

function botDamage(): number {
  const s = getState();
  const hours = (now() - (s.createdAt ?? now())) / 3.6e6;
  return Math.min(GUILD_BOSS_HP * 0.9, Math.round(hours * 180_000));
}

export function GuildScreen() {
  const s = useGame();
  const [tab, setTab] = useState<'boss' | 'war' | 'members' | 'chat' | 'shop'>('boss');
  useEffect(() => markSeen('guild'), []);
  // le bandeau de titre sur le panorama de la forteresse (comme les autres parties)
  const banner = (title: string, icon: string) => (
    <div class="adv-banner"><h1 class="sr-only">{title}</h1><TitleBanner title={title} ribbon={['#4f7ae0', '#2a4aa8', '#16285e']}><Icon name={icon} size={30} /></TitleBanner></div>
  );
  if (!isUnlocked(s, 'guild')) {
    return <div class="screen guild">{banner(t('nav.guild'), 'guild')}<section class="card center"><Locked stage={UNLOCKS.guild} /></section></div>;
  }
  if (!s.guild.joined) {
    return (
      <div class="screen guild list">
        {banner(t('nav.guild'), 'guild')}
        {BOT_GUILDS.map((g, i) => (
          <div class="card guild-row row between center-y">
            <Icon name={emblem(g)} size={52} />
            <div class="grow">
              <strong>{g}</strong>
              <div class="muted small">{t('guild.level', { n: 5 + i * 3 })} · {18 + i * 4} / 30</div>
            </div>
            <Btn kind="green" small onClick={() => joinGuild(g)}>{t('guild.join')}</Btn>
          </div>
        ))}
      </div>
    );
  }
  const total = Math.min(GUILD_BOSS_HP, botDamage() + s.guild.bossDamage);
  const left = GUILD_BOSS_ATTEMPTS - s.daily.guildAttempts;
  return (
    <div class="screen guild">
      {banner(s.guild.joined, emblem(s.guild.joined))}
      <div class="guild-info">
        <span>{t('guild.level', { n: 7 })} · <Icon name="friends" size={18} /> 22 / 30</span>
        <Cur k="guildCoins" n={s.wallet.guildCoins} />
      </div>
      <Tabs value={tab} onChange={setTab} options={[
        ['boss', t('guild.boss'), left > 0], ['war', t('guild.war'), !!s.guildWar && (warAttacksLeft(s.guildWar) > 0 || !!s.guildWar.pending || (warPhase() === 'results' && !s.guildWar.claimed))], ['members', t('guild.members')], ['chat', t('guild.chat')], ['shop', t('guild.shop')],
      ]} />
      {tab === 'boss' && (
        <section class="card center">
          <div class="boss-scene" style={sceneBg(bossClan('dragon'))}><Figure id={bossArt('dragon')} class="boss-img" /></div>
          <h2>{t('monster.dragon')}</h2>
          <Bar value={GUILD_BOSS_HP - total} max={GUILD_BOSS_HP} color="#e5484d" label={`${fmt(GUILD_BOSS_HP - total)} / ${fmt(GUILD_BOSS_HP)}`} />
          <p class="muted">{t('guild.total')} : <b>{fmt(total)}</b></p>
          <p class="muted">{t('boss.attempts', { n: left, m: GUILD_BOSS_ATTEMPTS })}</p>
          <Btn kind="red" wide disabled={left <= 0} onClick={() => prepare(guildBossPlan())}>{t('boss.attack')}</Btn>
        </section>
      )}
      {tab === 'members' && (
        <section class="list">
          <div class="card member me"><img src={heroImage(s.heroes[0]!.defId)} alt="" /><strong class="grow">{s.name}</strong><span class="power-chip"><Icon name="power" size={16} />{fmt(teamPower(s))}</span></div>
          {members(s.guild.joined).map((m) => (
            <div class="card member"><img src={heroImage(m.defId)} alt="" /><strong class="grow">{m.role && <Icon name={m.role} size={18} />} {m.name}</strong><span class="power-chip"><Icon name="power" size={16} />{fmt(m.power)}</span></div>
          ))}
          <Btn kind="ghost" small onClick={() => open({ type: 'confirm', text: `${t('guild.leave')} ?`, onYes: leaveGuild })}>{t('guild.leave')}</Btn>
        </section>
      )}
      {tab === 'war' && <GuildWar guild={s.guild.joined} />}
      {tab === 'chat' && <Chat target="guild" />}
      {tab === 'shop' && (
        <div class="shop-grid">
          {GUILD_SHOP.map((x) => (
            <ShopTile cost={<Cur k="guildCoins" n={x.cost} />} reward={x.reward} disabled={s.wallet.guildCoins < x.cost}
              onBuy={() => {
                const gain = buyExchange('guild', x.id);
                if (gain) open({ type: 'gain', title: t('guild.shop'), gain });
              }} />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Guerre de guildes, une par semaine : lundi préparation, mardi → samedi 2 attaques par jour
 * (un héros n'attaque qu'une fois par jour), dimanche résultats et récompenses.
 */
function GuildWar({ guild }: { guild: string }) {
  const s = useGame();
  useEffect(() => void ensureWar(), []);
  const w = s.guildWar;
  if (!w) return null;
  const phase = warPhase();
  const sc = warScores(s, w);
  const defenses = warDefenses(s, w);
  const left = warAttacksLeft(w);
  const mine = teamPower(s);
  const showResult = phase === 'results' && !w.claimed;
  const pending = w.pending;
  const result = showResult ? (sc.mine > sc.foe ? 'win' : sc.mine === sc.foe ? 'draw' : 'loss') : pending?.result;

  return (
    <section class="list war">
      <div class="card war-head">
        <div class="war-side"><Icon name={emblem(guild)} size={44} /><strong>{guild}</strong><span class="war-score"><Icon name="star" size={18} /> {sc.mine}</span></div>
        <span class="war-vs">VS</span>
        <div class="war-side foe"><Icon name={emblem(w.foe)} size={44} /><strong>{w.foe}</strong><span class="war-score"><Icon name="star" size={18} /> {sc.foe}</span></div>
      </div>

      {(showResult || pending) && (
        <div class={`card center war-result ${result}`}>
          <h2>{t(`war.${result}`)}</h2>
          <Btn kind="gold" wide onClick={() => {
            const gain = claimWar();
            if (gain) open({ type: 'gain', title: t('guild.war'), gain });
          }}>{t('claim')}</Btn>
        </div>
      )}

      <div class="row between center-y">
        <span class="tag">{t(`war.${phase}`)}{phase === 'battle' && ` · ${t('war.day', { n: Math.min(5, Math.floor((new Date(now()).getDay() + 6) % 7)) })}`}</span>
        {phase === 'battle' && <span class={left ? 'gold-text' : 'muted'}>{t('war.attacks', { n: left, m: GUILD_WAR.attacksPerDay })}</span>}
      </div>

      <TeamStrip />
      <TeamStrip team="defense" />

      <div class="war-grid">
        {defenses.map((d, i) => {
          const leader = d.team.find((m) => m.slot === 2) ?? d.team[0]!;
          return (
            <button class="card war-fort" disabled={!left} onClick={() => { const p = warPlan(i); if (p) prepare(p); }}>
              <img src={heroImage(leader.defId)} alt="" />
              <strong>{d.name}</strong>
              <span class={`power-chip ${mine >= d.power ? 'ok' : 'low'}`}><Icon name="power" size={14} />{fmt(d.power)}</span>
            </button>
          );
        })}
      </div>

      <h3>{t('war.ranking')}</h3>
      <div class="card war-ranking">
        {sc.members.map((m, i) => (
          <div class={`row between${m.me ? ' me' : ''}`}><span>{i + 1}. {m.name}</span><span class="gold-text"><Icon name="star" size={16} /> {m.stars}</span></div>
        ))}
      </div>
    </section>
  );
}

export function Chat({ target }: { target: 'guild' | 'world' }) {
  const s = useGame();
  const [text, setText] = useState('');
  const list = useRef<HTMLDivElement>(null);
  const messages: ChatMessage[] = target === 'guild' ? s.guild.chat : s.worldChat;
  useEffect(() => botChatter(CHAT_LINES[s.lang], target), []);
  useEffect(() => {
    list.current?.scrollTo({ top: list.current.scrollHeight });
  }, [messages.length]);
  const send = () => {
    sendChat(text, target);
    setText('');
  };
  return (
    <section class="chat">
      <div class="chat-list" ref={list}>
        {messages.map((m) => (
          <div class={`msg${m.me ? ' msg-me' : ''}`}>
            {!m.me && <b>{m.from}</b>}
            <span>{m.text}</span>
          </div>
        ))}
      </div>
      <form class="chat-input" onSubmit={(e) => { e.preventDefault(); send(); }}>
        <input id={`chat-${target}`} value={text} maxLength={200} onInput={(e) => setText((e.target as HTMLInputElement).value)} />
        <Btn kind="blue" small onClick={send}>{t('send')}</Btn>
      </form>
    </section>
  );
}

export function ChatModal() {
  return <Modal title={t('side.chat')} wide><Chat target="world" /></Modal>;
}

export function RankingModal() {
  const s = useGame();
  const [tab, setTab] = useState<'campaign' | 'power' | 'arena'>('campaign');
  const mine = { campaign: s.campaign.cleared, power: Math.round(teamPower(s)), arena: s.arena.points }[tab];
  const rng = createRng({ campaign: 1, power: 2, arena: 3 }[tab] * 31);
  const bots = MEMBER_NAMES.concat(['Aïko', 'Feyd', 'Mirelle', 'Draven7']).map((name) => ({
    name,
    value: Math.round(Math.max(10, mine) * (0.5 + rng() * 1.2)),
  }));
  const rows = [...bots, { name: s.name, value: mine, me: true }].sort((a, b) => b.value - a.value);
  return (
    <Modal title={t('side.ranking')} wide>
      <Tabs value={tab} onChange={setTab} options={[['campaign', t('rank.campaign')], ['power', t('rank.power')], ['arena', t('rank.arena')]]} />
      <ol class="ranking">
        {rows.map((r, i) => (
          <li class={'me' in r ? 'me' : ''}>
            <span class={`rank rank-${i + 1}`}>{i + 1}</span>
            <span class="grow">{'me' in r ? `${r.name} (${t('rank.you')})` : r.name}</span>
            <b>{fmt(r.value)}</b>
          </li>
        ))}
      </ol>
    </Modal>
  );
}
