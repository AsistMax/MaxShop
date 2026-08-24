from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="MaxShop - AsistMax", version="4.2")

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
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950">

        <!-- Navbar Superior -->
        <header class="w-full px-6 py-4 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 shadow-lg">
            <div class="flex items-center space-x-3">
                <!-- LOGO CON TU ENLACE DIRECTO DE IMGBB -->
                <img src="https://i.ibb.co/rRGzqgnx/logo.jpg" alt="MaxShop Logo" id="logoMaxShop" class="w-10 h-10 rounded-xl object-cover border border-cyan-500/40 shadow-md shadow-cyan-500/20 bg-slate-900">
                <div>
                    <h1 class="text-sm font-black tracking-wider text-white">MAXSHOP <span class="text-cyan-400 font-light">| AsistMax</span></h1>
                    <p class="text-[10px] text-cyan-400 font-semibold tracking-widest uppercase">Red B2B & Consumidores</p>
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

            <!-- BANNER PRINCIPAL CON TU ENLACE DIRECTO DE IMGBB -->
            <div class="w-full rounded-3xl overflow-hidden border border-slate-800 shadow-xl relative bg-slate-900">
                <img src="https://i.ibb.co/wFDXX9TK/banner.jpg" alt="MaxShop Banner" id="bannerMaxShop" class="w-full h-36 object-cover">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent flex items-end p-4">
                    <div>
                        <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/90 px-2.5 py-0.5 rounded-full border border-cyan-800/50">Comercio Destacado</span>
                        <h2 class="text-lg font-extrabold text-white mt-1">MaxShop Oficial</h2>
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

            <!-- Sección Mi Historial (Dinámico) -->
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-3">
                <div class="flex justify-between items-center">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">🧾 Mi Historial de Operaciones</h3>
                    <div class="space-x-1">
                        <button onclick="cambiarVistaHistorial('consumos')" id="btnHistConsumos" class="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/40 font-bold">Consumos</button>
                        <button onclick="cambiarVistaHistorial('ventas')" id="btnHistVentas" class="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">Ventas (MaxShop)</button>
                    </div>
                </div>

                <!-- Historial Consumos -->
                <div id="historialConsumosContainer" class="space-y-2">
                    <div class="text-xs bg-slate-950 p-3 rounded-xl border border-slate-800/80 space-y-1">
                        <div class="flex justify-between text-slate-400 text-[10px]">
                            <span>Fecha: 24/08/2026 - 08:30hs</span>
                            <span>Op #1042</span>
                        </div>
                        <p class="font-bold text-white">Consumo en MaxShop (5% desc. aplicado)</p>
                        <div class="flex justify-between items-center pt-1 border-t border-slate-900">
                            <span class="text-slate-400">Total pagado: <strong class="text-emerald-400">$9.500</strong></span>
                            <button onclick="verComprobanteDetalle('1042', 'MaxShop', 'Consumo con Descuento', '$9.500')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20">Ver Comprobante</button>
                        </div>
                    </div>
                </div>

                <!-- Historial Ventas -->
                <div id="historialVentasContainer" class="space-y-2 hidden">
                    <div class="text-xs bg-slate-950 p-3 rounded-xl border border-slate-800/80 space-y-1">
                        <div class="flex justify-between text-slate-400 text-[10px]">
                            <span>Fecha: 23/08/2026 - 19:15hs</span>
                            <span>Op #1039</span>
                        </div>
                        <p class="font-bold text-white">Venta realizada a Cliente: Juan Pérez</p>
                        <div class="flex justify-between items-center pt-1 border-t border-slate-900">
                            <span class="text-slate-400">Acreditado: <strong class="text-emerald-400">$12.200</strong></span>
                            <button onclick="verComprobanteDetalle('1039', 'MaxShop', 'Venta a Consumidor', '$12.200')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20">Ver Comprobante</button>
                        </div>
                    </div>
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
                <p class="text-[11px] text-slate-400">Enfoque el código QR del comercio para validar su compra y obtener su beneficio.</p>
                <button onclick="cerrarEscaneoQR()" class="w-full py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl text-xs hover:bg-slate-700 transition">Cancelar / Cerrar</button>
            </div>
        </div>

        <!-- MODAL REGISTRO COMERCIO -->
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
                        <input type="text" id="c_fantasia" value="MaxShop" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-400">Rubro</label>
                        <select id="c_rubro" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:border-cyan-500 outline-none mt-1">
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

        <!-- MODAL REGISTRO USUARIO -->
        <div id="modalUsuario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">👤 Cuenta Consumidor & Suscripción</h3>
                    <button onclick="cerrarModalUsuario()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <p class="text-[11px] text-blue-400 bg-blue-950/40 p-2.5 rounded-xl border border-blue-800/30">Membresía mensual de $10.000. Complete sus datos para registrarse y elija su método de pago sin abandonar la plataforma.</p>
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

        <!-- MODAL SELECTOR DE PAGO -->
        <div id="modalOpcionesPago" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 class="text-sm font-bold text-white">💳 Seleccione Método de Pago ($10.000)</h3>
                    <button onclick="cerrarOpcionesPago()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
                <div class="space-y-3">
                    <div onclick="pagarSuscripcion()" class="bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-blue-500/50 p-4 rounded-2xl cursor-pointer transition space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold text-blue-400">🔄 Suscripción Automática Mensual</span>
                            <span class="text-[10px] bg-blue-950 text-blue-300 px-2 py-0.5 rounded border border-blue-800">Con Tarjeta</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Débito mensual automático. <strong class="text-slate-300">Nota: No afecta el margen ni límite de compra de tu tarjeta de crédito.</strong></p>
                    </div>

                    <div onclick="pagarLinkUnico()" class="bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-cyan-500/50 p-4 rounded-2xl cursor-pointer transition space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold text-cyan-400">🔗 Link de Pago Único (Efectivo / Débito / Otros)</span>
                            <span class="text-[10px] bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-800">Sin Tarjeta de Crédito</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Ideal si no posees tarjeta de crédito. Paga mediante medios habilitados.</p>
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

        <!-- MODAL PANEL DE ADMINISTRADOR -->
        <div id="modalAdmin" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <span class="text-xl">⚙️</span>
                        <h3 class="text-base font-bold text-white">Panel de Control & Auditoría MaxShop</h3>
                    </div>
                    <button onclick="cerrarAdmin()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>

                <div class="flex border-b border-slate-800 space-x-4 pt-2">
                    <button onclick="cambiarPestanaAdmin('comercios')" id="btnTabComercios" class="pb-2 text-xs font-bold text-cyan-400 border-b-2 border-cyan-400 transition">🏪 Comercios</button>
                    <button onclick="cambiarPestanaAdmin('usuarios')" id="btnTabUsuarios" class="pb-2 text-xs font-bold text-slate-400 hover:text-white transition">👤 Usuarios (Consumidores)</button>
                    <button onclick="cambiarPestanaAdmin('operaciones')" id="btnTabOperaciones" class="pb-2 text-xs font-bold text-slate-400 hover:text-white transition">🧾 Historial Operaciones</button>
                </div>

                <div id="seccionComerciosAdmin" class="space-y-3">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-cyan-400 uppercase">📊 Listado de Comercios</h4>
                        <button onclick="exportarCSV('comercios')" class="text-[11px] bg-cyan-500/10 text-cyan-400 px-2.5 py-1 rounded-lg border border-cyan-500/30">📥 CSV Comercios</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs text-white flex justify-between items-center">
                        <div><p class="font-bold">MaxShop Oficial</p><p class="text-[10px] text-slate-400">ID: #1 • Rubro: Supermercados</p></div>
                        <span class="text-emerald-400">140 transacciones ($450.000)</span>
                    </div>
                </div>

                <div id="seccionUsuariosAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-blue-400 uppercase">📊 Listado de Usuarios y Membresías</h4>
                        <button onclick="exportarCSV('usuarios')" class="text-[11px] bg-blue-500/10 text-blue-400 px-2.5 py-1 rounded-lg border border-blue-500/30">📥 CSV Usuarios</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs text-white flex justify-between items-center">
                        <div><p class="font-bold">Juan Pérez (Comerciante/Consumidor)</p><p class="text-[10px] text-slate-400">DNI: 34... • Plata (450 pts)</p></div>
                        <span class="text-amber-400">Suscripción Activa</span>
                    </div>
                </div>

                <div id="seccionOperacionesAdmin" class="space-y-3 hidden">
                    <div class="flex justify-between items-center">
                        <h4 class="text-xs font-bold text-emerald-400 uppercase">🧾 Auditoría Centralizada de Comprobantes</h4>
                        <button onclick="exportarCSV('operaciones')" class="text-[11px] bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-lg border border-emerald-500/30">📥 CSV Historial</button>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-3 text-xs text-white flex justify-between items-center">
                        <div><p class="font-bold">Juan Pérez ➔ MaxShop</p><p class="text-[10px] text-slate-400">24/08/2026 - Op #1042</p></div>
                        <span class="text-emerald-400 font-bold">$9.500</span>
                    </div>
                </div>

            </div>
        </div>

        <!-- Footer -->
        <footer class="w-full text-center py-6 border-t border-slate-900 text-xs text-slate-500 bg-slate-950 space-y-2">
            <p class="font-semibold text-slate-400">MaxShop & AsistMax &copy; 2026 - Todos los derechos reservados.</p>
        </footer>

        <!-- Scripts -->
        <script>
            let html5QrCode = null;

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

            function verComprobanteDetalle(op, entidad, concepto, monto) {
                document.getElementById('compOp').innerText = "#" + op;
                document.getElementById('compEntidad').innerText = entidad;
                document.getElementById('compConcepto').innerText = concepto;
                document.getElementById('compMonto').innerText = monto;
                document.getElementById('modalComprobante').classList.remove('hidden');
            }
            function cerrarComprobante() { document.getElementById('modalComprobante').classList.add('hidden'); }

            function cambiarVistaHistorial(tipo) {
                if(tipo === 'consumos') {
                    document.getElementById('historialConsumosContainer').classList.remove('hidden');
                    document.getElementById('historialVentasContainer').classList.add('hidden');
                    document.getElementById('btnHistConsumos').className = "text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/40 font-bold";
                    document.getElementById('btnHistVentas').className = "text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700";
                } else {
                    document.getElementById('historialConsumosContainer').classList.add('hidden');
                    document.getElementById('historialVentasContainer').classList.remove('hidden');
                    document.getElementById('btnHistConsumos').className = "text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700";
                    document.getElementById('btnHistVentas').className = "text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/40 font-bold";
                }
            }

            function abrirLogin() {
                let id = prompt("Ingrese su Correo o ID:");
                if(id) alert("Ingresando a su perfil...");
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
                ['comercios', 'usuarios', 'operaciones'].forEach(t => {
                    document.getElementById('btnTab' + t.charAt(0).toUpperCase() + t.slice(1)).className = "pb-2 text-xs font-bold text-slate-400 hover:text-white transition";
                    document.getElementById('seccion' + t.charAt(0).toUpperCase() + t.slice(1) + 'Admin').classList.add('hidden');
                });
                document.getElementById('btnTab' + tipo.charAt(0).toUpperCase() + tipo.slice(1)).className = "pb-2 text-xs font-bold text-" + (tipo==='comercios'?'cyan':tipo==='usuarios'?'blue':'emerald') + "-400 border-b-2 border-" + (tipo==='comercios'?'cyan':tipo==='usuarios'?'blue':'emerald') + "-400 transition";
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

            function pagarSuscripcion() {
                window.location.href = "https://mpago.la/12kwFZe";
            }

            function pagarLinkUnico() {
                window.location.href = "https://mpago.la/2xio5HU";
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
