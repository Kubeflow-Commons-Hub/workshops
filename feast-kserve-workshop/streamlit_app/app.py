import streamlit as st
import pandas as pd
import json
import time
import traceback
import requests

st.set_page_config(page_title="Feast Remote Tester", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .test-pass { padding: 12px 16px; border-left: 5px solid #00e676; background-color: #1a2e1a; border-radius: 5px; margin: 10px 0; color: #c8e6c9; }
    .test-fail { padding: 12px 16px; border-left: 5px solid #ff5252; background-color: #2e1a1a; border-radius: 5px; margin: 10px 0; color: #ffcdd2; }
    .test-header { font-size: 1.2em; font-weight: bold; }
    h1, h2, h3, p, label, .stMarkdown { color: #e0e0e0 !important; }
    .stTextInput label, .stNumberInput label { color: #b0bec5 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Feast Remote Access Tester")
st.markdown("Validate that your Feast servers are reachable from this pod.")

st.divider()

col1, col2 = st.columns(2)
with col1:
    registry_url = st.text_input(
        "Registry Service (gRPC)",
        value="feast-registry-service.mlops-workshop.svc.cluster.local:6567",
        help="Format: host:port (no http://)"
    )
with col2:
    offline_host = st.text_input(
        "Offline Service Host (Arrow Flight)",
        value="feast-offline-service.mlops-workshop.svc.cluster.local",
    )
    offline_port = st.number_input("Offline Service Port", value=8815, min_value=1, max_value=65535)

online_url_parts = registry_url.replace("feast-registry-service", "feast-service").replace(":6567", "")
online_url = st.text_input(
    "Online Service (REST) — auto-derived, edit if needed",
    value=f"http://{online_url_parts}:6566",
)

st.divider()

if st.button("🚀 Run Feast Tests", type="primary", use_container_width=True):

    results = []

    st.subheader("Test 1: Registry Connection (gRPC)")
    t1_start = time.time()
    try:
        from feast import FeatureStore, RepoConfig

        config = RepoConfig(
            project="fraud_detection",
            provider="local",
            registry={"registry_type": "remote", "path": registry_url},
            offline_store={"type": "remote", "host": offline_host, "port": int(offline_port)},
            online_store={"type": "sqlite", "path": "/tmp/feast_test_online.db"},
            entity_key_serialization_version=3,
        )
        store = FeatureStore(config=config)

        feature_views = store.list_feature_views()
        t1_dur = time.time() - t1_start

        if len(feature_views) > 0:
            st.markdown(f'<div class="test-pass"><span class="test-header">✅ PASS</span> — Found {len(feature_views)} feature view(s) in {t1_dur:.2f}s</div>', unsafe_allow_html=True)
            for fv in feature_views:
                st.markdown(f"**{fv.name}**: {[f.name for f in fv.features]}")
            results.append(("Registry", True))
        else:
            st.markdown(f'<div class="test-fail"><span class="test-header">⚠️ WARNING</span> — No feature views found ({t1_dur:.2f}s)</div>', unsafe_allow_html=True)
            results.append(("Registry", False))
    except Exception as e:
        t1_dur = time.time() - t1_start
        st.markdown(f'<div class="test-fail"><span class="test-header">❌ FAIL</span> — {str(e)[:200]} ({t1_dur:.2f}s)</div>', unsafe_allow_html=True)
        with st.expander("Full Error Traceback", expanded=True):
            st.code(traceback.format_exc(), language="text")
        results.append(("Registry", False))

    st.divider()

    st.subheader("Test 2: Historical Feature Fetch (Arrow Flight)")
    t2_start = time.time()
    try:
        entity_df = pd.DataFrame({
            "entity_id": [57618, 145325, 115180, 90287, 143563],
            "event_timestamp": pd.to_datetime([
                "2025-01-02", "2025-01-22", "2025-03-29", "2025-05-20", "2025-01-15",
            ]),
        })

        features = store.get_historical_features(
            entity_df=entity_df,
            features=[
                "fraud_features:distance_from_home",
                "fraud_features:distance_from_last_transaction",
                "fraud_features:ratio_to_median_purchase_price",
                "fraud_features:repeat_retailer",
                "fraud_features:used_chip",
                "fraud_features:used_pin_number",
                "fraud_features:online_order",
            ],
        )

        result_df = features.to_df()
        t2_dur = time.time() - t2_start

        non_null = result_df.drop(columns=["entity_id", "event_timestamp"]).notna().sum().sum()
        total = result_df.drop(columns=["entity_id", "event_timestamp"]).size

        if result_df.shape[0] > 0 and non_null > 0:
            st.markdown(f'<div class="test-pass"><span class="test-header">✅ PASS</span> — {result_df.shape[0]} rows, {result_df.shape[1]} columns, {non_null}/{total} values populated ({t2_dur:.2f}s)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="test-fail"><span class="test-header">⚠️ WARNING</span> — Got {result_df.shape[0]} rows but {non_null}/{total} non-null values ({t2_dur:.2f}s)</div>', unsafe_allow_html=True)

        st.dataframe(result_df, use_container_width=True)
        results.append(("Historical Features", non_null > 0))
    except Exception as e:
        t2_dur = time.time() - t2_start
        st.markdown(f'<div class="test-fail"><span class="test-header">❌ FAIL</span> — {str(e)[:200]} ({t2_dur:.2f}s)</div>', unsafe_allow_html=True)
        with st.expander("Full Error Traceback", expanded=True):
            st.code(traceback.format_exc(), language="text")
        results.append(("Historical Features", False))

    st.divider()

    st.subheader("Test 3: Online Feature Fetch (REST)")
    t3_start = time.time()
    try:
        payload = {
            "features": [
                "fraud_features:distance_from_home",
                "fraud_features:distance_from_last_transaction",
                "fraud_features:ratio_to_median_purchase_price",
            ],
            "entities": {"entity_id": [57618]},
        }
        resp = requests.post(f"{online_url}/get-online-features", json=payload, timeout=10)
        t3_dur = time.time() - t3_start

        if resp.status_code == 200:
            st.markdown(f'<div class="test-pass"><span class="test-header">✅ PASS</span> — HTTP {resp.status_code} ({t3_dur:.2f}s)</div>', unsafe_allow_html=True)
            st.json(resp.json())
        else:
            st.markdown(f'<div class="test-fail"><span class="test-header">❌ FAIL</span> — HTTP {resp.status_code} ({t3_dur:.2f}s)</div>', unsafe_allow_html=True)
            st.code(resp.text)
        results.append(("Online Features", resp.status_code == 200))
    except Exception as e:
        t3_dur = time.time() - t3_start
        st.markdown(f'<div class="test-fail"><span class="test-header">❌ FAIL</span> — {str(e)[:200]} ({t3_dur:.2f}s)</div>', unsafe_allow_html=True)
        with st.expander("Full Error Traceback", expanded=True):
            st.code(traceback.format_exc(), language="text")
        results.append(("Online Features", False))

    st.divider()
    st.subheader("Summary")
    passed = sum(1 for _, ok in results if ok)
    total_tests = len(results)

    if passed == total_tests:
        st.success(f"🎉 All {total_tests} tests passed! Your Feast remote access is working.")
    else:
        st.warning(f"⚠️ {passed}/{total_tests} tests passed. Check failed tests above.")

    for name, ok in results:
        icon = "✅" if ok else "❌"
        st.write(f"{icon} {name}")
