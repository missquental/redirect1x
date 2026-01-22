import streamlit as st
import urllib.parse
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="OAuth Redirect Handler",
    page_icon="🔄",
    layout="centered"
)

# Function to detect previous Streamlit page
def detect_previous_streamlit_page():
    """Detect previous Streamlit page from various sources"""
    
    # Method 1: Check session state for origin
    if 'oauth_origin' in st.session_state:
        origin = st.session_state['oauth_origin']
        if isinstance(origin, str) and '.streamlit.app' in origin:
            return origin.split('?')[0]  # Remove query parameters
    
    # Method 2: Check referer (if available through headers - limited in Streamlit)
    # Note: Streamlit doesn't expose HTTP referer directly
    
    # Method 3: Check for origin parameter in URL
    query_params = st.query_params
    if 'origin' in query_params:
        origin = query_params['origin']
        if isinstance(origin, str) and '.streamlit.app' in origin:
            return origin.split('?')[0]
    
    # Method 4: Default fallback
    return 'https://serverliveupdate6.streamlit.app/'

# Function to extract OAuth code from URL parameters
def extract_oauth_code():
    """Extract OAuth code from URL parameters"""
    query_params = st.query_params
    
    # Check common parameter names
    for param in ['code', 'auth_code', 'oauth_code']:
        if param in query_params:
            return query_params[param]
    
    return None

# Function to build redirect URL with code
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
        for param in ['code', 'auth_code', 'oauth_code']:
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

# Function to perform auto-redirect
def auto_redirect_with_code(code, previous_page=None):
    """Perform automatic redirect with code"""
    if not previous_page:
        previous_page = detect_previous_streamlit_page()
    
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

# Main processing function
def process_oauth_callback():
    """Main function to process OAuth callback"""
    query_params = st.query_params
    code = extract_oauth_code()
    
    # Display processing interface
    st.title("🔄 OAuth Redirect Handler")
    
    if code:
        st.success("✅ OAuth code received successfully!")
        
        # Show code preview (first 50 chars)
        code_preview = code[:50] + "..." if len(code) > 50 else code
        st.info(f"**Code:** `{code_preview}`")
        
        # Detect previous page
        previous_page = detect_previous_streamlit_page()
        st.info(f"**Detected previous page:** `{previous_page}`")
        
        # Build redirect URL
        redirect_url = build_redirect_url(previous_page, code)
        st.info(f"**Will redirect to:** `{redirect_url}`")
        
        # Auto redirect after short delay
        if st.button("⏭️ Redirect Now (Auto-redirect in 3 seconds)"):
            auto_redirect_with_code(code, previous_page)
        else:
            # Auto redirect after 3 seconds
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
        
        return True
    else:
        # No code found
        st.warning("⚠️ No OAuth code found in URL parameters")
        
        # Show URL parameters for debugging
        if query_params:
            st.subheader("🔍 URL Parameters Received:")
            st.json(dict(query_params))
        else:
            st.info("No URL parameters detected")
        
        # Debug information
        st.subheader("🔧 Debug Information")
        st.write("**Session State:**")
        if st.session_state:
            st.json(dict(st.session_state))
        else:
            st.write("No session state data")
            
        # Test interface
        st.subheader("🧪 Test Interface")
        test_code = st.text_input("Enter test code:")
        test_origin = st.text_input("Enter test origin URL:", "https://serverliveupdate6.streamlit.app/")
        
        if test_code and test_origin:
            if st.button("Test Redirect"):
                test_redirect_url = build_redirect_url(test_origin, test_code)
                st.success(f"Test redirect URL: `{test_redirect_url}`")
                st.markdown(f"[Test Link]({test_redirect_url})")
        
        return False

# Enhanced version with better detection
def enhanced_process_oauth_callback():
    """Enhanced version with better previous page detection"""
    query_params = st.query_params
    code = extract_oauth_code()
    
    st.title("🔄 OAuth Redirect Handler")
    st.markdown("---")
    
    # Always show what we received
    st.subheader("📥 Received Data")
    if query_params:
        st.json(dict(query_params))
    else:
        st.info("No URL parameters received")
    
    if code:
        st.success("✅ OAuth authorization code received!")
        
        # Try multiple methods to detect previous page
        detected_pages = []
        
        # Method 1: Session state origin
        if 'oauth_origin' in st.session_state:
            detected_pages.append(("Session State Origin", st.session_state['oauth_origin']))
        
        # Method 2: Origin parameter
        if 'origin' in query_params:
            detected_pages.append(("URL Origin Parameter", query_params['origin']))
        
        # Method 3: Referrer-like detection (if passed manually)
        if 'referrer' in query_params:
            detected_pages.append(("URL Referrer Parameter", query_params['referrer']))
        
        # Default fallback
        detected_pages.append(("Default Fallback", "https://serverliveupdate6.streamlit.app/"))
        
        st.subheader("📍 Detected Previous Pages")
        for method, page in detected_pages:
            st.write(f"**{method}:** `{page}`")
        
        # Use the best detected page
        previous_page = detected_pages[0][1]  # First detected (usually most reliable)
        
        # Validate it's a Streamlit app URL
        if '.streamlit.app' not in previous_page:
            previous_page = "https://serverliveupdate6.streamlit.app/"
        
        st.info(f"**Selected redirect target:** `{previous_page}`")
        
        # Show the code (truncated for security)
        st.subheader("🔐 Authorization Code")
        if len(code) > 100:
            st.text_area("Code (truncated):", code[:100] + "...", height=100, disabled=True)
            st.caption(f"*Code is {len(code)} characters long*")
        else:
            st.code(code, language="text")
        
        # Build and show redirect URL
        redirect_url = build_redirect_url(previous_page, code)
        st.subheader("🔗 Redirect Information")
        st.info(f"**Final redirect URL:** `{redirect_url}`")
        
        # Auto redirect options
        st.subheader("⚡ Redirect Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Auto Redirect Now", type="primary"):
                auto_redirect_with_code(code, previous_page)
        
        with col2:
            delay = st.slider("Auto-delay (seconds)", 1, 10, 3)
            if st.button(f"⏰ Auto Redirect in {delay}s"):
                st.markdown(
                    f"""
                    <script>
                        setTimeout(function() {{
                            window.location.href = "{redirect_url}";
                        }}, {delay * 1000});
                    </script>
                    <p style="text-align: center; color: #666;">
                        Redirecting in {delay} seconds...
                    </p>
                    """, 
                    unsafe_allow_html=True
                )
        
        # Manual link
        st.markdown("---")
        st.subheader("🖱️ Manual Redirect")
        st.markdown(f"[Click here to continue manually]({redirect_url})")
        
        return True
    else:
        st.warning("⚠️ No authorization code found")
        return False

# Main app execution
def main():
    # Process OAuth callback
    processed = enhanced_process_oauth_callback()
    
    # Additional debug tools
    st.markdown("---")
    st.subheader("🛠️ Debug Tools")
    
    with st.expander("Session State Inspector"):
        if st.session_state:
            st.json(dict(st.session_state))
        else:
            st.write("No session state data")
    
    with st.expander("URL Builder Tool"):
        st.write("Build custom redirect URLs:")
        base_url = st.text_input("Base URL:", "https://serverliveupdate6.streamlit.app/")
        code_param = st.text_input("Code parameter:", "")
        
        if base_url and code_param:
            custom_url = build_redirect_url(base_url, code_param)
            st.code(custom_url, language="text")
            st.markdown(f"[Test Link]({custom_url})")

if __name__ == "__main__":
    main()
