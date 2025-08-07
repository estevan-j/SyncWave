#!/bin/bash

echo "🎵 Iniciando Music Service..."

# Función para registrar en Consul (opcional y en segundo plano)
register_in_consul() {
    echo "📋 Verificando disponibilidad de Consul..."
    
    # Intentar solo 3 veces, 5 segundos cada uno
    for i in {1..3}; do
        if curl -f http://consul:8500/v1/status/leader 2>/dev/null; then
            echo "✅ Consul disponible - Registrando servicio..."
            curl -X PUT http://consul:8500/v1/agent/service/register \
                -d '{
                    "ID": "music-service",
                    "Name": "music-service",
                    "Tags": ["music", "api", "microservice"],
                    "Address": "music-service",
                    "Port": 5000,
                    "Check": {
                        "HTTP": "http://music-service:5000/health",
                        "Interval": "10s"
                    }
                }' 2>/dev/null && echo "✅ Music Service registrado en Consul" || echo "⚠️ Error al registrar en Consul"
            return 0
        fi
        echo "⏳ Intento $i/3 - Consul no disponible, esperando..."
        sleep 5
    done
    
    echo "ℹ️ Consul no disponible después de 15 segundos"
    echo "🚀 Continuando sin Service Discovery..."
}

# Ejecutar registro en segundo plano (no bloquea el inicio del servicio)
register_in_consul &

# Iniciar el servicio inmediatamente
echo "🚀 Iniciando Music Service en puerto 5000..."
python run.py
