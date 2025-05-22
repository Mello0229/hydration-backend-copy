# 💧 Smart Hydration Backend API

This backend powers the athlete and coach apps for hydration monitoring, real-time device integration, and session tracking using **FastAPI** and **MongoDB**.

---

## 🔗 Live API (Hosted via Railway)

https://hydration-backend.up.railway.app

---

## 📦 Project Structure

```bash
backend/
├── main.py                  # FastAPI entrypoint (unified)
├── athlete_app/
│   ├── api/routes/
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── data.py
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── settings.py
│   │   └── device.py
│   ├── core/
│   │   ├── config.py
│   │   ├── model_loader.py
│   │   └── security.py
│   ├── models/schemas.py
│   ├── services/
│   │   ├── predictor.py
│   │   └── preprocess.py
│   └── model/
│       ├── hydration_model.pkl
│       ├── hydration_scaler.pkl
│       └── train_ecg_sigmoid.csv
├── coach_app/
│   ├── api/routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── profile.py
│   │   ├── alerts.py
│   │   ├── athletes.py
│   │   ├── sessions.py
│   │   ├── settings.py
│   │   └── account.py
│   ├── models/schemas.py
│   └── services/utils.py
├── shared/
│   ├── database.py
│   └── security.py
├── check/model.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

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

## 🧪 API Endpoints

### 🔐 Auth

| Method | Path               | Description      |
| ------ | ------------------ | ---------------- |
| POST   | /auth/signup       | Signup (athlete) |
| POST   | /auth/login        | Login (athlete)  |
| POST   | /coach/auth/signup | Signup (coach)   |
| POST   | /coach/auth/login  | Login (coach)    |

### 🧍 Athlete

| Method | Path                      | Description                  |
| ------ | ------------------------- | ---------------------------- |
| POST   | /data/receive             | Submit sensor data           |
| POST   | /data/receive-raw-stream  | Submit batch raw sensor data |
| GET    | /data/hydration/status    | Get latest hydration status  |
| GET    | /data/warnings/prediction | Prediction log               |
| GET    | /data/warnings/sensor     | Sensor warnings              |
| GET    | /data/alerts              | Get sensor warnings/alerts   |
| GET    | /data/time                | Get server time              |
| GET    | /data/ping                | Health check endpoint        |

### ⏱ Athlete Sessions

| Method | Path           | Description            |
| ------ | -------------- | ---------------------- |
| POST   | /session/start | Start training session |
| POST   | /session/end   | End training session   |
| GET    | /session/logs  | Get athlete sessions   |

### 👤 Athlete Profile & Settings

| Method | Path                    | Description               |
| ------ | ----------------------- | ------------------------- |
| GET    | /user/profile           | Get profile               |
| POST   | /user/profile           | Update profile            |
| POST   | /account/password       | Change password           |
| DELETE | /account/delete         | Delete account            |
| GET    | /settings/units         | Get preferred units       |
| PUT    | /settings/units         | Update units              |
| GET    | /settings/notifications | Get notification settings |
| PUT    | /settings/notifications | Update notifications      |

### 📡 Device

| Method | Path                   | Description            |
| ------ | ---------------------- | ---------------------- |
| GET    | /device/pairing-status | Check device pairing   |
| GET    | /device/status         | Get device health info |

### 🧑‍🏫 Coach Dashboard

| Method | Path                  | Description       |
| ------ | --------------------- | ----------------- |
| GET    | /dashboard            | Overview stats    |
| GET    | /athletes/            | List all athletes |
| POST   | /athletes/add         | Add athlete       |
| DELETE | /athletes/remove/{id} | Remove athlete    |

### 🚨 Alerts

| Method | Path                 | Description           |
| ------ | -------------------- | --------------------- |
| GET    | /alerts/             | Get all alerts        |
| GET    | /alerts/{id}         | Get alerts by athlete |
| POST   | /alerts/             | Create new alert      |
| POST   | /alerts/resolve/{id} | Resolve alert         |

### ⚙️ Coach Settings

| Method | Path                    | Description          |
| ------ | ----------------------- | -------------------- |
| GET    | /settings/units         | Get preferred units  |
| PUT    | /settings/units         | Update unit settings |
| GET    | /settings/notifications | Get notifications    |
| PUT    | /settings/notifications | Update notifications |

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
