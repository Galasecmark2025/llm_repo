@echo off
echo Running Virtual ENV
.venv\Scripts\activate

echo Running LLM Script
python llama_ai.python

echo Response Generated
pause