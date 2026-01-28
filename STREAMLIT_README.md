# 🛒 ScanShelf - Streamlit Edition

A simplified barcode scanner and expiry tracker built with Streamlit for easy deployment.

## ✨ Features

- 🔍 **Manual Barcode Entry**: Look up products by entering barcode numbers
- 📦 **Product Information**: Automatic lookup from Open Food Facts (2M+ products)
- ⏰ **Expiry Tracking**: Set expiry dates with 7-day advance warnings
- 📊 **Smart Dashboard**: View all items and expiry alerts in one place
- 💾 **Simple Storage**: SQLite database for persistent storage

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r streamlit_requirements_simple.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### Deploy to Streamlit Cloud (FREE!)

1. **Push to GitHub** (must be public repo)
2. **Go to** https://share.streamlit.io/
3. **Connect** your GitHub account
4. **Deploy** your repository
5. **Done!** Your app is live in 2 minutes 🎉

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 📱 How to Use

### 1. Scan/Enter Barcode
- Enter a barcode number manually (e.g., `7622210449283`)
- Click "Lookup Product"

### 2. Review Product Info
- View product name, brand, category
- See product image if available

### 3. Set Expiry Date
- **Required** for food items
- Optional for other products

### 4. Save to Inventory
- Click "Save to Inventory"
- Item appears in your inventory tab

### 5. Monitor Expiry Alerts
- Check sidebar for expiring items
- Color-coded urgency:
  - 🔴 Critical (0-2 days)
  - 🟡 Warning (3-7 days)
  - 🟢 Safe (7+ days)

## 📂 Files

- `streamlit_app.py` - Main application
- `streamlit_requirements_simple.txt` - Minimal dependencies for cloud deployment
- `streamlit_requirements.txt` - Full dependencies with camera support
- `.streamlit/config.toml` - Streamlit configuration
- `DEPLOYMENT_GUIDE.md` - Complete deployment instructions

## 🌐 Free Deployment Options

### 1. Streamlit Community Cloud ⭐ Recommended
- **Free forever**
- **Unlimited apps**
- **Auto-deploy from GitHub**
- **URL**: https://share.streamlit.io

### 2. Hugging Face Spaces
- **16GB RAM** (vs 1GB on Streamlit Cloud)
- **Persistent storage**
- **URL**: https://huggingface.co/spaces

### 3. Railway.app
- **$5 free credits/month**
- **Custom domains**
- **URL**: https://railway.app

### 4. Render.com
- **Free web services**
- **Auto-deploy from GitHub**
- **URL**: https://render.com

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step instructions for each platform.

## 🎯 Example Barcodes to Try

Test the app with these real barcodes:

- `7622210449283` - Milka Chocolate
- `3017620422003` - Nutella
- `5449000000996` - Coca-Cola
- `8076809513838` - Ferrero Rocher
- `40000031161` - Kraft Mac & Cheese

## 🔧 Customization

### Change Alert Threshold
Edit the notification check in `streamlit_app.py`:
```python
if 0 <= days_until <= 7:  # Change 7 to your preferred days
```

### Modify Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B35"  # Change to your color
```

## ⚠️ Important Notes

### Database Storage
- **Local**: SQLite database persists between runs
- **Streamlit Cloud**: Database resets on app restart/redeploy
- **Solution**: Use external database (Supabase, MongoDB Atlas) for production

### Camera Scanning
- Camera scanning requires additional dependencies
- Not available on most cloud platforms due to security restrictions
- Manual entry works everywhere ✅

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r streamlit_requirements_simple.txt
```

### Database not persisting on Streamlit Cloud
- This is normal behavior - database resets on redeploy
- Use external database service for production
- Or accept it as demo/testing behavior

### App is slow
- Check your internet connection
- Open Food Facts API may be slow sometimes
- Consider adding caching

## 📚 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python + SQLite
- **API**: Open Food Facts (free, no key required)
- **Deployment**: Streamlit Community Cloud

## 🤝 Contributing

Feel free to fork and improve! Some ideas:
- Add camera scanning for mobile
- Integrate with other product databases
- Add shopping list generation
- Export inventory to CSV
- Multi-user support

## 📄 License

Open source - use freely for personal and commercial projects!

## 🎉 Credits

- **Product Data**: Open Food Facts (https://world.openfoodfacts.org)
- **Framework**: Streamlit (https://streamlit.io)

---

**Happy Scanning!** 📱🛒

*Made with ❤️ and Streamlit*
