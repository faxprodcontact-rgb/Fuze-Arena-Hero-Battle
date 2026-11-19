// Fiche d'un héros : niveau, équipement, talent de chef (s'il en a un), compétence avec son aperçu en boucle.
// La fusion et la Renaissance se font sur leurs pages (onglet Héros).
import { useEffect, useRef, useState } from 'preact/hooks';
import { heroToUnit } from '../../../core/battle/units';
import type { Talent } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { GEAR_SLOTS, type GearSlot } from '../../../core/data/items';
import { levelCap } from '../../../core/data/stats';
import { ELEMENT_COLOR, RARITY_COLOR, heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { equipBest, levelUp, toggleInFormation, unequipAll } from '../../state/actions';
import { canLevelUp, gearPct, heroByUid, heroItems, heroPower, levelUpCost, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, Icon, ItemIcon, Modal, Stars } from '../kit';
import { SlotPanel, betterInBag } from './bag';
import { runSkillPreview } from '../../skill-scene';
import type { UnitInit } from '../../../core/battle/types';
import { close, open, toast } from '../nav';

export function talentText(talent: Talent | undefined): string {
  const parts: string[] = [];
  if (!talent) return '';
  const pct = (x: number) => Math.round((x - 1) * 100);
  if (talent.atkMult) parts.push(t('talent.atkMult', { n: pct(talent.atkMult) }));
  if (talent.defMult) parts.push(t('talent.defMult', { n: pct(talent.defMult) }));
  if (talent.intervalMult) parts.push(t('talent.intervalMult', { n: Math.round((1 - talent.intervalMult) * 100) }));
  if (talent.energyMult) parts.push(t('talent.energyMult', { n: pct(talent.energyMult) }));
  if (talent.startEnergy) parts.push(t('talent.startEnergy', { n: talent.startEnergy }));
  return parts.join(' · ');
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
  const unit = heroToUnit(hero, 0, gearPct(s, uid));
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
          <div class="stats">
            <span>{t('detail.hp')} <b>{fmt(unit.maxHp)}</b></span>
            <span>{t('detail.atk')} <b>{fmt(unit.atk)}</b></span>
            <span>{t('detail.def')} <b>{fmt(unit.def)}</b></span>
          </div>
        </div>
      </div>

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
            <Btn kind="green" wide disabled={!canLevelUp(s, hero)} onClick={() => levelUp(uid)}>{t('detail.levelUp')}</Btn>
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
        <p class="muted">{t(`skilltext.${d.skill.kind}`)}</p>
        <SkillPreview unit={unit} />
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
