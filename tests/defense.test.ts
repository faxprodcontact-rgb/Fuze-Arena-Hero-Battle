// Mode Défense : partie rejouable à l'identique, étoiles selon les vies, récompenses une seule fois par étoile.
import { describe, expect, it } from 'vitest';
import { DefenseBattle } from '../src/core/defense/engine';
import { DEFENSE_HEROES, DEFENSE_LIVES, DEFENSE_REWARD, defenseCrystals, defenseStars } from '../src/core/data/defense';
import { autoDefense, defenseRequest, finishDefense, placeDefender } from '../src/game/state/actions';
import { getState } from '../src/game/state/store';

describe('défense', () => {
  it('même placement + même graine = même partie', () => {
    autoDefense();
    const req = defenseRequest(1)!;
    const a = DefenseBattle.run(req.setup);
    const b = DefenseBattle.run(req.setup);
    expect(a.lives).toBe(b.lives);
    expect(a.tick).toBe(b.tick);
    expect(a.over).toBe(true);
  });

  it('étoiles selon les vies', () => {
    expect(defenseStars(DEFENSE_LIVES)).toBe(3);
    expect(defenseStars(DEFENSE_LIVES / 2)).toBe(2);
    expect(defenseStars(1)).toBe(1);
    expect(defenseStars(0)).toBe(0);
  });

  it('victoire : niveau suivant ouvert, cristaux à la première victoire, coffres d\'étoiles', () => {
    const req = defenseRequest(1)!;
    const g1 = finishDefense(req, DEFENSE_LIVES / 2); // 2 étoiles
    expect(getState().defense.level).toBe(1);
    expect(g1.currencies.crystals).toBe(defenseCrystals(1));
    const g2 = finishDefense(defenseRequest(1)!, DEFENSE_LIVES); // rejouer : seulement les étoiles en plus
    expect(g2.currencies.gold).toBeUndefined();
    expect(getState().defense.stars[1]).toBe(3);
    expect(defenseRequest(3)).toBeNull(); // on ne saute pas de niveau
    expect(finishDefense(defenseRequest(2)!, 0).currencies.gold).toBeUndefined(); // défaite : rien
    // 15 étoiles = un coffre (niveaux 2 à 5 en 3 étoiles : 3 + 12 = 15)
    let chest = 0;
    for (let l = 2; l <= 5; l++) chest += finishDefense(defenseRequest(l)!, DEFENSE_LIVES).currencies.scrolls ?? 0;
    expect(chest).toBe(DEFENSE_REWARD.chest.scrolls);
    expect(getState().defense.chests).toBe(1);
  });

  it('5 héros au plus sur la carte', () => {
    const s = getState();
    for (const h of s.heroes) for (let pad = 0; pad < 9; pad++) placeDefender(h.uid, pad);
    expect(getState().defense.placement.length).toBeLessThanOrEqual(DEFENSE_HEROES);
  });
});
