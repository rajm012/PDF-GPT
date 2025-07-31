#!/usr/bin/env python3
"""
PDF GPT - Complete Application Launcher
This script launches both backend and frontend with proper error handling
"""

import subprocess
import sys
import time
import threading
import os
import webbrowser
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check Python environment
    python_exe = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        print("❌ Virtual environment not found. Please run: python -m venv .venv")
        return False
    
    # Check Streamlit
    streamlit_exe = Path(__file__).parent / ".venv" / "Scripts" / "streamlit.exe"
    if not streamlit_exe.exists():
        print("❌ Streamlit not found. Please install requirements: pip install -r requirements.txt")
        return False
    
    print("✅ Prerequisites check passed!")
    return True

def start_backend():
    """Start the Flask backend"""
    print("🚀 Starting Flask backend...")
    
    python_exe = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    backend_script = Path(__file__).parent / "backend" / "app.py"
    
    # Change to backend directory
    os.chdir(Path(__file__).parent / "backend")
    
    # Start backend
    subprocess.run([str(python_exe), str(backend_script)])

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for backend to start
    
    streamlit_exe = Path(__file__).parent / ".venv" / "Scripts" / "streamlit.exe"
    frontend_script = Path(__file__).parent / "frontend" / "app.py"
    
    # Change back to project root
    os.chdir(Path(__file__).parent)
    
    # Start frontend
    subprocess.run([
        str(streamlit_exe), 
        "run", 
        str(frontend_script), 
        "--server.port", "8501",
        "--server.address", "localhost"
    ])

def open_browser():
    """Open browser after services start"""
    time.sleep(8)  # Wait for services to start
    try:
        webbrowser.open("http://localhost:8501")
        print("🌐 Opened browser at http://localhost:8501")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("📖 Please open http://localhost:8501 manually")

def main():
    """Main function"""
    print("📚 PDF GPT - Chat with Your Documents")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    print("🎯 Starting services...")
    
    try:
        # Start backend in background thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Start browser opener in background
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Start frontend (this will block)
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down PDF GPT...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
