// Amis : code ami, cadeaux une fois par jour, pas soi-même ni deux fois le même.
import { describe, expect, it } from 'vitest';
import { FRIEND_GIFT } from '../src/core/data/modes';
import { addFriend, claimGifts, friendPlan, friendSuggestions, playerId, sendGift } from '../src/game/state/actions';
import { getState, update } from '../src/game/state/store';

describe('amis', () => {
  it('ajouter par code', () => {
    const code = friendSuggestions()[0]!.code;
    expect(addFriend(code)).toBe('added');
    expect(addFriend(code.toLowerCase())).toBe('already');
    expect(addFriend(playerId(getState()))).toBe('self');
    expect(addFriend('ab')).toBe('invalid');
    // Même code = même ami (avec le serveur, ce sera le même joueur).
    const f = getState().friends.list[0]!;
    expect(f.code).toBe(code);
    expect(friendPlan(f.id)).not.toBeNull();
  });

  it('un cadeau par ami et par jour ; ouvrir les cadeaux reçus', () => {
    expect(sendGift()).toBe(1);
    expect(sendGift()).toBe(0);
    update((s) => void (s.friends.inbox = s.friends.list.map((f) => f.id)));
    const before = getState().wallet.basicScrolls;
    const gain = claimGifts();
    expect(gain.currencies.basicScrolls).toBe(FRIEND_GIFT.basicScrolls);
    expect(getState().wallet.basicScrolls).toBe(before + FRIEND_GIFT.basicScrolls);
    expect(claimGifts().currencies.basicScrolls).toBeUndefined();
  });
});
