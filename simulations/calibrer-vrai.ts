// Règle la difficulté de la campagne (CAMPAIGN_ANCHORS de src/core/data/campaign.ts) sur le VRAI jeu (28/11/2026) :
// le joueur de référence (3 × 20 min par jour, sans rien acheter : simulations/vrai-jeu.ts) doit atteindre chaque niveau
// visé au jour visé. À chaque passe, la puissance demandée à un niveau visé devient celle que le joueur avait ce jour-là
// (moyenne géométrique avec l'ancienne, pour converger en douceur). Afficher les points d'ancrage, à recopier.
//   npx tsx simulations/calibrer-vrai.ts [passes] [graines]
import { CAMPAIGN_ANCHORS } from '../src/core/data/campaign';
import { RealPlayer } from './vrai-jeu';

/** [jour (0 = premier jour), niveau de campagne visé à la fin de ce jour] : tout le jeu en 5 à 7 mois. */
export const TARGETS: [number, number][] = [
  [0, 150], [2, 260], [6, 380], [13, 500], [29, 680], [59, 860], [89, 980], [119, 1070], [149, 1140], [174, 1200],
];

const passes = Number(process.argv[2] ?? 6);
const seeds = Number(process.argv[3] ?? 3);
const days = TARGETS.at(-1)![0] + 6;

// les points d'ancrage : le 1er niveau, le 15e (la première demi-heure), puis un point par niveau visé
const start = CAMPAIGN_ANCHORS.filter((a) => a.stage <= 15);
const fresh = [...start, ...TARGETS.map(([, stage]) => ({ stage, power: 0 }))];
// valeur de départ : la courbe actuelle
const curve0 = fresh.map((a) => ({ ...a }));
{
  const { stagePower } = await import('../src/core/data/campaign');
  for (const a of curve0) if (!a.power) a.power = Math.round(stagePower(a.stage));
}
CAMPAIGN_ANCHORS.splice(0, CAMPAIGN_ANCHORS.length, ...curve0);

const median = (xs: number[]) => [...xs].sort((a, b) => a - b)[Math.floor(xs.length / 2)]!;

for (let pass = 1; pass <= passes; pass++) {
  const runs = Array.from({ length: seeds }, (_, i) => new RealPlayer('regulier', i + 1).run(days));
  const line: string[] = [];
  for (const [day, stage] of TARGETS) {
    const reached = median(runs.map((r) => r.days[day]!.stage));
    const power = median(runs.map((r) => r.days[day]!.power));
    const a = CAMPAIGN_ANCHORS.find((x) => x.stage === stage)!;
    a.power = Math.round(Math.sqrt(a.power * power));
    line.push(`j${day + 1}:${reached}/${stage}`);
  }
  // la courbe doit monter
  for (let i = 1; i < CAMPAIGN_ANCHORS.length; i++) {
    const prev = CAMPAIGN_ANCHORS[i - 1]!;
    if (CAMPAIGN_ANCHORS[i]!.power <= prev.power) CAMPAIGN_ANCHORS[i]!.power = Math.round(prev.power * 1.05);
  }
  // la plus longue série de jours sans gagner un niveau de campagne (un « mur »), avant la fin de la campagne
  const wall = median(runs.map((r) => {
    let best = 0, cur = 0, at = 0;
    for (let i = 1; i < r.days.length; i++) {
      if (r.days[i]!.stage === r.days[i - 1]!.stage && r.days[i]!.stage < 1200) { cur++; if (cur > best) { best = cur; at = r.days[i]!.stage; } } else cur = 0;
    }
    return best * 10000 + at;
  }));
  line.push(`mur ${Math.floor(wall / 10000)} j au niveau ${wall % 10000}`);
  const m = runs.map((r) => r.milestones);
  const ms = (k: keyof (typeof m)[0]) => median(m.map((x) => x[k] ?? 999)) + 1;
  console.log(`  ancres : ${CAMPAIGN_ANCHORS.map((x) => `${x.stage}:${x.power}`).join(' ')}`);
  console.log(`passe ${pass} : ${line.join(' ')} | ★5 j${ms('star5')} rouge j${ms('red1')} section rouge j${ms('teamRed')} ★5 rouge j${ms('red5')} Mythique j${ms('mythic')} fin j${ms('campaignEnd')}`);
}
console.log('export const CAMPAIGN_ANCHORS: Anchor[] = [');
for (const a of CAMPAIGN_ANCHORS) console.log(`  { stage: ${a.stage}, power: ${a.power} },`);
console.log('];');
