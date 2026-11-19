// Fusion avec les héros choisis par le joueur (et refus d'un mauvais choix).
import { describe, expect, it } from 'vitest';
import { HEROES } from '../src/core/data/heroes';
import { autoPicks, fuse, fusionNeeds } from '../src/game/state/actions';
import { getState, update } from '../src/game/state/store';

describe('fusion : héros choisis', () => {
  const epic = HEROES.find((h) => h.rarity === 'epic')!;
  const sameFaction = HEROES.filter((h) => h.element === epic.element && h.rarity === 'rare');
  const otherFaction = HEROES.find((h) => h.element !== epic.element && h.rarity === 'rare')!;

  function setup() {
    update((s) => {
      s.heroes = [
        { uid: 1, defId: epic.id, stars: 3, level: 1 }, // cible
        { uid: 2, defId: epic.id, stars: 3, level: 1 }, // copie
        { uid: 3, defId: sameFaction[0]!.id, stars: 3, level: 1 },
        { uid: 4, defId: sameFaction[1]!.id, stars: 3, level: 1 },
        { uid: 5, defId: sameFaction[2]!.id, stars: 3, level: 1 },
        { uid: 6, defId: otherFaction.id, stars: 3, level: 1 },
      ];
      s.formation = [[1, 2]];
    });
  }

  it('utilise exactement les héros choisis', () => {
    setup();
    expect(autoPicks(1).fodder).toHaveLength(2);
    const needs = fusionNeeds(1, { identical: [], copy: [2], fodder: [3, 5] })!;
    expect(needs.ready).toBe(true);
    expect(fuse(1, needs.consumed)).not.toBeNull();
    const left = getState().heroes.map((h) => h.uid).sort();
    expect(left).toEqual([1, 4, 6]);
    expect(getState().heroes.find((h) => h.uid === 1)!.stars).toBe(4);
  });

  it("refuse un héros d'un autre élément", () => {
    setup();
    expect(fusionNeeds(1, { identical: [], copy: [2], fodder: [3, 6] })!.ready).toBe(false);
    expect(fuse(1, [2, 3, 6])).toBeNull();
    expect(getState().heroes).toHaveLength(6);
  });
});
