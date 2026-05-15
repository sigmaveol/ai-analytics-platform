"""Dashboard builder — compose multiple charts into a structured layout."""
import streamlit as st
import pandas as pd
from viz.charts import render_from_config, bar, pie, histogram, line
from core.analytics import category_distribution, monthly_trend, detect_datetime_col
from core.data_loader import infer_column_roles


def auto_dashboard(df: pd.DataFrame, chart_configs: list[dict] | None = None):
    """Render an automatic dashboard. Uses AI chart configs if provided, else auto-generates."""
    roles = infer_column_roles(df)
    num_cols = [c for c, r in roles.items() if r == 'numeric']
    cat_cols = [c for c, r in roles.items() if r == 'categorical']
    date_col = detect_datetime_col(df)

    if chart_configs:
        _render_ai_charts(df, chart_configs)
    else:
        _render_auto_charts(df, num_cols, cat_cols, date_col)


def _render_ai_charts(df: pd.DataFrame, configs: list[dict]):
    """Render charts from AI-suggested configs in a 2-column grid."""
    cols_per_row = 2
    chunks = [configs[i:i+cols_per_row] for i in range(0, len(configs), cols_per_row)]
    for chunk in chunks:
        cols = st.columns(len(chunk))
        for col_el, cfg in zip(cols, chunk):
            with col_el:
                with st.container():
                    st.markdown(f"**{cfg.get('title', '')}**")
                    st.caption(cfg.get('rationale', ''))
                    fig = render_from_config(df, cfg)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Không thể render biểu đồ này — cột không tồn tại.")


def _render_auto_charts(df: pd.DataFrame, num_cols: list, cat_cols: list, date_col: str | None):
    """Auto-generate charts based on column types without AI."""
    if cat_cols:
        st.markdown("#### Phân bổ dữ liệu phân loại")
        c1, c2 = st.columns(2)
        with c1:
            col = cat_cols[0]
            vc = category_distribution(df, col)
            fig = bar(vc, col, 'Số lượng', f"Phân bổ: {col}", horizontal=True)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            col2 = cat_cols[min(1, len(cat_cols)-1)]
            vc2 = category_distribution(df, col2, top_n=8)
            fig2 = pie(vc2, col2, 'Số lượng', f"Tỷ trọng: {col2}")
            st.plotly_chart(fig2, use_container_width=True)

    if num_cols:
        st.markdown("#### Phân phối dữ liệu số")
        cols = st.columns(min(3, len(num_cols)))
        for el, nc in zip(cols, num_cols[:3]):
            with el:
                fig = histogram(df.dropna(subset=[nc]), nc, f"{nc}")
                st.plotly_chart(fig, use_container_width=True)

    if date_col:
        st.markdown("#### Xu hướng theo thời gian")
        trend_df = monthly_trend(df, date_col)
        y_col = list(trend_df.columns)[-1]
        fig = line(trend_df, 'Tháng', y_col, f"Xu hướng: {y_col}")
        st.plotly_chart(fig, use_container_width=True)


def kpi_row(metrics: list[dict]):
    """Render a row of KPI cards. Each metric: {label, value, delta, icon}."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            icon = m.get('icon', '')
            delta = m.get('delta')
            st.metric(
                label=f"{icon} {m['label']}",
                value=m['value'],
                delta=delta,
            )
