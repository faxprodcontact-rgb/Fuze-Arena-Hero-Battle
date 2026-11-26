// Petites images des effets de combat (altérations, mort), dessinées une fois par le code dans une texture.
// Lisses et douces (comme les pictos modernes) : bulle, flamme, goutte, étoile, chevron, sceau, lumière ronde.
// Une seule lumière, en haut à droite : les reflets sont posés de ce côté.
import type Phaser from 'phaser';
import type { Element } from '../core/types';

/** La lumière de chaque élément (la même que la charge des personnages HD). */
export const ELEMENT_LIGHT: Record<Element, number> = { fire: 0xffa04a, wind: 0x8cf0c0, water: 0x7cc4ff, earth: 0xe8c070 };

type Draw = (ctx: CanvasRenderingContext2D, w: number, h: number) => void;

function make(scene: Phaser.Scene, key: string, w: number, h: number, draw: Draw): string {
  if (scene.textures.exists(key)) return key;
  const c = scene.textures.createCanvas(key, w, h)!;
  draw(c.getContext(), w, h);
  c.refresh();
  return key;
}

/** Une lumière ronde et douce (blanche : on la teinte). */
export const dotTex = (s: Phaser.Scene) =>
  make(s, 'fx-dot', 48, 48, (ctx, w) => {
    const g = ctx.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.3, 'rgba(255,255,255,0.75)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, w);
  });

/** Une bulle : un voile, un bord plus clair, un reflet en haut à droite (blanche : on la teinte). */
export const bubbleTex = (s: Phaser.Scene) =>
  make(s, 'fx-bubble', 40, 40, (ctx) => {
    const g = ctx.createRadialGradient(20, 20, 4, 20, 20, 18);
    g.addColorStop(0, 'rgba(255,255,255,0.25)');
    g.addColorStop(0.8, 'rgba(255,255,255,0.55)');
    g.addColorStop(1, 'rgba(255,255,255,0.95)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(20, 20, 17, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,1)';
    ctx.beginPath();
    ctx.ellipse(26, 13, 4.5, 3, -0.6, 0, Math.PI * 2);
    ctx.fill();
  });

/** Une flamme en goutte pointée vers le haut, cœur clair (blanche : on la teinte). */
export const flameTex = (s: Phaser.Scene) =>
  make(s, 'fx-flame', 32, 48, (ctx) => {
    const g = ctx.createRadialGradient(16, 34, 1, 16, 32, 18);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.5, 'rgba(255,255,255,0.8)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(16, 2);
    ctx.bezierCurveTo(21, 14, 30, 22, 29, 33);
    ctx.bezierCurveTo(28, 42, 22, 46, 16, 46);
    ctx.bezierCurveTo(10, 46, 4, 42, 3, 33);
    ctx.bezierCurveTo(2, 22, 11, 14, 16, 2);
    ctx.fill();
  });

/** Une goutte (pointe en haut) avec son reflet (couleurs posées : rouge sang). */
export const dropTex = (s: Phaser.Scene) =>
  make(s, 'fx-drop', 20, 28, (ctx) => {
    ctx.fillStyle = '#c81e3a';
    ctx.strokeStyle = '#5a0a1c';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(10, 2);
    ctx.bezierCurveTo(14, 10, 18, 14, 18, 19);
    ctx.bezierCurveTo(18, 24, 14, 26, 10, 26);
    ctx.bezierCurveTo(6, 26, 2, 24, 2, 19);
    ctx.bezierCurveTo(2, 14, 6, 10, 10, 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,190,200,0.9)';
    ctx.beginPath();
    ctx.ellipse(13, 17, 2, 3, 0.3, 0, Math.PI * 2);
    ctx.fill();
  });

/** Une étoile à cinq branches arrondies, dorée, son contour sombre (couleurs posées). */
export const starTex = (s: Phaser.Scene) =>
  make(s, 'fx-star', 36, 36, (ctx) => {
    ctx.beginPath();
    for (let i = 0; i < 10; i++) {
      const r = i % 2 ? 7 : 16, a = -Math.PI / 2 + (i * Math.PI) / 5;
      ctx[i ? 'lineTo' : 'moveTo'](18 + Math.cos(a) * r, 19 + Math.sin(a) * r);
    }
    ctx.closePath();
    ctx.lineJoin = 'round';
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#7a4a10';
    ctx.stroke();
    const g = ctx.createLinearGradient(26, 6, 10, 32);
    g.addColorStop(0, '#fff6b8');
    g.addColorStop(1, '#ffb52e');
    ctx.fillStyle = g;
    ctx.fill();
  });

/** Un chevron arrondi pointé vers le haut (blanc : on le teinte ; retourné pour une baisse). */
export const chevronTex = (s: Phaser.Scene) =>
  make(s, 'fx-chevron', 36, 28, (ctx) => {
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = 'rgba(20,12,40,0.9)';
    ctx.lineWidth = 11;
    ctx.beginPath();
    ctx.moveTo(7, 21);
    ctx.lineTo(18, 9);
    ctx.lineTo(29, 21);
    ctx.stroke();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 6;
    ctx.stroke();
  });

/** Le sceau du silence : un anneau violet barré d'un trait (couleurs posées). */
export const sealTex = (s: Phaser.Scene) =>
  make(s, 'fx-seal', 40, 40, (ctx) => {
    ctx.lineCap = 'round';
    for (const [col, lw] of [['#2a1050', 9], ['#c39bff', 5]] as const) {
      ctx.strokeStyle = col;
      ctx.lineWidth = lw;
      ctx.beginPath();
      ctx.arc(20, 20, 13, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(11, 29);
      ctx.lineTo(29, 11);
      ctx.stroke();
    }
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.beginPath();
    ctx.arc(27, 12, 2, 0, Math.PI * 2);
    ctx.fill();
  });

/** Le bouclier : une bulle ovale, transparente au centre, au bord lumineux, reflet en haut à droite (blanche). */
export const shieldTex = (s: Phaser.Scene) =>
  make(s, 'fx-shield', 128, 160, (ctx, w, h) => {
    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.scale(1, h / w);
    const g = ctx.createRadialGradient(0, 0, w * 0.2, 0, 0, w / 2 - 2);
    g.addColorStop(0, 'rgba(255,255,255,0.04)');
    g.addColorStop(0.75, 'rgba(255,255,255,0.18)');
    g.addColorStop(0.93, 'rgba(255,255,255,0.7)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(0, 0, w / 2 - 1, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    // le reflet, en haut à droite
    ctx.strokeStyle = 'rgba(255,255,255,0.9)';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.ellipse(w / 2, h / 2, w / 2 - 12, h / 2 - 12, 0, -1.25, -0.55);
    ctx.stroke();
  });

/** Une petite croix de soin aux bras arrondis, bord sombre (blanche : on la teinte). */
export const plusTex = (s: Phaser.Scene) =>
  make(s, 'fx-plus', 28, 28, (ctx) => {
    ctx.lineCap = 'round';
    for (const [col, lw] of [['rgba(10,40,20,0.85)', 10], ['#ffffff', 5]] as const) {
      ctx.strokeStyle = col;
      ctx.lineWidth = lw;
      ctx.beginPath();
      ctx.moveTo(14, 6);
      ctx.lineTo(14, 22);
      ctx.moveTo(6, 14);
      ctx.lineTo(22, 14);
      ctx.stroke();
    }
  });

/** Une étincelle : un cœur plein et un halo court (se voit mieux qu'une lumière douce quand elle est petite). */
export const sparkTex = (s: Phaser.Scene) =>
  make(s, 'fx-spark', 32, 32, (ctx, w) => {
    const g = ctx.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.28, 'rgba(255,255,255,1)');
    g.addColorStop(0.45, 'rgba(255,255,255,0.45)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, w);
  });
