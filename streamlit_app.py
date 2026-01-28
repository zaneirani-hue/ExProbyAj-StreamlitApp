import streamlit as st
import sqlite3
import requests
from datetime import datetime, timedelta
import pandas as pd
from PIL import Image
from pyzbar.pyzbar import decode
import io

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
    .stButton>button:hover {
        background: linear-gradient(135deg, #F7B801, #FF6B35);
        box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4);
    }
    .expiry-critical {
        background-color: #e74c3c;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
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
        font-weight: 800;
    }
    .camera-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 2rem;
        border-radius: 20px;
        border: 2px dashed rgba(255, 107, 53, 0.5);
        text-align: center;
    }
    .success-box {
        background: rgba(46, 204, 113, 0.2);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2ecc71;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database setup
@st.cache_resource
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
conn = init_db()

# Decode barcode from image
def decode_barcode(image):
    """Decode barcode from PIL Image"""
    try:
        # Convert to PIL Image if needed
        if not isinstance(image, Image.Image):
            image = Image.open(io.BytesIO(image))
        
        # Decode barcodes
        decoded_objects = decode(image)
        
        if decoded_objects:
            # Return the first barcode found
            barcode_data = decoded_objects[0].data.decode('utf-8')
            barcode_type = decoded_objects[0].type
            return barcode_data, barcode_type
        else:
            return None, None
    except Exception as e:
        st.error(f"Error decoding barcode: {e}")
        return None, None

# Product lookup function
@st.cache_data(ttl=3600)
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
    df = pd.read_sql_query(
        "SELECT * FROM items ORDER BY scan_date DESC",
        conn
    )
    return df

# Get expiry notifications
def get_notifications():
    df = pd.read_sql_query(
        """SELECT id, name, brand, expiry_date 
           FROM items 
           WHERE expiry_date IS NOT NULL AND expiry_date != ''
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
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()

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
                <br>
                """, unsafe_allow_html=True)
        else:
            st.info("No items expiring soon! 🎉")
        
        st.markdown("---")
        st.markdown("### 📝 Example Barcodes")
        st.code("7622210449283", language=None)
        st.caption("Milka Chocolate")
        st.code("3017620422003", language=None)
        st.caption("Nutella")
        st.code("5449000000996", language=None)
        st.caption("Coca-Cola")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📸 Scan Item", "📦 Inventory", "ℹ️ About"])
    
    with tab1:
        st.header("Scan or Enter Barcode")
        
        # Create two columns for camera and manual entry
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Camera Scan")
            st.markdown('<div class="camera-box">', unsafe_allow_html=True)
            
            # Camera input
            camera_photo = st.camera_input("Take a picture of the barcode")
            
            if camera_photo:
                # Display the captured image
                image = Image.open(camera_photo)
                st.image(image, caption="Captured Image", use_container_width=True)
                
                # Decode barcode
                with st.spinner("🔍 Scanning barcode..."):
                    barcode_data, barcode_type = decode_barcode(image)
                    
                    if barcode_data:
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ <strong>Barcode detected!</strong><br>
                            Type: {barcode_type}<br>
                            Code: {barcode_data}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Automatically lookup product
                        with st.spinner("Looking up product..."):
                            product = lookup_product(barcode_data)
                            st.session_state.current_product = product
                            st.session_state.current_barcode = barcode_data
                            st.success("Product found!")
                    else:
                        st.error("❌ No barcode detected in image. Please try again with better lighting or angle.")
                        st.info("💡 **Tips:**\n- Ensure good lighting\n- Hold camera steady\n- Get close to the barcode\n- Make sure barcode is in focus")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("⌨️ Manual Entry")
            st.markdown("Or enter the barcode manually:")
            
            barcode_input = st.text_input(
                "Barcode Number",
                placeholder="e.g., 7622210449283",
                help="Enter the numbers under the barcode"
            )
            
            if st.button("🔎 Lookup Product", use_container_width=True, type="primary"):
                if barcode_input:
                    with st.spinner("Looking up product..."):
                        product = lookup_product(barcode_input)
                        st.session_state.current_product = product
                        st.session_state.current_barcode = barcode_input
                        st.success("Product found!")
                else:
                    st.warning("Please enter a barcode number")
            
            st.markdown("---")
            st.info("📱 **Camera not working?**\n\n"
                   "Use manual entry as a backup. "
                   "Camera scanning works best on:\n"
                   "- Mobile devices\n"
                   "- Chrome/Edge browsers\n"
                   "- HTTPS connections")
        
        # Display scanned product
        if 'current_product' in st.session_state and st.session_state.current_product:
            st.markdown("---")
            st.markdown("---")
            st.subheader("📦 Product Information")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if st.session_state.current_product.get('image_url'):
                    st.image(st.session_state.current_product['image_url'], width=250)
                else:
                    st.info("No image available")
            
            with col2:
                st.markdown(f"### {st.session_state.current_product['name']}")
                st.write(f"**Brand:** {st.session_state.current_product['brand']}")
                st.write(f"**Category:** {st.session_state.current_product['category']}")
                st.write(f"**Barcode:** {st.session_state.current_barcode}")
                
                st.markdown("---")
                
                # Expiry date input for food items
                expiry_date = None
                if st.session_state.current_product.get('is_food'):
                    st.warning("⚠️ This is a food item - expiry date required")
                    expiry_date = st.date_input(
                        "Expiry Date",
                        min_value=datetime.now().date(),
                        help="Set the expiration date for this food item"
                    )
                else:
                    if st.checkbox("Set expiry date (optional)"):
                        expiry_date = st.date_input(
                            "Expiry Date",
                            min_value=datetime.now().date()
                        )
                
                # Save button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("💾 Save to Inventory", use_container_width=True, type="primary", key="save_btn"):
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
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        items_df = get_items()
        
        if items_df.empty:
            st.info("📭 No items in inventory yet. Start scanning to add items!")
        else:
            st.write(f"**Total items:** {len(items_df)}")
            st.markdown("---")
            
            # Display items
            for idx, row in items_df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                    
                    with col1:
                        if row['image_url']:
                            st.image(row['image_url'], width=80)
                        else:
                            st.markdown("### 📦")
                    
                    with col2:
                        st.markdown(f"**{row['name']}**")
                        st.caption(f"{row['brand']} • {row['category']}")
                        st.caption(f"Scanned: {row['scan_date']}")
                    
                    with col3:
                        if row['expiry_date']:
                            try:
                                expiry = datetime.strptime(row['expiry_date'], '%Y-%m-%d').date()
                                days_until = (expiry - datetime.now().date()).days
                                
                                if days_until < 0:
                                    st.markdown("<div class='expiry-critical'>EXPIRED!</div>", unsafe_allow_html=True)
                                elif days_until <= 2:
                                    st.markdown(f"<div class='expiry-critical'>Expires in {days_until} days!</div>", unsafe_allow_html=True)
                                elif days_until <= 7:
                                    st.markdown(f"<div class='expiry-warning'>Expires in {days_until} days</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='expiry-safe'>Expires: {row['expiry_date']}</div>", unsafe_allow_html=True)
                            except:
                                st.write(f"Expires: {row['expiry_date']}")
                        else:
                            st.caption("No expiry date")
                    
                    with col4:
                        if st.button("🗑️", key=f"delete_{row['id']}", help="Delete item"):
                            delete_item(row['id'])
                            st.rerun()
                    
                    st.markdown("---")
    
    with tab3:
        st.header("About ScanShelf")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Features
            - **📷 Camera Scanning**: Take photos of barcodes
            - **⌨️ Manual Entry**: Backup input method
            - **🔍 Auto Lookup**: 2M+ products database
            - **⏰ Expiry Tracking**: 7-day advance warnings
            - **📊 Smart Dashboard**: Visual alerts & stats
            
            ### 📱 How to Use
            1. Click "Take a picture" button
            2. Point camera at barcode
            3. App auto-detects and looks up product
            4. Set expiry date (required for food)
            5. Save to inventory
            6. Monitor alerts in sidebar
            """)
        
        with col2:
            st.markdown("""
            ### 🚀 Camera Tips
            - ✅ Use good lighting
            - ✅ Hold camera steady
            - ✅ Get close to barcode
            - ✅ Ensure barcode is in focus
            - ✅ Try different angles if needed
            
            ### 📊 Alert System
            - 🔴 **Critical**: 0-2 days (urgent!)
            - 🟡 **Warning**: 3-7 days
            - 🟢 **Safe**: 7+ days
            
            ### 📊 Data Source
            Product info from **Open Food Facts**
            - Free, open database
            - 2+ million products
            - Community maintained
            """)
        
        st.markdown("---")
        st.info("💡 **Note:** Camera requires HTTPS and browser permissions. Works best on mobile devices and modern browsers (Chrome, Edge, Safari).")
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #666;'>Made with ❤️ using Streamlit</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
