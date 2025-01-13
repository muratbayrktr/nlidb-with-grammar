from app.classification import router
from app.classification.model import ClassificationRequest
from app.classification.service import ClassificationEngine

@router.post("/classify")
async def sample_func(request : ClassificationRequest):

    return {"a":"b"}