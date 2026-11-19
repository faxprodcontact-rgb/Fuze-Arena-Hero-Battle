import Phaser from 'phaser';
import { makeTextures } from '../art';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('boot');
  }

  create() {
    makeTextures(this);
    this.scene.start('home');
  }
}
