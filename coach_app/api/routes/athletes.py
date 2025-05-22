from fastapi import APIRouter, HTTPException, Depends
from coach_app.models.schemas import Athlete
from coach_app.api.deps import get_current_coach
from shared.database import db

router = APIRouter()

@router.get("/", response_model=list[Athlete])
async def get_athletes(coach=Depends(get_current_coach)):
    # ✅ Only return athletes added by this coach
    return [doc async for doc in db.athletes.find({"assigned_by": coach["email"]})]

@router.get("/{athlete_id}", response_model=Athlete)
async def get_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    athlete = await db.athletes.find_one({"id": athlete_id})
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete

@router.post("/add")
async def add_athlete(data: Athlete, coach=Depends(get_current_coach)):
    athlete = data.dict()
    athlete["assigned_by"] = coach["email"]  # ✅ Track which coach added the athlete
    await db.athletes.insert_one(athlete)
    return {"message": "Athlete added"}

@router.delete("/remove/{athlete_id}")
async def remove_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    result = await db.athletes.delete_one({"id": athlete_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return {"message": "Athlete removed"}
