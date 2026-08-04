from fastapi import FastAPI, HTTPException, Depends, status, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
import random
import urllib.parse
from datetime import datetime

ADMIN_USER = "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026")

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Bolillero Semanal",
    version="20.0.0"
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

# Base de datos simulada completa para la app del cliente y comercios
DB_MOCK = {
    "pozo_acumulado": 450000, 
    "socios": [
        {"dni": "12345678", "nombre": "Juan Pérez", "plan": "Familiar VIP ($5M)", "estado": "activo"}
    ],
    "apuestas_semanales": [
        {"id": 1, "dni": "12345678", "nombre": "Juan Pérez", "numeros": [7, 14, 22, 33, 41], "comercio": "App Digital Directa", "fecha": "2026-06-07"}
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
            "oferta": "3 cuotas sin interés con tarjeta de socio",
            "imagen": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",
            "estado": "Aprobado"
        },
        {
            "id": 3,
            "nombre": "Farmacia del Pueblo",
            "categoria": "Salud y Bienestar",
            "oferta": "15% de descuento en perfumería",
            "imagen": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400",
            "estado": "Aprobado"
        }
    ]
}

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, mensaje_sorteo: str = None):
    pozo_actual = DB_MOCK["pozo_acumulado"]
    
    # Renderizar comercios adheridos para que el cliente los vea
    comercios_html = ""
    for com in DB_MOCK["comercios"]:
        comercios_html += f"""
        <div class="bg-[#101833] border border-slate-800 rounded-2xl overflow-hidden shadow-xl hover:border-orange-500/50 transition flex flex-col justify-between">
            <img src="{com['imagen']}" alt="{com['nombre']}" class="w-full h-40 object-cover opacity-80">
            <div class="p-5 space-y-3 flex-1 flex flex-col justify-between">
                <div class="space-y-1">
                    <span class="text-[10px] font-bold text-orange-400 bg-orange-500/10 px-2.5 py-1 rounded-md uppercase">{com['categoria']}</span>
                    <h4 class="text-base font-black text-white">{com['nombre']}</h4>
                    <p class="text-xs text-slate-300">🔥 <b>Beneficio:</b> {com['oferta']}</p>
                </div>
                <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                    <span>📍 Catamarca Capital</span>
                    <span class="text-emerald-400 font-bold">Activo en la Red</span>
                </div>
            </div>
        </div>
        """

    alerta_sorteo = ""
    if mensaje_sorteo:
        alerta_sorteo = f"""
        <div class="bg-orange-500/10 border border-orange-500 text-orange-400 px-4 py-3 rounded-xl font-bold text-sm text-center animate-pulse">
            🎲 {mensaje_sorteo}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Club de Beneficios y Bolillero Semanal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0A1128; }}
        ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 4px; }}
        
        .wheel-container-wrapper {{ text-align: center; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }}
        .wheel-container {{
            position: relative; width: 240px; height: 240px; border-radius: 50%; border: 8px solid #cbd5e1;
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

        /* Estilo Bolillero Real */
        .bolillero-cage {{
            width: 180px; height: 180px; border-radius: 50%; border: 4px solid rgba(255,255,255,0.2);
            background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.15), rgba(15,23,42,0.9));
            box-shadow: inset 0 0 20px rgba(255,255,255,0.1), 0 0 30px rgba(249,115,22,0.3);
            display: flex; align-items: center; justify-content: center; position: relative; margin: 0 auto;
        }}
        .bolilla {{
            width: 36px; height: 36px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ffedd5, #f97316);
            color: #0f172a; font-weight: 900; font-size: 14px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.4), inset -2px -2px 4px rgba(0,0,0,0.3);
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
            <nav class="hidden md:flex items-center space-x-6 text-xs font-bold text-slate-300">
                <a href="#comprar" class="hover:text-orange-400 transition">Comprar Números</a>
                <a href="#bolillero" class="hover:text-orange-400 transition">Bolillero Dominical</a>
                <a href="#comercios" class="hover:text-orange-400 transition">Comercios Adheridos</a>
                <a href="#ruleta" class="hover:text-orange-400 transition">Ruleta</a>
            </nav>
            <div class="flex items-center space-x-3">
                <a href="#comprar" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs px-4 py-2.5 rounded-xl uppercase shadow-lg">
                    Participar $1.000
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16">
        
        <!-- HERO -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-8 md:p-14 shadow-2xl flex flex-col md:flex-row justify-between items-center gap-8">
            <div class="max-w-xl space-y-6">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase">
                    <span>🔥</span> <span>Sorteo Semanal estilo Telekino y Quiniela</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Pozo Acumulado <span class="text-orange-500">${pozo_actual:,.0f}</span>
                </h1>
                <p class="text-slate-300 text-sm leading-relaxed">Elegí tus números de la suerte por solo $1.000 cada uno. Participa todos los domingos y gana beneficios exclusivos en nuestra red de comercios en Catamarca.</p>
                <div class="flex gap-4">
                    <a href="#comprar" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-6 py-3 rounded-xl text-xs uppercase shadow-lg">Comprar Números</a>
                    <a href="#comercios" class="bg-slate-800 hover:bg-slate-700 text-white font-bold px-6 py-3 rounded-xl text-xs uppercase border border-slate-700">Ver Comercios</a>
                </div>
            </div>
            <div class="bg-[#0A1128] border border-orange-500/30 p-6 rounded-3xl shadow-2xl text-center space-y-4">
                <p class="text-xs text-slate-400 font-bold uppercase tracking-wider">Próximo Sorteo Dominical</p>
                <div class="bolillero-cage">
                    <div class="bolilla animate-bounce">17</div>
                </div>
                <p class="text-[11px] text-orange-400 font-bold">DOMINGO 21:00 HS EN VIVO</p>
            </div>
        </div>

        {alerta_sorteo}

        <!-- SECCIÓN 1: COMPRAR NÚMEROS EN LA APP -->
        <div id="comprar" class="bg-gradient-to-r from-emerald-950/30 via-[#101833] to-[#0A1128] border border-emerald-500/40 rounded-3xl p-8 shadow-2xl space-y-6">
            <div class="max-w-xl space-y-2">
                <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase border border-emerald-500/20">Autogestión de Socio</span>
                <h3 class="text-2xl font-black text-white">Comprar Números Directo en la App ($1.000 c/u)</h3>
                <p class="text-xs text-slate-400">Ingresá tus datos, elegí tus números preferidos y abona online para participar este domingo en el pozo acumulado.</p>
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

        <!-- SECCIÓN 2: EL BOLILLERO VIRTUAL REAL -->
        <div id="bolillero" class="bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-orange-500/30 rounded-3xl p-8 shadow-2xl space-y-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div class="space-y-2 max-w-xl">
                    <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Sorteo Dominical Estilo Telekino</span>
                    <h3 class="text-3xl font-black text-white">El Bolillero Virtual de Max%Shop</h3>
                    <p class="text-sm text-slate-400 leading-relaxed">Nuestro bolillero electrónico sortea semanalmente las bolillas ganadoras. Si tus números coinciden, te llevas el pozo acumulado.</p>
                </div>
                <div class="bg-[#0A1128] border border-orange-500/40 p-6 rounded-2xl text-center shadow-xl w-full md:w-auto">
                    <p class="text-xs text-slate-400">POZO ACUMULADO ACTUAL</p>
                    <p class="text-3xl font-black text-emerald-400 mt-1">${pozo_actual:,.0f}</p>
                </div>
            </div>

            <!-- Simulación visual de bolillas saliendo del bolillero -->
            <div class="bg-[#0A1128] border border-slate-800 p-8 rounded-2xl text-center space-y-6">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Últimas Bolillas Sorteadas del Bolillero</p>
                <div class="flex justify-center items-center gap-4 flex-wrap">
                    <div class="bolilla">07</div>
                    <div class="bolilla">14</div>
                    <div class="bolilla">22</div>
                    <div class="bolilla">33</div>
                    <div class="bolilla">41</div>
                </div>
                <div class="pt-2">
                    <form action="/bolillero/sortear" method="POST">
                        <button type="submit" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-8 py-3 rounded-xl text-xs uppercase shadow-lg">
                            🎲 Girar Bolillero y Simular Sorteo Dominical
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <!-- SECCIÓN 3: COMERCIOS ADHERIDOS (LO QUE IMPORTA PARA MOSTRAR LA RED) -->
        <div id="comercios" class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                <div class="space-y-2">
                    <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Red Comercial Catamarca</span>
                    <h3 class="text-3xl font-black text-white">Comercios Adheridos</h3>
                    <p class="text-xs text-slate-400">Con tu credencial de socio o participando en el bolillero accedés a beneficios en estos locales.</p>
                </div>
            </div>

            <!-- Grid de Comercios -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {comercios_html}
            </div>
        </div>

        <!-- SECCIÓN 4: RULETA COMERCIAL -->
        <div id="ruleta" class="bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-slate-800 rounded-3xl p-8 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-8">
            <div class="space-y-4 max-w-lg">
                <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Ruleta de Descuentos</span>
                <h3 class="text-3xl font-black text-white">Gira por Beneficios Directos</h3>
                <p class="text-sm text-slate-400 leading-relaxed">Los socios activos pueden girar la ruleta para ganar premios instantáneos en los comercios adheridos de la red.</p>
                <form action="/ruleta/iniciar-pago" method="POST">
                    <button type="submit" class="bg-slate-800 hover:bg-slate-700 text-white font-bold px-6 py-3 rounded-xl transition text-xs uppercase border border-slate-700">
                        Girar Ruleta Comercial ($1.000)
                    </button>
                </form>
            </div>
            <div class="wheel-container-wrapper">
                <div class="pointer"></div>
                <div class="wheel-container">
                    <div class="wheel-center">MAX%</div>
                </div>
            </div>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800 bg-[#070C1E] mt-20 py-10 text-center text-xs text-slate-500">
        <p>Max%Shop © 2026 - Catamarca (Capital), Argentina. Todos los derechos reservados.</p>
    </footer>
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

    mensaje = f"¡Compra exitosa! Se procesaron ${monto_agregado} y tus números ya participan para este domingo."
    return RedirectResponse(url=f"/?mensaje_sorteo={urllib.parse.quote(mensaje)}#bolillero", status_code=303)

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
        mensaje = f"¡SORTEO REALIZADO! Bolillas: {ganadores_sorteo}. ¡Ganador del pozo de ${pozo_actual:,.0f}: {ganador_encontrado}!"
        DB_MOCK["pozo_acumulado"] = 200000 
        DB_MOCK["apuestas_semanales"] = [] 
    else:
        DB_MOCK["pozo_acumulado"] += 150000 
        mensaje = f"¡SORTEO REALIZADO! Bolillas: {ganadores_sorteo}. Pozo VACANTE. ¡Se acumulan $150.000 más para el próximo domingo!"

    return RedirectResponse(url=f"/?mensaje_sorteo={urllib.parse.quote(mensaje)}#bolillero", status_code=303)

@app.post("/ruleta/iniciar-pago", response_class=HTMLResponse)
async def iniciar_pago():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-[#0A1128] flex items-center justify-center h-screen">
        <div class="bg-[#101833] p-10 rounded-3xl border border-slate-800 text-center space-y-4 shadow-2xl max-w-sm">
            <h3 class="text-orange-500 font-bold text-xl">💳 Redirigiendo a Pasarela</h3>
            <div class="w-10 h-10 border-4 border-slate-700 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
            <p class="text-slate-400 text-xs">Procesando pago de ruleta...</p>
        </div>
        <script>setTimeout(() => { window.location.href = "/#ruleta"; }, 2000);</script>
    </body>
    </html>
    """)

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
            <a href="/" class="bg-slate-800 px-4 py-2 rounded-xl text-xs text-white">Ver Sitio</a>
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
        <h1 class="text-2xl font-black text-center text-white">Validar Socio / Jugada</h1>
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
        <h1 class="text-xl font-bold text-white">Resultado de Validación</h1>
        {res}
        <div class="text-left bg-[#0A1128] p-4 rounded-xl border border-slate-700">
            <p class="text-xs font-bold text-slate-300 mb-2">Jugadas activas para este domingo:</p>
            <ul class="list-disc pl-4 space-y-1">{jugadas_str if jugadas_str else "<p class='text-xs text-slate-500'>Sin jugadas esta semana.</p>"}</ul>
        </div>
        <a href="/comercio/validar" class="block bg-slate-800 text-white py-3 rounded-xl text-xs">Consultar otro DNI</a>
    </div>
</body>
</html>"""
