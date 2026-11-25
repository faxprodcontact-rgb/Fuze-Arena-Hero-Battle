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

// ---------- Pictos (pixel art, planche public/art/icons.webp : refonte-graphique/pixel/ui/pictos/) ----------

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

/** Les petits signes dessinés en pixels par px.ts (variables CSS --px-<signe>). */
export type SignName = 'star' | 'star-red' | 'check' | 'cross' | 'up' | 'chev' | 'chev-s' | 'back-s' | 'play' | 'stop' | 'op-plus' | 'op-eq' | 'op-arrow';

/** Un petit signe en pixels (coche, croix, étoile, chevron…), agrandi ×k sans flou (k = 2 par défaut : 1 pixel = 2 px). */
export function Sign({ name, k, class: cls }: { name: SignName; k?: number; class?: string }) {
  return <i class={`sign sign-${name} ${cls ?? ''}`} aria-hidden="true" style={k ? { '--k': k } : undefined} />;
}

/** Un texte traduit où « ★ » est remplacé par l'étoile dessinée (« 2 héros ★3+ », « Éveil ★10 »). */
export function starText(text: string): ComponentChildren {
  const parts = text.split('★');
  return parts.map((p, i) => (i ? <><Sign name="star" class="sign-in-text" />{p}</> : p));
}

/** Un picto de la planche à la taille voulue (rien si le nom n'y est pas). */
export function Icon({ name, size = 22 }: { name: string; size?: number }) {
  return <Art name={name} size={size} class="icon icon-art" />;
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
  // des étoiles dessinées en pixels (--px-star de px.ts), à la taille du texte autour
  return <span class={`stars${red ? ' red' : ''}`} role="img" aria-label={`${n}★`}>{Array.from({ length: n }, () => <i />)}</span>;
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
