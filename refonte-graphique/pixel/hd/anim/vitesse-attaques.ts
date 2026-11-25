// Mesure la durée des attaques de base HD telles que le jeu les joue (src/game/hd-tempo.ts, hd-fight.ts) : avant
// (durées des GIF, course et vol) et après le tempo commun. Écrit refonte-graphique/pixel/sortie/vitesse-attaques.md.
//   npx tsx refonte-graphique/pixel/hd/anim/vitesse-attaques.ts        (depuis la racine du dépôt)
import { writeFileSync } from 'node:fs';
import { HD_ANIM } from '../../../../src/game/hd-meta';
import { EVEN, meleeTempo, plainTempo, tirTempo, type TempoAnim } from '../../../../src/game/hd-tempo';

type A = TempoAnim & { portee?: number; haut?: number; bouche?: readonly number[] };
const CHARS = HD_ANIM.chars as unknown as Record<string, { name: string; anims: { attaque: A; speciale: A } }>;
const K = HD_ANIM.scale;
const sum = (x: readonly number[], i0 = 0, i1 = x.length) => x.slice(i0, i1).reduce((s, m) => s + m, 0);

/** Les cases du combat (fight-view.ts) : x des pieds ; la même rangée pour les deux. */
const FRONT = { from: 245, to: 475 };
const FAR = { from: 82, to: 638 };
const BIG_BOSS_X = 548;

/** Le coup tel que hdStrike le joue : [moment du coup, durée totale] en ms (vitesse ×1, sans la pause commune de 260 ms). */
function play(a: A, from: number, to: number, even: boolean): [number, number] {
  const coup = a.coup ?? 0;
  const d = Math.abs(to - from);
  if (a.genre === 'melee') {
    const reach = Math.max(56, ((a.portee ?? 100) - (a.avance ? a.avance[coup]! : 0)) * K);
    const t = meleeTempo(a, Math.max(0, d - reach), 1, even);
    return [sum(t.ms, 0, coup), sum(t.ms) + t.back - t.overlap];
  }
  if (a.genre === 'tir') {
    const b = a.bouche!;
    const dx = d - 8 - b[0]! * K, dy = (-(a.haut ?? 40) - b[1]!) * K;
    const fly0 = Math.min(650, Math.max(140, (Math.hypot(dx, dy) / Math.max(60, (a.vitesse ?? 400) * K)) * 1000));
    const { ms, fly } = tirTempo(a, fly0, 1, even);
    const hit = sum(ms, 0, a.depart ?? 0) + fly;
    const after = a.cible ? sum(ms, coup) : 220;
    return [hit, Math.max(sum(ms), hit + after) + 100];
  }
  const ms = plainTempo(a, 1, even);
  return [sum(ms, 0, coup), sum(ms)];
}

const kind = (id: string) => (id.startsWith('boss-') ? 'grand boss' : id.startsWith('mon-') ? 'monstre' : 'héros');
const genre: Record<string, string> = { melee: 'corps à corps', tir: 'tir', sort: 'sort', rayon: 'rayon', equipe: 'équipe' };
const rows = Object.entries(CHARS).map(([id, ch]) => {
  const a = ch.anims.attaque;
  const g = id.startsWith('boss-') ? { from: BIG_BOSS_X, to: FRONT.from } : FRONT;
  const far = id.startsWith('boss-') ? { from: BIG_BOSS_X, to: FAR.from } : FAR;
  return { id, name: ch.name, kind: kind(id), genre: genre[a.genre] ?? a.genre, before: play(a, g.from, g.to, false), after: play(a, g.from, g.to, true),
    beforeFar: play(a, far.from, far.to, false), afterFar: play(a, far.from, far.to, true), special: sum(ch.anims.speciale.ms) };
});
const order = ['héros', 'monstre', 'grand boss'];
rows.sort((p, q) => order.indexOf(p.kind) - order.indexOf(q.kind) || q.before[1] - p.before[1]);
const s = (x: number) => (x / 1000).toFixed(2).replace('.', ',');
const stats = (xs: number[]) => `${s(Math.min(...xs))} à ${s(Math.max(...xs))} s (moyenne ${s(sum(xs) / xs.length)})`;

const out: string[] = [];
out.push('# Vitesse des attaques de base (personnages HD)', '');
out.push(`Mesuré par \`npx tsx refonte-graphique/pixel/hd/anim/vitesse-attaques.ts\` sur les vraies règles du jeu (\`src/game/hd-tempo.ts\`), à la vitesse ×1, sans la petite pause commune de 0,26 s entre deux coups. « Coup » = le moment où le chiffre s'affiche ; « fin » = quand le combat peut passer au coup suivant (course, vol et retour compris).`, '');
out.push(`Cases : un personnage du premier rang qui frappe l'ennemi du premier rang (x ${FRONT.from} → ${FRONT.to}) ; « du fond » : dernier rang contre dernier rang (x ${FAR.from} → ${FAR.to}). Grand boss : depuis le milieu (x ${BIG_BOSS_X}).`, '');
out.push(`Tempo commun (\`EVEN\`) : coup vers ${s(EVEN.hit)} s, fin vers ${s(EVEN.total)} s ; aucune image sous ${EVEN.min} ms ; une attaque rapide est allongée au plus de ×${EVEN.slower} ; vol d'un projectile entre ${s(EVEN.fly[0])} et ${s(EVEN.fly[1])} s. Les spéciales ne changent pas.`, '');
out.push('## Résumé', '');
out.push('| | coup | fin |', '|---|---|---|');
out.push(`| avant (premier rang) | ${stats(rows.map((r) => r.before[0]))} | ${stats(rows.map((r) => r.before[1]))} |`);
out.push(`| après (premier rang) | ${stats(rows.map((r) => r.after[0]))} | ${stats(rows.map((r) => r.after[1]))} |`);
out.push(`| avant (du fond) | ${stats(rows.map((r) => r.beforeFar[0]))} | ${stats(rows.map((r) => r.beforeFar[1]))} |`);
out.push(`| après (du fond) | ${stats(rows.map((r) => r.afterFar[0]))} | ${stats(rows.map((r) => r.afterFar[1]))} |`, '');
out.push('## Chaque personnage (secondes)', '');
out.push('| personnage | id | sorte | attaque | avant : coup / fin | après : coup / fin | du fond, après | spéciale (images) |', '|---|---|---|---|---|---|---|---|');
for (const r of rows) {
  out.push(`| ${r.name} | \`${r.id}\` | ${r.kind} | ${r.genre} | ${s(r.before[0])} / **${s(r.before[1])}** | ${s(r.after[0])} / **${s(r.after[1])}** | ${s(r.afterFar[0])} / ${s(r.afterFar[1])} | ${s(r.special)} |`);
}
out.push('');
writeFileSync(new URL('../../sortie/vitesse-attaques.md', import.meta.url), out.join('\n'));
console.log(out.slice(0, 14).join('\n'));
