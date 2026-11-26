// Les grains de lumière du tirage, dessinés sur un <canvas> (plus léger qu'une foule d'éléments pour un téléphone) :
// aspirés en spirale vers le portail pendant qu'il se charge, projetés en courbes quand il s'ouvre, rassemblés en
// silhouette quand un héros sort, une pluie d'étincelles d'or pour un Légendaire, des grains qui montent de l'estrade.
// Les grains laissent une traîne courte (l'image précédente s'efface un peu à chaque fois), ce qui dessine des courbes.
// La boucle s'arrête d'elle-même quand plus rien ne bouge.

type Particle = {
  x: number; y: number; vx: number; vy: number;
  /** vers un point (aspiration, rassemblement) : la force et la cible */
  tx?: number; ty?: number; pull?: number;
  /** une rotation autour de la cible (spirale) */
  spin?: number;
  drag: number; grav: number;
  life: number; max: number; size: number;
  sprite: HTMLCanvasElement; star: boolean;
};
type Emitter = { until: number; rate: number; acc: number; spawn: () => void };

const MAX = 520;

function hexToRgb(c: string): [number, number, number] {
  const h = c.replace('#', '');
  const n = parseInt(h.length === 3 ? h.split('').map((x) => x + x).join('') : h.slice(0, 6), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export class SummonFx {
  private ctx: CanvasRenderingContext2D | null;
  private ps: Particle[] = [];
  private ems: Emitter[] = [];
  private raf = 0;
  private last = 0;
  private dpr = 1;
  private sprites = new Map<string, HTMLCanvasElement>();
  private stars = new Map<string, HTMLCanvasElement>();
  private reduced = typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;

  constructor(private canvas: HTMLCanvasElement) {
    this.ctx = canvas.getContext('2d');
    this.resize();
  }

  resize(): void {
    this.dpr = Math.min(2, window.devicePixelRatio || 1);
    const r = this.canvas.getBoundingClientRect();
    this.canvas.width = Math.max(1, Math.round(r.width * this.dpr));
    this.canvas.height = Math.max(1, Math.round(r.height * this.dpr));
  }

  /** Un grain : un rond flou blanc au cœur, de la couleur voulue autour (préparé une fois par couleur). */
  private sprite(color: string, star = false): HTMLCanvasElement {
    const map = star ? this.stars : this.sprites;
    let s = map.get(color);
    if (s) return s;
    s = document.createElement('canvas');
    s.width = s.height = 48;
    const c = s.getContext('2d')!;
    const [r, g, b] = hexToRgb(color);
    const grd = c.createRadialGradient(24, 24, 0, 24, 24, 24);
    grd.addColorStop(0, 'rgba(255,255,255,1)');
    grd.addColorStop(0.18, `rgba(${r},${g},${b},0.95)`);
    grd.addColorStop(0.5, `rgba(${r},${g},${b},0.32)`);
    grd.addColorStop(1, `rgba(${r},${g},${b},0)`);
    c.fillStyle = grd;
    c.fillRect(0, 0, 48, 48);
    if (star) {
      // une étoile à quatre branches courbes par-dessus la lueur
      c.fillStyle = '#fff';
      c.beginPath();
      c.moveTo(24, 2); c.quadraticCurveTo(26, 22, 46, 24); c.quadraticCurveTo(26, 26, 24, 46);
      c.quadraticCurveTo(22, 26, 2, 24); c.quadraticCurveTo(22, 22, 24, 2); c.fill();
    }
    map.set(color, s);
    return s;
  }

  private add(p: Omit<Particle, 'sprite' | 'star' | 'drag' | 'grav'> & { color: string; star?: boolean; drag?: number; grav?: number }): void {
    if (this.ps.length >= MAX) this.ps.shift();
    this.ps.push({ drag: 0.985, grav: 0, ...p, star: !!p.star, sprite: this.sprite(p.color, p.star) });
    this.start();
  }

  private emit(ms: number, rate: number, spawn: () => void): void {
    this.ems.push({ until: performance.now() + ms, rate, acc: 0, spawn });
    this.start();
  }

  /** Le portail se charge : des grains naissent loin autour et filent en spirale vers lui. */
  charge(cx: number, cy: number, radius: number, colors: string[], ms: number): void {
    if (this.reduced) return;
    this.emit(ms, 90, () => {
      const a = Math.random() * Math.PI * 2, r = radius * (0.9 + Math.random() * 0.7);
      this.add({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r, vx: 0, vy: 0, tx: cx, ty: cy, pull: 5 + Math.random() * 4, spin: 2.6,
        life: 0, max: 0.75 + Math.random() * 0.3, size: 7 + Math.random() * 9, color: colors[Math.floor(Math.random() * colors.length)]!, drag: 0.9 });
    });
  }

  /** Le portail éclate : des grains projetés en courbes (ils tournent en s'éloignant), quelques étoiles. */
  burst(cx: number, cy: number, colors: string[], n: number, power: number): void {
    const k = this.reduced ? Math.round(n / 4) : n;
    for (let i = 0; i < k; i++) {
      const a = Math.random() * Math.PI * 2, v = power * (0.35 + Math.random() * 0.75);
      const curl = (Math.random() < 0.5 ? -1 : 1) * (0.6 + Math.random() * 0.6);
      this.add({ x: cx, y: cy, vx: Math.cos(a) * v + Math.cos(a + Math.PI / 2) * v * 0.35 * curl, vy: Math.sin(a) * v + Math.sin(a + Math.PI / 2) * v * 0.35 * curl,
        life: 0, max: 0.7 + Math.random() * 0.7, size: 8 + Math.random() * 14, color: colors[i % colors.length]!, star: i % 9 === 0, drag: 0.955, grav: 120 });
    }
  }

  /** Un héros se forme : des grains venus de tout autour se posent dans sa silhouette (le rectangle donné). */
  converge(x: number, y: number, w: number, h: number, color: string, n: number): void {
    if (this.reduced) return;
    for (let i = 0; i < n; i++) {
      const tx = x + w * (0.25 + Math.random() * 0.5), ty = y + h * (0.12 + Math.random() * 0.8);
      const a = Math.random() * Math.PI * 2, r = 120 + Math.random() * 120;
      this.add({ x: tx + Math.cos(a) * r, y: ty + Math.sin(a) * r, vx: 0, vy: 0, tx, ty, pull: 9 + Math.random() * 5, spin: 1.4,
        life: 0, max: 0.42 + Math.random() * 0.12, size: 6 + Math.random() * 8, color: Math.random() < 0.35 ? '#ffffff' : color, drag: 0.86 });
    }
  }

  /** Des étincelles qui tombent doucement d'en haut (Légendaire). */
  rain(w: number, h: number, color: string, ms: number): void {
    if (this.reduced) return;
    this.emit(ms, 16, () => {
      this.add({ x: Math.random() * w, y: Math.random() * h * 0.7, vx: (Math.random() - 0.5) * 50, vy: 25 + Math.random() * 35, life: 0, max: 2.6 + Math.random(),
        size: 8 + Math.random() * 10, color, star: Math.random() < 0.5, drag: 0.995 });
    });
  }

  /** Des grains qui montent de l'estrade, sous le héros. */
  motes(x: number, y: number, w: number, color: string, ms: number, rate = 14): void {
    if (this.reduced) return;
    this.emit(ms, rate, () => {
      this.add({ x: x + (Math.random() - 0.5) * w, y, vx: (Math.random() - 0.5) * 12, vy: -(40 + Math.random() * 60), life: 0, max: 1.1 + Math.random() * 0.8,
        size: 5 + Math.random() * 7, color, drag: 0.99 });
    });
  }

  /** Tout arrêter (on passe à la suite). */
  clear(): void {
    this.ps = [];
    this.ems = [];
    this.ctx?.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  destroy(): void {
    cancelAnimationFrame(this.raf);
    this.raf = 0;
    this.clear();
  }

  private start(): void {
    if (this.raf) return;
    this.last = performance.now();
    this.raf = requestAnimationFrame(this.tick);
  }

  private tick = (now: number): void => {
    const ctx = this.ctx;
    if (!ctx) return;
    const dt = Math.min(0.05, (now - this.last) / 1000);
    this.last = now;
    for (const e of this.ems) {
      e.acc += e.rate * dt;
      while (e.acc >= 1) { e.acc -= 1; e.spawn(); }
    }
    this.ems = this.ems.filter((e) => e.until > now);
    // la traîne : l'image précédente pâlit au lieu de disparaître
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = 'rgba(0,0,0,0.45)';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.globalCompositeOperation = 'lighter';
    const d = this.dpr;
    const keep: Particle[] = [];
    for (const p of this.ps) {
      p.life += dt;
      if (p.life >= p.max) continue;
      if (p.tx !== undefined && p.ty !== undefined) {
        const dx = p.tx - p.x, dy = p.ty - p.y;
        p.vx += dx * (p.pull ?? 0) * dt * 4 - dy * (p.spin ?? 0) * dt * 2;
        p.vy += dy * (p.pull ?? 0) * dt * 4 + dx * (p.spin ?? 0) * dt * 2;
      }
      p.vy += p.grav * dt;
      const k = Math.pow(p.drag, dt * 60);
      p.vx *= k; p.vy *= k;
      p.x += p.vx * dt; p.y += p.vy * dt;
      const t = p.life / p.max;
      const a = t < 0.15 ? t / 0.15 : 1 - (t - 0.15) / 0.85;
      ctx.globalAlpha = Math.max(0, a);
      const s = p.size * d * (p.star ? 1.6 : 1) * (1 - t * 0.4);
      ctx.drawImage(p.sprite, p.x * d - s / 2, p.y * d - s / 2, s, s);
      keep.push(p);
    }
    ctx.globalAlpha = 1;
    this.ps = keep;
    if (this.ps.length || this.ems.length) this.raf = requestAnimationFrame(this.tick);
    else {
      this.raf = 0;
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
  };
}
