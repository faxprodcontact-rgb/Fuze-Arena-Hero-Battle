// Les 8 monstres de clan devenus héros (Nyrra, Sarvik, Jessa, Oboro, Sorai, Bao, Gribou, Karu) : ils existent, on peut
// les invoquer, ils fusionnent avec leur élément, ils combattent, ils ont leurs dessins et restent des monstres de clan.
import { describe, expect, it } from 'vitest';
import { Battle } from '../src/core/battle/engine';
import { heroToUnit } from '../src/core/battle/units';
import type { Slot } from '../src/core/battle/types';
import { HEROES, heroDef, heroesOfElement, isHero } from '../src/core/data/heroes';
import { planFusion } from '../src/core/fusion';
import { createRng } from '../src/core/rng';
import { campaignWaves } from '../src/core/stages';
import { summonOne } from '../src/core/summon';
import type { Hero } from '../src/core/types';
import { heroImage } from '../src/game/art';
import { VECTO_ANIM } from '../src/game/vecto-anim';
import { vectoFig } from '../src/game/vecto';
import { t } from '../src/game/i18n';
import { CLANS, HERO_ART, campaignLook, heroArt, monsterArtId } from '../src/game/look';
import { getState } from '../src/game/state/store';

const NEW: Record<string, [string, string]> = {
  nyrra: ['Nyrra', 'earth'], sarvik: ['Sarvik', 'earth'], jessa: ['Jessa', 'water'], oboro: ['Oboro', 'fire'],
  sorai: ['Sorai', 'wind'], bao: ['Bao', 'wind'], gribou: ['Gribou', 'wind'], karu: ['Karu', 'wind'],
};
const IDS = Object.keys(NEW);

describe('monstres de clan devenus héros', () => {
  it('les 8 existent, avec leur nom et leur élément ; 2 Épiques, 3 Rares, 3 Communs', () => {
    expect(HEROES).toHaveLength(47);
    for (const id of IDS) {
      expect(isHero(id)).toBe(true);
      expect(heroDef(id).name).toBe(NEW[id]![0]);
      expect(heroDef(id).element).toBe(NEW[id]![1]);
    }
    const count = (r: string) => IDS.filter((id) => heroDef(id).rarity === r).length;
    expect([count('legendary'), count('epic'), count('rare'), count('common')]).toEqual([0, 2, 3, 3]);
    expect(heroDef('bao').role).toBe('healer');
  });

  it('leur dessin est celui de leur monstre de clan (combat, dessin en pied) ; leur tête est la leur', () => {
    const anims = VECTO_ANIM.chars as Record<string, unknown>;
    expect(Object.keys(HERO_ART).sort()).toEqual([...IDS].sort());
    for (const h of HEROES) {
      expect(heroArt(h.id) in anims).toBe(true);
      expect(vectoFig(heroArt(h.id))).toBeDefined();
    }
    expect(heroImage('nyrra')).toMatch(/^art\/vecto\/v\/nyrra\.webp(\?h=\w+)?$/);
    expect(vectoFig(heroArt('karu'))!.big).toMatch(/^art\/vecto\/mon-orin-rapide\.webp(\?h=\w+)?$/);
    expect(heroArt('knights-8')).toBe('knights-8');
    // ils jouent toujours les monstres de leur clan
    const monsterArts = new Set<string>();
    for (let c = 1; c <= 40; c++) {
      const look = campaignLook(c);
      for (const el of ['fire', 'water', 'wind', 'earth'] as const) for (const m of ['goblin', 'golem', 'archer']) monsterArts.add(monsterArtId(m, el, look));
    }
    for (const art of Object.values(HERO_ART)) {
      expect(monsterArts.has(art)).toBe(true);
      expect(CLANS.some((c) => art.startsWith(`mon-${c}-`))).toBe(true);
    }
  });

  it('on peut les invoquer', () => {
    const rng = createRng(7);
    const state = { pity: 0 };
    const seen = new Set<string>();
    for (let i = 0; i < 20000 && IDS.some((id) => !seen.has(id)); i++) seen.add(summonOne(state, rng).id);
    for (const id of IDS) expect(seen.has(id)).toBe(true);
  });

  it('ils fusionnent avec des héros de leur élément', () => {
    let uid = 1;
    const hero = (defId: string, stars: number): Hero => ({ uid: uid++, defId, stars, level: 1 });
    const target = hero('bao', 3);
    const wind = (r: 'common' | 'rare') => heroesOfElement('wind', r)[0]!.id;
    const roster = [target, hero('bao', 3), hero(wind('common'), 3), hero(wind('rare'), 3), hero(heroesOfElement('fire', 'rare')[0]!.id, 3)];
    const plan = planFusion(roster, target.uid);
    expect(plan).not.toBeNull();
    expect(plan!.consumed).not.toContain(roster[4]!.uid);
    expect(heroesOfElement('wind', 'epic').map((h) => h.id)).toContain('bao');
  });

  it('ils combattent ; la compétence de Bao frappe et soigne son équipe', () => {
    const team = ['sarvik', 'karu', 'oboro', 'jessa', 'bao'];
    const battle = new Battle({
      heroes: team.map((defId, i) => heroToUnit({ uid: i + 1, defId, stars: 5, level: 40 }, i as Slot)),
      waves: campaignWaves(120),
      seed: 3,
      auto: true,
    });
    let baoHealed = false, baoHit = false;
    for (let n = 0; n < 20000 && !battle.over; n++) {
      for (const e of battle.step()) {
        if (e.type !== 'skill' || e.skill.id !== 'bao') continue;
        baoHealed ||= e.hits.some((h) => h.kind === 'heal');
        baoHit ||= e.hits.some((h) => h.kind === 'damage' || h.kind === 'miss');
      }
    }
    expect(battle.over).toBe(true);
    expect(baoHealed && baoHit).toBe(true);
  });

  it('leur compétence a un nom en français et en anglais', () => {
    const lang = getState().lang;
    for (const l of ['fr', 'en'] as const) {
      getState().lang = l;
      for (const id of IDS) expect(t(`skill.${heroDef(id).skill.id}`)).not.toBe(`skill.${heroDef(id).skill.id}`);
    }
    getState().lang = lang;
    expect(t('skill.bao')).not.toBe('');
  });
});
