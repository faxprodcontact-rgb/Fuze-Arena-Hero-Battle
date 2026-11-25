// Combat d'essai HD : un scénario qui fait jouer à chacun ses deux attaques, sur des cibles choisies pour tout
// montrer (corps à corps jusqu'au fond, tir sur la case du fond en bas à droite, charges, sort d'équipe).
// Les règles ne tournent pas : les chiffres sont plausibles, personne ne tombe (la vie remonte à chaque tour).
import type { Battle } from '../core/battle/engine';
import type { BattleEvent, Hit, Slot, Unit } from '../core/battle/types';

type Step = [side: 'hero' | 'enemy', slot: Slot, kind: 'attaque' | 'speciale', targets: Slot[]];

// héros : 0 Eldra (corps à corps), 2 Myrr (soigneuse), 4 Jinn (archer) ; ennemis : 0 matelot, 2 sorcier oni, 4 salamandre
const STEPS: Step[] = [
  ['hero', 0, 'attaque', [0]],          // Eldra frappe le matelot (devant)
  ['enemy', 0, 'attaque', [0]],         // le matelot fond sur Eldra
  ['hero', 4, 'attaque', [4]],          // Jinn tire sur la salamandre (au fond, en bas à droite)
  ['enemy', 4, 'attaque', [4]],         // la salamandre crache sur Jinn (au fond, en bas à gauche)
  ['hero', 2, 'attaque', [2]],          // Myrr souffle sur le sorcier (milieu)
  ['enemy', 2, 'attaque', [2]],         // le sorcier lance son feu follet sur Myrr
  ['hero', 0, 'attaque', [4]],          // Eldra va jusqu'au fond frapper la salamandre
  ['hero', 0, 'speciale', [0]],         // spéciale d'Eldra (charge, bond, onde)
  ['enemy', 2, 'speciale', [4]],        // spéciale du sorcier sur Jinn (charge, trois feux follets)
  ['hero', 4, 'speciale', [0, 2, 4]],   // spéciale de Jinn : la volée retombe sur les trois
  ['enemy', 0, 'speciale', [2]],        // spéciale du matelot sur Myrr (vague)
  ['enemy', 4, 'speciale', [0]],        // spéciale de la salamandre : le souffle de feu jusqu'à Eldra
  ['hero', 2, 'speciale', [0, 2, 4]],   // spéciale de Myrr : soin, purification et énergie sur toute l'équipe
  ['hero', 4, 'attaque', [2]],          // Jinn tire sur le sorcier (milieu)
];

export function hdTrialScript(b: Battle): () => BattleEvent[] {
  let step = 0;
  const find = (side: 'hero' | 'enemy', slot: Slot): Unit | undefined => (side === 'hero' ? b.heroes : b.enemies).find((u) => u.slot === slot);
  return () => {
    const [side, slot, kind, slots] = STEPS[step % STEPS.length]!;
    // au début de chaque tour du scénario, tout le monde reprend sa vie
    if (step % STEPS.length === 0) for (const u of [...b.heroes, ...b.enemies]) u.hp = u.maxHp;
    step += 1;
    const src = find(side, slot);
    if (!src) return [];
    const team = kind === 'speciale' && src.skill.effects.every((e) => e.type !== 'damage');
    const targets = slots.map((s) => find(team ? side : side === 'hero' ? 'enemy' : 'hero', s)).filter((u): u is Unit => !!u);
    const hits: Hit[] = targets.map((t, i) => {
      if (team) {
        const amount = Math.round(t.maxHp * 0.18);
        t.hp = Math.min(t.maxHp, t.hp + amount);
        return { target: t.id, amount, kind: 'heal' };
      }
      const crit = (step + i) % 4 === 0;
      const amount = Math.round(t.maxHp * (kind === 'speciale' ? 0.12 : 0.05) * (crit ? 1.6 : 1) * (0.9 + ((step * 7 + i * 3) % 5) * 0.05));
      t.hp = Math.max(Math.round(t.maxHp * 0.2), t.hp - amount);
      return { target: t.id, amount, kind: 'damage', crit };
    });
    if (kind === 'attaque') return hits.map((hit) => ({ type: 'attack', source: src.id, hit }));
    return [{ type: 'skill', source: src.id, skill: src.skill, hits }];
  };
}
