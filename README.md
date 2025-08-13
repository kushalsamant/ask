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

## 📊 **Content Generation Stats**

### **Daily Output**
- **28 Stories Per Day** (4 runs × 7 stories per run)
- **196 Stories Per Week** (4 runs × 7 stories × 7 days)
- **840 Stories Per Month** (4 runs × 7 stories × 30 days)  
- **10,220 Stories Per Year** (4 runs × 7 stories × 365 days)

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

## 🔧 **Quick Start**

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
   
   **Note**: Your API key should start with `tgp_v1_` for Together.ai

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
├── 📄 daily.py                    # Main Instagram story generator
├── 📄 ask.env                     # Environment variables
├── 📄 ask.env.template            # Environment template
├── 📄 requirements.txt            # Python dependencies
├── 📄 README.md                   # This file
├── 📄 .gitignore                  # Git ignore rules
├── 📄 log.csv                     # Generated questions log
├── 📁 images/                     # Generated Instagram stories
├── 📁 logs/                       # Application logs
└── 📁 .github/                    # GitHub workflows
```

---

## 🔍 **Troubleshooting**

### **Common Issues**
1. **API Key Issues**: 
   - Ensure your Together.ai API key starts with `tgp_v1_`
   - Verify the key is properly set in `ask.env`
2. **API Errors**: Check your Together.ai API key and rate limits
3. **Image Generation Failures**: Verify API configuration and internet connection
4. **Text Overlay Issues**: Ensure PIL/Pillow is properly installed
5. **Permission Errors**: Check write permissions for `images/` and `logs/` directories

### **Logs**
- **Application Logs**: Check `logs/execution.log`
- **Questions Log**: Review `log.csv` for generated content

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `python daily.py`
5. Submit a pull request

---

## 📄 **License**

This project is licensed under the MIT License.

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

**Status**: Production Ready | **Last Updated**: August 2025 | **Version**: Instagram Story Generator v2.4

*Built with ❤️ for the architecture community*
