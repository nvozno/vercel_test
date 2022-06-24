from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import requests

class handler(BaseHTTPRequestHandler):

  def do_GET(self):
    ip = requests.get('https://api.ip.sb/ip').text
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    self.wfile.write(ip.encode())
    return

if __name__ == "__main__":
    http_server = HTTPServer(('', int(8888)), handler)
    http_server.serve_forever() 