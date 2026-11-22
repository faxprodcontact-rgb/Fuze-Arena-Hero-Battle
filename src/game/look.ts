// Ce que l'on voit pendant un combat : le terrain et la famille de monstres, selon le mode et l'avancée.
// Les règles (forces, éléments des monstres) ne changent pas : on choisit seulement les dessins.
import type { DungeonKind } from '../core/data/modes';
import { chapterOf } from '../core/stages';
import type { Element } from '../core/types';
import { ART_META } from './art-meta';

export type Terrain = keyof typeof ART_META.terrains;

/** Les 12 familles de monstres, 3 par élément. Dessins : `<famille>-1` à `-6` (rapide, costaud, tireur, sorts, élite, boss). */
const FAMILIES: Record<Element, readonly [string, string, string]> = {
  fire: ['fauves', 'idoles', 'parade'],
  wind: ['epouvantails', 'voliere', 'ruche'],
  water: ['bayou', 'glaces', 'abysses'],
  earth: ['ronciers', 'cuirasses', 'echiquier'],
};

/**
 * La campagne traverse 8 régions (30 chapitres), puis recommence. L'élément des monstres change à chaque chapitre
 * (règles du jeu) : chaque région a donc une famille par élément, choisie pour aller avec son décor.
 */
const REGIONS: { chapters: number; terrain: Terrain; families: Record<Element, string> }[] = [
  { chapters: 4, terrain: 'meadow', families: { fire: 'parade', wind: 'epouvantails', water: 'bayou', earth: 'ronciers' } },
  { chapters: 4, terrain: 'bramble', families: { fire: 'fauves', wind: 'ruche', water: 'bayou', earth: 'ronciers' } },
  { chapters: 4, terrain: 'bayou', families: { fire: 'fauves', wind: 'voliere', water: 'bayou', earth: 'cuirasses' } },
  { chapters: 4, terrain: 'ash', families: { fire: 'fauves', wind: 'voliere', water: 'bayou', earth: 'cuirasses' } },
  { chapters: 4, terrain: 'tundra', families: { fire: 'fauves', wind: 'voliere', water: 'glaces', earth: 'cuirasses' } },
  { chapters: 4, terrain: 'storm', families: { fire: 'idoles', wind: 'voliere', water: 'glaces', earth: 'echiquier' } },
  { chapters: 3, terrain: 'temple', families: { fire: 'idoles', wind: 'ruche', water: 'abysses', earth: 'echiquier' } },
  { chapters: 3, terrain: 'abyss', families: { fire: 'parade', wind: 'voliere', water: 'abysses', earth: 'cuirasses' } },
];
const LOOP = REGIONS.reduce((n, r) => n + r.chapters, 0);

/** Les 8 régions de la carte : premier et dernier chapitre de chacune (dans l'ordre de la campagne). */
export function regionChapters(): { from: number; to: number }[] {
  let c = 1;
  return REGIONS.map((r) => { const out = { from: c, to: c + r.chapters - 1 }; c += r.chapters; return out; });
}

/** Monstres des règles → place dans la famille (1 rapide, 2 costaud, 3 tireur, 4 sorts, 5 élite, 6 boss). */
const SLOT_OF: Record<string, number> = { goblin: 1, wolf: 5, golem: 2, archer: 3, shaman: 4, wraith: 4 };
/** Les boss du jour et de guilde ont leur propre dessin. */
const BOSS_ART: Record<string, string> = { dragon: 'parade-6', ogre: 'glaces-6', lich: 'abysses-6' };

export interface Look {
  terrain: Terrain;
  /** Famille des monstres d'un élément donné. */
  family: (element: Element) => string;
  /** Les boss gardent leur dessin propre (boss du jour, de guilde) au lieu du boss de la famille. */
  namedBoss?: boolean;
}

function regionOf(chapter: number) {
  let c = (chapter - 1) % LOOP;
  for (const r of REGIONS) {
    if (c < r.chapters) return r;
    c -= r.chapters;
  }
  return REGIONS[0]!;
}

export function campaignLook(chapter: number): Look {
  const r = regionOf(chapter);
  return { terrain: r.terrain, family: (e) => r.families[e] };
}

const DUNGEONS: DungeonKind[] = ['gold', 'essence', 'gear'];

/** Les 14 décors dessinés, dans l'ordre de la campagne puis des modes (pour l'outil de test des réglages). */
export const TERRAINS: Terrain[] = ['meadow', 'bramble', 'bayou', 'ash', 'tundra', 'storm', 'temple', 'abyss', 'tower', 'mine', 'spring', 'armory', 'lair', 'arena'];

const FOND_KEY = 'fuze-fond';
/** Outil de test : le décor imposé à tous les combats et à l'accueil (réglages, ou `#fond=<terrain>` dans l'adresse). */
export function forcedTerrain(): Terrain | null {
  const m = typeof location === 'undefined' ? null : /(?:^#|&)fond=([a-z]+)/.exec(location.hash);
  let v: string | null = m?.[1] ?? null;
  if (!v) try { v = localStorage.getItem(FOND_KEY); } catch { v = null; }
  return v && v in ART_META.terrains ? (v as Terrain) : null;
}
export function setForcedTerrain(t: Terrain | null) {
  try { if (t) localStorage.setItem(FOND_KEY, t); else localStorage.removeItem(FOND_KEY); } catch { /* rien */ }
}
function forced(look: Look): Look {
  const t = forcedTerrain();
  return t ? { ...look, terrain: t } : look;
}

/** Le décor d'un combat, d'après son mode et son titre (« 3-12 » en campagne, l'étage de la tour…). */
export function battleLook(kind: string, title: string, dungeon?: DungeonKind): Look {
  return forced(lookOf(kind, title, dungeon));
}

function lookOf(kind: string, title: string, dungeon?: DungeonKind): Look {
  switch (kind) {
    case 'campaign':
      return campaignLook(Math.max(1, Number.parseInt(title, 10) || 1));
    case 'tower': {
      const floor = Number.parseInt(title, 10) || 1;
      return { terrain: 'tower', family: (e) => FAMILIES[e][Math.floor(floor / 4) % 3]! };
    }
    case 'dungeon': {
      const i = Math.max(0, DUNGEONS.indexOf(dungeon ?? 'gold'));
      return { terrain: (['mine', 'spring', 'armory'] as const)[i]!, family: (e) => FAMILIES[e][i]! };
    }
    case 'dailyBoss':
    case 'guildBoss':
      return { terrain: 'lair', family: (e) => FAMILIES[e][0]!, namedBoss: true };
    default:
      return { terrain: 'arena', family: (e) => FAMILIES[e][0]! };
  }
}

/** Le décor de l'accueil : celui du chapitre en cours. */
export function idleLook(cleared: number): Look {
  return forced(campaignLook(chapterOf(Math.max(1, cleared))));
}

/** Le dessin d'un monstre des règles (gobelin, loup…, ou boss) dans un décor donné. */
export function monsterArtId(defId: string, element: Element, look: Look): string {
  if (BOSS_ART[defId]) return look.namedBoss ? BOSS_ART[defId]! : `${look.family(element)}-6`;
  return `${look.family(element)}-${SLOT_OF[defId] ?? 1}`;
}

/** Les menus sans décor précis (page du boss du jour, de guilde…). */
export const DEFAULT_LOOK: Look = { terrain: 'lair', family: (e) => FAMILIES[e][0]!, namedBoss: true };
