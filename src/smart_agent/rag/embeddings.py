import os
from typing import List
import numpy as np

os.environ['CURL_CA_BUNDLE'] = ''
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


class BaseEmbeddings:
    def __init__(self, path: str, is_api: bool) -> None:
        self.path = path
        self.is_api = is_api

    def get_embedding(self, text: str, model: str) -> List[float]:
        raise NotImplementedError

    @classmethod
    def cosine_similarity(cls, vector1: List[float], vector2: List[float]) -> float:
        dot_product = np.dot(vector1, vector2)
        magnitude = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        if not magnitude:
            return 0
        return dot_product / magnitude


class OpenAIEmbedding(BaseEmbeddings):
    def __init__(self, path: str = '', is_api: bool = True) -> None:
        super().__init__(path, is_api)
        if self.is_api:
            from openai import OpenAI
            self.client = OpenAI()
            self.client.api_key = os.getenv("OPENAI_API_KEY")
            self.client.base_url = os.getenv("OPENAI_BASE_URL")

    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        if self.is_api:
            text = text.replace("\n", " ")
            response = self.client.embeddings.create(input=[text], model=model)
            return response.data[0].embedding
        else:
            raise NotImplementedError("OpenAI本地模型暂未实现")


class JinaEmbedding(BaseEmbeddings):
    def __init__(self, path: str = 'jinaai/jina-embeddings-v2-base-zh', is_api: bool = False) -> None:
        super().__init__(path, is_api)
        self._model = self.load_model()

    def get_embedding(self, text: str) -> List[float]:
        return self._model.encode([text])[0].tolist()

    def load_model(self):
        import torch
        from transformers import AutoModel
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        model = AutoModel.from_pretrained(self.path, trust_remote_code=True).to(device)
        return model


class ZhipuEmbedding(BaseEmbeddings):
    def __init__(self, path: str = '', is_api: bool = True) -> None:
        super().__init__(path, is_api)
        if self.is_api:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))

    def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="embedding-2",
            input=text,
        )
        return response.data[0].embedding


class DashscopeEmbedding(BaseEmbeddings):
    def __init__(self, path: str = '', is_api: bool = True) -> None:
        super().__init__(path, is_api)
        if self.is_api:
            import dashscope
            dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
            self.client = dashscope.TextEmbedding

    def get_embedding(self, text: str, model: str = 'text-embedding-v2') -> List[float]:
        response = self.client.call(model=model, input=text)
        return response.output['embeddings'][0]['embedding']


class BgeEmbedding(BaseEmbeddings):
    def __init__(self, path: str = 'BAAI/bge-base-zh-v1.5', is_api: bool = False) -> None:
        super().__init__(path, is_api)
        self._model, self._tokenizer = self.load_model(path)

    def get_embedding(self, text: str) -> List[float]:
        import torch
        
        encoded_input = self._tokenizer(
            [text], 
            padding=True, 
            truncation=True, 
            return_tensors='pt'
        )
        
        encoded_input = {k: v.to(self._model.device) for k, v in encoded_input.items()}
        
        with torch.no_grad():
            model_output = self._model(**encoded_input)
            sentence_embeddings = model_output[0][:, 0]
        
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        
        return sentence_embeddings[0].tolist()

    def load_model(self, path: str):
        import torch
        from transformers import AutoModel, AutoTokenizer
        
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        
        tokenizer = AutoTokenizer.from_pretrained(path)
        
        model = AutoModel.from_pretrained(path).to(device)
        
        model.eval()
        
        return model, tokenizer


class BgeWithAPIEmbedding(BaseEmbeddings):
    def __init__(self, path: str = '', is_api: bool = True) -> None:
        super().__init__(path, is_api)
        if self.is_api:
            from openai import OpenAI
            self.client = OpenAI()
            self.client.api_key = os.getenv("SILICONFLOW_API_KEY")
            self.client.base_url = os.getenv("SILICONFLOW_BASE_URL")

    def get_embedding(self, text: str, model: str = "BAAI/bge-m3") -> List[float]:
        if self.is_api:
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input=[text], model=model).data[0].embedding
        else:
            raise NotImplementedError
