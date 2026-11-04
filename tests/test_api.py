from datetime import date, timedelta

HOY = date.today()


def sesion_valida(**cambios):
    datos = {"fecha": HOY.isoformat(), "duracion_min": 60, "fc_promedio": 150}
    datos.update(cambios)
    return datos


# ----------------------------------------------------------------- cálculo
def test_calculo_directo(client):
    r = client.get("/api/zona2?edad=24&fc_reposo=65")
    assert r.status_code == 200
    assert r.get_json()["zona2_inferior"] == 144
    assert r.get_json()["zona2_superior"] == 157


def test_calculo_directo_con_datos_invalidos(client):
    r = client.get("/api/zona2?edad=abc&fc_reposo=65")
    assert r.status_code == 400
    assert "edad" in r.get_json()["error"]


# ---------------------------------------------------------------- usuarios
def test_crear_usuario_devuelve_zona2(client):
    r = client.post("/api/usuarios", json={"nombre": "  Luis  ", "edad": 35, "fc_reposo": 70})
    assert r.status_code == 201
    datos = r.get_json()
    assert datos["nombre"] == "Luis"                       # se limpian los espacios
    assert datos["zona2"]["zona2_inferior"] == 139
    assert datos["zona2"]["zona2_superior"] == 151


def test_crear_usuario_con_datos_invalidos(client):
    for cuerpo in (
        {"nombre": "", "edad": 30, "fc_reposo": 60},
        {"nombre": "Ana", "edad": 5, "fc_reposo": 60},
        {"nombre": "Ana", "edad": 30},
        {"edad": 30, "fc_reposo": 60},
    ):
        r = client.post("/api/usuarios", json=cuerpo)
        assert r.status_code == 400, cuerpo
        assert "error" in r.get_json()


def test_crear_usuario_sin_json(client):
    r = client.post("/api/usuarios", data="no es json", content_type="text/plain")
    assert r.status_code == 400


def test_listar_y_obtener_usuarios(client, usuario):
    lista = client.get("/api/usuarios").get_json()
    assert [u["nombre"] for u in lista] == ["Ana Prueba"]
    r = client.get(f"/api/usuarios/{usuario['id']}")
    assert r.status_code == 200 and r.get_json()["edad"] == 24


def test_zona2_de_usuario(client, usuario):
    r = client.get(f"/api/usuarios/{usuario['id']}/zona2")
    assert r.status_code == 200
    assert (r.get_json()["zona2_inferior"], r.get_json()["zona2_superior"]) == (144, 157)


def test_usuario_inexistente(client):
    assert client.get("/api/usuarios/999").status_code == 404
    assert client.get("/api/usuarios/999/zona2").status_code == 404
    assert client.get("/api/usuarios/999/sesiones").status_code == 404
    assert client.post("/api/usuarios/999/sesiones", json=sesion_valida()).status_code == 404


# ---------------------------------------------------------------- sesiones
def test_registrar_sesion_dentro_de_zona(client, usuario):
    r = client.post(f"/api/usuarios/{usuario['id']}/sesiones",
                    json=sesion_valida(fc_promedio=150, minutos_zona2=45))
    assert r.status_code == 201
    datos = r.get_json()
    assert datos["estado_zona"] == "dentro"
    assert datos["pct_tiempo_zona2"] == 75.0


def test_clasificacion_debajo_y_encima(client, usuario):
    url = f"/api/usuarios/{usuario['id']}/sesiones"
    assert client.post(url, json=sesion_valida(fc_promedio=130)).get_json()["estado_zona"] == "debajo"
    assert client.post(url, json=sesion_valida(fc_promedio=170)).get_json()["estado_zona"] == "encima"


def test_sin_minutos_el_porcentaje_es_nulo(client, usuario):
    r = client.post(f"/api/usuarios/{usuario['id']}/sesiones", json=sesion_valida())
    assert r.get_json()["pct_tiempo_zona2"] is None


def test_sesion_con_datos_invalidos(client, usuario):
    url = f"/api/usuarios/{usuario['id']}/sesiones"
    manana = (HOY + timedelta(days=1)).isoformat()
    for cambios in (
        {"fecha": manana},                    # fecha futura
        {"fecha": "12/05/2026"},              # formato incorrecto
        {"duracion_min": 0},                  # duración fuera de rango
        {"fc_promedio": 20},                  # FC fuera de rango
        {"fc_promedio": "alta"},              # no es número
        {"minutos_zona2": 61},                # más minutos en zona que la duración
    ):
        r = client.post(url, json=sesion_valida(**cambios))
        assert r.status_code == 400, cambios
        assert "error" in r.get_json()


# --------------------------------------------------------------- histórico
def test_historico_ordenado_y_con_filtro_de_fechas(client, usuario):
    url = f"/api/usuarios/{usuario['id']}/sesiones"
    for dias in (10, 5, 1):
        fecha = (HOY - timedelta(days=dias)).isoformat()
        assert client.post(url, json=sesion_valida(fecha=fecha)).status_code == 201

    completo = client.get(url).get_json()
    fechas = [s["fecha"] for s in completo["sesiones"]]
    assert fechas == sorted(fechas) and len(fechas) == 3
    assert completo["usuario"]["id"] == usuario["id"]

    desde = (HOY - timedelta(days=6)).isoformat()
    assert len(client.get(f"{url}?desde={desde}").get_json()["sesiones"]) == 2

    hasta = (HOY - timedelta(days=6)).isoformat()
    assert len(client.get(f"{url}?hasta={hasta}").get_json()["sesiones"]) == 1


def test_filtro_con_fecha_invalida(client, usuario):
    r = client.get(f"/api/usuarios/{usuario['id']}/sesiones?desde=ayer")
    assert r.status_code == 400


def test_historico_solo_muestra_sesiones_del_propio_usuario(client, usuario):
    otro = client.post("/api/usuarios", json={"nombre": "Otro", "edad": 40, "fc_reposo": 68}).get_json()
    client.post(f"/api/usuarios/{usuario['id']}/sesiones", json=sesion_valida())
    assert client.get(f"/api/usuarios/{otro['id']}/sesiones").get_json()["sesiones"] == []


def test_eliminar_sesion(client, usuario):
    url = f"/api/usuarios/{usuario['id']}/sesiones"
    sesion = client.post(url, json=sesion_valida()).get_json()
    assert client.delete(f"{url}/{sesion['id']}").status_code == 204
    assert client.get(url).get_json()["sesiones"] == []
    assert client.delete(f"{url}/{sesion['id']}").status_code == 404


# ----------------------------------------------------------------- interfaz
def test_pagina_principal(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Registrar sesión" in r.get_data(as_text=True)