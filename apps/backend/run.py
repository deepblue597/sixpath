#!/usr/bin/env python3
"""
Backend startup script for uvicorn
Run from workspace root: uv run apps/backend/run.py
"""
import sys
import os

# Add backend directory to path so relative imports work
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
