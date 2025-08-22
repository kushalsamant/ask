#!/usr/bin/env python3
"""
API Client Module
Consolidated API client for all Together.ai API calls with unified retry logic and error handling
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv('ask.env')

# Setup logging
log = logging.getLogger(__name__)

class APIClient:
    """Unified API client for Together.ai services"""
    
    def __init__(self):
        """Initialize API client with configuration"""
        self.api_key = os.getenv('TOGETHER_API_KEY')
        self.api_base = os.getenv('TOGETHER_API_BASE', 'https://api.together.xyz/v1')
        self.timeout = int(os.getenv('API_TIMEOUT', '60'))
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))
        self.max_retries = int(os.getenv('API_MAX_RETRIES', '5'))
        self.retry_delay_multiplier = int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))
        self.retryable_codes = [int(x) for x in os.getenv('RETRYABLE_STATUS_CODES', '408,429,500,502,503,504').split(',')]
        
        # Fixed retry delays: 30, 60, 90, 120, 150 seconds
        self.retry_delays = [30, 60, 90, 120, 150]
        
        # Default headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any], operation_name: str = "API call") -> Optional[Dict[str, Any]]:
        """
        Make API request with unified retry logic and error handling
        
        Args:
            endpoint (str): API endpoint (e.g., '/chat/completions')
            payload (dict): Request payload
            operation_name (str): Name of operation for logging
        
        Returns:
            dict: API response data or None if failed
        """
        url = f"{self.api_base}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                log.info(f"Making {operation_name} (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    log.info(f"✅ {operation_name} successful")
                    return data
                
                elif response.status_code in self.retryable_codes:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delays[attempt]  # Fixed delays: 30, 60, 90, 120, 150s
                        log.warning(f"Retryable error {response.status_code}, retrying in {wait_time} seconds (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        log.error(f"Retryable error {response.status_code} after {self.max_retries} attempts")
                        return None
                
                else:
                    error_text = response.text[:200] if response.text else "No response text"
                    log.error(f"API error {response.status_code}: {error_text}")
                    return None
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delays[attempt]  # Fixed delays: 30, 60, 90, 120, 150s
                    log.warning(f"Timeout, retrying in {wait_time} seconds (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    log.error(f"Timeout after {self.max_retries} attempts")
                    return None
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delays[attempt]  # Fixed delays: 30, 60, 90, 120, 150s
                    log.warning(f"Network error, retrying in {wait_time} seconds (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    log.error(f"Network error after {self.max_retries} attempts: {e}")
                    return None
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delays[attempt]  # Fixed delays: 30, 60, 90, 120, 150s
                    log.warning(f"Unexpected error, retrying in {wait_time} seconds (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    log.error(f"Unexpected error after {self.max_retries} attempts: {e}")
                    return None
        
        log.error(f"Failed {operation_name} after {self.max_retries} attempts")
        return None
    
    def call_text_api(self, prompt: str, system_prompt: Optional[str] = None, 
                     model: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Make text generation API call
        
        Args:
            prompt (str): User prompt
            system_prompt (str): System prompt (optional)
            model (str): Model to use (optional, uses default if not provided)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            str: Generated text or None if failed
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
        
        # Override with provided kwargs
        default_params.update(kwargs)
        
        payload = {
            "model": model,
            "messages": messages,
            **default_params
        }
        
        data = self._make_request('/chat/completions', payload, "text generation API call")
        
        if data and 'choices' in data and data['choices']:
            raw_text = data['choices'][0]['message']['content'].strip()
            # Clean up the text - remove instruction tokens
            raw_text = raw_text.replace('[/INST]', '').replace('[INST]', '').strip()
            return raw_text
        
        log.error("Invalid API response format for text generation")
        return None
    
    def call_vision_api(self, prompt: str, system_prompt: Optional[str] = None, 
                       model: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Make vision API call (same as text but with vision parameters)
        
        Args:
            prompt (str): User prompt
            system_prompt (str): System prompt (optional)
            model (str): Model to use (optional, uses default if not provided)
            **kwargs: Additional parameters
        
        Returns:
            str: Generated text or None if failed
        """
        if model is None:
            model = os.getenv('VISION_MODEL', 'meta-llama/Llama-Vision-Free')
        
        # Use vision-specific parameters
        vision_params = {
            "temperature": float(os.getenv('VISION_TEMPERATURE', '0.7')),
            "max_tokens": int(os.getenv('VISION_MAX_TOKENS', '100')),
            "top_p": float(os.getenv('VISION_TOP_P', '0.9')),
            "frequency_penalty": float(os.getenv('VISION_FREQUENCY_PENALTY', '0.3')),
            "presence_penalty": float(os.getenv('VISION_PRESENCE_PENALTY', '0.3'))
        }
        vision_params.update(kwargs)
        
        return self.call_text_api(prompt, system_prompt, model, **vision_params)
    
    def call_image_api(self, prompt: str, negative_prompt: str = "", 
                      width: int = None, height: int = None, **kwargs) -> Optional[str]:
        """
        Make image generation API call
        
        Args:
            prompt (str): Image generation prompt
            negative_prompt (str): Negative prompt
            width (int): Image width
            height (int): Image height
            **kwargs: Additional parameters
        
        Returns:
            str: Image URL or None if failed
        """
        model = os.getenv('IMAGE_MODEL', 'black-forest-labs/FLUX.1-schnell-Free')
        
        if width is None:
            width = int(os.getenv('IMAGE_WIDTH', '1072'))
        if height is None:
            height = int(os.getenv('IMAGE_HEIGHT', '1792'))
        
        # Default image parameters
        default_params = {
            "negative_prompt": negative_prompt or "low quality, blurry, distorted, deformed, disfigured, bad proportions, watermark, signature, text",
            "steps": int(os.getenv('INFERENCE_STEPS', '20')),
            "guidance_scale": float(os.getenv('GUIDANCE_SCALE', '7.5')),
            "seed": int(time.time() * 1000) % 999999999  # Use timestamp-based seed
        }
        default_params.update(kwargs)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "width": width,
            "height": height,
            **default_params
        }
        
        data = self._make_request('/images/generations', payload, "image generation API call")
        
        if data and 'data' in data and data['data']:
            return data['data'][0]['url']
        
        log.error("Invalid API response format for image generation")
        return None
    
    def download_image(self, image_url: str, save_path: str, timeout: int = None) -> bool:
        """
        Download image from URL and save to file
        
        Args:
            image_url (str): URL of image to download
            save_path (str): Path to save image
            timeout (int): Download timeout
        
        Returns:
            bool: True if successful, False otherwise
        """
        if timeout is None:
            timeout = int(os.getenv('DOWNLOAD_TIMEOUT', '30'))
        
        try:
            log.info(f"Downloading image from {image_url}")
            response = requests.get(image_url, timeout=timeout)
            response.raise_for_status()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            log.info(f"✅ Image downloaded successfully: {save_path}")
            return True
            
        except Exception as e:
            log.error(f"Error downloading image: {e}")
            return False

# Global API client instance
api_client = APIClient()

# Convenience functions for backward compatibility
def call_together_api(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Optional[str]:
    """Backward compatibility function for text API calls"""
    return api_client.call_text_api(prompt, system_prompt, **kwargs)

def call_together_api_for_answer(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Optional[str]:
    """Backward compatibility function for vision API calls"""
    return api_client.call_vision_api(prompt, system_prompt, **kwargs)
