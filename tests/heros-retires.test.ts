// Vieilles sauvegardes : les héros retirés du jeu sont échangés contre un dédommagement par courrier.
import { describe, expect, it } from 'vitest';
import { HEROES, RETIRED_HEROES, STARTER_HERO, isHero } from '../src/core/data/heroes';
import { checkMail, claimMail, mailbox } from '../src/game/state/actions';
import { RETIRED_MAIL, copiesFor } from '../src/game/state/migrate';
import { fresh, getState, replaceState, restore } from '../src/game/state/store';
import type { PlayerState } from '../src/game/state/types';

/** Une sauvegarde d'avant : un Légendaire retiré ★7 en section (niveau 80, une arme portée), un Commun retiré, un héros gardé. */
function oldSave(): PlayerState {
  const s = fresh(Date.now() - 90 * 864e5);
  s.heroes = [
    { uid: 1, defId: STARTER_HERO, stars: 4, level: 50 },
    { uid: 2, defId: 'assassins-4', stars: 7, level: 80 },
    { uid: 3, defId: 'knights-2', stars: 2, level: 10 },
  ];
  s.formation = [[1, 2], [2, 0], [3, 3]];
  s.defenseTeam = [[2, 1]];
  s.items = [{ uid: 9, slot: 'weapon', rarity: 2, tier: 1, heroUid: 2 }];
  s.slotLevels = { 2: { weapon: 2 } };
  s.discovered = [STARTER_HERO, 'assassins-4', 'knights-2'];
  s.fragments = { 'assassins-4': 25 };
  s.fragmentTarget = 'assassins-4';
  s.arena.opponents = [{ id: 'o', name: 'X', points: 1000, team: [{ defId: 'mages-1', stars: 1, level: 3, slot: 0 }] }];
  s.mail = { got: { welcome: s.createdAt }, read: ['welcome'], claimed: ['welcome'] };
  return JSON.parse(JSON.stringify(s)) as PlayerState;
}

describe('héros retirés (36 héros HD)', () => {
  it('les héros retirés existent bien, aucun n’est encore dans le jeu', () => {
    expect(RETIRED_HEROES.size).toBe(36);
    expect(HEROES.some((h) => RETIRED_HEROES.has(h.id))).toBe(false);
  });

  it('une vieille sauvegarde est nettoyée sans rien perdre', () => {
    const s = restore(oldSave());
    expect(s.heroes.map((h) => h.uid)).toEqual([1]);
    expect(s.formation).toEqual([[1, 2]]);
    expect(s.defenseTeam).toEqual([]);
    expect(s.discovered).toEqual([STARTER_HERO]);
    expect(s.items[0]!.heroUid).toBeUndefined();
    expect(s.slotLevels[2]).toBeUndefined();
    expect(s.fragments['assassins-4']).toBeUndefined();
    expect(s.fragmentTarget).toBeUndefined();
    expect(s.arena.opponents[0]!.team.every((m) => isHero(m.defId))).toBe(true);
    const gift = s.mail!.personal![RETIRED_MAIL]!;
    // Légendaire ★7 = 4 copies (★4, puis une à ★5, ★6, ★7) × 20, + 25 fragments = 10 ; Commun ★2 = 3 copies × 1
    expect(copiesFor('legendary', 7)).toBe(4);
    expect(gift.scrolls).toBe(90);
    expect(gift.basicScrolls).toBe(3);
    expect(gift.gold).toBeGreaterThan(0);
    expect(gift.dust).toBeGreaterThan(0);
  });

  it('le cadeau arrive par courrier, une seule fois', () => {
    replaceState(restore(oldSave()));
    checkMail();
    const m = mailbox().find((x) => x.def.id === RETIRED_MAIL)!;
    expect(m.def.reward?.scrolls).toBe(90);
    const before = getState().wallet.scrolls;
    claimMail(RETIRED_MAIL);
    expect(getState().wallet.scrolls).toBe(before + 90);
    claimMail(RETIRED_MAIL);
    expect(getState().wallet.scrolls).toBe(before + 90);
    // une sauvegarde déjà propre ne reçoit rien de plus
    const again = restore(JSON.parse(JSON.stringify(getState())) as PlayerState);
    expect(again.mail!.claimed).toContain(RETIRED_MAIL);
    expect(again.heroes).toHaveLength(1);
  });

  it('une partie neuve ne reçoit pas ce message', () => {
    replaceState(fresh());
    checkMail();
    expect(mailbox().some((x) => x.def.id === RETIRED_MAIL)).toBe(false);
  });
});
