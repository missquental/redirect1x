import streamlit as st
import urllib.parse
from datetime import datetime
import json

# Judul aplikasi
st.set_page_config(page_title="OAuth Code Extractor", page_icon="🔑")
st.title("🔑 YouTube OAuth Code Extractor")

# Inisialisasi session state
if 'processed_codes' not in st.session_state:
    st.session_state.processed_codes = set()

if 'extracted_codes' not in st.session_state:
    st.session_state.extracted_codes = []

# Fungsi untuk mengekstrak kode dari URL
def extract_code_from_url(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'code' in query_params:
            return query_params['code'][0], query_params.get('scope', [''])[0]
        else:
            return None, None
    except Exception as e:
        st.error(f"Error parsing URL: {str(e)}")
        return None, None

# Fungsi untuk menyimpan kode yang diekstrak
def save_extracted_code(code, scope="", source=""):
    extraction_data = {
        'code': code,
        'scope': scope,
        'source': source,
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
    current_params = st.query_params
    
    if 'code' in current_params:
        detected_code = current_params['code']
        detected_scope = current_params.get('scope', [''])[0] if 'scope' in current_params else ""
        
        # Cek apakah kode sudah diproses
        if detected_code not in st.session_state.processed_codes:
            st.success("✅ Kode terdeteksi secara otomatis dari URL saat ini!")
            st.session_state.processed_codes.add(detected_code)
            save_extracted_code(detected_code, detected_scope, "Current URL")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(detected_code, language="text")
            with col2:
                st.markdown(f"**Scope:** `{detected_scope}`")
            
            with st.expander("Detail Parameter URL", expanded=False):
                st.json(dict(current_params))
        else:
            st.info("Kode ini sudah pernah diproses sebelumnya")
    else:
        st.info("🔍 Menunggu deteksi kode otomatis...")
        st.caption("Setelah redirect dari proses OAuth, kode akan terdeteksi secara otomatis")
    
    st.divider()
    
    st.header("Manual URL Processing")
    
    # Input URL manual
    url_input = st.text_input("Masukkan URL Redirect:", 
                              placeholder="https://redirect1x.streamlit.app/?code=...",
                              help="Paste URL lengkap hasil redirect OAuth")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Ekstrak Kode", type="primary", use_container_width=True):
            if url_input:
                code, scope = extract_code_from_url(url_input)
                if code:
                    if code not in st.session_state.processed_codes:
                        st.session_state.processed_codes.add(code)
                        save_extracted_code(code, scope, "Manual Input")
                        st.success("✅ Kode berhasil diekstrak!")
                        st.code(code, language="text")
                        if scope:
                            st.markdown(f"**Scope:** `{scope}`")
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
    
    # Deteksi referer/referrer (jika tersedia)
    st.divider()
    st.header("Referer Information")
    
    # Mencoba mendapatkan informasi referer
    referer_info = st.query_params.get('referer', [''])[0] if 'referer' in st.query_params else ""
    if referer_info:
        st.info(f"🔗 Referer: {referer_info}")
    else:
        st.caption("Informasi referer tidak tersedia")

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
    
    **Cara Penggunaan Otomatis:**
    1. Setelah redirect dari proses OAuth Google, buka halaman ini
    2. Aplikasi akan secara otomatis mendeteksi parameter `code` di URL
    3. Kode akan langsung ditampilkan dan disimpan di histori
    
    **Contoh URL yang diproses:**
    ```
    https://redirect1x.streamlit.app/?code=4/0ASc3gC1UK7CZaC_9lgm-M7egYKx_AbhIIxr0f8W3xKjbsBPgVndCbSsAaWOeCVecybc-Ew&scope=https://www.googleapis.com/auth/youtube.force-ssl
    ```
    
    **Catatan Penting:**
    - Kode yang diekstrak biasanya memiliki waktu kedaluwarsa singkat
    - Pastikan URL berasal dari sumber yang terpercaya
    - Aplikasi ini tidak menyimpan data apapun di server
    """)
    
    st.divider()
    st.markdown("**Technical Info:**")
    st.markdown("- Hostname saat ini: `" + st.request.headers.get('Host', 'Unknown') + "`")
    st.markdown("- Scheme: `" + st.request.headers.get('X-Forwarded-Proto', 'Unknown') + "`")
    
    # Tampilkan semua query parameters untuk debugging
    if st.query_params:
        st.subheader("Query Parameters Saat Ini:")
        st.json(dict(st.query_params))

# Footer
st.divider()
st.caption("⚠️ Aplikasi ini tidak menyimpan data apapun secara permanen. Semua proses dilakukan di sisi client.")

# Auto-refresh untuk deteksi real-time (opsional)
if st.checkbox("Aktifkan deteksi real-time (auto-refresh setiap 5 detik)"):
    import time
    time.sleep(5)
    st.experimental_rerun()
