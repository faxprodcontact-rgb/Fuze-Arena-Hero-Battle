// Points rouges : « il y a quelque chose à faire ici ».
import {
  ARENA_FREE_TICKETS, DAILY_BOSS_ATTEMPTS, DAILY_CHESTS, DAILY_QUESTS, DUNGEON_BY_WEEKDAY, DUNGEON_ENTRIES_PER_DAY,
  GUILD_BOSS_ATTEMPTS, UNLOCKS, WEEKLY_CHESTS, WEEKLY_QUESTS, type Feature,
} from '../../core/data/modes';
import { fusionPreview, missionEnd, passLevel, questPoints } from '../state/actions';
import { canLevelUp, heroByUid, idlePreview, isUnlocked } from '../state/selectors';
import { now } from '../state/store';
import type { PlayerState } from '../state/types';

export function isNew(s: PlayerState, f: Feature): boolean {
  return isUnlocked(s, f) && !s.seen.includes(f);
}

export const dots = {
  campaign: (s: PlayerState) => idlePreview(s).hours >= 2 || s.daily.fastLoot === 0,
  heroes: (s: PlayerState) =>
    s.formation.some(([uid]) => {
      const h = heroByUid(s, uid);
      return !!h && (canLevelUp(s, h) || !!fusionPreview(uid).plan);
    }),
  summon: (s: PlayerState) => s.wallet.scrolls >= 1 || s.wallet.basicScrolls >= 1,
  missions: (s: PlayerState) =>
    s.daily.missions.some((m) => !m.claimed && (!m.startedAt || now() >= missionEnd(m))),
  dungeons: (s: PlayerState) => {
    const open = DUNGEON_BY_WEEKDAY[new Date(now()).getDay()] ?? [];
    return open.some((k) => s.daily.entries[k] < DUNGEON_ENTRIES_PER_DAY);
  },
  dailyBoss: (s: PlayerState) => s.daily.bossAttempts < DAILY_BOSS_ATTEMPTS,
  arena: (s: PlayerState) => s.daily.arenaFights < ARENA_FREE_TICKETS,
  tower: () => false,
  defense: () => false,
  adventure: (s: PlayerState) =>
    (['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'defense'] as const).some(
      (f) => isUnlocked(s, f) && (isNew(s, f) || dots[f](s)),
    ),
  guild: (s: PlayerState) =>
    isUnlocked(s, 'guild') && (isNew(s, 'guild') || !s.guild.joined || s.daily.guildAttempts < GUILD_BOSS_ATTEMPTS),
  quests: (s: PlayerState) => {
    const claimable = (defs: typeof DAILY_QUESTS, box: { quests: Record<string, number>; claimed: string[] }) =>
      defs.some((q) => !box.claimed.includes(q.id) && (box.quests[q.id] ?? 0) >= q.goal);
    const chests = (kind: 'daily' | 'weekly', list: typeof DAILY_CHESTS, done: number[]) =>
      list.some((c, i) => !done.includes(i) && questPoints(kind) >= c.points);
    return claimable(DAILY_QUESTS, s.daily) || claimable(WEEKLY_QUESTS, s.weekly)
      || chests('daily', DAILY_CHESTS, s.daily.chests) || chests('weekly', WEEKLY_CHESTS, s.weekly.chests);
  },
  pass: (s: PlayerState) => {
    const level = passLevel(s);
    for (let i = 0; i < level; i++) {
      if (!s.pass.claimedFree.includes(i)) return true;
      if (s.shop.passPremium && !s.pass.claimedPremium.includes(i)) return true;
    }
    return false;
  },
};

export const ADVENTURE_ORDER: Exclude<Feature, 'guild'>[] = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'defense'];
export { UNLOCKS };
