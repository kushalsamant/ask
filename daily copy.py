#!/usr/bin/env python3  # Shebang for Unix-like systems
"""
Instagram Story Generator
Architecture Questions → Instagram Stories with Text Overlay
Includes question generation, image generation, and analysis
"""

import os
import time
import json
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

# Additional environment variables for text generation and vision models
TEXT_MODEL = os.getenv('TEXT_MODEL', 'togethercomputer/llama-3.3-70b-instruct-turbo')  # Model for question generation
VISION_MODEL = os.getenv('VISION_MODEL', 'togethercomputer/llama-3.2-11b')  # Model for blurb generation

# Questions per discipline settings
TEXT_QUESTIONS_PER_DISCIPLINE = int(os.getenv('TEXT_QUESTIONS_PER_DISCIPLINE', '15'))

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

def generate_questions_for_discipline(discipline):
    """Generate architectural questions for a specific discipline using Together AI"""
    try:
        url = os.getenv('TOGETHER_API_URL', 'https://api.together.xyz/v1') + '/completions'
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Craft a detailed prompt for the AI
        prompt = f'''[INST] You are an expert architectural researcher and educator. Generate {TEXT_QUESTIONS_PER_DISCIPLINE} thought-provoking questions about {discipline} in architecture.

Context: These questions will inspire architectural research and creative thinking. They should challenge conventional wisdom and explore the intersection of {discipline} with contemporary challenges.

Requirements:
- Create open-ended questions that encourage deep thinking and discussion
- Focus on innovation, sustainability, future trends, and societal impact
- Address real-world challenges and opportunities in {discipline}
- Consider global perspectives and cross-cultural implications
- Start questions with "How", "What", or "Why"
- Use clear, professional language
- Make each question unique within its topic
- Format: One question per line, no question marks or numbering

Example format:
How can we design buildings that respond to climate change
What makes a space feel truly architectural
How can we create buildings that age gracefully

Please generate {discipline}-specific questions that provoke meaningful architectural discourse: [/INST]'''

        payload = {
            "model": TEXT_MODEL,
            "prompt": prompt,
            "temperature": float(os.getenv('TEXT_TEMPERATURE', '0.72')),
            "max_tokens": int(os.getenv('TEXT_MAX_TOKENS', '150')),
            "top_p": float(os.getenv('TEXT_TOP_P', '0.85')),
            "frequency_penalty": float(os.getenv('TEXT_FREQUENCY_PENALTY', '0.3')),
            "presence_penalty": float(os.getenv('TEXT_PRESENCE_PENALTY', '0.6')),
            "stop": ["\\n\\n", "1.", "2.", "3."]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                # Process the generated text into individual questions
                questions = [
                    q.strip() for q in data['choices'][0]['text'].strip().split('\\n')
                    if q.strip() and len(q.strip()) > 10  # Ensure questions are meaningful
                ]
                return questions
            else:
                log.error(f"Invalid API response format for {discipline}")
                return []
        else:
            log.error(f"API error for {discipline}: {response.status_code} - {response.text[:200]}")
            return []
            
    except Exception as e:
        log.error(f"Error generating questions for {discipline}: {e}")
        return []

def populate_questions():
    """Generate questions for all disciplines and add them to log.csv"""
    # Get disciplines from environment
    disciplines = os.getenv('REQUIRED_DISCIPLINES', '').lower().split(',')
    if not disciplines or disciplines[0] == '':
        disciplines = ['architecture', 'construction', 'design', 'engineering', 
                      'interiors', 'planning', 'urbanism']

    total_new_questions = 0
    for discipline in disciplines:
        console_logger.info(f"Generating questions for {discipline}...")
        
        # Generate questions
        questions = generate_questions_for_discipline(discipline)
        if questions:
            # Add to log.csv
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('log.csv', 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for question in questions:
                    writer.writerow([timestamp, discipline, question, '', 'false', '', ''])
            
            total_new_questions += len(questions)
            console_logger.info(f"Added {len(questions)} new questions for {discipline}")
            for q in questions:
                log.info(f"New {discipline} question: {q}")
            
            # Wait between API calls
            time.sleep(RATE_LIMIT_DELAY)
        else:
            console_logger.error(f"Failed to generate questions for {discipline}")

    console_logger.info(f"Added {total_new_questions} new questions to log.csv")

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

def get_questions_and_styles_from_log():
    """Read all questions and styles from log.csv and organize by discipline"""
    questions_by_discipline = {}
    styles_by_discipline = {}
    used_questions = set()
    
    try:
        if not os.path.exists('log.csv'):
            # Create log.csv with headers if it doesn't exist
            with open('log.csv', 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'discipline', 'question', 'image_filename', 'is_used', 'style', 'blurb'])
            return questions_by_discipline, styles_by_discipline, used_questions

        with open('log.csv', 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            
            # Add required columns if they don't exist
            fieldnames = reader.fieldnames or []
            new_columns = []
            if 'is_used' not in fieldnames:
                new_columns.append('is_used')
            if 'style' not in fieldnames:
                new_columns.append('style')
            if 'blurb' not in fieldnames:
                new_columns.append('blurb')
            
            if new_columns:
                rows = list(reader)
                fieldnames = fieldnames + new_columns
                with open('log.csv', 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in rows:
                        if 'is_used' not in row:
                            row['is_used'] = row.get('image_filename', '') != ''
                        if 'style' not in row:
                            row['style'] = ''
                        writer.writerow(row)
                
                # Reopen file for reading
                with open('log.csv', 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
            else:
                rows = list(reader)

            # Organize questions and styles by discipline
            for row in rows:
                discipline = row.get('discipline', '').strip()
                question = row.get('question', '').strip()
                is_used = row.get('is_used', '').lower() == 'true'
                style = row.get('style', '').strip()

                if discipline and question:
                    # Organize questions
                    if discipline not in questions_by_discipline:
                        questions_by_discipline[discipline] = set()
                    questions_by_discipline[discipline].add(question)
                    if is_used:
                        used_questions.add(question)
                    
                    # Organize styles
                    if discipline not in styles_by_discipline:
                        styles_by_discipline[discipline] = set()
                    if style:
                        styles_by_discipline[discipline].add(style)

    except Exception as e:
        log.error(f"Error reading from log.csv: {e}")
        console_logger.error(f"Error reading from log.csv: {e}")
        raise

    return questions_by_discipline, styles_by_discipline, used_questions

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
    """Get questions based on configured disciplines and count requirements"""
    # Get configuration settings
    required_count = int(os.getenv('QUESTIONS_PER_RUN', '7'))
    required_disciplines = os.getenv('REQUIRED_DISCIPLINES', '').lower().split(',')
    enforce_count = os.getenv('ENFORCE_DISCIPLINE_COUNT', 'true').lower() == 'true'
    
    # Validate required disciplines
    if not required_disciplines or required_disciplines[0] == '':
        required_disciplines = ['architecture', 'construction', 'design', 'engineering', 
                              'interiors', 'planning', 'urbanism']
    
    # Get questions, styles, and used questions from log.csv
    all_questions, styles_by_discipline, used_questions = get_questions_and_styles_from_log()
    
    # Filter disciplines based on available questions
    disciplines_with_questions = {
        discipline: questions 
        for discipline, questions in all_questions.items() 
        if discipline in required_disciplines and questions
    }
    
    # Validate discipline count
    if enforce_count and len(disciplines_with_questions) != required_count:
        error_msg = f"Number of disciplines with available questions ({len(disciplines_with_questions)}) does not match QUESTIONS_PER_RUN ({required_count})"
        log.error(error_msg)
        console_logger.error(error_msg)
        missing_disciplines = set(required_disciplines) - set(disciplines_with_questions.keys())
        if missing_disciplines:
            log.error(f"Disciplines without questions: {', '.join(missing_disciplines)}")
            console_logger.error(f"Disciplines without questions: {', '.join(missing_disciplines)}")
        raise ValueError(error_msg)
    
    selected_questions = {}  # Initialize selected questions dictionary
    for discipline, question_set in disciplines_with_questions.items():
        # Filter out previously used questions
        available_questions = [q for q in question_set if q not in used_questions]
        
        if available_questions:
            selected_question = random.choice(available_questions)
            selected_questions[discipline] = selected_question
            log.info(f"Selected question for {discipline}: {selected_question}")
        else:
            log.warning(f"No unused questions available for {discipline}, skipping...")
            continue
    
    return selected_questions

def generate_blurb(question, discipline, image_path):
    """Generate a 100-word blurb analyzing the Question-Image pair using Llama 3.2 11B"""
    try:
        url = os.getenv('TOGETHER_API_URL', 'https://api.together.xyz/v1') + '/chat/completions'
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        system_prompt = """You are an expert architectural researcher and educator analyzing architectural concepts and imagery. 
        Provide insightful, academic analysis focusing on architectural principles, design theory, and practical implications."""

        prompt = f"""Question: {question}
        Discipline: {discipline}
        
        Analyze this architectural question and provide a thoughtful, academic response in approximately 100 words. 
        Consider:
        - Key architectural principles involved
        - Contemporary relevance and future implications
        - Connection to {discipline} specifically
        - Practical and theoretical considerations
        
        Provide your analysis:"""

        payload = {
            "model": os.getenv('VISION_MODEL', 'togethercomputer/llama-3.2-11b'),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": float(os.getenv('VISION_TEMPERATURE', '0.7')),
            "max_tokens": int(os.getenv('VISION_MAX_TOKENS', '200')),
            "top_p": float(os.getenv('VISION_TOP_P', '0.9')),
            "frequency_penalty": float(os.getenv('VISION_FREQUENCY_PENALTY', '0.3')),
            "presence_penalty": float(os.getenv('VISION_PRESENCE_PENALTY', '0.3'))
        }

        response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                blurb = data['choices'][0]['message']['content'].strip()
                # Clean up the blurb
                blurb = ' '.join(blurb.split())  # Remove extra whitespace
                return blurb
            else:
                log.error("Invalid API response format for blurb generation")
                return None
        else:
            log.error(f"API error generating blurb: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        log.error(f"Error generating blurb: {e}")
        return None

def log_single_question(discipline, question, image_filename, style=None):
    """Log a single question and image to log.csv immediately"""
    try:
        import csv
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate blurb if image exists
        blurb = None
        if image_filename:
            image_path = os.path.join(IMAGES_DIR, image_filename)
            if os.path.exists(image_path):
                blurb = generate_blurb(question, discipline, image_path)
        
        # Read existing rows and update if question exists
        rows = []
        headers = ['timestamp', 'discipline', 'question', 'image_filename', 'is_used', 'style', 'blurb']
        file_exists = os.path.exists('log.csv')
        
        if file_exists:
            with open('log.csv', 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or headers
                rows = list(reader)
        
        # Check if question already exists
        question_exists = False
        for row in rows:
            if row['question'].strip() == question.strip():
                row['timestamp'] = timestamp
                row['image_filename'] = image_filename
                row['is_used'] = 'true'
                question_exists = True
                break
        
        # If question doesn't exist, add it as a new row
        if not question_exists:
            new_row = {
                'timestamp': timestamp,
                'discipline': discipline,
                'question': question,
                'image_filename': image_filename,
                'is_used': 'true',
                'style': style or '',
                'blurb': blurb or ''
            }
            rows.append(new_row)
        
        # Write all rows back to CSV
        with open('log.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
            
        log.info(f"Logged {discipline} question and image to log.csv: {image_filename}")
    except Exception as e:
        log.error(f"Error logging question to CSV: {e}")
        raise

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

def get_style_for_discipline(discipline, styles_by_discipline):
    """Get appropriate architectural style for each discipline from log.csv"""
    # Get styles for this discipline
    styles = styles_by_discipline.get(discipline, set())
    if not styles:
        error_msg = f"No styles configured for discipline: {discipline}"
        log.error(error_msg)
        console_logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Log the available styles
    log.info(f"Selecting from {len(styles)} styles for {discipline}: {', '.join(sorted(styles))}")
    
    # Return a random style from the list
    return random.choice(list(styles))

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
            
            try:
                _, styles_by_discipline, _ = get_questions_and_styles_from_log()  # Get styles
                style = get_style_for_discipline(discipline, styles_by_discipline)  # Get style for discipline
                log.info(f"Selected style for {discipline}: {style}")
            except ValueError as e:
                log.error(f"Style selection failed for {discipline}: {e}")
                raise  # Re-raise the error to be caught by the outer try-except
                
            # Craft a detailed prompt optimized for FLUX.1 schnell
            formatted_prompt = (
                f"Professional architectural visualization, {style} architectural style. "
                f"Focus on {discipline} aspects. {prompt} "
                f"High-quality, photorealistic, detailed, professional photography, architectural visualisation"
            )
            
            payload = {  # Request payload
                "model": IMAGE_MODEL,  # AI model name
                "prompt": formatted_prompt,  # Formatted prompt
                "negative_prompt": "low quality, blurry, distorted, deformed, disfigured, bad proportions, watermark, signature, text",  # Avoid common issues
                "width": IMAGE_WIDTH,  # Image width
                "height": IMAGE_HEIGHT,  # Image height
                "steps": INFERENCE_STEPS,  # Inference steps - schnell model optimized for fast inference
                "guidance_scale": GUIDANCE_SCALE,  # Guidance scale - balanced for good results
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

def get_next_volume_number():
    """Get the next volume number by checking existing PDFs"""
    try:
        pdf_dir = os.getenv('PDF_OUTPUT_DIR', 'pdfs')
        if not os.path.exists(pdf_dir):
            return 1
            
        # Get all PDF files in the directory
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        max_vol = 0
        
        # Extract volume numbers from existing files
        for pdf_file in pdf_files:
            try:
                # Look for VOL-XX pattern in filename
                if 'VOL-' in pdf_file:
                    vol_str = pdf_file.split('VOL-')[1].split('_')[0]
                    vol_num = int(vol_str)
                    max_vol = max(max_vol, vol_num)
            except (ValueError, IndexError):
                continue
                
        return max_vol + 1
    except Exception as e:
        log.warning(f"Could not determine next volume number: {e}")
        return 1

def create_pdf_from_images(image_paths):
    """Create a PDF from the generated images with full bleed (no margins)"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import (width, height)
        from PIL import Image
        
        # Check image count requirement
        required_images = int(os.getenv('PDF_IMAGES_PER_VOLUME', '7'))
        enforce_count = os.getenv('PDF_ENFORCE_IMAGE_COUNT', 'true').lower() == 'true'
        
        if enforce_count and len(image_paths) != required_images:
            error_msg = f"Expected {required_images} images, but got {len(image_paths)}"
            log.error(error_msg)
            console_logger.error(error_msg)
            return False
            
        # Ensure PDF output directory exists
        pdf_dir = os.getenv('PDF_OUTPUT_DIR', 'pdfs')
        Path(pdf_dir).mkdir(exist_ok=True)
        
        # Get the next volume number and create filename
        vol_num = get_next_volume_number()
        output_filename = f"ASK-VOL-{vol_num:02d}.pdf"
        output_path = os.path.join(pdf_dir, output_filename)
        
        # Get page dimensions from environment
        page_width = int(os.getenv('PDF_PAGE_WIDTH', '1072'))
        page_height = int(os.getenv('PDF_PAGE_HEIGHT', '1792'))
        pagesize = (page_width, page_height)
        
        # Create PDF with configured dimensions
        c = canvas.Canvas(output_path, pagesize=pagesize)
        
        # Image placement coordinates from environment
        x = int(os.getenv('PDF_IMAGE_X', '0'))
        y = int(os.getenv('PDF_IMAGE_Y', '0'))
        
        # For each image
        for img_path in image_paths:
            if os.path.exists(img_path):
                # Open and place image at full size
                img = Image.open(img_path)
                
                # Draw image
                c.drawImage(img_path, x, y, width, height)
                c.showPage()
        
        c.save()
        log.info(f"Created PDF: {output_filename} (Volume {vol_num})")
        console_logger.info(f"Created PDF: {output_filename} (Volume {vol_num})")
        return True
    except Exception as e:
        log.error(f"Error creating PDF: {e}")
        console_logger.error(f"Error creating PDF: {e}")
        return False

def main():
    """Main pipeline: Generate questions → Create Instagram stories with text overlay → Generate blurbs"""
    try:
        # Create required directories
        Path(IMAGES_DIR).mkdir(exist_ok=True)  # Create images directory if it doesn't exist
        Path(os.getenv('LOG_DIR', 'logs')).mkdir(exist_ok=True)  # Create logs directory if it doesn't exist
        Path(os.getenv('PDF_OUTPUT_DIR', 'pdfs')).mkdir(exist_ok=True)  # Create PDFs directory if it doesn't exist
        
        # Ensure log.csv exists with headers
        if not os.path.exists('log.csv'):
            with open('log.csv', 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'discipline', 'question', 'image_filename', 'is_used', 'style', 'blurb'])
        
        # Check if we need to generate more questions
        questions_by_discipline, _, _ = get_questions_and_styles_from_log()
        min_questions_needed = int(os.getenv('QUESTIONS_PER_RUN', '7')) * 2  # Keep a buffer
        
        for discipline in os.getenv('REQUIRED_DISCIPLINES', '').lower().split(','):
            if not discipline:
                continue
            if discipline not in questions_by_discipline or len(questions_by_discipline[discipline]) < min_questions_needed:
                console_logger.info(f"Generating new questions for {discipline}...")
                populate_questions()
                break
        
        # Initialize logging
        console_logger.info("Starting Instagram Story Generation...")  # Console start message
        log_separator_length = int(os.getenv('LOG_SEPARATOR_LENGTH', '60'))  # Get separator length
        log.info("=" * log_separator_length)  # Log separator line
        log.info("Starting Instagram Story Generation")  # Log start message
        log.info("=" * log_separator_length)  # Log separator line
        
        # Log configuration settings
        required_count = int(os.getenv('QUESTIONS_PER_RUN', '7'))
        required_disciplines = os.getenv('REQUIRED_DISCIPLINES', '').lower().split(',')
        enforce_count = os.getenv('ENFORCE_DISCIPLINE_COUNT', 'true').lower() == 'true'
        
        log.info(f"Configuration:")
        log.info(f"- Required questions per run: {required_count}")
        log.info(f"- Required disciplines: {', '.join(required_disciplines) if required_disciplines[0] else 'All'}")
        log.info(f"- Enforce discipline count: {enforce_count}")
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
            
            # Create PDF from generated images
            if create_pdf_from_images(list(generated_images.values())):
                console_logger.info(f"Created PDF compilation of all images")
            else:
                console_logger.error("Failed to create PDF compilation")
        else:
            console_logger.error("Failed to generate any images")  # Console error
            log.error("Failed to generate any images")  # Log error
            
    except Exception as e:  # Catch any exceptions
        console_logger.error(f"Error in main function: {e}")  # Console error
        log.error(f"Error in main function: {e}")  # Log error

if __name__ == "__main__":  # Check if script is run directly
    main()  # Call main function 