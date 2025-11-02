.PHONY: all ingest features eda model report

all: ingest features eda model report

ingest:
	python -m src.ingest_nhanes --config config.yaml --vars var_map.yaml

features:
	python -m src.build_features --config config.yaml

eda:
	jupyter nbconvert --to notebook --execute notebooks/01_ingest_clean.ipynb --output 01_ingest_clean.ipynb

model:
	python -m src.run_models --config config.yaml

report:
	jupyter nbconvert --to notebook --execute notebooks/03_summary.ipynb --output 03_summary.ipynb
