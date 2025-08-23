#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized API Client Module for ASK Research Tool
Enhanced with heavy testing, performance optimization, and advanced features
"""

import os
import time
import json
import logging
import requests
import asyncio
import aiohttp
import threading
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps, lru_cache
from dotenv import load_dotenv
import hashlib
import pickle
from pathlib import Path

# Load environment variables
load_dotenv('ask.env')

# Setup logging
log = logging.getLogger(__name__)

@dataclass
class APIMetrics:
    """API performance metrics tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    rate_limit_hits: int = 0
    timeout_hits: int = 0
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    def update_metrics(self, success: bool, response_time: float, error_type: str = None):
        """Update metrics with new request data"""
        self.total_requests += 1
        self.total_response_time += response_time
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        self.average_response_time = self.total_response_time / self.total_requests
        self.last_request_time = datetime.now()

class APICache:
    """Intelligent API response caching system"""
    
    def __init__(self, cache_dir: str = ".api_cache", max_size: int = 1000, ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.cache_index = {}
        self._load_cache_index()
    
    def _get_cache_key(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """Generate cache key from endpoint and payload"""
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.md5(f"{endpoint}:{payload_str}".encode()).hexdigest()
    
    def _load_cache_index(self):
        """Load cache index from disk"""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self.cache_index = json.load(f)
            except Exception as e:
                log.warning(f"Failed to load cache index: {e}")
                self.cache_index = {}
    
    def _save_cache_index(self):
        """Save cache index to disk"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            with open(index_file, 'w') as f:
                json.dump(self.cache_index, f)
        except Exception as e:
            log.warning(f"Failed to save cache index: {e}")
    
    def get(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        cache_key = self._get_cache_key(endpoint, payload)
        
        if cache_key not in self.cache_index:
            return None
        
        cache_info = self.cache_index[cache_key]
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Check if cache is expired
        cache_time = datetime.fromisoformat(cache_info['timestamp'])
        if datetime.now() - cache_time > timedelta(hours=self.ttl_hours):
            self._remove_cache_entry(cache_key)
            return None
        
        # Load cached response
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            log.warning(f"Failed to load cached response: {e}")
            self._remove_cache_entry(cache_key)
            return None
    
    def set(self, endpoint: str, payload: Dict[str, Any], response: Dict[str, Any]):
        """Cache API response"""
        cache_key = self._get_cache_key(endpoint, payload)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Implement LRU eviction if cache is full
        if len(self.cache_index) >= self.max_size:
            self._evict_oldest()
        
        try:
            # Save response to disk
            with open(cache_file, 'wb') as f:
                pickle.dump(response, f)
            
            # Update cache index
            self.cache_index[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'file': str(cache_file)
            }
            self._save_cache_index()
            
        except Exception as e:
            log.warning(f"Failed to cache response: {e}")
    
    def _remove_cache_entry(self, cache_key: str):
        """Remove cache entry"""
        if cache_key in self.cache_index:
            cache_file = Path(self.cache_index[cache_key]['file'])
            if cache_file.exists():
                cache_file.unlink()
            del self.cache_index[cache_key]
            self._save_cache_index()
    
    def _evict_oldest(self):
        """Evict oldest cache entry"""
        if not self.cache_index:
            return
        
        oldest_key = min(self.cache_index.keys(), 
                        key=lambda k: self.cache_index[k]['timestamp'])
        self._remove_cache_entry(oldest_key)
    
    def clear(self):
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        self.cache_index.clear()
        self._save_cache_index()

class RateLimiter:
    """Advanced rate limiting with token bucket algorithm"""
    
    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        self.lock = threading.Lock()
    
    def acquire(self) -> bool:
        """Acquire a token for API request"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            
            self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
            self.last_refill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
    
    def wait_for_token(self, max_wait: float = 60.0) -> bool:
        """Wait for a token to become available"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.acquire():
                return True
            time.sleep(0.1)
        return False

class APIClient:
    """Enhanced API client with advanced features for heavy testing and optimization"""
    
    def __init__(self):
        """Initialize optimized API client"""
        # Configuration
        self.api_key = os.getenv('TOGETHER_API_KEY')
        self.api_base = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1')
        self.timeout = int(os.getenv('API_TIMEOUT', '60'))
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))
        self.max_retries = int(os.getenv('API_MAX_RETRIES', '5'))
        self.retry_delay_multiplier = int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))
        self.retryable_codes = [int(x) for x in os.getenv('RETRYABLE_STATUS_CODES', '408,429,500,502,503,504').split(',')]
        
        # Enhanced retry delays with exponential backoff
        self.retry_delays = [30, 60, 90, 120, 150]
        
        # Headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ASK-Research-Tool/1.0"
        }
        
        # Performance tracking
        self.metrics = APIMetrics()
        self.cache = APICache()
        self.rate_limiter = RateLimiter(
            requests_per_minute=int(os.getenv('API_RATE_LIMIT', '60')),
            burst_size=int(os.getenv('API_BURST_SIZE', '10'))
        )
        
        # Connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Circuit breaker
        self.circuit_breaker = {
            'failures': 0,
            'last_failure': None,
            'threshold': int(os.getenv('CIRCUIT_BREAKER_THRESHOLD', '5')),
            'timeout': int(os.getenv('CIRCUIT_BREAKER_TIMEOUT', '300')),
            'state': 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        }
    
    def _circuit_breaker_check(self) -> bool:
        """Check if circuit breaker should allow request"""
        now = time.time()
        
        if self.circuit_breaker['state'] == 'OPEN':
            if (now - self.circuit_breaker['last_failure']) > self.circuit_breaker['timeout']:
                self.circuit_breaker['state'] = 'HALF_OPEN'
                return True
            return False
        
        return True
    
    def _circuit_breaker_success(self):
        """Record successful request"""
        if self.circuit_breaker['state'] == 'HALF_OPEN':
            self.circuit_breaker['state'] = 'CLOSED'
        self.circuit_breaker['failures'] = 0
    
    def _circuit_breaker_failure(self):
        """Record failed request"""
        self.circuit_breaker['failures'] += 1
        self.circuit_breaker['last_failure'] = time.time()
        
        if self.circuit_breaker['failures'] >= self.circuit_breaker['threshold']:
            self.circuit_breaker['state'] = 'OPEN'
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any], 
                     operation_name: str = "API call", use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Enhanced API request with caching, rate limiting, and circuit breaker
        """
        # Check circuit breaker
        if not self._circuit_breaker_check():
            log.warning(f"Circuit breaker OPEN, skipping {operation_name}")
            return None
        
        # Check cache first
        if use_cache:
            cached_response = self.cache.get(endpoint, payload)
            if cached_response:
                log.info(f"✅ {operation_name} served from cache")
                self.metrics.update_metrics(True, 0.0)
                return cached_response
        
        # Rate limiting
        if not self.rate_limiter.wait_for_token():
            log.error(f"Rate limit exceeded for {operation_name}")
            return None
        
        url = f"{self.api_base}{endpoint}"
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                log.info(f"Making {operation_name} (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.session.post(url, json=payload, timeout=self.timeout)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Cache successful response
                    if use_cache:
                        self.cache.set(endpoint, payload, data)
                    
                    log.info(f"✅ {operation_name} successful ({response_time:.2f}s)")
                    self.metrics.update_metrics(True, response_time)
                    self._circuit_breaker_success()
                    return data
                
                elif response.status_code in self.retryable_codes:
                    self.metrics.rate_limit_hits += 1
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delays[attempt]
                        log.warning(f"Retryable error {response.status_code}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        log.error(f"Retryable error {response.status_code} after {self.max_retries} attempts")
                        self.metrics.update_metrics(False, response_time, f"HTTP_{response.status_code}")
                        self._circuit_breaker_failure()
                        return None
                
                else:
                    error_text = response.text[:200] if response.text else "No response text"
                    log.error(f"API error {response.status_code}: {error_text}")
                    self.metrics.update_metrics(False, response_time, f"HTTP_{response.status_code}")
                    self._circuit_breaker_failure()
                    return None
                    
            except requests.exceptions.Timeout:
                self.metrics.timeout_hits += 1
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delays[attempt]
                    log.warning(f"Timeout, retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    log.error(f"Timeout after {self.max_retries} attempts")
                    self.metrics.update_metrics(False, time.time() - start_time, "TIMEOUT")
                    self._circuit_breaker_failure()
                    return None
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delays[attempt]
                    log.warning(f"Network error, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    log.error(f"Network error after {self.max_retries} attempts: {e}")
                    self.metrics.update_metrics(False, time.time() - start_time, "NETWORK_ERROR")
                    self._circuit_breaker_failure()
                    return None
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delays[attempt]
                    log.warning(f"Unexpected error, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    log.error(f"Unexpected error after {self.max_retries} attempts: {e}")
                    self.metrics.update_metrics(False, time.time() - start_time, "UNEXPECTED_ERROR")
                    self._circuit_breaker_failure()
                    return None
        
        log.error(f"Failed {operation_name} after {self.max_retries} attempts")
        return None
    
    def call_text_api(self, prompt: str, system_prompt: Optional[str] = None, 
                     model: Optional[str] = None, use_cache: bool = True, **kwargs) -> Optional[str]:
        """
        Enhanced text generation API call with caching
        """
        if model is None:
            model = os.getenv('TEXT_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Default parameters
        default_params = {
            "temperature": float(os.getenv('TEXT_TEMPERATURE', '0.72')),
            "max_tokens": int(os.getenv('TEXT_MAX_TOKENS', '150')),
            "top_p": float(os.getenv('TEXT_TOP_P', '0.85')),
            "frequency_penalty": float(os.getenv('TEXT_FREQUENCY_PENALTY', '0.3')),
            "presence_penalty": float(os.getenv('TEXT_PRESENCE_PENALTY', '0.6'))
        }
        default_params.update(kwargs)
        
        payload = {
            "model": model,
            "messages": messages,
            **default_params
        }
        
        data = self._make_request('/chat/completions', payload, "text generation API call", use_cache)
        
        if data and 'choices' in data and data['choices']:
            raw_text = data['choices'][0]['message']['content'].strip()
            raw_text = raw_text.replace('[/INST]', '').replace('[INST]', '').strip()
            return raw_text
        
        log.error("Invalid API response format for text generation")
        return None
    
    def call_vision_api(self, prompt: str, system_prompt: Optional[str] = None, 
                       model: Optional[str] = None, use_cache: bool = True, **kwargs) -> Optional[str]:
        """
        Enhanced vision API call
        """
        if model is None:
            model = os.getenv('VISION_MODEL', 'meta-llama/Llama-Vision-Free')
        
        vision_params = {
            "temperature": float(os.getenv('VISION_TEMPERATURE', '0.7')),
            "max_tokens": int(os.getenv('VISION_MAX_TOKENS', '100')),
            "top_p": float(os.getenv('VISION_TOP_P', '0.9')),
            "frequency_penalty": float(os.getenv('VISION_FREQUENCY_PENALTY', '0.3')),
            "presence_penalty": float(os.getenv('VISION_PRESENCE_PENALTY', '0.3'))
        }
        vision_params.update(kwargs)
        
        return self.call_text_api(prompt, system_prompt, model, use_cache, **vision_params)
    
    def call_image_api(self, prompt: str, negative_prompt: str = "", 
                      width: int = None, height: int = None, use_cache: bool = False, **kwargs) -> Optional[str]:
        """
        Enhanced image generation API call (caching disabled by default for images)
        """
        model = os.getenv('IMAGE_MODEL', 'black-forest-labs/FLUX.1-schnell-Free')
        
        if width is None:
            width = int(os.getenv('IMAGE_WIDTH', '1072'))
        if height is None:
            height = int(os.getenv('IMAGE_HEIGHT', '1792'))
        
        default_params = {
            "negative_prompt": negative_prompt or "low quality, blurry, distorted, deformed, disfigured, bad proportions, watermark, signature, text",
            "steps": int(os.getenv('INFERENCE_STEPS', '20')),
            "guidance_scale": float(os.getenv('GUIDANCE_SCALE', '7.5')),
            "seed": int(time.time() * 1000) % 999999999
        }
        default_params.update(kwargs)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "width": width,
            "height": height,
            **default_params
        }
        
        data = self._make_request('/images/generations', payload, "image generation API call", use_cache)
        
        if data and 'data' in data and data['data']:
            return data['data'][0]['url']
        
        log.error("Invalid API response format for image generation")
        return None
    
    def download_image(self, image_url: str, save_path: str, timeout: int = None) -> bool:
        """
        Enhanced image download with retry logic
        """
        if timeout is None:
            timeout = int(os.getenv('DOWNLOAD_TIMEOUT', '30'))
        
        for attempt in range(3):  # 3 download attempts
            try:
                log.info(f"Downloading image from {image_url} (attempt {attempt + 1}/3)")
                response = self.session.get(image_url, timeout=timeout)
                response.raise_for_status()
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                log.info(f"✅ Image downloaded successfully: {save_path}")
                return True
                
            except Exception as e:
                log.warning(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    log.error(f"Failed to download image after 3 attempts: {e}")
                    return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive API metrics"""
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'success_rate': (self.metrics.successful_requests / self.metrics.total_requests * 100) if self.metrics.total_requests > 0 else 0,
            'average_response_time': self.metrics.average_response_time,
            'rate_limit_hits': self.metrics.rate_limit_hits,
            'timeout_hits': self.metrics.timeout_hits,
            'error_counts': self.metrics.error_counts,
            'circuit_breaker_state': self.circuit_breaker['state'],
            'cache_stats': {
                'cache_size': len(self.cache.cache_index),
                'cache_dir': str(self.cache.cache_dir)
            }
        }
    
    def clear_cache(self):
        """Clear API cache"""
        self.cache.clear()
        log.info("API cache cleared")
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = APIMetrics()
        log.info("API metrics reset")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform API health check"""
        try:
            response = self.session.get(f"{self.api_base}/models", timeout=10)
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'circuit_breaker_state': self.circuit_breaker['state']
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'circuit_breaker_state': self.circuit_breaker['state']
            }

# Global API client instance
api_client = APIClient()

# Convenience functions for backward compatibility
def call_together_api(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Optional[str]:
    """Backward compatibility function for text API calls"""
    return api_client.call_text_api(prompt, system_prompt, **kwargs)

def call_together_api_for_answer(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Optional[str]:
    """Backward compatibility function for vision API calls"""
    return api_client.call_vision_api(prompt, system_prompt, **kwargs)

def make_api_request(api_key: str, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    # Create temporary client with provided API key
    temp_client = APIClient()
    temp_client.api_key = api_key
    temp_client.headers["Authorization"] = f"Bearer {api_key}"
    return temp_client._make_request(endpoint, payload, "legacy API request", use_cache=False)
