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

app = FastAPI(title="MaxShop - Red de Comercios & Ahorro", version="9.7")

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
    porcentaje_descuento: float = 20.0
    dia_promocion: str = "Todos los días"
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
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950" onload="inicializarApp()">

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
                <button onclick="abrirModalAuth('login')" class="text-xs bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-3 py-1.5 rounded-xl border border-cyan-500/30 transition font-semibold cursor-pointer">🔑 Login</button>
                <button onclick="abrirAdmin()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-xl border border-slate-700 transition font-medium cursor-pointer">⚙️ Admin</button>
            </div>
        </header>

        <main class="w-full max-w-md mx-auto px-4 py-6 space-y-6 flex-1">

            <div class="w-full flex justify-center items-center">
                <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="MaxShop Banner" class="w-auto max-w-full h-auto object-contain block">
            </div>

            <!-- Panel de Estado del Usuario -->
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
                    <button onclick="abrirModalPlanesDetallados()" class="text-xs bg-cyan-500 hover:bg-cyan-400 text-slate-950 px-3.5 py-2 rounded-xl font-extrabold shadow-lg shadow-cyan-500/20 transition cursor-pointer">📋 Ver Beneficios</button>
                </div>

                <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80">
                    <button onclick="ejecutarRecargaExpres()" class="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 p-2.5 rounded-2xl border border-cyan-500/30 text-center transition cursor-pointer">
                        <span class="block text-xs font-bold">⚡ Recarga Exprés</span>
                        <span class="block text-[10px] text-slate-400">+$10k crédito por $500</span>
                    </button>
                    <button onclick="ejecutarSuscripcionPro()" class="bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 p-2.5 rounded-2xl text-center shadow-md font-bold transition hover:opacity-90 cursor-pointer">
                        <span class="block text-xs font-black">⭐ Plan Pro Mensual</span>
                        <span class="block text-[9px] text-slate-950/80">$5.000/mes (Pase Libre)</span>
                    </button>
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-xl font-bold text-white mt-2">Canjear Descuento en Comercio</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el código QR del comercio adherido para aplicar tu descuento instantáneo.</p>
                <div class="mt-4">
                    <button onclick="iniciarEscaneoQR()" class="w-full py-3.5 text-sm font-bold text-slate-950 transition-all bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl shadow-lg shadow-cyan-500/20 cursor-pointer">📷 Escanear QR del Comercio</button>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <button onclick="abrirModalComercio()" class="bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl text-left transition-all group cursor-pointer">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-cyan-400 transition">Sumar mi Comercio</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Súmate a la red gratuita</p>
                </button>
                <button onclick="abrirModalPlanesDetallados()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group cursor-pointer">
                    <div class="text-blue-400 text-xl mb-1">📋</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Conocer Beneficios</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Información detallada</p>
                </button>
            </div>

            <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 space-y-4 shadow-xl">
                <div class="flex justify-between items-center">
                    <div>
                        <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-800/50">Vidriera Abierta</span>
                        <h3 class="text-sm font-extrabold text-white mt-1">🏪 Comercios Adheridos</h3>
                    </div>
                </div>
                <input type="text" id="inputBuscadorComercios" onkeyup="filtrarComerciosPublicos()" placeholder="Buscar por nombre, rubro o localidad..." class="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-2.5 text-xs text-white outline-none">
                <div id="listaComerciosPublicos" class="space-y-2.5 max-h-64 overflow-y-auto">Cargando...</div>
            </div>
        </main>

        <!-- Modales -->
        <div id="authModal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <button onclick="cerrarModalAuth()" class="text-cyan-400 text-xs font-bold bg-slate-950 px-2.5 py-1 rounded-xl border border-slate-800 cursor-pointer">⬅️ Volver</button>
                    <h3 class="text-sm font-bold text-white" id="authTitle">🔑 Iniciar Sesión</h3>
                    <button onclick="cerrarModalAuth()" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <div id="panelSesionContainer" class="space-y-4 hidden">
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 flex justify-between items-center">
                        <div>
                            <span class="text-[10px] text-cyan-400 font-bold uppercase" id="sesionTipoPlanLabel">Plan Gratuito</span>
                            <h4 class="text-xs font-bold text-white" id="nombreSesionLabel">Usuario</h4>
                        </div>
                        <button onclick="cerrarSesion()" class="text-[10px] bg-rose-500/10 text-rose-400 px-2.5 py-1 rounded-lg cursor-pointer">Cerrar Sesión</button>
                    </div>
                    <p class="text-xs text-slate-300">Crédito Disponible: <strong id="sesionCredito" class="text-emerald-400">$0</strong></p>
                </div>
                <form id="authForm" onsubmit="procesarAutenticacion(event)" class="space-y-3 text-xs">
                    <div id="camposRegistro" class="space-y-3 hidden">
                        <input type="text" id="reg_nombre" placeholder="Nombre Completo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                        <input type="text" id="reg_dni" placeholder="DNI" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="text" id="reg_dir" placeholder="Dirección" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                            <input type="text" id="reg_loc" placeholder="Localidad" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                        </div>
                        <input type="text" id="reg_wpp" placeholder="WhatsApp" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    </div>
                    <input type="email" id="auth_correo" required placeholder="Correo Electrónico" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <input type="password" id="auth_password" required placeholder="Contraseña" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <button type="submit" id="btnSubmitAuth" class="w-full py-3 bg-cyan-400 text-slate-950 font-bold rounded-xl cursor-pointer shadow-lg">Ingresar</button>
                    <div class="text-center pt-2">
                        <span onclick="cambiarModoAuth()" id="toggleAuthText" class="text-cyan-400 cursor-pointer hover:underline">¿No tienes cuenta? Regístrate aquí</span>
                    </div>
                </form>
            </div>
        </div>

        <div id="modalQR" class="fixed inset-0 bg-slate-950/95 z-50 hidden flex flex-col items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 text-center shadow-2xl">
                <div class="flex justify-between items-center">
                    <button onclick="detenerEscaneoQR()" class="text-cyan-400 text-xs font-bold bg-slate-950 px-2 py-1 rounded-xl border border-slate-800 cursor-pointer">⬅️ Volver</button>
                    <h3 class="text-sm font-bold text-white">📷 Escanear QR</h3>
                    <button onclick="detenerEscaneoQR()" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <div id="reader" class="w-full overflow-hidden rounded-2xl bg-slate-950 min-h-[220px]"></div>
                <button onclick="detenerEscaneoQR()" class="w-full py-2 bg-slate-800 text-white rounded-xl text-xs cursor-pointer">Cancelar</button>
            </div>
        </div>

        <div id="modalMontoVenta" class="fixed inset-0 bg-slate-950/90 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 text-xs shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                    <button onclick="cerrarModalVenta()" class="text-cyan-400 text-xs font-bold bg-slate-950 px-2 py-1 rounded-xl border border-slate-800 cursor-pointer">⬅️ Volver</button>
                    <h3 class="text-sm font-bold text-white">💳 Canjear Descuento</h3>
                    <button onclick="cerrarModalVenta()" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <p class="text-slate-400">Comercio: <strong id="lblComercioEscaneado" class="text-cyan-400"></strong></p>
                <p class="text-[11px] text-cyan-300 bg-cyan-950/50 p-2 rounded-xl border border-cyan-800/40" id="lblInfoDescuentoComercio"></p>
                <input type="number" id="inputMontoCompra" onkeyup="calcularDescuentoQR()" placeholder="Monto compra ($)" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-1">
                    <div class="flex justify-between text-slate-400"><span>Ahorro:</span> <span id="lblAhorroCalculado" class="text-cyan-400 font-bold">$0</span></div>
                    <div class="flex justify-between text-slate-400 pt-1 border-t border-slate-900"><span>Total final:</span> <span id="lblTotalFinal" class="text-emerald-400 font-black text-sm">$0</span></div>
                </div>
                <button onclick="confirmarConsumoCredito()" class="w-full py-3 bg-cyan-400 text-slate-950 font-bold rounded-xl cursor-pointer shadow-lg">Aplicar Descuento</button>
            </div>
        </div>

        <!-- Modal Sumar Comercio (Rubros completos y días de lunes a domingo) -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <button onclick="cerrarModalComercio()" class="text-cyan-400 text-xs font-bold bg-slate-950 px-2.5 py-1 rounded-xl border border-slate-800 cursor-pointer">⬅️ Volver</button>
                    <h3 class="text-sm font-bold text-white">🏪 Sumar mi Comercio</h3>
                    <button onclick="cerrarModalComercio()" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <form id="formComercio" onsubmit="enviarComercio(event)" class="space-y-3 text-xs">
                    <input type="text" id="c_nombre" required placeholder="Nombre Completo Titular" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <input type="email" id="c_correo" required placeholder="Correo Electrónico" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <input type="text" id="c_wpp" required placeholder="WhatsApp" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <input type="text" id="c_fantasia" required placeholder="Nombre de Fantasía" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    
                    <select id="c_rubro" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                        <option value="Supermercados, Almacenes y Autoservicios">Supermercados, Almacenes y Autoservicios</option>
                        <option value="Gastronomía (Restaurantes, Cafés, Bares)">Gastronomía (Restaurantes, Cafés, Bares)</option>
                        <option value="Indumentaria, Calzado y Marroquinería">Indumentaria, Calzado y Marroquinería</option>
                        <option value="Salud, Farmacias y Perfumerías">Salud, Farmacias y Perfumerías</option>
                        <option value="Electro, Tecnología y Hogar">Electro, Tecnología y Hogar</option>
                        <option value="Construcción, Ferretería y Pinturería">Construcción, Ferretería y Pinturería</option>
                        <option value="Automotor, Repuestos y Lubricentros">Automotor, Repuestos y Lubricentros</option>
                        <option value="Belleza, Estética y Peluquerías">Belleza, Estética y Peluquerías</option>
                        <option value="Entretenimiento, Turismo y Hotelería">Entretenimiento, Turismo y Hotelería</option>
                        <option value="Servicios Profesionales y Oficios">Servicios Profesionales y Oficios</option>
                        <option value="Otro">Otro</option>
                    </select>

                    <div class="grid grid-cols-2 gap-2">
                        <div class="bg-slate-950 border border-slate-800 rounded-xl p-2">
                            <label class="text-[10px] text-cyan-400 block font-semibold">Logo</label>
                            <input type="file" id="c_logo_file" accept="image/*" class="w-full text-[9px] text-slate-300">
                        </div>
                        <div class="bg-slate-950 border border-slate-800 rounded-xl p-2">
                            <label class="text-[10px] text-cyan-400 block font-semibold">Foto</label>
                            <input type="file" id="c_foto_file" accept="image/*" class="w-full text-[9px] text-slate-300">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <input type="number" id="c_porcentaje" value="20" placeholder="% Descuento" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                        <select id="c_dia_promo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                            <option value="Todos los días">Todos los días</option>
                            <option value="Lunes">Lunes</option>
                            <option value="Martes">Martes</option>
                            <option value="Miércoles">Miércoles</option>
                            <option value="Jueves">Jueves</option>
                            <option value="Viernes">Viernes</option>
                            <option value="Sábado">Sábado</option>
                            <option value="Domingo">Domingo</option>
                        </select>
                    </div>
                    <input type="text" id="c_dir" required placeholder="Dirección" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <input type="text" id="c_loc" required placeholder="Localidad" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <input type="text" id="c_cuit" required placeholder="CUIT / CUIL" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                    <div class="text-[10px] text-slate-400 space-y-1 pt-1">
                        <label class="flex items-center space-x-2 cursor-pointer">
                            <input type="checkbox" id="c_terminos" required class="rounded bg-slate-950 border-slate-800 text-cyan-500">
                            <span>Acepto términos y condiciones y acepto ofrecer un 5% todos los días en la red.</span>
                        </label>
                        <p class="text-cyan-400">ℹ️ Si desea saber más sobre otros costos, comunicarse al WhatsApp <a href="https://wa.me/5493834000000?text=Hola,%20quiero%20consultar%20costos%20para%20comercios" target="_blank" class="underline font-bold">👉 ℹ️ (Enlace WhatsApp)</a></p>
                    </div>
                    <button type="submit" class="w-full py-3 bg-cyan-400 text-slate-950 font-bold rounded-xl cursor-pointer shadow-lg">Registrar Comercio</button>
                </form>
            </div>
        </div>

        <!-- Modal Conocer Beneficios (Redacción corregida con "accederás") -->
        <div id="modalPlanesDetallados" class="fixed inset-0 bg-slate-950/85 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl text-xs">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <button onclick="cerrarModalPlanesDetallados()" class="text-cyan-400 text-xs font-bold bg-slate-950 px-2 py-1 rounded-xl border border-slate-800 cursor-pointer">⬅️ Volver</button>
                    <h3 class="text-sm font-bold text-white">📋 Opciones de Membresía & Beneficios</h3>
                    <button onclick="cerrarModalPlanesDetallados()" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                <div class="space-y-4 text-slate-300 leading-relaxed">
                    <div class="bg-slate-950 border border-emerald-500/30 rounded-2xl p-4 space-y-2">
                        <h4 class="text-emerald-400 font-bold text-sm">⚡ Plan Gratuito (Pase Libre)</h4>
                        <p>Al registrarte accederás a un plan totalmente gratuito, y por ser la primera vez te daremos <b>$50.000</b> en crédito para usarlos como más te guste en toda nuestra red de comercios adheridos. Además, tenés <b>5% de descuento todos los días</b> en toda la red. Con este plan obtienes <b>50% de descuento</b> del descuento promocionado por el comercio adherido. Si deseas tener 100% en tus descuentos proporcionados por el comercio, cámbiate al Plan Pro.</p>
                        <button onclick="cerrarModalPlanesDetallados(); abrirModalAuth('registro');" class="w-full py-2 bg-emerald-500/20 text-emerald-400 rounded-xl font-bold cursor-pointer">Registrarme en Plan Gratuito</button>
                    </div>
                    <div class="bg-slate-950 border border-cyan-500/30 rounded-2xl p-4 space-y-2">
                        <h4 class="text-cyan-400 font-bold text-sm">⚡ Recarga Exprés ($500)</h4>
                        <p>Si te quedas sin saldo, realiza una recarga rápida de <b>$10.000 extra de crédito</b> abonando únicamente <b>$500</b> mediante plataforma de pago segura.</p>
                        <button onclick="cerrarModalPlanesDetallados(); ejecutarRecargaExpres();" class="w-full py-2 bg-cyan-500/20 text-cyan-300 rounded-xl font-bold cursor-pointer">Realizar Recarga Exprés</button>
                    </div>
                    <div class="bg-slate-950 border border-cyan-500/50 rounded-2xl p-4 space-y-2">
                        <h4 class="text-cyan-400 font-bold text-sm">⭐ Plan Pro Mensual ($5.000 / mes)</h4>
                        <p>Suscripción mensual automática. Disfrutas del <b>100% del descuento</b> proporcionado por el comercio sin recortes. No requiere saldo acumulado extra, ya que tienes un plan completo y libre de restricciones.</p>
                        <button onclick="cerrarModalPlanesDetallados(); ejecutarSuscripcionPro();" class="w-full py-2 bg-cyan-400 text-slate-950 rounded-xl font-bold cursor-pointer">Pagar Plan Pro ($5.000/mes)</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Panel de Administrador Avanzado Sectorizado -->
        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-5xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl text-xs">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <button onclick="cerrarAdmin()" class="text-cyan-400 text-xs font-bold bg-slate-950 px-2 py-1 rounded-xl border border-slate-800 cursor-pointer">⬅️ Volver</button>
                    <h3 class="text-base font-bold text-white">⚙️ Panel de Control & Auditoría MaxShop</h3>
                    <button onclick="cerrarAdmin()" class="text-slate-400 font-bold cursor-pointer">✕</button>
                </div>
                
                <div class="flex border-b border-slate-800 space-x-4 pb-2 overflow-x-auto">
                    <button onclick="cambiarPestanaAdmin('comercios')" id="btnTabComercios" class="font-bold text-cyan-400 border-b-2 border-cyan-400 pb-1 cursor-pointer">🏪 Comercios & Planes Titulares</button>
                    <button onclick="cambiarPestanaAdmin('usuarios')" id="btnTabUsuarios" class="font-bold text-slate-400 pb-1 cursor-pointer">👤 Clientes Registrados</button>
                    <button onclick="cambiarPestanaAdmin('acciones')" id="btnTabAcciones" class="font-bold text-slate-400 pb-1 cursor-pointer">📊 Informe de Recargas & Acciones</button>
                </div>

                <div id="seccionComerciosAdmin" class="space-y-2">
                    <h4 class="font-bold text-cyan-400 uppercase">Listado de Comercios Adheridos y Planes de Titulares</h4>
                    <div id="tablaComerciosAdminList" class="space-y-2">Cargando...</div>
                </div>

                <div id="seccionUsuariosAdmin" class="space-y-2 hidden">
                    <h4 class="font-bold text-blue-400 uppercase">Clientes / Usuarios Registrados</h4>
                    <div id="tablaUsuariosAdminList" class="space-y-2">Cargando...</div>
                </div>

                <div id="seccionAccionesAdmin" class="space-y-2 hidden">
                    <h4 class="font-bold text-emerald-400 uppercase">Auditoría de Recargas Exprés, Pro y Transacciones</h4>
                    <div id="tablaAccionesAdminList" class="space-y-2">Cargando registro de transacciones...</div>
                </div>
            </div>
        </div>

        <script>
            let html5QrCode = null;
            let listaComerciosGlobal = [];
            let comercioEscaneadoActual = null;
            let usuarioLogueadoGlobal = null;
            let modoRegistroAuth = false;
            let porcentajeDescActual = 20.0;

            function mostrarToast(mensaje, tipo = 'success') {
                const contenedor = document.getElementById('toastContainer');
                if(!contenedor) return;
                const toast = document.createElement('div');
                toast.className = `p-3 rounded-2xl border text-xs font-bold ${tipo === 'error' ? 'bg-rose-950 border-rose-500/40 text-rose-400' : 'bg-emerald-950 border-emerald-500/40 text-emerald-400'} shadow-xl`;
                toast.innerText = mensaje;
                contenedor.appendChild(toast);
                setTimeout(() => toast.remove(), 4000);
            }

            function inicializarApp() {
                cargarComerciosPublicos();
                let sesion = localStorage.getItem('maxshop_correo_usuario');
                if(sesion) verificarEstadoUsuario(sesion);
            }

            async function cargarComerciosPublicos() {
                try {
                    let res = await fetch('/api/comercios');
                    let json = await res.json();
                    if(json.success) {
                        listaComerciosGlobal = json.data;
                        renderizarComercios(json.data);
                    }
                } catch(e) {}
            }

            function renderizarComercios(comercios) {
                const contenedor = document.getElementById('listaComerciosPublicos');
                if(!contenedor) return;
                if(!comercios || comercios.length === 0) {
                    contenedor.innerHTML = `<div class="text-center text-slate-500 text-xs">No hay comercios adheridos.</div>`;
                    return;
                }
                let html = '';
                comercios.forEach(c => {
                    html += `<div class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center text-xs">
                        <div><b>${c.nombre_fantasias}</b> (${c.rubro})<br><span class="text-[10px] text-cyan-400">${c.porcentaje_descuento || 20}% Off • ${c.dia_promocion || 'Todos los días'}</span></div>
                        <a href="https://wa.me/${c.whatsapp}" target="_blank" class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded">WhatsApp</a>
                    </div>`;
                });
                contenedor.innerHTML = html;
            }

            function filtrarComerciosPublicos() {
                let txt = document.getElementById('inputBuscadorComercios').value.toLowerCase();
                let filtrados = listaComerciosGlobal.filter(c => c.nombre_fantasias.toLowerCase().includes(txt) || c.rubro.toLowerCase().includes(txt) || c.localidad.toLowerCase().includes(txt));
                renderizarComercios(filtrados);
            }

            async function verificarEstadoUsuario(correo) {
                try {
                    let res = await fetch(`/api/usuario/${correo}`);
                    let json = await res.json();
                    if(json.success) {
                        usuarioLogueadoGlobal = json.data;
                        localStorage.setItem('maxshop_correo_usuario', correo);
                        let esPro = usuarioLogueadoGlobal.es_pro || false;
                        document.getElementById('lblEstadoPlan').innerText = esPro ? "⭐ Plan Pro Mensual Activo" : "⚡ Plan Gratuito Activo";
                        document.getElementById('lblCreditoDisponible').innerText = "$" + (usuarioLogueadoGlobal.credito_descuento_disponible || 0).toLocaleString();
                    }
                } catch(e) {}
            }

            function abrirModalAuth(modo) {
                document.getElementById('authModal').classList.remove('hidden');
                if (modo === 'registro' && !modoRegistroAuth) cambiarModoAuth();
                if (modo === 'login' && modoRegistroAuth) cambiarModoAuth();
                
                if (usuarioLogueadoGlobal) {
                    document.getElementById('authForm').classList.add('hidden');
                    document.getElementById('panelSesionContainer').classList.remove('hidden');
                    document.getElementById('nombreSesionLabel').innerText = usuarioLogueadoGlobal.nombre_completo;
                    document.getElementById('sesionTipoPlanLabel').innerText = usuarioLogueadoGlobal.es_pro ? "Plan Pro Mensual" : "Plan Gratuito";
                    document.getElementById('sesionCredito').innerText = "$" + (usuarioLogueadoGlobal.credito_descuento_disponible || 0).toLocaleString();
                } else {
                    document.getElementById('authForm').classList.remove('hidden');
                    document.getElementById('panelSesionContainer').classList.add('hidden');
                }
            }

            function cerrarModalAuth() { document.getElementById('authModal').classList.add('hidden'); }

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
                        mostrarToast("¡Accediste a un plan totalmente gratuito! Y por ser la primera vez te damos $50.000 en crédito para usarlos en toda nuestra red de comercios adheridos.");
                        verificarEstadoUsuario(correo);
                        cerrarModalAuth();
                    } else {
                        mostrarToast("Error en el registro o correo ya existente", "error");
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
                        cerrarModalAuth();
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

            function ejecutarRecargaExpres() {
                if(!usuarioLogueadoGlobal) { mostrarToast("Inicia sesión o regístrate primero", "error"); abrirModalAuth('login'); return; }
                if(confirm("Redirigiendo a plataforma de pago segura para abonar Recarga Exprés ($500)...")) {
                    fetch('/api/recarga-expres', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: usuarioLogueadoGlobal.correo })
                    }).then(r => r.json()).then(res => {
                        if(res.success) { mostrarToast("¡Pago aprobado! +$10.000 acreditados a tu saldo."); verificarEstadoUsuario(usuarioLogueadoGlobal.correo); }
                    });
                }
            }

            function ejecutarSuscripcionPro() {
                if(!usuarioLogueadoGlobal) { mostrarToast("Inicia sesión o regístrate primero", "error"); abrirModalAuth('login'); return; }
                if(confirm("Redirigiendo a plataforma de pago segura para abonar Plan Pro Mensual ($5.000)...")) {
                    fetch('/api/suscripcion-pro', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: usuarioLogueadoGlobal.correo })
                    }).then(r => r.json()).then(res => {
                        if(res.success) { mostrarToast("¡Pago aprobado! Plan Pro Activo con 100% de descuento."); verificarEstadoUsuario(usuarioLogueadoGlobal.correo); }
                    });
                }
            }

            function iniciarEscaneoQR() {
                if(!usuarioLogueadoGlobal) { mostrarToast("Inicia sesión para usar tus descuentos", "error"); abrirModalAuth('login'); return; }
                document.getElementById('modalQR').classList.remove('hidden');
                if (!html5QrCode) html5QrCode = new Html5Qrcode("reader");
                html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: 200 }, (decodedText) => {
                    detenerEscaneoQR();
                    comercioEscaneadoActual = decodedText;
                    document.getElementById('lblComercioEscaneado').innerText = decodedText;
                    let comercioObj = listaComerciosGlobal.find(c => c.nombre_fantasias === decodedText || c.nombre_completo === decodedText);
                    let pctComercio = comercioObj && comercioObj.porcentaje_descuento ? parseFloat(comercioObj.porcentaje_descuento) : 20.0;
                    let esPro = usuarioLogueadoGlobal.es_pro || false;
                    porcentajeDescActual = esPro ? pctComercio : (pctComercio * 0.5);
                    document.getElementById('lblInfoDescuentoComercio').innerText = `Descuento aplicado: ${porcentajeDescActual}% (${esPro ? 'Plan Pro 100%' : 'Plan Gratuito 50%'})`;
                    document.getElementById('modalMontoVenta').classList.remove('hidden');
                }).catch(() => {});
            }

            function detenerEscaneoQR() {
                if (html5QrCode && html5QrCode.isScanning) {
                    html5QrCode.stop().then(() => document.getElementById('modalQR').classList.add('hidden'));
                } else { document.getElementById('modalQR').classList.add('hidden'); }
            }
            function cerrarModalVenta() { document.getElementById('modalMontoVenta').classList.add('hidden'); }

            function calcularDescuentoQR() {
                let monto = parseFloat(document.getElementById('inputMontoCompra').value) || 0;
                let ahorro = monto * (porcentajeDescActual / 100);
                document.getElementById('lblAhorroCalculado').innerText = "$" + ahorro.toLocaleString();
                document.getElementById('lblTotalFinal').innerText = "$" + (monto - ahorro).toLocaleString();
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
                    mostrarToast(`¡Descuento aplicado con éxito! Ahorro: $${json.ahorro_aplicado}`);
                    cerrarModalVenta();
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
                    porcentaje_descuento: parseFloat(document.getElementById('c_porcentaje').value) || 20.0,
                    dia_promocion: document.getElementById('c_dia_promo').value
                };
                let res = await fetch('/api/registrar-comercio', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                if(res.ok) {
                    mostrarToast("¡Comercio registrado con éxito en la red!");
                    document.getElementById('modalComercio').classList.add('hidden');
                    cargarComerciosPublicos();
                } else {
                    mostrarToast("Error al registrar comercio", "error");
                }
            }

            function abrirModalComercio() { document.getElementById('modalComercio').classList.remove('hidden'); }
            function cerrarModalComercio() { document.getElementById('modalComercio').classList.add('hidden'); }
            function abrirModalPlanesDetallados() { document.getElementById('modalPlanesDetallados').classList.remove('hidden'); }
            function cerrarModalPlanesDetallados() { document.getElementById('modalPlanesDetallados').classList.add('hidden'); }

            function abrirAdmin() {
                let c = prompt("Clave Admin:");
                if(c === "AsistMaxAdmin2026Secure") {
                    document.getElementById('modalAdmin').classList.remove('hidden');
                    cargarDatosAdmin();
                } else if(c !== null) { mostrarToast("Clave incorrecta", "error"); }
            }
            function cerrarAdmin() { document.getElementById('modalAdmin').classList.add('hidden'); }

            function cambiarPestanaAdmin(pestana) {
                document.getElementById('seccionComerciosAdmin').classList.add('hidden');
                document.getElementById('seccionUsuariosAdmin').classList.add('hidden');
                document.getElementById('seccionAccionesAdmin').classList.add('hidden');
                document.getElementById('btnTabComercios').className = "font-bold text-slate-400 pb-1 cursor-pointer";
                document.getElementById('btnTabUsuarios').className = "font-bold text-slate-400 pb-1 cursor-pointer";
                document.getElementById('btnTabAcciones').className = "font-bold text-slate-400 pb-1 cursor-pointer";

                if(pestana === 'comercios') {
                    document.getElementById('seccionComerciosAdmin').classList.remove('hidden');
                    document.getElementById('btnTabComercios').className = "font-bold text-cyan-400 border-b-2 border-cyan-400 pb-1 cursor-pointer";
                } else if(pestana === 'usuarios') {
                    document.getElementById('seccionUsuariosAdmin').classList.remove('hidden');
                    document.getElementById('btnTabUsuarios').className = "font-bold text-blue-400 border-b-2 border-blue-400 pb-1 cursor-pointer";
                } else {
                    document.getElementById('seccionAccionesAdmin').classList.remove('hidden');
                    document.getElementById('btnTabAcciones').className = "font-bold text-emerald-400 border-b-2 border-emerald-400 pb-1 cursor-pointer";
                }
            }

            async function cargarDatosAdmin() {
                let res = await fetch('/api/admin/datos');
                let json = await res.json();
                if(json.success) {
                    document.getElementById('tablaComerciosAdminList').innerHTML = json.comercios.map(c => `
                        <div class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center">
                            <div><b>${c.nombre_fantasias}</b> (${c.rubro})<br><span class="text-[10px] text-slate-400">Titular: ${c.nombre_completo} (${c.correo}) | Plan Titular: ${c.es_pro ? 'PRO' : 'FREE'}</span></div>
                        </div>`).join('') || 'Sin comercios';

                    document.getElementById('tablaUsuariosAdminList').innerHTML = json.usuarios.map(u => `
                        <div class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center">
                            <div><b>${u.nombre_completo}</b> (${u.correo})<br><span class="text-[10px] text-cyan-400">Membresía: ${u.es_pro ? 'Plan Pro' : 'Plan Gratuito'} | Saldo: $${u.credito_descuento_disponible}</span></div>
                        </div>`).join('') || 'Sin usuarios';

                    document.getElementById('tablaAccionesAdminList').innerHTML = json.acciones.map(a => `
                        <div class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center">
                            <div><b>Acción:</b> ${a.tipo} <br><span class="text-[10px] text-slate-400">Usuario/Emisor: ${a.correo} | Detalle: ${a.detalle} | Fecha: ${a.fecha}</span></div>
                        </div>`).join('') || 'Sin registros de acciones';
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
        
        # Registrar acción en auditoría
        try:
            supabase.table("acciones_log").insert({"correo": u.correo, "tipo": "REGISTRO_GRATUITO", "detalle": "Nuevo usuario registrado con $50.000 iniciales"}).execute()
        except: pass

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
        data = c.dict()
        data["es_pro"] = False # Identificador de plan titular comercio
        supabase.table("comercios").insert(data).execute()
        
        try:
            supabase.table("acciones_log").insert({"correo": c.correo, "tipo": "REGISTRO_COMERCIO", "detalle": f"Comercio adherido: {c.nombre_fantasias}"}).execute()
        except: pass

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/datos")
def admin_datos():
    if not supabase: return {"success": False, "comercios": [], "usuarios": [], "acciones": []}
    try:
        rc = supabase.table("comercios").select("*").execute()
        ru = supabase.table("usuarios").select("*").execute()
        ra = supabase.table("acciones_log").select("*").order("id", desc=True).limit(50).execute()
        return {"success": True, "comercios": rc.data, "usuarios": ru.data, "acciones": ra.data if ra.data else []}
    except: return {"success": False, "comercios": [], "usuarios": [], "acciones": []}

@app.post("/api/suscripcion-pro")
def suscripcion_pro(payload: dict):
    correo = payload.get("correo")
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        supabase.table("usuarios").update({"es_pro": True}).eq("correo", correo).execute()
        try:
            supabase.table("acciones_log").insert({"correo": correo, "tipo": "PAGO_PLAN_PRO", "detalle": "Suscripción Plan Pro Mensual activada ($5.000)"}).execute()
        except: pass
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
        try:
            supabase.table("acciones_log").insert({"correo": correo, "tipo": "RECARGA_EXPRES", "detalle": "Recarga exprés de $500 realizada (+$10k crédito)"}).execute()
        except: pass
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/consumir-credito")
def consumir_credito(consumo: ConsumoQRModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        c_res = supabase.table("comercios").select("porcentaje_descuento").eq("nombre_fantasias", consumo.nombre_comercio).execute()
        pct_base = 20.0
        if c_res.data: pct_base = float(c_res.data[0].get("porcentaje_descuento", 20.0))

        u_res = supabase.table("usuarios").select("*").eq("correo", consumo.correo_usuario).execute()
        if not u_res.data: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user = u_res.data[0]
        es_pro = user.get("es_pro", False)
        pct_aplicado = pct_base if es_pro else (pct_base * 0.5)

        credito_disponible = float(user.get("credito_descuento_disponible", 0))
        ahorro = consumo.monto_compra * (pct_aplicado / 100.0)

        if not es_pro and credito_disponible < ahorro:
            raise HTTPException(status_code=400, detail="Crédito de descuento insuficiente. Realiza una Recarga Exprés o pásate a Pro.")

        nuevo_credito = credito_disponible - ahorro if not es_pro else credito_disponible
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_credito}).eq("correo", consumo.correo_usuario).execute()

        try:
            supabase.table("acciones_log").insert({"correo": consumo.correo_usuario, "tipo": "CANJE_DESCUENTO", "detalle": f"Canje en {consumo.nombre_comercio} por ${consumo.monto_compra} (Ahorro: ${ahorro})"}).execute()
        except: pass

        return {"success": True, "ahorro_aplicado": ahorro, "credito_restante": nuevo_credito}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
