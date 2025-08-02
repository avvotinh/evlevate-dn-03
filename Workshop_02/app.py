import argparse
import os
import json
import sys
import logging
import openai
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import AzureOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from utils import read_csv_file
from document_processors import process_raw_csv_data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
    ]
)
logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    """Simple Financial Analyzer with CSV processing and AI analysis"""
        
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

        self.financial_data = {}
        self.conversation_history = []
    
    def extract_data_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """Extract structured data from CSV file"""
        if not os.path.exists(csv_file_path):
            logger.error(f"CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        logger.info(f"Extracting data from: {csv_file_path}")
        
        # Read CSV data
        csv_records = read_csv_file(csv_file_path)
        if not csv_records:
            logger.error("Failed to read CSV data")
            raise ValueError("Failed to read CSV data")
        
        logger.info(f"Successfully read {len(csv_records)} records")
        
        # Process raw data
        doc_id = os.path.splitext(os.path.basename(csv_file_path))[0]
        raw_csv_data = [{'filename': os.path.basename(csv_file_path), 'data': csv_records}]
        
        structured_data = process_raw_csv_data(raw_csv_data, doc_id, '160')
        if not structured_data:
            logger.error("Failed to process structured data")
            raise ValueError("Failed to process structured data")
        
        self.financial_data = structured_data
        company_name = structured_data.get('company_name_en', 'Unknown Company')
        logger.info(f"Successfully processed data for: {company_name}")
        
        return structured_data
    
    # Financial analysis methods
    def calculate_growth_rate(self, metric: str) -> Dict[str, Any]:
        """Calculate growth rate for a metric"""
        try:
            logger.debug(f"Calculating growth rate for metric: {metric}")
            key_facts = self.financial_data['key_facts']
            current = float(key_facts[metric]['current'])
            prior = float(key_facts[metric]['prior'])
            growth_rate = ((current - prior) / prior) * 100
            
            logger.debug(f"Growth rate calculation successful for {metric}: {growth_rate}%")
            return {
                "metric": metric,
                "current_value": current,
                "prior_value": prior,
                "growth_rate": round(growth_rate, 2),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error calculating growth rate for {metric}: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def calculate_financial_ratios(self) -> Dict[str, Any]:
        """Calculate key financial ratios"""
        try:
            logger.debug("Calculating financial ratios")
            key_facts = self.financial_data['key_facts']
            net_income = float(key_facts['NetIncome']['current'])
            net_assets = float(key_facts['NetAssets']['current'])
            total_assets = float(key_facts['TotalAssets']['current'])
            
            roe = (net_income / net_assets) * 100
            roa = (net_income / total_assets) * 100
            equity_ratio = (net_assets / total_assets) * 100
            
            logger.debug(f"Financial ratios calculated - ROE: {roe}%, ROA: {roa}%, Equity Ratio: {equity_ratio}%")
            return {
                "roe": round(roe, 2),
                "roa": round(roa, 2),
                "equity_ratio": round(equity_ratio, 2),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def get_company_overview(self) -> Dict[str, Any]:
        """Get company overview"""
        logger.debug("Retrieving company overview")
        return {
            "company_name_ja": self.financial_data.get('company_name_ja', 'N/A'),
            "company_name_en": self.financial_data.get('company_name_en', 'N/A'),
            "edinet_code": self.financial_data.get('edinet_code', 'N/A'),
            "status": "success"
        }
    
    def analyze_eps_performance(self) -> Dict[str, Any]:
        """Analyze EPS performance"""
        try:
            logger.debug("Analyzing EPS performance")
            key_facts = self.financial_data['key_facts']
            current_eps = float(key_facts['EPS']['current'])
            prior_eps = float(key_facts['EPS']['prior'])
            eps_growth = ((current_eps - prior_eps) / prior_eps) * 100
            
            if eps_growth > 20:
                performance = "Excellent"
            elif eps_growth > 10:
                performance = "Good"
            elif eps_growth > 0:
                performance = "Positive"
            else:
                performance = "Declining"
            
            logger.debug(f"EPS analysis completed - Growth: {eps_growth}%, Performance: {performance}")
            return {
                "current_eps": current_eps,
                "prior_eps": prior_eps,
                "eps_growth": round(eps_growth, 2),
                "performance_rating": performance,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error analyzing EPS performance: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def generate_investment_summary(self, focus_area: str = "comprehensive") -> Dict[str, Any]:
        """Generate investment summary"""
        try:
            logger.debug(f"Generating investment summary with focus: {focus_area}")
            growth_data = self.calculate_growth_rate("NetIncome")
            ratios = self.calculate_financial_ratios()
            eps_analysis = self.analyze_eps_performance()
            
            summary = {
                "company": self.financial_data.get('company_name_en', 'Unknown Company'),
                "analysis_focus": focus_area,
                "key_highlights": [],
                "strengths": [],
                "overall_rating": "",
                "status": "success"
            }
            
            # Add highlights
            net_income_growth = growth_data.get("growth_rate", 0)
            eps_growth = eps_analysis.get("eps_growth", 0)
            roe = ratios.get("roe", 0)
            
            summary["key_highlights"] = [
                f"Net Income Growth: {net_income_growth}%",
                f"EPS Growth: {eps_growth}%",
                f"ROE: {roe}%"
            ]
            
            # Add strengths
            if net_income_growth > 20:
                summary["strengths"].append(f"Strong profit growth: {net_income_growth}%")
            if roe > 15:
                summary["strengths"].append(f"Excellent ROE: {roe}%")
            
            # Overall rating
            strength_count = len(summary["strengths"])
            if strength_count >= 2:
                summary["overall_rating"] = "Buy"
            elif strength_count >= 1:
                summary["overall_rating"] = "Hold"
            else:
                summary["overall_rating"] = "Sell"
            
            logger.info(f"Investment summary generated - Rating: {summary['overall_rating']}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating investment summary: {str(e)}")
            return {"error": str(e), "status": "error"}

    def get_tools_definitions(self) -> List[Dict]:
        """Define tools for function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_growth_rate",
                    "description": "Calculate growth rate for a financial metric",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric": {
                                "type": "string",
                                "enum": ["NetIncome", "EPS", "NetAssets", "TotalAssets", "CashAndCashEquivalents"]
                            }
                        },
                        "required": ["metric"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_financial_ratios",
                    "description": "Calculate financial ratios (ROE, ROA, etc.)",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_company_overview",
                    "description": "Get company basic information",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_eps_performance",
                    "description": "Analyze EPS performance",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_investment_summary",
                    "description": "Generate investment summary",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "focus_area": {
                                "type": "string",
                                "enum": ["growth", "profitability", "comprehensive"],
                                "default": "comprehensive"
                            }
                        }
                    }
                }
            }
        ]

    def execute_function(self, function_name: str, arguments: Dict) -> Any:
        """Execute function"""
        logger.debug(f"Executing function: {function_name} with arguments: {arguments}")
        
        if function_name == "calculate_growth_rate":
            return self.calculate_growth_rate(arguments.get("metric"))
        elif function_name == "calculate_financial_ratios":
            return self.calculate_financial_ratios()
        elif function_name == "get_company_overview":
            return self.get_company_overview()
        elif function_name == "analyze_eps_performance":
            return self.analyze_eps_performance()
        elif function_name == "generate_investment_summary":
            return self.generate_investment_summary(arguments.get("focus_area", "comprehensive"))
        else:
            logger.error(f"Unknown function called: {function_name}")
            return {"error": f"Unknown function: {function_name}", "status": "error"}

    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def _make_openai_request(self, messages: List[Dict], tools: List[Dict] = None) -> Any:
        """Make OpenAI request with retry"""
        logger.debug("Making OpenAI API request")
        params = {
            "model": self.deployment_name,
            "messages": messages,
            "temperature": 0.1
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        try:
            response = self.client.chat.completions.create(**params)
            logger.debug("OpenAI API request successful")
            return response
        except Exception as e:
            logger.error(f"OpenAI API request failed: {str(e)}")
            raise

    def chat(self, user_message: str) -> str:
        """Chat with AI"""
        logger.debug(f"Processing user message: {user_message[:100]}...")
        self.conversation_history.append({"role": "user", "content": user_message})
        
        company_name = self.financial_data.get('company_name_en', 'the company')
        system_prompt = f"""You are a financial analyst. You have access to {company_name}'s financial data. 
        Use the available tools to provide accurate analysis. Be professional and provide actionable insights."""
        
        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history
        
        try:
            # First request
            response = self._make_openai_request(messages, self.get_tools_definitions())
            message = response.choices[0].message
            
            if message.tool_calls:
                logger.debug(f"Processing {len(message.tool_calls)} tool calls")
                # Handle tool calls
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                })
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    function_result = self.execute_function(function_name, function_args)
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result)
                    })
                
                # Second request for final response
                final_response = self._make_openai_request(
                    [{"role": "system", "content": system_prompt}] + self.conversation_history
                )
                final_message = final_response.choices[0].message.content
                self.conversation_history.append({"role": "assistant", "content": final_message})
                logger.debug("Chat response generated successfully with tool calls")
                return final_message
            else:
                self.conversation_history.append({"role": "assistant", "content": message.content})
                logger.debug("Chat response generated successfully without tool calls")
                return message.content
                
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            logger.error(f"Chat processing error: {str(e)}")
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return error_msg


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simple Financial Analyzer")
    parser.add_argument("--file", required=True, help="Path to CSV file")
    args = parser.parse_args()
    
    try:
        logger.info("Starting Simple Financial Analyzer")
        print("🏢 Simple Financial Analyzer")
        print("=" * 50)
        
        # Initialize analyzer
        analyzer = FinancialAnalyzer()
        logger.info("Analyzer initialized successfully")
        
        # Extract data from CSV
        analyzer.extract_data_from_csv(args.file)
        
        # Run 5 sample analyses
        print(f"\n🤖 Running 5 Sample Analyses:")
        print("=" * 50)
        
        samples = [
            "What is the company's basic information including name, code, and document type?",
            "Calculate and analyze the growth rate for net income between current and prior periods.", 
            "Please calculate ROE, ROA, and equity ratio to assess profitability performance.",
            "Analyze the Earnings Per Share (EPS) performance and provide a performance rating.",
            "Create a comprehensive investment analysis summary with overall recommendation."
        ]
        
        for i, query in enumerate(samples, 1):
            logger.info(f"Processing sample query {i}: {query[:50]}...")
            print(f"\n🔍 Sample {i}: {query}")
            print("-" * 40)
            response = analyzer.chat(query)
            print(response)
            print()
        
        logger.info("Analysis completed successfully")
        print("✅ Analysis completed!")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()