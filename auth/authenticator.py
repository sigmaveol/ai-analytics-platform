"""Simple auth — session state based, no external auth service required."""
import streamlit as st

# Default users: {username: {password_plain, name, role}}
_USERS = {
    'admin':   {'password': 'admin123',   'name': 'Admin',   'role': 'admin'},
    'analyst': {'password': 'analyst123', 'name': 'Analyst', 'role': 'analyst'},
    'viewer':  {'password': 'viewer123',  'name': 'Viewer',  'role': 'viewer'},
}


def _check(username: str, password: str) -> bool:
    user = _USERS.get(username)
    return user is not None and user['password'] == password


def login_form():
    """Render login form and return (success, username)."""
    with st.form("login_form"):
        st.markdown("### Đăng nhập")
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type='password')
        submitted = st.form_submit_button("Đăng nhập", use_container_width=True)

    if submitted:
        if _check(username, password):
            st.session_state['auth_username'] = username
            st.session_state['auth_name'] = _USERS[username]['name']
            st.session_state['auth_role'] = _USERS[username]['role']
            return True, username
        else:
            st.error("Tên đăng nhập hoặc mật khẩu không đúng.")
    return False, None


def get_role(username: str) -> str:
    return _USERS.get(username, {}).get('role', 'viewer')


def require_auth() -> tuple[str, str]:
    """Call from top of any page. Returns (display_name, role) or stops."""
    if st.session_state.get('auth_username'):
        name = st.session_state['auth_name']
        role = st.session_state['auth_role']

        with st.sidebar:
            st.markdown(f"**{name}** (`{role}`)")
            if st.button("Đăng xuất", key="_logout"):
                for k in ['auth_username', 'auth_name', 'auth_role']:
                    st.session_state.pop(k, None)
                st.rerun()

        return name, role

    # Not logged in — show centered form
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("## 📊 AI Analytics Platform")
        st.caption("Đăng nhập để truy cập dashboard")
        ok, username = login_form()
        if ok:
            st.rerun()
        st.caption("Demo: admin/admin123 · analyst/analyst123 · viewer/viewer123")
    st.stop()
