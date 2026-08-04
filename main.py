from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, status, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random
import urllib.parse

ADMIN_USER = "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026")

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Ruleta Comercial",
    version="17.0.0"
)

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

def verificar_admin(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    if credentials.username != ADMIN_USER or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Base de datos simulada con comercios y ofertas reales
DB_MOCK = {
    "socios": [
        {"dni": "12345678", "nombre": "Juan Pérez", "plan": "Familiar VIP ($5M)", "estado": "activo"}
    ],
    "comercios": [
        {
            "id": 1,
            "nombre": "Café & Bar Central",
            "categoria": "Gastronomía",
            "oferta": "20% de descuento abonando en efectivo",
            "imagen": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400",
            "estado": "Aprobado"
        },
        {
            "id": 2,
            "nombre": "Moda Urbana Store",
            "categoria": "Indumentaria",
            "oferta": "15% off en toda la temporada",
            "imagen": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",
            "estado": "Aprobado"
        }
    ]
}

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, premio: str = None):
    comercios_activos = [c for c in DB_MOCK["comercios"] if c["estado"] == "Aprobado"]
    
    # Renderizar grilla de comercios
    grid_html = ""
    for c in comercios_activos:
        grid_html += f"""
        <div class="bg-[#101833] border border-slate-800 rounded-3xl p-5 space-y-3 shadow-xl">
            <div class="h-40 bg-slate-800 rounded-2xl overflow-hidden border border-slate-700">
                <img src="{c['imagen']}" alt="{c['nombre']}" class="w-full h-full object-cover">
            </div>
            <span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md">{c.get('categoria', 'Comercio')}</span>
            <h4 class="text-base font-bold text-white">{c['nombre']}</h4>
            <p class="text-xs text-slate-400">{c['oferta']}</p>
        </div>
        """

    # Alerta de Ruleta si el usuario ganó
    alerta_premio = ""
    if premio:
        alerta_premio = f"""
        <div class="bg-emerald-500/10 border border-emerald-500 text-emerald-400 px-4 py-3 rounded-xl font-bold text-sm mt-4 text-center animate-pulse">
            🎉 ¡Premio obtenido en la Ruleta: {premio}!
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Club de Beneficios y Ruleta Comercial</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0A1128; }}
        ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 4px; }}
        
        /* Estilo Ruleta Multisección similar a la foto de referencia */
        .wheel-container-wrapper {{ text-align: center; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }}
        .wheel-container {{
            position: relative;
            width: 260px;
            height: 260px;
            border-radius: 50%;
            border: 8px solid #cbd5e1;
            /* Degradado cónico simulando los gajos de colores múltiples */
            background: conic-gradient(
                #ef4444 0deg 36deg,
                #f97316 36deg 72deg,
                #eab308 72deg 108deg,
                #84cc16 108deg 144deg,
                #10b981 144deg 180deg,
                #06b6d4 180deg 216deg,
                #3b82f6 216deg 252deg,
                #8b5cf6 252deg 288deg,
                #ec4899 288deg 324deg,
                #f43f5e 324deg 360deg
            );
            box-shadow: 0 0 25px rgba(249, 115, 22, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .wheel-center {{
            width: 45px;
            height: 45px;
            background: #0f172a;
            border-radius: 50%;
            border: 4px solid #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 9px;
            color: #f97316;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .pointer {{
            width: 0; 
            height: 0; 
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-bottom: 20px solid #f97316;
            margin-bottom: -8px;
            z-index: 20;
            filter: drop-shadow(0 2px 2px rgba(0,0,0,0.5));
        }}
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 flex justify-between items-center border-b border-slate-800">
        <div class="flex items-center gap-2">
            <span>📍 Catamarca (Capital)</span>
        </div>
        <div class="flex items-center gap-3">
            <a href="/comercio/validar" class="text-[11px] font-bold bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded-full text-emerald-400 border border-slate-700">🛡️ Validar DNI</a>
            <a href="/admin" class="text-[11px] font-bold bg-orange-500/10 hover:bg-orange-500/20 px-3 py-1 rounded-full text-orange-400 border border-orange-500/30">⚙️ Admin</a>
        </div>
    </div>

    <!-- HEADER / NAVBAR -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                Max<span class="text-orange-500">%</span>Shop
            </div>
            <div class="flex items-center space-x-3">
                <a href="/socio/12345678" class="hidden sm:inline-block text-xs font-bold text-blue-400 bg-blue-500/10 px-4 py-2.5 rounded-xl border border-blue-500/20">Ver Credencial</a>
                <a href="#planes" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs sm:text-sm px-5 py-3 rounded-xl transition shadow-lg shadow-orange-500/20 uppercase">
                    🛡️ Suscribirme
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
        
        <!-- HERO -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-14 shadow-2xl">
            <div class="max-w-2xl space-y-6">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase">
                    <span>🔥</span> <span>Club de Beneficios y Cobertura Total</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Descuentos Reales + Cobertura <span class="text-orange-500">$5.000.000</span>
                </h1>
                <p class="text-slate-300 text-base">Gira la ruleta comercial con los descuentos reales cargados por los comercios de la red.</p>
            </div>
        </div>

        <!-- SECCIÓN RULETA COMERCIAL ESTÉTICA -->
        <div class="bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-orange-500/30 rounded-3xl p-8 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-8">
            <div class="space-y-4 max-w-lg">
                <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Ruleta Interactiva Comercial</span>
                <h3 class="text-3xl font-black text-white">Gira por Descuentos de Comercios</h3>
                <p class="text-sm text-slate-400 leading-relaxed">Participa por tan solo <b>$1.000</b>. Los premios se generan directamente utilizando los descuentos registrados por nuestros comercios adheridos.</p>
                
                <!-- Botón de Pago Real (Listo para integrar pasarela MercadoPago) -->
                <form action="/ruleta/iniciar-pago" method="POST" class="pt-2">
                    <button type="submit" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-7 py-3 rounded-xl transition text-xs uppercase tracking-wider shadow-lg flex items-center gap-2">
                        💳 Pagar $1.000 y Girar (Mercado Pago)
                    </button>
                </form>
                {alerta_premio}
            </div>
            
            <div class="wheel-container-wrapper">
                <div class="pointer"></div>
                <div class="wheel-container">
                    <div class="wheel-center">MAX%</div>
                </div>
            </div>
        </div>

        <!-- SECCIÓN DE PLANES / SUSCRIPCIÓN (BOTÓN ARREGLADO) -->
        <div id="planes" class="bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-xl space-y-6">
            <div class="text-center max-w-xl mx-auto space-y-2">
                <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Membresías</span>
                <h3 class="text-2xl font-black text-white">Planes de Suscripción Activos</h3>
                <p class="text-xs text-slate-400">Obtén acceso ilimitado a todos los descuentos y cobertura médica/financiera familiar.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
                <div class="bg-[#0A1128] border border-slate-800 p-6 rounded-2xl space-y-4">
                    <h4 class="text-lg font-bold text-white">Plan Estándar</h4>
                    <p class="text-2xl font-black text-orange-400">$3.500 <span class="text-xs text-slate-400 font-normal">/mes</span></p>
                    <ul class="text-xs text-slate-300 space-y-2">
                        <li>✔️ Credencial digital de socio</li>
                        <li>✔️ Acceso a descuentos en red</li>
                    </ul>
                    <a href="/ruleta/iniciar-pago" class="block text-center bg-slate-800 hover:bg-slate-700 text-white font-bold py-2.5 rounded-xl text-xs uppercase">Suscribirme</a>
                </div>
                <div class="bg-gradient-to-b from-blue-950/40 to-[#0A1128] border border-blue-500/40 p-6 rounded-2xl space-y-4 relative">
                    <span class="absolute top-4 right-4 bg-blue-500 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded">POPULAR</span>
                    <h4 class="text-lg font-bold text-white">Plan Familiar VIP</h4>
                    <p class="text-2xl font-black text-emerald-400">$6.500 <span class="text-xs text-slate-400 font-normal">/mes</span></p>
                    <ul class="text-xs text-slate-300 space-y-2">
                        <li>✔️ Cobertura total hasta $5.000.000</li>
                        <li>✔️ Descuentos VIP en comercios</li>
                        <li>✔️ Giros gratis mensuales en ruleta</li>
                    </ul>
                    <a href="/ruleta/iniciar-pago" class="block text-center bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 rounded-xl text-xs uppercase shadow-lg">Elegir VIP</a>
                </div>
            </div>
        </div>

        <!-- VITRINA DE COMERCIOS -->
        <div id="comercios" class="space-y-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#101833] border border-slate-800 rounded-3xl p-8">
                <div class="md:w-1/3">
                    <h2 class="text-2xl font-black text-white">Sube tu Comercio</h2>
                    <p class="text-xs text-slate-400 mt-1">Registra tu oferta para que aparezca en la vitrina y en la ruleta de premios.</p>
                </div>
                <form action="/comercio/publicar" method="POST" enctype="multipart/form-data" class="w-full md:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <input type="text" name="nombre" required placeholder="Nombre del comercio" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                    <input type="text" name="oferta" required placeholder="Ej: 20% de descuento en efectivo" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                    <select name="categoria" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-slate-400">
                        <option value="Gastronomía">Gastronomía</option>
                        <option value="Indumentaria">Indumentaria</option>
                    </select>
                    <input type="file" name="imagen_archivo" accept="image/*" required class="bg-[#0A1128] border border-slate-700 px-4 py-2 rounded-xl text-xs text-slate-400">
                    <div class="sm:col-span-2">
                        <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-5 py-3 rounded-xl text-xs uppercase">Publicar Oferta</button>
                    </div>
                </form>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {grid_html}
            </div>
        </div>
    </main>
</body>
</html>
"""

@app.post("/comercio/publicar", response_class=HTMLResponse)
async def publicar_comercio(
    nombre: str = Form(...),
    oferta: str = Form(...),
    categoria: str = Form("Local"),
    imagen_archivo: UploadFile = File(...)
):
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
    return RedirectResponse(url="/#comercios", status_code=303)

@app.post("/ruleta/iniciar-pago", response_class=HTMLResponse)
async def iniciar_pago():
    """Simula o integra pasarela de pago real (Ej: Mercado Pago)"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-[#0A1128] flex items-center justify-center h-screen">
        <div class="bg-[#101833] p-10 rounded-3xl border border-slate-800 text-center space-y-4 shadow-2xl max-w-sm">
            <h3 class="text-orange-500 font-bold text-xl">💳 Redirigiendo a Mercado Pago</h3>
            <div class="w-10 h-10 border-4 border-slate-700 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
            <p class="text-slate-400 text-xs">Generando orden de cobro segura...</p>
        </div>
        <script>setTimeout(() => { window.location.href = "/ruleta/girar-premio-real"; }, 2500);</script>
    </body>
    </html>
    """)

@app.get("/ruleta/girar-premio-real", response_class=HTMLResponse)
async def girar_premio_real():
    # Extraer ofertas reales cargadas por los comercios para armar la ruleta de premios dinámica
    premios_comercios = [c["oferta"] for c in DB_MOCK["comercios"] if c["estado"] == "Aprobado"]
    premios_genericos = ["¡Suerte la próxima!", "Regalo Sorpresa en Red", "Vuelve a Girar"]
    
    bolsa_premios = premios_comercios + premios_genericos
    premio_obtenido = random.choice(bolsa_premios)
    
    return RedirectResponse(url=f"/?premio={urllib.parse.quote(premio_obtenido)}", status_code=303)

@app.get("/socio/{dni}", response_class=HTMLResponse)
async def credencial_digital(dni: str):
    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-sm bg-[#101833] border-2 border-emerald-500 rounded-3xl p-6 shadow-2xl space-y-6">
        <div class="flex justify-between items-center border-b border-slate-700 pb-4">
            <span class="font-black text-lg text-white">Max<span class="text-orange-500">%</span>Shop</span>
            <span class="bg-emerald-500/20 text-emerald-400 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">Socio Activo</span>
        </div>
        <div class="text-center">
            <h2 class="text-xl font-bold text-white">Juan Pérez</h2>
            <p class="text-xs text-slate-400">DNI: <span class="text-white font-mono">{dni}</span></p>
        </div>
        <a href="/" class="block text-center bg-slate-800 text-white font-bold py-2.5 rounded-xl text-xs">Volver al inicio</a>
    </div>
</body>
</html>"""

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin)):
    filas = "".join([f"""
        <tr class="border-b border-slate-800">
            <td class="p-3 text-white font-bold">{c['nombre']}</td>
            <td class="p-3 text-slate-300">{c['oferta']}</td>
            <td class="p-3 text-emerald-400">Activo en Ruleta</td>
        </tr>""" for c in DB_MOCK["comercios"]])
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#070C1E] text-slate-100 min-h-screen p-8">
    <div class="max-w-4xl mx-auto space-y-6">
        <div class="flex justify-between items-center">
            <h1 class="text-2xl font-black">Panel de Administración</h1>
            <a href="/" class="bg-slate-800 px-4 py-2 rounded-xl text-xs">Ver Sitio</a>
        </div>
        <div class="bg-[#101833] p-6 rounded-3xl border border-slate-800">
            <h2 class="text-lg font-bold mb-4">Ofertas Activas en la Ruleta</h2>
            <table class="w-full text-left text-xs">
                <thead><tr class="text-slate-400 border-b border-slate-800"><th class="p-3">Comercio</th><th class="p-3">Descuento / Oferta</th><th class="p-3">Estado</th></tr></thead>
                <tbody>{filas}</tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

@app.get("/comercio/validar", response_class=HTMLResponse)
async def validar_dni_get():
    return """<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex items-center justify-center">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
        <h1 class="text-2xl font-black text-center">Validar DNI de Socio</h1>
        <form action="/comercio/validar" method="POST" class="space-y-4">
            <input type="text" name="dni" required placeholder="DNI del cliente" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-sm text-white">
            <button type="submit" class="w-full bg-emerald-500 text-slate-950 font-black py-3 rounded-xl text-xs uppercase">Verificar</button>
        </form>
        <a href="/" class="block text-center text-xs text-slate-400">← Volver</a>
    </div>
</body>
</html>"""

@app.post("/comercio/validar", response_class=HTMLResponse)
async def validar_dni_post(dni: str = Form(...)):
    socio = next((s for s in DB_MOCK["socios"] if s["dni"] == dni), None)
    res = f"<p class='text-emerald-400 font-bold'>✅ Socio Activo: {socio['nombre']}</p>" if socio else "<p class='text-red-400 font-bold'>❌ Socio no encontrado</p>"
    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex items-center justify-center">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 text-center space-y-6">
        <h1 class="text-xl font-bold">Resultado</h1>
        {res}
        <a href="/comercio/validar" class="block bg-slate-800 text-white py-3 rounded-xl text-xs">Consultar otro</a>
    </div>
</body>
</html>"""
