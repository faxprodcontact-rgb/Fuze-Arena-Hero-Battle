// Les cases des héros montrent leur tête vectorielle (demande du 27/11) : chaque héros du jeu doit avoir la sienne,
// fabriquée par refonte-graphique/ui-moderne/heros/tetes.py, avec son réglage dans tetes.json.
import { existsSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { HEROES } from '../src/core/data/heroes';
import { heroImage } from '../src/game/art';

describe('têtes des héros (cases)', () => {
  it('chaque héros a sa tête (art/vecto/v/<id>.webp) et son réglage', () => {
    const reglages = JSON.parse(readFileSync('refonte-graphique/ui-moderne/heros/tetes.json', 'utf8')) as Record<string, unknown>;
    for (const h of HEROES) {
      const url = heroImage(h.id).split('?')[0]!;
      expect(url).toBe(`art/vecto/v/${h.id}.webp`);
      expect(existsSync(`public/${url}`), h.id).toBe(true);
      expect(h.id in reglages, h.id).toBe(true);
    }
  });
});
