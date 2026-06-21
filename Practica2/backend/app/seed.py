from .database import SessionLocal
from .models import AdminUser, Category, Question, Answer, BotConfig
from .auth import get_password_hash


def seed_data():
    # Inserta datos iniciales en la BD la primera vez que el sistema arranca
    # Se llama desde el evento "startup" de FastAPI (main.py)
    db = SessionLocal()
    try:
        # Crea el usuario administrador si no existe todavía
        if not db.query(AdminUser).filter(AdminUser.username == "IA1-User").first():
            db.add(AdminUser(
                username="IA1-User",
                password_hash=get_password_hash("IA1-password@_new"),  # contraseña hasheada con bcrypt
            ))

        # Crea la entrada de configuración del Chat ID si no existe
        if not db.query(BotConfig).filter(BotConfig.key == "telegram_chat_id").first():
            db.add(BotConfig(key="telegram_chat_id", value=None))  # valor vacío hasta que el admin lo configure

        # Si ya hay categorías, los datos de preguntas/respuestas ya fueron insertados; salir
        if db.query(Category).count() > 0:
            db.commit()
            return

        # ── Categorías ──────────────────────────────────────────────────────────
        cat1 = Category(name="Horarios y Fechas",      description="Información sobre horarios y fechas importantes")
        cat2 = Category(name="Requisitos y Trámites",  description="Documentación y procesos de inscripción")
        cat3 = Category(name="Servicios y Recursos",   description="Servicios disponibles para estudiantes")
        cat4 = Category(name="Tecnología e Informática", description="Soporte técnico y recursos digitales")
        cat5 = Category(name="General",                description="Preguntas generales de la facultad")
        db.add_all([cat1, cat2, cat3, cat4, cat5])
        # flush() envía los INSERTs a la BD sin hacer commit, para que los objetos reciban su id
        db.flush()

        # ── Preguntas y respuestas ───────────────────────────────────────────────
        # Cada tupla: (id de categoría, texto de pregunta, texto de respuesta)
        qa_data = [
            # Horarios y Fechas
            (cat1.id, "¿Cuál es el horario de la biblioteca?",
             "La biblioteca está abierta de lunes a viernes de 7:30 AM a 8:00 PM y los sábados de 8:00 AM a 1:00 PM."),
            (cat1.id, "¿Cuándo son los exámenes finales?",
             "Los exámenes finales se realizan en la última semana del semestre según el calendario académico publicado en el portal estudiantil."),
            (cat1.id, "¿Cuál es el horario de secretaría?",
             "Secretaría atiende de lunes a viernes de 8:00 AM a 4:00 PM sin cerrar al mediodía."),
            (cat1.id, "¿Cuándo inicia el próximo semestre?",
             "Las fechas de inicio de semestre se publican en el calendario académico oficial disponible en el portal web de la facultad."),
            (cat1.id, "¿Cuáles son los períodos de zona?",
             "Los períodos de zona se realizan aproximadamente a la mitad del semestre. Consulte el calendario académico para las fechas exactas."),

            # Requisitos y Trámites
            (cat2.id, "¿Cómo me puedo inscribir?",
             "Para inscribirse debe acceder al portal estudiantil con sus credenciales, seleccionar los cursos disponibles y completar el proceso en las fechas habilitadas."),
            (cat2.id, "¿Qué documentos necesito para inscripción?",
             "Para la inscripción necesita: DPI vigente, certificado de bachillerato, fotografías tamaño cédula y comprobante de pago de inscripción."),
            (cat2.id, "¿Cómo solicito mi cierre de pensum?",
             "Debe acudir a secretaría con su historial académico completo y llenar el formulario de cierre de pensum para revisión por el departamento académico."),
            (cat2.id, "¿Cómo obtengo mi carné universitario?",
             "El carné universitario se tramita en el Departamento de Registro una vez completada la inscripción. Necesita presentar DPI y fotografía reciente."),
            (cat2.id, "¿Cómo solicito una constancia de estudios?",
             "Las constancias de estudios se solicitan en secretaría o mediante el portal estudiantil en la sección de trámites. El tiempo de entrega es de 3 a 5 días hábiles."),
            (cat2.id, "¿Cuál es el proceso para retiro de cursos?",
             "El retiro de cursos se realiza en las fechas habilitadas a través del portal estudiantil o en secretaría con el formulario correspondiente."),

            # Servicios y Recursos
            (cat3.id, "¿Hay servicio de transporte universitario?",
             "Sí, la universidad cuenta con rutas de transporte universitario. Consulte los horarios y rutas disponibles en el portal estudiantil o en la sección de bienestar."),
            (cat3.id, "¿Hay cafetería en el campus?",
             "Sí, hay varias cafeterías en el campus que ofrecen desayuno, almuerzo y refacciones a precios accesibles para la comunidad universitaria."),
            (cat3.id, "¿Cómo accedo al servicio de salud estudiantil?",
             "El servicio de salud está disponible en la clínica universitaria de lunes a viernes. Puede solicitar cita de manera presencial o por teléfono."),
            (cat3.id, "¿Existe orientación psicológica?",
             "Sí, la facultad ofrece servicio de orientación psicológica gratuita para estudiantes. Consulte el horario de atención en el departamento de bienestar estudiantil."),
            (cat3.id, "¿Dónde puedo hacer impresiones?",
             "Existen centros de copiado e impresión dentro del campus, generalmente ubicados cerca de las principales edificaciones académicas."),

            # Tecnología e Informática
            (cat4.id, "¿Cómo me conecto al WiFi de la universidad?",
             "Para conectarse al WiFi universitario use su correo institucional como usuario. Si es la primera vez, solicite sus credenciales en el departamento de sistemas."),
            (cat4.id, "¿Cómo accedo al portal estudiantil?",
             "Ingrese al portal estudiantil en portal.usac.edu.gt con su número de carné. Si es primera vez, use su número de carné como contraseña y cámbiela de inmediato."),
            (cat4.id, "¿Qué hago si olvidé mi contraseña del portal?",
             "Si olvidó su contraseña, contacte al departamento de soporte técnico presentando su DPI y número de carné para el proceso de recuperación."),
            (cat4.id, "¿Tienen laboratorios de computación disponibles?",
             "Sí, hay laboratorios de computación disponibles para estudiantes en horarios establecidos. Consulte la disponibilidad en el departamento de informática."),
            (cat4.id, "¿Cómo accedo a las plataformas virtuales de clases?",
             "Las plataformas virtuales de clases se acceden con sus credenciales institucionales. El enlace específico lo proporciona el catedrático al inicio del curso."),

            # General
            (cat5.id, "¿Cuál es el número de teléfono principal?",
             "El número de teléfono principal aparece en el sitio web oficial de la facultad. También puede consultar el directorio por departamentos."),
            (cat5.id, "¿Cómo puedo contactar a un catedrático?",
             "Puede contactar a los catedráticos a través del correo institucional, el portal estudiantil o acudiendo a sus horas de consulta publicadas al inicio del semestre."),
            (cat5.id, "¿Qué hago si tengo problemas con una nota?",
             "Si tiene problemas con una nota debe acudir al catedrático del curso primero. Si no se resuelve, puede presentar una apelación formal en secretaría dentro del plazo establecido."),
        ]

        for cat_id, question_text, answer_text in qa_data:
            q = Question(question_text=question_text, category_id=cat_id)
            db.add(q)
            db.flush()  # obtiene el id de la pregunta recién insertada
            db.add(Answer(answer_text=answer_text, question_id=q.id))

        db.commit()
        print("[SmartBot] Datos iniciales cargados correctamente.")
    except Exception as e:
        db.rollback()  # revierte todos los cambios si algo falló
        print(f"[SmartBot] Error al cargar datos iniciales: {e}")
    finally:
        db.close()
