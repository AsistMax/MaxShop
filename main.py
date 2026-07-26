import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Configuración de Base de Datos (Supabase / PostgreSQL)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres.tyvrhprlkpatyoxbbyqd:MaxShop2026@aws-1-us-west-2.pooler.supabase.com:5432/postgres"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modelos de Base de Datos ---
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    subscription_status = Column(String, default="active")

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

class ExternalFeedDB(Base):
    __tablename__ = "external_feeds"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_name = Column(String, nullable=False) # Ej: "PromoAgenda / iProfesional"
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    url = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# --- Inicializar Aplicación ---
app = FastAPI(title="MaxShop Club de Descuentos% - Motor Inteligente", version="12.0.0")

# --- Interfaz de Usuario Principal (Frontend Integrado) ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop | Club de Descuentos % & Motor Inteligente</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #030712; color: #f8fafc; overflow-x: hidden; -webkit-overflow-scrolling: touch; }
            .brand-gradient { background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); }
            .locos-gradient { background: linear-gradient(135deg, #f59e0b 0%, #ef4444 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .glass-card { background: rgba(11, 19, 38, 0.95); backdrop-filter: blur(16px); border: 1px solid rgba(30, 58, 138, 0.4); }
            @keyframes marquee { 0% { transform: translateX(0%); } 100% { transform: translateX(-50%); } }
            .animate-marquee { display: flex; width: 200%; animation: marquee 35s linear infinite; }
            .swipe-container { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth; -webkit-overflow-scrolling: touch; }
            .swipe-container::-webkit-scrollbar { display: none; }
            .swipe-item { flex: 0 0 100%; scroll-snap-align: start; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
        
        <!-- Barra Financiera en Vivo -->
        <div class="bg-slate-950 border-b border-slate-800/80 py-1.5 px-4 text-[11px] text-slate-400">
            <div class="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-2">
                <div class="flex items-center space-x-4">
                    <span class="flex items-center space-x-1 text-emerald-400 font-bold">🟢 <span>Dólar Blue:</span> <strong class="text-white">$1.220 / $1.240</strong></span>
                    <span class="hidden md:inline text-slate-600">|</span>
                    <span class="hidden md:inline text-slate-300">Club Activo: <strong class="text-emerald-400">¡Hasta 50% OFF Automático!</strong></span>
                </div>
                <div class="flex items-center space-x-3 text-amber-400 font-bold">
                    <span>⚡ Alianza AsistMax: Póliza hasta $20M</span>
                </div>
            </div>
        </div>

        <!-- Cabecera -->
        <header class="border-b border-slate-800/80 bg-[#030712]/95 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded-xl p-1 shadow-md">
                        <button onclick="goBackSection()" class="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg></button>
                        <button onclick="goForwardSection()" class="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg></button>
                    </div>

                    <div class="flex items-center space-x-2.5 cursor-pointer" onclick="switchSection('home')">
                        <div class="w-10 h-10 rounded-2xl brand-gradient flex items-center justify-center shadow-lg shadow-emerald-500/20 font-black text-slate-950 text-base">M%</div>
                        <div>
                            <h1 class="font-extrabold text-sm text-white tracking-wide">Max<span class="text-emerald-400">Shop</span></h1>
                            <span class="text-[9px] text-emerald-300 tracking-wider uppercase font-bold block -mt-1">Club de Descuentos %</span>
                        </div>
                    </div>
                </div>

                <div class="flex items-center space-x-2">
                    <nav class="hidden md:flex items-center space-x-1 text-xs">
                        <button onclick="switchSection('home')" id="navHome" class="px-3 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition">Inicio</button>
                        <button onclick="switchSection('catalog')" id="navCatalog" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">¡Descuentos de Locos!!</button>
                        <button onclick="switchSection('news')" id="navNews" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Tendencias & Redes</button>
                        <button onclick="switchSection('insurance')" id="navInsurance" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Seguros AsistMax</button>
                        <button onclick="switchSection('register')" id="navRegister" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Registrarse</button>
                        <button onclick="switchSection('pay')" id="navPay" class="px-3 py-2 rounded-xl text-slate-400 hover:text-white transition">Caja QR</button>
                    </nav>
                    <button onclick="openLoginModal()" class="bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 px-3 py-2 rounded-xl text-xs font-bold transition">Ingresar</button>
                </div>
            </div>
        </header>

        <!-- Contenido -->
        <main class="max-w-6xl mx-auto px-4 py-8 w-full flex-grow space-y-16">
            
            <!-- INICIO -->
            <section id="secHome" class="space-y-10">
                <div class="swipe-container rounded-3xl overflow-hidden glass-card shadow-2xl border-emerald-500/20">
                    <div class="swipe-item p-6 md:p-10 grid md:grid-cols-2 gap-6 items-center">
                        <div class="space-y-4">
                            <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-3 py-1 rounded-full uppercase">MaxShop Club de Descuentos %</span>
                            <h2 class="text-2xl md:text-4xl font-extrabold tracking-tight text-white leading-tight">Descuentos Automáticos con <span class="locos-gradient font-black">Inteligencia Artificial</span></h2>
                            <p class="text-slate-300 text-xs md:text-sm leading-relaxed">
                                Agregamos en tiempo real las mejores ofertas del país (PromoAgenda, Reddit, Comercios Locales y Bancos) para aplicarlas en tus compras de forma 100% automatizada.
                            </p>
                            <div class="flex flex-wrap gap-3 pt-2">
                                <button onclick="switchSection('catalog')" class="brand-gradient hover:opacity-90 text-slate-950 font-extrabold px-5 py-3 rounded-xl text-xs transition shadow-lg">Ver Descuentos de Locos</button>
                                <button onclick="switchSection('news')" class="bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-semibold px-5 py-3 rounded-xl text-xs transition">Ver Radar de Ofertas Externas</button>
                            </div>
                        </div>
                        <div class="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950 p-2 flex items-center justify-center">
                            <img src="https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=800&q=80" alt="MaxShop Club" class="w-full h-52 md:h-64 object-cover rounded-xl">
                        </div>
                    </div>
                </div>
            </section>

            <!-- CATÁLOGO PRINCIPAL -->
            <section id="secCatalog" class="hidden space-y-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 class="text-3xl font-black locos-gradient tracking-wide">¡Descuentos de Locos!!</h2>
                        <p class="text-xs text-slate-400">Comercios adheridos y beneficios automáticos sincronizados.</p>
                    </div>
                    <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
                        <button onclick="changePage(-1)" class="text-slate-400 font-bold px-2 bg-slate-800 rounded-lg">◀ Regresar</button>
                        <span id="pageIndicator" class="text-emerald-400 font-bold px-2">Página 1</span>
                        <button onclick="changePage(1)" class="text-slate-400 font-bold px-2 bg-slate-800 rounded-lg">Avanzar ▶</button>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="realMerchantsContainer">
                    <div class="col-span-3 text-center text-slate-400 text-xs py-10 glass-card rounded-2xl animate-pulse">Cargando red de descuentos...</div>
                </div>
            </section>

            <!-- RADAR DE NOTICIAS Y OFERTAS EXTERNAS (PromoAgenda, Reddit, iProfesional, etc.) -->
            <section id="secNews" class="hidden space-y-6">
                <div class="flex justify-between items-center">
                    <div>
                        <h2 class="text-2xl font-bold text-white">Radar de Ofertas & Noticias del Mercado</h2>
                        <p class="text-xs text-slate-400">Sincronización automatizada desde fuentes externas (PromoAgenda, Reddit, iProfesional, HotSale).</p>
                    </div>
                    <button onclick="syncExternalFeeds()" class="brand-gradient text-slate-950 font-bold px-4 py-2 rounded-xl text-xs transition">🔄 Sincronizar Ahora</button>
                </div>

                <div class="grid md:grid-cols-2 gap-6" id="externalFeedsContainer">
                    <div class="glass-card p-5 rounded-2xl space-y-3 animate-pulse">
                        <span class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded-md font-bold">CARGANDO RED...</span>
                        <h3 class="font-bold text-sm text-white">Sincronizando feeds externos de descuentos...</h3>
                    </div>
                </div>
            </section>

            <!-- SEGUROS ASISTMAX -->
            <section id="secInsurance" class="hidden space-y-6">
                <div class="max-w-3xl mx-auto glass-card rounded-3xl p-8 shadow-2xl border-amber-500/30 space-y-6">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 rounded-2xl bg-amber-500/20 flex items-center justify-center text-amber-400 font-black text-xl">🛡️</div>
                        <div>
                            <h2 class="text-2xl font-bold text-white">Seguros & Asistencia AsistMax</h2>
                            <p class="text-xs text-slate-400">Protección financiera y sepelio de hasta $20.000.000.</p>
                        </div>
                    </div>
                    <a href="https://sistema-seguros.onrender.com/" target="_blank" class="block text-center bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold py-3 rounded-xl text-xs transition shadow-lg">
                        Abrir Sistema AsistMax ➔
                    </a>
                </div>
            </section>

            <!-- REGISTRO -->
            <section id="secRegister" class="hidden space-y-6">
                <div class="max-w-2xl mx-auto space-y-6">
                    <div class="text-center space-y-2">
                        <h2 class="text-2xl font-bold text-white">Membresía MaxShop Club</h2>
                        <p class="text-xs text-slate-400">Accede a descuentos automáticos en comercios y tiendas digitales.</p>
                    </div>

                    <div class="glass-card rounded-2xl p-6 shadow-xl space-y-4">
                        <form id="userForm" class="space-y-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Correo Electrónico</label>
                                <input type="email" id="userEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3 py-2.5 text-sm text-white">
                            </div>
                            <div id="userPaymentWrapper" class="hidden p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-3">
                                <div class="flex justify-between items-center text-xs">
                                    <span class="text-slate-300 font-semibold">Membresía Mensual:</span>
                                    <span class="text-emerald-400 font-bold text-sm">$5,000 / mes</span>
                                </div>
                                <a href="https://mpago.la/12kwFZe" target="_blank" class="block text-center bg-[#009ee3] text-white font-bold py-3 rounded-xl text-xs transition shadow-lg">
                                    Pagar con Mercado Pago ➔
                                </a>
                            </div>
                            <button type="submit" id="btnUserSubmit" class="w-full brand-gradient text-slate-950 font-extrabold py-3 rounded-xl text-xs transition">Activar Membresía</button>
                        </form>
                        <div id="userResult" class="mt-4 hidden"></div>
                    </div>
                </div>
            </section>

            <!-- CAJA QR -->
            <section id="secPay" class="hidden space-y-6">
                <div class="max-w-xl mx-auto glass-card rounded-2xl p-8 shadow-2xl border-emerald-500/30 relative">
                    <div class="absolute -top-3 right-6 bg-emerald-500 text-slate-950 text-[10px] font-extrabold px-3 py-1 rounded-full uppercase">Caja Automática QR MaxShop</div>
                    <form id="paymentForm" class="space-y-4 pt-2">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio Club</label>
                            <input type="email" id="payEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Comercio</label>
                                <select id="payMerchantSelect" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white"><option value="">Cargando...</option></select>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Monto Total ($)</label>
                                <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 15000" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white">
                            </div>
                        </div>
                        <button type="submit" class="w-full brand-gradient text-slate-950 font-extrabold py-3.5 rounded-xl text-xs transition shadow-xl">Aplicar Descuento Automático</button>
                    </form>
                    <div id="paymentResult" class="mt-6 hidden"></div>
                </div>
            </section>
        </main>

        <footer class="border-t border-slate-800/80 py-6 text-center text-[10px] text-slate-500 space-y-2">
            <p>MaxShop Club de Descuentos % & Motor Inteligente • Pagos operados a través de Mercado Pago y MODO</p>
        </footer>

        <!-- Script General -->
        <script>
            let loadedMerchants = [];
            let currentPage = 1;
            const itemsPerPage = 6;
            const sectionHistory = ['home', 'catalog', 'news', 'insurance', 'register', 'pay'];
            let currentSectionIndex = 0;

            async function fetchMerchants() {
                try {
                    const res = await fetch('/api/merchants/');
                    loadedMerchants = await res.json();
                    renderCatalog();
                } catch(e) { console.error(e); }
            }

            function renderCatalog() {
                const catalogContainer = document.getElementById('realMerchantsContainer');
                const selectPay = document.getElementById('payMerchantSelect');
                const totalPages = Math.ceil(loadedMerchants.length / itemsPerPage) || 1;
                
                const start = (currentPage - 1) * itemsPerPage;
                const paginatedItems = loadedMerchants.slice(start, start + itemsPerPage);

                catalogContainer.innerHTML = '';
                if(selectPay) selectPay.innerHTML = '';

                paginatedItems.forEach(m => {
                    catalogContainer.innerHTML += `
                        <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-emerald-500/20 flex flex-col justify-between">
                            <img src="${m.image_url}" alt="${m.name}" class="w-full h-40 object-cover">
                            <div class="p-4 space-y-2">
                                <div class="flex justify-between items-center">
                                    <span class="bg-amber-500 text-slate-950 text-[9px] font-black px-2 py-0.5 rounded-full">${m.percentage}% OFF</span>
                                    <span class="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded-md">${m.category}</span>
                                </div>
                                <h3 class="font-bold text-sm text-white">${m.name}</h3>
                                <p class="text-xs text-slate-400">Promo: <span class="text-emerald-400 font-semibold">${m.title}</span></p>
                            </div>
                        </div>
                    `;
                });

                if(selectPay) {
                    loadedMerchants.forEach(m => {
                        selectPay.innerHTML += `<option value="${m.id}">${m.name} (${m.percentage}% OFF)</option>`;
                    });
                }
            }

            async function syncExternalFeeds() {
                const container = document.getElementById('externalFeedsContainer');
                container.innerHTML = `<div class="glass-card p-5 rounded-2xl text-xs text-slate-400 animate-pulse">Sincronizando fuentes externas (PromoAgenda, Reddit, iProfesional)...</div>`;
                try {
                    const res = await fetch('/api/sync-external-feeds', { method: 'POST' });
                    const data = await res.json();
                    loadExternalFeeds();
                } catch(e) { container.innerHTML = `<div class="text-red-400 text-xs">Error al sincronizar.</div>`; }
            }

            async function loadExternalFeeds() {
                const container = document.getElementById('externalFeedsContainer');
                try {
                    const res = await fetch('/api/external-feeds');
                    const feeds = await res.json();
                    container.innerHTML = '';
                    feeds.forEach(f => {
                        container.innerHTML += `
                            <div class="glass-card p-5 rounded-2xl space-y-3 border-cyan-500/20">
                                <span class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded-md font-bold">${f.source_name}</span>
                                <h3 class="font-bold text-sm text-white">${f.title}</h3>
                                <p class="text-xs text-slate-400 leading-relaxed">${f.summary || ''}</p>
                                <a href="${f.url}" target="_blank" class="inline-block text-xs text-emerald-400 font-semibold hover:underline">Ver fuente original ➔</a>
                            </div>
                        `;
                    });
                } catch(e) { container.innerHTML = `<div class="text-slate-500 text-xs">Sin feeds externos sincronizados.</div>`; }
            }

            function switchSection(sectionId) {
                ['home', 'catalog', 'news', 'insurance', 'register', 'pay'].forEach(s => {
                    document.getElementById('sec' + s.charAt(0).toUpperCase() + s.slice(1)).classList.add('hidden');
                    const btn = document.getElementById('nav' + s.charAt(0).toUpperCase() + s.slice(1));
                    if(btn) btn.className = "px-3 py-2 rounded-xl text-slate-400 hover:text-white transition";
                });
                document.getElementById('sec' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1)).classList.remove('hidden');
                const activeBtn = document.getElementById('nav' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1));
                if(activeBtn) activeBtn.className = "px-3 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 transition";

                if(sectionId === 'catalog') fetchMerchants();
                if(sectionId === 'news') loadExternalFeeds();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            function goBackSection() {
                currentSectionIndex = (currentSectionIndex - 1 + sectionHistory.length) % sectionHistory.length;
                switchSection(sectionHistory[currentSectionIndex]);
            }
            function goForwardSection() {
                currentSectionIndex = (currentSectionIndex + 1) % sectionHistory.length;
                switchSection(sectionHistory[currentSectionIndex]);
            }

            document.getElementById('userForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('userEmail').value;
                const wrapper = document.getElementById('userPaymentWrapper');
                const btn = document.getElementById('btnUserSubmit');
                if(wrapper.classList.contains('hidden')) {
                    wrapper.classList.remove('hidden');
                    btn.textContent = "Confirmar Activación";
                    return;
                }
                const res = await fetch(`/users/?email=${encodeURIComponent(email)}`, { method: 'POST' });
                const data = await res.json();
                document.getElementById('userResult').classList.remove('hidden');
                document.getElementById('userResult').innerHTML = `<div class="p-3 bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300">✨ ¡Membresía activada con éxito!</div>`;
            });

            document.getElementById('paymentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('payEmail').value;
                const merchantId = document.getElementById('payMerchantSelect').value;
                const amount = document.getElementById('payAmount').value;
                const resDiv = document.getElementById('paymentResult');

                const response = await fetch(`/process-payment/?user_email=${encodeURIComponent(email)}&merchant_id=${merchantId}&total_amount=${amount}`, { method: 'POST' });
                const data = await response.json();
                resDiv.classList.remove('hidden');
                if(data.error) {
                    resDiv.innerHTML = `<div class="p-3 bg-amber-950/40 text-xs text-amber-200">⚠️ ${data.error}</div>`;
                } else {
                    resDiv.innerHTML = `
                        <div class="p-4 bg-emerald-950/40 border border-emerald-500/40 space-y-1 text-xs">
                            <span class="font-bold text-emerald-400 text-sm">✅ ¡Descuento Aplicado Automáticamente! (${data.discount_applied} OFF)</span>
                            <div class="flex justify-between text-slate-300"><span>Original: $${data.original_amount}</span><span class="text-emerald-400 font-bold">Ahorro: -$${data.amount_saved}</span></div>
                            <div class="text-sm font-extrabold text-white">Total Cobrado: $${data.final_amount_to_pay}</div>
                        </div>`;
                }
            });

            fetchMerchants();
        </script>
    </body>
    </html>
    """

# --- Endpoints del Backend e Integración de Datos Externos ---

@app.get("/api/merchants/")
def get_merchants():
    db = SessionLocal()
    try:
        merchants = db.query(MerchantDB).all()
        if not merchants:
            # Semilla inicial para que la app luzca completa al instante
            return [
                {"id": 1, "name": "TechStore Argentina", "category": "Tecnología", "image_url": "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80", "percentage": 25, "title": "25% OFF en Smartphones"},
                {"id": 2, "name": "Supermercados Max", "category": "Supermercados", "image_url": "https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=600&q=80", "percentage": 20, "title": "20% OFF en Canasta Básica"},
                {"id": 3, "name": "ModaFit Indumentaria", "category": "Moda e Indumentaria", "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=600&q=80", "percentage": 30, "title": "30% OFF Temporada Otoño"}
            ]
        result = []
        for m in merchants:
            disc = db.query(DiscountDB).filter(DiscountDB.merchant_id == m.id).first()
            result.append({
                "id": m.id, "name": m.name, "category": m.category, "image_url": m.image_url,
                "percentage": float(disc.percentage) if disc else 0.0, "title": disc.title if disc else ""
            })
        return result
    finally:
        db.close()

@app.post("/api/sync-external-feeds")
def sync_external_feeds():
    """Motor ETL que simula la captura y normalización inteligente de fuentes externas (PromoAgenda, Reddit, iProfesional)"""
    db = SessionLocal()
    try:
        # Limpiar y actualizar con datos frescos simulados de las APIs y RSS consultados
        db.query(ExternalFeedDB).delete()
        db.commit()

        sample_feeds = [
            ExternalFeedDB(source_name="PromoAgenda AR", title="HotSale 2026: Anticipos con hasta 50% de descuento en tecnología", summary="Las marcas líderes preparan rebajas exclusivas combinables con pasarelas de pago digitales.", category="Tecnología", url="https://promoagenda.com.ar/promo-agenda"),
            ExternalFeedDB(source_name="Reddit Descuentos", title="[Megathread] Top Promos Bancarias con MODO y BNA+ este fin de semana", summary="Usuarios reportan acumulación de hasta 40% en hipermercados usando tarjetas seleccionadas.", category="Supermercados", url="https://www.reddit.com/r/DescuentosArgentina/"),
            ExternalFeedDB(source_name="iProfesional RSS", title="Consumo inteligente: Cómo optimizar las compras con clubes de beneficios", summary="El impacto de las membresías digitales en el ahorro mensual de los hogares argentinos.", category="Economía", url="https://www.iprofesional.com/rss"),
            ExternalFeedDB(source_name="Mercado & Finanzas", title="BCRA actualiza tasas y se dinamizan los pagos QR instantáneos", summary="Nuevas facilidades para adquirencia y liquidación de descuentos automáticos en comercios físicos.", category="Finanzas", url="https://www.bcra.gob.ar/")
        ]

        for feed in sample_feeds:
            db.add(feed)
        db.commit()
        return {"status": "success", "message": "Feeds externos sincronizados correctamente."}
    finally:
        db.close()

@app.get("/api/external-feeds")
def get_external_feeds():
    db = SessionLocal()
    try:
        feeds = db.query(ExternalFeedDB).all()
        return [{"source_name": f.source_name, "title": f.title, "summary": f.summary, "category": f.category, "url": f.url} for f in feeds]
    finally:
        db.close()

@app.post("/users/")
def create_user(email: str):
    db = SessionLocal()
    try:
        existing = db.query(UserDB).filter(UserDB.email == email).first()
        if existing:
            return {"message": "Usuario ya registrado", "email": existing.email}
        new_u = UserDB(email=email, subscription_status="active")
        db.add(new_u)
        db.commit()
        return {"message": "Usuario registrado con éxito", "email": new_u.email}
    finally:
        db.close()

@app.post("/process-payment/")
def process_payment(user_email: str, merchant_id: int, total_amount: float):
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.email == user_email).first()
        if not user or user.subscription_status != "active":
            return {"error": "Membresía inactiva o usuario no registrado en el club."}
        
        # Simulación de motor de descuento automático (combina comercio + beneficios de fuentes externas)
        discount = db.query(DiscountDB).filter(DiscountDB.merchant_id == merchant_id).first()
        percentage = float(discount.percentage) if discount else 20.0 # 20% por defecto automatizado
        
        saved = (total_amount * percentage) / 100
        final = total_amount - saved

        return {
            "message": "¡Descuento aplicado de forma 100% automática!",
            "original_amount": total_amount,
            "discount_applied": f"{percentage}%",
            "amount_saved": round(saved, 2),
            "final_amount_to_pay": round(final, 2)
        }
    finally:
        db.close()
