# Smart Hydration API

A FastAPI-based backend supporting two user roles: **Athletes** and **Coaches**, managing hydration tracking, sensor data ingestion, and coaching dashboards.

---

## 🔗 Live API (Hosted via Railway)

https://hydration-backend.up.railway.app

---

## 📁 Project Structure

backend/
├── main.py # FastAPI entrypoint (unified for athlete + coach)
├── athlete_app/
│ ├── api/routes/
│ │ ├── auth.py # Signup & login for athletes
│ │ ├── profile.py # Athlete profile creation/update
│ │ ├── data.py # Sensor data ingestion & prediction
│ │ ├── user.py # Account settings, password, join coach
│ │ ├── session.py # Training session logs
│ │ └── device.py # Device pairing and status
│ ├── core/
│ │ ├── config.py
│ │ ├── model_loader.py
│ │ └── security.py
│ ├── models/schemas.py
│ ├── services/
│ │ ├── predictor.py
│ │ └── preprocess.py
│ └── model/
│ ├── hydration_model.pkl
│ ├── hydration_scaler.pkl
│ └── train_ecg_sigmoid.csv
├── coach_app/
│ ├── api/routes/
│ │ ├── auth.py # Signup & login for coaches
│ │ ├── dashboard.py # Overview stats for coach
│ │ ├── profile.py # Coach profile
│ │ ├── alerts.py # Alerts issued
│ │ ├── athletes.py # Athlete roster
│ │ ├── sessions.py # Athlete training logs
│ │ └── account.py # Password / account management
│ ├── models/schemas.py
│ └── services/utils.py
├── shared/
│ ├── database.py # MongoDB client & helpers
│ ├── schemas.py # Shared models (signup/login)
│ └── security.py # Auth token + password hashing
├── requirements.txt
├── Dockerfile
└── .env.example

---

## 🚀 How to Run Locally

```bash
git clone https://github.com/your-username/smart-hydration-backend
cd backend

cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

Swagger Docs: http://localhost:8000/docs

---

## 🚀 API Endpoints

### 🔐 Authentication

| Method | Path                 | Description      |
| ------ | -------------------- | ---------------- |
| POST   | `/auth/signup`       | Signup (athlete) |
| POST   | `/auth/login`        | Login (athlete)  |
| POST   | `/coach/auth/signup` | Signup (coach)   |
| POST   | `/coach/auth/login`  | Login (coach)    |

---

### 🧍 Athlete Endpoints

#### 🩺 Sensor Data

| Method | Path                        | Description             |
| ------ | --------------------------- | ----------------------- |
| POST   | `/data/receive`             | Submit sensor data      |
| GET    | `/data/hydration/status`    | Latest hydration status |
| GET    | `/data/warnings/prediction` | View prediction history |
| GET    | `/data/warnings/sensor`     | View sensor warnings    |
| GET    | `/data/alerts`              | Alerts sent to athlete  |
| GET    | `/data/time`                | Get current server time |
| GET    | `/data/ping`                | Server health check     |

#### ⏱ Session Tracking

| Method | Path             | Description             |
| ------ | ---------------- | ----------------------- |
| POST   | `/session/start` | Start training session  |
| POST   | `/session/end`   | End and log session     |
| GET    | `/session/logs`  | List athlete's sessions |
| GET    | `/session/{id}`  | Get session details     |

#### 👤 Account & Profile

| Method | Path                    | Description         |
| ------ | ----------------------- | ------------------- |
| POST   | `/user/profile`         | Update profile info |
| POST   | `/account/athlete/join` | Join a coach        |
| POST   | `/account/password`     | Change password     |
| DELETE | `/account/delete`       | Delete account      |

#### 📡 Device

| Method | Path                     | Description        |
| ------ | ------------------------ | ------------------ |
| GET    | `/device/pairing-status` | Check if paired    |
| GET    | `/device/status`         | Device health info |

---

### 🧑‍🏫 Coach Endpoints

#### 📊 Dashboard

| Method | Path         | Description          |
| ------ | ------------ | -------------------- |
| GET    | `/dashboard` | Coach overview stats |

#### 🧑‍💻 Athletes

| Method | Path                    | Description               |
| ------ | ----------------------- | ------------------------- |
| GET    | `/athletes/`            | List assigned athletes    |
| GET    | `/athletes/{id}`        | Get athlete by ID         |
| GET    | `/athletes/vitals/{id}` | Latest vitals for athlete |

#### 🚨 Alerts

| Method | Path                   | Description           |
| ------ | ---------------------- | --------------------- |
| GET    | `/alerts/`             | Get all alerts        |
| GET    | `/alerts/{athlete_id}` | Get alerts by athlete |
| POST   | `/alerts/`             | Create new alert      |
| POST   | `/alerts/resolve/{id}` | Resolve an alert      |

#### 🗓 Sessions

| Method | Path                       | Description            |
| ------ | -------------------------- | ---------------------- |
| GET    | `/coach/session/logs/{id}` | Get athlete's sessions |

#### 🧾 Profile & Account

| Method | Path                      | Description           |
| ------ | ------------------------- | --------------------- |
| GET    | `/profile/`               | Get coach profile     |
| POST   | `/profile/`               | Create coach profile  |
| PUT    | `/profile/`               | Update coach profile  |
| POST   | `/coach/account/password` | Change coach password |
| DELETE | `/coach/account/delete`   | Delete coach account  |

---

## ✅ Notes

- Athletes must complete `/user/profile` with a valid `coach_name` after signing up.
- Coaches and athletes share the same MongoDB instance but operate on separate collections (e.g., `coaches` vs `users`).
- Alerts, predictions, and sensor data are associated via `username`.

---

## ⚙️ Environment Variables (`.env`)

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
DB_NAME=hydration_db
SECRET_KEY=your-secret-key
GSR_MULTIPLIER=1.25
```

---

## 🧼 Deployment with Railway

1. Push your GitHub repo
2. Go to [https://railway.app](https://railway.app)
3. Create a new project → Deploy from GitHub
4. Railway auto-detects `Dockerfile`
5. Set environment variables in the Railway dashboard
6. App builds & deploys to a public URL

Access your API at:

```
https://<your-railway-app>.up.railway.app/docs
```

---

## ✅ Tips

- Keep `.env` out of GitHub (`.gitignore`)
- Use `.env.example` to share safely
- Use tags in Swagger to test routes by user role

---

## 👨‍💻 Author

- Jan Josef Randrup
- Smart Hydration Capstone Backend
