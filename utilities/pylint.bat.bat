@echo off
pylint *.py **/*.py > utilities/pylint-results.txt
type utilities\pylint-results.txt
