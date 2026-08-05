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
    version="21.0.0"
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

# Base de datos ampliada estructurada por roles y registros
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
        }
    ],
    "apuestas_semanales": [
        {"id": 1, "dni": "12345678", "nombre": "Juan Pérez", "numeros": [7, 14, 22, 33, 41], "comercio": "App Digital Directa", "fecha": "2026-06-07"}
    ]
}

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, mensaje: str = None):
    pozo_actual = DB_MOCK["pozo_acumulado"]
    
    # Renderizar comercios adheridos
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
        <div class="bg-orange-500/10 border border-orange-500 text-orange-400 px-4 py-3 rounded-xl font-bold text-sm text-center animate-pulse">
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

    <!-- TOP BAR CON SELECTOR DE CIUDAD Y ACCESOS RÁPIDOS -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-2.5 px-4 flex flex-col sm:flex-row justify-between items-center gap-3 border-b border-slate-800">
        <div class="flex items-center gap-3">
            <span class="font-bold text-slate-300">📍 Ciudad:</span>
            <select class="bg-slate-900 border border-slate-700 text-orange-400 text-xs rounded-lg px-3 py-1 font-bold outline-none">
                <option>Catamarca (Capital)</option>
                <option>Valle Viejo</option>
                <option>Fray Mamerto Esquiú</option>
                <option>San Fernando del Valle</option>
            </select>
        </div>
        <div class="flex items-center gap-3">
            <div class="relative group">
                <button class="text-[11px] font-bold bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-full text-slate-200 border border-slate-700 flex items-center gap-1">
                    👥 Accesos y Roles ▾
                </button>
                <div class="absolute right-0 mt-1 w-48 bg-[#101833] border border-slate-700 rounded-xl shadow-2xl hidden group-hover:block z-50 p-2 space-y-1">
                    <a href="/comercio/validar" class="block px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 rounded-lg">🛡️ Panel Comercio</a>
                    <a href="/admin" class="block px-3 py-2 text-xs text-orange-400 hover:bg-slate-800 rounded-lg font-bold">⚙️ Panel Administrador</a>
                </div>
            </div>
            <a href="#registro" class="text-[11px] font-bold bg-orange-500 text-slate-950 px-4 py-1.5 rounded-full uppercase shadow-md">Registrarse / Ingresar</a>
        </div>
    </div>

    <!-- MAPA HORIZONTAL FINO Y SUTIL -->
    <div class="w-full bg-[#070C1E] border-b border-slate-800 py-2 px-4 flex items-center justify-between text-[11px] text-slate-400">
        <div class="flex items-center gap-2 overflow-x-auto whitespace-nowrap">
            <span class="text-orange-400 font-bold">🗺️ Mapa de Red Activa:</span>
            <span class="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">Centro Comercial (Catamarca)</span>
            <span class="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">Zona Norte</span>
            <span class="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">Zona Sur</span>
        </div>
        <span class="hidden md:inline text-emerald-400 font-bold">● Geolocalización GPS Activa</span>
    </div>

    <!-- HEADER / LOGO OFICIAL -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-3">
                <!-- Espacio preparado para logo oficial desde GitHub o estáticos -->
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
                <a href="#suscripcion" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs px-4 py-2.5 rounded-xl uppercase shadow-lg">
                    Suscribirse $10k+
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16">
        
        <!-- HERO CON IMAGEN PRINCIPAL -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-6 md:p-12 shadow-2xl space-y-8">
            <div class="text-center max-w-3xl mx-auto space-y-4">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-3.5 py-1.5 rounded-full border border-orange-500/20 uppercase">
                    <span>🔥</span> <span>Club de Beneficios, Cobertura y Sorteos Semanales</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Pozo Acumulado <span class="text-orange-500">${pozo_actual:,.0f}</span>
                </h1>
                <p class="text-slate-300 text-sm leading-relaxed">Disfruta de la red de comercios más grande, obtén cobertura de hasta 30 millones y participa por el bolillero dominical.</p>
            </div>

            <!-- Imagen principal de la app (Banner que adjuntaste) -->
            <div class="rounded-2xl overflow-hidden border border-slate-700 shadow-2xl relative">
                <img src="/static/uploads/hero_banner.png" alt="Max%Shop Banner" class="w-full h-auto object-cover max-h-[450px]" onerror="this.src='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200'">
            </div>
        </div>

        {alerta_box}

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

    <!-- FOOTER -->
    <footer class="border-t border-slate-800 bg-[#070C1E] mt-20 py-10 text-center text-xs text-slate-500">
        <p>Max%Shop © 2026 - Catamarca (Capital), Argentina. Todos los derechos reservados.</p>
    </footer>
</body>
</html>
"""

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin)):
    usuarios_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs">
            <td class="p-3 text-white font-bold">{u['nombre']}</td>
            <td class="p-3 text-slate-300 font-mono">{u['dni']}</td>
            <td class="p-3 text-slate-300">{u['telefono']}</td>
            <td class="p-3 text-orange-400">{u['email']}</td>
            <td class="p-3 text-emerald-400">{u['ciudad']}</td>
        </tr>""" for u in DB_MOCK["usuarios"]])

    return f"""<!DOCTYPE html>
<html lang="es">
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#070C1E] text-slate-100 min-h-screen p-8">
    <div class="max-w-6xl mx-auto space-y-6">
        <div class="flex justify-between items-center">
            <h1 class="text-2xl font-black">Panel de Administración Exclusivo (Super-Admin)</h1>
            <a href="/" class="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-xl text-xs text-white">← Volver al Sitio</a>
        </div>
        <div class="bg-[#101833] p-6 rounded-3xl border border-slate-800 space-y-4 shadow-2xl">
            <h2 class="text-lg font-bold text-orange-400">Base de Datos de Usuarios Registrados</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-3">Nombre</th><th class="p-3">DNI</th><th class="p-3">Teléfono</th><th class="p-3">Correo</th><th class="p-3">Ciudad</th></tr></thead>
                    <tbody>{usuarios_filas}</tbody>
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
<head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen p-6 flex items-center justify-center">
    <div class="w-full max-w-md bg-[#101833] border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6 text-center">
        <h1 class="text-2xl font-black text-white">Panel de Comercio / Colaborador</h1>
        <p class="text-xs text-slate-400">Herramientas de validación de socios y registro de ventas locales (Acceso restringido sin privilegios de administrador).</p>
        <div class="bg-[#0A1128] p-4 rounded-xl border border-slate-700 text-left space-y-2">
            <label class="text-xs font-bold text-slate-300">Validar DNI de Socio:</label>
            <input type="text" placeholder="Ingrese DNI..." class="w-full bg-slate-900 border border-slate-700 px-3 py-2 rounded-lg text-xs text-white">
            <button class="w-full bg-emerald-500 text-slate-950 font-bold py-2 rounded-lg text-xs uppercase mt-2">Verificar Estado en Red</button>
        </div>
        <a href="/" class="block text-xs text-slate-400 hover:text-white">← Volver al inicio</a>
    </div>
</body>
</html>"""
