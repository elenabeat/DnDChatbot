import os
import logging
from pathlib import Path
from uuid import uuid4

import toml
from chromadb import PersistentClient, Collection
from chromadb.utils import embedding_functions

from src.text_extraction import load_file

logger = logging.getLogger(__name__)

CONFIG = toml.load("config.toml")


def init_db(path: os.PathLike, collection_name: str) -> Collection:
    """
    Initialize the database with the specified collection. If the collection
    already exists, it will be returned. Otherwise, a new collection will be
    created.

    Args:
        path (os.PathLike): path to the database
        collection_name (str): name of the collection

    Returns:
        Collection: the specified collection
    """
    client = PersistentClient(path)

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=CONFIG["EMBEDDING_MODEL"],
        ),
    )

    return collection


def add_file(collection: Collection, file_path: Path) -> None:
    """
    Add a file to the database collection.

    Args:
        collection (Collection): the collection to add the file to
        file_path (Path): path to the file to add
    """

    chunks = load_file(file_path)
    documents = []
    metadata = []
    ids = []

    for chunk in chunks:
        documents.append(chunk.page_content)
        metadata.append(chunk.metadata)
        ids.append(str(uuid4()))

    collection.add(
        documents=documents,
        metadatas=metadata,
        ids=ids,
    )


def update_sources(collection: Collection, source_dir: Path) -> None:
    """
    Update the database collection with all files in the specified directory.

    Args:
        collection (Collection): the collection to update
        source_dir (Path): path to the directory containing files to add
    """
    for file_path in source_dir.glob("*.pdf"):
        results = collection.get(
            where={"source": str(file_path)},
            include=["metadatas"],
        )
        if results["ids"]:
            logger.info(f"File {file_path} already exists in the database.")
            continue
        else:
            try:
                add_file(collection, file_path)
                logger.info(f"Added file: {file_path}")
                logger.info(results)
            except NotImplementedError as e:
                logger.error(
                    f"Failed to add file: {file_path} because it was not a pdf file."
                )
                continue
            except Exception as e:
                logger.error(
                    f"Failed to add file: {file_path} due to an unexpected error. Error: {e}"
                )
                continue
