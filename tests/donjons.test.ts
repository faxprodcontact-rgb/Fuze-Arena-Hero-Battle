// Donjons : 3 essais par jour, balayage du dernier niveau gagné, combat obligatoire pour avancer.
import { describe, expect, it } from 'vitest';
import { DUNGEON_ATTEMPTS_PER_DAY } from '../src/core/data/modes';
import { dungeonPlan, dungeonRewardPreview, finishBattle, sweepDungeon } from '../src/game/state/actions';
import { getState, update } from '../src/game/state/store';

describe('donjons', () => {
  it('pas de balayage tant qu\'aucun niveau n\'est gagné', () => {
    update((s) => { s.dungeons.gold = 0; s.daily.entries.gold = 0; });
    expect(sweepDungeon('gold')).toBeNull();
    expect(dungeonPlan('gold')!.title).toBe('1');
  });

  it('gagner le niveau suivant avance d\'un niveau et compte un essai', () => {
    const plan = dungeonPlan('gold')!;
    const req = plan.build();
    finishBattle(req, { win: true, damage: 0 } as never);
    expect(getState().dungeons.gold).toBe(1);
    expect(getState().daily.entries.gold).toBe(1);
    // Une défaite ne coûte rien.
    finishBattle(dungeonPlan('gold')!.build(), { win: false, damage: 0 } as never);
    expect(getState().dungeons.gold).toBe(1);
    expect(getState().daily.entries.gold).toBe(1);
  });

  it('le balayage rend la récompense du dernier niveau gagné, dans la limite des essais', () => {
    const before = getState().wallet.gold;
    const gain = sweepDungeon('gold')!;
    expect(gain.currencies.gold).toBe(dungeonRewardPreview('gold', 1).gold);
    expect(getState().wallet.gold).toBe(before + gain.currencies.gold!);
    for (let i = 2; i < DUNGEON_ATTEMPTS_PER_DAY; i++) expect(sweepDungeon('gold')).not.toBeNull();
    expect(sweepDungeon('gold')).toBeNull();
    expect(getState().dungeons.gold).toBe(1);
  });
});
