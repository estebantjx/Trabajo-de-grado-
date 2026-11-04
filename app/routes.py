
from datetime import date

from flask import Blueprint, jsonify, request

from .calculo import a_entero, calcular_zona2, validar_sesion, validar_usuario
from .models import Sesion, Usuario, db

api = Blueprint("api", __name__, url_prefix="/api")


def _json_o_error():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo de la petición debe ser un JSON válido.")
    return datos


@api.errorhandler(ValueError)
def error_de_validacion(error):
    return jsonify({"error": str(error)}), 400


@api.errorhandler(404)
def no_encontrado(_):
    return jsonify({"error": "Recurso no encontrado."}), 404


def _usuario_o_404(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        return None, (jsonify({"error": "El usuario no existe."}), 404)
    return usuario, None


# ------------------------------------------------------------------ cálculo
@api.get("/zona2")
def calcular():
    """Cálculo directo de la zona 2: /api/zona2?edad=24&fc_reposo=65"""
    return jsonify(calcular_zona2(request.args.get("edad"), request.args.get("fc_reposo")))


# ----------------------------------------------------------------- usuarios
@api.post("/usuarios")
def crear_usuario():
    datos = validar_usuario(_json_o_error())
    usuario = Usuario(**datos)
    db.session.add(usuario)
    db.session.commit()
    return jsonify(usuario.to_dict()), 201


@api.get("/usuarios")
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return jsonify([u.to_dict() for u in usuarios])


@api.get("/usuarios/<int:usuario_id>")
def obtener_usuario(usuario_id):
    usuario, error = _usuario_o_404(usuario_id)
    return error or jsonify(usuario.to_dict())


@api.get("/usuarios/<int:usuario_id>/zona2")
def zona2_de_usuario(usuario_id):
    usuario, error = _usuario_o_404(usuario_id)
    return error or jsonify(usuario.zona2())


# ----------------------------------------------------------------- sesiones
@api.post("/usuarios/<int:usuario_id>/sesiones")
def registrar_sesion(usuario_id):
    usuario, error = _usuario_o_404(usuario_id)
    if error:
        return error
    sesion = Sesion(usuario_id=usuario.id, **validar_sesion(_json_o_error()))
    db.session.add(sesion)
    db.session.commit()
    return jsonify(sesion.to_dict()), 201


@api.get("/usuarios/<int:usuario_id>/sesiones")
def historico(usuario_id):
    """Histórico de sesiones; admite filtro por fechas: ?desde=AAAA-MM-DD&hasta=AAAA-MM-DD"""
    usuario, error = _usuario_o_404(usuario_id)
    if error:
        return error
    consulta = Sesion.query.filter_by(usuario_id=usuario.id)
    for parametro, operador in (("desde", "__ge__"), ("hasta", "__le__")):
        texto = request.args.get(parametro)
        if texto:
            try:
                limite = date.fromisoformat(texto)
            except ValueError:
                raise ValueError(f"El parámetro '{parametro}' debe tener formato AAAA-MM-DD.") from None
            consulta = consulta.filter(getattr(Sesion.fecha, operador)(limite))
    sesiones = consulta.order_by(Sesion.fecha, Sesion.id).all()
    return jsonify({"usuario": usuario.to_dict(), "sesiones": [s.to_dict() for s in sesiones]})


@api.delete("/usuarios/<int:usuario_id>/sesiones/<int:sesion_id>")
def eliminar_sesion(usuario_id, sesion_id):
    sesion = Sesion.query.filter_by(id=sesion_id, usuario_id=usuario_id).first()
    if sesion is None:
        return jsonify({"error": "La sesión no existe."}), 404
    db.session.delete(sesion)
    db.session.commit()
    return "", 204