#!/usr/bin/env python3
"""
Upload ALL processed documents to Pinecone
"""

import sys
import os
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.storage.vector_db import VectorDB
from test_pinecone import MockEmbeddingsGenerator

def main():
    print("🚀 Uploading ALL documents to Pinecone...")
    
    # Load processed documents
    if not os.path.exists('db/processed_documents.json'):
        print("❌ No processed documents found. Run: python db/data_processor.py")
        return
    
    with open('db/processed_documents.json', 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"📋 Found {len(documents)} documents to upload")
    
    # Initialize
    try:
        emb = MockEmbeddingsGenerator()
        vdb = VectorDB()
        print("✅ Connected to Pinecone")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Upload all documents in batches
    batch_size = 20
    uploaded_count = 0
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        try:
            # Prepare batch
            ids = []
            vectors = []
            metadatas = []
            
            for doc in batch:
                vector = emb.embed_one(doc['text'])
                ids.append(doc['id'])
                vectors.append(vector)
                metadatas.append(doc['metadata'])
            
            # Upload batch
            result = vdb.upsert(ids, vectors, metadatas)
            uploaded_count += len(ids)
            
            print(f"✅ Batch {i//batch_size + 1}: Uploaded {len(ids)} documents (Total: {uploaded_count})")
            
        except Exception as e:
            print(f"❌ Batch {i//batch_size + 1} failed: {e}")
    
    print(f"\n🎉 Upload completed! Total uploaded: {uploaded_count}/{len(documents)}")
    
    # Check final stats
    try:
        stats = vdb.list_stats()
        print(f"\n📊 Final Pinecone Stats:")
        print(f"Total vectors: {stats.get('total_vector_count', 'Unknown')}")
        print(f"Dimension: {stats.get('dimension', 'Unknown')}")
    except Exception as e:
        print(f"⚠️  Could not get stats: {e}")

if __name__ == "__main__":
    main()
