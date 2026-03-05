import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from smart_agent.rag import (
    VectorStore,
    BgeEmbedding,
    ReadFiles,
    Documents,
    GSSCPipeline,
    MQESearch,
    HyDESearch,
    HybridSearch,
)
from smart_agent.rag.reranker import BgeReranker


def rag_basic_demo():
    print("=" * 80)
    print("RAG Basic Demo")
    print("=" * 80)
    
    print("\n1. Initializing components...")
    try:
        embeddings = BgeEmbedding()
        vector_store = VectorStore(dim=1024)
        
        print("   ✓ Embeddings initialized")
        print("   ✓ Vector store initialized")
        
    except Exception as e:
        print(f"   ⚠ Note: Some components may require additional dependencies: {e}")
        print("   Continuing with demo anyway...")
        return
    
    print("\n2. Adding sample documents...")
    sample_docs = [
        "SmartAgent is a comprehensive AI agent framework with advanced RAG capabilities.",
        "The RAG system includes vector search, embeddings, and reranking capabilities.",
        "Multiple memory types are supported: working, episodic, semantic, and perceptual.",
        "Various tools are available: Python interpreter, search, note-taking, terminal, and more."
    ]
    
    try:
        for i, doc in enumerate(sample_docs):
            embedding = embeddings.embed(doc)
            vector_store.add(embedding, doc)
        
        print(f"   ✓ Added {len(sample_docs)} documents")
        
    except Exception as e:
        print(f"   ⚠ Error adding documents: {e}")
        return
    
    print("\n3. Performing search...")
    query = "What features does SmartAgent have?"
    
    try:
        query_embedding = embeddings.embed(query)
        results = vector_store.search(query_embedding, top_k=3)
        
        print(f"   Query: {query}")
        print(f"   Results found: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"\n   Result {i}:")
            print(f"   {result.get('text', '')[:100]}...")
            
    except Exception as e:
        print(f"   ⚠ Error searching: {e}")


def rag_pipeline_demo():
    print("\n" + "=" * 80)
    print("RAG Pipeline Demo")
    print("=" * 80)
    
    print("\n1. GSSC Pipeline (Generate-Store-Search-Combine)")
    print("   - Generate: Enhance the query")
    print("   - Store: Add documents to vector store")
    print("   - Search: Retrieve relevant documents")
    print("   - Combine: Generate final answer")
    
    print("\n2. Advanced Search Methods")
    print("   - MQE (Multiple Query Expansion): Generate multiple query variations")
    print("   - HyDE (Hypothetical Document Embedding): Generate hypothetical answer first")
    print("   - Hybrid Search: Combine vector search with keyword search (BM25)")


def main():
    rag_basic_demo()
    rag_pipeline_demo()
    
    print("\n" + "=" * 80)
    print("RAG Demo completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
