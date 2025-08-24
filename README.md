# *ASK*: Daily Research

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Advanced Research & Image Generation Pipeline**  
> Generate high-quality Q&A content with AI-powered image generation, primarily GPU-based with CPU fallback and API as last resort.

## Overview

*ASK* is a comprehensive research tool that combines AI-powered question generation, answer creation, and intelligent image generation. It operates primarily as an offline tool using GPU acceleration, with CPU fallback and API as last resort. It features multiple generation modes, smart fallback systems, and professional output formatting.

## Key Features

- **AI-Powered Content**: Generate questions and answers using advanced language models
- **Smart Image Generation**: Primarily GPU-based with CPU fallback and API as last resort
- **Multiple Modes**: Simple, Hybrid, Cross-Disciplinary, and Chained content generation
- **Intelligent Fallback**: Automatic switching between generation methods
- **Professional Output**: Individual images, compilations, covers, and table of contents
- **Highly Configurable**: Extensive customization through environment variables
- **Progress Tracking**: Real-time progress monitoring and logging
- **Error Handling**: Robust error recovery and fallback strategies
- **Offline-First**: Works completely offline with local AI models
- **Lazy Loading**: Models downloaded only when needed

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Modes](#usage-modes)
- [Image Generation](#image-generation)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Installation

### Prerequisites

- **Python 3.8+**
- **Git**
- **NVIDIA GPU** (primary mode of operation)
- **CPU** (fallback mode)
- **Together.ai API Key** (last resort fallback - optional)

### Automatic Installation

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

### Manual Installation

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

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | NVIDIA GTX 1650+ | NVIDIA RTX 3060+ |
| **GPU Memory** | 4GB | 8GB+ |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB | 50GB+ |
| **CPU** | 4 cores | 8+ cores |

## Quick Start

### 1. Configuration Setup

```bash
# Copy template and configure
cp ask.env.template ask.env

# Edit ask.env with your settings
```

### 2. Basic Usage

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

## Configuration

### Environment Variables

Copy `ask.env.template` to `ask.env` and configure:

```bash
# API Configuration
TOGETHER_API_KEY=your_api_key_here
TOGETHER_API_BASE=https://api.together.xyz/v1

# AI Model Configuration
TEXT_MODEL=llama-3.3-70b-instruct-turbo-free
IMAGE_MODEL=flux.1-schnell-free
VISION_MODEL=llama-vision-free

# Image Generation Settings
IMAGE_WIDTH=1072
IMAGE_HEIGHT=1792
IMAGE_QUALITY=95
INFERENCE_STEPS=4
GUIDANCE_SCALE=7.5

# CPU/GPU Configuration
CPU_IMAGE_GENERATION_ENABLED=true
GPU_IMAGE_GENERATION_ENABLED=true
API_IMAGE_GENERATION_ENABLED=false
CPU_MODEL_ID=SimianLuo/LCM_Dreamshaper_v7
GPU_MODEL_ID=runwayml/stable-diffusion-v1-5
```

### Theme Configuration

Configure your research themes in `ask.env`:

```bash
# Example themes
SIMPLE_MODE_THEMES=design_research,technology_innovation,sustainability_science,engineering_systems,environmental_design,urban_planning,spatial_design,digital_technology
DEFAULT_CHAINED_THEMES=design_research,technology_innovation
```

### Hardware Configuration

Configure for your hardware:

```bash
# GPU settings (primary mode)
GPU_IMAGE_GENERATION_ENABLED=true
GPU_MODEL_ID=runwayml/stable-diffusion-v1-5

# CPU settings (first fallback)
CPU_IMAGE_GENERATION_ENABLED=true
CPU_MODEL_ID=SimianLuo/LCM_Dreamshaper_v7

# API settings (last resort fallback)
API_IMAGE_GENERATION_ENABLED=false
```

## Usage Modes

### Simple Mode

Generate basic Q&A content for research themes.

```bash
python main.py simple
```

**Features:**
- Single theme focus
- 10 Q&A pairs
- Basic image generation
- Quick generation
- Volume tracking

### Hybrid Mode

Combine multiple research themes in innovative ways.

```bash
python main.py hybrid
```

**Features:**
- Multiple theme integration
- 10 Q&A pairs (2 themes × 5 chains)
- Advanced content connections
- Professional styling
- Cross-disciplinary questions

### Cross-disciplinary Mode

Generate content that bridges multiple research themes, creating innovative connections and insights.

```bash
python main.py cross-disciplinary
```

**Features:**
- Combines multiple themes in single Q&A pairs
- Creates interdisciplinary research questions
- Generates innovative content connections
- Produces 10 Q&A pairs with cross-theme integration

### Chained Mode

Create deep exploration content with chained questions.

```bash
python main.py chained
```

**Features:**
- Deep theme exploration
- 10 Q&A pairs (2 categories × 5 chains)
- Progressive complexity
- Comprehensive coverage
- Connected question chains

## Image Generation

### Generation Methods

The system operates as a primarily offline tool with intelligent fallback:

1. **GPU Generation** (Primary Mode)
   - NVIDIA CUDA acceleration
   - Fastest generation
   - Highest quality output
   - Completely offline operation
   - Uses Stable Diffusion models

2. **CPU Generation** (First Fallback)
   - CPU-based generation
   - Works when GPU unavailable
   - Moderate speed
   - Completely offline operation
   - Uses lightweight LCM models

3. **API Generation** (Last Resort Fallback)
   - Together.ai API
   - Requires internet connection
   - Used only when local generation fails
   - Reliable quality

4. **Placeholder Images** (Emergency Fallback)
   - Local generation
   - Always available
   - Basic styling
   - Completely offline

### Output Types

- **Individual Images**: Each Q&A pair as separate image
- **Compilations**: Multiple Q&A pairs in single image
- **Cover Images**: Professional title pages
- **Table of Contents**: Navigation and overview

### Image Naming Convention

Images follow the format:
- Questions: `ASK-<question number>-<discipline>-q.jpg`
- Answers: `ASK-<question number>-<discipline>-a.jpg`

## Project Structure

```
ask/
├── main.py                    # Main orchestration pipeline
├── api_client.py              # API client with optimizations
├── ask.env                    # Configuration file
├── ask.env.template           # Configuration template
├── requirements.txt           # Python dependencies
├── install.bat               # Windows installer
├── install.sh                # Linux/macOS installer
├── install_dependencies.py   # Smart dependency installer
├── README.md                 # This file
├── .gitignore                # Git ignore rules
├── log.csv                   # Activity log
├── images/                   # Output directory
├── logs/                     # Application logs
├── models/                   # AI model cache
│
├── Research Modules (13 files)
│   ├── research_orchestrator.py      # Research coordination
│   ├── research_question_generator.py # Question generation
│   ├── research_question_manager.py  # Question management
│   ├── research_question_prompts.py  # Question prompts
│   ├── research_answer_generator.py  # Answer generation
│   ├── research_answer_manager.py    # Answer management
│   ├── research_answer_prompts.py    # Answer prompts
│   ├── research_statistics.py        # Statistics and analytics
│   ├── research_theme_system.py      # Theme management
│   ├── research_categories_data.py   # Category data
│   ├── research_csv_manager.py       # CSV data management
│   ├── research_backup_manager.py    # Backup management
│   └── research_find_path.py         # Path finding utilities
│
├── Image Generation (8 files)
│   ├── image_generation_system.py    # Main image system
│   ├── smart_image_generator.py      # Smart fallback system
│   ├── cpu_image_generator.py        # CPU image generation
│   ├── gpu_image_generator.py        # GPU image generation
│   ├── image_create_ai.py            # AI image creation
│   ├── image_create_cover.py         # Cover image creation
│   ├── image_add_text.py             # Text overlay system
│   ├── image_layout_creator.py       # Layout creation
│   ├── image_layout_config.py        # Layout configuration
│   ├── image_text_processor.py       # Text processing
│   └── image_typography_config.py    # Typography settings
│
├── Style Management (4 files)
│   ├── style_ai_generator.py         # AI style generation
│   ├── style_data_manager.py         # Style data management
│   ├── style_manager.py              # Style management
│   └── style_trend_analyzer.py       # Trend analysis
│
├── Offline Generation (2 files)
│   ├── offline_question_generator.py # Offline question generation
│   └── offline_answer_generator.py   # Offline answer generation
│
└── Volume Management (1 file)
    └── volume_manager.py              # Volume management
```

## API Reference

### Main Functions

The main pipeline provides several key functions:

- `main()`: Main orchestration function
- `run_simple_mode()`: Run simple content generation
- `run_hybrid_mode()`: Run hybrid content generation
- `run_cross_disciplinary_mode()`: Run cross-disciplinary content generation
- `run_chained_mode()`: Run chained content generation

### API Client

The API client provides optimized communication with Together.ai:

- `APIClient`: Optimized API client with connection pooling
- `generate_content()`: Generate content asynchronously
- `generate_content_sync()`: Generate content synchronously

### Image Generation System

The image generation system handles all image creation:

- `ImageGenerationSystem`: Main image generation orchestrator
- `generate_qa_image()`: Generate Q&A image
- `generate_compilation()`: Generate compilation image
- `generate_cover()`: Generate cover image

## Troubleshooting

### Common Issues

#### API Key Issues

**Problem**: `Missing TOGETHER_API_KEY`
**Solution**: 
1. Copy `ask.env.template` to `ask.env`
2. Add your Together.ai API key
3. Set `API_IMAGE_GENERATION_ENABLED=false` for offline mode
4. Restart the application

#### Installation Issues

**Problem**: `ModuleNotFoundError`
**Solution**:
1. Run `pip install -r requirements.txt`
2. Or use `install.bat` / `install.sh`
3. Check Python version (3.8+)

#### Image Generation Issues

**Problem**: Images not generating
**Solution**:
1. Check hardware configuration
2. Verify fallback settings
3. Check disk space
4. Ensure models are downloaded

#### Performance Issues

**Problem**: Slow generation
**Solution**:
1. Ensure GPU is properly configured (primary mode)
2. Check GPU memory usage and adjust settings
3. CPU fallback is slower but reliable
4. API is only used as last resort

### Performance Tips

- **GPU Usage**: GPU is the primary mode - ensure CUDA is properly installed
- **GPU Memory**: Monitor GPU memory usage for optimal performance
- **CPU Fallback**: CPU mode is slower but works when GPU unavailable
- **Offline Operation**: System works completely offline with GPU/CPU modes
- **API Usage**: Only used as last resort when local generation fails
- **Model Caching**: Models are cached locally after first download

### Getting Help

- Check the logs in `logs/execution.log`
- Review error messages
- Verify configuration settings
- Test with minimal settings

## Contributing

We welcome contributions! Please see our contributing guidelines for details.

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where appropriate

### Testing

- Write tests for new features
- Ensure all tests pass before submitting

### Pull Requests

- Fork the repository
- Create a feature branch
- Submit a pull request with detailed description

### Bug Reports

- Use GitHub Issues
- Include error messages
- Provide reproduction steps

### Feature Requests

- Describe the feature clearly
- Explain the use case
- Consider implementation complexity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Together.ai for AI capabilities
- Open source community for inspiration
- Contributors and users for feedback

## Support

### Issues

Report bugs and issues on GitHub

### Discussions

Join community discussions

### Documentation

Check the wiki for detailed guides

### Contact Information

- GitHub Issues: [Repository Issues](https://github.com/kushalsamant/ask/issues)
- Discussions: [GitHub Discussions](https://github.com/kushalsamant/ask/discussions)
- Wiki: [Project Wiki](https://github.com/kushalsamant/ask/wiki)

---

**Made with ❤️ by the *ASK* Community**
