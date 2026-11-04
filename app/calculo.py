
from datetime import date

PCT_INFERIOR = 60  # % de la reserva de FC donde empieza la zona 2
PCT_SUPERIOR = 70  # % de la reserva de FC donde termina la zona 2

EDAD_MIN, EDAD_MAX = 10, 100
FC_REPOSO_MIN, FC_REPOSO_MAX = 30, 120
FC_PROMEDIO_MIN, FC_PROMEDIO_MAX = 30, 230
DURACION_MIN, DURACION_MAX = 1, 600


# ---------------------------------------------------------------- utilidades
def a_entero(valor, campo):
    """Convierte a entero un valor que llega de la API (número o texto)."""
    if isinstance(valor, bool):
        raise ValueError(f"El campo '{campo}' debe ser un número entero.")
    if isinstance(valor, int):
        return valor
    if isinstance(valor, str) and valor.strip().lstrip("-").isdigit():
        return int(valor.strip())
    raise ValueError(f"El campo '{campo}' debe ser un número entero.")


def _en_rango(valor, minimo, maximo, campo, unidad=""):
    if not minimo <= valor <= maximo:
        raise ValueError(f"El campo '{campo}' debe estar entre {minimo} y {maximo}{unidad}.")
    return valor


def _porcentaje(fc_reposo, reserva, pct):
    """FC objetivo = fc_reposo + reserva x pct/100, redondeada al entero más cercano
    (0,5 hacia arriba), usando solo aritmética entera."""
    return (fc_reposo * 100 + reserva * pct + 50) // 100


# ------------------------------------------------------------------ cálculo
def fc_maxima(edad):
    """Frecuencia cardíaca máxima teórica: 220 - edad."""
    return 220 - edad


def calcular_zona2(edad, fc_reposo):
    """Devuelve un diccionario con la FC máxima, la reserva y los límites de la zona 2."""
    edad = _en_rango(a_entero(edad, "edad"), EDAD_MIN, EDAD_MAX, "edad", " años")
    fc_reposo = _en_rango(a_entero(fc_reposo, "fc_reposo"),
                          FC_REPOSO_MIN, FC_REPOSO_MAX, "fc_reposo", " lpm")
    fc_max = fc_maxima(edad)
    reserva = fc_max - fc_reposo
    if reserva <= 0:
        raise ValueError("La frecuencia cardíaca en reposo debe ser menor que la máxima teórica.")
    return {
        "edad": edad,
        "fc_reposo": fc_reposo,
        "fc_maxima": fc_max,
        "reserva": reserva,
        "zona2_inferior": _porcentaje(fc_reposo, reserva, PCT_INFERIOR),
        "zona2_superior": _porcentaje(fc_reposo, reserva, PCT_SUPERIOR),
    }


def clasificar_sesion(fc_promedio, zona2_inferior, zona2_superior):
    """Indica si la FC promedio de una sesión estuvo debajo, dentro o encima de la zona 2."""
    if fc_promedio < zona2_inferior:
        return "debajo"
    if fc_promedio > zona2_superior:
        return "encima"
    return "dentro"


# -------------------------------------------------------------- validaciones
def validar_usuario(datos):
    """Valida y normaliza los datos de un usuario. Lanza ValueError si hay un error."""
    nombre = (datos.get("nombre") or "").strip() if isinstance(datos.get("nombre"), str) else ""
    if not 2 <= len(nombre) <= 100:
        raise ValueError("El campo 'nombre' es obligatorio (entre 2 y 100 caracteres).")
    zona = calcular_zona2(datos.get("edad"), datos.get("fc_reposo"))
    return {"nombre": nombre, "edad": zona["edad"], "fc_reposo": zona["fc_reposo"]}


def validar_sesion(datos):
    """Valida y normaliza los datos de una sesión de entrenamiento."""
    fecha_txt = datos.get("fecha")
    try:
        fecha = date.fromisoformat(fecha_txt)
    except (TypeError, ValueError):
        raise ValueError("El campo 'fecha' es obligatorio con formato AAAA-MM-DD.") from None
    if fecha > date.today():
        raise ValueError("La fecha de la sesión no puede ser futura.")

    duracion = _en_rango(a_entero(datos.get("duracion_min"), "duracion_min"),
                         DURACION_MIN, DURACION_MAX, "duracion_min", " minutos")
    fc_prom = _en_rango(a_entero(datos.get("fc_promedio"), "fc_promedio"),
                        FC_PROMEDIO_MIN, FC_PROMEDIO_MAX, "fc_promedio", " lpm")

    minutos_zona2 = datos.get("minutos_zona2")
    if minutos_zona2 in (None, ""):
        minutos_zona2 = None
    else:
        minutos_zona2 = a_entero(minutos_zona2, "minutos_zona2")
        if not 0 <= minutos_zona2 <= duracion:
            raise ValueError("'minutos_zona2' debe estar entre 0 y la duración de la sesión.")

    return {"fecha": fecha, "duracion_min": duracion,
            "fc_promedio": fc_prom, "minutos_zona2": minutos_zona2}