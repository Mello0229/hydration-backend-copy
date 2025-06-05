# backend/main.py
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

# Athlete App Routers
from athlete_app.api.routes import (
    auth as athlete_auth,
    profile as athlete_profile,
    data as athlete_data,
    user as athlete_user,
    device,
    session,
    alerts as athlete_alerts
)

# Coach App Routers
from coach_app.api.routes import (
    auth as coach_auth,
    dashboard,
    athletes,
    profile as coach_profile,
    sessions,
    account as coach_account,
    alerts as coach_alerts
)

# Init FastAPI
app = FastAPI(
    title="Smart Hydration API",
    version="1.0.0",
    description="Unified API for athlete and coach apps"
)

# 🌐 Middleware: Log requests with missing authorization
@app.middleware("http")
async def log_missing_auth_header(request: Request, call_next):
    if "authorization" not in request.headers:
        print("❌ Missing Authorization Header in request to:", request.url.path)
    return await call_next(request)

# 🌐 Middleware: Log all request headers
class LogRequestHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"\n🔍 [HTTP] {request.method} {request.url.path}")
        for name, value in request.headers.items():
            print(f"   🧾 {name}: {value}")
        return await call_next(request)

app.add_middleware(LogRequestHeadersMiddleware)

# 🌍 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧪 ATHLETE ROUTES
app.include_router(athlete_auth.router, prefix="/auth", tags=["Athlete Auth"])
app.include_router(athlete_profile.router, prefix="/user", tags=["Athlete Profile"])
app.include_router(athlete_data.router, prefix="/data", tags=["Sensor Data"])
app.include_router(athlete_user.router, prefix="/account", tags=["Athlete Account"])
app.include_router(device.router, prefix="/device", tags=["Device"])
app.include_router(session.router, prefix="/session", tags=["Sessions"])
app.include_router(athlete_alerts.router, prefix="/notifications", tags=["Athlete Alerts"])

# 🧑‍🏫 COACH ROUTES
app.include_router(coach_auth.router, prefix="/coach/auth", tags=["Coach Auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Coach Dashboard"])
app.include_router(athletes.router, prefix="/athletes", tags=["Coach Athletes"])
app.include_router(coach_profile.router, prefix="/profile", tags=["Coach Profile"])
app.include_router(sessions.router, prefix="/coach", tags=["Coach Sessions"])
app.include_router(coach_account.router, prefix="/coach/account", tags=["Coach Account"])
app.include_router(coach_alerts.router, prefix="/coach/alerts", tags=["Coach Alerts"])

# 🛑 Global Error Handler
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        print("🚨 Error:", traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(exc)}
        )