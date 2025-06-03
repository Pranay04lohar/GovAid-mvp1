import os
import traceback
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # Embeddings can remain HuggingFace
#from langchain_community.embeddings import HuggingFaceEmbeddings
#from langchain_huggingface import HuggingFaceEndpoint # Removing HuggingFaceEndpoint
# from langchain_google_genai import ChatGoogleGenerativeAI # Import for Gemini

from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai # Import for listing models

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
# from langchain_huggingface import HuggingFaceEndpoint # Using deprecated HuggingFaceHub instead
# from langchain_openai import ChatOpenAI # Commented out OpenAI
# from huggingface_hub import InferenceClient # No longer needed for this version

# # --- Debug: Check provider_mapping --- # Removed as it causes import error in some versions
# from huggingface_hub.inference._providers import provider_mapping 

# --- Configuration ---
VECTORSTORE_PATH = "vectorstore/faiss_index"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
# DEFAULT_LLM_REPO_ID = "google/flan-t5-base" # No longer needed for HuggingFace
# DEFAULT_LLM_TASK = "text-generation" # No longer needed for HuggingFace
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash-latest" # Using Gemini 1.5 Flash latest

# --- Function to List Models ---
def list_available_models():
    """Lists available Gemini models."""
    print("\n--- Listing Available Google Generative AI Models ---")
    try:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model name: {m.name}, Supported methods: {m.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")
    print("-----------------------------------------------------\n")

# --- Custom Prompt Template ---
PROMPT_TEMPLATE = """
  You are a helpful legal AI assistant. Use the following pieces of context to answer the question at the end.
  If the context is not helpful, use your own legal knowledge to provide a useful answer.

  Provide a comprehensive and detailed answer.

Context:
{context}

Question: {question}

Helpful Answer:
"""

def load_custom_prompt():
    """
    Loads the custom prompt template.
    """
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE, input_variables=["context", "question"]
    )
    return prompt

def retrieval_qa_chain(llm, prompt, db):
    """
    Creates and returns a RetrievalQA chain.
    """
    retriever = db.as_retriever(search_kwargs={"k": 2})
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return chain

# Removed direct_hf_client_test as we are focusing on LangChain integration with downgraded libraries

def qa_pipeline():
    """
    Initializes and returns the full QA pipeline.
    """
    print("Initializing QA pipeline with Google Gemini...")

    # Load Embeddings
    try:
        print(f"Loading HuggingFace embeddings (Model: {DEFAULT_EMBEDDING_MODEL})...")
        embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL)
    except Exception as e:
        print(f"Error loading HuggingFaceEmbeddings: {e}")
        return None

    # Load FAISS Vector Store
    if not os.path.exists(VECTORSTORE_PATH):
        print(f"Vector store not found at {VECTORSTORE_PATH}. Please run ingest.py first.")
        return None
    try:
        print(f"Loading FAISS vector store from {VECTORSTORE_PATH}...")
        db = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
        print("FAISS vector store loaded successfully.")
    except Exception as e:
        print(f"Error loading FAISS vector store: {e}")
        return None

    # Load LLM using ChatGoogleGenerativeAI
    llm = None 
    try:
        print(f"Loading LLM from Google (Model: {DEFAULT_GEMINI_MODEL})...")
        if not os.getenv("GOOGLE_API_KEY"):
            print("GOOGLE_API_KEY not found in environment variables.")
            return None
        
        llm = ChatGoogleGenerativeAI(
            model=DEFAULT_GEMINI_MODEL,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            # Optional: Add temperature, top_p, etc. if needed
            # temperature=0.7,
            convert_system_message_to_human=True # Often helpful for RAG prompts
        )
        print(f"ChatGoogleGenerativeAI instance created for model {DEFAULT_GEMINI_MODEL}.")

    except Exception as e:
        print(f"Error during ChatGoogleGenerativeAI loading (Type: {type(e)}):")
        print(traceback.format_exc())
        return None
    
    if not llm:
        print("LLM object is None after ChatGoogleGenerativeAI loading attempt. Cannot proceed.")
        return None

    # Load Prompt
    print("Loading custom prompt...")
    prompt = load_custom_prompt()

    # Create RetrievalQA Chain
    print("Creating RetrievalQA chain...")
    qa_chain = retrieval_qa_chain(llm, prompt, db)
    print("QA pipeline initialized successfully with Gemini.")
    return qa_chain

# --- Example Usage (can be run directly or imported) ---
if __name__ == "__main__":
    print("Starting QA example with Google Gemini...")
    
    # List models before starting the pipeline
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY not found in environment variables. Cannot list models or run pipeline.")
    else:
        list_available_models() # Call the function to list models

    chain = qa_pipeline()

    if chain:
        print("\n--- QA System Ready (Powered by Google Gemini) ---")
        print("Ask a question about your legal documents. Type 'exit' to quit.")
        
        while True:
            user_question = ""
            try:
                user_question = input("\nYour question: ")
            except KeyboardInterrupt:
                print("\nExiting QA system due to user interruption.")
                break
            
            if user_question.lower() == 'exit':
                print("Exiting QA system.")
                break
            if not user_question.strip():
                print("Please enter a question.")
                continue

            print("Processing your question with Gemini...")
            try:
                bot_output = chain.invoke({"query": user_question})
                
                print("\nAnswer:")
                print(bot_output["result"])
                
                print("\nSource Documents:")
                if bot_output.get("source_documents"):
                    for i, doc in enumerate(bot_output["source_documents"]):
                        source = doc.metadata.get('source', 'Unknown')
                        page = doc.metadata.get('page', 'N/A')
                        print(f"--- Document {i+1} (Source: {source}, Page: {page}) ---")
                else:
                    print("No source documents were returned for this query.")
                print("--------------------")

            except Exception as e:
                print(f"Error during QA processing with Gemini (Type: {type(e)}):")
                print(traceback.format_exc())
    else:
        print("Failed to initialize QA pipeline with Gemini. Please check error messages above.") 