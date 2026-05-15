"""Page 5 — Export reports and charts."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from auth.authenticator import require_auth
from viz.export import to_csv_bytes, to_json_bytes, to_markdown_bytes, to_html_bytes
from ai.report_generator import executive_summary, slide_outline, full_report

st.set_page_config(page_title="Xuất Báo Cáo", page_icon="📥", layout="wide")
name, role = require_auth()

st.title("📥 Xuất Báo Cáo")

df       = st.session_state.get('df')
insights = st.session_state.get('insights', [])
summary  = st.session_state.get('exec_summary', '')
domain   = st.session_state.get('domain', '')
ds_name  = st.session_state.get('dataset_name', 'dataset')

if df is None:
    st.warning("Chưa có dữ liệu.")
    if st.button("Upload ngay"): st.switch_page("pages/1_Upload.py")
    st.stop()

st.markdown(f"**Dataset:** `{ds_name}` · **{len(df):,} bản ghi** · **{len(df.columns)} cột**")
st.divider()

# ── Quick exports ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📄 CSV")
    st.download_button(
        "Download CSV",
        data=to_csv_bytes(df),
        file_name=f"{ds_name.split('.')[0]}_export.csv",
        mime='text/csv',
        use_container_width=True,
    )

with col2:
    st.markdown("#### 📊 Insights JSON")
    if insights:
        st.download_button(
            "Download JSON",
            data=to_json_bytes(insights, domain, len(df)),
            file_name="insights.json",
            mime='application/json',
            use_container_width=True,
        )
    else:
        st.info("Cần tạo insights trước.")

with col3:
    st.markdown("#### 📝 Markdown")
    if insights or summary:
        st.download_button(
            "Download Markdown",
            data=to_markdown_bytes(domain, ds_name, len(df), insights, summary),
            file_name="report.md",
            mime='text/markdown',
            use_container_width=True,
        )
    else:
        st.info("Cần tạo insights trước.")

st.divider()

# ── HTML Report ───────────────────────────────────────────────────────────────
st.markdown("#### 🌐 HTML Report (đẹp, có thể share)")

if insights:
    if not summary:
        if st.button("Tạo Executive Summary trước", use_container_width=True):
            with st.spinner("Đang generate summary..."):
                try:
                    summary = executive_summary(df, domain, insights)
                    st.session_state.exec_summary = summary
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi API: {e}")
    else:
        st.download_button(
            "Download HTML Report",
            data=to_html_bytes(domain, ds_name, len(df), insights, summary),
            file_name="report.html",
            mime='text/html',
            use_container_width=True,
        )
        with st.expander("Preview HTML"):
            st.markdown(summary)
else:
    st.info("Cần tạo insights ở trang AI Insights trước.")

st.divider()

# ── Slide Outline ─────────────────────────────────────────────────────────────
st.markdown("#### 🎯 Slide Outline (PowerPoint)")

if insights:
    if st.button("Generate Slide Outline bằng AI", use_container_width=True):
        with st.spinner("AI đang tạo slide outline..."):
            try:
                outline = slide_outline(domain, insights, ds_name, len(df))
                st.session_state.slide_outline = outline
            except Exception as e:
                st.error(f"Lỗi API: {e}")

    outline = st.session_state.get('slide_outline', '')
    if outline:
        st.markdown(outline)
        st.download_button(
            "Download Slide Outline (.md)",
            data=outline.encode('utf-8'),
            file_name="slide_outline.md",
            mime='text/markdown',
            use_container_width=True,
        )
else:
    st.info("Cần tạo insights trước.")

st.divider()

# ── Full Report ───────────────────────────────────────────────────────────────
st.markdown("#### 📋 Full Report (tất cả trong một)")
if insights and summary:
    report_md = full_report(df, domain, insights, summary, ds_name)
    st.download_button(
        "Download Full Report (.md)",
        data=report_md.encode('utf-8'),
        file_name="full_report.md",
        mime='text/markdown',
        use_container_width=True,
    )
