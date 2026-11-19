// Mode Défense : partie rejouable à l'identique, étoiles selon les vies, récompenses une seule fois par étoile.
import { describe, expect, it } from 'vitest';
import { DefenseBattle } from '../src/core/defense/engine';
import { DEFENSE_LIVES, defenseStars } from '../src/core/data/defense';
import { autoDefense, defenseRequest, finishDefense } from '../src/game/state/actions';
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

  it('victoire : niveau suivant ouvert, gemmes seulement pour les nouvelles étoiles', () => {
    const req = defenseRequest(1)!;
    const g1 = finishDefense(req, DEFENSE_LIVES / 2); // 2 étoiles
    expect(getState().defense.level).toBe(1);
    expect(g1.currencies.gems).toBe(40);
    const g2 = finishDefense(defenseRequest(1)!, DEFENSE_LIVES); // 3 étoiles : +1 étoile
    expect(g2.currencies.gems).toBe(20);
    expect(g2.currencies.gold).toBeUndefined();
    const g3 = finishDefense(defenseRequest(1)!, DEFENSE_LIVES);
    expect(g3.currencies.gems).toBeUndefined();
    expect(defenseRequest(3)).toBeNull(); // on ne saute pas de niveau
    expect(finishDefense(defenseRequest(2)!, 0).currencies.gold).toBeUndefined(); // défaite : rien
  });
});
