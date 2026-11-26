// Connexion des comptes (Google, Apple) — prête à être allumée, éteinte tant que le serveur n'existe pas.
// Mode d'emploi complet : docs/connexion-comptes.md.
//
// - Le jeu ne parle QU'À ce fichier pour les comptes (écran du premier lancement, réglages).
// - Allumé quand les deux variables publiques de Supabase sont données à la construction (Vite) :
//     VITE_SUPABASE_URL=https://<projet>.supabase.co   VITE_SUPABASE_ANON_KEY=<clé publique « anon »>
//   (ces deux valeurs sont publiques ; les secrets Google et Apple restent DANS Supabase, jamais dans le jeu).
// - Éteint (aujourd'hui) : chaque fonction répond { ok: false, reason: 'not-configured' } et l'interface montre
//   la petite fenêtre « Bientôt disponible ». Le code de Supabase (auth-supabase.ts) n'est alors jamais téléchargé :
//   il est chargé à la demande (import dynamique), donc le jeu ne grossit pas.
// - Le joueur invité garde sa partie sur le téléphone ; lier un compte plus tard GARDE cette partie (elle sera
//   envoyée au serveur, qui deviendra le juge, à l'étape du serveur).
import { linkAuth, unlinkAuth } from './state/actions';
import type { AuthProvider } from './state/types';

export type { AuthProvider };

export interface AuthUser {
  provider: AuthProvider;
  /** Identifiant de l'utilisateur chez Supabase. */
  id: string;
  email?: string;
}

export type AuthFail = 'not-configured' | 'redirecting' | 'cancelled' | 'error';
export type AuthResult = { ok: true; user: AuthUser } | { ok: false; reason: AuthFail; message?: string };

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

/** Vrai quand la connexion est branchée (les deux variables de Supabase sont données). */
export const AUTH_READY = Boolean(SUPABASE_URL && SUPABASE_KEY);

const NOT_CONFIGURED: AuthResult = { ok: false, reason: 'not-configured' };

/** Le code de Supabase, chargé seulement quand la connexion est branchée. */
async function backend() {
  const mod = await import('./auth-supabase');
  return mod.createSupabaseAuth(SUPABASE_URL!, SUPABASE_KEY!);
}

/**
 * Se connecter (premier lancement). Sur le site : part chez Google ou Apple puis revient au jeu (la page se
 * recharge ; `finishSignIn` termine au retour) — le résultat est alors { ok: false, reason: 'redirecting' }.
 */
export async function signIn(provider: AuthProvider): Promise<AuthResult> {
  if (!AUTH_READY) return NOT_CONFIGURED;
  return (await backend()).start(provider, 'signin');
}

/** Lier un compte à la partie invitée (réglages). La partie du téléphone est gardée. */
export async function linkAccount(provider: AuthProvider): Promise<AuthResult> {
  if (!AUTH_READY) return NOT_CONFIGURED;
  return (await backend()).start(provider, 'link');
}

/**
 * Application native (Capacitor, plus tard) : le module natif Google / Apple donne un « id token », Supabase
 * l'échange contre une session (pas de passage par le navigateur). Voir docs/connexion-comptes.md.
 */
export async function signInWithIdToken(provider: AuthProvider, idToken: string, nonce?: string): Promise<AuthResult> {
  if (!AUTH_READY) return NOT_CONFIGURED;
  const r = await (await backend()).idToken(provider, idToken, nonce);
  if (r.ok) linkAuth(r.user);
  return r;
}

/** Au lancement du jeu : termine une connexion revenue de Google ou Apple (rien à faire sinon : null). */
export async function finishSignIn(): Promise<AuthResult | null> {
  if (!AUTH_READY) return null;
  const r = await (await backend()).finish();
  if (r?.ok) linkAuth(r.user);
  return r;
}

/** Se déconnecter : la partie redevient invitée et reste sur le téléphone. */
export async function signOut(): Promise<void> {
  if (AUTH_READY) await (await backend()).signOut();
  unlinkAuth();
}

/** L'utilisateur connecté (null : invité, ou connexion pas branchée). */
export async function currentUser(): Promise<AuthUser | null> {
  if (!AUTH_READY) return null;
  return (await backend()).user();
}
