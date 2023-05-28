.PHONY: clean_cache lint format check test sync_data_to_s3 sync_data_from_s3 create_env update_env remove_env activate_env deactivate_env create_tile_index_parquet create_tile_index_gpkg

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
# CODE MANAGEMENT                                                               #
#################################################################################

## Delete all compiled Python files
clean_cache:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint src code and notebooks with flake8
lint:
	flake8 --config .flake8 src notebooks tests

## Format src code and notebooks with isort & black
format:
	isort src notebooks tests
	black src notebooks tests

## Format and lint src code and notebooks
check: format lint

## Run unit tests with pytest
test: check
	pytest tests

#################################################################################
# DATA MANAGEMENT                                                               #
#################################################################################

## Upload data to S3. Pass dry-run=False to preform permanent sync to remote.
sync_data_to_s3:
ifeq (False,$(dry-run))
	rclone sync --progress ./data $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET)
else
	rclone sync --dry-run ./data $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET)
endif

## Download data from S3. Pass dry-run=False to preform permanent sync from remote.
sync_data_from_s3:
ifeq (False,$(dry-run))
	rclone sync --progress $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET) ./data
else
	rclone sync --dry-run $(RCLONE_REMOTE_CONFIG_NAME):/$(BUCKET) ./data 
endif

#################################################################################
# ENVIRONMENT MANAGEMENT                                                        #
#################################################################################

## Set up the conda environment
create_env:
ifeq (True,$(HAS_MAMBA))
	@echo "Detected mamba, creating mamba environment."
	mamba env create --name $(PROJECT_NAME) --file environment.yml
else
ifeq (True,$(HAS_CONDA))
	@echo "mamba not found, falling back to conda."
	conda env create --name $(PROJECT_NAME) --file environment.yml
else
	$(error Neither mamba or conda was found. Install mamba or conda before continuing.)
endif
endif

## Update the conda environment to reflect changes to environment.yml
update_env:
ifeq (True,$(HAS_MAMBA))
	@echo "Detected mamba, updating mamba environment."
	mamba env update --name $(PROJECT_NAME) --file environment.yml --prune
else
ifeq (True,$(HAS_CONDA))
	@echo "mamba not found, falling back to conda."
	conda env update --name $(PROJECT_NAME) --file environment.yml --prune
else
	$(error Neither mamba or conda was found. Install mamba or conda before continuing.)
endif
endif

## Remove the conda environment
remove_env:
	conda env remove --name $(PROJECT_NAME)

## Displays the command to activate the conda environment
activate_env:
	@echo "To activate this environment, use\n"
	@echo "\t$$ conda activate $(PROJECT_NAME)\n"

## Displays the command to deactivate an active environment
deactivate_env:
	@echo "To deactivate an activate environment, use\n"
	@echo "\t$$ conda deactivate\n"

#################################################################################
# PROCESSING MANAGEMENT                                                         #
#################################################################################

## Make tile index geoparquet from zipped shapefiles
create_tile_index_parquet:
	$(PYTHON_INTERPRETER) src/data/make_tile_index.py \
		--config-file config/tile_index_pipeline.toml \
		--input-dir data/external/usgs/tile_index \
		--output-file data/interim/tile_index.parquet

## Make tile index geopackage from zipped shapefiles
create_tile_index_gpkg:
	$(PYTHON_INTERPRETER) src/data/make_tile_index.py \
		--config-file config/tile_index_pipeline.toml \
		--input-dir data/external/usgs/tile_index \
		--output-file data/interim/tile_index.gpkg

## Create rasters from point clouds
create_rasters_from_points:
	$(PYTHON_INTERPRETER) src/data/make_rasters_from_points.py \
		--aoi-file data/raw/test_point.geojson \
		--tile-index-file data/interim/tile_index.gpkg \
		--output-dir data/processed

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
