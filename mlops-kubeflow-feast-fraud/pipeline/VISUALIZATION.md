# How to visualize this pipeline

## A) From the workshop notebook (integrated)

Section **3** in [`notebooks/WORKSHOP.ipynb`](../notebooks/WORKSHOP.ipynb):

1. **Clickable link** to the Pipelines UI — hostname from `oc get route ml-pipeline-ui -n kubeflow` (configurable via `KFP_ROUTE_NAME` / `KFP_UI_NAMESPACE` in the config cell).
2. **In-notebook DAG** — `networkx` + `matplotlib` schematic for the smoke pipeline (one `@dsl.component`).
3. **Optional API submit** — set `SUBMIT_KFP_RUN = True` to create a run with `kfp.Client(..., existing_token=oc whoami -t)` and then open the run’s **Graph** in the UI.

## B) Kubeflow Pipelines UI (recommended when KFP is installed)

The compiled package [`fraud_workshop_pipeline.yaml`](fraud_workshop_pipeline.yaml) is a **KFP v2** pipeline. After your cluster has **Kubeflow Pipelines** (or **OpenShift AI Data Science Pipelines**):

1. Open the **Pipelines** UI in your platform (URL from `oc get routes -A | grep -i pipeline` or your admin docs).
2. **Upload pipeline** → select `fraud_workshop_pipeline.yaml`.
3. **Create run** (any parameters are empty for this smoke pipeline).
4. Open the run → **Graph** / **DAG** / **Visualizations** tab (wording depends on version).

That view is the standard way to see **dependencies**, **step order**, and **run status** per task.

## C) No KFP server yet (static diagram)

The current smoke pipeline has **one component** (`workshop_hello`). Logical shape:

```mermaid
flowchart LR
  start([Start]) --> hello[workshop_hello]
  hello --> end([End])
```

When you add more `@dsl.component` steps and wire them in `@dsl.pipeline`, this graph grows; the **KFP UI** will reflect that automatically after recompile.

## D) From Python (optional)

After `pip install kfp`:

```bash
python pipeline/fraud_workshop_pipeline.py
```

This refreshes `fraud_workshop_pipeline.yaml`. The **SDK** does not render the v2 IR as a graph; use the **notebook** schematic (`networkx`/`matplotlib`) plus the **UI** for the full interactive DAG.

## E) Third-party / IDE

Some IDEs and MLOps products can import KFP YAML or connect to the API server to show graphs. Those are distribution-specific.
