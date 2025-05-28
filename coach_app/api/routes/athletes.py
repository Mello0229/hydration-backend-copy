# coach_app/api/routes/athletes.py

from fastapi import APIRouter, HTTPException, Depends
from coach_app.models.schemas import Athlete
from coach_app.api.deps import get_current_coach
from shared.database import db

router = APIRouter()

@router.get("/", response_model=list[Athlete])
async def list_athletes(coach=Depends(get_current_coach)):
    """List all athletes assigned to the authenticated coach."""
    athletes = db.athletes.find({"assigned_by": coach["email"]})
    return [athlete async for athlete in athletes]

@router.get("/{athlete_id}", response_model=Athlete)
async def retrieve_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    """Get details of a specific athlete by ID."""
    athlete = await db.athletes.find_one({"id": athlete_id})
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete
