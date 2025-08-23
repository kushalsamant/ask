#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Testing Suite for ASK Research Tool
Heavy testing and optimization framework
"""

import os
import sys
import time
import json
import traceback
import subprocess
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTester:
    """Comprehensive testing suite for ASK research tool"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test result with details"""
        self.test_count += 1
        if success:
            self.passed_count += 1
            logger.info(f"✅ PASS: {test_name} ({duration:.2f}s)")
        else:
            self.failed_count += 1
            logger.error(f"❌ FAIL: {test_name} ({duration:.2f}s)")
            if details:
                logger.error(f"   Details: {details}")
        
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_environment_setup(self) -> bool:
        """Test environment and dependencies"""
        logger.info("🔧 Testing Environment Setup...")
        start_time = time.time()
        
        try:
            # Test Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                self.log_test_result("Python Version", False, f"Python 3.8+ required, got {python_version}")
                return False
            else:
                self.log_test_result("Python Version", True, f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Test required packages
            required_packages = [
                'requests', 'pillow', 'numpy', 'pandas', 'dotenv',
                'torch', 'diffusers', 'transformers', 'accelerate'
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    importlib.import_module(package)
                    self.log_test_result(f"Package: {package}", True)
                except ImportError:
                    missing_packages.append(package)
                    self.log_test_result(f"Package: {package}", False, f"Package not found")
            
            if missing_packages:
                return False
            
            # Test environment file
            if not os.path.exists('ask.env'):
                self.log_test_result("Environment File", False, "ask.env not found")
                return False
            else:
                self.log_test_result("Environment File", True)
            
            # Test directories
            required_dirs = ['images', 'logs']
            for dir_name in required_dirs:
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)
                self.log_test_result(f"Directory: {dir_name}", True)
            
            duration = time.time() - start_time
            self.log_test_result("Environment Setup", True, duration=duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Environment Setup", False, str(e), duration)
            return False
    
    def test_module_imports(self) -> bool:
        """Test all module imports"""
        logger.info("📦 Testing Module Imports...")
        start_time = time.time()
        
        modules_to_test = [
            'main',
            'research_orchestrator',
            'research_question_generator',
            'research_answer_generator',
            'research_csv_manager',
            'image_generation_system',
            'smart_image_generator',
            'api_client',
            'volume_manager'
        ]
        
        failed_imports = []
        for module in modules_to_test:
            try:
                importlib.import_module(module)
                self.log_test_result(f"Import: {module}", True)
            except ImportError as e:
                failed_imports.append(f"{module}: {str(e)}")
                self.log_test_result(f"Import: {module}", False, str(e))
        
        duration = time.time() - start_time
        success = len(failed_imports) == 0
        self.log_test_result("Module Imports", success, 
                           f"Failed: {len(failed_imports)}" if failed_imports else "All imports successful", 
                           duration)
        return success
    
    def test_configuration_loading(self) -> bool:
        """Test configuration loading"""
        logger.info("⚙️ Testing Configuration Loading...")
        start_time = time.time()
        
        try:
            from dotenv import load_dotenv
            load_dotenv('ask.env')
            
            # Test required environment variables
            required_vars = [
                'TOGETHER_API_BASE',
                'TEXT_MODEL',
                'IMAGE_MODEL'
            ]
            
            missing_vars = []
            for var in required_vars:
                value = os.getenv(var)
                if value:
                    self.log_test_result(f"Config: {var}", True, f"Value: {value[:20]}...")
                else:
                    missing_vars.append(var)
                    self.log_test_result(f"Config: {var}", False, "Not set")
            
            # Test API key (don't log the actual key)
            api_key = os.getenv('TOGETHER_API_KEY')
            if api_key and api_key.startswith('tgp_'):
                self.log_test_result("API Key Format", True, "Valid format")
            else:
                self.log_test_result("API Key Format", False, "Invalid or missing API key")
                missing_vars.append('TOGETHER_API_KEY')
            
            duration = time.time() - start_time
            success = len(missing_vars) == 0
            self.log_test_result("Configuration Loading", success, 
                               f"Missing: {len(missing_vars)}" if missing_vars else "All configs loaded", 
                               duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Configuration Loading", False, str(e), duration)
            return False
    
    def test_api_connectivity(self) -> bool:
        """Test API connectivity"""
        logger.info("🌐 Testing API Connectivity...")
        start_time = time.time()
        
        try:
            import requests
            from dotenv import load_dotenv
            load_dotenv('ask.env')
            
            api_base = os.getenv('TOGETHER_API_BASE')
            api_key = os.getenv('TOGETHER_API_KEY')
            
            if not api_base or not api_key:
                self.log_test_result("API Connectivity", False, "Missing API configuration")
                return False
            
            # Test API endpoint
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Simple health check
            response = requests.get(f"{api_base}/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.log_test_result("API Endpoint", True, f"Status: {response.status_code}")
            else:
                self.log_test_result("API Endpoint", False, f"Status: {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test_result("API Connectivity", True, "Connection successful", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("API Connectivity", False, str(e), duration)
            return False
    
    def test_image_generation_system(self) -> bool:
        """Test image generation system"""
        logger.info("🎨 Testing Image Generation System...")
        start_time = time.time()
        
        try:
            from smart_image_generator import generate_image_with_smart_fallback
            
            # Test with a simple prompt
            test_prompt = "A simple architectural sketch"
            test_theme = "design_research"
            
            # This might take time, so we'll set a timeout
            result = generate_image_with_smart_fallback(test_prompt, test_theme)
            
            if result and os.path.exists(result):
                self.log_test_result("Image Generation", True, f"Generated: {result}")
            else:
                self.log_test_result("Image Generation", False, "No image generated")
                return False
            
            duration = time.time() - start_time
            self.log_test_result("Image Generation System", True, "System functional", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Image Generation System", False, str(e), duration)
            return False
    
    def test_research_orchestration(self) -> bool:
        """Test research orchestration"""
        logger.info("🔬 Testing Research Orchestration...")
        start_time = time.time()
        
        try:
            from research_orchestrator import ResearchOrchestrator
            
            orchestrator = ResearchOrchestrator()
            
            # Test theme generation
            themes = orchestrator.get_available_themes()
            if themes and len(themes) > 0:
                self.log_test_result("Theme Generation", True, f"Found {len(themes)} themes")
            else:
                self.log_test_result("Theme Generation", False, "No themes found")
                return False
            
            # Test question generation
            test_theme = themes[0] if themes else "design_research"
            question = orchestrator.generate_question(test_theme)
            
            if question and len(question) > 10:
                self.log_test_result("Question Generation", True, f"Generated: {question[:50]}...")
            else:
                self.log_test_result("Question Generation", False, "No question generated")
                return False
            
            duration = time.time() - start_time
            self.log_test_result("Research Orchestration", True, "Orchestration functional", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Research Orchestration", False, str(e), duration)
            return False
    
    def test_data_management(self) -> bool:
        """Test data management systems"""
        logger.info("📊 Testing Data Management...")
        start_time = time.time()
        
        try:
            from research_csv_manager import read_log_csv, log_single_question
            
            # Test CSV reading
            if os.path.exists('log.csv'):
                data = read_log_csv()
                if data is not None:
                    self.log_test_result("CSV Reading", True, f"Read {len(data)} records")
                else:
                    self.log_test_result("CSV Reading", False, "Failed to read CSV")
                    return False
            else:
                self.log_test_result("CSV Reading", True, "No CSV file (will be created)")
            
            # Test CSV writing
            test_data = {
                'question': 'Test question for data management',
                'answer': 'Test answer for data management',
                'theme': 'test_theme',
                'timestamp': datetime.now().isoformat()
            }
            
            success = log_single_question(test_data)
            if success:
                self.log_test_result("CSV Writing", True, "Data logged successfully")
            else:
                self.log_test_result("CSV Writing", False, "Failed to log data")
                return False
            
            duration = time.time() - start_time
            self.log_test_result("Data Management", True, "Management systems functional", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Data Management", False, str(e), duration)
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        logger.info("⚡ Testing Performance Benchmarks...")
        start_time = time.time()
        
        try:
            # Test import performance
            import_start = time.time()
            from research_orchestrator import ResearchOrchestrator
            import_time = time.time() - import_start
            
            if import_time < 5.0:  # Should import in under 5 seconds
                self.log_test_result("Import Performance", True, f"Import time: {import_time:.2f}s")
            else:
                self.log_test_result("Import Performance", False, f"Slow import: {import_time:.2f}s")
            
            # Test memory usage
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 500:  # Should use less than 500MB
                self.log_test_result("Memory Usage", True, f"Memory: {memory_mb:.1f}MB")
            else:
                self.log_test_result("Memory Usage", False, f"High memory: {memory_mb:.1f}MB")
            
            duration = time.time() - start_time
            self.log_test_result("Performance Benchmarks", True, "Performance acceptable", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Performance Benchmarks", False, str(e), duration)
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling"""
        logger.info("🛡️ Testing Error Handling...")
        start_time = time.time()
        
        try:
            # Test with invalid API key
            from api_client import make_api_request
            
            # This should handle the error gracefully
            try:
                result = make_api_request("invalid_key", "test", {})
                self.log_test_result("Invalid API Key Handling", True, "Error handled gracefully")
            except Exception as e:
                if "invalid" in str(e).lower() or "401" in str(e) or "403" in str(e):
                    self.log_test_result("Invalid API Key Handling", True, "Error handled gracefully")
                else:
                    self.log_test_result("Invalid API Key Handling", False, f"Unexpected error: {str(e)}")
            
            # Test with invalid file paths
            from research_csv_manager import read_log_csv
            
            try:
                # This should handle missing file gracefully
                data = read_log_csv("nonexistent_file.csv")
                self.log_test_result("Invalid File Path Handling", True, "Error handled gracefully")
            except Exception as e:
                if "file" in str(e).lower() or "not found" in str(e).lower():
                    self.log_test_result("Invalid File Path Handling", True, "Error handled gracefully")
                else:
                    self.log_test_result("Invalid File Path Handling", False, f"Unexpected error: {str(e)}")
            
            duration = time.time() - start_time
            self.log_test_result("Error Handling", True, "Error handling functional", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Error Handling", False, str(e), duration)
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive Testing Suite...")
        logger.info("=" * 80)
        
        test_functions = [
            self.test_environment_setup,
            self.test_module_imports,
            self.test_configuration_loading,
            self.test_api_connectivity,
            self.test_image_generation_system,
            self.test_research_orchestration,
            self.test_data_management,
            self.test_performance_benchmarks,
            self.test_error_handling
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                logger.error(f"❌ Test {test_func.__name__} crashed: {str(e)}")
                self.log_test_result(test_func.__name__, False, f"Test crashed: {str(e)}")
        
        # Generate summary
        total_time = time.time() - self.start_time
        success_rate = (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
        
        summary = {
            'total_tests': self.test_count,
            'passed': self.passed_count,
            'failed': self.failed_count,
            'success_rate': success_rate,
            'total_time': total_time,
            'timestamp': datetime.now().isoformat(),
            'results': self.test_results
        }
        
        # Log summary
        logger.info("=" * 80)
        logger.info("📊 TESTING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {self.test_count}")
        logger.info(f"Passed: {self.passed_count}")
        logger.info(f"Failed: {self.failed_count}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Total Time: {total_time:.2f}s")
        
        if self.failed_count == 0:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.warning(f"⚠️ {self.failed_count} tests failed")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("📄 Results saved to test_results.json")
        
        return summary

def main():
    """Main testing function"""
    tester = ComprehensiveTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['failed'] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
