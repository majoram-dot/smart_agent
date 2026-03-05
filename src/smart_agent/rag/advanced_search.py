from typing import List, Dict, Any
import re


class MQESearch:
    def __init__(self, vector_store, embeddings):
        self.vector_store = vector_store
        self.embeddings = embeddings

    def generate_multiple_queries(self, query: str, num_queries: int = 3) -> List[str]:
        queries = [query]
        
        synonyms = {
            "what": ["how", "explain", "describe"],
            "how": ["what", "explain", "describe"],
            "why": ["reason", "cause", "because"],
            "best": ["top", "recommended", "good"],
            "good": ["best", "great", "excellent"],
        }
        
        for word, syns in synonyms.items():
            if word in query.lower():
                for syn in syns[:num_queries-1]:
                    new_query = re.sub(r'\b' + word + r'\b', syn, query, flags=re.IGNORECASE)
                    if new_query not in queries:
                        queries.append(new_query)
                break
        
        if len(queries) < num_queries:
            prefixes = ["", "Please ", "Can you "]
            for prefix in prefixes[1:]:
                if len(queries) >= num_queries:
                    break
                new_query = prefix + query
                if new_query not in queries:
                    queries.append(new_query)
        
        return queries[:num_queries]

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        queries = self.generate_multiple_queries(query)
        
        all_results = []
        seen_texts = set()
        
        for q in queries:
            query_embedding = self.embeddings.embed(q)
            results = self.vector_store.search(query_embedding, top_k * 2)
            
            for result in results:
                text = result.get("text", "")
                if text not in seen_texts:
                    seen_texts.add(text)
                    all_results.append(result)
        
        all_results = sorted(all_results, key=lambda x: x.get("score", 0), reverse=True)
        
        return all_results[:top_k]


class HyDESearch:
    def __init__(self, vector_store, embeddings, llm=None):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.llm = llm

    def generate_hypothetical_document(self, query: str) -> str:
        if self.llm:
            prompt = f"Write a detailed paragraph that answers the following question:\n{query}"
            return self.llm(prompt)
        
        return f"This is a hypothetical answer to the question: {query}. It contains relevant information that might be found in documents about this topic."

    def search(self, query: str, top_k: int = 5, use_hyde: bool = True) -> List[Dict[str, Any]]:
        if use_hyde:
            hyde_doc = self.generate_hypothetical_document(query)
            search_text = f"{query}\n\n{hyde_doc}"
        else:
            search_text = query
        
        query_embedding = self.embeddings.embed(search_text)
        results = self.vector_store.search(query_embedding, top_k)
        
        return results


class HybridSearch:
    def __init__(self, vector_store, embeddings, bm25=None):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.bm25 = bm25
        self.documents = []

    def add_documents(self, documents: List[str]):
        self.documents = documents
        
        if self.bm25:
            try:
                from rank_bm25 import BM25Okapi
                tokenized_docs = [doc.lower().split() for doc in documents]
                self.bm25 = BM25Okapi(tokenized_docs)
            except ImportError:
                pass

    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.documents:
            return []
        
        try:
            tokenized_query = query.lower().split()
            scores = self.bm25.get_scores(tokenized_query)
            
            results = []
            for i, score in enumerate(scores):
                results.append({
                    "text": self.documents[i],
                    "score": float(score),
                    "index": i
                })
            
            results = sorted(results, key=lambda x: x["score"], reverse=True)
            return results[:top_k]
        except Exception:
            return []

    def search(self, query: str, top_k: int = 5, alpha: float = 0.5) -> List[Dict[str, Any]]:
        vector_results = []
        query_embedding = self.embeddings.embed(query)
        vector_results = self.vector_store.search(query_embedding, top_k * 2)
        
        bm25_results = self._bm25_search(query, top_k * 2)
        
        combined_scores = {}
        
        for result in vector_results:
            text = result.get("text", "")
            score = result.get("score", 0)
            if text not in combined_scores:
                combined_scores[text] = {"vector_score": 0, "bm25_score": 0}
            combined_scores[text]["vector_score"] = score
        
        for result in bm25_results:
            text = result.get("text", "")
            score = result.get("score", 0)
            if text not in combined_scores:
                combined_scores[text] = {"vector_score": 0, "bm25_score": 0}
            combined_scores[text]["bm25_score"] = score
        
        final_results = []
        for text, scores in combined_scores.items():
            vector_score = scores["vector_score"]
            bm25_score = scores["bm25_score"]
            
            max_vector = max([r.get("score", 0) for r in vector_results]) if vector_results else 1
            max_bm25 = max([r.get("score", 0) for r in bm25_results]) if bm25_results else 1
            
            norm_vector = vector_score / max_vector if max_vector > 0 else 0
            norm_bm25 = bm25_score / max_bm25 if max_bm25 > 0 else 0
            
            combined_score = alpha * norm_vector + (1 - alpha) * norm_bm25
            
            final_results.append({
                "text": text,
                "score": combined_score,
                "vector_score": vector_score,
                "bm25_score": bm25_score
            })
        
        final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)
        return final_results[:top_k]
