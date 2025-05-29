from fastapi import APIRouter, Depends
from shared.database import db
from coach_app.api.deps import get_current_coach

router = APIRouter()

@router.get("/")
async def dashboard(coach=Depends(get_current_coach)):
    coach_name = coach["full_name"]
    
    # Get usernames of athletes assigned to this coach
    athlete_usernames = [
        doc["username"]
        async for doc in db.users.find(
            {"role": "athlete", "profile.coach_name": coach_name},
            {"username": 1}
        )
    ]

    total = len(athlete_usernames)
    
    dehydrated = await db.predictions.count_documents({
        "hydration_status": "Dehydrated",
        "user": { "$in": athlete_usernames }
    })

    hydrated_pct = 100 - (dehydrated * 100 // total) if total else 0

    trend = [round(80 + i % 5, 1) for i in range(7)]  # Dummy data for now

    return {
        "coach": coach["username"],
        "total_athletes": total,
        "hydrated_pct": hydrated_pct,
        "hydration_trend": trend
    }