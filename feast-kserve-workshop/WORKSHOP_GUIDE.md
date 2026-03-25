# Workshop Guide: Sovereignty & Open Source ML

## Welcome

This is a 1-hour hands-on workshop where you'll build a fraud detection ML pipeline using **Feast** (feature store) and **KServe** (model serving) on OpenShift.

Everything is pre-configured. You just need a browser.

---

## What's Already Set Up For You

- **Postgres** — 600,000 fraud detection transactions pre-loaded
- **Feast** — Feature store with 3 servers running (online, registry, offline)
- **KServe** — Model serving with a trained RandomForest model deployed
- **Jupyter Notebook** — Your workspace with all code ready to run
- **Two Testing Apps** — Streamlit UIs for validating Feast and inference

---

## Step 1: Open Jupyter Notebook (2 min)

1. Open the Jupyter URL provided by the instructor
2. Enter the token: `workshop`
3. Navigate to `/mnt/notebooks/workshop.ipynb`
4. Open it

---

## Step 2: Verify Data in Postgres (3 min)

Run the first three cells in Section 1. You'll see:
- **600,000 rows** in the `fraud_transactions` table
- **11 columns** — entity_id, 7 features, fraud label, 2 timestamps
- **~8.7% fraud rate**
- Feature statistics computed directly in Postgres (no data loaded into memory)

**What you're learning:** The data lives in Postgres. Feast reads from here — you never load the full dataset into Python.

---

## Step 3: Apply Feast Feature Definitions (2 min)

Run Section 2: `feast apply`

This registers:
- An **Entity** (`entity_id`) — the primary key for looking up features
- A **FeatureView** (`fraud_features`) — 7 features from the Postgres table

**What you're learning:** Feast uses a registry to track what features exist and where they come from. We use a SQL registry (Postgres) so any pod in the cluster can discover features.

---

## Step 4: Materialize Features (3 min)

Run Section 3: `feast materialize 2025-01-01T00:00:00 2025-12-31T23:59:59`

This copies feature values from the offline store (Postgres) to the online store (SQLite) for fast lookups.

**What you're learning:** Materialization bridges offline (batch) and online (real-time) feature serving.

---

## Step 5: Fetch Historical Features (5 min)

Run Section 4 (two cells):
1. Build an entity DataFrame — 200 entity_ids with timestamps from Jan–Mar 2025
2. Call `store.get_historical_features()` — Feast joins the entities with their feature values using point-in-time correctness

You'll get a DataFrame with 200 rows and 9 columns (entity_id + timestamp + 7 features).

**What you're learning:** This is exactly what a training pipeline does — ask Feast for the right features at the right time for each training example.

---

## Step 6: Start Feast Servers (3 min)

Run Section 5. This starts three servers inside the notebook pod:

| Server | Port | Protocol | Purpose |
|--------|------|----------|---------|
| Online server | 6566 | REST | Serve features via HTTP |
| Registry server | 6567 | gRPC | Let remote pods discover features |
| Offline server | 8815 | Arrow Flight | Let remote pods fetch historical features |

Run Section 6 to verify all three ports are open and the REST health check returns 200.

**What you're learning:** In production, these servers run as dedicated services. Training jobs and inference services connect to them remotely.

---

## Step 7: Test Remote Feast Access (5 min)

Section 7 shows the remote `feature_store.yaml` that training jobs use:

```yaml
provider: local
registry:
  registry_type: remote
  path: feast-registry-service:6567
offline_store:
  type: remote
  host: feast-offline-service:8815
```

The key insight: **training jobs don't need database credentials**. They connect to Feast servers via k8s Services.

### Test with the Feast Tester App

1. Open the **Feast Tester** URL provided by the instructor
2. The default service URLs are pre-filled
3. Click **"Run Feast Tests"**
4. You should see all 3 tests pass:
   - Registry connection (finds `fraud_features`)
   - Historical feature fetch (5 rows with real values)
   - Online feature fetch (JSON response)

---

## Step 8: Test Model Inference (5 min)

A fraud detection model (RandomForest, 99.9% accuracy) is already deployed via KServe.

### Test with the Inference Tester App

1. Open the **Inference Tester** URL provided by the instructor
2. Try the **Quick Presets**:
   - **Likely Safe** → prediction: `0.0` (legitimate)
   - **Likely Fraud** → prediction: `1.0` (fraudulent)
   - **Edge Case** → see what the model decides
3. Adjust individual features and click **"Predict"** to explore

### Or test from the notebook

Run Section 8 to see the inference JSON format and curl command.

---

## Step 9: Review Inference Input Contract (2 min)

Run Section 8 in the notebook. This shows:
- The exact JSON format KServe expects
- Feature names in order
- A ready-to-use curl command

The 7 features (in order):
1. `distance_from_home`
2. `distance_from_last_transaction`
3. `ratio_to_median_purchase_price`
4. `repeat_retailer`
5. `used_chip`
6. `used_pin_number`
7. `online_order`

The `fraud` label is **never** sent to the model — it's what the model predicts.

---

## Step 10: Cleanup (1 min)

Run the Cleanup cell to stop the Feast servers.

---

## Architecture Summary

```
Postgres (600K rows)
    ↓
Feast (feature store)
    ├── Online Server  :6566  → real-time feature lookup
    ├── Registry       :6567  → feature discovery
    └── Offline Server :8815  → historical features for training
                                    ↓
                            Training Job (remote pod)
                                    ↓
                            model.joblib (RandomForest)
                                    ↓
                            KServe InferenceService
                                    ↓
                            POST /predict → {fraud: 0 or 1}
```

---

## Key Takeaways

1. **Feast separates feature engineering from model training** — define features once, use everywhere
2. **Remote access pattern** — training jobs don't need database credentials, just Feast service URLs
3. **KServe serves models from PVC** — no S3/cloud storage needed for sovereign deployments
4. **Everything runs on OpenShift** — sovereign, open-source, no vendor lock-in
