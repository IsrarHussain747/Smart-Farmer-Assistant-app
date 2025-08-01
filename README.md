

# 🌾 AgroDoc: Smart Farmer Assistant

**AgroDoc** is a multilingual AI-powered assistant designed to support low-tech farmers by answering crop, soil, and weather-related queries. Using cutting-edge **Retrieval-Augmented Generation (RAG)**, AgroDoc provides context-aware responses based on trusted agricultural documents and real-time weather data, in **English** or **Urdu**.

---

## 🚀 Features

* 🌐 **Multilingual Support** — Ask questions in English or Urdu
* 📄 **PDF Document Ingestion** — Upload agricultural manuals or research papers
* ☁️ **Weather Integration** — Real-time, location-specific weather data
* 🔌 **Offline Support** — Basic functionalities available without internet
* 🧑‍🌾 **User-Centric Design** — Simple UI built with non-technical users in mind

---

## 🧠 System Architecture

| Layer         | Technology                                           |
| ------------- | ---------------------------------------------------- |
| **Frontend**  | Streamlit (for intuitive web-based interface)        |
| **Backend**   | Flask (API handling and RAG logic)                   |
| **LLM**       | Groq's Llama3-8b-8192 model                          |
| **Embedding** | HuggingFace: `paraphrase-multilingual-MiniLM-L12-v2` |
| **Vector DB** | ChromaDB (document retrieval and storage)            |
| **APIs**      | OpenWeatherMap (weather) + Google Translate (Urdu)   |

---

## 🛠️ Setup Instructions

### ✅ Prerequisites

* Python 3.8+
* [virtualenv](https://docs.python.org/3/library/venv.html) (recommended)

### 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/agrodoc.git
   cd agrodoc
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate       # For Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:

   ```env
   GROQ_API_KEY="your_groq_api_key"
   WEATHER_API_KEY="your_openweathermap_api_key"
   BACKEND_URL="http://localhost:5000"
   ```

---

## ▶️ Running the Application

### Start the Backend

```bash
python backend/main.py
```

### Start the Frontend (in another terminal)

```bash
streamlit run frontend/app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📡 API Endpoints

| Method | Endpoint  | Description                           |
| ------ | --------- | ------------------------------------- |
| GET    | `/health` | Health check for backend service      |
| POST   | `/ingest` | Ingest new documents into ChromaDB    |
| POST   | `/query`  | Get an AI-generated answer to a query |

### Sample Request (Query)

```json
{
  "query": "What crops are best in August?",
  "location": "Gilgit",
  "target_lang": "ur"
}
```

---

## 📁 Project Structure

```
agrodoc/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── rag.py
│   └── embedding.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
├── .env
└── README.md
```

---

## 🌍 Use Cases

* Localized farming recommendations in native languages
* Smart weather-based crop planning
* On-field support for remote or low-infrastructure regions

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo, open issues, or submit pull requests.

---

## 📬 Contact

**Israr Hussain**
📧 Email: [your.email@example.com](israrmir606@gmail.com)
🔗 GitHub: [github.com/yourusername](https://github.com/IsrarHussain747)

