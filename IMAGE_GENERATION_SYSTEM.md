# Image Generation System

## 🎯 Overview

The **Image Generation System** converts all PDF generation features into comprehensive image generation functions. This system provides the same powerful features as the PDF system but generates images instead of PDFs, making it perfect for social media, presentations, and digital content creation.

## 🚀 Features Converted from PDF to Images

### **📄 Image Generation Features** (Converted from PDF Generation)
- `CREATE_INDIVIDUAL_IMAGES=true` - Create individual images for each Q&A pair
- `CREATE_FINAL_COMPILATION=true` - Create final compilation image
- `CREATE_AUTOMATIC_CATEGORY_COMPILATIONS=false` - Create automatic category compilations
- `CREATE_COVER_IMAGE=true` - Create cover image for volume
- `CREATE_TABLE_OF_CONTENTS=true` - Create table of contents image
- `CREATE_SEQUENTIAL_TOC=true` - Create sequential table of contents
- `CREATE_CATEGORY_TOC=true` - Create category table of contents
- `PRESERVE_TEMP_FILES=true` - Preserve temporary files

### **📊 Table of Contents Features** (Converted from PDF TOC)
- `TOC_SHOW_FULL_QUESTIONS=true` - Show full questions in TOC
- `TOC_BACKGROUND_PROMPT=true` - Use background prompt for TOC images
- `TOC_CATEGORY_GROUPING=true` - Group by category in TOC
- `TOC_GROUP_UNKNOWN_CATEGORIES=true` - Group unknown categories
- `TOC_SORT_CATEGORIES_ALPHABETICALLY=true` - Sort categories alphabetically

### **📝 Logging Features** (Converted from PDF Logging)
- `LOG_SUCCESS_MESSAGES=true` - Log success messages
- `LOG_ERROR_MESSAGES=true` - Log error messages
- `LOG_PROGRESS_MESSAGES=true` - Log progress messages
- `LOG_DETAILED_ERRORS=true` - Log detailed error information
- `LOG_TIMING=true` - Log timing information

### **📈 Progress Tracking Features** (Converted from PDF Progress)
- `PROGRESS_STEP_TRACKING=true` - Track progress steps
- `PROGRESS_EMOJI_ENABLED=true` - Enable emoji in progress messages
- `PROGRESS_VERBOSE=true` - Verbose progress output
- `PROGRESS_STEP_NUMBERING=true` - Number progress steps
- `PROGRESS_TIMING_DETAILED=true` - Detailed timing information
- `PROGRESS_FILE_OPERATIONS=true` - Track file operations
- `PROGRESS_IMAGE_OPERATIONS=true` - Track image operations
- `PROGRESS_TEXT_OPERATIONS=true` - Track text operations

### **⚠️ Error Handling Features** (Converted from PDF Error Handling)
- `ERROR_HANDLING_ENABLED=true` - Enable error handling
- `ERROR_CONTINUE_ON_FAILURE=true` - Continue processing on failure
- `ERROR_SKIP_MISSING_FILES=true` - Skip missing files
- `ERROR_LOG_DETAILED=true` - Log detailed error information
- `ERROR_CREATE_PLACEHOLDER=true` - Create placeholder images on failure
- `ERROR_NOTIFY_ON_FAILURE=true` - Notify on failure

## 🎨 What Each Feature Generates

### **Individual Images**
- **Question Images**: AI-generated images with question text overlay
- **Answer Images**: AI-generated images with answer text overlay
- **Professional Layout**: Branded with ASK logo and consistent styling

### **Compilation Images**
- **Final Compilation**: Single image showcasing all Q&A pairs
- **Category Compilations**: Separate images for each architectural category
- **Grid Layout**: Organized presentation of multiple Q&A pairs

### **Cover Images**
- **Volume Covers**: Professional covers for each content volume
- **Category Covers**: Specialized covers for different architectural categories
- **Branded Design**: Consistent ASK branding and professional appearance

### **Table of Contents Images**
- **Main TOC**: Complete table of contents with all Q&A pairs
- **Sequential TOC**: Numbered list of all content in order
- **Category TOC**: Organized by architectural categories
- **Interactive Layout**: Easy-to-read format with category grouping

## 🚀 Usage

### **Basic Usage**
```python
from image_generation_system import ImageGenerationSystem, ImageGenerationConfig

# Initialize with default configuration
image_system = ImageGenerationSystem()

# Load Q&A pairs from log.csv
qa_pairs = read_log_csv()

# Generate complete image set
results = image_system.generate_complete_image_set(qa_pairs, volume_number=1)
```

### **Custom Configuration**
```python
# Custom configuration
config = ImageGenerationConfig(
    CREATE_INDIVIDUAL_IMAGES=True,
    CREATE_FINAL_COMPILATION=True,
    CREATE_COVER_IMAGE=True,
    CREATE_TABLE_OF_CONTENTS=True,
    PROGRESS_EMOJI_ENABLED=True,
    ERROR_CREATE_PLACEHOLDER=True
)

image_system = ImageGenerationSystem(config)
```

### **Command Line Usage**
```bash
# Run with default settings
python image_generation_system.py

# Run with custom environment file
cp image_generation_config.env .env
python image_generation_system.py
```

## 📁 Output Structure

```
images/
├── covers/                    # Cover images
│   ├── ASK-Volume-01-Cover.jpg
│   └── ASK-architectural_design-Cover.jpg
├── toc/                      # Table of contents
│   ├── ASK-TOC-20241201_143022.jpg
│   ├── ASK-Sequential-TOC-20241201_143022.jpg
│   └── ASK-Category-TOC-20241201_143022.jpg
├── compilations/             # Compilation images
│   ├── ASK-Compilation-Research.jpg
│   └── ASK-architectural_design-Compilation.jpg
├── temp/                     # Temporary files (if preserved)
│   ├── ASK-01-architectural_design-q.jpg
│   └── ASK-01-architectural_design-a.jpg
└── individual/               # Individual Q&A images
    ├── ASK-01-architectural_design-q-final.jpg
    └── ASK-01-architectural_design-a-final.jpg
```

## ⚙️ Configuration Options

### **Image Generation Settings**
```bash
# Core features
CREATE_INDIVIDUAL_IMAGES=true
CREATE_FINAL_COMPILATION=true
CREATE_COVER_IMAGE=true
CREATE_TABLE_OF_CONTENTS=true

# Image quality
IMAGE_WIDTH=1072
IMAGE_HEIGHT=1792
IMAGE_QUALITY=95
IMAGE_STYLE=photographic

# Text overlay
MAX_CHARS_PER_LINE=35
MAX_TEXT_LINES_ANSWER=12
TEXT_COLOR=#F0F0F0
```

### **Progress and Logging**
```bash
# Progress tracking
PROGRESS_STEP_TRACKING=true
PROGRESS_EMOJI_ENABLED=true
PROGRESS_VERBOSE=true

# Logging
LOG_SUCCESS_MESSAGES=true
LOG_ERROR_MESSAGES=true
LOG_TIMING=true
```

### **Error Handling**
```bash
# Error management
ERROR_HANDLING_ENABLED=true
ERROR_CONTINUE_ON_FAILURE=true
ERROR_CREATE_PLACEHOLDER=true
ERROR_MAX_FAILURES=10
```

## 🎯 Example Output

### **Individual Q&A Images**
```
✅ Created images for Q&A pair 1
📁 Question image: ASK-01-architectural_design-q-final.jpg
📁 Answer image: ASK-01-architectural_design-a-final.jpg
```

### **Compilation Images**
```
✅ Final compilation created: images/compilations/ASK-Compilation-Research.jpg
✅ Category compilation created for architectural_design: images/compilations/ASK-architectural_design-Compilation.jpg
```

### **Table of Contents**
```
✅ Table of contents created: images/toc/ASK-TOC-20241201_143022.jpg
✅ Sequential TOC created: images/toc/ASK-Sequential-TOC-20241201_143022.jpg
✅ Category TOC created: images/toc/ASK-Category-TOC-20241201_143022.jpg
```

### **Cover Images**
```
✅ Cover image created: images/covers/ASK-Volume-01-Cover.jpg
```

## 🔧 Advanced Features

### **Batch Processing**
```python
# Process multiple volumes
for volume in range(1, 4):
    results = image_system.generate_complete_image_set(qa_pairs, volume_number=volume)
```

### **Custom TOC Content**
```python
# Customize TOC content
def custom_toc_content(qa_pairs):
    return "Custom table of contents format"

image_system._create_toc_content = custom_toc_content
```

### **Error Recovery**
```python
# Handle failures gracefully
try:
    results = image_system.generate_complete_image_set(qa_pairs)
except Exception as e:
    print(f"Generation failed: {e}")
    # Continue with available results
```

## 📊 Performance Optimization

### **Parallel Processing**
```bash
# Enable parallel processing for faster generation
PARALLEL_PROCESSING=true
BATCH_SIZE=5
```

### **Quality Control**
```bash
# Quality checks
QUALITY_CHECK_ENABLED=true
MIN_IMAGE_SIZE=100000
MAX_IMAGE_SIZE=10000000
VALIDATE_IMAGE_INTEGRITY=true
```

### **Caching and Optimization**
```bash
# Performance settings
IMAGE_GENERATION_TIMEOUT=300
RETRY_ATTEMPTS=3
SAVE_INTERMEDIATE_FILES=false
```

## 🎨 Customization Options

### **Branding**
```bash
# Customize branding
BRAND_TEXT=Your Custom Brand
BRAND_X_POSITION=40
BRAND_Y_OFFSET=100
TEXT_COLOR=#FFFFFF
```

### **Layout**
```bash
# Layout customization
COMPILATION_MAX_IMAGES_PER_PAGE=4
COMPILATION_LAYOUT_GRID=true
TOC_MAX_QUESTIONS_PER_CATEGORY=5
```

### **Styling**
```bash
# Visual styling
FONT_FILE_PATH=fonts/your-font.ttf
MAIN_FONT_SIZE=32
BRAND_FONT_SIZE=24
SHADOW_OFFSET=2
```

## 🔍 Troubleshooting

### **Common Issues**
1. **Missing Fonts**: Ensure font files exist in the specified path
2. **API Limits**: Check API rate limits and timeouts
3. **Memory Issues**: Reduce batch size for large datasets
4. **File Permissions**: Ensure write permissions for output directories

### **Debug Mode**
```bash
# Enable debug mode for detailed information
DEBUG_MODE=true
VERBOSE_OUTPUT=true
LOG_LEVEL=DEBUG
```

### **Recovery Mode**
```bash
# Enable recovery mode to resume from failures
RECOVERY_MODE=true
BACKUP_ORIGINAL_IMAGES=true
```

## 🎯 Benefits of Image Generation System

1. **Social Media Ready**: Perfect for Instagram, Twitter, LinkedIn
2. **Presentation Friendly**: Ideal for slideshows and presentations
3. **Digital Content**: Easy to share and embed in websites
4. **Professional Quality**: High-resolution, branded images
5. **Flexible Output**: Multiple formats and layouts
6. **Automated Workflow**: Complete automation from Q&A to images
7. **Error Resilient**: Robust error handling and recovery
8. **Customizable**: Extensive configuration options

## 🚀 Integration with Existing Pipeline

The Image Generation System integrates seamlessly with the existing pipeline:

```python
# Use with simple pipeline
from simple_pipeline import SimplePipeline
from image_generation_system import ImageGenerationSystem

# Run simple pipeline
pipeline = SimplePipeline()
qa_pairs = pipeline.run_continuous(3)

# Generate images from results
image_system = ImageGenerationSystem()
results = image_system.generate_complete_image_set(qa_pairs)
```

The Image Generation System provides **all the power of the PDF system** with the **flexibility and accessibility of image-based content**!
