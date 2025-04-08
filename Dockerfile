FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /core

# Instala dependencias del sistema necesarias para PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* # Limpieza de caché

# Copia el archivo de requerimientos
COPY requirements.txt /core/
COPY .env /core/

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación al contenedor
COPY . /core/

# Copia el script wait-for-it
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copia el script de entrada
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Exponer el puerto en el que se ejecuta la aplicación (por defecto Django usa el 8000)
EXPOSE 9000

# Comando para correr la aplicación usando el script de entrada
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
