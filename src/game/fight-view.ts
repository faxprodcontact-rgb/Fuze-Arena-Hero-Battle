// Base commune des scènes de combat (combat, accueil, aperçu d'une compétence) : le décor animé du clan, les
// personnages HD animés et leurs coups (hd-fight.ts), les chiffres, les barres de vie.
import Phaser from 'phaser';
import type { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type BattleEvent, type Hit, type SkillDef, type Slot, type Unit } from '../core/battle/types';
import { isHero } from '../core/data/heroes';
import type { Element } from '../core/types';
import { loadPxFond, placePxFond } from './bg/fond-px';
import { HdActor, hasHd, hdChar, hdStrike, loadHd, type HdHost } from './hd-fight';
import { HD_ANIM } from './hd-meta';
import { t } from './i18n';
import { ICON_CELL, ICON_INDEX } from './icons-meta';
import { battleLook, isBigBoss, monsterArtId, type Look } from './look';
import { HERO_X } from './scenes';
import { themeColor } from './theme';

export const W = 720;
/** La police des combats (la même que les titres des menus) : une seule graisse, ne jamais demander « bold ». */
export const FONT = '"Lilita One", "Trebuchet MS", "Segoe UI", Roboto, sans-serif';
/** Couleurs de l'interface des combats : les mêmes que les menus (style.css). */
export const C = { ink: 0x2a1c12, paper: 0x5c3a1e, paper2: 0xecd9a8, paper3: 0xdfc58c, sky: 0x6b8fb5, panel: 0xecd9a8, panelLight: 0xffffff, trim: 0xd9a63e, hudText: '#4a2a0e',
  green: 0x3fae5a, greenDark: 0x2a8442, red: 0xdc4f4f, redDark: 0xa83232, blue: 0x3f86e0, blueDark: 0x2a5fb5, energy: 0x4fc3ff, gold: 0xf0b530, goldDark: 0xc8860f };

/** Les couleurs du panneau de combat suivent celles des menus (variables de style.css). */
export function applyTheme() {
  C.ink = themeColor('hud-edge', C.ink);
  C.paper = themeColor('hud-under', C.paper);
  C.panel = C.paper2 = themeColor('hud-panel', C.panel);
  C.trim = themeColor('trim', C.trim);
  const light = ((C.panel >> 16) & 255) * 0.3 + ((C.panel >> 8) & 255) * 0.59 + (C.panel & 255) * 0.11 > 150;
  C.paper3 = Phaser.Display.Color.ValueToColor(C.panel).darken(light ? 12 : 18).color;
  C.hudText = light ? '#4a2a0e' : '#ffffff';
}

// Les deux équipes sont bien séparées (230 px entre les deux premières lignes, les rangs du fond assez loin des bords pour ne pas être coupés) : on voit qui fonce sur qui.
export { HERO_X };
const ENEMY_X: Record<Slot, number> = { 0: 475, 1: 475, 2: 557, 3: 638, 4: 638 };
/** Hauteur des rangées, mesurée depuis le haut du sol (`groundTop`). */
const ROW_DY: Record<Slot, number> = { 0: 90, 3: 90, 2: 180, 1: 270, 4: 270 };
/** Les pieds sont à `FEET` sous le point de la rangée. */
const FEET = 47;
/** Un grand boss est seul en face : au milieu du côté ennemi, un peu plus loin du bord pour que sa queue tienne. */
const BIG_BOSS_X = 548;

/** Les effets et la planche de pictos ont déjà été téléchargés une fois (le navigateur les a gardés). */
let laterFetched = false;

/** Couleur des statuts affichés au-dessus des combattants. */
const STATUS_COLOR: Partial<Record<string, string>> = {
  burn: '#ff8a3d', poison: '#9be15d', bleed: '#ff5a6a', regen: '#5dff9a', stun: '#ffe27a', silence: '#c39bff',
  slow: '#7fc8ff', taunt: '#ffb15c', atkUp: '#ffcf5a', atkDown: '#b0b7d6', defUp: '#7fc8ff', defDown: '#b0b7d6',
  speedUp: '#9be15d', critUp: '#ffcf5a',
};

export interface View {
  unit: Unit;
  body: Phaser.GameObjects.Container;
  /** Le dessin : un conteneur posé aux pieds (retourné pour les ennemis). */
  sprite: Phaser.GameObjects.Container;
  /** Toutes ses images (pour les teintes). */
  imgs: Phaser.GameObjects.Image[];
  bars: Phaser.GameObjects.Graphics;
  homeX: number;
  homeY: number;
  /** Hauteur et largeur de la barre de vie (au-dessus de la tête du dessin). */
  barY: number;
  barW: number;
  /** Vie affichée : elle baisse quand le coup est montré, pas quand les règles l'ont calculé. */
  hp: number;
  /** Petits pictos des effets en cours (brûlure, étourdi, bonus…) au-dessus de la barre de vie. */
  stIcons?: Phaser.GameObjects.Image[];
  stKey?: string;
  sx: number;
  sy: number;
  /** Le personnage HD animé (hd-fight.ts) : il joue ses propres animations. */
  hd?: HdActor;
}

/**
 * Chacun son tour : pendant qu'un coup se joue, le combat est en pause (les règles ne changent pas, seul l'affichage
 * attend). Durée d'un tour, en ms à vitesse ×1 ; ×2 et ×3 les raccourcissent. Un coup HD dure le temps de son animation.
 */
const TURN_MS = { attack: 470, skill: 1450, passive: 260, wave: 550 };

export abstract class FightScene extends Phaser.Scene {
  protected battle!: Battle;
  protected views = new Map<string, View>();
  /** Haut du sol : tout le terrain se place à partir de là. */
  protected groundTop = 380;
  /** Les boss des combats « au score » (boss du jour, de guilde) sont dessinés plus gros. */
  protected bigBoss = false;
  /** Resserre le terrain vers le centre (écran d'accueil, plus étroit). */
  protected xSquash = 1;
  /** Premier plan du décor (il passe devant les combattants, s'efface pendant les compétences). */
  private fg: Phaser.GameObjects.GameObject[] = [];
  /** Bas du terrain (pour l'assombrir en entier). */
  private arenaBottom = 0;
  /** Le décor et le clan des monstres de ce combat. */
  protected look: Look = battleLook('arena', '');
  /** Durée du coup qui vient d'être lancé (ms réelles), quand elle n'est pas la durée habituelle. */
  protected turnMs?: number;
  private lastNow = 0;

  /** Les combattants à charger avant le combat. */
  protected abstract preloadUnits(): { id?: string; defId: string; element: string }[];

  /** Le haut du sol et le bas du terrain : chaque écran les fixe (le décor est dessiné pour cette place). */
  protected arenaBox(): { groundTop: number; bottom: number } {
    return { groundTop: this.groundTop, bottom: this.scale.height };
  }

  preload() {
    loadPxFond(this, this.look.fond);
    // La planche de pictos n'empêche pas la scène de démarrer : elle arrive en arrière-plan une fois le combat affiché.
    this.events.once('create', () => {
      const fetchLater = () => {
        if (!this.sys.isActive()) return;
        if (!this.textures.exists('icons')) this.load.spritesheet('icons', 'art/icons.webp', { frameWidth: ICON_CELL, frameHeight: ICON_CELL });
        this.load.start();
        laterFetched = true;
      };
      // au tout premier lancement, on laisse d'abord arriver ce que l'écran montre (pictos, polices) ; ensuite c'est immédiat
      if (laterFetched) fetchLater();
      else if (document.readyState === 'complete') setTimeout(fetchLater, 800);
      else addEventListener('load', () => setTimeout(fetchLater, 800), { once: true });
    });
    for (const u of this.preloadUnits()) {
      const id = this.charId(u);
      if (hasHd(id)) loadHd(this, id, u.element as Element);
    }
  }

  /** Le dessin d'un combattant : un héros, ou le monstre du clan de ce combat (général ou grand boss pour un boss). */
  protected charId(u: { id?: string; defId: string; element: string }): string {
    return isHero(u.defId) ? u.defId : monsterArtId(u.defId, u.element as Element, this.look);
  }

  protected text(x: number, y: number, value: string, size = 28, color = '#ffffff') {
    return this.add
      .text(x, y, value, { fontFamily: FONT, fontSize: `${size}px`, color, align: 'center' })
      .setOrigin(0.5)
      .setStroke('#1a1420', Math.max(3, Math.round(size * 0.13)))
      .setShadow(0, Math.max(2, Math.round(size * 0.07)), '#2f2244', 0, true, true);
  }

  /** Le décor animé du clan : son bas 430 unités sous le haut du sol (= le bas du terrain ; l'accueil en coupe le bas). */
  protected drawArena(bottom: number) {
    this.arenaBottom = bottom;
    const placed = placePxFond(this, this.look.fond, this.arenaBox().groundTop + 430);
    if (placed.ok) {
      this.fg = placed.front;
      return;
    }
    // décor pas encore arrivé (réseau coupé) : un ciel et un sol tout simples
    const g = this.add.graphics().setDepth(-10);
    const top = this.groundTop;
    g.fillGradientStyle(0x2b3a78, 0x2b3a78, 0x6b5ca8, 0x6b5ca8, 1);
    g.fillRect(0, 0, W, top + 40);
    g.fillGradientStyle(0x3d6b4a, 0x3d6b4a, 0x274a34, 0x274a34, 1);
    g.fillRect(0, top, W, bottom - top);
  }

  protected slotPos(unit: Unit): { x: number; y: number } {
    const hero = unit.side === 'hero';
    const x = hero ? HERO_X[unit.slot] : ENEMY_X[unit.slot];
    return { x: W / 2 + (x - W / 2) * this.xSquash, y: this.groundTop + ROW_DY[unit.slot] };
  }

  protected addView(unit: Unit, enter = false, speed = 1) {
    const hero = unit.side === 'hero';
    const id = this.charId(unit);
    const big = isBigBoss(id);
    let { x, y } = this.slotPos(unit);
    if (big) x = W / 2 + (BIG_BOSS_X - W / 2) * this.xSquash;
    const body = this.add.container(enter ? x + (hero ? -320 : 320) : x, y).setDepth(y);
    const fig = this.add.container(0, FEET);
    const imgs: Phaser.GameObjects.Image[] = [];
    let shadow: Phaser.GameObjects.Ellipse;
    let barY: number;
    // un grand boss est dessiné à sa taille (deux fois un héros) ; un général de clan qui joue un boss est agrandi
    const boost = big ? 1 : unit.boss ? (this.bigBoss ? 1.45 : 1.2) : 1;
    const barW = big ? 170 : unit.boss ? 130 : 86;
    let hd: HdActor | undefined;
    if (hasHd(id) && this.textures.exists(`hd-${id}`)) {
      // un pixel du dessin = `scale` unités ; les pieds sur la ligne de sol
      const ch = hdChar(id), k = HD_ANIM.scale * boost;
      hd = new HdActor(this, fig, id, k, unit.element);
      imgs.push(hd.img);
      shadow = this.add.ellipse(0, FEET, Math.min(big ? 300 : 160, (ch.sol[1]! - ch.sol[0]!) * k * 1.1), big ? 30 : 20, 0x000000, 0.3);
      barY = FEET - Math.min(ch.top * k, (big ? 290 : 126) * boost) - 6;
    } else {
      // dessin pas encore arrivé : seulement son ombre et sa barre de vie
      shadow = this.add.ellipse(0, FEET, 90, 20, 0x000000, 0.3);
      barY = -72;
    }
    fig.setScale(hero ? 1 : -1, 1);
    const bars = this.add.graphics();
    body.add([shadow, fig, bars]);
    this.views.set(unit.id, { unit, body, sprite: fig, imgs, bars, homeX: x, homeY: body.y, barY, barW, hp: unit.hp, sx: fig.scaleX, sy: 1, hd });
    if (enter) this.tweens.add({ targets: body, x, duration: 450 / speed, ease: 'Back.easeOut' });
  }

  protected clearViews(side?: 'hero' | 'enemy') {
    for (const [id, v] of this.views) {
      if (side && v.unit.side !== side) continue;
      v.body.destroy();
      this.views.delete(id);
    }
  }

  /** Les effets en cours, en petits pictos alignés au-dessus de la barre de vie (4 au plus). */
  private syncStatusIcons(v: View) {
    const kinds = [...new Set(v.unit.statuses.map((x) => x.kind))].filter((k) => `st-${k}` in ICON_INDEX).slice(0, 4);
    if (!this.textures.exists('icons')) return;
    const key = kinds.join(',');
    if (key === v.stKey) return;
    v.stKey = key;
    v.stIcons?.forEach((i) => i.destroy());
    v.stIcons = kinds.map((k, i) => {
      const img = this.add.image(-v.barW / 2 + 12 + i * 27, v.barY - 18, 'icons', ICON_INDEX[`st-${k}`]).setDisplaySize(27, 27);
      v.body.add(img);
      return img;
    });
  }

  protected syncUnits() {
    // quand le décor s'assombrit (compétence), le premier plan s'efface : le décor assombri est déjà dessous
    const fa = this.veil?.active ? 1 - Math.min(1, this.veil.fillAlpha * 2.2) : 1;
    const dt = this.lastNow ? Math.min(100, this.time.now - this.lastNow) : 0;
    this.lastNow = this.time.now;
    for (const v of this.views.values()) v.hd?.update(dt);
    for (const o of this.fg) (o as unknown as Phaser.GameObjects.Components.Alpha).setAlpha(fa);
    for (const v of this.views.values()) {
      const u = v.unit;
      const g = v.bars;
      g.clear();
      if (v.hp <= 0 && u.hp <= 0) continue;
      const w = v.barW;
      const y = v.barY;
      g.fillStyle(0x15101c);
      g.fillRoundedRect(-w / 2 - 2, y - 2, w + 4, 16, 6);
      g.fillStyle(0x2a2230);
      g.fillRoundedRect(-w / 2, y, w, 12, 4);
      const wHp = w * (Math.max(0, v.hp) / u.maxHp);
      if (wHp > 1) {
        g.fillStyle(u.side === 'hero' ? C.green : C.red);
        g.fillRoundedRect(-w / 2, y, wHp, 12, Math.min(4, wHp / 2));
        g.fillStyle(0xffffff, 0.35);
        g.fillRect(-w / 2 + 2, y + 1.5, Math.max(0, wHp - 4), 3);
      }
      if (u.shield > 0) {
        g.fillStyle(0x9fd8ff, 0.85);
        g.fillRoundedRect(-w / 2, y, Math.min(w, w * (u.shield / u.maxHp)), 6, 3);
      }
      g.fillStyle(C.energy);
      g.fillRect(-w / 2, y + 15, w * (u.energy / ENERGY_MAX), 4);
      this.syncStatusIcons(v);
      // étourdi : il vacille (le dessin respire déjà tout seul)
      v.sprite.setAngle(u.stun > 0 ? Math.sin(this.time.now / 60) * 8 : 0);
    }
  }

  /** Une teinte sur tout le dessin, ou aucune. */
  private tint(v: View, color?: number) {
    for (const img of v.imgs) {
      if (color === undefined) img.clearTint();
      else img.setTint(color);
    }
  }

  /** Ce que chaque scène fait de plus quand une vague arrive, qu'un combattant tombe, ou à la fin. */
  protected onWave(index: number): void {
    void index;
  }
  protected onDeath(unit: Unit): void {
    void unit;
  }
  protected abstract onEnd(win: boolean): void;

  private queue: { e: BattleEvent; speed: number }[] = [];
  private busy = 0;
  private stepAcc = 0;

  /**
   * Fait avancer le combat un coup à la fois : on joue le coup suivant de la file, on attend qu'il soit fini, et
   * quand la file est vide les règles avancent jusqu'au prochain coup. Les coups calculés au même instant passent
   * donc l'un après l'autre, héros comme ennemis.
   */
  protected advance(delta: number, speed: number) {
    if (this.busy > 0) {
      this.busy -= delta;
      return;
    }
    while (this.queue.length) {
      const q = this.queue.shift()!;
      this.turnMs = undefined;
      this.handle([q.e], q.speed);
      const ms = q.e.type === 'attack' ? TURN_MS.attack : q.e.type === 'skill' ? TURN_MS.skill : q.e.type === 'passive' ? TURN_MS.passive : q.e.type === 'wave' ? TURN_MS.wave : 0;
      if (this.turnMs !== undefined) {
        this.busy = this.turnMs;
        return;
      }
      if (ms) {
        this.busy = ms / q.speed;
        return;
      }
    }
    // file vide : les barres de vie rattrapent les règles (brûlures, etc.), puis les règles avancent
    for (const v of this.views.values()) v.hp = v.unit.hp;
    this.stepAcc = Math.min(this.stepAcc + delta * speed, 1000);
    while (this.stepAcc >= TICK_MS && !this.battle.over) {
      this.stepAcc -= TICK_MS;
      const events = this.battle.step();
      for (const e of events) this.queue.push({ e, speed });
      if (events.some((e) => e.type !== 'tick')) {
        this.stepAcc = 0;
        break;
      }
    }
  }

  protected handle(events: BattleEvent[], speed: number) {
    for (const e of events) {
      switch (e.type) {
        case 'attack':
          if (!this.hdStrike(e.source, 'attaque', [e.hit], speed)) this.showHit(e.hit, false);
          break;
        case 'skill':
          if (!this.hdStrike(e.source, 'speciale', e.hits, speed, e.skill)) e.hits.forEach((h) => this.showHit(h, true));
          break;
        case 'passive':
          this.time.delayedCall(250 / speed, () => e.hits.forEach((h) => this.showHit(h, false)));
          break;
        case 'tick':
          e.hits.forEach((h) => this.showHit(h, false));
          break;
        case 'death': {
          const v = this.views.get(e.unit);
          if (v) {
            this.tweens.add({ targets: v.body, alpha: 0, y: v.body.y + 20, angle: v.unit.side === 'hero' ? -20 : 20, duration: 450 });
            this.onDeath(v.unit);
          }
          break;
        }
        case 'wave':
          this.clearViews('enemy');
          for (const u of e.units) this.addView(u, true, speed);
          this.onWave(e.index);
          break;
        case 'end':
          this.onEnd(e.win);
          break;
      }
    }
  }

  /** Un éclair de lumière bref au point d'impact, avec une onde qui s'élargit. */
  private flashAt(x: number, y: number, color = 0xffffff, r = 34, t = 1) {
    const c = this.add.circle(x, y, r, color, 0.8).setDepth(1600).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: c, scale: 1.8, alpha: 0, duration: 180 * t, onComplete: () => c.destroy() });
    const ring = this.add.circle(x, y, r * 0.8).setStrokeStyle(5, color, 0.9).setDepth(1600).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: ring, scale: 3, alpha: 0, duration: 300 * t, ease: 'Cubic.easeOut', onComplete: () => ring.destroy() });
  }

  /** Le coup porte : la cible est repoussée, s'écrase un instant puis reprend sa forme. */
  private recoil(v: View, dir: number, px: number, t: number) {
    v.body.x = v.homeX + dir * px;
    this.tweens.add({ targets: v.body, x: v.homeX, duration: 170 * t, ease: 'Quad.easeOut' });
    v.sprite.setScale(v.sx, v.sy);
    this.tweens.add({ targets: v.sprite, scaleX: v.sx * 0.9, scaleY: v.sy * 1.06, duration: 50 * t, yoyo: true });
  }

  /** Le décor s'assombrit pendant une compétence : seuls les combattants et les effets restent éclairés. Un seul voile, réutilisé. */
  private veil?: Phaser.GameObjects.Rectangle;
  private dim(ms: number) {
    if (!this.veil || !this.veil.active) this.veil = this.add.rectangle(0, 0, W, this.arenaBottom || 2000, 0x05030f, 0).setOrigin(0).setDepth(5);
    const r = this.veil;
    this.tweens.killTweensOf(r);
    this.tweens.add({ targets: r, fillAlpha: 0.55, duration: 140, ease: 'Quad.easeOut' });
    this.tweens.add({ targets: r, fillAlpha: 0, delay: ms, duration: 260 });
  }

  /** Ce que la mise en scène HD emprunte à la scène (hd-fight.ts). */
  private hdHost?: HdHost;
  /**
   * Le coup d'un personnage : sa vraie animation, le déplacement jusqu'à la cible (corps à corps), le projectile
   * jusqu'à la vraie case, l'impact sur la cible, la lumière de la charge. Renvoie faux s'il n'est pas encore dessiné.
   */
  private hdStrike(sourceId: string, which: 'attaque' | 'speciale', hits: Hit[], speed: number, skill?: SkillDef): boolean {
    const src = this.views.get(sourceId);
    if (!src?.hd) return false;
    this.hdHost ??= {
      view: (id) => this.views.get(id),
      allies: (side) => [...this.views.values()].filter((v) => v.unit.side === side),
      showHit: (h, big) => this.showHit(h, big),
      recoil: (v, dir, px, t) => this.recoil(v as View, dir, px, t),
      flash: (x, y, color, r, t) => this.flashAt(x, y, color, r, t),
      feetY: FEET,
    };
    if (which === 'speciale') {
      // le nom de la compétence au-dessus du lanceur, le décor s'assombrit un peu le temps du coup
      const hero = src.unit.side === 'hero';
      const name = this.text(src.body.x, src.body.y + src.barY - 34, t(`skill.${skill?.id ?? ''}`), 28, hero ? '#ffe27a' : '#ff8a8a').setDepth(2000);
      this.tweens.add({ targets: name, y: name.y - 30, alpha: 0, delay: 650 / speed, duration: 450 / speed, onComplete: () => name.destroy() });
    }
    const ms = hdStrike(this, this.hdHost, src, which, hits, speed, skill);
    if (which === 'speciale') this.dim(Math.max(300, ms - 300));
    this.turnMs = ms + 260 / speed;
    return true;
  }

  private showHit(hit: Hit, big: boolean) {
    const v = this.views.get(hit.target);
    if (!v) return;
    if (hit.kind === 'damage') v.hp = Math.max(0, v.hp - hit.amount);
    else if (hit.kind === 'heal') v.hp = Math.min(v.unit.maxHp, v.hp + hit.amount);
    else if (hit.kind === 'revive') v.hp = v.unit.hp;
    if (hit.kind === 'miss' || hit.kind === 'status' || hit.kind === 'revive') {
      if (hit.kind === 'revive') this.tweens.add({ targets: v.body, alpha: 1, y: v.homeY, angle: 0, duration: 400 });
      const label = hit.kind === 'miss' ? t('fx.miss') : hit.kind === 'revive' ? '+' : t(`st.${hit.status}`, { n: '' }).replace(/[+−-]\s*%/, '').trim();
      const color = hit.kind === 'miss' ? '#c8d0ff' : hit.kind === 'revive' ? '#5dff9a' : STATUS_COLOR[hit.status ?? 'stun'] ?? '#ffe27a';
      // un effet ou un relevé : son picto (planche des pictos) ; à défaut (planche pas encore arrivée), son nom écrit
      const pic = hit.kind === 'status' ? `st-${hit.status}` : hit.kind === 'revive' ? 'revive' : '';
      const icon = pic in ICON_INDEX && this.textures.exists('icons');
      const y0 = v.body.y + v.barY - 30;
      const n = icon ? this.add.image(v.body.x, y0, 'icons', ICON_INDEX[pic]).setDisplaySize(40, 40).setDepth(2000) : this.text(v.body.x, y0, label, 22, color).setDepth(2000);
      this.tweens.add({ targets: n, y: n.y - 34, alpha: 0, duration: icon ? 1000 : 800, onComplete: () => n.destroy() });
      return;
    }
    const x = v.body.x + Phaser.Math.Between(-18, 18);
    let color: string;
    let label = hit.amount.toLocaleString('fr-FR');
    if (hit.kind === 'heal') {
      color = '#5dff9a';
      label = `+${label}`;
    } else if (hit.kind === 'shield') {
      // Un bouclier se voit à son anneau bleu, sans chiffre (sinon la scène devient illisible).
      const ring = this.add.circle(v.body.x, v.body.y, 70).setStrokeStyle(5, 0x9fd8ff).setDepth(998);
      this.tweens.add({ targets: ring, scale: 1.3, alpha: 0, duration: 500, onComplete: () => ring.destroy() });
      return;
    } else {
      color = hit.crit ? '#ffe27a' : hit.advantage ? '#ffb15c' : v.unit.side === 'hero' ? '#ff9b9b' : '#ffffff';
      // touché : le dessin rougit un instant
      this.tint(v, 0xff9a9a);
      this.time.delayedCall(90, () => this.tint(v));
      if (hit.stun) {
        // le coup étourdit : le picto de l'étourdissement saute au-dessus de la tête, puis s'efface
        const y0 = v.body.y + v.barY + 10;
        if (this.textures.exists('icons')) {
          const star = this.add.image(v.body.x + 30, y0, 'icons', ICON_INDEX['st-stun']).setDisplaySize(32, 32).setDepth(2000);
          this.tweens.add({ targets: star, y: y0 - 18, alpha: 0, duration: 900, ease: 'Quad.easeOut', onComplete: () => star.destroy() });
        }
      }
    }
    if (hit.dot) {
      color = hit.kind === 'heal' ? '#5dff9a' : STATUS_COLOR[hit.status ?? 'burn'] ?? color;
      const n = this.text(x, v.body.y - 40, label, 20, color).setDepth(2000);
      this.tweens.add({ targets: n, y: n.y - 60, alpha: 0, duration: 750, ease: 'Quad.easeOut', onComplete: () => n.destroy() });
      return;
    }
    // le chiffre jaillit au-dessus de la tête (gros, puis il se pose), tient un instant, puis monte et s'efface
    const y0 = v.body.y + v.barY - 8;
    const n = this.text(x, y0, hit.crit ? `${label}!` : label, (big ? 34 : 26) + (hit.crit ? 8 : 0), color).setDepth(2000);
    n.setScale(hit.crit ? 2 : 1.7);
    this.tweens.add({ targets: n, scale: 1, duration: 200, ease: 'Back.easeOut' });
    this.tweens.add({ targets: n, y: y0 - 46, alpha: 0, delay: 420, duration: 520, ease: 'Quad.easeIn', onComplete: () => n.destroy() });
  }

  protected banner(label: string, y = 300) {
    const b = this.text(W / 2, y, label, 56).setDepth(3000).setScale(0.5);
    this.tweens.add({ targets: b, scale: 1, duration: 250, ease: 'Back.easeOut' });
    this.tweens.add({ targets: b, alpha: 0, delay: 800, duration: 300, onComplete: () => b.destroy() });
  }
}
