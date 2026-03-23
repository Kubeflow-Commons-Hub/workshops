"""Layout checks for the shareable workshop folder."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "VERSIONS.md",
    "LICENSE",
    "trainer/train.py",
    "trainer/Dockerfile",
    "trainer/TrainJob.yaml",
    "manifests/trainjob-fraud-workshop.yaml",
    "manifests/workshop-training-configmap.yaml",
    "feast_repo/feature_store.yaml",
    "feast_repo/features/fraud_features.py",
    "feast_repo/data/transactions.csv",
    "pipeline/fraud_workshop_pipeline.py",
    "pipeline/fraud_workshop_pipeline.yaml",
    "notebooks/WORKSHOP.ipynb",
    "scripts/validate_workshop.py",
    "cluster-setup/README.md",
    "cluster-setup/apply-workshop-manifests.sh",
    "pipeline/VISUALIZATION.md",
]


@pytest.mark.parametrize("rel", REQUIRED)
def test_required_files_exist(rel: str) -> None:
    assert (ROOT / rel).is_file(), f"missing {rel}"


def test_trainjob_references_torch_distributed() -> None:
    text = (ROOT / "manifests/trainjob-fraud-workshop.yaml").read_text()
    assert "torch-distributed" in text
    assert "nvidia.com/gpu" not in text
