# Transformations de données ETL
def transform_employe_data(employe_data):
    """Transforme les données d'employé pour la synchronisation"""
    return {
        **employe_data,
        'email': employe_data['email'].lower().strip(),
        'nom': employe_data['nom'].strip().title(),
        'prenom': employe_data['prenom'].strip().title()
    }