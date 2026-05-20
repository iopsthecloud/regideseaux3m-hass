# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr-FR/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Non publié]

### Ajouté
- Support multi-compteurs avec gestion individuelle
- Intégration native au tableau de bord Énergie/Eau de Home Assistant
- Configuration de l'intervalle de mise à jour (30 min à 24h)
- Service `regiedeseauxmpl.refresh_meters` pour rafraîchir manuellement
- Outils de diagnostic via l'intégration Diagnostics
- Traductions complètes en français et anglais
- Documentation complète pour HACS

### Modifié
- Amélioration de la gestion des erreurs et des timeouts
- Optimisation de la session HTTP avec curl_cffi
- Meilleure restauration des états après redémarrage
- Amélioration des messages de log

### Corrigé
- Gestion des cookies BIG-IP pour une connexion stable
- Problèmes de TLS fingerprinting avec l'API
- Affichage des attributs des entités

---

## [0.2.0] - 2025-01-XX

### Ajouté
- Version initiale pour HACS
- Interface de configuration UI complète
- Support de RestoreSensor pour persister les données
- Gestion des erreurs d'authentification

---

## [0.1.0] - 2024-XX-XX

### Ajouté
- Première version de l'intégration
- API client fonctionnel avec curl_cffi
- Récupération des index des compteurs
- Flux de configuration basique

[non publié]: https://github.com/iopsthecloud/regiedeseauxmpl/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/iopsthecloud/regiedeseauxmpl/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/iopsthecloud/regiedeseauxmpl/releases/tag/v0.1.0
