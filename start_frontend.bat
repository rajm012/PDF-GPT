@echo off
echo Starting PDF GPT Frontend...
cd /d "E:\9. Run In VS\PDF-GPT"
"E:\9. Run In VS\PDF-GPT\.venv\Scripts\streamlit.exe" run frontend/app.py --server.port 8501
pause
