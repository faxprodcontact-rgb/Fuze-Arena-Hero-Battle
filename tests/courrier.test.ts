// Courrier : message de bienvenue avec cadeau, récupéré une seule fois.
import { describe, expect, it } from 'vitest';
import { checkMail, claimMail, mailbox, mailWaiting, readMail } from '../src/game/state/actions';

describe('courrier', () => {
  it('le message de bienvenue arrive, se lit et son cadeau se prend une fois', () => {
    checkMail();
    const box = mailbox();
    const welcome = box.find((m) => m.def.id === 'welcome')!;
    expect(welcome).toBeTruthy();
    expect(mailWaiting()).toBeGreaterThan(0);
    readMail('welcome');
    const gain = claimMail('welcome');
    expect(gain.currencies.gems).toBe(welcome.def.reward!.gems);
    expect(claimMail('welcome').currencies.gems).toBeUndefined();
  });
});
