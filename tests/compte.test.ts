// Le compte lié (Google / Apple) : invité par défaut, la liaison garde la partie, une vieille sauvegarde reste invitée.
import { describe, expect, it } from 'vitest';
import { AUTH_READY, linkAccount, signIn } from '../src/game/auth';
import { linkAuth, unlinkAuth } from '../src/game/state/actions';
import { fresh, getState, restore, update } from '../src/game/state/store';
import type { PlayerState } from '../src/game/state/types';

describe('compte lié', () => {
  it('une nouvelle partie est invitée', () => {
    expect(fresh().auth).toBeUndefined();
  });
  it('lier garde la partie, délier la laisse sur le téléphone', () => {
    update((s) => void (s.wallet.gold = 1234));
    expect(linkAuth({ provider: 'apple', id: 'u-1', email: 'a@b.c' })).toBe(true);
    expect(getState().auth).toMatchObject({ provider: 'apple', id: 'u-1', email: 'a@b.c' });
    expect(getState().wallet.gold).toBe(1234);
    unlinkAuth();
    expect(getState().auth).toBeUndefined();
    expect(getState().wallet.gold).toBe(1234);
  });
  it('refuse un fournisseur inconnu ou un id vide', () => {
    expect(linkAuth({ provider: 'facebook' as never, id: 'x' })).toBe(false);
    expect(linkAuth({ provider: 'google', id: '' })).toBe(false);
    expect(getState().auth).toBeUndefined();
  });
  it('vieille sauvegarde : invitée ; compte abîmé : oublié', () => {
    const old = structuredClone(fresh()) as PlayerState;
    expect(restore(old).auth).toBeUndefined();
    expect(restore({ ...old, auth: { provider: 'google', id: 'g', at: 1 } }).auth?.provider).toBe('google');
    expect(restore({ ...old, auth: { provider: 'x' as never, id: 'g', at: 1 } }).auth).toBeUndefined();
  });
  it.skipIf(AUTH_READY)('connexion pas branchée : réponse « not-configured »', async () => {
    expect(await signIn('google')).toEqual({ ok: false, reason: 'not-configured' });
    expect(await linkAccount('apple')).toEqual({ ok: false, reason: 'not-configured' });
  });
});
