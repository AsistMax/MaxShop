from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import random

app = FastAPI(title="Max Shop - Sistema de Sorteos y Ruleta")

# Configuración de Base de Datos SQLite
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

# ---------------------------------------------------------
# MODELOS DE DATOS (SQLModel)
# ---------------------------------------------------------
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dni: str = Field(index=True, unique=True)
    nombre: str
    email: str

class ApuestaBolillero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dni_usuario: str
    pagado: bool = Field(default=False)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)

class GiroRuleta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dni_usuario: str
    premio: str
    pagado: bool = Field(default=False)
    fecha: datetime = Field(default_factory=datetime.utcnow)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Iniciar planificador automático para el bolillero dominical (Domingos a las 19:00 hs)
    if not scheduler.running:
        scheduler.add_job(sorteo_dominical_automatico, 'cron', day_of_week='sun', hour=19, minute=0)
        scheduler.start()

def get_session():
    with Session(engine) as session:
        yield session

# ---------------------------------------------------------
# LÓGICA AUTOMÁTICA DEL BOLILLERO DOMINICAL
# ---------------------------------------------------------
scheduler = BackgroundScheduler()

def sorteo_dominical_automatico():
    with Session(engine) as session:
        # Validación estricta: Solo participan usuarios con cartón pagado
        participantes = session.exec(
            select(ApuestaBolillero).where(ApuestaBolillero.pagado == True)
        ).all()
        
        if participantes:
            ganador = random.choice(participantes)
            print(f"[{datetime.now()}] ¡Sorteo dominical ejecutado! Ganador DNI: {ganador.dni_usuario}")
        else:
            print(f"[{datetime.now()}] Sorteo dominical cancelado: No hay cartones pagados registrados.")

# ---------------------------------------------------------
# RUTAS DE LA APLICACIÓN (FRONTEND Y BACKEND)
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return HTMLResponse(content=""""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max Shop - Sorteos y Ruleta</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .ruleta-container {
            position: relative;
            width: 320px;
            height: 320px;
            margin: 0 auto;
        }
        .ruleta-wheel {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 8px solid #f59e0b;
            position: relative;
            overflow: hidden;
            transition: transform 4s cubic-bezier(0.15, 0.75, 0.14, 1);
            background: conic-gradient(
                #facc15 0deg 36deg,
                #10b981 36deg 72deg,
                #3b82f6 72deg 108deg,
                #8b5cf6 108deg 144deg,
                #ec4899 144deg 180deg,
                #f97316 180deg 216deg,
                #06b6d4 216deg 252deg,
                #6366f1 252deg 288deg,
                #14b8a6 288deg 324deg,
                #eab308 324deg 360deg
            );
        }
        .pointer {
            width: 0; 
            height: 0; 
            border-left: 15px solid transparent;
            border-right: 15px solid transparent;
            border-bottom: 30px solid #ef4444;
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 20;
        }
        .center-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 70px;
            height: 70px;
            background: #b45309;
            border: 4px solid #fff;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body class="bg-[#0b0f19] text-white font-sans antialiased">

    <!-- Header -->
    <header class="flex justify-between items-center p-4 border-b border-slate-800">
        <div class="flex items-center gap-2">
            <span class="text-xl font-black bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Max%Shop</span>
        </div>
        <a href="#ruleta-section" class="bg-gradient-to-r from-amber-500 to-orange-600 px-4 py-2 rounded-xl font-bold text-sm shadow-lg">PARTICIPAR $1,000</a>
    </header>

    <main class="max-w-md mx-auto p-4 space-y-8 pb-12">
        
        <!-- BANNER ESTÁTICO -->
        <div class="w-full static">
            <img src="https://lh3.googleusercontent.com/d/1M7-vHb8XMAVgecZdlYe9UBo9SH_mDoEI" alt="Banner Principal Max Shop" class="w-full h-auto object-cover rounded-2xl shadow-xl border border-slate-700 block">
        </div>

        <!-- Pozo Acumulado y Bolillero -->
        <div class="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl text-center shadow-xl">
            <span class="bg-orange-500/10 text-orange-400 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">🔥 Club de Beneficios y Sorteos</span>
            <h1 class="text-3xl font-black mt-4">Pozo Acumulado</h1>
            <p class="text-4xl font-extrabold text-amber-500 mt-2">$400,000</p>
            <p class="text-sm text-slate-400 mt-3">Disfruta de la red de comercios, cobertura familiar y participa por el bolillero dominical automático todos los domingos a las 19:00 hs.</p>
            
            <form action="/app/comprar-carton" method="POST" class="mt-6">
                <input type="text" name="dni" required placeholder="Tu DNI para el cartón" class="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-white mb-3 focus:outline-none focus:border-amber-500 text-sm">
                <button type="submit" class="w-full bg-gradient-to-r from-amber-500 to-orange-600 font-bold py-3 rounded-xl shadow-lg">COMPRAR CARTÓN DOMINICAL ($1,000)</button>
            </form>
        </div>

        <!-- SECCIÓN RULETA -->
        <div id="ruleta-section" class="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-6">
            <h2 class="text-xl font-bold text-center">Gira y Gana Premios</h2>
            
            <div class="ruleta-container">
                <div class="pointer"></div>
                <div class="ruleta-wheel" id="wheel"></div>
                <div class="center-btn">GIRAR</div>
            </div>

            <form id="ruletaForm" action="/app/pagar-ruleta" method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-1">Tu DNI de Socio</label>
                    <input type="text" id="dniSocio" name="dni" required placeholder="Ingresa tu DNI" class="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-white focus:outline-none focus:border-amber-500">
                </div>
                <button type="submit" id="btnGirarRuleta" class="w-full bg-blue-600 hover:bg-blue-500 font-bold py-3 rounded-xl shadow-lg transition-all">
                    GIRAR RULETA ($5,000)
                </button>
            </form>
        </div>

    </main>

    <script>
        document.getElementById('ruletaForm').addEventListener('submit', function(e) {
            const dni = document.getElementById('dniSocio').value.trim();
            if (!dni) {
                alert('Por favor, completa tu DNI de Socio antes de girar.');
                e.preventDefault();
            }
        });
    </script>
</body>
</html>
""")

@app.post("/app/comprar-carton")
def comprar_carton(dni: str = Form(...), session: Session = Depends(get_session)):
    # Registrar la apuesta pendiente de pago para el bolillero dominical
    nueva_apuesta = ApuestaBolillero(dni_usuario=dni, pagado=False)
    session.add(nueva_apuesta)
    session.commit()
    return RedirectResponse(url="/app/pago-exitoso?tipo=carton_dominical", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/app/pagar-ruleta")
def pagar_ruleta(dni: str = Form(...), session: Session = Depends(get_session)):
    nuevo_giro = GiroRuleta(dni_usuario=dni, premio="Pendiente", pagado=False)
    session.add(nuevo_giro)
    session.commit()
    return RedirectResponse(url="/app/pago-exitoso?tipo=ruleta", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/app/pago-exitoso", response_class=HTMLResponse)
def pago_exitoso(tipo: str):
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Pago Exitoso - Max Shop</title>
    </head>
    <body class="bg-[#0b0f19] text-white flex items-center justify-center h-screen">
        <div class="bg-slate-900 border border-slate-800 p-8 rounded-2xl text-center max-w-md shadow-2xl">
            <h1 class="text-2xl font-bold text-green-400 mb-2">¡Operación Exitosa!</h1>
            <p class="text-slate-300 mb-6">Tu pago para {tipo} se procesó con éxito.</p>
            <a href="/" class="bg-amber-500 text-slate-950 font-bold px-6 py-3 rounded-xl shadow-lg">Volver al Inicio</a>
        </div>
    </body>
    </html>
    """)
