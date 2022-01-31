test:
	@pipenv run pytest

lint:
	@pipenv run pylint --rcfile=./.pylintrc manen/

isort:
	@pipenv run isort --check-only manen/ tests/
