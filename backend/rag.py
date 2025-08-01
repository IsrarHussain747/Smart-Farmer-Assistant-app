import chromadb
import groq
import requests
from translate import Translator
from chromadb.utils import embedding_functions
import yaml
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class AgroDocRAG:
    def __init__(self):
        """Initialize RAG pipeline with persistent ChromaDB, Groq LLM, and translation."""
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Use persistent ChromaDB to store data in data/processed/
        self.client = chromadb.PersistentClient(path="data/processed")
        self.collection = self.client.get_or_create_collection("agri_docs")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.config["embedding_model"]
        )
        # Initialize Groq client with fallback
        try:
            self.groq_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        except TypeError:
            # Handle case where proxies parameter is not supported
            import httpx
            self.groq_client = groq.Groq(
                api_key=os.getenv("GROQ_API_KEY"),
                http_client=httpx.Client(follow_redirects=True)
            )
        # Initialize translators
        self.translators = {"ur": Translator(to_lang="ur")}
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.offline_cache = {}  # Simple cache for offline answers

    def store_documents(self, texts: List[str], embeddings: List, metadatas: List[Dict]) -> None:
        """Store document chunks and embeddings in ChromaDB."""
        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=[f"doc_{i}" for i in range(len(texts))]
            )
            logger.info(f"Stored {len(texts)} document chunks in ChromaDB at data/processed/")
        except Exception as e:
            logger.error(f"Error storing documents: {str(e)}")
            raise

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant document chunks from ChromaDB."""
        try:
            query_embedding = self.embedding_function([query])[0]
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return [
                {"text": doc, "metadata": meta}
                for doc, meta in zip(results["documents"][0], results["metadatas"][0])
            ]
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []

    def fetch_weather_data(self, location: str) -> Dict:
        """Fetch real-time weather data."""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return {"error": "Unable to fetch weather data"}

    def generate_answer(self, query: str, context: List[Dict]) -> str:
        """Generate an answer using Groq LLM."""
        try:
            context_text = "\n".join([item["text"] for item in context])
            prompt = f"""
            You are AgroDoc, a smart farmer assistant. Use the following context to answer the query accurately and concisely. If relevant, include agricultural insights or local weather advice.
            Context: {context_text}
            Query: {query}
            Answer in clear, simple language suitable for low-tech farmers.
            """
            response = self.groq_client.chat.completions.create(
                model=self.config["llm_model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            answer = response.choices[0].message.content
            # Cache answer for offline use
            self.offline_cache[query] = answer
            return answer
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            # Check offline cache
            return self.offline_cache.get(query, "Sorry, I couldn't generate an answer. Please try again.")

    def translate_answer(self, text: str, target_lang: str = "ur") -> str:
        """Translate the answer to the target language."""
        try:
            # If target language is English, no need to translate
            if target_lang == "en":
                return text
                
            # For other languages, use the appropriate translator
            if target_lang in self.translators:
                # The translate library has a character limit of 500
                # Split the text into chunks of 400 characters to be safe
                chunk_size = 400
                chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
                
                # Translate each chunk and join them back together
                translated_chunks = []
                for chunk in chunks:
                    translated_chunk = self.translators[target_lang].translate(chunk)
                    translated_chunks.append(translated_chunk)
                
                return ''.join(translated_chunks)
            else:
                logger.warning(f"No translator available for language: {target_lang}")
                return text
        except Exception as e:
            logger.error(f"Error translating answer: {str(e)}")
            return text

    def process_query(self, query: str, location: str = None, target_lang: str = "ur") -> Dict:
        """Process a farmer's query, retrieve context, generate answer, and translate."""
        try:
            # Check offline cache first
            if query in self.offline_cache and not location:
                answer = self.offline_cache[query]
                translated_answer = self.translate_answer(answer, target_lang)
                return {
                    "answer": answer,
                    "translated_answer": translated_answer,
                    "context": [{"text": "Cached answer", "metadata": {"source": "offline_cache"}}]
                }
            
            # Retrieve context
            context = self.retrieve_context(query)
            
            # Fetch weather data if location provided
            if location:
                weather_info = self.fetch_weather_data(location)
                if weather_info and "error" not in weather_info:
                    weather_context = f"Weather in {location}: {weather_info['weather'][0]['description']}, Temp: {weather_info['main']['temp']}°C"
                    context.append({"text": weather_context, "metadata": {"source": "weather_api"}})
            
            # Generate and translate answer
            answer = self.generate_answer(query, context)
            translated_answer = self.translate_answer(answer, target_lang)
            
            return {
                "answer": answer,
                "translated_answer": translated_answer,
                "context": context
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {"error": "Failed to process query"}

if __name__ == "__main__":
    rag = AgroDocRAG()