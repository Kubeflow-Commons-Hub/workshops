# Cluster setup — workshop dependencies

## What this cluster has (admin install summary)

| Component | Namespace | Notes |
|-----------|-----------|--------|
| **Kubeflow Trainer v2** | `kubeflow-trainer` | Helm chart `kubeflow-trainer` (v2.1.0) + JobSet dependency; **`ClusterTrainingRuntime/torch-distributed`** installed |
| **Kubeflow Pipelines** | `kubeflow` | Kustomize `platform-agnostic` for **KFP 2.4.0** + **OpenShift fixes** (see below) |
| **Feast (Redis online store)** | `feast` | Bitnami **Redis** (standalone, no auth) for optional `feast materialize` → online |
| **Workshop workloads** | `worshop-example` | `ConfigMap/workshop-training` + **`TrainJob/fraud-workshop-train`** (CPU; validated **Completed**) |

### KFP UI (this cluster)

After `oc expose svc ml-pipeline-ui -n kubeflow`, the console URL is:

```bash
oc get route ml-pipeline-ui -n kubeflow -o jsonpath='https://{.spec.host}{"\n"}'
```

Upload `pipeline/fraud_workshop_pipeline.yaml`, create a run, open the **Graph** tab.

### Feast Redis endpoint (optional, from pods in `worshop-example`)

`redis://feast-redis-master.feast.svc.cluster.local:6379` — point a Feast `feature_store.yaml` **online_store** here if you move off embedded SQLite for teams.

### OpenShift-specific fixes applied (upstream KFP is not ROSA-ready out of the box)

1. **SCC:** `system:serviceaccounts:kubeflow` bound to **`anyuid`** and **`privileged`** so KFP images (UID **1000**, **seccomp** annotations) can run. **Tighten before production** (custom SCC, patches, or OpenShift AI Pipelines instead).
2. **MinIO image:** `gcr.io/ml-pipeline/minio:…` manifest missing → patched Deployment to **`quay.io/minio/minio:RELEASE.2024-05-10T01-41-38Z`**.
3. **MinIO + MySQL volumes:** `securityContext.fsGroup: 1000` on Deployments so PVC mounts are writable.
4. **TrainJob image:** Docker Hub rate limits / bad PyTorch tags → **`public.ecr.aws/docker/library/python:3.12-slim-bookworm`** + `pip install --target /workspace/out/.pypkgs` (see `manifests/trainjob-fraud-workshop.yaml`).
5. **TrainJob volumes:** **Projected** `ConfigMap` (single mount at `/workspace`) — duplicate `volumeMounts` with the same name are invalid.

---

## 1) Namespace-scoped resources (workshop attendees)

```bash
export WORKSHOP_NAMESPACE="worshop-example"   # or your project
./apply-workshop-manifests.sh
```

---

## 2) Install Kubeflow Trainer v2 (cluster admin) — recap

From a checkout of [kubeflow/training-operator](https://github.com/kubeflow/training-operator):

```bash
cd charts/kubeflow-trainer
helm dependency update
helm upgrade --install kubeflow-trainer . \
  --namespace kubeflow-trainer --create-namespace \
  --set runtimes.torchDistributed.enabled=true \
  --set dataCache.enabled=false
```

```bash
oc get clustertrainingruntime torch-distributed
```

---

## 3) Install Kubeflow Pipelines 2.4 (cluster admin) — recap

```bash
export PIPELINE_VERSION=2.4.0
oc apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
oc apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"
```

Then apply the **OpenShift mitigations** in the table above, expose the UI:

```bash
oc expose svc ml-pipeline-ui -n kubeflow
```

---

## 4) Feast — Redis only (optional cluster backing store)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm upgrade --install feast-redis bitnami/redis -n feast --create-namespace \
  --set architecture=standalone --set auth.enabled=false
```

The minimal workshop still runs **`feast apply`** with **local file + SQLite** in the notebook; Redis is for **online** materialization when you extend the lab.

---

## 5) Notebook / Jupyter

Deploy or use your platform’s **Notebook** / **Workbench** with `oc`, `feast`, `pandas`, `pyarrow`, and `kfp`.
