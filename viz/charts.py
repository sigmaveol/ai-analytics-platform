"""Plotly chart factory — render charts from config dicts."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e8eaf6', family='Segoe UI, system-ui, sans-serif'),
    xaxis=dict(gridcolor='#2d3250', zerolinecolor='#2d3250'),
    yaxis=dict(gridcolor='#2d3250', zerolinecolor='#2d3250'),
    colorway=['#6c63ff','#ff6584','#43e97b','#f7971e','#56ccf2','#f093fb'],
    hoverlabel=dict(bgcolor='#22263a', bordercolor='#6c63ff', font_color='#e8eaf6'),
    margin=dict(t=40, b=40, l=60, r=20),
)


def _apply_theme(fig) -> go.Figure:
    fig.update_layout(**THEME)
    return fig


def bar(df: pd.DataFrame, x: str, y: str, title: str = '', color: str = None, horizontal: bool = False) -> go.Figure:
    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation='h', title=title, color=color,
                     color_discrete_sequence=THEME['colorway'])
    else:
        fig = px.bar(df, x=x, y=y, title=title, color=color,
                     color_discrete_sequence=THEME['colorway'])
    return _apply_theme(fig)


def line(df: pd.DataFrame, x: str, y: str | list, title: str = '') -> go.Figure:
    fig = px.line(df, x=x, y=y, title=title, markers=True,
                  color_discrete_sequence=THEME['colorway'])
    return _apply_theme(fig)


def pie(df: pd.DataFrame, names: str, values: str, title: str = '') -> go.Figure:
    fig = px.pie(df, names=names, values=values, title=title, hole=0.4,
                 color_discrete_sequence=THEME['colorway'])
    return _apply_theme(fig)


def histogram(df: pd.DataFrame, col: str, title: str = '', bins: int = 30) -> go.Figure:
    fig = px.histogram(df, x=col, title=title, nbins=bins,
                       color_discrete_sequence=['#6c63ff'])
    return _apply_theme(fig)


def box(df: pd.DataFrame, x: str, y: str, title: str = '', color: str = None) -> go.Figure:
    fig = px.box(df, x=x, y=y, title=title, color=color or x,
                 color_discrete_sequence=THEME['colorway'])
    return _apply_theme(fig)


def scatter(df: pd.DataFrame, x: str, y: str, title: str = '', color: str = None, size: str = None) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, title=title, color=color, size=size,
                     color_discrete_sequence=THEME['colorway'])
    return _apply_theme(fig)


def heatmap(df: pd.DataFrame, title: str = '') -> go.Figure:
    fig = go.Figure(data=go.Heatmap(
        z=df.values, x=df.columns.tolist(), y=df.index.tolist(),
        colorscale='Viridis', text=df.round(2).values,
        texttemplate='%{text}', showscale=True,
    ))
    fig.update_layout(title=title, **THEME)
    return fig


def render_from_config(df: pd.DataFrame, cfg: dict) -> go.Figure | None:
    """Render a chart from AI-suggested config dict."""
    ct = cfg.get('chart_type', '')
    x = cfg.get('x_col')
    y = cfg.get('y_col')
    title = cfg.get('title', '')
    color = cfg.get('color_col')

    # Validate columns exist
    for col in [x, y, color]:
        if col and col not in df.columns:
            return None

    try:
        if ct == 'bar':
            return bar(df, x, y, title, color)
        elif ct == 'line':
            return line(df, x, y, title)
        elif ct == 'pie':
            vc = df[x].value_counts().reset_index()
            vc.columns = [x, 'count']
            return pie(vc, x, 'count', title)
        elif ct == 'histogram':
            return histogram(df, x or y, title)
        elif ct == 'box':
            return box(df, x, y, title, color)
        elif ct == 'scatter':
            return scatter(df, x, y, title, color)
        elif ct == 'heatmap':
            corr = df.select_dtypes('number').corr()
            return heatmap(corr, title)
    except Exception:
        return None
