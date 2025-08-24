# ASK: Daily Research Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Advanced Research & Image Generation Pipeline**  
> Generate high-quality Q&A content with AI-powered image generation, supporting GPU, CPU, and API fallback systems.

#  Overview

ASK is a comprehensive research tool that combines AI-powered question generation, answer creation, and intelligent image generation. It features multiple generation modes, smart fallback systems, and professional output formatting.

#  Key Features

- **AI-Powered Content**: Generate questions and answers using advanced language models
- ** Smart Image Generation**: GPU, CPU, and API fallback with professional styling
- ** Multiple Modes**: Simple, Hybrid, Cross-Disciplinary, and Chained content generation
- ** Intelligent Fallback**: Automatic switching between generation methods
- ** Professional Output**: Individual images, compilations, covers, and table of contents
- ** Highly Configurable**: Extensive customization through environment variables
- ** Progress Tracking**: Real-time progress monitoring and logging
- ** Error Handling**: Robust error recovery and fallback strategies

#  Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage Modes](#-usage-modes)
- [Image Generation](#-image-generation)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

#  Installation

## Prerequisites

- **Python 3.8+**
- **Git**
- **Together.ai API Key** (for AI content generation)

# Automatic Installation

**Windows:**
```bash
# Clone the repository
git clone https://github.com/kushalsamant/ask.git
cd ask

# Run automatic installer
install.bat
```

**Linux/macOS:**
```bash
# Clone the repository
git clone https://github.com/kushalsamant/ask.git
cd ask

# Run automatic installer
chmod +x install.sh
./install.sh
```

# Manual Installation

```bash
# Clone the repository
git clone https://github.com/kushalsamant/ask.git
cd ask

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ask.env.template ask.env
# Edit ask.env with your API key and preferences
```

##  Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB | 50GB+ |
| **GPU** | CPU-only | NVIDIA GTX 1650+ |
| **CPU** | 4 cores | 8+ cores |

#  Quick Start

## 1. Configuration Setup

```bash
# Copy template and configure
cp ask.env.template ask.env

# Edit ask.env with your settings
```

## 2. Basic Usage

```bash
# Run in simple mode
python main.py simple

# Run in hybrid mode
python main.py hybrid

# Run in cross-disciplinary mode
python main.py cross-disciplinary

# Run in chained mode
python main.py chained
```

#  Configuration

## Environment Variables

Copy `ask.env.template` to `ask.env` and configure:

```bash
# API Configuration
TOGETHER_API_KEY=your_api_key_here

# Theme Configuration
THEME_1=your_first_theme
THEME_2=your_second_theme
THEME_3=your_third_theme

# Generation Settings
HYBRID_THEME_COUNT=2
CROSS_DISCIPLINARY_THEME_COUNT=3
CHAIN_LENGTH=3

# Image Generation
IMAGE_QUALITY=high
IMAGE_WIDTH=1200
IMAGE_HEIGHT=800
```

# Theme Configuration

Configure your research themes in `ask.env`:

```bash
# Example themes
THEME_1=Artificial Intelligence
THEME_2=Sustainable Architecture
THEME_3=Urban Planning
THEME_4=Digital Transformation
THEME_5=Climate Change
```

# API Configuration

Set up your Together.ai API key:

```bash
TOGETHER_API_KEY=your_actual_api_key_here
```

# Image Configuration

Customize image generation settings:

```bash
# Quality settings
IMAGE_QUALITY=high
IMAGE_WIDTH=1200
IMAGE_HEIGHT=800

# Style settings
FONT_SIZE=24
TEXT_COLOR=#F0F0F0
BACKGROUND_COLOR=#1a1a1a
```

# Hardware Configuration

Configure for your hardware:

```bash
# GPU settings (if available)
USE_GPU=true
GPU_MEMORY_LIMIT=4GB

# CPU settings
USE_CPU=true
CPU_THREADS=4

# Fallback settings
API_FALLBACK=true
PLACEHOLDER_FALLBACK=true
```

#  Usage Modes

##  Simple Mode

Generate basic Q&A content for a single theme.

```bash
python main.py simple
```

**Features:**
- Single theme focus
- 10 Q&A pairs
- Basic image generation
- Quick generation

#  Hybrid Mode

Combine multiple themes in innovative ways.

```bash
python main.py hybrid
```

**Features:**
- Multiple theme integration
- 10 Q&A pairs (2 themes × 5 chains)
- Advanced content connections
- Professional styling

#  Cross-disciplinary Mode

Generate content that bridges multiple research themes, creating innovative connections and insights.

```bash
python main.py cross-disciplinary
```

**Features:**
- Combines multiple themes in single Q&A pairs
- Creates interdisciplinary research questions
- Generates innovative content connections
- Produces 10 Q&A pairs with cross-theme integration

#  Chained Mode

Create deep exploration content with chained questions.

```bash
python main.py chained
```

**Features:**
- Deep theme exploration
- 10 Q&A pairs (2 categories × 5 chains)
- Progressive complexity
- Comprehensive coverage

#  Image Generation

## Generation Methods

The system supports multiple image generation methods with intelligent fallback:

1. **GPU Generation** (Priority when enabled)
   - NVIDIA CUDA acceleration
   - Fastest generation
   - High quality output

2. **CPU Generation** (Priority when enabled)
   - CPU-based generation
   - Works on any system
   - Moderate speed

3. **API Generation** (Fallback)
   - Together.ai API
   - Reliable quality
   - Requires internet

4. **Placeholder Images** (Final fallback)
   - Local generation
   - Always available
   - Basic styling

# Output Types

- **Individual Images**: Each Q&A pair as separate image
- **Compilations**: Multiple Q&A pairs in single image
- **Cover Images**: Professional title pages
- **Table of Contents**: Navigation and overview

#  Project Structure

```
ask/
 main.py                 # Main orchestration pipeline
 ask.env                 # Configuration file
 ask.env.template        # Configuration template
 requirements.txt        # Python dependencies
 install.bat            # Windows installer
 install.sh             # Linux/macOS installer
 install_dependencies.py # Smart dependency installer
 README.md              # This file
 LICENSE                # MIT License
 .gitignore             # Git ignore rules
 FUNDING.yml            # GitHub funding config
 log.csv                # Activity log
 test_comprehensive.py  # Comprehensive test suite
 optimize_performance.py # Performance optimizer
 api_client.py          # API client with optimizations
 cpu_image_generator.py # CPU image generation
 gpu_image_generator.py # GPU image generation
 smart_image_generator.py # Smart fallback system
 image_generation_system.py # Main image system
 image_create_ai.py     # AI image creation
 image_create_cover.py  # Cover image creation
 image_add_text.py      # Text overlay system
 image_layout_creator.py # Layout creation
 image_layout_config.py # Layout configuration
 image_text_processor.py # Text processing
 image_typography_config.py # Typography settings
 research_orchestrator.py # Research coordination
 research_question_manager.py # Question management
 research_answer_manager.py # Answer management
 style_manager.py       # Style management
 volume_manager.py      # Volume management
 research_csv_manager.py # CSV data management
 research_backup_manager.py # Backup management
 generated_images/      # Output directory
     individual/        # Individual Q&A images
     compilations/      # Multi-Q&A images
     covers/           # Cover images
     toc/              # Table of contents
```

# Core Modules

- **Main Pipeline**: Orchestrates the entire process
- **Research Orchestrator**: Manages content generation
- **Image Generation System**: Handles all image creation
- **Smart Fallback**: Ensures reliable generation
- **Volume Management**: Organizes output by volumes

# Image Generation

- **AI Image Creation**: Together.ai API integration
- **Layout Creator**: Professional image layouts
- **Text Processor**: Smart text handling
- **Typography Config**: Font and style management

# Utilities

- **API Client**: Optimized API communication
- **CSV Manager**: Data logging and management
- **Backup Manager**: Automatic backup system
- **Volume Manager**: Output organization

#  API Reference

## Main Functions

The main pipeline provides several key functions:

- `main()`: Main orchestration function
- `run_simple_mode()`: Run simple content generation
- `run_hybrid_mode()`: Run hybrid content generation
- `run_cross_disciplinary_mode()`: Run cross-disciplinary content generation
- `run_chained_mode()`: Run chained content generation

# API Client

The API client provides optimized communication with Together.ai:

- `APIClient`: Optimized API client with connection pooling
- `generate_content()`: Generate content asynchronously
- `generate_content_sync()`: Generate content synchronously

# Image Generation System

The image generation system handles all image creation:

- `ImageGenerationSystem`: Main image generation orchestrator
- `generate_qa_image()`: Generate Q&A image
- `generate_compilation()`: Generate compilation image
- `generate_cover()`: Generate cover image

#  Troubleshooting

## Common Issues

####  API Key Issues

**Problem**: `Missing TOGETHER_API_KEY`
**Solution**: 
1. Copy `ask.env.template` to `ask.env`
2. Add your Together.ai API key
3. Restart the application

# Installation Issues

**Problem**: `ModuleNotFoundError`
**Solution**:
1. Run `pip install -r requirements.txt`
2. Or use `install.bat` / `install.sh`
3. Check Python version (3.8+)

# Image Generation Issues

**Problem**: Images not generating
**Solution**:
1. Check hardware configuration
2. Verify fallback settings
3. Check disk space

# Performance Issues

**Problem**: Slow generation
**Solution**:
1. Enable GPU if available
2. Adjust image quality settings
3. Use CPU optimization

# Performance Tips

- **GPU Usage**: Enable GPU for faster generation
- **Image Quality**: Lower quality for faster generation
- **Batch Processing**: Process multiple items together
- **Memory Management**: Monitor system resources

# Getting Help

- Check the logs in `log.csv`
- Review error messages
- Verify configuration settings
- Test with minimal settings

# 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details.

#  Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where appropriate

# 🧪 Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Run `python test_comprehensive.py`

#  Pull Requests

- Fork the repository
- Create a feature branch
- Submit a pull request with detailed description

#  Bug Reports

- Use GitHub Issues
- Include error messages
- Provide reproduction steps

#  Feature Requests

- Describe the feature clearly
- Explain the use case
- Consider implementation complexity

#  License

This project is licensed under the MIT License - see the LICENSE file for details.

#  Acknowledgments

- Together.ai for AI capabilities
- Open source community for inspiration
- Contributors and users for feedback

#  Support

##  Issues

Report bugs and issues on GitHub

#  Discussions

Join community discussions

#  Documentation

Check the wiki for detailed guides

#  Contact Information

- GitHub Issues: [Repository Issues](https://github.com/kushalsamant/ask/issues)
- Discussions: [GitHub Discussions](https://github.com/kushalsamant/ask/discussions)
- Wiki: [Project Wiki](https://github.com/kushalsamant/ask/wiki)

---

**Made with  by the ASK Community**
