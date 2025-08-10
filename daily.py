#!/usr/bin/env python3
"""
Instagram Story Generator
Architecture Questions → Instagram Stories with Text Overlay
"""

import os
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import random

# Load environment variables
load_dotenv('ask.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{os.getenv('LOG_DIR', 'logs')}/execution.log")
    ]
)
log = logging.getLogger()

# Console logger
console_logger = logging.getLogger('console')
console_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_logger.addHandler(console_handler)

# Environment variables
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'black-forest-labs/FLUX.1-schnell-free')
IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '1072'))
IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', '1792'))
INFERENCE_STEPS = int(os.getenv('INFERENCE_STEPS', '4'))
GUIDANCE_SCALE = float(os.getenv('GUIDANCE_SCALE', '7.5'))
IMAGES_DIR = os.getenv('IMAGES_DIR', 'images')
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))
DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', '30'))
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '95'))

# Validate API key
if not TOGETHER_API_KEY:
    log.error("❌ TOGETHER_API_KEY environment variable is not set!")
    console_logger.error("❌ TOGETHER_API_KEY environment variable is not set!")
    exit(1)

if not TOGETHER_API_KEY.startswith('tgsk_'):
    log.warning("⚠️  TOGETHER_API_KEY format may be invalid (should start with 'tgsk_')")
    console_logger.warning("⚠️  TOGETHER_API_KEY format may be invalid (should start with 'tgsk_')")

log.info(f"✅ API key configured: {TOGETHER_API_KEY[:10]}...")
console_logger.info(f"✅ API key configured: {TOGETHER_API_KEY[:10]}...")

def test_api_connection():
    """Test API connection to verify the key works"""
    try:
        url = os.getenv('TOGETHER_API_URL', 'https://api.together.xyz/v1') + '/models'
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        log.info("Testing API connection...")
        console_logger.info("Testing API connection...")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            log.info("✅ API connection test successful")
            console_logger.info("✅ API connection test successful")
            return True
        else:
            log.error(f"❌ API connection test failed: {response.status_code} - {response.text[:200]}")
            console_logger.error(f"❌ API connection test failed: {response.status_code}")
            return False
            
    except Exception as e:
        log.error(f"❌ API connection test failed: {e}")
        console_logger.error(f"❌ API connection test failed: {e}")
        return False

def get_used_questions():
    """Read previously used questions from log.csv to avoid duplicates"""
    used_questions = set()
    try:
        if os.path.exists('log.csv'):
            import csv
            with open('log.csv', 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'question' in row and row['question'].strip():
                        used_questions.add(row['question'].strip())
    except Exception as e:
        log.warning(f"Could not read previous questions from log.csv: {e}")
    return used_questions

def get_next_image_number():
    """Get the next image number based on existing images in log.csv"""
    try:
        if os.path.exists('log.csv'):
            import csv
            max_number = 0
            with open('log.csv', 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'image_filename' in row and row['image_filename'].strip():
                        # Extract number from filename like "ASK-01-architecture.jpg"
                        filename = row['image_filename']
                        if filename.startswith('ASK-') and '-' in filename:
                            try:
                                number_part = filename.split('-')[1]
                                number = int(number_part)
                                max_number = max(max_number, number)
                            except (ValueError, IndexError):
                                continue
            return max_number + 1
        else:
            return 1
    except Exception as e:
        log.warning(f"Could not read image numbers from log.csv: {e}")
        return 1

def get_questions_by_discipline():
    """Get one question from each discipline category, avoiding duplicates"""
    disciplines = {
        'architecture': os.getenv('ARCHITECTURE_QUESTIONS', '').split('|'),
        'construction': os.getenv('CONSTRUCTION_QUESTIONS', '').split('|'),
        'design': os.getenv('DESIGN_QUESTIONS', '').split('|'),
        'engineering': os.getenv('ENGINEERING_QUESTIONS', '').split('|'),
        'interiors': os.getenv('INTERIOR_QUESTIONS', '').split('|'),
        'planning': os.getenv('PLANNING_QUESTIONS', '').split('|'),
        'urbanism': os.getenv('URBANISM_QUESTIONS', '').split('|')
    }
    
    # Get previously used questions to avoid duplicates
    used_questions = get_used_questions()
    
    questions = {}
    for discipline, question_list in disciplines.items():
        valid_questions = [q.strip() for q in question_list if q.strip()]
        # Filter out previously used questions
        available_questions = [q for q in valid_questions if q not in used_questions]
        
        if available_questions:
            questions[discipline] = random.choice(available_questions)
        else:
            # If all questions have been used, use fallback questions
            fallback_questions = {
                'architecture': os.getenv('FALLBACK_ARCHITECTURE', 'How can we design buildings that respond to climate change?'),
                'construction': os.getenv('FALLBACK_CONSTRUCTION', 'How can we build more efficiently with less waste?'),
                'design': os.getenv('FALLBACK_DESIGN', 'How can we design spaces that adapt to changing needs?'),
                'engineering': os.getenv('FALLBACK_ENGINEERING', 'How can we make buildings more resilient to disasters?'),
                'interiors': os.getenv('FALLBACK_INTERIORS', 'How can interiors reflect the building\'s purpose?'),
                'planning': os.getenv('FALLBACK_PLANNING', 'How can we plan cities for people, not cars?'),
                'urbanism': os.getenv('FALLBACK_URBANISM', 'How can we create vibrant public spaces?')
            }
            questions[discipline] = fallback_questions[discipline]
            log.info(f"All {discipline} questions used, using fallback question")
    
    return questions

def log_single_question(discipline, question, image_filename):
    """Log a single question and image to log.csv immediately"""
    try:
        import csv
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists('log.csv')
        
        with open('log.csv', 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write headers if file doesn't exist
            if not file_exists:
                writer.writerow(['timestamp', 'discipline', 'question', 'image_filename'])
            
            writer.writerow([timestamp, discipline, question, image_filename])
            
        log.info(f"Logged {discipline} question and image to log.csv: {image_filename}")
    except Exception as e:
        log.error(f"Error logging question to CSV: {e}")

def log_questions(questions, generated_images=None):
    """Log questions to log.csv with timestamp and image information"""
    try:
        import csv
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists('log.csv')
        
        with open('log.csv', 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write headers if file doesn't exist
            if not file_exists:
                writer.writerow(['timestamp', 'discipline', 'question', 'image_filename'])
            
            for discipline, question in questions.items():
                image_filename = ""
                if generated_images and discipline in generated_images:
                    image_filename = os.path.basename(generated_images[discipline])
                
                writer.writerow([timestamp, discipline, question, image_filename])
            
        log.info(f"Questions and images logged to log.csv")
    except Exception as e:
        log.error(f"Error logging questions to CSV: {e}")

def get_style_for_discipline(discipline):
    """Get appropriate architectural style for each discipline"""
    styles = {
        'architecture': os.getenv('ARCHITECTURE_STYLES', 'Contemporary').split(','),
        'construction': os.getenv('CONSTRUCTION_STYLES', 'Contemporary').split(','),
        'design': os.getenv('DESIGN_STYLES', 'Contemporary').split(','),
        'engineering': os.getenv('ENGINEERING_STYLES', 'Contemporary').split(','),
        'interiors': os.getenv('INTERIOR_STYLES', 'Contemporary').split(','),
        'planning': os.getenv('PLANNING_STYLES', 'Contemporary').split(','),
        'urbanism': os.getenv('URBANISM_STYLES', 'Contemporary').split(',')
    }
    default_style = os.getenv('DEFAULT_STYLE', 'Contemporary')
    return random.choice(styles.get(discipline, [default_style]))

def generate_image_with_retry(prompt, discipline, image_number, max_retries=None, timeout=None):
    """Generate Instagram story image using Together.ai API with retry logic"""
    
    if max_retries is None:
        max_retries = MAX_RETRIES
    if timeout is None:
        timeout = API_TIMEOUT
    
    for attempt in range(max_retries):
        try:
            url = os.getenv('TOGETHER_API_URL', 'https://api.together.xyz/v1') + '/images/generations'
            
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            style = get_style_for_discipline(discipline)
            formatted_prompt = f"Architectural visualization, {discipline} focus, {style} style: {prompt}"
            
            payload = {
                "model": IMAGE_MODEL,
                "prompt": formatted_prompt,
                "width": IMAGE_WIDTH,
                "height": IMAGE_HEIGHT,
                "steps": INFERENCE_STEPS,
                "guidance_scale": GUIDANCE_SCALE,
                "seed": random.randint(1, 999999999)
            }
            
            log.info(f"Generating {discipline} image {image_number} with {style} style (attempt {attempt + 1}/{max_retries})")
            
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            
            if response.status_code != 200:
                error_text = response.text[:200] if response.text else "No response text"
                log.error(f"API Error {response.status_code}: {error_text}")
                
                retryable_codes = [int(x) for x in os.getenv('RETRYABLE_STATUS_CODES', '408,429,500,502,503,504').split(',')]
                if response.status_code in retryable_codes:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))
                        log.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                else:
                    raise Exception(f"API returned status {response.status_code}: {error_text}")
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                log.error(f"Invalid API response: {data}")
                raise Exception("Invalid API response format")
            
            image_url = data['data'][0]['url']
            
            # Download and save image
            img_response = requests.get(image_url, timeout=DOWNLOAD_TIMEOUT)
            img_response.raise_for_status()
            
            filename = f"{IMAGES_DIR}/ASK-{image_number:02d}-{discipline}.jpg"
            
            with open(filename, 'wb') as f:
                f.write(img_response.content)
            
            log.info(f"Generated {discipline} image {image_number}: {filename}")
            return filename
            
        except requests.exceptions.Timeout:
            log.error(f"Timeout error generating {discipline} image {image_number} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))
                log.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Timeout after {max_retries} attempts")
                
        except requests.exceptions.RequestException as e:
            log.error(f"Network error generating {discipline} image {image_number} (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))
                log.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Network error after {max_retries} attempts: {e}")
                        
        except Exception as e:
            log.error(f"Error generating {discipline} image {image_number} (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))
                log.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Image generation failed after {max_retries} attempts: {e}")
    
    raise Exception(f"Failed to generate {discipline} image {image_number} after {max_retries} attempts")

def add_text_overlay(image_path, prompt, image_number):
    """Add professional text overlay to Instagram story image"""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Font settings
        font_file = os.getenv('FONT_FILE', 'arial.ttf')
        main_font_size = int(os.getenv('MAIN_FONT_SIZE', '56'))
        brand_font_size = int(os.getenv('BRAND_FONT_SIZE', '36'))
        number_font_size = int(os.getenv('NUMBER_FONT_SIZE', '28'))
        
        try:
            main_font = ImageFont.truetype(font_file, main_font_size)
            brand_font = ImageFont.truetype(font_file, brand_font_size)
            number_font = ImageFont.truetype(font_file, number_font_size)
        except:
            main_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()
            number_font = ImageFont.load_default()
        
        # Create overlay
        overlay_height = int(os.getenv('OVERLAY_HEIGHT', '400'))
        overlay_y = IMAGE_HEIGHT - overlay_height
        
        # Gradient overlay
        overlay = Image.new('RGBA', (IMAGE_WIDTH, overlay_height), (0, 0, 0, 0))
        for i in range(overlay_height):
            alpha = int(200 - (i * 100 / overlay_height))
            alpha = max(100, min(200, alpha))
            line_overlay = Image.new('RGBA', (IMAGE_WIDTH, 1), (0, 0, 0, alpha))
            overlay.paste(line_overlay, (0, i))
        
        img.paste(overlay, (0, overlay_y), overlay)
        
        # Separator line
        separator_line_color = tuple(int(x) for x in os.getenv('SEPARATOR_LINE_COLOR', '255,255,255,40').split(','))
        separator_line_width = int(os.getenv('SEPARATOR_LINE_WIDTH', '1'))
        draw.line([(50, overlay_y + 20), (IMAGE_WIDTH - 50, overlay_y + 20)], fill=separator_line_color, width=separator_line_width)
        
        # Prepare prompt text
        max_chars_per_line = int(os.getenv('MAX_CHARS_PER_LINE', '35'))
        words = prompt.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars_per_line:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        max_text_lines = int(os.getenv('MAX_TEXT_LINES', '2'))
        lines = lines[:max_text_lines]  # Limit to max lines
        
        # Draw prompt text
        line_height = int(os.getenv('LINE_HEIGHT', '72'))
        text_start_offset = int(os.getenv('TEXT_START_OFFSET', '80'))
        text_start_y = overlay_y + text_start_offset
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=main_font)
            text_width = bbox[2] - bbox[0]
            x = (IMAGE_WIDTH - text_width) // 2
            y = text_start_y + i * line_height
            
            # Shadow
            shadow_offset = int(os.getenv('SHADOW_OFFSET', '2'))
            text_shadow_color = tuple(int(x) for x in os.getenv('TEXT_SHADOW_COLOR', '0,0,0,100').split(','))
            draw.text((x + shadow_offset, y + shadow_offset), line, fill=text_shadow_color, font=main_font)
            text_color = os.getenv('TEXT_COLOR', 'white')
            draw.text((x, y), line, fill=text_color, font=main_font)
        
        # Calculate brand position
        brand_text_offset = int(os.getenv('BRAND_TEXT_OFFSET', '56'))
        last_prompt_y = text_start_y + (len(lines) - 1) * line_height + brand_text_offset
        
        # Separator line
        separator_line_color = tuple(int(x) for x in os.getenv('SEPARATOR_LINE_COLOR', '255,255,255,40').split(','))
        separator_line_width = int(os.getenv('SEPARATOR_LINE_WIDTH', '1'))
        draw.line([(50, last_prompt_y + 40), (IMAGE_WIDTH - 50, last_prompt_y + 40)], fill=separator_line_color, width=separator_line_width)
        
        # Brand text
        brand_text = os.getenv('BRAND_TEXT', 'ASK: Daily Architectural Research')
        bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        brand_text_width = bbox[2] - bbox[0]
        brand_x_position = int(os.getenv('BRAND_X_POSITION', '30'))
        brand_y_offset = int(os.getenv('BRAND_Y_OFFSET', '100'))
        brand_x = brand_x_position
        brand_y = last_prompt_y + brand_y_offset
        
        shadow_color = tuple(int(x) for x in os.getenv('SHADOW_COLOR', '0,0,0,80').split(','))
        draw.text((brand_x + 1, brand_y + 1), brand_text, fill=shadow_color, font=brand_font)
        draw.text((brand_x, brand_y), brand_text, fill='white', font=brand_font)
        
        # Image number
        number_format = os.getenv('NUMBER_FORMAT', '#{:02d}')
        number_text = number_format.format(image_number)
        bbox = draw.textbbox((0, 0), number_text, font=number_font)
        number_text_width = bbox[2] - bbox[0]
        number_x_offset = int(os.getenv('NUMBER_X_OFFSET', '30'))
        number_x = IMAGE_WIDTH - number_text_width - number_x_offset
        number_y = brand_y
        
        draw.text((number_x + 1, number_y + 1), number_text, fill=shadow_color, font=number_font)
        draw.text((number_x, number_y), number_text, fill='white', font=number_font)
        
        img.save(image_path, quality=IMAGE_QUALITY)
        log.info(f"Added text overlay to image: {image_path}")
                
    except Exception as e:
        log.error(f"Error adding text overlay to {image_path}: {e}")

def main():
    """Main pipeline: Generate questions → Create Instagram stories with text overlay"""
    try:
        Path(IMAGES_DIR).mkdir(exist_ok=True)
        Path(os.getenv('LOG_DIR', 'logs')).mkdir(exist_ok=True)
        
        console_logger.info("Starting Instagram Story Generation...")
        log_separator_length = int(os.getenv('LOG_SEPARATOR_LENGTH', '60'))
        log.info("=" * log_separator_length)
        log.info("Starting Instagram Story Generation")
        log.info("=" * log_separator_length)
        
        # Test API connection first
        if not test_api_connection():
            console_logger.error("❌ API connection test failed. Exiting.")
            log.error("❌ API connection test failed. Exiting.")
            exit(1)
        
        # Generate questions
        console_logger.info("Generating questions for each discipline...")
        questions = get_questions_by_discipline()
        
        # Generate images
        console_logger.info("Generating Instagram stories...")
        start_image_number = get_next_image_number()
        console_logger.info(f"Starting image numbering from: {start_image_number}")
        image_number = start_image_number
        generated_images = {}  # Track images by discipline
        
        for discipline, prompt in questions.items():
            try:
                console_logger.info(f"Generating {discipline} story (Image #{image_number})...")
                
                image_path = generate_image_with_retry(prompt, discipline, image_number)
                add_text_overlay(image_path, prompt, image_number)
                
                # Log immediately after successful generation
                image_filename = os.path.basename(image_path)
                log_single_question(discipline, prompt, image_filename)
                
                generated_images[discipline] = image_path
                image_number += 1
                
                time.sleep(RATE_LIMIT_DELAY)
                
            except Exception as e:
                console_logger.error(f"Failed to generate {discipline} story: {e}")
                log.error(f"Failed to generate {discipline} story: {e}")
                continue
        
        # Success logging
        if generated_images:
            console_logger.info("SUCCESS! All Instagram stories created successfully")
            log.info("=" * log_separator_length)
            log.info("SUCCESS! All Instagram stories created successfully")
            log.info(f"Images generated: {len(generated_images)}")
            log.info("=" * log_separator_length)
            
            for discipline, prompt in questions.items():
                if discipline in generated_images:
                    log.info(f"Image ({discipline}): {prompt}")
            log.info("=" * log_separator_length)
        else:
            console_logger.error("Failed to generate any images")
            log.error("Failed to generate any images")
            
    except Exception as e:
        console_logger.error(f"Error in main function: {e}")
        log.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main() 