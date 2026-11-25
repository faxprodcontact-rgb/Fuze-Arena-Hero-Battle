// Les monstres des règles. Statistiques pour une force de 100 ; le niveau de campagne les multiplie.
// Leur dessin vient du clan du combat (src/game/look.ts) : rapide (goblin, wolf), costaud (golem), tireur ou lanceur
// de sorts (archer, shaman, wraith) ; les boss sont le général du clan, ou un grand boss de leur élément.
import type { SkillDef } from '../battle/types';
import type { Element } from '../types';

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
  { id: 'goblin', hp: 620, atk: 70, def: 25, interval: 11, ranged: false, skill: { id: 'slash', effects: [{ type: 'damage', target: 'front', power: 2 }] } },
  { id: 'wolf', hp: 560, atk: 76, def: 20, interval: 9, ranged: false, skill: { id: 'bite', effects: [{ type: 'damage', target: 'front', power: 2, lifesteal: 0.5 }] } },
  { id: 'golem', hp: 1100, atk: 45, def: 60, interval: 15, ranged: false, skill: { id: 'quake', effects: [{ type: 'damage', target: 'frontRow', power: 1.4 }] } },
  { id: 'archer', hp: 480, atk: 78, def: 18, interval: 13, ranged: true, skill: { id: 'snipe', effects: [{ type: 'damage', target: 'back', power: 2.4 }] } },
  { id: 'shaman', hp: 520, atk: 50, def: 22, interval: 14, ranged: true, skill: { id: 'mend', effects: [{ type: 'heal', target: 'allies', power: 2 }] } },
  { id: 'wraith', hp: 500, atk: 66, def: 20, interval: 14, ranged: true, skill: { id: 'doom', effects: [{ type: 'damage', target: 'all', power: 1.1 }] } },
  { id: 'ogre', hp: 2600, atk: 110, def: 55, interval: 14, ranged: false, boss: true, skill: { id: 'crush', effects: [{ type: 'damage', target: 'frontRow', power: 2 }, { type: 'status', target: 'frontRow', status: 'stun', seconds: 1.5, chance: 0.4 }] } },
  { id: 'lich', hp: 2300, atk: 100, def: 45, interval: 14, ranged: true, boss: true, skill: { id: 'doom', effects: [{ type: 'damage', target: 'all', power: 1.3 }, { type: 'status', target: 'all', status: 'poison', value: 0.02, seconds: 4, chance: 0.5 }] } },
  { id: 'dragon', hp: 3000, atk: 105, def: 60, interval: 15, ranged: true, boss: true, skill: { id: 'firestorm', effects: [{ type: 'damage', target: 'all', power: 1.4 }, { type: 'status', target: 'all', status: 'burn', value: 0.25, seconds: 4, chance: 0.6 }] } },
];

export const FRONT_MONSTERS = ['goblin', 'wolf', 'golem'];
export const BACK_MONSTERS = ['archer', 'shaman', 'wraith'];
export const BOSSES = ['ogre', 'lich', 'dragon'];
/** L'élément des boss du jour et de guilde (et du grand boss qui les joue : titan de pierre, léviathan, dragon de lave). */
export const BOSS_ELEMENT: Record<string, Element> = { ogre: 'earth', lich: 'water', dragon: 'fire' };

const BY_ID = new Map(MONSTERS.map((m) => [m.id, m]));

export function monsterDef(id: string): MonsterDef {
  const m = BY_ID.get(id);
  if (!m) throw new Error(`Monstre inconnu : ${id}`);
  return m;
}
