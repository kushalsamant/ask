# ASK: Daily Research Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Advanced Research & Image Generation Pipeline**  
> Generate high-quality Q&A content with AI-powered image generation, supporting GPU, CPU, and API fallback systems.

## 🚀 Overview

ASK is a comprehensive research tool that combines AI-powered question generation, answer creation, and intelligent image generation. It features multiple generation modes, smart fallback systems, and professional output formatting.

### ✨ Key Features

- **🤖 AI-Powered Content**: Generate questions and answers using advanced language models
- **🎨 Smart Image Generation**: GPU, CPU, and API fallback with professional styling
- **📊 Multiple Modes**: Simple, Hybrid, Cross-Disciplinary, and Chained content generation
- **🔄 Intelligent Fallback**: Automatic switching between generation methods
- **📁 Professional Output**: Individual images, compilations, covers, and table of contents
- **⚙️ Highly Configurable**: Extensive customization through environment variables
- **📈 Progress Tracking**: Real-time progress monitoring and logging
- **🛡️ Error Handling**: Robust error recovery and fallback strategies

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage Modes](#-usage-modes)
- [Image Generation](#-image-generation)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **Git**
- **Together.ai API Key** (for AI content generation)

### Automatic Installation

**Windows:**
```bash
# Clone the repository
git clone https://github.com/yourusername/ask.git
cd ask

# Run automatic installer
install.bat
```

**Linux/macOS:**
```bash
# Clone the repository
git clone https://github.com/yourusername/ask.git
cd ask

# Run automatic installer
chmod +x install.sh
./install.sh
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ask.git
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
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB | 50GB+ |
| **GPU** | CPU-only | NVIDIA GTX 1650+ |
| **CPU** | 4 cores | 8+ cores |

## ⚡ Quick Start

### 1. Configuration Setup

```bash
# Copy template and configure
cp ask.env.template ask.env

# Edit ask.env with your settings
# Required: TOGETHER_API_KEY=your_api_key_here
```

### 2. Basic Usage

```bash
# Simple mode (1 Q&A pair)
python main.py simple

# Hybrid mode (10 Q&A pairs)
python main.py hybrid

# Cross-disciplinary mode (10 Q&A pairs)
python main.py cross-disciplinary

# Chained mode (10 Q&A pairs)
python main.py chained
```

### 3. View Results

Generated content will be saved in:
- `images/individual/` - Individual Q&A images
- `images/compilations/` - Compilation images
- `images/covers/` - Cover images
- `images/toc/` - Table of contents
- `log.csv` - Content database

## ⚙️ Configuration

### Environment Variables

The tool is configured through `ask.env`. Key settings include:

```bash
# API Configuration
TOGETHER_API_KEY=your_api_key_here
TOGETHER_API_BASE=https://api.together.xyz/v1

# AI Models
TEXT_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo-Free
IMAGE_MODEL=black-forest-labs/FLUX.1-schnell-Free

# Image Generation
IMAGE_WIDTH=1072
IMAGE_HEIGHT=1792
IMAGE_QUALITY=95

# Generation Modes
HYBRID_THEME_COUNT=5
CROSS_DISCIPLINARY_THEME_COUNT=10
CHAIN_LENGTH=5
```

### Theme Configuration

Configure themes in `ask.env`:

```bash
# Simple mode themes
SIMPLE_MODE_THEMES=design_research,technology_innovation,sustainability_science,engineering_systems,environmental_design,urban_planning,spatial_design,digital_technology

# Default chained themes
DEFAULT_CHAINED_THEMES=design_research,technology_innovation
```

## 🎯 Usage Modes

### Simple Mode
Generate a single Q&A pair with image.

```bash
python main.py simple
```

**Output**: 1 Q&A pair with individual image

### Hybrid Mode
Generate content across multiple themes with chaining.

```bash
python main.py hybrid
```

**Output**: 10 Q&A pairs (5 themes × 2 chains each)

### Cross-Disciplinary Mode
Generate content exploring connections between different themes.

```bash
python main.py cross-disciplinary
```

**Output**: 10 Q&A pairs across diverse themes

### Chained Mode
Generate deep exploration of specific themes through chaining.

```bash
python main.py chained
```

**Output**: 10 Q&A pairs (2 themes × 5 chains each)

## 🎨 Image Generation

### Generation Methods

The tool supports multiple image generation methods with intelligent fallback:

1. **GPU Generation** (Priority when enabled)
   - Uses NVIDIA CUDA for fast generation
   - Optimized for GTX 1650+ graphics cards
   - High-quality output with memory optimization

2. **CPU Generation** (Fallback)
   - Uses Diffusers with LCM-SD15 model
   - Memory-efficient for CPU-only systems
   - Slower but fully offline

3. **API Generation** (Fallback)
   - Uses Together.ai FLUX.1 model
   - High-quality cloud-based generation
   - Requires internet connection

4. **Placeholder Images** (Final fallback)
   - Generated when all other methods fail
   - Professional styling with error indication

### Configuration

```bash
# GPU Settings
GPU_IMAGE_GENERATION_ENABLED=true
GPU_MODEL_ID=runwayml/stable-diffusion-v1-5
GPU_DEFAULT_STEPS=20

# CPU Settings
CPU_IMAGE_GENERATION_ENABLED=false
CPU_MODEL_ID=latent-consistency/lcm-sd15
CPU_DEFAULT_STEPS=6
```

## 📁 Project Structure

```
ask/
├── main.py                          # Main orchestration pipeline
├── ask.env                          # Configuration file
├── ask.env.template                 # Configuration template
├── requirements.txt                 # Python dependencies
├── install_dependencies.py          # Smart installer
├── install.bat                      # Windows installer
├── install.sh                       # Linux/macOS installer
│
├── Core Components/
│   ├── research_orchestrator.py     # Research orchestration
│   ├── research_question_generator.py # Question generation
│   ├── research_answer_generator.py # Answer generation
│   ├── research_csv_manager.py      # Data management
│   └── volume_manager.py            # Volume management
│
├── Image Generation/
│   ├── image_generation_system.py   # Main image system
│   ├── smart_image_generator.py     # Smart fallback system
│   ├── gpu_image_generator.py       # GPU generation
│   ├── cpu_image_generator.py       # CPU generation
│   ├── image_create_ai.py           # API generation
│   ├── image_add_text.py            # Text overlay
│   └── image_typography_config.py   # Typography settings
│
├── Management Systems/
│   ├── research_question_manager.py # Question management
│   ├── research_answer_manager.py   # Answer management
│   ├── style_manager.py             # Style management
│   └── research_theme_system.py     # Theme system
│
├── Output/
│   ├── images/                      # Generated images
│   │   ├── individual/              # Individual Q&A images
│   │   ├── compilations/            # Compilation images
│   │   ├── covers/                  # Cover images
│   │   └── toc/                     # Table of contents
│   ├── logs/                        # Log files
│   └── log.csv                      # Content database
│
└── Tests/
    └── test_image_generation.py     # Image generation tests
```

## 🔧 API Reference

### Main Pipeline

```python
from main import SimplePipeline

# Initialize pipeline
pipeline = SimplePipeline()

# Run simple mode
pipeline.run_simple_mode()

# Run hybrid mode
pipeline.run_hybrid_mode()
```

### Image Generation

```python
from smart_image_generator import generate_image_with_smart_fallback

# Generate image with smart fallback
image = generate_image_with_smart_fallback(
    prompt="Your prompt here",
    theme="design_research"
)
```

### Research Orchestration

```python
from research_orchestrator import ResearchOrchestrator

# Initialize orchestrator
orchestrator = ResearchOrchestrator()

# Generate chained content
content = orchestrator.generate_chained_content(
    themes=["design_research", "technology_innovation"],
    chain_length=3
)
```

## 🐛 Troubleshooting

### Common Issues

**1. API Key Error**
```bash
ERROR: TOGETHER_API_KEY environment variable is not set!
```
**Solution**: Set your API key in `ask.env`

**2. GPU Generation Fails**
```bash
CUDA not available
```
**Solution**: Install CUDA drivers or disable GPU generation

**3. Memory Issues**
```bash
Out of memory error
```
**Solution**: Reduce image size or enable memory optimization

**4. Import Errors**
```bash
ModuleNotFoundError
```
**Solution**: Run `pip install -r requirements.txt`

### Performance Optimization

**For GPU Users:**
- Enable `GPU_IMAGE_GENERATION_ENABLED=true`
- Set appropriate memory optimizations
- Use `GPU_DEFAULT_STEPS=20` for quality

**For CPU Users:**
- Enable `CPU_IMAGE_GENERATION_ENABLED=true`
- Use `CPU_DEFAULT_STEPS=6` for speed
- Enable memory optimizations

**For API Users:**
- Ensure stable internet connection
- Set appropriate rate limits
- Monitor API usage

### Logging

Logs are stored in `logs/execution.log`. Enable debug mode for detailed logging:

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ask.git
cd ask

# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_image_generation.py

# Check code quality
python -m flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Together.ai** for AI model access
- **Diffusers** for image generation capabilities
- **OpenAI** for inspiration and research methodologies
- **Community contributors** for feedback and improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ask/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ask/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/ask/wiki)

---

**Made with ❤️ for the research community**

*Last updated: August 2024*