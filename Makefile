FMT = black
LINT = isort --py 310 --gitignore --profile $(FMT)
SRC_DIR = ./oceantemp
ENV_DIR = ./.env
ENV_SCRIPT = . $(ENV_DIR)/bin/activate

CODE = $$(find $(SRC_DIR) -name '*.py')

$(ENV_DIR):
	@printf "[\e[34m%s\e[00m] %s\n" "ENV" "Creating environment"
	@( \
		python3 -m venv $(ENV_DIR); \
		$(ENV_SCRIPT); pip install -r requirements.txt; \
	)

environment: $(ENV_DIR)

lint: environment
	@printf "[\e[34m%s\e[00m] %s\n" "LINT" "Linting source directory..."
	@$(LINT) --virtual-env $(ENV_DIR) --src $(SRC_DIR) $(SRC_DIR)/.

format: environment
	@printf "[\e[34m%s\e[00m] %s\n" "FMT" "Formatting source directory..."
	@$(FMT) $(SRC_DIR)/.

.PHONY: env run clean

env: environment

run: $(ENV_DIR)
	@$(ENV_SCRIPT); python3 oceantemp/main.py

clean: lint format
