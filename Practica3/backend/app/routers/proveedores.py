# Router CRUD de proveedores
# Implementa las 4 operaciones basicas: listar, obtener, crear, actualizar y eliminar (baja logica)
# Todos los endpoints requieren autenticacion JWT

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.proveedor import Proveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorOut
from app.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/api/proveedores", tags=["Proveedores"])

@router.get("/", response_model=List[ProveedorOut])
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Retorna unicamente los proveedores activos (baja logica oculta los desactivados)
    return db.query(Proveedor).filter(Proveedor.activo == True).all()

@router.get("/{id}", response_model=ProveedorOut)
def obtener(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Proveedor).filter(Proveedor.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return p

@router.post("/", response_model=ProveedorOut, status_code=201)
def crear(data: ProveedorCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    # El NIT es unico: si ya existe, se rechaza la creacion con error 400
    if db.query(Proveedor).filter(Proveedor.nit == data.nit).first():
        raise HTTPException(status_code=400, detail="NIT ya registrado")
    p = Proveedor(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.put("/{id}", response_model=ProveedorOut)
def actualizar(id: int, data: ProveedorUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Proveedor).filter(Proveedor.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    # Actualiza solo los campos enviados en la peticion; los campos ausentes (None) se omiten
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{id}", status_code=204)
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(Proveedor).filter(Proveedor.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    # Baja logica: se marca como inactivo pero el registro permanece en la BD
    # Esto evita romper referencias en facturas historicas que ya apuntan a este proveedor
    p.activo = False
    db.commit()
