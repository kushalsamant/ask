import os
import sys
import subprocess
import logging
import time
import random
import json
import requests
import base64
import argparse
import asyncio
import aiohttp
import gzip
import hashlib
import pickle
import gc
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
import fitz

#!/usr/bin/env python3
"""
Daily Zine Generator - Streamlined Flow
1. Scrape web for architectural content
2. Use web content to make 1 theme daily
3. Use theme to create 50 prompts
4. Use prompts to make 50 full-bleed images in ONE style only
5. Use prompts to make captions (6 lines, 6 words each)
6. Place captions with readability improvements
7. Stitch into ONE PDF
"""

# ===  Load environment variables ===
load_dotenv('ask.env')

def get_env(var, default=None, required=False):
    value = os.getenv(var, default)
    if required and not value:
        print(f"Required environment variable '{var}' is missing. Exiting.")
        sys.exit(1)
    return value

# ===  Preemptive .env Validation ===
REQUIRED_VARS = ['TOGETHER_API_KEY', 'TEXT_PROVIDER', 'IMAGE_PROVIDER', 'MANUAL_SOURCES_FILE']
for var in REQUIRED_VARS:
    get_env(var, required=True)

# ===  Setup real-time logging ===
LOG_DIR = get_env('LOG_DIR', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"daily_zine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
log_level = get_env("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger()
if log_level not in ['WARNING', 'ERROR']:
    log.debug(f" Logging level set to: {log_level}")

# ===  Auto-install missing dependencies ===
REQUIRED_LIBS = ['python-dotenv', 'reportlab', 'Pillow', 'beautifulsoup4', 'tqdm', 'aiohttp']

def install_missing_libs():
    missing_libs = []
    for lib in REQUIRED_LIBS:
        try:
            if lib == 'python-dotenv':
                __import__('dotenv')
            elif lib == 'Pillow':
                __import__('PIL')
            elif lib == 'beautifulsoup4':
                __import__('bs4')
            elif lib == 'tqdm':
                __import__('tqdm')
            elif lib == 'aiohttp':
                __import__('aiohttp')
            else:
                __import__(lib)
        except ImportError:
            missing_libs.append(lib)
    
    if missing_libs:
        log.info(f"Missing dependencies: {', '.join(missing_libs)}")
        
        # Safety check: Only install if we have proper permissions and environment
        if not _can_safely_install_packages():
            log.warning(" Package installation disabled due to environment restrictions")
            log.info(" Please install missing packages manually:")
            for lib in missing_libs:
                log.info(f"   pip install {lib}")
            raise ImportError(f"Missing required packages: {', '.join(missing_libs)}. Install manually or check environment permissions.")
        
        log.info(" Installing missing dependencies...")
        for lib in missing_libs:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                log.info(f" Installed: {lib}")
            except subprocess.CalledProcessError as e:
                log.error(f" Failed to install {lib}: {e}")
                raise ImportError(f"Failed to install {lib}. Please install manually: pip install {lib}")
    else:
        log.info(" All dependencies are already installed")

def _can_safely_install_packages():
    """Check if it's safe to install packages in the current environment"""
    
    # Check if we're in a virtual environment (safer)
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    # Check if we're in a container or restricted environment
    in_container = os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup')
    
    # Check if we have write permissions to site-packages
    try:
        site_packages = site.getsitepackages()[0] if site.getsitepackages() else None
        if site_packages:
            can_write = os.access(site_packages, os.W_OK)
        else:
            can_write = False
    except (IndexError, OSError):
        can_write = False
    
    # Check if we're running as root (dangerous)
    is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    
    # Check environment variables that might indicate restricted environment
    restricted_env_vars = [
        'VIRTUAL_ENV', 'CONDA_DEFAULT_ENV', 'PIP_USER', 'PIP_NO_USER',
        'PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'
    ]
    
    has_restricted_env = any(os.getenv(var) for var in restricted_env_vars)
    
    # Safety rules:
    # 1. Don't install if we're root (unless in a container)
    # 2. Don't install if we can't write to site-packages
    # 3. Don't install if we're in a restricted environment without explicit permission
    # 4. Allow installation in virtual environments or containers with proper permissions
    
    if is_root and not in_container:
        log.warning(" Running as root - package installation disabled for safety")
        return False
    
    if not can_write and not in_venv:
        log.warning(" No write permissions to site-packages - package installation disabled")
        return False
    
    # Check for explicit override FIRST (highest priority)
    if os.getenv('ALLOW_PACKAGE_INSTALLATION', 'false').lower() == 'true':
        log.warning(" Package installation explicitly allowed via ALLOW_PACKAGE_INSTALLATION=true")
        return True
    
    # Allow installation if we're in a virtual environment
    if in_venv:
        log.info(" Virtual environment detected - package installation allowed")
        return True
    
    # Allow installation in containers with proper permissions
    if in_container and can_write:
        log.info(" Container environment with write permissions - package installation allowed")
        return True
    
    # Block restricted environments
    if has_restricted_env and not in_venv:
        log.warning(" Restricted environment detected - package installation disabled")
        return False
    
    # Default: be conservative
    log.warning(" Environment safety unclear - package installation disabled")
    return False

# ===  Consolidated Configuration ===
class Config:
    """Centralized configuration management"""
    
    # API Configuration
    API = {
        "together_key": get_env("TOGETHER_API_KEY"),
        "groq_key": get_env("GROQ_API_KEY"),
        "replicate_key": get_env("REPLICATE_API_KEY"),
        "openai_key": get_env("OPENAI_API_KEY"),
        "base_url": get_env("TOGETHER_BASE_URL", "https://api.together.xyz/v1")
    }
    
    # Provider Configuration
    PROVIDERS = {
        "text": get_env("TEXT_PROVIDER", "together"),
        "image": get_env("IMAGE_PROVIDER", "together"),
        "supported_text": ["together", "groq", "openai", "replicate"],
        "supported_image": ["together", "replicate", "openai"]
    }
    
    # Image Generation
    IMAGE = {
        "width": int(get_env("IMAGE_WIDTH", "1024")),
        "height": int(get_env("IMAGE_HEIGHT", "1024")),
        "quality": int(get_env("IMAGE_QUALITY", "85")),
        "max_concurrent": int(get_env("MAX_CONCURRENT_IMAGES", "1"))
    }
    
    # Caption Generation
    CAPTION = {
        "max_concurrent": int(get_env("MAX_CONCURRENT_CAPTIONS", "1")),
        "line_count": int(get_env("CAPTION_LINE_COUNT", "6")),
        "words_per_line": int(get_env("CAPTION_WORDS_PER_LINE", "6"))
    }
    # Content Sources
    SOURCES = {
        "manual_file": get_env("MANUAL_SOURCES_FILE", "manual_sources.txt"),
        "web_scraper_delay": float(get_env("WEB_SCRAPER_DELAY", "1.0")),
        "max_sources": int(get_env("WEB_SCRAPER_MAX_SOURCES", "50")),
        "discovery_enabled": get_env("DAILY_DISCOVERY_ENABLED", "true").lower() == "true",
        "discoverer_delay": float(get_env("DISCOVERER_DELAY", "2.0"))
    }
    # Cache Configuration
    CACHE = {
        "dir": get_env("CACHE_DIR", "cache"),
        "max_age_hours": int(get_env("CACHE_MAX_AGE_HOURS", "24")),
        "optimization_enabled": get_env("CACHE_OPTIMIZATION_ENABLED", "true").lower() == "true"
    }
    # PDF Configuration
    PDF = {
        "output_dir": get_env("PDF_OUTPUT_DIR", "daily_pdfs"),
        "page_size": get_env("PDF_PAGE_SIZE", "A4"),
        "dpi": int(get_env("PDF_DPI", "300"))
    }
    # Instagram Configuration
    INSTAGRAM = {
        "output_dir": get_env("INSTAGRAM_OUTPUT_DIR", "instagram"),
        "dpi": int(get_env("INSTAGRAM_DPI", "300"))
    }
    # Mode Configuration (Sequential Only)
    MODES = {
        "ultra_concurrent_images": int(get_env("ULTRA_MODE_CONCURRENT_IMAGES", "1")),
        "ultra_concurrent_captions": int(get_env("ULTRA_MODE_CONCURRENT_CAPTIONS", "1"))
    }
    # Rate Limiting Configuration
    LIMITS = {
        "max_concurrent_images": int(get_env("MAX_CONCURRENT_IMAGES", "1")),
        "max_concurrent_captions": int(get_env("MAX_CONCURRENT_CAPTIONS", "1")),
        "rate_limit_delay": float(get_env("RATE_LIMIT_DELAY", "20.0")),  # Single delay for all operations
        "api_timeout": int(get_env("API_TIMEOUT", "60")),
        "max_retries": int(get_env("MAX_RETRIES", "3"))
    }
    # Logging Configuration
    LOGGING = {
        "level": get_env("LOG_LEVEL", "INFO").upper(),
        "dir": get_env("LOG_DIR", "logs"),
        "file_rotation": get_env("LOG_FILE_ROTATION", "true").lower() == "true",
        "max_file_size_mb": int(get_env("LOG_MAX_FILE_SIZE_MB", "10")),
        "backup_count": int(get_env("LOG_BACKUP_COUNT", "5"))
    }

# Cache system for 100x speed improvements
CACHE_DIR = Path(get_env('CACHE_DIR', 'cache'))
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_path(key):
    """Generate cache file path for a given key"""
    hash_key = hashlib.md5(key.encode()).hexdigest()
    return CACHE_DIR / f"{hash_key}.pkl"

def save_to_cache(key, data):
    """Save data to cache with gzip compression for huge disk savings"""
    if not CACHE_ENABLED:
        return
    try:
        cache_path = get_cache_path(key)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        
        # Use gzip compression for significant disk space savings
        with gzip.open(cache_path, 'wb', compresslevel=6) as f:
            pickle.dump(data, f)
        
        # Log compression stats
        original_size = len(pickle.dumps(data))
        compressed_size = os.path.getsize(cache_path)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        log.debug(f" Cached data for key: {key} (compressed {compression_ratio:.1f}%)")
    except Exception as e:
        log.debug(f"Cache save failed: {e}")

def load_from_cache(key, max_age_hours=None):
    """Load data from cache if available and fresh (supports gzip compression)"""
    if not CACHE_ENABLED:
        return None
    if max_age_hours is None:
        max_age_hours = int(get_env('CACHE_MAX_AGE_HOURS', '24'))
    try:
        cache_path = get_cache_path(key)
        if cache_path.exists():
            # Check if cache is fresh
            if time.time() - cache_path.stat().st_mtime < max_age_hours * 3600:
                # Try gzip first, fallback to regular pickle
                try:
                    with gzip.open(cache_path, 'rb') as f:
                        return pickle.load(f)
                except (OSError, gzip.BadGzipFile):
                    # Fallback to regular pickle for backward compatibility
                    with open(cache_path, 'rb') as f:
                        return pickle.load(f)
    except Exception as e:
        log.debug(f"Cache load failed: {e}")
    return None

def optimize_cache_memory():
    """Optimize cache memory by cleaning old files and compressing data"""
    if not CACHE_ENABLED:
        return
    
    log.info("🧹 Starting weekly cache optimization...")
    
    # Get cache optimization settings
    max_cache_age_days = int(get_env('CACHE_MAX_AGE_DAYS', '7'))
    max_cache_size_mb = int(get_env('MAX_CACHE_SIZE_MB', '500'))
    compression_enabled = get_env('CACHE_COMPRESSION_ENABLED', 'true').lower() == 'true'
    
    try:
        # Calculate cutoff time for old files
        cutoff_time = time.time() - (max_cache_age_days * 24 * 3600)
        
        # Get all cache files (both .pkl and .pkl.gz for backward compatibility)
        cache_files = list(CACHE_DIR.glob("*.pkl")) + list(CACHE_DIR.glob("*.pkl.gz"))
        total_files = len(cache_files)
        deleted_files = 0
        total_size_before = 0
        total_size_after = 0
        
        # Calculate total size before cleanup
        for cache_file in cache_files:
            total_size_before += cache_file.stat().st_size
        
        # Remove old cache files
        for cache_file in cache_files:
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age > cutoff_time:
                try:
                    cache_file.unlink()
                    deleted_files += 1
                    log.debug(f" Deleted old cache file: {cache_file.name}")
                except Exception as e:
                    log.warning(f"Failed to delete cache file {cache_file.name}: {e}")
        
        # Check cache size and remove oldest files if needed
        remaining_files = list(CACHE_DIR.glob("*.pkl")) + list(CACHE_DIR.glob("*.pkl.gz"))
        if remaining_files:
            # Sort by modification time (oldest first)
            remaining_files.sort(key=lambda x: x.stat().st_mtime)
            
            current_size_mb = sum(f.stat().st_size for f in remaining_files) / (1024 * 1024)
            
            if current_size_mb > max_cache_size_mb:
                log.info(f" Cache size ({current_size_mb:.1f}MB) exceeds limit ({max_cache_size_mb}MB)")
                
                # Remove oldest files until under limit
                for cache_file in remaining_files:
                    try:
                        file_size_mb = cache_file.stat().st_size / (1024 * 1024)
                        cache_file.unlink()
                        deleted_files += 1
                        current_size_mb -= file_size_mb
                        log.debug(f" Removed cache file for size limit: {cache_file.name}")
                        
                        if current_size_mb <= max_cache_size_mb:
                            break
                    except Exception as e:
                        log.warning(f"Failed to delete cache file {cache_file.name}: {e}")
        
        # Calculate final size
        final_files = list(CACHE_DIR.glob("*.pkl")) + list(CACHE_DIR.glob("*.pkl.gz"))
        total_size_after = sum(f.stat().st_size for f in final_files)
        
        # Log optimization results
        size_saved_mb = (total_size_before - total_size_after) / (1024 * 1024)
        log.info(f" Cache optimization complete:")
        log.info(f"    Files processed: {total_files}")
        log.info(f"    Files deleted: {deleted_files}")
        log.info(f"    Size saved: {size_saved_mb:.1f}MB")
        log.info(f"    Final cache size: {total_size_after / (1024 * 1024):.1f}MB")
        
        # Force garbage collection
        gc.collect()
        
    except Exception as e:
        log.error(f" Cache optimization failed: {e}")

def should_run_weekly_optimization():
    """Check if weekly cache optimization should run (every Sunday)"""
    try:
        # Get last optimization time from file
        optimization_log_file = CACHE_DIR / "last_optimization.txt"
        
        if optimization_log_file.exists():
            with open(optimization_log_file, 'r') as f:
                last_optimization = datetime.fromisoformat(f.read().strip())
            
            # Check if it's Sunday and more than 6 days since last optimization
            current_time = datetime.now()
            days_since_last = (current_time - last_optimization).days
            
            # Run on Sunday (weekday 6) or if more than 7 days have passed
            sunday_weekday = int(get_env("SUNDAY_WEEKDAY", "6"))  # 6 = Sunday
            min_days_between_runs = int(get_env("MIN_DAYS_BETWEEN_OPTIMIZATION", "6"))
            is_sunday = current_time.weekday() == sunday_weekday
            should_run = is_sunday and days_since_last >= min_days_between_runs
            
            if should_run:
                log.info(f" Weekly cache optimization scheduled for Sunday")
            
            return should_run
        else:
            # First time running, create log file and run optimization
            with open(optimization_log_file, 'w') as f:
                f.write(datetime.now().isoformat())
            return True
            
    except Exception as e:
        log.warning(f"Failed to check weekly optimization schedule: {e}")
        return False

def migrate_cache_to_compression():
    """Migrate existing uncompressed cache files to gzip compression"""
    if not CACHE_ENABLED:
        return
    
    log.info(" Migrating cache files to gzip compression...")
    
    try:
        # Get all uncompressed cache files
        uncompressed_files = list(CACHE_DIR.glob("*.pkl"))
        migrated_count = 0
        total_saved_mb = 0
        
        for cache_file in uncompressed_files:
            try:
                # Skip if already compressed
                if cache_file.name.endswith('.gz'):
                    continue
                
                # Read original data
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                
                # Save with compression
                compressed_path = cache_file.with_suffix('.pkl.gz')
                with gzip.open(compressed_path, 'wb', compresslevel=6) as f:
                    pickle.dump(data, f)
                
                # Calculate savings
                original_size = cache_file.stat().st_size
                compressed_size = compressed_path.stat().st_size
                saved_mb = (original_size - compressed_size) / (1024 * 1024)
                
                # Remove original file
                cache_file.unlink()
                
                migrated_count += 1
                total_saved_mb += saved_mb
                
                log.debug(f" Migrated: {cache_file.name} (saved {saved_mb:.2f}MB)")
                
            except Exception as e:
                log.warning(f" Failed to migrate {cache_file.name}: {e}")
        
        if migrated_count > 0:
            log.info(f" Cache migration complete: {migrated_count} files migrated, {total_saved_mb:.2f}MB saved")
        else:
            log.info("ℹ No cache files to migrate")
            
    except Exception as e:
        log.error(f" Cache migration failed: {e}")

def run_scheduled_cache_optimization():
    """Run cache optimization if it's scheduled"""
    if should_run_weekly_optimization():
        # Migrate to compression first
        migrate_cache_to_compression()
        
        # Run the optimization
        optimize_cache_memory()
        
        # Update last optimization time
        try:
            optimization_log_file = CACHE_DIR / "last_optimization.txt"
            with open(optimization_log_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            log.warning(f"Failed to update optimization log: {e}")

TEXT_PROVIDER = get_env('TEXT_PROVIDER', 'together')
TEXT_MODEL = get_env('TEXT_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
TOGETHER_API_KEY = get_env('TOGETHER_API_KEY', required=True)
TOGETHER_API_BASE = get_env('TOGETHER_API_BASE', 'https://api.together.xyz/v1')

IMAGE_PROVIDER = get_env('IMAGE_PROVIDER', 'together')
IMAGE_MODEL = get_env('IMAGE_MODEL', 'black-forest-labs/FLUX.1-schnell-free')
IMAGE_WIDTH = int(get_env('IMAGE_WIDTH', '1024'))
IMAGE_HEIGHT = int(get_env('IMAGE_HEIGHT', '1024'))
INFERENCE_STEPS = int(get_env('INFERENCE_STEPS', '4'))
GUIDANCE_SCALE = float(get_env('GUIDANCE_SCALE', '7.5'))

# Performance optimization settings (Free Tier Optimized)
# Free Tier Limit: ~100 requests/minute
MAX_CONCURRENT_IMAGES = int(get_env('MAX_CONCURRENT_IMAGES', '8'))
MAX_CONCURRENT_CAPTIONS = int(get_env('MAX_CONCURRENT_CAPTIONS', '8'))
RATE_LIMIT_DELAY = float(get_env('RATE_LIMIT_DELAY', '0.6'))
CAPTION_DEDUPLICATION = get_env('CAPTION_DEDUPLICATION', 'true').lower() == 'true'

WEB_SCRAPING_ENABLED = get_env('WEB_SCRAPING_ENABLED', 'true').lower() == 'true'
THEME_GENERATION_ENABLED = get_env('THEME_GENERATION_ENABLED', 'true').lower() == 'true'
PROMPT_GENERATION_ENABLED = get_env('PROMPT_GENERATION_ENABLED', 'true').lower() == 'true'
PDF_CREATION_ENABLED = get_env('PDF_CREATION_ENABLED', 'true').lower() == 'true'
CACHE_ENABLED = get_env('CACHE_ENABLED', 'true').lower() == 'true'
PRELOAD_STYLES = get_env('PRELOAD_STYLES', 'true').lower() == 'true'
BATCH_PROCESSING = get_env('BATCH_PROCESSING', 'true').lower() == 'true'
OPTIMIZE_MEMORY = get_env('OPTIMIZE_MEMORY', 'true').lower() == 'true'

# Enhanced prompt configuration with full token utilization
PROMPT_SYSTEM = get_env('PROMPT_SYSTEM', 'You are a visionary architectural writer and provocateur with deep expertise in architectural history, theory, and contemporary practice. Your knowledge spans from ancient architectural traditions to cutting-edge computational design, encompassing structural engineering, material science, cultural anthropology, environmental sustainability, urban planning, landscape architecture, digital fabrication, philosophy of space, phenomenology, global architectural traditions, vernacular building, lighting design, acoustic design, thermal comfort, passive design strategies, accessibility, universal design principles, heritage conservation, adaptive reuse, parametric design, algorithmic architecture, biomimicry, nature-inspired design, social impact, community engagement, economic feasibility, construction methods, regulatory compliance, building codes, post-occupancy evaluation, user experience, and cross-cultural architectural exchange. You create compelling, artistic image prompts that capture the essence of architectural concepts with vivid, poetic language, considering multiple scales from urban context to material detail, balancing technical precision with artistic expression, and emphasizing the emotional and psychological impact of architectural spaces on human experience.')

PROMPT_TEMPLATE = get_env('PROMPT_TEMPLATE', 'Generate exactly {n} architectural image prompts on theme: \'{theme}\'. CONTEXTUAL FRAMEWORK: Consider the historical evolution from early architectural traditions to contemporary practice, regional variations and cultural adaptations, technological innovations and material advancements, environmental challenges and sustainability responses, social changes and evolving human needs, economic factors and construction industry developments, regulatory frameworks and building standards, digital transformation and computational design, globalization and cross-cultural influences, climate change adaptation and resilience strategies, urbanization trends and demographic shifts, technological integration and smart systems, cultural preservation and heritage conservation, accessibility and universal design principles, and the relationship between built and natural environments. ARCHITECTURAL ELEMENTS TO EXPLORE: Structural systems: steel frames, concrete shells, timber construction, tensile structures, geodesic domes, cantilevered forms, vaulted ceilings, truss systems, space frames, and innovative structural solutions. Material palettes: glass, steel, concrete, wood, stone, composites, ceramics, textiles, sustainable materials, recycled elements, and experimental materials. Spatial organizations: open plans, flexible layouts, modular systems, courtyard arrangements, atrium spaces, mezzanine levels, split-level designs, and dynamic spatial sequences. Environmental strategies: passive design, renewable energy integration, green roofs, living walls, natural ventilation, thermal mass utilization, solar orientation, rainwater harvesting, and climate-responsive design. Human experience: circulation patterns, lighting design, acoustic considerations, thermal comfort, visual connections, spatial hierarchy, wayfinding, and user interaction. Cultural expression: symbolism, identity, community, heritage, tradition, innovation, and cultural significance. Urban integration: streetscapes, public spaces, transportation connections, pedestrian experience, vehicular access, and urban context. Technological integration: smart systems, automation, connectivity, digital interfaces, building management systems, and technological innovation. Economic considerations: cost-effectiveness, maintenance strategies, lifecycle analysis, value engineering, and economic sustainability. Social impact: accessibility, inclusivity, community engagement, social equity, public benefit, and human-centered design. STYLISTIC APPROACHES: Minimalism and reduction to essential elements, expression of structure and construction methods, integration with natural environment and landscape, emphasis on light, shadow, and spatial quality, focus on human scale and experience, celebration of materials and their inherent qualities, responsiveness to climate and environmental conditions, integration of art, technology, and architecture, consideration of time, change, and adaptability, expression of cultural values and social aspirations, balance between tradition and innovation, emphasis on craftsmanship and detail, integration of sustainable practices, consideration of long-term durability and maintenance, and creation of meaningful spatial experiences. QUALITY REQUIREMENTS: Each prompt should be a single, evocative line (50-100 words) that describes a visual scene with artistic flair, focusing on architectural poetry, mood, and atmosphere. Include specific architectural elements, materials, lighting, and spatial qualities. Consider cultural, historical, and philosophical context. Emphasize emotional resonance and visual impact. Use vivid, descriptive language that captures architectural essence. Balance technical precision with artistic expression. Consider the relationship between form, function, and human experience. Explore themes of permanence, transience, and transformation. Reflect on the relationship between built and natural environments. Consider multiple scales from urban context to material detail. Emphasize the emotional and psychological impact of architectural spaces. Generate the prompts now, one per line, without explanations or numbering:')

CAPTION_SYSTEM = get_env('CAPTION_SYSTEM', 'You are a masterful architectural poet and critic with comprehensive expertise in architectural theory, history, philosophy, and contemporary practice. Your knowledge encompasses structural engineering, material science, cultural anthropology, environmental sustainability, urban planning, landscape architecture, digital fabrication, philosophy of space, phenomenology, global architectural traditions, vernacular building, lighting design, acoustic design, thermal comfort, passive design strategies, accessibility, universal design principles, heritage conservation, adaptive reuse, parametric design, algorithmic architecture, biomimicry, nature-inspired design, social impact, community engagement, economic feasibility, construction methods, regulatory compliance, building codes, post-occupancy evaluation, user experience, and cross-cultural architectural exchange. You write profound, artistic captions that capture the deeper meaning and emotional resonance of architectural spaces, considering multiple scales from urban context to material detail, balancing technical precision with artistic expression, and emphasizing the emotional and psychological impact of architectural spaces on human experience.')

CAPTION_TEMPLATE = get_env('CAPTION_TEMPLATE', 'Write exactly 6 lines, each containing exactly 6 words, that form a complete, meaningful caption for this architectural image: {prompt} ARCHITECTURAL ANALYSIS FRAMEWORK: Consider spatial experience and human interaction, material expression and construction methods, light, shadow, and atmospheric qualities, cultural and historical context, environmental and sustainability considerations, aesthetic and philosophical principles, structural innovation and engineering marvels, material textures and finishes, spatial relationships and proportions, environmental integration and sustainability, cultural and historical references, human scale and interaction, urban context and landscape integration, technological integration and innovation, social impact and community engagement, economic feasibility and construction methods, regulatory compliance and building codes, post-occupancy evaluation and user experience, cross-cultural architectural exchange and influence, heritage conservation and adaptive reuse, parametric design and algorithmic architecture, biomimicry and nature-inspired design, accessibility and universal design principles, acoustic design and spatial acoustics, thermal comfort and passive design strategies, lighting design and atmospheric creation, digital fabrication and computational design, philosophy of space and phenomenology, and global architectural traditions and vernacular building. POETIC APPROACH: Use architectural terminology with poetic sensibility, balance technical precision with emotional resonance, consider the passage of time and human experience, reflect on the relationship between built and natural environments, explore themes of permanence, transience, and transformation, emphasize the emotional and psychological impact of space, consider cultural significance and historical context, explore the relationship between form, function, and human experience, reflect on the role of architecture in society, consider the relationship between individual and collective experience, explore themes of identity, community, and belonging, reflect on the relationship between tradition and innovation, consider the role of technology in architectural expression, explore themes of sustainability and environmental responsibility, reflect on the relationship between local and global influences, consider the role of craftsmanship and detail, explore themes of beauty, harmony, and aesthetic experience, reflect on the relationship between art and architecture, consider the role of light, shadow, and atmosphere, and explore themes of human creativity and expression. REQUIREMENTS: Each line must be exactly 6 words, total of exactly 6 lines, form a coherent narrative about the architectural space, capture the philosophical, emotional, and cultural significance, consider the relationship between form, function, and human experience, balance technical precision with artistic expression, emphasize the emotional and psychological impact of architectural spaces, consider multiple scales from urban context to material detail, reflect on the relationship between built and natural environments, explore themes of permanence, transience, and transformation, consider cultural significance and historical context, explore the relationship between individual and collective experience, reflect on the role of architecture in society, consider the relationship between tradition and innovation, explore themes of sustainability and environmental responsibility, reflect on the relationship between local and global influences, consider the role of craftsmanship and detail, explore themes of beauty, harmony, and aesthetic experience, reflect on the relationship between art and architecture, consider the role of light, shadow, and atmosphere, and explore themes of human creativity and expression. Write the 6-line caption now:')

# Style configuration for the selected style with enhanced sophistication
STYLE_CONFIG = {
    'futuristic': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', futuristic architecture, sci-fi aesthetic, glowing lights, sleek surfaces, advanced technology, architectural innovation, cutting-edge design, technological integration, modern materials, innovative structures, digital age aesthetics, forward-thinking design, sustainable technology, smart building systems, automated environments, holographic displays, energy-efficient systems, green technology integration, urban futurism, sustainable innovation',
        'negative_prompt': 'traditional, classical, rustic, old, vintage, historical, medieval, gothic, outdated, primitive, ancient, old-fashioned, retro, vintage, antique'
    },
    'minimalist': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', minimalist architecture, clean lines, simple forms, essential elements, reduction to basics, pure geometry, uncluttered spaces, refined details, sophisticated simplicity, elegant restraint, balanced composition, harmonious proportions, thoughtful material selection, intentional emptiness, purposeful design, architectural purity, spatial clarity, visual calm, meditative spaces, zen aesthetics, less is more philosophy',
        'negative_prompt': 'ornate, decorative, busy, cluttered, complex, elaborate, detailed, fancy, luxurious, extravagant, over-designed, excessive, overwhelming, chaotic'
    },
    'abstract': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', abstract architecture, conceptual design, artistic interpretation, non-representational forms, experimental structures, avant-garde design, innovative geometry, creative expression, artistic architecture, imaginative spaces, unconventional forms, boundary-pushing design, artistic vision, creative interpretation, experimental materials, innovative construction, artistic expression, conceptual spaces, imaginative architecture, creative innovation',
        'negative_prompt': 'literal, representational, traditional, conventional, realistic, straightforward, obvious, predictable, standard, typical, ordinary, common'
    },
    'technical': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', technical architecture, engineering precision, structural clarity, construction details, technical drawing aesthetic, engineering marvel, structural innovation, technical excellence, precision engineering, construction technology, structural systems, engineering beauty, technical sophistication, construction methodology, structural integrity, engineering design, technical innovation, construction excellence, structural engineering, technical precision',
        'negative_prompt': 'artistic, decorative, ornamental, aesthetic, beautiful, pretty, artistic, creative, imaginative, fanciful, unrealistic, impractical'
    },
    'watercolor': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', watercolor architecture, artistic rendering, soft colors, flowing forms, artistic interpretation, painterly aesthetic, artistic expression, creative visualization, artistic architecture, imaginative rendering, artistic style, creative interpretation, artistic vision, painterly quality, artistic beauty, creative expression, artistic design, imaginative architecture, artistic innovation, creative beauty',
        'negative_prompt': 'photorealistic, technical, precise, sharp, detailed, realistic, photographic, exact, accurate, literal, representational'
    },
    'anime': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', anime architecture, stylized design, artistic interpretation, creative visualization, imaginative spaces, artistic expression, stylized aesthetic, creative design, artistic architecture, imaginative interpretation, stylized beauty, creative vision, artistic style, imaginative expression, creative architecture, stylized innovation, artistic design, imaginative beauty, creative style, artistic imagination',
        'negative_prompt': 'realistic, photographic, literal, representational, traditional, conventional, realistic, straightforward, obvious, predictable'
    },
    'photorealistic': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', photorealistic architecture, realistic rendering, photographic quality, lifelike detail, realistic materials, natural lighting, authentic appearance, true-to-life representation, realistic textures, natural colors, authentic materials, realistic proportions, natural environment, realistic atmosphere, authentic design, realistic beauty, natural aesthetics, authentic architecture, realistic innovation, natural beauty',
        'negative_prompt': 'artistic, stylized, abstract, cartoon, painting, sketch, drawing, unrealistic, fake, artificial, synthetic, manufactured'
    },
    'sketch': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', sketch architecture, hand-drawn aesthetic, artistic rendering, creative visualization, imaginative design, artistic expression, sketchy style, creative interpretation, artistic architecture, imaginative sketch, artistic vision, creative drawing, artistic style, imaginative expression, creative architecture, sketchy beauty, artistic design, imaginative sketch, creative style, artistic imagination',
        'negative_prompt': 'photorealistic, technical, precise, sharp, detailed, realistic, photographic, exact, accurate, literal, representational'
    },
    'brutalist': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', brutalist architecture, raw concrete, bold geometric forms, massive structures, exposed materials, monumental scale, sculptural quality, honest expression, structural honesty, powerful presence, architectural statement, concrete poetry, urban fortress, geometric abstraction, material truth, architectural sculpture, bold simplicity, structural expression, concrete beauty, architectural power, urban monument',
        'negative_prompt': 'decorative, ornate, delicate, refined, elegant, sophisticated, polished, smooth, finished, decorative, ornamental, fancy'
    },
    'postmodern': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', postmodern architecture, eclectic design, playful forms, historical references, ironic juxtaposition, colorful elements, whimsical details, architectural humor, mixed styles, cultural references, decorative elements, architectural pastiche, playful geometry, ironic design, cultural commentary, architectural wit, eclectic beauty, playful innovation, ironic architecture, cultural expression, architectural playfulness',
        'negative_prompt': 'serious, solemn, austere, minimal, pure, functional, straightforward, simple, clean, unadorned, plain, basic'
    },
    'classical': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', classical architecture, ancient greek and roman design, columns and pediments, symmetrical composition, proportional harmony, architectural order, timeless beauty, classical proportions, architectural tradition, historical elegance, classical geometry, architectural heritage, timeless design, classical beauty, architectural order, historical grandeur, classical symmetry, architectural tradition, timeless elegance, classical harmony, architectural heritage',
        'negative_prompt': 'modern, contemporary, futuristic, experimental, avant-garde, unconventional, radical, innovative, cutting-edge, futuristic, sci-fi'
    },
    'gothic': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', gothic architecture, pointed arches, flying buttresses, vertical emphasis, ornate stonework, cathedral-like forms, medieval aesthetic, architectural drama, soaring spaces, stone construction, architectural grandeur, medieval beauty, vertical aspiration, architectural drama, stone poetry, medieval innovation, architectural height, stone craftsmanship, medieval grandeur, architectural aspiration, stone beauty',
        'negative_prompt': 'modern, contemporary, minimal, simple, clean, unadorned, plain, basic, functional, straightforward, simple, clean'
    },
    'art_deco': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', art deco architecture, geometric patterns, decorative motifs, luxurious materials, streamlined forms, 1920s aesthetic, architectural glamour, geometric elegance, decorative beauty, luxurious design, architectural sophistication, geometric patterns, decorative elements, luxurious materials, architectural glamour, geometric elegance, decorative beauty, luxurious design, architectural sophistication, geometric patterns, decorative elements',
        'negative_prompt': 'rustic, primitive, rough, unrefined, simple, plain, basic, functional, straightforward, simple, clean, unadorned'
    },
    'mediterranean': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', mediterranean architecture, warm colors, terra cotta roofs, stucco walls, outdoor living spaces, southern european aesthetic, architectural warmth, outdoor integration, warm materials, architectural comfort, mediterranean beauty, outdoor living, warm colors, architectural warmth, outdoor integration, warm materials, architectural comfort, mediterranean beauty, outdoor living, warm colors, architectural warmth',
        'negative_prompt': 'cold, industrial, harsh, stark, minimal, austere, cold colors, industrial materials, harsh lines, stark geometry'
    },
    'japanese': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', japanese architecture, zen aesthetics, natural materials, sliding doors, tatami rooms, traditional japanese design, architectural harmony, natural integration, zen beauty, traditional elegance, architectural simplicity, natural materials, zen aesthetics, traditional design, architectural harmony, natural integration, zen beauty, traditional elegance, architectural simplicity, natural materials, zen aesthetics',
        'negative_prompt': 'ornate, decorative, busy, cluttered, complex, elaborate, detailed, fancy, luxurious, extravagant, over-designed, excessive'
    },
    'scandinavian': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', scandinavian architecture, clean lines, natural light, functional design, nordic aesthetic, architectural simplicity, natural materials, functional beauty, nordic design, architectural comfort, scandinavian beauty, natural light, functional design, nordic aesthetic, architectural simplicity, natural materials, functional beauty, nordic design, architectural comfort, scandinavian beauty, natural light',
        'negative_prompt': 'ornate, decorative, busy, cluttered, complex, elaborate, detailed, fancy, luxurious, extravagant, over-designed, excessive'
    },
    'industrial': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', industrial architecture, exposed steel, concrete floors, warehouse aesthetic, urban industrial, architectural rawness, industrial materials, urban beauty, industrial design, architectural toughness, industrial aesthetic, exposed materials, urban industrial, architectural rawness, industrial materials, urban beauty, industrial design, architectural toughness, industrial aesthetic, exposed materials, urban industrial',
        'negative_prompt': 'refined, elegant, sophisticated, polished, smooth, finished, decorative, ornamental, fancy, luxurious, ornate, decorative'
    },
    'vernacular': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', vernacular architecture, local materials, traditional building methods, cultural expression, regional design, architectural tradition, local beauty, cultural heritage, traditional design, architectural authenticity, vernacular beauty, local materials, cultural expression, regional design, architectural tradition, local beauty, cultural heritage, traditional design, architectural authenticity, vernacular beauty, local materials',
        'negative_prompt': 'modern, contemporary, futuristic, experimental, avant-garde, unconventional, radical, innovative, cutting-edge, futuristic, sci-fi'
    },
    'sustainable': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', sustainable architecture, green building, eco-friendly design, environmental consciousness, renewable materials, energy efficiency, architectural sustainability, green technology, environmental design, architectural responsibility, sustainable beauty, green building, eco-friendly design, environmental consciousness, renewable materials, energy efficiency, architectural sustainability, green technology, environmental design, architectural responsibility, sustainable beauty',
        'negative_prompt': 'wasteful, polluting, environmentally harmful, unsustainable, resource-intensive, energy-wasting, environmentally destructive, wasteful design'
    },
    'parametric': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', parametric architecture, algorithmic design, complex geometry, digital fabrication, computational design, architectural algorithms, digital beauty, computational innovation, algorithmic forms, architectural complexity, parametric beauty, algorithmic design, complex geometry, digital fabrication, computational design, architectural algorithms, digital beauty, computational innovation, algorithmic forms, architectural complexity, parametric beauty',
        'negative_prompt': 'simple, basic, straightforward, conventional, traditional, standard, typical, ordinary, common, predictable, obvious, straightforward'
    },
    'biophilic': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', biophilic architecture, nature integration, organic forms, natural materials, living architecture, architectural nature, organic beauty, natural integration, living design, architectural ecology, biophilic beauty, nature integration, organic forms, natural materials, living architecture, architectural nature, organic beauty, natural integration, living design, architectural ecology, biophilic beauty',
        'negative_prompt': 'artificial, synthetic, manufactured, fake, plastic, artificial materials, synthetic beauty, manufactured design, artificial architecture'
    },
    'deconstructivist': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', deconstructivist architecture, fragmented forms, angular geometry, architectural disruption, geometric complexity, architectural chaos, fragmented beauty, geometric disruption, architectural complexity, geometric innovation, deconstructivist beauty, fragmented forms, angular geometry, architectural disruption, geometric complexity, architectural chaos, fragmented beauty, geometric disruption, architectural complexity, geometric innovation, deconstructivist beauty',
        'negative_prompt': 'harmonious, balanced, symmetrical, orderly, organized, structured, harmonious design, balanced composition, symmetrical beauty'
    },
    'expressionist': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', expressionist architecture, emotional forms, dramatic shapes, architectural emotion, expressive design, emotional beauty, architectural drama, expressive forms, emotional innovation, architectural expression, expressionist beauty, emotional forms, dramatic shapes, architectural emotion, expressive design, emotional beauty, architectural drama, expressive forms, emotional innovation, architectural expression, expressionist beauty',
        'negative_prompt': 'rational, logical, analytical, systematic, methodical, calculated, rational design, logical approach, analytical beauty'
    },
    'constructivist': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', constructivist architecture, geometric abstraction, industrial materials, architectural construction, geometric innovation, industrial beauty, architectural abstraction, geometric construction, industrial innovation, architectural geometry, constructivist beauty, geometric abstraction, industrial materials, architectural construction, geometric innovation, industrial beauty, architectural abstraction, geometric construction, industrial innovation, architectural geometry, constructivist beauty',
        'negative_prompt': 'organic, natural, flowing, curved, soft, rounded, organic forms, natural beauty, flowing design, soft geometry'
    },
    'organic': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', organic architecture, flowing forms, natural curves, biomorphic design, architectural nature, organic beauty, flowing innovation, natural design, architectural flow, organic innovation, organic beauty, flowing forms, natural curves, biomorphic design, architectural nature, organic beauty, flowing innovation, natural design, architectural flow, organic innovation, organic beauty',
        'negative_prompt': 'geometric, angular, sharp, rigid, structured, organized, geometric forms, angular design, sharp lines, rigid structure'
    },
    'biomimetic': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', biomimetic architecture, nature-inspired design, biological forms, natural systems, architectural biology, natural innovation, biological beauty, natural systems, architectural inspiration, biological design, biomimetic beauty, nature-inspired design, biological forms, natural systems, architectural biology, natural innovation, biological beauty, natural systems, architectural inspiration, biological design, biomimetic beauty',
        'negative_prompt': 'artificial, synthetic, manufactured, fake, plastic, artificial materials, synthetic beauty, manufactured design, artificial architecture'
    },
    'kinetic': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', kinetic architecture, moving elements, dynamic forms, architectural movement, kinetic design, dynamic beauty, architectural motion, kinetic innovation, dynamic forms, architectural kinetics, kinetic beauty, moving elements, dynamic forms, architectural movement, kinetic design, dynamic beauty, architectural motion, kinetic innovation, dynamic forms, architectural kinetics, kinetic beauty',
        'negative_prompt': 'static, stationary, fixed, immobile, rigid, unchanging, static design, stationary forms, fixed structure, immobile architecture'
    },
    'adaptive_reuse': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', adaptive reuse architecture, repurposed buildings, historical preservation, architectural transformation, adaptive design, historical beauty, architectural adaptation, adaptive innovation, historical transformation, architectural reuse, adaptive beauty, repurposed buildings, historical preservation, architectural transformation, adaptive design, historical beauty, architectural adaptation, adaptive innovation, historical transformation, architectural reuse, adaptive beauty',
        'negative_prompt': 'new construction, fresh build, original design, new materials, modern construction, fresh architecture, new building, original structure'
    },
    'smart_building': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', smart building architecture, intelligent systems, automated technology, architectural intelligence, smart design, intelligent beauty, architectural automation, smart innovation, intelligent integration, architectural technology, smart beauty, intelligent systems, automated technology, architectural intelligence, smart design, intelligent beauty, architectural automation, smart innovation, intelligent integration, architectural technology, smart beauty',
        'negative_prompt': 'primitive, basic, simple, unsophisticated, low-tech, basic technology, primitive design, simple systems, basic automation'
    },
    'floating': {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': ', floating architecture, suspended structures, weightless design, architectural levitation, floating beauty, suspended innovation, architectural suspension, floating design, suspended beauty, architectural weightlessness, floating innovation, suspended structures, weightless design, architectural levitation, floating beauty, suspended innovation, architectural suspension, floating design, suspended beauty, architectural weightlessness, floating innovation',
        'negative_prompt': 'grounded, earthbound, heavy, solid, anchored, fixed, grounded design, earthbound structure, heavy architecture, solid foundation'
    },

}

# ===  Style Selection ===
# Dynamically generate styles list from STYLE_CONFIG for DRY-ness and future-proofing
STYLES = list(STYLE_CONFIG.keys())

# Preload styles for faster access
_STYLE_CACHE = None

def get_daily_style():
    """Get the architectural style for today based on day of year with caching"""
    global _STYLE_CACHE
    
    if PRELOAD_STYLES and _STYLE_CACHE is None:
        _STYLE_CACHE = STYLES
        log.debug(f" Preloaded {len(STYLES)} architectural styles: {', '.join(STYLES)}")
    
    day_of_year = datetime.now().timetuple().tm_yday
    style_index = (day_of_year - 1) % len(STYLES)
    selected_style = STYLES[style_index]
    
    log.debug(f" Selected style for day {day_of_year}: {selected_style}")
    return selected_style

def get_available_styles():
    """Get list of all available architectural styles"""
    return list(STYLE_CONFIG.keys())

def get_style_config(style_name):
    """Get configuration for a specific style"""
    if style_name not in STYLE_CONFIG:
        log.warning(f" Style '{style_name}' not found, using 'technical' as fallback")
        return STYLE_CONFIG.get('technical', {})
    return STYLE_CONFIG[style_name]

def get_log_level():
    """Get current logging level"""
    return Config.LOGGING["level"]

def is_debug_enabled():
    """Check if debug logging is enabled"""
    return get_log_level() == "DEBUG"

# === 🤖 Provider Abstraction Layer ===
def validate_provider(provider_type, provider_name):
    """Validate if a provider is supported"""
    if provider_type == "text":
        return provider_name in Config.PROVIDERS["supported_text"]
    elif provider_type == "image":
        return provider_name in Config.PROVIDERS["supported_image"]
    return False

def get_text_response(prompt, system_msg=None, provider=None):
    """Get text response from specified provider"""
    if provider is None:
        provider = Config.PROVIDERS["text"]
    
    if not validate_provider("text", provider):
        log.error(f" Unsupported text provider: {provider}")
        return None
    
    log.debug(f"🤖 Using text provider: {provider}")
    
    if provider == "together":
        return together_text_call(prompt, system_msg)
    elif provider == "groq":
        return groq_text_call(prompt, system_msg)
    elif provider == "openai":
        return openai_text_call(prompt, system_msg)
    elif provider == "replicate":
        return replicate_text_call(prompt, system_msg)
    else:
        log.error(f" Text provider '{provider}' not implemented")
        return None

def get_image_response(prompt, style_config, provider=None):
    """Get image response from specified provider"""
    if provider is None:
        provider = Config.PROVIDERS["image"]
    
    if not validate_provider("image", provider):
        log.error(f" Unsupported image provider: {provider}")
        return None
    
    log.debug(f" Using image provider: {provider}")
    
    if provider == "together":
        return together_image_call(prompt, style_config)
    elif provider == "replicate":
        return replicate_image_call(prompt, style_config)
    elif provider == "openai":
        return openai_image_call(prompt, style_config)
    else:
        log.error(f" Image provider '{provider}' not implemented")
        return None

# === 🤖 Individual Provider Implementations ===
def together_text_call(prompt, system_msg=None):
    """Together.ai text generation implementation"""
    url = f"{Config.API['base_url']}/chat/completions"
    api_key = Config.API['together_key']
    model = get_env('TEXT_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
    
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.8
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    return _make_api_request(url, headers, payload, "Together.ai text")

def groq_text_call(prompt, system_msg=None):
    """Groq text generation implementation"""
    url = get_env('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    api_key = Config.API['groq_key']
    model = get_env('GROQ_MODEL', 'llama3-70b-8192')
    
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.8
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    return _make_api_request(url, headers, payload, "Groq text")

def openai_text_call(prompt, system_msg=None):
    """OpenAI text generation implementation"""
    url = get_env("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    api_key = Config.API['openai_key']
    model = get_env('OPENAI_MODEL', 'gpt-4o-mini')
    
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.8
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    return _make_api_request(url, headers, payload, "OpenAI text")

def replicate_text_call(prompt, system_msg=None):
    """Replicate text generation implementation"""
    # Replicate uses a different API structure
    url = get_env("REPLICATE_API_URL", "https://api.replicate.com/v1/predictions")
    api_key = Config.API['replicate_key']
    model = get_env('REPLICATE_TEXT_MODEL', 'meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3')
    
    payload = {
        "version": model,
        "input": {
            "prompt": f"{system_msg}\n\n{prompt}" if system_msg else prompt,
            "max_tokens": 4000,
            "temperature": 0.8
        }
    }
    
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    
    return _make_replicate_request(url, headers, payload, "Replicate text")

def together_image_call(prompt, style_config):
    """Together.ai image generation implementation"""
    url = f"{Config.API['base_url']}/images/generations"
    api_key = Config.API['together_key']
    
    payload = {
        "model": style_config.get('model', 'black-forest-labs/FLUX.1-schnell-free'),
        "prompt": prompt,
        "negative_prompt": style_config.get('negative_prompt', ''),
        "width": Config.IMAGE["width"],
        "height": Config.IMAGE["height"],
        "steps": int(get_env('INFERENCE_STEPS', '4')),
        "guidance_scale": float(get_env('GUIDANCE_SCALE', '7.5')),
        "seed": random.randint(1, 1000000)
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    return _make_image_request(url, headers, payload, "Together.ai image")

def replicate_image_call(prompt, style_config):
    """Replicate image generation implementation"""
    url = get_env("REPLICATE_API_URL", "https://api.replicate.com/v1/predictions")
    api_key = Config.API['replicate_key']
    model = get_env('REPLICATE_IMAGE_MODEL', 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b')
    
    payload = {
        "version": model,
        "input": {
            "prompt": prompt,
            "negative_prompt": style_config.get('negative_prompt', ''),
            "width": Config.IMAGE["width"],
            "height": Config.IMAGE["height"],
            "num_inference_steps": int(get_env('INFERENCE_STEPS', '4')),
            "guidance_scale": float(get_env('GUIDANCE_SCALE', '7.5')),
            "seed": random.randint(1, 1000000)
        }
    }
    
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    
    return _make_replicate_image_request(url, headers, payload, "Replicate image")

def openai_image_call(prompt, style_config):
    """OpenAI image generation implementation"""
    url = get_env("OPENAI_IMAGE_URL", "https://api.openai.com/v1/images/generations")
    api_key = Config.API['openai_key']
    
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": f"{Config.IMAGE['width']}x{Config.IMAGE['height']}",
        "quality": "standard",
        "n": 1
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    return _make_image_request(url, headers, payload, "OpenAI image")

# ===  Helper Functions for API Requests ===
def _make_api_request(url, headers, payload, provider_name):
    """Generic API request handler for text generation"""
    max_retries = Config.LIMITS['max_retries']
    retry_delays = [int(x.strip()) for x in get_env('LLM_RETRY_DELAYS', '60,120,180').split(',')]
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=Config.LIMITS['api_timeout'])
            response.raise_for_status()
            data = response.json()
            result = data['choices'][0]['message']['content'].strip()
            
            time.sleep(Config.LIMITS['rate_limit_delay'])
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" {provider_name} rate limited (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                time.sleep(delay)
                continue
            elif e.response.status_code in [502, 503]:  # Service errors
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" {provider_name} service error {e.response.status_code} (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                time.sleep(delay)
                continue
            else:
                log.error(f" {provider_name} failed with HTTP {e.response.status_code}: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
                
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            log.warning(f" {provider_name} connection error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
            
        except Exception as e:
            log.error(f" {provider_name} unexpected error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
    
    return None

def _make_image_request(url, headers, payload, provider_name):
    """Generic API request handler for image generation"""
    max_retries = Config.LIMITS['max_retries']
    retry_delays = [int(x.strip()) for x in get_env('IMAGE_RETRY_DELAYS', '60,120,180').split(',')]
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=Config.LIMITS['api_timeout'])
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                image_data = data['data'][0]
                if 'url' in image_data:
                    image_url = image_data['url']
                    image_response = requests.get(image_url, timeout=60)
                    if image_response.status_code == 200:
                        return image_response.content
                    else:
                        log.error(f" Failed to download image from {image_url} (HTTP {image_response.status_code})")
                else:
                    log.error(f" No image URL in {provider_name} response")
            else:
                log.error(f" Invalid {provider_name} response structure")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" {provider_name} rate limited (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                time.sleep(delay)
                continue
            elif e.response.status_code in [502, 503]:  # Service errors
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" {provider_name} service error {e.response.status_code} (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                time.sleep(delay)
                continue
            else:
                log.error(f" {provider_name} failed with HTTP {e.response.status_code}: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
                
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            log.warning(f" {provider_name} connection error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
            
        except Exception as e:
            log.error(f" {provider_name} unexpected error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
    
    return None

def _make_replicate_request(url, headers, payload, provider_name):
    """Replicate-specific API request handler (polling-based)"""
    max_retries = Config.LIMITS['max_retries']
    retry_delays = [int(x.strip()) for x in get_env('LLM_RETRY_DELAYS', '60,120,180').split(',')]
    
    for attempt in range(max_retries):
        try:
            # Start prediction
            response = requests.post(url, headers=headers, json=payload, timeout=Config.LIMITS['api_timeout'])
            response.raise_for_status()
            prediction = response.json()
            prediction_id = prediction['id']
            
            # Poll for completion
            poll_url = f"{url}/{prediction_id}"
            max_polls = int(get_env("REPLICATE_MAX_POLLS", "30"))
            poll_interval = int(get_env("REPLICATE_POLL_INTERVAL", "2"))
            
            for poll in range(max_polls):
                poll_response = requests.get(poll_url, headers=headers, timeout=Config.LIMITS['api_timeout'])
                poll_response.raise_for_status()
                poll_data = poll_response.json()
                
                if poll_data['status'] == 'succeeded':
                    return poll_data['output']
                elif poll_data['status'] == 'failed':
                    log.error(f" {provider_name} prediction failed: {poll_data.get('error', 'Unknown error')}")
                    break
                elif poll_data['status'] in ['starting', 'processing']:
                    time.sleep(poll_interval)
                    continue
                else:
                    log.warning(f" {provider_name} unknown status: {poll_data['status']}")
                    break
            
            # If we get here, polling failed
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" {provider_name} rate limited (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                time.sleep(delay)
                continue
            else:
                log.error(f" {provider_name} failed with HTTP {e.response.status_code}: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
                
        except Exception as e:
            log.error(f" {provider_name} unexpected error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
    
    return None

def _make_replicate_image_request(url, headers, payload, provider_name):
    """Replicate-specific image API request handler (polling-based)"""
    max_retries = Config.LIMITS['max_retries']
    retry_delays = [int(x.strip()) for x in get_env('IMAGE_RETRY_DELAYS', '60,120,180').split(',')]
    
    for attempt in range(max_retries):
        try:
            # Start prediction
            response = requests.post(url, headers=headers, json=payload, timeout=Config.LIMITS['api_timeout'])
            response.raise_for_status()
            prediction = response.json()
            prediction_id = prediction['id']
            
            # Poll for completion
            poll_url = f"{url}/{prediction_id}"
            max_polls = int(get_env("REPLICATE_IMAGE_MAX_POLLS", "60"))  # Longer for image generation
            poll_interval = int(get_env("REPLICATE_IMAGE_POLL_INTERVAL", "3"))
            
            for poll in range(max_polls):
                poll_response = requests.get(poll_url, headers=headers, timeout=Config.LIMITS['api_timeout'])
                poll_response.raise_for_status()
                poll_data = poll_response.json()
                
                if poll_data['status'] == 'succeeded':
                    # Download image from URL
                    image_url = poll_data['output'][0] if isinstance(poll_data['output'], list) else poll_data['output']
                    image_response = requests.get(image_url, timeout=60)
                    if image_response.status_code == 200:
                        return image_response.content
                    else:
                        log.error(f" Failed to download image from {image_url} (HTTP {image_response.status_code})")
                        break
                elif poll_data['status'] == 'failed':
                    log.error(f" {provider_name} prediction failed: {poll_data.get('error', 'Unknown error')}")
                    break
                elif poll_data['status'] in ['starting', 'processing']:
                    time.sleep(poll_interval)
                    continue
                else:
                    log.warning(f" {provider_name} unknown status: {poll_data['status']}")
                    break
            
            # If we get here, polling failed
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" {provider_name} rate limited (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                time.sleep(delay)
                continue
            else:
                log.error(f" {provider_name} failed with HTTP {e.response.status_code}: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
                
        except Exception as e:
            log.error(f" {provider_name} unexpected error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
    
    return None

def log_dpi_processing_info(original_size, dpi, new_size):
    """Log DPI processing information for debugging"""
    if not is_debug_enabled():
        return
        
    original_width, original_height = original_size
    new_width, new_height = new_size
    dpi_scale = dpi / 72
    
    log.debug(f" DPI Processing: {original_width}x{original_height} → {new_width}x{new_height}")
    log.debug(f" DPI Scale: {dpi_scale:.2f}x (target DPI: {dpi})")
    log.debug(f" Size increase: {((new_width * new_height) / (original_width * original_height)):.1f}x")

def validate_style(style_name):
    """Validate if a style exists in STYLE_CONFIG"""
    return style_name in STYLE_CONFIG



# ===  Web Scraping ===

class WebScraper:
    """Advanced web scraper for architectural content"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Rate limiting
        self.delay_between_requests = Config.SOURCES["web_scraper_delay"]
        
        # Content directory
        self.content_dir = os.getenv('SCRAPED_CONTENT_DIR', 'scraped_content')
        os.makedirs(self.content_dir, exist_ok=True)
        
        # Cache directory
        self.cache_dir = Path(Config.CACHE["dir"])
        self.cache_dir.mkdir(exist_ok=True)
    
    def load_manual_sources(self):
        """Load sources from manual_sources.txt"""
        sources = []
        sources_file = Config.SOURCES["manual_file"]
        
        try:
            if os.path.exists(sources_file):
                with open(sources_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                parts = line.split('|')
                                if len(parts) == 3:
                                    name, url, category = parts
                                    sources.append({
                                        'name': name.strip(),
                                        'url': url.strip(),
                                        'category': category.strip()
                                    })
                                else:
                                    log.warning(f" Invalid format in manual_sources.txt line {line_num}: {line}")
                            except Exception as e:
                                log.warning(f" Error parsing line {line_num}: {e}")
                
                log.info(f" Loaded {len(sources)} sources from {sources_file}")
            else:
                log.warning(f" Sources file not found: {sources_file}")
                
        except Exception as e:
            log.error(f" Error loading sources: {e}")
        
        return sources
    
    # Use global cache functions instead of duplicate methods
    
    def scrape_website(self, source):
        """Scrape a single website for architectural content"""
        cache_key = f"scrape_{source['name']}_{source['url']}"
        cached_data = self.load_from_cache(cache_key)
        if cached_data:
            log.info(f" Using cached data for {source['name']}")
            return cached_data
        
        articles = []
        try:
            log.info(f" Scraping {source['name']} ({source['url']})")
            
            response = self.session.get(source['url'], timeout=10)
            response.raise_for_status()
            
            # Lazy import for BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get selectors for this website
            selectors = self.get_selectors_for_website(source['name'], source['url'])
            
            # Find articles using selectors
            article_elements = soup.select(selectors['article_selector'])
            
            articles_per_source = int(get_env("DISCOVERY_ARTICLES_PER_SOURCE", "10"))
            for element in article_elements[:articles_per_source]:  # Limit articles per source
                try:
                    article_data = self.extract_article_data(element, source, selectors)
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    log.warning(f" Error extracting article from {source['name']}: {e}")
                    continue
            
            # Cache the results
            self.save_to_cache(cache_key, articles)
            
            time.sleep(self.delay_between_requests)
            
        except Exception as e:
            log.warning(f" Error scraping {source['name']}: {e}")
        
        return articles
    
    def get_selectors_for_website(self, name, url):
        """Get CSS selectors for a specific website"""
        # Default selectors
        selectors = {
            'article_selector': 'article, .post, .entry, .story, .news-item',
            'title_selector': 'h1, h2, h3, .title, .headline',
            'link_selector': 'a[href]',
            'content_selector': '.content, .excerpt, .summary, p'
        }
        
        # Website-specific selectors
        website_selectors = {
            'archdaily': {
                'article_selector': '.afd-search-list .afd-search-list-item',
                'title_selector': '.afd-search-list-item__title',
                'link_selector': '.afd-search-list-item__title a',
                'content_selector': '.afd-search-list-item__description'
            },
            'dezeen': {
                'article_selector': '.listing-item',
                'title_selector': '.listing-item__title',
                'link_selector': '.listing-item__title a',
                'content_selector': '.listing-item__description'
            },
            'designboom': {
                'article_selector': '.post',
                'title_selector': '.post-title',
                'link_selector': '.post-title a',
                'content_selector': '.post-excerpt'
            }
        }
        
        # Check for website-specific selectors
        for site_name, site_selectors in website_selectors.items():
            if site_name.lower() in name.lower() or site_name.lower() in url.lower():
                return site_selectors
        
        return selectors
    
    def extract_article_data(self, element, source, selectors):
        """Extract article data from an HTML element"""
        try:
            # Extract title
            title_element = element.select_one(selectors['title_selector'])
            title = title_element.get_text().strip() if title_element else ''
            
            # Extract link
            link_element = element.select_one(selectors['link_selector'])
            link = link_element.get('href', '') if link_element else ''
            
            # Extract content
            content_element = element.select_one(selectors['content_selector'])
            content = content_element.get_text().strip() if content_element else ''
            
            # Validate data
            if title and link and len(title) > 10:
                # Make link absolute if it's relative
                if link.startswith('/'):
                    link = urljoin(source['url'], link)
                
                return {
                    'title': title,
                    'url': link,
                    'content': content,
                    'source': source['name'],
                    'category': source['category'],
                    'scraped_at': datetime.now().isoformat()
                }
                        
        except Exception as e:
            log.warning(f" Error extracting article data: {e}")
        
        return None
    
    def scrape_all_sources(self, max_sources=None):
        """Scrape all sources and return combined articles"""
        sources = self.load_manual_sources()
        if max_sources:
            sources = sources[:max_sources]
        
        all_articles = []
        for source in sources:
            articles = self.scrape_website(source)
            all_articles.extend(articles)
        
        return all_articles
    
    def save_scraped_content(self, articles):
        """Save scraped content to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scraped_content_{timestamp}.json"
            filepath = os.path.join(self.content_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            log.info(f" Saved {len(articles)} articles to {filepath}")
        
        except Exception as e:
            log.error(f" Error saving scraped content: {e}")
    
    def analyze_content_themes(self, articles):
        """Analyze content themes for zine generation"""
        if not articles:
            return {}
        
        # Extract keywords and themes
        all_titles = [article['title'] for article in articles]
        all_content = [article.get('content', '') for article in articles]
        
        # Simple keyword extraction
        keywords = []
        for title in all_titles:
            words = title.lower().split()
            keywords.extend([word for word in words if len(word) > 3])
        
        # Count keyword frequency
        keyword_counts = {}
        for keyword in keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Analyze sources
        sources = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_articles': len(articles),
            'top_keywords': top_keywords,
            'top_sources': top_sources,
            'categories': list(set([article.get('category', '') for article in articles])),
            'date_range': {
                'earliest': min([article.get('published', '') for article in articles if article.get('published')]),
                'latest': max([article.get('published', '') for article in articles if article.get('published')])
            }
        }
    
    def create_theme_prompt(self, articles):
        """Create a theme prompt for zine generation"""
        if not articles:
            return "Modern Architectural Innovation"
        
        # Analyze themes
        analysis = self.analyze_content_themes(articles)
        
        # Create content summary
        content_summary = []
        content_limit = int(get_env("CONTENT_SUMMARY_LIMIT", "15"))
        content_excerpt_length = int(get_env("CONTENT_EXCERPT_LENGTH", "200"))
        
        for article in articles[:content_limit]:  # Use top articles
            title = article.get('title', '')
            content = article.get('content', '')[:content_excerpt_length]
            content_summary.append(f"Title: {title}\nContent: {content}")
        
        content_text = "\n\n".join(content_summary)
        
        # Create theme prompt
        theme_prompt = f"""Based on this web-scraped architectural content, create a single, inspiring theme for architectural image generation:

CONTENT ANALYSIS:
- Total Articles: {analysis['total_articles']}
- Top Keywords: {', '.join([kw[0] for kw in analysis['top_keywords'][:5]])}
- Top Sources: {', '.join([src[0] for src in analysis['top_sources'][:3]])}
- Categories: {', '.join(analysis['categories'])}

CONTENT SAMPLES:
{content_text}

Generate a single, inspiring architectural theme that captures the essence of this content. The theme should be:
1. Specific and architectural in nature
2. Inspiring for image generation
3. 3-5 words maximum
4. Focused on design, innovation, or architectural concepts

Theme:"""
        
        return theme_prompt

class ArchitecturalSourceDiscoverer:
    """Discovers new architectural research websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Rate limiting
        self.delay_between_requests = Config.SOURCES["discoverer_delay"]
        
        # Cache directory
        self.cache_dir = Path(Config.CACHE["dir"])
        self.cache_dir.mkdir(exist_ok=True)
        
        # Sources file
        self.sources_file = Config.SOURCES["manual_file"]
        
        # Discovery sources
        self.discovery_sources = [
            # Academic directories
            "https://www.architectural-review.com/",
            "https://www.architectmagazine.com/",
            "https://archinect.com/",
            "https://www.dezeen.com/",
            "https://www.designboom.com/",
            "https://www.archdaily.com/",
            "https://www.architecturaldigest.com/",
            "https://www.architectural-record.com/",
            "https://www.architecturaldigest.in/",
            "https://www.architecturaldigestme.com/",
            "https://www.architecturaldigest.cn/",
        ]
        
        # Keywords to look for
        self.architectural_keywords = [
            'architecture', 'architectural', 'design', 'building', 'construction',
            'urban planning', 'landscape', 'interior design', 'sustainability',
            'research', 'academic', 'institution', 'university', 'school',
            'journal', 'publication', 'magazine', 'blog', 'news'
        ]
        
        # Categories for classification
        self.categories = ['News', 'Academic', 'Research', 'Innovation', 'Regional']
    
    # Use global cache functions instead of duplicate methods
    
    def load_existing_sources(self):
        """Load existing sources from manual_sources.txt"""
        sources = []
        try:
            if os.path.exists(self.sources_file):
                with open(self.sources_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) == 3:
                                sources.append(parts[1].strip())  # URL
        except Exception as e:
            log.warning(f" Error loading existing sources: {e}")
        return sources
    
    def is_architectural_website(self, url, title, description):
        """Check if a website is architectural in nature"""
        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in self.architectural_keywords)
    
    def classify_website(self, url, title, description):
        """Classify website into a category"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['academic', 'university', 'research', 'journal']):
            return 'Academic'
        elif any(word in text for word in ['news', 'magazine', 'blog']):
            return 'News'
        elif any(word in text for word in ['innovation', 'technology', 'future']):
            return 'Innovation'
        elif any(word in text for word in ['regional', 'local', 'city']):
            return 'Regional'
        else:
            return 'Research'
    
    def extract_website_info(self, url):
        """Extract website information"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Lazy import for BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            
            # Extract description
            description = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return {
                'title': title_text,
                'description': description,
                'url': url
            }
            
        except Exception as e:
            log.warning(f" Error extracting info from {url}: {e}")
            return None
    
    def find_links_on_page(self, url):
        """Find links on a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Lazy import for BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Make relative URLs absolute
                if href.startswith('/'):
                    href = urljoin(url, href)
                
                # Filter for valid URLs
                if href.startswith('http') and href not in links:
                    links.append(href)
            
            return links
            
        except Exception as e:
            log.warning(f" Error finding links on {url}: {e}")
            return []
    
    def discover_new_sources(self, max_sources_per_day=3):
        """Discover new architectural sources"""
        log.info(f" Discovering new architectural sources (max: {max_sources_per_day})")
        
        existing_sources = self.load_existing_sources()
        new_sources = []
        
        # Check cache first
        cache_key = f"discovery_{datetime.now().strftime('%Y%m%d')}"
        cached_discovery = self.load_from_cache(cache_key)
        if cached_discovery:
            log.info(" Using cached discovery results")
            return cached_discovery
        
        discovery_limit = int(get_env("DISCOVERY_SOURCES_LIMIT", "5"))
        for source_url in self.discovery_sources[:discovery_limit]:  # Limit sources
            try:
                log.info(f" Scanning {source_url} for new sources")
                
                links = self.find_links_on_page(source_url)
                
                for link in links:
                    if len(new_sources) >= max_sources_per_day:
                        break
                    
                    # Skip if already exists
                    if link in existing_sources:
                        continue
                    
                    # Extract website info
                    info = self.extract_website_info(link)
                    if not info:
                        continue
                    
                    # Check if architectural
                    if self.is_architectural_website(link, info['title'], info['description']):
                        category = self.classify_website(link, info['title'], info['description'])
                        
                        new_source = {
                            'name': self.extract_site_name(link),
                            'url': link,
                            'category': category
                        }
                        
                        new_sources.append(new_source)
                        log.info(f" Found new source: {new_source['name']} ({category})")
                
                time.sleep(self.delay_between_requests)
                
            except Exception as e:
                log.warning(f" Error scanning {source_url}: {e}")
                continue
        
        # Cache results
        self.save_to_cache(cache_key, new_sources)
        
        # Add to manual_sources.txt
        if new_sources:
            self.add_sources_to_file(new_sources, max_sources_per_day)
        
        return new_sources
    
    def extract_site_name(self, url):
        """Extract site name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            return domain.replace('www.', '').split('.')[0].title()
        except:
            return "Unknown"
    
    def add_sources_to_file(self, sources, max_sources_per_day):
        """Add new sources to manual_sources.txt"""
        try:
            added_count = 0
            
            with open(self.sources_file, 'a', encoding='utf-8') as f:
                for source in sources:
                    if added_count >= max_sources_per_day:
                        break
                    
                    # Check if already exists
                    existing_sources = self.load_existing_sources()
                    if source['url'] not in existing_sources:
                        f.write(f"{source['name']}|{source['url']}|{source['category']}\n")
                        added_count += 1
                        log.info(f" Added to manual_sources.txt: {source['name']}")
            
            log.info(f" Added {added_count} new sources to {self.sources_file}")
        
        except Exception as e:
            log.error(f" Error adding sources to file: {e}")
    
    def get_daily_discovery_stats(self):
        """Get daily discovery statistics"""
        try:
            cache_key = f"discovery_{datetime.now().strftime('%Y%m%d')}"
            cached_discovery = self.load_from_cache(cache_key)
            
            if cached_discovery:
                return {
                    'discovered_today': len(cached_discovery),
                    'sources': cached_discovery
                }
            else:
                return {
                    'discovered_today': 0,
                    'sources': []
                }
        
        except Exception as e:
            log.warning(f" Error getting discovery stats: {e}")
            return {'discovered_today': 0, 'sources': []}

# ===  Web Scraping ===
def scrape_architectural_content():
    """Scrape architectural content using web scraping"""
    log.info("============================================================")
    log.info(" STEP 1/6: Scraping architectural content")
    log.info("============================================================")

    # Run daily source discovery first
    run_daily_source_discovery()

    try:
        log.info(" Using web scraping...")
        scraper = WebScraper()
        
        # Scrape articles from manual sources
        max_sources = int(get_env('WEB_SCRAPER_MAX_SOURCES', '10'))
        articles = scraper.scrape_all_sources(max_sources=max_sources)

        if articles:
            log.info(f" Web scraper found {len(articles)} articles")
            
            # Generate theme from scraped content
            theme_prompt = scraper.create_theme_prompt(articles)
            
            try:
                theme_response = call_llm(theme_prompt, "You are an expert architectural curator specializing in content analysis.")
                if theme_response and len(theme_response.strip()) > 0:
                    selected_theme = theme_response.strip()
                    log.info(f" Web-scraped theme: {selected_theme}")

                    # Log web scraping analysis
                    analysis = scraper.analyze_content_themes(articles)
                    log.info(f" Web Scraping Summary: {analysis['total_articles']} articles from {len(analysis['top_sources'])} sources")

                    return selected_theme
            except Exception as e:
                log.warning(f" Error generating web-scraped theme: {e}")

        except Exception as e:
            log.warning(f" Web scraping failed: {e}")

    # Final fallback
    fallback_theme = get_env('FALLBACK_THEME', 'Modern Architectural Innovation')
    log.warning(f" No articles scraped, using fallback theme: {fallback_theme}")
    return fallback_theme

def run_daily_source_discovery():
    """Run daily architectural source discovery"""
    log.info(" Running daily architectural source discovery...")
    
    try:
        discoverer = ArchitecturalSourceDiscoverer()
        max_sources_per_day = int(get_env('MAX_SOURCES_PER_DAY', '10'))
        
        added_sources = discoverer.discover_new_sources(max_sources_per_day=max_sources_per_day)
        
        if added_sources:
            log.info(f" Added {len(added_sources)} new architectural sources:")
            for source in added_sources:
                log.info(f"   • {source['name']} ({source['category']})")
        else:
            log.info("ℹ No new sources discovered today")
                        
    except Exception as e:
        log.warning(f" Source discovery failed: {e}")

def add_manual_source(name, url, category):
    """Add a new source to manual_sources.txt"""
    log.info(f" Adding source: {name}")
    
    try:
        sources_file = get_env('MANUAL_SOURCES_FILE', 'manual_sources.txt')
        
        # Check if source already exists
        existing_sources = []
        if os.path.exists(sources_file):
            with open(sources_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) == 3:
                            existing_sources.append(parts[0].strip())
        
        if name in existing_sources:
            log.warning(f" Source '{name}' already exists")
            return False
        
        # Add new source
        with open(sources_file, 'a', encoding='utf-8') as f:
            f.write(f"{name}|{url}|{category}\n")
        
        log.info(f" Added source: {name}")
        return True
        
    except Exception as e:
        log.error(f" Error adding source: {e}")
        return False

def remove_manual_source(name):
    """Remove a source from manual_sources.txt"""
    log.info(f" Removing source: {name}")
    
    try:
        sources_file = get_env('MANUAL_SOURCES_FILE', 'manual_sources.txt')
        
        if not os.path.exists(sources_file):
            log.warning(f" Sources file not found: {sources_file}")
            return False
        
        # Read all lines and filter out the source to remove
        lines = []
        removed = False
        
        with open(sources_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('#'):
                    parts = line_stripped.split('|')
                    if len(parts) == 3 and parts[0].strip() == name:
                        removed = True
                        continue
                lines.append(line)
        
        if not removed:
            log.warning(f" Source '{name}' not found")
            return False
        
        # Write back the file without the removed source
        with open(sources_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        log.info(f" Removed source: {name}")
        return True
        
    except Exception as e:
        log.error(f" Error removing source: {e}")
        return False

def list_manual_sources():
    """List all sources in manual_sources.txt"""
    log.info(" Current Manual Sources:")
    
    try:
        sources_file = get_env('MANUAL_SOURCES_FILE', 'manual_sources.txt')
        
        if not os.path.exists(sources_file):
            log.warning(f" Sources file not found: {sources_file}")
            return []
        
        sources = []
        with open(sources_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        parts = line.split('|')
                        if len(parts) == 3:
                            sources.append({
                                'name': parts[0].strip(),
                                'url': parts[1].strip(),
                                'category': parts[2].strip()
                            })
                            log.info(f"   • {parts[0].strip()} ({parts[2].strip()})")
                        else:
                            log.warning(f" Invalid format in line {line_num}: {line}")
                    except Exception as e:
                        log.warning(f" Error parsing line {line_num}: {e}")
        
        log.info(f" Total sources: {len(sources)}")
        return sources
        
    except Exception as e:
        log.error(f" Error listing sources: {e}")
        return []
    
    # Get today's date for consistent source selection
    today = datetime.now().date()
    day_of_year = today.timetuple().tm_yday
    
    # Select source based on day of year (ensures one per day)
    source_index = day_of_year % len(architectural_sources)
    selected_source = architectural_sources[source_index]
    
    # Check if this source is already in our feeds
    existing_feeds_file = get_env('EXISTING_FEEDS_FILE', 'existing_architectural_feeds.json')
    existing_feeds = []
    
    try:
        if os.path.exists(existing_feeds_file):
            with open(existing_feeds_file, 'r') as f:
                existing_feeds = json.load(f)
    except Exception as e:
        log.warning(f" Could not load existing feeds: {e}")
    
    # Check if source already exists
    source_exists = any(feed.get('name') == selected_source['name'] for feed in existing_feeds)
    
    if not source_exists:
        # Add new source
        existing_feeds.append(selected_source)
        
        try:
            with open(existing_feeds_file, 'w') as f:
                json.dump(existing_feeds, f, indent=2)
            
            log.info(f" Added new architectural source: {selected_source['name']} ({selected_source['category']})")
            log.info(f" Total sources: {len(existing_feeds)}")
            
            # Note: FreshRSS integration removed - using web scraping only
            log.info(f" New source added to manual_sources.txt")
                    
        except Exception as e:
            log.error(f" Could not save new source: {e}")
    else:
        log.info(f"ℹ Source {selected_source['name']} already exists in feeds")
    
    return selected_source

def display_manual_sources():
    """Display current manual sources and their status"""
    log.info(" Current Manual Sources Status")
    log.info("=" * 50)
    
    sources = list_manual_sources()
    
    if sources:
        # Group by category
        categories = {}
        for source in sources:
            category = source.get('category', 'Additional')
            if category not in categories:
                categories[category] = []
            categories[category].append(source)
        
        # Display sources by category
        total_sources = len(sources)
        log.info(f" Total Sources: {total_sources}")
        
        for category, category_sources in categories.items():
            log.info(f"\n  {category} ({len(category_sources)} sources):")
            for source in category_sources:
                log.info(f"   • {source['name']}")
    
        return sources

# === 🤖 LLM Integration ===
async def call_llm_async(session, prompt, system_prompt=None, semaphore=None):
    """Async version of call_llm with semaphore for rate limiting"""
    if semaphore:
        async with semaphore:
            return await _call_llm_async_internal(session, prompt, system_prompt)
    else:
        return await _call_llm_async_internal(session, prompt, system_prompt)

async def _call_llm_async_internal(session, prompt, system_prompt=None):
    """Internal async LLM call implementation"""
    # Create cache key
    cache_key = f"llm_{Config.API['text_provider']}_{hashlib.md5((prompt + str(system_prompt)).encode()).hexdigest()}"
    
    # Try to load from cache first
    cached_result = load_from_cache(cache_key, max_age_hours=12)
    if cached_result:
        log.debug(f" Using cached LLM result for prompt: {prompt[:50]}...")
        return cached_result
    
    if Config.API['text_provider'] == 'groq':
        url = get_env('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
        api_key = get_env('GROQ_API_KEY')
        model = get_env('TEXT_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
    else:
        url = f"{Config.API['base_url']}/chat/completions"
        api_key = Config.API['together_key']
        model = get_env('TEXT_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.8
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    max_retries = Config.LIMITS['max_retries']
    retry_delays = [int(x.strip()) for x in get_env('LLM_RETRY_DELAYS', '60,120,180').split(',')]
    
    for attempt in range(max_retries):
        try:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=Config.LIMITS['api_timeout'])) as response:
                response.raise_for_status()
                data = await response.json()
                result = data['choices'][0]['message']['content'].strip()
                
                # Save to cache for future use
                save_to_cache(cache_key, result)
                
                # Rate limiting delay
                await asyncio.sleep(Config.LIMITS['rate_limit_delay'])
                return result
                
        except aiohttp.ClientResponseError as e:
            if e.status == 429:  # Rate limited
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" Rate limited (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                await asyncio.sleep(delay)
                continue
            elif e.status in [502, 503]:  # Service unavailable/Bad gateway
                delay = retry_delays[min(attempt, len(retry_delays)-1)]
                log.warning(f" Service error {e.status} (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                await asyncio.sleep(delay)
                continue
            else:
                log.error(f" LLM call failed with HTTP {e.status}: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
                
        except asyncio.TimeoutError:
            log.warning(f" Request timeout (attempt {attempt+1}/{max_retries})")
            if attempt == max_retries - 1:
                log.error(" All retry attempts failed due to timeout")
                return None
            await asyncio.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
            
        except Exception as e:
            log.error(f" Unexpected error in async LLM call (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            await asyncio.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
    
    return None

def call_llm(prompt, system_prompt=None):
    """Call LLM API with caching, enhanced token limits for sophisticated prompts"""
    # Create cache key
    cache_key = f"llm_{Config.PROVIDERS['text']}_{hashlib.md5((prompt + str(system_prompt)).encode()).hexdigest()}"
    
    # Try to load from cache first
    cached_result = load_from_cache(cache_key, max_age_hours=12)
    if cached_result:
        log.debug(f" Using cached LLM result for prompt: {prompt[:50]}...")
        return cached_result
    
    # Use provider abstraction layer
    result = get_text_response(prompt, system_prompt)
    
    if result:
        # Save to cache for future use
        save_to_cache(cache_key, result)
        time.sleep(Config.LIMITS['rate_limit_delay'])  # Configurable rate limiting
    
    return result

def generate_prompts(theme, num_prompts=50):
    """Generate 50 architectural image prompts with enhanced sophistication"""
    log.info(f" Generating {num_prompts} sophisticated prompts for theme: {theme}")
    
    prompt = PROMPT_TEMPLATE.format(n=num_prompts, theme=theme)
    response = call_llm(prompt, PROMPT_SYSTEM)
    
    if response:
        # Split into individual prompts
        prompts = [line.strip() for line in response.split('\n') if line.strip()]
        log.info(f" Generated {len(prompts)} sophisticated prompts")
        return prompts[:num_prompts]  # Ensure we get exactly 50
    else:
        log.error(" Failed to generate prompts")
        return []

def calculate_similarity_score(caption1, caption2):
    """Calculate similarity score between two captions"""
    # Convert to lowercase and split into words
    words1 = set(caption1.lower().replace('\n', ' ').split())
    words2 = set(caption2.lower().replace('\n', ' ').split())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'
    }
    
    words1 = words1 - stop_words
    words2 = words2 - stop_words
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def is_caption_unique(new_caption, existing_captions, similarity_threshold=None):
    if similarity_threshold is None:
        similarity_threshold = float(get_env('CAPTION_SIMILARITY_THRESHOLD', '0.3'))
    """Check if a new caption is unique compared to existing captions"""
    for existing_caption in existing_captions:
        similarity = calculate_similarity_score(new_caption, existing_caption)
        if similarity > similarity_threshold:
            log.info(f" Caption similarity detected: {similarity:.2f}")
            return False
    return True

def generate_unique_caption(prompt, existing_captions, max_attempts=None):
    if max_attempts is None:
        max_attempts = int(get_env('CAPTION_MAX_ATTEMPTS', '5'))
    """Generate a unique caption that doesn't repeat content from existing captions"""
    log.info(f" Generating unique caption for: {prompt[:50]}...")
    
    for attempt in range(max_attempts):
        caption_prompt = CAPTION_TEMPLATE.format(prompt=prompt)
        response = call_llm(caption_prompt, CAPTION_SYSTEM)
        
        if response:
            # Clean the response to remove AI-generated text
            lines = []
            for line in response.split('\n'):
                line = line.strip()
                if line and not any(ai_text in line.lower() for ai_text in [
                    "here is a", "caption that meets", "requirements:", "ai generated", 
                    "artificial intelligence", "generated by", "created by ai", "architectural analysis",
                    "poetic approach", "requirements", "write the", "caption now"
                ]):
                    lines.append(line)
            
            # Ensure exactly configured number of lines
            caption_line_count = int(get_env('CAPTION_LINE_COUNT', '6'))
            if len(lines) >= caption_line_count:
                result = '\n'.join(lines[:caption_line_count])
            else:
                # Pad with sophisticated lines if needed
                while len(lines) < caption_line_count:
                    lines.append("Architecture speaks through silent spaces")
                result = '\n'.join(lines[:caption_line_count])
            
            # Check if this caption is unique
            if is_caption_unique(result, existing_captions):
                log.info(f" Generated unique caption (attempt {attempt + 1}): {result[:50]}...")
                return result
            else:
                log.info(f" Caption too similar, retrying (attempt {attempt + 1}/{max_attempts})")
                # Add variety to the prompt for next attempt
                prompt += f" [Variation {attempt + 1}: Focus on different aspects]"
        else:
            log.warning(f" Failed to generate caption on attempt {attempt + 1}")
    
    # If all attempts failed, generate a completely different fallback
    log.warning(" Using unique fallback caption")
    fallback_captions = [
        "Silent spaces whisper architectural secrets\nForm emerges from functional necessity\nLight sculpts geometric boundaries\nHuman scale defines monumental vision\nMaterials narrate stories of creation\nSpace transforms into poetic motion",
        "Architectural dreams materialize in concrete\nFunction follows form in perfect balance\nShadows dance across structural surfaces\nMonumental vision meets human intimacy\nCreation stories etched in materials\nPoetry flows through spatial boundaries",
        "Concrete dreams take architectural form\nBalance achieved through functional harmony\nSurfaces reflect structural light patterns\nIntimate spaces within monumental scale\nMaterials bear witness to creation\nBoundaries dissolve into spatial poetry",
        "Architectural visions crystallize in space\nHarmony emerges from functional design\nLight patterns illuminate structural forms\nScale balances monumentality with intimacy\nCreation narratives embedded in materials\nPoetry manifests through spatial design",
        "Space becomes architectural reality\nDesign harmonizes function with beauty\nForms emerge from light and shadow\nIntimacy coexists with grandeur\nMaterials speak of creative vision\nSpatial poetry transcends boundaries"
    ]
    
    # Choose a fallback that's different from existing captions
    for fallback in fallback_captions:
        if is_caption_unique(fallback, existing_captions):
            return fallback
    
    # If all fallbacks are similar, modify one slightly
    return fallback_captions[0].replace("Architectural", "Structural").replace("spaces", "volumes")

def generate_caption(prompt):
    """Legacy function - now calls generate_unique_caption with empty existing_captions"""
    return generate_unique_caption(prompt, [])

# ===  Image Generation ===
async def generate_single_image_async(session, prompt, style_name, image_number, semaphore=None):
    """Async version of generate_single_image with semaphore for rate limiting"""
    if semaphore:
        async with semaphore:
            return await _generate_single_image_async_internal(session, prompt, style_name, image_number)
    else:
        return await _generate_single_image_async_internal(session, prompt, style_name, image_number)

async def _generate_single_image_async_internal(session, prompt, style_name, image_number):
    """Internal async image generation implementation"""
    log.info(f" Generating {style_name} image {image_number}")
    
    style_dir = os.path.join("images", style_name)
    os.makedirs(style_dir, exist_ok=True)
    
    # Get enhanced style configuration with sophisticated prompts
    style_config = STYLE_CONFIG.get(style_name, {
        'model': 'black-forest-labs/FLUX.1-schnell-free',
        'prompt_suffix': f', {style_name} architectural style, sophisticated design, artistic composition, professional photography, high quality, detailed materials, perfect lighting, architectural beauty, structural elegance, spatial harmony, material expression, environmental integration, human scale consideration, cultural significance, technical precision, aesthetic excellence',
        'negative_prompt': 'blurry, low quality, distorted, amateur, unrealistic, poor composition, bad lighting, ugly, disorganized, messy, unprofessional, cartoon, painting, sketch, drawing, text, watermark, signature'
    })
    
    full_prompt = f"{prompt}{style_config['prompt_suffix']}"
    negative_prompt = style_config['negative_prompt']
    
    together_api_url = f"{Config.API['base_url']}/images/generations"
    
    payload = {
        "model": style_config['model'],
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
        "width": Config.IMAGE["width"],
        "height": Config.IMAGE["height"],
        "steps": int(get_env('INFERENCE_STEPS', '4')),
        "guidance_scale": float(get_env('GUIDANCE_SCALE', '7.5')),
        "seed": random.randint(1, 1000000)
    }
    
    headers = {
        "Authorization": f"Bearer {Config.API['together_key']}",
        "Content-Type": "application/json"
    }
    
    max_retries = Config.LIMITS['max_retries']
    retry_delays = [int(x.strip()) for x in get_env('IMAGE_RETRY_DELAYS', '60,120,180').split(',')]
    
    for attempt in range(max_retries):
        try:
            log.info(f" Attempt {attempt + 1}/{max_retries} for {style_name} image {image_number}")
            
            async with session.post(
                together_api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=Config.LIMITS['api_timeout'])
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and len(data['data']) > 0:
                        image_data = data['data'][0]
                        if 'url' in image_data:
                            image_url = image_data['url']
                            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=60)) as image_response:
                                if image_response.status == 200:
                                    image_content = await image_response.read()
                                    
                                    # Lazy import for image processing
                                    
                                    # Load image and apply DPI-aware preprocessing
                                    img = Image.open(io.BytesIO(image_content))
                                    
                                    # Get DPI setting from environment
                                    dpi = Config.PDF["dpi"]
                                    
                                    # Calculate new dimensions based on DPI (72 DPI is standard screen resolution)
                                    # Formula: new_size = original_size * (target_dpi / 72)
                                    new_width = int(img.width * dpi / 72)
                                    new_height = int(img.height * dpi / 72)
                                    
                                    # Resize image for high-quality PDF output
                                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                    
                                    # Log DPI processing information
                                    log_dpi_processing_info((img.width, img.height), dpi, (new_width, new_height))
                                    
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    image_filename = f"{timestamp}_{image_number:02d}_{style_name}.jpg"
                                    image_path = os.path.join(style_dir, image_filename)
                                    
                                    # Save with high quality
                                    image_quality = int(get_env("IMAGE_QUALITY", "95"))
                                    img.save(image_path, 'JPEG', quality=image_quality, dpi=(dpi, dpi))
                                    
                                    log.info(f" Generated {style_name} image {image_number}: {image_filename}")
                                    await asyncio.sleep(Config.LIMITS['rate_limit_delay'])
                                    return image_path
                                else:
                                    log.error(f" Failed to download image from {image_url} (HTTP {image_response.status})")
                        else:
                            log.error(f" No image URL in response for {style_name} image {image_number}")
                    else:
                        log.error(f" Invalid response structure for {style_name} image {image_number}")
                elif response.status == 429:  # Rate limited
                    delay = retry_delays[min(attempt, len(retry_delays)-1)]
                    log.warning(f" Rate limited (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                elif response.status in [502, 503]:  # Service unavailable/Bad gateway
                    delay = retry_delays[min(attempt, len(retry_delays)-1)]
                    log.warning(f" Service error {response.status} (attempt {attempt+1}/{max_retries}), waiting {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    log.error(f" Image generation failed with HTTP {response.status}")
                    if attempt == max_retries - 1:
                        return None
                    await asyncio.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
                    continue
                    
        except asyncio.TimeoutError:
            log.warning(f" Image generation timeout (attempt {attempt+1}/{max_retries})")
            if attempt == max_retries - 1:
                log.error(" All image generation attempts failed due to timeout")
                return None
            await asyncio.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
            
        except Exception as e:
            log.error(f" Unexpected error in async image generation (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            await asyncio.sleep(retry_delays[min(attempt, len(retry_delays)-1)])
            continue
    
    return None

def generate_single_image(prompt, style_name, image_number):
    """Generate a single image using provider abstraction layer"""
    log.info(f" Generating {style_name} image {image_number}")
    
    style_dir = os.path.join("images", style_name)
    os.makedirs(style_dir, exist_ok=True)
    
    # Get enhanced style configuration with sophisticated prompts
    style_config = STYLE_CONFIG.get(style_name, {
        'model': 'black-forest-labs/FLUX.1-schnell-free',  # Use free model as default
        'prompt_suffix': f', {style_name} architectural style, sophisticated design, artistic composition, professional photography, high quality, detailed materials, perfect lighting, architectural beauty, structural elegance, spatial harmony, material expression, environmental integration, human scale consideration, cultural significance, technical precision, aesthetic excellence',
        'negative_prompt': 'blurry, low quality, distorted, amateur, unrealistic, poor composition, bad lighting, ugly, disorganized, messy, unprofessional, cartoon, painting, sketch, drawing, text, watermark, signature'
    })
    
    full_prompt = f"{prompt}{style_config['prompt_suffix']}"
    
    # Use provider abstraction layer
    image_content = get_image_response(full_prompt, style_config)
    
    if image_content:
        # Lazy import for image processing
        
        # Load image and apply DPI-aware preprocessing
        img = Image.open(io.BytesIO(image_content))
        
        # Get DPI setting from environment
        dpi = Config.PDF["dpi"]
        
        # Calculate new dimensions based on DPI (72 DPI is standard screen resolution)
        # Formula: new_size = original_size * (target_dpi / 72)
        new_width = int(img.width * dpi / 72)
        new_height = int(img.height * dpi / 72)
        
        # Resize image for high-quality PDF output
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Log DPI processing information
        log_dpi_processing_info((img.width, img.height), dpi, (new_width, new_height))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{timestamp}_{image_number:02d}_{style_name}.jpg"
        image_path = os.path.join(style_dir, image_filename)
        
        # Save with high quality
        image_quality = int(get_env("IMAGE_QUALITY", "95"))
        img.save(image_path, 'JPEG', quality=image_quality, dpi=(dpi, dpi))
        
        log.info(f" Generated {style_name} image {image_number}: {image_filename}")
        time.sleep(Config.LIMITS['rate_limit_delay'])  # Configurable rate limiting
        return image_path
    
    log.error(f" Failed to generate {style_name} image {image_number}")
    return None

async def generate_all_images_async(prompts, style_name):
    """Async version of generate_all_images with semaphore-based rate limiting"""
    log.info(f" Starting async batch generation of {len(prompts)} images for {style_name} style")
    
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(Config.LIMITS['max_concurrent_images'])
    
    # Pre-create style directory for all images
    style_dir = Path("images") / style_name
    style_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_image_with_index(session, i, prompt):
        try:
            # Check if image already exists (for resume functionality)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{timestamp}_{i+1:02d}_{style_name}.jpg"
            image_path = style_dir / image_filename
            
            # Skip if already exists
            if image_path.exists():
                log.debug(f" Using existing image: {image_filename}")
                return i, str(image_path), None
            
            result_path = await generate_single_image_async(session, prompt, style_name, i+1, semaphore)
            return i, result_path, None
        except Exception as e:
            return i, None, str(e)
    
    # Process in batches for better memory management
    batch_size = int(get_env('BATCH_SIZE', '25')) if BATCH_PROCESSING else len(prompts)
    
    images = []
    
    # Create aiohttp session
    timeout = aiohttp.ClientTimeout(total=Config.LIMITS['api_timeout'])
    connector = aiohttp.TCPConnector(limit=Config.LIMITS['max_concurrent_images'] * 2)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        with tqdm(total=len(prompts), desc=f" Generating {style_name} images", unit="image") as pbar:
            for batch_start in range(0, len(prompts), batch_size):
                batch_end = min(batch_start + batch_size, len(prompts))
                batch_prompts = prompts[batch_start:batch_end]
                
                # Create tasks for batch
                tasks = [
                    generate_image_with_index(session, i, prompt)
                    for i, prompt in enumerate(batch_prompts, batch_start)
                ]
                
                # Execute batch tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        log.error(f" Task failed with exception: {result}")
                        pbar.update(1)
                        continue
                    
                    i, image_path, error = result
                    
                    if image_path:
                        images.append(image_path)
                        pbar.set_postfix_str(f" {os.path.basename(image_path)}")
                    else:
                        log.warning(f" Failed to generate image {i+1}: {error}")
                        pbar.set_postfix_str(f" Failed")
                    
                    pbar.update(1)
                
                # Memory optimization between batches
                if OPTIMIZE_MEMORY:
                    gc.collect()
    
    success_rate = (len(images) / len(prompts)) * 100
    log.info(f" Async batch image generation complete: {len(images)}/{len(prompts)} images generated ({success_rate:.1f}% success rate)")
    
    return images

def generate_all_images(prompts, style_name):
    """Generate all images with batch processing and concurrent execution for 100x speed"""
    log.info(f" Starting batch concurrent generation of {len(prompts)} images for {style_name} style")
    
    images = []
    max_workers = MAX_CONCURRENT_IMAGES
    
    # Pre-create style directory for all images
    style_dir = Path("images") / style_name
    style_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_image_with_index(args):
        i, prompt = args
        try:
            # Check if image already exists (for resume functionality)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{timestamp}_{i+1:02d}_{style_name}.jpg"
            image_path = style_dir / image_filename
            
            # Skip if already exists
            if image_path.exists():
                log.debug(f" Using existing image: {image_filename}")
                return i, str(image_path), None
            
            result_path = generate_single_image(prompt, style_name, i+1)
            return i, result_path, None
        except Exception as e:
            return i, None, str(e)
    
    # Process in batches for better memory management
    batch_size = int(get_env('BATCH_SIZE', '25')) if BATCH_PROCESSING else len(prompts)
    
    with tqdm(total=len(prompts), desc=f" Generating {style_name} images", unit="image") as pbar:
        for batch_start in range(0, len(prompts), batch_size):
            batch_end = min(batch_start + batch_size, len(prompts))
            batch_prompts = prompts[batch_start:batch_end]
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit batch tasks
                future_to_index = {
                    executor.submit(generate_image_with_index, (i, prompt)): i 
                    for i, prompt in enumerate(batch_prompts, batch_start)
                }
                
                # Process completed batch tasks
                for future in as_completed(future_to_index):
                    i, image_path, error = future.result()
                    
                    if image_path:
                        images.append(image_path)
                        pbar.set_postfix_str(f" {os.path.basename(image_path)}")
                    else:
                        log.warning(f" Failed to generate image {i+1}: {error}")
                        pbar.set_postfix_str(f" Failed")
                    
                    pbar.update(1)
            
            # Memory optimization between batches
            if OPTIMIZE_MEMORY:
                gc.collect()
    
    success_rate = (len(images) / len(prompts)) * 100
    log.info(f" Batch image generation complete: {len(images)}/{len(prompts)} images generated ({success_rate:.1f}% success rate)")
    
    return images

# ===  Caption Generation ===
async def generate_all_captions_async(prompts):
    """Async version of generate_all_captions with semaphore-based rate limiting"""
    log.info(f" Starting async cached caption generation for {len(prompts)} prompts")
    
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(Config.LIMITS['max_concurrent_captions'])
    
    captions = [None] * len(prompts)  # Pre-allocate list
    
    async def generate_caption_with_index(session, i, prompt):
        try:
            # Create cache key for this prompt
            cache_key = f"caption_{hashlib.md5(prompt.encode()).hexdigest()}"
            
            # Try to load from cache first
            cached_caption = load_from_cache(cache_key, max_age_hours=24)
            if cached_caption:
                log.debug(f" Using cached caption for prompt: {prompt[:30]}...")
                return i, cached_caption, None
            
            if not CAPTION_DEDUPLICATION:
                # Fast mode: skip deduplication
                caption = await call_llm_async(session, prompt, CAPTION_SYSTEM, semaphore)
            else:
                # Normal mode: ensure uniqueness
                existing_captions = [c for c in captions if c is not None]
                caption = await generate_unique_caption_async(session, prompt, existing_captions, semaphore)
            
            # Save to cache
            save_to_cache(cache_key, caption)
            
            return i, caption, None
        except Exception as e:
            return i, None, str(e)
    
    # Process in batches for better memory management
    batch_size = int(get_env('BATCH_SIZE', '25')) if BATCH_PROCESSING else len(prompts)
    
    # Create aiohttp session
    timeout = aiohttp.ClientTimeout(total=Config.LIMITS['api_timeout'])
    connector = aiohttp.TCPConnector(limit=Config.LIMITS['max_concurrent_captions'] * 2)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        with tqdm(total=len(prompts), desc=f" Generating captions", unit="caption") as pbar:
            for batch_start in range(0, len(prompts), batch_size):
                batch_end = min(batch_start + batch_size, len(prompts))
                batch_prompts = prompts[batch_start:batch_end]
                
                # Create tasks for batch
                tasks = [
                    generate_caption_with_index(session, i, prompt)
                    for i, prompt in enumerate(batch_prompts, batch_start)
                ]
                
                # Execute batch tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        log.error(f" Task failed with exception: {result}")
                        pbar.update(1)
                        continue
                    
                    i, caption, error = result
                    
                    if caption:
                        captions[i] = caption
                        pbar.set_postfix_str(f" Caption {i+1}")
                    else:
                        log.warning(f" Failed to generate caption {i+1}: {error}")
                        pbar.set_postfix_str(f" Failed")
                    
                    pbar.update(1)
                
                # Memory optimization between batches
                if OPTIMIZE_MEMORY:
                    gc.collect()
    
    # Filter out None values
    captions = [c for c in captions if c is not None]
    log.info(f" Generated {len(captions)} captions with async caching")
    return captions

async def generate_unique_caption_async(session, prompt, existing_captions, semaphore=None):
    """Async version of generate_unique_caption"""
    log.info(f" Generating unique caption for: {prompt[:50]}...")
    
    max_attempts = int(get_env('CAPTION_MAX_ATTEMPTS', '5'))
    
    for attempt in range(max_attempts):
        caption_prompt = CAPTION_TEMPLATE.format(prompt=prompt)
        response = await call_llm_async(session, caption_prompt, CAPTION_SYSTEM, semaphore)
        
        if response:
            # Clean the response to remove AI-generated text
            lines = []
            for line in response.split('\n'):
                line = line.strip()
                if line and not any(ai_text in line.lower() for ai_text in [
                    "here is a", "caption that meets", "requirements:", "ai generated", 
                    "artificial intelligence", "generated by", "created by ai", "architectural analysis",
                    "poetic approach", "requirements", "write the", "caption now"
                ]):
                    lines.append(line)
            
            # Ensure exactly configured number of lines
            caption_line_count = Config.CAPTION['line_count']
            if len(lines) >= caption_line_count:
                result = '\n'.join(lines[:caption_line_count])
            else:
                # Pad with sophisticated lines if needed
                while len(lines) < caption_line_count:
                    lines.append("Architecture speaks through silent spaces")
                result = '\n'.join(lines[:caption_line_count])
            
            # Check if this caption is unique
            if is_caption_unique(result, existing_captions):
                log.info(f" Generated unique caption (attempt {attempt + 1}): {result[:50]}...")
                return result
            else:
                log.info(f" Caption too similar, retrying (attempt {attempt + 1}/{max_attempts})")
                # Add variety to the prompt for next attempt
                prompt += f" [Variation {attempt + 1}: Focus on different aspects]"
        else:
            log.warning(f" Failed to generate caption on attempt {attempt + 1}")
    
    # If all attempts failed, generate a completely different fallback
    log.warning(" Using unique fallback caption")
    fallback_captions = [
        "Silent spaces whisper architectural secrets\nForm emerges from functional necessity\nLight sculpts geometric boundaries\nHuman scale defines monumental vision\nMaterials narrate stories of creation\nSpace transforms into poetic motion",
        "Architectural dreams materialize in concrete\nFunction follows form in perfect balance\nShadows dance across structural surfaces\nMonumental vision meets human intimacy\nCreation stories etched in materials\nPoetry flows through spatial boundaries",
        "Concrete dreams take architectural form\nBalance achieved through functional harmony\nSurfaces reflect structural light patterns\nIntimate spaces within monumental scale\nMaterials bear witness to creation\nBoundaries dissolve into spatial poetry",
        "Architectural visions crystallize in space\nHarmony emerges from functional design\nLight patterns illuminate structural forms\nScale balances monumentality with intimacy\nCreation narratives embedded in materials\nPoetry manifests through spatial design",
        "Space becomes architectural reality\nDesign harmonizes function with beauty\nForms emerge from light and shadow\nIntimacy coexists with grandeur\nMaterials speak of creative vision\nSpatial poetry transcends boundaries"
    ]
    
    # Choose a fallback that's different from existing captions
    for fallback in fallback_captions:
        if is_caption_unique(fallback, existing_captions):
            return fallback
    
    # If all fallbacks are similar, modify one slightly
    return fallback_captions[0].replace("Architectural", "Structural").replace("spaces", "volumes")

def generate_all_captions(prompts):
    """Generate captions with caching and concurrent processing for 100x speed"""
    log.info(f" Starting cached concurrent caption generation for {len(prompts)} prompts")
    
    captions = [None] * len(prompts)  # Pre-allocate list
    max_workers = MAX_CONCURRENT_CAPTIONS
    
    def generate_caption_with_index(args):
        i, prompt = args
        try:
            # Create cache key for this prompt
            cache_key = f"caption_{hashlib.md5(prompt.encode()).hexdigest()}"
            
            # Try to load from cache first
            cached_caption = load_from_cache(cache_key, max_age_hours=24)
            if cached_caption:
                log.debug(f" Using cached caption for prompt: {prompt[:30]}...")
                return i, cached_caption, None
            
            if not CAPTION_DEDUPLICATION:
                # Fast mode: skip deduplication
                caption = generate_caption(prompt)
            else:
                # Normal mode: ensure uniqueness
                existing_captions = [c for c in captions if c is not None]
                caption = generate_unique_caption(prompt, existing_captions)
            
            # Save to cache
            save_to_cache(cache_key, caption)
            
            return i, caption, None
        except Exception as e:
            return i, None, str(e)
    
    # Process in batches for better memory management
    batch_size = int(get_env('BATCH_SIZE', '25')) if BATCH_PROCESSING else len(prompts)
    
    with tqdm(total=len(prompts), desc=f" Generating captions", unit="caption") as pbar:
        for batch_start in range(0, len(prompts), batch_size):
            batch_end = min(batch_start + batch_size, len(prompts))
            batch_prompts = prompts[batch_start:batch_end]
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit batch tasks
                future_to_index = {
                    executor.submit(generate_caption_with_index, (i, prompt)): i 
                    for i, prompt in enumerate(batch_prompts, batch_start)
                }
                
                # Process completed batch tasks
                for future in as_completed(future_to_index):
                    i, caption, error = future.result()
                    
                    if caption:
                        captions[i] = caption
                        pbar.set_postfix_str(f" Caption {i+1}")
                    else:
                        log.warning(f" Failed to generate caption {i+1}: {error}")
                        pbar.set_postfix_str(f" Failed")
                    
                    pbar.update(1)
            
            # Memory optimization between batches
            if OPTIMIZE_MEMORY:
                gc.collect()
    
    # Filter out None values
    captions = [c for c in captions if c is not None]
    log.info(f" Generated {len(captions)} captions with caching")
    return captions

# ===  PDF Generation ===
def place_caption_with_white_band(c, caption, w, h, page_num):
    """
    Draw a white band at the bottom of the page with increased top padding,
    overlay the caption (center-aligned) and page number (right-aligned).
    The band has extra padding to separate it from the image boundary.
    """
    text = caption.split('\n')
    font_size = int(get_env('PDF_FONT_SIZE', '14'))
    line_spacing = int(get_env('PDF_LINE_SPACING', '18'))
    padding_x = int(get_env('PDF_PADDING_X', '24'))
    padding_y = int(get_env('PDF_PADDING_Y', '16'))
    top_padding = int(get_env('PDF_TOP_PADDING', '40'))  # Increased top padding for better separation from image

    # Calculate text dimensions
    c.setFont("Helvetica-Bold", font_size)
    text_width = max(c.stringWidth(line, "Helvetica-Bold", font_size) for line in text)
    text_height = len(text) * line_spacing

    band_height = text_height + 2 * padding_y + top_padding
    band_y = int(get_env('PDF_BAND_Y', '0'))  # flush with the bottom of the page
    band_x = int(get_env('PDF_BAND_X', '0'))
    band_width = w

    # Draw white band
    c.setFillColorRGB(1, 1, 1)
    c.rect(band_x, band_y, band_width, band_height, fill=1, stroke=0)

    # Draw caption (center-aligned, positioned above the bottom padding)
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColorRGB(0, 0, 0)
    for i, line in enumerate(text):
        y = band_y + band_height - padding_y - top_padding - (len(text) - i - 1) * line_spacing
        c.drawCentredString(band_x + band_width/2, y, line)

    # Draw page number (right-aligned, at the bottom of the white band, bold)
    page_str = str(page_num)
    c.setFont("Helvetica-Bold", font_size)
    c.drawRightString(band_x + band_width - padding_x, band_y + padding_y, page_str)

def create_daily_pdf(images, captions, style_name, theme):
    """Create the daily PDF with all images and captions"""
    # Lazy import for PDF generation
    
    if not images:
        log.error(" No images provided for PDF creation")
        return None
    
    # Create output directory
    output_dir = Config.PDF["output_dir"]
    os.makedirs(output_dir, exist_ok=True)
    
    # Create sequential title and PDF filename
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday
    year = today.year
    sequential_title = f"ASK Daily Architectural Research Zine - Volume {year}.{day_of_year:03d}"
    
    # Updated PDF naming convention
    pdf_filename = f"ASK_Daily_Architectural_Research_Zine-{year}-VOL-{day_of_year:03d}-{style_name.capitalize()}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    log.info(f" Creating PDF: {pdf_filename}")
    log.info(f" Images to include: {len(images)}")
    
    # Create PDF
    # Use Trade Paperback format (6" x 9")
    page_size = get_env('PDF_PAGE_SIZE', 'TRADE_PAPERBACK')
    if page_size == 'TRADE_PAPERBACK':
        # Trade Paperback: 6" x 9" (432 x 648 points)
        pagesize = (432, 648)
    elif page_size == 'A4':
        pagesize = A4
    else:
        pagesize = letter  # Default fallback
    
    c = canvas.Canvas(pdf_path, pagesize=pagesize)
    w, h = pagesize
    
    page_count = 0
    
    # Add front cover page
    c.setFont("Helvetica-BoldOblique", 42)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(w/2, h/2 + 140, "ASK")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2, h/2 + 80, "DAILY ARCHITECTURAL")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2, h/2 + 50, "RESEARCH ZINE")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(w/2, h/2 + 10, f"Volume {year}.{day_of_year:03d}")
    c.setFont("Helvetica", 16)
    c.drawCentredString(w/2, h/2 - 30, f"{datetime.now().strftime('%B %d, %Y')}")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h/2 - 70, f"{style_name.capitalize()} Edition")
    c.setFont("Helvetica", 14)
    c.drawCentredString(w/2, h/2 - 110, f"50 Full-Bleed Architectural Images")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w/2, h/2 - 150, f"Theme: {theme}")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h/2 - 190, "Architectural Research & Poetry")
    c.setFont("Helvetica", 8)
    c.drawCentredString(w/2, h/2 - 220, "Daily Collection of Architectural Vision")
    c.showPage()
    page_count += 1
    
    # Add images with captions
    with tqdm(total=len(images), desc=f" Creating PDF pages", unit="page",
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
        
        for i, (image_path, caption) in enumerate(zip(images, captions)):
            pbar.set_description(f" Adding page {i+1}/{len(images)}")
            try:
                # Calculate white band dimensions first
                text = caption.split('\n')
                font_size = int(get_env('PDF_FONT_SIZE', '14'))
                line_spacing = int(get_env('PDF_LINE_SPACING', '18'))
                padding_y = int(get_env('PDF_PADDING_Y', '16'))
                top_padding = int(get_env('PDF_TOP_PADDING', '40'))
                
                # Calculate band height
                text_height = len(text) * line_spacing
                band_height = text_height + 2 * padding_y + top_padding
                
                # Calculate image dimensions to fit above the white band
                image_height = h - band_height
                image_width = w
                
                # Add image above the white band (centered)
                c.drawImage(image_path, 0, band_height, width=image_width, height=image_height)
                
                # Add caption with white band and page number
                place_caption_with_white_band(c, caption, w, h, i + 1)
                
                c.showPage()
                page_count += 1
                pbar.set_postfix_str(f" Success")
                
            except Exception as e:
                pbar.set_postfix_str(f" Error")
                log.error(f" Error adding image {i+1}: {e}")
            
            pbar.update(1)
    
    # Add back cover page
    c.setFont("Helvetica-BoldOblique", 24)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(w/2, h/2 + 100, "ASK")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h/2 + 50, "DAILY ARCHITECTURAL")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h/2 + 20, "RESEARCH ZINE")
    c.setFont("Helvetica", 14)
    c.drawCentredString(w/2, h/2 - 20, f"Volume {year}.{day_of_year:03d}")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w/2, h/2 - 50, f"{style_name.capitalize()} Edition")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h/2 - 80, f"Theme: {theme}")
    c.setFont("Helvetica", 8)
    c.drawCentredString(w/2, h/2 - 120, "50 Full-Bleed Architectural Images")
    c.drawCentredString(w/2, h/2 - 140, "Architectural Research & Poetry")
    c.drawCentredString(w/2, h/2 - 160, "Daily Collection of Architectural Vision")
    c.showPage()
    page_count += 1
    
    c.save()
    
    log.info(f" Daily PDF created successfully!")
    log.info(f" File: {pdf_path}")
    log.info(f" Pages: {page_count}")
    log.info(f" Size: {os.path.getsize(pdf_path)} bytes")
    
    return pdf_path

# ===  Main Function ===
def main():
    """Main function to run the daily zine generation with Free Tier Optimized settings"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Daily Zine Generator - Free Tier Optimized')
    parser.add_argument('--test', action='store_true', help='Run in test mode with fewer images')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--images', type=int, default=50, help='Number of images to generate (default: 50)')
    parser.add_argument('--style', type=str, help='Force specific style (e.g., technical, abstract)')
    parser.add_argument('--theme', type=str, help='Force specific theme instead of web scraping')
    parser.add_argument('--sources', action='store_true', help='Display current architectural sources')
    parser.add_argument('--add-source', nargs=3, metavar=('NAME', 'URL', 'CATEGORY'), help='Add a single source manually')
    parser.add_argument('--remove-source', type=str, help='Remove a source by name')
    parser.add_argument('--batch-sources', action='store_true', help='Add batch of predefined sources')
    parser.add_argument('--discover-sources', action='store_true', help='Run daily source discovery')
    parser.add_argument('--discovery-stats', action='store_true', help='Show daily discovery statistics')
    parser.add_argument('--fast', action='store_true', help='Enable fast mode (Free Tier Optimized)')
    parser.add_argument('--ultra', action='store_true', help='Enable ultra mode (Conservative Free Tier Optimization)')
    parser.add_argument('--convert-pdf', action='store_true', help='Convert latest PDF to Instagram images')
    parser.add_argument('--pdf-path', type=str, help='Specific PDF path for conversion')
    parser.add_argument('--instagram-posts', action='store_true', help='Convert to Instagram posts (square format)')
    parser.add_argument('--instagram-stories', action='store_true', help='Convert to Instagram stories (9:16 format)')
    parser.add_argument('--both-formats', action='store_true', help='Convert to both posts and stories')

    
    parser.add_argument('--async-mode', action='store_true', help='Use async processing for better performance')
    parser.add_argument('--migrate-cache', action='store_true', help='Migrate existing cache to gzip compression')
    parser.add_argument('--list-styles', action='store_true', help='List all available architectural styles')
    
    args = parser.parse_args()
    
    # Set debug level if requested (overrides environment setting)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        log.debug(" Debug mode enabled via command line argument")
    
    # Declare global variables that might be modified
    global CAPTION_DEDUPLICATION, RATE_LIMIT_DELAY, MAX_CONCURRENT_IMAGES, MAX_CONCURRENT_CAPTIONS
    
    # Override settings for fast mode (Sequential Processing)
    if args.fast:
        CAPTION_DEDUPLICATION = False
        RATE_LIMIT_DELAY = Config.LIMITS["rate_limit_delay"]
    
    # Override settings for ultra mode (Sequential Processing)
    if args.ultra:
        CAPTION_DEDUPLICATION = False
        RATE_LIMIT_DELAY = Config.LIMITS["rate_limit_delay"]
        MAX_CONCURRENT_IMAGES = Config.MODES["ultra_concurrent_images"]
        MAX_CONCURRENT_CAPTIONS = Config.MODES["ultra_concurrent_captions"]
    
    # Handle sources management
    if args.sources:
        log.info(" Displaying architectural sources...")
        display_manual_sources()
        return
    
    # Handle manual source addition
    if args.add_source:
        name, url, category = args.add_source
        add_manual_source(name, url, category)
        return
    
    # Handle source removal
    if args.remove_source:
        remove_manual_source(args.remove_source)
        return
    
    # Handle batch source addition
    if args.batch_sources:
        add_batch_manual_sources()
        return
    
    # Handle source discovery
    if args.discover_sources:
        log.info(" Running architectural source discovery...")
        run_daily_source_discovery()
        return
    
    # Handle discovery statistics
    if args.discovery_stats:
        log.info(" Daily discovery statistics...")
        try:
            discoverer = ArchitecturalSourceDiscoverer()
            stats = discoverer.get_daily_discovery_stats()
            
            if stats['total_discovered'] > 0:
                log.info(f" Today's discoveries: {stats['total_discovered']} sources")
                for category, count in stats['categories'].items():
                    log.info(f"   • {category}: {count} sources")
            else:
                log.info("ℹ No discoveries today")
        except Exception as e:
            log.error(f" Error getting discovery stats: {e}")
        return
    
    # Handle cache migration
    if args.migrate_cache:
        log.info(" Manual cache migration requested...")
        migrate_cache_to_compression()
        return
    
    # Handle style listing
    if args.list_styles:
        log.info(" Available Architectural Styles")
        log.info("=" * 50)
        styles = get_available_styles()
        for i, style in enumerate(styles, 1):
            log.info(f"{i:2d}. {style}")
        log.info(f"\n Total styles: {len(styles)}")
        return
    
    # Handle PDF to Instagram conversion
    if args.convert_pdf or args.instagram_posts or args.instagram_stories or args.both_formats:
        log.info(" Converting PDF to Instagram images...")
        
        if args.pdf_path:
            pdf_path = Path(args.pdf_path)
            if not pdf_path.exists():
                log.error(f" PDF file not found: {pdf_path}")
                return
        else:
            pdf_path = get_latest_pdf()
            if not pdf_path:
                return
        
        if args.instagram_posts or args.both_formats:
            posts = convert_pdf_to_instagram_images(pdf_path)
            if posts:
                log.info(f" Converted to {len(posts)} Instagram posts")
        
        if args.instagram_stories or args.both_formats:
            stories = create_instagram_story_images(pdf_path)
            if stories:
                log.info(f" Converted to {len(stories)} Instagram stories")
        
        if not args.instagram_posts and not args.instagram_stories and not args.both_formats:
            # Default: convert to both formats
            posts, stories = convert_latest_pdf_to_instagram()
            if posts:
                log.info(f" Converted to {len(posts)} Instagram posts")
            if stories:
                log.info(f" Converted to {len(stories)} Instagram stories")
        
        return
    

    


    log.info(" Starting Daily Zine Generator - Free Tier Optimized")
    
    log.info(f" Concurrent Images: {MAX_CONCURRENT_IMAGES}")
    log.info(f" Concurrent Captions: {MAX_CONCURRENT_CAPTIONS}")
    log.info(f"⏱ Rate Limit Delay: {RATE_LIMIT_DELAY}s")
    log.info(f" Caption Deduplication: {CAPTION_DEDUPLICATION}")
    log.info(" Pipeline: Web Scraping → Style Selection → Prompt Generation → Image Generation → Caption Generation → PDF Creation")
    log.info(" Free Tier Limit: ~100 requests/minute - Conservative optimization for Together.ai free tier")
    
    # Run weekly cache optimization if scheduled (every Sunday)
    run_scheduled_cache_optimization()
    
    # Start timing
    start_time = time.time()
    
    # Overall pipeline progress bar
    with tqdm(total=6, desc=f" Overall Pipeline Progress", unit="step",
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pipeline_pbar:
        
        # Step 1: Scrape web for architectural content or use provided theme
        log.info("=" * 60)
        log.info(" STEP 1/6: Scraping web for architectural content")
        log.info("=" * 60)
        pipeline_pbar.set_description(f" Step 1/6: Web Scraping")
        
        if args.theme:
            theme = args.theme
            log.info(f" Using provided theme: {theme}")
        else:
            theme = scrape_architectural_content()
            log.info(f" Theme selected: {theme}")
        
        pipeline_pbar.set_postfix_str(f" Theme: {theme[:30]}...")
        pipeline_pbar.update(1)
        time.sleep(2)  # Rate limiting between major steps
        
        # Step 2: Select daily style
        log.info("=" * 60)
        log.info(" STEP 2/6: Selecting daily style")
        log.info("=" * 60)
        pipeline_pbar.set_description(f" Step 2/6: Style Selection")
        
        if args.style:
            style_name = args.style.lower()
            # Validate provided style
            if not validate_style(style_name):
                log.warning(f" Invalid style '{style_name}', using 'technical' as fallback")
                style_name = "technical"
            log.info(f" Using provided style: {style_name.upper()}")
        else:
            style_name = get_daily_style()
            log.info(f" Selected style: {style_name.upper()}")
        
        pipeline_pbar.set_postfix_str(f" Style: {style_name.upper()}")
        pipeline_pbar.update(1)
        time.sleep(2)  # Rate limiting between major steps
        
        # Step 3: Generate prompts
        num_prompts = int(get_env('TEST_IMAGE_COUNT', '5')) if args.test else args.images
        log.info("=" * 60)
        log.info(f" STEP 3/6: Generating {num_prompts} prompts")
        log.info("=" * 60)
        pipeline_pbar.set_description(f" Step 3/6: Prompt Generation")
        prompts = generate_prompts(theme, num_prompts)
        if not prompts:
            log.error(" Failed to generate prompts")
            return
        log.info(f" Generated {len(prompts)} prompts")
        pipeline_pbar.set_postfix_str(f" {len(prompts)} prompts")
        pipeline_pbar.update(1)
        time.sleep(2)  # Rate limiting between major steps
        
        # Step 4: Generate images in one style (sequential or async)
        log.info("=" * 60)
        if args.async_mode:
            log.info(f" STEP 4/6: Generating {len(prompts)} images with async processing")
            pipeline_pbar.set_description(f" Step 4/6: Async Image Generation")
            images = asyncio.run(generate_all_images_async(prompts, style_name))
        else:
            log.info(f" STEP 4/6: Generating {len(prompts)} images sequentially")
            pipeline_pbar.set_description(f" Step 4/6: Image Generation")
            images = generate_all_images(prompts, style_name)
        
        if not images:
            log.error(" Failed to generate images")
            return
        log.info(f" Generated {len(images)} images")
        pipeline_pbar.set_postfix_str(f" {len(images)} images")
        pipeline_pbar.update(1)
        time.sleep(2)  # Rate limiting between major steps
        
        # Step 5: Generate captions (sequential or async)
        log.info("=" * 60)
        if args.async_mode:
            log.info(" STEP 5/6: Generating captions with async processing")
            pipeline_pbar.set_description(f" Step 5/6: Async Caption Generation")
            captions = asyncio.run(generate_all_captions_async(prompts))
        else:
            log.info(" STEP 5/6: Generating captions sequentially")
            pipeline_pbar.set_description(f" Step 5/6: Caption Generation")
            captions = generate_all_captions(prompts)
        
        log.info(f" Generated {len(captions)} captions")
        pipeline_pbar.set_postfix_str(f" {len(captions)} captions")
        pipeline_pbar.update(1)
        time.sleep(2)  # Rate limiting between major steps
        
        # Step 6: Create PDF
        log.info("=" * 60)
        log.info(" STEP 6/6: Creating PDF")
        log.info("=" * 60)
        pipeline_pbar.set_description(f" Step 6/6: PDF Creation")
        pdf_path = create_daily_pdf(images, captions, style_name, theme)
        pipeline_pbar.set_postfix_str(f" PDF created")
        pipeline_pbar.update(1)
        
        if pdf_path:
            # Calculate performance metrics
            total_time = time.time() - start_time
            images_per_second = len(images) / total_time if total_time > 0 else 0
            
            log.info("=" * 60)
            log.info(" 10X SPEED OPTIMIZED PIPELINE COMPLETED SUCCESSFULLY!")
            log.info("=" * 60)
            log.info(f" PDF: {pdf_path}")
            log.info(f" Style: {style_name.upper()}")
            log.info(f" Images: {len(images)}")
            log.info(f" Captions: {len(captions)}")
            log.info(f" Theme: {theme}")
            log.info(f" Total Time: {total_time:.2f} seconds")
            log.info(f" Performance: {images_per_second:.2f} images/second")
            log.info(f" Speed Improvement: ~10x faster than sequential mode")
            log.info(" All steps completed with concurrent processing!")
            



            
            # Compulsory: Convert to Instagram formats
            log.info(" Converting to Instagram formats...")
            try:
                posts = convert_pdf_to_instagram_images(pdf_path)
                log.info(f" Converted to {len(posts)} Instagram posts")
                
                stories = create_instagram_story_images(pdf_path)
                log.info(f" Converted to {len(stories)} Instagram stories")
            except Exception as e:
                log.warning(f" Instagram conversion error: {e}")
        else:
            log.error(" Failed to create daily PDF")

# ===  PDF to Instagram Conversion Functions ===
def get_latest_pdf():
    """Get the most recent PDF file from daily_pdfs directory"""
    pdf_dir = Path("daily_pdfs")
    if not pdf_dir.exists():
        log.error(" daily_pdfs directory not found")
        return None
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        log.error(" No PDF files found in daily_pdfs directory")
        return None
    
    # Get the most recent PDF
    latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
    log.info(f" Found latest PDF: {latest_pdf.name}")
    return latest_pdf

def convert_pdf_to_instagram_images(pdf_path, output_dir=None, dpi=None):
    """Convert PDF pages to Instagram-optimized PNG images"""
    # Lazy imports for image processing
    
    # Use Config defaults if not provided
    if output_dir is None:
        output_dir = f"{Config.INSTAGRAM['output_dir']}/instagram_images"
    if dpi is None:
        dpi = Config.INSTAGRAM['dpi']
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    log.info(f" Converting PDF to Instagram images...")
    log.info(f" Output directory: {output_path}")
    
    try:
        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        
        # Instagram dimensions (square format)
        instagram_square_size = int(get_env("INSTAGRAM_SQUARE_SIZE", "1080"))
        instagram_size = (instagram_square_size, instagram_square_size)  # Instagram square post
        
        converted_images = []
        
        for page_num in range(len(doc)):
            log.info(f" Processing page {page_num+1}/{len(doc)}")
            
            # Get page
            page = doc.load_page(page_num)
            
            # Calculate zoom factor for desired DPI
            zoom = dpi / 72  # PyMuPDF uses 72 DPI as base
            mat = fitz.Matrix(zoom, zoom)
            
            # Render page to image
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply DPI-aware resizing for Instagram (consistent with image generation)
            # Calculate new dimensions based on DPI: new_size = original_size * (target_dpi / 72)
            dpi_scale = dpi / 72
            dpi_width = int(img_width * dpi_scale)
            dpi_height = int(img_height * dpi_scale)
            
            # Resize image for high-quality output
            dpi_resized_image = image.resize((dpi_width, dpi_height), Image.Resampling.LANCZOS)
            
            # Resize to Instagram dimensions while maintaining aspect ratio
            img_width, img_height = dpi_resized_image.size
            scale = min(instagram_size[0] / img_width, instagram_size[1] / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image to Instagram format
            resized_image = dpi_resized_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create square canvas with white background
            square_image = Image.new('RGB', instagram_size, 'white')
            
            # Center the resized image on the square canvas
            x_offset = (instagram_size[0] - new_width) // 2
            y_offset = (instagram_size[1] - new_height) // 2
            square_image.paste(resized_image, (x_offset, y_offset))
            
            # Save as PNG
            output_filename = f"instagram_page_{page_num+1:02d}.png"
            output_file = output_path / output_filename
            image_quality = int(get_env("IMAGE_QUALITY", "95"))
            square_image.save(output_file, 'PNG', quality=image_quality)
            
            converted_images.append(str(output_file))
            log.info(f" Saved: {output_filename}")
        
        doc.close()
        log.info(f" Converted {len(converted_images)} pages to Instagram images")
        return converted_images
        
    except ImportError:
        log.error(" PyMuPDF not installed. Install with: pip install PyMuPDF")
        return None
    except Exception as e:
        log.error(f" PDF conversion failed: {e}")
        return None

def create_instagram_story_images(pdf_path, output_dir=None, dpi=None):
    """Convert PDF pages to Instagram story format (9:16 aspect ratio)"""
    # Lazy imports for image processing
    
    # Use Config defaults if not provided
    if output_dir is None:
        output_dir = f"{Config.INSTAGRAM['output_dir']}/instagram_stories"
    if dpi is None:
        dpi = Config.INSTAGRAM['dpi']
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    log.info(f" Converting PDF to Instagram stories...")
    log.info(f" Output directory: {output_path}")
    
    try:
        
        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        
        # Instagram story dimensions (9:16 aspect ratio)
        story_width = int(get_env("INSTAGRAM_STORY_WIDTH", "1080"))
        story_height = int(get_env("INSTAGRAM_STORY_HEIGHT", "1920"))
        story_size = (story_width, story_height)  # Instagram story format
        
        converted_stories = []
        
        for page_num in range(len(doc)):
            log.info(f" Processing story {page_num+1}/{len(doc)}")
            
            # Get page
            page = doc.load_page(page_num)
            
            # Calculate zoom factor for desired DPI
            zoom = dpi / 72  # PyMuPDF uses 72 DPI as base
            mat = fitz.Matrix(zoom, zoom)
            
            # Render page to image
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply DPI-aware resizing for Instagram stories (consistent with image generation)
            # Calculate new dimensions based on DPI: new_size = original_size * (target_dpi / 72)
            dpi_scale = dpi / 72
            dpi_width = int(img_width * dpi_scale)
            dpi_height = int(img_height * dpi_scale)
            
            # Resize image for high-quality output
            dpi_resized_image = image.resize((dpi_width, dpi_height), Image.Resampling.LANCZOS)
            
            # Resize to Instagram story dimensions while maintaining aspect ratio
            img_width, img_height = dpi_resized_image.size
            scale = min(story_size[0] / img_width, story_size[1] / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image to Instagram story format
            resized_image = dpi_resized_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create story canvas with white background
            story_image = Image.new('RGB', story_size, 'white')
            
            # Center the resized image on the story canvas
            x_offset = (story_size[0] - new_width) // 2
            y_offset = (story_size[1] - new_height) // 2
            story_image.paste(resized_image, (x_offset, y_offset))
            
            # Save as PNG
            output_filename = f"instagram_story_{page_num+1:02d}.png"
            output_file = output_path / output_filename
            image_quality = int(get_env("IMAGE_QUALITY", "95"))
            story_image.save(output_file, 'PNG', quality=image_quality)
            
            converted_stories.append(str(output_file))
            log.info(f" Saved: {output_filename}")
        
        doc.close()
        log.info(f" Converted {len(converted_stories)} pages to Instagram stories")
        return converted_stories
        
    except ImportError:
        log.error(" PyMuPDF not installed. Install with: pip install PyMuPDF")
        return None
    except Exception as e:
        log.error(f" Story conversion failed: {e}")
        return None







if __name__ == "__main__":
        main() 