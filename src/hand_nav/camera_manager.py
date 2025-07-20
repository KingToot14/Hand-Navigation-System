import time

import mediapipe as mp
import cv2

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from hand_nav.hands import HandPair

class CameraManager:
    def __init__(self, detector = None, show_capture: bool = False, pair: HandPair = None):
        self.running: bool = True
        
        # hand pair
        self.pair = pair if pair else HandPair()
        
        # detector
        self.detector = detector
        if not self.detector:
            base_options = python.BaseOptions(
                model_asset_path='models/hand_landmarker.task',
            )

            options = vision.HandLandmarkerOptions( base_options=base_options,
                                                    running_mode=vision.RunningMode.VIDEO,
                                                    num_hands=2,
            )

            self.detector = vision.HandLandmarker.create_from_options(options)
        
        # show capture
        self.show_capture = show_capture
        
        self.start_time = 0
    
    def start_capture(self, cap: cv2.VideoCapture = None):
        # use default camera if not specified
        if not cap:
            cap = cv2.VideoCapture(0)

        # load image size
        self.width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        if self.pair:
            self.pair.set_capture_size(self.width, self.height)

        # start capture
        self.start_time = time.time() * 1000
        
        while self.running:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            results = self.handle_image(frame)
            
            if results:
                self.pair.update_landmarks(results)
            
            if self.show_capture:
                annotated = self.pair.draw_hands(frame)
                
                cv2.imshow("Output", annotated)
            
            if cv2.waitKey(1) == ord('q'):
                break
    
    def result_handler(self, results, image, timestamp) -> None:
        self.pair.update_landmarks(results)
    
    def handle_image(self, frame: cv2.typing.MatLike, is_bgr: bool = True) -> HandLandmarkerResult:
        if is_bgr:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        
        return self.detector.detect_for_video(image, int(time.time() * 1000 - self.start_time))

    def close(self):
        self.running = False
        if self.pair:
            self.pair.close()