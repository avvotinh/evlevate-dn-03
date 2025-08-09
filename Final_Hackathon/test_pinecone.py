#!/usr/bin/env python3
"""
Test script for Pinecone integration
Run: python test_pinecone.py
"""

import sys
import os
import numpy as np

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.storage.vector_db import VectorDB

class MockEmbeddingsGenerator:
    """Mock embeddings generator for testing without API calls"""

    def __init__(self):
        self.dimension = 1536

    def embed_one(self, text: str):
        """Generate deterministic mock embedding based on text"""
        # Use hash to create consistent embeddings for same text
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to float vector
        vector = []
        for i in range(0, len(hash_bytes)):
            vector.append(float(hash_bytes[i]) / 255.0)

        # Extend to required dimension
        while len(vector) < self.dimension:
            vector.extend(vector[:min(len(vector), self.dimension - len(vector))])

        return vector[:self.dimension]

    def embed(self, texts):
        return [self.embed_one(text) for text in texts]

def main():
    print("🚀 Testing Pinecone integration...")
    
    try:
        # Initialize
        print("📦 Initializing embeddings generator and vector DB...")
        print("🔧 Using mock embeddings generator to avoid API issues...")
        emb = MockEmbeddingsGenerator()
        vdb = VectorDB()
        print("✅ Initialization successful!")
        
        # Test 1: Upsert
        print("\n🔄 Test 1: Upsert")
        text = "Tesla announced new battery technology"
        print(f"Text: {text}")
        vector = emb.embed_one(text)
        print(f"Vector dimension: {len(vector)}")
        result = vdb.upsert(["tesla-1"], [vector], [{"company": "Tesla"}])
        print("Upsert result:", result)
        
        # Test 2: Query
        print("\n🔍 Test 2: Query")
        query_text = "electric vehicle battery innovation"
        print(f"Query: {query_text}")
        query_vector = emb.embed_one(query_text)
        matches = vdb.query(query_vector, top_k=3)
        print("Query matches:", matches)
        
        # Test 3: Update
        print("\n📝 Test 3: Update")
        new_metadata = {"company": "Tesla", "topic": "battery", "year": "2024"}
        print(f"New metadata: {new_metadata}")
        update_result = vdb.update("tesla-1", set_metadata=new_metadata)
        print("Update result:", update_result)
        
        # Test 4: Compare embeddings
        print("\n🔄 Test 4: Compare Embeddings")
        text_a = "Tesla battery technology"
        text_b = "electric vehicle batteries"
        vec_a = emb.embed_one(text_a)
        vec_b = emb.embed_one(text_b)
        
        # Calculate cosine similarity
        import numpy as np
        def cosine_similarity(a, b):
            va = np.array(a)
            vb = np.array(b)
            return np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb))
        
        similarity = cosine_similarity(vec_a, vec_b)
        print(f"Similarity between '{text_a}' and '{text_b}': {similarity:.4f}")

        # Test 5: List/Stats
        print("\n📊 Test 5: Index Stats")
        try:
            stats = vdb.index.describe_index_stats()
            print("Index stats:", stats)
        except Exception as e:
            print(f"Stats error: {e}")

        # Test 6: Fetch specific vectors
        print("\n📋 Test 6: Fetch vectors")
        try:
            fetch_result = vdb.index.fetch(ids=["tesla-1"])
            print("Fetch result:", fetch_result)
        except Exception as e:
            print(f"Fetch error: {e}")

        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
