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
app = FastAPI(title="MaxShop - Club de Descuentos & Pagos", version="6.0.0")

# --- Interfaz Comercial Definitiva ---
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
        
        <!-- Barra de Navegación con Notificación de Geolocalización -->
        <header class="border-b border-slate-800/80 bg-[#040914]/90 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
                
                <div class="flex items-center space-x-3 cursor-pointer" onclick="switchSection('home')">
                    <div class="w-10 h-10 rounded-2xl brand-gradient flex items-center justify-center shadow-lg shadow-emerald-500/20">
                        <svg class="w-5 h-5 text-slate-950" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                    </div>
                    <div>
                        <div class="flex items-center space-x-1.5">
                            <h1 class="font-extrabold text-base text-white">Max<span class="text-emerald-400">Shop</span></h1>
                            <span class="text-[8px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full font-bold uppercase">PRO</span>
                        </div>
                    </div>
                </div>

                <!-- Campanita de Geolocalización e Alertas Cerca Tuyo -->
                <div class="flex items-center space-x-3">
                    <div class="relative">
                        <button onclick="toggleGeoAlert()" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 hover:bg-slate-800 transition relative flex items-center justify-center">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                            </svg>
                            <span id="geoBadge" class="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-ping"></span>
                            <span class="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full"></span>
                        </button>
                        
                        <!-- Ventana Flotante de Geolocalización -->
                        <div id="geoPopup" class="hidden absolute right-0 mt-2 w-72 glass-card rounded-2xl p-4 shadow-2xl border-emerald-500/30 z-50 space-y-2 text-xs">
                            <div class="flex justify-between items-center font-bold text-white border-b border-slate-800 pb-1.5">
                                <span class="flex items-center space-x-1">📍 <span>Radar Cerca Tuyo</span></span>
                                <span class="text-[9px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">GPS Activo</span>
                            </div>
                            <p class="text-slate-300">Detectamos que estás cerca de un comercio adherido:</p>
                            <div class="bg-[#040914] p-2.5 rounded-xl border border-emerald-500/30 space-y-1">
                                <span class="font-bold text-emerald-400">🧥 Zoot & Marken (Indumentaria)</span>
                                <p class="text-[10px] text-slate-400">Tenés un <strong class="text-white">25% OFF</strong> acumulable con tu membresía.</p>
                            </div>
                            <button onclick="switchSection('pay')" class="w-full brand-gradient text-slate-950 font-bold py-2 rounded-xl text-center">Usar Descuento Ahora</button>
                        </div>
                    </div>

                    <nav class="hidden md:flex items-center space-x-1 text-xs">
                        <button onclick="switchSection('home')" id="navHome" class="px-3 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition">Inicio</button>
                        <button onclick="switchSection('catalog')" id="navCatalog" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Comercios</button>
                        <button onclick="switchSection('banks')" id="navBanks" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Promos Bancarias</button>
                        <button onclick="switchSection('register')" id="navRegister" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Registrarse</button>
                        <button onclick="switchSection('pay')" id="navPay" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Caja QR</button>
                    </nav>
                </div>
            </div>
        </header>

        <!-- Contenido Principal -->
        <main class="max-w-6xl mx-auto px-4 py-8 w-full flex-grow space-y-10">
            
            <!-- SECCIÓN INICIO -->
            <section id="secHome" class="space-y-8">
                <!-- Banner Publicitario Principal con Imágenes Reales Integradas -->
                <div class="glass-card rounded-3xl p-6 md:p-10 relative overflow-hidden shadow-2xl border-emerald-500/20 grid md:grid-cols-2 gap-6 items-center">
                    <div class="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
                    <div class="space-y-4 relative z-10">
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">Ahorro Inteligente & Fintech</span>
                        <h2 class="text-2xl md:text-4xl font-extrabold tracking-tight text-white leading-tight">Potenciá tus compras con <span class="brand-text-gradient">MaxShop</span></h2>
                        <p class="text-slate-300 text-xs md:text-sm leading-relaxed">
                            Combiná los descuentos exclusivos de nuestra red con las promociones vigentes de los principales bancos del país de forma automática en caja.
                        </p>
                        <div class="flex flex-wrap gap-3 pt-2">
                            <button onclick="switchSection('register')" class="brand-gradient hover:opacity-90 text-slate-950 font-extrabold px-5 py-3 rounded-xl text-xs transition shadow-lg shadow-emerald-500/20">Asociarme Ahora</button>
                            <button onclick="switchSection('catalog')" class="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-5 py-3 rounded-xl text-xs border border-slate-700 transition">Ver Comercios</button>
                        </div>
                    </div>
                    <div class="relative z-10 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
                        <img src="https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=800&q=80" alt="Shopping Experience" class="w-full h-56 md:h-64 object-cover transform hover:scale-105 transition duration-500">
                    </div>
                </div>

                <!-- Alianzas con Bancos y Tarjetas (Con Logos/Estilos Institucionales) -->
                <div class="space-y-4">
                    <p class="text-[11px] uppercase tracking-wider text-slate-400 font-bold text-center">Entidades Financieras y Tarjetas Aliadas</p>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="glass-card p-4 rounded-xl flex items-center justify-between border-slate-800">
                            <div class="flex items-center space-x-2">
                                <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-extrabold text-white text-xs">G</div>
                                <div>
                                    <span class="text-white font-bold block text-xs">Banco Galicia</span>
                                    <span class="text-[10px] text-emerald-400">Visual + 30%</span>
                                </div>
                            </div>
                            <span class="text-xs bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded font-mono">VISA</span>
                        </div>

                        <div class="glass-card p-4 rounded-xl flex items-center justify-between border-slate-800">
                            <div class="flex items-center space-x-2">
                                <div class="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center font-extrabold text-white text-xs">S</div>
                                <div>
                                    <span class="text-white font-bold block text-xs">Santander</span>
                                    <span class="text-[10px] text-red-400">Modo Shoppings</span>
                                </div>
                            </div>
                            <span class="text-xs bg-red-500/10 text-red-400 px-2 py-0.5 rounded font-mono">MASTER</span>
                        </div>

                        <div class="glass-card p-4 rounded-xl flex items-center justify-between border-slate-800">
                            <div class="flex items-center space-x-2">
                                <div class="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center font-extrabold text-slate-950 text-xs">M</div>
                                <div>
                                    <span class="text-white font-bold block text-xs">Banco Macro</span>
                                    <span class="text-[10px] text-amber-400">Plan Vto Cero</span>
                                </div>
                            </div>
                            <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded font-mono">QR</span>
                        </div>

                        <div class="glass-card p-4 rounded-xl flex items-center justify-between border-slate-800">
                            <div class="flex items-center space-x-2">
                                <div class="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center font-extrabold text-white text-xs">B</div>
                                <div>
                                    <span class="text-white font-bold block text-xs">BBVA Francés</span>
                                    <span class="text-[10px] text-purple-400">Modo Go</span>
                                </div>
                            </div>
                            <span class="text-xs bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded font-mono">VISA</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN CATÁLOGO DE COMERCIOS ADHERIDOS -->
            <section id="secCatalog" class="hidden space-y-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">Comercios Adheridos y Beneficios</h2>
                    <p class="text-xs text-slate-400">Explorá los locales asociados donde podés aplicar descuentos automáticos.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-indigo-500/20">
                        <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=600&q=80" alt="Zoot Store" class="w-full h-32 object-cover">
                        <div class="p-4 space-y-2">
                            <span class="bg-indigo-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full">25% OFF</span>
                            <h3 class="font-bold text-sm text-white">Zoot & Marken Store</h3>
                            <p class="text-xs text-slate-400">Rubro: Indumentaria | ID Comercio: <span class="text-indigo-400 font-bold">1</span></p>
                            <button onclick="selectMerchantForPay(1)" class="w-full mt-2 bg-slate-900 text-emerald-400 text-xs font-semibold py-2 rounded-xl border border-slate-800 hover:bg-slate-800 transition">Usar en Caja ➔</button>
                        </div>
                    </div>

                    <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-cyan-500/20">
                        <img src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80" alt="TecnoHouse" class="w-full h-32 object-cover">
                        <div class="p-4 space-y-2">
                            <span class="bg-cyan-500 text-slate-950 text-[9px] font-bold px-2 py-0.5 rounded-full">15% OFF</span>
                            <h3 class="font-bold text-sm text-white">TecnoHouse Digital</h3>
                            <p class="text-xs text-slate-400">Rubro: Tecnología | ID Comercio: <span class="text-cyan-400 font-bold">2</span></p>
                            <button onclick="selectMerchantForPay(2)" class="w-full mt-2 bg-slate-900 text-emerald-400 text-xs font-semibold py-2 rounded-xl border border-slate-800 hover:bg-slate-800 transition">Usar en Caja ➔</button>
                        </div>
                    </div>

                    <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-emerald-500/20">
                        <img src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80" alt="FarmaSalud" class="w-full h-32 object-cover">
                        <div class="p-4 space-y-2">
                            <span class="bg-emerald-500 text-slate-950 text-[9px] font-bold px-2 py-0.5 rounded-full">20% OFF</span>
                            <h3 class="font-bold text-sm text-white">Red FarmaSalud</h3>
                            <p class="text-xs text-slate-400">Rubro: Farmacia | ID Comercio: <span class="text-emerald-400 font-bold">3</span></p>
                            <button onclick="selectMerchantForPay(3)" class="w-full mt-2 bg-slate-900 text-emerald-400 text-xs font-semibold py-2 rounded-xl border border-slate-800 hover:bg-slate-800 transition">Usar en Caja ➔</button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN PROMOS BANCARIAS -->
            <section id="secBanks" class="hidden space-y-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">Promociones Bancarias Vigentes</h2>
                    <p class="text-xs text-slate-400">Descuentos reales otorgados por entidades financieras combinables con el club.</p>
                </div>
                <div class="grid md:grid-cols-3 gap-6">
                    <div class="glass-card p-6 rounded-2xl space-y-3 border-blue-500/30">
                        <span class="bg-blue-500/10 text-blue-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-blue-500/20">Banco Galicia</span>
                        <h3 class="text-base font-bold text-white">Jueves de Supermercados & Moda</h3>
                        <p class="text-xs text-slate-400">30% de ahorro pagando con tarjetas Visa Débito y Crédito a través de MODO.</p>
                        <div class="text-[10px] text-blue-400 font-semibold pt-1">✨ Acumulable con Club MaxShop</div>
                    </div>
                    <div class="glass-card p-6 rounded-2xl space-y-3 border-red-500/30">
                        <span class="bg-red-500/10 text-red-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-red-500/20">Banco Santander</span>
                        <h3 class="text-base font-bold text-white">Especial Shopping & Style</h3>
                        <p class="text-xs text-slate-400">Hasta 6 cuotas sin interés y 25% OFF en shoppings adheridos seleccionados.</p>
                        <div class="text-[10px] text-red-400 font-semibold pt-1">✨ Válido todos los días</div>
                    </div>
                    <div class="glass-card p-6 rounded-2xl space-y-3 border-amber-500/30">
                        <span class="bg-amber-500/10 text-amber-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-amber-500/20">Banco Macro</span>
                        <h3 class="text-base font-bold text-white">Plan Vto Cero en Combustible y Farmacias</h3>
                        <p class="text-xs text-slate-400">20% de reintegro automático con cartera general usando QR directo.</p>
                        <div class="text-[10px] text-amber-400 font-semibold pt-1">✨ Beneficio exclusivo socios Pro</div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN REGISTRO -->
            <section id="secRegister" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto space-y-6">
                    <div class="text-center space-y-2">
                        <h2 class="text-2xl font-bold text-white">Centro de Altas y Membresías</h2>
                        <p class="text-xs text-slate-400">Unite como socio o registrá tu comercio en la red de beneficios.</p>
                    </div>

                    <div class="grid grid-cols-2 gap-2 bg-[#0b1326] p-1.5 rounded-2xl border border-slate-800 text-xs font-semibold">
                        <button onclick="switchRegSub('user')" id="btnSubUser" class="py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold transition">1. Socio (Cliente)</button>
                        <button onclick="switchRegSub('merchant')" id="btnSubMerchant" class="py-2 rounded-xl text-slate-400 hover:text-white transition">2. Integrar Comercio</button>
                    </div>

                    <!-- Socio -->
                    <div id="formUserBox" class="glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-xs font-bold text-emerald-400 uppercase tracking-wider">Alta Automática de Socio</h3>
                        <form id="userForm" class="space-y-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Correo Electrónico</label>
                                <input type="email" id="userEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-emerald-500">
                            </div>
                            
                            <div id="userPaymentWrapper" class="hidden p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Membresía Mensual Socio:</span>
                                    <span class="text-emerald-400 font-bold">$1,500 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-2.5 rounded-xl text-xs transition shadow-lg">
                                    Pagar Suscripción en Mercado Pago ➔
                                </a>
                            </div>

                            <button type="submit" id="btnUserSubmit" class="w-full brand-gradient text-slate-950 font-extrabold py-3 rounded-xl text-xs transition">Continuar y Activar Membresía</button>
                        </form>
                        <div id="userResult" class="mt-4 hidden"></div>
                    </div>

                    <!-- Comercio (Con costo oculto $5000 publicidad) -->
                    <div id="formMerchantBox" class="hidden glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-xs font-bold text-cyan-400 uppercase tracking-wider">Alta de Comercio y Publicidad</h3>
                        <form id="merchantForm" class="space-y-3">
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Nombre del Comercio</label>
                                    <input type="text" id="mercName" required placeholder="Ej: Zoot Store" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Rubro</label>
                                    <input type="text" id="mercCat" required placeholder="Ej: Indumentaria" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500">
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">% Descuento</label>
                                    <input type="number" step="0.1" id="discPercentage" required placeholder="Ej: 20" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Título Promo</label>
                                    <input type="text" id="discTitle" required placeholder="Ej: 20% Club MaxShop" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-500">
                                </div>
                            </div>

                            <div id="merchantPaymentWrapper" class="hidden p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Costo Publicidad en Red:</span>
                                    <span class="text-cyan-400 font-bold">$5,000 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-2.5 rounded-xl text-xs transition shadow-lg">
                                    Abonar Publicidad en Mercado Pago ➔
                                </a>
                            </div>

                            <button type="submit" id="btnMerchantSubmit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-950 font-extrabold py-3 rounded-xl text-xs transition">Generar Comercio en Red</button>
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
                        <p class="text-xs text-slate-400">Ingresá tu correo y seleccioná el comercio para aplicar el descuento automático.</p>
                    </div>

                    <form id="paymentForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio</label>
                            <input type="email" id="payEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Comercio Adherido</label>
                                <select id="payMerchantSelect" onchange="document.getElementById('payMerchant').value = this.value;" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                                    <option value="1">Zoot & Marken (ID 1)</option>
                                    <option value="2">TecnoHouse (ID 2)</option>
                                    <option value="3">Red FarmaSalud (ID 3)</option>
                                </select>
                                <input type="hidden" id="payMerchant" value="1">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total ($)</label>
                                <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 18000" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                            </div>
                        </div>
                        <button type="submit" class="w-full brand-gradient text-slate-950 font-extrabold py-3.5 rounded-xl text-xs transition shadow-xl">Pagar con Descuento Automático</button>
                    </form>

                    <div id="paymentResult" class="mt-6 hidden"></div>
                </div>
            </section>

        </main>

        <!-- Footer -->
        <footer class="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
            <p>MaxShop Corporation • Pagos seguros operados a través de Mercado Pago</p>
        </footer>

        <!-- Script de Navegación y Geolocalización Interactiva -->
        <script>
            function switchSection(sectionId) {
                const sections = ['home', 'catalog', 'banks', 'register', 'pay'];
                sections.forEach(s => {
                    const el = document.getElementById('sec' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(el) el.classList.add('hidden');
                    const navBtn = document.getElementById('nav' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(navBtn) navBtn.className = "px-3 py-2 rounded-xl text-slate-400 hover:text-white transition";
                });

                const targetSec = document.getElementById('sec' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(targetSec) targetSec.classList.remove('hidden');
                
                const activeNav = document.getElementById('nav' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(activeNav) activeNav.className = "px-3 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition";
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            function toggleGeoAlert() {
                const popup = document.getElementById('geoPopup');
                popup.classList.toggle('hidden');
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
                    bUser.className = "py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold transition";
                    bMerchant.className = "py-2 rounded-xl text-slate-400 hover:text-white transition";
                } else {
                    uBox.classList.add('hidden');
                    mBox.classList.remove('hidden');
                    bMerchant.className = "py-2 rounded-xl bg-cyan-500 text-slate-950 font-bold transition";
                    bUser.className = "py-2 rounded-xl text-slate-400 hover:text-white transition";
                }
            }

            // Formularios backend
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
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-[#040914] text-xs text-slate-400 animate-pulse">Registrando socio...</div>`;

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
                                    <span>Membresía activa lista para usar.</span>
                                    <button onclick="switchSection('pay')" class="underline font-bold">Ir a Pagar ➔</button>
                                </div>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error de conexión.</div>`;
                }
            });

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
                resDiv.innerHTML = `<div class="p-3 rounded-xl bg-[#040914] text-xs text-slate-400 animate-pulse">Generando comercio...</div>`;

                try {
                    const mRes = await fetch(`/merchants/?name=${encodeURIComponent(name)}&category=${encodeURIComponent(cat)}`, { method: 'POST' });
                    const mData = await mRes.json();
                    
                    if(mData.merchant_id) {
                        await fetch(`/discounts/?title=${encodeURIComponent(title)}&percentage=${perc}&merchant_id=${mData.merchant_id}`, { method: 'POST' });
                        resDiv.innerHTML = `
                            <div class="p-4 rounded-xl bg-cyan-950/40 border border-cyan-500/30 space-y-2">
                                <span class="font-bold text-cyan-400 text-xs">🏢 ¡Comercio Integrado!</span>
                                <p class="text-xs text-slate-300">${name} (${cat}) - <strong class="text-cyan-400">${perc}% OFF</strong></p>
                                <div class="pt-2 border-t border-cyan-500/20 text-[11px] text-cyan-300 flex justify-between items-center">
                                    <span>Beneficios publicados en la red.</span>
                                    <button onclick="switchSection('pay')" class="underline font-bold">Probar Caja ➔</button>
                                </div>
                            </div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error al registrar.</div>`;
                }
            });

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
                                    <span class="text-xs bg-emerald-500 text-slate-950 px-2 py-0.5 rounded-full font-bold">${data.discount_applied || '0%'} OFF</span>
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
                    resDiv.innerHTML = `<div class="p-4 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-300">❌ Error de conexión.</div>`;
                }
            });
        </script>
    </body>
    </html>
    """

# --- Rutas de la API (Backend) ---
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
