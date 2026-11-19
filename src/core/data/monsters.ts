// Les monstres. Statistiques pour une force de 100 ; le niveau de campagne les multiplie.
import type { SkillDef } from '../battle/types';

export interface MonsterDef {
  id: string;
  hp: number;
  atk: number;
  def: number;
  interval: number;
  ranged: boolean;
  skill: SkillDef;
  boss?: boolean;
}

export const MONSTERS: MonsterDef[] = [
  { id: 'goblin', hp: 620, atk: 70, def: 25, interval: 11, ranged: false, skill: { id: 'slash', kind: 'strike', power: 2 } },
  { id: 'wolf', hp: 560, atk: 76, def: 20, interval: 9, ranged: false, skill: { id: 'bite', kind: 'drain', power: 2 } },
  { id: 'golem', hp: 1100, atk: 45, def: 60, interval: 15, ranged: false, skill: { id: 'quake', kind: 'smash', power: 1.4 } },
  { id: 'archer', hp: 480, atk: 78, def: 18, interval: 13, ranged: true, skill: { id: 'snipe', kind: 'strikeBack', power: 2.4 } },
  { id: 'shaman', hp: 520, atk: 50, def: 22, interval: 14, ranged: true, skill: { id: 'mend', kind: 'healAll', power: 2 } },
  { id: 'wraith', hp: 500, atk: 66, def: 20, interval: 14, ranged: true, skill: { id: 'doom', kind: 'aoe', power: 1.1 } },
  { id: 'ogre', hp: 2600, atk: 110, def: 55, interval: 14, ranged: false, boss: true, skill: { id: 'crush', kind: 'smash', power: 2 } },
  { id: 'lich', hp: 2300, atk: 100, def: 45, interval: 14, ranged: true, boss: true, skill: { id: 'doom', kind: 'aoe', power: 1.3 } },
  { id: 'dragon', hp: 3000, atk: 105, def: 60, interval: 15, ranged: true, boss: true, skill: { id: 'firestorm', kind: 'aoe', power: 1.4 } },
];

export const FRONT_MONSTERS = ['goblin', 'wolf', 'golem'];
export const BACK_MONSTERS = ['archer', 'shaman', 'wraith'];
export const BOSSES = ['ogre', 'lich', 'dragon'];

const BY_ID = new Map(MONSTERS.map((m) => [m.id, m]));

export function monsterDef(id: string): MonsterDef {
  const m = BY_ID.get(id);
  if (!m) throw new Error(`Monstre inconnu : ${id}`);
  return m;
}
