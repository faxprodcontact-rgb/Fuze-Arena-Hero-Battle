// Le tempo des coups HD au combat (sans affichage : hd-fight.ts s'en sert, et le script de mesure
// refonte-graphique/pixel/hd/anim/vitesse-attaques.ts aussi). Les durées des images viennent des GIF des animateurs
// (hd-meta.ts) ; le jeu les ralentit pour la course du corps à corps et le vol du projectile.
//
// Attaque de base (demande du propriétaire, 25/11/2026 : « tous les héros tapent à peu près à la même vitesse ») :
// chaque attaque de base est ramenée au même tempo au moment de la jouer, sans toucher aux planches ni aux règles.
// Le coup tombe vers EVEN.hit ms et tout est fini vers EVEN.total ms (course, vol et retour compris). Les images gardent
// leur rythme (elles sont toutes allongées ou raccourcies dans la même proportion, par phase) ; la récupération
// après le coup est raccourcie davantage que le coup lui-même ; aucune image ne descend sous EVEN.min ms ; la course et
// le vol gardent le temps qu'il leur faut. Les spéciales gardent leurs durées.

/** Ce qu'il faut d'une animation exportée pour régler son tempo. */
export interface TempoAnim {
  genre: string;
  ms: readonly number[];
  coup?: number;
  cible?: readonly number[];
  charge?: readonly number[];
  avance?: readonly number[];
  elan?: readonly number[];
  depart?: number;
  vitesse?: number;
  retour?: readonly number[];
  retourDe?: number;
}

/** Le tempo commun des attaques de base (ms à la vitesse ×1). */
export const EVEN = {
  /** le coup tombe (chiffre, recul) */
  hit: 440,
  /** tout est fini (le combat peut passer au coup suivant) */
  total: 980,
  /** une image ne dure jamais moins (sauf si l'animateur l'a faite plus courte) */
  min: 45,
  /** une attaque rapide est allongée au plus de… (pour ne pas la rendre molle) */
  slower: 1.25,
  /** une attaque lente est raccourcie au plus de… avant le coup (l'élan reste lisible) et après (la récupération) */
  faster: { pre: 0.45, post: 0.3 },
  /** corps à corps sans élan dessiné : part de la course du retour qui commence pendant la fin de la récupération */
  overlap: 0.6,
  /** le vol d'un projectile d'attaque de base (ms) */
  fly: [120, 380] as const,
};

const clamp = (x: number, a: number, b: number) => Math.min(b, Math.max(a, x));
const sum = (x: readonly number[], i0 = 0, i1 = x.length) => x.slice(i0, i1).reduce((s, m) => s + m, 0);

/**
 * Met une liste de durées au tempo commun. `fixed` : images qui gardent leur durée (course, vol) ; `extra` : temps
 * qui s'ajoute après l'animation (retour en courant, fin du coup). Deux phases : avant le coup (→ EVEN.hit), après le
 * coup (→ EVEN.total). Après le coup, l'image du coup et la suivante (l'impact) sont moins raccourcies que la
 * récupération.
 */
export function evenOut(ms: readonly number[], coup: number, sp: number, fixed: readonly boolean[] = [], extra = 0): number[] {
  const out = ms.slice();
  const min = EVEN.min / sp;
  const scalePhase = (idx: number[], target: number, gentle: (i: number) => boolean, floor: number) => {
    if (!idx.length) return;
    const at = (i: number, s: number) => Math.max(Math.min(ms[i]!, min), ms[i]! * (gentle(i) ? Math.sqrt(s) : s));
    const tot = (s: number) => idx.reduce((t, i) => t + at(i, s), 0);
    let lo = floor, hi = EVEN.slower;
    if (tot(hi) <= target) lo = hi;
    else if (tot(lo) >= target) hi = lo;
    for (let n = 0; n < 40 && hi - lo > 1e-4; n++) {
      const mid = (lo + hi) / 2;
      if (tot(mid) < target) lo = mid;
      else hi = mid;
    }
    const s = (lo + hi) / 2;
    idx.forEach((i) => { out[i] = at(i, s); });
  };
  const free = (i: number) => !fixed[i];
  const pre = ms.map((_, i) => i).filter((i) => i < coup && free(i));
  const post = ms.map((_, i) => i).filter((i) => i >= coup && free(i));
  const preFixed = sum(ms.filter((_, i) => i < coup && !free(i)));
  const postFixed = sum(ms.filter((_, i) => i >= coup && !free(i))) + extra;
  scalePhase(pre, EVEN.hit / sp - preFixed, () => false, EVEN.faster.pre);
  // le coup peut tomber plus tard que prévu (course longue, image courte déjà au minimum) : la fin suit
  const hit = sum(out, 0, coup);
  scalePhase(post, Math.max(EVEN.total / sp - hit, 0) - postFixed, (i) => i <= coup + 1, EVEN.faster.post);
  return out;
}

/** Le corps à corps : durées des images, course de retour après l'animation (ms réelles), façon de se déplacer. */
export interface MeleeTempo { ms: number[]; back: number; overlap: number; hop: boolean; e0: number; e1: number }

/**
 * Corps à corps : `dist` = la distance jusqu'à la case d'où il frappe (unités du jeu). Les images où il se déplace
 * sont allongées si elles sont trop courtes pour cette distance. `even` : attaque de base (tempo commun).
 */
export function meleeTempo(a: TempoAnim, dist: number, sp: number, even: boolean): MeleeTempo {
  const coup = a.coup ?? 0;
  const av = a.avance;
  const hop = !av || Math.max(...av) <= 3;
  const [e0, e1] = (a.elan ?? [a.charge ? a.charge[1]! + 1 : 0, coup]) as [number, number];
  const back = hop ? Math.max(200, dist / 1.5) / sp : 0;
  // attaque de base : il repart pendant la fin de sa récupération (au plus jusqu'à l'image qui suit le coup)
  const overlapOf = (ms: number[]) => (even && back ? Math.min(back * EVEN.overlap, sum(ms, coup + 2)) : 0);
  /** Allonge les images du déplacement trop courtes pour la distance ; renvoie celles qui ont été allongées. */
  const stretch = (ms: number[]): boolean[] => {
    const fixed = ms.map(() => false);
    if (!hop) {
      const f = av!.map((x) => clamp(x / Math.max(1, av![coup]!), 0, 1));
      const moving = ms.map((_, i) => Math.abs((f[i + 1] ?? 0) - f[i]!) > 0.01);
      const go = ms.reduce((s, m, i) => s + (moving[i] && i < coup ? m : 0), 0);
      const ret = ms.reduce((s, m, i) => s + (moving[i] && i >= coup ? m : 0), 0);
      const needGo = dist / 1.6 / sp, needRet = dist / 1.3 / sp;
      ms.forEach((m, i) => {
        if (moving[i] && i < coup && go < needGo) { ms[i] = (m * needGo) / go; fixed[i] = true; }
        if (moving[i] && i >= coup && ret > 0 && ret < needRet) { ms[i] = (m * needRet) / ret; fixed[i] = true; }
      });
    } else {
      const go = sum(ms, e0, e1);
      const need = Math.max(160, dist / 1.4) / sp;
      if (go < need) for (let i = e0; i < e1; i++) { ms[i] = (ms[i]! * need) / Math.max(1, go); fixed[i] = true; }
    }
    return fixed;
  };
  let ms = a.ms.map((m) => m / sp);
  if (even) ms = evenOut(ms, coup, sp, [], back * (1 - EVEN.overlap));
  const fixed = stretch(ms);
  if (even && fixed.some(Boolean)) ms = evenOut(ms, coup, sp, fixed, back * (1 - EVEN.overlap));
  return { ms, back, overlap: overlapOf(ms), hop, e0, e1 };
}

/**
 * Tir : `fly` = le temps du vol jusqu'à la première cible (ms réelles, d'après la distance et la vitesse du
 * projectile). Les images du vol durent le temps du vol ; l'arme qui revient (boomerang) met le même temps.
 * Renvoie les durées et le vol (raccourci pour une attaque de base trop lente).
 */
export function tirTempo(a: TempoAnim, fly: number, sp: number, even: boolean): { ms: number[]; fly: number } {
  const coup = a.coup ?? 0;
  const dep = a.depart ?? 0;
  if (even) fly = clamp(fly, EVEN.fly[0] / sp, EVEN.fly[1] / sp);
  const fixed: boolean[] = [];
  const retime = (ms: number[], i0: number, i1: number, dur: number) => {
    const was = sum(ms, i0, i1);
    if (was > 0) for (let i = i0; i < i1; i++) { ms[i] = Math.max(16, (ms[i]! * dur) / was); fixed[i] = true; }
  };
  const ret = a.retour, r0 = a.retourDe ?? 0;
  const place = (ms: number[]) => {
    retime(ms, dep, coup, fly);
    if (ret) retime(ms, r0, r0 + ret.length, fly);
    return ms;
  };
  const ms = place(a.ms.map((m) => m / sp));
  // sans impact dessiné, le coup finit 220 ms après l'arrivée ; puis 100 ms de battement (hdStrike)
  const tail = (a.cible ? 0 : Math.max(0, 220 / sp - sum(ms, coup))) + 100 / sp;
  return { ms: even ? evenOut(ms, coup, sp, fixed, tail) : ms, fly };
}

/** Sort, rayon, sort d'équipe : il lance sur place. */
export function plainTempo(a: TempoAnim, sp: number, even: boolean): number[] {
  const ms = a.ms.map((m) => m / sp);
  return even ? evenOut(ms, a.coup ?? 0, sp) : ms;
}
