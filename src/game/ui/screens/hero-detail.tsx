// La page d'un héros, en plein écran. En haut, sa case : il s'y tient sur son piédestal, dans le décor de son élément
// (hero-scene.tsx), à taille modeste (les dessins passent moins bien en grand) ; à côté, ce qu'il est, sa puissance et ses
// attributs principaux ; les secondaires sur une rangée dessous. Puis un panneau sombre : l'équipement (un emplacement ouvre sa fenêtre par-dessus la page), le niveau,
// l'attaque spéciale (aperçu en boucle à la demande), les talents. Les flèches de la case, ou un geste sur elle, passent au
// héros suivant. La fusion et la Renaissance se font sur leurs pages (onglet Héros).
import type preact from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';
import { applyStatMods } from '../../../core/battle/engine';
import { AWAKEN_SKILL, AWAKEN_STARS } from '../../../core/data/heroes';
import { heroToUnit } from '../../../core/battle/units';
import type { Talent } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { GEAR_SLOTS, type GearSlot } from '../../../core/data/items';
import { levelCap } from '../../../core/data/stats';
import { ELEMENT_COLOR, RARITY_COLOR } from '../../art';
import { fmt, t } from '../../i18n';
import { equipBest, levelUp, toggleInFormation, unequipAll } from '../../state/actions';
import { canLevelUp, gearStatsOf, heroByUid, heroItems, heroPower, levelUpCost, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Bar, Btn, Cur, Icon, ItemIcon, Sign, Stars, starText } from '../kit';
import { MYTHIC_STARS } from '../../../core/data/stars';
import { Halo } from '../anim';
import { HeroFigure } from '../hero-figure';
import { HeroScene, Pedestal } from '../hero-scene';
import { TitleBanner } from '../title-banner';
import { SlotPanel, betterInBag } from './bag';
import { describePassive, describeSkill, describeTalent } from '../../describe';
import { runSkillPreview } from '../../scenes';
import type { UnitInit } from '../../../core/battle/types';
import { close, open, swap, toast } from '../nav';

export function talentText(talent: Talent | undefined): string {
  return describeTalent(talent);
}

/** Le picto d'un attribut (cœur, épée, bouclier, aile, cible, éclat, plume, roc) : ceux de la planche. */
function StatIcon({ k }: { k: string }) {
  return <Art name={k} class="stat-icon" />;
}

/** Les 8 attributs du héros, avec ses passifs permanents déjà débloqués : les quatre principaux (à côté de sa case, en
 * creux : picto, valeur, nom) ou les quatre secondaires (une rangée sous la case). */
function StatsGrid({ unit, part }: { unit: UnitInit; part: 'main' | 'minor' }) {
  let u = unit;
  for (const p of unit.passives ?? []) if (p.kind === 'stats') u = applyStatMods(u, p.stats);
  const pct = (x = 0) => `${Math.round(x * 100)} %`;
  if (part === 'main') {
    const main: [string, string][] = [['hp', fmt(u.maxHp)], ['atk', fmt(u.atk)], ['def', fmt(u.def)], ['speed', String(Math.round(1000 / u.interval))]];
    return <div class="stat-main">{main.map(([k, v]) => <span><StatIcon k={k} /><b>{v}</b><small>{t(`stat.${k}`)}</small></span>)}</div>;
  }
  const minor: [string, string][] = [['crit', pct(u.crit)], ['critDmg', pct((u.critDmg ?? 1.5) - 1)], ['dodge', pct(u.dodge)], ['tenacity', pct(u.tenacity)]];
  return <div class="stat-minor">{minor.map(([k, v]) => <span><StatIcon k={k} /><b>{v}</b><small>{t(`stat.${k}`)}</small></span>)}</div>;
}

/** La compétence jouée en boucle contre des monstres. Redémarre si la force du héros change. */
function SkillPreview({ unit }: { unit: UnitInit }) {
  const host = useRef<HTMLDivElement>(null);
  const key = `${unit.id}|${unit.atk}|${unit.maxHp}`;
  useEffect(() => {
    if (!host.current) return;
    return runSkillPreview(host.current, unit);
  }, [key]);
  return <div class="skill-preview" ref={host} />;
}

/** Le ruban du titre, à la couleur de la rareté. */
const RIBBON: Record<string, [string, string, string]> = {
  common: ['#9aa6bc', '#5c677e', '#343c4e'], rare: ['#5a8cf0', '#2a4fb5', '#172c6e'], epic: ['#b06aff', '#6a2fc0', '#3a1470'], legendary: ['#ffb02a', '#c86a0a', '#7a3c05'],
};


export function HeroDetail({ uid }: { uid: number }) {
  const s = useGame();
  // l'emplacement d'équipement ouvert (sa fenêtre monte du bas), l'aperçu de la compétence
  const [gearSlot, setGearSlot] = useState<GearSlot | null>(null);
  const [preview, setPreview] = useState(false);
  const hero = heroByUid(s, uid);
  // Un niveau gagné : un éclair monte du piédestal.
  const seen = useRef({ uid, level: hero?.level ?? 0 });
  const [flash, setFlash] = useState(0);
  useEffect(() => {
    if (!hero) return;
    if (seen.current.uid === uid && hero.level > seen.current.level) setFlash((x) => x + 1);
    seen.current = { uid, level: hero.level };
  }, [uid, hero?.level]);
  // glisser la case vers la gauche ou la droite : le héros suivant
  const swipe = useRef<number | null>(null);
  if (!hero) return null;
  const d = heroDef(hero.defId);
  const unit = heroToUnit(hero, 0, gearStatsOf(s, uid));
  const cost = levelUpCost(hero);
  const items = heroItems(s, uid);
  const inTeam = s.formation.some(([u]) => u === uid);
  const rar = hero.stars >= MYTHIC_STARS ? '#ff4d5e' : RARITY_COLOR[d.rarity];
  const cap = levelCap(hero.stars);
  // les flèches : le héros d'avant ou d'après, du plus fort au plus faible
  const order = [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a));
  const at = order.findIndex((h) => h.uid === uid);
  const step = (k: number) => swap({ type: 'hero', uid: order[(at + k + order.length) % order.length]!.uid });

  return (
    <div class={`page hero-page hp-${d.rarity}`} style={{ '--rar': rar, '--el': ELEMENT_COLOR[d.element] } as never}>
      <i class="hp-bg" />
      <header class="hp-head">
        <button class="x hp-back" aria-label={t('back')} onClick={close}>‹</button>
        <TitleBanner title={d.name} ribbon={RIBBON[d.rarity]} />
        <button class={`hp-team${inTeam ? ' on' : ''}`} aria-label={inTeam ? t('heroes.inTeam') : t('heroes.addTeam')} onClick={() => {
          const r = toggleInFormation(uid);
          if (r === 'full') toast(t('heroes.full'));
        }}>
          <Icon name="heroes" size={24} />
          <i>{inTeam ? <Sign name="check" /> : <Sign name="op-plus" />}</i>
        </button>
      </header>

      <div class="hp-top">
        {/* la case du héros : il se tient sur son piédestal, dans le décor de son élément */}
        <div class="hp-card-wrap">
          <div class={`hp-card hcard-${d.rarity}${hero.stars >= MYTHIC_STARS ? ' hcard-mythic' : ''}`}
            onTouchStart={(e) => { swipe.current = e.touches[0]!.clientX; }}
            onTouchEnd={(e) => {
              const x0 = swipe.current;
              swipe.current = null;
              if (x0 === null || order.length < 2) return;
              const dx = e.changedTouches[0]!.clientX - x0;
              if (Math.abs(dx) > 44) step(dx < 0 ? 1 : -1);
            }}>
            <HeroScene element={d.element} crop={[118, 500]} />
            <i class="hp-aura" />
            {d.rarity === 'legendary' && <Halo size={150} color="#ffd45c" class="hp-halo" />}
            <span class="hp-ped"><Pedestal element={d.element} rarity={rar} /></span>
            {flash > 0 && (
              <span class="hp-levelup" key={flash}>
                <i class="hp-flash" />
                {Array.from({ length: 7 }, (_, i) => <i class="hp-spark" style={{ left: `${24 + ((i * 37) % 52)}%`, animationDelay: `${(i % 4) * 70}ms`, '--h': `${60 + ((i * 53) % 60)}px` } as never} />)}
                <b class="hp-lvpop">{t('lv')} {hero.level}</b>
              </span>
            )}
            <span class={`hp-fig${flash > 0 ? ' hp-up' : ''}`} key={`${d.id}-${flash}`}><HeroFigure defId={d.id} /></span>
            <i class="hcard-frame" />
            <span class="hp-card-lv">{t('lv')} {hero.level}</span>
            <Art name={d.element} class="hp-card-el" />
            {d.talent && <span class="hp-card-lead"><Icon name="crown" size={18} /></span>}
            <span class="hp-card-stars"><Stars stars={hero.stars} /></span>
          </div>
          {order.length > 1 && <button class="hp-arrow hp-arrow-l" aria-label="‹" onClick={() => step(-1)}><Sign name="chev" class="flip" /></button>}
          {order.length > 1 && <button class="hp-arrow hp-arrow-r" aria-label="›" onClick={() => step(1)}><Sign name="chev" /></button>}
        </div>

        {/* à côté : ce qu'il est, sa puissance, ses attributs */}
        <div class="hp-side">
          <div class="hp-tags">
            <span class="hp-tag hp-tag-rar">{t(`rarity.${d.rarity}`)}</span>
            <span class="hp-tag"><Icon name={d.role} size={15} />{t(`role.${d.role}`)}</span>
          </div>
          <div class="hp-power"><Icon name="power" size={24} /><b>{fmt(heroPower(s, hero))}</b></div>
          <StatsGrid unit={unit} part="main" />
        </div>
      </div>
      <StatsGrid unit={unit} part="minor" />

      <div class="hp-panel">
        {/* l'équipement : quatre emplacements, et le meilleur du sac d'un geste */}
        <div class="hp-gear">
          {GEAR_SLOTS.map((g) => (
            <div class={`hp-slot${gearSlot === g ? ' on' : ''}`}>
              <ItemIcon item={items[g]} slot={g} level={slotLevel(s, uid, g)} onClick={() => setGearSlot(g)} />
              {betterInBag(s, uid, g) && <span class="better"><Sign name="up" /></span>}
            </div>
          ))}
          <Btn kind="blue" small class="hp-auto" onClick={() => equipBest(uid)}>{t('detail.autoEquip')}</Btn>
        </div>

        {/* le niveau */}
        <div class="hp-level">
          <strong>{t('lv')} {hero.level}<span class="muted"> / {cap}</span></strong>
          <Bar value={hero.level} max={cap} color="linear-gradient(180deg, #8fe6a0, #3fae5a)" />
          {cost && <span class="row gap-s"><Cur k="gold" n={cost.gold} /><Cur k="essence" n={cost.essence} /></span>}
        </div>
        {cost ? (
          <div class="row gap">
            <Btn kind="green" wide class="tuto-levelup" disabled={!canLevelUp(s, hero)} onClick={() => levelUp(uid)}>{t('detail.levelUp')}</Btn>
            <Btn kind="green" small disabled={!canLevelUp(s, hero)} onClick={() => levelUp(uid, 10)}>{t('detail.levelUp10')}</Btn>
          </div>
        ) : (
          <Btn kind="gold" wide onClick={() => open({ type: 'fusion', uid })}><Icon name="fusion" size={20} /> {t('fusion.title')}</Btn>
        )}

        {/* l'attaque spéciale, avec son aperçu en boucle si on le demande */}
        <section class="hp-skill">
          <div class="hp-skill-head">
            <span class="hp-medal"><Art name={d.element} size={26} /></span>
            <span class="hp-skill-name"><small>{t('detail.skill')}</small><b>{t(`skill.${d.skill.id}`)}</b></span>
            <button class={`hp-play${preview ? ' on' : ''}`} aria-label={t('detail.preview')} onClick={() => setPreview(!preview)}><Sign name={preview ? 'stop' : 'play'} /></button>
          </div>
          <p>{describeSkill(unit.skill)}</p>
          {d.rarity === 'legendary' && (
            <p class={`small ${hero.stars >= AWAKEN_STARS ? 'gold-text' : 'muted'}`}>{starText(t('detail.awaken', { n: AWAKEN_STARS, p: Math.round((AWAKEN_SKILL - 1) * 100) }))}</p>
          )}
          {preview && <SkillPreview unit={unit} />}
        </section>

        {/* les talents : débloqués par les étoiles */}
        {d.passives.map((p, i) => {
          const locked = hero.stars < p.stars;
          return (
            <section class={`hp-talent${locked ? ' locked' : ''}`}>
              <span class="hp-req">{locked ? <Icon name="lock" size={15} /> : null}<Sign name="star" />{p.stars}</span>
              <div><h3>{t('detail.passive')} {i + 1}</h3><p>{describePassive(p.passive)}</p></div>
            </section>
          );
        })}
        {d.talent && (
          <section class="hp-talent hp-lead">
            <span class="hp-req"><Icon name="crown" size={20} /></span>
            <div><h3>{t('detail.leader')}</h3><p>{talentText(d.talent)}</p></div>
          </section>
        )}
      </div>

      {/* un emplacement ouvert : sa fenêtre monte du bas, par-dessus la page */}
      {gearSlot && (
        <div class="hp-sheet-wrap" onClick={(e) => { if (e.target === e.currentTarget) setGearSlot(null); }}>
          <div class="hp-sheet">
            <div class="hp-sheet-head">
              <span class="hp-sheet-slots">
                {GEAR_SLOTS.map((g) => (
                  <button class={`hp-sheet-tab${g === gearSlot ? ' on' : ''}`} aria-label={t(`slot.${g}`)} onClick={() => setGearSlot(g)}><Icon name={g} size={26} /></button>
                ))}
              </span>
              <button class="x" aria-label={t('close')} onClick={() => setGearSlot(null)}>✕</button>
            </div>
            <div class="row gap-s">
              <Btn kind="blue" small wide onClick={() => equipBest(uid)}>{t('detail.autoEquip')}</Btn>
              <Btn kind="ghost" small onClick={() => unequipAll(uid)}>{t('detail.unequip')}</Btn>
            </div>
            <div class="hp-sheet-body">
              <h3 class="hp-slot-name"><Icon name={gearSlot} size={18} /> {t(`slot.${gearSlot}`)}</h3>
              <SlotPanel heroUid={uid} slot={gearSlot} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
