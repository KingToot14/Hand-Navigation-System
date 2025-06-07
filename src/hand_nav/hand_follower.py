import mediapipe as mp
import cv2
import numpy as np

from mediapipe import solutions
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

MARGIN = 10
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)

# --- Create Hand Landmarker --- #
base_options = python.BaseOptions(
    model_asset_path='models/hand_landmarker.task'
)

options = vision.HandLandmarkerOptions(base_options=base_options,
                                       num_hands=2)

detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    mp.Image
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    results = detector.detect(image)
    landmarks = results.hand_landmarks
    
    output = frame
    
    if landmarks:
        landmarks = landmarks[0]
        
        # palm points
        p1 = landmarks[0]
        p2 = landmarks[5]
        p3 = landmarks[17]
        
        # avg point
        avg = ((p1.x + p2.x + p3.x) / 3, (p1.y + p2.y + p3.y) / 3)
        
        # draw palm points
        height, width, _ = frame.shape
        
        annotated = cv2.circle(frame, (int(width * p1.x), int(height * p1.y)), 7, (0, 0, 0), -1)
        annotated = cv2.circle(frame, (int(width * p1.x), int(height * p1.y)), 5, (255, 0, 0), -1)
        annotated = cv2.circle(frame, (int(width * p2.x), int(height * p2.y)), 7, (0, 0, 0), -1)
        annotated = cv2.circle(frame, (int(width * p2.x), int(height * p2.y)), 5, (255, 0, 0), -1)
        annotated = cv2.circle(frame, (int(width * p3.x), int(height * p3.y)), 7, (0, 0, 0), -1)
        annotated = cv2.circle(frame, (int(width * p3.x), int(height * p3.y)), 5, (255, 0, 0), -1)
        
        annotated = cv2.circle(frame, (int(width * avg[0]), int(height * avg[1])), 7, (0, 0, 0), -1)
        annotated = cv2.circle(frame, (int(width * avg[0]), int(height * avg[1])), 5, (0, 0, 255), -1)
        
        output = annotated
    
    cv2.imshow("Output", output)
    
    if cv2.waitKey(1) == ord('q'):
        break
