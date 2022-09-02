"""
This module provides the server functionality in a socket system.
The server sets up three sockets bound to three given ports that represent
the three languages the server can respond to a request in, English, Maori and
German. When the server recieves a request it processes the request, constructs
a response packet and returns it to the client that provided the request.

Author: Lucas Redding
"""
import sys
import socket
import select
from datetime import datetime

UDP_IP = "localhost"
ENGLISH_MONTHS = ["January", "Februaray", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November",
                  "December"]
MAORI_MONTHS = ["Kohitatea", "Hui-tanguru", "Poutu-te-rangi", "Paenga-whawha",
                "Haratua", "Pipiri", "Hongongoi", "Here-turi-koka", "Mahuru",
                "Whiringa-a-nuku", "Whiringa-a-rangi", "Hakihea"]
GERMAN_MONTHS = ["Januar", "Februar", "Marz", "April", "Mai", "Juni", "Juli",
                 "August", "September", "Oktober", "November", "Dezember"]

def check_ports(ports):
    """Checks the integrity of the input port numbers"""
    if len(ports) != 3:
        print("Error: Server takes three arguments: English port, Maori port and German port")
        sys.exit(-1)
    if len(ports) != len(set(ports)):
        print("Error: All ports must be distinct")
        sys.exit(-1)
    for i in range(len(ports)):
        ports[i] = int(ports[i])
        if ports[i] < 1024 or ports[i] > 64000:
            print("Error: Ports must be between 1,024 and 64,000")
            sys.exit(-1)
    return True

def open_sockets(ports):
    """Opens sockets and binds them to the given ports"""
    sockets = []
    for i in range(len(ports)):
        try:
            sockets.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
            sockets[i].bind((UDP_IP, ports[i]))
            print(f"Socket {i} created and bound")
        except OSError as error:
            print(error)
            print("Error: Failed to create and bind socket")
            sys.exit()
    print("Socket bind complete")
    return sockets

def check_request(dt_request):
    """Checks the integrity of a request packet, returns query if packet is
    valid otherwise prints diagnostic and exits
    """
    query = None
    if len(dt_request) != 6:
        print("Error: Recieved packet is not 6 bytes")
    elif not (dt_request[0] == 0x49 and dt_request[1] == 0x7E):
        print("Error: Recieved packet has wrong magic number")
    elif not (dt_request[2] == 0x00 and dt_request[3] == 0x01):
        print("Error: Recieved packet is not correct packet type")
    elif not (dt_request[4] == 0x00 and (dt_request[5] == 0x01 or dt_request[5] == 0x02)):
        print("Error: Recieved packet does not have a valid request type")
    else:
        if dt_request[5] == 0x01:
            query = "date"
        else:
            query = "time"
    return query

def  eng_text(query, now):
    """returns a textual representation of a query in English"""
    text_rep = ""
    if query == "date":
        text_rep = f"Today's date is {ENGLISH_MONTHS[now.month-1]} {now.day}, {now.year}"
    elif query == "time":
        text_rep = f"The current time is {now.hour}:{now.minute}"
    return text_rep

def  mao_text(query, now):
    """returns a textual representation of a query in Maori"""
    text_rep = ""
    if query == "date":
        text_rep = f"Ko te ra o tenei ra ko {MAORI_MONTHS[now.month-1]} {now.day}, {now.year}"
    elif query == "time":
        text_rep = f"Ko te wa o tenei wa {now.hour}:{now.minute}"
    return text_rep

def  ger_text(query, now):
    """returns a textual representation of a query in German"""
    text_rep = ""
    if query == "date":
        text_rep = f"Heute ist der {GERMAN_MONTHS[now.month-1]} {now.day}, {now.year}"
    elif query == "time":
        text_rep = f"Die Uhrzeit ist {now.hour}:{now.minute}"
    return text_rep

def construct_response(lang, text_bytes, now):
    """Takes a text representation of date/time and constructs a response packet"""
    if lang == "eng":
        lang_code = 0x01
    elif lang == "mao":
        lang_code = 0x02
    else:
        lang_code = 0x03
    array = bytearray(13+len(text_bytes))
    array[0] = 0x49
    array[1] = 0x7E
    array[2] = 0x00
    array[3] = 0x02
    array[4] = 0x00
    array[5] = lang_code
    array[6] = ((now.year & 0xFF00) >> 8)
    array[7] = (now.year & 0x00FF)
    array[8] = now.month
    array[9] = now.day
    array[10] = now.hour
    array[11] = now.minute
    array[12] = len(text_bytes)
    array[13:] = text_bytes
    return array

def prepare_response(query, active_port, ports):
    """Prepare and return a bytearray packet based on client's query"""
    now = datetime.now()
    text_rep = ""
    dt_response = None
    lang = ""
    if active_port == ports[0]:
        text_rep = eng_text(query, now)
        lang = "eng"
    elif active_port == ports[1]:
        text_rep = mao_text(query, now)
        lang = "mao"
    elif active_port == ports[2]:
        text_rep = ger_text(query, now)
        lang = "ger"
    text_bytes = text_rep.encode('utf-8')
    if len(text_bytes) <= 255:
        dt_response = construct_response(lang, text_bytes, now)
    else:
        print("Error: Textual representation of current date/time is over 255 bytes")
    return dt_response


def send_response(dt_response, address, active_socket):
    """Send response packet to client that requested it"""
    active_socket.sendto(dt_response, address)

def socket_loop(sockets, ports):
    """Infinite loop that waits for client connection, processes the request and
    sends back a response"""
    readable, writable, exceptional = select.select(sockets,[],[])
    while True:
        print("Waiting for input to socket")
        readable, writable, exceptional = select.select(sockets,[],[])
        for active_socket in readable:
            active_port = active_socket.getsockname()[1]
            bytes, address = active_socket.recvfrom(6)
            print(f"Packet recieved from {address}")
            dt_request = bytearray(bytes)
            query = check_request(dt_request)
            if query is not None:
                dt_response = prepare_response(query, active_port, ports)
                if dt_response is not None:
                    send_response(dt_response, address, active_socket)


if __name__ == "__main__":
    ports = sys.argv[1:]
    if check_ports(ports):
        sockets = open_sockets(ports)
        socket_loop(sockets, ports)
