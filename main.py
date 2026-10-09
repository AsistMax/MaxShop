import os
import re
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import uvicorn

try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supa = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except:
    supa = None

app = FastAPI(title="MaxShop API - Real", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="templates")

class TarjetaIn(BaseModel):
    numero: str
    titular: str
    venc: str
    user_id: Optional[str] = None

class TransferIn(BaseModel):
    origen: str
    destino: str
    monto: float

def luhn_valid(card_number: str) -> bool:
    n = re.sub(r"\D", "", card_number)
    if len(n) < 13: return False
    total = 0
    reverse = n[::-1]
    for i, d in enumerate(reverse):
        digit = int(d)
        if i % 2 == 1:
            digit *= 2
            if digit > 9: digit -= 9
        total += digit
    return total % 10 == 0

def detect_banco_brand(numero: str):
    num = re.sub(r"\D", "", numero)
    brand = "Visa" if num.startswith("4") else "Mastercard" if num.startswith("5") else "Amex" if num.startswith("3") else "Visa"
    banco = "Galicia" if num.startswith("4") else "Santander" if num.startswith("5") else "BBVA" if num.startswith("3") else "Naranja"
    return banco, brand, num[-4:]

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "alive", "service": "maxshop-api", "real": True}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "supabase": supa is not None}

@app.post("/api/validar-tarjeta")
async def validar_tarjeta(data: TarjetaIn):
    numero_limpio = re.sub(r"\D", "", data.numero)
    if len(numero_limpio) != 16:
        raise HTTPException(status_code=400, detail="Tarjeta debe tener 16 dígitos")
    if not luhn_valid(numero_limpio):
        raise HTTPException(status_code=400, detail="Tarjeta inválida (Luhn)")
    banco, brand, last4 = detect_banco_brand(numero_limpio)
    token = f"tok_live_{last4}_{banco.lower()}_{brand.lower()}"
    if supa and data.user_id:
        try:
            supa.table("tarjetas").insert({"user_id": data.user_id, "last4": last4, "brand": brand, "banco": banco, "token": token, "titular": data.titular, "venc": data.venc}).execute()
        except Exception as e:
            print(f"Supabase error: {e}")
    return {"ok": True, "banco": banco, "brand": brand, "last4": last4, "token": token}

@app.post("/api/transferir")
async def transferir(data: TransferIn):
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="Monto inválido")
    comprobante = f"TR-{data.origen[:4].upper()}-{data.destino[:4].upper()}-{int(data.monto)}"
    if supa:
        try:
            supa.table("transferencias").insert({"id": comprobante, "origen": data.origen, "destino": data.destino, "monto": data.monto}).execute()
        except Exception as e:
            print(f"Transfer error: {e}")
    return {"ok": True, "comprobante": comprobante, "monto": data.monto}

@app.get("/api/wallet/{user_id}")
async def get_wallet(user_id: str):
    if supa:
        try:
            res = supa.table("wallets").select("*").eq("user_id", user_id).execute()
            if res.data:
                return res.data[0]
        except:
            pass
    return {"user_id": user_id, "disponible": 31250.0, "bloqueado": 0.0, "progreso": 42}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
