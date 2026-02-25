set dotenv-load := true

default:
    @just --list

prod:
    docker compose up --build

prod-d:
    docker compose up --build -d

dev:
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-d:
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

down:
    docker compose down

down-v:
    docker compose down -v

logs:
    docker compose logs -f

ps:
    docker compose ps

restart svc:
    docker compose restart {{svc}}

shell svc:
    docker compose exec {{svc}} /bin/sh

clean:
    docker compose down --rmi local --volumes --remove-orphans
