// La page d'un héros (refaite le 26/11/2026, style moderne ; demande du propriétaire : « le héros en grand sur un beau
// fond sobre mais classe, en dessous ses caractéristiques et attaques, bien agencées de façon ludique avec des pictos,
// épuré ; son niveau bien visible ; pas trop d'informations »).
// De haut en bas : le nom et ses pastilles (rareté, élément, rôle) ; la scène (le héros en pied qui respire, à une
// échelle entière pour rester net, sous une lumière à la couleur de son élément ; ses étoiles ; un geste ou les flèches
// passent au héros suivant) ; le niveau (un gros médaillon cerclé de sa progression, le coût, le bouton) ; cinq
// attributs en pictos (les autres en touchant la rangée) ; ses deux attaques en cartes ; ses talents en pastilles ;
// l'équipement. Les détails s'ouvrent dans des fenêtres au milieu de l'écran.
import { useEffect, useLayoutEffect, useRef, useState } from 'preact/hooks';
import { applyStatMods } from '../../../core/battle/engine';
import { AWAKEN_SKILL, AWAKEN_STARS, heroDef } from '../../../core/data/heroes';
import { heroToUnit } from '../../../core/battle/units';
import { ENERGY_PER_ATTACK, type Talent, type UnitInit } from '../../../core/battle/types';
import { GEAR_SLOTS, type GearSlot } from '../../../core/data/items';
import { levelCap } from '../../../core/data/stats';
import { MYTHIC_STARS } from '../../../core/data/stars';
import { ELEMENT_COLOR, RARITY_COLOR, heroImage } from '../../art';
import { fmt, t } from '../../i18n';
import { equipBest, levelUp, toggleInFormation, unequipAll } from '../../state/actions';
import { canLevelUp, gearStatsOf, heroByUid, heroItems, heroPower, levelUpCost, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Art, Btn, Cur, Icon, ItemIcon, Modal, Sign, Stars, starText } from '../kit';
import { SlotPanel, betterInBag } from './bag';
import { describePassive, describeSkill, describeTalent } from '../../describe';
import { runSkillPreview } from '../../scenes';
import { close, open, swap, toast } from '../nav';
import { FigStrip, figMeta } from '../sections/hero-fig';
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

/** Le héros en grand, au milieu de la scène, pieds sur le sol. L'échelle est la même pour tous (calée sur la hauteur de
 * la scène) et tombe sur un multiple d'un demi-pixel d'écran : le pixel art reste net. */
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
  const m = figMeta(defId);
  const [bw, bh] = box;
  if (!m) return <span class="hx-stage-fig" ref={host}><img class="hx-flat" src={heroImage(defId)} alt="" /></span>;
  const [w, h, fx, fy, n, ms] = m;
  // la place du héros : de 4 % sous le haut de la scène jusqu'à la ligne du sol (84 %) ; 116 = un grand héros.
  // Un pixel du dessin = un nombre entier de points de l'écran (1/3 de pixel CSS sur un écran ×3) : il reste net.
  const dpr = Math.round(window.devicePixelRatio || 1) || 1;
  const steps = dpr >= 2 ? dpr : 2;
  const k = Math.max(1, Math.floor(((bh * 0.8) / 116) * steps) / steps);
  const feetY = bh * 0.84;
  return (
    <span class="hx-stage-fig" ref={host}>
      {bh > 0 && (
        <span class={`hx-stage-win hx-up-${up % 2}`} key={`${defId}-${up}`} style={{ left: `${bw / 2 - fx * k}px`, top: `${feetY - fy * k}px`, width: `${w * k}px`, height: `${h * k}px` }}>
          <FigStrip id={defId} n={n} ms={ms} />
        </span>
      )}
    </span>
  );
}

type Sheet = { kind: 'gear'; slot: GearSlot } | { kind: 'stats' } | { kind: 'talents' } | { kind: 'skill' } | null;

export function HeroDetail({ uid }: { uid: number }) {
  const s = useGame();
  // la fenêtre ouverte par-dessus la page (équipement, attributs, talents, aperçu de la compétence)
  const [sheet, setSheet] = useState<Sheet>(null);
  const hero = heroByUid(s, uid);
  // Un niveau gagné : la scène s'illumine, « +1 » monte du médaillon.
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
  // les flèches : le héros d'avant ou d'après, du plus fort au plus faible
  const order = [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a));
  const at = order.findIndex((h) => h.uid === uid);
  const step = (k: number) => swap({ type: 'hero', uid: order[(at + k + order.length) % order.length]!.uid });
  const ranged = unit.ranged;
  const basicIcon = unit.hitsBack ? 'assassin' : ranged ? 'marksman' : 'atk';
  const basicText = `${t('fx.damage', { p: '1', t: t(unit.hitsBack ? 'tgt.back' : 'tgt.front') })} · ${t('fx.energy', { n: ENERGY_PER_ATTACK, t: t('tgt.self') })}`;
  const awaken = d.rarity === 'legendary';

  return (
    <div class={`page hx-page hx-p-${d.rarity}${mythic ? ' hx-p-mythic' : ''}`} style={{ '--rar': rar, '--el': ELEMENT_COLOR[d.element] } as never}>
      <i class="hx-bg" />

      {/* le haut : retour, le nom et ses pastilles, l'entrée dans la section */}
      <header class="hx-head">
        <button class="hx-round hx-back" aria-label={t('back')} onClick={close}><Sign name="chev" class="flip" /></button>
        <div class="hx-title">
          <h1>{d.name}</h1>
          <div class="hx-tags">
            <span class="hx-tag hx-tag-rar">{t(mythic ? 'rarity.mythic' : `rarity.${d.rarity}`)}</span>
            <span class="hx-tag"><Art name={d.element} size={16} />{t(`element.${d.element}`)}</span>
            <span class="hx-tag"><Icon name={d.role} size={16} />{t(`role.${d.role}`)}</span>
          </div>
        </div>
        <button class={`hx-round hx-team${inTeam ? ' on' : ''}`} aria-label={inTeam ? t('heroes.inTeam') : t('heroes.addTeam')} onClick={() => {
          const r = toggleInFormation(uid);
          if (r === 'full') toast(t('heroes.full'));
        }}>
          <Icon name="heroes" size={26} />
          <i>{inTeam ? <Sign name="check" /> : <Sign name="op-plus" />}</i>
        </button>
      </header>

      {/* la scène : le héros en grand */}
      <div class="hx-stage"
        onTouchStart={(e) => { swipe.current = e.touches[0]!.clientX; }}
        onTouchEnd={(e) => {
          const x0 = swipe.current;
          swipe.current = null;
          if (x0 === null || order.length < 2) return;
          const dx = e.changedTouches[0]!.clientX - x0;
          if (Math.abs(dx) > 44) step(dx < 0 ? 1 : -1);
        }}>
        <i class="hx-light" />
        <i class="hx-floor-band" />
        <i class="hx-shadow" />
        {flash > 0 && <i class="hx-flash" key={flash} />}
        <StageFigure defId={d.id} up={flash} />
        <span class="hx-power"><Icon name="power" size={22} /><b>{fmt(heroPower(s, hero))}</b></span>
        {d.talent && <span class="hx-lead" aria-label={t('detail.leader')}><Icon name="crown" size={20} /></span>}
        <span class="hx-stars"><Stars stars={hero.stars} /></span>
        {order.length > 1 && <button class="hx-arrow hx-arrow-l" aria-label="‹" onClick={() => step(-1)}><Sign name="chev" class="flip" /></button>}
        {order.length > 1 && <button class="hx-arrow hx-arrow-r" aria-label="›" onClick={() => step(1)}><Sign name="chev" /></button>}
      </div>

      {/* le niveau : le médaillon cerclé de la progression vers le niveau maximum, le coût, le bouton */}
      <div class="hx-level">
        <span class="hx-lvbadge" style={{ '--p': `${Math.min(1, hero.level / cap) * 360}deg` } as never}>
          <span class="hx-lvin"><small>{t('lv')}</small><b>{hero.level}</b><em>/ {cap}</em></span>
          {flash > 0 && <b class="hx-lvpop" key={flash}>+1</b>}
        </span>
        {cost ? (
          <>
            <span class="hx-cost"><Cur k="gold" n={cost.gold} /><Cur k="essence" n={cost.essence} /></span>
            <span class="hx-lvbtns">
              <Btn kind="green" class="tuto-levelup hx-lvup" disabled={!can} onClick={() => levelUp(uid)}><Icon name="levelUp" size={22} />{t('detail.levelUp')}</Btn>
              <Btn kind="green" small class="hx-lv10" disabled={!can} onClick={() => levelUp(uid, 10)}>{t('detail.levelUp10')}</Btn>
            </span>
          </>
        ) : (
          <span class="hx-lvbtns hx-capped">
            <Btn kind="gold" onClick={() => open({ type: 'fusion', uid })}><Icon name="fusion" size={22} /> {t('fusion.title')}</Btn>
          </span>
        )}
      </div>

      {/* cinq attributs en pictos ; les autres en touchant la rangée */}
      <button class="hx-stats" aria-label={t('detail.tabStats')} onClick={() => setSheet({ kind: 'stats' })}>
        {stats.main.map(([k, v]) => (
          <span class={`hx-stat hx-stat-${k}`}><Art name={k} class="hx-stat-ic" /><b>{v}</b><small>{t(`stat.${k}`)}</small></span>
        ))}
        <span class="hx-more" aria-hidden="true"><i /><i /><i /></span>
      </button>

      {/* ses deux attaques, en cartes */}
      <div class="hx-moves">
        <div class="hx-move hx-basic">
          <span class="hx-move-ic"><Icon name={basicIcon} size={30} /></span>
          <small>{t('detail.basic')}</small>
          <b>{t(ranged ? 'detail.ranged' : 'detail.melee')}</b>
          <p>{basicText}</p>
        </div>
        <button class="hx-move hx-special" aria-label={t('detail.preview')} onClick={() => setSheet({ kind: 'skill' })}>
          <span class="hx-move-ic"><Art name={d.element} size={30} /></span>
          <span class="hx-play"><Sign name="play" /></span>
          <small>{t('detail.skill')}</small>
          <b>{t(`skill.${d.skill.id}`)}</b>
          <p>{describeSkill(unit.skill)}</p>
        </button>
      </div>

      {/* l'équipement, puis les talents en pastilles */}
      <div class="hx-gear">
        {GEAR_SLOTS.map((g) => (
          <div class="hx-slot">
            <ItemIcon item={items[g]} slot={g} level={slotLevel(s, uid, g)} onClick={() => setSheet({ kind: 'gear', slot: g })} />
            {!items[g] && <Icon name={g} size={26} />}
            {betterInBag(s, uid, g) && <span class="hx-better"><Sign name="up" /></span>}
          </div>
        ))}
        <button class="hx-auto" aria-label={t('detail.autoEquip')} onClick={() => equipBest(uid)}><Icon name="armory" size={28} /><small>{t('detail.autoEquip')}</small></button>
      </div>
      <button class="hx-talents" aria-label={t('detail.talents')} onClick={() => setSheet({ kind: 'talents' })}>
        {d.passives.map((p) => {
          const locked = hero.stars < p.stars;
          return <span class={`hx-tal${locked ? ' locked' : ''}`}>{locked ? <Icon name="lock" size={14} /> : <Sign name="check" />}<Sign name="star" />{p.stars}</span>;
        })}
        {d.talent && <span class="hx-tal hx-tal-lead"><Icon name="crown" size={16} />{t('detail.leader')}</span>}
        {awaken && <span class={`hx-tal${hero.stars >= AWAKEN_STARS ? '' : ' locked'}`}><Sign name="star" />{AWAKEN_STARS}</span>}
      </button>

      {/* les fenêtres, au milieu de l'écran */}
      {sheet?.kind === 'gear' && (
        <Modal center title={t('detail.equip')} onClose={() => setSheet(null)}>
          <div class="hx-sheet">
            <div class="hx-sheet-tabs">
              {GEAR_SLOTS.map((g) => (
                <button class={`hx-sheet-tab${g === sheet.slot ? ' on' : ''}`} aria-label={t(`slot.${g}`)} onClick={() => setSheet({ kind: 'gear', slot: g })}><Icon name={g} size={28} /></button>
              ))}
            </div>
            <div class="row gap-s">
              <Btn kind="blue" small wide onClick={() => equipBest(uid)}>{t('detail.autoEquip')}</Btn>
              <Btn kind="ghost" small onClick={() => unequipAll(uid)}>{t('detail.unequip')}</Btn>
            </div>
            <h3 class="hx-slot-name"><Icon name={sheet.slot} size={18} /> {t(`slot.${sheet.slot}`)}</h3>
            <SlotPanel heroUid={uid} slot={sheet.slot} />
          </div>
        </Modal>
      )}
      {sheet?.kind === 'stats' && (
        <Modal center title={t('detail.tabStats')} onClose={() => setSheet(null)}>
          <div class="hx-statlist">
            {[...stats.main, ...stats.minor].map(([k, v]) => (
              <span><Art name={k === 'lifesteal' ? 'hp' : k} class="hx-stat-ic" /><small>{t(`stat.${k}`)}</small><b>{v}</b></span>
            ))}
          </div>
        </Modal>
      )}
      {sheet?.kind === 'talents' && (
        <Modal center title={t('detail.talents')} onClose={() => setSheet(null)}>
          <div class="hx-tallist">
            {d.passives.map((p, i) => {
              const locked = hero.stars < p.stars;
              return (
                <section class={locked ? 'locked' : ''}>
                  <span class="hx-req">{locked && <Icon name="lock" size={15} />}<Sign name="star" />{p.stars}</span>
                  <div><h3>{t('detail.passive')} {i + 1}</h3><p>{describePassive(p.passive)}</p></div>
                </section>
              );
            })}
            {d.talent && (
              <section class="lead">
                <span class="hx-req"><Icon name="crown" size={20} /></span>
                <div><h3>{t('detail.leader')}</h3><p>{talentText(d.talent)}</p></div>
              </section>
            )}
            {awaken && (
              <section class={hero.stars >= AWAKEN_STARS ? '' : 'locked'}>
                <span class="hx-req">{hero.stars < AWAKEN_STARS && <Icon name="lock" size={15} />}<Sign name="star" />{AWAKEN_STARS}</span>
                <div><p>{starText(t('detail.awaken', { n: AWAKEN_STARS, p: Math.round((AWAKEN_SKILL - 1) * 100) }))}</p></div>
              </section>
            )}
          </div>
        </Modal>
      )}
      {sheet?.kind === 'skill' && (
        <Modal center title={t(`skill.${d.skill.id}`)} onClose={() => setSheet(null)}>
          <div class="hx-skillsheet">
            <SkillPreview unit={unit} />
            <p>{describeSkill(unit.skill)}</p>
          </div>
        </Modal>
      )}
    </div>
  );
}
