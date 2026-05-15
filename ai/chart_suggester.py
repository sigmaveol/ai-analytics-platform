"""AI chart suggester — ask Claude to recommend charts based on dataset schema."""
from core.data_loader import infer_column_roles, get_schema_description
from ai.agent import call_json
import pandas as pd

SYSTEM = """Bạn là BI engineer chuyên thiết kế dashboard analytics.
Nhiệm vụ: phân tích schema dataset và đề xuất các biểu đồ phù hợp nhất.
Ưu tiên biểu đồ có insight rõ ràng và dễ hiểu với business user."""


def suggest(df: pd.DataFrame, domain: str = "", n: int = 5) -> list[dict]:
    """Return list of chart config dicts suggested by Claude."""
    roles = infer_column_roles(df)
    schema = get_schema_description(df)

    numerics  = [c for c, r in roles.items() if r == 'numeric']
    cats      = [c for c, r in roles.items() if r == 'categorical']
    datetimes = [c for c, r in roles.items() if r == 'datetime']

    user = f"""Dataset domain: {domain or 'chưa xác định'}
Số hàng: {len(df):,} | Số cột: {len(df.columns)}

Cột số (numeric): {numerics}
Cột phân loại (categorical): {cats}
Cột thời gian (datetime): {datetimes}

Schema chi tiết:
{schema}

Đề xuất {n} biểu đồ phù hợp nhất. Trả về JSON array:
[
  {{
    "chart_type": "bar|line|scatter|pie|histogram|box|heatmap",
    "title": "Tiêu đề biểu đồ tiếng Việt",
    "x_col": "tên cột hoặc null",
    "y_col": "tên cột hoặc null",
    "color_col": "tên cột màu sắc hoặc null",
    "rationale": "Lý do tại sao biểu đồ này có giá trị với domain này"
  }}
]"""

    return call_json(SYSTEM, user)
