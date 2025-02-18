default:
  just --list

up:
  docker-compose up -d

kill:
  docker-compose kill

build:
  docker-compose build

ps:
  docker-compose ps

exec *args:
  docker-compose exec fastapi-starter-template {{args}}

logs *args:
    docker-compose logs {{args}} -f

mm *args:
  docker compose exec fastapi-starter-template alembic revision --autogenerate -m "{{args}}"

migrate:
  docker compose exec fastapi-starter-template alembic upgrade head
tests:
  docker compose exec fastapi-starter-template pytest
downgrade *args:
  docker compose exec fastapi-starter-template alembic downgrade {{args}}

ruff *args:
  docker compose exec fastapi-starter-template ruff {{args}} src
  docker compose exec fastapi-starter-template ruff format src

lint:
  just ruff --fix

backup:
  docker compose exec app_db scripts/backup

# examples:
# "just get-backup dump_name_2021-01-01..backup.gz" to copy particular backup
# "just get-backup" to copy directory (backups) with all dumps
mount-docker-backup *args:
  docker cp app_db:/backups/{{args}} ./{{args}}

restore *args:
    docker compose exec app_db scripts/restore {{args}}
