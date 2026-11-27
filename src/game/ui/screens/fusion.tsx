// Fusion des héros : [héros] → [résultat], et dessous, plus petit, ce qu'il faut sacrifier (refait le 27/11 : un autel de
// pierre grise baigné de la couleur de l'élément, à la place du fond blanc).
// Ce qui manque est grisé et montre ce qu'il faut. Toucher une case permet de choisir quel héros sacrifier.
// En dessous, tous les héros, ceux qu'on peut fusionner en premier.
import { useState } from 'preact/hooks';
import { heroDef } from '../../../core/data/heroes';
import { canGainStar } from '../../../core/fusion';
import { RARITIES, type Element, type Hero } from '../../../core/types';
import { ELEMENT_COLOR, heroImage } from '../../art';
import { t } from '../../i18n';
import { autoPicks, fuse, fuseAllSimple, fusionNeeds, fusionPool, type FusionNeed, type FusionPicks, type NeedKind } from '../../state/actions';
import { heroByUid, heroPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, HeroCard, Page, Sign, Stars } from '../kit';
import { toast } from '../nav';
import { Halo } from '../anim';

function NeedSlot({ need, on, onClick }: { need: FusionNeed; on: boolean; onClick: () => void }) {
  if (need.hero) {
    return <button class={`fuse-slot pick${on ? ' on' : ''}`} onClick={onClick}><HeroCard hero={need.hero} small /></button>;
  }
  // Case vide : on montre ce qu'il faut, en grisé.
  return (
    <button class={`fuse-slot missing${on ? ' on' : ''}`} style={{ '--fac': ELEMENT_COLOR[need.element as Element] } as never} onClick={onClick}>
      {need.defId ? <img src={heroImage(need.defId)} alt="" /> : <span class="fuse-faction" />}
      <Stars stars={need.stars} />
      <span class="fuse-label">{need.defId ? heroDef(need.defId).name : t(`element.${need.element}`)}</span>
    </button>
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
  // rangés par rareté (demande du 27/11), puis étoiles, puis les plus proches d'une fusion, puis la puissance
  const rank = (h: Hero) => RARITIES.indexOf(heroDef(h.defId).rarity);
  const ranked = candidates
    .map((h) => ({ h, p: progress(h.uid) }))
    .sort((a, b) => rank(b.h) - rank(a.h) || b.h.stars - a.h.stars || b.p - a.p || heroPower(s, b.h) - heroPower(s, a.h));
  // proposé d'office : le plus proche d'une fusion
  const closest = [...ranked].sort((a, b) => b.p - a.p)[0];
  const [picked, setPicked] = useState<number | undefined>(uid ?? closest?.h.uid);
  // Héros choisis pour être sacrifiés (proposés d'office, modifiables en touchant une case).
  const [picks, setPicks] = useState<FusionPicks | undefined>(undefined);
  const [editing, setEditing] = useState<NeedKind | undefined>(undefined);
  const target: Hero | undefined = picked !== undefined ? heroByUid(s, picked) : undefined;
  const chosen = target ? picks ?? autoPicks(target.uid) : undefined;
  const needs = target ? fusionNeeds(target.uid, chosen) : null;

  const selectTarget = (u: number) => {
    setPicked(u);
    setPicks(undefined);
    setEditing(undefined);
  };
  const max = (kind: NeedKind) => needs?.needs.filter((n) => n.kind === kind).length ?? 0;
  const toggle = (kind: NeedKind, u: number) => {
    if (!chosen) return;
    const list = needs!.needs.filter((n) => n.kind === kind && n.hero).map((n) => n.hero!.uid);
    let next = list.includes(u) ? list.filter((x) => x !== u) : [...list, u];
    if (next.length > max(kind)) next = next.slice(next.length - max(kind));
    setPicks({ ...chosen, [kind]: next });
  };
  const usedElsewhere = (kind: NeedKind) => new Set(needs?.needs.filter((n) => n.kind !== kind && n.hero).map((n) => n.hero!.uid));
  const inKind = (kind: NeedKind) => new Set(needs?.needs.filter((n) => n.kind === kind && n.hero).map((n) => n.hero!.uid));

  return (
    <Page title={t('fusion.title')}>
      {target && needs ? (
        <section class="fuse-stage fuse-altar" style={{ '--el': ELEMENT_COLOR[heroDef(target.defId).element] } as never}>
          <div class="fuse-main">
            <div class="fuse-big"><HeroCard hero={target} /></div>
            <Sign name="op-arrow" class="fuse-op" />
            <div class="fuse-big result"><Halo size={190} /><HeroCard hero={{ ...target, stars: needs.newStars }} /></div>
          </div>
          {/* ce qu'il faut donner : plus petit, dans un creux de pierre sous les deux cartes */}
          <div class="fuse-needs">
            {needs.needs.map((n) => (
              <><Sign name="op-plus" class="fuse-plus" /><NeedSlot need={n} on={editing === n.kind} onClick={() => setEditing(editing === n.kind ? undefined : n.kind)} /></>
            ))}
            {needs.crystals > 0 && (
              <><Sign name="op-plus" class="fuse-plus" /><span class={`fuse-crystals${s.wallet.crystals >= needs.crystals ? '' : ' missing'}`}><Cur k="crystals" n={needs.crystals} /></span></>
            )}
          </div>
          <Btn kind="gold" wide disabled={!needs.ready} onClick={() => {
            if (fuse(target.uid, needs.consumed)) {
              setPicks(undefined);
              setEditing(undefined);
              toast('★');
            }
          }}>{t('detail.fuse')}</Btn>
        </section>
      ) : <p class="center muted">{t('detail.maxStars')}</p>}

      {target && editing ? (
        <>
          <div class="row between center-y">
            <strong>{t('fusion.choose')} <span class="muted">{inKind(editing).size} / {max(editing)}</span></strong>
            <Btn kind="green" small onClick={() => setEditing(undefined)}>OK</Btn>
          </div>
          {fusionPool(target.uid, editing).length === 0 ? <p class="center muted">{t('fusion.none')}</p> : (
            <div class="roster fuse-roster">
              {fusionPool(target.uid, editing).map((h) => {
                const other = usedElsewhere(editing).has(h.uid);
                return (
                  <div class="hcard-wrap">
                    <HeroCard hero={h} small selected={inKind(editing).has(h.uid)} dim={other} onClick={() => !other && toggle(editing, h.uid)} />
                    {inKind(editing).has(h.uid) && <span class="ready-tag"><Sign name="check" /></span>}
                  </div>
                );
              })}
            </div>
          )}
        </>
      ) : (
        <>
          <div class="row between">
            <strong>{t('nav.heroes')}</strong>
            <Btn kind="gold" small onClick={() => toast(t('heroes.fused', { n: fuseAllSimple() }))}>{t('heroes.fuseAll')}</Btn>
          </div>
          <div class="roster fuse-roster">
            {ranked.map(({ h, p }) => (
              <div class="hcard-wrap">
                <HeroCard hero={h} small selected={h.uid === picked} dim={p < 0} onClick={() => selectTarget(h.uid)} />
                {p === 2 && <span class="ready-tag"><Sign name="star" /></span>}
              </div>
            ))}
          </div>
        </>
      )}
    </Page>
  );
}
