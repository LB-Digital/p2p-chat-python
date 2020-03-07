import socket
# using threads to allow multiple people to connect at a time
import threading
import sys


IP = '127.0.0.1'
PORT = 2000



class Server:
    # first param tells the socket it's going to send the info using IPv4 (not IPv6)
    # SOCK_STREAM means TCP, SOCK_DGRAM would be UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connections = []

    def __init__(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((IP, PORT))
        # 1 is the number of connections we want allow
        self.sock.listen(1)

    def handler(self, c, a):
        # loop running in background as it's in a different thread
        while True:
            # max data we can receive is 1024 bytes
            # recv function is a blocking function, so the loop won't run until we receive data
            data = c.recv(1024)

            for connection in self.connections:
                connection.send(bytes(data))

            if not data:
                # client disconnected
                print(f'{a[0]}:{a[1]} disconnected!')
                self.connections.remove(c)
                c.close()
                break

    def run(self):
        while True:
            # c:clients connection, a:clients address
            c, a = self.sock.accept()
            # every time we get a new connection, create a new thread
            # pass it the name of the function that's going to be run when we run our thread
            # passing the connection and the address as parameters to handler
            c_thread = threading.Thread(target=self.handler, args=(c, a))
            # means the program will be able to exit, regardless of whether any threads are running
            # as usually, the OS won't let u close the program if any threads are still running
            c_thread.daemon = True
            # start the thread
            c_thread.start()

            self.connections.append(c)
            print(f'{a[0]}:{a[1]} connected!')


class Client:
    # client socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, server_ip, server_port):
        print(server_ip, server_port)
        self.sock.connect((server_ip, server_port))

        # create new thread to send msg's via, since the main thread is continually trying to receive
        # data, we can't send and receive dat at the same time, so create a new thread so both
        # can be done at same time
        # i_thread (input thread)
        i_thread = threading.Thread(target=self.send)
        # will close when we close program
        i_thread.daemon = True
        i_thread.start()

        # continually receiving data
        while True:
            data = self.sock.recv(1024)

            if not data:
                # client has disconnected
                break

            # print data received
            print(data.decode('utf-8'))

    # method to send msg's to server
    def send(self):
        # this is continually running in background on it's own thread, so need to put in
        # a while loop
        while True:
            # input is a blocking function, so always waiting
            self.sock.send(bytes(input(''), 'utf-8'))


# do we want to be server or the client?
# sys.argv is cmd line args, if more than 1 is given (first is always the name of the file)
# 2nd will be IP we want to connect to as the client
if len(sys.argv) > 1:
    server_ip, server_port = sys.argv[1].split(':')
    server_port = int(server_port)
    client = Client(server_ip, server_port)

else:
    # server ip not given for client to connect too, so starting a server

    server = Server()
    server.run()



