import struct

import socket
import argparse

from hands import Hand

def run():
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
    
    # parse arguments
    args = parser.parse_args()
    
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    
    sock.connect((args.host, args.port))
    
    left = Hand()
    right = Hand()
    
    running = True
    while running:
        try:
            retr = sock.recv(1024)
            
            if len(retr) == 0:
                print("Connection closed")
                break
            
            # helper method
            bp: int = 0
            
            def parse(format: str):
                nonlocal bp
                
                size = struct.calcsize(format)
                out = struct.unpack(format, retr[bp:bp+size])
                
                bp += size
                
                if len(format) > 1:
                    return out
                return out[0]
            
            # unpack
            flags = parse('B')
            
            # left hand
            if flags & 0b00000001:
                landmarks = [parse('ff') for i in range(21)]
                
                left.update_landmarks(landmarks)
            
            # right hand
            if flags & 0b00000010:
                landmarks = [parse('ff') for i in range(21)]
                
                right.update_landmarks(landmarks)
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            print("Closing client")
            if sock:
                sock.close()
            break
    
    sock.close()

if __name__ == "__main__":
    run()
        