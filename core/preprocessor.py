"""Auto data cleaning pipeline — handle nulls, normalize dtypes, detect outliers."""
import pandas as pd
import numpy as np


def auto_clean(df: pd.DataFrame, verbose: bool = False) -> tuple[pd.DataFrame, list[str]]:
    """Run full auto-cleaning pipeline. Returns (cleaned_df, log_of_changes)."""
    df = df.copy()
    log = []

    # 1. Drop fully empty columns
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    if empty_cols:
        df.drop(columns=empty_cols, inplace=True)
        log.append(f"Xóa {len(empty_cols)} cột rỗng hoàn toàn: {empty_cols}")

    # 2. Drop fully empty rows
    n_before = len(df)
    df.dropna(how='all', inplace=True)
    dropped = n_before - len(df)
    if dropped:
        log.append(f"Xóa {dropped} hàng rỗng hoàn toàn")

    # 3. Remove duplicate rows
    n_before = len(df)
    df.drop_duplicates(inplace=True)
    dups = n_before - len(df)
    if dups:
        log.append(f"Xóa {dups} hàng trùng lặp")

    # 4. Infer and convert datetime columns
    for col in df.select_dtypes(include='object').columns:
        sample = df[col].dropna().head(50)
        try:
            parsed = pd.to_datetime(sample, infer_datetime_format=True)
            if parsed.notna().mean() > 0.8:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors='coerce')
                log.append(f"Chuyển '{col}' sang datetime")
        except Exception:
            pass

    # 5. Fill missing values — median for numeric, mode for categorical
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count == 0:
            continue
        null_pct = null_count / len(df)
        if null_pct > 0.8:
            continue  # Too many nulls — skip
        if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
            fill_val = df[col].median()
            df[col].fillna(fill_val, inplace=True)
            log.append(f"Fill null '{col}' bằng median ({fill_val:.2f}) — {null_count} giá trị")
        elif df[col].dtype == object and df[col].nunique() <= 50:
            mode_vals = df[col].mode()
            if len(mode_vals):
                df[col].fillna(mode_vals[0], inplace=True)
                log.append(f"Fill null '{col}' bằng mode ('{mode_vals[0]}') — {null_count} giá trị")

    # 6. Strip whitespace from string columns
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

    log.append(f"Kết quả: {len(df)} hàng x {len(df.columns)} cột")
    return df, log


def detect_outliers(df: pd.DataFrame, method: str = 'iqr') -> dict[str, pd.Series]:
    """Return boolean mask of outliers for each numeric column."""
    result = {}
    num_cols = [c for c in df.select_dtypes(include='number').columns
                if not pd.api.types.is_bool_dtype(df[c])]
    for col in num_cols:
        s = df[col].dropna()
        if method == 'iqr':
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            mask = (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)
        else:  # z-score
            z = (df[col] - s.mean()) / s.std()
            mask = z.abs() > 3
        result[col] = mask
    return result


def outlier_summary(df: pd.DataFrame) -> pd.DataFrame:
    masks = detect_outliers(df)
    rows = []
    for col, mask in masks.items():
        n = int(mask.sum())
        if n > 0:
            rows.append({
                'Cột': col,
                'Outliers': n,
                'Tỷ lệ (%)': round(100 * n / len(df), 1),
                'Min outlier': round(float(df.loc[mask, col].min()), 2),
                'Max outlier': round(float(df.loc[mask, col].max()), 2),
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['Cột', 'Outliers', 'Tỷ lệ (%)', 'Min outlier', 'Max outlier'])
