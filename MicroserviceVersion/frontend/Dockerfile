FROM node:18-alpine

WORKDIR /app

# Copiar package.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 4200

# Comando para desarrollo
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--port", "4200"]
