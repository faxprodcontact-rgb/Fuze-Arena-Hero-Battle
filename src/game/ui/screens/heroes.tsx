// Héros : la collection (tri dépliable), la section et l'accès à la page de fusion.
import { useState } from 'preact/hooks';
import { LEADER_SLOT } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { RARITIES, type Hero } from '../../../core/types';
import { heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { fusionPreview } from '../../state/actions';
import { canLevelUp, heroPower, teamHeroes, teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import type { PlayerState } from '../../state/types';
import { Btn, HeroCard, Icon, RedDot } from '../kit';
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
  const [view, setView] = useState<'heroes' | 'bag'>('heroes');
  return (
    <div class="screen">
      <Tabs value={view} onChange={setView} options={[['heroes', t('nav.heroes')], ['bag', t('bag.title')]]} />
      {view === 'heroes' ? <HeroList /> : <BagView />}
    </div>
  );
}

function HeroList() {
  const s = useGame();
  const [sort, setSort] = useState<Sort>('power');
  const [menu, setMenu] = useState(false);
  const inTeam = new Set(s.formation.map(([u]) => u));
  const list = sortHeroes(s, s.heroes, sort);
  const sorts: Sort[] = ['power', 'stars', 'rarity'];

  return (
    <div class="screen heroes">
      <button class="team-strip" onClick={() => prepare(null)}>
        <span class="team-faces">
          {teamHeroes(s).map(({ hero, slot }) => (
            <span class={`team-face${slot === LEADER_SLOT ? ' leader' : ''}`}><img src={heroImage(hero.defId)} alt="" /></span>
          ))}
        </span>
        <span class="team-info">
          <strong>{t('heroes.team')}</strong>
          <span class="power-chip"><Icon name="power" size={16} />{fmt(teamPower(s))}</span>
        </span>
        <span class="chev">›</span>
      </button>

      <div class="row between">
        <h2>{t('nav.heroes')} <span class="muted">{s.heroes.length}</span></h2>
        <div class="row gap-s">
          <span class="hcard-wrap">
            <Btn kind="purple" small onClick={() => open({ type: 'fusion' })}>{t('fusion.title')}</Btn>
            {s.formation.some(([u]) => !!fusionPreview(u).plan) && <RedDot />}
          </span>
          <div class="dropdown">
            <Btn kind="ghost" small onClick={() => setMenu(!menu)}>{t(`sort.${sort}`)} ▾</Btn>
            {menu && (
              <div class="dropdown-menu">
                {sorts.map((x) => (
                  <button class={x === sort ? 'on' : ''} onClick={() => { setSort(x); setMenu(false); }}>{t(`sort.${x}`)}</button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div class="grid">
        {list.map((h) => (
          <div class="hcard-wrap">
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
  );
}
