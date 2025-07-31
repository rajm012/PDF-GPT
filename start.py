#!/usr/bin/env python3
"""
PDF GPT Startup Script
This script starts both the Flask backend and Streamlit frontend
"""

import subprocess
import sys
import time
import threading
import signal
import os
from pathlib import Path

def run_backend():
    """Run the Flask backend server"""
    print("🚀 Starting Flask backend...")
    backend_path = Path(__file__).parent / "backend" / "app.py"
    subprocess.run([sys.executable, str(backend_path)])

def run_frontend():
    """Run the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    # Wait a bit for backend to start
    time.sleep(3)
    frontend_path = Path(__file__).parent / "frontend" / "app.py"
    subprocess.run(["streamlit", "run", str(frontend_path), "--server.port", "8501"])

def main():
    """Main startup function"""
    print("📚 Starting PDF GPT Application...")
    print("=" * 50)
    
    # Check if required packages are installed
    try:
        import streamlit
        import flask
        import fitz  # PyMuPDF
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("⚠️  Ollama might not be ready")
    except:
        print("⚠️  Cannot connect to Ollama - make sure it's running")
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Start frontend (this will block)
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down PDF GPT...")
        sys.exit(0)

if __name__ == "__main__":
    main()
