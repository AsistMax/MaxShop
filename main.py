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
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

class DiscountDB(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    percentage = Column(Numeric, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))

Base.metadata.create_all(bind=engine)

# --- Inicializar FastAPI ---
app = FastAPI(title="MaxShop Pro - Versión Desplazamiento Total", version="11.1.0")

# --- Interfaz Principal ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop Pro | ¡Descuentos de Locos!! & Seguros AsistMax</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #030712; color: #f8fafc; overflow-x: hidden; -webkit-overflow-scrolling: touch; }
            .brand-gradient { background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); }
            .locos-gradient { background: linear-gradient(135deg, #f59e0b 0%, #ef4444 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .glass-card { background: rgba(11, 19, 38, 0.95); backdrop-filter: blur(16px); border: 1px solid rgba(30, 58, 138, 0.4); }
            @keyframes marquee { 0% { transform: translateX(0%); } 100% { transform: translateX(-50%); } }
            .animate-marquee { display: flex; width: 200%; animation: marquee 35s linear infinite; }
            /* Deslizamiento lateral suave para celulares */
            .swipe-container { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth; -webkit-overflow-scrolling: touch; }
            .swipe-container::-webkit-scrollbar { display: none; }
            .swipe-item { flex: 0 0 100%; scroll-snap-align: start; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
        
        <!-- Barra Financiera Superior en Vivo -->
        <div class="bg-slate-950 border-b border-slate-800/80 py-1.5 px-4 text-[11px] text-slate-400">
            <div class="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-2">
                <div class="flex items-center space-x-4">
                    <span class="flex items-center space-x-1 text-emerald-400 font-bold">🟢 <span>Dólar Blue:</span> <strong class="text-white">$1.220 / $1.240</strong></span>
                    <span class="hidden md:inline text-slate-600">|</span>
                    <span class="hidden md:inline text-slate-300">Inflación: <strong class="text-emerald-400">2.8%</strong></span>
                </div>
                <div class="flex items-center space-x-3 text-amber-400 font-bold">
                    <span>⚡ AsistMax Seguro Financiero: Póliza hasta $20M Activa</span>
                </div>
            </div>
        </div>

        <!-- Navegación y Control Superior con Flechas Antirretorno -->
        <header class="border-b border-slate-800/80 bg-[#030712]/95 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
                
                <div class="flex items-center space-x-3">
                    <!-- Botones de flecha para evitar que el botón del celular cierre la app -->
                    <div class="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded-xl p-1 shadow-md">
                        <button onclick="goBackSection()" class="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition" title="Sección Anterior">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                        </button>
                        <button onclick="goForwardSection()" class="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition" title="Sección Siguiente">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        </button>
                    </div>

                    <div class="flex items-center space-x-2 cursor-pointer" onclick="switchSection('home')">
                        <div class="w-9 h-9 rounded-2xl brand-gradient flex items-center justify-center shadow-lg shadow-emerald-500/20">
                            <svg class="w-4 h-4 text-slate-950" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        </div>
                        <h1 class="font-extrabold text-sm text-white hidden sm:block">Max<span class="text-emerald-400">Shop</span></h1>
                    </div>
                </div>

                <!-- Menú y Acceso -->
                <div class="flex items-center space-x-2">
                    <nav class="hidden md:flex items-center space-x-1 text-xs">
                        <button onclick="switchSection('home')" id="navHome" class="px-3 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition">Inicio</button>
                        <button onclick="switchSection('catalog')" id="navCatalog" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">¡Descuentos de Locos!!</button>
                        <button onclick="switchSection('insurance')" id="navInsurance" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Seguros AsistMax</button>
                        <button onclick="switchSection('news')" id="navNews" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Noticias & Finanzas</button>
                        <button onclick="switchSection('register')" id="navRegister" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Registrarse</button>
                        <button onclick="switchSection('pay')" id="navPay" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Caja QR</button>
                    </nav>

                    <button onclick="openLoginModal()" class="bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 px-3 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-1">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4v-4l5.257-5.257A6 6 0 1117 9z"/></svg>
                        <span>Ingresar</span>
                    </button>
                </div>
            </div>
        </header>

        <!-- Contenedor Principal Deslizable Vertical y Horizontal -->
        <main class="max-w-6xl mx-auto px-4 py-8 w-full flex-grow space-y-16">
            
            <!-- SECCIÓN INICIO (Deslizable a los lados) -->
            <section id="secHome" class="space-y-10">
                <div class="swipe-container rounded-3xl overflow-hidden glass-card shadow-2xl border-emerald-500/20">
                    <!-- Slide 1 -->
                    <div class="swipe-item p-6 md:p-10 grid md:grid-cols-2 gap-6 items-center">
                        <div class="space-y-4">
                            <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-3 py-1 rounded-full uppercase">Red Federal MaxShop</span>
                            <h2 class="text-2xl md:text-4xl font-extrabold tracking-tight text-white leading-tight">Desplázate y descubre <span class="locos-gradient font-black">¡Descuentos de Locos!!</span></h2>
                            <p class="text-slate-300 text-xs md:text-sm leading-relaxed">
                                Navega verticalmente o desliza hacia los costados para explorar comercios, tecnología, indumentaria, hogar, moda y mucho más.
                            </p>
                            <div class="flex flex-wrap gap-3 pt-2">
                                <button onclick="switchSection('catalog')" class="brand-gradient hover:opacity-90 text-slate-950 font-extrabold px-5 py-3 rounded-xl text-xs transition shadow-lg">Ver Descuentos de Locos</button>
                                <button onclick="switchSection('insurance')" class="bg-amber-500/10 border border-amber-500/30 text-amber-400 font-semibold px-5 py-3 rounded-xl text-xs transition">Seguros AsistMax ($20M)</button>
                            </div>
                        </div>
                        <div class="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
                            <img src="https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=800&q=80" alt="MaxShop" class="w-full h-52 md:h-64 object-cover">
                        </div>
                    </div>
                    <!-- Slide 2 -->
                    <div class="swipe-item p-6 md:p-10 grid md:grid-cols-2 gap-6 items-center bg-slate-950/60">
                        <div class="space-y-4">
                            <span class="bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-bold px-3 py-1 rounded-full uppercase">Alianza Estratégica AsistMax</span>
                            <h2 class="text-2xl md:text-4xl font-extrabold text-white">Asistencia Financiera y de Sepelio</h2>
                            <p class="text-slate-300 text-xs md:text-sm leading-relaxed">
                                Obtén cobertura de hasta $20.000.000 en tu póliza con solo activar tu membresía en la red. Protección integral para ti y tu familia.
                            </p>
                            <a href="https://sistema-seguros.onrender.com/" target="_blank" class="inline-block bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold px-6 py-3 rounded-xl text-xs transition">Contratar en AsistMax ➔</a>
                        </div>
                        <div class="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
                            <img src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80" alt="Seguros" class="w-full h-52 md:h-64 object-cover">
                        </div>
                    </div>
                </div>

                <!-- Carrusel de Marcas, Canales, Compras y Tecnología -->
                <div class="space-y-3">
                    <div class="flex justify-between items-center px-1">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest">Tecnología, Moda, Hogar & Canales Aliados</h3>
                        <span class="text-[10px] text-emerald-400">Deslizamiento Continuo</span>
                    </div>
                    <div class="overflow-hidden py-3 bg-slate-950/80 border-y border-slate-800/80 relative rounded-2xl">
                        <div class="animate-marquee flex space-x-6 items-center">
                            <div class="flex items-center space-x-6 shrink-0">
                                <img src="https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                            </div>
                            <div class="flex items-center space-x-6 shrink-0">
                                <img src="https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                                <img src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80" class="w-64 h-32 object-cover rounded-2xl border border-slate-800 shadow-xl">
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN: ¡DESCUENTOS DE LOCOS!! (Comercios y Ofertas) -->
            <section id="secCatalog" class="hidden space-y-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 class="text-3xl font-black locos-gradient tracking-wide">¡Descuentos de Locos!!</h2>
                        <p class="text-xs text-slate-400">Supermercados, tecnología, indumentaria, farmacias, hogar y gastronomía.</p>
                    </div>
                    <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
                        <button onclick="changePage(-1)" class="text-slate-400 hover:text-white font-bold px-2 py-0.5 bg-slate-800 rounded-lg">◀ Regresar</button>
                        <span id="pageIndicator" class="text-emerald-400 font-bold px-2">Página 1</span>
                        <button onclick="changePage(1)" class="text-slate-400 hover:text-white font-bold px-2 py-0.5 bg-slate-800 rounded-lg">Avanzar ▶</button>
                    </div>
                </div>

                <!-- Filtros Rubro -->
                <div class="flex flex-wrap gap-2 text-xs">
                    <button onclick="filterCategory('all')" class="px-3 py-1.5 rounded-xl bg-emerald-500 text-slate-950 font-bold">Todos</button>
                    <button onclick="filterCategory('Supermercados')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">Supermercados</button>
                    <button onclick="filterCategory('Tecnología')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">Tecnología</button>
                    <button onclick="filterCategory('Moda e Indumentaria')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">Moda e Indumentaria</button>
                    <button onclick="filterCategory('Hogar')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">Hogar</button>
                    <button onclick="filterCategory('Farmacias')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">Farmacias</button>
                    <button onclick="filterCategory('Gastronomía')" class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">Gastronomía</button>
                </div>

                <!-- Grid de Comercios -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="realMerchantsContainer">
                    <div class="col-span-3 text-center text-slate-400 text-xs py-10 glass-card rounded-2xl">Cargando descuentos...</div>
                </div>
            </section>

            <!-- SECCIÓN: SEGUROS ASISTMAX -->
            <section id="secInsurance" class="hidden space-y-6">
                <div class="max-w-3xl mx-auto glass-card rounded-3xl p-8 shadow-2xl border-amber-500/30 space-y-6">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 rounded-2xl bg-amber-500/20 flex items-center justify-center text-amber-400 font-black text-xl">🛡️</div>
                        <div>
                            <h2 class="text-2xl font-bold text-white">AsistMax Seguro Financiero</h2>
                            <p class="text-xs text-slate-400">Asistencia integral en vida y sepelio de hasta $20.000.000 de póliza.</p>
                        </div>
                    </div>
                    <p class="text-xs text-slate-300 leading-relaxed">
                        Como socio activo de MaxShop Pro, tienes acceso preferencial a los planes de protección financiera más avanzados del mercado provistos por nuestro socio estratégico **AsistMax**.
                    </p>
                    <div class="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/30 flex flex-col sm:flex-row justify-between items-center gap-4">
                        <span class="text-xs text-amber-300 font-semibold">¿Deseas cotizar o contratar otra cobertura adicional?</span>
                        <a href="https://sistema-seguros.onrender.com/" target="_blank" class="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold px-6 py-3 rounded-xl text-xs transition shadow-lg shrink-0">
                            Abrir Sistema de Seguros ➔
                        </a>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN: NOTICIAS EN VIVO Y FINANZAS -->
            <section id="secNews" class="hidden space-y-6">
                <div class="space-y-2">
                    <h2 class="text-2xl font-bold text-white">Noticias de Impacto Mundial & Finanzas</h2>
                    <p class="text-xs text-slate-400">Actualización automática diaria sobre economía, tecnología, mercado y consumo.</p>
                </div>

                <div class="grid md:grid-cols-3 gap-6">
                    <div class="glass-card p-5 rounded-2xl space-y-3">
                        <span class="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-md font-bold">MERCADOS & INFLACIÓN</span>
                        <h3 class="font-bold text-sm text-white">Impacto de la inflación en las compras de tecnología y hogar</h3>
                        <p class="text-xs text-slate-400 leading-relaxed">Cómo capitalizar las cuotas sin interés y los descuentos masivos para mantener el poder adquisitivo familiar.</p>
                    </div>
                    <div class="glass-card p-5 rounded-2xl space-y-3">
                        <span class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded-md font-bold">TENDENCIAS MUNDIALES</span>
                        <h3 class="font-bold text-sm text-white">La revolución del e-commerce y los clubes de beneficios</h3>
                        <p class="text-xs text-slate-400 leading-relaxed">Nuevas estrategias de marketing digital implementadas por plataformas líderes en el mundo este año.</p>
                    </div>
                    <div class="glass-card p-5 rounded-2xl space-y-3">
                        <span class="text-[10px] bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded-md font-bold">FINANZAS PERSONALES</span>
                        <h3 class="font-bold text-sm text-white">Seguros de vida y cobertura patrimonial: ¿Por qué son vitales?</h3>
                        <p class="text-xs text-slate-400 leading-relaxed">Análisis de pólizas de hasta $20M con AsistMax y su rendimiento frente a contextos inflacionarios.</p>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN REGISTRO -->
            <section id="secRegister" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto space-y-6">
                    <div class="text-center space-y-2">
                        <h2 class="text-2xl font-bold text-white">Centro de Altas & Membresías</h2>
                        <p class="text-xs text-slate-400">Únete como socio y obtén beneficios en toda la red y seguros.</p>
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
                                <input type="email" id="userEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2.5 text-sm text-white">
                            </div>
                            <div id="userPaymentWrapper" class="hidden p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Cuota Membresía Mensual:</span>
                                    <span class="text-emerald-400 font-bold text-sm">$5,000 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-3 rounded-xl text-xs transition shadow-lg">
                                    Pagar en Mercado Pago ➔
                                </a>
                            </div>
                            <button type="submit" id="btnUserSubmit" class="w-full brand-gradient text-slate-950 font-extrabold py-3 rounded-xl text-xs transition">Continuar y Activar Membresía</button>
                        </form>
                        <div id="userResult" class="mt-4 hidden"></div>
                    </div>

                    <!-- Comercio Form -->
                    <div id="formMerchantBox" class="hidden glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <h3 class="text-xs font-bold text-cyan-400 uppercase tracking-wider">Carga de Comercio & Publicidad</h3>
                        <form id="merchantForm" class="space-y-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Tu Correo (Login de Comerciante)</label>
                                <input type="email" id="mercEmail" required placeholder="correo_comercio@email.com" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white">
                                <p class="text-[10px] text-slate-500 mt-1">Si ya te registraste antes, el sistema actualizará tu publicidad sin cobrarte nuevamente.</p>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Nombre del Local</label>
                                    <input type="text" id="mercName" required placeholder="Ej: TechStore" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Rubro / Sección</label>
                                    <select id="mercCat" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white">
                                        <option value="Supermercados">Supermercados</option>
                                        <option value="Tecnología">Tecnología</option>
                                        <option value="Moda e Indumentaria">Moda e Indumentaria</option>
                                        <option value="Hogar">Hogar</option>
                                        <option value="Farmacias">Farmacias</option>
                                        <option value="Gastronomía">Gastronomía</option>
                                    </select>
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">% Descuento</label>
                                    <input type="number" step="0.1" id="discPercentage" required placeholder="Ej: 25" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Título de Promo / Flyer</label>
                                    <input type="text" id="discTitle" required placeholder="Ej: 25% OFF Liquidación" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white">
                                </div>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Imagen o Flyer (Archivo o Enlace URL)</label>
                                <input type="file" id="mercFile" accept="image/*" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-500 file:text-slate-950">
                                <input type="url" id="mercImgUrl" placeholder="O pega URL de imagen..." class="w-full mt-2 bg-[#030712] border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white">
                            </div>

                            <div id="merchantPaymentWrapper" class="hidden p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Membresía Mensual Comercio:</span>
                                    <span class="text-cyan-400 font-bold text-sm">$5,000 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block w-full text-center bg-[#009ee3] hover:opacity-90 text-white font-bold py-3 rounded-xl text-xs transition shadow-lg">
                                    Abonar en Mercado Pago ➔
                                </a>
                            </div>

                            <button type="submit" id="btnMerchantSubmit" class="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-950 font-extrabold py-3 rounded-xl text-xs transition">Publicar / Actualizar Publicidad</button>
                        </form>
                        <div id="merchantResult" class="mt-4 hidden"></div>
                    </div>
                </div>
            </section>

            <!-- SECCIÓN CAJA Y PAGO QR -->
            <section id="secPay" class="hidden space-y-6">
                <div class="max-w-xl mx-auto glass-card rounded-2xl p-8 shadow-2xl border-emerald-500/30 relative">
                    <div class="absolute -top-3 right-6 bg-emerald-500 text-slate-950 text-[10px] font-extrabold px-3 py-1 rounded-full uppercase">Caja Inteligente QR</div>
                    <div class="space-y-2 mb-6">
                        <h2 class="text-xl font-bold text-white">Simulador de Cobro en Caja</h2>
                        <p class="text-xs text-slate-400">Verifica socio y aplica el descuento instantáneo.</p>
                    </div>
                    <form id="paymentForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio</label>
                            <input type="email" id="payEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Comercio Adherido</label>
                                <select id="payMerchantSelect" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white">
                                    <option value="">Cargando...</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total ($)</label>
                                <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 15000" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white">
                            </div>
                        </div>
                        <button type="submit" class="w-full brand-gradient text-slate-950 font-extrabold py-3.5 rounded-xl text-xs transition shadow-xl">Pagar con Descuento de Locos</button>
                    </form>
                    <div id="paymentResult" class="mt-6 hidden"></div>
                </div>
            </section>

            <!-- SECCIÓN PANEL ADMINISTRADOR EXCLUSIVO -->
            <section id="secAdmin" class="hidden space-y-6">
                <div class="max-w-4xl mx-auto glass-card rounded-2xl p-6 md:p-8 shadow-2xl border-amber-500/40 space-y-6">
                    <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                        <div>
                            <h2 class="text-xl font-bold text-white">👑 Panel de Control Privado (Propietario)</h2>
                            <p class="text-xs text-slate-400">Control absoluto de funciones, secciones y comercios de la empresa.</p>
                        </div>
                        <button onclick="loadAdminData()" class="bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 px-3 py-1.5 rounded-xl text-xs font-bold transition">🔄 Actualizar</button>
                    </div>

                    <div class="grid md:grid-cols-2 gap-6">
                        <div class="bg-[#030712] p-4 rounded-xl border border-slate-800 space-y-3">
                            <h3 class="font-bold text-xs text-emerald-400 uppercase">Socios Registrados</h3>
                            <div id="adminUsersList" class="space-y-2 max-h-60 overflow-y-auto text-xs pr-1"><span class="text-slate-500">Cargando...</span></div>
                        </div>
                        <div class="bg-[#030712] p-4 rounded-xl border border-slate-800 space-y-3">
                            <h3 class="font-bold text-xs text-cyan-400 uppercase">Comercios en la Red</h3>
                            <div id="adminMerchantsList" class="space-y-2 max-h-60 overflow-y-auto text-xs pr-1"><span class="text-slate-500">Cargando...</span></div>
                        </div>
                    </div>
                </div>
            </section>

        </main>

        <!-- Modal de Login -->
        <div id="loginModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
            <div class="glass-card rounded-3xl p-6 max-w-sm w-full space-y-4 border-cyan-500/40 shadow-2xl relative">
                <button onclick="closeLoginModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white font-bold">✕</button>
                <h3 class="font-bold text-base text-white">Acceso Exclusivo / Login</h3>
                <p class="text-xs text-slate-400">Ingresa tu clave de propietario o correo de comerciante registrado.</p>
                <div class="space-y-3">
                    <input type="password" id="loginKeyInput" placeholder="Clave de Administrador o Email..." class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-white">
                    <button onclick="executeLogin()" class="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold py-2.5 rounded-xl text-xs transition">Acceder al Sistema</button>
                </div>
                <div id="loginError" class="text-xs text-red-400 hidden">Clave incorrecta.</div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="border-t border-slate-800/80 py-6 text-center text-[10px] text-slate-500 space-y-2">
            <p>MaxShop Pro & AsistMax Seguros • Pagos seguros operados a través de Mercado Pago</p>
            <p class="text-slate-600">Bancos y Tarjetas compatibles: BNA+, Modo, Visa, Mastercard, Galicia, Santander, Macro.</p>
        </footer>

        <!-- Script -->
        <script>
            let loadedMerchants = [];
            let currentFilter = 'all';
            let currentPage = 1;
            const itemsPerPage = 6;
            const sectionHistory = ['home', 'catalog', 'insurance', 'news', 'register', 'pay'];
            let currentSectionIndex = 0;

            async function fetchMerchants() {
                try {
                    const res = await fetch('/api/merchants/');
                    loadedMerchants = await res.json();
                    if(loadedMerchants.length === 0) {
                        // Precargar un comercio por defecto si la base está vacía para evitar pantallas en blanco
                        loadedMerchants = [
                            { id: 1, email: "demo@techstore.com", name: "TechStore Argentina", category: "Tecnología", image_url: "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80", percentage: 20, title: "20% OFF en Celulares" },
                            { id: 2, email: "demo@supermax.com", name: "Supermercados Max", category: "Supermercados", image_url: "https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=600&q=80", percentage: 15, title: "15% OFF en Canasta Básica" }
                        ];
                    }
                    renderCatalog();
                } catch(e) {
                    console.error("Error cargando comercios:", e);
                }
            }

            function renderCatalog() {
                const catalogContainer = document.getElementById('realMerchantsContainer');
                const selectPay = document.getElementById('payMerchantSelect');
                
                const filtered = currentFilter === 'all' 
                    ? loadedMerchants 
                    : loadedMerchants.filter(m => m.category === currentFilter);

                const totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;
                if(currentPage > totalPages) currentPage = totalPages;
                document.getElementById('pageIndicator').innerText = `Página ${currentPage} de ${totalPages}`;

                const start = (currentPage - 1) * itemsPerPage;
                const paginatedItems = filtered.slice(start, start + itemsPerPage);

                catalogContainer.innerHTML = '';
                selectPay.innerHTML = '';

                paginatedItems.forEach((m) => {
                    catalogContainer.innerHTML += `
                        <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-emerald-500/20 flex flex-col justify-between">
                            <img src="${m.image_url || 'https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=600&q=80'}" alt="${m.name}" class="w-full h-40 object-cover">
                            <div class="p-4 space-y-2">
                                <div class="flex justify-between items-center">
                                    <span class="bg-amber-500 text-slate-950 text-[9px] font-black px-2 py-0.5 rounded-full">${m.percentage}% OFF</span>
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

            function changePage(direction) {
                const filtered = currentFilter === 'all' 
                    ? loadedMerchants 
                    : loadedMerchants.filter(m => m.category === currentFilter);
                const totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;

                currentPage += direction;
                if(currentPage < 1) currentPage = 1;
                if(currentPage > totalPages) currentPage = totalPages;
                renderCatalog();
            }

            function filterCategory(cat) {
                currentFilter = cat;
                currentPage = 1;
                renderCatalog();
            }

            function switchSection(sectionId) {
                ['home', 'catalog', 'insurance', 'news', 'register', 'pay', 'admin'].forEach(s => {
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

                const idx = sectionHistory.indexOf(sectionId);
                if(idx !== -1) currentSectionIndex = idx;
                
                if(sectionId === 'catalog') fetchMerchants();
                if(sectionId === 'admin') loadAdminData();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            function goBackSection() {
                currentSectionIndex--;
                if(currentSectionIndex < 0) currentSectionIndex = sectionHistory.length - 1;
                switchSection(sectionHistory[currentSectionIndex]);
            }

            function goForwardSection() {
                currentSectionIndex++;
                if(currentSectionIndex >= sectionHistory.length) currentSectionIndex = 0;
                switchSection(sectionHistory[currentSectionIndex]);
            }

            function openLoginModal() { document.getElementById('loginModal').classList.remove('hidden'); }
            function closeLoginModal() { document.getElementById('loginModal').classList.add('hidden'); document.getElementById('loginError').classList.add('hidden'); }

            function executeLogin() {
                const val = document.getElementById('loginKeyInput').value.trim();
                if(val === "admin2026" || val === "MaxShopPro") {
                    closeLoginModal();
                    switchSection('admin');
                } else {
                    const found = loadedMerchants.find(m => m.email === val);
                    if(found) {
                        closeLoginModal();
                        switchRegSub('merchant');
                        switchSection('register');
                        document.getElementById('mercEmail').value = found.email;
                        document.getElementById('mercName').value = found.name;
                        document.getElementById('merchantPaymentWrapper').classList.add('hidden');
                        alert("¡Bienvenido de nuevo! Tus datos fueron recordados. Puedes actualizar tu flyer o promoción sin volver a pagar.");
                    } else {
                        document.getElementById('loginError').classList.remove('hidden');
                    }
                }
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
                resDiv.innerHTML = `<div class="p-3 bg-[#030712] text-xs text-slate-400 animate-pulse">Registrando...</div>`;

                try {
                    const response = await fetch(`/users/?email=${encodeURIComponent(email)}&subscription_status=active`, { method: 'POST' });
                    const data = await response.json();
                    if(data.error) {
                        resDiv.innerHTML = `<div class="p-3 bg-red-950/40 text-xs text-red-300">⚠️ ${data.error}</div>`;
                    } else {
                        resDiv.innerHTML = `<div class="p-3 bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300">✨ ¡Socio registrado con éxito!</div>`;
                    }
                } catch (err) {
                    resDiv.innerHTML = `<div class="p-3 bg-red-950/40 text-xs text-red-300">❌ Error de conexión.</div>`;
                }
            });

            document.getElementById('merchantForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('mercEmail').value;
                const name = document.getElementById('mercName').value;
                const cat = document.getElementById('mercCat').value;
                const perc = document.getElementById('discPercentage').value;
                const title = document.getElementById('discTitle').value;
                
                let imgUrl = document.getElementById('mercImgUrl').value;
                const fileInput = document.getElementById('mercFile');

                if(fileInput.files && fileInput.files[0]) {
                    const reader = new FileReader();
                    reader.onload = async function(uploadEvent) {
                        await sendMerchantToServer(email, name, cat, uploadEvent.target.result, perc, title);
                    };
                    reader.readAsDataURL(fileInput.files[0]);
                } else {
                    await sendMerchantToServer(email, name, cat, imgUrl || 'https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=600&q=80', perc, title);
                }
            });

            async function sendMerchantToServer(email, name, cat, imgUrl, perc, title) {
                const wrapper = document.getElementById('merchantPaymentWrapper');
                const btn = document.getElementById('btnMerchantSubmit');
                const resDiv = document.getElementById('merchantResult');

                const isReturningMerchant = loadedMerchants.some(m => m.email === email);

                if(wrapper.classList.contains('hidden') && !isReturningMerchant) {
                    wrapper.classList.remove('hidden');
                    btn.textContent = "Finalizar y Publicar";
                    return;
                }

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 bg-[#030712] text-xs text-slate-400 animate-pulse">Publicando...</div>`;

                try {
                    const res = await fetch(`/api/merchants/create?email=${encodeURIComponent(email)}&name=${encodeURIComponent(name)}&category=${encodeURIComponent(cat)}&image_url=${encodeURIComponent(imgUrl)}&lat=-34.6&lng=-58.3&title=${encodeURIComponent(title)}&percentage=${perc}`, { method: 'POST' });
                    const data = await res.json();
                    if(data.merchant_id) {
                        resDiv.innerHTML = `<div class="p-3 bg-cyan-950/40 border border-cyan-500/30 text-xs text-cyan-300">🏢 ¡Publicación actualizada con éxito en ¡Descuentos de Locos!!</div>`;
                        fetchMerchants();
                    }
                } catch(err) {
                    resDiv.innerHTML = `<div class="p-3 bg-red-950/40 text-xs text-red-300">❌ Error al publicar.</div>`;
                }
            }

            document.getElementById('paymentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('payEmail').value;
                const merchantId = document.getElementById('payMerchantSelect').value;
                const amount = document.getElementById('payAmount').value;
                const resDiv = document.getElementById('paymentResult');

                resDiv.classList.remove('hidden');
                resDiv.innerHTML = `<div class="p-3 bg-[#030712] text-xs text-slate-400 animate-pulse text-center">Procesando pago QR...</div>`;

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

            async function loadAdminData() {
                const uList = document.getElementById('adminUsersList');
                const mList = document.getElementById('adminMerchantsList');
                uList.innerHTML = "Cargando...";
                mList.innerHTML = "Cargando...";

                try {
                    const uRes = await fetch('/api/admin/users');
                    const users = await uRes.json();
                    uList.innerHTML = users.length === 0 ? '<span class="text-slate-500">Sin socios.</span>' : '';
                    users.forEach(u => {
                        uList.innerHTML += `<div class="bg-slate-900 p-2 rounded-lg border border-slate-800 flex justify-between items-center text-xs"><span>${u.email}</span><span class="text-emerald-400 font-bold">${u.subscription_status}</span></div>`;
                    });

                    uList.innerHTML += `<div class="mt-3 p-2 bg-slate-950 border border-slate-800 rounded-lg text-[11px] text-slate-400"><strong>Control Propietario:</strong> Tienes acceso total para desplazar secciones, verificar pagos y administrar comercios.</div>`;

                    mList.innerHTML = loadedMerchants.length === 0 ? '<span class="text-slate-500">Sin comercios.</span>' : '';
                    loadedMerchants.forEach(m => {
                        mList.innerHTML += `<div class="bg-slate-900 p-2 rounded-lg border border-slate-800 flex justify-between items-center text-xs"><span>${m.name} (${m.category})</span><span class="text-cyan-400 font-bold">${m.percentage}% OFF</span></div>`;
                    });
                } catch(e) {
                    uList.innerHTML = '<span class="text-red-400">Error al cargar.</span>';
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
                "email": m.email,
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

@app.post("/api/merchants/create")
def create_full_merchant(email: str, name: str, category: str, image_url: str, lat: float, lng: float, title: str, percentage: float):
    db = SessionLocal()
    try:
        existing_m = db.query(MerchantDB).filter(MerchantDB.email == email).first()
        if existing_m:
            existing_m.name = name
            existing_m.category = category
            existing_m.image_url = image_url
            db.commit()
            
            disc = db.query(DiscountDB).filter(DiscountDB.merchant_id == existing_m.id).first()
            if disc:
                disc.title = title
                disc.percentage = percentage
                db.commit()
            return {"message": "Comercio actualizado con éxito sin recargo", "merchant_id": existing_m.id}

        new_m = MerchantDB(email=email, name=name, category=category, image_url=image_url, lat=lat, lng=lng)
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
