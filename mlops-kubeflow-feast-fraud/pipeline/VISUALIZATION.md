# How to visualize this pipeline

## A) Kubeflow Pipelines UI (recommended when KFP is installed)

The compiled package [`fraud_workshop_pipeline.yaml`](fraud_workshop_pipeline.yaml) is a **KFP v2** pipeline. After your cluster has **Kubeflow Pipelines** (or **OpenShift AI Data Science Pipelines**):

1. Open the **Pipelines** UI in your platform (URL from `oc get routes -A | grep -i pipeline` or your admin docs).
2. **Upload pipeline** → select `fraud_workshop_pipeline.yaml`.
3. **Create run** (any parameters are empty for this smoke pipeline).
4. Open the run → **Graph** / **DAG** / **Visualizations** tab (wording depends on version).

That view is the standard way to see **dependencies**, **step order**, and **run status** per task.

## B) No KFP server yet (static diagram)

The current smoke pipeline has **one component** (`workshop_hello`). Logical shape:

```mermaid
flowchart LR
  start([Start]) --> hello[workshop_hello]
  hello --> end([End])
```

When you add more `@dsl.component` steps and wire them in `@dsl.pipeline`, this graph grows; the **KFP UI** will reflect that automatically after recompile.

## C) From Python (optional)

After `pip install kfp`:

```bash
python pipeline/fraud_workshop_pipeline.py
```

This refreshes `fraud_workshop_pipeline.yaml`. There is **no built-in matplotlib graph** in the SDK for v2 IR; use the **UI** for interactive DAGs.

## D) Third-party / IDE

Some IDEs and MLOps products can import KFP YAML or connect to the API server to show graphs. Those are distribution-specific.
