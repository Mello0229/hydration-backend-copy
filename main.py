from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

# Import routers
from athlete_app.api.routes import auth, profile as athlete_profile, data, user
from athlete_app.api.routes import device, session, settings as athlete_settings
from coach_app.api.routes import (
    dashboard, athletes, alerts,
    profile as coach_profile,
    settings as coach_settings,
    auth as coach_auth,
    sessions,
    account as coach_account
)

# Init app
app = FastAPI(
    title="Smart Hydration API",
    version="1.0.0",
    description="Unified API for athlete and coach apps"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ATHLETE ROUTES
app.include_router(auth.router, prefix="/auth", tags=["Athlete Auth"])
app.include_router(athlete_profile.router, prefix="/user", tags=["Athlete Profile"])
app.include_router(data.router, prefix="/data", tags=["Sensor Data"])
app.include_router(user.router, prefix="/account", tags=["Athlete Account"])
app.include_router(device.router, prefix="/device", tags=["Device"])
app.include_router(session.router, prefix="/session", tags=["Sessions"])
app.include_router(athlete_settings.router, prefix="/settings", tags=["Athlete Settings"])  # ✅ Added

# COACH ROUTES
app.include_router(coach_auth.router, prefix="/coach/auth", tags=["Coach Auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Coach Dashboard"])
app.include_router(athletes.router, prefix="/athletes", tags=["Coach Athletes"])
app.include_router(alerts.router, prefix="/alerts", tags=["Coach Alerts"])
app.include_router(coach_profile.router, prefix="/profile", tags=["Coach Profile"])
app.include_router(coach_settings.router, prefix="/settings", tags=["Coach Settings"])
app.include_router(sessions.router, prefix="/coach", tags=["Coach Sessions"])
app.include_router(coach_account.router, prefix="/coach/account", tags=["Coach Account"])

# Global exception logger
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
