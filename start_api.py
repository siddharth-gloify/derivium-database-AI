"""
Start the fetcherio web UI.
Usage: python start_api.py
Then open http://localhost:8000
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
