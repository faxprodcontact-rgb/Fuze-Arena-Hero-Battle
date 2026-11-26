// Le portrait du joueur : seulement un héros découvert ; sans choix (ou choix disparu), le visage du chef de section.
import { describe, expect, it } from 'vitest';
import { HEROES } from '../src/core/data/heroes';
import { setAvatar } from '../src/game/state/actions';
import { retireHeroes } from '../src/game/state/migrate';
import { avatarOf } from '../src/game/state/selectors';
import { getState, update } from '../src/game/state/store';

describe('portrait du joueur', () => {
  const [a, b, c] = HEROES.slice(0, 3).map((h) => h.id) as [string, string, string];
  it('suit le premier héros de la section tant que rien n’est choisi', () => {
    update((s) => {
      s.heroes = [{ uid: 1, defId: a, stars: 1, level: 1 }, { uid: 2, defId: b, stars: 1, level: 1 }];
      s.formation = [[2, 2], [1, 0]];
      s.discovered = [a, b, c];
      delete s.avatar;
    });
    expect(avatarOf(getState())).toBe(b);
  });
  it('prend un héros découvert, refuse un inconnu', () => {
    expect(setAvatar(c)).toBe(true);
    expect(avatarOf(getState())).toBe(c);
    expect(setAvatar('pas-un-heros')).toBe(false);
    expect(getState().avatar).toBe(c);
  });
  it('un portrait d’un héros retiré du jeu est oublié', () => {
    const s = retireHeroes({ ...structuredClone(getState()), avatar: 'heros-retire' });
    expect(s.avatar).toBeUndefined();
    expect(avatarOf(s)).toBe(b);
  });
});
