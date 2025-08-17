#!/usr/bin/env python3
"""
Pinecone Methods - Complete toolkit for vector database operations
Usage: python db/pinecone_methods.py [method] [args]

Available methods:
- seedData: Load and upload all seed data to Pinecone
- upsert: Add/update vectors with embeddings
- query: Search similar vectors by text
- update: Update existing vector metadata
- compare: Compare similarity between two texts
- list: Show index statistics and browse data
"""

import sys
import os
import json
from typing import List, Dict, Any, Optional

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, project_root)  # For test_pinecone import

from src.storage.vector_db import VectorDB
try:
    from src.embeddings.embeddings_generator import EmbeddingsGenerator
except:
    EmbeddingsGenerator = None


class PineconeMethods:
    """Complete Pinecone operations toolkit"""
    
    def __init__(self):
        """Initialize Pinecone and embeddings"""
        try:
            self.vdb = VectorDB()
            # Try real embeddings first, fallback to mock
            if EmbeddingsGenerator:
                try:
                    self.emb = EmbeddingsGenerator()
                    self.embedding_type = "real"
                except:
                    from test_pinecone import MockEmbeddingsGenerator
                    self.emb = MockEmbeddingsGenerator()
                    self.embedding_type = "mock"
            else:
                from test_pinecone import MockEmbeddingsGenerator
                self.emb = MockEmbeddingsGenerator()
                self.embedding_type = "mock"

            pass
        except Exception as e:
            raise
    
    def seedData(self):
        """Load and upload all seed data to Pinecone"""
        os.system("python db/data_processor.py")

        if not os.path.exists('db/processed_documents.json'):
            return

        with open('db/processed_documents.json', 'r', encoding='utf-8') as f:
            documents = json.load(f)

        batch_size = 25
        uploaded_count = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            try:
                ids = []
                vectors = []
                metadatas = []

                for doc in batch:
                    vector = self.emb.embed_one(doc['text'])
                    ids.append(doc['id'])
                    vectors.append(vector)
                    metadatas.append(doc['metadata'])

                self.vdb.upsert(ids, vectors, metadatas)
                uploaded_count += len(ids)

            except Exception:
                pass

        return uploaded_count
    
    def upsert(self, text: str, doc_id: str, metadata: Optional[Dict] = None):
        """Add/update a single vector"""
        if not metadata:
            metadata = {"type": "manual", "content": text[:100]}

        try:
            vector = self.emb.embed_one(text)
            result = self.vdb.upsert([doc_id], [vector], [metadata])
            return result
        except Exception:
            return None
    
    def query(self, query_text: str, top_k: int = 5):
        """Search similar vectors"""
        try:
            query_vector = self.emb.embed_one(query_text)
            results = self.vdb.query(query_vector, top_k=top_k)
            return results
        except Exception:
            return None
    
    def update(self, doc_id: str, new_text: Optional[str] = None, new_metadata: Optional[Dict] = None):
        """Update existing vector"""
        try:
            new_vector = None
            if new_text:
                new_vector = self.emb.embed_one(new_text)

            result = self.vdb.update(doc_id, vector=new_vector, set_metadata=new_metadata)
            return result
        except Exception:
            return None
    
    def compare(self, text_a: str, text_b: str):
        """Compare similarity between two texts"""
        try:
            vec_a = self.emb.embed_one(text_a)
            vec_b = self.emb.embed_one(text_b)

            import numpy as np
            va = np.array(vec_a)
            vb = np.array(vec_b)
            similarity = np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb))

            return similarity
        except Exception:
            return None
    
    def list(self):
        """Show index statistics and sample data"""
        try:
            stats = self.vdb.list_stats()
            sample_vector = self.emb.embed_one("sample query")
            results = self.vdb.query(sample_vector, top_k=3)

            return {
                'stats': stats,
                'sample_data': results
            }
        except Exception:
            return None


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        return

    method = sys.argv[1].lower()

    try:
        pm = PineconeMethods()
        
        if method == "seeddata":
            result = pm.seedData()
            return result

        elif method == "upsert":
            if len(sys.argv) < 4:
                return None
            text = sys.argv[2]
            doc_id = sys.argv[3]
            metadata = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
            result = pm.upsert(text, doc_id, metadata)
            return result
            
        elif method == "query":
            if len(sys.argv) < 3:
                return None
            query_text = sys.argv[2]
            top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            result = pm.query(query_text, top_k)
            return result

        elif method == "update":
            if len(sys.argv) < 3:
                return None
            doc_id = sys.argv[2]
            new_text = sys.argv[3] if len(sys.argv) > 3 else None
            new_metadata = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
            result = pm.update(doc_id, new_text, new_metadata)
            return result

        elif method == "compare":
            if len(sys.argv) < 4:
                return None
            text_a = sys.argv[2]
            text_b = sys.argv[3]
            result = pm.compare(text_a, text_b)
            return result

        elif method == "list":
            result = pm.list()
            return result

        else:
            return None

    except Exception:
        return None


if __name__ == "__main__":
    main()
