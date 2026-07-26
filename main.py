import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, Float
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
    image_url = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    status = Column(String, default="active") # active, pending

class DiscountDB(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    percentage = Column(Numeric, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))

Base.metadata.create_all(bind=engine)

# --- Inicializar FastAPI ---
app = FastAPI(title="MaxShop - Red Nacional de Descuentos & Control IA", version="9.0.0")

# --- Interfaz General y Panel de Control ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop Pro | Red Nacional de Descuentos & IA</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #040914; color: #f8fafc; }
            .brand-gradient { background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); }
            .brand-text-gradient { background: linear-gradient(135deg, #34d399 0%, #22d3ee 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .glass-card { background: rgba(11, 19, 38, 0.9); backdrop-filter: blur(16px); border: 1px solid rgba(30, 58, 138, 0.4); }
            @keyframes marquee { 0% { transform: translateX(0%); } 100% { transform: translateX(-50%); } }
            .animate-marquee { display: flex; width: 200%; animation: marquee 35s linear infinite; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
        
        <!-- Barra de Navegación -->
        <header class="border-b border-slate-800/80 bg-[#040914]/95 backdrop-blur-md sticky top-0 z-50">
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
                            <span class="text-[8px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full font-bold uppercase">Nacional IA</span>
                        </div>
                    </div>
                </div>

                <div class="flex items-center space-x-3">
                    <!-- Radar GPS Inteligente -->
                    <div class="relative">
                        <button onclick="checkGeoProximity()" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 hover:bg-slate-800 transition flex items-center justify-center shadow-md" title="Radar IA Cercano">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                            </svg>
                        </button>
                        <div id="geoPopup" class="hidden absolute right-0 mt-2 w-72 glass-card rounded-2xl p-4 shadow-2xl border-emerald-500/30 z-50 space-y-2 text-xs">
                            <div class="flex justify-between items-center font-bold text-white border-b border-slate-800 pb-1.5">
                                <span class="flex items-center space-x-1">📍 <span>Radar IA Nacional</span></span>
                                <span class="text-[9px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">Activo</span>
                            </div>
                            <div id="geoPopupContent" class="text-slate-300">Escaneando comercios en todo el país...</div>
                        </div>
                    </div>

                    <nav class="hidden md:flex items-center space-x-1 text-xs">
                        <button onclick="switchSection('home')" id="navHome" class="px-3 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition">Inicio</button>
                        <button onclick="switchSection('catalog')" id="navCatalog" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Comercios y Ofertas</button>
                        <button onclick="switchSection('live')" id="navLive" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Streaming & TV</button>
                        <button onclick="switchSection('register')" id="navRegister" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Registrarse</button>
                        <button onclick="switchSection('pay')" id="navPay" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Caja QR</button>
                        <button onclick="switchSection('admin')" id="navAdmin" class="px-3 py-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30 font-bold transition">👑 Mi Panel Admin</button>
                    </nav>
                </div>
            </div>
        </header>

        <!-- Contenido Dinámico -->
        <main class="max-w-6xl mx-auto px-4 py-8 w-full flex-grow space-y-12">
            
            <!-- SECCIÓN INICIO -->
            <section id="secHome" class="space-y-10">
                <div class="glass-card rounded-3xl p-6 md:p-10 relative overflow-hidden shadow-2xl border-emerald-500/20 grid md:grid-cols-2 gap-6 items-center">
                    <div class="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
                    <div class="space-y-4 relative z-10">
                        <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">Red Federal de Descuentos & IA</span>
                        <h2 class="text-2xl md:text-4xl font-extrabold tracking-tight text-white leading-tight">El poder de ahorrar en <span class="brand-text-gradient">todo el país</span></h2>
                        <p class="text-slate-300 text-xs md:text-sm leading-relaxed">
                            Integramos comercios locales, grandes marcas y pasarelas de pago con inteligencia artificial para ubicar las mejores ofertas a tu alcance.
                        </p>
                        <div class="flex flex-wrap gap-3 pt-2">
                            <button onclick="switchSection('register')" class="brand-gradient hover:opacity-90 text-slate-950 font-extrabold px-5 py-3 rounded-xl text-xs transition shadow-lg">Unirme Ahora ($5.000)</button>
                            <button onclick="switchSection('catalog')" class="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-5 py-3 rounded-xl text-xs border border-slate-700 transition">Explorar Ofertas</button>
                        </div>
                    </div>
                    <div class="relative z-10 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
                        <img src="https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=800&q=80" alt="MaxShop Nacional" class="w-full h-52 md:h-60 object-cover">
                    </div>
                </div>

                <!-- Carrusel Dinámico -->
                <div class="space-y-3">
                    <div class="flex justify-between items-center px-1">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest">Tendencias y Alianzas Nacionales</h3>
                        <span class="text-[10px] text-emerald-400">Actualización en Vivo</span>
                    </div>
                    <div class="overflow-hidden py-3 bg-slate-950/80 border-y border-slate-800/80 relative rounded-2xl">
                        <div class="animate-marquee flex space-x-6 items-center">
                            <div class="flex items-center space-x-6 shrink-0">
                                <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1511556532299-8f662fc26c06?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1472851294608-062f824d29cc?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                            </div>
                            <div class="flex items-center space-x-6 shrink-0">
                                <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1511556532299-8f662fc26c06?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1472851294608-062f824d29cc?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN CATÁLOGO DE COMERCIOS Y RUBROS -->
            <section id="secCatalog" class="hidden space-y-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 class="text-2xl font-bold text-white">Comercios y Ofertas en el País</h2>
                        <p class="text-xs text-slate-400">Filtrado inteligente por rubro y geolocalización.</p>
                    </div>
                    <!-- Filtros por Rubro -->
                    <div class="flex flex-wrap gap-2 text-xs">
                        <button onclick="filterCategory('all')" class="px-3 py-1.5 rounded-xl bg-emerald-500 text-slate-950 font-bold">Todos</button>
                        <button onclick="filterCategory('Supermercados')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white">Supermercados</button>
                        <button onclick="filterCategory('Farmacias')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white">Farmacias</button>
                        <button onclick="filterCategory('Indumentaria')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white">Indumentaria</button>
                        <button onclick="filterCategory('Tecnología')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white">Tecnología</button>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="realMerchantsContainer">
                    <div class="col-span-3 text-center text-slate-400 text-xs py-8 glass-card rounded-2xl">Cargando red federal...</div>
                </div>
            </section>

            <!-- SECCIÓN EN VIVO / TV -->
            <section id="secLive" class="hidden space-y-6">
                <div class="space-y-2">
                    <h2 class="text-2xl font-bold text-white">MaxShop Live & Streaming</h2>
                    <p class="text-xs text-slate-400">Canales en directo con novedades comerciales, pasarelas y tendencias.</p>
                </div>
                <div class="grid md:grid-cols-3 gap-6">
                    <div class="glass-card p-4 rounded-2xl space-y-3">
                        <div class="aspect-video w-full rounded-xl overflow-hidden bg-slate-900">
                            <iframe class="w-full h-full" src="https://www.youtube.com/embed/jfKfPfyJRdk" title="Live 1" frameborder="0" allowfullscreen></iframe>
                        </div>
                        <h3 class="font-bold text-sm text-white">Tendencias Urbanas Live</h3>
                    </div>
                    <div class="glass-card p-4 rounded-2xl space-y-3">
                        <div class="aspect-video w-full rounded-xl overflow-hidden bg-slate-900">
                            <iframe class="w-full h-full" src="https://www.youtube.com/embed/5qap5aO4i9A" title="Live 2" frameborder="0" allowfullscreen></iframe>
                        </div>
                        <h3 class="font-bold text-sm text-white">Moda & Marcas Directas</h3>
                    </div>
                    <div class="glass-card p-4 rounded-2xl space-y-3">
                        <div class="aspect-video w-full rounded-xl overflow-hidden bg-slate-900">
                            <iframe class="w-full h-full" src="https://www.youtube.com/embed/1la41qXISzs" title="Live 3" frameborder="0" allowfullscreen></iframe>
                        </div>
                        <h3 class="font-bold text-sm text-white">Actualidad y Finanzas</h3>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN REGISTRO CON SUBIDA DE IMAGEN DESDE TELÉFONO -->
            <section id="secRegister" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto space-y-6">
                    <div class="text-center space-y-2">
                        <h2 class="text-2xl font-bold text-white">Centro de Altas & Publicidad</h2>
                        <p class="text-xs text-slate-400">Sumate como socio o registrá tu comercio subiendo tu foto directo desde el celu.</p>
                    </div>

                    <div class="grid grid-cols-2 gap-2 bg-[#0b1326] p-1.5 rounded-2xl border border-slate-800 text-xs font-semibold">
                        <button onclick="switchRegSub('user')" id="btnSubUser" class="py-2.5 rounded-xl bg-emerald-500 text-slate-950 font-bold transition">1. Socio ($5.000)</button>
                        <button onclick="switchRegSub('merchant')" id="btnSubMerchant" class="py-2.5 rounded-xl text-slate-400 hover:text-white transition">2. Comercio Adherido ($5.000)</button>
                    </div>

                    <!-- Socio Form -->
                    <div id="formUserBox" class="glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-xs font-bold text-emerald-400 uppercase tracking-wider">Membresía Mensual Socio</h3>
                        <form id="userForm" class="space-y-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Correo Electrónico</label>
                                <input type="email" id="userEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                            </div>
                            <div id="userPaymentWrapper" class="hidden p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Cuota Membresía Mensual:</span>
                                    <span class="text-emerald-400 font-bold text-sm">$5,000 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-3 rounded-xl text-xs transition shadow-lg">
                                    Pagar Membresía en Mercado Pago ➔
                                </a>
                            </div>
                            <button type="submit" id="btnUserSubmit" class="w-full brand-gradient text-slate-950 font-extrabold py-3 rounded-xl text-xs transition">Continuar y Activar Membresía</button>
                        </form>
                        <div id="userResult" class="mt-4 hidden"></div>
                    </div>

                    <!-- Comercio Form (Con Subida de Imagen desde el Telefono) -->
                    <div id="formMerchantBox" class="hidden glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-xs font-bold text-cyan-400 uppercase tracking-wider">Carga de Comercio & Publicidad Local</h3>
                        <form id="merchantForm" class="space-y-3">
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Nombre del Local</label>
                                    <input type="text" id="mercName" required placeholder="Ej: Farmacia Central" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyan-500">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Rubro Clasificado</label>
                                    <select id="mercCat" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500">
                                        <option value="Supermercados">Supermercados</option>
                                        <option value="Farmacias">Farmacias</option>
                                        <option value="Indumentaria">Indumentaria</option>
                                        <option value="Tecnología">Tecnología</option>
                                        <option value="Gastronomía">Gastronomía</option>
                                    </select>
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">% Descuento Red</label>
                                    <input type="number" step="0.1" id="discPercentage" required placeholder="Ej: 15" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-xs">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Título Promo</label>
                                    <input type="text" id="discTitle" required placeholder="Ej: 15% OFF MaxShop" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-xs">
                                </div>
                            </div>

                            <!-- Selector de Archivo / Imagen desde el Telefono -->
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Subir Imagen / Foto desde tu Teléfono o PC</label>
                                <input type="file" id="mercFile" accept="image/*" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-500 file:text-slate-950 hover:file:bg-cyan-400">
                                <p class="text-[10px] text-slate-500 mt-1">También podés pegar una URL si preferís:</p>
                                <input type="url" id="mercImgUrl" placeholder="https://..." class="w-full mt-1 bg-[#040914] border border-slate-800 rounded-xl px-3 py-1.5 text-xs">
                            </div>

                            <button type="button" onclick="autoDetectGPS()" class="w-full bg-slate-900 border border-slate-700 text-cyan-400 font-semibold py-2 rounded-xl text-xs hover:bg-slate-800 transition">📍 Obtener GPS Actual</button>

                            <div id="merchantPaymentWrapper" class="hidden p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Membresía Mensual Comercio:</span>
                                    <span class="text-cyan-400 font-bold text-sm">$5,000 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-3 rounded-xl text-xs transition shadow-lg">
                                    Abonar Membresía en Mercado Pago ➔
                                </a>
                            </div>

                            <button type="submit" id="btnMerchantSubmit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-950 font-extrabold py-3 rounded-xl text-xs transition">Publicar en la Red</button>
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
                        <h2 class="text-xl font-bold text-white">Simulador de Cobro en Caja</h2>
                        <p class="text-xs text-slate-400">Verificá tu membresía y aplicá el descuento en el acto.</p>
                    </div>
                    <form id="paymentForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio</label>
                            <input type="email" id="payEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-emerald-500">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Comercio Adherido</label>
                                <select id="payMerchantSelect" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white">
                                    <option value="">Cargando comercios...</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total ($)</label>
                                <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 15000" class="w-full bg-[#040914] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm">
                            </div>
                        </div>
                        <button type="submit" class="w-full brand-gradient text-slate-950 font-extrabold py-3.5 rounded-xl text-xs transition shadow-xl">Pagar con Descuento Automático</button>
                    </form>
                    <div id="paymentResult" class="mt-6 hidden"></div>
                </div>
            </section>

            <!-- SECCIÓN MI PANEL DE CONTROL EXCLUSIVO (ADMINISTRADOR) -->
            <section id="secAdmin" class="hidden space-y-6">
                <div class="max-w-4xl mx-auto glass-card rounded-2xl p-6 md:p-8 shadow-2xl border-amber-500/40 space-y-6">
                    <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                        <div>
                            <h2 class="text-xl font-bold text-white flex items-center space-x-2">
                                <span>👑 Panel de Control Privado</span>
                            </h2>
                            <p class="text-xs text-slate-400">Control absoluto de registros, socios y comercios adheridos.</p>
                        </div>
                        <button onclick="loadAdminData()" class="bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 px-3 py-1.5 rounded-xl text-xs font-bold transition">🔄 Actualizar Datos</button>
                    </div>

                    <div class="grid md:grid-cols-2 gap-6">
                        <!-- Control de Socios -->
                        <div class="bg-[#040914] p-4 rounded-xl border border-slate-800 space-y-3">
                            <h3 class="font-bold text-xs text-emerald-400 uppercase tracking-wider">Socios Registrados (Membresías)</h3>
                            <div id="adminUsersList" class="space-y-2 max-h-60 overflow-y-auto text-xs pr-1">
                                <span class="text-slate-500">Cargando socios...</span>
                            </div>
                        </div>

                        <!-- Control de Comercios -->
                        <div class="bg-[#040914] p-4 rounded-xl border border-slate-800 space-y-3">
                            <h3 class="font-bold text-xs text-cyan-400 uppercase tracking-wider">Comercios Adheridos en la Red</h3>
                            <div id="adminMerchantsList" class="space-y-2 max-h-60 overflow-y-auto text-xs pr-1">
                                <span class="text-slate-500">Cargando comercios...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

        </main>

        <!-- Footer -->
        <footer class="border-t border-slate-800/80 py-6 text-center text-[10px] text-slate-500 space-y-2">
            <p>MaxShop Pro Corporation • Pagos seguros operados a través de Mercado Pago</p>
            <p class="text-slate-600">Tarjetas y pasarelas compatibles: BNA+, Modo, Visa, Mastercard, Galicia, Santander, Macro, BBVA.</p>
        </footer>

        <!-- Script General -->
        <script>
            let loadedMerchants = [];
            let currentFilter = 'all';

            async function fetchMerchants() {
                try {
                    const res = await fetch('/api/merchants/');
                    loadedMerchants = await res.json();
                    renderCatalog();
                } catch(e) {
                    console.error("Error al cargar red:", e);
                }
            }

            function renderCatalog() {
                const catalogContainer = document.getElementById('realMerchantsContainer');
                const selectPay = document.getElementById('payMerchantSelect');
                
                const filtered = currentFilter === 'all' 
                    ? loadedMerchants 
                    : loadedMerchants.filter(m => m.category === currentFilter);

                if(filtered.length === 0) {
                    catalogContainer.innerHTML = `<div class="col-span-3 text-center text-slate-400 text-xs py-10 glass-card rounded-2xl">No hay comercios activos en esta categoría. ¡Sumá tu local!</div>`;
                    selectPay.innerHTML = `<option value="">No hay comercios disponibles</option>`;
                    return;
                }

                catalogContainer.innerHTML = '';
                selectPay.innerHTML = '';

                filtered.forEach((m) => {
                    catalogContainer.innerHTML += `
                        <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-emerald-500/20 flex flex-col justify-between">
                            <img src="${m.image_url || 'https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=600&q=80'}" alt="${m.name}" class="w-full h-40 object-cover">
                            <div class="p-4 space-y-2">
                                <div class="flex justify-between items-center">
                                    <span class="bg-emerald-500 text-slate-950 text-[9px] font-bold px-2 py-0.5 rounded-full">${m.percentage}% OFF</span>
                                    <span class="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded-md border border-slate-800">${m.category || 'General'}</span>
                                </div>
                                <h3 class="font-bold text-sm text-white">${m.name}</h3>
                                <p class="text-xs text-slate-400">Promo: <span class="text-emerald-400 font-semibold">${m.title}</span></p>
                                <button onclick="selectMerchantForPay(${m.id})" class="w-full mt-2 bg-slate-900 text-emerald-400 text-xs font-semibold py-2 rounded-xl border border-slate-800 hover:bg-slate-800 transition">Usar en Caja ➔</button>
                            </div>
                        </div>
                    `;
                });

                loadedMerchants.forEach((m) => {
                    selectPay.innerHTML += `<option value="${m.id}">${m.name} (${m.percentage}% OFF)</option>`;
                });
            }

            function filterCategory(cat) {
                currentFilter = cat;
                renderCatalog();
            }

            function checkGeoProximity() {
                const popup = document.getElementById('geoPopup');
                const content = document.getElementById('geoPopupContent');
                popup.classList.toggle('hidden');

                if(!navigator.geolocation) {
                    content.innerHTML = "Geolocalización no disponible.";
                    return;
                }

                content.innerHTML = "Analizando ubicación con IA...";

                navigator.geolocation.getCurrentPosition(async (position) => {
                    const userLat = position.coords.latitude;
                    const userLng = position.coords.longitude;

                    try {
                        const res = await fetch(`/api/merchants/nearby?lat=${userLat}&lng=${userLng}`);
                        const nearby = await res.json();

                        if(nearby.length > 0) {
                            content.innerHTML = `
                                <div class="space-y-2">
                                    <p class="text-emerald-400 font-bold">¡Cerca de ${nearby[0].name}!</p>
                                    <p class="text-[10px] text-slate-300">Descuento: <strong class="text-white">${nearby[0].percentage}% OFF</strong></p>
                                    <button onclick="selectMerchantForPay(${nearby[0].id})" class="w-full brand-gradient text-slate-950 font-bold py-1.5 rounded-lg text-center mt-1">Usar en Caja</button>
                                </div>
                            `;
                        } else {
                            content.innerHTML = "No hay comercios muy cerca, pero podés ver todas las promos nacionales.";
                        }
                    } catch(err) {
                        content.innerHTML = "Sin comercios activos en esta zona.";
                    }
                }, () => {
                    content.innerHTML = "Habilitá los permisos de ubicación para usar el radar.";
                });
            }

            function autoDetectGPS() {
                if(navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition((pos) => {
                        window.tempLat = pos.coords.latitude;
                        window.tempLng = pos.coords.longitude;
                        alert("¡GPS capturado con éxito!");
                    });
                }
            }

            function switchSection(sectionId) {
                ['home', 'catalog', 'live', 'register', 'pay', 'admin'].forEach(s => {
                    const el = document.getElementById('sec' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(el) el.classList.add('hidden');
                    const navBtn = document.getElementById('nav' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(navBtn && s !== 'admin') navBtn.className = "px-3 py-2 rounded-xl text-slate-400 hover:text-white transition";
                });

                const targetSec = document.getElementById('sec' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(targetSec) targetSec.classList.remove('hidden');
                
                const activeNav = document.getElementById('nav' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(activeNav && sectionId !== 'admin') {
                    activeNav.className = "px-3 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition";
                }
                
                if(sectionId === 'catalog') fetchMerchants();
                if(sectionId === 'admin') loadAdminData();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            function selectMerchantForPay(id) {
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

            // Manejo de Registro Socio
            document.getElementById('userForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('userEmail').value;
                const wrapper = document.getElementById('userPaymentWrapper');
                const btn = document.getElementById('btnUserSubmit');
                const resDiv = document.getElementById('userResult');

                if(wrapper.classList.contains('hidden')) {
                    wrapper.classList.remove('hidden');
                    btn.textContent = "Confirmar Alta Socio";
                    return;
                }

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 bg-[#040914] text-xs text-slate-400 animate-pulse">Registrando...</div>`;

                try {
                    const response = await fetch(`/users/?email=${encodeURIComponent(email)}&subscription_status=active`, { method: 'POST' });
                    const data = await response.json();
                    if(data.error) {
                        resDiv.innerHTML = `<div class="p-3 bg-red-950/40 border border-red-800 text-xs text-red-300">⚠️ ${data.error}</div>`;
                    } else {
                        resDiv.innerHTML = `<div class="p-3 bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300">✨ ¡Socio registrado con éxito! Membresía activa.</div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 bg-red-950/40 text-xs text-red-300">❌ Error de conexión.</div>`;
                }
            });

            // Manejo de Registro Comercio (Con soporte de archivo de imagen local o URL)
            document.getElementById('merchantForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('mercName').value;
                const cat = document.getElementById('mercCat').value;
                const perc = document.getElementById('discPercentage').value;
                const title = document.getElementById('discTitle').value;
                
                let imgUrl = document.getElementById('mercImgUrl').value;
                const fileInput = document.getElementById('mercFile');

                if(fileInput.files && fileInput.files[0]) {
                    // Convertimos la imagen local subida desde el teléfono a Base64 para guardarla directamente
                    const reader = new FileReader();
                    reader.onload = async function(uploadEvent) {
                        const base64Image = uploadEvent.target.result;
                        await sendMerchantToServer(name, cat, base64Image, perc, title);
                    };
                    reader.readAsDataURL(fileInput.files[0]);
                } else {
                    await sendMerchantToServer(name, cat, imgUrl || 'https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=600&q=80', perc, title);
                }
            });

            async function sendMerchantToServer(name, cat, imgUrl, perc, title) {
                const wrapper = document.getElementById('merchantPaymentWrapper');
                const btn = document.getElementById('btnMerchantSubmit');
                const resDiv = document.getElementById('merchantResult');

                if(wrapper.classList.contains('hidden')) {
                    wrapper.classList.remove('hidden');
                    btn.textContent = "Finalizar y Publicar";
                    return;
                }

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 bg-[#040914] text-xs text-slate-400 animate-pulse">Publicando comercio...</div>`;

                const lat = window.tempLat || -34.6037;
                const lng = window.tempLng || -58.3816;

                try {
                    const res = await fetch(`/api/merchants/create?name=${encodeURIComponent(name)}&category=${encodeURIComponent(cat)}&image_url=${encodeURIComponent(imgUrl)}&lat=${lat}&lng=${lng}&title=${encodeURIComponent(title)}&percentage=${perc}`, { method: 'POST' });
                    const data = await res.json();
                    if(data.merchant_id) {
                        resDiv.innerHTML = `<div class="p-3 bg-cyan-950/40 border border-cyan-500/30 text-xs text-cyan-300">🏢 ¡Comercio y publicidad publicados en la red nacional con éxito!</div>`;
                        fetchMerchants();
                    }
                } catch(err) {
                    resDiv.innerHTML = `<div class="p-3 bg-red-950/40 text-xs text-red-300">❌ Error al publicar.</div>`;
                }
            }

            // Pago QR
            document.getElementById('paymentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('payEmail').value;
                const merchantId = document.getElementById('payMerchantSelect').value;
                const amount = document.getElementById('payAmount').value;
                const resDiv = document.getElementById('paymentResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 bg-[#040914] text-xs text-slate-400 animate-pulse text-center">Procesando pago QR...</div>`;

                try {
                    const response = await fetch(`/process-payment/?user_email=${encodeURIComponent(email)}&merchant_id=${merchantId}&total_amount=${amount}`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.error) {
                        resDiv.innerHTML = `<div class="p-3 bg-amber-950/40 border border-amber-500/40 text-xs text-amber-200">⚠️ ${data.error}</div>`;
                    } else {
                        resDiv.innerHTML = `
                            <div class="p-4 bg-emerald-950/40 border border-emerald-500/40 space-y-2 text-xs">
                                <span class="font-bold text-emerald-400 text-sm">✅ ¡Pago QR Exitoso! (${data.discount_applied} OFF)</span>
                                <div class="flex justify-between text-slate-300 pt-1 border-t border-slate-800">
                                    <span>Original: $${data.original_amount}</span>
                                    <span class="text-emerald-400 font-bold">Ahorro: -$${data.amount_saved}</span>
                                </div>
                                <div class="text-sm font-extrabold text-white pt-1">Total Cobrado: $${data.final_amount_to_pay}</div>
                            </div>`;
                    }
                } catch(e) {
                    resDiv.innerHTML = `<div class="p-3 bg-red-950/40 text-xs text-red-300">❌ Error en caja.</div>`;
                }
            });

            // Cargar datos en el Panel Admin Exclusivo
            async function loadAdminData() {
                const uList = document.getElementById('adminUsersList');
                const mList = document.getElementById('adminMerchantsList');
                uList.innerHTML = "Cargando...";
                mList.innerHTML = "Cargando...";

                try {
                    const uRes = await fetch('/api/admin/users');
                    const users = await uRes.json();
                    uList.innerHTML = users.length === 0 ? '<span class="text-slate-500">Sin socios registrados.</span>' : '';
                    users.forEach(u => {
                        uList.innerHTML += `<div class="bg-slate-900 p-2 rounded-lg border border-slate-800 flex justify-between items-center"><span>${u.email}</span><span class="text-emerald-400 font-bold">${u.subscription_status}</span></div>`;
                    });

                    const mRes = await fetch('/api/merchants/');
                    const merchants = await mRes.json();
                    mList.innerHTML = merchants.length === 0 ? '<span class="text-slate-500">Sin comercios cargados.</span>' : '';
                    merchants.forEach(m => {
                        mList.innerHTML += `<div class="bg-slate-900 p-2 rounded-lg border border-slate-800 flex justify-between items-center"><span>${m.name} (${m.category})</span><span class="text-cyan-400 font-bold">${m.percentage}% OFF</span></div>`;
                    });
                } catch(e) {
                    uList.innerHTML = '<span class="text-red-400">Error al cargar datos.</span>';
                }
            }

            fetchMerchants();
        </script>
    </body>
    </html>
    """

# --- Endpoints API ---
@app.get("/api/merchants/")
def get_merchants():
    db = SessionLocal()
    try:
        merchants = db.query(MerchantDB).all()
        result = []
        for m in merchants:
            disc = db.query(DiscountDB).filter(DiscountDB.merchant_id == m.id).first()
            result.append({
                "id": m.id,
                "name": m.name,
                "category": m.category,
                "image_url": m.image_url,
                "lat": m.lat,
                "lng": m.lng,
                "percentage": float(disc.percentage) if disc else 0.0,
                "title": disc.title if disc else ""
            })
        return result
    finally:
        db.close()

@app.get("/api/admin/users")
def get_admin_users():
    db = SessionLocal()
    try:
        users = db.query(UserDB).all()
        return [{"id": u.id, "email": u.email, "subscription_status": u.subscription_status} for u in users]
    finally:
        db.close()

@app.get("/api/merchants/nearby")
def get_nearby_merchants(lat: float, lng: float):
    db = SessionLocal()
    try:
        merchants = db.query(MerchantDB).all()
        nearby = []
        for m in merchants:
            if m.lat and m.lng:
                diff = abs(m.lat - lat) + abs(m.lng - lng)
                if diff < 2.0:
                    disc = db.query(DiscountDB).filter(DiscountDB.merchant_id == m.id).first()
                    nearby.append({
                        "id": m.id,
                        "name": m.name,
                        "percentage": float(disc.percentage) if disc else 0.0
                    })
        return nearby
    finally:
        db.close()

@app.post("/api/merchants/create")
def create_full_merchant(name: str, category: str, image_url: str, lat: float, lng: float, title: str, percentage: float):
    db = SessionLocal()
    try:
        new_m = MerchantDB(name=name, category=category, image_url=image_url, lat=lat, lng=lng)
        db.add(new_m)
        db.commit()
        db.refresh(new_m)

        new_d = DiscountDB(title=title, percentage=percentage, merchant_id=new_m.id)
        db.add(new_d)
        db.commit()

        return {"message": "Comercio adherido con éxito", "merchant_id": new_m.id}
    finally:
        db.close()

@app.post("/users/")
def create_user(email: str, subscription_status: str = "active"):
    db = SessionLocal()
    try:
        existing_user = db.query(UserDB).filter(UserDB.email == email).first()
        if existing_user:
            return {"error": "El correo ya está registrado"}
        new_user = UserDB(email=email, subscription_status=subscription_status)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Usuario registrado", "user_id": new_user.id, "email": new_user.email}
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
            "message": "¡Pago procesado con éxito!",
            "original_amount": total_amount,
            "discount_applied": f"{discount_percentage}%",
            "amount_saved": round(amount_saved, 2),
            "final_amount_to_pay": round(final_amount, 2)
        }
    finally:
        db.close()
