# Régie des Eaux Montpellier

[![GitHub Release][release-shield]][release] [![GitHub Activity][commits-shield]][commits] [![License][license-shield]](license)

**Intégration Home Assistant pour récupérer les index de consommation d'eau de la Régie des Eaux de Montpellier Méditerranée Métropole.**

## Fonctionnalités

- 🔐 **Authentification sécurisée** via l'API officielle de la Régie des Eaux
- 💧 **Support multi-compteurs** avec gestion individuelle
- ⚡ **Intégration native** au tableau de bord Énergie/Eau de Home Assistant
- 🔄 **Mise à jour automatique** configurable (de 30 min à 24h)
- 💾 **Restauration automatique** des dernières valeurs après un redémarrage
- 📊 **Historique des relevés** avec timestamp
- 🌐 **Interface de configuration** simple et intuitive

## Installation

### Via HACS (Recommandé)

1. Ouvrez **HACS** dans Home Assistant
2. Cliquez sur les **trois points** en haut à droite
3. Sélectionnez **"Dépôts personnalisés"**
4. Ajoutez ce dépôt : `https://github.com/iopsthecloud/regideseaux3m-hass`
5. Sélectionnez la catégorie **"Intégration"**
6. Cliquez sur **"Ajouter"**
7. Recherchez **"Régie des Eaux Montpellier"** dans HACS
8. Cliquez sur **"Télécharger"**
9. Redémarrez Home Assistant

### Manuellement

1. Téléchargez la dernière version depuis [Releases][release]
2. Décompressez le fichier ZIP
3. Copiez le dossier `custom_components/regiedeseauxmpl/` dans votre dossier `custom_components/` de Home Assistant
4. Redémarrez Home Assistant

## Configuration

1. Dans Home Assistant, allez dans **Paramètres → Appareils et services**
2. Cliquez sur **"Ajouter une intégration"**
3. Recherchez **"Régie des Eaux Montpellier"**
4. Saisissez vos identifiants de connexion (email et mot de passe)
5. Sélectionnez l'intervalle de mise à jour souhaité (par défaut : 6 heures)
6. Cliquez sur **"Soumettre"**

## Options de Configuration

Une fois l'intégration configurée, vous pouvez modifier les paramètres :

- **Intervalle de mise à jour** : De 30 minutes à 24 heures
- **Forcer le rafraîchissement** : Via le service `regiedeseauxmpl.refresh_meters`

## Entités Créées

Pour chaque compteur configuré, une entité sensor sera créée :

- **Domaine** : `sensor`
- **ID** : `sensor.regiedeseauxmpl_<short_name>_<serial>`
- **Exemple** : `sensor.regiedeseauxmpl_eau_potable_i23ia727517`
- **Nom** : Nom court du contrat (ex: "Eau potable")
- **Classe** : `water` (intégration au tableau de bord Énergie)
- **État** : Index en m³ (ex: `123.456`)
- **State Class** : `total_increasing` (compatible avec le suivi de consommation)

### Intégration avec le Tableau Énergie

✅ **Compatibilité totale** avec le tableau de bord Énergie de Home Assistant :
- Les entités apparaissent automatiquement dans **Énergie → Eau**
- Peuvent être utilisées comme **"Upstream devices"** pour d'autres appareils (lave-linge, etc.)
- Prise en charge native du suivi de consommation

### Attributs Disponibles

| Attribut | Description | Exemple |
|----------|-------------|---------|
| `friendly_name` | Nom du compteur | "Eau potable" |
| `last_updated` | Dernière mise à jour | "2024-05-20T14:30:00+02:00" |
| `last_reading` | Date du dernier relevé | "2024-05-20" |
| `contract_id` | ID du contrat | "CONTRAT12345" |
| `serial_number` | Numéro de série | "SN12345678" |
| `unit` | Unité de mesure | "m³" |

### Device Information

Chaque entité est associée à un **device** avec les informations suivantes :
- **Fabricant** : Régie des Eaux Montpellier 3M
- **Modèle** : Compteur <contract_id>
- **Numéro de série** : Numéro unique du compteur
- **Lié au** : Config entry de l'intégration

> **Note** : Les devices sont visibles dans **Paramètres → Appareils et services → Appareils**

## Services

### `regiedeseauxmpl.refresh_meters`

Forcer le rafraîchissement de toutes les données des compteurs.

**Exemple d'utilisation** :

```yaml
automation:
  - alias: "Rafraîchir les compteurs d'eau tous les matins"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: regiedeseauxmpl.refresh_meters
```

**Avec cibles** (pour rafraîchir un compteur spécifique) :

```yaml
service: regiedeseauxmpl.refresh_meters
  target:
    entity_id: sensor.regiedeseauxmpl_contract123
```

## Dépannage

### "Impossible de se connecter à l'API"

- Vérifiez votre connexion internet
- Assurez-vous que le site https://ael.regiedeseaux3m.fr est accessible
- Essayez de vous connecter manuellement sur le site web de la Régie des Eaux

### "Identifiants invalides"

- Vérifiez que votre email et mot de passe sont corrects
- Essayez de vous connecter sur le site web officiel
- Si vous avez changé votre mot de passe, mettez à jour la configuration dans Home Assistant

### "Aucun compteur trouvé"

- Vérifiez que votre compte a bien des contrats associés
- Contactez le service client de la Régie des Eaux

### Voir les logs

Pour diagnostiquer les problèmes :

1. Allez dans **Paramètres → Journaux**
2. Filtrez par `regiedeseauxmpl`
3. Activez le mode debug dans la configuration de l'intégration

## Contribuer

Les contributions sont les bienvenues !

- **Signaler un bug** : [Ouvrir une issue][issues]
- **Proposer une amélioration** : [Ouvrir une Pull Request][repo]
- **Traduire** : Aidez à traduire dans d'autres langues

## License

Ce projet est sous licence MIT. Voir [LICENSE][license] pour plus de détails.

[commits-shield]: https://img.shields.io/github/commit-activity/y/iopsthecloud/regideseaux3m-hass.svg?style=for-the-badge
[commits]: https://github.com/iopsthecloud/regideseaux3m-hass/commits/main
[license-shield]: https://img.shields.io/github/license/iopsthecloud/regideseaux3m-hass.svg?style=for-the-badge
[license]: https://github.com/iopsthecloud/regideseaux3m-hass/blob/main/LICENSE
[release-shield]: https://img.shields.io/github/release/iopsthecloud/regideseaux3m-hass.svg?style=for-the-badge
[release]: https://github.com/iopsthecloud/regideseaux3m-hass/releases
[repo]: https://github.com/iopsthecloud/regideseaux3m-hass
[issues]: https://github.com/iopsthecloud/regideseaux3m-hass/issues
