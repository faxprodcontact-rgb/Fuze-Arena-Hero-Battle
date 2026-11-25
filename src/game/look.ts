// Ce que l'on voit pendant un combat : le terrain et la famille de monstres, selon le mode et l'avancée.
// Les règles (forces, éléments des monstres) ne changent pas : on choisit seulement les dessins.
import type { DungeonKind } from '../core/data/modes';
import { chapterOf } from '../core/stages';
import type { Element } from '../core/types';
import { ART_META } from './art-meta';

export type Terrain = keyof typeof ART_META.terrains;

/**
 * Les 8 fonds de combat HD animés en pixel art, un par clan de monstres (refonte-graphique/pixel/fonds/, chargés par
 * src/game/bg/fond-px.ts), dans l'ordre des régions de la campagne.
 */
export const FONDS = ['eldra', 'arachne', 'meduse', 'kael', 'orin', 'barzul', 'lenore', 'kesha'] as const;
export type Fond = (typeof FONDS)[number];
const isFond = (v: string): v is Fond => (FONDS as readonly string[]).includes(v);

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
const REGIONS: { chapters: number; terrain: Terrain; fond: Fond; families: Record<Element, string> }[] = [
  { chapters: 4, terrain: 'meadow', fond: 'eldra', families: { fire: 'parade', wind: 'epouvantails', water: 'bayou', earth: 'ronciers' } },
  { chapters: 4, terrain: 'bramble', fond: 'arachne', families: { fire: 'fauves', wind: 'ruche', water: 'bayou', earth: 'ronciers' } },
  { chapters: 4, terrain: 'bayou', fond: 'meduse', families: { fire: 'fauves', wind: 'voliere', water: 'bayou', earth: 'cuirasses' } },
  { chapters: 4, terrain: 'ash', fond: 'kael', families: { fire: 'fauves', wind: 'voliere', water: 'bayou', earth: 'cuirasses' } },
  { chapters: 4, terrain: 'tundra', fond: 'orin', families: { fire: 'fauves', wind: 'voliere', water: 'glaces', earth: 'cuirasses' } },
  { chapters: 4, terrain: 'storm', fond: 'barzul', families: { fire: 'idoles', wind: 'voliere', water: 'glaces', earth: 'echiquier' } },
  { chapters: 3, terrain: 'temple', fond: 'lenore', families: { fire: 'idoles', wind: 'ruche', water: 'abysses', earth: 'echiquier' } },
  { chapters: 3, terrain: 'abyss', fond: 'kesha', families: { fire: 'parade', wind: 'voliere', water: 'abysses', earth: 'cuirasses' } },
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
  /** Fond en pixel art à la place du décor (art/px/fond-<nom>.webp), pour l'essai du nouveau style. */
  pixel?: string;
  /** Fond HD animé du clan, à la place du décor dessiné par le code (`terrain` reste celui de la région). */
  fond?: Fond;
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
  return { terrain: r.terrain, fond: r.fond, family: (e) => r.families[e] };
}

const DUNGEONS: DungeonKind[] = ['gold', 'essence', 'gear'];

/** Les 14 décors dessinés, dans l'ordre de la campagne puis des modes (pour l'outil de test des réglages). */
export const TERRAINS: Terrain[] = ['meadow', 'bramble', 'bayou', 'ash', 'tundra', 'storm', 'temple', 'abyss', 'tower', 'mine', 'spring', 'armory', 'lair', 'arena'];

/** Ce que l'outil de test peut imposer : un fond HD animé (les 8 clans) ou un des décors dessinés par le code. */
export const FOND_CHOICES: (Fond | Terrain)[] = [...FONDS, ...TERRAINS];

const FOND_KEY = 'fuze-fond';
/** Outil de test : le décor imposé à tous les combats et à l'accueil (réglages, ou `#fond=<clan ou terrain>` dans l'adresse). */
export function forcedTerrain(): Fond | Terrain | null {
  const m = typeof location === 'undefined' ? null : /(?:^#|&)fond=([a-z]+)/.exec(location.hash);
  let v: string | null = m?.[1] ?? null;
  if (!v) try { v = localStorage.getItem(FOND_KEY); } catch { v = null; }
  return v && (isFond(v) || v in ART_META.terrains) ? (v as Fond | Terrain) : null;
}
export function setForcedTerrain(t: Fond | Terrain | null) {
  try { if (t) localStorage.setItem(FOND_KEY, t); else localStorage.removeItem(FOND_KEY); } catch { /* rien */ }
}
function forced(look: Look): Look {
  const t = forcedTerrain();
  if (!t) return look;
  return isFond(t) ? { ...look, fond: t, pixel: undefined } : { ...look, terrain: t, fond: undefined, pixel: undefined };
}

/**
 * Le fond du combat d'essai HD : celui du clan le plus nombreux chez les ennemis (à égalité, le premier venu) ;
 * `clans` = le clan de chaque ennemi (les monstres `mon-<clan>-…`, sinon un général de clan). Aucun : un clan au hasard.
 */
export function trialFond(clans: string[]): Fond {
  const own = clans.filter(isFond);
  if (!own.length) return FONDS[Math.floor(Math.random() * FONDS.length)]!;
  const count = (c: Fond) => own.filter((o) => o === c).length;
  return own.reduce((best, c) => (count(c) > count(best) ? c : best), own[0]!);
}

/** Le décor d'un combat, d'après son mode et son titre (« 3-12 » en campagne, l'étage de la tour…) ; `fond` : l'essai HD. */
export function battleLook(kind: string, title: string, dungeon?: DungeonKind, fond?: Fond): Look {
  return forced(lookOf(kind, title, dungeon, fond));
}

function lookOf(kind: string, title: string, dungeon?: DungeonKind, fond?: Fond): Look {
  switch (kind) {
    case 'campaign':
      return campaignLook(Math.max(1, Number.parseInt(title, 10) || 1));
    case 'hdDemo':
      // outil de test : le fond HD du clan des ennemis (les familles ne servent qu'aux monstres sans dessin HD)
      return { terrain: 'meadow', fond: fond ?? trialFond([]), family: (e) => ({ earth: 'ronciers', water: 'bayou', fire: 'parade', wind: 'glaces' })[e] };
    case 'demo':
      // outil de test : les familles des monstres redessinés en pixel art (voir pixelDemoBattle)
      return { terrain: 'meadow', pixel: 'prairie', family: (e) => ({ earth: 'ronciers', water: 'bayou', fire: 'parade', wind: 'glaces' })[e] };
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
