from fastapi import FastAPI, Depends, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import requests
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="MaxShop - Descuentos de Locos",
    description="Plataforma de Beneficios Inteligentes de Alto Impacto",
    version="6.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeolocationTrigger(BaseModel):
    city: str = "Catamarca"

# ==========================================
# 1. LANDING PAGE CLIENTES (ALTO IMPACTO VISUAL)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def client_landing():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop - Descuentos de Locos</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .neon-gradient-glow {
                box-shadow: 0 0 35px rgba(16, 185, 129, 0.25), inset 0 0 15px rgba(249, 115, 22, 0.15);
            }
            .neon-text-gradient {
                background: linear-gradient(135deg, #10b981 0%, #3b82f6 50%, #f97316 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .neon-border-glow {
                border: 1px solid rgba(16, 185, 129, 0.4);
                box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
            }
            @keyframes scroll {
                0% { transform: translateX(0); }
                100% { transform: translateX(-50%); }
            }
            .animate-infinite-scroll {
                display: flex;
                width: max-content;
                animation: scroll 25s linear infinite;
            }
            .animate-infinite-scroll:hover {
                animation-play-state: paused;
            }
        </style>
    </head>
    <body class="bg-[#050B14] text-white min-h-screen font-sans selection:bg-emerald-500 selection:text-black overflow-x-hidden">

        <!-- HEADER / NAVBAR -->
        <header class="border-b border-emerald-500/20 bg-[#050B14]/80 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-blue-600 flex items-center justify-center font-black text-xl shadow-lg shadow-emerald-500/30 text-slate-950">M%</div>
                    <span class="text-2xl font-black tracking-wider text-white">Max<span class="text-emerald-400">%</span>Shop</span>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="hidden md:inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        <span class="w-2 h-2 mr-2 bg-emerald-400 rounded-full animate-pulse"></span> Descuentos Verificados
                    </span>
                    <a href="#radar" class="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold px-5 py-2.5 rounded-xl text-sm transition shadow-lg shadow-emerald-500/20">
                        Activar Mis Beneficios
                    </a>
                </div>
            </div>
        </header>

        <!-- CARRUSEL INFINITO DE MARCAS REALES -->
        <div class="bg-slate-900/60 border-y border-emerald-500/20 py-4 overflow-hidden relative shadow-inner">
            <div class="absolute left-0 inset-y-0 w-24 bg-gradient-to-r from-[#050B14] to-transparent z-10 pointer-events-none"></div>
            <div class="absolute right-0 inset-y-0 w-24 bg-gradient-to-l from-[#050B14] to-transparent z-10 pointer-events-none"></div>
            
            <div class="animate-infinite-scroll space-x-12 px-6 items-center">
                <!-- Bloque de marcas reales (Repetido para efecto infinito fluido) -->
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-blue-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">FRÁVEGA</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">JUMBO</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-amber-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">MCDONALD'S</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-red-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">BANCO GALICIA</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-cyan-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">VISA REWARDS</span>
                </div>
                <!-- Duplicado exacto para loop continuo -->
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-blue-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">FRÁVEGA</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">JUMBO</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-amber-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">MCDONALD'S</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-red-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">BANCO GALICIA</span>
                </div>
                <div class="flex items-center space-x-3 bg-slate-950/80 px-6 py-2.5 rounded-2xl border border-slate-800 shadow-md">
                    <span class="w-3 h-3 rounded-full bg-cyan-500"></span>
                    <span class="font-bold tracking-wide text-slate-200">VISA REWARDS</span>
                </div>
            </div>
        </div>

        <!-- HERO SECTION (IMPACTO VISUAL) -->
        <main class="max-w-6xl mx-auto px-6 py-20 space-y-24">
            <div class="text-center space-y-6 max-w-3xl mx-auto">
                <span class="bg-gradient-to-r from-emerald-500/10 to-blue-500/10 text-emerald-400 text-xs font-bold px-4 py-1.5 rounded-full uppercase tracking-widest border border-emerald-500/20">
                    Descuentos de Locos en Tiempo Real
                </span>
                <h1 class="text-5xl md:text-7xl font-black tracking-tight text-white leading-tight">
                    El poder de ahorrar <span class="neon-text-gradient">sin límites</span>
                </h1>
                <p class="text-slate-400 text-lg md:text-xl font-normal leading-relaxed">
                    Conecta tus tarjetas y descubre de forma automática las mejores promociones exclusivas en tus marcas y tiendas favoritas.
                </p>
            </div>

            <!-- SECCIÓN INTERACTIVA DE RADAR -->
            <div id="radar" class="max-w-2xl mx-auto bg-slate-900/90 border neon-border-glow rounded-3xl p-8 md:p-10 backdrop-blur-xl shadow-2xl relative">
                <div class="absolute -top-3 right-8 bg-emerald-500 text-slate-950 font-black text-xs px-3 py-1 rounded-full uppercase tracking-wider">
                    Match Automático
                </div>
                
                <h3 class="text-2xl font-black mb-2 text-white flex items-center">
                    <span class="text-emerald-400 mr-3 text-3xl">⚡</span> Encuentra tus Beneficios
                </h3>
                <p class="text-slate-400 text-sm mb-8">Ingresa tu correo electrónico para vincular tus tarjetas y ver al instante las ofertas activas cerca de ti.</p>
                
                <form onsubmit="alert('¡Búsqueda procesada con éxito! Revisa tu correo para ver tus ofertas sincronizadas.'); event.preventDefault();" class="space-y-5">
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Correo Electrónico</label>
                        <input type="email" required placeholder="tucorreo@ejemplo.com" class="w-full px-5 py-4 bg-[#030712] border border-slate-800 rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 transition text-base">
                    </div>
                    <button type="submit" class="w-full py-4 bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-400 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black rounded-2xl transition shadow-xl shadow-emerald-500/20 text-base uppercase tracking-wider">
                        Consultar Mis Descuentos
                    </button>
                </form>
            </div>

            <!-- BLOQUES DE VALOR / SCROLL INFERIOR -->
            <div class="grid md:grid-cols-3 gap-6 pt-10">
                <div class="bg-slate-900/40 border border-slate-800/80 p-8 rounded-3xl backdrop-blur transition hover:border-emerald-500/40">
                    <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-xl mb-6 border border-emerald-500/20">💎</div>
                    <h4 class="text-white font-bold text-lg mb-2">Marcas Líderes</h4>
                    <p class="text-slate-400 text-sm leading-relaxed">Acceso preferencial a convenios con los comercios más importantes del país y la región.</p>
                </div>
                <div class="bg-slate-900/40 border border-slate-800/80 p-8 rounded-3xl backdrop-blur transition hover:border-blue-500/40">
                    <div class="w-12 h-12 rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-xl mb-6 border border-blue-500/20">🛡️</div>
                    <h4 class="text-white font-bold text-lg mb-2">Cero Fricción</h4>
                    <p class="text-slate-400 text-sm leading-relaxed">Sin cupones impresos ni validaciones molestas. El sistema detecta tu medio de pago automáticamente.</p>
                </div>
                <div class="bg-slate-900/40 border border-slate-800/80 p-8 rounded-3xl backdrop-blur transition hover:border-amber-500/40">
                    <div class="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold text-xl mb-6 border border-amber-500/20">🚀</div>
                    <h4 class="text-white font-bold text-lg mb-2">Radar en Tiempo Real</h4>
                    <p class="text-slate-400 text-sm leading-relaxed">Geolocalización permanente para que nunca te pierdas una oferta activa al caminar por la ciudad.</p>
                </div>
            </div>
        </main>

        <!-- FOOTER -->
        <footer class="border-t border-slate-900 mt-32 py-12 text-center text-xs text-slate-500 space-y-3">
            <p class="font-bold text-slate-400">MaxShop &copy; 2026 - Todos los derechos reservados.</p>
            <p>Innovación tecnológica y beneficios inteligentes de alto nivel.</p>
        </footer>
    </body>
    </html>
    """

# ==========================================
# 2. PANEL ADMINISTRATIVO (OCULTO AL CLIENTE)
# ==========================================
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>MaxShop - Panel de Administración</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white p-8 font-sans">
        <div class="max-w-4xl mx-auto space-y-6">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                <h1 class="text-2xl font-bold text-emerald-400">Panel Interno de Administración</h1>
                <a href="/" class="text-xs bg-slate-800 px-4 py-2 rounded-xl text-slate-300">Ir al Sitio Web Principal</a>
            </div>
            <p class="text-slate-400 text-sm">Este panel es de uso estrictamente interno para la gestión de bases de datos, APIs y disparadores de geolocalización.</p>
            
            <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
                <h3 class="font-bold text-lg">Ejecutar Pipeline de Geolocalización (OSM)</h3>
                <form action="/api/admin/run-geolocation-pipeline" method="POST">
                    <button type="submit" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 font-bold rounded-xl text-sm transition">
                        Iniciar Escaneo Catamarca
                    </button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# --- RUTAS DE API INTERNAS ---
@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger = GeolocationTrigger(), background_tasks: BackgroundTasks = None):
    return {"status": "success", "message": f"Pipeline autónomo iniciado para {payload.city}"}

@app.get("/promo", response_class=HTMLResponse)
async def smart_promo_landing(offer_id: int = Query(...)):
    return f"<h1>Landing de Oferta Flash #{offer_id}</h1>"
