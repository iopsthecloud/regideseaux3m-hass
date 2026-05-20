# Régie des Eaux Montpellier

[![Open in my Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=iopsthecloud&repository=regideseaux3m-hass&category=integration) [![HACS][hacs-badge]][hacs] [![License: MIT][license-badge]][license] [![Python 3.14+][python-badge]] [![GitHub Release][release-badge]][release] [![GitHub Last Commit][last-commit-badge]][repo]

> **Intégration Home Assistant pour récupérer les index de consommation d'eau de la Régie des Eaux de Montpellier Méditerranée Métropole**

---

## 🏛️ **À Propos de la Régie des Eaux de Montpellier**

**La Régie des Eaux de Montpellier Méditerranée Métropole** est un **service public** géré par **Montpellier 3M** (Métropole de Montpellier), qui assure la gestion complète du cycle de l'eau pour les habitants et entreprises de son territoire.

### 🌍 **Territoire et Missions**

Cette intégration concerne **tous les usagers** de la Régie des Eaux de **Montpellier Méditerranée Métropole**, qui regroupe **31 communes** :

- Montpellier
- Castelnau-le-Lez
- Lattes
- Pérols
- Saint-Geniès-des-Mourguieres
- Fabrègues
- Lavérune
- Village-neuf
- Et les 23 autres communes de la métropole

**Missions principales :**
- ✅ **Distribution d'eau potable** - Fourniture d'eau de qualité
- ✅ **Gestion des abonnements** - Contrats et facturation
- ✅ **Suivi de la consommation** - Relevés de compteurs (manuels et télérelève)
- ✅ **Assainissement** - Collecte et traitement des eaux usées
- ✅ **Service client** - Accompagnement des usagers

### 💡 **Pourquoi cette Intégration ?**

La Régie des Eaux propose une **[agence en ligne](https://ael.regiedeseaux3m.fr/)** permettant aux usagers de consulter :
- Leurs **index de consommation** (relevés)
- Leur **historique de consommation**
- Leurs **contrats et factures**
- Le **paiement en ligne**

Cependant, **aucune API publique officielle** n'est proposée par la Régie des Eaux pour une intégration automatique avec des systèmes tiers comme Home Assistant.

**Notre solution :**
Cette intégration utilise **l'API interne** (découverte par reverse engineering) de l'agence en ligne pour **récupérer automatiquement vos données de consommation** directement dans Home Assistant.

**Avantages :**
- 📊 **Suivi en temps réel** de votre consommation d'eau
- 📈 **Intégration native** au tableau de bord **Énergie/Eau** de Home Assistant
- 🔄 **Mises à jour automatiques** (configurables de 30 min à 24h)
- 💾 **Historique préservé** même après un redémarrage de Home Assistant
- 🎯 **Création d'automatisations** basées sur votre consommation
- 📱 **Centralisation** de toutes vos données dans un seul outil

> ⚠️ **Important** : Cette intégration dépend de l'API interne de la Régie des Eaux. Si leur système évolue (changement d'URL, de protocole, etc.), l'intégration pourrait nécessiter une mise à jour. Nous nous engageons à maintenir cette intégration à jour **dans la mesure du possible**. Les contributeurs sont les bienvenus !

> 🔗 **Ressources officielles** :
> - [Site de la Régie des Eaux](https://regiedeseaux.montpellier3m.fr/)
> - [Agence en ligne (espace client)](https://ael.regiedeseaux3m.fr/)
> - [Montpellier 3M - Cycle de l'eau](https://www.montpellier3m.fr/vivre-cycles-de-leau)

---

## 📖 **Table des Matières**

- [🎯 Fonctionnalités](#-fonctionnalités)
- [📥 Installation](#-installation)
  - [Via HACS (Recommandé)](#via-hacs-recommandé)
  - [Installation manuelle](#installation-manuelle)
- [⚙️ Configuration](#-configuration)
  - [Première configuration](#première-configuration)
  - [Options avancées](#options-avancées)
  - [Configuration YAML (optionnelle)](#configuration-yaml-optionnelle)
- [📊 Entités créées](#-entités-créées)
- [🎨 Tableau de bord Énergie](#-tableau-de-bord-énergie)
- [🔧 Services disponibles](#-services-disponibles)
- [📝 Exemples d'automatisations](#-exemples-dautomatisations)
- [❓ Dépannage](#-dépannage)
  - [Erreurs courantes](#erreurs-courantes)
  - [Voir les logs](#voir-les-logs)
  - [Diagnostics](#diagnostics)
- [🛠️ Développement](#-développement)
  - [Prérequis](#prérequis)
  - [Environnement de développement](#environnement-de-développement)
  - [Structure du projet](#structure-du-projet)
- [🤝 Contribuer](#-contribuer)
- [📜 Licence](#-licence)
- [🙏 Remerciements](#-remerciements)

---

## 🎯 **Fonctionnalités**

| Fonctionnalité | Description |
|--------------|-------------|
| 🔐 **Authentification sécurisée** | Connexion via l'API officielle avec gestion des tokens (curl_cffi pour F5 BIG-IP) |
| 💧 **Multi-compteurs** | Support de tous vos contrats/compteurs d'eau |
| ⚡ **Intégration Énergie** | Intégration native au tableau de bord Énergie/Eau de Home Assistant |
| 🔄 **Mise à jour automatique** | Rafraîchissement configurable (30 min à 24h) |
| 💾 **Restauration automatique** | Les dernières valeurs persistent après un redémarrage (RestoreSensor) |
| 📊 **Historique** | Timestamp du dernier relevé pour chaque compteur |
| 🎨 **UI moderne** | Interface de configuration intuitive dans Home Assistant |
| 🔍 **Diagnostics** | Outils intégrés pour le dépannage (statut API, liste des compteurs) |
| 🔄 **Rafraîchissement manuel** | Service `regiedeseauxmpl.refresh_meters` pour forcer la mise à jour |
| 📱 **Notifications** | Possibilité de créer des alertes de consommation anormale |

---

## 📥 **Installation**

[![Open in my Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=iopsthecloud&repository=regideseaux3m-hass&category=integration)

### Via HACS (Recommandé) 🎉

1. **Ouvrez HACS** dans votre Home Assistant
   - Dans la barre latérale : **HACS** → ou via **Paramètres → HACS**

2. **Ajoutez le dépôt personnalisé**
   - Cliquez sur les **trois points (⋮)** en haut à droite
   - Sélectionnez **"Dépôts personnalisés"**
   - Ajoutez l'URL du dépôt : `https://github.com/iopsthecloud/regideseaux3m-hass`
   - Sélectionnez la catégorie : **"Intégration"**
   - Cliquez sur **"Ajouter"**

3. **Installez l'intégration**
   - Recherchez **"Régie des Eaux Montpellier"** dans l'onglet **Intégrations**
   - Cliquez sur **"Télécharger"**
   - Redémarrez Home Assistant

4. **Configurez l'intégration**
   - Allez dans **Paramètres → Appareils et services**
   - Cliquez sur **"Ajouter une intégration"**
   - Recherchez et sélectionnez **"Régie des Eaux Montpellier"**
   - Saisissez vos identifiants (email + mot de passe de l'agence en ligne)

### Installation manuelle

1. **Téléchargez la dernière version**
   - Allez dans les [Releases](https://github.com/iopsthecloud/regideseaux3m-hass/releases) de ce dépôt
   - Téléchargez le fichier `regiedeseauxmpl-*.zip`

2. **Décompressez le fichier**
   ```bash
   unzip regiedeseauxmpl-*.zip -d regiedeseauxmpl
   ```

3. **Copiez le dossier** dans votre installation Home Assistant
   ```bash
   # Sur la plupart des systèmes
   cp -r regiedeseauxmpl /config/custom_components/
   
   # Ou via l'interface de fichiers de Home Assistant
   # Ou via Samba/Partage réseau : copiez dans \\HASSIO\\config\\custom_components\\
   ```

4. **Redémarrez Home Assistant**

5. **Configurez l'intégration** (comme pour HACS)

---

## ⚙️ **Configuration**

### Première configuration

1. **Accédez à l'intégration**
   - **Paramètres → Appareils et services**
   - Cliquez sur **"Ajouter une intégration"**
   - Recherchez **"Régie des Eaux Montpellier"**

2. **Saisissez vos identifiants**
   - **Adresse email / Identifiant** : Votre email de connexion à [l'agence en ligne](https://ael.regiedeseaux3m.fr/)
   - **Mot de passe** : Votre mot de passe de l'agence en ligne
   - **Intervalle de mise à jour** : Fréquence de rafraîchissement (par défaut : 6 heures)

3. **Validez**
   - Cliquez sur **"Soumettre"**
   - L'intégration va tester la connexion avec l'API de la Régie des Eaux
   - Si tout va bien, vous serez redirigé vers la liste des appareils

### Options avancées

Une fois l'intégration configurée, vous pouvez modifier les paramètres :

1. **Changer l'intervalle de mise à jour**
   - Allez dans **Paramètres → Appareils et services**
   - Trouvez votre intégration **"Régie des Eaux Montpellier"**
   - Cliquez sur les **trois points (⋮)** → **"Options"**
   - Modifiez l'intervalle de mise à jour (30 min, 1h, 2h, 3h, 6h, 12h, 24h)
   - Sauvegardez

2. **Forcer un rafraîchissement manuel**
   - Via l'interface : **Développeur → Services** → `regiedeseauxmpl.refresh_meters`
   - Via une automatisation (voir [Exemples](#-exemples-dautomatisations))

---

## 📊 **Entités créées**

Pour chaque compteur configuré dans votre espace client, une **entité sensor** est créée automatiquement dans Home Assistant.

### Propriétés des entités

| Propriété | Valeur | Description |
|-----------|--------|-------------|
| **Domaine** | `sensor` | Type d'entité |
| **ID** | `sensor.regiedeseauxmpl_<contract_id>` | Identifiant unique basé sur le numéro de contrat |
| **Nom** | Nom du contrat | Ex: "Compteur Principal – 123 Rue de la Paix, 34000 Montpellier" |
| **Classe** | `water` | Intégration automatique au tableau de bord Énergie |
| **État** | `123.456` | Index en m³ (avec 3 décimales = litres) |
| **Unité** | `m³` | Unité de mesure |
| **Icône** | `mdi:water` | Icône dans l'interface |

### Attributs disponibles

| Attribut | Type | Exemple | Description |
|----------|------|---------|-------------|
| `friendly_name` | string | "Compteur Principal – 123 Rue de la Paix" | Nom complet du compteur |
| `last_updated` | datetime | "2024-05-20T14:30:00+02:00" | Dernière mise à jour par l'intégration |
| `last_reading` | date | "2024-05-20" | Date du dernier relevé officiel |
| `contract_id` | string | "CONTRAT12345" | Identifiant unique du contrat |
| `serial_number` | string | "SN12345678" | Numéro de série du compteur |
| `unit` | string | "m³" | Unité de mesure |

### Exemple d'entité

```yaml
# Exemple d'entité générée
sensor:
  - platform: regiedeseauxmpl
    entity_id: sensor.regiedeseauxmpl_contract12345
    name: "Compteur Principal – 123 Rue de la Paix"
    state: 1234.567
    unit_of_measurement: "m³"
    device_class: water
    state_class: total_increasing
    attributes:
      friendly_name: "Compteur Principal – 123 Rue de la Paix"
      last_updated: "2024-05-20T14:30:00+02:00"
      last_reading: "2024-05-20"
      contract_id: "CONTRAT12345"
      serial_number: "SN12345678"
      unit: "m³"
```

---

## 🎨 **Tableau de bord Énergie**

Vos entités sont **automatiquement intégrées** au tableau de bord **Énergie/Eau** de Home Assistant.

### Comment configurer :

1. **Accédez au tableau de bord Énergie**
   - Dans la barre latérale : **Tableau de bord → Énergie**

2. **Ajoutez vos compteurs**
   - Cliquez sur **"Ajouter un compteur"**
   - Sélectionnez vos entités `sensor.regiedeseauxmpl_*`
   - Choisissez le type **"Eau"**
   - Validez

3. **Visualisez votre consommation**
   - Graphiques de consommation sur différentes périodes (jour, semaine, mois, année)
   - Comparaison avec d'autres sources (électricité, gaz)
   - Statistiques de consommation
   - Historique détaillé

4. **(Optionnel) Configurez le coût**
   - Allez dans **Paramètres du tableau de bord Énergie**
   - Ajoutez le tarif de l'eau pour Montpellier (environ **4,15 €/m³** en 2024, tarif variable selon la commune)
   - L'intégration calculera automatiquement le coût de votre consommation

> 💡 **Astuce** : Le tarif de l'eau à Montpellier inclut la distribution, l'assainissement et les taxes. Consultez votre dernière facture pour le tarif exact.

---

## 🔧 **Services disponibles**

### `regiedeseauxmpl.refresh_meters`

Force un rafraîchissement immédiat de toutes les données des compteurs via l'API de la Régie des Eaux.

**Utilisation via l'interface** :
1. Allez dans **Développeur → Services**
2. Sélectionnez **`regiedeseauxmpl.refresh_meters`**
3. Cliquez sur **"Appeler le service"**

**Utilisation via YAML** :

```yaml
automation:
  - alias: "Rafraîchir les compteurs d'eau tous les jours à minuit"
    description: "Mise à jour quotidienne des index depuis l'API Régie des Eaux"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: regiedeseauxmpl.refresh_meters
        data:
          force: true

  - alias: "Rafraîchir un compteur spécifique avant une alerte"
    description: "Mise à jour ciblée avant vérification"
    trigger:
      - platform: event
        event_type: STATE_CHANGE
    action:
      - service: regiedeseauxmpl.refresh_meters
        target:
          entity_id: sensor.regiedeseauxmpl_contract12345
```

---

## 📝 **Exemples d'automatisations**

### 1. Notification de nouvelle lecture

Recevez une notification quand un nouveau relevé est disponible dans votre espace client.

```yaml
automation:
  - alias: "Notification nouvelle lecture d'eau"
    description: "Alertes quand les index sont mis à jour"
    mode: restart
    trigger:
      - platform: state
        entity_id:
          - sensor.regiedeseauxmpl_*
    condition:
      - condition: template
        value_template: >-
          {{ trigger.to_state.state != trigger.from_state.state }}
    action:
      - service: notify.notify
        data:
          title: "💧 Nouveau relevé d'eau"
          message: >-
            Compteur {{ trigger.entity_id.split('_')[-1] }}: 
            {{ "%.3f"|format(trigger.to_state.state|float) }} m³ 
            (Relevé le {{ trigger.to_state.attributes.last_reading }})
          data:
            priority: default
            tag: regie-eaux
```

### 2. Suivi de consommation quotidienne

Calculez et enregistrez votre consommation quotidienne.

```yaml
automation:
  - alias: "Suivi consommation quotidienne d'eau"
    description: "Journal de la consommation d'eau"
    trigger:
      - platform: time
        at: "23:55:00"
    action:
      - service: system_log.write
        data:
          message: >-
            Consommation du {{ now().strftime('%Y-%m-%d') }}:
            {% for state in states.sensor if 'regiedeseauxmpl' in state.entity_id %}
            • {{ state.name }}: {{ "%.3f"|format(state.state|float) }} m³
              (Dernière MAJ: {{ state.attributes.last_updated }})
            {% endfor %}
          level: info
          logger: regiedeseauxmpl.daily
```

### 3. Alerte de consommation anormale

Détectez une consommation inhabituellement élevée (ex: fuite).

```yaml
automation:
  - alias: "Alerte consommation d'eau anormale"
    description: "Détection de consommation excessive"
    trigger:
      - platform: numeric_state
        entity_id: sensor.regiedeseauxmpl_*
        above: 5  # Plus de 5 m³ en une seule mise à jour
    condition:
      - condition: template
        value_template: >-
          {{ trigger.to_state.attributes.last_reading != none }}
    action:
      - service: notify.notify
        data:
          title: "⚠️ Consommation d'eau anormale détectée"
          message: >-
            Compteur: {{ trigger.entity_id }}
            Consommation: {{ "%.3f"|format(trigger.to_state.state|float) }} m³
            Dernier relevé: {{ trigger.to_state.attributes.last_reading }}
            
            Cela représente une consommation élevée. Vérifiez les fuites !
          data:
            priority: high
            tag: regie-eaux-alert
            actions:
              - action: URI
                title: "Voir sur Régie des Eaux"
                uri: "https://ael.regiedeseaux3m.fr/"
```

### 4. Calcul du coût de la consommation

Calculez le coût de votre consommation en temps réel.

```yaml
# configuration.yaml
utility_meter:
  consommation_eau_quotidienne:
    source: sensor.regiedeseauxmpl_contract12345
    cycle: daily
    tariffs:
      - 4.15  # Tarif moyen à Montpellier en 2024 (€/m³)

sensor:
  - platform: template
    sensors:
      cout_eau_journalier:
        friendly_name: "Coût eau quotidien"
        unit_of_measurement: "€"
        value_template: >-
          {{ states("sensor.consummation_eau_quotidienne") | float * 4.15 | round(2) }}
```

---

## ❓ **Dépannage**

### 🚨 **Erreurs courantes et solutions**

#### ❌ **"Impossible de se connecter à l'API"**

**Causes possibles :**
- ❌ Problème de connexion internet
- ❌ Le site de la Régie des Eaux ([ael.regiedeseaux3m.fr](https://ael.regiedeseaux3m.fr/)) est indisponible
- ❌ Bloqué par un firewall ou un adblocker
- ❌ Problème temporaire avec le serveur F5 BIG-IP

**Solutions :**
- ✅ Vérifiez votre connexion internet
- ✅ Essayez d'accéder à [https://ael.regiedeseaux3m.fr](https://ael.regiedeseaux3m.fr/) dans votre navigateur
- ✅ Désactivez temporairement votre adblocker
- ✅ Vérifiez que votre Home Assistant a accès à internet
- ✅ Attendez 10-15 minutes et réessayez
- ✅ Consultez [l'état du service Régie des Eaux](https://regiedeseaux.montpellier3m.fr/) pour d'éventuelles maintenances

---

#### ❌ **"Identifiants invalides"**

**Causes possibles :**
- ❌ Email/mot de passe incorrect
- ❌ Votre compte a été désactivé
- ❌ Vous avez changé votre mot de passe récemment
- ❌ Problème de session expirée

**Solutions :**
- ✅ Vérifiez que vous utilisez le **bon email** (celui de l'agence en ligne)
- ✅ Essayez de vous connecter sur [l'agence en ligne](https://ael.regiedeseaux3m.fr/) pour confirmer vos identifiants
- ✅ Réinitialisez votre mot de passe via [ce lien](https://ael.regiedeseaux3m.fr/#/forgot-password)
- ✅ Supprimez et reconfigurez l'intégration avec les bons identifiants
- ✅ Attendez quelques minutes avant de réessayer (limite de tentatives)

---

#### ❌ **"Aucun compteur trouvé"**

**Causes possibles :**
- ❌ Votre compte n'a pas de contrats actifs associés
- ❌ Problème temporaire avec l'API de la Régie des Eaux
- ❌ Votre compte n'est pas encore activé

**Solutions :**
- ✅ Vérifiez que vous avez bien des contrats dans votre [espace client](https://ael.regiedeseaux3m.fr/)
- ✅ Contactez le **service client** au **04 67 15 71 71** ou via [le formulaire](https://regiedeseaux.montpellier3m.fr/contact-3m.php)
- ✅ Attendez quelques heures et réessayez
- ✅ Vérifiez que vous utilisez le bon compte (certains usagers ont plusieurs contrats)

---

#### ❌ **"Erreur de TLS/SSL" ou "F5 BIG-IP"**

Ceci est **normal** et **attendu** avec cette intégration.

**Explication :**
L'API de la Régie des Eaux utilise un **load balancer F5 BIG-IP** qui effectue du **TLS fingerprinting** pour bloquer les requêtes non-browsers. Cette intégration utilise **curl_cffi** avec **l'impersonation Chrome** pour contourner cette restriction.

- ✅ C'est **sécurisé** (curl_cffi est une bibliothèque Python standard)
- ✅ C'est **nécessaire** pour que l'API fonctionne
- ✅ Aucun risque pour vos données

---

#### ❌ **"Timeout" ou "Trop long à répondre"**

**Causes possibles :**
- ❌ Serveur de la Régie des Eaux surchargé
- ❌ Votre connexion internet est lente
- ❌ Problème de DNS

**Solutions :**
- ✅ Augmentez l'intervalle de mise à jour (ex: 12h au lieu de 1h)
- ✅ Vérifiez votre connexion internet
- ✅ Essayez à un autre moment de la journée

---

### 📋 **Voir les logs**

Pour diagnostiquer les problèmes :

1. **Via l'interface Home Assistant :**
   - Allez dans **Paramètres → Journaux**
   - Filtrez par `regiedeseauxmpl`

2. **Activez le mode debug :**
   ```yaml
   # configuration.yaml
   logger:
     default: info
     logs:
       custom_components.regiedeseauxmpl: debug
   ```

3. **Via SSH/Terminal :**
   ```bash
   # Pour Home Assistant OS
   ha logs --filter regiedeseauxmpl
   
   # Pour d'autres installations
   tail -f /config/home-assistant.log | grep regiedeseauxmpl
   ```

---

### 🔍 **Diagnostics intégrés**

L'intégration propose des outils de diagnostic :

1. **Via l'interface :**
   - Allez dans **Paramètres → Appareils et services**
   - Trouvez votre intégration **"Régie des Eaux Montpellier"**
   - Cliquez sur les **trois points (⋮)** → **"Diagnostics"**

2. **Informations disponibles :**
   - Statut de connexion à l'API
   - Liste des compteurs configurés
   - Dernières valeurs récupérées
   - État des tokens de session (masqués pour sécurité)
   - Dernière mise à jour

---

## 🛠️ **Développement**

### 📋 **Prérequis**

- Python **3.14+** (recommandé : 3.14)
- **uv** (pour la gestion des dépendances, recommandé) ou **pip**
- Git
- Un compte sur [l'agence en ligne de la Régie des Eaux](https://ael.regiedeseaux3m.fr/) pour les tests

### 🚀 **Environnement de développement**

#### Option 1 : Avec Make (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/iopsthecloud/regideseaux3m-hass.git
cd regiedeseauxmpl

# Créer l'environnement et installer les dépendances
make setup

# Activer l'environnement
source .venv/bin/activate
```

#### Option 2 : Manuellement

```bash
# Créer l'environnement virtuel
uv venv

# Installer les dépendances
uv pip install -e ".[dev]"

# Activer l'environnement
source .venv/bin/activate
```

---

### 🧪 **Tester l'intégration**

#### Exécuter les tests unitaires

```bash
# Tous les tests
make test

# Tests spécifiques
uv run pytest tests/test_api_auth.py -v
uv run pytest tests/test_coordinator.py -v

# Avec coverage
make test-cov
```

#### Tester avec des identifiants réels

```bash
# Exporter vos credentials
export REGIE_USERNAME=votre@email.com
export REGIE_PASSWORD=votre_mot_de_passe

# Exécuter un test de connexion
uv run pytest tests/test_meter_index.py -v -s
```

---

### 📁 **Structure du projet**

```
regiedeseauxmpl/
├── custom_components/regiedeseauxmpl/          # Intégration HACS
│   ├── __init__.py                           # Setup principal + services
│   ├── api.py                                # Client API (curl_cffi pour F5 BIG-IP)
│   ├── const.py                              # Constantes et configuration
│   ├── config_flow.py                        # Flux de configuration UI
│   ├── coordinator.py                        # Gestion centralisée des données
│   ├── diagnostics.py                        # Outils de diagnostic
│   ├── entity.py                             # Base entity avec DeviceInfo
│   ├── exceptions.py                         # Gestion des erreurs personnalisées
│   ├── sensor.py                             # Entités sensor (water, total_increasing)
│   ├── manifest.json                         # Métadonnées de l'intégration
│   ├── info.md                               # Documentation pour le store HACS
│   ├── services.yaml                         # Définition des services
│   ├── strings.json                          # Strings de base
│   └── translations/                         # Traductions
│       ├── en.json                           # Anglais
│       └── fr.json                           # Français
│
├── tests/                                    # Tests unitaires (pytest)
│   ├── __init__.py
│   ├── conftest.py                           # Fixtures communes
│   ├── test_api_auth.py                      # Tests d'authentification
│   ├── test_coordinator.py                   # Tests du coordinator
│   └── test_sensor.py                        # Tests des sensors
│
├── brand/                                   # Assets pour HACS (OBLIGATOIRE)
│   └── icon.png                             # Icône 512x512
│
├── .github/workflows/                       # CI/CD
│   ├── test_and_release.yml                  # Tests + Release GitHub
│   └── hacs_validation.yml                  # Validation HACS
│
├── Makefile                                 # Commandes utiles
├── pyproject.toml                           # Dépendances (uv/pip)
├── .env.example                             # Template pour les variables d'environnement
├── .gitignore                               # Exclusions Git
├── README.md                                # Documentation principale
├── CHANGELOG.md                             # Historique des changements
├── LICENSE                                  # Licence MIT
├── hacs.json                                # Configuration HACS (racine)
└── requirements.txt                         # Dépendances (optionnel)
```

---

### 📊 **Commandes Make utiles**

| Commande | Description |
|----------|-------------|
| `make help` | Affiche toutes les commandes disponibles |
| `make setup` | Crée l'environnement virtuel avec uv |
| `make clean` | Supprime l'environnement virtuel |
| `make test` | Exécute tous les tests pytest |
| `make test-cov` | Exécute les tests avec coverage |
| `make lint` | Vérifie la qualité du code avec ruff |
| `make format` | Formate le code avec ruff |
| `make pkgs` | Liste les packages installés |
| `make python-version` | Affiche la version de Python |
| `make uv-version` | Affiche la version de uv |

---

## 🤝 **Contribuer**

Les contributions sont **les bienvenues** ! Voici comment aider :

### 🐛 **Signaler un problème**

- Ouvrez une [Issue](https://github.com/iopsthecloud/regideseaux3m-hass/issues)
- Incluez :
  - Votre version de Home Assistant
  - La version de l'intégration (dans `manifest.json`)
  - Les **logs complets** (via Paramètres → Journaux, filtrés par `regiedeseauxmpl`)
  - Les étapes pour reproduire le problème
  - Votre configuration (masquez vos identifiants !)

### 💡 **Proposer une amélioration**

1. Forkez le dépôt
2. Créez une branche (`git checkout -b feature/amazing-feature`)
3. Commitez vos changements (`git commit -m 'Add amazing feature'`)
4. Poussez vers votre fork (`git push origin feature/amazing-feature`)
5. Ouvrez une [Pull Request](https://github.com/iopsthecloud/regideseaux3m-hass/pulls)

### 🌍 **Traduire dans une autre langue**

1. Copiez `translations/en.json` en `translations/<lang>.json` (ex: `es.json`, `de.json`)
2. Traduisiez **toutes les valeurs** (pas les clés !)
3. Ouvrez une Pull Request

---

## 📜 **Licence**

Ce projet est sous licence **MIT** - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 **Remerciements**

- **Home Assistant** pour la plateforme incroyable et ouverte
- **HACS** pour simplifier l'installation des intégrations personnalisées
- **Montpellier Méditerranée Métropole** et **la Régie des Eaux** pour leur service public essentiel
- **Tous les contributeurs** qui aident à améliorer ce projet
- **Les utilisateurs** qui testent et remontent les problèmes

---

## 💬 **Support**

Pour du support :
- **Ouvrez une Issue** : [GitHub Issues](https://github.com/iopsthecloud/regideseaux3m-hass/issues)
- **Forum Home Assistant FR** : [Discussion sur le forum](https://community.home-assistant.io/)
- **Documentation officielle** : [HACS](https://www.hacs.xyz/) | [Home Assistant Dev](https://developers.home-assistant.io/)

---

[hacs]: https://hacs.xyz
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge&logo=homeassistantcommunitystore
[hacs-repo]: https://my.home-assistant.io/redirect/hacs_repository/?owner=iopsthecloud&repository=regideseaux3m-hass&category=integration
[license]: LICENSE
[license-badge]: https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge&logo=open-source-initiative
[python-badge]: https://img.shields.io/badge/Python-3.14%2B-blue.svg?style=for-the-badge&logo=python
[release]: https://github.com/iopsthecloud/regideseaux3m-hass/releases
[release-badge]: https://img.shields.io/github/release/iopsthecloud/regideseaux3m-hass.svg?style=for-the-badge&logo=github
[repo]: https://github.com/iopsthecloud/regideseaux3m-hass
[last-commit-badge]: https://img.shields.io/github/last-commit/iopsthecloud/regideseaux3m-hass.svg?style=for-the-badge&logo=github
