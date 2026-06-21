from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Los schemas de Pydantic validan y serializan los datos que entran y salen de la API.
# Cada modelo ORM tiene schemas separados: Base (campos comunes), Create (entrada),
# Update (edición parcial) y Out (respuesta al cliente).


# ── Category ────────────────────────────────────────────────
class CategoryBase(BaseModel):
    # Campos comunes a crear y leer una categoría
    name: str
    description: Optional[str] = None   # Optional → puede omitirse en el JSON de entrada


class CategoryCreate(CategoryBase):
    pass  # Hereda todos los campos de CategoryBase sin cambios; se usa en POST /api/categories/


class CategoryUpdate(BaseModel):
    # Todos los campos son opcionales para permitir actualizaciones parciales (PATCH-style en PUT)
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int  # El ID lo asigna la BD; se incluye solo en la respuesta, no en la creación

    # from_attributes=True permite que Pydantic lea los datos desde un objeto ORM (no solo dicts)
    model_config = {"from_attributes": True}


# ── Answer ──────────────────────────────────────────────────
class AnswerBase(BaseModel):
    answer_text: str


class AnswerCreate(AnswerBase):
    question_id: int  # Al crear una respuesta se debe indicar a qué pregunta pertenece


class AnswerUpdate(BaseModel):
    answer_text: Optional[str] = None  # Solo se puede editar el texto (no cambiar la pregunta)


class AnswerOut(AnswerBase):
    id: int
    question_id: int

    model_config = {"from_attributes": True}


# ── Question ────────────────────────────────────────────────
class QuestionBase(BaseModel):
    question_text: str
    category_id: Optional[int] = None  # La categoría es opcional


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    category_id: Optional[int] = None


class QuestionOut(QuestionBase):
    id: int
    category: Optional[CategoryOut] = None  # Objeto categoría anidado (puede ser null)
    answers: List[AnswerOut] = []            # Lista de respuestas anidadas

    model_config = {"from_attributes": True}


# ── Auth ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    # Cuerpo del POST /api/auth/login
    username: str
    password: str


class Token(BaseModel):
    # Respuesta que devuelve el endpoint de login
    access_token: str   # El JWT codificado
    token_type: str     # Siempre "bearer"


# ── Bot Config ───────────────────────────────────────────────
class ConfigItem(BaseModel):
    # Cuerpo del POST /api/config/ para crear o actualizar una clave
    key: str
    value: Optional[str] = None


class ConfigOut(BaseModel):
    # Respuesta de los endpoints de configuración
    key: str
    value: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Bot Query ────────────────────────────────────────────────
class BotQueryRequest(BaseModel):
    # Cuerpo del POST /api/bot/query (lo envía el bot de Telegram)
    query: str                              # Texto que escribió el usuario en Telegram
    telegram_user: Optional[str] = None    # @username del usuario (para los logs)
    telegram_user_id: Optional[str] = None # ID numérico del usuario (para los logs)


class BotQueryResponse(BaseModel):
    # Respuesta que recibe el bot de Telegram
    answer: Optional[str] = None  # Texto de la respuesta; None si no se encontró
    found: bool                   # True si el algoritmo encontró una respuesta con score >= 0.25


# ── Query Log ────────────────────────────────────────────────
class QueryLogOut(BaseModel):
    # Schema para leer el historial de consultas del bot
    id: int
    telegram_user: Optional[str] = None
    query_text: Optional[str] = None
    response_text: Optional[str] = None
    timestamp: datetime
    found_answer: bool

    model_config = {"from_attributes": True}


# ── Stats ────────────────────────────────────────────────────
class StatsOut(BaseModel):
    # Schema de respuesta del dashboard de estadísticas
    total_questions: int
    total_answers: int
    total_categories: int
    total_queries: int        # Total de consultas registradas en el log
    queries_answered: int     # Consultas que sí tuvieron respuesta
    queries_unanswered: int   # Consultas sin respuesta
    top_queries: List[dict]   # Lista de las 10 consultas más frecuentes [{query, count}]
