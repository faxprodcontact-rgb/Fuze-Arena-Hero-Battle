// Dessins provisoires, faits par le code (le vrai style graphique arrive à l'étape 4).
// Tous les personnages regardent vers la droite ; les monstres sont retournés au combat.
import Phaser from 'phaser';
import type { Element, Faction } from '../core/types';

export const FACTION_COLOR: Record<Faction, number> = {
  knights: 0xc9a227, angels: 0xe9e4f5, mages: 0x7b4bd6, assassins: 0x3a3f58, demons: 0xb3262e, myths: 0x2a9d8f,
};

export const ELEMENT_COLOR: Record<Element, number> = {
  fire: 0xff6b3d, water: 0x3da5ff, wind: 0x5bd17a, earth: 0xc08a4a,
};

export const UI = {
  bg: 0x14162b, panel: 0x1f2340, panelLight: 0x2c3260, gold: 0xffc94a, text: '#ffffff', textDim: '#a9b0d6',
  green: 0x3ccf7a, red: 0xe5484d, blue: 0x4c8dff, energy: 0x4fd1ff,
};

const SKIN = 0xf2c9a0;
const S = 128;

type Draw = (g: Phaser.GameObjects.Graphics) => void;

function eyes(g: Phaser.GameObjects.Graphics, color = 0x1b1b2f, y = 44) {
  g.fillStyle(color);
  g.fillCircle(69, y, 3.2);
  g.fillCircle(80, y, 3.2);
}

function body(g: Phaser.GameObjects.Graphics, color: number, head = SKIN) {
  g.fillStyle(color);
  g.fillRoundedRect(42, 62, 44, 50, 14);
  g.fillStyle(head);
  g.fillCircle(66, 44, 22);
}

const HEROES: Record<string, Draw> = {
  knight: (g) => {
    body(g, FACTION_COLOR.knights);
    g.fillStyle(0x9aa3b5);
    g.slice(66, 44, 24, Math.PI, 0, false);
    g.fillPath();
    g.fillRect(42, 40, 48, 6);
    eyes(g);
    g.fillStyle(0x8a6d14);
    g.fillRoundedRect(84, 66, 26, 36, 8);
    g.fillStyle(0xfff3c4);
    g.fillRect(95, 70, 4, 28);
    g.fillRect(88, 80, 18, 4);
    g.fillStyle(0xd7dce6);
    g.fillRect(30, 50, 6, 50);
  },
  angel: (g) => {
    g.fillStyle(0xffffff, 0.9);
    g.fillEllipse(34, 74, 34, 50);
    g.fillEllipse(28, 64, 26, 34);
    body(g, FACTION_COLOR.angels);
    g.fillStyle(0xffe08a);
    g.slice(66, 40, 23, Math.PI, 0, false);
    g.fillPath();
    eyes(g, 0x2f5fd0);
    g.lineStyle(4, 0xffd34a);
    g.strokeEllipse(66, 14, 34, 10);
  },
  mage: (g) => {
    body(g, FACTION_COLOR.mages);
    eyes(g);
    g.fillStyle(0x4b2a8f);
    g.fillTriangle(38, 32, 94, 32, 74, -2);
    g.fillRect(36, 28, 60, 8);
    g.fillStyle(0xffd34a);
    g.fillCircle(80, 14, 4);
    g.fillStyle(0x6b4a2a);
    g.fillRect(98, 40, 5, 72);
    g.fillStyle(0xff6b3d);
    g.fillCircle(100, 36, 9);
  },
  assassin: (g) => {
    body(g, FACTION_COLOR.assassins);
    g.fillStyle(0x23263a);
    g.slice(66, 44, 25, Math.PI * 0.9, Math.PI * 0.1, false);
    g.fillPath();
    g.fillStyle(SKIN);
    g.fillEllipse(74, 46, 26, 22);
    eyes(g, 0xc81d3a);
    g.fillStyle(0xc81d3a);
    g.fillRect(48, 58, 40, 7);
    g.fillTriangle(48, 58, 30, 70, 48, 66);
    g.fillStyle(0xd7dce6);
    g.fillTriangle(92, 80, 116, 70, 92, 88);
  },
  demon: (g) => {
    g.fillStyle(0x7a1219);
    g.fillTriangle(30, 104, 18, 84, 40, 96);
    body(g, FACTION_COLOR.demons, 0xe8a28c);
    g.fillStyle(0x2b1a1a);
    g.fillTriangle(48, 30, 42, 6, 58, 26);
    g.fillTriangle(80, 26, 92, 4, 88, 30);
    g.fillStyle(0x2b1a1a);
    g.slice(66, 40, 22, Math.PI, 0, false);
    g.fillPath();
    eyes(g, 0xffd34a);
  },
  myth: (g) => {
    body(g, FACTION_COLOR.myths);
    g.fillStyle(0xffffff);
    g.fillRoundedRect(46, 70, 36, 8, 3);
    eyes(g);
    g.fillStyle(0xe0e0e0);
    g.fillEllipse(70, 60, 30, 18);
    g.fillStyle(0x3fa34d);
    for (let i = 0; i < 6; i++) g.fillEllipse(46 + i * 8, 26 - Math.sin((i / 5) * Math.PI) * 6, 9, 6);
    g.fillStyle(0xffd34a);
    g.fillTriangle(104, 30, 92, 62, 102, 60);
    g.fillTriangle(102, 56, 112, 56, 94, 92);
  },
};

const MONSTERS: Record<string, Draw> = {
  goblin: (g) => {
    g.fillStyle(0x6b4a2a);
    g.fillRoundedRect(46, 70, 38, 40, 12);
    g.fillStyle(0x5bb34a);
    g.fillCircle(64, 52, 22);
    g.fillTriangle(44, 46, 22, 36, 46, 58);
    g.fillTriangle(84, 46, 104, 36, 82, 58);
    eyes(g, 0xffe14a, 50);
    g.fillStyle(0x8a5a2b);
    g.fillRoundedRect(88, 58, 12, 44, 5);
  },
  archer: (g) => {
    g.fillStyle(0x2c2c3a);
    g.fillRoundedRect(46, 66, 36, 44, 10);
    g.fillStyle(0xeeeadf);
    g.fillCircle(64, 44, 20);
    g.fillStyle(0x1b1b2f);
    g.fillCircle(70, 42, 5);
    g.fillCircle(81, 42, 5);
    g.lineStyle(4, 0x9b6b3a);
    g.beginPath();
    g.arc(86, 80, 26, -1.2, 1.2);
    g.strokePath();
  },
  golem: (g) => {
    g.fillStyle(0x7d8191);
    g.fillRoundedRect(28, 40, 72, 72, 18);
    g.fillStyle(0x6a6e7c);
    g.fillRoundedRect(42, 14, 46, 36, 10);
    g.fillStyle(0x4fd1ff);
    g.fillRect(66, 26, 7, 7);
    g.fillRect(79, 26, 7, 7);
    g.fillStyle(0x5c606d);
    g.fillCircle(46, 66, 6);
    g.fillCircle(80, 92, 7);
  },
  shaman: (g) => {
    g.fillStyle(0x4f7a3a);
    g.fillRoundedRect(44, 64, 40, 46, 12);
    g.fillStyle(0x5bb34a);
    g.fillCircle(64, 46, 20);
    g.fillStyle(0xf3efe3);
    g.fillRoundedRect(58, 32, 30, 26, 8);
    g.fillStyle(0x1b1b2f);
    g.fillCircle(68, 44, 3.5);
    g.fillCircle(79, 44, 3.5);
    g.fillStyle(0x6b4a2a);
    g.fillRect(94, 30, 5, 80);
    g.fillStyle(0xe5484d);
    g.fillTriangle(96, 30, 110, 16, 104, 34);
  },
  ogre: (g) => {
    g.fillStyle(0x6a4a8f);
    g.fillRoundedRect(24, 52, 80, 64, 22);
    g.fillStyle(0x8a6ab3);
    g.fillCircle(64, 40, 28);
    eyes(g, 0xffe14a, 38);
    g.fillStyle(0xffffff);
    g.fillTriangle(66, 56, 70, 48, 74, 56);
    g.fillTriangle(80, 56, 84, 48, 88, 56);
    g.fillStyle(0x5a3a1a);
    g.fillRoundedRect(98, 30, 18, 70, 8);
  },
  lich: (g) => {
    g.fillStyle(0x2a1f3d);
    g.fillTriangle(30, 116, 98, 116, 64, 40);
    g.fillStyle(0xeeeadf);
    g.fillCircle(64, 40, 20);
    g.fillStyle(0x7cf7c1);
    g.fillCircle(70, 40, 4.5);
    g.fillCircle(81, 40, 4.5);
    g.fillStyle(0xffd34a);
    g.fillTriangle(46, 22, 52, 6, 58, 22);
    g.fillTriangle(58, 22, 64, 2, 70, 22);
    g.fillTriangle(70, 22, 76, 6, 82, 22);
    g.fillStyle(0x7cf7c1, 0.8);
    g.fillCircle(102, 70, 11);
  },
};

/** Fabrique toutes les images du prototype une fois au démarrage. */
export function makeTextures(scene: Phaser.Scene): void {
  const g = scene.add.graphics();
  for (const [id, draw] of [...Object.entries(HEROES), ...Object.entries(MONSTERS)]) {
    g.clear();
    draw(g);
    g.generateTexture(`unit-${id}`, S, S);
  }
  g.clear();
  g.fillStyle(0xffffff);
  g.fillCircle(8, 8, 8);
  g.generateTexture('dot', 16, 16);
  g.clear();
  g.fillStyle(0xffffff);
  g.fillTriangle(16, 0, 32, 40, 0, 40);
  g.fillRoundedRect(8, 34, 16, 26, 6);
  g.generateTexture('finger', 32, 60);
  g.destroy();
}
