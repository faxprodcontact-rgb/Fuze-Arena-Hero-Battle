// Connexion Google / Apple : les boutons officiels, la petite fenêtre « Bientôt disponible », la ligne des réglages.
// Les boutons suivent les règles des deux marques (logos officiels dessinés en vecteur, couleurs et proportions
// d'origine, textes approuvés « Continuer avec … » / « Continue with … ») : obligatoire pour l'App Store et Google.
// Tant que la connexion n'est pas branchée (auth.ts, AUTH_READY faux), toucher un bouton ouvre « Bientôt disponible ».
import { useState } from 'preact/hooks';
import { linkAccount, signIn, signOut, type AuthProvider, type AuthResult } from '../auth';
import { t } from '../i18n';
import { useGame } from '../state/store';
import { Btn, Modal } from './kit';
import { close, open, toast } from './nav';
import './sections/compte.css';

const NAME: Record<AuthProvider, string> = { google: 'Google', apple: 'Apple' };

/** Le « G » multicolore officiel de Google (dessin d'origine des boutons de connexion Google). */
export function GoogleMark({ size = 20 }: { size?: number }) {
  return (
    <svg class="auth-mark" width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
    </svg>
  );
}

/** La pomme d'Apple (une seule couleur : celle du texte du bouton). */
export function AppleMark({ size = 20 }: { size?: number }) {
  return (
    <svg class="auth-mark" width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path fill="currentColor" d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701" />
    </svg>
  );
}

export function ProviderMark({ provider, size }: { provider: AuthProvider; size?: number }) {
  return provider === 'google' ? <GoogleMark size={size} /> : <AppleMark size={size} />;
}

/**
 * Bouton officiel. `tone` : Apple a un bouton blanc (sur fond sombre) et noir (sur fond clair) ;
 * Google garde son bouton blanc partout. `compact` : le logo seul (permis par les deux marques).
 */
export function ProviderButton({ provider, tone = 'light', compact, onClick }: {
  provider: AuthProvider; tone?: 'light' | 'dark'; compact?: boolean; onClick: () => void;
}) {
  const label = t(`auth.continue.${provider}`);
  return (
    <button class={`auth-btn auth-${provider} auth-${provider === 'apple' ? tone : 'light'}${compact ? ' compact' : ''}`}
      aria-label={label} onClick={onClick}>
      <ProviderMark provider={provider} size={compact ? 22 : 20} />
      {!compact && <span>{label}</span>}
    </button>
  );
}

/** Ce que fait l'interface d'une réponse d'auth.ts : rien (départ vers Google / Apple), « bientôt », ou un message. */
function afterAuth(r: AuthResult, soon: () => void): void {
  if (r.ok) toast('✓');
  else if (r.reason === 'not-configured') soon();
  else if (r.reason === 'error') toast(t('auth.error'));
}

/** « Bientôt disponible » : la connexion n'est pas encore branchée. */
export function AuthSoonModal({ provider, onClose, onGuest }: { provider: AuthProvider; onClose?: () => void; onGuest?: () => void }) {
  return (
    <Modal title={t('auth.soon')} onClose={onClose}>
      <div class="auth-soon">
        <span class={`auth-soon-mark auth-${provider}`}><ProviderMark provider={provider} size={40} /></span>
      </div>
      {onGuest
        ? <Btn kind="green" wide onClick={onGuest}>{t('auth.guest.play')}</Btn>
        : <Btn kind="green" wide onClick={onClose ?? close}>{t('ok')}</Btn>}
    </Modal>
  );
}

/** Premier lancement, avant le nom : se connecter, ou jouer en invité (on pourra lier le compte plus tard). */
export function SignInCard({ onGuest }: { onGuest: () => void }) {
  const [soon, setSoon] = useState<AuthProvider | null>(null);
  const go = (p: AuthProvider) => void signIn(p).then((r) => afterAuth(r, () => setSoon(p)));
  return (
    <>
      <div class="name-card signin-card">
        <h1>{t('auth.title')}</h1>
        <div class="auth-stack">
          <ProviderButton provider="google" onClick={() => go('google')} />
          <ProviderButton provider="apple" tone="light" onClick={() => go('apple')} />
        </div>
        <div class="auth-or"><span>{t('auth.or')}</span></div>
        <button class="auth-guest" onClick={onGuest}>{t('auth.guest.play')}</button>
      </div>
      {soon && <AuthSoonModal provider={soon} onClose={() => setSoon(null)} onGuest={() => { setSoon(null); onGuest(); }} />}
    </>
  );
}

/** Réglages, groupe « Compte » : invité (avec les boutons pour lier) ou le compte lié. */
export function AccountRow() {
  const s = useGame();
  const link = (p: AuthProvider) => void linkAccount(p).then((r) => afterAuth(r, () => open({ type: 'authSoon', provider: p })));
  if (s.auth) {
    const a = s.auth;
    return (
      <div class="setting-row static auth-row">
        <span class="auth-who">
          <span class={`auth-chip auth-${a.provider}`}><ProviderMark provider={a.provider} size={18} /></span>
          <span class="auth-id"><b>{NAME[a.provider]}</b>{a.email && <small>{a.email}</small>}</span>
        </span>
        <Btn kind="ghost" small onClick={() => open({ type: 'confirm', text: t('auth.signOutConfirm'), onYes: () => void signOut() })}>
          {t('auth.signOut')}
        </Btn>
      </div>
    );
  }
  return (
    <div class="setting-row static auth-row">
      <span class="auth-id"><b>{t('auth.guest')}</b><small>{t('auth.guestWarn')}</small></span>
      <span class="row gap-s center-y">
        <ProviderButton provider="google" compact onClick={() => link('google')} />
        <ProviderButton provider="apple" tone="dark" compact onClick={() => link('apple')} />
      </span>
    </div>
  );
}
