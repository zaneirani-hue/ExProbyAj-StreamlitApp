# 🚀 Deployment Guide - ScanShelf Streamlit App

This guide covers **FREE** deployment options for your Streamlit barcode scanner app.

## 📋 Table of Contents
1. [Streamlit Community Cloud (Recommended)](#streamlit-community-cloud)
2. [GitHub Setup](#github-setup)
3. [Alternative Free Options](#alternative-free-options)
4. [Configuration Tips](#configuration-tips)

---

## 🎯 Streamlit Community Cloud (Recommended)

**Best Option**: Free, easy, and made specifically for Streamlit apps!

### Features
- ✅ **100% Free** forever
- ✅ Unlimited public apps
- ✅ Auto-deploys from GitHub
- ✅ Free SSL certificate
- ✅ 1GB RAM, 1 CPU core per app
- ✅ Sleeps after 7 days of inactivity (wakes instantly)

### Deployment Steps

#### 1. Prepare Your Repository
```bash
# Create a new directory for your project
mkdir scanshelf-streamlit
cd scanshelf-streamlit

# Copy these files
# - streamlit_app.py (rename to app.py if you prefer)
# - streamlit_requirements_simple.txt (rename to requirements.txt)
```

#### 2. Create GitHub Repository

**Option A: Using GitHub Web Interface**
1. Go to https://github.com/new
2. Repository name: `scanshelf-streamlit`
3. Make it **Public** (required for free Streamlit hosting)
4. Click "Create repository"

**Option B: Using Command Line**
```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: ScanShelf barcode scanner"

# Create on GitHub and push
gh repo create scanshelf-streamlit --public --source=. --remote=origin --push
```

#### 3. Deploy on Streamlit Cloud

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository**: `your-username/scanshelf-streamlit`
   - **Branch**: `main` (or `master`)
   - **Main file path**: `streamlit_app.py`
5. Click **"Deploy"**

**Your app will be live in 2-3 minutes!** 🎉

### Your App URL
```
https://your-username-scanshelf-streamlit-streamlit-app-xyz123.streamlit.app
```

---

## 📂 GitHub Setup

### File Structure
```
scanshelf-streamlit/
├── streamlit_app.py          # Main application
├── requirements.txt           # Dependencies
├── README.md                  # Documentation (optional)
└── .gitignore                # Git ignore file
```

### Create `.gitignore`
```bash
# Create .gitignore file
cat > .gitignore << EOF
*.db
*.sqlite
*.sqlite3
__pycache__/
*.py[cod]
.env
.venv/
venv/
*.log
.DS_Store
EOF
```

### Push to GitHub
```bash
# If not already initialized
git init

# Add files
git add .
git commit -m "ScanShelf: Streamlit barcode scanner app"

# Add remote and push
git remote add origin https://github.com/YOUR-USERNAME/scanshelf-streamlit.git
git branch -M main
git push -u origin main
```

---

## 🌐 Alternative Free Deployment Options

### 2. **Hugging Face Spaces**
- **URL**: https://huggingface.co/spaces
- **Free Tier**: Unlimited public spaces
- **RAM**: 16GB (much more than Streamlit Cloud!)
- **Persistent Storage**: Yes

**Steps:**
1. Create account at huggingface.co
2. Go to "Spaces" → "Create new Space"
3. Select "Streamlit" as SDK
4. Upload your files or connect GitHub
5. Done!

**Pros**: More resources, persistent storage
**Cons**: Slightly more complex setup

### 3. **Railway.app** (with limitations)
- **URL**: https://railway.app
- **Free Tier**: $5 credit/month (enough for small apps)
- **Auto-deploy**: From GitHub

**Steps:**
1. Sign up with GitHub
2. "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Streamlit
5. Deploy!

**Pros**: More control, databases included
**Cons**: Limited free credits

### 4. **Render.com**
- **URL**: https://render.com
- **Free Tier**: Free web services (sleeps after 15 min inactivity)
- **Auto-deploy**: From GitHub

**Steps:**
1. Create account
2. "New" → "Web Service"
3. Connect GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
5. Deploy!

**Pros**: Good for multiple apps
**Cons**: Slower cold starts

---

## ⚙️ Configuration Tips

### 1. Optimize requirements.txt

**For Streamlit Cloud** (use simplified version):
```txt
streamlit==1.31.0
requests==2.31.0
pandas==2.1.4
```

**Avoid** heavy packages if not needed:
- ❌ `opencv-python` (use `opencv-python-headless` if needed)
- ❌ `tensorflow`, `torch` (unless required)
- ❌ `pyzbar`, `streamlit-webrtc` (camera features won't work on cloud anyway)

### 2. Add Streamlit Config

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#1a1a2e"
secondaryBackgroundColor = "#2d2d44"
textColor = "#ffffff"

[server]
headless = true
enableCORS = false
port = 8501
```

### 3. Database Considerations

**Important**: On Streamlit Cloud, SQLite database resets on each deploy!

**Solutions:**
- Use Streamlit session state for temporary data
- Integrate with free database services:
  - **Supabase** (PostgreSQL)
  - **MongoDB Atlas** (NoSQL)
  - **Google Sheets** (simple option)

### 4. Environment Variables

For API keys or secrets, use Streamlit Secrets:

1. In Streamlit Cloud dashboard, go to app settings
2. Add secrets in "Secrets" section:
```toml
[secrets]
api_key = "your-api-key-here"
```

3. Access in code:
```python
import streamlit as st
api_key = st.secrets["api_key"]
```

---

## 🎯 Quick Start Commands

### Local Testing
```bash
# Install dependencies
pip install -r streamlit_requirements_simple.txt

# Run app
streamlit run streamlit_app.py
```

### Deploy to Streamlit Cloud
```bash
# 1. Initialize git (if not done)
git init

# 2. Add and commit
git add .
git commit -m "Initial commit"

# 3. Push to GitHub
git remote add origin https://github.com/YOUR-USERNAME/scanshelf-streamlit.git
git push -u origin main

# 4. Go to share.streamlit.io and deploy!
```

---

## 📊 Comparison Table

| Platform | Free Tier | Persistent Storage | Custom Domain | Auto-Deploy | Best For |
|----------|-----------|-------------------|---------------|-------------|----------|
| **Streamlit Cloud** | ✅ Unlimited | ❌ No | ✅ Yes (paid) | ✅ Yes | Streamlit apps |
| **Hugging Face** | ✅ Unlimited | ✅ Yes | ❌ No | ✅ Yes | ML/AI apps |
| **Railway** | ⚠️ $5/month | ✅ Yes | ✅ Yes | ✅ Yes | Full-stack apps |
| **Render** | ✅ Limited | ✅ Yes | ✅ Yes | ✅ Yes | Multiple apps |

---

## 🐛 Troubleshooting

### App Won't Deploy
- Check `requirements.txt` has exact versions
- Ensure `streamlit_app.py` is in root directory
- Check logs in deployment dashboard

### Database Issues
- SQLite resets on Streamlit Cloud restarts
- Use external database for persistence
- Or accept temporary storage for demo apps

### Import Errors
- Remove unused imports (pyzbar, opencv, webrtc)
- Use `streamlit_requirements_simple.txt`

### Slow Performance
- Optimize image processing
- Use caching: `@st.cache_data`
- Reduce API calls

---

## 🎉 You're Ready!

**Recommended Path for Beginners:**
1. ✅ Push code to GitHub (public repo)
2. ✅ Deploy on Streamlit Community Cloud
3. ✅ Share your app URL!

**Total time**: 10-15 minutes ⏱️

**Cost**: $0.00 💰

---

## 📚 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Deployment Guide**: https://docs.streamlit.io/streamlit-community-cloud
- **GitHub Guide**: https://docs.github.com/en/get-started
- **Streamlit Forum**: https://discuss.streamlit.io

---

**Need Help?** Check the Streamlit Community Forum or GitHub Issues!

Happy Deploying! 🚀
