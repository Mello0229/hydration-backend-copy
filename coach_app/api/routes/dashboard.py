from fastapi import APIRouter, Depends
from shared.database import db
from coach_app.api.deps import get_current_coach  # ✅ import this

router = APIRouter()

@router.get("/")
async def dashboard(coach=Depends(get_current_coach)):  # ✅ require valid coach token
    total = await db.athletes.count_documents({})
    dehydrated = await db.athletes.count_documents({"status": "Dehydrated"})
    hydrated_pct = 100 - (dehydrated * 100 // total) if total else 0
    trend = [round(80 + i % 5, 1) for i in range(7)]  # Dummy trend

    return {
        "coach": coach["username"],  # Optional personalization
        "total_athletes": total,
        "hydrated_pct": hydrated_pct,
        "hydration_trend": trend
    }
