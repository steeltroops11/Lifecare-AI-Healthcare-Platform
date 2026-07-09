# Smart Healthcare Analytics & Recommendation System 🏥

An enterprise-ready, production-hardened machine learning diagnostic platform that combines clinical disease risk screening, AI recommendations, and an automated specialist finder geolocator (using OpenStreetMap, Overpass, and OpenRouteService).

---

## 🌟 Key Features

* **🩺 Multi-Disease ML Risk Screening**: Predicts risk probabilities for **Diabetes**, **Heart Disease**, **Chronic Kidney Disease**, and **Hospital Readmissions** using optimized Scikit-Learn models.
* **🤖 AI Clinical Recommendation Engine**: Evaluates risk and patient data to generate personalized immediate action checklists, test recommendations, lifestyle plans, and department routes.
* **🔍 Smart Specialist Finder**: Queries OpenStreetMap (Overpass API) to locate nearby hospitals and clinics based on coordinates.
* **🚗 OpenRouteService Travel ETAs**: Generates driving, walking, and cycling ETAs to clinics. Features a 2.5s timeout, exponential backoff retries, and a 5-minute circuit breaker deactivation cooldown.
* **🔌 Offline Mode & Cache**: Caches queries for 24 hours. Automatically loads expired cache results if the live Overpass network requests time out or fail.
* **🛡️ Security & Audit Logging**: Fully parameterized SQL query structures, Werkzeug PBKDF2 password hashing, a per-user rate limiter (10 searches/min), and audit logging.

---

## 🏗️ System Architecture

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

---

## ⚙️ Quick Start

### Method A: Docker Compose (Recommended)
Exposes the entire dual-portal architecture with a single command:
```bash
docker compose up --build
```
* **Identity Portal**: [http://localhost:5000](http://localhost:5000)
* **Streamlit Patient Dashboard**: [http://localhost:8501](http://localhost:8501)

### Method B: Manual Local Setup
1. **Create and Activate Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   ```
2. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Portals**:
   ```bash
   python login/auth_app.py
   streamlit run app.py
   ```

---

## 🧪 Demo Login Credentials

Use the following accounts to access role-based navigation portals:
* **Admin Portal**: `admin@healthcare.com` / `admin123`
* **Doctor Portal**: `doctor@healthcare.com` / `doctor123`
* **Patient Portal**: `patient@healthcare.com` / `patient123`

---

## 📡 API Configuration
To activate live ORS ETAs, get a free key from [OpenRouteService](https://openrouteservice.org/) and add it to your environment variables or Streamlit secrets:
```bash
export ORS_API_KEY="your_api_key"
```

---

## 📄 Comprehensive Documentation
For in-depth technical details, refer to:
* 🗺️ [Architecture & Directory Guide](docs/Architecture.md)
* 🗄️ [SQLite Database Schemas](docs/Database.md)
* 🔌 [Nominatim, Overpass, and ORS APIs](docs/API.md)
* 🐳 [Deployment Guide](docs/Deployment.md)
* 🛡️ [Security & Hardening Policies](docs/Security.md)
