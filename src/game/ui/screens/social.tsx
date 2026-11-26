// Social : guilde (boss commun, membres, tchat, boutique), tchat général, classements.
// Dans le prototype, les autres joueurs sont des joueurs fictifs : le vrai social arrivera avec le serveur.
// Style « moderne » de la guilde (26/11/2026) : sections/guilde.css (carte de la guilde à l'emblème, onglets en tuiles,
// boss en grand, membres en lignes nettes). L'onglet tient dans l'écran : seules les listes défilent, à l'intérieur.
import type { ComponentChildren } from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';
import { DungeonArt } from '../backdrop-dungeon';
import { GUILD_BOSS_ATTEMPTS, GUILD_SHOP, GUILD_WAR, UNLOCKS } from '../../../core/data/modes';
import { BOSS_ELEMENT } from '../../../core/data/monsters';
import { createRng } from '../../../core/rng';
import { heroImage } from '../../art';
import { CHAT_LINES, fmt, t } from '../../i18n';
import {
  BOT_GUILDS, botChatter, claimWar, ensureWar, guildBossEndsAt, guildBossId, guildBossPlan, joinGuild, leaveGuild, markSeen, sendChat,
  warAttacksLeft, warDefenses, warPhase, warPlan, warScores,
} from '../../state/actions';
import { isUnlocked, teamPower } from '../../state/selectors';
import { getState, now, useGame } from '../../state/store';
import type { ChatMessage } from '../../state/types';
import { Bar, Btn, Icon, Locked, Modal, RedDot, Tabs } from '../kit';
import { btClass } from '../buttons';
import { open, prepare } from '../nav';
import { ModeShop } from '../sections/boutiques-modes';
import { TeamStrip } from './heroes';
import '../sections/guilde.css';

const MEMBER_NAMES = ['Kaïro', 'Lunaria', 'Vaelis', 'Tormund', 'Ishara', 'Mikaze', 'Orsolya', 'Bastien', 'Yuna', 'Ragnis', 'Selka', 'Noctis'];
const GUILD_BOSS_HP = 50_000_000;

/** Emblème d'une guilde (12 dessins) : choisi d'après son nom, toujours le même pour une guilde. */
function emblem(guild: string): string {
  let h = 0;
  for (const c of guild) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return `emblem-${h % 12}`;
}

type Role = 'leader' | 'officer' | '';
interface Member { name: string; power: number; level: number; role: Role; defId: string; me?: boolean }

/** Membres fictifs de la guilde (leur force suit celle du joueur), avec le joueur : le chef, les officiers, puis par puissance. */
function members(guild: string): Member[] {
  const s = getState();
  const rng = createRng(guild.length * 977);
  const mine = Math.max(1000, teamPower(s));
  const lv = s.account.level;
  const bots: Member[] = MEMBER_NAMES.slice(0, 9).map((name, i) => ({
    name,
    power: Math.round(mine * (0.6 + rng() * 0.9)),
    level: Math.max(5, Math.round(lv * (0.7 + rng() * 0.6))),
    role: i === 0 ? 'leader' : i < 3 ? 'officer' : '',
    defId: ['knights-9', 'mages-11', 'angels-6', 'demons-9', 'myths-10', 'assassins-11', 'knights-7', 'mages-7', 'angels-10'][i]!,
  }));
  const me: Member = { name: s.name, power: Math.round(teamPower(s)), level: lv, role: '', defId: s.heroes[0]?.defId ?? 'knights-1', me: true };
  const rank = (m: Member) => (m.role === 'leader' ? 0 : m.role === 'officer' ? 1 : 2);
  return [...bots, me].sort((a, b) => rank(a) - rank(b) || b.power - a.power);
}

function botDamage(): number {
  const s = getState();
  const hours = (now() - (s.createdAt ?? now())) / 3.6e6;
  return Math.min(GUILD_BOSS_HP * 0.9, Math.round(hours * 180_000));
}

/** L'emblème posé sur sa tuile arrondie (dégradé, halo) : la pièce forte de la guilde. */
function Crest({ name, size = 'm' }: { name: string; size?: 's' | 'm' | 'l' }) {
  return <span class={`g-crest g-crest-${size}`}><Icon name={name} size={size === 'l' ? 60 : size === 'm' ? 44 : 40} /></span>;
}

/** La carte de la guilde, posée au pied du panorama de la forteresse : emblème, nom, niveau et membres, pièces de guilde. */
function GuildHead({ title, crest, meta, side }: { title: string; crest: string; meta?: ComponentChildren; side?: ComponentChildren }) {
  return (
    <header class="g-head">
      <Crest name={crest} size="l" />
      <div class="g-id">
        <h1 class="g-name">{title}</h1>
        {meta && <div class="g-meta">{meta}</div>}
      </div>
      {side}
    </header>
  );
}

type GuildTab = 'boss' | 'war' | 'members' | 'chat' | 'shop';
const TAB_ICONS: Record<GuildTab, string> = { boss: 'dailyBoss', war: 'arena', members: 'friends', chat: 'chat', shop: 'shop' };

/** Les onglets de la guilde : une rangée de tuiles (picto + nom) ; l'onglet ouvert est une tuile azur soulevée. */
function GuildTabs({ value, options, onChange }: { value: GuildTab; options: [GuildTab, string, boolean?][]; onChange: (v: GuildTab) => void }) {
  return (
    <nav class="g-tabs bt-rail">
      {options.map(([v, label, dot]) => (
        <button class={`g-tab${v === value ? ` on ${btClass('basalte', 'm')}` : ''}`} onClick={() => onChange(v)}>
          <Icon name={TAB_ICONS[v]} size={26} />
          <span class="g-tab-label">{label}</span>
          {dot && <RedDot />}
        </button>
      ))}
    </nav>
  );
}

export function GuildScreen() {
  const s = useGame();
  const [tab, setTab] = useState<GuildTab>('boss');
  useEffect(() => markSeen('guild'), []);
  if (!isUnlocked(s, 'guild')) {
    return (
      <div class="screen guild">
        <GuildHead title={t('nav.guild')} crest="guild" />
        <section class="g-panel g-locked"><Icon name="lock" size={48} /><Locked stage={UNLOCKS.guild} /></section>
      </div>
    );
  }
  if (!s.guild.joined) {
    return (
      <div class="screen guild">
        <GuildHead title={t('nav.guild')} crest="guild" />
        <section class="g-scroll g-list">
          {BOT_GUILDS.map((g, i) => {
            const count = 18 + i * 4;
            return (
              <div class="g-row g-find">
                <Crest name={emblem(g)} size="s" />
                <div class="g-row-main">
                  <strong class="g-row-name">{g}</strong>
                  <span class="g-row-sub">
                    <span class="g-lv">{t('guild.level', { n: 5 + i * 3 })}</span>
                    <span class="g-fill"><Icon name="friends" size={16} />{count} / 30<i style={{ '--p': `${Math.round((count / 30) * 100)}%` } as never} /></span>
                  </span>
                </div>
                <Btn kind="green" small onClick={() => joinGuild(g)}>{t('guild.join')}</Btn>
              </div>
            );
          })}
        </section>
      </div>
    );
  }
  const name = s.guild.joined;
  const total = Math.min(GUILD_BOSS_HP, botDamage() + s.guild.bossDamage);
  const left = GUILD_BOSS_ATTEMPTS - s.daily.guildAttempts;
  const warDot = !!s.guildWar && (warAttacksLeft(s.guildWar) > 0 || !!s.guildWar.pending || (warPhase() === 'results' && !s.guildWar.claimed));
  return (
    <div class="screen guild">
      <GuildHead title={name} crest={emblem(name)}
        meta={<><span class="g-lv">{t('guild.level', { n: 7 })}</span><span class="g-count"><Icon name="friends" size={18} />22 / 30</span></>}
        side={<span class="g-coins"><Icon name="guildCoins" size={26} /><b>{fmt(s.wallet.guildCoins)}</b></span>} />
      <GuildTabs value={tab} onChange={setTab} options={[
        ['boss', t('guild.boss'), left > 0], ['war', t('guild.war'), warDot], ['members', t('guild.members')], ['chat', t('guild.chat')], ['shop', t('guild.shop')],
      ]} />
      {tab === 'boss' && (
        <section class="g-panel g-boss">
          <DungeonStage hp={<Bar value={GUILD_BOSS_HP - total} max={GUILD_BOSS_HP} color="linear-gradient(90deg, #f03e58, #ff7a6a)" label={`${fmt(GUILD_BOSS_HP - total)} / ${fmt(GUILD_BOSS_HP)}`} />} />
          <div class="g-stats">
            <div class="g-stat"><Icon name="atk" size={30} /><span><b>{fmt(total)}</b><small>{t('guild.total')}</small></span></div>
            <div class="g-stat mine"><Icon name="power" size={30} /><span><b>{fmt(s.guild.bossDamage)}</b><small>{t('guild.mine')}</small></span></div>
          </div>
          <Btn kind="red" wide class="g-attack" disabled={left <= 0} onClick={() => prepare(guildBossPlan())}>
            <span>{t('boss.attack')}</span><span class="g-tries">{left} / {GUILD_BOSS_ATTEMPTS}</span>
          </Btn>
        </section>
      )}
      {tab === 'members' && (
        <section class="g-scroll g-list">
          {members(name).map((m) => (
            <div class={`g-row g-member${m.me ? ' me' : ''}`}>
              <span class="g-face"><img src={heroImage(m.defId)} alt="" /><span class="g-face-lv">{m.level}</span></span>
              <div class="g-row-main">
                <strong class="g-row-name">{m.name}</strong>
                {m.role && <span class={`g-role ${m.role}`}><Icon name={m.role === 'leader' ? 'crown' : 'star'} size={15} />{t(`guild.${m.role}`)}</span>}
              </div>
              <span class="g-power"><Icon name="power" size={18} />{fmt(m.power)}</span>
            </div>
          ))}
          <button class={`g-leave ${btClass('feu', 's')}`} onClick={() => open({ type: 'confirm', text: `${t('guild.leave')} ?`, onYes: leaveGuild })}>{t('guild.leave')}</button>
        </section>
      )}
      {tab === 'war' && <GuildWar guild={name} />}
      {tab === 'chat' && <Chat target="guild" />}
      {tab === 'shop' && (
        <section class="g-shop"><ModeShop kind="guild" items={GUILD_SHOP} crest={emblem(name)} /></section>
      )}
    </div>
  );
}

/** HH:MM (les heures peuvent dépasser 24). */
function hhmm(ms: number): string {
  const m = Math.max(0, Math.ceil(ms / 60_000));
  return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
}

/**
 * Le boss de guilde, montré par son élément (demande du propriétaire, 26/11/2026) : la grande image de la porte de son
 * donjon (« Donjon de feu »…, backdrop-dungeon.tsx) et le temps qu'il reste avant qu'il change (à minuit, avec les essais).
 * L'élément change avec le boss : l'image suit toute seule.
 */
function DungeonStage({ hp }: { hp: ComponentChildren }) {
  const [, tick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => tick((x) => x + 1), 1000);
    return () => clearInterval(id);
  }, []);
  const element = BOSS_ELEMENT[guildBossId()] ?? 'fire';
  return (
    <div class={`g-boss-stage g-dungeon el-${element}`}>
      <DungeonArt element={element} class="g-dungeon-art" />
      <div class="g-boss-label">
        <span class="g-boss-name"><Icon name={element} size={22} /><span class="g-boss-title">{t(`gboss.${element}`)}</span></span>
        <span class="g-boss-time"><Icon name="hourglass" size={16} />{t('gboss.left', { d: hhmm(guildBossEndsAt() - now()) })}</span>
      </div>
      <div class="g-boss-hp">{hp}</div>
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
    <section class="g-scroll g-war">
      <div class="g-vs">
        <div class="g-vs-side"><Crest name={emblem(guild)} size="m" /><strong>{guild}</strong><span class="g-vs-score"><Icon name="star" size={18} />{sc.mine}</span></div>
        <span class="g-vs-badge">VS</span>
        <div class="g-vs-side foe"><Crest name={emblem(w.foe)} size="m" /><strong>{w.foe}</strong><span class="g-vs-score"><Icon name="star" size={18} />{sc.foe}</span></div>
      </div>

      {(showResult || pending) && (
        <div class={`g-war-result ${result}`}>
          <h2>{t(`war.${result}`)}</h2>
          <Btn kind="gold" wide onClick={() => {
            const gain = claimWar();
            if (gain) open({ type: 'gain', title: t('guild.war'), gain });
          }}>{t('claim')}</Btn>
        </div>
      )}

      <div class="g-war-phase">
        <span class="g-pill">{t(`war.${phase}`)}{phase === 'battle' && ` · ${t('war.day', { n: Math.min(5, Math.floor((new Date(now()).getDay() + 6) % 7)) })}`}</span>
        {phase === 'battle' && <span class={`g-pill${left ? ' gold' : ''}`}>{t('war.attacks', { n: left, m: GUILD_WAR.attacksPerDay })}</span>}
      </div>

      <TeamStrip />
      <TeamStrip team="defense" />

      <div class="g-forts">
        {defenses.map((d, i) => {
          const leader = d.team.find((m) => m.slot === 2) ?? d.team[0]!;
          return (
            <button class="g-fort" disabled={!left} onClick={() => { const p = warPlan(i); if (p) prepare(p); }}>
              <span class="g-face"><img src={heroImage(leader.defId)} alt="" /></span>
              <strong>{d.name}</strong>
              <span class={`g-power ${mine >= d.power ? 'ok' : 'low'}`}><Icon name="power" size={14} />{fmt(d.power)}</span>
            </button>
          );
        })}
      </div>

      <h3 class="g-sub">{t('war.ranking')}</h3>
      <div class="g-ranking">
        {sc.members.map((m, i) => (
          <div class={`g-rank-row${m.me ? ' me' : ''}`}>
            <span class={`g-rank r${i + 1}`}>{i + 1}</span>
            <span class="g-rank-name">{m.name}</span>
            <span class="g-stars"><Icon name="star" size={16} />{m.stars}</span>
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
