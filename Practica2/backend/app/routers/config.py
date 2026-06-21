from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import BotConfig
from ..schemas import ConfigItem, ConfigOut

router = APIRouter()


@router.get("/", response_model=List[ConfigOut])
def get_all_config(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Devuelve todas las entradas de configuración (solo el admin puede verlas)
    return db.query(BotConfig).all()


@router.get("/{key}", response_model=ConfigOut)
def get_config_by_key(key: str, db: Session = Depends(get_db)):
    # Busca una configuración por su clave (ej: "telegram_chat_id")
    # No requiere autenticación para que el bot pueda leerla internamente
    cfg = db.query(BotConfig).filter(BotConfig.key == key).first()
    if not cfg:
        # Si la clave no existe devuelve un objeto vacío en lugar de 404
        # para evitar errores en el bot cuando la config aún no fue establecida
        return ConfigOut(key=key, value=None)
    return cfg


@router.post("/", response_model=ConfigOut)
def set_config(
    data: ConfigItem,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    # Implementa "upsert": actualiza si la clave existe, inserta si no
    cfg = db.query(BotConfig).filter(BotConfig.key == data.key).first()
    if cfg:
        cfg.value = data.value   # actualiza el valor existente
    else:
        cfg = BotConfig(key=data.key, value=data.value)  # crea nueva entrada
        db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg
