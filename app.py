# File: redirect_app_simple.py (versi paling sederhana)
import streamlit as st
import requests
import json
import urllib.parse

st.set_page_config(page_title="YouTube Auth Redirect", layout="centered")

# Konfigurasi OAuth
CLIENT_ID = "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://redirect1x.streamlit.app"

st.title("🔑 YouTube Auth Handler")

# Dapatkan parameter dari URL
query_params = st.query_params

# Cek apakah ada referer di parameter
referer = query_params.get('referer', [''])[0] if 'referer' in query_params else ''

# Jika tidak ada referer, cek dari state parameter (yang dikirim oleh Google)
state = query_params.get('state', [''])[0] if 'state' in query_params else ''
if state and not referer:
    try:
        # State bisa berisi referer yang diencode
        referer = urllib.parse.unquote(state)
    except:
        pass

# Jika masih tidak ada referer, gunakan dari session
if not referer and 'last_referer' in st.session_state:
    referer = st.session_state['last_referer']

if 'code' in query_params:
    auth_code = query_params['code']
    
    if not referer:
        st.error("❌ Tidak dapat menemukan aplikasi tujuan. Silakan autentikasi ulang dari aplikasi utama.")
        st.stop()
    
    st.info("🔄 Memproses autentikasi...")
    
    try:
        # Exchange code for tokens
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
            
            # Simpan referer untuk kunjungan berikutnya
            st.session_state['last_referer'] = referer
            
            # Kirim tokens kembali ke aplikasi utama
            tokens_json = json.dumps(tokens)
            encoded_tokens = urllib.parse.quote(tokens_json)
            redirect_url = f"{referer}?tokens={encoded_tokens}"
            
            st.success("✅ Sukses! Mengarahkan kembali...")
            st.markdown(f"[➡️ Klik jika tidak otomatis redirect]({redirect_url})")
            
            # Auto redirect
            st.components.v1.html(f"""
                <script>
                    setTimeout(function() {{
                        window.location.href = "{redirect_url}";
                    }}, 2000);
                </script>
            """)
        else:
            st.error(f"❌ Error: {response.text}")
    except Exception as e:
        st.error(f"❌ Exception: {str(e)}")
else:
    if referer:
        st.info(f"🔗 Dikirim dari: {referer}")
        st.markdown("[🏠 Kembali ke Aplikasi]({})".format(referer))
    else:
        st.warning("❌ Tidak ada kode autentikasi. Silakan autentikasi dari aplikasi utama.")
