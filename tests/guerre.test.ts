// Guerre de guildes : semaine (préparation, combats, résultats), 2 attaques par jour, un héros = une attaque par jour.
import { describe, expect, it } from 'vitest';
import { GUILD_WAR } from '../src/core/data/modes';
import {
  claimWar, ensureWar, finishBattle, joinGuild, warAttacksLeft, warPhase, warPlan, warScores, warStars, BOT_GUILDS,
} from '../src/game/state/actions';
import { getState, now, update } from '../src/game/state/store';

/** Place l'heure du jeu sur le prochain jour de la semaine voulu (0 = dimanche … 6 = samedi), à midi. */
function goTo(weekday: number) {
  update((s) => {
    const d = new Date(now());
    d.setHours(12, 0, 0, 0);
    while (d.getDay() !== weekday) d.setDate(d.getDate() + 1);
    s.timeShift += d.getTime() - now();
  });
}

describe('guerre de guildes', () => {
  it('le rythme de la semaine', () => {
    goTo(1);
    expect(warPhase()).toBe('prep');
    goTo(3);
    expect(warPhase()).toBe('battle');
    goTo(0);
    expect(warPhase()).toBe('results');
  });

  it('étoiles selon les héros debout', () => {
    expect(warStars(false, 1)).toBe(0);
    expect(warStars(true, 1)).toBe(3);
    expect(warStars(true, 0.6)).toBe(2);
    expect(warStars(true, 0.2)).toBe(1);
  });

  it('2 attaques par jour ; un héros déjà utilisé reste sur le côté', () => {
    joinGuild(BOT_GUILDS[0]!);
    goTo(3);
    const w = ensureWar()!;
    expect(warAttacksLeft(w)).toBe(GUILD_WAR.attacksPerDay);
    const req = warPlan(0)!.build()!;
    finishBattle(req, { win: true, damage: 0, alive: 1, inputs: [] });
    const war = getState().guildWar!;
    expect(war.myStars).toBe(3);
    expect(war.used.length).toBe(req.heroes.length);
    // Le seul héros de la section a déjà attaqué : pas de deuxième attaque avec lui aujourd'hui.
    expect(warPlan(1)!.exclude).toEqual(war.used);
    expect(warPlan(1)!.build()).toBeNull();
    expect(warScores(getState(), war).members.some((m) => m.me && m.stars === 3)).toBe(true);
  });

  it('le dimanche : récompense une seule fois (pièces de guilde + parchemins)', () => {
    goTo(0);
    const gain = claimWar()!;
    expect(gain.currencies.guildCoins).toBeGreaterThan(0);
    expect(gain.currencies.scrolls).toBeGreaterThan(0);
    expect(claimWar()).toBeNull();
  });
});

describe('section de défense', () => {
  it('par défaut la même que la section ; modifiable sans toucher à la section', async () => {
    const { formationOf } = await import('../src/game/state/selectors');
    const { autoFormation } = await import('../src/game/state/actions');
    const s0 = getState();
    expect(formationOf(s0, 'defense')).toEqual(s0.formation);
    const before = JSON.stringify(s0.formation);
    autoFormation([], 'defense');
    expect(JSON.stringify(getState().formation)).toBe(before);
    expect(getState().defenseTeam?.length).toBeGreaterThan(0);
  });
});
