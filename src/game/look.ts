// Ce que l'on voit pendant un combat : le clan des monstres et son décor, selon le mode et l'avancée.
// Les règles (forces, éléments des monstres) ne changent pas : on choisit seulement les dessins.
//
// 8 clans, 2 par élément. Chaque clan a un général (un héros, qui joue ses boss, dessiné plus grand), 3 monstres
// (rapide, costaud, tireur ou lanceur de sorts : public/art/vecto/jeu/mon-<clan>-<rôle>.webp) et son décor animé
// (public/art/vecto/fonds/<clan>.webp, src/game/bg/fond-px.ts). Les grands boss (un par élément) jouent les boss du jour,
// de guilde et les fins de région, dès que leur animation est exportée (sinon : le général du clan, plus grand).
import type { DungeonKind } from '../core/data/modes';
import { STAGES_PER_CHAPTER } from '../core/data/economy';
import { BOSS_ELEMENT } from '../core/data/monsters';
import { REGION_CHAPTERS, chapterElement, chapterOf, isRegionFinale, regionOf } from '../core/stages';
import type { Element } from '../core/types';
import { VECTO_ANIM } from './vecto-anim';

/** Les 8 clans, dans l'ordre des régions de la campagne (et de leurs décors). */
export const CLANS = ['eldra', 'arachne', 'meduse', 'kael', 'orin', 'barzul', 'lenore', 'kesha'] as const;
export type Clan = (typeof CLANS)[number];

const CLAN_ELEMENT: Record<Clan, Element> = {
  eldra: 'wind', orin: 'wind', arachne: 'earth', meduse: 'earth', kael: 'fire', lenore: 'fire', barzul: 'water', kesha: 'water',
};
/** L'élément d'un clan (teinte du plateau de la préparation : ui/formation-stage.tsx). */
export const clanElement = (clan: Clan): Element => CLAN_ELEMENT[clan];
/** Le général de chaque clan (un héros). */
export const CLAN_CHIEF: Record<Clan, string> = {
  eldra: 'mages-8', orin: 'mages-3', arachne: 'myths-10', meduse: 'myths-4', kael: 'assassins-2', lenore: 'knights-9',
  barzul: 'demons-3', kesha: 'demons-5',
};
/**
 * Les monstres de clan devenus héros (src/core/data/heroes.ts, CLAN_HEROES) : leur dessin est celui du monstre
 * (mon-<clan>-<rôle>). Côté héros, ils regardent à droite, comme dessinés.
 */
export const HERO_ART: Readonly<Record<string, string>> = {
  nyrra: 'mon-arachne-tisseuse', sarvik: 'mon-meduse-rapide', jessa: 'mon-barzul-tireur', oboro: 'mon-lenore-sorts',
  sorai: 'mon-orin-sorts', bao: 'mon-eldra-sorts', gribou: 'mon-eldra-rapide', karu: 'mon-orin-rapide',
};
/** Le dessin d'un héros (son identifiant, sauf pour un monstre de clan devenu héros). */
export const heroArt = (defId: string): string => HERO_ART[defId] ?? defId;
/** Le troisième monstre du clan : un tireur, ou un lanceur de sorts. */
const THIRD: Record<Clan, string> = {
  eldra: 'sorts', orin: 'sorts', arachne: 'tisseuse', meduse: 'sorts', kael: 'tireur', lenore: 'sorts', barzul: 'tireur', kesha: 'sorts',
};
/** Les 2 clans de chaque élément. */
const OF_ELEMENT = (e: Element): Clan[] => CLANS.filter((c) => CLAN_ELEMENT[c] === e);
/** Les grands boss, un par élément (refonte-graphique/ui-moderne/monstres/) : dragon de lave, léviathan, titan, oiseau-tempête. */
const BIG_BOSS: Record<Element, string> = { fire: 'boss-feu', water: 'boss-eau', earth: 'boss-terre', wind: 'boss-vent' };

/** Ce personnage a-t-il sa planche de combat (exportée par jeu_export_vecto.py) ? */
export const hasFigure = (id: string): boolean => id in VECTO_ANIM.chars;
/** Le grand boss d'un élément, s'il est déjà exporté. */
export function bigBoss(element: Element): string | undefined {
  const id = BIG_BOSS[element];
  return hasFigure(id) ? id : undefined;
}
export const isBigBoss = (id: string): boolean => id.startsWith('boss-');

export interface Look {
  /** Le décor (celui d'un clan). */
  fond: Clan;
  /** Le clan des monstres d'un élément donné. */
  clan: (element: Element) => Clan;
  /** Les boss de ce combat sont joués par le grand boss de leur élément (sinon par le général du clan). */
  bigBoss?: boolean;
}

/** Un combat dont tous les monstres sont d'un même clan, dans son décor. */
function clanLook(clan: Clan, bigBoss = false): Look {
  return { fond: clan, clan: (e) => (CLAN_ELEMENT[clan] === e ? clan : OF_ELEMENT(e)[0]!), bigBoss };
}

/**
 * Campagne : l'élément des monstres change à chaque chapitre (règles du jeu). Chaque région a son clan ; un chapitre
 * d'un autre élément prend l'un des deux clans de cet élément (en alternant d'une région à l'autre). Le décor suit le clan.
 */
export function campaignLook(chapter: number, finale = false): Look {
  const r = regionOf(chapter);
  const home = CLANS[r.index]!;
  const e = chapterElement(chapter);
  const clan = CLAN_ELEMENT[home] === e ? home : OF_ELEMENT(e)[r.index % 2]!;
  return clanLook(clan, finale);
}

/** Le décor de la tour : le clan de l'élément de l'étage, l'un ou l'autre tous les 4 étages. */
function towerLook(floor: number): Look {
  return clanLook(OF_ELEMENT(chapterElement(floor))[Math.floor((floor - 1) / 4) % 2]!);
}

/** Chaque donjon a son clan : la forge de lave (or), la mer (essence), l'antre des araignées (équipement). */
export const DUNGEON_CLAN: Record<DungeonKind, Clan> = { gold: 'kael', essence: 'kesha', gear: 'arachne' };

/** Le clan d'un boss du jour ou de guilde (son décor) : volcan pour le dragon, mer pour le léviathan, pierre pour le titan. */
export function bossClan(bossId: string): Clan {
  return ({ fire: 'kael', water: 'kesha', earth: 'meduse', wind: 'orin' } as const)[BOSS_ELEMENT[bossId] ?? 'fire'];
}

/** Un décor tiré du nom (arène, défis, guerre de guildes : les équipes adverses mêlent les éléments). */
function namedLook(name: string): Look {
  let h = 7;
  for (const ch of name) h = (Math.imul(h, 31) + ch.charCodeAt(0)) >>> 0;
  return clanLook(CLANS[h % CLANS.length]!);
}

/** Le décor d'un combat, d'après son mode et son titre (« 3-12 » en campagne, l'étage de la tour, le boss…). */
export function battleLook(kind: string, title: string, dungeon?: DungeonKind): Look {
  switch (kind) {
    case 'campaign': {
      const [c, p] = title.split('-').map((x) => Number.parseInt(x, 10) || 1) as [number, number?];
      const stage = (c - 1) * STAGES_PER_CHAPTER + (p ?? 1);
      return campaignLook(Math.max(1, c), isRegionFinale(stage));
    }
    case 'tower':
      return towerLook(Number.parseInt(title, 10) || 1);
    case 'dungeon':
      return clanLook(DUNGEON_CLAN[dungeon ?? 'gold']);
    case 'event': {
      // le mode Événement (« 2-7 » = difficulté 2, niveau 7) : chaque niveau du chemin a son clan ; le grand boss au 20e
      const level = Number.parseInt(title.split('-')[1] ?? '1', 10) || 1;
      return clanLook(CLANS[(level - 1) % CLANS.length]!, level % 5 === 0);
    }
    case 'guildBoss':
      return clanLook(bossClan(title), true);
    case 'coliseum':
      // le Colisée : la cour pavée du temple aux bannières et aux torches (le décor qui fait le plus arène)
      return clanLook('lenore');
    default:
      return namedLook(`${kind}:${title}`);
  }
}

/** Le décor de l'accueil : celui du chapitre en cours. */
export function idleLook(cleared: number): Look {
  return campaignLook(chapterOf(Math.max(1, cleared)));
}

/** Monstres des règles → monstre du clan. */
const ROLE_OF: Record<string, 'rapide' | 'costaud' | 'third'> = {
  goblin: 'rapide', wolf: 'rapide', golem: 'costaud', archer: 'third', shaman: 'third', wraith: 'third',
};
const BOSS_IDS = new Set(Object.keys(BOSS_ELEMENT));

/** Le dessin d'un monstre des règles (gobelin, loup…, ou boss) dans un décor donné. */
export function monsterArtId(defId: string, element: Element, look: Look): string {
  const clan = look.clan(element);
  if (BOSS_IDS.has(defId)) return (look.bigBoss && bigBoss(element)) || CLAN_CHIEF[clan];
  const role = ROLE_OF[defId] ?? 'rapide';
  return `mon-${clan}-${role === 'third' ? THIRD[clan] : role}`;
}

/** Les menus sans décor précis. */
export const DEFAULT_LOOK: Look = clanLook('kael', true);

/** Le dessin d'un boss du jour ou de guilde : son grand boss s'il est exporté, sinon le général du clan de son décor. */
export function bossArt(bossId: string): string {
  return monsterArtId(bossId, BOSS_ELEMENT[bossId] ?? 'fire', clanLook(bossClan(bossId), true));
}

/** Les 8 régions de la carte : premier et dernier chapitre de chacune (dans l'ordre de la campagne). */
export function regionChapters(): { from: number; to: number }[] {
  let c = 1;
  return REGION_CHAPTERS.map((n) => { const out = { from: c, to: c + n - 1 }; c += n; return out; });
}
