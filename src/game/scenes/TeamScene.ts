// Section : placer ses héros sur les postes et les faire monter de niveau.
// Toucher une carte = ajouter / retirer le héros. Toucher deux postes = les échanger.
import Phaser from 'phaser';
import type { Slot } from '../../core/battle/types';
import { LEADER_SLOT } from '../../core/battle/types';
import { PROTO_HEROES, PROTO_MAX_LEVEL, protoLevelCost, protoSlots } from '../../core/data/prototype';
import { ELEMENT_COLOR, FACTION_COLOR, UI } from '../art';
import { t } from '../i18n';
import { loadSave, writeSave } from '../save';
import { W, background, button, goldBar, panel, pointAt, text } from '../ui';

/** Position des postes à l'écran, comme au combat : l'avant est à droite. */
export const SLOT_POS: Record<Slot, { x: number; y: number }> = {
  3: { x: 170, y: 300 }, 4: { x: 170, y: 500 }, 2: { x: 360, y: 400 }, 0: { x: 550, y: 300 }, 1: { x: 550, y: 500 },
};

const PREFERRED: Record<string, Slot[]> = {
  knight: [0, 1, 2, 3, 4], demon: [1, 0, 2, 3, 4], assassin: [1, 0, 3, 2, 4],
  mage: [2, 3, 4, 1, 0], angel: [3, 4, 2, 1, 0], myth: [4, 3, 2, 1, 0],
};

export class TeamScene extends Phaser.Scene {
  private picked: Slot | undefined;

  constructor() {
    super('team');
  }

  create() {
    this.picked = undefined;
    writeSave({ unseen: false });
    this.draw();
  }

  private draw() {
    this.children.removeAll(true);
    const save = loadSave();
    const max = protoSlots(save.cleared);
    background(this);
    goldBar(this, save.gold);
    button(this, 100, 50, 160, 64, `‹ ${t('back')}`, UI.panelLight, () => this.scene.start('home'), 26);
    text(this, W / 2, 130, `${t('team')}  ${save.formation.length} / ${max}`, 40, '#ffe27a');

    panel(this, W / 2, 400, 660, 400, UI.panel, 0.85);
    const lane = this.add.graphics();
    lane.lineStyle(3, 0x3a4180, 1);
    lane.lineBetween(265, 220, 265, 580);
    lane.lineBetween(455, 220, 455, 580);
    text(this, 680, 400, '›', 60, '#e5484d');

    for (const slot of [0, 1, 2, 3, 4] as Slot[]) this.drawSlot(slot);

    const leader = save.formation.find(([, s]) => s === LEADER_SLOT)?.[0];
    text(this, 360, 545, leader ? `♛ ${t(`talent.${leader}`)}` : '♛', 22, '#ffe27a');

    PROTO_HEROES.forEach((hero, i) => this.drawCard(hero.id, 195 + (i % 2) * 330, 720 + Math.floor(i / 2) * 180));

    // Une place libre et un héros sur le banc : un doigt montre ce héros.
    const bench = PROTO_HEROES.findIndex((h) => save.owned.includes(h.id) && !save.formation.some(([id]) => id === h.id));
    if (save.formation.length < max && bench >= 0) pointAt(this, 110 + (bench % 2) * 330, 690 + Math.floor(bench / 2) * 180);
  }

  /** Redessine après le geste en cours (on ne détruit pas un bouton pendant qu'on le touche). */
  private redraw() {
    this.time.delayedCall(0, () => this.draw());
  }

  private drawSlot(slot: Slot) {
    const save = loadSave();
    const { x, y } = SLOT_POS[slot];
    const hero = save.formation.find(([, s]) => s === slot)?.[0];
    const leader = slot === LEADER_SLOT;
    const ring = this.add.circle(x, y, 74, 0x14162b, 0.8).setStrokeStyle(5, this.picked === slot ? 0xffffff : leader ? UI.gold : 0x4a5290);
    if (leader) text(this, x, y - 92, '♛', 30, '#ffe27a');
    if (hero) {
      this.add.image(x, y, `unit-${hero}`).setScale(1.05);
      text(this, x, y + 62, `${t('levelShort')} ${save.levels[hero] ?? 1}`, 22);
    }
    ring.setInteractive({ useHandCursor: true }).on('pointerup', () => this.tapSlot(slot));
  }

  private tapSlot(slot: Slot) {
    const save = loadSave();
    if (this.picked === undefined) {
      if (save.formation.some(([, s]) => s === slot)) this.picked = slot;
    } else {
      const from = this.picked;
      this.picked = undefined;
      const formation = save.formation.map(([id, s]): [string, Slot] => [id, s === from ? slot : s === slot ? from : s]);
      writeSave({ formation });
    }
    this.redraw();
  }

  private drawCard(id: string, x: number, y: number) {
    const save = loadSave();
    const def = PROTO_HEROES.find((h) => h.id === id)!;
    const owned = save.owned.includes(id);
    const inTeam = save.formation.some(([h]) => h === id);
    const g = this.add.graphics();
    g.fillStyle(UI.panel, owned ? 1 : 0.5);
    g.fillRoundedRect(x - 155, y - 80, 310, 160, 20);
    if (inTeam) {
      g.lineStyle(5, UI.green);
      g.strokeRoundedRect(x - 155, y - 80, 310, 160, 20);
    }
    g.fillStyle(FACTION_COLOR[def.faction], owned ? 0.35 : 0.1);
    g.fillRoundedRect(x - 145, y - 70, 120, 140, 16);
    const img = this.add.image(x - 85, y, `unit-${id}`).setScale(0.95);
    if (!owned) {
      img.setTint(0x000000).setAlpha(0.6);
      text(this, x + 60, y, '?', 54, UI.textDim);
      return;
    }
    const level = save.levels[id] ?? 1;
    text(this, x + 60, y - 45, t(`hero.${id}`), 26).setOrigin(0.5);
    this.add.circle(x + 135, y - 62, 10, ELEMENT_COLOR[def.element]);
    text(this, x + 60, y - 10, `${t('levelShort')} ${level}`, 24, UI.textDim, 'normal');

    const zone = this.add.zone(x - 85, y, 130, 150).setInteractive({ useHandCursor: true });
    zone.on('pointerup', () => this.toggle(id));

    if (level >= PROTO_MAX_LEVEL) {
      text(this, x + 60, y + 45, t('max'), 26, '#ffe27a');
      return;
    }
    const cost = protoLevelCost(level);
    const up = button(this, x + 60, y + 45, 160, 56, `▲ ${cost}`, UI.gold, () => {
      const s = loadSave();
      if (s.gold < cost) return;
      writeSave({ gold: s.gold - cost, levels: { ...s.levels, [id]: level + 1 } });
      this.redraw();
    }, 24);
    up.label.setColor('#3a2a00');
    up.setEnabled(save.gold >= cost);
  }

  /** Ajoute le héros à son poste préféré libre, ou le retire de la section. */
  private toggle(id: string) {
    const save = loadSave();
    const max = protoSlots(save.cleared);
    if (save.formation.some(([h]) => h === id)) {
      if (save.formation.length <= 1) return;
      writeSave({ formation: save.formation.filter(([h]) => h !== id) });
    } else {
      if (save.formation.length >= max) {
        this.cameras.main.shake(150, 0.004);
        return;
      }
      const taken = new Set(save.formation.map(([, s]) => s));
      const slot = (PREFERRED[id] ?? [2, 0, 1, 3, 4]).find((s) => !taken.has(s))!;
      writeSave({ formation: [...save.formation, [id, slot]] });
    }
    this.picked = undefined;
    this.redraw();
  }
}
