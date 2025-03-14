#!/bin/bash

# Espera a que la base de datos esté disponible
echo "Esperando a que la base de datos esté lista..."

# Usando wait-for-it para esperar a que MySQL esté listo
wait-for-it.sh db:3306 -t 60

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate

echo "Verificando si el superusuario ya existe..."
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists()" | grep -q 'True'; then
    echo "Creando superusuario..."
    python manage.py createsuperuser --no-input --username ${DJANGO_SUPERUSER_USERNAME} --email ${DJANGO_SUPERUSER_EMAIL}
    echo "Superusuario creado."
else
    echo "El superusuario ya existe."
fi

# Levantar el servidor
exec "$@"
