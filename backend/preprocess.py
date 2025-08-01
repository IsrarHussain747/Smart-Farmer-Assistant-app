from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List, Dict, Union, BinaryIO
import logging
import PyPDF2
import io
import os

logger = logging.getLogger(__name__)

def parse_pdf(file_content: Union[str, bytes, BinaryIO], filename: str = "") -> str:
    """Parse PDF file content and extract text."""
    try:
        if isinstance(file_content, str):
            # If it's a file path
            if os.path.exists(file_content):
                with open(file_content, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        text += pdf_reader.pages[page_num].extract_text() + "\n"
                    return text
            # If it's already text content
            return file_content
        else:
            # If it's bytes or file-like object
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content) if isinstance(file_content, bytes) else file_content)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"Error parsing PDF {filename}: {str(e)}")
        return ""

def preprocess_documents(documents: List[Union[str, bytes, BinaryIO]], metadata: List[Dict] = None) -> List[Document]:
    """Preprocess documents by cleaning and splitting into chunks."""
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        processed_docs = []
        
        for i, doc in enumerate(documents):
            # Get metadata for this document if available
            meta = metadata[i] if metadata and i < len(metadata) else {}
            filename = meta.get('source', f'document_{i}')
            
            # Check if it might be a PDF and try to parse it
            if isinstance(doc, bytes) or (isinstance(doc, str) and filename.lower().endswith('.pdf')):
                doc_text = parse_pdf(doc, filename)
            else:
                doc_text = doc
            
            # Only process if we have content
            if doc_text and doc_text.strip():
                # Create document with metadata
                document = Document(page_content=doc_text.strip(), metadata=meta)
                processed_docs.append(document)
        
        # Split into chunks
        chunks = text_splitter.split_documents(processed_docs)
        logger.info(f"Preprocessed {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Error preprocessing documents: {str(e)}")
        raise