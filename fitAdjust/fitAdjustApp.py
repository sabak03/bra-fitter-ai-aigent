"""
Streamlit Frontend for Bra Fit AI Agent

This application provides an interactive user interface for:
- Entering a starting bra size
- Answering fit-related questions
- Receiving size adjustments from a rule-based fit engine (fitAdjust.py)
- Viewing explanations for recommendations
- Generating style suggestions and new sister sizes

The app communicates with the fit engine module to produce
explainable and user-friendly recommendations.

Technologies:
- Streamlit (UI)
- Python rule-based engine (fitAdjust.py)
"""

import streamlit as st
from fitAdjust import allCups, evaluate_fit, get_sister_sizes

st.set_page_config(page_title="Bra Fitter AI Agent", layout="centered")
st.title("Bra Fitter AI Agent")

st.subheader("Starting size")
col1, col2 = st.columns(2)
with col1:
    band = st.number_input("Band size", min_value=26, max_value=50, step=2, value=32)
with col2:
    cup = st.selectbox("Cup size", allCups, index=allCups.index("F"))

st.subheader("Fit questions")
with st.form("fit_form"):
    feedback = {
        "bandRidesUp": st.radio("Does the band ride up at the back?", ["No", "A little", "Yes"]),
        "bandTooTight": st.radio("Does the band feel too tight? (you can't fit two finger comfortable at the back)", ["No", "A little", "Yes"]),
        "topSpillage": st.radio("Do you spill out at the top of the cups?", ["No", "A little", "Yes"]),
        "sideSpillage": st.radio("Do you spill out at the sides?", ["No", "A little", "Yes"]),
        "cupGaping": st.radio("Do the cups gape or wrinkle?", ["No", "A little", "Yes"]),
        "centreWire": st.radio("Does the centre wire sit flat on your chest?", ["Yes", "No"]),
        "wiresDigging": st.radio("Do the wires dig in?", ["No", "A little", "Yes"]),
        "strapsFalling": st.radio("Do the straps fall down?", ["No", "Yes"]),
        "support": st.selectbox("What matters most?", ["Not sure", "Comfort", "Lift", "Everyday support", "Minimising"]),
        "shape": st.selectbox("Which sounds most like your shape?", ["Not sure", "Full on top", "Full on bottom", "Centre full", "Wide set", "Close set"]),
    }
    submitted = st.form_submit_button("Adjust size")

if submitted:
    result = evaluate_fit(band, cup, feedback)
    st.subheader("Result")
    if result.changed:
        st.success(f"Recommended size: {result.recommendedSize}")
    else:
        st.info(f"Suggested size stays the same: {result.recommendedSize}")
    st.write(f"Original size: {result.originalSize}")

    st.subheader("Why")
    for reason in result.reasons:
        st.write(f"- {reason}")

    st.subheader("Style suggestions")
    if result.styleSuggestions:
        for suggestion in result.styleSuggestions:
            st.write(f"- {suggestion}")
    else:
        st.write("No specific style changes suggested.")

    st.subheader("Sister Sizes")
    st.session_state["adjustedBand"] = result.band
    st.session_state["adjustedCup"] = result.cup
    st.session_state["adjustedSize"] = result.recommendedSize
    sister = get_sister_sizes(
        st.session_state["adjustedBand"],
        st.session_state["adjustedCup"],
        st.session_state["adjustedSize"]
    )
    formatted = []
    for s in sister:
        if s == result.recommendedSize:
            formatted.append(f"-> **{s}** <-")
        else:
            formatted.append(s)
    st.write(" - | - ".join(formatted))
