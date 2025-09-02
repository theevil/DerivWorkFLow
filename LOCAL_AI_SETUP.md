# Configuración de IA Local para DerivWorkFlow

Este documento explica cómo configurar y usar la IA local en DerivWorkFlow para evitar depender de APIs externas como OpenAI.

## 🚀 Características

- **IA Local Completa**: Análisis de mercado, decisiones de trading y gestión de riesgos usando modelos locales
- **Sin Costos Externos**: No más pagos por tokens de OpenAI
- **Privacidad Total**: Todos los datos se procesan localmente
- **Optimizado para Microtransacciones**: Modelos pequeños y rápidos ideales para trading de alta frecuencia
- **Fallback Inteligente**: Si la IA local falla, puede usar OpenAI como respaldo

## 📋 Requisitos

### Hardware Mínimo
- **CPU**: Intel i5/AMD Ryzen 5 o superior
- **RAM**: 8GB mínimo, 16GB recomendado
- **GPU**: Opcional pero recomendado (NVIDIA con 4GB+ VRAM)
- **Almacenamiento**: 10GB libres para modelos

### Software
- Docker y Docker Compose
- Ollama (incluido en el docker-compose)
- Conexión a internet para descargar modelos inicialmente

## 🛠️ Instalación

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd DerivWorkFlow
```

### 2. Configurar Variables de Entorno
```bash
# Copiar el archivo de ejemplo
cp backend-env-example.txt apps/backend/.env

# Editar la configuración
nano apps/backend/.env
```

Configuración recomendada para IA local:
```env
# Local AI Configuration
LOCAL_AI_ENABLED=true
OLLAMA_HOST=http://localhost:11434
DEFAULT_AI_MODEL=phi-3-mini
LOCAL_AI_FALLBACK_ENABLED=true
LOCAL_AI_TIMEOUT=30
LOCAL_AI_MAX_RETRIES=3
AI_PROVIDER=local  # local, openai, hybrid
```

### 3. Iniciar con Docker Compose
```bash
# Iniciar todos los servicios incluyendo Ollama
docker-compose up -d

# Verificar que Ollama esté funcionando
docker-compose logs ollama
```

### 4. Inicializar Modelos de IA
```bash
# Ejecutar el script de inicialización
docker-compose exec backend python scripts/init_local_ai.py
```

O manualmente:
```bash
# Conectar a Ollama
docker-compose exec ollama ollama pull phi3:mini
docker-compose exec ollama ollama pull gemma2:2b
docker-compose exec ollama ollama pull llama3.1:3b
```

## 🎯 Modelos Disponibles

### Modelos Recomendados para Microtransacciones

| Modelo | Tamaño | Velocidad | Memoria | Uso Recomendado |
|--------|--------|-----------|---------|-----------------|
| **Phi-3 Mini** | 3.8B | ⚡⚡⚡⚡⚡ | 4GB | **Recomendado** - Rápido y eficiente |
| **Gemma 2B** | 2B | ⚡⚡⚡⚡⚡ | 3GB | Muy rápido, menor precisión |
| **Llama 3.1 3B** | 3B | ⚡⚡⚡⚡ | 4GB | Buen balance velocidad/precisión |
| **Llama 3.1 8B** | 8B | ⚡⚡⚡ | 8GB | Mayor precisión, más lento |
| **Mistral 7B** | 7B | ⚡⚡⚡ | 7GB | Excelente precisión |

### Modelos OpenAI (Fallback)
- GPT-4o Mini
- GPT-4o
- GPT-4 Turbo
- GPT-3.5 Turbo

## ⚙️ Configuración en la Interfaz

### 1. Acceder a Configuración
1. Inicia sesión en la aplicación
2. Ve a **Settings** → **AI Configuration**

### 2. Seleccionar Proveedor de IA
- **Local AI (Recomendado)**: Usa solo modelos locales
- **OpenAI**: Usa solo OpenAI (requiere API key)
- **Hybrid**: Combina ambos (local como principal, OpenAI como fallback)

### 3. Configurar Modelo Local
- Selecciona el modelo preferido (Phi-3 Mini recomendado)
- Ajusta la temperatura (0.1-0.3 para trading)
- Configura el umbral de confianza (0.6-0.8)

### 4. Probar Conexión
- Haz clic en **"Test Local AI"** para verificar que los modelos funcionan
- Haz clic en **"Initialize Models"** si necesitas descargar modelos

## 🔧 Configuración Avanzada

### Variables de Entorno Adicionales

```env
# Configuración de Rendimiento
LOCAL_AI_TIMEOUT=30          # Timeout en segundos
LOCAL_AI_MAX_RETRIES=3       # Intentos máximos
LOCAL_AI_FALLBACK_ENABLED=true  # Habilitar fallback

# Configuración de Modelos
DEFAULT_AI_MODEL=phi-3-mini  # Modelo por defecto
AI_PROVIDER=local            # Proveedor preferido
```

### Configuración de GPU (Opcional)

Si tienes GPU NVIDIA, edita `docker-compose.yml`:

```yaml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### Configuración de Memoria

Para modelos más grandes, ajusta la memoria de Docker:

```yaml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      limits:
        memory: 8G
      reservations:
        memory: 4G
```

## 🧪 Pruebas y Verificación

### 1. Verificar Estado de Ollama
```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags

# Ver modelos disponibles
docker-compose exec ollama ollama list
```

### 2. Probar Modelo Local
```bash
# Probar directamente con Ollama
docker-compose exec ollama ollama run phi3:mini "Hello, test message"
```

### 3. Verificar desde la API
```bash
# Probar endpoint de IA local
curl -X POST http://localhost:8000/api/v1/ai/test-local-ai \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Verificar desde la Interfaz
1. Ve a **Settings** → **AI Configuration**
2. Haz clic en **"Test Local AI"**
3. Verifica que aparezca "Local AI Test Successful"

## 🔍 Monitoreo y Logs

### Ver Logs de Ollama
```bash
docker-compose logs -f ollama
```

### Ver Logs del Backend
```bash
docker-compose logs -f backend
```

### Ver Logs de IA Local
```bash
docker-compose logs -f backend | grep "local_ai"
```

## 🚨 Solución de Problemas

### Problema: Ollama no inicia
```bash
# Verificar que el puerto 11434 esté libre
netstat -tulpn | grep 11434

# Reiniciar Ollama
docker-compose restart ollama
```

### Problema: Modelos no se descargan
```bash
# Verificar conexión a internet
docker-compose exec ollama ping google.com

# Descargar manualmente
docker-compose exec ollama ollama pull phi3:mini
```

### Problema: IA local no responde
```bash
# Verificar que los modelos estén cargados
docker-compose exec ollama ollama list

# Reiniciar el backend
docker-compose restart backend
```

### Problema: Bajo rendimiento
1. Verifica que tienes suficiente RAM (8GB+)
2. Considera usar un modelo más pequeño
3. Ajusta `LOCAL_AI_TIMEOUT` si es necesario
4. Verifica que no haya otros procesos consumiendo recursos

## 📊 Comparación de Rendimiento

| Métrica | Local AI | OpenAI |
|---------|----------|--------|
| **Latencia** | 1-3 segundos | 2-5 segundos |
| **Costo** | $0 | $0.01-0.10 por análisis |
| **Privacidad** | 100% local | Datos enviados a OpenAI |
| **Disponibilidad** | 99.9% | Depende de OpenAI |
| **Personalización** | Total | Limitada |

## 🔄 Migración desde OpenAI

### 1. Configuración Gradual
1. Cambia `AI_PROVIDER` a `hybrid`
2. Prueba con ambos proveedores
3. Monitorea el rendimiento
4. Cambia a `local` cuando estés seguro

### 2. Configuración Inmediata
1. Cambia `AI_PROVIDER` a `local`
2. Inicializa los modelos locales
3. Prueba la funcionalidad
4. Desactiva OpenAI si todo funciona bien

## 📈 Optimización

### Para Microtransacciones
- Usa **Phi-3 Mini** o **Gemma 2B**
- Configura `AI_TEMPERATURE=0.1`
- Ajusta `AI_CONFIDENCE_THRESHOLD=0.7`
- Usa `AI_ANALYSIS_INTERVAL=30` segundos

### Para Trading de Medio Plazo
- Usa **Llama 3.1 8B** o **Mistral 7B**
- Configura `AI_TEMPERATURE=0.2`
- Ajusta `AI_CONFIDENCE_THRESHOLD=0.6`
- Usa `AI_ANALYSIS_INTERVAL=60` segundos

## 🆘 Soporte

Si encuentras problemas:

1. **Verifica los logs**: `docker-compose logs -f`
2. **Revisa la documentación**: Este archivo y el README principal
3. **Prueba con un modelo más pequeño**: Cambia a Phi-3 Mini
4. **Verifica recursos**: CPU, RAM y almacenamiento
5. **Reinicia servicios**: `docker-compose restart`

## 🎉 ¡Listo!

Con esta configuración, tienes un sistema de IA completamente local que:

- ✅ No depende de APIs externas
- ✅ No genera costos por uso
- ✅ Mantiene total privacidad
- ✅ Está optimizado para microtransacciones
- ✅ Tiene fallback inteligente
- ✅ Es fácil de configurar y mantener

¡Disfruta de tu sistema de trading con IA local! 🚀
