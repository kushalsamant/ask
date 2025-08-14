# ASK: Architectural Research Catalyst
## *Daily Research Questions Generator for the Built Environment*

Generate focused research questions across architecture, construction, design, engineering, interiors, planning, and urbanism — paired with AI-generated visuals for inspiration and deeper thinking.

## 🎯 What ASK Does

ASK is a Python-based tool that:
- Generates targeted research questions across 7 built environment disciplines
- Creates AI-generated architectural imagery using Together.ai's FLUX.1
- Combines questions and images in Instagram story format (1072×1792px)
- Logs all generated questions for future reference
- Can run multiple times daily (5-10 minutes per run)

## 🎓 Who Can Benefit?

### Researchers
- Find new research angles
- Discover unexplored questions
- Get daily inspiration for investigations
- Build interdisciplinary connections
- Document research ideas systematically

### Educators
- Source discussion topics for seminars
- Generate student assignments
- Inspire thesis directions
- Create visual teaching aids
- Facilitate critical thinking

### Practitioners
- Question current practices
- Explore new approaches
- Document professional inquiries
- Inspire team discussions
- Build research repositories

## 💡 Use Cases

### Research Development
- Daily research journaling
- Team brainstorming sessions
- Literature review guidance
- Research proposal development
- Interdisciplinary exploration

### Education
- Classroom discussions
- Student assignments
- Workshop activities
- Design critiques
- Research seminars

### Practice
- Team meetings
- Project kickoffs
- Design reviews
- Process evaluation
- Strategic planning

## 🔧 Technical Features

### Question Generation
- 7 disciplines covered
- 1 unique question per discipline per run
- Questions logged in CSV format
- Run as often as needed

### Visual Component
- AI-generated architectural imagery
- Instagram story format
- Professional text overlay
- Sequential numbering
- Consistent branding

### Performance
- 5-10 minutes per complete run
- 7 images per run
- Theoretical maximum: 288 runs per day
- Up to 2,016 unique question-image pairs daily

## 🚀 Getting Started

```sh
git clone <repository-url>
cd ask
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- Together.ai API key (starts with `tgp_v1_`)
- Internet connection for API access

### Configuration
1. Copy template:
```sh
cp ask.env.template ask.env
```

2. Add API key to `ask.env`:
```
TOGETHER_API_KEY=your_api_key_here
```

### Run
```sh
python daily.py
```

### Output
- Questions saved to `log.csv`
- Images saved to `images/` directory
- Execution logs in `logs/execution.log`

## 📁 Project Structure

```
ask/
├── daily.py           # Main generator
├── ask.env           # Configuration
├── ask.env.template  # Config template
├── requirements.txt  # Dependencies
├── README.md        # Documentation
├── log.csv         # Question archive
├── images/         # Generated visuals
└── logs/          # System logs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

[---
Get today's updates here
---](https://patreon.com/c/kvshvl)

**Version:** 2.0  
**Updated:** August 2025
*Better questions lead to better research.*
