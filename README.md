# 🤖 Bot de WhatsApp con Gemini 3 Pro

Tu asistente personal de IA en WhatsApp. Responde textos, escucha notas de voz y ve imágenes.

---

## ⏱️ Tiempo estimado: 15 minutos

---

## 📋 ANTES DE EMPEZAR

Necesitarás crear 3 cuentas gratuitas:

| Servicio | Para qué | Enlace |
|----------|----------|--------|
| Google AI Studio | La inteligencia del bot | [aistudio.google.com](https://aistudio.google.com) |
| Twilio | Conectar con WhatsApp | [twilio.com](https://www.twilio.com/try-twilio) |
| Render | Servidor gratuito 24/7 | [render.com](https://render.com) |
| GitHub | Guardar el código | [github.com](https://github.com) |

---

# 🔑 PASO 1: Obtener API Key de Google

1. Abre **[aistudio.google.com](https://aistudio.google.com)**
2. Inicia sesión con tu cuenta de Google
3. En el menú de la izquierda, haz clic en **"Get API Key"**
4. Clic en el botón **"Create API Key"**
5. Selecciona **"Create API key in new project"**
6. Aparecerá una clave que empieza con `AIza...`

```
✏️ COPIA Y GUARDA ESTA CLAVE EN UN BLOC DE NOTAS:

GOOGLE_API_KEY = AIza________________________________
```

---

# 📱 PASO 2: Configurar Twilio

## 2.1 Crear cuenta

1. Ve a **[twilio.com/try-twilio](https://www.twilio.com/try-twilio)**
2. Rellena el formulario con tu email y contraseña
3. Verifica tu email (te llegará un correo)
4. Verifica tu número de teléfono (te envían SMS)

## 2.2 Obtener credenciales

1. Después de registrarte, llegas al **Dashboard**
2. En la parte de arriba verás **"Account Info"**
3. Copia estos dos valores:

```
✏️ COPIA Y GUARDA ESTAS DOS CLAVES:

TWILIO_ACCOUNT_SID = AC________________________________
                     (empieza con AC)

TWILIO_AUTH_TOKEN = ________________________________
                    (haz clic en "Show" para verlo)
```

## 2.3 Activar WhatsApp Sandbox

1. En el menú lateral izquierdo: **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Verás un número de teléfono y un código como: `join funny-elephant`
3. **Abre WhatsApp en tu móvil**
4. Añade ese número como contacto
5. Envíale el mensaje con el código (ej: `join funny-elephant`)
6. Recibirás: *"You are all set!"*

```
✏️ GUARDA EL NÚMERO DE TWILIO:

NÚMERO DE WHATSAPP = +1 415 XXX XXXX
```

---

# 💻 PASO 3: Subir código a GitHub

## 3.1 Crear repositorio

1. Ve a **[github.com](https://github.com)** e inicia sesión
2. Clic en el botón verde **"New"** (arriba a la izquierda)
3. Configura:
   - **Repository name**: `whatsapp-gemini-bot`
   - **Visibility**: Public ✓
4. Clic en **"Create repository"**

## 3.2 Subir archivos

1. En la página del repositorio vacío, clic en **"uploading an existing file"**
2. Arrastra estos 3 archivos desde tu ordenador:
   - `main.py`
   - `requirements.txt`
   - `Procfile`
3. Clic en **"Commit changes"** (botón verde abajo)

---

# 🚀 PASO 4: Desplegar en Render

## 4.1 Crear cuenta y servicio

1. Ve a **[render.com](https://render.com)**
2. Clic en **"Get Started for Free"**
3. Elige **"GitHub"** para registrarte (más fácil)
4. Una vez dentro, clic en **"New +"** → **"Web Service"**

## 4.2 Conectar repositorio

1. Si te pide permisos de GitHub, acéptalos
2. Busca tu repositorio `whatsapp-gemini-bot` y haz clic en **"Connect"**

## 4.3 Configurar el servicio

Rellena estos campos:

| Campo | Valor |
|-------|-------|
| **Name** | `whatsapp-bot` |
| **Region** | Frankfurt (EU Central) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn main:app` |

Baja hasta **"Instance Type"** y selecciona **Free**

## 4.4 Añadir variables de entorno (⚠️ MUY IMPORTANTE)

1. Baja hasta la sección **"Environment Variables"**
2. Añade estas 3 variables (haz clic en **"Add Environment Variable"** para cada una):

| Key | Value |
|-----|-------|
| `GOOGLE_API_KEY` | `AIza...` (la que copiaste en Paso 1) |
| `TWILIO_ACCOUNT_SID` | `AC...` (la que copiaste en Paso 2) |
| `TWILIO_AUTH_TOKEN` | (la que copiaste en Paso 2) |

3. Clic en **"Create Web Service"**

## 4.5 Esperar el despliegue

1. Render empezará a construir tu bot (barra de progreso)
2. Espera 2-3 minutos
3. Cuando termine, verás **"Live"** en verde
4. Arriba aparecerá tu URL:

```
✏️ COPIA TU URL DE RENDER:

https://whatsapp-bot-xxxx.onrender.com
```

---

# 🔗 PASO 5: Conectar Twilio con tu bot

1. Vuelve a **[console.twilio.com](https://console.twilio.com)**
2. Ve a **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Clic en la pestaña **"Sandbox settings"**
4. En el campo **"When a message comes in"**, escribe tu URL + `/webhook`:

```
https://whatsapp-bot-xxxx.onrender.com/webhook
```

5. Asegúrate de que diga **HTTP POST**
6. Clic en **"Save"**

---

# ✅ PASO 6: ¡Probar el bot!

1. Abre **WhatsApp** en tu móvil
2. Ve al chat con el número de Twilio
3. Escribe cualquier mensaje (ej: "Hola, ¿cómo estás?")
4. Espera unos segundos...
5. **¡El bot te responderá!** 🎉

### Prueba también:
- 🎤 **Envía una nota de voz** → El bot la escuchará y responderá
- 📷 **Envía una imagen** → El bot la describirá
- 💬 **Hazle preguntas** → El bot recuerda la conversación

---

# ❓ Problemas comunes

| Problema | Solución |
|----------|----------|
| **El bot no responde** | Verifica las 3 variables de entorno en Render |
| **Tarda mucho la primera vez** | Render apaga los servidores gratis tras 15 min. El primer mensaje puede tardar 30 seg |
| **Error de cuota** | El plan gratis de Gemini tiene límites. Espera unos minutos |
| **"Algo salió mal"** | Revisa que la URL en Twilio termine en `/webhook` |

---

# 📊 Resumen de claves

```
╔═══════════════════════════════════════════════════════════╗
║                    TUS CLAVES SECRETAS                     ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  GOOGLE_API_KEY      = AIza____________________________    ║
║                                                            ║
║  TWILIO_ACCOUNT_SID  = AC______________________________    ║
║                                                            ║
║  TWILIO_AUTH_TOKEN   = ________________________________    ║
║                                                            ║
║  URL DE RENDER       = https://_________.onrender.com      ║
║                                                            ║
║  WEBHOOK COMPLETO    = https://_________.onrender.com/webhook
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

---

# 🔧 Especificaciones técnicas

| Característica | Valor |
|---------------|-------|
| Modelo principal | Gemini 3 Pro Preview |
| Modelo de respaldo | Gemini 2.0 Flash |
| Memoria | Últimos 20 mensajes por usuario |
| Formatos soportados | Texto, audio, imágenes |
| Contexto máximo | 1 millón de tokens |

---

**¿Todo listo?** ¡Disfruta tu bot! 🚀
