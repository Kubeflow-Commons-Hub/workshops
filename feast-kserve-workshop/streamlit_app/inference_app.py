import streamlit as st
import json
import traceback
import requests

st.set_page_config(page_title="Fraud Detection Inference", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .pred-fraud { padding: 20px; border-left: 6px solid #ff5252; background-color: #2e1a1a; border-radius: 8px; margin: 16px 0; color: #ffcdd2; font-size: 1.3em; }
    .pred-safe { padding: 20px; border-left: 6px solid #00e676; background-color: #1a2e1a; border-radius: 8px; margin: 16px 0; color: #c8e6c9; font-size: 1.3em; }
    .pred-error { padding: 20px; border-left: 6px solid #ffa726; background-color: #2e2a1a; border-radius: 8px; margin: 16px 0; color: #ffe0b2; }
    h1, h2, h3, p, label, .stMarkdown { color: #e0e0e0 !important; }
    .stNumberInput label, .stTextInput label, .stSelectbox label { color: #b0bec5 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Fraud Detection — Live Inference")
st.markdown("Test your KServe InferenceService by sending transaction data and getting predictions.")

st.divider()

inference_url = st.text_input(
    "KServe Inference URL",
    value="http://fraud-detector-predictor.mlops-workshop.svc.cluster.local/v1/models/fraud-detector:predict",
    help="Full predict endpoint URL for your InferenceService",
)

st.divider()

st.subheader("Transaction Features")

col1, col2, col3 = st.columns(3)

with col1:
    distance_home = st.number_input("Distance from Home", value=57.0, format="%.2f",
                                     help="Distance of transaction from cardholder's home")
    distance_last = st.number_input("Distance from Last Transaction", value=0.53, format="%.4f",
                                     help="Distance from the previous transaction location")
    ratio_median = st.number_input("Ratio to Median Purchase Price", value=1.18, format="%.4f",
                                    help="Transaction amount relative to cardholder's median")

with col2:
    repeat_retailer = st.selectbox("Repeat Retailer", [1.0, 0.0], index=0,
                                    help="1.0 = repeat retailer, 0.0 = new retailer")
    used_chip = st.selectbox("Used Chip", [0.0, 1.0], index=0,
                              help="1.0 = chip used, 0.0 = not used")

with col3:
    used_pin = st.selectbox("Used PIN", [0.0, 1.0], index=0,
                             help="1.0 = PIN used, 0.0 = not used")
    online_order = st.selectbox("Online Order", [1.0, 0.0], index=0,
                                 help="1.0 = online, 0.0 = in-person")

st.divider()

features = [distance_home, distance_last, ratio_median, repeat_retailer, used_chip, used_pin, online_order]
feature_names = ["distance_from_home", "distance_from_last_transaction", "ratio_to_median_purchase_price",
                 "repeat_retailer", "used_chip", "used_pin_number", "online_order"]

col_btn, col_preset = st.columns([2, 3])

with col_preset:
    st.markdown("**Quick Presets:**")
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        if st.button("🟢 Likely Safe", use_container_width=True):
            st.session_state["preset"] = [3.6, 0.69, 0.08, 1.0, 1.0, 1.0, 0.0]
    with pcol2:
        if st.button("🔴 Likely Fraud", use_container_width=True):
            st.session_state["preset"] = [113.6, 0.53, 1.75, 1.0, 0.0, 0.0, 1.0]
    with pcol3:
        if st.button("🟡 Edge Case", use_container_width=True):
            st.session_state["preset"] = [45.0, 5.2, 0.95, 0.0, 0.0, 0.0, 1.0]

if "preset" in st.session_state:
    features = st.session_state.pop("preset")
    st.rerun()

with col_btn:
    predict_clicked = st.button("🔮 Predict", type="primary", use_container_width=True)

if predict_clicked:

    payload = {"instances": [features]}

    st.divider()
    st.subheader("Request")
    st.code(json.dumps(payload, indent=2), language="json")

    st.subheader("Result")

    try:
        resp = requests.post(inference_url, json=payload, timeout=15,
                             headers={"Content-Type": "application/json"})

        if resp.status_code == 200:
            result = resp.json()
            predictions = result.get("predictions", [])

            st.markdown("**Raw Response:**")
            st.code(json.dumps(result, indent=2), language="json")

            if len(predictions) > 0:
                pred = predictions[0]
                if pred == 1.0 or pred == 1:
                    st.markdown(
                        '<div class="pred-fraud">🚨 <b>FRAUD DETECTED</b> — This transaction is predicted as fraudulent.</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="pred-safe">✅ <b>LEGITIMATE</b> — This transaction appears safe.</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("**Feature Summary:**")
                summary_data = {name: [val] for name, val in zip(feature_names, features)}
                summary_data["prediction"] = [pred]
                st.dataframe(summary_data, use_container_width=True)
        else:
            st.markdown(
                f'<div class="pred-error">⚠️ <b>HTTP {resp.status_code}</b></div>',
                unsafe_allow_html=True
            )
            st.code(resp.text, language="text")

    except Exception as e:
        st.markdown(
            f'<div class="pred-error">❌ <b>Request Failed</b> — {str(e)[:300]}</div>',
            unsafe_allow_html=True
        )
        with st.expander("Full Error Traceback", expanded=True):
            st.code(traceback.format_exc(), language="text")
