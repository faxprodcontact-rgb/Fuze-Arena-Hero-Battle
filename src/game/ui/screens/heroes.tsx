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

/** Où se tient chaque héros sur l'estrade (en % de la largeur de la salle) : le chef devant, au centre ; les autres en arc. */
const SPOTS = [
  { x: 50, y: 88.5, w: 23 }, { x: 34.2, y: 84.2, w: 20.8 }, { x: 65.8, y: 84.2, w: 20.8 }, { x: 19.6, y: 80.2, w: 19 }, { x: 80.4, y: 80.2, w: 19 },
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
          <span class="hall-hero" style={{ left: `${spot.x}%`, top: `${spot.y}%`, width: `${spot.w}%`, animationDelay: `${-i * 0.7}s` }}>
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

/** Le médaillon « tous les éléments » : un disque à quatre quartiers, un par élément. */
function AllElements() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="10.500" fill="#160d06" />
      <path d="M12 12 V2.500 A9.500 9.500 0 0 1 21.500 12 Z" fill="#5bd17a" /><path d="M12 12 H21.500 A9.500 9.500 0 0 1 12 21.500 Z" fill="#c08a4a" />
      <path d="M12 12 V21.500 A9.500 9.500 0 0 1 2.500 12 Z" fill="#3da5ff" /><path d="M12 12 H2.500 A9.500 9.500 0 0 1 12 2.500 Z" fill="#ff6b3d" />
      <path d="M12 2.500 V21.500 M2.500 12 H21.500" stroke="#160d06" stroke-width="1.400" /><circle cx="12" cy="12" r="3" fill="#fff6c8" stroke="#160d06" stroke-width="1.200" />
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
