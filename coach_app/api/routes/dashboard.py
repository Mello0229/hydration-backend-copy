from fastapi import APIRouter, Depends
from shared.database import db
from coach_app.api.deps import get_current_coach

router = APIRouter()

@router.get("/")
async def dashboard(coach=Depends(get_current_coach)):
    coach_email = coach["email"]

    # Pull all athletes linked to the coach
    athletes = await db.athletes.find({"assigned_by": coach_email}).to_list(length=None)

    total_athletes = len(athletes)

    avg_hydration = (
        sum(a.get("hydration_level", 0) for a in athletes) // total_athletes
        if total_athletes > 0 else 0
    )

    critical_hydration = sum(1 for a in athletes if a.get("status") == "Critical")

    return {
        "totalAthletes": total_athletes,
        "avgHydration": avg_hydration,
        "criticalHydration": critical_hydration,
        # "healthy": total_athletes - critical_hydration,
    }