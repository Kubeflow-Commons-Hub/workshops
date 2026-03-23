# Pinned versions (facilitator: update after dry-run)

Copy tested digests/tags into your facilitator Brain notes; attendees use defaults below unless you publish overrides.

| Component | Version / image | Notes |
|-----------|-----------------|--------|
| Kubernetes / OpenShift | Your cluster | CPU-only; no `nvidia.com/gpu` in workshop YAML |
| Kubeflow Trainer CRD | `trainer.kubeflow.org/v1alpha1` | Must match your Training Operator / Trainer install |
| `ClusterTrainingRuntime` | `torch-distributed` | [Upstream manifest](https://github.com/kubeflow/training-operator/blob/master/manifests/base/runtimes/torch_distributed.yaml) |
| TrainJob training image | `pytorch/pytorch:2.5.1-cpu` | Override in `trainer/TrainJob.yaml` if your registry mirrors |
| Feast | `feast` CLI **0.38.x–0.40.x** (example) | Align `feast_repo` with your `pip install feast` in notebook image |
| Kubeflow Pipelines SDK | `kfp>=2.5,<3` | Used to compile `pipeline/fraud_workshop_pipeline.py` |
| Python (notebook) | 3.10+ | |

After validation, add a row: **TrainJob image digest** `pytorch/pytorch@sha256:…` for air-gapped clusters.
