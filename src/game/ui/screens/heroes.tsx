// Héros : la collection (tri, filtre par faction), la section et la fusion groupée.
import { useState } from 'preact/hooks';
import { LEADER_SLOT } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { FACTIONS, RARITIES, type Faction, type Hero } from '../../../core/types';
import { FACTION_COLOR, heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { fuseAllSimple, fusionPreview } from '../../state/actions';
import { canLevelUp, heroPower, teamHeroes, teamPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import type { PlayerState } from '../../state/types';
import { Btn, HeroCard, Icon, RedDot } from '../kit';
import { open, prepare, toast } from '../nav';

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
  const [faction, setFaction] = useState<Faction | 'all'>('all');
  const [sort, setSort] = useState<Sort>('power');
  const inTeam = new Set(s.formation.map(([u]) => u));
  const list = sortHeroes(s, s.heroes.filter((h) => faction === 'all' || heroDef(h.defId).faction === faction), sort);
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
          <Btn kind="ghost" small onClick={() => setSort(sorts[(sorts.indexOf(sort) + 1) % sorts.length]!)}>⇅ {t(`sort.${sort}`)}</Btn>
          <Btn kind="gold" small onClick={() => toast(t('heroes.fused', { n: fuseAllSimple() }))}>{t('heroes.fuseAll')}</Btn>
        </div>
      </div>

      <div class="chips">
        <button class={`chip${faction === 'all' ? ' on' : ''}`} onClick={() => setFaction('all')}>{t('all')}</button>
        {FACTIONS.map((f) => (
          <button class={`chip${faction === f ? ' on' : ''}`} onClick={() => setFaction(f)}>
            <span class="chip-dot" style={{ background: FACTION_COLOR[f] }} />
            {t(`faction.${f}`)}
          </button>
        ))}
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
            {inTeam.has(h.uid) && (canLevelUp(s, h) || !!fusionPreview(h.uid).plan) && <RedDot />}
          </div>
        ))}
      </div>
    </div>
  );
}
