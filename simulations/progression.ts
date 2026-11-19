// Simulations de progression.
//   npm run simuler                 → rapport (plusieurs joueurs, plusieurs tirages)
//   npm run simuler -- --calibrer   → recalcule les points d'ancrage de la campagne
import { mkdirSync, writeFileSync } from 'node:fs';
import { CAMPAIGN_ANCHORS, curveFromAnchors, type Anchor } from '../src/core/data/campaign';
import { starLabel } from '../src/core/data/stars';
import { PlayerSim, type Milestone, type Profile } from './model';
import { PROFILES, REGULAR } from './profiles';

const DAYS = 300;
const SEEDS = 30;
const CALIBRATION_SEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

/** Rythme visé pour le joueur régulier (cahier de conception, partie Progression). */
const TARGETS: { label: string; hours: number; stage: number }[] = [
  { label: '10 premières minutes', hours: 0, stage: 15 },
  { label: 'Jour 1', hours: 24 - 0.01, stage: 120 },
  { label: 'Semaine 1', hours: 7 * 24 - 0.01, stage: 360 },
  { label: 'Mois 1', hours: 30 * 24 - 0.01, stage: 700 },
  { label: 'Mois 2', hours: 60 * 24 - 0.01, stage: 900 },
  { label: 'Mois 4', hours: 120 * 24 - 0.01, stage: 1080 },
  { label: 'Mois 6,5 : fin de la campagne', hours: 200 * 24 - 0.01, stage: 1200 },
];

const MILESTONES: { id: Milestone; label: string; target: string }[] = [
  { id: 'legendary', label: 'Premier Légendaire', target: 'jour 1' },
  { id: 'star5', label: 'Premier héros ★5', target: 'semaine 2' },
  { id: 'red1', label: 'Première étoile rouge', target: 'mois 2' },
  { id: 'teamRed', label: 'Section entière en étoiles rouges', target: 'mois 4' },
  { id: 'red5', label: 'Premier ★5 rouge', target: 'mois 5,5' },
  { id: 'mythic', label: 'Premier Mythique', target: 'mois 6' },
  { id: 'campaignEnd', label: 'Fin de la campagne', target: 'mois 6,5' },
  { id: 'teamMythic', label: 'Section entière Mythique', target: 'mois 7' },
];

function stageAt(profile: Profile, anchors: Anchor[], hours: number, seed: number): number {
  const sim = new PlayerSim(profile, curveFromAnchors(anchors), seed);
  sim.run(Math.ceil((hours + 1) / 24), hours);
  return sim.stage;
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)] ?? NaN;
}

function quantile(values: number[], q: number): number {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor(q * sorted.length))] ?? NaN;
}

/**
 * Pour chaque objectif, dans l'ordre : cherche la puissance la plus haute du point d'ancrage
 * qui laisse encore le joueur médian atteindre le niveau visé à temps.
 */
function calibrate(): Anchor[] {
  const anchors: Anchor[] = [CAMPAIGN_ANCHORS[0]!];
  for (const target of TARGETS) {
    let lo = Math.log(anchors[anchors.length - 1]!.power);
    let hi = lo + Math.log(1000);
    for (let i = 0; i < 22; i++) {
      const mid = (lo + hi) / 2;
      const trial = [...anchors, { stage: target.stage, power: Math.exp(mid) }];
      const stages = CALIBRATION_SEEDS.map((seed) => stageAt(REGULAR, trial, target.hours, seed));
      if (median(stages) >= target.stage) lo = mid;
      else hi = mid;
    }
    anchors.push({ stage: target.stage, power: Math.round(Math.exp(lo)) });
    console.log(`  ${target.label} : niveau ${target.stage} → puissance ${Math.round(Math.exp(lo))}`);
  }
  return anchors;
}

function fmtDay(d: number | undefined): string {
  if (d === undefined) return 'jamais';
  if (d < 1) return `${Math.round(d * 24)} h`;
  return `jour ${Math.round(d)}`;
}

function report(anchors: Anchor[]): void {
  const curve = curveFromAnchors(anchors);
  const out: Record<string, unknown> = { anchors };
  for (const profile of PROFILES) {
    const sims = Array.from({ length: SEEDS }, (_, i) => new PlayerSim(profile, curve, 1000 + i).run(DAYS));
    console.log(`\n=== ${profile.label} (${SEEDS} joueurs, ${DAYS} jours) ===`);

    const rows: string[] = [];
    rows.push(`  10 premières minutes : niveau ${median(sims.map((s) => s.stageAfterFirstSession))}`);
    for (const day of [0, 6, 29, 59, 119, 199, DAYS - 1]) {
      const stages = sims.map((s) => s.days[day]!.stage);
      const ref = sims[0]!.days[day]!;
      const levels = sims.map((s) => median(s.days[day]!.teamLevels));
      const gear = sims.map((s) => median(s.days[day]!.teamGear));
      rows.push(
        `  Jour ${day + 1} : niveau ${median(stages)} (${quantile(stages, 0.1)}–${quantile(stages, 0.9)}), ` +
          `section ${ref.teamStars.map(starLabel).join(' ')}, niveau des héros ≈ ${median(levels)}, équipement ≈ ${median(gear)}`,
      );
    }
    console.log(rows.join('\n'));

    console.log('  Étapes :');
    const milestoneOut: Record<string, unknown> = {};
    for (const m of MILESTONES) {
      const days = sims.map((s) => s.milestones[m.id] ?? Infinity);
      const reached = days.filter((d) => d !== Infinity).length;
      const med = median(days);
      console.log(
        `    ${m.label} : ${fmtDay(Number.isFinite(med) ? med : undefined)}` +
          ` (10 % des joueurs avant ${fmtDay(Number.isFinite(quantile(days, 0.1)) ? quantile(days, 0.1) : undefined)},` +
          ` atteint par ${reached}/${SEEDS}) — visé : ${m.target}`,
      );
      milestoneOut[m.id] = { median: Number.isFinite(med) ? med : null, reached };
    }

    // Jours sans aucun niveau de campagne gagné (après la première semaine).
    const stalls = sims.map((s) => {
      let longest = 0;
      let run = 0;
      let total = 0;
      const end = Math.min(DAYS, Math.floor(s.milestones.campaignEnd ?? DAYS));
      for (let d = 7; d < end; d++) {
        const flat = s.days[d]!.stage === s.days[d - 1]!.stage;
        run = flat ? run + 1 : 0;
        total += flat ? 1 : 0;
        longest = Math.max(longest, run);
      }
      return { longest, total };
    });
    console.log(
      `  Jours sans gagner de niveau de campagne (de la semaine 2 à la fin de la campagne) : ${median(stalls.map((x) => x.total))}` +
        `, plus longue série : ${median(stalls.map((x) => x.longest))} jours`,
    );
    console.log(`  Invocations faites en ${DAYS} jours : ${median(sims.map((s) => s.summonsDone))}`);

    out[profile.id] = {
      label: profile.label,
      stageByDay: sims[0]!.days.map((_, d) => median(sims.map((s) => s.days[d]!.stage))),
      milestones: milestoneOut,
    };
  }
  mkdirSync('simulations/resultats', { recursive: true });
  writeFileSync('simulations/resultats/progression.json', JSON.stringify(out, null, 1));
  console.log('\nRésultats détaillés : simulations/resultats/progression.json');
}

if (process.argv.includes('--calibrer')) {
  console.log('Calibrage de la campagne sur le joueur régulier :');
  const anchors = calibrate();
  console.log('\nÀ recopier dans src/core/data/campaign.ts :\n' + JSON.stringify(anchors));
  report(anchors);
} else {
  report(CAMPAIGN_ANCHORS);
}
