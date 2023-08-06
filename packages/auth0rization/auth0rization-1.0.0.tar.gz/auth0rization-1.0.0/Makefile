VENV := ./venv


.PHONY: default
default: test


${VENV}:
	@python3 -m venv venv && \
	. ./venv/bin/activate && \
	python3 -m pip --require-virtualenv install --upgrade pip && \
	python3 -m pip --require-virtualenv install -e '.[dev]'


.PHONY: install
install: ${VENV}
	@. ./venv/bin/activate && \
	python3 -m pip --require-virtualenv install -e '.[dev]'


.PHONY: test
test: ${VENV}
	@. ./venv/bin/activate && \
	coverage erase && \
	coverage run -m unittest discover && \
	coverage report -m


.PHONY: lint
lint: ${VENV}
	@. ./venv/bin/activate && \
	pylint ./src ./tests


.PHONY: build
build: ${VENV}
	@. ./venv/bin/activate && \
	rm -rf dist && \
	python3 -m build


.PHONY: upload_test_pypi
upload_test_pypi: build
	@. ./venv/bin/activate && \
	python3 -m twine upload --repository testpypi ./dist/*


.PHONY: upload_pypi
upload_pypi: build
	@. ./venv/bin/activate && \
	python3 -m twine upload ./dist/*


.PHONY: clean
clean:
	git clean -dfx


.PHONY: help
help:
	@echo "Targets:"
	@echo "   test"
	@echo "      Test python module."
	@echo "   lint"
	@echo "      Lint python module."
	@echo "   build"
	@echo "      Build wheel file for python module."
	@echo "   upload_pypi"
	@echo "      Upload wheel to PyPi."
	@echo "   upload_test_pypi"
	@echo "      Upload wheel to TestPyPi."
	@echo "   clean"
	@echo "      Clean repo of artifacts."
