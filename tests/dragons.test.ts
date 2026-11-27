// Les 3 dragons de la famille d'Elvyn (Brasyr feu, Rocvar terre, Venthys vent ; 27/11) : de vrais héros Épiques qu'on
// peut invoquer et fusionner avec leur élément, qui combattent, avec leurs noms de compétence en français et en anglais,
// et leurs images vectorielles (ils n'ont pas de pixel art).
import { existsSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { Battle } from '../src/core/battle/engine';
import { heroToUnit } from '../src/core/battle/units';
import type { Slot } from '../src/core/battle/types';
import { heroDef, heroesOfElement, isHero } from '../src/core/data/heroes';
import { createRng } from '../src/core/rng';
import { campaignWaves } from '../src/core/stages';
import { summonOne } from '../src/core/summon';
import { heroImage } from '../src/game/art';
import { t } from '../src/game/i18n';
import { heroArt } from '../src/game/look';
import { getState } from '../src/game/state/store';
import { vectoFig } from '../src/game/vecto';

const DRAGONS: Record<string, [string, string, string]> = {
  'dragon-feu': ['Brasyr', 'fire', 'warrior'],
  'dragon-terre': ['Rocvar', 'earth', 'protector'],
  'dragon-vent': ['Venthys', 'wind', 'assassin'],
};
const IDS = Object.keys(DRAGONS);

describe('les 3 dragons', () => {
  it('sont des héros Épiques, avec leur nom, leur élément et leur rôle', () => {
    for (const id of IDS) {
      const [name, element, role] = DRAGONS[id]!;
      expect(isHero(id)).toBe(true);
      expect(heroDef(id)).toMatchObject({ name, element, role, rarity: 'epic' });
      expect(heroesOfElement(heroDef(id).element, 'epic').map((h) => h.id)).toContain(id);
    }
  });

  it('on peut les invoquer', () => {
    const rng = createRng(11);
    const state = { pity: 0 };
    const seen = new Set<string>();
    for (let i = 0; i < 20000 && IDS.some((id) => !seen.has(id)); i++) seen.add(summonOne(state, rng).id);
    for (const id of IDS) expect(seen.has(id)).toBe(true);
  });

  it('ils combattent et lancent leur compétence', () => {
    const team = ['dragon-terre', 'dragon-feu', 'dragon-vent', 'knights-8', 'mages-11'];
    const battle = new Battle({
      heroes: team.map((defId, i) => heroToUnit({ uid: i + 1, defId, stars: 5, level: 40 }, i as Slot)),
      waves: campaignWaves(120),
      seed: 5,
      auto: true,
    });
    const cast = new Set<string>();
    for (let n = 0; n < 20000 && !battle.over; n++) for (const e of battle.step()) if (e.type === 'skill') cast.add(e.skill.id);
    expect(battle.over).toBe(true);
    for (const s of ['brasyr', 'rocvar', 'venthys']) expect(cast.has(s)).toBe(true);
  });

  it('leur compétence a un nom en français et en anglais', () => {
    const lang = getState().lang;
    for (const l of ['fr', 'en'] as const) {
      getState().lang = l;
      for (const id of IDS) expect(t(`skill.${heroDef(id).skill.id}`)).not.toBe(`skill.${heroDef(id).skill.id}`);
    }
    getState().lang = lang;
  });

  it('leurs images sont vectorielles, même sans ?vecto=1 (visage, dessin en pied)', () => {
    for (const id of IDS) {
      expect(heroArt(id)).toBe(id);
      expect(heroImage(id)).toMatch(new RegExp(`^art/vecto/v/${id}\\.webp(\\?h=\\w+)?$`));
      const v = vectoFig(id);
      expect(v).toBeDefined();
      for (const url of [heroImage(id), v!.big, v!.small]) expect(existsSync(`public/${url.split('?')[0]}`)).toBe(true);
    }
    // un héros qui a son pixel art le garde (l'essai vectoriel reste éteint par défaut)
    expect(vectoFig('knights-8')).toBeUndefined();
  });
});
