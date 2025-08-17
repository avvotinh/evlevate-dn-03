#!/usr/bin/env python3
"""
Data processor for seed data - converts JSON to vector documents
Following SOLID principles with clear separation of concerns
"""

import json
import os
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Document:
    """Document structure for vector database"""
    id: str
    text: str
    metadata: Dict[str, Any]


class DataLoader(ABC):
    """Abstract base class for data loading - Single Responsibility"""
    
    @abstractmethod
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        pass


class JSONDataLoader(DataLoader):
    """JSON file loader implementation"""
    
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if 'products' in data:
            return data['products']
        elif 'reviews' in data:
            return data['reviews']
        elif isinstance(data, list):
            return data
        else:
            return [data]


class DocumentProcessor(ABC):
    """Abstract document processor - Open/Closed Principle"""
    
    @abstractmethod
    def process(self, raw_data: List[Dict[str, Any]]) -> List[Document]:
        pass


class ProductDocumentProcessor(DocumentProcessor):
    """Process product data into documents"""
    
    def process(self, raw_data: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        
        for product in raw_data:
            # Create comprehensive text for embedding
            text_parts = [
                f"{product.get('name', '')} - {product.get('brand', '')}",
                f"Giá: {product.get('price', 0):,} VND",
                f"Mô tả: {product.get('description', '')}",
            ]
            
            # Add specs
            if 'specs' in product:
                text_parts.append("Thông số kỹ thuật:")
                for key, value in product['specs'].items():
                    text_parts.append(f"- {key}: {value}")
            
            # Add features, pros, cons
            for field in ['features', 'pros', 'cons', 'use_cases']:
                if field in product and product[field]:
                    text_parts.append(f"{field.title()}: {', '.join(product[field])}")
            
            # Add rating info
            if 'rating' in product:
                text_parts.append(f"Đánh giá: {product['rating']}/5 từ {product.get('review_count', 0)} người dùng")
            
            document = Document(
                id=product['id'],
                text='\n'.join(text_parts),
                metadata={
                    'type': 'product',
                    'category': product.get('category', ''),
                    'subcategory': product.get('subcategory', ''),
                    'brand': product.get('brand', ''),
                    'name': product.get('name', ''),
                    'price': product.get('price', 0),
                    'rating': product.get('rating', 0),
                    'in_stock': product.get('in_stock', True),
                    **{k: v for k, v in product.items() if k not in ['description', 'specs']}
                }
            )
            documents.append(document)
        
        return documents


class ReviewDocumentProcessor(DocumentProcessor):
    """Process review data into documents"""
    
    def process(self, raw_data: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        
        for review in raw_data:
            text_parts = [
                f"Review: {review.get('title', '')}",
                f"Đánh giá: {review.get('rating', 0)}/5",
                f"Nội dung: {review.get('content', '')}",
            ]
            
            # Add pros/cons
            if 'pros' in review and review['pros']:
                text_parts.append(f"Ưu điểm: {', '.join(review['pros'])}")
            if 'cons' in review and review['cons']:
                text_parts.append(f"Nhược điểm: {', '.join(review['cons'])}")
            
            document = Document(
                id=review['id'],
                text='\n'.join(text_parts),
                metadata={
                    'type': 'review',
                    'product_id': review.get('product_id', ''),
                    'rating': review.get('rating', 0),
                    'helpful_count': review.get('helpful_count', 0),
                    'verified_purchase': review.get('verified_purchase', False),
                    **review
                }
            )
            documents.append(document)
        
        return documents


class DataProcessorFactory:
    """Factory for creating processors - Dependency Inversion"""
    
    @staticmethod
    def create_processor(data_type: str) -> DocumentProcessor:
        processors = {
            'product': ProductDocumentProcessor(),
            'review': ReviewDocumentProcessor(),
        }
        
        if data_type not in processors:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return processors[data_type]


class SeedDataManager:
    """Main manager class - Interface Segregation"""
    
    def __init__(self, loader: DataLoader):
        self.loader = loader
    
    def process_seed_files(self, file_configs: List[Dict[str, str]]) -> List[Document]:
        """Process multiple seed files"""
        all_documents = []
        
        for config in file_configs:
            file_path = config['path']
            data_type = config['type']
            
            # Load data
            raw_data = self.loader.load(file_path)
            if not raw_data:
                print(f"Warning: No data loaded from {file_path}")
                continue
            
            # Process data
            processor = DataProcessorFactory.create_processor(data_type)
            documents = processor.process(raw_data)
            
            all_documents.extend(documents)
            print(f"Processed {len(documents)} {data_type} documents from {file_path}")
        
        return all_documents
    
    def save_processed_data(self, documents: List[Document], output_path: str):
        """Save processed documents to JSON"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert to serializable format
        serializable_docs = [
            {
                'id': doc.id,
                'text': doc.text,
                'metadata': doc.metadata
            }
            for doc in documents
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_docs, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(documents)} documents to {output_path}")


def main():
    """Main function to process all seed data"""
    
    # Configuration
    file_configs = [
        {'path': 'seedData/laptops.json', 'type': 'product'},
        {'path': 'seedData/smartphone.json', 'type': 'product'},
        {'path': 'seedData/reviews.json', 'type': 'review'},
    ]
    
    # Check for generated files
    generated_files = [
        {'path': 'seedData/generated_laptops.json', 'type': 'product'},
        {'path': 'seedData/generated_phones.json', 'type': 'product'},
    ]
    
    for gen_file in generated_files:
        if os.path.exists(gen_file['path']):
            file_configs.append(gen_file)
    
    # Process data
    loader = JSONDataLoader()
    manager = SeedDataManager(loader)
    
    documents = manager.process_seed_files(file_configs)
    
    # Save processed data
    manager.save_processed_data(documents, 'db/processed_documents.json')
    
    # Print summary
    product_count = len([d for d in documents if d.metadata['type'] == 'product'])
    review_count = len([d for d in documents if d.metadata['type'] == 'review'])
    
    print(f"\n📊 Processing Summary:")
    print(f"Total documents: {len(documents)}")
    print(f"Products: {product_count}")
    print(f"Reviews: {review_count}")


if __name__ == "__main__":
    main()
