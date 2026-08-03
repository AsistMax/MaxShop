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
    title="Max%Shop - Club de Beneficios y Cobertura Total",
    version="11.0.0"
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
    <title>Max%Shop - Club de Beneficios y Cobertura Total</title>
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
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0A1128; }
        ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #334155; }
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR DE ALERTA -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 text-center font-medium border-b border-slate-800/80 tracking-wide">
        🌟 <span class="text-emerald-400 font-bold">Club de Beneficios Activo:</span> Suscríbete a un plan de asistencia y obtén cobertura familiar inmediata.
    </div>

    <!-- HEADER -->
    <header class="sticky top-0 z-50 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-3 cursor-pointer">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                    Max<span class="text-orange-500">%</span>Shop
                </div>
                <span class="hidden md:inline-block text-[10px] font-bold uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-md">
                    CLUB VIP + ASISTENCIA
                </span>
            </div>

            <div class="flex items-center space-x-3">
                <a href="#planes" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs sm:text-sm px-5 py-3 rounded-xl transition shadow-lg shadow-orange-500/20 flex items-center gap-2 uppercase tracking-wider">
                    <span>🛡️</span> <span>Elegir Plan</span>
                </a>
            </div>
        </div>
    </header>

    <!-- CARRUSEL DE MARCAS -->
    <div class="bg-[#070C1E] border-b border-slate-800/80 py-3 overflow-hidden relative shadow-inner">
        <div class="absolute left-0 inset-y-0 w-24 bg-gradient-to-r from-[#070C1E] to-transparent z-10 pointer-events-none"></div>
        <div class="absolute right-0 inset-y-0 w-24 bg-gradient-to-l from-[#070C1E] to-transparent z-10 pointer-events-none"></div>
        
        <div class="animate-scroll space-x-6 px-4 items-center text-xs font-bold tracking-wider text-slate-300 uppercase">
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span><span>FRÁVEGA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span>JUMBO</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span><span>MCDONALD'S</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>BANCO GALICIA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span><span>VISA REWARDS</span></div>
            <!-- Loop -->
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span><span>FRÁVEGA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span>JUMBO</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span><span>MCDONALD'S</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>BANCO GALICIA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800 shadow-sm"><span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span><span>VISA REWARDS</span></div>
        </div>
    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
        
        <!-- HERO BANNER -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-14 overflow-hidden shadow-2xl">
            <div class="absolute right-0 top-0 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="absolute left-1/3 bottom-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
            
            <div class="relative z-10 max-w-2xl space-y-6">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase tracking-widest">
                    <span>🔥</span> <span>Asistencia Financiera + Club de Beneficios Gratis</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Protección Familiar con <span class="text-orange-500">Cobertura Total</span>
                </h1>
                <p class="text-slate-300 text-base sm:text-lg leading-relaxed">
                    Elige el plan de asistencia que se adapte a tus necesidades. Incluye respaldo ante emergencias extremas (salud, vida, sepelio, hogar, vehículo) para toda la familia y acceso total al club de descuentos.
                </p>
                <div class="pt-2 flex flex-wrap gap-4">
                    <a href="#planes" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-8 py-4 rounded-2xl transition shadow-xl shadow-orange-500/20 text-sm uppercase tracking-wider">
                        Ver Planes Disponibles
                    </a>
                </div>
            </div>
        </div>

        <!-- ZONA DE COMERCIOS: REGISTRO GRATIS -->
        <div class="bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-xl space-y-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-slate-800">
                <div>
                    <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase tracking-wider border border-emerald-500/20">Alianzas Comerciales</span>
                    <h2 class="text-2xl font-black text-white mt-2">¿Tienes un negocio? Sube tu publicidad gratis</h2>
                    <p class="text-sm text-slate-400">Publica tus ofertas en nuestro club de beneficios y potencia tus ventas al instante.</p>
                </div>
                <a href="#planes" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-5 py-3 rounded-xl text-xs uppercase tracking-wider transition shadow-lg shrink-0">
                    Sumarme al Club y Proteger mi Negocio
                </a>
            </div>

            <form onsubmit="alert('¡Publicidad enviada con éxito! Quedará visible en el club de beneficios de forma gratuita.'); event.preventDefault();" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input type="text" required placeholder="Nombre del Comercio / Tienda" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                <input type="text" required placeholder="Beneficio o Descuento (Ej: 20% OFF)" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                <div class="flex gap-2">
                    <input type="file" required class="bg-[#0A1128] border border-slate-700 px-3 py-2 rounded-xl text-xs text-slate-400 file:mr-2 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-white w-full">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-5 py-3 rounded-xl text-xs uppercase transition shrink-0">Publicar Gratis</button>
                </div>
            </form>
        </div>

        <!-- SECCIÓN DE PLANES Y SUSCRIPCIÓN CON MONTOS FIJOS DE MERCADO PAGO -->
        <div id="planes" class="space-y-8 pt-4">
            <div class="text-center max-w-xl mx-auto space-y-3">
                <span class="text-xs font-bold text-orange-400 uppercase tracking-widest bg-orange-500/10 px-3.5 py-1 rounded-full border border-orange-500/20">Planes Oficiales de Asistencia</span>
                <h2 class="text-3xl font-black text-white">Selecciona tu Cobertura y Regístrate</h2>
                <p class="text-sm text-slate-400">Al elegir tu plan, el sistema te redirigirá al link de pago seguro con el monto exacto integrado de la cobertura + el club de beneficios.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                <!-- Plan Esencial -->
                <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 flex flex-col justify-between shadow-xl">
                    <div class="space-y-4">
                        <span class="text-xs font-bold px-3 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">PLAN ESENCIAL</span>
                        <h3 class="text-xl font-bold text-white">Respaldo Personal</h3>
                        <div class="text-3xl font-black text-white">$5.000 <span class="text-xs text-slate-400 font-normal">/ mes</span></div>
                        <p class="text-xs text-slate-400 leading-relaxed">Cobertura de emergencia esencial + Acceso completo al Club de Descuentos.</p>
                    </div>
                    <div class="pt-6 mt-6 border-t border-slate-800">
                        <!-- LINK FIJO DE MERCADO PAGO PARA ESTE PLAN (Reemplaza con tu link real de $5.000) -->
                        <a href="https://link.mercadopago.com.ar/tu-link-plan-esencial" target="_blank" class="block text-center py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition text-xs uppercase tracking-wider shadow-lg">
                            Suscribirme ($5.000)
                        </a>
                    </div>
                </div>

                <!-- Plan Familiar VIP (El Destacado de $5.000.000) -->
                <div class="bg-gradient-to-b from-[#1E2959] to-[#101833] border-2 border-orange-500 rounded-3xl p-6 flex flex-col justify-between shadow-2xl relative scale-105">
                    <div class="absolute -top-3 right-6 bg-orange-500 text-slate-950 font-black text-[10px] px-3 py-1 rounded-full uppercase tracking-wider">Recomendado</div>
                    <div class="space-y-4">
                        <span class="text-xs font-bold px-3 py-1 rounded-md bg-orange-500/10 text-orange-400 border border-orange-500/20">PLAN FAMILIAR VIP</span>
                        <h3 class="text-xl font-bold text-white">Cobertura Total $5M</h3>
                        <div class="text-3xl font-black text-white">$8.000 <span class="text-xs text-slate-400 font-normal">/ mes</span></div>
                        <p class="text-xs text-slate-300 leading-relaxed">Salud, vida, sepelio, hogar y vehículo. Casos extremos y de emergencia cubiertos para toda la familia + Club VIP.</p>
                    </div>
                    <div class="pt-6 mt-6 border-t border-slate-800">
                        <!-- LINK FIJO DE MERCADO PAGO PARA ESTE PLAN (Reemplaza con tu link real de $8.000) -->
                        <a href="https://link.mercadopago.com.ar/tu-link-plan-familiar" target="_blank" class="block text-center py-3.5 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black rounded-xl transition text-xs uppercase tracking-wider shadow-xl">
                            Suscribirme a los $5.000.000
                        </a>
                    </div>
                </div>

                <!-- Plan Empresarial -->
                <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 flex flex-col justify-between shadow-xl">
                    <div class="space-y-4">
                        <span class="text-xs font-bold px-3 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">PLAN EMPRESARIAL</span>
                        <h3 class="text-xl font-bold text-white">Comercio Protegido</h3>
                        <div class="text-3xl font-black text-white">$15.000 <span class="text-xs text-slate-400 font-normal">/ mes</span></div>
                        <p class="text-xs text-slate-400 leading-relaxed">Cobertura comercial integral + Publicidad ilimitada destacada en el portal de descuentos.</p>
                    </div>
                    <div class="pt-6 mt-6 border-t border-slate-800">
                        <!-- LINK FIJO DE MERCADO PAGO PARA ESTE PLAN (Reemplaza con tu link real de $15.000) -->
                        <a href="https://link.mercadopago.com.ar/tu-link-plan-comercial" target="_blank" class="block text-center py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl transition text-xs uppercase tracking-wider shadow-lg">
                            Suscribirme Comercial
                        </a>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800/80 bg-[#070C1E] mt-24 py-12 text-center text-xs text-slate-400 space-y-3">
        <p class="font-bold text-slate-300 text-sm">Max%Shop &copy; 2026 - Todos los derechos reservados.</p>
        <p>Ecosistema de descuentos inteligentes y asistencia financiera de alta complejidad.</p>
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
            <p class="text-slate-400 text-sm">Área exclusiva para control de base de datos y validación de comercios.</p>
            <a href="/" class="inline-block px-4 py-2 bg-slate-800 text-xs rounded-xl font-bold">Volver al Sitio Principal</a>
        </div>
    </body>
    </html>
    """

@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger = GeolocationTrigger()):
    return {"status": "success", "message": f"Pipeline ejecutado para {payload.city}"}
