# 🚀 Service GraphQL avec Synchronisation ETL Kafka & Monitoring Prometheus/Grafana

## 📋 Vue d'ensemble du projet

Ce projet implémente un service GraphQL avancé pour la gestion des données d'employés, avec synchronisation en temps réel entre deux bases de données (MySQL et PostgreSQL) via Apache Kafka. L'architecture inclut un monitoring complet avec Prometheus et Grafana pour assurer la fiabilité et la performance du système.

**Objectif principal** : Créer un pipeline ETL robuste permettant la synchronisation bidirectionnelle des données d'employés entre différentes bases de données, avec une API GraphQL moderne et un système de monitoring professionnel.

---

## 👥 Membres du groupe

| Nom | Prénom | 
|-----|------|----------------|
| **BOGNINI** | Benjamine | 
| **CODJIA** | M. Moréno | 
| **OUEDRAOGO** | R. Daouda | 
| **ZOUNDI** | Jean Philippe | 

---

## 🏗️ Architecture complète

┌─────────────────────────────────────────────────────────────┐
│ CLIENT APPLICATIONS │
│ ┌────────────┐ ┌────────────┐ ┌────────────────────┐ │
│ │ Frontend │ │ Mobile │ │ Third-party APIs │ │
│ └─────┬──────┘ └─────┬──────┘ └──────────┬─────────┘ │
│ │ │ │ │
└────────┼────────────────┼────────────────────┼──────────────┘
│ │ │
▼ ▼ ▼
┌─────────────────────────────────────────────────────────────┐
│ FASTAPI GRAPHQL API │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ GraphQL Endpoint: /graphql │ │
│ │ • Query: employes, employe_par_id, stats_employes │ │
│ │ • Mutation: create_employe, sync_employes │ │
│ │ • Monitoring: /metrics (Prometheus) │ │
│ └──────────────┬───────────────────────────────────────┘ │
└─────────────────┼───────────────────────────────────────────┘
│
┌─────────────┼─────────────────────────────────────┐
│ ▼ │
│ ┌─────────────────────────────────────────┐ │
│ │ APACHE KAFKA (ETL) │ │
│ │ Topic: employes-sync │ │
│ │ • Producer: Envoie les modifications │ │
│ │ • Consumer: Synchronise les bases │ │
│ └─────┬─────────────────────┬─────────────┘ │
│ │ │ │
│ ▼ ▼ │
│ ┌─────────────┐ ┌──────────────┐ │
│ │ MySQL │ │ PostgreSQL │ │
│ │ (Source) │ │ (Destination)│ │
│ └─────────────┘ └──────────────┘ │
│ │
│ ┌─────────────────────────────────────────┐ │
│ │ MONITORING STACK │ │
│ │ • Prometheus: Collecte métriques │ │
│ │ • Grafana: Visualisation dashboards │ │
│ │ • Kafka Exporter: Métriques Kafka │ │
│ └─────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘

## 🔄 Flux de données détaillés

### Flux 1 : Création d'un employé
Client → Mutation GraphQL → MySQL → Kafka → PostgreSQL → Monitoring

### Flux 2 : Synchronisation automatique
Modification BD → Kafka Producer → Kafka Topic → Kafka Consumer → Sync BD

### Flux 3 : Monitoring en temps réel
Application → Métriques Prometheus → Scraping Prometheus → Dashboards Grafana

### Flux 4 : Requête de données
Client → Query GraphQL → PostgreSQL → Réponse JSON → Client