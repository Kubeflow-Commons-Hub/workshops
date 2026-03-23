# Workshops

Hands-on, shareable workshop packages for the Kubeflow / MLOps community hub. Each subdirectory is a **self-contained** tree (materials, manifests, notebooks, license) you can zip, clone, or copy into a Jupyter workspace.

## Current workshops

| Directory | Topic | Notes |
|-----------|--------|--------|
| [`mlops-kubeflow-feast-fraud/`](mlops-kubeflow-feast-fraud/) | OSS MLOps on OpenShift: **Feast**, **KFP**, **Trainer v2** (`TrainJob` + `torch-distributed`), CPU-only fraud lab | Start with [`mlops-kubeflow-feast-fraud/README.md`](mlops-kubeflow-feast-fraud/README.md) |

## This repository

This `workshops/` tree is its **own Git repository** (sibling to `meetup-talks/`, which may be cloned separately). To publish:

```bash
cd workshops
git status
git remote add origin <your-git-url>   # first time only
git push -u origin main                  # or master, per your default branch
```

## Contributing a new workshop

Add a new folder under `workshops/<name>/` with its own `README.md`, `LICENSE`, and clear facilitator vs attendee instructions. Prefer **no secrets** in-repo; use placeholders and Brain/private notes for cluster URLs.
