from fastapi import APIRouter, HTTPException
from app.db.model import DBRequest, ErrorModel, SuccessResponse
from app.db import router
from app.db.service import DBEngine



@router.post("/execute")
async def execute_query(request: DBRequest):
    """
    API endpoint to execute a given nlq
    """
    db_engine = DBEngine()

    try:
        exec_result = db_engine.perform_query_on_postgresql_databases(request.sql)
    except Exception as e:
        return ErrorModel(error=str(e))

    return SuccessResponse(value=exec_result[0][0])