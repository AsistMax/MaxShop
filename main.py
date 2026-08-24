from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="MaxShop - AsistMax", version="4.6")

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
        <!-- Librería para lectura real de códigos QR -->
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950" onload="cargarComerciosPublicos()">

        <!-- Navbar Superior con Logo Nítido y Separado -->
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

            <!-- BANNER PRINCIPAL 100% NÍDITO (IMAGEN LIMPIA + TEXTO SEPARADO DEBAJO) -->
            <div class="space-y-2">
                <div class="w-full rounded-3xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-900">
                    <img src="https://i.ibb.co/wFDXX9TK/banner.jpg" alt="MaxShop Banner" class="w-full h-44 object-cover filter contrast-105 brightness-105">
                </div>
                <div class="px-2 flex justify-between items-center">
                    <div>
                        <span class="text-[9px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-800/50">Comercio Destacado Oficial</span>
                        <h2 class="text-lg font-extrabold text-white mt-1">MaxShop Red Global</h2>
                    </div>
                </div>
            </div>

            <!-- Tarjeta de Progreso / Nivel -->
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

            <!-- Escáner QR Banner -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl"></div>
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-2xl font-bold text-white mt-2">Pagos & Descuentos</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el código QR de MaxShop o comercios adheridos para validar tu beneficio (5% min) y sumar puntos.</p>
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
                    <p class="text-[11px] text-slate-400 mt-0.5">100% Gratuito (Ventas)</p>
                </button>
                <button onclick="abrirModalUsuario()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-blue-400 text-xl mb-1">👤</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Crear Cuenta Usuario</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Clientes y Comerciantes</p>
                </button>
            </div>

            <!-- BUSCADOR Y COMERCIOS ADHERIDOS -->
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

        <!-- MODAL LOGIN / INICIO DE SESIÓN -->
        <div id="modalLogin" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white" id="tituloModalLogin">🔑 Iniciar Sesión / Mi Perfil</h3>
                    <button onclick="cerrarLogin()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                
                <div id="loginFormContainer" class="space-y-3">
                    <p class="text-[11px] text-slate-400">Ingrese su Correo Electrónico o DNI/CUIT registrado para acceder a su panel y su historial correspondiente.</p>
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

                    <div class="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 space-y-3">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-cyan-400" id="tituloHistorialRol">🧾 Mi Historial de Operaciones</h3>

                        <div id="historialConsumosContainer" class="space-y-2">
                            <div class="text-xs bg-slate-900 p-3 rounded-xl border border-slate-800/80 space-y-1">
                                <div class="flex justify-between text-slate-400 text-[10px]">
                                    <span>Fecha: 24/08/2026 - 08:30hs</span>
                                    <span>Op #1042</span>
                                </div>
                                <p class="font-bold text-white">Consumo en MaxShop (5% desc. aplicado)</p>
                                <div class="flex justify-between items-center pt-1 border-t border-slate-800">
                                    <span class="text-slate-400">Total pagado: <strong class="text-emerald-400">$9.500</strong></span>
                                    <button onclick="verComprobanteDetalle('1042', 'MaxShop', 'Consumo con Descuento', '$9.500')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20">Ver Comprobante</button>
                                </div>
                            </div>
                        </div>

                        <div id="historialVentasContainer" class="space-y-2 hidden">
                            <div class="text-xs bg-slate-900 p-3 rounded-xl border border-slate-800/80 space-y-1">
                                <div class="flex justify-between text-slate-400 text-[10px]">
                                    <span>Fecha: 23/08/2026 - 19:15hs</span>
                                    <span>Op #1039</span>
                                </div>
                                <p class="font-bold text-white">Venta realizada a Cliente: Juan Pérez</p>
                                <div class="flex justify-between items-center pt-1 border-t border-slate-800">
                                    <span class="text-slate-400">Acreditado: <strong class="text-emerald-400">$12.200</strong></span>
                                    <button onclick="verComprobanteDetalle('1039', 'MaxShop', 'Venta a Consumidor', '$12.200')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20">Ver Comprobante</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- MODAL CÁMARA ESCÁNER QR -->
        <div id="modalQR" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex flex-col items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl text-center">
                <div class="flex justify-between items-center">
                    <h3 class="text-sm font-bold text-white">📷 Escáner de Código QR</h3>
                    <button onclick="cerrarEscaneoQR()" class="text-slate-400 hover:text-white text-lg font-bold p-1">✕</button>
                </div>
                <div id="reader" class="w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 min-h-[250px]"></div>
                <p class="text-[11px] text-slate-400">Enfoque el código QR del comercio para validar su compra y obtener su beneficio.</p>
                <button onclick="cerrarEscaneoQR()" class="w-full py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs hover:bg-slate-700 transition">Cancelar / Cerrar</button>
            </div>
        </div>

        <!-- MODAL REGISTRO COMERCIO (SIN REFERENCIAS PREESTABLECIDAS) -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">🏪 Sumar mi Comercio (Gratis)</h3>
                    <button onclick="cerrarModalComercio()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-cyan-400 bg-cyan-950/40 p-2.5 rounded-xl border border-cyan-800/30">Inscripción sin costo. <br><strong class="text-white mt-1 block">💡 Recordatorio: Como comerciante de MaxShop, si deseas comprar en otros comercios con descuento, regístrate también como Usuario.</strong></p>
                <form id="formComercio" onsubmit="enviarComercio(event)" class="space-y-3">
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Nombre Completo (Titular)</label>
                        <input type="text" id="c_nombre" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Correo Electrónico</label>
                        <input type="email" id="c_correo" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">WhatsApp (Teléfono)</label>
                        <input type="text" id="c_wpp" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Nombre de Fantasía del Comercio</label>
                        <input type="text" id="c_fantasia" placeholder="ej: Mi Negocio" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Rubro del Comercio</label>
                        <select id="c_rubro" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                            <option value="Supermercados, Almacenes y Autoservicios">Supermercados, Almacenes y Autoservicios</option>
                            <option value="Gastronomía (Restaurantes, Cafés, Bares)">Gastronomía (Restaurantes, Cafés, Bares)</option>
                            <option value="Indumentaria, Calzado y Marroquinería">Indumentaria, Calzado y Marroquinería</option>
                            <option value="Salud, Farmacias y Perfumerías">Salud, Farmacias y Perfumerías</option>
                            <option value="Construcción, Ferretería y Hogar">Construcción, Ferretería y Hogar</option>
                            <option value="Tecnología, Computación y Celulares">Tecnología, Computación y Celulares</option>
                            <option value="Automotor, Repuestos y Lubricentros">Automotor, Repuestos y Lubricentros</option>
                            <option value="Servicios Profesionales y Oficios">Servicios Profesionales y Oficios</option>
                            <option value="Entretenimiento, Turismo y Hotelería">Entretenimiento, Turismo y Hotelería</option>
                            <option value="Otros Comercios y Servicios">Otros Comercios y Servicios</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Dirección</label>
                        <input type="text" id="c_dir" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Localidad</label>
                        <input type="text" id="c_loc" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">CUIT o CUIL</label>
                        <input type="text" id="c_cuit" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg">Registrar Comercio y Obtener QR</button>
                </form>
            </div>
        </div>

        <!-- MODAL REGISTRO USUARIO -->
        <div id="modalUsuario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">👤 Cuenta Consumidor & Suscripción</h3>
                    <button onclick="cerrarModalUsuario()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-blue-400 bg-blue-950/40 p-2.5 rounded-xl border border-blue-800/30">Membresía mensual de $10.000. Complete sus datos para registrarse y elija su método de pago.</p>
                <form id="formUsuario" onsubmit="enviarUsuario(event)" class="space-y-3">
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Nombre Completo</label>
                        <input type="text" id="u_nombre" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-blue-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">DNI</label>
                        <input type="text" id="u_dni" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-blue-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Dirección</label>
                        <input type="text" id="u_dir" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-blue-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Localidad</label>
                        <input type="text" id="u_loc" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-blue-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">WhatsApp (Teléfono)</label>
                        <input type="text" id="u_wpp" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-blue-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Correo Electrónico</label>
                        <input type="email" id="u_correo" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-blue-500 outline-none mt-1">
                    </div>
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-blue-400 to-indigo-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg">Continuar a Opciones de Pago</button>
                </form>
            </div>
        </div>

        <!-- MODAL SELECTOR DE PAGO (CON OPCIÓN "PAGO EN EL COMERCIO (EFECTIVO)") -->
        <div id="modalOpcionesPago" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white">💳 Seleccione Método de Pago ($10.000)</h3>
                    <button onclick="cerrarOpcionesPago()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-slate-400">Elija cómo abonar su membresía mensual de forma segura:</p>
                <div class="space-y-3">
                    <div onclick="seleccionarMetodoPago('suscripcion')" class="bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-blue-500/50 p-3.5 rounded-2xl cursor-pointer transition space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold text-blue-400">🔄 Suscripción Automática Mensual</span>
                            <span class="text-[10px] bg-blue-950 text-blue-300 px-2 py-0.5 rounded border border-blue-800">Con Tarjeta</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Débito automático sin afectar el margen ni límite de crédito.</p>
                    </div>

                    <div onclick="seleccionarMetodoPago('unico')" class="bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-cyan-500/50 p-3.5 rounded-2xl cursor-pointer transition space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold text-cyan-400">🔗 Link de Pago Único</span>
                            <span class="text-[10px] bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-800">Digital</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Medios habilitados de pago electrónico independiente.</p>
                    </div>

                    <div onclick="seleccionarMetodoPago('comercio')" class="bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-emerald-500/50 p-3.5 rounded-2xl cursor-pointer transition space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold text-emerald-400">💵 Pago en el Comercio (Efectivo)</span>
                            <span class="text-[10px] bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">Presencial</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Abona en efectivo en cualquier comercio adherido de la red. El comercio realizará la rendición a AsistMax.</p>
                    </div>
                </div>
                <button onclick="cerrarOpcionesPago()" class="w-full py-2.5 bg-slate-800 text-slate-300 text-xs font-semibold rounded-xl hover:bg-slate-700 transition">Cancelar</button>
            </div>
        </div>

        <!-- MODAL COMPROBANTE DETALLE -->
        <div id="modalComprobante" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-6 space-y-4 shadow-2xl text-center">
                <div class="w-12 h-12 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 rounded-2xl flex items-center justify-center mx-auto text-xl font-black">✓</div>
                <h3 class="text-sm font-bold text-white">Comprobante de Operación</h3>
                <div class="bg-slate-950 p-4 rounded-2xl border border-slate-800 text-left space-y-2 text-xs">
                    <div class="flex justify-between"><span class="text-slate-400">Operación:</span> <span class="text-white font-mono" id="compOp">#1042</span></div>
                    <div class="flex justify-between"><span class="text-slate-400">Fecha/Hora:</span> <span class="text-white">24/08/2026 08:30hs</span></div>
                    <div class="flex justify-between"><span class="text-slate-400">Entidad / Comercio:</span> <span class="text-white" id="compEntidad">MaxShop</span></div>
                    <div class="flex justify-between"><span class="text-slate-400">Concepto:</span> <span class="text-white" id="compConcepto">Consumo con Descuento</span></div>
                    <div class="flex justify-between pt-2 border-t border-slate-900"><span class="text-slate-400 font-bold">Monto Total:</span> <span class="text-emerald-400 font-black text-sm" id="compMonto">$9.500</span></div>
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <button onclick="alert('Descargando comprobante PDF...')" class="py-2.5 bg-cyan-500/10 text-cyan-400 font-bold rounded-xl text-xs border border-cyan-500/30 hover:bg-cyan-500/20">📥 Descargar</button>
                    <button onclick="cerrarComprobante()" class="py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs hover:bg-slate-700">Cerrar</button>
                </div>
            </div>
        </div>

        <!-- MODAL PANEL DE ADMINISTRADOR (CON GESTIÓN DE PAGOS EN COMERCIO PENDIENTES) -->
        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <span class="text-xl">⚙️</span>
                        <h3 class="text-base font-bold text-white">Panel de Control & Auditoría MaxShop</h3>
                    </div>
                    <button onclick="cerrarAdmin()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>

                <div class="flex border-b border-slate-800 space-x-4 pt-2 overflow-x-auto">
                    <button onclick="cambiarPestanaAdmin('comercios')" id="btnTabComercios" class="pb-2 text-xs font-bold text-cyan-400 border-b-2 border-cyan-400 transition whitespace-nowrap">🏪 Comercios</button>
                    <button onclick="cambiarPestanaAdmin('usuarios')" id="btnTabUsuarios" class="pb-2 text-xs font-bold text-slate-400 hover:text-white transition whitespace-nowrap">👤 Usuarios</button>
                    <button onclick="cambiarPestanaAdmin('efectivo')" id="btnTabEfectivo" class="pb-2 text-xs font-bold text-slate-400 hover:text-white transition whitespace-nowrap">💵 Cobros en Comercio 🟡</button>
                    <button onclick="cambiarPestanaAdmin('operaciones')" id="btnTabOperaciones" class="pb-2 text-xs font-bold text-slate-400 hover:text-white transition whitespace-nowrap">🧾 Historial</button>
                </div>

                <div id="seccionComerciosAdmin" class="space-y-3">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-cyan-400 uppercase">📊 Listado de Comercios</h4>
                        <button onclick="exportarCSV('comercios')" class="text-[11px] bg-cyan-500/10 text-cyan-400 px-2.5 py-1 rounded-lg border border-cyan-500/30">📥 CSV</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs text-white flex justify-between items-center">
                        <div><p class="font-bold">MaxShop Oficial</p><p class="text-[10px] text-slate-400">ID: #1 • Rubro: Supermercados</p></div>
                        <span class="text-emerald-400">140 transacciones ($450.000)</span>
                    </div>
                </div>

                <div id="seccionUsuariosAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-blue-400 uppercase">📊 Listado de Usuarios y Membresías</h4>
                        <button onclick="exportarCSV('usuarios')" class="text-[11px] bg-blue-500/10 text-blue-400 px-2.5 py-1 rounded-lg border border-blue-500/30">📥 CSV</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs text-white flex justify-between items-center">
                        <div><p class="font-bold">Juan Pérez</p><p class="text-[10px] text-slate-400">DNI: 34... • Plata (450 pts)</p></div>
                        <span class="text-amber-400">Suscripción Activa</span>
                    </div>
                </div>

                <!-- SECCIÓN ESPECIAL PARA COBROS EN EFECTIVO EN COMERCIO PENDIENTES DE RENDICIÓN -->
                <div id="seccionEfectivoAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-emerald-400 uppercase">💵 Solicitudes de Alta - Pago en Comercio Pendientes</h4>
                        <button onclick="exportarCSV('cobros_comercio')" class="text-[11px] bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-lg border border-emerald-500/30">📥 CSV Pendientes</button>
                    </div>
                    <p class="text-[11px] text-slate-400">Aquí se registran los usuarios que eligieron abonar en efectivo en un comercio. Una vez que el comercio reciba el dinero y lo rinda a AsistMax, podrás marcarlo como cobrado para habilitar definitivamente su alta y generar el comprobante.</p>
                    
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs text-white space-y-2">
                        <div class="flex justify-between items-center">
                            <div>
                                <p class="font-bold text-amber-400">Usuario: Roberto Gómez (DNI: 28...) Wpp: 3834...</p>
                                <p class="text-[10px] text-slate-400">Método: Pago en el Comercio (Efectivo) • Monto: $10.000</p>
                            </div>
                            <span class="text-[10px] bg-amber-950 text-amber-300 px-2 py-1 rounded border border-amber-800">Pendiente Rendición</span>
                        </div>
                        <div class="flex justify-end space-x-2 pt-2 border-t border-slate-900">
                            <button onclick="alert('Comprobante de Alta generado y registrado para rendición.')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2.5 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20">📄 Generar Comprobante</button>
                            <button onclick="alert('¡Pago rendido y registrado con éxito! El usuario ya cuenta con estado activo.')" class="text-[10px] bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded border border-emerald-500/30 hover:bg-emerald-500/20">✅ Marcar Cobrado / Rendido</button>
                        </div>
                    </div>
                </div>

                <div id="seccionOperacionesAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-emerald-400 uppercase">🧾 Auditoría Centralizada de Comprobantes</h4>
                        <button onclick="exportarCSV('operaciones')" class="text-[11px] bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-lg border border-emerald-500/30">📥 CSV</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs text-white flex justify-between items-center">
                        <div><p class="font-bold">Juan Pérez ➔ MaxShop</p><p class="text-[10px] text-slate-400">24/08/2026 - Op #1042</p></div>
                        <span class="text-emerald-400 font-bold">$9.500</span>
                    </div>
                </div>

            </div>
        </div>

        <!-- MODAL DE POLÍTICAS Y CONDICIONES -->
        <div id="modalPoliticas" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[85vh] overflow-y-auto shadow-2xl text-xs">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white">📜 Políticas de Privacidad y Términos</h3>
                    <button onclick="cerrarPoliticas()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <div class="space-y-3 text-slate-300">
                    <p><strong>1. Privacidad de los Datos:</strong> MaxShop & AsistMax protege los datos personales de consumidores y comercios bajo rigurosos estándares de seguridad y confidencialidad.</p>
                    <p><strong>2. Membresías y Pagos:</strong> Las suscripciones y pagos se procesan de manera segura sin comprometer los límites de crédito personales ni requerir validaciones biométricas externas ajenas al servicio.</p>
                    <p><strong>3. Beneficios y Descuentos:</strong> Los comercios adheridos garantizan un descuento mínimo del 5% al escanear el código QR oficial de la red.</p>
                </div>
                <button onclick="cerrarPoliticas()" class="w-full py-2.5 bg-slate-800 text-slate-200 font-bold rounded-xl mt-2">Entendido</button>
            </div>
        </div>

        <!-- Footer Completo -->
        <footer class="w-full text-center py-6 border-t border-slate-900 text-xs text-slate-500 bg-slate-950 space-y-2">
            <p class="font-semibold text-slate-400">MaxShop & AsistMax &copy; 2026 - Todos los derechos reservados.</p>
            <div class="flex justify-center space-x-4 text-[11px]">
                <button onclick="abrirPoliticas()" class="text-cyan-400 hover:underline">Términos y Condiciones</button>
                <span class="text-slate-700">•</span>
                <button onclick="abrirPoliticas()" class="text-cyan-400 hover:underline">Políticas de Privacidad</button>
            </div>
        </footer>

        <!-- Scripts -->
        <script>
            let html5QrCode = null;
            let listaComerciosGlobal = [];

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
                        { nombre_fantasias: "MaxShop Oficial", rubro: "Supermercados, Almacenes y Autoservicios", localidad: "Central", whatsapp: "3834000000" }
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
                    html += `
                    <div class="bg-slate-950 border border-slate-800/80 rounded-2xl p-3 flex justify-between items-center transition hover:border-cyan-500/40">
                        <div class="space-y-0.5">
                            <h4 class="text-xs font-bold text-white flex items-center">🏪 ${c.nombre_fantasias} <span class="ml-2 text-[9px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-800/60">5% Descuento</span></h4>
                            <p class="text-[10px] text-slate-400">Rubro: ${c.rubro} • Localidad: ${c.localidad || 'General'}</p>
                        </div>
                        <a href="https://wa.me/${c.whatsapp}?text=Hola,%20vengo%20de%20MaxShop%20y%20quiero%20consultar%20por%20sus%20beneficios." target="_blank" class="text-[10px] bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 px-2.5 py-1.5 rounded-xl border border-emerald-500/30 font-semibold transition">💬 Contacto</a>
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
                        alert("Comercio / QR Identificado: " + decodedText + "\\nDescuento del 5% aplicado y puntos sumados.");
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

            function abrirModalComercio() { document.getElementById('modalComercio').classList.remove('hidden'); }
            function cerrarModalComercio() { document.getElementById('modalComercio').classList.add('hidden'); }
            function abrirModalUsuario() { document.getElementById('modalUsuario').classList.remove('hidden'); }
            function cerrarModalUsuario() { document.getElementById('modalUsuario').classList.add('hidden'); }
            function cerrarOpcionesPago() { document.getElementById('modalOpcionesPago').classList.add('hidden'); }

            function abrirPoliticas() { document.getElementById('modalPoliticas').classList.remove('hidden'); }
            function cerrarPoliticas() { document.getElementById('modalPoliticas').classList.add('hidden'); }

            function verComprobanteDetalle(op, entidad, concepto, monto) {
                document.getElementById('compOp').innerText = "#" + op;
                document.getElementById('compEntidad').innerText = entidad;
                document.getElementById('compConcepto').innerText = concepto;
                document.getElementById('compMonto').innerText = monto;
                document.getElementById('modalComprobante').classList.remove('hidden');
            }
            function cerrarComprobante() { document.getElementById('modalComprobante').classList.add('hidden'); }

            function abrirLogin() {
                document.getElementById('modalLogin').classList.remove('hidden');
                document.getElementById('loginFormContainer').classList.remove('hidden');
                document.getElementById('panelSesionContainer').classList.add('hidden');
                document.getElementById('tituloModalLogin').innerText = "🔑 Iniciar Sesión / Mi Perfil";
            }
            function cerrarLogin() { document.getElementById('modalLogin').classList.add('hidden'); }

            function ejecutarLogin() {
                let id = document.getElementById('inputLoginIdentificador').value.trim();
                if(!id) {
                    alert("Por favor ingrese su correo o identificador.");
                    return;
                }
                let esComercio = id.toLowerCase().includes('comercio') || id.toLowerCase().includes('shop');

                document.getElementById('loginFormContainer').classList.add('hidden');
                document.getElementById('panelSesionContainer').classList.remove('hidden');
                document.getElementById('tituloModalLogin').innerText = "👤 Panel de Usuario & Historial";

                if(esComercio) {
                    document.getElementById('rolSesionBadge').innerText = "Rol: Comercio Adherido";
                    document.getElementById('rolSesionBadge').className = "text-[10px] text-cyan-400 font-bold uppercase";
                    document.getElementById('nombreSesionLabel').innerText = "Comercio: " + id;
                    document.getElementById('tituloHistorialRol').innerText = "🧾 Historial de Ventas Generadas";
                    document.getElementById('historialVentasContainer').classList.remove('hidden');
                    document.getElementById('historialConsumosContainer').classList.add('hidden');
                } else {
                    document.getElementById('rolSesionBadge').innerText = "Rol: Consumidor / Usuario";
                    document.getElementById('rolSesionBadge').className = "text-[10px] text-blue-400 font-bold uppercase";
                    document.getElementById('nombreSesionLabel').innerText = "Usuario: " + id;
                    document.getElementById('tituloHistorialRol').innerText = "🧾 Mi Historial de Consumos / Compras";
                    document.getElementById('historialConsumosContainer').classList.remove('hidden');
                    document.getElementById('historialVentasContainer').classList.add('hidden');
                }
            }

            function cerrarSesion() {
                document.getElementById('inputLoginIdentificador').value = "";
                document.getElementById('panelSesionContainer').classList.add('hidden');
                document.getElementById('loginFormContainer').classList.remove('hidden');
                document.getElementById('tituloModalLogin').innerText = "🔑 Iniciar Sesión / Mi Perfil";
            }

            function abrirAdmin() {
                let clave = prompt("Ingrese la Clave de Administrador:");
                if (clave === "AsistMaxAdmin2026Secure") {
                    document.getElementById('modalAdmin').classList.remove('hidden');
                } else if (clave !== null) {
                    alert("Clave incorrecta.");
                }
            }
            function cerrarAdmin() { document.getElementById('modalAdmin').classList.add('hidden'); }

            function cambiarPestanaAdmin(tipo) {
                ['comercios', 'usuarios', 'efectivo', 'operaciones'].forEach(t => {
                    document.getElementById('btnTab' + t.charAt(0).toUpperCase() + t.slice(1)).className = "pb-2 text-xs font-bold text-slate-400 hover:text-white transition whitespace-nowrap";
                    document.getElementById('seccion' + t.charAt(0).toUpperCase() + t.slice(1) + 'Admin').classList.add('hidden');
                });
                let colorActivo = tipo === 'comercios' ? 'cyan' : tipo === 'usuarios' ? 'blue' : tipo === 'efectivo' ? 'emerald' : 'emerald';
                document.getElementById('btnTab' + tipo.charAt(0).toUpperCase() + tipo.slice(1)).className = `pb-2 text-xs font-bold text-${colorActivo}-400 border-b-2 border-${colorActivo}-400 transition whitespace-nowrap`;
                document.getElementById('seccion' + tipo.charAt(0).toUpperCase() + tipo.slice(1) + 'Admin').classList.remove('hidden');
            }

            function exportarCSV(tipo) {
                let contenido = `ID,Fecha,Cliente/Comercio,Concepto,Monto\\n1,2026-08-24,Juan Pérez,Consumo con Descuento,9500`;
                let blob = new Blob([contenido], { type: 'text/csv;charset=utf-8;' });
                let enlace = document.createElement("a");
                enlace.href = URL.createObjectURL(blob);
                enlace.download = `reporte_${tipo}_maxshop.csv`;
                enlace.click();
                alert("Reporte CSV exportado correctamente.");
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
                    cuit_cuil: document.getElementById('c_cuit').value
                };
                let res = await fetch('/api/registrar-comercio', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
                });
                let json = await res.json();
                if(json.success) {
                    alert("¡Comercio MaxShop registrado con éxito!");
                    cerrarModalComercio();
                    document.getElementById('formComercio').reset();
                    cargarComerciosPublicos();
                } else { alert("Error: " + json.detail); }
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
                    document.getElementById('modalOpcionesPago').classList.remove('hidden');
                    document.getElementById('formUsuario').reset();
                } else { alert("Error: " + json.detail); }
            }

            function seleccionarMetodoPago(tipo) {
                cerrarOpcionesPago();
                if(tipo === 'suscripcion') {
                    window.open("https://mpago.la/12kwFZe", "_blank");
                } else if(tipo === 'unico') {
                    window.open("https://mpago.la/2xio5HU", "_blank");
                } else {
                    alert("¡Solicitud registrada con éxito! Acérquese a abonar en efectivo a cualquiera de los comercios adheridos de la red. Su alta quedará pendiente de validación para la posterior rendición del comercio.");
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
        response = supabase.table("comercios").select("nombre_fantasias, rubro, localidad, whatsapp").execute()
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/registrar-usuario")
def registrar_usuario(usuario: UsuarioModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no conectada.")
    try:
        response = supabase.table("usuarios").insert(usuario.dict()).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
