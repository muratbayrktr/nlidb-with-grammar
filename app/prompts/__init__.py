from fastapi import APIRouter
from app.prompts.builder import PromptBuilder

router = APIRouter( prefix="/prompts", tags=["prompts"] )
