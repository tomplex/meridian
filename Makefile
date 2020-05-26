black:
	python -m black meridian/

typecheck:


requirements:
	python -m pip install -r requirements.txt -r requirements-dev.txt

tox:
	python -m tox

clean:
	rm -r .coverage meridian.egg-info

publish: clean tox black
	python setup.py upload
