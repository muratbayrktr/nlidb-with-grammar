from app.generation import router
from app.generation.service import InferenceEngine
from app.generation.model import NLQRequest


@router.post("/infer")
async def infer(request : NLQRequest):
    """
    A simple endpoint to infer a query.

    Returns: the generated query

    """
    engine = InferenceEngine(
        natural_language_query=request.natural_language_query,
        tables=request.tables,
        columns=request.columns,
        clarifications=request.clarifications
    )
    return engine.generate()