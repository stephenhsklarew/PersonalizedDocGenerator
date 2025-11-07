"""
AI Model integration for multiple providers
Supports: Anthropic Claude, OpenAI GPT, Google Gemini
"""

import os
from typing import Optional
from anthropic import Anthropic
import openai
import google.generativeai as genai


class AIModelManager:
    """Manages different AI models from various providers"""

    # Available models
    MODELS = {
        # Anthropic Claude models
        'claude-3-5-sonnet': {'provider': 'anthropic', 'model': 'claude-sonnet-4-20250514', 'name': 'Claude 3.5 Sonnet (Latest)'},
        'claude-3-5-haiku': {'provider': 'anthropic', 'model': 'claude-3-5-haiku-20241022', 'name': 'Claude 3.5 Haiku (Fast)'},
        'claude-3-opus': {'provider': 'anthropic', 'model': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus (Most Capable)'},

        # OpenAI GPT models
        'gpt-4': {'provider': 'openai', 'model': 'gpt-4-turbo-preview', 'name': 'GPT-4 Turbo (Most Capable)'},
        'gpt-4o': {'provider': 'openai', 'model': 'gpt-4o', 'name': 'GPT-4o (Multimodal)'},
        'gpt-3.5-turbo': {'provider': 'openai', 'model': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo (Fast & Efficient)'},

        # Google Gemini models
        'gemini-pro': {'provider': 'gemini', 'model': 'gemini-pro', 'name': 'Gemini Pro'},
        'gemini-1.5-pro': {'provider': 'gemini', 'model': 'gemini-1.5-pro-latest', 'name': 'Gemini 1.5 Pro (Latest)'},
        'gemini-1.5-flash': {'provider': 'gemini', 'model': 'gemini-1.5-flash-latest', 'name': 'Gemini 1.5 Flash (Fast)'},
    }

    def __init__(self, model_key: str = 'claude-3-5-sonnet'):
        """Initialize AI Model Manager"""
        self.model_key = model_key
        self.model_info = self.MODELS.get(model_key)

        if not self.model_info:
            raise ValueError(f"Unknown model: {model_key}")

        self.provider = self.model_info['provider']
        self.model = self.model_info['model']
        self.name = self.model_info['name']

        # Initialize appropriate client
        self._init_client()

    def _init_client(self):
        """Initialize the appropriate AI client based on provider"""
        if self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found. Please set it in your .env file.\n"
                    "Get your API key from https://console.anthropic.com/"
                )
            self.client = Anthropic(api_key=api_key)

        elif self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found. Please set it in your .env file.\n"
                    "Get your API key from https://platform.openai.com/api-keys"
                )
            openai.api_key = api_key
            self.client = openai

        elif self.provider == 'gemini':
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY not found. Please set it in your .env file.\n"
                    "Get your API key from https://makersuite.google.com/app/apikey"
                )
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)

    def generate(self, prompt: str, max_tokens: int = 16000) -> str:
        """Generate content using the selected model"""
        try:
            if self.provider == 'anthropic':
                return self._generate_anthropic(prompt, max_tokens)
            elif self.provider == 'openai':
                return self._generate_openai(prompt, max_tokens)
            elif self.provider == 'gemini':
                return self._generate_gemini(prompt)
        except Exception as e:
            raise Exception(f"Error generating with {self.name}: {str(e)}")

    def _generate_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Generate using Anthropic Claude"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        """Generate using OpenAI GPT"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def _generate_gemini(self, prompt: str) -> str:
        """Generate using Google Gemini"""
        response = self.client.generate_content(prompt)
        return response.text

    @classmethod
    def get_available_models(cls) -> dict:
        """Get list of available models"""
        return cls.MODELS

    @classmethod
    def list_models_by_provider(cls) -> dict:
        """List models grouped by provider"""
        providers = {}
        for key, info in cls.MODELS.items():
            provider = info['provider']
            if provider not in providers:
                providers[provider] = []
            providers[provider].append({
                'key': key,
                'name': info['name'],
                'model': info['model']
            })
        return providers

    @classmethod
    def get_model_display_list(cls) -> list:
        """Get formatted list for display in UI"""
        models = []
        by_provider = cls.list_models_by_provider()

        for provider in ['anthropic', 'openai', 'gemini']:
            if provider in by_provider:
                provider_name = {
                    'anthropic': 'Anthropic Claude',
                    'openai': 'OpenAI GPT',
                    'gemini': 'Google Gemini'
                }[provider]

                models.append(f"\n{provider_name}:")
                for model in by_provider[provider]:
                    models.append(f"  • {model['key']}: {model['name']}")

        return models
