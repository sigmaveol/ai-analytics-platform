# AI Analytics Platform

AI-powered analytics dashboard — upload dữ liệu, AI tự phân tích, tạo insights và dashboard tự động.

## Chạy nhanh

```bash
pip install -r requirements.txt
streamlit run app.py
```

Mở browser tại `http://localhost:8501`

**Tài khoản mặc định:**
- Admin: `admin` / `admin123`
- Analyst: `analyst` / `analyst123`
- Viewer: `viewer` / `viewer123`

## Cấu hình AI (Claude API)

Thêm API key vào `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Lấy API key tại: https://console.anthropic.com

## Deploy lên Streamlit Cloud (miễn phí)

1. Push code lên GitHub
2. Vào https://share.streamlit.io → "Deploy an app"
3. Chọn repo → `app.py` → Deploy
4. Thêm secrets trong Settings → Secrets

## Tính năng

- Upload CSV / Excel / Parquet / JSON
- Auto data profiling (completeness, distributions)
- Interactive dashboard với Plotly
- AI chart suggestions (Claude API)
- AI-generated business insights (5–8 insights)
- Executive summary tự động
- Export: CSV, JSON, Markdown, HTML report
- Slide outline cho PowerPoint
- Authentication (admin / analyst / viewer roles)

## Tech stack

- Streamlit — frontend
- Claude API (Haiku 4.5) — AI layer
- Pandas + Plotly — data & charts
- streamlit-authenticator — auth

## Mở rộng (Phase B)

Xem `../Project/ARCHITECTURE.md` để biết roadmap đầy đủ:
Google OAuth, FastAPI backend, realtime pipeline, RBAC đầy đủ.
