# File: redirect_app.py (untuk aplikasi redirect seperti livenews1x.streamlit.app)
import streamlit as st
import requests
import json
import urllib.parse

st.set_page_config(page_title="Auth Redirect Handler", layout="centered")

# Konfigurasi OAuth - HARUS SESUAI DENGAN GOOGLE CLOUD CONSOLE
CLIENT_ID = "1086578184958-hin4d45sit9ma5psovppiq543eho41sl.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://redirect1x.streamlit.app"  # URI redirect ini

st.title("🔑 OAuth Redirect Handler")

# Dapatkan parameter dari URL
query_params = st.query_params

# Coba dapatkan referer dari parameter URL
referer = query_params.get('referer', [''])[0] if isinstance(query_params.get('referer', []), list) else query_params.get('referer', '')

# Jika tidak ada referer, gunakan header referer (terbatas di Streamlit)
# Karena Streamlit tidak selalu memberikan header referer, kita gunakan metode lain

# Metode alternatif: minta pengguna memasukkan URL tujuan jika tidak ditemukan
if not referer and 'target_app' in st.session_state:
    referer = st.session_state['target_app']

# Jika masih tidak ada, tampilkan form untuk input manual (sekali saja)
if not referer:
    st.warning("📝 Tidak dapat mendeteksi aplikasi tujuan secara otomatis")
    st.info("Silakan masukkan URL aplikasi utama Anda di bawah:")
    
    with st.form("target_form"):
        target_url = st.text_input("URL Aplikasi Utama", placeholder="https://namaserver.streamlit.app")
        submit = st.form_submit_button("Simpan dan Proses")
        
        if submit and target_url:
            st.session_state['target_app'] = target_url
            referer = target_url
            st.rerun()

if referer:
    st.success(f"🎯 Aplikasi tujuan: {referer}")
    
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
                redirect_url = f"{referer}?tokens={encoded_tokens}"
                
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
                
                # Simpan untuk kunjungan berikutnya
                st.session_state['target_app'] = referer
                
            else:
                st.error(f"❌ Gagal menukar kode: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
    else:
        st.warning("❌ Tidak ada kode otorisasi ditemukan di URL")
        st.info("Silakan kembali ke aplikasi utama dan klik tombol otorisasi.")
        st.markdown(f"[🏠 Kembali ke Aplikasi Utama]({referer})")
else:
    st.info("Menunggu informasi aplikasi tujuan...")
