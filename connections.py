import socketserver

class ServerHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print(self.data.decode("utf-8") + " send by " + self.client_address[0])
        self.request.sendall(bytes("Escape", "utf-8"))

    
def make_server():
    port = 2005
    host = "flippinnublet.com"
    with socketserver.TCPServer((host, port), ServerHandler) as server:
        server.serve_forever()