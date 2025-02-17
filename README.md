# **Flood Evacuation Assistance System : FlowAway**

This project was developed during the **AI Action Summit Hackathon**, held on February 15-16, 2025, at Doctolib, in partnership with Back Market, Mistral AI, Nvidia, RAISE Summit, Scaleway, SIA Partners, and Sweep. The event brought together over a hundred participants to tackle challenges related to health and the environment under the theme **"One Health"**.

Our team participated in the **health track**, made it to the **finals**, and ranked **4th out of 26 teams**.

## **Context**

Floods pose a significant threat to human safety and urban infrastructure. Ensuring efficient and timely evacuation is crucial to minimizing casualties and property damage. Our project provides an **AI-powered** evacuation assistance system that helps people navigate safely during floods by dynamically adjusting routes based on real-time water level predictions.

## **Project Overview**

Our solution is a **web-based evacuation assistance tool** that guides users to the nearest safe zone while avoiding flooded roads. The system is built around three core components:

1. **Flood Prediction Model**: Using **XGBoost**, we forecast water levels based on meteorological and hydrological data.
2. **Graph-Based City Road Network**: We construct a **graph** of the city's streets and dynamically remove flooded roads.
3. **Optimal Route Calculation**: The safest and shortest path to an evacuation point is computed using graph traversal algorithms.
4. **Web Application for Navigation**: A real-time, interactive web app allows users to input their location and receive updated evacuation routes.

## **Repository Structure**

- `model/` – Code and scripts for training the flood prediction model.
- `WebApp/` – Contains the front-end and back-end of the web application.
- `graph/` – Contains the Jupyter notebook for road graph creation and manipulation.
- `presentation.pdf` – Detailed slides explaining the project's methodology.
- `requirements.txt` – List of required Python dependencies.

## **Installation & Usage**

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/saimeur/AI-Summit-Hackathon.git
   cd AI-Summit-Hackathon
   ```

2. **Install Dependencies**:

   Ensure you have **Python 3.7 or later** installed.

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Web Application**:

   ```bash
   cd WebApp
   python app.py
   ```

   The application will be accessible at **`http://localhost:5000`**.
