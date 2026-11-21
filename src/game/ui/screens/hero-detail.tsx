// La page d'un héros, en plein écran : il se tient sur son piédestal dans le décor de son élément (hero-scene.tsx), son
// équipement de part et d'autre, ses étoiles et sa puissance dessous ; en bas, un panneau à trois onglets (attributs et
// niveau, compétences, équipement). Les flèches du titre passent au héros suivant. La fusion et la Renaissance se font
// sur leurs pages (onglet Héros).
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
import { Art, Bar, Btn, Cur, Icon, ItemIcon, Stars, Tabs } from '../kit';
import { MYTHIC_STARS } from '../../../core/data/stars';
import { Halo } from '../anim';
import { HeroFigure } from '../hero-figure';
import { HeroScene, Pedestal } from '../hero-scene';
import { TitleBanner } from '../title-banner';
import { SlotPanel, betterInBag } from './bag';
import { describePassive, describeSkill, describeTalent } from '../../describe';
import { runSkillPreview } from '../../scenes';
import type { UnitInit } from '../../../core/battle/types';
import { close, swap, toast } from '../nav';

export function talentText(talent: Talent | undefined): string {
  return describeTalent(talent);
}

/** Les 8 statistiques du héros, avec ses passifs permanents déjà débloqués. */
function StatsGrid({ unit }: { unit: UnitInit }) {
  let u = unit;
  for (const p of unit.passives ?? []) if (p.kind === 'stats') u = applyStatMods(u, p.stats);
  const pct = (x = 0) => `${Math.round(x * 100)} %`;
  const rows: [string, string][] = [
    ['hp', fmt(u.maxHp)], ['atk', fmt(u.atk)], ['def', fmt(u.def)], ['speed', String(Math.round(1000 / u.interval))],
    ['crit', pct(u.crit)], ['critDmg', pct((u.critDmg ?? 1.5) - 1)], ['dodge', pct(u.dodge)], ['tenacity', pct(u.tenacity)],
  ];
  return (
    <div class="stat-grid">
      {rows.map(([k, v]) => <span><small>{t(`stat.${k}`)}</small><b>{v}</b></span>)}
    </div>
  );
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
const LEFT_SLOTS = GEAR_SLOTS.slice(0, 2), RIGHT_SLOTS = GEAR_SLOTS.slice(2);

function Chevron({ dir }: { dir: number }) {
  return (
    <svg width="22" height="34" viewBox="0 0 22 34" aria-hidden="true" style={dir < 0 ? { transform: 'scaleX(-1)' } : undefined}>
      <path d="M6 5 L17 17 L6 29" fill="none" stroke="#2f1b0c" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M6 5 L17 17 L6 29" fill="none" stroke="#ffd45c" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
      <path d="M6 5 L17 17" fill="none" stroke="#fff6c8" stroke-width="1.5" stroke-linecap="round" />
    </svg>
  );
}

type PanelTab = 'stats' | 'skills' | 'gear';

export function HeroDetail({ uid }: { uid: number }) {
  const s = useGame();
  const [tab, setTab] = useState<PanelTab>('stats');
  const [gearSlot, setGearSlot] = useState<GearSlot>(GEAR_SLOTS[0]!);
  const hero = heroByUid(s, uid);
  // Un niveau gagné : un éclair monte du piédestal.
  const seen = useRef({ uid, level: hero?.level ?? 0 });
  const [flash, setFlash] = useState(0);
  useEffect(() => {
    if (!hero) return;
    if (seen.current.uid === uid && hero.level > seen.current.level) setFlash((x) => x + 1);
    seen.current = { uid, level: hero.level };
  }, [uid, hero?.level]);
  if (!hero) return null;
  const d = heroDef(hero.defId);
  const unit = heroToUnit(hero, 0, gearStatsOf(s, uid));
  const cost = levelUpCost(hero);
  const items = heroItems(s, uid);
  const inTeam = s.formation.some(([u]) => u === uid);
  const rar = hero.stars >= MYTHIC_STARS ? '#ff4d5e' : RARITY_COLOR[d.rarity];
  // les flèches : le héros d'avant ou d'après, du plus fort au plus faible
  const order = [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a));
  const at = order.findIndex((h) => h.uid === uid);
  const step = (k: number) => swap({ type: 'hero', uid: order[(at + k + order.length) % order.length]!.uid });
  const slot = (g: GearSlot) => (
    <div class={`hp-slot${tab === 'gear' && gearSlot === g ? ' on' : ''}`}>
      <ItemIcon item={items[g]} slot={g} level={slotLevel(s, uid, g)} onClick={() => { setGearSlot(g); setTab('gear'); }} />
      {betterInBag(s, uid, g) && <span class="better">▲</span>}
    </div>
  );

  return (
    <div class={`page hero-page hp-${d.rarity}`} style={{ '--rar': rar, '--el': ELEMENT_COLOR[d.element] } as never}>
      <HeroScene element={d.element} />
      <header class="hp-head">
        <button class="x hp-back" aria-label={t('back')} onClick={close}>‹</button>
        {order.length > 1 && <button class="hp-arrow" aria-label="‹" onClick={() => step(-1)}><Chevron dir={-1} /></button>}
        <TitleBanner title={d.name} ribbon={RIBBON[d.rarity]} />
        {order.length > 1 && <button class="hp-arrow hp-arrow-r" aria-label="›" onClick={() => step(1)}><Chevron dir={1} /></button>}
        <button class={`hp-team${inTeam ? ' on' : ''}`} aria-label={inTeam ? t('heroes.inTeam') : t('heroes.addTeam')} onClick={() => {
          const r = toggleInFormation(uid);
          if (r === 'full') toast(t('heroes.full'));
        }}>
          <Icon name="heroes" size={24} />
          <i>{inTeam ? '✓' : '+'}</i>
        </button>
      </header>
      <div class="hp-tags">
        <span class="hp-tag hp-tag-rar">{t(`rarity.${d.rarity}`)}</span>
        <span class="hp-tag">{t(`role.${d.role}`)}</span>
        <span class="hp-tag"><Art name={d.element} size={16} />{t(`element.${d.element}`)}</span>
        {d.talent && <span class="hp-tag hp-tag-lead"><Icon name="crown" size={16} /></span>}
      </div>

      <div class="hp-stage">
        <div class="hp-art">
          <i class="hp-aura" />
          {d.rarity === 'legendary' && <Halo size={260} color="#ffd45c" class="hp-halo" />}
          <Pedestal element={d.element} rarity={rar} />
          {flash > 0 && <i class="hp-flash" key={flash} />}
          <span class={`hp-fig${flash > 0 ? ' hp-up' : ''}`} key={`${d.id}-${flash}`}><HeroFigure defId={d.id} /></span>
        </div>
        <div class="hp-slots hp-slots-l">{LEFT_SLOTS.map(slot)}</div>
        <div class="hp-slots hp-slots-r">{RIGHT_SLOTS.map(slot)}</div>
        <div class="hp-plate">
          <Stars stars={hero.stars} />
          <span class="hp-power"><Icon name="power" size={18} />{fmt(heroPower(s, hero))}</span>
        </div>
      </div>

      <div class="hp-panel">
        <Tabs value={tab} onChange={setTab} options={[
          ['stats', t('detail.tabStats'), inTeam && canLevelUp(s, hero)],
          ['skills', t('detail.skill')],
          ['gear', t('detail.equip'), GEAR_SLOTS.some((g) => betterInBag(s, uid, g))],
        ]} />
        <div class="hp-body">
          {tab === 'stats' && (
            <>
              <div class="hp-level">
                <strong>{t('lv')} {hero.level}<span class="muted"> / {levelCap(hero.stars)}</span></strong>
                <Bar value={hero.level} max={levelCap(hero.stars)} color="linear-gradient(180deg, #8fe6a0, #3fae5a)" />
                {cost && <span class="row gap-s"><Cur k="gold" n={cost.gold} /><Cur k="essence" n={cost.essence} /></span>}
              </div>
              {cost ? (
                <div class="row gap">
                  <Btn kind="green" wide class="tuto-levelup" disabled={!canLevelUp(s, hero)} onClick={() => levelUp(uid)}>{t('detail.levelUp')}</Btn>
                  <Btn kind="green" small disabled={!canLevelUp(s, hero)} onClick={() => levelUp(uid, 10)}>{t('detail.levelUp10')}</Btn>
                </div>
              ) : (
                <p class="muted center">{t('detail.cap')}</p>
              )}
              <StatsGrid unit={unit} />
            </>
          )}

          {tab === 'skills' && (
            <>
              <section class="block">
                <h3>{t(`skill.${d.skill.id}`)}</h3>
                <p class="muted">{describeSkill(unit.skill)}</p>
                <SkillPreview unit={unit} />
                {d.rarity === 'legendary' && (
                  <p class={`small ${hero.stars >= AWAKEN_STARS ? 'gold-text' : 'muted'}`}>{t('detail.awaken', { n: AWAKEN_STARS, p: Math.round((AWAKEN_SKILL - 1) * 100) })}</p>
                )}
              </section>
              {d.talent && (
                <section class="block leader-block">
                  <h3><Icon name="crown" size={20} /> {t('detail.leader')}</h3>
                  <p class="muted">{talentText(d.talent)}</p>
                </section>
              )}
              <section class="block">
                {d.passives.map((p, i) => (
                  <div class={`passive${hero.stars >= p.stars ? '' : ' locked'}`}>
                    <h3>{hero.stars < p.stars && <Icon name="lock" size={16} />} {t('detail.passive')} {i + 1} <span class="muted small">{t('detail.unlockAt', { n: p.stars })}</span></h3>
                    <p class="muted">{describePassive(p.passive)}</p>
                  </div>
                ))}
              </section>
            </>
          )}

          {tab === 'gear' && (
            <>
              <div class="row gap-s">
                <Btn kind="blue" small wide onClick={() => equipBest(uid)}>{t('detail.autoEquip')}</Btn>
                <Btn kind="ghost" small onClick={() => unequipAll(uid)}>{t('detail.unequip')}</Btn>
              </div>
              <div class="hp-gear-tabs">
                {GEAR_SLOTS.map((g) => (
                  <button class={`chip${gearSlot === g ? ' on' : ''}`} onClick={() => setGearSlot(g)}><Icon name={g} size={16} /> {t(`slot.${g}`)}</button>
                ))}
              </div>
              <SlotPanel heroUid={uid} slot={gearSlot} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
