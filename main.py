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

# Inicialización de Supabase (Credenciales desde variables de entorno seguras)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-supabase-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Club de Beneficios Inteligente - API Completa",
    description="Backend de Captación Masiva, Match de Tarjetas, Radar y Geolocalización Autónoma a Costo Cero",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS PYDANTIC ---
class UserProfileUpdate(BaseModel):
    email: EmailStr
    preferred_cards: List[str] # Ej: ["Visa Galicia", "MODO"]

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


# --- 1. MÓDULO DE CAPTACIÓN MASIVA (SMART REFERRAL LINKS) ---
@app.get("/promo", response_class=HTMLResponse)
async def smart_promo_landing(
    request: Request,
    offer_id: int = Query(..., description="ID de la oferta promocionada"),
    source: Optional[str] = Query("direct", description="Canal de origen (telegram, redes, etc)")
):
    """
    Landing Page Dinámica para Captación Masiva (Costo Cero):
    Registra el clic, capta el interés y muestra el gancho para registrarse gratis en la app.
    """
    client_ip = request.client.host
    
    try:
        supabase.table("referral_clicks").insert({
            "offer_id": offer_id,
            "source_channel": source,
            "ip_address": client_ip
        }).execute()
    except Exception as e:
        print(f"Error registrando analítica de clic: {e}")

    offer_res = supabase.table("offers").select("*, stores(name, address)").eq("id", offer_id).execute()
    
    if not offer_res.data:
        return "<h1>Oferta no encontrada o expirada</h1><p>Visita nuestra app principal para ver más beneficios.</p>"
    
    offer = offer_res.data[0]
    store_name = offer["stores"]["name"] if offer.get("stores") else "Comercio Aliado"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{offer['title']} - Beneficio Exclusivo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-white min-h-screen flex items-center justify-center p-4">
        <div class="max-w-md w-full bg-slate-800 rounded-2xl shadow-2xl p-6 border border-slate-700">
            <span class="bg-emerald-500/15 text-emerald-400 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">¡Oferta Flash Verificada!</span>
            <h1 class="text-2xl font-bold mt-4 mb-2">{offer['title']}</h1>
            <p class="text-slate-400 text-sm mb-4">📍 <strong>{store_name}</strong></p>
            <div class="bg-slate-700/50 rounded-xl p-4 mb-6 border border-slate-600">
                <p class="text-emerald-400 font-bold text-lg mb-1">{offer['discount_percentage']}% de Descuento</p>
                <p class="text-slate-300 text-sm">{offer['description']}</p>
                <p class="text-xs text-amber-400 mt-2">⚡ Condición: Requiere medio de pago ({offer['required_card']})</p>
            </div>
            
            <div class="bg-indigo-900/40 border border-indigo-500/30 rounded-xl p-4 text-center">
                <h3 class="font-semibold text-indigo-300 mb-1">Desbloquea este beneficio al instante</h3>
                <p class="text-xs text-slate-300 mb-4">Regístrate gratis en 10 segundos para acceder a este y más de 100 descuentos activos en tu zona.</p>
                <form action="/api/register-lead" method="POST" class="space-y-3">
                    <input type="hidden" name="offer_id" value="{offer_id}">
                    <input type="email" name="email" required placeholder="Ingresa tu correo electrónico" class="w-full px-4 py-3 bg-slate-900 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 text-sm">
                    <button type="submit" class="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl transition duration-200 shadow-lg shadow-emerald-500/20">
                        Quiero mi Descuento Gratis
                    </button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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
    <body class="bg-slate-900 text-white min-h-screen flex items-center justify-center p-4">
        <div class="max-w-md w-full bg-slate-800 rounded-2xl p-8 text-center border border-slate-700">
            <div class="w-16 h-16 bg-emerald-500/15 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">✓</div>
            <h2 class="text-2xl font-bold mb-2">¡Registro Exitoso!</h2>
            <p class="text-slate-400 text-sm mb-6">Ya formas parte de nuestra comunidad. Tu beneficio ha sido activado en tu cuenta.</p>
            <a href="/" class="inline-block w-full py-3 bg-emerald-500 text-slate-950 font-bold rounded-xl">Ir a mi Billetera de Beneficios</a>
        </div>
    </body>
    </html>
    """


# --- 2. MÓDULO DE MATCH INTELIGENTE DE TARJETAS Y OFERTAS ---
@app.post("/api/user/preferences")
async def update_user_cards(data: UserProfileUpdate):
    try:
        supabase.table("profiles").update({
            "preferred_cards": data.preferred_cards
        }).eq("email", data.email).execute()
        return {"status": "success", "message": "Tarjetas actualizadas correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        if req_card in user_cards or req_card == "General":
            offer["matched_for_user"] = True
        else:
            offer["matched_for_user"] = False
        matched_offers.append(offer)

    return {
        "user_cards": user_cards,
        "total_offers": len(matched_offers),
        "offers": matched_offers
    }


# --- 3. MÓDULO DE GEOLOCALIZACIÓN AUTÓNOMA Y CAPTACIÓN B2B ---
@app.post("/api/admin/run-geolocation-pipeline")
async def run_geolocation_pipeline(payload: GeolocationTrigger, background_tasks: BackgroundTasks):
    """
    Ejecuta en segundo plano la búsqueda masiva en OpenStreetMap para geolocalizar
    comercios de la zona (ej. Catamarca), guardarlos automáticamente en Supabase,
    generar archivos CSV de auditoría y preparar la campaña de invitación automática.
    """
    background_tasks.add_task(execute_osm_pipeline, payload.city)
    return {
        "status": "success",
        "message": f"Pipeline autónomo de geolocalización iniciado en segundo plano para: {payload.city}"
    }

def execute_osm_pipeline(ciudad: str):
    print(f"[{datetime.now()}] Iniciando escaneo geolocalizado autónomo para: {ciudad}...")
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
        elements = data.get("elements", [])
        
        print(f"Se encontraron {len(elements)} comercios geolocalizados en {ciudad}.")
        comercios_procesados = []
        
        for elem in elements:
            tags = elem.get("tags", {})
            name = tags.get("name")
            if not name:
                continue
                
            lat = elem.get("lat")
            lon = elem.get("lon")
            shop_type = tags.get("shop", tags.get("amenity", "comercio"))
            email_contacto = tags.get("email", f"contacto@{name.lower().replace(' ', '').replace('\t', '')}.com")
            
            comercio_data = {
                "name": name,
                "category": shop_type,
                "address": f"{ciudad}, Argentina",
                "latitude": lat,
                "longitude": lon
            }
            
            # Guardar automáticamente en Supabase
            try:
                supabase.table("stores").insert(comercio_data).execute()
            except Exception:
                pass

            comercios_procesados.append({
                "Nombre": name,
                "Categoria": shop_type,
                "Latitud": lat,
                "Longitud": lon,
                "Email": email_contacto,
                "Fecha_Deteccion": datetime.now().strftime("%Y-%m-%d")
            })

        # Generar archivo CSV de respaldo automático
        nombre_archivo = f"comercios_detectados_{ciudad.lower()}.csv"
        with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as file:
            fieldnames = ["Nombre", "Categoria", "Latitud", "Longitud", "Email", "Fecha_Deteccion"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in comercios_procesados:
                writer.writerow(row)
                
        print(f"📁 Archivo de respaldo generado con éxito: {nombre_archivo}")
        
    except Exception as e:
        print(f"❌ Error en el pipeline autónomo: {e}")


# --- 4. GESTIÓN MANUAL DE COMERCIOS Y OFERTAS ---
@app.post("/api/stores", status_code=201)
async def create_store(store: StoreCreate):
    res = supabase.table("stores").insert(store.dict()).execute()
    return {"status": "success", "data": res.data}

@app.post("/api/offers", status_code=201)
async def create_offer(offer: OfferCreate):
    res = supabase.table("offers").insert(offer.dict()).execute()
    return {"status": "success", "data": res.data}
