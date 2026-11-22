// Petites pièces d'interface réutilisées partout.
import type { ComponentChildren } from 'preact';
import { heroDef } from '../../core/data/heroes';
import { itemMain, type Item } from '../../core/data/items';
import { MAX_YELLOW, MYTHIC_STARS } from '../../core/data/stars';
import type { Hero } from '../../core/types';
import { Backdrop } from './backdrop';
import { ELEMENT_COLOR, ITEM_COLORS, RARITY_COLOR, heroImage } from '../art';
import { fmt, t } from '../i18n';
import { close } from './nav';
import { ICON_COLS, ICON_INDEX, ICON_ROWS } from '../icons-meta';

// ---------- Icônes (dessins vectoriels simples) ----------

const ICONS: Record<string, ComponentChildren> = {
  gold: <><circle cx="12" cy="12" r="9" fill="#ffc94a" stroke="#b8860b" stroke-width="2" /><path d="M9 9h5a2 2 0 0 1 0 4H9v3" stroke="#8a6200" stroke-width="2" fill="none" /></>,
  essence: <><path d="M12 3c4 5 6 8 6 11a6 6 0 0 1-12 0c0-3 2-6 6-11z" fill="#7cf7c1" stroke="#2a9d8f" stroke-width="1.5" /></>,
  gems: <><path d="M6 4h12l4 6-10 11L2 10z" fill="#ff5fa2" stroke="#b0246a" stroke-width="1.5" /><path d="M2 10h20M8 4l4 17 4-17" stroke="#ffd1e6" stroke-width="1" fill="none" /></>,
  scrolls: <><rect x="5" y="4" width="14" height="16" rx="3" fill="#ffe8b0" stroke="#c9a227" stroke-width="2" /><path d="M8 9h8M8 13h8" stroke="#c9a227" stroke-width="1.6" /><circle cx="12" cy="17" r="2" fill="#a35cff" /></>,
  basicScrolls: <><rect x="5" y="4" width="14" height="16" rx="3" fill="#dfe6f5" stroke="#7d8bb0" stroke-width="2" /><path d="M8 9h8M8 13h8" stroke="#7d8bb0" stroke-width="1.6" /></>,
  arenaTokens: <><circle cx="12" cy="12" r="9" fill="#e5484d" stroke="#8a1c20" stroke-width="2" /><path d="M8 16l8-8M9 8h-1v1M16 15v1h-1" stroke="#fff" stroke-width="2" /></>,
  guildCoins: <><circle cx="12" cy="12" r="9" fill="#4c8dff" stroke="#1d4fa8" stroke-width="2" /><path d="M8 7h8v6l-4 4-4-4z" fill="#dce8ff" /></>,
  crystals: <><path d="M12 2l6 8-6 12-6-12z" fill="#b388ff" stroke="#6b3fa0" stroke-width="1.5" /></>,
  fragments: <><path d="M4 14l6-10 4 6 6-2-4 12H6z" fill="#ffc94a" stroke="#b8860b" stroke-width="1.5" /></>,
  campaign: <><path d="M5 21V4h11l-2 4 2 4H7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" /></>,
  heroes: <><path d="M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z" fill="none" stroke="currentColor" stroke-width="2.2" /></>,
  summon: <><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2.2" /><path d="M12 6l1.8 4 4.2.4-3.2 2.8 1 4.2-3.8-2.3-3.8 2.3 1-4.2L6 10.4l4.2-.4z" fill="currentColor" /></>,
  adventure: <><path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z M9 4v14 M15 6v14" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" /></>,
  guild: <><path d="M6 3h12v12l-6 5-6-5z" fill="none" stroke="currentColor" stroke-width="2.2" /><path d="M9 8h6M9 11h6" stroke="currentColor" stroke-width="2" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="3" fill="#fff3d6" stroke="#c9a227" stroke-width="2" /><rect x="3" y="5" width="18" height="5" rx="2" fill="#e5484d" /><path d="M8 3v4M16 3v4" stroke="#8a6200" stroke-width="2" stroke-linecap="round" /><path d="M8.5 15l2.2 2.2 4.8-4.8" stroke="#35c873" stroke-width="2.4" fill="none" stroke-linecap="round" /></>,
  mail: <><rect x="3" y="6" width="18" height="13" rx="2" fill="#dfe7ff" stroke="#4c8dff" stroke-width="2" /><path d="M4 7l8 6 8-6" stroke="#4c8dff" stroke-width="2" fill="none" /></>,
  quests: <><rect x="5" y="3" width="14" height="18" rx="2" fill="#ffe8b0" stroke="#c9a227" stroke-width="2" /><path d="M8 9l2 2 4-4M8 15h8" stroke="#8a6200" stroke-width="2" fill="none" /></>,
  shop: <><path d="M4 8h16l-1.5 12h-13z" fill="#ffc94a" stroke="#b8860b" stroke-width="2" /><path d="M8 8a4 4 0 0 1 8 0" fill="none" stroke="#b8860b" stroke-width="2" /></>,
  pass: <><path d="M4 6h16v4a2 2 0 0 0 0 4v4H4v-4a2 2 0 0 0 0-4z" fill="#a35cff" stroke="#5b2a9f" stroke-width="2" /><path d="M12 9l1 2h2l-1.6 1.3.6 2.2-2-1.3-2 1.3.6-2.2L9 11h2z" fill="#fff" /></>,
  ranking: <><path d="M7 4h10v5a5 5 0 0 1-10 0z" fill="#ffc94a" stroke="#b8860b" stroke-width="2" /><path d="M12 14v4M8 20h8M7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4" stroke="#b8860b" stroke-width="2" fill="none" /></>,
  friends: <><circle cx="9" cy="8" r="3.5" fill="currentColor" /><circle cx="16.5" cy="9" r="3" fill="currentColor" opacity="0.7" /><path d="M2 20c0-4 3-6.5 7-6.5s7 2.5 7 6.5z" fill="currentColor" /><path d="M15 13.6c3.6-.4 7 1.6 7 5.4h-4.6" fill="currentColor" opacity="0.7" /></>,
  gift: <><rect x="3" y="9" width="18" height="12" rx="2" fill="currentColor" /><rect x="2" y="6" width="20" height="4" rx="1.5" fill="currentColor" opacity="0.8" /><path d="M12 6v15" stroke="#0008" stroke-width="2" /><path d="M12 6c-2-4-7-4-6 0zm0 0c2-4 7-4 6 0z" fill="none" stroke="currentColor" stroke-width="2" /></>,
  chat: <><path d="M4 5h16v11H9l-5 4z" fill="#4c8dff" stroke="#1d4fa8" stroke-width="2" stroke-linejoin="round" /><circle cx="9" cy="10.5" r="1.3" fill="#fff" /><circle cx="13" cy="10.5" r="1.3" fill="#fff" /><circle cx="17" cy="10.5" r="1.3" fill="#fff" /></>,
  settings: <><circle cx="12" cy="12" r="3.5" fill="none" stroke="#c7cbe0" stroke-width="2" /><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l3 3M16 16l3 3M19 5l-3 3M8 16l-3 3" stroke="#c7cbe0" stroke-width="2" /></>,
  weapon: <><path d="M19 3l2 2-11 11-3 1 1-3z" fill="#d7dce6" stroke="#7d8191" stroke-width="1.2" /><path d="M5 15l4 4M3 21l3-3" stroke="#c98a3a" stroke-width="2.4" stroke-linecap="round" /></>,
  armor: <><path d="M7 3h10l3 4-2 3v11H6V10L4 7z" fill="#9aa3b5" stroke="#5c606d" stroke-width="1.4" stroke-linejoin="round" /><path d="M9 3l3 4 3-4" fill="none" stroke="#5c606d" stroke-width="1.4" /></>,
  helmet: <><path d="M4 15a8 8 0 0 1 16 0v3H4z" fill="#9aa3b5" stroke="#5c606d" stroke-width="1.4" /><path d="M4 13h16M12 7v6" stroke="#5c606d" stroke-width="1.6" /></>,
  boots: <><path d="M7 3h6v10l6 3v4H5V13z" fill="#a0703a" stroke="#5a3a10" stroke-width="1.4" stroke-linejoin="round" /><path d="M5 17h14" stroke="#5a3a10" stroke-width="1.4" /></>,
  dust: <><circle cx="8" cy="15" r="3.5" fill="#7cf7e1" /><circle cx="15" cy="10" r="4.5" fill="#4fd1c5" /><circle cx="16" cy="18" r="2.5" fill="#b388ff" /><circle cx="9" cy="7" r="1.8" fill="#fff" /></>,
  lock: <><rect x="5" y="10" width="14" height="11" rx="2" fill="currentColor" /><path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="2.2" /></>,
  power: <><path d="M13 2L4 14h7l-1 8 9-12h-7z" fill="#ffc94a" stroke="#b8860b" stroke-width="1.2" /></>,
  clock: <><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2" /><path d="M12 7v5l3 2" stroke="currentColor" stroke-width="2" fill="none" /></>,
  ad: <><rect x="3" y="5" width="18" height="14" rx="3" fill="#3ccf7a" /><path d="M10 9v6l5-3z" fill="#fff" /></>,
  tower: <><path d="M7 21V8h10v13M9 8V4h6v4M5 21h14" fill="none" stroke="currentColor" stroke-width="2" /><path d="M11 13h2v3h-2z" fill="currentColor" /></>,
  dungeons: <><path d="M4 21V11a8 8 0 0 1 16 0v10z" fill="none" stroke="currentColor" stroke-width="2" /><path d="M9 21v-6a3 3 0 0 1 6 0v6" fill="currentColor" /></>,
  missions: <><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2" /><path d="M15.5 8.5l-2 5-5 2 2-5z" fill="currentColor" /></>,
  dailyBoss: <><path d="M5 10a7 7 0 0 1 14 0v4l-2 2v4H7v-4l-2-2z" fill="none" stroke="currentColor" stroke-width="2" /><circle cx="9.5" cy="11" r="1.6" fill="currentColor" /><circle cx="14.5" cy="11" r="1.6" fill="currentColor" /></>,
  arena: <><path d="M5 19L19 5M15 5h4v4M9 19H5v-4M19 19L5 5M5 9V5h4M15 19h4v-4" fill="none" stroke="currentColor" stroke-width="2" /></>,
  defense: <><path d="M3 20c4-6 6-2 9-8s5-6 9-8" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3 3" /><circle cx="7" cy="10" r="2.5" fill="currentColor" /><circle cx="16" cy="17" r="2.5" fill="currentColor" /></>,
};

/** Ce picto a-t-il son dessin (public/art/icons.webp) ? */
export function hasArt(name: string): boolean {
  return name in ICON_INDEX;
}

/** Un picto dessiné, découpé dans l'image de tous les pictos ; sa taille vient de `size` ou de la classe CSS. */
export function Art({ name, size, class: cls }: { name: string; size?: number; class?: string }) {
  const i = ICON_INDEX[name];
  if (i === undefined) return null;
  const x = ((i % ICON_COLS) / (ICON_COLS - 1)) * 100, y = (Math.floor(i / ICON_COLS) / Math.max(1, ICON_ROWS - 1)) * 100;
  return (
    <span class={`art ${cls ?? ''}`} aria-hidden="true" style={{
      ...(size ? { width: `${size}px`, height: `${size}px` } : {}),
      backgroundImage: 'url(art/icons.webp)', backgroundRepeat: 'no-repeat', backgroundSize: `${ICON_COLS * 100}% ${ICON_ROWS * 100}%`, backgroundPosition: `${x}% ${y}%`,
    }} />
  );
}

export function Icon({ name, size = 22 }: { name: string; size?: number }) {
  if (hasArt(name)) return <Art name={name} size={size} class="icon icon-art" />;
  return (
    <svg class="icon" width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      {ICONS[name] ?? null}
    </svg>
  );
}

// ---------- Boutons, montants, barres ----------

type BtnKind = 'green' | 'blue' | 'gold' | 'ghost' | 'red' | 'purple';

export function Btn(p: {
  kind?: BtnKind; onClick?: () => void; disabled?: boolean; small?: boolean; wide?: boolean;
  children: ComponentChildren; dot?: boolean; class?: string;
}) {
  return (
    <button
      class={`btn btn-${p.kind ?? 'blue'}${p.small ? ' btn-small' : ''}${p.wide ? ' btn-wide' : ''} ${p.class ?? ''}`}
      disabled={p.disabled}
      onClick={() => !p.disabled && p.onClick?.()}
    >
      {p.children}
      {p.dot && <RedDot />}
    </button>
  );
}

export function Cur({ k, n, big }: { k: string; n: number; big?: boolean }) {
  return (
    <span class={`cur${big ? ' cur-big' : ''}`}>
      <Icon name={k} size={big ? 26 : 18} />
      <span>{fmt(n)}</span>
    </span>
  );
}

export function RedDot() {
  return <span class="dot" />;
}

export function Bar({ value, max, color = '#3ccf7a', label }: { value: number; max: number; color?: string; label?: string }) {
  const pct = Math.max(0, Math.min(100, (value / Math.max(1, max)) * 100));
  return (
    <div class="bar">
      <div class="bar-fill" style={{ width: `${pct}%`, background: color }} />
      {label && <span class="bar-label">{label}</span>}
    </div>
  );
}

export function Tabs<T extends string>({ value, options, onChange }: { value: T; options: [T, string, boolean?][]; onChange: (v: T) => void }) {
  return (
    <div class="tabs">
      {options.map(([v, label, dot]) => (
        <button class={`tab${v === value ? ' tab-on' : ''}`} onClick={() => onChange(v)}>
          {label}
          {dot && <RedDot />}
        </button>
      ))}
    </div>
  );
}

// ---------- Héros et objets ----------

export function Stars({ stars }: { stars: number }) {
  if (stars >= MYTHIC_STARS) return <span class="stars mythic">{t('rarity.mythic')}</span>;
  const red = stars > MAX_YELLOW;
  const n = red ? stars - MAX_YELLOW : stars;
  return <span class={`stars${red ? ' red' : ''}`}>{'★'.repeat(n)}</span>;
}

export function HeroCard(p: { hero: Hero; power?: number; onClick?: () => void; selected?: boolean; dim?: boolean; badge?: string; small?: boolean }) {
  const d = heroDef(p.hero.defId);
  const mythic = p.hero.stars >= MYTHIC_STARS;
  const color = mythic ? '#ff4d5e' : RARITY_COLOR[d.rarity];
  const Tag = p.onClick ? 'button' : 'span';
  // Derrière le héros : un mur à la couleur de sa rareté, frappé de l'emblème de son élément, et un sol éclairé.
  // Par-dessus : un cadre de métal de la même couleur (il luit sur les Légendaires), le niveau, l'élément, les étoiles.
  return (
    <Tag
      class={`hcard hcard-${d.rarity} el-${d.element}${mythic ? ' hcard-mythic' : ''}${p.selected ? ' hcard-on' : ''}${p.dim ? ' hcard-dim' : ''}${p.small ? ' hcard-small' : ''}`}
      style={{ '--rar': color, '--el': ELEMENT_COLOR[d.element] } as never}
      onClick={p.onClick}
    >
      <img src={heroImage(d.id)} alt={d.name} />
      <i class="hcard-frame" />
      <Art name={d.element} class="hcard-el" />
      <span class="hcard-lv">{p.hero.level}</span>
      <Stars stars={p.hero.stars} />
      {p.power !== undefined && <span class="hcard-pow">{fmt(p.power)}</span>}
      {p.badge && <span class="hcard-badge">{p.badge}</span>}
    </Tag>
  );
}

export function ItemIcon(p: { item?: Item; level?: number; onClick?: () => void; heroDefId?: string; slot?: string; hideLevel?: boolean }) {
  const { item } = p;
  const Tag = p.onClick ? 'button' : 'span';
  if (!item) {
    return (
      <Tag class="item item-empty" onClick={p.onClick}>
        {!!p.level && <span class="item-level">+{p.level}</span>}
      </Tag>
    );
  }
  return (
    <Tag class="item" style={{ '--rar': ITEM_COLORS[item.rarity] } as never} onClick={p.onClick}>
      <Icon name={hasArt(`${item.slot}-${item.rarity}`) ? `${item.slot}-${item.rarity}` : item.slot} size={38} />
      <span class="item-bonus">+{itemMain(item, p.level ?? 0)}%</span>
      {item.set && (hasArt(`set-${item.set}`) ? <Art name={`set-${item.set}`} class="item-set-art" /> : <span class={`item-set set-${item.set}`} />)}
      {!!p.level && !p.hideLevel && <span class="item-level">+{p.level}</span>}
      {p.heroDefId && <img class="item-owner" src={heroImage(p.heroDefId)} alt="" />}
    </Tag>
  );
}

// ---------- Pages plein écran (préparation, forge, fusion) ----------

export function Page({ title, children }: { title: string; children: ComponentChildren }) {
  return (
    <div class="page">
      <Backdrop kind="page" />
      <header class="prep-head">
        <button class="x" aria-label={t('back')} onClick={close}>‹</button>
        <h2>{title}</h2>
      </header>
      <div class="page-body">{children}</div>
    </div>
  );
}

// ---------- Fenêtres ----------

export function Modal(p: { title: string; children: ComponentChildren; wide?: boolean; center?: boolean; onClose?: () => void }) {
  return (
    <div class={`modal-back${p.center ? ' center' : ''}`} onClick={(e) => e.target === e.currentTarget && (p.onClose ?? close)()}>
      <div class={`modal${p.wide ? ' modal-wide' : ''}`}>
        <div class="modal-head">
          <h2>{p.title}</h2>
          <button class="x" aria-label={t('close')} onClick={p.onClose ?? close}>✕</button>
        </div>
        <div class="modal-body">{p.children}</div>
      </div>
    </div>
  );
}

export function Locked({ stage }: { stage: number }) {
  return (
    <span class="locked">
      <Icon name="lock" size={16} />
      {t('locked', { n: stage })}
    </span>
  );
}

export function duration(ms: number): string {
  const s = Math.max(0, Math.ceil(ms / 1000));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (h) return `${h} h ${String(m).padStart(2, '0')}`;
  return `${m} min ${String(s % 60).padStart(2, '0')}`;
}
