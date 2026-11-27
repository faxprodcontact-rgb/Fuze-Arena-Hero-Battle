// Courrier de l'équipe : messages (avec ou sans cadeau) envoyés aux joueurs.
// Pour envoyer un message : l'ajouter ici avec un `id` unique (jamais réutilisé) et une date d'envoi.
// Avec le serveur, ces messages viendront de la base (et pourront viser un seul joueur).
import type { Reward } from './modes';

export interface MailDef {
  id: string;
  /** Date d'envoi (ISO). Un message n'arrive qu'à partir de cette date. `null` = dès la création du compte. */
  at: string | null;
  title: { fr: string; en: string };
  body: { fr: string; en: string };
  reward?: Reward;
  /** Le cadeau dépend du joueur : il est rangé dans sa sauvegarde (`mail.personal`), le message n'arrive que s'il y en a un. */
  personal?: boolean;
}

export const MAILS: MailDef[] = [
  {
    id: 'welcome',
    at: null,
    title: { fr: 'Bienvenue !', en: 'Welcome!' },
    body: {
      fr: 'Bienvenue dans Fuze Arena – Hero Battle. Voici de quoi bien commencer. Bonne aventure !',
      en: 'Welcome to Fuze Arena – Hero Battle. Here is something to get you started. Have fun!',
    },
    reward: { gems: 500, scrolls: 5 },
  },
  {
    id: 'test-site',
    at: '2026-11-19T00:00:00Z',
    title: { fr: 'Version de test', en: 'Test version' },
    body: {
      fr: 'Merci de tester le jeu ! Tout peut encore changer : les dessins sont provisoires et les réglages seront revus avant la bêta.',
      en: 'Thanks for testing the game! Everything can still change: art is temporary and balance will be reviewed before the beta.',
    },
  },
  {
    // Cadeau personnel (state/migrate.ts) : seulement dans les vieilles sauvegardes qui avaient des héros retirés.
    id: 'heros-retires-2611',
    at: null,
    personal: true,
    title: { fr: 'Nouveaux héros', en: 'New heroes' },
    body: {
      fr: 'Le jeu garde désormais 36 héros, tous redessinés. Les héros retirés de ta collection sont échangés contre ce cadeau ; leurs niveaux et leur équipement te sont rendus.',
      en: 'The game now keeps 36 heroes, all redrawn. The heroes removed from your collection are exchanged for this gift; their levels and gear are given back.',
    },
  },
  {
    // Le portail spécial et sa monnaie, le parchemin d’événement (rouge) (27/11/2026) : de quoi l'essayer tout de suite
    id: 'parchemins-rouges-2711',
    at: '2026-11-27T00:00:00Z',
    title: { fr: 'Le portail d’événement', en: 'The Event Portal' },
    body: {
      fr: 'Un nouveau portail s\'ouvre : ses Légendaires sont les dragons. Il s\'ouvre avec des parchemins d\'événement, en voici pour commencer.',
      en: 'A new portal opens: its Legendaries are the dragons. It opens with event scrolls; here are some to start.',
    },
    reward: { redScrolls: 10 },
  },
];

/** Un message reste 30 jours dans la boîte. */
export const MAIL_KEEP_DAYS = 30;
