import socket
import argparse

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
    
    running = True
    while running:
        command = input()
        cmd = command.split("|")[0]
        sock.send(command.encode())
        
        retr = sock.recv(1024).decode()
        tokens = retr.split('|')
        
        match tokens[0]:
            case 'suc':
                if len(tokens) == 1:
                    print("[Success]")
                else:
                    print(f"[Success] {tokens[1:]}")
            case 'err':
                if len(tokens) == 1:
                    print('[Error] No error message')
                    break
                
                match tokens[1]:
                    case 'tma':
                        print(f"[Error] Too many arguments for {cmd}")
                    case 'tla':
                        print(f"[Error] Too little arguments for {cmd}")
                    case 'ivc':
                        print(f"[Error] Invalid command: {cmd}")
        
        if cmd == 'ext':
            running = False
            print("Exiting")
    
    sock.close()
        