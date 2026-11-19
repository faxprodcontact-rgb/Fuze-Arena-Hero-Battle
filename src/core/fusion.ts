// Fusion des héros : vérification des règles et choix automatique des héros à sacrifier.
import { heroDef } from './data/heroes';
import { LADDER, RARITY_RULES, TRIPLE_COUNT } from './data/stars';
import { gearRefund, levelRefund } from './power';
import type { Hero, Rarity } from './types';

export interface FusionPlan {
  targetUid: number;
  /** Héros sacrifiés (copies et héros de la même faction). */
  consumed: number[];
  crystals: number;
  newStars: number;
}

const RARITY_RANK: Record<Rarity, number> = { common: 0, rare: 1, epic: 2, legendary: 3 };

function ruleOf(hero: Hero) {
  return RARITY_RULES[heroDef(hero.defId).rarity];
}

export function canGainStar(hero: Hero): boolean {
  return hero.stars < ruleOf(hero).maxStars;
}

/** Vérifie qu'une fusion respecte les règles (utilisé par le serveur pour refuser la triche). */
export function isValidFusion(roster: readonly Hero[], plan: FusionPlan, crystalsOwned: number): boolean {
  const byUid = new Map(roster.map((h) => [h.uid, h]));
  const target = byUid.get(plan.targetUid);
  if (!target || !canGainStar(target) || plan.newStars !== target.stars + 1) return false;
  if (new Set(plan.consumed).size !== plan.consumed.length || plan.consumed.includes(target.uid)) return false;
  const consumed = plan.consumed.map((uid) => byUid.get(uid));
  if (consumed.some((h) => !h)) return false;
  const others = consumed as Hero[];
  const def = heroDef(target.defId);
  const rule = RARITY_RULES[def.rarity];

  if (rule.fusion === 'triple') {
    return (
      plan.crystals === 0 &&
      others.length === TRIPLE_COUNT - 1 &&
      others.every((h) => h.defId === target.defId && h.stars === target.stars)
    );
  }

  const step = LADDER[plan.newStars];
  if (!step || plan.crystals !== step.crystals || crystalsOwned < step.crystals) return false;
  const copies = others.filter((h) => h.defId === target.defId && h.stars === rule.bornStars);
  // Une copie peut aussi compter comme héros de faction : on réserve d'abord les copies.
  const usedAsCopies = new Set(copies.slice(0, step.copies).map((h) => h.uid));
  if (usedAsCopies.size < step.copies) return false;
  const fodder = others.filter((h) => !usedAsCopies.has(h.uid));
  return (
    fodder.length === step.fodderCount &&
    fodder.every((h) => heroDef(h.defId).faction === def.faction && h.stars === step.fodderStars)
  );
}

/** Choisit automatiquement les héros à sacrifier (les moins précieux d'abord), ou null si impossible. */
export function planFusion(
  roster: readonly Hero[],
  targetUid: number,
  options: { protect?: ReadonlySet<number>; crystalsOwned?: number } = {},
): FusionPlan | null {
  const target = roster.find((h) => h.uid === targetUid);
  if (!target || !canGainStar(target)) return null;
  const protect = options.protect ?? new Set<number>();
  const def = heroDef(target.defId);
  const rule = RARITY_RULES[def.rarity];
  const free = roster.filter((h) => h.uid !== target.uid && !protect.has(h.uid));
  const byLevel = (a: Hero, b: Hero) => a.level - b.level;

  if (rule.fusion === 'triple') {
    const same = free.filter((h) => h.defId === target.defId && h.stars === target.stars).sort(byLevel);
    if (same.length < TRIPLE_COUNT - 1) return null;
    return { targetUid, consumed: same.slice(0, TRIPLE_COUNT - 1).map((h) => h.uid), crystals: 0, newStars: target.stars + 1 };
  }

  const newStars = target.stars + 1;
  const step = LADDER[newStars];
  if (!step || (options.crystalsOwned ?? 0) < step.crystals) return null;
  const copies = free.filter((h) => h.defId === target.defId && h.stars === rule.bornStars).sort(byLevel).slice(0, step.copies);
  if (copies.length < step.copies) return null;
  const copyIds = new Set(copies.map((h) => h.uid));
  const fodder = free
    .filter(
      (h) =>
        !copyIds.has(h.uid) &&
        h.stars === step.fodderStars &&
        heroDef(h.defId).faction === def.faction &&
        heroDef(h.defId).rarity !== 'legendary', // jamais un Légendaire en nourriture automatique
    )
    .sort((a, b) => RARITY_RANK[heroDef(a.defId).rarity] - RARITY_RANK[heroDef(b.defId).rarity] || byLevel(a, b))
    .slice(0, step.fodderCount);
  if (fodder.length < step.fodderCount) return null;
  return { targetUid, consumed: [...copyIds, ...fodder.map((h) => h.uid)], crystals: step.crystals, newStars };
}

/** Applique la fusion. Les niveaux et l'équipement des héros sacrifiés sont rendus en ressources. */
export function applyFusion(roster: readonly Hero[], plan: FusionPlan): { roster: Hero[]; refund: number } {
  const consumed = new Set(plan.consumed);
  let refund = 0;
  const next: Hero[] = [];
  for (const h of roster) {
    if (consumed.has(h.uid)) refund += levelRefund(h.level) + gearRefund(h.gear ?? 0);
    else next.push(h.uid === plan.targetUid ? { ...h, stars: plan.newStars } : h);
  }
  return { roster: next, refund };
}
