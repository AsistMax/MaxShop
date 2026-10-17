from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

try:
    from tracking.router import router as tracking_router
    HAS_TRACKING = True
except:
    HAS_TRACKING = False

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="templates")

def render(name, request):
    tmpl = templates.get_template(name)
    return HTMLResponse(tmpl.render({"request": request}))

@app.get("/health")
def health():
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    return {"status":"OK","supabase":bool(os.getenv("SUPABASE_URL") and key)}

@app.get("/")
def root():
    return RedirectResponse(url="/app")

@app.get("/app", response_class=HTMLResponse)
async def app_view(request: Request):
    return render("index.html", request)

@app.get("/mapa-calles-real", response_class=HTMLResponse)
async def mapa(request: Request):
    return render("mapa-calles-real.html", request)

@app.get("/cadete", response_class=HTMLResponse)
async def cadete(request: Request):
    return render("cadete.html", request)

@app.get("/qr/{qr_id}", response_class=HTMLResponse)
async def qr(request: Request, qr_id: str):
    return render("index.html", request)

if HAS_TRACKING:
    app.include_router(tracking_router)
