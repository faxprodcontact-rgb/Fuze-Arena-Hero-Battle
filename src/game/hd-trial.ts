// Combat d'essai HD : un scénario qui fait jouer à chacun son attaque puis sa spéciale, sur des cases variées (le
// fond en bas à droite compris), pour tout montrer : corps à corps jusqu'à la cible, tirs jusqu'à la vraie case,
// charges, sorts d'équipe. Les règles ne tournent pas : les chiffres sont plausibles et personne ne tombe (la vie
// remonte dès qu'elle est basse). Mode « tous » : à la fin d'une manche, les équipes suivantes entrent.
import type { Battle } from '../core/battle/engine';
import type { BattleEvent, Hit, Slot, Unit } from '../core/battle/types';

type Which = 'attaque' | 'speciale';
type Step = { src: Unit; kind: Which; n: number };

export interface HdTrialHost {
  battle: Battle;
  /** Le genre de l'animation HD d'un combattant (melee, tir, sort, rayon, equipe). */
  genre(u: Unit, which: Which): string | undefined;
  /** Nombre de manches (1 : on rejoue la même, avec d'autres cibles). */
  rounds: number;
  /** Fait entrer les équipes de la manche `r` (les héros tout de suite) ; renvoie les nouveaux ennemis. */
  nextRound(r: number): Unit[];
}

/** L'ordre des cibles : le fond en bas d'abord (le plus loin), puis devant, le fond en haut, le milieu, devant en bas. */
const TARGET_ORDER: Slot[] = [4, 0, 3, 2, 1];

/** Le journal des coups joués (heure, lanceur, coup, cibles) : lu par les outils de contrôle (captures du combat). */
export const hdTrialLog: { t: number; src: string; kind: Which; targets: string[] }[] = [];

const bySlot = (us: Unit[]) => us.slice().sort((a, b) => TARGET_ORDER.indexOf(a.slot) - TARGET_ORDER.indexOf(b.slot));

export function hdTrialScript(host: HdTrialHost): () => BattleEvent[] {
  let round = 0;
  let loop = 0;
  let steps: Step[] = [];
  let k = 0;
  const plan = () => {
    // chacun son attaque (héros et ennemis en alternance), puis chacun sa spéciale
    const b = host.battle;
    const hs = bySlot(b.heroes), es = bySlot(b.enemies);
    steps = [];
    for (const kind of ['attaque', 'speciale'] as const) {
      for (let n = 0; n < Math.max(hs.length, es.length); n++) {
        if (hs[n]) steps.push({ src: hs[n]!, kind, n });
        if (es[n]) steps.push({ src: es[n]!, kind, n });
      }
    }
    k = 0;
  };
  plan();
  return () => {
    const b = host.battle;
    if (k >= steps.length) {
      loop += 1;
      if (host.rounds > 1) {
        round = (round + 1) % host.rounds;
        const units = host.nextRound(round);
        plan();
        return [{ type: 'wave', index: round, units }];
      }
      plan();
    }
    const { src, kind, n } = steps[k++]!;
    // personne ne tombe : la vie basse remonte avant le coup suivant
    for (const u of [...b.heroes, ...b.enemies]) if (u.hp < u.maxHp * 0.35) u.hp = u.maxHp;
    const genre = host.genre(src, kind);
    const team = kind === 'speciale' && (genre === 'equipe' || src.skill.effects.every((e) => e.type !== 'damage'));
    const allies = (src.side === 'hero' ? b.heroes : b.enemies).slice().sort((a, c) => a.slot - c.slot);
    const foes = bySlot(src.side === 'hero' ? b.enemies : b.heroes);
    let targets: Unit[];
    if (team) targets = allies;
    else if (!foes.length) return [];
    else {
      // une case différente pour chacun (et d'un tour à l'autre) ; la spéciale vise ailleurs que l'attaque
      const i = (n + loop + (kind === 'speciale' ? 2 : 0)) % foes.length;
      const main = foes[i]!;
      if (kind === 'attaque' || genre === 'melee' || genre === 'rayon') targets = [main];
      else if (genre === 'sort') targets = [main, ...foes.filter((f) => f !== main)];
      else targets = [main, foes[(i + 1) % foes.length]!].filter((u, j, a) => a.indexOf(u) === j);
    }
    hdTrialLog.push({ t: Date.now(), src: src.id, kind, targets: targets.map((u) => u.id) });
    const hits: Hit[] = targets.map((t, j) => {
      if (team) {
        const amount = Math.round(t.maxHp * 0.18);
        t.hp = Math.min(t.maxHp, t.hp + amount);
        return { target: t.id, amount, kind: 'heal' };
      }
      const crit = (k + j) % 4 === 0;
      const amount = Math.round(t.maxHp * (kind === 'speciale' ? 0.12 : 0.05) * (crit ? 1.6 : 1) * (0.9 + ((k * 7 + j * 3) % 5) * 0.05));
      t.hp = Math.max(Math.round(t.maxHp * 0.2), t.hp - amount);
      return { target: t.id, amount, kind: 'damage', crit };
    });
    if (kind === 'attaque') return hits.map((hit) => ({ type: 'attack', source: src.id, hit }));
    return [{ type: 'skill', source: src.id, skill: src.skill, hits }];
  };
}
