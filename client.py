"""
This module provides the client functionality in a socket system.
The client constructs a request packet and sends it to the given server asking
for either the current date or time in English, Maori or German. The client then
process the response packet and prints to output the response it requested.

Author: Lucas Redding
"""
import sys
import socket
import select

def process_input(inputs):
    """Checks the integrity of the inputs to the program and returns the server
    information"""
    query = inputs[0]
    server_ip = inputs[1]
    server_port = int(inputs[2])

    if len(inputs) != 3:
        print("Error: Client takes three arguments: date/time, IP address and server port")
        sys.exit(-1)
    if query != "date" and query != "time":
        print("Error: First argument must be either \"date\" or \"time\"")
        sys.exit(-1)
    if server_port < 1024 or server_port > 64000:
        print("Error: Port must be between 1,024 and 64,000")
        sys.exit(-1)
    try:
        servers = socket.getaddrinfo(server_ip,server_port,family=socket.AF_INET,type=socket.SOCK_DGRAM)
    except OSError as error:
        print(error)
        print("Error: Hostname does not exist or IP notation is not well formed")

    return query, servers[0]

def open_socket(server):
    """Opens a socket and connects it to the given server"""
    server_addr = server[4]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.connect(server_addr)
    return server_socket

def construct_request(query):
    """Construct and return request packet based on query"""
    req_type = int()
    if query == "date":
        req_type = 0x01
    elif query == "time":
        req_type = 0x02
    array = bytearray(6)
    array[0] = 0x49
    array[1] = 0x7E
    array[2] = 0x00
    array[3] = 0x01
    array[4] = 0x00
    array[5] = req_type
    return array

def send_request(server_socket, dt_request):
    """Send request packet to server socket and return response"""
    dt_response = None
    server_socket.send(dt_request)
    readable, writable, exceptional = select.select([server_socket],[],[],1)
    if len(readable) == 0:
        print("Error: Response from server took too long")
        sys.exit(-1)
    else:
        try:
            server_socket = readable[0]
            bytes, address = server_socket.recvfrom(268)
            dt_response = bytes
        except ConnectionRefusedError:
            print("Error: Connection to server failed")
            sys.exit()
    return dt_response


def print_data(dt_response):
    """Print data from response packet"""
    print(f"Magic number: {hex((dt_response[0] << 8) | (dt_response[1]))}")
    print(f"Packet type: {hex((dt_response[2] << 8) | dt_response[3])}")
    print(f"Language code: {hex((dt_response[4] << 8) | dt_response[5])}")
    print(f"Year: {((dt_response[6] << 8) | dt_response[7])}")
    print(f"Month: {dt_response[8]}")
    print(f"Day: {dt_response[9]}")
    print(f"Hour: {dt_response[10]}")
    print(f"Minute: {dt_response[11]}")
    print(f"Data length: {dt_response[12]}")
    print(f"{dt_response[13:].decode('utf-8')}")


def process_response(dt_response):
    """Check integrity of response packet and print its data"""
    if len(dt_response) < 13:
        print("Error: Recieved packet is not at least 13 bytes")
        sys.exit(-1)
    elif not (dt_response[0] == 0x49 and dt_response[1] == 0x7E):
        print("Error: Recieved packet has wrong magic number")
        sys.exit(-1)
    elif not (dt_response[2] == 0x00 and dt_response[3] == 0x02):
        print("Error: Recieved packet is not correct packet type")
        sys.exit(-1)
    elif not (dt_response[4] == 0x00 and (dt_response[5] in [0x01,0x02,0x03])):
        print("Error: Recieved packet has invalid language code")
        sys.exit(-1)
    elif ((dt_response[6] << 8) | (dt_response[7])) >= 2100:
        print("Error: Recieved packet has invalid year")
        sys.exit()
    elif dt_response[8] < 1 or dt_response[8] > 12:
        print("Error: Recieved packet has invalid month")
        sys.exit()
    elif dt_response[9] < 1 or dt_response[9] > 31:
        print("Error: Recieved packet has invalid day")
        sys.exit()
    elif dt_response[10] < 0 or dt_response[10] > 23:
        print("Error: Recieved packet has invalid hour")
        sys.exit()
    elif dt_response[11] < 0 or dt_response[11] > 59:
        print("Error: Recieved packet has invalid minute")
        sys.exit()
    elif len(dt_response) != 13 + dt_response[12]:
        print(len(dt_response), dt_response[12])
        print("Error: Recieved packet has invalid length")
        sys.exit()
    else:
        print_data(dt_response)


if __name__ == "__main__":
    inputs = sys.argv[1:]
    query, server = process_input(inputs)
    server_socket = open_socket(server)
    dt_request = construct_request(query)
    dt_response = send_request(server_socket, dt_request)
    process_response(dt_response)
