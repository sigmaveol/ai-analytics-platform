"""Descriptive analytics — correlation, distribution, trend detection."""
import pandas as pd
import numpy as np


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    num_cols = df.select_dtypes(include='number').columns.tolist()
    if not num_cols:
        return pd.DataFrame()
    return df[num_cols].describe().round(3).T.reset_index().rename(columns={'index': 'Cột'})


def correlation_matrix(df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
    num_cols = df.select_dtypes(include='number').columns.tolist()
    if len(num_cols) < 2:
        return pd.DataFrame()
    return df[num_cols].corr(method=method).round(3)


def top_correlations(df: pd.DataFrame, target_col: str = None, top_n: int = 10) -> pd.DataFrame:
    corr = correlation_matrix(df)
    if corr.empty:
        return pd.DataFrame()
    rows = []
    cols = corr.columns.tolist()
    for i, a in enumerate(cols):
        for b in cols[i+1:]:
            rows.append({'Cột A': a, 'Cột B': b, 'Correlation': corr.loc[a, b]})
    result = pd.DataFrame(rows).sort_values('Correlation', key=abs, ascending=False)
    if target_col and target_col in cols:
        result = result[result['Cột A'].eq(target_col) | result['Cột B'].eq(target_col)]
    return result.head(top_n)


def detect_datetime_col(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
        if df[col].dtype == object:
            try:
                pd.to_datetime(df[col].dropna().head(20), infer_datetime_format=True)
                return col
            except Exception:
                pass
    return None


def monthly_trend(df: pd.DataFrame, date_col: str, value_col: str = None) -> pd.DataFrame:
    df = df.copy()
    df['_dt'] = pd.to_datetime(df[date_col], errors='coerce')
    df = df[df['_dt'].notna()]
    df['_month'] = df['_dt'].dt.to_period('M').astype(str)
    if value_col and value_col in df.columns:
        return df.groupby('_month')[value_col].mean().reset_index().rename(columns={'_month': 'Tháng', value_col: 'Giá trị TB'})
    else:
        return df.groupby('_month').size().reset_index().rename(columns={'_month': 'Tháng', 0: 'Số bản ghi'})


def category_distribution(df: pd.DataFrame, col: str, top_n: int = 15) -> pd.DataFrame:
    vc = df[col].value_counts().head(top_n).reset_index()
    vc.columns = [col, 'Số lượng']
    vc['Tỷ lệ (%)'] = (100 * vc['Số lượng'] / vc['Số lượng'].sum()).round(1)
    return vc
