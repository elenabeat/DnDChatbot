from pathlib import Path
from typing import List

import toml
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document


CONFIG = toml.load("config.toml")


def load_document(file_path: Path) -> List[Document]:
    """
    Extract and chunk text from pdf file at the given path.

    Args:
        file_path (Path): Path to the pdf file.

    Raises:
        FileNotFoundError: if the file does not exist.
        NotImplementedError: if the file extension is not pdf.

    Returns:
        List[Document]: A list of Document objects containing chunks of the extracted text.
            Each document has the following attributes: metadata (dict), page_content (str).
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    elif file_path.suffix == ".pdf":
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split(
            text_splitter=RecursiveCharacterTextSplitter(
                chunk_size=CONFIG["CHUNK_SIZE"],
                chunk_overlap=CONFIG["CHUNK_OVERLAP"],
            )
        )
        return pages
    else:
        raise NotImplementedError(f"File type not supported: {file_path}")
