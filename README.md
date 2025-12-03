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

flowchart LR
  %% Clients
  A[Client Web / GraphiQL] -->|HTTP GraphQL| B[API GraphQL - FastAPI + Strawberry]
  A2[CI / Professeur / Tests] -->|HTTP| B

  %% API & internal
  subgraph APP
    B --> C[MySQL (source)]
    B --> K[Kafka Producer]
    B --> M[Prometheus client / metrics]
  end

  %% Kafka pipeline
  subgraph KAFKA_CLUSTER
    Z[Zookeeper]
    Kb[Kafka Broker]
    Kb --> KE[Topic: employes-sync]
  end
  K --> Kb

  %% Consumer & Postgres
  subgraph WORKERS
    KC[Kafka Consumer (ETL)]
    KC --> P[PostgreSQL (destination)]
  end
  Kb --> KC

  %% Monitoring stack
  M --> Prom[Prometheus]
  Prom --> Graf[Grafana]
  Kb --> Kexp[Kafka Exporter]
  Kexp --> Prom
  Kb --> KUI[Kafka UI]

  %% Volumes & Docker
  B ---|container| Docker[Docker Compose network: monitoring]
  C ---|volume| VolMySQL[(mysql_data)]
  P ---|volume| VolPG[(postgres_data)]
  Graf ---|volume| VolGraf[(grafana_data)]
  Prom ---|volume| VolProm[(prometheus_data)]

  style APP fill:#f9f,stroke:#333,stroke-width:1px
  style KAFKA_CLUSTER fill:#ffd,stroke:#333,stroke-width:1px
  style WORKERS fill:#efe,stroke:#333


## 🔄 Flux de données détaillés

### Flux 1 : Création d'un employé
Client → Mutation GraphQL → MySQL → Kafka → PostgreSQL → Monitoring

### Flux 2 : Synchronisation automatique
Modification BD → Kafka Producer → Kafka Topic → Kafka Consumer → Sync BD

### Flux 3 : Monitoring en temps réel
Application → Métriques Prometheus → Scraping Prometheus → Dashboards Grafana

### Flux 4 : Requête de données
Client → Query GraphQL → PostgreSQL → Réponse JSON → Client