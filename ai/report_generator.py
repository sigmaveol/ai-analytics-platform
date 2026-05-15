"""AI report generator — executive summary, slide outline, full markdown report."""
import pandas as pd
from ai.agent import call
from core.data_loader import get_schema_description

SYSTEM = """Bạn là chuyên gia tư vấn dữ liệu và viết báo cáo kinh doanh chuyên nghiệp.
Luôn viết bằng tiếng Việt, súc tích, có cấu trúc rõ ràng, phù hợp với đối tượng quản lý cấp cao."""


def executive_summary(df: pd.DataFrame, domain: str, insights: list[dict], words: int = 400) -> str:
    """Generate executive summary in Vietnamese markdown."""
    insights_text = "\n".join(
        f"- **{i.get('title','')}**: {i.get('insight','')} (Số liệu: {i.get('metric','')})"
        for i in insights
    )
    schema = get_schema_description(df)

    user = f"""Tạo executive summary (~{words} từ) bằng tiếng Việt cho báo cáo phân tích dữ liệu.

**Domain:** {domain}
**Dataset:** {len(df):,} bản ghi, {len(df.columns)} cột
**Schema tóm tắt:**
{schema}

**Key insights:**
{insights_text}

Format bắt buộc: Markdown với các mục:
## Tổng quan
## Phát hiện chính
## Khuyến nghị
## Kết luận"""

    return call(SYSTEM, user, max_tokens=1200)


def slide_outline(domain: str, insights: list[dict], dataset_name: str = '', n_records: int = 0) -> str:
    """Generate PowerPoint slide outline as markdown."""
    insights_text = "\n".join(
        f"Slide {i+3}: {ins.get('title','')}\n  - {ins.get('insight','')}\n  - Số liệu: {ins.get('metric','')}\n  - Khuyến nghị: {ins.get('action','')}"
        for i, ins in enumerate(insights)
    )

    user = f"""Tạo slide outline cho bài thuyết trình PowerPoint về phân tích dữ liệu.

Domain: {domain}
Dataset: {dataset_name} ({n_records:,} bản ghi)
Số insights: {len(insights)}

Insights:
{insights_text}

Tạo outline đầy đủ gồm: trang bìa, agenda, context, {len(insights)} insight slides, kết luận.
Với mỗi slide: tiêu đề, 3-4 bullet points, ghi chú cho presenter.
Format: Markdown có cấu trúc rõ ràng."""

    return call(SYSTEM, user, max_tokens=1500)


def full_report(df: pd.DataFrame, domain: str, insights: list[dict],
                summary: str = '', dataset_name: str = '') -> str:
    """Combine all sections into a full markdown report."""
    if not summary:
        summary = executive_summary(df, domain, insights)

    insights_md = ""
    for i, ins in enumerate(insights, 1):
        insights_md += f"""
### {i}. {ins.get('title', '')}

{ins.get('insight', '')}

**Số liệu hỗ trợ:** {ins.get('metric', '—')}

**Khuyến nghị:** {ins.get('action', '—')}

---
"""

    return f"""# Báo Cáo Phân Tích Dữ Liệu

**Domain:** {domain}
**Dataset:** {dataset_name or 'N/A'} ({len(df):,} bản ghi · {len(df.columns)} cột)
**Tạo bởi:** AI Analytics Platform

---

{summary}

---

## Chi Tiết Insights

{insights_md}
"""
