"""API endpoints for AI summary generation."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any
from backend.routers.auth import get_current_user
from backend.utils.summary_generator import generate_summary
from backend.utils.assumptions_summarizer import generate_assumptions_summary


router = APIRouter(prefix="/api/v1/summaries", tags=["summaries"])


class GenerateSummaryRequest(BaseModel):
    """Request model for summary generation."""
    projection: dict[str, Any] = Field(..., description="Complete projection object")
    custom_instructions: str | None = Field(None, description="Optional custom instructions for AI summary generation")


class GenerateSummaryResponse(BaseModel):
    """Response model for summary generation."""
    summary: str = Field(..., description="Markdown-formatted AI summary")
    generatedAt: str = Field(..., description="ISO 8601 timestamp of generation")


@router.post("/generate", response_model=GenerateSummaryResponse)
async def generate_summary_endpoint(
    request: GenerateSummaryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI summary from projection data.
    
    This endpoint accepts a complete projection object and uses OpenAI's API
    to generate an empathetic, structured markdown summary.
    
    **IMPORTANT**: The AI is instructed to use ONLY the calculated numbers
    provided in the projection and NOT to invent new numbers.
    
    Args:
        request: Contains the projection object and optional custom instructions
        current_user: Authenticated user (from JWT token)
    
    Returns:
        GenerateSummaryResponse with markdown summary and timestamp
    
    Raises:
        HTTPException: If summary generation fails
    """
    try:
        # Validate that projection data is present
        if not request.projection:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Projection data is required"
            )
        
        # Validate required fields in projection
        required_fields = ["profile", "yearlyProjections", "totalCost", "warnings", "assumptions"]
        missing_fields = [field for field in required_fields if field not in request.projection]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required projection fields: {', '.join(missing_fields)}"
            )
        
        # Generate AI summary with optional custom instructions
        summary = await generate_summary(request.projection, request.custom_instructions)
        
        return GenerateSummaryResponse(
            summary=summary,
            generatedAt=datetime.now(timezone.utc).isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


class GenerateAssumptionsRequest(BaseModel):
    """Request model for assumptions summary generation."""
    assumptions: dict[str, Any] = Field(..., description="Assumptions object from projection")


class GenerateAssumptionsResponse(BaseModel):
    """Response model for assumptions summary generation."""
    summary: str = Field(..., description="Markdown-formatted AI assumptions summary")
    generatedAt: str = Field(..., description="ISO 8601 timestamp of generation")


@router.post("/generate-assumptions", response_model=GenerateAssumptionsResponse)
async def generate_assumptions_endpoint(
    request: GenerateAssumptionsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI summary of assumptions.
    
    This endpoint accepts an assumptions object and uses OpenAI's API
    to generate a concise, scannable summary of key assumptions.
    
    Args:
        request: Contains the assumptions object
        current_user: Authenticated user (from JWT token)
    
    Returns:
        GenerateAssumptionsResponse with markdown summary and timestamp
    
    Raises:
        HTTPException: If summary generation fails
    """
    try:
        # Validate that assumptions data is present
        if not request.assumptions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assumptions data is required"
            )
        
        # Generate AI summary
        summary = await generate_assumptions_summary(request.assumptions)
        
        return GenerateAssumptionsResponse(
            summary=summary,
            generatedAt=datetime.now(timezone.utc).isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate assumptions summary: {str(e)}"
        )