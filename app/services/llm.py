from groq import Groq
from typing import Dict, Any
import json
from app.rag.llm import LLMProvider
from app.core.config import settings
from app.core.logging import logger


class GroqLLMProvider(LLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.groq_api_key
        self.model_name = model_name or settings.groq_model
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        self.client = Groq(api_key=self.api_key)
        logger.info(f"Initialized Groq LLM with model: {self.model_name}")
    
    async def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 2048),
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            else:
                logger.warning("Groq returned empty response")
                return ""
        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            raise
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], system_prompt: str = None) -> Dict[str, Any]:
        try:
            schema_prompt = f"""You must respond with a valid JSON object that matches this schema:
{json.dumps(schema, indent=2)}

{prompt}"""

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": schema_prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            
            if response.choices and response.choices[0].message.content:
                return json.loads(response.choices[0].message.content.strip())
            else:
                logger.warning("Groq returned empty structured response")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Groq structured generation error: {e}")
            raise


def get_llm_provider() -> LLMProvider:
    return GroqLLMProvider()