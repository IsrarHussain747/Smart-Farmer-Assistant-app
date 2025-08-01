from chromadb.utils import embedding_functions
from langchain.docstore.document import Document
from typing import List, Dict, Tuple
import yaml
import logging
import os

logger = logging.getLogger(__name__)

def generate_embeddings(documents: List[Document], metadata: List[Dict]) -> Tuple[List, List, List]:
    """Generate embeddings for document chunks."""
    try:
        # Try different paths for config file
        config_paths = ['config/config.yaml', '../config/config.yaml', os.path.join(os.path.dirname(__file__), '../config/config.yaml')]
        config = None
        
        for path in config_paths:
            try:
                with open(path, 'r') as f:
                    config = yaml.safe_load(f)
                    break
            except FileNotFoundError:
                continue
                
        if not config:
            raise FileNotFoundError("Could not find config/config.yaml")
        
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config["embedding_model"]
        )
        texts = [doc.page_content for doc in documents]
        embeddings = embedding_function(texts)
        metadatas = [meta if meta else {} for meta in metadata[:len(documents)]]
        
        logger.info(f"Generated embeddings for {len(texts)} document chunks")
        return embeddings, texts, metadatas
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise