"""
Bot de WhatsApp con Gemini 1.5 Pro
===================================
- Procesa texto y notas de voz
- Memoria de conversación por usuario
- Fallback automático a Flash si hay error de cuota
"""

import os
import base64
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

# ============================================================
# CONFIGURACIÓN - Las claves se leen de variables de entorno
# ============================================================
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

# Configurar el cliente de Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# ============================================================
# MEMORIA - Almacena el historial de cada usuario en RAM
# ============================================================
# Formato: { "whatsapp:+34612345678": [{"role": "user", "parts": ["Hola"]}, ...] }
conversation_history = {}

# Límite de mensajes en memoria por usuario (para evitar tokens excesivos)
MAX_HISTORY_LENGTH = 20

# ============================================================
# MODELOS DE GEMINI
# ============================================================
PRIMARY_MODEL = "gemini-1.5-flash-latest"  # Modelo estable y rápido
FALLBACK_MODEL = "gemini-pro"              # Fallback clásico que siempre funciona

# Instrucción de sistema para el bot
SYSTEM_INSTRUCTION = """Eres un asistente amigable y útil en WhatsApp. 
Responde de forma natural, concisa y en el mismo idioma que te escriban.
Si te envían un audio, escúchalo y responde apropiadamente.
Mantén las respuestas breves ya que es una conversación por chat."""

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__)


def get_gemini_response(user_id: str, content: list, model_name: str = PRIMARY_MODEL) -> str:
    """
    Envía el contenido a Gemini y obtiene una respuesta.
    Mantiene el historial de conversación por usuario.
    """
    # Inicializar historial si es un usuario nuevo
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # Añadir mensaje del usuario al historial
    conversation_history[user_id].append({
        "role": "user",
        "parts": content
    })
    
    # Limitar el tamaño del historial
    if len(conversation_history[user_id]) > MAX_HISTORY_LENGTH:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY_LENGTH:]
    
    try:
        # Crear el modelo
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # Iniciar chat con historial
        chat = model.start_chat(history=conversation_history[user_id][:-1])
        
        # Enviar el mensaje actual
        response = chat.send_message(content)
        
        # Guardar respuesta en historial
        conversation_history[user_id].append({
            "role": "model",
            "parts": [response.text]
        })
        
        return response.text
    
    except Exception as e:
        error_str = str(e).lower()
        print(f"[ERROR GEMINI] {str(e)}")  # Log para ver en Render
        
        # Si es error de cuota y estamos en el modelo primario, intentar con fallback
        if model_name == PRIMARY_MODEL and ("quota" in error_str or "429" in error_str or "resource" in error_str):
            # Eliminar el mensaje que falló del historial
            if conversation_history[user_id]:
                conversation_history[user_id].pop()
            return get_gemini_response(user_id, content, FALLBACK_MODEL)
        
        # Eliminar el mensaje que falló del historial
        if conversation_history[user_id]:
            conversation_history[user_id].pop()
        
        # Error genérico
        return f"⚠️ Error: {str(e)[:100]}"


def download_media(media_url: str) -> bytes | None:
    """
    Descarga un archivo multimedia de Twilio usando autenticación básica.
    """
    try:
        response = requests.get(
            media_url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=30
        )
        if response.status_code == 200:
            return response.content
        return None
    except Exception:
        return None


def process_audio(media_url: str, content_type: str) -> list:
    """
    Descarga y prepara el audio para enviarlo a Gemini.
    Retorna el contenido formateado para la API.
    """
    audio_data = download_media(media_url)
    
    if audio_data:
        # Determinar el tipo MIME correcto
        mime_type = content_type if content_type else "audio/ogg"
        
        # Codificar en base64 para la API
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        return [
            {"mime_type": mime_type, "data": audio_base64},
            "Escucha este audio y responde apropiadamente."
        ]
    
    return ["El usuario intentó enviar un audio pero no se pudo procesar."]


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint principal que recibe los mensajes de WhatsApp vía Twilio.
    """
    # Crear respuesta TwiML
    twiml_response = MessagingResponse()
    
    try:
        # Datos del mensaje entrante
        user_id = request.form.get("From", "unknown")
        message_body = request.form.get("Body", "").strip()
        num_media = int(request.form.get("NumMedia", 0))
        
        # Contenido a enviar a Gemini
        content_for_gemini = []
        
        # Procesar archivos adjuntos (audio/imágenes)
        if num_media > 0:
            for i in range(num_media):
                media_url = request.form.get(f"MediaUrl{i}")
                content_type = request.form.get(f"MediaContentType{i}", "")
                
                # Verificar si es audio
                if content_type.startswith("audio/"):
                    audio_content = process_audio(media_url, content_type)
                    content_for_gemini.extend(audio_content)
                
                # Verificar si es imagen
                elif content_type.startswith("image/"):
                    image_data = download_media(media_url)
                    if image_data:
                        image_base64 = base64.b64encode(image_data).decode("utf-8")
                        content_for_gemini.append({"mime_type": content_type, "data": image_base64})
                        content_for_gemini.append("Describe esta imagen y responde si el usuario pregunta algo sobre ella.")
                    else:
                        content_for_gemini.append("El usuario envió una imagen que no se pudo procesar.")
                
                else:
                    # Formato no soportado
                    content_for_gemini.append(f"El usuario envió un archivo de tipo {content_type} que no puedo procesar.")
        
        # Añadir texto del mensaje si existe
        if message_body:
            content_for_gemini.append(message_body)
        
        # Si no hay contenido válido
        if not content_for_gemini:
            twiml_response.message("🤔 No pude entender eso. Envíame un texto o una nota de voz.")
            return str(twiml_response)
        
        # Obtener respuesta de Gemini
        bot_response = get_gemini_response(user_id, content_for_gemini)
        
        # Limitar longitud de respuesta (WhatsApp tiene límite de 1600 caracteres)
        if len(bot_response) > 1500:
            bot_response = bot_response[:1497] + "..."
        
        twiml_response.message(bot_response)
    
    except Exception:
        # Error a prueba de balas - nunca crashea
        twiml_response.message("⚠️ Algo salió mal. Por favor, intenta de nuevo.")
    
    return str(twiml_response)


@app.route("/", methods=["GET"])
def health_check():
    """
    Endpoint de verificación de salud para Render/Railway.
    """
    return "✅ Bot de WhatsApp con Gemini activo", 200


if __name__ == "__main__":
    # Solo para desarrollo local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
