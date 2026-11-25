// Les 36 héros du jeu, construits comme des GABARITS : rareté × élément × rôle × variante.
// Chaque gabarit a ses statistiques, son attaque, sa compétence, ses passifs et (1 sur 3) son talent de chef.
// Les 72 gabarits d'origine sont gardés pour les statistiques ; seuls les 36 dessinés en HD sont dans le jeu (HERO_IDS).
import type { Effect, Passive, SkillDef, Talent } from '../battle/types';
import { ELEMENTS, type Element, type HeroDef, type Rarity, type Role } from '../types';

// ---------- Profils de rôle (niveau 1, ★1, Épique) ----------

interface Profile {
  hp: number; atk: number; def: number; interval: number;
  crit: number; critDmg: number; dodge: number; tenacity: number;
  ranged: boolean; hitsBack?: boolean;
}

export const ROLE_PROFILES: Record<Role, Profile> = {
  protector: { hp: 1000, atk: 45, def: 60, interval: 12, crit: 0.05, critDmg: 1.5, dodge: 0.02, tenacity: 0.2, ranged: false },
  warrior: { hp: 780, atk: 80, def: 40, interval: 11, crit: 0.08, critDmg: 1.5, dodge: 0.03, tenacity: 0.1, ranged: false },
  marksman: { hp: 540, atk: 86, def: 22, interval: 14, crit: 0.1, critDmg: 1.6, dodge: 0.03, tenacity: 0.05, ranged: true },
  assassin: { hp: 560, atk: 92, def: 24, interval: 9, crit: 0.18, critDmg: 1.7, dodge: 0.1, tenacity: 0.05, ranged: false, hitsBack: true },
  healer: { hp: 600, atk: 52, def: 26, interval: 14, crit: 0.05, critDmg: 1.5, dodge: 0.03, tenacity: 0.1, ranged: true },
  support: { hp: 680, atk: 60, def: 32, interval: 13, crit: 0.05, critDmg: 1.5, dodge: 0.05, tenacity: 0.15, ranged: true },
};

/** PV, attaque et défense selon la rareté. */
export const RARITY_STAT: Record<Rarity, number> = { common: 0.9, rare: 0.95, epic: 1, legendary: 1.08 };
/** Force des compétences selon la rareté. */
export const RARITY_SKILL: Record<Rarity, number> = { common: 1, rare: 1.05, epic: 1.12, legendary: 1.22 };
/** Petite touche de chaque élément sur les statistiques. */
export const ELEMENT_STAT: Record<Element, { hp?: number; atk?: number; def?: number; speed?: number }> = {
  fire: { atk: 0.05 }, water: { hp: 0.05 }, wind: { speed: 0.05 }, earth: { def: 0.1 },
};

/** Étoiles nécessaires pour débloquer le 1er et le 2e passif. Éveil des Légendaires (compétence +25 %) à ★10. */
export const PASSIVE_STARS = [3, 5] as const;
export const AWAKEN_STARS = 10;
export const AWAKEN_SKILL = 1.25;

// ---------- Touche d'élément sur les compétences ----------

/** Ce que l'élément ajoute à une compétence de dégâts (sur les mêmes cibles) ou de soin. */
function elementRider(element: Element, kind: 'damage' | 'heal'): Effect {
  if (kind === 'heal') {
    switch (element) {
      case 'fire': return { type: 'status', target: 'allies', status: 'atkUp', value: 0.1, seconds: 5 };
      case 'water': return { type: 'status', target: 'allies', status: 'regen', value: 0.2, seconds: 5 };
      case 'wind': return { type: 'energy', target: 'allies', amount: 10 };
      case 'earth': return { type: 'shield', target: 'allies', power: 0.05 };
    }
  }
  switch (element) {
    case 'fire': return { type: 'status', target: 'same', status: 'burn', value: 0.3, seconds: 4, chance: 0.7 };
    case 'water': return { type: 'status', target: 'same', status: 'slow', value: 0.4, seconds: 3, chance: 0.6 };
    case 'wind': return { type: 'status', target: 'self', status: 'speedUp', value: 0.3, seconds: 4 };
    case 'earth': return { type: 'status', target: 'same', status: 'defDown', value: 0.2, seconds: 5, chance: 0.6 };
  }
}

// ---------- Compétences : 3 variantes par rôle ----------

function skillFor(role: Role, v: number, element: Element, rarity: Rarity): SkillDef {
  const k = RARITY_SKILL[rarity];
  const p = (x: number) => Math.round(x * k * 100) / 100;
  const dmg = (e: Effect[]): SkillDef => ({ id: `${role}-${v}`, effects: [...e, elementRider(element, 'damage')] });
  const heal = (e: Effect[]): SkillDef => ({ id: `${role}-${v}`, effects: [...e, elementRider(element, 'heal')] });
  const plain = (e: Effect[]): SkillDef => ({ id: `${role}-${v}`, effects: e });
  switch (role) {
    case 'protector':
      return [
        plain([{ type: 'shield', target: 'allies', power: p(0.12) }, { type: 'status', target: 'self', status: 'taunt', seconds: 3 }]),
        dmg([{ type: 'damage', target: 'frontRow', power: p(1.3) }, { type: 'status', target: 'same', status: 'stun', seconds: 1.5, chance: 0.5 }]),
        plain([{ type: 'status', target: 'allies', status: 'defUp', value: 0.3, seconds: 5 }, { type: 'heal', target: 'self', pctMax: p(0.15) }, { type: 'status', target: 'self', status: 'taunt', seconds: 3 }]),
      ][v]!;
    case 'warrior':
      return [
        dmg([{ type: 'damage', target: 'front', power: p(2.4), execute: 0.5 }]),
        dmg([{ type: 'damage', target: 'frontRow', power: p(1.5) }, { type: 'status', target: 'same', status: 'bleed', value: 0.35, seconds: 4, chance: 0.8 }]),
        dmg([{ type: 'damage', target: 'front', power: p(2.6), lifesteal: 0.3 }, { type: 'status', target: 'self', status: 'atkUp', value: 0.3, seconds: 6 }]),
      ][v]!;
    case 'marksman':
      return [
        dmg([{ type: 'damage', target: 'all', power: p(1.1) }]),
        dmg([{ type: 'damage', target: 'backRow', power: p(1.9) }]),
        dmg([{ type: 'damage', target: 'random3', power: p(1.6) }, { type: 'status', target: 'self', status: 'critUp', value: 0.2, seconds: 6 }]),
      ][v]!;
    case 'assassin':
      return [
        dmg([{ type: 'damage', target: 'lowestHp', power: p(3), execute: 0.6 }]),
        dmg([{ type: 'damage', target: 'back', power: p(2.5) }, { type: 'status', target: 'same', status: 'silence', seconds: 3, chance: 0.7 }]),
        dmg([{ type: 'damage', target: 'highestAtk', power: p(2.8) }, { type: 'status', target: 'same', status: 'bleed', value: 0.4, seconds: 5 }]),
      ][v]!;
    case 'healer':
      return [
        heal([{ type: 'heal', target: 'allies', power: p(2.2) }]),
        heal([{ type: 'heal', target: 'lowestAlly', power: p(4.5) }, { type: 'status', target: 'allies', status: 'regen', value: 0.25, seconds: 5 }]),
        heal([
          { type: 'heal', target: 'allies', power: p(1.6) }, { type: 'cleanse', target: 'allies' },
          ...(rarity === 'legendary' ? [{ type: 'revive', pctMax: 0.3 } as Effect] : []),
        ]),
      ][v]!;
    case 'support':
      return [
        plain([{ type: 'damage', target: 'frontRow', power: p(0.9) }, { type: 'status', target: 'same', status: 'stun', seconds: 2.5, chance: 0.7 }]),
        plain([{ type: 'status', target: 'allies', status: 'atkUp', value: p(0.25), seconds: 6 }, { type: 'energy', target: 'allies', amount: 20 }]),
        plain([{ type: 'status', target: 'all', status: 'defDown', value: p(0.3), seconds: 6, chance: 0.8 }, { type: 'status', target: 'all', status: 'slow', value: 0.4, seconds: 4, chance: 0.6 }]),
      ][v]!;
  }
}

// ---------- Passifs : le 1er (★3) dépend du rôle, le 2e (★5) de la variante ----------

function passivesFor(role: Role, v: number): [Passive, Passive] {
  const st = (stats: Passive & { kind: 'stats' }) => stats;
  switch (role) {
    case 'protector':
      return [st({ kind: 'stats', stats: { hp: 0.15, tenacity: 0.1 } }), [
        { kind: 'trigger', on: 'hurt', chance: 0.25, effects: [{ type: 'damage', target: 'attacker', power: 0.8 }] },
        { kind: 'trigger', on: 'lowHp', effects: [{ type: 'shield', target: 'self', power: 0.3 }] },
        { kind: 'stats', stats: { def: 0.08 }, team: true },
      ][v] as Passive];
    case 'warrior':
      return [st({ kind: 'stats', stats: { lifesteal: 0.1, atk: 0.08 } }), [
        { kind: 'trigger', on: 'kill', effects: [{ type: 'energy', target: 'self', amount: 40 }] },
        { kind: 'trigger', on: 'attack', chance: 0.3, effects: [{ type: 'status', target: 'attacker', status: 'bleed', value: 0.3, seconds: 3 }] },
        { kind: 'trigger', on: 'lowHp', effects: [{ type: 'status', target: 'self', status: 'atkUp', value: 0.4, seconds: 8 }, { type: 'heal', target: 'self', pctMax: 0.2 }] },
      ][v] as Passive];
    case 'marksman':
      return [st({ kind: 'stats', stats: { crit: 0.1 } }), [
        { kind: 'trigger', on: 'start', effects: [{ type: 'status', target: 'self', status: 'atkUp', value: 0.2, seconds: 10 }] },
        { kind: 'stats', stats: { critDmg: 0.3 } },
        { kind: 'trigger', on: 'kill', effects: [{ type: 'energy', target: 'self', amount: 30 }] },
      ][v] as Passive];
    case 'assassin':
      return [st({ kind: 'stats', stats: { dodge: 0.1, crit: 0.08 } }), [
        { kind: 'stats', stats: { critDmg: 0.4 } },
        { kind: 'trigger', on: 'kill', effects: [{ type: 'status', target: 'self', status: 'speedUp', value: 0.3, seconds: 5 }] },
        { kind: 'trigger', on: 'start', effects: [{ type: 'status', target: 'self', status: 'critUp', value: 0.3, seconds: 8 }] },
      ][v] as Passive];
    case 'healer':
      return [st({ kind: 'stats', stats: { tenacity: 0.08 }, team: true }), [
        { kind: 'trigger', on: 'allyDeath', effects: [{ type: 'heal', target: 'allies', power: 1.2 }] },
        { kind: 'trigger', on: 'start', effects: [{ type: 'shield', target: 'allies', power: 0.08 }] },
        { kind: 'stats', stats: { hp: 0.06 }, team: true },
      ][v] as Passive];
    case 'support':
      return [{ kind: 'trigger', on: 'start', effects: [{ type: 'energy', target: 'allies', amount: 15 }] }, [
        { kind: 'trigger', on: 'attack', chance: 0.25, effects: [{ type: 'status', target: 'attacker', status: 'atkDown', value: 0.2, seconds: 4 }] },
        { kind: 'stats', stats: { speed: 0.06 }, team: true },
        { kind: 'stats', stats: { crit: 0.05 }, team: true },
      ][v] as Passive];
  }
}

// ---------- Talents de chef (1 héros sur 3) ----------

function talentFor(role: Role, rarity: Rarity): Talent {
  const l = rarity === 'legendary';
  switch (role) {
    case 'protector': return { defMult: l ? 1.3 : 1.2 };
    case 'warrior': return { atkMult: l ? 1.18 : 1.12 };
    case 'marksman': return { startEnergy: l ? 50 : 40 };
    case 'healer': return { healMult: l ? 1.35 : 1.25 };
    case 'support': return l ? { energyMult: 1.22 } : { intervalMult: 0.9 };
    case 'assassin': return { atkMult: l ? 1.15 : 1.1 };
  }
}

// ---------- Les 18 gabarits d'un élément ----------
/** [rareté, rôle, variante, chef ?] pour chaque place de la liste d'un élément (les 72 gabarits d'origine). */
const ELEMENT_ROSTER: [Rarity, Role, number, boolean][] = [
  ['common', 'protector', 0, false], ['common', 'warrior', 0, false], ['common', 'marksman', 0, false],
  ['rare', 'protector', 1, false], ['rare', 'assassin', 0, false], ['rare', 'healer', 0, false], ['rare', 'support', 0, true],
  ['epic', 'protector', 2, true], ['epic', 'warrior', 1, false], ['epic', 'marksman', 1, false],
  ['epic', 'assassin', 1, false], ['epic', 'healer', 1, true], ['epic', 'support', 1, false],
  ['legendary', 'warrior', 2, true], ['legendary', 'marksman', 2, true], ['legendary', 'assassin', 2, false],
  ['legendary', 'healer', 2, false], ['legendary', 'support', 2, true],
];

// Identifiants et noms conservés (les sauvegardes existantes restent valables) : les identifiants viennent des
// anciens groupes du dessin provisoire (knights, mages…), ils ne veulent plus rien dire.
const GROUPS = ['knights', 'assassins', 'mages', 'demons', 'angels', 'myths'] as const;
const OLD_NAMES: Record<(typeof GROUPS)[number], string[]> = {
  knights: ['Bérold', 'Maëla', 'Aldric', 'Sorène', 'Tybalt', 'Cassian', 'Ysolde', 'Garvin', 'Lenore', 'Aurèle', 'Valdis', 'Orlane'],
  assassins: ['Nyx', 'Kael', 'Sable', 'Vesper', 'Rook', 'Isha', 'Corvin', 'Lysa', 'Jinn', 'Morrow', 'Zéphyre', 'Saïko'],
  mages: ['Pell', 'Mira', 'Orin', 'Tessa', 'Ilvar', 'Sélène', 'Arcan', 'Eldra', 'Nimue', 'Ozias', 'Myrr', 'Faust'],
  demons: ['Grizz', 'Vrak', 'Barzul', 'Lilou', 'Kesha', 'Morgath', 'Ruka', 'Zaroth', 'Velith', 'Skarn', 'Azgor', 'Nerith'],
  angels: ['Célia', 'Ilian', 'Aube', 'Séraphin', 'Lumen', 'Elyon', 'Solenn', 'Ariel', 'Raphaëlle', 'Auriel', 'Gabryel', 'Céleste'],
  myths: ['Faune', 'Satyre', 'Astérion', 'Méduse', 'Dryade', 'Minotaure', 'Anubis', 'Freyja', 'Isis', 'Arachné', 'Atlas', 'Zeus'],
};
const SLOTS = GROUPS.flatMap((f) => OLD_NAMES[f].map((name, i) => ({ id: `${f}-${i + 1}`, name })));

/**
 * Les 36 héros du jeu (décision du propriétaire, 25/11/2026) : ceux qui sont dessinés et animés en pixel art HD
 * (refonte-graphique/pixel/hd/, planches public/art/hd/<id>.webp). Les 36 autres gabarits sont retirés : dans une
 * vieille sauvegarde, ils sont échangés contre un dédommagement (state/migrate.ts).
 */
export const HERO_IDS = [
  'knights-1', 'knights-3', 'knights-5', 'knights-7', 'knights-8', 'knights-9', 'assassins-2', 'assassins-3', 'assassins-5',
  'assassins-7', 'assassins-9', 'assassins-11', 'mages-2', 'mages-3', 'mages-4', 'mages-7', 'mages-8', 'mages-11',
  'demons-3', 'demons-4', 'demons-5', 'demons-8', 'demons-9', 'demons-12', 'angels-1', 'angels-2', 'angels-6',
  'angels-7', 'angels-10', 'angels-11', 'myths-3', 'myths-4', 'myths-6', 'myths-7', 'myths-9', 'myths-10',
] as const;
const KEPT = new Set<string>(HERO_IDS);

const TEMPLATES: HeroDef[] = ELEMENTS.flatMap((element, e) =>
  ELEMENT_ROSTER.map(([rarity, role, v, leader], i) => {
    const slot = SLOTS[e * ELEMENT_ROSTER.length + i]!;
    const pr = ROLE_PROFILES[role];
    const k = RARITY_STAT[rarity];
    const el = ELEMENT_STAT[element];
    const [p1, p2] = passivesFor(role, v);
    return {
      id: slot.id,
      name: slot.name,
      element,
      role,
      rarity,
      ranged: pr.ranged,
      hitsBack: pr.hitsBack,
      hp: Math.round(pr.hp * k * (1 + (el.hp ?? 0))),
      atk: Math.round(pr.atk * k * (1 + (el.atk ?? 0))),
      def: Math.round(pr.def * k * (1 + (el.def ?? 0))),
      interval: Math.max(4, Math.round(pr.interval / (1 + (el.speed ?? 0)))),
      crit: pr.crit,
      critDmg: pr.critDmg,
      dodge: pr.dodge,
      tenacity: pr.tenacity,
      skill: skillFor(role, v, element, rarity),
      passives: [{ stars: PASSIVE_STARS[0], passive: p1 }, { stars: PASSIVE_STARS[1], passive: p2 }],
      talent: leader ? talentFor(role, rarity) : undefined,
    } satisfies HeroDef;
  }),
);

export const HEROES: HeroDef[] = TEMPLATES.filter((h) => KEPT.has(h.id));

/** Les héros retirés du jeu (identifiant → rareté, élément) : seulement pour dédommager les vieilles sauvegardes. */
export const RETIRED_HEROES: ReadonlyMap<string, { rarity: Rarity; element: Element }> = new Map(
  TEMPLATES.filter((h) => !KEPT.has(h.id)).map((h) => [h.id, { rarity: h.rarity, element: h.element }]),
);

const BY_ID = new Map(HEROES.map((h) => [h.id, h]));

export function isHero(id: string): boolean {
  return BY_ID.has(id);
}

export function heroDef(id: string): HeroDef {
  const def = BY_ID.get(id);
  if (!def) throw new Error(`Héros inconnu : ${id}`);
  return def;
}

/** Les héros d'un élément et d'une rareté (la fusion demande des héros du même élément). */
export function heroesOfElement(element: Element, rarity: Rarity): HeroDef[] {
  return HEROES.filter((h) => h.element === element && h.rarity === rarity);
}

/** Le héros du départ (Garvin, protecteur Épique de feu), offert à la création du compte. */
export const STARTER_HERO = 'knights-8';
