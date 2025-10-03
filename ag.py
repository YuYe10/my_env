#!/usr/bin/env python3
"""
ag.py - (LLM) AGent for everything
基于DeepSeek API的多模态AI Agent实现
支持流式输出，避免超时问题
"""

import argparse
import sys
import os
import base64
import requests
import readline
import json
from typing import Optional, List, Dict, Any, Generator
from pathlib import Path

class DeepSeekAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or pass via --api-key")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.conversation_history: List[Dict[str, Any]] = []
    
    def stream_text_response(self, prompt: str, use_cot: bool = False, model: str = "deepseek-chat") -> Generator[str, None, None]:
        """流式处理文本响应"""
        if use_cot:
            prompt = "请使用思维链推理逐步分析以下内容:\n" + prompt
        
        # 添加对话历史
        messages = self.conversation_history.copy()
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        try:
            with requests.post(f"{self.base_url}/chat/completions", 
                              json=payload, headers=self.headers, stream=True, timeout=60) as response:
                response.raise_for_status()
                
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            json_str = decoded_line[6:]
                            if json_str == '[DONE]':
                                break
                            
                            try:
                                data = json.loads(json_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_response += content
                                        yield content
                            except json.JSONDecodeError:
                                continue
                
                # 更新对话历史
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
                # 保持对话历史长度合理
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-6:]
                
        except requests.exceptions.RequestException as e:
            yield f"API请求错误: {e}"
    
    def stream_image_response(self, image_path: str, query: Optional[str] = None) -> Generator[str, None, None]:
        """流式处理图片响应"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                yield f"错误: 文件 '{image_path}' 不存在"
                return
            
            # 编码图片为base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            content = []
            if query:
                content.append({"type": "text", "text": query})
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
            
            payload = {
                "model": "deepseek-vl",
                "messages": [{"role": "user", "content": content}],
                "stream": True
            }
            
            with requests.post(f"{self.base_url}/chat/completions", 
                              json=payload, headers=self.headers, stream=True, timeout=60) as response:
                response.raise_for_status()
                
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            json_str = decoded_line[6:]
                            if json_str == '[DONE]':
                                break
                            
                            try:
                                data = json.loads(json_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_response += content
                                        yield content
                            except json.JSONDecodeError:
                                continue
                
                # 更新对话历史
                self.conversation_history.append({"role": "user", "content": f"图片: {image_path}, 查询: {query}"})
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            yield f"处理图片时出错: {e}"
    
    def stream_file_response(self, file_path: str, operation: str) -> Generator[str, None, None]:
        """流式处理文件响应"""
        try:
            if not os.path.exists(file_path):
                yield f"错误: 文件 '{file_path}' 不存在"
                return
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if operation == "email":
                prompt = f"请将以下内容修订为专业的英文邮件:\n\n{content}"
            elif operation == "revise":
                prompt = f"请修订以下内容，指出修改之处:\n\n{content}"
            else:
                prompt = content
            
            for chunk in self.stream_text_response(prompt):
                yield chunk
                
        except Exception as e:
            yield f"处理文件时出错: {e}"
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []
    
    def interactive_chat(self, use_cot: bool = False):
        """启动交互式对话模式（流式输出）"""
        print("启动交互式对话模式...")
        print("输入 'quit' 或 'exit' 退出对话")
        print("输入 'clear' 清除对话历史")
        print("输入 'image <路径>' 分析图片")
        print("输入 'file <路径> [操作]' 分析文件")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("您: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("结束对话")
                    break
                
                if user_input.lower() == 'clear':
                    self.clear_history()
                    print("对话历史已清除")
                    continue
                
                # 处理图片命令
                if user_input.startswith('image '):
                    parts = user_input.split(' ', 1)
                    if len(parts) < 2:
                        print("请提供图片路径")
                        continue
                    
                    image_path = parts[1].strip()
                    query = input("请输入关于此图片的问题 (直接回车使用默认分析): ").strip()
                    if not query:
                        query = "请描述这张图片的内容"
                    
                    print("AI: ", end='', flush=True)
                    for chunk in self.stream_image_response(image_path, query):
                        print(chunk, end='', flush=True)
                    print()  # 换行
                    continue
                
                # 处理文件命令
                if user_input.startswith('file '):
                    parts = user_input.split(' ', 1)
                    if len(parts) < 2:
                        print("请提供文件路径")
                        continue
                    
                    file_args = parts[1].strip().split(' ', 1)
                    file_path = file_args[0]
                    
                    operation = "default"
                    if len(file_args) > 1:
                        operation = file_args[1]
                    
                    print("AI: ", end='', flush=True)
                    for chunk in self.stream_file_response(file_path, operation):
                        print(chunk, end='', flush=True)
                    print()  # 换行
                    continue
                
                # 处理普通文本输入
                if user_input:
                    print("AI: ", end='', flush=True)
                    for chunk in self.stream_text_response(user_input, use_cot):
                        print(chunk, end='', flush=True)
                    print()  # 换行
                    
            except KeyboardInterrupt:
                print("\n结束对话")
                break
            except Exception as e:
                print(f"\n错误: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="(LLM) AGent for everything",
        usage="ag.py [-h] [-c] [-q] [-s] [-a] [-e] [-r] [instruct ...]"
    )
    
    # 选项参数
    parser.add_argument("-c", "--cot", action="store_true", 
                       help="启用思维链推理")
    parser.add_argument("-q", "--query", action="store_true",
                       help="使用参数查询标准输入内容")
    parser.add_argument("-s", "--slides", action="store_true",
                       help="生成和播放幻灯片")
    parser.add_argument("-a", "--agent", action="store_true",
                       help="与代理聊天（更强大但更慢）")
    parser.add_argument("-e", "--email", action="store_true",
                       help="修订邮件（翻译为英文）")
    parser.add_argument("-r", "--revise", action="store_true",
                       help="修订内容；产生diff形式")
    parser.add_argument("--api-key", help="DeepSeek API密钥")
    
    # 位置参数
    parser.add_argument("instruct", nargs="*", 
                       help="所有剩余参数")
    
    args = parser.parse_args()
    
    try:
        agent = DeepSeekAgent(args.api_key)
        
        # 处理标准输入
        if not sys.stdin.isatty() and args.query:
            stdin_content = sys.stdin.read().strip()
            if stdin_content:
                print("AI: ", end='', flush=True)
                for chunk in agent.stream_text_response(stdin_content, args.cot):
                    print(chunk, end='', flush=True)
                print()  # 换行
                return
        
        # 交互式对话模式
        if args.agent and not args.instruct:
            agent.interactive_chat(args.cot)
            return
        
        # 处理位置参数
        if args.instruct:
            input_content = " ".join(args.instruct)
            
            # 检查是否是文件路径
            if os.path.exists(input_content):
                file_path = input_content
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    # 处理图片
                    query = " ".join(args.instruct[1:]) if len(args.instruct) > 1 else None
                    print("AI: ", end='', flush=True)
                    for chunk in agent.stream_image_response(file_path, query):
                        print(chunk, end='', flush=True)
                    print()  # 换行
                else:
                    # 处理文本文件
                    operation = "default"
                    if args.email:
                        operation = "email"
                    elif args.revise:
                        operation = "revise"
                    
                    print("AI: ", end='', flush=True)
                    for chunk in agent.stream_file_response(file_path, operation):
                        print(chunk, end='', flush=True)
                    print()  # 换行
            else:
                # 处理文本输入
                if args.agent:
                    print("AI: ", end='', flush=True)
                    for chunk in agent.stream_text_response(input_content, args.cot):
                        print(chunk, end='', flush=True)
                    print()  # 换行
                elif args.email:
                    prompt = f"请将以下内容修订为专业的英文邮件:\n\n{input_content}"
                    print("AI: ", end='', flush=True)
                    for chunk in agent.stream_text_response(prompt):
                        print(chunk, end='', flush=True)
                    print()  # 换行
                elif args.revise:
                    prompt = f"请修订以下内容，指出修改之处:\n\n{input_content}"
                    print("AI: ", end='', flush=True)
                    for chunk in agent.stream_text_response(prompt):
                        print(chunk, end='', flush=True)
                    print()  # 换行
                else:
                    print("AI: ", end='', flush=True)
                    for chunk in agent.stream_text_response(input_content, args.cot):
                        print(chunk, end='', flush=True)
                    print()  # 换行
        
        # 如果没有参数，显示帮助
        if not args.instruct and not args.agent and sys.stdin.isatty():
            parser.print_help()
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
