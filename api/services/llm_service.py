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
	if "result" in resp_json and isinstance(resp_json["result"], dict):
		return resp_json["result"].get("output") or resp_json["result"].get("content")
	return None


def _call_gemini(p: str, model: Optional[str] = None) -> str:
	model_name = model or config.GEMINI_MODEL
	api_key = config.GEMINI_API_KEY
	url = f"https://generativelanguage.googleapis.com/v1beta2/{model_name}:generateText?key={api_key}"
	body = {
		"prompt": {"text": p},
		"temperature": 0.2,
		"maxOutputTokens": 400,
	}
	data = json.dumps(body).encode("utf-8")
	req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
	with urllib.request.urlopen(req, timeout=30) as resp:
		resp_json = json.load(resp)
	text = _extract_gemini_text(resp_json)
	return text or json.dumps(resp_json)


def _call_openai(p: str, model: Optional[str] = None) -> str:
	import openai

	openai.api_key = config.OPENAI_API_KEY
	model_name = model or "gpt-4o-mini"
	resp = openai.ChatCompletion.create(
		model=model_name,
		messages=[{"role": "user", "content": p}],
		max_tokens=400,
	)
	return resp["choices"][0]["message"]["content"]


def call_llm(prompt: str, model: Optional[str] = None) -> str:
	"""Call Gemini/OpenAI and support a simple tool-invocation loop.

	The LLM may return a JSON object containing {"tool": "name", "args": {...}}.
	This function will execute the tool via `api.services.tools.run_tool` and then
	re-query the LLM with the tool output appended. The loop repeats until the LLM
	returns a non-tool response.
	"""

	# lazy import to avoid heavy deps during module import
	from api.services import tools

	current_prompt = prompt
	for step in range(4):
		# choose backend
		if config.GEMINI_API_KEY:
			try:
				resp_text = _call_gemini(current_prompt, model=model)
			except Exception as e:
				return f"Gemini call failed: {e}"
		elif config.OPENAI_API_KEY:
			try:
				resp_text = _call_openai(current_prompt, model=model)
			except Exception as e:
				return f"OpenAI call failed: {e}"
		else:
			return f"LLM not configured. Prompt:\n\n{prompt}"

		# try parse tool request
		parsed = tools._safe_json_parse(resp_text) if hasattr(tools, "_safe_json_parse") else None
		if parsed and isinstance(parsed, dict) and "tool" in parsed:
			tool_name = parsed.get("tool")
			args = parsed.get("args", {})
			tool_res = tools.run_tool(tool_name, args)
			# append tool output to the prompt and continue the loop
			tool_block = f"\n\n[TOOL OUTPUT] {json.dumps(tool_res)}\n\n"
			current_prompt = current_prompt + "\n\n" + resp_text + tool_block
			continue

		# no tool requested — return LLM's response
		return resp_text

	return "LLM tool loop exceeded max steps"


