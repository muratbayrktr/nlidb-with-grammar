""" Main application module. """

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.prompts.view import router as prompts_router
from app.generation.view import router as generation_router

import os

from dotenv import load_dotenv

if not load_dotenv(dotenv_path=os.getcwd() + "/app/.env", verbose=True):
    print("Failed to load .env file current path is:")
    
app = FastAPI(
    title="NLIDB",
    description="LLM-powered text-to-sql tool",
    routes=[
        *prompts_router.routes,
        *generation_router.routes,
    ],
    dependencies=[],
)