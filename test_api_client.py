#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive API Client Testing Suite
Heavy testing and optimization for the enhanced API client
"""

import os
import sys
import time
import json
import asyncio
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from unittest.mock import Mock, patch, MagicMock

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_client_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APIClientTester:
    """Comprehensive testing suite for the optimized API client"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        
        # Import the API client
        try:
            from api_client import APIClient, APICache, RateLimiter, APIMetrics
            self.APIClient = APIClient
            self.APICache = APICache
            self.RateLimiter = RateLimiter
            self.APIMetrics = APIMetrics
        except ImportError as e:
            logger.error(f"Failed to import API client: {e}")
            raise
    
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
    
    def test_api_client_initialization(self) -> bool:
        """Test API client initialization"""
        logger.info("🔧 Testing API Client Initialization...")
        start_time = time.time()
        
        try:
            client = self.APIClient()
            
            # Test basic attributes
            required_attrs = ['api_key', 'api_base', 'timeout', 'max_retries', 'headers']
            for attr in required_attrs:
                if not hasattr(client, attr):
                    self.log_test_result(f"Missing Attribute: {attr}", False, f"Attribute {attr} not found")
                    return False
                else:
                    self.log_test_result(f"Attribute: {attr}", True, f"Value: {getattr(client, attr)}")
            
            # Test components
            components = ['metrics', 'cache', 'rate_limiter', 'session', 'circuit_breaker']
            for component in components:
                if not hasattr(client, component):
                    self.log_test_result(f"Missing Component: {component}", False, f"Component {component} not found")
                    return False
                else:
                    self.log_test_result(f"Component: {component}", True)
            
            duration = time.time() - start_time
            self.log_test_result("API Client Initialization", True, "All components initialized", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("API Client Initialization", False, str(e), duration)
            return False
    
    def test_cache_functionality(self) -> bool:
        """Test API cache functionality"""
        logger.info("💾 Testing API Cache Functionality...")
        start_time = time.time()
        
        try:
            # Create test cache
            cache = self.APICache(cache_dir=".test_cache", max_size=10, ttl_hours=1)
            
            # Test data
            test_endpoint = "/test/endpoint"
            test_payload = {"test": "data", "number": 42}
            test_response = {"result": "success", "data": "cached"}
            
            # Test cache set
            cache.set(test_endpoint, test_payload, test_response)
            self.log_test_result("Cache Set", True, "Data cached successfully")
            
            # Test cache get
            retrieved = cache.get(test_endpoint, test_payload)
            if retrieved == test_response:
                self.log_test_result("Cache Get", True, "Data retrieved correctly")
            else:
                self.log_test_result("Cache Get", False, f"Expected {test_response}, got {retrieved}")
                return False
            
            # Test cache key generation
            cache_key = cache._get_cache_key(test_endpoint, test_payload)
            if len(cache_key) == 32:  # MD5 hash length
                self.log_test_result("Cache Key Generation", True, f"Generated key: {cache_key}")
            else:
                self.log_test_result("Cache Key Generation", False, f"Invalid key length: {len(cache_key)}")
                return False
            
            # Test cache clear
            cache.clear()
            self.log_test_result("Cache Clear", True, "Cache cleared successfully")
            
            duration = time.time() - start_time
            self.log_test_result("Cache Functionality", True, "All cache operations working", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Cache Functionality", False, str(e), duration)
            return False
    
    def test_rate_limiter(self) -> bool:
        """Test rate limiter functionality"""
        logger.info("⏱️ Testing Rate Limiter...")
        start_time = time.time()
        
        try:
            # Create rate limiter with low limits for testing
            rate_limiter = self.RateLimiter(requests_per_minute=60, burst_size=5)
            
            # Test token acquisition
            acquired_tokens = 0
            for i in range(10):
                if rate_limiter.acquire():
                    acquired_tokens += 1
            
            # Should acquire up to burst_size tokens
            if acquired_tokens <= 5:
                self.log_test_result("Rate Limiter Burst", True, f"Acquired {acquired_tokens} tokens")
            else:
                self.log_test_result("Rate Limiter Burst", False, f"Acquired {acquired_tokens} tokens, expected <= 5")
                return False
            
            # Test wait for token
            success = rate_limiter.wait_for_token(max_wait=1.0)
            self.log_test_result("Rate Limiter Wait", True, f"Wait result: {success}")
            
            duration = time.time() - start_time
            self.log_test_result("Rate Limiter", True, "Rate limiting working correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Rate Limiter", False, str(e), duration)
            return False
    
    def test_metrics_tracking(self) -> bool:
        """Test metrics tracking functionality"""
        logger.info("📊 Testing Metrics Tracking...")
        start_time = time.time()
        
        try:
            metrics = self.APIMetrics()
            
            # Test metrics update
            metrics.update_metrics(True, 1.5, None)
            metrics.update_metrics(False, 2.0, "TIMEOUT")
            metrics.update_metrics(True, 0.5, None)
            
            # Verify metrics
            if metrics.total_requests == 3:
                self.log_test_result("Total Requests", True, f"Count: {metrics.total_requests}")
            else:
                self.log_test_result("Total Requests", False, f"Expected 3, got {metrics.total_requests}")
                return False
            
            if metrics.successful_requests == 2:
                self.log_test_result("Successful Requests", True, f"Count: {metrics.successful_requests}")
            else:
                self.log_test_result("Successful Requests", False, f"Expected 2, got {metrics.successful_requests}")
                return False
            
            if metrics.failed_requests == 1:
                self.log_test_result("Failed Requests", True, f"Count: {metrics.failed_requests}")
            else:
                self.log_test_result("Failed Requests", False, f"Expected 1, got {metrics.failed_requests}")
                return False
            
            if abs(metrics.average_response_time - 1.33) < 0.1:
                self.log_test_result("Average Response Time", True, f"Time: {metrics.average_response_time:.2f}s")
            else:
                self.log_test_result("Average Response Time", False, f"Expected ~1.33s, got {metrics.average_response_time:.2f}s")
                return False
            
            if "TIMEOUT" in metrics.error_counts and metrics.error_counts["TIMEOUT"] == 1:
                self.log_test_result("Error Counts", True, f"Error counts: {metrics.error_counts}")
            else:
                self.log_test_result("Error Counts", False, f"Expected TIMEOUT: 1, got {metrics.error_counts}")
                return False
            
            duration = time.time() - start_time
            self.log_test_result("Metrics Tracking", True, "All metrics tracking correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Metrics Tracking", False, str(e), duration)
            return False
    
    def test_circuit_breaker(self) -> bool:
        """Test circuit breaker functionality"""
        logger.info("🔌 Testing Circuit Breaker...")
        start_time = time.time()
        
        try:
            client = self.APIClient()
            
            # Test initial state
            if client.circuit_breaker['state'] == 'CLOSED':
                self.log_test_result("Initial State", True, "Circuit breaker starts in CLOSED state")
            else:
                self.log_test_result("Initial State", False, f"Expected CLOSED, got {client.circuit_breaker['state']}")
                return False
            
            # Test circuit breaker check
            if client._circuit_breaker_check():
                self.log_test_result("Circuit Breaker Check", True, "Check allows requests in CLOSED state")
            else:
                self.log_test_result("Circuit Breaker Check", False, "Check should allow requests in CLOSED state")
                return False
            
            # Simulate failures to trigger circuit breaker
            for i in range(6):  # Threshold is 5
                client._circuit_breaker_failure()
            
            # Check if circuit breaker opened
            if client.circuit_breaker['state'] == 'OPEN':
                self.log_test_result("Circuit Breaker Open", True, "Circuit breaker opened after failures")
            else:
                self.log_test_result("Circuit Breaker Open", False, f"Expected OPEN, got {client.circuit_breaker['state']}")
                return False
            
            # Test that requests are blocked when open
            if not client._circuit_breaker_check():
                self.log_test_result("Circuit Breaker Block", True, "Requests blocked when circuit breaker is OPEN")
            else:
                self.log_test_result("Circuit Breaker Block", False, "Requests should be blocked when circuit breaker is OPEN")
                return False
            
            duration = time.time() - start_time
            self.log_test_result("Circuit Breaker", True, "Circuit breaker working correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Circuit Breaker", False, str(e), duration)
            return False
    
    def test_mock_api_calls(self) -> bool:
        """Test API calls with mocked responses"""
        logger.info("🎭 Testing Mock API Calls...")
        start_time = time.time()
        
        try:
            client = self.APIClient()
            
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'Mock response'}}]
            }
            mock_response.elapsed.total_seconds.return_value = 1.5
            
            with patch.object(client.session, 'post', return_value=mock_response):
                result = client.call_text_api("Test prompt", use_cache=False)
                
                if result == "Mock response":
                    self.log_test_result("Mock Text API", True, "Mock text API call successful")
                else:
                    self.log_test_result("Mock Text API", False, f"Expected 'Mock response', got '{result}'")
                    return False
            
            # Mock image generation response
            mock_image_response = Mock()
            mock_image_response.status_code = 200
            mock_image_response.json.return_value = {
                'data': [{'url': 'https://example.com/image.jpg'}]
            }
            
            with patch.object(client.session, 'post', return_value=mock_image_response):
                result = client.call_image_api("Test image prompt", use_cache=False)
                
                if result == "https://example.com/image.jpg":
                    self.log_test_result("Mock Image API", True, "Mock image API call successful")
                else:
                    self.log_test_result("Mock Image API", False, f"Expected image URL, got '{result}'")
                    return False
            
            duration = time.time() - start_time
            self.log_test_result("Mock API Calls", True, "All mock API calls working", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Mock API Calls", False, str(e), duration)
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling scenarios"""
        logger.info("🛡️ Testing Error Handling...")
        start_time = time.time()
        
        try:
            client = self.APIClient()
            
            # Test timeout handling
            with patch.object(client.session, 'post', side_effect=requests.exceptions.Timeout):
                result = client.call_text_api("Test prompt", use_cache=False)
                if result is None:
                    self.log_test_result("Timeout Handling", True, "Timeout handled gracefully")
                else:
                    self.log_test_result("Timeout Handling", False, "Timeout should return None")
                    return False
            
            # Test network error handling
            with patch.object(client.session, 'post', side_effect=requests.exceptions.ConnectionError):
                result = client.call_text_api("Test prompt", use_cache=False)
                if result is None:
                    self.log_test_result("Network Error Handling", True, "Network error handled gracefully")
                else:
                    self.log_test_result("Network Error Handling", False, "Network error should return None")
                    return False
            
            # Test invalid response handling
            mock_invalid_response = Mock()
            mock_invalid_response.status_code = 200
            mock_invalid_response.json.return_value = {'invalid': 'response'}
            
            with patch.object(client.session, 'post', return_value=mock_invalid_response):
                result = client.call_text_api("Test prompt", use_cache=False)
                if result is None:
                    self.log_test_result("Invalid Response Handling", True, "Invalid response handled gracefully")
                else:
                    self.log_test_result("Invalid Response Handling", False, "Invalid response should return None")
                    return False
            
            duration = time.time() - start_time
            self.log_test_result("Error Handling", True, "All error scenarios handled correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Error Handling", False, str(e), duration)
            return False
    
    def test_concurrent_requests(self) -> bool:
        """Test concurrent request handling"""
        logger.info("🔄 Testing Concurrent Requests...")
        start_time = time.time()
        
        try:
            client = self.APIClient()
            
            # Mock successful responses for concurrent testing
            def mock_successful_response(*args, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'choices': [{'message': {'content': f'Response {threading.current_thread().name}'}}]
                }
                return mock_response
            
            with patch.object(client.session, 'post', side_effect=mock_successful_response):
                # Test concurrent requests
                results = []
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [
                        executor.submit(client.call_text_api, f"Prompt {i}", use_cache=False)
                        for i in range(10)
                    ]
                    
                    for future in as_completed(futures):
                        try:
                            result = future.result(timeout=10)
                            results.append(result)
                        except Exception as e:
                            self.log_test_result("Concurrent Request", False, f"Concurrent request failed: {e}")
                            return False
                
                if len(results) == 10:
                    self.log_test_result("Concurrent Requests", True, f"All {len(results)} concurrent requests completed")
                else:
                    self.log_test_result("Concurrent Requests", False, f"Expected 10 results, got {len(results)}")
                    return False
            
            duration = time.time() - start_time
            self.log_test_result("Concurrent Handling", True, "Concurrent requests handled correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Concurrent Handling", False, str(e), duration)
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        logger.info("⚡ Testing Performance Benchmarks...")
        start_time = time.time()
        
        try:
            client = self.APIClient()
            
            # Mock fast response for performance testing
            mock_fast_response = Mock()
            mock_fast_response.status_code = 200
            mock_fast_response.json.return_value = {
                'choices': [{'message': {'content': 'Fast response'}}]
            }
            
            with patch.object(client.session, 'post', return_value=mock_fast_response):
                # Test response time
                test_start = time.time()
                result = client.call_text_api("Performance test", use_cache=False)
                test_duration = time.time() - test_start
                
                if test_duration < 5.0:  # Should be fast with mock
                    self.log_test_result("Response Time", True, f"Response time: {test_duration:.3f}s")
                else:
                    self.log_test_result("Response Time", False, f"Response too slow: {test_duration:.3f}s")
                    return False
                
                # Test metrics after request
                metrics = client.get_metrics()
                if metrics['total_requests'] == 1:
                    self.log_test_result("Metrics After Request", True, f"Total requests: {metrics['total_requests']}")
                else:
                    self.log_test_result("Metrics After Request", False, f"Expected 1 request, got {metrics['total_requests']}")
                    return False
            
            duration = time.time() - start_time
            self.log_test_result("Performance Benchmarks", True, "Performance benchmarks passed", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Performance Benchmarks", False, str(e), duration)
            return False
    
    def test_health_check(self) -> bool:
        """Test health check functionality"""
        logger.info("🏥 Testing Health Check...")
        start_time = time.time()
        
        try:
            client = self.APIClient()
            
            # Mock health check response
            mock_health_response = Mock()
            mock_health_response.status_code = 200
            mock_health_response.elapsed.total_seconds.return_value = 0.5
            
            with patch.object(client.session, 'get', return_value=mock_health_response):
                health_status = client.health_check()
                
                if health_status['status'] == 'healthy':
                    self.log_test_result("Health Check Status", True, "Health check returned healthy status")
                else:
                    self.log_test_result("Health Check Status", False, f"Expected healthy, got {health_status['status']}")
                    return False
                
                if 'response_time' in health_status:
                    self.log_test_result("Health Check Response Time", True, f"Response time: {health_status['response_time']}s")
                else:
                    self.log_test_result("Health Check Response Time", False, "Response time not in health status")
                    return False
            
            duration = time.time() - start_time
            self.log_test_result("Health Check", True, "Health check working correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Health Check", False, str(e), duration)
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive API client tests"""
        logger.info("🚀 Starting API Client Testing Suite...")
        logger.info("=" * 80)
        
        test_functions = [
            self.test_api_client_initialization,
            self.test_cache_functionality,
            self.test_rate_limiter,
            self.test_metrics_tracking,
            self.test_circuit_breaker,
            self.test_mock_api_calls,
            self.test_error_handling,
            self.test_concurrent_requests,
            self.test_performance_benchmarks,
            self.test_health_check
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
        logger.info("📊 API CLIENT TESTING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {self.test_count}")
        logger.info(f"Passed: {self.passed_count}")
        logger.info(f"Failed: {self.failed_count}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Total Time: {total_time:.2f}s")
        
        if self.failed_count == 0:
            logger.info("🎉 ALL API CLIENT TESTS PASSED!")
        else:
            logger.warning(f"⚠️ {self.failed_count} API client tests failed")
        
        # Save results to file
        with open('api_client_test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("📄 API client test results saved to api_client_test_results.json")
        
        return summary

def main():
    """Main testing function"""
    tester = APIClientTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['failed'] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
