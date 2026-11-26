// Connexion par Supabase Auth, sans bibliothèque : quelques appels à l'API de Supabase (« GoTrue »), flux PKCE.
// Chargé à la demande par auth.ts, SEULEMENT quand VITE_SUPABASE_URL et VITE_SUPABASE_ANON_KEY sont donnés.
// À l'étape du serveur, on pourra le remplacer par @supabase/supabase-js (il faudra la bibliothèque pour la base de
// données) : les fonctions d'auth.ts ne changeront pas. À VÉRIFIER au branchement (rien n'a pu être essayé sans
// projet Supabase) : docs/connexion-comptes.md, « Ce que Claude fera ».
//
// Site (navigateur) :
//   1. start()  : garde un « vérificateur » secret, part vers <url>/auth/v1/authorize?provider=google|apple&…
//   2. Google / Apple → Supabase → retour sur le jeu avec ?code=… (adresse autorisée dans Supabase, Redirect URLs)
//   3. finish() : échange le code contre une session (POST /token?grant_type=pkce), lit l'utilisateur.
// Application native : idToken() (POST /token?grant_type=id_token), le jeton vient du module natif.
import type { AuthFail, AuthProvider, AuthResult, AuthUser } from './auth';

const SESSION_KEY = 'fuze-auth-session';
const PENDING_KEY = 'fuze-auth-pending';

interface Session {
  access_token: string;
  refresh_token: string;
  /** Fin de validité (ms). */
  expires_at: number;
  provider: AuthProvider;
}

interface Pending {
  provider: AuthProvider;
  verifier: string;
  /** signin : premier lancement ; link : depuis les réglages (la partie du téléphone est gardée). */
  mode: 'signin' | 'link';
}

function readJson<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}
function writeJson(key: string, v: unknown): void {
  try {
    if (v === null) localStorage.removeItem(key);
    else localStorage.setItem(key, JSON.stringify(v));
  } catch {
    // stockage indisponible
  }
}

const fail = (reason: AuthFail, message?: string): AuthResult => ({ ok: false, reason, ...(message ? { message } : {}) });

function b64url(bytes: Uint8Array): string {
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/** Vérificateur PKCE (secret, reste sur le téléphone) et son empreinte (envoyée). */
async function pkce(): Promise<{ verifier: string; challenge: string }> {
  const verifier = b64url(crypto.getRandomValues(new Uint8Array(48)));
  const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
  return { verifier, challenge: b64url(new Uint8Array(hash)) };
}

/** L'adresse du jeu, sans ?… ni #… (doit être dans la liste « Redirect URLs » de Supabase). */
function backUrl(): string {
  return location.origin + location.pathname;
}

export function createSupabaseAuth(url: string, key: string) {
  const api = url.replace(/\/+$/, '') + '/auth/v1';
  const headers = (token?: string): Record<string, string> => ({
    apikey: key,
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  });

  async function post(path: string, body: unknown, token?: string): Promise<Record<string, unknown>> {
    const res = await fetch(api + path, { method: 'POST', headers: headers(token), body: JSON.stringify(body) });
    const data = (await res.json().catch(() => ({}))) as Record<string, unknown>;
    if (!res.ok) throw new Error(String(data.error_description ?? data.msg ?? data.message ?? res.status));
    return data;
  }

  function toUser(raw: Record<string, unknown>, provider: AuthProvider): AuthUser {
    const email = typeof raw.email === 'string' && raw.email ? raw.email : undefined;
    return { provider, id: String(raw.id), ...(email ? { email } : {}) };
  }

  /** Une réponse de /token : la session est gardée sur le téléphone, l'utilisateur est renvoyé. */
  function keep(data: Record<string, unknown>, provider: AuthProvider): AuthResult {
    const user = data.user as Record<string, unknown> | undefined;
    if (!data.access_token || !user?.id) return fail('error', 'no session');
    writeJson(SESSION_KEY, {
      access_token: String(data.access_token),
      refresh_token: String(data.refresh_token ?? ''),
      expires_at: Date.now() + Number(data.expires_in ?? 3600) * 1000,
      provider,
    } satisfies Session);
    return { ok: true, user: toUser(user, provider) };
  }

  /** Une session encore bonne (rafraîchie si elle a expiré), ou null. */
  async function session(): Promise<Session | null> {
    const s = readJson<Session>(SESSION_KEY);
    if (!s) return null;
    if (s.expires_at - 60_000 > Date.now()) return s;
    try {
      const data = await post('/token?grant_type=refresh_token', { refresh_token: s.refresh_token });
      return keep(data, s.provider).ok ? readJson<Session>(SESSION_KEY) : null;
    } catch {
      writeJson(SESSION_KEY, null);
      return null;
    }
  }

  return {
    async start(provider: AuthProvider, mode: Pending['mode']): Promise<AuthResult> {
      try {
        const { verifier, challenge } = await pkce();
        writeJson(PENDING_KEY, { provider, verifier, mode } satisfies Pending);
        const q = new URLSearchParams({
          provider,
          redirect_to: backUrl(),
          code_challenge: challenge,
          code_challenge_method: 's256',
        });
        location.assign(`${api}/authorize?${q}`);
        return fail('redirecting');
      } catch (e) {
        return fail('error', String(e));
      }
    },

    async finish(): Promise<AuthResult | null> {
      const params = new URLSearchParams(location.search);
      const pending = readJson<Pending>(PENDING_KEY);
      const code = params.get('code');
      const error = params.get('error');
      if (!pending || (!code && !error)) return null;
      writeJson(PENDING_KEY, null);
      // l'adresse redevient propre (sans ?code=…)
      history.replaceState(null, '', backUrl() + location.hash);
      if (error) return fail(error === 'access_denied' ? 'cancelled' : 'error', params.get('error_description') ?? error);
      try {
        return keep(await post('/token?grant_type=pkce', { auth_code: code, code_verifier: pending.verifier }), pending.provider);
      } catch (e) {
        return fail('error', String(e));
      }
    },

    async idToken(provider: AuthProvider, idToken: string, nonce?: string): Promise<AuthResult> {
      try {
        return keep(await post('/token?grant_type=id_token', { provider, id_token: idToken, ...(nonce ? { nonce } : {}) }), provider);
      } catch (e) {
        return fail('error', String(e));
      }
    },

    async user(): Promise<AuthUser | null> {
      const s = await session();
      if (!s) return null;
      const res = await fetch(api + '/user', { headers: headers(s.access_token) });
      if (!res.ok) return null;
      return toUser((await res.json()) as Record<string, unknown>, s.provider);
    },

    async signOut(): Promise<void> {
      const s = readJson<Session>(SESSION_KEY);
      writeJson(SESSION_KEY, null);
      if (s) await post('/logout', {}, s.access_token).catch(() => undefined);
    },
  };
}
