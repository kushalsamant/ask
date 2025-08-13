# 🏗️ ASK: Daily Architectural Research
## *AI-Powered Instagram Stories for Architecture Enthusiasts*

---

## 🎯 **The Vision**

Wake up to fresh, thought-provoking architectural content every day.  
**ASK: Daily Architectural Research** is an AI-powered Instagram story generator that creates stunning visuals and questions across 7 architectural disciplines daily.

---

## 🌟 **Features**

- **AI-Powered Visuals:** Uses Together.ai's FLUX.1 model for architectural images.
- **Intelligent Questions:** 105 unique questions, 7 disciplines.
- **Professional Design:** Automated text overlays, branding, and numbering.

---

## 🏛️ **Disciplines Covered**

- Architecture
- Construction
- Design
- Engineering
- Interiors
- Planning
- Urbanism

---

## 📊 **Content Generation**

- **Daily:** 7 stories (7 disciplines)
- **Weekly:** 49 stories
- **Monthly:** 210 stories
- **Yearly:** 2,555 stories

**Performance:**  
- Image generation: ~30–60s/image  
- Full run: ~5–10min  
- API response: <2s  
- Text overlay: <5s/image

---

## 🎨 **Sample Story**

Each Instagram story includes:
- AI-generated architectural visual
- Thought-provoking question
- Branding: "ASK: Daily Architectural Research"
- Sequential numbering (#01, #02, ...)

---

## 💡 **Why Use ASK?**

- **Inspiration:** Daily architectural ideas.
- **Education:** Learn about disciplines.
- **Visual Learning:** AI-generated concepts.
- **Community:** Questions spark discussion.

---

## 🔧 **Quick Start**

### Prerequisites
- Python 3.8+
- Together.ai API key (starts with `tgp_v1_`)

### Installation
```sh
git clone <repository-url>
cd ask
pip install -r requirements.txt
```

### Configuration
1. Copy `ask.env.template` to `ask.env`:
   ```sh
   cp ask.env.template ask.env
   ```
2. Add your Together.ai API key to `ask.env`:
   ```
   TOGETHER_API_KEY=your_api_key_here
   ```

### Generate Instagram Stories
```sh
python daily.py
```
This will:
- Generate 7 questions (one per discipline)
- Create Instagram story images (1072×1792px)
- Add text overlays and branding
- Save images to `images/`
- Log questions to `log.csv`

---

## 📁 **Project Structure**

```
ask/
├── daily.py           # Main generator script
├── ask.env            # Environment variables
├── ask.env.template   # Example config
├── requirements.txt   # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
├── log.csv            # Generated questions log
├── images/            # Generated stories
├── logs/              # Application logs
└── .github/           # GitHub workflows
```

---

## 🔍 **Troubleshooting**

- **API Key Issues:**  
  - Key must start with `tgp_v1_`
  - Set in `ask.env`
- **API Errors:**  
  - Check key and rate limits
- **Image Generation Failures:**  
  - Verify API config and internet
- **Text Overlay Issues:**  
  - Ensure Pillow is installed
- **Permission Errors:**  
  - Check write access to `images/` and `logs/`

**Logs:**  
- Application: `logs/execution.log`  
- Questions: `log.csv`

---

## 🤝 **Contributing**

1. Fork the repo
2. Create a feature branch
3. Make changes
4. Test with `python daily.py`
5. Submit a pull request

---

## 📄 **License**

MIT License

---

## 🌟 **Join the ASK Community**

Whether you’re a student, creator, developer, or enthusiast—ASK brings architectural thinking to everyone.

---

**Status:** Production Ready  
**Last Updated:** August 2025  
**Version:** Instagram Story Generator v2.0

*Built with ❤️ for the architecture community*
