"""
CSV Financial Data Analyzer CLI Tool
===================================

A command-line tool to extract financial data from CSV files and analyze them using OpenAI API.
This tool uses existing CSV extraction functions and sends the processed data to OpenAI for analysis.
"""

import argparse
import os
import json
import sys
import logging
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from utils import read_csv_file, detect_encoding
from document_processors import process_raw_csv_data

# Load environment variables from .env file
load_dotenv()


# Setup logging
logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """Financial data analyzer for CSV files using OpenAI API."""
    
    def __init__(self):
        """
        Initialize the FinancialAnalyzer with Azure OpenAI client configuration.

        Environment variables required:
        - AZURE_OPENAI_API_VERSION: API version (e.g., "2024-02-15-preview")
        - AZURE_OPENAI_API_BASE: Azure endpoint URL
        - AZURE_OPENAI_API_KEY: Authentication key
        - AZURE_OPENAI_DEPLOYMENT_NAME: Model deployment name
        """

        # Initialize Azure OpenAI client with environment configuration
        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        # Store the deployment name for model calls
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  
    
    def analyze_csv_file_info(self, csv_file_path: str) -> Dict[str, Any]:
        """
        Analyze CSV file information using existing utility functions.
        
        Args:
            csv_file_path: Path to the CSV file
        
        Returns:
            Dictionary containing file analysis information
        """
        if not os.path.exists(csv_file_path):
            return {"error": "File not found"}
        
        info = {
            "file_path": csv_file_path,
            "file_size": os.path.getsize(csv_file_path),
            "encoding": detect_encoding(csv_file_path),
            "exists": True
        }
        
        # Try to get a quick preview of the data
        try:
            csv_records = read_csv_file(csv_file_path)
            if csv_records:
                info["total_records"] = len(csv_records)
                info["sample_record"] = csv_records[0] if csv_records else None
                
                # Count unique element IDs if available
                element_ids = set()
                for record in csv_records[:100]:  # Sample first 100 records
                    if "要素ID" in record and record["要素ID"]:
                        element_ids.add(record["要素ID"])
                
                info["unique_element_ids_sample"] = len(element_ids)
                info["sample_element_ids"] = list(element_ids)[:10]  # First 10 as sample
            else:
                info["total_records"] = 0
                info["error"] = "Could not read CSV data"
        except Exception as e:
            info["error"] = f"Error reading file: {str(e)}"
        
        return info
    
    def extract_data_from_csv(self, csv_file_path: str, doc_id: str = None, doc_type_code: str = None) -> Optional[Dict[str, Any]]:
        """
        Extract and process data from a single CSV file using existing utility functions.
        
        Args:
            csv_file_path: Path to the CSV file
            doc_id: Document ID (optional, defaults to filename)
            doc_type_code: Document type code (optional, defaults to '160')
        
        Returns:
            Structured data dictionary or None if processing failed
        """
        if not os.path.exists(csv_file_path):
            logger.error(f"CSV file not found: {csv_file_path}")
            return None
        
        # Set defaults if not provided
        if doc_id is None:
            doc_id = os.path.splitext(os.path.basename(csv_file_path))[0]
        
        if doc_type_code is None:
            doc_type_code = '160'  # Default to Semi-Annual Report
        
        logger.info(f"Processing CSV file: {csv_file_path}")
        logger.info(f"Document ID: {doc_id}, Document Type: {doc_type_code}")
        
        # Use existing read_csv_file function from utils.py
        csv_records = read_csv_file(csv_file_path)
        if csv_records is None:
            logger.error(f"Failed to read CSV file: {csv_file_path}")
            return None
        
        logger.info(f"Successfully read {len(csv_records)} records from CSV file")
        
        # Prepare raw data in the expected format for process_raw_csv_data
        raw_csv_data = [{
            'filename': os.path.basename(csv_file_path),
            'data': csv_records
        }]
        
        # Use existing process_raw_csv_data function from document_processors.py
        structured_data = process_raw_csv_data(raw_csv_data, doc_id, doc_type_code)
        
        if structured_data:
            logger.info(f"Successfully processed structured data for {csv_file_path}")
            return structured_data
        else:
            logger.warning(f"Document processor returned no data for {csv_file_path}")
            return None
    
    def create_analysis_prompt(self, structured_data: Dict[str, Any]) -> list:
        """
        Create the analysis prompt for OpenAI based on extracted CSV data.
        
        Args:
            structured_data: Processed data from CSV extraction
            
        Returns:
            list: Messages for OpenAI API
        """
        # Convert structured data to JSON for the prompt
        data_json = json.dumps(structured_data, ensure_ascii=False, indent=2)
        
        return [
            {
                "role": "system",
                "content": "You are a financial data analyst assistant specializing in Japanese corporate financial reports from EDINET XBRL data."
            },
            {
                "role": "user",
                "content": f"""
The following content is extracted and processed from an EDINET CSV file containing XBRL financial data.

Please help extract and analyze key financial indicators for this company:

1. Revenue
2. Operating Profit  
3. Net Profit  
4. Total Assets  
5. Total Liabilities  
6. Cash Flow from Operating Activities  
7. Equity

For each item:
- Return the corresponding value (preferably in million yen or actual currency unit).
- Indicate the fiscal period (e.g. FY2023 or Q2 2024) if available.
- If multiple entries exist, prefer the most recent full-year value.
- Compare with previous period if available and calculate growth rate.

Please also provide:
- Company name and code if available
- Report period and type
- Key financial ratios (ROE, ROA, Debt-to-Equity, Current Ratio if calculable)

## Summary Financial Trends Analysis:
Based on the extracted data, please provide:
1. **Growth Analysis**: Year-over-year or period-over-period growth rates for revenue, profit, and assets
2. **Profitability Trends**: Changes in profit margins and profitability indicators
3. **Financial Health**: Assessment of liquidity, leverage, and overall financial stability
4. **Key Insights**: Notable trends, improvements, or concerns in the financial performance
5. **Risk Factors**: Any financial metrics that indicate potential risks or areas of concern

Please format the output in a clear, structured way with headers for each financial indicator and include the financial trends summary at the end.

Extracted CSV Data:
{data_json}
"""
            }
        ]
    
    def analyze_financial_data(self, structured_data: Dict[str, Any]) -> str:
        """
        Send extracted CSV data to OpenAI for analysis.
        
        Args:
            structured_data: Processed data from CSV extraction
            
        Returns:
            str: Analysis result from OpenAI
            
        Raises:
            Exception: If API call fails
        """
        print("🤖 Sending extracted CSV data to OpenAI for analysis...")
        
        messages = self.create_analysis_prompt(structured_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0.1,
                max_tokens=3000
            )
            
            result = response.choices[0].message.content
            
            print("✓ Analysis completed successfully!")
            
            return result
            
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {e}")
    
    def save_result(self, result: str, output_path: str, input_file_path: str, structured_data: Dict[str, Any]):
        """
        Save analysis result to file with metadata.
        
        Args:
            result: Analysis result
            output_path: Output file path
            input_file_path: Original input file path for reference
            structured_data: The extracted data for reference
        """
        output_path = Path(output_path)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract some metadata from structured data
        doc_info = structured_data.get('document_info', {})
        company_name = doc_info.get('company_name', 'Unknown')
        doc_type = doc_info.get('document_type', 'Unknown')
        period = doc_info.get('period', 'Unknown')
        
        header = f"""Financial Data Analysis Report (CSV Source)
=============================================
Source File: {input_file_path}
Company: {company_name}
Document Type: {doc_type}
Period: {period}
Analysis Date: {timestamp}
Model Used: {self.deployment_name}
=============================================

"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + result)
        
        print(f"📄 Results saved to: {output_path}")


def create_default_output_path(input_path: str) -> Path:
    """Create default output file path based on input file."""
    input_path = Path(input_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"{input_path.stem}_analysis_{timestamp}.txt"
    
    # Create outputs folder in the root directory (where the script is located)
    script_dir = Path(__file__).parent
    outputs_dir = script_dir / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    return outputs_dir / output_name


def print_csv_analysis_summary(info: Dict[str, Any]) -> None:
    """Print summary of CSV file analysis."""
    print(f"\n{'='*60}")
    print("CSV FILE ANALYSIS")
    print(f"{'='*60}")
    
    print(f"File Path: {info['file_path']}")
    print(f"File Size: {info['file_size']:,} bytes")
    print(f"Detected Encoding: {info.get('encoding', 'Unknown')}")
    print(f"Total Records: {info.get('total_records', 0):,}")
    
    if info.get('unique_element_ids_sample'):
        print(f"Unique Element IDs (sample): {info['unique_element_ids_sample']}")
        
    if info.get('sample_element_ids'):
        print(f"Sample Element IDs: {', '.join(info['sample_element_ids'][:5])}")
    
    if info.get('error'):
        print(f"⚠️  Error: {info['error']}")
    
    print(f"{'='*60}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Extract and analyze financial data from CSV files using Azure OpenAI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv_analyzer_cli.py --file data.csv
  python csv_analyzer_cli.py --file data.csv --output results.txt
        """
    )
    
    # Required arguments
    parser.add_argument(
        "-f", "--file",
        help="Path to the CSV file to analyze"
    )
    
    # Optional arguments
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: auto-generated based on input filename)"
    )

    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        logger.info("Initializing Financial Analyzer...")
        analyzer = FinancialAnalyzer()
        
        if not args.file:
            print("❌ Error: --file argument is required")
            parser.print_help()
            sys.exit(1)
        
        print(f"Input file: {args.file}")
        
        # Analyze CSV file structure
        file_info = analyzer.analyze_csv_file_info(args.file)
        print_csv_analysis_summary(file_info)
        
        if file_info.get('error'):
            print(f"❌ Cannot proceed due to error: {file_info['error']}")
            sys.exit(1)
        
        print("\n📊 Extracting financial data from CSV...")
        
        structured_data = analyzer.extract_data_from_csv(args.file)
        
        if not structured_data:
            print("❌ Failed to extract data from CSV file")
            sys.exit(1)
        
        print(f"✓ Extracted structured data with {len(structured_data)} sections")
        
        # Analyze data with OpenAI
        result = analyzer.analyze_financial_data(structured_data)
        
        # Display results
        print("\n" + "="*60)
        print("FINANCIAL ANALYSIS RESULTS")
        print("="*60)
        print(result)
        print("="*60)
        
        output_path = args.output or create_default_output_path(args.file)
        analyzer.save_result(result, output_path, args.file, structured_data)
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
