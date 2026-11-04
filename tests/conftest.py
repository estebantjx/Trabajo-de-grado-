import pytest

from app import create_app
from app.models import db


@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.test_client() as cliente:
        yield cliente
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture()
def usuario(client):
    """Usuario ya registrado: 24 años, FC en reposo 65 -> zona 2 de 144 a 157 lpm."""
    respuesta = client.post("/api/usuarios", json={"nombre": "Ana Prueba", "edad": 24, "fc_reposo": 65})
    return respuesta.get_json()