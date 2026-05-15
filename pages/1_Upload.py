"""Page 1 — Upload data."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from auth.authenticator import require_auth
from core.data_loader import load_file, load_sample

st.set_page_config(page_title="Upload Dữ Liệu", page_icon="📋", layout="wide")
name, role = require_auth()

st.title("📋 Upload Dữ Liệu")
st.markdown("Hỗ trợ **CSV, Excel (.xlsx), Parquet, JSON**. Tối đa 50 MB.")

tab1, tab2 = st.tabs(["Upload file", "Dataset mẫu"])

with tab1:
    uploaded = st.file_uploader("Chọn file dữ liệu", type=['csv', 'xlsx', 'xls', 'parquet', 'json'])
    domain_input = st.text_input("Domain / lĩnh vực (để AI hiểu đúng ngữ cảnh)", placeholder="VD: tuyển dụng IT, bán lẻ, tài chính...")

    if uploaded:
        try:
            with st.spinner("Đang đọc dữ liệu..."):
                df = load_file(uploaded)
            st.session_state.df = df
            st.session_state.dataset_name = uploaded.name
            st.session_state.domain = domain_input or ''
            st.session_state.insights = None
            st.session_state.chart_suggestions = None

            st.success(f"Đã tải: **{len(df):,} bản ghi** · **{len(df.columns)} cột**")
            st.dataframe(df.head(10), use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Phân tích tổng quan →", use_container_width=True):
                    st.switch_page("pages/2_Profile.py")
            with col2:
                if st.button("AI Insights →", use_container_width=True):
                    st.switch_page("pages/4_AI_Insights.py")

        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

with tab2:
    st.markdown("""
    #### Dataset mẫu có sẵn

    | Tên | Mô tả | Bản ghi |
    |---|---|---|
    | vn_jobs_sample.parquet | Tin tuyển dụng AI/Data Việt Nam 2026 | ~500 |
    """)

    if st.button("Tải VN Jobs Dataset", use_container_width=True):
        try:
            with st.spinner("Đang tải..."):
                df = load_sample('vn_jobs_sample.parquet')
            st.session_state.df = df
            st.session_state.dataset_name = 'vn_jobs_sample.parquet'
            st.session_state.domain = 'Thị trường tuyển dụng AI/Data tại Việt Nam'
            st.session_state.insights = None
            st.session_state.chart_suggestions = None
            st.success(f"Đã tải: {len(df):,} bản ghi · {len(df.columns)} cột")
            st.dataframe(df.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Không tìm thấy dataset mẫu: {e}")
