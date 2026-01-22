# File: redirect_handler.py (deploy ke redirect1x.streamlit.app)
import streamlit as st
import urllib.parse
from datetime import datetime

st.set_page_config(
    page_title="OAuth Redirect Handler",
    page_icon="🔄",
    layout="centered"
)

def detect_previous_page(query_params):
    """Detect previous page from various sources"""
    # Method 1: Check state parameter (from OAuth)
    if 'state' in query_params:
        try:
            decoded_state = urllib.parse.unquote_plus(query_params['state'])
            if '.streamlit.app' in decoded_state:
                return decoded_state.split('?')[0]  # Remove query parameters
        except:
            pass
    
    # Method 2: Check custom referer parameter
    if 'referer' in query_params:
        referer = query_params['referer']
        if isinstance(referer, str) and '.streamlit.app' in referer:
            return referer.split('?')[0]
    
    # Method 3: Check session state (if preserved)
    if 'oauth_referer' in st.session_state:
        referer = st.session_state['oauth_referer']
        if isinstance(referer, str) and '.streamlit.app' in referer:
            return referer
    
    # Method 4: Default fallback
    return 'https://serverliveupdate6.streamlit.app/'

def extract_oauth_code(query_params):
    """Extract OAuth code from URL parameters"""
    # Check common parameter names
    for param in ['code', 'auth_code']:
        if param in query_params:
            return query_params[param]
    return None

def build_redirect_url(previous_page, code):
    """Build redirect URL with code parameter"""
    if not code:
        return previous_page
    
    # Remove existing code parameters to avoid conflicts
    base_url = previous_page.split('?')[0]
    
    # Parse existing query parameters
    if '?' in previous_page:
        existing_params = urllib.parse.parse_qs(urllib.parse.urlparse(previous_page).query)
        # Remove code-related parameters
        for param in ['code', 'auth_code']:
            if param in existing_params:
                del existing_params[param]
        
        # Rebuild query string
        if existing_params:
            query_string = urllib.parse.urlencode(existing_params, doseq=True)
            base_url = f"{base_url}?{query_string}"
    
    # Add the new code parameter
    separator = '&' if '?' in base_url else '?'
    redirect_url = f"{base_url}{separator}auth_code={urllib.parse.quote(code)}"
    
    return redirect_url

def auto_redirect_with_code(code, previous_page):
    """Perform automatic redirect with code"""
    redirect_url = build_redirect_url(previous_page, code)
    
    # Perform redirect
    st.markdown(
        f"""
        <meta http-equiv="refresh" content="0;url={redirect_url}">
        <script>
            setTimeout(function() {{
                window.location.href = "{redirect_url}";
            }}, 100);
        </script>
        <p style="text-align: center; font-family: Arial, sans-serif;">
            🔁 Redirecting to your application...<br>
            If not redirected automatically, <a href="{redirect_url}">click here</a>
        </p>
        """, 
        unsafe_allow_html=True
    )
    
    return redirect_url

def main():
    st.title("🔄 OAuth Redirect Handler")
    
    # Get URL parameters
    query_params = st.query_params
    code = extract_oauth_code(query_params)
    
    if code:
        st.success("✅ OAuth code received successfully!")
        
        # Detect previous page
        previous_page = detect_previous_page(query_params)
        st.info(f"**Detected previous page:** `{previous_page}`")
        
        # Show code preview
        code_preview = code[:50] + "..." if len(code) > 50 else code
        st.info(f"**Code:** `{code_preview}`")
        
        # Build redirect URL
        redirect_url = build_redirect_url(previous_page, code)
        st.info(f"**Will redirect to:** `{redirect_url}`")
        
        # Auto redirect after short delay
        st.markdown(
            f"""
            <script>
                setTimeout(function() {{
                    window.location.href = "{redirect_url}";
                }}, 3000);
            </script>
            <p style="text-align: center; color: #666;">
                Auto-redirecting in 3 seconds...
            </p>
            """, 
            unsafe_allow_html=True
        )
        
        # Manual redirect option
        st.markdown("---")
        st.subheader(" Manual Redirect")
        st.markdown(f"[Click here to go back]({redirect_url})")
        
    else:
        # No code found
        st.warning("⚠️ No OAuth code found in URL parameters")
        
        # Show debug information
        st.subheader("🔍 Debug Information")
        if query_params:
            st.write("**URL Parameters:**")
            st.json(dict(query_params))
        else:
            st.write("No URL parameters detected")
        
        st.write("**Session State:**")
        if st.session_state:
            st.json(dict(st.session_state))
        else:
            st.write("No session state data")

if __name__ == "__main__":
    main()
