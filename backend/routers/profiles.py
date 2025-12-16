"""Financial profile routes for creating and retrieving user profiles."""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone, date
from bson import ObjectId

from backend.models.profile import (
    FinancialProfile,
    FinancialProfileCreate,
    FinancialProfileResponse,
    LeaveDetails
)
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.database import get_database

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


@router.post("", response_model=FinancialProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(
    profile_data: FinancialProfileCreate,
    current_user: User = Depends(get_current_user)
):
    """Create or update user's financial profile (upsert)."""
    db = get_database()
    
    # Check if user already has a profile
    existing_profile = await db.profiles.find_one({"user_id": ObjectId(current_user.id)})
    
    # Prepare profile document
    profile_dict = profile_data.model_dump(by_alias=False)
    profile_dict["user_id"] = ObjectId(current_user.id)
    profile_dict["updated_at"] = datetime.now(timezone.utc)
    
    # Convert date to datetime for MongoDB compatibility
    if isinstance(profile_dict.get("due_date"), date) and not isinstance(profile_dict.get("due_date"), datetime):
        profile_dict["due_date"] = datetime.combine(profile_dict["due_date"], datetime.min.time()).replace(tzinfo=timezone.utc)
    
    if existing_profile:
        # Update existing profile
        profile_dict["created_at"] = existing_profile["created_at"]
        
        await db.profiles.update_one(
            {"user_id": ObjectId(current_user.id)},
            {"$set": profile_dict}
        )
        
        # Fetch updated profile
        updated_profile = await db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        profile = FinancialProfile(**updated_profile)
    else:
        # Create new profile
        profile_dict["created_at"] = datetime.now(timezone.utc)
        
        result = await db.profiles.insert_one(profile_dict)
        profile_dict["_id"] = result.inserted_id
        profile = FinancialProfile(**profile_dict)
    
    # Return response with camelCase fields
    return FinancialProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        partner1_income=profile.partner1_income,
        partner2_income=profile.partner2_income,
        zip_code=profile.zip_code,
        due_date=profile.due_date.isoformat(),
        current_savings=profile.current_savings,
        childcare_preference=profile.childcare_preference,
        partner1_leave=profile.partner1_leave,
        partner2_leave=profile.partner2_leave,
        monthly_housing_cost=profile.monthly_housing_cost,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )


@router.get("/me", response_model=FinancialProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's financial profile."""
    db = get_database()
    
    # Find user's profile
    profile_doc = await db.profiles.find_one({"user_id": ObjectId(current_user.id)})
    
    if not profile_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile = FinancialProfile(**profile_doc)
    
    # Return response with camelCase fields
    return FinancialProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        partner1_income=profile.partner1_income,
        partner2_income=profile.partner2_income,
        zip_code=profile.zip_code,
        due_date=profile.due_date.isoformat(),
        current_savings=profile.current_savings,
        childcare_preference=profile.childcare_preference,
        partner1_leave=profile.partner1_leave,
        partner2_leave=profile.partner2_leave,
        monthly_housing_cost=profile.monthly_housing_cost,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )