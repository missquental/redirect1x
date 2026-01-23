import streamlit as st
import urllib.parse
from datetime import datetime
import re

# Judul aplikasi
st.set_page_config(page_title="OAuth Code Extractor", page_icon="🔑")
st.title("🔑 YouTube OAuth Code Extractor")

# Inisialisasi session state
if 'processed_codes' not in st.session_state:
    st.session_state.processed_codes = set()

if 'extracted_codes' not in st.session_state:
    st.session_state.extracted_codes = []

# Fungsi untuk mengekstrak kode dari URL dengan format khusus
def extract_code_from_special_url(url):
    try:
        # Parse URL dasar
        parsed_url = urllib.parse.urlparse(url)
        query_string = parsed_url.query
        
        # Cek format khusus: ?https://*.streamlit.app/code=...
        if query_string.startswith('https://') and 'code=' in query_string:
            # Pisahkan bagian URL referer dan parameter sebenarnya
            parts = query_string.split('code=', 1)
            if len(parts) == 2:
                referer_part = parts[0]  # https://*.streamlit.app/
                params_part = 'code=' + parts[1]  # code=...&scope=...
                
                # Parse parameter sebenarnya
                params = urllib.parse.parse_qs(params_part)
                code = params.get('code', [''])[0] if 'code' in params else ''
                scope = params.get('scope', [''])[0] if 'scope' in params else ''
                
                return code, scope, referer_part.rstrip('/')
        
        # Format normal
        query_params = urllib.parse.parse_qs(query_string)
        code = query_params.get('code', [''])[0] if 'code' in query_params else ''
        scope = query_params.get('scope', [''])[0] if 'scope' in query_params else ''
        referer = query_params.get('referer', [''])[0] if 'referer' in query_params else ''
        
        return code, scope, referer
    except Exception as e:
        st.error(f"Error parsing URL: {str(e)}")
        return None, None, None

# Fungsi untuk menyimpan kode yang diekstrak
def save_extracted_code(code, scope="", source="", referer=""):
    extraction_data = {
        'code': code,
        'scope': scope,
        'source': source,
        'referer': referer,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.extracted_codes.append(extraction_data)
    if len(st.session_state.extracted_codes) > 50:  # Batasi penyimpanan
        st.session_state.extracted_codes = st.session_state.extracted_codes[-50:]

# Tab navigasi
tab1, tab2, tab3 = st.tabs(["Extractor", "History", "About"])

with tab1:
    st.header("Automatic URL Detection")
    
    # Deteksi otomatis dari query parameters saat ini
    current_params = dict(st.query_params)
    
    # Gabungkan semua parameter menjadi string query untuk analisis
    full_query_string = "&".join([f"{k}={v[0] if v else ''}" for k, v in current_params.items()])
    
    # Cek format khusus
    code, scope, referer = extract_code_from_special_url(f"?{full_query_string}")
    
    if code and code not in st.session_state.processed_codes:
        st.success("✅ Kode terdeteksi secara otomatis dari URL!")
        st.session_state.processed_codes.add(code)
        save_extracted_code(code, scope, "Auto Detected", referer)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.code(code, language="text")
        with col2:
            if scope:
                st.markdown(f"**Scope:** `{scope}`")
        
        if referer:
            st.info(f"🔗 Referer: `{referer}`")
        
        with st.expander("Detail Parameter URL", expanded=False):
            st.json(current_params)
    elif code in st.session_state.processed_codes:
        st.info("Kode ini sudah pernah diproses sebelumnya")
        
        # Tetap tampilkan kode yang sudah diproses
        col1, col2 = st.columns([3, 1])
        with col1:
            st.code(code, language="text")
        with col2:
            if scope:
                st.markdown(f"**Scope:** `{scope}`")
    else:
        st.info("🔍 Menunggu deteksi kode otomatis...")
        st.caption("Setelah redirect dari proses OAuth dengan format:")
        st.code("https://redirect1x.streamlit.app/?https://*.streamlit.app/code=...&scope=...")
        
        # Debug info
        if current_params:
            st.caption("Parameter saat ini:")
            st.json(current_params)
    
    st.divider()
    
    st.header("Manual URL Processing")
    
    # Input URL manual
    url_input = st.text_input("Masukkan URL Redirect:", 
                              placeholder="https://redirect1x.streamlit.app/?https://serverliveupdate9.streamlit.app/code=...",
                              help="Paste URL lengkap hasil redirect OAuth")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Ekstrak Kode", type="primary", use_container_width=True):
            if url_input:
                extracted_code, extracted_scope, extracted_referer = extract_code_from_special_url(url_input)
                if extracted_code:
                    if extracted_code not in st.session_state.processed_codes:
                        st.session_state.processed_codes.add(extracted_code)
                        save_extracted_code(extracted_code, extracted_scope, "Manual Input", extracted_referer)
                        st.success("✅ Kode berhasil diekstrak!")
                        st.code(extracted_code, language="text")
                        if extracted_scope:
                            st.markdown(f"**Scope:** `{extracted_scope}`")
                        if extracted_referer:
                            st.info(f"🔗 Referer: `{extracted_referer}`")
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
                if extraction['referer']:
                    st.markdown(f"**_REFERER:** `{extraction['referer']}`")
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
    
    **Format URL yang Didukung:**
    1. Format Normal: `?code=...&scope=...`
    2. Format Khusus: `?https://*.streamlit.app/code=...&scope=...`
    
    **Fitur Utama:**
    - ✅ Deteksi otomatis dari URL saat ini
    - 🔍 Ekstraksi manual dari URL input
    - 📋 Histori penyimpanan kode
    - 🔄 Reset dan refresh session
    - 🔗 Deteksi referer otomatis
    
    **Contoh URL yang diproses:**
    ```
    https://redirect1x.streamlit.app/?https://serverliveupdate9.streamlit.app/code=4/0ASc3gC1UK7CZaC_9lgm-M7egYKx_AbhIIxr0f8W3xKjbsBPgVndCbSsAaWOeCVecybc-Ew&scope=https://www.googleapis.com/auth/youtube.force-ssl
    ```
    
    **Cara Kerja Otomatis:**
    1. Setelah redirect dari proses OAuth Google, buka halaman ini
    2. Aplikasi akan secara otomatis mendeteksi parameter `code` di URL
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
