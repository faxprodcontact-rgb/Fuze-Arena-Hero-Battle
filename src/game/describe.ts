// Textes des compétences, passifs et talents, fabriqués à partir des effets (aucune phrase écrite à la main par héros).
import type { Effect, Passive, SkillDef, StatMods, Talent } from '../core/battle/types';
import { t } from './i18n';

const pct = (x: number) => Math.round(x * 100);

function target(e: { target: string }): string {
  return t(`tgt.${e.target}`);
}

export function describeEffect(e: Effect): string {
  switch (e.type) {
    case 'damage':
      return t('fx.damage', { p: e.power, t: target(e) })
        + (e.execute ? t('fx.execute', { n: pct(e.execute) }) : '')
        + (e.lifesteal ? t('fx.lifesteal', { n: pct(e.lifesteal) }) : '');
    case 'heal':
      return e.pctMax ? t('fx.healPct', { t: target(e), n: pct(e.pctMax) }) : t('fx.heal', { t: target(e), p: e.power ?? 0 });
    case 'shield':
      return t('fx.shield', { t: target(e), n: pct(e.power) });
    case 'energy':
      return t(e.amount >= 0 ? 'fx.energy' : 'fx.drain', { n: Math.abs(e.amount), t: target(e) });
    case 'cleanse':
      return t('fx.cleanse', { t: target(e) });
    case 'revive':
      return t('fx.revive', { n: pct(e.pctMax) });
    case 'status': {
      const chance = e.chance !== undefined && e.chance < 1 ? t('fx.chance', { n: pct(e.chance) }) : '';
      const name = t(`st.${e.status}`, { n: pct(e.value ?? 0) });
      if (e.status === 'burn' || e.status === 'bleed' || e.status === 'regen') return t('fx.statusDot', { s: name, t: target(e), n: pct(e.value ?? 0), d: e.seconds }) + chance;
      if (e.status === 'poison') return t('fx.statusDot', { s: name, t: target(e), n: pct(e.value ?? 0), d: e.seconds }) + chance;
      return t('fx.status', { s: name, t: target(e), d: e.seconds }) + chance;
    }
  }
}

export function describeSkill(skill: SkillDef): string {
  return skill.effects.map(describeEffect).join(' · ');
}

export function describeStats(m: StatMods): string {
  return Object.entries(m)
    .filter(([, v]) => v)
    .map(([k, v]) => `${t(`stat.${k}`)} +${pct(v as number)} %`)
    .join(' · ');
}

export function describePassive(p: Passive): string {
  if (p.kind === 'stats') return t(p.team ? 'on.team' : 'on.stats', { s: describeStats(p.stats) });
  const chance = p.chance !== undefined && p.chance < 1 ? t('fx.chance', { n: pct(p.chance) }) : '';
  return `${t(`on.${p.on}`)}${chance} : ${p.effects.map(describeEffect).join(' · ')}`;
}

export function describeTalent(talent: Talent | undefined): string {
  if (!talent) return '';
  const parts: string[] = [];
  if (talent.atkMult) parts.push(t('talent.atkMult', { n: pct(talent.atkMult - 1) }));
  if (talent.defMult) parts.push(t('talent.defMult', { n: pct(talent.defMult - 1) }));
  if (talent.intervalMult) parts.push(t('talent.intervalMult', { n: pct(1 - talent.intervalMult) }));
  if (talent.energyMult) parts.push(t('talent.energyMult', { n: pct(talent.energyMult - 1) }));
  if (talent.healMult) parts.push(t('talent.healMult', { n: pct(talent.healMult - 1) }));
  if (talent.startEnergy) parts.push(t('talent.startEnergy', { n: talent.startEnergy }));
  return parts.join(' · ');
}
