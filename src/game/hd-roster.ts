// Combat d'essai des personnages HD animés (outil de test, à retirer avant la bêta) : les héros et monstres qui ont
// une planche HD (hd-meta.ts, refonte-graphique/pixel/hd/anim/jeu_export.py) et les combats qui les montrent.
// À part de state/actions.ts pour que hd-meta.ts (lourd) ne soit chargé qu'à l'ouverture du choix des combattants.
import type { Slot, UnitInit } from '../core/battle/types';
import { heroToUnit, monsterToUnit } from '../core/battle/units';
import { HEROES, heroDef } from '../core/data/heroes';
import type { Element } from '../core/types';
import { HD_ANIM } from './hd-meta';
import type { BattleRequest } from './state/actions';

/** Les personnages HD animés (refonte-graphique/pixel/hd/anim/jeu_export.py) : les héros par leur id, les monstres par leur planche. */
export const HD_CHARS = HD_ANIM.chars as unknown as Record<string, { name: string; visage: number[]; size: number[]; anims: { attaque: { genre: string } } }>;
export const HD_UP = HD_ANIM.up;
export const HD_HEROES: string[] = HEROES.map((h) => h.id).filter((id) => id in HD_CHARS);
export const HD_MONSTERS: string[] = Object.keys(HD_CHARS).filter((id) => id.startsWith('mon-'));

/** Un monstre HD au combat : l'élément de son clan (celui du héros chef, `mon-<chef>-<rôle>`), un corps de monstre selon son rôle. */
function hdMonster(art: string, slot: Slot, id: string): UnitInit {
  const clan = art.split('-')[1];
  const chief = Object.keys(HD_CHARS).find((k) => !k.startsWith('mon-') && HD_CHARS[k]!.name === clan);
  const element: Element = chief ? heroDef(chief).element : 'fire';
  const body = art.endsWith('-costaud') ? 'golem' : HD_CHARS[art]!.anims.attaque.genre === 'melee' ? 'goblin' : 'archer';
  const u = monsterToUnit(body, slot, element, 12, id);
  return { ...u, maxHp: u.maxHp * 6 };
}

function hdHero(defId: string, slot: Slot, n: number, side: 'hero' | 'enemy'): UnitInit {
  const u = heroToUnit({ uid: 9100 + n, defId, stars: 5, level: 40 }, slot);
  return side === 'hero' ? u : { ...u, id: `hde-${n}`, side: 'enemy' };
}

/** L'ordre des cases : le premier sur la case du milieu, puis devant, puis au fond. */
const HD_SLOTS: Slot[] = [2, 0, 1, 3, 4];

/** Une manche du combat d'essai HD : jusqu'à 5 contre 5 (héros par id, monstres par planche ; un héros peut être en face). */
function hdRound(heroes: string[], foes: string[], r: number, hdArt: Record<string, string>) {
  const sorted = (ids: string[]) => ids.slice(0, 5).map((id, i) => [id, HD_SLOTS[i]!] as const);
  return {
    heroes: sorted(heroes).map(([id, slot], i) => hdHero(id, slot, r * 10 + i, 'hero')),
    enemies: sorted(foes).map(([id, slot], i) => {
      if (!id.startsWith('mon-')) return hdHero(id, slot, r * 10 + 5 + i, 'enemy');
      const u = hdMonster(id, slot, `hd-${r}-${i}`);
      hdArt[u.id!] = id;
      return u;
    }),
  };
}

/**
 * Outil de test : le combat d'essai des personnages HD animés, avec les héros et les monstres choisis (5 au plus de
 * chaque). Les coups suivent un scénario (src/game/hd-trial.ts) : chacun montre son attaque et sa spéciale, sur
 * des cases différentes ; personne ne tombe, sans récompense.
 */
export function hdTrialBattle(heroes: string[], monsters: string[]): BattleRequest {
  const hdArt: Record<string, string> = {};
  const round = hdRound(heroes, monsters, 0, hdArt);
  return { kind: 'hdDemo', title: '', heroes: round.heroes, waves: [round.enemies], seed: 1, hdArt };
}

/**
 * Outil de test : les 60 personnages HD à la suite, en manches de 5 contre 5 où chacun passe une fois (6 manches :
 * 5 héros contre 4 monstres et 1 héros).
 */
export function hdTrialAll(): BattleRequest {
  const hdArt: Record<string, string> = {};
  const n = Math.ceil((HD_HEROES.length + HD_MONSTERS.length) / 10);
  const rounds = Array.from({ length: n }, (_, r) => {
    const hs = HD_HEROES.filter((_, i) => i % n === r);
    const ms = HD_MONSTERS.filter((_, i) => i % n === r);
    // les héros en trop passent en face, avec les monstres
    return hdRound(hs.slice(0, 5), [...ms, ...hs.slice(5)], r, hdArt);
  });
  return { kind: 'hdDemo', title: '', heroes: rounds[0]!.heroes, waves: [rounds[0]!.enemies], seed: 1, hdArt, hdRounds: rounds };
}
