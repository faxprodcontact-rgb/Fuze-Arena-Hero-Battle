// L'application : barre du haut, raccourcis, onglets, fenêtres et combat.
import { useEffect, useRef, useState } from 'preact/hooks';
import { accountXpForLevel } from '../../core/data/modes';
import { heroImage } from '../art';
import { runBattle } from '../battle-scene';
import { t } from '../i18n';
import { ensureDay, finishBattle, type BattleRequest } from '../state/actions';
import { useGame } from '../state/store';
import { dots } from './dots';
import { Cur, Icon, RedDot } from './kit';
import { close, go, open, startBattle, useNav, type Modal, type Tab } from './nav';
import { AdventureScreen } from './screens/adventure';
import { CampaignScreen } from './screens/campaign';
import { HeroDetail } from './screens/hero-detail';
import { HeroesScreen } from './screens/heroes';
import { AdModal, ConfirmModal, GainModal, QuestsModal, SettingsModal, ShopModal } from './screens/meta';
import { ChatModal, GuildScreen, RankingModal } from './screens/social';
import { OddsModal, SummonResult, SummonScreen } from './screens/summon';

const TABS: Tab[] = ['campaign', 'heroes', 'summon', 'adventure', 'guild'];

function TopBar() {
  const s = useGame();
  const leader = s.heroes.find((h) => h.uid === s.formation[0]?.[0]) ?? s.heroes[0];
  return (
    <header class="topbar">
      <button class="avatar" onClick={() => open({ type: 'settings' })}>
        {leader && <img src={heroImage(leader.defId)} alt="" />}
        <span class="avatar-lv">{s.account.level}</span>
        <span class="avatar-xp" style={{ width: `${(s.account.xp / accountXpForLevel(s.account.level)) * 100}%` }} />
      </button>
      <div class="wallet">
        <Cur k="gold" n={s.wallet.gold} />
        <Cur k="essence" n={s.wallet.essence} />
        <button class="gems" onClick={() => open({ type: 'shop' })}>
          <Cur k="gems" n={s.wallet.gems} />
          <span class="plus">+</span>
        </button>
      </div>
    </header>
  );
}

function SideBar() {
  const s = useGame();
  const items: [string, () => void, boolean][] = [
    ['quests', () => open({ type: 'quests' }), dots.quests(s)],
    ['shop', () => open({ type: 'shop' }), !s.shop.bought.starter],
    ['pass', () => open({ type: 'shop', tab: 'pass' }), dots.pass(s)],
    ['ranking', () => open({ type: 'ranking' }), false],
    ['chat', () => open({ type: 'chat' }), false],
    ['settings', () => open({ type: 'settings' }), false],
  ];
  return (
    <nav class="sidebar">
      {items.map(([name, action, dot]) => (
        <button class="side-btn" onClick={action}>
          <Icon name={name} size={26} />
          <span>{t(`side.${name}`)}</span>
          {dot && <RedDot />}
        </button>
      ))}
    </nav>
  );
}

function TabBar({ tab }: { tab: Tab }) {
  const s = useGame();
  return (
    <nav class="tabbar">
      {TABS.map((x) => (
        <button class={`tabbar-btn${x === tab ? ' on' : ''}`} onClick={() => go(x)}>
          <Icon name={x} size={28} />
          <span>{t(`nav.${x}`)}</span>
          {x !== tab && dots[x](s) && <RedDot />}
        </button>
      ))}
    </nav>
  );
}

function ModalView({ modal }: { modal: Modal }) {
  switch (modal.type) {
    case 'hero': return <HeroDetail uid={modal.uid} />;
    case 'gain': return <GainModal title={modal.title} gain={modal.gain} damage={modal.damage} win={modal.win} />;
    case 'summon': return <SummonResult heroes={modal.heroes} />;
    case 'quests': return <QuestsModal />;
    case 'shop': return <ShopModal tab={modal.tab} />;
    case 'ranking': return <RankingModal />;
    case 'chat': return <ChatModal />;
    case 'settings': return <SettingsModal />;
    case 'odds': return <OddsModal />;
    case 'confirm': return <ConfirmModal text={modal.text} onYes={modal.onYes} />;
    case 'ad': return <AdModal onDone={modal.onDone} />;
  }
}

function BattleOverlay({ request }: { request: BattleRequest }) {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!host.current) return;
    return runBattle(host.current, request, (result) => {
      const gain = finishBattle(request, result);
      startBattle(null);
      const title = t(`mode.${request.kind}`);
      if (request.damageMode) open({ type: 'gain', title, gain, damage: result.damage });
      else open({ type: 'gain', title, gain, win: result.win });
    });
  }, [request]);
  return <div class="battle" ref={host} />;
}

export function App() {
  useGame();
  const nav = useNav();
  const [, setClock] = useState(0);
  useEffect(() => {
    ensureDay();
    const day = setInterval(ensureDay, 30_000);
    // Le butin et les minuteurs avancent à l'écran.
    const clock = setInterval(() => setClock((x) => x + 1), 1000);
    return () => {
      clearInterval(day);
      clearInterval(clock);
    };
  }, []);
  return (
    <div class="app">
      <TopBar />
      <SideBar />
      <main class="content">
        {nav.tab === 'campaign' && <CampaignScreen />}
        {nav.tab === 'heroes' && <HeroesScreen />}
        {nav.tab === 'summon' && <SummonScreen />}
        {nav.tab === 'adventure' && <AdventureScreen sub={nav.sub} />}
        {nav.tab === 'guild' && <GuildScreen />}
      </main>
      <TabBar tab={nav.tab} />
      {nav.modals.map((m) => <ModalView modal={m} />)}
      {nav.battle && <BattleOverlay request={nav.battle} />}
      {nav.toast && <div class="toast" onClick={close}>{nav.toast}</div>}
    </div>
  );
}
