.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = culvert-vision
RCLONE_REMOTE_CONFIG_NAME = CulvertVision
PROJECT_NAME = culvert-vision
PYTHON_INTERPRETER = python3

ifeq (,$(shell conda --version))
HAS_CONDA=False
else
HAS_CONDA=True
endif

ifeq (,$(shell mamba --version))
HAS_MAMBA=False
else
HAS_MAMBA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Make Dataset
data: requirements
	$(PYTHON_INTERPRETER) src/data/make_dataset.py data/raw data/processed

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint src code and notebooks with flake8
lint:
	flake8 --config .flake8 src notebooks

## Format src code and notebooks with isort & black
format:
	isort src notebooks
	black src notebooks

## Format and lint src code and notebooks
check: format lint

## Upload data to S3. Pass dry-run=False to preform permanent sync to remote.
sync_data_to_s3:
ifeq (False,$(dry-run))
	rclone sync ./data $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET)
else
	rclone sync --dry-run ./data $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET)
endif

## Download data from S3. Pass dry-run=False to preform permanent sync from remote.
sync_data_from_s3:
ifeq (False,$(dry-run))
	rclone sync $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET) ./data
else
	rclone sync --dry-run $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET) ./data 
endif

## Set up mamba environment
create_environment:
ifeq (True,$(HAS_MAMBA))
	@echo "Detected mamba, creating mamba environment."
	mamba env create -f environment.yml
else
ifeq (True,$(HAS_CONDA))
	@echo "mamba not found, falling back to conda."
	conda env create -f environment.yml
else
	$(error Neither mamba or conda was found. Install mamba or conda before continuing.)
endif
endif

## Update mamba environment
update_environment:
ifeq (True,$(HAS_MAMBA))
	@echo "Detected mamba, updating mamba environment."
	mamba env update -n $(PROJECT_NAME) -f environment.yml --prune
else
ifeq (True,$(HAS_CONDA))
	@echo "mamba not found, falling back to conda."
	conda env update -n $(PROJECT_NAME) -f environment.yml --prune
else
	$(error Neither mamba or conda was found. Install mamba or conda before continuing.)
endif
endif

## Make tile index geoparquet from zipped shapefiles
tile_index:
	$(PYTHON_INTERPRETER) src/data/make_tile_index.py \
		--config-file config/tile_index_pipeline.toml \
		--input-dir data/external/usgs/tile_index \
		--output-file data/interim/tile_index.parquet

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
