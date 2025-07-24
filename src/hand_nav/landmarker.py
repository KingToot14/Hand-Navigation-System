import sys
import os

import time

import socket
import select
import argparse

import mediapipe as mp
import cv2

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from hand_nav.hands import HandPair

class Landmarker:
    def __init__(self, **kwargs):
        self.running: bool = True
        
        # hand pair
        self.pair = kwargs.get('pair', HandPair())
        
        # detector
        model_path: str = 'models/hand_landmarker.task'
        
        if hasattr(sys, '_MEIPASS'):
            model_path = os.path.join(sys._MEIPASS, model_path)
        
        base_options = python.BaseOptions(
            model_asset_path=model_path,
        )

        options = vision.HandLandmarkerOptions( base_options=base_options,
                                                running_mode=vision.RunningMode.VIDEO,
                                                num_hands=2,
        )

        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # show capture
        self.show_capture = kwargs.get('show_capture', False)
        
        self.start_time = 0
        
        # server mode
        self.server = kwargs.get('server', False)
        
        if self.server:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
            print(f'Starting server at {kwargs.get('host', '127.0.0.1')} on port {kwargs.get('port', 8040)}')
            self.sock.bind((kwargs.get('host', '127.0.0.1'), kwargs.get('port', 8040)))
            self.sock.listen(1)
            
            print(f' - Started')

            self.start_capture()
    
    def start_capture(self, cap: cv2.VideoCapture = None):
        # use default camera if not specified
        if not cap:
            cap = cv2.VideoCapture(0)

        # load image size
        self.width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        if self.pair:
            self.pair.set_capture_size(self.width, self.height)

        # wait for connection
        conn = None
        if self.server:
            print("Waiting for client connection")
            
            conn, addr = self.sock.accept()
            
            print(f" - Connected at: {addr}")

        # start capture
        self.start_time = time.time() * 1000
        
        while self.running:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            results = self.handle_image(frame)
            
            if self.server:
                if not results or len(results.handedness) == 0:
                    continue
                
                conn.send(self.pack_results(results).encode())
                
            else:
                if results:
                    self.pair.update_landmarks(results)
                
                if self.show_capture:
                    annotated = self.pair.draw_hands(frame)
                    
                    cv2.imshow("Output", annotated)
            
                if cv2.waitKey(1) == ord('q'):
                    break
    
    def pack_results(self, results: HandLandmarkerResult) -> str:
        left = ""
        right = ""
        
        for i in range(min(len(results.handedness), 2)):
            if results.handedness[i][0].category_name == 'Left':
                for landmark in results.hand_landmarks[i]:
                    left += f"|{landmark.x:.3f},{landmark.y:.3f}"
            else:
                for landmark in results.hand_landmarks[i]:
                    right += f"|{landmark.x:.3f},{landmark.y:.3f}"
        
        retr = ""
        
        if len(left.strip()) == 0:
            retr += 'l0'
        else:
            retr += 'l1' + left
        
        retr += '^'
        
        if len(right.strip()) == 0:
            retr += 'r0'
        else:
            retr += 'r1' + right
        
        return retr
    
    def handle_image(self, frame: cv2.typing.MatLike, is_bgr: bool = True) -> HandLandmarkerResult:
        if is_bgr:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        
        return self.detector.detect_for_video(image, int(time.time() * 1000 - self.start_time))

    def close(self):
        self.running = False
        if self.pair:
            self.pair.close()

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
    
    landmarker = Landmarker(host=args.host, port=args.port, server=True)