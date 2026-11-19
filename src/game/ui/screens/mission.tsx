// Envoyer une mission : on choisit soi-même les héros (ou « Auto »). Ceux qui n'ont pas assez d'étoiles
// ou sont déjà partis sont grisés.
import { useState } from 'preact/hooks';
import { t } from '../../i18n';
import { missionCandidates, missionTemplate, sendMission } from '../../state/actions';
import { heroByUid, heroPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, HeroCard, Icon, Page, Stars } from '../kit';
import { close } from '../nav';

export function MissionPage({ id }: { id: string }) {
  const s = useGame();
  const m = s.daily.missions.find((x) => x.id === id);
  const c = missionCandidates(id);
  const [team, setTeam] = useState<number[]>(() => c?.eligible.slice(0, c.need).map((h) => h.uid) ?? []);
  if (!m || !c) return null;
  const tpl = missionTemplate(m);
  const ok = new Set(c.eligible.map((h) => h.uid));
  const toggle = (uid: number) => {
    if (team.includes(uid)) setTeam(team.filter((u) => u !== uid));
    else if (team.length < c.need) setTeam([...team, uid]);
    else setTeam([...team.slice(1), uid]);
  };
  const roster = [...s.heroes].sort((a, b) => Number(ok.has(b.uid)) - Number(ok.has(a.uid)) || b.stars - a.stars || heroPower(s, b) - heroPower(s, a));

  return (
    <Page title={t(`mission.${tpl.id}`)}>
      <section class="fuse-stage mission-stage">
        <div class="row between center-y">
          <span class="muted"><Icon name="clock" size={16} /> {tpl.hours} h</span>
          {tpl.reward.amount ? <Cur k={tpl.reward.kind} n={tpl.reward.amount} big /> : <span class="cur cur-big"><Icon name={tpl.reward.kind} size={22} /> {tpl.reward.hours} h</span>}
        </div>
        <div class="fuse-needs">
          {Array.from({ length: c.need }, (_, i) => {
            const h = team[i] !== undefined ? heroByUid(s, team[i]!) : undefined;
            return h ? (
              <div class="fuse-slot"><HeroCard hero={h} small onClick={() => toggle(h.uid)} /></div>
            ) : (
              <div class="fuse-slot missing"><span class="fuse-faction" style={{ background: 'var(--line)' }} /><Stars stars={c.minStars} /></div>
            );
          })}
        </div>
        <div class="row gap-s">
          <Btn kind="ghost" small wide onClick={() => setTeam(c.eligible.slice(0, c.need).map((h) => h.uid))}>{t('auto')}</Btn>
          <Btn kind="blue" small wide disabled={team.length !== c.need} onClick={() => { if (sendMission(id, team)) close(); }}>{t('send')}</Btn>
        </div>
      </section>
      <div class="roster">
        {roster.map((h) => (
          <div class="hcard-wrap">
            <HeroCard hero={h} small power={heroPower(s, h)} selected={team.includes(h.uid)} dim={!ok.has(h.uid)}
              onClick={() => ok.has(h.uid) && toggle(h.uid)} />
          </div>
        ))}
      </div>
    </Page>
  );
}
