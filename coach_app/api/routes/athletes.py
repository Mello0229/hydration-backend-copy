from fastapi import APIRouter, HTTPException, Depends
from coach_app.models.schemas import Athlete
from coach_app.api.deps import get_current_coach
from shared.database import db

router = APIRouter()

@router.get("/", response_model=list[Athlete])
async def get_athletes(coach=Depends(get_current_coach)):
    if not coach or "email" not in coach:
        raise HTTPException(status_code=401, detail="Invalid or missing coach token")

    profile = await db.coach_profile.find_one({"email": coach["email"]})
    if not profile or not profile.get("name"):
        raise HTTPException(status_code=400, detail="Coach profile missing name")

    coach_name = profile["name"]

    pipeline = [
        {"$match": {"assigned_by": coach["email"]}},
        {
            "$lookup": {
                "from": "predictions",
                "let": {"athlete": "$email"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$user", "$$athlete"]}}},
                    {"$sort": {"timestamp": -1}},
                    {"$limit": 1}
                ],
                "as": "latest_prediction"
            }
        },
        {
            "$lookup": {
                "from": "sensor_data",
                "let": {"athlete": "$email"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$user", "$$athlete"]}}},
                    {"$sort": {"timestamp": -1}},
                    {"$limit": 1}
                ],
                "as": "latest_vitals"
            }
        },
        {
            "$lookup": {
                "from": "sensor_warnings",
                "let": {"athlete": "$email"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$user", "$$athlete"]}}},
                    {"$sort": {"timestamp": -1}},
                    {"$limit": 5}
                ],
                "as": "warnings"
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "athlete_id": 1,
                "name": 1,
                "email": 1,
                "sport": 1,
                "assigned_by": 1,
                "hydration_level": 1,
                "status": 1,
                "ecg_sigmoid": 1,
                "skin_conductance": 1,
                "heart_rate": 1,
                "body_temp": 1,
                "latest_prediction": {"$arrayElemAt": ["$latest_prediction", 0]},
                "latest_vitals": {"$arrayElemAt": ["$latest_vitals", 0]},
                "warnings": 1
            }
        }
    ]

    raw_athletes = await db.athletes.aggregate(pipeline).to_list(length=None)

    athletes = []
    for doc in raw_athletes:
        vitals = doc.get("latest_vitals", {})
        prediction = doc.get("latest_prediction", {})
        athlete = {
        "id": doc.get("id") or doc.get("email"),
        "athlete_id": doc.get("athlete_id", ""),
        "name": doc.get("name", ""),
        "email": doc.get("email", ""),
        "sport": doc.get("sport", ""),
        "assigned_by": doc.get("assigned_by", ""),
        "hydration_level": int(doc.get("hydration_level", 0)),
        "heart_rate": float(vitals.get("heart_rate", 0)),
        "body_temp": float(vitals.get("body_temp", 0)),
        "skin_conductance": float(vitals.get("skin_conductance", 0)),
        "ecg_sigmoid": float(vitals.get("ecg_sigmoid", 0)),
        "status": doc.get("status", "Unknown"),
        "alerts": doc.get("warnings", [])
        }

        athletes.append(athlete)

    return athletes

@router.get("/{athlete_id}", response_model=Athlete)
async def retrieve_athlete(athlete_id: str, coach=Depends(get_current_coach)):
    athlete = await db.athletes.find_one({"id": athlete_id})
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.get("/vitals/{athlete_id}")
async def get_latest_vitals(athlete_id: str, coach=Depends(get_current_coach)):
    latest_data = await db.sensor_data.find_one({"user": athlete_id}, sort=[("timestamp", -1)])
    if not latest_data:
        raise HTTPException(status_code=404, detail="No sensor data found for this athlete")
    return latest_data