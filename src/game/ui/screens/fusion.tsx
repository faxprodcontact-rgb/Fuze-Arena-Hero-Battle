// Fusion des héros : [héros] + [ce qu'il faut sacrifier] = [résultat].
// Ce qui manque est grisé et montre ce qu'il faut. En dessous, tous les héros, ceux qu'on peut fusionner en premier.
import { useState } from 'preact/hooks';
import { heroDef } from '../../../core/data/heroes';
import { canGainStar } from '../../../core/fusion';
import type { Faction, Hero } from '../../../core/types';
import { FACTION_COLOR, heroImage } from '../../art';
import { t } from '../../i18n';
import { fuse, fuseAllSimple, fusionNeeds, type FusionNeed } from '../../state/actions';
import { heroByUid, heroPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, HeroCard, Page, Stars } from '../kit';
import { toast } from '../nav';

function NeedSlot({ need }: { need: FusionNeed }) {
  if (need.hero) return <div class="fuse-slot"><HeroCard hero={need.hero} small /></div>;
  // Case vide : on montre ce qu'il faut, en grisé.
  return (
    <div class="fuse-slot missing" style={{ '--fac': FACTION_COLOR[need.faction as Faction] } as never}>
      {need.defId ? <img src={heroImage(need.defId)} alt="" /> : <span class="fuse-faction" />}
      <Stars stars={need.stars} />
      <span class="fuse-label">{need.defId ? heroDef(need.defId).name : t(`faction.${need.faction}`)}</span>
    </div>
  );
}

/** Part des besoins remplis (pour classer les héros : les plus proches d'une fusion d'abord). */
function progress(uid: number): number {
  const n = fusionNeeds(uid);
  if (!n) return -1;
  if (n.ready) return 2;
  return n.needs.filter((x) => x.hero).length / Math.max(1, n.needs.length);
}

export function FusionPage({ uid }: { uid?: number }) {
  const s = useGame();
  const candidates = s.heroes.filter((h) => canGainStar(h));
  const ranked = candidates
    .map((h) => ({ h, p: progress(h.uid) }))
    .sort((a, b) => b.p - a.p || b.h.stars - a.h.stars || heroPower(s, b.h) - heroPower(s, a.h));
  const [picked, setPicked] = useState<number | undefined>(uid ?? ranked[0]?.h.uid);
  const target: Hero | undefined = picked !== undefined ? heroByUid(s, picked) : undefined;
  const needs = target ? fusionNeeds(target.uid) : null;

  return (
    <Page title={t('fusion.title')}>
      {target && needs ? (
        <section class="fuse-stage">
          <div class="fuse-main">
            <div class="fuse-big"><HeroCard hero={target} /></div>
            <span class="fuse-op">=</span>
            <div class="fuse-big result"><HeroCard hero={{ ...target, stars: needs.newStars }} /></div>
          </div>
          <div class="fuse-needs">
            {needs.needs.map((n) => <><span class="fuse-plus">+</span><NeedSlot need={n} /></>)}
            {needs.crystals > 0 && (
              <><span class="fuse-plus">+</span><span class={`fuse-crystals${s.wallet.crystals >= needs.crystals ? '' : ' missing'}`}><Cur k="crystals" n={needs.crystals} /></span></>
            )}
          </div>
          <Btn kind="purple" wide disabled={!needs.ready} onClick={() => {
            if (fuse(target.uid)) toast('★');
          }}>{t('detail.fuse')}</Btn>
        </section>
      ) : <p class="center muted">{t('detail.maxStars')}</p>}

      <div class="row between">
        <strong>{t('nav.heroes')}</strong>
        <Btn kind="gold" small onClick={() => toast(t('heroes.fused', { n: fuseAllSimple() }))}>{t('heroes.fuseAll')}</Btn>
      </div>
      <div class="roster">
        {ranked.map(({ h, p }) => (
          <div class="hcard-wrap">
            <HeroCard hero={h} small selected={h.uid === picked} dim={p < 0} onClick={() => setPicked(h.uid)} />
            {p === 2 && <span class="ready-tag">★</span>}
          </div>
        ))}
      </div>
    </Page>
  );
}
