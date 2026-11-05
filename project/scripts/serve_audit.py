"""Run the real local UI for browser validation; no emulator is started."""
import os
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
os.chdir(root)
sys.path.insert(0,str(root))
from main import pyla_main
from webui import create_app

app=create_app(pyla_main, start_discord_bot=False)
app.run(host='127.0.0.1',port=5199,debug=False,use_reloader=False)
