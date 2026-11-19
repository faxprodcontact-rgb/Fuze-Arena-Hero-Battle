// Accueil : la carte des 20 niveaux, « Combattre » et la section.
import Phaser from 'phaser';
import { PROTO_MAX_LEVEL, PROTO_STAGES, protoLevelCost, stageElement } from '../../core/data/prototype';
import { ELEMENT_COLOR, UI } from '../art';
import { t } from '../i18n';
import { loadSave, resetSave, writeSave } from '../save';
import { H, W, background, button, goldBar, panel, pointAt, redDot, text } from '../ui';

const COLS = [150, 290, 430, 570];
const ROWS_Y = [800, 660, 520, 380, 240];
const BOSSES = new Set([10, 20]);

function nodePos(stage: number): { x: number; y: number } {
  const i = stage - 1;
  const row = Math.floor(i / 4);
  const col = row % 2 === 0 ? i % 4 : 3 - (i % 4);
  return { x: COLS[col]!, y: ROWS_Y[row]! };
}

/** Il y a quelque chose à faire dans la section : nouveauté, ou assez d'or pour monter un héros. */
export function teamHasNews(): boolean {
  const save = loadSave();
  if (save.unseen) return true;
  return save.formation.some(([id]) => {
    const level = save.levels[id] ?? 1;
    return level < PROTO_MAX_LEVEL && save.gold >= protoLevelCost(level);
  });
}

export class HomeScene extends Phaser.Scene {
  private selected = 1;

  constructor() {
    super('home');
  }

  create(data: { selected?: number } = {}) {
    const save = loadSave();
    const total = PROTO_STAGES.length;
    this.selected = data.selected ?? Math.min(save.cleared + 1, total);
    background(this);
    goldBar(this, save.gold);

    button(this, 70, 50, 90, 60, save.lang === 'fr' ? 'FR' : 'EN', UI.panelLight, () => {
      writeSave({ lang: save.lang === 'fr' ? 'en' : 'fr' });
      this.scene.restart({ selected: this.selected });
    }, 26);
    button(this, 170, 50, 80, 60, '⟲', UI.panelLight, () => this.confirmReset(), 30);

    const chapter = this.selected > 10 ? 2 : 1;
    text(this, W / 2, 130, `${t('chapter')} ${chapter}`, 44, '#ffe27a');

    const path = this.add.graphics();
    path.lineStyle(10, 0x3a4180);
    path.beginPath();
    for (let s = 1; s <= total; s++) {
      const p = nodePos(s);
      if (s === 1) path.moveTo(p.x, p.y);
      else path.lineTo(p.x, p.y);
    }
    path.strokePath();

    for (let s = 1; s <= total; s++) this.drawNode(s, save.cleared);
    this.drawInfo();

    const play = button(this, W / 2, 1100, 420, 110, t('play'), UI.green, () => {
      this.scene.start('battle', { stage: this.selected });
    }, 44);
    button(this, W / 2, 1215, 300, 76, t('team'), UI.blue, () => this.scene.start('team'), 32);
    if (teamHasNews()) redDot(this, W / 2 + 140, 1215 - 34);
    if (save.cleared === 0) pointAt(this, play.x + 210, play.y, 'right');
  }

  private drawNode(stage: number, cleared: number) {
    const { x, y } = nodePos(stage);
    const boss = BOSSES.has(stage);
    const r = boss ? 52 : 42;
    const isNext = stage === cleared + 1;
    const open = stage <= cleared + 1;
    const fill = stage <= cleared ? UI.gold : isNext ? UI.blue : 0x3a3f5c;
    const node = this.add.circle(x, y, r, fill).setStrokeStyle(6, boss ? UI.red : 0xffffff, open ? 1 : 0.25);
    text(this, x, y, String(stage), boss ? 36 : 32, stage <= cleared ? '#3a2a00' : '#ffffff').setAlpha(open ? 1 : 0.45);
    this.add.circle(x + r * 0.72, y - r * 0.72, 9, ELEMENT_COLOR[stageElement(stage)]).setAlpha(open ? 1 : 0.4);
    if (isNext) this.tweens.add({ targets: node, scale: 1.12, yoyo: true, repeat: -1, duration: 600 });
    if (stage === this.selected) this.add.circle(x, y, r + 12).setStrokeStyle(4, 0xffffff, 0.9);
    if (open) {
      node.setInteractive({ useHandCursor: true });
      node.on('pointerup', () => this.scene.restart({ selected: stage }));
    }
  }

  /** Aperçu du niveau choisi : ses monstres, vague par vague. */
  private drawInfo() {
    panel(this, W / 2, 955, 640, 150, UI.panel, 0.9);
    text(this, 110, 905, `${t('stage')} ${this.selected}`, 30).setOrigin(0, 0.5);
    const waves = PROTO_STAGES[this.selected - 1] ?? [];
    let x = 70;
    waves.forEach((wave, i) => {
      if (i > 0) {
        text(this, x + 6, 975, '›', 40, UI.textDim);
        x += 26;
      }
      for (const [monster] of wave) {
        this.add.image(x + 26, 975, `unit-${monster}`).setScale(0.42).setFlipX(true);
        x += 46;
      }
    });
  }

  private confirmReset() {
    const layer = this.add.container(0, 0).setDepth(100);
    const shade = this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 0.7).setInteractive();
    layer.add([shade, panel(this, W / 2, H / 2, 560, 300), text(this, W / 2, H / 2 - 70, t('resetConfirm'), 34)]);
    layer.add(button(this, W / 2 - 130, H / 2 + 60, 200, 80, t('yes'), UI.red, () => {
      resetSave();
      this.scene.restart({});
    }));
    layer.add(button(this, W / 2 + 130, H / 2 + 60, 200, 80, t('no'), UI.panelLight, () => layer.destroy()));
  }
}
