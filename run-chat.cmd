@echo off
setlocal
cd /d "%~dp0"
echo Starting the MCP chat UI (Streamlit)...
echo It opens in your browser at http://localhost:8501
echo.
.venv\Scripts\python.exe -m streamlit run app.py
