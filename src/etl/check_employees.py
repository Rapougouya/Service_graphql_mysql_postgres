#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de vérification : affiche les employés insérés dans MySQL et PostgreSQL
"""

import logging
from sqlalchemy import text
from src.database.connection_pool import get_mysql_client, get_postgres_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_employees():
    """Vérifier les employés dans les deux bases de données"""
    
    # MySQL
    logger.info("\n📊 Employés dans MySQL:")
    logger.info("-" * 80)
    try:
        mysql_client = get_mysql_client()
        with mysql_client.get_session() as session:
            result = session.execute(text("SELECT id, nom, prenom, email, poste, department, salaire FROM employes ORDER BY id"))
            rows = result.fetchall()
            if rows:
                for row in rows:
                    logger.info(f"ID: {row[0]:2} | {row[1]:15} {row[2]:15} | {row[3]:35} | {row[4]:25} | {row[5]:10} | ${row[6]:.2f}")
            else:
                logger.warning("❌ Aucun employé trouvé dans MySQL")
    except Exception as e:
        logger.error(f"❌ Erreur MySQL: {e}")
    
    # PostgreSQL
    logger.info("\n📊 Employés dans PostgreSQL:")
    logger.info("-" * 80)
    try:
        postgres_client = get_postgres_client()
        with postgres_client.get_session() as session:
            result = session.execute(text("SELECT id, nom, prenom, email, poste, department, salaire FROM employes ORDER BY id"))
            rows = result.fetchall()
            if rows:
                for row in rows:
                    logger.info(f"ID: {row[0]:2} | {row[1]:15} {row[2]:15} | {row[3]:35} | {row[4]:25} | {row[5]:10} | ${row[6]:.2f}")
            else:
                logger.warning("❌ Aucun employé trouvé dans PostgreSQL")
    except Exception as e:
        logger.error(f"❌ Erreur PostgreSQL: {e}")
    
    logger.info("\n✅ Vérification terminée!\n")

if __name__ == "__main__":
    check_employees()
