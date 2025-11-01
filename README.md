docker run \
    --name auth-redis \
    --network auth-bridge-network \
    -p 3333:6379 \
    -d redis:7.2


docker run \
    --name auth-postgres \
    --network auth-bridge-network \
    -v auth-data:/app \
    -p 5555:5432 \
    -e POSTGRES_USER=auth_user \
    -e POSTGRES_PASSWORD=2004 \
    -e POSTGRES_DB=authentication \
    -d postgres:17


docker run \
    --name auth-app \
    --rm  \
    --network auth-bridge-network \
    -p 8000:8000 \
    auth:1.0


docker run \
    --name celery-worker \
    --rm  \
    --network auth-bridge-network \
    auth:1.0 \
    uv run celery --app=src.core.celery.config:celery_app worker -l INFO 


docker run \
    --name celery-beat \
    --rm  \
    --network auth-bridge-network \
    auth:1.0 \
    uv run celery --app=src.core.celery.config:celery_app beat -l INFO 


