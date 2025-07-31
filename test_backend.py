import requests
import json

# Test the backend
def test_backend():
    print("🔍 Testing PDF GPT Backend...")
    
    # Check health
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"📊 Documents loaded: {data.get('documents_loaded', 0)}")
        else:
            print("❌ Backend health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # List documents
    try:
        response = requests.get("http://127.0.0.1:5000/documents")
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            print(f"📚 Found {len(documents)} documents:")
            
            for doc in documents:
                print(f"  - {doc.get('filename', 'Unknown')} (ID: {doc.get('id', 'N/A')[:8]}...)")
                print(f"    Chunks: {doc.get('chunk_count', 0)}")
                
                # Test debug endpoint
                doc_id = doc.get('id')
                if doc_id:
                    debug_response = requests.get(f"http://127.0.0.1:5000/documents/{doc_id}/debug")
                    if debug_response.status_code == 200:
                        debug_data = debug_response.json()
                        print(f"    Debug info: {debug_data.get('total_chunks_in_metadata', 0)} chunks in metadata")
                        samples = debug_data.get('sample_chunks', [])
                        if samples:
                            print(f"    Sample text: {samples[0][:100]}...")
                    
                    # Test a simple search
                    test_query = "chapter"
                    chat_response = requests.post("http://127.0.0.1:5000/chat", json={
                        "document_id": doc_id,
                        "question": test_query
                    })
                    if chat_response.status_code == 200:
                        chat_data = chat_response.json()
                        answer = chat_data.get('answer', '')
                        sources = chat_data.get('sources', [])
                        print(f"    Test query '{test_query}': Found {len(sources)} sources")
                        if sources:
                            print(f"    First source: {sources[0][:100]}...")
                    
        else:
            print("❌ Cannot list documents")
    except Exception as e:
        print(f"❌ Error testing documents: {e}")

if __name__ == "__main__":
    test_backend()
