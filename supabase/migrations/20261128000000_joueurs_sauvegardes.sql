-- Premières tables du serveur (28/11/2026, projet « Fuze Arena - Hero Battle » du compte Supabase dédié au jeu).
-- Un joueur = un compte de Supabase Auth (Google, Apple, plus tard anonyme). Le serveur est le juge : le téléphone
-- peut LIRE sa ligne, mais n'écrit pas directement ; les écritures passeront par des fonctions du serveur (étape 3),
-- qui contrôlent ce qui est envoyé (docs/connexion-comptes.md, §4).

-- Le profil public du joueur (nom, avatar, niveau du compte) : ce que voient les autres joueurs (classements, guilde).
create table if not exists public.players (
  id uuid primary key references auth.users (id) on delete cascade,
  name text not null default '' check (char_length(name) <= 24),
  avatar text not null default '',
  account_level integer not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- La partie du joueur : toute la sauvegarde du jeu (src/game/state/types.ts, PlayerState) en JSON, avec quelques
-- chiffres à part pour les classements et les contrôles de bon sens.
create table if not exists public.saves (
  player_id uuid primary key references auth.users (id) on delete cascade,
  data jsonb not null,
  save_version integer not null default 1,
  campaign_cleared integer not null default 0,
  power integer not null default 0,
  updated_at timestamptz not null default now()
);

alter table public.players enable row level security;
alter table public.saves enable row level security;

-- Chacun ne lit que sa propre ligne (les écritures : seulement par les fonctions du serveur, avec la clé secrète).
drop policy if exists "players: lire sa ligne" on public.players;
create policy "players: lire sa ligne" on public.players for select to authenticated using (auth.uid() = id);
drop policy if exists "saves: lire sa partie" on public.saves;
create policy "saves: lire sa partie" on public.saves for select to authenticated using (auth.uid() = player_id);

-- Date de mise à jour automatique.
create or replace function public.touch_updated_at() returns trigger language plpgsql set search_path = '' as $$
begin
  new.updated_at := now();
  return new;
end;
$$;
drop trigger if exists players_touch on public.players;
create trigger players_touch before update on public.players for each row execute function public.touch_updated_at();
drop trigger if exists saves_touch on public.saves;
create trigger saves_touch before update on public.saves for each row execute function public.touch_updated_at();
