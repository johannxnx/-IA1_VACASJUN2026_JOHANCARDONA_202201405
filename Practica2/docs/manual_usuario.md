# Manual de Usuario – SmartBot

**Práctica 2 – Inteligencia Artificial 1**  
Universidad de San Carlos de Guatemala – Facultad de Ingeniería

---

## 1. Requisitos previos

- Docker Desktop instalado y en ejecución
- Docker Compose incluido (viene con Docker Desktop)
- Token de bot de Telegram (obtenido desde BotFather)
- Conexión a internet

---

## 2. Obtener el token del bot de Telegram

1. Abre Telegram y busca `@BotFather`
2. Envía el comando `/newbot`
3. Sigue las instrucciones: ingresa el nombre y username del bot
4. BotFather te proporcionará un token similar a: `123456:ABCdef...`
5. Guarda ese token, lo necesitarás en el siguiente paso

---

## 3. Instalación y configuración

### 3.1 Clonar o descargar el repositorio

```bash
git clone https://github.com/johannxnx/-IA1_VACASJUN2026_JOHANCARDONA_202201405.git
cd -IA1_VACASJUN2026_JOHANCARDONA_202201405/Practica2
```

### 3.2 Crear el archivo de variables de entorno

Copia el archivo de ejemplo y completa tu token:

```bash
cp .env.example .env
```

Edita `.env` y reemplaza el valor:

```env
TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI
```

### 3.3 Levantar el proyecto con Docker Compose

```bash
docker-compose up --build
```

Espera hasta que veas el mensaje:

```
smartbot_backend | INFO:     Application startup complete.
smartbot_bot     | INFO - SmartBot iniciado. Esperando mensajes…
```

> Los datos iniciales (23 preguntas, 5 categorías, usuario admin) se cargan automáticamente.

---

## 4. Acceder al panel administrativo

Abre tu navegador en:

```
http://localhost:8000
```

### Credenciales de acceso

| Campo      | Valor              |
|------------|--------------------|
| Usuario    | `IA1-User`         |
| Contraseña | `IA1-password@_new`|

---

## 5. Usar el panel administrativo

### 5.1 Dashboard

Al iniciar sesión verás el **Dashboard** con estadísticas:
- Total de preguntas, respuestas y categorías
- Total de consultas recibidas por el bot
- Consultas respondidas vs sin respuesta
- Las 10 consultas más frecuentes

### 5.2 Gestión de Categorías

Navega a **Categorías** en el menú lateral:

- **Ver**: todas las categorías aparecen en la tabla
- **Crear**: click en el botón **"Nueva"** → completa nombre y descripción → **Guardar**
- **Editar**: click en el ícono ✏️ de la fila correspondiente
- **Eliminar**: click en el ícono 🗑️ → confirmar

> Las preguntas de una categoría eliminada quedan sin categoría asignada.

### 5.3 Gestión de Preguntas

Navega a **Preguntas**:

- **Crear**: click en **"Nueva"** → escribe la pregunta → selecciona categoría (opcional) → **Guardar**
- **Editar**: click en ✏️
- **Eliminar**: click en 🗑️ → confirmar (también elimina sus respuestas asociadas)

La columna **Resp.** muestra cuántas respuestas tiene cada pregunta.

### 5.4 Gestión de Respuestas

Navega a **Respuestas**:

- **Crear**: click en **"Nueva"** → selecciona la pregunta → escribe la respuesta → **Guardar**
- **Editar**: click en ✏️ (solo se puede editar el texto, no cambiar la pregunta)
- **Eliminar**: click en 🗑️

### 5.5 Configuración del Bot

Navega a **Configuración**:

- Ingresa el **Chat ID** del grupo o canal de Telegram donde opera el bot
- Click en **Guardar configuración**

Para obtener el Chat ID de un grupo, añade el bot al grupo y envía un mensaje; el ID aparecerá en los logs del bot.

### 5.6 Historial de Consultas (Logs)

Navega a **Logs** para ver:
- Fecha y hora de cada consulta
- Usuario de Telegram que realizó la consulta
- Texto de la consulta
- Respuesta proporcionada
- Estado: `Respondida` o `Sin respuesta`

Usa el botón **Actualizar** para refrescar los datos.

---

## 6. Usar el bot de Telegram

1. Busca tu bot en Telegram por su username
2. Envía `/start` para iniciarlo
3. Escribe cualquier pregunta en lenguaje natural, por ejemplo:
   - `¿Cuál es el horario de la biblioteca?`
   - `cómo me inscribo`
   - `wifi de la universidad`
4. El bot responderá con la información más relevante

### Comandos disponibles

| Comando       | Descripción                          |
|---------------|--------------------------------------|
| `/start`      | Inicia el bot y muestra bienvenida   |
| `/help`       | Muestra ayuda de uso                 |
| `/categorias` | Lista las categorías disponibles     |

---

## 7. Detener el proyecto

```bash
docker-compose down
```

Para también eliminar la base de datos:

```bash
docker-compose down -v
```

---

## 8. Solución de problemas

| Problema                              | Solución                                                              |
|---------------------------------------|-----------------------------------------------------------------------|
| El bot no responde                    | Verifica que `TELEGRAM_BOT_TOKEN` está correcto en el archivo `.env`  |
| El panel no carga en `localhost:8000` | Espera que el backend termine de iniciar (~30 s)                      |
| Error de conexión a la base de datos  | El servicio `db` puede no estar listo; espera el healthcheck          |
| "Credenciales incorrectas"            | Usa exactamente `IA1-User` y `IA1-password@_new`                      |
| El bot dice "Error al procesar"       | El backend puede no estar disponible; revisa los logs con `docker-compose logs` |

---

## 9. Ver logs de los servicios

```bash
# Todos los servicios
docker-compose logs -f

# Solo el bot
docker-compose logs -f bot

# Solo el backend
docker-compose logs -f backend
```

---

## 10. Documentación de la API

La documentación interactiva (Swagger) está disponible en:

```
http://localhost:8000/api/docs
```

Desde ahí puedes probar todos los endpoints de la API REST.
