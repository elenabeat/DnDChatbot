import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path

import toml
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from src.chroma_database import init_db, update_sources


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs/backend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

CONFIG = toml.load("config.toml")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Controls startup and shutdown events for the FastAPI application.
    Anything before the yield statement is executed on startup,
    and anything after is executed on shutdown.

    Args:
        app (FastAPI): unaccessed here but necessary for FASTAPI to accept this
            lifespan.
    """
    # Startup events
    load_dotenv()
    global COLLECTION
    COLLECTION = init_db(
        path=CONFIG["CHROMADB_PATH"],
        collection_name=CONFIG["COLLECTION_NAME"],
    )
    logger.info(f"Initialized database collection: {COLLECTION.name}")
    update_sources(collection=COLLECTION, source_dir=Path(CONFIG["SOURCE_DIR"]))
    yield
    # Shutdown events
    pass


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def custom_form_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Sends formats detailed responses for any requests that trigger validation errors.

    Args:
        request (Request): request triggering the validation error.
        exc (RequestValidationError): the validation error exception that was raised.

    Returns:
        JSONResponse: json response explaining what fields were missing, of the wrong 
            type, etc.
    """

    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"detail": "Invalid request", "errors": reformatted_message}
        ),
    )
