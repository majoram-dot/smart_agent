from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
from .embeddings import BaseEmbeddings
from .document_loader import Documents


class GSSCPipeline:
    def __init__(self, vector_store: VectorStore, embeddings: BaseEmbeddings, llm=None):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.llm = llm

    def generate(self, query: str) -> str:
        if self.llm:
            return self.llm(query)
        return query

    def store(self, documents: Documents):
        for doc in documents.docs:
            embedding = self.embeddings.embed(doc)
            self.vector_store.add(embedding, doc)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.embeddings.embed(query)
        results = self.vector_store.search(query_embedding, top_k)
        return results

    def combine(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        combined = f"Query: {query}\n\n"
        for i, result in enumerate(search_results, 1):
            combined += f"Result {i}:\n{result.get('text', '')}\n\n"
        
        if self.llm:
            prompt = f"Based on the following information, answer the query: {query}\n\n{combined}"
            return self.llm(prompt)
        
        return combined

    def run(self, query: str, documents: Optional[Documents] = None, top_k: int = 5) -> str:
        if documents:
            self.store(documents)
        
        enhanced_query = self.generate(query)
        search_results = self.search(enhanced_query, top_k)
        final_answer = self.combine(query, search_results)
        
        return final_answer


class MarkItDownPipeline:
    def __init__(self):
        pass

    def convert(self, content: str, format: str = "markdown") -> str:
        if format == "markdown":
            return self._to_markdown(content)
        return content

    def _to_markdown(self, content: str) -> str:
        lines = content.split("\n")
        markdown_lines = []
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                markdown_lines.append(line)
                continue
            
            if not in_code_block:
                if stripped.startswith("#"):
                    markdown_lines.append(line)
                elif stripped and not stripped.startswith(">") and not stripped.startswith("-"):
                    if len(stripped) < 80 and "." in stripped[-3:]:
                        markdown_lines.append(f"## {stripped}")
                    else:
                        markdown_lines.append(line)
                else:
                    markdown_lines.append(line)
            else:
                markdown_lines.append(line)
        
        return "\n".join(markdown_lines)
