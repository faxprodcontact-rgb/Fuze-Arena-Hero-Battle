// Base commune des scènes de combat (combat, accueil, aperçu d'une compétence) : le décor animé du clan, les
// personnages HD animés et leurs coups (hd-fight.ts), les chiffres, les barres de vie.
import Phaser from 'phaser';
import type { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type BattleEvent, type Hit, type SkillDef, type Slot, type Unit } from '../core/battle/types';
import { isHero } from '../core/data/heroes';
import type { Element } from '../core/types';
import { loadPxFond, placePxFond } from './bg/fond-px';
import { playDeath, playRevive, type DeathTier, type DeathView } from './fx-death';
import { StatusFx } from './fx-status';
import { HdActor, hasHd, hdChar, hdStrike, loadHd, type HdHost } from './hd-fight';
import { HD_ANIM } from './hd-meta';
import { t } from './i18n';
import { ICON_CELL, ICON_INDEX } from './icons-meta';
import { battleLook, heroArt, isBigBoss, monsterArtId, type Look } from './look';
import { HERO_X } from './scenes';
import { themeColor } from './theme';
import { artUrl } from './art-url';
import { vectoFig } from './vecto';

export const W = 720;
/** La police des combats (la même que les titres des menus) : une seule graisse, ne jamais demander « bold ». */
export const FONT = '"Lilita One", "Trebuchet MS", "Segoe UI", Roboto, sans-serif';
/** Couleurs de l'interface des combats : les mêmes que les menus (style.css). */
export const C = { ink: 0x2a1c12, paper: 0x5c3a1e, paper2: 0xecd9a8, paper3: 0xdfc58c, sky: 0x6b8fb5, panel: 0xecd9a8, panelLight: 0xffffff, trim: 0xd9a63e, hudText: '#4a2a0e',
  green: 0x2fc457, greenDark: 0x12823a, red: 0xff5468, redDark: 0xb01f3a, blue: 0x2f8cff, blueDark: 0x1a47b8, energy: 0x6cc4ff, gold: 0xffc22e, goldDark: 0xe58a00 };

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
/**
 * Place des combattants (choisie le 26/11, « V1 ») : `gap` = l'écart au milieu entre les deux premières colonnes
 * (unités), chaque équipe recule vers son bord ; `dx` / `dy` resserrent les équipiers (en X depuis la première colonne,
 * en Y autour du rang du milieu), `size` règle la taille des dessins.
 */
const BATTLE_LAYOUT = { gap: 288, dx: 0.88, dy: 1, size: 0.95 } as const;
/** Une place en X (côté héros, depuis le bord gauche) avec l'écart choisi ; les ennemis sont en miroir. */
const spreadX = (x: number) => (W - BATTLE_LAYOUT.gap) / 2 + (x - HERO_X[0]) * BATTLE_LAYOUT.dx;

/** Les effets et la planche de pictos ont déjà été téléchargés une fois (le navigateur les a gardés). */
let laterFetched = false;

/** Couleur des statuts affichés au-dessus des combattants. */
const STATUS_COLOR: Partial<Record<string, string>> = {
  burn: '#ff8a3d', poison: '#9be15d', bleed: '#ff5a6a', regen: '#5dff9a', stun: '#ffe27a', silence: '#c39bff',
  slow: '#7fc8ff', taunt: '#ffb15c', atkUp: '#ffcf5a', atkDown: '#b0b7d6', defUp: '#7fc8ff', defDown: '#b0b7d6',
  speedUp: '#9be15d', critUp: '#ffcf5a',
};
/** Ordre des pictos au-dessus de la barre de vie : ce qui empêche d'agir d'abord, puis les dégâts, les malus, les bonus. */
const STATUS_ORDER = ['stun', 'silence', 'taunt', 'burn', 'poison', 'bleed', 'slow', 'atkDown', 'defDown', 'atkUp', 'defUp', 'speedUp', 'critUp', 'regen'];
/** La teinte du dessin au coup d'une brûlure, d'un poison, d'un saignement. */
const DOT_TINT: Partial<Record<string, number>> = { burn: 0xffa070, poison: 0xa8f070, bleed: 0xff7080 };
/** Au plus 3 pictos, puis « +n ». */
const MAX_ICONS = 3;
const ICON_SIZE = 34;

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
  stIcons?: Phaser.GameObjects.GameObject[];
  stKey?: string;
  /** Son ombre au sol (elle rétrécit quand il tombe). */
  shadow: Phaser.GameObjects.Ellipse;
  /** Hauteur et largeur du dessin (pour placer les effets). */
  h: number;
  w: number;
  /** Les altérations dessinées sur lui (fx-status.ts). */
  fx: StatusFx;
  /** Il est en train de tomber (ou est tombé) : ses barres et ses effets ne sont plus dessinés. */
  dying?: boolean;
  /** La teinte de ses altérations (poison, lenteur), reprise après chaque coup. */
  baseTint?: number;
  /** Retiré du terrain pendant sa chute (nouvelle vague) : son conteneur se détruit à la fin de l'animation. */
  detached?: boolean;
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
  /** Le décor agrandi (combat plein écran : son sol va jusqu'en bas, sous les cartes des héros). */
  protected fondZoom = 1;
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
        if (!this.textures.exists('icons')) this.load.spritesheet('icons', artUrl('art/icons.webp'), { frameWidth: ICON_CELL, frameHeight: ICON_CELL });
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
      else loadStill(this, id);
    }
  }

  /** Le dessin d'un combattant : un héros, ou le monstre du clan de ce combat (général ou grand boss pour un boss). */
  protected charId(u: { id?: string; defId: string; element: string }): string {
    return isHero(u.defId) ? heroArt(u.defId) : monsterArtId(u.defId, u.element as Element, this.look);
  }

  protected text(x: number, y: number, value: string, size = 28, color = '#ffffff') {
    return this.add
      .text(x, y, value, { fontFamily: FONT, fontSize: `${size}px`, color, align: 'center' })
      .setOrigin(0.5)
      .setStroke('#150f36', Math.max(3, Math.round(size * 0.12)))
      .setShadow(0, Math.max(2, Math.round(size * 0.08)), '#0c0822', 0, true, true);
  }

  /** Le décor animé du clan : son bas 430 unités sous le haut du sol (= le bas du terrain ; l'accueil en coupe le bas). */
  protected drawArena(bottom: number) {
    this.arenaBottom = bottom;
    const placed = placePxFond(this, this.look.fond, this.arenaBox().groundTop + 430 * this.fondZoom, this.fondZoom);
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
    const x = hero ? spreadX(HERO_X[unit.slot]) : W - spreadX(W - ENEMY_X[unit.slot]);
    const dy = ROW_DY[2] + (ROW_DY[unit.slot] - ROW_DY[2]) * BATTLE_LAYOUT.dy;
    return { x: W / 2 + (x - W / 2) * this.xSquash, y: this.groundTop + dy };
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
    let h = 100, w = 60;
    // un grand boss est dessiné à sa taille (deux fois un héros) ; un général de clan qui joue un boss est agrandi
    const boost = (big ? 1 : unit.boss ? (this.bigBoss ? 1.45 : 1.2) : 1) * BATTLE_LAYOUT.size;
    const barW = big ? 170 : unit.boss ? 130 : 86;
    let hd: HdActor | undefined;
    if (hasHd(id) && this.textures.exists(`hd-${id}`)) {
      // un pixel du dessin = `scale` unités ; les pieds sur la ligne de sol
      const ch = hdChar(id), k = HD_ANIM.scale * boost;
      hd = new HdActor(this, fig, id, k, unit.element);
      imgs.push(hd.img);
      shadow = this.add.ellipse(0, FEET, Math.min(big ? 300 : 160, (ch.sol[1]! - ch.sol[0]!) * k * 1.1), big ? 30 : 20, 0x000000, 0.3);
      h = Math.min(ch.top * k, (big ? 290 : 126) * boost);
      w = Phaser.Math.Clamp((ch.sol[1]! - ch.sol[0]!) * k, 40, big ? 260 : 150);
      barY = FEET - h - 6;
    } else if (stillFig(id) && this.textures.exists(`vs-${id}`)) {
      // pas de planche de combat (les 3 dragons, dessinés seulement en vectoriel) : son dessin fixe, à l'échelle des
      // planches HD, pieds sur la ligne de sol ; il respire (voir stillStrike pour ses coups)
      const v = stillFig(id)!, k = HD_ANIM.scale * boost;
      const img = this.add.image(0, 0, `vs-${id}`).setOrigin(v.fx / v.w, v.fy / v.h).setDisplaySize(v.w * k, v.h * k);
      fig.add(img);
      imgs.push(img);
      this.tweens.add({ targets: img, scaleY: img.scaleY * 1.025, duration: 950, yoyo: true, repeat: -1, ease: 'Sine.easeInOut', delay: (x % 7) * 90 });
      shadow = this.add.ellipse(0, FEET, Math.min(160, v.w * k * 0.75), 20, 0x000000, 0.3);
      h = Math.min(v.fy * k, 126 * boost);
      w = Phaser.Math.Clamp(v.w * k * 0.7, 40, 150);
      barY = FEET - h - 6;
    } else {
      // dessin pas encore arrivé : seulement son ombre et sa barre de vie
      shadow = this.add.ellipse(0, FEET, 90, 20, 0x000000, 0.3);
      barY = -72;
    }
    fig.setScale(hero ? 1 : -1, 1);
    const bars = this.add.graphics();
    body.add([shadow, fig, bars]);
    const fx = new StatusFx(this, { body, fig, feet: FEET, h, w, inward: hero ? 1 : -1 });
    this.views.set(unit.id, { unit, body, sprite: fig, imgs, bars, homeX: x, homeY: body.y, barY, barW, hp: unit.hp, sx: fig.scaleX, sy: 1, hd, shadow, h, w, fx });
    if (enter) this.tweens.add({ targets: body, x, duration: 450 / speed, ease: 'Back.easeOut' });
  }

  protected clearViews(side?: 'hero' | 'enemy') {
    for (const [id, v] of this.views) {
      if (side && v.unit.side !== side) continue;
      this.views.delete(id);
      v.fx.destroy();
      // il finit de tomber avant de disparaître
      if (v.dying && v.body.alpha > 0) v.detached = true;
      else v.body.destroy();
    }
  }

  /** Les effets en cours, en petits pictos alignés au-dessus de la barre de vie (3 au plus, puis « +n »). */
  private syncStatusIcons(v: View, kinds: string[]) {
    if (!this.textures.exists('icons')) return;
    const shown = kinds.filter((k) => `st-${k}` in ICON_INDEX);
    const key = shown.join(',');
    if (key === v.stKey) return;
    v.stKey = key;
    v.stIcons?.forEach((i) => i.destroy());
    const y = v.barY - 21, step = ICON_SIZE - 2, x0 = -v.barW / 2 + ICON_SIZE / 2 - 2;
    v.stIcons = [];
    shown.slice(0, MAX_ICONS).forEach((k, i) => {
      // un rond sombre derrière chaque picto : il se lit sur n'importe quel décor
      const back = this.add.circle(x0 + i * step, y, ICON_SIZE / 2 - 1, 0x0c0822, 0.6);
      const img = this.add.image(x0 + i * step, y, 'icons', ICON_INDEX[`st-${k}`]).setDisplaySize(ICON_SIZE, ICON_SIZE);
      v.stIcons!.push(back, img);
    });
    // les autres : « +n » en pastille sur le coin du dernier picto (sans dépasser la barre de vie)
    if (shown.length > MAX_ICONS) {
      const bx = x0 + (MAX_ICONS - 1) * step + 12, by = y + 10;
      v.stIcons.push(this.add.circle(bx, by, 11, 0x0c0822, 0.9), this.text(bx, by, `+${shown.length - MAX_ICONS}`, 17, '#ffe27a'));
    }
    v.body.add(v.stIcons);
  }

  protected syncUnits() {
    // quand le décor s'assombrit (compétence), le premier plan s'efface : le décor assombri est déjà dessous
    const fa = this.veil?.active ? 1 - Math.min(1, this.veil.fillAlpha * 2.2) : 1;
    const dt = this.lastNow ? Math.min(100, this.time.now - this.lastNow) : 0;
    this.lastNow = this.time.now;
    for (const v of this.views.values()) {
      v.hd?.update(dt);
      v.fx.update(dt);
    }
    for (const o of this.fg) (o as unknown as Phaser.GameObjects.Components.Alpha).setAlpha(fa);
    for (const v of this.views.values()) {
      const u = v.unit;
      const g = v.bars;
      // il tombe : sa barre (vide) s'efface toute seule, plus d'effets sur lui
      if (v.dying) continue;
      g.clear();
      const kinds = [...new Set(u.statuses.map((x) => x.kind))].sort((a, b) => STATUS_ORDER.indexOf(a) - STATUS_ORDER.indexOf(b));
      v.fx.sync(u.hp > 0 ? kinds : [], u.hp > 0 && u.shield > 0);
      if (v.hd) v.hd.poseRate = kinds.includes('slow') ? 0.5 : 1;
      // empoisonné : le dessin verdit un peu ; ralenti : il bleuit un peu
      const base = kinds.includes('poison') ? 0xcdf5b4 : kinds.includes('slow') ? 0xc4d8ff : undefined;
      if (base !== v.baseTint) {
        v.baseTint = base;
        this.tint(v);
      }
      if (v.hp <= 0 && u.hp <= 0) continue;
      const w = v.barW;
      const y = v.barY;
      // (style moderne : des pilules ; la vie dans un creux sombre, l'énergie en dessous)
      g.fillStyle(0x0c0822, 0.85);
      g.fillRoundedRect(-w / 2 - 3, y - 3, w + 6, 18, 9);
      const wHp = w * (Math.max(0, v.hp) / u.maxHp);
      if (wHp > 1) {
        g.fillStyle(u.side === 'hero' ? C.green : C.red);
        g.fillRoundedRect(-w / 2, y, Math.max(8, wHp), 12, Math.min(6, wHp / 2));
        g.fillStyle(0xffffff, 0.35);
        g.fillRoundedRect(-w / 2 + 3, y + 2, Math.max(2, wHp - 6), 3, 1.5);
      }
      if (u.shield > 0) {
        g.fillStyle(0xd4f0ff, 0.9);
        g.fillRoundedRect(-w / 2, y, Math.min(w, w * (u.shield / u.maxHp)), 5, 2.5);
      }
      if (u.energy > 0) {
        g.fillStyle(0x0c0822, 0.85);
        g.fillRoundedRect(-w / 2 - 1, y + 16, w + 2, 7, 3.5);
        g.fillStyle(u.energy >= ENERGY_MAX ? C.gold : C.energy);
        g.fillRoundedRect(-w / 2, y + 17, Math.max(5, w * Math.min(1, u.energy / ENERGY_MAX)), 5, 2.5);
      }
      this.syncStatusIcons(v, kinds);
      // étourdi : il vacille doucement (les étoiles tournent au-dessus de sa tête)
      v.sprite.setAngle(u.stun > 0 ? Math.sin(this.time.now / 140) * 5 : 0);
    }
  }

  /** Une teinte sur tout le dessin, ou celle de ses altérations (`baseTint`). */
  private tint(v: View, color = v.baseTint) {
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

  /** Vitesse du combat au moment présent (pour les animations lancées par un coup). */
  private speedNow = 1;
  /** Moment (horloge de la scène) où la dernière chute sera finie : la fin du combat l'attend. */
  protected deathsEnd = 0;

  private deathView(v: View): DeathView {
    return { body: v.body, fig: v.sprite, shadow: v.shadow, bars: v.bars, img: v.hd?.img, sx: v.sx, side: v.unit.side, element: v.unit.element, feet: FEET, h: v.h, w: v.w };
  }

  /** Il tombe (fx-death.ts) : monstre, héros, boss ou grand boss. */
  private kill(v: View) {
    v.dying = true;
    v.fx.sync([], false);
    v.hd?.halt();
    v.sprite.setAngle(0);
    // la barre se vide d'un coup, puis s'efface avec les pictos
    this.drawEmptyBar(v);
    v.stIcons?.forEach((i) => this.tweens.add({ targets: i, alpha: 0, duration: 250 }));
    v.stKey = '-';
    const tier: DeathTier = v.hd && isBigBoss(v.hd.id) ? 'bigBoss' : v.unit.boss ? 'boss' : v.unit.side === 'hero' ? 'hero' : 'monster';
    const ms = playDeath(this, this.deathView(v), tier, this.speedNow, () => {
      if (v.detached) v.body.destroy();
    });
    this.deathsEnd = Math.max(this.deathsEnd, this.time.now + ms);
  }

  /** Il se relève (fx-death.ts) : tout reprend comme avant sa chute. */
  private raise(v: View) {
    if (!v.dying) {
      this.tweens.add({ targets: v.body, alpha: 1, duration: 300 });
      return;
    }
    v.dying = false;
    v.stKey = undefined;
    this.tweens.killTweensOf(v.body);
    v.body.setPosition(v.homeX, v.homeY);
    playRevive(this, this.deathView(v), this.speedNow);
    v.hd?.resume();
  }

  private drawEmptyBar(v: View) {
    const g = v.bars, w = v.barW, y = v.barY;
    g.clear();
    g.fillStyle(0x0c0822, 0.85);
    g.fillRoundedRect(-w / 2 - 3, y - 3, w + 6, 18, 9);
  }

  protected handle(events: BattleEvent[], speed: number) {
    this.speedNow = speed;
    for (const e of events) {
      switch (e.type) {
        case 'attack':
          if (!this.hdStrike(e.source, 'attaque', [e.hit], speed) && !this.stillStrike(e.source, [e.hit], speed)) this.showHit(e.hit, false);
          break;
        case 'skill':
          if (!this.hdStrike(e.source, 'speciale', e.hits, speed, e.skill) && !this.stillStrike(e.source, e.hits, speed, e.skill)) e.hits.forEach((h) => this.showHit(h, true));
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
            if (!v.dying) this.kill(v);
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
    if (v.dying) return;
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
    // une frappe qui soigne aussi son équipe (hors sort d'équipe, qui les montre lui-même) : soins et boucliers au coup
    if (src.hd.ch.anims[which].genre !== 'equipe') {
      const mine = hits.filter((h) => (h.kind === 'heal' || h.kind === 'shield' || h.kind === 'revive') && this.views.get(h.target)?.unit.side === src.unit.side);
      if (mine.length) this.time.delayedCall(ms * 0.6, () => mine.forEach((h) => this.showHit(h, false)));
    }
    if (which === 'speciale') this.dim(Math.max(300, ms - 300));
    this.turnMs = ms + 260 / speed;
    return true;
  }

  /**
   * Le coup d'un personnage dessiné seulement en vectoriel (les 3 dragons, en attendant leur animation de combat) :
   * il s'élance un peu vers l'ennemi et revient ; pour sa compétence, son nom s'affiche et le décor s'assombrit.
   * Renvoie faux pour tout autre personnage.
   */
  private stillStrike(sourceId: string, hits: Hit[], speed: number, skill?: SkillDef): boolean {
    const src = this.views.get(sourceId);
    if (!src || src.hd || !src.imgs.length || src.dying) return false;
    const hero = src.unit.side === 'hero', big = !!skill;
    const t1 = (big ? 220 : 140) / speed;
    this.tweens.add({ targets: src.sprite, x: (hero ? 1 : -1) * (big ? 46 : 30), duration: t1, yoyo: true, ease: 'Quad.easeOut', onComplete: () => src.sprite.setX(0) });
    if (big) {
      const name = this.text(src.body.x, src.body.y + src.barY - 34, t(`skill.${skill.id}`), 28, hero ? '#ffe27a' : '#ff8a8a').setDepth(2000);
      this.tweens.add({ targets: name, y: name.y - 30, alpha: 0, delay: 650 / speed, duration: 450 / speed, onComplete: () => name.destroy() });
      this.dim(500 / speed);
    }
    this.time.delayedCall(t1, () => hits.forEach((h) => {
      const target = this.views.get(h.target);
      if (target && h.kind === 'damage') this.flashAt(target.body.x, target.body.y + FEET - target.h / 2, 0xffffff, big ? 30 : 22, 1 / speed);
      this.showHit(h, big);
    }));
    this.turnMs = t1 * 2 + 260 / speed;
    return true;
  }

  private showHit(hit: Hit, big: boolean) {
    const v = this.views.get(hit.target);
    if (!v) return;
    if (hit.kind === 'damage') {
      v.hp = Math.max(0, v.hp - hit.amount);
      // le coup qui tue : il tombe tout de suite, sans attendre la fin de l'animation de celui qui frappe
      if (v.hp <= 0 && v.unit.hp <= 0 && !v.dying) this.kill(v);
    }
    else if (hit.kind === 'heal') v.hp = Math.min(v.unit.maxHp, v.hp + hit.amount);
    else if (hit.kind === 'revive') v.hp = v.unit.hp;
    if (hit.kind === 'miss' || hit.kind === 'status' || hit.kind === 'revive') {
      if (hit.kind === 'revive') this.raise(v);
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
      // touché : le dessin rougit un instant (une brûlure, un poison… : il prend la couleur de l'effet, qui repart)
      if (!v.dying) {
        const dotColor = hit.dot ? DOT_TINT[hit.status ?? ''] : undefined;
        this.tint(v, dotColor ?? 0xff9a9a);
        this.time.delayedCall(hit.dot ? 140 : 90, () => { if (!v.dying) this.tint(v); });
        if (hit.dot && hit.status) v.fx.pulse(hit.status);
      }
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
      // les dégâts dans le temps : un chiffre plus petit, à la couleur de l'effet, qui monte de son corps
      color = hit.kind === 'heal' ? '#5dff9a' : STATUS_COLOR[hit.status ?? 'burn'] ?? color;
      if (hit.kind === 'heal') v.fx.pulse('regen');
      const n = this.text(x, v.body.y - 30, label, 24, color).setDepth(2000).setScale(1.3);
      this.tweens.add({ targets: n, scale: 1, duration: 160, ease: 'Back.easeOut' });
      this.tweens.add({ targets: n, y: n.y - 56, alpha: 0, delay: 200, duration: 650, ease: 'Quad.easeIn', onComplete: () => n.destroy() });
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

/** Le dessin vectoriel fixe d'un personnage sans planche de combat HD (les 3 dragons), ou rien. */
function stillFig(id: string) {
  return hasHd(id) ? undefined : vectoFig(id);
}

/** Charge ce dessin fixe (lissé : ce n'est pas du pixel art). */
function loadStill(scene: Phaser.Scene, id: string) {
  const v = stillFig(id);
  if (!v || scene.textures.exists(`vs-${id}`)) return;
  scene.load.image(`vs-${id}`, v.big);
  scene.load.once(`filecomplete-image-vs-${id}`, () => scene.textures.get(`vs-${id}`).setFilter(Phaser.Textures.FilterMode.LINEAR));
}
