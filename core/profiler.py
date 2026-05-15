"""Auto data profiling — shape, completeness, distributions."""
import pandas as pd
import numpy as np


def profile(df: pd.DataFrame) -> dict:
    n_rows, n_cols = df.shape
    n_missing = int(df.isna().sum().sum())
    completeness = round(100 * (1 - n_missing / (n_rows * n_cols)), 1)
    duplicates = int(df.duplicated().sum())

    col_profiles = []
    for col in df.columns:
        s = df[col]
        p = {
            'name': col,
            'dtype': str(s.dtype),
            'null_count': int(s.isna().sum()),
            'null_pct': round(100 * s.isna().mean(), 1),
            'unique': int(s.nunique()),
        }
        if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
            sv = s.dropna()
            p.update({
                'mean': round(float(sv.mean()), 3) if len(sv) else None,
                'median': round(float(sv.median()), 3) if len(sv) else None,
                'std': round(float(sv.std()), 3) if len(sv) else None,
                'min': float(sv.min()) if len(sv) else None,
                'max': float(sv.max()) if len(sv) else None,
                'q25': float(sv.quantile(0.25)) if len(sv) else None,
                'q75': float(sv.quantile(0.75)) if len(sv) else None,
            })
        elif s.dtype == object or str(s.dtype) == 'category':
            vc = s.value_counts().head(5)
            p['top_values'] = vc.index.tolist()
            p['top_counts'] = vc.values.tolist()
        col_profiles.append(p)

    return {
        'n_rows': n_rows,
        'n_cols': n_cols,
        'n_missing': n_missing,
        'completeness_pct': completeness,
        'duplicates': duplicates,
        'columns': col_profiles,
    }


def completeness_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append({
            'Cột': col,
            'Kiểu dữ liệu': str(s.dtype),
            'Giá trị null': int(s.isna().sum()),
            'Tỷ lệ null (%)': round(100 * s.isna().mean(), 1),
            'Unique': int(s.nunique()),
        })
    return pd.DataFrame(rows).sort_values('Tỷ lệ null (%)', ascending=False)
