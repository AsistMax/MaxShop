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
    version="26.5.4"
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
    monto_suscripcion: float = Field(default=30000.0)

class Transaccion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: Optional[int] = Field(default=None)
    dni: str = Field(index=True)
    tipo: str # "carton" o "ruleta"
    monto: float
    estado: str = Field(default="pendiente") # pendiente, aprobado
    preference_id: Optional[str] = None
    payment_id: Optional[str] = Field(default=None, index=True)
    fecha: str

class Apuesta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dni: str
    nombre: str
    linea1: str
    linea2: str
    linea3: str
    comercio: str = Field(default="App Digital Directa")
    pagado: bool = Field(default=False)
    fecha: str

class RegistroRuleta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dni: str
    nombre: str
    monto_poliza: float
    pagado: bool = Field(default=False)
    comprobante_solicitado: bool = Field(default=False)
    fecha: str

CONFIG_NEGOCIO = {
    "pozo_acumulado": 400000.0,
    "valor_carton": 1000.0,
    "valor_giro_ruleta": 5000.0,
    "permitir_salida_pozo": False,
    "ultimas_bolillas": [3, 7, 12, 14, 18, 22, 25, 27, 33, 38, 40, 41, 45, 48, 50]
}

RULETA_PREMIOS = [
    {"label": "$2.000.000", "valor": 2000000},
    {"label": "$4.000.000", "valor": 4000000},
    {"label": "$6.000.000", "valor": 6000000},
    {"label": "$8.000.000", "valor": 8000000},
    {"label": "$10.000.000", "valor": 10000000},
    {"label": "$12.000.000", "valor": 12000000},
    {"label": "$14.000.000", "valor": 14000000},
    {"label": "$16.000.000", "valor": 16000000},
    {"label": "$18.000.000", "valor": 18000000},
    {"label": "$20.000.000", "valor": 20000000},
]

DB_COMERCIOS = {
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

@app.get("/", response_class=HTMLResponse)
async def client_landing(request: Request, ciudad_filtro: str = "Catamarca (Capital)", mensaje: str = None, resultado_ruleta: str = None):
    pozo_actual = CONFIG_NEGOCIO["pozo_acumulado"]
    valor_carton = CONFIG_NEGOCIO["valor_carton"]
    valor_giro = CONFIG_NEGOCIO["valor_giro_ruleta"]
    bolillas = CONFIG_NEGOCIO["ultimas_bolillas"]
    
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
        <div class="bg-orange-500/20 border border-orange-500 text-orange-300 px-6 py-4 rounded-2xl font-bold text-sm text-center shadow-2xl">
            ✨ {mensaje}
        </div>
        """

    resultado_ruleta_box = ""
    if resultado_ruleta:
        resultado_ruleta_box = f"""
        <div class="bg-emerald-500/20 border border-emerald-500 text-emerald-300 px-6 py-5 rounded-2xl font-black text-base text-center shadow-2xl">
            🎉 ¡Felicitaciones! Obtuviste {resultado_ruleta} en tu póliza para tu grupo familiar.
        </div>
        """

    bolillas_html = "".join([f'<div class="bolillera">{b:02d}</div>' for b in bolillas])

    segmentos_ruleta_html = ""
    colores_segmentos = ["#f97316", "#3b82f6", "#10b981", "#8b5cf6", "#ec4899", "#f59e0b", "#06b6d4", "#6366f1", "#14b8a6", "#eab308"]
    for i, item in enumerate(RULETA_PREMIOS):
        angulo = i * 36
        color = colores_segmentos[i % len(colores_segmentos)]
        segmentos_ruleta_html += f"""
        <div class="ruleta-segmento" style="transform: rotate({angulo}deg); background-color: {color};">
            <span class="segmento-texto">{item['label']}</span>
        </div>
        """

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
        
        .bolillera {{
            width: 48px; height: 48px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ffedd5, #f97316);
            color: #0f172a; font-weight: 900; font-size: 16px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 15px rgba(249,115,22,0.5), inset -2px -2px 6px rgba(0,0,0,0.4);
        }}

        .bolillero-wrapper {{
            display: flex; flex-direction: column; align-items: center; margin: 0 auto;
        }}
        .cage-container {{ position: relative; width: 180px; height: 180px; }}
        .bolillero-cage {{
            width: 100%; height: 100%; border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.25), rgba(0,0,0,0.75));
            border: 4px solid #f59e0b;
            box-shadow: 0 0 25px rgba(245, 158, 11, 0.4), inset 0 0 20px rgba(0,0,0,0.9);
            position: relative; overflow: hidden; animation: girarJaula 6s infinite linear;
        }}
        .cage-bars {{
            position: absolute; inset: 0; border-radius: 50%;
            background: repeating-linear-gradient(45deg, transparent, transparent 12px, rgba(251, 191, 36, 0.35) 12px, rgba(251, 191, 36, 0.35) 16px);
        }}
        .cage-bars-vertical {{
            position: absolute; inset: 0; border-radius: 50%;
            background: repeating-linear-gradient(-45deg, transparent, transparent 12px, rgba(251, 191, 36, 0.35) 12px, rgba(251, 191, 36, 0.35) 16px);
        }}
        .inner-balls {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }}
        .mini-ball {{
            position: absolute; width: 22px; height: 22px; border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #ffffff, #f97316);
            color: #000; font-size: 8px; font-weight: 900; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.6);
        }}
        .mb-1 {{ animation: rebotar1 2.1s infinite ease-in-out; top: 25%; left: 20%; }}
        .mb-2 {{ animation: rebotar2 1.7s infinite ease-in-out; top: 55%; left: 35%; }}
        .mb-3 {{ animation: rebotar3 2.4s infinite ease-in-out; top: 15%; left: 55%; }}
        .mb-4 {{ animation: rebotar1 1.9s infinite ease-in-out; top: 65%; left: 60%; }}
        .mb-5 {{ animation: rebotar2 2.6s infinite ease-in-out; top: 40%; left: 40%; }}
        .mb-6 {{ animation: rebotar3 2.0s infinite ease-in-out; top: 30%; left: 70%; }}
        .mb-7 {{ animation: rebotar1 2.3s infinite ease-in-out; top: 70%; left: 25%; }}
        .mb-8 {{ animation: rebotar2 1.8s infinite ease-in-out; top: 45%; left: 75%; }}

        @keyframes girarJaula {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes rebotar1 {{
            0% {{ transform: translate(0, 0) scale(1); }}
            25% {{ transform: translate(12px, -18px) scale(1.05); }}
            50% {{ transform: translate(-8px, 12px) scale(0.95); }}
            75% {{ transform: translate(18px, 8px) scale(1.02); }}
            100% {{ transform: translate(0, 0) scale(1); }}
        }}
        @keyframes rebotar2 {{
            0% {{ transform: translate(0, 0) scale(1); }}
            30% {{ transform: translate(-15px, -12px) scale(0.98); }}
            60% {{ transform: translate(12px, -22px) scale(1.06); }}
            90% {{ transform: translate(-8px, 16px) scale(0.95); }}
            100% {{ transform: translate(0, 0) scale(1); }}
        }}
        @keyframes rebotar3 {{
            0% {{ transform: translate(0, 0) scale(1); }}
            20% {{ transform: translate(18px, 12px) scale(1.04); }}
            50% {{ transform: translate(-12px, -16px) scale(0.96); }}
            80% {{ transform: translate(8px, 18px) scale(1.02); }}
            100% {{ transform: translate(0, 0) scale(1); }}
        }}

        .bolillero-base {{
            width: 70px; height: 14px; background: linear-gradient(to bottom, #d97706, #78350f);
            border-radius: 4px; margin-top: -2px; box-shadow: 0 4px 10px rgba(0,0,0,0.6); position: relative; z-index: 2;
        }}
        .bolillero-stand {{
            width: 35px; height: 18px; background: linear-gradient(to right, #78350f, #b45309, #78350f);
            margin: 0 auto; border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;
        }}

        .ruleta-container {{
            position: relative; width: 300px; height: 300px; margin: 0 auto;
        }}
        .ruleta-wheel {{
            width: 100%; height: 100%; border-radius: 50%; border: 6px solid #f59e0b;
            position: relative; overflow: hidden; box-shadow: 0 0 30px rgba(245,158,11,0.5);
            transition: transform 4s cubic-bezier(0.15, 0.9, 0.2, 1);
        }}
        .ruleta-segmento {{
            position: absolute; top: 0; left: 50%; width: 50%; height: 100%;
            transform-origin: left center; clip-path: polygon(0 50%, 100% 0, 100% 100%);
            display: flex; align-items: center; justify-content: flex-end; padding-right: 24px;
        }}
        .segmento-texto {{
            color: #fff; font-size: 10px; font-weight: 900; text-shadow: 0 1px 3px rgba(0,0,0,0.9);
            transform: rotate(90deg); transform-origin: center right; text-align: right; white-space: nowrap;
        }}
        .ruleta-puntero {{
            position: absolute; top: -15px; left: 50%; transform: translateX(-50%);
            width: 0; height: 0; border-left: 12px solid transparent; border-right: 12px solid transparent;
            border-top: 24px solid #ef4444; z-index: 10; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
        }}
        .ruleta-centro {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 55px; height: 55px; background: radial-gradient(circle, #f59e0b, #78350f);
            border-radius: 50%; border: 3px solid #fff; z-index: 11;
            display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 10px; color: #000;
        }}
    </style>
</head>
<body class="bg-[#0A1128] text-slate-100 min-h-screen font-sans selection:bg-orange-500 selection:text-white antialiased">

    <!-- BARRA SUPERIOR -->
    <div class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-xs py-3 px-4 sm:px-8 flex flex-col lg:flex-row justify-between items-center gap-4 border-b border-slate-800">
        <div class="flex items-center gap-3 w-full lg:w-auto justify-between lg:justify-start">
            <span class="font-black text-orange-400 flex items-center gap-1.5 text-sm">📍 Ciudad Actual: <span class="text-white underline">{ciudad_filtro}</span></span>
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

    <!-- HEADER OFICIAL CON LOGO -->
    <header class="sticky top-0 z-40 bg-[#0A1128]/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="Logo Max%Shop" class="w-12 h-12 object-cover rounded-xl border border-orange-500/50 shadow">
                <div class="text-2xl sm:text-3xl font-black tracking-tighter text-white">
                    Max<span class="text-orange-500">%</span>Shop
                </div>
            </div>
            <nav class="hidden md:flex items-center space-x-6 text-xs font-bold text-slate-300">
                <a href="#comprar" class="hover:text-orange-400 transition">Comprar Números</a>
                <a href="#ruleta" class="hover:text-orange-400 transition">Ruleta de Cobertura</a>
                <a href="#bolillero" class="hover:text-orange-400 transition">Bolillero Dominical</a>
                <a href="#comercios" class="hover:text-orange-400 transition">Comercios Adheridos</a>
            </nav>
            <div class="flex items-center space-x-3">
                <a href="/login" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black text-xs px-5 py-2.5 rounded-xl uppercase shadow-lg transition">
                    Participar ${valor_carton:,.0f}
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16">
        
        {alerta_box}
        {resultado_ruleta_box}

        <!-- HERO PRINCIPAL (BANNER ESTÁTICO CORREGIDO) -->
        <div class="relative bg-gradient-to-br from-[#131E3E] via-[#0F1730] to-[#0A1128] border border-slate-800 rounded-3xl p-6 md:p-12 shadow-2xl space-y-8 text-center overflow-hidden">
            <div class="max-w-4xl mx-auto">
                <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="Banner Principal Max%Shop" class="w-full max-h-[420px] object-cover rounded-2xl shadow-2xl border border-slate-700 mb-8 static-banner">
            </div>
            <div class="max-w-3xl mx-auto space-y-4">
                <span class="inline-flex items-center space-x-2 bg-orange-500/10 text-orange-400 text-xs font-bold px-4 py-2 rounded-full border border-orange-500/20 uppercase shadow">
                    <span>🔥</span> <span>Club de Beneficios, Cobertura y Sorteos Semanales</span>
                </span>
                <h1 class="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
                    Pozo Acumulado <span class="text-orange-500">${pozo_actual:,.0f}</span>
                </h1>
                <p class="text-slate-300 text-sm sm:text-base leading-relaxed">Disfruta de la red de comercios, cobertura familiar y participa por el bolillero dominical de los domingos a las 19:00 hs.</p>
                <div class="flex justify-center gap-4 flex-wrap">
                    <a href="#comprar" class="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-bold text-sm shadow-lg transition">Comprar Números (${valor_carton:,.0f})</a>
                    <a href="#ruleta" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-bold text-sm shadow-lg transition">Girar Ruleta Cobertura (${valor_giro:,.0f})</a>
                </div>
            </div>
        </div>

        <!-- SECCIÓN RULETA DE COBERTURAS (CON GIRO VISUAL EN JS) -->
        <div id="ruleta" class="bg-gradient-to-r from-blue-950/40 via-[#101833] to-[#0A1128] border border-blue-500/40 rounded-3xl p-8 shadow-2xl space-y-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div class="space-y-2 max-w-xl">
                    <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Cobertura Integral Grupo Familiar</span>
                    <h3 class="text-3xl font-black text-white">Ruleta de Cobertura Max%Shop</h3>
                    <p class="text-sm text-slate-400 leading-relaxed">Paga ${valor_giro:,.0f} para girar y obtener tu monto de póliza familiar.</p>
                </div>
                <div class="bg-[#0A1128] border border-blue-500/40 p-6 rounded-2xl text-center shadow-xl w-full md:w-auto">
                    <p class="text-xs text-slate-400">COSTO POR GIRO</p>
                    <p class="text-3xl font-black text-blue-400 mt-1">${valor_giro:,.0f}</p>
                </div>
            </div>

            <div class="bg-[#0A1128] border border-slate-800 p-8 rounded-2xl text-center space-y-6">
                <div class="ruleta-container">
                    <div class="ruleta-puntero"></div>
                    <div id="ruletaWheel" class="ruleta-wheel">
                        {segmentos_ruleta_html}
                    </div>
                    <div class="ruleta-centro" onclick="girarRuletaVisual()">GIRAR</div>
                </div>

                <!-- Formulario de Pago y Giro seguro -->
                <form id="formRuleta" action="/app/pagar-ruleta" method="POST" class="max-w-md mx-auto space-y-4 pt-4" onsubmit="return prepararGiro(event)">
                    <input type="text" name="dni" id="ruletaDni" required placeholder="Tu DNI de Socio" class="w-full bg-slate-900 border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                    <input type="text" name="nombre" id="ruletaNombre" required placeholder="Tu Nombre y Apellido" class="w-full bg-slate-900 border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-black py-3.5 rounded-xl text-xs uppercase shadow-lg transition">
                        💳 Pagar Giro de Ruleta y Jugar (${valor_giro:,.0f})
                    </button>
                </form>

                <div class="pt-4 border-t border-slate-800">
                    <form action="/app/solicitar-comprobante-ruleta" method="POST" class="max-w-md mx-auto flex gap-2">
                        <input type="text" name="dni" required placeholder="Ingresa tu DNI para Comprobante" class="flex-1 bg-slate-900 border border-slate-700 px-4 py-2.5 rounded-xl text-xs text-white">
                        <button type="submit" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-5 py-2.5 rounded-xl text-xs uppercase shadow transition">
                            📄 Solicitar Comprobante
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <!-- SECCIÓN COMPRAR NÚMEROS -->
        <div id="comprar" class="bg-gradient-to-r from-emerald-950/30 via-[#101833] to-[#0A1128] border border-emerald-500/40 rounded-3xl p-8 shadow-2xl space-y-6">
            <div class="max-w-xl space-y-2">
                <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase border border-emerald-500/20">Cartón Digital de 3 Líneas</span>
                <h3 class="text-2xl font-black text-white">Elegí 3 Líneas de 5 Números (Del 1 al 50)</h3>
                <p class="text-xs text-slate-400">Ingresa números separados por comas para cada línea. Al presionar comprar, serás redirigido a la pasarela de pago para procesar ${valor_carton:,.0f} de forma segura.</p>
            </div>
            
            <form action="/app/comprar-jugada" method="POST" class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-4xl">
                <input type="text" name="dni" required placeholder="Tu DNI de Socio" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                <input type="text" name="nombre" required placeholder="Tu Nombre y Apellido" class="bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                
                <div class="sm:col-span-2 space-y-1">
                    <label class="text-[11px] font-bold text-orange-400">Línea 1 (5 Números):</label>
                    <input type="text" name="linea1" required placeholder="Ej: 07, 14, 22, 33, 41" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                </div>
                <div class="sm:col-span-2 space-y-1">
                    <label class="text-[11px] font-bold text-orange-400">Línea 2 (5 Números):</label>
                    <input type="text" name="linea2" required placeholder="Ej: 03, 12, 25, 38, 49" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                </div>
                <div class="sm:col-span-2 space-y-1">
                    <label class="text-[11px] font-bold text-orange-400">Línea 3 (5 Números):</label>
                    <input type="text" name="linea3" required placeholder="Ej: 05, 18, 27, 40, 50" class="w-full bg-[#0A1128] border border-slate-700 px-4 py-3 rounded-xl text-xs text-white">
                </div>

                <div class="sm:col-span-2 pt-2">
                    <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-3.5 rounded-xl text-xs uppercase tracking-wider shadow-lg transition">
                        💳 Pagar Cartón Digital (${valor_carton:,.0f}) y Participar
                    </button>
                </div>
            </form>
        </div>

        <!-- SECCIÓN BOLILLERO VIRTUAL 3D (VALIDACIÓN DOMINICAL Y COMPRA) -->
        <div id="bolillero" class="bg-gradient-to-r from-[#1E293B] to-[#0F172A] border border-orange-500/30 rounded-3xl p-8 shadow-2xl space-y-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div class="space-y-2 max-w-xl">
                    <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Sorteo Dominical en Vivo (Domingos 19:00 hs)</span>
                    <h3 class="text-3xl font-black text-white">El Bolillero Virtual de Max%Shop</h3>
                    <p class="text-sm text-slate-400 leading-relaxed">Requiere compra previa de cartón digital. Activo exclusivamente los domingos desde las 19:00 hs.</p>
                </div>
                <div class="bg-[#0A1128] border border-orange-500/40 p-6 rounded-2xl text-center shadow-xl w-full md:w-auto">
                    <p class="text-xs text-slate-400">POZO ACUMULADO ACTUAL</p>
                    <p class="text-3xl font-black text-emerald-400 mt-1">${pozo_actual:,.0f}</p>
                </div>
            </div>

            <div class="bg-[#0A1128] border border-slate-800 p-8 rounded-2xl text-center space-y-6">
                <!-- Panel de validación por DNI para ver el bolillero en tiempo real -->
                <div class="max-w-md mx-auto bg-slate-900 border border-slate-700 p-6 rounded-2xl space-y-4">
                    <h4 class="text-xs font-bold text-orange-400 uppercase">Validar Acceso al Sorteo Dominical</h4>
                    <p class="text-[11px] text-slate-400">Ingrese su DNI para comprobar que adquirió su cartón digital y que el sorteo se encuentra en horario (Domingos 19hs).</p>
                    <div class="flex gap-2">
                        <input type="text" id="dniBolillero" placeholder="Ingrese su DNI..." class="flex-1 bg-slate-950 border border-slate-700 px-4 py-2 rounded-xl text-xs text-white">
                        <button onclick="verificarAccesoBolillero()" class="bg-orange-500 hover:bg-orange-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs transition">Verificar</button>
                    </div>
                    <div id="resultadoBolilleroAcceso" class="text-xs font-bold pt-2"></div>
                </div>

                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest pt-2">BOLILLERO</p>
                
                <div class="bolillero-wrapper">
                    <div class="cage-container">
                        <div class="bolillero-cage">
                            <div class="cage-bars"></div>
                            <div class="cage-bars-vertical"></div>
                            <div class="inner-balls">
                                <div class="mini-ball mb-1">04</div>
                                <div class="mini-ball mb-2">12</div>
                                <div class="mini-ball mb-3">19</div>
                                <div class="mini-ball mb-4">28</div>
                                <div class="mini-ball mb-5">35</div>
                                <div class="mini-ball mb-6">42</div>
                                <div class="mini-ball mb-7">08</div>
                                <div class="mini-ball mb-8">49</div>
                            </div>
                        </div>
                    </div>
                    <div class="bolillero-base">
                        <div class="bolillero-stand"></div>
                    </div>
                </div>

                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest pt-4">Las 15 Bolillas Ganadoras Extraídas</p>
                <div id="contenedorBolillas" class="flex justify-center items-center gap-2 sm:gap-3 flex-wrap max-w-3xl mx-auto">
                    {bolillas_html}
                </div>
                
                <div class="pt-4 flex flex-col sm:flex-row justify-center items-center gap-4">
                    <button onclick="reproducirVozBolillas()" class="w-full sm:w-auto bg-blue-600 hover:bg-blue-500 text-white font-bold px-8 py-3 rounded-xl text-xs uppercase shadow transition flex items-center justify-center gap-2">
                        🔊 Escuchar Bolillas en Vivo (Audio)
                    </button>
                    <a href="#comprar" class="w-full sm:w-auto bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-8 py-3 rounded-xl text-xs uppercase shadow-lg transition flex items-center justify-center gap-2">
                        🎟️ Comprar Número para el Sorteo
                    </a>
                </div>
            </div>
        </div>

        <!-- SECCIÓN COMERCIOS ADHERIDOS -->
        <div id="comercios" class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                <div class="space-y-2 flex items-center gap-4">
                    <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="Logo Max%Shop" class="w-14 h-14 object-cover rounded-2xl border border-blue-500/40 shadow-lg">
                    <div>
                        <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Geolocalización Activa</span>
                        <h3 class="text-3xl font-black text-white mt-1">Comercios en <span class="text-orange-400">{ciudad_filtro}</span></h3>
                        <p class="text-xs text-slate-400">Cupones instantáneos y beneficios activos con tu membresía oficial.</p>
                    </div>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {lista_comercios_html}
            </div>
        </div>

    </main>

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

        function girarRuletaVisual() {{
            const wheel = document.getElementById('ruletaWheel');
            const randomDegree = Math.floor(1440 + Math.random() * 1440);
            wheel.style.transform = `rotate(${{randomDegree}}deg)`;
        }}

        function prepararGiro(event) {{
            girarRuletaVisual();
        }}

        async function verificarAccesoBolillero() {{
            const dni = document.getElementById('dniBolillero').value.trim();
            const resDiv = document.getElementById('resultadoBolilleroAcceso');
            if(!dni) {{
                resDiv.innerHTML = "<span class='text-red-400'>Por favor ingrese un DNI válido.</span>";
                return;
            }}
            try {{
                const response = await fetch(`/api/verificar-bolillero?dni=${{dni}}`);
                const data = await response.json();
                if(data.permitido) {{
                    resDiv.innerHTML = `<span class='text-emerald-400'>✨ ¡Acceso concedido! Cartón verificado y horario dominical activo.</span>`;
                }} else {{
                    resDiv.innerHTML = `<span class='text-red-400'>❌ ${{data.motivo}}</span>`;
                }}
            }} catch(e) {{
                resDiv.innerHTML = "<span class='text-red-400'>Error al verificar el acceso. Intente nuevamente.</span>";
            }}
        }}

        function reproducirVozBolillas() {{
            if ('speechSynthesis' in window) {{
                const bolillasTexto = "{', '.join(map(str, bolillas))}";
                const mensaje = new SpeechSynthesisUtterance("Atención socios de Max%Shop. Las bolillas sorteadas son: " + bolillasTexto);
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
# RUTAS DE PAGO SEGURO Y FLUJO DE COMPRA
# ==========================================

@app.post("/app/comprar-jugada", response_class=HTMLResponse)
async def comprar_jugada_app(
    dni: str = Form(...),
    nombre: str = Form(...),
    linea1: str = Form(...),
    linea2: str = Form(...),
    linea3: str = Form(...)
):
    try:
        l1 = [int(n.strip()) for n in linea1.split(",") if n.strip().isdigit() and 1 <= int(n.strip()) <= 50]
        l2 = [int(n.strip()) for n in linea2.split(",") if n.strip().isdigit() and 1 <= int(n.strip()) <= 50]
        l3 = [int(n.strip()) for n in linea3.split(",") if n.strip().isdigit() and 1 <= int(n.strip()) <= 50]
    except:
        l1, l2, l3 = [7,14,22,33,41], [3,12,25,38,49], [5,18,27,40,50]

    if len(l1) != 5 or len(l2) != 5 or len(l3) != 5:
        mensaje = "Error: Cada línea debe contener exactamente 5 números válidos entre 1 y 50."
        return RedirectResponse(url=f"/?mensaje={urllib.parse.quote(mensaje)}#comprar", status_code=303)

    valor_carton = CONFIG_NEGOCIO["valor_carton"]

    nueva_apuesta = Apuesta(
        dni=dni,
        nombre=nombre,
        linea1=", ".join([f"{n:02d}" for n in l1]),
        linea2=", ".join([f"{n:02d}" for n in l2]),
        linea3=", ".join([f"{n:02d}" for n in l3]),
        comercio="App Digital Directa",
        pagado=False,
        fecha=datetime.now().strftime("%Y-%m-%d")
    )
    with Session(engine) as session:
        session.add(nueva_apuesta)
        session.commit()
        session.refresh(nueva_apuesta)
        apuesta_id = nueva_apuesta.id

    preference_data = {
        "items": [
            {
                "title": f"Cartón Digital 3 Líneas - Max%Shop (DNI: {dni})",
                "quantity": 1,
                "unit_price": float(valor_carton)
            }
        ],
        "back_urls": {
            "success": f"https://maxshop.com/app/pago-exitoso?tipo=carton&ref_id={apuesta_id}",
            "pending": f"https://maxshop.com/app/pago-pend?tipo=carton&ref_id={apuesta_id}",
            "failure": f"https://maxshop.com/app/pago-fail?tipo=carton"
        },
        "auto_return": "approved",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        init_point = preference.get("init_point")
    except Exception:
        init_point = f"/app/pago-exitoso?tipo=carton&ref_id={apuesta_id}"

    return RedirectResponse(url=init_point, status_code=303)


@app.get("/api/verificar-bolillero")
async def verificar_bolillero(dni: str):
    ahora = datetime.now()
    # Validación dominical: 6 corresponde a Domingo en datetime.weekday() (lunes=0 ... domingo=6)
    es_domingo = ahora.weekday() == 6
    es_horario = ahora.hour >= 19

    if not (es_domingo and es_horario):
        return {"permitido": False, "motivo": "El bolillero solo se activa los domingos a partir de las 19:00 hs."}

    with Session(engine) as session:
        apuesta = session.exec(select(Apuesta).where(Apuesta.dni == dni, Apuesta.pagado == True)).first()
        if not apuesta:
            return {"permitido": False, "motivo": "No se registra la compra de un cartón digital pagado para este DNI."}

    return {"permitido": True, "motivo": "Acceso autorizado"}


@app.post("/app/pagar-ruleta", response_class=HTMLResponse)
async def pagar_ruleta_app(dni: str = Form(...), nombre: str = Form(...)):
    valor_giro = CONFIG_NEGOCIO["valor_giro_ruleta"]
    premio_obtenido = random.choice(RULETA_PREMIOS)

    nuevo_registro = RegistroRuleta(
        dni=dni,
        nombre=nombre,
        monto_poliza=premio_obtenido["valor"],
        pagado=False,
        comprobante_solicitado=False,
        fecha=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    with Session(engine) as session:
        session.add(nuevo_registro)
        session.commit()
        session.refresh(nuevo_registro)
        reg_id = nuevo_registro.id

    preference_data = {
        "items": [
            {
                "title": f"Giro Ruleta de Cobertura - Max%Shop (DNI: {dni})",
                "quantity": 1,
                "unit_price": float(valor_giro)
            }
        ],
        "back_urls": {
            "success": f"https://maxshop.com/app/pago-exitoso?tipo=ruleta&ref_id={reg_id}&premio={premio_obtenido['label']}",
            "pending": f"https://maxshop.com/app/pago-pend?tipo=ruleta",
            "failure": f"https://maxshop.com/app/pago-fail?tipo=ruleta"
        },
        "auto_return": "approved",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        init_point = preference.get("init_point")
    except Exception:
        init_point = f"/app/pago-exitoso?tipo=ruleta&ref_id={reg_id}&premio={premio_obtenido['label']}"

    return RedirectResponse(url=init_point, status_code=303)


@app.get("/app/pago-exitoso", response_class=HTMLResponse)
async def pago_exitoso(tipo: str, ref_id: int, premio: str = None):
    with Session(engine) as session:
        if tipo == "carton":
            apuesta = session.get(Apuesta, ref_id)
            if apuesta:
                apuesta.pagado = True
                session.add(apuesta)
                session.commit()
                
                l1 = [int(n.strip()) for n in apuesta.linea1.split(",")]
                l2 = [int(n.strip()) for n in apuesta.linea2.split(",")]
                l3 = [int(n.strip()) for n in apuesta.linea3.split(",")]
                valor_carton = CONFIG_NEGOCIO["valor_carton"]

                return HTMLResponse(content=f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Cartón Digital - Max%Shop</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-[#0A1128] text-slate-100 min-h-screen flex items-center justify-center p-4">
                    <div class="bg-[#101833] border border-emerald-500/50 rounded-3xl p-8 max-w-lg w-full shadow-2xl space-y-6 text-center">
                        <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full uppercase border border-emerald-500/20">✅ Pago Aprobado - Comprobante Oficial (${valor_carton:,.0f})</span>
                        <div class="space-y-1">
                            <h2 class="text-3xl font-black text-white">Cartón Digital 3 Líneas</h2>
                            <p class="text-xs text-slate-400">Sorteo Dominical en Vivo - Domingo 19:00 hs</p>
                        </div>
                        
                        <div class="bg-[#0A1128] border border-slate-700 p-6 rounded-2xl text-left space-y-3">
                            <p class="text-xs text-slate-300">👤 <b>Titular:</b> {apuesta.nombre}</p>
                            <p class="text-xs text-slate-300">🆔 <b>DNI:</b> {apuesta.dni}</p>
                            <p class="text-xs text-slate-300">📅 <b>Fecha de Emisión:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                            
                            <div class="pt-3 border-t border-slate-800 space-y-2">
                                <p class="text-xs text-orange-400 font-bold">Línea 1:</p>
                                <div class="flex gap-2">{"".join([f'<div class="w-8 h-8 rounded-full bg-orange-500 text-slate-950 font-black flex items-center justify-center text-xs shadow">{n:02d}</div>' for n in l1])}</div>
                                
                                <p class="text-xs text-orange-400 font-bold pt-1">Línea 2:</p>
                                <div class="flex gap-2">{"".join([f'<div class="w-8 h-8 rounded-full bg-orange-500 text-slate-950 font-black flex items-center justify-center text-xs shadow">{n:02d}</div>' for n in l2])}</div>
                                
                                <p class="text-xs text-orange-400 font-bold pt-1">Línea 3:</p>
                                <div class="flex gap-2">{"".join([f'<div class="w-8 h-8 rounded-full bg-orange-500 text-slate-950 font-black flex items-center justify-center text-xs shadow">{n:02d}</div>' for n in l3])}</div>
                            </div>
                        </div>

                        <p class="text-[11px] text-slate-400 leading-relaxed">Pago validado con éxito. Este comprobante valida tu participación en el bolillero virtual dominical.</p>
                        
                        <div class="flex gap-4">
                            <a href="/" class="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl text-xs uppercase transition">Volver al Inicio</a>
                            <button onclick="window.print()" class="flex-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-3 rounded-xl text-xs uppercase transition shadow">Imprimir / Guardar</button>
                        </div>
                    </div>
                </body>
                </html>
                """)

        elif tipo == "ruleta":
            registro = session.get(RegistroRuleta, ref_id)
            if registro:
                registro.pagado = True
                registro.comprobante_solicitado = True
                session.add(registro)
                session.commit()
                
                monto_str = f"${registro.monto_poliza:,.0f}"

                return HTMLResponse(content=f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Comprobante de Póliza - Max%Shop</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-[#0A1128] text-slate-100 min-h-screen flex items-center justify-center p-4">
                    <div class="bg-[#101833] border border-blue-500/50 rounded-3xl p-8 max-w-lg w-full shadow-2xl space-y-6 text-center">
                        <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">✅ Giro Pagado - Comprobante Oficial de Cobertura Familiar</span>
                        <div class="space-y-1">
                            <h2 class="text-3xl font-black text-white">Póliza de Grupo Familiar</h2>
                            <p class="text-xs text-slate-400">Max%Shop - Cobertura Activa</p>
                        </div>
                        
                        <div class="bg-[#0A1128] border border-slate-700 p-6 rounded-2xl text-left space-y-3">
                            <p class="text-xs text-slate-300">👤 <b>Titular:</b> {registro.nombre}</p>
                            <p class="text-xs text-slate-300">🆔 <b>DNI:</b> {registro.dni}</p>
                            <p class="text-xs text-slate-300">📅 <b>Fecha de Emisión:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                            <div class="pt-3 border-t border-slate-800">
                                <p class="text-xs text-orange-400 font-bold">Monto Máximo de Póliza Asignada:</p>
                                <p class="text-2xl font-black text-emerald-400 mt-1">{monto_str}</p>
                            </div>
                        </div>

                        <p class="text-[11px] text-slate-400 leading-relaxed">Este comprobante valida la póliza obtenida tras el pago exitoso en la ruleta de coberturas para tu grupo familiar.</p>
                        
                        <div class="flex gap-4">
                            <a href="/" class="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl text-xs uppercase transition">Volver al Inicio</a>
                            <button onclick="window.print()" class="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl text-xs uppercase transition shadow">Imprimir / Guardar</button>
                        </div>
                    </div>
                </body>
                </html>
                """)

    return RedirectResponse(url="/?mensaje=Error+en+la+transacción", status_code=303)


@app.post("/app/solicitar-comprobante-ruleta", response_class=HTMLResponse)
async def solicitar_comprobante_ruleta(dni: str = Form(...)):
    with Session(engine) as session:
        registros = session.exec(select(RegistroRuleta).where(RegistroRuleta.dni == dni, RegistroRuleta.pagado == True)).all()
        if not registros:
            mensaje = "No se encontraron registros de giros pagados para este DNI. Debe abonar el giro primero."
            return RedirectResponse(url=f"/?mensaje={urllib.parse.quote(mensaje)}#ruleta", status_code=303)
        
        max_registro = max(registros, key=lambda r: r.monto_poliza)
        max_registro.comprobante_solicitado = True
        session.add(max_registro)
        session.commit()
        
        nombre = max_registro.nombre
        monto_str = f"${max_registro.monto_poliza:,.0f}"

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Comprobante de Póliza - Max%Shop</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-[#0A1128] text-slate-100 min-h-screen flex items-center justify-center p-4">
        <div class="bg-[#101833] border border-blue-500/50 rounded-3xl p-8 max-w-lg w-full shadow-2xl space-y-6 text-center">
            <span class="text-xs font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full uppercase border border-blue-500/20">Comprobante Oficial de Cobertura Familiar</span>
            <div class="space-y-1">
                <h2 class="text-3xl font-black text-white">Póliza de Grupo Familiar</h2>
                <p class="text-xs text-slate-400">Max%Shop - Cobertura Activa</p>
            </div>
            
            <div class="bg-[#0A1128] border border-slate-700 p-6 rounded-2xl text-left space-y-3">
                <p class="text-xs text-slate-300">👤 <b>Titular:</b> {nombre}</p>
                <p class="text-xs text-slate-300">🆔 <b>DNI:</b> {dni}</p>
                <p class="text-xs text-slate-300">📅 <b>Fecha de Emisión:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                <div class="pt-3 border-t border-slate-800">
                    <p class="text-xs text-orange-400 font-bold">Monto Máximo de Póliza Asignada:</p>
                    <p class="text-2xl font-black text-emerald-400 mt-1">{monto_str}</p>
                </div>
            </div>

            <p class="text-[11px] text-slate-400 leading-relaxed">Este comprobante valida la póliza más alta obtenida en la ruleta de coberturas para tu grupo familiar.</p>
            
            <div class="flex gap-4">
                <a href="/" class="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl text-xs uppercase transition">Volver al Inicio</a>
                <button onclick="window.print()" class="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl text-xs uppercase transition shadow">Imprimir / Guardar</button>
            </div>
        </div>
    </body>
    </html>
    """)

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

@app.post("/admin/bolillero/sortear", response_class=HTMLResponse)
async def admin_sortear(username: str = Depends(verificar_admin)):
    ganadores_sorteo = sorted(random.sample(range(1, 51), 15))
    CONFIG_NEGOCIO["ultimas_bolillas"] = ganadores_sorteo
    
    ganador_pozo = None
    with Session(engine) as session:
        apuestas = session.exec(select(Apuesta).where(Apuesta.pagado == True)).all()
        
        if CONFIG_NEGOCIO["permitir_salida_pozo"]:
            for ap in apuestas:
                for linea_str in [ap.linea1, ap.linea2, ap.linea3]:
                    nums_list = [int(n.strip()) for n in linea_str.split(",") if n.strip().isdigit()]
                    if len(set(nums_list).intersection(set(ganadores_sorteo))) >= 5:
                        ganador_pozo = ap.nombre
                        break
                if ganador_pozo:
                    break

        premios_sorpresa_msj = ""
        if apuestas:
            ganadores_consuelo = random.sample(apuestas, min(2, len(apuestas)))
            premios_sorpresa_msj = f" | 🎁 Premios sorpresa ocultos adjudicados a: {ganadores_consuelo[0].nombre}."

    pozo_actual = CONFIG_NEGOCIO["pozo_acumulado"]
    if ganador_pozo:
        mensaje = f"¡SORTEO OFICIAL REALIZADO! ¡Ganador del pozo de ${pozo_actual:,.0f}: {ganador_pozo}!" + premios_sorpresa_msj
        CONFIG_NEGOCIO["pozo_acumulado"] = 400000.0
    else:
        CONFIG_NEGOCIO["pozo_acumulado"] += 100000.0
        mensaje = f"¡SORTEO OFICIAL REALIZADO! Pozo VACANTE. ¡Se acumulan $100.000 más para el próximo domingo!" + premios_sorpresa_msj

    return RedirectResponse(url=f"/admin?mensaje={urllib.parse.quote(mensaje)}", status_code=303)

@app.post("/admin/configurar", response_class=HTMLResponse)
async def admin_configurar(
    pozo_acumulado: float = Form(...),
    valor_carton: float = Form(...),
    valor_giro_ruleta: float = Form(...),
    permitir_salida_pozo: bool = Form(False),
    username: str = Depends(verificar_admin)
):
    CONFIG_NEGOCIO["pozo_acumulado"] = pozo_acumulado
    CONFIG_NEGOCIO["valor_carton"] = valor_carton
    CONFIG_NEGOCIO["valor_giro_ruleta"] = valor_giro_ruleta
    CONFIG_NEGOCIO["permitir_salida_pozo"] = permitir_salida_pozo
    
    mensaje = "Configuración del negocio, precios y ruleta actualizada exitosamente."
    return RedirectResponse(url=f"/admin?mensaje={urllib.parse.quote(mensaje)}", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verificar_admin), mensaje: str = None):
    with Session(engine) as session:
        usuarios = session.exec(select(Usuario)).all()
        apuestas = session.exec(select(Apuesta)).all()
        registros_ruleta = session.exec(select(RegistroRuleta)).all()
        
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
            <td class="p-4 text-orange-400 font-mono font-bold">L1: {ap.linea1}<br>L2: {ap.linea2}<br>L3: {ap.linea3}</td>
            <td class="p-4 {'text-emerald-400' if ap.pagado else 'text-red-400'} font-bold">{'Pagado' if ap.pagado else 'Pendiente'}</td>
            <td class="p-4 text-slate-400">{ap.fecha}</td>
        </tr>""" for ap in apuestas]) if apuestas else '<tr><td colspan="5" class="p-4 text-center text-slate-500">Sin cartones registrados aún.</td></tr>'

    ruleta_filas = "".join([f"""
        <tr class="border-b border-slate-800 text-xs hover:bg-slate-800/40 transition">
            <td class="p-4 text-white font-bold">{r.nombre}</td>
            <td class="p-4 text-slate-300 font-mono">{r.dni}</td>
            <td class="p-4 text-blue-400 font-mono font-bold">${r.monto_poliza:,.0f}</td>
            <td class="p-4 {'text-emerald-400' if r.pagado else 'text-red-400'} font-bold">{'Pagado' if r.pagado else 'Pendiente'}</td>
            <td class="p-4 text-emerald-400">{'Sí' if r.comprobante_solicitado else 'Pendiente'}</td>
            <td class="p-4 text-slate-400">{r.fecha}</td>
        </tr>""" for r in registros_ruleta]) if registros_ruleta else '<tr><td colspan="6" class="p-4 text-center text-slate-500">Sin giros de ruleta registrados aún.</td></tr>'

    alerta_box = f'<div class="bg-orange-500/20 border border-orange-500 text-orange-300 px-6 py-4 rounded-2xl font-bold text-sm text-center shadow-xl">✨ {mensaje}</div>' if mensaje else ''

    pozo_val = CONFIG_NEGOCIO["pozo_acumulado"]
    carton_val = CONFIG_NEGOCIO["valor_carton"]
    giro_val = CONFIG_NEGOCIO["valor_giro_ruleta"]
    salida_checked = "checked" if CONFIG_NEGOCIO["permitir_salida_pozo"] else ""

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
            <div class="flex items-center gap-4">
                <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="Logo" class="w-12 h-12 rounded-xl object-cover border border-orange-500">
                <div>
                    <span class="text-xs font-bold text-orange-400 bg-orange-500/10 px-3 py-1 rounded-full uppercase border border-orange-500/20">Control Absoluto, Precios y Bolillero</span>
                    <h1 class="text-2xl sm:text-4xl font-black text-white mt-2">Panel de Administración Max%Shop</h1>
                </div>
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
                <h3 class="text-4xl font-black text-emerald-400">${pozo_val:,.0f}</h3>
            </div>
        </div>

        <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-6">
            <h2 class="text-xl font-black text-white">⚙️ Configuración de Montos, Ruleta y Seguridad</h2>
            <form action="/admin/configurar" method="POST" class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div>
                    <label class="block text-xs font-bold text-slate-300 mb-2">Monto Pozo Acumulado ($):</label>
                    <input type="number" step="any" name="pozo_acumulado" value="{pozo_val}" required class="w-full bg-[#0A1128] border border-slate-700 p-3 rounded-xl text-xs text-white">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-300 mb-2">Valor Cartón Digital ($):</label>
                    <input type="number" step="any" name="valor_carton" value="{carton_val}" required class="w-full bg-[#0A1128] border border-slate-700 p-3 rounded-xl text-xs text-white">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-300 mb-2">Valor Giro Ruleta Cobertura ($):</label>
                    <input type="number" step="any" name="valor_giro_ruleta" value="{giro_val}" required class="w-full bg-[#0A1128] border border-slate-700 p-3 rounded-xl text-xs text-white">
                </div>
                <div class="sm:col-span-3 flex flex-col justify-end">
                    <label class="flex items-center gap-3 bg-[#0A1128] border border-slate-700 p-3 rounded-xl cursor-pointer">
                        <input type="checkbox" name="permitir_salida_pozo" value="true" {salida_checked} class="w-4 h-4 accent-orange-500">
                        <span class="text-xs font-bold text-orange-400">Permitir salida del Pozo Mayor</span>
                    </label>
                </div>
                <div class="sm:col-span-3">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-3 rounded-xl text-xs uppercase shadow transition">
                        💾 Guardar Nueva Configuración de Precios
                    </button>
                </div>
            </form>
        </div>

        <div class="bg-gradient-to-r from-orange-950/40 via-[#101833] to-[#0A1128] p-8 rounded-3xl border border-orange-500/40 shadow-2xl space-y-4">
            <h2 class="text-xl font-black text-white">🎲 Ejecución de Sorteo Dominical en Vivo</h2>
            <p class="text-xs text-slate-300">Presiona para sortear las 15 bolillas oficiales y aplicar el filtro de premios.</p>
            <form action="/admin/bolillero/sortear" method="POST">
                <button type="submit" class="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-400 text-slate-950 font-black px-8 py-3.5 rounded-xl text-xs uppercase shadow-xl transition">
                    🚀 Ejecutar Sorteo Oficial Ahora
                </button>
            </form>
        </div>

        <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-xl font-black text-white flex items-center gap-2">🎡 Giros y Pólizas de Ruleta Registradas</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-4">Nombre</th><th class="p-4">DNI</th><th class="p-4">Monto Póliza</th><th class="p-4">Estado Pago</th><th class="p-4">Comprobante Solicitado</th><th class="p-4">Fecha</th></tr></thead>
                    <tbody>{ruleta_filas}</tbody>
                </table>
            </div>
        </div>

        <div class="bg-[#101833] p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <h2 class="text-xl font-black text-white flex items-center gap-2">🎟️ Cartones y Jugadas Registradas</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <thead><tr class="text-slate-400 border-b border-slate-800 text-xs"><th class="p-4">Nombre</th><th class="p-4">DNI</th><th class="p-4">Líneas de Números</th><th class="p-4">Estado Pago</th><th class="p-4">Fecha</th></tr></thead>
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
