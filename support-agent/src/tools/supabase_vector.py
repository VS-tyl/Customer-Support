import os
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
except Exception:
    create_client = None

try:
    from langchain_community.vectorstores import SupabaseVectorStore
except Exception:
    SupabaseVectorStore = None

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except Exception:
    GoogleGenerativeAIEmbeddings = None

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_supabase_client = None
_embeddings = None


def _init_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    if create_client is None:
        raise RuntimeError("supabase client library is not installed")
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY not set in environment")
    _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase_client


def _init_embeddings():
    global _embeddings
    if _embeddings is not None:
        return _embeddings
    if GoogleGenerativeAIEmbeddings is None:
        raise RuntimeError("GoogleGenerativeAIEmbeddings is not available (missing package)")
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in environment")
    _embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=GEMINI_API_KEY)
    return _embeddings


def get_vectorstore():
    """Return a SupabaseVectorStore instance or None.

    This function tries to initialize the supabase client and embeddings lazily.
    If required libraries or environment variables are missing, it returns None
    and prints a helpful message instead of crashing the import.
    """
    if SupabaseVectorStore is None:
        print("Warning: SupabaseVectorStore is not available (optional dependency missing). RAG disabled.")
        return None

    try:
        client = _init_supabase_client()
        emb = _init_embeddings()
    except Exception as e:
        print(f"Warning: failed to initialize Supabase vectorstore: {e}")
        return None

    vectorstore = SupabaseVectorStore(
        supabase_client=client,
        table_name="documents",
        query_name="match_documents",
        embedding=emb,
    )
    return vectorstore