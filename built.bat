@echo off
pyinstaller --onefile --distpath=. --noconsole .\transcriber.py
pause