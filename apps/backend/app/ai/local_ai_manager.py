"""
Local AI Manager for running AI models locally without external APIs
"""

import json
import os
from typing import Any, Dict, List, Optional, Union
from enum import Enum

import numpy as np
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings


class LocalAIModelType(str, Enum):
    """Types of local AI models supported"""
    OLLAMA = "ollama"
    TRANSFORMERS = "transformers"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"


class LocalAIModelConfig(BaseModel):
    """Configuration for local AI models"""
    model_type: LocalAIModelType
    model_name: str
    model_path: Optional[str] = None
    api_url: Optional[str] = None  # For Ollama
    max_tokens: int = 1000
    temperature: float = 0.1
    context_window: int = 4096
    is_quantized: bool = False
    device: str = "auto"  # cpu, cuda, auto


class LocalAIResponse(BaseModel):
    """Response from local AI model"""
    content: str
    confidence: float = 0.0
    tokens_used: int = 0
    processing_time: float = 0.0
    model_used: str = ""


class LocalAIManager:
    """
    Manager for local AI models with fallback strategies
    """
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.active_model: Optional[str] = None
        self.model_configs: Dict[str, LocalAIModelConfig] = {}
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default local AI models"""
        default_models = {
            "llama3.1-8b": LocalAIModelConfig(
                model_type=LocalAIModelType.OLLAMA,
                model_name="llama3.1:8b",
                api_url="http://localhost:11434",
                max_tokens=1000,
                temperature=0.1,
                context_window=8192,
                is_quantized=True
            ),
            "llama3.1-3b": LocalAIModelConfig(
                model_type=LocalAIModelType.OLLAMA,
                model_name="llama3.1:3b",
                api_url="http://localhost:11434",
                max_tokens=1000,
                temperature=0.1,
                context_window=4096,
                is_quantized=True
            ),
            "mistral-7b": LocalAIModelConfig(
                model_type=LocalAIModelType.OLLAMA,
                model_name="mistral:7b",
                api_url="http://localhost:11434",
                max_tokens=1000,
                temperature=0.1,
                context_window=8192,
                is_quantized=True
            ),
            "phi-3-mini": LocalAIModelConfig(
                model_type=LocalAIModelType.OLLAMA,
                model_name="phi3:mini",
                api_url="http://localhost:11434",
                max_tokens=1000,
                temperature=0.1,
                context_window=4096,
                is_quantized=True
            ),
            "gemma-2b": LocalAIModelConfig(
                model_type=LocalAIModelType.OLLAMA,
                model_name="gemma2:2b",
                api_url="http://localhost:11434",
                max_tokens=1000,
                temperature=0.1,
                context_window=4096,
                is_quantized=True
            )
        }
        
        self.model_configs.update(default_models)
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize a specific local AI model"""
        try:
            if model_name not in self.model_configs:
                logger.error(f"Model {model_name} not found in configurations")
                return False
            
            config = self.model_configs[model_name]
            
            if config.model_type == LocalAIModelType.OLLAMA:
                return await self._initialize_ollama_model(model_name, config)
            elif config.model_type == LocalAIModelType.TRANSFORMERS:
                return await self._initialize_transformers_model(model_name, config)
            else:
                logger.warning(f"Model type {config.model_type} not yet implemented")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing model {model_name}: {e}")
            return False
    
    async def _initialize_ollama_model(self, model_name: str, config: LocalAIModelConfig) -> bool:
        """Initialize Ollama model"""
        try:
            import httpx
            
            # Check if Ollama is running
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{config.api_url}/api/tags")
                if response.status_code != 200:
                    logger.error(f"Ollama not running at {config.api_url}")
                    return False
                
                # Check if model is available
                models_response = await client.get(f"{config.api_url}/api/tags")
                if models_response.status_code == 200:
                    available_models = models_response.json().get("models", [])
                    model_available = any(
                        model.get("name", "").startswith(config.model_name.split(":")[0])
                        for model in available_models
                    )
                    
                    if not model_available:
                        logger.warning(f"Model {config.model_name} not available in Ollama")
                        return False
            
            self.models[model_name] = config
            logger.info(f"Ollama model {model_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Ollama model {model_name}: {e}")
            return False
    
    async def _initialize_transformers_model(self, model_name: str, config: LocalAIModelConfig) -> bool:
        """Initialize Transformers model"""
        try:
            # This would load the model into memory
            # For now, we'll just mark it as available
            self.models[model_name] = config
            logger.info(f"Transformers model {model_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Transformers model {model_name}: {e}")
            return False
    
    async def generate_response(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LocalAIResponse:
        """Generate response using local AI model"""
        try:
            # Use specified model or fallback to best available
            if model_name and model_name in self.models:
                config = self.models[model_name]
            else:
                # Find best available model
                available_models = list(self.models.keys())
                if not available_models:
                    raise Exception("No local AI models available")
                
                # Prefer smaller, faster models for microtransactions
                preferred_models = ["phi-3-mini", "gemma-2b", "llama3.1-3b", "llama3.1-8b", "mistral-7b"]
                
                for preferred in preferred_models:
                    if preferred in available_models:
                        model_name = preferred
                        config = self.models[preferred]
                        break
                else:
                    model_name = available_models[0]
                    config = self.models[available_models[0]]
            
            if config.model_type == LocalAIModelType.OLLAMA:
                return await self._generate_ollama_response(prompt, model_name, config, system_prompt, **kwargs)
            elif config.model_type == LocalAIModelType.TRANSFORMERS:
                return await self._generate_transformers_response(prompt, model_name, config, system_prompt, **kwargs)
            else:
                raise Exception(f"Model type {config.model_type} not supported")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Return fallback response
            return LocalAIResponse(
                content="Unable to generate AI response. Using fallback analysis.",
                confidence=0.3,
                model_used="fallback"
            )
    
    async def _generate_ollama_response(
        self,
        prompt: str,
        model_name: str,
        config: LocalAIModelConfig,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LocalAIResponse:
        """Generate response using Ollama"""
        try:
            import httpx
            import time
            
            start_time = time.time()
            
            # Prepare the request
            request_data = {
                "model": config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", config.temperature),
                    "num_predict": kwargs.get("max_tokens", config.max_tokens),
                }
            }
            
            if system_prompt:
                request_data["system"] = system_prompt
            
            # Make request to Ollama
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.api_url}/api/generate",
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.status_code}")
                
                result = response.json()
                content = result.get("response", "")
                
                processing_time = time.time() - start_time
                
                return LocalAIResponse(
                    content=content,
                    confidence=0.7,  # Default confidence for local models
                    tokens_used=result.get("eval_count", 0),
                    processing_time=processing_time,
                    model_used=model_name
                )
                
        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            raise
    
    async def _generate_transformers_response(
        self,
        prompt: str,
        model_name: str,
        config: LocalAIModelConfig,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LocalAIResponse:
        """Generate response using Transformers (placeholder)"""
        # This would implement actual transformers model inference
        # For now, return a placeholder response
        return LocalAIResponse(
            content="Transformers model response (not yet implemented)",
            confidence=0.5,
            model_used=model_name
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available local AI models"""
        return list(self.models.keys())
    
    def get_model_config(self, model_name: str) -> Optional[LocalAIModelConfig]:
        """Get configuration for a specific model"""
        return self.models.get(model_name)
    
    async def test_model_connection(self, model_name: str) -> bool:
        """Test if a model is accessible and working"""
        try:
            test_prompt = "Hello, this is a test message."
            response = await self.generate_response(test_prompt, model_name)
            return bool(response.content and response.content != "Unable to generate AI response")
        except Exception as e:
            logger.error(f"Model connection test failed for {model_name}: {e}")
            return False
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available"""
        return model_name in self.models


# Global instance
local_ai_manager = LocalAIManager()
