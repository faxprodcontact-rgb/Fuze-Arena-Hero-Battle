// Petites pièces d'interface réutilisées partout.
import type { ComponentChildren } from 'preact';
import { heroDef } from '../../core/data/heroes';
import { itemMain, type Item } from '../../core/data/items';
import { MAX_YELLOW, MYTHIC_STARS } from '../../core/data/stars';
import type { Hero } from '../../core/types';
import { Backdrop } from './backdrop';
import { ELEMENT_COLOR, ITEM_COLORS, RARITY_COLOR, figureUrl, heroImage } from '../art';
import { fmt, t } from '../i18n';
import { close } from './nav';
import { ICON_COLS, ICON_INDEX, ICON_ROWS } from '../icons-meta';
import { HD_FIG } from '../hd-figures';
import { heroArt } from '../look';
import { btClass, type BtSize, type BtTone } from './buttons';
import { artUrl } from '../art-url';

// ---------- Pictos (style moderne, lisses : planche public/art/icons.webp, refonte-graphique/ui-moderne/pictos/) ----------

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
      backgroundImage: `url(${artUrl('art/icons.webp')})`, backgroundRepeat: 'no-repeat', backgroundSize: `${ICON_COLS * 100}% ${ICON_ROWS * 100}%`, backgroundPosition: `${x}% ${y}%`,
    }} />
  );
}

/** Les petits signes (style moderne, SVG de signs-art.ts posés par px.ts dans les variables CSS --px-<signe>). */
export type SignName = 'star' | 'star-red' | 'check' | 'cross' | 'up' | 'chev' | 'chev-s' | 'back-s' | 'play' | 'stop' | 'op-plus' | 'op-eq' | 'op-arrow';

/** Un petit signe (coche, croix, étoile, chevron…), à k fois sa taille de base (k = 2 par défaut). */
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

/** La teinte de pierre de chaque sorte de bouton (buttons.ts) : l'action principale est le basalte allumé. */
const BTN_TONE: Record<BtnKind, BtTone> = { green: 'basalte', gold: 'or', purple: 'arcane', red: 'feu', blue: 'ardoise', ghost: 'ardoise' };

/**
 * Un bouton « Pierre de l'arène » (style.css, « Boutons »). Taille : `small` = s (38 px), normal = m (48), `btn-fight` = l
 * (62) ; `size` la donne directement. Les classes `btn btn-<sorte>` restent posées (le tutoriel les vise).
 */
export function Btn(p: {
  kind?: BtnKind; onClick?: () => void; disabled?: boolean; small?: boolean; wide?: boolean; size?: BtSize;
  children: ComponentChildren; dot?: boolean; class?: string;
}) {
  const kind = p.kind ?? 'blue';
  const size = p.size ?? (p.small ? 's' : /\bbtn-fight\b/.test(p.class ?? '') ? 'l' : 'm');
  return (
    <button
      class={`btn btn-${kind} ${btClass(BTN_TONE[kind], size)}${p.small ? ' btn-small' : ''}${p.wide ? ' btn-wide' : ''} ${p.class ?? ''}`}
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
        <button class={`tab${v === value ? ` tab-on ${btClass('basalte', 's')}` : ''}`} onClick={() => onChange(v)}>
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

/**
 * Le héros en entier dans sa case (demande du propriétaire, 26/11 : « pas seulement la tête »), petit, au milieu, loin
 * des bords. Tous les héros ont la MÊME échelle : la case fait 128 pixels du dessin de large (le plus large des héros,
 * arme comprise, mesuré sur ses images) plus une marge ; ses pieds sont au milieu, à 80 % de la hauteur (`--feet`).
 * Il respire (sa bande d'images défile), sans flou. Sans planche HD : son visage.
 */
export function CardFigure({ id, alt = '' }: { id: string; alt?: string }) {
  const m = (HD_FIG.chars as Record<string, readonly number[] | undefined>)[id];
  if (!m) return <img class="hcard-face" src={heroImage(id)} alt={alt} />;
  const [w, h, fx, fy, n, ms] = m as unknown as [number, number, number, number, number, number];
  let hash = 0;
  for (const ch of id) hash = (hash * 31 + ch.charCodeAt(0)) % 997;
  return (
    <span class="hcard-fig" role="img" aria-label={alt} style={{ '--w': w, '--h': h, '--fx': fx, '--fy': fy } as never}>
      <img src={figureUrl(id)} alt="" draggable={false} style={{
        width: `${n * 100}%`, animation: `px-idle ${((n * ms) / 1000).toFixed(2)}s steps(${n}) infinite`, animationDelay: `-${(((hash % n) * ms) / 1000).toFixed(2)}s`,
      }} />
    </span>
  );
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
      <CardFigure id={heroArt(d.id)} alt={d.name} />
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
        <button class="x bt-rond bt-galet" aria-label={t('back')} onClick={close}>‹</button>
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
          <button class="x bt-rond bt-feu" aria-label={t('close')} onClick={p.onClose ?? close}>✕</button>
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
