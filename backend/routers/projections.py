"""Projection calculation routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime, timezone

from backend.models.user import User
from backend.models.profile import FinancialProfile
from backend.models.projection import Projection
from backend.routers.auth import get_current_user
from backend.database import get_database
from backend.utils.projection_calculator import calculate_five_year_projection

router = APIRouter(prefix="/api/v1/projections", tags=["projections"])


class CalculateProjectionRequest(BaseModel):
    """Request model for projection calculation."""
    profile_id: Optional[str] = None


@router.post("/calculate")
async def calculate_projection(
    current_user: User = Depends(get_current_user),
    request: CalculateProjectionRequest = None
):
    # Handle None request by creating default
    if request is None:
        request = CalculateProjectionRequest()
    """
    Calculate 5-year financial projection from user's profile.
    
    If profile_id is provided, uses that profile (must belong to user).
    Otherwise, uses the user's current profile.
    
    Caches the result in database for subsequent requests.
    """
    db = get_database()
    
    # Determine which profile to use
    if request.profile_id:
        # Use specified profile
        try:
            profile_doc = await db.profiles.find_one({
                "_id": ObjectId(request.profile_id),
                "user_id": ObjectId(current_user.id)
            })
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid profile ID"
            )
    else:
        # Use user's current profile
        profile_doc = await db.profiles.find_one({"user_id": ObjectId(current_user.id)})
    
    if not profile_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile_id = str(profile_doc["_id"])
    
    # Check if we have a cached projection for this profile
    cached_projection = await db.projections.find_one({
        "user_id": ObjectId(current_user.id),
        "profile_id": ObjectId(profile_id)
    })
    
    # If cached projection exists and profile hasn't been updated since, return it
    if cached_projection:
        profile_updated_at = profile_doc.get("updated_at")
        projection_created_at = cached_projection.get("created_at")
        
        # Return cached if profile wasn't updated after projection was created
        if profile_updated_at and projection_created_at and profile_updated_at <= projection_created_at:
            return cached_projection["projection_data"]
    
    # Convert profile document to FinancialProfile model
    profile = FinancialProfile(**profile_doc)
    
    # Convert profile to dict for calculation
    profile_dict = {
        'partner1_income': profile.partner1_income,
        'partner2_income': profile.partner2_income,
        'zip_code': profile.zip_code,
        'due_date': profile.due_date.isoformat(),
        'current_savings': profile.current_savings,
        'childcare_preference': profile.childcare_preference,
        'partner1_leave': {
            'duration_weeks': profile.partner1_leave.duration_weeks,
            'percent_paid': profile.partner1_leave.percent_paid,
        },
        'partner2_leave': {
            'duration_weeks': profile.partner2_leave.duration_weeks,
            'percent_paid': profile.partner2_leave.percent_paid,
        },
        'monthly_housing_cost': profile.monthly_housing_cost,
    }
    
    # Calculate projection
    projection = calculate_five_year_projection(profile_dict)
    
    # Convert snake_case keys to camelCase for frontend compatibility
    def to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def convert_keys_to_camel(obj):
        """Recursively convert dictionary keys from snake_case to camelCase."""
        if isinstance(obj, dict):
            return {to_camel_case(k): convert_keys_to_camel(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_keys_to_camel(item) for item in obj]
        else:
            return obj
    
    # Convert the projection to camelCase
    projection_camel = convert_keys_to_camel(projection)
    
    # Save/update the projection in database
    now = datetime.now(timezone.utc)
    projection_doc = {
        "user_id": ObjectId(current_user.id),
        "profile_id": ObjectId(profile_id),
        "projection_data": projection_camel,
        "updated_at": now
    }
    
    if cached_projection:
        # Update existing projection
        await db.projections.update_one(
            {"_id": cached_projection["_id"]},
            {"$set": projection_doc}
        )
    else:
        # Create new projection
        projection_doc["created_at"] = now
        await db.projections.insert_one(projection_doc)
    
    return projection_camel