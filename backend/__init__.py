from backend.preprocess import preprocess_documents
from backend.embeddings import generate_embeddings
from backend.rag import AgroDocRAG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_chromadb():
    """Initialize ChromaDB with sample document to generate Parquet files."""
    try:
        # Read sample document
        with open('data/raw/sample_doc.txt', 'r') as f:
            documents = [f.read()]
        
        # Preprocess and generate embeddings
        processed_docs = preprocess_documents(documents)
        embeddings, texts, metadatas = generate_embeddings(processed_docs, [{"source": "sample_doc.txt"}])
        
        # Store in ChromaDB
        rag = AgroDocRAG()
        rag.store_documents(texts, embeddings, metadatas)
        
        logger.info("Initialized ChromaDB and generated Parquet files in data/processed/")
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {str(e)}")
        raise

if __name__ == "__main__":
    initialize_chromadb()