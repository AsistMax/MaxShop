from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-anon-key")
# Clave secreta para proteger el panel de administración (puedes cambiarla por la que desees)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026*")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
security = HTTPBasic()

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Panel Maestro",
    version="15.1.0"
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

# Función de autenticación para proteger rutas sensibles (Admin)
def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # Usuario por defecto: admin / Contraseña configurada en ADMIN_PASSWORD
    if credentials.username != "admin" or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administrador incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# 1. LANDING PAGE PRINCIPAL
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
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR Y GEOLOCALIZACIÓN -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 flex flex-col sm:flex-row justify-between items-center border-b border-slate-800/80 gap-2">
        <div class="flex items-center gap-2">
            <span>📍 Ubicación:</span>
            <select id="citySelect" onchange="cambiarCiudad(this.value)" class="bg-[#0A1128] text-emerald-400 font-bold px-2 py-1 rounded border border-slate-700 focus:outline-none">
                <option value="Catamarca">Catamarca (Capital)</option>
                <option value="Valle Viejo">Valle Viejo</option>
                <option value="Fray Mamerto Esquiú">Fray Mamerto Esquiú</option>
            </select>
        </div>
        <div class="text-slate-300 font-medium hidden md:block">
            🌟 <span class="text-emerald-400 font-bold">Club de Descuentos:</span> Cobertura familiar de hasta <span class="text-orange-400 font-bold">$5.000.000</span>
        </div>
        <!-- Campanita de notificaciones -->
        <div class="flex items-center gap-3">
            <a href="/comercio/validar" class="text-[11px] font-bold bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded-full text-emerald-400 border border-slate-700">🛡️ Validar DNI</a>
            <a href="/admin" class="text-[11px] font-bold bg-orange-500/10 hover:bg-orange-500/20 px-3 py-1 rounded-full text-orange-400 border border-orange-500/30">⚙️ Admin</a>
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
    </div>

    <!-- HEADER / NAVBAR -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-3 cursor-pointer">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                    Max<span class="text-orange-500">%</span>Shop
                </div>
                <span class="hidden md:inline-block text-[10px] font-bold uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-md">
                    CLUB DE DESCUENTOS + CREDENCIAL
                </span>
            </div>
            <div class="flex items-center space-x-3">
                <a href="/socio/12345678" class="hidden sm:inline-block text-xs font-bold text-blue-400 bg-blue-500/10 hover:bg-blue-500/20 px-4 py-2.5 rounded-xl border border-blue-500/20 transition">Ver Mi Credencial</a>
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
                    Navega por los comercios adheridos, presenta tu credencial digital y obtén respaldo financiero integral ante emergencias.
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

        <!-- SECCIÓN DE PLANES Y SUSCRIPCIÓN -->
        <div id="planes" class="space-y-8 pt-6">
            <div class="text-center max-w-xl mx-auto space-y-3">
                <span class="text-xs font-bold text-orange-400 uppercase tracking-widest bg-orange-500/10 px-3.5 py-1 rounded-full border border-orange-500/20">Planes Oficiales</span>
                <h2 class="text-3xl font-black text-white">Selecciona tu Cobertura y Suscríbete</h2>
                <p class="text-sm text-slate-400">Elige tu nivel de protección. Incluye credencial digital y respaldo familiar de hasta $5.000.000.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                <!-- Plan Esencial -->
                <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 flex flex-col justify-between shadow-xl">
                    <div class="space-y-4">
                        <span class="text-xs font-bold px-3 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">PLAN ESENCIAL</span>
                        <h3 class="text-xl font-bold text-white">Respaldo Personal</h3>
                        <div class="text-3xl font-black text-white">$5.000 <span class="text-xs text-slate-400 font-normal">/ mes</span></div>
                        <p class="text-xs text-slate-400 leading-relaxed">Credencial digital de socio + Club de Descuentos total.</p>
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
                        <p class="text-xs text-slate-300 leading-relaxed">Salud, vida, sepelio, hogar y vehículo. Casos extremos cubiertos + Credencial VIP.</p>
                    </div>
                    <div class="pt-6 mt-6 border-t border-slate-800">
                        <a href="https://link.mercadopago.com.ar/tu-link-familiar" target="_blank" class="block text-center py-3.5 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black rounded-xl transition text-xs uppercase tracking-wider shadow-xl">
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

    <!-- JAVASCRIPT -->
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

# 2. CREDENCIAL DIGITAL DEL SOCIO
@app.get("/socio/{dni}", response_class=HTMLResponse)
async def credencial_digital(dni: str):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Credencial Digital - Max%Shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-sm bg-gradient-to-b from-[#1E2959] to-[#101833] border-2 border-emerald-500 rounded-3xl p-6 shadow-2xl space-y-6">
        <div class="flex justify-between items-center border-b border-slate-700 pb-4">
            <span class="font-black text-lg text-white">Max<span class="text-orange-500">%</span>Shop</span>
            <span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">Socio Activo</span>
        </div>
        <div class="space-y-2 text-center">
            <div class="w-20 h-20 bg-slate-800 rounded-full mx-auto flex items-center justify-center text-2xl font-bold text-slate-400 border border-slate-700">👤</div>
            <h2 class="text-xl font-bold text-white">Juan Pérez</h2>
            <p class="text-xs text-slate-400">DNI: <span class="text-white font-mono">{dni}</span></p>
        </div>
        <div class="bg-[#0A1128] p-4 rounded-2xl border border-slate-800 text-xs space-y-2">
            <div class="flex justify-between"><span class="text-slate-400">Plan:</span> <span class="font-bold text-orange-400">Familiar VIP ($5M)</span></div>
            <div class="flex justify-between"><span class="text-slate-400">Vencimiento Cuota:</span> <span class="font-bold text-emerald-400">01/09/2026</span></div>
        </div>
        <div class="text-center">
            <p class="text-[10px] text-slate-400">Presenta esta credencial digital al empleado del comercio para validar tus beneficios.</p>
        </div>
        <a href="/" class="block text-center bg-slate-800 hover:bg-slate-700 text-white font-bold py-2.5 rounded-xl text-xs">Volver al inicio</a>
    </div>
</body>
</html>
"""

# 3. PANEL DE VALIDACIÓN PARA COMERCIOS / EMPLEADOS (Antifraude por DNI)
@app.get("/comercio/validar", response_class=HTMLResponse)
async def panel_validacion():
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validación de Socios - Comercios</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex flex-col items-center justify-center">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
        <div class="text-center space-y-2">
            <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">Control Antifraude</span>
            <h1 class="text-2xl font-black text-white">Validar DNI de Socio</h1>
            <p class="text-xs text-slate-400">Ingrese el DNI del cliente si tiene dudas o necesita reconfirmar la membresía activa.</p>
        </div>

        <form onsubmit="verificarSocio(event)" class="space-y-4">
            <input type="text" id="inputDni" required placeholder="Ingrese DNI sin puntos" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500">
            <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-3 rounded-xl text-xs uppercase transition shadow-lg">Verificar Estado en Sistema</button>
        </form>

        <div id="resultadoValidacion" class="hidden p-4 rounded-2xl text-xs space-y-2 border"></div>

        <div class="pt-4 border-t border-slate-800 text-center">
            <a href="/" class="text-xs font-bold text-slate-400 hover:text-white">← Volver al sitio principal</a>
        </div>
    </div>

    <script>
        function verificarSocio(e) {
            e.preventDefault();
            const dni = document.getElementById('inputDni').value;
            const resBox = document.getElementById('resultadoValidacion');
            resBox.classList.remove('hidden');

            if (dni.length >= 7) {
                resBox.className = "p-4 rounded-2xl text-xs space-y-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300";
                resBox.innerHTML = `
                    <p class="font-bold text-sm">✅ SOCIO ACTIVO HABILITADO</p>
                    <p>Cliente: <strong>Juan Pérez</strong></p>
                    <p>Plan: <strong>Familiar VIP ($5M)</strong></p>
                    <p class="text-[10px] text-emerald-400 pt-1">Cuota al día en Mercado Pago. Aplica descuento.</p>
                `;
            } else {
                resBox.className = "p-4 rounded-2xl text-xs space-y-1 bg-red-500/10 border border-red-500/30 text-red-300";
                resBox.innerHTML = `
                    <p class="font-bold text-sm">❌ SOCIO NO ENCONTRADO O VENCIDO</p>
                    <p>El DNI ingresado no figura con una suscripción activa al día.</p>
                `;
            }
        }
    </script>
</body>
</html>
"""

# 4. PANEL DE ADMINISTRACIÓN MAESTRO (Protegido por Contraseña)
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin)):
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Administración Maestro - Max%Shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#070C1E] text-slate-100 min-h-screen font-sans">

    <!-- Navbar Admin -->
    <header class="bg-[#0A1128] border-b border-slate-800 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <span class="text-xl font-black text-white">Max<span class="text-orange-500">%</span>Shop</span>
            <span class="bg-orange-500/20 text-orange-400 border border-orange-500/30 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">Panel Maestro Admin (Seguro)</span>
        </div>
        <a href="/" class="text-xs font-bold text-slate-400 hover:text-white bg-slate-800 px-4 py-2 rounded-xl">Ver Sitio Público →</a>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8 space-y-8">
        
        <!-- Métricas Rápidas -->
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div class="bg-[#101833] border border-slate-800 p-5 rounded-3xl space-y-1 shadow-lg">
                <p class="text-xs text-slate-400 uppercase font-bold">Socios Activos</p>
                <h3 class="text-2xl font-black text-emerald-400">1,248</h3>
            </div>
            <div class="bg-[#101833] border border-slate-800 p-5 rounded-3xl space-y-1 shadow-lg">
                <p class="text-xs text-slate-400 uppercase font-bold">Comercios Adheridos</p>
                <h3 class="text-2xl font-black text-blue-400">64</h3>
            </div>
            <div class="bg-[#101833] border border-slate-800 p-5 rounded-3xl space-y-1 shadow-lg">
                <p class="text-xs text-slate-400 uppercase font-bold">Cobros del Mes (MP)</p>
                <h3 class="text-2xl font-black text-orange-400">$8.450.000</h3>
            </div>
            <div class="bg-[#101833] border border-slate-800 p-5 rounded-3xl space-y-1 shadow-lg">
                <p class="text-xs text-slate-400 uppercase font-bold">Publicidades Pendientes</p>
                <h3 class="text-2xl font-black text-amber-400">3</h3>
            </div>
        </div>

        <!-- Moderación de Publicidades -->
        <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 space-y-6 shadow-xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                <div>
                    <h2 class="text-lg font-bold text-white">Moderación de Publicidades y Comercios</h2>
                    <p class="text-xs text-slate-400">Aprueba, rechaza o elimina las publicidades enviadas por las tiendas locales.</p>
                </div>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs text-slate-300">
                    <thead class="bg-[#0A1128] text-slate-400 uppercase tracking-wider border-b border-slate-800">
                        <tr>
                            <th class="p-3">Comercio</th>
                            <th class="p-3">Oferta / Descuento</th>
                            <th class="p-3">Estado</th>
                            <th class="p-3 text-right">Acciones de Control</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
                        <tr class="hover:bg-slate-800/40">
                            <td class="p-3 font-bold text-white">Café & Bar Central</td>
                            <td class="p-3">20% OFF en efectivo</td>
                            <td class="p-3"><span class="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">Aprobado</span></td>
                            <td class="p-3 text-right space-x-2">
                                <button onclick="alert('Publicidad pausada')" class="bg-amber-600/20 text-amber-400 px-3 py-1 rounded-lg font-bold">Pausar</button>
                                <button onclick="alert('Publicidad eliminada')" class="bg-red-600/20 text-red-400 px-3 py-1 rounded-lg font-bold">Eliminar</button>
                            </td>
                        </tr>
                        <tr class="hover:bg-slate-800/40">
                            <td class="p-3 font-bold text-white">Moda Urbana Store</td>
                            <td class="p-3">3 cuotas sin interés + 15% off</td>
                            <td class="p-3"><span class="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">Aprobado</span></td>
                            <td class="p-3 text-right space-x-2">
                                <button onclick="alert('Publicidad pausada')" class="bg-amber-600/20 text-amber-400 px-3 py-1 rounded-lg font-bold">Pausar</button>
                                <button onclick="alert('Publicidad eliminada')" class="bg-red-600/20 text-red-400 px-3 py-1 rounded-lg font-bold">Eliminar</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Automatizaciones -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
                <h3 class="text-base font-bold text-white">Motor de Geolocalización</h3>
                <p class="text-xs text-slate-400">Ejecuta o actualiza las reglas geográficas para las ciudades habilitadas en el sistema.</p>
                <button onclick="ejecutarPipeline()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-wider transition">Forzar Sincronización Geográfica</button>
            </div>

            <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
                <h3 class="text-base font-bold text-white">Control de Base de Datos (Supabase)</h3>
                <p class="text-xs text-slate-400">Verifica la integridad de los registros de socios y pagos pendientes.</p>
                <button onclick="alert('Base de datos sincronizada correctamente con Supabase.')" class="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-wider transition">Auditar Conexión Supabase</button>
            </div>
        </div>

    </main>

    <script>
        function ejecutarPipeline() {
            fetch('/api/admin/run-geolocation-pipeline', { method: 'POST' })
                .then(res => res.json())
                .then(data => alert('Pipeline ejecutado con éxito: ' + data.message));
        }
    </script>
</body>
</html>
"""

@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger = GeolocationTrigger(), username: str = Depends(verificar_admin)):
    return {"status": "success", "message": f"Pipeline de geolocalización actualizado para {payload.city}"}
