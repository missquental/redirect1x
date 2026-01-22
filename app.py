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
STREAMLIT_PATTERN = r'https?://[^\s/$.?#].[^\s]*\.streamlit\.app(?:/[^\s]*)?'

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

# Fungsi untuk mendeteksi aplikasi utama
def detect_main_app():
    # Coba dari parameter state dulu (jika ada)
    state = get_param_value(query_params, 'state')
    if state:
        try:
            # Decode state yang mungkin di-encode
            decoded_state = urllib.parse.unquote(state)
            # Cek apakah state mengandung URL streamlit yang valid
            if re.match(STREAMLIT_PATTERN, decoded_state):
                # Pastikan URL memiliki protokol
                if decoded_state.startswith(('http://', 'https://')):
                    return decoded_state
                else:
                    return f"https://{decoded_state}"
        except Exception as e:
            pass
    
    # Coba dari parameter referer
    referer = get_param_value(query_params, 'referer')
    if referer:
        try:
            decoded_referer = urllib.parse.unquote(referer)
            if re.match(STREAMLIT_PATTERN, decoded_referer):
                if decoded_referer.startswith(('http://', 'https://')):
                    return decoded_referer
                else:
                    return f"https://{decoded_referer}"
        except:
            pass
    
    # Coba dari parameter redirect_uri (jika merupakan URL streamlit)
    redirect_uri = get_param_value(query_params, 'redirect_uri')
    if redirect_uri:
        try:
            if re.match(STREAMLIT_PATTERN, redirect_uri):
                if redirect_uri.startswith(('http://', 'https://')):
                    return redirect_uri
                else:
                    return f"https://{redirect_uri}"
        except:
            pass
    
    # Fallback ke default yang umum
    common_apps = [
        "https://serverliveupdate10.streamlit.app/",
        "https://serverliveupdate12.streamlit.app/",
        "https://mainapp.streamlit.app/",
        "https://youtube-streamer.streamlit.app/"
    ]
    
    # Cek apakah salah satu common apps bisa diakses
    for app in common_apps:
        try:
            # Kita tidak benar-benar mengecek koneksi, hanya mengembalikan yang pertama
            return app
        except:
            continue
    
    # Jika semua cara gagal, gunakan default
    return "https://serverliveupdate12.streamlit.app/"

# Debug information
st.subheader("Debug - Raw Query Params:")
st.json(query_params)

code = get_param_value(query_params, 'code')
state = get_param_value(query_params, 'state')

st.write(f"Debug - Code: {code}")
st.write(f"Debug - State: {state}")

# Deteksi aplikasi tujuan
target_app = detect_main_app()
st.write(f"Debug - Target app: {target_app}")

if code:
    try:
        # Buat URL redirect dengan code sebagai parameter
        redirect_url = f"{target_app}?code={code}"
        
        st.success("✅ Authentication successful!")
        st.info(f"🎯 Sending code to: {target_app}")
        
        # Redirect otomatis dalam 2 detik
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <p>🔄 Redirecting automatically in 2 seconds...</p>
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
                    🔄 Go Back to App Now
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
