# ChurnGuard: Customer Churn Prediction API

A full-stack machine learning application to predict customer churn. This project uses a Random Forest model served via a FastAPI backend, with an interactive web interface built in Streamlit. The entire backend is containerized with Docker for easy deployment.

---

## 🚀 Key Features

* **Interactive Frontend:** A user-friendly interface built with Streamlit to input customer data.
* **RESTful API:** A robust backend powered by FastAPI to serve model predictions.
* **Machine Learning Model:** A `scikit-learn` Random Forest Classifier trained on synthetic customer data.
* **Containerized:** The backend is fully containerized using Docker for reproducible builds and simple deployment.
* **Cloud-Ready:** Designed for easy deployment on platforms like Render.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** FastAPI, Pydantic, Uvicorn
* **ML & Data:** Scikit-learn, Pandas, Joblib
* **Deployment:** Docker, Render

[Image of logos for Streamlit, FastAPI, and Docker]

---

## 🏛️ Project Architecture

The application is split into two main components: a frontend web app and a backend API.

1.  The **Streamlit Frontend** captures user input through a web form.
2.  When the user clicks "Predict," the frontend sends the data as a JSON payload to the FastAPI backend.
3.  The **FastAPI Backend** receives the data, validates it using Pydantic, preprocesses it, and feeds it to the loaded machine learning model.
4.  The model returns a prediction and probability, which the API then sends back to the frontend.
5.  The Streamlit app displays the received prediction to the user.

---
