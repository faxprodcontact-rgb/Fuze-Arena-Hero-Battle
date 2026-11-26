// Héros : la salle des héros (la section debout sur son estrade, le bouton Formation au-dessus, la fusion et la
// Renaissance en médaillons),
// puis la collection : filtre par élément, tri dépliable, les cases.
import { useState } from 'preact/hooks';
import { LEADER_SLOT } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { ELEMENTS, RARITIES, type Element, type Hero } from '../../../core/types';
import { heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { fusionPreview } from '../../state/actions';
import { canLevelUp, heroPower, teamHeroes, teamPower, type TeamKind } from '../../state/selectors';
import { useGame } from '../../state/store';
import type { PlayerState } from '../../state/types';
import { Art, HeroCard, Icon, RedDot, Sign } from '../kit';
import { ELEMENT_TONE, btClass } from '../buttons';
import { HeroFigure } from '../hero-figure';
import { open, prepare } from '../nav';
import { BagView } from './bag';
import { Tabs } from '../kit';
import '../sections/heros.css';

type Sort = 'power' | 'stars' | 'rarity';

function sortHeroes(s: PlayerState, list: Hero[], sort: Sort): Hero[] {
  const rarity = (h: Hero) => RARITIES.indexOf(heroDef(h.defId).rarity);
  return [...list].sort((a, b) => {
    if (sort === 'stars') return b.stars - a.stars || heroPower(s, b) - heroPower(s, a);
    if (sort === 'rarity') return rarity(b) - rarity(a) || b.stars - a.stars;
    return heroPower(s, b) - heroPower(s, a);
  });
}

export function HeroesScreen() {
  const s = useGame();
  const [view, setView] = useState<'heroes' | 'bag'>('heroes');
  return (
    <div class="screen heroes-tab">
      <Hall />
      <Tabs value={view} onChange={setView} options={[['heroes', `${t('nav.heroes')} ${s.heroes.length}`], ['bag', t('bag.title')]]} />
      {view === 'heroes' ? <HeroList /> : <div class="hall-scroll"><BagView /></div>}
    </div>
  );
}

/** Où se tient chaque héros sur l'estrade (en % de la salle) : deux devant (le chef à gauche), trois derrière, plus petits. */
const SPOTS = [
  { x: 36.5, y: 89, w: 23.5, back: false }, { x: 63.5, y: 89, w: 23.5, back: false },
  { x: 50, y: 80.6, w: 19.5, back: true }, { x: 23.5, y: 81.2, w: 19.5, back: true }, { x: 76.5, y: 81.2, w: 19.5, back: true },
];

/** La salle des héros : le bouton Formation, la section debout sur l'estrade (la toucher ouvre son réglage), sa puissance, les médaillons. */
function Hall() {
  const s = useGame();
  const team = teamHeroes(s);
  // le chef au centre, puis les autres de part et d'autre, dans l'ordre de leur place
  const lead = team.find((x) => x.slot === LEADER_SLOT) ?? team[0];
  const rest = team.filter((x) => x !== lead).sort((a, b) => a.slot - b.slot);
  const placed = [lead, ...rest].filter((x): x is NonNullable<typeof x> => !!x);
  // on dessine d'abord ceux du fond, pour que ceux de devant passent par-dessus
  const order = placed.map((x, i) => ({ ...x, spot: SPOTS[i]! })).reverse();
  return (
    <div class="hall">
      <div class="hall-cta">
        <button class={`hall-formation ${btClass('basalte', 'l')}`} onClick={() => prepare(null, 'main')}>
          <FormationSign />{t('heroes.formation')}
        </button>
      </div>
      <button class="hall-team" aria-label={t('heroes.team')} onClick={() => prepare(null, 'main')}>
        {order.map(({ hero, spot }, i) => (
          <span class={`hall-hero${spot.back ? ' hall-back' : ''}`} style={{ left: `${spot.x}%`, top: `${spot.y}%`, width: `${spot.w}%`, animationDelay: `${-i * 0.7}s` }}>
            <HeroFigure defId={hero.defId} />
          </span>
        ))}
        <span class="hall-power"><Icon name="power" size={17} />{fmt(teamPower(s))}</span>
      </button>
      <div class="sum-side sum-left">
        <button class="sum-med hall-med" onClick={() => open({ type: 'fusion' })}>
          <span class="sum-med-icon"><Icon name="fusion" size={30} /></span>
          <span class="sum-med-label">{t('fusion.title')}</span>
          {s.formation.some(([u]) => !!fusionPreview(u).plan) && <span class="dot" />}
        </button>
      </div>
      <div class="sum-side sum-right">
        <button class="sum-med hall-med" onClick={() => open({ type: 'reset' })}>
          <span class="sum-med-icon"><Icon name="rebirth" size={30} /></span>
          <span class="sum-med-label">{t('detail.reset')}</span>
        </button>
      </div>
    </div>
  );
}

/**
 * Le signe de la formation (inventé) : les cinq dalles des postes vues d'un peu au-dessus, comme sur le terrain
 * (deux à l'arrière, le chef au milieu, deux à l'avant) et un chevron vers les ennemis ; il luit de l'or du basalte.
 */
function FormationSign() {
  const tile = (x: number, y: number, lead = false) => (
    <g>
      <rect x={x - 5.5} y={y - 1.6} width="11" height="6.4" rx="3.2" fill="#6a3000" opacity="0.6" />
      <rect x={x - 5.5} y={y - 3.4} width="11" height="6.4" rx="3.2" fill={lead ? '#fff1b8' : '#ffc95a'} />
      <rect x={x - 3.6} y={y - 2.6} width="7.2" height="1.8" rx="0.9" fill="#fffbe6" opacity={lead ? 0.95 : 0.6} />
    </g>
  );
  return (
    <svg class="fm-sign" viewBox="0 0 42 32" aria-hidden="true">
      {tile(7, 12)}{tile(7, 27)}{tile(35, 12)}{tile(35, 27)}{tile(21, 20, true)}
      {/* la couronne du chef, au-dessus de sa dalle */}
      <path d="M16 15 L15.4 8.6 L18.6 11.2 L21 6.6 L23.4 11.2 L26.6 8.6 L26 15 Z" fill="#ffd23a" stroke="#6a3000" stroke-opacity="0.55" stroke-width="0.9" stroke-linejoin="round" />
    </svg>
  );
}

/** Bandeau « Section » : les visages, la puissance ; toucher pour changer la section. */
export function TeamStrip({ team = 'main' }: { team?: TeamKind } = {}) {
  const s = useGame();
  return (
    <button class={`team-strip${team === 'defense' ? ' defense' : ''}`} onClick={() => prepare(null, team)}>
      <span class="team-faces">
        {teamHeroes(s, team).map(({ hero, slot }) => (
          <span class={`team-face${slot === LEADER_SLOT ? ' leader' : ''}`}><img src={heroImage(hero.defId)} alt="" /></span>
        ))}
      </span>
      <span class="team-info">
        <strong>{team === 'defense' ? t('war.defense') : t('heroes.team')}</strong>
        <span class="power-chip"><Icon name="power" size={16} />{fmt(teamPower(s, team))}</span>
      </span>
      <Sign name="chev-s" class="chev" />
    </button>
  );
}

function HeroList() {
  const s = useGame();
  const [sort, setSort] = useState<Sort>('power');
  const [element, setElement] = useState<Element | 'all'>('all');
  const [menu, setMenu] = useState(false);
  const inTeam = new Set(s.formation.map(([u]) => u));
  const list = sortHeroes(s, s.heroes.filter((h) => element === 'all' || heroDef(h.defId).element === element), sort);
  const sorts: Sort[] = ['power', 'stars', 'rarity'];

  return (
    <div class="screen heroes">
      <div class="hero-filters">
        <button class={`el-pick bt-rond ${element === 'all' ? 'on bt-basalte' : 'bt-galet'}`} aria-label={t('all')} onClick={() => setElement('all')}><Art name="allElements" size={24} /></button>
        {ELEMENTS.map((e) => (
          <button class={`el-pick bt-rond ${element === e ? `on bt-${ELEMENT_TONE[e]}` : 'bt-galet'}`} aria-label={t(`element.${e}`)} onClick={() => setElement(e)}><Art name={e} size={24} /></button>
        ))}
        <span class="grow" />
        <div class="dropdown">
          <button class={`sort-btn ${btClass('galet', 's')}`} onClick={() => setMenu(!menu)}>{t(`sort.${sort}`)}<span class="sort-caret" /></button>
          {menu && (
            <div class="dropdown-menu">
              {sorts.map((x) => (
                <button class={x === sort ? 'on' : ''} onClick={() => { setSort(x); setMenu(false); }}>{t(`sort.${x}`)}</button>
              ))}
            </div>
          )}
        </div>
      </div>
      <div class="hall-scroll">
        <div class="grid">
          {list.map((h) => (
            <div class="hcard-wrap" key={h.uid}>
              <HeroCard
                hero={h}
                power={heroPower(s, h)}
                selected={inTeam.has(h.uid)}
                onClick={() => open({ type: 'hero', uid: h.uid })}
              />
              {inTeam.has(h.uid) && canLevelUp(s, h) && <RedDot />}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
