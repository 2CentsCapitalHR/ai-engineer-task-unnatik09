import glob
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

# Use SentenceTransformerEmbeddings (not HuggingFaceEmbeddings) to avoid deprecation warning
EMBED = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def build_store(src_dir="assets/legal_refs", dst="assets/chroma_index"):
    import glob, os
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import SentenceTransformerEmbeddings
    from langchain.vectorstores import Chroma

    EMBED = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    docs = []
    for pdf in glob.glob(os.path.join(src_dir, "**", "*.pdf"), recursive=True):
        print(f"Loading {pdf}...")
        try:
            loaded = PyPDFLoader(pdf).load()
            print(f"  -> loaded {len(loaded)} pages")
            docs += loaded
        except Exception as e:
            print(f"  -> failed: {e}")

    if not docs:
        raise RuntimeError("No documents loaded. Check your path or PDF content.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    print(f"Total chunks: {len(chunks)}")

    os.makedirs(dst, exist_ok=True)
    Chroma.from_documents(chunks, EMBED, persist_directory=dst).persist()
    print("Vector store built successfully!")

def load_store(dst="assets/chroma_index"):
    # Add debug print to show what files exist in the directory
    import os
    print(f"Trying to load vector store from: {dst}")
    if not os.path.exists(dst):
        print(f"Directory {dst} does not exist!")
    else:
        print(f"Directory {dst} contents: {os.listdir(dst)}")
    return Chroma(persist_directory=dst, embedding_function=EMBED)
