from flask import Flask, request, jsonify
from backend.preprocess import preprocess_documents
from backend.embeddings import generate_embeddings
from backend.rag import AgroDocRAG
import os
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
rag = AgroDocRAG()

@app.route('/health', methods=['GET'])
def health_check():
    """Check if the API is running."""
    return jsonify({"status": "healthy"}), 200

@app.route('/ingest', methods=['POST'])
def ingest_documents():
    """Ingest agricultural documents into ChromaDB."""
    try:
        data = request.get_json()
        documents = data.get('documents', [])
        metadata = data.get('metadata', [{}] * len(documents))
        if not documents:
            return jsonify({"error": "No documents provided"}), 400
        
        # Process PDF documents if needed
        processed_documents = []
        for i, doc in enumerate(documents):
            meta = metadata[i] if i < len(metadata) else {}
            # Check if this is a PDF document (base64 encoded)
            if meta.get('type') == 'pdf':
                try:
                    import base64
                    # Decode base64 string to bytes
                    pdf_bytes = base64.b64decode(doc)
                    processed_documents.append(pdf_bytes)
                except Exception as pdf_error:
                    logger.error(f"Error decoding PDF: {str(pdf_error)}")
                    return jsonify({"error": f"Error processing PDF: {str(pdf_error)}"}), 400
            else:
                processed_documents.append(doc)
        
        # Preprocess and generate embeddings
        processed_docs = preprocess_documents(processed_documents, metadata)
        # Extract metadata from processed documents to ensure length matches
        doc_metadata = [doc.metadata for doc in processed_docs]
        embeddings, texts, metadatas = generate_embeddings(processed_docs, doc_metadata)
        
        # Store in ChromaDB
        rag.store_documents(texts, embeddings, metadatas)
        return jsonify({"message": f"Ingested {len(texts)} document chunks"}), 200
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def process_query():
    """Process a farmer's query and return an answer."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location', None)
        target_lang = data.get('target_lang', 'ur')
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Process query using RAG pipeline
        result = rag.process_query(query, location, target_lang)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)