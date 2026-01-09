# ============================================================================
# IMPORTS
# ============================================================================

# Import document loading utilities from LangChain Community package
# - DirectoryLoader: Loads multiple documents from a directory
# - TextLoader: Handles loading individual text files

# langchain_community.document_loaders provides classes to load various data types 
# (text, PDF, CSV, web pages, etc.) into LangChain's standard Document format, 
# enabling consistent processing for LLM applications, 
# with examples like CSVLoader, PyPDFLoader, UnstructuredPDFLoader, 
# and DirectoryLoader for handling multiple files, 
# supporting both standard and lazy loading for efficiency. 

from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Import text splitting utility for breaking documents into smaller chunks
# RecursiveCharacterTextSplitter intelligently splits text while trying to
# maintain semantic coherence by splitting on paragraphs, sentences, then words
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import embeddings model from the HuggingFace integration
# This converts text into numerical vector representations for similarity search
from langchain_huggingface import HuggingFaceEmbeddings

# Import Chroma vector database for storing and retrieving document embeddings
# Chroma is a lightweight, open-source vector database optimized for AI applications
from langchain_community.vectorstores import Chroma

# Standard library for operating system operations (imported but not used in this code)
import os

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Path to the directory containing source documents to be ingested
# All .txt files in this directory and subdirectories will be processed
DATA_PATH = "./data"

# Path where the Chroma vector database will be persisted
# This allows the database to be reused across different program runs
DB_PATH = "./chroma"

# ============================================================================
# MAIN INGESTION FUNCTION
# ============================================================================

def ingest_documents():
    """
    Ingest documents from a directory into a Chroma vector database.
    
    This function performs the following steps:
    1. Load all .txt files from the specified directory
    2. Split documents into smaller chunks for better retrieval
    3. Generate embeddings for each chunk using a HuggingFace model
    4. Store the chunks and embeddings in a Chroma vector database
    
    The resulting vector database can be used for semantic search,
    question answering, or retrieval-augmented generation (RAG) systems.
    """
    
    # ========================================================================
    # STEP 1: LOAD DOCUMENTS
    # ========================================================================
    
    # Create a DirectoryLoader to recursively load all .txt files
    loader = DirectoryLoader(
        DATA_PATH,              # Directory to search for documents
        glob="**/example*.txt",        # Pattern: all subdirectories' all txt files
        # "**/" searches all subdirectories,
        # "*.txt" matches all text files
        loader_cls=TextLoader  # Class used to load each individual file
    )
    
    # Execute the loading process and return a list of Document objects
    # Each Document contains the text content and metadata (like file path)
    documents = loader.load()
    
    # ========================================================================
    # STEP 2: SPLIT DOCUMENTS INTO CHUNKS
    # ========================================================================
    
    # Create a text splitter with specific parameters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # Maximum size of each chunk in characters
                            # Smaller chunks = more precise retrieval but more chunks
                            # Larger chunks = more context but less precise
        
        chunk_overlap=100    # Number of characters to overlap between chunks
                            # Overlap ensures context isn't lost at chunk boundaries
                            # e.g., if a sentence is split, the overlap captures it
    )
    
    # Split all loaded documents into smaller chunks
    # Returns a list of Document objects, each representing one chunk
    chunks = splitter.split_documents(documents)
    
    # ========================================================================
    # STEP 3: CREATE EMBEDDINGS MODEL
    # ========================================================================
    
    # Initialize the HuggingFace embeddings model
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"  
        # Lightweight sentence transformer model 
        # 384-dimensional embeddings
        # ~80MB model size
        # Good balance of speed and quality
        # Trained on 1B+ sentence pairs
    )
    
    # ========================================================================
    # STEP 4: CREATE VECTOR DATABASE
    # ========================================================================
    
    # Create a Chroma vector database from the document chunks
    vectordb = Chroma.from_documents(
        documents=chunks,              # The chunked documents to store
        embedding=embeddings,          # The embedding model to use
        # Chroma will automatically generate embeddings for each chunk
        persist_directory=DB_PATH      
        # Where to save the database on disk
        # Enables persistence across sessions
    )
    
    # Note: In newer versions of ChromaDB, the database automatically persists
    # to the specified directory, so no explicit .persist() call is needed
    
    # ========================================================================
    # STEP 5: CONFIRMATION OUTPUT
    # ========================================================================
    
    # Print confirmation message showing how many chunks were processed
    # Useful for debugging and monitoring the ingestion process
    print(f"Ingested {len(chunks)} chunks into ChromaDB.")

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Execute the document ingestion process
    ingest_documents()