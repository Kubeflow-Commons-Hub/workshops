# MLOps workshop: Kubeflow + Feast (fraud use case, CPU-only)

This folder lives under the **`workshops/` Git repo** (see [`../README.md`](../README.md) for how to add `origin` and push the whole workshops tree).

Shareable materials for a **60–75 minute** notebook-driven session on OpenShift: **Feast**, **Kubeflow Pipelines**, and **Kubeflow Trainer v2** (`TrainJob` + upstream **`torch-distributed`** `ClusterTrainingRuntime`). **No GPUs** — training uses `pytorch/pytorch:*-cpu` and no `nvidia.com/gpu` requests.

## What attendees need

- A **Notebook** (Kubeflow Notebook or equivalent Jupyter) with **`oc` or `kubectl`** configured for their namespace (in-cluster SA or kubeconfig).
- This **entire folder** available inside the notebook environment (git clone, zip upload, or `oc cp` to the notebook PVC).
- Facilitator has already installed: Kubeflow Trainer (with `torch-distributed` runtime), KFP, Feast-compatible cluster networking as you designed, and optional serving stack.

## Cluster setup (operators + this namespace)

Step-by-step install order, apply script, and what your OpenShift project needs are in **[`cluster-setup/README.md`](cluster-setup/README.md)**.

## Pipeline visualization

- **With Kubeflow Pipelines:** upload [`pipeline/fraud_workshop_pipeline.yaml`](pipeline/fraud_workshop_pipeline.yaml) in the Pipelines UI → create a run → open the **Graph/DAG** view. Details: **[`pipeline/VISUALIZATION.md`](pipeline/VISUALIZATION.md)**.
- **Without KFP:** use the static Mermaid diagram in that doc (smoke pipeline = single step).

## Facilitator prep (summary)

1. Install **Kubeflow Trainer v2** / Training Operator and confirm:

   ```bash
   oc get clustertrainingruntime torch-distributed
   ```

2. Per attendee (or shared lab): **namespace**, **RBAC** to create `ConfigMap`, `TrainJob`, and KFP runs.
3. Pin versions you actually tested in [`VERSIONS.md`](VERSIONS.md) and in your private Brain runbook.
4. Optional: build/push a custom trainer image from [`trainer/Dockerfile`](trainer/Dockerfile); the default lab uses **ConfigMap-mounted** `train.py` + CSV instead.

## Getting materials into the notebook

- **Git:** clone this repo/path into `~/workshop` (or any path).
- **Zip:** upload and unzip in Jupyter file tree.
- **OpenShift:** from your laptop, `oc cp ./mlops-kubeflow-feast-fraud <notebook-pod>:/path/` (exact pod path depends on your Notebook image).

Open [`notebooks/WORKSHOP.ipynb`](notebooks/WORKSHOP.ipynb) and run top to bottom.

## Story (integration)

1. **Feast** — Register features from parquet; same definitions underpin offline training and (conceptually) serving.
2. **Trainer** — `TrainJob` references **cluster** `ClusterTrainingRuntime` `torch-distributed`; **CPU** image and data come from **`podTemplateOverrides`** + `ConfigMap` (upstream runtime’s default CUDA image is **not** used as-is).
3. **KFP** — Compile and submit a minimal pipeline to show orchestration (extend with real steps later).

## Layout

| Path | Purpose |
|------|---------|
| `notebooks/WORKSHOP.ipynb` | Attendee copy-paste path |
| `feast_repo/` | Feast project (CSV → parquet step in notebook before `feast apply`) |
| `manifests/` | `ConfigMap` + `TrainJob` YAML (`REPLACE_NAMESPACE`) |
| `trainer/` | `train.py`, `Dockerfile`, duplicate `TrainJob.yaml` |
| `pipeline/` | KFP v2 DSL — run `python fraud_workshop_pipeline.py` to emit YAML |
| `scripts/validate_workshop.py` | Offline YAML lint |

## Offline validation (CI or laptop)

```bash
cd workshops/mlops-kubeflow-feast-fraud
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/validate_workshop.py
pytest tests/
```

## Sovereignty angle (facilitator talking points)

- Data and feature logic stay on **your** cluster; Feast is the **contract** between training and serving paths.
- Training is a normal **Kubernetes** workload (`TrainJob`), not an opaque SaaS runtime.
- Stack is **OSS** and portable across distributions (install paths differ; concepts stay the same).

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
