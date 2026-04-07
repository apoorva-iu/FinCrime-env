from main import app

def main():
	"""Return the ASGI app for multi-mode deployment validators.

	When executed directly, start a local uvicorn server for manual testing.
	"""
	return app


if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="0.0.0.0", port=7860)
