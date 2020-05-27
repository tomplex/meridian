.PHONY:

black:
	python -m black meridian/

typecheck:
	mypy meridian

requirements:
	python -m pip install -r requirements.txt -r requirements-dev.txt

tox:
	python -m tox

clean:
	rm -r .coverage meridian.egg-info .pytest_cache .mypy_cache .tox

docs: .PHONY
	sphinx-build -b html docs/ docs/_build/html

publish: clean tox black
	python setup.py upload
