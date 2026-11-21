// Héros : la salle des héros (la section debout sur son estrade, la fusion et la Renaissance en médaillons),
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
import { Art, HeroCard, Icon, RedDot } from '../kit';
import { HeroFigure } from '../hero-figure';
import { TitleBanner } from '../title-banner';
import { open, prepare } from '../nav';
import { BagView } from './bag';
import { Tabs } from '../kit';

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

/** La salle des héros : le titre, la section debout sur l'estrade (la toucher ouvre son réglage), sa puissance, les médaillons. */
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
      <div class="hall-title"><TitleBanner title={t('nav.heroes')} ribbon={['#5a8cf0', '#2a4fb5', '#172c6e']} /></div>
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
          <span class="sum-med-icon"><RebirthIcon /></span>
          <span class="sum-med-label">{t('detail.reset')}</span>
        </button>
      </div>
    </div>
  );
}

/** Le picto de la Renaissance : deux flèches d'or qui tournent autour d'une étincelle. */
function RebirthIcon() {
  return (
    <svg class="icon" width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">
      <g fill="none" stroke="#2f1b0c" stroke-width="5.4" stroke-linecap="round"><path d="M6 13 A9.500 9.500 0 0 1 22.500 8.500" /><path d="M24 17 A9.500 9.500 0 0 1 7.500 21.500" /></g>
      <g fill="none" stroke="#ffd45c" stroke-width="3" stroke-linecap="round"><path d="M6 13 A9.500 9.500 0 0 1 22.500 8.500" /><path d="M24 17 A9.500 9.500 0 0 1 7.500 21.500" /></g>
      <path d="M25.500 3.500 L24.200 11.500 L17.600 7 Z M4.500 26.500 L5.800 18.500 L12.400 23 Z" fill="#ffd45c" stroke="#2f1b0c" stroke-width="1.200" stroke-linejoin="round" />
      <path d="M15 10.500 L16.300 13.700 L19.500 15 L16.300 16.300 L15 19.500 L13.700 16.300 L10.500 15 L13.700 13.700 Z" fill="#fff6c8" />
    </svg>
  );
}

/** Le médaillon « tous les éléments » : quatre gemmes en losange, une par élément. */
function AllElements() {
  const gem = (x: number, y: number, c: string, light: string) => (
    <g transform={`translate(${x} ${y})`}>
      <path d="M0 -6 L6 0 L0 6 L-6 0 Z" fill="#160d06" /><path d="M0 -4.600 L4.600 0 L0 4.600 L-4.600 0 Z" fill={c} /><path d="M0 -4.600 L4.600 0 H0 Z" fill={light} /><path d="M0 0 H4.600 L0 4.600 Z" fill="#000" opacity="0.2" />
    </g>
  );
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
      {gem(13, 6.500, '#ff6b3d', '#ffc0a0')}{gem(19.500, 13, '#5bd17a', '#c8f5d0')}{gem(13, 19.500, '#3da5ff', '#bfe0ff')}{gem(6.500, 13, '#c08a4a', '#f0d0a0')}
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
      <span class="chev">›</span>
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
        <button class={`el-pick${element === 'all' ? ' on' : ''}`} aria-label={t('all')} onClick={() => setElement('all')}><AllElements /></button>
        {ELEMENTS.map((e) => (
          <button class={`el-pick${element === e ? ' on' : ''}`} aria-label={t(`element.${e}`)} onClick={() => setElement(e)}><Art name={e} size={24} /></button>
        ))}
        <span class="grow" />
        <div class="dropdown">
          <button class="sort-btn" onClick={() => setMenu(!menu)}>{t(`sort.${sort}`)}<span class="sort-caret" /></button>
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
