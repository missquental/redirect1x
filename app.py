# File: redirect_app.py
import streamlit as st
import requests
import json
import urllib.parse
import time

st.set_page_config(page_title="YouTube Auth Redirect", layout="centered")
st.title("🔑 YouTube Auth Handler")

# Konfigurasi OAuth
CLIENT_ID = "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://redirect1x.streamlit.app"

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

code = get_param_value(query_params, 'code')
state = get_param_value(query_params, 'state')

if code and state:
    try:
        # Decode state untuk mendapatkan URL aplikasi tujuan
        target_app = ''
        try:
            decoded_state = urllib.parse.unquote(state)
            if decoded_state.startswith(('https://', 'http://')) and '.streamlit.app' in decoded_state:
                target_app = decoded_state
            elif '.streamlit.app' in decoded_state and '://' not in decoded_state:
                target_app = f"https://{decoded_state}"
        except:
            pass
        
        if not target_app:
            st.error("❌ Invalid target URL")
            st.stop()
        
        # Exchange code for tokens
        token_data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }
        
        with st.spinner("🔄 Processing authentication..."):
            response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        
        if response.status_code == 200:
            tokens = response.json()
            
            # Encode tokens dan buat URL redirect
            tokens_json = json.dumps(tokens)
            encoded_tokens = urllib.parse.quote(tokens_json)
            redirect_url = f"{target_app}?tokens={encoded_tokens}"
            
            st.success("✅ Authentication successful!")
            st.info(f"🎯 Redirecting to: {target_app}")
            
            # Redirect otomatis dalam 3 detik
            st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <p>Redirecting in 3 seconds...</p>
                    <meta http-equiv="refresh" content="3; url={redirect_url}">
                    <a href="{redirect_url}" 
                       style="background-color: #4CAF50; 
                              color: white; 
                              padding: 12px 24px; 
                              text-decoration: none; 
                              border-radius: 6px; 
                              font-weight: bold;
                              display: inline-block;
                              margin-top: 10px;">
                        🔄 Go Now
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            # Auto-redirect JavaScript fallback
            st.markdown(f"""
                <script>
                    setTimeout(function(){{
                        window.location.href = "{redirect_url}";
                    }}, 3000);
                </script>
            """, unsafe_allow_html=True)
            
        else:
            st.error(f"❌ Token exchange failed: {response.status_code}")
            st.text(response.text[:200] + "...")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)[:100]}...")
elif code:
    st.error("❌ Missing target application information")
    st.write("Received code but no state parameter")
else:
    st.info("🔐 Waiting for OAuth callback...")
    if query_params:
        st.write("Received parameters:", {k: str(v)[:50] + "..." if len(str(v)) > 50 else v 
                                         for k, v in query_params.items()})
