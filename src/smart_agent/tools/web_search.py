"""基于 DuckDuckGo 的网络搜索工具。"""

from __future__ import annotations

from typing import Any, List, Dict
from duckduckgo_search import DDGS

from ..base.tool import Tool

class WebSearchTool(Tool):
    """基于 DuckDuckGo 的网络搜索工具封装。"""
    
    name = "web_search"
    description = "Perform a search on DuckDuckGo and return the snippets of the top results."
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to perform on DuckDuckGo."
        }
    }
    output_type = "string"

    def __init__(self, max_results: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.max_results = max_results

    def __call__(self, query: str) -> str:
        """执行搜索并返回格式化结果。"""
        results = []
        try:
            with DDGS() as ddgs:
                ddgs_gen = ddgs.text(query, max_results=self.max_results)
                for r in ddgs_gen:
                    results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n")
        except Exception as e:
            return f"Error performing search: {str(e)}"
            
        if not results:
            return "No results found."
            
        return "\n---\n".join(results)
