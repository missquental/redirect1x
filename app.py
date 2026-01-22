# File: redirect_app.py
import streamlit as st
import requests
import json
import urllib.parse
import time
import re

st.set_page_config(page_title="YouTube Auth Redirect", layout="centered")
st.title("🔑 YouTube Auth Handler")

# Konfigurasi OAuth
CLIENT_ID = "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://redirect1x.streamlit.app"

# Pola untuk mendeteksi aplikasi Streamlit
STREAMLIT_PATTERN = r'https?://.*\.streamlit\.app.*'

# Dapatkan parameter dari URL
query_params = dict(st.query_params)

# Fungsi untuk mengambil parameter dengan benar
def get_param_value(params, param_name):
    if param_name in params:
        value = params[param_name]
        if isinstance(value, list):
            return value[0] if value else ""
        return str(value)
    return ""

# Fungsi untuk mendeteksi aplikasi utama dari referrer atau parameter
def detect_main_app():
    # Coba dari parameter state dulu (jika ada)
    state = get_param_value(query_params, 'state')
    if state:
        try:
            decoded_state = urllib.parse.unquote(state)
            if re.match(STREAMLIT_PATTERN, decoded_state):
                return decoded_state if decoded_state.startswith(('http://', 'https://')) else f"https://{decoded_state}"
        except:
            pass
    
    # Jika tidak ada state yang valid, gunakan default
    return "https://serverliveupdate10.streamlit.app/"

code = get_param_value(query_params, 'code')
state = get_param_value(query_params, 'state')

if code:
    try:
        # Deteksi aplikasi utama secara otomatis
        target_app = detect_main_app()
        
        # Buat URL redirect dengan code sebagai parameter
        redirect_url = f"{target_app}?code={code}"
        
        st.success("✅ Authentication successful!")
        st.info(f"🎯 Redirecting to: {target_app}")
        
        # Redirect otomatis dalam 2 detik
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <p>Redirecting to main app in 2 seconds...</p>
                <meta http-equiv="refresh" content="2; url={redirect_url}">
                <a href="{redirect_url}" 
                   style="background-color: #4CAF50; 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 6px; 
                          font-weight: bold;
                          display: inline-block;
                          margin-top: 10px;">
                    🔄 Go to Main App Now
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        # Auto-redirect JavaScript fallback
        st.markdown(f"""
            <script>
                setTimeout(function(){{
                    window.location.href = "{redirect_url}";
                }}, 2000);
            </script>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)[:100]}...")
else:
    st.info("🔐 Waiting for OAuth callback...")
    if query_params:
        st.write("Received parameters:", {k: str(v)[:50] + "..." if len(str(v)) > 50 else v 
                                         for k, v in query_params.items()})
    
    # Tampilkan informasi debug
    st.subheader("🔍 Debug Info")
    detected_app = detect_main_app()
    st.write(f"Detected target app: {detected_app}")
