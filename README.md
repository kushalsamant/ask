# ASK: Daily Architectural Research - Instagram Story Generator

An AI-powered Instagram story generator that creates daily architectural content across 7 disciplines: Architecture, Construction, Design, Engineering, Interiors, Planning, and Urbanism.

## 🎯 Features

### Core Functionality
- **Multi-Discipline Questions**: Generates unique questions for 7 architectural disciplines
- **AI-Powered Image Generation**: Creates stunning Instagram stories using Together.ai FLUX.1 model
- **Professional Text Overlays**: Adds beautiful typography with prompts, branding, and image numbers
- **Automated Pipeline**: Complete workflow from question generation to final Instagram stories

### Architectural Disciplines
- **Architecture**: Building design and spatial concepts
- **Construction**: Building methods and materials
- **Design**: Creative space solutions
- **Engineering**: Structural and technical systems
- **Interiors**: Interior design and space planning
- **Planning**: Urban and city planning
- **Urbanism**: Public spaces and urban design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Together.ai API key

### Installation
```bash
git clone <repository-url>
cd ask
pip install -r requirements.txt
```

### Configuration
1. Copy `ask.env.template` to `ask.env`
2. Add your Together.ai API key to `ask.env`:
   ```
   TOGETHER_API_KEY=your_api_key_here
   ```

## 📱 Usage

### Generate Instagram Stories
```bash
python daily.py
```

This will:
1. Generate 7 unique questions (one per discipline)
2. Create Instagram story images (1072x1792px)
3. Add professional text overlays
4. Save images to `images/` directory
5. Log questions to `questions.log`

### Output
- **7 Instagram Stories**: One for each architectural discipline
- **Professional Layout**: Full-bleed images with text overlays
- **Branded Content**: "ASK: Daily Architectural Research" branding
- **Question Log**: All generated questions saved to `questions.log`

## 📁 Project Structure

```
ask/
├── 📄 daily.py     # Main Instagram story generator
├── 📄 ask.env                     # Environment variables (local)
├── 📄 ask.env.template            # Environment template
├── 📄 requirements.txt            # Python dependencies
├── 📄 README.md                   # This file
├── 📄 .gitignore                  # Git ignore rules
├── 📄 questions.log               # Generated questions log
├── 📁 images/                     # Generated Instagram stories
├── 📁 logs/                       # Application logs
├── 📁 .git/                       # Git repository
└── 📁 .github/                    # GitHub workflows
```

## 🎨 Instagram Story Features

### Image Specifications
- **Dimensions**: 1072x1792 pixels (Instagram story format)
- **Quality**: High-resolution AI-generated architectural visuals
- **Style**: Discipline-specific architectural styles

### Text Overlay Design
- **Main Prompt**: Large, readable question text
- **Brand Text**: "ASK: Daily Architectural Research"
- **Image Number**: Sequential numbering (#01, #02, etc.)
- **Professional Typography**: Clean fonts with shadows and gradients
- **Proper Spacing**: Professional layout with adequate padding

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
TOGETHER_API_KEY=your_api_key
TOGETHER_API_URL=https://api.together.xyz/v1

# AI Model
IMAGE_MODEL=black-forest-labs/FLUX.1-schnell-free

# Image Generation Settings
INFERENCE_STEPS=4
GUIDANCE_SCALE=7.5
RATE_LIMIT_DELAY=10.0

# Directories
LOG_DIR=logs
IMAGES_DIR=images

# Questions by Discipline (105 total questions)
ARCHITECTURE_QUESTIONS=question1|question2|...
CONSTRUCTION_QUESTIONS=question1|question2|...
# ... (7 disciplines with 15 questions each)
```

## 🧪 Testing

### Run the Generator
```bash
python daily.py
```

### Check Output
- Verify 7 images are generated in `images/` directory
- Check `questions.log` for generated questions
- Review `logs/` for any errors

## 🔍 Troubleshooting

### Common Issues
1. **API Errors**: Check your Together.ai API key and rate limits
2. **Image Generation Failures**: Verify API configuration and internet connection
3. **Text Overlay Issues**: Ensure PIL/Pillow is properly installed
4. **Permission Errors**: Check write permissions for `images/` and `logs/` directories

### Logs
- **Application Logs**: Check `logs/daily_zine.log`
- **Questions Log**: Review `questions.log` for generated content
- **Error Details**: Full error messages in log files

## 📊 Performance

### Metrics
- **Image Generation**: ~30-60 seconds per image
- **Total Runtime**: ~5-10 minutes for 7 images
- **API Response**: <2 seconds average
- **Text Overlay**: <5 seconds per image

### Optimization Features
- **Retry Logic**: Automatic retry on API failures
- **Rate Limiting**: Intelligent API rate limiting
- **Error Handling**: Graceful failure handling
- **Memory Management**: Efficient image processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `python daily.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues related to:
- **Image Generation**: Check API configuration and logs
- **Text Overlays**: Verify PIL installation and font availability
- **Questions**: Review `questions.log` for generated content

---

**Status**: Production Ready | **Last Updated**: August 2025 | **Version**: Instagram Story Generator v2.0
