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
app = FastAPI(title="MaxShop - Club de Descuentos & Pagos", version="5.0.0")

# --- Interfaz Comercial Avanzada ---
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
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #040914; color: #f8fafc; }
            .brand-gradient { background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); }
            .brand-text-gradient { background: linear-gradient(135deg, #34d399 0%, #22d3ee 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .glass-card { background: rgba(11, 19, 38, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(30, 58, 138, 0.4); }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
        
        <!-- Barra de Navegación -->
        <header class="border-b border-slate-800/80 bg-[#040914]/90 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 py-3.5 flex justify-between items-center">
                
                <div class="flex items-center space-x-3 cursor-pointer" onclick="switchSection('home')">
                    <div class="w-11 h-11 rounded-2xl brand-gradient flex items-center justify-center shadow-lg shadow-emerald-500/20 transform hover:scale-105 transition">
                        <svg class="w-6 h-6 text-slate-950" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                    </div>
                    <div>
                        <div class="flex items-center space-x-2">
                            <h1 class="font-extrabold text-lg leading-tight tracking-tight text-white">Max<span class="text-emerald-400">Shop</span></h1>
                            <span class="text-[9px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">Club Pro</span>
                        </div>
                        <p class="text-[10px] text-slate-400 font-medium">Beneficios & Pagos Inteligentes</p>
                    </div>
                </div>
                
                <nav class="hidden md:flex items-center space-x-1 text-xs">
                    <button onclick="switchSection('home')" id="navHome" class="px-3.5 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition">Inicio</button>
                    <button onclick="switchSection('catalog')" id="navCatalog" class="px-3.5 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 transition">Comercios & Ofertas</button>
                    <button onclick="switchSection('banks')" id="navBanks" class="px-3.5 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 transition">Promos Bancarias</button>
                    <button onclick="switchSection('register')" id="navRegister" class="px-3.5 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 transition">Asociarme / Comercios</button>
                    <button onclick="switchSection('pay')" id="navPay" class="px-3.5 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 transition">Caja & Pago QR</button>
                </nav>
            </div>
        </header>

        <!-- Contenido Dinámico -->
        <main class="max-w-6xl mx-auto px-4 py-8 w-full flex-grow space-y-10">
            
            <!-- SECCIÓN INICIO -->
            <section id="secHome" class="space-y-8">
                <div class="glass-card rounded-3xl p-8 md:p-12 relative overflow-hidden shadow-2xl border-emerald-500/20">
                    <div class="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
                    <div class="max-w-2xl space-y-5 relative z-10">
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold px-3.5 py-1.5 rounded-full uppercase tracking-wider">Ecosistema Financiero y Comercial</span>
                        <h2 class="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">Ahorrá inteligentemente con tu membresía <span class="brand-text-gradient">MaxShop</span></h2>
                        <p class="text-slate-300 text-sm md:text-base leading-relaxed">
                            Acumulá los beneficios de MaxShop con tus tarjetas bancarias favoritas. Pagá escaneando códigos QR de forma instantánea con Mercado Pago.
                        </p>
                        <div class="flex flex-wrap gap-3 pt-2">
                            <button onclick="switchSection('register')" class="brand-gradient hover:opacity-90 text-slate-950 font-extrabold px-6 py-3.5 rounded-xl text-sm transition shadow-lg shadow-emerald-500/20">Quiero ser Socio</button>
                            <button onclick="switchSection('banks')" class="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-6 py-3.5 rounded-xl text-sm border border-slate-700 transition">Ver Promos Bancarias</button>
                        </div>
                    </div>
                </div>

                <!-- Alianzas Bancarias -->
                <div class="space-y-3">
                    <p class="text-[11px] uppercase tracking-wider text-slate-400 font-bold text-center">Entidades Financieras Asociadas (Promociones Acumulables)</p>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-200 font-bold text-xs border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> <span>Galicia Visual + 20%</span>
                        </div>
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-200 font-bold text-xs border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-red-500"></span> <span>Santander / MODO</span>
                        </div>
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-200 font-bold text-xs border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> <span>Macro Clientes Selecta</span>
                        </div>
                        <div class="glass-card p-4 rounded-xl flex items-center justify-center space-x-2 text-slate-200 font-bold text-xs border-slate-800">
                            <span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span> <span>BBVA Francés Go</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN CATÁLOGO DE OFERTAS -->
            <section id="secCatalog" class="hidden space-y-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">Catálogo de Comercios Aliados</h2>
                    <p class="text-xs text-slate-400">Seleccioná un local para aplicar tu beneficio directamente en caja.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" id="catalogGrid">
                    <!-- Se llena dinámicamente o por defecto -->
                    <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-indigo-500/20">
                        <div class="h-36 bg-gradient-to-tr from-indigo-950 to-slate-900 p-4 flex flex-col justify-between">
                            <span class="bg-indigo-500 text-white text-[10px] font-bold px-2.5 py-1 rounded-full w-max">25% OFF</span>
                            <span class="text-xl font-bold text-white">🧥 Zoot & Marken</span>
                        </div>
                        <div class="p-4 space-y-2">
                            <h3 class="font-bold text-sm text-white">Indumentaria & Moda</h3>
                            <p class="text-xs text-slate-400">ID Comercio: <span class="text-indigo-400 font-bold">1</span></p>
                            <button onclick="selectMerchantForPay(1)" class="w-full mt-2 bg-slate-900 hover:bg-slate-800 text-emerald-400 text-xs font-semibold py-2 rounded-xl transition border border-slate-800">Usar en Caja ➔</button>
                        </div>
                    </div>
                    <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-cyan-500/20">
                        <div class="h-36 bg-gradient-to-tr from-cyan-950 to-slate-900 p-4 flex flex-col justify-between">
                            <span class="bg-cyan-500 text-slate-950 text-[10px] font-bold px-2.5 py-1 rounded-full w-max">15% OFF</span>
                            <span class="text-xl font-bold text-white">⚡ TecnoHouse</span>
                        </div>
                        <div class="p-4 space-y-2">
                            <h3 class="font-bold text-sm text-white">Electro & Tecnología</h3>
                            <p class="text-xs text-slate-400">ID Comercio: <span class="text-cyan-400 font-bold">2</span></p>
                            <button onclick="selectMerchantForPay(2)" class="w-full mt-2 bg-slate-900 hover:bg-slate-800 text-emerald-400 text-xs font-semibold py-2 rounded-xl transition border border-slate-800">Usar en Caja ➔</button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN PROMOS BANCARIAS -->
            <section id="secBanks" class="hidden space-y-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">Promociones Bancarias Integradas</h2>
                    <p class="text-xs text-slate-400">Aprovechá las alianzas vigentes de las principales entidades financieras combinadas con MaxShop.</p>
                </div>
                <div class="grid md:grid-cols-3 gap-6">
                    <div class="glass-card p-6 rounded-2xl space-y-3 border-blue-500/30">
                        <span class="bg-blue-500/10 text-blue-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-blue-500/20">Banco Galicia</span>
                        <h3 class="text-lg font-bold text-white">Jueves de Supermercados & Moda</h3>
                        <p class="text-xs text-slate-400">30% de ahorro pagando con tarjetas Visa Débito y Crédito a través de MODO.</p>
                        <div class="text-[11px] text-blue-400 font-semibold pt-2">✨ Acumulable con Club MaxShop</div>
                    </div>
                    <div class="glass-card p-6 rounded-2xl space-y-3 border-red-500/30">
                        <span class="bg-red-500/10 text-red-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-red-500/20">Banco Santander</span>
                        <h3 class="text-lg font-bold text-white">Especial Shopping & Style</h3>
                        <p class="text-xs text-slate-400">Hasta 6 cuotas sin interés y 25% OFF en shoppings adheridos seleccionados.</p>
                        <div class="text-[11px] text-red-400 font-semibold pt-2">✨ Válido todos los días</div>
                    </div>
                    <div class="glass-card p-6 rounded-2xl space-y-3 border-amber-500/30">
                        <span class="bg-amber-500/10 text-amber-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-amber-500/20">Banco Macro</span>
                        <h3 class="text-lg font-bold text-white">Plan Vto Cero en Combustible y Farmacias</h3>
                        <p class="text-xs text-slate-400">20% de reintegro automático con cartera general usando QR directo.</p>
                        <div class="text-[11px] text-amber-400 font-semibold pt-2">✨ Beneficio exclusivo socios Pro</div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN REGISTRO (CON SUSCRIPCIÓN OCULTA Y MERCADO PAGO) -->
            <section id="secRegister" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto space-y-6">
                    <div class="text-center space-y-2">
                        <h2 class="text-2xl font-bold text-white">Centro de Altas y Membresías</h2>
                        <p class="text-xs text-slate-400">Unite a la red de socios o sumá tu comercio de forma automatizada.</p>
                    </div>

                    <div class="grid grid-cols-2 gap-2 bg-[#0b1326] p-1.5 rounded-2xl border border-slate-800 text-xs font-semibold">
                        <button onclick="switchRegSub('user')" id="btnSubUser" class="py-2.5 rounded-xl bg-emerald-500 text-slate-950 font-bold transition">1. Socio (Cliente)</button>
                        <button onclick="switchRegSub('merchant')" id="btnSubMerchant" class="py-2.5 rounded-xl text-slate-400 hover:text-white transition">2. Integrar Comercio</button>
                    </div>

                    <!-- Usuario -->
                    <div id="formUserBox" class="glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-sm font-bold text-emerald-400 uppercase tracking-wider">Alta Automática de Socio</h3>
                        <form id="userForm" class="space-y-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Correo Electrónico</label>
                                <input type="email" id="userEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                            </div>
                            
                            <!-- Membresía Costo Oculto hasta activar -->
                            <div id="userPaymentWrapper" class="hidden p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Membresía Mensual Socio Club:</span>
                                    <span class="text-emerald-400 font-bold text-sm">$1,500 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-3 rounded-xl text-xs transition shadow-lg shadow-blue-500/20">
                                    Pagar Suscripción en Mercado Pago ➔
                                </a>
                            </div>

                            <button type="submit" id="btnUserSubmit" class="w-full brand-gradient hover:opacity-90 text-slate-950 font-extrabold py-3 rounded-xl text-sm transition shadow-lg shadow-emerald-500/20">Continuar y Activar Membresía</button>
                        </form>
                        <div id="userResult" class="mt-4 hidden"></div>
                    </div>

                    <!-- Comercio (Con Costo Oculto de Publicidad $5000) -->
                    <div id="formMerchantBox" class="hidden glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-sm font-bold text-cyan-400 uppercase tracking-wider">Alta de Comercio y Publicidad</h3>
                        <form id="merchantForm" class="space-y-3">
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Nombre del Comercio</label>
                                    <input type="text" id="mercName" required placeholder="Ej: Zoot Store" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 transition">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Rubro</label>
                                    <input type="text" id="mercCat" required placeholder="Ej: Indumentaria" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 transition">
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">% Descuento a Ofrecer</label>
                                    <input type="number" step="0.1" id="discPercentage" required placeholder="Ej: 20" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 transition">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Título Promo</label>
                                    <input type="text" id="discTitle" required placeholder="Ej: 20% Club MaxShop" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 transition">
                                </div>
                            </div>

                            <!-- Costo Oculto Publicidad Mensual Comercio -->
                            <div id="merchantPaymentWrapper" class="hidden p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Costo por Publicidad en Red:</span>
                                    <span class="text-cyan-400 font-bold text-sm">$5,000 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-3 rounded-xl text-xs transition shadow-lg shadow-blue-500/20">
                                    Abonar Publicidad en Mercado Pago ➔
                                </a>
                            </div>

                            <button type="submit" id="btnMerchantSubmit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:opacity-90 text-slate-950 font-extrabold py-3 rounded-xl text-sm transition shadow-lg shadow-cyan-500/20">Generar Comercio Automáticamente</button>
                        </form>
                        <div id="merchantResult" class="mt-4 hidden"></div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN CAJA Y PAGO QR -->
            <section id="secPay" class="hidden space-y-6">
                <div class="max-w-xl mx-auto glass-card rounded-2xl p-8 shadow-2xl border-emerald-500/30 relative">
                    <div class="absolute -top-3 right-6 bg-emerald-500 text-slate-950 text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">Caja Inteligente QR</div>
                    <div class="space-y-2 mb-6">
                        <h2 class="text-xl font-bold text-white">Simulador de Pago en Caja</h2>
                        <p class="text-xs text-slate-400">Ingresá tu correo y seleccioná el comercio. El ID se autocompleta.</p>
                    </div>

                    <form id="paymentForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio</label>
                            <input type="email" id="payEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Comercio Adherido</label>
                                <select id="payMerchantSelect" onchange="document.getElementById('payMerchant').value = this.value;" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                                    <option value="1">Zoot & Marken (ID 1)</option>
                                    <option value="2">TecnoHouse (ID 2)</option>
                                </select>
                                <input type="hidden" id="payMerchant" value="1">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total ($)</label>
                                <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 18000" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition">
                            </div>
                        </div>
                        <button type="submit" class="w-full brand-gradient hover:opacity-90 text-slate-950 font-extrabold py-3.5 rounded-xl text-sm transition shadow-xl shadow-emerald-500/20">Pagar con Descuento Automático</button>
                    </form>

                    <div id="paymentResult" class="mt-6 hidden"></div>
                </div>
            </section>

        </main>

        <!-- Footer -->
        <footer class="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
            <p>MaxShop Corporation • Pagos procesados de forma segura mediante Mercado Pago</p>
        </footer>

        <!-- JavaScript Dinámico Automatizado -->
        <script>
            function switchSection(sectionId) {
                const sections = ['home', 'catalog', 'banks', 'register', 'pay'];
                sections.forEach(s => {
                    const el = document.getElementById('sec' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(el) el.classList.add('hidden');
                    const navBtn = document.getElementById('nav' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(navBtn) navBtn.className = "px-3.5 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 transition";
                });

                const targetSec = document.getElementById('sec' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(targetSec) targetSec.classList.remove('hidden');
                
                const activeNav = document.getElementById('nav' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(activeNav) activeNav.className = "px-3.5 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition";
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            function selectMerchantForPay(id) {
                document.getElementById('payMerchant').value = id;
                document.getElementById('payMerchantSelect').value = id;
                switchSection('pay');
            }

            function switchRegSub(type) {
                const uBox = document.getElementById('formUserBox');
                const mBox = document.getElementById('formMerchantBox');
                const bUser = document.getElementById('btnSubUser');
                const bMerchant = document.getElementById('btnSubMerchant');

                if(type === 'user') {
                    uBox.classList.remove('hidden');
                    mBox.classList.add('hidden');
                    bUser.className = "py-2.5 rounded-xl bg-emerald-500 text-slate-950 font-bold transition";
                    bMerchant.className = "py-2.5 rounded-xl text-slate-400 hover:text-white transition";
                } else {
                    uBox.classList.add('hidden');
                    mBox.classList.remove('hidden');
                    bMerchant.className = "py-2.5 rounded-xl bg-cyan-500 text-slate-950 font-bold transition";
                    bUser.className = "py-2.5 rounded-xl text-slate-400 hover:text-white transition";
                }
            }

            // Registro de Socio con revelado de costo y link de Mercado Pago
            document.getElementById('userForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('userEmail').value;
                const wrapper = document.getElementById('userPaymentWrapper');
                const btn = document.getElementById('btnUserSubmit');
                const resDiv = document.getElementById('userResult');

                if(wrapper.classList.contains('hidden')) {
                    wrapper.classList.remove('hidden');
                    btn.textContent = "Confirmar Registro en Sistema";
                    return;
                }

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-[#040914] text-xs text-slate-400 animate-pulse">Registrando socio automáticamente...</div>`;

                try {
                    const response = await fetch(`/users/?email=${encodeURIComponent(email)}&subscription_status=active`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.error) {
                        resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">⚠️ ${data.error}</div>`;
                    } else {
                        resDiv.innerHTML = `
                            <div class="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 space-y-2">
                                <span class="font-bold text-emerald-400 text-xs">✨ ¡Socio Registrado con Éxito!</span>
                                <p class="text-xs text-slate-300">Email: <strong class="text-white">${data.email}</strong></p>
                                <div class="pt-2 border-t border-emerald-500/20 text-[11px] text-emerald-300 flex justify-between items-center">
                                    <span>Membresía lista para operar en caja.</span>
                                    <button onclick="switchSection('pay')" class="underline font-bold">Ir a Pagar ➔</button>
                                </div>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error de conexión.</div>`;
                }
            });

            // Registro de Comercio con revelado de costo publicitario ($5000) y link de Mercado Pago
            document.getElementById('merchantForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('mercName').value;
                const cat = document.getElementById('mercCat').value;
                const perc = document.getElementById('discPercentage').value;
                const title = document.getElementById('discTitle').value;
                const wrapper = document.getElementById('merchantPaymentWrapper');
                const btn = document.getElementById('btnMerchantSubmit');
                const resDiv = document.getElementById('merchantResult');

                if(wrapper.classList.contains('hidden')) {
                    wrapper.classList.remove('hidden');
                    btn.textContent = "Finalizar Alta y Publicar";
                    return;
                }

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-[#040914] text-xs text-slate-400 animate-pulse">Generando comercio y descuento automáticamente...</div>`;

                try {
                    // 1. Crear Comercio Automático
                    const mRes = await fetch(`/merchants/?name=${encodeURIComponent(name)}&category=${encodeURIComponent(cat)}`, { method: 'POST' });
                    const mData = await mRes.json();
                    
                    if(mData.merchant_id) {
                        // 2. Crear Descuento Automático asociado al ID generado
                        await fetch(`/discounts/?title=${encodeURIComponent(title)}&percentage=${perc}&merchant_id=${mData.merchant_id}`, { method: 'POST' });
                        
                        resDiv.innerHTML = `
                            <div class="p-4 rounded-xl bg-cyan-950/40 border border-cyan-500/30 space-y-2">
                                <span class="font-bold text-cyan-400 text-xs">🏢 ¡Comercio Integrado Automáticamente!</span>
                                <p class="text-xs text-slate-300">${name} (${cat}) - <strong class="text-cyan-400">${perc}% OFF</strong> (ID asignado: ${mData.merchant_id})</p>
                                <div class="pt-2 border-t border-cyan-500/20 text-[11px] text-cyan-300 flex justify-between items-center">
                                    <span>Ya publicate tus beneficios en la red.</span>
                                    <button onclick="switchSection('pay')" class="underline font-bold">Probar Caja ➔</button>
                                </div>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error al registrar comercio.</div>`;
                }
            });

            // Pago en Caja
            document.getElementById('paymentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('payEmail').value;
                const merchantId = document.getElementById('payMerchant').value;
                const amount = document.getElementById('payAmount').value;
                const resDiv = document.getElementById('paymentResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-4 rounded-xl bg-[#040914] text-xs text-slate-400 animate-pulse text-center">Procesando pago QR inteligente...</div>`;

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
                            <div class="p-5 rounded-xl bg-gradient-to-br from-emerald-950/50 to-[#040914] border border-emerald-500/40 space-y-3">
                                <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                                    <span class="font-bold text-emerald-400 text-sm">✅ ¡Pago QR Exitoso!</span>
                                    <span class="text-xs bg-emerald-500 text-slate-950 px-2.5 py-0.5 rounded-full font-bold">${data.discount_applied || '0%'} OFF</span>
                                </div>
                                <div class="grid grid-cols-2 gap-2 text-xs">
                                    <div class="bg-[#040914] p-2.5 rounded-lg border border-slate-800">
                                        <span class="text-slate-400 block text-[10px]">Monto Original</span>
                                        <span class="text-white font-mono font-bold">$${data.original_amount}</span>
                                    </div>
                                    <div class="bg-emerald-950/40 p-2.5 rounded-lg border border-emerald-500/30">
                                        <span class="text-emerald-300 block text-[10px]">Ahorro Club</span>
                                        <span class="text-emerald-400 font-mono font-bold">-$${data.amount_saved}</span>
                                    </div>
                                </div>
                                <div class="bg-[#040914] p-3 rounded-xl border border-emerald-500/30 flex justify-between items-center">
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

# --- Rutas de la API (Backend con auto-generación de IDs) ---
@app.post("/users/")
def create_user(email: str, subscription_status: str = "active"):
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
