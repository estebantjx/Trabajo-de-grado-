import os

from flask import Flask, render_template

from .models import db
from .routes import api


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    # Por defecto usa SQLite (archivo local, sin instalar nada). Para usar PostgreSQL basta
    # definir la variable de entorno DATABASE_URL, por ejemplo:
    #   postgresql+psycopg2://usuario:clave@localhost:5432/zona2
    url = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(app.instance_path, "zona2.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    app.config.from_mapping(SQLALCHEMY_DATABASE_URI=url)
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    db.init_app(app)
    app.register_blueprint(api)

    @app.get("/")
    def inicio():
        return render_template("index.html")

    with app.app_context():
        db.create_all()

    return app