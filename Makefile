all: coverage

test:
	pytest

coverage:
	coverage run --source deveba -m pytest
	coverage html
