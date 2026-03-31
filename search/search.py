"""
Streamlit Frontend for Bra Search

This application allows users to search for bras based on size and style.

Features:
- User input for band and cup size
- Optional style selection (e.g. balconette, plunge, full cup)
- Sends requests to a FastAPI backend service
- Displays results from trusted retailers

The frontend communicates with the backend API to retrieve and display
normalised product data from multiple sources.

Technologies:
- Streamlit (UI)
- FastAPI (backend API)
- Python
"""

import requests
import streamlit as st

allCups = ["AA","A","B","C","D","DD","E","F","FF","G","H","HH","I","J","JJ","K","KK","L","M","N"]

st.title("Find My Bra")
st.subheader("Search by size")
col1, col2 = st.columns(2)
with col1:
    band = st.number_input("Band size", min_value=26, max_value=50, step=2, value=30)
with col2:
    cup = st.selectbox("Cup size", allCups, index=allCups.index("KK"))
style = st.selectbox(
    "Style",
    ["Any", "Plunge", "Full cup", "Non-wired", "Comfort", "Balconette"]
)
size = f"{band}{cup}"

if st.button("Search trusted retailers"):
    with st.spinner(f"Searching trusted retailers for {size}..."):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/search-bras",
                params={"size": size, "style": style},
                timeout=20
            )
            response.raise_for_status()
            st.session_state["retailerResults"] = response.json()
            st.session_state["searchedSize"] = size
            st.session_state["searchedStyle"] = style
        except requests.RequestException as e:
            st.error(f"Could not reach the API: {e}")

if "retailerResults" in st.session_state:
    st.subheader("Trusted retailer results")

    searchedSize = st.session_state.get("searchedSize", size)
    searchedStyle = st.session_state.get("searchedStyle", "Any")
    st.write(f"Showing results for **{searchedSize}**")
    if searchedStyle != "Any":
        st.write(f"Style: **{searchedStyle}**")

    results = st.session_state["retailerResults"]
    if results:
        for item in results:
            st.markdown(f"**{item.get('title', 'No title')}**")
            if item.get("retailer"):
                st.write(f"Retailer: {item['retailer']}")
            if item.get("price"):
                st.write(f"Price: {item['price']}")
            if item.get("url"):
                st.markdown(f"[View product]({item['url']})")
            st.divider()
    else:
        st.info("No trusted retailer matches found.")