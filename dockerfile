# Usar una imagen de Python liviana
FROM python:3.9-slim

# Crear carpeta de trabajo
WORKDIR /app

# Copiar el archivo de requisitos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos
COPY . .

# Comando para ejecutar tu servidor
CMD ["python", "app.py"]