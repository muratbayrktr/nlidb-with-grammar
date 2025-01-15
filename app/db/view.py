from fastapi import APIRouter, HTTPException
from app.db.model import DBRequest
from app.db import router

@router.post("/execute")
async def execute_query(request: DBRequest):
    """
    API endpoint to execute a given nlq
    """
    
    return "asfasfn"