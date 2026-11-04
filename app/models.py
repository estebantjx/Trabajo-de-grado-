from flask_sqlalchemy import SQLAlchemy

from .calculo import calcular_zona2, clasificar_sesion

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    fc_reposo = db.Column(db.Integer, nullable=False)

    sesiones = db.relationship(
        "Sesion", back_populates="usuario",
        cascade="all, delete-orphan", order_by="Sesion.fecha",
    )

    def zona2(self):
        return calcular_zona2(self.edad, self.fc_reposo)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "edad": self.edad,
                "fc_reposo": self.fc_reposo, "zona2": self.zona2()}


class Sesion(db.Model):
    __tablename__ = "sesion"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, nullable=False)
    duracion_min = db.Column(db.Integer, nullable=False)
    fc_promedio = db.Column(db.Integer, nullable=False)
    # Opcional: minutos que el usuario estuvo dentro de la zona 2 (por ejemplo, leídos de su reloj).
    minutos_zona2 = db.Column(db.Integer, nullable=True)

    usuario = db.relationship("Usuario", back_populates="sesiones")

    @property
    def pct_tiempo_zona2(self):
        """Porcentaje de la sesión dentro de la zona 2 (solo si se registraron los minutos)."""
        if self.minutos_zona2 is None:
            return None
        return round(self.minutos_zona2 * 100 / self.duracion_min, 1)

    def to_dict(self):
        zona = self.usuario.zona2()
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "fecha": self.fecha.isoformat(),
            "duracion_min": self.duracion_min,
            "fc_promedio": self.fc_promedio,
            "minutos_zona2": self.minutos_zona2,
            "pct_tiempo_zona2": self.pct_tiempo_zona2,
            "estado_zona": clasificar_sesion(
                self.fc_promedio, zona["zona2_inferior"], zona["zona2_superior"]),
        }