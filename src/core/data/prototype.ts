// Contenu du prototype : 6 héros (un par faction), 5 monstres, 20 niveaux.
// Les noms affichés sont dans src/game/i18n ; ici seules les règles comptent.
import type { SkillDef, Slot, Talent, UnitInit } from '../battle/types';
import type { Element, Faction, Role } from '../types';

export interface ProtoHero {
  id: string;
  faction: Faction;
  role: Role;
  element: Element;
  hp: number;
  atk: number;
  def: number;
  interval: number;
  ranged: boolean;
  skill: SkillDef;
  talent: Talent;
}

export const PROTO_HEROES: ProtoHero[] = [
  {
    id: 'knight', faction: 'knights', role: 'protector', element: 'earth',
    hp: 1000, atk: 45, def: 60, interval: 12, ranged: false,
    skill: { id: 'rampart', kind: 'shieldAll', power: 0.12 },
    talent: { defMult: 1.25 },
  },
  {
    id: 'angel', faction: 'angels', role: 'healer', element: 'water',
    hp: 560, atk: 45, def: 25, interval: 14, ranged: true,
    skill: { id: 'light', kind: 'healAll', power: 2.6 },
    talent: { energyMult: 1.2 },
  },
  {
    id: 'mage', faction: 'mages', role: 'attacker', element: 'fire',
    hp: 520, atk: 80, def: 20, interval: 15, ranged: true,
    skill: { id: 'firestorm', kind: 'aoe', power: 1.4 },
    talent: { startEnergy: 50 },
  },
  {
    id: 'assassin', faction: 'assassins', role: 'attacker', element: 'wind',
    hp: 620, atk: 90, def: 30, interval: 10, ranged: false,
    skill: { id: 'shadowblade', kind: 'strikeBack', power: 3.2 },
    talent: { atkMult: 1.15 },
  },
  {
    id: 'demon', faction: 'demons', role: 'attacker', element: 'earth',
    hp: 800, atk: 70, def: 40, interval: 12, ranged: false,
    skill: { id: 'bite', kind: 'drain', power: 2.6 },
    talent: { intervalMult: 0.85 },
  },
  {
    id: 'myth', faction: 'myths', role: 'support', element: 'wind',
    hp: 680, atk: 55, def: 35, interval: 13, ranged: true,
    skill: { id: 'thunder', kind: 'stunFront', power: 1.0, stunTicks: 25 },
    talent: { atkMult: 1.1, defMult: 1.1 },
  },
];

export interface ProtoMonster {
  id: string;
  hp: number;
  atk: number;
  def: number;
  interval: number;
  ranged: boolean;
  skill: SkillDef;
  boss?: boolean;
}

export const PROTO_MONSTERS: ProtoMonster[] = [
  { id: 'goblin', hp: 420, atk: 38, def: 15, interval: 11, ranged: false, skill: { id: 'slash', kind: 'strike', power: 2 } },
  { id: 'archer', hp: 320, atk: 46, def: 10, interval: 13, ranged: true, skill: { id: 'snipe', kind: 'strikeBack', power: 2 } },
  { id: 'golem', hp: 950, atk: 34, def: 55, interval: 16, ranged: false, skill: { id: 'quake', kind: 'smash', power: 1.5 } },
  { id: 'shaman', hp: 380, atk: 30, def: 15, interval: 15, ranged: true, skill: { id: 'mend', kind: 'healAll', power: 1.6 } },
  { id: 'ogre', hp: 4200, atk: 85, def: 60, interval: 14, ranged: false, boss: true, skill: { id: 'crush', kind: 'smash', power: 2 } },
  { id: 'lich', hp: 4600, atk: 80, def: 45, interval: 14, ranged: true, boss: true, skill: { id: 'doom', kind: 'aoe', power: 1.1 } },
];

type W = [string, Slot][];
/** Les 20 niveaux : chaque niveau = une ou plusieurs vagues de monstres placés sur leurs postes. */
export const PROTO_STAGES: W[][] = [
  [[['goblin', 2]]],
  [[['goblin', 0], ['goblin', 1]]],
  [[['goblin', 0], ['archer', 3]]],
  [[['goblin', 0], ['goblin', 1]], [['goblin', 0], ['archer', 3]]],
  [[['golem', 0], ['archer', 3], ['archer', 4]]],
  [[['goblin', 0], ['goblin', 1], ['archer', 3]], [['goblin', 0], ['shaman', 3]]],
  [[['golem', 0], ['goblin', 1], ['archer', 3]], [['goblin', 0], ['goblin', 1], ['archer', 4]]],
  [[['goblin', 0], ['goblin', 1], ['archer', 3], ['shaman', 4]], [['golem', 0], ['golem', 1]]],
  [[['golem', 0], ['goblin', 1], ['archer', 3], ['archer', 4]], [['goblin', 0], ['goblin', 1], ['shaman', 2]]],
  [[['goblin', 0], ['goblin', 1], ['archer', 3]], [['goblin', 0], ['ogre', 2], ['shaman', 4]]],
  [[['goblin', 0], ['goblin', 1], ['goblin', 2], ['archer', 3], ['archer', 4]]],
  [[['golem', 0], ['golem', 1], ['shaman', 3]], [['goblin', 0], ['goblin', 1], ['archer', 3], ['archer', 4]]],
  [[['goblin', 0], ['golem', 1], ['archer', 2], ['shaman', 3], ['archer', 4]], [['golem', 0], ['golem', 1]]],
  [[['golem', 0], ['goblin', 1], ['goblin', 2], ['archer', 3], ['shaman', 4]], [['goblin', 0], ['goblin', 1], ['archer', 3], ['archer', 4]]],
  [[['golem', 0], ['golem', 1], ['archer', 3], ['archer', 4]], [['goblin', 0], ['goblin', 1], ['golem', 2], ['shaman', 4]]],
  [[['goblin', 0], ['goblin', 1], ['shaman', 2], ['archer', 3], ['archer', 4]], [['golem', 0], ['golem', 1], ['shaman', 3], ['shaman', 4]]],
  [[['golem', 0], ['golem', 1], ['goblin', 2], ['archer', 3], ['archer', 4]], [['goblin', 0], ['goblin', 1], ['goblin', 2], ['shaman', 3], ['archer', 4]]],
  [[['golem', 0], ['golem', 1], ['shaman', 2], ['archer', 3], ['archer', 4]], [['golem', 0], ['goblin', 1], ['archer', 3], ['shaman', 4]]],
  [[['golem', 0], ['goblin', 1], ['archer', 2], ['archer', 3], ['shaman', 4]], [['golem', 0], ['golem', 1], ['goblin', 2], ['archer', 3], ['archer', 4]], [['goblin', 0], ['goblin', 1], ['shaman', 3], ['shaman', 4]]],
  [[['goblin', 0], ['goblin', 1], ['archer', 3], ['archer', 4]], [['golem', 0], ['golem', 1], ['shaman', 3]], [['goblin', 0], ['lich', 2], ['archer', 3], ['shaman', 4]]],
];

/** Élément des monstres de chaque niveau (tourne entre les 4 éléments, par paires de niveaux). */
export function stageElement(stage: number): Element {
  const order: Element[] = ['fire', 'water', 'wind', 'earth'];
  return order[Math.floor((stage - 1) / 2) % 4]!;
}

/** Niveau des monstres d'un niveau de campagne. */
export function monsterLevel(stage: number): number {
  return stage <= 3 ? 1 : 1 + Math.round((stage - 1) * 1.7);
}

/** Les statistiques montent de 12 % par niveau (défense : 5 %). */
export function scaleStat(base: number, level: number, perLevel = 0.12): number {
  return Math.round(base * (1 + perLevel * (level - 1)));
}

export const PROTO_MAX_LEVEL = 40;

/** Or nécessaire pour passer un héros du niveau L au niveau L+1. */
export function protoLevelCost(level: number): number {
  return Math.round(40 * 1.17 ** (level - 1));
}

/** Or gagné : victoire, victoire sur un niveau déjà fini, défaite. */
export function protoGold(stage: number, kind: 'first' | 'replay' | 'loss'): number {
  const base = 80 + 35 * stage;
  return kind === 'first' ? base : kind === 'replay' ? Math.round(base * 0.5) : Math.round(base * 0.2);
}

/** Héros reçus en finissant un niveau (le chevalier est là dès le début). */
export const HERO_UNLOCKS: Record<number, string> = { 1: 'angel', 3: 'mage', 5: 'assassin', 8: 'demon', 12: 'myth' };
export const STARTING_HERO = 'knight';
/** Nombre de places de la section après avoir fini ce niveau : chaque nouveau héros arrive avec sa place. */
export function protoSlots(cleared: number): number {
  return cleared >= 8 ? 5 : cleared >= 5 ? 4 : cleared >= 3 ? 3 : cleared >= 1 ? 2 : 1;
}

export function heroUnit(id: string, level: number, slot: Slot): UnitInit {
  const h = PROTO_HEROES.find((x) => x.id === id);
  if (!h) throw new Error(`Héros inconnu : ${id}`);
  return {
    id: `h-${id}`, defId: id, side: 'hero', slot, element: h.element,
    maxHp: scaleStat(h.hp, level), atk: scaleStat(h.atk, level), def: scaleStat(h.def, level, 0.05),
    interval: h.interval, ranged: h.ranged, skill: h.skill, talent: h.talent,
  };
}

export function stageWaves(stage: number): UnitInit[][] {
  const waves = PROTO_STAGES[stage - 1];
  if (!waves) throw new Error(`Niveau inconnu : ${stage}`);
  const level = monsterLevel(stage);
  const element = stageElement(stage);
  return waves.map((wave, w) =>
    wave.map(([monsterId, slot], i) => {
      const m = PROTO_MONSTERS.find((x) => x.id === monsterId)!;
      return {
        id: `e-${w}-${i}`, defId: m.id, side: 'enemy' as const, slot, element,
        maxHp: scaleStat(m.hp, level), atk: scaleStat(m.atk, level), def: scaleStat(m.def, level, 0.05),
        interval: m.interval, ranged: m.ranged, skill: m.skill, boss: m.boss,
      };
    }),
  );
}
