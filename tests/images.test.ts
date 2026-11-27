// Toutes les images que le jeu demande existent (v0.65.0 : le pixel art est supprimé, tout est vectoriel) : la planche
// de combat de chaque personnage, son dessin des menus, les effets reçus, les fonds de chaque clan.
import { existsSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { FOND_VECTO } from '../src/game/fond-vecto';
import { VECTO_ANIM } from '../src/game/vecto-anim';
import { VECTO_FX } from '../src/game/vecto-fx';
import { VECTO_REPOS } from '../src/game/vecto-repos';
import { vectoFig } from '../src/game/vecto';

const file = (url: string) => `public/${url.split('?')[0]}`;

describe('images vectorielles', () => {
  it('chaque personnage du combat a sa planche et son dessin des menus', () => {
    const ids = Object.keys(VECTO_ANIM.chars);
    expect(ids.length).toBeGreaterThanOrEqual(67);
    for (const id of ids) {
      expect(existsSync(`public/art/vecto/jeu/${id}.webp`), id).toBe(true);
      const v = vectoFig(id);
      expect(v, id).toBeDefined();
      expect(existsSync(file(v!.big)) && existsSync(file(v!.small)), id).toBe(true);
    }
  });

  it('les effets reçus et les fonds existent', () => {
    for (const k of Object.keys(VECTO_FX.fx)) expect(existsSync(`public/art/vecto/fx/${k}.webp`), k).toBe(true);
    for (const c of Object.keys(FOND_VECTO)) {
      for (const f of [c, `${c}-anim`, `${c}-menu`]) expect(existsSync(`public/art/vecto/fonds/${f}.webp`), f).toBe(true);
    }
  });

  it('le signe du repos des menus : la base et une bande par zone (vecto-live.tsx)', () => {
    for (const [id, r] of Object.entries(VECTO_REPOS)) {
      expect(existsSync(`public/art/vecto/repos/${id}-${r.v}-base.webp`), id).toBe(true);
      r.zones.forEach((_, k) => expect(existsSync(`public/art/vecto/repos/${id}-${r.v}-${k}.webp`), `${id}-${k}`).toBe(true));
      expect(vectoFig(id), id).toBeDefined();
    }
  });
});
