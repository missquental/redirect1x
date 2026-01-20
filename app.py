# File: redirect_app.py (untuk redirect1x.streamlit.app)
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

# Cek apakah ada code dan state dari Google
if 'code' in query_params:
    auth_code = query_params['code']
    state = query_params.get('state', [''])[0] if 'state' in query_params else ''
    
    # Decode state untuk mendapatkan URL aplikasi tujuan
    target_app = ''
    if state:
        try:
            target_app = urllib.parse.unquote(state)
            # Validasi bahwa ini adalah URL Streamlit
            if not target_app.startswith('http'):
                target_app = f"https://{target_app}"
        except:
            target_app = ''
    
    # Jika tidak ada state yang valid, coba dari session
    if not target_app and 'last_target' in st.session_state:
        target_app = st.session_state['last_target']
    
    # Jika masih tidak ada, minta input manual
    if not target_app:
        st.warning("📝 Tidak dapat menemukan aplikasi tujuan")
        user_target = st.text_input("Masukkan URL aplikasi tujuan", 
                                  placeholder="https://serverliveupdate12.streamlit.app")
        if user_target:
            target_app = user_target if user_target.startswith('http') else f"https://{user_target}"
            st.session_state['last_target'] = target_app
    
    if target_app:
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
                
                # Simpan target app untuk kunjungan berikutnya
                st.session_state['last_target'] = target_app
                
                # Kirim tokens kembali ke aplikasi utama
                tokens_json = json.dumps(tokens)
                encoded_tokens = urllib.parse.quote(tokens_json)
                redirect_url = f"{target_app}?tokens={encoded_tokens}"
                
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
        st.error("❌ Tidak dapat menentukan aplikasi tujuan")
else:
    st.warning("❌ Tidak ada kode autentikasi. Silakan autentikasi dari aplikasi utama.")
    
    # Debug info
    st.write("Query Params diterima:", dict(query_params))
