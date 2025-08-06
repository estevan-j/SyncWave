@echo off
echo Deteniendo Grafana...

docker-compose -f docker-compose.monitoring.yml down

echo Grafana detenido.
pause
