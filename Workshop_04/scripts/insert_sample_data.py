#!/usr/bin/env python3
"""
Data Insertion Script for E-commerce AI Product Advisor
This script loads sample data from JSON files and inserts them into Pinecone vector database.

Usage:
    python scripts/insert_sample_data.py
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Debug path information
print(f"Project root: {project_root}")
print(f"Python path added: {str(project_root)}")
print(f"Current working directory: {os.getcwd()}")

from src.services.pinecone_service import pinecone_service
from src.utils.logger import get_logger

logger = get_logger("data_insertion")


def load_json_file(file_path: str) -> dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Loaded {file_path}")
        return data
    except Exception as e:
        logger.error(f"❌ Failed to load {file_path}: {e}")
        return {}


def prepare_enhanced_product_vector(product: dict) -> tuple:
    """Prepare product data for vector storage with enhanced embedding text"""
    try:
        # Extract metadata for better organization
        metadata = product.get('metadata', {})
        
        # Create comprehensive searchable text from product data
        searchable_parts = []
        
        # Basic info
        if 'name' in metadata:
            searchable_parts.append(f"Product: {metadata['name']}")
        if 'brand' in metadata:
            searchable_parts.append(f"Brand: {metadata['brand']}")
        if 'category' in metadata:
            searchable_parts.append(f"Category: {metadata['category']}")
        if 'subcategory' in metadata:
            searchable_parts.append(f"Type: {metadata['subcategory']}")
        
        # Price information with categorization
        if 'price' in metadata:
            price = metadata['price']
            searchable_parts.append(f"Price: {price:,.0f} VND")
            
            # Add price range categorization for better search
            if price < 10000000:  # < 10M
                searchable_parts.append("Budget affordable cheap economical low-cost")
            elif price < 30000000:  # 10-30M
                searchable_parts.append("Mid-range value moderate reasonable")
            else:  # > 30M
                searchable_parts.append("Premium high-end expensive luxury flagship")
        
        # Rating information with descriptive terms
        if 'rating' in metadata:
            rating = metadata['rating']
            searchable_parts.append(f"Rating: {rating}/5 stars")
            if rating >= 4.5:
                searchable_parts.append("Excellent outstanding top-rated highly-rated superior")
            elif rating >= 4.0:
                searchable_parts.append("Good well-rated quality reliable")
            elif rating >= 3.5:
                searchable_parts.append("Average decent acceptable")
        
        # Features with enhanced descriptions
        if 'features' in metadata:
            features = metadata['features']
            if features:
                searchable_parts.append(f"Key features: {' '.join(features)}")
        
        # Pros and Cons for sentiment analysis
        if 'pros' in metadata:
            pros = metadata['pros']
            if pros:
                searchable_parts.append(f"Strengths advantages: {' '.join(pros)}")
        
        if 'cons' in metadata:
            cons = metadata['cons']
            if cons:
                searchable_parts.append(f"Weaknesses disadvantages: {' '.join(cons)}")
        
        # Use cases for better matching
        if 'use_cases' in metadata:
            use_cases = metadata['use_cases']
            if use_cases:
                searchable_parts.append(f"Suitable for: {' '.join(use_cases)}")
        
        # Tags for enhanced categorization
        if 'tags' in metadata:
            tags = metadata['tags']
            if tags:
                searchable_parts.append(f"Keywords: {' '.join(tags)}")
        
        # Extract and use the complete 'text' field
        text_content = product.get('text', '')
        if text_content:
            # Use the complete text content without splitting
            searchable_parts.append(f"Full product information: {text_content}")
        
        # Add category-specific keywords
        category = metadata.get('category', '').lower()
        if category == 'laptop':
            searchable_parts.append("Computer notebook portable PC laptop máy tính xách tay")
        elif category == 'smartphone':
            searchable_parts.append("Phone mobile cellphone điện thoại di động smartphone")
        
        # Combine all parts into searchable text
        searchable_text = ' '.join(filter(None, searchable_parts))
        
        # Create embedding using pinecone service
        embedding = pinecone_service.create_embedding(searchable_text)
        
        # Prepare comprehensive metadata for storage
        vector_metadata = {
            'id': product.get('id', metadata.get('id')),
            'name': metadata.get('name', ''),
            'brand': metadata.get('brand', '').lower(),  # Normalize brand to lowercase
            'category': metadata.get('category', '').lower(),  # Normalize category to lowercase
            'subcategory': metadata.get('subcategory', ''),
            'price': float(metadata.get('price', 0)),
            'currency': metadata.get('currency', 'VND'),
            'type': 'product',
            'rating': float(metadata.get('rating', 0)),
            'in_stock': metadata.get('in_stock', True),
            'features': json.dumps(metadata.get('features', []), ensure_ascii=False),
            'pros': json.dumps(metadata.get('pros', []), ensure_ascii=False),
            'cons': json.dumps(metadata.get('cons', []), ensure_ascii=False),
            'use_cases': json.dumps(metadata.get('use_cases', []), ensure_ascii=False),
            'tags': json.dumps(metadata.get('tags', []), ensure_ascii=False),
            'review_count': int(metadata.get('review_count', 0)),
            'warranty': metadata.get('warranty', ''),
            'created_at': datetime.now().isoformat()
        }
        
        return product.get('id', metadata.get('id')), embedding, vector_metadata
        
    except Exception as e:
        logger.error(f"❌ Failed to prepare enhanced product vector: {e}")
        return None, None, None


def prepare_enhanced_review_vector(review: dict) -> tuple:
    """Prepare review data for vector storage with enhanced embedding text"""
    try:
        # Extract metadata
        metadata = review.get('metadata', {})
        
        # Create comprehensive searchable text from review
        searchable_parts = []
        
        # Review title and content
        if 'title' in metadata:
            searchable_parts.append(f"Review title: {metadata['title']}")
        
        if 'content' in metadata:
            searchable_parts.append(f"Review content: {metadata['content']}")
        
        # Rating with descriptive terms
        if 'rating' in metadata:
            rating = metadata['rating']
            searchable_parts.append(f"User rating: {rating}/5 stars")
            if rating >= 5:
                searchable_parts.append("Perfect excellent outstanding amazing")
            elif rating >= 4:
                searchable_parts.append("Good positive satisfied happy")
            elif rating >= 3:
                searchable_parts.append("Average okay acceptable neutral")
            elif rating >= 2:
                searchable_parts.append("Poor disappointed unsatisfied")
            else:
                searchable_parts.append("Terrible awful bad horrible")
        
        # Pros and cons from review
        if 'pros' in metadata:
            pros = metadata['pros']
            if pros:
                searchable_parts.append(f"Positive aspects: {' '.join(pros)}")
        
        if 'cons' in metadata:
            cons = metadata['cons']
            if cons:
                searchable_parts.append(f"Negative aspects: {' '.join(cons)}")
        
        # User information
        if 'user_name' in metadata:
            searchable_parts.append(f"Reviewer: {metadata['user_name']}")
        
        # Purchase verification
        if metadata.get('verified_purchase', False):
            searchable_parts.append("Verified purchase confirmed buyer authentic review")
        
        # Helpful count indicates review quality
        helpful_count = metadata.get('helpful_count', 0)
        if helpful_count > 50:
            searchable_parts.append("Popular helpful review many likes")
        elif helpful_count > 20:
            searchable_parts.append("Useful helpful review")
        
        # Extract and use the complete 'text' field for review
        text_content = review.get('text', '')
        if text_content:
            # Use the complete text content without splitting
            searchable_parts.append(f"Complete review: {text_content}")
        
        # Add sentiment keywords based on rating
        rating = metadata.get('rating', 0)
        if rating >= 4:
            searchable_parts.append("Positive review recommendation satisfied customer")
        elif rating <= 2:
            searchable_parts.append("Negative review complaint unsatisfied customer")
        
        # Combine all parts
        searchable_text = ' '.join(filter(None, searchable_parts))
        
        # Create embedding
        embedding = pinecone_service.create_embedding(searchable_text)
        
        # Prepare metadata for storage
        vector_metadata = {
            'id': review.get('id', metadata.get('id')),
            'product_id': metadata.get('product_id', ''),
            'type': 'review',
            'rating': float(metadata.get('rating', 0)),
            'title': metadata.get('title', ''),
            'content': metadata.get('content', '')[:500],  # Limit content length
            'pros': json.dumps(metadata.get('pros', []), ensure_ascii=False),
            'cons': json.dumps(metadata.get('cons', []), ensure_ascii=False),
            'helpful_count': int(metadata.get('helpful_count', 0)),
            'verified_purchase': metadata.get('verified_purchase', False),
            'user_name': metadata.get('user_name', ''),
            'date': metadata.get('date', ''),
            'created_at': datetime.now().isoformat()
        }
        
        return f"review_{review.get('id', metadata.get('id'))}", embedding, vector_metadata
        
    except Exception as e:
        logger.error(f"❌ Failed to prepare enhanced review vector: {e}")
        return None, None, None


def insert_products(products_data: list) -> bool:
    """Insert product data into Pinecone using enhanced embedding"""
    try:
        logger.info(f"🔄 Processing {len(products_data)} products...")
        
        # Prepare vectors using enhanced method
        vectors = []
        for product in products_data:
            vector_id, embedding, metadata = prepare_enhanced_product_vector(product)
            if vector_id and embedding and metadata:
                vectors.append((vector_id, embedding, metadata))
            else:
                logger.warning(f"⚠️ Skipped product: {product.get('id', 'unknown')}")
        
        # Insert into Pinecone
        if vectors:
            success = pinecone_service.upsert_vectors(vectors)
            if success:
                logger.info(f"✅ Successfully inserted {len(vectors)} products")
                return True
        
        logger.error("❌ No valid product vectors to insert")
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to insert products: {e}")
        return False


def insert_reviews(reviews_data: list) -> bool:
    """Insert review data into Pinecone using enhanced embedding"""
    try:
        logger.info(f"🔄 Processing {len(reviews_data)} reviews...")
        
        # Prepare vectors using enhanced method
        vectors = []
        for review in reviews_data:
            vector_id, embedding, metadata = prepare_enhanced_review_vector(review)
            if vector_id and embedding and metadata:
                vectors.append((vector_id, embedding, metadata))
            else:
                logger.warning(f"⚠️ Skipped review: {review.get('id', 'unknown')}")
        
        # Insert into Pinecone
        if vectors:
            success = pinecone_service.upsert_vectors(vectors)
            if success:
                logger.info(f"✅ Successfully inserted {len(vectors)} reviews")
                return True
        
        logger.error("❌ No valid review vectors to insert")
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to insert reviews: {e}")
        return False


def calculate_product_ratings(products: list, reviews: list) -> list:
    """Calculate average ratings for products based on reviews"""
    try:
        # Group reviews by product_id
        product_reviews = {}
        for review in reviews:
            product_id = review.get('product_id')
            if product_id:
                if product_id not in product_reviews:
                    product_reviews[product_id] = []
                product_reviews[product_id].append(review.get('rating', 0))
        
        # Update product ratings
        updated_products = []
        for product in products:
            product_copy = product.copy()
            product_id = product.get('id')
            
            if product_id in product_reviews:
                ratings = product_reviews[product_id]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                product_copy['rating'] = round(avg_rating, 1)
                product_copy['review_count'] = len(ratings)
                logger.info(f"📊 {product['name']}: {avg_rating:.1f}/5 ({len(ratings)} reviews)")
            else:
                product_copy['rating'] = 0.0
                product_copy['review_count'] = 0
                logger.info(f"📊 {product['name']}: No reviews")
            
            updated_products.append(product_copy)
        
        return updated_products
        
    except Exception as e:
        logger.error(f"❌ Failed to calculate ratings: {e}")
        return products


def test_embedding_quality(products: list, reviews: list) -> None:
    """Test and display embedding quality for sample data"""
    try:
        logger.info("🧪 Testing embedding quality...")
        
        # Test a sample product
        if products:
            sample_product = products[0]
            vector_id, embedding, metadata = prepare_enhanced_product_vector(sample_product)
            
            logger.info(f"📦 Sample Product Embedding:")
            logger.info(f"   Product: {metadata.get('name', 'Unknown')}")
            logger.info(f"   Vector ID: {vector_id}")
            logger.info(f"   Embedding dimension: {len(embedding) if embedding else 0}")
            logger.info(f"   Metadata keys: {list(metadata.keys()) if metadata else []}")
            
            # Show first few embedding values
            if embedding:
                logger.info(f"   Embedding sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, ..., {embedding[-1]:.4f}]")
        
        # Test a sample review
        if reviews:
            sample_review = reviews[0]
            vector_id, embedding, metadata = prepare_enhanced_review_vector(sample_review)
            
            logger.info(f"💬 Sample Review Embedding:")
            logger.info(f"   Review: {metadata.get('title', 'Unknown')}")
            logger.info(f"   Vector ID: {vector_id}")
            logger.info(f"   Embedding dimension: {len(embedding) if embedding else 0}")
            logger.info(f"   Metadata keys: {list(metadata.keys()) if metadata else []}")
            
            # Show first few embedding values
            if embedding:
                logger.info(f"   Embedding sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, ..., {embedding[-1]:.4f}]")
        
        logger.info("✅ Embedding quality test completed")
        
    except Exception as e:
        logger.error(f"❌ Failed to test embedding quality: {e}")


def main():
    """Main function to insert all sample data"""
    try:
        logger.info("🚀 Starting data insertion process...")
        
        # File paths
        samples_dir = project_root / "samples"
        laptop_file = samples_dir / "laptops.json"
        smartphone_file = samples_dir / "smartphone.json"
        reviews_file = samples_dir / "reviews.json"
        
        # Check if files exist
        for file_path in [laptop_file, smartphone_file, reviews_file]:
            if not file_path.exists():
                logger.error(f"❌ File not found: {file_path}")
                return False
        
        # Initialize Pinecone service
        logger.info("🔄 Initializing Pinecone service...")
        if not pinecone_service.create_index_if_not_exists():
            logger.error("❌ Failed to create/connect to Pinecone index")
            return False
        
        # Load data
        logger.info("📂 Loading sample data...")
        laptops_data = load_json_file(laptop_file)
        smartphones_data = load_json_file(smartphone_file)
        reviews_data = load_json_file(reviews_file)
        
        # Extract products and reviews
        laptops = laptops_data.get('products', [])
        smartphones = smartphones_data.get('products', [])
        reviews = reviews_data.get('reviews', [])
        
        all_products = laptops + smartphones
        
        logger.info(f"📊 Data summary:")
        logger.info(f"   - Laptops: {len(laptops)}")
        logger.info(f"   - Smartphones: {len(smartphones)}")
        logger.info(f"   - Total products: {len(all_products)}")
        logger.info(f"   - Reviews: {len(reviews)}")
        
        # Calculate product ratings from reviews
        logger.info("🔄 Calculating product ratings from reviews...")
        updated_products = calculate_product_ratings(all_products, reviews)
        
        # Option to clear existing data
        user_input = input("\n🗑️ Do you want to clear existing data first? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            logger.info("🔄 Clearing existing data...")
            pinecone_service.delete_all_vectors()
            logger.info("✅ Existing data cleared")
        
        # Insert products
        logger.info("\n📦 Inserting products...")
        products_success = insert_products(updated_products)
        
        # Insert reviews
        logger.info("\n💬 Inserting reviews...")
        reviews_success = insert_reviews(reviews)
        
        # Check final status
        if products_success and reviews_success:
            logger.info("\n🎉 Data insertion completed successfully!")
            
            # Show index stats
            stats = pinecone_service.get_index_stats()
            if stats:
                total_vectors = stats.get('total_vector_count', 0)
                logger.info(f"📊 Final index stats: {total_vectors} vectors total")
            
            # Test search
            logger.info("\n🔍 Testing search functionality...")
            test_results = pinecone_service.search_products("laptop gaming", top_k=3)
            logger.info(f"✅ Test search returned {len(test_results)} results")
            
            for i, product in enumerate(test_results[:2], 1):
                logger.info(f"   {i}. {product['name']} - {product['price']:,.0f} VND (score: {product.get('similarity_score', 0):.3f})")
            
            return True
        else:
            logger.error("❌ Data insertion failed!")
            return False
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Process interrupted by user")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
