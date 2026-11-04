import math
import re
from database import board_exists

BOARD_WIDTH = 8000
BOARD_HEIGHT = 6000
COLORS = {'#ffe66d','#f9b9cf','#b7e5f3','#c7efba','#e7c7ff','#ffffff','#ffcfa8'}
MEDIA_RE = re.compile(r'^data:(image/(?:png|jpeg|gif|webp)|audio/(?:mpeg|mp4|ogg|wav|webm));base64,[A-Za-z0-9+/]+={0,2}$')

def number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value):
        raise ValueError('Expected a finite number')
    return max(low, min(high, float(value)))

def validate_note(data, existing=None):
    if not isinstance(data, dict): raise ValueError('Expected an object')
    allowed = {'title','body','image','audio','x','y','width','height','color'}
    if set(data)-allowed: raise ValueError('Unknown note field')
    result = {}
    for key in ('title','body'):
        if key in data:
            if not isinstance(data[key],str) or len(data[key]) > (120 if key=='title' else 20000):
                raise ValueError('Invalid '+key)
            result[key] = data[key]
    for key in ('image','audio'):
        if key in data:
            val = data[key]
            if not isinstance(val,str) or len(val)>4_000_000 or (val and (not MEDIA_RE.fullmatch(val) or not val.startswith('data:'+key+'/'))):
                raise ValueError('Invalid '+key+' attachment')
            result[key] = val
    for key,lo,hi in [('x',0,BOARD_WIDTH-120),('y',0,BOARD_HEIGHT-100),('width',160,1000),('height',150,1000)]:
        if key in data: result[key] = number(data[key],lo,hi)
    if 'color' in data:
        if data['color'] not in COLORS: raise ValueError('Invalid note color')
        result['color'] = data['color']
    width = result.get('width', (existing or {}).get('width',260))
    height = result.get('height', (existing or {}).get('height',240))
    if 'x' in result: result['x'] = min(result['x'],BOARD_WIDTH-width)
    if 'y' in result: result['y'] = min(result['y'],BOARD_HEIGHT-height)
    if 'width' in result and existing: result['width'] = min(width,BOARD_WIDTH-result.get('x',existing['x']))
    if 'height' in result and existing: result['height'] = min(height,BOARD_HEIGHT-result.get('y',existing['y']))
    return result

def new_note(data):
    base = {'title':'Untitled','body':'','image':'','audio':'','x':3700,'y':2800,'width':260,'height':240,'color':'#ffe66d'}
    base.update(validate_note(data))
    return base

def validate_board(data):
    if not isinstance(data,dict): raise ValueError('Expected an object')
    if set(data)-{'name','view_x','view_y','zoom'}: raise ValueError('Unknown board field')
    result={}
    if 'name' in data:
        if not isinstance(data['name'],str) or not (1<=len(data['name'].strip())<=80): raise ValueError('Invalid board name')
        result['name']=data['name'].strip()
    for k,lo,hi in [('view_x',-20000,20000),('view_y',-20000,20000),('zoom',0.1,3)]:
        if k in data: result[k]=number(data[k],lo,hi)
    return result
