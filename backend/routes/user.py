"""
User preferences and settings API endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

try:
    from routes.auth import get_current_user
except ImportError:
    get_current_user = lambda: {"id": "mock_user", "preferences": {}}

router = APIRouter(prefix="/user", tags=["user"])

class PreferencesUpdate(BaseModel):
    ai_provider: str = "openrouter"
    default_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    email_check_frequency: int = 15  # minutes
    notification_settings: Dict[str, bool] = {
        "email_notifications": True,
        "task_reminders": True,
        "meeting_alerts": True
    }
    ui_preferences: Dict[str, Any] = {
        "theme": "light",
        "dashboard_layout": "default",
        "timezone": "UTC"
    }

class UserPreferencesResponse(BaseModel):
    user_id: str
    preferences: Dict[str, Any]

# Default preferences for new users
DEFAULT_PREFERENCES = {
    "ai_provider": "openrouter",
    "default_model": "meta-llama/llama-3.1-8b-instruct:free",
    "email_check_frequency": 15,
    "notification_settings": {
        "email_notifications": True,
        "task_reminders": True,
        "meeting_alerts": True
    },
    "ui_preferences": {
        "theme": "light",
        "dashboard_layout": "default",
        "timezone": "UTC"
    },
    "integrations": {
        "gmail_enabled": False,
        "outlook_enabled": False,
        "calendar_enabled": False
    }
}

@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(current_user: dict = Depends(get_current_user)):
    """Get user preferences"""
    user_id = current_user.get("id", "mock_user")
    preferences = current_user.get("preferences", DEFAULT_PREFERENCES)
    
    # Ensure all default keys exist
    merged_preferences = {**DEFAULT_PREFERENCES, **preferences}
    
    return UserPreferencesResponse(
        user_id=user_id,
        preferences=merged_preferences
    )

@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences_update: PreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    user_id = current_user.get("id", "mock_user")
    current_prefs = current_user.get("preferences", DEFAULT_PREFERENCES)
    
    # Update preferences with new values
    updated_preferences = {**current_prefs}
    update_data = preferences_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if isinstance(value, dict) and key in updated_preferences:
            # Merge nested dictionaries
            updated_preferences[key] = {**updated_preferences[key], **value}
        else:
            updated_preferences[key] = value
    
    # In a real implementation, this would update the database
    # For now, we'll just return the updated preferences
    
    return UserPreferencesResponse(
        user_id=user_id,
        preferences=updated_preferences
    )

@router.patch("/preferences/{key}")
async def update_preference_key(
    key: str,
    value: Any,
    current_user: dict = Depends(get_current_user)
):
    """Update a specific preference key"""
    user_id = current_user.get("id", "mock_user")
    current_prefs = current_user.get("preferences", DEFAULT_PREFERENCES)
    
    if key not in DEFAULT_PREFERENCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid preference key: {key}"
        )
    
    # Update the specific key
    updated_preferences = {**current_prefs}
    updated_preferences[key] = value
    
    return {
        "user_id": user_id,
        "key": key,
        "value": value,
        "updated": True
    }

@router.post("/preferences/reset")
async def reset_user_preferences(current_user: dict = Depends(get_current_user)):
    """Reset user preferences to defaults"""
    user_id = current_user.get("id", "mock_user")
    
    return UserPreferencesResponse(
        user_id=user_id,
        preferences=DEFAULT_PREFERENCES
    )