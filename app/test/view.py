from app.test import router
from app.test.model import TestRequest
from app.generation.model import NLQRequest
from fastapi import HTTPException
from app.test import router
from pathlib import Path
import json
import asyncio
import httpx

@router.post("/single")
async def test_infer_and_compare(request: TestRequest):
    """
    Test endpoint to:
    1. Send NLQRequest to /infer and retrieve the SQL query.
    2. Execute both groundtruth and inferred SQL queries on the database.
    3. Compare the results of the queries.
    """
    try:
        # Step 1: Send NLQRequest to the /infer endpoint
        async with httpx.AsyncClient() as client:
            infer_response = await client.post(
                "http://127.0.0.1:8000/generate/infer",
                json={
                    "natural_language_query": request.question,
                    "clarifications": [request.evidence],
                    "model": request.model
                }
            )
        
        if infer_response.status_code != 200:
            raise HTTPException(
                status_code=infer_response.status_code,
                detail=f"Infer endpoint failed: {infer_response.text}"
            )

        # Extract the inferred SQL query
        infer_data = infer_response.json()
        inferred_sql_query = infer_data.get("response").get("final_query")
        if not inferred_sql_query:
            raise ValueError("No SQL query was inferred from the /infer endpoint." + json.dumps(infer_data))

        # Step 2: Execute the ground-truth SQL query
        async with httpx.AsyncClient() as client:
            groundtruth_response = await client.post(
                "http://127.0.0.1:8000/db/execute",
                json={"sql": request.SQL}
            )

        if groundtruth_response.status_code != 200:
            raise HTTPException(
                status_code=groundtruth_response.status_code,
                detail=f"Groundtruth query failed: {groundtruth_response.text}"
            )

        groundtruth_result = groundtruth_response.json().get("value")

        # Step 3: Execute the inferred SQL query
        async with httpx.AsyncClient() as client:
            inferred_response = await client.post(
                "http://127.0.0.1:8000/db/execute",
                json={"sql": inferred_sql_query}
            )

        if inferred_response.status_code != 200:
            raise HTTPException(
                status_code=inferred_response.status_code,
                detail=f"Inferred query failed: {inferred_response.text}"
            )

        inferred_result_data = inferred_response.json()
        inferred_result = inferred_result_data.get("value")
        inferred_error = inferred_result_data.get("error")

        # Determine if the inferred query is valid
        valid = inferred_error is None

        # Step 4: Compare the results if the inferred query is valid
        match = False
        if valid:
            match = groundtruth_result == inferred_result

        # Prepare the evaluation result
        comparison_result = {
            "valid": valid,  # Whether the inferred query executed successfully
            "match": match,  # Whether the results match
            "groundtruth_result": groundtruth_result,
            "inferred_result": inferred_result if valid else None,  # Result if valid
            "inferred_sql_query": inferred_sql_query,
            "error": inferred_error if not valid else None  # Include error if invalid
        }

        return comparison_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/bulk")
async def bulk_infer_and_compare():
    """
    Bulk endpoint to:
    1. Read requests from app.test.mini_dev_postgresql.json.
    2. Send each request to /single endpoint in parallel.
    3. Return categorized results for valid, invalid, and failed requests.
    """
    try:
        # Step 1: Read JSON requests from the file
        file_path = Path("app/test/mini_dev_postgresql.json")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="mini_dev_postgresql.json file not found.")
        
        with file_path.open("r") as file:
            test_requests = json.load(file)

        # Step 2: Prepare requests for the /single endpoint
        async def send_to_single(request_data):
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "http://127.0.0.1:8000/test/single",
                        json=request_data
                    )
                    response_data = response.json()
                    return {
                        "request": request_data,
                        "response": response_data,
                        "status": response.status_code
                    }
                except Exception as e:
                    return {
                        "request": request_data,
                        "error": str(e),
                        "status": 500
                    }

        # Step 3: Create asyncio tasks for all requests
        tasks = [
            send_to_single(request_data) for request_data in test_requests
        ]

        # Step 4: Execute all tasks in parallel
        results = await asyncio.gather(*tasks)

        # Step 5: Categorize the results
        valid_requests = []
        invalid_requests = []
        failed_requests = []

        for res in results:
            if res.get("status") == 200:
                response = res.get("response", {})
                if response.get("valid", False):  # Valid SQL query
                    valid_requests.append(res)
                else:  # Invalid SQL query
                    invalid_requests.append(res)
            else:  # Failed request
                failed_requests.append(res)

        # Return the categorized results
        return {
            "total_requests": len(test_requests),
            "valid_requests": len(valid_requests),
            "invalid_requests": len(invalid_requests),
            "failed_requests": len(failed_requests),
            "results": {
                "valid": valid_requests,
                "invalid": invalid_requests,
                "failed": failed_requests
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))