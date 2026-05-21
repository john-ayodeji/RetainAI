import json
import logging
import urllib.request
import urllib.error
from typing import Optional

from api.services import config, tools


def _call_openrouter(p: str, model: Optional[str] = None) -> str:
    model_name = model or config.OPENROUTER_MODEL
    payload = json.dumps({
        "model": model_name,
        "messages": [{"role": "user", "content": p}],
        "temperature": 0.2,
        "max_tokens": 400,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "HTTP-Referer": config.OPENROUTER_REFERER, 
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter HTTP {e.code}: {body}")

    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response shape: {data}") from e

    if not text:
        raise RuntimeError("OpenRouter returned an empty response.")
    return text


def call_llm(prompt: str, model: Optional[str] = None) -> str:
    """Call OpenRouter with a simple tool-invocation loop.

    If the model returns JSON containing {"tool": "name", "args": {...}},
    the tool is executed and its output is appended to the prompt for the
    next iteration. Repeats until a plain response is returned or max steps
    are reached.
    """
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    current_prompt = prompt
    for _ in range(4):
        try:
            resp_text = _call_openrouter(current_prompt, model=model)
        except Exception as e:
            logging.warning("OpenRouter call failed: %s", e)
            raise

        parsed = tools._safe_json_parse(resp_text) if hasattr(tools, "_safe_json_parse") else None
        if parsed and isinstance(parsed, dict) and "tool" in parsed:
            tool_res = tools.run_tool(parsed["tool"], parsed.get("args", {}))
            current_prompt = (
                current_prompt
                + "\n\n"
                + resp_text
                + f"\n\n[TOOL OUTPUT] {json.dumps(tool_res)}\n\n"
            )
            continue

        return resp_text

    return "LLM tool loop exceeded max steps"