# File: redirect_app_advanced.py (versi lebih cerdas)
import streamlit as st
import requests
import json
import urllib.parse
import re

st.set_page_config(page_title="Redirect Handler", layout="centered")

# Konfigurasi OAuth
CLIENT_ID = "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://livenews1x.streamlit.app"

st.title("🔑 Proses Autentikasi YouTube")

# Fungsi untuk mendeteksi aplikasi tujuan secara otomatis
def detect_target_app(current_domain):
    """Deteksi aplikasi tujuan berdasarkan pola nama domain"""
    if "livenews1x" in current_domain:
        return current_domain.replace("livenews1x", "livenews2x")
    elif "redirect" in current_domain:
        return current_domain.replace("redirect", "main")
    elif "auth" in current_domain:
        return current_domain.replace("auth", "app")
    else:
        # Pattern matching untuk kasus umum
        patterns = [
            (r'(\w+)1x(\.streamlit\.app)', lambda m: f"{m.group(1)}2x{m.group(2)}"),
            (r'(\w+)redirect(\.streamlit\.app)', lambda m: f"{m.group(1)}main{m.group(2)}"),
            (r'(.*?)-auth(\.streamlit\.app)', lambda m: f"{m.group(1)}-app{m.group(2)}")
        ]
        
        for pattern, replacement in patterns:
            match = re.search(pattern, current_domain)
            if match:
                return re.sub(pattern, replacement, current_domain)
        
        # Fallback default
        return "https://livenews2x.streamlit.app"

# Dapatkan parameter dari URL
query_params = st.query_params

# Deteksi aplikasi tujuan
current_domain = "livenews1x.streamlit.app"  # Domain saat ini
TARGET_APP = f"https://{detect_target_app(current_domain)}"

st.write(f"Aplikasi tujuan terdeteksi: {TARGET_APP}")

if 'code' in query_params:
    auth_code = query_params['code']
    st.info("🔄 Memproses kode otorisasi...")
    
    # Exchange code for tokens
    try:
        token_data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }
        
        response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        
        if response.status_code == 200:
            tokens = response.json()
            
            # Encode tokens untuk dikirim ke aplikasi utama
            tokens_json = json.dumps(tokens)
            encoded_tokens = urllib.parse.quote(tokens_json)
            
            # Redirect ke aplikasi utama dengan tokens
            redirect_url = f"{TARGET_APP}?tokens={encoded_tokens}"
            
            st.success("✅ Autentikasi berhasil! Mengarahkan kembali...")
            st.markdown(f"### [➡️ Klik di sini jika tidak otomatis redirect]({redirect_url})")
            
            # Auto redirect dengan JavaScript
            st.components.v1.html(f"""
                <script>
                    setTimeout(function() {{
                        window.location.href = "{redirect_url}";
                    }}, 3000);
                </script>
            """)
            
        else:
            st.error(f"❌ Gagal menukar kode: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        
else:
    st.warning("❌ Tidak ada kode otorisasi ditemukan di URL")
    st.info("Silakan kembali ke aplikasi utama dan klik tombol otorisasi.")
    st.markdown(f"[🏠 Kembali ke Aplikasi Utama]({TARGET_APP})")
