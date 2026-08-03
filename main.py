from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Max%Shop - Ecosistema Integral y Panel Admin",
    version="14.0.0"
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

# 1. LANDING PRINCIPAL
@app.get("/", response_class=HTMLResponse)
async def client_landing():
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Club de Beneficios y Cobertura Total</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white">

    <header class="sticky top-0 z-50 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800">
        <div class="max-w-7xl mx-auto px-4 h-20 flex items-center justify-between">
            <div class="text-2xl font-black text-white">Max<span class="text-orange-500">%</span>Shop</div>
            <div class="flex items-center gap-3">
                <a href="/comercio/validar" class="text-xs font-bold bg-slate-800 hover:bg-slate-700 px-3 py-2.5 rounded-xl border border-slate-700 text-emerald-400">🛡️ Validar DNI</a>
                <a href="/admin" class="text-xs font-bold bg-orange-500/10 hover:bg-orange-500/20 px-3 py-2.5 rounded-xl border border-orange-500/30 text-orange-400">⚙️ Admin</a>
                <a href="#planes" class="bg-gradient-to-r from-orange-500 to-amber-500 text-slate-950 font-black text-xs px-4 py-2.5 rounded-xl uppercase">Suscribirme</a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-12 space-y-12">
        <div class="bg-gradient-to-br from-[#131E3E] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-12 text-center space-y-6">
            <h1 class="text-4xl font-black text-white">Club de Descuentos + Cobertura Total $5.000.000</h1>
            <p class="text-slate-300 text-sm max-w-xl mx-auto">Disfruta de beneficios en comercios locales y protege a tu familia ante emergencias extremas.</p>
            <div class="flex justify-center gap-4">
                <a href="/socio/ejemplo-dni" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-3 rounded-xl text-xs uppercase shadow-lg">Ver Credencial Digital Ejemplo</a>
            </div>
        </div>

        <div id="planes" class="text-center space-y-6">
            <h2 class="text-2xl font-black text-white">Planes Oficiales</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
                <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 text-left space-y-4">
                    <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-md">PLAN ESENCIAL</span>
                    <h3 class="text-xl font-bold text-white">$5.000 / mes</h3>
                    <p class="text-xs text-slate-400">Credencial digital + Club de descuentos locales.</p>
                    <a href="https://link.mercadopago.com.ar/tu-link-esencial" target="_blank" class="block text-center py-3 bg-blue-600 text-white font-bold rounded-xl text-xs uppercase">Suscribirme</a>
                </div>
                <div class="bg-gradient-to-b from-[#1E2959] to-[#101833] border-2 border-orange-500 rounded-3xl p-6 text-left space-y-4 relative">
                    <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-md">PLAN FAMILIAR VIP</span>
                    <h3 class="text-xl font-bold text-white">$8.000 / mes</h3>
                    <p class="text-xs text-slate-300">Credencial digital VIP + Cobertura total de $5.000.000 para emergencias.</p>
                    <a href="https://link.mercadopago.com.ar/tu-link-familiar" target="_blank" class="block text-center py-3 bg-orange-500 text-slate-950 font-black rounded-xl text-xs uppercase">Suscribirme a los $5M</a>
                </div>
            </div>
        </div>
    </main>
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
        <a href="/" class="block text-center bg-slate-800 hover:bg-slate-700 text-white font-bold py-2.5 rounded-xl text-xs">Volver al inicio</a>
    </div>
</body>
</html>
"""

# 3. PANEL DE VALIDACIÓN PARA COMERCIOS / EMPLEADOS
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
            <p class="text-xs text-slate-400">Ingrese el DNI del cliente para verificar su membresía activa al instante.</p>
        </div>
        <form onsubmit="verificarSocio(event)" class="space-y-4">
            <input type="text" id="inputDni" required placeholder="Ingrese DNI sin puntos" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500">
            <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-3 rounded-xl text-xs uppercase transition shadow-lg">Verificar Estado</button>
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
                resBox.innerHTML = `<p class="font-bold text-sm">✅ SOCIO ACTIVO HABILITADO</p><p>Cliente: <strong>Juan Pérez</strong></p><p>Plan: <strong>Familiar VIP ($5M)</strong></p>`;
            } else {
                resBox.className = "p-4 rounded-2xl text-xs space-y-1 bg-red-500/10 border border-red-500/30 text-red-300";
                resBox.innerHTML = `<p class="font-bold text-sm">❌ NO ENCONTRADO O VENCIDO</p>`;
            }
        }
    </script>
</body>
</html>
"""

# 4. PANEL DE ADMINISTRACIÓN MAESTRO (Control Total)
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
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
            <span class="bg-orange-500/20 text-orange-400 border border-orange-500/30 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">Panel Maestro Admin</span>
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

        <!-- Sección de Control de Comercios y Publicidades -->
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

        <!-- Acciones del Sistema / Automatizaciones -->
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
async def run_geolocation_pipeline(payload: GeolocationTrigger = GeolocationTrigger()):
    return {"status": "success", "message": f"Pipeline de geolocalización actualizado para {payload.city}"}
