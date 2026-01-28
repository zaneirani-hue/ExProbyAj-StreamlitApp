import streamlit as st
import sqlite3
import requests
from datetime import datetime, timedelta
import pandas as pd
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av
from pyzbar import pyzbar
import numpy as np

# Page configuration
st.set_page_config(
    page_title="ScanShelf - Barcode Scanner",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #1a1a2e;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35, #F7B801);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: 600;
    }
    .expiry-critical {
        background-color: #e74c3c;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: bold;
    }
    .expiry-warning {
        background-color: #f39c12;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: bold;
    }
    .expiry-safe {
        background-color: #2ecc71;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: bold;
    }
    h1 {
        color: #FF6B35;
        font-size: 3rem;
        text-align: center;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Database setup
def init_db():
    conn = sqlite3.connect('scanshelf.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  barcode TEXT NOT NULL,
                  name TEXT NOT NULL,
                  category TEXT,
                  brand TEXT,
                  image_url TEXT,
                  expiry_date TEXT,
                  scan_date TEXT)''')
    conn.commit()
    return conn

# Initialize database
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = init_db()

# Product lookup function
def lookup_product(barcode):
    """Look up product information from Open Food Facts API"""
    try:
        response = requests.get(
            f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1:
                product = data.get('product', {})
                return {
                    'name': product.get('product_name', 'Unknown Product'),
                    'brand': product.get('brands', 'Unknown Brand'),
                    'category': product.get('categories', 'General'),
                    'image_url': product.get('image_url', ''),
                    'is_food': 'food' in product.get('categories', '').lower() or 
                               'beverage' in product.get('categories', '').lower()
                }
    except Exception as e:
        st.error(f"API Error: {e}")
    
    return {
        'name': f'Product {barcode}',
        'brand': 'Unknown',
        'category': 'General Item',
        'image_url': '',
        'is_food': False
    }

# Save item to database
def save_item(barcode, name, category, brand, image_url, expiry_date):
    conn = st.session_state.db_conn
    c = conn.cursor()
    c.execute('''INSERT INTO items 
                 (barcode, name, category, brand, image_url, expiry_date, scan_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (barcode, name, category, brand, image_url, expiry_date,
               datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    return True

# Get all items
def get_items():
    conn = st.session_state.db_conn
    df = pd.read_sql_query(
        "SELECT * FROM items ORDER BY scan_date DESC",
        conn
    )
    return df

# Get expiry notifications
def get_notifications():
    conn = st.session_state.db_conn
    df = pd.read_sql_query(
        """SELECT id, name, brand, expiry_date 
           FROM items 
           WHERE expiry_date IS NOT NULL 
           ORDER BY expiry_date""",
        conn
    )
    
    if df.empty:
        return df
    
    today = datetime.now().date()
    notifications = []
    
    for _, row in df.iterrows():
        try:
            expiry = datetime.strptime(row['expiry_date'], '%Y-%m-%d').date()
            days_until = (expiry - today).days
            
            if 0 <= days_until <= 7:
                notifications.append({
                    'id': row['id'],
                    'name': row['name'],
                    'brand': row['brand'],
                    'expiry_date': row['expiry_date'],
                    'days_until': days_until,
                    'urgency': 'critical' if days_until <= 2 else 'warning'
                })
        except ValueError:
            continue
    
    return pd.DataFrame(notifications)

# Delete item
def delete_item(item_id):
    conn = st.session_state.db_conn
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()

# Barcode scanner class for camera
class BarcodeScanner(VideoTransformerBase):
    def __init__(self):
        self.barcode_data = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Decode barcodes
        barcodes = pyzbar.decode(img)
        
        for barcode in barcodes:
            self.barcode_data = barcode.data.decode('utf-8')
            
            # Draw rectangle around barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw barcode data
            text = f"{barcode.data.decode('utf-8')}"
            cv2.putText(img, text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return img

# Main app
def main():
    st.markdown("<h1>🛒 ScanShelf</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>Smart Barcode Scanner & Expiry Tracker</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Dashboard")
        
        # Stats
        items_df = get_items()
        notifications_df = get_notifications()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Items", len(items_df))
        with col2:
            st.metric("Expiring Soon", len(notifications_df))
        
        st.markdown("---")
        st.header("⚠️ Expiry Alerts")
        
        if not notifications_df.empty:
            for _, notif in notifications_df.iterrows():
                urgency_class = f"expiry-{notif['urgency']}"
                days_text = "TODAY!" if notif['days_until'] == 0 else \
                           "TOMORROW!" if notif['days_until'] == 1 else \
                           f"in {notif['days_until']} days"
                
                st.markdown(f"""
                <div class="{urgency_class}">
                    <strong>{notif['name']}</strong><br>
                    <small>{notif['brand']}</small><br>
                    Expires {days_text}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No items expiring soon! 🎉")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📸 Scan Item", "📦 Inventory", "ℹ️ About"])
    
    with tab1:
        st.header("Scan or Enter Barcode")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🔍 Manual Entry")
            barcode_input = st.text_input("Enter Barcode Number", placeholder="e.g., 7622210449283")
            
            if st.button("🔎 Lookup Product", use_container_width=True):
                if barcode_input:
                    with st.spinner("Looking up product..."):
                        product = lookup_product(barcode_input)
                        st.session_state.current_product = product
                        st.session_state.current_barcode = barcode_input
                        st.success("Product found!")
                        st.rerun()
        
        with col2:
            st.subheader("📷 Camera Scan")
            st.info("📱 Camera scanning works best in mobile browsers or with webcam")
            st.markdown("*Note: Install `streamlit-webrtc` and `pyzbar` for camera scanning*")
        
        # Display scanned product
        if 'current_product' in st.session_state and st.session_state.current_product:
            st.markdown("---")
            st.subheader("📦 Product Information")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if st.session_state.current_product.get('image_url'):
                    st.image(st.session_state.current_product['image_url'], width=200)
            
            with col2:
                st.markdown(f"### {st.session_state.current_product['name']}")
                st.write(f"**Brand:** {st.session_state.current_product['brand']}")
                st.write(f"**Category:** {st.session_state.current_product['category']}")
                st.write(f"**Barcode:** {st.session_state.current_barcode}")
                
                # Expiry date input for food items
                expiry_date = None
                if st.session_state.current_product.get('is_food'):
                    st.warning("⚠️ This is a food item - expiry date required")
                    expiry_date = st.date_input("Expiry Date", min_value=datetime.now().date())
                else:
                    if st.checkbox("Set expiry date (optional)"):
                        expiry_date = st.date_input("Expiry Date", min_value=datetime.now().date())
                
                # Save button
                if st.button("💾 Save to Inventory", use_container_width=True, type="primary"):
                    if st.session_state.current_product.get('is_food') and not expiry_date:
                        st.error("Please set an expiry date for food items!")
                    else:
                        expiry_str = expiry_date.strftime('%Y-%m-%d') if expiry_date else None
                        save_item(
                            st.session_state.current_barcode,
                            st.session_state.current_product['name'],
                            st.session_state.current_product['category'],
                            st.session_state.current_product['brand'],
                            st.session_state.current_product.get('image_url', ''),
                            expiry_str
                        )
                        st.success("✅ Item saved successfully!")
                        del st.session_state.current_product
                        del st.session_state.current_barcode
                        st.rerun()
    
    with tab2:
        st.header("Your Inventory")
        
        items_df = get_items()
        
        if items_df.empty:
            st.info("No items in inventory yet. Start scanning to add items!")
        else:
            # Add expiry status
            for idx, row in items_df.iterrows():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                
                with col1:
                    if row['image_url']:
                        st.image(row['image_url'], width=80)
                    else:
                        st.write("📦")
                
                with col2:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"{row['brand']} • {row['category']}")
                    st.caption(f"Scanned: {row['scan_date']}")
                
                with col3:
                    if row['expiry_date']:
                        try:
                            expiry = datetime.strptime(row['expiry_date'], '%Y-%m-%d').date()
                            days_until = (expiry - datetime.now().date()).days
                            
                            if days_until <= 2:
                                st.markdown(f"<div class='expiry-critical'>Expires in {days_until} days!</div>", unsafe_allow_html=True)
                            elif days_until <= 7:
                                st.markdown(f"<div class='expiry-warning'>Expires in {days_until} days</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='expiry-safe'>Expires: {row['expiry_date']}</div>", unsafe_allow_html=True)
                        except:
                            st.write(f"Expires: {row['expiry_date']}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_{row['id']}"):
                        delete_item(row['id'])
                        st.rerun()
                
                st.markdown("---")
    
    with tab3:
        st.header("About ScanShelf")
        
        st.markdown("""
        ### 🎯 Features
        - **Barcode Scanning**: Look up products using barcodes
        - **Product Information**: Get details from Open Food Facts database (2M+ products)
        - **Expiry Tracking**: Set expiry dates and get 7-day advance warnings
        - **Smart Notifications**: Color-coded alerts for expiring items
        - **Inventory Management**: Track all your scanned items
        
        ### 📱 How to Use
        1. Enter a barcode number manually or scan with camera
        2. Review product information
        3. Set expiry date for food items
        4. Save to inventory
        5. Check sidebar for expiry alerts
        
        ### 🚀 Technology
        - Built with **Streamlit**
        - Data from **Open Food Facts API**
        - Local **SQLite** database
        
        ### 📝 Tips
        - Set expiry dates for food items to get notifications
        - Check the sidebar regularly for expiring items
        - Delete items after consuming them
        
        ---
        
        Made with ❤️ using Streamlit
        """)

if __name__ == "__main__":
    main()
