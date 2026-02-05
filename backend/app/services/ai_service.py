"""AI model service layer"""

import os
from typing import Optional, Dict, Any, List
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.base import BaseChatModel
import httpx

from app.core.config import settings


class AIService:
    """AI model service using Ollama"""
    
    def __init__(self):
        self.model: Optional[BaseChatModel] = None
        self.model_name: str = ""
        self._init_ollama()
    
    def _init_ollama(self):
        """Initialize Ollama model"""
        print("[*] Initializing Ollama...")
        
        try:
            from langchain_community.chat_models import ChatOllama
            
            # Test if Ollama is running and model exists
            try:
                response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.0)
                if response.status_code == 200:
                    # Verify model exists
                    models = response.json().get('models', [])
                    model_names = [m['name'] for m in models]
                    
                    if settings.ollama_model not in model_names:
                        print(f"[-] Model '{settings.ollama_model}' not found")
                        print(f"    Available models: {', '.join(model_names)}")
                        return
                    
                    self.model = ChatOllama(
                        base_url=settings.ollama_base_url,
                        model=settings.ollama_model,
                        temperature=0.7,
                        format="json" if "cloud" in settings.ollama_model else None,
                    )
                    self.model_name = f"Ollama ({settings.ollama_model})"
                    print(f"[+] Using model: {self.model_name}")
                    print(f"[+] Model verified and ready")
                else:
                    print("[-] Ollama is not responding")
            except (httpx.ConnectError, httpx.TimeoutException):
                print("[-] Ollama not running")
                print("    Install from: https://ollama.ai")
                print(f"    Then run: ollama pull {settings.ollama_model}")
        except ImportError:
            print("[-] langchain-community not installed")
            print("    Run: poetry add langchain-community")
        except Exception as e:
            print(f"[-] Ollama initialization failed: {e}")
    
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate AI response using Ollama"""
        if not self.model:
            return "Error: Ollama not initialized. Please install and run Ollama from https://ollama.ai"
        
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            print(f"[DEBUG] Sending to Ollama: {settings.ollama_model}")
            response = await self.model.ainvoke(messages)
            print(f"[DEBUG] Response received: {len(response.content)} chars")
            return response.content
        
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Ollama call failed: {error_msg}")
            
            # Try direct API call as fallback
            try:
                print("[*] Trying direct Ollama API...")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    payload = {
                        "model": settings.ollama_model,
                        "prompt": f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt,
                        "stream": False
                    }
                    response = await client.post(
                        f"{settings.ollama_base_url}/api/generate",
                        json=payload
                    )
                    if response.status_code == 200:
                        result = response.json()
                        print("[+] Direct API call successful")
                        return result.get('response', 'No response from model')
                    else:
                        print(f"[-] Direct API failed: {response.status_code}")
                        return f"Error: Ollama request failed with status {response.status_code}"
            except Exception as fallback_error:
                print(f"[ERROR] Fallback also failed: {fallback_error}")
                return f"Error: Could not connect to Ollama. {error_msg}"
    
    async def detect_intent(self, user_input: str) -> str:
        """Detect user intent from input"""
        system_prompt = """You are an intent classifier. Classify the user's input into one of these intents:
- planning: Creating schedules, organizing tasks, time management
- learning: Studying, learning new topics, tracking progress
- remembering: Storing or retrieving information, notes
- rewriting: Improving text, changing tone, grammar correction
- decision_making: Comparing options, making choices
- general: General conversation or unclear intent

Respond with ONLY the intent name, nothing else."""
        
        try:
            intent = await self.generate_response(user_input, system_prompt)
            intent = intent.strip().lower()
            
            # Validate intent
            valid_intents = ["planning", "learning", "remembering", "rewriting", "decision_making", "general"]
            if intent not in valid_intents:
                return "general"
            
            return intent
        except Exception as e:
            print(f"Error detecting intent: {e}")
            return "general"
    
    async def rewrite_text(self, text: str, tone: str, instructions: Optional[str] = None) -> str:
        """Rewrite text with specified tone"""
        system_prompt = f"""You are a professional text editor. Rewrite the given text in a {tone} tone.
Make improvements to grammar, clarity, and style while maintaining the original meaning.
{f'Additional instructions: {instructions}' if instructions else ''}

Return ONLY the rewritten text, no explanations."""
        
        return await self.generate_response(text, system_prompt)
    
    async def analyze_decision(self, question: str, options: list) -> Dict[str, Any]:
        """Analyze decision options"""
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""Question: {question}

Options:
{options_text}

Analyze each option with pros and cons. Provide a balanced analysis but do NOT make the final decision for the user.
Format your response as JSON with this structure:
{{
    "analysis": "detailed analysis text",
    "option_details": [
        {{"option": "option 1", "pros": ["pro1", "pro2"], "cons": ["con1", "con2"]}},
        ...
    ],
    "considerations": ["important factor 1", "important factor 2"]
}}"""
        
        system_prompt = "You are a decision analysis assistant. Provide balanced, objective analysis without forcing decisions."
        
        response = await self.generate_response(prompt, system_prompt)
        
        # Try to parse as JSON, fallback to text if fails
        try:
            import json
            return json.loads(response)
        except:
            return {"analysis": response}


# Global AI service instance
ai_service = AIService()
