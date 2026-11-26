// Colisée : duels en chaîne (le gagnant reste), points, ligues, récompenses, semaine et combats du jour.
import { describe, expect, it } from 'vitest';
import { heroToUnit } from '../src/core/battle/units';
import {
  DuelChain, botPoints, botTeam, foePower, leagueAfter, makeGroup, pointsChange, rankReward, runColiseum, standings,
  type ColiseumSetup, type DuelEvent,
} from '../src/core/coliseum';
import { COLISEUM, COLISEUM_LEAGUES } from '../src/core/data/coliseum';
import { HERO_IDS } from '../src/core/data/heroes';
import {
  buyColiseumFight, claimColiseumWeek, coliseumFightsLeft, coliseumTeam, ensureDay, findColiseumFoe, finishColiseum,
} from '../src/game/state/actions';
import { getState, now, update } from '../src/game/state/store';

const ids = HERO_IDS as readonly string[];
const unit = (defId: string, level: number, n: number, side: 'hero' | 'enemy') => ({
  ...heroToUnit({ uid: n, defId, stars: 4, level }, 0),
  id: side === 'hero' ? `h-${n}` : `e-0-${n}`,
  side,
});

function setup(heroLevels: number[], foeLevels: number[], seed = 42): ColiseumSetup {
  return {
    heroes: heroLevels.map((l, i) => unit(ids[i]!, l, i + 1, 'hero')),
    foes: foeLevels.map((l, i) => unit(ids[10 + i]!, l, i, 'enemy')),
    seed,
  };
}

describe('Colisée : duels en chaîne', () => {
  it('même graine, mêmes équipes = même combat', () => {
    const a = runColiseum(setup([30, 30, 30], [30, 30, 30], 7));
    const b = runColiseum(setup([30, 30, 30], [30, 30, 30], 7));
    expect(a).toEqual(b);
    // le combat pas à pas (l'écran) finit pareil que le combat joué d'un coup (le serveur)
    const chain = new DuelChain(setup([30, 30, 30], [30, 30, 30], 7));
    while (!chain.over) chain.step();
    expect(chain.win).toBe(a.win);
    expect(chain.duels).toEqual(a.duels);
  });

  it('le gagnant reste, avec la vie qui lui reste', () => {
    const chain = new DuelChain(setup([200, 1, 1], [5, 5, 5]));
    const duels: DuelEvent[] = [];
    while (!chain.over) for (const e of chain.step()) if (e.type === 'duel') duels.push(e);
    expect(chain.win).toBe(true);
    // le premier héros a battu les trois adversaires, l'un après l'autre
    expect(chain.duels.map((d) => d.hero)).toEqual(['h-1', 'h-1', 'h-1']);
    expect(chain.duels.every((d) => d.winner === 'hero')).toBe(true);
    expect(duels.map((d) => [d.heroNew, d.enemyNew])).toEqual([[false, true], [false, true]]);
    const out = runColiseum(setup([200, 1, 1], [5, 5, 5]));
    expect(out.heroesLeft).toBe(3);
    expect(out.foesLeft).toBe(0);
  });

  it('un combattant blessé garde ses blessures au duel suivant', () => {
    const chain = new DuelChain(setup([1, 1, 1], [60, 1, 1]));
    let seen = false;
    while (!chain.over) {
      for (const e of chain.step()) {
        if (e.type === 'duel' && !e.enemyNew) {
          expect(e.enemy.id).toBe('e-0-0');
          seen ||= e.enemy.hp < e.enemy.maxHp;
        }
      }
    }
    expect(chain.win).toBe(false);
    expect(seen).toBe(true);
  });

  it("l'équipe qui n'a plus de héros a perdu", () => {
    const out = runColiseum(setup([1, 1, 1], [200, 200, 200]));
    expect(out.win).toBe(false);
    expect(out.heroesLeft).toBe(0);
  });
});

describe('Colisée : points, ligues et récompenses', () => {
  it('points à la façon d’Elo', () => {
    expect(pointsChange(1000, 1000, true)).toBe(COLISEUM.win.base);
    expect(pointsChange(1000, 1000, false)).toBe(-COLISEUM.loss.base);
    // battre un mieux classé rapporte plus ; perdre contre lui coûte moins
    expect(pointsChange(1000, 1200, true)).toBeGreaterThan(pointsChange(1000, 1000, true));
    expect(pointsChange(1000, 1200, false)).toBeGreaterThan(pointsChange(1000, 1000, false));
    expect(pointsChange(1000, 5000, true)).toBe(COLISEUM.win.max);
    expect(pointsChange(5000, 1000, true)).toBe(COLISEUM.win.min);
  });

  it('les 3 premiers montent, les 3 derniers descendent', () => {
    const last = COLISEUM_LEAGUES.length - 1;
    expect(leagueAfter(0, 1)).toBe(1);
    expect(leagueAfter(2, 3)).toBe(3);
    expect(leagueAfter(2, 4)).toBe(2);
    expect(leagueAfter(2, 27)).toBe(2);
    expect(leagueAfter(2, 28)).toBe(1);
    expect(leagueAfter(2, 30)).toBe(1);
    // ni sous Bronze, ni au-dessus de Champion
    expect(leagueAfter(0, 30)).toBe(0);
    expect(leagueAfter(last, 1)).toBe(last);
  });

  it('récompenses par place, plus grosses dans les ligues hautes', () => {
    const r1 = rankReward(0, 1), r2 = rankReward(0, 2), r3 = rankReward(0, 3);
    expect(r1.gems).toBeGreaterThan(r2.gems);
    expect(r2.gems).toBeGreaterThan(r3.gems);
    expect(rankReward(0, 4)).toEqual(rankReward(0, 10));
    expect(rankReward(0, 11)).toEqual(rankReward(0, 20));
    expect(rankReward(0, 21)).toEqual(rankReward(0, 30));
    expect(rankReward(0, 10).badge).toBeGreaterThan(rankReward(0, 11).badge);
    expect(rankReward(5, 1).gems).toBeGreaterThan(rankReward(0, 1).gems);
  });

  it('le groupe : 29 autres joueurs, toujours les mêmes pour une graine, des points qui bougent dans la semaine', () => {
    const g = makeGroup(123, 2);
    expect(g).toHaveLength(COLISEUM.groupSize - 1);
    expect(makeGroup(123, 2)).toEqual(g);
    expect(new Set(g.map((b) => b.name)).size).toBe(g.length);
    expect(g.every((b) => b.heroes.length === 3 && new Set(b.heroes).size === 3)).toBe(true);
    expect(g.map((b) => botPoints(b, 0)).every((p) => p <= COLISEUM.startPoints + COLISEUM.win.max)).toBe(true);
    const end = g.map((b) => botPoints(b, 168));
    expect(new Set(end).size).toBeGreaterThan(10);
    expect(g.map((b) => botPoints(b, 168))).toEqual(end);
    const table = standings(g, 168, { name: 'Moi', points: 99999 });
    expect(table).toHaveLength(COLISEUM.groupSize);
    expect(table[0]!.idx).toBe(-1);
  });

  it("l'équipe d'un adversaire a la puissance demandée", () => {
    const team = botTeam(['knights-1', 'mages-3', 'demons-5'], 6000);
    expect(team).toHaveLength(3);
    expect(Math.abs(foePower(team) - 6000) / 6000).toBeLessThan(0.1);
  });
});

describe('Colisée : la semaine du joueur', () => {
  function shiftDays(days: number) {
    update((s) => void (s.timeShift += days * 86_400_000));
  }

  it('combats du jour, achats, et récompense de la semaine avec montée', () => {
    update((s) => {
      s.campaign.cleared = 400;
      s.name = 'Moi';
    });
    ensureDay();
    const c = getState().coliseum!;
    expect(c).toBeTruthy();
    expect(c.league).toBe(0);
    expect(coliseumTeam().length).toBe(Math.min(3, getState().heroes.length));
    expect(coliseumFightsLeft()).toBe(COLISEUM.freeFights);

    // un combat : l'adversaire tiré reste le même jusqu'au combat
    const foe = findColiseumFoe()!;
    expect(findColiseumFoe()).toEqual(foe);
    const res = finishColiseum()!;
    expect(Math.sign(res.delta)).toBe(res.win ? 1 : -1);
    expect(getState().coliseum!.foe).toBeUndefined();
    expect(coliseumFightsLeft()).toBe(COLISEUM.freeFights - 1);

    // les combats du jour épuisés, on en achète un (pas avant)
    expect(buyColiseumFight()).toBe(false);
    update((s) => {
      s.coliseum!.today = COLISEUM.freeFights;
      s.wallet.gems = 1000;
    });
    expect(coliseumFightsLeft()).toBe(0);
    expect(findColiseumFoe()).toBeNull();
    expect(buyColiseumFight()).toBe(true);
    expect(getState().wallet.gems).toBe(1000 - COLISEUM.extraCosts[0]!);
    expect(coliseumFightsLeft()).toBe(1);

    // le lendemain, les combats reviennent
    shiftDays(1);
    ensureDay();
    expect(coliseumFightsLeft()).toBe(COLISEUM.freeFights);

    // premier du groupe en fin de semaine : récompense à récupérer et ligue supérieure
    update((s) => void (s.coliseum!.points = 99999));
    const week = getState().coliseum!.week;
    shiftDays(7);
    ensureDay();
    const after = getState().coliseum!;
    expect(after.week).not.toBe(week);
    expect(after.league).toBe(1);
    expect(after.points).toBe(COLISEUM.startPoints);
    expect(after.pending).toMatchObject({ rank: 1, league: 0, next: 1 });
    const gems = getState().wallet.gems;
    const gain = claimColiseumWeek()!;
    expect(gain.currencies.gems).toBe(rankReward(0, 1).gems);
    expect(getState().wallet.gems).toBe(gems + rankReward(0, 1).gems);
    expect(getState().coliseum!.pending).toBeUndefined();

    // une semaine sans combat : pas de récompense, même ligue
    shiftDays(7);
    ensureDay();
    expect(getState().coliseum!.league).toBe(1);
    expect(getState().coliseum!.pending).toBeUndefined();
    void now;
  });
});
