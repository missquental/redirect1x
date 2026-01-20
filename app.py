# File: redirect_app.py (untuk redirect1x.streamlit.app)
import streamlit as st
import requests
import json
import urllib.parse

# Konfigurasi OAuth
CLIENT_ID = "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://redirect1x.streamlit.app"

st.set_page_config(page_title="YouTube Auth Redirect", layout="centered")
st.title("🔑 YouTube Auth Handler")

# Dapatkan parameter dari URL
query_params = st.query_params

if 'code' in query_params:
    auth_code = query_params['code']
    state = query_params.get('state', [''])[0] if 'state' in query_params else ''
    
    # Decode state untuk mendapatkan URL aplikasi tujuan
    target_app = ''
    if state:
        try:
            decoded_state = urllib.parse.unquote(state)
            if decoded_state.startswith('http'):
                target_app = decoded_state
            elif '.' in decoded_state and 'streamlit.app' in decoded_state:
                target_app = f"https://{decoded_state}"
        except Exception as e:
            st.error(f"Error decoding state: {e}")
    
    if not target_app:
        st.error("❌ Tidak dapat menemukan aplikasi tujuan")
        st.stop()
    
    st.info(f"🎯 Mengirim token ke: {target_app}")
    
    try:
        # Exchange code for tokens
        token_data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
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
            
            # Auto redirect dengan meta refresh (lebih reliable)
            st.markdown(f"""
                <meta http-equiv="refresh" content="2;url={redirect_url}">
                <p>Jika tidak otomatis redirect dalam 2 detik, 
                <a href="{redirect_url}">klik di sini</a></p>
            """, unsafe_allow_html=True)
            
            # Backup dengan JavaScript
            st.components.v1.html(f"""
                <script>
                    console.log("Redirecting to: {redirect_url}");
                    // Meta refresh backup
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
    st.warning("❌ Tidak ada kode autentikasi ditemukan")
    if query_params:
        st.write("Parameters:", dict(query_params))
