import csv
import io
import traceback
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, EmailStr
import os
import hashlib
from supabase import create_client, Client

app = FastAPI(title="MaxShop - Red de Comercios & Ahorro", version="9.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

class ComercioModel(BaseModel):
    nombre_completo: str
    correo: str
    whatsapp: str
    nombre_fantasias: str
    rubro: str
    direccion: str
    localidad: str
    cuit_cuil: str
    descuento_base_diario: float = 5.0
    porcentaje_campana: float = 20.0
    dias_campana: str = "Martes y Jueves"
    logo_url: str = ""
    fotos_url: str = ""

class UsuarioRegistroModel(BaseModel):
    nombre_completo: str
    dni: str
    direccion: str
    localidad: str
    whatsapp: str
    correo: EmailStr
    password: str

class UsuarioLoginModel(BaseModel):
    correo: EmailStr
    password: str

class ConsumoQRModel(BaseModel):
    correo_usuario: str
    nombre_comercio: str
    monto_compra: float

def encriptar_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.get("/", response_class=HTMLResponse)
def mostrar_interfaz():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop & AsistMax - Red de Comercios</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950">

        <div id="toastContainer" class="fixed top-20 right-4 z-50 flex flex-col space-y-2 pointer-events-none"></div>
        <div id="modalLoader" class="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 hidden flex items-center justify-center">
            <div class="bg-slate-900 border border-slate-800 p-5 rounded-3xl text-center shadow-xl space-y-3">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
                <p class="text-sm text-slate-300" id="loaderText">Procesando...</p>
            </div>
        </div>

        <a href="https://wa.me/5493834000000?text=Hola,%20necesito%20asistencia%20con%20el%20sistema%20MaxShop." target="_blank" class="fixed bottom-6 right-6 z-50 bg-emerald-500 hover:bg-emerald-400 text-slate-950 p-4 rounded-full shadow-2xl flex items-center justify-center transition transform hover:scale-105 border border-emerald-300/50" title="Asistencia IA">
            <span class="text-2xl">💬</span>
        </a>

        <header class="w-full px-4 py-3 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/95 backdrop-blur-md sticky top-0 z-50 shadow-lg">
            <div class="flex items-center space-x-3">
                <img src="https://i.ibb.co/rRGzqgnx/logo.jpg" alt="MaxShop Logo" class="w-auto h-auto max-h-12 object-contain bg-slate-900">
                <div class="flex flex-col">
                    <span class="text-xs font-black tracking-wider text-white">MAXSHOP <span class="text-cyan-400 font-light">| AsistMax</span></span>
                    <span class="text-[10px] text-cyan-400 font-semibold tracking-widest uppercase">Red de Comercios & Ahorro</span>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button type="button" id="btnLogin" class="text-xs bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-400 px-3 py-1.5 rounded-xl border border-cyan-500/30 transition font-semibold cursor-pointer">🔑 Login</button>
                <button type="button" id="btnAdmin" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-xl border border-slate-700 transition font-medium cursor-pointer">⚙️ Admin</button>
            </div>
        </header>

        <main class="w-full max-w-md mx-auto px-4 py-6 space-y-6 flex-1">

            <div class="w-full flex justify-center items-center">
                <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="MaxShop Banner" class="w-auto max-w-full h-auto object-contain block rounded-2xl shadow-lg border border-slate-800/60">
            </div>

            <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-4">
                <div class="flex justify-between items-center">
                    <span class="text-[10px] uppercase tracking-wider text-emerald-400 font-bold bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-800/50" id="lblEstadoPlan">Plan Gratuito Activo</span>
                    <span class="text-[10px] text-slate-400" id="lblVencimientoPlan">Descuento Base 50%</span>
                </div>
                <div class="flex justify-between items-center">
                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase">Crédito de Ahorro</h3>
                        <p class="text-2xl font-black text-emerald-400 mt-0.5" id="lblCreditoDisponible">$0</p>
                    </div>
                    <button type="button" id="btnVerPlanes" class="text-xs bg-cyan-500 hover:bg-cyan-400 text-slate-950 px-3.5 py-2 rounded-xl font-extrabold shadow-lg shadow-cyan-500/20 transition cursor-pointer">📋 Ver Planes</button>
                </div>

                <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80">
                    <button type="button" id="btnRecargaExpres" class="bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 p-2.5 rounded-2xl border border-cyan-500/30 text-center transition cursor-pointer">
                        <span class="block text-xs font-bold">⚡ Recarga Exprés</span>
                        <span class="block text-[10px] text-slate-400">+$10k por $500 (MP)</span>
                    </button>
                    <button type="button" id="btnPlanPro" class="bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 p-2.5 rounded-2xl text-center shadow-md font-bold transition hover:opacity-90 cursor-pointer">
                        <span class="block text-xs font-black">⭐ Plan Pro Mensual</span>
                        <span class="block text-[9px] text-slate-950/80">$5.000/mes (MP)</span>
                    </button>
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-xl font-bold text-white mt-2">Canjear Descuento en Comercio</h2>
                <div class="mt-4">
                    <button type="button" id="btnEscanearQR" class="w-full py-3.5 text-sm font-bold text-slate-950 transition-all bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl shadow-lg cursor-pointer">📷 Escanear QR del Comercio</button>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <button type="button" id="btnSumarComercio" class="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl text-left cursor-pointer">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white">Sumar mi Comercio</h3>
                </button>
                <button type="button" id="btnConocerBeneficios" class="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl text-left cursor-pointer">
                    <div class="text-blue-400 text-xl mb-1">📋</div>
                    <h3 class="text-xs font-bold text-white">Conocer Beneficios</h3>
                </button>
            </div>

            <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 space-y-4 shadow-xl">
                <h3 class="text-sm font-extrabold text-white">🏪 Comercios Adheridos</h3>
                <input type="text" id="inputBuscadorComercios" placeholder="Buscar por nombre, rubro..." class="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-2.5 text-xs text-white outline-none">
                <div id="listaComerciosPublicos" class="space-y-2.5 max-h-64 overflow-y-auto">Cargando...</div>
            </div>
        </main>

        <!-- Modales -->
        <div id="authModal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white" id="authTitle">🔑 Iniciar Sesión</h3>
                    <button type="button" id="btnCloseAuth" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <div id="panelSesionContainer" class="space-y-4 hidden">
                    <p class="text-xs text-emerald-400">Sesión activa</p>
                    <button type="button" id="btnCerrarSesion" class="w-full py-2 bg-rose-500/20 text-rose-400 rounded-xl font-bold cursor-pointer">Cerrar Sesión</button>
                </div>
                <form id="authForm" class="space-y-3 text-xs">
                    <div id="camposRegistro" class="space-y-3 hidden">
                        <input type="text" id="reg_nombre" placeholder="Nombre Completo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        <input type="text" id="reg_dni" placeholder="DNI" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        <input type="text" id="reg_dir" placeholder="Dirección" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        <input type="text" id="reg_loc" placeholder="Localidad" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        <input type="text" id="reg_wpp" placeholder="WhatsApp" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    </div>
                    <input type="email" id="auth_correo" required placeholder="Correo Electrónico" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <input type="password" id="auth_password" required placeholder="Contraseña" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <button type="submit" id="btnSubmitAuth" class="w-full py-3 bg-cyan-400 text-slate-950 font-bold rounded-xl cursor-pointer">Ingresar</button>
                    <div class="text-center pt-2">
                        <span id="toggleAuthText" class="text-cyan-400 cursor-pointer hover:underline">¿No tienes cuenta? Regístrate aquí</span>
                    </div>
                </form>
            </div>
        </div>

        <div id="modalQR" class="fixed inset-0 bg-slate-950/95 z-50 hidden flex flex-col items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 text-center">
                <button type="button" id="btnCloseQR" class="text-cyan-400 text-xs font-bold cursor-pointer">Volver / Cerrar</button>
                <div id="reader" class="w-full overflow-hidden rounded-2xl bg-slate-950 min-h-[220px]"></div>
            </div>
        </div>

        <div id="modalMontoVenta" class="fixed inset-0 bg-slate-950/90 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 text-xs">
                <h3 class="text-sm font-bold text-white">💳 Canjear Descuento</h3>
                <p class="text-slate-400">Comercio: <strong id="lblComercioEscaneado" class="text-cyan-400"></strong></p>
                <input type="number" id="inputMontoCompra" placeholder="Monto compra ($)" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                <button type="button" id="btnConfirmarConsumo" class="w-full py-3 bg-cyan-400 text-slate-950 font-bold rounded-xl cursor-pointer">Aplicar Descuento</button>
                <button type="button" id="btnCloseVenta" class="w-full py-2 bg-slate-800 text-white rounded-xl cursor-pointer">Cancelar</button>
            </div>
        </div>

        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white">🏪 Sumar mi Comercio</h3>
                    <button type="button" id="btnCloseComercio" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <form id="formComercio" class="space-y-3 text-xs">
                    <input type="text" id="c_nombre" required placeholder="Nombre Completo Titular" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <input type="email" id="c_correo" required placeholder="Correo Electrónico" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <input type="text" id="c_wpp" required placeholder="WhatsApp" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <input type="text" id="c_fantasia" required placeholder="Nombre de Fantasía" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <select id="c_rubro" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                        <option value="Supermercados">Supermercados</option>
                        <option value="Gastronomía">Gastronomía</option>
                        <option value="Indumentaria">Indumentaria</option>
                        <option value="Otro">Otro</option>
                    </select>
                    <input type="text" id="c_dir" required placeholder="Dirección" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <input type="text" id="c_loc" required placeholder="Localidad" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <input type="text" id="c_cuit" required placeholder="CUIT / CUIL" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white">
                    <button type="submit" class="w-full py-3 bg-cyan-400 text-slate-950 font-bold rounded-xl cursor-pointer">Registrar Comercio</button>
                </form>
            </div>
        </div>

        <div id="modalPlanesDetallados" class="fixed inset-0 bg-slate-950/85 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-3xl p-6 space-y-4">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white">📋 Opciones de Membresía</h3>
                    <button type="button" id="btnClosePlanes" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <button type="button" id="btnRegPlanGratis" class="w-full py-2.5 bg-emerald-500/20 text-emerald-400 rounded-xl font-bold cursor-pointer">Registrarme en Plan Gratuito</button>
                <button type="button" id="btnPagarPlanProModal" class="w-full py-2.5 bg-cyan-400 text-slate-950 rounded-xl font-bold cursor-pointer">Pagar Plan Pro ($5.000)</button>
            </div>
        </div>

        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-4xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-base font-bold text-white">⚙️ Panel Admin</h3>
                    <button type="button" id="btnCloseAdmin" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <div id="tablaComerciosAdminList" class="text-xs text-slate-300">Cargando...</div>
            </div>
        </div>

        <script>
            let html5QrCode = null;
            let listaComerciosGlobal = [];
            let comercioEscaneadoActual = null;
            let usuarioLogueadoGlobal = null;
            let modoRegistroAuth = false;

            // Función universal ejecutada por reintento de seguridad para garantizar cero estática
            function inicializarBotonesSeguros() {
                const vincular = (id, evento, fn) => {
                    const el = document.getElementById(id);
                    if (el && !el.dataset.vinculado) {
                        el.addEventListener(evento, fn);
                        el.dataset.vinculado = "true";
                    }
                };

                vincular('btnLogin', 'click', () => abrirModalAuth('login'));
                vincular('btnAdmin', 'click', abrirAdmin);
                vincular('btnVerPlanes', 'click', () => document.getElementById('modalPlanesDetallados').classList.remove('hidden'));
                vincular('btnConocerBeneficios', 'click', () => document.getElementById('modalPlanesDetallados').classList.remove('hidden'));
                vincular('btnRecargaExpres', 'click', iniciarPagoRecargaExpres);
                vincular('btnPlanPro', 'click', iniciarPagoPlanPro);
                vincular('btnEscanearQR', 'click', iniciarEscaneoQR);
                vincular('btnSumarComercio', 'click', () => document.getElementById('modalComercio').classList.remove('hidden'));
                
                vincular('btnCloseAuth', 'click', () => document.getElementById('authModal').classList.add('hidden'));
                vincular('btnCloseQR', 'click', detenerEscaneoQR);
                vincular('btnCloseVenta', 'click', () => document.getElementById('modalMontoVenta').classList.add('hidden'));
                vincular('btnCloseComercio', 'click', () => document.getElementById('modalComercio').classList.add('hidden'));
                vincular('btnClosePlanes', 'click', () => document.getElementById('modalPlanesDetallados').classList.add('hidden'));
                vincular('btnCloseAdmin', 'click', () => document.getElementById('modalAdmin').classList.add('hidden'));

                vincular('toggleAuthText', 'click', cambiarModoAuth);
                vincular('authForm', 'submit', procesarAutenticacion);
                vincular('formComercio', 'submit', enviarComercio);
                vincular('btnCerrarSesion', 'click', cerrarSesion);
                vincular('btnConfirmarConsumo', 'click', confirmarConsumoCredito);
                vincular('btnRegPlanGratis', 'click', () => { document.getElementById('modalPlanesDetallados').classList.add('hidden'); abrirModalAuth('registro'); });
                vincular('btnPagarPlanProModal', 'click', () => { document.getElementById('modalPlanesDetallados').classList.add('hidden'); iniciarPagoPlanPro(); });

                const buscador = document.getElementById('inputBuscadorComercios');
                if(buscador && !buscador.dataset.vinculado) {
                    buscador.addEventListener('input', (e) => {
                        let txt = e.target.value.toLowerCase();
                        let filtrados = listaComerciosGlobal.filter(c => c.nombre_fantasias.toLowerCase().includes(txt) || c.rubro.toLowerCase().includes(txt));
                        renderizarComercios(filtrados);
                    });
                    buscador.dataset.vinculado = "true";
                }
            }

            window.addEventListener('DOMContentLoaded', () => {
                inicializarBotonesSeguros();
                setTimeout(inicializarBotonesSeguros, 500); // Doble reintento dinámico anti-estática
                cargarComerciosPublicos();
                let sesion = localStorage.getItem('maxshop_correo_usuario');
                if(sesion) verificarEstadoUsuario(sesion);
            });

            function mostrarToast(mensaje, tipo = 'success') {
                const contenedor = document.getElementById('toastContainer');
                if(!contenedor) return;
                const toast = document.createElement('div');
                toast.className = `p-3 rounded-xl border text-xs font-bold ${tipo === 'error' ? 'bg-rose-950 text-rose-400' : 'bg-emerald-950 text-emerald-400'}`;
                toast.innerText = mensaje;
                contenedor.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
            }

            function abrirModalAuth(modo) {
                document.getElementById('authModal').classList.remove('hidden');
                if (modo === 'registro' && !modoRegistroAuth) cambiarModoAuth();
                if (modo === 'login' && modoRegistroAuth) cambiarModoAuth();
                
                if (usuarioLogueadoGlobal) {
                    document.getElementById('authForm').classList.add('hidden');
                    document.getElementById('panelSesionContainer').classList.remove('hidden');
                } else {
                    document.getElementById('authForm').classList.remove('hidden');
                    document.getElementById('panelSesionContainer').classList.add('hidden');
                }
            }

            function cambiarModoAuth() {
                modoRegistroAuth = !modoRegistroAuth;
                const camposReg = document.getElementById('camposRegistro');
                const titulo = document.getElementById('authTitle');
                const btnSubmit = document.getElementById('btnSubmitAuth');
                const toggleText = document.getElementById('toggleAuthText');

                if (modoRegistroAuth) {
                    camposReg.classList.remove('hidden');
                    titulo.innerText = '🎁 Registro de Usuario';
                    btnSubmit.innerText = 'Registrarse y Activar';
                    toggleText.innerText = '¿Ya tienes cuenta? Inicia sesión aquí';
                } else {
                    camposReg.classList.add('hidden');
                    titulo.innerText = '🔑 Iniciar Sesión';
                    btnSubmit.innerText = 'Ingresar';
                    toggleText.innerText = '¿No tienes cuenta? Regístrate aquí';
                }
            }

            async function procesarAutenticacion(e) {
                e.preventDefault();
                let correo = document.getElementById('auth_correo').value.trim();
                let password = document.getElementById('auth_password').value;

                if (modoRegistroAuth) {
                    let payload = {
                        nombre_completo: document.getElementById('reg_nombre').value,
                        dni: document.getElementById('reg_dni').value,
                        direccion: document.getElementById('reg_dir').value,
                        localidad: document.getElementById('reg_loc').value,
                        whatsapp: document.getElementById('reg_wpp').value,
                        correo: correo,
                        password: password
                    };
                    let res = await fetch('/api/registro', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                    if(res.ok) {
                        mostrarToast("¡Cuenta creada con éxito y $50.000 de saldo!");
                        verificarEstadoUsuario(correo);
                        document.getElementById('authModal').classList.add('hidden');
                    } else {
                        mostrarToast("Error en el registro", "error");
                    }
                } else {
                    let res = await fetch('/api/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: correo, password: password })
                    });
                    let json = await res.json();
                    if(res.ok) {
                        mostrarToast("¡Sesión iniciada con éxito!");
                        verificarEstadoUsuario(json.usuario.correo);
                        document.getElementById('authModal').classList.add('hidden');
                    } else {
                        mostrarToast("Correo o contraseña incorrectos", "error");
                    }
                }
            }

            function cerrarSesion() {
                localStorage.removeItem('maxshop_correo_usuario');
                usuarioLogueadoGlobal = null;
                location.reload();
            }

            async function verificarEstadoUsuario(correo) {
                try {
                    let res = await fetch(`/api/usuario/${correo}`);
                    let json = await res.json();
                    if(json.success) {
                        usuarioLogueadoGlobal = json.data;
                        localStorage.setItem('maxshop_correo_usuario', correo);
                        let esPro = usuarioLogueadoGlobal.es_pro || false;
                        document.getElementById('lblEstadoPlan').innerText = esPro ? "⭐ Plan Pro Activo" : "⚡ Plan Gratuito Activo";
                        document.getElementById('lblCreditoDisponible').innerText = "$" + (usuarioLogueadoGlobal.credito_descuento_disponible || 0).toLocaleString();
                    }
                } catch(e) {}
            }

            async function cargarComerciosPublicos() {
                try {
                    let res = await fetch('/api/comercios');
                    let json = await res.json();
                    if(json.success) {
                        listaComerciosGlobal = json.data;
                        renderizarComercios(listaComerciosGlobal);
                    }
                } catch(e) { listaComerciosGlobal = []; }
            }

            function renderizarComercios(comercios) {
                const contenedor = document.getElementById('listaComerciosPublicos');
                if(!contenedor) return;
                if(!comercios || comercios.length === 0) {
                    contenedor.innerHTML = `<div class="text-center text-slate-500 text-xs">No hay comercios.</div>`;
                    return;
                }
                let html = '';
                comercios.forEach(c => {
                    html += `<div class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center text-xs">
                        <div><b>${c.nombre_fantasias}</b><br><span class="text-[10px] text-cyan-400">5% Base + ${c.porcentaje_campana || 20}% (${c.dias_campana})</span></div>
                        <a href="https://wa.me/${c.whatsapp}" target="_blank" class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded">WhatsApp</a>
                    </div>`;
                });
                contenedor.innerHTML = html;
            }

            function iniciarPagoPlanPro() {
                if(!usuarioLogueadoGlobal) { mostrarToast("Inicia sesión primero", "error"); abrirModalAuth('login'); return; }
                if(confirm("Redirigiendo a Mercado Pago para abonar Plan Pro ($5.000)...")) {
                    fetch('/api/suscripcion-pro', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: usuarioLogueadoGlobal.correo })
                    }).then(r => r.json()).then(res => {
                        if(res.success) { mostrarToast("¡Plan Pro Activado!"); verificarEstadoUsuario(usuarioLogueadoGlobal.correo); }
                    });
                }
            }

            function iniciarPagoRecargaExpres() {
                if(!usuarioLogueadoGlobal) { mostrarToast("Inicia sesión primero", "error"); abrirModalAuth('login'); return; }
                if(confirm("Redirigiendo a Mercado Pago para Recarga Exprés ($500)...")) {
                    fetch('/api/recarga-expres', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: usuarioLogueadoGlobal.correo })
                    }).then(r => r.json()).then(res => {
                        if(res.success) { mostrarToast("¡Recarga Exitosa!"); verificarEstadoUsuario(usuarioLogueadoGlobal.correo); }
                    });
                }
            }

            function iniciarEscaneoQR() {
                if(!usuarioLogueadoGlobal) { mostrarToast("Inicia sesión primero", "error"); abrirModalAuth('login'); return; }
                document.getElementById('modalQR').classList.remove('hidden');
                if (!html5QrCode) html5QrCode = new Html5Qrcode("reader");
                html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: 200 }, (decodedText) => {
                    detenerEscaneoQR();
                    comercioEscaneadoActual = decodedText;
                    document.getElementById('lblComercioEscaneado').innerText = decodedText;
                    document.getElementById('modalMontoVenta').classList.remove('hidden');
                }).catch(() => {});
            }

            function detenerEscaneoQR() {
                if (html5QrCode && html5QrCode.isScanning) {
                    html5QrCode.stop().then(() => document.getElementById('modalQR').classList.add('hidden'));
                } else { document.getElementById('modalQR').classList.add('hidden'); }
            }

            async function confirmarConsumoCredito() {
                let monto = parseFloat(document.getElementById('inputMontoCompra').value) || 0;
                if(monto <= 0) { mostrarToast("Monto inválido", "error"); return; }
                let res = await fetch('/api/consumir-credito', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ correo_usuario: usuarioLogueadoGlobal.correo, nombre_comercio: comercioEscaneadoActual, monto_compra: monto })
                });
                let json = await res.json();
                if(json.success) {
                    mostrarToast(`¡Descuento aplicado! Ahorro: $${json.ahorro_aplicado}`);
                    document.getElementById('modalMontoVenta').classList.add('hidden');
                    verificarEstadoUsuario(usuarioLogueadoGlobal.correo);
                } else {
                    mostrarToast(json.detail || "Error", "error");
                }
            }

            async function enviarComercio(e) {
                e.preventDefault();
                let data = {
                    nombre_completo: document.getElementById('c_nombre').value,
                    correo: document.getElementById('c_correo').value,
                    whatsapp: document.getElementById('c_wpp').value,
                    nombre_fantasias: document.getElementById('c_fantasia').value,
                    rubro: document.getElementById('c_rubro').value,
                    direccion: document.getElementById('c_dir').value,
                    localidad: document.getElementById('c_loc').value,
                    cuit_cuil: document.getElementById('c_cuit').value,
                    descuento_base_diario: 5.0,
                    porcentaje_campana: 20.0,
                    dias_campana: "Martes y Jueves"
                };
                let res = await fetch('/api/registrar-comercio', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                if(res.ok) {
                    mostrarToast("¡Comercio registrado con éxito!");
                    document.getElementById('modalComercio').classList.add('hidden');
                    cargarComerciosPublicos();
                } else {
                    mostrarToast("Error al registrar comercio", "error");
                }
            }

            function abrirAdmin() {
                let c = prompt("Clave Admin:");
                if(c === "AsistMaxAdmin2026Secure") {
                    document.getElementById('modalAdmin').classList.remove('hidden');
                    cargarDatosAdmin();
                } else if(c !== null) { mostrarToast("Clave incorrecta", "error"); }
            }

            async function cargarDatosAdmin() {
                let res = await fetch('/api/admin/datos');
                let json = await res.json();
                if(json.success) {
                    document.getElementById('tablaComerciosAdminList').innerHTML = json.comercios.map(c => `<div class="p-2 border-b border-slate-800"><b>${c.nombre_fantasias}</b> (${c.rubro})</div>`).join('') || 'Sin comercios';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/registro")
def registrar_usuario_seguro(u: UsuarioRegistroModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        data = u.dict()
        password_plana = data.pop("password")
        data["password_hash"] = encriptar_password(password_plana)
        data["es_pro"] = False
        data["credito_descuento_disponible"] = 50000
        supabase.table("usuarios").insert(data).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
def iniciar_sesion_seguro(cred: UsuarioLoginModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("*").eq("correo", cred.correo).execute()
        if not res.data: raise HTTPException(status_code=401, detail="Error")
        user = res.data[0]
        if user.get("password_hash") != encriptar_password(cred.password):
            raise HTTPException(status_code=401, detail="Error")
        return {"success": True, "usuario": user}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/usuario/{correo}")
def obtener_usuario(correo: str):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if res.data: return {"success": True, "data": res.data[0]}
        return {"success": False}
    except: return {"success": False}

@app.get("/api/comercios")
def obtener_comercios():
    if not supabase: return {"success": False, "data": []}
    try:
        res = supabase.table("comercios").select("*").execute()
        return {"success": True, "data": res.data}
    except: return {"success": False, "data": []}

@app.post("/api/registrar-comercio")
def registrar_comercio(c: ComercioModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("comercios").insert(c.dict()).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/datos")
def admin_datos():
    if not supabase: return {"success": False, "comercios": [], "usuarios": []}
    try:
        rc = supabase.table("comercios").select("*").execute()
        ru = supabase.table("usuarios").select("*").execute()
        return {"success": True, "comercios": rc.data, "usuarios": ru.data}
    except: return {"success": False, "comercios": [], "usuarios": []}

@app.post("/api/suscripcion-pro")
def suscripcion_pro(payload: dict):
    correo = payload.get("correo")
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("credito_descuento_disponible").eq("correo", correo).execute()
        actual = float(res.data[0].get("credito_descuento_disponible", 0)) if res.data else 0
        nuevo = actual + 50000
        supabase.table("usuarios").update({"es_pro": True, "credito_descuento_disponible": nuevo}).eq("correo", correo).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/recarga-expres")
def recarga_expres(payload: dict):
    correo = payload.get("correo")
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("credito_descuento_disponible").eq("correo", correo).execute()
        actual = float(res.data[0].get("credito_descuento_disponible", 0)) if res.data else 0
        nuevo = actual + 10000
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo}).eq("correo", correo).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/consumir-credito")
def consumir_credito(consumo: ConsumoQRModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        c_res = supabase.table("comercios").select("porcentaje_campana").eq("nombre_fantasias", consumo.nombre_comercio).execute()
        pct_campana = 20.0
        if c_res.data: pct_campana = float(c_res.data[0].get("porcentaje_campana", 20.0))

        u_res = supabase.table("usuarios").select("*").eq("correo", consumo.correo_usuario).execute()
        if not u_res.data: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user = u_res.data[0]
        es_pro = user.get("es_pro", False)
        pct_aplicado = pct_campana if es_pro else (pct_campana * 0.5)

        credito_disponible = float(user.get("credito_descuento_disponible", 0))
        ahorro = consumo.monto_compra * (pct_aplicado / 100.0)

        if credito_disponible < ahorro:
            raise HTTPException(status_code=400, detail="Crédito de descuento insuficiente.")

        nuevo_credito = credito_disponible - ahorro
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_credito}).eq("correo", consumo.correo_usuario).execute()

        return {"success": True, "ahorro_aplicado": ahorro, "credito_restante": nuevo_credito}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
