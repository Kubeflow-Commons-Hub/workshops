# Pinned versions (facilitator: update after dry-run)

Copy tested digests/tags into your facilitator Brain notes; attendees use defaults below unless you publish overrides.

| Component | Version / image | Notes |
|-----------|-----------------|--------|
| Kubernetes / OpenShift | Your cluster | CPU-only; no `nvidia.com/gpu` in workshop YAML |
| Kubeflow Trainer CRD | `trainer.kubeflow.org/v1alpha1` | Must match your Training Operator / Trainer install |
| `ClusterTrainingRuntime` | `torch-distributed` | [Upstream manifest](https://github.com/kubeflow/training-operator/blob/master/manifests/base/runtimes/torch_distributed.yaml) |
| TrainJob training image | `public.ecr.aws/docker/library/python:3.12-slim-bookworm` + `pip install torch pandas` (CPU index) | Use ECR public mirror to reduce Docker Hub rate limits on shared clusters |
| Feast | `feast` CLI **0.38.x–0.40.x** (example) | Align `feast_repo` with your `pip install feast` in notebook image |
| Kubeflow Pipelines SDK | `kfp>=2.5,<3` | Used to compile `pipeline/fraud_workshop_pipeline.py` |
| Python (notebook) | 3.10+ | |

After validation, add a row: **TrainJob image digest** `pytorch/pytorch@sha256:…` for air-gapped clusters.
