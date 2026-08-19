from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], system_prompt: str = None) -> Dict[str, Any]:
        pass