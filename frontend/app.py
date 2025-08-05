import streamlit as st
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "https://xargham-farmer-app.hf.space")

st.title("AgroDoc: Smart Farmer Assistant")
st.markdown("Ask crop, soil, or weather-related questions and get advice in English or Urdu.")

# Query input section
st.header("Ask a Question")
query = st.text_input("Enter your farming question:", placeholder="e.g., How to improve wheat yield?")
location = st.text_input("Enter your location (optional):", placeholder="e.g., Lahore")
language = st.selectbox("Select language:", ["Urdu", "English"], index=0)

if st.button("Get Answer"):
    if query:
        target_lang = "ur" if language == "Urdu" else "en"
        try:
            # Send query to backend API
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"query": query, "location": location, "target_lang": target_lang}
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" not in result:
                # Show answer based on selected language
                if language == "English":
                    st.subheader("Answer")
                    st.write(result["answer"])
                    
                    # Only show sources if available
                    if "context" in result and result["context"]:
                        st.subheader("Sources Used")
                        for ctx in result["context"]:
                            st.write(f"- {ctx['text']} (Source: {ctx['metadata'].get('source', 'unknown')})")
                else:  # Urdu
                    st.subheader("جواب")
                    st.write(result["translated_answer"])
                    
                    # Only show sources if available
                    if "context" in result and result["context"]:
                        st.subheader("استعمال شدہ ذرائع")
                        for ctx in result["context"]:
                            st.write(f"- {ctx['text']} (Source: {ctx['metadata'].get('source', 'unknown')})")
            else:
                st.error(f"Error: {result['error']}")
        except requests.RequestException as e:
            st.error(f"Failed to connect to backend: {str(e)}")
    else:
        st.warning("Please enter a question.")

# Document upload section
st.header("Upload Agricultural Documents")
uploaded_file = st.file_uploader("Upload a document (PDF or text):", type=["txt", "pdf"])

if uploaded_file is not None:
    try:
        # Process based on file type
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type == 'txt':
            # For text files, decode and display preview
            document = uploaded_file.read().decode("utf-8")
            st.write("**Uploaded Document Preview:**")
            st.write(document[:500] + "..." if len(document) > 500 else document)
            document_content = document
        elif file_type == 'pdf':
            # For PDF files, just show confirmation
            document_content = uploaded_file.read()
            st.write(f"**PDF Uploaded:** {uploaded_file.name}")
            st.info("PDF content will be processed by the backend.")
        
        if st.button("Ingest Document"):
            try:
                # Send document to backend /ingest endpoint
                if file_type == 'txt':
                    # For text files, send as string
                    payload = {"documents": [document_content], "metadata": [{"source": uploaded_file.name}]}
                else:
                    # For PDFs, encode as base64 string
                    import base64
                    encoded_pdf = base64.b64encode(document_content).decode('utf-8')
                    payload = {"documents": [encoded_pdf], "metadata": [{"source": uploaded_file.name, "type": "pdf"}]}
                
                response = requests.post(
                    f"{BACKEND_URL}/ingest",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                if "error" not in result:
                    st.success(result["message"])
                else:
                    st.error(f"Error: {result['error']}")
            except requests.RequestException as e:
                st.error(f"Failed to ingest document: {str(e)}")
    except Exception as e:

        st.error(f"Error processing file: {str(e)}")


