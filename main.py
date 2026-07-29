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
    title="Max%Shop - Descuentos de Locos",
    version="8.0.0"
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
    <title>Max%Shop - Descuentos de Locos</title>
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
        /* Scrollbar personalizado limpio */
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
    <div class="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-xs py-2 px-4 text-center font-medium border-b border-slate-800 tracking-wide">
        ⚡ <span class="text-emerald-400 font-bold">Radar Activo:</span> Detectando descuentos automáticos vinculados a tus tarjetas en Catamarca y región.
    </div>

    <!-- HEADER / NAVBAR PRINCIPAL (ESTILO E-COMMERCE PREMIUM) -->
    <header class="sticky top-0 z-50 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            
            <!-- LOGOTIPO OFICIAL -->
            <div class="flex items-center space-x-3 cursor-pointer">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                    Max<span class="text-orange-500">%</span>Shop
                </div>
                <span class="hidden md:inline-block text-[10px] font-bold uppercase tracking-widest bg-orange-500/10 text-orange-400 border border-orange-500/20 px-2 py-0.5 rounded-md">
                    PRO
                </span>
            </div>

            <!-- BUSCADOR INTELIGENTE CENTRAL -->
            <div class="flex-1 max-w-xl hidden md:block">
                <div class="relative">
                    <input type="text" placeholder="Busca tiendas, marcas (ej. Frávega, Jumbo) o tarjetas..." class="w-full bg-[#131B36] border border-slate-700/80 rounded-xl px-4 py-2.5 pl-11 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-orange-500 transition shadow-inner">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        🔍
                    </div>
                </div>
            </div>

            <!-- BOTONES DE ACCIÓN RÁPIDA -->
            <div class="flex items-center space-x-3">
                <a href="#radar" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs sm:text-sm px-4 py-2.5 rounded-xl transition shadow-lg shadow-emerald-500/20 flex items-center gap-2">
                    <span>⚡</span> <span>Activar Radar</span>
                </a>
            </div>
        </div>
    </header>

    <!-- CARRUSEL INFINITO DE MARCAS Y TIENDAS REALES -->
    <div class="bg-[#070C1E] border-b border-slate-800/80 py-3 overflow-hidden relative shadow-inner">
        <div class="absolute left-0 inset-y-0 w-24 bg-gradient-to-r from-[#070C1E] to-transparent z-10 pointer-events-none"></div>
        <div class="absolute right-0 inset-y-0 w-24 bg-gradient-to-l from-[#070C1E] to-transparent z-10 pointer-events-none"></div>
        
        <div class="animate-scroll space-x-6 px-4 items-center text-xs font-bold tracking-wider text-slate-300 uppercase">
            <!-- Bloque de marcas reales -->
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                <span>FRÁVEGA</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <span>JUMBO</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <span>MCDONALD'S</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                <span>BANCO GALICIA</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
                <span>VISA REWARDS</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>
                <span>YPF SERVI CLUB</span>
            </div>
            <!-- Duplicado para loop fluido -->
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                <span>FRÁVEGA</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <span>JUMBO</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <span>MCDONALD'S</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                <span>BANCO GALICIA</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
                <span>VISA REWARDS</span>
            </div>
            <div class="flex items-center space-x-2 bg-[#101833] hover:bg-[#162042] transition px-5 py-2.5 rounded-xl border border-slate-800 cursor-pointer shadow-sm">
                <span class="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>
                <span>YPF SERVI CLUB</span>
            </div>
        </div>
    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
        
        <!-- HERO BANNER DE ALTO IMPACTO (ESTILO RETAIL PREMIUM) -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-14 overflow-hidden shadow-2xl">
            <div class="absolute right-0 top-0 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="absolute left-1/3 bottom-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
            
            <div class="relative z-10 max-w-2xl space-y-6">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase tracking-widest">
                    <span>🔥</span> <span>Descuentos de Locos</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    El poder de ahorrar <span class="text-orange-500">sin límites</span>
                </h1>
                <p class="text-slate-300 text-base sm:text-lg leading-relaxed">
                    Conecta tus tarjetas de crédito y débito de forma segura. Nuestro radar detecta automáticamente los mejores beneficios activos en comercios y tiendas cercanas.
                </p>
                <div class="pt-2 flex flex-wrap gap-4">
                    <a href="#radar" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 hover:to-amber-400 text-slate-950 font-black px-8 py-4 rounded-2xl transition shadow-xl shadow-orange-500/20 text-sm uppercase tracking-wider">
                        Consultar Mis Ofertas
                    </a>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DE OFERTAS Y TARJETAS DESTACADAS (GRILLA ESTILO E-COMMERCE) -->
        <div class="space-y-6">
            <div class="flex justify-between items-end">
                <div>
                    <h2 class="text-2xl font-black text-white">Promociones Destacadas Hoy</h2>
                    <p class="text-sm text-slate-400">Actualizado al instante según tus medios de pago registrados.</p>
                </div>
                <span class="text-xs text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-lg">
                    Ver Todos (24)
                </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- Tarjeta 1 -->
                <div class="bg-[#101833] border border-slate-800/80 hover:border-orange-500/50 rounded-2xl p-5 transition group flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">FRÁVEGA</span>
                            <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded">35% OFF</span>
                        </div>
                        <h3 class="font-bold text-white group-hover:text-orange-400 transition text-base">Electro & Tecnología</h3>
                        <p class="text-xs text-slate-400">Hasta 12 cuotas sin interés pagando con tarjetas seleccionadas.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 flex justify-between items-center text-xs">
                        <span class="text-slate-400">Vence hoy</span>
                        <span class="font-bold text-emerald-400">Match Automático</span>
                    </div>
                </div>

                <!-- Tarjeta 2 -->
                <div class="bg-[#101833] border border-slate-800/80 hover:border-orange-500/50 rounded-2xl p-5 transition group flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">JUMBO</span>
                            <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded">25% OFF</span>
                        </div>
                        <h3 class="font-bold text-white group-hover:text-orange-400 transition text-base">Supermercados & Hogar</h3>
                        <p class="text-xs text-slate-400">Descuento directo en caja aplicable con tus tarjetas adheridas.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 flex justify-between items-center text-xs">
                        <span class="text-slate-400">Vence en 3 días</span>
                        <span class="font-bold text-emerald-400">Match Automático</span>
                    </div>
                </div>

                <!-- Tarjeta 3 -->
                <div class="bg-[#101833] border border-slate-800/80 hover:border-orange-500/50 rounded-2xl p-5 transition group flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">MCDONALD'S</span>
                            <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded">2x1 APP</span>
                        </div>
                        <h3 class="font-bold text-white group-hover:text-orange-400 transition text-base">Gastronomía & Fast Food</h3>
                        <p class="text-xs text-slate-400">Beneficios exclusivos en combos seleccionados todos los martes.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 flex justify-between items-center text-xs">
                        <span class="text-slate-400">Exclusivo socios</span>
                        <span class="font-bold text-emerald-400">Match Automático</span>
                    </div>
                </div>

                <!-- Tarjeta 4 -->
                <div class="bg-[#101833] border border-slate-800/80 hover:border-orange-500/50 rounded-2xl p-5 transition group flex flex-col justify-between shadow-lg">
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-bold px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 border border-red-500/20">GALICIA</span>
                            <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded">40% OFF</span>
                        </div>
                        <h3 class="font-bold text-white group-hover:text-orange-400 transition text-base">Especial Tarjetas Visa</h3>
                        <p class="text-xs text-slate-400">Reintegro inmediato en comercios adheridos de indumentaria.</p>
                    </div>
                    <div class="pt-5 mt-4 border-t border-slate-800 flex justify-between items-center text-xs">
                        <span class="text-slate-400">Tope $15.000</span>
                        <span class="font-bold text-emerald-400">Match Automático</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DE CONSULTA / RADAR DE BENEFICIOS (INTERACTIVA) -->
        <div id="radar" class="max-w-2xl mx-auto bg-gradient-to-b from-[#131E3E] to-[#0D152D] border border-orange-500/30 rounded-3xl p-8 md:p-10 shadow-2xl relative">
            <div class="absolute -top-3 right-8 bg-gradient-to-r from-orange-500 to-amber-500 text-slate-950 font-black text-xs px-3.5 py-1 rounded-full uppercase tracking-wider shadow-md">
                Radar Inteligente
            </div>
            
            <h3 class="text-2xl font-black mb-2 text-white flex items-center">
                <span class="text-orange-500 mr-3 text-3xl">⚡</span> Consulta tus Ofertas Activas
            </h3>
            <p class="text-slate-300 text-sm mb-8">Ingresa tu correo electrónico para sincronizar de forma automática tus tarjetas y consultar los beneficios vigentes en tu zona.</p>
            
            <form onsubmit="alert('¡Sincronización exitosa! Revisa tu correo para ver tus ofertas activas.'); event.preventDefault();" class="space-y-5">
                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Correo Electrónico</label>
                    <input type="email" required placeholder="tucorreo@ejemplo.com" class="w-full px-5 py-4 bg-[#0A1128] border border-slate-700 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-orange-500 transition text-base shadow-inner">
                </div>
                <button type="submit" class="w-full py-4 bg-gradient-to-r from-orange-500 via-amber-500 to-orange-400 hover:from-orange-400 hover:to-amber-400 text-slate-950 font-black rounded-2xl transition shadow-xl shadow-orange-500/20 text-base uppercase tracking-wider">
                    Ver Mis Descuentos Activos
                </button>
            </form>
        </div>

        <!-- BLOQUES DE CARACTERÍSTICAS (BENEFICIOS DE LA PLATAFORMA) -->
        <div class="grid md:grid-cols-3 gap-6 pt-6">
            <div class="bg-[#101833]/60 border border-slate-800/80 p-7 rounded-2xl">
                <div class="text-orange-500 font-bold text-lg mb-2">💎 Alianzas Exclusivas</div>
                <p class="text-slate-400 text-sm leading-relaxed">Convenios directos con las tiendas y marcas más importantes del país para garantizarte ahorros reales.</p>
            </div>
            <div class="bg-[#101833]/60 border border-slate-800/80 p-7 rounded-2xl">
                <div class="text-orange-500 font-bold text-lg mb-2">🛡️ Cero Fricción</div>
                <p class="text-slate-400 text-sm leading-relaxed">Olvídate de cupones impresos. El sistema detecta y aplica tu medio de pago automáticamente.</p>
            </div>
            <div class="bg-[#101833]/60 border border-slate-800/80 p-7 rounded-2xl">
                <div class="text-orange-500 font-bold text-lg mb-2">🚀 Geolocalización Pro</div>
                <p class="text-slate-400 text-sm leading-relaxed">Radar permanente que te avisa por notificaciones qué locales cercanos tienen ofertas listas para ti.</p>
            </div>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800/80 bg-[#070C1E] mt-24 py-12 text-center text-xs text-slate-400 space-y-3">
        <p class="font-bold text-slate-300 text-sm">Max%Shop &copy; 2026 - Todos los derechos reservados.</p>
        <p>Plataforma inteligente de beneficios, descuentos y optimización de compras de alto impacto.</p>
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

