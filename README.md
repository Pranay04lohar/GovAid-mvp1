# Demo Video:

https://github.com/user-attachments/assets/7c171346-9cb2-4909-a015-cfa187f88e82


# YojnaBuddy Backend

This directory contains the backend components for the YojnaBuddy project, which scrapes and serves government scheme data.

## Project Structure

- `fetch_all_scheme_urls.py`: Script to scrape all scheme URLs by category
- `scraper.py`: Core scraping functionality for extracting scheme details
- `batch_scraper.py`: Script to process all URLs from category JSON files
- `validate_data.py`: Script to validate and clean the database data
- `api.py`: FastAPI backend to serve the scheme data
- `database.py`: Database operations and schema
- `output/`: Directory containing category-wise scheme URLs
- `data_export/`: Directory for exported data for manual review
- `yojnabuddy.db`: SQLite database containing all scheme data

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install
```

## Usage

### 1. Scrape Scheme URLs (Already Completed)

The script `fetch_all_scheme_urls.py` has already been run to collect all scheme URLs by category. The results are stored in the `output/` directory.

### 2. Scrape Scheme Details

To scrape detailed information for all schemes:

```bash
python batch_scraper.py
```

This will:

- Read URLs from all JSON files in `output/`
- Scrape details for each scheme
- Save the data to `yojnabuddy.db`

### 3. Validate Data

To validate and clean the database:

```bash
python validate_data.py
```

This will:

- Check for missing fields
- Identify duplicates
- Verify related data
- Export data for manual review to `data_export/`

### 4. Run API Server

To start the FastAPI server:

```bash
python api.py
```

The API will be available at `http://localhost:8000`

API Endpoints:

- `GET /`: Welcome message
- `GET /schemes`: List all schemes (with filtering)
- `GET /schemes/{id}`: Get detailed scheme information
- `GET /categories`: List all categories
- `GET /states`: List all states

API Documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Schema

The SQLite database (`yojnabuddy.db`) contains the following tables:

1. `schemes`: Main scheme information

   - id (PRIMARY KEY)
   - name
   - description
   - state
   - url
   - created_at
   - updated_at

2. `categories`: Scheme categories

   - id (PRIMARY KEY)
   - scheme_id (FOREIGN KEY)
   - category

3. `benefits`: Scheme benefits

   - id (PRIMARY KEY)
   - scheme_id (FOREIGN KEY)
   - benefit

4. `eligibility_criteria`: Eligibility requirements

   - id (PRIMARY KEY)
   - scheme_id (FOREIGN KEY)
   - criterion

5. `required_documents`: Required documents

   - id (PRIMARY KEY)
   - scheme_id (FOREIGN KEY)
   - document

6. `faqs`: Frequently asked questions
   - id (PRIMARY KEY)
   - scheme_id (FOREIGN KEY)
   - question
   - answer

## Development

- Use `test_scraper.py` to test the scraping functionality
- Use `test_single_scheme.py` to test scraping a single scheme
- Use `inspect_page.py` to debug page structure

## Notes

- The scraper includes rate limiting and error handling
- The API includes CORS middleware for frontend integration
- All data is validated before being saved to the database
- The database uses foreign key constraints for data integrity

### Backend Workflow

1. First, it fetches scheme URLs using `fetch_all_scheme_urls.py`
2. Then processes these URLs in batches using `batch_scraper.py`
3. Stores the data in SQLite database `(yojnabuddy.db)`
4. Validates and cleans the data using `validate_data.py`
5. Serves the data through a FastAPI server `(api.py)`

## Legal AI Chatbot Architecture and Components

This chatbot utilizes a Retrieval Augmented Generation (RAG) architecture to answer questions based on a provided set of legal documents.

### Architecture Overview:

1.  **Offline Processing (Data Ingestion & Indexing via `legal_chatbot_logic/ingest.py`)**:

    - Legal documents (PDFs from the `legal_data` folder) are loaded and their text content is extracted.
    - The extracted text is split into smaller, manageable chunks.
    - These text chunks are converted into numerical vector representations (embeddings) using a sentence transformer model (e.g., `sentence-transformers/all-mpnet-base-v2`).
    - The embeddings and their corresponding text chunks are stored in a FAISS vector store (saved to `vectorstore/faiss_index`), creating a searchable index.

2.  **Online Processing (Question Answering via `legal_chatbot_logic/qa_logic.py`)**:
    - When a user submits a question, the system initializes the QA pipeline.
    - The user's question is converted into an embedding using the same sentence transformer model.
    - The FAISS vector store is queried with the question's embedding to find the most semantically similar text chunks from the indexed documents.
    - These retrieved text chunks (the context) are combined with the original user question using a predefined prompt template.
    - This combined prompt (context + question) is then sent to a Google Generative AI model (e.g., `gemini-1.5-flash-latest`).
    - The LLM generates an answer based on the provided context and its general knowledge.
    - The answer and the source documents used for retrieval are returned to the user.

### Key Components:

- **Document Loaders (`langchain_community.document_loaders`)**:
  - `DirectoryLoader`: Loads all specified files (e.g., PDFs) from a directory.
  - `PyPDFLoader`: Specifically extracts text content from PDF files.
- **Text Splitter (`langchain.text_splitter`)**:
  - `RecursiveCharacterTextSplitter`: Splits long texts into smaller chunks with optional overlap to maintain context.
- **Embeddings Model (`langchain_huggingface.HuggingFaceEmbeddings`)**:
  - Uses a pre-trained model (e.g., `sentence-transformers/all-mpnet-base-v2`) to convert text chunks into dense vector embeddings.
- **Vector Store (`langchain_community.vectorstores.FAISS`)**:
  - `FAISS`: A library for efficient similarity search and clustering of dense vectors; used here to store and retrieve document embeddings.
- **Large Language Model (LLM - `langchain_google_genai.ChatGoogleGenerativeAI`)**:
  - Utilizes a powerful Google Generative AI model (e.g., `gemini-1.5-flash-latest` accessed via API with `GOOGLE_API_KEY`) to understand the question and context, and generate a coherent answer.
- **Prompt Template (`langchain.prompts.PromptTemplate`)**:
  - Defines a structured way to present the user's question and the retrieved context to the LLM for optimal answer generation.
- **RetrievalQA Chain (`langchain.chains.RetrievalQA`)**:
  - Orchestrates the entire RAG process: takes a user query, retrieves relevant documents from the vector store, formats the prompt, passes it to the LLM, and returns the result.
- **Core Python Scripts (`legal_chatbot_logic/`)**:
  - `ingest.py`: Manages the offline data ingestion pipeline (loading, splitting, embedding, storing in FAISS).
  - `qa_logic.py`: Manages the online question-answering pipeline (loading resources, handling user queries, and generating responses using the RAG chain).
