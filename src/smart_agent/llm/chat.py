#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   chat.py
@Time    :   2024/02/12 13:50:47
@Author  :   不要葱姜蒜
@Version :   1.0
@Desc    :   LLM 对话模块，包含多种大语言模型实现
'''
import os
from typing import Dict, List, Iterator

# RAG 场景的 Prompt 模板
# {question} - 用户问题
# {context} - 检索到的相关文档
PROMPT_TEMPLATE = dict(
    # 通用模板：直接用上下文回答
    RAG_PROMPT_TEMPALTE="""你是一个专业的技术文档助手。请根据以下上下文回答用户问题。

## 上下文
{context}

## 要求
1. 只基于提供的内容回答，不要编造信息
2. 如果无法从上下文中找到答案，请回答"数据库中没有这个内容，我无法回答"
3. 使用简洁、清晰的中文回答

## 问题
{question}

## 回答
""",
    
    # InternLM 专用：先总结上下文再回答
    InternLM_PROMPT_TEMPALTE="""你是一个专业的技术文档助手。请先对上下文进行总结，再回答用户问题。

## 上下文
{context}

## 要求
1. 先用一句话总结上下文的主要内容
2. 然后基于上下文回答用户问题
3. 如果无法从上下文中找到答案，请回答"数据库中没有这个内容，我无法回答"
4. 使用简洁、清晰的中文回答

## 问题
{question}

## 回答
"""
)


class BaseModel:
    """LLM 基类，定义对话接口"""
    def __init__(self, path: str = '') -> None:
        self.path = path

    def chat(self, prompt: str, history: List[dict], content: str) -> str:
        """对话接口，子类必须实现
        Args:
            prompt: 用户当前问题
            history: 对话历史列表
            content: 检索到的相关上下文
        Returns:
            LLM 的回答
        """
        pass

    def chat_stream(self, prompt: str, history: List[dict], content: str) -> Iterator[str]:
        """流式对话接口，子类可选择实现
        Args:
            prompt: 用户当前问题
            history: 对话历史列表
            content: 检索到的相关上下文
        Yields:
            流式输出的文本片段
        """
        pass

    def load_model(self):
        """加载模型，子类必须实现"""
        pass

class OpenAIChat(BaseModel):
    """调用 OpenAI 兼容 API 进行对话"""
    def __init__(self, path: str = '', model: str = "qwen-plus") -> None:
        super().__init__(path)
        self.model = model

    def chat(self, prompt: str, history: List[dict], content: str) -> str:
        """调用 API 进行对话"""
        from openai import OpenAI
        # 创建客户端，配置 API Key 和 base_url
        client = OpenAI()
        client.api_key = os.getenv("OPENAI_API_KEY")   
        client.base_url = os.getenv("OPENAI_BASE_URL")
        
        # 将问题 + 上下文格式化成 prompt，追加到历史记录
        # history 格式: [{'role': 'user/assistant', 'content': '...'}]
        history.append({
            'role': 'user', 
            'content': PROMPT_TEMPLATE['RAG_PROMPT_TEMPALTE'].format(
                question=prompt, 
                context=content
            )
        })
        
        # 调用 ChatCompletion 接口
        response = client.chat.completions.create(
            model=self.model,        # 使用的模型
            messages=history,        # 对话历史
            max_tokens=150,         # 最大生成 token 数
            temperature=0.1         # 温度参数，控制随机性
        )
        
        # 返回模型回复内容
        return response.choices[0].message.content

    def chat_stream(self, prompt: str, history: List[dict], content: str) -> Iterator[str]:
        """流式调用 API 进行对话"""
        from openai import OpenAI
        # 创建客户端
        client = OpenAI()
        client.api_key = os.getenv("OPENAI_API_KEY")   
        client.base_url = os.getenv("OPENAI_BASE_URL")
        
        # 格式化 prompt
        history.append({
            'role': 'user', 
            'content': PROMPT_TEMPLATE['RAG_PROMPT_TEMPALTE'].format(
                question=prompt, 
                context=content
            )
        })
        
        # 流式调用 ChatCompletion 接口
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
            max_tokens=150,
            temperature=0.1,
            stream=True  # 开启流式输出
        )
        
        # 逐块返回
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

class InternLMChat(BaseModel):
    """使用 InternLM 本地模型进行对话"""
    def __init__(self, path: str = '') -> None:
        super().__init__(path)
        # 初始化时直接加载模型
        self.load_model()

    def chat(self, prompt: str, history: List = [], content: str='') -> str:
        """使用本地模型进行对话"""
        # 使用 InternLM 专用模板（先总结再回答）
        prompt = PROMPT_TEMPLATE['InternLM_PROMPT_TEMPALTE'].format(
            question=prompt, 
            context=content
        )
        # InternLM 的 chat 方法会返回 (回答, 新历史)
        response, history = self.model.chat(self.tokenizer, prompt, history)
        return response


    def load_model(self):
        """加载 InternLM 本地模型"""
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        # 分词器
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.path, 
            trust_remote_code=True
        )
        # 因果语言模型 (Causal LM)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path, 
            torch_dtype=torch.float16,  # 使用半精度，节省显存
            trust_remote_code=True
        ).cuda()  # 移到 GPU

class DashscopeChat(BaseModel):
    """调用阿里云 DashScope API 进行对话"""
    def __init__(self, path: str = '', model: str = "qwen-turbo") -> None:
        super().__init__(path)
        self.model = model

    def chat(self, prompt: str, history: List[Dict], content: str) -> str:
        """调用 DashScope API 进行对话"""
        import dashscope
        # 阿里云需要全局设置 API Key
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        # 追加用户消息到历史
        history.append({
            'role': 'user', 
            'content': PROMPT_TEMPLATE['RAG_PROMPT_TEMPALTE'].format(
                question=prompt, 
                context=content
            )
        })
        
        # 调用 Generation.call 接口
        response = dashscope.Generation.call(
            model=self.model,
            messages=history,
            result_format='message',  # 返回消息格式
            max_tokens=150,
            temperature=0.1
        )
        return response.output.choices[0].message.content
    

class ZhipuChat(BaseModel):
    """调用智谱 AI API 进行对话"""
    def __init__(self, path: str = '', model: str = "glm-4") -> None:
        super().__init__(path)
        from zhipuai import ZhipuAI
        # 智谱有专用 SDK
        self.client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
        self.model = model

    def chat(self, prompt: str, history: List[Dict], content: str) -> str:
        """调用智谱 API 进行对话"""
        # 追加用户消息到历史
        history.append({
            'role': 'user', 
            'content': PROMPT_TEMPLATE['RAG_PROMPT_TEMPALTE'].format(
                question=prompt, 
                context=content
            )
        })
        
        # 调用智谱 chat.completions 接口
        response = self.client.chat.completions.create(
            model=self.model,
            messages=history,
            max_tokens=150,
            temperature=0.1
        )
        # 注意：智谱返回的是 message 对象，不是 content 字符串
        return response.choices[0].message

class SiliconflowChat(BaseModel):
    """调用硅基流动 API 进行对话"""
    def __init__(self, path: str = '', model: str = "Qwen/Qwen2.5-7B-Instruct") -> None:
        super().__init__(path)
        self.model = model

    def chat(self, prompt: str, history: List[dict], content: str) -> str:
        """调用硅基流动 API 进行对话"""
        from openai import OpenAI
        # 硅基流动也兼容 OpenAI 格式
        client = OpenAI()
        client.api_key = os.getenv("SILICONFLOW_API_KEY")   
        client.base_url = os.getenv("SILICONFLOW_BASE_URL")
        
        # 格式化 prompt
        final_prompt = {
            'role': 'user', 
            'content': PROMPT_TEMPLATE['RAG_PROMPT_TEMPALTE'].format(
                question=prompt, 
                context=content
            )
        }
        
        # 打印调试信息
        print("---------------------input---------------------")
        print(final_prompt)
        
        # 追加到历史
        history.append(final_prompt)
        
        # 调用 API
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
            # max_tokens=150,  # 注释掉了，不限制长度
            temperature=0.1
        )
        return response.choices[0].message.content
    
    def chat_stream(self, prompt: str, history: List[dict], content: str) -> Iterator[str]:
        """流式调用硅基流动 API 进行对话"""
        from openai import OpenAI
        client = OpenAI()
        client.api_key = os.getenv("SILICONFLOW_API_KEY")   
        client.base_url = os.getenv("SILICONFLOW_BASE_URL")
        
        # 格式化 prompt
        final_prompt = {
            'role': 'user', 
            'content': PROMPT_TEMPLATE['RAG_PROMPT_TEMPALTE'].format(
                question=prompt, 
                context=content
            )
        }
        
        # 追加到历史
        history.append(final_prompt)
        
        # 流式调用 API
        response = client.chat.completions.create(
            model=self.model,
            messages=history,
            temperature=0.1,
            stream=True
        )
        
        # 逐块返回
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
