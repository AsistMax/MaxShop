from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="AsistMax-cobros", version="3.0")

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

# Modelos de datos para recibir la información de los formularios
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
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between font-sans selection:bg-cyan-500 selection:text-slate-950">

        <!-- Navbar Superior -->
        <header class="w-full px-6 py-4 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 shadow-lg">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-md shadow-cyan-500/20 font-black text-slate-950 text-lg">AM</div>
                <div>
                    <h1 class="text-sm font-black tracking-wider text-white">ASISTMAX</h1>
                    <p class="text-[10px] text-cyan-400 font-semibold tracking-widest uppercase">Red Fintech B2B</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button onclick="abrirAdmin()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition font-medium">
                    ⚙️ Admin
                </button>
            </div>
        </header>

        <!-- Contenido Principal -->
        <main class="w-full max-w-md mx-auto px-4 py-6 space-y-6 flex-1">

            <!-- Banner Principal -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl"></div>
                <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                <h2 class="text-2xl font-bold text-white mt-2">Pagos & Descuentos</h2>
                <p class="text-xs text-slate-400 mt-1">Escanea el código QR en el local adherido para procesar tu pago y aplicar beneficios al instante.</p>
                <div class="mt-5">
                    <button onclick="escanearQR()" class="w-full group relative inline-flex items-center justify-center px-6 py-3.5 text-sm font-bold text-slate-950 transition-all bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl hover:from-cyan-300 hover:to-blue-400 shadow-lg shadow-cyan-500/20 active:scale-95">
                        <span class="mr-2 text-base">📷</span> Escanear QR del Comercio
                    </button>
                </div>
            </div>

            <!-- Botones de Registro -->
            <div class="grid grid-cols-2 gap-3">
                <button onclick="abrirModalComercio()" class="bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-cyan-400 transition">Sumar mi Comercio</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Registro comercial</p>
                </button>
                <button onclick="abrirModalUsuario()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-blue-400 text-xl mb-1">👤</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Crear Cuenta</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Beneficios exclusivos</p>
                </button>
            </div>

            <!-- Listado de Comercios Adheridos -->
            <div class="space-y-3">
                <div class="flex justify-between items-center px-1">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">🏢 Comercios Adheridos</h3>
                    <span class="text-[10px] text-cyan-400">Red AsistMax</span>
                </div>
                <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-cyan-400">☕</div>
                        <div>
                            <h4 class="text-xs font-bold text-white">Café Central AsistMax</h4>
                            <p class="text-[11px] text-slate-400">Gastronomía • 15% OFF</p>
                        </div>
                    </div>
                    <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-lg border border-emerald-500/20 font-semibold">Activo</span>
                </div>
            </div>

        </main>

        <!-- MODAL REGISTRO COMERCIO -->
        <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">🏪 Registro de Comercio</h3>
                    <button onclick="cerrarModalComercio()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
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
                            <optgroup label="Alimentos y Consumo Masivo">
                                <option value="Supermercados y almacenes">Supermercados y almacenes</option>
                                <option value="Gastronomía">Gastronomía</option>
                                <option value="Verdulerías y carnicerías">Verdulerías y carnicerías</option>
                            </optgroup>
                            <optgroup label="Indumentaria y Estética">
                                <option value="Textil y calzado">Textil y calzado</option>
                                <option value="Perfumería y cosmética">Perfumería y cosmética</option>
                                <option value="Joyería y relojería">Joyería y relojería</option>
                            </optgroup>
                            <optgroup label="Hogar, Construcción y Tecnología">
                                <option value="Ferretería y corralón">Ferretería y corralón</option>
                                <option value="Electrodomésticos">Electrodomésticos</option>
                                <option value="Bazar y decoración">Bazar y decoración</option>
                            </optgroup>
                            <optgroup label="Servicios y Profesional">
                                <option value="Salud y bienestar">Salud y bienestar</option>
                                <option value="Automotriz">Automotriz</option>
                                <option value="Turismo y hotelería">Turismo y hotelería</option>
                            </optgroup>
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
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg">Registrar Comercio</button>
                </form>
            </div>
        </div>

        <!-- MODAL REGISTRO USUARIO -->
        <div id="modalUsuario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 w-full max-w-md rounded-3xl p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
                <div class="flex justify-between items-center">
                    <h3 class="text-base font-bold text-white">👤 Registro de Usuario</h3>
                    <button onclick="cerrarModalUsuario()" class="text-slate-400 hover:text-white text-lg font-bold">✕</button>
                </div>
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
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-blue-400 to-indigo-500 text-slate-950 font-bold rounded-xl text-xs mt-2 shadow-lg">Crear Cuenta</button>
                </form>
            </div>
        </div>

        <!-- Footer -->
        <footer class="w-full text-center py-5 border-t border-slate-900 text-xs text-slate-500 bg-slate-950">
            <p class="font-semibold text-slate-400">AsistMax-cobros &copy; 2026</p>
        </footer>

        <!-- Scripts de interacción -->
        <script>
            function escanearQR() {
                alert("📷 [Cámara activada]: Apunte al código QR del comercio asociado.");
            }
            function abrirModalComercio() { document.getElementById('modalComercio').classList.remove('hidden'); }
            function cerrarModalComercio() { document.getElementById('modalComercio').classList.add('hidden'); }
            function abrirModalUsuario() { document.getElementById('modalUsuario').classList.remove('hidden'); }
            function cerrarModalUsuario() { document.getElementById('modalUsuario').classList.add('hidden'); }

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
                    alert("¡Comercio registrado con éxito en AsistMax!");
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
                    alert("¡Cuenta creada con éxito en AsistMax!");
                    cerrarModalUsuario();
                    document.getElementById('formUsuario').reset();
                } else {
                    alert("Error al registrar: " + json.detail);
                }
            }

            function abrirAdmin() {
                let clave = prompt("Ingrese la clave de Administrador:");
                if (clave === "admin123") {
                    alert("Acceso concedido al Panel de Control.");
                } else if (clave !== null) {
                    alert("Clave incorrecta.");
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
