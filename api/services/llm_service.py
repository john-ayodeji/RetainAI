import json
import urllib.request
from typing import Optional
from api.services import config


def _extract_gemini_text(resp_json: dict) -> Optional[str]:
	# Try common response shapes
	if not isinstance(resp_json, dict):
		return None
	if "candidates" in resp_json and resp_json["candidates"]:
		cand = resp_json["candidates"][0]
		return cand.get("output") or cand.get("content") or cand.get("text")
	# Some responses place text under 'result' or 'output'
	if "result" in resp_json and isinstance(resp_json["result"], dict):
		return resp_json["result"].get("output") or resp_json["result"].get("content")
	return None


def call_llm(prompt: str, model: Optional[str] = None) -> str:
	"""Call Gemini via the Generative Language REST API when configured.

	Falls back to OpenAI if configured, otherwise returns the prompt
	so callers can inspect it during development.
	"""
	# Prefer Gemini if an API key is set
	if config.GEMINI_API_KEY:
		try:
			model_name = model or config.GEMINI_MODEL
			api_key = config.GEMINI_API_KEY
			url = f"https://generativelanguage.googleapis.com/v1beta2/{model_name}:generateText?key={api_key}"
			body = {
				"prompt": {"text": prompt},
				"temperature": 0.2,
				"maxOutputTokens": 400,
			}
			data = json.dumps(body).encode("utf-8")
			req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
			with urllib.request.urlopen(req, timeout=30) as resp:
				resp_json = json.load(resp)

			text = _extract_gemini_text(resp_json)
			if text:
				return text
			return f"Gemini returned unexpected payload: {json.dumps(resp_json)}"
		except Exception as e:
			return f"Gemini call failed: {e}"

	# Fall back to OpenAI if configured
	if config.OPENAI_API_KEY:
		try:
			import openai

			openai.api_key = config.OPENAI_API_KEY
			model_name = model or "gpt-4o-mini"
			resp = openai.ChatCompletion.create(
				model=model_name,
				messages=[{"role": "user", "content": prompt}],
				max_tokens=400,
			)
			return resp["choices"][0]["message"]["content"]
		except Exception as e:
			return f"OpenAI call failed: {e}"

	# Final fallback: return the prompt so developers can inspect it
	return f"LLM not configured. Prompt:\n\n{prompt}"

