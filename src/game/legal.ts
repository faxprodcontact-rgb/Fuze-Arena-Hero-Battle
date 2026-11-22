// Pages légales et d'information (BROUILLONS). Avant la sortie sur l'App Store et Google Play :
// compléter les champs [À COMPLÉTER] et faire relire par un professionnel.
// Chaque page = une liste de blocs : un titre (h) ou un paragraphe (p).

export type LegalDoc = 'privacy' | 'terms' | 'notice' | 'credits';
type Block = { h: string } | { p: string };

const FR: Record<LegalDoc, Block[]> = {
  privacy: [
    { p: 'Brouillon — version de test.' },
    { h: 'Qui sommes-nous' },
    { p: "Fuze Arena – Hero Battle est édité par [À COMPLÉTER : nom ou société, adresse]. Contact : [À COMPLÉTER : adresse e-mail d'assistance]." },
    { h: 'Données collectées' },
    { p: "Un identifiant de compte (anonyme, ou lié à ton compte Apple ou Google si tu le choisis), ton nom de joueur, ta progression dans le jeu, tes achats dans le jeu, tes messages dans le tchat, et des statistiques d'utilisation (pages vues, durée des sessions)." },
    { p: "Publicité : uniquement si tu choisis de regarder une pub, et seulement avec ton accord pour le suivi publicitaire." },
    { h: 'Pourquoi' },
    { p: "Faire fonctionner le jeu et sauvegarder ta partie, gérer les achats, modérer le tchat, améliorer le jeu, et afficher les publicités que tu choisis de regarder." },
    { h: 'Durée de conservation' },
    { p: "Tant que ton compte existe. Si tu supprimes ton compte (Réglages → Supprimer mon compte), tes données sont effacées dans un délai de 30 jours, sauf obligation légale (par exemple les factures)." },
    { h: 'Tes droits' },
    { p: "Tu peux demander l'accès, la correction, la suppression ou l'export de tes données, et retirer ton accord à tout moment, en écrivant à [À COMPLÉTER]. Tu peux aussi saisir la CNIL (www.cnil.fr)." },
    { h: 'Mineurs' },
    { p: "Les moins de 15 ans doivent avoir l'accord d'un parent pour la publicité personnalisée et les achats." },
    { h: 'Prestataires' },
    { p: "Hébergement des données : Supabase. Achats : Apple, Google et RevenueCat. Publicité : Google AdMob. Chacun traite les données selon sa propre politique de confidentialité." },
  ],
  terms: [
    { p: 'Brouillon — version de test.' },
    { h: 'Utilisation du jeu' },
    { p: "Le jeu est gratuit. Tu reçois un droit personnel d'y jouer ; le jeu, ses personnages et ses dessins restent la propriété de l'éditeur." },
    { h: 'Compte' },
    { p: "Un compte par personne. Ne partage pas ton compte. Tricher, utiliser des programmes automatiques ou exploiter un bug peut entraîner la suspension du compte." },
    { h: 'Achats dans le jeu' },
    { p: "Les gemmes et objets virtuels n'ont pas de valeur en argent réel et ne sont ni échangeables ni remboursables, sauf si la loi l'impose. Les achats passent par Apple ou Google, selon leurs conditions." },
    { h: 'Invocations' },
    { p: "Les chances de chaque invocation sont affichées dans le jeu (Invoquer → Chances, ou Réglages → Chances d'invocation)." },
    { h: 'Tchat et comportement' },
    { p: "Pas d'insultes, de harcèlement, de contenu choquant, de publicité ni de partage d'informations personnelles. Tu peux signaler ou bloquer un joueur. Les messages signalés peuvent être lus par la modération." },
    { h: 'Modifications' },
    { p: "Le jeu et ces conditions peuvent évoluer. En cas de changement important, tu seras prévenu dans le jeu." },
    { h: 'Contact' },
    { p: '[À COMPLÉTER : adresse e-mail d’assistance]' },
  ],
  notice: [
    { p: 'Brouillon — version de test.' },
    { h: 'Éditeur' },
    { p: '[À COMPLÉTER : nom ou raison sociale, statut (ex. micro-entreprise), numéro SIRET, adresse, e-mail]' },
    { h: 'Directeur de la publication' },
    { p: '[À COMPLÉTER]' },
    { h: 'Hébergement' },
    { p: "Site de test : GitHub Pages (GitHub, Inc., San Francisco, États-Unis). Serveur du jeu : Supabase. Applications : App Store (Apple) et Google Play (Google)." },
  ],
  credits: [
    { h: 'Conception' },
    { p: "[À COMPLÉTER : ton nom ou ton studio]" },
    { h: 'Développement' },
    { p: "Réalisé avec l'aide de Claude (Anthropic)." },
    { h: 'Outils libres' },
    { p: 'Phaser (licence MIT), Preact (licence MIT), Vite (licence MIT).' },
    { h: 'Polices' },
    { p: 'Lilita One et Fredoka (SIL Open Font License).' },
  ],
};

const EN: Record<LegalDoc, Block[]> = {
  privacy: [
    { p: 'Draft — test version.' },
    { h: 'Who we are' },
    { p: 'Fuze Arena – Hero Battle is published by [TO COMPLETE: name or company, address]. Contact: [TO COMPLETE: support e-mail].' },
    { h: 'Data we collect' },
    { p: 'An account ID (anonymous, or linked to your Apple or Google account if you choose), your player name, your game progress, your in-game purchases, your chat messages, and usage statistics (screens viewed, session length).' },
    { p: 'Advertising: only if you choose to watch an ad, and only with your consent to ad tracking.' },
    { h: 'Why' },
    { p: 'To run the game and save your progress, process purchases, moderate the chat, improve the game, and show the ads you choose to watch.' },
    { h: 'Retention' },
    { p: 'As long as your account exists. If you delete your account (Settings → Delete my account), your data is erased within 30 days, except where the law requires otherwise (e.g. invoices).' },
    { h: 'Your rights' },
    { p: 'You can request access, correction, deletion or export of your data, and withdraw consent at any time, by writing to [TO COMPLETE].' },
    { h: 'Children' },
    { p: 'Players under 15 need a parent’s consent for personalised ads and purchases.' },
    { h: 'Service providers' },
    { p: 'Data hosting: Supabase. Purchases: Apple, Google and RevenueCat. Advertising: Google AdMob. Each processes data under its own privacy policy.' },
  ],
  terms: [
    { p: 'Draft — test version.' },
    { h: 'Using the game' },
    { p: 'The game is free. You get a personal right to play it; the game, its characters and artwork remain the publisher’s property.' },
    { h: 'Account' },
    { p: 'One account per person. Do not share your account. Cheating, bots or exploiting bugs may lead to suspension.' },
    { h: 'In-game purchases' },
    { p: 'Gems and virtual items have no real-money value and are neither transferable nor refundable, except where the law requires. Purchases go through Apple or Google under their terms.' },
    { h: 'Summons' },
    { p: 'The odds of every summon are shown in the game (Summon → Odds, or Settings → Summon odds).' },
    { h: 'Chat and behaviour' },
    { p: 'No insults, harassment, offensive content, advertising or sharing of personal information. You can report or block a player. Reported messages may be read by moderators.' },
    { h: 'Changes' },
    { p: 'The game and these terms may change. You will be told in the game about important changes.' },
    { h: 'Contact' },
    { p: '[TO COMPLETE: support e-mail]' },
  ],
  notice: [
    { p: 'Draft — test version.' },
    { h: 'Publisher' },
    { p: '[TO COMPLETE: name or company, legal status, registration number, address, e-mail]' },
    { h: 'Hosting' },
    { p: 'Test site: GitHub Pages (GitHub, Inc., San Francisco, USA). Game server: Supabase. Apps: App Store (Apple) and Google Play (Google).' },
  ],
  credits: [
    { h: 'Design' },
    { p: '[TO COMPLETE: your name or studio]' },
    { h: 'Development' },
    { p: 'Made with the help of Claude (Anthropic).' },
    { h: 'Open-source tools' },
    { p: 'Phaser (MIT licence), Preact (MIT licence), Vite (MIT licence).' },
    { h: 'Fonts' },
    { p: 'Lilita One and Fredoka (SIL Open Font License).' },
  ],
};

export function legalDoc(doc: LegalDoc, lang: 'fr' | 'en'): Block[] {
  return (lang === 'en' ? EN : FR)[doc];
}
