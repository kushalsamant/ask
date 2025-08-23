#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive ASK Environment Configuration Testing Suite
Heavy testing and optimization for ask.env configuration
"""

import os
import sys
import time
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import configparser
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ask_env_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ConfigValidation:
    """Configuration validation result"""
    key: str
    value: Any
    is_valid: bool
    expected_type: str
    actual_type: str
    validation_message: str
    category: str

class ASKEnvTester:
    """Comprehensive testing suite for ask.env configuration"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.validation_results = []
        self.optimization_suggestions = []
        
        # Load environment file
        self.env_file = 'ask.env.optimized'  # Test the optimized version
        self.config_data = {}
        self.load_environment_file()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test result with details"""
        self.test_count += 1
        if success:
            self.passed_count += 1
            logger.info(f"PASS: {test_name} ({duration:.2f}s)")
        else:
            self.failed_count += 1
            logger.error(f"FAIL: {test_name} ({duration:.2f}s)")
            if details:
                logger.error(f"   Details: {details}")
        
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
    
    def load_environment_file(self):
        """Load and parse the environment file"""
        try:
            if not os.path.exists(self.env_file):
                raise FileNotFoundError(f"Environment file {self.env_file} not found")
            
            # Load using python-dotenv
            load_dotenv(self.env_file)
            
            # Read raw file content for analysis
            with open(self.env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse key-value pairs with proper comment handling
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    # Split on first '=' and handle comments
                    parts = line.split('=', 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Remove inline comments (everything after #)
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    self.config_data[key] = value
            
            logger.info(f"Loaded {len(self.config_data)} configuration variables")
            
        except Exception as e:
            logger.error(f"Failed to load environment file: {e}")
            raise
    
    def test_file_structure(self) -> bool:
        """Test environment file structure and format"""
        logger.info("Testing Environment File Structure...")
        start_time = time.time()
        
        try:
            # Check file exists
            if not os.path.exists(self.env_file):
                self.log_test_result("File Exists", False, "Environment file not found")
                return False
            else:
                self.log_test_result("File Exists", True)
            
            # Check file size
            file_size = os.path.getsize(self.env_file)
            if file_size > 0:
                self.log_test_result("File Size", True, f"File size: {file_size} bytes")
            else:
                self.log_test_result("File Size", False, "File is empty")
                return False
            
            # Check encoding
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.log_test_result("File Encoding", True, "UTF-8 encoding valid")
            except UnicodeDecodeError:
                self.log_test_result("File Encoding", False, "Invalid encoding")
                return False
            
            # Check for required sections
            required_sections = [
                'API CONFIGURATION',
                'AI MODEL CONFIGURATION',
                'TEXT GENERATION CONFIGURATION',
                'IMAGE GENERATION CONFIGURATION'
            ]
            
            content_lower = content.lower()
            for section in required_sections:
                if section.lower() in content_lower:
                    self.log_test_result(f"Section: {section}", True)
                else:
                    self.log_test_result(f"Section: {section}", False, f"Missing section: {section}")
            
            duration = time.time() - start_time
            self.log_test_result("File Structure", True, "File structure is valid", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("File Structure", False, str(e), duration)
            return False
    
    def test_required_variables(self) -> bool:
        """Test required environment variables"""
        logger.info("Testing Required Environment Variables...")
        start_time = time.time()
        
        required_vars = {
            'TOGETHER_API_BASE': str,
            'TEXT_MODEL': str,
            'IMAGE_MODEL': str,
            'VISION_MODEL': str,
            'API_TIMEOUT': int,
            'RATE_LIMIT_DELAY': float,
            'API_MAX_RETRIES': int,
            'TEXT_TEMPERATURE': float,
            'TEXT_MAX_TOKENS': int,
            'IMAGE_WIDTH': int,
            'IMAGE_HEIGHT': int,
            'INFERENCE_STEPS': int,
            'GUIDANCE_SCALE': float
        }
        
        missing_vars = []
        invalid_types = []
        
        for var, expected_type in required_vars.items():
            if var not in self.config_data:
                missing_vars.append(var)
                self.log_test_result(f"Required Variable: {var}", False, "Variable missing")
            else:
                value = self.config_data[var]
                try:
                    # Try to convert to expected type
                    if expected_type == int:
                        int(value)
                    elif expected_type == float:
                        float(value)
                    elif expected_type == str:
                        str(value)
                    
                    self.log_test_result(f"Required Variable: {var}", True, f"Value: {value}")
                except (ValueError, TypeError):
                    invalid_types.append(f"{var} (expected {expected_type.__name__}, got {type(value).__name__})")
                    self.log_test_result(f"Required Variable: {var}", False, f"Invalid type: expected {expected_type.__name__}")
        
        if missing_vars:
            self.log_test_result("Required Variables", False, f"Missing: {', '.join(missing_vars)}")
            return False
        
        if invalid_types:
            self.log_test_result("Required Variables", False, f"Invalid types: {', '.join(invalid_types)}")
            return False
        
        duration = time.time() - start_time
        self.log_test_result("Required Variables", True, "All required variables present and valid", duration)
        return True
    
    def test_api_configuration(self) -> bool:
        """Test API configuration settings"""
        logger.info("Testing API Configuration...")
        start_time = time.time()
        
        api_configs = {
            'TOGETHER_API_BASE': {
                'type': str,
                'pattern': r'^https?://.+',
                'description': 'API base URL'
            },
            'API_TIMEOUT': {
                'type': int,
                'min': 10,
                'max': 300,
                'description': 'Request timeout'
            },
            'RATE_LIMIT_DELAY': {
                'type': float,
                'min': 0.1,
                'max': 60.0,
                'description': 'Rate limit delay'
            },
            'API_MAX_RETRIES': {
                'type': int,
                'min': 1,
                'max': 10,
                'description': 'Max retry attempts'
            }
        }
        
        validation_results = []
        
        for key, config in api_configs.items():
            if key in self.config_data:
                value = self.config_data[key]
                validation = self.validate_config_value(key, value, config)
                validation_results.append(validation)
                
                if validation.is_valid:
                    self.log_test_result(f"API Config: {key}", True, f"{validation.validation_message}")
                else:
                    self.log_test_result(f"API Config: {key}", False, f"{validation.validation_message}")
            else:
                self.log_test_result(f"API Config: {key}", False, "Variable missing")
        
        duration = time.time() - start_time
        success = all(r.is_valid for r in validation_results)
        self.log_test_result("API Configuration", success, f"API configuration validation complete", duration)
        return success
    
    def test_model_configuration(self) -> bool:
        """Test AI model configuration"""
        logger.info("Testing AI Model Configuration...")
        start_time = time.time()
        
        model_configs = {
            'TEXT_MODEL': {
                'type': str,
                'required': True,
                'description': 'Text generation model'
            },
            'IMAGE_MODEL': {
                'type': str,
                'required': True,
                'description': 'Image generation model'
            },
            'VISION_MODEL': {
                'type': str,
                'required': True,
                'description': 'Vision model'
            }
        }
        
        validation_results = []
        
        for key, config in model_configs.items():
            if key in self.config_data:
                value = self.config_data[key]
                if value and len(value) > 0:
                    self.log_test_result(f"Model Config: {key}", True, f"Model: {value}")
                    validation_results.append(True)
                else:
                    self.log_test_result(f"Model Config: {key}", False, "Empty model name")
                    validation_results.append(False)
            else:
                self.log_test_result(f"Model Config: {key}", False, "Model not configured")
                validation_results.append(False)
        
        duration = time.time() - start_time
        success = all(validation_results)
        self.log_test_result("Model Configuration", success, f"Model configuration validation complete", duration)
        return success
    
    def test_text_generation_config(self) -> bool:
        """Test text generation configuration"""
        logger.info("Testing Text Generation Configuration...")
        start_time = time.time()
        
        text_configs = {
            'TEXT_TEMPERATURE': {
                'type': float,
                'min': 0.0,
                'max': 2.0,
                'description': 'Temperature for text generation'
            },
            'TEXT_MAX_TOKENS': {
                'type': int,
                'min': 10,
                'max': 2000,
                'description': 'Maximum tokens for text generation'
            },
            'TEXT_TOP_P': {
                'type': float,
                'min': 0.0,
                'max': 1.0,
                'description': 'Top-p sampling'
            },
            'TEXT_FREQUENCY_PENALTY': {
                'type': float,
                'min': -2.0,
                'max': 2.0,
                'description': 'Frequency penalty'
            },
            'TEXT_PRESENCE_PENALTY': {
                'type': float,
                'min': -2.0,
                'max': 2.0,
                'description': 'Presence penalty'
            }
        }
        
        validation_results = []
        
        for key, config in text_configs.items():
            if key in self.config_data:
                value = self.config_data[key]
                validation = self.validate_config_value(key, value, config)
                validation_results.append(validation)
                
                if validation.is_valid:
                    self.log_test_result(f"Text Config: {key}", True, f"{validation.validation_message}")
                else:
                    self.log_test_result(f"Text Config: {key}", False, f"{validation.validation_message}")
            else:
                self.log_test_result(f"Text Config: {key}", False, "Variable missing")
        
        duration = time.time() - start_time
        success = all(r.is_valid for r in validation_results)
        self.log_test_result("Text Generation Config", success, f"Text generation configuration validation complete", duration)
        return success
    
    def test_image_generation_config(self) -> bool:
        """Test image generation configuration"""
        logger.info("Testing Image Generation Configuration...")
        start_time = time.time()
        
        image_configs = {
            'IMAGE_WIDTH': {
                'type': int,
                'min': 256,
                'max': 2048,
                'description': 'Image width'
            },
            'IMAGE_HEIGHT': {
                'type': int,
                'min': 256,
                'max': 2048,
                'description': 'Image height'
            },
            'INFERENCE_STEPS': {
                'type': int,
                'min': 1,
                'max': 100,
                'description': 'Inference steps'
            },
            'GUIDANCE_SCALE': {
                'type': float,
                'min': 0.1,
                'max': 20.0,
                'description': 'Guidance scale'
            },
            'IMAGE_QUALITY': {
                'type': int,
                'min': 1,
                'max': 100,
                'description': 'Image quality'
            }
        }
        
        validation_results = []
        
        for key, config in image_configs.items():
            if key in self.config_data:
                value = self.config_data[key]
                validation = self.validate_config_value(key, value, config)
                validation_results.append(validation)
                
                if validation.is_valid:
                    self.log_test_result(f"Image Config: {key}", True, f"{validation.validation_message}")
                else:
                    self.log_test_result(f"Image Config: {key}", False, f"{validation.validation_message}")
            else:
                self.log_test_result(f"Image Config: {key}", False, "Variable missing")
        
        duration = time.time() - start_time
        success = all(r.is_valid for r in validation_results)
        self.log_test_result("Image Generation Config", success, f"Image generation configuration validation complete", duration)
        return success
    
    def test_mode_configuration(self) -> bool:
        """Test mode-specific configuration"""
        logger.info("Testing Mode Configuration...")
        start_time = time.time()
        
        mode_configs = {
            'HYBRID_THEME_COUNT': {
                'type': int,
                'min': 1,
                'max': 20,
                'description': 'Hybrid mode theme count'
            },
            'HYBRID_CHAIN_LENGTH': {
                'type': int,
                'min': 1,
                'max': 10,
                'description': 'Hybrid mode chain length'
            },
            'CROSS_DISCIPLINARY_THEME_COUNT': {
                'type': int,
                'min': 1,
                'max': 20,
                'description': 'Cross-disciplinary theme count'
            },
            'CHAIN_LENGTH': {
                'type': int,
                'min': 1,
                'max': 10,
                'description': 'Chained mode chain length'
            }
        }
        
        validation_results = []
        
        for key, config in mode_configs.items():
            if key in self.config_data:
                value = self.config_data[key]
                validation = self.validate_config_value(key, value, config)
                validation_results.append(validation)
                
                if validation.is_valid:
                    self.log_test_result(f"Mode Config: {key}", True, f"{validation.validation_message}")
                else:
                    self.log_test_result(f"Mode Config: {key}", False, f"{validation.validation_message}")
            else:
                self.log_test_result(f"Mode Config: {key}", False, "Variable missing")
        
        duration = time.time() - start_time
        success = all(r.is_valid for r in validation_results)
        self.log_test_result("Mode Configuration", success, f"Mode configuration validation complete", duration)
        return success
    
    def test_optimization_settings(self) -> bool:
        """Test optimization and performance settings"""
        logger.info("Testing Optimization Settings...")
        start_time = time.time()
        
        optimization_configs = {
            'CPU_IMAGE_GENERATION_ENABLED': {
                'type': bool,
                'description': 'CPU image generation enabled'
            },
            'GPU_IMAGE_GENERATION_ENABLED': {
                'type': bool,
                'description': 'GPU image generation enabled'
            },
            'BATCH_SIZE': {
                'type': int,
                'min': 1,
                'max': 20,
                'description': 'Batch size for processing'
            },
            'PARALLEL_PROCESSING': {
                'type': bool,
                'description': 'Parallel processing enabled'
            }
        }
        
        validation_results = []
        
        for key, config in optimization_configs.items():
            if key in self.config_data:
                value = self.config_data[key]
                validation = self.validate_config_value(key, value, config)
                validation_results.append(validation)
                
                if validation.is_valid:
                    self.log_test_result(f"Optimization Config: {key}", True, f"{validation.validation_message}")
                else:
                    self.log_test_result(f"Optimization Config: {key}", False, f"{validation.validation_message}")
            else:
                self.log_test_result(f"Optimization Config: {key}", False, "Variable missing")
        
        duration = time.time() - start_time
        success = all(r.is_valid for r in validation_results)
        self.log_test_result("Optimization Settings", success, f"Optimization settings validation complete", duration)
        return success
    
    def test_duplicate_variables(self) -> bool:
        """Test for duplicate variable definitions"""
        logger.info("Testing for Duplicate Variables...")
        start_time = time.time()
        
        # Read raw file content
        with open(self.env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all variable definitions
        variable_pattern = r'^([A-Z_][A-Z0-9_]*)\s*='
        variables = re.findall(variable_pattern, content, re.MULTILINE)
        
        # Check for duplicates
        duplicates = []
        seen = set()
        for var in variables:
            if var in seen:
                duplicates.append(var)
            else:
                seen.add(var)
        
        if duplicates:
            self.log_test_result("Duplicate Variables", False, f"Found duplicates: {', '.join(duplicates)}")
            return False
        else:
            self.log_test_result("Duplicate Variables", True, f"No duplicates found in {len(variables)} variables")
        
        duration = time.time() - start_time
        self.log_test_result("Duplicate Check", True, "Duplicate variable check complete", duration)
        return True
    
    def test_value_consistency(self) -> bool:
        """Test for value consistency and logical relationships"""
        logger.info("Testing Value Consistency...")
        start_time = time.time()
        
        consistency_checks = []
        
        # Check image dimensions consistency
        if 'IMAGE_WIDTH' in self.config_data and 'IMAGE_HEIGHT' in self.config_data:
            try:
                width = int(self.config_data['IMAGE_WIDTH'])
                height = int(self.config_data['IMAGE_HEIGHT'])
                
                if width > 0 and height > 0:
                    aspect_ratio = width / height
                    if 0.1 < aspect_ratio < 10.0:  # Reasonable aspect ratio
                        consistency_checks.append(("Image Dimensions", True, f"Aspect ratio: {aspect_ratio:.2f}"))
                    else:
                        consistency_checks.append(("Image Dimensions", False, f"Unusual aspect ratio: {aspect_ratio:.2f}"))
                else:
                    consistency_checks.append(("Image Dimensions", False, "Invalid dimensions"))
            except ValueError:
                consistency_checks.append(("Image Dimensions", False, "Non-numeric dimensions"))
        
        # Check timeout consistency
        if 'API_TIMEOUT' in self.config_data and 'RATE_LIMIT_DELAY' in self.config_data:
            try:
                timeout = int(self.config_data['API_TIMEOUT'])
                delay = float(self.config_data['RATE_LIMIT_DELAY'])
                
                if timeout > delay * 2:  # Timeout should be significantly larger than delay
                    consistency_checks.append(("Timeout Consistency", True, f"Timeout ({timeout}s) > 2x delay ({delay}s)"))
                else:
                    consistency_checks.append(("Timeout Consistency", False, f"Timeout ({timeout}s) too close to delay ({delay}s)"))
            except ValueError:
                consistency_checks.append(("Timeout Consistency", False, "Non-numeric values"))
        
        # Check mode configuration consistency
        if 'HYBRID_THEME_COUNT' in self.config_data and 'HYBRID_CHAIN_LENGTH' in self.config_data:
            try:
                theme_count = int(self.config_data['HYBRID_THEME_COUNT'])
                chain_length = int(self.config_data['HYBRID_CHAIN_LENGTH'])
                total_pairs = theme_count * chain_length
                
                if total_pairs == 10:  # Expected total
                    consistency_checks.append(("Hybrid Mode", True, f"Total Q&A pairs: {total_pairs}"))
                else:
                    consistency_checks.append(("Hybrid Mode", False, f"Expected 10 Q&A pairs, got {total_pairs}"))
            except ValueError:
                consistency_checks.append(("Hybrid Mode", False, "Non-numeric values"))
        
        # Log consistency check results
        for check_name, is_valid, message in consistency_checks:
            if is_valid:
                self.log_test_result(f"Consistency: {check_name}", True, message)
            else:
                self.log_test_result(f"Consistency: {check_name}", False, message)
        
        duration = time.time() - start_time
        success = all(is_valid for _, is_valid, _ in consistency_checks)
        self.log_test_result("Value Consistency", success, f"Value consistency checks complete", duration)
        return success
    
    def test_performance_optimization(self) -> bool:
        """Test performance optimization settings"""
        logger.info("Testing Performance Optimization...")
        start_time = time.time()
        
        optimization_checks = []
        
        # Check batch size optimization
        if 'BATCH_SIZE' in self.config_data:
            try:
                batch_size = int(self.config_data['BATCH_SIZE'])
                if 1 <= batch_size <= 10:
                    optimization_checks.append(("Batch Size", True, f"Optimal batch size: {batch_size}"))
                else:
                    optimization_checks.append(("Batch Size", False, f"Batch size {batch_size} may impact performance"))
            except ValueError:
                optimization_checks.append(("Batch Size", False, "Invalid batch size"))
        
        # Check timeout optimization
        if 'API_TIMEOUT' in self.config_data:
            try:
                timeout = int(self.config_data['API_TIMEOUT'])
                if 30 <= timeout <= 120:
                    optimization_checks.append(("API Timeout", True, f"Reasonable timeout: {timeout}s"))
                else:
                    optimization_checks.append(("API Timeout", False, f"Timeout {timeout}s may be too short/long"))
            except ValueError:
                optimization_checks.append(("API Timeout", False, "Invalid timeout"))
        
        # Check image generation settings
        if 'INFERENCE_STEPS' in self.config_data:
            try:
                steps = int(self.config_data['INFERENCE_STEPS'])
                if 4 <= steps <= 20:
                    optimization_checks.append(("Inference Steps", True, f"Balanced steps: {steps}"))
                else:
                    optimization_checks.append(("Inference Steps", False, f"Steps {steps} may affect quality/speed"))
            except ValueError:
                optimization_checks.append(("Inference Steps", False, "Invalid steps"))
        
        # Log optimization check results
        for check_name, is_valid, message in optimization_checks:
            if is_valid:
                self.log_test_result(f"Optimization: {check_name}", True, message)
            else:
                self.log_test_result(f"Optimization: {check_name}", False, message)
        
        duration = time.time() - start_time
        success = all(is_valid for _, is_valid, _ in optimization_checks)
        self.log_test_result("Performance Optimization", success, f"Performance optimization checks complete", duration)
        return success
    
    def validate_config_value(self, key: str, value: str, config: Dict[str, Any]) -> ConfigValidation:
        """Validate a configuration value against its specification"""
        try:
            expected_type = config['type']
            
            # Type conversion and validation
            if expected_type == int:
                converted_value = int(value)
                actual_type = 'int'
            elif expected_type == float:
                converted_value = float(value)
                actual_type = 'float'
            elif expected_type == bool:
                converted_value = value.lower() in ('true', '1', 'yes', 'on')
                actual_type = 'bool'
            else:
                converted_value = str(value)
                actual_type = 'str'
            
            # Range validation
            is_valid = True
            validation_message = f"Valid {config['description']}: {converted_value}"
            
            if 'min' in config and converted_value < config['min']:
                is_valid = False
                validation_message = f"Value {converted_value} below minimum {config['min']}"
            
            if 'max' in config and converted_value > config['max']:
                is_valid = False
                validation_message = f"Value {converted_value} above maximum {config['max']}"
            
            # Pattern validation
            if 'pattern' in config:
                if not re.match(config['pattern'], str(converted_value)):
                    is_valid = False
                    validation_message = f"Value {converted_value} doesn't match pattern {config['pattern']}"
            
            return ConfigValidation(
                key=key,
                value=converted_value,
                is_valid=is_valid,
                expected_type=expected_type.__name__,
                actual_type=actual_type,
                validation_message=validation_message,
                category=config.get('category', 'general')
            )
            
        except (ValueError, TypeError) as e:
            return ConfigValidation(
                key=key,
                value=value,
                is_valid=False,
                expected_type=config['type'].__name__,
                actual_type=type(value).__name__,
                validation_message=f"Type conversion failed: {str(e)}",
                category=config.get('category', 'general')
            )
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        logger.info("Generating Optimization Report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'file_info': {
                'filename': self.env_file,
                'size_bytes': os.path.getsize(self.env_file),
                'total_variables': len(self.config_data)
            },
            'test_summary': {
                'total_tests': self.test_count,
                'passed': self.passed_count,
                'failed': self.failed_count,
                'success_rate': (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
            },
            'validation_results': [vars(v) for v in self.validation_results],
            'optimization_suggestions': self.optimization_suggestions,
            'detailed_results': self.test_results
        }
        
        # Add optimization suggestions
        suggestions = []
        
        # Check for performance optimizations
        if 'BATCH_SIZE' in self.config_data:
            batch_size = int(self.config_data['BATCH_SIZE'])
            if batch_size < 3:
                suggestions.append("Consider increasing BATCH_SIZE to 3-5 for better performance")
            elif batch_size > 8:
                suggestions.append("Consider reducing BATCH_SIZE to 5-8 to avoid memory issues")
        
        if 'API_TIMEOUT' in self.config_data:
            timeout = int(self.config_data['API_TIMEOUT'])
            if timeout < 45:
                suggestions.append("Consider increasing API_TIMEOUT to 60-90 seconds for stability")
            elif timeout > 120:
                suggestions.append("Consider reducing API_TIMEOUT to 60-90 seconds for faster failure detection")
        
        if 'INFERENCE_STEPS' in self.config_data:
            steps = int(self.config_data['INFERENCE_STEPS'])
            if steps < 4:
                suggestions.append("Consider increasing INFERENCE_STEPS to 4-8 for better image quality")
            elif steps > 20:
                suggestions.append("Consider reducing INFERENCE_STEPS to 8-15 for faster generation")
        
        # Check for missing optimizations
        if 'CPU_IMAGE_GENERATION_ENABLED' not in self.config_data:
            suggestions.append("Add CPU_IMAGE_GENERATION_ENABLED for offline image generation")
        
        if 'GPU_IMAGE_GENERATION_ENABLED' not in self.config_data:
            suggestions.append("Add GPU_IMAGE_GENERATION_ENABLED for hardware acceleration")
        
        if 'PARALLEL_PROCESSING' not in self.config_data:
            suggestions.append("Add PARALLEL_PROCESSING setting for concurrent operations")
        
        report['optimization_suggestions'] = suggestions
        
        return report
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive environment tests"""
        logger.info("Starting ASK Environment Testing Suite...")
        logger.info("=" * 80)
        
        test_functions = [
            self.test_file_structure,
            self.test_required_variables,
            self.test_api_configuration,
            self.test_model_configuration,
            self.test_text_generation_config,
            self.test_image_generation_config,
            self.test_mode_configuration,
            self.test_optimization_settings,
            self.test_duplicate_variables,
            self.test_value_consistency,
            self.test_performance_optimization
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_func.__name__} crashed: {str(e)}")
                self.log_test_result(test_func.__name__, False, f"Test crashed: {str(e)}")
        
        # Generate optimization report
        report = self.generate_optimization_report()
        
        # Log summary
        total_time = time.time() - self.start_time
        success_rate = (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
        
        logger.info("=" * 80)
        logger.info("ASK ENVIRONMENT TESTING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {self.test_count}")
        logger.info(f"Passed: {self.passed_count}")
        logger.info(f"Failed: {self.failed_count}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Total Time: {total_time:.2f}s")
        
        if self.failed_count == 0:
            logger.info("ALL ASK ENVIRONMENT TESTS PASSED!")
        else:
            logger.warning(f"{self.failed_count} ASK environment tests failed")
        
        # Save results to file
        with open('ask_env_test_results.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("ASK environment test results saved to ask_env_test_results.json")
        
        return report

def main():
    """Main testing function"""
    tester = ASKEnvTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['test_summary']['failed'] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
