import os
from pathlib import Path
from uuid import uuid4

import toml
from chromadb import PersistentClient, Collection
from chromadb.utils import embedding_functions

from text_extraction import load_document

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

    chunks = load_document(file_path)
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
