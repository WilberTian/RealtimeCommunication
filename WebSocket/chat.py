from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from gevent.event import Event
from cgi import parse_qs, escape
import uuid

chat_html = ""

with open("chat.html") as f:
    chat_html = f.read()


def application(env, start_response):
    # visit the main page
    if env['PATH_INFO'] == '/':
        response_body = chat_html
        if len(messageBuffer.cache) == 0:
            response_body = chat_html %""
        else:
            response_body = chat_html %"".join(messageBuffer.cache)
            
        response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        start_response('200 OK', response_headers)
        return [response_body]
    
    elif env['PATH_INFO'] == '/chatsocket':
        ws = env["wsgi.websocket"]
        messageBuffer.clients.append(ws)
        print "new client join, total client count %d" %len(messageBuffer.clients)
        while True:
            message = ws.receive()
            if message is None:
                messageBuffer.clients.remove(ws)
                print "client leave, total client count %d" %len(messageBuffer.clients)
                break
            print "Got message: %s" %message
            message = "<div>{0}</div>".format(message)
            messageBuffer.new_message(message)
            messageBuffer.update_clients(message)

    else:
        response_body = b'<h1>Not Found</h1>'
        response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        start_response('404 Not Found', response_headers)
        return [response_body]
        
class MessageBuffer(object):
    def __init__(self, cache_size = 200):
        self.cache = []
        self.cache_size = cache_size
        self.clients = []        

    def new_message(self, msg):
        self.cache.append(msg)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]
            
    def update_clients(self, msg):
        for client in self.clients:
            client.send(msg)        
        
print 'Serving on 8080...'
messageBuffer = MessageBuffer()
WSGIServer(('', 8080), application, handler_class=WebSocketHandler).serve_forever()

