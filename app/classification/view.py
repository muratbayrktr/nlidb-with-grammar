from fastapi import APIRouter, HTTPException
from app.classification.model import ClassificationRequest
from app.classification.service import ClassificationEngine

router = APIRouter()

classification_engine = ClassificationEngine()

@router.post("/classify")
async def classify_query(request: ClassificationRequest):
    """
    API endpoint to classify a natural language query based on classification type.
    :param request: Request body containing the NLQ and classification type.
    :return: Predicted label.
    """
    try:
        predicted_label = classification_engine.classify(
            nlq=request.nlq, classification_type=request.classification_type
        )
        return {"classification_type": request.classification_type, "predicted_label": predicted_label}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
