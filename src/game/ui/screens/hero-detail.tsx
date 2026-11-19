// Fiche d'un héros : niveau, équipement, étoiles (fusion), compétence et talent de chef.
import { heroToUnit } from '../../../core/battle/units';
import type { Talent } from '../../../core/battle/types';
import { heroDef } from '../../../core/data/heroes';
import { GEAR_SLOTS } from '../../../core/data/items';
import { LADDER, RARITY_RULES, TRIPLE_COUNT } from '../../../core/data/stars';
import { levelCap } from '../../../core/data/stats';
import { canGainStar } from '../../../core/fusion';
import { ELEMENT_COLOR, RARITY_COLOR, heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { equipBest, fuse, fusionPreview, levelUp, resetHero, toggleInFormation, unequipAll } from '../../state/actions';
import { canLevelUp, gearPct, heroByUid, heroItems, heroPower, levelUpCost, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import type { PlayerState } from '../../state/types';
import { Btn, Cur, Icon, ItemIcon, Modal, Stars } from '../kit';
import { close, open, toast } from '../nav';

export function talentText(talent: Talent): string {
  const parts: string[] = [];
  const pct = (x: number) => Math.round((x - 1) * 100);
  if (talent.atkMult) parts.push(t('talent.atkMult', { n: pct(talent.atkMult) }));
  if (talent.defMult) parts.push(t('talent.defMult', { n: pct(talent.defMult) }));
  if (talent.intervalMult) parts.push(t('talent.intervalMult', { n: Math.round((1 - talent.intervalMult) * 100) }));
  if (talent.energyMult) parts.push(t('talent.energyMult', { n: pct(talent.energyMult) }));
  if (talent.startEnergy) parts.push(t('talent.startEnergy', { n: talent.startEnergy }));
  return parts.join(' · ');
}

/** Ce que le joueur possède pour la prochaine étoile (pour afficher « 1 / 2 »). */
function starNeeds(s: PlayerState, uid: number) {
  const hero = heroByUid(s, uid)!;
  const d = heroDef(hero.defId);
  const rule = RARITY_RULES[d.rarity];
  const inTeam = new Set(s.formation.map(([u]) => u));
  const others = s.heroes.filter((h) => h.uid !== uid && !inTeam.has(h.uid));
  if (rule.fusion === 'triple') {
    return { triple: others.filter((h) => h.defId === hero.defId && h.stars === hero.stars).length + 1 };
  }
  const step = LADDER[hero.stars + 1];
  if (!step) return {};
  const copies = others.filter((h) => h.defId === hero.defId && h.stars === rule.bornStars);
  const fodder = others.filter(
    (h) => heroDef(h.defId).faction === d.faction && h.stars === step.fodderStars && heroDef(h.defId).rarity !== 'legendary',
  );
  return { step, copies: copies.length, fodder: fodder.length };
}

export function HeroDetail({ uid }: { uid: number }) {
  const s = useGame();
  const hero = heroByUid(s, uid);
  if (!hero) return null;
  const d = heroDef(hero.defId);
  const unit = heroToUnit(hero, 0, gearPct(s, uid));
  const cost = levelUpCost(hero);
  const items = heroItems(s, uid);
  const inTeam = s.formation.some(([u]) => u === uid);
  const preview = fusionPreview(uid);
  const needs = starNeeds(s, uid);

  return (
    <Modal title={d.name} wide>
      <div class="detail-top" style={{ '--rar': RARITY_COLOR[d.rarity] } as never}>
        <img class="detail-img" src={heroImage(d.id)} alt="" />
        <div class="detail-info">
          <Stars stars={hero.stars} />
          <div class="tags">
            <span class="tag" style={{ color: RARITY_COLOR[d.rarity] }}>{t(`rarity.${d.rarity}`)}</span>
            <span class="tag">{t(`faction.${d.faction}`)}</span>
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
            <div class="item-cell">
              <ItemIcon item={items[slot]} slot={slot} level={slotLevel(s, uid, slot)} onClick={() => open({ type: 'slot', heroUid: uid, slot })} />
              <span class="muted small">{t(`slot.${slot}`)}</span>
            </div>
          ))}
        </div>
      </section>

      <section class="block">
        <h3>{t('detail.stars')}</h3>
        {!canGainStar(hero) ? (
          <p class="muted">{t('detail.maxStars')}</p>
        ) : (
          <>
            <div class="row gap-s center-y">
              <Stars stars={hero.stars} /> <span class="arrow">→</span> <Stars stars={hero.stars + 1} />
            </div>
            <ul class="needs">
              {needs.triple !== undefined && <li class={needs.triple >= TRIPLE_COUNT ? 'ok' : ''}>{t('detail.triple', { have: needs.triple })}</li>}
              {needs.step && (
                <>
                  <li class={(needs.copies ?? 0) >= needs.step.copies ? 'ok' : ''}>{t('detail.copies', { have: needs.copies ?? 0, need: needs.step.copies })}</li>
                  {needs.step.fodderCount > 0 && (
                    <li class={(needs.fodder ?? 0) >= needs.step.fodderCount ? 'ok' : ''}>
                      {t('detail.fodder', { s: needs.step.fodderStars, have: needs.fodder ?? 0, need: needs.step.fodderCount })}
                    </li>
                  )}
                  {needs.step.crystals > 0 && (
                    <li class={s.wallet.crystals >= needs.step.crystals ? 'ok' : ''}>{t('detail.crystals', { have: s.wallet.crystals, need: needs.step.crystals })}</li>
                  )}
                </>
              )}
            </ul>
            <Btn
              kind="purple"
              wide
              disabled={!preview.plan}
              onClick={() => {
                const gain = fuse(uid);
                if (gain) toast('★');
              }}
            >
              {t('detail.fuse')}
            </Btn>
          </>
        )}
      </section>

      <section class="block">
        <h3>{t('detail.skill')} · {t(`skill.${d.skill.id}`)}</h3>
        <p class="muted">{t(`skilltext.${d.skill.kind}`)}</p>
        <h3>♛ {t('detail.leader')}</h3>
        <p class="muted">{talentText(d.talent)}</p>
      </section>

      <div class="row gap">
        <Btn kind={inTeam ? 'ghost' : 'blue'} wide onClick={() => {
          const r = toggleInFormation(uid);
          if (r === 'full') toast(t('heroes.full'));
        }}>
          {inTeam ? t('heroes.inTeam') : t('heroes.addTeam')}
        </Btn>
        {hero.level > 1 && (
          <Btn kind="red" small onClick={() => open({ type: 'confirm', text: `${t('detail.reset')} ?`, onYes: () => {
            resetHero(uid);
          } })}>
            {t('detail.reset')}
          </Btn>
        )}
      </div>
      <button class="sr-only" onClick={close}>{t('close')}</button>
    </Modal>
  );
}
