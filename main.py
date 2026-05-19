"""Top-level app entrypoint for convenience.

This re-exports the FastAPI app defined in `api.main` so both
`uvicorn main:app` and `uvicorn api.main:app` can be used from the repo root.
"""

from api.main import app


def main():
    print("RetainAI API app is available as `app`.")


if __name__ == "__main__":
    main()
