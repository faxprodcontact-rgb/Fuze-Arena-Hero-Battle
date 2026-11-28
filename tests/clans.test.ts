// Les dessins des combats : chaque monstre des règles a sa planche vectorielle dans le clan du combat, chaque décor existe,
// et la fin d'une région est un boss seul.
import { describe, expect, it } from 'vitest';
import { BOSSES, MONSTERS } from '../src/core/data/monsters';
import { FOND_VECTO } from '../src/game/fond-vecto';
import { VECTO_ANIM } from '../src/game/vecto-anim';
import { CLANS, CLAN_CHIEF, battleLook, bossArt, campaignLook, isBigBoss, monsterArtId } from '../src/game/look';
import { campaignWaves, chapterElement, campaignElement, isRegionFinale } from '../src/core/stages';
import { ELEMENTS } from '../src/core/types';
import { heroDef } from '../src/core/data/heroes';

const chars = VECTO_ANIM.chars as Record<string, unknown>;

describe('clans et décors', () => {
  it('chaque clan a son décor, son général et ses 3 monstres', () => {
    for (const c of CLANS) {
      expect(c in FOND_VECTO).toBe(true);
      expect(CLAN_CHIEF[c] in chars).toBe(true);
      expect(Object.keys(chars).filter((k) => k.startsWith(`mon-${c}-`))).toHaveLength(3);
    }
  });

  it('tous les monstres des règles ont un dessin dans tous les modes, du clan de leur élément', () => {
    const looks = [
      ...Array.from({ length: 30 }, (_, i) => campaignLook(i + 1)),
      battleLook('tower', '7'), battleLook('dungeon', '1', 'gold'), battleLook('dungeon', '1', 'essence'),
      battleLook('dungeon', '1', 'gear'), battleLook('event', '1-5'), battleLook('event', '2-20'), battleLook('guildBoss', 'dragon'), battleLook('arena', 'Kaïro'),
    ];
    for (const look of looks) {
      expect(look.fond in FOND_VECTO).toBe(true);
      for (const e of ELEMENTS) {
        for (const m of MONSTERS) {
          const id = monsterArtId(m.id, e, look);
          expect(id in chars, `${m.id} ${e} → ${id}`).toBe(true);
          // le dessin est bien de l'élément du monstre (clan, général ou grand boss de cet élément)
          if (!isBigBoss(id) && !id.startsWith('mon-')) expect(heroDef(id).element).toBe(e);
        }
      }
    }
  });

  it('en campagne, le décor est celui du clan des monstres du chapitre', () => {
    for (let c = 1; c <= 30; c++) {
      const look = campaignLook(c);
      const id = monsterArtId('goblin', campaignElement(c), look);
      expect(id.startsWith(`mon-${look.fond}-`)).toBe(true);
    }
  });

  it('les boss du jour et de guilde sont des grands boss', () => {
    for (const b of BOSSES) expect(isBigBoss(bossArt(b))).toBe(true);
  });

  it('la fin d’une région est un boss seul', () => {
    expect(isRegionFinale(200)).toBe(true);
    expect(isRegionFinale(160)).toBe(false);
    const waves = campaignWaves(200);
    expect(waves.at(-1)).toHaveLength(1);
    expect(waves.at(-1)![0]!.boss).toBe(true);
    expect(campaignWaves(120).at(-1)!.length).toBeGreaterThan(1);
  });
});
