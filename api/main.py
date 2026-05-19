from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import predict, explain, simulate


def create_app() -> FastAPI:
	app = FastAPI(title="RetainAI API")

	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	app.include_router(predict.router, prefix="/api")
	app.include_router(explain.router, prefix="/api")
	app.include_router(simulate.router, prefix="/api")

	@app.get("/")
	def root():
		return {"status": "ok", "service": "RetainAI API"}

	return app


app = create_app()
