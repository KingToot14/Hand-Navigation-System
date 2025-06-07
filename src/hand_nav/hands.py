import cv2

from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

class Hand:
    def __init__(self):
        self.position = None
        self.landmarks = []
    
    def update_landmarks(self, landmarks: list[NormalizedLandmark]) -> None:
        self.landmarks = landmarks
        
        if not landmarks:
            self.position = None
            return
        
        # palm points
        p1 = landmarks[0]
        p2 = landmarks[5]
        p3 = landmarks[17]
        
        # calculate new positiong (avg point)
        self.position = ((p1.x + p2.x + p3.x) / 3, (p1.y + p2.y + p3.y) / 3)
    
    def draw_hand(self, image) -> cv2.typing.MatLike:
        if not self.landmarks:
            return image
        
        height, width, _ = image.shape
        
        # palm points
        image = cv2.circle(image, (int(width * self.landmarks[0].x), int(height * self.landmarks[0].y)), 7, (0, 0, 0), -1)
        image = cv2.circle(image, (int(width * self.landmarks[0].x), int(height * self.landmarks[0].y)), 5, (255, 0, 0), -1)
        image = cv2.circle(image, (int(width * self.landmarks[5].x), int(height * self.landmarks[5].y)), 7, (0, 0, 0), -1)
        image = cv2.circle(image, (int(width * self.landmarks[5].x), int(height * self.landmarks[5].y)), 5, (255, 0, 0), -1)
        image = cv2.circle(image, (int(width * self.landmarks[17].x), int(height * self.landmarks[17].y)), 7, (0, 0, 0), -1)
        image = cv2.circle(image, (int(width * self.landmarks[17].x), int(height * self.landmarks[17].y)), 5, (255, 0, 0), -1)
        
        # center point
        image = cv2.circle(image, (int(width * self.position[0]), int(height * self.position[1])), 7, (0, 0, 0), -1)
        image = cv2.circle(image, (int(width * self.position[0]), int(height * self.position[1])), 5, (0, 0, 255), -1)
        
        return image

class HandPair:
    def __init__(self, left_hand: Hand = None, right_hand: Hand = None):
        self.left_hand = left_hand   if left_hand  else Hand()
        self.right_hand = right_hand if right_hand else Hand()
    
    def swap_hands(self) -> None:
        self.left_hand, self.right_hand = self.right_hand, self.left_hand
    
    def update_landmarks(self, results: HandLandmarkerResult) -> None:
        l_updated = False
        r_updated = False
        
        for i in range(len(results.handedness)):
            handedness = results.handedness[i][0]
            
            if handedness.category_name == 'Left':
                self.left_hand.update_landmarks(results.hand_landmarks[i])
                l_updated = True
            elif handedness.category_name == 'Right':
                self.right_hand.update_landmarks(results.hand_landmarks[i])
                r_updated = True
        
        if not l_updated:
            self.left_hand.update_landmarks(None)
        if not r_updated:
            self.right_hand.update_landmarks(None)

    def draw_hands(self, image) -> cv2.typing.MatLike:
        if self.left_hand:
            image = self.left_hand.draw_hand(image)
        if self.right_hand:
            image = self.right_hand.draw_hand(image)
        
        return image