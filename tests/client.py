import socket
import argparse

from hands import Hand

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
    
    # parse arguments
    args = parser.parse_args()
    
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    sock.connect((args.host, args.port))
    sock.settimeout(0.5)
    
    left = Hand()
    right = Hand()
    
    running = True
    while running:
        try:
            retr = sock.recv(1024).decode()
            
            # unpack
            hands = retr.split("^")
            
            if hands[0][1] == '1':
                points = hands[0].split("|")
                landmarks = []
                
                for point in points[1:]:
                    landmarks.append(list(map(float, point.split(','))))
                
                left.update_landmarks(landmarks)
            
            if hands[1][1] == '1':
                points = hands[1].split("|")
                landmarks = []
                
                for point in points[1:]:
                    landmarks.append(list(map(float, point.split(','))))
                
                right.update_landmarks(landmarks)
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            print("Closing client")
            if sock:
                sock.close()
            break
    
    sock.close()
        