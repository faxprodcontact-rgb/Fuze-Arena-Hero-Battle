// Cristaux d'éveil de la campagne : 5 par jour dans le butin, à partir du niveau 900.
import { describe, expect, it } from 'vitest';
import { REWARDS } from '../src/core/data/economy';
import { collectIdle } from '../src/game/state/actions';
import { update } from '../src/game/state/store';

describe('cristaux de campagne', () => {
  it('rien avant le niveau prévu', () => {
    update((s) => { s.campaign.cleared = REWARDS.crystalsFromStage - 1; s.campaign.idleFrom = Date.now() + s.timeShift - 12 * 3.6e6; });
    expect(collectIdle().currencies.crystals).toBeUndefined();
  });

  it('5 par jour ensuite, sans rien perdre entre deux collectes', () => {
    let total = 0;
    update((s) => { s.campaign.cleared = REWARDS.crystalsFromStage; s.campaign.crystalHours = 0; });
    for (let i = 0; i < 24; i++) {
      update((s) => { s.campaign.idleFrom = Date.now() + s.timeShift - 3.6e6; }); // 1 h de butin
      total += collectIdle().currencies.crystals ?? 0;
    }
    expect(total).toBeGreaterThanOrEqual(REWARDS.crystalsPerDay - 1);
    expect(total).toBeLessThanOrEqual(REWARDS.crystalsPerDay);
  });
});
