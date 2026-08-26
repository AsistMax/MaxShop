from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client, Client

app = FastAPI(title="MaxShop - AsistMax", version="7.2")

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

def enviar_correo_transaccional(destinatario: str, asunto: str, cuerpo_html: str):
    remitente = os.getenv("SMTP_CORREO")
    password = os.getenv("SMTP_PASSWORD")
    
    if not remitente or not password:
        print("SMTP no configurado. Omitiendo envío.")
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
        print(f"Error al enviar correo: {e}")
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

        <!-- CONTENEDOR DE NOTIFICACIONES TOAST -->
        <div id="toastContainer" class="fixed top-20 right-4 z-50 flex flex-col space-y-2 pointer-events-none"></div>

        <!-- Navbar Superior -->
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

            <!-- BANNER PRINCIPAL -->
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

            <!-- Panel de Estado / Crédito de Descuento del Usuario -->
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

            <!-- Escáner QR de Comercio -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-xl font-bold text-white mt-2">Canjear Descuento en Comercio</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el QR del comercio adherido para aplicar tu descuento y descontarlo de tu línea de crédito.</p>
                <div class="mt-4">
                    <button onclick="iniciarEscaneoQR()" class="w-full py-3.5 text-sm font-bold text-slate-950 transition-all bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl hover:from-cyan-300 hover:to-blue-400 shadow-lg shadow-cyan-500/20">
                        📷 Escanear QR del Comercio
                    </button>
                </div>
            </div>

            <!-- Botones de Registro (Freemium) -->
            <div class="grid grid-cols-2 gap-3">
                <button onclick="abrirModalComercio()" class="bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-cyan-400 transition">Sumar mi Comercio</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Gratis con QR propio</p>
                </button>
                <button onclick="abrirModalUsuario()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-blue-400 text-xl mb-1">👤</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Planes & Membresías</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Hasta $500k de ahorro</p>
                </button>
            </div>

            <!-- Directorio de Comercios -->
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

        <!-- MODAL LOGIN / PERFIL -->
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

        <!-- MODAL CÁMARA ESCÁNER QR -->
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

        <!-- MODAL MONTO DE VENTA Y APLICACIÓN DE CRÉDITO -->
        <div id="modalMontoVenta" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                    <h3 class="text-sm font-bold text-white">💳 Canjear Descuento (Créditos)</h3>
                    <button onclick="cerrarModalVenta()" class="text-slate-400 hover:text-white font-bold">✕</button>
                </div>
                <div class="space-y-3 text-xs">
                    <p class="text-slate-400">Comercio: <strong id="lblComercioEscaneado" class="text-cyan-400">Comercio</strong></p>
                    <div>
                        <label class="text-slate-400">Monto Total de la Compra ($)</label>
                        <input type="number" id="inputMontoCompra" placeholder="ej: 10000" onkeyup="calcularDescuentoQR()" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-1">
                        <div class="flex justify-between text-slate-400"><span>Descuento estimado (5%):</span> <span id="lblAhorroCalculado" class="text-cyan-400 font-bold">$0</span></div>
                        <div class="flex justify-between text-slate-400 pt-1 border-t border-slate-900"><span>Total con Descuento:</span> <span id="lblTotalFinal" class="text-emerald-400 font-black text-sm">$0</span></div>
                    </div>
                    <button onclick="confirmarConsumoCredito()" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl shadow-lg">Aplicar y Descontar de mi Crédito</button>
                </div>
            </div>
        </div>

        <!-- MODAL REGISTRO COMERCIO (CON TODOS LOS RUBROS) -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">🏪 Sumar mi Comercio (Gratis)</h3>
                    <button onclick="cerrarModalComercio()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-cyan-400 bg-cyan-950/40 p-2.5 rounded-xl border border-cyan-800/30">Inscripción gratuita con generación automática de tu Código QR oficial.</p>
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
                            <label class="text-[10px] font-semibold text-cyan-400">Porcentaje Descuento (%)</label>
                            <input type="number" id="c_porcentaje" min="5" value="5" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                        </div>
                        <div>
                            <label class="text-[10px] font-semibold text-cyan-400">Día de Promoción</label>
                            <select id="c_dia_promo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                                <option value="Ninguno">Ninguno</option>
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

        <!-- MODAL REGISTRO USUARIO Y SELECCIÓN DE PLANES -->
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
                        <input type="text" id="u_dir" placeholder="Dirección" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
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
                        <label class="text-cyan-400 font-bold">Seleccionar Plan Mensual & Crédito de Ahorro:</label>
                        <select id="u_plan_monto" class="w-full bg-slate-950 border border-cyan-500/40 rounded-xl px-3 py-2.5 text-white font-bold outline-none mt-1">
                            <option value="5000">Plan Básico ($5.000/mes) ➔ $100.000 Crédito Ahorro</option>
                            <option value="10000" selected>Plan Estándar ($10.000/mes) ➔ $250.000 Crédito Ahorro</option>
                            <option value="15000">Plan Pro ($15.000/mes) ➔ $375.000 Crédito Ahorro</option>
                            <option value="20000">Plan VIP ($20.000/mes) ➔ $500.000 Crédito Ahorro + $200k Extra (Nuevo Registro)</option>
                        </select>
                    </div>

                    <button type="submit" id="btnPagarMP" class="w-full py-3 bg-gradient-to-r from-blue-400 to-indigo-500 text-slate-950 font-bold rounded-xl shadow-lg mt-2 transition hover:opacity-90">Pagar con Mercado Pago</button>
                </form>
            </div>
        </div>

        <!-- MODAL ADMINISTRADOR -->
        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-3xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-base font-bold text-white">⚙️ Panel de Control & Auditoría MaxShop</h3>
                    <button onclick="cerrarAdmin()" class="text-slate-400 hover:text-white font-bold">✕</button>
                </div>
                <div class="flex border-b border-slate-800 space-x-4 pt-2 overflow-x-auto text-xs">
                    <button onclick="cambiarPestanaAdmin('comercios')" id="btnTabComercios" class="pb-2 font-bold text-cyan-400 border-b-2 border-cyan-400">🏪 Comercios</button>
                    <button onclick="cambiarPestanaAdmin('usuarios')" id="btnTabUsuarios" class="pb-2 font-bold text-slate-400">👤 Usuarios & Créditos</button>
                </div>

                <div id="seccionComerciosAdmin" class="space-y-3">
                    <h4 class="text-xs font-bold text-cyan-400 uppercase">Comercios Adheridos</h4>
                    <div id="tablaComerciosAdminList" class="text-xs text-slate-400">Cargando...</div>
                </div>
                <div id="seccionUsuariosAdmin" class="space-y-3 hidden">
                    <h4 class="text-xs font-bold text-blue-400 uppercase">Usuarios con Créditos Activos</h4>
                    <div id="tablaUsuariosAdminList" class="text-xs text-slate-400">Cargando...</div>
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
                let ahorro = monto * 0.05;
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
                    document.getElementById('seccionComerciosAdmin').classList.remove('hidden');
                    document.getElementById('seccionUsuariosAdmin').classList.add('hidden');
                } else {
                    document.getElementById('btnTabUsuarios').className = "pb-2 font-bold text-blue-400 border-b-2 border-blue-400";
                    document.getElementById('btnTabComercios').className = "pb-2 font-bold text-slate-400";
                    document.getElementById('seccionUsuariosAdmin').classList.remove('hidden');
                    document.getElementById('seccionComerciosAdmin').classList.add('hidden');
                }
            }

            async function cargarDatosAdmin() {
                try {
                    let res = await fetch('/api/admin/datos');
                    let json = await res.json();
                    if(json.success) {
                        document.getElementById('tablaComerciosAdminList').innerHTML = json.comercios.map(c => `<div class="p-2 bg-slate-950 border border-slate-800 rounded mb-1"><b>${c.nombre_fantasias}</b> - ${c.rubro} (${c.localidad})</div>`).join('') || 'Sin comercios';
                        document.getElementById('tablaUsuariosAdminList').innerHTML = json.usuarios.map(u => `<div class="p-2 bg-slate-950 border border-slate-800 rounded mb-1"><b>${u.nombre_completo}</b> (${u.correo}) - Crédito: $${u.credito_descuento_disponible || 0}</div>`).join('') || 'Sin usuarios';
                    }
                } catch(e) {
                    document.getElementById('tablaComerciosAdminList').innerHTML = "Error al cargar datos";
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
                    porcentaje_descuento: parseFloat(document.getElementById('c_porcentaje').value) || 5.0,
                    dia_promocion: document.getElementById('c_dia_promo').value
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
                const btn = document.getElementById('btnPagarMP');
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
                    let res = await fetch('/api/registrar-usuario', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                    let json = await res.json();
                    if(json.success) {
                        cerrarModalUsuario();
                        mostrarToast("Redirigiendo a pasarela segura...", "success");
                        setTimeout(() => {
                            window.location.href = json.init_point || "https://mpago.la/12kwFZe";
                        }, 800);
                    } else {
                        mostrarToast("Error al procesar registro", "error");
                        btn.innerText = "Pagar con Mercado Pago";
                        btn.disabled = false;
                    }
                } catch(err) {
                    mostrarToast("Error de conexión con el servidor", "error");
                    btn.innerText = "Pagar con Mercado Pago";
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

@app.post("/api/registrar-comercio")
def registrar_comercio(comercio: ComercioModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        res = supabase.table("comercios").insert(comercio.dict()).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/registrar-usuario")
def registrar_usuario(usuario: UsuarioModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        # Verificar si el usuario ya existe previamente en la base de datos
        existente = supabase.table("usuarios").select("*").eq("correo", usuario.correo).execute()
        es_primer_registro = not (existente.data and len(existente.data) > 0)

        datos = usuario.dict()
        datos["suscripcion_activa"] = False
        # Guardamos un marcador indicando si es primer registro o usuario que reingresa
        datos["es_nuevo_registro"] = es_primer_registro

        res = supabase.table("usuarios").upsert(datos, on_conflict="correo").execute()
        return {"success": True, "init_point": "https://mpago.la/12kwFZe"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consumir-credito")
def consumir_credito(consumo: ConsumoQRModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        res = supabase.table("usuarios").select("*").eq("correo", consumo.correo_usuario).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        usuario = res.data[0]
        if not usuario.get("suscripcion_activa"):
            raise HTTPException(status_code=400, detail="Membresía inactiva.")
        
        credito_disponible = float(usuario.get("credito_descuento_disponible", 0))
        ahorro = consumo.monto_compra * 0.05
        
        if credito_disponible < ahorro:
            raise HTTPException(status_code=400, detail="Crédito de descuento insuficiente en su plan.")
        
        nuevo_credito = credito_disponible - ahorro
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_credito}).eq("correo", consumo.correo_usuario).execute()
        
        return {"success": True, "ahorro_aplicado": ahorro, "credito_restante": nuevo_credito}
    except Exception as e:
        raise HTTPException(status_0=400, detail=str(e))

@app.post("/api/webhook/mercadopago")
async def webhook_mercadopago(request: Request):
    try:
        data = await request.json()
        print("Webhook MP recibido:", data)
        
        tipo_evento = data.get("type") or data.get("topic")
        if tipo_evento == "payment":
            if supabase:
                res = supabase.table("usuarios").select("*").eq("suscripcion_activa", False).order("dni", desc=True).limit(1).execute()
                if res.data:
                    u = res.data[0]
                    plan_monto = float(u.get("plan_monto", 10000))
                    es_nuevo = u.get("es_nuevo_registro", True)
                    
                    # Cálculo base de créditos según el plan seleccionado
                    credito_otorgado = 250000
                    if plan_monto == 5000: credito_otorgado = 100000
                    elif plan_monto == 15000: credito_otorgado = 375000
                    elif plan_monto >= 20000: 
                        credito_otorgado = 500000
                        # Si es VIP Y es un usuario totalmente NUEVO, le sumamos los $200k extra de bienvenida
                        if es_nuevo:
                            credito_otorgado += 200000
                    
                    ahora = datetime.now()
                    vencimiento = ahora + timedelta(days=30)
                    
                    supabase.table("usuarios").update({
                        "suscripcion_activa": True,
                        "credito_descuento_disponible": credito_otorgado,
                        "credito_descuento_total": credito_otorgado,
                        "fecha_inicio_suscripcion": ahora.isoformat(),
                        "fecha_vencimiento": vencimiento.isoformat(),
                        "es_nuevo_registro": False # Ya queda marcado como usuario histórico
                    }).eq("correo", u["correo"]).execute()
                    
                    asunto = "¡Tu membresía MaxShop ha sido activada con éxito!"
                    html = f"""
                    <div style="font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; border-radius: 15px;">
                        <h2 style="color: #22d3ee;">¡Hola, {u['nombre_completo']}!</h2>
                        <p>Tu pago ha sido procesado de forma automática por <b>Mercado Pago</b>.</p>
                        <p>Tu membresía está activa por 30 días y se te han acreditado <b>${credito_otorgado:,.0f}</b> en tu línea de consumo para canjear en los comercios adheridos.</p>
                        <hr style="border-color: #334155;">
                        <p style="font-size: 11px; color: #94a3b8;">AsistMax - Red Fintech Global</p>
                    </div>
                    """
                    enviar_correo_transaccional(u["correo"], asunto, html)

        return {"status": "ok"}
    except Exception as e:
        print(f"Error en webhook MP: {e}")
        return {"status": "error", "detail": str(e)}
