"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "category": "Intellectual"
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "category": "Intellectual"
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "category": "Sports"
    },
    "Soccer Team": {
        "description": "Practice teamwork and play competitive soccer matches",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": [],
        "category": "Sports"
    },
    "Basketball Club": {
        "description": "Improve shooting, dribbling, and game strategy",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": [],
        "category": "Sports"
    },
    "Drama Club": {
        "description": "Act, rehearse, and perform in school productions",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": [],
        "category": "Artistic"
    },
    "Art Workshop": {
        "description": "Explore drawing, painting, and mixed media techniques",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": [],
        "category": "Artistic"
    },
    "Math Olympiad": {
        "description": "Solve advanced math problems and prepare for competitions",
        "schedule": "Saturdays, 10:00 AM - 12:00 PM",
        "max_participants": 10,
        "participants": [],
        "category": "Intellectual"
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": [],
        "category": "Intellectual"
    },
    "Horse Riding": {
        "description": "Learn riding techniques and care for horses while enjoying outdoor activities",
        "schedule": "Saturdays, 9:00 AM - 11:00 AM",
        "max_participants": 12,
        "participants": [],
        "category": "Outdoor"
    },
    "Camping Club": {
        "description": "Build camping skills, outdoor survival knowledge, and teamwork in nature",
        "schedule": "Sundays, 8:00 AM - 1:00 PM",
        "max_participants": 16,
        "participants": [],
        "category": "Outdoor"
    },
    "Hiking Club": {
        "description": "Explore local trails, improve endurance, and enjoy the outdoors together",
        "schedule": "Saturdays, 8:00 AM - 10:30 AM",
        "max_participants": 20,
        "participants": [],
        "category": "Outdoor"
    },
    "Rowing Team": {
        "description": "Develop rowing technique, strength, and teamwork on the water",
        "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 14,
        "participants": [],
        "category": "Outdoor"
    },
    "Archery Club": {
        "description": "Practice precision, focus, and target shooting in a safe outdoor setting",
        "schedule": "Wednesdays, 3:45 PM - 5:15 PM",
        "max_participants": 10,
        "participants": [],
        "category": "Outdoor"
    },
    "Kayaking Club": {
        "description": "Learn paddling skills and enjoy scenic routes on the lake or river",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 12,
        "participants": [],
        "category": "Outdoor"
    },
    "Rock Climbing": {
        "description": "Build strength, coordination, and confidence through climbing challenges",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": [],
        "category": "Outdoor"
    },
    "Outdoor Survival Skills": {
        "description": "Learn shelter building, navigation, and emergency preparedness for the outdoors",
        "schedule": "Saturdays, 9:30 AM - 12:00 PM",
        "max_participants": 18,
        "participants": [],
        "category": "Outdoor"
    },
    "Cycling Club": {
        "description": "Train for longer rides, practice biking safety, and explore the community trails",
        "schedule": "Sundays, 9:00 AM - 11:00 AM",
        "max_participants": 15,
        "participants": [],
        "category": "Outdoor"
    },
    "Nature Appreciation Group": {
        "description": "Observe local wildlife, document ecosystems, and enjoy guided outdoor learning",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": [],
        "category": "Outdoor"
    }
}


class ActivitySignupRequest(BaseModel):
    email: str
    activity_names: list[str] = Field(min_length=1)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return activities


@app.post("/activities/signup")
def signup_for_activities(request: ActivitySignupRequest):
    """Sign up a student for multiple activities."""
    unknown_activities = [
        name for name in request.activity_names if name not in activities
    ]
    if unknown_activities:
        raise HTTPException(
            status_code=404,
            detail=f"Activity not found: {', '.join(unknown_activities)}",
        )

    if len(request.activity_names) != len(set(request.activity_names)):
        raise HTTPException(
            status_code=400,
            detail="An activity can only be selected once",
        )

    already_signed_up = [
        name
        for name in request.activity_names
        if request.email in activities[name]["participants"]
    ]
    if already_signed_up:
        raise HTTPException(
            status_code=400,
            detail=(
                "Student already signed up for: "
                f"{', '.join(already_signed_up)}"
            ),
        )

    for name in request.activity_names:
        activities[name]["participants"].append(request.email)

    return {
        "message": (
            f"Signed up {request.email} for "
            f"{', '.join(request.activity_names)}"
        )
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_for_activity(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)
    return {"message": f"Removed {email} from {activity_name}"}
