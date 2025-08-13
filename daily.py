#!/usr/bin/env python3  # Shebang for Unix-like systems
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
import csv

# Load environment variables from ask.env file
load_dotenv('ask.env')

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format with timestamp
    handlers=[
        logging.FileHandler(f"{os.getenv('LOG_DIR', 'logs')}/execution.log")  # Log to file
    ]
)
log = logging.getLogger()  # Get logger instance

# Console logger for user-friendly output
console_logger = logging.getLogger('console')  # Create separate console logger
console_logger.setLevel(logging.INFO)  # Set console logging level
console_handler = logging.StreamHandler()  # Create console handler
console_handler.setFormatter(logging.Formatter('%(message)s'))  # Simple format for console
console_logger.addHandler(console_handler)  # Add handler to console logger

# Environment variables - load from .env file with defaults
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')  # API key for Together.ai
IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'black-forest-labs/FLUX.1-schnell-free')  # AI model name
IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '1072'))  # Image width in pixels
IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', '1792'))  # Image height in pixels
INFERENCE_STEPS = int(os.getenv('INFERENCE_STEPS', '4'))  # AI inference steps
GUIDANCE_SCALE = float(os.getenv('GUIDANCE_SCALE', '7.5'))  # AI guidance scale
IMAGES_DIR = os.getenv('IMAGES_DIR', 'images')  # Directory for generated images
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))  # Delay between API calls
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))  # Maximum retry attempts
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '60'))  # API request timeout
DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', '30'))  # Image download timeout
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '95'))  # JPEG quality setting

# Validate API key - check if it exists
if not TOGETHER_API_KEY:  # Check if API key is missing
    log.error("❌ TOGETHER_API_KEY environment variable is not set!")  # Log error
    console_logger.error("❌ TOGETHER_API_KEY environment variable is not set!")  # Console error
    exit(1)  # Exit with error code

if not TOGETHER_API_KEY.startswith('tgp_'):  # Check API key format
    log.warning("⚠️  TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")  # Log warning
    console_logger.warning("⚠️  TOGETHER_API_KEY format may be invalid (should start with 'tgp_')")  # Console warning

log.info(f"✅ API key configured: {TOGETHER_API_KEY[:10]}...")  # Log successful configuration
console_logger.info(f"✅ API key configured: {TOGETHER_API_KEY[:10]}...")  # Console confirmation

def test_api_connection():
    """Test API connection to verify the key works"""
    try:
        url = os.getenv('TOGETHER_API_URL', 'https://api.together.xyz/v1') + '/models'  # API endpoint URL
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",  # Authorization header
            "Content-Type": "application/json"  # Content type header
        }
        
        log.info("Testing API connection...")  # Log test start
        console_logger.info("Testing API connection...")  # Console test start
        
        response = requests.get(url, headers=headers, timeout=30)  # Make API request
        
        if response.status_code == 200:  # Check if request was successful
            log.info("✅ API connection test successful")  # Log success
            console_logger.info("✅ API connection test successful")  # Console success
            return True  # Return success
        else:
            log.error(f"❌ API connection test failed: {response.status_code} - {response.text[:200]}")  # Log error details
            console_logger.error(f"❌ API connection test failed: {response.status_code}")  # Console error
            return False  # Return failure
            
    except Exception as e:  # Catch any exceptions
        log.error(f"❌ API connection test failed: {e}")  # Log exception
        console_logger.error(f"❌ API connection test failed: {e}")  # Console exception
        return False  # Return failure

def get_used_questions():
    """Read previously used questions from log.csv to avoid duplicates"""
    used_questions = set()  # Initialize empty set for used questions
    try:
        if os.path.exists('log.csv'):  # Check if log file exists
            import csv  # Import CSV module
            with open('log.csv', 'r', encoding='utf-8', newline='') as f:  # Open CSV file
                reader = csv.DictReader(f)  # Create CSV reader
                for row in reader:  # Iterate through rows
                    if 'question' in row and row['question'].strip():  # Check if question exists and is not empty
                        used_questions.add(row['question'].strip())  # Add to used questions set
    except Exception as e:  # Catch any exceptions
        log.warning(f"Could not read previous questions from log.csv: {e}")  # Log warning
    return used_questions  # Return set of used questions

def get_next_image_number():
    """Get the next image number based on existing images in log.csv"""
    try:
        if os.path.exists('log.csv'):  # Check if log file exists
            import csv  # Import CSV module
            max_number = 0  # Initialize maximum number
            with open('log.csv', 'r', encoding='utf-8', newline='') as f:  # Open CSV file
                reader = csv.DictReader(f)  # Create CSV reader
                for row in reader:  # Iterate through rows
                    if 'image_filename' in row and row['image_filename'].strip():  # Check if filename exists
                        # Extract number from filename like "ASK-01-architecture.jpg"
                        filename = row['image_filename']  # Get filename
                        if filename.startswith('ASK-') and '-' in filename:  # Check filename format
                            try:
                                number_part = filename.split('-')[1]  # Extract number part
                                number = int(number_part)  # Convert to integer
                                max_number = max(max_number, number)  # Update maximum number
                            except (ValueError, IndexError):  # Catch conversion errors
                                continue  # Skip invalid entries
            return max_number + 1  # Return next number
        else:
            return 1  # Return 1 if no log file exists
    except Exception as e:  # Catch any exceptions
        log.warning(f"Could not read image numbers from log.csv: {e}")  # Log warning
        return 1  # Return 1 as fallback

def get_questions_by_discipline():
    """Get one question from each discipline category, avoiding duplicates"""
    disciplines = {  # Dictionary of discipline questions
        'architecture': os.getenv('ARCHITECTURE_QUESTIONS', '').split('|'),  # Architecture questions
        'construction': os.getenv('CONSTRUCTION_QUESTIONS', '').split('|'),  # Construction questions
        'design': os.getenv('DESIGN_QUESTIONS', '').split('|'),  # Design questions
        'engineering': os.getenv('ENGINEERING_QUESTIONS', '').split('|'),  # Engineering questions
        'interiors': os.getenv('INTERIOR_QUESTIONS', '').split('|'),  # Interior questions
        'planning': os.getenv('PLANNING_QUESTIONS', '').split('|'),  # Planning questions
        'urbanism': os.getenv('URBANISM_QUESTIONS', '').split('|')  # Urbanism questions
    }
    
    # Get previously used questions to avoid duplicates
    used_questions = get_used_questions()  # Get set of used questions
    
    questions = {}  # Initialize questions dictionary
    for discipline, question_list in disciplines.items():  # Iterate through disciplines
        valid_questions = [q.strip() for q in question_list if q.strip()]  # Filter valid questions
        # Filter out previously used questions
        available_questions = [q for q in valid_questions if q not in used_questions]  # Get available questions
        
        if available_questions:  # Check if questions are available
            questions[discipline] = random.choice(available_questions)  # Choose random question
        else:
            # If all questions have been used, use fallback questions
            fallback_questions = {  # Dictionary of fallback questions
                'architecture': os.getenv('FALLBACK_ARCHITECTURE', 'How can we design buildings that respond to climate change?'),
                'construction': os.getenv('FALLBACK_CONSTRUCTION', 'How can we build more efficiently with less waste?'),
                'design': os.getenv('FALLBACK_DESIGN', 'How can we design spaces that adapt to changing needs?'),
                'engineering': os.getenv('FALLBACK_ENGINEERING', 'How can we make buildings more resilient to disasters?'),
                'interiors': os.getenv('FALLBACK_INTERIORS', 'How can interiors reflect the building\'s purpose?'),
                'planning': os.getenv('FALLBACK_PLANNING', 'How can we plan cities for people, not cars?'),
                'urbanism': os.getenv('FALLBACK_URBANISM', 'How can we create vibrant public spaces?')
            }
            questions[discipline] = fallback_questions[discipline]  # Use fallback question
            log.info(f"All {discipline} questions used, using fallback question")  # Log fallback usage
    
    return questions  # Return questions dictionary

def log_single_question(discipline, question, image_filename):
    """Log a single question and image to log.csv immediately"""
    try:
        import csv  # Import CSV module
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists('log.csv')  # Check if log file exists
        
        with open('log.csv', 'a', encoding='utf-8', newline='') as f:  # Open CSV file in append mode
            writer = csv.writer(f)  # Create CSV writer
            
            # Write headers if file doesn't exist
            if not file_exists:  # Check if file is new
                writer.writerow(['timestamp', 'discipline', 'question', 'image_filename'])  # Write headers
            
            writer.writerow([timestamp, discipline, question, image_filename])  # Write data row
            
        log.info(f"Logged {discipline} question and image to log.csv: {image_filename}")  # Log success
    except Exception as e:  # Catch any exceptions
        log.error(f"Error logging question to CSV: {e}")  # Log error

def log_questions(questions, generated_images=None):
    """Log questions to log.csv with timestamp and image information"""
    try:
        import csv  # Import CSV module
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists('log.csv')  # Check if log file exists
        
        with open('log.csv', 'a', encoding='utf-8', newline='') as f:  # Open CSV file in append mode
            writer = csv.writer(f)  # Create CSV writer
            
            # Write headers if file doesn't exist
            if not file_exists:  # Check if file is new
                writer.writerow(['timestamp', 'discipline', 'question', 'image_filename'])  # Write headers
            
            for discipline, question in questions.items():  # Iterate through questions
                image_filename = ""  # Initialize empty filename
                if generated_images and discipline in generated_images:  # Check if image was generated
                    image_filename = os.path.basename(generated_images[discipline])  # Get filename
                
                writer.writerow([timestamp, discipline, question, image_filename])  # Write data row
            
        log.info(f"Questions and images logged to log.csv")  # Log success
    except Exception as e:  # Catch any exceptions
        log.error(f"Error logging questions to CSV: {e}")  # Log error

def get_style_for_discipline(discipline):
    """Get appropriate architectural style for each discipline"""
    styles = {  # Dictionary of styles by discipline
        'architecture': os.getenv('ARCHITECTURE_STYLES', 'Contemporary').split(','),  # Architecture styles
        'construction': os.getenv('CONSTRUCTION_STYLES', 'Contemporary').split(','),  # Construction styles
        'design': os.getenv('DESIGN_STYLES', 'Contemporary').split(','),  # Design styles
        'engineering': os.getenv('ENGINEERING_STYLES', 'Contemporary').split(','),  # Engineering styles
        'interiors': os.getenv('INTERIOR_STYLES', 'Contemporary').split(','),  # Interior styles
        'planning': os.getenv('PLANNING_STYLES', 'Contemporary').split(','),  # Planning styles
        'urbanism': os.getenv('URBANISM_STYLES', 'Contemporary').split(',')  # Urbanism styles
    }
    default_style = os.getenv('DEFAULT_STYLE', 'Contemporary')  # Get default style
    return random.choice(styles.get(discipline, [default_style]))  # Return random style

def generate_image_with_retry(prompt, discipline, image_number, max_retries=None, timeout=None):
    """Generate Instagram story image using Together.ai API with retry logic"""
    
    if max_retries is None:  # Check if max_retries not provided
        max_retries = MAX_RETRIES  # Use default max retries
    if timeout is None:  # Check if timeout not provided
        timeout = API_TIMEOUT  # Use default timeout
    
    for attempt in range(max_retries):  # Loop through retry attempts
        try:
            url = os.getenv('TOGETHER_API_URL', 'https://api.together.xyz/v1') + '/images/generations'  # API endpoint
            
            headers = {  # Request headers
                "Authorization": f"Bearer {TOGETHER_API_KEY}",  # Authorization header
                "Content-Type": "application/json"  # Content type header
            }
            
            style = get_style_for_discipline(discipline)  # Get style for discipline
            formatted_prompt = f"Architectural visualization, {discipline} focus, {style} style: {prompt}"  # Format prompt
            
            payload = {  # Request payload
                "model": IMAGE_MODEL,  # AI model name
                "prompt": formatted_prompt,  # Formatted prompt
                "width": IMAGE_WIDTH,  # Image width
                "height": IMAGE_HEIGHT,  # Image height
                "steps": INFERENCE_STEPS,  # Inference steps
                "guidance_scale": GUIDANCE_SCALE,  # Guidance scale
                "seed": random.randint(1, 999999999)  # Random seed
            }
            
            log.info(f"Generating {discipline} image {image_number} with {style} style (attempt {attempt + 1}/{max_retries})")  # Log generation start
            
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)  # Make API request
            
            if response.status_code != 200:  # Check if request failed
                error_text = response.text[:200] if response.text else "No response text"  # Get error text
                log.error(f"API Error {response.status_code}: {error_text}")  # Log error
                
                retryable_codes = [int(x) for x in os.getenv('RETRYABLE_STATUS_CODES', '408,429,500,502,503,504').split(',')]  # Get retryable codes
                if response.status_code in retryable_codes:  # Check if error is retryable
                    if attempt < max_retries - 1:  # Check if more retries available
                        wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))  # Calculate wait time
                        log.info(f"Retrying in {wait_time} seconds...")  # Log retry wait
                        time.sleep(wait_time)  # Wait before retry
                        continue  # Continue to next attempt
                else:
                    raise Exception(f"API returned status {response.status_code}: {error_text}")  # Raise non-retryable error
            
            data = response.json()  # Parse JSON response
            
            if 'data' not in data or not data['data']:  # Check if response has data
                log.error(f"Invalid API response: {data}")  # Log invalid response
                raise Exception("Invalid API response format")  # Raise format error
            
            image_url = data['data'][0]['url']  # Extract image URL
            
            # Download and save image
            img_response = requests.get(image_url, timeout=DOWNLOAD_TIMEOUT)  # Download image
            img_response.raise_for_status()  # Check download success
            
            filename = f"{IMAGES_DIR}/ASK-{image_number:02d}-{discipline}.jpg"  # Generate filename
            
            with open(filename, 'wb') as f:  # Open file for writing
                f.write(img_response.content)  # Write image data
            
            log.info(f"Generated {discipline} image {image_number}: {filename}")  # Log success
            return filename  # Return filename
            
        except requests.exceptions.Timeout:  # Catch timeout exceptions
            log.error(f"Timeout error generating {discipline} image {image_number} (attempt {attempt + 1}/{max_retries})")  # Log timeout
            if attempt < max_retries - 1:  # Check if more retries available
                wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))  # Calculate wait time
                log.info(f"Retrying in {wait_time} seconds...")  # Log retry wait
                time.sleep(wait_time)  # Wait before retry
            else:
                raise Exception(f"Timeout after {max_retries} attempts")  # Raise timeout error
                
        except requests.exceptions.RequestException as e:  # Catch request exceptions
            log.error(f"Network error generating {discipline} image {image_number} (attempt {attempt + 1}/{max_retries}): {e}")  # Log network error
            if attempt < max_retries - 1:  # Check if more retries available
                wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))  # Calculate wait time
                log.info(f"Retrying in {wait_time} seconds...")  # Log retry wait
                time.sleep(wait_time)  # Wait before retry
            else:
                raise Exception(f"Network error after {max_retries} attempts: {e}")  # Raise network error
                        
        except Exception as e:  # Catch any other exceptions
            log.error(f"Error generating {discipline} image {image_number} (attempt {attempt + 1}/{max_retries}): {e}")  # Log general error
            if attempt < max_retries - 1:  # Check if more retries available
                wait_time = (attempt + 1) * int(os.getenv('RETRY_DELAY_MULTIPLIER', '30'))  # Calculate wait time
                log.info(f"Retrying in {wait_time} seconds...")  # Log retry wait
                time.sleep(wait_time)  # Wait before retry
            else:
                raise Exception(f"Image generation failed after {max_retries} attempts: {e}")  # Raise generation error
    
    raise Exception(f"Failed to generate {discipline} image {image_number} after {max_retries} attempts")  # Raise final failure

def add_text_overlay(image_path, prompt, image_number):
    """Add professional text overlay to Instagram story image"""
    try:
        img = Image.open(image_path)  # Open image file
        draw = ImageDraw.Draw(img)  # Create drawing object
        
        # Font settings
        font_file = os.getenv('FONT_FILE', 'arial.ttf')  # Get font file path
        main_font_size = int(os.getenv('MAIN_FONT_SIZE', '56'))  # Main text font size
        brand_font_size = int(os.getenv('BRAND_FONT_SIZE', '36'))  # Brand text font size
        number_font_size = int(os.getenv('NUMBER_FONT_SIZE', '28'))  # Number font size
        
        try:
            main_font = ImageFont.truetype(font_file, main_font_size)  # Load main font
            brand_font = ImageFont.truetype(font_file, brand_font_size)  # Load brand font
            number_font = ImageFont.truetype(font_file, number_font_size)  # Load number font
        except:
            main_font = ImageFont.load_default()  # Use default font if loading fails
            brand_font = ImageFont.load_default()  # Use default font if loading fails
            number_font = ImageFont.load_default()  # Use default font if loading fails
        
        # Create overlay
        overlay_height = int(os.getenv('OVERLAY_HEIGHT', '400'))  # Overlay height in pixels
        overlay_y = IMAGE_HEIGHT - overlay_height  # Calculate overlay Y position
        
        # Gradient overlay
        overlay = Image.new('RGBA', (IMAGE_WIDTH, overlay_height), (0, 0, 0, 0))  # Create transparent overlay
        for i in range(overlay_height):  # Loop through overlay height
            alpha = int(200 - (i * 100 / overlay_height))  # Calculate alpha value
            alpha = max(100, min(200, alpha))  # Clamp alpha between 100-200
            line_overlay = Image.new('RGBA', (IMAGE_WIDTH, 1), (0, 0, 0, alpha))  # Create line overlay
            overlay.paste(line_overlay, (0, i))  # Paste line at position
        
        img.paste(overlay, (0, overlay_y), overlay)  # Paste overlay onto image
        
        # Separator line
        separator_line_color = tuple(int(x) for x in os.getenv('SEPARATOR_LINE_COLOR', '255,255,255,40').split(','))  # Get separator color
        separator_line_width = int(os.getenv('SEPARATOR_LINE_WIDTH', '1'))  # Get separator width
        draw.line([(50, overlay_y + 20), (IMAGE_WIDTH - 50, overlay_y + 20)], fill=separator_line_color, width=separator_line_width)  # Draw separator line
        
        # Prepare prompt text
        max_chars_per_line = int(os.getenv('MAX_CHARS_PER_LINE', '35'))  # Maximum characters per line
        words = prompt.split()  # Split prompt into words
        lines = []  # Initialize lines list
        current_line = ""  # Initialize current line
        
        for word in words:  # Loop through words
            if len(current_line + " " + word) <= max_chars_per_line:  # Check if word fits on line
                current_line += (" " + word) if current_line else word  # Add word to current line
            else:
                if current_line:  # Check if current line has content
                    lines.append(current_line)  # Add current line to lines
                current_line = word  # Start new line with word
        
        if current_line:  # Check if there's a remaining line
            lines.append(current_line)  # Add final line
        
        max_text_lines = int(os.getenv('MAX_TEXT_LINES', '2'))  # Maximum text lines
        lines = lines[:max_text_lines]  # Limit to max lines
        
        # Draw prompt text
        line_height = int(os.getenv('LINE_HEIGHT', '72'))  # Height between lines
        text_start_offset = int(os.getenv('TEXT_START_OFFSET', '80'))  # Text start offset
        text_start_y = overlay_y + text_start_offset  # Calculate text start Y position
        
        for i, line in enumerate(lines):  # Loop through lines
            bbox = draw.textbbox((0, 0), line, font=main_font)  # Get text bounding box
            text_width = bbox[2] - bbox[0]  # Calculate text width
            x = (IMAGE_WIDTH - text_width) // 2  # Center text horizontally
            y = text_start_y + i * line_height  # Calculate Y position
            
            # Shadow
            shadow_offset = int(os.getenv('SHADOW_OFFSET', '2'))  # Shadow offset in pixels
            text_shadow_color = tuple(int(x) for x in os.getenv('TEXT_SHADOW_COLOR', '0,0,0,100').split(','))  # Shadow color
            draw.text((x + shadow_offset, y + shadow_offset), line, fill=text_shadow_color, font=main_font)  # Draw shadow
            text_color = os.getenv('TEXT_COLOR', 'white')  # Get text color
            draw.text((x, y), line, fill=text_color, font=main_font)  # Draw main text
        
        # Calculate brand position
        brand_text_offset = int(os.getenv('BRAND_TEXT_OFFSET', '56'))  # Brand text offset
        last_prompt_y = text_start_y + (len(lines) - 1) * line_height + brand_text_offset  # Calculate brand Y position
        
        # Separator line
        separator_line_color = tuple(int(x) for x in os.getenv('SEPARATOR_LINE_COLOR', '255,255,255,40').split(','))  # Get separator color
        separator_line_width = int(os.getenv('SEPARATOR_LINE_WIDTH', '1'))  # Get separator width
        draw.line([(50, last_prompt_y + 40), (IMAGE_WIDTH - 50, last_prompt_y + 40)], fill=separator_line_color, width=separator_line_width)  # Draw separator line
        
        # Brand text
        brand_text = os.getenv('BRAND_TEXT', 'ASK: Daily Architectural Research')  # Get brand text
        bbox = draw.textbbox((0, 0), brand_text, font=brand_font)  # Get brand text bounding box
        brand_text_width = bbox[2] - bbox[0]  # Calculate brand text width
        brand_x_position = int(os.getenv('BRAND_X_POSITION', '30'))  # Brand X position
        brand_y_offset = int(os.getenv('BRAND_Y_OFFSET', '100'))  # Brand Y offset
        brand_x = brand_x_position  # Set brand X coordinate
        brand_y = last_prompt_y + brand_y_offset  # Set brand Y coordinate
        
        shadow_color = tuple(int(x) for x in os.getenv('SHADOW_COLOR', '0,0,0,80').split(','))  # Get shadow color
        draw.text((brand_x + 1, brand_y + 1), brand_text, fill=shadow_color, font=brand_font)  # Draw brand shadow
        draw.text((brand_x, brand_y), brand_text, fill='white', font=brand_font)  # Draw brand text
        
        # Image number
        number_format = os.getenv('NUMBER_FORMAT', '#{:02d}')  # Get number format
        number_text = number_format.format(image_number)  # Format number text
        bbox = draw.textbbox((0, 0), number_text, font=number_font)  # Get number text bounding box
        number_text_width = bbox[2] - bbox[0]  # Calculate number text width
        number_x_offset = int(os.getenv('NUMBER_X_OFFSET', '30'))  # Number X offset
        number_x = IMAGE_WIDTH - number_text_width - number_x_offset  # Calculate number X position
        number_y = brand_y  # Set number Y position to match brand
        
        draw.text((number_x + 1, number_y + 1), number_text, fill=shadow_color, font=number_font)  # Draw number shadow
        draw.text((number_x, number_y), number_text, fill='white', font=number_font)  # Draw number text
        
        img.save(image_path, quality=IMAGE_QUALITY)  # Save image with quality setting
        log.info(f"Added text overlay to image: {image_path}")  # Log success
                
    except Exception as e:  # Catch any exceptions
        log.error(f"Error adding text overlay to {image_path}: {e}")  # Log error

def main():
    """Main pipeline: Generate questions → Create Instagram stories with text overlay"""
    try:
        Path(IMAGES_DIR).mkdir(exist_ok=True)  # Create images directory if it doesn't exist
        Path(os.getenv('LOG_DIR', 'logs')).mkdir(exist_ok=True)  # Create logs directory if it doesn't exist
        
        console_logger.info("Starting Instagram Story Generation...")  # Console start message
        log_separator_length = int(os.getenv('LOG_SEPARATOR_LENGTH', '60'))  # Get separator length
        log.info("=" * log_separator_length)  # Log separator line
        log.info("Starting Instagram Story Generation")  # Log start message
        log.info("=" * log_separator_length)  # Log separator line
        
        # Generate questions
        console_logger.info("Generating questions for each discipline...")  # Console message
        questions = get_questions_by_discipline()  # Get questions for each discipline
        
        # Generate images
        console_logger.info("Generating Instagram stories...")  # Console message
        start_image_number = get_next_image_number()  # Get starting image number
        console_logger.info(f"Starting image numbering from: {start_image_number}")  # Console message
        image_number = start_image_number  # Initialize image number
        generated_images = {}  # Track images by discipline
        
        for discipline, prompt in questions.items():  # Loop through disciplines and questions
            try:
                console_logger.info(f"Generating {discipline} story (Image #{image_number})...")  # Console message
                
                image_path = generate_image_with_retry(prompt, discipline, image_number)  # Generate image
                add_text_overlay(image_path, prompt, image_number)  # Add text overlay
                
                # Log immediately after successful generation
                image_filename = os.path.basename(image_path)  # Get image filename
                log_single_question(discipline, prompt, image_filename)  # Log question and image
                
                generated_images[discipline] = image_path  # Store image path
                image_number += 1  # Increment image number
                
                time.sleep(RATE_LIMIT_DELAY)  # Wait between API calls
                
            except Exception as e:  # Catch any exceptions
                console_logger.error(f"Failed to generate {discipline} story: {e}")  # Console error
                log.error(f"Failed to generate {discipline} story: {e}")  # Log error
                continue  # Continue with next discipline
        
        # Success logging
        if generated_images:  # Check if any images were generated
            console_logger.info("SUCCESS! All Instagram stories created successfully")  # Console success
            log.info("=" * log_separator_length)  # Log separator
            log.info("SUCCESS! All Instagram stories created successfully")  # Log success
            log.info(f"Images generated: {len(generated_images)}")  # Log count
            log.info("=" * log_separator_length)  # Log separator
            
            for discipline, prompt in questions.items():  # Loop through questions
                if discipline in generated_images:  # Check if image was generated
                    log.info(f"Image ({discipline}): {prompt}")  # Log question
            log.info("=" * log_separator_length)  # Log separator
        else:
            console_logger.error("Failed to generate any images")  # Console error
            log.error("Failed to generate any images")  # Log error
            
    except Exception as e:  # Catch any exceptions
        console_logger.error(f"Error in main function: {e}")  # Console error
        log.error(f"Error in main function: {e}")  # Log error

if __name__ == "__main__":  # Check if script is run directly
    main()  # Call main function 