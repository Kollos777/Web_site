from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import threading
import json
import socket
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        self.socket_server(data_dict)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def socket_server(self, data_dict):
        data_dict['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        data_bytes = json.dumps(data_dict).encode('utf-8')
        
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5000
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data_bytes, (UDP_IP, UDP_PORT))
        sock.close()

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())



def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run_socket():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, _ = sock.recvfrom(1024)
        data_dict = json.loads(data.decode('utf-8'))

        with open('storage/data.json', 'r+') as f:
            try:
                data_json = json.load(f)
            except json.JSONDecodeError:
                data_json = {}
            
            data_json[data_dict['timestamp']] = {
                'username': data_dict['username'],
                'message': data_dict['message']
            }

            f.seek(0)
            json.dump(data_json, f, indent=2)
            f.truncate()


if __name__ == '__main__':

    pathlib.Path('storage').mkdir(exist_ok=True)
    if not pathlib.Path('storage/data.json').exists():
        with open('storage/data.json', 'w') as file:
            json.dump({}, file)

    http_thread = threading.Thread(target=run)
    http_thread.daemon = True
    http_thread.start()

    udp_thread = threading.Thread(target=run_socket)
    udp_thread.daemon = True

    udp_thread.start()
    http_thread.join()

