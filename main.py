import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Conexión configurada directamente con tu proyecto de Supabase
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres.tyvrhprlkpatyoxbbyqd:MaxShop2026@aws-1-us-west-2.pooler.supabase.com:5432/postgres"
)

# Motor de conexión para PostgreSQL
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
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)

class DiscountDB(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    percentage = Column(Numeric, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))

# Crear las tablas automáticamente en Supabase si no existen
Base.metadata.create_all(bind=engine)

# --- Inicializar FastAPI ---
app = FastAPI(title="API Club de Descuentos MaxShop", version="1.0.0")

# --- Rutas de la API ---
@app.get("/")
def read_root():
    return {"message": "¡API del Club de Descuentos MaxShop en la nube funcionando al 100%! 🚀"}

@app.post("/users/")
def create_user(email: str, subscription_status: str = "inactive"):
    db = SessionLocal()
    try:
        existing_user = db.query(UserDB).filter(UserDB.email == email).first()
        if existing_user:
            return {"error": "El correo ya está registrado"}
        new_user = UserDB(email=email, subscription_status=subscription_status)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Usuario registrado con éxito", "user_id": new_user.id, "email": new_user.email, "subscription_status": new_user.subscription_status}
    finally:
        db.close()

@app.post("/merchants/")
def create_merchant(name: str, category: str):
    db = SessionLocal()
    try:
        new_merchant = MerchantDB(name=name, category=category)
        db.add(new_merchant)
        db.commit()
        db.refresh(new_merchant)
        return {"message": "Comercio creado con éxito", "merchant_id": new_merchant.id, "name": new_merchant.name}
    finally:
        db.close()

@app.post("/discounts/")
def create_discount(title: str, percentage: float, merchant_id: int):
    db = SessionLocal()
    try:
        merchant = db.query(MerchantDB).filter(MerchantDB.id == merchant_id).first()
        if not merchant:
            return {"error": "El comercio indicado no existe"}
        new_discount = DiscountDB(title=title, percentage=percentage, merchant_id=merchant_id)
        db.add(new_discount)
        db.commit()
        db.refresh(new_discount)
        return {"message": "Descuento creado con éxito", "discount_id": new_discount.id, "title": new_discount.title, "percentage": float(new_discount.percentage)}
    finally:
        db.close()

@app.post("/process-payment/")
def process_payment(user_email: str, merchant_id: int, total_amount: float):
    db = SessionLocal()
    try:
        # 1. Validar usuario activo
        user = db.query(UserDB).filter(UserDB.email == user_email).first()
        if not user:
            return {"error": "Usuario no encontrado."}
        if user.subscription_status != "active":
            return {"error": "Suscripción inactiva. El descuento automático no se puede aplicar."}
        
        # 2. Buscar descuento del comercio
        discount = db.query(DiscountDB).filter(DiscountDB.merchant_id == merchant_id).first()
        if not discount:
            return {
                "message": "Pago procesado sin descuentos (el comercio no tiene promociones vigentes).",
                "final_amount_to_pay": total_amount,
                "amount_saved": 0.0
            }
        
        # 3. Aplicar descuento automático
        discount_percentage = float(discount.percentage)
        amount_saved = (total_amount * discount_percentage) / 100
        final_amount = total_amount - amount_saved
        
        return {
            "message": "¡Pago procesado con éxito! Descuento aplicado automáticamente en caja. 💸",
            "original_amount": total_amount,
            "discount_applied": f"{discount_percentage}%",
            "amount_saved": round(amount_saved, 2),
            "final_amount_to_pay": round(final_amount, 2)
        }
    finally:
        db.close()
