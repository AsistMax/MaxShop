from fastapi import FastAPI, Depends, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import requests
import csv
from datetime import datetime
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="MaxShop - Club de Beneficios Inteligente",
    description="Sistema Visual Neón con Radar y Captación Automática",
    version="5.0.0"
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

# --- INTERFAZ VISUAL COMPLETA CON ESTÉTICA NEÓN Y CARRUSEL ---
@app.get("/", response_class=HTMLResponse)
async def neon_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop - Radar Neón de Beneficios</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .neon-glow {
                box-shadow: 0 0 25px rgba(16, 185, 129, 0.4);
            }
            .neon-text {
                text-shadow: 0 0 10px rgba(16, 185, 129, 0.6);
            }
            .neon-border {
                border-color: rgba(16, 185, 129, 0.4);
            }
            @keyframes scroll {
                0% { transform: translateX(0); }
                100% { transform: translateX(-50%); }
            }
            .animate-carousel {
                display: flex;
                width: max-content;
                animation: scroll 20s linear infinite;
            }
            .animate-carousel:hover {
                animation-play-state: paused;
            }
        </style>
    </head>
    <body class="bg-[#030712] text-white min-h-screen font-sans selection:bg-emerald-500 selection:text-black overflow-x-hidden">
        
        <!-- Header Neón -->
        <header class="border-b border-emerald-500/20 bg-[#030712]/80 backdrop-blur sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-extrabold text-xl border neon-border neon-glow">M</div>
                    <span class="text-2xl font-black tracking-wider text-white neon-text">MAX<span class="text-emerald-400">SHOP</span></span>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border neon-border">
                        <span class="w-2 h-2 mr-2 bg-emerald-400 rounded-full animate-ping"></span> Radar Activo
                    </span>
                    <a href="/docs" class="text-xs bg-slate-900 hover:bg-slate-800 text-emerald-400 px-4 py-2 rounded-xl border neon-border transition">API Docs</a>
                </div>
            </div>
        </header>

        <!-- Carrusel Infinito de Marcas y Tiendas Aliadas -->
        <div class="bg-slate-900/50 border-y border-emerald-500/20 py-4 overflow-hidden relative">
            <div class="absolute left-0 inset-y-0 w-20 bg-gradient-to-r from-[#030712] to-transparent z-10 pointer-events-none"></div>
            <div class="absolute right-0 inset-y-0 w-20 bg-gradient-to-l from-[#030712] to-transparent z-10 pointer-events-none"></div>
            <div class="animate-carousel space-x-8 px-4 text-slate-400 font-semibold tracking-wider text-sm uppercase">
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">⚡ Supermercados Mayoristas</span>
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">🔥 Estaciones de Servicio</span>
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">💳 Visa & Galicia Rewards</span>
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">📍 Catamarca Comercial</span>
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">⚡ Supermercados Mayoristas</span>
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">🔥 Estaciones de Servicio</span>
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">💳 Visa & Galicia Rewards</span>
                <span class="flex items-center space-x-2 bg-emerald-500/5 px-4 py-2 rounded-xl border border-emerald-500/10">📍 Catamarca Comercial</span>
            </div>
        </div>

        <!-- Hero / Sección Principal con Desplيزamiento -->
        <main class="max-w-5xl mx-auto px-6 py-16 space-y-20">
            <div class="text-center space-y-6">
                <h1 class="text-5xl md:text-7xl font-black tracking-tight text-white">
                    El Radar de Ofertas <span class="text-emerald-400 neon-text">Inteligente</span>
                </h1>
                <p class="text-slate-400 text-lg max-w-2xl mx-auto">
                    Descubre descuentos en tiempo real vinculados automáticamente a tus tarjetas de crédito y métodos de pago habituales.
                </p>
            </div>

            <!-- Panel de Control / Tarjetas Neón -->
            <div class="grid md:grid-cols-2 gap-8">
                <!-- Tarjeta 1 -->
                <div class="bg-slate-900/80 border neon-border rounded-3xl p-8 neon-glow backdrop-blur transition hover:scale-[1.02]">
                    <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-xl mb-6 border neon-border">⚡</div>
                    <h3 class="text-2xl font-bold mb-3 text-white">Consulta tus Beneficios</h3>
                    <p class="text-slate-400 text-sm mb-6">Ingresa tu correo para hacer match automático con las promociones activas en tu zona.</p>
                    <form onsubmit="alert('Para probar el match de ofertas por correo, utiliza la ruta /api/offers/matched?email=tu@correo.com'); event.preventDefault();" class="space-y-4">
                        <input type="email" placeholder="correo@ejemplo.com" class="w-full px-4 py-4 bg-[#030712] border border-slate-800 rounded-2xl text-white focus:outline-none focus:border-emerald-500 text-sm">
                        <button type="submit" class="w-full py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-2xl transition shadow-lg neon-glow text-sm uppercase tracking-wider">
                            Buscar Mis Ofertas
                        </button>
                    </form>
                </div>

                <!-- Tarjeta 2 -->
                <div class="bg-slate-900/80 border border-indigo-500/30 rounded-3xl p-8 backdrop-blur transition hover:scale-[1.02] shadow-[0_0_25px_rgba(99,102,241,0.15)]">
                    <div class="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-xl mb-6 border border-indigo-500/30">📍</div>
                    <h3 class="text-2xl font-bold mb-3 text-white">Captación B2B Autománea</h3>
                    <p class="text-slate-400 text-sm mb-6">Motor geolocalizado en segundo plano para escaneo masivo de comercios y comercios aliados.</p>
                    <div class="bg-[#030712] border border-indigo-500/20 rounded-2xl p-6 text-center space-y-4">
                        <p class="text-xs text-slate-400 font-medium">Zona configurada: <span class="text-indigo-400 font-bold">Catamarca, Argentina</span></p>
                        <a href="/docs" class="block w-full py-4 bg-slate-900 hover:bg-slate-800 text-indigo-300 font-bold rounded-2xl border border-indigo-500/30 text-sm transition">
                            Gestionar Automatización
                        </a>
                    </div>
                </div>
            </div>

            <!-- Sección de Desplazamiento Infinito / Beneficios Adicionales -->
            <div class="border-t border-slate-900 pt-16 text-center space-y-8">
                <h2 class="text-3xl font-extrabold text-white">Tecnología de Vanguardia Sin Costo</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                    <div class="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl">
                        <div class="text-emerald-400 font-bold text-lg mb-2">01. Geolocalización</div>
                        <p class="text-slate-400 text-sm">Mapeo autónomo mediante mapas abiertos de alta precisión para detección instantánea de locales.</p>
                    </div>
                    <div class="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl">
                        <div class="text-emerald-400 font-bold text-lg mb-2">02. Enlaces Inteligentes</div>
                        <p class="text-slate-400 text-sm">Campañas flash optimizadas con invitación directa mediante links seguros sin pasarelas costosas.</p>
                    </div>
                    <div class="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl">
                        <div class="text-emerald-400 font-bold text-lg mb-2">03. Cero Fricción</div>
                        <p class="text-slate-400 text-sm">Match directo entre las tarjetas del usuario y los descuentos del comercio verificado.</p>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="border-t border-slate-900 mt-24 py-12 text-center text-xs text-slate-500 space-y-2">
            <p>MaxShop Engine &copy; 2026 - Todos los derechos reservados.</p>
            <p class="text-emerald-500/60 font-mono">STATUS: 100% AUTOMATED & SECURE</p>
        </footer>
    </body>
    </html>
    """

# --- RUTAS DE API ---
@app.get("/promo", response_class=HTMLResponse)
async def smart_promo_landing(request: Request, offer_id: int = Query(...)):
    return f"<h1>Landing de Oferta #{offer_id} - Estética Neón</h1>"

@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger, background_tasks: BackgroundTasks):
    return {"status": "success", "message": f"Pipeline iniciado para {payload.city}"}
