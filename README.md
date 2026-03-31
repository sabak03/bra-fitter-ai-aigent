# Bra Fit AI Agent (Python Full-Stack Project)

This project combines Python, AI logic, and real-world problem solving to improve bra fitting accuracy and user wellbeing.

A full-stack Python application that helps users:
- Calculate bra size
- Adjust fit using a rule-based AI engine
- Discover products from trusted retailers

This project demonstrates:
- frontend + backend
- intelligent logic design
- Built using Streamlit and FastAPI.

---

## Features

### 1. Size Calculator
- Calculates bra size based on underbust and full bust measurement (in inches)
- Handles cup mapping and band rounding
- Includes sister size recommendations

`size.py`

---

### 2. Fit Adjustment Engine (Rule-Based AI)
- Uses a modular rule engine to analyse fit feedback
- Applies band and cup adjustments based on real world fitting logic
- Includes:
  - Rule weighting (confidence)
  - Conflict resolution
  - Style recommendations

Backend: `fitAdjust/fitAdjust.py`  
Frontend: `fitAdjust/fitAdjustApp.py`

---

### 3. Product Search (FastAPI + Streamlit)
- User inputs size and style
- FastAPI backend searches retailer pages
- Streamlit frontend displays structured results

Backend API: `search/api.py`  
Frontend: `search/search.py`

---

## Tech Stack

- **Python**
- **Streamlit** – frontend UI
- **FastAPI** – backend API
- **BeautifulSoup** – web scraping
- **Requests** – HTTP calls
- **Dataclasses** – structured rule engine design

---

## How to Run

### 1. Install dependencies

```bash
pip install streamlit fastapi uvicorn requests beautifulsoup4
```

### 2. Run Size Calculator

```bash
streamlit run size.py
```

### 3. Run Fit Adjustment App

```bash
streamlit run fitAdjust/fitAdjustApp.py
```

### 4. Run Search API, then Product Search App

```bash
uvicorn search.api:app --reload
streamlit run search/search.py
```

---

## Architecture Overview

User → Streamlit UI → FastAPI → Retailer Search → Structured Results → UI

The project is structured into clear layers:
- **Frontend (Streamlit)** → Handles user input and displays results  
- **Backend (FastAPI)** → Retrieves and processes product data  
- **Logic Engine** → Applies rule-based reasoning for fit/size adjustments and recommendations  

---

## Key Concepts Demonstrated

- Rule-based AI system design  
- Feature engineering from user feedback  
- API development and integration  
- Data normalisation across multiple sources  
- Clean Python architecture  

---

## Why This Project Stands Out

- Not just a UI, it includes real decision-making logic  
- Demonstrates a full-stack Python development  
- Shows understanding of user-driven systems  
- Designed with scalability in mind, including potential for:
  - Machine learning model integration  
  - Retail recommendation engine  
  - Personalised shopping assistant
- Addresses a real world issue affecting women of all ages, where incorrect bra sizing can impact comfort, posture, and overall wellbeing  
- Combines technical problem solving with a practical, user-focused solution that has genuine everyday impact  

---

## Future Improvements

- Add multi-retailer scraping
- Improve search results
- Integrate all Streamlit applications for better user experience
- Introduce caching for faster API responses  
- Replace rule-based engine with ML model (e.g. seq2seq or classifier)  
- Deploy FastAPI backend and Streamlit frontend to cloud  


