#!/usr/bin/python
# Server that will accept connections from a Vim channel.
# Run this server and then in Vim you can open the channel:
#  :let handle = connect('localhost:8765', 'json')
#
# Then Vim can send requests to the server:
#  :let response = sendexpr(handle, 'hello!')
#
# And you can control Vim by typing a JSON message here, e.g.:
#   ["ex","echo 'hi there'"]
#
# See ":help channel-demo" in Vim.

import SocketServer
import json
import socket
import sys
import threading

thesocket = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        print "=== socket opened ==="
        global thesocket
        thesocket = self.request
        while True:
            try:
                data = self.request.recv(4096)
            except socket.error:
                print "=== socket error ==="
                break
            except IOError:
                print "=== socket closed ==="
                break
            if data == '':
                print "=== socket closed ==="
                break
            print "received: {}".format(data)
            try:
                decoded = json.loads(data)
            except ValueError:
                print "json decoding failed"
                decoded = [0, '']

            if decoded[1] == 'hello!':
                response = "got it"
            else:
                response = "what?"
            encoded = json.dumps([decoded[0], response])
            print "sending {}".format(encoded)
            self.request.sendall(encoded)
        thesocket = None

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 8765

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread: ", server_thread.name

    print "Listening on port {}".format(PORT)
    while True:
        typed = sys.stdin.readline()
        if "quit" in typed:
            print "Goodbye!"
            break
        if thesocket is None:
            print "No socket yet"
        else:
            print "sending {}".format(typed)
            thesocket.sendall(typed)

    server.shutdown()
    server.server_close()
