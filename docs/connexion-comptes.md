# Connexion Google et Apple — mode d'emploi

Ce document explique comment allumer la connexion « Continuer avec Google » et « Continuer avec Apple ».
Il sert à deux personnes : **toi** (les comptes à créer, clic par clic) et **la prochaine conversation de Claude**
(ce qu'il reste à brancher). Écrit le 26/11/2026.

> **Règle d'or : ne jamais coller une clé secrète dans la conversation avec Claude.** Les secrets (le « client secret »
> de Google, la clé `.p8` d'Apple) se collent **seulement dans Supabase**. Les deux seules valeurs que le jeu connaît
> (l'adresse du projet Supabase et sa clé « anon » / « publishable ») sont publiques : elles vont dans GitHub.

---

## 1. Où on en est

**Déjà fait dans le jeu (26/11/2026, toujours hors ligne) :**

- Premier lancement : une étape **« Bienvenue »** avant le choix du nom, avec les deux boutons officiels
  « Continuer avec Google » et « Continuer avec Apple », puis un lien discret **« Jouer en invité »**.
  Ordre : connexion → nom → jeu.
- Tant que la connexion n'est pas branchée, toucher Google ou Apple ouvre une petite fenêtre **« Bientôt disponible »**
  qui propose « Jouer en invité ».
- **Réglages** (par l'avatar), groupe « Compte » : une ligne « Invité — Partie gardée seulement sur ce téléphone » avec
  deux boutons ronds (logo Google, logo Apple) pour **lier le compte plus tard**. Une fois lié : le logo, l'adresse
  e-mail et un bouton « Déconnecter ».
- La sauvegarde garde le compte lié dans un champ `auth` (absent = invité). Les vieilles sauvegardes restent invitées.
- Le code qui parle à Supabase est écrit et **s'allume tout seul** dès que les deux valeurs publiques sont données à la
  construction du jeu (voir §5). Il n'est pas téléchargé tant que ce n'est pas le cas : le jeu ne grossit pas.

**Ce qui manque :** les comptes (Google Cloud, Apple Developer, Supabase), puis le serveur (sauvegarde en ligne).
Ça, seul toi peux le faire (ce sont tes comptes, à ton nom, et Apple est payant).

### Où est le code

| Fichier | Rôle |
|---|---|
| `src/game/auth.ts` | La seule porte pour les comptes : `signIn`, `linkAccount`, `signOut`, `currentUser`, `finishSignIn`, `signInWithIdToken`, et le drapeau `AUTH_READY` |
| `src/game/auth-supabase.ts` | Le branchement à Supabase Auth (appels directs à son API, flux PKCE), chargé seulement si `AUTH_READY` |
| `src/game/ui/sign-in.tsx` | Boutons officiels, fenêtre « Bientôt disponible », ligne des réglages |
| `src/game/ui/sections/compte.css` | Leur style (couleurs imposées par Google et Apple : ne pas les changer) |
| `src/game/ui/screens/meta.tsx` | `NameScreen` (étape connexion puis nom), `SettingsModal` (ligne du compte) |
| `src/game/state/actions.ts` | `linkAuth`, `unlinkAuth` (le champ `auth` de la sauvegarde) |
| `.github/workflows/site-test.yml` | Passe les deux valeurs publiques à la construction du site de test |
| `.env.example` | Modèle pour essayer en local (`.env.local`, jamais envoyé sur GitHub) |
| `tests/compte.test.ts` | Tests du champ `auth` |

---

## 2. Ce que TU dois créer (dans cet ordre)

Prévoir environ 1 h 30. Garde une note (papier ou gestionnaire de mots de passe) des valeurs marquées 📝.

### 2.1 Supabase (gratuit) — en premier, car Google et Apple demandent son adresse

> **FAIT le 28/11/2026** (par Claude, avec le jeton du compte dédié rangé dans les secrets réseau de l'environnement
> cloud, hôte `api.supabase.com`) : projet **« Fuze Arena - Hero Battle »** (créé par le propriétaire, région
> `eu-west-1`, Irlande), code `fervxczzgbbyawaqzrxj`, adresse `https://fervxczzgbbyawaqzrxj.supabase.co`, clé publique
> (publishable) `sb_publishable_Tw5VsJpYBNSALG0MRCnAjQ_f3Rdc3RY`. Site URL et Redirect URLs réglés (point 3 ci-dessous).
> Tables `players` et `saves` créées, lecture de sa seule ligne (`supabase/migrations/`). L'ancien compte et son
> ancien projet ne servent plus au jeu (rien n'y a été touché). Reste : Google et Apple (§2.2 à 2.4), puis les deux
> variables GitHub (§2.5) **seulement quand Google et Apple marchent** (sinon les boutons s'allument pour rien).

Décidé : au début de l'étape 3, on supprime l'ancien projet « Fuze Arena » (après une sauvegarde) pour faire de la
place, et on garde le projet AVA.

1. https://supabase.com/dashboard → **New project**.
   - Nom : `fuze-arena` ; mot de passe de base de données : en générer un et le garder 📝 (ne pas le donner à Claude).
   - Région : **Europe (Paris, `eu-west-3`)** ou Francfort.
2. Une fois créé : **Project Settings → API** (ou « Data API » / « API Keys »). Noter 📝 :
   - **Project URL** : `https://<code-du-projet>.supabase.co` → c'est `VITE_SUPABASE_URL` (public).
   - **anon public key** (ou la nouvelle **publishable key** `sb_publishable_…`) → c'est `VITE_SUPABASE_ANON_KEY` (public).
   - ⚠️ La clé **`service_role`** / **secret key** est SECRÈTE : elle ne va nulle part dans le jeu, jamais dans GitHub.
3. **Authentication → URL Configuration** :
   - **Site URL** : `https://faxprodcontact-rgb.github.io/Fuze-Arena-Hero-Battle/`
   - **Redirect URLs** (bouton « Add URL », une par ligne) :
     - `https://faxprodcontact-rgb.github.io/Fuze-Arena-Hero-Battle/`
     - `http://localhost:5173/**` (essais de Claude en local)
     - `http://localhost:4811/**` (aperçus de Claude)
     - plus tard, l'application : `com.fuzearena.herobattle://login-callback` (le nom exact sera choisi avec l'app)
4. **Authentication → Sign In / Providers** : laisser ouvert, on y revient après Google et Apple.
   L'adresse de retour à donner à Google et Apple y est affichée : `https://<code-du-projet>.supabase.co/auth/v1/callback` 📝.

### 2.2 Google (gratuit)

1. https://console.cloud.google.com → en haut, **sélecteur de projet → New Project** → nom `Fuze Arena` → Create.
2. Menu ☰ → **APIs & Services → OAuth consent screen** (nouvelle interface : **Google Auth Platform**) → **Get started** :
   - **App name** : `Fuze Arena – Hero Battle` ; **User support email** : ton adresse.
   - **Audience** : **External**.
   - **Contact information** : ton adresse → accepter les conditions → **Create**.
   - **Branding** : logo (l'icône du jeu `public/art/ui-px/icone-512.png`, carré), page d'accueil = le site de test,
     **Privacy policy link** et **Terms of service link** (à mettre en ligne avant la sortie, voir §8).
     **Authorized domains** : `<code-du-projet>.supabase.co` et `faxprodcontact-rgb.github.io` (et plus tard le
     domaine du jeu).
   - **Data access → Add or remove scopes** : cocher seulement `openid`, `.../auth/userinfo.email`,
     `.../auth/userinfo.profile` (pas de vérification longue de Google pour ces trois-là).
   - **Audience → Publish app** (« In production ») quand tout marche (en « Testing », seuls les testeurs ajoutés
     peuvent se connecter).
3. **Clients → Create client** (ou **Credentials → Create credentials → OAuth client ID**) :
   - **Web application** — nom `Supabase web` :
     - **Authorized JavaScript origins** : `https://faxprodcontact-rgb.github.io`
     - **Authorized redirect URIs** : `https://<code-du-projet>.supabase.co/auth/v1/callback`
     - Create → noter 📝 **Client ID** (`…apps.googleusercontent.com`) et **Client secret** (SECRET).
   - Plus tard, pour l'application iPhone : **iOS** — Bundle ID `com.fuzearena.herobattle` → noter 📝 le Client ID
     (pas de secret).
   - Plus tard, pour Android : **Android** — nom du paquet `com.fuzearena.herobattle` + **empreinte SHA-1** du
     certificat (Google Play Console → ton app → Test and release → **App integrity → App signing** : « SHA-1 certificate
     fingerprint »). Créer aussi un client pour la clé de test si besoin. Pas de secret.

### 2.3 Apple (99 $ par an)

1. **Adhérer à l'Apple Developer Program** : https://developer.apple.com/programs/enroll/ (avec ton identifiant
   Apple, double authentification activée). En **individuel** c'est le plus simple ; en **société** il faut un numéro
   D-U-N-S (gratuit mais quelques jours). Compter 1 à 2 jours de validation.
2. **Team ID** 📝 : https://developer.apple.com/account → **Membership details** → « Team ID » (10 caractères).
3. **Certificates, Identifiers & Profiles → Identifiers → (+) → App IDs → App** :
   - Description `Fuze Arena`, **Bundle ID : Explicit** `com.fuzearena.herobattle` (le même partout ensuite).
   - Dans **Capabilities**, cocher **Sign In with Apple** → Continue → Register.
4. **Identifiers → (+) → Services IDs** (c'est l'identité « site web » de la connexion Apple) :
   - Description `Fuze Arena web`, Identifier `com.fuzearena.herobattle.web` 📝 → Register.
   - Rouvrir ce Services ID → cocher **Sign In with Apple** → **Configure** :
     - **Primary App ID** : `com.fuzearena.herobattle`
     - **Domains and Subdomains** : `<code-du-projet>.supabase.co`
     - **Return URLs** : `https://<code-du-projet>.supabase.co/auth/v1/callback`
     - Next → Done → Continue → **Save**.
5. **Keys → (+)** : nom `Fuze Arena Sign in`, cocher **Sign In with Apple** → **Configure** → Primary App ID
   `com.fuzearena.herobattle` → Save → Continue → **Register** → **Download** le fichier `AuthKey_XXXXXXXXXX.p8`
   (⚠️ téléchargeable **une seule fois** : le ranger en lieu sûr, ne jamais le donner à Claude). Noter 📝 le **Key ID**
   (10 caractères).
6. (Facultatif, pour écrire aux joueurs qui cachent leur e-mail) **Services → Sign in with Apple for Email
   Communication** : déclarer l'adresse d'envoi des e-mails du jeu.

### 2.4 Retour dans Supabase : Authentication → Sign In / Providers

- **Google** → Enable :
  - **Client IDs** : le Client ID Web (plus tard, ajouter ceux d'iOS et d'Android, séparés par des virgules).
  - **Client Secret (for OAuth)** : le secret Google.
  - **Skip nonce checks** : à cocher plus tard seulement si la connexion Google native sur iPhone le demande.
  - Save.
- **Apple** → Enable :
  - **Client IDs** : `com.fuzearena.herobattle.web` (le Services ID) et, pour l'app, `com.fuzearena.herobattle`
    (séparés par une virgule).
  - **Secret Key (for OAuth)** : ce n'est pas le fichier `.p8` lui-même mais une « clé » fabriquée à partir de lui
    (Team ID + Key ID + Services ID + `.p8`). Supabase donne un outil pour la fabriquer dans sa page d'aide
    « Login with Apple » (le fabriquer **sur ton ordinateur**, dans le navigateur). ⚠️ Cette clé **expire tous les 6 mois** :
    mettre un rappel dans ton agenda pour la refaire (sinon la connexion Apple sur le site s'arrête ; l'app iPhone
    native, elle, n'en a pas besoin).
  - Save.

### 2.5 GitHub : les deux valeurs publiques (c'est ce qui allume les boutons)

À faire **en dernier**, quand Google et Apple sont prêts dans Supabase :

1. https://github.com/faxprodcontact-rgb/Fuze-Arena-Hero-Battle → **Settings → Secrets and variables → Actions**.
2. Onglet **Variables** (pas « Secrets » : ces valeurs sont publiques) → **New repository variable** :
   - `VITE_SUPABASE_URL` = l'adresse du projet (`https://<code-du-projet>.supabase.co`)
   - `VITE_SUPABASE_ANON_KEY` = la clé anon / publishable
3. Le prochain envoi reconstruit le site de test avec la connexion allumée (déjà prévu dans
   `.github/workflows/site-test.yml`). Rien d'autre à toucher.

Ensuite, dis simplement à Claude : « les comptes sont créés ». Il pourra lire ces deux valeurs publiques dans GitHub,
ou tu peux les lui donner (elles ne sont pas secrètes). Ne lui donne jamais le secret Google, la clé `.p8` ni la clé
`service_role`.

---

## 3. Comment marche la connexion (pour Claude)

**Site (navigateur) — flux PKCE de Supabase Auth, sans bibliothèque (`auth-supabase.ts`) :**

1. `signIn(p)` / `linkAccount(p)` : crée un vérificateur secret (gardé dans `localStorage`, clé `fuze-auth-pending`),
   puis va sur `<url>/auth/v1/authorize?provider=google|apple&redirect_to=<adresse du jeu>&code_challenge=…&code_challenge_method=s256`.
2. Google / Apple → Supabase → retour sur le jeu avec `?code=…` (l'adresse doit être dans « Redirect URLs »).
3. Au lancement, `main.tsx` appelle `finishSignIn()` : `POST /auth/v1/token?grant_type=pkce` `{ auth_code, code_verifier }`
   → session gardée (`fuze-auth-session`, rafraîchie par `grant_type=refresh_token`) → `linkAuth(user)` écrit
   `auth: { provider, id, email?, at }` dans la sauvegarde → l'écran du nom s'affiche directement (premier lancement).
4. `signOut()` : `POST /auth/v1/logout` puis `unlinkAuth()` (la partie reste sur le téléphone, redevient invitée).

**Application native (Capacitor, plus tard)** : on n'ouvre pas le navigateur. Le module natif donne un *id token*,
que `signInWithIdToken(provider, idToken, nonce)` échange contre une session (`POST /auth/v1/token?grant_type=id_token`).

- Modules conseillés : **`@capgo/capacitor-social-login`** (Google et Apple, iOS et Android, entretenu), ou
  **`@capacitor-community/apple-sign-in`** (Apple) + un module Google (`@capgo/capacitor-social-login` ou
  `@codetrix-studio/capacitor-google-auth`, plus ancien).
- iPhone : Xcode → la cible → **Signing & Capabilities → + Capability → Sign in with Apple** ; Google iOS : ajouter le
  « reversed client ID » dans les URL Types d'`Info.plist`.
- Apple : fabriquer un *nonce* au hasard, donner son empreinte SHA-256 à Apple et le nonce brut à Supabase.
- Android : la connexion Apple passe par une page web (le Services ID sert) ; Google natif utilise le client Android
  (SHA-1) et le client Web comme « serverClientId ».
- Ajouter les Client IDs iOS / Android dans le champ « Client IDs » des fournisseurs de Supabase (§2.4).

**À vérifier au branchement** (rien n'a pu être essayé sans projet Supabase) : les noms exacts des paramètres de
`/authorize` et `/token` contre la version de Supabase du moment ; si besoin, remplacer `auth-supabase.ts` par
`@supabase/supabase-js` (il faudra de toute façon la bibliothèque pour la base de données) **sans changer `auth.ts`**,
et en gardant l'import dynamique (le code ne doit pas être téléchargé quand la connexion est éteinte).

---

## 4. Invité → compte lié : que devient la partie ?

Aujourd'hui (hors ligne) : lier un compte **garde la partie du téléphone** telle quelle, et note le compte dans la
sauvegarde. Rien n'est perdu.

Avec le serveur (étape 3), **le serveur devient le juge** :

1. **Lier depuis les réglages** (partie invitée déjà avancée) : la sauvegarde du téléphone est envoyée **une seule fois**
   au serveur, qui l'accepte comme point de départ de ce compte (avec des contrôles de bon sens : monnaies et niveaux
   plafonnés selon l'avancée de la campagne). Ensuite, toutes les actions passent par le serveur (`actions.ts` = la
   seule porte, à brancher), le téléphone n'est plus qu'une copie.
2. **« Continuer avec Google / Apple » sur un nouveau téléphone** : le compte a déjà une partie en ligne → on la
   télécharge, la partie locale vide est remplacée.
3. **Conflit** (partie invitée avancée sur ce téléphone ET partie en ligne sur ce compte) : une fenêtre demande laquelle
   garder (« Ce téléphone » / « Le compte », avec niveau de campagne et force de chaque côté). Jamais de fusion.
4. **Option à décider à l'étape 3** : créer un compte **anonyme** Supabase dès le premier lancement (« Anonymous
   sign-ins » dans Supabase), pour que même l'invité ait sa sauvegarde sur le serveur ; lier = `linkIdentity` (réglage
   « Allow manual linking » dans Authentication → Settings). Avantage : le serveur est juge dès le premier jour.
   Inconvénient : des comptes vides à nettoyer.
5. **Supprimer mon compte** (Réglages) : devra aussi supprimer le compte en ligne et, pour Apple, **révoquer le jeton**
   (règle d'Apple), via une fonction du serveur (jamais depuis le téléphone avec une clé secrète).

---

## 5. Les variables (où va quoi)

| Valeur | Publique ? | Où |
|---|---|---|
| `VITE_SUPABASE_URL` | oui | GitHub → Actions → **Variables** ; en local `.env.local` |
| `VITE_SUPABASE_ANON_KEY` (anon / publishable) | oui | idem |
| Google Client ID (Web, iOS, Android) | oui | Supabase → Providers → Google ; plus tard dans la config de l'app |
| Google **Client secret** | **NON** | seulement Supabase → Providers → Google |
| Apple Services ID, Bundle ID, Team ID, Key ID | oui | Supabase → Providers → Apple |
| Apple **fichier .p8** / clé secrète fabriquée | **NON** | seulement Supabase → Providers → Apple (et ton coffre) |
| Supabase **service_role / secret key**, mot de passe de la base | **NON** | jamais dans le jeu ni GitHub ; seulement les fonctions du serveur |

Essai en local : copier `.env.example` en `.env.local`, remplir les deux valeurs, `npm run dev`.

---

## 6. Règles des magasins

- **App Store, règle 4.8 (Login Services)** : si le jeu propose une connexion par un service tiers (Google), il doit
  aussi proposer une option équivalente respectueuse de la vie privée — **Sign in with Apple** la remplit. Les deux
  boutons sont donc toujours présentés ensemble, au même niveau. Le mode invité est aussi accepté.
- **Boutons** : textes approuvés (« Continuer avec Google », « Continuer avec Apple »), logos officiels, couleurs
  d'origine (Google : blanc, filet gris ; Apple : blanc sur fond sombre, noir sur fond clair), même taille pour les deux.
  Ne pas les redessiner aux couleurs du jeu.
- **App Store 5.1.1(v)** et **Google Play** : un jeu qui crée des comptes doit permettre de **supprimer le compte dans
  le jeu** (déjà là : Réglages → Supprimer mon compte) ; Google Play demande aussi **une page web** pour demander la
  suppression (à mettre en ligne avec la politique de confidentialité).
- **Google Play → Data safety** et **App Store → App Privacy** : déclarer l'identifiant de compte, l'adresse e-mail
  (liée à l'identité, pour le compte, pas pour la pub).

## 7. Politique de confidentialité (`src/game/legal.ts`) : à compléter au branchement

Elle parle déjà du compte « lié à ton compte Apple ou Google si tu le choisis » et de Supabase. Ajouter :

- l'**adresse e-mail** reçue de Google ou Apple (et le fait qu'Apple peut donner une adresse relais « masquée ») ;
- le **nom du fournisseur** et l'**identifiant** du compte ; aucun mot de passe n'est reçu par le jeu ;
- le but : sauvegarde en ligne, retrouver sa partie sur un autre téléphone ;
- l'hébergeur (Supabase, région Europe) ; la durée (tant que le compte existe) ; la suppression (Réglages) ;
- le lien de la politique en ligne (à donner aussi à Google « Branding » et à Apple « App Privacy »).

## 8. Ce que Claude fera quand tu auras créé les comptes

1. Vérifier (sans rien modifier dans Supabase sans ton accord) que les fournisseurs sont bien réglés, et essayer la
   connexion sur le site de test : Google, Apple, retour au jeu, ligne du compte dans les Réglages.
2. Ajuster `auth-supabase.ts` si l'API de Supabase a changé (ou passer à `@supabase/supabase-js` en import dynamique).
3. Étape 3 (serveur) : tables `players` et `saves` avec règles de sécurité (chaque joueur ne lit que sa ligne),
   envoi de la partie invitée à la liaison, fenêtre « quelle partie garder ? », fonctions du serveur pour les actions
   (le serveur juge), suppression du compte en ligne (et révocation Apple).
4. Compléter la politique de confidentialité (§7) et mettre en ligne la page de suppression de compte.
5. Application (Capacitor) : modules natifs Google / Apple, Bundle ID, capacités Xcode, clients iOS / Android
   (§3), puis essais sur un vrai téléphone.
6. Rappel : la clé Apple « Secret Key (for OAuth) » expire tous les 6 mois.
