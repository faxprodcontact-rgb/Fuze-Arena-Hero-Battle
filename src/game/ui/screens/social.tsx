// Social : guilde (boss commun, membres, tchat, boutique), tchat général, classements.
// Dans le prototype, les autres joueurs sont des joueurs fictifs : le vrai social arrivera avec le serveur.
import { useEffect, useRef, useState } from 'preact/hooks';
import { GUILD_BOSS_ATTEMPTS, GUILD_SHOP, UNLOCKS } from '../../../core/data/modes';
import { createRng } from '../../../core/rng';
import { heroImage, monsterImage } from '../../art';
import { CHAT_LINES, fmt, t } from '../../i18n';
import {
  BOT_GUILDS, botChatter, buyExchange, guildBossPlan, joinGuild, leaveGuild, markSeen, sendChat,
} from '../../state/actions';
import { isUnlocked, teamPower } from '../../state/selectors';
import { getState, now, useGame } from '../../state/store';
import type { ChatMessage } from '../../state/types';
import { Bar, Btn, Cur, Icon, Locked, Modal, Tabs } from '../kit';
import { open, prepare } from '../nav';
import { ShopTile } from './adventure';

const MEMBER_NAMES = ['Kaïro', 'Lunaria', 'Vaelis', 'Tormund', 'Ishara', 'Mikaze', 'Orsolya', 'Bastien', 'Yuna', 'Ragnis', 'Selka', 'Noctis'];
const GUILD_BOSS_HP = 50_000_000;

/** Membres fictifs de la guilde : leur force suit celle du joueur, leurs dégâts montent avec le temps. */
function members(guild: string) {
  const rng = createRng(guild.length * 977);
  const mine = Math.max(1000, teamPower(getState()));
  return MEMBER_NAMES.slice(0, 9).map((name, i) => ({
    name,
    power: Math.round(mine * (0.6 + rng() * 0.9)),
    role: i === 0 ? '♛' : i < 3 ? '★' : '',
    defId: ['knights-10', 'mages-11', 'angels-12', 'demons-10', 'myths-10', 'assassins-11', 'knights-6', 'mages-7', 'angels-8'][i]!,
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
  if (!isUnlocked(s, 'guild')) {
    return <div class="screen"><section class="card center"><Icon name="guild" size={64} /><h1>{t('nav.guild')}</h1><Locked stage={UNLOCKS.guild} /></section></div>;
  }
  if (!s.guild.joined) {
    return (
      <div class="screen list">
        <h1>{t('nav.guild')}</h1>
        {BOT_GUILDS.map((g, i) => (
          <div class="card row between center-y">
            <div>
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
    <div class="screen">
      <div class="card guild-head">
        <h1>{s.guild.joined}</h1>
        <div class="row between"><span class="muted">{t('guild.level', { n: 7 })} · 22 / 30</span><Cur k="guildCoins" n={s.wallet.guildCoins} /></div>
      </div>
      <Tabs value={tab} onChange={setTab} options={[
        ['boss', t('guild.boss'), left > 0], ['war', t('guild.war')], ['members', t('guild.members')], ['chat', t('guild.chat')], ['shop', t('guild.shop')],
      ]} />
      {tab === 'boss' && (
        <section class="card center">
          <img class="boss-img" src={monsterImage('dragon', 'fire')} alt="" />
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
            <div class="card member"><img src={heroImage(m.defId)} alt="" /><strong class="grow">{m.role} {m.name}</strong><span class="power-chip"><Icon name="power" size={16} />{fmt(m.power)}</span></div>
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
 * Guerre de guildes : APERÇU de l'écran, les règles sont encore à décider avec le propriétaire.
 * Deux guildes face à face, les défenses adverses à attaquer, les étoiles gagnées.
 */
function GuildWar({ guild }: { guild: string }) {
  const s = useGame();
  const foe = BOT_GUILDS.find((g) => g !== guild) ?? BOT_GUILDS[0]!;
  const enemies = members(foe);
  return (
    <section class="list war">
      <div class="card war-head">
        <div class="war-side"><Icon name="guild" size={34} /><strong>{guild}</strong><span class="war-score">★ 0</span></div>
        <span class="war-vs">VS</span>
        <div class="war-side"><Icon name="guild" size={34} /><strong>{foe}</strong><span class="war-score">★ 0</span></div>
      </div>
      <div class="row between center-y">
        <span class="tag">{t('soon')}</span>
        <span class="muted">{t('boss.attempts', { n: 2, m: 2 })}</span>
      </div>
      <div class="war-grid">
        {enemies.map((m) => (
          <div class="card war-fort">
            <img src={heroImage(m.defId)} alt="" />
            <strong>{m.name}</strong>
            <span class={`power-chip ${teamPower(s) >= m.power ? 'ok' : 'low'}`}><Icon name="power" size={14} />{fmt(m.power)}</span>
            <span class="def-stars"><span class="off">★★★</span></span>
          </div>
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
