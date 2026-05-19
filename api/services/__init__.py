"""Services package

Avoid importing heavy submodules at package import time so tests and
lightweight imports (like the LLM service) don't require optional
dependencies such as pandas or shap to be installed.
"""

__all__ = ["config", "llm_service", "shap_service", "schemas"]

