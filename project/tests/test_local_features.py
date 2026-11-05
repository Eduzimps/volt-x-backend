from io import BytesIO
import json
import numpy as np

SNAPSHOT = {'player_tag':'PYLQGR','player_name':'Local audit fixture','stats':{
    'SHELLY':{'trophies':120,'power_level':5},'COLT':{'trophies':1500,'power_level':7}}}

def test_import_sort_data_and_push_all(client,headers,application):
    response=client.post('/api/player/import',data={'file':(BytesIO(json.dumps(SNAPSHOT).encode()),'player.json')},headers=headers)
    assert response.status_code==200 and response.json['ok']
    assert response.json['source']=='imported'
    assert 'win_streak' not in response.json['stats']['shelly']
    bootstrap=client.get('/api/bootstrap',headers=headers).json
    assert bootstrap['auth']['premium'] is False
    assert bootstrap['capabilities']['player_data']
    assert bootstrap['player_data']['player_name']=='Local audit fixture'
    assert bootstrap['settings']['general']['player_tag']=='PYLQGR'
    pushed=client.post('/api/queue/push-all',headers=headers)
    assert pushed.status_code==200
    assert pushed.json['added_count']==1
    items=pushed.json['items']
    assert len(items)==1 and items[0]['brawler']=='shelly' and items[0]['trophies']==120
    assert items[0]['push_until']==1000
    assert len(client.post('/api/queue/push-all',headers=headers).json['items'])==1

def test_refresh_without_key_is_explicit_and_no_network(client,headers,monkeypatch):
    monkeypatch.delenv('BRAWL_STARS_API_TOKEN',raising=False)
    result=client.post('/api/player/refresh',json={'player_tag':'PYLQGR'},headers=headers).json
    assert result['ok'] is False and result['code']=='MISSING_CREDENTIAL'

def test_invalid_import_preserves_previous_snapshot(client,headers):
    assert client.post('/api/player/import',json=SNAPSHOT,headers=headers).json['ok']
    assert client.post('/api/player/import',json={'stats':{}},headers=headers).status_code==400
    assert client.get('/api/player',headers=headers).json['player_name']=='Local audit fixture'

def test_debug_controls_real_draw_and_roundtrip(client,headers):
    result=client.put('/api/settings/debug',json={'debug_view':True,'advanced_debug_visuals':True,'record_debug_preview_clips':True},headers=headers)
    assert result.json['advanced_debug_visuals'] is True
    from debug_view import draw_player_hit_circle,draw_range_circles
    image=np.zeros((200,200,3),dtype=np.uint8)
    draw_player_hit_circle(image,(100,100,20))
    assert np.count_nonzero(image)>0
    before=image.copy()
    draw_range_circles(image,[(80,80,120,120)],40,60)
    assert np.count_nonzero(image!=before)>0

def test_profile_api_creation(client,headers):
    result=client.post('/api/profiles',json={'name':'Second account'},headers=headers)
    assert result.status_code==200 and result.json['ok']
    items=client.get('/api/profiles',headers=headers).json['items']
    assert any(item['name']=='Second account' for item in items)
    assert client.post('/api/profiles',json={'name':''},headers=headers).status_code==400

def test_new_routes_require_session(client):
    for path in ('/api/profiles','/api/player'):
        assert client.get(path).status_code==403
    for path in ('/api/player/import','/api/player/refresh','/api/queue/push-all','/api/profiles'):
        assert client.post(path,json={}).status_code==403
