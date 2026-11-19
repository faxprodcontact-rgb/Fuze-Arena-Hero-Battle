// Courrier : les messages de l'équipe, avec leur cadeau éventuel. Toucher un message l'ouvre (et le marque lu).
import { useState } from 'preact/hooks';
import { t } from '../../i18n';
import { claimMail, mailbox, readMail, type MailItem } from '../../state/actions';
import { useGame } from '../../state/store';
import { Btn, Cur, Icon, Page } from '../kit';
import { open } from '../nav';

function Rewards({ m }: { m: MailItem }) {
  if (!m.def.reward) return null;
  return <span class={`row gap-s center-y${m.claimed ? ' claimed' : ''}`}>{Object.entries(m.def.reward).map(([k, v]) => <Cur k={k} n={v ?? 0} />)}</span>;
}

export function MailPage() {
  const s = useGame();
  const list = mailbox(s);
  const [openId, setOpenId] = useState<string | undefined>(undefined);
  const lang = s.lang;
  const date = (ms: number) => new Date(ms).toLocaleDateString(lang === 'fr' ? 'fr-FR' : 'en-GB', { day: 'numeric', month: 'short' });
  const toClaim = list.some((m) => m.def.reward && !m.claimed);
  const take = (id?: string) => {
    const gain = claimMail(id);
    if (Object.keys(gain.currencies).length) open({ type: 'gain', title: t('mail.title'), gain });
  };

  return (
    <Page title={t('mail.title')}>
      {list.length === 0 && <p class="center muted">∅</p>}
      <section class="list">
        {list.map((m) => {
          const isOpen = openId === m.def.id;
          return (
            <div class={`card mail${m.read ? '' : ' unread'}${isOpen ? ' open' : ''}`}>
              <button class="mail-head" onClick={() => {
                setOpenId(isOpen ? undefined : m.def.id);
                readMail(m.def.id);
              }}>
                <span class="row gap-s center-y"><Icon name="mail" size={22} /><strong>{m.def.title[lang]}</strong></span>
                <span class="muted small">{date(m.at)}</span>
              </button>
              {isOpen && <p class="mail-body">{m.def.body[lang]}</p>}
              {m.def.reward && (
                <div class="row between center-y">
                  <Rewards m={m} />
                  {m.claimed ? <span class="muted small">✓</span> : isOpen && <Btn kind="gold" small onClick={() => take(m.def.id)}>{t('claim')}</Btn>}
                </div>
              )}
            </div>
          );
        })}
      </section>
      {toClaim && <Btn kind="gold" wide onClick={() => take()}>{t('mail.claimAll')}</Btn>}
    </Page>
  );
}
