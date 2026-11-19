// Textes du jeu en français et en anglais. Règle : pas de phrase évidente, des mots courts.
// `{n}` dans un texte est remplacé par la valeur donnée.
import { getState } from './state/store';

const FR = {
  'nav.campaign': 'Campagne', 'nav.heroes': 'Héros', 'nav.summon': 'Invoquer', 'nav.adventure': 'Aventure', 'nav.guild': 'Guilde',
  'side.quests': 'Quêtes', 'side.shop': 'Boutique', 'side.pass': 'Passe', 'side.ranking': 'Classement', 'side.chat': 'Tchat', 'side.settings': 'Réglages',

  'cur.dust': 'Poussière de forge', 'forge.title': 'Forge', 'fusion.title': 'Fusion', cancel: 'Annuler', 'fusion.choose': 'Choisir', 'reset.none': 'Aucun héros à réinitialiser', 'fusion.none': 'Aucun héros disponible',
  'recycle.count': '✓ {n}', 'recycle.confirm': 'Recycler',
  'bag.title': 'Sac', 'bag.forgeAll': 'Tout forger', 'bag.recycleLow': 'Recycler gris et verts', 'bag.empty': 'Sac vide',
  'bag.forged': '{n} objets forgés', 'bag.recycled': '+{n} poussière',
  'item.chapter': 'Chapitre {n}', 'item.forge': 'Forger', 'item.forgeNeed': '{have} / 3 identiques', 'item.recycle': 'Recycler',
  'item.unequip': 'Retirer', 'item.wornBy': 'Porté par {n}', 'item.equip': 'Équiper',
  'slot.upgrade': 'Renforcer', 'slot.level': 'Emplacement +{n}', 'slot.max': 'Renforcement maximum', 'slot.choose': 'Objets du sac',
  'cur.gold': 'Or', 'cur.essence': 'Essence', 'cur.gems': 'Gemmes', 'cur.scrolls': 'Parchemins', 'cur.basicScrolls': 'Parchemins simples',
  'cur.arenaTokens': "Jetons d'arène", 'cur.guildCoins': 'Pièces de guilde', 'cur.crystals': "Cristaux d'éveil", 'cur.fragments': 'Fragments',

  fight: 'Combattre', collect: 'Récolter', claim: 'Récupérer', claimed: 'Reçu', buy: 'Acheter', free: 'Gratuit', close: 'Fermer',
  back: 'Retour', ok: 'OK', yes: 'Oui', no: 'Non', auto: 'Auto', max: 'MAX', power: 'Force', lv: 'Niv.', stage: 'Niveau',
  chapter: 'Chapitre', locked: 'Niveau {n}', soon: 'Bientôt', left: '{n} restants', send: 'Envoyer', all: 'Tous', new: 'Nouveau',
  required: 'Demandé', ad: 'Pub',

  'camp.loot': 'Butin', 'camp.perHour': '/ h', 'camp.fast': 'Butin rapide', 'camp.adBoost': '+2 h', 'camp.next': 'Niveau suivant',
  'camp.done': 'Campagne terminée', 'camp.boss': 'Boss',

  'heroes.team': 'Section', 'heroes.autoTeam': 'Meilleure section', 'heroes.fuseAll': 'Tout fusionner', 'heroes.fused': '{n} fusions',
  'heroes.full': 'Section complète', 'sort.power': 'Force', 'sort.stars': 'Étoiles', 'sort.rarity': 'Rareté', 'heroes.inTeam': 'Retirer de la section', 'heroes.addTeam': 'Ajouter à la section',

  'detail.levelUp': 'Niveau +1', 'detail.levelUp10': '+10', 'detail.cap': 'Niveau max : plus d’étoiles', 'detail.stars': 'Étoiles',
  'detail.copies': 'Copies : {have} / {need}', 'detail.fodder': 'Héros ★{s} de la faction : {have} / {need}',
  'detail.crystals': 'Cristaux : {have} / {need}', 'detail.fuse': 'Fusionner', 'detail.maxStars': 'Étoiles au maximum',
  'detail.triple': '3 héros identiques : {have} / 3', 'detail.equip': 'Équipement', 'detail.autoEquip': 'Équiper le meilleur',
  'detail.unequip': 'Tout retirer', 'detail.reset': 'Réinitialiser', 'detail.hp': 'PV', 'detail.atk': 'ATQ', 'detail.def': 'DÉF',
  'detail.skill': 'Compétence', 'detail.leader': 'Chef de section',

  'rarity.common': 'Commun', 'rarity.rare': 'Rare', 'rarity.epic': 'Épique', 'rarity.legendary': 'Légendaire', 'rarity.mythic': 'Mythique',
  'role.protector': 'Protecteur', 'role.attacker': 'Attaquant', 'role.healer': 'Soigneur', 'role.support': 'Soutien',
  'faction.knights': 'Chevaliers', 'faction.assassins': 'Assassins', 'faction.mages': 'Mages', 'faction.demons': 'Démons',
  'faction.angels': 'Anges', 'faction.myths': 'Mythes',
  'element.fire': 'Feu', 'element.wind': 'Vent', 'element.water': 'Eau', 'element.earth': 'Terre',
  'slot.weapon': 'Arme', 'slot.armor': 'Armure', 'slot.helmet': 'Casque', 'slot.boots': 'Bottes',
  'item.0': 'Gris', 'item.1': 'Vert', 'item.2': 'Bleu', 'item.3': 'Violet', 'item.4': 'Or', 'item.5': 'Rouge',

  'talent.atkMult': 'Attaque +{n} %', 'talent.defMult': 'Défense +{n} %', 'talent.intervalMult': "Vitesse d'attaque +{n} %",
  'talent.energyMult': 'Énergie +{n} %', 'talent.startEnergy': 'Jauges à {n} % au départ',

  'skill.rampart': 'Rempart', 'skill.quake': 'Séisme', 'skill.light': 'Lumière', 'skill.thunder': 'Tonnerre', 'skill.firestorm': 'Déluge',
  'skill.snipe': 'Tir précis', 'skill.slash': 'Taillade', 'skill.bite': 'Morsure', 'skill.shadowblade': "Lame d'ombre",
  'skill.mend': 'Soin', 'skill.crush': 'Écrasement', 'skill.doom': 'Fléau',
  'skilltext.shieldAll': 'Bouclier sur toute la section', 'skilltext.smash': 'Frappe toute la première ligne',
  'skilltext.healAll': 'Soigne toute la section', 'skilltext.stunFront': 'Étourdit la première ligne', 'skilltext.aoe': 'Frappe tous les ennemis',
  'skilltext.strikeBack': "Frappe l'arrière le plus fragile", 'skilltext.strike': 'Gros coup sur l’avant', 'skilltext.drain': 'Frappe et se soigne',

  'monster.goblin': 'Gobelin', 'monster.wolf': 'Loup', 'monster.golem': 'Golem', 'monster.archer': 'Archer', 'monster.shaman': 'Chaman',
  'monster.wraith': 'Spectre', 'monster.ogre': 'Ogre', 'monster.lich': 'Liche', 'monster.dragon': 'Dragon',

  'summon.normal': 'Invocation', 'summon.basic': 'Invocation simple', 'summon.x1': '×1', 'summon.x10': '×10',
  'summon.pity': 'Légendaire garanti dans {n}', 'summon.odds': 'Chances', 'summon.adFree': 'Invocation gratuite',
  'summon.fragments': 'Fragments', 'summon.copy': 'Obtenir une copie', 'summon.target': 'Cible des fragments',

  'adv.tower': 'Tour des Épreuves', 'adv.dungeons': 'Donjons', 'adv.missions': 'Missions', 'adv.dailyBoss': 'Boss du jour',
  'adv.arena': 'Arène', 'adv.defense': 'Défense',
  'tower.floor': 'Étage {n}', 'tower.challenge': 'Défier',
  'dungeon.gold': "Mine d'or", 'dungeon.essence': "Source d'essence", 'dungeon.gear': 'Forge', 'dungeon.tier': 'Difficulté {n}',
  'dungeon.closed': 'Fermé aujourd’hui', 'dungeon.entries': 'Entrées : {n} / {m}',
  'mission.patrol': 'Patrouille', 'mission.escort': 'Escorte', 'mission.ruins': 'Ruines', 'mission.hunt': 'Chasse',
  'mission.relic': 'Relique', 'mission.siege': 'Siège', 'mission.need': '{n} héros ★{s}+', 'mission.missing': 'Héros insuffisants',
  'boss.best': 'Record', 'boss.attempts': 'Essais : {n} / {m}', 'boss.attack': 'Attaquer',
  'arena.points': 'Points', 'arena.tickets': 'Combats : {n} / {m}', 'arena.refresh': 'Autres adversaires', 'arena.shop': 'Boutique',
  'league.bronze': 'Bronze', 'league.silver': 'Argent', 'league.gold': 'Or', 'league.platinum': 'Platine', 'league.diamond': 'Diamant',
  'defense.text': 'Place tes héros autour du chemin.',

  'guild.join': 'Rejoindre', 'guild.leave': 'Quitter', 'guild.members': 'Membres', 'guild.boss': 'Boss', 'guild.chat': 'Tchat',
  'guild.shop': 'Boutique', 'guild.total': 'Dégâts de la guilde', 'guild.level': 'Niv. {n}',

  'quests.daily': 'Du jour', 'quests.weekly': 'De la semaine', 'quests.activity': 'Activité',
  'quest.login': 'Connexion', 'quest.collectIdle': 'Récolter le butin', 'quest.winStage': 'Gagner en campagne', 'quest.summon': 'Invoquer',
  'quest.levelUp': 'Monter des niveaux', 'quest.fuse': 'Fusionner', 'quest.tower': 'Étages de la tour', 'quest.dungeon': 'Donjon',
  'quest.mission': 'Missions', 'quest.dailyBoss': 'Boss du jour', 'quest.arena': 'Combats d’arène', 'quest.guildBoss': 'Boss de guilde',
  'quest.watchAd': 'Pub',

  'shop.offers': 'Offres', 'shop.gems': 'Gemmes', 'shop.pass': 'Passe', 'shop.exchange': 'Échanges', 'shop.simulated': 'Achat simulé (prototype)',
  'offer.starter': 'Offre de départ', 'offer.growth': 'Pack de croissance', 'offer.card': 'Carte mensuelle', 'offer.pass': 'Passe premium',
  'offer.noads': 'Sans pub', 'offer.card.desc': '+100 gemmes par jour, 30 jours', 'offer.noads.desc': 'Bonus des pubs sans les regarder',
  'offer.daysLeft': '{n} j restants', 'offer.owned': 'Acheté',
  'pass.level': 'Palier {n}', 'pass.free': 'Gratuit', 'pass.premium': 'Premium', 'pass.points': '{n} / {m} points',

  'rank.campaign': 'Campagne', 'rank.power': 'Force', 'rank.arena': 'Arène', 'rank.you': 'Toi',

  'settings.account': 'Compte', 'settings.rename': 'Changer', 'settings.id': 'Identifiant', 'settings.game': 'Jeu',
  'settings.sound': 'Sons', 'settings.music': 'Musique', 'settings.notifications': 'Notifications', 'settings.info': 'Informations',
  'settings.delete': 'Supprimer mon compte', 'settings.deleteConfirm': 'Supprimer ton compte et toute ta progression ?',
  'settings.deleteConfirm2': 'Vraiment ? Rien ne pourra être récupéré.', 'settings.version': 'Version',
  'legal.privacy': 'Politique de confidentialité', 'legal.terms': "Conditions d'utilisation", 'legal.notice': 'Mentions légales',
  'legal.credits': 'Crédits', 'legal.support': 'Assistance',
  'legal.supportText': 'Un problème ou une question ? Écris-nous en donnant ton identifiant de joueur.',
  'legal.supportContact': 'Adresse de contact : à venir.',
  'name.title': 'Ton nom', 'name.random': 'Nom au hasard', 'name.rule': '3 à 16 caractères',
  'name.length': '3 à 16 caractères', 'name.chars': 'Lettres, chiffres, espaces, - et _ seulement', 'name.taken': 'Nom non autorisé',
  'name.gems': 'Pas assez de gemmes',
  'settings.name': 'Nom', 'settings.lang': 'Langue', 'settings.speed': 'Vitesse des combats', 'settings.tests': 'Outils de test',
  'settings.h2': '+2 h', 'settings.h12': '+12 h', 'settings.d1': '+1 jour', 'settings.resources': 'Ressources',
  'settings.unlock': 'Tout débloquer', 'settings.reset': 'Recommencer', 'settings.resetConfirm': 'Effacer la partie ?',

  'result.victory': 'Victoire !', 'result.defeat': 'Défaite', 'result.damage': 'Dégâts', 'result.nothing': 'Rien cette fois',
  'battle.quit': 'Quitter', 'battle.wave': 'Vague', 'battle.auto': 'AUTO',
  'mode.campaign': 'Niveau', 'mode.tower': 'Étage', 'mode.dungeon': 'Donjon', 'mode.dailyBoss': 'Boss', 'mode.arena': 'Arène', 'mode.guildBoss': 'Guilde',
  'new.feature': 'Débloqué !',
};

type Key = keyof typeof FR;

const EN: Record<Key, string> = {
  'nav.campaign': 'Campaign', 'nav.heroes': 'Heroes', 'nav.summon': 'Summon', 'nav.adventure': 'Adventure', 'nav.guild': 'Guild',
  'side.quests': 'Quests', 'side.shop': 'Shop', 'side.pass': 'Pass', 'side.ranking': 'Ranking', 'side.chat': 'Chat', 'side.settings': 'Settings',

  'cur.dust': 'Forge dust', 'forge.title': 'Forge', 'fusion.title': 'Fusion', cancel: 'Cancel', 'fusion.choose': 'Choose', 'reset.none': 'No hero to reset', 'fusion.none': 'No hero available',
  'recycle.count': '✓ {n}', 'recycle.confirm': 'Recycle',
  'bag.title': 'Bag', 'bag.forgeAll': 'Forge all', 'bag.recycleLow': 'Recycle grey and green', 'bag.empty': 'Bag empty',
  'bag.forged': '{n} items forged', 'bag.recycled': '+{n} dust',
  'item.chapter': 'Chapter {n}', 'item.forge': 'Forge', 'item.forgeNeed': '{have} / 3 identical', 'item.recycle': 'Recycle',
  'item.unequip': 'Remove', 'item.wornBy': 'Worn by {n}', 'item.equip': 'Equip',
  'slot.upgrade': 'Upgrade', 'slot.level': 'Slot +{n}', 'slot.max': 'Max upgrade', 'slot.choose': 'Items in bag',
  'cur.gold': 'Gold', 'cur.essence': 'Essence', 'cur.gems': 'Gems', 'cur.scrolls': 'Scrolls', 'cur.basicScrolls': 'Basic scrolls',
  'cur.arenaTokens': 'Arena tokens', 'cur.guildCoins': 'Guild coins', 'cur.crystals': 'Awakening crystals', 'cur.fragments': 'Shards',

  fight: 'Fight', collect: 'Collect', claim: 'Claim', claimed: 'Claimed', buy: 'Buy', free: 'Free', close: 'Close',
  back: 'Back', ok: 'OK', yes: 'Yes', no: 'No', auto: 'Auto', max: 'MAX', power: 'Power', lv: 'Lv.', stage: 'Stage',
  chapter: 'Chapter', locked: 'Stage {n}', soon: 'Soon', left: '{n} left', send: 'Send', all: 'All', new: 'New',
  required: 'Required', ad: 'Ad',

  'camp.loot': 'Loot', 'camp.perHour': '/ h', 'camp.fast': 'Fast loot', 'camp.adBoost': '+2 h', 'camp.next': 'Next stage',
  'camp.done': 'Campaign complete', 'camp.boss': 'Boss',

  'heroes.team': 'Squad', 'heroes.autoTeam': 'Best squad', 'heroes.fuseAll': 'Fuse all', 'heroes.fused': '{n} fusions',
  'heroes.full': 'Squad full', 'sort.power': 'Power', 'sort.stars': 'Stars', 'sort.rarity': 'Rarity', 'heroes.inTeam': 'Remove from squad', 'heroes.addTeam': 'Add to squad',

  'detail.levelUp': 'Level +1', 'detail.levelUp10': '+10', 'detail.cap': 'Max level: more stars needed', 'detail.stars': 'Stars',
  'detail.copies': 'Copies: {have} / {need}', 'detail.fodder': '★{s} heroes of the faction: {have} / {need}',
  'detail.crystals': 'Crystals: {have} / {need}', 'detail.fuse': 'Fuse', 'detail.maxStars': 'Max stars',
  'detail.triple': '3 identical heroes: {have} / 3', 'detail.equip': 'Gear', 'detail.autoEquip': 'Equip best',
  'detail.unequip': 'Remove all', 'detail.reset': 'Reset', 'detail.hp': 'HP', 'detail.atk': 'ATK', 'detail.def': 'DEF',
  'detail.skill': 'Skill', 'detail.leader': 'Squad leader',

  'rarity.common': 'Common', 'rarity.rare': 'Rare', 'rarity.epic': 'Epic', 'rarity.legendary': 'Legendary', 'rarity.mythic': 'Mythic',
  'role.protector': 'Protector', 'role.attacker': 'Attacker', 'role.healer': 'Healer', 'role.support': 'Support',
  'faction.knights': 'Knights', 'faction.assassins': 'Assassins', 'faction.mages': 'Mages', 'faction.demons': 'Demons',
  'faction.angels': 'Angels', 'faction.myths': 'Myths',
  'element.fire': 'Fire', 'element.wind': 'Wind', 'element.water': 'Water', 'element.earth': 'Earth',
  'slot.weapon': 'Weapon', 'slot.armor': 'Armor', 'slot.helmet': 'Helmet', 'slot.boots': 'Boots',
  'item.0': 'Grey', 'item.1': 'Green', 'item.2': 'Blue', 'item.3': 'Purple', 'item.4': 'Gold', 'item.5': 'Red',

  'talent.atkMult': 'Attack +{n}%', 'talent.defMult': 'Defense +{n}%', 'talent.intervalMult': 'Attack speed +{n}%',
  'talent.energyMult': 'Energy +{n}%', 'talent.startEnergy': 'Gauges start at {n}%',

  'skill.rampart': 'Rampart', 'skill.quake': 'Quake', 'skill.light': 'Radiance', 'skill.thunder': 'Thunder', 'skill.firestorm': 'Deluge',
  'skill.snipe': 'Snipe', 'skill.slash': 'Slash', 'skill.bite': 'Bite', 'skill.shadowblade': 'Shadow Blade',
  'skill.mend': 'Mend', 'skill.crush': 'Crush', 'skill.doom': 'Doom',
  'skilltext.shieldAll': 'Shields the whole squad', 'skilltext.smash': 'Hits the whole front row',
  'skilltext.healAll': 'Heals the whole squad', 'skilltext.stunFront': 'Stuns the front row', 'skilltext.aoe': 'Hits all enemies',
  'skilltext.strikeBack': 'Hits the weakest back-row enemy', 'skilltext.strike': 'Heavy hit on the front', 'skilltext.drain': 'Hits and heals itself',

  'monster.goblin': 'Goblin', 'monster.wolf': 'Wolf', 'monster.golem': 'Golem', 'monster.archer': 'Archer', 'monster.shaman': 'Shaman',
  'monster.wraith': 'Wraith', 'monster.ogre': 'Ogre', 'monster.lich': 'Lich', 'monster.dragon': 'Dragon',

  'summon.normal': 'Summon', 'summon.basic': 'Basic summon', 'summon.x1': '×1', 'summon.x10': '×10',
  'summon.pity': 'Legendary guaranteed in {n}', 'summon.odds': 'Odds', 'summon.adFree': 'Free summon',
  'summon.fragments': 'Shards', 'summon.copy': 'Get a copy', 'summon.target': 'Shard target',

  'adv.tower': 'Tower of Trials', 'adv.dungeons': 'Dungeons', 'adv.missions': 'Missions', 'adv.dailyBoss': 'Daily boss',
  'adv.arena': 'Arena', 'adv.defense': 'Defense',
  'tower.floor': 'Floor {n}', 'tower.challenge': 'Challenge',
  'dungeon.gold': 'Gold mine', 'dungeon.essence': 'Essence spring', 'dungeon.gear': 'Forge', 'dungeon.tier': 'Difficulty {n}',
  'dungeon.closed': 'Closed today', 'dungeon.entries': 'Entries: {n} / {m}',
  'mission.patrol': 'Patrol', 'mission.escort': 'Escort', 'mission.ruins': 'Ruins', 'mission.hunt': 'Hunt',
  'mission.relic': 'Relic', 'mission.siege': 'Siege', 'mission.need': '{n} heroes ★{s}+', 'mission.missing': 'Not enough heroes',
  'boss.best': 'Best', 'boss.attempts': 'Tries: {n} / {m}', 'boss.attack': 'Attack',
  'arena.points': 'Points', 'arena.tickets': 'Fights: {n} / {m}', 'arena.refresh': 'New opponents', 'arena.shop': 'Shop',
  'league.bronze': 'Bronze', 'league.silver': 'Silver', 'league.gold': 'Gold', 'league.platinum': 'Platinum', 'league.diamond': 'Diamond',
  'defense.text': 'Place your heroes around the path.',

  'guild.join': 'Join', 'guild.leave': 'Leave', 'guild.members': 'Members', 'guild.boss': 'Boss', 'guild.chat': 'Chat',
  'guild.shop': 'Shop', 'guild.total': 'Guild damage', 'guild.level': 'Lv. {n}',

  'quests.daily': 'Daily', 'quests.weekly': 'Weekly', 'quests.activity': 'Activity',
  'quest.login': 'Log in', 'quest.collectIdle': 'Collect loot', 'quest.winStage': 'Win campaign stages', 'quest.summon': 'Summon',
  'quest.levelUp': 'Level up heroes', 'quest.fuse': 'Fuse', 'quest.tower': 'Tower floors', 'quest.dungeon': 'Dungeon',
  'quest.mission': 'Missions', 'quest.dailyBoss': 'Daily boss', 'quest.arena': 'Arena fights', 'quest.guildBoss': 'Guild boss',
  'quest.watchAd': 'Ad',

  'shop.offers': 'Offers', 'shop.gems': 'Gems', 'shop.pass': 'Pass', 'shop.exchange': 'Exchange', 'shop.simulated': 'Simulated purchase (prototype)',
  'offer.starter': 'Starter pack', 'offer.growth': 'Growth pack', 'offer.card': 'Monthly card', 'offer.pass': 'Premium pass',
  'offer.noads': 'No ads', 'offer.card.desc': '+100 gems a day, 30 days', 'offer.noads.desc': 'Ad bonuses without watching',
  'offer.daysLeft': '{n} days left', 'offer.owned': 'Owned',
  'pass.level': 'Tier {n}', 'pass.free': 'Free', 'pass.premium': 'Premium', 'pass.points': '{n} / {m} points',

  'rank.campaign': 'Campaign', 'rank.power': 'Power', 'rank.arena': 'Arena', 'rank.you': 'You',

  'settings.account': 'Account', 'settings.rename': 'Change', 'settings.id': 'Player ID', 'settings.game': 'Game',
  'settings.sound': 'Sound', 'settings.music': 'Music', 'settings.notifications': 'Notifications', 'settings.info': 'Information',
  'settings.delete': 'Delete my account', 'settings.deleteConfirm': 'Delete your account and all your progress?',
  'settings.deleteConfirm2': 'Are you sure? Nothing can be recovered.', 'settings.version': 'Version',
  'legal.privacy': 'Privacy policy', 'legal.terms': 'Terms of use', 'legal.notice': 'Legal notice',
  'legal.credits': 'Credits', 'legal.support': 'Support',
  'legal.supportText': 'A problem or a question? Write to us with your player ID.',
  'legal.supportContact': 'Contact address: coming soon.',
  'name.title': 'Your name', 'name.random': 'Random name', 'name.rule': '3 to 16 characters',
  'name.length': '3 to 16 characters', 'name.chars': 'Letters, digits, spaces, - and _ only', 'name.taken': 'Name not allowed',
  'name.gems': 'Not enough gems',
  'settings.name': 'Name', 'settings.lang': 'Language', 'settings.speed': 'Battle speed', 'settings.tests': 'Test tools',
  'settings.h2': '+2 h', 'settings.h12': '+12 h', 'settings.d1': '+1 day', 'settings.resources': 'Resources',
  'settings.unlock': 'Unlock everything', 'settings.reset': 'Start over', 'settings.resetConfirm': 'Erase progress?',

  'result.victory': 'Victory!', 'result.defeat': 'Defeat', 'result.damage': 'Damage', 'result.nothing': 'Nothing this time',
  'battle.quit': 'Quit', 'battle.wave': 'Wave', 'battle.auto': 'AUTO',
  'mode.campaign': 'Stage', 'mode.tower': 'Floor', 'mode.dungeon': 'Dungeon', 'mode.dailyBoss': 'Boss', 'mode.arena': 'Arena', 'mode.guildBoss': 'Guild',
  'new.feature': 'Unlocked!',
};

export function t(key: Key | string, vars: Record<string, string | number> = {}): string {
  const table: Record<string, string> = getState().lang === 'en' ? EN : FR;
  let s = table[key] ?? FR[key as Key] ?? key;
  for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, String(v));
  return s;
}

export function fmt(n: number): string {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} G`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)} M`;
  if (n >= 1e4) return `${Math.floor(n / 1e3)} k`;
  return Math.floor(n).toLocaleString(getState().lang === 'en' ? 'en-US' : 'fr-FR');
}

/** Lignes de tchat des autres joueurs (prototype, sans serveur). */
export const CHAT_LINES = {
  fr: ['Quelqu’un a battu le boss du chapitre 5 ?', 'GG à tous pour le boss !', 'Je cherche une guilde active', 'Le Légendaire sort enfin 😄',
    'Astuce : mettez un protecteur devant', 'Qui fait la tour ce soir ?', 'Mon chef de section change tout', 'Encore 2 copies pour l’étoile rouge…',
    'Bienvenue aux nouveaux !', 'La forge donne de bons objets aujourd’hui'],
  en: ['Anyone beat the chapter 5 boss?', 'GG everyone on the boss!', 'Looking for an active guild', 'Finally pulled a Legendary 😄',
    'Tip: put a protector in front', 'Who is doing the tower tonight?', 'My squad leader changes everything', '2 more copies for the red star…',
    'Welcome newcomers!', 'The forge drops good gear today'],
};
