# Plataforma web para el seguimiento de entrenamiento aeróbico en Zona 2

**Trabajo de grado – Ingeniería de Software**
Institución Universitaria Politécnico Grancolombiano · Grupo de Investigación E-TIC

| | |
|---|---|
| **Autor** | Esteban Alejandro Piñeros Niño (código 100383218) |
| **Asesor** | Carlos David Seligmann Trujillo |
| **Versión** | Entrega 2 – Fases 3 (backend) y 4 (frontend de registro) |
| **Fecha** | Noviembre de 2026 |
| **Repositorio** | <https://github.com/estebantjx/Trabajo-de-grado-> |

---

## Contenido

1. [Descripción](#1-descripción)
2. [Qué incluye esta entrega](#2-qué-incluye-esta-entrega)
3. [Requisitos](#3-requisitos)
4. [Instalación en Windows (paso a paso)](#4-instalación-en-windows-paso-a-paso)
5. [Ejecución de la aplicación](#5-ejecución-de-la-aplicación)
6. [Guía de uso rápida](#6-guía-de-uso-rápida)
7. [Pruebas automáticas](#7-pruebas-automáticas)
8. [Instalación en Mac o Linux](#8-instalación-en-mac-o-linux)
9. [Solución de problemas](#9-solución-de-problemas)
10. [Estructura del proyecto](#10-estructura-del-proyecto)
11. [Documentación de la API](#11-documentación-de-la-api)
12. [Decisiones técnicas y limitaciones](#12-decisiones-técnicas-y-limitaciones)

---

## 1. Descripción

La aplicación permite a una persona que entrena de forma recreativa:

- Registrar sus datos básicos (nombre, edad y frecuencia cardíaca en reposo).
- Conocer automáticamente su **rango de zona 2** de frecuencia cardíaca.
- Registrar sesiones de entrenamiento (fecha, duración y frecuencia cardíaca promedio).
- Consultar un histórico de sesiones y ver si cada una quedó **dentro, debajo o encima** de la zona 2.

El cálculo usa la **fórmula de Karvonen**:

```
FC máxima teórica = 220 − edad
Reserva de FC     = FC máxima − FC en reposo
Zona 2            = FC en reposo + reserva × 60 %   hasta   FC en reposo + reserva × 70 %
```

Los valores se redondean al entero más cercano (0,5 hacia arriba). Ejemplo: una persona de 24 años con
frecuencia cardíaca en reposo de 65 lpm tiene FC máxima de 196, reserva de 131 y zona 2 de **144 a 157 lpm**.

> La aplicación es un proyecto académico de apoyo al entrenamiento; no es un dispositivo médico ni
> reemplaza la valoración de un profesional de la salud.

## 2. Qué incluye esta entrega

| Fase | Contenido | Dónde está |
|---|---|---|
| 3. Backend | API REST con Flask, cálculo de zona 2, base de datos, validaciones | `app/` |
| 4. Frontend de registro | Página web con formulario de usuario, formulario de sesión e histórico | `app/templates/`, `app/static/` |
| Pruebas | 40 pruebas automáticas (cobertura del 99 %) | `tests/` |

El tablero con gráficas (Chart.js) corresponde a la Entrega Final.

## 3. Requisitos

- **Windows 10 u 11** (también funciona en Mac y Linux, ver sección 8).
- **Python 3.10 o superior** (se probó con Python 3.13).
- Un navegador web (Chrome, Edge o Firefox).
- **No** se necesita instalar ninguna base de datos: por defecto se usa SQLite, que crea un archivo local.

## 4. Instalación en Windows (paso a paso)

### 4.1. Instalar Python (solo la primera vez)

1. Entra a <https://www.python.org/downloads/> y descarga la versión más reciente para Windows.
2. Ejecuta el instalador. **Antes de presionar "Install Now", marca la casilla "Add python.exe to PATH"**
   (está en la parte inferior de la primera ventana). Este paso es el que más errores evita.
3. Al terminar, abre **PowerShell** (tecla Windows, escribe `PowerShell`, Enter) y verifica:

   ```powershell
   python --version
   ```

   Debe mostrar algo como `Python 3.13.x`. Si aparece un error, revisa la sección 9.

### 4.2. Descargar el proyecto

1. En la página del repositorio presiona el botón verde **Code → Download ZIP**. Descomprime el archivo
   (clic derecho → "Extraer todo…") en una carpeta sencilla, por ejemplo `C:\proyectos\zona2`.
   Evita rutas dentro de OneDrive o con muchos caracteres especiales.
2. Abre esa carpeta en el Explorador de archivos, haz clic en la barra de direcciones, escribe `powershell`
   y presiona Enter. Se abrirá una terminal ya ubicada en la carpeta del proyecto.

### 4.3. Crear el entorno virtual e instalar las dependencias

Ejecuta estos comandos, uno por uno:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

- El segundo comando activa el entorno; verás `(venv)` al inicio de la línea.
- Si PowerShell muestra el error *"la ejecución de scripts está deshabilitada en este sistema"*, ejecuta
  primero `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, responde `S` y repite el
  segundo comando. Ese cambio solo vale para la ventana actual.

**Alternativa sin comandos:** haz doble clic en `instalar.bat`, que ejecuta los mismos pasos.

## 5. Ejecución de la aplicación

Con el entorno activado (`(venv)` visible):

```powershell
python scripts/cargar_datos_ejemplo.py
python run.py
```

- El primer comando es **opcional**: crea un usuario "Usuario de prueba" con 15 sesiones de ejemplo
  (datos inventados) para ver el histórico lleno. Se puede ejecutar varias veces; no duplica datos.
- El segundo inicia el servidor. Abre en el navegador: **<http://localhost:5000>**
- Para detener la aplicación, presiona `Ctrl + C` en la terminal.

**Alternativa sin comandos:** doble clic en `iniciar.bat` (inicia el servidor y abre el navegador).

Los datos quedan guardados en el archivo `instance\zona2.db`. Para empezar de cero, detén la aplicación y
borra ese archivo.

## 6. Guía de uso rápida

1. **Crear un usuario.** En la tarjeta "1. Usuario", abre *Registrar un usuario nuevo*, completa nombre,
   edad (10–100) y frecuencia cardíaca en reposo (30–120 lpm) y presiona *Guardar usuario*.
   La aplicación muestra de inmediato la zona 2 calculada.
2. **Registrar una sesión.** En "2. Registrar sesión" indica la fecha, la duración en minutos y la
   frecuencia cardíaca promedio. Opcionalmente, indica cuántos minutos estuviste dentro de la zona 2 para
   obtener el porcentaje de la sesión.
3. **Consultar el histórico.** En "3. Histórico de sesiones" aparecen las sesiones ordenadas por fecha, con
   la etiqueta *Dentro*, *Debajo* o *Encima* de zona 2. Se puede filtrar por rango de fechas y eliminar
   sesiones.

Si algún dato es inválido (por ejemplo, una fecha futura o más minutos en zona 2 que la duración total),
la aplicación muestra un mensaje en rojo explicando el problema y no guarda nada.

## 7. Pruebas automáticas

Con el entorno activado:

```powershell
pytest
pytest --cov=app
```

El primer comando ejecuta las 40 pruebas; el segundo, además, muestra el porcentaje de cobertura.
Resultado esperado: `40 passed` y una cobertura total cercana al 99 %.

Las pruebas cubren:

- **Cálculo (`tests/test_calculo.py`):** 10 casos con valores esperados calculados aparte con la fórmula de
  Karvonen (los 5 primeros son los de la Tabla 4 del documento de la Entrega 1), rechazo de datos inválidos
  y clasificación de sesiones.
- **API (`tests/test_api.py`):** creación y consulta de usuarios y sesiones, validaciones, filtros de
  fechas, eliminación y carga de la página principal.

Las pruebas usan una base de datos en memoria, por lo que **no modifican** los datos de la aplicación.

## 8. Instalación en Mac o Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 scripts/cargar_datos_ejemplo.py     # opcional
python3 run.py
```

Luego abre <http://localhost:5000>. Las pruebas se ejecutan con `pytest`.

## 9. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `python` no se reconoce como comando, o se abre la Microsoft Store | Python no está en el PATH | Reinstala Python marcando *Add python.exe to PATH*. Si persiste, en *Configuración → Aplicaciones → Configuración avanzada → Alias de ejecución de aplicaciones*, desactiva los alias de "python.exe". También puedes probar con `py` en lugar de `python`. |
| Error de ejecución de scripts al activar `venv` | Política de PowerShell | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` y repetir la activación. O usa `venv\Scripts\activate.bat` desde el Símbolo del sistema (cmd). |
| `No module named flask` | El entorno virtual no está activado | Activa `venv` y repite `pip install -r requirements.txt`. |
| `Address already in use` / el puerto 5000 está ocupado | Otro programa usa ese puerto | Cierra la otra aplicación, o en `run.py` cambia la última línea por `app.run(debug=True, port=5001)` y abre <http://localhost:5001>. |
| La página abre pero la lista de usuarios está vacía | Aún no hay datos | Registra un usuario nuevo o ejecuta `python scripts/cargar_datos_ejemplo.py`. |
| Quiero borrar todos los datos | — | Detén la aplicación y borra `instance\zona2.db`. |

## 10. Estructura del proyecto

```
Trabajo-de-grado-/
├── app/
│   ├── __init__.py        Fábrica de la aplicación y configuración de la base de datos
│   ├── calculo.py         Fórmula de Karvonen, clasificación de sesiones y validaciones
│   ├── models.py          Tablas Usuario y Sesion (SQLAlchemy)
│   ├── routes.py          Endpoints de la API REST (prefijo /api)
│   ├── templates/         Página web (HTML)
│   └── static/            Estilos (CSS) y lógica del navegador (JavaScript)
├── tests/                 Pruebas automáticas (pytest)
├── scripts/               Carga de datos de ejemplo
├── run.py                 Punto de entrada del servidor
├── requirements.txt       Dependencias
├── .gitignore             Archivos que no se suben al repositorio
├── instalar.bat           Atajo de instalación para Windows
└── iniciar.bat            Atajo de ejecución para Windows
```

## 11. Documentación de la API

Todas las respuestas son JSON. Los errores devuelven `{"error": "mensaje"}` con código 400 (datos
inválidos) o 404 (recurso inexistente).

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/zona2?edad=24&fc_reposo=65` | Calcula la zona 2 sin guardar nada |
| POST | `/api/usuarios` | Crea un usuario; devuelve también su zona 2 |
| GET | `/api/usuarios` | Lista los usuarios |
| GET | `/api/usuarios/<id>` | Consulta un usuario |
| GET | `/api/usuarios/<id>/zona2` | Zona 2 de un usuario |
| POST | `/api/usuarios/<id>/sesiones` | Registra una sesión |
| GET | `/api/usuarios/<id>/sesiones?desde=AAAA-MM-DD&hasta=AAAA-MM-DD` | Histórico (filtro opcional) |
| DELETE | `/api/usuarios/<id>/sesiones/<sid>` | Elimina una sesión |

Ejemplo de solicitud y respuesta:

```
GET /api/zona2?edad=24&fc_reposo=65

{
  "edad": 24, "fc_reposo": 65, "fc_maxima": 196, "reserva": 131,
  "zona2_inferior": 144, "zona2_superior": 157
}
```

Cuerpo para registrar una sesión (`minutos_zona2` es opcional):

```json
{ "fecha": "2026-11-03", "duracion_min": 60, "fc_promedio": 150, "minutos_zona2": 45 }
```

Rangos válidos: edad 10–100 años; FC en reposo 30–120 lpm; FC promedio 30–230 lpm; duración 1–600 min;
la fecha no puede ser futura.

## 12. Decisiones técnicas y limitaciones

- **Flask + SQLAlchemy:** framework ligero y gratuito, adecuado para una API de alcance acotado.
- **SQLite por defecto:** no requiere instalación y facilita que cualquier persona ejecute el proyecto.
  Para usar PostgreSQL basta con instalar `psycopg2-binary` y definir la variable de entorno
  `DATABASE_URL` (por ejemplo, `postgresql+psycopg2://usuario:clave@localhost:5432/zona2`); no hay que
  cambiar el código.
- **Aritmética entera en el redondeo:** evita errores de coma flotante en valores como 150,5.
- **Alcance:** no incluye autenticación de usuarios ni integración con relojes o bandas de frecuencia
  cardíaca; las gráficas se agregarán en la Entrega Final.
- **Seguridad:** la interfaz escribe los datos con `textContent` (no interpreta HTML) y las consultas pasan
  por el ORM, lo que evita inyección de HTML y de SQL. El servidor incluido (`python run.py`) es de
  desarrollo y no está pensado para exponerse en internet.