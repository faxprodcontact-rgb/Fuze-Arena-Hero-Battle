// L'application : barre du haut, raccourcis, onglets, fenêtres et combat.
import { useEffect, useRef, useState } from 'preact/hooks';
import { accountXpForLevel } from '../../core/data/modes';
import { heroImage } from '../art';
import { runBattle } from '../battle-scene';
import { fmt, t } from '../i18n';
import { ensureDay, finishBattle, type BattleRequest } from '../state/actions';
import { getState, useGame } from '../state/store';
import { dots } from './dots';
import { Cur, Icon, RedDot } from './kit';
import { teamPower } from '../state/selectors';
import { close, go, open, startBattle, useNav, type Modal, type Tab } from './nav';
import { AdventureScreen } from './screens/adventure';
import { CampaignScreen, FastLootModal } from './screens/campaign';
import { Prep } from './screens/prep';
import { ItemModal } from './screens/bag';
import { ForgePage } from './screens/forge';
import { FusionPage } from './screens/fusion';
import { ResetPage } from './screens/reset';
import { MissionPage } from './screens/mission';
import { DungeonPage } from './screens/dungeon';
import { HeroDetail } from './screens/hero-detail';
import { HeroesScreen } from './screens/heroes';
import { AdModal, ConfirmModal, GainModal, LegalModal, NameScreen, QuestsModal, RenameModal, SettingsModal, ShopModal } from './screens/meta';
import { ChatModal, GuildScreen, RankingModal } from './screens/social';
import { OddsModal, SummonResult, SummonScreen } from './screens/summon';

const TABS: Tab[] = ['campaign', 'heroes', 'summon', 'adventure', 'guild'];

function TopBar() {
  const s = useGame();
  const leader = s.heroes.find((h) => h.uid === s.formation[0]?.[0]) ?? s.heroes[0];
  return (
    <header class="topbar">
      <button class="avatar" aria-label={t('side.settings')} onClick={() => open({ type: 'settings' })}>
        {leader && <img src={heroImage(leader.defId)} alt="" />}
        <span class="avatar-lv">{s.account.level}</span>
        <span class="avatar-xp" style={{ width: `${(s.account.xp / accountXpForLevel(s.account.level)) * 100}%` }} />
      </button>
      <div class="who">
        <strong>{s.name}</strong>
        <span class="power-chip"><Icon name="power" size={14} />{fmt(teamPower(s))}</span>
      </div>
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
    case 'prep': return <Prep plan={modal.plan} />;
    case 'fastLoot': return <FastLootModal />;
    case 'rename': return <RenameModal />;
    case 'fusion': return <FusionPage uid={modal.uid} />;
    case 'forge': return <ForgePage />;
    case 'reset': return <ResetPage uid={modal.uid} />;
    case 'mission': return <MissionPage id={modal.id} />;
    case 'dungeon': return <DungeonPage kind={modal.kind} />;
    case 'item': return <ItemModal uid={modal.uid} />;
    case 'legal': return <LegalModal doc={modal.doc} />;
  }
}

function BattleOverlay({ request }: { request: BattleRequest }) {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!host.current) return;
    return runBattle(host.current, request, (result) => {
      const gain = finishBattle(request, result);
      startBattle(null);
      const named = request.kind === 'campaign' || request.kind === 'tower' || request.kind === 'dungeon';
      const title = `${t(`mode.${request.kind}`)}${named ? ` ${request.title}` : ''}`;
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
      <main class={`content${nav.tab === 'campaign' ? ' content-home' : ''}`}>
        {nav.tab === 'campaign' && <CampaignScreen running={!nav.battle && !nav.modals.some((m) => m.type === 'prep')} />}
        {nav.tab === 'heroes' && <HeroesScreen />}
        {nav.tab === 'summon' && <SummonScreen />}
        {nav.tab === 'adventure' && <AdventureScreen sub={nav.sub} />}
        {nav.tab === 'guild' && <GuildScreen />}
      </main>
      <TabBar tab={nav.tab} />
      {nav.modals.map((m) => <ModalView modal={m} />)}
      {nav.battle && <BattleOverlay request={nav.battle} />}
      {nav.toast && <div class="toast" onClick={close}>{nav.toast}</div>}
      {!getState().named && <NameScreen />}
    </div>
  );
}
