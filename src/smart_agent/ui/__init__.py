"""
ui/ — Gradio Web 界面子包。

将 gradio_ui.py 的实现封装在此子包内，保持包结构整洁。
需要安装 gradio 可选依赖：`pip install 'smart_agent[gradio]'`
"""
from .gradio_ui import GradioUI as GradioUI, stream_to_gradio as stream_to_gradio

__all__ = [
    "GradioUI",
    "stream_to_gradio",
]
