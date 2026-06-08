# scripts/test_connections.py
import os
import sys
import logging

# Ensure root directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("connection_test")

from dotenv import load_dotenv
load_dotenv()

def test_groq():
    logger.info("🧪 Test 1: Verifying connection to Groq API...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("❌ GROQ_API_KEY is missing from environment variables.")
        return False
    
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)
        res = llm.invoke("Say 'connection verified' in exactly two words.")
        response_text = res.content.strip().lower()
        if "connection" in response_text or "verified" in response_text:
            logger.info("🟢 Groq API connection successful. Response: '%s'", res.content.strip())
            return True
        else:
            logger.warning("⚠️ Groq connected but returned unexpected response: '%s'", res.content.strip())
            return True
    except Exception as e:
        logger.error("❌ Failed to connect to Groq API: %s", e)
        return False

def test_supabase():
    logger.info("🧪 Test 2: Verifying connection to Supabase database...")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        logger.info("ℹ️ Supabase environment variables are missing. Using local fallback (Chroma / JSON).")
        return "local"
        
    try:
        from supabase import create_client
        client = create_client(url, key)
        
        # Test writing a temporary state to state_store
        logger.info("   Writing test state to 'state_store' table...")
        test_state = {"test_connection": "successful", "timestamp": "now"}
        client.table("state_store").upsert({"id": "test_connection", "state": test_state}).execute()
        
        # Test reading the state
        logger.info("   Reading test state from 'state_store' table...")
        res = client.table("state_store").select("state").eq("id", "test_connection").execute()
        if res.data and res.data[0]["state"]["test_connection"] == "successful":
            logger.info("   Successfully validated read/write operations.")
        else:
            raise ValueError("Read mismatch or empty response.")
            
        # Clean up test row
        logger.info("   Cleaning up test connection row...")
        client.table("state_store").delete().eq("id", "test_connection").execute()
        
        logger.info("🟢 Supabase DB connection successful.")
        return "supabase"
    except Exception as e:
        logger.error("❌ Failed to connect to Supabase: %s", e)
        logger.error("   Ensure you ran the SQL setup script to create tables in your Supabase SQL editor.")
        return False

def test_vectorstore():
    logger.info("🧪 Test 3: Verifying Vector Store connectivity...")
    try:
        from rag.vectorstore import get_vectorstore
        db = get_vectorstore()
        
        # Perform a quick similarity search test
        logger.info("   Running query similarity search...")
        results = db.similarity_search("AMD Hackathon", k=1)
        
        # Check type
        from langchain_community.vectorstores import SupabaseVectorStore
        if isinstance(db, SupabaseVectorStore):
            logger.info("🟢 Vector Store: Connected to Supabase pgvector.")
        else:
            logger.info("🟢 Vector Store: Connected to local Chroma DB.")
            
        if results:
            logger.info("   Successfully retrieved matching document chunk: '%s...'", results[0].page_content[:60])
        else:
            logger.info("   Search completed successfully, but returned 0 results (empty database).")
        return True
    except Exception as e:
        logger.error("❌ Failed to initialize Vector Store: %s", e)
        return False

def main():
    print("\n==========================================")
    print("🔍 CO-FOUNDER MEMORY DIAGNOSTIC SUITE")
    print("==========================================\n")
    
    groq_ok = test_groq()
    print()
    
    db_status = test_supabase()
    print()
    
    vs_ok = test_vectorstore()
    print()
    
    print("==========================================")
    print("📋 DIAGNOSTIC RESULTS")
    print("==========================================")
    print("Groq Connection:       " + ("🟢 OK" if groq_ok else "❌ FAILED"))
    
    if db_status == "supabase":
        print("Database Mode:         " + "🟢 SUPABASE (PROD)")
    elif db_status == "local":
        print("Database Mode:         " + "ℹ️ LOCAL FALLBACK (DEV)")
    else:
        print("Database Mode:         " + "❌ FAILED")
        
    print("Vector Store status:   " + ("🟢 OK" if vs_ok else "❌ FAILED"))
    print("==========================================\n")
    
    if groq_ok and db_status and vs_ok:
        print("🎉 All systems verified and connected successfully!")
    else:
        print("⚠️ Some checks failed. Please check the logs above to troubleshoot.")

if __name__ == "__main__":
    main()
