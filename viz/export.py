"""Export utilities — HTML report, CSV, Markdown, slide outline."""
import io
import json
import pandas as pd


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding='utf-8-sig')
    return buf.getvalue().encode('utf-8-sig')


def to_json_bytes(insights: list[dict], domain: str, n_records: int) -> bytes:
    payload = {'domain': domain, 'n_records': n_records, 'insights': insights}
    return json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')


def to_markdown_bytes(domain: str, dataset_name: str, n_records: int,
                      insights: list[dict], summary: str = '') -> bytes:
    parts = [f"# Báo Cáo Phân Tích Dữ Liệu\n\n**Domain:** {domain}\n**Dataset:** {dataset_name}\n**Bản ghi:** {n_records:,}\n"]
    if insights:
        parts.append("## Key Insights\n")
        for i, ins in enumerate(insights, 1):
            parts.append(
                f"### {i}. {ins.get('title','')}\n"
                f"{ins.get('insight','')}\n\n"
                f"**Số liệu:** {ins.get('metric','')}\n\n"
                f"**Khuyến nghị:** {ins.get('action','')}\n"
            )
    if summary:
        parts.append(f"## Executive Summary\n\n{summary}\n")
    return "\n".join(parts).encode('utf-8')


def to_html_bytes(domain: str, dataset_name: str, n_records: int,
                  insights: list[dict], summary: str = '') -> bytes:
    insights_html = ""
    for i, ins in enumerate(insights, 1):
        insights_html += f"""
        <div class="card">
          <h3><span class="num">{i}</span> {ins.get('title','')}</h3>
          <p>{ins.get('insight','')}</p>
          <div class="meta-row">
            <div class="meta-box"><b>Số liệu:</b> {ins.get('metric','—')}</div>
            <div class="meta-box"><b>Khuyến nghị:</b> {ins.get('action','—')}</div>
          </div>
        </div>"""

    summary_html = f'<section><h2>Executive Summary</h2><div class="summary">{summary.replace(chr(10),"<br>")}</div></section>' if summary else ''

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo cáo: {domain}</title>
<style>
  body{{font-family:Segoe UI,sans-serif;background:#0f1117;color:#e8eaf6;padding:48px;max-width:960px;margin:auto;line-height:1.7}}
  h1{{color:#6c63ff;font-size:28px;margin-bottom:4px}}
  h2{{color:#9098b1;font-size:13px;text-transform:uppercase;letter-spacing:1px;margin:32px 0 16px}}
  h3{{color:#e8eaf6;font-size:17px;margin-bottom:8px;display:flex;align-items:center;gap:10px}}
  .num{{background:#6c63ff;color:white;border-radius:50%;width:26px;height:26px;display:inline-flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0}}
  .meta{{background:#1a1d2e;border-radius:8px;padding:16px 20px;margin-bottom:32px;font-size:14px;color:#9098b1}}
  .card{{background:#22263a;border:1px solid #2d3250;border-radius:12px;padding:24px;margin-bottom:16px;border-left:4px solid #6c63ff}}
  .meta-row{{display:flex;gap:12px;margin-top:14px;flex-wrap:wrap}}
  .meta-box{{background:#1a1d2e;border-radius:6px;padding:10px 14px;font-size:13px;flex:1;min-width:200px}}
  .summary{{background:#1a1d2e;border-radius:10px;padding:24px;font-size:14px}}
  section{{margin-top:40px}}
</style>
</head>
<body>
<h1>Báo Cáo Phân Tích Dữ Liệu</h1>
<div class="meta">
  <b>Domain:</b> {domain} &nbsp;·&nbsp;
  <b>Dataset:</b> {dataset_name} &nbsp;·&nbsp;
  <b>Bản ghi:</b> {n_records:,}
</div>
<section>
  <h2>Key Insights</h2>
  {insights_html}
</section>
{summary_html}
<footer style="margin-top:48px;font-size:12px;color:#555;border-top:1px solid #2d3250;padding-top:16px">
  Tạo bởi AI Analytics Platform · Powered by Claude AI
</footer>
</body>
</html>"""
    return html.encode('utf-8')
