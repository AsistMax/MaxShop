from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="AsistMax-cobros", version="2.0")

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

class TransaccionRequest(BaseModel):
    monto_bruto: float
    comercio_id: str
    cliente_id: str

@app.get("/", response_class=HTMLResponse)
def mostrar_interfaz():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AsistMax - Plataforma de Cobros y Red de Descuentos</title>
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
                <div class="text-[11px] px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold hidden sm:block">
                    ● Sistema Activo
                </div>
            </div>
        </header>

        <!-- Contenido Principal -->
        <main class="w-full max-w-lg mx-auto px-4 py-6 space-y-6 flex-1">

            <!-- Banner Principal de Bienvenida -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
                <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl"></div>
                <div class="flex justify-between items-start">
                    <div>
                        <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/80 px-2.5 py-1 rounded-full border border-cyan-800/50">Billetera Inteligente</span>
                        <h2 class="text-2xl font-bold text-white mt-2">Pagos & Beneficios</h2>
                        <p class="text-xs text-slate-400 mt-1">Escanea el código QR del comercio asociado para aplicar split de pagos y descuentos instantáneos.</p>
                    </div>
                </div>
                <div class="mt-6">
                    <button onclick="escanearQR()" class="w-full group relative inline-flex items-center justify-center px-6 py-4 text-sm font-bold text-slate-950 transition-all duration-200 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl hover:from-cyan-300 hover:to-blue-400 shadow-xl shadow-cyan-500/20 active:scale-95">
                        <span class="mr-2 text-lg">📷</span> Escanear QR del Comercio
                    </button>
                </div>
            </div>

            <!-- Accesos Rápidos de Registro (Comercios y Usuarios) -->
            <div class="grid grid-cols-2 gap-3">
                <button onclick="registrarComercio()" class="bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-cyan-400 text-xl mb-1">🏪</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-cyan-400 transition">Sumar mi Comercio</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Acepta pagos y cobra con QR</p>
                </button>
                <button onclick="registrarUsuario()" class="bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 p-4 rounded-2xl text-left transition-all group">
                    <div class="text-blue-400 text-xl mb-1">👤</div>
                    <h3 class="text-xs font-bold text-white group-hover:text-blue-400 transition">Crear Cuenta</h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">Accede a beneficios exclusivos</p>
                </button>
            </div>

            <!-- Listado de Comercios Adheridos -->
            <div class="space-y-3">
                <div class="flex justify-between items-center px-1">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">🏢 Comercios Adheridos Destacados</h3>
                    <span class="text-[10px] text-cyan-400">Ver todos (12)</span>
                </div>

                <!-- Comercio 1 -->
                <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 flex items-center justify-between hover:border-slate-700 transition">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-cyan-400">☕</div>
                        <div>
                            <h4 class="text-xs font-bold text-white">Café Central AsistMax</h4>
                            <p class="text-[11px] text-slate-400">Gastronomía • 15% OFF con app</p>
                        </div>
                    </div>
                    <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-lg border border-emerald-500/20 font-semibold">Activo</span>
                </div>

                <!-- Comercio 2 -->
                <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 flex items-center justify-between hover:border-slate-700 transition">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-blue-400">💊</div>
                        <div>
                            <h4 class="text-xs font-bold text-white">Farmacia San José</h4>
                            <p class="text-[11px] text-slate-400">Salud & Bienestar • 20% OFF</p>
                        </div>
                    </div>
                    <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-lg border border-emerald-500/20 font-semibold">Activo</span>
                </div>
            </div>

        </main>

        <!-- Pie de página institucional -->
        <footer class="w-full text-center py-5 border-t border-slate-900 text-xs text-slate-500 bg-slate-950">
            <p class="font-semibold text-slate-400">AsistMax-cobros &copy; 2026</p>
            <p class="text-[10px] text-slate-600 mt-1">Infraestructura tecnológica segura para comercios y usuarios.</p>
        </footer>

        <!-- Scripts de interacción moderna -->
        <script>
            function escanearQR() {
                alert("📷 [Cámara activada]: Apunte al código QR provisto por el comercio en caja para procesar el cobro automático.");
            }
            function registrarComercio() {
                let nombre = prompt("Ingrese el nombre de su comercio para asociarse a AsistMax:");
                if (nombre) {
                    alert("¡Gracias, " + nombre + "! Pronto nos pondremos en contacto para habilitar su terminal QR.");
                }
            }
            function registrarUsuario() {
                let email = prompt("Ingrese su correo electrónico para registrarse en AsistMax:");
                if (email) {
                    alert("¡Registro exitoso! Ya puede disfrutar de los beneficios en los comercios adheridos.");
                }
            }
            function abrirAdmin() {
                let clave = prompt("Ingrese la clave de Administrador:");
                if (clave === "admin123") {
                    alert("Acceso concedido al Panel de Control de AsistMax.");
                } else if (clave !== null) {
                    alert("Clave incorrecta.");
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/api/promociones")
def obtener_promociones():
    if not supabase:
        return {"success": True, "promociones": []}
    try:
        response = supabase.table("promociones").select("*").eq("activa", True).execute()
        return {"success": True, "promociones": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
