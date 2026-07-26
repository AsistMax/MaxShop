import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Conexión a Supabase
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres.tyvrhprlkpatyoxbbyqd:MaxShop2026@aws-1-us-west-2.pooler.supabase.com:5432/postgres"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modelos de la Base de Datos ---
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    subscription_status = Column(String, default="inactive")

class MerchantDB(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)

class DiscountDB(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    percentage = Column(Numeric, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))

Base.metadata.create_all(bind=engine)

# --- Inicializar FastAPI ---
app = FastAPI(title="MaxShop - Club de Descuentos Pro", version="3.0.0")

# --- Interfaz Visual de Nivel Profesional (Frontend Avanzado) ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop | Club de Descuentos Inteligente</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; }
            .glass-card { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(51, 65, 85, 0.5); }
        </style>
    </head>
    <body class="bg-[#030712] text-slate-100 min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
        
        <!-- Barra de Navegación Profesional -->
        <header class="border-b border-slate-800/80 bg-[#030712]/80 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-5xl mx-auto px-4 py-3.5 flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 font-extrabold text-lg text-slate-950">M</div>
                    <div>
                        <div class="flex items-center space-x-2">
                            <h1 class="font-bold text-base leading-tight tracking-tight">MaxShop</h1>
                            <span class="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">PRO Cloud</span>
                        </div>
                        <p class="text-xs text-slate-400">Ecosistema inteligente de beneficios y pagos</p>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <button onclick="switchTab('dashboard')" id="btnNavDash" class="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 text-white transition">Panel Principal</button>
                    <button onclick="switchTab('about')" id="btnNavAbout" class="text-xs font-medium px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition">Guía y Arquitectura</button>
                </div>
            </div>
        </header>

        <!-- Contenido Principal -->
        <main class="max-w-5xl mx-auto px-4 py-8 w-full flex-grow">
            
            <!-- SECCIÓN 1: PANEL INTERACTIVO -->
            <div id="tabDashboard" class="space-y-6">
                
                <!-- Banner de Bienvenida y Guía de Pasos -->
                <div class="glass-card rounded-2xl p-6 relative overflow-hidden shadow-2xl">
                    <div class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>
                    <h2 class="text-xl font-bold mb-2 text-white">Centro de Control de Caja y Socios 🚀</h2>
                    <p class="text-sm text-slate-300 mb-6 leading-relaxed">
                        Bienvenido al simulador de transacciones de MaxShop. Para procesar un descuento exitoso en caja, seguí este flujo dinámico:
                    </p>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                            <span class="text-emerald-400 font-bold text-sm block mb-1">Paso 1</span>
                            Registrá tu correo y asegurate de tener la suscripción en estado <strong class="text-white">Activa</strong>.
                        </div>
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                            <span class="text-emerald-400 font-bold text-sm block mb-1">Paso 2</span>
                            Creá un comercio y asignale un porcentaje de descuento (Ej: Comercio ID 1 con 20%).
                        </div>
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                            <span class="text-emerald-400 font-bold text-sm block mb-1">Paso 3</span>
                            Simulá el pago ingresando el monto total: el sistema aplicará la rebaja de forma automática.
                        </div>
                    </div>
                </div>

                <!-- Grilla de Operaciones (Formularios Avanzados) -->
                <div class="grid md:grid-cols-2 gap-6">
                    
                    <!-- Columna Izquierda: Gestión (Usuarios y Comercios) -->
                    <div class="space-y-6">
                        
                        <!-- Tarjeta: Registrar Usuario -->
                        <div class="glass-card rounded-2xl p-6 shadow-xl">
                            <h3 class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4 flex items-center justify-between">
                                <span>1. Registro de Socio</span>
                                <span class="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">POST /users/</span>
                            </h3>
                            <form id="userForm" class="space-y-3">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Correo Electrónico</label>
                                    <input type="email" id="userEmail" required placeholder="socio@maxshop.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Estado de Beneficio</label>
                                    <select id="userStatus" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                                        <option value="active">Activa (Habilita descuentos)</option>
                                        <option value="inactive">Inactiva (Sin beneficios)</option>
                                    </select>
                                </div>
                                <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold py-2.5 rounded-xl text-sm transition shadow-lg shadow-emerald-500/10">Registrar Socio en Nube</button>
                            </form>
                            <div id="userResult" class="mt-4 hidden"></div>
                        </div>

                        <!-- Tarjeta: Crear Comercio y Descuento -->
                        <div class="glass-card rounded-2xl p-6 shadow-xl">
                            <h3 class="text-sm font-bold uppercase tracking-wider text-teal-400 mb-4 flex items-center justify-between">
                                <span>2. Alta de Comercio & Beneficio</span>
                                <span class="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">POST /merchants/</span>
                            </h3>
                            <form id="merchantForm" class="space-y-3">
                                <div class="grid grid-cols-2 gap-2">
                                    <div>
                                        <label class="block text-xs font-medium text-slate-400 mb-1">Comercio</label>
                                        <input type="text" id="mercName" required placeholder="Ej: Café Central" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                    </div>
                                    <div>
                                        <label class="block text-xs font-medium text-slate-400 mb-1">Rubro</label>
                                        <input type="text" id="mercCat" required placeholder="Ej: Gastronomía" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                    </div>
                                </div>
                                <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80">
                                    <div>
                                        <label class="block text-xs font-medium text-slate-400 mb-1">ID Comercio</label>
                                        <input type="number" id="discMerchantId" required placeholder="Ej: 1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                    </div>
                                    <div>
                                        <label class="block text-xs font-medium text-slate-400 mb-1">% Descuento</label>
                                        <input type="number" step="0.1" id="discPercentage" required placeholder="Ej: 15" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                    </div>
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Título Promo</label>
                                    <input type="text" id="discTitle" required placeholder="Ej: 15% Club MaxShop" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                </div>
                                <button type="submit" class="w-full bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold py-2.5 rounded-xl text-sm transition shadow-lg shadow-teal-500/10">Crear Comercio y Promoción</button>
                            </form>
                            <div id="merchantResult" class="mt-4 hidden"></div>
                        </div>

                    </div>

                    <!-- Columna Derecha: Simulador de Caja en Vivo -->
                    <div class="space-y-6">
                        <div class="glass-card rounded-2xl p-6 shadow-xl border-emerald-500/30 relative">
                            <div class="absolute -top-3 right-6 bg-emerald-500 text-slate-950 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-md">Caja Registradora</div>
                            <h3 class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">
                                3. Simulador de Pago Automático
                            </h3>
                            <p class="text-xs text-slate-400 mb-4">
                                Ingresá los datos de la compra en el comercio adherido. El motor evaluará el estado del socio y aplicará el descuento de forma instantánea.
                            </p>
                            <form id="paymentForm" class="space-y-4">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio Registrado</label>
                                    <input type="email" id="payEmail" required placeholder="socio@maxshop.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                                </div>
                                <div class="grid grid-cols-2 gap-3">
                                    <div>
                                        <label class="block text-xs font-medium text-slate-400 mb-1">ID del Comercio</label>
                                        <input type="number" id="payMerchant" required placeholder="Ej: 1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                                    </div>
                                    <div>
                                        <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total ($)</label>
                                        <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 12500" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                                    </div>
                                </div>
                                <button type="submit" class="w-full bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 text-slate-950 font-bold py-3 rounded-xl text-sm transition shadow-xl shadow-emerald-500/20">Procesar Transacción en Caja</button>
                            </form>
                            
                            <!-- Resultado Visual de Pago Profesional -->
                            <div id="paymentResult" class="mt-6 hidden"></div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- SECCIÓN 2: GUÍA Y ARQUITECTURA -->
            <div id="tabAbout" class="hidden space-y-6">
                <div class="glass-card rounded-2xl p-8 space-y-6">
                    <h2 class="text-2xl font-bold text-emerald-400">Arquitectura y Guía de MaxShop Pro 📘</h2>
                    <p class="text-slate-300 text-sm leading-relaxed">
                        MaxShop es una plataforma corporativa en la nube diseñada bajo una arquitectura moderna de alta disponibilidad. Combina un backend ultrarrápido en <strong class="text-white">FastAPI</strong> alojado en <strong class="text-white">Render</strong>, conectado de forma segura a una base de datos relacional PostgreSQL administrada en <strong class="text-white">Supabase</strong>.
                    </p>
                    <div class="grid md:grid-cols-2 gap-4 pt-4 border-t border-slate-800">
                        <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-2">
                            <h3 class="font-bold text-sm text-emerald-400">Seguridad y Validaciones</h3>
                            <p class="text-xs text-slate-400">Las transacciones validan restricciones de base de datos en tiempo real. Si un usuario no cuenta con suscripción activa, el motor bloquea el beneficio de forma automática.</p>
                        </div>
                        <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-2">
                            <h3 class="font-bold text-sm text-teal-400">Documentación Técnica</h3>
                            <p class="text-xs text-slate-400">¿Necesitás integrar esta API con una app móvil nativa? Podés consultar la especificación completa y los esquemas interactivos de endpoints en <a href="/docs" target="_blank" class="text-emerald-400 underline font-semibold">/docs (Swagger UI)</a>.</p>
                        </div>
                    </div>
                </div>
            </div>

        </main>

        <!-- Footer -->
        <footer class="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
            <p>MaxShop Corporation • Infraestructura Cloud Desplegada en Render & Supabase</p>
        </footer>

        <!-- JavaScript Dinámico & Profesional -->
        <script>
            function switchTab(tab) {
                const dash = document.getElementById('tabDashboard');
                const about = document.getElementById('tabAbout');
                const btnDash = document.getElementById('btnNavDash');
                const btnAbout = document.getElementById('btnNavAbout');

                if (tab === 'dashboard') {
                    dash.classList.remove('hidden');
                    about.classList.add('hidden');
                    btnDash.className = "text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 text-white transition";
                    btnAbout.className = "text-xs font-medium px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition";
                } else {
                    dash.classList.add('hidden');
                    about.classList.remove('hidden');
                    btnAbout.className = "text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 text-white transition";
                    btnDash.className = "text-xs font-medium px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition";
                }
            }

            // Registrar Usuario con Feedback Visual
            document.getElementById('userForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('userEmail').value;
                const status = document.getElementById('userStatus').value;
                const resDiv = document.getElementById('userResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 animate-pulse">Procesando registro en Supabase...</div>`;

                try {
                    const response = await fetch(`/users/?email=${encodeURIComponent(email)}&subscription_status=${status}`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.error) {
                        resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800/60 text-xs text-red-300">⚠️ ${data.error}</div>`;
                    } else {
                        resDiv.innerHTML = `
                            <div class="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-2">
                                <div class="flex items-center justify-between">
                                    <span class="font-bold text-emerald-400 text-xs">✨ ¡Socio Registrado con Éxito!</span>
                                    <span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-mono">ID: ${data.user_id}</span>
                                </div>
                                <p class="text-xs text-slate-300">Email: <strong class="text-white">${data.email}</strong></p>
                                <p class="text-[11px] text-slate-400">Estado: <span class="text-emerald-400 font-semibold uppercase">${data.subscription_status}</span></p>
                                <div class="pt-2 border-t border-emerald-500/20 text-[11px] text-emerald-300/80">
                                    👉 Siguiente paso: Registrá un comercio e ingresá este correo en el simulador de pago.
                                </div>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800/60 text-xs text-red-300">❌ Error de conexión con el servidor cloud.</div>`;
                }
            });

            // Crear Comercio y Descuento en Cadena
            document.getElementById('merchantForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('mercName').value;
                const cat = document.getElementById('mercCat').value;
                const mId = document.getElementById('discMerchantId').value;
                const perc = document.getElementById('discPercentage').value;
                const title = document.getElementById('discTitle').value;
                const resDiv = document.getElementById('merchantResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 animate-pulse">Registrando comercio y beneficio...</div>`;

                try {
                    // 1. Crear Comercio
                    const resM = await fetch(`/merchants/?name=${encodeURIComponent(name)}&category=${encodeURIComponent(cat)}`, { method: 'POST' });
                    const dataM = await resM.json();

                    // 2. Crear Descuento asociado
                    const resD = await fetch(`/discounts/?title=${encodeURIComponent(title)}&percentage=${perc}&merchant_id=${mId}`, { method: 'POST' });
                    const dataD = await resD.json();

                    resDiv.innerHTML = `
                        <div class="p-4 rounded-xl bg-teal-950/30 border border-teal-500/30 space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-teal-400 text-xs">🏢 ¡Comercio y Promo Activos!</span>
                                <span class="text-[10px] bg-teal-500/20 text-teal-300 px-2 py-0.5 rounded font-mono">Comercio ID: ${mId}</span>
                            </div>
                            <p class="text-xs text-slate-300">Comercio: <strong class="text-white">${name}</strong> (${cat})</p>
                            <p class="text-xs text-slate-300">Descuento aplicado en caja: <strong class="text-teal-400">${perc}% OFF</strong></p>
                            <div class="pt-2 border-t border-teal-500/20 text-[11px] text-teal-300/80">
                                💸 Todo listo. Ya podés ir al paso 3 y simular un pago con este comercio.
                            </div>
                        </div>`;
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800/60 text-xs text-red-300">❌ Error al registrar comercio o descuento.</div>`;
                }
            });

            // Simular Pago Profesional
            document.getElementById('paymentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('payEmail').value;
                const merchantId = document.getElementById('payMerchant').value;
                const amount = document.getElementById('payAmount').value;
                const resDiv = document.getElementById('paymentResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 animate-pulse text-center">Calculando beneficios y procesando caja...</div>`;

                try {
                    const response = await fetch(`/process-payment/?user_email=${encodeURIComponent(email)}&merchant_id=${merchantId}&total_amount=${amount}`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.error) {
                        resDiv.innerHTML = `
                            <div class="p-4 rounded-xl bg-amber-950/30 border border-amber-500/40 space-y-2">
                                <span class="font-bold text-amber-400 text-xs flex items-center space-x-1"><span>⚠️ Transacción No Completada</span></span>
                                <p class="text-xs text-amber-200/90">${data.error}</p>
                                <p class="text-[11px] text-slate-400 pt-1">Verificá que el email tenga la suscripción activa o que el comercio exista.</p>
                            </div>`;
                    } else {
                        resDiv.innerHTML = `
                            <div class="p-5 rounded-xl bg-gradient-to-br from-emerald-950/40 to-slate-900 border border-emerald-500/40 space-y-3 shadow-lg">
                                <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                                    <span class="font-extrabold text-emerald-400 text-sm">✅ ¡Pago Procesado en Caja!</span>
                                    <span class="text-xs bg-emerald-500 text-slate-950 px-2.5 py-0.5 rounded-full font-bold">${data.discount_applied || '0%'} OFF</span>
                                </div>
                                <div class="grid grid-cols-2 gap-2 text-xs">
                                    <div class="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
                                        <span class="text-slate-400 block text-[10px]">Monto Original</span>
                                        <span class="text-white font-mono font-bold">$${data.original_amount}</span>
                                    </div>
                                    <div class="bg-emerald-950/40 p-2.5 rounded-lg border border-emerald-500/30">
                                        <span class="text-emerald-300 block text-[10px]">Ahorro del Socio</span>
                                        <span class="text-emerald-400 font-mono font-bold">-$${data.amount_saved}</span>
                                    </div>
                                </div>
                                <div class="bg-slate-950 p-3 rounded-xl border border-emerald-500/30 flex justify-between items-center">
                                    <span class="text-xs font-semibold text-slate-300">Total Final a Pagar:</span>
                                    <span class="text-lg font-extrabold font-mono text-emerald-400">$${data.final_amount_to_pay}</span>
                                </div>
                                <p class="text-[11px] text-center text-slate-400 italic pt-1">${data.message}</p>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-xs text-red-300">❌ Error al procesar el pago en la nube.</div>`;
                }
            });
        </script>
    </body>
    </html>
    """

# --- Rutas de la API (Backend intacto) ---
@app.post("/users/")
def create_user(email: str, subscription_status: str = "inactive"):
    db = SessionLocal()
    try:
        existing_user = db.query(UserDB).filter(UserDB.email == email).first()
        if existing_user:
            return {"error": "El correo ya está registrado en el sistema"}
        new_user = UserDB(email=email, subscription_status=subscription_status)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Usuario registrado con éxito", "user_id": new_user.id, "email": new_user.email, "subscription_status": new_user.subscription_status}
    finally:
        db.close()

@app.post("/merchants/")
def create_merchant(name: str, category: str):
    db = SessionLocal()
    try:
        new_merchant = MerchantDB(name=name, category=category)
        db.add(new_merchant)
        db.commit()
        db.refresh(new_merchant)
        return {"message": "Comercio creado con éxito", "merchant_id": new_merchant.id, "name": new_merchant.name}
    finally:
        db.close()

@app.post("/discounts/")
def create_discount(title: str, percentage: float, merchant_id: int):
    db = SessionLocal()
    try:
        merchant = db.query(MerchantDB).filter(MerchantDB.id == merchant_id).first()
        if not merchant:
            return {"error": "El comercio indicado no existe"}
        new_discount = DiscountDB(title=title, percentage=percentage, merchant_id=merchant_id)
        db.add(new_discount)
        db.commit()
        db.refresh(new_discount)
        return {"message": "Descuento creado con éxito", "discount_id": new_discount.id, "title": new_discount.title, "percentage": float(new_discount.percentage)}
    finally:
        db.close()

@app.post("/process-payment/")
def process_payment(user_email: str, merchant_id: int, total_amount: float):
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.email == user_email).first()
        if not user:
            return {"error": "Usuario no encontrado en la base de datos de socios."}
        if user.subscription_status != "active":
            return {"error": "Suscripción inactiva. El beneficio de descuento no se puede aplicar."}
        
        discount = db.query(DiscountDB).filter(DiscountDB.merchant_id == merchant_id).first()
        if not discount:
            return {
                "message": "Pago procesado sin descuentos (el comercio no tiene promociones vigentes).",
                "original_amount": total_amount,
                "discount_applied": "0%",
                "amount_saved": 0.0,
                "final_amount_to_pay": total_amount
            }
        
        discount_percentage = float(discount.percentage)
        amount_saved = (total_amount * discount_percentage) / 100
        final_amount = total_amount - amount_saved
        
        return {
            "message": "¡Pago procesado con éxito! Descuento aplicado automáticamente en caja. 💸",
            "original_amount": total_amount,
            "discount_applied": f"{discount_percentage}%",
            "amount_saved": round(amount_saved, 2),
            "final_amount_to_pay": round(final_amount, 2)
        }
    finally:
        db.close()
