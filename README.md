# 🏗️ ASK: Daily Architectural Research
## *AI-Powered Instagram Stories for Architecture Enthusiasts*

---

## 🎯 **The Vision**

**Imagine waking up every day to fresh, thought-provoking architectural content that challenges your perspective on the built environment.**

That's exactly what **ASK: Daily Architectural Research** delivers - an AI-powered Instagram story generator that creates stunning visual content across 7 architectural disciplines, 4 times daily, with questions that make you think deeper about the spaces we inhabit.

---

## 🌟 **What Makes This Special?**

### **🤖 AI-Powered Creativity**
- **Advanced AI Model**: Using Together.ai's FLUX.1 model for stunning architectural visuals
- **Intelligent Question Generation**: 105 unique questions across 7 disciplines
- **Professional Design**: Automated text overlays with perfect typography
- **24/7 Content Creation**: Running 4 times daily via GitHub Actions

### **📱 Instagram-Ready Content**
- **Perfect Dimensions**: 1072x1792px optimized for Instagram stories
- **Professional Branding**: "ASK: Daily Architectural Research" with sequential numbering
- **Visual Excellence**: Full-bleed images with elegant text overlays
- **Engagement Optimized**: Questions designed to spark conversations

### **🏛️ 7 Architectural Disciplines**
- **Architecture**: Building design and spatial concepts
- **Construction**: Building methods and materials  
- **Design**: Creative space solutions
- **Engineering**: Structural and technical systems
- **Interiors**: Interior design and space planning
- **Planning**: Urban and city planning
- **Urbanism**: Public spaces and urban design

---

## 🚀 **The Technology Behind the Magic**

### **🆕 Recent Improvements (v2.3)**
- **Streamlined Workflow**: Removed API connectivity testing for faster execution
- **Simplified Architecture**: Direct image generation without pre-flight checks
- **Enhanced Reliability**: Graceful handling of API issues during generation
- **Self-Documenting Code**: Every line in `daily.py` includes inline comments
- **Enhanced Configuration**: All settings in `ask.env` and `ask.env.template` are fully documented
- **Comprehensive Logging**: Enhanced debugging information and error reporting
- **Developer Experience**: Clear documentation and easier troubleshooting

### **Core Features**
- **Multi-Discipline Questions**: Generates unique questions for 7 architectural disciplines
- **AI-Powered Image Generation**: Creates stunning Instagram stories using Together.ai FLUX.1 model
- **Professional Text Overlays**: Adds beautiful typography with prompts, branding, and image numbers
- **Automated Pipeline**: Complete workflow from question generation to final Instagram stories

### **Technical Excellence**
- **Sequential Numbering**: Continuous image numbering across all runs
- **Immediate Logging**: Real-time tracking of generated content
- **Error Recovery**: Robust retry logic and failure handling
- **API Validation**: Built-in API key validation with format checking
- **Self-Documenting Code**: Comprehensive inline comments throughout the codebase
- **Permanent Storage**: All content committed to repository with full history

---

## 📊 **Content Generation Stats**

### **Daily Output**
- **28 Stories Per Week** (4 runs × 7 days)
- **120 Stories Per Month** (4 runs × 30 days)  
- **1,460 Stories Per Year** (4 runs × 365 days)

### **Performance Metrics**
- **Image Generation**: ~30-60 seconds per image
- **Total Runtime**: ~5-10 minutes for 7 images
- **API Response**: <2 seconds average
- **Text Overlay**: <5 seconds per image

---

## 🎨 **Sample Content Preview**

Each Instagram story features:
- **Stunning AI-Generated Visuals**: Architectural concepts brought to life
- **Thought-Provoking Questions**: "What makes a building feel like home?"
- **Professional Branding**: Clean, modern typography
- **Sequential Numbering**: #01, #02, #03... tracking all content

---

## 💡 **Why This Matters**

### **For Architecture Enthusiasts**
- **Daily Inspiration**: Fresh perspectives on architectural concepts
- **Educational Content**: Learn about different architectural disciplines
- **Visual Learning**: AI-generated visuals of architectural ideas
- **Community Building**: Questions that spark meaningful discussions

### **For Content Creators**
- **Consistent Content**: Reliable daily Instagram stories
- **Professional Quality**: Production-ready visuals and typography
- **Scalable System**: Automated content generation
- **Brand Building**: Consistent "ASK" branding across all content

---

## 🔧 **Technical Implementation**

### **GitHub Actions Automation**
The project includes a fully automated GitHub Actions workflow that:
- **Runs 4 times daily** at scheduled intervals
- **Validates API keys** before execution with format checking
- **Handles errors gracefully** with detailed debugging information
- **Commits generated content** to the repository automatically
- **Provides comprehensive logging** for troubleshooting
- **Validates configuration** and provides clear error messages
- **Streamlined execution** without pre-flight API connectivity tests

### **Quick Start for Developers**

#### **Prerequisites**
- Python 3.8+
- Together.ai API key

#### **Installation**
```bash
git clone <repository-url>
cd ask
pip install -r requirements.txt
```

#### **Configuration**
1. Copy `ask.env.template` to `ask.env`
2. Add your Together.ai API key to `ask.env`:
   ```
   TOGETHER_API_KEY=your_api_key_here
   TOGETHER_API_BASE=https://api.together.xyz/v1
   TOGETHER_API_URL=https://api.together.xyz/v1
   ```
   
   **Note**: Your API key should start with `tgsk_` or `tgp_v1_` for Together.ai
   
   **Pro Tip**: The configuration files include comprehensive inline comments explaining every setting!

#### **Generate Instagram Stories**
```bash
python daily.py
```

This will:
1. Generate 7 unique questions (one per discipline)
2. Create Instagram story images (1072x1792px)
3. Add professional text overlays
4. Save images to `images/` directory
5. Log questions to `log.csv`

---

## 📁 **Project Structure**

```
ask/
├── 📄 daily.py                    # Main Instagram story generator (fully commented)
├── 📄 ask.env                     # Environment variables with inline documentation
├── 📄 ask.env.template            # Environment template with detailed comments
├── 📄 requirements.txt            # Python dependencies
├── 📄 README.md                   # This file
├── 📄 .gitignore                  # Git ignore rules
├── 📄 log.csv                     # Generated questions log
├── 📁 images/                     # Generated Instagram stories
├── 📁 logs/                       # Application logs
├── 📁 .git/                       # Git repository
└── 📁 .github/                    # GitHub workflows
```

---

## 🎯 **Configuration Options**

### **Environment Variables**
```bash
# API Configuration
TOGETHER_API_KEY=your_api_key
TOGETHER_API_BASE=https://api.together.xyz/v1
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

### **📝 Self-Documenting Configuration**
Every configuration file includes comprehensive inline comments:
- **`ask.env.template`**: Template with detailed explanations for each setting
- **`ask.env`**: Your local configuration with inline documentation
- **`daily.py`**: Fully commented code explaining every function and line

---

## 🧪 **Testing & Quality Assurance**

### **Run the Generator**
```bash
python daily.py
```

### **Check Output**
- Verify 7 images are generated in `images/` directory
- Check `log.csv` for generated questions
- Review `logs/` for any errors

---

## 🔍 **Troubleshooting**

### **Common Issues**
1. **API Key Issues**: 
   - Ensure your Together.ai API key starts with `tgsk_` or `tgp_v1_`
   - Verify the key is properly set in `ask.env`
   - Check that `TOGETHER_API_BASE` and `TOGETHER_API_URL` are configured
   - The script validates API keys automatically and provides clear error messages
2. **API Errors**: Check your Together.ai API key and rate limits
3. **Image Generation Failures**: Verify API configuration and internet connection
4. **Text Overlay Issues**: Ensure PIL/Pillow is properly installed
5. **Permission Errors**: Check write permissions for `images/` and `logs/` directories
6. **Configuration Issues**: All settings are documented with inline comments in the config files

### **Logs**
- **Application Logs**: Check `logs/execution.log`
- **Questions Log**: Review `log.csv` for generated content
- **Error Details**: Full error messages in log files

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `python daily.py`
5. Ensure all code includes inline comments for clarity
6. Submit a pull request

### **Code Quality Standards**
- **Inline Comments**: Every line should be self-documenting
- **Configuration Documentation**: All settings should have clear explanations
- **Error Handling**: Comprehensive error messages and logging
- **API Validation**: Proper validation and testing of external services

---

## 📄 **License**

This project is licensed under the MIT License.

---

## 🆘 **Support**

For issues related to:
- **Image Generation**: Check API configuration and logs
- **Text Overlays**: Verify PIL installation and font availability
- **Questions**: Review `log.csv` for generated content

---

## 🌟 **Join the ASK Community**

**This isn't just a technical project - it's a movement to make architectural thinking accessible to everyone.**

Whether you're:
- **An architecture student** looking for daily inspiration
- **A content creator** seeking consistent, high-quality Instagram content
- **A developer** interested in AI-powered content generation
- **An architecture enthusiast** wanting to explore the built environment

**ASK: Daily Architectural Research** offers something unique - a blend of cutting-edge AI technology with thoughtful architectural discourse.

---

**Status**: Production Ready | **Last Updated**: December 2024 | **Version**: Instagram Story Generator v2.3

*Built with ❤️ for the architecture community*
