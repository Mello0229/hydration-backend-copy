# coach_app/api/routes/athletes.py

from fastapi import APIRouter, HTTPException, Depends
from coach_app.models.schemas import Athlete
from coach_app.api.deps import get_current_coach
from shared.database import db

router = APIRouter()

@router.get("/")
async def get_athletes(coach=Depends(get_current_coach)):
    pipeline = [
        {
            "$match": {
                "role": "athlete",
                "profile.coach_name": coach["full_name"]
            }
        },
        {
            "$lookup": {
                "from": "predictions",
                "let": { "athlete": "$username" },
                "pipeline": [
                    { "$match": { "$expr": { "$eq": ["$user", "$$athlete"] } } },
                    { "$sort": { "timestamp": -1 } },
                    { "$limit": 1 }
                ],
                "as": "latest_prediction"
            }
        },
        {
            "$lookup": {
                "from": "sensor_data",
                "let": { "athlete": "$username" },
                "pipeline": [
                    { "$match": { "$expr": { "$eq": ["$user", "$$athlete"] } } },
                    { "$sort": { "timestamp": -1 } },
                    { "$limit": 1 }
                ],
                "as": "latest_vitals"
            }
        },
        {
            "$lookup": {
                "from": "sensor_warnings",
                "let": { "athlete": "$username" },
                "pipeline": [
                    { "$match": { "$expr": { "$eq": ["$user", "$$athlete"] } } },
                    { "$sort": { "timestamp": -1 } },
                    { "$limit": 5 }
                ],
                "as": "warnings"
            }
        },
        {
            "$project": {
                "_id": 0,
                "username": 1,
                "email": 1,
                "profile.full_name": 1,
                "profile.sport": 1,
                "latest_prediction": { "$arrayElemAt": ["$latest_prediction", 0] },
                "latest_vitals": { "$arrayElemAt": ["$latest_vitals", 0] },
                "warnings": 1
            }
        }
    ]
    return await db.users.aggregate(pipeline).to_list(length=None)

@router.get("/{athlete_id}", response_model=Athlete)
async def retrieve_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    """Get details of a specific athlete by ID."""
    athlete = await db.athletes.find_one({"id": athlete_id})
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete

@router.get("/vitals/{athlete_id}")
async def get_latest_vitals(athlete_id: str, coach=Depends(get_current_coach)):
    """
    Get the latest sensor vitals for a specific athlete.
    """
    from shared.database import db
    latest_data = await db.sensor_data.find_one({"user": athlete_id}, sort=[("timestamp", -1)])
    if not latest_data:
        raise HTTPException(status_code=404, detail="No sensor data found for this athlete")
    return latest_data