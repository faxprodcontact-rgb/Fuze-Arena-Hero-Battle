// Base commune des scènes de combat (Phaser) : décor, personnages, barres de vie, coups et chiffres.
// Le moteur (src/core/battle) calcule ; ces scènes animent ce qu'il raconte.
import Phaser from 'phaser';
import type { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type BattleEvent, type Hit, type SkillDef, type Slot, type Unit } from '../core/battle/types';
import { HEROES } from '../core/data/heroes';
import type { Element } from '../core/types';
import { ELEMENT_COLOR, artUrl, cardUrl, hasArt, heroCanvas, isPixel, monsterCanvas, pixelUrl } from './art';
import { PIXEL } from './pixel-meta';
import { ART_META } from './art-meta';
import { SCENES, loadBackdrop, placeBackdrop, type Ctx as BgCtx } from './bg';
import { ICON_INDEX } from './icons-meta';

/** Effets en combat qui ont leur picto (case st-<effet> de public/art/icons.webp). */
const STATUS_ICONS = ['burn', 'poison', 'bleed', 'regen', 'stun', 'silence', 'slow', 'taunt', 'atkUp', 'atkDown', 'defUp', 'defDown', 'speedUp', 'critUp'];
import { t } from './i18n';
import { themeColor } from './theme';
import { HERO_X } from './scenes';
import { battleLook, monsterArtId, type Look } from './look';
import { HdActor, hasHd, hdChar, hdStrike, loadHd, type HdHost } from './hd-fight';
import { HD_ANIM } from './hd-meta';

export const W = 720;
/** La police des combats (la même que les titres des menus) : une seule graisse, ne jamais demander « bold ». */
export const FONT = '"Lilita One", "Trebuchet MS", "Segoe UI", Roboto, sans-serif';
/** Couleurs de l'interface des combats : les mêmes que les menus (style.css). */
export const C = { ink: 0x2a1c12, paper: 0x5c3a1e, paper2: 0xecd9a8, paper3: 0xdfc58c, sky: 0x6b8fb5, panel: 0xecd9a8, panelLight: 0xffffff, trim: 0xd9a63e, hudText: '#4a2a0e',
  green: 0x3fae5a, greenDark: 0x2a8442, red: 0xdc4f4f, redDark: 0xa83232, blue: 0x3f86e0, blueDark: 0x2a5fb5, energy: 0x4fc3ff, gold: 0xf0b530, goldDark: 0xc8860f };

/** Les couleurs du panneau de combat suivent la direction graphique des menus (variables de style.css). */
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

const HERO_IDS = new Set(HEROES.map((h) => h.id));
/** Les effets et la planche de pictos ont déjà été téléchargés une fois (le navigateur les a gardés). */
let laterFetched = false;

/** Couleur des statuts affichés au-dessus des combattants. */
const STATUS_COLOR: Partial<Record<string, string>> = {
  burn: '#ff8a3d', poison: '#9be15d', bleed: '#ff5a6a', regen: '#5dff9a', stun: '#ffe27a', silence: '#c39bff',
  slow: '#7fc8ff', taunt: '#ffb15c', atkUp: '#ffcf5a', atkDown: '#b0b7d6', defUp: '#7fc8ff', defDown: '#b0b7d6',
  speedUp: '#9be15d', critUp: '#ffcf5a',
};

function hex(color: string): number {
  return Number.parseInt(color.slice(1), 16);
}

export interface View {
  unit: Unit;
  body: Phaser.GameObjects.Container;
  /** Le dessin : un conteneur posé aux pieds (retourné pour les ennemis). Image d'un bloc, ou morceaux animés. */
  sprite: Phaser.GameObjects.Container;
  /** Toutes ses images (pour les teintes). */
  imgs: Phaser.GameObjects.Image[];
  /** Morceaux animés (personnages découpés) : l'image et son réglage. */
  parts: { img: Phaser.GameObjects.Image; p: RigPart }[];
  /** Geste en cours (attaque de base ou compétence) : les morceaux le suivent. */
  act?: { k: 'atk' | 'skill'; t0: number; sp: number; lead: number };
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
  /** Échelle de repos du dessin et décalage de sa respiration (chacun respire à son rythme). */
  sx: number;
  sy: number;
  ph: number;
  /** Pixel art : la planche respire et cligne déjà ; pas d'écrasement ni de balancement en plus. */
  px?: boolean;
  /** Personnage HD animé (essai) : il joue ses propres animations (hd-fight.ts). */
  hd?: HdActor;
}

/**
 * Chacun son tour : pendant qu'un coup se joue, le combat est en pause (les règles ne changent pas, seul l'affichage
 * attend). Durée d'un tour, en ms à vitesse ×1 ; ×2 et ×3 les raccourcissent.
 */
const TURN_MS = { attack: 470, skill: 1450, passive: 260, wave: 550 };

/** Taille des dessins Hailuo : pixels de l'écran par unité du repère du dessin (un héros mesure ~190 unités). */
const UNIT_PX = 0.56;
/** Les pieds sont un peu sous le centre du conteneur (comme les anciens dessins). */
const FEET = 47;

type FxName = keyof typeof ART_META.fx;
type RigPart = { n: string; k: string; x: number; y: number; w: number; h: number; px: number; py: number; s: readonly number[]; m: readonly number[]; b: number; i: number; ax: number; ay: number };
// base : [x, y, largeur, hauteur, ax, ay] = place du corps dans le dessin, puis dans l'image regroupée (art/r/<id>.webp)
const RIGS = ART_META.rigs as unknown as Record<string, { size: readonly number[]; base: readonly number[]; parts: readonly RigPart[] }>;
const ease = {
  out: (t: number) => 1 - (1 - t) ** 3,
  inOut: (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2),
  back: (t: number) => 1 + 2.7 * (t - 1) ** 3 + 1.7 * (t - 1) ** 2,
};
const seg = (t: number, a: number, b: number) => Math.max(0, Math.min(1, (t - a) / (b - a)));
/** Rythme du repos de chaque sorte de morceau (la tête suit le souffle, la queue et les ailes vont à leur rythme). */
const IDLE_SPEED: Record<string, [number, number]> = { head: [2.3, -0.6], weapon: [2.3, -1], offhand: [2.3, -0.4], limb: [2.3, -1.4], tail: [1.6, 0.5], wing: [3.4, 0] };
/** Largeur d'affichage de chaque effet (pixels) et point d'ancrage : centre, ou sol (le bas de l'effet aux pieds). */
const FX: Record<FxName, [number, 'c' | 'g']> = {
  slash: [180, 'c'], crossSlash: [195, 'c'], claw: [170, 'c'], impact: [120, 'c'], shockwave: [230, 'g'], pierce: [200, 'c'],
  fireball: [110, 'c'], explosion: [175, 'c'], flamePillar: [130, 'g'], fireSlash: [180, 'c'], meteor: [150, 'c'], emberBurst: [150, 'c'],
  waterBolt: [115, 'c'], splash: [165, 'g'], iceSpikes: [170, 'g'], frostBurst: [150, 'c'], tornado: [130, 'g'], windBlades: [170, 'c'],
  lightning: [150, 'g'], electricOrb: [80, 'c'], featherGust: [170, 'c'], sonicRing: [130, 'c'], rockSpikes: [170, 'g'], quake: [210, 'g'],
  poison: [140, 'c'], thornVines: [140, 'c'], leafStorm: [170, 'c'], boulder: [115, 'c'], heal: [130, 'c'], holyBeam: [120, 'g'],
  goldShield: [105, 'c'], darkOrb: [130, 'c'],
};
/**
 * Compétences (attaques spéciales) : les images Hailuo, chacune avec sa petite chorégraphie (voir `skillFx`).
 * Les combattants au corps à corps et à distance n'ont pas les mêmes ; la compétence choisit dans sa liste.
 * Les attaques de base, elles, restent discrètes et sont dessinées par le code (`basicMelee`, `basicShot`).
 */
const SKILL_FX: Record<Element, { melee: readonly FxName[]; ranged: readonly FxName[] }> = {
  fire: { melee: ['fireSlash', 'explosion', 'flamePillar'], ranged: ['fireball', 'meteor', 'flamePillar'] },
  water: { melee: ['slash', 'iceSpikes', 'splash'], ranged: ['waterBolt', 'frostBurst', 'iceSpikes'] },
  wind: { melee: ['windBlades', 'crossSlash', 'tornado'], ranged: ['lightning', 'tornado', 'featherGust'] },
  earth: { melee: ['claw', 'rockSpikes', 'quake'], ranged: ['boulder', 'rockSpikes', 'thornVines'] },
};
/** Ce qui éclate à l'arrivée d'un projectile de compétence. */
const ARRIVAL_FX: Partial<Record<FxName, FxName>> = { fireball: 'explosion', meteor: 'explosion', waterBolt: 'splash', electricOrb: 'sonicRing', boulder: 'quake' };
type Pt = { x: number; y: number; feet: number };
/** Effets lumineux : un double additif posé dessus les fait vraiment briller (pas les rochers ni la terre). */
const LIGHT = new Set<FxName>(['slash', 'fireSlash', 'crossSlash', 'windBlades', 'claw', 'pierce', 'lightning', 'explosion', 'emberBurst',
  'impact', 'sonicRing', 'frostBurst', 'flamePillar', 'holyBeam', 'electricOrb', 'fireball', 'waterBolt', 'meteor', 'iceSpikes', 'heal', 'goldShield', 'darkOrb']);
const rgb = (c: number) => [(c >> 16) & 255, (c >> 8) & 255, c & 255] as const;
/** Temps avant l'impact (projectiles, météore : ils doivent d'abord voyager). */
const TRAVEL: Partial<Record<FxName, number>> = { meteor: 300, fireball: 260, waterBolt: 260, electricOrb: 260, boulder: 260 };
const STATUS_FX: Partial<Record<string, FxName>> = {
  poison: 'poison', burn: 'emberBurst', stun: 'sonicRing', silence: 'darkOrb', atkDown: 'darkOrb', defDown: 'darkOrb',
  slow: 'frostBurst', regen: 'leafStorm', atkUp: 'emberBurst', critUp: 'emberBurst',
};
const hash = (s: string) => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);

export abstract class FightScene extends Phaser.Scene {
  protected battle!: Battle;
  protected views = new Map<string, View>();
  /** Haut du sol : tout le terrain se place à partir de là. */
  protected groundTop = 380;
  /** Les boss des combats « au score » sont dessinés plus gros. */
  protected bigBoss = false;
  /** Resserre le terrain vers le centre (écran d'accueil, plus étroit). */
  protected xSquash = 1;
  /** Bandeau de cinéma des compétences des héros (pas sur l'accueil ni dans l'aperçu de la fiche, trop petits). */
  protected cutInBand = true;
  /** Premier plan du terrain (rochers, piliers…) : il passe devant les combattants. */
  private fg: Phaser.GameObjects.GameObject[] = [];
  /** Bas du terrain (pour l'assombrir en entier). */
  private arenaBottom = 0;
  /** Terrain et famille de monstres de ce combat. */
  protected look: Look = battleLook('arena', '');
  /** Combat d'essai HD : les personnages qui ont une planche HD (hd-meta.ts) jouent leurs vraies animations. */
  protected hdMode = false;
  /** Combat joué d'après un scénario (essai HD) : la suite des coups vient de là, pas des règles. */
  protected script?: () => BattleEvent[];
  /** Durée du coup qui vient d'être lancé, quand elle n'est pas la durée habituelle (ms réelles). */
  private turnMs?: number;
  private lastNow = 0;

  /** Les combattants à charger avant le combat (les autres arrivent plus tard, avec l'ancien dessin en attendant). */
  protected abstract preloadUnits(): { id?: string; defId: string; element: string }[];

  /** Le haut du sol et le bas du terrain : chaque écran les fixe (le décor est dessiné pour cette place). */
  protected arenaBox(): { groundTop: number; bottom: number } {
    return { groundTop: this.groundTop, bottom: this.scale.height };
  }

  /** Les repères du décor dessiné par le code : l'horizon, le bas, le milieu des pieds des deux équipes. */
  private bgCtx(): BgCtx {
    const { groundTop, bottom } = this.arenaBox();
    const cy = groundTop + (ROW_DY[0] + ROW_DY[1]) / 2 + FEET;
    // la plateforme déborde de 50 px derrière les pieds du rang du fond et de 48 px devant ceux du rang de devant
    return { hz: groundTop + 50, bottom, cx: W / 2, cy, p0: groundTop + ROW_DY[0] + FEET - 50, p1: groundTop + ROW_DY[1] + FEET + 48 };
  }

  preload() {
    const terrain = this.look.terrain;
    const scene = SCENES[terrain];
    const pxBg = this.look.pixel;
    if (pxBg) {
      if (!this.textures.exists(`pxbg-${pxBg}`)) this.load.image(`pxbg-${pxBg}`, `art/px/fond-${pxBg}.webp`);
    } else if (scene) loadBackdrop(this, terrain, scene, this.bgCtx());
    else {
      if (!this.textures.exists(`t-${terrain}`)) this.load.image(`t-${terrain}`, `art/t/${terrain}.jpg`);
      const tm = ART_META.terrains[terrain] as { fg?: number };
      if (tm?.fg && !this.textures.exists(`t-${terrain}-fg`)) this.load.image(`t-${terrain}-fg`, `art/t/${terrain}-fg.webp`);
    }
    // Les images d'effets (1,2 Mo) et la planche de pictos n'empêchent plus la scène de démarrer : elles se chargent
    // en arrière-plan une fois le combat affiché (un effet pas encore arrivé est simplement sauté).
    this.events.once('create', () => {
      const fetchLater = () => {
        if (!this.sys.isActive()) return;
        for (const name of Object.keys(ART_META.fx)) if (!this.textures.exists(`fx-${name}`)) this.load.image(`fx-${name}`, `art/fx/${name}.webp`);
        if (!this.textures.exists('icons')) this.load.spritesheet('icons', 'art/icons.webp', { frameWidth: 128, frameHeight: 128 });
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
      if (this.hdMode && hasHd(id)) {
        loadHd(this, id, u.element as Element);
        if (HERO_IDS.has(u.defId) && !this.textures.exists(`c-${id}`)) this.load.image(`c-${id}`, cardUrl(id));
        continue;
      }
      if (isPixel(id)) {
        // pixel art : une planche de 8 images (respiration, clignement), à la place du dessin découpé
        if (!this.textures.exists(`x-${id}`)) this.load.spritesheet(`x-${id}`, pixelUrl(id), { frameWidth: PIXEL.cw * PIXEL.up, frameHeight: PIXEL.ch * PIXEL.up });
        if (HERO_IDS.has(u.defId) && !this.textures.exists(`c-${id}`)) this.load.image(`c-${id}`, cardUrl(id));
        continue;
      }
      const rig = RIGS[id];
      if (rig) {
        if (!this.textures.exists(`r-${id}`)) this.load.image(`r-${id}`, `art/r/${id}.webp`);
      }
      if (hasArt(id) && (!rig || HERO_IDS.has(u.defId)) && !this.textures.exists(`p-${id}`)) this.load.image(`p-${id}`, artUrl(id));
      if (hasArt(id) && HERO_IDS.has(u.defId) && !this.textures.exists(`c-${id}`)) this.load.image(`c-${id}`, cardUrl(id));
    }
  }

  /** Le dessin d'un combattant : un héros, ou le monstre de la famille de ce décor. */
  protected charId(u: { id?: string; defId: string; element: string }): string {
    return HERO_IDS.has(u.defId) ? u.defId : monsterArtId(u.defId, u.element as Element, this.look);
  }

  protected text(x: number, y: number, value: string, size = 28, color = '#ffffff') {
    return this.add
      .text(x, y, value, { fontFamily: FONT, fontSize: `${size}px`, color, align: 'center' })
      .setOrigin(0.5)
      .setStroke('#1a1420', Math.max(3, Math.round(size * 0.13)))
      .setShadow(0, Math.max(2, Math.round(size * 0.07)), '#2f2244', 0, true, true);
  }

  /** Les adversaires d'arène sont des héros : le dessin dépend de ce qu'est le combattant, pas de son camp. */
  protected texture(u: { defId: string; element: string }): string {
    const isHero = HERO_IDS.has(u.defId);
    const key = isHero ? `h-${u.defId}` : `m-${u.defId}-${u.element}`;
    if (!this.textures.exists(key)) {
      this.textures.addCanvas(key, isHero ? heroCanvas(u.defId) : monsterCanvas(u.defId, u.element as never));
    }
    return key;
  }

  /** Le terrain : l'image du décor, le centre de son arène au milieu des rangées de combattants. */
  protected drawArena(bottom: number) {
    this.arenaBottom = bottom;
    const pxBg = this.look.pixel;
    if (pxBg && this.textures.exists(`pxbg-${pxBg}`)) {
      // fond en pixel art (refonte-graphique/pixel/fond.py) : dessiné pour cet écran, son bas sur le bas du terrain
      this.add.image(0, bottom, `pxbg-${pxBg}`).setOrigin(0, 1).setDepth(-30);
      return;
    }
    const scene = SCENES[this.look.terrain];
    if (scene) {
      const placed = placeBackdrop(this, this.look.terrain, scene, this.bgCtx());
      if (placed.ok) {
        this.fg = placed.front;
        return;
      }
    }
    const key = `t-${this.look.terrain}`;
    const m = ART_META.terrains[this.look.terrain];
    if (this.textures.exists(key) && m) {
      // le centre du cercle tracé au sol sous le milieu des pieds des combattants, et l'image assez grande pour que
      // toute l'équipe (pieds et largeur des dessins) tienne dans ce cercle ; l'écran reste couvert
      const [ox, oy, orx, ory] = (m as unknown as { oval: [number, number, number, number] }).oval;
      const cy = this.groundTop + (ROW_DY[0] + ROW_DY[1]) / 2 + FEET;
      const dx = (W / 2 - HERO_X[3]) * this.xSquash + 42, dy = (ROW_DY[1] - ROW_DY[0]) / 2 + 26;
      const k = Math.max(
        Math.hypot(dx / (orx * m.w), dy / (ory * m.h)),
        W / 2 / (ox * m.w), W / 2 / ((1 - ox) * m.w), cy / (oy * m.h), (bottom - cy) / ((1 - oy) * m.h),
      );
      const x0 = W / 2 - ox * m.w * k, y0 = cy - oy * m.h * k;
      const fgKey = `${key}-fg`;
      if (this.textures.exists(fgKey)) {
        // coupé au bas du terrain : rien ne déborde sur le panneau du bas
        const fg = this.add.image(x0, y0, fgKey).setOrigin(0).setScale(k).setDepth(1300);
        fg.setCrop(0, 0, m.w, Math.max(0, (bottom - y0) / k));
        this.fg = [fg];
      }
      return this.add.image(x0, y0, key).setOrigin(0).setScale(k).setDepth(-10);
    }
    const g = this.add.graphics().setDepth(-10);
    const top = this.groundTop;
    g.fillGradientStyle(0x2b3a78, 0x2b3a78, 0x6b5ca8, 0x6b5ca8, 1);
    g.fillRect(0, 0, W, top + 40);
    g.fillStyle(0x4a5a9a, 0.6);
    for (let i = 0; i < 6; i++) g.fillTriangle(i * 150 - 40, top + 10, i * 150 + 60, top - 70 - (i % 2) * 40, i * 150 + 160, top + 10);
    g.fillGradientStyle(0x3d6b4a, 0x3d6b4a, 0x274a34, 0x274a34, 1);
    g.fillRect(0, top, W, bottom - top);
    g.fillStyle(0xffffff, 0.06);
    g.fillEllipse(W / 2, top + 180, 760, 330);
    return g;
  }

  protected slotPos(unit: Unit): { x: number; y: number } {
    const hero = unit.side === 'hero';
    const x = hero ? HERO_X[unit.slot] : ENEMY_X[unit.slot];
    return { x: W / 2 + (x - W / 2) * this.xSquash, y: this.groundTop + ROW_DY[unit.slot] };
  }

  protected addView(unit: Unit, enter = false, speed = 1) {
    const hero = unit.side === 'hero';
    const { x, y } = this.slotPos(unit);
    const body = this.add.container(enter ? x + 320 : x, unit.boss && this.bigBoss ? y - 30 : y).setDepth(y);
    const id = this.charId(unit);
    const fig = this.add.container(0, 0);
    const imgs: Phaser.GameObjects.Image[] = [];
    const parts: View['parts'] = [];
    let shadow: Phaser.GameObjects.Ellipse;
    let barY: number;
    const barW = unit.boss ? 130 : 86;
    const rig = RIGS[id];
    const boost = unit.boss ? (this.bigBoss ? 1.45 : 1.12) : 1;
    let hd: HdActor | undefined;
    if (this.hdMode && hasHd(id) && this.textures.exists(`hd-${id}`)) {
      // personnage HD : un pixel du dessin = `scale` unités ; les pieds sur la ligne de sol
      const ch = hdChar(id), k = HD_ANIM.scale * boost;
      fig.setPosition(0, FEET);
      hd = new HdActor(this, fig, id, k, unit.element);
      imgs.push(hd.img);
      shadow = this.add.ellipse(0, FEET, Math.min(160, (ch.sol[1]! - ch.sol[0]!) * k * 1.1), 20, 0x000000, 0.3);
      barY = FEET - Math.min(ch.top * k, 126 * boost) - 6;
    } else if (isPixel(id) && this.textures.exists(`x-${id}`)) {
      // pixel art : les pieds (fx, fy de la case) sur la ligne de sol ; un pixel mesure `scale` unités (la taille des anciens dessins)
      const [top, left, right, scale] = PIXEL.chars[id as keyof typeof PIXEL.chars];
      const k = scale * boost, key = `x-${id}`;
      if (!this.anims.exists(key)) {
        this.anims.create({ key, frames: this.anims.generateFrameNumbers(key, { start: 0, end: PIXEL.frames - 1 }), frameRate: 7, repeat: -1 });
      }
      fig.setPosition(0, FEET);
      const spr = this.add.sprite(0, 0, key, 0).setOrigin(PIXEL.fx / PIXEL.cw, PIXEL.fy / PIXEL.ch).setScale(k / PIXEL.up);
      spr.play({ key, startFrame: Math.floor(Math.random() * PIXEL.frames) });
      fig.add(spr);
      imgs.push(spr);
      shadow = this.add.ellipse(0, FEET, Math.min(160, (right - left) * k * 0.55), 20, 0x000000, 0.3);
      // la barre de vie au-dessus de la tête (les ailes, plumes et flammes qui montent plus haut ne comptent pas)
      barY = FEET - Math.min((PIXEL.fy - top) * k, 126 * boost) - 6;
    } else if (hasArt(id) && (this.textures.exists(`p-${id}`) || (rig && this.textures.exists(`r-${id}`)))) {
      // dessin Hailuo : les pieds (point 106, 228 du repère) sur la ligne de sol
      // norm : la même stature pour tous les héros (mesurée par art-jeu.py) ; les monstres gardent leur échelle
      const [ox, oy, w, h, sc, norm] = ART_META.chars[id as keyof typeof ART_META.chars];
      const k = UNIT_PX * (norm || Math.max(0.85, Math.min(1.35, sc))) * boost;
      fig.setPosition(0, FEET);
      if (rig && this.textures.exists(`r-${id}`)) {
        // découpé en morceaux : le corps, puis chaque morceau posé sur son articulation (ceux « derrière » avant le corps).
        // Tout est dans une seule image : on y repère une fois la place de chaque morceau.
        const key = `r-${id}`, tex = this.textures.get(key);
        const [bx, by, bw, bh, bax, bay] = rig.base as unknown as [number, number, number, number, number, number];
        if (!tex.has('base')) {
          tex.add('base', 0, bax, bay, bw, bh);
          for (const p of rig.parts) tex.add(p.n, 0, p.ax, p.ay, p.w, p.h);
        }
        const [W0, H0] = rig.size as [number, number];
        const u = (w * k) / W0, fx = ((106 - ox) / w) * W0, fy = ((228 - oy) / h) * H0;
        const inner = this.add.container(-fx * u, -fy * u).setScale(u);
        const base = this.add.image(bx, by, key, 'base').setOrigin(0);
        const mk = (p: RigPart) => {
          const img = this.add.image(p.px, p.py, key, p.n).setOrigin((p.px - p.x) / p.w, (p.py - p.y) / p.h);
          parts.push({ img, p });
          return img;
        };
        const behind = rig.parts.filter((p) => p.b).map(mk), front = rig.parts.filter((p) => !p.b).map(mk);
        inner.add([...behind, base, ...front]);
        imgs.push(base, ...behind, ...front);
        fig.add(inner);
      } else {
        const img = this.add.image(0, 0, `p-${id}`).setDisplaySize(w * k, h * k).setOrigin((106 - ox) / w, (228 - oy) / h);
        fig.add(img);
        imgs.push(img);
      }
      shadow = this.add.ellipse(0, FEET, Math.min(160, w * k * 0.55), 20, 0x000000, 0.3);
      barY = FEET - (228 - Math.max(oy, 228 - 330)) * k - 6;
    } else {
      const scale = unit.boss ? (this.bigBoss ? 2 : 1.45) : 0.95;
      shadow = this.add.ellipse(0, 50 * scale, 90 * scale, 22, 0x000000, 0.3);
      const img = this.add.image(0, 0, this.texture(unit)).setScale(scale);
      fig.add(img);
      imgs.push(img);
      barY = unit.boss ? -100 : -72;
    }
    fig.setScale(hero ? 1 : -1, 1);
    const bars = this.add.graphics();
    body.add([shadow, fig, bars]);
    this.views.set(unit.id, { unit, body, sprite: fig, imgs, parts, bars, homeX: x, homeY: body.y, barY, barW, hp: unit.hp, sx: fig.scaleX, sy: 1, ph: Math.random() * 6.28, px: !!hd || (isPixel(id) && this.textures.exists(`x-${id}`)), hd });
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
      g.fillStyle(C.ink);
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
      // au repos, chacun respire (le haut du corps monte et descend, pivot aux pieds) et se balance un peu
      const now = this.time.now / 1000;
      if (!v.px && !this.tweens.isTweening(v.sprite)) {
        const b = Math.sin(now * (u.boss ? 1.5 : 2.3) + v.ph);
        v.sprite.setScale(v.sx * (1 - 0.014 * b), v.sy * (1 + 0.03 * b));
      }
      const sway = v.px ? 0 : Math.sin(now * 1.3 + v.ph * 2) * (u.side === 'enemy' ? 1.6 : 0.8);
      v.sprite.setAngle(u.stun > 0 ? Math.sin(this.time.now / 60) * 8 : sway + this.animateParts(v, now));
    }
    this.syncGlows();
  }

  /**
   * Les morceaux d'un personnage découpé : un petit mouvement de repos chacun, et le geste en cours (élan, coup,
   * compétence) avec les angles de son réglage. Renvoie l'inclinaison du corps entier (degrés).
   */
  private animateParts(v: View, now: number): number {
    const dir = v.unit.side === 'hero' ? 1 : -1;
    let w = 0, h = 0, r = 0, skill = false;
    if (v.act) {
      const t = (this.time.now - v.act.t0) * v.act.sp;
      if (v.act.k === 'atk') {
        w = ease.out(seg(t, 0, 70)); h = ease.back(seg(t, 70, 165)); r = ease.inOut(seg(t, 240, 410));
        if (t > 420) v.act = undefined;
      } else {
        const L = v.act.lead;
        skill = true;
        w = ease.out(seg(t, 0, L)); h = ease.back(seg(t, L, L + 170)); r = ease.inOut(seg(t, L + 450, L + 720));
        if (t > L + 740) v.act = undefined;
      }
    }
    const b = Math.sin(now * 2.3 + v.ph);
    for (const { img, p } of v.parts) {
      const [sp, ph] = IDLE_SPEED[p.k] ?? [2.3, 0];
      let ang = Math.sin(now * sp + v.ph + ph) * p.i;
      const wind = p.s[0]! * (skill ? 1.3 : 1), hit = skill ? p.s[2]! : p.s[1]!;
      ang += (wind * w + (hit - wind) * h) * (1 - r);
      const mv = h * (1 - r);
      img.setAngle(ang).setPosition(p.px + p.m[0]! * mv, p.py + p.m[1]! * mv + (p.k === 'head' ? -4 * b : 0));
    }
    const lean = skill ? [-6, 14] : [-4, 10];
    return dir * (lean[0]! * w + (lean[1]! - lean[0]!) * h) * (1 - r);
  }

  /** Une teinte sur tout le dessin (morceaux compris), ou aucune. */
  private tint(v: View, color?: number) {
    for (const img of v.imgs) {
      if (color === undefined) img.clearTint();
      else img.setTint(color);
    }
  }

  /** Copie du dessin dans sa pose de l'instant (pour le double lumineux de la compétence). */
  private cloneFig(c: Phaser.GameObjects.Container): Phaser.GameObjects.Container {
    const out = this.add.container(c.x, c.y).setScale(c.scaleX, c.scaleY).setAngle(c.angle);
    for (const ch of c.list) {
      if (ch instanceof Phaser.GameObjects.Container) out.add(this.cloneFig(ch));
      else if (ch instanceof Phaser.GameObjects.Image) {
        out.add(this.add.image(ch.x, ch.y, ch.texture.key, ch.frame.name).setOrigin(ch.originX, ch.originY).setScale(ch.scaleX, ch.scaleY).setAngle(ch.angle).setBlendMode(Phaser.BlendModes.ADD));
      }
    }
    return out;
  }

  private tintDeep(c: Phaser.GameObjects.GameObject, color: number) {
    if (c instanceof Phaser.GameObjects.Container) c.each((ch: Phaser.GameObjects.GameObject) => this.tintDeep(ch, color));
    else if (c instanceof Phaser.GameObjects.Image) c.setTint(color);
  }

  /** Les doubles lumineux suivent leur effet (position, taille, rotation, transparence). */
  private glows: { src: Phaser.GameObjects.Image; g: Phaser.GameObjects.Image }[] = [];
  private syncGlows() {
    this.glows = this.glows.filter(({ src, g }) => {
      if (!src.active) {
        g.destroy();
        return false;
      }
      g.setPosition(src.x, src.y).setScale(src.scaleX * 1.06, src.scaleY * 1.06).setAngle(src.angle).setAlpha(src.alpha * 0.55).setFlipX(src.flipX);
      return true;
    });
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
    if (this.script) {
      for (const e of this.script()) this.queue.push({ e, speed });
      return;
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
          if (this.hdStrike(e.source, 'attaque', [e.hit], speed)) break;
          this.animateAttack(e.source, e.hit, speed);
          break;
        case 'skill':
          if (this.hdStrike(e.source, 'speciale', e.hits, speed, e.skill)) break;
          this.animateSkill(e.source, e.skill.id, e.hits, speed);
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

  /** Une image d'effet posée en (x, y), à sa taille de base (`k` = échelle correspondante). */
  private fxImage(name: FxName, x: number, y: number, flip = false, ground = FX[name][1] === 'g') {
    const key = `fx-${name}`;
    if (!this.textures.exists(key)) return null;
    const oy = ground ? 0.95 : 0.5;
    const img = this.add.image(x, y, key).setOrigin(0.5, oy).setFlipX(flip).setDepth(1500);
    const k = FX[name][0] / img.width;
    img.setScale(k);
    if (LIGHT.has(name)) this.glows.push({ src: img, g: this.add.image(x, y, key).setOrigin(0.5, oy).setDepth(1501).setBlendMode(Phaser.BlendModes.ADD).setScale(k) });
    return { img, k };
  }

  /** Effet simple (soin, bouclier, statut) : il grossit un peu puis s'efface. */
  protected fx(name: FxName, x: number, y: number, o: { size?: number; flip?: boolean; dur?: number } = {}) {
    const f = this.fxImage(name, x, y, o.flip);
    if (!f) return;
    const { img } = f, k = f.k * (o.size ?? 1), dur = o.dur ?? 420;
    img.setScale(k * 0.7).setAlpha(0.95);
    this.tweens.add({ targets: img, scale: k, duration: dur * 0.35, ease: 'Back.easeOut' });
    this.tweens.add({ targets: img, alpha: 0, delay: dur * 0.5, duration: dur * 0.5, onComplete: () => img.destroy() });
  }

  /** Un éclair de lumière bref au point d'impact, avec une onde qui s'élargit. */
  private flashAt(x: number, y: number, color = 0xffffff, r = 34, t = 1) {
    const c = this.add.circle(x, y, r, color, 0.8).setDepth(1600).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: c, scale: 1.8, alpha: 0, duration: 180 * t, onComplete: () => c.destroy() });
    const ring = this.add.circle(x, y, r * 0.8).setStrokeStyle(5, color, 0.9).setDepth(1600).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: ring, scale: 3, alpha: 0, duration: 300 * t, ease: 'Cubic.easeOut', onComplete: () => ring.destroy() });
  }

  /** Gerbe d'étincelles (traits qui partent en étoile). */
  private sparks(x: number, y: number, color: number, n: number, len: number, t: number) {
    const g = this.add.graphics().setDepth(1450).setPosition(x, y).setBlendMode(Phaser.BlendModes.ADD);
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + Math.random() * 0.5, l = len * (0.55 + Math.random() * 0.45);
      g.lineStyle(4, color, 0.9).lineBetween(Math.cos(a) * 6, Math.sin(a) * 6, Math.cos(a) * l, Math.sin(a) * l);
      g.lineStyle(1.5, 0xffffff, 1).lineBetween(Math.cos(a) * 6, Math.sin(a) * 6, Math.cos(a) * l * 0.7, Math.sin(a) * l * 0.7);
    }
    g.setScale(0.35);
    this.tweens.add({ targets: g, scale: 1.15, alpha: 0, duration: 200 * t, ease: 'Cubic.easeOut', onComplete: () => g.destroy() });
  }

  /** Le coup porte : la cible est repoussée, s'écrase un instant puis reprend sa forme. */
  private recoil(v: View, dir: number, px: number, t: number) {
    v.body.x = v.homeX + dir * px;
    this.tweens.add({ targets: v.body, x: v.homeX, duration: 170 * t, ease: 'Quad.easeOut' });
    v.sprite.setScale(v.sx, v.sy);
    this.tweens.add({ targets: v.sprite, scaleX: v.sx * 0.9, scaleY: v.sy * 1.06, duration: 50 * t, yoyo: true });
  }

  /**
   * La chorégraphie d'une compétence sur une cible : chaque image a sa façon d'arriver, de frapper et de partir
   * (la lame balaie et percute, l'éclair tombe et claque, les pics jaillissent du sol, le météore s'écrase…).
   * `t` = 1 / vitesse du combat. Renvoie le moment de l'impact (ms), pour y caler les chiffres de dégâts.
   */
  private skillFx(name: FxName, from: Pt, to: Pt, dir: number, t: number): number {
    const flip = dir < 0;
    const end = (img: Phaser.GameObjects.Image, delay: number, dur: number, extra: Record<string, unknown> = {}) =>
      this.tweens.add({ targets: img, alpha: 0, delay, duration: dur, ...extra, onComplete: () => img.destroy() });
    const shake = (ms: number, k: number) => this.cameras.main.shake(ms, k);
    switch (name) {
      case 'slash': case 'fireSlash': case 'claw': case 'windBlades': case 'crossSlash': {
        // la lame arrive de derrière en tournant, s'écrase sur la cible en grossissant, puis file en s'étirant
        const f = this.fxImage(name, to.x - dir * 60, to.y, flip);
        if (!f) return 0;
        const { img, k } = f, cross = name === 'crossSlash';
        img.setScale(k * (cross ? 1.7 : 0.35), k * (cross ? 1.7 : 0.9)).setAngle(cross ? dir * 90 : -dir * 40).setAlpha(0.3);
        this.tweens.add({ targets: img, x: to.x + dir * 8, angle: 0, scaleX: k * 1.15, scaleY: k * 1.15, alpha: 1, duration: 120 * t, ease: 'Cubic.easeOut' });
        this.time.delayedCall(110 * t, () => { this.flashAt(to.x, to.y, 0xffffff, 26, t); shake(70, 0.004); });
        end(img, 170 * t, 200 * t, { x: to.x + dir * 50, scaleX: k * 1.5, scaleY: k * 0.5 });
        return 110 * t;
      }
      case 'pierce': {
        const f = this.fxImage(name, to.x - dir * 160, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.4, k);
        this.tweens.add({ targets: img, x: to.x + dir * 40, scaleX: k * 1.3, duration: 150 * t, ease: 'Quad.easeIn' });
        this.time.delayedCall(140 * t, () => this.flashAt(to.x, to.y, 0xcfe8ff, 28, t));
        end(img, 170 * t, 160 * t, { x: to.x + dir * 90 });
        return 140 * t;
      }
      case 'fireball': case 'waterBolt': case 'electricOrb': case 'boulder': {
        // le projectile part du lanceur, grossit en approchant (le rocher tourne sur lui-même), puis éclate
        const f = this.fxImage(name, from.x + dir * 30, from.y, false);
        if (!f) return 0;
        const { img, k } = f, travel = 260 * t;
        img.setScale(k * 0.6).setRotation(Math.atan2(to.y - from.y, to.x - from.x));
        this.tweens.add({ targets: img, x: to.x, y: to.y, scale: k * 1.1, duration: travel, ease: 'Quad.easeIn', onComplete: () => img.destroy() });
        if (name === 'boulder') this.tweens.add({ targets: img, angle: img.angle + dir * 540, duration: travel });
        if (name === 'electricOrb') this.tweens.add({ targets: img, alpha: 0.6, yoyo: true, repeat: 3, duration: travel / 8 });
        this.time.delayedCall(travel, () => this.skillFx(ARRIVAL_FX[name]!, from, to, dir, t));
        return travel;
      }
      case 'meteor': {
        // tombe du ciel en diagonale, de plus en plus vite, puis s'écrase : explosion, sol fendu, secousse
        const f = this.fxImage(name, to.x - dir * 230, to.y - 360, flip);
        if (!f) return 0;
        const { img, k } = f, fall = 300 * t;
        img.setScale(k * 0.55);
        this.tweens.add({ targets: img, x: to.x - dir * 20, y: to.y - 30, scale: k * 1.05, duration: fall, ease: 'Quad.easeIn', onComplete: () => img.destroy() });
        this.time.delayedCall(fall, () => { this.skillFx('explosion', from, to, dir, t); this.skillFx('quake', from, to, dir, t); shake(220, 0.012); });
        return fall;
      }
      case 'lightning': {
        // l'éclair jaillit d'un coup jusqu'au sol, clignote, claque (flash + secousse), puis s'amincit
        const f = this.fxImage(name, to.x, to.feet, flip, true);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.8, 0);
        this.tweens.add({ targets: img, scaleY: k * 1.3, duration: 70 * t, ease: 'Expo.easeOut' });
        this.tweens.add({ targets: img, alpha: 0.35, delay: 80 * t, duration: 45 * t, yoyo: true, repeat: 2 });
        this.time.delayedCall(70 * t, () => { this.flashAt(to.x, to.feet - 10, 0xfff3a0, 44, t); this.flashAt(to.x, to.y, 0xffffff, 30, t); shake(140, 0.01); });
        end(img, 380 * t, 160 * t, { scaleX: 0 });
        return 70 * t;
      }
      case 'flamePillar': case 'iceSpikes': case 'rockSpikes': case 'splash': case 'holyBeam': {
        // jaillit du sol en s'étirant vers le haut (avec un rebond), tient un instant, puis rentre dans le sol
        const f = this.fxImage(name, to.x, to.feet, flip, true);
        if (!f) return 0;
        const { img, k } = f, beam = name === 'holyBeam';
        img.setScale(beam ? 0 : k * 0.7, beam ? k * 1.2 : 0);
        this.tweens.add({ targets: img, scaleX: k, scaleY: k * (beam ? 1.2 : 1.15), duration: 170 * t, ease: 'Back.easeOut' });
        this.tweens.add({ targets: img, scaleY: k * (beam ? 1.2 : 1), delay: 170 * t, duration: 120 * t });
        if (name === 'rockSpikes' || name === 'iceSpikes') this.time.delayedCall(90 * t, () => shake(110, 0.007));
        if (name === 'flamePillar') this.tweens.add({ targets: img, scaleX: k * 1.08, delay: 200 * t, duration: 70 * t, yoyo: true, repeat: 2 });
        this.time.delayedCall(90 * t, () => this.flashAt(to.x, to.feet - 20, beam ? 0xfff3b0 : 0xffffff, 30, t));
        end(img, 480 * t, 200 * t, beam ? { scaleX: 0 } : { scaleY: 0 });
        return 90 * t;
      }
      case 'quake': case 'shockwave': {
        // l'onde part des pieds et s'élargit au ras du sol pendant que l'écran tremble
        const f = this.fxImage(name, to.x, to.feet + 6, flip, true);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.25, k * 0.4);
        this.tweens.add({ targets: img, scaleX: k * 1.35, scaleY: k * 1.05, duration: 260 * t, ease: 'Cubic.easeOut' });
        shake(200, 0.009);
        end(img, 220 * t, 260 * t);
        return 60 * t;
      }
      case 'explosion': case 'emberBurst': case 'impact': case 'sonicRing': case 'frostBurst': {
        // éclate d'un petit point à plus grand que nature, en tournant un peu, puis se dissipe en gonflant
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.2).setAngle(name === 'frostBurst' ? -40 : Phaser.Math.Between(-15, 15));
        this.tweens.add({ targets: img, scale: k * 1.15, angle: name === 'frostBurst' ? 30 : img.angle, duration: 150 * t, ease: 'Back.easeOut' });
        this.flashAt(to.x, to.y, name === 'frostBurst' ? 0xcff4ff : 0xfff0c0, 36, t);
        if (name === 'explosion') shake(160, 0.01);
        end(img, 200 * t, 240 * t, { scale: k * 1.4 });
        return 20 * t;
      }
      case 'tornado': {
        // la tornade naît au sol, grandit, oscille de gauche à droite en se retournant, puis s'évanouit
        const f = this.fxImage(name, to.x, to.feet, flip, true);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.2);
        this.tweens.add({ targets: img, scale: k * 1.1, duration: 200 * t, ease: 'Back.easeOut' });
        this.tweens.add({ targets: img, x: to.x + 14, delay: 120 * t, duration: 90 * t, yoyo: true, repeat: 3, onRepeat: () => img.toggleFlipX() });
        end(img, 640 * t, 200 * t, { scaleX: 0 });
        return 160 * t;
      }
      case 'featherGust': case 'leafStorm': {
        // la rafale traverse la cible depuis le lanceur, en s'étirant (les feuilles tournent)
        const f = this.fxImage(name, to.x - dir * 150, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.6, k * 0.8).setAlpha(0.2);
        this.tweens.add({ targets: img, x: to.x + dir * 30, scaleX: k * 1.15, scaleY: k, alpha: 1, duration: 260 * t, ease: 'Sine.easeOut' });
        if (name === 'leafStorm') this.tweens.add({ targets: img, angle: dir * 120, duration: 600 * t });
        end(img, 300 * t, 260 * t, { x: to.x + dir * 120 });
        return 200 * t;
      }
      case 'thornVines': {
        // la liane fouette : elle part couchée en arrière et claque sur la cible
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.5).setAngle(-dir * 75);
        this.tweens.add({ targets: img, angle: dir * 12, scale: k * 1.1, duration: 170 * t, ease: 'Back.easeOut' });
        this.time.delayedCall(150 * t, () => { this.flashAt(to.x, to.y, 0xd8ffb0, 28, t); shake(80, 0.005); });
        end(img, 320 * t, 200 * t, { scale: k * 0.8 });
        return 150 * t;
      }
      case 'darkOrb': case 'poison': {
        // tourbillon qui se resserre sur la cible (orbe), ou nuage qui gonfle et monte (poison)
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f, orb = name === 'darkOrb';
        img.setScale(orb ? k * 1.5 : k * 0.4).setAlpha(orb ? 0.2 : 1);
        this.tweens.add({ targets: img, scale: orb ? k * 0.8 : k * 1.1, angle: orb ? -360 : 0, y: orb ? to.y : to.y - 18, alpha: 1, duration: 420 * t, ease: 'Sine.easeInOut' });
        end(img, 420 * t, 220 * t);
        return 200 * t;
      }
      case 'heal': {
        const f = this.fxImage(name, to.x, to.y + 20, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.6);
        this.tweens.add({ targets: img, y: to.y - 30, scale: k, duration: 500 * t, ease: 'Sine.easeOut' });
        end(img, 300 * t, 300 * t);
        return 0;
      }
      case 'goldShield': {
        // le bouclier se pose d'un coup (grand → normal), brille, puis se resserre sur le héros
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 1.7).setAlpha(0);
        this.tweens.add({ targets: img, scale: k, alpha: 1, duration: 200 * t, ease: 'Back.easeOut' });
        this.tweens.add({ targets: img, alpha: 0.6, delay: 220 * t, duration: 110 * t, yoyo: true });
        end(img, 520 * t, 200 * t, { scale: k * 0.5 });
        return 0;
      }
    }
    return 0;
  }

  /** Le centre du corps d'un combattant (là où les coups portent) et ses pieds. */
  private chest(v: View) {
    return { x: v.body.x, y: v.body.y + (FEET + v.barY) / 2 + 10, feet: v.body.y + FEET };
  }

  /** Attaque de base au corps à corps : la traînée du coup et l'étincelle au contact, sobres, à la couleur de l'élément. */
  private basicMelee(to: Pt, dir: number, color: number, t: number) {
    const g = this.add.graphics().setDepth(1400).setPosition(to.x - dir * 4, to.y).setBlendMode(Phaser.BlendModes.ADD);
    const a0 = dir > 0 ? -1.3 : Math.PI - 1.3, a1 = dir > 0 ? 1.1 : Math.PI + 1.1;
    g.lineStyle(9, color, 0.75).beginPath().arc(0, 0, 32, a0, a1).strokePath();
    g.lineStyle(3, 0xffffff, 1).beginPath().arc(0, 0, 32, a0 + 0.2, a1 - 0.2).strokePath();
    g.setScale(0.5).setAngle(dir * -35);
    this.tweens.add({ targets: g, scale: 1.15, angle: dir * 20, alpha: 0, duration: 170 * t, ease: 'Cubic.easeOut', onComplete: () => g.destroy() });
    this.sparks(to.x, to.y, color, 7, 42, t);
  }

  /** Attaque de base à distance : un trait d'énergie rapide (cœur blanc, traînée colorée), une petite étincelle à l'arrivée. */
  private basicShot(from: Pt, to: Pt, dir: number, color: number, t: number) {
    const x0 = from.x + dir * 34, ang = Math.atan2(to.y - from.y, to.x - x0);
    const tail = this.add.ellipse(x0, from.y, 46, 7, color, 0.75).setDepth(1000).setRotation(ang).setBlendMode(Phaser.BlendModes.ADD);
    const ball = this.add.ellipse(x0, from.y, 16, 9, 0xffffff).setDepth(1001).setRotation(ang);
    this.flashAt(x0, from.y, color, 9, t);
    this.tweens.add({ targets: [ball, tail], x: to.x, y: to.y, duration: 170 * t, ease: 'Quad.easeIn', onComplete: () => { ball.destroy(); tail.destroy(); } });
    this.time.delayedCall(170 * t, () => this.sparks(to.x, to.y, color, 6, 30, t));
  }

  /** Ce que la mise en scène HD emprunte à la scène (hd-fight.ts). */
  private hdHost?: HdHost;
  /**
   * Coup d'un personnage HD (combat d'essai) : sa vraie animation, le déplacement jusqu'à la cible, le projectile
   * jusqu'à la vraie case, l'impact sur la cible. Renvoie faux si ce combattant n'a pas d'animation HD.
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
      const name = this.text(src.body.x, src.body.y + src.barY - 34, this.skillName(skill?.id ?? ''), 28, hero ? '#ffe27a' : '#ff8a8a').setDepth(2000);
      this.tweens.add({ targets: name, y: name.y - 30, alpha: 0, delay: 650 / speed, duration: 450 / speed, onComplete: () => name.destroy() });
    }
    src.act = undefined;
    const ms = hdStrike(this, this.hdHost, src, which, hits, speed, skill);
    if (which === 'speciale') this.dim(Math.max(300, ms - 300));
    this.turnMs = ms + 260 / speed;
    return true;
  }

  private animateAttack(sourceId: string, hit: Hit, speed: number) {
    const src = this.views.get(sourceId);
    const dst = this.views.get(hit.target);
    if (!src || !dst) return;
    const dir = src.unit.side === 'hero' ? 1 : -1;
    const color = hex(ELEMENT_COLOR[src.unit.element]);
    const t = 1 / speed;
    const to = this.chest(dst);
    const touch = hit.kind === 'damage';
    src.act = { k: 'atk', t0: this.time.now, sp: speed, lead: 0 };
    let at: number;
    if (src.unit.ranged) {
      // le tireur recule d'un coup sec au départ du tir
      this.tweens.add({ targets: src.body, x: src.homeX - dir * 9, duration: 50 * t, yoyo: true, ease: 'Quad.easeOut' });
      this.basicShot(this.chest(src), to, dir, color, t);
      at = 170 * t;
      if (touch) this.time.delayedCall(at, () => this.recoil(dst, dir, 8, t));
    } else {
      // élan en arrière, ruée jusqu'à la cible, coup, puis retour à sa place
      this.tweens.add({ targets: src.body, x: src.homeX - dir * 14, duration: 70 * t, ease: 'Quad.easeOut' });
      this.tweens.add({ targets: src.body, x: dst.homeX - dir * 78, y: dst.homeY, delay: 70 * t, duration: 90 * t, ease: 'Expo.easeIn' });
      this.tweens.add({ targets: src.body, x: src.homeX, y: src.homeY, delay: 230 * t, duration: 170 * t, ease: 'Quad.easeInOut' });
      at = 160 * t;
      this.time.delayedCall(at, () => {
        this.basicMelee(to, dir, color, t);
        if (touch) {
          this.recoil(dst, dir, hit.crit ? 20 : 13, t);
          this.cameras.main.shake(70, hit.crit ? 0.005 : 0.0025);
        }
      });
    }
    this.time.delayedCall(at, () => this.showHit(hit, false));
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

  /** Le lanceur se charge : rayons de lumière derrière lui, halo autour du dessin, double lumineux qui jaillit. */
  private charge(v: View, color: number, t: number) {
    const p = this.chest(v);
    const rays = this.add.graphics().setDepth(v.body.depth - 1).setPosition(p.x, p.y).setBlendMode(Phaser.BlendModes.ADD);
    for (let i = 0; i < 14; i++) {
      const a = (i / 14) * Math.PI * 2, l = i % 2 ? 120 : 165;
      rays.fillStyle(i % 2 ? 0xffffff : color, i % 2 ? 0.35 : 0.55);
      rays.fillTriangle(Math.cos(a - 0.07) * 18, Math.sin(a - 0.07) * 18, Math.cos(a + 0.07) * 18, Math.sin(a + 0.07) * 18, Math.cos(a) * l, Math.sin(a) * l);
    }
    rays.setScale(0.3).setAlpha(0);
    const dy = p.y - v.body.y;
    this.tweens.add({ targets: rays, scale: 1.25, alpha: 1, angle: 50, duration: 260 * t, ease: 'Cubic.easeOut', onUpdate: () => rays.setPosition(v.body.x, v.body.y + dy) });
    this.tweens.add({ targets: rays, alpha: 0, angle: 90, delay: 260 * t, duration: v.unit.ranged ? 300 * t : 120 * t, onUpdate: () => rays.setPosition(v.body.x, v.body.y + dy), onComplete: () => rays.destroy() });
    const s = v.sprite;
    const ghost = this.cloneFig(s);
    this.tintDeep(ghost, color);
    ghost.setAlpha(0.9);
    v.body.addAt(ghost, v.body.getIndex(s) + 1);
    this.tweens.add({ targets: ghost, scaleX: v.sx * 1.4, scaleY: v.sy * 1.4, alpha: 0, delay: 120 * t, duration: 380 * t, ease: 'Cubic.easeOut', onComplete: () => ghost.destroy() });
    s.setScale(v.sx, v.sy);
    this.tweens.add({ targets: s, scaleX: v.sx * 1.18, scaleY: v.sy * 1.18, duration: 170 * t, yoyo: true, hold: 80 * t, ease: 'Back.easeOut' });
  }

  /** Bandeau de cinéma (héros) : le héros traverse l'écran dans une bande inclinée avec le nom de sa compétence. */
  private cutIn(v: View, skillId: string, color: number, t: number) {
    const y = Math.max(150, this.groundTop - (this.bigBoss ? 85 : 125)), h = 116;
    const band = this.add.container(W, y).setDepth(2600);
    const g = this.add.graphics();
    g.fillStyle(0x0a0818, 0.82).fillPoints([{ x: -60, y: -h / 2 + 16 }, { x: W + 60, y: -h / 2 - 16 }, { x: W + 60, y: h / 2 - 16 }, { x: -60, y: h / 2 + 16 }], true);
    g.fillStyle(color, 0.35).fillPoints([{ x: -60, y: h / 2 + 2 }, { x: W + 60, y: h / 2 - 30 }, { x: W + 60, y: h / 2 - 16 }, { x: -60, y: h / 2 + 16 }], true);
    g.lineStyle(4, color, 1).lineBetween(-60, -h / 2 + 16, W + 60, -h / 2 - 16).lineBetween(-60, h / 2 + 16, W + 60, h / 2 - 16);
    band.add(g);
    const cid = this.charId(v.unit), key = `p-${cid}`, px = `x-${cid}`;
    if (isPixel(cid) && this.textures.exists(px)) {
      // pixel art : la première image de sa planche, pieds en bas du bandeau, 200 de haut
      const top = PIXEL.chars[cid as keyof typeof PIXEL.chars][0];
      const img = this.add.image(120, h / 2 + 8, px, 0).setOrigin(PIXEL.fx / PIXEL.cw, PIXEL.fy / PIXEL.ch);
      img.setScale(200 / ((PIXEL.fy - top) * PIXEL.up));
      band.add(img);
      this.tweens.add({ targets: img, x: 175, duration: 560 * t });
    } else if (this.textures.exists(key)) {
      const img = this.add.image(120, h / 2 + 8, key).setOrigin(0.5, 1);
      img.setScale(Math.min(200 / img.height, 220 / img.width));
      band.add(img);
      this.tweens.add({ targets: img, x: 175, duration: 560 * t });
    }
    const name = this.text(W * 0.64, -2, this.skillName(skillId), 40, '#ffe27a');
    band.add(name);
    this.tweens.add({ targets: band, x: 0, duration: 150 * t, ease: 'Cubic.easeOut' });
    this.tweens.add({ targets: band, x: -W, alpha: 0, delay: 430 * t, duration: 160 * t, ease: 'Cubic.easeIn', onComplete: () => band.destroy() });
    // un trait de lumière balaie l'écran au moment où le bandeau arrive
    const streak = this.add.rectangle(-80, y, 44, h * 1.6, 0xffffff, 0.35).setDepth(2599).setAngle(-12).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: streak, x: W + 80, duration: 260 * t, ease: 'Quad.easeIn', onComplete: () => streak.destroy() });
  }

  private skillName(skillId: string) {
    return t(`skill.${skillId}`);
  }

  private baseZoom = 0;
  /** L'impact d'une compétence : éclair de couleur sur tout l'écran, secousse, petit coup de zoom, distorsion. */
  private punch(color: number, strong: boolean, t: number) {
    const cam = this.cameras.main;
    if (!this.baseZoom) this.baseZoom = cam.zoom;
    const flash = this.add.rectangle(0, 0, W, 2000, color, 0.32).setOrigin(0).setDepth(1900).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: flash, fillAlpha: 0, duration: 220 * t, onComplete: () => flash.destroy() });
    cam.shake(strong ? 260 : 170, strong ? 0.013 : 0.008);
    this.tweens.add({ targets: cam, zoom: this.baseZoom * 1.035, duration: 70 * t, yoyo: true, ease: 'Quad.easeOut', onComplete: () => cam.setZoom(this.baseZoom) });
    if (this.renderer.type === Phaser.WEBGL && cam.postFX) {
      const fx = cam.postFX.addBarrel(1);
      this.tweens.add({ targets: fx, amount: strong ? 1.1 : 1.06, duration: 90 * t, yoyo: true, ease: 'Quad.easeOut', onComplete: () => cam.postFX.remove(fx) });
    }
  }

  private animateSkill(sourceId: string, skillId: string, hits: Hit[], speed: number) {
    const src = this.views.get(sourceId);
    if (!src) return;
    const hero = src.unit.side === 'hero';
    const dir = hero ? 1 : -1;
    const tm = 1 / speed;
    const color = hex(ELEMENT_COLOR[src.unit.element]);
    // 1. le décor s'assombrit, le lanceur se charge ; les héros ont leur bandeau de cinéma
    this.dim(1250 * tm);
    this.charge(src, color, tm);
    let lead: number;
    if (hero && this.cutInBand) {
      this.cutIn(src, skillId, color, tm);
      lead = 470 * tm;
    } else {
      const name = this.text(src.body.x, src.body.y + src.barY - 34, this.skillName(skillId), 30, hero ? '#ffe27a' : '#ff8a8a').setDepth(2000);
      this.tweens.add({ targets: name, y: name.y - 40, alpha: 0, delay: 500 * tm, duration: 500 * tm, onComplete: () => name.destroy() });
      lead = 260 * tm;
    }
    src.act = { k: 'skill', t0: this.time.now, sp: speed, lead: lead * speed };
    // 2. la chorégraphie de la compétence sur chaque cible touchée (une même image pour toute la compétence)
    const list = SKILL_FX[src.unit.element][src.unit.ranged ? 'ranged' : 'melee'];
    const fxName = list[hash(skillId) % list.length]!;
    const from = this.chest(src);
    let impact = lead + 120 * tm;
    // au corps à corps, le lanceur fonce sur sa première cible, frappe, puis revient à sa place
    const first = hits.find((h) => h.kind === 'damage' && this.views.get(h.target));
    if (!src.unit.ranged && first) {
      const tgt = this.views.get(first.target)!;
      this.tweens.add({ targets: src.body, x: tgt.homeX - dir * 85, y: tgt.homeY, delay: lead - 120 * tm, duration: 120 * tm, ease: 'Expo.easeIn' });
      this.tweens.add({ targets: src.body, x: src.homeX, y: src.homeY, delay: lead + 520 * tm, duration: 220 * tm, ease: 'Quad.easeInOut' });
    }
    const seen = new Set<string>();
    hits.forEach((h) => {
      if (h.kind !== 'damage' || seen.has(h.target)) return;
      const v = this.views.get(h.target);
      if (!v) return;
      const delay = lead + seen.size * 70 * tm;
      seen.add(h.target);
      const at = this.skillFx.bind(this, fxName, from, this.chest(v), dir, tm);
      // l'impact (et les chiffres) arrive quand l'effet touche : on l'estime avant de lancer
      impact = Math.max(impact, delay + (TRAVEL[fxName] ?? 100) * tm);
      this.time.delayedCall(delay, at);
      this.time.delayedCall(delay + (TRAVEL[fxName] ?? 100) * tm, () => this.recoil(v, dir, 22, tm));
    });
    // 3. l'impact : éclair, secousse, zoom, distorsion, puis les chiffres
    this.time.delayedCall(impact, () => {
      if (seen.size) this.punch(color, seen.size > 1 || fxName === 'meteor' || fxName === 'lightning', tm);
      hits.forEach((h) => this.showHit(h, true));
    });
  }

  private showHit(hit: Hit, big: boolean) {
    const v = this.views.get(hit.target);
    if (!v) return;
    if (hit.kind === 'damage') v.hp = Math.max(0, v.hp - hit.amount);
    else if (hit.kind === 'heal') v.hp = Math.min(v.unit.maxHp, v.hp + hit.amount);
    else if (hit.kind === 'revive') v.hp = v.unit.hp;
    // les images d'effets ne viennent qu'avec les compétences (big) ; le reste reste discret
    if (big) {
      const p = this.chest(v), dir = v.unit.side === 'hero' ? 1 : -1;
      if (hit.kind === 'status' && hit.status && STATUS_FX[hit.status]) this.fx(STATUS_FX[hit.status]!, p.x, p.y, { size: 0.8, dur: 600 });
      if (hit.kind === 'revive') this.skillFx('holyBeam', p, p, dir, 1);
      if (hit.kind === 'heal' && !hit.dot) this.skillFx('heal', p, p, dir, 1);
      if (hit.kind === 'shield') this.skillFx('goldShield', p, p, dir, 1);
    }
    if (hit.kind === 'miss' || hit.kind === 'status' || hit.kind === 'revive') {
      if (hit.kind === 'revive') this.tweens.add({ targets: v.body, alpha: 1, y: v.homeY, angle: 0, duration: 400 });
      const label = hit.kind === 'miss' ? t('fx.miss') : hit.kind === 'revive' ? '✚' : t(`st.${hit.status}`, { n: '' }).replace(/[+−-]\s*%/, '').trim();
      const color = hit.kind === 'miss' ? '#c8d0ff' : hit.kind === 'revive' ? '#5dff9a' : STATUS_COLOR[hit.status ?? 'stun'] ?? '#ffe27a';
      const icon = hit.kind === 'status' && `st-${hit.status}` in ICON_INDEX && this.textures.exists('icons');
      const n = icon ? this.add.image(v.body.x, v.body.y - 92, 'icons', ICON_INDEX[`st-${hit.status}`]).setDisplaySize(40, 40).setDepth(2000) : this.text(v.body.x, v.body.y - 92, label, 22, color).setDepth(2000);
      this.tweens.add({ targets: n, y: n.y - 34, alpha: 0, duration: icon ? 1000 : 800, onComplete: () => n.destroy() });
      return;
    }
    const x = v.body.x + Phaser.Math.Between(-18, 18);
    const y = v.body.y - 40;
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
      // touché : le dessin rougit un instant (un flash tout blanc effaçait les grands dessins)
      this.tint(v, 0xff9a9a);
      this.time.delayedCall(90, () => this.tint(v));
      if (hit.stun) {
        const star = this.text(v.body.x + 30, v.body.y - 70, '✦', 28, '#ffe27a').setDepth(2000);
        this.tweens.add({ targets: star, angle: 360, alpha: 0, duration: 900, onComplete: () => star.destroy() });
      }
    }
    if (hit.dot) color = hit.kind === 'heal' ? '#5dff9a' : STATUS_COLOR[hit.status ?? 'burn'] ?? color;
    const n = this.text(x, y, hit.crit ? `${label}!` : label, hit.dot ? 20 : (big ? 34 : 26) + (hit.crit ? 8 : 0), color).setDepth(2000);
    if (this.hdMode && !hit.dot) {
      // essai HD : le chiffre jaillit (gros, puis il se pose), tient un instant, puis monte et s'efface
      const y0 = v.body.y + v.barY - 8;
      n.setPosition(x, y0).setScale(hit.crit ? 2 : 1.7);
      this.tweens.add({ targets: n, scale: 1, duration: 200, ease: 'Back.easeOut' });
      this.tweens.add({ targets: n, y: y0 - 46, alpha: 0, delay: 420, duration: 520, ease: 'Quad.easeIn', onComplete: () => n.destroy() });
      return;
    }
    this.tweens.add({ targets: n, y: y - 60, alpha: 0, duration: 750, ease: 'Quad.easeOut', onComplete: () => n.destroy() });
  }

  protected banner(label: string, y = 300) {
    const b = this.text(W / 2, y, label, 56).setDepth(3000).setScale(0.5);
    this.tweens.add({ targets: b, scale: 1, duration: 250, ease: 'Back.easeOut' });
    this.tweens.add({ targets: b, alpha: 0, delay: 800, duration: 300, onComplete: () => b.destroy() });
  }
}
