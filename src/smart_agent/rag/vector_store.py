import os
from typing import List
import json
import numpy as np
from tqdm import tqdm

try:
    import hnswlib
    HNSW_AVAILABLE = True
except ImportError:
    HNSW_AVAILABLE = False


class VectorStore:
    
    def __init__(self, document: List[str] = [''], use_hnsw: bool = True) -> None:
        self.document = document
        self.vectors = []
        self.use_hnsw = use_hnsw and HNSW_AVAILABLE
        self.hnsw_index = None
        self.dim = 0

    def get_vector(self, EmbeddingModel) -> List[List[float]]:
        self.vectors = []
        for doc in tqdm(self.document, desc="Calculating embeddings"):
            self.vectors.append(EmbeddingModel.get_embedding(doc))
        
        if self.use_hnsw and self.vectors:
            self._build_hnsw_index()
        
        return self.vectors

    def _build_hnsw_index(self):
        if not self.vectors:
            return
            
        self.dim = len(self.vectors[0])
        
        self.hnsw_index = hnswlib.Index(space='cosine', dim=self.dim)
        
        self.hnsw_index.init_index(
            max_elements=len(self.vectors),
            ef_construction=200,
            M=16
        )
        
        vectors_array = np.array(self.vectors).astype('float32')
        self.hnsw_index.add_items(vectors_array, list(range(len(self.vectors))))
        
        self.hnsw_index.set_ef(50)

    def persist(self, path: str = 'storage'):
        if not os.path.exists(path):
            os.makedirs(path)
        
        with open(f"{path}/document.json", 'w', encoding='utf-8') as f:
            json.dump(self.document, f, ensure_ascii=False)
        
        if self.vectors:
            with open(f"{path}/vectors.json", 'w', encoding='utf-8') as f:
                json.dump(self.vectors, f)
        
        if self.hnsw_index is not None:
            self.hnsw_index.save_index(f"{path}/hnsw_index.bin")

    def load_vector(self, path: str = 'storage'):
        with open(f"{path}/vectors.json", 'r', encoding='utf-8') as f:
            self.vectors = json.load(f)
        
        doc_path = f"{path}/document.json"
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                self.document = json.load(f)
        else:
            with open(f"{path}/doecment.json", 'r', encoding='utf-8') as f:
                self.document = json.load(f)
        
        index_path = f"{path}/hnsw_index.bin"
        if self.use_hnsw and os.path.exists(index_path):
            self.dim = len(self.vectors[0]) if self.vectors else 0
            self.hnsw_index = hnswlib.Index(space='cosine', dim=self.dim)
            self.hnsw_index.load_index(index_path)
            self.hnsw_index.set_ef(50)

    def get_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        from .embeddings import BaseEmbeddings
        return BaseEmbeddings.cosine_similarity(vector1, vector2)

    def query(self, query: str, EmbeddingModel, k: int = 1) -> List[str]:
        query_vector = EmbeddingModel.get_embedding(query)
        
        if self.use_hnsw and self.hnsw_index is not None:
            return self._query_hnsw(query_vector, k)
        else:
            return self._query_brute_force(query_vector, k)

    def _query_hnsw(self, query_vector: List[float], k: int) -> List[str]:
        query_array = np.array([query_vector]).astype('float32')
        
        search_k = min(k * 2, len(self.vectors))
        labels, distances = self.hnsw_index.knn_query(query_array, k=search_k)
        
        similarities = 1 - distances[0]
        
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        result_indices = labels[0][top_k_indices]
        
        return [self.document[i] for i in result_indices]

    def _query_brute_force(self, query_vector: List[float], k: int) -> List[str]:
        similarities = np.array([
            self.get_similarity(query_vector, vector)
            for vector in self.vectors
        ])
        
        top_k_indices = similarities.argsort()[-k:][::-1]
        return np.array(self.document)[top_k_indices].tolist()
