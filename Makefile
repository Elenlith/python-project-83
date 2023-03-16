dev:
	poetry run flask --app page_analyzer:app run

install:
	poetry install

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	poetry run flake8 page_analyzer

test:
	poetry run pytest

check:
	make test
	make lint

test-coverage:
	poetry run pytest --cov --cov-report xml
