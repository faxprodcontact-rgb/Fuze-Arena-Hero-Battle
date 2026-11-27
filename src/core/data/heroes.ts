// Les 47 héros du jeu. 36 sont construits comme des GABARITS : rareté × élément × rôle × variante (statistiques,
// attaque, compétence, passifs et, 1 sur 3, talent de chef) ; les 72 gabarits d'origine sont gardés pour les
// statistiques, seuls les 36 dessinés en HD sont dans le jeu (HERO_IDS). 8 sont des monstres de clan devenus
// héros (CLAN_HEROES) et 3 sont les dragons de la famille d'Elvyn (DRAGONS), avec une compétence écrite pour eux.
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
  assassins: ['Nyx', 'Kael', 'Sable', 'Vesper', 'Rook', 'Isha', 'Corvin', 'Lysa', 'Jarek', 'Morrow', 'Zéphyre', 'Saïko'],
  mages: ['Pell', 'Mira', 'Orin', 'Tessa', 'Ilvar', 'Sélène', 'Arcan', 'Eldra', 'Nimue', 'Ozias', 'Myrr', 'Faust'],
  demons: ['Grizz', 'Vrak', 'Barzul', 'Lilou', 'Kesha', 'Morgath', 'Ruka', 'Zaroth', 'Velith', 'Skarn', 'Azgor', 'Nerith'],
  angels: ['Célia', 'Ilian', 'Aube', 'Séraphin', 'Lumen', 'Elvyn', 'Solenn', 'Ariel', 'Raphaëlle', 'Aurelle', 'Dardane', 'Céleste'],
  myths: ['Faune', 'Satyre', 'Taurok', 'Ophira', 'Dryade', 'Néfira', 'Malgrave', 'Freyja', 'Sylvar', 'Soyane', 'Atlas', 'Zeus'],
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

/** Ce qu'un héros a en propre ; le reste (PV, attaque, défense, vitesse) vient de son rôle, sa rareté, son élément. */
interface Spec {
  id: string; name: string; element: Element; role: Role; rarity: Rarity;
  skill: SkillDef; passives: [Passive, Passive]; talent?: Talent;
  /** Retouches de son profil de rôle (un assassin plus rapide, un tireur plus précis…). */
  tweak?: Partial<Profile>;
}

function build(s: Spec): HeroDef {
  const pr = { ...ROLE_PROFILES[s.role], ...s.tweak };
  const k = RARITY_STAT[s.rarity];
  const el = ELEMENT_STAT[s.element];
  return {
    id: s.id,
    name: s.name,
    element: s.element,
    role: s.role,
    rarity: s.rarity,
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
    skill: s.skill,
    passives: [{ stars: PASSIVE_STARS[0], passive: s.passives[0] }, { stars: PASSIVE_STARS[1], passive: s.passives[1] }],
    talent: s.talent,
  };
}

/**
 * Raretés choisies par le propriétaire (26/11/2026) : 8 Légendaires, 12 Épiques, 13 Rares, 11 Communs, 2 Légendaires et
 * 3 Épiques par élément. Elles remplacent celles des gabarits (statistiques, compétence et talent suivent la rareté).
 */
const RARITY: Readonly<Record<string, Rarity>> = {'angels-11':  'legendary', 'mages-3':  'legendary', 'assassins-5':  'epic', 'demons-5':  'epic', 'myths-9':  'epic', 'mages-11':  'epic', 'knights-3':  'rare', 'demons-3':  'rare', 'demons-9':  'rare', 'demons-12':  'rare', 'myths-3':  'rare', 'myths-4':  'rare', 'mages-7':  'rare', 'mages-2':  'rare', 'knights-8':  'common', 'demons-4':  'common', 'angels-10':  'common', 'assassins-11':  'common'};

const TEMPLATES: HeroDef[] = ELEMENTS.flatMap((element, e) =>
  ELEMENT_ROSTER.map(([base, role, v, leader], i) => {
    const slot = SLOTS[e * ELEMENT_ROSTER.length + i]!;
    const rarity = RARITY[slot.id] ?? base;
    return build({
      id: slot.id, name: slot.name, element, role, rarity,
      skill: skillFor(role, v, element, rarity),
      passives: passivesFor(role, v),
      talent: leader ? talentFor(role, rarity) : undefined,
    });
  }),
);

// ---------- Les 8 monstres de clan devenus héros (décision du propriétaire, 26/11/2026) ----------
// Ils restent aussi des monstres dans leur clan ; leur dessin est celui du monstre (src/game/look.ts, HERO_ART).
// Compétences écrites pour coller à leur animation. Valeurs raisonnables : le grand réglage se fera avant la bêta.

/** Force d'une compétence selon la rareté (comme skillFor). */
const pw = (x: number, rarity: Rarity) => Math.round(x * RARITY_SKILL[rarity] * 100) / 100;
const first = (role: Role) => passivesFor(role, 0)[0];

const CLAN_HEROES: HeroDef[] = [
  // Araignée tisseuse (clan d'Arachné) : elle crache sa toile, la cible ralentit et reste collée
  build({
    id: 'nyrra', name: 'Nyrra', element: 'earth', role: 'marksman', rarity: 'rare',
    skill: { id: 'nyrra', effects: [
      { type: 'damage', target: 'back', power: pw(2, 'rare') },
      { type: 'status', target: 'same', status: 'slow', value: 0.5, seconds: 5 },
      { type: 'status', target: 'same', status: 'stun', seconds: 1.5, chance: 0.5 },
    ] },
    passives: [first('marksman'), { kind: 'trigger', on: 'attack', chance: 0.3, effects: [{ type: 'status', target: 'attacker', status: 'slow', value: 0.3, seconds: 3 }] }],
  }),
  // Serpent guerrier (clan de Méduse) : deux lames très vite, la morsure empoisonne
  build({
    id: 'sarvik', name: 'Sarvik', element: 'earth', role: 'assassin', rarity: 'common', tweak: { interval: 8 },
    skill: { id: 'sarvik', effects: [
      { type: 'damage', target: 'lowestHp', power: pw(1.4, 'common') },
      { type: 'damage', target: 'same', power: pw(1.4, 'common') },
      { type: 'status', target: 'same', status: 'poison', value: 0.03, seconds: 5, chance: 0.9 },
    ] },
    passives: [first('assassin'), { kind: 'trigger', on: 'attack', chance: 0.3, effects: [{ type: 'status', target: 'attacker', status: 'poison', value: 0.02, seconds: 3 }] }],
  }),
  // Tireuse pirate (clan de Barzul) : le mousquet, puis la grosse balle d'eau ; son perroquet repère les points faibles
  build({
    id: 'jessa', name: 'Jessa', element: 'water', role: 'marksman', rarity: 'common', tweak: { crit: 0.14 },
    skill: { id: 'jessa', effects: [
      { type: 'damage', target: 'highestAtk', power: pw(2.4, 'common') },
      { type: 'status', target: 'same', status: 'slow', value: 0.4, seconds: 4, chance: 0.8 },
      { type: 'status', target: 'self', status: 'critUp', value: 0.2, seconds: 6 },
    ] },
    passives: [first('marksman'), { kind: 'stats', stats: { critDmg: 0.3 } }],
  }),
  // Sorcier oni (clan de Lenore) : sa lanterne lâche des feux follets qui brûlent et affaiblissent
  build({
    id: 'oboro', name: 'Oboro', element: 'fire', role: 'support', rarity: 'epic',
    skill: { id: 'oboro', effects: [
      { type: 'damage', target: 'random3', power: pw(1.2, 'epic') },
      { type: 'status', target: 'same', status: 'burn', value: 0.4, seconds: 5, chance: 0.9 },
      { type: 'status', target: 'same', status: 'atkDown', value: 0.2, seconds: 5, chance: 0.6 },
    ] },
    passives: [first('support'), { kind: 'trigger', on: 'attack', chance: 0.3, effects: [{ type: 'status', target: 'attacker', status: 'burn', value: 0.3, seconds: 3 }] }],
    talent: { energyMult: 1.22 },
  }),
  // Tengu à l'éventail (clan d'Orin) : ses rafales repoussent la première ligne et lui volent son énergie
  build({
    id: 'sorai', name: 'Sorai', element: 'wind', role: 'support', rarity: 'rare',
    skill: { id: 'sorai', effects: [
      { type: 'damage', target: 'frontRow', power: pw(0.9, 'rare') },
      { type: 'energy', target: 'same', amount: -25 },
      { type: 'status', target: 'same', status: 'slow', value: 0.3, seconds: 3, chance: 0.7 },
    ] },
    passives: [first('support'), { kind: 'stats', stats: { speed: 0.06 }, team: true }],
  }),
  // Singe chaman (clan d'Eldra) : le grand souffle de sa gourde frappe l'ennemi et soigne toute l'équipe
  build({
    id: 'bao', name: 'Bao', element: 'wind', role: 'healer', rarity: 'epic',
    skill: { id: 'bao', effects: [
      { type: 'damage', target: 'front', power: pw(1, 'epic') },
      { type: 'heal', target: 'allies', power: pw(1.6, 'epic') },
      { type: 'cleanse', target: 'allies' },
      { type: 'energy', target: 'allies', amount: 10 },
    ] },
    passives: [first('healer'), { kind: 'trigger', on: 'start', effects: [{ type: 'shield', target: 'allies', power: 0.08 }] }],
    talent: { healMult: 1.35 },
  }),
  // Singe voleur (clan d'Eldra) : deux coups de dague éclair, il chipe l'énergie de sa cible
  build({
    id: 'gribou', name: 'Gribou', element: 'wind', role: 'assassin', rarity: 'common', tweak: { interval: 8, dodge: 0.14 },
    skill: { id: 'gribou', effects: [
      { type: 'damage', target: 'back', power: pw(1.2, 'common') },
      { type: 'damage', target: 'same', power: pw(1.2, 'common') },
      { type: 'energy', target: 'same', amount: -30 },
      { type: 'energy', target: 'self', amount: 30 },
    ] },
    passives: [first('assassin'), { kind: 'trigger', on: 'kill', effects: [{ type: 'status', target: 'self', status: 'speedUp', value: 0.3, seconds: 5 }] }],
  }),
  // Corbeau tengu (clan d'Orin) : un coup de sabre précis sur le plus affaibli, ses coups critiques font très mal
  build({
    id: 'karu', name: 'Karu', element: 'wind', role: 'assassin', rarity: 'rare', tweak: { crit: 0.25, critDmg: 1.8 },
    skill: { id: 'karu', effects: [
      { type: 'damage', target: 'lowestHp', power: pw(2.8, 'rare'), execute: 0.5 },
      { type: 'status', target: 'self', status: 'critUp', value: 0.3, seconds: 6 },
    ] },
    passives: [first('assassin'), { kind: 'stats', stats: { critDmg: 0.4 } }],
    talent: { atkMult: 1.1 },
  }),
];

// ---------- Les 3 dragons, famille d'Elvyn (demande du propriétaire, 27/11/2026) ----------
// Dessinés seulement en vectoriel (refonte-graphique/ui-moderne/heros/brasyr|rocvar|venthys/, images
// public/art/vecto/dragon-<élément>.webp) : pas de pixel art. Compétence = leur attaque spéciale animée. Légendaires comme
// Elvyn (décision du propriétaire, 27/11 : les 4 dragons sont les Légendaires du portail spécial, FEATURED_BANNER de
// data/summon.ts) ; valeurs au niveau des Légendaires de leur rôle, sans simulation : le grand réglage se fera avant la
// bêta. Noms provisoires.
const DRAGONS: HeroDef[] = [
  // Brasyr, dragon de feu, hallebarde : « souffle du dragon », un long jet de feu qui enveloppe la première ligne
  build({
    id: 'dragon-feu', name: 'Brasyr', element: 'fire', role: 'warrior', rarity: 'legendary',
    skill: { id: 'brasyr', effects: [
      { type: 'damage', target: 'frontRow', power: pw(1.6, 'legendary') },
      { type: 'status', target: 'same', status: 'burn', value: 0.5, seconds: 5, chance: 0.9 },
    ] },
    // son attaque de base, le « croissant de braise », met parfois le feu
    passives: [first('warrior'), { kind: 'trigger', on: 'attack', chance: 0.3, effects: [{ type: 'status', target: 'attacker', status: 'burn', value: 0.3, seconds: 3 }] }],
  }),
  // Rocvar, dragon de terre, marteau et pavois : « la colère de la montagne », il enfonce son pavois dans le sol et des
  // aiguilles de pierre jaillissent sous l'ennemi (étourdi, défense brisée) ; il attire les coups sur lui
  build({
    id: 'dragon-terre', name: 'Rocvar', element: 'earth', role: 'protector', rarity: 'legendary',
    skill: { id: 'rocvar', effects: [
      { type: 'damage', target: 'front', power: pw(1.6, 'legendary') },
      { type: 'status', target: 'same', status: 'stun', seconds: 2, chance: 0.7 },
      { type: 'status', target: 'same', status: 'defDown', value: 0.25, seconds: 5, chance: 0.7 },
      { type: 'status', target: 'self', status: 'taunt', seconds: 3 },
    ] },
    // « le roc lancé » : celui qui le frappe peut recevoir un rocher en retour
    passives: [first('protector'), { kind: 'trigger', on: 'hurt', chance: 0.25, effects: [{ type: 'damage', target: 'attacker', power: 0.8 }] }],
    talent: { defMult: 1.3 },
  }),
  // Venthys, dragon de vent, deux lames : « cyclone », un tourbillon qui file jusqu'à la dernière ligne et l'entaille
  // trois fois ; le vent le rend plus rapide
  build({
    id: 'dragon-vent', name: 'Venthys', element: 'wind', role: 'assassin', rarity: 'legendary',
    skill: { id: 'venthys', effects: [
      { type: 'damage', target: 'back', power: pw(1, 'legendary') },
      { type: 'damage', target: 'same', power: pw(1, 'legendary') },
      { type: 'damage', target: 'same', power: pw(1, 'legendary') },
      { type: 'status', target: 'self', status: 'speedUp', value: 0.3, seconds: 4 },
    ] },
    passives: [first('assassin'), { kind: 'trigger', on: 'kill', effects: [{ type: 'status', target: 'self', status: 'speedUp', value: 0.3, seconds: 5 }] }],
  }),
];

export const HEROES: HeroDef[] = [...TEMPLATES.filter((h) => KEPT.has(h.id)), ...CLAN_HEROES, ...DRAGONS];

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
