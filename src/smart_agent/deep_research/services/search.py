"""搜索分发助手。"""

from __future__ import annotations
import logging
from typing import Any, Tuple

# 引用统一的工具位置
from ...tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)

# 使用统一的搜索工具实例
_GLOBAL_SEARCH_TOOL = WebSearchTool()

def dispatch_search(
    query: str,
    loop_count: int,
) -> Tuple[str, list[str]]:
    """执行搜索工具并返回标准化响应。"""
    try:
        # 统一使用 __call__ 接口
        response = _GLOBAL_SEARCH_TOOL(query=query)
        
        if not response or response.startswith("No results found") or response.startswith("Error"):
            return "", [response]
        
        return response, []
    except Exception as exc:
        logger.exception("搜索工具调用失败")
        return "", [f"搜索出错: {str(exc)}"]

def prepare_research_context(
    search_result: str,
) -> tuple[str, str]:
    """为下游 Agent 构建结构化上下文和来源摘要。"""
    sources_summary = "实时网络搜索结果"
    context = search_result
    
    return sources_summary, context
