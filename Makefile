
# Exports environment to requirements.txt
export-conda-env:
	conda env export --no-builds > environment.yml
	pip freeze > requirements.txt

# Installs requirements.txt
install-requirements:
	pip install -r requirements.txt

create-conda-env:
	conda env create -f environment.yml

# Starts MongoDB API
start-mongo:
	cd mongodb_api
	python -m uvicorn mongodb_api.main:app --reload

prepare-commit:
	make export-conda-env
	black . --preview
	isort .
	flake8 .
	git add *
