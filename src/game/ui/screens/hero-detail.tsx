// Fiche d'un héros : niveau, équipement, talent de chef (s'il en a un), compétence avec son aperçu en boucle.
// La fusion et la Renaissance se font sur leurs pages (onglet Héros).
import { useEffect, useRef, useState } from 'preact/hooks';
import { applyStatMods } from '../../../core/battle/engine';
import { AWAKEN_SKILL, AWAKEN_STARS } from '../../../core/data/heroes';
import { heroToUnit } from '../../../core/battle/units';
import type { Talent } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { GEAR_SLOTS, type GearSlot } from '../../../core/data/items';
import { levelCap } from '../../../core/data/stats';
import { ELEMENT_COLOR, RARITY_COLOR, heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { equipBest, levelUp, toggleInFormation, unequipAll } from '../../state/actions';
import { canLevelUp, gearStatsOf, heroByUid, heroItems, heroPower, levelUpCost, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, Icon, ItemIcon, Modal, Stars } from '../kit';
import { SlotPanel, betterInBag } from './bag';
import { describePassive, describeSkill, describeTalent } from '../../describe';
import { runSkillPreview } from '../../skill-scene';
import type { UnitInit } from '../../../core/battle/types';
import { close, open, toast } from '../nav';

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

export function HeroDetail({ uid }: { uid: number }) {
  const s = useGame();
  // Emplacement ouvert : le choix des objets s'affiche directement sous l'équipement.
  const [gearSlot, setGearSlot] = useState<GearSlot | undefined>(undefined);
  const hero = heroByUid(s, uid);
  if (!hero) return null;
  const d = heroDef(hero.defId);
  const unit = heroToUnit(hero, 0, gearStatsOf(s, uid));
  const cost = levelUpCost(hero);
  const items = heroItems(s, uid);
  const inTeam = s.formation.some(([u]) => u === uid);

  return (
    <Modal title={d.name} wide>
      <div class="detail-top" style={{ '--rar': RARITY_COLOR[d.rarity] } as never}>
        <img class="detail-img" src={heroImage(d.id)} alt="" />
        <div class="detail-info">
          <Stars stars={hero.stars} />
          <div class="tags">
            <span class="tag" style={{ color: RARITY_COLOR[d.rarity] }}>{t(`rarity.${d.rarity}`)}</span>
            <span class="tag">{t(`role.${d.role}`)}</span>
            <span class="tag" style={{ color: ELEMENT_COLOR[d.element] }}>{t(`element.${d.element}`)}</span>
          </div>
          <div class="power-chip"><Icon name="power" size={18} />{fmt(heroPower(s, hero))}</div>
        </div>
      </div>
      <StatsGrid unit={unit} />

      <section class="block">
        <div class="row between">
          <h3>{t('lv')} {hero.level} / {levelCap(hero.stars)}</h3>
          {cost && (
            <span class="row gap-s">
              <Cur k="gold" n={cost.gold} />
              <Cur k="essence" n={cost.essence} />
            </span>
          )}
        </div>
        {cost ? (
          <div class="row gap">
            <Btn kind="green" wide class="tuto-levelup" disabled={!canLevelUp(s, hero)} onClick={() => levelUp(uid)}>{t('detail.levelUp')}</Btn>
            <Btn kind="green" small disabled={!canLevelUp(s, hero)} onClick={() => levelUp(uid, 10)}>{t('detail.levelUp10')}</Btn>
          </div>
        ) : (
          <p class="muted">{t('detail.cap')}</p>
        )}
      </section>

      <section class="block">
        <div class="row between">
          <h3>{t('detail.equip')}</h3>
          <span class="row gap-s">
            <Btn kind="blue" small onClick={() => equipBest(uid)}>{t('detail.autoEquip')}</Btn>
            <Btn kind="ghost" small onClick={() => unequipAll(uid)}>✕</Btn>
          </span>
        </div>
        <div class="items-row">
          {GEAR_SLOTS.map((slot) => (
            <div class={`item-cell${gearSlot === slot ? ' on' : ''}`}>
              <ItemIcon item={items[slot]} slot={slot} level={slotLevel(s, uid, slot)} onClick={() => setGearSlot(gearSlot === slot ? undefined : slot)} />
              {betterInBag(s, uid, slot) && <span class="better">▲</span>}
              <span class="muted small">{t(`slot.${slot}`)}</span>
            </div>
          ))}
        </div>
        {gearSlot && <SlotPanel heroUid={uid} slot={gearSlot} />}
      </section>

      {d.talent && (
        <section class="block leader-block">
          <h3>♛ {t('detail.leader')}</h3>
          <p class="muted">{talentText(d.talent)}</p>
        </section>
      )}

      <section class="block">
        <h3>{t('detail.skill')} · {t(`skill.${d.skill.id}`)}</h3>
        <p class="muted">{describeSkill(unit.skill)}</p>
        <SkillPreview unit={unit} />
        {d.rarity === 'legendary' && (
          <p class={`small ${hero.stars >= AWAKEN_STARS ? 'gold-text' : 'muted'}`}>{t('detail.awaken', { n: AWAKEN_STARS, p: Math.round((AWAKEN_SKILL - 1) * 100) })}</p>
        )}
      </section>

      <section class="block">
        {d.passives.map((p, i) => (
          <div class={`passive${hero.stars >= p.stars ? '' : ' locked'}`}>
            <h3>{hero.stars >= p.stars ? '◆' : '🔒'} {t('detail.passive')} {i + 1} <span class="muted small">{t('detail.unlockAt', { n: p.stars })}</span></h3>
            <p class="muted">{describePassive(p.passive)}</p>
          </div>
        ))}
      </section>

      <div class="row gap">
        <Btn kind={inTeam ? 'ghost' : 'blue'} wide onClick={() => {
          const r = toggleInFormation(uid);
          if (r === 'full') toast(t('heroes.full'));
        }}>
          {inTeam ? t('heroes.inTeam') : t('heroes.addTeam')}
        </Btn>
      </div>
      <button class="sr-only" onClick={close}>{t('close')}</button>
    </Modal>
  );
}
