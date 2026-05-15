"""Claude API orchestration — stateless helper for analytics tasks."""
import os
import json
import anthropic
import streamlit as st


def _client() -> anthropic.Anthropic:
    api_key = (
        st.secrets.get("ANTHROPIC_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
    )
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY chưa được cấu hình. Thêm vào .streamlit/secrets.toml hoặc biến môi trường.")
    return anthropic.Anthropic(api_key=api_key)


def call(system: str, user: str, model: str = "claude-haiku-4-5-20251001", max_tokens: int = 2048) -> str:
    client = _client()
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def call_json(system: str, user: str, **kwargs) -> dict | list:
    raw = call(system, user + "\n\nTrả về JSON hợp lệ, không có text thêm.", **kwargs)
    # Extract JSON block if wrapped in markdown
    import re
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
    text = m.group(1) if m else raw.strip()
    return json.loads(text)
