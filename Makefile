test:
	python -m pytest -q

coverage:
	python -m pytest -q --cov=rover --cov-report=term-missing --cov-report=xml:coverage.xml

lint:
	ruff check rover.py tests

docker-build:
	docker build --pull -t mars-rover:local .
