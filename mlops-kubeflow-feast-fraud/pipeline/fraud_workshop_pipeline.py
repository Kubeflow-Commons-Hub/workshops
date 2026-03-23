"""Minimal Kubeflow Pipelines v2 pipeline — integration smoke for the workshop."""
from pathlib import Path

from kfp import compiler, dsl


@dsl.component(base_image="python:3.11-slim-bookworm")
def workshop_hello() -> str:
    print("fraud workshop: KFP integration step")
    return "ok"


@dsl.pipeline(
    name="fraud-workshop-pipeline",
    description="Minimal CPU-only pipeline for MLOps workshop (extend with real steps).",
)
def fraud_workshop_pipeline():
    workshop_hello()


if __name__ == "__main__":
    out = Path(__file__).with_suffix(".yaml")
    compiler.Compiler().compile(
        pipeline_func=fraud_workshop_pipeline,
        package_path=str(out),
    )
    print(f"Wrote {out}")
