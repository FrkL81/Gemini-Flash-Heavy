# 📊 Sistema de Monitoreo de Uso - Capa Gratuita

## 🎯 Objetivo
Maximizar el uso de la capa gratuita de Google AI Studio monitoreando y optimizando el consumo de API.

## 📋 Límites Reales de la Capa Gratuita

| Modelo | RPM | Solicitudes/Día | Delay Óptimo |
|--------|-----|-----------------|--------------|
| `gemini-2.5-flash` | 10 | 500 | 6.0s |
| `gemini-2.0-flash` | 15 | 1500 | 4.0s |
| `gemini-2.0-flash-lite` | 15 | 1500 | 4.0s |
| `gemini-2.5-flash-lite-preview` | 15 | 500 | 4.0s |

## 🔧 Funcionalidades del Sistema

### 1. **Tracking Automático**
- ✅ Registra cada solicitud API automáticamente
- ✅ Cuenta solicitudes por minuto y por día
- ✅ Limpia datos antiguos (>24h) automáticamente
- ✅ Almacena datos en `usage_data.json`

### 2. **Monitoreo en Tiempo Real**
- ✅ Muestra estado antes de cada sesión
- ✅ Actualiza estado después de cada consulta
- ✅ Comando `usage` para verificar estado actual

### 3. **Optimización Inteligente**
- ✅ Delays calculados para maximizar throughput
- ✅ Recomendaciones de modelos con más capacidad
- ✅ Alertas cuando se acercan los límites

## 🚀 Comandos Disponibles

### En el programa principal:
```bash
python main.py
```
- Tipo `usage`, `uso`, `status`, o `estado` para ver el estado actual
- El estado se muestra automáticamente después de cada consulta

### Script independiente:
```bash
python check_usage.py
```
- Verifica el estado sin iniciar el agente principal

### Con orchestrator:
```bash
python debug_agent.py
```
- Muestra resumen completo al final de todas las tareas

## 📊 Interpretación del Resumen

```
📊 RESUMEN DE USO DE MODELOS - CAPA GRATUITA
================================================================================

🤖 gemini-2.5-flash
   📈 Por minuto: 2/10 (quedan 8)
   📅 Diario: 45/500 (quedan 455)
   ✅ Estado: Disponible para nuevas solicitudes
   📊 Eficiencia diaria: 9.0%

📈 RESUMEN GENERAL:
   Total solicitudes hoy: 127
   Capacidad total diaria: 3500
   Eficiencia general: 3.6%
```

### Significado de los indicadores:
- **📈 Por minuto**: Uso en la última ventana de 60 segundos
- **📅 Diario**: Uso en las últimas 24 horas
- **✅/❌ Estado**: Si puede hacer nuevas solicitudes
- **⏰ Próxima disponibilidad**: Cuándo estará disponible si está bloqueado
- **📊 Eficiencia**: Porcentaje del límite diario utilizado

## 💡 Estrategias de Optimización

### 1. **Distribución de Carga**
- Usa diferentes modelos para diferentes tareas
- `gemini-2.0-flash` para tareas generales (más capacidad diaria)
- `gemini-2.5-flash` para tareas complejas (mejor calidad)

### 2. **Timing Inteligente**
- Respeta los delays automáticos
- Usa el comando `usage` antes de tareas grandes
- Planifica investigaciones profundas cuando hay más capacidad

### 3. **Monitoreo Continuo**
- Revisa el estado después de cada sesión
- Ajusta la estrategia según la capacidad restante
- Usa `check_usage.py` para planificación

## 🎯 Recomendaciones por Capacidad

| Capacidad Restante | Estrategia |
|-------------------|------------|
| >50 solicitudes | ✅ Investigación profunda, múltiples agentes |
| 20-50 solicitudes | ⚠️ Uso moderado, tareas importantes |
| <20 solicitudes | 🚨 Solo tareas críticas, un agente |

## 📁 Archivos del Sistema

- `usage_tracker.py`: Clase principal de tracking
- `usage_data.json`: Datos de uso (se crea automáticamente)
- `check_usage.py`: Script de verificación independiente
- `config.yaml`: Configuración con límites reales

## 🔄 Mantenimiento

El sistema es automático, pero puedes:
- Borrar `usage_data.json` para resetear contadores
- Ajustar límites en `config.yaml` si cambian
- Revisar logs en caso de problemas

¡El sistema está optimizado para sacar el máximo provecho de la capa gratuita! 🚀