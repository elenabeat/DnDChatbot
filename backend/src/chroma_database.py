import os

import toml
from chromadb import PersistentClient, Collection
from chromadb.utils import embedding_functions

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
