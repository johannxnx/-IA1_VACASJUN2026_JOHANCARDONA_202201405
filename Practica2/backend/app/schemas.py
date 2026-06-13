from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ── Category ────────────────────────────────────────────────
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int

    model_config = {"from_attributes": True}


# ── Answer ──────────────────────────────────────────────────
class AnswerBase(BaseModel):
    answer_text: str


class AnswerCreate(AnswerBase):
    question_id: int


class AnswerUpdate(BaseModel):
    answer_text: Optional[str] = None


class AnswerOut(AnswerBase):
    id: int
    question_id: int

    model_config = {"from_attributes": True}


# ── Question ────────────────────────────────────────────────
class QuestionBase(BaseModel):
    question_text: str
    category_id: Optional[int] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    category_id: Optional[int] = None


class QuestionOut(QuestionBase):
    id: int
    category: Optional[CategoryOut] = None
    answers: List[AnswerOut] = []

    model_config = {"from_attributes": True}


# ── Auth ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ── Bot Config ───────────────────────────────────────────────
class ConfigItem(BaseModel):
    key: str
    value: Optional[str] = None


class ConfigOut(BaseModel):
    key: str
    value: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Bot Query ────────────────────────────────────────────────
class BotQueryRequest(BaseModel):
    query: str
    telegram_user: Optional[str] = None
    telegram_user_id: Optional[str] = None


class BotQueryResponse(BaseModel):
    answer: Optional[str] = None
    found: bool


# ── Query Log ────────────────────────────────────────────────
class QueryLogOut(BaseModel):
    id: int
    telegram_user: Optional[str] = None
    query_text: Optional[str] = None
    response_text: Optional[str] = None
    timestamp: datetime
    found_answer: bool

    model_config = {"from_attributes": True}


# ── Stats ────────────────────────────────────────────────────
class StatsOut(BaseModel):
    total_questions: int
    total_answers: int
    total_categories: int
    total_queries: int
    queries_answered: int
    queries_unanswered: int
    top_queries: List[dict]
