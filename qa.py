import os
from dotenv import load_dotenv

# Always use absolute import for local modules
import vector_store

load_dotenv()

SYSTEM = (
    "You are an ADGM legal assistant. "
    "Always cite ADGM regulations when answering (e.g., 'Companies Regulations 2020 s.6')."
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

_client_type = None
client = None
store = None

if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        _client_type = "groq"
    except Exception as e:
        print(f"GROQ client error: {e}")
        client = None

try:
    # Print debug info to help diagnose vector store loading
    print("Attempting to load vector store from assets/chroma_index ...")
    store = vector_store.load_store()
    print("Vector store loaded successfully.")
except Exception as e:
    print(f"Vector store load error: {e}")
    import traceback
    traceback.print_exc()
    store = None

def rag_ask(query, k=6):
    """st
    Retrieve relevant ADGM context from vector store and ask the configured LLM.
    If no LLM or store present, return a safe placeholder.
    """
    if store is None:
        return (
            "Legal rationale unavailable (RAG backend not configured). "
            "Vector store could not be loaded. Please ensure you have run the vector store build step "
            "and that the assets/chroma_index directory exists and is populated."
        )
    if client is None:
        return (
            "Legal rationale unavailable (RAG backend not configured). "
            "No LLM API key found or LLM client could not be initialized. "
            "Please set GROQ_API_KEY in your environment."
        )

    docs = store.similarity_search(query, k=k)
    context = "\n\n".join(d.page_content for d in docs)

    if _client_type == "groq":
        messages = [
            {"role":"system", "content":SYSTEM},
            {"role":"user", "content":f"---\nCONTEXT:\n{context}\n---\n\nQ: {query}\nA:"}
        ]
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            max_tokens=800
        )
        return resp.choices[0].message.content

    return "RAG/LLM invocation failed (unsupported client)."