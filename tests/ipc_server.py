import socket
import argparse

import struct

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # args
    parser.add_argument(
        "--host", help="The host address",
        type=str, default='127.0.0.1'
    )
    parser.add_argument(
        "-p", "--port", help="The port to bind to",
        type=int, default=8040
    )
    
    # parse arguemts
    args = parser.parse_args()
    
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print(f"Starting server on {args.host} on port {args.port}")
    sock.bind((args.host, args.port))
    sock.listen(1)
    
    conn, addr = sock.accept()
    print(f"Got connection from: {addr}")
    
    running = True
    while running:
        command = conn.recv(1024).decode()
        tokens = command.split("|")
        
        retr: bytes = b''
        
        match tokens[0]:
            case 'add':
                if len(tokens) < 3:
                    retr = 'err|tla'.encode()
                else:
                    retr = 'suc|'.encode()
                    retr += f"{float(tokens[1]) + float(tokens[2]):.2f}".encode()
            case 'sub':
                if len(tokens) < 3:
                    retr = 'err|tla'.encode()
                else:
                    retr = 'suc|'.encode()
                    retr += f"{float(tokens[1]) - float(tokens[2]):.2f}".encode()
            case 'mul':
                if len(tokens) < 3:
                    retr = 'err|tla'.encode()
                else:
                    retr = 'suc|'.encode()
                    retr += f"{float(tokens[1]) * float(tokens[2]):.2f}".encode()
            case 'div':
                if len(tokens) < 3:
                    retr = 'err|tla'.encode()
                else:
                    retr = 'suc|'.encode()
                    retr += f"{float(tokens[1]) / float(tokens[2]):.2f}".encode()
            case 'ext':
                retr = 'suc'.encode()
                running = False
            case _:
                retr = 'err|ivc'.encode()
        
        conn.send(retr)
        
    conn.close()
    