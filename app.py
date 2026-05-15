"""AI Analytics Platform — Main entry point."""
import streamlit as st

st.set_page_config(
    page_title="AI Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth ──────────────────────────────────────────────────────────────────────
from auth.authenticator import require_auth
name, role = require_auth()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### Xin chào, **{name}** 👋")
    st.caption(f"Vai trò: `{role}`")
    st.divider()
    st.markdown("""
**AI Analytics Platform**

Nhập dữ liệu → AI phân tích → Dashboard tự động

---
📋 [Upload Dữ Liệu](/Upload)
🔍 [Phân Tích Tổng Quan](/Profile)
📊 [Dashboard & Charts](/Analytics)
🤖 [AI Insights](/AI_Insights)
📥 [Xuất Báo Cáo](/Export)
""")
    st.divider()
    st.caption("Data Analysis & Visualization (505067)  \nHoàng Sinh Hưng · Trần Thiên Hưng")

# ── Home page ─────────────────────────────────────────────────────────────────
st.title("📊 AI Analytics Platform")
st.markdown("> Nhập dữ liệu → AI tự động phân tích → Dashboard interactive")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 1. Upload Dữ Liệu
    Hỗ trợ CSV, Excel, Parquet, JSON
    hoặc dùng dataset mẫu có sẵn.
    """)
    if st.button("Upload ngay →", key="btn_upload", use_container_width=True):
        st.switch_page("pages/1_Upload.py")

with col2:
    st.markdown("""
    #### 2. AI Phân Tích
    Claude AI tự động nhận diện domain,
    đề xuất charts và generate insights.
    """)
    if st.button("Xem insights →", key="btn_insights", use_container_width=True):
        st.switch_page("pages/4_AI_Insights.py")

with col3:
    st.markdown("""
    #### 3. Xuất Báo Cáo
    Download báo cáo HTML, executive
    summary, và outline slide.
    """)
    if st.button("Xuất báo cáo →", key="btn_export", use_container_width=True):
        st.switch_page("pages/5_Export.py")

st.divider()

# Quick start — check if data loaded
if 'df' in st.session_state and st.session_state.df is not None:
    df = st.session_state.df
    st.success(f"Dataset đã tải: **{len(df):,} bản ghi** · **{len(df.columns)} cột** · Nguồn: `{st.session_state.get('dataset_name', 'unknown')}`")
    if st.button("Đến Dashboard →", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")
else:
    st.info("Chưa có dữ liệu. Bắt đầu bằng cách **Upload dữ liệu** hoặc chọn dataset mẫu.")
    if st.button("Bắt đầu với dataset mẫu (VN Jobs 2026)", use_container_width=True):
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from core.data_loader import load_sample
        try:
            df = load_sample('vn_jobs_sample.parquet')
            st.session_state.df = df
            st.session_state.dataset_name = 'vn_jobs_sample.parquet'
            st.session_state.domain = 'Thị trường tuyển dụng AI/Data tại Việt Nam'
            st.rerun()
        except Exception as e:
            st.error(f"Không tìm thấy dataset mẫu: {e}")
