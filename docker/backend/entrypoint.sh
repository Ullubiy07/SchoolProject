#!/usr/bin/env sh

set -o errexit
set -o nounset

readonly cmd="$*"

: "${CREATED_SUPERUSER:=1}"

database_ready () {
  # Check that postgres is up and running on port `5432`:
  dockerize -wait 'tcp://db:5432' -timeout 5s
}

# We need this line to make sure that this container is started
# after the one with postgres:
until database_ready; do
  >&2 echo 'Database is unavailable - sleeping'
done

# It is also possible to wait for other services as well: redis, elastic, mongo
>&2 echo 'Database is up - continuing...'

python manage.py migrate --noinput --run-syncdb

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', 'DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
EOF

fi

# Evaluating passed command (do not touch):
exec $cmd
