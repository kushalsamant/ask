#!/usr/bin/env python3
"""
Image Generation System
Converts PDF generation features into image generation functions
"""

import os
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.metrics = {
            'total_operations': 0, 
            'successful_operations': 0, 
            'failed_operations': 0, 
            'total_time': 0.0,
            'image_generation_time': 0.0,
            'text_overlay_time': 0.0,
            'cover_creation_time': 0.0,
            'toc_creation_time': 0.0
        }
        self.lock = threading.Lock()
    
    def start_timer(self):
        self.start_time = time.time()
    
    def end_timer(self):
        if self.start_time:
            duration = time.time() - self.start_time
            with self.lock:
                self.metrics['total_time'] += duration
                self.metrics['total_operations'] += 1
    
    def record_success(self):
        with self.lock:
            self.metrics['successful_operations'] += 1
    
    def record_failure(self):
        with self.lock:
            self.metrics['failed_operations'] += 1
    
    def record_operation_time(self, operation_type: str, duration: float):
        with self.lock:
            if operation_type in self.metrics:
                self.metrics[operation_type] += duration
    
    def get_stats(self):
        with self.lock:
            stats = self.metrics.copy()
            stats['success_rate'] = (self.metrics['successful_operations'] / max(self.metrics['total_operations'], 1)) * 100
            return stats

# Global performance monitor
performance_monitor = PerformanceMonitor()

def validate_input_parameters(qa_pairs: List[Dict], volume_number: int = 1) -> Tuple[bool, str]:
    """Enhanced input validation"""
    try:
        if not qa_pairs or not isinstance(qa_pairs, list):
            return False, "Invalid Q&A pairs"
        if len(qa_pairs) == 0:
            return False, "Empty Q&A pairs list"
        if not isinstance(volume_number, int) or volume_number < 1:
            return False, "Invalid volume number"
        
        # Validate each Q&A pair
        for i, qa_pair in enumerate(qa_pairs):
            if not isinstance(qa_pair, dict):
                return False, f"Invalid Q&A pair at index {i}"
            if 'question' not in qa_pair or 'answer' not in qa_pair:
                return False, f"Missing question or answer at index {i}"
            if not qa_pair.get('theme'):
                return False, f"Missing theme at index {i}"
        
        return True, "All parameters valid"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def validate_environment():
    """Validate environment configuration"""
    try:
        required_vars = ['IMAGES_DIR', 'IMAGE_WIDTH', 'IMAGE_HEIGHT', 'IMAGE_QUALITY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            return False, f"Missing environment variables: {missing_vars}"
        
        return True, "Environment configuration valid"
    except Exception as e:
        return False, f"Environment validation error: {str(e)}"
import sys
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import time
from pathlib import Path

# Import existing modules
from image_create_ai import generate_image_with_retry
from image_add_text import add_text_overlay
from image_create_cover import create_volume_cover, create_category_cover, create_compilation_cover
from research_csv_manager import read_log_csv

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@dataclass
class ImageGenerationConfig:
    """Configuration for image generation features - converted from PDF system"""
    # Image Generation Features (converted from PDF Generation)
    CREATE_INDIVIDUAL_IMAGES: bool = True
    CREATE_FINAL_COMPILATION: bool = True
    CREATE_AUTOMATIC_THEME_COMPILATIONS: bool = False
    CREATE_COVER_IMAGE: bool = True
    CREATE_TABLE_OF_CONTENTS: bool = True
    CREATE_SEQUENTIAL_TOC: bool = True
    CREATE_THEME_TOC: bool = True
    PRESERVE_TEMP_FILES: bool = True
    TOC_SHOW_FULL_QUESTIONS: bool = True
    TOC_BACKGROUND_PROMPT: bool = True
    
    # Table of Contents Features (converted from PDF TOC)
    TOC_THEME_GROUPING: bool = True
    TOC_GROUP_UNKNOWN_CATEGORIES: bool = True
    TOC_SORT_THEMES_ALPHABETICALLY: bool = True
    TOC_UNKNOWN_THEME_NAME: str = "Uncategorized"
    TOC_IMAGE_NUMBER_SPACE: int = 50
    
    # TOC Templates (converted from PDF TOC templates)
    TOC_MAIN_TITLE_TEMPLATE: str = "*ASK*: Daily Research - Volume {volume_number}"
    TOC_SEQUENTIAL_SUBTITLE: str = "Sequential Table of Contents"
    TOC_THEME_SUBTITLE: str = "Theme Index"
    TOC_SEQUENTIAL_SECTION_TITLE: str = "Sequential Order"
    TOC_THEME_INFO_TEMPLATE: str = "{count} Q&A Pairs • Sequential Order"
    TOC_TOTAL_COUNT_TEMPLATE: str = "Total Q&A Pairs: {count}"
    TOC_THEME_OVERVIEW_TEMPLATE: str = "Theme Overview and Research Insights"
    TOC_RESEARCH_INSIGHTS_TEMPLATE: str = "Research Insights: {insights}..."
    TOC_DATE_TEMPLATE: str = "Generated: {date}"
    TOC_TITLE_TEMPLATE: str = "Table of Contents"
    TOC_SUBTITLE_TEMPLATE: str = "*ASK*: Daily Research - Volume {volume_number}"
    TOC_IMAGE_NUMBER_TEMPLATE: str = "{image_number}"
    TOC_SUMMARY_TEMPLATE: str = "Total Q&A Pairs: {qa_count} | Themes: {category_count}"
    
    # Individual Image Settings (converted from PDF Individual)
    INDIVIDUAL_FILENAME_TEMPLATE: str = "ASK_{image_number}_{theme}.jpg"
    INDIVIDUAL_FALLBACK_TEMPLATE: str = "ASK_QA_{theme}.jpg"
    FOOTER_BRAND_TEXT: str = "ASK: Daily Research"
    FOOTER_IMAGE_NUMBER_TEMPLATE: str = "ASK-{image_number}"
    
    # Page and Layout Settings (converted from PDF Page)
    PAGE_WIDTH: int = 1072
    PAGE_HEIGHT: int = 1792
    PAGE_BREAK_BUFFER: int = 100
    MAX_TEXT_LINES: int = 8
    TEXT_WRAP_WIDTH_ANSWER: int = 60
    TEXT_WRAP_WIDTH_OVERLAY: int = 50
    FOOTER_HEIGHT: int = 80
    FOOTER_BRAND_X: int = 40
    FOOTER_BRAND_Y_OFFSET: int = 20
    FOOTER_THEME_Y_OFFSET: int = 20
    FOOTER_IMAGE_X_OFFSET: int = 40
    FOOTER_IMAGE_Y_OFFSET: int = 20
    
    # Typography Settings (converted from PDF Typography)
    FONT_FAMILY_PRIMARY: str = "Helvetica"
    FONT_FAMILY_SECONDARY: str = "Times-Roman"
    FONT_FAMILY_MONOSPACE: str = "Courier"
    FONT_SIZE_TITLE: int = 36
    FONT_SIZE_SUBTITLE: int = 18
    FONT_SIZE_SECTION: int = 16
    FONT_SIZE_THEME_HEADER: int = 20
    FONT_SIZE_ENTRY: int = 14
    FONT_SIZE_QUESTION: int = 12
    FONT_SIZE_DETAIL: int = 10
    FONT_SIZE_FOOTER: int = 14
    FONT_SIZE_CAPTION: int = 8
    FONT_SIZE_COVER_TITLE: int = 48
    FONT_SIZE_COVER_SUBTITLE: int = 24
    FONT_SIZE_COVER_BRAND: int = 18
    
    # Color Settings (converted from PDF Colors)
    COLOR_PRIMARY: str = "#000000"
    COLOR_SECONDARY: str = "#2C3E50"
    COLOR_ACCENT: str = "#E74C3C"
    COLOR_THEME_HEADER: str = "#8E44AD"
    COLOR_MUTED: str = "#7F8C8D"
    COLOR_BRAND: str = "#34495E"
    TEXT_COLOR: str = "#F0F0F0"
    FOOTER_BACKGROUND_COLOR: str = "0.1,0.1,0.1"
    
    # Spacing Settings (converted from PDF Spacing)
    LINE_SPACING_SINGLE: float = 1.0
    LINE_SPACING_ONE_HALF: float = 1.5
    LINE_SPACING_DOUBLE: float = 2.0
    CHAR_SPACING_NORMAL: int = 0
    CHAR_SPACING_TIGHT: float = -0.5
    CHAR_SPACING_WIDE: float = 1.0
    TITLE_TO_SUBTITLE_SPACING: int = 20
    SUBTITLE_TO_SECTION_SPACING: int = 30
    SECTION_TO_CONTENT_SPACING: int = 40
    ENTRY_SPACING: int = 15
    CATEGORY_SPACING: int = 20
    SECTION_SPACING: int = 25
    LINE_SPACING: int = 30
    
    # Margin Settings (converted from PDF Margins)
    MARGIN_LEFT: int = 72
    MARGIN_TOP: int = 72
    MARGIN_RIGHT: int = 72
    MARGIN_BOTTOM: int = 72
    
    # Cover Generation Settings (converted from PDF Cover)
    COVER_PROMPT: str = "Professional research compilation cover with modern design elements, typography, and visual hierarchy"
    COVER_TITLE: str = "*ASK*: Daily Research"
    COVER_TEXT_COLOR: str = "#000000"
    COVER_BRAND_COLOR: str = "#2C3E50"
    
    # Logging Features (converted from PDF Logging)
    LOG_SUCCESS_MESSAGES: bool = True
    LOG_ERROR_MESSAGES: bool = True
    LOG_PROGRESS_MESSAGES: bool = True
    LOG_DETAILED_ERRORS: bool = True
    LOG_TIMING: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Progress Tracking Features (converted from PDF Progress)
    PROGRESS_STEP_TRACKING: bool = True
    PROGRESS_EMOJI_ENABLED: bool = True
    PROGRESS_VERBOSE: bool = True
    PROGRESS_STEP_NUMBERING: bool = True
    PROGRESS_TIMING_DETAILED: bool = True
    PROGRESS_FILE_OPERATIONS: bool = True
    PROGRESS_IMAGE_OPERATIONS: bool = True
    PROGRESS_TEXT_OPERATIONS: bool = True
    
    # Error Handling Features (converted from PDF Error Handling)
    ERROR_HANDLING_ENABLED: bool = True
    ERROR_CONTINUE_ON_FAILURE: bool = True
    ERROR_SKIP_MISSING_FILES: bool = True
    ERROR_LOG_DETAILED: bool = True
    ERROR_CREATE_PLACEHOLDER: bool = True
    ERROR_NOTIFY_ON_FAILURE: bool = True
    ERROR_MAX_FAILURES: int = 10
    ERROR_RETRY_ATTEMPTS: int = 3
    ERROR_RETRY_DELAY: float = 1.0
    ERROR_FALLBACK_STRATEGY: str = "graceful"
    ERROR_PLACEHOLDER_TEXT: str = "Content Unavailable"
    
    # Volume Configuration (converted from PDF Volume)
    VOLUME_NUMBER: int = 1
    VOLUME_FORMAT: str = "02d"
    QA_PAIRS_PER_VOLUME: int = 100
    
    # Output Directory Configuration (converted from PDF Output)
    OUTPUT_DIR: str = "images"
    COVERS_DIR: str = "images/covers"
    TOC_DIR: str = "images/toc"
    COMPILATIONS_DIR: str = "images/compilations"
    TEMP_DIR: str = "images/temp"
    INDIVIDUAL_DIR: str = "images/individual"
    
    # Image Quality Settings
    IMAGE_WIDTH: int = 1072
    IMAGE_HEIGHT: int = 1792
    IMAGE_QUALITY: int = 95
    IMAGE_STYLE: str = "photographic"
    IMAGE_ASPECT_RATIO: str = "9:16"
    
    # Text Overlay Settings
    MAX_CHARS_PER_LINE: int = 35
    MAX_TEXT_LINES_ANSWER: int = 12
    LINE_HEIGHT: int = 72
    TEXT_AREA_START: int = 40
    BRAND_TEXT: str = "ASK: Daily Research"
    BRAND_X_POSITION: int = 40
    BRAND_Y_OFFSET: int = 100
    TEXT_LEFT_MARGIN: int = 40
    SHADOW_OFFSET: int = 2
    
    # Font Settings
    FONT_FILE_PATH: str = "fonts/arial.ttf"
    MAIN_FONT_SIZE: int = 32
    BRAND_FONT_SIZE: int = 24
    NUMBER_FONT_SIZE: int = 20
    
    # TOC Content Settings
    TOC_MAX_QUESTIONS_PER_CATEGORY: int = 5
    TOC_QUESTION_PREVIEW_LENGTH: int = 50
    TOC_SHOW_THEME_COUNTS: bool = True
    TOC_SHOW_GENERATION_DATE: bool = True
    
    # Compilation Settings
    COMPILATION_MAX_IMAGES_PER_PAGE: int = 4
    COMPILATION_LAYOUT_GRID: bool = True
    COMPILATION_INCLUDE_CATEGORIES: bool = True

    PLACEHOLDER_BACKGROUND_COLOR: str = "#f0f0f0"
    PLACEHOLDER_TEXT_COLOR: str = "#666666"
    PLACEHOLDER_TEXT: str = "Content Unavailable"
    
    # Timing and Performance
    IMAGE_GENERATION_TIMEOUT: int = 300
    BATCH_SIZE: int = 5
    PARALLEL_PROCESSING: bool = False
    RETRY_ATTEMPTS: int = 3
    
    # Output Formats
    OUTPUT_FORMAT: str = "jpg"
    COMPRESSION_QUALITY: int = 95
    INCLUDE_METADATA: bool = True
    GENERATE_THUMBNAILS: bool = False
    
    # Quality Control
    QUALITY_CHECK_ENABLED: bool = True
    MIN_IMAGE_SIZE: int = 100000
    MAX_IMAGE_SIZE: int = 10000000
    VALIDATE_IMAGE_INTEGRITY: bool = True
    
    # Backup and Recovery
    BACKUP_ORIGINAL_IMAGES: bool = True
    BACKUP_RETENTION_DAYS: int = 7
    RECOVERY_MODE: bool = False
    
    # Notifications
    NOTIFY_ON_COMPLETION: bool = True
    NOTIFY_ON_ERROR: bool = True
    NOTIFY_ON_PROGRESS: bool = False
    
    # Debugging
    DEBUG_MODE: bool = False
    VERBOSE_OUTPUT: bool = False
    SAVE_INTERMEDIATE_FILES: bool = False

class ImageGenerationSystem:
    """Comprehensive image generation system with all PDF features converted to images"""
    
    def __init__(self, config: ImageGenerationConfig = None):
        # Start performance monitoring
        performance_monitor.start_timer()
        
        try:
            # Input validation
            is_valid, validation_message = validate_environment()
            if not is_valid:
                log.error(f"Environment validation failed: {validation_message}")
                performance_monitor.record_failure()
                raise ValueError(validation_message)
            
            log.info("Starting enhanced image generation system initialization...")
            
            self.config = config or ImageGenerationConfig()
            self.output_dir = os.getenv('IMAGES_DIR', 'images')
            self.failure_count = 0
            self.max_failures = int(os.getenv('ERROR_MAX_FAILURES', '10'))
            
            # Create output directories
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(f"{self.output_dir}/covers", exist_ok=True)
            os.makedirs(f"{self.output_dir}/toc", exist_ok=True)
            os.makedirs(f"{self.output_dir}/compilations", exist_ok=True)
            os.makedirs(f"{self.output_dir}/temp", exist_ok=True)
            
            self._setup_logging()
            
            # Record success and end timer
            performance_monitor.end_timer()
            performance_monitor.record_success()
            
            log.info("Enhanced image generation system initialization completed")
            
        except Exception as e:
            log.error(f"Error in enhanced image generation system initialization: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if self.config.LOG_SUCCESS_MESSAGES:
            log.info(" Image generation system initialized")
        if self.config.LOG_TIMING:
            self.start_time = time.time()
    
    def _log_progress(self, message: str, emoji: str = "", step: int = None):
        """Log progress with optional emoji and step numbering"""
        if not self.config.PROGRESS_STEP_TRACKING:
            return
            
        prefix = ""
        if self.config.PROGRESS_EMOJI_ENABLED and emoji:
            prefix += f"{emoji} "
        if self.config.PROGRESS_STEP_NUMBERING and step:
            prefix += f"Step {step}: "
            
        if self.config.PROGRESS_VERBOSE:
            log.info(f"{prefix}{message}")
    
    def _log_timing(self, operation: str, start_time: float):
        """Log timing information"""
        if not self.config.LOG_TIMING:
            return
            
        duration = time.time() - start_time
        if self.config.PROGRESS_TIMING_DETAILED:
            log.info(f"⏱  {operation} completed in {duration:.2f} seconds")
    
    def _handle_error(self, error: Exception, operation: str, context: str = ""):
        """Handle errors with configurable behavior"""
        if not self.config.ERROR_HANDLING_ENABLED:
            raise error
            
        self.failure_count += 1
        
        if self.config.ERROR_LOG_DETAILED:
            log.error(f" Error in {operation}: {error}")
            if context:
                log.error(f"   Context: {context}")
        
        if self.config.ERROR_NOTIFY_ON_FAILURE:
            log.warning(f"  Failure #{self.failure_count} in {operation}")
        
        if self.failure_count >= self.max_failures:
            raise Exception(f"Maximum failures ({self.max_failures}) reached")
        
        if not self.config.ERROR_CONTINUE_ON_FAILURE:
            raise error
    
    def create_individual_images(self, qa_pairs: List[Dict]) -> List[Dict]:
        """Create individual images for each Q&A pair"""
        if not self.config.CREATE_INDIVIDUAL_IMAGES:
            return qa_pairs
            
        self._log_progress("Creating individual images", "", 1)
        start_time = time.time()
        
        results = []
        for i, qa_pair in enumerate(qa_pairs):
            try:
                self._log_progress(f"Processing Q&A pair {i+1}/{len(qa_pairs)}", "")
                
                # Generate question image
                question_image = self._create_question_image(qa_pair, i+1)
                qa_pair['question_image'] = question_image
                
                # Generate answer image
                answer_image = self._create_answer_image(qa_pair, i+1)
                qa_pair['answer_image'] = answer_image
                
                results.append(qa_pair)
                
                if self.config.LOG_SUCCESS_MESSAGES:
                    log.info(f" Created images for Q&A pair {i+1}")
                    
            except Exception as e:
                log.error(f"Error in enhanced complete image generation: {e}")
                performance_monitor.end_timer()
                performance_monitor.record_failure()
                raise
                self._handle_error(e, "individual image creation", f"Q&A pair {i+1}")
                if self.config.ERROR_SKIP_MISSING_FILES:
                    continue
                else:
                    raise
        
        self._log_timing("Individual image creation", start_time)
        return results
    
    def _create_question_image(self, qa_pair: Dict, image_number: int) -> str:
        """Create question image with text overlay"""
        if not self.config.PROGRESS_IMAGE_OPERATIONS:
            return ""
            
        question = qa_pair.get('question', '')
        theme = qa_pair.get('theme', 'unknown')
        
        # Generate base image
        image_path = f"{self.output_dir}/temp/ASK-{image_number:02d}-{theme}-q.jpg"
        
        try:
            # Generate AI image
            generated_path, _ = generate_image_with_retry(
                prompt=question,
                theme=theme,
                image_number=image_number,
                image_type="q"
            )
            
            # Add text overlay
            if self.config.PROGRESS_TEXT_OPERATIONS:
                final_path = add_text_overlay(generated_path, question, image_number, is_question=True)
                return final_path
            
            return generated_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "question image creation", f"Image {image_number}")
            if self.config.ERROR_CREATE_PLACEHOLDER:
                return self._create_placeholder_image(image_number, theme, "q")
            raise
    
    def _create_answer_image(self, qa_pair: Dict, image_number: int) -> str:
        """Create answer image with text overlay"""
        if not self.config.PROGRESS_IMAGE_OPERATIONS:
            return ""
            
        answer = qa_pair.get('answer', '')
        theme = qa_pair.get('theme', 'unknown')
        
        # Generate base image
        image_path = f"{self.output_dir}/temp/ASK-{image_number:02d}-{theme}-a.jpg"
        
        try:
            # Generate AI image
            generated_path, _ = generate_image_with_retry(
                prompt=answer,
                theme=theme,
                image_number=image_number,
                image_type="a"
            )
            
            # Add text overlay
            if self.config.PROGRESS_TEXT_OPERATIONS:
                final_path = add_text_overlay(generated_path, answer, image_number, is_question=False)
                return final_path
            
            return generated_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "answer image creation", f"Image {image_number}")
            if self.config.ERROR_CREATE_PLACEHOLDER:
                return self._create_placeholder_image(image_number, theme, "a")
            raise
    
    def _create_placeholder_image(self, image_number: int, theme: str, image_type: str) -> str:
        """Create placeholder image when generation fails"""
        placeholder_path = f"{self.output_dir}/temp/ASK-{image_number:02d}-{theme}-{image_type}-placeholder.jpg"

        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create blank image
            img = Image.new('RGB', (1072, 1792), color='#f0f0f0')
            draw = ImageDraw.Draw(img)

            text = f"Image {image_number}\n{theme.title()}\n{image_type.upper()}\n\nContent Unavailable"
            draw.text((536, 896), text, fill='#666666', anchor='mm')
            
            img.save(placeholder_path)
            return placeholder_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            log.error(f"Failed to create placeholder image: {e}")
            return ""
    
    def create_final_compilation(self, qa_pairs: List[Dict]) -> str:
        """Create final compilation image"""
        if not self.config.CREATE_FINAL_COMPILATION:
            return ""
            
        self._log_progress("Creating final compilation", "", 2)
        start_time = time.time()
        
        try:
            compilation_path = create_compilation_cover('research', qa_pairs, f"{self.output_dir}/compilations")
            
            if self.config.LOG_SUCCESS_MESSAGES:
                log.info(f" Final compilation created: {compilation_path}")
            
            self._log_timing("Final compilation creation", start_time)
            return compilation_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "final compilation creation")
            return ""
    
    def create_automatic_category_compilations(self, qa_pairs: List[Dict]) -> List[str]:
        """Create automatic theme compilations"""
        if not self.config.CREATE_AUTOMATIC_THEME_COMPILATIONS:
            return []
            
        self._log_progress("Creating theme compilations", "", 3)
        start_time = time.time()
        
        # Group Q&A pairs by theme
        themes = {}
        for qa_pair in qa_pairs:
            theme = qa_pair.get('theme', 'unknown')
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(qa_pair)
        
        compilation_paths = []
        for theme, category_qa_pairs in themes.items():
            try:
                if self.config.TOC_THEME_GROUPING:
                    self._log_progress(f"Creating compilation for {theme}", "")
                    
                    compilation_path = create_category_cover(theme, category_qa_pairs, f"{self.output_dir}/compilations")
                    compilation_paths.append(compilation_path)
                    
                    if self.config.LOG_SUCCESS_MESSAGES:
                        log.info(f" Theme compilation created for {theme}")
                        
            except Exception as e:
                log.error(f"Error in enhanced complete image generation: {e}")
                performance_monitor.end_timer()
                performance_monitor.record_failure()
                raise
                self._handle_error(e, "theme compilation creation", theme)
                if not self.config.ERROR_CONTINUE_ON_FAILURE:
                    break
        
        self._log_timing("Theme compilations creation", start_time)
        return compilation_paths
    
    def create_cover_image(self, volume_number: int, qa_pairs: List[Dict]) -> str:
        """Create cover image for volume"""
        if not self.config.CREATE_COVER_IMAGE:
            return ""
            
        self._log_progress("Creating cover image", "", 4)
        start_time = time.time()
        
        try:
            cover_path = create_volume_cover(volume_number, qa_pairs, f"{self.output_dir}/covers")
            
            if self.config.LOG_SUCCESS_MESSAGES:
                log.info(f" Cover image created: {cover_path}")
            
            self._log_timing("Cover image creation", start_time)
            return cover_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "cover image creation")
            return ""
    
    def create_table_of_contents(self, qa_pairs: List[Dict]) -> str:
        """Create table of contents image"""
        if not self.config.CREATE_TABLE_OF_CONTENTS:
            return ""
            
        self._log_progress("Creating table of contents", "", 5)
        start_time = time.time()
        
        try:
            toc_path = self._generate_toc_image(qa_pairs)
            
            if self.config.LOG_SUCCESS_MESSAGES:
                log.info(f" Table of contents created: {toc_path}")
            
            self._log_timing("Table of contents creation", start_time)
            return toc_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "table of contents creation")
            return ""
    
    def _generate_toc_image(self, qa_pairs: List[Dict]) -> str:
        """Generate table of contents image"""
        toc_path = f"{self.output_dir}/toc/ASK-TOC-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        try:
            # Create TOC content
            toc_content = self._create_toc_content(qa_pairs)
            
            # Generate TOC image
            if self.config.TOC_BACKGROUND_PROMPT:
                prompt = "Professional table of contents with modern design, typography, and visual hierarchy"
            else:
                prompt = "Table of contents"
            
            generated_path, _ = generate_image_with_retry(
                prompt=prompt,
                theme="toc",
                image_number=0,
                image_type="toc"
            )
            
            # Add TOC text overlay
            final_path = add_text_overlay(generated_path, toc_content, 0, is_question=True)
            
            return final_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "TOC image generation")
            return ""
    
    def _create_toc_content(self, qa_pairs: List[Dict]) -> str:
        """Create table of contents content"""
        toc_lines = []
        toc_lines.append("*ASK*: Daily Research")
        toc_lines.append("Table of Contents")
        toc_lines.append("")
        
        # Group by theme if enabled
        if self.config.TOC_THEME_GROUPING:
            themes = {}
            for qa_pair in qa_pairs:
                theme = qa_pair.get('theme', 'unknown')
                if theme not in themes:
                    themes[theme] = []
                themes[theme].append(qa_pair)
            
            # Sort themes if enabled
            if self.config.TOC_SORT_THEMES_ALPHABETICALLY:
                themes = dict(sorted(themes.items()))
            
            for theme, category_qa_pairs in themes.items():
                toc_lines.append(f" {theme.replace('_', ' ').title()}")
                toc_lines.append(f"   {len(category_qa_pairs)} Q&A pairs")
                
                for i, qa_pair in enumerate(category_qa_pairs[:5]):  # Show first 5
                    question = qa_pair.get('question', '')
                    if self.config.TOC_SHOW_FULL_QUESTIONS:
                        toc_lines.append(f"   {i+1}. {question}")
                    else:
                        toc_lines.append(f"   {i+1}. {question[:50]}...")
                
                if len(category_qa_pairs) > 5:
                    toc_lines.append(f"   ... and {len(category_qa_pairs) - 5} more")
                toc_lines.append("")
        else:
            # Sequential listing
            for i, qa_pair in enumerate(qa_pairs):
                question = qa_pair.get('question', '')
                theme = qa_pair.get('theme', 'unknown')
                
                if self.config.TOC_SHOW_FULL_QUESTIONS:
                    toc_lines.append(f"{i+1:02d}. {question}")
                else:
                    toc_lines.append(f"{i+1:02d}. {question[:50]}...")
                toc_lines.append(f"    Theme: {theme}")
                toc_lines.append("")
        
        toc_lines.append(f"Total Q&A Pairs: {len(qa_pairs)}")
        toc_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(toc_lines)
    
    def create_sequential_toc(self, qa_pairs: List[Dict]) -> str:
        """Create sequential table of contents"""
        if not self.config.CREATE_SEQUENTIAL_TOC:
            return ""
            
        self._log_progress("Creating sequential TOC", "", 6)
        start_time = time.time()
        
        try:
            # Create sequential TOC content
            toc_content = "*ASK*: Daily Research\nSequential Table of Contents\n\n"
            
            for i, qa_pair in enumerate(qa_pairs):
                question = qa_pair.get('question', '')
                theme = qa_pair.get('theme', 'unknown')
                
                if self.config.TOC_SHOW_FULL_QUESTIONS:
                    toc_content += f"{i+1:02d}. {question}\n"
                else:
                    toc_content += f"{i+1:02d}. {question[:50]}...\n"
                toc_content += f"    Theme: {theme}\n\n"
            
            # Generate sequential TOC image
            toc_path = f"{self.output_dir}/toc/ASK-Sequential-TOC-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            generated_path, _ = generate_image_with_retry(
                prompt="Sequential table of contents with numbered list",
                theme="toc",
                image_number=0,
                image_type="sequential_toc"
            )
            
            final_path = add_text_overlay(generated_path, toc_content, 0, is_question=True)
            
            if self.config.LOG_SUCCESS_MESSAGES:
                log.info(f" Sequential TOC created: {final_path}")
            
            self._log_timing("Sequential TOC creation", start_time)
            return final_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "sequential TOC creation")
            return ""
    
    def create_category_toc(self, qa_pairs: List[Dict]) -> str:
        """Create theme table of contents"""
        if not self.config.CREATE_THEME_TOC:
            return ""
            
        self._log_progress("Creating theme TOC", "", 7)
        start_time = time.time()
        
        try:
            # Group by theme
            themes = {}
            for qa_pair in qa_pairs:
                theme = qa_pair.get('theme', 'unknown')
                if theme not in themes:
                    themes[theme] = []
                themes[theme].append(qa_pair)
            
            # Sort themes if enabled
            if self.config.TOC_SORT_THEMES_ALPHABETICALLY:
                themes = dict(sorted(themes.items()))
            
            # Create theme TOC content
            toc_content = "*ASK*: Daily Research\nCategory Table of Contents\n\n"
            
            for theme, category_qa_pairs in themes.items():
                toc_content += f" {theme.replace('_', ' ').title()}\n"
                toc_content += f"   {len(category_qa_pairs)} Q&A pairs\n\n"
                
                for i, qa_pair in enumerate(category_qa_pairs):
                    question = qa_pair.get('question', '')
                    if self.config.TOC_SHOW_FULL_QUESTIONS:
                        toc_content += f"   {i+1}. {question}\n"
                    else:
                        toc_content += f"   {i+1}. {question[:50]}...\n"
                toc_content += "\n"
            
            # Generate theme TOC image
            toc_path = f"{self.output_dir}/toc/ASK-Theme-TOC-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            generated_path, _ = generate_image_with_retry(
                prompt="Theme table of contents with grouped sections",
                theme="toc",
                image_number=0,
                image_type="category_toc"
            )
            
            final_path = add_text_overlay(generated_path, toc_content, 0, is_question=True)
            
            if self.config.LOG_SUCCESS_MESSAGES:
                log.info(f" Theme TOC created: {final_path}")
            
            self._log_timing("Theme TOC creation", start_time)
            return final_path
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "theme TOC creation")
            return ""
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.config.PRESERVE_TEMP_FILES:
            return
            
        self._log_progress("Cleaning up temporary files", "🧹", 8)
        
        try:
            temp_dir = f"{self.output_dir}/temp"
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                
                if self.config.LOG_SUCCESS_MESSAGES:
                    log.info(" Temporary files cleaned up")
                    
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise
            self._handle_error(e, "temp file cleanup")
    
    def generate_qa_images(self, qa_pairs: List[dict]) -> List[dict]:
        """Generate images for all Q&A pairs (from ImageOrchestrator)"""
        if not self.config.CREATE_INDIVIDUAL_IMAGES:
            return qa_pairs
            
        self._log_progress(f"Generating images for {len(qa_pairs)} Q&A pairs", "")
        log.info(f"Generating images for {len(qa_pairs)} Q&A pairs...")
        
        generated_images = []
        
        for i, qa_pair in enumerate(qa_pairs, 1):
            try:
                theme = qa_pair.get('theme', 'Unknown')
                question_text = qa_pair.get('question_text', '')
                answer_text = qa_pair.get('answer_text', '')
                image_number = qa_pair.get('image_number', str(i))
                
                log.info(f"Generating images for Q&A pair {i}/{len(qa_pairs)} ({theme})")
                
                # Generate question image
                question_image_path, _ = generate_image_with_retry(
                    prompt=question_text,
                    theme=theme,
                    image_number=image_number,
                    image_type="q"
                )
                
                # Add text overlay to question image
                if question_image_path and os.path.exists(question_image_path):
                    add_text_overlay(question_image_path, question_text, image_number, is_question=True)
                    log.info(f"Added text overlay to question image: {os.path.basename(question_image_path)}")
                
                # Generate answer image
                answer_image_path, _ = generate_image_with_retry(
                    prompt=answer_text,
                    theme=theme,
                    image_number=image_number,
                    image_type="a"
                )
                
                # Add text overlay to answer image
                if answer_image_path and os.path.exists(answer_image_path):
                    add_text_overlay(answer_image_path, answer_text, image_number, is_question=False)
                    log.info(f"Added text overlay to answer image: {os.path.basename(answer_image_path)}")
                
                # Add image paths to Q&A pair
                qa_pair_with_images = qa_pair.copy()
                qa_pair_with_images['question'] = question_image_path
                qa_pair_with_images['answer'] = answer_image_path
                
                generated_images.append(qa_pair_with_images)
                
                log.info(f"Generated images for Q&A pair {i}")
                
            except Exception as e:
                log.error(f"Error in enhanced complete image generation: {e}")
                performance_monitor.end_timer()
                performance_monitor.record_failure()
                raise
                log.error(f"Failed to generate images for Q&A pair {i}: {e}")
                generated_images.append(qa_pair)
        
        return generated_images

    def generate_complete_image_set(self, qa_pairs: List[Dict], volume_number: int = 1) -> Dict[str, str]:
        """Generate complete image set with all features (enhanced with performance monitoring)"""
        # Start performance monitoring
        performance_monitor.start_timer()
        
        try:
            # Input validation
            is_valid, validation_message = validate_input_parameters(qa_pairs, volume_number)
            if not is_valid:
                log.error(f"Input validation failed: {validation_message}")
                performance_monitor.record_failure()
                raise ValueError(validation_message)
            
            # Environment validation
            is_valid, validation_message = validate_environment()
            if not is_valid:
                log.error(f"Environment validation failed: {validation_message}")
                performance_monitor.record_failure()
                raise ValueError(validation_message)
            
            log.info(f"Starting enhanced complete image generation for {len(qa_pairs)} Q&A pairs...")
            
            self._log_progress("Starting complete image generation", "")
            start_time = time.time()
            
            results = {
                'individual_images': [],
                'final_compilation': '',
                'category_compilations': [],
                'cover_image': '',
                'table_of_contents': '',
                'sequential_toc': '',
                'category_toc': '',
                'total_images': 0,
                'qa_pairs': [],
                'covers': {}
            }
            
            # Step 1: Create individual images
            if self.config.CREATE_INDIVIDUAL_IMAGES:
                processed_qa_pairs = self.generate_qa_images(qa_pairs)
                results['individual_images'] = processed_qa_pairs
                results['qa_pairs'] = processed_qa_pairs
                results['total_images'] += len(processed_qa_pairs) * 2  # Question + Answer images
            
            # Step 2: Create final compilation
            if self.config.CREATE_FINAL_COMPILATION:
                results['final_compilation'] = self.create_final_compilation(qa_pairs)
                if results['final_compilation']:
                    results['total_images'] += 1
            
            # Step 3: Create theme compilations
            if self.config.CREATE_AUTOMATIC_THEME_COMPILATIONS:
                results['category_compilations'] = self.create_automatic_category_compilations(qa_pairs)
                results['total_images'] += len(results['category_compilations'])
            
            # Step 4: Create cover image
            if self.config.CREATE_COVER_IMAGE:
                results['cover_image'] = self.create_cover_image(volume_number, qa_pairs)
                if results['cover_image']:
                    results['total_images'] += 1
                    results['covers']['volume'] = results['cover_image']
                
                # Generate theme covers (from ImageOrchestrator)
                try:
                    themes = {}
                    for qa_pair in qa_pairs:
                        theme = qa_pair.get('theme', 'Unknown')
                        if theme not in themes:
                            themes[theme] = []
                        themes[theme].append(qa_pair)
                    
                    # Generate theme covers
                    for theme, category_qa_pairs in themes.items():
                        category_cover_path = create_category_cover(theme, category_qa_pairs, self.output_dir)
                        if category_cover_path:
                            results['covers'][f'category_{theme}'] = category_cover_path
                            results['total_images'] += 1
                            log.info(f"Generated theme cover for {theme}: {category_cover_path}")
                    
                    # Generate compilation cover
                    compilation_cover_path = create_compilation_cover('research', qa_pairs, self.output_dir)
                    if compilation_cover_path:
                        results['covers']['compilation'] = compilation_cover_path
                        results['total_images'] += 1
                        log.info(f"Generated compilation cover: {compilation_cover_path}")
                        
                except Exception as e:
                    log.error(f"Error generating additional cover images: {e}")
            
            # Step 5: Create table of contents
            if self.config.CREATE_TABLE_OF_CONTENTS:
                results['table_of_contents'] = self.create_table_of_contents(qa_pairs)
                if results['table_of_contents']:
                    results['total_images'] += 1
            
            # Step 6: Create sequential TOC
            if self.config.CREATE_SEQUENTIAL_TOC:
                results['sequential_toc'] = self.create_sequential_toc(qa_pairs)
                if results['sequential_toc']:
                    results['total_images'] += 1
            
            # Step 7: Create theme TOC
            if self.config.CREATE_THEME_TOC:
                results['category_toc'] = self.create_category_toc(qa_pairs)
                if results['category_toc']:
                    results['total_images'] += 1
            
            # Step 8: Cleanup
            self.cleanup_temp_files()
            
            # Final summary
            if self.config.LOG_SUCCESS_MESSAGES:
                log.info(f" Complete image generation finished!")
                log.info(f" Total images created: {results['total_images']}")
                log.info(f" Individual images: {len(results['individual_images'])}")
                log.info(f" Final compilation: {'' if results['final_compilation'] else ''}")
                log.info(f" Theme compilations: {len(results['category_compilations'])}")
                log.info(f"  Cover image: {'' if results['cover_image'] else ''}")
                log.info(f" Table of contents: {'' if results['table_of_contents'] else ''}")
            
            self._log_timing("Complete image generation", start_time)
            
            # Record success and end timer
            performance_monitor.end_timer()
            performance_monitor.record_success()
            
            return results
            
        except Exception as e:
            log.error(f"Error in enhanced complete image generation: {e}")
            performance_monitor.end_timer()
            performance_monitor.record_failure()
            raise

def main():
    """Main function to demonstrate the image generation system"""
    # Load configuration from environment - all PDF features converted to image features
    config = ImageGenerationConfig(
        # Image Generation Features (converted from PDF Generation)
        CREATE_INDIVIDUAL_IMAGES=os.getenv('CREATE_INDIVIDUAL_IMAGES', 'true').lower() == 'true',
        CREATE_FINAL_COMPILATION=os.getenv('CREATE_FINAL_COMPILATION', 'true').lower() == 'true',
        CREATE_AUTOMATIC_THEME_COMPILATIONS=os.getenv('CREATE_AUTOMATIC_THEME_COMPILATIONS', 'false').lower() == 'true',
        CREATE_COVER_IMAGE=os.getenv('CREATE_COVER_IMAGE', 'true').lower() == 'true',
        CREATE_TABLE_OF_CONTENTS=os.getenv('CREATE_TABLE_OF_CONTENTS', 'true').lower() == 'true',
        CREATE_SEQUENTIAL_TOC=os.getenv('CREATE_SEQUENTIAL_TOC', 'true').lower() == 'true',
        CREATE_THEME_TOC=os.getenv('CREATE_THEME_TOC', 'true').lower() == 'true',
        PRESERVE_TEMP_FILES=os.getenv('PRESERVE_TEMP_FILES', 'true').lower() == 'true',
        
        # Table of Contents Features (converted from PDF TOC)
        TOC_SHOW_FULL_QUESTIONS=os.getenv('TOC_SHOW_FULL_QUESTIONS', 'true').lower() == 'true',
        TOC_BACKGROUND_PROMPT=os.getenv('TOC_BACKGROUND_PROMPT', 'true').lower() == 'true',
        TOC_THEME_GROUPING=os.getenv('TOC_THEME_GROUPING', 'true').lower() == 'true',
        TOC_GROUP_UNKNOWN_CATEGORIES=os.getenv('TOC_GROUP_UNKNOWN_CATEGORIES', 'true').lower() == 'true',
        TOC_SORT_THEMES_ALPHABETICALLY=os.getenv('TOC_SORT_THEMES_ALPHABETICALLY', 'true').lower() == 'true',
        TOC_UNKNOWN_THEME_NAME=os.getenv('TOC_UNKNOWN_THEME_NAME', 'Uncategorized'),
        TOC_IMAGE_NUMBER_SPACE=int(os.getenv('TOC_IMAGE_NUMBER_SPACE', '50')),
        
        # TOC Templates (converted from PDF TOC templates)
        TOC_MAIN_TITLE_TEMPLATE=os.getenv('TOC_MAIN_TITLE_TEMPLATE', '*ASK*: Daily Research - Volume {volume_number}'),
        TOC_SEQUENTIAL_SUBTITLE=os.getenv('TOC_SEQUENTIAL_SUBTITLE', 'Sequential Table of Contents'),
        TOC_THEME_SUBTITLE=os.getenv('TOC_THEME_SUBTITLE', 'Theme Index'),
        TOC_SEQUENTIAL_SECTION_TITLE=os.getenv('TOC_SEQUENTIAL_SECTION_TITLE', 'Sequential Order'),
        TOC_THEME_INFO_TEMPLATE=os.getenv('TOC_THEME_INFO_TEMPLATE', '{count} Q&A Pairs • Sequential Order'),
        TOC_TOTAL_COUNT_TEMPLATE=os.getenv('TOC_TOTAL_COUNT_TEMPLATE', 'Total Q&A Pairs: {count}'),
        TOC_THEME_OVERVIEW_TEMPLATE=os.getenv('TOC_THEME_OVERVIEW_TEMPLATE', 'Theme Overview and Research Insights'),
        TOC_RESEARCH_INSIGHTS_TEMPLATE=os.getenv('TOC_RESEARCH_INSIGHTS_TEMPLATE', 'Research Insights: {insights}...'),
        TOC_DATE_TEMPLATE=os.getenv('TOC_DATE_TEMPLATE', 'Generated: {date}'),
        TOC_TITLE_TEMPLATE=os.getenv('TOC_TITLE_TEMPLATE', 'Table of Contents'),
        TOC_SUBTITLE_TEMPLATE=os.getenv('TOC_SUBTITLE_TEMPLATE', '*ASK*: Daily Research - Volume {volume_number}'),
        TOC_IMAGE_NUMBER_TEMPLATE=os.getenv('TOC_IMAGE_NUMBER_TEMPLATE', '{image_number}'),
        TOC_SUMMARY_TEMPLATE=os.getenv('TOC_SUMMARY_TEMPLATE', 'Total Q&A Pairs: {qa_count} | Themes: {category_count}'),
        
        # Individual Image Settings (converted from PDF Individual)
        INDIVIDUAL_FILENAME_TEMPLATE=os.getenv('INDIVIDUAL_FILENAME_TEMPLATE', 'ASK_{image_number}_{theme}.jpg'),
        INDIVIDUAL_FALLBACK_TEMPLATE=os.getenv('INDIVIDUAL_FALLBACK_TEMPLATE', 'ASK_QA_{theme}.jpg'),
                    FOOTER_BRAND_TEXT=os.getenv('FOOTER_BRAND_TEXT', 'ASK: Daily Research'),
        FOOTER_IMAGE_NUMBER_TEMPLATE=os.getenv('FOOTER_IMAGE_NUMBER_TEMPLATE', 'ASK-{image_number}'),
        
        # Page and Layout Settings (converted from PDF Page)
        PAGE_WIDTH=int(os.getenv('PAGE_WIDTH', '1072')),
        PAGE_HEIGHT=int(os.getenv('PAGE_HEIGHT', '1792')),
        PAGE_BREAK_BUFFER=int(os.getenv('PAGE_BREAK_BUFFER', '100')),
        MAX_TEXT_LINES=int(os.getenv('MAX_TEXT_LINES', '8')),
        TEXT_WRAP_WIDTH_ANSWER=int(os.getenv('TEXT_WRAP_WIDTH_ANSWER', '60')),
        TEXT_WRAP_WIDTH_OVERLAY=int(os.getenv('TEXT_WRAP_WIDTH_OVERLAY', '50')),
        FOOTER_HEIGHT=int(os.getenv('FOOTER_HEIGHT', '80')),
        FOOTER_BRAND_X=int(os.getenv('FOOTER_BRAND_X', '40')),
        FOOTER_BRAND_Y_OFFSET=int(os.getenv('FOOTER_BRAND_Y_OFFSET', '20')),
        FOOTER_THEME_Y_OFFSET=int(os.getenv('FOOTER_THEME_Y_OFFSET', '20')),
        FOOTER_IMAGE_X_OFFSET=int(os.getenv('FOOTER_IMAGE_X_OFFSET', '40')),
        FOOTER_IMAGE_Y_OFFSET=int(os.getenv('FOOTER_IMAGE_Y_OFFSET', '20')),
        
        # Typography Settings (converted from PDF Typography)
        FONT_FAMILY_PRIMARY=os.getenv('FONT_FAMILY_PRIMARY', 'Helvetica'),
        FONT_FAMILY_SECONDARY=os.getenv('FONT_FAMILY_SECONDARY', 'Times-Roman'),
        FONT_FAMILY_MONOSPACE=os.getenv('FONT_FAMILY_MONOSPACE', 'Courier'),
        FONT_SIZE_TITLE=int(os.getenv('FONT_SIZE_TITLE', '36')),
        FONT_SIZE_SUBTITLE=int(os.getenv('FONT_SIZE_SUBTITLE', '18')),
        FONT_SIZE_SECTION=int(os.getenv('FONT_SIZE_SECTION', '16')),
        FONT_SIZE_THEME_HEADER=int(os.getenv('FONT_SIZE_THEME_HEADER', '20')),
        FONT_SIZE_ENTRY=int(os.getenv('FONT_SIZE_ENTRY', '14')),
        FONT_SIZE_QUESTION=int(os.getenv('FONT_SIZE_QUESTION', '12')),
        FONT_SIZE_DETAIL=int(os.getenv('FONT_SIZE_DETAIL', '10')),
        FONT_SIZE_FOOTER=int(os.getenv('FONT_SIZE_FOOTER', '14')),
        FONT_SIZE_CAPTION=int(os.getenv('FONT_SIZE_CAPTION', '8')),
        FONT_SIZE_COVER_TITLE=int(os.getenv('FONT_SIZE_COVER_TITLE', '48')),
        FONT_SIZE_COVER_SUBTITLE=int(os.getenv('FONT_SIZE_COVER_SUBTITLE', '24')),
        FONT_SIZE_COVER_BRAND=int(os.getenv('FONT_SIZE_COVER_BRAND', '18')),
        
        # Color Settings (converted from PDF Colors)
        COLOR_PRIMARY=os.getenv('COLOR_PRIMARY', '#000000'),
        COLOR_SECONDARY=os.getenv('COLOR_SECONDARY', '#2C3E50'),
        COLOR_ACCENT=os.getenv('COLOR_ACCENT', '#E74C3C'),
        COLOR_THEME_HEADER=os.getenv('COLOR_THEME_HEADER', '#8E44AD'),
        COLOR_MUTED=os.getenv('COLOR_MUTED', '#7F8C8D'),
        COLOR_BRAND=os.getenv('COLOR_BRAND', '#34495E'),
        TEXT_COLOR=os.getenv('TEXT_COLOR', '#F0F0F0'),
        FOOTER_BACKGROUND_COLOR=os.getenv('FOOTER_BACKGROUND_COLOR', '0.1,0.1,0.1'),
        
        # Spacing Settings (converted from PDF Spacing)
        LINE_SPACING_SINGLE=float(os.getenv('LINE_SPACING_SINGLE', '1.0')),
        LINE_SPACING_ONE_HALF=float(os.getenv('LINE_SPACING_ONE_HALF', '1.5')),
        LINE_SPACING_DOUBLE=float(os.getenv('LINE_SPACING_DOUBLE', '2.0')),
        CHAR_SPACING_NORMAL=int(os.getenv('CHAR_SPACING_NORMAL', '0')),
        CHAR_SPACING_TIGHT=float(os.getenv('CHAR_SPACING_TIGHT', '-0.5')),
        CHAR_SPACING_WIDE=float(os.getenv('CHAR_SPACING_WIDE', '1.0')),
        TITLE_TO_SUBTITLE_SPACING=int(os.getenv('TITLE_TO_SUBTITLE_SPACING', '20')),
        SUBTITLE_TO_SECTION_SPACING=int(os.getenv('SUBTITLE_TO_SECTION_SPACING', '30')),
        SECTION_TO_CONTENT_SPACING=int(os.getenv('SECTION_TO_CONTENT_SPACING', '40')),
        ENTRY_SPACING=int(os.getenv('ENTRY_SPACING', '15')),
        CATEGORY_SPACING=int(os.getenv('CATEGORY_SPACING', '20')),
        SECTION_SPACING=int(os.getenv('SECTION_SPACING', '25')),
        LINE_SPACING=int(os.getenv('LINE_SPACING', '30')),
        
        # Margin Settings (converted from PDF Margins)
        MARGIN_LEFT=int(os.getenv('MARGIN_LEFT', '72')),
        MARGIN_TOP=int(os.getenv('MARGIN_TOP', '72')),
        MARGIN_RIGHT=int(os.getenv('MARGIN_RIGHT', '72')),
        MARGIN_BOTTOM=int(os.getenv('MARGIN_BOTTOM', '72')),
        
        # Cover Generation Settings (converted from PDF Cover)
        COVER_PROMPT=os.getenv('COVER_PROMPT', 'Professional research compilation cover with modern design elements, typography, and visual hierarchy'),
        COVER_TITLE=os.getenv('COVER_TITLE', '*ASK*: Daily Research'),
        COVER_TEXT_COLOR=os.getenv('COVER_TEXT_COLOR', '#000000'),
        COVER_BRAND_COLOR=os.getenv('COVER_BRAND_COLOR', '#2C3E50'),
        
        # Logging Features (converted from PDF Logging)
        LOG_SUCCESS_MESSAGES=os.getenv('LOG_SUCCESS_MESSAGES', 'true').lower() == 'true',
        LOG_ERROR_MESSAGES=os.getenv('LOG_ERROR_MESSAGES', 'true').lower() == 'true',
        LOG_PROGRESS_MESSAGES=os.getenv('LOG_PROGRESS_MESSAGES', 'true').lower() == 'true',
        LOG_DETAILED_ERRORS=os.getenv('LOG_DETAILED_ERRORS', 'true').lower() == 'true',
        LOG_TIMING=os.getenv('LOG_TIMING', 'true').lower() == 'true',
        LOG_LEVEL=os.getenv('LOG_LEVEL', 'INFO'),
        
        # Progress Tracking Features (converted from PDF Progress)
        PROGRESS_STEP_TRACKING=os.getenv('PROGRESS_STEP_TRACKING', 'true').lower() == 'true',
        PROGRESS_EMOJI_ENABLED=os.getenv('PROGRESS_EMOJI_ENABLED', 'true').lower() == 'true',
        PROGRESS_VERBOSE=os.getenv('PROGRESS_VERBOSE', 'true').lower() == 'true',
        PROGRESS_STEP_NUMBERING=os.getenv('PROGRESS_STEP_NUMBERING', 'true').lower() == 'true',
        PROGRESS_TIMING_DETAILED=os.getenv('PROGRESS_TIMING_DETAILED', 'true').lower() == 'true',
        PROGRESS_FILE_OPERATIONS=os.getenv('PROGRESS_FILE_OPERATIONS', 'true').lower() == 'true',
        PROGRESS_IMAGE_OPERATIONS=os.getenv('PROGRESS_IMAGE_OPERATIONS', 'true').lower() == 'true',
        PROGRESS_TEXT_OPERATIONS=os.getenv('PROGRESS_TEXT_OPERATIONS', 'true').lower() == 'true',
        
        # Error Handling Features (converted from PDF Error Handling)
        ERROR_HANDLING_ENABLED=os.getenv('ERROR_HANDLING_ENABLED', 'true').lower() == 'true',
        ERROR_CONTINUE_ON_FAILURE=os.getenv('ERROR_CONTINUE_ON_FAILURE', 'true').lower() == 'true',
        ERROR_SKIP_MISSING_FILES=os.getenv('ERROR_SKIP_MISSING_FILES', 'true').lower() == 'true',
        ERROR_LOG_DETAILED=os.getenv('ERROR_LOG_DETAILED', 'true').lower() == 'true',
        ERROR_CREATE_PLACEHOLDER=os.getenv('ERROR_CREATE_PLACEHOLDER', 'true').lower() == 'true',
        ERROR_NOTIFY_ON_FAILURE=os.getenv('ERROR_NOTIFY_ON_FAILURE', 'true').lower() == 'true',
        ERROR_MAX_FAILURES=int(os.getenv('ERROR_MAX_FAILURES', '10')),
        ERROR_RETRY_ATTEMPTS=int(os.getenv('ERROR_RETRY_ATTEMPTS', '3')),
        ERROR_RETRY_DELAY=float(os.getenv('ERROR_RETRY_DELAY', '1.0')),
        ERROR_FALLBACK_STRATEGY=os.getenv('ERROR_FALLBACK_STRATEGY', 'graceful'),

        # Volume Configuration (converted from PDF Volume)
        VOLUME_NUMBER=int(os.getenv('VOLUME_NUMBER', '1')),
        VOLUME_FORMAT=os.getenv('VOLUME_FORMAT', '02d'),
        QA_PAIRS_PER_VOLUME=int(os.getenv('QA_PAIRS_PER_VOLUME', '100')),
        
        # Output Directory Configuration (converted from PDF Output)
        OUTPUT_DIR=os.getenv('OUTPUT_DIR', 'images'),
        COVERS_DIR=os.getenv('COVERS_DIR', 'images/covers'),
        TOC_DIR=os.getenv('TOC_DIR', 'images/toc'),
        COMPILATIONS_DIR=os.getenv('COMPILATIONS_DIR', 'images/compilations'),
        TEMP_DIR=os.getenv('TEMP_DIR', 'images/temp'),
        INDIVIDUAL_DIR=os.getenv('INDIVIDUAL_DIR', 'images/individual'),
        
        # Image Quality Settings
        IMAGE_WIDTH=int(os.getenv('IMAGE_WIDTH', '1072')),
        IMAGE_HEIGHT=int(os.getenv('IMAGE_HEIGHT', '1792')),
        IMAGE_QUALITY=int(os.getenv('IMAGE_QUALITY', '95')),
        IMAGE_STYLE=os.getenv('IMAGE_STYLE', 'photographic'),
        IMAGE_ASPECT_RATIO=os.getenv('IMAGE_ASPECT_RATIO', '9:16'),
        
        # Text Overlay Settings
        MAX_CHARS_PER_LINE=int(os.getenv('MAX_CHARS_PER_LINE', '35')),
        MAX_TEXT_LINES_ANSWER=int(os.getenv('MAX_TEXT_LINES_ANSWER', '12')),
        LINE_HEIGHT=int(os.getenv('LINE_HEIGHT', '72')),
        TEXT_AREA_START=int(os.getenv('TEXT_AREA_START', '40')),
                    BRAND_TEXT=os.getenv('BRAND_TEXT', 'ASK: Daily Research'),
        BRAND_X_POSITION=int(os.getenv('BRAND_X_POSITION', '40')),
        BRAND_Y_OFFSET=int(os.getenv('BRAND_Y_OFFSET', '100')),
        TEXT_LEFT_MARGIN=int(os.getenv('TEXT_LEFT_MARGIN', '40')),
        SHADOW_OFFSET=int(os.getenv('SHADOW_OFFSET', '2')),
        
        # Font Settings
        FONT_FILE_PATH=os.getenv('FONT_FILE_PATH', 'fonts/arial.ttf'),
        MAIN_FONT_SIZE=int(os.getenv('MAIN_FONT_SIZE', '32')),
        BRAND_FONT_SIZE=int(os.getenv('BRAND_FONT_SIZE', '24')),
        NUMBER_FONT_SIZE=int(os.getenv('NUMBER_FONT_SIZE', '20')),
        
        # TOC Content Settings
        TOC_MAX_QUESTIONS_PER_CATEGORY=int(os.getenv('TOC_MAX_QUESTIONS_PER_CATEGORY', '5')),
        TOC_QUESTION_PREVIEW_LENGTH=int(os.getenv('TOC_QUESTION_PREVIEW_LENGTH', '50')),
        TOC_SHOW_THEME_COUNTS=os.getenv('TOC_SHOW_THEME_COUNTS', 'true').lower() == 'true',
        TOC_SHOW_GENERATION_DATE=os.getenv('TOC_SHOW_GENERATION_DATE', 'true').lower() == 'true',
        
        # Compilation Settings
        COMPILATION_MAX_IMAGES_PER_PAGE=int(os.getenv('COMPILATION_MAX_IMAGES_PER_PAGE', '4')),
        COMPILATION_LAYOUT_GRID=os.getenv('COMPILATION_LAYOUT_GRID', 'true').lower() == 'true',
        COMPILATION_INCLUDE_CATEGORIES=os.getenv('COMPILATION_INCLUDE_CATEGORIES', 'true').lower() == 'true',

        PLACEHOLDER_TEXT_COLOR=os.getenv('PLACEHOLDER_TEXT_COLOR', '#666666'),
        PLACEHOLDER_TEXT=os.getenv('PLACEHOLDER_TEXT', 'Content Unavailable'),
        
        # Timing and Performance
        IMAGE_GENERATION_TIMEOUT=int(os.getenv('IMAGE_GENERATION_TIMEOUT', '300')),
        BATCH_SIZE=int(os.getenv('BATCH_SIZE', '5')),
        PARALLEL_PROCESSING=os.getenv('PARALLEL_PROCESSING', 'false').lower() == 'true',
        RETRY_ATTEMPTS=int(os.getenv('RETRY_ATTEMPTS', '3')),
        
        # Output Formats
        OUTPUT_FORMAT=os.getenv('OUTPUT_FORMAT', 'jpg'),
        COMPRESSION_QUALITY=int(os.getenv('COMPRESSION_QUALITY', '95')),
        INCLUDE_METADATA=os.getenv('INCLUDE_METADATA', 'true').lower() == 'true',
        GENERATE_THUMBNAILS=os.getenv('GENERATE_THUMBNAILS', 'false').lower() == 'true',
        
        # Quality Control
        QUALITY_CHECK_ENABLED=os.getenv('QUALITY_CHECK_ENABLED', 'true').lower() == 'true',
        MIN_IMAGE_SIZE=int(os.getenv('MIN_IMAGE_SIZE', '100000')),
        MAX_IMAGE_SIZE=int(os.getenv('MAX_IMAGE_SIZE', '10000000')),
        VALIDATE_IMAGE_INTEGRITY=os.getenv('VALIDATE_IMAGE_INTEGRITY', 'true').lower() == 'true',
        
        # Backup and Recovery
        BACKUP_ORIGINAL_IMAGES=os.getenv('BACKUP_ORIGINAL_IMAGES', 'true').lower() == 'true',
        BACKUP_RETENTION_DAYS=int(os.getenv('BACKUP_RETENTION_DAYS', '7')),
        RECOVERY_MODE=os.getenv('RECOVERY_MODE', 'false').lower() == 'true',
        
        # Notifications
        NOTIFY_ON_COMPLETION=os.getenv('NOTIFY_ON_COMPLETION', 'true').lower() == 'true',
        NOTIFY_ON_ERROR=os.getenv('NOTIFY_ON_ERROR', 'true').lower() == 'true',
        NOTIFY_ON_PROGRESS=os.getenv('NOTIFY_ON_PROGRESS', 'false').lower() == 'true',
        
        # Debugging
        DEBUG_MODE=os.getenv('DEBUG_MODE', 'false').lower() == 'true',
        VERBOSE_OUTPUT=os.getenv('VERBOSE_OUTPUT', 'false').lower() == 'true',
        SAVE_INTERMEDIATE_FILES=os.getenv('SAVE_INTERMEDIATE_FILES', 'false').lower() == 'true'
    )
    
    # Initialize image generation system
    image_system = ImageGenerationSystem(config)
    
    # Load Q&A pairs from log.csv
    try:
        qa_pairs = read_log_csv()
        if not qa_pairs:
            log.error("No Q&A pairs found in log.csv")
            return
        
        # Generate complete image set
        results = image_system.generate_complete_image_set(qa_pairs, volume_number=1)
        
        log.info(" Image generation system completed successfully!")
        
    except Exception as e:
        log.error(f" Image generation system failed: {e}")
        raise

if __name__ == "__main__":
    main()


def get_performance_stats():
    """Get performance statistics"""
    return performance_monitor.get_stats()

def reset_performance_stats():
    """Reset performance statistics"""
    global performance_monitor
    performance_monitor = PerformanceMonitor()
    log.info("Performance statistics reset")

def get_generation_history():
    """Get recent image generation history"""
    stats = performance_monitor.get_stats()
    return {
        'total_generated': stats['successful_operations'],
        'total_failed': stats['failed_operations'],
        'success_rate': stats['success_rate'],
        'total_time': stats['total_time'],
        'image_generation_time': stats['image_generation_time'],
        'text_overlay_time': stats['text_overlay_time'],
        'cover_creation_time': stats['cover_creation_time'],
        'toc_creation_time': stats['toc_creation_time']
    }

def validate_image_quality(image_path: str) -> Tuple[bool, str]:
    """Validate generated image quality"""
    try:
        if not os.path.exists(image_path):
            return False, f"Image file does not exist: {image_path}"
        
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            return False, f"Image file is empty: {image_path}"
        
        if file_size < 1024:  # Less than 1KB
            return False, f"Image file too small: {file_size} bytes"
        
        if file_size > 10 * 1024 * 1024:  # More than 10MB
            return False, f"Image file too large: {file_size} bytes"
        
        return True, "Image quality valid"
    except Exception as e:
        return False, f"Image quality validation error: {str(e)}"

def get_system_status():
    """Get current system status"""
    stats = performance_monitor.get_stats()
    return {
        'system_ready': True,
        'performance_metrics': stats,
        'environment_valid': validate_environment()[0],
        'recommendations': [
            'Monitor image generation performance',
            'Optimize batch processing for large datasets',
            'Implement caching for frequently used images',
            'Add parallel processing for faster generation',
            'Monitor memory usage during large operations'
        ]
    }

def optimize_batch_processing(qa_pairs: List[Dict], batch_size: int = 5) -> List[List[Dict]]:
    """Optimize Q&A pairs for batch processing"""
    try:
        batches = []
        for i in range(0, len(qa_pairs), batch_size):
            batch = qa_pairs[i:i + batch_size]
            batches.append(batch)
        
        log.info(f"Created {len(batches)} batches of size {batch_size}")
        return batches
    except Exception as e:
        log.error(f"Error optimizing batch processing: {e}")
        return [qa_pairs]

def validate_configuration(config: ImageGenerationConfig) -> Tuple[bool, str]:
    """Validate configuration settings"""
    try:
        # Check essential settings
        if not config.CREATE_INDIVIDUAL_IMAGES and not config.CREATE_FINAL_COMPILATION:
            return False, "At least one image generation feature must be enabled"
        
        if config.IMAGE_WIDTH <= 0 or config.IMAGE_HEIGHT <= 0:
            return False, "Invalid image dimensions"
        
        if config.IMAGE_QUALITY < 1 or config.IMAGE_QUALITY > 100:
            return False, "Invalid image quality setting"
        
        if config.ERROR_MAX_FAILURES < 1:
            return False, "Invalid error max failures setting"
        
        return True, "Configuration valid"
    except Exception as e:
        return False, f"Configuration validation error: {str(e)}"

def get_system_health():
    """Get system health status"""
    try:
        stats = performance_monitor.get_stats()
        env_valid = validate_environment()[0]
        
        health_score = 0
        issues = []
        
        # Check success rate
        if stats['success_rate'] >= 90:
            health_score += 30
        elif stats['success_rate'] >= 70:
            health_score += 20
            issues.append("Low success rate")
        else:
            issues.append("Very low success rate")
        
        # Check environment
        if env_valid:
            health_score += 20
        else:
            issues.append("Environment configuration issues")
        
        # Check performance
        if stats['total_time'] > 0:
            avg_time = stats['total_time'] / stats['total_operations']
            if avg_time < 5.0:
                health_score += 25
            elif avg_time < 10.0:
                health_score += 15
                issues.append("Slow performance")
            else:
                issues.append("Very slow performance")
        
        # Check error rate
        error_rate = stats['failed_operations'] / max(stats['total_operations'], 1)
        if error_rate < 0.1:
            health_score += 25
        elif error_rate < 0.3:
            health_score += 15
            issues.append("High error rate")
        else:
            issues.append("Very high error rate")
        
        return {
            'health_score': health_score,
            'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical',
            'issues': issues,
            'recommendations': [
                'Monitor error rates and success rates',
                'Optimize image generation parameters',
                'Check environment configuration',
                'Consider parallel processing for large datasets',
                'Implement caching mechanisms'
            ]
        }
    except Exception as e:
        return {
            'health_score': 0,
            'status': 'error',
            'issues': [f"Health check failed: {str(e)}"],
            'recommendations': ['Check system configuration and logs']
        }
