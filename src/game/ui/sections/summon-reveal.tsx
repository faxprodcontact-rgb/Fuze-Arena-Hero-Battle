// Le tirage (refait de zéro le 26/11/2026, demande du propriétaire : « qu'ils n'arrivent plus en mode carte, mais en
// mode héros invoqué ; refais les animations de zéro, le portail aussi »). Repris le 27/11 : le portail arrive d'abord et
// s'installe au premier plan (0), le tirage ne commence qu'ensuite ; tout est un peu plus lent, et plus spectaculaire
// selon la rareté (Commun sobre ; Rare un éclat ; Épique plus long, la couleur monte ; Légendaire : montée en tension,
// l'écran s'assombrit, le sol gronde, un éclair frappe, une onde, des étincelles d'or et de son élément, sortie lente).
// Le portail (le même que dans l'onglet) est posé sur l'estrade ; les héros sortent du tourbillon et se posent devant lui.
// 0. Le portail s'avance depuis l'onglet, se pose (une onde de poussière à ses pieds) et reste calme un instant.
// 1. Le portail se charge : des grains de lumière filent vers lui en spirale, et sa couleur monte d'un cran par rareté
//    gagnée (argent, bleu, violet, or) : on devine ce qui arrive avant de le voir.
// 2. Il éclate : un éclair, une onde, des grains projetés en courbes ; pour un ×10, dix perles de la couleur de chaque
//    héros filent vers la rangée du haut.
// 3. Chaque héros sort du portail : une colonne de lumière descend sur l'estrade, sa silhouette de lumière grandit, puis
//    le vrai héros (son dessin vectoriel, public/art/vecto/<id>.webp) apparaît et respire, entouré d'une aura de sa rareté (Épique : deux croissants
//    qui tournent ; Légendaire : un temps d'attente doré, l'écran tremble, une pluie d'étincelles d'or).
//    Dessous : rareté, élément, rôle, nom, étoiles, et « Nouveau ! » ou le nombre d'exemplaires possédés.
// 4. ×10 : les héros sortent l'un après l'autre (du moins rare au plus rare), puis un récapitulatif : les dix héros en
//    pied sur de petites dalles, du plus rare au moins rare ; en toucher un le montre en grand.
// Toucher l'écran passe à la suite ; le bouton du haut passe directement au récapitulatif. Les règles ne changent pas :
// les héros viennent de actions.ts (summon), le tirage est déjà fait quand cet écran s'ouvre.
import { useEffect, useLayoutEffect, useRef, useState } from 'preact/hooks';
import { heroDef } from '../../../core/data/heroes';
import { RARITIES, type Hero, type Rarity } from '../../../core/types';
import { FEATURED_BANNER, type SummonKind } from '../../../core/data/summon';
import { ELEMENT_COLOR, RARITY_COLOR } from '../../art';
import { t } from '../../i18n';
import { newlyFound, summon, summonCost } from '../../state/actions';
import { useGame } from '../../state/store';
import { HeroFigure } from '../hero-figure';
import { Cur, Icon, Stars } from '../kit';
import { btClass } from '../buttons';
import { close } from '../nav';
import { Dais, GATE_VIEW, Gate } from './summon-gate';
import { SummonFx } from './summon-fx';
import './invoquer.css';

type Kind = SummonKind;

/** La dernière invocation lancée depuis l'onglet (pour « encore une fois ») ; rien pour les fragments ou la pub. */
let lastCast: { kind: Kind; count: 1 | 10 } | null = null;
export function rememberCast(c: { kind: Kind; count: 1 | 10 } | null): void { lastCast = c; }

/** Les couleurs du portail et des grains : [principale, claire, profonde] ; une par portail (sa lumière au repos : bleu
 * calme pour le simple, violet et or pour le normal, celle du groupe mis en avant pour le spécial), puis une par rareté. */
const TONES: Record<Kind | Rarity, readonly [string, string, string]> = {
  normal: ['#9b5cff', '#ffd36a', '#2a145e'],
  basic: ['#3b95ff', '#a9f3ff', '#12306b'],
  featured: FEATURED_BANNER.tone,
  common: ['#b9c2da', '#ffffff', '#3a3f5c'],
  rare: ['#2f8cff', '#8fe0ff', '#0f2f72'],
  epic: ['#a35cff', '#f0a8ff', '#35107a'],
  legendary: ['#ffb21f', '#fff0a0', '#7a3a00'],
};
const toneVars = (k: Kind | Rarity) => ({ '--g-a': TONES[k][0], '--g-b': TONES[k][1], '--g-deep': TONES[k][2] });
/** Les couleurs d'un portail au repos (posées sur l'onglet, screens/summon.tsx). */
export const kindTone = (k: Kind) => toneVars(k);

/** Le rythme (ms). Le portail arrive et se pose (ARRIVE) avant tout ; la charge dure plus longtemps pour une belle rareté. */
const ARRIVE = 1050;
const CHARGE = [1000, 1350, 1800, 2400];
/** L'attente avant que le héros sorte : un Épique fait monter sa couleur, un Légendaire la tension (puis l'éclair). */
const PRE = [0, 0, 420, 1450];
/** Le moment où la silhouette de lumière devient le héros (après PRE) ; un Légendaire sort lentement, en majesté. */
const MAT = [340, 440, 660, 900];
/** Combien de temps un héros reste seul à l'écran avant le suivant (×10), selon sa rareté (PRE compris). */
const DWELL = [1350, 1650, 2500, 4300];

const rankOf = (h: Hero) => RARITIES.indexOf(heroDef(h.defId).rarity);

/** Secoue un élément (plus fort pour une rareté plus haute). */
function shake(el: HTMLElement | null, level: number) {
  if (!el?.animate) return;
  const a = 2 + level * 2.5;
  el.animate([
    { transform: 'translate(0, 0)' }, { transform: `translate(${-a}px, ${a * 0.6}px)` }, { transform: `translate(${a}px, ${-a * 0.5}px)` },
    { transform: `translate(${-a * 0.5}px, ${a * 0.3}px)` }, { transform: 'translate(0, 0)' },
  ], { duration: 240 + level * 80, easing: 'ease-out' });
}

/** Un petit dessin à deux chevrons (passer), sans lettre. */
function SkipGlyph() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      <path d="M4.5 5.5 Q4.5 4 6 4.8 L12.5 10.6 Q13.6 12 12.5 13.4 L6 19.2 Q4.5 20 4.5 18.5 Z" fill="currentColor" />
      <path d="M12 5.5 Q12 4 13.5 4.8 L20 10.6 Q21.1 12 20 13.4 L13.5 19.2 Q12 20 12 18.5 Z" fill="currentColor" opacity="0.75" />
    </svg>
  );
}

/** Un héros sur l'estrade (devant le portail) : la colonne de lumière, son aura, sa silhouette de lumière puis lui. */
function HeroShow({ hero, instant }: { hero: Hero; instant?: boolean }) {
  const d = heroDef(hero.defId);
  const r = RARITIES.indexOf(d.rarity);
  return (
    <div class={`sr-show sr-r${r}${instant ? ' sr-instant' : ''}`}
      style={{ '--rar': RARITY_COLOR[d.rarity], '--el': ELEMENT_COLOR[d.element], '--pre': `${instant ? 0 : PRE[r]}ms`, '--mat': `${instant ? 0 : MAT[r]}ms`, ...toneVars(d.rarity) } as never}>
      {r === 3 && !instant && <><span class="sr-strike" /><LegendBolt /></>}
      {r >= 1 && !instant && <span class="sr-ring" />}
      <span class="sr-beam" />
      <span class="sr-aura" />
      {r >= 2 && (
        <svg class="sr-halo" viewBox="-100 -100 200 200" aria-hidden="true">
          <g class="sr-halo-spin"><circle r="95" fill="none" />
            <path d="M-86 0 A86 86 0 0 1 40 -76" fill="none" style={{ stroke: 'var(--rar)' }} stroke-width="5" stroke-linecap="round" />
            <path d="M86 0 A86 86 0 0 1 -40 76" fill="none" style={{ stroke: 'var(--rar)' }} stroke-width="5" stroke-linecap="round" />
            <path d="M-80 -20 A82 82 0 0 1 10 -81" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity="0.8" />
            {r === 3 && <path d="M70 40 A82 82 0 0 1 -20 79" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity="0.8" />}
          </g>
        </svg>
      )}
      <div class="sr-hero">
        <HeroFigure defId={hero.defId} class="sr-real" />
        {!instant && <HeroFigure defId={hero.defId} class="sr-ghost" />}
      </div>
      {r === 3 && !instant && <span class="sr-wave" />}
    </div>
  );
}

/** L'éclair du Légendaire : une ligne courbe (jamais droite) qui tombe du haut de l'écran sur l'estrade, deux branches. */
function LegendBolt() {
  // repère 100 × 300 étiré sur la hauteur de la scène ; l'épaisseur des traits ne s'étire pas (non-scaling-stroke)
  const main = 'M58 -4 Q44 30 56 52 T46 104 Q60 128 50 150 T56 204 Q44 232 52 258 T50 300';
  const br1 = 'M53 96 Q70 110 66 128 T80 160';
  const br2 = 'M51 182 Q36 196 40 214 T28 236';
  const line = (d: string, w: number, c: string, o = 1) => <path d={d} fill="none" stroke={c} stroke-width={w} stroke-linecap="round" stroke-linejoin="round" opacity={o} vector-effect="non-scaling-stroke" />;
  return (
    <svg class="sr-bolt" viewBox="0 0 100 300" preserveAspectRatio="none" aria-hidden="true">
      {[main, br1, br2].map((d, i) => <g opacity={i ? 0.8 : 1}>{line(d, i ? 9 : 16, 'var(--el)', 0.35)}{line(d, i ? 4 : 7, '#ffd34a')}{line(d, i ? 1.6 : 2.8, '#fff')}</g>)}
    </svg>
  );
}

/** Ce qu'on lit sous le héros : rareté, élément, rôle, nom, étoiles, nouveau ou nombre d'exemplaires. */
function HeroInfo({ hero, instant }: { hero: Hero; instant?: boolean }) {
  const s = useGame();
  const d = heroDef(hero.defId);
  const r = RARITIES.indexOf(d.rarity);
  const owned = s.heroes.filter((h) => h.defId === hero.defId).length;
  return (
    <div class={`sr-info sr-r${r}${instant ? ' sr-instant' : ''}`} style={{ '--rar': RARITY_COLOR[d.rarity], '--pre': `${instant ? 0 : PRE[r]}ms`, '--mat': `${instant ? 0 : MAT[r]}ms` } as never}>
      <div class="sr-tags">
        <span class="sr-rarity">{t(`rarity.${d.rarity}`)}</span>
        <span class="sr-chip"><Icon name={d.element} size={20} /></span>
        <span class="sr-chip"><Icon name={d.role} size={20} /></span>
      </div>
      <div class="sr-name">{d.name}</div>
      <div class="sr-sub">
        <Stars stars={hero.stars} />
        {newlyFound.has(hero.uid)
          ? <span class="sr-new">{t('new')} !</span>
          : <span class="sr-dup"><Icon name="copy" size={16} />×{owned}</span>}
      </div>
    </div>
  );
}

function Reveal({ heroes, onAgain }: { heroes: Hero[]; onAgain: (h: Hero[]) => void }) {
  const s = useGame();
  const one = heroes.length === 1;
  // l'ordre de sortie : du moins rare au plus rare (le meilleur en dernier) ; le récapitulatif : l'inverse
  const order = heroes.map((h, i) => ({ h, i, r: rankOf(h) })).sort((a, b) => a.r - b.r || a.i - b.i).map((x) => x.h);
  const recap = [...order].reverse();
  const best = rankOf(order[order.length - 1]!);
  const base: Kind = lastCast?.kind ?? 'normal';

  const [phase, setPhase] = useState<'arrive' | 'charge' | 'show' | 'recap'>('arrive');
  /** Le Légendaire se fait attendre : la tension (écran sombre, portail qui s'emballe, le sol qui gronde). */
  const [tense, setTense] = useState(false);
  const [idx, setIdx] = useState(0);
  const [tease, setTease] = useState(-1);
  const [ready, setReady] = useState(false);
  const [focus, setFocus] = useState<number | null>(null);
  const root = useRef<HTMLDivElement>(null);
  const stage = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const fx = useRef<SummonFx | null>(null);

  useEffect(() => {
    if (!canvas.current) return;
    const f = new SummonFx(canvas.current);
    fx.current = f;
    const onResize = () => f.resize();
    addEventListener('resize', onResize);
    return () => { removeEventListener('resize', onResize); f.destroy(); fx.current = null; };
  }, []);

  // La taille du héros sur l'estrade : environ 75 % de l'ancienne taille, arrondie au plus proche pour qu'un pixel du dessin couvre un nombre
  // entier de pixels de l'écran (il reste net). Boîte 200 × 240, 1,75 unité par pixel du dessin (hero-figure.tsx).
  useLayoutEffect(() => {
    const st = stage.current;
    if (!st) return;
    const fit = () => {
      const dpr = window.devicePixelRatio || 1;
      const h = Math.min(st.clientHeight * 0.48, st.clientWidth * 0.72);
      const perArt = (h * (200 / 240)) / 200 * 1.75; // pixels de l'écran (CSS) par pixel du dessin
      const snapped = Math.max(1, Math.round(perArt * dpr)) / dpr;
      st.style.setProperty('--hero-px', `${((snapped * 240) / 1.75).toFixed(2)}px`);
    };
    fit();
    const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(fit) : null;
    ro?.observe(st);
    return () => ro?.disconnect();
  }, []);

  /** Un point d'un élément, dans le repère du canvas. */
  const where = (sel: string): DOMRect | null => {
    const el = root.current?.querySelector(sel), c = canvas.current?.getBoundingClientRect();
    if (!el || !c) return null;
    const b = el.getBoundingClientRect();
    return new DOMRect(b.left - c.left, b.top - c.top, b.width, b.height);
  };
  // le centre de l'anneau (le portail est posé sur l'estrade : sa boîte descend jusqu'au sol, sous l'anneau)
  const gateCenter = () => {
    const g = where('.sr-gate');
    return g ? { x: g.x + g.width / 2, y: g.y + (g.height * GATE_VIEW.cy) / GATE_VIEW.h, r: (g.width * GATE_VIEW.ring) / GATE_VIEW.w } : null;
  };

  // 0. le portail arrive et se pose au premier plan ; rien d'autre ne bouge tant qu'il n'est pas installé
  useEffect(() => {
    if (phase !== 'arrive') return;
    const id = window.setTimeout(() => setPhase('charge'), ARRIVE);
    return () => clearTimeout(id);
  }, [phase]);

  // 1. la charge : les grains aspirés, la couleur qui monte d'un cran par rareté gagnée
  useEffect(() => {
    if (phase !== 'charge') return;
    const total = CHARGE[best]!;
    const g = gateCenter();
    const extra = base === 'featured' ? FEATURED_BANNER.sparks : [];
    if (g) fx.current?.charge(g.x, g.y, g.r * 1.5, [TONES[base][0], TONES[base][1], '#ffffff', ...extra], total - 120);
    const ids: number[] = [];
    for (let k = 0; k <= best; k++) {
      ids.push(window.setTimeout(() => {
        setTease(k);
        const gate = root.current?.querySelector<HTMLElement>('.sr-gate .sg-hole');
        gate?.animate?.([{ scale: '1' }, { scale: `${1.08 + k * 0.05}` }, { scale: '1' }], { duration: 420 + k * 60, easing: 'cubic-bezier(.2,1.6,.4,1)' });
        if (k > 0) shake(stage.current, k - 1);
      }, total * (0.18 + (0.62 * k) / Math.max(1, best))));
    }
    ids.push(window.setTimeout(() => burstNow(), total));
    return () => ids.forEach(clearTimeout);
  }, [phase]);

  const burstNow = () => {
    const g = gateCenter();
    const c = TONES[RARITIES[best]!];
    fx.current?.clear();
    if (g) fx.current?.burst(g.x, g.y, [c[0], c[1], '#ffffff'], 70 + best * 30, 480 + best * 90);
    shake(stage.current, Math.min(best, 2));
    setTease(best);
    setPhase('show');
  };

  // 2. un héros sort : grains rassemblés dans sa silhouette, puis (×10) le suivant au bout d'un moment.
  //    Rare : un éclat de grains, une onde bleue sur l'estrade. Épique : la couleur monte (PRE), un éclat plus grand, la
  //    scène vibre. Légendaire : la tension (PRE : l'écran s'assombrit, le portail s'emballe, le sol gronde de plus en
  //    plus fort, des grains d'or et de son élément aspirés), l'éclair, l'onde, puis le héros sort lentement, en majesté,
  //    sous une pluie d'étincelles d'or et de son élément.
  useEffect(() => {
    if (phase !== 'show') return;
    const h = order[idx]!;
    const d = heroDef(h.defId);
    const r = rankOf(h);
    const c = TONES[RARITIES[r]!];
    const el = ELEMENT_COLOR[d.element];
    const pre = PRE[r]!, mat = MAT[r]!;
    const ids: number[] = [];
    const later = (ms: number, fn: () => void) => ids.push(window.setTimeout(fn, ms));
    const W = root.current?.clientWidth ?? 390, H = root.current?.clientHeight ?? 700;
    if (r === 3) {
      setTense(true);
      const g = gateCenter();
      if (g) fx.current?.charge(g.x, g.y, g.r * 1.8, ['#ffd34a', '#fff0a0', el, '#ffffff'], pre - 200);
      [0, 380, 700, 960, 1180].forEach((ms, k) => later(ms, () => shake(stage.current, Math.min(2, k * 0.5))));
      // l'éclair tombe juste avant la sortie : l'écran se rallume d'un coup
      later(pre - 140, () => { setTense(false); shake(root.current, 3); });
    }
    later(pre + 40, () => {
      const box = where('.sr-show .sr-real');
      if (box) fx.current?.converge(box.x, box.y, box.width, box.height, r === 3 ? el : c[0], 24 + r * 14);
    });
    if (r === 3) later(pre, () => {
      const g = gateCenter();
      if (g) fx.current?.burst(g.x, g.y, ['#ffd34a', '#fff0a0', el, '#ffffff'], 120, 760);
    });
    later(pre + mat, () => {
      const box = where('.sr-show .sr-real'), dais = where('.sr-show .sr-dais');
      if (dais) fx.current?.motes(dais.x + dais.width / 2, dais.y + dais.height * 0.3, dais.width * 0.5, r === 3 ? el : c[1], one ? 60000 : DWELL[r]! - pre - mat, 8 + r * 5);
      if (r >= 1 && box) {
        const cols = r === 3 ? ['#ffd34a', el, '#fff0a0', '#ffffff'] : [c[0], c[1], '#ffffff'];
        fx.current?.burst(box.x + box.width / 2, box.y + box.height * 0.45, cols, [0, 26, 48, 96][r]!, [0, 340, 460, 680][r]!);
      }
      if (r === 2) shake(stage.current, 1);
      if (r === 3) {
        shake(stage.current, 2);
        const left = one ? 5200 : DWELL[3]! - pre - mat;
        fx.current?.rain(W, H, '#ffd34a', left);
        fx.current?.rain(W, H, el, left * 0.7);
      }
    });
    if (one) later(pre + mat + 420, () => setReady(true));
    else later(DWELL[r]!, () => next());
    return () => { ids.forEach(clearTimeout); setTense(false); };
  }, [phase, idx]);

  const next = () => {
    if (idx < order.length - 1) setIdx(idx + 1);
    else toRecap();
  };
  const toRecap = () => { fx.current?.clear(); setPhase('recap'); setReady(true); };

  // les perles qui filent du portail vers la rangée du haut (×10) : leur trajet, mesuré une fois posé
  useLayoutEffect(() => {
    if (one || phase !== 'show' || idx !== 0) return;
    const g = gateCenter();
    root.current?.querySelectorAll<HTMLElement>('.sr-pip').forEach((p, i) => {
      const orb = root.current?.querySelector<HTMLElement>(`.sr-orb-${i}`);
      const b = where(`.sr-pip-${i}`);
      if (!orb || !b || !g) return;
      orb.style.left = `${g.x}px`; orb.style.top = `${g.y}px`;
      orb.style.setProperty('--dx', `${b.x + b.width / 2 - g.x}px`);
      orb.style.setProperty('--dy', `${b.y + b.height / 2 - g.y}px`);
      void p;
    });
  }, [phase]);

  const tap = () => {
    if (focus !== null) { setFocus(null); return; }
    if (phase === 'arrive' || phase === 'charge') burstNow();
    else if (phase === 'show') {
      if (one) { if (!ready) { fx.current?.clear(); setReady(true); } }
      else next();
    }
  };
  const skip = (e: Event) => { e.stopPropagation(); setTense(false); toRecap(); };

  const again = (e: Event) => {
    e.stopPropagation();
    if (!lastCast) return;
    const h = summon(lastCast.kind, lastCast.count);
    if (h) onAgain(h);
  };
  const cost = lastCast && lastCast.count === heroes.length ? summonCost(lastCast.kind, lastCast.count) : null;

  const shown = phase === 'show' ? order[idx]! : null;
  const focused = focus !== null ? recap.find((h) => h.uid === focus) ?? null : null;
  const tone: Kind | Rarity = phase === 'arrive' || phase === 'charge' ? (tease < 0 ? base : RARITIES[tease]!) : shown ? heroDef(shown.defId).rarity : focused ? heroDef(focused.defId).rarity : RARITIES[best]!;
  return (
    <div ref={root} class={`sr-screen sr-p-${phase}${one ? ' sr-one' : ' sr-many'}${ready ? ' sr-ready' : ''}${focused ? ' sr-focus' : ''}${tense ? ' sr-tense' : ''}`}
      style={toneVars(tone) as never} onClick={tap}>
      <h2 class="sr-only">{t('summon.normal')}</h2>
      <div class="sr-top">
        {!one && (
          <div class="sr-pips">
            {order.map((h, i) => (
              <span class={`sr-pip sr-pip-${i}${phase === 'recap' || (phase === 'show' && i <= idx) ? ' seen' : ''}${phase !== 'charge' ? ' got' : ''}`}
                style={{ '--rar': RARITY_COLOR[heroDef(h.defId).rarity], '--d': `${300 + i * 55}ms` } as never} />
            ))}
          </div>
        )}
        {!one && phase !== 'recap' && <button class={`sr-skip ${btClass('galet', 's')}`} aria-label="skip" onClick={skip}><SkipGlyph /></button>}
      </div>

      <div class="sr-stage" ref={stage}>
        {/* le portail, posé sur l'estrade : les héros en sortent et se posent devant lui */}
        <Gate uid="rv" charging={phase === 'charge' || tense} open={phase === 'show' || phase === 'recap'} class="sr-gate" />
        <Dais uid="rv" class="sr-dais" />
        {phase === 'arrive' && <span class="sr-land" />}
        {phase === 'charge' && <span class="sr-charge-ring" />}
        {phase === 'show' && shown && <HeroShow hero={shown} key={`s${idx}`} />}
        {phase === 'recap' && !focused && (
          <div class="sr-recap">
            {recap.map((h, i) => {
              const d = heroDef(h.defId);
              return (
                <button class={`sr-cell sr-r${RARITIES.indexOf(d.rarity)}`} style={{ '--rar': RARITY_COLOR[d.rarity], '--d': `${i * 45}ms` } as never}
                  onClick={(e) => { e.stopPropagation(); setFocus(h.uid); }}>
                  <span class="sr-cell-fig">
                    <span class="sr-cell-glow" />
                    <span class="sr-cell-plinth" />
                    <HeroFigure defId={h.defId} />
                    {newlyFound.has(h.uid) && <span class="sr-cell-new">{t('new')}</span>}
                  </span>
                  <span class="sr-cell-name">{d.name}</span>
                </button>
              );
            })}
          </div>
        )}
        {focused && <HeroShow hero={focused} instant key={`f${focused.uid}`} />}
        {phase === 'show' && idx === 0 && !one && order.map((h, i) => (
          <span class={`sr-orb sr-orb-${i}`} style={{ '--rar': RARITY_COLOR[heroDef(h.defId).rarity], '--d': `${i * 55}ms` } as never} />
        ))}
      </div>

      <div class="sr-info-slot">
        {phase === 'show' && shown && <HeroInfo hero={shown} key={`i${idx}`} />}
        {focused && <HeroInfo hero={focused} instant key={`fi${focused.uid}`} />}
      </div>

      <div class="sr-bar">
        {cost && !focused && (
          <button class={`sr-btn sr-again ${btClass('arcane', 'l')}`} disabled={s.wallet[cost.currency] < cost.amount} onClick={again}>
            <span class="sr-btn-n">{t(`summon.x${heroes.length}`)}</span>
            <Cur k={cost.currency} n={cost.amount} />
          </button>
        )}
        <button class={`sr-btn sr-ok reveal-ok ${btClass('basalte', 'l')}`} onClick={(e) => { e.stopPropagation(); if (focused) setFocus(null); else close(); }}>
          <span class="sr-btn-n">{t('ok')}</span>
        </button>
      </div>
      <span class="sr-dim" />
      <span class="sr-flash" key={`fl${phase === 'arrive' || phase === 'charge' ? 0 : 1}`} />
      <canvas class="sr-fx" ref={canvas} />
    </div>
  );
}

/** La fenêtre du tirage (ouverte par open({ type: 'summon', heroes })) ; « encore » relance tout avec les nouveaux héros. */
export function SummonResult({ heroes }: { heroes: Hero[] }) {
  const [state, setState] = useState({ heroes, run: 0 });
  return <Reveal key={state.run} heroes={state.heroes} onAgain={(h) => setState({ heroes: h, run: state.run + 1 })} />;
}
