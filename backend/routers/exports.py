"""PDF export routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.utils.pdf_generator import generate_pdf


router = APIRouter(prefix="/api/v1/exports", tags=["exports"])


class ExportPDFRequest(BaseModel):
    """Request model for PDF export."""
    projection: dict[str, Any] = Field(..., description="Complete projection object")
    summary: str = Field(..., description="Markdown-formatted AI summary")


@router.post("/pdf")
async def export_pdf(
    request: ExportPDFRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate and download PDF from projection and summary.
    
    This endpoint accepts a complete projection object and AI summary,
    generates a professional PDF document, and returns it as a downloadable file.
    
    Args:
        request: Contains projection and summary data
        current_user: Authenticated user (from JWT token)
    
    Returns:
        StreamingResponse: PDF file with appropriate headers for download
    
    Raises:
        HTTPException: If PDF generation fails
    """
    try:
        # Validate that projection and summary are present
        if not request.projection:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Projection data is required"
            )
        
        if not request.summary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Summary is required"
            )
        
        # Validate required fields in projection
        required_fields = ["profile", "yearlyProjections", "totalCost", "warnings", "assumptions"]
        missing_fields = [field for field in required_fields if field not in request.projection]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required projection fields: {', '.join(missing_fields)}"
            )
        
        # Generate PDF
        pdf_buffer = generate_pdf(request.projection, request.summary)
        
        # Generate filename with current date
        filename = f"nestworth-plan-{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )