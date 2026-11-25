// Joue les premiers jours du VRAI jeu (mêmes actions que les boutons) avec un joueur automatique,
// pour vérifier que le jeu complet suit le rythme des simulations.   npx tsx simulations/premiers-jours.ts
import { Battle } from '../src/core/battle/engine';
import { DAILY_CHESTS, DAILY_QUESTS, WEEKLY_CHESTS, WEEKLY_QUESTS } from '../src/core/data/modes';
import {
  autoFormation, campaignBattle, claimChest, claimQuest, collectIdle, ensureDay, equipBest, finishBattle, fuse,
  fuseAllSimple, levelUp, summon,
} from '../src/game/state/actions';
import { canLevelUp, teamPower } from '../src/game/state/selectors';
import { getState, update } from '../src/game/state/store';

/** Le temps passe (le joueur automatique attend) : décalage de l'horloge du jeu. */
function timeTravel(hours: number) {
  update((s) => void (s.timeShift += hours * 3.6e6));
  ensureDay();
}

function play(minutes: number) {
  let left = minutes * 60;
  while (left > 0) {
    const s = getState();
    collectIdle();
    for (const q of DAILY_QUESTS) claimQuest(q.id, 'daily');
    for (const q of WEEKLY_QUESTS) claimQuest(q.id, 'weekly');
    DAILY_CHESTS.forEach((_, i) => claimChest(i, 'daily'));
    WEEKLY_CHESTS.forEach((_, i) => claimChest(i, 'weekly'));
    while (getState().wallet.gems >= 2700) summon('normal', 10);
    while (getState().wallet.scrolls >= 10) summon('normal', 10);
    while (getState().wallet.scrolls >= 1) summon('normal', 1);
    while (getState().wallet.basicScrolls >= 1) summon('basic', 1);
    fuseAllSimple();
    for (const h of [...getState().heroes]) if (getState().heroes.includes(h)) fuse(h.uid);
    autoFormation();
    for (const [uid] of getState().formation) equipBest(uid);
    for (let k = 0; k < 400; k++) {
      const st = getState();
      const team = st.formation.map(([u]) => st.heroes.find((h) => h.uid === u)!).filter((h) => canLevelUp(st, h)).sort((a, b) => a.level - b.level);
      if (!team.length || !levelUp(team[0]!.uid)) break;
    }
    const req = campaignBattle();
    const b = new Battle({ heroes: req.heroes, waves: req.waves, seed: req.seed, auto: true });
    while (!b.over) b.step();
    finishBattle(req, { win: b.win, damage: 0, inputs: [] });
    left -= 20;
    if (!b.win) break;
    void s;
  }
}

ensureDay();
const sessions: [number, number][] = [[0, 10], [0, 10], [4, 15], [6, 10]];
for (const [wait, min] of sessions) {
  timeTravel(wait);
  play(min);
  const s = getState();
  console.log(`après ${min} min : niveau ${s.campaign.cleared}, force ${Math.round(teamPower(s))}, héros ${s.heroes.length}`);
}
for (let day = 2; day <= 7; day++) {
  for (const wait of [11, 5, 8]) {
    timeTravel(wait);
    play(5);
  }
  const s = getState();
  console.log(`jour ${day} : niveau ${s.campaign.cleared}, force ${Math.round(teamPower(s))}, niv. héros ${s.formation.map(([u]) => s.heroes.find((h) => h.uid === u)!.level).join('/')}`);
}
