"""Load and validate uploaded datasets."""
import io
import pandas as pd
import streamlit as st
from pathlib import Path


def load_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith('.csv'):
        return pd.read_csv(uploaded_file, encoding='utf-8-sig')
    if name.endswith(('.xls', '.xlsx')):
        return pd.read_excel(uploaded_file)
    if name.endswith('.parquet'):
        return pd.read_parquet(io.BytesIO(uploaded_file.read()))
    if name.endswith('.json'):
        return pd.read_json(uploaded_file)
    raise ValueError(f"Unsupported file type: {uploaded_file.name}")


def load_sample(name: str) -> pd.DataFrame:
    base = Path(__file__).parent.parent / 'data' / 'samples'
    path = base / name
    if path.suffix == '.parquet':
        return pd.read_parquet(path)
    return pd.read_csv(path, encoding='utf-8-sig')


def infer_column_roles(df: pd.DataFrame) -> dict:
    """Classify columns as numeric, categorical, datetime, text."""
    roles = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            roles[col] = 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            roles[col] = 'datetime'
        elif df[col].nunique() <= 30 and df[col].dtype == object:
            roles[col] = 'categorical'
        else:
            roles[col] = 'text'
    return roles


def get_schema_description(df: pd.DataFrame) -> str:
    roles = infer_column_roles(df)
    lines = []
    for col, role in roles.items():
        n_unique = df[col].nunique()
        null_pct = round(100 * df[col].isna().mean(), 1)
        if role == 'numeric':
            mn, mx, med = df[col].min(), df[col].max(), df[col].median()
            lines.append(f"- {col} [numeric]: min={mn:.2f}, max={mx:.2f}, median={med:.2f}, null={null_pct}%")
        elif role == 'categorical':
            top = df[col].value_counts().index[:3].tolist()
            lines.append(f"- {col} [categorical]: {n_unique} giá trị, top: {top}, null={null_pct}%")
        elif role == 'datetime':
            lines.append(f"- {col} [datetime]: null={null_pct}%")
        else:
            lines.append(f"- {col} [text]: null={null_pct}%")
    return "\n".join(lines)
