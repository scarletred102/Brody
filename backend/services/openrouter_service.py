import os
import json
import importlib
import logging
from typing import List, Optional

# Dynamically resolve OpenAI client to avoid static import errors if not installed yet
OpenAI = None
_openai_mod = None
try:
    _openai_mod = importlib.import_module("openai")
    OpenAI = getattr(_openai_mod, "OpenAI", None)
except Exception:
    OpenAI = None


class OpenRouterService:
    """
    Unified AI service using OpenRouter for multiple LLM access.
    Falls back gracefully when API is unavailable or not configured.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.default_model = os.getenv("DEFAULT_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "mistralai/mistral-7b-instruct:free")

        self.client = None
        if OpenAI and self.api_key:
            try:
                # Add recommended headers for OpenRouter
                default_headers = {
                    "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", "http://localhost:9000"),
                    "X-Title": os.getenv("OPENROUTER_TITLE", "Brody Dev"),
                }
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    default_headers=default_headers,
                )
            except Exception:
                self.client = None

        # Only-free model enforcement / allowlist
        self.only_free = os.getenv("ONLY_FREE_MODELS", "true").lower() in ("1", "true", "yes")
        allowlist = os.getenv("FREE_MODEL_ALLOWLIST", "meta-llama/llama-3.1-8b-instruct:free,mistralai/mistral-7b-instruct:free,nousresearch/nous-hermes-2-mistral-7b:free")
        self.free_allowlist = [m.strip() for m in allowlist.split(",") if m.strip()]

        # Task → model mapping (will be validated against allowlist if only_free)
        self.model_config = {
            "email_classification": os.getenv("EMAIL_MODEL", self.default_model),
            "task_generation": os.getenv("TASK_MODEL", self.default_model),
            "meeting_brief": os.getenv("MEETING_MODEL", self.default_model),
            "summarization": os.getenv("SUMMARY_MODEL", self.fallback_model),
        }

    def available(self) -> bool:
        return self.client is not None

    def _select_model(self, requested: Optional[str]) -> Optional[str]:
        """Pick a model honoring only-free and allowlist settings."""
        candidate = requested or self.default_model
        if not self.only_free:
            return candidate
        # Enforce free allowlist
        if candidate in self.free_allowlist:
            return candidate
        # Try to find a close alternative from allowlist
        return self.free_allowlist[0] if self.free_allowlist else None

    def _chat(self, messages: List[dict], model: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 800) -> Optional[str]:
        logger = logging.getLogger("openrouter")
        if not self.client:
            logger.debug("OpenRouter client not initialized; skipping AI call")
            return None
        def _messages_to_prompt(msgs: List[dict]) -> str:
            parts = []
            for m in msgs:
                role = m.get("role", "user")
                content = m.get("content", "")
                parts.append(f"{role.upper()}: {content}")
            return "\n\n".join(parts)

        def _call(mdl: str) -> Optional[str]:
            # First try chat.completions
            resp = self.client.chat.completions.create(
                model=mdl,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            try:
                content = resp.choices[0].message.content
            except Exception:
                content = None
            if content and isinstance(content, str) and content.strip():
                return content
            # Fallback to responses.create aggregation
            try:
                prompt = _messages_to_prompt(messages)
                r2 = self.client.responses.create(model=mdl, input=prompt, max_output_tokens=max_tokens)
                text = getattr(r2, "output_text", None)
                if not text:
                    # best-effort extraction
                    out = []
                    for item in getattr(r2, "output", []) or []:
                        if getattr(item, "type", None) == "message":
                            for c in getattr(getattr(item, "content", None), "__iter__", lambda: [])():
                                t = getattr(c, "text", None)
                                if t and getattr(t, "value", None):
                                    out.append(t.value)
                    text = "\n".join(out)
                if text and text.strip():
                    return text
            except Exception:
                pass
            return None
        # Primary model
        try:
            use_model = self._select_model(model)
            if not use_model:
                logger.warning("No allowed model available for request")
                return None
            out = _call(use_model)
            if out:
                return out
            logger.info(f"Primary model '{use_model}' returned empty; trying fallback")
        except Exception as e:
            logger.warning(f"Primary model call failed: {e}")
        # Fallback model
        try:
            fb_model = self._select_model(self.fallback_model)
            if not fb_model:
                logger.warning("No allowed fallback model available")
                return None
            out = _call(fb_model)
            if out:
                return out
            logger.error("Fallback model also returned empty content")
            # Try all allowed free models as a last resort
            tried = set([use_model, fb_model]) if 'use_model' in locals() else set([fb_model])
            for mdl in self.free_allowlist:
                if mdl in tried:
                    continue
                try:
                    out = _call(mdl)
                    if out:
                        logger.info(f"Succeeded with alternate model '{mdl}'")
                        return out
                except Exception as e:
                    logger.debug(f"Alternate model '{mdl}' failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Fallback model call failed: {e}")
            return None

    def classify_email(self, subject: str, body: str, sender: str) -> Optional[dict]:
        messages = [
            {"role": "system", "content": "You are an expert email triage assistant. Return ONLY valid JSON."},
            {"role": "user", "content": (
                "Analyze the email and return JSON with keys: urgency (high|medium|low), "
                "category (work|personal|promotional|newsletter|meeting|task), sentiment (positive|neutral|negative), "
                "action (response_needed|fyi|action_item|meeting_invite), summary (<=25 words).\n\n"
                f"Subject: {subject}\nFrom: {sender}\nBody: {body[:2000]}"
            )}
        ]
        out = self._chat(messages, model=self.model_config["email_classification"], temperature=0.1, max_tokens=400)
        if not out:
            return None
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            # Best-effort parsing for common wrappers
            try:
                start = out.find("{")
                end = out.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(out[start:end])
            except Exception:
                pass
            return None

    def suggest_tasks(self, subject: str, body: str, sender: str) -> Optional[List[dict]]:
        messages = [
            {"role": "system", "content": "You are a productivity expert. Return ONLY a JSON array of tasks."},
            {"role": "user", "content": (
                "From the email, generate 1-3 actionable tasks as a JSON array. Each task has: "
                "title, description, priority (high|medium|low), estimated_minutes (int), due_date (ISO8601 or null).\n\n"
                f"Subject: {subject}\nFrom: {sender}\nBody: {body[:2000]}"
            )}
        ]
        out = self._chat(messages, model=self.model_config["task_generation"], temperature=0.3, max_tokens=700)
        if not out:
            return None
        try:
            data = json.loads(out)
            return data if isinstance(data, list) else None
        except json.JSONDecodeError:
            try:
                start = out.find("[")
                end = out.rfind("]") + 1
                if start >= 0 and end > start:
                    return json.loads(out[start:end])
            except Exception:
                pass
            return None

    def meeting_brief(self, title: str, when_iso: str, attendees: List[str], description: str = "", related_summaries: Optional[List[str]] = None) -> Optional[str]:
        context = f"Title: {title}\nTime: {when_iso}\nAttendees: {', '.join(attendees)}\nDescription: {description}\n"
        if related_summaries:
            context += "\nRelated recent emails (summaries):\n- " + "\n- ".join(related_summaries[:5])
        messages = [
            {"role": "system", "content": "You are an executive assistant. Return a concise bullet-style meeting brief."},
            {"role": "user", "content": (
                "Create a meeting brief with sections: Objective, Agenda (3-5 bullets), Key Context, Pre-reads, "
                "Questions to Ask, Expected Outcomes. Keep it under 250 words.\n\n" + context
            )}
        ]
        return self._chat(messages, model=self.model_config["meeting_brief"], temperature=0.4, max_tokens=800)
