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
    return db.query(BotConfig).all()


@router.get("/{key}", response_model=ConfigOut)
def get_config_by_key(key: str, db: Session = Depends(get_db)):
    cfg = db.query(BotConfig).filter(BotConfig.key == key).first()
    if not cfg:
        return ConfigOut(key=key, value=None)
    return cfg


@router.post("/", response_model=ConfigOut)
def set_config(
    data: ConfigItem,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cfg = db.query(BotConfig).filter(BotConfig.key == data.key).first()
    if cfg:
        cfg.value = data.value
    else:
        cfg = BotConfig(key=data.key, value=data.value)
        db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg
