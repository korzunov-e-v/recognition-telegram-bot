#PROJECT_NAME := $(notdir $(CURDIR))

up:
	#docker compose -f docker/app-docker-compose.yml -p $(PROJECT_NAME) up -d --force-recreate
	docker compose -f docker/app-docker-compose.yml up -d --force-recreate

down:
	docker compose -f docker/app-docker-compose.yml down

build:
	docker compose -f docker/app-docker-compose.yml build

build-no-cache:
	docker compose -f docker/app-docker-compose.yml build --no-cache

lint:
	autoflake -r --quiet --config .autoflake.cfg .
	isort .
	black --config .black .
	flake8 .
