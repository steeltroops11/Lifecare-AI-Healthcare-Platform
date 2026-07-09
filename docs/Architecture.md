# Architecture Documentation

This document explains the architecture of the Healthcare Analytics System.

## Architecture Overview
The application consists of a dual-framework setup communicating locally via signed query parameters:
1. **Frontend (Streamlit)**: Serves as the primary patient and clinical interface, hosting interactive forms, ML prediction dials, XAI feature contributions, and the Specialist Finder map dashboard.
2. **Identity Portal (Flask)**: A secure portal running on port 5000 that manages account registration, password hashing (PBKDF2/SHA-256), session verification, and simulated Google Sign-in routing.
3. **Database (SQLite)**: A relational database stored locally in `data/healthcare.db` tracking authentication credentials, patient profiles, EHR histories, audit logs, appointments, reminders, and Overpass caching.

## System Workflow Diagram
```
              +----------------------------+
              |   Flask Identity Portal    | <-----+
              |        (Port 5000)         |       |
              +----------------------------+       | Redirect / Auth
                            |                      | parameters
                            v                      |
              +----------------------------+       |
              | Streamlit Patient Portal   | ------+
              |        (Port 8501)         |
              +----------------------------+
                |          |             |
                v          v             v
       +----------+  +-----------+  +-------------------+
       | ML Models|  | Local DB  |  | OpenStreetMap/ORS |
       | (.pkl)   |  | (SQLite)  |  | External APIs     |
       +----------+  +-----------+  +-------------------+
```

## Folder Structure
```
├── app.py                     # Streamlit routing entrypoint
├── requirements.txt           # Dependency definition
├── Dockerfile                 # Multi-stage Docker config
├── docker-compose.yml         # Local container orchestrator
├── data/
│   └── healthcare.db          # SQLite Database
├── model/
│   ├── diabetes_model.pkl     # Random Forest model
│   ├── heart_model.pkl        # Gradient Boosting model
│   ├── kidney_model.pkl       # Random Forest model
│   └── readmission_model.pkl  # Logistic Regression model
├── components/
│   ├── cards.py               # Custom UI card renderers
│   ├── charts.py              # Risk dials and Plotly charts
│   ├── location_picker.py     # Geolocation forms
│   └── navbar.py              # Role-based side navigation
├── pages/
│   ├── dashboard.py           # Patient metrics overview
│   ├── specialist_finder.py   # OSM specialist routing page
│   ├── diabetes.py            # Diabetes screening form
│   ├── heart.py               # Cardiovascular screening form
│   ├── kidney.py              # Kidney screening form
│   └── readmission.py         # transitional care form
└── utils/
    ├── auth.py                # Identity helper functions
    ├── database.py            # CRUD operations & Cache DB setup
    ├── logger.py              # Centralized logging & error handlers
    ├── hospital_ranker.py     # Facility scoring matrices
    ├── osm_service.py         # Geocoding and routing ETAs
    └── recommendation_engine.py # Personalised clinical guides
```
