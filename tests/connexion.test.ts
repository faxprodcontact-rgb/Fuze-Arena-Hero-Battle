// Calendrier de connexion : une case par jour, 7 jours de bienvenue (Légendaire le 7e), puis 28 jours.
import { describe, expect, it } from 'vitest';
import { LOGIN_MONTH, LOGIN_WELCOME } from '../src/core/data/modes';
import { claimLogin, loginCalendar } from '../src/game/state/actions';
import { getState, update } from '../src/game/state/store';

const nextDay = () => update((s) => void (s.timeShift += 24 * 3.6e6));

describe('calendrier de connexion', () => {
  it('une seule case par jour', () => {
    expect(loginCalendar().index).toBe(0);
    expect(claimLogin()).not.toBeNull();
    expect(claimLogin()).toBeNull();
    expect(loginCalendar().claimed).toBe(true);
  });

  it('7e jour : un Légendaire ; ensuite le calendrier du mois', () => {
    for (let d = 1; d < LOGIN_WELCOME.length - 1; d++) { nextDay(); claimLogin(); }
    nextDay();
    const gain = claimLogin()!;
    expect(gain.heroes.length).toBe(1);
    expect(gain.heroes[0]!.defId).toMatch(/./);
    nextDay();
    const cal = loginCalendar();
    expect(cal.kind).toBe('month');
    expect(cal.index).toBe(0);
    expect(cal.rewards.length).toBe(LOGIN_MONTH.length);
    expect(getState().login?.count).toBe(LOGIN_WELCOME.length);
  });
});
