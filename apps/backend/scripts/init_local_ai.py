#!/usr/bin/env python3
"""
Script to initialize local AI models for DerivWorkFlow
"""

import asyncio
import os
import sys
import httpx
from loguru import logger

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ai.local_ai_manager import local_ai_manager
from app.core.config import settings


async def check_ollama_status():
    """Check if Ollama is running and accessible"""
    try:
        ollama_host = settings.ollama_host
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_host}/api/tags", timeout=10.0)
            if response.status_code == 200:
                logger.info(f"✅ Ollama is running at {ollama_host}")
                return True
            else:
                logger.error(f"❌ Ollama responded with status {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Ollama at {settings.ollama_host}: {e}")
        return False


async def list_available_models():
    """List models available in Ollama"""
    try:
        ollama_host = settings.ollama_host
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_host}/api/tags", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if models:
                    logger.info("📋 Available models in Ollama:")
                    for model in models:
                        logger.info(f"  - {model.get('name', 'Unknown')}")
                    return [model.get('name', '').split(':')[0] for model in models]
                else:
                    logger.warning("⚠️  No models found in Ollama")
                    return []
            else:
                logger.error(f"❌ Failed to get models from Ollama: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"❌ Error listing models: {e}")
        return []


async def pull_model(model_name: str):
    """Pull a model to Ollama"""
    try:
        ollama_host = settings.ollama_host
        logger.info(f"📥 Pulling model: {model_name}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ollama_host}/api/pull",
                json={"name": model_name},
                timeout=300.0  # 5 minutes timeout for model download
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully pulled {model_name}")
                return True
            else:
                logger.error(f"❌ Failed to pull {model_name}: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Error pulling {model_name}: {e}")
        return False


async def initialize_default_models():
    """Initialize default models for the application"""
    default_models = [
        "phi3:mini",      # Small, fast model for microtransactions
        "gemma2:2b",      # Another small, efficient model
        "llama3.1:3b",    # Medium-sized model
    ]
    
    logger.info("🚀 Initializing default AI models...")
    
    # Check Ollama status first
    if not await check_ollama_status():
        logger.error("❌ Ollama is not available. Please start Ollama first.")
        return False
    
    # Get currently available models
    available_models = await list_available_models()
    
    # Pull missing models
    for model in default_models:
        model_base = model.split(':')[0]
        if model_base not in available_models:
            logger.info(f"📥 Model {model} not found, pulling...")
            success = await pull_model(model)
            if not success:
                logger.warning(f"⚠️  Failed to pull {model}, continuing with other models...")
        else:
            logger.info(f"✅ Model {model} already available")
    
    # Initialize models in the local AI manager
    logger.info("🔧 Initializing models in Local AI Manager...")
    for model_name in ["phi-3-mini", "gemma-2b", "llama3.1-3b"]:
        try:
            success = await local_ai_manager.initialize_model(model_name)
            if success:
                logger.info(f"✅ Initialized {model_name}")
            else:
                logger.warning(f"⚠️  Failed to initialize {model_name}")
        except Exception as e:
            logger.error(f"❌ Error initializing {model_name}: {e}")
    
    return True


async def test_models():
    """Test the initialized models"""
    logger.info("🧪 Testing initialized models...")
    
    available_models = local_ai_manager.get_available_models()
    if not available_models:
        logger.warning("⚠️  No models available for testing")
        return
    
    test_prompt = "Hello, this is a test message for trading analysis."
    
    for model_name in available_models:
        try:
            logger.info(f"🧪 Testing {model_name}...")
            response = await local_ai_manager.generate_response(
                prompt=test_prompt,
                model_name=model_name,
                max_tokens=50
            )
            
            if response.content and response.content != "Unable to generate AI response":
                logger.info(f"✅ {model_name} is working correctly")
                logger.debug(f"   Response: {response.content[:100]}...")
            else:
                logger.warning(f"⚠️  {model_name} returned empty response")
                
        except Exception as e:
            logger.error(f"❌ Error testing {model_name}: {e}")


async def main():
    """Main function"""
    logger.info("🤖 DerivWorkFlow Local AI Initialization")
    logger.info("=" * 50)
    
    # Check if local AI is enabled
    if not settings.local_ai_enabled:
        logger.warning("⚠️  Local AI is disabled in settings")
        logger.info("   Set LOCAL_AI_ENABLED=true to enable local AI")
        return
    
    # Initialize models
    success = await initialize_default_models()
    if not success:
        logger.error("❌ Failed to initialize models")
        return
    
    # Test models
    await test_models()
    
    logger.info("=" * 50)
    logger.info("✅ Local AI initialization completed!")
    logger.info(f"📊 Available models: {local_ai_manager.get_available_models()}")
    logger.info(f"🎯 Default model: {settings.default_ai_model}")
    logger.info(f"🔧 AI Provider: {getattr(settings, 'ai_provider', 'local')}")


if __name__ == "__main__":
    asyncio.run(main())
