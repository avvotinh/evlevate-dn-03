"""
Pinecone Vector Database Service for E-commerce AI Product Advisor
Handles all vector operations including indexing, searching, and filtering.
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

import numpy as np
from pinecone import Pinecone, ServerlessSpec
from openai import AzureOpenAI

from src.config.config import Config
from src.utils.logger import get_logger

logger = get_logger("pinecone_service")


class PineconeService:
    """Service for Pinecone vector database operations"""
    
    def __init__(self):
        """Initialize Pinecone service"""
        self.pc = None
        self.index = None
        self.embedding_client = None
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Pinecone and OpenAI clients"""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            logger.info("✅ Pinecone client initialized")
            
            # Initialize Azure OpenAI for embeddings
            embedding_config = Config.get_embedding_config()
            self.embedding_client = AzureOpenAI(
                api_key=embedding_config["api_key"],
                api_version=embedding_config["api_version"],
                azure_endpoint=embedding_config["api_base"]
            )
            logger.info("✅ Azure OpenAI embedding client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize clients: {e}")
            raise
    
    def create_index_if_not_exists(self) -> bool:
        """Create Pinecone index if it doesn't exist"""
        try:
            # Check if index exists
            if Config.PINECONE_INDEX_NAME in [idx.name for idx in self.pc.list_indexes()]:
                logger.info(f"✅ Index '{Config.PINECONE_INDEX_NAME}' already exists")
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
                return True
            
            # Create index
            logger.info(f"🔄 Creating index '{Config.PINECONE_INDEX_NAME}'...")
            self.pc.create_index(
                name=Config.PINECONE_INDEX_NAME,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            
            # Wait for index to be ready
            while not self.pc.describe_index(Config.PINECONE_INDEX_NAME).status['ready']:
                time.sleep(1)
            
            self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            logger.info(f"✅ Index '{Config.PINECONE_INDEX_NAME}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create index: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            if not self.index:
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            
            stats = self.index.describe_index_stats()
            logger.info(f"📊 Index stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get index stats: {e}")
            return {}
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using Azure OpenAI"""
        try:
            # Clean and prepare text
            text = text.strip().replace('\n', ' ')
            if not text:
                return [0.0] * self.embedding_dimension
            
            # Get embedding
            response = self.embedding_client.embeddings.create(
                model=Config.AZURE_OPENAI_EMBEDDING_MODEL,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"✅ Created embedding for text: {text[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to create embedding: {e}")
            return [0.0] * self.embedding_dimension
    
    def prepare_product_vector(self, product: Dict[str, Any]) -> Tuple[str, List[float], Dict[str, Any]]:
        """Prepare product data for vector storage"""
        try:
            # Create searchable text from product data
            searchable_parts = [
                product.get('name', ''),
                product.get('brand', ''),
                product.get('description', ''),
                ' '.join(product.get('features', [])),
            ]
            
            # Add specs information
            specs = product.get('specs', {})
            for key, value in specs.items():
                if isinstance(value, str):
                    searchable_parts.append(f"{key}: {value}")
            
            searchable_text = ' '.join(filter(None, searchable_parts))
            
            # Create embedding
            embedding = self.create_embedding(searchable_text)
            
            # Prepare metadata
            metadata = {
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'category': product['category'],
                'subcategory': product.get('subcategory', ''),
                'price': float(product['price']),
                'currency': product.get('currency', 'VND'),
                'type': 'product',
                'description': product.get('description', '')[:500],  # Limit description length
                'features': json.dumps(product.get('features', []), ensure_ascii=False),
                'specs': json.dumps(specs, ensure_ascii=False),
                'rating': product.get('rating', 0.0),
                'created_at': datetime.now().isoformat()
            }
            
            return product['id'], embedding, metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare product vector: {e}")
            return None, None, None
    
    def prepare_review_vector(self, review: Dict[str, Any]) -> Tuple[str, List[float], Dict[str, Any]]:
        """Prepare review data for vector storage"""
        try:
            # Create searchable text from review
            searchable_parts = [
                review.get('title', ''),
                review.get('content', ''),
                ' '.join(review.get('pros', [])),
                ' '.join(review.get('cons', []))
            ]
            
            searchable_text = ' '.join(filter(None, searchable_parts))
            
            # Create embedding
            embedding = self.create_embedding(searchable_text)
            
            # Prepare metadata
            metadata = {
                'id': review['id'],
                'product_id': review['product_id'],
                'type': 'review',
                'rating': float(review['rating']),
                'title': review.get('title', ''),
                'content': review.get('content', '')[:500],  # Limit content length
                'pros': json.dumps(review.get('pros', []), ensure_ascii=False),
                'cons': json.dumps(review.get('cons', []), ensure_ascii=False),
                'helpful_count': review.get('helpful_count', 0),
                'verified_purchase': review.get('verified_purchase', False),
                'user_name': review.get('user_name', ''),
                'date': review.get('date', ''),
                'created_at': datetime.now().isoformat()
            }
            
            return f"review_{review['id']}", embedding, metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare review vector: {e}")
            return None, None, None
    
    def upsert_vectors(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]], batch_size: int = 100):
        """Upsert vectors to Pinecone in batches"""
        try:
            if not self.index:
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            
            # Filter out None vectors
            valid_vectors = [(id, emb, meta) for id, emb, meta in vectors if id and emb and meta]
            
            logger.info(f"🔄 Upserting {len(valid_vectors)} vectors in batches of {batch_size}...")
            
            # Process in batches
            for i in range(0, len(valid_vectors), batch_size):
                batch = valid_vectors[i:i + batch_size]
                
                # Format for Pinecone
                vectors_to_upsert = [
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": metadata
                    }
                    for vector_id, embedding, metadata in batch
                ]
                
                # Upsert batch
                self.index.upsert(vectors=vectors_to_upsert)
                logger.info(f"✅ Upserted batch {i//batch_size + 1}/{(len(valid_vectors) + batch_size - 1)//batch_size}")
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
            
            logger.info(f"✅ Successfully upserted {len(valid_vectors)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upsert vectors: {e}")
            return False
    
    def search_products(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 5,
        include_reviews: bool = False
    ) -> List[Dict[str, Any]]:
        """Search for products using natural language query"""
        try:
            if not self.index:
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            
            # Create query embedding
            query_embedding = self.create_embedding(query)
            
            # Prepare metadata filter
            metadata_filter = {"type": "product"}
            if filters:
                metadata_filter.update(filters)
            
            logger.info(f"🔍 Searching for: '{query}' with filters: {metadata_filter}")
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                filter=metadata_filter,
                top_k=min(top_k, Config.MAX_TOP_K),
                include_metadata=True
            )
            
            # Debug logging
            logger.info(f"🔍 Pinecone returned {len(results.matches)} matches")
            for i, match in enumerate(results.matches[:3]):  # Log first 3 matches
                logger.info(f"  Match {i+1}: score={match.score:.3f}, id={match.id}")
            
            logger.info(f"🎯 Using similarity threshold: {Config.SIMILARITY_THRESHOLD}")
            
            products = []
            filtered_count = 0
            for match in results.matches:
                logger.debug(f"Processing match: id={match.id}, score={match.score}")
                if match.score >= Config.SIMILARITY_THRESHOLD:
                    product_data = match.metadata.copy()
                    product_data['similarity_score'] = float(match.score)
                    
                    # Parse JSON fields back to objects
                    if 'features' in product_data:
                        try:
                            product_data['features'] = json.loads(product_data['features'])
                        except:
                            product_data['features'] = []
                    
                    if 'specs' in product_data:
                        try:
                            product_data['specs'] = json.loads(product_data['specs'])
                        except:
                            product_data['specs'] = {}
                    
                    # Include reviews if requested
                    if include_reviews:
                        product_data['reviews'] = self.get_product_reviews(product_data['id'])
                    
                    products.append(product_data)
                else:
                    filtered_count += 1
                    logger.debug(f"Filtered out {match.id} (score {match.score:.3f} < {Config.SIMILARITY_THRESHOLD})")
            
            if filtered_count > 0:
                logger.info(f"⚠️ Filtered out {filtered_count} matches due to low similarity scores")
            
            logger.info(f"✅ Found {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            # Re-raise the exception so tools can handle it properly
            raise e
    
    def get_product_reviews(self, product_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get reviews for a specific product"""
        try:
            if not self.index:
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            
            # Search for reviews of this product
            results = self.index.query(
                vector=[0.0] * self.embedding_dimension,  # Dummy vector, we're filtering by metadata
                filter={
                    "type": "review",
                    "product_id": product_id
                },
                top_k=limit,
                include_metadata=True
            )
            
            reviews = []
            for match in results.matches:
                review_data = match.metadata.copy()
                
                # Parse JSON fields
                if 'pros' in review_data:
                    try:
                        review_data['pros'] = json.loads(review_data['pros'])
                    except:
                        review_data['pros'] = []
                
                if 'cons' in review_data:
                    try:
                        review_data['cons'] = json.loads(review_data['cons'])
                    except:
                        review_data['cons'] = []
                
                reviews.append(review_data)
            
            return reviews
            
        except Exception as e:
            logger.error(f"❌ Failed to get reviews: {e}")
            return []
    
    def filter_products(
        self, 
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        min_rating: Optional[float] = None,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """Filter products by criteria"""
        try:
            if not self.index:
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            
            # Build filter
            filter_dict = {"type": "product"}
            
            if category:
                filter_dict["category"] = category
            
            if brand:
                filter_dict["brand"] = brand
            
            if min_price is not None or max_price is not None:
                price_filter = {}
                if min_price is not None:
                    price_filter["$gte"] = min_price
                if max_price is not None:
                    price_filter["$lte"] = max_price
                filter_dict["price"] = price_filter
            
            if min_rating is not None:
                filter_dict["rating"] = {"$gte": min_rating}
            
            logger.info(f"🔍 Filtering products with: {filter_dict}")
            
            # Query with dummy vector (we're just filtering)
            results = self.index.query(
                vector=[0.0] * self.embedding_dimension,
                filter=filter_dict,
                top_k=top_k,
                include_metadata=True
            )
            
            products = []
            for match in results.matches:
                product_data = match.metadata.copy()
                
                # Parse JSON fields
                if 'features' in product_data:
                    try:
                        product_data['features'] = json.loads(product_data['features'])
                    except:
                        product_data['features'] = []
                
                if 'specs' in product_data:
                    try:
                        product_data['specs'] = json.loads(product_data['specs'])
                    except:
                        product_data['specs'] = {}
                
                products.append(product_data)
            
            logger.info(f"✅ Found {len(products)} products matching criteria")
            return products
            
        except Exception as e:
            logger.error(f"❌ Filter failed: {e}")
            return []
    
    def delete_all_vectors(self) -> bool:
        """Delete all vectors from the index (for testing/reset)"""
        try:
            if not self.index:
                self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            
            logger.warning("🗑️ Deleting all vectors from index...")
            self.index.delete(delete_all=True)
            logger.info("✅ All vectors deleted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete vectors: {e}")
            return False


# Singleton instance
pinecone_service = PineconeService()
