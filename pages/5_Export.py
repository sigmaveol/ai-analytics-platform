"""Page 5 — Export reports and charts."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import io
import json
import streamlit as st
import pandas as pd
from auth.authenticator import require_auth

st.set_page_config(page_title="Xuất Báo Cáo", page_icon="📥", layout="wide")
name, role = require_auth()

st.title("📥 Xuất Báo Cáo")

df = st.session_state.get('df')
if df is None:
    st.warning("Chưa có dữ liệu.")
    if st.button("Upload ngay"): st.switch_page("pages/1_Upload.py")
    st.stop()

insights  = st.session_state.get('insights', [])
summary   = st.session_state.get('exec_summary', '')
domain    = st.session_state.get('domain', '')
ds_name   = st.session_state.get('dataset_name', 'dataset')

st.markdown(f"**Dataset:** `{ds_name}` · **{len(df):,} bản ghi** · **{len(df.columns)} cột**")
st.divider()

# ── Export CSV ─────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📄 Export CSV")
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False, encoding='utf-8-sig')
    st.download_button(
        "Download CSV",
        data=csv_buf.getvalue().encode('utf-8-sig'),
        file_name=f"{ds_name.split('.')[0]}_export.csv",
        mime='text/csv',
        use_container_width=True,
    )

with col2:
    st.markdown("#### 📊 Export Insights JSON")
    if insights:
        payload = {'domain': domain, 'n_records': len(df), 'insights': insights}
        st.download_button(
            "Download Insights JSON",
            data=json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8'),
            file_name="insights.json",
            mime='application/json',
            use_container_width=True,
        )
    else:
        st.info("Chưa có insights. Hãy tạo ở trang AI Insights.")

with col3:
    st.markdown("#### 📝 Export Markdown Report")
    if summary or insights:
        md_parts = [f"# Báo Cáo Phân Tích Dữ Liệu\n\n**Domain:** {domain}\n**Dataset:** {ds_name}\n**Bản ghi:** {len(df):,}\n"]
        if insights:
            md_parts.append("## Key Insights\n")
            for i, ins in enumerate(insights, 1):
                md_parts.append(f"### {i}. {ins.get('title','')}\n{ins.get('insight','')}\n\n**Số liệu:** {ins.get('metric','')}\n\n**Khuyến nghị:** {ins.get('action','')}\n")
        if summary:
            md_parts.append(f"## Executive Summary\n\n{summary}\n")
        md_content = "\n".join(md_parts)
        st.download_button(
            "Download Markdown",
            data=md_content.encode('utf-8'),
            file_name="report.md",
            mime='text/markdown',
            use_container_width=True,
        )
    else:
        st.info("Chưa có nội dung báo cáo.")

st.divider()

# ── Export HTML report ─────────────────────────────────────────────────────────
st.markdown("#### 🌐 Export HTML Report")

if st.button("Tạo HTML Report", use_container_width=True):
    if not insights:
        st.warning("Hãy tạo insights trước.")
    else:
        insights_html = ""
        for i, ins in enumerate(insights, 1):
            insights_html += f"""
            <div style="background:#22263a;border-radius:10px;padding:20px;margin-bottom:16px;border-left:4px solid #6c63ff">
              <h3 style="color:#6c63ff;margin:0 0 10px">{i}. {ins.get('title','')}</h3>
              <p>{ins.get('insight','')}</p>
              <div style="display:flex;gap:16px;margin-top:12px">
                <div style="background:#1a1d2e;padding:10px;border-radius:6px;flex:1"><b>Số liệu:</b> {ins.get('metric','—')}</div>
                <div style="background:#1a1d2e;padding:10px;border-radius:6px;flex:1"><b>Khuyến nghị:</b> {ins.get('action','—')}</div>
              </div>
            </div>"""

        html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8">
<title>Báo cáo: {domain}</title>
<style>body{{font-family:Segoe UI,sans-serif;background:#0f1117;color:#e8eaf6;padding:40px;max-width:900px;margin:auto}}
h1{{color:#6c63ff}}h2{{color:#9098b1;font-size:14px;text-transform:uppercase;letter-spacing:1px}}
.meta{{background:#1a1d2e;border-radius:8px;padding:16px;margin-bottom:32px;font-size:14px}}
.summary{{background:#1a1d2e;border-radius:10px;padding:24px;margin-top:32px;line-height:1.8}}
</style></head><body>
<h1>Báo Cáo Phân Tích Dữ Liệu</h1>
<div class="meta"><b>Domain:</b> {domain} &nbsp;|&nbsp; <b>Dataset:</b> {ds_name} &nbsp;|&nbsp; <b>Bản ghi:</b> {len(df):,}</div>
<h2>Key Insights</h2>
{insights_html}
{'<h2>Executive Summary</h2><div class="summary">' + summary.replace(chr(10),'<br>') + '</div>' if summary else ''}
</body></html>"""

        st.download_button(
            "Download HTML Report",
            data=html.encode('utf-8'),
            file_name="report.html",
            mime='text/html',
            use_container_width=True,
        )

# ── Slide outline ──────────────────────────────────────────────────────────────
st.divider()
st.markdown("#### 🎯 Slide Outline (PowerPoint tham khảo)")
if insights:
    outline = f"""# Slide Outline — {domain}

## Slide 1: Tiêu đề
- {domain}
- Phân tích dữ liệu: {len(df):,} bản ghi

## Slide 2: Tổng quan dữ liệu
- Nguồn: {ds_name}
- Số cột: {len(df.columns)}
- Độ đầy đủ: ...

## Slide 3–{2+len(insights)}: Key Insights
""" + "\n".join(f"### Slide {i+3}: {ins.get('title','')}\n- {ins.get('insight','')}\n- Số liệu: {ins.get('metric','')}\n- Khuyến nghị: {ins.get('action','')}" for i, ins in enumerate(insights))
    outline += f"\n\n## Slide {3+len(insights)}: Kết luận\n- Tóm tắt insights chính\n- Bước tiếp theo"
    st.text_area("Copy outline này vào PowerPoint:", outline, height=300)
else:
    st.info("Hãy tạo insights trước.")
