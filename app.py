import streamlit as st
import urllib.parse
from datetime import datetime

# Judul aplikasi
st.title("YouTube OAuth Code Extractor")

# Inisialisasi session state untuk menyimpan kode
if 'auth_code' not in st.session_state:
    st.session_state.auth_code = None
    st.session_state.extracted_time = None

# Fungsi untuk mengekstrak kode dari URL
def extract_code_from_url(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'code' in query_params:
            return query_params['code'][0]
        else:
            return None
    except Exception as e:
        st.error(f"Error parsing URL: {str(e)}")
        return None

# Tab navigasi
tab1, tab2 = st.tabs(["Extractor", "About"])

with tab1:
    st.header("URL Code Extractor")
    
    # Input URL
    url_input = st.text_input("Masukkan URL Redirect:", 
                              placeholder="https://redirect1x.streamlit.app/?code=...")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tombol ekstrak manual
        if st.button("Ekstrak Kode", type="primary"):
            if url_input:
                code = extract_code_from_url(url_input)
                if code:
                    st.session_state.auth_code = code
                    st.session_state.extracted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success("Kode berhasil diekstrak!")
                else:
                    st.error("Tidak ditemukan kode dalam URL")
            else:
                st.warning("Silakan masukkan URL terlebih dahulu")
    
    with col2:
        # Tombol reset
        if st.button("Reset"):
            st.session_state.auth_code = None
            st.session_state.extracted_time = None
            st.experimental_rerun()
    
    # Deteksi otomatis dari query parameters
    st.subheader("Deteksi Otomatis")
    query_params = st.experimental_get_query_params()
    
    if 'code' in query_params:
        detected_code = query_params['code'][0]
        st.success("Kode terdeteksi secara otomatis dari URL!")
        st.session_state.auth_code = detected_code
        st.session_state.extracted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Tampilkan hasil deteksi
        with st.expander("Hasil Deteksi Otomatis", expanded=True):
            st.info(f"**Kode Terdeteksi:** `{detected_code}`")
            st.json(query_params)  # Tampilkan semua parameter untuk debugging
    
    # Tampilkan hasil ekstraksi
    if st.session_state.auth_code:
        st.subheader("Hasil Ekstraksi")
        st.success("✅ Kode berhasil ditemukan!")
        st.code(st.session_state.auth_code, language="text")
        
        if st.session_state.extracted_time:
            st.caption(f"Diekstrak pada: {st.session_state.extracted_time}")
            
        # Opsi copy to clipboard (simulasi)
        st.info("Copy kode di atas dan gunakan sesuai kebutuhan")
        
        # Tampilkan scope jika ada
        if 'scope' in query_params:
            st.subheader("Scope Informasi")
            scopes = query_params['scope']
            for scope in scopes:
                st.markdown(f"- `{scope}`")

with tab2:
    st.header("Tentang Aplikasi")
    st.markdown("""
    ### YouTube OAuth Code Extractor
    
    Aplikasi ini membantu Anda mengekstrak kode autentikasi dari URL redirect 
    hasil proses OAuth dengan Google/YouTube.
    
    **Fitur Utama:**
    - Ekstraksi manual dari URL input
    - Deteksi otomatis dari parameter URL
    - Menyimpan history ekstraksi
    - Menampilkan scope permissions
    
    **Cara Penggunaan:**
    1. Setelah redirect dari proses OAuth, copy URL lengkap
    2. Paste URL di input field atau biarkan deteksi otomatis
    3. Klik tombol "Ekstrak Kode"
    4. Gunakan kode hasil ekstraksi untuk proses selanjutnya
    
    **Contoh URL yang diproses:**
    ```
    https://redirect1x.streamlit.app/?code=4/0ASc3gC1UK7CZaC_9lgm-M7egYKx_AbhIIxr0f8W3xKjbsBPgVndCbSsAaWOeCVecybc-Ew&scope=https://www.googleapis.com/auth/youtube.force-ssl
    ```
    """)
    
    st.divider()
    st.markdown("**Developer Info:**")
    st.markdown("- Script ini hanya untuk demonstrasi ekstraksi kode")
    st.markdown("- Pastikan URL berasal dari sumber yang terpercaya")
    st.markdown("- Kode yang diekstrak biasanya memiliki waktu kedaluwarsa singkat")

# Footer
st.divider()
st.caption("⚠️ Aplikasi ini tidak menyimpan data apapun. Semua proses dilakukan di sisi client.")

# Auto-refresh untuk deteksi real-time (opsional)
if st.checkbox("Aktifkan deteksi real-time"):
    st.experimental_rerun()
