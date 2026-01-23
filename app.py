import streamlit as st
import urllib.parse
from datetime import datetime

# Judul aplikasi
st.set_page_config(page_title="OAuth Code Extractor", page_icon="🔑")
st.title("🔑 YouTube OAuth Code Extractor")

# Inisialisasi session state
if 'processed_codes' not in st.session_state:
    st.session_state.processed_codes = set()

if 'extracted_codes' not in st.session_state:
    st.session_state.extracted_codes = []

# Fungsi untuk mengekstrak kode dan redirect_from dari URL
def extract_code_and_redirect_from_url(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        code = query_params.get('code', [''])[0] if 'code' in query_params else ''
        scope = query_params.get('scope', [''])[0] if 'scope' in query_params else ''
        redirect_from = query_params.get('redirect_from', [''])[0] if 'redirect_from' in query_params else ''
        return code, scope, redirect_from
    except Exception as e:
        st.error(f"Error parsing URL: {str(e)}")
        return None, None, None

# Fungsi untuk menyimpan kode yang diekstrak
def save_extracted_code(code, scope="", redirect_from="", source=""):
    extraction_data = {
        'code': code,
        'scope': scope,
        'redirect_from': redirect_from,
        'source': source,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.extracted_codes.append(extraction_data)
    if len(st.session_state.extracted_codes) > 50:
        st.session_state.extracted_codes = st.session_state.extracted_codes[-50:]

# Tab navigasi
tab1, tab2, tab3 = st.tabs(["Extractor", "History", "About"])

with tab1:
    st.header("Automatic URL Detection")
    
    # Deteksi otomatis dari query parameters saat ini
    query_params = st.query_params
    
    # Cek apakah ada parameter code
    if 'code' in query_params:
        detected_code = query_params['code']
        detected_scope = query_params.get('scope', [''])[0] if 'scope' in query_params else ""
        detected_redirect_from = query_params.get('redirect_from', [''])[0] if 'redirect_from' in query_params else ""
        
        # Cek apakah kode sudah diproses
        if detected_code not in st.session_state.processed_codes:
            st.success("✅ Kode terdeteksi secara otomatis dari URL!")
            st.session_state.processed_codes.add(detected_code)
            save_extracted_code(detected_code, detected_scope, detected_redirect_from, "Auto Detected")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(detected_code, language="text")
            with col2:
                if detected_scope:
                    st.markdown(f"**Scope:** `{detected_scope}`")
            
            if detected_redirect_from:
                st.info(f"🔗 Redirected from: `{detected_redirect_from}`")
            
            with st.expander("Detail Parameter URL", expanded=False):
                st.json(dict(query_params))
        else:
            st.info("Kode ini sudah pernah diproses sebelumnya")
            
            # Tetap tampilkan kode yang sudah diproses
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(detected_code, language="text")
            with col2:
                if detected_scope:
                    st.markdown(f"**Scope:** `{detected_scope}`")
            
            if detected_redirect_from:
                st.info(f"🔗 Redirected from: `{detected_redirect_from}`")
    else:
        st.info("🔍 Menunggu deteksi kode otomatis...")
        st.caption("Setelah redirect dari proses OAuth dengan format:")
        st.code("https://redirect1x.streamlit.app/?redirect_from=https://*.streamlit.app&code=...&scope=...")
        
        # Debug info
        if query_params:
            st.caption("Parameter saat ini:")
            st.json(dict(query_params))
    
    st.divider()
    
    st.header("Manual URL Processing")
    
    # Input URL manual
    url_input = st.text_input("Masukkan URL Redirect:", 
                              placeholder="https://redirect1x.streamlit.app/?redirect_from=https://*.streamlit.app&code=...",
                              help="Paste URL lengkap hasil redirect OAuth")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Ekstrak Kode", type="primary", use_container_width=True):
            if url_input:
                code, scope, redirect_from = extract_code_and_redirect_from_url(url_input)
                if code:
                    if code not in st.session_state.processed_codes:
                        st.session_state.processed_codes.add(code)
                        save_extracted_code(code, scope, redirect_from, "Manual Input")
                        st.success("✅ Kode berhasil diekstrak!")
                        st.code(code, language="text")
                        if scope:
                            st.markdown(f"**Scope:** `{scope}`")
                        if redirect_from:
                            st.info(f"🔗 Redirected from: `{redirect_from}`")
                    else:
                        st.warning("Kode ini sudah pernah diproses")
                else:
                    st.error("❌ Tidak ditemukan kode dalam URL")
            else:
                st.warning("Silakan masukkan URL terlebih dahulu")
    
    with col2:
        if st.button("Reset Session", use_container_width=True):
            st.session_state.processed_codes = set()
            st.session_state.extracted_codes = []
            st.query_params.clear()
            st.success("✅ Session telah direset")
            st.experimental_rerun()
    
    with col3:
        if st.button("Refresh Halaman", use_container_width=True):
            st.experimental_rerun()

with tab2:
    st.header("Histori Ekstraksi Kode")
    
    if st.session_state.extracted_codes:
        st.subheader(f"Total Kode Diekstrak: {len(st.session_state.extracted_codes)}")
        
        # Tampilkan kode terbaru dulu
        for i, extraction in enumerate(reversed(st.session_state.extracted_codes)):
            with st.expander(f"Kode #{len(st.session_state.extracted_codes)-i} - {extraction['timestamp']}", expanded=i==0):
                st.code(extraction['code'], language="text")
                if extraction['scope']:
                    st.markdown(f"**Scope:** `{extraction['scope']}`")
                if extraction['redirect_from']:
                    st.markdown(f"**Redirect From:** `{extraction['redirect_from']}`")
                st.caption(f"Sumber: {extraction['source']} | Waktu: {extraction['timestamp']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Copy Kode", key=f"copy_{i}"):
                        st.code(extraction['code'])
                        st.info("Kode telah ditampilkan di atas untuk copy")
                with col2:
                    if st.button("Hapus", key=f"delete_{i}"):
                        st.session_state.extracted_codes.pop(len(st.session_state.extracted_codes)-1-i)
                        st.success("Kode telah dihapus")
                        st.experimental_rerun()
    else:
        st.info("Belum ada kode yang diekstrak. Kode akan muncul di sini setelah proses ekstraksi.")

with tab3:
    st.header("Tentang Aplikasi")
    st.markdown("""
    ### YouTube OAuth Code Extractor
    
    Aplikasi ini secara otomatis mendeteksi dan mengekstrak kode autentikasi 
    dari URL redirect hasil proses OAuth dengan Google/YouTube.
    
    **Fitur Utama:**
    - ✅ Deteksi otomatis dari URL saat ini
    - 🔍 Ekstraksi manual dari URL input
    - 📋 Histori penyimpanan kode
    - 🔄 Reset dan refresh session
    - 🔗 Deteksi URL redirect otomatis
    
    **Format URL yang Didukung:**
    ```
    https://redirect1x.streamlit.app/?redirect_from=https://*.streamlit.app&code=...&scope=...
    ```
    
    **Contoh URL lengkap:**
    ```
    https://redirect1x.streamlit.app/?redirect_from=https://serverliveupdate9.streamlit.app&code=4/0ASc3gC1UK7CZaC_9lgm-M7egYKx_AbhIIxr0f8W3xKjbsBPgVndCbSsAaWOeCVecybc-Ew&scope=https://www.googleapis.com/auth/youtube.force-ssl
    ```
    
    **Cara Kerja Otomatis:**
    1. Setelah redirect dari proses OAuth Google dengan parameter `redirect_from`, buka halaman ini
    2. Aplikasi akan secara otomatis mendeteksi parameter `code`, `scope`, dan `redirect_from` di URL
    3. Kode akan langsung ditampilkan dan disimpan di histori
    """)
    
    st.divider()
    st.markdown("**Technical Info:**")
    
    # Tampilkan semua query parameters untuk debugging
    if st.query_params:
        st.subheader("Query Parameters Saat Ini:")
        st.json(dict(st.query_params))

# Footer
st.divider()
st.caption("⚠️ Aplikasi ini tidak menyimpan data apapun secara permanen. Semua proses dilakukan di sisi client.")

# Auto-refresh untuk deteksi real-time (opsional)
if st.checkbox("Aktifkan deteksi real-time (auto-refresh setiap 3 detik)"):
    import time
    time.sleep(3)
    st.experimental_rerun()
