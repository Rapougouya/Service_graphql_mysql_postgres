import strawberry
from typing import List, Optional
from datetime import datetime
from sqlalchemy import text  # ← IMPORT DÉJÀ PRÉSENT
from src.database.connection_pool import get_mysql_client, get_postgres_client
from src.database.models import EmployeMySQL, EmployePostgreSQL
from src.etl.kafka_producer import EmployeProducer


# TYPES GRAPHQL ----------------------------------------

@strawberry.type
class EmployeType:
    id: int
    nom: str
    prenom: str
    email: str
    poste: str
    salaire: float
    department: str
    date_embauche: datetime


@strawberry.input
class EmployeInput:
    nom: str
    prenom: str
    email: str
    poste: str
    salaire: float
    department: str


# QUERY -------------------------------------------------

@strawberry.type
class Query:

    @strawberry.field
    def employes(self) -> List[EmployeType]:
        client = get_postgres_client()
        with client.get_session() as session:
            # ✅ UTILISATION CORRECTE - pas de session.execute() ici
            employees = session.query(EmployePostgreSQL).all()
            return employees

    @strawberry.field
    def employe_par_id(self, id: int) -> Optional[EmployeType]:
        client = get_postgres_client()
        with client.get_session() as session:
            # ✅ UTILISATION CORRECTE
            return session.query(EmployePostgreSQL).filter_by(id=id).first()

    @strawberry.field
    def employes_par_department(self, department: str) -> List[EmployeType]:
        client = get_postgres_client()
        with client.get_session() as session:
            # ✅ UTILISATION CORRECTE
            return session.query(EmployePostgreSQL).filter_by(department=department).all()

    # ✅ AJOUTER DES MÉTRIQUES DE MONITORING
    @strawberry.field
    def stats_employes(self) -> str:
        """Statistiques des employés pour le monitoring"""
        try:
            client = get_postgres_client()
            with client.get_session() as session:
                # ✅ CORRECT : utiliser text() pour les requêtes raw
                total = session.execute(text("SELECT COUNT(*) FROM employes")).scalar()
                par_departement = session.execute(  # ← ✅ MAINTENANT AVEC text() !
                text("SELECT department, COUNT(*) FROM employes GROUP BY department")
            ).fetchall()
                
                stats = f"Total employés: {total}\n"
                for dept, count in par_departement:
                    stats += f"{dept}: {count}\n"
                
                return stats
                
        except Exception as e:
            return f"Erreur statistiques: {str(e)}"


# MUTATIONS ---------------------------------------------

@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_employe(self, input: EmployeInput) -> EmployeType:
      from datetime import datetime
    
      client = get_mysql_client()
      with client.get_session() as session:
        new_emp = EmployeMySQL(
            nom=input.nom,
            prenom=input.prenom,
            email=input.email,
            poste=input.poste,
            salaire=input.salaire,
            department=input.department,
            date_embauche=datetime.utcnow()
        )
        session.add(new_emp)
        session.commit()
        session.refresh(new_emp)

        # Synchroniser dans Kafka
        try:
           producer = EmployeProducer()
           producer.sync_all_employes()
        except Exception as e:
          print(f"⚠️ Kafka sync error: {e}")

        return EmployeType(
           id=new_emp.id,
           nom=new_emp.nom,
           prenom=new_emp.prenom,
           email=new_emp.email,
           poste=new_emp.poste,
           salaire=new_emp.salaire,
           department=new_emp.department,
           date_embauche=new_emp.date_embauche
        )

    @strawberry.mutation
    def update_employe(self, id: int, input: EmployeInput) -> Optional[EmployeType]:
      """Mutation pour mettre à jour un employé"""
      client = get_mysql_client()
      with client.get_session() as session:
        employe = session.query(EmployeMySQL).filter_by(id=id).first()
        if not employe:
            return None
        
        # Mettre à jour les champs
        employe.nom = input.nom
        employe.prenom = input.prenom
        employe.email = input.email
        employe.poste = input.poste
        employe.salaire = input.salaire
        employe.department = input.department
        
        session.commit()
        
        # Déclencher la synchronisation
        producer = EmployeProducer()
        producer.sync_all_employes()
        
        return EmployeType(
            id=employe.id,
            nom=employe.nom,
            prenom=employe.prenom,
            email=employe.email,
            poste=employe.poste,
            salaire=employe.salaire,
            department=employe.department,
            date_embauche=employe.date_embauche
        )

    @strawberry.mutation
    def delete_employe(self, id: int) -> bool:
        """Mutation pour supprimer un employé"""
        client = get_mysql_client()
        with client.get_session() as session:
            employe = session.query(EmployeMySQL).filter_by(id=id).first()
            if not employe:
                return False
            
            session.delete(employe)
            session.commit()
            
            # Déclencher la synchronisation
            producer = EmployeProducer()
            producer.sync_all_employes()
            
            return True

    @strawberry.mutation
    def sync_employes(self) -> str:
        producer = EmployeProducer()
        producer.sync_all_employes()
        return "Synchronisation déclenchée"

    @strawberry.mutation
    def health_check(self) -> str:
        """Mutation pour vérifier la santé des bases de données"""
        try:
           # MySQL
            mysql_client = get_mysql_client()
            with mysql_client.get_session() as session:
               mysql_ok = session.execute(text("SELECT 1")).scalar() is not None

            # PostgreSQL
            postgres_client = get_postgres_client()
            with postgres_client.get_session() as session:
               postgres_ok = session.execute(text("SELECT 1")).scalar() is not None

            if mysql_ok and postgres_ok:
               return "✅ Toutes les bases de données sont opérationnelles"
            elif mysql_ok:
               return "⚠️ MySQL OK mais PostgreSQL inaccessible"
            elif postgres_ok:
               return "⚠️ PostgreSQL OK mais MySQL inaccessible"
            else:
               return "❌ Toutes les bases de données sont inaccessibles"
        except Exception as e:
            return f"❌ Erreur health check: {str(e)}"

schema = strawberry.Schema(query=Query, mutation=Mutation)