// Simulation du prototype : un joueur virtuel fait les 20 niveaux en mode AUTO.
// Il monte ses héros avec son or, et rejoue le dernier niveau gagné quand il perd (pour gagner de l'or).
//   npx tsx simulations/prototype.ts
import { Battle } from '../src/core/battle/engine';
import { ENERGY_MAX, type BattleSetup, type Slot, type Unit } from '../src/core/battle/types';
import {
  HERO_UNLOCKS,
  PROTO_HEROES,
  PROTO_MAX_LEVEL,
  PROTO_STAGES,
  STARTING_HERO,
  heroUnit,
  protoGold,
  protoLevelCost,
  protoSlots,
  stageWaves,
} from '../src/core/data/prototype';

/** Postes préférés de chaque héros, du meilleur au moins bon. */
const PREFERRED: Record<string, Slot[]> = {
  knight: [0, 1, 2], demon: [1, 0, 2], assassin: [1, 0, 3, 2],
  mage: [2, 3, 4], angel: [3, 4, 2], myth: [4, 3, 2],
};

export function autoFormation(owned: string[], levels: Record<string, number>, slots: number): [string, Slot][] {
  const order = PROTO_HEROES.map((h) => h.id).filter((id) => owned.includes(id));
  const chosen = [...order].sort((a, b) => (levels[b] ?? 1) - (levels[a] ?? 1)).slice(0, slots);
  if (chosen.length === 1) return [[chosen[0]!, 2]];
  const taken = new Set<Slot>();
  const out: [string, Slot][] = [];
  for (const id of order.filter((x) => chosen.includes(x))) {
    const slot = (PREFERRED[id] ?? [2]).find((s) => !taken.has(s)) ?? ([0, 1, 2, 3, 4] as Slot[]).find((s) => !taken.has(s))!;
    taken.add(slot);
    out.push([id, slot]);
  }
  return out;
}

/**
 * Ce que ferait un joueur attentif en mode manuel : il garde une compétence pour le bon moment
 * (soin quand un allié est blessé, étourdissement quand un ennemi va frapper fort…), mais jamais plus de 3 s.
 */
export function manualChoice(battle: Battle, readySince: Map<string, number>): string[] {
  const foes = battle.enemies.filter((e) => e.hp > 0);
  const allies = battle.heroes.filter((h) => h.hp > 0);
  const hurt = (u: Unit) => u.hp / u.maxHp;
  const out: string[] = [];
  for (const h of allies) {
    if (h.energy < ENERGY_MAX) {
      readySince.delete(h.id);
      continue;
    }
    if (!readySince.has(h.id)) readySince.set(h.id, battle.tick);
    const waited = battle.tick - readySince.get(h.id)!;
    let good = true;
    switch (h.skill.kind) {
      case 'healAll': good = allies.some((a) => hurt(a) < 0.6); break;
      case 'shieldAll': good = allies.some((a) => hurt(a) < 0.85); break;
      case 'aoe': good = foes.length >= 3 || foes.some((f) => f.boss) || battle.wave + 1 === battle.waveCount; break;
      case 'stunFront': good = foes.some((f) => f.energy >= 60 || f.boss); break;
    }
    if (good || waited >= 30) out.push(h.id);
  }
  return out;
}

export function fight(stage: number, team: [string, Slot][], levels: Record<string, number>, seed: number, manual = false): Battle {
  const setup: BattleSetup = {
    heroes: team.map(([id, slot]) => heroUnit(id, levels[id] ?? 1, slot)),
    waves: stageWaves(stage),
    seed,
    auto: !manual,
  };
  const battle = new Battle(setup);
  const readySince = new Map<string, number>();
  while (!battle.over) {
    if (manual) for (const id of manualChoice(battle, readySince)) battle.requestSkill(id);
    battle.step();
  }
  return battle;
}

function spend(levels: Record<string, number>, team: string[], gold: number): number {
  for (;;) {
    const next = team.filter((id) => (levels[id] ?? 1) < PROTO_MAX_LEVEL).sort((a, b) => (levels[a] ?? 1) - (levels[b] ?? 1))[0];
    if (!next || gold < protoLevelCost(levels[next] ?? 1)) return gold;
    gold -= protoLevelCost(levels[next] ?? 1);
    levels[next] = (levels[next] ?? 1) + 1;
  }
}

function playthrough(seed: number, manual: boolean) {
  const owned = [STARTING_HERO];
  const levels: Record<string, number> = { [STARTING_HERO]: 1 };
  let gold = 0;
  let seconds = 0;
  const rows: { stage: number; tries: number; farms: number; levels: number[]; seconds: number }[] = [];
  for (let stage = 1; stage <= PROTO_STAGES.length; stage++) {
    let tries = 0;
    let farms = 0;
    for (;;) {
      const team = autoFormation(owned, levels, protoSlots(stage - 1));
      gold = spend(levels, team.map(([id]) => id), gold);
      const battle = fight(stage, team, levels, seed * 1000 + stage * 50 + tries, manual);
      tries += 1;
      seconds += battle.tick / 10 / 2; // vitesse ×2
      if (battle.win) {
        gold += protoGold(stage, 'first');
        break;
      }
      gold += protoGold(stage, 'loss');
      if (stage > 1) {
        gold += protoGold(stage - 1, 'replay');
        seconds += 30;
        farms += 1;
      }
      if (tries > 60) break;
    }
    const unlock = HERO_UNLOCKS[stage];
    if (unlock) {
      owned.push(unlock);
      levels[unlock] = Math.max(1, Math.min(...Object.values(levels)) - 2);
    }
    rows.push({ stage, tries, farms, levels: owned.map((id) => levels[id] ?? 1), seconds: Math.round(seconds) });
  }
  return rows;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  for (const manual of process.argv.includes('--manuel') ? [false, true] : [false]) {
    console.log(manual ? '\n=== Joueur en mode MANUEL attentif ===' : '=== Joueur en mode AUTO ===');
    const runs = [1, 2, 3, 4, 5].map((s) => playthrough(s, manual));
    for (let i = 0; i < PROTO_STAGES.length; i++) {
      const r = runs.map((run) => run[i]!);
      const med = (xs: number[]) => [...xs].sort((a, b) => a - b)[2]!;
      console.log(
        `Niveau ${String(i + 1).padStart(2)} : essais ${med(r.map((x) => x.tries))}, ` +
          `rejoués pour l'or ${med(r.map((x) => x.farms))}, niveaux des héros ${r[0]!.levels.join('/')}, ` +
          `temps total ≈ ${Math.round(med(r.map((x) => x.seconds)) / 60)} min`,
      );
    }
  }
}
