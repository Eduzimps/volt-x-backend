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
    child_id=None
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
        def api(path, data=None, method=None, base=url, secret=token):
            headers={'X-Pyla-UI-Token':secret,'Content-Type':'application/json'}
            request=urllib.request.Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
            with opener.open(request,timeout=40) as response:return json.load(response)
        snapshot={'player_tag':'PYLQGR','player_name':'Synthetic audit fixture','stats':{
            'SHELLY':{'trophies':120,'power_level':5},'COLT':{'trophies':1500,'power_level':7}}}
        imported=api('/api/player/import',snapshot,'POST')
        assert imported['ok'] and imported['source']=='imported'
        pushed=api('/api/queue/push-all',{},'POST')
        assert pushed['added_count']==1 and pushed['items'][0]['brawler']=='shelly'
        assert pushed['items'][0]['trophies']==120
        debug=api('/api/settings/debug',{'debug_view':True,'advanced_debug_visuals':True},'PUT')
        assert debug['advanced_debug_visuals'] is True
        child_id=api('/api/profiles',{'name':'Native smoke profile'},'POST')['profile']['id']
        child=api('/api/profiles/'+child_id+'/launch',{},'POST')['profile']
        assert child['ready'] and child['running']
        with opener.open(child['url'],timeout=10) as response:child_html=response.read().decode()
        child_token=re.search(r'name="pyla-ui-token" content="([^"]+)"',child_html).group(1)
        child_payload=api('/api/bootstrap',base=child['url'],secret=child_token)
        assert child_payload['queue']==[] and child_payload['profiles']['enabled'] is False
        assert child_payload['auth']['premium'] is False
        api('/api/settings/general',{'run_for_minutes':37},'PUT',base=child['url'],secret=child_token)
        assert api('/api/bootstrap')['settings']['general']['run_for_minutes']!=37
        stopped=api('/api/profiles/'+child_id+'/stop',{},'POST')['profile']
        assert not stopped['running']
        child_id=None
        print(json.dumps({'exe_started':True,'ui_html':True,'bootstrap':True,'invalid_fps_rejected':True,'promotion_links_removed':True,'import_snapshot':True,'push_all':True,'debug_settings':True,'real_child_profile_started':True,'profile_queue_and_settings_isolated':True,'profile_stopped':True,'premium_entitlement':False,'game_automation_tested':False,'live_external_api_tested':False}))
    finally:
        if child_id:
            try:api('/api/profiles/'+child_id+'/stop',{},'POST')
            except Exception:pass
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
