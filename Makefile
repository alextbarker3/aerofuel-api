.PHONY: install bootstrap run test openapi docker

install:
	python -m pip install -r requirements.txt

bootstrap:
	python scripts/bootstrap.py

run:
	uvicorn app.main:app --reload

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q

openapi:
	python scripts/generate_openapi.py

docker:
	docker compose up --build
