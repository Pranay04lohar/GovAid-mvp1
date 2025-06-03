import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = "legal_data"
VECTORSTORE_DIR = "vectorstore"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

def embed_all():
    """
    Loads PDF documents, splits them into chunks, generates embeddings,
    creates a FAISS vector store, and saves it to disk.
    """
    # Create vectorstore directory if it doesn't exist
    if not os.path.exists(VECTORSTORE_DIR):
        os.makedirs(VECTORSTORE_DIR)

    # Load documents
    print(f"Loading documents from {DATA_DIR}...")
    if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
        print(f"Directory {DATA_DIR} is empty or does not exist.")
        print("Please create it and add your PDF files.")
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        try:
            from reportlab.pdfgen import canvas
            dummy_pdf_path = os.path.join(DATA_DIR, "dummy_document.pdf")
            if not os.path.exists(dummy_pdf_path):
                c = canvas.Canvas(dummy_pdf_path)
                c.drawString(100, 750, "This is a dummy PDF document for testing the ingestion pipeline.")
                c.drawString(100, 735, "It contains some sample text about legal matters.")
                c.save()
                print(f"Created a dummy PDF for testing: {dummy_pdf_path}")
                print("You should replace this with actual legal documents.")
        except ImportError:
            print("ReportLab not found. Cannot create dummy PDF. Please add PDFs to 'legal_data' manually.")
        except Exception as e:
            print(f"Error creating dummy PDF: {e}")

    pdf_files = []
    if os.path.exists(DATA_DIR):
        pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF documents found in {DATA_DIR}. Please add some PDF files to this directory. Exiting.")
        return

    try:
        loader = DirectoryLoader(
            DATA_DIR,
            glob="*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True,
            silent_errors=True
        )
        documents = loader.load()
        if not documents:
            print(f"No PDF documents were successfully loaded from {DATA_DIR}. Please check file integrity and permissions. Exiting.")
            return
        print(f"Loaded {len(documents)} document(s)/pages (PyPDFLoader loads each page as a document).")
    except Exception as e:
        print(f"Error loading documents: {e}")
        return

    # Split documents into chunks
    print("Splitting documents into chunks...")
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        texts = text_splitter.split_documents(documents)
        if not texts:
            print("No text chunks were generated. This might happen if documents are empty or unparseable. Exiting.")
            return
        print(f"Split into {len(texts)} chunks.")
    except Exception as e:
        print(f"Error splitting documents: {e}")
        return

    # Generate embeddings
    print(f"Generating embeddings (Model: {DEFAULT_EMBEDDING_MODEL}). This may take a while...\nMake sure you have 'pip install sentence-transformers langchain-huggingface' and internet access for model download.")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL)
    except Exception as e:
        print(f"Error initializing HuggingFaceEmbeddings: {e}")
        print("Please ensure you have the 'sentence-transformers' and 'langchain-huggingface' libraries installed and internet connectivity.")
        return

    # Create FAISS vector store
    print("Creating FAISS vector store...")
    try:
        db = FAISS.from_documents(texts, embeddings)
    except Exception as e:
        print(f"Error creating FAISS vector store: {e}")
        return

    # Save FAISS index
    faiss_index_path = os.path.join(VECTORSTORE_DIR, "faiss_index")
    print(f"Saving FAISS index to {faiss_index_path}...")
    try:
        db.save_local(faiss_index_path)
        print("FAISS index saved successfully.")
    except Exception as e:
        print(f"Error saving FAISS index: {e}")
        return

    print("Data ingestion and embedding complete.")

if __name__ == "__main__":
    embed_all() 