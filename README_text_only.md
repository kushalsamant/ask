# ASK: Daily Research - Text-Only Q&A Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Text-Only](https://img.shields.io/badge/Text--Only-Research%20Q%26A-lightblue.svg)]()

> **Simple research tool that generates high-quality Q&A content in text format, perfect for research, learning, and knowledge building.**

## 🌟 Overview

ASK is a simple text-based research tool that automatically generates comprehensive question-answer pairs. Built with a focus on research methodology, sustainability science, engineering systems, and multi-theme exploration, it creates text-only content perfect for research and learning.

### ✨ Key Features

- **🔬 Text-Only Generation**: Pure Q&A content without image dependencies
- **📚 Multi-Theme Support**: Research methodology, sustainability, engineering, and more
- **🔗 Connected Experience**: Questions reference previous content for continuity
- **📊 CSV Logging**: Detailed tracking of all generated content
- **⚡ Lightweight**: Minimal dependencies, fast execution
- **🧠 Intelligent Content**: Multi-theme research exploration
- **🎯 Sequential Knowledge Building**: Questions and answers numbered systematically

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **2GB RAM minimum**
- **100MB free storage**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kushalsamant/ask.git
cd ask
```

2. **Install dependencies**
```bash
pip install -r requirements_text_only.txt
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
- **Content Generation**: Automatic generation of research Q&A content
- **CSV Output**: High-quality Q&A pairs logged to `log.csv`

## 📋 Usage Modes

### 🎯 Text-Only Mode (Default)
```bash
python main.py
```
Generates Q&A pairs with multi-theme support and connected, chained-like experience.

### 📖 Help
```bash
python main.py --help
```
Shows all available modes and options.

## 🏗️ System Architecture

### Simple Text-Only Design
```
Input: Theme Selection
    ↓
Question Generation (Offline Templates)
    ↓
Answer Generation (Offline Templates)
    ↓
CSV Logging
    ↓
Output: Text Q&A Pairs
```

### Core Components

| Component | Purpose | Status |
|-----------|---------|--------|
| `main.py` | Main pipeline orchestrator | ✅ Active |
| `offline_question_generator.py` | Template-based question generation | ✅ Active |
| `offline_answer_generator.py` | Template-based answer generation | ✅ Active |
| `volume_manager.py` | Volume tracking | ✅ Active |
| `research_csv_manager.py` | CSV logging and data management | ✅ Active |

## ⚙️ Configuration

### Environment Variables

Key configuration options in `ask.env`:

```env
# Theme Configuration
SIMPLE_MODE_THEMES=research_methodology,technology_innovation,sustainability_science,engineering_systems,environmental_design,urban_planning,spatial_design,digital_technology

# Logging
LOG_DIR=logs
LOG_CSV_FILE=log.csv
```

### Research Themes

The tool supports multiple research themes:

- **research_methodology**: Research methods and approaches
- **sustainability_science**: Environmental and sustainability research
- **engineering_systems**: Systems engineering and design
- **technology_innovation**: Technology and innovation studies
- **urban_planning**: Urban development and planning
- **environmental_design**: Environmental design principles
- **spatial_design**: Spatial and interior design
- **digital_technology**: Digital technology and innovation

## 📊 Output Structure

### Generated Content

Each run creates:
- **Question**: Research question text
- **Answer**: Comprehensive answer text
- **Theme**: Research theme classification
- **Timestamp**: Generation timestamp

### File Organization

```
ask/
├── main.py                    # Main pipeline
├── requirements_text_only.txt # Dependencies
├── ask.env                   # Configuration file
├── log.csv                   # Q&A tracking database
└── logs/                     # Execution logs
```

### CSV Logging

The system maintains detailed logs in `log.csv`:

| Column | Description |
|--------|-------------|
| `question_number` | Sequential identifier |
| `theme` | Research theme |
| `question` | Generated question |
| `answer` | Generated answer |
| `question_image` | Empty (text-only) |
| `answer_image` | Empty (text-only) |
| `style` | Generation style |
| `is_used` | Usage tracking |
| `created_timestamp` | Creation timestamp |

## 💡 Perfect For:

### **🏢 Research Professionals**
- **Research Inspiration**: Daily research questions and insights
- **Knowledge Building**: Systematic exploration of research concepts
- **Offline Work**: Complete functionality without internet dependency
- **Content Creation**: Ready-to-use research content

### **🎓 Students & Educators**
- **Learning Tool**: Structured research content
- **Research Projects**: Ready-to-use research content
- **Educational Material**: Professional-quality research Q&A
- **Study Aid**: Systematic knowledge building

### **🔬 Researchers & Innovators**
- **Multi-Theme Exploration**: Intelligent exploration across multiple research themes
- **Content Generation**: Automated research question and answer creation
- **Knowledge Management**: Systematic organization of research content
- **Research Planning**: Structured approach to research topics

## 🛠️ Development

### Project Structure

```
ask/
├── main.py                    # Main pipeline
├── requirements_text_only.txt # Python dependencies
├── ask.env                   # Active configuration
├── *.py                      # Core modules
├── log.csv                   # Generated content
└── logs/                     # Execution logs
```

### Key Modules

- **`main.py`**: Pipeline orchestrator with text-only mode
- **`offline_question_generator.py`**: Template-based question generation
- **`offline_answer_generator.py`**: Template-based answer generation
- **`volume_manager.py`**: Volume numbering and management
- **`research_csv_manager.py`**: CSV logging and data management

### Dependencies

Core dependencies include:
- **python-dotenv**: Environment variable management
- **Standard Library**: All other functionality uses Python standard library

## 📈 Performance

### Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | Any | Multi-core |
| **RAM** | 2GB | 4GB+ |
| **Storage** | 100MB | 500MB+ |

### Generation Times

| Operation | Time |
|-----------|------|
| **Question Generation** | <1s |
| **Answer Generation** | <1s |
| **CSV Logging** | <1s |
| **Total Pipeline** | <5s |

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
pip install -r requirements_text_only.txt
```

**2. Missing log.csv**
```bash
# The system will create log.csv automatically on first run
python main.py
```

**3. Theme Configuration**
```bash
# Edit ask.env to customize themes
SIMPLE_MODE_THEMES=your,themes,here
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
pip install -r requirements_text_only.txt
cp ask.env.template ask.env
# Edit ask.env for your environment
python main.py --help
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Research Community**: For inspiration and feedback
- **Open Source Community**: For tools and libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kushalsamant/ask/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kushalsamant/ask/discussions)
- **Documentation**: [Wiki](https://github.com/kushalsamant/ask/wiki)

---

**Made with ❤️ for the research community**

*Generate, explore, and share knowledge with ASK: Daily Research*
