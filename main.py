import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NODO Argentina")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Si existe la carpeta static, la monta, si no, no crashea
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health():
    return {"status":"ok","service":"nodo-api"}

@app.get("/")
def home():
    return FileResponse("templates/index.html")

@app.get("/api/tareas")
def tareas(region: str = "Buenos Aires", lat: float = -34.6118, lng: float = -58.3960):
    detected = region
    if -35.2 < lat < -34.3 and -58.7 < lng < -58.2:
        detected = "Buenos Aires"
    elif -29 < lat < -27 and -66.5 < lng < -65:
        detected = "Catamarca"
    if detected == "Catamarca":
        return {"tareas":[
            {"id":"1","title":"Sacar foto local","tag":"FOTO","loc":"Catamarca","lat":-28.46957,"lng":-65.78524,"price":"$1.500"},
            {"id":"2","title":"Llevar paquete","tag":"ENVIO","loc":"Catamarca","lat":-28.471,"lng":-65.79,"price":"$2.000"}
        ], "region_detectada": detected}
    else:
        return {"tareas":[
            {"id":"3","title":"Electricista","tag":"OFICIO","loc":f"{detected}","lat":lat,"lng":lng,"price":"A convenir"}
        ], "region_detectada": detected}
