@echo off
setlocal
cd /d "%~dp0"
echo Starting MCP Inspector v2 with the catalog in this folder...
echo UI opens at http://localhost:6274  (the browser auto-launches)
echo.
npx @modelcontextprotocol/inspector --catalog "%cd%\inspector.json"
