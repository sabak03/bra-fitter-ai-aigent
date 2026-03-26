import streamlit as st

allCups = ["AA","A","B","C","D","DD","E","F","FF","G","H","HH","I","J","JJ","K","KK","L","M","N"]


def adjust_size(band, cup, feedback):
    reasons = []
    style_suggestions = []
    cup_index = allCups.index(cup)
    band_change = 0
    cup_change = 0

    spilling = feedback["spilling_top"] == "Yes" or feedback["spilling_side"] == "Yes"

    if spilling:
        cup_change += 1
        reasons.append("Spilling suggests the cup is too small.")
    if feedback["gore_tacks"] == "No":
        cup_change += 1
        reasons.append("The centre gore not sitting flat suggests the cup may be too small.")

    if feedback["band_rides_up"] == "Yes":
        band_change -= 2
        cup_change += 1
        reasons.append("Band rides up, so a firmer band may fit better.")
    elif feedback["band_too_tight"] == "Yes" and not spilling:
        band_change += 2
        cup_change -= 1
        reasons.append("Band feels tight, so a slightly larger band may help.")

    if feedback["cup_gaping"] == "Yes" and not spilling:
        if feedback["shape"] != "Full on bottom":
            cup_change -= 1
            reasons.append("Gaping suggests the cup may be too large.")

    new_band = band + band_change
    new_cup_index = cup_index + cup_change
    new_cup_index = max(0, min(new_cup_index, len(allCups) - 1))
    new_cup = allCups[new_cup_index]

    changed = (new_band != band) or (new_cup != cup)
    if not changed:
        reasons.append("Your current size looks consistent based on your answers.")

    if feedback["wires_dig"] in ["A little", "Yes"]:
        style_suggestions.append("Try softer-wire or comfort-focused styles.")
    if feedback["support_level"] == "Comfort":
        style_suggestions.append("Try non-wired or softer everyday bras.")
    if feedback["support_level"] == "Lift":
        style_suggestions.append("Try balconette or side-support bras.")
    if feedback["shape"] == "Full on top":
        style_suggestions.append("Try stretch lace upper cups.")
    if feedback["shape"] == "Full on bottom":
        style_suggestions.append("Try plunge or lower-cut styles.")
    if feedback["straps_fall"] == "Yes":
        style_suggestions.append("Try bras with more centred straps.")

    style_suggestions = list(dict.fromkeys(style_suggestions))

    return {
        "original_size": f"{band}{cup}",
        "size": f"{new_band}{new_cup}",
        "band": new_band,
        "cup": new_cup,
        "changed": changed,
        "band_change": band_change,
        "cup_change": cup_change,
        "reasons": reasons,
        "style_suggestions": style_suggestions,
    }


st.title("Bra Fit Agent")

st.subheader("Starting size")
band = st.number_input("Band size", min_value=26, max_value=50, step=2, value=30)
cup = st.selectbox("Cup size", allCups, index=allCups.index("KK"))

st.subheader("Fit questions")
with st.form("fit_form"):
    feedback = {
        "band_rides_up": st.radio("Does the band ride up at the back?", ["No", "A little", "Yes"]),
        "band_too_tight": st.radio("Does the band feel too tight?", ["No", "A little", "Yes"]),
        "spilling_top": st.radio("Do you spill out at the top of the cups?", ["No", "A little", "Yes"]),
        "spilling_side": st.radio("Do you spill out at the sides?", ["No", "A little", "Yes"]),
        "cup_gaping": st.radio("Do the cups gape or wrinkle?", ["No", "A little", "Yes"]),
        "gore_tacks": st.radio("Does the wire in the middle sit flat on your chest?", ["Yes", "No"]),
        "wires_dig": st.radio("Do the wires dig in?", ["No", "A little", "Yes"]),
        "straps_fall": st.radio("Do the straps fall down?", ["No", "Yes"]),
        "support_level": st.selectbox("What matters most?", ["Comfort", "Lift", "Everyday support", "Minimising"]),
        "shape": st.selectbox("Which sounds most like your shape?", ["Not sure", "Full on top", "Full on bottom", "Centre full", "Wide set", "Close set"]),
    }

    submitted = st.form_submit_button("Adjust size")

if submitted:
    result = adjust_size(band, cup, feedback)

    st.subheader("Result")
    if result["changed"]:
        st.success(f"Recommended size: {result['size']}")
    else:
        st.info(f"Suggested size stays the same: {result['size']}")
    st.write(f"Original size: {result['original_size']}")

    st.subheader("Why")
    for reason in result["reasons"]:
        st.write(f"- {reason}")

    st.subheader("Style suggestions")
    if result["style_suggestions"]:
        for suggestion in result["style_suggestions"]:
            st.write(f"- {suggestion}")
    else:
        st.write("No specific style changes suggested.")