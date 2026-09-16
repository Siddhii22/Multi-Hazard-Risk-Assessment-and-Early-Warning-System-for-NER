"""Run audit, final-dataset preprocessing, EDA, and model identification."""

from src.data_audit import main as audit
from src.preprocessing.pipeline import main as preprocess
from src.eda.report import main as run_eda
from src.model_identification import main as identify_models


if __name__ == "__main__":
    for step in (audit, preprocess, run_eda, identify_models):
        if step() != 0:
            raise SystemExit(1)