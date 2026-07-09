# Deployment Guide

This document describes how to deploy the system locally, with Docker Compose, or to cloud staging systems.

## Prerequisites
- Python 3.11+
- Pip package manager
- Docker (optional, for containerised execution)

## Method A: Local Manual Execution

1. **Clone & Navigate**:
   ```bash
   cd Healthcare-Analytics-System
   ```
2. **Environment Setup**:
   Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables Configuration**:
   Create a `.env` file or export variables:
   ```bash
   ORS_API_KEY=your_openrouteservice_key_here
   ```
5. **Run Database Initialization**:
   The system database initializes automatically on startup.
6. **Launch Portals**:
   - **Identity Portal (Flask)**:
     ```bash
     python login/auth_app.py
     ```
   - **Primary Streamlit App**:
     ```bash
     streamlit run app.py
     ```
   Access the Flask Identity portal at `http://localhost:5000` to register accounts or log in.

---

## Method B: Docker Compose (Recommended)

Both Flask and Streamlit apps can be launched in isolated containers using a single command:

1. **Verify Configs**: Ensure `Dockerfile` and `docker-compose.yml` are present in the project root.
2. **Build and Run**:
   ```bash
   docker compose up --build
   ```
3. **Ports exposed**:
   - Identity / Auth Portal: `http://localhost:5000`
   - Primary Streamlit Portal: `http://localhost:8501`

---

## Staging & Production Hosting
- **Secret Protection**: Set `ORS_API_KEY` inside your host provider dashboard (e.g. Heroku config vars, AWS ECS task variables, or Streamlit Cloud Secrets). Do not commit `.env` or `secrets.toml` files with API keys to Git.
- **Port Forwarding**: Ensure port `5000` and `8501` are accessible, or set up an Nginx reverse proxy routing requests properly.
