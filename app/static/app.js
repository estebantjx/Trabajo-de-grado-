// Cliente web: consume la API REST de Flask (/api) y pinta los resultados.
"use strict";

const $ = (id) => document.getElementById(id);
let usuarioActual = null; // id del usuario seleccionado

// ------------------------------------------------------------ utilidades
async function api(ruta, opciones = {}) {
  const respuesta = await fetch("/api" + ruta, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) throw new Error(datos.error || "Ocurrió un error inesperado.");
  return datos;
}

let temporizadorAviso = null;
function aviso(texto, tipo = "ok") {
  const caja = $("aviso");
  caja.textContent = texto;
  caja.className = "aviso " + tipo;
  caja.hidden = false;
  clearTimeout(temporizadorAviso);
  temporizadorAviso = setTimeout(() => { caja.hidden = true; }, 6000);
}

function datosDeFormulario(formulario) {
  const datos = {};
  new FormData(formulario).forEach((valor, clave) => {
    const texto = String(valor).trim();
    datos[clave] = texto !== "" && !isNaN(texto) && clave !== "nombre" && clave !== "fecha"
      ? Number(texto) : texto;
  });
  return datos;
}

function guardarUsuarioSeleccionado(id) {
  try { localStorage.setItem("usuarioZona2", id ? String(id) : ""); } catch (_) { /* sin almacenamiento */ }
}
function leerUsuarioGuardado() {
  try { return localStorage.getItem("usuarioZona2") || ""; } catch (_) { return ""; }
}

function hoy() {
  const d = new Date();
  const dos = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
}

// -------------------------------------------------------------- usuarios
async function cargarUsuarios(idASeleccionar) {
  const usuarios = await api("/usuarios");
  const lista = $("sel-usuario");
  lista.replaceChildren(new Option("— Selecciona un usuario —", ""));
  usuarios.forEach((u) => lista.add(new Option(`${u.nombre} (${u.edad} años)`, u.id)));

  const objetivo = String(idASeleccionar || leerUsuarioGuardado() || "");
  if (objetivo && usuarios.some((u) => String(u.id) === objetivo)) {
    lista.value = objetivo;
  }
  await seleccionarUsuario(lista.value);
}

async function seleccionarUsuario(id) {
  usuarioActual = id ? Number(id) : null;
  guardarUsuarioSeleccionado(usuarioActual);
  $("campos-sesion").disabled = !usuarioActual;
  $("msg-sin-usuario").hidden = Boolean(usuarioActual);
  if (!usuarioActual) {
    $("panel-zona").hidden = true;
    pintarHistorico([]);
    return;
  }
  await cargarHistorico();
}

function pintarZona(usuario) {
  const z = usuario.zona2;
  $("z-inf").textContent = z.zona2_inferior;
  $("z-sup").textContent = z.zona2_superior;
  $("z-max").textContent = z.fc_maxima + " lpm";
  $("z-res").textContent = z.reserva + " lpm";
  $("z-rep").textContent = z.fc_reposo + " lpm";
  $("panel-zona").hidden = false;
}

// ------------------------------------------------------------- histórico
const ETIQUETAS = {
  dentro: "Dentro de zona 2",
  debajo: "Debajo de zona 2",
  encima: "Encima de zona 2",
};

function celda(texto, clase) {
  const td = document.createElement("td");
  td.textContent = texto;
  if (clase) td.className = clase;
  return td;
}

function pintarHistorico(sesiones) {
  const cuerpo = $("cuerpo-historico");
  cuerpo.replaceChildren();
  $("vacio").hidden = sesiones.length > 0;

  sesiones.forEach((s) => {
    const fila = document.createElement("tr");
    fila.append(
      celda(s.fecha),
      celda(s.duracion_min + " min"),
      celda(s.fc_promedio + " lpm"),
    );

    const tdEstado = document.createElement("td");
    const insignia = document.createElement("span");
    insignia.className = "insignia " + s.estado_zona;
    insignia.textContent = ETIQUETAS[s.estado_zona] || s.estado_zona;
    tdEstado.append(insignia);
    fila.append(tdEstado);

    fila.append(celda(s.pct_tiempo_zona2 === null ? "—" : s.pct_tiempo_zona2 + " %"));

    const tdAccion = document.createElement("td");
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "peligro";
    boton.textContent = "Eliminar";
    boton.setAttribute("aria-label", "Eliminar la sesión del " + s.fecha);
    boton.addEventListener("click", () => eliminarSesion(s.id));
    tdAccion.append(boton);
    fila.append(tdAccion);

    cuerpo.append(fila);
  });
}

async function cargarHistorico() {
  if (!usuarioActual) return;
  const parametros = new URLSearchParams();
  if ($("f-desde").value) parametros.set("desde", $("f-desde").value);
  if ($("f-hasta").value) parametros.set("hasta", $("f-hasta").value);
  const consulta = parametros.toString() ? "?" + parametros : "";
  const datos = await api(`/usuarios/${usuarioActual}/sesiones${consulta}`);
  pintarZona(datos.usuario);
  pintarHistorico(datos.sesiones);
}

async function eliminarSesion(id) {
  if (!confirm("¿Eliminar esta sesión? Esta acción no se puede deshacer.")) return;
  try {
    await api(`/usuarios/${usuarioActual}/sesiones/${id}`, { method: "DELETE" });
    aviso("Sesión eliminada.");
    await cargarHistorico();
  } catch (error) {
    aviso(error.message, "error");
  }
}

// ----------------------------------------------------------- formularios
$("sel-usuario").addEventListener("change", (e) => {
  seleccionarUsuario(e.target.value).catch((err) => aviso(err.message, "error"));
});

$("form-usuario").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const usuario = await api("/usuarios", {
      method: "POST",
      body: JSON.stringify(datosDeFormulario(e.target)),
    });
    e.target.reset();
    $("detalle-nuevo").open = false;
    aviso(`Usuario "${usuario.nombre}" guardado.`);
    await cargarUsuarios(usuario.id);
  } catch (error) {
    aviso(error.message, "error");
  }
});

$("form-sesion").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!usuarioActual) return;
  try {
    const datos = datosDeFormulario(e.target);
    if (datos.minutos_zona2 === "") delete datos.minutos_zona2;
    const sesion = await api(`/usuarios/${usuarioActual}/sesiones`, {
      method: "POST",
      body: JSON.stringify(datos),
    });
    e.target.reset();
    $("s-fecha").value = hoy();
    aviso(`Sesión guardada: ${ETIQUETAS[sesion.estado_zona].toLowerCase()}.`);
    await cargarHistorico();
  } catch (error) {
    aviso(error.message, "error");
  }
});

$("form-filtro").addEventListener("submit", (e) => {
  e.preventDefault();
  cargarHistorico().catch((err) => aviso(err.message, "error"));
});

$("btn-limpiar").addEventListener("click", () => {
  $("f-desde").value = "";
  $("f-hasta").value = "";
  cargarHistorico().catch((err) => aviso(err.message, "error"));
});

// ---------------------------------------------------------------- inicio
$("s-fecha").value = hoy();
$("s-fecha").max = hoy();
cargarUsuarios().catch((err) => aviso(err.message, "error"));