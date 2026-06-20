# SmartInvoice - Manual Tecnico

**Universidad de San Carlos de Guatemala**
**Facultad de Ingenieria - Escuela de Ciencias y Sistemas**
**Inteligencia Artificial 1 - Seccion A - Vacaciones Junio 2026**

| Campo | Detalle |
|---|---|
| Estudiante | Johan Moises Cardona Rosales |
| Carne | 202201405 |
| Catedratico | M.S.c Luis Fernando Espino Barrios |
| Auxiliar | Roberto Miguel Garcia Santizo |
| Fecha | Junio 2026 |

---

## 1. Descripcion General

SmartInvoice es un sistema web de procesamiento inteligente de facturas que combina Reconocimiento Optico de Caracteres (OCR), tecnicas de Computer Vision y Automatizacion Robotica de Procesos (RPA) para extraer, validar y registrar datos de documentos fiscales de forma automatica.

El sistema acepta facturas en formato PDF, JPG y PNG, aplica un pipeline de preprocesamiento de imagen con OpenCV, ejecuta el motor EasyOCR para extraer los campos relevantes, valida la consistencia numerica de los datos y los persiste en una base de datos PostgreSQL. Adicionalmente, cada factura procesada dispara una automatizacion RPA con Playwright que llena un formulario web simulado y genera un screenshot de evidencia.

### 1.1 Objetivos

- Automatizar la extraccion de datos de facturas mediante OCR y Computer Vision
- Validar automaticamente la consistencia numerica de los datos extraidos
- Vincular facturas con proveedores registrados por NIT o nombre
- Generar reportes en multiples formatos y enviarlos por correo electronico
- Demostrar la aplicacion de RPA como herramienta de automatizacion de procesos

### 1.2 Stack Tecnologico

| Componente | Tecnologia | Funcion |
|---|---|---|
| Backend | FastAPI (Python) | Framework web y API REST |
| ORM | SQLAlchemy 2.0 | Mapeo objeto-relacional |
| Base de Datos | PostgreSQL 15 | Almacenamiento persistente |
| OCR | EasyOCR | Reconocimiento de texto en imagenes |
| Computer Vision | OpenCV 4 | Preprocesamiento de imagen |
| PDF | PyMuPDF (fitz) | Conversion de PDF a imagen |
| RPA | Playwright | Automatizacion de navegador Chromium |
| Reportes PDF | fpdf2 | Generacion de documentos PDF |
| Reportes Excel | openpyxl | Generacion de archivos Excel |
| Autenticacion | JWT + bcrypt | Tokens de sesion y hash de contrasenas |
| Email | smtplib (stdlib) | Envio de correos via SMTP/TLS |
| Frontend | HTML + CSS + JS | SPA sin frameworks externos |
| Contenedores | Docker Compose | Orquestacion de servicios |

---

## 2. Arquitectura del Sistema

SmartInvoice implementa una **arquitectura en capas** donde cada capa tiene responsabilidades bien definidas y se comunica unicamente con la capa adyacente.

![alt text](image-17.png)

### 2.1 Diagrama de Componentes

![alt text](image-18.png)



### 2.2 Flujo de Procesamiento de una Factura

![alt text](diagramaflujo.drawio.png)

---

## 3. Modelo de Datos

### 3.1 Diagrama de Tablas

![alt text](image-19.png)

### 3.2 Descripcion de Tablas

#### usuarios
| Columna | Tipo | Descripcion |
|---|---|---|
| id | INTEGER PK | Identificador autoincremental |
| nombre | VARCHAR(100) | Nombre completo del usuario |
| email | VARCHAR(150) UNIQUE | Correo electronico usado como login |
| password_hash | VARCHAR(255) | Hash bcrypt de la contrasena |
| rol | VARCHAR(20) | Rol del usuario (admin por defecto) |
| activo | BOOLEAN | Baja logica del usuario |
| creado_en | TIMESTAMP TZ | Fecha de registro |

#### proveedores
| Columna | Tipo | Descripcion |
|---|---|---|
| id | INTEGER PK | Identificador autoincremental |
| nombre | VARCHAR(150) | Razon social o nombre comercial |
| nit | VARCHAR(20) UNIQUE | NIT para vinculacion automatica con facturas |
| direccion | VARCHAR(255) | Direccion fiscal |
| telefono | VARCHAR(20) | Telefono de contacto |
| email | VARCHAR(150) | Correo del proveedor |
| activo | BOOLEAN | Baja logica del proveedor |
| actualizado_en | TIMESTAMP TZ | Ultima modificacion |

#### facturas
| Columna | Tipo | Descripcion |
|---|---|---|
| id | INTEGER PK | Identificador autoincremental |
| usuario_id | INTEGER FK | Usuario que cargo la factura |
| proveedor_id | INTEGER FK | Proveedor vinculado automaticamente |
| numero_factura | VARCHAR(50) | Numero extraido por OCR |
| fecha_factura | DATE | Fecha extraida por OCR |
| subtotal | NUMERIC(12,2) | Monto antes de impuestos |
| impuestos | NUMERIC(12,2) | IVA u otros impuestos |
| total | NUMERIC(12,2) | Monto total |
| nombre_proveedor_ocr | VARCHAR(200) | Nombre del proveedor detectado por OCR |
| estado | VARCHAR(20) | Pendiente / Procesado / Rechazado / Error |
| datos_crudos | TEXT | Texto completo extraido por EasyOCR |
| confianza_ocr | NUMERIC(5,2) | Confianza promedio del OCR en porcentaje |
| procesado_en | TIMESTAMP TZ | Timestamp de fin del proceso OCR |

#### bitacora
| Columna | Tipo | Descripcion |
|---|---|---|
| id | INTEGER PK | Identificador autoincremental |
| factura_id | INTEGER FK | Factura asociada al evento |
| usuario_id | INTEGER FK | Usuario que genero el evento |
| fecha_hora | TIMESTAMP TZ | Fecha y hora exacta del evento |
| accion | VARCHAR(100) | upload / ocr_process / rpa_registro |
| estado | VARCHAR(20) | Estado resultante del proceso |
| resultado | TEXT | Descripcion del resultado |
| detalle_error | TEXT | Error detallado o ruta del screenshot RPA |

#### reportes
| Columna | Tipo | Descripcion |
|---|---|---|
| id | INTEGER PK | Identificador autoincremental |
| usuario_id | INTEGER FK | Usuario que solicito el reporte |
| nombre | VARCHAR(150) | Nombre del archivo (incluye timestamp) |
| tipo | VARCHAR(10) | pdf / excel / csv |
| archivo_ruta | VARCHAR(500) | Ruta en disco del archivo generado |
| enviado_email | BOOLEAN | Indica si fue enviado por correo |
| email_destino | VARCHAR(150) | Correo destinatario |
| creado_en | TIMESTAMP TZ | Fecha de generacion |

---

## 4. API REST

La API esta disponible en `http://localhost:8000`. La documentacion interactiva (Swagger UI) se encuentra en `/docs`.

Todos los endpoints excepto `/api/auth/login` y `/api/auth/registro` requieren autenticacion JWT:

```
Authorization: Bearer <token>
```

### 4.1 Autenticacion

| Metodo | Endpoint | Descripcion |
|---|---|---|
| POST | `/api/auth/login` | Iniciar sesion. Retorna token JWT. |
| POST | `/api/auth/registro` | Registrar nuevo usuario. |

### 4.2 Facturas

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/api/facturas/` | Listar todas las facturas |
| GET | `/api/facturas/{id}` | Detalle de factura (incluye texto OCR) |
| POST | `/api/facturas/upload` | Cargar factura (multipart/form-data) |
| DELETE | `/api/facturas/{id}` | Eliminar factura |

### 4.3 Proveedores

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/api/proveedores/` | Listar proveedores activos |
| GET | `/api/proveedores/{id}` | Obtener proveedor por ID |
| POST | `/api/proveedores/` | Crear proveedor (NIT unico requerido) |
| PUT | `/api/proveedores/{id}` | Actualizar proveedor |
| DELETE | `/api/proveedores/{id}` | Baja logica del proveedor |

### 4.4 Bitacora y Reportes

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/api/bitacora/` | Historial de los ultimos 200 eventos |
| GET | `/api/reportes/` | Listar reportes generados |
| POST | `/api/reportes/generar` | Generar reporte PDF/Excel/CSV |
| GET | `/api/reportes/{id}/descargar` | Descargar archivo de reporte |

---

## 5. Descripcion de los Servicios

### 5.1 Vision Service (`vision_service.py`)

Pipeline de Computer Vision aplicado antes del OCR:

1. **Carga del archivo:** PyMuPDF renderiza el PDF con escala 2x para aumentar resolucion. PIL carga imagenes JPG/PNG.
2. **Escala de grises:** `cv2.cvtColor(img, COLOR_RGB2GRAY)` elimina el color innecesario.
3. **Redimensionamiento:** Si el ancho es menor a 800px se escala con interpolacion cubica.
4. **Denoising:** `fastNlMeansDenoising` elimina ruido preservando bordes del texto.
5. **Binarizacion adaptativa:** Umbral local Gaussiano para iluminacion no uniforme.
6. **Deskew:** `minAreaRect` detecta el angulo de inclinacion y `warpAffine` corrige la rotacion.

### 5.2 OCR Service (`ocr_service.py`)

Utiliza EasyOCR con modelos en espanol e ingles. El lector se inicializa una sola vez (patron Singleton) y se reutiliza entre peticiones. Los campos se extraen con expresiones regulares priorizadas:

- **Numero de factura:** Patrones DTE guatemalteco, FAC-XXXXX, serie+numero, Factura No.
- **Fecha:** Formato ISO, europeo (dd-mm-yyyy), con mes en texto ("31 de enero de 2017").
- **Proveedor:** Etiqueta "Proveedor:", "Razon Social:", sufijo legal (S.A., LTDA), linea en mayusculas.
- **Montos:** Normalizacion de formato europeo (1.100,50) y americano (1,100.50).

### 5.3 RPA Service (`rpa_service.py`)

Playwright controla Chromium en modo headless (`--no-sandbox`). Al procesar una factura exitosamente:

1. Navega a `http://localhost:8000/rpa-form.html`
2. Llena los campos: numero_factura, fecha, proveedor, nit, subtotal, impuestos, total
3. Toma screenshot guardado en `uploads/rpa_evidence_{numero}.png`
4. Hace clic en el boton de registro
5. El nombre del screenshot se guarda en la bitacora para mostrar el enlace "Ver evidencia"

### 5.4 Report Service (`report_service.py`)

| Formato | Libreria | Descripcion |
|---|---|---|
| PDF | fpdf2 | Tabla con encabezado azul y filas alternadas |
| Excel | openpyxl | Hoja de calculo con encabezados |
| CSV | csv (stdlib) | Valores separados por comas en UTF-8 |

La generacion se ejecuta en segundo plano con `BackgroundTasks` de FastAPI.

### 5.5 Email Service (`email_service.py`)

Envia el reporte como adjunto usando `smtplib` con `STARTTLS` (puerto 587). La autenticacion con Gmail usa App Password generado en la cuenta, cumpliendo los requisitos de seguridad de Google. El archivo se adjunta codificado en Base64 mediante `MIMEBase`.

---

## 6. Instalacion y Configuracion

### 6.1 Requisitos

- Python 3.10 o superior
- PostgreSQL 15
- Docker y Docker Compose (opcional)
- Cuenta Gmail con App Password para el envio de correos

### 6.2 Instalacion Manual

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd Practica3/backend

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar navegador para Playwright (RPA)
python -m playwright install chromium

# 5. Crear archivo .env en Practica3/backend/
DATABASE_URL=postgresql://postgres:admin@localhost:5432/smartinvoice
SECRET_KEY=smartinvoice-secret-key-2026-usac-ia1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASSWORD=tu_app_password
EMAIL_FROM=tu_correo@gmail.com

# 6. Ejecutar el script de base de datos en pgAdmin
# Archivo: database/init.sql

# 7. Iniciar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6.3 Instalacion con Docker Compose

```bash
# Desde la carpeta Practica3/
docker-compose up --build

# El sistema queda disponible en http://localhost:8000
```

### 6.4 Estructura de Archivos

```
Practica3/
├── backend/
│   ├── app/
│   │   ├── main.py              # Punto de entrada FastAPI
│   │   ├── config.py            # Variables de entorno
│   │   ├── database.py          # Conexion SQLAlchemy
│   │   ├── auth/
│   │   │   └── jwt_handler.py   # JWT y bcrypt
│   │   ├── models/              # Modelos ORM (5 tablas)
│   │   ├── schemas/             # Esquemas Pydantic
│   │   ├── routers/             # Endpoints por dominio
│   │   └── services/            # Logica de negocio
│   ├── static/                  # Frontend SPA
│   ├── uploads/                 # Facturas subidas y screenshots RPA
│   ├── reports/                 # Reportes generados
│   └── .env                     # Variables de entorno (no en git)
├── database/
│   └── init.sql                 # Script de creacion de tablas
├── docs/                        # Manuales
└── docker-compose.yml
```

---

## 7. Seguridad

- **Autenticacion JWT:** Todos los endpoints privados validan el token en el encabezado `Authorization: Bearer`.
- **Hash de contrasenas:** bcrypt con factor de costo adaptativo. Nunca texto plano en BD.
- **Validacion de archivos:** El servidor verifica el tipo MIME antes de guardar cualquier archivo.
- **Variables de entorno:** Credenciales en `.env`, excluido del repositorio con `.gitignore`.
- **Baja logica:** Usuarios y proveedores se desactivan en lugar de eliminarse para preservar integridad referencial.
- **CORS:** Configurado para permitir peticiones del mismo servidor. En produccion se limitaria al dominio real.

---

*SmartInvoice - Manual Tecnico - Inteligencia Artificial 1 - USAC 2026*
