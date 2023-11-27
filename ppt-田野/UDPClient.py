import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
message = input('Input lowercase sentence:')

sock.bind(('localhost',10001))

try:

    # Send data
    print('sending', message)
    sent = sock.sendto(message.encode(), server_address)

    # Receive response
    print('waiting to receive')
    data, server = sock.recvfrom(4096)
    print('received ', data.decode())

finally:
    print('closing socket')
    sock.close()