import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 12000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connectionsock, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connectionsock.recv(16)
            print('received ', data.decode())
            if data:
                print('sending data back to the client')
                msg = data.decode()
                msg = msg.upper()
                connectionsock.sendall(msg.encode())
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connectionsock.close()