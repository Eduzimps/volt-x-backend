"""Exercise the real browser UI against a local audit server (no game worker)."""
import json
import os
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright, expect

base=os.environ.get('PYLA_AUDIT_URL','http://127.0.0.1:5199')
out=Path(os.environ.get('PYLA_AUDIT_REPORTS',str(Path(__file__).resolve().parents[1]/'test-results')))
out.mkdir(parents=True,exist_ok=True)
errors=[]
failed_assets=[]
checks=[]
with sync_playwright() as p:
    executable=os.environ.get('CHROMIUM_EXECUTABLE')
    browser=p.chromium.launch(executable_path=executable,headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.on('response',lambda response:failed_assets.append({'url':response.url,'status':response.status}) if response.status>=400 and '/api/assets/' in response.url else None)
    # The app must remain usable without the optional Google Fonts service.
    page.route('https://fonts.googleapis.com/**',lambda route:route.abort())
    page.route('https://fonts.gstatic.com/**',lambda route:route.abort())
    page.goto(base,wait_until='domcontentloaded')
    page.wait_for_function('Boolean(state.bootstrap)',timeout=20000)
    for view in ('dashboard','queue','playstyles','history','logs','settings'):
        page.locator(f'.nav-item[data-view="{view}"]').click()
        expect(page.locator(f'#view-{view}')).to_be_visible()
        checks.append('navigation:'+view)
        page.screenshot(path=str(out/(view+'.png')),full_page=True)
    selector='input[data-setting-section="general"][data-setting-key="run_for_minutes"]'
    original=page.locator(selector).input_value()
    page.locator(selector).fill('12')
    page.locator(selector).dispatch_event('change')
    page.wait_for_function('state.bootstrap.settings.general.run_for_minutes === 12')
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function('Boolean(state.bootstrap)')
    assert page.evaluate('state.bootstrap.settings.general.run_for_minutes')==12
    page.locator('.nav-item[data-view="settings"]').click()
    page.locator(selector).fill(original)
    page.locator(selector).dispatch_event('change')
    page.wait_for_function('(expected) => String(state.bootstrap.settings.general.run_for_minutes) === expected',arg=original)
    checks.append('settings:autosave-and-reload')
    page.locator('.nav-item[data-view="queue"]').click()
    card=page.locator('[data-brawler]').first
    selected=card.get_attribute('data-brawler')
    card.click()
    expect(page.locator('#saveQueueItemBtn')).to_be_visible()
    page.locator('#saveQueueItemBtn').click()
    page.wait_for_function('(name) => state.bootstrap.queue.some(x => x.brawler === name)',arg=selected)
    checks.append('queue:add-via-button')
    # Use the actual protected API to remove only the entry created by this check.
    response=page.evaluate("""async(name) => fetch('/api/queue/'+encodeURIComponent(name),{method:'DELETE',headers:{'X-Pyla-UI-Token':document.querySelector('meta[name="pyla-ui-token"]').content}}).then(r=>r.status)""",selected)
    assert response==200
    page.locator('.nav-item[data-view="playstyles"]').click()
    assert page.locator('#playstyleLibrary').inner_text().strip()
    checks.append('playstyles:library')
    page.locator('.nav-item[data-view="dashboard"]').click()
    page.locator('.premium-locked-action:visible').first.click()
    expect(page.locator('#premiumFeatureModal')).to_be_visible()
    checks.append('premium:existing-modal-kept')
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function('Boolean(state.bootstrap)')
    with page.expect_navigation(wait_until='domcontentloaded'):
        page.locator('#languageSelect').select_option('es')
    page.wait_for_function('Boolean(state.bootstrap)')
    expect(page.locator('#languageSelect')).to_have_value('es')
    checks.append('language:Spanish')
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#menuToggle').click()
    expect(page.locator('body')).to_have_class(__import__('re').compile('sidebar-open'))
    page.locator('.nav-item[data-view="settings"]').click()
    expect(page.locator('#view-settings')).to_be_visible()
    checks.append('mobile:menu-and-navigation')
    page.screenshot(path=str(out/'mobile.png'),full_page=True)
    browser.close()
report={'checks':checks,'page_errors':errors,'failed_local_assets':failed_assets,'optional_fonts_blocked':True,'game_worker_started':False}
(out/'browser-results.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert not errors,errors
assert not failed_assets,failed_assets
