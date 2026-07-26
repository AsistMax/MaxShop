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

class UserCardDB(Base):
    __tablename__ = "user_cards"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_email = Column(String, nullable=False)
    card_alias = Column(String, nullable=False)
    card_last4 = Column(String, nullable=False)
    card_brand = Column(String, nullable=False) # Visa, Master, MODO, etc.

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
    source_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    url = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# --- Inicializar Aplicación ---
app = FastAPI(title="MaxShop Club de Descuentos% - Feed Vertical", version="13.0.0")

# --- Interfaz de Usuario Vertical Unificada ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="es" class="scroll-smooth">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop | Club de Descuentos % & Pagos Automáticos</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #030712; color: #f8fafc; overflow-x: hidden; }
            .brand-gradient { background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); }
            .locos-gradient { background: linear-gradient(135deg, #f59e0b 0%, #ef4444 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .glass-card { background: rgba(11, 19, 38, 0.95); backdrop-filter: blur(16px); border: 1px solid rgba(30, 58, 138, 0.4); }
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
        
        <!-- Barra Superior Financiera -->
        <div class="bg-slate-950 border-b border-slate-800/80 py-2 px-4 text-[11px] text-slate-400">
            <div class="max-w-5xl mx-auto flex flex-wrap justify-between items-center gap-2">
                <div class="flex items-center space-x-3">
                    <span class="text-emerald-400 font-bold">🟢 Dólar Blue: $1.220 / $1.240</span>
                    <span class="text-slate-600 hidden sm:inline">|</span>
                    <span class="text-slate-300 hidden sm:inline">Descuentos Universales Automáticos Activos</span>
                </div>
                <div class="text-amber-400 font-bold">
                    <span>⚡ AsistMax Seguros hasta $20M</span>
                </div>
            </div>
        </div>

        <!-- Cabecera de Navegación Vertical -->
        <header class="border-b border-slate-800/80 bg-[#030712]/95 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
                <div class="flex items-center space-x-2.5 cursor-pointer" onclick="window.scrollTo({top:0, behavior:'smooth'})">
                    <div class="w-10 h-10 rounded-2xl brand-gradient flex items-center justify-center shadow-lg shadow-emerald-500/20 font-black text-slate-950 text-base">M%</div>
                    <div>
                        <h1 class="font-extrabold text-sm text-white tracking-wide">Max<span class="text-emerald-400">Shop</span></h1>
                        <span class="text-[9px] text-emerald-300 tracking-wider uppercase font-bold block -mt-1">Club de Descuentos %</span>
                    </div>
                </div>

                <nav class="hidden md:flex items-center space-x-2 text-xs font-semibold">
                    <a href="#hero" class="text-slate-300 hover:text-white px-3 py-2 rounded-xl transition">Inicio</a>
                    <a href="#catalog" class="text-slate-300 hover:text-white px-3 py-2 rounded-xl transition">Descuentos</a>
                    <a href="#news" class="text-slate-300 hover:text-white px-3 py-2 rounded-xl transition">Radar & Noticias</a>
                    <a href="#wallet" class="text-slate-300 hover:text-white px-3 py-2 rounded-xl transition">Mis Tarjetas</a>
                    <a href="#pay" class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-2 rounded-xl transition">Caja QR / Point Tap</a>
                </nav>
            </div>
        </header>

        <!-- CONTENIDO PRINCIPAL EN DESPLAZAMIENTO VERTICAL -->
        <main class="max-w-5xl mx-auto px-4 py-8 w-full flex-grow space-y-20">
            
            <!-- 1. INICIO / HERO -->
            <section id="hero" class="glass-card p-6 md:p-10 rounded-3xl shadow-2xl border-emerald-500/20 grid md:grid-cols-2 gap-8 items-center">
                <div class="space-y-4">
                    <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-3 py-1 rounded-full uppercase">Plataforma Inteligente de Ahorro</span>
                    <h2 class="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">Compra y Ahorra de Forma <span class="locos-gradient font-black">100% Automática</span></h2>
                    <p class="text-slate-300 text-xs md:text-sm leading-relaxed">
                        Asocia tus tarjetas una sola vez. Nuestro motor unifica descuentos de comercios, bancos y fuentes externas para aplicarlos al instante mediante escaneo de cámara o proximidad (Point Tap).
                    </p>
                    <div class="flex flex-wrap gap-3 pt-2">
                        <a href="#pay" class="brand-gradient hover:opacity-90 text-slate-950 font-extrabold px-5 py-3 rounded-xl text-xs transition shadow-lg text-center">Ir a Caja Automática</a>
                        <a href="#wallet" class="bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-semibold px-5 py-3 rounded-xl text-xs transition text-center">Registrarme / Mis Tarjetas</a>
                    </div>
                </div>
                <div class="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950 p-2 flex items-center justify-center">
                    <img src="https://images.unsplash.com/photo-1556742049-0a67d553c299?auto=format&fit=crop&w=800&q=80" alt="MaxShop" class="w-full h-56 md:h-72 object-cover rounded-xl">
                </div>
            </section>

            <!-- 2. CATÁLOGO DE COMERCIOS Y DESCUENTOS -->
            <section id="catalog" class="space-y-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 class="text-3xl font-black locos-gradient tracking-wide">¡Descuentos de Locos en Comercios!</h2>
                        <p class="text-xs text-slate-400">Beneficios aplicables con cualquier medio de pago asociado en tu cuenta.</p>
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="realMerchantsContainer">
                    <div class="col-span-3 text-center text-slate-400 text-xs py-10 glass-card rounded-2xl animate-pulse">Cargando red de comercios...</div>
                </div>
            </section>

            <!-- 3. RADAR DE NOTICIAS Y OFERTAS EXTERNAS -->
            <section id="news" class="space-y-6">
                <div class="flex justify-between items-center">
                    <div>
                        <h2 class="text-2xl font-bold text-white">Radar de Ofertas & Noticias del Mercado</h2>
                        <p class="text-xs text-slate-400">Sincronización continua de PromoAgenda, Reddit, iProfesional y portales de consumo.</p>
                    </div>
                    <button onclick="syncExternalFeeds()" class="brand-gradient text-slate-950 font-bold px-4 py-2 rounded-xl text-xs transition">🔄 Actualizar Feeds</button>
                </div>
                <div class="grid md:grid-cols-2 gap-6" id="externalFeedsContainer">
                    <div class="glass-card p-5 rounded-2xl space-y-3 animate-pulse text-xs text-slate-400">Cargando fuentes de información externas...</div>
                </div>
            </section>

            <!-- 4. GESTIÓN DE USUARIO Y ASOCIACIÓN DE TARJETAS (BILLETERA) -->
            <section id="wallet" class="space-y-6">
                <div class="max-w-3xl mx-auto glass-card rounded-3xl p-8 shadow-2xl border-cyan-500/30 space-y-6">
                    <div>
                        <span class="text-cyan-400 text-[10px] font-extrabold uppercase bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/30">Billetera Club MaxShop</span>
                        <h2 class="text-2xl font-bold text-white mt-2">Registro de Usuario y Tarjetas</h2>
                        <p class="text-xs text-slate-400">Asocia tus tarjetas para que el sistema aplique descuentos automáticos sin importar con cuál pagues.</p>
                    </div>

                    <!-- Formulario de Registro / Activación de Socio -->
                    <form id="userForm" class="space-y-4 pt-2 border-t border-slate-800">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Correo Electrónico (Socio)</label>
                            <input type="email" id="userEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white">
                        </div>
                        <button type="submit" class="w-full brand-gradient text-slate-950 font-extrabold py-3 rounded-xl text-xs transition shadow-lg">1. Validar / Activar Membresía</button>
                    </form>

                    <!-- Formulario para Asociar Tarjeta -->
                    <div id="cardSection" class="hidden space-y-4 pt-4 border-t border-slate-800">
                        <h3 class="font-bold text-sm text-white">Asociar Nueva Tarjeta de Débito/Crédito</h3>
                        <form id="cardForm" class="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Alias (Ej: Visa Galicia)</label>
                                <input type="text" id="cardAlias" required placeholder="Visa Personal" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Últimos 4 Dígitos</label>
                                <input type="text" maxlength="4" id="cardLast4" required placeholder="4321" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Entidad / Red</label>
                                <select id="cardBrand" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white">
                                    <option value="Visa">Visa</option>
                                    <option value="Mastercard">Mastercard</option>
                                    <option value="MODO">MODO / Billetera</option>
                                    <option value="Amex">American Express</option>
                                </select>
                            </div>
                            <button type="submit" class="md:col-span-3 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold py-2.5 rounded-xl text-xs transition">Guardar Tarjeta en Billetera ➔</button>
                        </form>

                        <div class="space-y-2 pt-2">
                            <span class="text-xs font-bold text-slate-300">Tus tarjetas asociadas:</span>
                            <div id="userCardsList" class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-400">
                                <span class="text-slate-500 italic">No hay tarjetas asociadas aún.</span>
                            </div>
                        </div>
                    </div>

                    <div id="userResult"></div>
                </div>
            </section>

            <!-- 5. CAJA AUTOMÁTICA QR & POINT TAP -->
            <section id="pay" class="space-y-6">
                <div class="max-w-xl mx-auto glass-card rounded-3xl p-8 shadow-2xl border-emerald-500/30 relative">
                    <div class="absolute -top-3 right-6 bg-emerald-500 text-slate-950 text-[10px] font-extrabold px-3 py-1 rounded-full uppercase">Caja Automática Universal</div>
                    
                    <div class="space-y-4 pt-2">
                        <div>
                            <h2 class="text-2xl font-bold text-white">Caja Inteligente (Point Tap & QR)</h2>
                            <p class="text-xs text-slate-400">Elige cómo deseas abonar en el comercio para aplicar el descuento automático universal.</p>
                        </div>

                        <form id="paymentForm" class="space-y-4">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Email del Socio Club</label>
                                <input type="email" id="payEmail" required placeholder="tu_correo@email.com" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white">
                            </div>
                            <div class="grid grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Comercio Adherido</label>
                                    <select id="payMerchantSelect" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white"><option value="">Cargando...</option></select>
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-slate-400 mb-1">Monto de Compra ($)</label>
                                    <input type="number" step="0.01" id="payAmount" required placeholder="Ej: 15000" class="w-full bg-[#030712] border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white">
                                </div>
                            </div>

                            <!-- Selector de Modo de Pago (Point Tap / Escaneo de Cámara) -->
                            <div class="space-y-2 pt-1">
                                <label class="block text-xs font-medium text-slate-400">Método de Cobro en Tienda</label>
                                <div class="grid grid-cols-2 gap-3">
                                    <button type="button" onclick="selectPaymentMethod('tap')" id="btnTap" class="p-3 rounded-xl border border-emerald-500 bg-emerald-500/10 text-emerald-400 font-bold text-xs text-center transition">📱 Point Tap (Acercar Celular)</button>
                                    <button type="button" onclick="selectPaymentMethod('qr')" id="btnQr" class="p-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-400 font-bold text-xs text-center transition">📷 Escaneo de Cámara QR</button>
                                </div>
                                <input type="hidden" id="selectedMethod" value="tap">
                            </div>

                            <button type="submit" class="w-full brand-gradient text-slate-950 font-extrabold py-3.5 rounded-xl text-xs transition shadow-xl mt-2">Ejecutar Pago con Descuento Automático</button>
                        </form>

                        <div id="paymentResult" class="mt-6 hidden"></div>
                    </div>
                </div>
            </section>
        </main>

        <footer class="border-t border-slate-800/80 py-8 text-center text-[10px] text-slate-500 space-y-2">
            <p>MaxShop Club de Descuentos % & Motor Inteligente Universal • Todos los derechos reservados.</p>
        </footer>

        <!-- Script de Automatización -->
        <script>
            let loadedMerchants = [];

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
                catalogContainer.innerHTML = '';
                if(selectPay) selectPay.innerHTML = '';

                loadedMerchants.forEach(m => {
                    catalogContainer.innerHTML += `
                        <div class="glass-card rounded-2xl overflow-hidden shadow-lg border-emerald-500/20 flex flex-col justify-between">
                            <img src="${m.image_url}" alt="${m.name}" class="w-full h-40 object-cover">
                            <div class="p-4 space-y-2">
                                <div class="flex justify-between items-center">
                                    <span class="bg-amber-500 text-slate-950 text-[9px] font-black px-2 py-0.5 rounded-full">${m.percentage}% OFF Universal</span>
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
                container.innerHTML = `<div class="glass-card p-5 rounded-2xl text-xs text-slate-400 animate-pulse">Sincronizando fuentes externas...</div>`;
                try {
                    await fetch('/api/sync-external-feeds', { method: 'POST' });
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

            function selectPaymentMethod(method) {
                document.getElementById('selectedMethod').value = method;
                if(method === 'tap') {
                    document.getElementById('btnTap').className = "p-3 rounded-xl border border-emerald-500 bg-emerald-500/10 text-emerald-400 font-bold text-xs text-center transition";
                    document.getElementById('btnQr').className = "p-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-400 font-bold text-xs text-center transition";
                } else {
                    document.getElementById('btnQr').className = "p-3 rounded-xl border border-emerald-500 bg-emerald-500/10 text-emerald-400 font-bold text-xs text-center transition";
                    document.getElementById('btnTap').className = "p-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-400 font-bold text-xs text-center transition";
                }
            }

            // Validación de Usuario y Carga de Tarjetas
            document.getElementById('userForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('userEmail').value;
                const res = await fetch(`/users/?email=${encodeURIComponent(email)}`, { method: 'POST' });
                const data = await res.json();
                
                document.getElementById('cardSection').classList.remove('hidden');
                document.getElementById('userResult').innerHTML = `<div class="p-3 bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300 mt-2">✨ Socio validado correctamente. Ya puedes gestionar tus tarjetas abajo.</div>`;
                loadUserCards(email);
            });

            document.getElementById('cardForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('userEmail').value;
                const alias = document.getElementById('cardAlias').value;
                const last4 = document.getElementById('cardLast4').value;
                const brand = document.getElementById('cardBrand').value;

                const res = await fetch(`/api/add-card/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_email: email, card_alias: alias, card_last4: last4, card_brand: brand })
                });
                if(res.ok) {
                    document.getElementById('cardAlias').value = '';
                    document.getElementById('cardLast4').value = '';
                    loadUserCards(email);
                }
            });

            async function loadUserCards(email) {
                const res = await fetch(`/api/user-cards/?email=${encodeURIComponent(email)}`);
                const cards = await res.json();
                const list = document.getElementById('userCardsList');
                list.innerHTML = '';
                if(cards.length === 0) {
                    list.innerHTML = `<span class="text-slate-500 italic">No hay tarjetas asociadas.</span>`;
                    return;
                }
                cards.forEach(c => {
                    list.innerHTML += `<div class="p-2.5 bg-slate-900 border border-slate-800 rounded-xl flex justify-between items-center text-xs"><span>💳 <strong>${c.card_alias}</strong> (${c.card_brand} •••• ${c.card_last4})</span><span class="text-emerald-400 font-bold">Vinculada</span></div>`;
                });
            }

            // Ejecución de Pago Automático (Point Tap / QR)
            document.getElementById('paymentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('payEmail').value;
                const merchantId = document.getElementById('payMerchantSelect').value;
                const amount = document.getElementById('payAmount').value;
                const method = document.getElementById('selectedMethod').value;
                const resDiv = document.getElementById('paymentResult');

                const response = await fetch(`/process-payment/?user_email=${encodeURIComponent(email)}&merchant_id=${merchantId}&total_amount=${amount}&method=${method}`, { method: 'POST' });
                const data = await response.json();
                resDiv.classList.remove('hidden');
                if(data.error) {
                    resDiv.innerHTML = `<div class="p-3 bg-amber-950/40 text-xs text-amber-200 rounded-xl">⚠️ ${data.error}</div>`;
                } else {
                    resDiv.innerHTML = `
                        <div class="p-4 bg-emerald-950/40 border border-emerald-500/40 space-y-2 text-xs rounded-xl">
                            <span class="font-bold text-emerald-400 text-sm block">✅ ¡Pago Exitoso con Descuento Universal! (${data.discount_applied})</span>
                            <div class="text-slate-300">Modo de cobro: <strong class="text-white uppercase">${data.payment_method}</strong></div>
                            <div class="flex justify-between text-slate-300"><span>Monto Original: $${data.original_amount}</span><span class="text-emerald-400 font-bold">Ahorro: -$${data.amount_saved}</span></div>
                            <div class="text-sm font-extrabold text-white pt-1 border-t border-emerald-500/30">Total debitado automáticamente: $${data.final_amount_to_pay}</div>
                        </div>`;
                }
            });

            fetchMerchants();
            loadExternalFeeds();
        </script>
    </body>
    </html>
    """

# --- Endpoints del Backend ---

@app.get("/api/merchants/")
def get_merchants():
    db = SessionLocal()
    try:
        merchants = db.query(MerchantDB).all()
        if not merchants:
            return [
                {"id": 1, "name": "TechStore Argentina", "category": "Tecnología", "image_url": "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80", "percentage": 25, "title": "25% OFF con cualquier tarjeta asociada"},
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
    db = SessionLocal()
    try:
        db.query(ExternalFeedDB).delete()
        db.commit()

        sample_feeds = [
            ExternalFeedDB(source_name="PromoAgenda AR", title="HotSale 2026: Descuentos universales acumulables", summary="Las rebajas se aplican automáticamente al pagar con cualquier tarjeta vinculada a la app.", category="Tecnología", url="https://promoagenda.com.ar/promo-agenda"),
            ExternalFeedDB(source_name="Reddit Descuentos", title="[Megathread] Top Promos con Point Tap y QR este fin de semana", summary="Usuarios reportan ahorro inmediato sin importar la entidad bancaria emisora.", category="Supermercados", url="https://www.reddit.com/r/DescuentosArgentina/"),
            ExternalFeedDB(source_name="iProfesional RSS", title="Consumo inteligente: El auge de los pagos por proximidad", summary="Cómo la tecnología sin contacto optimiza el ahorro mensual de los hogares.", category="Economía", url="https://www.iprofesional.com/rss")
        ]
        for feed in sample_feeds:
            db.add(feed)
        db.commit()
        return {"status": "success"}
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
            return {"message": "Usuario registrado", "email": existing.email}
        new_u = UserDB(email=email, subscription_status="active")
        db.add(new_u)
        db.commit()
        return {"message": "Usuario creado con éxito", "email": new_u.email}
    finally:
        db.close()

@app.post("/api/add-card/")
def add_card(data: dict):
    db = SessionLocal()
    try:
        new_card = UserCardDB(
            user_email=data.get("user_email"),
            card_alias=data.get("card_alias"),
            card_last4=data.get("card_last4"),
            card_brand=data.get("card_brand")
        )
        db.add(new_card)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.get("/api/user-cards/")
def get_user_cards(email: str):
    db = SessionLocal()
    try:
        cards = db.query(UserCardDB).filter(UserCardDB.user_email == email).all()
        return [{"card_alias": c.card_alias, "card_last4": c.card_last4, "card_brand": c.card_brand} for c in cards]
    finally:
        db.close()

@app.post("/process-payment/")
def process_payment(user_email: str, merchant_id: int, total_amount: float, method: str):
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.email == user_email).first()
        if not user or user.subscription_status != "active":
            return {"error": "Debes activar tu membresía de socio primero."}
        
        cards = db.query(UserCardDB).filter(UserCardDB.user_email == user_email).all()
        if not cards:
            return {"error": "Debes asociar al menos una tarjeta en tu billetera para cobrar con descuento universal."}

        discount = db.query(DiscountDB).filter(DiscountDB.merchant_id == merchant_id).first()
        percentage = float(discount.percentage) if discount else 20.0
        
        saved = (total_amount * percentage) / 100
        final = total_amount - saved

        method_desc = "Point Tap (Proximidad NFC)" if method == 'tap' else "Escaneo de Cámara QR"

        return {
            "message": "¡Descuento universal aplicado de forma automática!",
            "payment_method": method_desc,
            "original_amount": total_amount,
            "discount_applied": f"{percentage}% OFF",
            "amount_saved": round(saved, 2),
            "final_amount_to_pay": round(final, 2)
        }
    finally:
        db.close()
