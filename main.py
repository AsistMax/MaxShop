import os
from fastapi import FastAPI, HTTPException, Depends, status, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

ADMIN_USER = "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026")

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Bolillero Semanal",
    version="22.0.0"
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

# Base de datos en memoria completa y estructurada
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
    "apuestas_semanales": [
        {"id": 1, "dni": "12345678", "nombre": "Juan Pérez", "numeros": [7, 14, 22, 33, 41], "comercio": "App Digital Directa", "fecha": "2026-06-07"}
    ]
}

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, mensaje: str = None):
    pozo_actual = DB_MOCK["pozo_acumulado"]
    
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
                    <span>📍 {com['ciudad']}</span>
                    <span class="text-emerald-400 font-bold">Activo en la Red</span>
                </div>
            </div>
        </div>
        """

    alerta_box = ""
    if mensaje:
        alerta_box = f"""
        <div class="bg-orange-500/10 border border-orange-500 text-orange-400 px-6 py-4 rounded-2xl font-bold text-sm text-center shadow-xl animate-bounce">
            ✨ {mensaje}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Descuentos de Locos y Bolillero Semanal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0A1128; }}
        ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 4px; }}
        .bolilla {{
            width: 36px; height: 36px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ffedd5, #f97316);
            color: #0f172a; font-weight: 900; font-size: 14px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.4), inset -2px -2px 4px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- TOP BAR DE NAVEGACIÓN Y CIUDADES -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-3 px-4 sm:px-8 flex flex-col md:flex-row justify-between items-center gap-4 border-b border-slate-800">
        <div class="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
            <span class="font-bold text-slate-300 flex items-center gap-1">📍 Ciudad:</span>
            <select id="selectorCiudad" onchange="cambiarCiudad(this.value)" class="bg-slate-900 border border-slate-700 text-orange-400 text-xs rounded-xl px-4 py-2 font-bold outline-none shadow-inner">
                <option value="Catamarca">Catamarca (Capital)</option>
                <option value="Valle Viejo">Valle Viejo</option>
                <option value="Fray Mamerto Esquiú">Fray Mamerto Esquiú</option>
                <option value="Tinogasta">Tinogasta</option>
                <option value="Chilecito">Chilecito</option>
            </select>
        </div>
        <div class="flex items-center gap-3">
            <div class="relative group">
                <button class="text-xs font-bold bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-xl text-slate-200 border border-slate-700 flex items-center gap-1.5 shadow">
                    👥 Accesos y Roles ▾
                </button>
                <div class="absolute right-0 mt-2 w-52 bg-[#101833] border border-slate-700 rounded-2xl shadow-2xl hidden group-hover:block z-50 p-2 space-y-1">
                    <a href="/comercio/validar" class="block px-3 py-2.5 text-xs text-slate-300 hover:bg-slate-800 rounded-xl transition">🛡️ Panel Comercio / Colaborador</a>
                    <a href="/admin" class="block px-3 py-2.5 text-xs text-orange-400 hover:bg-slate-800 rounded-xl font-bold transition">⚙️ Panel Administrador (Super)</a>
                </div>
            </div>
            <button onclick="abrirModalRegistro()" class="text-xs font-bold bg-orange-500 hover:bg-orange-400 text-slate-950 px-5 py-2 rounded-xl uppercase shadow-lg transition">Registrarse / Ingresar</button>
        </div>
    </div>

    <!-- MAPA HORIZONTAL ELEGANTE Y INTERACTIVO -->
    <div class="w-full bg-[#070C1E] border-b border-slate-800 py-3 px-6 flex flex-col md:flex-row items-center justify-between text-xs text-slate-300 gap-3">
        <div class="flex items-center gap-3 overflow-x-auto whitespace-nowrap w-full md:w-auto">
            <span class="text-orange-400 font-black flex items-center gap-1">🗺️ Mapa de Red Georeferenciada:</span>
            <span onclick="filtrarZona('Centro')" class="cursor-pointer bg-slate-900 hover:bg-slate-800 px-3 py-1 rounded-lg border border-slate-700 transition">Centro Comercial</span>
            <span onclick="filtrarZona('Norte')" class="cursor-pointer bg-slate-900 hover:bg-slate-800 px-3 py-1 rounded-lg border border-slate-700 transition">Zona Norte</span>
            <span onclick="filtrarZona('Sur')" class="cursor-pointer bg-slate-900 hover:bg-slate-800 px-3 py-1 rounded-lg border border-slate-700 transition">Zona Sur</span>
            <span onclick="filtrarZona('Oeste')" class="cursor-pointer bg-slate-900 hover:bg-slate-800 px-3 py-1 rounded-lg border border-slate-700 transition">Zona Oeste</span>
        </div>
        <div class="flex items-center gap-2 text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20">
            <span>🟢 Geolocalización GPS Activa</span>
        </div>
    </div>

    <!-- HEADER / LOGO OFICIAL -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-3">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white flex items-center gap-2">
                    Max<span class="text-orange-500">%</span>Shop
                    <span class="text-[10px] bg-orange-500/10 text-orange-400 border border-orange-500/20 px-2 py-0.5 rounded-md uppercase hidden sm:inline">Descuentos de Locos</span>
                </div>
            </div>
            <nav class="hidden md:flex items-center space-x-6 text-xs font-bold text-slate-300">
                <a href="#comprar" class="hover:text-orange-400 transition">Comprar Números</a>
                <a href="#bolillero" class="hover:text-orange-400 transition">Bolillero Dominical</a>
                <a href="#comercios" class="hover:text-orange-400 transition">Comercios Adheridos</a>
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

        <!-- HERO CON LOGO Y BANNER PRINCIPAL SOLICITADO -->
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

            <!-- Imagen principal cargada y ajustada -->
            <div class="rounded-2xl overflow-hidden border border-slate-700 shadow-2xl relative bg-slate-900">
                <img src="/static/uploads/hero_banner.png" alt="Max%Shop Banner" class="w-full h-auto object-cover max-h-[500px]" onerror="this.src='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200'">
            </div>
        </div>

        <!-- SECCIÓN DE COMERCIOS ADHERIDOS -->
        <div id="comercios" class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                <div class="space-y-2">
                    <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Red Comercial Catamarca</span>
                    <h3 class="text-3xl font-black text-white">Comercios Adheridos</h3>
                    <p class="text-xs text-slate-400">Navega por los comercios y obtén cupones instantáneos de descuento.</p>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {comercios_html}
            </div>
        </div>

    </main>

    <!-- MODAL DE REGISTRO / SUSCRIPCIÓN / MERCADO PAGO INTEGRADO -->
    <div id="modalRegistro" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md hidden z-50 flex items-center justify-center p-4">
        <div class="bg-[#101833] border border-slate-700 rounded-3xl max-w-lg w-full p-8 shadow-2xl space-y-6 relative">
            <button onclick="cerrarModalRegistro()" class="absolute top-5 right-5 text-slate-400 hover:text-white text-lg font-bold">✕</button>
            <div class="text-center space-y-2">
                <h3 class="text-2xl font-black text-white">Registro en Max%Shop</h3>
                <p class="text-xs text-slate-300">Completa tus datos para activar geolocalización, notificaciones y cupones exclusivos.</p>
            </div>
            <form action="/registrar-usuario" method="POST" class="space-y-4">
                <div>
                    <label class="text-xs font-bold text-slate-300">Nombre y Apellido</label>
                    <input type="text" name="nombre" required placeholder="Ej: María Gómez" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white mt-1 outline-none focus:border-orange-500">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs font-bold text-slate-300">DNI</label>
                        <input type="text" name="dni" required placeholder="Ej: 35123456" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white mt-1 outline-none focus:border-orange-500">
                    </div>
                    <div>
                        <label class="text-xs font-bold text-slate-300">Teléfono (WhatsApp)</label>
                        <input type="text" name="telefono" required placeholder="Ej: 3834556677" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white mt-1 outline-none focus:border-orange-500">
                    </div>
                </div>
                <div>
                    <label class="text-xs font-bold text-slate-300">Correo Electrónico (Notificaciones)</label>
                    <input type="email" name="email" required placeholder="correo@ejemplo.com" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white mt-1 outline-none focus:border-orange-500">
                </div>
                <div>
                    <label class="text-xs font-bold text-slate-300">Seleccionar Nivel de Suscripción / Cobertura</label>
                    <select name="suscripcion" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-orange-400 font-bold mt-1 outline-none">
                        <option value="Gratis">Registro Gratis (Navegación y Cupones)</option>
                        <option value="10M">Suscripción $10.000 (Cobertura $10 Millones)</option>
                        <option value="20M">Suscripción $20.000 (Cobertura $20 Millones)</option>
                        <option value="30M">Suscripción $30.000 (Cobertura $30 Millones)</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black py-3 rounded-xl text-xs uppercase shadow-xl transition">
                    💳 Pagar y Activar Cuenta (Pasarela Segura)
                </button>
            </form>
        </div>
    </div>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800 bg-[#070C1E] mt-20 py-10 text-center text-xs text-slate-500">
        <p>Max%Shop © 2026 - Catamarca (Capital), Argentina. Todos los derechos reservados.</p>
    </footer>

    <script>
        function abrirModalRegistro() {{
            document.getElementById('modalRegistro').classList.remove('hidden');
        }}
        function cerrarModalRegistro() {{
            document.getElementById('modalRegistro').classList.add('hidden');
        }}
        function cambiarCiudad(ciudad) {{
            alert("Ciudad seleccionada: " + ciudad + ". Actualizando red de comercios cercanos...");
        }}
        function filtrarZona(zona) {{
            alert("Filtrando comercios en: " + zona);
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
    # Guardar en base de datos en memoria
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
            <td class="p-3.5 text-white font-bold">{u['nombre']}</td>
            <td class="p-3.5 text-slate-300 font-mono">{u['dni']}</td>
            <td class="p-3.5 text-slate-300">{u['telefono']}</td>
            <td class="p-3.5 text-orange-400">{u['email']}</td>
            <td class="p-3.5 text-emerald-400 font-bold">{u['suscripcion']}</td>
        </tr>""" for u in DB_MOCK["usuarios"]])

    comercios_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-3.5 text-white font-bold">{c['nombre']}</td>
            <td class="p-3.5 text-slate-300">{c['categoria']}</td>
            <td class="p-3.5 text-emerald-400 font-bold">{c['estado']}</td>
            <td class="p-3.5 text-right">
                <span class="text-orange-400 font-bold cursor-pointer hover:underline">Gestionar</span>
            </td>
        </tr>""" for c in DB_MOCK["comercios"]])

    colaboradores_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-3.5 text-white font-bold">{col['nombre']}</td>
            <td class="p-3.5 text-slate-300">{col['email']}</td>
            <td class="p-3.5 text-orange-400 font-mono font-bold">{col['ventas']} ventas</td>
            <td class="p-3.5 text-emerald-400">{col['estado']}</td>
        </tr>""" for col in DB_MOCK["colaboradores"]])

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel de Administración - Max%Shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#070C1E] text-slate-100 min-h-screen p-6 sm:p-10 font-sans">
    <div class="max-w-7xl mx-auto space-y-8">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-[#101833] p-6 rounded-3xl border border-slate-800 shadow-2xl">
            <div>
                <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Control Absoluto</span>
                <h1 class="text-2xl sm:text-3xl font-black text-white mt-2">Panel de Administración Max%Shop</h1>
            </div>
            <a href="/" class="bg-slate-800 hover:bg-slate-700 px-5 py-2.5 rounded-xl text-xs font-bold text-white border border-slate-700 transition">← Volver al Sitio Web</a>
        </div>

        <!-- TARJETAS DE ESTADÍSTICAS -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div class="bg-[#101833] p-6 rounded-3xl border border-slate-800 shadow-xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Total Socios Registrados</span>
                <h3 class="text-3xl font-black text-white">{len(DB_MOCK["usuarios"])}</h3>
            </div>
            <div class="bg-[#101833] p-6 rounded-3xl border border-slate-800 shadow-xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Comercios Activos en Red</span>
                <h3 class="text-3xl font-black text-orange-400">{len(DB_MOCK["comercios"])}</h3>
            </div>
            <div class="bg-[#101833] p-6 rounded-3xl border border-slate-800 shadow-xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Pozo Acumulado Actual</span>
                <h3 class="text-3xl font-black text-emerald-400">${DB_MOCK["pozo_acumulado"]:,.0f}</h3>
            </div>
        </div>

        <!-- TABLA DE USUARIOS / SOCIOS -->
        <div class="bg-[#101833] p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-lg font-black text-white flex items-center gap-2">👥 Base de Datos Completa de Socios (Clientes)</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-3.5">Nombre</th><th class="p-3.5">DNI</th><th class="p-3.5">Teléfono</th><th class="p-3.5">Correo (Notificaciones)</th><th class="p-3.5">Suscripción</th></tr></thead>
                    <tbody>{usuarios_filas}</tbody>
                </table>
            </div>
        </div>

        <!-- TABLA DE COMERCIOS -->
        <div class="bg-[#101833] p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-lg font-black text-white flex items-center gap-2">🏪 Control de Comercios Adheridos</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-3.5">Comercio</th><th class="p-3.5">Categoría</th><th class="p-3.5">Estado</th><th class="p-3.5 text-right">Acciones</th></tr></thead>
                    <tbody>{comercios_filas}</tbody>
                </table>
            </div>
        </div>

        <!-- TABLA DE COLABORADORES -->
        <div class="bg-[#101833] p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-lg font-black text-white flex items-center gap-2">🛡️ Control de Colaboradores y Ventas</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-3.5">Colaborador</th><th class="p-3.5">Correo</th><th class="p-3.5">Ventas Registradas</th><th class="p-3.5">Estado</th></tr></thead>
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
    <title>Panel Comercio / Colaborador - Max%Shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex items-center justify-center font-sans">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6 text-center">
        <span class="text-[10px] font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Acceso Restringido Comercial</span>
        <h1 class="text-2xl font-black text-white">Panel de Comercio y Colaboradores</h1>
        <p class="text-xs text-slate-300">Valida socios activos en la red y registra consumos o números para el sorteo dominical.</p>
        <div class="bg-[#0A1128] p-5 rounded-2xl border border-slate-700 text-left space-y-3">
            <label class="text-xs font-bold text-slate-300">Validar DNI de Socio:</label>
            <input type="text" placeholder="Ingrese DNI del cliente..." class="w-full bg-slate-900 border border-slate-700 px-4 py-2.5 rounded-xl text-xs text-white outline-none focus:border-orange-500">
            <button onclick="alert('Socio verificado correctamente en la red Max%Shop.')" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-2.5 rounded-xl text-xs uppercase mt-2 transition shadow-lg">Verificar Estado en Red</button>
        </div>
        <a href="/" class="block text-xs text-slate-400 hover:text-white transition">← Volver al inicio principal</a>
    </div>
</body>
</html>"""
