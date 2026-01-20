# File: redirect_app_final.py (versi yang pasti bekerja)
import streamlit as st
import requests
import json
import urllib.parse

st.set_page_config(page_title="YouTube Auth Redirect", layout="centered")
st.title("🔑 YouTube Auth Handler")

# Konfigurasi OAuth
CLIENT_ID = "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://redirect1x.streamlit.app"

# Dapatkan parameter dari URL - PERBAIKAN UTAMA
query_params = dict(st.query_params)

# Debug: Tampilkan semua parameter
st.write("Debug - Raw Query Params:", query_params)

# Tangani parameter dengan benar (Streamlit bisa mengembalikan list)
def get_param_value(params, param_name):
    if param_name in params:
        value = params[param_name]
        if isinstance(value, list):
            return value[0] if value else ""
        return str(value)
    return ""

# Ambil parameter dengan benar
code = get_param_value(query_params, 'code')
state = get_param_value(query_params, 'state')

st.write("Debug - Code:", code)
st.write("Debug - State:", state)

if code:
    # Decode state untuk mendapatkan URL aplikasi tujuan
    target_app = ''
    if state:
        try:
            # Decode state (bisa URL-encoded)
            decoded_state = urllib.parse.unquote(state)
            st.write("Debug - Decoded state:", decoded_state)
            
            # Validasi URL target
            if decoded_state.startswith(('https://', 'http://')) and '.streamlit.app' in decoded_state:
                target_app = decoded_state
            elif '.streamlit.app' in decoded_state and '://' not in decoded_state:
                target_app = f"https://{decoded_state}"
                
        except Exception as e:
            st.error(f"Error decoding state: {e}")
    
    st.write("Debug - Target app:", target_app)
    
    if not target_app:
        st.error("❌ Tidak dapat menemukan aplikasi tujuan yang valid")
        # Fallback manual input
        manual_target = st.text_input("Masukkan URL target manual:", "https://serverliveupdate12.streamlit.app")
        if manual_target:
            target_app = manual_target if manual_target.startswith('http') else f"https://{manual_target}"
    
    if target_app:
        st.info(f"🎯 Mengirim token ke: {target_app}")
        
        try:
            # Exchange code for tokens
            token_data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': REDIRECT_URI
            }
            
            with st.spinner("🔄 Memproses autentikasi..."):
                response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
            
            if response.status_code == 200:
                tokens = response.json()
                
                # Encode tokens dan buat URL redirect
                tokens_json = json.dumps(tokens)
                encoded_tokens = urllib.parse.quote(tokens_json)
                redirect_url = f"{target_app}?tokens={encoded_tokens}"
                
                st.success("✅ Autentikasi berhasil!")
                st.info("🔄 Mengarahkan kembali secara otomatis...")
                
                # Auto redirect dengan meta refresh
                st.markdown(f"""
                    <meta http-equiv="refresh" content="2;url={redirect_url}">
                    <p>Jika tidak otomatis redirect dalam 2 detik, 
                    <a href="{redirect_url}">klik di sini</a></p>
                """, unsafe_allow_html=True)
                
                # Backup dengan JavaScript
                st.components.v1.html(f"""
                    <script>
                        console.log("Redirecting to: {redirect_url}");
                        setTimeout(function() {{
                            window.location.href = "{redirect_url}";
                        }}, 1000);
                    </script>
                """, height=0)
                
            else:
                st.error(f"❌ Token exchange failed: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"❌ Error processing tokens: {str(e)}")
    else:
        st.warning("📝 Masukkan URL target untuk melanjutkan")
else:
    st.warning("❌ Tidak ada kode autentikasi ditemukan")
    if query_params:
        st.write("Parameters diterima:", query_params)
