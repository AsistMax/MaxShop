from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="AsistMax-cobros", version="3.5")

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
        <title>AsistMax - Red de Cobros y Comercios Adheridos</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- Librería para lectura real de códigos QR -->
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950">

        <!-- Navbar Superior con Login y Admin -->
        <header class="w-full px-6 py-4 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 shadow-lg">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-md shadow-cyan-500/20 font-black text-slate-950 text-lg">AM</div>
                <div>
                    <h1 class="text-sm font-black tracking-wider text-white">ASISTMAX</h1>
                    <p class="text-[10px] text-cyan-400 font-semibold tracking-widest uppercase">Red Fintech B2B</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button onclick="abrirLogin()" class="text-xs bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-3 py-1.5 rounded-lg border border-cyan-500/30 transition font-semibold">
                    🔑 Login
                </button>
                <button onclick="abrirAdmin()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition font-medium">
                    ⚙️ Admin
                </button>
            </div>
        </header>

        <!-- Contenido Principal -->
        <main class="w-full max-w-md mx-auto px-4 py-6 space-y-6 flex-1">

            <!-- Tarjeta de Progreso / Nivel del Cliente (Simulada para usuario logueado) -->
            <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-4 shadow-xl flex items-center justify-between">
                <div class="space-y-1">
                    <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-800/50">Mi Nivel Actual</span>
                    <h3 class="text-sm font-bold text-white">Nivel Plata • 450 Puntos</h3>
                    <p class="text-[11px] text-slate-400">Te faltan 55p para el Nivel Oro</p>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center text-slate-950 font-black text-lg shadow-lg">
                    🥈
                </div>
            </div>

            <!-- Banner Principal Escáner -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl"></div>
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-2xl font-bold text-white mt-2">Pagos & Descuentos</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el código QR del comercio adherido para validar tu beneficio del 5% mínimo o promoción vigente y sumar puntos.</p>
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
                    <p class="text-[11px] text-slate-400 mt-0.5">100% Gratuito (5% base)</p>
                </button>
                <button onclick="abrirModalUsuario()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-blue-400 text-xl mb-1">👤</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Crear Cuenta</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Suscripción mensual</p>
                </button>
            </div>

            <!-- Listado de Comercios Adheridos -->
            <div class="space-y-3">
                <div class="flex justify-between items-center px-1">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">🏢 Comercios Adheridos (5% OFF Base)</h3>
                    <span class="text-[10px] text-cyan-400">Red AsistMax</span>
                </div>
                <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-cyan-400">☕</div>
                        <div>
                            <h4 class="text-xs font-bold text-white">Café Central AsistMax</h4>
                            <p class="text-[11px] text-slate-400">Gastronomía • 5% Base + Promo Día</p>
                        </div>
                    </div>
                    <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-lg border border-emerald-500/20 font-semibold">Activo</span>
                </div>
            </div>

        </main>

        <!-- MODAL CÁMARA ESCÁNER QR -->
        <div id="modalQR" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex flex-col items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-5 space-y-4 shadow-2xl text-center">
                <div class="flex justify-between items-center">
                    <h3 class="text-sm font-bold text-white">📷 Escáner de Código QR</h3>
                    <button onclick="cerrarEscaneoQR()" class="text-slate-400 hover:text-white text-lg font-bold p-1">✕</button>
                </div>
                <div id="reader" class="w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 min-h-[250px]"></div>
                <p class="text-[11px] text-slate-400">Enfoque el código QR del comercio para validar su compra y acumular puntos.</p>
                <button onclick="cerrarEscaneoQR()" class="w-full py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs hover:bg-slate-700 transition">Cancelar / Cerrar</button>
            </div>
        </div>

        <!-- MODAL REGISTRO COMERCIO (GRATIS) -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">🏪 Sumar mi Comercio (Gratis)</h3>
                    <button onclick="cerrarModalComercio()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-cyan-400 bg-cyan-950/40 p-2.5 rounded-xl border border-cyan-800/30">Inscripción sin costo. Se otorga su QR de identificación y el 5% de descuento base obligatorio como costo publicitario.</p>
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
                        <input type="text" id="c_fantasia" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Rubro</label>
                        <select id="c_rubro" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                            <option value="">Seleccione un rubro...</option>
                            <option value="Supermercados y almacenes">Supermercados y almacenes</option>
                            <option value="Gastronomía">Gastronomía</option>
                            <option value="Indumentaria y calzado">Indumentaria y calzado</option>
                            <option value="Servicios y otros">Servicios y otros</option>
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

        <!-- MODAL REGISTRO USUARIO + SUSCRIPCIÓN MERCADO PAGO -->
        <div id="modalUsuario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">👤 Crear Cuenta & Suscripción</h3>
                    <button onclick="cerrarModalUsuario()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-blue-400 bg-blue-950/40 p-2.5 rounded-xl border border-blue-800/30">Membresía mensual de $10.000. Al registrarse será redirigido automáticamente a Mercado Pago para abonar su suscripción.</p>
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
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-blue-400 to-indigo-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg">Pagar Suscripción en Mercado Pago</button>
                </form>
            </div>
        </div>

        <!-- MODAL PANEL DE ADMINISTRADOR Y COLABORADORES SEPARADO Y ORDENADO -->
        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <span class="text-xl">⚙️</span>
                        <h3 class="text-base font-bold text-white">Panel de Control & Gestión AsistMax</h3>
                    </div>
                    <button onclick="cerrarAdmin()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>

                <!-- Contadores superiores -->
                <div class="grid grid-cols-3 gap-3">
                    <div class="bg-slate-950 border border-slate-800 p-3 rounded-2xl text-center">
                        <span class="text-[10px] text-slate-400 uppercase font-semibold">Comercios Activos</span>
                        <h4 class="text-lg font-black text-cyan-400 mt-0.5">24</h4>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 p-3 rounded-2xl text-center">
                        <span class="text-[10px] text-slate-400 uppercase font-semibold">Usuarios Suscriptos</span>
                        <h4 class="text-lg font-black text-blue-400 mt-0.5">142</h4>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 p-3 rounded-2xl text-center">
                        <span class="text-[10px] text-slate-400 uppercase font-semibold">Nivel Promedio Red</span>
                        <h4 class="text-lg font-black text-emerald-400 mt-0.5">Plata</h4>
                    </div>
                </div>

                <!-- Pestañas de Navegación del Panel -->
                <div class="flex border-b border-slate-800 space-x-4 pt-2">
                    <button onclick="cambiarPestanaAdmin('comercios')" id="btnTabComercios" class="pb-2 text-xs font-bold text-cyan-400 border-b-2 border-cyan-400 transition">🏪 Gestión de Comercios</button>
                    <button onclick="cambiarPestanaAdmin('usuarios')" id="btnTabUsuarios" class="pb-2 text-xs font-bold text-slate-400 hover:text-white transition">👤 Gestión de Usuarios</button>
                </div>

                <!-- SECCIÓN COMERCIOS -->
                <div id="seccionComerciosAdmin" class="space-y-3">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-cyan-400 uppercase">📊 Listado y Ventas de Comercios</h4>
                        <button onclick="exportarCSV('comercios')" class="text-[11px] bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-2.5 py-1 rounded-lg border border-cyan-500/30 font-semibold">📥 Descargar CSV Comercios</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden p-3 space-y-2">
                        <div class="flex justify-between items-center text-xs text-slate-400 border-b border-slate-800 pb-2">
                            <span>Comercio (ID)</span>
                            <span>Estrella / Nivel</span>
                            <span>Ventas / Monto</span>
                            <span>Acción</span>
                        </div>
                        <div class="flex justify-between items-center text-xs text-white py-1">
                            <div>
                                <p class="font-bold">Café Central</p>
                                <p class="text-[10px] text-slate-400">ID: #102</p>
                            </div>
                            <span class="text-cyan-400">Estrella 2</span>
                            <span class="text-emerald-400">140 ventas ($450.000)</span>
                            <button onclick="cambiarEstadoComercio('Café Central')" class="text-[10px] bg-slate-800 hover:bg-slate-700 px-2 py-1 rounded border border-slate-700">Pausar / Activar</button>
                        </div>
                    </div>
                </div>

                <!-- SECCIÓN USUARIOS (OCULTA POR DEFECTO) -->
                <div id="seccionUsuariosAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-blue-400 uppercase">📊 Listado, Puntos y Suscripciones de Usuarios</h4>
                        <button onclick="exportarCSV('usuarios')" class="text-[11px] bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 px-2.5 py-1 rounded-lg border border-blue-500/30 font-semibold">📥 Descargar CSV Usuarios</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden p-3 space-y-2">
                        <div class="flex justify-between items-center text-xs text-slate-400 border-b border-slate-800 pb-2">
                            <span>Usuario / DNI</span>
                            <span>Nivel / Puntos</span>
                            <span>Suscripción</span>
                            <span>Acción</span>
                        </div>
                        <div class="flex justify-between items-center text-xs text-white py-1">
                            <div>
                                <p class="font-bold">Juan Pérez</p>
                                <p class="text-[10px] text-slate-400">DNI: 34... • wpp: 3834...</p>
                            </div>
                            <span class="text-blue-400">Plata (450 pts)</span>
                            <span class="text-amber-400">Pendiente / Efectivo</span>
                            <button onclick="darDeAlta('Juan Pérez')" class="text-[10px] bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold px-2 py-1 rounded">Dar de Alta</button>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <!-- MODAL LEGALES / POLÍTICAS -->
        <div id="modalLegal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-3xl p-6 space-y-4 max-h-[85vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 id="legalTitulo" class="text-base font-bold text-white">Información Legal</h3>
                    <button onclick="cerrarLegal()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <div id="legalContenido" class="text-xs text-slate-300 space-y-3 leading-relaxed"></div>
            </div>
        </div>

        <!-- Footer con enlaces en letras azules -->
        <footer class="w-full text-center py-6 border-t border-slate-900 text-xs text-slate-500 bg-slate-950 space-y-2">
            <p class="font-semibold text-slate-400">AsistMax-cobros &copy; 2026 - Todos los derechos reservados.</p>
            <div class="flex justify-center flex-wrap gap-2 text-[11px]">
                <a href="javascript:void(0)" onclick="mostrarLegal('terminos')" class="text-cyan-400 hover:underline">Términos y Condiciones</a>
                <span class="text-slate-700">•</span>
                <a href="javascript:void(0)" onclick="mostrarLegal('privacidad')" class="text-cyan-400 hover:underline">Política de Privacidad y Confidencialidad</a>
                <span class="text-slate-700">•</span>
                <a href="javascript:void(0)" onclick="mostrarLegal('suscripcion')" class="text-cyan-400 hover:underline">Condiciones de Suscripción</a>
            </div>
        </footer>

        <!-- Scripts de interacción -->
        <script>
            let html5QrCode = null;

            function iniciarEscaneoQR() {
                const modal = document.getElementById('modalQR');
                modal.classList.remove('hidden');
                if (!html5QrCode) {
                    html5QrCode = new Html5Qrcode("reader");
                }
                const config = { fps: 10, qrbox: { width: 220, height: 220 } };
                html5QrCode.start(
                    { facingMode: "environment" },
                    config,
                    (decodedText) => {
                        detenerEscaneoQR();
                        alert("Comercio / QR Identificado:\\n\\n" + decodedText + "\\n\\nBeneficio del 5% base o promoción aplicada con éxito. Acumulando puntos.");
                    },
                    (errorMessage) => {}
                ).catch((err) => {
                    alert("No se pudo iniciar la cámara. Verifique permisos o conexión HTTPS.");
                    modal.classList.add('hidden');
                });
            }

            function detenerEscaneoQR() {
                const modal = document.getElementById('modalQR');
                if (html5QrCode && html5QrCode.isScanning) {
                    html5QrCode.stop().then(() => modal.classList.add('hidden')).catch(() => modal.classList.add('hidden'));
                } else {
                    modal.classList.add('hidden');
                }
            }

            function cerrarEscaneoQR() { detenerEscaneoQR(); }

            function abrirModalComercio() { document.getElementById('modalComercio').classList.remove('hidden'); }
            function cerrarModalComercio() { document.getElementById('modalComercio').classList.add('hidden'); }
            function abrirModalUsuario() { document.getElementById('modalUsuario').classList.remove('hidden'); }
            function cerrarModalUsuario() { document.getElementById('modalUsuario').classList.add('hidden'); }

            function abrirLogin() {
                let id = prompt("Ingrese su Correo o ID de Usuario / Comercio para ingresar:");
                if(id) {
                    alert("Redirigiendo al panel de control de: " + id);
                }
            }

            function abrirAdmin() {
                let clave = prompt("Ingrese la Clave Única de Administrador o Colaborador:");
                if (clave === "AsistMaxAdmin2026Secure") {
                    document.getElementById('modalAdmin').classList.remove('hidden');
                } else if (clave !== null) {
                    alert("Clave incorrecta o acceso no autorizado.");
                }
            }

            function cerrarAdmin() {
                document.getElementById('modalAdmin').classList.add('hidden');
            }

            function cambiarPestanaAdmin(tipo) {
                const btnComercios = document.getElementById('btnTabComercios');
                const btnUsuarios = document.getElementById('btnTabUsuarios');
                const secComercios = document.getElementById('seccionComerciosAdmin');
                const secUsuarios = document.getElementById('seccionUsuariosAdmin');

                if(tipo === 'comercios') {
                    btnComercios.className = "pb-2 text-xs font-bold text-cyan-400 border-b-2 border-cyan-400 transition";
                    btnUsuarios.className = "pb-2 text-xs font-bold text-slate-400 hover:text-white transition";
                    secComercios.classList.remove('hidden');
                    secUsuarios.classList.add('hidden');
                } else {
                    btnUsuarios.className = "pb-2 text-xs font-bold text-blue-400 border-b-2 border-blue-400 transition";
                    btnComercios.className = "pb-2 text-xs font-bold text-slate-400 hover:text-white transition";
                    secUsuarios.classList.remove('hidden');
                    secComercios.classList.add('hidden');
                }
            }

            function cambiarEstadoComercio(nombre) {
                alert("Estado modificado para el comercio: " + nombre);
            }

            function darDeAlta(nombre) {
                alert("¡Cuenta dada de alta por el Administrador/Colaborador para: " + nombre + "!");
            }

            function exportarCSV(tipo) {
                let contenido = tipo === 'comercios' ? "ID,Comercio,Estrella,Ventas,MontoTotal\\n102,Café Central,2,140,450000" : "ID,Usuario,DNI,Puntos,Nivel,Suscripcion\\n1,Juan Pérez,34000000,450,Plata,Activo";
                let blob = new Blob([contenido], { type: 'text/csv;charset=utf-8;' });
                let enlace = document.createElement("a");
                enlace.href = URL.createObjectURL(blob);
                enlace.download = `reporte_${tipo}_asistmax.csv`;
                enlace.click();
                alert("Archivo CSV descargado con éxito.");
            }

            const textosLegales = {
                terminos: `<b>Términos y Condiciones Generales:</b> AsistMax opera como una red tecnológica B2C de intermediación publicitaria y fidelización comercial. Los comercios adheridos participan de forma gratuita y ofrecen un beneficio mínimo obligatorio del 5% en carácter de contraprestación publicitaria dentro de la red.`,
                privacidad: `<b>Política de Privacidad y Confidencialidad:</b> En cumplimiento de las normativas de protección de datos personales y confidencialidad, la información provista por usuarios y comercios se encuentra rigurosamente resguardada.`,
                suscripcion: `<b>Condiciones de Suscripción y Período de Gracia:</b> La activación de la cuenta de usuario se encuentra sujeta al abono de la membresía mensual ($10.000).`
            };

            function mostrarLegal(tipo) {
                document.getElementById('legalTitulo').innerText = tipo === 'terminos' ? 'Términos y Condiciones' : tipo === 'privacidad' ? 'Política de Privacidad' : 'Condiciones de Suscripción';
                document.getElementById('legalContenido').innerHTML = textosLegales[tipo];
                document.getElementById('modalLegal').classList.remove('hidden');
            }

            function cerrarLegal() {
                document.getElementById('modalLegal').classList.add('hidden');
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
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                let json = await res.json();
                if(json.success) {
                    alert("¡Comercio registrado gratis con éxito! Ya se generó su QR y su beneficio base del 5%.");
                    cerrarModalComercio();
                    document.getElementById('formComercio').reset();
                } else {
                    alert("Error al registrar: " + json.detail);
                }
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
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                let json = await res.json();
                if(json.success) {
                    alert("¡Registro pre-aprobado! Redirigiendo a Mercado Pago para completar la suscripción mensual de $10.000...");
                    window.location.href = "https://www.mercadopago.com.ar"; // Enlace directo a tu cuenta/suscripción de MP
                } else {
                    alert("Error al registrar: " + json.detail);
                }
            }
        </script>
    </body>
    </html>
    """

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
