import os
import urllib.parse
from fastapi import FastAPI, HTTPException, Depends, status, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware

ADMIN_USER = "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026")

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Bolillero Semanal",
    version="23.0.0"
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
            detail="Credenciales incorrectas de Administrador",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

DB_MOCK = {
    "pozo_acumulado": 900000,
    "usuarios": [
        {"dni": "12345678", "nombre": "Juan Pérez", "email": "juan@mail.com", "telefono": "3834123456", "ciudad": "Catamarca (Capital)", "suscripcion": "Activa ($10M)"}
    ],
    "colaboradores": [
        {"id": 1, "nombre": "Carlos Gómez", "email": "carlos@colab.com", "ventas": 12, "estado": "Activo"}
    ],
    "comercios": [
        {
            "id": 1,
            "nombre": "Café & Bar Central",
            "categoria": "Gastronomía",
            "oferta": "20% de descuento abonando en efectivo",
            "imagen": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400",
            "ciudad": "Catamarca (Capital)",
            "estado": "Aprobado"
        },
        {
            "id": 2,
            "nombre": "Moda Urbana Store",
            "categoria": "Indumentaria",
            "oferta": "3 cuotas sin interés con tarjeta de socio",
            "imagen": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",
            "ciudad": "Catamarca (Capital)",
            "estado": "Aprobado"
        }
    ],
    "comercios_nacionales": [
        {
            "nombre": "Supermercados Yaguar / Mayorista",
            "categoria": "Supermercado Nacional",
            "oferta": "15% de ahorro en compras con membresía Max%Shop",
            "imagen": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=400",
            "ciudad": "Nacional (Todo el país)"
        },
        {
            "nombre": "Farmacias Central-Farma",
            "categoria": "Salud y Farmacia",
            "oferta": "Hasta 35% de descuento en medicamentos y perfumería",
            "imagen": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400",
            "ciudad": "Nacional (Todo el país)"
        },
        {
            "nombre": "YPF Serviclub Beneficios",
            "categoria": "Combustibles y Estaciones",
            "oferta": "Acumulables con puntos y descuentos directos en boxes",
            "imagen": "https://images.unsplash.com/photo-1527018270360-1e82f87aef2e?w=400",
            "ciudad": "Nacional (Todo el país)"
        }
    ]
}

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, ciudad_filtro: str = "Catamarca (Capital)", mensaje: str = None):
    pozo_actual = DB_MOCK["pozo_acumulado"]
    
    # Filtrar comercios locales o mostrar nacionales si está vacío
    comercios_filtrados = [c for c in DB_MOCK["comercios"] if ciudad_filtro.lower() in c["ciudad"].lower()]
    
    lista_comercios_html = ""
    if len(comercios_filtrados) > 0:
        for com in comercios_filtrados:
            lista_comercios_html += f"""
            <div class="bg-[#101833] border border-slate-800 rounded-3xl overflow-hidden shadow-2xl hover:border-orange-500/50 transition flex flex-col justify-between">
                <img src="{com['imagen']}" alt="{com['nombre']}" class="w-full h-48 object-cover opacity-90">
                <div class="p-6 space-y-3 flex-1 flex flex-col justify-between">
                    <div class="space-y-1.5">
                        <span class="text-[10px] font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-md uppercase border border-orange-500/20">{com['categoria']}</span>
                        <h4 class="text-lg font-black text-white">{com['nombre']}</h4>
                        <p class="text-xs text-slate-300">🔥 <b>Beneficio:</b> {com['oferta']}</p>
                    </div>
                    <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                        <span>📍 {com['ciudad']}</span>
                        <span class="text-emerald-400 font-bold">Activo en Red</span>
                    </div>
                </div>
            </div>
            """
    else:
        # Si la ciudad no tiene comercios locales, mostramos la red nacional de respaldo solicitada
        lista_comercios_html = f"""
        <div class="col-span-full bg-orange-500/10 border border-orange-500/30 p-6 rounded-3xl text-center space-y-2 mb-4">
            <h4 class="text-white font-bold text-sm">ℹ️ No hay comercios locales registrados aún en {ciudad_filtro}.</h4>
            <p class="text-xs text-slate-300">¡Pero tienes cobertura total habilitada con nuestra Red de Comercios y Supermercados Nacionales!</p>
        </div>
        """
        for com in DB_MOCK["comercios_nacionales"]:
            lista_comercios_html += f"""
            <div class="bg-[#101833] border border-slate-800 rounded-3xl overflow-hidden shadow-2xl hover:border-orange-500/50 transition flex flex-col justify-between">
                <img src="{com['imagen']}" alt="{com['nombre']}" class="w-full h-48 object-cover opacity-90">
                <div class="p-6 space-y-3 flex-1 flex flex-col justify-between">
                    <div class="space-y-1.5">
                        <span class="text-[10px] font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-md uppercase border border-blue-500/20">{com['categoria']}</span>
                        <h4 class="text-lg font-black text-white">{com['nombre']}</h4>
                        <p class="text-xs text-slate-300">🔥 <b>Beneficio:</b> {com['oferta']}</p>
                    </div>
                    <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                        <span>🌐 {com['ciudad']}</span>
                        <span class="text-emerald-400 font-bold">Cobertura Nacional</span>
                    </div>
                </div>
            </div>
            """

    alerta_box = ""
    if mensaje:
        alerta_box = f"""
        <div class="bg-orange-500/20 border border-orange-500 text-orange-300 px-6 py-4 rounded-2xl font-bold text-sm text-center shadow-2xl animate-pulse">
            ✨ {mensaje}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Club de Beneficios y Cobertura Nacional</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0A1128; }}
        ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 4px; }}
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- BARRA SUPERIOR CON CIUDAD DETECTADA Y BUSCADOR -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-3 px-4 sm:px-8 flex flex-col lg:flex-row justify-between items-center gap-4 border-b border-slate-800">
        <div class="flex items-center gap-3 w-full lg:w-auto justify-between lg:justify-start">
            <span class="font-black text-orange-400 flex items-center gap-1.5 text-sm">📍 Ciudad Actual: <span id="lblCiudadActiva" class="text-white underline">{ciudad_filtro}</span></span>
            <div class="flex items-center gap-2">
                <input type="text" id="inputBuscadorCiudad" placeholder="Buscar ciudad (Ej: Córdoba, Río Tercero)..." class="bg-slate-900 border border-slate-700 text-white text-xs rounded-xl px-3 py-1.5 outline-none focus:border-orange-500 w-48 sm:w-60">
                <button onclick="buscarCiudadManual()" class="bg-orange-500 hover:bg-orange-400 text-slate-950 font-bold px-3 py-1.5 rounded-xl transition">Ir</button>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <div class="relative group">
                <button class="text-xs font-bold bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-xl text-slate-200 border border-slate-700 flex items-center gap-1.5 shadow">
                    👥 Accesos y Roles ▾
                </button>
                <div class="absolute right-0 mt-2 w-56 bg-[#101833] border border-slate-700 rounded-2xl shadow-2xl hidden group-hover:block z-50 p-2 space-y-1">
                    <a href="/comercio/validar" class="block px-4 py-3 text-xs text-slate-300 hover:bg-slate-800 rounded-xl transition font-bold">🛡️ Panel Comercio / Colaboradores</a>
                    <a href="/admin" class="block px-4 py-3 text-xs text-orange-400 hover:bg-slate-800 rounded-xl font-bold transition">⚙️ Panel Administrador (Super)</a>
                </div>
            </div>
            <button onclick="abrirModalRegistro()" class="text-xs font-bold bg-orange-500 hover:bg-orange-400 text-slate-950 px-5 py-2 rounded-xl uppercase shadow-lg transition">Registrarse / Ingresar</button>
        </div>
    </div>

    <!-- MAPA INTERACTIVO GIGANTE Y ELEGANTE -->
    <div class="w-full bg-[#070C1E] border-b border-slate-800 py-4 px-6">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <span class="text-orange-400 font-black text-sm flex items-center gap-2">🗺️ Mapa de Red Georreferenciada Activa:</span>
                <span class="text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 font-bold">🟢 GPS Sincronizado</span>
            </div>
            <div class="flex flex-wrap gap-2 text-xs">
                <button onclick="cambiarCiudadSelect('Catamarca (Capital)')" class="bg-slate-900 hover:bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-xl font-bold text-slate-300 transition">Catamarca</button>
                <button onclick="cambiarCiudadSelect('Córdoba')" class="bg-slate-900 hover:bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-xl font-bold text-slate-300 transition">Córdoba</button>
                <button onclick="cambiarCiudadSelect('Río Tercero')" class="bg-slate-900 hover:bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-xl font-bold text-slate-300 transition">Río Tercero</button>
                <button onclick="cambiarCiudadSelect('Buenos Aires')" class="bg-slate-900 hover:bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-xl font-bold text-slate-300 transition">Buenos Aires</button>
            </div>
        </div>
        <!-- Contenedor Visual de Mapa Grande Estilo App -->
        <div class="max-w-7xl mx-auto mt-3 h-36 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-2xl flex items-center justify-center relative overflow-hidden shadow-inner">
            <div class="absolute inset-0 opacity-20 bg-[radial-gradient(#f97316_1px,transparent_1px)] [background-size:16px_16px]"></div>
            <div class="text-center z-10 space-y-1">
                <p class="text-xs text-orange-400 font-bold uppercase tracking-widest">Radar de Comercios y Cobertura Activa</p>
                <h3 class="text-lg font-black text-white">Explorando red para: <span class="text-orange-400">{ciudad_filtro}</span></h3>
                <p class="text-[11px] text-slate-400">Haga clic en cualquier zona o busque arriba para cambiar de localidad al instante.</p>
            </div>
        </div>
    </div>

    <!-- HEADER / LOGO OFICIAL -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-3">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white flex items-center gap-2">
                    Max<span class="text-orange-500">%</span>Shop
                    <span class="text-[10px] bg-orange-500/10 text-orange-400 border border-orange-500/20 px-2.5 py-1 rounded-md uppercase hidden sm:inline font-bold">Descuentos y Cobertura</span>
                </div>
            </div>
            <nav class="hidden md:flex items-center space-x-6 text-xs font-bold text-slate-300">
                <a href="#comercios" class="hover:text-orange-400 transition">Comercios Adheridos</a>
                <a href="#bolillero" class="hover:text-orange-400 transition">Bolillero Dominical</a>
                <a href="#suscripcion" class="hover:text-orange-400 transition">Planes y Cobertura</a>
            </nav>
            <div class="flex items-center space-x-3">
                <a href="#suscripcion" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs px-5 py-2.5 rounded-xl uppercase shadow-lg transition">
                    Suscribirse $10k+
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16">
        
        {alerta_box}

        <!-- HERO / BANNER PRINCIPAL OFICIAL SOLICITADO (DEBAJO DE LA BARRA DE TAREAS) -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-6 md:p-12 shadow-2xl space-y-8 text-center">
            <div class="max-w-3xl mx-auto space-y-4">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-4 py-2 rounded-full border border-orange-500/20 uppercase shadow">
                    <span>🔥</span> <span>Club de Beneficios, Cobertura y Sorteos Semanales</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Pozo Acumulado <span class="text-orange-500">${pozo_actual:,.0f}</span>
                </h1>
                <p class="text-slate-300 text-sm leading-relaxed">Disfruta de la red de comercios más grande, obtén cobertura de hasta 30 millones y participa por el bolillero dominical.</p>
            </div>

            <!-- Imagen principal cargada perfectamente -->
            <div class="rounded-3xl overflow-hidden border border-slate-700 shadow-2xl relative bg-slate-900 max-h-[500px]">
                <img src="/static/uploads/hero_banner.png" alt="Max%Shop Banner" class="w-full h-full object-cover" onerror="this.src='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200'">
            </div>
        </div>

        <!-- SECCIÓN DE COMERCIOS ADHERIDOS Y NACIONALES -->
        <div id="comercios" class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                <div class="space-y-2">
                    <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Red Georreferenciada</span>
                    <h3 class="text-3xl font-black text-white">Comercios en <span class="text-orange-400">{ciudad_filtro}</span></h3>
                    <p class="text-xs text-slate-400">Cupones instantáneos y beneficios activos con tu membresía.</p>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {lista_comercios_html}
            </div>
        </div>

    </main>

    <!-- MODAL DE REGISTRO / SUSCRIPCIÓN A PANTALLA COMPLETA (ESTILO APP CÓMODO) -->
    <div id="modalRegistro" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md hidden z-50 flex items-center justify-center p-4 overflow-y-auto">
        <div class="bg-[#101833] border border-slate-700 rounded-3xl max-w-xl w-full p-8 sm:p-10 shadow-2xl space-y-6 relative my-8">
            <button onclick="cerrarModalRegistro()" class="absolute top-6 right-6 text-slate-400 hover:text-white text-xl font-bold bg-slate-900 w-10 h-10 rounded-full flex items-center justify-center border border-slate-800">✕</button>
            <div class="text-center space-y-2">
                <span class="text-[10px] font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Registro Seguro App</span>
                <h3 class="text-3xl font-black text-white">Únete a Max%Shop</h3>
                <p class="text-xs text-slate-300">Completa tus datos para activar geolocalización, notificaciones y cupones exclusivos al instante.</p>
            </div>
            <form action="/registrar-usuario" method="POST" class="space-y-4">
                <div>
                    <label class="text-xs font-bold text-slate-300">Nombre y Apellido</label>
                    <input type="text" name="nombre" required placeholder="Ej: María Gómez" class="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-xs text-white mt-1.5 outline-none focus:border-orange-500 shadow-inner">
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs font-bold text-slate-300">DNI</label>
                        <input type="text" name="dni" required placeholder="Ej: 35123456" class="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-xs text-white mt-1.5 outline-none focus:border-orange-500 shadow-inner">
                    </div>
                    <div>
                        <label class="text-xs font-bold text-slate-300">Teléfono (WhatsApp)</label>
                        <input type="text" name="telefono" required placeholder="Ej: 3834556677" class="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-xs text-white mt-1.5 outline-none focus:border-orange-500 shadow-inner">
                    </div>
                </div>
                <div>
                    <label class="text-xs font-bold text-slate-300">Correo Electrónico (Notificaciones)</label>
                    <input type="email" name="email" required placeholder="correo@ejemplo.com" class="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-xs text-white mt-1.5 outline-none focus:border-orange-500 shadow-inner">
                </div>
                <div>
                    <label class="text-xs font-bold text-slate-300">Seleccionar Nivel de Suscripción / Cobertura</label>
                    <select name="suscripcion" class="w-full bg-slate-900 border border-slate-700 rounded-2xl px-4 py-3 text-xs text-orange-400 font-bold mt-1.5 outline-none shadow-inner">
                        <option value="Gratis">Registro Gratis (Navegación y Cupones)</option>
                        <option value="10M">Suscripción $10.000 (Cobertura $10 Millones)</option>
                        <option value="20M">Suscripción $20.000 (Cobertura $20 Millones)</option>
                        <option value="30M">Suscripción $30.000 (Cobertura $30 Millones)</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black py-4 rounded-2xl text-xs uppercase shadow-2xl transition tracking-wide">
                    💳 Pagar y Activar Cuenta (Pasarela Segura)
                </button>
            </form>
        </div>
    </div>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800 bg-[#070C1E] mt-20 py-10 text-center text-xs text-slate-500">
        <p>Max%Shop © 2026 - Cobertura Georreferenciada Nacional. Todos los derechos reservados.</p>
    </footer>

    <script>
        function abrirModalRegistro() {{
            document.getElementById('modalRegistro').classList.remove('hidden');
        }}
        function cerrarModalRegistro() {{
            document.getElementById('modalRegistro').classList.add('hidden');
        }}
        function cambiarCiudadSelect(ciudad) {{
            window.location.href = "/?ciudad_filtro=" + encodeURIComponent(ciudad);
        }}
        function buscarCiudadManual() {{
            const val = document.getElementById('inputBuscadorCiudad').value.trim();
            if(val) {{
                window.location.href = "/?ciudad_filtro=" + encodeURIComponent(val);
            }} else {{
                alert("Por favor ingresa una ciudad para buscar.");
            }}
        }}
    </script>
</body>
</html>
"""

@app.post("/registrar-usuario")
async def registrar_usuario(
    nombre: str = Form(...),
    dni: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    suscripcion: str = Form(...)
):
    DB_MOCK["usuarios"].append({
        "dni": dni,
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "ciudad": "Catamarca (Capital)",
        "suscripcion": suscripcion
    })
    mensaje = f"¡Registro exitoso, {nombre}! Tu cuenta y notificaciones han sido activadas correctamente."
    return RedirectResponse(url=f"/?mensaje={urllib.parse.quote(mensaje)}", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin)):
    usuarios_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-4 text-white font-bold">{u['nombre']}</td>
            <td class="p-4 text-slate-300 font-mono">{u['dni']}</td>
            <td class="p-4 text-slate-300">{u['telefono']}</td>
            <td class="p-4 text-orange-400">{u['email']}</td>
            <td class="p-4 text-emerald-400 font-bold">{u['suscripcion']}</td>
        </tr>""" for u in DB_MOCK["usuarios"]])

    comercios_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-4 text-white font-bold">{c['nombre']}</td>
            <td class="p-4 text-slate-300">{c['categoria']}</td>
            <td class="p-4 text-emerald-400 font-bold">{c['estado']}</td>
            <td class="p-4 text-right">
                <span class="text-orange-400 font-bold cursor-pointer hover:underline">Gestionar</span>
            </td>
        </tr>""" for c in DB_MOCK["comercios"]])

    colaboradores_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-4 text-white font-bold">{col['nombre']}</td>
            <td class="p-4 text-slate-300">{col['email']}</td>
            <td class="p-4 text-orange-400 font-mono font-bold">{col['ventas']} ventas</td>
            <td class="p-4 text-emerald-400">{col['estado']}</td>
        </tr>""" for col in DB_MOCK["colaboradores"]])

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel de Administración - Max%Shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#070C1E] text-slate-100 min-h-screen p-6 sm:p-12 font-sans">
    <div class="max-w-7xl mx-auto space-y-8">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl">
            <div>
                <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Control Absoluto</span>
                <h1 class="text-2xl sm:text-4xl font-black text-white mt-2">Panel de Administración Max%Shop</h1>
            </div>
            <a href="/" class="bg-slate-800 hover:bg-slate-700 px-6 py-3 rounded-2xl text-xs font-bold text-white border border-slate-700 transition shadow">← Volver al Sitio Web</a>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Total Socios Registrados</span>
                <h3 class="text-4xl font-black text-white">{len(DB_MOCK["usuarios"])}</h3>
            </div>
            <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Comercios Activos en Red</span>
                <h3 class="text-4xl font-black text-orange-400">{len(DB_MOCK["comercios"])}</h3>
            </div>
            <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Pozo Acumulado Actual</span>
                <h3 class="text-4xl font-black text-emerald-400">${DB_MOCK["pozo_acumulado"]:,.0f}</h3>
            </div>
        </div>

        <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-xl font-black text-white flex items-center gap-2">👥 Base de Datos Completa de Socios</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-4">Nombre</th><th class="p-4">DNI</th><th class="p-4">Teléfono</th><th class="p-4">Correo</th><th class="p-4">Suscripción</th></tr></thead>
                    <tbody>{usuarios_filas}</tbody>
                </table>
            </div>
        </div>

        <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-xl font-black text-white flex items-center gap-2">🏪 Control de Comercios Adheridos</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-4">Comercio</th><th class="p-4">Categoría</th><th class="p-4">Estado</th><th class="p-4 text-right">Acciones</th></tr></thead>
                    <tbody>{comercios_filas}</tbody>
                </table>
            </div>
        </div>

        <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-xl font-black text-white flex items-center gap-2">🛡️ Control de Colaboradores y Ventas</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-4">Colaborador</th><th class="p-4">Correo</th><th class="p-4">Ventas Registradas</th><th class="p-4">Estado</th></tr></thead>
                    <tbody>{colaboradores_filas}</tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>"""

@app.get("/comercio/validar", response_class=HTMLResponse)
async def validar_comercio():
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel Comercio y Colaboradores - Max%Shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 sm:p-12 flex items-center justify-center font-sans">
    <div class="w-full max-w-xl bg-[#101833] border border-slate-800 rounded-3xl p-8 sm:p-12 shadow-2xl space-y-8 text-center relative">
        <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-4 py-1.5 rounded-full uppercase border border-orange-500/20">Acceso Restringido Comercial</span>
        <div class="space-y-2">
            <h1 class="text-3xl font-black text-white">Panel de Comercio y Colaboradores</h1>
            <p class="text-xs text-slate-300">Valida socios activos en la red y registra consumos o números para el sorteo dominical en pantalla completa.</p>
        </div>
        <div class="bg-[#0A1128] p-8 rounded-3xl border border-slate-700 text-left space-y-4 shadow-inner">
            <label class="text-xs font-bold text-slate-300">Validar DNI de Socio / Cliente:</label>
            <input type="text" placeholder="Ingrese DNI del cliente..." class="w-full bg-slate-900 border border-slate-700 px-5 py-3.5 rounded-2xl text-xs text-white outline-none focus:border-orange-500 shadow-inner">
            <button onclick="alert('Socio verificado correctamente en la red Max%Shop.')" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-4 rounded-2xl text-xs uppercase mt-2 transition shadow-xl tracking-wide">Verificar Estado en Red</button>
        </div>
        <a href="/" class="block text-xs text-slate-400 hover:text-white transition font-bold">← Volver al inicio principal</a>
    </div>
</body>
</html>"""
