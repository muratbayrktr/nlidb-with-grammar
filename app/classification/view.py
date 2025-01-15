from fastapi import APIRouter, HTTPException
from app.classification.model import (
    DBClassificationRequest,
    TableClassificationRequest,
    ColumnsClassificationRequest,
    AllClassificationRequest
)
from app.classification.service import ClassificationEngine
from app.classification import router
from app.generation.service import InferenceEngine
from app.prompts.model import ModelChoices
from app.constants import SystemPrompts
import pandas as pd
import importlib.resources as pkg_resources
import os
from app.generation.model import (
    ExtractTables,
    ExtractColumns
)

classification_engine = ClassificationEngine()

@router.post("/db")
async def classify_query(request: DBClassificationRequest):
    """
    API endpoint to classify a natural language query based on classification type.
    :param request: Request body containing the NLQ and classification type.
    :return: Predicted label.
    """
    try:
        predicted_label = classification_engine.classify(
            nlq=request.nlq, classification_type="db"
        )
        return {"db": predicted_label}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def read_and_format_table_info(db_name: str) -> str:
    """
    Reads all table CSV files in the database's directory and concatenates their information in a readable format.
    
    Args:
        db_name (str): The name of the database.
    
    Returns:
        str: A string containing the formatted table and column information.
    """
    base_path = pkg_resources.files(f"app.dev_databases.{db_name}.database_description")
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Database description path not found: {base_path}")
    
    formatted_info = []
    for file in os.listdir(base_path):
        if file.endswith(".csv"):
            table_name = os.path.splitext(file)[0]
            table_path = os.path.join(base_path, file)
            table_data = pd.read_csv(table_path)
            column_descriptions = [
                f"- {row['original_column_name']}: {row['column_description']} "
                f"(Data Format: {row['data_format']}, Value Description: {row['value_description']})"
                for _, row in table_data.iterrows()
            ]
            formatted_info.append(f"Table: {table_name}\n\tColumns Info:\n\t\t" + "\n\t\t".join(column_descriptions))
    
    return "\n\n".join(formatted_info)


def read_table_columns_info(db_name: str, table_name: str) -> str:
    """
    Reads the specific table CSV file and formats its columns information.
    
    Args:
        db_name (str): The name of the database.
        table_name (str): The name of the table.
    
    Returns:
        str: A string containing the formatted column information for the given table.
    """
    table_path = pkg_resources.files(f"app.dev_databases.{db_name}.database_description") / f"{table_name}.csv"
    if not os.path.exists(table_path):
        raise FileNotFoundError(f"Table file not found: {table_path}")
    
    table_data = pd.read_csv(table_path)
    column_descriptions = [
        f"- {row['original_column_name']}: {row['column_description']} "
        f"(Data Format: {row['data_format']}, Value Description: {row['value_description']})"
        for _, row in table_data.iterrows()
    ]
    return f"Table: {table_name}\n\tColumns Info:\n\t\t" + "\n\t\t".join(column_descriptions)


@router.post("/tablenames")
async def classify_query_tablenames(request: TableClassificationRequest):
    """
    Classify and identify relevant tables based on a natural language query.
    """
    try:
        db_schema = read_and_format_table_info(request.db)
        request_data = {
            "nlq": request.nlq,
            "db_schema": db_schema,
        }
        inference_engine = InferenceEngine(
            model=ModelChoices.GPT4o,
            response_format=ExtractTables
        )
        return inference_engine.generate(
            system_prompt=SystemPrompts.EXTRACT_TABLES,
            **request_data
        )["response"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/columns")
async def classify_query_columns(request: ColumnsClassificationRequest):
    """
    Classify and identify relevant columns within a specific table based on a natural language query.
    """
    try:
        db_schema = read_table_columns_info(request.db, request.tables[0])
        request_data = {
            "nlq": request.nlq,
            "db_schema": db_schema,
        }
        inference_engine = InferenceEngine(
            model=ModelChoices.GPT4o,
            response_format=ExtractColumns
        )
        return inference_engine.generate(
            system_prompt=SystemPrompts.EXTRACT_COLUMNS,
            **request_data
        )["response"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/all_incremental")
async def incremental_inference(request : AllClassificationRequest):
    """
    Incremental inference endpoint to classify NLQ into database, tables, and columns.
    :param nlq: Natural Language Query.
    :return: Incremental classification results.
    """
    nlq = request.nlq
    # Step 1: Classify Database
    predicted_db = classification_engine.classify(
        nlq=nlq, classification_type="db"
    )
    
    if not predicted_db:
        raise ValueError("Database classification failed. Please provide a valid query.")
    
    # Step 2: Extract Relevant Tables
    db_schema = read_and_format_table_info(predicted_db)
    inference_engine_tables = InferenceEngine(
        model=ModelChoices.GPT4o,
        response_format=ExtractTables
    )
    tables_response : ExtractTables = inference_engine_tables.generate(
        system_prompt=SystemPrompts.EXTRACT_TABLES,
        nlq=nlq,
        db_schema=db_schema
    )["response"]


    if not tables_response or not tables_response.table_names:
        raise ValueError(f"No relevant tables found for the database: {predicted_db}")

    # Step 3: Extract Relevant Columns
    relevant_columns = {}
    for table_name in tables_response.table_names:
        table_columns_info = read_table_columns_info(predicted_db, table_name)
        
        inference_engine_columns = InferenceEngine(
            model=ModelChoices.GPT4o,
            response_format=ExtractColumns
        )
        
        columns_response = inference_engine_columns.generate(
            system_prompt=SystemPrompts.EXTRACT_COLUMNS,
            nlq=nlq,
            db_schema=table_columns_info
        )["response"]
        
        relevant_columns[table_name] = columns_response.model_dump(mode="json").get("column_names", [])

    return {
        "db": predicted_db,
        "tables": tables_response.table_names,
        "columns": relevant_columns,
    }
