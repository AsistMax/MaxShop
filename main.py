from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, status, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random
import urllib.parse
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-anon-key")

# Clave y usuario de acceso configurados para el panel de administración
ADMIN_USER = "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
security = HTTPBasic()

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Panel Maestro",
    version="16.0.0"
)

# 1. Configuración de Archivos Estáticos para Subida de Imágenes Locales
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeolocationTrigger(BaseModel):
    city: str = "Catamarca"

# Función de autenticación segura para el panel de administración
def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USER or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administrador incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Simulación de Base de Datos Dinámica
DB_MOCK = {
    "socios": [
        {"dni": "12345678", "nombre": "Juan Pérez", "plan": "Familiar VIP ($5M)", "estado": "activo"}
    ],
    "comercios": [
        {
            "id": 1,
            "nombre": "Café & Bar Central",
            "categoria": "Gastronomía",
            "oferta": "20% de descuento abonando por transferencia o efectivo.",
            "imagen": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400",
            "estado": "Aprobado"
        },
        {
            "id": 2,
            "nombre": "Moda Urbana Store",
            "categoria": "Indumentaria",
            "oferta": "3 cuotas sin interés + 15% off",
            "imagen": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",
            "estado": "Aprobado"
        }
    ]
}

# 1. LANDING PAGE PRINCIPAL
@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, premio: str = None):
    # Generar las cards de los comercios dinámicamente
    comercios_activos = [c for c in DB_MOCK["comercios"] if c["estado"] == "Aprobado"]
    grid_html = ""
    for c in comercios_activos:
        grid_html += f"""
        <div class="bg-[#101833] border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
            <div class="h-40 bg-slate-800 rounded-2xl flex items-center justify-center overflow-hidden border border-slate-700">
                <img src="{c['imagen']}" alt="{c['nombre']}" class="w-full h-full object-cover">
            </div>
            <span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md">{c.get('categoria', 'Comercio')}</span>
            <h4 class="text-base font-bold text-white">{c['nombre']}</h4>
            <p class="text-xs text-slate-400">{c['oferta']}</p>
        </div>
        """

    # Alerta de Ruleta si el usuario ganó algo
    alerta_premio = ""
    if premio:
        alerta_premio = f"""
        <div class="bg-emerald-500/10 border border-emerald-500 text-emerald-400 px-4 py-3 rounded-xl font-bold text-sm mt-4 text-center">
            🎉 Resultado de la Ruleta: {premio}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Club de Beneficios y Cobertura Total</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes scroll {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        .animate-scroll {{ display: flex; width: max-content; animation: scroll 35s linear infinite; }}
        .animate-scroll:hover {{ animation-play-state: paused; }}
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0A1128; }}
        ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 4px; }}
        
        /* Estilos Ruleta */
        .wheel-container-wrapper {{ text-align: center; margin: 0 auto; }}
        .wheel-container {{ position: relative; width: 160px; height: 160px; border-radius: 50%; border: 6px solid #f97316; background: conic-gradient(#38bdf8 0deg 90deg, #3b82f6 90deg 180deg, #1e293b 180deg 270deg, #34d399 270deg 360deg); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(249, 115, 22, 0.3); }}
        .wheel-center {{ width: 40px; height: 40px; background: #0f172a; border-radius: 50%; border: 3px solid #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 10px; color: #f97316; }}
        .pointer {{ width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-bottom: 16px solid #f97316; margin: 0 auto -6px auto; position: relative; z-index: 10; }}
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR Y GEOLOCALIZACIÓN -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 flex flex-col sm:flex-row justify-between items-center border-b border-slate-800/80 gap-2">
        <div class="flex items-center gap-2">
            <span>📍 Ubicación:</span>
            <select id="citySelect" class="bg-[#0A1128] text-emerald-400 font-bold px-2 py-1 rounded border border-slate-700 focus:outline-none">
                <option value="Catamarca">Catamarca (Capital)</option>
                <option value="Valle Viejo">Valle Viejo</option>
            </select>
        </div>
        <div class="text-slate-300 font-medium hidden md:block">
            🌟 <span class="text-emerald-400 font-bold">Club de Descuentos:</span> Cobertura familiar de hasta <span class="text-orange-400 font-bold">$5.000.000</span>
        </div>
        <div class="flex items-center gap-3">
            <a href="/comercio/validar" class="text-[11px] font-bold bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded-full text-emerald-400 border border-slate-700">🛡️ Validar DNI</a>
            <a href="/admin" class="text-[11px] font-bold bg-orange-500/10 hover:bg-orange-500/20 px-3 py-1 rounded-full text-orange-400 border border-orange-500/30">⚙️ Admin</a>
        </div>
    </div>

    <!-- HEADER / NAVBAR -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-3 cursor-pointer">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                    Max<span class="text-orange-500">%</span>Shop
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <a href="/socio/12345678" class="hidden sm:inline-block text-xs font-bold text-blue-400 bg-blue-500/10 px-4 py-2.5 rounded-xl border border-blue-500/20">Ver Mi Credencial</a>
                <a href="#planes" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs sm:text-sm px-5 py-3 rounded-xl transition shadow-lg shadow-orange-500/20 uppercase">
                    🛡️ Suscribirme
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
        
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
                    Navega por los comercios adheridos, presenta tu credencial digital y obtén respaldo financiero.
                </p>
                <div class="pt-2 flex flex-wrap gap-4">
                    <a href="#comercios" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-7 py-3.5 rounded-2xl transition text-sm uppercase shadow-lg">Ver Comercios</a>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DE RULETA AGREGADA AL DISEÑO -->
        <div class="bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-orange-500/30 rounded-3xl p-8 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden">
            <div class="absolute -right-10 -top-10 w-40 h-40 bg-orange-500/10 blur-3xl rounded-full"></div>
            <div class="space-y-4 max-w-lg relative z-10">
                <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase tracking-wider border border-orange-500/20">Sorteo Interactivo</span>
                <h3 class="text-3xl font-black text-white">La Ruleta de la Fortuna</h3>
                <p class="text-sm text-slate-400 leading-relaxed">Gira por solo <b>$1.000</b>. Gana beneficios, servicios bonificados o descuentos exclusivos (tope estricto 20%).</p>
                <form action="/ruleta/pagar-y-girar" method="POST" class="pt-2">
                    <button type="submit" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-7 py-3 rounded-xl transition text-xs uppercase tracking-wider shadow-lg">💳 Pagar $1.000 y Girar</button>
                </form>
                {alerta_premio}
            </div>
            
            <div class="wheel-container-wrapper relative z-10">
                <div class="pointer"></div>
                <div class="wheel-container">
                    <div class="wheel-center">MAX%</div>
                </div>
            </div>
        </div>

        <!-- SECCIÓN: REGISTRO DE COMERCIOS (AHORA CON UPLOADFILE Y ENCTYPE) -->
        <div id="comercios" class="space-y-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-xl">
                <div class="md:w-1/3">
                    <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase tracking-wider border border-emerald-500/20">Portal de Socios</span>
                    <h2 class="text-2xl font-black text-white mt-2">Sube tu publicidad</h2>
                    <p class="text-sm text-slate-400 mt-2">Añade tu logo o foto del local y la oferta para aparecer al instante en la red.</p>
                </div>
                <!-- FORMULARIO REAL DE SUBIDA -->
                <form action="/comercio/publicar" method="POST" enctype="multipart/form-data" class="w-full md:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <input type="text" name="nombre" required placeholder="Nombre de tu tienda" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                    <input type="text" name="oferta" required placeholder="Ej: 25% OFF en efectivo" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500">
                    <select name="categoria" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-slate-400 focus:outline-none focus:border-emerald-500">
                        <option value="Gastronomía">Gastronomía</option>
                        <option value="Indumentaria">Indumentaria</option>
                        <option value="Servicios">Servicios</option>
                    </select>
                    <input type="file" name="imagen_archivo" accept="image/*" required class="bg-[#0A1128] border border-slate-700 px-4 py-2 rounded-xl text-xs text-slate-400 file:mr-4 file:py-1 file:px-3 file:rounded-full file:border-0 file:text-[10px] file:font-bold file:bg-emerald-500/10 file:text-emerald-400 hover:file:bg-emerald-500/20 cursor-pointer">
                    <div class="sm:col-span-2">
                        <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-5 py-3 rounded-xl text-xs uppercase tracking-wider transition">Publicar en Vitrina</button>
                    </div>
                </form>
            </div>

            <!-- VITRINA DINÁMICA DE PUBLICIDADES -->
            <div class="space-y-4 pt-4">
                <h3 class="text-xl font-bold text-white flex items-center gap-2">
                    <span>🛍️</span> Comercios y Publicidades Activas
                </h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {grid_html}
                </div>
            </div>
        </div>
    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800/80 bg-[#070C1E] mt-24 py-12 text-center text-xs text-slate-400 space-y-3">
        <p class="font-bold text-slate-300 text-sm">Max%Shop &copy; 2026 - Todos los derechos reservados.</p>
    </footer>
</body>
</html>
"""

# ==========================================
# ENDPOINTS AGREGADOS (IMÁGENES Y RULETA)
# ==========================================

@app.post("/comercio/publicar", response_class=HTMLResponse)
async def publicar_comercio(
    nombre: str = Form(...),
    oferta: str = Form(...),
    categoria: str = Form("Local"),
    imagen_archivo: UploadFile = File(...)
):
    """Guarda la imagen localmente y actualiza la vitrina"""
    imagen_url = "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400"
    
    if imagen_archivo and imagen_archivo.filename:
        file_path = os.path.join(UPLOAD_DIR, imagen_archivo.filename)
        with open(file_path, "wb") as buffer:
            content = await imagen_archivo.read()
            buffer.write(content)
        imagen_url = f"/static/uploads/{imagen_archivo.filename}"

    nuevo_comercio = {
        "id": len(DB_MOCK["comercios"]) + 1,
        "nombre": nombre,
        "categoria": categoria,
        "oferta": oferta,
        "imagen": imagen_url,
        "estado": "Aprobado"
    }
    DB_MOCK["comercios"].append(nuevo_comercio)
    
    # Redirigir de vuelta al inicio simulando éxito
    return RedirectResponse(url="/#comercios", status_code=303)


@app.post("/ruleta/pagar-y-girar", response_class=HTMLResponse)
async def pagar_y_girar():
    """Simula el cobro estilo Tailwind"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-[#0A1128] flex items-center justify-center h-screen">
        <div class="bg-[#101833] p-10 rounded-3xl border border-slate-800 text-center space-y-4 shadow-2xl max-w-sm">
            <h3 class="text-orange-500 font-bold text-xl">💳 Procesando Pago de $1.000</h3>
            <div class="w-10 h-10 border-4 border-slate-700 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
            <p class="text-slate-400 text-xs">Validando en MercadoPago para habilitar el giro...</p>
        </div>
        <script>setTimeout(() => { window.location.href = "/ruleta/girar-accion"; }, 2000);</script>
    </body>
    </html>
    """)

@app.get("/ruleta/girar-accion", response_class=HTMLResponse)
async def girar_accion():
    premios = [
        ("¡Seguí participando! Gracias por apoyar al club.", 55),
        ("Servicio de Asesoría / Cobertura Básica bonificada", 25),
        ("Descuento del 10% en Comercios Adheridos", 12),
        ("Descuento tope del 20% en la Red", 7),
        ("Premio Especial Bonificado", 1)
    ]
    premio_obtenido = random.choices([p[0] for p in premios], weights=[p[1] for p in premios], k=1)[0]
    return RedirectResponse(url=f"/?premio={urllib.parse.quote(premio_obtenido)}", status_code=303)


# ==========================================
# SECCIONES ORIGINALES (CREDENCIAL, ADMIN, VALIDAR)
# ==========================================

@app.get("/socio/{dni}", response_class=HTMLResponse)
async def credencial_digital(dni: str):
    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-sm bg-gradient-to-b from-[#1E2959] to-[#101833] border-2 border-emerald-500 rounded-3xl p-6 shadow-2xl space-y-6">
        <div class="flex justify-between items-center border-b border-slate-700 pb-4">
            <span class="font-black text-lg text-white">Max<span class="text-orange-500">%</span>Shop</span>
            <span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">Socio Activo</span>
        </div>
        <div class="text-center">
            <div class="w-20 h-20 bg-slate-800 rounded-full mx-auto flex items-center justify-center text-2xl font-bold text-slate-400 border border-slate-700 mb-2">👤</div>
            <h2 class="text-xl font-bold text-white">Juan Pérez</h2>
            <p class="text-xs text-slate-400">DNI: <span class="text-white font-mono">{dni}</span></p>
        </div>
        <a href="/" class="block text-center bg-slate-800 hover:bg-slate-700 text-white font-bold py-2.5 rounded-xl text-xs">Volver al inicio</a>
    </div>
</body>
</html>
"""

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin)):
    # Generar tabla dinámicamente con los comercios subidos
    filas_html = ""
    for c in DB_MOCK["comercios"]:
        filas_html += f"""
        <tr class="hover:bg-slate-800/40 border-b border-slate-800">
            <td class="p-3">
                <div class="flex items-center gap-3">
                    <img src="{c['imagen']}" class="w-10 h-10 rounded-lg object-cover bg-slate-800">
                    <div>
                        <p class="font-bold text-white text-sm">{c['nombre']}</p>
                        <p class="text-[10px] text-slate-400">{c['categoria']}</p>
                    </div>
                </div>
            </td>
            <td class="p-3 text-slate-300 text-xs">{c['oferta']}</td>
            <td class="p-3"><span class="bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded text-[10px] font-bold">Aprobado</span></td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#070C1E] text-slate-100 min-h-screen">
    <header class="bg-[#0A1128] border-b border-slate-800 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <span class="text-xl font-black text-white">Max<span class="text-orange-500">%</span>Shop</span>
            <span class="bg-orange-500/20 text-orange-400 border border-orange-500/30 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">Panel Maestro</span>
        </div>
        <a href="/" class="text-xs font-bold text-slate-400 hover:text-white bg-slate-800 px-4 py-2 rounded-xl">Ver Sitio Público →</a>
    </header>
    <main class="max-w-7xl mx-auto px-4 py-8 space-y-8">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="bg-[#101833] border border-slate-800 p-5 rounded-3xl"><p class="text-xs text-slate-400">Comercios</p><h3 class="text-2xl font-black text-blue-400">{len(DB_MOCK['comercios'])}</h3></div>
            <div class="bg-[#101833] border border-slate-800 p-5 rounded-3xl"><p class="text-xs text-slate-400">Socios Activos</p><h3 class="text-2xl font-black text-emerald-400">1,248</h3></div>
            <div class="bg-[#101833] border border-slate-800 p-5 rounded-3xl"><p class="text-xs text-slate-400">Caja</p><h3 class="text-2xl font-black text-orange-400">$8.450.000</h3></div>
        </div>
        <div class="bg-[#101833] border border-slate-800 rounded-3xl p-6 shadow-xl">
            <h2 class="text-lg font-bold text-white mb-4">Comercios Publicados en Vitrina</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="bg-[#0A1128] text-slate-400 uppercase">
                        <tr><th class="p-3">Comercio</th><th class="p-3">Oferta</th><th class="p-3">Estado</th></tr>
                    </thead>
                    <tbody>{filas_html}</tbody>
                </table>
            </div>
        </div>
    </main>
</body>
</html>
"""

# Validación vía POST unificada al diseño Tailwind
@app.get("/comercio/validar", response_class=HTMLResponse)
async def panel_validacion_get():
    return """<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex flex-col items-center justify-center">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
        <div class="text-center space-y-2">
            <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">Control Antifraude</span>
            <h1 class="text-2xl font-black text-white">Validar DNI</h1>
        </div>
        <form action="/comercio/validar" method="POST" class="space-y-4">
            <input type="text" name="dni" required placeholder="Ingrese DNI (Ej: 12345678)" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500">
            <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-3 rounded-xl text-xs uppercase shadow-lg">Verificar</button>
        </form>
        <div class="pt-4 border-t border-slate-800 text-center">
            <a href="/" class="text-xs font-bold text-slate-400 hover:text-white">← Volver al sitio</a>
        </div>
    </div>
</body>
</html>"""

@app.post("/comercio/validar", response_class=HTMLResponse)
async def panel_validacion_post(dni: str = Form(...)):
    socio = next((s for s in DB_MOCK["socios"] if s["dni"] == dni), None)
    if socio:
        html_res = f"""<div class="p-4 rounded-2xl text-xs bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
            <p class="font-bold text-sm">✅ SOCIO ACTIVO HABILITADO</p>
            <p>Cliente: <strong>{socio['nombre']}</strong> | Plan: <strong>{socio['plan']}</strong></p>
        </div>"""
    else:
        html_res = """<div class="p-4 rounded-2xl text-xs bg-red-500/10 border border-red-500/30 text-red-300">
            <p class="font-bold text-sm">❌ SOCIO NO ENCONTRADO O VENCIDO</p>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex items-center justify-center">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6 text-center">
        <h1 class="text-2xl font-black text-white">Resultado de Validación</h1>
        {html_res}
        <a href="/comercio/validar" class="block w-full bg-slate-800 text-white font-bold py-3 rounded-xl text-xs uppercase">Consultar otro DNI</a>
        <a href="/" class="block text-xs font-bold text-slate-400 hover:text-white pt-2">← Volver al sitio principal</a>
    </div>
</body>
</html>"""
