"""Page 3 — Interactive analytics dashboard."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from auth.authenticator import require_auth
from core.analytics import numeric_summary, correlation_matrix, category_distribution, monthly_trend, detect_datetime_col
from viz.charts import bar, line, pie, scatter, heatmap, histogram, box

st.set_page_config(page_title="Dashboard Analytics", page_icon="📊", layout="wide")
name, role = require_auth()

st.title("📊 Dashboard Analytics")

df = st.session_state.get('df')
if df is None:
    st.warning("Chưa có dữ liệu.")
    if st.button("Upload ngay"): st.switch_page("pages/1_Upload.py")
    st.stop()

num_cols = df.select_dtypes(include='number').columns.tolist()
cat_cols = [c for c in df.columns if df[c].dtype == object and df[c].nunique() <= 50]
date_col = detect_datetime_col(df)

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Bộ lọc")
    filters = {}
    for col in cat_cols[:3]:
        opts = df[col].dropna().unique().tolist()
        selected = st.multiselect(col, opts, default=[], key=f'filter_{col}')
        if selected:
            filters[col] = selected

df_filtered = df.copy()
for col, vals in filters.items():
    df_filtered = df_filtered[df_filtered[col].isin(vals)]

st.caption(f"Đang hiển thị **{len(df_filtered):,}** / {len(df):,} bản ghi sau lọc")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📈 Tổng Quan", "💡 Phân Phối", "🔗 Tương Quan", "📅 Xu Hướng"])

with tabs[0]:
    st.subheader("Thống kê mô tả")
    summary = numeric_summary(df_filtered)
    if not summary.empty:
        st.dataframe(summary, use_container_width=True, hide_index=True)

    if cat_cols:
        col1, col2 = st.columns(2)
        with col1:
            cat1 = st.selectbox("Biểu đồ bar — cột phân loại", cat_cols, key='bar1')
            vc = category_distribution(df_filtered, cat1)
            fig = bar(vc, cat1, 'Số lượng', f"Phân bổ: {cat1}", horizontal=True)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            cat2 = st.selectbox("Biểu đồ pie — cột phân loại", cat_cols, key='pie1')
            vc2 = category_distribution(df_filtered, cat2, top_n=8)
            fig2 = pie(vc2, cat2, 'Số lượng', f"Tỷ trọng: {cat2}")
            st.plotly_chart(fig2, use_container_width=True)

with tabs[1]:
    st.subheader("Phân phối biến số")
    if num_cols:
        c1, c2 = st.columns(2)
        with c1:
            nc = st.selectbox("Histogram", num_cols, key='hist1')
            fig = histogram(df_filtered.dropna(subset=[nc]), nc, f"Phân phối: {nc}")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            if cat_cols and len(num_cols) >= 1:
                nc2 = st.selectbox("Box plot — giá trị", num_cols, key='box_y')
                cc = st.selectbox("Box plot — nhóm", cat_cols, key='box_x')
                try:
                    fig2 = box(df_filtered.dropna(subset=[nc2, cc]), cc, nc2, f"{nc2} theo {cc}")
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception:
                    st.info("Không đủ dữ liệu để vẽ box plot.")

        if len(num_cols) >= 2:
            st.subheader("Scatter plot")
            c3, c4 = st.columns(2)
            with c3: xc = st.selectbox("Trục X", num_cols, key='sc_x')
            with c4: yc = st.selectbox("Trục Y", num_cols, index=min(1,len(num_cols)-1), key='sc_y')
            cc2 = st.selectbox("Màu theo", [None] + cat_cols, key='sc_c')
            fig3 = scatter(df_filtered.dropna(subset=[xc, yc]), xc, yc, f"{xc} vs {yc}", cc2)
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Không có cột số.")

with tabs[2]:
    st.subheader("Ma trận tương quan")
    corr = correlation_matrix(df_filtered)
    if not corr.empty:
        fig = heatmap(corr, "Correlation Matrix")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Bảng số"):
            st.dataframe(corr, use_container_width=True)
    else:
        st.info("Cần ít nhất 2 cột số để tính tương quan.")

with tabs[3]:
    st.subheader("Xu hướng theo thời gian")
    if date_col:
        val_col = st.selectbox("Giá trị", [None] + num_cols, key='trend_val')
        trend_df = monthly_trend(df_filtered, date_col, val_col)
        y_col = list(trend_df.columns)[-1]
        fig = line(trend_df, 'Tháng', y_col, f"Xu hướng: {y_col}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không phát hiện cột ngày tháng. Hãy đảm bảo có cột datetime.")
