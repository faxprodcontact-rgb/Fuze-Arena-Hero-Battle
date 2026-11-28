// Le héros joker (29/11) : gagné au 20e niveau d'une zone d'Événement, une fois par événement ; il ne combat pas.
import { describe, expect, it } from 'vitest';
import { EVENT_LEVELS } from '../src/core/data/event';
import { heroDef, isJoker } from '../src/core/data/heroes';
import { autoFormation, claimJoker, eventOf, finishBattle, jokerPending, summon } from '../src/game/state/actions';
import { getState, update } from '../src/game/state/store';

if (!getState().heroes.length) summon('normal', 1);

function winLevel20() {
  update((s) => {
    const uid = s.heroes[0]!.uid;
    s.event = { ...eventOf(s), run: { team: [[uid, 2]], level: EVENT_LEVELS, hp: { [uid]: 1 }, atk: 0, def: 0 } };
  });
  finishBattle({ kind: 'event', title: '1-20', heroes: [], waves: [], seed: 1 }, { win: true, damage: 0, inputs: [], heroHp: {} });
}

describe('héros joker', () => {
  it('la première zone finie de l’événement le donne, la suivante non', () => {
    expect(jokerPending()).toBe(false);
    winLevel20();
    expect(jokerPending()).toBe(true);
    const hero = claimJoker('water')!;
    expect(isJoker(hero.defId)).toBe(true);
    expect(heroDef(hero.defId).element).toBe('water');
    expect(hero.stars).toBe(5);
    expect(jokerPending()).toBe(false);
    winLevel20();
    expect(jokerPending()).toBe(false);
  });

  it('il n’entre jamais dans la section', () => {
    autoFormation();
    const s = getState();
    expect(s.formation.some(([u]) => isJoker(s.heroes.find((h) => h.uid === u)!.defId))).toBe(false);
  });
});
