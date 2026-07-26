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
app = FastAPI(title="MaxShop - Club de Descuentos & Pagos", version="4.0.0")

# --- Interfaz Comercial Interactiva de Alta Gama ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop | Club de Descuentos y Pagos Inteligentes</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; }
            .glass-card { background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(16px); border: 1px solid rgba(51, 65, 85, 0.4); }
        </style>
    </head>
    <body class="bg-[#020617] text-slate-100 min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
        
        <!-- Barra de Navegación Comercial -->
        <header class="border-b border-slate-800/80 bg-[#020617]/90 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 py-3.5 flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 font-extrabold text-lg text-slate-950">M</div>
                    <div>
                        <div class="flex items-center space-x-2">
                            <h1 class="font-bold text-base leading-tight tracking-tight">MaxShop</h1>
                            <span class="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">Club Premium</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Beneficios, Descuentos & Pagos QR</p>
                    </div>
                </div>
                
                <!-- Menú de Opciones Interactivo -->
                <nav class="hidden md:flex items-center space-x-1 text-xs">
                    <button onclick="switchSection('home')" id="navHome" class="px-3 py-2 rounded-lg bg-slate-800 text-white font-medium transition">Inicio</button>
                    <button onclick="switchSection('catalog')" id="navCatalog" class="px-3 py-2 rounded-lg text-slate-400 hover:text-white transition">Comercios & Ofertas</button>
                    <button onclick="switchSection('register')" id="navRegister" class="px-3 py-2 rounded-lg text-slate-400 hover:text-white transition">Asociarme / Comercios</button>
                    <button onclick="switchSection('pay')" id="navPay" class="px-3 py-2 rounded-lg text-slate-400 hover:text-white transition">Caja & Pago QR</button>
                    <button onclick="switchSection('contact')" id="navContact" class="px-3 py-2 rounded-lg text-slate-400 hover:text-white transition">Contacto</button>
                </nav>
            </div>
        </header>

        <!-- Contenido Dinámico -->
        <main class="max-w-6xl mx-auto px-4 py-8 w-full flex-grow space-y-10">
            
            <!-- SECCIÓN INICIO: HERO & PUBLICIDAD BANCOS / TARJETAS -->
            <section id="secHome" class="space-y-8">
                <!-- Banner Principal -->
                <div class="glass-card rounded-3xl p-8 md:p-12 relative overflow-hidden shadow-2xl border-emerald-500/20">
                    <div class="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
                    <div class="max-w-2xl space-y-4 relative z-10">
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">La forma más inteligente de comprar</span>
                        <h2 class="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">Ahorrá en cada compra con tu membresía MaxShop</h2>
                        <p class="text-slate-300 text-sm md:text-base leading-relaxed">
                            Olvidate de los cupones físicos. Pagá escaneando un código QR en caja o desde tu celular de forma instantánea. Descuentos automáticos en las mejores marcas, farmacias, indumentaria y hogar.
                        </p>
                        <div class="flex flex-wrap gap-3 pt-2">
                            <button onclick="switchSection('register')" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-6 py-3 rounded-xl text-sm transition shadow-lg shadow-emerald-500/20">Quiero ser Socio</button>
                            <button onclick="switchSection('catalog')" class="bg-slate-800 hover:bg-slate-700 text-white font-semibold px-6 py-3 rounded-xl text-sm border border-slate-700 transition">Ver Ofertas</button>
                        </div>
                    </div>
                </div>

                <!-- Espacio Publicitario: Bancos y Tarjetas Asociadas -->
                <div class="space-y-3">
                    <p class="text-xs uppercase tracking-wider text-slate-400 font-semibold text-center">Bancos y Medios de Pago Aliados con Beneficios Acumulables</p>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-300 font-bold text-sm border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> <span>Visa & Mastercard</span>
                        </div>
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-300 font-bold text-sm border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> <span>Banco Galicia / Macro</span>
                        </div>
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-300 font-bold text-sm border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> <span>Modo & Mercado Pago</span>
                        </div>
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-300 font-bold text-sm border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span> <span>BBVA / Santander</span>
                        </div>
                    </div>
                </div>

                <!-- Cómo Funciona (Explicación limpia y rápida) -->
                <div class="grid md:grid-cols-3 gap-6 pt-4">
                    <div class="glass-card p-6 rounded-2xl space-y-3">
                        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-lg">1</div>
                        <h3 class="font-bold text-base text-white">Registro Exprés</h3>
                        <p class="text-xs text-slate-400 leading-relaxed">Te registrás con tu correo en segundos. Activás tu membresía sin trámites engorrosos ni papeleo.</p>
                    </div>
                    <div class="glass-card p-6 rounded-2xl space-y-3">
                        <div class="w-10 h-10 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center font-bold text-lg">2</div>
                        <h3 class="font-bold text-base text-white">Elegís el Comercio</h3>
                        <p class="text-xs text-slate-400 leading-relaxed">Navegá por nuestra red de marcas en indumentaria, tecnología, gastronomía, farmacias y mucho más.</p>
                    </div>
                    <div class="glass-card p-6 rounded-2xl space-y-3">
                        <div class="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-lg">3</div>
                        <h3 class="font-bold text-base text-white">Pago QR Inteligente</h3>
                        <p class="text-xs text-slate-400 leading-relaxed">Escaneás el QR en caja o simulás el cobro: el descuento se aplica solo y pagás menos al instante.</p>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN CATÁLOGO & OFERTAS (Rubros y Comercios) -->
            <section id="secCatalog" class="hidden space-y-6">
                <div class="flex justify-between items-center">
                    <div>
                        <h2 class="text-2xl font-bold text-white">Catálogo de Ofertas y Comercios Adheridos</h2>
                        <p class="text-xs text-slate-400">Descubrí dónde podés usar tus beneficios hoy mismo.</p>
                    </div>
                </div>

                <!-- Grilla de Ofertas con imágenes representativas simuladas -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- Tarjeta 1: Indumentaria -->
                    <div class="glass-card rounded-2xl overflow-hidden group shadow-lg">
                        <div class="h-36 bg-gradient-to-tr from-indigo-900 to-slate-800 p-4 flex flex-col justify-between relative">
                            <span class="bg-indigo-500 text-white text-[10px] font-bold px-2.5 py-1 rounded-full w-max">25% OFF</span>
                            <span class="text-2xl font-bold text-white">🧥 Indumentaria & Moda</span>
                        </div>
                        <div class="p-4 space-y-2">
                            <h3 class="font-bold text-sm text-white">Zoot & Marken Store</h3>
                            <p class="text-xs text-slate-400">Descuento exclusivo en toda la temporada otoño-invierno.</p>
                            <button onclick="switchSection('pay')" class="w-full mt-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-semibold py-2 rounded-xl transition">Usar Beneficio</button>
                        </div>
                    </div>

                    <!-- Tarjeta 2: Electrodomésticos -->
                    <div class="glass-card rounded-2xl overflow-hidden group shadow-lg">
                        <div class="h-36 bg-gradient-to-tr from-cyan-900 to-slate-800 p-4 flex flex-col justify-between relative">
                            <span class="bg-cyan-500 text-slate-950 text-[10px] font-bold px-2.5 py-1 rounded-full w-max">15% OFF</span>
                            <span class="text-2xl font-bold text-white">⚡ Electro & Tecnología</span>
                        </div>
                        <div class="p-4 space-y-2">
                            <h3 class="font-bold text-sm text-white">TecnoHouse Digital</h3>
                            <p class="text-xs text-slate-400">Smart TVs, audio y línea blanca con cuotas sin interés.</p>
                            <button onclick="switchSection('pay')" class="w-full mt-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-semibold py-2 rounded-xl transition">Usar Beneficio</button>
                        </div>
                    </div>

                    <!-- Tarjeta 3: Farmacias -->
                    <div class="glass-card rounded-2xl overflow-hidden group shadow-lg">
                        <div class="h-36 bg-gradient-to-tr from-emerald-900 to-slate-800 p-4 flex flex-col justify-between relative">
                            <span class="bg-emerald-500 text-slate-950 text-[10px] font-bold px-2.5 py-1 rounded-full w-max">20% OFF</span>
                            <span class="text-2xl font-bold text-white">💊 Farmacia & Perfumería</span>
                        </div>
                        <div class="p-4 space-y-2">
                            <h3 class="font-bold text-sm text-white">Red FarmaSalud</h3>
                            <p class="text-xs text-slate-400">Descuentos en medicamentos genéricos y perfumería selecta.</p>
                            <button onclick="switchSection('pay')" class="w-full mt-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-semibold py-2 rounded-xl transition">Usar Beneficio</button>
                        </div>
                    </div>

                    <!-- Tarjeta 4: Muebles y Hogar -->
                    <div class="glass-card rounded-2xl overflow-hidden group shadow-lg">
                        <div class="h-36 bg-gradient-to-tr from-amber-900 to-slate-800 p-4 flex flex-col justify-between relative">
                            <span class="bg-amber-500 text-slate-950 text-[10px] font-bold px-2.5 py-1 rounded-full w-max">30% OFF</span>
                            <span class="text-2xl font-bold text-white">🛋️ Muebles & Decoración</span>
                        </div>
                        <div class="p-4 space-y-2">
                            <h3 class="font-bold text-sm text-white">Habitat Design</h3>
                            <p class="text-xs text-slate-400">Renová tus espacios con mobiliario de diseño moderno.</p>
                            <button onclick="switchSection('pay')" class="w-full mt-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-semibold py-2 rounded-xl transition">Usar Beneficio</button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN REGISTRO: ASOCIARME O INTEGRAR COMERCIO -->
            <section id="secRegister" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto space-y-6">
                    <div class="text-center space-y-2">
                        <h2 class="text-2xl font-bold text-white">Centro de Altas y Registros</h2>
                        <p class="text-xs text-slate-400">Sumate como socio para recibir descuentos o registrá tu comercio para formar parte de la red.</p>
                    </div>

                    <!-- Pestañas internas de registro -->
                    <div class="grid grid-cols-2 gap-2 bg-slate-900 p-1.5 rounded-2xl border border-slate-800 text-xs font-semibold">
                        <button onclick="switchRegSub('user')" id="btnSubUser" class="py-2.5 rounded-xl bg-slate-800 text-white transition">1. Asociarme (Cliente)</button>
                        <button onclick="switchRegSub('merchant')" id="btnSubMerchant" class="py-2.5 rounded-xl text-slate-400 hover:text-white transition">2. Integrar Comercio</button>
                    </div>

                    <!-- Formulario Usuario -->
                    <div id="formUserBox" class="glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-sm font-bold text-emerald-400 uppercase tracking-wider">Registro Rápido de Socio</h3>
                        <form id="userForm" class="space-y-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Correo Electrónico</label>
                                <input type="email" id="userEmail" required placeholder="tu_correo@email.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Estado de Membresía</label>
                                <select id="userStatus" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                                    <option value="active">Activa (Con beneficios plenos)</option>
                                    <option value="inactive">Inactiva</option>
                                </select>
                            </div>
                            <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-3 rounded-xl text-sm transition shadow-lg shadow-emerald-500/20">Obtener Membresía Gratis</button>
                        </form>
                        <div id="userResult" class="mt-4 hidden"></div>
                    </div>

                    <!-- Formulario Comercio -->
                    <div id="formMerchantBox" class="hidden glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-sm font-bold text-teal-400 uppercase tracking-wider">Integración de Comercio y Descuentos</h3>
                        <form id="merchantForm" class="space-y-3">
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Nombre del Comercio</label>
                                    <input type="text" id="mercName" required placeholder="Ej: Zoot Store" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Rubro</label>
                                    <input type="text" id="mercCat" required placeholder="Ej: Indumentaria" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">ID Comercio</label>
                                    <input type="number" id="discMerchantId" required placeholder="Ej: 1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">% Descuento</label>
                                    <input type="number" step="0.1" id="discPercentage" required placeholder="Ej: 25" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                                </div>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Título de la Promo</label>
                                <input type="text" id="discTitle" required placeholder="Ej: 25% Club MaxShop" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm focus:outline-none focus:border-teal-500 transition">
                            </div>
                            <button type="submit" class="w-full bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold py-3 rounded-xl text-sm transition shadow-lg shadow-teal-500/20">Registrar Comercio y Descuento</button>
                        </form>
                        <div id="merchantResult" class="mt-4 hidden"></div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN CAJA Y PAGO QR INTELIGENTE -->
            <section id="secPay" class="hidden space-y-6">
                <div class="max-w-xl mx-auto glass-card rounded-2xl p-8 shadow-2xl border-emerald-500/30 relative">
                    <div class="absolute -top-3 right-6 bg-emerald-500 text-slate-950 text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">Caja Inteligente QR</div>
                    <div class="space-y-2 mb-6">
                        <h2 class="text-xl font-bold text-white">Simulador de Pago en Caja</h2>
                        <p class="text-xs text-slate-400">Escaneá o ingresá los datos de tu compra. El sistema valida tu membresía y aplica el beneficio al instante.</p>
                    </div>

                    <form id="paymentForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio</label>
                            <input type="email" id="payEmail" required placeholder="tu_correo@email.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">ID del Comercio</label>
                                <input type="number" id="payMerchant" required placeholder="Ej: 1" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total ($)</label>
                                <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 18000" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                            </div>
                        </div>
                        <button type="submit" class="w-full bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 text-slate-950 font-bold py-3.5 rounded-xl text-sm transition shadow-xl shadow-emerald-500/20">Pagar con Descuento Automático</button>
                    </form>

                    <div id="paymentResult" class="mt-6 hidden"></div>
                </div>
            </section>

            <!-- SECCIÓN CONTACTO Y SOPORTE -->
            <section id="secContact" class="hidden space-y-6">
                <div class="max-w-xl mx-auto glass-card rounded-2xl p-8 space-y-6 text-center">
                    <h2 class="text-2xl font-bold text-white">Canales de Comunicación y Soporte</h2>
                    <p class="text-xs text-slate-400 leading-relaxed">
                        ¿Tenés dudas sobre tu membresía, querés sumar tu cadena de comercios o necesitás asistencia técnica con las pasarelas de pago? Estamos para ayudarte.
                    </p>
                    <div class="grid grid-cols-2 gap-4 pt-2">
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                            <span class="text-emerald-400 font-bold block mb-1 text-sm">💬 WhatsApp Comercial</span>
                            <span class="text-xs text-slate-300">+54 9 11 5555-MAXSHOP</span>
                        </div>
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                            <span class="text-teal-400 font-bold block mb-1 text-sm">✉️ Soporte Empresas</span>
                            <span class="text-xs text-slate-300">empresas@maxshop.com</span>
                        </div>
                    </div>
                </div>
            </section>

        </main>

        <!-- Footer -->
        <footer class="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
            <p>MaxShop Corporation • Club de Beneficios, Descuentos & Pagos Inteligentes</p>
        </footer>

        <!-- JavaScript de Navegación e Interactividad -->
        <script>
            function switchSection(sectionId) {
                const sections = ['home', 'catalog', 'register', 'pay', 'contact'];
                sections.forEach(s => {
                    document.getElementById('sec' + s.charAt(0).toUpperCase() + s.slice(1)).classList.add('hidden');
                    const navBtn = document.getElementById('nav' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(navBtn) navBtn.className = "px-3 py-2 rounded-lg text-slate-400 hover:text-white transition";
                });

                document.getElementById('sec' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1)).classList.remove('hidden');
                const activeNav = document.getElementById('nav' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(activeNav) activeNav.className = "px-3 py-2 rounded-lg bg-slate-800 text-white font-medium transition";
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            function switchRegSub(type) {
                const uBox = document.getElementById('formUserBox');
                const mBox = document.getElementById('formMerchantBox');
                const bUser = document.getElementById('btnSubUser');
                const bMerchant = document.getElementById('btnSubMerchant');

                if(type === 'user') {
                    uBox.classList.remove('hidden');
                    mBox.classList.add('hidden');
                    bUser.className = "py-2.5 rounded-xl bg-slate-800 text-white transition";
                    bMerchant.className = "py-2.5 rounded-xl text-slate-400 hover:text-white transition";
                } else {
                    uBox.classList.add('hidden');
                    mBox.classList.remove('hidden');
                    bMerchant.className = "py-2.5 rounded-xl bg-slate-800 text-white transition";
                    bUser.className = "py-2.5 rounded-xl text-slate-400 hover:text-white transition";
                }
            }

            // Registrar Usuario
            document.getElementById('userForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('userEmail').value;
                const status = document.getElementById('userStatus').value;
                const resDiv = document.getElementById('userResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-slate-950 text-xs text-slate-400 animate-pulse">Procesando membresía...</div>`;

                try {
                    const response = await fetch(`/users/?email=${encodeURIComponent(email)}&subscription_status=${status}`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.error) {
                        resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">⚠️ ${data.error}</div>`;
                    } else {
                        resDiv.innerHTML = `
                            <div class="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 space-y-2">
                                <span class="font-bold text-emerald-400 text-xs">✨ ¡Membresía Activada con Éxito!</span>
                                <p class="text-xs text-slate-300">Socio: <strong class="text-white">${data.email}</strong></p>
                                <div class="pt-2 border-t border-emerald-500/20 text-[11px] text-emerald-300 flex justify-between items-center">
                                    <span>Ya podés usar tus descuentos en caja.</span>
                                    <button onclick="switchSection('pay')" class="underline font-bold">Ir a Pagar ➔</button>
                                </div>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error de conexión.</div>`;
                }
            });

            // Registrar Comercio
            document.getElementById('merchantForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('mercName').value;
                const cat = document.getElementById('mercCat').value;
                const mId = document.getElementById('discMerchantId').value;
                const perc = document.getElementById('discPercentage').value;
                const title = document.getElementById('discTitle').value;
                const resDiv = document.getElementById('merchantResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-slate-950 text-xs text-slate-400 animate-pulse">Integrando comercio...</div>`;

                try {
                    await fetch(`/merchants/?name=${encodeURIComponent(name)}&category=${encodeURIComponent(cat)}`, { method: 'POST' });
                    await fetch(`/discounts/?title=${encodeURIComponent(title)}&percentage=${perc}&merchant_id=${mId}`, { method: 'POST' });

                    resDiv.innerHTML = `
                        <div class="p-4 rounded-xl bg-teal-950/40 border border-teal-500/30 space-y-2">
                            <span class="font-bold text-teal-400 text-xs">🏢 ¡Comercio Integrado a la Red!</span>
                            <p class="text-xs text-slate-300">${name} (${cat}) - <strong class="text-teal-400">${perc}% OFF</strong></p>
                            <div class="pt-2 border-t border-teal-500/20 text-[11px] text-teal-300 flex justify-between items-center">
                                <span>Listo para recibir pagos con descuento.</span>
                                <button onclick="switchSection('pay')" class="underline font-bold">Probar Caja ➔</button>
                            </div>
                        </div>`;
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error al registrar comercio.</div>`;
                }
            });

            // Simular Pago
            document.getElementById('paymentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('payEmail').value;
                const merchantId = document.getElementById('payMerchant').value;
                const amount = document.getElementById('payAmount').value;
                const resDiv = document.getElementById('paymentResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-4 rounded-xl bg-slate-950 text-xs text-slate-400 animate-pulse text-center">Procesando pago QR inteligente...</div>`;

                try {
                    const response = await fetch(`/process-payment/?user_email=${encodeURIComponent(email)}&merchant_id=${merchantId}&total_amount=${amount}`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.error) {
                        resDiv.innerHTML = `
                            <div class="p-4 rounded-xl bg-amber-950/40 border border-amber-500/40 space-y-2">
                                <span class="font-bold text-amber-400 text-xs">⚠️ Pago no autorizado</span>
                                <p class="text-xs text-amber-200">${data.error}</p>
                            </div>`;
                    } else {
                        resDiv.innerHTML = `
                            <div class="p-5 rounded-xl bg-gradient-to-br from-emerald-950/50 to-slate-900 border border-emerald-500/40 space-y-3">
                                <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                                    <span class="font-bold text-emerald-400 text-sm">✅ ¡Pago QR Exitoso!</span>
                                    <span class="text-xs bg-emerald-500 text-slate-950 px-2.5 py-0.5 rounded-full font-bold">${data.discount_applied || '0%'} OFF</span>
                                </div>
                                <div class="grid grid-cols-2 gap-2 text-xs">
                                    <div class="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                                        <span class="text-slate-400 block text-[10px]">Monto Original</span>
                                        <span class="text-white font-mono font-bold">$${data.original_amount}</span>
                                    </div>
                                    <div class="bg-emerald-950/40 p-2.5 rounded-lg border border-emerald-500/30">
                                        <span class="text-emerald-300 block text-[10px]">Ahorro Club</span>
                                        <span class="text-emerald-400 font-mono font-bold">-$${data.amount_saved}</span>
                                    </div>
                                </div>
                                <div class="bg-slate-950 p-3 rounded-xl border border-emerald-500/30 flex justify-between items-center">
                                    <span class="text-xs font-semibold text-slate-300">Total Final Cobrado:</span>
                                    <span class="text-lg font-extrabold font-mono text-emerald-400">$${data.final_amount_to_pay}</span>
                                </div>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-4 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error de conexión en caja.</div>`;
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
            return {"error": "Usuario no encontrado. Registrate primero."}
        if user.subscription_status != "active":
            return {"error": "Membresía inactiva. El descuento no se pudo aplicar."}
        
        discount = db.query(DiscountDB).filter(DiscountDB.merchant_id == merchant_id).first()
        if not discount:
            return {
                "message": "Pago procesado sin descuentos vigentes.",
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
