import pytest
from src.graphql.schema import schema

def test_employes_query():
    query = """
    query {
        employes {
            id
            nom
            prenom
        }
    }
    """
    result = schema.execute(query)
    assert result.errors is None
    assert result.data is not None