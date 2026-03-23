# Cluster setup — workshop dependencies

Your **namespace** can hold ConfigMaps and (once CRDs exist) `TrainJob` objects. **Installing** Kubeflow Trainer and Kubeflow Pipelines requires **cluster-admin** (or an equivalent platform team).

## What was applied on your current cluster

- **Namespace:** `worshop-example` (as reported by `oc projects`).
- **Created:** `ConfigMap/workshop-training` (training script + CSV).
- **Not available yet:** `TrainJob` (`trainer.kubeflow.org/v1alpha1`) — CRD missing → install **Kubeflow Trainer** / Training Operator v2 first.
- **Pipeline UI:** No pipeline-related API resources visible to your user in this sandbox → install **Kubeflow Pipelines** (or **OpenShift AI / RHOAI Data Science Pipelines**) for DAG visualization and runs.

## 1) Namespace-scoped resources (any user with project admin)

From this directory:

```bash
export WORKSHOP_NAMESPACE="worshop-example"   # or your project
./apply-workshop-manifests.sh
```

This applies `workshop-training` ConfigMap and `TrainJob` (the latter succeeds only after Trainer CRDs exist).

## 2) Cluster-scoped: Kubeflow Trainer v2 (cluster admin)

1. Install the **Kubeflow Training Operator** / **Trainer** release that ships **`ClusterTrainingRuntime`** and **`TrainJob`** (see [kubeflow/training-operator](https://github.com/kubeflow/training-operator) Helm or manifests).
2. Confirm the default PyTorch runtime:

   ```bash
   oc get clustertrainingruntime torch-distributed
   ```

3. Grant your workshop namespace SA (or user) RBAC to create `trainjobs` in that namespace.

4. Re-run `./apply-workshop-manifests.sh` and watch the job:

   ```bash
   oc get trainjob,pods -n "$WORKSHOP_NAMESPACE"
   ```

## 3) Cluster-scoped: Kubeflow Pipelines (for runs + **graph** UI)

Install **Kubeflow Pipelines** as documented for your distribution (upstream Kubeflow manifest, **OpenShift AI** component, etc.).

After install, discover the UI route (names vary):

```bash
# Examples — adjust namespace to where KFP / DS Pipelines runs
oc get routes -A | grep -iE 'pipeline|kubeflow|datascience'
```

In the UI:

1. **Upload pipeline** → choose `pipeline/fraud_workshop_pipeline.yaml` (or compile from `.py` in the notebook).
2. **Create run** → open the run → **Graph** (or **DAG**) shows the pipeline structure.

Without a KFP server, see [pipeline/VISUALIZATION.md](../pipeline/VISUALIZATION.md) for static diagrams and options.

## 4) Notebook / Jupyter

Deploy or use your platform’s **Notebook** / **Workbench** so attendees run `WORKSHOP.ipynb` with `oc`, `feast`, `pandas`, `pyarrow`, and optionally `kfp`.

## 5) Feast

The lab uses the **Feast CLI** from the notebook against the **local** `feast_repo` (file/SQLite stores). No cluster operator is strictly required for the minimal path. For team-wide registry/online store, extend with your chosen Feast deployment pattern.
