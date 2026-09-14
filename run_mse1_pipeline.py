"""Run the reproducible MSE-1 preprocessing and EDA pipeline."""

from src.preprocessing.build_mse1_dataset import main as build_dataset
from src.eda.run_eda import main as run_eda


if __name__ == "__main__":
    if build_dataset() == 0:
        raise SystemExit(run_eda())