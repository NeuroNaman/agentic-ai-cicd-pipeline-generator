"""
LLM tools — Unified interface for LLM calls with fallback, retry, and token tracking.

Supported providers (via LiteLLM):
- OpenAI (gpt-4o, gpt-4o-mini, etc.)
- Anthropic (claude-3-5-sonnet, claude-3-opus, etc.)
- Groq (llama-3.3-70b-versatile, mixtral-8x7b-32768, etc.)
- Google AI Studio / Gemini (gemini/gemini-2.0-flash, gemini/gemini-1.5-pro, etc.)
- Local models (ollama, vllm, etc.)

LiteLLM model prefixes:
- OpenAI:    "gpt-4o"
- Anthropic: "claude-3-5-sonnet-20241022"
- Groq:      "groq/llama-3.3-70b-versatile"
- Gemini:    "gemini/gemini-2.0-flash"
"""

from __future__ import annotations

import os
from typing import Any

import structlog
from litellm import acompletion

from src.config import get_settings

logger = structlog.get_logger()


class LLMClient:
    """
    Unified LLM client with provider fallback, retry logic, and token tracking.

    Uses LiteLLM under the hood for cross-provider compatibility.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self._configure_api_keys()

    def _configure_api_keys(self) -> None:
        """
        Set API key environment variables for LiteLLM.

        LiteLLM reads keys from env vars. We propagate them from our
        Pydantic settings so users only need to configure .env once.
        """
        key_map = {
            "OPENAI_API_KEY": self.settings.openai_api_key,
            "ANTHROPIC_API_KEY": self.settings.anthropic_api_key,
            "GROQ_API_KEY": self.settings.groq_api_key,
            "GEMINI_API_KEY": self.settings.google_api_key,  # LiteLLM uses GEMINI_API_KEY
            "GOOGLE_API_KEY": self.settings.google_api_key,  # Fallback for some integrations
        }
        for env_var, secret in key_map.items():
            if secret and env_var not in os.environ:
                os.environ[env_var] = secret.get_secret_value()

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt.
            system_prompt: System prompt.
            model: Override model name.
            temperature: Override temperature.
            max_tokens: Override max tokens.
            json_mode: Request JSON output.

        Returns:
            Generated text response.
        """
        model = model or self.settings.llm_model
        temperature = temperature if temperature is not None else self.settings.llm_temperature
        max_tokens = max_tokens or self.settings.llm_max_tokens

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await acompletion(**kwargs)

            # Track token usage
            usage = response.usage
            if usage:
                self.total_tokens_used += usage.total_tokens
                logger.debug(
                    "llm_tokens",
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total=usage.total_tokens,
                )

            # Check token budget
            if self.total_tokens_used > self.settings.llm_token_budget_per_run:
                logger.warning(
                    "token_budget_exceeded",
                    used=self.total_tokens_used,
                    budget=self.settings.llm_token_budget_per_run,
                )

            content = response.choices[0].message.content
            return content or ""

        except Exception as e:
            logger.warning("llm_primary_failed", model=model, error=str(e))

            # Fallback to secondary model
            if model != self.settings.llm_fallback_model:
                logger.info("llm_fallback", fallback_model=self.settings.llm_fallback_model)
                return await self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=self.settings.llm_fallback_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                )

            raise

    async def generate_pipeline_config(
        self,
        repo_context: str,
        plan_context: str,
        platform: str,
        similar_examples: list[str] | None = None,
    ) -> str:
        """
        Generate pipeline configuration using LLM with RAG context.

        Args:
            repo_context: Repository analysis summary.
            plan_context: Pipeline plan summary.
            platform: Target CI/CD platform.
            similar_examples: Similar pipeline configs from knowledge base.

        Returns:
            Generated pipeline configuration YAML.
        """
        system_prompt = f"""You are an expert DevOps engineer specializing in CI/CD pipeline configuration.
Generate a production-grade {platform} pipeline configuration based on the repository analysis and plan.

Rules:
- Use the latest stable versions of actions/tools
- Include proper caching for dependencies
- Use secrets references, never hardcode credentials
- Add meaningful step names
- Include error handling and notifications
- Follow platform best practices
- Output only valid YAML, no explanation"""

        examples_context = ""
        if similar_examples:
            examples_context = "\n\nSimilar successful pipeline examples for reference:\n"
            for i, example in enumerate(similar_examples[:3], 1):
                examples_context += f"\n--- Example {i} ---\n{example}\n"

        prompt = f"""Repository Analysis:
{repo_context}

Pipeline Plan:
{plan_context}
{examples_context}

Generate the complete {platform} pipeline configuration:"""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
        )

    async def diagnose_error(
        self,
        error_logs: str,
        pipeline_config: str,
        repo_context: str,
    ) -> dict[str, str]:
        """
        Use LLM to diagnose a pipeline error and suggest a fix.

        Returns:
            Dict with 'root_cause', 'fix_description', and 'fixed_config'.
        """
        system_prompt = """You are an expert DevOps engineer diagnosing CI/CD pipeline failures.
Analyze the error logs, identify the root cause, and generate a fix.

Respond in JSON format:
{
    "root_cause": "Brief description of the root cause",
    "fix_description": "Description of the fix to apply",
    "fixed_config": "The corrected pipeline configuration (full YAML)"
}"""

        prompt = f"""Error Logs:
{error_logs[:3000]}

Current Pipeline Configuration:
{pipeline_config[:3000]}

Repository Context:
{repo_context[:2000]}

Diagnose the error and provide a fix:"""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True,
            temperature=0.1,
        )

        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "root_cause": "Unable to parse LLM response",
                "fix_description": response[:500],
                "fixed_config": "",
            }


# Singleton
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
