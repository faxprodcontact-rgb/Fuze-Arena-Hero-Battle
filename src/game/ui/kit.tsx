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
import { ICON_INDEX } from '../icons-meta';
import { heroArt } from '../look';
import { btClass, type BtSize, type BtTone } from './buttons';
import { artUrl } from '../art-url';
import { vectoFig } from '../vecto';
import './sections/cartes-heros.css';

// ---------- Pictos (style moderne, lisses : planche public/art/icons.webp, refonte-graphique/ui-moderne/pictos/) ----------

/** Ce picto a-t-il son dessin (public/art/icons.webp) ? */
export function hasArt(name: string): boolean {
  return name in ICON_INDEX;
}

/** Un picto dessiné, découpé dans l'image de tous les pictos ; sa taille vient de `size` ou de la classe CSS. */
export function Art({ name, size, class: cls }: { name: string; size?: number; class?: string }) {
  if (ICON_INDEX[name] === undefined) return null;
  // une petite image par picto (public/art/icons/<nom>.webp, decoupe.py) : afficher un picto en agrandissant la planche
  // entière faisait garder à Safari une copie de toute la planche par taille de picto (plantage sur iPhone, 26/11)
  return (
    <span class={`art ${cls ?? ''}`} aria-hidden="true" style={{
      ...(size ? { width: `${size}px`, height: `${size}px` } : {}),
      backgroundImage: `url(${artUrl(`art/icons/${name}.webp`)})`, backgroundRepeat: 'no-repeat', backgroundSize: '100% 100%',
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
 * Immobile, sans flou. Sans dessin : son visage.
 */
export function CardFigure({ id, alt = '' }: { id: string; alt?: string }) {
  // le dessin vectoriel lisse (la petite image, au contour plus épais, faite pour les cases) ; une seule image, immobile,
  // dessinée en fond (plantage sur iPhone le 26/11 : jamais de bande d'images animée par carte)
  const v = vectoFig(id);
  if (!v) return <img class="hcard-face" src={heroImage(id)} alt={alt} />;
  return (
    <span class="hcard-fig" role="img" aria-label={alt} style={{ '--w': v.w, '--h': v.h, '--fx': v.fx, '--fy': v.fy } as never}>
      <span class="hcard-still" style={{ backgroundImage: `url(${v.small})`, backgroundSize: '100% 100%' }} />
    </span>
  );
}

export function HeroCard(p: { hero: Hero; power?: number; onClick?: () => void; selected?: boolean; dim?: boolean; badge?: string; small?: boolean }) {
  const d = heroDef(p.hero.defId);
  const mythic = p.hero.stars >= MYTHIC_STARS;
  const color = mythic ? '#ff4d5e' : RARITY_COLOR[d.rarity];
  const Tag = p.onClick ? 'button' : 'span';
  // Chaque rareté a sa carte (sections/cartes-heros.css, demande du 26/11 : « des raretés plus spectaculaires ») :
  // Commun en pierre mate, Rare en saphir cerclé d'argent, Épique en améthyste avec une aura et un reflet qui passe,
  // Légendaire en or fondu avec des étincelles qui montent, un reflet sur le cadre et une gemme ; Mythique : en rubis.
  // `hcard-aura` porte ce qui bouge derrière le héros (Épique et plus). Chaque carte a son propre temps (--hc-t), pour
  // que les reflets d'une grille ne passent pas tous ensemble.
  const shiny = mythic || d.rarity === 'epic' || d.rarity === 'legendary';
  let hash = 7;
  for (const ch of d.id) hash = (hash * 31 + ch.charCodeAt(0)) % 1009;
  return (
    <Tag
      class={`hcard hcard-${d.rarity} el-${d.element}${mythic ? ' hcard-mythic' : ''}${p.selected ? ' hcard-on' : ''}${p.dim ? ' hcard-dim' : ''}${p.small ? ' hcard-small' : ''}`}
      style={{ '--rar': color, '--el': ELEMENT_COLOR[d.element], '--hc-t': `-${(hash % 97) / 10}s` } as never}
      onClick={p.onClick}
    >
      {shiny && <i class="hcard-aura" />}
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
