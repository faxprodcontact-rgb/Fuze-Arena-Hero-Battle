// La page d'un héros (style moderne, 26/11/2026 ; disposition voulue par le propriétaire : « bien agencé » comme les
// grands jeux du genre). Tout l'écran est son sanctuaire, teinté par son élément : une arche douce au fond, une dalle
// plate d'un bord à l'autre où il se tient, en grand, au milieu.
// En haut : ses étoiles, son nom, sa rareté. De part et d'autre : ses capacités en médaillons ronds (à gauche sa
// compétence et son attaque, à droite ses talents ; toucher = la description au milieu de l'écran). Des flèches (ou un
// geste) passent au héros d'avant ou d'après. Dessous : sa puissance entre de petits ronds (élément, rôle, attributs,
// section) ; une rangée d'attributs (niveau bien visible, PV, ATQ, DÉF, vitesse) ; le niveau +1 ; les actions
// (retour, équipement, fusion, Renaissance).
import { useEffect, useLayoutEffect, useRef, useState } from 'preact/hooks';
import { applyStatMods } from '../../../core/battle/engine';
import { AWAKEN_SKILL, AWAKEN_STARS, heroDef } from '../../../core/data/heroes';
import { heroToUnit } from '../../../core/battle/units';
import { ENERGY_PER_ATTACK, type Passive, type Talent, type UnitInit } from '../../../core/battle/types';
import { GEAR_SLOTS, type GearSlot } from '../../../core/data/items';
import { levelCap } from '../../../core/data/stats';
import { MYTHIC_STARS } from '../../../core/data/stars';
import { ELEMENT_COLOR, RARITY_COLOR, heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { equipBest, levelUp, toggleInFormation, unequipAll } from '../../state/actions';
import { canLevelUp, gearStatsOf, heroByUid, heroItems, heroPower, levelUpCost, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Btn, Cur, Icon, ItemIcon, Modal, Sign, Stars, hasArt, starText } from '../kit';
import { ELEMENT_TONE, btClass } from '../buttons';
import { SlotPanel, betterInBag } from './bag';
import { describePassive, describeSkill, describeTalent } from '../../describe';
import { runSkillPreview } from '../../scenes';
import { close, open, swap, toast } from '../nav';
import { heroArt } from '../../look';
import { vectoFig } from '../../vecto';
import { VectoImage } from '../vecto-live';
import { sizeK } from '../../hero-size';
import '../sections/heros.css';

export function talentText(talent: Talent | undefined): string {
  return describeTalent(talent);
}

/** Les attributs du héros, passifs permanents compris : [picto, valeur]. */
function statsOf(unit: UnitInit) {
  let u = unit;
  for (const p of unit.passives ?? []) if (p.kind === 'stats') u = applyStatMods(u, p.stats);
  const pct = (x = 0) => `${Math.round(x * 100)} %`;
  const main: [string, string][] = [['hp', fmt(u.maxHp)], ['atk', fmt(u.atk)], ['def', fmt(u.def)], ['speed', String(Math.round(1000 / u.interval))]];
  const minor: [string, string][] = [['crit', pct(u.crit)], ['critDmg', pct((u.critDmg ?? 1.5) - 1)], ['dodge', pct(u.dodge)], ['tenacity', pct(u.tenacity)]];
  if (u.lifesteal) minor.push(['lifesteal', pct(u.lifesteal)]);
  return { main, minor };
}

/** Le picto d'un talent : l'attribut qu'il renforce, ou l'effet qu'il déclenche. */
function passiveIcon(p: Passive): string {
  const pick = (...names: string[]) => names.find(hasArt) ?? 'star';
  if (p.kind === 'stats') {
    const k = Object.keys(p.stats).find((x) => (p.stats as Record<string, number | undefined>)[x]) ?? 'hp';
    return pick(k === 'lifesteal' ? 'hp' : k);
  }
  const e = p.effects[0];
  if (!e) return 'star';
  switch (e.type) {
    case 'damage': return pick('atk');
    case 'heal': return pick('healer', 'hp');
    case 'shield': return pick('def');
    case 'energy': return pick('power');
    case 'revive': return pick('revive');
    case 'cleanse': return pick('st-regen');
    case 'status': return pick(`st-${e.status}`);
  }
  return 'star';
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

/** Le héros en grand, pieds sur la dalle (88 % de la scène). L'échelle est la même pour tous (calée sur la hauteur de la
 * scène, sans toucher les médaillons). */
function StageFigure({ defId, up }: { defId: string; up: number }) {
  const host = useRef<HTMLSpanElement>(null);
  const [box, setBox] = useState<[number, number]>([0, 0]);
  useLayoutEffect(() => {
    const el = host.current;
    if (!el) return;
    const measure = () => setBox([el.clientWidth, el.clientHeight]);
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const [bw, bh] = box;
  const art = heroArt(defId);
  const v = vectoFig(art);
  if (!v) return <span class="hx-stage-fig" ref={host}><img class="hx-flat" src={heroImage(defId)} alt="" /></span>;
  // le dessin vectoriel lisse : tous à la même taille de corps (hero-size.ts : un humain = 100 pixels du dessin, × son
  // gabarit ; demande du 27/11), un humain sur ~45 % de la hauteur de la scène (de l'air autour, demande du 26/11) ; la
  // largeur ne le réduit que s'il passait sous les flèches (arme, ailes). Il respire par le CSS, pieds fixes.
  const k = sizeK(art);
  const fit = Math.min(((0.65 * bh * 0.8) / 116) * k, (bw / 2 - 30) / Math.max(v.fx, v.w - v.fx));
  const feetY = bh * 0.88;
  return (
    <span class="hx-stage-fig" ref={host}>
      {bh > 0 && (
        <span class="hx-stage-win hx-vec" key={`${defId}-${up}`} style={{ left: `${bw / 2 - v.fx * fit}px`, top: `${feetY - v.fy * fit}px`, width: `${v.w * fit}px`, height: `${v.h * fit}px` }}>
          <VectoImage id={art} src={v.big} style={{ transformOrigin: `${((v.fx / v.w) * 100).toFixed(1)}% ${((v.fy / v.h) * 100).toFixed(1)}%` }} />
        </span>
      )}
    </span>
  );
}

type Sheet = { kind: 'gear'; slot: GearSlot } | { kind: 'stats' } | { kind: 'skill' } | { kind: 'basic' } | { kind: 'passive'; i: number } | { kind: 'lead' } | null;

export function HeroDetail({ uid }: { uid: number }) {
  const s = useGame();
  // la fenêtre ouverte au milieu de l'écran (capacité, attributs, équipement)
  const [sheet, setSheet] = useState<Sheet>(null);
  const hero = heroByUid(s, uid);
  // Un niveau gagné : la scène s'illumine, « +1 » monte du niveau.
  const seen = useRef({ uid, level: hero?.level ?? 0 });
  const [flash, setFlash] = useState(0);
  useEffect(() => {
    if (!hero) return;
    if (seen.current.uid === uid && hero.level > seen.current.level) setFlash((x) => x + 1);
    seen.current = { uid, level: hero.level };
  }, [uid, hero?.level]);
  // glisser la scène vers la gauche ou la droite : le héros suivant
  const swipe = useRef<number | null>(null);
  if (!hero) return null;
  const d = heroDef(hero.defId);
  const unit = heroToUnit(hero, 0, gearStatsOf(s, uid));
  const cost = levelUpCost(hero);
  const items = heroItems(s, uid);
  const inTeam = s.formation.some(([u]) => u === uid);
  const mythic = hero.stars >= MYTHIC_STARS;
  const rar = mythic ? '#ff4d5e' : RARITY_COLOR[d.rarity];
  const cap = levelCap(hero.stars);
  const can = canLevelUp(s, hero);
  const stats = statsOf(unit);
  const gearUp = GEAR_SLOTS.some((g) => betterInBag(s, uid, g));
  // les flèches : le héros d'avant ou d'après, du plus fort au plus faible
  const order = [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a));
  const at = order.findIndex((h) => h.uid === uid);
  const step = (k: number) => swap({ type: 'hero', uid: order[(at + k + order.length) % order.length]!.uid });
  const basicIcon = unit.hitsBack ? 'assassin' : unit.ranged ? 'marksman' : 'atk';
  const basicText = `${t('fx.damage', { p: '1', t: t(unit.hitsBack ? 'tgt.back' : 'tgt.front') })} · ${t('fx.energy', { n: ENERGY_PER_ATTACK, t: t('tgt.self') })}`;
  const awaken = d.rarity === 'legendary';
  const awakened = awaken && hero.stars >= AWAKEN_STARS;
  const statIcon = (k: string) => (k === 'lifesteal' ? 'hp' : k);

  return (
    <div class={`page hx-page hx-p-${d.rarity}${mythic ? ' hx-p-mythic' : ''}`} style={{ '--rar': rar, '--el': ELEMENT_COLOR[d.element] } as never}>
      {/* le sanctuaire : tout l'écran */}
      <i class="hx-bg" />
      <i class="hx-light" />

      {/* en haut au milieu : étoiles, nom, rareté */}
      <header class="hx-head">
        <Stars stars={hero.stars} />
        <h1>{d.name}</h1>
        <span class="hx-tag-rar">{t(mythic ? 'rarity.mythic' : `rarity.${d.rarity}`)}</span>
        {/* les flèches de part et d'autre du nom (28/11 : dans la scène, elles passaient sous les médaillons) */}
        {order.length > 1 && <button class="hx-arrow hx-arrow-l" aria-label="‹" onClick={() => step(-1)}><Sign name="chev" class="flip" /></button>}
        {order.length > 1 && <button class="hx-arrow hx-arrow-r" aria-label="›" onClick={() => step(1)}><Sign name="chev" /></button>}
      </header>

      {/* la scène : le héros en grand, ses capacités de part et d'autre */}
      <div class="hx-stage"
        onTouchStart={(e) => { swipe.current = e.touches[0]!.clientX; }}
        onTouchEnd={(e) => {
          const x0 = swipe.current;
          swipe.current = null;
          if (x0 === null || order.length < 2) return;
          const dx = e.changedTouches[0]!.clientX - x0;
          if (Math.abs(dx) > 44) step(dx < 0 ? 1 : -1);
        }}>
        <i class="hx-arch" />
        <i class="hx-slab" />
        <i class="hx-shadow" />
        {flash > 0 && <i class="hx-flash" key={flash} />}
        <StageFigure defId={d.id} up={flash} />

        <div class="hx-meds hx-meds-l">
          <button class={`hx-med hx-med-ult${awakened ? ' on' : ''}`} aria-label={t(`skill.${d.skill.id}`)} onClick={() => setSheet({ kind: 'skill' })}>
            <Art name={d.element} class="hx-med-ic" />
          </button>
          <button class="hx-med" aria-label={t('detail.basic')} onClick={() => setSheet({ kind: 'basic' })}>
            <Icon name={basicIcon} size={32} />
          </button>
        </div>
        <div class="hx-meds hx-meds-r">
          {d.passives.map((p, i) => {
            const locked = hero.stars < p.stars;
            return (
              <button class={`hx-med${locked ? ' locked' : ''}`} aria-label={`${t('detail.passive')} ${i + 1}`} onClick={() => setSheet({ kind: 'passive', i })}>
                <Icon name={passiveIcon(p.passive)} size={32} />
                <span class="hx-med-badge">{locked ? <Icon name="lock" size={12} /> : <Sign name="star" />}{p.stars}</span>
              </button>
            );
          })}
          {d.talent && (
            <button class="hx-med hx-med-lead" aria-label={t('detail.leader')} onClick={() => setSheet({ kind: 'lead' })}>
              <Icon name="crown" size={32} />
            </button>
          )}
        </div>

      </div>

      {/* la puissance, entre de petits ronds */}
      <div class="hx-powerline">
        <span class={`hx-dot bt-rond bt-${ELEMENT_TONE[d.element]}`} aria-label={t(`element.${d.element}`)}><Art name={d.element} size={24} /></span>
        <span class="hx-dot bt-rond bt-galet" aria-label={t(`role.${d.role}`)}><Icon name={d.role} size={24} /></span>
        <span class="hx-power"><Icon name="power" size={26} /><b>{fmt(heroPower(s, hero))}</b></span>
        <button class="hx-dot bt-rond bt-galet" aria-label={t('detail.tabStats')} onClick={() => setSheet({ kind: 'stats' })}><Icon name="crit" size={24} /></button>
        <button class={`hx-dot hx-team bt-rond ${inTeam ? 'on bt-basalte' : 'bt-galet'}`} aria-label={inTeam ? t('heroes.inTeam') : t('heroes.addTeam')} onClick={() => {
          const r = toggleInFormation(uid);
          if (r === 'full') toast(t('heroes.full'));
        }}>
          <Icon name="heroes" size={24} />
          <i>{inTeam ? <Sign name="check" /> : <Sign name="op-plus" />}</i>
        </button>
      </div>

      {/* les attributs : le niveau d'abord, bien visible */}
      <button class="hx-stats" aria-label={t('detail.tabStats')} onClick={() => setSheet({ kind: 'stats' })}>
        <span class="hx-stat hx-stat-lv">
          <small>{t('lv')}</small><b>{hero.level}</b>
          <i class="hx-lvbar"><i style={{ width: `${Math.min(100, (hero.level / cap) * 100)}%` }} /></i>
          {flash > 0 && <b class="hx-lvpop" key={flash}>+1</b>}
        </span>
        {stats.main.map(([k, v]) => <span class={`hx-stat hx-stat-${k}`}><Art name={k} class="hx-stat-ic" /><b>{v}</b></span>)}
      </button>

      {/* le niveau +1 (ou la fusion au niveau maximum) */}
      {cost ? (
        <div class="hx-lvrow">
          <span class="hx-cost"><Cur k="gold" n={cost.gold} /><Cur k="essence" n={cost.essence} /></span>
          <Btn kind="green" class="tuto-levelup hx-lvup" disabled={!can} onClick={() => levelUp(uid)}><Icon name="levelUp" size={22} />{t('detail.levelUp')}</Btn>
          <Btn kind="green" class="hx-lv10" disabled={!can} onClick={() => levelUp(uid, 10)}>{t('detail.levelUp10')}</Btn>
        </div>
      ) : (
        <div class="hx-lvrow hx-capped">
          <span class="hx-cap"><Sign name="star" />{cap}</span>
          <Btn kind="gold" class="hx-lvup" onClick={() => open({ type: 'fusion', uid })}><Icon name="fusion" size={22} />{t('fusion.title')}</Btn>
        </div>
      )}

      {/* les actions ; le retour en bas à gauche */}
      <nav class="hx-actions">
        <button class="hx-act-back bt-rond bt-galet" aria-label={t('back')} onClick={close}><Sign name="chev" class="flip" /></button>
        <span class="grow" />
        <button class={`hx-act ${btClass('galet', 'l')}`} onClick={() => setSheet({ kind: 'gear', slot: 'weapon' })}>
          <Icon name="armory" size={30} /><small>{t('detail.equip')}</small>
          {gearUp && <span class="hx-act-up"><Sign name="up" /></span>}
        </button>
        <button class={`hx-act ${btClass('galet', 'l')}`} onClick={() => open({ type: 'fusion', uid })}><Icon name="fusion" size={30} /><small>{t('fusion.title')}</small></button>
        <button class={`hx-act ${btClass('galet', 'l')}`} onClick={() => open({ type: 'reset', uid })}><Icon name="rebirth" size={30} /><small>{t('detail.reset')}</small></button>
      </nav>

      {/* les fenêtres, au milieu de l'écran */}
      {sheet?.kind === 'gear' && (
        <Modal center class="modal-dark" title={t('detail.equip')} onClose={() => setSheet(null)}>
          <div class="hx-sheet">
            <div class="hx-sheet-slots">
              {GEAR_SLOTS.map((g) => (
                <div class={`hx-sheet-slot${g === sheet.slot ? ' on' : ''}`}>
                  <ItemIcon item={items[g]} slot={g} level={slotLevel(s, uid, g)} onClick={() => setSheet({ kind: 'gear', slot: g })} />
                  {!items[g] && <Icon name={g} size={26} />}
                  {betterInBag(s, uid, g) && <span class="hx-better"><Sign name="up" /></span>}
                </div>
              ))}
            </div>
            <div class="row gap-s">
              <Btn tone="galet" small wide onClick={() => equipBest(uid)}>{t('detail.autoEquip')}</Btn>
              <Btn tone="galet" small onClick={() => unequipAll(uid)}>{t('detail.unequip')}</Btn>
            </div>
            <h3 class="hx-slot-name"><Icon name={sheet.slot} size={18} /> {t(`slot.${sheet.slot}`)}</h3>
            <SlotPanel key={sheet.slot} heroUid={uid} slot={sheet.slot} />
          </div>
        </Modal>
      )}
      {sheet?.kind === 'stats' && (
        <Modal center title={t('detail.tabStats')} onClose={() => setSheet(null)}>
          <div class="hx-statlist">
            {[...stats.main, ...stats.minor].map(([k, v]) => (
              <span><Art name={statIcon(k)} class="hx-stat-ic" /><small>{t(`stat.${k}`)}</small><b>{v}</b></span>
            ))}
          </div>
        </Modal>
      )}
      {sheet?.kind === 'skill' && (
        <Modal center title={t(`skill.${d.skill.id}`)} onClose={() => setSheet(null)}>
          <div class="hx-skillsheet">
            <SkillPreview unit={unit} />
            <p>{describeSkill(unit.skill)}</p>
            {awaken && <p class={`hx-awaken${awakened ? ' on' : ''}`}>{starText(t('detail.awaken', { n: AWAKEN_STARS, p: Math.round((AWAKEN_SKILL - 1) * 100) }))}</p>}
          </div>
        </Modal>
      )}
      {sheet?.kind === 'basic' && (
        <Modal center title={t(unit.ranged ? 'detail.ranged' : 'detail.melee')} onClose={() => setSheet(null)}>
          <div class="hx-capsheet"><span class="hx-med"><Icon name={basicIcon} size={32} /></span><p>{basicText}</p></div>
        </Modal>
      )}
      {sheet?.kind === 'passive' && d.passives[sheet.i] && (
        <Modal center title={`${t('detail.passive')} ${sheet.i + 1}`} onClose={() => setSheet(null)}>
          <div class={`hx-capsheet${hero.stars < d.passives[sheet.i]!.stars ? ' locked' : ''}`}>
            <span class="hx-med"><Icon name={passiveIcon(d.passives[sheet.i]!.passive)} size={32} />
              <span class="hx-med-badge">{hero.stars < d.passives[sheet.i]!.stars ? <Icon name="lock" size={12} /> : <Sign name="star" />}{d.passives[sheet.i]!.stars}</span></span>
            <p>{describePassive(d.passives[sheet.i]!.passive)}</p>
          </div>
        </Modal>
      )}
      {sheet?.kind === 'lead' && d.talent && (
        <Modal center title={t('detail.leader')} onClose={() => setSheet(null)}>
          <div class="hx-capsheet"><span class="hx-med hx-med-lead"><Icon name="crown" size={32} /></span><p>{talentText(d.talent)}</p></div>
        </Modal>
      )}
    </div>
  );
}
