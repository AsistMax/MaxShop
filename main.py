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

app = FastAPI(title="MaxShop - Red de Comercios & Ahorro", version="9.3")

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
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
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
                <button type="button" id="btnLogin" class="text-xs bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-3 py-1.5 rounded-xl border border-cyan-500/30 transition font-semibold cursor-pointer">🔑 Login</button>
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
                    <button type="button" id="btnRecargaExpres" class="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 p-2.5 rounded-2xl border border-cyan-500/30 text-center transition cursor-pointer">
                        <span class="block text-xs font-bold">⚡ Recarga Exprés</span>
                        <span class="block text-[10px] text-slate-400">+$10.000 crédito por $500 (MP)</span>
                    </button>
                    <button type="button" id="btnPlanPro" class="bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 p-2.5 rounded-2xl text-center shadow-md font-bold transition hover:opacity-90 cursor-pointer">
                        <span class="block text-xs font-black">⭐ Plan Pro Mensual</span>
                        <span class="block text-[9px] text-slate-950/80">100% Descuento + $50k ($5.000/mes)</span>
                    </button>
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-xl font-bold text-white mt-2">Canjear Descuento en Comercio</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el QR del comercio adherido para aplicar tu descuento instantáneo.</p>
                <div class="mt-4">
                    <button type="button" id="btnEscanearQR" class="w-full py-3.5 text-sm font-bold text-slate-950 transition-all bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl hover:from-cyan-300 hover:to-blue-400 shadow-lg shadow-cyan-500/20 cursor-pointer">📷 Escanear QR del Comercio</button>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <button type="button" id="btnSumarComercio" class="bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl text-left transition-all group cursor-pointer">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-cyan-400 transition">Sumar mi Comercio</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Súmate a la red gratuita</p>
                </button>
                <button type="button" id="btnConocerBeneficios" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group cursor-pointer">
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

                <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400 text-xs">🔍</span>
                    <input type="text" id="inputBuscadorComercios" placeholder="Buscar por nombre, rubro o localidad..." class="w-full bg-slate-950 border border-slate-800 rounded-2xl pl-9 pr-4 py-2.5 text-xs text-white focus:border-cyan-500 outline-none transition">
                </div>

                <div id="listaComerciosPublicos" class="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                    <div class="text-center py-4 text-xs text-slate-500">Cargando comercios adheridos...</div>
                </div>
            </div>

        </main>

        <!-- Modales -->
        <!-- Modal Auth -->
        <div id="authModal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <button type="button" id="btnVolverAuth" class="text-cyan-400 text-xs font-bold flex items-center space-x-1 bg-slate-950 px-2.5 py-1 rounded-xl border border-slate-800 cursor-pointer"><span>⬅️</span><span>Volver</span></button>
                        <h3 class="text-sm font-bold text-white" id="authTitle">🔑 Iniciar Sesión en MaxShop</h3>
                    </div>
                    <button type="button" id="btnCloseAuth" class="text-slate-400 hover:text-white text-lg font-bold cursor-pointer">✕</button>
                </div>

                <div id="panelSesionContainer" class="space-y-4 hidden">
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 flex justify-between items-center">
                        <div>
                            <span class="text-[10px] text-cyan-400 font-bold uppercase" id="sesionTipoPlanLabel">Plan Gratuito</span>
                            <h4 class="text-xs font-bold text-white" id="nombreSesionLabel">Usuario</h4>
                        </div>
                        <button type="button" id="btnCerrarSesion" class="text-[10px] bg-rose-500/10 text-rose-400 px-2.5 py-1 rounded-lg border border-rose-500/30 cursor-pointer">Cerrar Sesión</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-2">
                        <h4 class="text-xs font-bold text-cyan-400 uppercase">📊 Mi Saldo MaxShop</h4>
                        <p class="text-[11px] text-slate-300">Crédito Disponible: <strong id="sesionCredito" class="text-emerald-400">$0</strong></p>
                    </div>
                </div>

                <form id="authForm" class="space-y-3 text-xs">
                    <div id="camposRegistro" class="space-y-3 hidden">
                        <div>
                            <label class="text-slate-400">Nombre Completo</label>
                            <input type="text" id="reg_nombre" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                        </div>
                        <div>
                            <label class="text-slate-400">DNI</label>
                            <input type="text" id="reg_dni" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <input type="text" id="reg_dir" placeholder="Dirección" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                            <input type="text" id="reg_loc" placeholder="Localidad" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none">
                        </div>
                        <div>
                            <label class="text-slate-400">WhatsApp</label>
                            <input type="text" id="reg_wpp" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                        </div>
                    </div>

                    <div>
                        <label class="text-slate-400">Correo Electrónico</label>
                        <input type="email" id="auth_correo" required placeholder="tu@correo.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-slate-400">Contraseña</label>
                        <input type="password" id="auth_password" required placeholder="••••••••" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>

                    <button type="submit" id="btnSubmitAuth" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl shadow-lg mt-2 cursor-pointer">Ingresar</button>
                    
                    <div class="text-center pt-2">
                        <span id="toggleAuthText" class="text-cyan-400 cursor-pointer hover:underline">¿No tienes cuenta? Regístrate aquí</span>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal QR -->
        <div id="modalQR" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex flex-col items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl text-center">
                <div class="flex justify-between items-center">
                    <button type="button" id="btnVolverQR" class="text-cyan-400 text-xs font-bold flex items-center space-x-1 bg-slate-950 px-2 py-1 rounded-xl border border-slate-800 cursor-pointer"><span>⬅️</span><span>Volver</span></button>
                    <h3 class="text-sm font-bold text-white">📷 Escanear QR</h3>
                    <button type="button" id="btnCloseQR" class="text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer">✕</button>
                </div>
                <div id="reader" class="w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 min-h-[220px]"></div>
                <p class="text-[11px] text-slate-400">Enfoque el código QR provisto por el comercio adherido.</p>
                <button type="button" id="btnCancelarQR" class="w-full py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs cursor-pointer">Cancelar</button>
            </div>
        </div>

        <!-- Modal Venta -->
        <div id="modalMontoVenta" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                    <div class="flex items-center space-x-2">
                        <button type="button" id="btnVolverVenta" class="text-cyan-400 text-xs font-bold flex items-center space-x-1 bg-slate-950 px-2.5 py-1 rounded-xl border border-slate-800 cursor-pointer"><span>⬅️</span><span>Volver</span></button>
                        <h3 class="text-sm font-bold text-white">💳 Canjear Descuento</h3>
                    </div>
                    <button type="button" id="btnCloseVenta" class="text-slate-400 hover:text-white font-bold cursor-pointer">✕</button>
                </div>
                <div class="space-y-3 text-xs">
                    <p class="text-slate-400">Comercio: <strong id="lblComercioEscaneado" class="text-cyan-400">Comercio</strong></p>
                    <p class="text-[11px] text-cyan-300 bg-cyan-950/50 p-2 rounded-xl border border-cyan-800/40" id="lblInfoDescuentoComercio">Descuento aplicado según política de la red</p>
                    <div>
                        <label class="text-slate-400">Monto Total de la Compra ($)</label>
                        <input type="number" id="inputMontoCompra" placeholder="ej: 10000" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-1">
                        <div class="flex justify-between text-slate-400"><span>Descuento estimado:</span> <span id="lblAhorroCalculado" class="text-cyan-400 font-bold">$0</span></div>
                        <div class="flex justify-between text-slate-400 pt-1 border-t border-slate-900"><span>Total con Descuento:</span> <span id="lblTotalFinal" class="text-emerald-400 font-black text-sm">$0</span></div>
                    </div>
                    <button type="button" id="btnConfirmarConsumo" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl shadow-lg cursor-pointer">Aplicar y Descontar de mi Crédito</button>
                </div>
            </div>
        </div>

        <!-- Modal Sumar Comercio -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <button type="button" id="btnVolverComercio" class="text-cyan-400 text-xs font-bold flex items-center space-x-1 bg-slate-950 px-2.5 py-1 rounded-xl border border-slate-800 cursor-pointer"><span>⬅️</span><span>Volver</span></button>
                        <h3 class="text-sm font-bold text-white">🏪 Sumar mi Comercio a la Red</h3>
                    </div>
                    <button type="button" id="btnCloseComercio" class="text-slate-400 hover:text-white text-lg font-bold cursor-pointer">✕</button>
                </div>
                <form id="formComercio" class="space-y-3">
                    <div class="bg-cyan-950/40 border border-cyan-800/50 p-2.5 rounded-2xl text-[10px] text-cyan-300">
                        ℹ️ <b>Política obligatoria:</b> Todo comercio ofrece por defecto el <b>5% de descuento todos los días</b>. Puedes configurar adicionalmente una campaña con mayor porcentaje para días específicos.
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Nombre Completo (Titular)</label>
                        <input type="text" id="c_nombre" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Correo Electrónico</label>
                        <input type="email" id="c_correo" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">WhatsApp</label>
                        <input type="text" id="c_wpp" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Nombre de Fantasía del Comercio</label>
                        <input type="text" id="c_fantasia" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Rubro</label>
                        <select id="c_rubro" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
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
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div class="bg-slate-950 border border-slate-800 rounded-2xl p-2.5 space-y-1.5">
                            <label class="text-[10px] font-semibold text-cyan-400 block">Logo del Negocio</label>
                            <input type="file" id="c_logo_file" accept="image/*" class="w-full text-[9px] text-slate-300 file:mr-1 file:py-1 file:px-2 file:rounded-lg file:border-0 file:text-[10px] file:font-semibold file:bg-cyan-500 file:text-slate-950 cursor-pointer">
                            <button type="button" id="btnLimpiarLogo" class="w-full text-[9px] bg-rose-500/10 text-rose-400 py-1 rounded-lg border border-rose-500/20 font-semibold transition cursor-pointer">🗑️ Quitar</button>
                        </div>
                        <div class="bg-slate-950 border border-slate-800 rounded-2xl p-2.5 space-y-1.5">
                            <label class="text-[10px] font-semibold text-cyan-400 block">Foto del Negocio</label>
                            <input type="file" id="c_foto_file" accept="image/*" class="w-full text-[9px] text-slate-300 file:mr-1 file:py-1 file:px-2 file:rounded-lg file:border-0 file:text-[10px] file:font-semibold file:bg-cyan-500 file:text-slate-950 cursor-pointer">
                            <button type="button" id="btnLimpiarFoto" class="w-full text-[9px] bg-rose-500/10 text-rose-400 py-1 rounded-lg border border-rose-500/20 font-semibold transition cursor-pointer">🗑️ Quitar</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="text-[10px] font-semibold text-cyan-400">Campaña Descuento (%)</label>
                            <input type="number" id="c_porcentaje_campana" value="20" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                        </div>
                        <div>
                            <label class="text-[10px] font-semibold text-cyan-400">Días de Campaña</label>
                            <select id="c_dias_campana" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                                <option value="Martes y Jueves">Martes y Jueves</option>
                                <option value="Lunes a Miércoles">Lunes a Miércoles</option>
                                <option value="Viernes y Sábado">Viernes y Sábado</option>
                                <option value="Fines de semana">Fines de semana</option>
                                <option value="Ninguno">Ninguno (Solo base 5%)</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <input type="text" id="c_dir" placeholder="Dirección" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                        <input type="text" id="c_loc" placeholder="Localidad" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1.5">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">CUIT / CUIL</label>
                        <input type="text" id="c_cuit" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <div class="text-[10px] text-slate-400 pt-1">
                        <label class="flex items-center space-x-2 cursor-pointer">
                            <input type="checkbox" id="c_terminos" required class="rounded bg-slate-950 border-slate-800 text-cyan-500">
                            <span>Acepto las condiciones (Obligatorio ofrecer 5% diario y respetar días de campaña inamovibles).</span>
                        </label>
                    </div>
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg cursor-pointer">Sumar mi Comercio</button>
                </form>
            </div>
        </div>

        <!-- Modal Planes y Beneficios -->
        <div id="modalPlanesDetallados" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-3xl p-6 space-y-5 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <button type="button" id="btnVolverPlanes" class="text-cyan-400 text-xs font-bold flex items-center space-x-1 bg-slate-950 px-2.5 py-1 rounded-xl border border-slate-800 cursor-pointer"><span>⬅️</span><span>Volver</span></button>
                        <h3 class="text-sm font-bold text-white">📋 Opciones de Membresía & Ahorro</h3>
                    </div>
                    <button type="button" id="btnClosePlanes" class="text-slate-400 hover:text-white font-bold cursor-pointer">✕</button>
                </div>

                <div class="space-y-4 text-xs text-slate-300">
                    <p class="leading-relaxed">MaxShop te conecta con la red de comercios adheridos para que ahorres en cada compra diaria. Elige la modalidad:</p>

                    <div class="bg-slate-950 border border-emerald-500/30 rounded-2xl p-4 space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-emerald-400 font-black text-sm">⚡ Plan Gratuito (Prepago Base)</span>
                            <span class="bg-emerald-950 text-emerald-300 text-[10px] px-2 py-0.5 rounded-full font-bold">100% Sin Costo</span>
                        </div>
                        <ul class="space-y-1 text-slate-400 text-[11px] list-disc list-inside">
                            <li><strong>Saldo inicial de bienvenida:</strong> $50.000 para comenzar a ahorrar de inmediato.</li>
                            <li><strong>Descuento activo:</strong> Accedes al 50% del beneficio real publicado por cada comercio.</li>
                            <li><strong>Recarga exprés opcional:</strong> Recarga $10.000 extra por sólo $500 vía Mercado Pago.</li>
                        </ul>
                        <button type="button" id="btnRegPlanGratis" class="w-full mt-2 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold rounded-xl text-xs transition cursor-pointer">Registrarme en Plan Gratuito</button>
                    </div>

                    <div class="bg-slate-950 border border-cyan-500/40 rounded-2xl p-4 space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-cyan-400 font-black text-sm">⭐ Plan Pro Mensual ($5.000 / mes)</span>
                            <span class="bg-cyan-950 text-cyan-300 text-[10px] px-2 py-0.5 rounded-full font-bold">Beneficio Pleno</span>
                        </div>
                        <ul class="space-y-1 text-slate-400 text-[11px] list-disc list-inside">
                            <li><strong>Suscripción mensual automática:</strong> Se renueva cada mes para mantener tu línea activa.</li>
                            <li><strong>Descuento pleno (100%):</strong> Disfrutas del total del descuento publicado por el comercio.</li>
                            <li><strong>Saldo mensual extra:</strong> Recibes $50.000 todos los 1 de cada mes.</li>
                        </ul>
                        <button type="button" id="btnPagarPlanProModal" class="w-full mt-2 py-2.5 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs transition shadow-md cursor-pointer">Pagar y Activar Plan Pro ($5.000/mes MP)</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Panel de Administración -->
        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-4xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <button type="button" id="btnVolverAdmin" class="text-cyan-400 text-xs font-bold flex items-center space-x-1 bg-slate-950 px-2.5 py-1 rounded-xl border border-slate-800 cursor-pointer"><span>⬅️</span><span>Volver</span></button>
                        <h3 class="text-base font-bold text-white">⚙️ Panel de Control & Auditoría MaxShop</h3>
                    </div>
                    <button type="button" id="btnCloseAdmin" class="text-slate-400 hover:text-white font-bold cursor-pointer">✕</button>
                </div>
                <div class="flex border-b border-slate-800 space-x-4 pt-2 overflow-x-auto text-xs">
                    <button type="button" id="btnTabComercios" class="pb-2 font-bold text-cyan-400 border-b-2 border-cyan-400 cursor-pointer">🏪 Comercios</button>
                    <button type="button" id="btnTabUsuarios" class="pb-2 font-bold text-slate-400 cursor-pointer">👤 Usuarios & Control Centralizado</button>
                </div>
                
                <div id="seccionComerciosAdmin" class="space-y-3">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-cyan-400 uppercase">Comercios Adheridos (Gestión Exclusiva Admin)</h4>
                        <a href="/api/admin/exportar/comercios" target="_blank" class="text-[10px] bg-cyan-500/25 text-cyan-300 px-3 py-1.5 rounded-xl border border-cyan-500/40 font-bold">📥 Exportar Comercios (CSV)</a>
                    </div>
                    <div id="tablaComerciosAdminList" class="text-xs text-slate-400 max-h-60 overflow-y-auto space-y-2">Cargando...</div>
                </div>

                <div id="seccionUsuariosAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-blue-400 uppercase">Clientes Registrados & Membresías</h4>
                        <a href="/api/admin/exportar/usuarios" target="_blank" class="text-[10px] bg-blue-500/25 text-blue-300 px-3 py-1.5 rounded-xl border border-blue-500/40 font-bold">📥 Exportar Usuarios (CSV)</a>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-slate-300 border-collapse">
                            <thead>
                                <tr class="border-b border-slate-800 text-cyan-400">
                                    <th class="p-2">Cliente / WhatsApp</th>
                                    <th class="p-2">Correo Electrónico</th>
                                    <th class="p-2">Membresía</th>
                                    <th class="p-2">Saldo Ahorro</th>
                                    <th class="p-2 text-right">Acciones Admin</th>
                                </tr>
                            </thead>
                            <tbody id="tablaUsuariosAdminBody">
                                <tr><td colspan="5" class="text-center p-4 text-slate-500">Cargando usuarios...</td></tr>
                            </tbody>
                        </table>
                    </div>
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

            document.addEventListener('DOMContentLoaded', () => {
                // Enlaces de eventos principales seguros con addEventListener
                document.getElementById('btnLogin').addEventListener('click', () => abrirModalAuth('login'));
                document.getElementById('btnAdmin').addEventListener('click', abrirAdmin);
                document.getElementById('btnVerPlanes').addEventListener('click', abrirModalPlanesDetallados);
                document.getElementById('btnConocerBeneficios').addEventListener('click', abrirModalPlanesDetallados);
                document.getElementById('btnRecargaExpres').addEventListener('click', iniciarPagoRecargaExpres);
                document.getElementById('btnPlanPro').addEventListener('click', iniciarPagoPlanPro);
                document.getElementById('btnEscanearQR').addEventListener('click', iniciarEscaneoQR);
                document.getElementById('btnSumarComercio').addEventListener('click', abrirModalComercio);

                // Botones de cierre / navegación en modales
                document.getElementById('btnCloseAuth').addEventListener('click', cerrarModalAuth);
                document.getElementById('btnVolverAuth').addEventListener('click', cerrarModalAuth);
                document.getElementById('btnCloseQR').addEventListener('click', detenerEscaneoQR);
                document.getElementById('btnVolverQR').addEventListener('click', detenerEscaneoQR);
                document.getElementById('btnCancelarQR').addEventListener('click', detenerEscaneoQR);
                document.getElementById('btnCloseVenta').addEventListener('click', cerrarModalVenta);
                document.getElementById('btnVolverVenta').addEventListener('click', cerrarModalVenta);
                document.getElementById('btnCloseComercio').addEventListener('click', cerrarModalComercio);
                document.getElementById('btnVolverComercio').addEventListener('click', cerrarModalComercio);
                document.getElementById('btnClosePlanes').addEventListener('click', cerrarModalPlanesDetallados);
                document.getElementById('btnVolverPlanes').addEventListener('click', cerrarModalPlanesDetallados);
                document.getElementById('btnCloseAdmin').addEventListener('click', cerrarAdmin);
                document.getElementById('btnVolverAdmin').addEventListener('click', cerrarAdmin);

                document.getElementById('btnRegPlanGratis').addEventListener('click', () => { cerrarModalPlanesDetallados(); abrirModalAuth('registro'); });
                document.getElementById('btnPagarPlanProModal').addEventListener('click', () => { cerrarModalPlanesDetallados(); iniciarPagoPlanPro(); });

                document.getElementById('toggleAuthText').addEventListener('click', cambiarModoAuth);
                document.getElementById('authForm').addEventListener('submit', procesarAutenticacion);
                document.getElementById('formComercio').addEventListener('submit', enviarComercio);
                document.getElementById('btnCerrarSesion').addEventListener('click', cerrarSesion);
                document.getElementById('btnConfirmarConsumo').addEventListener('click', confirmarConsumoCredito);

                document.getElementById('btnLimpiarLogo').addEventListener('click', () => limpiarArchivo('c_logo_file'));
                document.getElementById('btnLimpiarFoto').addEventListener('click', () => limpiarArchivo('c_foto_file'));

                document.getElementById('inputMontoCompra').addEventListener('keyup', calcularDescuentoQR);
                document.getElementById('inputBuscadorComercios').addEventListener('keyup', filtrarComerciosPublicos);

                document.getElementById('btnTabComercios').addEventListener('click', () => cambiarPestanaAdmin('comercios'));
                document.getElementById('btnTabUsuarios').addEventListener('click', () => cambiarPestanaAdmin('usuarios'));

                inicializarApp();
            });

            function mostrarToast(mensaje, tipo = 'success') {
                const contenedor = document.getElementById('toastContainer');
                if(!contenedor) return;
                const toast = document.createElement('div');
                let bgColors = "bg-slate-900 border-emerald-500/40 text-emerald-400";
                let icono = "✅";
                if (tipo === 'error') { bgColors = "bg-slate-900 border-rose-500/40 text-rose-400"; icono = "⚠️"; }
                toast.className = `pointer-events-auto flex items-center space-x-2 px-4 py-3 rounded-2xl border ${bgColors} shadow-2xl backdrop-blur-md text-xs font-bold`;
                toast.innerHTML = `<span>${icono}</span><span>${mensaje}</span>`;
                contenedor.appendChild(toast);
                setTimeout(() => toast.remove(), 3500);
            }

            function mostrarLoader(texto) {
                document.getElementById('loaderText').innerText = texto;
                document.getElementById('modalLoader').classList.remove('hidden');
            }

            function ocultarLoader() { document.getElementById('modalLoader').classList.add('hidden'); }
            function limpiarArchivo(idInput) { document.getElementById(idInput).value = ""; mostrarToast("Imagen descartada."); }

            function inicializarApp() {
                cargarComerciosPublicos();
                let sesionGuardada = localStorage.getItem('maxshop_correo_usuario');
                if(sesionGuardada) { verificarEstadoUsuario(sesionGuardada); }
            }

            async function cargarComerciosPublicos() {
                try {
                    let res = await fetch('/api/comercios');
                    let json = await res.json();
                    if(json.success) {
                        listaComerciosGlobal = json.data;
                        renderizarComercios(listaComerciosGlobal);
                    }
                } catch(e) { listaComerciosGlobal = []; renderizarComercios([]); }
            }

            function renderizarComercios(comercios) {
                const contenedor = document.getElementById('listaComerciosPublicos');
                if(!contenedor) return;
                if(!comercios || comercios.length === 0) {
                    contenedor.innerHTML = `<div class="text-center py-6 text-xs text-slate-500">No hay comercios registrados aún.</div>`;
                    return;
                }
                let html = '';
                comercios.forEach(c => {
                    html += `
                    <div class="bg-slate-950 border border-slate-800/80 rounded-2xl p-3 flex justify-between items-center">
                        <div class="flex items-center space-x-2.5">
                            ${c.logo_url ? `<img src="${c.logo_url}" class="w-10 h-10 rounded-xl object-cover border border-slate-800">` : '<div class="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-xs">🏪</div>'}
                            <div class="space-y-0.5">
                                <h4 class="text-xs font-bold text-white">${c.nombre_fantasias} <span class="ml-2 text-[9px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded-full">5% Base + ${c.porcentaje_campana || 20}% (${c.dias_campana || 'Campaña'})</span></h4>
                                <p class="text-[10px] text-slate-400">${c.rubro} • ${c.localidad || 'General'}</p>
                            </div>
                        </div>
                        <a href="https://wa.me/${c.whatsapp}?text=Hola,%20vengo%20de%20MaxShop." target="_blank" class="text-[10px] bg-emerald-500/10 text-emerald-400 px-2.5 py-1.5 rounded-xl border border-emerald-500/30 font-semibold">💬 Contacto</a>
                    </div>`;
                });
                contenedor.innerHTML = html;
            }

            function filtrarComerciosPublicos() {
                let texto = document.getElementById('inputBuscadorComercios').value.toLowerCase();
                let filtrados = listaComerciosGlobal.filter(c => c.nombre_fantasias.toLowerCase().includes(texto) || c.rubro.toLowerCase().includes(texto));
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
                        document.getElementById('lblVencimientoPlan').innerText = esPro ? "100% Descuento Ilimitado" : "Descuento Base 50%";
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
                    titulo.innerText = '🎁 Registro de Usuario Seguro';
                    btnSubmit.innerText = 'Registrarse y Activar';
                    toggleText.innerText = '¿Ya tienes cuenta? Inicia sesión aquí';
                } else {
                    camposReg.classList.add('hidden');
                    titulo.innerText = '🔑 Iniciar Sesión en MaxShop';
                    btnSubmit.innerText = 'Ingresar';
                    toggleText.innerText = '¿No tienes cuenta? Regístrate aquí';
                }
            }

            async function procesarAutenticacion(e) {
                e.preventDefault();
                let correo = document.getElementById('auth_correo').value.trim();
                let password = document.getElementById('auth_password').value;

                if (modoRegistroAuth) {
                    mostrarLoader("Registrando cuenta de usuario...");
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
                    let json = await res.json();
                    ocultarLoader();
                    if(res.ok) {
                        mostrarToast("¡Cuenta creada con éxito y $50.000 de saldo inicial!", "success");
                        verificarEstadoUsuario(correo);
                        cerrarModalAuth();
                    } else {
                        mostrarToast(json.detail || "Error en el registro", "error");
                    }
                } else {
                    mostrarLoader("Validando credenciales...");
                    let res = await fetch('/api/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: correo, password: password })
                    });
                    let json = await res.json();
                    ocultarLoader();
                    if(res.ok) {
                        mostrarToast("¡Sesión iniciada con éxito!", "success");
                        verificarEstadoUsuario(json.usuario.correo);
                        cerrarModalAuth();
                    } else {
                        mostrarToast(json.detail || "Correo o contraseña incorrectos", "error");
                    }
                }
            }

            function cerrarSesion() {
                localStorage.removeItem('maxshop_correo_usuario');
                usuarioLogueadoGlobal = null;
                location.reload();
            }

            function iniciarPagoPlanPro() {
                if(!usuarioLogueadoGlobal) { 
                    mostrarToast("Debe iniciar sesión primero para adquirir el Plan Pro.", "error"); 
                    abrirModalAuth('login'); 
                    return; 
                }
                let ok = confirm("Será redirigido a Mercado Pago para abonar la membresía mensual de $5.000 del Plan Pro. ¿Desea continuar?");
                if(!ok) return;
                mostrarLoader("Conectando con Mercado Pago...");
                setTimeout(async () => {
                    let res = await fetch('/api/suscripcion-pro', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: usuarioLogueadoGlobal.correo })
                    });
                    let json = await res.json();
                    ocultarLoader();
                    if(json.success) {
                        mostrarToast("¡Pago aprobado por Mercado Pago! Plan Pro activado.", "success");
                        verificarEstadoUsuario(usuarioLogueadoGlobal.correo);
                    } else {
                        mostrarToast("Error al procesar el pago", "error");
                    }
                }, 1500);
            }

            function iniciarPagoRecargaExpres() {
                if(!usuarioLogueadoGlobal) { 
                    mostrarToast("Inicia sesión o regístrate primero.", "error"); 
                    abrirModalAuth('login'); 
                    return; 
                }
                let ok = confirm("Será redirigido a Mercado Pago para abonar la Recarga Exprés de $500 y sumar $10.000 de crédito. ¿Desea continuar?");
                if(!ok) return;
                mostrarLoader("Conectando con Mercado Pago...");
                setTimeout(async () => {
                    let res = await fetch('/api/recarga-expres', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ correo: usuarioLogueadoGlobal.correo })
                    });
                    let json = await res.json();
                    ocultarLoader();
                    if(json.success) {
                        mostrarToast("¡Pago aprobado! Se acreditaron $10.000 extra.", "success");
                        verificarEstadoUsuario(usuarioLogueadoGlobal.correo);
                    } else {
                        mostrarToast("Error en recarga", "error");
                    }
                }, 1500);
            }

            function iniciarEscaneoQR() {
                if(!usuarioLogueadoGlobal) { mostrarToast("⚠️ Inicia sesión para usar tus créditos.", "error"); abrirModalAuth('login'); return; }
                const modal = document.getElementById('modalQR');
                modal.classList.remove('hidden');
                if (!html5QrCode) { html5QrCode = new Html5Qrcode("reader"); }
                html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: { width: 220, height: 220 } },
                    (decodedText) => {
                        detenerEscaneoQR();
                        comercioEscaneadoActual = decodedText;
                        document.getElementById('lblComercioEscaneado').innerText = decodedText;
                        let comercioObj = listaComerciosGlobal.find(c => c.nombre_fantasias === decodedText || c.nombre_completo === decodedText);
                        
                        let pctCampana = comercioObj && comercioObj.porcentaje_campana ? parseFloat(comercioObj.porcentaje_campana) : 20.0;
                        let esPro = usuarioLogueadoGlobal.es_pro || false;
                        let pctFinal = esPro ? pctCampana : (pctCampana * 0.5);
                        porcentajeDescActual = pctFinal;
                        
                        document.getElementById('lblInfoDescuentoComercio').innerText = `Descuento aplicado: ${pctFinal}% (${esPro ? 'Plan Pro 100% campaña' : 'Plan Gratuito 50% de campaña'})`;
                        document.getElementById('modalMontoVenta').classList.remove('hidden');
                    }, (err) => {}
                ).catch(() => { modal.classList.add('hidden'); });
            }

            function detenerEscaneoQR() {
                if (html5QrCode && html5QrCode.isScanning) {
                    html5QrCode.stop().then(() => document.getElementById('modalQR').classList.add('hidden'));
                } else { document.getElementById('modalQR').classList.add('hidden'); }
            }

            function cerrarModalVenta() { document.getElementById('modalMontoVenta').classList.add('hidden'); }

            function calcularDescuentoQR() {
                let monto = parseFloat(document.getElementById('inputMontoCompra').value) || 0;
                let pct = porcentajeDescActual || 5.0;
                let ahorro = monto * (pct / 100);
                document.getElementById('lblAhorroCalculado').innerText = "$" + ahorro.toLocaleString();
                document.getElementById('lblTotalFinal').innerText = "$" + (monto - ahorro).toLocaleString();
            }

            async function confirmarConsumoCredito() {
                let monto = parseFloat(document.getElementById('inputMontoCompra').value);
                if(!monto || monto <= 0) { mostrarToast("Ingrese un monto válido", "error"); return; }
                let res = await fetch('/api/consumir-credito', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ correo_usuario: usuarioLogueadoGlobal.correo, nombre_comercio: comercioEscaneadoActual, monto_compra: monto })
                });
                let json = await res.json();
                if(json.success) {
                    mostrarToast(`¡Descuento aplicado! Ahorro: $${json.ahorro_aplicado}`, "success");
                    cerrarModalVenta();
                    verificarEstadoUsuario(usuarioLogueadoGlobal.correo);
                } else {
                    mostrarToast("Error: " + json.detail, "error");
                }
            }

            function abrirModalComercio() { document.getElementById('modalComercio').classList.remove('hidden'); }
            function cerrarModalComercio() { document.getElementById('modalComercio').classList.add('hidden'); }
            function abrirModalPlanesDetallados() { document.getElementById('modalPlanesDetallados').classList.remove('hidden'); }
            function cerrarModalPlanesDetallados() { document.getElementById('modalPlanesDetallados').classList.add('hidden'); }

            function abrirAdmin() {
                let c = prompt("Clave Admin:");
                if(c === "AsistMaxAdmin2026Secure") { document.getElementById('modalAdmin').classList.remove('hidden'); cargarDatosAdmin(); }
                else if(c !== null) { mostrarToast("Clave incorrecta", "error"); }
            }
            function cerrarAdmin() { document.getElementById('modalAdmin').classList.add('hidden'); }

            function cambiarPestanaAdmin(pestana) {
                if(pestana === 'comercios') {
                    document.getElementById('btnTabComercios').className = "pb-2 font-bold text-cyan-400 border-b-2 border-cyan-400 cursor-pointer";
                    document.getElementById('btnTabUsuarios').className = "pb-2 font-bold text-slate-400 cursor-pointer";
                    document.getElementById('seccionComerciosAdmin').classList.remove('hidden');
                    document.getElementById('seccionUsuariosAdmin').classList.add('hidden');
                } else {
                    document.getElementById('btnTabUsuarios').className = "pb-2 font-bold text-blue-400 border-b-2 border-blue-400 cursor-pointer";
                    document.getElementById('btnTabComercios').className = "pb-2 font-bold text-slate-400 cursor-pointer";
                    document.getElementById('seccionUsuariosAdmin').classList.remove('hidden');
                    document.getElementById('seccionComerciosAdmin').classList.add('hidden');
                }
            }

            async function cargarDatosAdmin() {
                try {
                    let res = await fetch('/api/admin/datos');
                    let json = await res.json();
                    if(json.success) {
                        let comerciosHtml = '';
                        json.comercios.forEach(c => {
                            comerciosHtml += `
                                <div class="p-3 bg-slate-950 border border-slate-800 rounded-2xl mb-2 flex justify-between items-center">
                                    <div>
                                        <b>${c.nombre_fantasias}</b> (${c.rubro}) - ${c.localidad}<br>
                                        <span class="text-[10px] text-emerald-400">Descuento Base Diario: 5% (Fijo)</span> | 
                                        <span class="text-[10px] text-cyan-400">Campaña: ${c.porcentaje_campana || 20}% (${c.dias_campana || 'Martes y Jueves'})</span><br>
                                        <span class="text-[9px] text-slate-400">Titular: ${c.nombre_completo} | CUIT: ${c.cuit_cuil}</span>
                                    </div>
                                    <button type="button" onclick="adminModificarCampanaComercio('${c.correo}')" class="px-2.5 py-1.5 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded-xl text-[10px] font-bold hover:bg-amber-500/20 cursor-pointer">⚙️ Modificar Campaña</button>
                                </div>`;
                        });
                        document.getElementById('tablaComerciosAdminList').innerHTML = comerciosHtml || 'Sin comercios';
                        
                        let tablaUsuariosHtml = '';
                        json.usuarios.forEach(u => {
                            let planBadge = u.es_pro ? '<span class="bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded-full text-[10px] font-bold">Plan Pro</span>' : '<span class="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded-full text-[10px] font-bold">Plan Gratuito</span>';
                            tablaUsuariosHtml += `
                                <tr class="border-b border-slate-800/60 hover:bg-slate-950/40">
                                    <td class="p-2"><b>${u.nombre_completo}</b><br><small class="text-slate-400">${u.whatsapp || 'Sin WhatsApp'}</small></td>
                                    <td class="p-2 text-slate-300">${u.correo}</td>
                                    <td class="p-2">${planBadge}</td>
                                    <td class="p-2 font-black text-emerald-400">$${(u.credito_descuento_disponible || 0).toLocaleString()}</td>
                                    <td class="p-2 text-right">
                                        <button type="button" onclick="adminCambiarPlan('${u.correo}', '${u.es_pro ? 'FREE' : 'PRO}')" class="px-2 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-lg text-[10px] font-bold hover:bg-cyan-500/20 cursor-pointer">Cambiar a ${u.es_pro ? 'Free' : 'Pro'}</button>
                                    </td>
                                </tr>`;
                        });
                        document.getElementById('tablaUsuariosAdminBody').innerHTML = tablaUsuariosHtml || '<tr><td colspan="5" class="text-center p-4 text-slate-500">Sin usuarios registrados</td></tr>';
                    }
                } catch(e) {}
            }

            async function adminModificarCampanaComercio(correoComercio) {
                let nuevoPct = prompt("Ingrese el nuevo porcentaje autorizado para la campaña (Ej: 20 para 20%):");
                if(!nuevoPct) return;
                let res = await fetch('/api/admin/comercio/campana', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ correo: correoComercio, porcentaje_campana: parseFloat(nuevoPct) })
                });
                let json = await res.json();
                if(json.success) {
                    mostrarToast("Campaña de comercio actualizada por administración", "success");
                    cargarDatosAdmin();
                    cargarComerciosPublicos();
                } else {
                    mostrarToast("Error al actualizar campaña", "error");
                }
            }

            async function adminCambiarPlan(correo, nuevoPlan) {
                let ok = confirm(`¿Deseas cambiar el plan del usuario ${correo} a ${nuevoPlan}?`);
                if(!ok) return;
                let res = await fetch(`/api/admin/usuario/plan`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ correo: correo, nuevo_plan: nuevoPlan })
                });
                let json = await res.json();
                if(json.success) {
                    mostrarToast("Membresía actualizada con éxito", "success");
                    cargarDatosAdmin();
                } else {
                    mostrarToast("Error al actualizar plan", "error");
                }
            }

            async function enviarComercio(e) {
                e.preventDefault();
                mostrarLoader("Registrando comercio...");
                let logoUrl = "", fotoUrl = "";
                try {
                    const logoFile = document.getElementById('c_logo_file').files[0];
                    if (logoFile) {
                        let fd = new FormData(); fd.append("file", logoFile);
                        let r = await fetch('/api/subir-imagen', { method: 'POST', body: fd });
                        let j = await r.json(); if(j.success) logoUrl = j.url;
                    }
                    const fotoFile = document.getElementById('c_foto_file').files[0];
                    if (fotoFile) {
                        let fd = new FormData(); fd.append("file", fotoFile);
                        let r = await fetch('/api/subir-imagen', { method: 'POST', body: fd });
                        let j = await r.json(); if(j.success) fotoUrl = j.url;
                    }

                    const data = {
                        nombre_completo: document.getElementById('c_nombre').value,
                        correo: document.getElementById('c_correo').value,
                        whatsapp: document.getElementById('c_wpp').value,
                        nombre_fantasias: document.getElementById('c_fantasia').value,
                        rubro: document.getElementById('c_rubro').value,
                        direccion: document.getElementById('c_dir').value,
                        localidad: document.getElementById('c_loc').value,
                        cuit_cuil: document.getElementById('c_cuit').value,
                        descuento_base_diario: 5.0,
                        porcentaje_campana: parseFloat(document.getElementById('c_porcentaje_campana').value) || 20.0,
                        dias_campana: document.getElementById('c_dias_campana').value,
                        logo_url: logoUrl,
                        fotos_url: fotoUrl
                    };

                    let res = await fetch('/api/registrar-comercio', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                    let json = await res.json();
                    ocultarLoader();
                    if(res.ok) {
                        mostrarToast("¡Comercio registrado con éxito!", "success");
                        cerrarModalComercio();
                        cargarComerciosPublicos();
                    } else {
                        mostrarToast("Error al registrar", "error");
                    }
                } catch(err) { ocultarLoader(); mostrarToast("Error de conexión", "error"); }
            }
        </script>
    </body>
    </html>
    """

# ==========================================
# ENDPOINTS BACKEND DE API Y SUPABASE
# ==========================================

@app.post("/api/subir-imagen")
async def subir_imagen(file: UploadFile = File(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin Supabase")
    try:
        file_bytes = await file.read()
        file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}.jpg"
        supabase.storage.from_("comercios-multimedia").upload(file_name, file_bytes, {"content-type": file.content_type or "image/jpeg"})
        return {"success": True, "url": supabase.storage.from_("comercios-multimedia").get_public_url(file_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comercios")
def obtener_comercios():
    if not supabase: return {"success": False, "data": []}
    try:
        res = supabase.table("comercios").select("*").execute()
        return {"success": True, "data": res.data}
    except: return {"success": False, "data": []}

@app.get("/api/usuario/{correo}")
def obtener_usuario(correo: str):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if res.data and len(res.data) > 0:
            return {"success": True, "data": res.data[0]}
        return {"success": False, "detail": "No encontrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/registro")
def registrar_usuario_seguro(u: UsuarioRegistroModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        existe = supabase.table("usuarios").select("correo").eq("correo", u.correo).execute()
        if existe.data and len(existe.data) > 0:
            raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado.")
        
        data = u.dict()
        password_plana = data.pop("password")
        data["password_hash"] = encriptar_password(password_plana)
        data["es_pro"] = False
        data["credito_descuento_disponible"] = 50000
        
        supabase.table("usuarios").insert(data).execute()
        return {"success": True}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
def iniciar_sesion_seguro(cred: UsuarioLoginModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("*").eq("correo", cred.correo).execute()
        if not res.data or len(res.data) == 0:
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
        
        user = res.data[0]
        pwd_hash = encriptar_password(cred.password)
        if user.get("password_hash") != pwd_hash:
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
            
        return {"success": True, "usuario": user}
    except HTTPException as he:
        raise he
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

@app.put("/api/admin/usuario/plan")
def admin_cambiar_plan(payload: dict):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        correo = payload.get("correo")
        nuevo_plan = payload.get("nuevo_plan")
        es_pro = (nuevo_plan == "PRO")
        
        res = supabase.table("usuarios").select("credito_descuento_disponible").eq("correo", correo).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        actual = float(res.data[0].get("credito_descuento_disponible", 0))
        nuevo_saldo = (actual + 50000) if es_pro else actual
        
        supabase.table("usuarios").update({"es_pro": es_pro, "credito_descuento_disponible": nuevo_saldo}).eq("correo", correo).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/admin/comercio/campana")
def admin_modificar_campana(payload: dict):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        correo = payload.get("correo")
        nuevo_pct = float(payload.get("porcentaje_campana", 20.0))
        supabase.table("comercios").update({"porcentaje_campana": nuevo_pct}).eq("correo", correo).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/admin/exportar/comercios", response_class=PlainTextResponse)
def exportar_comercios():
    if not supabase: return "Sin BD"
    try:
        res = supabase.table("comercios").select("*").execute()
        out = io.StringIO(); w = csv.writer(out)
        if res.data: w.writerow(res.data[0].keys()); [w.writerow(r.values()) for r in res.data]
        return out.getvalue()
    except: return "Error"

@app.get("/api/admin/exportar/usuarios", response_class=PlainTextResponse)
def exportar_usuarios():
    if not supabase: return "Sin BD"
    try:
        res = supabase.table("usuarios").select("*").execute()
        out = io.StringIO(); w = csv.writer(out)
        if res.data: w.writerow(res.data[0].keys()); [w.writerow(r.values()) for r in res.data]
        return out.getvalue()
    except: return "Error"

@app.post("/api/registrar-comercio")
def registrar_comercio(c: ComercioModel):
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("comercios").insert(c.dict()).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recarga-expres")
def recarga_expres(payload: dict):
    correo = payload.get("correo")
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("credito_descuento_disponible").eq("correo", correo).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        actual = float(res.data[0].get("credito_descuento_disponible", 0))
        nuevo = actual + 10000
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo}).eq("correo", correo).execute()
        return {"success": True, "nuevo_credito": nuevo}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/suscripcion-pro")
def suscripcion_pro(payload: dict):
    correo = payload.get("correo")
    if not supabase: raise HTTPException(status_code=500, detail="Sin BD")
    try:
        res = supabase.table("usuarios").select("credito_descuento_disponible").eq("correo", correo).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        actual = float(res.data[0].get("credito_descuento_disponible", 0))
        nuevo = actual + 50000
        supabase.table("usuarios").update({"es_pro": True, "credito_descuento_disponible": nuevo}).eq("correo", correo).execute()
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
            raise HTTPException(status_code=400, detail="Crédito de descuento insuficiente. Realiza una Recarga Exprés o pásate a Pro.")

        nuevo_credito = credito_disponible - ahorro
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_credito}).eq("correo", consumo.correo_usuario).execute()

        return {"success": True, "ahorro_aplicado": ahorro, "credito_restante": nuevo_credito}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
