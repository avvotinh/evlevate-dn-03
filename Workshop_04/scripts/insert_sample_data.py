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


def insert_products(products_data: list) -> bool:
    """Insert product data into Pinecone"""
    try:
        logger.info(f"🔄 Processing {len(products_data)} products...")
        
        # Prepare vectors
        vectors = []
        for product in products_data:
            vector_id, embedding, metadata = pinecone_service.prepare_product_vector(product)
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
    """Insert review data into Pinecone"""
    try:
        logger.info(f"🔄 Processing {len(reviews_data)} reviews...")
        
        # Prepare vectors
        vectors = []
        for review in reviews_data:
            vector_id, embedding, metadata = pinecone_service.prepare_review_vector(review)
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
