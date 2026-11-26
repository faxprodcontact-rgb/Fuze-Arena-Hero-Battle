// Fenêtres : quêtes, boutique et passe, réglages, récompenses, pub simulée, confirmation.
import { useEffect, useState } from 'preact/hooks';
import {
  AD_SECONDS, ARENA_SHOP, DAILY_CHESTS, DAILY_QUESTS, GUILD_SHOP, OFFERS, PASS_LEVELS, PASS_POINTS_PER_LEVEL,
  WEEKLY_CHESTS, WEEKLY_QUESTS, type Reward,
} from '../../../core/data/modes';
import { STARTER_HERO, heroDef } from '../../../core/data/heroes';
import { RENAME_COST } from '../../../core/data/modes';
import { heroImage } from '../../art';
import { legalDoc, type LegalDoc } from '../../legal';
import { APP_VERSION } from '../../version';
import { t } from '../../i18n';
import {
  buyExchange, buyOffer, claimChest, claimPass, claimQuest, passLevel, questPoints,
  chooseName, deleteAccount, playerId, randomName, rename, setLang, setSetting,
} from '../../state/actions';
import { now, useGame } from '../../state/store';
import type { Gain } from '../../state/types';
import { Art, Bar, Btn, Cur, HeroCard, Icon, ItemIcon, Modal, Sign, Tabs } from '../kit';
import { close, open, toast } from '../nav';
import { Halo } from '../anim';
import { ShopTile } from './adventure';
import { AvatarRow } from './avatar';

function RewardLine({ reward }: { reward: Reward }) {
  return <span class="row gap-s wrap">{Object.entries(reward).map(([k, v]) => <Cur k={k} n={v ?? 0} />)}</span>;
}

export function QuestsModal() {
  const s = useGame();
  const [kind, setKind] = useState<'daily' | 'weekly'>('daily');
  const defs = kind === 'daily' ? DAILY_QUESTS : WEEKLY_QUESTS;
  const box = kind === 'daily' ? s.daily : s.weekly;
  const chests = kind === 'daily' ? DAILY_CHESTS : WEEKLY_CHESTS;
  const points = questPoints(kind);
  const max = chests[chests.length - 1]!.points;
  return (
    <Modal title={t('side.quests')} wide>
      <Tabs value={kind} onChange={setKind} options={[['daily', t('quests.daily')], ['weekly', t('quests.weekly')]]} />
      <div class="activity">
        <Bar value={points} max={max} color="var(--gold)" label={`${t('quests.activity')} ${points}`} />
        <div class="chests">
          {chests.map((c, i) => {
            const done = box.chests.includes(i);
            const ready = !done && points >= c.points;
            return (
              <button class={`chest-btn${done ? ' done' : ''}${ready ? ' ready' : ''}`} style={{ left: `${(c.points / max) * 100}%` }}
                onClick={() => {
                  const gain = claimChest(i, kind);
                  if (gain) open({ type: 'gain', title: t('quests.activity'), gain });
                }}>
                <Art name={done ? 'chestOpen' : ready ? 'chestReady' : 'chestClosed'} size={36} class="chest-mini" />
                <small>{c.points}</small>
              </button>
            );
          })}
        </div>
      </div>
      <ul class="quests">
        {defs.map((q) => {
          const progress = Math.min(q.goal, box.quests[q.id] ?? 0);
          const claimed = box.claimed.includes(q.id);
          const ready = !claimed && progress >= q.goal;
          return (
            <li class={claimed ? 'done' : ''}>
              <div class="grow">
                <strong>{t(`quest.${q.event}`)}</strong>
                <Bar value={progress} max={q.goal} label={`${progress} / ${q.goal}`} />
              </div>
              <span class="pts">+{q.points}</span>
              {claimed ? <span class="muted small">{t('claimed')}</span> : (
                <Btn kind={ready ? 'gold' : 'ghost'} small disabled={!ready} onClick={() => claimQuest(q.id, kind)}>{t('claim')}</Btn>
              )}
            </li>
          );
        })}
      </ul>
    </Modal>
  );
}

function simulatedBuy(id: string) {
  open({
    type: 'confirm',
    text: t('shop.simulated'),
    onYes: () => {
      const gain = buyOffer(id);
      if (gain) open({ type: 'gain', title: id.startsWith('gems') ? t('shop.gems') : t(`offer.${id}`), gain });
    },
  });
}

export function ShopModal({ tab: initial = 'offers' }: { tab?: 'offers' | 'pass' | 'exchange' }) {
  const s = useGame();
  const [tab, setTab] = useState<'offers' | 'gems' | 'pass' | 'exchange'>(initial);
  const level = passLevel(s);
  return (
    <Modal title={t('side.shop')} wide>
      <Tabs value={tab} onChange={setTab} options={[
        ['offers', t('shop.offers')], ['gems', t('shop.gems')], ['pass', t('shop.pass')], ['exchange', t('shop.exchange')],
      ]} />
      {tab === 'offers' && (
        <div class="list">
          {OFFERS.filter((o) => o.kind !== 'gems').map((o) => {
            const bought = s.shop.bought[o.id] ?? 0;
            const soldOut = o.limit > 0 && bought >= o.limit;
            const cardDays = Math.ceil((s.shop.cardUntil - now()) / 86_400_000);
            return (
              <div class={`card offer offer-${o.kind}`}>
                <Art class="offer-art" name={`offer-${o.kind}`} />
                <div class="grow">
                  <strong>{t(`offer.${o.id}`)}</strong>
                  {o.kind === 'card' && <p class="muted small">{cardDays > 0 ? t('offer.daysLeft', { n: cardDays }) : t('offer.card.desc')}</p>}
                  {o.kind === 'noAds' && <p class="muted small">{t('offer.noads.desc')}</p>}
                  <RewardLine reward={o.reward} />
                </div>
                <Btn kind="gold" small disabled={soldOut} onClick={() => simulatedBuy(o.id)}>{soldOut ? t('offer.owned') : o.price}</Btn>
              </div>
            );
          })}
        </div>
      )}
      {tab === 'gems' && (
        <div class="shop-grid">
          {OFFERS.filter((o) => o.kind === 'gems').map((o) => (
            <ShopTile cost={o.price} reward={o.reward} onBuy={() => simulatedBuy(o.id)} art={`offer-${o.id}`} />
          ))}
        </div>
      )}
      {tab === 'pass' && (
        <div class="list">
          <div class="card">
            <div class="row between"><strong>{t('pass.level', { n: level })}</strong><span class="muted">{t('pass.points', { n: s.pass.points % PASS_POINTS_PER_LEVEL, m: PASS_POINTS_PER_LEVEL })}</span></div>
            <Bar value={s.pass.points % PASS_POINTS_PER_LEVEL} max={PASS_POINTS_PER_LEVEL} color="#a35cff" />
            {!s.shop.passPremium && <Btn kind="purple" wide onClick={() => simulatedBuy('pass')}>{t('offer.pass')} · 9,99 €</Btn>}
          </div>
          <div class="pass-grid">
            <span class="muted small">{t('pass.free')}</span><span /><span class="muted small">{t('pass.premium')}</span>
            {PASS_LEVELS.slice(0, Math.max(10, level + 3)).map((lv, i) => (
              <>
                <PassCell reward={lv.free} done={s.pass.claimedFree.includes(i)} ready={i < level} onClaim={() => claimPass(i, false)} />
                <span class={`pass-num${i < level ? ' on' : ''}`}>{i + 1}</span>
                <PassCell reward={lv.premium} done={s.pass.claimedPremium.includes(i)} ready={i < level && s.shop.passPremium} locked={!s.shop.passPremium} onClaim={() => claimPass(i, true)} />
              </>
            ))}
          </div>
        </div>
      )}
      {tab === 'exchange' && (
        <div class="list">
          <h3><Cur k="arenaTokens" n={s.wallet.arenaTokens} /></h3>
          <div class="shop-grid">
            {ARENA_SHOP.map((x) => <ShopTile cost={<Cur k="arenaTokens" n={x.cost} />} reward={x.reward} disabled={s.wallet.arenaTokens < x.cost}
              onBuy={() => { const g = buyExchange('arena', x.id); if (g) open({ type: 'gain', title: t('shop.exchange'), gain: g }); }} />)}
          </div>
          <h3><Cur k="guildCoins" n={s.wallet.guildCoins} /></h3>
          <div class="shop-grid">
            {GUILD_SHOP.map((x) => <ShopTile cost={<Cur k="guildCoins" n={x.cost} />} reward={x.reward} disabled={s.wallet.guildCoins < x.cost}
              onBuy={() => { const g = buyExchange('guild', x.id); if (g) open({ type: 'gain', title: t('shop.exchange'), gain: g }); }} />)}
          </div>
        </div>
      )}
    </Modal>
  );
}

function PassCell(p: { reward: Reward; done: boolean; ready: boolean; locked?: boolean; onClaim: () => void }) {
  return (
    <button class={`pass-cell${p.done ? ' done' : ''}${p.ready && !p.done ? ' ready' : ''}${p.locked ? ' locked' : ''}`}
      onClick={() => p.ready && !p.done && p.onClaim()}>
      <RewardLine reward={p.reward} />
    </button>
  );
}

function Toggle({ on, onChange, label }: { on: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button class="setting-row" role="switch" aria-checked={on} onClick={() => onChange(!on)}>
      <span>{label}</span>
      <span class={`switch${on ? ' on' : ''}`}><span /></span>
    </button>
  );
}

function LinkRow({ label, onClick, danger }: { label: string; onClick: () => void; danger?: boolean }) {
  return (
    <button class={`setting-row${danger ? ' danger' : ''}`} onClick={onClick}>
      <span>{label}</span>
      <Sign name="chev-s" class="chev" />
    </button>
  );
}

export function SettingsModal() {
  const s = useGame();
  return (
    <Modal title={t('side.settings')}>
      <section class="settings-group">
        <h3>{t('settings.account')}</h3>
        <AvatarRow />
        <div class="setting-row static">
          <span>{t('settings.name')}</span>
          <span class="row gap-s center-y">
            <b>{s.name}</b>
            <Btn kind="ghost" small onClick={() => open({ type: 'rename' })}>{t('settings.rename')}</Btn>
          </span>
        </div>
        <div class="setting-row static">
          <span>{t('settings.id')}</span>
          <b class="mono">{playerId(s)}</b>
        </div>
      </section>

      <section class="settings-group">
        <h3>{t('settings.game')}</h3>
        <div class="setting-row static">
          <span>{t('settings.lang')}</span>
          <span class="row gap-s">
            <Btn kind={s.lang === 'fr' ? 'green' : 'ghost'} small onClick={() => setLang('fr')}>Français</Btn>
            <Btn kind={s.lang === 'en' ? 'green' : 'ghost'} small onClick={() => setLang('en')}>English</Btn>
          </span>
        </div>
        <Toggle label={t('settings.sound')} on={s.settings.sound} onChange={(v) => setSetting('sound', v)} />
        <Toggle label={t('settings.music')} on={s.settings.music} onChange={(v) => setSetting('music', v)} />
        <Toggle label={t('settings.notifications')} on={s.settings.notifications} onChange={(v) => setSetting('notifications', v)} />
      </section>

      <section class="settings-group">
        <h3>{t('settings.info')}</h3>
        <LinkRow label={t('legal.privacy')} onClick={() => open({ type: 'legal', doc: 'privacy' })} />
        <LinkRow label={t('legal.terms')} onClick={() => open({ type: 'legal', doc: 'terms' })} />
        <LinkRow label={t('legal.notice')} onClick={() => open({ type: 'legal', doc: 'notice' })} />
        <LinkRow label={t('summon.odds')} onClick={() => open({ type: 'odds' })} />
        <LinkRow label={t('legal.support')} onClick={() => open({ type: 'legal', doc: 'support' })} />
        <LinkRow label={t('legal.credits')} onClick={() => open({ type: 'legal', doc: 'credits' })} />
        <LinkRow label={t('settings.delete')} danger onClick={() => open({
          type: 'confirm', text: t('settings.deleteConfirm'),
          onYes: () => open({ type: 'confirm', text: t('settings.deleteConfirm2'), onYes: () => { deleteAccount(); close(); } }),
        })} />
        <p class="muted small center">{t('settings.version')} {APP_VERSION}</p>
      </section>

    </Modal>
  );
}

/** Champ de nom avec un dé qui propose un nom au hasard. */
function NameField({ value, onInput, error }: { value: string; onInput: (v: string) => void; error: string | null }) {
  return (
    <div class="name-field">
      <div class="row gap-s">
        <input id="player-name" value={value} maxLength={16} autoComplete="off"
          onInput={(e) => onInput((e.target as HTMLInputElement).value)} />
        <button class="dice bt bt-ardoise bt-l" aria-label={t('name.random')} onClick={() => onInput(randomName())}><Icon name="dice" size={40} /></button>
      </div>
      <span class={`muted small${error ? ' error' : ''}`}>{error ? t(error) : t('name.rule')}</span>
    </div>
  );
}

/** Premier lancement : le joueur choisit son nom. */
export function NameScreen() {
  const [name, setName] = useState(randomName());
  const [error, setError] = useState<string | null>(null);
  return (
    <div class="name-screen" style={{ backgroundImage: 'linear-gradient(180deg, #1a0e2a55, #1a0e2a99), url(art/ui-px/chargement.webp)' }}>
      <div class="name-card">
        <img src={heroImage(STARTER_HERO)} alt="" />
        <h1>{t('name.title')}</h1>
        <NameField value={name} onInput={(v) => { setName(v); setError(null); }} error={error} />
        <Btn kind="green" wide onClick={() => setError(chooseName(name))}>{t('ok')}</Btn>
      </div>
    </div>
  );
}

export function RenameModal() {
  const s = useGame();
  const [name, setName] = useState(s.name);
  const [error, setError] = useState<string | null>(null);
  return (
    <Modal title={t('settings.rename')}>
      <NameField value={name} onInput={(v) => { setName(v); setError(null); }} error={error} />
      <Btn kind="gold" wide disabled={s.wallet.gems < RENAME_COST} onClick={() => {
        const err = rename(name);
        if (err) setError(err);
        else { close(); toast('✓'); }
      }}>
        <Cur k="gems" n={RENAME_COST} />
      </Btn>
    </Modal>
  );
}

export function LegalModal({ doc }: { doc: LegalDoc | 'support' }) {
  const s = useGame();
  if (doc === 'support') {
    return (
      <Modal title={t('legal.support')}>
        <p>{t('legal.supportText')}</p>
        <div class="setting-row static"><span>{t('settings.id')}</span><b class="mono">{playerId(s)}</b></div>
        <p class="muted small">{t('legal.supportContact')}</p>
      </Modal>
    );
  }
  return (
    <Modal title={t(`legal.${doc}`)}>
      <article class="legal">
        {legalDoc(doc, s.lang).map((b) => ('h' in b ? <h3>{b.h}</h3> : <p>{b.p}</p>))}
      </article>
    </Modal>
  );
}

export function GainModal({ title, gain, damage, win }: { title: string; gain: Gain; damage?: number; win?: boolean }) {
  const empty = !Object.keys(gain.currencies).length && !gain.heroes.length && !gain.items.length && !gain.fragments;
  return (
    <Modal title={title}>
      {win !== undefined && <div class="result-stage">{win && <Halo size={164} />}<Art class={`result-art ${win ? 'win' : 'lose'}`} name={win ? 'trophy' : 'defeat'} /></div>}
      {win !== undefined && <div class={`result-title ${win ? 'win' : 'lose'}`}>{win ? t('result.victory') : t('result.defeat')}</div>}
      {damage !== undefined && <p class="center">{t('result.damage')} : <b class="gold-text">{damage.toLocaleString('fr-FR')}</b></p>}
      <div class="gain">
        {Object.entries(gain.currencies).map(([k, v]) => <Cur k={k} n={v ?? 0} big />)}
        {gain.fragments && <span class="cur cur-big">{heroDef(gain.fragments.defId).name} <Cur k="fragments" n={gain.fragments.amount} /></span>}
      </div>
      {gain.items.length > 0 && <div class="items-row">{gain.items.map((it) => <ItemIcon item={it} />)}</div>}
      {gain.heroes.length > 0 && <div class="grid">{gain.heroes.map((h) => <HeroCard hero={h} small />)}</div>}
      {empty && damage === undefined && win !== true && <p class="center muted">{t('result.nothing')}</p>}
      <Btn kind="green" wide onClick={close}>{t('ok')}</Btn>
    </Modal>
  );
}

export function AdModal({ onDone }: { onDone: () => void }) {
  const [left, setLeft] = useState(AD_SECONDS);
  useEffect(() => {
    if (left <= 0) {
      close();
      onDone();
      return;
    }
    const id = setTimeout(() => setLeft(left - 1), 1000);
    return () => clearTimeout(id);
  }, [left]);
  return (
    <div class="modal-back ad">
      <div class="ad-box">
        <span class="tag">{t('ad')}</span>
        <div class="ad-count">{left}</div>
      </div>
    </div>
  );
}

export function ConfirmModal({ text, onYes }: { text: string; onYes: () => void }) {
  return (
    <Modal title={text}>
      <div class="row gap">
        <Btn kind="green" wide onClick={() => { close(); onYes(); }}>{t('yes')}</Btn>
        <Btn kind="ghost" wide onClick={close}>{t('no')}</Btn>
      </div>
    </Modal>
  );
}
