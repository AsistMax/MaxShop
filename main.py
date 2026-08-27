from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
import os
import smtplib
import csv
import io
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client, Client
import mercadopago

app = FastAPI(title="MaxShop - AsistMax", version="7.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

if MP_ACCESS_TOKEN:
    sdk_mp = mercadopago.SDK(MP_ACCESS_TOKEN)
else:
    sdk_mp = None

class ComercioModel(BaseModel):
    nombre_completo: str
    correo: str
    whatsapp: str
    nombre_fantasias: str
    rubro: str
    direccion: str
    localidad: str
    cuit_cuil: str
    porcentaje_descuento: float = 5.0
    dia_promocion: str = "Ninguno"
    logo_url: str = ""
    fotos_url: str = ""

class UsuarioModel(BaseModel):
    nombre_completo: str
    dni: str
    direccion: str
    localidad: str
    whatsapp: str
    correo: str
    plan_monto: int = 10000

class ConsumoQRModel(BaseModel):
    correo_usuario: str
    nombre_comercio: str
    monto_compra: float

class ConfigModel(BaseModel):
    plan_basico_costo: int = 5000
    plan_basico_credito: int = 100000
    plan_estandar_costo: int = 10000
    plan_estandar_credito: int = 250000
    plan_pro_costo: int = 15000
    plan_pro_credito: int = 375000
    plan_vip_costo: int = 20000
    plan_vip_credito: int = 500000
    premio_nuevo_registro: int = 200000

def enviar_correo_transaccional(destinatario: str, asunto: str, cuerpo_html: str):
    remitente = os.getenv("SMTP_CORREO")
    password = os.getenv("SMTP_PASSWORD")
    
    if not remitente or not password:
        return False

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"] = f"MaxShop <{remitente}>"
        mensaje["To"] = destinatario
        
        parte_html = MIMEText(cuerpo_html, "html", "utf-8")
        mensaje.attach(parte_html)
        
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        servidor.quit()
        return True
    except Exception as e:
        return False

@app.get("/", response_class=HTMLResponse)
def mostrar_interfaz():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop & AsistMax - Red Fintech B2B</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950" onload="inicializarApp()">

        <div id="toastContainer" class="fixed top-20 right-4 z-50 flex flex-col space-y-2 pointer-events-none"></div>

        <!-- Botón flotante de WhatsApp / IA -->
        <a href="https://wa.me/5493834000000?text=Hola,%20necesito%20asistencia%20con%20el%20sistema%20MaxShop." target="_blank" class="fixed bottom-6 right-6 z-50 bg-emerald-500 hover:bg-emerald-400 text-slate-950 p-4 rounded-full shadow-2xl flex items-center justify-center transition transform hover:scale-105 border border-emerald-300/50" title="Asistencia IA & Atención al Cliente">
            <span class="text-2xl">💬</span>
        </a>

        <!-- Navbar -->
        <header class="w-full px-4 py-3 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/95 backdrop-blur-md sticky top-0 z-50 shadow-lg">
            <div class="flex items-center space-x-3">
                <img src="https://i.ibb.co/rRGzqgnx/logo.jpg" alt="MaxShop Logo" class="w-11 h-11 rounded-xl object-cover border border-cyan-500/50 shadow-md shadow-cyan-500/20 bg-slate-900">
                <div class="flex flex-col">
                    <span class="text-xs font-black tracking-wider text-white">MAXSHOP <span class="text-cyan-400 font-light">| AsistMax</span></span>
                    <span class="text-[9px] text-cyan-400 font-semibold tracking-widest uppercase">Red B2B & Consumidores</span>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button onclick="abrirLogin()" class="text-xs bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-3 py-1.5 rounded-xl border border-cyan-500/30 transition font-semibold">
                    🔑 Login
                </button>
                <button onclick="abrirAdmin()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-xl border border-slate-700 transition font-medium">
                    ⚙️ Admin
                </button>
            </div>
        </header>

        <!-- Contenido Principal -->
        <main class="w-full max-w-md mx-auto px-4 py-6 space-y-6 flex-1">

            <!-- Banner -->
            <div class="space-y-2">
                <div class="w-full rounded-3xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-900 flex justify-center items-center">
                    <img src="https://i.ibb.co/wFDXX9TK/banner.jpg" alt="MaxShop Banner" class="w-full h-auto object-cover max-h-52">
                </div>
                <div class="px-2 flex justify-between items-center">
                    <div>
                        <span class="text-[9px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-800/50">Red Global de Beneficios</span>
                        <h2 class="text-lg font-extrabold text-white mt-1">Ahorro Inteligente en Comercios</h2>
                    </div>
                </div>
            </div>

            <!-- Estado del Crédito -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-3">
                <div class="flex justify-between items-center">
                    <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-800/50" id="lblEstadoSuscripcionBadge">Modo Explorador (Gratis)</span>
                    <span class="text-[10px] text-slate-400" id="lblVencimientoSuscripcion">Sin membresía activa</span>
                </div>
                <div class="flex justify-between items-center">
                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase">Crédito de Descuento Disponible</h3>
                        <p class="text-2xl font-black text-emerald-400 mt-0.5" id="lblCreditoDisponible">$0</p>
                    </div>
                    <button onclick="abrirModalUsuario()" class="text-xs bg-cyan-500 hover:bg-cyan-400 text-slate-950 px-4 py-2 rounded-xl font-extrabold shadow-lg shadow-cyan-500/20 transition">
                        ⚡ Activar Créditos
                    </button>
                </div>
            </div>

            <!-- Escáner QR -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-xl font-bold text-white mt-2">Canjear Descuento en Comercio</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el QR del comercio adherido para aplicar tu descuento obligatorio del 5% (o día promo).</p>
                <div class="mt-4">
                    <button onclick="iniciarEscaneoQR()" class="w-full py-3.5 text-sm font-bold text-slate-950 transition-all bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl hover:from-cyan-300 hover:to-blue-400 shadow-lg shadow-cyan-500/20">
                        📷 Escanear QR del Comercio
                    </button>
                </div>
            </div>

            <!-- Accesos Rápidos (Corregido sin 'k') -->
            <div class="grid grid-cols-2 gap-3">
                <button onclick="abrirModalComercio()" class="bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-cyan-400 transition">Sumar mi Comercio</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Gratis con QR propio</p>
                </button>
                <button onclick="abrirModalUsuario()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-blue-400 text-xl mb-1">👤</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Planes & Membresías</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Con $200.000 extra de regalo</p>
                </button>
            </div>

            <!-- Directorio -->
            <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 space-y-4 shadow-xl">
                <div class="flex justify-between items-center">
                    <div>
                        <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-800/50">Vidriera Abierta</span>
                        <h3 class="text-sm font-extrabold text-white mt-1">🏪 Comercios Adheridos & Beneficios</h3>
                    </div>
                </div>

                <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400 text-xs">🔍</span>
                    <input type="text" id="inputBuscadorComercios" onkeyup="filtrarComerciosPublicos()" placeholder="Buscar por nombre, rubro o localidad..." class="w-full bg-slate-950 border border-slate-800 rounded-2xl pl-9 pr-4 py-2.5 text-xs text-white focus:border-cyan-500 outline-none transition">
                </div>

                <div id="listaComerciosPublicos" class="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                    <div class="text-center py-4 text-xs text-slate-500">Cargando comercios adheridos...</div>
                </div>
            </div>

        </main>

        <!-- Modal Login -->
        <div id="modalLogin" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white">🔑 Iniciar Sesión en MaxShop</h3>
                    <button onclick="cerrarLogin()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                
                <div id="loginFormContainer" class="space-y-3">
                    <p class="text-[11px] text-slate-400">Ingrese su Correo Electrónico registrado para ver el estado de su crédito y su membresía.</p>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Correo Electrónico</label>
                        <input type="email" id="inputLoginCorreo" placeholder="ej: tu@correo.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <button onclick="ejecutarLogin()" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs shadow-lg">Ingresar</button>
                </div>

                <div id="panelSesionContainer" class="space-y-4 hidden">
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 flex justify-between items-center">
                        <div>
                            <span class="text-[10px] text-cyan-400 font-bold uppercase" id="rolSesionBadge">Rol: Usuario</span>
                            <h4 class="text-xs font-bold text-white" id="nombreSesionLabel">Usuario</h4>
                        </div>
                        <button onclick="cerrarSesion()" class="text-[10px] bg-rose-500/10 text-rose-400 px-2.5 py-1 rounded-lg border border-rose-500/30">Cerrar Sesión</button>
                    </div>

                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-2">
                        <h4 class="text-xs font-bold text-cyan-400 uppercase">📊 Mi Membresía Actual</h4>
                        <p class="text-[11px] text-slate-300">Plan: <strong id="sesionPlan" class="text-white">Estándar</strong></p>
                        <p class="text-[11px] text-slate-300">Crédito de Ahorro: <strong id="sesionCredito" class="text-emerald-400">$0</strong></p>
                        <p class="text-[11px] text-slate-300">Vencimiento: <strong id="sesionVencimiento" class="text-amber-400">-</strong></p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal QR -->
        <div id="modalQR" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex flex-col items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl text-center">
                <div class="flex justify-between items-center">
                    <h3 class="text-sm font-bold text-white">📷 Escanear QR del Comercio</h3>
                    <button onclick="cerrarEscaneoQR()" class="text-slate-400 hover:text-white text-lg font-bold p-1">✕</button>
                </div>
                <div id="reader" class="w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 min-h-[220px]"></div>
                <p class="text-[11px] text-slate-400">Enfoque el código QR provisto por el comercio adherido.</p>
                <button onclick="cerrarEscaneoQR()" class="w-full py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs">Cancelar</button>
            </div>
        </div>

        <!-- Modal Monto Venta -->
        <div id="modalMontoVenta" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                    <h3 class="text-sm font-bold text-white">💳 Canjear Descuento (Créditos)</h3>
                    <button onclick="cerrarModalVenta()" class="text-slate-400 hover:text-white font-bold">✕</button>
                </div>
                <div class="space-y-3 text-xs">
                    <p class="text-slate-400">Comercio: <strong id="lblComercioEscaneado" class="text-cyan-400">Comercio</strong></p>
                    <p class="text-[11px] text-cyan-300 bg-cyan-950/50 p-2 rounded-xl border border-cyan-800/40" id="lblInfoDescuentoComercio">Descuento aplicado: 5% (Base obligatoria permanente)</p>
                    <div>
                        <label class="text-slate-400">Monto Total de la Compra ($)</label>
                        <input type="number" id="inputMontoCompra" placeholder="ej: 10000" onkeyup="calcularDescuentoQR()" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-1">
                        <div class="flex justify-between text-slate-400"><span>Descuento estimado:</span> <span id="lblAhorroCalculado" class="text-cyan-400 font-bold">$0</span></div>
                        <div class="flex justify-between text-slate-400 pt-1 border-t border-slate-900"><span>Total con Descuento:</span> <span id="lblTotalFinal" class="text-emerald-400 font-black text-sm">$0</span></div>
                    </div>
                    <button onclick="confirmarConsumoCredito()" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl shadow-lg">Aplicar y Descontar de mi Crédito</button>
                </div>
            </div>
        </div>

        <!-- Modal Registro Comercio -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">🏪 Sumar mi Comercio (Gratis)</h3>
                    <button onclick="cerrarModalComercio()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-cyan-400 bg-cyan-950/40 p-2.5 rounded-xl border border-cyan-800/30">Inscripción gratuita con QR oficial y descuento base permanente del 5%.</p>
                <form id="formComercio" onsubmit="enviarComercio(event)" class="space-y-3">
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
                        <div>
                            <label class="text-[10px] font-semibold text-cyan-400">Logo o Img. del Negocio (URL)</label>
                            <input type="url" id="c_logo" placeholder="https://..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                        </div>
                        <div>
                            <label class="text-[10px] font-semibold text-cyan-400">Fotos del Negocio (Opcional)</label>
                            <input type="text" id="c_fotos" placeholder="URLs separadas por coma" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="text-[10px] font-semibold text-cyan-400">Descuento Base (%)</label>
                            <input type="number" id="c_porcentaje" value="5" readonly class="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-400 outline-none mt-1 cursor-not-allowed">
                        </div>
                        <div>
                            <label class="text-[10px] font-semibold text-cyan-400">Día de Promoción Especial</label>
                            <select id="c_dia_promo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                                <option value="Ninguno">Ninguno (Rige 5%)</option>
                                <option value="Lunes">Lunes</option>
                                <option value="Martes">Martes</option>
                                <option value="Miércoles">Miércoles</option>
                                <option value="Jueves">Jueves</option>
                                <option value="Viernes">Viernes</option>
                                <option value="Sábado">Sábado</option>
                                <option value="Domingo">Domingo</option>
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
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg">Registrar Comercio Gratis</button>
                </form>
            </div>
        </div>

        <!-- Modal Registro Usuario con Mercado Pago Real (Sin 'k' en valores) -->
        <div id="modalUsuario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">👤 Elegir Plan & Membresía MaxShop</h3>
                    <button onclick="cerrarModalUsuario()" class="text-slate-400 hover:text-white font-bold">✕</button>
                </div>
                <form id="formUsuario" onsubmit="enviarUsuario(event)" class="space-y-3 text-xs">
                    <div>
                        <label class="text-slate-400">Nombre Completo</label>
                        <input type="text" id="u_nombre" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-slate-400">DNI</label>
                        <input type="text" id="u_dni" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div>
                        <input type="text" id="u_dir" placeholder="Dirección" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                        <input type="text" id="u_loc" placeholder="Localidad" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1.5">
                    </div>
                    <div>
                        <label class="text-slate-400">WhatsApp</label>
                        <input type="text" id="u_wpp" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-slate-400">Correo Electrónico</label>
                        <input type="email" id="u_correo" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>

                    <div>
                        <label class="text-cyan-400 font-bold">Seleccionar Plan Mensual (Incluye $200.000 Extra si es Nuevo Registro):</label>
                        <select id="u_plan_monto" class="w-full bg-slate-950 border border-cyan-500/40 rounded-xl px-3 py-2.5 text-white font-bold outline-none mt-1">
                            <option value="5000">Plan Básico ($5.000) ➔ $100.000 Crédito + $200.000 Extra Nuevo</option>
                            <option value="10000" selected>Plan Estándar ($10.000) ➔ $250.000 Crédito + $200.000 Extra Nuevo</option>
                            <option value="15000">Plan Pro ($15.000) ➔ $375.000 Crédito + $200.000 Extra Nuevo</option>
                            <option value="20000">Plan VIP ($20.000) ➔ $500.000 Crédito + $200.000 Extra Nuevo</option>
                        </select>
                    </div>

                    <p class="text-[10px] text-slate-400 italic bg-slate-950 p-2 rounded-xl border border-slate-800">ℹ️ Al confirmar, será redirigido de manera segura a la pasarela de pago oficial de Mercado Pago.</p>

                    <button type="submit" id="btnPagarIntegrado" class="w-full py-3 bg-gradient-to-r from-blue-400 to-indigo-500 text-slate-950 font-bold rounded-xl shadow-lg mt-2 transition hover:opacity-90">💳 Confirmar Pago y Activar Membresía</button>
                </form>
            </div>
        </div>

        <!-- Modal Admin -->
        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-3xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-base font-bold text-white">⚙️ Panel de Control & Auditoría MaxShop</h3>
                    <button onclick="cerrarAdmin()" class="text-slate-400 hover:text-white font-bold">✕</button>
                </div>
                <div class="flex border-b border-slate-800 space-x-4 pt-2 overflow-x-auto text-xs">
                    <button onclick="cambiarPestanaAdmin('comercios')" id="btnTabComercios" class="pb-2 font-bold text-cyan-400 border-b-2 border-cyan-400">🏪 Comercios</button>
                    <button onclick="cambiarPestanaAdmin('usuarios')" id="btnTabUsuarios" class="pb-2 font-bold text-slate-400">👤 Usuarios & Créditos</button>
                    <button onclick="cambiarPestanaAdmin('config')" id="btnTabConfig" class="pb-2 font-bold text-slate-400">⚙️ Costos y Créditos</button>
                </div>

                <div id="seccionComerciosAdmin" class="space-y-3">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-cyan-400 uppercase">Comercios Adheridos Registrados</h4>
                        <a href="/api/admin/exportar/comercios" target="_blank" class="text-[10px] bg-cyan-500/20 text-cyan-300 px-3 py-1.5 rounded-xl border border-cyan-500/40 font-bold">📥 Descargar Base Comercios (CSV)</a>
                    </div>
                    <div id="tablaComerciosAdminList" class="text-xs text-slate-400 max-h-60 overflow-y-auto space-y-2">Cargando...</div>
                </div>

                <div id="seccionUsuariosAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-blue-400 uppercase">Usuarios & Clientes Registrados</h4>
                        <a href="/api/admin/exportar/usuarios" target="_blank" class="text-[10px] bg-blue-500/20 text-blue-300 px-3 py-1.5 rounded-xl border border-blue-500/40 font-bold">📥 Descargar Base Usuarios (CSV)</a>
                    </div>
                    <div id="tablaUsuariosAdminList" class="text-xs text-slate-400 max-h-60 overflow-y-auto space-y-2">Cargando...</div>
                </div>

                <div id="seccionConfigAdmin" class="space-y-3 hidden">
                    <h4 class="text-xs font-bold text-amber-400 uppercase">Configuración de Costos y Créditos de Planes</h4>
                    <form id="formConfigAdmin" onsubmit="guardarConfigAdmin(event)" class="space-y-3 text-xs">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="text-slate-400">Costo Plan Básico ($)</label>
                                <input type="number" id="cfg_basico_costo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                            <div>
                                <label class="text-slate-400">Crédito Plan Básico ($)</label>
                                <input type="number" id="cfg_basico_cred" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="text-slate-400">Costo Plan Estándar ($)</label>
                                <input type="number" id="cfg_estandar_costo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                            <div>
                                <label class="text-slate-400">Crédito Plan Estándar ($)</label>
                                <input type="number" id="cfg_estandar_cred" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="text-slate-400">Costo Plan Pro ($)</label>
                                <input type="number" id="cfg_pro_costo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                            <div>
                                <label class="text-slate-400">Crédito Plan Pro ($)</label>
                                <input type="number" id="cfg_pro_cred" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="text-slate-400">Costo Plan VIP ($)</label>
                                <input type="number" id="cfg_vip_costo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                            <div>
                                <label class="text-slate-400">Crédito Plan VIP ($)</label>
                                <input type="number" id="cfg_vip_cred" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white mt-1">
                            </div>
                        </div>
                        <div>
                            <label class="text-cyan-400 font-bold">Premio Extra Nuevo Registro ($)</label>
                            <input type="number" id="cfg_premio_nuevo" class="w-full bg-slate-950 border border-cyan-500/50 rounded-xl px-3 py-2 text-white mt-1 font-bold">
                        </div>
                        <button type="submit" class="w-full py-2.5 bg-amber-500 text-slate-950 font-bold rounded-xl mt-2">Guardar Nueva Configuración</button>
                    </form>
                </div>
            </div>
        </div>

        <script>
            let html5QrCode = null;
            let listaComerciosGlobal = [];
            let comercioEscaneadoActual = null;
            let usuarioLogueadoGlobal = null;

            function mostrarToast(mensaje, tipo = 'success') {
                const contenedor = document.getElementById('toastContainer');
                const toast = document.createElement('div');
                let bgColors = "bg-slate-900 border-emerald-500/40 text-emerald-400";
                let icono = "✅";
                if (tipo === 'error') { bgColors = "bg-slate-900 border-rose-500/40 text-rose-400"; icono = "⚠️"; }
                toast.className = `pointer-events-auto flex items-center space-x-2 px-4 py-3 rounded-2xl border ${bgColors} shadow-2xl backdrop-blur-md text-xs font-bold`;
                toast.innerHTML = `<span>${icono}</span><span>${mensaje}</span>`;
                contenedor.appendChild(toast);
                setTimeout(() => toast.remove(), 3500);
            }

            function inicializarApp() {
                cargarComerciosPublicos();
                let sesionGuardada = localStorage.getItem('maxshop_correo_usuario');
                if(sesionGuardada) {
                    verificarEstadoUsuario(sesionGuardada);
                }
            }

            async function cargarComerciosPublicos() {
                try {
                    let res = await fetch('/api/comercios');
                    let json = await res.json();
                    if(json.success) {
                        listaComerciosGlobal = json.data;
                        renderizarComercios(listaComerciosGlobal);
                    }
                } catch(e) {
                    listaComerciosGlobal = [];
                    renderizarComercios(listaComerciosGlobal);
                }
            }

            function renderizarComercios(comercios) {
                const contenedor = document.getElementById('listaComerciosPublicos');
                if(!comercios || comercios.length === 0) {
                    contenedor.innerHTML = '<div class="text-center py-4 text-xs text-slate-500">No hay comercios registrados aún.</div>';
                    return;
                }
                let html = '';
                comercios.forEach(c => {
                    html += `
                    <div class="bg-slate-950 border border-slate-800/80 rounded-2xl p-3 flex justify-between items-center">
                        <div class="space-y-0.5">
                            <h4 class="text-xs font-bold text-white">🏪 ${c.nombre_fantasias} <span class="ml-2 text-[9px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded-full">${c.porcentaje_descuento || 5}% Off</span></h4>
                            <p class="text-[10px] text-slate-400">${c.rubro} • ${c.localidad || 'General'}</p>
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
                        
                        if(usuarioLogueadoGlobal.suscripcion_activa) {
                            document.getElementById('lblEstadoSuscripcionBadge').innerText = "Membresía Activa ⚡";
                            document.getElementById('lblCreditoDisponible').innerText = "$" + (usuarioLogueadoGlobal.credito_descuento_disponible || 0).toLocaleString();
                            document.getElementById('lblVencimientoSuscripcion').innerText = "Vence: " + new Date(usuarioLogueadoGlobal.fecha_vencimiento).toLocaleDateString();
                        } else {
                            document.getElementById('lblEstadoSuscripcionBadge').innerText = "Membresía Inactiva (Requiere Pago)";
                            document.getElementById('lblCreditoDisponible').innerText = "$0";
                        }
                    }
                } catch(e) {}
            }

            function iniciarEscaneoQR() {
                if(!usuarioLogueadoGlobal || !usuarioLogueadoGlobal.suscripcion_activa) {
                    mostrarToast("⚠️ Necesitas tener una membresía activa para usar tus créditos de descuento.", "error");
                    abrirModalUsuario();
                    return;
                }
                const modal = document.getElementById('modalQR');
                modal.classList.remove('hidden');
                if (!html5QrCode) { html5QrCode = new Html5Qrcode("reader"); }
                html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: { width: 220, height: 220 } },
                    (decodedText) => {
                        detenerEscaneoQR();
                        comercioEscaneadoActual = decodedText;
                        document.getElementById('lblComercioEscaneado').innerText = decodedText;
                        
                        let comercioObj = listaComerciosGlobal.find(c => c.nombre_fantasias === decodedText || c.nombre_completo === decodedText);
                        let descAplicado = 5.0;
                        if(comercioObj && comercioObj.porcentaje_descuento) {
                            descAplicado = parseFloat(comercioObj.porcentaje_descuento);
                        }
                        window.porcentajeDescActual = descAplicado;
                        document.getElementById('lblInfoDescuentoComercio').innerText = `Descuento aplicado: ${descAplicado}% (Base permanente 5% + Día especial)`;
                        
                        document.getElementById('modalMontoVenta').classList.remove('hidden');
                    }, (err) => {}
                ).catch(() => { modal.classList.add('hidden'); });
            }

            function detenerEscaneoQR() {
                if (html5QrCode && html5QrCode.isScanning) {
                    html5QrCode.stop().then(() => document.getElementById('modalQR').classList.add('hidden'));
                } else { document.getElementById('modalQR').classList.add('hidden'); }
            }
            function cerrarEscaneoQR() { detenerEscaneoQR(); }
            function cerrarModalVenta() { document.getElementById('modalMontoVenta').classList.add('hidden'); }

            function calcularDescuentoQR() {
                let monto = parseFloat(document.getElementById('inputMontoCompra').value) || 0;
                let pct = window.porcentajeDescActual || 5.0;
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
                    body: JSON.stringify({
                        correo_usuario: usuarioLogueadoGlobal.correo,
                        nombre_comercio: comercioEscaneadoActual,
                        monto_compra: monto
                    })
                });
                let json = await res.json();
                if(json.success) {
                    mostrarToast(`¡Descuento aplicado con éxito! Ahorro: $${json.ahorro_aplicado}`, "success");
                    cerrarModalVenta();
                    verificarEstadoUsuario(usuarioLogueadoGlobal.correo);
                } else {
                    mostrarToast("Error: " + json.detail, "error");
                }
            }

            function abrirModalComercio() { document.getElementById('modalComercio').classList.remove('hidden'); }
            function cerrarModalComercio() { document.getElementById('modalComercio').classList.add('hidden'); }
            function abrirModalUsuario() { document.getElementById('modalUsuario').classList.remove('hidden'); }
            function cerrarModalUsuario() { document.getElementById('modalUsuario').classList.add('hidden'); }
            function abrirLogin() { document.getElementById('modalLogin').classList.remove('hidden'); }
            function cerrarLogin() { document.getElementById('modalLogin').classList.add('hidden'); }

            async function ejecutarLogin() {
                let correo = document.getElementById('inputLoginCorreo').value.trim();
                if(!correo) return;
                await verificarEstadoUsuario(correo);
                if(usuarioLogueadoGlobal) {
                    document.getElementById('loginFormContainer').classList.add('hidden');
                    document.getElementById('panelSesionContainer').classList.remove('hidden');
                    document.getElementById('nombreSesionLabel').innerText = usuarioLogueadoGlobal.nombre_completo;
                    document.getElementById('sesionPlan').innerText = usuarioLogueadoGlobal.plan_seleccionado || "Estándar";
                    document.getElementById('sesionCredito').innerText = "$" + (usuarioLogueadoGlobal.credito_descuento_disponible || 0).toLocaleString();
                    document.getElementById('sesionVencimiento').innerText = usuarioLogueadoGlobal.fecha_vencimiento ? new Date(usuarioLogueadoGlobal.fecha_vencimiento).toLocaleDateString() : "Sin activar";
                    mostrarToast("Sesión iniciada", "success");
                } else {
                    mostrarToast("No se encontró usuario con ese correo.", "error");
                }
            }

            function cerrarSesion() {
                localStorage.removeItem('maxshop_correo_usuario');
                usuarioLogueadoGlobal = null;
                document.getElementById('panelSesionContainer').classList.add('hidden');
                document.getElementById('loginFormContainer').classList.remove('hidden');
                location.reload();
            }

            function abrirAdmin() {
                let c = prompt("Clave Admin:");
                if(c === "AsistMaxAdmin2026Secure") { 
                    document.getElementById('modalAdmin').classList.remove('hidden'); 
                    cargarDatosAdmin(); 
                } else if(c !== null) { 
                    mostrarToast("Clave incorrecta", "error"); 
                }
            }
            function cerrarAdmin() { document.getElementById('modalAdmin').classList.add('hidden'); }

            function cambiarPestanaAdmin(pestana) {
                if(pestana === 'comercios') {
                    document.getElementById('btnTabComercios').className = "pb-2 font-bold text-cyan-400 border-b-2 border-cyan-400";
                    document.getElementById('btnTabUsuarios').className = "pb-2 font-bold text-slate-400";
                    document.getElementById('btnTabConfig').className = "pb-2 font-bold text-slate-400";
                    document.getElementById('seccionComerciosAdmin').classList.remove('hidden');
                    document.getElementById('seccionUsuariosAdmin').classList.add('hidden');
                    document.getElementById('seccionConfigAdmin').classList.add('hidden');
                } else if(pestana === 'usuarios') {
                    document.getElementById('btnTabUsuarios').className = "pb-2 font-bold text-blue-400 border-b-2 border-blue-400";
                    document.getElementById('btnTabComercios').className = "pb-2 font-bold text-slate-400";
                    document.getElementById('btnTabConfig').className = "pb-2 font-bold text-slate-400";
                    document.getElementById('seccionUsuariosAdmin').classList.remove('hidden');
                    document.getElementById('seccionComerciosAdmin').classList.add('hidden');
                    document.getElementById('seccionConfigAdmin').classList.add('hidden');
                } else {
                    document.getElementById('btnTabConfig').className = "pb-2 font-bold text-amber-400 border-b-2 border-amber-400";
                    document.getElementById('btnTabComercios').className = "pb-2 font-bold text-slate-400";
                    document.getElementById('btnTabUsuarios').className = "pb-2 font-bold text-slate-400";
                    document.getElementById('seccionConfigAdmin').classList.remove('hidden');
                    document.getElementById('seccionComerciosAdmin').classList.add('hidden');
                    document.getElementById('seccionUsuariosAdmin').classList.add('hidden');
                    cargarConfigAdminForm();
                }
            }

            async function cargarDatosAdmin() {
                try {
                    let res = await fetch('/api/admin/datos');
                    let json = await res.json();
                    if(json.success) {
                        document.getElementById('tablaComerciosAdminList').innerHTML = json.comercios.map(c => `<div class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl mb-1 flex justify-between items-center"><div><b>${c.nombre_fantasias}</b> - ${c.rubro} (${c.localidad})<br><span class="text-[10px] text-slate-400">Titular: ${c.nombre_completo} | CUIT: ${c.cuit_cuil}</span></div></div>`).join('') || 'Sin comercios';
                        document.getElementById('tablaUsuariosAdminList').innerHTML = json.usuarios.map(u => `<div class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl mb-1 flex justify-between items-center"><div><b>${u.nombre_completo}</b> (${u.correo})<br><span class="text-[10px] text-slate-400">DNI: ${u.dni} | Wpp: ${u.whatsapp || '-'} | Plan: ${u.plan_seleccionado || '-'} | Crédito: $${u.credito_descuento_disponible || 0}</span></div></div>`).join('') || 'Sin usuarios';
                    }
                } catch(e) {}
            }

            async function cargarConfigAdminForm() {
                try {
                    let res = await fetch('/api/admin/config');
                    let json = await res.json();
                    if(json.success) {
                        let c = json.data;
                        document.getElementById('cfg_basico_costo').value = c.plan_basico_costo;
                        document.getElementById('cfg_basico_cred').value = c.plan_basico_credito;
                        document.getElementById('cfg_estandar_costo').value = c.plan_estandar_costo;
                        document.getElementById('cfg_estandar_cred').value = c.plan_estandar_credito;
                        document.getElementById('cfg_pro_costo').value = c.plan_pro_costo;
                        document.getElementById('cfg_pro_cred').value = c.plan_pro_credito;
                        document.getElementById('cfg_vip_costo').value = c.plan_vip_costo;
                        document.getElementById('cfg_vip_cred').value = c.plan_vip_credito;
                        document.getElementById('cfg_premio_nuevo').value = c.premio_nuevo_registro;
                    }
                } catch(e) {}
            }

            async function guardarConfigAdmin(e) {
                e.preventDefault();
                let data = {
                    plan_basico_costo: parseInt(document.getElementById('cfg_basico_costo').value),
                    plan_basico_credito: parseInt(document.getElementById('cfg_basico_cred').value),
                    plan_estandar_costo: parseInt(document.getElementById('cfg_estandar_costo').value),
                    plan_estandar_credito: parseInt(document.getElementById('cfg_estandar_cred').value),
                    plan_pro_costo: parseInt(document.getElementById('cfg_pro_costo').value),
                    plan_pro_credito: parseInt(document.getElementById('cfg_pro_cred').value),
                    plan_vip_costo: parseInt(document.getElementById('cfg_vip_costo').value),
                    plan_vip_credito: parseInt(document.getElementById('cfg_vip_cred').value),
                    premio_nuevo_registro: parseInt(document.getElementById('cfg_premio_nuevo').value)
                };
                let res = await fetch('/api/admin/config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                let json = await res.json();
                if(json.success) {
                    mostrarToast("Configuración guardada correctamente", "success");
                } else {
                    mostrarToast("Error al guardar configuración", "error");
                }
            }

            async function enviarComercio(e) {
                e.preventDefault();
                const data = {
                    nombre_completo: document.getElementById('c_nombre').value,
                    correo: document.getElementById('c_correo').value,
                    whatsapp: document.getElementById('c_wpp').value,
                    nombre_fantasias: document.getElementById('c_fantasia').value,
                    rubro: document.getElementById('c_rubro').value,
                    direccion: document.getElementById('c_dir').value,
                    localidad: document.getElementById('c_loc').value,
                    cuit_cuil: document.getElementById('c_cuit').value,
                    porcentaje_descuento: 5.0,
                    dia_promocion: document.getElementById('c_dia_promo').value,
                    logo_url: document.getElementById('c_logo').value || "",
                    fotos_url: document.getElementById('c_fotos').value || ""
                };
                let res = await fetch('/api/registrar-comercio', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                let json = await res.json();
                if(json.success) {
                    mostrarToast("¡Comercio registrado con éxito!", "success");
                    cerrarModalComercio();
                    cargarComerciosPublicos();
                }
            }

            async function enviarUsuario(e) {
                e.preventDefault();
                const btn = document.getElementById('btnPagarIntegrado');
                btn.innerText = "Conectando con Mercado Pago...";
                btn.disabled = true;

                const data = {
                    nombre_completo: document.getElementById('u_nombre').value,
                    dni: document.getElementById('u_dni').value,
                    direccion: document.getElementById('u_dir').value,
                    localidad: document.getElementById('u_loc').value,
                    whatsapp: document.getElementById('u_wpp').value,
                    correo: document.getElementById('u_correo').value,
                    plan_monto: parseInt(document.getElementById('u_plan_monto').value)
                };
                
                try {
                    let res = await fetch('/api/registrar-y-pagar-usuario', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                    let json = await res.json();
                    if(json.success && json.link_pago) {
                        mostrarToast("Redirigiendo a Mercado Pago...", "success");
                        window.location.href = json.link_pago;
                    } else {
                        mostrarToast("Error al procesar pago: " + (json.detail || ''), "error");
                        btn.innerText = "💳 Confirmar Pago y Activar Membresía";
                        btn.disabled = false;
                    }
                } catch(err) {
                    mostrarToast("Error de conexión con el servidor", "error");
                    btn.innerText = "💳 Confirmar Pago y Activar Membresía";
                    btn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/api/comercios")
def obtener_comercios():
    if not supabase:
        return {"success": False, "data": []}
    try:
        response = supabase.table("comercios").select("*").execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "data": []}

@app.get("/api/usuario/{correo}")
def obtener_usuario(correo: str):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if res.data and len(res.data) > 0:
            return {"success": True, "data": res.data[0]}
        return {"success": False, "detail": "Usuario no encontrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/datos")
def admin_datos():
    if not supabase:
        return {"success": False, "comercios": [], "usuarios": []}
    try:
        res_c = supabase.table("comercios").select("*").execute()
        res_u = supabase.table("usuarios").select("*").execute()
        return {"success": True, "comercios": res_c.data, "usuarios": res_u.data}
    except Exception as e:
        return {"success": False, "comercios": [], "usuarios": []}

@app.get("/api/admin/exportar/comercios", response_class=PlainTextResponse)
def exportar_comercios():
    if not supabase:
        return "Sin conexión a BD"
    try:
        res = supabase.table("comercios").select("*").execute()
        output = io.StringIO()
        writer = csv.writer(output)
        if res.data:
            keys = res.data[0].keys()
            writer.writerow(keys)
            for row in res.data:
                writer.writerow(row.values())
        return output.getvalue()
    except Exception as e:
        return f"Error: {e}"

@app.get("/api/admin/exportar/usuarios", response_class=PlainTextResponse)
def exportar_usuarios():
    if not supabase:
        return "Sin conexión a BD"
    try:
        res = supabase.table("usuarios").select("*").execute()
        output = io.StringIO()
        writer = csv.writer(output)
        if res.data:
            keys = res.data[0].keys()
            writer.writerow(keys)
            for row in res.data:
                writer.writerow(row.values())
        return output.getvalue()
    except Exception as e:
        return f"Error: {e}"

@app.get("/api/admin/config")
def obtener_config():
    if not supabase:
        return {"success": True, "data": {
            "plan_basico_costo": 5000, "plan_basico_credito": 100000,
            "plan_estandar_costo": 10000, "plan_estandar_credito": 250000,
            "plan_pro_costo": 15000, "plan_pro_credito": 375000,
            "plan_vip_costo": 20000, "plan_vip_credito": 500000,
            "premio_nuevo_registro": 200000
        }}
    try:
        res = supabase.table("configuracion").select("*").eq("id", 1).execute()
        if res.data:
            return {"success": True, "data": res.data[0]}
        else:
            default_cfg = {
                "id": 1,
                "plan_basico_costo": 5000, "plan_basico_credito": 100000,
                "plan_estandar_costo": 10000, "plan_estandar_credito": 250000,
                "plan_pro_costo": 15000, "plan_pro_credito": 375000,
                "plan_vip_costo": 20000, "plan_vip_credito": 500000,
                "premio_nuevo_registro": 200000
            }
            supabase.table("configuracion").upsert(default_cfg).execute()
            return {"success": True, "data": default_cfg}
    except Exception as e:
        return {"success": False, "detail": str(e)}

@app.post("/api/admin/config")
def guardar_config(cfg: ConfigModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        data = cfg.dict()
        data["id"] = 1
        supabase.table("configuracion").upsert(data).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/registrar-comercio")
def registrar_comercio(comercio: ComercioModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        comercio.porcentaje_descuento = 5.0
        res = supabase.table("comercios").insert(comercio.dict()).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/registrar-y-pagar-usuario")
def registrar_y_pagar_usuario(usuario: UsuarioModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    if not sdk_mp:
        raise HTTPException(status_code=500, detail="Falta configurar el MP_ACCESS_TOKEN en las variables de entorno de Render.")

    try:
        cfg_res = supabase.table("configuracion").select("*").eq("id", 1).execute()
        cfg = cfg_res.data[0] if cfg_res.data else {
            "plan_basico_costo": 5000, "plan_basico_credito": 100000,
            "plan_estandar_costo": 10000, "plan_estandar_credito": 250000,
            "plan_pro_costo": 15000, "plan_pro_credito": 375000,
            "plan_vip_costo": 20000, "plan_vip_credito": 500000,
            "premio_nuevo_registro": 200000
        }

        plan_monto = usuario.plan_monto
        credito_otorgado = cfg["plan_estandar_credito"]
        plan_nombre = "Estándar"

        if plan_monto == cfg["plan_basico_costo"]:
            credito_otorgado = cfg["plan_basico_credito"]
            plan_nombre = "Básico"
        elif plan_monto == cfg["plan_pro_costo"]:
            credito_otorgado = cfg["plan_pro_credito"]
            plan_nombre = "Pro"
        elif plan_monto >= cfg["plan_vip_costo"]:
            credito_otorgado = cfg["plan_vip_credito"]
            plan_nombre = "VIP"

        existente = supabase.table("usuarios").select("*").eq("correo", usuario.correo).execute()
        if not (existente.data and len(existente.data) > 0):
            credito_otorgado += cfg["premio_nuevo_registro"]

        ahora = datetime.now()
        vencimiento = ahora + timedelta(days=30)

        datos = usuario.dict()
        datos["suscripcion_activa"] = True
        datos["plan_seleccionado"] = plan_nombre
        datos["credito_descuento_disponible"] = credito_otorgado
        datos["credito_descuento_total"] = credito_otorgado
        datos["fecha_inicio_suscripcion"] = ahora.isoformat()
        datos["fecha_vencimiento"] = vencimiento.isoformat()

        supabase.table("usuarios").upsert(datos, on_conflict="correo").execute()

        # Generar preferencia real en Mercado Pago
        preference_data = {
            "items": [
                {
                    "title": f"Membresía MaxShop - Plan {plan_nombre}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": float(plan_monto)
                }
            ],
            "payer": {
                "name": usuario.nombre_completo,
                "email": usuario.correo
            },
            "back_urls": {
                "success": "https://asistmax.onrender.com/",
                "failure": "https://asistmax.onrender.com/",
                "pending": "https://asistmax.onrender.com/"
            },
            "auto_return": "approved"
        }

        preference_response = sdk_mp.preference().create(preference_data)
        init_point = preference_response["response"]["init_point"]

        return {"success": True, "link_pago": init_point}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consumir-credito")
def consumir_credito(consumo: ConsumoQRModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        comercio_res = supabase.table("comercios").select("*").eq("nombre_fantasias", consumo.nombre_comercio).execute()
        pct_descuento = 5.0 
        if comercio_res.data and len(comercio_res.data) > 0:
            pct_descuento = float(comercio_res.data[0].get("porcentaje_descuento", 5.0))

        res = supabase.table("usuarios").select("*").eq("correo", consumo.correo_usuario).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        usuario = res.data[0]
        if not usuario.get("suscripcion_activa"):
            raise HTTPException(status_code=400, detail="Membresía inactiva.")
        
        credito_disponible = float(usuario.get("credito_descuento_disponible", 0))
        ahorro = consumo.monto_compra * (pct_descuento / 100.0)
        
        if credito_disponible < ahorro:
            raise HTTPException(status_code=400, detail="Crédito de descuento insuficiente en su plan.")
        
        nuevo_credito = credito_disponible - ahorro
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_credito}).eq("correo", consumo.correo_usuario).execute()
        
        return {"success": True, "ahorro_aplicado": ahorro, "credito_restante": nuevo_credito}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
