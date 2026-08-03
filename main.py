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
    version="12.0.0"
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
        .animate-scroll:hover { animation-play-state: paused; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0A1128; }
        ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #334155; }
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR Y GEOLOCALIZACIÓN -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 flex flex-col sm:flex-row justify-between items-center border-b border-slate-800/80 gap-2">
        <div class="flex items-center gap-2">
            <span>📍 Ubicación detectada:</span>
            <select id="citySelect" onchange="cambiarCiudad(this.value)" class="bg-[#0A1128] text-emerald-400 font-bold px-2 py-1 rounded border border-slate-700 focus:outline-none">
                <option value="Catamarca">Catamarca (Capital)</option>
                <option value="Valle Viejo">Valle Viejo</option>
                <option value="Fray Mamerto Esquiú">Fray Mamerto Esquiú</option>
            </select>
        </div>
        <div class="text-slate-300 font-medium">
            🌟 <span class="text-emerald-400 font-bold">Club de Descuentos:</span> Únete y obtén cobertura familiar de hasta <span class="text-orange-400 font-bold">$5.000.000</span>
        </div>
        <!-- Campanita de notificaciones -->
        <div class="relative">
            <button onclick="toggleNotificaciones()" class="bg-slate-800 hover:bg-slate-700 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 border border-slate-700 transition">
                <span>🔔</span> Ofertas <span id="badgeCount" class="bg-orange-500 text-slate-950 rounded-full px-1.5 py-0.2 text-[10px] font-black">3</span>
            </button>
            <div id="notifDropdown" class="hidden absolute right-0 mt-2 w-72 bg-[#101833] border border-slate-700 rounded-2xl shadow-2xl p-4 z-50 text-xs space-y-2">
                <p class="font-bold text-slate-200 border-b border-slate-800 pb-1">Últimas Ofertas Flash</p>
                <div class="p-2 bg-[#0A1128] rounded-xl border border-slate-800">🔥 20% OFF en Gastronomía local - ¡Válido hoy!</div>
                <div class="p-2 bg-[#0A1128] rounded-xl border border-slate-800">🛡️ Cobertura $5M activada para nuevos socios.</div>
            </div>
        </div>
    </div>

    <!-- HEADER / NAVBAR -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-3 cursor-pointer">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                    Max<span class="text-orange-500">%</span>Shop
                </div>
                <span class="hidden md:inline-block text-[10px] font-bold uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-md">
                    CLUB DE DESCUENTOS + ASISTENCIA
                </span>
            </div>
            <div class="flex items-center space-x-3">
                <a href="#comercios" class="text-xs font-bold text-slate-300 hover:text-white transition">Comercios</a>
                <a href="#planes" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs sm:text-sm px-5 py-3 rounded-xl transition shadow-lg shadow-orange-500/20 uppercase tracking-wider">
                    🛡️ Suscribirme ($5M)
                </a>
            </div>
        </div>
    </header>

    <!-- CARRUSEL DE MARCAS -->
    <div class="bg-[#070C1E] border-b border-slate-800/80 py-3 overflow-hidden relative shadow-inner">
        <div class="animate-scroll space-x-6 px-4 items-center text-xs font-bold tracking-wider text-slate-300 uppercase">
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span><span>FRÁVEGA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span>JUMBO</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span><span>MCDONALD'S</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>BANCO GALICIA</span></div>
            <!-- Loop -->
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span><span>FRÁVEGA</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span>JUMBO</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span><span>MCDONALD'S</span></div>
            <div class="flex items-center space-x-2 bg-[#101833] px-5 py-2.5 rounded-xl border border-slate-800"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>BANCO GALICIA</span></div>
        </div>
    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
        
        <!-- HERO -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-14 shadow-2xl overflow-hidden">
            <div class="relative z-10 max-w-2xl space-y-6">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase tracking-widest">
                    <span>🔥</span> <span>Entras por los Descuentos, te proteges con todo</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Club de Descuentos + Cobertura Total <span class="text-orange-500">$5.000.000</span>
                </h1>
                <p class="text-slate-300 text-base sm:text-lg leading-relaxed">
                    Navega por los comercios adheridos, aprovecha cupones exclusivos y obtén respaldo financiero integral ante emergencias extremas para toda la familia.
                </p>
                <div class="pt-2 flex flex-wrap gap-4">
                    <a href="#comercios" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-7 py-3.5 rounded-2xl transition text-sm uppercase tracking-wider shadow-lg">
                        Ver Comercios y Descuentos
                    </a>
                    <a href="#planes" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-7 py-3.5 rounded-2xl transition text-sm uppercase tracking-wider shadow-lg">
                        Suscribirme al Plan
                    </a>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DINÁMICA: REGISTRO DE COMERCIOS Y VITRINA DE PUBLICIDADES -->
        <div id="comercios" class="space-y-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-xl">
                <div>
                    <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase tracking-wider border border-emerald-500/20">Portal de Socios</span>
                    <h2 class="text-2xl font-black text-white mt-2">¿Tienes un negocio? Sube tu publicidad gratis</h2>
                    <p class="text-sm text-slate-400">Publica tus imágenes y ofertas en el club para atraer clientes locales al instante.</p>
                </div>
                <form onsubmit="registrarComercio(event)" class="w-full md:w-auto flex flex-col sm:flex-row gap-3">
                    <input type="text" id="nombreNegocio" required placeholder="Nombre de tu tienda" class="bg-[#0A1128] border border-slate-700 px-4 py-2.5 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                    <input type="text" id="ofertaNegocio" required placeholder="Ej: 25% OFF en efectivo" class="bg-[#0A1128] border border-slate-700 px-4 py-2.5 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                    <button type="submit" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-5 py-2.5 rounded-xl text-xs uppercase tracking-wider transition">Subir Publicidad</button>
                </form>
            </div>

            <!-- VITRINA / GRILLA DE PUBLICIDADES DE COMERCIOS -->
            <div class="space-y-4">
                <h3 class="text-xl font-bold text-white flex items-center gap-2">
                    <span>🛍️</span> Comercios y Publicidades Activas en la Red
                </h3>
                <div id="gridComercios" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    <!-- Ejemplo estático inicial que se alimenta dinámicamente -->
                    <div class="bg-[#101833] border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
                        <div class="h-36 bg-slate-800 rounded-2xl flex items-center justify-center text-slate-500 font-bold text-xs uppercase tracking-wider">Imagen Publicitaria</div>
                        <span class="text-[10px] font-bold text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-md">Gastronomía</span>
                        <h4 class="text-base font-bold text-white">Café & Bar Central</h4>
                        <p class="text-xs text-slate-400">20% de descuento abonando por transferencia o efectivo.</p>
                    </div>
                    <div class="bg-[#101833] border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
                        <div class="h-36 bg-slate-800 rounded-2xl flex items-center justify-center text-slate-500 font-bold text-xs uppercase tracking-wider">Imagen Publicitaria</div>
                        <span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md">Indumentaria</span>
                        <h4 class="text-base font-bold text-white">Moda Urbana Store</h4>
                        <p class="text-xs text-slate-400">3 cuotas sin interés + 15% off acumulable con el club.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DE PLANES Y SUSCRIPCIÓN CON MONTOS FIJOS DE MERCADO PAGO -->
        <div id="planes" class="space-y-8 pt-6">
            <div class="text-center max-w-xl mx-auto space-y-3">
                <span class="text-xs font-bold text-orange-400 uppercase tracking-widest bg-orange-500/10 px-3.5 py-1 rounded-full border border-orange-500/20">Planes Oficiales</span>
                <h2 class="text-3xl font-black text-white">Selecciona tu Cobertura y Suscríbete</h2>
                <p class="text-sm text-slate-400">Elige tu nivel de protección. El monto incluye la membresía al club y el respaldo familiar de hasta $5.000.000.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                <!-- Plan Esencial -->
                <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 flex flex-col justify-between shadow-xl">
                    <div class="space-y-4">
                        <span class="text-xs font-bold px-3 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">PLAN ESENCIAL</span>
                        <h3 class="text-xl font-bold text-white">Respaldo Personal</h3>
                        <div class="text-3xl font-black text-white">$5.000 <span class="text-xs text-slate-400 font-normal">/ mes</span></div>
                        <p class="text-xs text-slate-400 leading-relaxed">Asistencia de emergencia básica + Club de Descuentos total.</p>
                    </div>
                    <div class="pt-6 mt-6 border-t border-slate-800">
                        <a href="https://link.mercadopago.com.ar/tu-link-plan-esencial" target="_blank" class="block text-center py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition text-xs uppercase tracking-wider shadow-lg">
                            Suscribirme ($5.000)
                        </a>
                    </div>
                </div>

                <!-- Plan Familiar VIP ($5.000.000) -->
                <div class="bg-gradient-to-b from-[#1E2959] to-[#101833] border-2 border-orange-500 rounded-3xl p-6 flex flex-col justify-between shadow-2xl relative scale-105">
                    <div class="absolute -top-3 right-6 bg-orange-500 text-slate-950 font-black text-[10px] px-3 py-1 rounded-full uppercase tracking-wider">Recomendado</div>
                    <div class="space-y-4">
                        <span class="text-xs font-bold px-3 py-1 rounded-md bg-orange-500/10 text-orange-400 border border-orange-500/20">PLAN FAMILIAR VIP</span>
                        <h3 class="text-xl font-bold text-white">Cobertura Total $5M</h3>
                        <div class="text-3xl font-black text-white">$8.000 <span class="text-xs text-slate-400 font-normal">/ mes</span></div>
                        <p class="text-xs text-slate-300 leading-relaxed">Salud, vida, sepelio, hogar y vehículo. Casos extremos y de emergencia cubiertos para toda la familia + Club VIP.</p>
                    </div>
                    <div class="pt-6 mt-6 border-t border-slate-800">
                        <a href="https://link.mercadopago.com.ar/tu-link-plan-familiar" target="_blank" class="block text-center py-3.5 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black rounded-xl transition text-xs uppercase tracking-wider shadow-xl">
                            Suscribirme a los $5.000.000
                        </a>
                    </div>
                </div>

                <!-- Plan Comercial -->
                <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 flex flex-col justify-between shadow-xl">
                    <div class="space-y-4">
                        <span class="text-xs font-bold px-3 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">PLAN EMPRESARIAL</span>
                        <h3 class="text-xl font-bold text-white">Comercio Protegido</h3>
                        <div class="text-3xl font-black text-white">$15.000 <span class="text-xs text-slate-400 font-normal">/ mes</span></div>
                        <p class="text-xs text-slate-400 leading-relaxed">Cobertura comercial integral + Publicidad ilimitada destacada en la vitrina.</p>
                    </div>
                    <div class="pt-6 mt-6 border-t border-slate-800">
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

    <!-- JAVASCRIPT DE FUNCIONALIDAD -->
    <script>
        function toggleNotificaciones() {
            const drop = document.getElementById('notifDropdown');
            drop.classList.toggle('hidden');
        }

        function cambiarCiudad(ciudad) {
            alert('Zona actualizada a: ' + ciudad + '. Mostrando ofertas y comercios locales.');
        }

        function registrarComercio(e) {
            e.preventDefault();
            const nombre = document.getElementById('nombreNegocio').value;
            const oferta = document.getElementById('ofertaNegocio').value;
            const grid = document.getElementById('gridComercios');

            const card = document.createElement('div');
            card.className = "bg-[#101833] border border-emerald-500/50 rounded-3xl p-5 space-y-3 shadow-2xl animate-pulse";
            card.innerHTML = `
                <div class="h-36 bg-slate-800 rounded-2xl flex items-center justify-center text-emerald-400 font-bold text-xs uppercase tracking-wider">Nueva Publicidad</div>
                <span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md">Local Adherido</span>
                <h4 class="text-base font-bold text-white">${nombre}</h4>
                <p class="text-xs text-slate-300">${oferta}</p>
            `;
            grid.prepend(card);
            alert('¡Publicidad subida con éxito y publicada en la vitrina del club!');
            e.target.reset();
        }
    </script>
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
            <a href="/" class="inline-block px-4 py-2 bg-slate-800 text-xs rounded-xl font-bold">Volver al Sitio Principal</a>
        </div>
    </body>
    </html>
    """

@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger = GeolocationTrigger()):
    return {"status": "success", "message": f"Pipeline ejecutado para {payload.city}"}
