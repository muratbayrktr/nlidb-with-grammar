""" Main module for the FastAPI backend. """

from __future__ import annotations

from fastapi.responses import HTMLResponse

from . import app


@app.get("/")
async def read_root():
    """
    A simple root endpoint to test the FastAPI application.

    Returns: html rendered by FastAPI

    """
    return HTMLResponse(content="<h1>Welcome to the NLIDB backend!</h1>")
