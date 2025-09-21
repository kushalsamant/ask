# ASK: Daily Research - Offline-First AI Research Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Offline-First](https://img.shields.io/badge/Offline-First-GPU%20%7C%20CPU%20%7C%20API-orange.svg)]()

> **Advanced research tool that generates high-quality Q&A content with photorealistic images, optimized for Instagram stories and social media sharing.**

## 💝 Support ASK: Daily Research

**Help us democratize research knowledge and make academic content accessible to everyone!**

🔬 **What we're building**: A revolutionary offline-first research tool that transforms complex academic concepts into engaging, shareable content with stunning visuals.

🎯 **Our mission**: Bridge the gap between academic research and public understanding by creating beautiful, educational content that's perfect for social media sharing.

### 🌟 Why Sponsor ASK?

- **📚 Educational Impact**: Every sponsorship helps create more educational content for students, researchers, and curious minds worldwide
- **🔬 Research Democratization**: Making complex research accessible through beautiful visual storytelling
- **💻 Open Source Excellence**: Supporting sustainable development of cutting-edge AI research tools
- **🌍 Global Knowledge Sharing**: Enabling researchers to share their work in engaging, social media-friendly formats

### 🎁 Support Our Mission

**Every contribution, no matter the size, makes a difference!**

Your support enables us to:
- 🚀 Develop new research themes and content types
- 🔧 Improve AI model performance and reliability  
- 📱 Create mobile apps and additional platforms
- 🌐 Build a global research content community
- 🎓 Provide free educational resources to students

**[Become a GitHub Sponsor →](https://github.com/sponsors/kushalsamant)**

**Every contribution helps us make research more accessible and engaging for everyone!** 💙

-

*"The best way to predict the future is to create it." - Let's build the future of research communication together!*

## 🌟 Overview

ASK is a sophisticated offline-first research tool that automatically generates comprehensive question-answer pairs with stunning visual content. Built with a focus on research methodology, sustainability science, engineering systems, and multi-theme exploration, it creates Instagram story-sized images (1080x1920) perfect for social media sharing.

### ✨ Key Features

- **🔬 Offline-First ure**: GPU → CPU → API fallback system
- **📱 Instagram Story Optimized**: All images generated at 1080x1920 pixels
- **🤖 Enhanced Simple Mode**: Multi-theme support with connected, chained-like experience
- **🎨 Photorealistic Images**: Advanced AI image generation with text overlays
- **📊 Comprehensive Logging**: Detailed CSV tracking and volume management
- **⚡ Lazy Model Loading**: Smart model downloads only when needed
- **🔄 Multi-Image Support**: Long answers automatically split across multiple images
- **🧠 Intelligent Content Generation**: Multi-theme research exploration
- **🎯 Sequential Knowledge Building**: Questions and answers numbered systematically (ASK-01, ASK-02, etc.)

## 🎨 What Makes ASK Special?

### **🎨 Photorealistic Visualizations**
- **AI-Generated Backgrounds**: Every research question and answer comes with stunning, photorealistic imagery
- **Theme-Specific Design**: Each discipline gets custom elements tailored to the research field
- **Professional Quality**: 8K resolution, professional photography style, realistic materials and lighting
- **Offline-First**: Works completely offline with cached AI models - no internet required!

### **🧠 Intelligent Content Generation**
- **Multi-Theme Research**: Explores intersections between various fields and disciplines
- **Sequential Knowledge Building**: Questions and answers are numbered sequentially (ASK-01, ASK-02, etc.) for systematic learning
- **Sentence-Case Answers**: All content is professionally formatted for readability
- **Research Focus**: Every piece of content is specifically tailored to research and practice

### **⚡ Advanced Technology Stack**
- **GPU-Primary ure**: Optimized for NVIDIA GPUs with CPU fallback
- **Stable Diffusion 2.1**: Latest AI models for photorealistic image generation
- **Offline Operation**: Complete independence from internet connectivity
- **Smart Fallback System**: GPU → CPU → API (if enabled) → Placeholder

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **8GB RAM minimum** (16GB recommended)
- **2GB free storage** for models
- **NVIDIA GPU with CUDA** (optional, for accelerated generation)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kushalsamant/ask.git
cd ask
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp ask.env.template ask.env
# Edit ask.env with your settings
```

4. **Run the tool**
```bash
python main.py
```

### 🎯 First Run
- **Model Download**: First run downloads AI models (~10GB)
- **Offline Operation**: Subsequent runs work completely offline
- **Content Generation**: Automatic generation of research content
- **Visual Output**: High-quality images in `images/` folder

## 📋 Usage Modes

### 🎯 Enhanced Simple Mode (Default)
```bash
python main.py
```
Generates Q&A pairs with multi-theme support and connected, chained-like experience.

### 📖 Help
```bash
python main.py -help
```
Shows all available modes and options.

## 🏗️ System ure

### Offline-First Design
```
Primary: GPU Generation (offline)
    ↓
Fallback: CPU Generation (offline)
    ↓
Last Resort: API Generation (online)
```

### Core Components

| Component | Purpose | Status |
|-|-|-|
| `main.py` | Main pipeline orchestrator | ✅ Active |
| `smart_image_generator.py` | Smart fallback image generation | ✅ Active |
| `offline_question_generator.py` | Template-based question generation | ✅ Active |
| `offline_answer_generator.py` | Template-based answer generation | ✅ Active |
| `image_add_text.py` | Text overlay and multi-image support | ✅ Active |
| `volume_manager.py` | Image numbering and volume tracking | ✅ Active |

## ⚙️ Configuration

### Environment Variables

Key configuration options in `ask.env`:

```env
# Image Generation
IMAGE_WIDTH=1080          # Instagram story width
IMAGE_HEIGHT=1920         # Instagram story height
IMAGE_QUALITY=95          # Image quality (1-100)

# AI Models
GPU_MODEL_ID=stabilityai/stable-diffusion-2-1
CPU_MODEL_ID=stabilityai/stable-diffusion-2-1-base

# Generation Modes
GPU_IMAGE_GENERATION_ENABLED=true
CPU_IMAGE_GENERATION_ENABLED=true
API_IMAGE_GENERATION_ENABLED=false

# Text Processing
MAX_CHARS_PER_LINE=50     # Characters per line
MULTI_IMAGE_THRESHOLD=800 # Trigger multi-image mode

# Multi-Theme Support
SIMPLE_MODE_THEMES=ure,marketing,cricket
```

### Research Themes

The tool supports multiple research themes:

- **sustainability_science**: Environmental and sustainability research
- **engineering_systems**: Systems engineering and design
- **technology_innovation**: Technology and innovation studies
- **urban_planning**: Urban development and planning
- **research_methodology**: Research methods and approaches
- **ure**: ural design and theory
- **marketing**: Marketing strategies and research
- **cricket**: Sports research and analysis

## 📊 Output Structure

### Generated Content

Each run creates:
- **Question Image**: `ASK-XXX-theme-q.jpg` (1080x1920)
- **Answer Image**: `ASK-XXX-theme-a.jpg` (1080x1920)
- **Multi-Image Answers**: `ASK-XXX-theme-a-1.jpg`, `ASK-XXX-theme-a-2.jpg`, etc.

### File Organization

```
ask/
├── images/                 # Generated images
│   ├── ASK-001-*.jpg      # Question images (odd numbers)
│   ├── ASK-002-*.jpg      # Answer images (even numbers)
│   └── compilations/      # Volume compilations
├── logs/                  # Execution logs
├── models/                # Downloaded AI models
├── log.csv               # Q&A tracking database
└── ask.env               # Configuration file
```

### CSV Logging

The system maintains detailed logs in `log.csv`:

| Column | Description |
|-|-|
| `id` | Sequential identifier |
| `theme` | Research theme |
| `question` | Generated question |
| `answer` | Generated answer |
| `question_image` | Question image filename |
| `answer_image` | Answer image filename |
| `is_question` | Boolean flag |
| `timestamp` | Creation timestamp |

## 🔧 Advanced Features

### Multi-Image Support

Long answers are automatically split across multiple images:
- **Threshold**: 800+ characters triggers multi-image mode
- **Chunk Size**: 1000 characters per image
- **Naming**: `ASK-XXX-theme-a-1.jpg`, `ASK-XXX-theme-a-2.jpg`

### Volume Management

- **Automatic numbering**: Sequential image numbers (odd for questions, even for answers)
- **Volume tracking**: Organizes content into manageable volumes
- **Duplicate prevention**: Prevents duplicate question generation

### Smart Fallback System

1. **GPU Generation**: High-quality, fast generation (primary)
2. **CPU Generation**: Reliable fallback (secondary)
3. **API Generation**: Last resort with internet (tertiary)

## 💡 Perfect For:

### **🏢 Research Professionals**
- **Research Inspiration**: Daily research questions and insights
- **Visual Presentations**: High-quality photorealistic backgrounds for presentations
- **Knowledge Building**: Systematic exploration of research concepts
- **Offline Work**: Complete functionality without internet dependency

### **🎓 Students & Educators**
- **Learning Tool**: Structured research content
- **Visual Learning**: Photorealistic imagery for better understanding
- **Research Projects**: Ready-to-use research content
- **Educational Presentations**: Professional-quality visual assets

### **🔬 Researchers & Innovators**
- **Multi-Theme Exploration**: Intelligent exploration across multiple research themes
- **Content Generation**: Automated research question and answer creation
- **Visual Documentation**: Professional imagery for research
- **Knowledge Management**: Systematic organization of research content

### **💼 Content Creators**
- **Research Content**: Daily research content for various fields
- **Visual Assets**: High-quality backgrounds for any discipline
- **Professional Branding**: Consistent ASK branding and numbering
- **Offline Production**: Create content without internet dependency

## 🛠️ Development

### Project Structure

```
ask/
├── main.py                    # Main pipeline
├── requirements.txt           # Python dependencies
├── ask.env.template          # Configuration template
├── ask.env                   # Active configuration
├── *.py                      # Core modules
├── images/                   # Generated content
├── logs/                     # Execution logs
├── models/                   # AI models cache
└── README.md                # This file
```

### Key Modules

- **`main.py`**: Pipeline orchestrator with multiple modes
- **`smart_image_generator.py`**: Intelligent image generation with fallbacks
- **`offline_question_generator.py`**: Template-based question generation
- **`offline_answer_generator.py`**: Template-based answer generation
- **`image_add_text.py`**: Text overlay and multi-image support
- **`volume_manager.py`**: Image numbering and volume management
- **`research_csv_manager.py`**: CSV logging and data management

### Dependencies

Core dependencies include:
- **PyTorch**: Deep learning framework
- **Diffusers**: Hugging Face image generation
- **Pillow**: Image processing
- **Transformers**: AI model loading
- **Accelerate**: Performance optimization

## 📈 Performance

### Hardware Recommendations

| Component | Minimum | Recommended |
|-|-|-|
| **CPU** | Multi-core | 8+ cores |
| **RAM** | 8GB | 16GB+ |
| **GPU** | None | NVIDIA with CUDA |
| **Storage** | 2GB | 5GB+ |

### Generation Times

| Mode | GPU | CPU | API |
|-|-|-|-|
| **Simple** | ~30s | ~2min | ~10s |
| **Enhanced** | ~45s | ~3min | ~15s |
| **Multi-Image** | ~60s | ~4min | ~20s |

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
pip install -r requirements.txt -upgrade
```

**2. GPU Not Detected**
```bash
# Check CUDA installation
nvidia-smi
# Install PyTorch with CUDA
pip install torch torchvision torchaudio -index-url https://download.pytorch.org/whl/cu118
```

**3. Model Download Issues**
```bash
# Clear cache and retry
rm -rf models/
python main.py
```

**4. Memory Issues**
```bash
# Reduce batch size in ask.env
BATCH_SIZE=1
```

### Log Files

- **`logs/execution.log`**: Detailed execution logs
- **`log.csv`**: Q&A content database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/kushalsamant/ask.git
cd ask
pip install -r requirements.txt
cp ask.env.template ask.env
# Edit ask.env for your environment
python main.py -help
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For the diffusers and transformers libraries
- **Stability AI**: For the Stable Diffusion models
- **PyTorch Team**: For the deep learning framework
- **Research Community**: For inspiration and feedback

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kushalsamant/ask/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kushalsamant/ask/discussions)
- **Documentation**: [Wiki](https://github.com/kushalsamant/ask/wiki)

-

**Made with ❤️ for the research community**

*Generate, explore, and share knowledge with ASK: Daily Research*

## 🔧 System ure & Implementation Status

### Current System State

**Date**: 2025-08-24  
**Analysis**: Current system ure vs. intended offline-first, GPU-primary design

#### 1. Smart Image Generator (smart_image_generator.py)
- ✅ **CORRECT**: GPU → CPU → API → Placeholder fallback order
- ✅ **CORRECT**: GPU is tried FIRST when enabled
- ✅ **FIXED**: Environment variables now default to "true" for both GPU and CPU
- ✅ **FIXED**: Clear indication that GPU is PRIMARY mode

#### 2. Environment Configuration
- ✅ **CORRECT**: ask.env.template has both GPU and CPU enabled by default
- ✅ **CORRECT**: ask.env has both GPU and CPU enabled
- ✅ **FIXED**: smart_image_generator.py now defaults to "true" instead of "false"

#### 3. Hardware Detection
- ✅ **CORRECT**: GPU detection with CUDA availability check
- ✅ **CORRECT**: Automatic fallback to CPU when GPU unavailable
- ✅ **CORRECT**: Proper CUDA version detection and PyTorch installation

#### 4. Main Pipeline (main.py)
- ✅ **FIXED**: API key validation is now optional for offline operation
- ✅ **FIXED**: Clear indication of offline-first operation
- ✅ **FIXED**: API key validation only happens when API generation is enabled

#### 5. Documentation
- ✅ **CORRECT**: README.md accurately reflects offline-first approach
- ✅ **CORRECT**: Hardware requirements show GPU as primary
- ✅ **CORRECT**: Generation methods show proper hierarchy

### Current Fallback Order (Correct)
1. **GPU Generation (Primary Mode)** - Offline
2. **CPU Generation (First Fallback)** - Offline
3. **API Generation (Last Resort)** - Requires Internet
4. **Placeholder Images (Emergency)** - Offline

### Environment Variables (Fixed)
- **GPU_IMAGE_GENERATION_ENABLED=true** ✅ (default)
- **CPU_IMAGE_GENERATION_ENABLED=true** ✅ (default)
- **API_IMAGE_GENERATION_ENABLED=false** ✅ (default)

### ✅ Completed Fixes

#### 1. Smart Image Generator Environment Variables
- Changed GPU_IMAGE_GENERATION_ENABLED default from "false" to "true"
- Changed CPU_IMAGE_GENERATION_ENABLED default from "false" to "true"
- Now defaults to offline-first operation

#### 2. Main Pipeline API Key Requirement
- Made API key validation optional for offline operation
- Added API_IMAGE_GENERATION_ENABLED environment variable check
- Only requires API key if API generation is explicitly enabled
- Added clear messaging for offline mode

#### 3. Environment Configuration
- Added API_IMAGE_GENERATION_ENABLED=false to ask.env.template
- Added API_IMAGE_GENERATION_ENABLED=false to ask.env
- Updated comments to reflect offline-first approach

#### 4. Documentation and Comments
- Updated smart_image_generator.py docstring to emphasize offline-first
- Updated main.py docstring to emphasize offline-first
- Added clear comments for each generation method:
  - GPU: "Primary Mode - Offline"
  - CPU: "First Fallback - Offline"
  - API: "Last Resort - Requires Internet"
  - Placeholder: "Emergency Fallback - Offline"

#### 5. Terminology Standardization
- Standardized on "primary/fallback" terminology
- Consistent messaging across all files
- Clear hierarchy: Primary → First Fallback → Last Resort → Emergency

### Current System Behavior

#### Offline-First Operation
- GPU and CPU generation enabled by default
- API generation disabled by default
- No API key required for offline operation
- Clear fallback hierarchy maintained

#### Fallback Order
1. **GPU Generation (Primary Mode)** - Offline, fastest, highest quality
2. **CPU Generation (First Fallback)** - Offline, slower but reliable
3. **API Generation (Last Resort)** - Requires internet, only when enabled
4. **Placeholder Images (Emergency)** - Offline, always available

#### Environment Variables
- **GPU_IMAGE_GENERATION_ENABLED=true** (default)
- **CPU_IMAGE_GENERATION_ENABLED=true** (default)
- **API_IMAGE_GENERATION_ENABLED=false** (default)

#### User Experience
- Users can run the tool completely offline
- No API key required for basic operation
- Clear messaging about offline mode
- Graceful fallback when hardware unavailable

### Verification

The system now properly implements offline-first ure:
- ✅ Defaults to offline operation
- ✅ GPU is primary mode
- ✅ CPU is first fallback
- ✅ API is last resort (optional)
- ✅ No API key required for offline use
- ✅ Clear documentation and messaging
- ✅ Consistent terminology throughout

### Result

The ASK research tool is now truly offline-first, with GPU as the primary mode of operation, CPU as the first fallback, and API generation as an optional last resort. Users can run the tool completely offline without requiring an API key, while still having the option to enable API generation if needed.
