// Bibliothèque d'effets : brûlure, provocation, réanimation, passifs débloqués par étoiles, bonus d'élément.
import { describe, expect, it } from 'vitest';
import { Battle, elementBonus } from '../src/core/battle/engine';
import { heroToUnit } from '../src/core/battle/units';
import { ELEMENT_BONUS, type Effect, type UnitInit } from '../src/core/battle/types';
import { HEROES, PASSIVE_STARS } from '../src/core/data/heroes';
import { HD_ANIM } from '../src/game/hd-meta';
import { heroArt } from '../src/game/look';

function unit(id: string, side: 'hero' | 'enemy', slot: 0 | 1 | 2 | 3 | 4, effects: Effect[], extra: Partial<UnitInit> = {}): UnitInit {
  return {
    id, defId: 'x', side, slot, element: 'fire', maxHp: 1000, atk: 100, def: 0, interval: 1000, ranged: false,
    skill: { id: 's', effects }, crit: 0, dodge: 0, tenacity: 0, ...extra,
  };
}

/** Un combat où le héros lance tout de suite sa compétence, puis on avance de quelques tours. */
function castOnce(hero: UnitInit, foes: UnitInit[], ticks = 1) {
  const b = new Battle({ heroes: [hero], waves: [foes], seed: 1, auto: false });
  // Personne n'attaque normalement : on ne mesure que la compétence.
  for (const u of [...b.heroes, ...b.enemies]) u.cooldown = 1e9;
  b.heroes[0]!.energy = 100;
  b.requestSkill(hero.id);
  const events = [];
  for (let i = 0; i < ticks; i++) events.push(...b.step());
  return { b, events };
}

describe('effets', () => {
  it('la brûlure fait des dégâts chaque seconde', () => {
    const { b } = castOnce(unit('h', 'hero', 2, [{ type: 'status', target: 'front', status: 'burn', value: 0.5, seconds: 3 }]), [unit('e', 'enemy', 0, [])], 35);
    // 3 secondes de brûlure à 50 % d'une attaque de 100 = 150 dégâts.
    expect(1000 - b.enemies[0]!.hp).toBe(150);
  });

  it('la provocation attire les coups', () => {
    const { b } = castOnce(
      unit('h', 'hero', 2, [{ type: 'damage', target: 'back', power: 1 }]),
      [unit('front', 'enemy', 0, []), unit('back', 'enemy', 4, [])],
    );
    expect(b.enemies.find((e) => e.id === 'back')!.hp).toBeLessThan(1000);
    const b2 = new Battle({ heroes: [unit('h', 'hero', 2, [{ type: 'damage', target: 'back', power: 1 }])], waves: [[unit('front', 'enemy', 0, []), unit('back', 'enemy', 4, [])]], seed: 1, auto: false });
    b2.enemies[0]!.statuses.push({ kind: 'taunt', value: 0, ticks: 50, power: 0, source: 'x' });
    b2.heroes[0]!.energy = 100;
    b2.requestSkill('h');
    b2.step();
    expect(b2.enemies.find((e) => e.id === 'front')!.hp).toBeLessThan(1000);
    expect(b2.enemies.find((e) => e.id === 'back')!.hp).toBe(1000);
  });

  it('la réanimation ramène un allié tombé', () => {
    const healer = unit('h', 'hero', 3, [{ type: 'revive', pctMax: 0.3 }]);
    const ally = unit('a', 'hero', 0, []);
    const b = new Battle({ heroes: [healer, ally], waves: [[unit('e', 'enemy', 0, [])]], seed: 1, auto: false });
    b.heroes[1]!.hp = 0;
    b.heroes[1]!.dead = true;
    b.heroes[0]!.energy = 100;
    b.requestSkill('h');
    b.step();
    expect(b.heroes[1]!.hp).toBe(300);
  });

  it('les passifs se débloquent avec les étoiles', () => {
    const d = HEROES.find((h) => h.rarity === 'epic')!;
    expect(heroToUnit({ uid: 1, defId: d.id, stars: PASSIVE_STARS[0] - 1, level: 1 }, 0).passives).toHaveLength(0);
    expect(heroToUnit({ uid: 1, defId: d.id, stars: PASSIVE_STARS[0], level: 1 }, 0).passives).toHaveLength(1);
    expect(heroToUnit({ uid: 1, defId: d.id, stars: PASSIVE_STARS[1], level: 1 }, 0).passives).toHaveLength(2);
  });

  it("bonus d'équipe par élément", () => {
    const h = (el: 'fire' | 'water' | 'wind' | 'earth') => ({ ...unit('x', 'hero', 0, []), element: el, hero: true });
    expect(elementBonus([h('fire'), h('fire'), h('fire'), h('water')])).toBe(ELEMENT_BONUS.same3);
    expect(elementBonus([h('fire'), h('fire'), h('fire'), h('fire'), h('fire')])).toBe(ELEMENT_BONUS.same5);
    expect(elementBonus([h('fire'), h('water'), h('wind'), h('earth')])).toBe(ELEMENT_BONUS.rainbow);
    expect(elementBonus([h('fire'), h('water')])).toBeNull();
  });

  it('44 héros (36 + 8 monstres de clan) : au moins 9 par élément, chaque rôle présent, tous dessinés en HD', () => {
    expect(HEROES).toHaveLength(44);
    for (const el of ['fire', 'water', 'wind', 'earth']) {
      const list = HEROES.filter((h) => h.element === el);
      expect(list.length).toBeGreaterThanOrEqual(9);
      for (const role of ['protector', 'warrior', 'marksman', 'assassin', 'healer', 'support']) expect(list.filter((h) => h.role === role).length).toBeGreaterThan(0);
      // la fusion des Épiques demande des héros du même élément : chaque élément en a de chaque rareté
      for (const r of ['common', 'rare', 'epic', 'legendary']) expect(list.filter((h) => h.rarity === r).length).toBeGreaterThan(0);
    }
    expect(HEROES.filter((h) => h.talent)).toHaveLength(15);
    expect(HEROES.every((h) => heroArt(h.id) in HD_ANIM.chars)).toBe(true);
  });
});
