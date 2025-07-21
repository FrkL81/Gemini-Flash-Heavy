@echo off
echo ========================================
echo SINCRONIZACION CON REPOSITORIO REMOTO
echo ========================================
echo.

echo 1. Inicializando repositorio Git...
git init

echo.
echo 2. Agregando todos los archivos...
git add .

echo.
echo 3. Verificando estado...
git status

echo.
echo 4. Creando commit inicial...
git commit -m "Initial release - Gemini Flash Heavy v1.0.0

🚀 Multi-agent system optimized for Google AI Studio free tier
🎯 Maximizes Gemini model utilization through intelligent orchestration
⚡ Real-time progress monitoring and smart quota management
🛠️ Extensible tool system with auto-discovery
🌍 Spanish language optimization

Based on the original Make It Heavy by @Doriandarko
Adapted for Google AI Studio and Gemini models"

echo.
echo 5. Agregando repositorio remoto...
git remote add origin https://github.com/FrkL81/Gemini-Flash-Heavy.git

echo.
echo 6. Configurando rama principal...
git branch -M main

echo.
echo 7. Subiendo al repositorio remoto...
git push -u origin main

echo.
echo ========================================
echo SINCRONIZACION COMPLETADA!
echo ========================================
pause