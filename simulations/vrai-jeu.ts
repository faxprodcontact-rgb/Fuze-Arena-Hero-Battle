// Joue le VRAI jeu pendant des mois (les mêmes actions que les boutons), avec tous les modes, pour régler le rythme
// (28/11/2026, grand réglage). Un joueur automatique par profil :
//   - « regulier » : la référence, 3 × 20 min par jour (environ 1 h), sans rien acheter, regarde les pubs ;
//   - « payeur » : comme le régulier, avec l'offre de départ, le fonds de croissance, la carte mensuelle, le passe
//     premium de chaque saison et un paquet de gemmes à 9,99 € par mois (≈ 25 € par mois).
// Visé (décision du propriétaire) : le régulier voit tout le jeu (fin des 1 200 niveaux, premier Mythique) en 5 à 7 mois ;
// le payeur avance environ 2 fois plus vite sur les étoiles et les héros.
//   npx tsx simulations/vrai-jeu.ts [regulier|payeur] [jours] [graine]
import { Battle } from '../src/core/battle/engine';
import { HEROES, heroDef } from '../src/core/data/heroes';
import { GEAR_SLOTS } from '../src/core/data/items';
import { DAILY_CHESTS, DAILY_QUESTS, PASS_LEVELS, WEEKLY_CHESTS, WEEKLY_QUESTS, type DungeonKind } from '../src/core/data/modes';
import { MYTHIC_STARS } from '../src/core/data/stars';
import { CAMPAIGN_STAGES } from '../src/core/data/economy';
import {
  adsLeft, arenaPlan, autoFormation, buyExchange, buyOffer, campaignBattle, claimChest, claimLogin, claimMail, claimMission,
  claimPass, claimQuest, collectIdle, dungeonAttemptsLeft, dungeonPlan, ensureDay, equipBest, eventBattle, eventChooseBonus,
  eventOf, eventPlan, eventTriesLeft, fastLoot, fastLootCost, finishBattle, forgeAll, fuse, fuseAllSimple, guildBossPlan,
  joinGuild, levelUp, loginLegendChoices, opponentPower, passLevel, recycleItems, sendMission, setFragmentTarget, claimFragments,
  summon, sweepDungeon, towerPlan, tutorialGift, upgradeSlot, watchAd, type BattleRequest, type BattleResult,
} from '../src/game/state/actions';
import { canLevelUp, isUnlocked, teamPower } from '../src/game/state/selectors';
import { fresh, getState, now, replaceState, update } from '../src/game/state/store';
import type { Hero } from '../src/core/types';
import { ARENA_FREE_TICKETS, GUILD_BOSS_ATTEMPTS } from '../src/core/data/modes';
import { FRAGMENTS_PER_COPY, RARITY_RULES } from '../src/core/data/stars';

export type ProfileId = 'regulier' | 'payeur';

/** Un combat dure 20 s environ (vitesse ×2, avec l'écran de fin). */
const FIGHT_SECONDS = 20;

function fight(req: BattleRequest): BattleResult {
  const b = new Battle({ heroes: req.heroes, waves: req.waves, seed: req.seed, auto: true });
  while (!b.over) b.step();
  return {
    win: b.win,
    damage: b.enemies.reduce((sum, e) => sum + (e.maxHp - e.hp), 0),
    alive: b.heroes.filter((h) => h.hp > 0).length / Math.max(1, b.heroes.length),
    heroHp: Object.fromEntries(b.heroes.map((h) => [h.id, h.hp > 0 ? h.hp / h.maxHp : 0])),
    inputs: [],
  };
}

function timeTravel(hours: number) {
  update((s) => void (s.timeShift += hours * 3.6e6));
  ensureDay();
}

export type Milestone = 'legendary' | 'star5' | 'red1' | 'teamRed' | 'red5' | 'mythic' | 'campaignEnd';

export interface Day {
  day: number; stage: number; power: number; stars: number[]; levels: number[]; summons: number; tower: number;
  gold: number; essence: number; gems: number;
}

export class RealPlayer {
  milestones: Partial<Record<Milestone, number>> = {};
  days: Day[] = [];
  private budget = 0;
  private day = 0;
  private clock = 0;

  constructor(private profile: ProfileId, seed: number) {
    const s = fresh(Date.UTC(2026, 0, 5, 7) + seed * 7919);
    s.named = true;
    s.name = 'Sim';
    s.tutorial = -1;
    s.rng = seed * 101 + 1;
    replaceState(s);
    ensureDay();
    // le tutoriel : le premier tirage, puis le cadeau de 10 invocations
    summon('normal', 1);
    tutorialGift();
  }

  private spend(): boolean {
    if (this.budget < FIGHT_SECONDS) return false;
    this.budget -= FIGHT_SECONDS;
    return true;
  }

  private shop() {
    if (this.profile !== 'payeur') return;
    const s = getState();
    if (this.day === 0) { buyOffer('starter'); buyOffer('growth'); }
    if (s.shop.cardUntil <= now() + 86_400_000) buyOffer('card');
    if (!s.shop.passPremium) buyOffer('pass');
    if (this.day % 30 === 0 && !(s.shop.bought[`gems2-${this.day}`])) {
      buyOffer('gems-2');
      update((st) => void (st.shop.bought[`gems2-${this.day}`] = 1));
    }
  }

  /** Tout ce qui fait grandir la section : invoquer, fusionner, équiper, monter les niveaux. */
  private grow() {
    for (let k = 0; k < 50 && getState().wallet.scrolls >= 10; k++) summon('normal', 10);
    while (getState().wallet.scrolls >= 1) summon('normal', 1);
    while (getState().wallet.gems >= 2700 + 300) summon('normal', 10);
    while (getState().wallet.redScrolls >= 10) summon('featured', 10);
    for (let k = 0; k < 200 && getState().wallet.basicScrolls >= 1; k++) summon('basic', 1);
    // fragments : le Légendaire le plus avancé de la section (comme un vrai joueur)
    const s0 = getState();
    const best = s0.formation.map(([u]) => s0.heroes.find((h) => h.uid === u)!).filter((h) => h && heroDef(h.defId).rarity === 'legendary')
      .sort((a, b) => b.stars - a.stars)[0];
    if (best && s0.fragmentTarget !== best.defId) setFragmentTarget(best.defId);
    else if (!s0.fragmentTarget) setFragmentTarget(HEROES.find((h) => h.rarity === 'legendary')!.id);
    for (const [id, n] of Object.entries(getState().fragments)) if (n >= FRAGMENTS_PER_COPY) claimFragments(id);
    fuseAllSimple();
    // les fusions des Épiques et Légendaires (les autres : fuseAllSimple) ; on recommence tant que quelque chose a fusionné
    for (let k = 0, again = true; k < 4 && again; k++) {
      again = false;
      // (comme un vrai joueur) d'un même Légendaire, on ne fait monter que la meilleure copie : les autres restent des copies
      const best = new Map<string, Hero>();
      for (const h of getState().heroes) {
        const b = best.get(h.defId);
        if (!b || h.stars > b.stars || (h.stars === b.stars && h.level > b.level)) best.set(h.defId, h);
      }
      const ladder = getState().heroes.filter((h) => RARITY_RULES[heroDef(h.defId).rarity].fusion === 'ladder' && h.stars < RARITY_RULES[heroDef(h.defId).rarity].maxStars
        && (heroDef(h.defId).rarity !== 'legendary' || best.get(h.defId) === h));
      for (const h of ladder.sort((a, b) => b.stars - a.stars).slice(0, 60)) if (getState().heroes.includes(h) && fuse(h.uid)) again = true;
    }
    autoFormation();
    for (const [uid] of getState().formation) equipBest(uid);
    forgeAll();
    for (const [uid] of getState().formation) equipBest(uid);
    // recycler l'équipement inutile (pas porté, gris et vert) pour la poussière
    const st = getState();
    recycleItems(st.items.filter((it) => it.heroUid === undefined && it.rarity <= 1).map((it) => it.uid));
    // les niveaux : le moins haut de la section d'abord
    for (let k = 0; k < 2000; k++) {
      const s = getState();
      const team = s.formation.map(([u]) => s.heroes.find((h) => h.uid === u)!).filter((h) => h && canLevelUp(s, h)).sort((a, b) => a.level - b.level);
      if (!team.length || !levelUp(team[0]!.uid)) break;
    }
    // le renforcement des emplacements, s'il reste de l'or
    for (const [uid] of getState().formation) for (const slot of GEAR_SLOTS) upgradeSlot(uid, slot);
  }

  private daily() {
    const s = getState();
    if (claimLogin()) {/* ok */} else claimLogin(loginLegendChoices()[0]);
    claimMail();
    collectIdle();
    if (fastLootCost(getState()) === 0) fastLoot();
    // les 6 pubs du jour : l'invocation gratuite (une par jour), puis le butin et les gemmes
    const ads: ('summon' | 'idle' | 'gems')[] = ['summon', 'idle', 'idle', 'idle', 'gems', 'gems'];
    while (adsLeft(getState()) > 0) if (!watchAd(ads[6 - adsLeft(getState())] ?? 'gems')) break;
    for (const m of [...getState().daily.missions]) claimMission(m.id);
    for (const m of [...getState().daily.missions]) if (!m.startedAt) sendMission(m.id);
    void s;
  }

  private modes() {
    const s = getState();
    // donjons : le niveau suivant, sinon le balayage
    if (isUnlocked(s, 'dungeons')) {
      for (const kind of ['gold', 'essence', 'gear'] as DungeonKind[]) {
        while (dungeonAttemptsLeft(getState(), kind) > 0) {
          const plan = dungeonPlan(kind);
          const req = plan?.build();
          if (req && this.spend()) {
            const r = fight(req);
            finishBattle(req, r);
            if (r.win) continue;
          }
          if (getState().dungeons[kind] > 0) { if (!sweepDungeon(kind)) break; } else break;
        }
      }
    }
    // tour : jusqu'au premier échec
    if (isUnlocked(getState(), 'tower')) {
      while (this.spend()) {
        const req = towerPlan().build();
        if (!req) break;
        const r = fight(req);
        finishBattle(req, r);
        if (!r.win) break;
      }
    }
    // Événement : une partie par essai, jusqu'à perdre ou finir la zone
    if (isUnlocked(getState(), 'event')) {
      for (let tries = 0; tries < 3; tries++) {
        if (!eventOf(getState()).run) {
          if (eventTriesLeft(getState()) <= 0) break;
          const first = eventPlan().build();
          if (!first || !this.spend()) break;
          finishBattle(first, fight(first));
        }
        while (eventOf(getState()).run && this.spend()) {
          const run = eventOf(getState()).run!;
          if (run.offer) {
            const order = ['revive', 'heal', 'atk', 'def'];
            eventChooseBonus([...run.offer].sort((a, b) => order.indexOf(a) - order.indexOf(b))[0]!);
          }
          const req = eventBattle();
          if (!req) break;
          finishBattle(req, fight(req));
        }
      }
    }
    // arène : contre l'adversaire le plus faible
    if (isUnlocked(getState(), 'arena')) {
      for (let k = 0; k < ARENA_FREE_TICKETS && getState().daily.arenaFights < ARENA_FREE_TICKETS && this.spend(); k++) {
        const o = [...getState().arena.opponents].sort((a, b) => opponentPower(a) - opponentPower(b))[0];
        const req = o && arenaPlan(o.id)?.build();
        if (!req) break;
        finishBattle(req, fight(req));
      }
      for (let k = 0; k < 20; k++) if (!buyExchange('arena', 'a-frag')) break;
      for (let k = 0; k < 20; k++) if (!buyExchange('arena', 'a-scroll')) break;
    }
    // guilde : rejoindre, puis le boss
    if (isUnlocked(getState(), 'guild')) {
      if (!getState().guild.joined) joinGuild('Sim');
      while (getState().daily.guildAttempts < GUILD_BOSS_ATTEMPTS && this.spend()) {
        const req = guildBossPlan().build();
        if (!req) break;
        finishBattle(req, fight(req));
      }
      for (let k = 0; k < 20; k++) if (!buyExchange('guild', 'g-frag')) break;
    }
  }

  private rewards() {
    for (const q of DAILY_QUESTS) claimQuest(q.id, 'daily');
    for (const q of WEEKLY_QUESTS) claimQuest(q.id, 'weekly');
    DAILY_CHESTS.forEach((_, i) => claimChest(i, 'daily'));
    WEEKLY_CHESTS.forEach((_, i) => claimChest(i, 'weekly'));
    const lv = passLevel(getState());
    for (let l = 0; l < Math.min(lv, PASS_LEVELS.length); l++) { claimPass(l, false); claimPass(l, true); }
  }

  private campaign() {
    while (getState().campaign.cleared < CAMPAIGN_STAGES && this.spend()) {
      const req = campaignBattle();
      const r = fight(req);
      finishBattle(req, r);
      if (!r.win) break;
    }
  }

  session(minutes: number) {
    this.budget = minutes * 60;
    this.shop();
    this.daily();
    this.grow();
    this.campaign();
    this.grow();
    this.modes();
    this.rewards();
    this.grow();
    this.campaign();
    this.rewards();
  }

  private mark(m: Milestone, ok: boolean) {
    if (ok && this.milestones[m] === undefined) this.milestones[m] = this.day;
  }

  run(days: number): this {
    for (this.day = 0; this.day < days; this.day++) {
      // le premier jour : 30 min en arrivant, puis 2 × 20 min ; ensuite 3 × 20 min (matin, midi, soir)
      const plan: [number, number][] = this.day === 0 ? [[0, 30], [3, 20], [10, 20]] : [[1, 20], [6, 20], [14, 20]];
      for (const [hour, min] of plan) {
        timeTravel(this.day * 24 + hour - this.clock);
        this.clock = this.day * 24 + hour;
        this.session(min);
      }
      const s = getState();
      const team = s.formation.map(([u]) => s.heroes.find((h) => h.uid === u)!).filter(Boolean);
      const stars = team.map((h) => h.stars).sort((a, b) => b - a);
      this.mark('legendary', s.heroes.some((h) => heroDef(h.defId).rarity === 'legendary'));
      this.mark('star5', s.heroes.some((h) => h.stars >= 5));
      this.mark('red1', s.heroes.some((h) => h.stars >= 6));
      // (5 héros en étoiles rouges, de quoi faire une section entière)
      this.mark('teamRed', s.heroes.filter((h) => h.stars >= 6).length >= 5);
      this.mark('red5', s.heroes.some((h) => h.stars >= 10));
      this.mark('mythic', s.heroes.some((h) => h.stars >= MYTHIC_STARS));
      this.mark('campaignEnd', s.campaign.cleared >= CAMPAIGN_STAGES);
      this.days.push({
        day: this.day, stage: s.campaign.cleared, power: Math.round(teamPower(s)), stars, levels: team.map((h) => h.level),
        summons: s.summon.total, tower: s.tower.floor, gold: s.wallet.gold, essence: s.wallet.essence, gems: s.wallet.gems,
      });
    }
    return this;
  }
}

const LABEL: Record<Milestone, string> = {
  legendary: 'Premier Légendaire', star5: 'Premier ★5', red1: 'Première étoile rouge', teamRed: 'Section en étoiles rouges',
  red5: 'Premier ★5 rouge', mythic: 'Premier Mythique', campaignEnd: 'Fin de la campagne',
};

if (import.meta.url === `file://${process.argv[1]}`) {
  const profile = (process.argv[2] ?? 'regulier') as ProfileId;
  const days = Number(process.argv[3] ?? 200);
  const seed = Number(process.argv[4] ?? 1);
  const p = new RealPlayer(profile, seed).run(days);
  for (const d of p.days) {
    if ([0, 1, 2, 6, 13, 29, 59, 89, 119, 149, 179, 209, 239, 299].includes(d.day)) {
      console.log(`jour ${d.day + 1} : niveau ${d.stage}, tour ${d.tower}, force ${d.power}, étoiles ${d.stars.join(' ')}, niveaux ${d.levels.join('/')}, invocations ${d.summons}, or ${d.gold}, essence ${d.essence}, gemmes ${d.gems}`);
    }
  }
  for (const [m, label] of Object.entries(LABEL)) console.log(`${label} : ${p.milestones[m as Milestone] === undefined ? 'jamais' : `jour ${p.milestones[m as Milestone]! + 1}`}`);
}
