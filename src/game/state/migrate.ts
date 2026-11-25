// Vieilles sauvegardes : les 36 héros retirés du jeu (le 25/11/2026, on ne garde que les héros dessinés en HD).
// Chaque héros retiré est échangé contre un dédommagement envoyé par courrier (message `heros-retires-2611`) :
// des parchemins selon sa rareté et ses étoiles, ses niveaux et l'équipement renforcé rendus, ses objets remis au sac.
// Les sections, les adversaires et les amis qui le montraient sont nettoyés. Rien ne plante si tout est déjà propre.
import { RETIRED_HEROES, heroesOfElement, isHero } from '../../core/data/heroes';
import { GEAR_SLOTS, slotUpgradeCost } from '../../core/data/items';
import { ESSENCE_RATIO, type Reward } from '../../core/data/modes';
import { FRAGMENTS_PER_COPY, LADDER, MYTHIC_STARS, RARITY_RULES } from '../../core/data/stars';
import { levelRefund } from '../../core/power';
import type { Hero, Rarity } from '../../core/types';
import type { PlayerState } from './types';

export const RETIRED_MAIL = 'heros-retires-2611';

/** Ce que vaut une copie (telle qu'elle sort de l'invocation) d'un héros retiré. */
const PER_COPY: Record<Rarity, Reward> = {
  common: { basicScrolls: 1 },
  rare: { basicScrolls: 3 },
  epic: { scrolls: 5 },
  legendary: { scrolls: 20 },
};

/** Nombre de copies du même héros qu'il a fallu pour l'amener à ses étoiles (les héros sacrifiés à côté ne comptent pas). */
export function copiesFor(rarity: Rarity, stars: number): number {
  const rule = RARITY_RULES[rarity];
  const s = Math.min(rule.maxStars, Math.max(rule.bornStars, stars));
  if (rule.fusion === 'triple') return 3 ** (s - rule.bornStars);
  let n = 1;
  for (let k = rule.bornStars + 1; k <= s; k++) n += LADDER[k]?.copies ?? 0;
  return n;
}

function add(r: Reward, k: keyof Reward, v: number) {
  if (v > 0) r[k] = (r[k] ?? 0) + Math.round(v);
}

/** Un héros d'équipe adverse (arène, amis) retiré : remplacé par un héros gardé du même élément et de la même rareté. */
function stand(defId: string): string {
  const old = RETIRED_HEROES.get(defId);
  if (!old) return defId;
  return heroesOfElement(old.element, old.rarity)[0]?.id ?? heroesOfElement(old.element, 'epic')[0]!.id;
}

/**
 * Retire les héros qui ne sont plus dans le jeu et prépare leur dédommagement (le courrier le fait arriver).
 * Modifie `s` et le renvoie.
 */
export function retireHeroes(s: PlayerState): PlayerState {
  const gone = s.heroes.filter((h) => !isHero(h.defId));
  const reward: Reward = {};
  for (const h of gone) compensate(s, h, reward);
  // les fragments d'un Légendaire retiré : leur part de parchemins
  for (const [defId, n] of Object.entries(s.fragments ?? {})) {
    if (isHero(defId)) continue;
    if (RETIRED_HEROES.has(defId)) add(reward, 'scrolls', ((PER_COPY.legendary.scrolls ?? 0) * n) / FRAGMENTS_PER_COPY);
    delete s.fragments[defId];
  }
  if (s.fragmentTarget && !isHero(s.fragmentTarget)) delete s.fragmentTarget;

  const goneUids = new Set(gone.map((h) => h.uid));
  s.heroes = s.heroes.filter((h) => !goneUids.has(h.uid));
  s.discovered = (s.discovered ?? []).filter(isHero);
  for (const h of s.heroes) if (!s.discovered.includes(h.defId)) s.discovered.push(h.defId);
  s.formation = (s.formation ?? []).filter(([uid]) => !goneUids.has(uid));
  if (!s.formation.length && s.heroes.length) s.formation = [[s.heroes[0]!.uid, 2]];
  if (s.defenseTeam) s.defenseTeam = s.defenseTeam.filter(([uid]) => !goneUids.has(uid));
  for (const m of s.daily?.missions ?? []) m.heroUids = m.heroUids.filter((uid) => !goneUids.has(uid));
  for (const o of s.arena?.opponents ?? []) for (const m of o.team) m.defId = stand(m.defId);
  for (const f of s.friends?.list ?? []) for (const m of f.team) m.defId = stand(m.defId);

  if (Object.keys(reward).length) {
    const box = (s.mail ??= { got: {}, read: [], claimed: [] });
    // une seule fois : si le message a déjà été envoyé, le nouveau cadeau s'y ajoute (il n'a pas encore été pris)
    const prev = box.claimed.includes(RETIRED_MAIL) ? undefined : box.personal?.[RETIRED_MAIL];
    const total: Reward = { ...prev };
    for (const [k, v] of Object.entries(reward)) add(total, k as keyof Reward, v ?? 0);
    box.personal = { ...box.personal, [RETIRED_MAIL]: total };
    if (box.claimed.includes(RETIRED_MAIL)) {
      box.claimed = box.claimed.filter((id) => id !== RETIRED_MAIL);
      box.read = box.read.filter((id) => id !== RETIRED_MAIL);
      delete box.got[RETIRED_MAIL];
    }
  }
  return s;
}

/** Le dédommagement d'un héros retiré : ses copies en parchemins, ses niveaux et ses emplacements renforcés, ses objets au sac. */
function compensate(s: PlayerState, h: Hero, reward: Reward) {
  const rarity = RETIRED_HEROES.get(h.defId)?.rarity ?? 'common';
  const copies = copiesFor(rarity, h.stars);
  for (const [k, v] of Object.entries(PER_COPY[rarity])) add(reward, k as keyof Reward, (v ?? 0) * copies);
  if (h.stars >= MYTHIC_STARS) add(reward, 'crystals', LADDER[MYTHIC_STARS]!.crystals);
  const gold = levelRefund(h.level);
  add(reward, 'gold', gold);
  add(reward, 'essence', gold * ESSENCE_RATIO);
  const levels = s.slotLevels?.[h.uid] ?? {};
  for (const slot of GEAR_SLOTS) {
    for (let l = 0; l < (levels[slot] ?? 0); l++) {
      const cost = slotUpgradeCost(l);
      add(reward, 'gold', cost.gold);
      add(reward, 'dust', cost.dust);
    }
  }
  if (s.slotLevels) delete s.slotLevels[h.uid];
  for (const it of s.items ?? []) if (it.heroUid === h.uid) delete it.heroUid;
}
