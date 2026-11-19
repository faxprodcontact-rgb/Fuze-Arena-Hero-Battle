// Les 72 héros du lancement : 6 factions × 12 héros (2 Communs, 3 Rares, 4 Épiques, 3 Légendaires).
// Noms PROVISOIRES (inventés) : la vraie liste sera écrite avec l'univers.
import type { SkillDef, Talent } from '../battle/types';
import { ELEMENTS, FACTIONS, type Element, type Faction, type HeroDef, type Rarity, type Role } from '../types';

export const HEROES_PER_FACTION: Rarity[] = [
  'common', 'common',
  'rare', 'rare', 'rare',
  'epic', 'epic', 'epic', 'epic',
  'legendary', 'legendary', 'legendary',
];

/** Rôle de chaque emplacement de la liste d'une faction. */
const ROLES_BY_INDEX: Role[] = [
  'protector', 'attacker',
  'protector', 'attacker', 'healer',
  'protector', 'attacker', 'support', 'healer',
  'attacker', 'protector', 'support',
];

const NAMES: Record<Faction, string[]> = {
  knights: ['Bérold', 'Maëla', 'Aldric', 'Sorène', 'Tybalt', 'Cassian', 'Ysolde', 'Garvin', 'Lenore', 'Aurèle', 'Valdis', 'Orlane'],
  assassins: ['Nyx', 'Kael', 'Sable', 'Vesper', 'Rook', 'Isha', 'Corvin', 'Lysa', 'Jinn', 'Morrow', 'Zéphyre', 'Saïko'],
  mages: ['Pell', 'Mira', 'Orin', 'Tessa', 'Ilvar', 'Sélène', 'Arcan', 'Eldra', 'Nimue', 'Ozias', 'Myrr', 'Faust'],
  demons: ['Grizz', 'Vrak', 'Barzul', 'Lilou', 'Kesha', 'Morgath', 'Ruka', 'Zaroth', 'Velith', 'Skarn', 'Azgor', 'Nerith'],
  angels: ['Célia', 'Ilian', 'Aube', 'Séraphin', 'Lumen', 'Elyon', 'Solenn', 'Ariel', 'Raphaëlle', 'Auriel', 'Gabryel', 'Céleste'],
  myths: ['Faune', 'Satyre', 'Cyclope', 'Méduse', 'Dryade', 'Minotaure', 'Anubis', 'Freyja', 'Isis', 'Thor', 'Atlas', 'Zeus'],
};

const RARITY_STAT: Record<Rarity, number> = { common: 0.9, rare: 0.95, epic: 1, legendary: 1.08 };

/** Statistiques de base (niveau 1, ★1) : une force de 100 vaut à peu près ces valeurs. */
function baseStats(role: Role, ranged: boolean) {
  switch (role) {
    case 'protector': return { hp: 1000, atk: 45, def: 60, interval: 12 };
    case 'healer': return { hp: 580, atk: 50, def: 25, interval: 14 };
    case 'support': return { hp: 680, atk: 58, def: 35, interval: 13 };
    default: return ranged ? { hp: 540, atk: 82, def: 22, interval: 14 } : { hp: 650, atk: 90, def: 30, interval: 10 };
  }
}

function skillFor(role: Role, ranged: boolean, f: number, i: number, rarity: Rarity): SkillDef {
  const boost = rarity === 'legendary' ? 1.15 : rarity === 'epic' ? 1.05 : 1;
  const r = (x: number) => Math.round(x * boost * 100) / 100;
  switch (role) {
    case 'protector':
      return (f + i) % 2 === 0 ? { id: 'rampart', kind: 'shieldAll', power: r(0.12) } : { id: 'quake', kind: 'smash', power: r(1.4) };
    case 'healer':
      return { id: 'light', kind: 'healAll', power: r(2.4) };
    case 'support':
      return { id: 'thunder', kind: 'stunFront', power: r(1), stunTicks: 25 };
    default:
      if (ranged) return (f + i) % 2 === 0 ? { id: 'firestorm', kind: 'aoe', power: r(1.3) } : { id: 'snipe', kind: 'strikeBack', power: r(3) };
      return [
        { id: 'slash', kind: 'strike', power: r(2.4) } as SkillDef,
        { id: 'bite', kind: 'drain', power: r(2.4) } as SkillDef,
        { id: 'shadowblade', kind: 'strikeBack', power: r(3) } as SkillDef,
      ][(f + i) % 3]!;
  }
}

/**
 * Seuls 6 héros sur 12 par faction sont chefs de section (talent quand ils sont au centre) :
 * 1 Rare, 2 Épiques et les 3 Légendaires, avec des rôles variés.
 */
const LEADER_INDEXES = new Set([4, 5, 7, 9, 10, 11]);

function talentFor(role: Role, rarity: Rarity, i: number): Talent | undefined {
  if (!LEADER_INDEXES.has(i)) return undefined;
  const l = rarity === 'legendary';
  switch (role) {
    case 'protector': return { defMult: l ? 1.3 : 1.2 };
    case 'healer': return { energyMult: l ? 1.22 : 1.15 };
    case 'support': return { intervalMult: l ? 0.82 : 0.88 };
    default: return i % 2 === 0 ? { atkMult: l ? 1.18 : 1.12 } : { startEnergy: l ? 50 : 40 };
  }
}

export const HEROES: HeroDef[] = FACTIONS.flatMap((faction, f) =>
  HEROES_PER_FACTION.map((rarity, i) => {
    const role = ROLES_BY_INDEX[i]!;
    const ranged = role === 'healer' || role === 'support' || (role === 'attacker' && i % 2 === 0);
    const base = baseStats(role, ranged);
    const k = RARITY_STAT[rarity];
    return {
      id: `${faction}-${i + 1}`,
      name: NAMES[faction][i]!,
      faction,
      rarity,
      role,
      element: ELEMENTS[(f + i) % ELEMENTS.length]!,
      ranged,
      hp: Math.round(base.hp * k),
      atk: Math.round(base.atk * k),
      def: Math.round(base.def * k),
      interval: base.interval,
      skill: skillFor(role, ranged, f, i, rarity),
      talent: talentFor(role, rarity, i),
    };
  }),
);

const BY_ID = new Map(HEROES.map((h) => [h.id, h]));

export function heroDef(id: string): HeroDef {
  const def = BY_ID.get(id);
  if (!def) throw new Error(`Héros inconnu : ${id}`);
  return def;
}

/** Les héros d'un élément et d'une rareté (la fusion demande des héros du même élément). */
export function heroesOfElement(element: Element, rarity: Rarity): HeroDef[] {
  return HEROES.filter((h) => h.element === element && h.rarity === rarity);
}

/** Les héros d'un groupe de la liste provisoire et d'une rareté (les camps ne sont plus une règle du jeu). */
export function heroesOf(faction: Faction, rarity: Rarity): HeroDef[] {
  return HEROES.filter((h) => h.faction === faction && h.rarity === rarity);
}
