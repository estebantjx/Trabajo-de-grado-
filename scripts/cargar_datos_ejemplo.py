import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app          # noqa: E402
from app.models import Sesion, Usuario, db  # noqa: E402

NOMBRE = "Usuario de prueba"

# (días atrás, duración en min, FC promedio, minutos en zona 2 o None)
SESIONES = [
    (28, 45, 138, 10), (26, 50, 148, 38), (24, 60, 152, 48), (21, 40, 165, 8),
    (19, 55, 150, 44), (17, 70, 146, 52), (14, 45, 160, 12), (12, 60, 151, 50),
    (10, 50, 143, None), (8, 65, 154, 55), (6, 40, 149, 33), (5, 75, 147, 60),
    (3, 55, 158, 30), (2, 60, 153, 51), (1, 45, 150, 40),
]


def main():
    app = create_app()
    with app.app_context():
        if Usuario.query.filter_by(nombre=NOMBRE).first():
            print(f'Ya existe el usuario "{NOMBRE}". No se cargó nada para evitar duplicados.')
            return
        usuario = Usuario(nombre=NOMBRE, edad=24, fc_reposo=65)
        db.session.add(usuario)
        db.session.flush()
        hoy = date.today()
        for dias, duracion, fc, minutos in SESIONES:
            db.session.add(Sesion(usuario_id=usuario.id, fecha=hoy - timedelta(days=dias),
                                  duracion_min=duracion, fc_promedio=fc, minutos_zona2=minutos))
        db.session.commit()
        print(f'Listo: usuario "{NOMBRE}" con {len(SESIONES)} sesiones de ejemplo.')


if __name__ == "__main__":
    main()