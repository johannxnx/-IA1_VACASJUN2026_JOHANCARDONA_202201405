from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class Category(Base):
    # Nombre de la tabla en PostgreSQL
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)           # Clave primaria autoincremental
    name        = Column(String(100), unique=True, nullable=False)        # Nombre único de la categoría
    description = Column(String(500), nullable=True)                      # Descripción opcional

    # Relación 1-N con Question: una categoría tiene muchas preguntas
    # cascade="all, delete-orphan" → al borrar una categoría se borran sus preguntas automáticamente
    # back_populates enlaza con el atributo "category" definido en Question
    questions = relationship(
        "Question",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="select",
    )


class Question(Base):
    __tablename__ = "questions"

    id            = Column(Integer, primary_key=True, index=True)
    question_text = Column(String(500), nullable=False)                   # Texto de la pregunta
    # FK a categories.id; ondelete="SET NULL" → si se borra la categoría, category_id queda NULL (no se borra la pregunta)
    category_id   = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    # Relación N-1 con Category (cada pregunta pertenece a una categoría)
    category = relationship("Category", back_populates="questions", lazy="select")

    # Relación 1-N con Answer: una pregunta puede tener varias respuestas
    # cascade="all, delete-orphan" → al borrar una pregunta se borran sus respuestas automáticamente
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="select",
    )


class Answer(Base):
    __tablename__ = "answers"

    id          = Column(Integer, primary_key=True, index=True)
    answer_text = Column(Text, nullable=False)                            # Texto de la respuesta (Text = sin límite de caracteres)
    # FK a questions.id; ondelete="CASCADE" → si se borra la pregunta, esta respuesta también se borra
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)

    # Relación N-1 con Question
    question = relationship("Question", back_populates="answers", lazy="select")


class AdminUser(Base):
    # Tabla de usuarios administradores del panel web
    __tablename__ = "admin_users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(100), unique=True, nullable=False)      # Nombre de usuario único
    password_hash = Column(String(255), nullable=False)                   # Contraseña hasheada con bcrypt (nunca en texto plano)


class QueryLog(Base):
    # Registro histórico de todas las consultas que los usuarios envían al bot
    __tablename__ = "query_logs"

    id               = Column(Integer, primary_key=True, index=True)
    telegram_user    = Column(String(100), nullable=True)                 # Nombre de usuario de Telegram (@usuario)
    telegram_user_id = Column(String(50),  nullable=True)                 # ID numérico del usuario en Telegram
    query_text       = Column(String(500), nullable=True)                 # Texto exacto que envió el usuario
    response_text    = Column(Text,        nullable=True)                 # Respuesta que devolvió el bot (NULL si no encontró)
    timestamp        = Column(DateTime, default=datetime.utcnow)          # Fecha y hora UTC de la consulta
    found_answer     = Column(Boolean, default=True)                      # True si se encontró respuesta, False si no


class BotConfig(Base):
    # Tabla de configuración del bot (clave-valor genérico)
    # Actualmente almacena: telegram_chat_id
    __tablename__ = "bot_config"

    id    = Column(Integer, primary_key=True, index=True)
    key   = Column(String(100), unique=True, nullable=False)              # Nombre de la configuración (ej: "telegram_chat_id")
    value = Column(String(500), nullable=True)                            # Valor de la configuración
