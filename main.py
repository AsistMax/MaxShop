from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, status, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random
import urllib.parse
from datetime import datetime

ADMIN_USER = "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026")

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Bolillero Semanal",
    version="19.0.0"
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

# Base de datos simulada con sistema de bolillero, apuestas semanales y pozo acumulado
DB_MOCK = {
    "pozo_acumulado": 450000, 
    "socios": [
        {"dni": "12345678", "nombre": "Juan Pérez", "plan": "Familiar VIP ($5M)", "estado": "activo"}
    ],
    "apuestas_semanales": [
        {"id": 1, "dni": "12345678", "nombre": "Juan Pérez", "numeros": [7, 14, 22, 33, 41], "comercio": "Café & Bar Central", "fecha": "2026-06-07"}
    ],
    "comercios": [
        {
            "id": 1,
            "nombre": "Café & Bar Central",
            "categoria": "Gastronomía",
            "oferta": "20% de descuento abonando en efectivo",
            "imagen": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400",
            "estado": "Aprobado"
        }
    ]
}

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, mensaje_sorteo: str = None):
    pozo_actual = DB_MOCK["pozo_acumulado"]
    
    apuestas_html = ""
    for ap in DB_MOCK["apuestas_semanales"]:
        nums_str = ", ".join(str(n) for n in ap["numeros"])
        apuestas_html += f"""
        <div class="bg-[#0A1128] border border-slate-800 p-4 rounded-2xl flex justify-between items-center text-xs">
            <div>
                <p class="font-bold text-white">{ap['nombre']} (DNI: {ap['dni']})</p>
                <p class="text-slate-400">Origen: {ap['comercio']} | Números: <span class="text-orange-400 font-mono font-bold">[{nums_str}]</span></p>
            </div>
            <span class="bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-md font-bold">Participa Domingo</span>
        </div>
        """

    alerta_sorteo = ""
    if mensaje_sorteo:
        alerta_sorteo = f"""
        <div class="bg-orange-500/10 border border-orange-500 text-orange-400 px-4 py-3 rounded-xl font-bold text-sm mt-4 text-center animate-pulse">
            🎲 {mensaje_sorteo}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Sorteo Semanal y Autogestión Digital</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0A1128; }}
        ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 4px; }}
        
        .wheel-container-wrapper {{ text-align: center; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }}
        .wheel-container {{
            position: relative; width: 260px; height: 260px; border-radius: 50%; border: 8px solid #cbd5e1;
            background: conic-gradient(
                #ef4444 0deg 36deg, #f97316 36deg 72deg, #eab308 72deg 108deg,
                #84cc16 108deg 144deg, #10b981 144deg 180deg, #06b6d4 180deg 216deg,
                #3b82f6 216deg 252deg, #8b5cf6 252deg 288deg, #ec4899 288deg 324deg, #f43f5e 324deg 360deg
            );
            box-shadow: 0 0 25px rgba(249, 115, 22, 0.4);
            display: flex; align-items: center; justify-content: center;
        }}
        .wheel-center {{
            width: 45px; height: 45px; background: #0f172a; border-radius: 50%; border: 4px solid #fff;
            display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 9px; color: #f97316;
        }}
        .pointer {{
            width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 20px solid #f97316;
            margin-bottom: -8px; z-index: 20; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.5));
        }}
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 flex justify-between items-center border-b border-slate-800">
        <span>📍 Catamarca (Capital) - App Oficial de Socios y Comercios</span>
        <div class="flex items-center gap-3">
            <a href="/comercio/validar" class="text-[11px] font-bold bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded-full text-emerald-400 border border-slate-700">🛡️ Validar Socio</a>
            <a href="/admin" class="text-[11px] font-bold bg-orange-500/10 hover:bg-orange-500/20 px-3 py-1 rounded-full text-orange-400 border border-orange-500/30">⚙️ Admin</a>
        </div>
    </div>

    <!-- HEADER -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                Max<span class="text-orange-500">%</span>Shop
            </div>
            <div class="flex items-center space-x-3">
                <a href="#comprar-app" class="hidden sm:inline-block text-xs font-bold text-emerald-400 bg-emerald-500/10 px-4 py-2.5 rounded-xl border border-emerald-500/20">📱 Comprar Online</a>
                <a href="#bolillero" class="hidden sm:inline-block text-xs font-bold text-orange-400 bg-orange-500/10 px-4 py-2.5 rounded-xl border border-orange-500/20">🎲 Sorteo Semanal</a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
        
        <!-- HERO -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-14 shadow-2xl">
            <div class="max-w-2xl space-y-6">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase">
                    <span>🔥</span> <span>Compra en Comercios o Directo en la App</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Pozo Acumulado <span class="text-orange-500">${pozo_actual:,.0f}</span>
                </h1>
                <p class="text-slate-300 text-base">Elegí tus números por $1.000 cada uno. Podes registrarlo en cualquier comercio adherido o comprarlos directamente aquí mismo en la app con pago digital.</p>
            </div>
        </div>

        <!-- SECCIÓN: COMPRAR NÚMEROS DIRECTO DESDE LA APP (CLIENTE) -->
        <div id="comprar-app" class="bg-gradient-to-r from-emerald-950/40 via-[#101833] to-[#0A1128] border border-emerald-500/40 rounded-3xl p-8 shadow-2xl space-y-6">
            <div class="max-w-xl space-y-2">
                <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase border border-emerald-500/20">Autogestión de Socio</span>
                <h3 class="text-2xl font-black text-white">Comprar Números Directo en la App ($1.000 c/u)</h3>
                <p class="text-xs text-slate-400">¿No querés pasar por el local? Ingresá tus datos, elegí tus números preferidos y abona online para participar este domingo.</p>
            </div>
            
            <form action="/app/comprar-jugada" method="POST" class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-4xl">
                <input type="text" name="dni" required placeholder="Tu DNI de Socio" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                <input type="text" name="nombre" required placeholder="Tu Nombre y Apellido" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                <input type="text" name="numeros" required placeholder="Ej: 3, 19, 27, 35, 42" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                <div class="sm:col-span-3">
                    <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-3 rounded-xl text-xs uppercase tracking-wider shadow-lg">
                        💳 Pagar Online y Participar este Domingo
                    </button>
                </div>
            </form>
        </div>

        <!-- SECCIÓN BOLILLERO / REGISTRO COMERCIAL -->
        <div id="bolillero" class="bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-orange-500/30 rounded-3xl p-8 shadow-2xl space-y-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div class="space-y-2 max-w-lg">
                    <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Sorteo Dominical Estilo Telekino</span>
                    <h3 class="text-3xl font-black text-white">El Bolillero de Max%Shop</h3>
                    <p class="text-sm text-slate-400 leading-relaxed">También podés acercarte a un comercio de la red habilitado y pedirle al comerciante que te cargue tus números de la suerte.</p>
                </div>
                <div class="bg-[#0A1128] border border-orange-500/40 p-6 rounded-2xl text-center shadow-xl">
                    <p class="text-xs text-slate-400">POZO ACUMULADO ACTUAL</p>
                    <p class="text-3xl font-black text-emerald-400 mt-1">${pozo_actual:,.0f}</p>
                    <span class="text-[10px] text-orange-400 mt-2 block font-bold">DOMINGO 21:00 HS</span>
                </div>
            </div>

            <!-- Formulario de Registro en Comercio Adherido -->
            <div class="bg-[#101833] border border-slate-800 p-6 rounded-2xl space-y-4">
                <h4 class="text-sm font-bold text-white uppercase tracking-wider">Registro Presencial en Comercio Adherido</h4>
                <form action="/bolillero/registrar" method="POST" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                    <input type="text" name="dni" required placeholder="DNI del Socio / Cliente" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                    <input type="text" name="nombre" required placeholder="Nombre y Apellido" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                    <input type="text" name="numeros" required placeholder="Ej: 5, 12, 23, 34, 45" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                    <select name="comercio" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-slate-300">
                        <option value="Café & Bar Central">Café & Bar Central</option>
                        <option value="Moda Urbana Store">Moda Urbana Store</option>
                    </select>
                    <div class="sm:col-span-2 md:col-span-4">
                        <button type="submit" class="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black py-3 rounded-xl text-xs uppercase tracking-wider">
                            🛡️ Registrar Jugada en Local Comercial
                        </button>
                    </div>
                </form>
                {alerta_sorteo}
            </div>

            <!-- Listado de jugadas activas -->
            <div class="space-y-3">
                <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Jugadas confirmadas para el sorteo:</h4>
                <div class="space-y-2">
                    {apuestas_html}
                </div>
            </div>

            <div class="pt-4 border-t border-slate-800 flex justify-end">
                <form action="/bolillero/sortear" method="POST">
                    <button type="submit" class="bg-slate-800 hover:bg-slate-700 text-orange-400 border border-orange-500/30 font-bold px-5 py-2.5 rounded-xl text-xs uppercase">
                        🎲 Simular Sorteo Dominical (Bolillero)
                    </button>
                </form>
            </div>
        </div>
    </main>
</body>
</html>
"""

@app.post("/app/comprar-jugada", response_class=HTMLResponse)
async def comprar_jugada_app(
    dni: str = Form(...),
    nombre: str = Form(...),
    numeros: str = Form(...)
):
    try:
        lista_nums = [int(n.strip()) for n in numeros.split(",") if n.strip().isdigit()]
    except:
        lista_nums = [4, 15, 26, 38, 49]

    nueva_apuesta = {
        "id": len(DB_MOCK["apuestas_semanales"]) + 1,
        "dni": dni,
        "nombre": nombre,
        "numeros": lista_nums,
        "comercio": "App Digital Directa",
        "fecha": datetime.now().strftime("%Y-%m-%d")
    }
    DB_MOCK["apuestas_semanales"].append(nueva_apuesta)
    
    monto_agregado = len(lista_nums) * 1000
    DB_MOCK["pozo_acumulado"] += monto_agregado

    mensaje = f"¡Compra exitosa en la App! Se procesaron ${monto_agregado} y tus números ya participan."
    return RedirectResponse(url=f"/?mensaje_sorteo={urllib.parse.quote(mensaje)}", status_code=303)

@app.post("/bolillero/registrar", response_class=HTMLResponse)
async def registrar_jugada(
    dni: str = Form(...),
    nombre: str = Form(...),
    numeros: str = Form(...),
    comercio: str = Form(...)
):
    try:
        lista_nums = [int(n.strip()) for n in numeros.split(",") if n.strip().isdigit()]
    except:
        lista_nums = [7, 14, 21]

    nueva_apuesta = {
        "id": len(DB_MOCK["apuestas_semanales"]) + 1,
        "dni": dni,
        "nombre": nombre,
        "numeros": lista_nums,
        "comercio": comercio,
        "fecha": datetime.now().strftime("%Y-%m-%d")
    }
    DB_MOCK["apuestas_semanales"].append(nueva_apuesta)
    
    monto_agregado = len(lista_nums) * 1000
    DB_MOCK["pozo_acumulado"] += monto_agregado

    mensaje = f"¡Jugada registrada en comercio! Se cobraron ${monto_agregado} y el pozo aumentó."
    return RedirectResponse(url=f"/?mensaje_sorteo={urllib.parse.quote(mensaje)}", status_code=303)

@app.post("/bolillero/sortear", response_class=HTMLResponse)
async def simular_sorteo():
    ganadores_sorteo = sorted(random.sample(range(1, 51), 5))
    
    ganador_encontrado = None
    for ap in DB_MOCK["apuestas_semanales"]:
        aciertos = len(set(ap["numeros"]).intersection(set(ganadores_sorteo)))
        if aciertos >= 3: 
            ganador_encontrado = ap["nombre"]
            break

    pozo_actual = DB_MOCK["pozo_acumulado"]
    if ganador_encontrado:
        mensaje = f"¡SORTEO DOMINICAL! Números ganadores: {ganadores_sorteo}. ¡Ganador del pozo de ${pozo_actual:,.0f}: {ganador_encontrado}!"
        DB_MOCK["pozo_acumulado"] = 200000 
        DB_MOCK["apuestas_semanales"] = [] 
    else:
        DB_MOCK["pozo_acumulado"] += 150000 
        mensaje = f"¡SORTEO DOMINICAL! Números bolillero: {ganadores_sorteo}. Pozo VACANTE. ¡Se acumulan $150.000 más para el próximo domingo!"

    return RedirectResponse(url=f"/?mensaje_sorteo={urllib.parse.quote(mensaje)}", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin)):
    apuestas_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs">
            <td class="p-3 text-white font-bold">{a['nombre']} (DNI: {a['dni']})</td>
            <td class="p-3 text-orange-400 font-mono">{a['numeros']}</td>
            <td class="p-3 text-slate-300">{a['comercio']}</td>
        </tr>""" for a in DB_MOCK["apuestas_semanales"]])

    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#070C1E] text-slate-100 min-h-screen p-8">
    <div class="max-w-4xl mx-auto space-y-6">
        <div class="flex justify-between items-center">
            <h1 class="text-2xl font-black">Panel de Administración</h1>
            <a href="/" class="bg-slate-800 px-4 py-2 rounded-xl text-xs">Ver Sitio</a>
        </div>
        <div class="bg-[#101833] p-6 rounded-3xl border border-slate-800 space-y-4">
            <h2 class="text-lg font-bold">Jugadas Registradas (App y Comercios)</h2>
            <table class="w-full text-left">
                <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-3">Socio / Cliente</th><th class="p-3">Números</th><th class="p-3">Origen</th></tr></thead>
                <tbody>{apuestas_filas}</tbody>
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
        <h1 class="text-2xl font-black text-center">Validar Socio / Jugada</h1>
        <form action="/comercio/validar" method="POST" class="space-y-4">
            <input type="text" name="dni" required placeholder="DNI del cliente" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-sm text-white">
            <button type="submit" class="w-full bg-emerald-500 text-slate-950 font-black py-3 rounded-xl text-xs uppercase">Verificar Estado</button>
        </form>
        <a href="/" class="block text-center text-xs text-slate-400">← Volver al inicio</a>
    </div>
</body>
</html>"""

@app.post("/comercio/validar", response_class=HTMLResponse)
async def validar_dni_post(dni: str = Form(...)):
    socio = next((s for s in DB_MOCK["socios"] if s["dni"] == dni), None)
    jugadas_socio = [j for j in DB_MOCK["apuestas_semanales"] if j["dni"] == dni]
    
    res = f"<p class='text-emerald-400 font-bold'>✅ Socio Activo: {socio['nombre']} ({socio['plan']})</p>" if socio else "<p class='text-red-400 font-bold'>❌ Socio no encontrado</p>"
    jugadas_str = "".join([f"<li class='text-xs text-orange-400 font-mono'>Números: {j['numeros']} (Origen: {j['comercio']})</li>" for j in jugadas_socio])
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex items-center justify-center">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 text-center space-y-6">
        <h1 class="text-xl font-bold">Resultado de Validación</h1>
        {res}
        <div class="text-left bg-[#0A1128] p-4 rounded-xl border border-slate-700">
            <p class="text-xs font-bold text-slate-300 mb-2">Jugadas activas para este domingo:</p>
            <ul class="list-disc pl-4 space-y-1">{jugadas_str if jugadas_str else "<p class='text-xs text-slate-500'>Sin jugadas esta semana.</p>"}</ul>
        </div>
        <a href="/comercio/validar" class="block bg-slate-800 text-white py-3 rounded-xl text-xs">Consultar otro DNI</a>
    </div>
</body>
</html>"""
