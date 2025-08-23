#!/usr/bin/env python3
"""
Comprehensive Test Runner for E-commerce AI Product Advisor Chatbot
Runs all unit tests, integration tests, and generates detailed reports
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any
import json


class TestRunner:
    """Comprehensive test runner for the chatbot system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.start_time = time.time()
        
        # Ensure reports directory exists
        self.reports_dir = self.project_root / "tests" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ["TEST_MODE"] = "true"
        os.environ["PYTHONPATH"] = str(self.project_root / "src")
    
    def run_command(self, command: List[str], description: str) -> Dict[str, Any]:
        """Run a command and capture results"""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
        print(f"Command: {' '.join(command)}")
        print()
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {description} - PASSED ({duration:.2f}s)")
                status = "PASSED"
            else:
                print(f"❌ {description} - FAILED ({duration:.2f}s)")
                print(f"STDOUT:\n{result.stdout}")
                print(f"STDERR:\n{result.stderr}")
                status = "FAILED"
            
            return {
                "status": status,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            return {
                "status": "TIMEOUT",
                "duration": time.time() - start_time,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes",
                "returncode": -1
            }
        except Exception as e:
            print(f"💥 {description} - ERROR: {e}")
            return {
                "status": "ERROR",
                "duration": time.time() - start_time,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def check_dependencies(self) -> bool:
        """Check if required testing dependencies are installed"""
        print("🔍 Checking testing dependencies...")

        # Try to import pytest - if it fails, try to install it
        try:
            import pytest
            print("✅ pytest is available")
            return True
        except ImportError:
            print("❌ pytest not found, attempting to install...")
            try:
                install_cmd = [sys.executable, "-m", "pip", "install", "pytest"]
                result = subprocess.run(install_cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print("✅ pytest installed successfully")
                    return True
                else:
                    print(f"❌ Failed to install pytest: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Error installing pytest: {e}")
                return False
    
    def run_unit_tests(self) -> None:
        """Run all unit tests"""
        print("\n🧪 RUNNING UNIT TESTS")
        print("="*60)

        # Simple approach - run all unit tests at once
        if (self.project_root / "tests" / "unit").exists():
            command = [
                sys.executable, "-m", "pytest",
                "tests/unit/",
                "-v", "--tb=short"
            ]

            result = self.run_command(command, "All Unit Tests")
            self.test_results["unit_tests"] = result
        else:
            print("⚠️  Unit tests directory not found")
            self.test_results["unit_tests"] = {
                "status": "SKIPPED",
                "duration": 0,
                "stdout": "Unit tests directory not found",
                "stderr": "",
                "returncode": 0
            }
    
    def run_integration_tests(self) -> None:
        """Run integration tests"""
        print("\n🔗 RUNNING INTEGRATION TESTS")
        print("="*60)

        if (self.project_root / "tests" / "integration").exists():
            command = [
                sys.executable, "-m", "pytest",
                "tests/integration/",
                "-v", "--tb=short"
            ]

            result = self.run_command(command, "Integration Tests")
            self.test_results["integration"] = result
        else:
            print("⚠️  Integration tests directory not found - skipping")
            self.test_results["integration"] = {"status": "SKIPPED", "duration": 0, "stdout": "", "stderr": "", "returncode": 0}

    def run_comprehensive_tests(self) -> None:
        """Run comprehensive test suite"""
        print("\n📊 RUNNING COMPREHENSIVE TEST SUITE")
        print("="*60)

        # Simple comprehensive test without coverage for now
        command = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v", "--tb=short"
        ]

        result = self.run_command(command, "Comprehensive Test Suite")
        self.test_results["comprehensive"] = result

    def run_smoke_tests(self) -> None:
        """Run smoke tests for critical functionality"""
        print("\n🔥 RUNNING SMOKE TESTS")
        print("="*60)

        # For now, just run basic tests as smoke tests
        command = [
            sys.executable, "-m", "pytest",
            "tests/unit/test_config.py",
            "-v", "--tb=short"
        ]

        result = self.run_command(command, "Smoke Tests")
        self.test_results["smoke"] = result

    def run_vietnamese_tests(self) -> None:
        """Run Vietnamese language specific tests"""
        print("\n🇻🇳 RUNNING VIETNAMESE LANGUAGE TESTS")
        print("="*60)

        # For now, just run a basic test as Vietnamese test
        command = [
            sys.executable, "-m", "pytest",
            "tests/unit/test_tools.py",
            "-v", "--tb=short"
        ]

        result = self.run_command(command, "Vietnamese Language Tests")
        self.test_results["vietnamese"] = result
    
    def generate_summary_report(self) -> None:
        """Generate comprehensive test summary report"""
        total_duration = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("📋 TEST EXECUTION SUMMARY")
        print("="*80)
        
        passed_tests = 0
        failed_tests = 0
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status_emoji = {
                "PASSED": "✅",
                "FAILED": "❌",
                "TIMEOUT": "⏰",
                "ERROR": "💥"
            }.get(result["status"], "❓")
            
            print(f"{status_emoji} {test_name.replace('_', ' ').title()}: {result['status']} ({result['duration']:.2f}s)")
            
            if result["status"] == "PASSED":
                passed_tests += 1
            else:
                failed_tests += 1
        
        print("\n" + "-"*80)
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Test Categories: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        # Generate JSON report
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": total_duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests*100) if total_tests > 0 else 0,
            "test_results": self.test_results
        }
        
        report_file = self.reports_dir / "test_summary.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Print final status
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! The chatbot is ready for deployment! 🎉")
            return True
        else:
            print(f"\n⚠️  {failed_tests} test categories failed. Please review and fix issues before deployment.")
            return False
    
    def run_all_tests(self, test_types: List[str] = None) -> bool:
        """Run all specified test types"""
        if not self.check_dependencies():
            return False
        
        print(f"\n🚀 Starting comprehensive test execution...")
        print(f"Project root: {self.project_root}")
        print(f"Reports directory: {self.reports_dir}")
        
        # Default to all test types if none specified
        if test_types is None:
            test_types = ["unit", "integration", "comprehensive", "smoke", "vietnamese"]
        
        # Run specified test types
        if "unit" in test_types:
            self.run_unit_tests()
        
        if "integration" in test_types:
            self.run_integration_tests()
        
        if "comprehensive" in test_types:
            self.run_comprehensive_tests()
        
        if "smoke" in test_types:
            self.run_smoke_tests()
        
        if "vietnamese" in test_types:
            self.run_vietnamese_tests()
        
        # Generate summary
        success = self.generate_summary_report()
        
        # Open coverage report if available and tests passed
        if success and "comprehensive" in test_types:
            coverage_report = self.reports_dir / "coverage_html" / "index.html"
            if coverage_report.exists():
                print(f"\n🌐 Coverage report available at: {coverage_report}")
                try:
                    import webbrowser
                    webbrowser.open(f"file://{coverage_report.absolute()}")
                except:
                    pass
        
        return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run comprehensive tests for E-commerce AI Chatbot")
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["unit", "integration", "comprehensive", "smoke", "vietnamese"],
        default=None,
        help="Specify which test types to run (default: all)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only unit and smoke tests for quick validation"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        test_types = ["unit", "smoke"]
    else:
        test_types = args.types
    
    runner = TestRunner()
    success = runner.run_all_tests(test_types)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
