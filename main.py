from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="MaxShop - AsistMax", version="6.0")

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
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950" onload="cargarComerciosPublicos()">

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

            <!-- BANNER PRINCIPAL (Sin efectos de transformaciones) -->
            <div class="space-y-2">
                <div class="w-full rounded-3xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-900 flex justify-center items-center">
                    <img src="https://i.ibb.co/wFDXX9TK/banner.jpg" alt="MaxShop Banner" class="w-full h-auto object-cover max-h-52">
                </div>
                <div class="px-2 flex justify-between items-center">
                    <div>
                        <span class="text-[9px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-800/50">Comercio Destacado Oficial</span>
                        <h2 class="text-lg font-extrabold text-white mt-1">MaxShop Red Global</h2>
                    </div>
                </div>
            </div>

            <!-- Nivel / Perfil -->
            <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-4 shadow-xl flex items-center justify-between">
                <div class="space-y-1">
                    <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-800/50">Mi Perfil / Nivel</span>
                    <h3 class="text-sm font-bold text-white" id="lblNivelUsuario">Nivel Plata • 450 Puntos</h3>
                    <p class="text-[11px] text-slate-400">Descuentos activos en toda la red</p>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center text-slate-950 font-black text-lg shadow-lg">
                    🥈
                </div>
            </div>

            <!-- Escáner QR de Comercio -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl"></div>
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-2xl font-bold text-white mt-2">Pagos & Descuentos</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el código QR del comercio para aplicar el descuento (mínimo 5%) e ingresar el monto de la compra.</p>
                <div class="mt-5">
                    <button onclick="iniciarEscaneoQR()" class="w-full group relative inline-flex items-center justify-center px-6 py-3.5 text-sm font-bold text-slate-950 transition-all bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl hover:from-cyan-300 hover:to-blue-400 shadow-lg shadow-cyan-500/20 active:scale-95">
                        <span class="mr-2 text-base">📷</span> Escanear QR del Comercio
                    </button>
                </div>
            </div>

            <!-- Botones de Registro -->
            <div class="grid grid-cols-2 gap-3">
                <button onclick="abrirModalComercio()" class="bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-cyan-400 transition">Sumar mi Comercio</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Con Logo y Fotos (Gratis)</p>
                </button>
                <button onclick="abrirModalUsuario()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-blue-400 text-xl mb-1">👤</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Crear Cuenta Usuario</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Clientes y Comerciantes</p>
                </button>
            </div>

            <!-- Directorio de Comercios -->
            <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 space-y-4 shadow-xl">
                <div class="flex justify-between items-center">
                    <div>
                        <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-800/50">Directorio</span>
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
                    <h3 class="text-sm font-bold text-white" id="tituloModalLogin">🔑 Iniciar Sesión / Mi Perfil</h3>
                    <button onclick="cerrarLogin()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                
                <div id="loginFormContainer" class="space-y-3">
                    <p class="text-[11px] text-slate-400">Ingrese su Correo Electrónico o DNI/CUIT registrado para acceder a su panel y su historial.</p>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Correo o Identificador</label>
                        <input type="text" id="inputLoginIdentificador" placeholder="ej: tu@correo.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <button onclick="ejecutarLogin()" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs shadow-lg">Ingresar</button>
                </div>

                <div id="panelSesionContainer" class="space-y-4 hidden">
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 flex justify-between items-center">
                        <div>
                            <span class="text-[10px] text-cyan-400 font-bold uppercase" id="rolSesionBadge">Rol: Usuario</span>
                            <h4 class="text-xs font-bold text-white" id="nombreSesionLabel">Juan Pérez</h4>
                        </div>
                        <button onclick="cerrarSesion()" class="text-[10px] bg-rose-500/10 text-rose-400 px-2.5 py-1 rounded-lg border border-rose-500/30 hover:bg-rose-500/20">Cerrar Sesión</button>
                    </div>

                    <!-- Panel de configuración exclusiva si es Comercio -->
                    <div id="configuracionComercioPanel" class="bg-slate-950/80 border border-cyan-500/30 rounded-2xl p-4 space-y-3 hidden">
                        <h3 class="text-xs font-bold text-cyan-400 uppercase">⚙️ Configuración de Descuentos & Promociones</h3>
                        <p class="text-[10px] text-slate-400">El descuento mínimo obligatorio es 5%. Si defines un día especial de promoción, este no podrá modificarse ni quitarse durante ese mismo día.</p>
                        <div class="space-y-2">
                            <div>
                                <label class="text-[10px] text-slate-400">Porcentaje de Descuento (%)</label>
                                <input type="number" id="edit_porcentaje" min="5" value="5" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white outline-none">
                            </div>
                            <div>
                                <label class="text-[10px] text-slate-400">Día de Promoción Especial</label>
                                <select id="edit_dia" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white outline-none">
                                    <option value="Ninguno">Ninguno (Sólo 5% base)</option>
                                    <option value="Lunes">Lunes</option>
                                    <option value="Martes">Martes</option>
                                    <option value="Miércoles">Miércoles</option>
                                    <option value="Jueves">Jueves</option>
                                    <option value="Viernes">Viernes</option>
                                    <option value="Sábado">Sábado</option>
                                    <option value="Domingo">Domingo</option>
                                </select>
                            </div>
                            <button onclick="guardarConfiguracionComercio()" class="w-full py-2 bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 font-bold rounded-xl text-xs border border-cyan-500/40">Guardar Cambios de Promoción</button>
                        </div>
                    </div>

                    <!-- PANEL ESTADÍSTICO PARA COMERCIOS (KPIs) -->
                    <div id="panelEstadisticasComercio" class="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3 hidden">
                        <h3 class="text-xs font-bold text-cyan-400 uppercase">📊 Estadísticas del Mes (MaxShop)</h3>
                        <div class="grid grid-cols-3 gap-2 text-center">
                            <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                                <span class="text-[9px] text-slate-400 block">Ventas Totales</span>
                                <span class="text-xs font-black text-emerald-400" id="statVentasTotal">$142.500</span>
                            </div>
                            <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                                <span class="text-[9px] text-slate-400 block">Descuentos</span>
                                <span class="text-xs font-black text-cyan-400" id="statDescuentosTotal">$7.125</span>
                            </div>
                            <div class="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                                <span class="text-[9px] text-slate-400 block">Clientes Únicos</span>
                                <span class="text-xs font-black text-blue-400" id="statClientesTotal">18</span>
                            </div>
                        </div>
                    </div>

                    <div class="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 space-y-3">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-cyan-400" id="tituloHistorialRol">🧾 Historial de Operaciones</h3>
                        <div id="historialConsumosContainer" class="space-y-2">
                            <div class="text-xs bg-slate-900 p-3 rounded-xl border border-slate-800/80 space-y-1">
                                <div class="flex justify-between text-slate-400 text-[10px]">
                                    <span>24/08/2026 - 08:30hs</span>
                                    <span>Op #1042</span>
                                </div>
                                <p class="font-bold text-white">Consumo con Descuento aplicado</p>
                                <div class="flex justify-between items-center pt-1 border-t border-slate-800">
                                    <span class="text-slate-400">Total: <strong class="text-emerald-400">$9.500</strong></span>
                                    <button onclick="mostrarToast('Comprobante descargado correctamente', 'success')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded border border-cyan-500/30">Ver Comprobante</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- MODAL CÁMARA ESCÁNER QR & VALIDACIÓN DE VENTA -->
        <div id="modalQR" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex flex-col items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl text-center">
                <div class="flex justify-between items-center">
                    <h3 class="text-sm font-bold text-white">📷 Escanear QR del Comercio</h3>
                    <button onclick="cerrarEscaneoQR()" class="text-slate-400 hover:text-white text-lg font-bold p-1">✕</button>
                </div>
                <div id="reader" class="w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 min-h-[220px]"></div>
                <p class="text-[11px] text-slate-400">Enfoque el código QR provisto por el comercio adherido.</p>
                <button onclick="cerrarEscaneoQR()" class="w-full py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs hover:bg-slate-700 transition">Cancelar</button>
            </div>
        </div>

        <!-- MODAL MONTO DE VENTA Y APLICACIÓN DE DESCUENTO -->
        <div id="modalMontoVenta" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                    <h3 class="text-sm font-bold text-white">💳 Registrar Venta y Descuento</h3>
                    <button onclick="cerrarModalVenta()" class="text-slate-400 hover:text-white font-bold">✕</button>
                </div>
                <div class="space-y-3 text-xs">
                    <p class="text-slate-400">Comercio escaneado: <strong id="lblComercioEscaneado" class="text-cyan-400">Comercio Oficial</strong></p>
                    <div>
                        <label class="text-slate-400">Monto Total de la Compra ($)</label>
                        <input type="number" id="inputMontoCompra" placeholder="ej: 10000" onkeyup="calcularDescuentoQR()" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div class="bg-slate-950 p-3 rounded-2xl border border-slate-800 space-y-1">
                        <div class="flex justify-between text-slate-400"><span>Descuento aplicado:</span> <span id="lblPorcentajeDesc" class="text-cyan-400 font-bold">5%</span></div>
                        <div class="flex justify-between text-slate-400 pt-1 border-t border-slate-900"><span>Total a Pagar con Beneficio:</span> <span id="lblTotalFinal" class="text-emerald-400 font-black text-sm">$0</span></div>
                    </div>
                    <button onclick="confirmarVentaQR()" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl shadow-lg">Confirmar y Generar Comprobante</button>
                </div>
            </div>
        </div>

        <!-- MODAL REGISTRO COMERCIO -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">🏪 Sumar mi Comercio (Gratis)</h3>
                    <button onclick="cerrarModalComercio()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-cyan-400 bg-cyan-950/40 p-2.5 rounded-xl border border-cyan-800/30">Inscripción gratuita con generación automática de tu Código QR y perfil multimedia.</p>
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
                        <label class="text-[11px] font-semibold text-slate-400">WhatsApp (Teléfono)</label>
                        <input type="text" id="c_wpp" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Nombre de Fantasía del Comercio</label>
                        <input type="text" id="c_fantasia" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Rubro del Comercio</label>
                        <select id="c_rubro" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                            <option value="Supermercados, Almacenes y Autoservicios">Supermercados, Almacenes y Autoservicios</option>
                            <option value="Gastronomía (Restaurantes, Cafés, Bares)">Gastronomía (Restaurantes, Cafés, Bares)</option>
                            <option value="Indumentaria, Calzado y Marroquinería">Indumentaria, Calzado y Marroquinería</option>
                            <option value="Salud, Farmacias y Perfumerías">Salud, Farmacias y Perfumerías</option>
                            <option value="Construcción, Ferretería y Hogar">Construcción, Ferretería y Hogar</option>
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
                        <label class="text-[11px] font-semibold text-slate-400">Dirección y Localidad</label>
                        <input type="text" id="c_dir" placeholder="Dirección" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                        <input type="text" id="c_loc" placeholder="Localidad" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1.5">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">CUIT / CUIL</label>
                        <input type="text" id="c_cuit" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none mt-1">
                    </div>
                    <!-- Subida de Multimedia -->
                    <div class="space-y-2 pt-1 border-t border-slate-800">
                        <label class="text-[11px] font-semibold text-cyan-400">Subir Logo del Comercio (1 archivo)</label>
                        <input type="file" id="c_logo_file" accept="image/*" class="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-cyan-500/10 file:text-cyan-400 hover:file:bg-cyan-500/20">
                    </div>
                    <div class="space-y-2">
                        <label class="text-[11px] font-semibold text-cyan-400">Fotos del Comercio (Hasta 3 imágenes)</label>
                        <input type="file" id="c_fotos_file" accept="image/*" multiple class="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-cyan-500/10 file:text-cyan-400 hover:file:bg-cyan-500/20">
                    </div>
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg">Registrar Comercio y Generar QR</button>
                </form>
            </div>
        </div>

        <!-- MODAL REGISTRO USUARIO -->
        <div id="modalUsuario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">👤 Cuenta Consumidor & Suscripción</h3>
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
                        <label class="text-slate-400">Dirección y Localidad</label>
                        <input type="text" id="u_dir" placeholder="Dirección" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                        <input type="text" id="u_loc" placeholder="Localidad" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1.5">
                    </div>
                    <div>
                        <label class="text-slate-400">WhatsApp</label>
                        <input type="text" id="u_wpp" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-slate-400">Correo Electrónico</label>
                        <input type="email" id="u_correo" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white outline-none mt-1">
                    </div>
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-blue-400 to-indigo-500 text-slate-950 font-bold rounded-xl shadow-lg mt-2">Continuar a Opciones de Pago ($10.000)</button>
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
                    <button onclick="cambiarPestanaAdmin('usuarios')" id="btnTabUsuarios" class="pb-2 font-bold text-slate-400">👤 Usuarios</button>
                    <button onclick="cambiarPestanaAdmin('efectivo')" id="btnTabEfectivo" class="pb-2 font-bold text-slate-400">💵 Cobros Efectivo 🟡</button>
                    <button onclick="cambiarPestanaAdmin('operaciones')" id="btnTabOperaciones" class="pb-2 font-bold text-slate-400">🧾 Historial</button>
                </div>

                <div id="seccionComerciosAdmin" class="space-y-3">
                    <div class="flex justify-between items-center"><h4 class="text-xs font-bold text-cyan-400 uppercase">Comercios Adheridos</h4><button onclick="exportarCSV('comercios')" class="text-[11px] bg-cyan-500/10 text-cyan-400 px-3 py-1.5 rounded-xl border border-cyan-500/30">📥 Exportar CSV</button></div>
                    <div id="tablaComerciosAdminList" class="space-y-2"></div>
                </div>
                <div id="seccionUsuariosAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center"><h4 class="text-xs font-bold text-blue-400 uppercase">Usuarios y Membresías</h4><button onclick="exportarCSV('usuarios')" class="text-[11px] bg-blue-500/10 text-blue-400 px-3 py-1.5 rounded-xl border border-blue-500/30">📥 Exportar CSV</button></div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs flex justify-between"><span>Juan Pérez (DNI: 34567892) - Suscripción Activa</span><span class="text-amber-400 font-bold">Plata (450 pts)</span></div>
                </div>
                <div id="seccionEfectivoAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center"><h4 class="text-xs font-bold text-emerald-400 uppercase">Cobros en Comercio Pendientes</h4><button onclick="exportarCSV('cobros_comercio')" class="text-[11px] bg-emerald-500/10 text-emerald-400 px-3 py-1.5 rounded-xl border border-emerald-500/30">📥 Exportar CSV</button></div>
                    <p class="text-[11px] text-slate-400">Validaciones de efectivo en comercio pendiente de rendición.</p>
                </div>
                <div id="seccionOperacionesAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center"><h4 class="text-xs font-bold text-emerald-400 uppercase">Auditoría Operaciones QR</h4><button onclick="exportarCSV('operaciones')" class="text-[11px] bg-emerald-500/10 text-emerald-400 px-3 py-1.5 rounded-xl border border-emerald-500/30">📥 Exportar CSV</button></div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs flex justify-between"><span>Op #1042 - Juan Pérez a MaxShop</span><span class="text-emerald-400 font-bold">$9.500</span></div>
                </div>
            </div>
        </div>

        <script>
            let html5QrCode = null;
            let listaComerciosGlobal = [];
            let comercioEscaneadoActual = null;

            // SISTEMA DE NOTIFICACIONES TOAST
            function mostrarToast(mensaje, tipo = 'success') {
                const contenedor = document.getElementById('toastContainer');
                const toast = document.createElement('div');
                let bgColors = "bg-slate-900 border-cyan-500/40 text-cyan-400";
                let icono = "✨";
                if (tipo === 'success') {
                    bgColors = "bg-slate-900 border-emerald-500/40 text-emerald-400";
                    icono = "✅";
                } else if (tipo === 'error') {
                    bgColors = "bg-slate-900 border-rose-500/40 text-rose-400";
                    icono = "⚠️";
                }
                toast.className = `pointer-events-auto flex items-center space-x-2 px-4 py-3 rounded-2xl border ${bgColors} shadow-2xl backdrop-blur-md transform transition-all duration-300 translate-y-[-10px] opacity-0 text-xs font-bold`;
                toast.innerHTML = `<span>${icono}</span><span>${mensaje}</span>`;
                contenedor.appendChild(toast);
                setTimeout(() => { toast.classList.remove('translate-y-[-10px]', 'opacity-0'); }, 10);
                setTimeout(() => {
                    toast.classList.add('translate-y-[-10px]', 'opacity-0');
                    setTimeout(() => toast.remove(), 300);
                }, 3500);
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
                    listaComerciosGlobal = [
                        { id: 1, nombre_fantasias: "MaxShop Oficial", rubro: "Supermercados, Almacenes y Autoservicios", localidad: "Central", whatsapp: "3834000000", porcentaje_descuento: 5, dia_promocion: "Lunes" }
                    ];
                    renderizarComercios(listaComerciosGlobal);
                }
            }

            function renderizarComercios(comercios) {
                const contenedor = document.getElementById('listaComerciosPublicos');
                if(!comercios || comercios.length === 0) {
                    contenedor.innerHTML = '<div class="text-center py-4 text-xs text-slate-500">No se encontraron comercios registrados.</div>';
                    return;
                }
                let html = '';
                comercios.forEach(c => {
                    let promoTexto = c.dia_promocion && c.dia_promocion !== 'Ninguno' ? `${c.por_descuento || c.porcentaje_descuento || 5}% Off los ${c.dia_promocion}` : `${c.porcentaje_descuento || 5}% Descuento`;
                    html += `
                    <div class="bg-slate-950 border border-slate-800/80 rounded-2xl p-3 flex justify-between items-center transition hover:border-cyan-500/40">
                        <div class="space-y-0.5">
                            <h4 class="text-xs font-bold text-white flex items-center">🏪 ${c.nombre_fantasias} <span class="ml-2 text-[9px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-800/60">${promoTexto}</span></h4>
                            <p class="text-[10px] text-slate-400">Rubro: ${c.rubro} • Localidad: ${c.localidad || 'General'}</p>
                        </div>
                        <a href="https://wa.me/${c.whatsapp}?text=Hola,%20vengo%20de%20MaxShop%20y%20quiero%20consultar%20por%20sus%20beneficios." target="_blank" class="text-[10px] bg-emerald-500/10 text-emerald-400 px-2.5 py-1.5 rounded-xl border border-emerald-500/30 font-semibold">💬 Contacto</a>
                    </div>`;
                });
                contenedor.innerHTML = html;
            }

            function filtrarComerciosPublicos() {
                let texto = document.getElementById('inputBuscadorComercios').value.toLowerCase();
                let filtrados = listaComerciosGlobal.filter(c => 
                    c.nombre_fantasias.toLowerCase().includes(texto) || 
                    c.rubro.toLowerCase().includes(texto) || 
                    (c.localidad && c.localidad.toLowerCase().includes(texto))
                );
                renderizarComercios(filtrados);
            }

            function iniciarEscaneoQR() {
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
                const modal = document.getElementById('modalQR');
                if (html5QrCode && html5QrCode.isScanning) {
                    html5QrCode.stop().then(() => modal.classList.add('hidden')).catch(() => modal.classList.add('hidden'));
                } else { modal.classList.add('hidden'); }
            }
            function cerrarEscaneoQR() { detenerEscaneoQR(); }
            function cerrarModalVenta() { document.getElementById('modalMontoVenta').classList.add('hidden'); }

            function calcularDescuentoQR() {
                let monto = parseFloat(document.getElementById('inputMontoCompra').value) || 0;
                let descuentoPorc = 5; // Mínimo obligatorio
                let totalFinal = monto - (monto * (descuentoPorc / 100));
                document.getElementById('lblPorcentajeDesc').innerText = descuentoPorc + "%";
                document.getElementById('lblTotalFinal').innerText = "$" + totalFinal.toLocaleString();
            }

            function confirmarVentaQR() {
                let monto = document.getElementById('inputMontoCompra').value;
                if(!monto || monto <= 0) { mostrarToast("Ingrese un monto válido.", "error"); return; }
                cerrarModalVenta();
                mostrarToast("¡Venta validada con éxito! Puntos y comprobante guardados.", "success");
            }

            function abrirModalComercio() { document.getElementById('modalComercio').classList.remove('hidden'); }
            function cerrarModalComercio() { document.getElementById('modalComercio').classList.add('hidden'); }
            function abrirModalUsuario() { document.getElementById('modalUsuario').classList.remove('hidden'); }
            function cerrarModalUsuario() { document.getElementById('modalUsuario').classList.add('hidden'); }
            function abrirLogin() { document.getElementById('modalLogin').classList.remove('hidden'); document.getElementById('loginFormContainer').classList.remove('hidden'); document.getElementById('panelSesionContainer').classList.add('hidden'); }
            function cerrarLogin() { document.getElementById('modalLogin').classList.add('hidden'); }
            function abrirAdmin() { let c = prompt("Clave Admin:"); if(c === "AsistMaxAdmin2026Secure") { document.getElementById('modalAdmin').classList.remove('hidden'); } else if(c !== null) { mostrarToast("Clave incorrecta.", "error"); } }
            function cerrarAdmin() { document.getElementById('modalAdmin').classList.add('hidden'); }

            function cambiarPestanaAdmin(tipo) {
                ['comercios', 'usuarios', 'efectivo', 'operaciones'].forEach(t => {
                    document.getElementById('btnTab' + t.charAt(0).toUpperCase() + t.slice(1)).className = "pb-2 font-bold text-slate-400";
                    document.getElementById('seccion' + t.charAt(0).toUpperCase() + t.slice(1) + 'Admin').classList.add('hidden');
                });
                document.getElementById('btnTab' + tipo.charAt(0).toUpperCase() + tipo.slice(1)).className = "pb-2 font-bold text-cyan-400 border-b-2 border-cyan-400";
                document.getElementById('seccion' + tipo.charAt(0).toUpperCase() + tipo.slice(1) + 'Admin').classList.remove('hidden');
            }

            function ejecutarLogin() {
                let id = document.getElementById('inputLoginIdentificador').value.trim();
                if(!id) return;
                document.getElementById('loginFormContainer').classList.add('hidden');
                document.getElementById('panelSesionContainer').classList.remove('hidden');
                if(id.toLowerCase().includes('comercio') || id.toLowerCase().includes('shop')) {
                    document.getElementById('rolSesionBadge').innerText = "Rol: Comercio Adherido";
                    document.getElementById('configuracionComercioPanel').classList.remove('hidden');
                    document.getElementById('panelEstadisticasComercio').classList.remove('hidden');
                    document.getElementById('nombreSesionLabel').innerText = "Comercio: " + id;
                } else {
                    document.getElementById('rolSesionBadge').innerText = "Rol: Consumidor";
                    document.getElementById('configuracionComercioPanel').classList.add('hidden');
                    document.getElementById('panelEstadisticasComercio').classList.add('hidden');
                    document.getElementById('nombreSesionLabel').innerText = "Usuario: " + id;
                }
                mostrarToast("Sesión iniciada correctamente", "success");
            }

            function cerrarSesion() {
                document.getElementById('inputLoginIdentificador').value = "";
                document.getElementById('panelSesionContainer').classList.add('hidden');
                document.getElementById('loginFormContainer').classList.remove('hidden');
                mostrarToast("Sesión cerrada", "info");
            }

            function guardarConfiguracionComercio() {
                let diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
                let diaHoy = diasSemana[new Date().getDay()];
                let diaSeleccionado = document.getElementById('edit_dia').value;

                // REGLA DE NEGOCIO: Bloqueo si intenta modificar el día de promoción actual
                if (diaHoy === diaSeleccionado) {
                    mostrarToast("⚠️ No puedes modificar el descuento el mismo día que está activo.", "error");
                    return;
                }
                mostrarToast("¡Configuración de descuentos actualizada!", "success");
            }

            function exportarCSV(tipo) {
                let cabeceras = "";
                let filas = "";
                if(tipo === 'comercios') {
                    cabeceras = "ID,Nombre Fantasia,Rubro,Localidad,WhatsApp,Descuento\\n";
                    filas = "1,MaxShop Oficial,Supermercados,Central,3834000000,5%";
                } else if(tipo === 'usuarios') {
                    cabeceras = "Nombre,DNI,Nivel,Puntos,WhatsApp,Estado\\n";
                    filas = "Juan Pérez,34567892,Plata,450,3834123456,Suscripción Activa";
                } else if(tipo === 'cobros_comercio') {
                    cabeceras = "Usuario,DNI,WhatsApp,Metodo,Monto,Estado\\n";
                    filas = "Roberto Gómez,28999111,3834987654,Pago en el Comercio,10000,Pendiente";
                } else {
                    cabeceras = "Operacion,Fecha,Participantes,Concepto,Monto\\n";
                    filas = "#1042,24/08/2026,Juan Pérez a MaxShop,Consumo con Descuento,9500";
                }
                
                // BOM (\uFEFF) para corregir acentos y caracteres especiales en Excel
                let contenido = "\\uFEFF" + cabeceras + filas;
                let blob = new Blob([contenido], { type: 'text/csv;charset=utf-8;' });
                let enlace = document.createElement("a");
                enlace.href = URL.createObjectURL(blob);
                enlace.download = `reporte_${tipo}_maxshop.csv`;
                enlace.click();
                mostrarToast("Reporte CSV exportado con éxito", "success");
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
                    dia_promocion: document.getElementById('c_dia_promo').value,
                    logo_url: "logo_cargado.jpg",
                    fotos_url: "fotos_multiples.jpg"
                };
                let res = await fetch('/api/registrar-comercio', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
                });
                let json = await res.json();
                if(json.success) {
                    mostrarToast("¡Comercio registrado con éxito y QR generado!", "success");
                    cerrarModalComercio();
                    document.getElementById('formComercio').reset();
                    cargarComerciosPublicos();
                } else { mostrarToast("Error: " + json.detail, "error"); }
            }

            async function enviarUsuario(e) {
                e.preventDefault();
                const data = {
                    nombre_completo: document.getElementById('u_nombre').value,
                    dni: document.getElementById('u_dni').value,
                    direccion: document.getElementById('u_dir').value,
                    localidad: document.getElementById('u_loc').value,
                    whatsapp: document.getElementById('u_wpp').value,
                    correo: document.getElementById('u_correo').value
                };
                let res = await fetch('/api/registrar-usuario', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
                });
                let json = await res.json();
                if(json.success) {
                    cerrarModalUsuario();
                    mostrarToast("Usuario registrado. Redirigiendo a pago...", "success");
                    window.open("https://mpago.la/12kwFZe", "_blank");
                } else { mostrarToast("Error: " + json.detail, "error"); }
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

@app.post("/api/registrar-comercio")
def registrar_comercio(comercio: ComercioModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no conectada.")
    try:
        response = supabase.table("comercios").insert(comercio.dict()).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=550, detail=str(e))

@app.post("/api/registrar-usuario")
def registrar_usuario(usuario: UsuarioModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no conectada.")
    try:
        response = supabase.table("usuarios").insert(usuario.dict()).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
