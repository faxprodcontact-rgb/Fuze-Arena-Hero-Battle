// Calendrier de connexion : une case cochée par jour de connexion. Bienvenue (7 jours), puis 28 jours qui recommencent.
import { t } from '../../i18n';
import { claimLogin, loginCalendar } from '../../state/actions';
import { useGame } from '../../state/store';
import { Btn, Cur, Icon, Modal, Sign } from '../kit';
import { close, open } from '../nav';

export function LoginModal() {
  const s = useGame();
  const cal = loginCalendar(s);
  return (
    <Modal title={t(cal.kind === 'welcome' ? 'login.welcome' : 'login.title')} wide center>
      <div class={`login-grid ${cal.kind}`}>
        {cal.rewards.map((r, i) => {
          const done = i < cal.index || (i === cal.index && cal.claimed);
          const today = i === cal.index && !cal.claimed;
          const big = cal.kind === 'welcome' ? i === 6 : i % 7 === 6;
          return (
            <div class={`login-day${done ? ' done' : ''}${today ? ' today' : ''}${big ? ' big' : ''}`}>
              <span class="login-n">{i + 1}</span>
              <div class="login-reward">
                {r.legendary ? <span class="login-legend"><Icon name="star" size={32} /></span> : Object.entries(r).map(([k, v]) => <Cur k={k} n={v ?? 0} />)}
              </div>
              {done && <span class="login-check"><Sign name="check" k={3} /></span>}
            </div>
          );
        })}
      </div>
      <Btn kind="gold" wide disabled={cal.claimed} onClick={() => {
        const gain = claimLogin();
        close();
        if (gain) open({ type: 'gain', title: t('login.title'), gain });
      }}><Icon name="calendar" size={20} /> {t('claim')}</Btn>
    </Modal>
  );
}
