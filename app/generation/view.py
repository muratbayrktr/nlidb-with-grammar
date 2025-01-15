from app.generation import router
from app.generation.service import InferenceEngine
from app.generation.model import (
    NLQRequest, 
    InferenceResponseFormat
)
from fastapi import HTTPException
import httpx  # For making HTTP requests to localhost endpoints.

@router.post("/infer")
async def infer(request : NLQRequest):
    """
    A simple endpoint to infer a query.

    Returns: the generated query

    """
    engine = InferenceEngine(
        model=request.model,
        response_format=InferenceResponseFormat
    )
    try:
        # Step 1: Send the NLQ to the /all_incremental endpoint.
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8000/classification/all_incremental",
                json={"nlq": request.natural_language_query},
            )

        # Ensure the response is successful.
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to classify NLQ: {response.text}"
            )

        # Parse the response from /all_incremental.
        classification_results = response.json()
        db = classification_results.get("db")
        tables = classification_results.get("tables", [])
        columns_dict = classification_results.get("columns", {})
        columns = []
        for table, column_list in columns_dict.items():
            for column in column_list:
                columns.append(table + "." + column)


        if not db or not tables or not columns:
            raise ValueError("Incomplete classification results received.")

        # Step 2: Pass classification results to the inference engine.
        kwargs = {
            "nlq": request.natural_language_query,
            "tables": tables,
            "columns": columns,
            "clarifications": request.clarifications,
        }

        # Generate the SQL query.
        return engine.generate(**kwargs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))