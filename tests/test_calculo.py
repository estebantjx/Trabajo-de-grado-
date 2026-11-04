
import pytest

from app.calculo import calcular_zona2, clasificar_sesion

# (edad, fc_reposo, fc_maxima, reserva, zona2_inferior, zona2_superior)
CASOS = [
    (22, 60, 198, 138, 143, 157),
    (24, 65, 196, 131, 144, 157),
    (30, 70, 190, 120, 142, 154),
    (35, 70, 185, 115, 139, 151),   # 150,5 -> 151
    (45, 75, 175, 100, 135, 145),
    (18, 55, 202, 147, 143, 158),
    (28, 60, 192, 132, 139, 152),
    (40, 68, 180, 112, 135, 146),
    (50, 72, 170, 98, 131, 141),
    (60, 80, 160, 80, 128, 136),
]


@pytest.mark.parametrize("edad, reposo, fc_max, reserva, inferior, superior", CASOS)
def test_zona2_coincide_con_verificacion_manual(edad, reposo, fc_max, reserva, inferior, superior):
    zona = calcular_zona2(edad, reposo)
    assert zona["fc_maxima"] == fc_max
    assert zona["reserva"] == reserva
    assert zona["zona2_inferior"] == inferior
    assert zona["zona2_superior"] == superior


def test_acepta_numeros_en_texto():
    assert calcular_zona2("24", "65")["zona2_inferior"] == 144


@pytest.mark.parametrize("edad, reposo", [
    (9, 60), (101, 60),          # edad fuera de rango
    (30, 29), (30, 121),         # FC en reposo fuera de rango
    (None, 60), (30, None),      # faltan datos
    ("abc", 60), (30, "x"),      # no son números
    (30.5, 60), (True, 60),      # decimales y booleanos no son válidos
])
def test_rechaza_datos_invalidos(edad, reposo):
    with pytest.raises(ValueError):
        calcular_zona2(edad, reposo)


def test_rechaza_reposo_mayor_que_maxima():
    # 100 años -> FCmáx = 120; un reposo de 120 deja la reserva en cero
    with pytest.raises(ValueError):
        calcular_zona2(100, 120)


def test_clasificacion_de_sesion():
    assert clasificar_sesion(143, 144, 157) == "debajo"
    assert clasificar_sesion(144, 144, 157) == "dentro"   # límite inferior incluido
    assert clasificar_sesion(157, 144, 157) == "dentro"   # límite superior incluido
    assert clasificar_sesion(158, 144, 157) == "encima"