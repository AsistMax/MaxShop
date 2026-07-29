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
    description="Sistema Automatizado de Geolocalización, Match de Tarjetas y Captación B2B",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS ---
class UserProfileUpdate(BaseModel):
    email: EmailStr
    preferred_cards: List[str]

class StoreCreate(BaseModel):
    name: str
    category: str
    address: str
    latitude: float
    longitude: float

class OfferCreate(BaseModel):
    store_id: int
    title: str
    description: str
    discount_percentage: int
    required_card: Optional[str] = "General"

class GeolocationTrigger(BaseModel):
    city: str = "Catamarca"


# --- INTERFAZ VISUAL PRINCIPAL (HOME CON DISEÑO Y ESTILOS) ---
@app.get("/", response_class=HTMLResponse)
async def home_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaxShop - Radar de Beneficios y Ofertas</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white min-h-screen font-sans">
        <!-- Header / Navbar -->
        <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xl border border-emerald-500/30">M</div>
                    <span class="text-xl font-extrabold tracking-tight text-white">Max<span class="text-emerald-400">Shop</span></span>
                </div>
                <div class="flex space-x-3">
                    <a href="/docs" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-lg border border-slate-700 transition">Documentación API</a>
                </div>
            </div>
        </header>

        <!-- Hero Section -->
        <main class="max-w-6xl mx-auto px-4 py-12">
            <div class="text-center max-w-2xl mx-auto mb-12">
                <span class="bg-emerald-500/10 text-emerald-400 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider border border-emerald-500/20">Comunidad Inteligente Local</span>
                <h1 class="text-4xl md:text-5xl font-extrabold mt-4 mb-4 tracking-tight">Descubre ofertas cerca de ti conectadas a tus tarjetas</h1>
                <p class="text-slate-400 text-base">El radar automático que detecta comercios, unifica descuentos y optimiza tus compras al instante.</p>
            </div>

            <!-- Panel de Acciones / Tarjetas Interactivas -->
            <div class="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                <!-- Card 1: Simular Buscador de Ofertas -->
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h3 class="text-lg font-bold mb-2 flex items-center text-emerald-400">
                        <span class="mr-2">⚡</span> Radar de Beneficios
                    </h3>
                    <p class="text-sm text-slate-400 mb-4">Ingresa tu correo para consultar las ofertas activas hechas a tu medida según tus medios de pago.</p>
                    <form action="/api/offers/matched" method="GET" class="space-y-3" onsubmit="event.preventDefault(); alert('Usa la ruta /api/offers/matched?email=tu@correo.com o la documentación en /docs');">
                        <input type="email" placeholder="tucorreo@email.com" class="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:outline-none focus:border-emerald-500 text-white">
                        <button type="submit" class="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl transition shadow-lg shadow-emerald-500/10 text-sm">
                            Ver mis Ofertas Activas
                        </button>
                    </form>
                </div>

                <!-- Card 2: Geolocalización Autónoma B2B -->
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h3 class="text-lg font-bold mb-2 flex items-center text-indigo-400">
                        <span class="mr-2">📍</span> Captación B2B Automática
                    </h3>
                    <p class="text-sm text-slate-400 mb-4">Ejecuta el escaneo inteligente de comercios locales para incorporarlos al mapa y enviar invitaciones.</p>
                    <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
                        <p class="text-xs text-slate-400 mb-3">Motor activo para Catamarca y región.</p>
                        <a href="/docs" class="inline-block w-full py-3 bg-slate-800 hover:bg-slate-700 text-indigo-300 font-semibold rounded-xl border border-indigo-500/30 text-sm transition">
                            Gestionar desde el Panel API
                        </a>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="border-t border-slate-900 mt-20 py-8 text-center text-xs text-slate-600">
            MaxShop Engine &copy; 2026 - Todos los derechos reservados.
        </footer>
    </body>
    </html>
    """


# --- MÓDULO DE CAPTACIÓN MASIVA (SMART REFERRAL LINKS) ---
@app.get("/promo", response_class=HTMLResponse)
async def smart_promo_landing(
    request: Request,
    offer_id: int = Query(..., description="ID de la oferta promocionada"),
    source: Optional[str] = Query("direct", description="Canal de origen")
):
    client_ip = request.client.host
    try:
        supabase.table("referral_clicks").insert({
            "offer_id": offer_id,
            "source_channel": source,
            "ip_address": client_ip
        }).execute()
    except Exception as e:
        print(f"Error registrando clic: {e}")

    offer_res = supabase.table("offers").select("*, stores(name, address)").eq("id", offer_id).execute()
    
    if not offer_res.data:
        return "<body style='background:#020617; color:white; font-family:sans-serif; text-align:center; padding-top:50px;'><h1>Oferta no encontrada</h1></body>"
    
    offer = offer_res.data[0]
    store_name = offer["stores"]["name"] if offer.get("stores") else "Comercio Aliado"

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{offer['title']} - Beneficio Exclusivo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white min-h-screen flex items-center justify-center p-4">
        <div class="max-w-md w-full bg-slate-900 rounded-2xl shadow-2xl p-6 border border-slate-800">
            <span class="bg-emerald-500/15 text-emerald-400 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">¡Oferta Flash Verificada!</span>
            <h1 class="text-2xl font-bold mt-4 mb-2">{offer['title']}</h1>
            <p class="text-slate-400 text-sm mb-4">📍 <strong>{store_name}</strong></p>
            <div class="bg-slate-950 rounded-xl p-4 mb-6 border border-slate-800">
                <p class="text-emerald-400 font-bold text-lg mb-1">{offer['discount_percentage']}% de Descuento</p>
                <p class="text-slate-300 text-sm">{offer['description']}</p>
                <p class="text-xs text-amber-400 mt-2">⚡ Condición: Requiere medio de pago ({offer['required_card']})</p>
            </div>
            
            <div class="bg-indigo-950/40 border border-indigo-500/30 rounded-xl p-4 text-center">
                <h3 class="font-semibold text-indigo-300 mb-1">Desbloquea este beneficio</h3>
                <form action="/api/register-lead" method="POST" class="space-y-3 mt-3">
                    <input type="hidden" name="offer_id" value="{offer_id}">
                    <input type="email" name="email" required placeholder="Tu correo electrónico" class="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 text-sm">
                    <button type="submit" class="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl transition duration-200 shadow-lg text-sm">
                        Quiero mi Descuento Gratis
                    </button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/api/register-lead")
async def register_lead(request: Request):
    form_data = await request.form()
    email = form_data.get("email")
    offer_id = form_data.get("offer_id")

    if not email:
        raise HTTPException(status_code=400, detail="El correo es obligatorio")

    try:
        supabase.table("profiles").upsert({
            "email": email,
            "preferred_cards": ["General"]
        }, on_conflict="email").execute()
    except Exception as e:
        print(f"Error guardando lead: {e}")

    return RedirectResponse(url=f"/promo/success?offer_id={offer_id}", status_code=303)

@app.get("/promo/success", response_class=HTMLResponse)
async def promo_success(offer_id: int):
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-white min-h-screen flex items-center justify-center p-4">
        <div class="max-w-md w-full bg-slate-900 rounded-2xl p-8 text-center border border-slate-800">
            <div class="w-16 h-16 bg-emerald-500/15 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">✓</div>
            <h2 class="text-2xl font-bold mb-2">¡Registro Exitoso!</h2>
            <p class="text-slate-400 text-sm mb-6">Tu beneficio ha sido activado en tu cuenta.</p>
            <a href="/" class="inline-block w-full py-3 bg-emerald-500 text-slate-950 font-bold rounded-xl text-sm">Volver al Inicio</a>
        </div>
    </body>
    </html>
    """


# --- MÓDULO DE MATCH INTELIGENTE ---
@app.get("/api/offers/matched")
async def get_matched_offers(email: str):
    user_res = supabase.table("profiles").select("preferred_cards").eq("email", email).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_cards = user_res.data[0].get("preferred_cards", [])
    user_cards.append("General")

    offers_res = supabase.table("offers").select("*, stores(name, address, latitude, longitude)").execute()
    all_offers = offers_res.data or []

    matched_offers = []
    for offer in all_offers:
        req_card = offer.get("required_card", "General")
        offer["matched_for_user"] = True if (req_card in user_cards or req_card == "General") else False
        matched_offers.append(offer)

    return {"user_cards": user_cards, "total_offers": len(matched_offers), "offers": matched_offers}


# --- MÓDULO DE GEOLOCALIZACIÓN AUTOMÁTICA ---
@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger, background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_osm_pipeline, payload.city)
    return {"status": "success", "message": f"Pipeline autónomo iniciado para: {payload.city}"}

def execute_osm_pipeline(ciudad: str):
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    area[name="{ciudad}"]->.searchArea;
    (
      node["shop"](area.searchArea);
      node["amenity"="restaurant"](area.searchArea);
      node["amenity"="fuel"](area.searchArea);
    );
    out body;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query}, timeout=30)
        data = response.json()
        for elem in data.get("elements", []):
            tags = elem.get("tags", {})
            name = tags.get("name")
            if not name: continue
            
            comercio_data = {
                "name": name,
                "category": tags.get("shop", tags.get("amenity", "comercio")),
                "address": f"{ciudad}, Argentina",
                "latitude": elem.get("lat"),
                "longitude": elem.get("lon")
            }
            try:
                supabase.table("stores").insert(comercio_data).execute()
            except Exception:
                pass
    except Exception as e:
        print(f"Error en pipeline: {e}")
