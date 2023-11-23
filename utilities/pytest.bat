@echo off
pytest --cov-report term-missing --cov > utilities/pytest-results.txt
type utilities\pytest-results.txt
