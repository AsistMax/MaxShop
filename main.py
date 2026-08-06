import os
from datetime import datetime
from typing import Optional
import mercadopago

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
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

app = FastAPI(title="Max%Shop - Sistema Robusto de Gestión y Pagos")

# ==========================================
# MODELOS DE BASE DE DATOS (SQLMODEL)
# ==========================================

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)
    password: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
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

# ==========================================
# EVENTO DE INICIO
# ==========================================

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
                estado_suscripcion="Activo",
                monto_suscripcion=30000.0
            )
            session.add(admin_user)
            session.commit()

# ==========================================
# RUTAS DE LA APLICACIÓN (FRONTEND & BACKEND)
# ==========================================

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Max%Shop - Descuentos y Sorteos</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col justify-between">
        <header class="bg-slate-800 border-b border-slate-700 px-4 py-4 flex justify-between items-center w-full">
            <h1 class="text-lg sm:text-xl font-bold text-orange-400">Max % Shop</h1>
            <a href="/login" class="bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 rounded font-bold text-xs sm:text-sm transition">Registrarse / Ingresar</a>
        </header>

        <main class="container mx-auto px-4 py-8 flex-grow flex items-center justify-center">
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 sm:p-10 text-center space-y-6 shadow-xl w-full max-w-2xl mx-auto">
                <h2 class="text-2xl sm:text-4xl font-extrabold text-white">Pozo Acumulado <span class="text-orange-400 block sm:inline">$900,000</span></h2>
                <p class="text-slate-300 text-sm sm:text-base leading-relaxed">Disfruta de la red de comercios más grande, obtén cobertura de hasta 30 millones y participa por el bolillero dominical de forma totalmente integrada y segura.</p>
                <a href="/login" class="inline-block w-full sm:w-auto bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-lg font-bold text-base shadow-lg transition">Comenzar Ahora</a>
            </div>
        </main>
        
        <footer class="text-center py-4 text-xs text-slate-500 border-t border-slate-800">
            Max%Shop &copy; 2026 - Todos los derechos reservados.
        </footer>
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
        <title>Max%Shop - Ingreso</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 flex items-center justify-center h-screen text-slate-100 px-4">
        <div class="bg-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-sm border border-slate-700 space-y-6">
            <h2 class="text-2xl font-bold text-orange-400 text-center">Acceso a Socio</h2>
            <form action="/login" method="POST" class="space-y-4">
                <div>
                    <label class="block text-sm mb-1 text-slate-300">Correo Electrónico</label>
                    <input type="email" name="email" required class="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-orange-500">
                </div>
                <div>
                    <label class="block text-sm mb-1 text-slate-300">Contraseña</label>
                    <input type="password" name="password" required class="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:outline-none focus:border-orange-500">
                </div>
                <button type="submit" class="w-full bg-orange-500 hover:bg-orange-600 py-2.5 rounded font-bold text-white transition">Ingresar / Registrarse</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.post("/login")
def login_post(email: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(Usuario).where(Usuario.email == email, Usuario.password == password)).first()
        if not user:
            user = Usuario(nombre="Socio Nuevo", email=email, password=password)
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

        transacciones = session.exec(select(Transaccion).where(Transaccion.usuario_id == user.id)).all()
        
        historial_html = "".join([f"""
            <tr class="border-b border-slate-700/50 text-sm">
                <td class="p-3">{t.tipo}</td>
                <td class="p-3">${t.monto:,.2f}</td>
                <td class="p-3"><span class="px-2 py-1 rounded text-xs {'bg-emerald-500/20 text-emerald-400' if t.estado == 'approved' else 'bg-amber-500/20 text-amber-400'}">{t.estado}</span></td>
                <td class="p-3 text-slate-400">{t.fecha}</td>
            </tr>
        """ for t in transacciones]) if transacciones else '<tr><td colspan="4" class="p-4 text-center text-slate-500">Sin transacciones registradas aún.</td></tr>'

        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Panel de Socio - Max%Shop</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://sdk.mercadopago.com/js/v2"></script>
        </head>
        <body class="bg-slate-900 text-slate-100 min-h-screen">
            <nav class="bg-slate-800 border-b border-slate-700 px-6 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
                <h1 class="text-lg font-bold text-orange-400">Panel: {user.nombre}</h1>
                <div class="flex items-center space-x-4">
                    <span class="text-xs bg-slate-700 px-3 py-1 rounded-full text-slate-300">Estado: <strong class="text-emerald-400">{user.estado_suscripcion}</strong></span>
                    <a href="/" class="text-red-400 hover:text-red-300 font-semibold text-sm">Cerrar Sesión</a>
                </div>
            </nav>

            <main class="container mx-auto p-4 sm:p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow space-y-4">
                    <h3 class="text-lg font-bold text-orange-300">Comprar Número Directo ($1.000)</h3>
                    <p class="text-sm text-slate-400">Participa en el pozo acumulado dominical abonando online.</p>
                    <button onclick="iniciarPago('Numero_Bolillero', 1000)" class="w-full bg-orange-500 hover:bg-orange-600 py-2.5 rounded font-bold text-white transition">Pagar Número ($1.000)</button>
                </div>

                <div class="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow space-y-4">
                    <h3 class="text-lg font-bold text-orange-300">Gestión de Suscripción y Cobertura</h3>
                    <p class="text-sm text-slate-400">Selecciona tu nivel mensual:</p>
                    <select id="monto_suscripcion" class="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white">
                        <option value="10000">Plan Básico - $10.000 / mes (Cobertura 10M)</option>
                        <option value="20000">Plan Avanzado - $20.000 / mes (Cobertura 20M)</option>
                        <option value="30000">Plan Premium - $30.000 / mes (Cobertura 30M)</option>
                    </select>
                    <button onclick="iniciarSuscripcion()" class="w-full bg-emerald-600 hover:bg-emerald-500 py-2.5 rounded font-bold text-white transition">Suscribirse al Monto Seleccionado</button>
                </div>

                <div class="md:col-span-2 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow space-y-4">
                    <h3 class="text-lg font-bold text-white">Pasarela de Pago Integrada</h3>
                    <div id="paymentBrick_container" class="min-h-[350px]"></div>
                </div>

                <div class="md:col-span-2 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow space-y-4">
                    <h3 class="text-lg font-bold text-white">Historial de Transacciones</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead>
                                <tr class="border-b border-slate-700 text-slate-400 text-sm">
                                    <th class="p-3">Concepto</th>
                                    <th class="p-3">Monto</th>
                                    <th class="p-3">Estado</th>
                                    <th class="p-3">Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {historial_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>

            <script>
                const mp = new MercadoPago('{PUBLIC_KEY}', {{ locale: 'es-AR' }});

                async function iniciarPago(tipo, monto) {{
                    const response = await fetch('/crear_preferencia', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ user_id: {user.id}, tipo: tipo, monto: monto }})
                    }});
                    const data = await response.json();
                    renderBrick(data.preference_id, tipo, monto);
                }}

                async function iniciarSuscripcion() {{
                    const monto = document.getElementById('monto_suscripcion').value;
                    iniciarPago('Suscripcion', parseFloat(monto));
                }}

                async function renderBrick(preferenceId, tipo, monto) {{
                    const container = document.getElementById('paymentBrick_container');
                    container.innerHTML = ""; 

                    const bricksBuilder = mp.bricks();
                    const settings = {{
                        initialization: {{ preferenceId: preferenceId }},
                        callbacks: {{
                            onReady: () => {{}},
                            onSubmit: (formData) => {{
                                return new Promise((resolve, reject) => {{
                                    fetch('/procesar_pago_brick', {{
                                        method: 'POST',
                                        headers: {{ 'Content-Type': 'application/json' }},
                                        body: JSON.stringify({{
                                            user_id: {user.id},
                                            tipo: tipo,
                                            monto: monto,
                                            payment_data: formData
                                        }})
                                    }})
                                    .then(res => res.json())
                                    .then(data => {{
                                        if(data.status === 'approved') {{
                                            alert('¡Pago procesado y aprobado con éxito!');
                                            window.location.reload();
                                            resolve();
                                        }} else {{
                                            alert('Pago pendiente o rechazado.');
                                            reject();
                                        }}
                                    }}).catch(() => reject());
                                }});
                            }},
                            onError: (error) => {{ console.error(error); }}
                        }}
                    }};
                    window.paymentBrickController = await bricksBuilder.create('payment', 'paymentBrick_container', settings);
                }}
            </script>
        </body>
        </html>
        """)

class PreferenciaRequest(BaseModel):
    user_id: int
    tipo: str
    monto: float

@app.post("/crear_preferencia")
def crear_preferencia(data: PreferenciaRequest):
    preference_data = {
        "items": [{
            "title": f"Max%Shop - {data.tipo}",
            "quantity": 1,
            "unit_price": data.monto
        }],
        "back_urls": {
            "success": f"http://localhost:8000/dashboard?user_id={data.user_id}",
            "failure": f"http://localhost:8000/dashboard?user_id={data.user_id}",
            "pending": f"http://localhost:8000/dashboard?user_id={data.user_id}"
        },
        "auto_return": "approved",
    }
    preference_response = sdk.preference().create(preference_data)
    return {"preference_id": preference_response["response"]["id"]}

class PagoBrickRequest(BaseModel):
    user_id: int
    tipo: str
    monto: float
    payment_data: dict

@app.post("/procesar_pago_brick")
def procesar_pago_brick(data: PagoBrickRequest):
    payment_response = sdk.payment().create(data.payment_data)
    payment = payment_response.get("response", {})
    
    status_pago = payment.get("status", "pending")
    payment_id = str(payment.get("id", ""))
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with Session(engine) as session:
        nueva_transaccion = Transaccion(
            usuario_id=data.user_id,
            tipo=data.tipo,
            monto=data.monto,
            estado=status_pago,
            payment_id=payment_id,
            fecha=hoy
        )
        session.add(nueva_transaccion)

        if status_pago == "approved" and data.tipo == "Suscripcion":
            user = session.get(Usuario, data.user_id)
            if user:
                user.estado_suscripcion = "Activo"
                user.monto_suscripcion = data.monto
                session.add(user)

        session.commit()

    return {"status": status_pago, "payment_id": payment_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
