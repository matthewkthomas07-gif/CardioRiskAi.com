"""Simple web page to try the heart risk AI (no coding needed)."""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

MODEL_PATH = Path(__file__).parent / "cardio_rf_model.pkl"
SCALER_PATH = Path(__file__).parent / "cardio_scaler.pkl"

st.set_page_config(page_title="Heart Risk Checker", page_icon="❤️", layout="centered")
st.title("❤️ Heart Risk Checker")
st.caption("School project demo — not real medical advice.")

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    st.error(f"Could not load the AI files. Ask an adult to check the .pkl files. ({e})")
    st.stop()

st.subheader("Patient info")
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age (years)", min_value=1, max_value=120, value=55)
    sex = st.selectbox("Sex (0 = female, 1 = male)", options=[0, 1], index=1)
    chest_pain = st.selectbox(
        "Chest pain type (0–3)",
        options=[0, 1, 2, 3],
        index=2,
        help="0 = none, higher = more serious types in the dataset.",
    )
    systolic_bp = st.number_input("Systolic blood pressure", min_value=80, max_value=250, value=140)
    cholesterol = st.number_input("Cholesterol", min_value=100, max_value=600, value=240)
    fasting_bs = st.selectbox("High fasting blood sugar? (0 = no, 1 = yes)", options=[0, 1], index=0)

with col2:
    resting_ecg = st.selectbox("Resting ECG result (0–2)", options=[0, 1, 2], index=1)
    max_hr = st.number_input("Max heart rate reached", min_value=60, max_value=220, value=150)
    exercise_angina = st.selectbox("Exercise angina? (0 = no, 1 = yes)", options=[0, 1], index=0)
    oldpeak = st.number_input("Oldpeak (ST depression)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    slope = st.selectbox("Slope of peak exercise ST (0–2)", options=[0, 1, 2], index=2)
    num_vessels = st.selectbox("Major vessels colored by fluoroscopy (0–3)", options=[0, 1, 2, 3], index=0)
    thal = st.selectbox("Thalassemia test result (1–3)", options=[1, 2, 3], index=2)

if st.button("Check risk", type="primary"):
    row = {
        "Age": age,
        "Sex": sex,
        "ChestPain": chest_pain,
        "SystolicBP": systolic_bp,
        "Cholesterol": cholesterol,
        "FastingBS": fasting_bs,
        "RestingECG": resting_ecg,
        "MaxHR": max_hr,
        "ExerciseAngina": exercise_angina,
        "Oldpeak": oldpeak,
        "Slope": slope,
        "NumVessels": num_vessels,
        "Thal": thal,
    }
    df = pd.DataFrame([row])
    scaled = scaler.transform(df)
    risk = model.predict_proba(scaled)[0][1] * 100

    st.success(f"Estimated cardiovascular risk: **{risk:.1f}%**")
    if risk < 30:
        st.info("Low in this demo model — still talk to a doctor for real health questions.")
    elif risk < 60:
        st.warning("Medium in this demo model.")
    else:
        st.error("High in this demo model — remember this is only a school project tool.")

st.divider()
st.markdown(
    "**Disclaimer:** This app is for learning and science fair demos only. "
    "It does not diagnose disease. Always ask a doctor about real health concerns."
)
