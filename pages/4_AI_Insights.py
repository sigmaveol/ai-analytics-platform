"""Page 4 — AI-generated insights via Claude."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from auth.authenticator import require_auth
from ai.insight_generator import generate_insights, generate_executive_summary, suggest_domain, suggest_charts
from viz.charts import render_from_config

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")
name, role = require_auth()

st.title("🤖 AI Insights")
st.markdown("Claude AI phân tích dữ liệu và tạo ra insights kinh doanh tự động.")

df = st.session_state.get('df')
if df is None:
    st.warning("Chưa có dữ liệu.")
    if st.button("Upload ngay"): st.switch_page("pages/1_Upload.py")
    st.stop()

domain = st.session_state.get('domain', '')

# ── Domain detection ───────────────────────────────────────────────────────────
with st.expander("1. Domain / Lĩnh vực kinh doanh", expanded=True):
    if not domain:
        if st.button("AI tự nhận diện domain"):
            with st.spinner("Đang nhận diện..."):
                try:
                    domain = suggest_domain(df)
                    st.session_state.domain = domain
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi API: {e}")
    else:
        st.success(f"Domain: **{domain}**")

    domain = st.text_input("Hoặc nhập thủ công:", value=domain, key='domain_input')
    if domain != st.session_state.get('domain', ''):
        st.session_state.domain = domain

# ── Chart suggestions ──────────────────────────────────────────────────────────
with st.expander("2. AI Đề Xuất Biểu Đồ", expanded=False):
    if st.button("Generate chart suggestions"):
        with st.spinner("AI đang đề xuất biểu đồ phù hợp..."):
            try:
                suggestions = suggest_charts(df, domain)
                st.session_state.chart_suggestions = suggestions
            except Exception as e:
                st.error(f"Lỗi API: {e}")
                suggestions = []

    suggestions = st.session_state.get('chart_suggestions', [])
    if suggestions:
        st.markdown(f"AI đề xuất **{len(suggestions)} biểu đồ:**")
        cols = st.columns(2)
        for i, cfg in enumerate(suggestions):
            with cols[i % 2]:
                st.markdown(f"**{cfg.get('title', f'Chart {i+1}')}**")
                st.caption(cfg.get('rationale', ''))
                fig = render_from_config(df, cfg)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Không thể render: cột `{cfg.get('x_col')}` hoặc `{cfg.get('y_col')}` không tồn tại.")

# ── Business insights ──────────────────────────────────────────────────────────
st.subheader("3. Key Business Insights")
n_insights = st.slider("Số lượng insights", 3, 8, 5)

if st.button("Generate Insights", type="primary", use_container_width=True):
    with st.spinner("Claude đang phân tích dữ liệu..."):
        try:
            insights = generate_insights(df, domain, n_insights)
            st.session_state.insights = insights
        except Exception as e:
            st.error(f"Lỗi API: {e}")
            insights = []

insights = st.session_state.get('insights', [])
if insights:
    for i, ins in enumerate(insights, 1):
        with st.container():
            st.markdown(f"### {i}. {ins.get('title', '')}")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(ins.get('insight', ''))
            with col2:
                if ins.get('metric'):
                    st.info(f"**Số liệu:** {ins['metric']}")
                if ins.get('action'):
                    st.success(f"**Khuyến nghị:** {ins['action']}")
            st.divider()

# ── Executive summary ──────────────────────────────────────────────────────────
st.subheader("4. Executive Summary")
if st.button("Generate Executive Summary", use_container_width=True):
    if not insights:
        st.warning("Hãy generate insights trước.")
    else:
        with st.spinner("Đang tạo executive summary..."):
            try:
                summary = generate_executive_summary(df, domain, insights)
                st.session_state.exec_summary = summary
            except Exception as e:
                st.error(f"Lỗi API: {e}")

summary = st.session_state.get('exec_summary', '')
if summary:
    st.markdown(summary)
    if st.button("Xuất báo cáo →", use_container_width=True):
        st.switch_page("pages/5_Export.py")
