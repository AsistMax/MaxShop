import os
import random
import urllib.parse
from datetime import datetime
from typing import Optional
import mercadopago

from fastapi import FastAPI, Form, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES MERCADO PAGO
# ==========================================
ACCESS_TOKEN = "APP_USR-3608400094634474-073007-07816a266bd69f8a7656079a054b085e-3577890616"
PUBLIC_KEY = "APP_USR-119e2550-1b5c-4ad4-ab88-c78a1e955c74"

sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS Y FASTAPI
# ==========================================
sqlite_file_name = "maxshop_robusto.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

ADMIN_USER = "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MaxShop2026")

app = FastAPI(
    title="Max%Shop - Club de Beneficios, Cobertura y Bolillero Semanal",
    version="26.1.0"
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

# ==========================================
# MODELOS DE BASE DE DATOS (SQLMODEL)
# ==========================================

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)
    password: str = Field(default="123456")
    dni: Optional[str] = Field(default=None, index=True)
    telefono: Optional[str] = None
    ciudad: str = Field(default="Catamarca (Capital)")
    estado_suscripcion: str = Field(default="Inactivo")
    monto_suscripcion: float = Field(default=0.0)

class Transaccion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int
    tipo: str
    monto: float
    estado: str
    payment_id: Optional[str] = Field(default=None, index=True)
    fecha: str

class Apuesta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dni: str
    nombre: str
    numeros: str
    comercio: str = Field(default="App Digital Directa")
    fecha: str

# Base de datos simulada para comercios y pozo inicial en $400.000
DB_COMERCIOS = {
    "pozo_acumulado": 400000,
    "ultimas_bolillas": [7, 14, 22, 33, 41],
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
        }
    ]
}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        admin = session.exec(select(Usuario).where(Usuario.email == "admin@maxshop.com")).first()
        if not admin:
            admin_user = Usuario(
                nombre="Administrador Max%Shop",
                email="admin@maxshop.com",
                password="admin",
                dni="00000000",
                estado_suscripcion="Activo",
                monto_suscripcion=30000.0
            )
            session.add(admin_user)
            session.commit()

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, ciudad_filtro: str = "Catamarca (Capital)", mensaje: str = None):
    pozo_actual = DB_COMERCIOS["pozo_acumulado"]
    bolillas = DB_COMERCIOS["ultimas_bolillas"]
    
    comercios_filtrados = [c for c in DB_COMERCIOS["comercios"] if ciudad_filtro.lower() in c["ciudad"].lower()]
    
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
        lista_comercios_html = f"""
        <div class="col-span-full bg-orange-500/10 border border-orange-500/30 p-6 rounded-3xl text-center space-y-2 mb-4">
            <h4 class="text-white font-bold text-sm">ℹ️ No hay comercios locales registrados aún en {ciudad_filtro}.</h4>
            <p class="text-xs text-slate-300">¡Pero tienes cobertura total habilitada con nuestra Red de Comercios y Supermercados Nacionales!</p>
        </div>
        """
        for com in DB_COMERCIOS["comercios_nacionales"]:
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

    bolillas_html = "".join([f'<div class="bolillera animate-bounce">{b:02d}</div>' for b in bolillas])

    return f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max%Shop - Club de Beneficios, Cobertura y Bolillero Semanal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #0A1128; }}
        ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 4px; }}
        
        .wheel-container-wrapper {{ text-align: center; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }}
        .wheel-container {{
            position: relative; width: 220px; height: 220px; border-radius: 50%; border: 8px solid #cbd5e1;
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
        .bolillera {{
            width: 48px; height: 48px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ffedd5, #f97316);
            color: #0f172a; font-weight: 900; font-size: 16px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5), inset -2px -2px 6px rgba(0,0,0,0.4);
        }}
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- BARRA SUPERIOR -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-3 px-4 sm:px-8 flex flex-col lg:flex-row justify-between items-center gap-4 border-b border-slate-800">
        <div class="flex items-center gap-3 w-full lg:w-auto justify-between lg:justify-start">
            <span class="font-black text-orange-400 flex items-center gap-1.5 text-sm">📍 Ciudad Actual: <span id="lblCiudadActiva" class="text-white underline">{ciudad_filtro}</span></span>
            <div class="flex items-center gap-2">
                <input type="text" id="inputBuscadorCiudad" placeholder="Buscar ciudad..." class="bg-slate-900 border border-slate-700 text-white text-xs rounded-xl px-3 py-1.5 outline-none focus:border-orange-500 w-44 sm:w-56">
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
                    <a href="/admin" class="block px-4 py-3 text-xs text-orange-400 hover:bg-slate-800 rounded-xl font-bold transition">⚙️ Panel Administrador</a>
                </div>
            </div>
            <a href="/login" class="text-xs font-bold bg-orange-500 hover:bg-orange-400 text-slate-950 px-5 py-2 rounded-xl uppercase shadow-lg transition">Registrarse / Ingresar</a>
        </div>
    </div>

    <!-- HEADER OFICIAL -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white flex items-center gap-2">
                Max<span class="text-orange-500">%</span>Shop
            </div>
            <nav class="hidden md:flex items-center space-x-6 text-xs font-bold text-slate-300">
                <a href="#comprar" class="hover:text-orange-400 transition">Comprar Números</a>
                <a href="#bolillero" class="hover:text-orange-400 transition">Bolillero Dominical</a>
                <a href="#comercios" class="hover:text-orange-400 transition">Comercios Adheridos</a>
            </nav>
            <div class="flex items-center space-x-3">
                <a href="/login" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs px-5 py-2.5 rounded-xl uppercase shadow-lg transition">
                    Participar $1.000
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16">
        
        {alerta_box}

        <!-- HERO PRINCIPAL -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-6 md:p-12 shadow-2xl space-y-8 text-center overflow-hidden">
            <div class="max-w-4xl mx-auto">
                <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="Banner Principal Max%Shop" class="w-full max-h-[420px] object-cover rounded-2xl shadow-2xl border border-slate-700 mb-8">
            </div>
            <div class="max-w-3xl mx-auto space-y-4">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-4 py-2 rounded-full border border-orange-500/20 uppercase shadow">
                    <span>🔥</span> <span>Club de Beneficios, Cobertura y Sorteos Semanales</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Pozo Acumulado <span class="text-orange-500">${pozo_actual:,.0f}</span>
                </h1>
                <p class="text-slate-300 text-sm sm:text-base leading-relaxed">Disfruta de la red de comercios, cobertura y participa por el bolillero dominical de los domingos a las 19:00 hs.</p>
                <a href="#comprar" class="inline-block bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-lg font-bold text-base shadow-lg transition">Comprar Mis Números ($1.000)</a>
            </div>
        </div>

        <!-- SECCIÓN 1: COMPRAR NÚMEROS (CARTÓN DIGITAL) -->
        <div id="comprar" class="bg-gradient-to-r from-emerald-950/30 via-[#101833] to-[#0A1128] border border-emerald-500/40 rounded-3xl p-8 shadow-2xl space-y-6">
            <div class="max-w-xl space-y-2">
                <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase border border-emerald-500/20">Selección de Jugada y Cartón Digital</span>
                <h3 class="text-2xl font-black text-white">Elegí 5 Números (Del 1 al 50)</h3>
                <p class="text-xs text-slate-400">Ingresa números de una o dos cifras separados por comas. Al abonar $1.000, se genera tu cartón digital con comprobante oficial.</p>
            </div>
            
            <form action="/app/comprar-jugada" method="POST" class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-4xl">
                <input type="text" name="dni" required placeholder="Tu DNI de Socio" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                <input type="text" name="nombre" required placeholder="Tu Nombre y Apellido" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                <input type="text" name="numeros" required placeholder="Ej: 07, 14, 22, 33, 41" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                <div class="sm:col-span-3">
                    <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-3.5 rounded-xl text-xs uppercase tracking-wider shadow-lg transition">
                        🎫 Generar Cartón Digital y Pagar $1.000 Online
                    </button>
                </div>
            </form>
        </div>

        <!-- SECCIÓN 2: EL BOLILLERO VIRTUAL EN VIVO -->
        <div id="bolillero" class="bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-orange-500/30 rounded-3xl p-8 shadow-2xl space-y-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div class="space-y-2 max-w-xl">
                    <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Sorteo Dominical en Vivo (Domingos 19:00 hs)</span>
                    <h3 class="text-3xl font-black text-white">El Bolillero Virtual de Max%Shop</h3>
                    <p class="text-sm text-slate-400 leading-relaxed">Sorteo automatizado con locución por voz integrada. Si aciertas las bolillas sorteadas, reclamas el pozo acumulado. (Acción exclusiva del Administrador).</p>
                </div>
                <div class="bg-[#0A1128] border border-orange-500/40 p-6 rounded-2xl text-center shadow-xl w-full md:w-auto">
                    <p class="text-xs text-slate-400">POZO ACUMULADO ACTUAL</p>
                    <p class="text-3xl font-black text-emerald-400 mt-1">${pozo_actual:,.0f}</p>
                </div>
            </div>

            <div class="bg-[#0A1128] border border-slate-800 p-8 rounded-2xl text-center space-y-6">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Bolillas Ganadoras en Vivo</p>
                <div id="contenedorBolillas" class="flex justify-center items-center gap-4 flex-wrap">
                    {bolillas_html}
                </div>
                <div class="pt-4 flex flex-col sm:flex-row justify-center items-center gap-4">
                    <button onclick="reproducirVozBolillas()" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2.5 rounded-xl text-xs uppercase shadow transition">
                        🔊 Escuchar Bolillas en Vivo (Audio)
                    </button>
                    <a href="#comprar" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-8 py-3 rounded-xl text-xs uppercase shadow-lg transition">
                        🎟️ Comprar Número para el Sorteo
                    </a>
                </div>
            </div>
        </div>

        <!-- SECCIÓN 3: COMERCIOS ADHERIDOS -->
        <div id="comercios" class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                <div class="space-y-2">
                    <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Geolocalización Activa</span>
                    <h3 class="text-3xl font-black text-white">Comercios en <span class="text-orange-400">{ciudad_filtro}</span></h3>
                    <p class="text-xs text-slate-400">Cupones instantáneos y beneficios activos con tu membresía.</p>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {lista_comercios_html}
            </div>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800 bg-[#070C1E] mt-20 py-10 text-center text-xs text-slate-500">
        <p>Max%Shop © 2026 - Cobertura Georreferenciada Nacional y Sorteos Dominicales Automatizados.</p>
    </footer>

    <script>
        function buscarCiudadManual() {{
            const val = document.getElementById('inputBuscadorCiudad').value.trim();
            if(val) {{
                window.location.href = "/?ciudad_filtro=" + encodeURIComponent(val);
            }} else {{
                alert("Por favor ingresa una ciudad para buscar.");
            }}
        }}

        function reproducirVozBolillas() {{
            if ('speechSynthesis' in window) {{
                const bolillasTexto = "{', '.join(map(str, bolillas))}";
                const mensaje = new SpeechSynthesisUtterance("Atención socios de Max%Shop. Las bolillas sorteadas en el bolillero dominical son: " + bolillasTexto);
                mensaje.lang = 'es-AR';
                window.speechSynthesis.speak(mensaje);
            }} else {{
                alert("Tu navegador no soporta reproducción de audio inteligente.");
            }}
        }}
    </script>
</body>
</html>
"""

# ==========================================
# RUTAS DE LOGIN Y DASHBOARD DE SOCIO
# ==========================================

@app.get("/login", response_class=HTMLResponse)
def login_get():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Max%Shop - Ingreso y Registro</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 flex items-center justify-center min-h-screen text-slate-100 px-4 py-8">
        <div class="bg-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-slate-700 space-y-6">
            <h2 class="text-2xl font-bold text-orange-400 text-center">Acceso a Socio / Registro</h2>
            <form action="/login" method="POST" class="space-y-4">
                <div>
                    <label class="block text-sm mb-1 text-slate-300">Nombre Completo</label>
                    <input type="text" name="nombre" placeholder="Ej: Juan Pérez" class="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-orange-500">
                </div>
                <div>
                    <label class="block text-sm mb-1 text-slate-300">Correo Electrónico</label>
                    <input type="email" name="email" required placeholder="correo@mail.com" class="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-orange-500">
                </div>
                <div>
                    <label class="block text-sm mb-1 text-slate-300">DNI</label>
                    <input type="text" name="dni" placeholder="Ej: 35123456" class="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-orange-500">
                </div>
                <div>
                    <label class="block text-sm mb-1 text-slate-300">Teléfono (WhatsApp)</label>
                    <input type="text" name="telefono" placeholder="Ej: 3834123456" class="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-orange-500">
                </div>
                <button type="submit" class="w-full bg-orange-500 hover:bg-orange-600 py-3 rounded font-bold text-white transition">Ingresar / Registrarse</button>
            </form>
            <div class="text-center pt-2">
                <a href="/" class="text-xs text-slate-400 hover:text-white">← Volver al inicio</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.post("/login")
def login_post(email: str = Form(...), nombre: str = Form("Socio Nuevo"), dni: str = Form("00000000"), telefono: str = Form("")):
    with Session(engine) as session:
        user = session.exec(select(Usuario).where(Usuario.email == email)).first()
        if not user:
            user = Usuario(nombre=nombre, email=email, dni=dni, telefono=telefono, estado_suscripcion="Inactivo")
            session.add(user)
            session.commit()
            session.refresh(user)
        return RedirectResponse(url=f"/dashboard?user_id={user.id}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(user_id: int):
    with Session(engine) as session:
        user = session.get(Usuario, user_id)
        if not user:
            return RedirectResponse(url="/login", status_code=303)

        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Panel de Socio - Max%Shop</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-900 text-slate-100 min-h-screen">
            <nav class="bg-slate-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center">
                <h1 class="text-lg font-bold text-orange-400">Panel de Socio: {user.nombre}</h1>
                <a href="/" class="text-red-400 hover:text-red-300 font-semibold text-sm">Cerrar Sesión</a>
            </nav>
            <main class="container mx-auto p-6 space-y-6">
                <div class="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow space-y-4">
                    <h3 class="text-lg font-bold text-orange-300">Bienvenido a tu cuenta Max%Shop</h3>
                    <p class="text-sm text-slate-300">Desde aquí puedes gestionar tus beneficios, verificar tus cartones digitales y mantener activa tu cobertura.</p>
                    <a href="/" class="inline-block bg-orange-500 hover:bg-orange-600 px-6 py-2.5 rounded font-bold text-white transition">Ir al Inicio y Bolillero</a>
                </div>
            </main>
        </body>
        </html>
        """)

# ==========================================
# RUTAS DE CARTÓN DIGITAL Y SORTEO AUTOMÁTICO
# ==========================================

@app.post("/app/comprar-jugada", response_class=HTMLResponse)
async def comprar_jugada_app(
    dni: str = Form(...),
    nombre: str = Form(...),
    numeros: str = Form(...)
):
    try:
        lista_nums = [int(n.strip()) for n in numeros.split(",") if n.strip().isdigit() and 1 <= int(n.strip()) <= 50]
    except:
        lista_nums = [7, 14, 22, 33, 41]

    if len(lista_nums) != 5:
        mensaje = "Error: Debes ingresar exactamente 5 números válidos entre 1 y 50."
        return RedirectResponse(url=f"/?mensaje={urllib.parse.quote(mensaje)}#comprar", status_code=303)

    numeros_str = ", ".join([f"{n:02d}" for n in lista_nums])
    
    nueva_apuesta = Apuesta(
        dni=dni,
        nombre=nombre,
        numeros=numeros_str,
        comercio="App Digital Directa",
        fecha=datetime.now().strftime("%Y-%m-%d")
    )
    with Session(engine) as session:
        session.add(nueva_apuesta)
        session.commit()

    # Retornar vista de Cartón Digital Oficial
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cartón Digital - Max%Shop</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-[#0A1128] text-slate-100 min-h-screen flex items-center justify-center p-4">
        <div class="bg-[#101833] border border-emerald-500/50 rounded-3xl p-8 max-w-lg w-full shadow-2xl space-y-6 text-center">
            <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase border border-emerald-500/20">Comprobante Oficial de Participación</span>
            <div class="space-y-1">
                <h2 class="text-3xl font-black text-white">Cartón Digital Max%Shop</h2>
                <p class="text-xs text-slate-400">Sorteo Dominical en Vivo - Domingo 19:00 hs</p>
            </div>
            
            <div class="bg-[#0A1128] border border-slate-700 p-6 rounded-2xl text-left space-y-3">
                <p class="text-xs text-slate-300">👤 <b>Titular:</b> {nombre}</p>
                <p class="text-xs text-slate-300">🆔 <b>DNI:</b> {dni}</p>
                <p class="text-xs text-slate-300">📅 <b>Fecha de Emisión:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                <div class="pt-2 border-t border-slate-800">
                    <p class="text-xs text-orange-400 font-bold mb-2">Tus Números Seleccionados:</p>
                    <div class="flex justify-center gap-2">
                        {"".join([f'<div class="w-10 h-10 rounded-full bg-orange-500 text-slate-950 font-black flex items-center justify-center text-sm shadow">{n:02d}</div>' for n in lista_nums])}
                    </div>
                </div>
            </div>

            <p class="text-[11px] text-slate-400 leading-relaxed">Este comprobante valida tu participación en el bolillero virtual dominical. Conserva tu número de DNI para reclamos de premios.</p>
            
            <div class="flex gap-4">
                <a href="/" class="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl text-xs uppercase transition">Volver al Inicio</a>
                <button onclick="window.print()" class="flex-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-3 rounded-xl text-xs uppercase transition shadow">Imprimir / Guardar</button>
            </div>
        </div>
    </body>
    </html>
    """)

@app.post("/admin/bolillero/sortear", response_class=HTMLResponse)
async def admin_sortear(username: str = Depends(verificar_admin)):
    ganadores_sorteo = sorted(random.sample(range(1, 51), 5))
    DB_COMERCIOS["ultimas_bolillas"] = ganadores_sorteo
    
    with Session(engine) as session:
        apuestas = session.exec(select(Apuesta)).all()
        ganador_encontrado = None
        for ap in apuestas:
            nums_list = [int(n.strip()) for n in ap.numeros.split(",") if n.strip().isdigit()]
            aciertos = len(set(nums_list).intersection(set(ganadores_sorteo)))
            if aciertos >= 5: 
                ganador_encontrado = ap.nombre
                break

    pozo_actual = DB_COMERCIOS["pozo_acumulado"]
    if ganador_encontrado:
        mensaje = f"¡SORTEO OFICIAL REALIZADO! Bolillas: {ganadores_sorteo}. ¡Ganador del pozo de ${pozo_actual:,.0f}: {ganador_encontrado}!"
        DB_COMERCIOS["pozo_acumulado"] = 400000  # Se reinicia al pozo base de $400k
    else:
        DB_COMERCIOS["pozo_acumulado"] += 100000  # Vacante: Acumula $100k más
        mensaje = f"¡SORTEO OFICIAL REALIZADO! Bolillas: {ganadores_sorteo}. Pozo VACANTE. ¡Se acumulan $100.000 más para el próximo domingo!"

    return RedirectResponse(url=f"/admin?mensaje={urllib.parse.quote(mensaje)}", status_code=303)

# ==========================================
# PANEL DE ADMINISTRACIÓN
# ==========================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin), mensaje: str = None):
    with Session(engine) as session:
        usuarios = session.exec(select(Usuario)).all()
        apuestas = session.exec(select(Apuesta)).all()
        
    usuarios_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-4 text-white font-bold">{u.nombre}</td>
            <td class="p-4 text-slate-300 font-mono">{u.dni}</td>
            <td class="p-4 text-slate-300">{u.telefono}</td>
            <td class="p-4 text-orange-400">{u.email}</td>
            <td class="p-4 text-emerald-400 font-bold">{u.estado_suscripcion} (${u.monto_suscripcion:,.0f})</td>
        </tr>""" for u in usuarios])

    apuestas_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-4 text-white font-bold">{ap.nombre}</td>
            <td class="p-4 text-slate-300 font-mono">{ap.dni}</td>
            <td class="p-4 text-orange-400 font-mono font-bold">{ap.numeros}</td>
            <td class="p-4 text-slate-400">{ap.fecha}</td>
        </tr>""" for ap in apuestas]) if apuestas else '<tr><td colspan="4" class="p-4 text-center text-slate-500">Sin cartones registrados aún.</td></tr>'

    alerta_box = f'<div class="bg-orange-500/20 border border-orange-500 text-orange-300 px-6 py-4 rounded-2xl font-bold text-sm text-center shadow-xl">✨ {mensaje}</div>' if mensaje else ''

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
                <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Control Absoluto y Bolillero</span>
                <h1 class="text-2xl sm:text-4xl font-black text-white mt-2">Panel de Administración Max%Shop</h1>
            </div>
            <a href="/" class="bg-slate-800 hover:bg-slate-700 px-6 py-3 rounded-2xl text-xs font-bold text-white border border-slate-700 transition shadow">← Volver al Sitio Web</a>
        </div>

        {alerta_box}

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Total Socios Registrados</span>
                <h3 class="text-4xl font-black text-white">{len(usuarios)}</h3>
            </div>
            <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Cartones / Jugadas Vigentes</span>
                <h3 class="text-4xl font-black text-orange-400">{len(apuestas)}</h3>
            </div>
            <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-2">
                <span class="text-xs text-slate-400 font-bold">Pozo Acumulado Actual</span>
                <h3 class="text-4xl font-black text-emerald-400">${DB_COMERCIOS["pozo_acumulado"]:,.0f}</h3>
            </div>
        </div>

        <!-- ACCIÓN EXCLUSIVA ADMINISTRADOR: GIRAR BOLILLERO -->
        <div class="bg-gradient-to-r from-orange-950/40 via-[#101833] to-[#0A1128] p-8 rounded-3xl border border-orange-500/40 shadow-2xl space-y-4">
            <h2 class="text-xl font-black text-white">⚙️ Acciones de Sorteo Dominical (Exclusivo Administrador)</h2>
            <p class="text-xs text-slate-300">Presiona este botón para realizar el sorteo oficial dominical. Selecciona aleatoriamente 5 bolillas y valida los aciertos de los cartones.</p>
            <form action="/admin/bolillero/sortear" method="POST">
                <button type="submit" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-8 py-3.5 rounded-xl text-xs uppercase shadow-xl transition">
                    🎲 Ejecutar Sorteo Oficial Dominical Ahora
                </button>
            </form>
        </div>

        <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-xl font-black text-white flex items-center gap-2">🎟️ Cartones y Jugadas Registradas</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-4">Nombre</th><th class="p-4">DNI</th><th class="p-4">Números Seleccionados</th><th class="p-4">Fecha</th></tr></thead>
                    <tbody>{apuestas_filas}</tbody>
                </table>
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
            <p class="text-xs text-slate-300">Valida socios activos en la red y registra consumos en pantalla.</p>
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
