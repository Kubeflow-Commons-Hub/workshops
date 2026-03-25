# MLOps Workshop: Sovereignty & Open Source ML

A 1-hour hands-on workshop demonstrating a sovereign ML pipeline using Feast + KServe on OpenShift.

## Prerequisites

- OpenShift cluster with `oc` CLI configured
- Kubeflow installed
- Cluster admin access (for KServe CRDs)

## Folder Structure

```
techGenieWorkshop/
├── k8s/
│   ├── namespace.yaml          # Workshop namespace
│   ├── postgres.yaml           # Postgres offline store
│   ├── pvc.yaml                # Shared persistent volume
│   ├── jupyter.yaml            # Jupyter pod with all tools
│   ├── jupyter-service.yaml    # Service for Jupyter access
│   ├── jupyter-route.yaml      # OpenShift route for browser access
│   ├── feast-service.yaml      # Service for Feast server
│   ├── load-data-job.yaml      # Job to pre-load fraud data into Postgres
│   ├── kserve-install.sh       # KServe installation script
│   ├── kserve-inferenceservice.yaml  # InferenceService template
│   ├── inference-request.json  # Sample inference request
│   └── inference-input-schema.md  # Feature schema docs
├── feast_repo/
│   ├── feature_store.yaml      # Feast configuration
│   └── features.py             # Feature definitions
├── notebooks/
│   └── workshop.ipynb          # Main workshop notebook
├── README.md
└── TROUBLESHOOTING.md
```

## Quick Start

### Step 1: Create Namespace
```bash
oc apply -f k8s/namespace.yaml
```

### Step 2: Deploy Infrastructure
```bash
oc apply -f k8s/pvc.yaml
oc apply -f k8s/postgres.yaml
oc apply -f k8s/jupyter.yaml
oc apply -f k8s/jupyter-service.yaml
oc apply -f k8s/feast-service.yaml
oc apply -f k8s/jupyter-route.yaml
```

### Step 3: Wait for Pods
```bash
oc get pods -n mlops-workshop -w
```

### Step 4: Load Data into Postgres
```bash
oc apply -f k8s/load-data-job.yaml
oc wait --for=condition=complete job/load-fraud-data -n mlops-workshop --timeout=600s
```

### Step 5: Copy Workshop Files to PVC
Once the Jupyter pod is running:
```bash
JUPYTER_POD=$(oc get pods -n mlops-workshop -l app=jupyter -o jsonpath='{.items[0].metadata.name}')
oc cp feast_repo/ $JUPYTER_POD:/mnt/feast_repo/ -n mlops-workshop
oc cp notebooks/ $JUPYTER_POD:/mnt/notebooks/ -n mlops-workshop
mkdir -p /tmp/models && oc cp /tmp/models $JUPYTER_POD:/mnt/models/ -n mlops-workshop
```

### Step 5: Access Jupyter
```bash
# Via OpenShift Route:
oc get route jupyter-route -n mlops-workshop -o jsonpath='{.spec.host}'

# Or via port-forward:
oc port-forward svc/jupyter-service 8888:8888 -n mlops-workshop
```

Token: `workshop`

### Step 6: Run the Notebook
Open `/mnt/notebooks/workshop.ipynb` in Jupyter and follow the steps.

### Step 7: Install KServe (if needed)
```bash
chmod +x k8s/kserve-install.sh
./k8s/kserve-install.sh
```

### Step 8: Deploy InferenceService
```bash
oc apply -f k8s/kserve-inferenceservice.yaml
```

### Step 9: Test Inference
```bash
curl -X POST http://fraud-detector.mlops-workshop.svc.cluster.local/v1/models/fraud-detector:predict \
  -H "Content-Type: application/json" \
  -d @k8s/inference-request.json
```

## Validation Checklist

- [ ] Namespace exists: `oc get ns mlops-workshop`
- [ ] Postgres is running: `oc get pods -n mlops-workshop -l app=postgres`
- [ ] PVC is bound: `oc get pvc -n mlops-workshop`
- [ ] Jupyter is running: `oc get pods -n mlops-workshop -l app=jupyter`
- [ ] Jupyter is accessible via route/port-forward
- [ ] Data loaded into Postgres (run Section 1 in notebook)
- [ ] `feast apply` succeeds (Section 2)
- [ ] `feast materialize` succeeds (Section 3)
- [ ] Historical features fetched (Section 4)
- [ ] Feast server starts (Section 5)
- [ ] Health check passes (Section 6)
- [ ] KServe controller is running: `oc get pods -n kserve`
- [ ] InferenceService is ready: `oc get inferenceservice -n mlops-workshop`

## Port Reference

| Service | Port | Access |
|---------|------|--------|
| Jupyter Lab | 8888 | Route or port-forward |
| Feast Server | 6566 | feast-service.mlops-workshop.svc.cluster.local |
| Postgres | 5432 | postgres.mlops-workshop.svc.cluster.local |
| KServe Inference | 80 | fraud-detector.mlops-workshop.svc.cluster.local |
