// Réinitialiser un héros : tout est rendu, cela coûte RESET_COST gemmes.
import { describe, expect, it } from 'vitest';
import { RESET_COST } from '../src/core/data/modes';
import { HEROES } from '../src/core/data/heroes';
import { heroRefund, levelUp, resetHero, upgradeSlot } from '../src/game/state/actions';
import { getState, update } from '../src/game/state/store';

describe('réinitialiser un héros', () => {
  it("rend tout ce qui a été dépensé et revient au niveau 1", () => {
    update((s) => {
      s.heroes = [{ uid: 1, defId: HEROES[0]!.id, stars: 1, level: 1 }];
      s.formation = [[1, 2]];
      s.items = [{ uid: 9, slot: 'weapon', rarity: 1, tier: 0, heroUid: 1 }];
      s.slotLevels = {};
      s.wallet.gold = 1e9; s.wallet.essence = 1e9; s.wallet.dust = 1e6; s.wallet.gems = RESET_COST;
    });
    for (let i = 0; i < 10; i++) levelUp(1);
    upgradeSlot(1, 'weapon'); upgradeSlot(1, 'weapon');
    const before = { ...getState().wallet };
    const back = heroRefund(getState(), getState().heroes[0]!);
    expect(back.items).toBe(1);
    expect(resetHero(1)).not.toBeNull();
    const s = getState();
    expect(s.heroes[0]!.level).toBe(1);
    expect(s.items[0]!.heroUid).toBeUndefined();
    expect(s.wallet.gold).toBe(before.gold + back.gold);
    expect(s.wallet.dust).toBe(before.dust + back.dust);
    expect(s.wallet.gems).toBe(0);
    expect(s.wallet.gold).toBe(1e9); // tout l'or dépensé est revenu
    expect(s.wallet.dust).toBe(1e6);
  });

  it('refusé sans assez de gemmes', () => {
    update((s) => { s.heroes[0]!.level = 20; s.wallet.gems = RESET_COST - 1; });
    expect(resetHero(1)).toBeNull();
    expect(getState().heroes[0]!.level).toBe(20);
  });
});
