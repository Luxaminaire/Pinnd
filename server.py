"""Local-only corkboard server; standard-library Python, no framework."""
import json
import mimetypes
import re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import database as db
from logic import new_note, validate_note, validate_board

STATIC = Path(__file__).with_name('static').resolve()
HOST, PORT = '127.0.0.1', 8000

class Handler(BaseHTTPRequestHandler):
    def respond(self, status, obj):
        payload=json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(payload)

    def body(self):
        size=int(self.headers.get('Content-Length','0'))
        if size<=0 or size>8_000_000: raise ValueError('Invalid request size (maximum 8 MB)')
        return json.loads(self.rfile.read(size))

    def route(self):
        path=urlsplit(self.path).path
        if path=='/api/boards': return ('boards',None)
        if path=='/api/notes': return ('notes',None)
        for pattern,kind in [(r'/api/boards/(\d+)','board'),(r'/api/notes/(\d+)','note'),(r'/api/notes/(\d+)/layer','layer')]:
            m=re.fullmatch(pattern,path)
            if m:return (kind,int(m.group(1)))
        return (None,None)

    def do_GET(self):
        kind,ident=self.route()
        if kind=='boards':return self.respond(200,db.boards())
        if kind=='notes':
            from urllib.parse import parse_qs
            raw=parse_qs(urlsplit(self.path).query).get('board_id',[''])[0]
            if not raw.isdigit() or not db.board_exists(int(raw)):return self.respond(404,{'error':'Board not found'})
            return self.respond(200,db.notes(int(raw)))
        path=urlsplit(self.path).path
        filename='index.html' if path=='/' else path.lstrip('/')
        file=(STATIC/filename).resolve()
        if not file.is_relative_to(STATIC) or not file.is_file():return self.respond(404,{'error':'Not found'})
        content=file.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
        self.send_header('Content-Length',str(len(content)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        try:
            kind,ident=self.route()
            data=self.body()
            if kind=='boards':
                validated=validate_board(data)
                if 'name' not in validated:raise ValueError('Board name required')
                return self.respond(201,{'id':db.add_board(validated['name'])})
            if kind=='notes':
                if not isinstance(data,dict) or not isinstance(data.get('board_id'),int) or not db.board_exists(data['board_id']):
                    return self.respond(404,{'error':'Board not found'})
                return self.respond(201,db.add_note(data['board_id'],new_note({k:v for k,v in data.items() if k!='board_id'})))
            if kind=='layer':
                if not isinstance(data,dict) or data.get('direction') not in ('front','back'):
                    raise ValueError('Invalid layer direction')
                result=db.layer_note(ident,data['direction']=='front')
                return self.respond(200 if result else 404,result or {'error':'Note not found'})
            return self.respond(404,{'error':'Not found'})
        except (ValueError,TypeError,json.JSONDecodeError) as exc:return self.respond(400,{'error':str(exc)})

    def do_PATCH(self):
        try:
            kind,ident=self.route()
            data=self.body()
            if kind=='note':
                old=db.get_note(ident)
                if not old:return self.respond(404,{'error':'Note not found'})
                return self.respond(200,db.update_note(ident,validate_note(data,old)))
            if kind=='board':
                valid=validate_board(data)
                updated=db.update_board(ident,valid)
                return self.respond(200 if updated else 404,{'success':updated})
            return self.respond(404,{'error':'Not found'})
        except (ValueError,TypeError,json.JSONDecodeError) as exc:return self.respond(400,{'error':str(exc)})

    def do_DELETE(self):
        kind,ident=self.route()
        if kind!='note':return self.respond(404,{'error':'Not found'})
        deleted=db.delete_note(ident)
        return self.respond(200 if deleted else 404,{'success':deleted})

if __name__=='__main__':
    db.initialize()
    print(f'Corkboard running at http://{HOST}:{PORT} (Ctrl+C to stop)')
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
