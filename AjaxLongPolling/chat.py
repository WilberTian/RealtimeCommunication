from gevent.pywsgi import WSGIServer
from gevent.event import Event
from cgi import parse_qs, escape
import uuid

chat_html = ""

with open("chat.html") as f:
    chat_html = f.read()

def application(env, start_response):
    # visit the main page
    if env['PATH_INFO'] == '/':
        return generate_response_data('200 OK', chat_html, start_response)
    # client to send a new message
    elif env['PATH_INFO'] == '/new':
        msg = escape(get_request_data("msg", env))    
        
        msg_item = {}
        msg_item["id"] = str(uuid.uuid4())
        msg_item["msg"] = msg
        print "Got new message from client %s" %str(msg_item)
        
        messageBuffer.cache.append(msg_item)

        if len(messageBuffer.cache) > messageBuffer.cache_size:
            messageBuffer.cache = messageBuffer.cache[-messageBuffer.cache_size:]
        messageBuffer.message_event.set()
        messageBuffer.message_event.clear()
        
        return generate_response_data('200 OK', "", start_response)
    # serve to send available messages
    elif env['PATH_INFO'] == '/update':
        cursor = escape(get_request_data("cursor", env))
        print "cursor: %s" %cursor

        # if message buffer is empty or no new messages, just wait
        if len(messageBuffer.cache) == 0 or messageBuffer.cache[-1]["id"] == cursor:
            messageBuffer.message_event.wait()
        
        for index, m in enumerate(messageBuffer.cache):
            if m['id'] == cursor:
                return generate_response_data('200 OK', generate_json_data(messageBuffer.cache[index + 1:]), start_response)
       
        return generate_response_data('200 OK', generate_json_data(messageBuffer.cache), start_response)
    else:
        return generate_response_data('404 Not Found', b'<h1>Not Found</h1>', start_response)
   
def get_request_data(field, env):
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = env['wsgi.input'].read(request_body_size)
    d = parse_qs(request_body)
    data = d.get(field, [''])[0] 
    return data
    
def generate_response_data(status, response_body, start_response):
     response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
     start_response('200 OK', response_headers)
     return [response_body]
     
def generate_json_data(msg_list):
    msg_dict = {}
    msg_dict["html"] = ""
    for msg in msg_list:
        msg_dict["html"] += "<div>{0}</div>".format(msg["msg"])
    msg_dict["latest_cursor"] = msg_list[-1]["id"]
    return str(msg_dict)
   
class MessageBuffer(object):
    def __init__(self, cache_size = 200):
        self.cache = []
        self.cache_size = cache_size
        self.message_event = Event()

print 'Serving on 8080...'
messageBuffer = MessageBuffer()
# use WSGIServer from gevent, it's a none-blocking server
WSGIServer(('192.168.56.101', 8080), application).serve_forever()
