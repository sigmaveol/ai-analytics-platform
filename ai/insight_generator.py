"""Generate business insights from dataset statistics using Claude."""
import json
import pandas as pd
from core.data_loader import get_schema_description
from core.analytics import numeric_summary, top_correlations
from ai.agent import call, call_json

SYSTEM = """Bạn là chuyên gia phân tích dữ liệu và business intelligence.
Nhiệm vụ của bạn là phân tích dữ liệu và tạo ra các insight kinh doanh có giá trị thực tế.
Luôn trả lời bằng tiếng Việt, ngắn gọn, súc tích, và focus vào ý nghĩa business."""


def generate_insights(df: pd.DataFrame, domain: str = "", n_insights: int = 5) -> list[dict]:
    schema = get_schema_description(df)
    num_sum = numeric_summary(df)
    corr_top = top_correlations(df)

    stats_text = num_sum.to_string(index=False) if not num_sum.empty else "Không có cột số."
    corr_text = corr_top.to_string(index=False) if not corr_top.empty else "Không đủ cột số."

    user = f"""Dataset có {len(df)} bản ghi, {len(df.columns)} cột.
Domain: {domain or 'chưa xác định'}

Schema:
{schema}

Thống kê mô tả:
{stats_text}

Top correlations:
{corr_text}

Hãy tạo {n_insights} insights kinh doanh quan trọng nhất. Trả về JSON array:
[
  {{
    "title": "Tiêu đề ngắn gọn",
    "insight": "Mô tả insight chi tiết (2-3 câu)",
    "metric": "Số liệu cụ thể hỗ trợ",
    "action": "Khuyến nghị hành động"
  }}
]"""

    return call_json(SYSTEM, user)


def generate_executive_summary(df: pd.DataFrame, domain: str, insights: list[dict]) -> str:
    insights_text = "\n".join(f"- {i['title']}: {i['insight']}" for i in insights)
    schema = get_schema_description(df)

    user = f"""Tạo executive summary (300-400 từ) bằng tiếng Việt cho báo cáo phân tích dữ liệu.

Domain: {domain}
Dữ liệu: {len(df)} bản ghi, {len(df.columns)} cột
Khoảng thời gian: (tự suy luận từ dữ liệu nếu có)

Schema:
{schema}

Key insights:
{insights_text}

Format: Markdown với header ## và bullet points."""

    return call(SYSTEM, user, max_tokens=1024)


def suggest_domain(df: pd.DataFrame) -> str:
    schema = get_schema_description(df)
    user = f"""Dựa vào tên cột và kiểu dữ liệu sau, đoán domain/lĩnh vực của dataset này (1 câu ngắn):
{schema}"""
    return call(SYSTEM, user, max_tokens=100)


def suggest_charts(df: pd.DataFrame, domain: str = "") -> list[dict]:
    from core.data_loader import infer_column_roles
    roles = infer_column_roles(df)
    schema = get_schema_description(df)

    numerics = [c for c, r in roles.items() if r == 'numeric']
    cats = [c for c, r in roles.items() if r == 'categorical']
    datetimes = [c for c, r in roles.items() if r == 'datetime']

    user = f"""Dataset domain: {domain or 'không rõ'}
Cột số: {numerics}
Cột phân loại: {cats}
Cột thời gian: {datetimes}

Schema chi tiết:
{schema}

Đề xuất 5 biểu đồ phù hợp nhất. Trả về JSON array:
[
  {{
    "chart_type": "bar|line|scatter|pie|histogram|box|heatmap",
    "title": "Tiêu đề biểu đồ",
    "x_col": "tên cột trục X hoặc null",
    "y_col": "tên cột trục Y hoặc null",
    "color_col": "cột màu sắc hoặc null",
    "rationale": "Lý do chọn biểu đồ này"
  }}
]"""

    return call_json(SYSTEM, user)
