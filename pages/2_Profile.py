"""Page 2 — Auto data profiling."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from auth.authenticator import require_auth
from core.profiler import profile, completeness_table
from core.preprocessor import auto_clean, outlier_summary
from viz.charts import histogram, bar, pie
import pandas as pd

st.set_page_config(page_title="Phân Tích Tổng Quan", page_icon="🔍", layout="wide")
name, role = require_auth()

st.title("🔍 Phân Tích Tổng Quan Dữ Liệu")

df = st.session_state.get('df')
if df is None:
    st.warning("Chưa có dữ liệu. Hãy upload trước.")
    if st.button("Upload ngay"): st.switch_page("pages/1_Upload.py")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
p = profile(df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Bản ghi", f"{p['n_rows']:,}")
col2.metric("Cột", p['n_cols'])
col3.metric("Độ đầy đủ", f"{p['completeness_pct']}%")
col4.metric("Bản ghi trùng", p['duplicates'])

st.divider()

# ── Completeness ──────────────────────────────────────────────────────────────
st.subheader("Độ đầy đủ theo cột")
ct = completeness_table(df)
st.dataframe(ct, use_container_width=True, hide_index=True)

# ── Column distributions ───────────────────────────────────────────────────────
st.subheader("Phân phối dữ liệu")

num_cols = df.select_dtypes(include='number').columns.tolist()
cat_cols = [c for c in df.columns if df[c].dtype == object and df[c].nunique() <= 30]

if num_cols:
    st.markdown("**Cột số — histogram**")
    selected_num = st.selectbox("Chọn cột số", num_cols)
    fig = histogram(df.dropna(subset=[selected_num]), selected_num, f"Phân phối: {selected_num}")
    st.plotly_chart(fig, use_container_width=True)

if cat_cols:
    st.markdown("**Cột phân loại — bar chart**")
    selected_cat = st.selectbox("Chọn cột phân loại", cat_cols)
    vc = df[selected_cat].value_counts().head(15).reset_index()
    vc.columns = [selected_cat, 'Số lượng']
    fig = bar(vc, selected_cat, 'Số lượng', f"Phân bổ: {selected_cat}", horizontal=True)
    st.plotly_chart(fig, use_container_width=True)

# ── Sample data ────────────────────────────────────────────────────────────────
# ── Outlier detection ─────────────────────────────────────────────────────────
st.subheader("Phát hiện Outliers")
out_df = outlier_summary(df)
if not out_df.empty:
    st.dataframe(out_df, use_container_width=True, hide_index=True)
else:
    st.success("Không phát hiện outlier đáng kể.")

# ── Auto-clean ────────────────────────────────────────────────────────────────
st.subheader("Tự động làm sạch dữ liệu")
if st.button("Chạy Auto-Clean Pipeline", use_container_width=True):
    with st.spinner("Đang làm sạch..."):
        df_clean, log = auto_clean(df)
    st.session_state.df = df_clean
    st.success(f"Hoàn thành! {len(df_clean):,} hàng · {len(df_clean.columns)} cột")
    for line in log:
        st.write(f"- {line}")

with st.expander("Xem dữ liệu mẫu (10 dòng đầu)"):
    st.dataframe(df.head(10), use_container_width=True)

if st.button("Tiếp theo: AI Insights →", use_container_width=True):
    st.switch_page("pages/4_AI_Insights.py")
