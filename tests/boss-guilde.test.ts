// Boss de guilde (26/11/2026) : 4 boss (avec l'oiseau-tempête), un par jour, jamais le même que le boss du jour.
import { describe, expect, it } from 'vitest';
import { BOSS_ELEMENT, GUILD_BOSSES, monsterDef } from '../src/core/data/monsters';
import { dailyBossId, guildBossId } from '../src/game/state/actions';
import { bossArt } from '../src/game/look';

describe('boss de guilde', () => {
  it('jamais le même que le boss du jour, et les 4 passent en un mois', () => {
    const seen = new Set<string>();
    for (let i = 0; i < 60; i++) {
      const at = new Date(2026, 10, 1 + i, 12).getTime();
      expect(guildBossId(at)).not.toBe(dailyBossId(at));
      seen.add(guildBossId(at));
    }
    expect([...seen].sort()).toEqual([...GUILD_BOSSES].sort());
  });

  it("l'oiseau-tempête est un boss du vent, joué par le grand boss du vent", () => {
    expect(monsterDef('storm').boss).toBe(true);
    expect(BOSS_ELEMENT.storm).toBe('wind');
    expect(bossArt('storm')).toBe('boss-vent');
  });
});
