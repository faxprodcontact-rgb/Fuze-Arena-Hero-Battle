// Les décors dessinés par le code : un par terrain (voir look.ts pour le choix du terrain). Sans Phaser.
import type { Scene } from './core';
import { ABYSS } from './abyss';
import { ASH } from './ash';
import { BAYOU } from './bayou';
import { MINE, SPRING } from './cave';
import { BRAMBLE } from './forest';
import { ARENA, ARMORY, LAIR } from './halls';
import { MEADOW } from './meadow';
import { STORM } from './storm';
import { TEMPLE } from './temple';
import { TOWER } from './tower';
import { TUNDRA } from './tundra';

export const SCENES: Partial<Record<string, Scene>> = {
  meadow: MEADOW, bramble: BRAMBLE, bayou: BAYOU, ash: ASH, tundra: TUNDRA, storm: STORM, temple: TEMPLE, abyss: ABYSS,
  tower: TOWER, mine: MINE, spring: SPRING, armory: ARMORY, lair: LAIR, arena: ARENA,
};
