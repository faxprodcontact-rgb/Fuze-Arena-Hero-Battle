// Le mode ÉVÉNEMENT (27/11/2026, à la place du boss du jour : « les boss seront déjà dans la guilde ») — décisions du
// propriétaire :
// - des zones de 20 niveaux reliés en chemin ; on inscrit une équipe et on ne joue qu'avec elle, jusqu'à perdre,
//   gagner les 20 niveaux ou abandonner ; la vie et les morts restent d'un niveau à l'autre ;
// - tous les 2 niveaux, 2 bonus tirés au hasard parmi : soin de 30 % à toute l'équipe, attaque +, défense +,
//   un héros mort qui revient ; le joueur en choisit 1 ; l'attaque et la défense durent jusqu'à la fin de la partie ;
// - les 20 niveaux finis : la difficulté suivante (zone suivante), et ainsi de suite ; elle repart à 1 à chaque nouvel
//   événement (quand le portail d'événement change, FEATURED_BANNER de summon.ts) ;
// - 3 essais par jour : une partie commencée en prend un ; perdre ou abandonner la finit ;
// - on gagne des parchemins d'événement et de l'XP pour les héros de l'équipe ; on s'arrête entre chaque combat
//   (on prend sa récompense, puis on continue si on veut).
// Les valeurs sont raisonnables, PAS équilibrées (grand réglage avant la bêta).

export const EVENT_LEVELS = 20;
export const EVENT_TRIES_PER_DAY = 3;
/** Un choix de bonus tous les N niveaux gagnés. */
export const EVENT_BONUS_EVERY = 2;

export type EventBonus = 'heal' | 'atk' | 'def' | 'revive';
export const EVENT_BONUSES: readonly EventBonus[] = ['heal', 'atk', 'def', 'revive'];
/** Force de chaque bonus : soin (part de la vie max), attaque et défense (+ part, cumulées), vie du héros qui revient. */
export const EVENT_BONUS_VALUE: Record<EventBonus, number> = { heal: 0.3, atk: 0.15, def: 0.15, revive: 0.5 };

/** La force des ennemis : celle d'un niveau de campagne qui avance avec la difficulté et le niveau de la zone. */
export function eventStage(difficulty: number, level: number): number {
  return 20 + (difficulty - 1) * 60 + level * 3;
}

/** Les niveaux qui donnent des parchemins d'événement (et combien, + 1 par difficulté au-dessus de la première). */
export const EVENT_SCROLL_LEVELS: readonly number[] = [10, 20];
export function eventScrolls(difficulty: number, level: number): number {
  return EVENT_SCROLL_LEVELS.includes(level) ? 1 + Math.floor((difficulty - 1) / 2) : 0;
}

/** L'XP gagnée par chaque héros vivant de l'équipe à chaque niveau gagné. */
export function eventXp(difficulty: number, level: number): number {
  return 40 * difficulty + 4 * level;
}

/** L'XP qu'il faut à un héros pour passer du niveau `level` au suivant (l'XP ne sert qu'à l'Événement pour l'instant). */
export function heroXpForLevel(level: number): number {
  return 60 + 12 * level;
}
