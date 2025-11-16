BASE_PYTHON=/opt/homebrew/bin/python3.12
help:
	@echo targets are: venv test clean help

venv: ./venv/bin/python3

./venv/bin/python3:
	mkdir -p ./venv
	cd ./venv; $(BASE_PYTHON) -m venv `pwd`
	./venv/bin/pip install openai pydantic

test: ./venv/bin/python3
	./venv/bin/python agent_test.py --verbose "what is 5 + 3 * 2"

clean:
	rm -rf ./venv

.PHONY: help venv test clean
