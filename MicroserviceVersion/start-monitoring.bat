@echo off
echo Iniciando Grafana...

docker-compose -f docker-compose.monitoring.yml up -d

echo Esperando que Grafana este listo...
timeout /t 20

echo.
echo ================================
echo   GRAFANA LISTO!
echo ================================
echo URL: http://localhost:3000
echo Usuario: admin
echo Password: admin123
echo ================================
echo.

pause
