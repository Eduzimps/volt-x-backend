"""Start the actual Windows executable and check its real loopback HTTP API."""
from pathlib import Path
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

package=Path(sys.argv[1]).resolve()
log=package.parent/'windows-exe-smoke.log'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
# Only loopback requests go through this opener; no remote network is bypassed.
with log.open('w',encoding='utf-8') as output:
    process=subprocess.Popen([str(package/'internal/pyla_main.exe'),'--headless'],cwd=package,stdout=output,stderr=subprocess.STDOUT)
    try:
        url=None
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('Executable exited early; see windows-exe-smoke.log')
            text=log.read_text(encoding='utf-8',errors='replace')
            match=re.search(r'http://127\.0\.0\.1:(\d+)',text)
            if match:
                candidate='http://127.0.0.1:'+match[1]
                try:
                    with opener.open(candidate,timeout=2) as response:html=response.read().decode()
                    url=candidate
                    break
                except (OSError,urllib.error.URLError):pass
            # Console output may be buffered; find_open_port starts at 5185.
            for port in range(5185,5190):
                try:
                    with opener.open(f'http://127.0.0.1:{port}',timeout=.3) as response:html=response.read().decode()
                    if 'pyla-ui-token' in html:url=f'http://127.0.0.1:{port}';break
                except (OSError,urllib.error.URLError):pass
            if url:break
            time.sleep(.3)
        if not url:raise RuntimeError('Executable did not serve the UI within 90 seconds')
        assert 'sidebarPremiumLink' not in html
        with opener.open(url+'/static/js/app.js',timeout=10) as response:frontend=response.read().decode()
        assert 'One setup today, more with Premium' not in frontend
        assert 'Unlock more automation' not in frontend
        token=re.search(r'name="pyla-ui-token" content="([^"]+)"',html).group(1)
        request=urllib.request.Request(url+'/api/bootstrap',headers={'X-Pyla-UI-Token':token})
        with opener.open(request,timeout=10) as response:payload=json.load(response)
        assert payload['app']['version']=='0.8.19'
        assert payload['auth']=={'required':False,'authenticated':True,'premium':False}
        request=urllib.request.Request(url+'/api/settings/general',data=b'{"max_fps":0}',headers={'X-Pyla-UI-Token':token,'Content-Type':'application/json'},method='PUT')
        try:opener.open(request,timeout=10);raise AssertionError('Invalid FPS was accepted')
        except urllib.error.HTTPError as error:assert error.code==400
        print(json.dumps({'exe_started':True,'ui_html':True,'bootstrap':True,'invalid_fps_rejected':True,'promotion_links_removed':True,'game_automation_tested':False}))
    finally:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
