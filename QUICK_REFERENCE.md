# Quick Reference - Upgraded Simple Pipeline

## 🚀 Quick Commands

### **Basic Usage**
```bash
# Simple mode (default)
python simple_pipeline.py

# Hybrid mode
python simple_pipeline.py hybrid

# Cross-disciplinary mode
python simple_pipeline.py cross-disciplinary

# Chained mode
python simple_pipeline.py chained

# Get help
python simple_pipeline.py help
```

## ⚙️ Essential Configuration

### **Mode Settings** (in `ask.env`)
```bash
# Hybrid mode
HYBRID_THEME_COUNT=2                    # Number of themes
HYBRID_CHAIN_LENGTH=3                   # Questions per chain

# Cross-disciplinary mode
CROSS_DISCIPLINARY_THEME_COUNT=3        # Number of themes

# Chained mode
CHAIN_LENGTH=3                          # Questions per chain
CATEGORIES_TO_GENERATE=architectural_design,construction_technology
```

### **Enhanced Features** (in `ask.env`)
```bash
# Enable/disable features
SIMPLE_PIPELINE_GENERATE_COVERS=false   # Cover images
SIMPLE_PIPELINE_SHOW_STATISTICS=true    # Statistics
SIMPLE_PIPELINE_VOLUME_TRACKING=true    # Volume tracking
SIMPLE_PIPELINE_MARK_QUESTIONS_USED=true # Prevent duplicates
SIMPLE_PIPELINE_ANALYZE_DIRECTION=true  # Research analysis
SIMPLE_PIPELINE_CREATE_BACKUP=true      # Automatic backups
SIMPLE_PIPELINE_EXPORT_DATA=false       # Data export
```

## 🎯 Mode Comparison

| Mode | Command | Best For | Output |
|------|---------|----------|---------|
| **Simple** | `python simple_pipeline.py` | Quick Q&A pairs | 1 Q&A pair |
| **Hybrid** | `python simple_pipeline.py hybrid` | Educational content | 6 Q&A pairs (2 themes × 3 chains) |
| **Cross-Disciplinary** | `python simple_pipeline.py cross-disciplinary` | Innovative research | 3 Q&A pairs |
| **Chained** | `python simple_pipeline.py chained` | Deep exploration | 6 Q&A pairs (2 categories × 3 chains) |

## 📊 Expected Outputs

### **Simple Mode**: 1 Q&A pair
### **Hybrid Mode**: 6 Q&A pairs (2 themes × 3 questions each)
### **Cross-Disciplinary Mode**: 3 Q&A pairs (3 themes)
### **Chained Mode**: 6 Q&A pairs (2 categories × 3 questions each)

## 🎨 What You Get

### **All Modes Include**:
- ✅ Volume tracking and progress
- ✅ Comprehensive statistics
- ✅ Research direction analysis
- ✅ Automatic backups
- ✅ Optional cover images
- ✅ Data export capabilities
- ✅ Duplicate prevention
- ✅ Enhanced error handling

## 🔧 Troubleshooting

### **If a mode fails**:
1. Check your `ask.env` configuration
2. Ensure all required modules are available
3. Check the logs in `logs/execution.log`
4. Try simple mode first: `python simple_pipeline.py`

### **To disable features**:
```bash
# Disable statistics
SIMPLE_PIPELINE_SHOW_STATISTICS=false

# Disable backups
SIMPLE_PIPELINE_CREATE_BACKUP=false

# Disable analysis
SIMPLE_PIPELINE_ANALYZE_DIRECTION=false
```

## 🎯 Pro Tips

1. **Start Simple**: Use simple mode first to test your setup
2. **Gradual Progression**: Move to advanced modes as you need them
3. **Customize Themes**: Edit `ask.env` to change theme counts and chain lengths
4. **Enable Covers**: Set `SIMPLE_PIPELINE_GENERATE_COVERS=true` for professional output
5. **Export Data**: Set `SIMPLE_PIPELINE_EXPORT_DATA=true` to save your content
6. **Check Backups**: Look for `log.csv.backup_*` files for data safety

## 📁 Output Files

### **Images**: `images/` directory
### **Logs**: `logs/execution.log`
### **Data**: `log.csv`
### **Backups**: `log.csv.backup_*`
### **Exports**: `research_export_*.csv` (if enabled)

## 🚀 Advanced Usage

### **Custom Categories for Chained Mode**:
```bash
CATEGORIES_TO_GENERATE=urban_planning,digital_technology,interior_environments
```

### **Longer Chains**:
```bash
HYBRID_CHAIN_LENGTH=5
CHAIN_LENGTH=5
```

### **More Themes**:
```bash
HYBRID_THEME_COUNT=4
CROSS_DISCIPLINARY_THEME_COUNT=5
```

The upgraded Simple Pipeline gives you **all the power of the main pipeline** with **simple, unified commands**!
