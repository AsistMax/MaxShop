from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Max%Shop - Club de Beneficios y Protección",
    version="9.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeolocationTrigger(BaseModel):
    city: str = "Catamarca"

@app.get("/", response_class=HTMLResponse)
async def client_landing():
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Club de Beneficios y Protección</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        .animate-scroll {
            display: flex;
            width: max-content;
            animation: scroll 35s linear infinite;
        }
        .animate-scroll:hover {
            animation-play-state: paused;
        }
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0A1128;
        }
        ::-webkit-scrollbar-thumb {
            background: #1E293B;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR DE ALERTA / BENEFICIO GLOBAL -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 text-center font-medium border-b border-slate-800/80 tracking-wide">
        🛡️ <span class="text-emerald-400 font-bold">Protección Activa:</span> Cobertura de emergencia por $5.000.000 + Club de Ahorro por solo $2.000/mes.
    </div>

    <!-- HEADER / NAVBAR PRINCIPAL -->
    <header class="sticky top-0 z-50 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            
            <div class="flex items-center space-x-3 cursor-pointer">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                    Max<span class="text-orange-500">%</span>Shop
                </div>
                <span class="hidden md:inline-block text-[10px] font-bold uppercase tracking-widest bg-orange-500/10 text-orange-400 border border-orange-500/20 px-2 py-0.5 rounded-md">
                    CLUB VIP
                </span>
            </div>

            <div class="flex-1 max-w-xl hidden md:block">
                <div class="relative">
                    <input type="text" placeholder="Busca tiendas, marcas (ej. Frávega, Jumbo) o asistencias..." class="w-full bg-[#131B36] border border-slate-700/80 rounded-xl px-4 py-2.5 pl-11 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-orange-500 transition shadow-inner">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        🔍
                    </div>
                </div>
            </div>

            <div class="flex items-center space-x-3">
                <a href="#suscripcion" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 hover:to-amber-400 text-slate-950 font-black text-xs sm:text-sm px-5 py-3 rounded-xl transition shadow-lg shadow-orange-500/20 flex items-center gap-2 uppercase tracking-wider">
                    <span>⚡</span> <span>Unirme por $2.000</span>
                </a>
            </div>
        </div>
    </header>

    <!-- CARRUSEL INFINITO DE MARCAS Y TIENDAS -->
    <div class="bg-[#070C1E] border-b border-slate-800/80 py-3 overflow-hidden relative shadow-inner">
        <div class="absolute left-0 inset-y-0 w-24 bg-gradient-to-r from-[#070C1E] to-transparent z-10 pointer-events-none"></div>
        <div class="absolute right-0 inset-y-0 w-24 bg-gradient-to-l from-[#070C1E] to-transparent z-10 pointer-events-none"></div>
        
        <div class="animate-scroll space-x-6 px-4 items-center text-xs font-bold tracking-wider text-slate-300 uppercase">
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span><span>FRÁVEGA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span>JUMBO</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span><span>MCDONALD'S</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>BANCO GALICIA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span><span>VISA REWARDS</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-indigo-500"></span><span>YPF SERVI CLUB</span></div>
            <!-- Duplicado loop -->
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span><span>FRÁVEGA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span>JUMBO</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span><span>MCDONALD'S</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>BANCO GALICIA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span><span>VISA REWARDS</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-indigo-500"></span><span>YPF SERVI CLUB</span></div>
        </div>
    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
        
        <!-- HERO BANNER DE ALTO IMPACTO -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-14 overflow-hidden shadow-2xl">
            <div class="absolute right-0 top-0 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="absolute left-1/3 bottom-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
            
            <div class="relative z-10 max-w-2xl space-y-6">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase tracking-widest">
                    <span>🛡️</span> <span>Seguro Financiero de Emergencia + Club VIP</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Protección de <span class="text-orange-500">$5.000.000</span> por $2.000/mes
                </h1>
                <p class="text-slate-300 text-base sm:text-lg leading-relaxed">
                    Respaldo absoluto ante cualquier emergencia de alta complejidad (vehículo, salud, vida, hogar) más el acceso automático a la red de descuentos de locos en tus marcas favoritas.
                </p>
                <div class="pt-2 flex flex-wrap gap-4">
                    <a href="#suscripcion" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 hover:to-amber-400 text-slate-950 font-black px-8 py-4 rounded-2xl transition shadow-xl shadow-orange-500/20 text-sm uppercase tracking-wider">
                        Activar Mi Membresía Ahora
                    </a>
                </div>
            </div>
        </div>

        <!-- GRILLA DE OFERTAS Y BENEFICIOS -->
        <div class="space-y-6">
            <div class="flex justify-between items-end">
                <div>
                    <h2 class="text-2xl font-black text-white">Beneficios del Club Incluidos</h2>
                    <p class="text-sm text-slate-400">Todo en una sola suscripción sin fricciones ni trámites engorrosos.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="bg-[#101833] border border-slate-800/80 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">SALUD & VIDA</span>
                        <h3 class="font-bold text-white text-base">Emergencias Médicas</h3>
                        <p class="text-xs text-slate-400">Cobertura de alta complejidad ante imprevistos graves familiares.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 text-xs font-bold text-emerald-400">Incluido en Plan $2.000</div>
                </div>

                <div class="bg-[#101833] border border-slate-800/80 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">VEHÍCULO</span>
                        <h3 class="font-bold text-white text-base">Asistencia en Ruta</h3>
                        <p class="text-xs text-slate-400">Auxilio mecánico y remolque ilimitado en todo el territorio nacional.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 text-xs font-bold text-emerald-400">Incluido en Plan $2.000</div>
                </div>

                <div class="bg-[#101833] border border-slate-800/80 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">HOGAR</span>
                        <h3 class="font-bold text-white text-base">Urgencias Domésticas</h3>
                        <p class="text-xs text-slate-400">Plomería, cerrajería y electricidad de emergencia garantizada.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 text-xs font-bold text-emerald-400">Incluido en Plan $2.000</div>
                </div>

                <div class="bg-[#101833] border border-slate-800/80 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-orange-500/10 text-orange-400 border border-orange-500/20">AHORRO COMERCIAL</span>
                        <h3 class="font-bold text-white text-base">Descuentos de Locos</h3>
                        <p class="text-xs text-slate-400">Match automático con Frávega, Jumbo, McDonald's y más.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 text-xs font-bold text-emerald-400">Match Automático</div>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DE SUSCRIPCIÓN EN 2 PASOS (ENLACE A LA APP DE ASISTENCIA) -->
        <div id="suscripcion" class="max-w-2xl mx-auto bg-gradient-to-b from-[#131E3E] to-[#0D152D] border border-orange-500/40 rounded-3xl p-8 md:p-10 shadow-2xl relative">
            <div class="absolute -top-3 right-8 bg-gradient-to-r from-orange-500 to-amber-500 text-slate-950 font-black text-xs px-3.5 py-1 rounded-full uppercase tracking-wider shadow-md">
                Paso 1 y 2 Automático
            </div>
            
            <h3 class="text-2xl font-black mb-2 text-white flex items-center">
                <span class="text-orange-500 mr-3 text-3xl">⚡</span> Suscripción Inmediata ($2.000/mes)
            </h3>
            <p class="text-slate-300 text-sm mb-8">Ingresa tus datos para registrar tu póliza de $5.000.000 en nuestra app de asistencia financiera y generar tu contrato al instante.</p>
            
            <!-- Formulario con redirección directa a tu app de asistencia financiera externa -->
            <form action="https://app.tuasistenciafinanciera.com/suscripcion" method="GET" class="space-y-5">
                <!-- Parámetros ocultos que envían el plan y monto exacto a tu app hermana -->
                <input type="hidden" name="plan" value="poliza_emergencia_5m">
                <input type="hidden" name="monto" value="2000">
                
                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Correo Electrónico de Registro</label>
                    <input type="email" name="email" required placeholder="tucorreo@ejemplo.com" class="w-full px-5 py-4 bg-[#0A1128] border border-slate-700 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-orange-500 transition text-base shadow-inner">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">WhatsApp de Contacto (Para la Póliza)</label>
                    <input type="tel" name="whatsapp" required placeholder="+54 9 ..." class="w-full px-5 py-4 bg-[#0A1128] border border-slate-700 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-orange-500 transition text-base shadow-inner">
                </div>
                <button type="submit" class="w-full py-4 bg-gradient-to-r from-orange-500 via-amber-500 to-orange-400 hover:from-orange-400 hover:to-amber-400 text-slate-950 font-black rounded-2xl transition shadow-xl shadow-orange-500/20 text-base uppercase tracking-wider cursor-pointer">
                    Confirmar y Generar Contrato (Paso 2)
                </button>
            </form>
            <p class="text-[11px] text-slate-400 text-center mt-4">Al hacer clic, serás dirigido de forma segura a nuestra plataforma de cobro y emisión de pólizas.</p>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800/80 bg-[#070C1E] mt-24 py-12 text-center text-xs text-slate-400 space-y-3">
        <p class="font-bold text-slate-300 text-sm">Max%Shop &copy; 2026 - Todos los derechos reservados.</p>
        <p>Ecosistema integrado de descuentos inteligentes y asistencia financiera de alta complejidad.</p>
    </footer>

</body>
</html>
"""

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-white p-8 font-sans">
        <div class="max-w-4xl mx-auto space-y-6">
            <h1 class="text-2xl font-bold text-orange-500">Panel Interno de Administración</h1>
            <p class="text-slate-400 text-sm">Área exclusiva para control de base de datos, APIs y motores de geolocalización.</p>
            <a href="/" class="inline-block px-4 py-2 bg-slate-800 text-xs rounded-xl font-bold">Volver al Sitio Principal</a>
        </div>
    </body>
    </html>
    """

@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger = GeolocationTrigger()):
    return {"status": "success", "message": f"Pipeline ejecutado para {payload.city}"}
