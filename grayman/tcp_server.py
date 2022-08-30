import socketserver

from helpers import wrap_dict

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address[0]} sent:")
        print(self.data)
        # just send back the same data, but upper-cased
        o = {"msg":'ok'}
        resp = wrap_dict(o).encode()
        self.request.sendall(resp)

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    print(f"running... listening on {HOST}:{PORT}")
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()