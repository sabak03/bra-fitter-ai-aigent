import streamlit as st

cups = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P"]
double = ["D","F","H","J","K"]
sisters = ["AA","A","B","C","D","DD","E","F","FF","G","H","HH","I","J","JJ","K","KK","L","M","N","O","P"]

def get_basic_size():
    """
    Calculate bra size based on underbust and full bust measurements:

    - Rounds band to nearest even number
    - Converts bust difference into cup size
    - Handles double cup sizes for odd measurements
    """
    # Round odd underbust measurements up to the nearest even number, as bands are typically sold in even sizes
    if under % 2 == 0:
        band = under
        odd = False
    else:
        band = under + 1
        band = band
        odd = True
    cup = full-under
    cup = cups[cup-1]
    # Accounting for half/double cup sizing
    if odd and cup in double:
        cup = cup+cup
    size = str(band)+cup
    return size, band, cup

def get_sister_sizes(band,cup,size):
    """
    Calculate sister sizes:

    - Increases band up or down by 2 and cup sizes up or down by 1
    - Including double cups
    """
    cupIndex = sisters.index(cup)
    # When going down in size band goes up and cup goes down
    # When going up in size cup goes up and band goes down
    sister = [(str(band+4)+sisters[cupIndex-2]),(str(band+2)+sisters[cupIndex-1]),size,(str(band-2)+sisters[cupIndex+1]),(str(band-4)+sisters[cupIndex+2])]
    return sister


# ----------------------------
# Streamlit UI
# ----------------------------

st.title("Bra Fit Agent")

st.subheader("Finding my size")
under = st.number_input("Underbust Measurement(inches)", min_value=24, max_value=50, value=30)
full = st.number_input("Full Bust Measurement(inches)", min_value=24, max_value=100, value=30)

if st.button("Calculate my size"):
    size, band, cup = get_basic_size()
    st.session_state["size"] = size
    st.session_state["band"] = band
    st.session_state["cup"] = cup

if "size" in st.session_state:
    st.write("Your Size:", st.session_state["size"])
    
    if st.button("See Sister Sizes"):
        sister = get_sister_sizes(
            st.session_state["band"],
            st.session_state["cup"],
            st.session_state["size"]
        )
        currentSize = st.session_state["size"]
        formatted = []
        for s in sister:
            if s == currentSize:
                formatted.append(f"-> **{s}** <-")
            else:
                formatted.append(s)

        st.subheader("Sister Sizes")
        st.write(" - | - ".join(formatted))