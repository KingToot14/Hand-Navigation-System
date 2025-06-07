import mediapipe as mp
import cv2

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from hand_nav.hands import HandPair

class CameraManager:
    def __init__(self, detector = None, show_capture: bool = False, pair: HandPair = None):
        # detector
        self.detector = detector
        if not self.detector:
            base_options = python.BaseOptions(
                model_asset_path='models/hand_landmarker.task'
            )

            options = vision.HandLandmarkerOptions(base_options=base_options,
                                                num_hands=2)

            self.detector = vision.HandLandmarker.create_from_options(options)
        
        # show capture
        self.show_capture = show_capture
        
        # hand pair
        self.pair = pair if pair else HandPair()
    
    def start_capture(self, cap: cv2.VideoCapture = None):
        # use default camera if not specified
        if not cap:
            cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            results = self.handle_image(frame)
            
            self.pair.update_landmarks(results)
            
            if self.show_capture:
                annotated = self.pair.draw_hands(frame)
                
                cv2.imshow("Output", annotated)
            
            if cv2.waitKey(1) == ord('q'):
                break
    
    def handle_image(self, frame: cv2.typing.MatLike, is_bgr: bool = True) -> HandLandmarkerResult:
        if is_bgr:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        
        return self.detector.detect(image)
