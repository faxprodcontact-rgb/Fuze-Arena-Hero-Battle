// Amis : mon code à partager, ajouter un ami par son code, cadeaux quotidiens (envoyer / ouvrir), défier en automatique.
import { useState } from 'preact/hooks';
import { FRIEND_GIFT, FRIENDS_MAX } from '../../../core/data/modes';
import { heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import {
  addFriend, claimGifts, friendPlan, friendPower, friendSuggestions, playerId, removeFriend, sendGift,
} from '../../state/actions';
import { teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import type { Friend } from '../../state/types';
import { Btn, Cur, Icon, Page, Sign } from '../kit';
import { open, prepare, toast } from '../nav';

function FriendRow({ f, mine, sent, waiting, onAdd }: { f: Friend; mine: number; sent?: boolean; waiting?: boolean; onAdd?: () => void }) {
  const power = friendPower(f);
  const leader = f.team.find((m) => m.slot === 2) ?? f.team[0]!;
  return (
    <div class="card friend">
      <img class="friend-face" src={heroImage(leader.defId)} alt="" />
      <div class="grow">
        <strong>{f.name}</strong>
        <div class="row gap-s center-y">
          <span class={`power-chip ${mine >= power ? 'ok' : 'low'}`}><Icon name="power" size={14} />{fmt(power)}</span>
          <span class="muted small">{f.code}</span>
        </div>
      </div>
      {onAdd ? (
        <Btn kind="green" small onClick={onAdd}>+</Btn>
      ) : (
        <>
          <button class={`gift-btn bt bt-galet bt-m${sent ? ' done' : ''}${waiting ? ' waiting' : ''}`} disabled={sent} onClick={() => sendGift(f.id)} aria-label="gift">
            <Icon name="gift" size={22} />
          </button>
          <Btn kind="red" small onClick={() => { const p = friendPlan(f.id); if (p) prepare(p); }}>{t('friends.challenge')}</Btn>
          <button class="friend-x" onClick={() => open({ type: 'confirm', text: t('friends.remove'), onYes: () => removeFriend(f.id) })} aria-label="✕"><Sign name="cross" /></button>
        </>
      )}
    </div>
  );
}

export function FriendsPage() {
  const s = useGame();
  const [code, setCode] = useState('');
  const mine = teamPower(s);
  const me = playerId(s);
  const inbox = s.friends.inbox.filter((id) => s.friends.list.some((f) => f.id === id));
  const unsent = s.friends.list.filter((f) => !s.friends.sent.includes(f.id)).length;
  const add = (c: string) => {
    const r = addFriend(c);
    toast(t(`friends.${r}`));
    if (r === 'added') setCode('');
  };

  return (
    <Page title={`${t('friends.title')} ${s.friends.list.length} / ${FRIENDS_MAX}`}>
      <section class="card friend-code">
        <div class="row between center-y">
          <span class="muted">{t('friends.code')}</span>
          <button class="code-chip" onClick={() => {
            void navigator.clipboard?.writeText(me).catch(() => {});
            toast(t('friends.copied'));
          }}>{me} <Icon name="copy" size={24} /></button>
        </div>
        <div class="row gap-s">
          <input class="input grow" maxLength={6} placeholder={t('friends.placeholder')} value={code}
            onInput={(e) => setCode((e.currentTarget as HTMLInputElement).value.toUpperCase())} />
          <Btn kind="green" small disabled={code.length !== 6} onClick={() => add(code)}>{t('friends.add')}</Btn>
        </div>
      </section>

      {s.friends.list.length > 0 && (
        <div class="row gap-s">
          <Btn kind="gold" small wide disabled={!inbox.length} onClick={() => {
            const gain = claimGifts();
            open({ type: 'gain', title: t('friends.title'), gain });
          }}>
            <Icon name="gift" size={18} /> {t('friends.claim')} {inbox.length > 0 && <Cur k="basicScrolls" n={inbox.length * FRIEND_GIFT.basicScrolls} />}
          </Btn>
          <Btn kind="blue" small wide disabled={!unsent} onClick={() => sendGift()}>{t('friends.sendAll')} · {unsent}</Btn>
        </div>
      )}

      <section class="list">
        {s.friends.list.map((f) => (
          <FriendRow f={f} mine={mine} sent={s.friends.sent.includes(f.id)} waiting={inbox.includes(f.id)} />
        ))}
      </section>

      {s.friends.list.length < 5 && (
        <section class="list">
          <strong class="muted">{t('friends.suggest')}</strong>
          {friendSuggestions(s).map((f) => <FriendRow f={f} mine={mine} onAdd={() => add(f.code)} />)}
        </section>
      )}
    </Page>
  );
}
